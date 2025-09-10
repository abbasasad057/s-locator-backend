"""
Pharmacy Report Generator
Main generator for pharmacy HTML reports using modular components
"""

from typing import Dict, Any
from pathlib import Path
from .css_styles import get_pharmacy_report_css
from .html_sections import (
    generate_executive_summary_section,
    generate_methodology_and_analysis_section,
    generate_visual_analysis_section,
)

# Global variable for pharmacy report directory
PHARMACY_REPORT_BASE_DIR = Path("static/pharmacy_report")
PHARMACY_REPORT_BASE_DIR.mkdir(parents=True, exist_ok=True)


def write_html_file(file_path: Path, content: str) -> None:
    """Write HTML content to file"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_complete__html_report(
    req,
    processed_report_data
):
    """Generate the HTML report"""
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


def generate_report(req, processed_report_data) -> str:
    """Generate the complete pharmacy HTML report"""
    index_path = PHARMACY_REPORT_BASE_DIR / "index.html"

    html_content = generate_complete__html_report(
        req=req,
        processed_report_data=processed_report_data
    )

    write_html_file(index_path, html_content)

    return str(index_path.absolute())
