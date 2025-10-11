"""
Pharmacy Report Generator
Main generator for pharmacy HTML reports using modular components
"""

import logging
from typing import Dict, Any
from all_types.request_dtypes import Reqsmartreport
from pathlib import Path
from .css_styles import get_pharmacy_report_css
from .html_sections import (
    generate_executive_summary_section,
    generate_methodology_and_analysis_section,
    generate_visual_analysis_section,
)
from .data_validator import validate_inputs, DataValidationError

logger = logging.getLogger(__name__)


def generate_complete_html_report(
    req,
    processed_report_data
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
    format_type = validate_inputs(processed_report_data)
    logger.info(f"Generating HTML report for format type: {format_type}")

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
            {generate_executive_summary_section(req, processed_report_data)}
            {generate_methodology_and_analysis_section(processed_report_data)}
            {generate_visual_analysis_section(processed_report_data)}
        </div>
    </body>
    </html>"""

    logger.info("HTML report generation completed successfully")
    return html_content 