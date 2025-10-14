"""
Report generation utilities for pharmacy site selection analysis.
"""

import os
import math
from typing import List, Dict, Optional, Any
from all_types.request_dtypes import Reqsmartreport
from utils.utils import DIR_IMAGE, DIR_REPORTS
from .map_generator import generate_all_site_map_image
from typing import Dict, List, Any, Optional
from .report_config import source_current_location, source_custom_locations
from .report_object import (
    generate_detailed_insights_dict,
    generate_best_site_insights,
    generate_rankings_dict,
    generate_rankings_dict_with_current_comparison,
)

MAX_TOTAL = 100


def generate_detailed_insights(site: Dict) -> str:
    insights = []
    insights.append("## 📊 Detailed Analysis\n")

    # 🚗 Traffic Performance
    traffic_score = site.get("traffic_score")
    if traffic_score is not None:
        if 20 <= traffic_score <= 30:
            traffic_status = "✅ Optimal traffic — moderate traffic flow ensures both convenience and visibility."
        elif traffic_score < 20:
            traffic_status = "⚠️ Heavy congestion — low traffic may reduce accessibility but can increase local visibility."
        else:
            traffic_status = "ℹ️ Light traffic — smooth access but potentially less exposure to passersby."

        insights.append(
            f"### 🚗 Traffic Performance\n"
            f"Current: {traffic_score} km/h | Target: 20–30 km/h  \n"
            f"Assessment: {traffic_status}\n\n"
        )

    # 🏪 Business Environment
    nearby_businesses = site.get("num_of_businesses_around", 0)
    if nearby_businesses > 20:
        bus_status = "✅ Strong ecosystem —  complementary businesses support customer flow."
    elif nearby_businesses >= 10:
        bus_status = "⚠️ Moderate ecosystem — some opportunities exist, but growth potential remains."
    else:
        bus_status = "❌ Weak ecosystem — limited complementary activity may reduce visibility."

    insights.append(
        f"### 🏪 Business Environment\n"
        f"{nearby_businesses} businesses within 500m  \n"
        f"Assessment: {bus_status}\n\n"
    )

    # 👥 Demographics Match (Age above 35)
    age_above_35 = site.get("percentage_age_above_35")
    avg_income = site.get("avg_income")
    if age_above_35 is not None:
        if age_above_35 >= 40:
            age_status = "✅ Strong alignment — high share of population above 35, consistent with core demand segment."
        elif age_above_35 >= 25:
            age_status = "⚠️ Partial alignment — balanced age structure with moderate fit."
        else:
            age_status = "❌ Weak alignment — younger population may reduce pharmacy demand."

        insights.append(
            f"### 👥 Demographics Match\n"
            f"Population Aged 35 and Above: {age_above_35}% of local population with average \n"
            f"Assessment: {age_status}  \n"
            f"Average Income: {avg_income} SAR\n\n"
        )

    # ☕ Competitive Position
    pharm_per_10k = site.get("pharmacies_per_10k_population")
    if pharm_per_10k is not None:
        if pharm_per_10k > 8:
            market_status = "🔴 Saturated market\nStrategy: Differentiation is essential to compete effectively."
        elif pharm_per_10k >= 4:
            market_status = "🟠 Moderately competitive\nStrategy: Focus on service quality and location advantage."
        else:
            market_status = "🟢 Underserved market\nStrategy: Strong opportunity for entry and growth."

        insights.append(
            f"### ☕ Competitive Position\n"
            f"Pharmacies per 10k population: {pharm_per_10k}  \n"
            f"Competing Pharmacies in the area: {site['num_of_pharmacies']}  \n"
            f"{market_status}\n\n"
        )
    hospitals = site.get("num_of_hospitals", 0)
    dentists = site.get("num_of_dentists", 0)
    if hospitals + dentists > 10:
        health_status = "✅ Strong healthcare hub — high concentration of facilities ensures steady demand."
    elif hospitals + dentists >= 5:
        health_status = "⚠️ Moderate healthcare presence — demand is supported but with limited spillover."
    else:
        health_status = "❌ Weak healthcare presence — fewer facilities may reduce referral opportunities."

    insights.append(
        f"### 🏥 Healthcare Environment\n"
        f"Hospitals nearby: {hospitals}  \n"
        f"Dentists nearby: {dentists}  \n"
        f"Assessment: {health_status}\n\n"
    )

    return "".join(insights)


def generate_insights(sites: List[Dict], best_site: Dict) -> str:
    """Generate key investment insights based on analysis (Markdown only)."""
    if not sites:
        return "No data available for insights generation."
    insights = []

    # Prime opportunity - convert to 100 scale for display
    best_score_100 = best_site["total_score"]
    insights.append(
        f"- **Prime Opportunity:** {best_site['display_name']} emerges as the clear "
        f"market leader with exceptional potential scoring {best_score_100} points.\n"
    )

    total_competitors = len(best_site["nearby_pharmacy"])
    avg_competitors = total_competitors / len(sites) if sites else 0

    if avg_competitors > 5:
        market_status = (
            "Highly saturated market requires strong differentiation strategy"
        )
    elif avg_competitors > 2:
        market_status = "Moderately competitive market with room for growth"
    else:
        market_status = "Emerging market with minimal competition"

    insights.append(
        f"- **Market Dynamics:** {market_status} with {total_competitors} total competing pharmacies.\n"
    )

    # Traffic advantage - normalize to 100 scale
    best_traffic_weighted = best_site.get("weighted_scores", {}).get(
        "traffic", 0
    )
    best_traffic_100 = best_traffic_weighted
    traffic_info = ""
    traffic_score = best_site.get("traffic_score")
    traffic_info = f" with {traffic_score} km/h average speeds"

    insights.append(
        f"- **Traffic Advantage:** Accessibility scoring {best_traffic_100} points{traffic_info} "
        "supporting consistent customer flow.\n"
    )

    # Business ecosystem
    nearby_businesses = best_site.get("num_of_businesses_around", 0)

    insights.append(
        f"- **Business Ecosystem:** {nearby_businesses} nearby complementary businesses ensure "
        "consistent foot traffic and cross-selling opportunities.\n"
    )

    # Demographic alignment - normalize to 100 scale
    demo_weighted = best_site.get("weighted_scores", {}).get("demographics", 0)
    demo_100 = demo_weighted
    age_alignment = ""
    age_above_35 = best_site.get("percentage_age_above_35")
    if age_above_35 is not None and not math.isnan(age_above_35):
        deviation = abs(age_above_35 - 35)
        age_alignment = (
            f" with {deviation}% deviation from ideal customer profile"
        )

    insights.append(
        f"- **Demographic Alignment:** Scoring {demo_100} points{age_alignment}, "
        "indicating strong market fit.\n"
    )

    return "".join(insights)


