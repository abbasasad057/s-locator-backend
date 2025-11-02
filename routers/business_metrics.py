"""
Business Metrics Router Module
Handles business category metrics configuration for different business types
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from enum import Enum
from all_types.response_dtypes import (
    BusinessTypeResponse,
    BusinessTypeConfig,
)
from preloaded_constants import ALL_POI_CATEGORIES_LOWER

business_metrics_router = APIRouter()

# Path to JSON file
BUSINESS_TYPES_FILE = (
    Path(__file__).resolve().parent.parent / "business_types_config.json"
)


class BusinessType(str, Enum):
    PHARMACY = "pharmacy"
    CAFE = "cafe"
    RETAIL = "retail"
    RESTAURANT = "restaurant"
    WAREHOUSE = "warehouse"


# Load business type configurations from JSON file
def load_business_type_configs():
    with open(BUSINESS_TYPES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


BUSINESS_TYPE_CONFIGS = load_business_type_configs()


@business_metrics_router.get(
    "/fastapi/business_category_metrics/{business_type}",
    response_model=BusinessTypeResponse,
)
async def get_business_category_metrics(business_type: str):
    """
    Get evaluation metrics configuration for a specific business type.
    """
    # Get configuration, fallback to pharmacy if business_type not found
    config_data = BUSINESS_TYPE_CONFIGS.get(business_type)
    if config_data is None:
        # Use pharmacy as fallback for metrics, but empty categories
        pharmacy_config = BUSINESS_TYPE_CONFIGS["pharmacy"].copy()
        config_data = {
            "business_type": business_type,
            "display_name": business_type.title(),
            "icon": "🏪",  # Generic business icon
            "description": f"Analysis for {business_type.title()} business type",
            "competition_categories": [],
            "complementary_categories": [],
            "cross_shopping_categories": [],
            "metrics": pharmacy_config["metrics"]
        }
    
    # Validate categories exist in POI list
    all_categories = (
        config_data.get("competition_categories", []) +
        config_data.get("complementary_categories", []) +
        config_data.get("cross_shopping_categories", [])
    )
    
    invalid_categories = [cat for cat in all_categories if cat.lower() not in ALL_POI_CATEGORIES_LOWER]
    if invalid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid categories in config: {invalid_categories}"
        )
    
    config = BusinessTypeConfig(**config_data)

    return BusinessTypeResponse(success=True, data=config)