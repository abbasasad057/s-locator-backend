"""
Pharmacy Report Generator
Main generator for pharmacy HTML reports using modular components
"""

from typing import Dict, Any
from all_types.request_dtypes import Reqsmartreport
from pathlib import Path
from .css_styles import get_pharmacy_report_css
from .html_sections import (
    generate_executive_summary_section,
    generate_methodology_and_analysis_section,
    generate_visual_analysis_section,
)



def generate_complete_html_report(
    req,
    processed_report_data
):
    """Generate the HTML report"""
    # prepare colors and logos
    # format data desired text
    # prepare charts and maps
    # insert formatted text and charts into html templates
    # combine all html parts into one complete html report


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
    return html_content
