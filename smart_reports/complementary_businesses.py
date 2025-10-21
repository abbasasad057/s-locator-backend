# fetchers/complementary_businesses.py
from utils.geo_std_utils import calculate_distance_point
from shapely.geometry import Point


def get_places_within_driving_distance(
    area_polygon: dict, 
    lat: float, 
    lng: float, 
    typ: str, 
    category_data: list,
    radius_meters: int
):
    """
    Extract places of a given category inside the polygon and compute their driving distance.
    Only includes places within the specified radius.
    
    Args:
        area_polygon: Polygon to check if points are inside
        lat: Center latitude
        lng: Center longitude
        typ: Category type name
        category_data: List of features for this category
        radius_meters: Maximum driving distance in meters
    
    Returns:
        Dictionary with nearby places within the radius
    """
    results = {f"nearby_{typ}": []}
    for feature in category_data:
        coords = feature.get("geometry", {}).get("coordinates", [])
        if len(coords) != 2:
            continue

        place_lng, place_lat = coords[0], coords[1]  # GeoJSON = [lng, lat]

        # Check if point is inside polygon
        point = Point(place_lng, place_lat)
        if area_polygon.contains(point):
            # Calculate distance
            dist_data = calculate_distance_point(lat, lng, place_lat, place_lng)
            driving_distance = dist_data["driving_distance_meters"]
            
            # Only include if within radius
            if driving_distance <= radius_meters:
                results[f"nearby_{typ}"].append(
                    {
                        "name": feature.get("properties", {}).get("name", ""),
                        "coordinates": [place_lng, place_lat],
                        "driving_distance_meters": driving_distance,
                    }
                )

    return results


async def get_all_nearby_businesses(
    area_polygon: dict,
    lat: float,
    lng: float,
    category_data: dict,
    radius_meters: int,
    potential_business_type: str,
    total_population: float = None,
    competition_categories: list = None,
    complementary_categories: list = None,
    cross_shopping_categories: list = None,
):
    """
    Dynamically process all categories from category_data and return nearby businesses
    within the specified radius.
    
    Args:
        area_polygon: Polygon to check if points are inside
        lat: Center latitude
        lng: Center longitude
        category_data: Dictionary mapping category names to their data lists
        radius_meters: Maximum driving distance in meters
        potential_business_type: The main business type being analyzed (e.g., "pharmacy")
        total_population: Total population in the area (optional, for per-10k calculations)
        competition_categories: List of competition category names
        complementary_categories: List of complementary category names
        cross_shopping_categories: List of cross-shopping category names
    
    Returns:
        Dictionary containing:
        - num_of_{category}: Count for each category nearby
        - nearby_{category}: List of nearby places for each category
        - {category}_per_10k_population: Count per 10k population for each category
        - closest_{category}: The closest place of this category (dict with name, coordinates, distance)
        - closest_{category}_distance: Distance in meters to the closest place of this category
        - num_of_competition: Total count of all competition businesses
        - num_of_complementary: Total count of all complementary businesses
        - num_of_cross_shopping: Total count of all cross-shopping businesses
    """
    results = {}
    
    # Initialize aggregate counters
    num_of_competition = 0
    num_of_complementary = 0
    num_of_cross_shopping = 0
    
    for category, data in category_data.items():
        if not data:  # Skip empty categories
            continue
            
        category_results = get_places_within_driving_distance(
            area_polygon, lat, lng, typ=category, category_data=data, radius_meters=radius_meters
        )
        
        nearby_key = f"nearby_{category}"
        nearby_items = category_results.get(nearby_key, [])
        
        # Store the nearby items
        results[nearby_key] = nearby_items
        
        # Store the count for this category
        category_count = len(nearby_items)
        results[f"num_of_{category}"] = category_count
        
        # Accumulate into aggregate counters
        if competition_categories and category in competition_categories:
            num_of_competition += category_count
        if complementary_categories and category in complementary_categories:
            num_of_complementary += category_count
        if cross_shopping_categories and category in cross_shopping_categories:
            num_of_cross_shopping += category_count
        
        # Calculate per 10k population for this category
        if total_population and total_population > 0:
            per_10k = category_count / (total_population / 10000)
        else:
            per_10k = 0
        
        results[f"{category}_per_10k_population"] = per_10k
        
        # Find the closest place for this category
        if nearby_items:
            closest_place = min(
                nearby_items, 
                key=lambda x: x.get("driving_distance_meters", float('inf'))
            )
            results[f"closest_{category}"] = closest_place
            results[f"closest_{category}_distance"] = closest_place.get("driving_distance_meters", float('inf'))
        else:
            results[f"closest_{category}"] = None
            results[f"closest_{category}_distance"] = float('inf')
    
    # Add aggregate counts to results
    results["num_of_competition"] = num_of_competition
    results["num_of_complementary"] = num_of_complementary
    results["num_of_cross_shopping"] = num_of_cross_shopping
    
    return results




