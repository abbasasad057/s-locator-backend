from typing import List, Dict, Optional, Any

MAX_TOTAL = 100


def generate_detailed_insights_dict(site: Dict) -> Dict[str, Any]:
    """Generate detailed insights as a dictionary structure."""
    insights = {}

    # Traffic Performance
    traffic_score = site["raw_scores"]["traffic"]
    if traffic_score is not None:
        if 20 <= traffic_score <= 30:
            traffic_status = "Optimal traffic — moderate traffic flow ensures both convenience and visibility."
            traffic_level = "optimal"
        elif traffic_score < 20:
            traffic_status = "Heavy congestion — low traffic speed may reduce accessibility but can increase local visibility."
            traffic_level = "congested"
        else:
            traffic_status = "Light traffic — smooth access but potentially less exposure to passersby."
            traffic_level = "light"

        insights["traffic_performance"] = {
            "current_speed_kmh": round(traffic_score, 1),
            "target_range": "20-30 km/h",
            "status": traffic_status,
            "level": traffic_level,
        }

    # Business Environment
    nearby_businesses = site["num_of_businesses_around"]
    if nearby_businesses > 20:
        bus_status = (
            "Strong ecosystem — complementary businesses support customer flow."
        )
        ecosystem_level = "strong"
    elif nearby_businesses >= 10:
        bus_status = "Moderate ecosystem — some opportunities exist, but growth potential remains."
        ecosystem_level = "moderate"
    else:
        bus_status = "Weak ecosystem — limited complementary activity may reduce visibility."
        ecosystem_level = "weak"

    insights["business_environment"] = {
        "nearby_businesses_500m": nearby_businesses,
        "assessment": bus_status,
        "ecosystem_level": ecosystem_level,
    }

    # Demographics Match
    age_above_35 = site["percentage_age_above_35"]
    avg_income = site["avg_income"]
    if age_above_35 is not None:
        if age_above_35 >= 40:
            age_status = "Strong alignment — high share of population above 35, consistent with core demand segment."
            alignment_level = "strong"
        elif age_above_35 >= 25:
            age_status = (
                "Partial alignment — balanced age structure with moderate fit."
            )
            alignment_level = "partial"
        else:
            age_status = "Weak alignment — younger population may reduce pharmacy demand."
            alignment_level = "weak"

        insights["demographics_match"] = {
            "population_age_35_plus_percent": round(age_above_35, 1),
            "average_income_sar": avg_income,
            "assessment": age_status,
            "alignment_level": alignment_level,
        }

    # Competitive Position
    pharm_per_10k = site["pharmacies_per_10k_population"]
    if pharm_per_10k is not None:
        if pharm_per_10k > 8:
            market_status = "Saturated market - Differentiation is essential to compete effectively."
            market_level = "saturated"
        elif pharm_per_10k >= 4:
            market_status = "Moderately competitive - Focus on service quality and location advantage."
            market_level = "moderate"
        else:
            market_status = (
                "Underserved market - Strong opportunity for entry and growth."
            )
            market_level = "underserved"

        insights["competitive_position"] = {
            "pharmacies_per_10k_population": round(pharm_per_10k, 1),
            "total_competing_pharmacies": site["num_of_pharmacies"],
            "market_status": market_status,
            "market_level": market_level,
        }
    hospitals = site["num_of_hospitals"]
    dentists = site["num_of_dentists"]

    if hospitals + dentists > 10:
        health_status = "✅ Strong healthcare hub — high concentration of facilities ensures steady demand."
    elif hospitals + dentists >= 5:
        health_status = "⚠️ Moderate healthcare presence — demand is supported but with limited spillover."
    else:
        health_status = "❌ Weak healthcare presence — fewer facilities may reduce referral opportunities."

    insights["healthcare_environment"] = {
        "hospitals_around": hospitals,
        "dentists_around": dentists,
        "healthcare_places": hospitals + dentists,
        "healthcare_market_status": health_status,
    }
    return insights