def generate_enhanced_table(
    sites: List[Dict], CRITERION_WEIGHTS: Dict[str, float]
) -> str:
    """Generate enhanced Markdown table with requested columns - scores normalized to 100."""

    if not sites:
        return "_No sites available for table generation._\n"

    header = (
        "| Rank | Site Name |Rent Price (SAR) | Final Score | Traffic | Demographics | "
        "Competition | Healthcare Environment | Complementary Businesses | View |\n"
        "|:----:|:---------:|:-----------:|:-----------:|:-------:|:-----------:|"
        ":----------:|:-----------------:|:-------------------:|:---:|\n"
    )

    rows = []
    for i, site in enumerate(sites, start=1):
        price_display = (
            f"{site.get('price', 0):,}" if site.get("price") else "N/A"
        )

        # Convert all scores to 100 scale for display
        total_score_100 = site["total_score"]
        traffic_100 = site.get("weighted_scores", {}).get("traffic", 0)
        demographics_100 = site.get("weighted_scores", {}).get(
            "demographics", 0
        )
        competitive_100 = site.get("weighted_scores", {}).get("competition", 0)
        healthcare_100 = site.get("weighted_scores", {}).get("healthcare", 0)
        complementary_100 = site.get("weighted_scores", {}).get(
            "complementary", 0
        )

        rows.append(
            f"| {site['rank']} | {site['display_name']} | {price_display} | {total_score_100} | "
            f"{traffic_100} | {demographics_100} | {competitive_100} | "
            f"{healthcare_100} | {complementary_100} | "
            f"[View]({site['url']}) |\n"
        )
    return header + "".join(rows) + "\n"


def write_detailed_analysis(
    md,
    sites,
    CRITERION_WEIGHTS,
    maps_dir,
    md_path,
    section_title: str,
    category: str = "Shop For Rent",
) -> List[Dict[str, Any]]:
    """Write detailed site analysis for a given set of sites and return structured data."""

    if not sites:
        return []

    md.write(f"## {section_title}\n\n")

    detailed_analysis = []
    for i, s in enumerate(sites, start=1):
        total_score_100 = s["total_score"]
        md.write(
            f"### {i}. {s['display_name']} (Score: {total_score_100})\n\n"
        )

        coords_text = (
            f"**Location:** {s['lat']}, {s['lng']}"
            if (s["lat"] is not None and s["lng"] is not None)
            else f"**Location:** {s.get('raw_place') or 'N/A'}"
        )
        price_text = (
            f"**Rent Price:** {s.get('price', 0):,} SAR"
            if s.get("price")
            else "**Rent Price:** Not specified"
        )

        md.write(f"{coords_text} | {price_text} | Category: {category} \n\n")
        analysis_space = (
            "Analysis Preformed for locations with 2km from all sides"
        )
        md.write(f"{analysis_space}\n\n")
        # Generate insights
        md.write(generate_detailed_insights(s))
        md.write(f"**[🗺️ View location]({s['url']})**\n\n")

        # Maps
        map_image, html_map = generate_all_site_map_image(s)
        # Make paths relative to markdown directory
        map_image_rel = (
            os.path.relpath(map_image, os.path.dirname(md_path)).replace(
                "\\", "/"
            )
            if map_image
            else None
        )
        html_map_rel = (
            os.path.relpath(html_map, os.path.dirname(md_path)).replace(
                "\\", "/"
            )
            if html_map
            else None
        )
        if map_image_rel:
            md.write(f"![Site Map]({map_image_rel})\n\n")
        if html_map_rel:
            md.write(f"[Open interactive map]({html_map_rel})\n\n")

        # Scoring breakdown
        md.write("| Criterion | Key Metrics | Raw Score | Weighted Points |\n")
        md.write("|-----------|-------------|-----------|----------------|\n")

        scoring_breakdown = []

        # Traffic scoring
        if "traffic" in CRITERION_WEIGHTS:
            traffic_raw = s.get("traffic_score", 0.0)
            weighted_points = s.get("weighted_scores", {}).get("traffic", 0.0)
            md.write(
                f"| Traffic | Average Speed | {traffic_raw} km/h | {weighted_points} |\n"
            )
            scoring_breakdown.append(
                {
                    "criterion": "Traffic",
                    "sub_factor": "Average Speed",
                    "raw_score": traffic_raw,
                    "weighted_points": weighted_points,
                }
            )

        # Demographics scoring
        if "demographics" in CRITERION_WEIGHTS:
            age_raw = s.get("percentage_age_above_35", 0.0)
            weighted_points = s.get("weighted_scores", {}).get(
                "demographics", 0.0
            )
            md.write(
                f"| Demographics | Age 35+ (%) | {age_raw}% | {weighted_points} |\n"
            )
            scoring_breakdown.append(
                {
                    "criterion": "Demographics",
                    "sub_factor": "Age 35+ (%)",
                    "raw_score": age_raw,
                    "weighted_points": weighted_points,
                }
            )

        # Competition scoring
        if "competition" in CRITERION_WEIGHTS:
            comp_raw = s.get("num_of_pharmacies", 0)
            weighted_points = s.get("weighted_scores", {}).get(
                "competition", 0.0
            )
            md.write(
                f"| Competition | Nearby Pharmacies | {comp_raw} | {weighted_points} |\n"
            )
            scoring_breakdown.append(
                {
                    "criterion": "Competition",
                    "sub_factor": "Nearby Pharmacies",
                    "raw_score": comp_raw,
                    "weighted_points": weighted_points,
                }
            )

        # Healthcare scoring
        if "healthcare" in CRITERION_WEIGHTS:
            health_raw = s.get("num_of_hospitals", 0) + s.get(
                "num_of_dentists", 0
            )
            weighted_points = s.get("weighted_scores", {}).get(
                "healthcare", 0.0
            )
            md.write(
                f"| Healthcare | Hospitals + Dentists | {health_raw} | {weighted_points} |\n"
            )
            scoring_breakdown.append(
                {
                    "criterion": "Healthcare",
                    "sub_factor": "Hospitals + Dentists",
                    "raw_score": health_raw,
                    "weighted_points": weighted_points,
                }
            )

        # Complementary businesses scoring
        if "complementary" in CRITERION_WEIGHTS:
            comp_raw = s.get("num_of_businesses_around", 0)
            weighted_points = s.get("weighted_scores", {}).get(
                "complementary", 0.0
            )
            md.write(
                f"| Complementary | Nearby Businesses | {comp_raw} | {weighted_points} |\n"
            )
            scoring_breakdown.append(
                {
                    "criterion": "Complementary",
                    "sub_factor": "Nearby Businesses",
                    "raw_score": comp_raw,
                    "weighted_points": weighted_points,
                }
            )
        md.write("\n")

        detailed_analysis.append(
            {
                "rank": i,
                "display_name": s["display_name"],
                "total_score": round(total_score_100, 1),
                "analysis_space": analysis_space,
                "location": {
                    "latitude": s["lat"] if s["lat"] is not None else None,
                    "longitude": s["lng"] if s["lng"] is not None else None,
                    "raw_place": s.get("raw_place"),
                },
                "price": s.get("price", 0) if s.get("price") else None,
                "category": category,
                "url": s.get("url"),
                "maps": {
                    "static_map_url": map_image_rel,
                    "interactive_map_url": html_map_rel,
                },
                "detailed_insights": generate_detailed_insights_dict(s),
                "scoring_breakdown": scoring_breakdown,
            }
        )

    return detailed_analysis


