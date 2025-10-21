"""
HTML Tables Module for Pharmacy Report Generation
Contains all table generation functions for pharmacy reports
"""

from typing import Dict, Any, List


def _get_display_text_with_icon(improv_over_current, site_score) -> str:
    """
    Extract display text with appropriate styled indicator based on comparison type.
    Raises:
        ValueError if no valid comparison data is found.
    """
    # First, try to use comparison data if available
    if improv_over_current:
        if improv_over_current > 0:
            return f'<span style="display: ruby;">{site_score}<span style="color: #22c55e; display: block; font-weight: 400;">(<span style="font-weight: 900;">↑</span> {improv_over_current})</span></span>'
        elif improv_over_current < 0:
            return f'<span style="display: ruby;">{site_score}<span style="color: #ef4444; display: block; font-weight: 400;">(<span style="font-weight: 900;">↓</span> {improv_over_current})</span></span>'
        elif improv_over_current == 0:
            return f'<span style="display: ruby;">{site_score}<span style="color: #6b7280; display: block; font-weight: 400;">(<span style="font-weight: 900;">≈</span> {improv_over_current})</span></span>'
        else:
            # For other types or no comparison type, just return the value
            return str(site_score)

    # If no comparison data, use fallback value
    if site_score is not None:
        # Format numeric fallback values nicely
        if isinstance(site_score, (int, float)):
            return str(round(site_score, 1))
        return str(site_score)

    # If no valid comparison data, raise an error
    raise ValueError("No valid comparison data found")


def generate_rankings_table(list_top_n_sites: List[Dict[str, Any]]) -> str:
    """Generate rankings table HTML"""
    table_rows = ""
    for i, site in enumerate(list_top_n_sites, 1):
        # --- Logic and formatting block ---
        rank_class = "top3" if i <= 3 else ""

        # Extract data with proper field mapping - ONLY use data that exists in JSON
        display_name = site["display_name"]  # Use site_name from JSON
        price = site["price"]
        # Extract scores from comparison objects (if they exist) in JSON using display_text with icons
        # Provide fallback to direct score values if comparison data is missing
        total_score = _get_display_text_with_icon(
            site["percentage_difference"],
            site["total_score"],
        )
        traffic_score = _get_display_text_with_icon(
            site["traffic_score_improvement"],
            site["raw_scores"]["traffic"],
        )
        demographics_score = _get_display_text_with_icon(
            site["demographics_score_improvement"],
            site["raw_scores"]["demographics"],
        )
        competition_score = _get_display_text_with_icon(
            site["competition_score_improvement"],
            site["raw_scores"]["competition"],
        )
        complementary_score = _get_display_text_with_icon(
            site["complementary_ecosystem_score_improvement"],
            site["raw_scores"]["complementary"],
        )
        cross_shopping_score = _get_display_text_with_icon(
            site["cross_shopping_businesses_score_improvement"],
            site["raw_scores"]["cross_shopping"],
        )

        # Generate Google Maps URL if coordinates are available
        listing_url = site["url"]

        # Format price display
        price_display = (
            "N/A" if price == 0 and site["price"] is None else f"{price}"
        )

        table_rows += f"""
      <tr>
        <td><a href="{listing_url}" target="_blank" class="rank-badge {rank_class}">#{i}</a></td>
        <td><a href="{listing_url}" target="_blank">{display_name}</a></td>
        <td>{price_display}</td>
        <td><strong>{total_score}</strong></td>
        <td>{traffic_score}</td>
        <td>{demographics_score}</td>
        <td>{competition_score}</td>
        <td>{complementary_score}</td>
        <td>{cross_shopping_score}</td>
      </tr>"""
    return table_rows


def generate_current_location_table(site: Dict[str, Any]) -> str:
    """Generate Current Location Scores table if current location data exists"""

    table_rows = ""
    display_name = site["display_name"]
    price = site["price"]
    rank = 0

    # Handle None price values
    if price is None:
        price = 0

    # Use direct score values from JSON (no comparison objects for current/custom locations)
    total_score = f"{site['total_score']}"
    traffic_score = f"{site['raw_scores']['traffic']}"
    demographics_score = f"{site['raw_scores']['demographics']}"
    competition_score = f"{site['raw_scores']['competition']}"
    complementary_score = f"{site['raw_scores']['complementary']}"
    cross_shopping_score = f"{site['raw_scores']['cross_shopping']}"

    # Format price display
    price_display = site["price"]

    table_rows += f"""
  <tr>
    <td><a href="" target="_blank" class="rank-badge">#{rank}</a></td>
    <td><a href="" target="_blank">{display_name}</a></td>
    <td>{price_display}</td>
    <td><strong>{total_score}</strong></td>
    <td>{traffic_score}</td>
    <td>{demographics_score}</td>
    <td>{competition_score}</td>
    <td>{complementary_score}</td>
    <td>{cross_shopping_score}</td>
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
        <th>Complementary Environment</th>
        <th>Cross Shopping Businesses</th>
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>"""


def generate_custom_locations_table(custom_results: Dict[str, Any]) -> str:
    """Generate Custom Location Analysis table if custom locations data exists"""
    table_rows = ""
    for site in custom_results:
        display_name = site["display_name"]
        price = site["price"]

        # Use direct score values from JSON (no comparison objects for current/custom locations)
        total_score = f"{site['total_score']}"
        traffic_score = f"{site['raw_scores']['traffic']}"
        demographics_score = f"{site['raw_scores']['demographics']}"
        competition_score = f"{site['raw_scores']['competition']}"
        complementary_score = f"{site['raw_scores']['complementary']}"
        cross_shopping_score = f"{site['raw_scores']['cross_shopping']}"

        table_rows += f"""
      <tr>
        <td><span class="rank-badge">#</span></td>
        <td><code>{display_name}</code></td>
        <td>{price}</td>
        <td><strong>{total_score}</strong></td>
        <td>{traffic_score}</td>
        <td>{demographics_score}</td>
        <td>{competition_score}</td>
        <td>{complementary_score}</td>
        <td>{cross_shopping_score}</td>
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
        <th>Complementary Environment</th>
        <th>Cross Shopping Businesses</th>
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>"""