def generate_best_site_insights(best_site: Dict) -> List[Dict[str, Any]]:
    """Generate key investment insights as structured data."""
    # insights = []

    # Prime opportunity
    best_site["total_category"] = "Prime Opportunity"
    best_site["total_description"] = (
        f"{best_site['display_name']} emerges as the clear market leader with exceptional potential scoring {best_site['total_score']} points."
    )


    # Market dynamics
    competition_score = best_site["raw_scores"]['competition']
    total_competitors = best_site["num_of_pharmacies"]
    
    # For competition, higher score means less competition (better for business)
    if competition_score >= 75:
        market_status = "Emerging market with minimal competition"
        market_level = "emerging"
    elif competition_score >= 50:
        market_status = "Moderately competitive market with room for growth"
        market_level = "competitive"
    else:
        market_status = "Highly saturated market requires strong differentiation strategy"
        market_level = "saturated"

    # Market color and icon logic (for market competition, emerging is good)
    if market_level == "emerging":
        market_color = "#2ecc71"
        market_icon = "🟢 Emerging"
    elif market_level == "competitive":
        market_color = "#f39c12"
        market_icon = "🟡 Competitive"
    else:  # saturated
        market_color = "#e74c3c"
        market_icon = "🔴 Saturated"

    best_site["market_category"] = "Market Dynamics"
    best_site["market_description"] = (
        f"{market_status} scoring {competition_score} points with {total_competitors} total competing pharmacies."
    )
    best_site["market_level"] = market_level
    best_site["market_color"] = market_color
    best_site["market_icon"] = market_icon


    # Traffic advantage
    traffic_score = best_site["raw_scores"]['traffic']
    if traffic_score >= 75:
        traffic_status = "Excellent accessibility with optimal traffic flow"
        traffic_level = "excellent"
        traffic_color = "#2ecc71"
        traffic_icon = "🟢 Excellent"
    elif traffic_score >= 50:
        traffic_status = "Good accessibility with moderate traffic conditions"
        traffic_level = "good"
        traffic_color = "#f39c12"
        traffic_icon = "🟡 Good"
    else:
        traffic_status = "Average accessibility with some traffic challenges"
        traffic_level = "average"
        traffic_color = "#e74c3c"
        traffic_icon = "🔴 Average"

    best_site["traffic_category"] = "Traffic Advantage"
    best_site["traffic_description"] = (
        f"{traffic_status} scoring {traffic_score} points."
    )
    best_site["traffic_level"] = traffic_level
    best_site["traffic_color"] = traffic_color
    best_site["traffic_icon"] = traffic_icon

    # Business ecosystem
    business_score = best_site["raw_scores"]['complementary']
    num_businesses = best_site['num_of_businesses_around']
    if business_score >= 75:
        business_status = "Thriving commercial hub with exceptional foot traffic potential"
        business_level = "excellent"
        business_color = "#2ecc71"
        business_icon = "🟢 Excellent"
    elif business_score >= 50:
        business_status = "Active business district with good cross-selling opportunities"
        business_level = "good"
        business_color = "#f39c12"
        business_icon = "🟡 Good"
    else:
        business_status = "Moderate business presence with basic commercial activity"
        business_level = "average"
        business_color = "#e74c3c"
        business_icon = "🔴 Average"

    best_site["business_category"] = "Business Ecosystem"
    best_site["business_description"] = (
        f"{business_status} scoring {business_score} points with {num_businesses} nearby complementary businesses."
    )
    best_site["business_level"] = business_level
    best_site["business_color"] = business_color
    best_site["business_icon"] = business_icon

    # Demographic alignment
    demographics_score = best_site["raw_scores"]['demographics']
    if demographics_score >= 75:
        demographics_status = "Exceptional demographic match with target customer profile"
        demographics_level = "excellent"
        demographics_color = "#2ecc71"
        demographics_icon = "🟢 Excellent"
    elif demographics_score >= 50:
        demographics_status = "Strong demographic alignment with good market potential"
        demographics_level = "good"
        demographics_color = "#f39c12"
        demographics_icon = "🟡 Good"
    else:
        demographics_status = "Adequate demographic fit with moderate market appeal"
        demographics_level = "average"
        demographics_color = "#e74c3c"
        demographics_icon = "🔴 Average"

    best_site["demographics_category"] = "Demographic Alignment"
    best_site["demographics_description"] = (
        f"{demographics_status} scoring {demographics_score} points."
    )
    best_site["demographics_level"] = demographics_level
    best_site["demographics_color"] = demographics_color
    best_site["demographics_icon"] = demographics_icon

    # Healthcare environment
    healthcare_score = best_site["raw_scores"]['healthcare']
    num_hospitals = best_site['num_of_hospitals']
    num_dentists = best_site['num_of_dentists']
    healthcare_facilities = num_hospitals + num_dentists
    
    if healthcare_score >= 75:
        healthcare_status = "Prime healthcare hub with strong referral network"
        healthcare_level = "excellent"
        healthcare_color = "#2ecc71"
        healthcare_icon = "🟢 Excellent"
    elif healthcare_score >= 50:
        healthcare_status = "Active medical district with good patient flow"
        healthcare_level = "good"
        healthcare_color = "#f39c12"
        healthcare_icon = "🟡 Good"
    else:
        healthcare_status = "Basic healthcare presence with limited medical synergy"
        healthcare_level = "average"
        healthcare_color = "#e74c3c"
        healthcare_icon = "🔴 Average"

    best_site["healthcare_category"] = "Healthcare Environment"
    best_site["healthcare_description"] = (
        f"{healthcare_status} scoring {healthcare_score} points with {healthcare_facilities} nearby medical facilities ({num_hospitals} hospitals, {num_dentists} dental clinics)."
    )
    best_site["healthcare_level"] = healthcare_level
    best_site["healthcare_color"] = healthcare_color
    best_site["healthcare_icon"] = healthcare_icon




