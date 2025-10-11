"""
Data processing utilities for pharmacy site selection analysis.
"""

import json
import math
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import quote_plus
from all_types.request_dtypes import Reqsmartreport


def to_num(x: Any) -> float:
    """Convert value to float, handling N/A and empty values."""
    try:
        if isinstance(x, str) and x.strip().upper() in ("N/A", "NA", ""):
            return float("nan")
        return float(x)
    except Exception:
        return float("nan")



def calculate_statistics(sites: List[Dict]) -> Dict[str, float]:
    """Calculate aggregate statistics for all sites."""
    if not sites:
        return {
            "average_score": 0.0,
            "average_price": 0.0,
        }

    scores = []
    prices = []

    for key, value in sites.items():
        scores.append(value["total_score"])
        prices.append(value["price"])


    return {
        "average_score": sum(scores) / len(scores),
        "average_price": sum(prices) / len(prices)
    }


def google_maps_link(site: Dict) -> str:
    """Generate Google Maps link for a site."""
    if site.get("lat") is not None and site.get("lng") is not None:
        return f"https://www.google.com/maps/search/?api=1&query={site['lat']},{site['lng']}"
    q = site.get("raw_place") or site.get("display_name") or site["id"]
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(q)}"