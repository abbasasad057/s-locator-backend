

def convert_strings_to_ints(d):
    """
    Recursively converts all string values in a nested dictionary to integers
    where possible. Leaves other values unchanged.
    """
    if isinstance(d, dict):
        # Process each key-value pair in the dictionary
        return {k: convert_strings_to_ints(v) for k, v in d.items()}
    elif isinstance(d, list):
        # Process each item in a list (if the dictionary contains lists)
        return [convert_strings_to_ints(i) for i in d]
    elif isinstance(d, str):
        # Try converting the string to an integer
        try:
            return int(d)
        except ValueError:
            return d  # Leave as is if conversion fails
    else:
        # Return the value as is for non-dict, non-list, non-str types
        return d


DIR_IMAGE = "static/reports/assets/image"
DIR_INTERACTIVE_HTML = "static/reports/assets/interactive_html"


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


DIR_TRAFFIC_SCREENSHOTS = "static/reports/assets/image/traffic_screenshots"
# Directory structure constants
DIR_REPORTS = "static/reports"