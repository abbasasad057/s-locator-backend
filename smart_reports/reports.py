import os
import json
import asyncio
import logging
import aiohttp
from logging_wrapper import (
    apply_decorator_to_module
)
from .report_generation.data_processor import calculate_statistics
from pathlib import Path
from smart_reports.report_generation.map_generator import (
    generate_all_site_map_image,
    create_static_map_png,
    create_demographic_heatmap_png,
)
from all_types.request_dtypes import Reqsmartreport, ReqFetchDataset
from utils.geo_std_utils import bbox_to_polygon
from data_fetcher import fetch_dataset
from .report_generation.pharmacy_report_final import (
    generate_all_maps,
    generate_all_charts,
)
from utils.utils import create_report_asset_path
from smart_reports.report_generation.report_object import (
    compare_values,
    generate_best_site_insights,
)
from smart_reports.traffic import fetch_traffic_data
from backend_common.database import MAX_POOL
from smart_reports.population import (
    fetch_demographics,
    fetch_household_sizes,
    get_demographic_info_for_listings,
)
from smart_reports.healthcare_system import get_healthcare_data
from smart_reports.complementary_businesses import get_other_businesses_data
from smart_reports.scoring import (
    score_demographics,
    score_competitive,
    score_healthcare_ecosystem,
    score_complementary_businesses,
)
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
from app_logger import get_logger
logger = get_logger(__name__)

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

# API scoring base URL
SCORING_API_BASE_URL = "http://46.62.227.32:8000"