def generate_markdown(
    sites: List[Dict],
    outdir: str,
    out_md: str,
    top_n: int,
    charts: Dict[str, str],
    map_png: Optional[str],
    heat_png: Optional[str],
    req: Reqsmartreport,
    sites_sorted,
    stats: Dict[str, Any],
    best_site: Dict[str, Any],
    list_top_n_sites: List[Dict[str, Any]],
    custom_results,
    current_results,
) -> Dict[str, Any]:
    """Generate comprehensive markdown report with enhanced design and features AND return structured dictionary And the path of the report.md."""
    report_data = {}
    # insights_md = generate_insights(sites, best_site)
    

    if current_location:
        # table_md = generate_table_with_current_comparison(
        #                 top_sites, current_location, CRITERION_WEIGHTS
        #             )
        # report_data["current_location"] = generate_rankings_dict(
        #     current_location, CRITERION_WEIGHTS
        # )
        # report_data["rankings"] = (
        #     generate_rankings_dict_with_current_comparison(
        #         top_sites, current_location, CRITERION_WEIGHTS
        #     )
        # )

        # detailed_analysis, current_detailed_analysis = (
        #     write_detailed_analysis_with_current(
        #         md,
        #         top_sites,
        #         current_location,
        #         CRITERION_WEIGHTS,
        #         maps_dir,
        #         md_path,
        #         "🔍 Detailed Site Analysis vs Current Location",
        #     )
        # )
        # else:
        # table_md = generate_enhanced_table(
        #     top_sites,CRITERION_WEIGHTS
        # )
        # report_data["rankings"] = generate_rankings_dict(
        #     top_sites, CRITERION_WEIGHTS
        # )
        report_data["detailed_analysis"] = write_detailed_analysis(
            md,
            top_sites,
            CRITERION_WEIGHTS,
            maps_dir,
            md_path,
            "🔍 Detailed Site Analysis",
        )

    if custom_locations:
        table_md = generate_enhanced_table(custom_locations, CRITERION_WEIGHTS)
        report_data["custom_locations"] = generate_rankings_dict(
            custom_locations, CRITERION_WEIGHTS
        )
        report_data["custom_detailed_analysis"] = write_detailed_analysis(
            md,
            custom_locations,
            CRITERION_WEIGHTS,
            maps_dir,
            md_path,
            "🔍 Detailed Custom Locations",
        )

    num_of_sites = len(sites)

    # 3️⃣ Separate by source
    custom_locations = [
        site
        for site in sites_sorted
        if site.get("source") == source_custom_locations
    ]
    current_location = [
        site
        for site in sites_sorted
        if site.get("source") == source_current_location
    ]

    # Save markdown file in markdown directory (directories assumed to be already created)
    md_path = os.path.join(DIR_REPORTS, out_md).replace("\\", "/")

    # Configure maps directory using config constant
    maps_dir = os.path.join(outdir, DIR_IMAGE)

    with open(md_path, "w", encoding="utf-8") as md:

        # Hero section

        md.write(f"# {report_data['title']}\n\n")

        md.write(f"{report_data['description']}\n\n")

        # Summary metrics
        summary_metrics_title = "📊 Summary Metrics"
        md.write(f"## {summary_metrics_title}\n\n")

        md.write(f"- **{"Total Locations"}:** {num_of_sites}\n")

        avg_score_100 = stats["average_score"]
        md.write(f"- **Average Score:** {avg_score_100}\n")
        md.write(
            f"- **Average Rent Price:** {stats['average_price']} SAR\n"
        )
        md.write(
            f"- **Competing Pharmacies:** {stats['total_competing_pharmacies']}\n\n"
        )

        # Executive Summary
        exec_summary_title = "Executive Summary"
        md.write(f"## 📋 {exec_summary_title}\n\n")

        price = best_site.get("price")
        price_str = f"{price:,}" if price is not None else "N/A"
        top_rec_text = (
            f"**Top recommendation:** **{best_site['display_name']}** with an overall score of "
            f"{best_site["total_score"]} points, rent priced at {price_str} SAR.\n\n"
        )
        md.write(top_rec_text)

        md.write(description_text)
        # Key Investment Insights
        insights_title = "💡 Key Investment Insights"
        md.write(f"## {insights_title}\n\n")

        md.write(insights_md)
        md.write("\n")

        # Enhanced Top Sites Table
        rankings_title = f"🏆 Top {top_n} Investment Opportunities"

        if current_location:

            # Use the new function and pass top_sites as baseline
            md.write("## Current Location Scores \n\n")

            md.write(table_current_md)
            md.write("\n\n\n")
            md.write(
                f"### 🏠 {rankings_title} compared  with Current Location Evaluation\n\n"
            )
            md.write("\n\n\n")

            md.write(table_md)

            md.write("\n\n")
            md.write("\n\n")
        else:
            md.write(f"## {rankings_title}\n\n")

            md.write(table_md)
            md.write("\n\n")
            md.write("\n\n")

        if custom_locations:
            md.write("### 📍 Custom Location Analysis\n\n")

            md.write(table_md)
            md.write("\n\n")
            md.write("\n\n")

        # Detailed Site Analysis
        # Function call usage:
        if current_location:

            report_data["detailed_analysis"] = detailed_analysis
            report_data["current_detailed_analysis"] = current_detailed_analysis
        else:
            pass

        # Detailed Site Analysis for top N
        # report_data["detailed_analysis"] = write_detailed_analysis(
        #     md, top_sites, MAX_TOTAL, CRITERION_WEIGHTS, maps_dir, md_path, "🔍 Detailed Site Analysis"
        # )

        if custom_locations:
            pass

        # if current_location:
        #     report_data["current_detailed_analysis"] = write_detailed_analysis(
        #         md, current_location, MAX_TOTAL, CRITERION_WEIGHTS, maps_dir, md_path, "🔍 Detailed Current Locations"
        #     )

        # Charts & Visualizations
        charts_title = "📊 Charts & Visualizations"
        md.write(f"## {charts_title}\n\n")

        visual_analysis = {"charts": [], "maps": [], "interactive_maps": []}

        if charts.get("top_stacked") and os.path.exists(charts["top_stacked"]):
            # rel = relpath_for_md(charts['top_stacked'], md_path)
            path = charts.get("top_stacked")
            if path:
                # Make path relative to markdown directory
                chart_path = os.path.relpath(
                    path, os.path.dirname(md_path)
                ).replace("\\", "/")
                md.write(
                    f"**Comparative Analysis:**\n\n![Top Candidates Comparison]({chart_path})\n\n\n"
                )
                md.write(f"**Path : {chart_path}\n\n")
                visual_analysis["charts"].append(
                    {
                        "title": "Top Candidates Comparison",
                        "type": "comparative_analysis",
                        "url": chart_path,
                    }
                )

        if charts.get("traffic") and os.path.exists(charts["traffic"]):
            path = charts.get("traffic")
            if path:
                # Make path relative to markdown directory
                chart_path = os.path.relpath(
                    path, os.path.dirname(md_path)
                ).replace("\\", "/")
                md.write(
                    f"**Traffic Analysis:**\n\n![Traffic Flow Analysis]({chart_path})\n\n\n"
                )
                md.write(f"**Path : {chart_path}\n\n")
                visual_analysis["charts"].append(
                    {
                        "title": "Traffic Flow Analysis",
                        "type": "traffic_analysis",
                        "url": chart_path,
                    }
                )

        if charts.get("best_breakdown") and os.path.exists(
            charts["best_breakdown"]
        ):
            path = charts.get("best_breakdown")
            if path:
                # Make path relative to markdown directory
                chart_path = os.path.relpath(
                    path, os.path.dirname(md_path)
                ).replace("\\", "/")
                md.write(
                    f"**Best Site Breakdown:**\n\n![Best Site Breakdown]({chart_path})\n\n\n"
                )
                md.write(f"**Path : {chart_path}\n\n")
                visual_analysis["charts"].append(
                    {
                        "title": "Best Site Breakdown",
                        "type": "site_breakdown",
                        "url": chart_path,
                    }
                )
        if charts.get("price_vs_score") and os.path.exists(
            charts["price_vs_score"]
        ):
            path = charts.get("price_vs_score")
            if path:
                # Make path relative to markdown directory
                chart_path = os.path.relpath(
                    path, os.path.dirname(md_path)
                ).replace("\\", "/")
                md.write(
                    f"**Price VS Final Score :**\n\n![Price VS Score]({chart_path})\n\n\n"
                )
                md.write(f"**Path : {chart_path}\n\n")
                visual_analysis["charts"].append(
                    {
                        "title": "Best Site Breakdown",
                        "type": "site_breakdown",
                        "url": chart_path,
                    }
                )
        if charts.get("healthcare_competition") and os.path.exists(
            charts["healthcare_competition"]
        ):
            path = charts.get("healthcare_competition")
            if path:
                # Make path relative to markdown directory
                chart_path = os.path.relpath(
                    path, os.path.dirname(md_path)
                ).replace("\\", "/")
                md.write(
                    f"**Healthcare vs pharmacies competition :**\n\n![healthcare_competition]({chart_path})\n\n\n"
                )
                md.write(f"**Path : {chart_path}\n\n")
                visual_analysis["charts"].append(
                    {
                        "title": "Healthcare vs Pharmacy Competition",
                        "type": "healthcare_competition",
                        "url": chart_path,
                    }
                )
        # Maps
        maps_title = "🗺️ Geographic Analysis"
        md.write(f"## {maps_title}\n\n")

        if map_png:
            # Make path relative to markdown directory
            map_path = os.path.relpath(
                map_png, os.path.dirname(md_path)
            ).replace("\\", "/")
            md.write("**Location Overview:**\n\n")
            md.write(f"![Candidates Map]({map_path})\n\n\n")
            md.write(f"**Path : {map_path}\n\n")
            visual_analysis["maps"].append(
                {
                    "title": "Location Overview",
                    "type": "candidates_map",
                    "url": map_path,
                }
            )
        else:
            md.write("**Location Overview:** *Map not available*\n\n")

        if heat_png:
            # Make path relative to markdown directory
            heat_path = os.path.relpath(
                heat_png, os.path.dirname(md_path)
            ).replace("\\", "/")
            md.write("**Demographic Distribution:**\n\n")
            md.write(f"![Demographic Heatmap]({heat_path})\n\n\n")
            md.write(f"**Path : {heat_path}\n\n")
            visual_analysis["maps"].append(
                {
                    "title": "Demographic Distribution",
                    "type": "demographic_heatmap",
                    "url": heat_path,
                }
            )
        else:
            md.write(
                "**Demographic Distribution:** *Heatmap not available*\n\n"
            )

        # Collect interactive maps from detailed analysis
        for site_data in report_data["detailed_analysis"]:
            if site_data["maps"]["interactive_map_url"]:
                visual_analysis["interactive_maps"].append(
                    {
                        "display_name": site_data["display_name"],
                        "url": site_data["maps"]["interactive_map_url"],
                    }
                )

        report_data["visual_analysis"] = visual_analysis

        # Methodology
        methodology_title = "📈 Analysis Methodology"
        md.write(f"## {methodology_title}\n\n")

        md.write(
            "Our site suitability analysis employs a **comprehensive, data-driven approach**. "
            "The methodology integrates multiple data sources and applies weighted scoring "
            "to identify optimal locations.\n\n"
        )

        methodology = {
            "overview": "Comprehensive, data-driven approach that integrates multiple data sources and applies weighted scoring to identify optimal locations.",
            "criteria": {},
        }

        # Traffic Analysis (25%)
        md.write("### 🚦 Traffic Analysis (25%)\n")
        traffic_method = (
            "**Data Source:** Traffic API data TOMTOM  \n"
            "**Method:** Real-time traffic flow analysis within 500m radius  \n"
            "**Scoring:** Perfect score (100) for speeds ≤40 km/h; penalty of 5 points per 40 km/h above target  \n"
            "**Rationale:** Lower traffic speeds indicate better accessibility and parking availability.\n\n"
        )
        md.write(traffic_method)

        methodology["criteria"]["traffic"] = {
            "weight_percentage": 25,
            "data_source": "Traffic API data TOMTOM",
            "method": "Real-time traffic flow analysis within 500m radius",
            "scoring": "Perfect score (100) for speeds ≤40 km/h; penalty of 5 points per 40 km/h above target",
            "rationale": "Lower traffic speeds indicate better accessibility and parking availability.",
        }

        # Demographics (30%)
        md.write("### 👥 Demographics (30%)\n")
        demo_method = (
            "**Data Source:** Demographic GeoJSON overlay  \n"
            "**Method:** Spatial join analysis for age and income matching  \n"
            "**Scoring:** Perfect score at target age Above 35; penalty of 5 points per year deviation  \n"
            "**Rationale:** Target demographic alignment ensures market-product fit.\n\n"
        )
        md.write(demo_method)

        methodology["criteria"]["demographics"] = {
            "weight_percentage": 30,
            "data_source": "Demographic GeoJSON overlay",
            "method": "Spatial join analysis for age and income matching",
            "scoring": "Perfect score at target age Above 35; penalty of 5 points per year deviation",
            "rationale": "Target demographic alignment ensures market-product fit.",
        }

        # Competition (15%)
        md.write("### 🏪 Competition (15%)\n")
        comp_method = (
            "**Data Source:** POI analysis of Pharmacies shops  \n"
            "**Method:** Competitive mapping within analysis radius  \n"
            "**Scoring:** Perfect score for nearest phramacy is above 500m in living area; penalty of 10 points per excess competitor  \n"
            "**Rationale:** Balanced competition validates demand while avoiding oversaturation.\n\n"
        )
        md.write(comp_method)

        methodology["criteria"]["competition"] = {
            "weight_percentage": 15,
            "data_source": "POI analysis of Pharmacies shops",
            "method": "Competitive mapping within analysis radius",
            "scoring": "Perfect score for nearest pharmacy is above 500m in living area; penalty of 10 points per excess competitor",
            "rationale": "Balanced competition validates demand while avoiding oversaturation.",
        }

        # Healthcare Ecosystem (20%)
        md.write("### 🏥 Healthcare Environment (20%)\n")
        health_method = (
            "**Data Source:** POI analysis of hospitals and dental clinics  \n"
            "**Method:** Scoring based on proximity to nearby hospitals and dentists (≤1500m preferred)  \n"
            "**Scoring:** Average of proximity scores; closer and more accessible healthcare improves score  \n"
            "**Rationale:** A strong healthcare environment increases site attractiveness and convenience for residents.\n\n"
        )
        md.write(health_method)

        methodology["criteria"]["healthcare"] = {
            "weight_percentage": 20,
            "data_source": "POI analysis of hospitals and dental clinics",
            "method": "Scoring based on proximity to nearby hospitals and dentists (≤1500m preferred)",
            "scoring": "Average of proximity scores; closer and more accessible healthcare improves score",
            "rationale": "A strong healthcare environment increases site attractiveness and convenience for residents.",
        }

        # Complementary Businesses (10%)
        md.write("### 🏪 Complementary Businesses (10%)\n")
        comp_bus_method = (
            "**Data Source:** POI analysis of grocery stores, supermarkets, restaurants, ATMs, and banks  \n"
            "**Method:** Proximity-based scoring within 1000m; closer businesses improve accessibility  \n"
            "**Scoring:** Average score across all complementary business types  \n"
            "**Rationale:** Access to everyday amenities supports sustained foot traffic and customer satisfaction.\n\n"
        )
        md.write(comp_bus_method)

        methodology["criteria"]["complementary"] = {
            "weight_percentage": 10,
            "data_source": "POI analysis of grocery stores, supermarkets, restaurants, ATMs, and banks",
            "method": "Proximity-based scoring within 1000m; closer businesses improve accessibility",
            "scoring": "Average score across all complementary business types",
            "rationale": "Access to everyday amenities supports sustained foot traffic and customer satisfaction.",
        }

        # Final Score Calculation
        md.write("### 🧮 Final Score Calculation\n")
        formula_text = (
            "**Formula:**  \n"
            "`Final Score = (Traffic × 0.25) + (Demographics × 0.30) + (Competition × 0.15) + "
            "(Healthcare × 0.20) + (Complementary × 0.10)`  \n\n"
            "**Range:** 0–100 scale where 100 = optimal conditions across all criteria  \n\n"
            "**Interpretation:**  \n"
            "- 🟢 ≥80 → Excellent potential  \n"
            "- 🟡 60–79 → Good potential  \n"
            "- 🔴 <60 → Requires careful consideration\n\n"
        )
        md.write(formula_text)

        methodology["final_calculation"] = {
            "formula": "Final Score = (Traffic × 0.25) + (Demographics × 0.30) + (Competition × 0.15) + (Healthcare × 0.20) + (Complementary × 0.10)",
            "range": "0–100 scale where 100 = optimal conditions across all criteria",
            "interpretation": {
                "excellent": "≥80 → Excellent potential",
                "good": "60–79 → Good potential",
                "caution": "<60 → Requires careful consideration",
            },
        }

        report_data["methodology"] = methodology

        # Key Statistical Insights
        stats_insights_title = "📈 Key Statistical Insights"
        md.write(f"## {stats_insights_title}\n\n")

        statistical_insights = []

        insight1 = f"💰 **Price vs Performance:** Among the {len(sites)} analysed properties, price showed a weak-to-moderate correlation with suitability, suggesting inefficiencies in the rental market and hidden value opportunities."
        md.write(f"- {insight1}\n")
        statistical_insights.append(
            {
                "category": "Price vs Performance",
                "description": f"Among the {len(sites)} analysed properties, price showed a weak-to-moderate correlation with suitability, suggesting inefficiencies in the rental market and hidden value opportunities.",
                "total_sites": len(sites),
            }
        )

        insight2 = "🏪 **Business Ecosystem Impact:** Locations with more than 15 nearby businesses consistently achieved higher performance scores, highlighting the critical role of commercial density."
        md.write(f"- {insight2}\n")
        statistical_insights.append(
            {
                "category": "Business Ecosystem Impact",
                "description": "Locations with more than 15 nearby businesses consistently achieved higher performance scores, highlighting the critical role of commercial density.",
                "threshold": 15,
            }
        )

        insight3 = "🚗 **Traffic Flow Optimisation:** Optimal site performance was observed where average traffic speeds range between 20–35 km/h, balancing accessibility with manageable congestion."
        md.write(f"- {insight3}\n")
        statistical_insights.append(
            {
                "category": "Traffic Flow Optimisation",
                "description": "Optimal site performance was observed where average traffic speeds range between 20–35 km/h, balancing accessibility with manageable congestion.",
                "optimal_speed_range": "20-35 km/h",
            }
        )

        insight4 = "👥 **Demographic Alignment:** Variance from the target median age of 35 strongly influenced demographic scores, validating age-based targeting across diverse districts."
        md.write(f"- {insight4}\n\n")
        statistical_insights.append(
            {
                "category": "Demographic Alignment",
                "description": "Variance from the target median age of 35 strongly influenced demographic scores, validating age-based targeting across diverse districts.",
                "target_age": 35,
            }
        )

        report_data["statistical_insights"] = statistical_insights

        # Footer
        md.write("---\n")
        footer_text = f"""*Report generated using advanced geospatial analysis and machine learning algorithms.*  
        \n*Analysis covered {len(sites)} candidate locations with comprehensive multi-criteria scoring.*\n\n"""
        md.write(footer_text)

        report_data["metadata"] = {
            "generation_method": "Advanced geospatial analysis and machine learning algorithms",
            "total_sites_analyzed": len(sites),
            "report_file_path": md_path,
        }

    print(f"✅ Enhanced report generated: {md_path}")
    # Return the structured report data
    return report_data


