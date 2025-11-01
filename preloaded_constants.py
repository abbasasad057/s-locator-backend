from all_types.request_dtypes import Dict, ReqCityCountry
from storage_methods import ALL_POI_CATEGORIES_DICT, AREA_INTELLIGENCE_CATEGORIES


from typing import Dict


async def poi_categories() -> Dict:
    """
    Provides a comprehensive list of place categories, including Google places,
    real estate, and other custom categories.

    Returns the pre-loaded ALL_POI_CATEGORIES_DICT from storage_methods.
    This is the same source of truth used by validators.
    """
    return ALL_POI_CATEGORIES_DICT


async def load_area_intelligence_categories(req: ReqCityCountry = "") -> Dict:
    """
    Loads and returns a dictionary of area intelligence categories.
    """
    return AREA_INTELLIGENCE_CATEGORIES