async def fetch_demographics_score(
    lat: float, lng: float, radius: float, target_age: int
) -> int:
    """
    Call the demographics scoring API.

    Args:
        lat: Latitude of location
        lng: Longitude of location
        radius: Search radius in meters
        target_age: Target age for scoring

    Returns:
        Demographics score (0-100)
    """
    url = f"{SCORING_API_BASE_URL}/demographics/score"
    payload = {
        "lat": lat,
        "lng": lng,
        "radius": radius,
        "target_age": target_age,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json=payload, timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return int(data.get("score")) * 100
            else:
                logging.warning(
                    f"Demographics API returned status {response.status}, using default score"
                )
                return 50


async def fetch_competition_score(
    lat: float,
    lng: float,
    radius: float,
    competition_business_categories: list,
    target_num_per_category: int,
) -> int:
    """
    Call the competition scoring API.

    Args:
        lat: Latitude of location
        lng: Longitude of location
        radius: Search radius in meters
        competition_business_categories: List of competing business categories
        target_num_per_category: Target number of competitors per category

    Returns:
        Competition score (0-100)
    """
    url = f"{SCORING_API_BASE_URL}/competition/score"
    payload = {
        "lat": lat,
        "lng": lng,
        "radius": radius,
        "competition_business_categories": competition_business_categories,
        "target_num_per_category": target_num_per_category,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json=payload, timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return int(data.get("score")) * 100
            else:
                logging.warning(
                    f"Competition API returned status {response.status}, using default score"
                )
                return 50


async def fetch_complementary_score(
    lat: float,
    lng: float,
    radius: float,
    complementary_business_categories: list,
    target_num_per_category: int,
) -> int:
    """
    Call the complementary businesses scoring API.

    Args:
        lat: Latitude of location
        lng: Longitude of location
        radius: Search radius in meters
        complementary_business_categories: List of complementary business categories
        target_num_per_category: Target number per category

    Returns:
        Complementary score (0-100)
    """
    url = f"{SCORING_API_BASE_URL}/complementary/score"
    payload = {
        "lat": lat,
        "lng": lng,
        "radius": radius,
        "complementary_business_categories": complementary_business_categories,
        "target_num_per_category": target_num_per_category,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json=payload, timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return int(data.get("score")) * 100
            else:
                logging.warning(
                    f"Complementary API returned status {response.status}, using default score"
                )
                return 50


async def fetch_income_score(
    lat: float, lng: float, radius: float, target_income_level: str
) -> int:
    """
    Call the income scoring API.

    Args:
        lat: Latitude of location
        lng: Longitude of location
        radius: Search radius in meters
        target_income_level: Target income level ("low", "medium", "high")

    Returns:
        Income score (0-100)
    """
    url = f"{SCORING_API_BASE_URL}/income/score"
    payload = {
        "lat": lat,
        "lng": lng,
        "radius": radius,
        "target_income_level": target_income_level,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json=payload, timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return int(data.get("score")) * 100
            else:
                logging.warning(
                    f"Income API returned status {response.status}, using default score"
                )
                return 50


async def fetch_traffic_score(
    lat: float,
    lng: float,
    storefront_direction: str = "north",
    day: str = "Monday",
    time: str = "6PM",
) -> int:
    """
    Call the traffic scoring API.

    Args:
        lat: Latitude of location
        lng: Longitude of location
        storefront_direction: Direction storefront faces ("north", "south", "east", "west")
        day: Day of week
        time: Time of day

    Returns:
        Traffic score (0-100)
    """
    url = f"{SCORING_API_BASE_URL}/traffic/score"
    payload = {
        "lat": lat,
        "lng": lng,
        "storefront_direction": storefront_direction,
        "day": day,
        "time": time,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json=payload, timeout=aiohttp.ClientTimeout(total=360)
        ) as response:
            if response.status == 200:
                data = await response.json()
                return int(data.get("score"))
            else:
                logging.warning(
                    f"Traffic API returned status {response.status}, using default score"
                )
                return 50


def write_html_file(file_path: Path, content: str) -> None:
    """Write HTML content to file"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


async def score_external_location(
    all_shops_data, req, single_item=False
) -> dict:
    """
    Score external locations using API calls to fetch real scores.

    Args:
        all_shops_data: List of shop data or single shop dict
        req: Request object containing evaluation parameters
        single_item: If True, expects single dict instead of list

    Returns:
        Dictionary of scored locations keyed by "lat,lng"
    """
    results = {}

    # Handle None or empty input
    if not all_shops_data:
        return {} if not single_item else None

    if single_item:
        all_shops_data = [all_shops_data]

    # Default parameters for scoring APIs
    radius = 1000  # 1km radius for scoring
    competition_categories = ["pharmacy"]
    complementary_categories = [
        "grocery_store",
        "supermarket",
        "restaurant",
        "bank",
        "atm",
    ]
    target_num_per_category = 5

    # Prepare all scoring tasks
    scoring_tasks = []
    shop_keys = []

    for shop in all_shops_data:
        lat = shop.get("lat")
        lng = shop.get("lng")
        loc_key = f"{lat},{lng}"
        shop_keys.append((loc_key, shop))

        # Create async tasks for parallel API calls
        tasks = {
            "traffic": fetch_traffic_score(lat, lng),
            "demographics": fetch_demographics_score(
                lat, lng, radius, req.target_age
            ),
            "competition": fetch_competition_score(
                lat,
                lng,
                radius,
                competition_categories,
                target_num_per_category,
            ),
            "healthcare": fetch_income_score(
                lat, lng, radius, req.target_income_level
            ),
            "complementary": fetch_complementary_score(
                lat,
                lng,
                radius,
                complementary_categories,
                target_num_per_category,
            ),
        }
        scoring_tasks.append(tasks)

    # Execute all scoring API calls in parallel
    for (loc_key, shop), tasks in zip(shop_keys, scoring_tasks):
        # Gather scores for this location
        scores = await asyncio.gather(
            tasks["traffic"],
            tasks["demographics"],
            tasks["competition"],
            tasks["healthcare"],
            tasks["complementary"],
            return_exceptions=True,
        )

        # Handle any exceptions and set default scores
        traffic_score = scores[0]
        demographics_score = scores[1]
        competition_score = scores[2]
        healthcare_score = scores[3]
        complementary_score = scores[4]

        # Calculate total score with weights
        total_score = (
            traffic_score * req.evaluation_metrics.traffic
            + demographics_score * req.evaluation_metrics.demographics
            + competition_score * req.evaluation_metrics.competition
            + healthcare_score * req.evaluation_metrics.healthcare
            + complementary_score * req.evaluation_metrics.complementary
        )

        results[loc_key] = {
            **shop,
            "id": loc_key,
            "total_score": int(total_score),
            "weighted_scores": {
                "traffic": traffic_score * req.evaluation_metrics.traffic,
                "demographics": demographics_score
                * req.evaluation_metrics.demographics,
                "competition": competition_score
                * req.evaluation_metrics.competition,
                "healthcare": healthcare_score
                * req.evaluation_metrics.healthcare,
                "complementary": complementary_score
                * req.evaluation_metrics.complementary,
            },
            "raw_scores": {
                "traffic": int(traffic_score),
                "demographics": int(demographics_score),
                "competition": int(competition_score),
                "healthcare": int(healthcare_score),
                "complementary": int(complementary_score),
            },
        }

    if single_item:
        results = list(results.values())[0] if results else None
    return results


def score_shops(all_shops_data, req, single_item=False) -> dict:
    # in this part we process all candidates locations data
    results = {}
    if single_item:
        all_shops_data = [all_shops_data]

    for shop in all_shops_data:
        # if traffic_score is None skip this shop
        if not shop.get("traffic_score"):
            continue

        lat = shop.get("lat")
        lng = shop.get("lng")
        # Compose key
        loc_key = f"{lat},{lng}"
        traffic_score = shop.get("traffic_score")
        demographics_score = score_demographics(shop, req)
        healthcare_score = score_healthcare_ecosystem(shop)
        competitive_score = score_competitive(shop)
        complementary_score = score_complementary_businesses(shop)

        total_score = (
            traffic_score * req.evaluation_metrics.traffic
            + demographics_score * req.evaluation_metrics.demographics
            + healthcare_score * req.evaluation_metrics.healthcare
            + competitive_score * req.evaluation_metrics.competition
            + complementary_score * req.evaluation_metrics.complementary
        )

        results[loc_key] = {
            **shop,
            "id": loc_key,
            "total_score": int(total_score),
            "weighted_scores": {
                "traffic": traffic_score * req.evaluation_metrics.traffic,
                "demographics": demographics_score
                * req.evaluation_metrics.demographics,
                "competition": competitive_score
                * req.evaluation_metrics.competition,
                "healthcare": healthcare_score
                * req.evaluation_metrics.healthcare,
                "complementary": complementary_score
                * req.evaluation_metrics.complementary,
            },
            "raw_scores": {
                "traffic": int(traffic_score),
                "demographics": int(demographics_score),
                "competition": int(competitive_score),
                "healthcare": int(healthcare_score),
                "complementary": int(complementary_score),
            },
        }

    return results


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

    current_loc = None
    if req.current_location:
        if req.current_location.lat != 0 and req.current_location.lng != 0:
            current_loc = await group_criterion_data(
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
            all_shops_data.append(current_loc)

    results = score_shops(all_shops_data, req)
    custom_sites = await score_external_location(custom_loc, req)
    current_site = await score_external_location(
        current_loc, req, single_item=True
    )

    stats = calculate_statistics(results)
    stats["total_competing_pharmacies"] = len(pharmacies)
    list_top_n_sites = sorted(
        results.values(), key=lambda s: s.get("total_score", 0), reverse=True
    )[:10]
    custom_results = sorted(
        custom_sites.values(),
        key=lambda s: s.get("total_score", 0),
        reverse=True,
    )[:10]

    # compare top n locations and custom locations with current location
    for site in list_top_n_sites:
        compare_info = compare_values(site, current_site)
        site.update(compare_info)
    for site in custom_results:
        compare_info = compare_values(site, current_site)
        site.update(compare_info)

    best_site = list_top_n_sites[0]

    return (
        results,
        stats,
        list_top_n_sites,
        best_site,
        custom_results,
        current_site,
    )


def make_report_text_sections(
    req,
    sites,
    stats,
    list_top_n_sites,
    best_site,
    custom_sites,
    current_site,
):
    report_text = {}
    report_text["title"] = "🏥 Pharmacy Expansion Analysis — Riyadh"
    report_text["description"] = (
        f"This Comprehensive analysis evaluates {len(sites)} pharmacy locations accorss Riyadh "
        "using advanced location intelligence methodologies. Each locations is systematically socred using "
        "our propiertary, wieghted methodolgy considering "
        "traffic, demographics, competition, healthcare proximity, and complementary businesses."
    )

    return report_text


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
    debug_path_sites = Path("sites.json")
    debug_path_stats = Path("stats.json")
    debug_path_list_top_n_sites = Path("list_top_n_sites.json")
    debug_path_best_site = Path("best_site.json")
    debug_path_custom_sites = Path("custom_sites.json")
    debug_path_current_site = Path("current_site.json")

    (
        sites,
        stats,
        list_top_n_sites,
        best_site,
        custom_sites,
        current_site,
    ) = await get_and_score_listings(req)
    with open(debug_path_sites, "w") as f:
        json.dump(sites, f, indent=4)
    with open(debug_path_stats, "w") as f:
        json.dump(stats, f, indent=4)
    with open(debug_path_list_top_n_sites, "w") as f:
        json.dump(list_top_n_sites, f, indent=4)
    with open(debug_path_best_site, "w") as f:
        json.dump(best_site, f, indent=4)
    with open(debug_path_custom_sites, "w") as f:
        json.dump(custom_sites, f, indent=4)
    with open(debug_path_current_site, "w") as f:
        json.dump(current_site, f, indent=4)

    # read from json files
    with open(debug_path_sites, "r") as f:
        sites = json.load(f)
    with open(debug_path_stats, "r") as f:
        stats = json.load(f)
    with open(debug_path_list_top_n_sites, "r") as f:
        list_top_n_sites = json.load(f)
    with open(debug_path_best_site, "r") as f:
        best_site = json.load(f)
    with open(debug_path_custom_sites, "r") as f:
        custom_sites = json.load(f)
    with open(debug_path_current_site, "r") as f:
        current_site = json.load(f)

    # Generate maps
    logging.info("🗺️  Generating maps...")
    charts = generate_all_charts(list_top_n_sites)
    map_png = create_report_asset_path("candidates_map.png", "image")
    heat_png = create_report_asset_path("demographics_heatmap.png", "image")

    # Generate candidates map
    extent = None

    extent = create_static_map_png(sites, map_png, list_top_n_sites)
    logging.info("✅ Generated candidates map")
    # Generate demographic heatmap
    # create_demographic_heatmap_png(list_top_n_sites, heat_png, extent=extent)
    logging.info("✅ Generated demographic heatmap")
    map_image, html_map = generate_all_site_map_image(list_top_n_sites)
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
    #     best_site,
    # )

    # Generate text content to be embedded in report
    report_text = make_report_text_sections(
        req,
        sites,
        stats,
        list_top_n_sites,
        best_site,
        custom_sites,
        current_site,
    )

    generate_best_site_insights(best_site)

    logging.info("✅ Report generation completed successfully")
    return (
        sites,
        stats,
        list_top_n_sites,
        best_site,
        custom_sites,
        current_site,
        report_text,
    )


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
        Dict[str, Any]
    """

    # Generate the processed report data
    (
        sites,
        stats,
        list_top_n_sites,
        best_site,
        custom_results,
        current_results,
        report_text,
    ) = await generate_pharmacy_report(req)

    # # save all_shops_data to json file for debugging
    # debug_path = Path("processed_report_data.json")
    # with open(debug_path, 'w') as f:
    #     json.dump(processed_report_data, f, indent=4)

    # # read from json file
    # debug_path = Path("processed_report_data.json")
    # with open(debug_path, "r") as f:
    #     processed_report_data = json.load(f)

    # Generate the HTML report file
    html_content = generate_complete_html_report(
        req,
        sites,
        stats,
        list_top_n_sites,
        best_site,
        custom_results,
        current_results,
        report_text,
    )

    html_file_path = Path(DIR_REPORTS) / f"{req.user_id}.html"
    write_html_file(html_file_path, html_content)

    return {
        "html_file_path": html_file_path,
    }


async def loading_category_dataset(req: ReqFetchDataset):

    data = await fetch_dataset(req)
    features = data.get("features", [])
    return features


# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
