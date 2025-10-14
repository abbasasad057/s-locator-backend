"""
HTML Charts and Visuals Module for Pharmacy Report Generation
Contains chart and visual component generation functions for pharmacy reports
"""

from typing import Dict, Any, List


def generate_chart_grid(processed_report_data = None) -> str:
    """Generate chart grid HTML"""
    # visual_analysis = processed_report_data.get("visual_analysis", {})
    # charts_data = visual_analysis.get("charts", [])
    # score_distribution_chart = "assets/image/score_distribution.png"
    analysis_dashboard_chart = "assets/image/analysis_dashboard.png"
    price_vs_score_chart = "assets/image/price_vs_score.png"
    generated_charts = []
    # for chart in charts_data:
    #     chart_url = chart["url"]
    #     generated_charts.append(chart_url)
    
    if not generated_charts:
        return f"""
      <div class="map-placeholder">
        <img src="{price_vs_score_chart}" alt="Price vs Score" style="width: 100%; height: auto; object-fit: cover;">
      </div>
      <div class="map-placeholder">
        <img src="{analysis_dashboard_chart}" alt="Analysis Dashboard" style="width: 100%; height: auto; object-fit: cover;">
      </div>"""
    
    # # Get chart titles from visual_analysis if available
    # chart_titles = {}
    # if visual_analysis:
    #     charts_data = visual_analysis['charts']
    #     for chart in charts_data:
    #         chart_url = chart['url']
    #         chart_title = chart['title']
    #         if chart_url and chart_title:
    #             # Extract filename from URL
    #             filename = chart_url.split('/')[-1]
    #             chart_titles[filename] = chart_title
    
    # chart_html = ""
    # for chart_path in generated_charts[:5]:
    #     # Extract filename from path
    #     filename = chart_path.split('/')[-1]
        
    #     # Use title from JSON if available, otherwise generate from filename
    #     if filename in chart_titles:
    #         chart_name = chart_titles[filename]
    #     else:
    #         chart_name = filename.replace('.png', '').replace('_', ' ').title()
        
    #     charts_path = f"assets/image/{filename}"
    #     chart_html += f"""
    #   <div class="map-placeholder">
    #     <img src="{charts_path}" alt="{chart_name}" style="width: 100%; height: auto; object-fit: cover;">
    #   </div>"""
    
    # return chart_html

def generate_investment_insights_list(processed_report_data: List[Dict[str, Any]]) -> str:
    """Generate investment insights list using only available JSON data"""

    insights_html = ""
    return insights_html
