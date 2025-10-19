import all_types.request_dtypes as Reqsmartreport

def score_demographics(shop: dict, req:Reqsmartreport) -> dict:
    """
    Returns dict with weighted overall score and detailed scores.
    """
    tgt_income_string = req.target_income_level
    tgt_age = req.target_age
    

    income_score = shop.get(f"income_score_{tgt_income_string}", 0)
    avg_median_age = shop.get("avg_median_age", 0)
    housing_score = shop.get("housing_score", 0)
    household_score = shop.get("household_score", 0)

    deviation = abs(avg_median_age - tgt_age) / tgt_age
    age_score = max(0, 1 - deviation)*100

    average_score = (
        age_score + income_score + household_score + housing_score
    ) / 4

    return average_score


def score_competitive(shop):
    # Ensure healthcare_data has the expected structure
    if not shop or "pharmacy" not in shop:
        return 0

    nearby_pharmacies = shop.get("nearby_pharmacy", [])

    # Ensure pharmacies_per_10k is a float
    pharmacies_per_10k = shop.get("pharmacies_per_10k_population")

    if nearby_pharmacies:
        closest_pharmacy_distance = min(
            float(p["driving_distance_meters"]) for p in nearby_pharmacies
        )
    else:
        closest_pharmacy_distance = 3000  # large distance, underserved
    
    # calculate distance score between 0 and 100
    # 1.0 score if further than 5km
    # 0 score if closer than 0.5km
    MIN_DISTANCE = 500  # 0.5km in meters
    MAX_DISTANCE = 5000  # 5km in meters

    if closest_pharmacy_distance <= MIN_DISTANCE:
        distance_score = 0.0
    elif closest_pharmacy_distance >= MAX_DISTANCE:
        distance_score = 1.0
    else:
        distance_score = (closest_pharmacy_distance - MIN_DISTANCE) / (MAX_DISTANCE - MIN_DISTANCE)

    distance_score = distance_score * 100.0

    # saturation score internally on 0.0..1.0
    # max (1.0) when pharmacies_per_10k == 0, min (0.0) when >= 5
    SAT_THRESHOLD = 3.0
    if pharmacies_per_10k <= 0:
        saturation_score = 1.0
    elif pharmacies_per_10k >= SAT_THRESHOLD:
        saturation_score = 0.0
    else:
        saturation_score = 1.0 - (pharmacies_per_10k / SAT_THRESHOLD)

    saturation_score = saturation_score * 100.0

    average_score = (distance_score + saturation_score) / 2.0


    return average_score


def score_healthcare_ecosystem(shop):
    # Ensure healthcare_data is not None
    if not shop:
        return 0

    PROXIMITY_MAX_DISTANCE = 1000  # 1km in meters
    MAX_COUNT_FOR_FULL_SCORE = 2  # 2 or more places gives max score

    # Score hospitals
    hospitals = shop.get("nearby_hospital", [])
    hospitals_within_range = [
        h for h in hospitals 
        if float(h["driving_distance_meters"]) <= PROXIMITY_MAX_DISTANCE
    ]
    hospitals_count = len(hospitals_within_range)
    hospitals_score = (hospitals_count / MAX_COUNT_FOR_FULL_SCORE) * 100

    # Score dentists
    dentists = shop.get("nearby_dentist", [])
    dentists_within_range = [
        d for d in dentists 
        if float(d["driving_distance_meters"]) <= PROXIMITY_MAX_DISTANCE
    ]
    dentists_count = len(dentists_within_range)
    dentists_score = (dentists_count / MAX_COUNT_FOR_FULL_SCORE) * 100

    # Average of both scores
    average_score = (hospitals_score + dentists_score) / 2
    
    return average_score 


def score_complementary_businesses(shop):
    # Ensure amenities_data is not None
    if not shop:
        return 0

    MAX_DISTANCE = 1000  # meters, max cutoff for proximity scoring

    def proximity_score(places):
        if not places:
            return 0.0
        # Score for each place: 1 - (distance / MAX_DISTANCE), clipped to [0,1]
        try:
            scores = [
                max(
                    0,
                    1 - (float(p["est_distance_meters"]) / (MAX_DISTANCE * 2)),
                )
                for p in places
            ]
            # Average score for all places of this type
            return min(1, (sum(scores) / len(scores)) + (len(places) * 0.05))
        except (ValueError, TypeError):
            return 0.0

    grocery_score = proximity_score(
        shop.get("nearby_grocery_store", [])
    )
    supermarket_score = proximity_score(
        shop.get("nearby_supermarket", [])
    )
    restaurant_score = proximity_score(
        shop.get("nearby_restaurant", [])
    )
    atm_score = proximity_score(
        shop.get("nearby_atm", [])
    )
    bank_score = proximity_score(
        shop.get("nearby_bank", [])
    )

    # Equal weight average of all five types
    average_score = (
        grocery_score
        + supermarket_score
        + restaurant_score
        + atm_score
        + bank_score
    ) / 5
    average_score = average_score * 100

    return average_score