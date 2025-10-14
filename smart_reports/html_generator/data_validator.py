"""
Data Validation Module for Pharmacy Report Generation
Validates response data before HTML generation to prevent N/A values
"""
from all_types.request_dtypes import Reqsmartreport
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Custom exception for data validation errors"""

    pass


def validate_response_data(req: Reqsmartreport,
    sites,
    stats,
    list_top_n_sites,
    best_site,
    custom_results,
    current_results,) -> Tuple[bool, str, str]:
    """
    Validate response data structure and determine format type.

    Returns:
        Tuple[bool, str, str]: (is_valid, format_type, error_message)
        format_type: "comparison" | "direct" | "invalid"
    """
    # Check if data has required structure

    if not list_top_n_sites:
        return False, "invalid", "Missing or empty 'list_top_n_sites' array"

    # Analyze first ranking to determine format type
    format_type = _determine_format_type(best_site)

    # Validate based on format type
    if format_type == "comparison":
        is_valid, error = _validate_comparison_format(list_top_n_sites)
    elif format_type == "direct":
        is_valid, error = _validate_direct_format(list_top_n_sites)
    else:
        return False, "invalid", "Unable to determine data format type"

    if not is_valid:
        return False, format_type, error

    logger.info(f"Data validation successful. Format type: {format_type}")
    return True, format_type, ""



def _determine_format_type(site: Dict[str, Any]) -> str:
    """Determine if ranking uses comparison format or direct format"""

    # Check for comparison objects
    comparison_fields = [
        "total_score_comparison",
        "traffic_score_improvement",
        "demographics_score_improvement",
        "competition_score_improvement",
        "healthcare_ecosystem_score_improvement",
        "complementary_businesses_score_improvement",
    ]

    has_comparison = any(
        site[field] is not None and isinstance(site[field], dict)
        for field in comparison_fields
    )

    # Check for direct score fields
    direct_fields = [
        "total_score",
        "traffic_score",
        "demographics_score",
        "competition_score",
        "healthcare_ecosystem_score",
        "complementary_businesses_score",
    ]

    has_direct = any(site[field] is not None for field in direct_fields)

    if has_comparison:
        return "comparison"
    elif has_direct:
        return "direct"
    else:
        return "invalid"


def _validate_comparison_format(list_top_n_sites: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Validate comparison format data"""

    required_comparison_fields = [
        "total_score_comparison",
        "traffic_score_improvement",
        "demographics_score_improvement",
        "competition_score_improvement",
        "healthcare_ecosystem_score_improvement",
        "complementary_businesses_score_improvement",
    ]

    for i, ranking in enumerate(list_top_n_sites):
        # Check comparison objects
        for field in required_comparison_fields:
            comparison_obj = ranking[field]
            if not isinstance(comparison_obj, dict):
                return False, f"Ranking {i+1}: {field} must be an object"

            if comparison_obj:  # If not empty, validate structure
                required_keys = ["value", "comparison_type"]
                for key in required_keys:
                    if key not in comparison_obj:
                        return False, f"Ranking {i+1}: {field} missing '{key}'"

                # Validate comparison_type values
                valid_types = ["improvement", "disadvantage", "same", "difference"]
                if comparison_obj["comparison_type"] not in valid_types:
                    return False, f"Ranking {i+1}: {field} has invalid comparison_type"

    return True, ""


def _validate_direct_format(list_top_n_sites: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Validate direct format data"""

    required_direct_fields = [
        "total_score",
        "traffic_score",
        "demographics_score",
        "competition_score",
        "healthcare_ecosystem_score",
        "complementary_businesses_score",
    ]

    for i, site in enumerate(list_top_n_sites):
        # Check direct score fields
        for field in required_direct_fields:
            value = site[field]

            if not isinstance(value, (int, float)):
                return (
                    False,
                    f"Ranking {i+1}: {field} must be a number, got {type(value)}",
                )

            if value < 0 or value > 100:
                return (
                    False,
                    f"Ranking {i+1}: {field} must be between 0-100, got {value}",
                )

    return True, ""