def generate_table_with_current_comparison(
    top_sites: List[Dict],
    current_location: List[Dict],  # usually just 1 dict
    CRITERION_WEIGHTS: Dict[str, float],
) -> str:
    """
    Generate Markdown table for top_sites with comparisons to current_location.
    Comparison format: top_val (current_val, XX% improvement/disadvantage)
    """

    current = current_location[0]  # baseline
    header = (
        "| Rank | Site Name | Rent Price (SAR) | Final Score | Traffic | Demographics | "
        "Competition | Healthcare Environment  | Complementary Businesses | View |\n"
        "|:----:|:---------:|:-----------:|:-----------:|:-------:|:-----------:|"
        ":----------:|:-----------------:|:-------------------:|:---:|\n"
    )

    rows = []

    # Helper to format comparison
    def compare(top_val, curr_val):
        if curr_val == 0:
            return f"{top_val} ({curr_val}, N/A)"
        diff_pct = abs(top_val - curr_val)
        if top_val > curr_val:
            result = f"{top_val} (⬆️{diff_pct})"
        elif top_val < curr_val:
            result = f"{top_val} (⬇️{diff_pct})"
        else:
            result = f"{top_val} (0 ⬇️⬆️)"
        return f"&lrm;{result}"

    for site in top_sites:
        price_display = (
            f"{site.get('price', 0):,}" if site.get("price") else "N/A"
        )

        total_score = site["total_score"]
        traffic = site.get("weighted_scores", {}).get("traffic", 0)
        demographics = site.get("weighted_scores", {}).get("demographics", 0)
        competition = site.get("weighted_scores", {}).get("competition", 0)
        healthcare = site.get("weighted_scores", {}).get("healthcare", 0)
        complementary = site.get("weighted_scores", {}).get("complementary", 0)

        curr_final = current["total_score"]
        curr_traffic = current.get("weighted_scores", {}).get("traffic", 0)
        curr_demo = current.get("weighted_scores", {}).get("demographics", 0)
        curr_comp = current.get("weighted_scores", {}).get("competition", 0)
        curr_health = current.get("weighted_scores", {}).get("healthcare", 0)
        curr_complement = current.get("weighted_scores", {}).get(
            "complementary", 0
        )

        # Format each score with comparison
        final_display = compare(total_score, curr_final)
        traffic_display = compare(traffic, curr_traffic)
        demo_display = compare(demographics, curr_demo)
        comp_display = compare(competition, curr_comp)
        health_display = compare(healthcare, curr_health)
        complement_display = compare(complementary, curr_complement)

        rows.append(
            f"| {site['rank']} | {site['display_name']} | {price_display} | {final_display} | "
            f"{traffic_display} | {demo_display} | {comp_display} | {health_display} | {complement_display} | "
            f"[View]({site['url']}) |\n"
        )

    return header + "".join(rows) + "\n"


