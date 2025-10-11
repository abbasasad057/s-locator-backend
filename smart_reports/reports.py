import os
import json
import asyncio
import logging
from .report_generation.data_processor import calculate_statistics
from pathlib import Path
from all_types.request_dtypes import Reqsmartreport, ReqFetchDataset
from utils.geo_std_utils import bbox_to_polygon
from data_fetcher import fetch_dataset
from .report_generation.pharmacy_report_final import generate_all_maps, generate_all_charts
from smart_reports.traffic import fetch_traffic_data
from backend_common.database import MAX_POOL
from smart_reports.population import (
    fetch_demographics,
    fetch_household_sizes,
    get_demographic_info_for_listings,
)
from smart_reports.healthcare_system import get_healthcare_data
from smart_reports.complementary_businesses import get_other_businesses_data
from smart_reports.scoring import *
from typing import Dict, Any
from utils.geo_std_utils import generate_bbox
from utils.utils import DIR_REPORTS

# Import the modular generator
from .html_generator.pharmacy_generator import (
    generate_complete_html_report,
)
from typing import Optional
from .report_generation.report_config import (
    source_current_location,
    source_custom_locations,
    source_shop_for_rent,
)

POPULATION_KEYS = [
    "total_population",
    "avg_density",
    "avg_median_age",
    "percentage_age_above_20",
    "percentage_age_above_25",
    "percentage_age_above_30",
    "percentage_age_above_35",
    "percentage_age_above_40",
    "percentage_age_above_45",
    "percentage_age_above_50",
]

INCOME_KEYS = ["avg_income"]

HOUSEHOLD_KEYS = [
    "avg_household_size",
    "median_household_size",
    "household_density_sum",
]

TRAFFIC_KEYS = [
    "traffic_score",
    "traffic_storefront_score",
    "traffic_area_score",
    "traffic_screenshot_filename",
    "traffic_analysis_date",
]


