"""
Pharmacy Report Generator
Main generator for pharmacy HTML reports using modular components
"""

import logging
from typing import Dict, Any
from all_types.request_dtypes import Reqsmartreport
from pathlib import Path
from all_types.request_dtypes import Reqsmartreport
from .css_styles import get_pharmacy_report_css
from .html_sections import (
    generate_executive_summary_section,
    generate_methodology_and_analysis_section,
    generate_visual_analysis_section,
)

logger = logging.getLogger(__name__)


def generate_complete_html_report(
    req: Reqsmartreport,
    sites,
    stats,
    list_top_n_sites,
    best_site,
    custom_results,
    current_results,
    report_text
):
    """
    Generate the HTML report with data validation

    Args:
        req: Request object
        processed_report_data: The processed report data

    Returns:
        str: Complete HTML report

    Raises:
        DataValidationError: If data validation fails
    """
    # Validate data before processing
    # format_type= validate_response_data(req,
    # sites,
    # stats,
    # list_top_n_sites,
    # best_site,
    # custom_results,
    # current_results,)
    # logger.info(f"Generating HTML report for format type: {format_type}")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">

    <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Riyadh Pharmacy Site Analysis Report</title>
    <style>
        {get_pharmacy_report_css()}
    </style>
    </head>
    <body>
        <div class="report-container">
            {generate_executive_summary_section(req,
    sites,
    stats,
    list_top_n_sites,
    best_site,
    custom_results,
    current_results
    , report_text)}
            {generate_methodology_and_analysis_section(req,
    sites,
    stats,
    list_top_n_sites,
    best_site,
    custom_results,
    current_results,
    report_text
    )}
            {generate_visual_analysis_section(req,
    sites,
    stats,
    list_top_n_sites,
    best_site,
    custom_results,
    current_results,
    report_text)}
        </div>
    </body>
    </html>"""

    logger.info("HTML report generation completed successfully")
    return html_content