def generate_rankings_dict(
    sites: List[Dict]
) -> List[Dict[str, Any]]:
    """Generate rankings as structured data."""

    rankings = []
    for i, site in enumerate(sites, start=1):
        # Convert all scores to 100 scale for display
        total_score_100 = (site["total_score"] / MAX_TOTAL) * 100
        traffic_100 = site["weighted_scores"]["traffic"]
        demographics_100 = site["weighted_scores"][
            "demographics"
        ]
        competitive_100 = site["weighted_scores"]["competition"]
        healthcare_100 = site["weighted_scores"]["healthcare"]
        complementary_100 = site["weighted_scores"][
            "complementary"
        ]

        rankings.append(
            {
                "rank": site["rank"],
                "traffic_score": round(traffic_100, 1),
                "demographics_score": round(demographics_100, 1),
                "competition_score": round(competitive_100, 1),
                "healthcare_ecosystem_score": round(healthcare_100, 1),
            }
        )

        rankings.append(
            {
                "rank": site["rank"],
                "display_name": site["display_name"],
                "price": (
                    site["price"] if site["price"] else None
                ),
                "total_score": round(total_score_100, 1),
                "traffic_score": round(traffic_100, 1),
                "demographics_score": round(demographics_100, 1),
                "competition_score": round(competitive_100, 1),
                "healthcare_ecosystem_score": round(healthcare_100, 1),
                "complementary_businesses_score": round(complementary_100, 1),
                "url": site["url"],
            }
        )

    return rankings


