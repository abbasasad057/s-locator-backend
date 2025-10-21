import all_types.request_dtypes as Reqsmartreport


def score_demographics(shop: dict, req: Reqsmartreport) -> dict:
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
    age_score = max(0, 1 - deviation) * 100

    average_score = (age_score + income_score + household_score + housing_score) / 4

    return average_score


def score_categories(shop: dict, categories: list, analysis_radius: int, closer_is_better: bool, optimal_count: int = None, per_10k_threshold: int = None) -> float:
    """
    Universal scoring function for any category type.
    
    Args:
        shop: Location data dictionary
        categories: List of category names to score
        analysis_radius: Radius in meters for distance calculations
        closer_is_better: True if proximity is good (complementary/cross-shopping), False if distance is good (competition)
        optimal_count: Target count for proximity-based categories (complementary/cross-shopping)
        per_10k_threshold: Maximum per-10k threshold for competition categories
    
    Returns:
        Average score (0-100) across all categories
    """
    category_scores = []
    
    for category in categories:
        closest_distance = shop[f"closest_{category}_distance"]
        
        if closer_is_better:
            # Complementary/Cross-shopping logic: closer is better, more is better
            count = shop[f"num_of_{category}"]
            
            # Distance score: 100 at distance 0, 0 at analysis_radius
            if closest_distance == float('inf'):
                distance_score = 0.0
            elif closest_distance <= analysis_radius:
                distance_score = (1.0 - (closest_distance / analysis_radius)) * 100.0
            else:
                distance_score = 0.0
            
            # Count score: linear up to optimal_count
            count_score = min(count / optimal_count, 1.0) * 100.0
            
            category_score = (distance_score + count_score) / 2.0
        else:
            # Competition logic: further is better, fewer per 10k is better
            per_10k = shop[f"{category}_per_10k_population"]
            
            # Distance score: 0 at radius/2, 100 at radius*2 or beyond
            min_distance = analysis_radius / 2
            max_distance = analysis_radius * 2
            
            if closest_distance >= max_distance:
                distance_score = 100.0
            elif closest_distance <= min_distance:
                distance_score = 0.0
            else:
                distance_score = ((closest_distance - min_distance) / (max_distance - min_distance)) * 100.0
            
            # Saturation score: 100 at 0, 0 at threshold or above
            if per_10k >= per_10k_threshold:
                saturation_score = 0.0
            else:
                saturation_score = (1.0 - (per_10k / per_10k_threshold)) * 100.0
            
            category_score = (distance_score + saturation_score) / 2.0
        
        category_scores.append(category_score)
    
    return sum(category_scores) / len(category_scores)
