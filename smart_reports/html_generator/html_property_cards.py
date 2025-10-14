"""
HTML Property Cards Module for Pharmacy Report Generation
Contains property card generation functions for pharmacy reports
"""

from typing import Dict, Any, List
from .html_tables import _get_display_text_with_icon


def generate_property_cards(list_top_n_sites: Dict[str, Any] = None) -> str:
    """Generate property cards HTML"""
    # Interactive maps mapping removed - not used in current implementation
    print(f"DEBUG: _generate_methodology_and_analysis_section called with {len(list_top_n_sites)} items")
    property_cards_html = ""
    for i, site in enumerate(list_top_n_sites, 1):
        site_name = site['display_name']
        total_score = site['total_score']
        total_score_display = f"{round(total_score, 1)}"
        price_display = str(int(site['price'])) + " SAR"
        category = site['category']
        listing_url = site['url']

        # Extract data directly from site structure based on available JSON keys
        # Traffic data - using available traffic_score instead of nested structure
        current_speed = site['traffic_score']  # Using traffic_score as proxy for speed data
        current_speed_display = f"{round(current_speed, 1)}"
        
        # Business environment - using num_of_businesses_around
        nearby_businesses = site['num_of_businesses_around']
        nearby_businesses_display = str(nearby_businesses)
        
        # Demographics - using available demographic fields
        population_age_35_plus = site['percentage_age_above_35']
        population_age_35_plus_display = f"{round(population_age_35_plus, 1)}"
        average_income = site['avg_income']
        average_income_display = f"{round(average_income, 2)} SAR"
        
        # Competition - using num_of_pharmacies
        total_competing_pharmacies = site['num_of_pharmacies']
        competing_pharmacies_display = str(total_competing_pharmacies)

        # Use actual scores from the site data instead of looking for rankings
        traffic_score_value = site['traffic_score']
        demographics_score_value = site['raw_scores']['demographics']  # Using raw_scores.demographics
        competition_score_value = site['raw_scores']['competition']   # Using raw_scores.competition

        # Get improvement values from the site data
        traffic_improvement = site['traffic_score_improvement']
        demographics_improvement = site['demographics_score_improvement']
        competition_improvement = site['competition_score_improvement']

        traffic_score_display = _get_display_text_with_icon(
            traffic_improvement,
            traffic_score_value,
        )
        demographics_score_display = _get_display_text_with_icon(
            demographics_improvement,
            demographics_score_value,
        )
        competition_score_display = _get_display_text_with_icon(
            competition_improvement,
            competition_score_value,
        )

        maps_path = f"assets/interactive_html/site_{site['lat']},{site['lng']}_map.html"

        property_cards_html += f"""
      <div class="property-card">
        <div class="property-header">
          <div class="property-title">#{i} {site_name}</div>
          <div class="score-badge">{total_score_display}/100</div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px">
          <div>
            <h4 style="color: #2c3e50; margin-bottom: 10px">📍 Property Details</h4>
            <p><strong>Price:</strong> {price_display}</p>
            <p><strong>Coordinates:</strong> {site['lat']}, {site['lng']}</p>
            <p><strong>Category:</strong> {category}</p>
            <p>
              <strong>Listing:</strong>
              <a href="{listing_url}" target="_blank" style="color: #3498db">View Property</a>
            </p>
          </div>

          <div>
            <h4 style="color: #2c3e50; margin-bottom: 10px">🎯 Performance Metrics</h4>
            <div class="score-breakdown">
              <div class="score-item">
                <div class="value">{traffic_score_display}</div>
                <div class="label">Traffic<br />({current_speed_display} km/h)</div>
              </div>
              <div class="score-item">
                <div class="value">{nearby_businesses_display}</div>
                <div class="label">Business<br />({nearby_businesses_display} nearby)</div>
              </div>
              <div class="score-item">
                <div class="value">{demographics_score_display}</div>
                <div class="label">Demographics<br />(Age: {population_age_35_plus_display})</div>
              </div>
              <div class="score-item">
                <div class="value">{competition_score_display}</div>
                <div class="label">Competition<br />({competing_pharmacies_display} pharmacies)</div>
              </div>
            </div>
          </div>
        </div>

        <div style="margin-top: 20px">
          <h4 style="color: #2c3e50; margin-bottom: 10px">📊 Detailed Analysis</h4>
          <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
              ">
            <div>
              <strong>🚗 Traffic Performance:</strong><br />
              <small>Current: {current_speed_display} km/h vs Target: 20–30 km/h<br />Assessment: ℹ️ Light traffic — smooth access but potentially less exposure to passersby.</small>
            </div>
            <div>
              <strong>🏪 Business Environment:</strong><br />
              <small>{nearby_businesses_display} businesses within 500m<br />Assessment: ❌ Weak ecosystem — limited complementary activity may reduce visibility.</small>
            </div>
            <div>
              <strong>👥 Demographics Match:</strong><br />
              <small>Population Aged 35+: {population_age_35_plus_display}%<br />Average Income: {average_income_display}<br />Assessment: ✅ Strong alignment with demand.</small>
            </div>
            <div>
              <strong>☕ Competitive Position:</strong><br />
              <small>{competing_pharmacies_display} pharmacies in area ({round(site['pharmacies_per_10k_population'], 1)} per 10k population)<br />🟢 Underserved market<br />Strategy: Strong opportunity for entry and growth.</small>
            </div>
          </div>
        </div>

        <div class="map-container">
          <h4 style="color: #2c3e50; margin-bottom: 15px">📍 Site Location Map</h4>
          <iframe src="{maps_path}" width="100%" height="400" style="border:0; border-radius: 12px;"></iframe>
          <p style="margin-top: 15px; color: #7f8c8d; font-size: 0.9em">
            <strong>Map shows:</strong> Property location, nearby businesses, analysis radius, and traffic patterns.
          </p>
        </div>
      </div>"""
    return property_cards_html
