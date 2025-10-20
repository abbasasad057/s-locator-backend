# fetchers/complementary_businesses.py
from smart_reports.healthcare_system import process_category_data
from utils.geo_std_utils import calculate_distance_point
from shapely.geometry import Point


def process_category_data(
    area_polygon: dict, lat: float, lng: float, typ, category_data
):
    """
    Extract places of a given category inside the polygon and compute their driving distance.
    """
    results = {f"nearby_{typ}": []}
    for feature in category_data:
        coords = feature.get("geometry", {}).get("coordinates", [])
        if len(coords) != 2:
            continue

        place_lng, place_lat = (
            coords[0],
            coords[1],
        )  # GeoJSON = [place_lng, place_lat]

        # Check if point is inside polygon
        point = Point(place_lng, place_lat)
        if area_polygon.contains(point):
            # Calculate distance
            dist_data = calculate_distance_point(lat, lng, place_lat, place_lng)

            results[f"nearby_{typ}"].append(
                {
                    "name": feature.get("properties", {}).get("name", ""),
                    "coordinates": [place_lng, place_lat],
                    "driving_distance_meters": dist_data["driving_distance_meters"],
                }
            )

    return results


async def get_other_bsusiness_data(
    area_polygon: dict,
    lat: float,
    lng: float,
    grocery_store_data,
    supermarket_data,
    restaurant_data,
    bank_data,
    atm_data,
):
    def top_n_closest(category_results, key, n=5):
        items = category_results.get(key, [])
        items_sorted = sorted(items, key=lambda x: x["est_distance_meters"])
        return items_sorted[:n]

    categories = ["grocery_store", "supermarket", "restaurant", "atm", "bank"]

    input_map = {
        "grocery_store": grocery_store_data,
        "supermarket": supermarket_data,
        "restaurant": restaurant_data,
        "atm": atm_data,
        "bank": bank_data,
    }

    amenities = {}
    num_of_businesses_around = 0
    for category in categories:
        data = input_map.get(category, {})
        key = f"nearby_{category}"
        # Keep the same key name used previously for amenities: 'est_distance_meters'
        results = process_category_data(
            area_polygon, lat, lng, typ=category, category_data=data
        )
        num_of_businesses_around += len(results[key])
        results[key] = top_n_closest(results, key, 5)
        amenities.update(results)

    return {"num_of_businesses_around": num_of_businesses_around, **amenities}


async def get_healthcare_data(
    area_polygon: dict,
    lat: float,
    lng: float,
    hospital_data,
    dentist_data,
    pharmacies_data,
):
    """
    Collect healthcare data (hospitals, dentists, pharmacies), count them, and return top closest results.
    """
    types = ["hospital", "dentist"]
    hospitals = process_category_data(area_polygon, lat, lng, types[0], hospital_data)
    dentists = process_category_data(area_polygon, lat, lng, types[1], dentist_data)
    pharmacies = process_category_data(
        area_polygon, lat, lng, typ="pharmacy", category_data=pharmacies_data
    )
    num_pharmacies = len(pharmacies.get("nearby_pharmacy", []))
    num_hospitals = len(hospitals.get("nearby_hospital", []))
    num_dentists = len(dentists.get("nearby_dentist", []))

    def top_n_closest(category_results, key, n=5):
        items = category_results.get(key, [])
        items_sorted = sorted(items, key=lambda x: x["driving_distance_meters"])
        return items_sorted[:n]

    hospitals["nearby_hospital"] = top_n_closest(hospitals, "nearby_hospital", 5)
    dentists["nearby_dentist"] = top_n_closest(dentists, "nearby_dentist", 5)
    pharmacies["nearby_pharmacy"] = top_n_closest(pharmacies, "nearby_pharmacy", 5)

    return {
        "num_of_pharmacies": num_pharmacies,
        **pharmacies,
        "num_of_hospitals": num_hospitals,
        "num_of_dentists": num_dentists,
        **hospitals,
        **dentists,
    }
