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
from .report_generator import generate_markdown
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


def generate_all_maps(sites: list, outdir: str, top_n: int) -> tuple:
    """Generate all required maps and return their file paths."""
    # Use image directory from config
    map_png = create_report_asset_path("candidates_map.png", "image")
    heat_png = create_report_asset_path("demographics_heatmap.png", "image")

    # Generate candidates map
    extent = None

    extent = create_static_map_png(sites, map_png, top_n=top_n)
    logging.info("✅ Generated candidates map")

    # Generate demographic heatmap

    create_demographic_heatmap_png(sites, heat_png, extent=extent)
    logging.info("✅ Generated demographic heatmap")

    return map_png, heat_png


async def generate_report_assets_from_data(
    sites: dict,
    list_top_n_sites: list,
    req: Reqsmartreport,
    stats,
    best_site,
    output_dir,
    output_filename: str = DEFAULT_OUTPUT_FILENAME,
    top_n: int = 10,
) -> Dict:
    """
    Generate pharmacy site selection report from in-memory data.

    Args:
        scores_data: Dictionary containing scores data from generate_pharmacy_report function
        output_dir: Output directory path
        output_filename: Output markdown filename
        top_n: Number of top sites to analyze

    Returns:
        Dict Containing all the report data

    Raises:
        Exception: If report generation fails
    """

    # Calculate statistics for the sites
    logging.info("📊 Calculating statistics...")

    charts = generate_all_charts(list_top_n_sites)

    # Generate maps
    logging.info("🗺️  Generating maps...")
    map_png, heat_png = generate_all_maps(sites, output_dir, top_n)

    # Generate markdown report
    logging.info("📝 Generating enhanced markdown report...")
    report_data = generate_markdown(
        sites,
        output_dir,
        output_filename,
        top_n,
        charts,
        map_png,
        heat_png,
        req,
        list_top_n_sites,
        stats,
        best_site,
        list_top_n_sites,
        best_site
    )
    logging.info("✅ Report generation completed successfully")

    return report_data
