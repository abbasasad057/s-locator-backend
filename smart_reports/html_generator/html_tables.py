"""
HTML Tables Module for Pharmacy Report Generation
Contains all table generation functions for pharmacy reports
"""

from typing import Dict, Any, List

def _get_display_text_with_icon(comparison_data: Dict[str, Any]) -> str:
    """Extract display text with appropriate styled indicator based on comparison type"""

    value = comparison_data.get("value", 0)
    comparison_type = comparison_data.get('comparison_type', '')
    percentage_difference = comparison_data.get("percentage_difference", 0)

    # Add appropriate styled indicator based on comparison type

    if comparison_type == 'improvement':
        return f'<span style="display: ruby;">{value}<span style="color: #22c55e; display: block; font-weight: 400;">(<span style="font-weight: 900;">↑</span> {percentage_difference})</span></span>'
    elif comparison_type == 'disadvantage':
        return f'<span style="display: ruby;">{value}<span style="color: #ef4444; display: block; font-weight: 400;">(<span style="font-weight: 900;">↓</span> {percentage_difference})</span></span>'
    elif comparison_type == 'difference':
        # For 'difference' (like 0% difference), just return the value
        return str(value)
    else:
        # For other types, just return the value
        return str(value)

def generate_rankings_table(rankings: List[Dict[str, Any]]) -> str:
    """Generate rankings table HTML"""
    table_rows = ""
    for i, property_data in enumerate(rankings, 1):
        # --- Logic and formatting block ---
        rank_class = "top3" if i <= 3 else ""
        site_name = property_data.get('site_name', 'Property')
        price_raw = property_data.get('price_sar', 0)
        price = price_raw
        price_display = str(int(price))

        final_score = _get_display_text_with_icon(property_data.get('final_score_comparison', {}))
        traffic_score = _get_display_text_with_icon(property_data.get('traffic_score_comparison', {}))
        demographics_score = _get_display_text_with_icon(property_data.get('demographics_score_comparison', {}))
        competition_score = _get_display_text_with_icon(property_data.get('competition_score_comparison', {}))
        healthcare_score = _get_display_text_with_icon(property_data.get('healthcare_ecosystem_score_comparison', {}))
        complementary_score = _get_display_text_with_icon(property_data.get('complementary_businesses_score_comparison', {}))

        google_maps_url = property_data.get('url', '#')
        if not google_maps_url or google_maps_url == '#':
            location = property_data.get('location', {})
            lat = location.get('latitude')
            lng = location.get('longitude')
            if lat and lng:
                google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

        # --- Display block ---
        table_rows += f"""
      <tr>
        <td><a href="{google_maps_url}" target="_blank" class="rank-badge {rank_class}">#{i}</a></td>
        <td><a href="{google_maps_url}" target="_blank">{site_name}</a></td>
        <td>{price_display}</td>
        <td><strong>{final_score}</strong></td>
        <td>{traffic_score}</td>
        <td>{demographics_score}</td>
        <td>{competition_score}</td>
        <td>{healthcare_score}</td>
        <td>{complementary_score}</td>
      </tr>"""
    return table_rows

def generate_current_location_table(processed_report_data: Dict[str, Any]) -> str:
    """Generate Current Location Scores table if current location data exists"""
    current_location = processed_report_data.get('current_location', [])

    if not current_location:
        return ""

    table_rows = ""
    for location_data in current_location:
        # --- Logic and formatting block ---
        site_name = location_data.get('site_name', 'Your current location')
        price_raw = location_data.get('price_sar', 0)
        price = price_raw
        price_display = str(int(price))
        rank = location_data.get('rank', 0)

        final_score = f"{round(location_data.get('final_score', 0), 1)}"
        traffic_score = f"{round(location_data.get('traffic_score', 0), 1)}"
        demographics_score = f"{round(location_data.get('demographics_score', 0), 1)}"
        competition_score = f"{round(location_data.get('competition_score', 0), 1)}"
        healthcare_score = f"{round(location_data.get('healthcare_ecosystem_score', 0), 1)}"
        complementary_score = f"{round(location_data.get('complementary_businesses_score', 0), 1)}"

        google_maps_url = location_data.get('url', '#')
        if not google_maps_url or google_maps_url == '#':
            location = location_data.get('location', {})
            lat = location.get('latitude')
            lng = location.get('longitude')
            if lat and lng:
                google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

        # --- Display block ---
        table_rows += f"""
      <tr>
        <td><a href="{google_maps_url}" target="_blank" class="rank-badge">#{rank}</a></td>
        <td><a href="{google_maps_url}" target="_blank">{site_name}</a></td>
        <td>{price_display}</td>
        <td><strong>{final_score}</strong></td>
        <td>{traffic_score}</td>
        <td>{demographics_score}</td>
        <td>{competition_score}</td>
        <td>{healthcare_score}</td>
        <td>{complementary_score}</td>
      </tr>"""

    return f"""
  <h2 class="section-title">📍 Current Location Scores</h2>

  <table class="rankings-table">
    <thead>
      <tr>
        <th>Rank</th>
        <th>Site Name</th>
        <th>Rent Price (SAR)</th>
        <th>Final Score</th>
        <th>Traffic</th>
        <th>Demographics</th>
        <th>Competition</th>
        <th>Healthcare Environment</th>
        <th>Complementary Businesses</th>
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>"""

def generate_custom_locations_table(processed_report_data: Dict[str, Any]) -> str:
    """Generate Custom Location Analysis table if custom locations data exists"""
    custom_locations = processed_report_data.get('custom_locations', [])

    if not custom_locations:
        return ""

    table_rows = ""
    for location_data in custom_locations:
        # --- Logic and formatting block ---
        site_name = location_data.get('site_name', 'Custom location')
        price_raw = location_data.get('price_sar', 0)
        price = price_raw
        price_display = str(int(price))
        rank = location_data.get('rank', 0)

        final_score = f"{round(location_data.get('final_score', 0), 1)}"
        traffic_score = f"{round(location_data.get('traffic_score', 0), 1)}"
        demographics_score = f"{round(location_data.get('demographics_score', 0), 1)}"
        competition_score = f"{round(location_data.get('competition_score', 0), 1)}"
        healthcare_score = f"{round(location_data.get('healthcare_ecosystem_score', 0), 1)}"
        complementary_score = f"{round(location_data.get('complementary_businesses_score', 0), 1)}"

        google_maps_url = location_data.get('url', '#')
        if not google_maps_url or google_maps_url == '#':
            location = location_data.get('location', {})
            lat = location.get('latitude')
            lng = location.get('longitude')
            if lat and lng:
                google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

        # --- Display block ---
        table_rows += f"""
      <tr>
        <td><span class="rank-badge">#{rank}</span></td>
        <td><code>{site_name}</code></td>
        <td>{price_display}</td>
        <td><strong>{final_score}</strong></td>
        <td>{traffic_score}</td>
        <td>{demographics_score}</td>
        <td>{competition_score}</td>
        <td>{healthcare_score}</td>
        <td>{complementary_score}</td>
      </tr>"""

    return f"""
  <h2 class="section-title">📍 Custom Location Analysis</h2>

  <table class="rankings-table">
    <thead>
      <tr>
        <th>Rank</th>
        <th>Site Name</th>
        <th>Rent Price (SAR)</th>
        <th>Final Score</th>
        <th>Traffic</th>
        <th>Demographics</th>
        <th>Competition</th>
        <th>Healthcare Environment</th>
        <th>Complementary Businesses</th>
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>"""
