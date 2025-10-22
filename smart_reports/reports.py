import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import aiohttp
from all_types.request_dtypes import ReqFetchDataset, Reqsmartreport
from app_logger import get_logger
from backend_common.database import MAX_POOL
from data_fetcher import fetch_dataset
from logging_wrapper import apply_decorator_to_module
from utils.geo_std_utils import bbox_to_polygon, generate_bbox
from utils.utils import DIR_REPORTS, create_report_asset_path

from smart_reports.complementary_businesses import get_all_nearby_businesses
from smart_reports.population import (
    fetch_demographics,
    fetch_household_sizes,
    get_demographic_info_for_listings,
)
from smart_reports.report_generation.map_generator import (
    create_demographic_heatmap_png,
    create_static_map_png,
    generate_all_site_map_image,
)
from smart_reports.report_generation.report_config import source_shop_for_rent
from smart_reports.report_generation.report_object import (
    compare_values,
    generate_best_site_insights,
)
from smart_reports.scoring import score_categories, score_demographics
from smart_reports.traffic import fetch_traffic_data

# Import the modular generator
from .html_generator.pharmacy_generator import generate_complete_html_report
from .report_generation.data_processor import calculate_statistics
from .report_generation.pharmacy_report_final import generate_all_charts
from .report_generation.report_config import (
    source_current_location,
    source_custom_locations,
)

# Traffic API import section
from .traffic_analysis_api import process_traffic_batch

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
    lat: float, lng: float, radius: float, target_age: int, req: Reqsmartreport
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
                demo_score = int(data.get("score"))
            else:
                logging.warning(
                    f"Demographics API returned status {response.status}, using default score"
                )
                demo_score = 50

    income_score = await fetch_income_score(lat, lng, radius, req.target_income_level)

    return demo_score + income_score / 2


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
                competition_score = int(data.get("score"))
            else:
                logging.warning(
                    f"Competition API returned status {response.status}, using default score"
                )
                competition_score = 50

    return competition_score


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
                complementary_score = int(data.get("score"))
            else:
                logging.warning(
                    f"Complementary API returned status {response.status}, using default score"
                )
                complementary_score = 50

    return complementary_score


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
                income_score = int(data.get("score"))
            else:
                logging.warning(
                    f"Income API returned status {response.status}, using default score"
                )
                income_score = 50

    return income_score


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
                traffic_score = int(data.get("score"))
            else:
                logging.warning(
                    f"Traffic API returned status {response.status}, using default score"
                )
                traffic_score = 50

    return traffic_score


async def score_external_location(all_shops_data, req, single_item=False) -> dict:
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
                lat, lng, radius, req.target_age, req
            ),
            "competition": fetch_competition_score(
                lat,
                lng,
                radius,
                competition_categories,
                target_num_per_category,
            ),
            "complementary": fetch_complementary_score(
                lat,
                lng,
                radius,
                ["dental_clinic", "dentist", "doctor", "hospital"],
                target_num_per_category,
            ),
            "cross_shopping": fetch_complementary_score(
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
            tasks["complementary"],
            tasks["cross_shopping"],
            return_exceptions=True,
        )

        # Handle any exceptions and set default scores
        traffic_score = scores[0]
        demographics_score = scores[1]
        competition_score = scores[2]
        complementary_score = scores[3]
        cross_shopping_score = scores[4]

        # Calculate total score with weights
        total_score = (
            traffic_score * req.evaluation_metrics.traffic
            + demographics_score * req.evaluation_metrics.demographics
            + competition_score * req.evaluation_metrics.competition
            + complementary_score * req.evaluation_metrics.complementary
            + cross_shopping_score * req.evaluation_metrics.cross_shopping
        )

        results[loc_key] = {
            **shop,
            "id": loc_key,
            "total_score": int(total_score),
            "weighted_scores": {
                "traffic": traffic_score * req.evaluation_metrics.traffic,
                "demographics": demographics_score
                * req.evaluation_metrics.demographics,
                "competition": competition_score * req.evaluation_metrics.competition,
                "complementary": complementary_score
                * req.evaluation_metrics.complementary,
                "cross_shopping": cross_shopping_score
                * req.evaluation_metrics.cross_shopping,
            },
            "raw_scores": {
                "traffic": int(traffic_score),
                "demographics": int(demographics_score),
                "competition": int(competition_score),
                "complementary": int(complementary_score),
                "cross_shopping": int(cross_shopping_score),
            },
        }

    if single_item:
        results = list(results.values())[0] if results else None
    return results


