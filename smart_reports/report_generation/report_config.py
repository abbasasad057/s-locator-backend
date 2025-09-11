import os

CHART_DPI = 200
CHART_FIGSIZE = (15, 8)
MAP_DPI = 150
MAP_FIGSIZE = (10, 7.5)
FONT_FAMILY = 'Arial'
UNICODE_MINUS = False
DEFAULT_OUTPUT_DIR = "static"
DEFAULT_OUTPUT_FILENAME = "report.md"

# Source type constants
source_current_location = "current"
source_custom_locations = "custom"
source_shop_for_rent = "shop_for_rent"

# Directory structure constants
DIR_REPORTS = "static/reports"
DIR_INTERACTIVE_HTML = "static/reports/assets/interactive_html"
DIR_IMAGE = "static/reports/assets/image"
DIR_TRAFFIC_SCREENSHOTS = "static/reports/assets/image/traffic_screenshots"


def setup_report_directories():
    """
    Create all necessary directories for report generation.
    """
    
    # Create all subdirectories
    os.makedirs(DIR_REPORTS, exist_ok=True)
    os.makedirs(DIR_INTERACTIVE_HTML, exist_ok=True)
    os.makedirs(DIR_IMAGE, exist_ok=True)
    os.makedirs(DIR_TRAFFIC_SCREENSHOTS, exist_ok=True)


def create_report_asset_path(file_name: str, asset_type: str) -> str:
    """
    Create the file path for a specific report asset.

    Args:
        asset_type (str): The type of asset (e.g., "image", "html")
        file_name (str): The name of the file

    Returns:
        str: The full path to the report asset
    """
    if asset_type == "image":
        return f"{DIR_IMAGE}/{file_name}"
    elif asset_type == "html":
        return f"{DIR_INTERACTIVE_HTML}/{file_name}"
    else:
        raise ValueError(f"Unknown asset type: {asset_type}")





