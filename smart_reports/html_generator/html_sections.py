"""
HTML Sections Module for Pharmacy Report Generation
Contains main section generation functions for pharmacy reports
"""

from typing import Dict, Any, List
from datetime import datetime
# Import functional modules
from .html_tables import generate_rankings_table, generate_current_location_table, generate_custom_locations_table
from .html_property_cards import generate_property_cards
from .html_charts_visuals import generate_chart_grid, generate_investment_insights_list


def generate_executive_summary_section(req, processed_report_data: Dict[str, Any]) -> str:
    """Generate Executive Summary Section with rankings and top recommendations"""
    # Extract data
    city_name = req.city_name
    title = processed_report_data.get("title", f"{city_name} Pharmacy Site Analysis Report")
    description = processed_report_data.get("description", "Comprehensive Location Intelligence & Investment Recommendations")
    summary_metrics = processed_report_data.get("summary_metrics", {})
    executive_summary = processed_report_data.get("executive_summary", {})
    rankings = processed_report_data.get("rankings", [])
    key_investment_insights = processed_report_data.get("key_investment_insights", [])

    total_locations = summary_metrics.get("total_locations", 0)
    average_score = summary_metrics.get("average_score", 0)
    average_price_sar = summary_metrics.get("average_price_sar", 0)
    competing_pharmacies = summary_metrics.get("competing_pharmacies", 0)

    top_recommendation = executive_summary.get("top_recommendation", {})
    total_sites_evaluated = executive_summary.get("total_sites_evaluated", 0)

    # Extract data from key investment insights for top recommendation details
    traffic_advantage = next((insight for insight in key_investment_insights if insight.get('category') == 'Traffic Advantage'), {})
    business_ecosystem = next((insight for insight in key_investment_insights if insight.get('category') == 'Business Ecosystem'), {})
    demographic_alignment = next((insight for insight in key_investment_insights if insight.get('category') == 'Demographic Alignment'), {})
    market_dynamics = next((insight for insight in key_investment_insights if insight.get('category') == 'Market Dynamics'), {})

    # Extract score data for display
    traffic_score = traffic_advantage.get('traffic_score', 0)
    avg_speed = traffic_advantage.get('average_speed_kmh', 0)
    nearby_businesses = business_ecosystem.get('nearby_businesses_count', 0)
    demographics_score = demographic_alignment.get('demographics_score', 0)
    total_competitors = market_dynamics.get('total_competitors', 0)

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
          This comprehensive analysis evaluates {total_sites_evaluated} pharmacy locations across {city_name} using advanced location intelligence methodologies. Our assessment integrates multiple data sources including traffic flow analysis, demographic profiling, healthcare ecosystem mapping, competitive landscape evaluation, and complementary business assessment. Each location is systematically scored using our proprietary weighted methodology, considering market opportunity, accessibility, and business environment factors to provide data-driven investment recommendations.
        </p>
      </div>

      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-value">{total_locations}</div>
          <div class="metric-label">Total Properties Analyzed</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{average_score:.1f}</div>
          <div class="metric-label">Average Performance Score</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{average_price_sar:,.0f} SAR</div>
          <div class="metric-label">Average Price</div>
        </div>
        <div class="metric-card">
          <div class="metric-value">{competing_pharmacies}</div>
          <div class="metric-label">Competing Pharmacies</div>
        </div>
      </div>

      <div class="top-recommendation">
        <h2 style="margin-bottom: 20px; border: none; color: white">
          🏆 TOP RECOMMENDATION
        </h2>
        <h3 style="font-size: 1.8em; margin-bottom: 10px">Property #1: {top_recommendation.get('site_name', 'Top Property')}</h3>
        <div class="score-display">{top_recommendation.get('score', 0):.1f}/100</div>
        <p style="margin-bottom: 20px">
          <strong>Investment Price:</strong> {top_recommendation.get('price_sar', 0):,.0f} SAR
        </p>
        <div style="
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
              gap: 20px;
              margin-top: 20px;
            ">
          <div>
            <strong>🚗 Traffic Advantage:</strong><br />
            {traffic_score:.1f}/100 points<br />
            <small>Average Speed: {avg_speed:.1f} km/h | ℹ️ Optimal accessibility</small>
          </div>
          <div>
            <strong>🏪 Business Ecosystem:</strong><br />
            {nearby_businesses} nearby businesses<br />
            <small>✅ Strong commercial environment</small>
          </div>
          <div>
            <strong>👥 Demographics:</strong><br />
            {demographics_score:.1f}/100 points<br />
            <small>Strong market alignment</small>
          </div>
          <div>
            <strong>🏥 Competition:</strong><br />
            {total_competitors} competing pharmacies<br />
            <small>Emerging market opportunity</small>
          </div>
        </div>
      </div>

      {generate_current_location_table(processed_report_data)}
      {generate_custom_locations_table(processed_report_data)}

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
            <th>Healthcare Ecosystem</th>
            <th>Complementary Businesses</th>
          </tr>
        </thead>
        <tbody>
          {generate_rankings_table(rankings[:10])}
        </tbody>
      </table>
    </div>"""

def generate_methodology_and_analysis_section(processed_report_data: Dict[str, Any]) -> str:
    """Generate Methodology and Detailed Property Analysis Section"""
    # Generate property cards
    property_cards_html = generate_property_cards(processed_report_data)
    print(f"DEBUG: Property cards HTML length: {len(property_cards_html)}")
    print(f"DEBUG: First 500 chars of property cards: {property_cards_html[:500]}")

    return f"""
    <div class="page page-break">
      <h1 class="section-title">📈 Analysis Methodology</h1>

    <div class="methodology">
        <h3 style="color: #2c3e50; margin-bottom: 15px">
          📋 How This Analysis Was Conducted
        </h3>
          <p style="margin-bottom: 20px; font-size: 1.1em">
              This analysis streamlines the process of site selection for pharmacies and cafes by leveraging advanced data aggregation and scoring methodologies. Instead of relying solely on manual searches and local intuition, we utilize real estate listings, demographic data, traffic patterns, and proximity to key amenities to objectively evaluate each location. The result is a focused shortlist of optimal sites, tailored to your business objectives and target audience, enabling confident investment and expansion decisions.
          </p>
          <div style="background: #e8f4fd; padding: 16px; border-radius: 8px; margin-bottom: 18px; font-size: 1em;">
              <strong>Summary:</strong> Locations are assessed using five key criteria: traffic, demographics, competition, healthcare ecosystem, and complementary businesses. Each criterion is scored and weighted to reflect its impact on business success. Detailed explanations are available in the sections below.
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
                <li>Traffic flow is assessed for ease of access and parking, which is essential for both cafes and pharmacies.</li>
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
                <li>Pharmacies: avoid areas saturated with competitors; seek locations with unmet demand.</li>
                <li>Cafes: proximity to other food and beverage outlets can be a risk or benefit, depending on foot traffic and customer preferences.</li>
                <li>Analysis quantifies these factors, helping you avoid oversaturated markets and identify areas with opportunity.</li>
              </ul>
            </div>
          </details>
          <details class="collapsible-card">
            <summary>🏥 Healthcare Ecosystem (20%) – Evaluates proximity to healthcare providers</summary>
            <div class="card-content">
              <ul style="margin-bottom:12px;">
                <li><strong>Method:</strong> Scoring based on proximity to hospitals, clinics, and dentists (≤1500m preferred).</li>
                <li><strong>Scoring:</strong> Higher scores for closer and more accessible healthcare providers. Accessibility for people with disabilities is also considered.</li>
                <li><strong>Rationale:</strong> A strong healthcare ecosystem increases site attractiveness and convenience for residents and patients. For specialty businesses, proximity to hospitals can drive significant customer traffic.</li>
              </ul>
              <div style="margin-bottom:8px; color:#3498db; font-weight:600;">Business Logic</div>
              <ul>
                <li>Pharmacies and health-focused cafes benefit from proximity to hospitals, clinics, or rehabilitation centers.</li>
                <li>Increases customer flow from patients, healthcare workers, and visitors.</li>
                <li>Supports specialized offerings, such as accessibility for people with disabilities.</li>
                <li>Cafes near hospitals may attract visitors seeking a comfortable place to rest or recover.</li>
                <li>Analysis highlights these opportunities, ensuring your business serves both general and specialized needs.</li>
              </ul>
            </div>
          </details>
          <details class="collapsible-card">
            <summary>🏪 Complementary Businesses (10%) – Assesses access to amenities and brand positioning</summary>
            <div class="card-content">
              <ul style="margin-bottom:12px;">
                <li><strong>Method:</strong> Proximity-based scoring within 1000m to nearby businesses and amenities. High-end brands (e.g., Gucci, Prada) are favored for luxury businesses; everyday amenities (offices, schools, malls, hospitals) for general businesses.</li>
                <li><strong>Scoring:</strong> Higher scores for locations near a greater number and diversity of complementary businesses and amenities.</li>
                <li><strong>Rationale:</strong> Access to amenities and high-end brands supports sustained foot traffic, customer satisfaction, and brand positioning. This criterion is about the business ecosystem, not the population.</li>
              </ul>
              <div style="margin-bottom:8px; color:#3498db; font-weight:600;">Business Logic</div>
              <ul>
                <li>Complementary businesses enhance your site's attractiveness and customer base by creating synergies and increasing convenience for customers.</li>
                <li>Luxury cafes: proximity to high-end brands and malls increases prestige and draws the right clientele.</li>
                <li>Pharmacies and everyday cafes: being near offices, schools, malls, and hospitals ensures steady foot traffic and convenience for customers.</li>
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
            (Healthcare × 0.20) + (Complementary × 0.10)
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

def generate_visual_analysis_section(processed_report_data: Dict[str, Any]) -> str:
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
            <p>• Healthcare Corridors: Strong referral potential</p>
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
          {generate_chart_grid(processed_report_data)}
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
                for pharmacy establishment and expansion</small>
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
          {generate_investment_insights_list(processed_report_data)}
        </ul>
      </div>
      
      <div class="footer">
        Report generated using advanced geospatial analysis and machine
        learning algorithms
        <br />Analysis covered {processed_report_data.get('summary_metrics', {}).get('total_locations', 0)}
        candidate locations with comprehensive multi-criteria scoring
      </div>
    </div>"""
