"""
HTML Sections Module for Report Generation
Contains main section generation functions for reports
"""

from datetime import datetime

from all_types.request_dtypes import Reqsmartreport

from .html_charts_visuals import generate_chart_grid, generate_investment_insights_list
from .html_property_cards import generate_property_cards

# Import functional modules
from .html_tables import (
    generate_current_location_table,
    generate_custom_locations_table,
    generate_rankings_table,
)

HEADER_ICONS: dict[str, str] = {
    "pharmacy": "🏥",
    "cafe": "☕",
    "retail": "🛍️",
    "restaurant": "🍽️",
    "warehouse": "🏭",
}


def generate_executive_summary_section(
    req: Reqsmartreport,
    sites,
    stats,
    list_top_n_sites,
    best_site,
    custom_results,
    current_results,
    report_text,
) -> str:
    """Generate Executive Summary Section with rankings and top recommendations"""
    # Extract data
    city_name = req.city_name
    title = report_text["title"]
    description = report_text["description"]

    total_locations = len(sites)
    average_score = stats["average_score"]
    average_price = stats["average_price"]
    total_competing_target_business = stats[
        f"total_competing_{req.potential_business_type}"
    ]
    emoji: str = HEADER_ICONS.get(req.potential_business_type.strip().lower(), "🏢")

    return f"""
    <div class="page">
      <div class="hero">
        <h1>{title}</h1>
        <div class="muted">{description}</div>
        <div style="margin-top: 20px; font-size: 0.9em">
          Generated on {datetime.now().strftime('%B %d, %Y')}
        </div>
      </div>

      <div class="executive-summary">
        <h2 style="margin-bottom: 20px; border: none; color: white">
          📊 Executive Summary
        </h2>
        <p style="margin-bottom: 0">
          This comprehensive analysis evaluates {total_locations} {req.potential_business_type.capitalize()} locations across {city_name} using advanced location intelligence methodologies. Our assessment integrates multiple data sources including traffic flow analysis, demographic profiling, {req.ecosystem_string_name.capitalize()} ecosystem mapping, competitive landscape evaluation, and complementary business assessment. Each location is systematically scored using our proprietary weighted methodology, considering market opportunity, accessibility, and business environment factors to provide data-driven investment recommendations.
        </p>
      </div>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-value">{total_locations}</div>
          <div class="metric-label">Total Properties Analyzed</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{average_score}</div>
          <div class="metric-label">Average Performance Score</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{average_price} SAR</div>
          <div class="metric-label">Average Price</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{total_competing_target_business}</div>
          <div class="metric-label">Competing {req.potential_business_type.capitalize()}</div>
        </div>
      </div>

      <div class="top-recommendation">
        <h2 style="margin-bottom: 20px; border: none; color: white">
          🏆 TOP RECOMMENDATION
        </h2>
        <h3 style="font-size: 1.8em; margin-bottom: 10px">Property #1: {best_site['display_name']}</h3>
        <div class="score-display">{best_site['total_score']}/100</div>
        <p style="margin-bottom: 20px">
          <strong>Investment Price:</strong> {best_site['price']} SAR
        </p>
        <div style="
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
              gap: 20px;
              margin-top: 20px;
            ">
          <div style="padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;">
            <strong>🚗 Traffic Advantage:</strong>
            <span style="color: {best_site['traffic_color']}; font-weight: bold;">
              {best_site['traffic_icon']}
            </span><br />
            {best_site["raw_scores"]['traffic']}s<br />
            <small style="color: #ecf0f1;">{best_site["traffic_description"]}</small>
          </div>
          <div style="padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;">
            <strong>🏪 Business Ecosystem:</strong>
            <span style="color: {best_site['cross_shopping_color']}; font-weight: bold;">
              {best_site['cross_shopping_icon']}
            </span><br />
            {best_site["raw_scores"]["complementary"]}s<br />
            <small style="color: #ecf0f1;">{best_site["cross_shopping_description"]}</small>
          </div>
          <div style="padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;">
            <strong>👥 Demographics:</strong>
            <span style="color: {best_site['demographics_color']}; font-weight: bold;">
              {best_site['demographics_icon']}
            </span><br />
            {best_site["raw_scores"]["demographics"]}s<br />
            <small style="color: #ecf0f1;">{best_site["demographics_description"]}</small>
          </div>
          <div style="padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;">
            <strong>{emoji} Market Competition:</strong>
            <span style="color: {best_site['market_color']}; font-weight: bold;">
              {best_site['market_icon']}
            </span><br />
            {best_site["raw_scores"]["competition"]}s<br />
            <small style="color: #ecf0f1;">{best_site["market_description"]}</small>
          </div>
          <div style="padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px;">
            <strong>{emoji} {req.ecosystem_string_name.capitalize()} Environment:</strong>
            <span style="color: {best_site['complementary_color']}; font-weight: bold;">
              {best_site['complementary_icon']}
            </span><br />
            {best_site["raw_scores"]["complementary"]}s<br />
            <small style="color: #ecf0f1;">{best_site["complementary_description"]}</small>
          </div>
        </div>
      </div>

      {generate_current_location_table(current_results) if current_results else ""}
      {generate_custom_locations_table(custom_results) if custom_results else ""}

      <h2 class="section-title">📈 Top 10 Rankings</h2>

      <table class="rankings-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Site Name</th>
            <th>Price (SAR)</th>
            <th>Final Score</th>
            <th>Traffic</th>
            <th>Demographics</th>
            <th>Competition</th>
            <th>{req.ecosystem_string_name} Ecosystem</th>
            <th>Complementary Businesses</th>
          </tr>
        </thead>
        <tbody>
          {generate_rankings_table(list_top_n_sites)}
        </tbody>
      </table>
    </div>"""