def write_detailed_analysis_with_current(
    md,
    sites,
    current_location,
    CRITERION_WEIGHTS,
    maps_dir,
    md_path,
    section_title: str,
    category: str = "Shop For Rent",
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Write detailed site analysis comparing top locations with current location and return structured data."""

    if not sites:
        return [], []

    md.write(f"## {section_title}\n\n")

    detailed_analysis = []
    current_detailed_analysis = []

    for i, s in enumerate(sites, start=1):
        total_score_100 = s["total_score"]
        current_total_score_100 = None
        current_s = None

        if current_location and len(current_location) > 0:
            current_s = current_location[0]  # Assuming single current location
            current_total_score_100 = current_s["total_score"]

        # Write headers for both locations
        if current_s:
            md.write(
                f"### {i}. {s['display_name']} vs Current Location Comparison (Scores: {total_score_100} vs {current_total_score_100})\n\n"
            )
        else:
            md.write(
                f"### {i}. {s['display_name']} (Score: {total_score_100})\n\n"
            )

        # Location info for top site
        coords_text = (
            f"**Location:** {s['lat']}, {s['lng']}"
            if (s["lat"] is not None and s["lng"] is not None)
            else f"**Location:** {s.get('raw_place') or 'N/A'}"
        )
        price_text = (
            f"**Rent Price:** {s.get('price', 0):,} SAR"
            if s.get("price")
            else "**Rent Price:** Not specified"
        )

        md.write(
            f"**Top Location:** {coords_text} | {price_text} | Category: {category}\n\n"
        )

        # Current location info if exists
        if current_s:
            current_coords_text = (
                f"**Location:** {current_s['lat']}, {current_s['lng']}"
                if (
                    current_s["lat"] is not None
                    and current_s["lng"] is not None
                )
                else f"**Location:** {current_s.get('raw_place') or 'N/A'}"
            )
            current_price_text = (
                f"**Rent Price:** {current_s.get('price', 0):,} SAR"
                if current_s.get("price")
                else "**Rent Price:** Not specified"
            )
            md.write(
                f"**Current Location:** {current_coords_text} | {current_price_text} | Category: {category}\n\n"
            )

        analysis_space = (
            "Analysis Preformed for locations with 2km from all sides"
        )
        md.write(f"{analysis_space}\n\n")

        # Generate insights for top location
        md.write("#### Top Location Analysis\n")
        md.write(generate_detailed_insights(s))
        md.write(f"**[🗺️ View location]({s['url']})**\n\n")

        # Generate insights for current location if exists

        # Make paths relative to markdown directory
        map_image_rel = (
            os.path.relpath(map_image, os.path.dirname(md_path)).replace(
                "\\", "/"
            )
            if map_image
            else None
        )
        html_map_rel = (
            os.path.relpath(html_map, os.path.dirname(md_path)).replace(
                "\\", "/"
            )
            if html_map
            else None
        )
        if map_image_rel:
            md.write(f"![Top Location Map]({map_image_rel})\n\n")
        if html_map_rel:
            md.write(
                f"[Open interactive map - Top Location]({html_map_rel})\n\n"
            )
        if current_s:
            md.write("#### Current Location Analysis\n")
            md.write(generate_detailed_insights(current_s))
            md.write(f"**[🗺️ View location]({current_s['url']})**\n\n")

        # Maps for top location

        # Maps for current location if exists
        current_map_image_rel = None
        current_html_map_rel = None
        if current_s:
            current_map_image, current_html_map = generate_all_site_map_image(
                current_s
            )
            # Make paths relative to markdown directory
            current_map_image_rel = (
                os.path.relpath(
                    current_map_image, os.path.dirname(md_path)
                ).replace("\\", "/")
                if current_map_image
                else None
            )
            current_html_map_rel = (
                os.path.relpath(
                    current_html_map, os.path.dirname(md_path)
                ).replace("\\", "/")
                if current_html_map
                else None
            )
            if current_map_image_rel:
                md.write(
                    f"![Current Location Map]({current_map_image_rel})\n\n"
                )
            if current_html_map_rel:
                md.write(
                    f"[Open interactive map - Current Location]({current_html_map_rel})\n\n"
                )

        # Scoring breakdown table - extended format
        if current_s:
            md.write(
                "| Criterion | Key Metrics | Raw Score | Weighted Score | Current Raw Score | Current Weighted Score |\n"
            )
            md.write(
                "|-----------|-------------|-----------|----------------|-------------------|------------------------|\n"
            )
        else:
            md.write(
                "| Criterion | Key Metrics | Raw Score | Weighted Points |\n"
            )
            md.write(
                "|-----------|-------------|-----------|----------------|\n"
            )

        scoring_breakdown = []
        current_scoring_breakdown = []

        # Traffic scoring
        if "traffic" in CRITERION_WEIGHTS:
            traffic_raw = s.get("traffic_score", 0.0)
            weighted_points = s.get("weighted_scores", {}).get("traffic", 0.0)

            if current_s:
                current_traffic_raw = current_s.get("traffic_score", 0.0)
                current_weighted_points = current_s.get(
                    "weighted_scores", {}
                ).get("traffic", 0.0)
                md.write(
                    f"| Traffic | Average Speed | {traffic_raw} km/h | {weighted_points} | {current_traffic_raw} km/h | {current_weighted_points} |\n"
                )
                current_scoring_breakdown.append(
                    {
                        "criterion": "Traffic",
                        "sub_factor": "Average Speed",
                        "raw_score": current_traffic_raw,
                        "weighted_points": current_weighted_points,
                    }
                )
            else:
                md.write(
                    f"| Traffic | Average Speed | {traffic_raw} km/h | {weighted_points} |\n"
                )

            scoring_breakdown.append(
                {
                    "criterion": "Traffic",
                    "sub_factor": "Average Speed",
                    "raw_score": traffic_raw,
                    "weighted_points": weighted_points,
                }
            )

        # Demographics scoring
        if "demographics" in CRITERION_WEIGHTS:
            age_raw = s.get("percentage_age_above_35", 0.0)
            weighted_points = s.get("weighted_scores", {}).get(
                "demographics", 0.0
            )

            if current_s:
                current_age_raw = current_s.get("percentage_age_above_35", 0.0)
                current_weighted_points = current_s.get(
                    "weighted_scores", {}
                ).get("demographics", 0.0)
                md.write(
                    f"| Demographics | Age 35+ (%) | {age_raw}% | {weighted_points} | {current_age_raw}% | {current_weighted_points} |\n"
                )
                current_scoring_breakdown.append(
                    {
                        "criterion": "Demographics",
                        "sub_factor": "Age 35+ (%)",
                        "raw_score": current_age_raw,
                        "weighted_points": current_weighted_points,
                    }
                )
            else:
                md.write(
                    f"| Demographics | Age 35+ (%) | {age_raw}% | {weighted_points} |\n"
                )

            scoring_breakdown.append(
                {
                    "criterion": "Demographics",
                    "sub_factor": "Age 35+ (%)",
                    "raw_score": age_raw,
                    "weighted_points": weighted_points,
                }
            )

        # Competition scoring
        if "competition" in CRITERION_WEIGHTS:
            comp_raw = s.get("num_of_pharmacies", 0)
            weighted_points = s.get("weighted_scores", {}).get(
                "competition", 0.0
            )

            if current_s:
                current_comp_raw = current_s.get("num_of_pharmacies", 0)
                current_weighted_points = current_s.get(
                    "weighted_scores", {}
                ).get("competition", 0.0)
                md.write(
                    f"| Competition | Nearby Pharmacies | {comp_raw} | {weighted_points} | {current_comp_raw} | {current_weighted_points} |\n"
                )
                current_scoring_breakdown.append(
                    {
                        "criterion": "Competition",
                        "sub_factor": "Nearby Pharmacies",
                        "raw_score": current_comp_raw,
                        "weighted_points": current_weighted_points,
                    }
                )
            else:
                md.write(
                    f"| Competition | Nearby Pharmacies | {comp_raw} | {weighted_points} |\n"
                )

            scoring_breakdown.append(
                {
                    "criterion": "Competition",
                    "sub_factor": "Nearby Pharmacies",
                    "raw_score": comp_raw,
                    "weighted_points": weighted_points,
                }
            )

        # Healthcare scoring
        if "healthcare" in CRITERION_WEIGHTS:
            health_raw = s.get("num_of_hospitals", 0) + s.get(
                "num_of_dentists", 0
            )
            weighted_points = s.get("weighted_scores", {}).get(
                "healthcare", 0.0
            )

            if current_s:
                current_health_raw = current_s.get(
                    "num_of_hospitals", 0
                ) + current_s.get("num_of_dentists", 0)
                current_weighted_points = current_s.get(
                    "weighted_scores", {}
                ).get("healthcare", 0.0)
                md.write(
                    f"| Healthcare | Hospitals + Dentists | {health_raw} | {weighted_points} | {current_health_raw} | {current_weighted_points} |\n"
                )
                current_scoring_breakdown.append(
                    {
                        "criterion": "Healthcare",
                        "sub_factor": "Hospitals + Dentists",
                        "raw_score": current_health_raw,
                        "weighted_points": current_weighted_points,
                    }
                )
            else:
                md.write(
                    f"| Healthcare | Hospitals + Dentists | {health_raw} | {weighted_points} |\n"
                )

            scoring_breakdown.append(
                {
                    "criterion": "Healthcare",
                    "sub_factor": "Hospitals + Dentists",
                    "raw_score": health_raw,
                    "weighted_points": weighted_points,
                }
            )

        # Complementary businesses scoring
        if "complementary" in CRITERION_WEIGHTS:
            comp_raw = s.get("num_of_businesses_around", 0)
            weighted_points = s.get("weighted_scores", {}).get(
                "complementary", 0.0
            )

            if current_s:
                current_comp_raw = current_s.get("num_of_businesses_around", 0)
                current_weighted_points = current_s.get(
                    "weighted_scores", {}
                ).get("complementary", 0.0)
                md.write(
                    f"| Complementary | Nearby Businesses | {comp_raw} | {weighted_points} | {current_comp_raw} | {current_weighted_points} |\n"
                )
                current_scoring_breakdown.append(
                    {
                        "criterion": "Complementary",
                        "sub_factor": "Nearby Businesses",
                        "raw_score": current_comp_raw,
                        "weighted_points": current_weighted_points,
                    }
                )
            else:
                md.write(
                    f"| Complementary | Nearby Businesses | {comp_raw} | {weighted_points} |\n"
                )

            scoring_breakdown.append(
                {
                    "criterion": "Complementary",
                    "sub_factor": "Nearby Businesses",
                    "raw_score": comp_raw,
                    "weighted_points": weighted_points,
                }
            )
        md.write("\n")

        detailed_analysis.append(
            {
                "rank": i,
                "display_name": s["display_name"],
                "total_score": round(total_score_100, 1),
                "analysis_space": analysis_space,
                "location": {
                    "latitude": s["lat"] if s["lat"] is not None else None,
                    "longitude": s["lng"] if s["lng"] is not None else None,
                    "raw_place": s.get("raw_place"),
                },
                "price": s.get("price", 0) if s.get("price") else None,
                "category": category,
                "url": s.get("url"),
                "maps": {
                    "static_map_url": map_image_rel,
                    "interactive_map_url": html_map_rel,
                },
                "detailed_insights": generate_detailed_insights_dict(s),
                "scoring_breakdown": scoring_breakdown,
            }
        )

        if current_s:
            current_detailed_analysis.append(
                {
                    "rank": i,
                    "display_name": current_s["display_name"],
                    "total_score": round(current_total_score_100, 1),
                    "analysis_space": analysis_space,
                    "location": {
                        "latitude": (
                            current_s["lat"]
                            if current_s["lat"] is not None
                            else None
                        ),
                        "longitude": (
                            current_s["lng"]
                            if current_s["lng"] is not None
                            else None
                        ),
                        "raw_place": current_s.get("raw_place"),
                    },
                    "price": (
                        current_s.get("price", 0)
                        if current_s.get("price")
                        else None
                    ),
                    "category": category,
                    "url": current_s.get("url"),
                    "maps": {
                        "static_map_url": current_map_image_rel,
                        "interactive_map_url": current_html_map_rel,
                    },
                    "detailed_insights": generate_detailed_insights_dict(
                        current_s
                    ),
                    "scoring_breakdown": current_scoring_breakdown,
                }
            )

    return detailed_analysis, current_detailed_analysis