def compare_values(site, current_site):
    if not current_site:
        return {
            "percentage_difference": None,
            "comparison_type": "N/A",
            "traffic_score_improvement": None,
            "demographics_score_improvement": None,
            "competition_score_improvement": None,
            "healthcare_ecosystem_score_improvement": None,
            "complementary_businesses_score_improvement": None,
        }
    
    # Total score comparison
    site_score = site["total_score"]
    current_score = current_site["total_score"]
    diff_pct = abs(site_score - current_score)
    
    if site_score > current_score:
        comparison_type = "improvement"
    elif site_score < current_score:
        comparison_type = "disadvantage"
    else:
        comparison_type = "same"

    # Sub-score comparisons
    site_raw_scores = site["raw_scores"]
    current_raw_scores = current_site["raw_scores"]

    # Traffic score comparison
    traffic_site = site_raw_scores["traffic"]
    traffic_current = current_raw_scores["traffic"]
    traffic_diff = abs(traffic_site - traffic_current)
    
    # Demographics score comparison
    demo_site = site_raw_scores["demographics"]
    demo_current = current_raw_scores["demographics"]
    demo_diff = abs(demo_site - demo_current)
    
    # Competition score comparison
    comp_site = site_raw_scores["competition"]
    comp_current = current_raw_scores["competition"]
    comp_diff = abs(comp_site - comp_current)
    
    # Healthcare ecosystem score comparison
    health_site = site_raw_scores["healthcare"]
    health_current = current_raw_scores["healthcare"]
    health_diff = abs(health_site - health_current)
    
    # Complementary businesses score comparison
    complement_site = site_raw_scores["complementary"]
    complement_current = current_raw_scores["complementary"]
    complement_diff = abs(complement_site - complement_current)

    return {
        "percentage_difference": int(diff_pct),
        "comparison_type": comparison_type,
        "traffic_score_improvement": int(traffic_diff),
        "demographics_score_improvement": int(demo_diff),
        "competition_score_improvement": int(comp_diff),
        "healthcare_ecosystem_score_improvement": int(health_diff),
        "complementary_businesses_score_improvement": int(complement_diff),
    }


def generate_rankings_dict_with_current_comparison(
    top_sites: List[Dict],
    current_location: List[Dict],
) -> List[Dict[str, Any]]:
    """
    Generate rankings as structured data with comparisons to current_location.
    Returns comparison format: {
        "value": top_val,
        "current_value": curr_val,
        "percentage_difference": XX.X,
        "comparison_type": "improvement"|"disadvantage"|"same",
        "display_text": "top_val (curr_val, XX% improvement)"
    }
    """

    if not top_sites:
        return []
    if not current_location:
        # fallback: no comparison, use original function
        return generate_rankings_dict(top_sites)

    current = current_location[0]  # baseline
    rankings = []

    # Helper to format comparison data
    for i, site in enumerate(top_sites, start=1):
        # Top site scores normalized to 100
        total_score = (site["total_score"] / MAX_TOTAL) * 100
        traffic = site["weighted_scores"]["traffic"]
        demographics = site["weighted_scores"]["demographics"]
        competition = site["weighted_scores"]["competition"]
        healthcare = site["weighted_scores"]["healthcare"]
        complementary = site["weighted_scores"]["complementary"]

        # Current location normalized scores
        curr_final = (current["total_score"] / MAX_TOTAL) * 100
        curr_traffic = current["weighted_scores"]["traffic"]
        curr_demo = current["weighted_scores"]["demographics"]
        curr_comp = current["weighted_scores"]["competition"]
        curr_health = current["weighted_scores"]["healthcare"]
        curr_complement = current["weighted_scores"][
            "complementary"
        ]

        # Generate comparison data for each metric
        final_comparison = compare_values(total_score, curr_final)
        traffic_comparison = compare_values(traffic, curr_traffic)
        demographics_comparison = compare_values(demographics, curr_demo)
        competition_comparison = compare_values(competition, curr_comp)
        healthcare_comparison = compare_values(healthcare, curr_health)
        complementary_comparison = compare_values(
            complementary, curr_complement
        )

        rankings.append(
            {
                "rank": site["rank"],
                "display_name": site["display_name"],
                "price": (
                    site["price"] if site["price"] else None
                ),
                "total_score_comparison": (
                    final_comparison if final_comparison else {}
                ),
                "traffic_score_improvement": traffic_comparison,
                "demographics_score_improvement": demographics_comparison,
                "competition_score_improvement": competition_comparison,
                "healthcare_ecosystem_score_improvement": healthcare_comparison,
                "complementary_businesses_score_improvement": complementary_comparison,
                "url": site["url"],
            }
        )

    return rankings
