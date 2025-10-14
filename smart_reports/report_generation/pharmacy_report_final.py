#!/usr/bin/env python3
"""
pharmacy_report_final.py

Enhanced pharmacy site selection report generator with modular architecture.
Generates comprehensive 3-page markdown reports with:
- Enhanced visual design and styling
- Investment insights and market analysis
- Price and competition analysis
- Interactive charts and maps
- Arabic text support

Usage: python pharmacy_report_final.py [scores_path] [output_dir] [output_filename] [top_n]
"""
import os
import logging
from typing import Dict
from all_types.request_dtypes import Reqsmartreport

from utils.utils import create_report_asset_path
from .chart_generator import (
    plot_healthcare_vs_competition,
    plot_score_vs_price,
)
from .map_generator import create_static_map_png, create_demographic_heatmap_png
from .report_config import FONT_FAMILY, UNICODE_MINUS, DEFAULT_OUTPUT_FILENAME

# Set up matplotlib for Arabic text support
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = FONT_FAMILY
plt.rcParams["axes.unicode_minus"] = UNICODE_MINUS


def generate_all_charts(top_n_sites: list) -> dict:
    """Generate all required charts and return their file paths."""
    # Use image directory for static plot images

    charts = {
        "price_vs_score": create_report_asset_path(
            "price_vs_score.png", "image"
        ),
        "healthcare_competition": create_report_asset_path(
            "healthcare_competition.png", "image"
        ),
    }

    plot_score_vs_price(top_n_sites, outpath=charts["price_vs_score"])
    plot_healthcare_vs_competition(
        top_n_sites, outpath=charts["healthcare_competition"]
    )
    return charts


def generate_all_maps(sites: list, top_n: int) -> tuple:
    """Generate all required maps and return their file paths."""
    # Use image directory from config


    return map_png, heat_png
