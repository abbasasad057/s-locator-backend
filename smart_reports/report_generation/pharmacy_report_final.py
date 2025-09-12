#!/usr/bin/env python3
"""
pharmacy_report_final.py

Enhanced pharmacy site selection report generator with modular architecture.
Generates comprehensive 3-page markdown reports with:
- Enhanced visual design and styling
- Investment insights and market analysis  
- Price and competition analysis
- Interactive charts and maps
- Arabic text support

Usage: python pharmacy_report_final.py [scores_path] [output_dir] [output_filename] [top_n]
"""
import os
import logging
from typing import Dict 
# Import our modular components

from .data_processor import  process_sites, calculate_statistics
from .chart_generator import plot_top_stacked, plot_traffic, plot_breakdown, plot_healthcare_vs_competition, plot_score_vs_price
from .map_generator import create_static_map_png, create_demographic_heatmap_png
from .report_generator import generate_markdown
from .report_config import (
    FONT_FAMILY, UNICODE_MINUS, DEFAULT_OUTPUT_FILENAME,
    DIR_IMAGE, create_report_asset_path
)
# Set up matplotlib for Arabic text support
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = FONT_FAMILY
plt.rcParams['axes.unicode_minus'] = UNICODE_MINUS


def generate_all_charts(sites: list, outdir: str, top_n: int , criterions : dict) -> dict:
    """Generate all required charts and return their file paths."""
    # Use image directory for static plot images

    charts = {
        'top_stacked': create_report_asset_path('top_stacked.png', "image"),
        'traffic': create_report_asset_path('traffic_flow.png', "image"),
        'best_breakdown': create_report_asset_path('best_breakdown.png', "image"),
        'price_vs_score' : create_report_asset_path('price_vs_score.png', "image"),
        'healthcare_competition' : create_report_asset_path('healthcare_competition.png', "image")
    }
    
    # Generate top stacked chart
    list_criterions = list(criterions)
    plot_top_stacked(sites, top_n, charts['top_stacked'] , list_criterions)
    logging.info("✅ Generated top stacked chart")

    
    # Generate traffic chart

    plot_traffic(sites, charts['traffic'])

    
    # Generate best site breakdown chart

    best = max(sites, key=lambda s: s.get('total_score', 0))
    plot_breakdown(best, charts['best_breakdown'] , criterions)
    plot_score_vs_price(sites , top_n=top_n, outpath=charts['price_vs_score'])
    plot_healthcare_vs_competition(sites=sites , outpath=charts['healthcare_competition'] , top_n=top_n)
    return charts

def generate_all_maps(sites: list, outdir: str, top_n: int) -> tuple:
    """Generate all required maps and return their file paths."""
    # Use image directory from config
    map_png = create_report_asset_path('candidates_map.png', "image")
    heat_png = create_report_asset_path('demographics_heatmap.png', "image")

    # Generate candidates map
    extent = None
    try:
        extent = create_static_map_png(sites, map_png, top_n=top_n)
        logging.info("✅ Generated candidates map")
    except Exception as e:
        logging.warning(f"❌ Failed to generate candidates map: {e}", exc_info=True)
    
    # Generate demographic heatmap
    try:
        create_demographic_heatmap_png(sites, heat_png, extent=extent)
        logging.info("✅ Generated demographic heatmap")
    except Exception as e:
        logging.warning(f"❌ Failed to generate demographic heatmap: {e}", exc_info=True)
    
    return map_png, heat_png


async def generate_md_report_from_data(
    scores_data: dict,
    criterion_weights : Dict[str , float],
    max_total : float ,
    output_dir,
    output_filename: str = DEFAULT_OUTPUT_FILENAME,
    top_n: int = 10,
) -> Dict:
    """
    Generate pharmacy site selection report from in-memory data.
    
    Args:
        scores_data: Dictionary containing scores data from generate_pharmacy_report function
        output_dir: Output directory path
        output_filename: Output markdown filename
        top_n: Number of top sites to analyze
        
    Returns:
        Dict Containing all the report data
        
    Raises:
        Exception: If report generation fails
    """
    
    print("🚀 Starting Enhanced Pharmacy Site Analysis...")
    print(f"📁 Output directory: {output_dir}")
    print(f"📊 Analyzing top {top_n} locations")
    
    # Process data directly from memory
    logging.info("📊 Processing site data from memory...")
    try:
        sites, warnings = process_sites(scores_data , criterion_weights)
        stats = calculate_statistics(sites)
        
        logging.info(f"✅ Processed {len(sites)} sites with {len(warnings)} warnings")
        
    except Exception as e:
        logging.error(f"❌ Failed to process data: {e}")
        raise Exception(f"Data processing failed: {e}")

    # Generate charts
    logging.info("📈 Generating charts...")
    criterions = criterion_weights.keys()
    charts = generate_all_charts(sites, output_dir, top_n , criterions)

    # Generate maps
    logging.info("🗺️  Generating maps...")
    map_png, heat_png = generate_all_maps(sites, output_dir, top_n)
    # Generate markdown report
    logging.info("📝 Generating enhanced markdown report...")
    try:
        report_data = generate_markdown(
            sites, output_dir, output_filename, top_n,
            charts, map_png, heat_png, len(sites), stats,
            max_total , criterion_weights
        )
        logging.info("✅ Report generation completed successfully")
        
    except Exception as e:
        logging.error(f"❌ Failed to generate report: {e}")
        raise Exception(f"Report generation failed: {e}")
    print(f"\n🎉 SUCCESS! Enhanced report generated:")
    if 'metadata' in report_data and 'report_file_path' in report_data['metadata']:
        report_path = report_data['metadata']['report_file_path']
        print(f"📄 Report path: {report_path}")
    print(f"\n💡 Open the report in any markdown viewer or browser for best experience!")
    
    return report_data