def generate_methodology_and_analysis_section(
    req: Reqsmartreport,
    sites,
    stats,
    list_top_n_sites,
    best_site,
    custom_results,
    current_results,
    report_text,
) -> str:
    """Generate Methodology and Detailed Property Analysis Section"""
    # Generate property cards using available data
    property_cards_html = generate_property_cards(list_top_n_sites)
    print(f"DEBUG: Property cards HTML length: {len(property_cards_html)}")
    print(f"DEBUG: First 500 chars of property cards: {property_cards_html[:500]}")
    Complementary_locations = "(" + " & ".join(req.complementary_categories) + ")"
    emoji: str = HEADER_ICONS.get(req.potential_business_type.strip().lower(), "🏢")

    return f"""
    <div class="page page-break">
      <h1 class="section-title">📈 Analysis Methodology</h1>

    <div class="methodology">
        <h3 style="color: #2c3e50; margin-bottom: 15px">
          📋 How This Analysis Was Conducted
        </h3>
          <p style="margin-bottom: 20px; font-size: 1.1em">
              This analysis leverages advanced data aggregation and scoring methodologies. We utilize real estate listings, demographic data, traffic patterns, and proximity to key amenities to objectively evaluate each location. The result is a shortlist of optimal sites, tailored to your business objectives and target audience, enabling confident investment and expansion decisions.
          </p>
          <div style="background: #e8f4fd; padding: 16px; border-radius: 8px; margin-bottom: 18px; font-size: 1em;">
              <strong>Summary:</strong> Locations are assessed using five key criteria: traffic, demographics, competition, {req.ecosystem_string_name.capitalize()} ecosystem, and complementary businesses. Each criterion is scored and weighted to reflect its impact on business success. Detailed explanations are available in the sections below.
          </div>
          <details class="collapsible-card">
            <summary>🚦 Traffic Analysis (25%) – Evaluates accessibility and visibility</summary>
            <div class="card-content">
              <ul style="margin-bottom:12px;">
                <li><strong>Method:</strong> Real-time traffic flow analysis within a 500m radius, focusing on car traffic as the primary mode of transportation in Saudi Arabia.</li>
                <li><strong>Scoring:</strong> Locations with slower traffic (≤40 km/h) receive higher scores, as they offer better visibility and accessibility. Penalties are applied for higher speeds.</li>
                <li><strong>Rationale:</strong> Lower traffic speeds improve accessibility, parking, and the likelihood that passersby will notice the business. High car traffic in front of the store is essential for visibility and walk-in potential.</li>
              </ul>
              <div style="margin-bottom:8px; color:#3498db; font-weight:600;">Business Logic</div>
              <ul>
                <li>Entrepreneurs often start by driving around the city or browsing real estate websites for available spaces.</li>
                <li>Our analysis goes beyond availability, evaluating if the site is in a high-traffic area where cars slow down, increasing visibility for your signage.</li>
                <li>Traffic flow is assessed for ease of access and parking, which is essential for {req.potential_business_type}.</li>
                <li>Sites with little or fast-moving traffic are deprioritized, as they are less likely to attract walk-ins or impulse visits.</li>
              </ul>
            </div>
          </details>
          <details class="collapsible-card">
            <summary>👥 Demographics (30%) – Assesses market fit and target audience</summary>
            <div class="card-content">
              <ul style="margin-bottom:12px;">
                <li><strong>Method:</strong> Spatial analysis for age, income, and household characteristics using public and government data.</li>
                <li><strong>Scoring:</strong> Higher scores for locations matching the target age and income profile. Penalties for deviation from target demographics.</li>
                <li><strong>Rationale:</strong> Ensures market-product fit and maximizes business success. For luxury brands, high-income areas are prioritized; for student-focused businesses, proximity to residential zones with younger populations is emphasized.</li>
              </ul>
              <div style="margin-bottom:8px; color:#3498db; font-weight:600;">Business Logic</div>
              <ul>
                <li>Location selection is about the people who live, work, and travel nearby—not just the physical space.</li>
                <li>High income: prioritize areas with higher income levels and affluent residents.</li>
                <li>Target age: focus on residential zones with diverse age groups and stable populations.</li>
                <li>Student-focused businesses: target areas near universities and schools, but the demographic score is based on the actual population, not the presence of amenities.</li>
                <li>Aggregated demographic data from public sources and government websites provides insights often inaccessible to individual entrepreneurs.</li>
                <li>Avoids the pitfall of choosing a location based solely on intuition or incomplete information.</li>
              </ul>
            </div>
          </details>
          <details class="collapsible-card">
            <summary>🏪 Competition (15%) – Measures market saturation and opportunity</summary>
            <div class="card-content">
              <ul style="margin-bottom:12px;">
                <li><strong>Method:</strong> Competitive mapping within the analysis radius, identifying the number and proximity of similar businesses.</li>
                <li><strong>Scoring:</strong> Higher scores for locations with fewer competitors nearby; penalties for excess competitors.</li>
                <li><strong>Rationale:</strong> Balanced competition validates demand while avoiding oversaturation. Helps avoid locations with too many competitors and identifies emerging market opportunities.</li>
              </ul>
              <div style="margin-bottom:8px; color:#3498db; font-weight:600;">Business Logic</div>
              <ul>
                <li>Assess the competitive landscape after narrowing down your options.</li>
                <li>{req.potential_business_type.capitalize()}: avoid areas saturated with competitors; seek locations with unmet demand.</li>
                <li>Cafes: proximity to other food and beverage outlets can be a risk or benefit, depending on foot traffic and customer preferences.</li>
                <li>Analysis quantifies these factors, helping you avoid oversaturated markets and identify areas with opportunity.</li>
              </ul>
            </div>
          </details>
          <details class="collapsible-card">
            <summary>{emoji} {req.ecosystem_string_name.capitalize()} Ecosystem (20%) – Evaluates proximity to {req.ecosystem_string_name.capitalize()} providers</summary>
            <div class="card-content">
              <ul style="margin-bottom:12px;">
                <li><strong>Method:</strong> Scoring based on proximity to {Complementary_locations}(≤1500m preferred).</li>
                <li><strong>Scoring:</strong> Higher scores for closer and more accessible {req.ecosystem_string_name.capitalize()} providers. Accessibility for people with disabilities is also considered.</li>
                <li><strong>Rationale:</strong> A strong {req.ecosystem_string_name.capitalize()} ecosystem increases site attractiveness and convenience for residents and patients. For specialty businesses, proximity to {Complementary_locations} can drive significant customer traffic.</li>
              </ul>
              <div style="margin-bottom:8px; color:#3498db; font-weight:600;">Business Logic</div>
              <ul>
                <li>{req.potential_business_type.capitalize()} benefit from proximity to {Complementary_locations}.</li>
                <li>Increases customer flow from patients, {req.ecosystem_string_name.capitalize()} workers, and visitors.</li>
                <li>Supports specialized offerings, such as accessibility for people with disabilities.</li>
                <li>{req.potential_business_type.capitalize()} near {Complementary_locations} may attract visitors seeking a comfortable place to rest or recover.</li>
                <li>Analysis highlights these opportunities, ensuring your business serves both general and specialized needs.</li>
              </ul>
            </div>
          </details>
          <details class="collapsible-card">
            <summary>🏪 Complementary Businesses (10%) – Assesses access to amenities and brand positioning</summary>
            <div class="card-content">
              <ul style="margin-bottom:12px;">
                <li><strong>Method:</strong> Proximity-based scoring within 1000m to nearby businesses and amenities. High-end brands (e.g., Gucci, Prada) are favored for luxury businesses; everyday amenities (offices, schools, malls) for general businesses.</li>
                <li><strong>Scoring:</strong> Higher scores for locations near a greater number and diversity of complementary businesses and amenities.</li>
                <li><strong>Rationale:</strong> Access to amenities and high-end brands supports sustained foot traffic, customer satisfaction, and brand positioning. This criterion is about the business ecosystem, not the population.</li>
              </ul>
              <div style="margin-bottom:8px; color:#3498db; font-weight:600;">Business Logic</div>
              <ul>
                <li>Complementary businesses enhance your site's attractiveness and customer base by creating synergies and increasing convenience for customers.</li>
                <li>Luxury cafes: proximity to high-end brands and malls increases prestige and draws the right clientele.</li>
                <li>{req.potential_business_type.capitalize()} and everyday cafes: being near offices, schools, malls, and {Complementary_locations} ensures steady foot traffic and convenience for customers.</li>
                <li>This analysis identifies these synergies, helping you select locations that benefit from existing business ecosystems and maximize your visibility and customer base.</li>
                <li>Unlike demographics, this score is based on the presence and diversity of nearby businesses, not the characteristics of the population.</li>
              </ul>
            </div>
          </details>

        <div style="
              background: #e8f4fd;
              padding: 20px;
              border-radius: 10px;
              margin-top: 20px;
            ">
          <h4 style="color: #2c3e50; margin-bottom: 10px">🧮 Final Score Calculation</h4>
          <p>
            <strong>Formula:</strong> Final Score = (Traffic × 0.25) + (Demographics × 0.30) + (Competition × 0.15) +
            ({req.ecosystem_string_name.capitalize()} × 0.20) + (Complementary × 0.10)
          </p>
          <p>
            <strong>Range:</strong> 0–100 scale where 100 = optimal conditions across all criteria
          </p>
          <p>
            <strong>Interpretation:</strong> 🟢 ≥80 indicates an excellent potential, 🟡 60–79 indicates a good
            potential, 🔴 &lt; 60 requires careful consideration
          </p>
        </div>
      </div>
        
      <h1 class="section-title">🔍 Detailed Property Analysis</h1>

      <p style="font-size: 1.1em; color: #7f8c8d; margin-bottom: 30px">
        Comprehensive breakdown of top 10 performing properties with detailed
        scoring analysis and individual site maps.
      </p>

      {property_cards_html}
    </div>"""


