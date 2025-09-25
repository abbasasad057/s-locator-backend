from storage_methods import fetch_intelligence_by_viewport
from backend_common.database import Database
from all_types.request_dtypes import ReqIntelligenceViewport
from all_types.internal_types import Feature

async def fetch_demographics(bbox : dict , user_id : str):
    req_bbox = ReqIntelligenceViewport(   
        top_lng=bbox["top_lng"],
        top_lat=bbox["top_lat"],
        bottom_lng=bbox["bottom_lng"],
        bottom_lat=bbox["bottom_lat"],
        user_id=user_id,
        zoom_level=12,
        income=True,
        population=True
    )
    data = await fetch_intelligence_by_viewport(req_bbox)
    features = data["features"]
    ## Return zeros values in case of an empty dict
    if not features:
            return {
        "total_population": 1500,
        "avg_density": 3000.0,  # Half of MAX_DENSITY from scoring
        "avg_median_age": 28.0,
        "avg_income": 5500.0,   # Half of MAX_INCOME from scoring
        "percentage_age_above_35": 30.0  # Half of max age percentage
        }
    
    total_population = 0
    pop_density_values = []
    age_values = []
    income_values = []
    for f in features:
        props = f["properties"]
        total_population += props.get("Population_Count")
        pop_density_values.append(props.get("Population_Density_KM2", 0))
        age_values.append(props.get("Median_Age_Total") or 0)
        income_values.append(props.get("income", 0))
    processed = {
    "total_population": total_population,
    "avg_density": round((sum(pop_density_values) / len(pop_density_values)), 2),
    "avg_median_age": round((sum(age_values) / len(age_values)), 2),
    "avg_income": round((sum(income_values) / len(income_values)), 2),
        }

    # Add derived percentages
    percentage_age_above_35 = (processed.get("avg_median_age", 0) - 35 + 50)

    processed.update({
        "percentage_age_above_35": percentage_age_above_35,
    })

    return processed

async def fetch_household_sizes(bbox : dict):
    try:
        query = """
            SELECT 
                AVG("Household_Average_Size")::INT AS avg_household_size,
                AVG("Household_Median_Size")::INT AS avg_median_size
            FROM schema_marketplace.household_all_features_v12
            WHERE ST_Intersects(
                geometry,
                ST_MakeEnvelope($1, $2, $3, $4, 4326)
            )
        """
        
        row = await Database.fetchrow(
            query,
            bbox["bottom_lng"],
            bbox["bottom_lat"],
            bbox["top_lng"],
            bbox["top_lat"]
        )

        return {
            "Household_Average_Size": row["avg_household_size"] if row["avg_household_size"] else 0,
            "Household_Median_Size":  row["avg_median_size"] if row["avg_median_size"] else 0,
        }
    except Exception as e:
        print(f"Failed to fetch household data: {str(e)}")
        return {
            "Household_Average_Size": 0,
            "Household_Median_Size": 0,
        }


async def get_demographic_info_for_listings(shop_for_rent:list[Feature]):
    # make list of listing_id
    listing_ids = [f['properties']['listing_id'] for f in shop_for_rent]
    sanitized_ids = [int(i) for i in listing_ids]
    # query real estate table and filter for those ids
    query = """
    SELECT
        listing_id, url, city, price, latitude, longitude, category, direction_id,
        total_population, avg_density, avg_median_age, avg_income,
        percentage_age_above_20, percentage_age_above_25, percentage_age_above_30,
        percentage_age_above_35, percentage_age_above_40, percentage_age_above_45,
        percentage_age_above_50, demographics_analysis_date,
        traffic_score, traffic_storefront_score, traffic_area_score,
        traffic_screenshot_filename, traffic_analysis_date
    FROM schema_marketplace.saudi_real_estate
    WHERE listing_id = ANY($1::BIGINT[])
    """

    rows = await Database.fetch(query, sanitized_ids)
    # Database.fetch should accept a list parameter that maps to $1
    # If your Database.fetch expects positional args instead of array param,
    # you can pass tuple(sanitized_ids) or adapt the query to use UNNEST.

    # convert to dictionary with url as key
    return {row["url"]: row for row in rows}