def write_html_file(file_path: Path, content: str) -> None:
    """Write HTML content to file"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


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
        competitive_score = score_categories(
            shop,
            req.competition_categories,
            req.analysis_radius,
            closer_is_better=False,
            per_10k_threshold=req.max_competition_threshold_per_category,
        )
        complementary_score = score_categories(
            shop,
            req.complementary_categories,
            req.analysis_radius,
            True,
            optimal_count=req.optimal_num_complementary_businesses_per_category,
        )
        cross_shopping_score = score_categories(
            shop,
            req.cross_shopping_categories,
            req.analysis_radius,
            True,
            optimal_count=req.optimal_num_cross_shopping_businesses_per_category,
        )

        total_score = (
            traffic_score * req.evaluation_metrics.traffic
            + demographics_score * req.evaluation_metrics.demographics
            + competitive_score * req.evaluation_metrics.competition
            + complementary_score * req.evaluation_metrics.complementary
            + cross_shopping_score * req.evaluation_metrics.cross_shopping
        )

        results[loc_key] = {
            **shop,
            "id": loc_key,
            "total_score": int(total_score),
            "weighted_scores": {
                "traffic": traffic_score * req.evaluation_metrics.traffic,
                "demographics": demographics_score
                * req.evaluation_metrics.demographics,
                "competition": competitive_score * req.evaluation_metrics.competition,
                "complementary": complementary_score
                * req.evaluation_metrics.complementary,
                "cross_shopping": cross_shopping_score
                * req.evaluation_metrics.cross_shopping,
            },
            "raw_scores": {
                "traffic": int(traffic_score),
                "demographics": int(demographics_score),
                "competition": int(competitive_score),
                "complementary": int(complementary_score),
                "cross_shopping": int(cross_shopping_score),
            },
        }

    return results


async def loading_category_dataset(req: ReqFetchDataset):
    data = await fetch_dataset(req)
    features = data.get("features", [])
    return features


async def group_criterion_data(
    lat: float,
    lng: float,
    Userid: str,
    category_data: dict,
    listing_demographic_info,
    analysis_radius: int,
    potential_business_type: str,
    req: Reqsmartreport,
    source: str = source_shop_for_rent,
    place_name: Optional[str] = None,
    place_price: Optional[float] = None,
    place_url: Optional[str] = None,
):
    """
    Fetch all relevant criterion data for evaluating a shop location.
    Combines demographics and all nearby businesses dynamically.

    Args:
        lat: Latitude of the location
        lng: Longitude of the location
        Userid: User ID
        category_data: Dictionary mapping category names to their data lists.
                      e.g., {"hospital": [...], "pharmacy": [...], "dentist": [...]}
        listing_demographic_info: Demographic information for listings
        analysis_radius: Radius in meters for nearby business search
        potential_business_type: The main business type being analyzed (e.g., "pharmacy")
        req: Request object containing category lists for competition, complementary, and cross_shopping
        source: Source of the location data
        place_name: Name of the place
        place_price: Price of the place
        place_url: URL of the place

    Returns:
        Dictionary containing all location data including demographics and nearby businesses
    """
    info_for_place: dict = listing_demographic_info.get(place_url, {})
    bbox = generate_bbox(lat, lng)
    area_polygon = bbox_to_polygon(bbox=bbox)

    demographics = {key: info_for_place.get(key) for key in POPULATION_KEYS}
    total_population = demographics.get("total_population")

    # Get all nearby businesses dynamically with per-10k calculations
    nearby_businesses = await get_all_nearby_businesses(
        area_polygon,
        lat,
        lng,
        category_data,
        analysis_radius,
        potential_business_type,
        total_population,
        req.competition_categories,
        req.complementary_categories,
        req.cross_shopping_categories,
    )

    return {
        "source": source,
        "display_name": place_name,
        "lat": lat,
        "lng": lng,
        "price": place_price,
        "url": place_url,
        **info_for_place,
        **nearby_businesses,
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

    categories = list(
        set(
            req.competition_categories
            + req.complementary_categories
            + req.cross_shopping_categories
            + [req.potential_business_type]
        )
    )

    # Bounded concurrency to avoid overwhelming DB or upstream APIs. Tune this.
    concurrency_limit = int(MAX_POOL // 2)  # Half of DB pool for fetching datasets
    sem = asyncio.Semaphore(concurrency_limit)

    async def _bounded_load(category: str):
        async with sem:
            rq = req_dataset.model_copy(update={"boolean_query": category})
            return await loading_category_dataset(rq)

    # Load all categories in parallel and store in a dictionary
    category_tasks = {category: _bounded_load(category) for category in categories}
    category_data = {}

    # Gather all results
    results = await asyncio.gather(*category_tasks.values(), return_exceptions=True)

    # Map results back to category names
    for category, result in zip(category_tasks.keys(), results):
        category_data[category] = result

    # get all demograhics + household + income for those shops_for_rent
    # isolate list of listing_ids from shops_for_rent
    listing_demographic_info = await get_demographic_info_for_listings(shops_for_rent)

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
            category_data=category_data,
            analysis_radius=req.analysis_radius,
            potential_business_type=req.potential_business_type,
            req=req,
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
                    category_data=category_data,
                    analysis_radius=req.analysis_radius,
                    potential_business_type=req.potential_business_type,
                    req=req,
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
                category_data=category_data,
                analysis_radius=req.analysis_radius,
                potential_business_type=req.potential_business_type,
                req=req,
                source=source_current_location,
                place_name="Your current location",
                place_price=None,
                listing_demographic_info=listing_demographic_info,
            )
            all_shops_data.append(current_loc)

    results = score_shops(all_shops_data, req)
    custom_sites = await score_external_location(custom_loc, req)
    current_site = await score_external_location(current_loc, req, single_item=True)

    stats = calculate_statistics(results)
    stats[f"total_competing_{req.potential_business_type}"] = len(
        category_data.get(req.potential_business_type, [])
    )
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
        "traffic, demographics, competition, complementary businesses, and cross-shopping opportunities."
    )

    return report_text


async def generate_target_business_report(req: Reqsmartreport):
    """
    Generate a target_business site report with multi-criteria scoring.

    Loads datasets, computes scores for traffic, demographics, complementary,
    competition, and nearby amenities, then returns top-ranked sites.

    Args:
        req (Reqsmartreport): Request with user info and evaluation metrics.

    Returns:
        dict: Target business report with scores and insights.
    """
    debug_path_sites = Path("sites.json")
    debug_path_stats = Path("stats.json")
    debug_path_list_top_n_sites = Path("list_top_n_sites.json")
    debug_path_best_site = Path("best_site.json")
    debug_path_custom_sites = Path("custom_sites.json")
    debug_path_current_site = Path("current_site.json")

    # (
    #     sites,
    #     stats,
    #     list_top_n_sites,
    #     best_site,
    #     custom_sites,
    #     current_site,
    # ) = await get_and_score_listings(req)

    # with open(debug_path_sites, "w") as f:
    #     json.dump(sites, f, indent=4)
    # with open(debug_path_stats, "w") as f:
    #     json.dump(stats, f, indent=4)
    # with open(debug_path_list_top_n_sites, "w") as f:
    #     json.dump(list_top_n_sites, f, indent=4)
    # with open(debug_path_best_site, "w") as f:
    #     json.dump(best_site, f, indent=4)
    # with open(debug_path_custom_sites, "w") as f:
    #     json.dump(custom_sites, f, indent=4)
    # with open(debug_path_current_site, "w") as f:
    #     json.dump(current_site, f, indent=4)

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

    logging.info("Fetching traffic map...")
    process_traffic_batch(
        [
            {"lat": site_data["lat"], "lng": site_data["lng"]}
            for site_data in list_top_n_sites
        ]
    )
    logging.info("✅ Generated traffic map")

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


async def generate_html_report(req: Reqsmartreport) -> Dict[str, Any]:
    """
    Generate a comprehensive target business report and return structured data.

    Creates a multi-page HTML report with executive summary, methodology,
    detailed analysis, and visual components following the specified structure.

    Args:
        req (Reqsmartreport): User request containing target business analysis parameters

    Returns:
        Dict[str, Any]
    """

    # If evaluation_metrics were provided on a scale of 0-100 instead of 0-1, rescale them
    metrics = req.evaluation_metrics
    total_weight = (
        metrics.traffic
        + metrics.demographics
        + metrics.competition
        + metrics.cross_shopping
        + metrics.complementary
    )

    # If total is around 100 (assuming 0-100 scale), rescale to 0-1
    if total_weight > 1:  # Threshold to detect 0-100 scale vs 0-1 scale
        metrics.traffic /= 100.0
        metrics.demographics /= 100.0
        metrics.competition /= 100.0
        metrics.cross_shopping /= 100.0
        metrics.complementary /= 100.0

    # Generate the processed report data
    (
        sites,
        stats,
        list_top_n_sites,
        best_site,
        custom_results,
        current_results,
        report_text,
    ) = await generate_target_business_report(req)

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


# Apply the decorator to all functions in this module
apply_decorator_to_module(logger)(__name__)
