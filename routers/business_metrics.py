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
    # Get configuration
    config_data = BUSINESS_TYPE_CONFIGS[business_type]
    config = BusinessTypeConfig(**config_data)

    return BusinessTypeResponse(success=True, data=config)