"""
Data Validation Module for Pharmacy Report Generation
Validates response data before HTML generation to prevent N/A values
"""

from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Custom exception for data validation errors"""

    pass


def validate_response_data(data: Dict[str, Any]) -> Tuple[bool, str, str]:
    """
    Validate response data structure and determine format type.

    Returns:
        Tuple[bool, str, str]: (is_valid, format_type, error_message)
        format_type: "comparison" | "direct" | "invalid"
    """
    try:
        # Check if data has required structure
        if not isinstance(data, dict):
            return False, "invalid", "Data must be a dictionary"
        rankings = data.get("rankings", [])

        if not rankings:
            data_section = data.get("data", {})
            if data_section:
                rankings = data_section.get("rankings", [])

        if not rankings:
            return False, "invalid", "Missing or empty 'rankings' array"

        if not isinstance(rankings, list):
            return False, "invalid", "'rankings' must be an array"

        # Analyze first ranking to determine format type
        first_ranking = rankings[0]
        format_type = _determine_format_type(first_ranking)

        # Validate based on format type
        if format_type == "comparison":
            is_valid, error = _validate_comparison_format(rankings)
        elif format_type == "direct":
            is_valid, error = _validate_direct_format(rankings)
        else:
            return False, "invalid", "Unable to determine data format type"

        if not is_valid:
            return False, format_type, error

        logger.info(f"Data validation successful. Format type: {format_type}")
        return True, format_type, ""

    except Exception as e:
        logger.error(f"Data validation failed with exception: {str(e)}")
        return False, "invalid", f"Validation error: {str(e)}"


def _determine_format_type(ranking: Dict[str, Any]) -> str:
    """Determine if ranking uses comparison format or direct format"""

    # Check for comparison objects
    comparison_fields = [
        "final_score_comparison",
        "traffic_score_comparison",
        "demographics_score_comparison",
        "competition_score_comparison",
        "healthcare_ecosystem_score_comparison",
        "complementary_businesses_score_comparison",
    ]

    has_comparison = any(
        ranking.get(field) and isinstance(ranking.get(field), dict)
        for field in comparison_fields
    )

    # Check for direct score fields
    direct_fields = [
        "final_score",
        "traffic_score",
        "demographics_score",
        "competition_score",
        "healthcare_ecosystem_score",
        "complementary_businesses_score",
    ]

    has_direct = any(ranking.get(field) is not None for field in direct_fields)

    if has_comparison:
        return "comparison"
    elif has_direct:
        return "direct"
    else:
        return "invalid"


def _validate_comparison_format(rankings: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Validate comparison format data"""

    required_comparison_fields = [
        "final_score_comparison",
        "traffic_score_comparison",
        "demographics_score_comparison",
        "competition_score_comparison",
        "healthcare_ecosystem_score_comparison",
        "complementary_businesses_score_comparison",
    ]

    for i, ranking in enumerate(rankings):
        # Check basic fields
        if not ranking.get("site_name"):
            return False, f"Ranking {i+1}: Missing site_name"

        if not ranking.get("rank"):
            return False, f"Ranking {i+1}: Missing rank"

        # Check comparison objects
        for field in required_comparison_fields:
            comparison_obj = ranking.get(field, {})
            if not isinstance(comparison_obj, dict):
                return False, f"Ranking {i+1}: {field} must be an object"

            if comparison_obj:  # If not empty, validate structure
                required_keys = ["value", "comparison_type"]
                for key in required_keys:
                    if key not in comparison_obj:
                        return False, f"Ranking {i+1}: {field} missing '{key}'"

                # Validate comparison_type values
                valid_types = ["improvement", "disadvantage", "same", "difference"]
                if comparison_obj.get("comparison_type") not in valid_types:
                    return False, f"Ranking {i+1}: {field} has invalid comparison_type"

    return True, ""


def _validate_direct_format(rankings: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Validate direct format data"""

    required_direct_fields = [
        "final_score",
        "traffic_score",
        "demographics_score",
        "competition_score",
        "healthcare_ecosystem_score",
        "complementary_businesses_score",
    ]

    for i, ranking in enumerate(rankings):
        # Check basic fields
        if not ranking.get("site_name"):
            return False, f"Ranking {i+1}: Missing site_name"

        if not ranking.get("rank"):
            return False, f"Ranking {i+1}: Missing rank"

        # Check direct score fields
        for field in required_direct_fields:
            value = ranking.get(field)
            if value is None:
                return False, f"Ranking {i+1}: Missing {field}"

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


def validate_inputs(response_data: Dict[str, Any]) -> str:
    """
    Main validation function that raises exception if data is invalid.

    Args:
        response_data: The response data to validate

    Returns:
        str: Format type ("comparison" or "direct")

    Raises:
        DataValidationError: If data is invalid
    """
    is_valid, format_type, error_message = validate_response_data(response_data)

    if not is_valid:
        raise DataValidationError(f"Data validation failed: {error_message}")

    if format_type not in ["comparison", "direct"]:
        raise DataValidationError(f"Invalid format type detected: {format_type}")

    logger.info(f"Data validation passed. Format: {format_type}")
    return format_type