def generate_visual_analysis_section(
    req,
    sites,
    stats,
    list_top_n_sites,
    best_site,
    custom_results,
    current_results,
    report_text,
) -> str:
    """Generate Visual Analysis Section with maps, charts, and investment insights"""
    candidates_map = "assets/image/candidates_map.png"
    return f"""
    <div class="page page-break">
      <h1 class="section-title">🗺️ Visual Analysis & Regional Overview</h1>

      <p style="font-size: 1.1em; color: #7f8c8d; margin-bottom: 30px">
        Interactive maps and statistical analysis providing comprehensive visual
        insights into market patterns and investment opportunities.
      </p>

      <div style="
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin: 30px 0;
          ">
        <h3 style="color: #2c3e50; margin-bottom: 20px">📊 Regional Overview</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
          <div class="performance-metrics">
            <h4>Market Performance</h4>
            <p>• Central Business District: High traffic, premium demographics</p>
            <p>• Residential Zones: Stable demand, moderate competition</p>
            <p>• {req.ecosystem_string_name.capitalize()} Corridors: Strong referral potential</p>
          </div>
          <div class="performance-metrics">
            <h4>Market Insights</h4>
            <p>• Score distribution shows clear performance tiers</p>
            <p>• Price-performance correlation analysis</p>
            <p>• Competition density mapping</p>
          </div>
        </div>
      </div>

      <div style="
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin: 30px 0;
          ">
        <h2 style="color: #2c3e50; margin-bottom: 20px">📈 Statistical Analysis</h2>
        <div style="display: flex; flex-direction:column; gap: 24px; margin: 20px 0;">
          {generate_chart_grid(stats)}
        </div>
      </div>

      <div class="property-card">
        <div class="property-header">
          <div class="property-title">
            🌍 Riyadh Commercial Properties Overview
          </div>
        </div>

        <div class="map-container">
          <img src="{candidates_map}" alt="Riyadh Properties Overview Map" class="map-image" />

          <p style="margin-top: 15px; color: #7f8c8d">
            <strong>Overview Map Features:</strong> Top 10 analyzed properties
            color-coded by performance score, demographic zones by area, and
            competitive distribution patterns. Green stars indicate top
            performers (80-100), orange shows good potential (60-79), and red
            highlights properties requiring careful consideration (&lt;60).
          </p>
        </div>

        <div style="margin-top: 20px">
          <h4 style="color: #2c3e50; margin-bottom: 10px">
            🎯 Regional Insights
          </h4>
          <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
              ">
            <div>
              <strong>🏆 Top Performing Areas:</strong><br />
              <small>Properties showing superior performance due to optimal
                business density and demographics clustering</small>
            </div>
            <div>
              <strong>📊 Market Distribution:</strong><br />
              <small>Geographic clustering analysis reveals optimal zones
                for {req.potential_business_type.capitalize()} establishment and expansion</small>
            </div>
            <div>
              <strong>🎯 Strategic Positioning:</strong><br />
              <small>Location optimization based on traffic patterns,
                demographic alignment, and competitive landscape</small>
            </div>
            <div>
              <strong>📈 Growth Opportunities:</strong><br />
              <small>Identified underserved areas with high growth
                potential and minimal competition</small>
            </div>
          </div>
        </div>
      </div>

      <div class="insights" style="margin-top: 30px;">
        <h3 style="margin-bottom: 15px;">💡 Key Investment Insights</h3>
        <ul style="margin-left: 20px; margin-top: 15px; line-height: 1.6;">
          {generate_investment_insights_list(best_site)}
        </ul>
      </div>
      
      <div class="footer">
        Report generated using advanced geospatial analysis and machine
        learning algorithms
        <br />Analysis covered {len(sites)}
        candidate locations with comprehensive multi-criteria scoring
      </div>
    </div>"""