def write_html_file(file_path: Path, content: str) -> None:
    """Write HTML content to file"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def score_shops(all_shops_data, req):
    # in this part we process all candidates locations data
    results = {}

    for shop in all_shops_data:
        # if traffic_score is None skip this shop
        if not shop.get("traffic_score"):
            continue

        lat = shop.get("lat")
        lng = shop.get("lng")
        # Compose key
        loc_key = f"{lat},{lng}"

        traffic_score = (
            shop.get("traffic_score", 1) * req.evaluation_metrics.traffic
        )
        demographics_score = score_demographics(shop, req)
        healthcare_score = score_healthcare_ecosystem(
            shop, req.evaluation_metrics.healthcare
        )
        competitive_score = score_competitive(
            shop, req.evaluation_metrics.competition
        )
        complementary_score = score_complementary_businesses(
            shop, req.evaluation_metrics.complementary
        )

        total_score = (
            traffic_score
            + demographics_score
            + healthcare_score
            + competitive_score
            + complementary_score
        )

        results[loc_key] = {
            **shop,
            "id": loc_key,
            "total_score": total_score,
            "weighted_scores": {
                "traffic": traffic_score,
                "demographics": demographics_score,
                "competition": competitive_score,
                "healthcare": healthcare_score,
                "complementary": complementary_score,
            },
        }


async def get_and_score_listings(req: Reqsmartreport) -> dict:
    req_dataset = ReqFetchDataset(
        user_id=req.user_id,
        city_name=req.city_name,
        country_name=req.country_name,
        boolean_query="shop_for_rent",
        action="full data",
        full_load=True,
    )
    # Load shop listings for rent first (used later)
    shops_for_rent = await loading_category_dataset(req_dataset)

    # We'll parallelize loading the other categories. Do NOT mutate req_dataset in-place.
    categories = [
        "pharmacy",
        "hospital",
        "dentist",
        "grocery_store",
        "supermarket",
        "restaurant",
        "atm",
        "bank",
    ]

    # Create independent ReqFetchDataset objects per category.
    reqs = []
    for category in categories:
        reqs.append(req_dataset.model_copy(update={"boolean_query": category}))

    # Bounded concurrency to avoid overwhelming DB or upstream APIs. Tune this.
    concurrency_limit = int(
        MAX_POOL // 2
    )  # Half of DB pool for fetching datasets
    sem = asyncio.Semaphore(concurrency_limit)

    async def _bounded_load(rq: ReqFetchDataset):
        async with sem:
            return await loading_category_dataset(rq)

    (
        pharmacies,
        hospitals,
        dentists,
        grocery_store,
        supermarket,
        restaurant,
        atm,
        bank,
    ) = await asyncio.gather(*(_bounded_load(r) for r in reqs))

    # get all demograhics + household + income for those shops_for_rent
    # isolate list of listing_ids from shops_for_rent
    listing_demographic_info = await get_demographic_info_for_listings(
        shops_for_rent
    )

    ## in this part For Each location (shop for rent),
    # we fetch all the details of that specific locations
    all_shops_data = []
    for shop in shops_for_rent:
        price = shop["properties"]["price"] or 0
        geometry = shop["geometry"]
        coordinates = geometry["coordinates"]
        lng = coordinates[0]
        lat = coordinates[1]
        place_url = shop["properties"]["url"]
        last_segment = place_url.split("/")[-1]
        extracted_part = last_segment.rsplit("-", 1)[0]
        shop_data = await group_criterion_data(
            lat=lat,
            lng=lng,
            Userid=req.user_id,
            hospital=hospitals,
            pharmacies=pharmacies,
            dentists=dentists,
            grocery_store=grocery_store,
            supermarket=supermarket,
            restaurant=restaurant,
            atm=atm,
            bank=bank,
            place_name=extracted_part,
            place_price=price,
            place_url=place_url,
            listing_demographic_info=listing_demographic_info,
        )

        all_shops_data.append(shop_data)
    # --- Step 2: process custom_locations (if any) 
    custom_loc = []
    if req.custom_locations:
        for i, coord in enumerate(req.custom_locations, start=1):
            if coord.lat != 0 and coord.lng != 0:
                shop_data = await group_criterion_data(
                    lat=coord.lat,
                    lng=coord.lng,
                    Userid=req.user_id,
                    hospital=hospitals,
                    pharmacies=pharmacies,
                    dentists=dentists,
                    grocery_store=grocery_store,
                    supermarket=supermarket,
                    restaurant=restaurant,
                    atm=atm,
                    bank=bank,
                    source=source_custom_locations,
                    place_name=f"Num {i} custom location",  # no URL for custom
                    place_price=None,  # no price for custom
                    listing_demographic_info=listing_demographic_info,
                )
                all_shops_data.append(shop_data)
                custom_loc.append(shop_data)

    current_loc = []
    if req.current_location:
        if req.current_location.lat != 0 and req.current_location.lng != 0:
            shop_data = await group_criterion_data(
                lat=req.current_location.lat,
                lng=req.current_location.lng,
                Userid=req.user_id,
                hospital=hospitals,
                pharmacies=pharmacies,
                dentists=dentists,
                grocery_store=grocery_store,
                supermarket=supermarket,
                restaurant=restaurant,
                atm=atm,
                bank=bank,
                source=source_current_location,
                place_name="Your current location",
                place_price=None,
                listing_demographic_info=listing_demographic_info,
            )
            all_shops_data.append(shop_data)
            current_loc.append(shop_data)


    results = score_shops(all_shops_data, req)
    custom_results = score_shops(custom_loc, req)
    current_results = score_shops(current_loc, req)

    stats = calculate_statistics(results)
    stats["total_competing_pharmacies"] = len(pharmacies)
    list_top_n_sites = sorted(
        results.values(), key=lambda s: s.get("total_score", 0), reverse=True
    )[:10]

    best_site = list_top_n_sites[0]

    return results, stats, list_top_n_sites, best_site, custom_results, current_results


async def generate_pharmacy_report(req: Reqsmartreport):
    """
    Generate a pharmacy site report with multi-criteria scoring.

    Loads datasets, computes scores for traffic, demographics, healthcare,
    competition, and nearby amenities, then returns top-ranked sites.

    Args:
        req (Reqsmartreport): Request with user info and evaluation metrics.

    Returns:
        dict: Pharmacy report with scores and insights.
    """
    debug_path_results = Path("results.json")
    debug_path_stats = Path("stats.json")
    debug_path_list_top_n_sites = Path("list_top_n_sites.json")
    debug_path_best_site = Path("best_site.json")
    debug_path_custom_results = Path("custom_results.json")
    debug_path_current_results = Path("current_results.json")

    (results, 
    stats, 
    list_top_n_sites, 
    best_site, 
    custom_results, 
    current_results) = await get_and_score_listings(
        req
    )
    with open(debug_path_results, "w") as f:
        json.dump(results, f, indent=4)
    with open(debug_path_stats, "w") as f:
        json.dump(stats, f, indent=4)
    with open(debug_path_list_top_n_sites, "w") as f:
        json.dump(list_top_n_sites, f, indent=4)
    with open(debug_path_best_site, "w") as f:
        json.dump(best_site, f, indent=4)
    with open(debug_path_custom_results, "w") as f:
        json.dump(custom_results, f, indent=4)
    with open(debug_path_current_results, "w") as f:
        json.dump(current_results, f, indent=4)

    # read from json files
    with open(debug_path_results, "r") as f:
        results = json.load(f)
    with open(debug_path_stats, "r") as f:
        stats = json.load(f)
    with open(debug_path_list_top_n_sites, "r") as f:
        list_top_n_sites = json.load(f)
    with open(debug_path_best_site, "r") as f:
        best_site = json.load(f)
    with open(debug_path_custom_results, "r") as f:
        custom_results = json.load(f)
    with open(debug_path_current_results, "r") as f:
        current_results = json.load(f)

    # Calculate statistics for the sites
    logging.info("📊 Calculating statistics...")

    charts = generate_all_charts(list_top_n_sites)

    # Generate maps
    logging.info("🗺️  Generating maps...")
    map_png, heat_png = generate_all_maps(sites, output_dir, top_n)

    # Generate markdown report
    # logging.info("📝 Generating enhanced markdown report...")
    # report_data = generate_markdown(
    #     sites,
    #     output_dir,
    #     output_filename,
    #     top_n,
    #     charts,
    #     map_png,
    #     heat_png,
    #     req,
    #     list_top_n_sites,
    #     stats,
    #     best_site,
    #     list_top_n_sites,
    #     best_site
    # )
    logging.info("✅ Report generation completed successfully")
    return results, stats, list_top_n_sites, best_site, custom_results, current_results



async def group_criterion_data(
    lat: float,
    lng: float,
    Userid: str,
    hospital: dict,
    pharmacies: dict,
    dentists: dict,
    grocery_store: dict,
    supermarket: dict,
    restaurant: dict,
    atm: dict,
    bank: dict,
    listing_demographic_info,
    source: str = source_shop_for_rent,
    place_name: Optional[str] = None,
    place_price: Optional[float] = None,  # or str, depending on your data
    place_url: Optional[str] = None,
):
    """
    Fetch all relevant criterion data for evaluating a shop location.
    Combines traffic, households, demographics, healthcare, and other businesses.
    """
    info_for_place: dict = listing_demographic_info.get(place_url, {})
    bbox = generate_bbox(lat, lng)
    area_polygon = bbox_to_polygon(bbox=bbox)

    healthcare = await get_healthcare_data(
        area_polygon, lat, lng, hospital, dentists, pharmacies
    )

    other_businesses = await get_other_businesses_data(
        area_polygon,
        lat,
        lng,
        grocery_store_data=grocery_store,
        supermarket_data=supermarket,
        restaurant_data=restaurant,
        bank_data=bank,
        atm_data=atm,
    )

    demographics = {key: info_for_place.get(key) for key in POPULATION_KEYS}

    # Calculate pharmacies per 10k population
    total_population = demographics.get("total_population")
    if total_population and total_population > 0:
        pharmacies_per_10k = healthcare.get("num_of_pharmacies") / (
            total_population / 10000
        )
    else:
        pharmacies_per_10k = 0

    # Add the new key right under num_of_pharmacies
    healthcare["pharmacies_per_10k_population"] = pharmacies_per_10k

    return {
        "source": source,
        "display_name": place_name,
        "lat": lat,
        "lng": lng,
        "price": place_price,
        "url": place_url,
        **info_for_place,
        **healthcare,
        **other_businesses,
    }


async def generate_html_pharmacy_report(req: Reqsmartreport) -> Dict[str, Any]:
    """
    Generate a comprehensive pharmacy report and return structured data.

    Creates a multi-page HTML report with executive summary, methodology,
    detailed analysis, and visual components following the specified structure.

    Args:
        req (Reqsmartreport): User request containing pharmacy analysis parameters

    Returns:
        Dict[str, Any]: Structured report data matching ResIntelligenceData format
    """

    # Generate the processed report data
    sites, processed_report_data = await generate_pharmacy_report(req)

    # # save all_shops_data to json file for debugging
    # debug_path = Path("processed_report_data.json")
    # with open(debug_path, 'w') as f:
    #     json.dump(processed_report_data, f, indent=4)

    # # read from json file
    # debug_path = Path("processed_report_data.json")
    # with open(debug_path, "r") as f:
    #     processed_report_data = json.load(f)

    # Generate the HTML report file
    html_content = generate_complete_html_report(req, processed_report_data)

    html_file_path = Path(DIR_REPORTS) / f"{req.user_id}.html"
    write_html_file(html_file_path, html_content)

    # Return structured data matching ResIntelligenceData format
    return {
        "title": processed_report_data.get(
            "title", f"{req.city_name} Pharmacy Site Analysis Report"
        ),
        "description": processed_report_data.get(
            "description",
            "Comprehensive Location Intelligence & Investment Recommendations",
        ),
        "summary_metrics": processed_report_data.get("summary_metrics", {}),
        "executive_summary": processed_report_data.get("executive_summary", {}),
        "key_investment_insights": processed_report_data.get(
            "key_investment_insights", []
        ),
        "rankings": processed_report_data.get("rankings", []),
        "detailed_analysis": processed_report_data.get("detailed_analysis", []),
        "visual_analysis": processed_report_data.get("visual_analysis", {}),
        "methodology": processed_report_data.get("methodology", {}),
        "statistical_insights": processed_report_data.get(
            "statistical_insights", []
        ),
        "metadata": {
            **processed_report_data.get("metadata", {}),
            "html_file_path": html_file_path,
            "generation_method": "HTML Report Generator",
            "report_type": "pharmacy_site_selection",
        },
    }


async def loading_category_dataset(req: ReqFetchDataset):

    data = await fetch_dataset(req)
    features = data.get("features", [])
    return features
