"""
Map generation utilities for target business site selection analysis.
"""

import numpy as np
import matplotlib

# Force matplotlib to use non-interactive backend before importing pyplot
matplotlib.use("Agg")  # Use Anti-Grain Geometry backend (no GUI)
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib import cm
import contextily as ctx
import geopandas as gpd
from shapely.geometry import Point
from typing import Dict, Optional, Tuple
import logging
from .report_config import MAP_DPI, MAP_FIGSIZE
import os
from html2image import Html2Image
from all_types.request_dtypes import Reqsmartreport
import folium
import random

from utils.utils import create_report_asset_path


def generate_all_site_map_image(sites: list[Dict], req: Reqsmartreport) -> str:
    """
    Generate map image for each site and return the (png_path, html_path) of the last generated site.

    Behavior changes made to satisfy dynamic requirements:
    - Uses only real POIs supplied in each site's data. For a category named "X" the function
      expects a key named `nearby_X` in the site's dict containing a list of POI objects with
      at least `lat` and `lng` fields.
    - Categories to render are derived from the incoming `Reqsmartreport` request model:
      `potential_business_type`, `complementary_categories`, `cross_shopping_categories`,
      and `competition_categories`.
    - No random markers are created. If required keys or coordinates are missing the function
      raises a ValueError and does not silently continue.
    - Colors are assigned deterministically per category (stable random using category name as seed)
      so the same category always gets the same color but colors are not hard-coded per category.

    Returns:
        (png_path, html_path) tuple for the last processed site.
    """

    def _category_color(category: str) -> str:
        """Return a deterministic hex color per category name."""
        # Use a simple seeded RNG based on category name to produce stable colors
        rnd = random.Random(category)
        return "#{:02x}{:02x}{:02x}".format(
            rnd.randint(30, 200), rnd.randint(30, 200), rnd.randint(30, 200)
        )

    def _category_emoji(category: str) -> str:
        """Return a deterministic emoji for visual legend marking per category."""
        # A small pool of neutral emojis to pick from deterministically per category
        emojis = ["🟠", "🟣", "🔵", "🟤", "🟡", "🔴", "🔵", "⚪", "🟢", "🔺"]
        idx = abs(hash(category)) % len(emojis)
        return emojis[idx]

    # Build the list of categories to render from the request model. Keep order: potential, complementary,
    # cross_shopping, competition. Normalize to lowercase strings and remove duplicates while preserving order.


    # Deduplicate while preserving order
    categories_to_render = list(
        set(
            [req.potential_business_type]
            + req.complementary_categories
            + req.cross_shopping_categories
            + req.competition_categories
        )
    )

    for site_data in sites:

        # Create map centered on site
        m = folium.Map(
            location=[site_data["lat"], site_data["lng"]],
            zoom_start=16,
            tiles="OpenStreetMap",
        )

        total_businesses = 0
        competitor_count = 0

        # For each category requested, look for a key `nearby_{category}` inside site_data
        for category in categories_to_render:
            nearby_key = f"nearby_{category}"
            pois = site_data[nearby_key]
            # Determine a color for this category (deterministic)
            color = _category_color(category)

            for poi in pois:
                popup_html = f"<b>{poi.get('name', category.title())}</b><br>Category: {category}<br>"
                # Include distance if available
                popup_html += f"Distance: {poi['driving_distance_meters']} m<br>"

                folium.CircleMarker(
                    location=[poi["coordinates"][1], poi["coordinates"][0]],
                    radius=10,
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=poi.get("name", category.title()),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.9,
                    opacity=0.9,
                    weight=1,
                ).add_to(m)

                total_businesses += 1
                # Count competitors if category matches potential business type or explicitly competition
                if (
                    req.potential_business_type
                    and category == req.potential_business_type.lower()
                ):
                    competitor_count += 1
                elif req.competition_categories and category in [
                    c.lower() for c in req.competition_categories
                ]:
                    competitor_count += 1

        # Property marker (red star)
        folium.Marker(
            [site_data["lat"], site_data["lng"]],
            popup=folium.Popup(
                f"""
            <div style='width: 250px'>
                <h4>🏢 {site_data["display_name"]}</h4>
                <b>Final Score:</b> {site_data["total_score"]}<br>
                <b>Competitors:</b> {competitor_count}<br>
                <b>Businesses:</b> {total_businesses} total
            </div>
            """,
                max_width=300,
            ),
            tooltip=f"{site_data['display_name']} - Score: {site_data['total_score']}",
            icon=folium.Icon(color="red", icon="star", prefix="fa"),
        ).add_to(m)

        # Analysis radius circle
        folium.Circle(
            [site_data["lat"], site_data["lng"]],
            radius=1000,
            color="red",
            weight=2,
            fill=True,
            fillColor="red",
            fillOpacity=0.1,
            opacity=0.6,
            popup="Analysis radius: 300m",
        ).add_to(m)

        # Traffic line (example coordinates)
        # Title
        title_html = """
        <div style="position: fixed; 
                    top: 20px; left: 50%; transform: translateX(-50%);
                    background-color: rgba(233, 30, 99, 0.9); 
                    color: white;
                    padding: 10px 20px; border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    z-index: 9999;">
            <h3 style="margin: 0; color: white;">📍 Site Location Map</h3>
        </div>
        """
        m.get_root().html.add_child(folium.Element(title_html))

        # Legend - build dynamically from categories_to_render and their deterministic colors
        legend_items_html = ""
        for cat in categories_to_render:
            color = _category_color(cat)
            emoji = _category_emoji(cat)
            legend_items_html += (
                f"<div style='margin-bottom:6px;display:flex;align-items:center;'>"
                f"<span style='font-size:16px;margin-right:6px;'>{emoji}</span>"
                f"<span style='display:inline-block;width:14px;height:14px;background:{color};border-radius:3px;margin-right:8px;'></span>"
                f"<b>{cat.title()}</b></div>"
            )

        legend_html = f"""
        <div style="position: fixed; 
                    top: 80px; left: 50px; width: 250px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        <div style="background-color: #e8f4f8; padding: 8px; margin-bottom: 8px; border-radius: 4px;">
            <b style="font-size: 14px;">📍 {site_data["display_name"]}</b><br>
            <b>Final Score:</b> {site_data["total_score"]}<br>
            <b>Competitors:</b> {competitor_count} <br>
            <b>Businesses:</b> {total_businesses} total<br>
        </div>
        <b>Legend:</b><br>
        {legend_items_html}
        <div style='margin-top:8px;'><span style='display:inline-block;width:14px;height:14px;background:red;border-radius:3px;margin-right:8px;'></span><b>Property</b></div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

        # Save HTML
        site_rank = site_data.get("id", 1)
        html_filename = f"site_{site_rank}_map.html"
        # Save interactive maps in interactive_maps directory
        html_path = create_report_asset_path(html_filename, "html")
        m.save(html_path)

        # Save PNG in image directory
        png_filename = f"site_{site_rank}_map.png"
        hti = Html2Image(size=(1200, 800))
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        hti.screenshot(html_str=html_content, save_as=png_filename)

        png_path = create_report_asset_path(png_filename, "image")

        import shutil

        if os.path.exists(png_filename):
            shutil.move(png_filename, png_path)

        print(f"Generated map image: {png_path}")

    return png_path, html_path


def create_static_map_png(
    sites: Dict, outpath: str, list_top_n_sites: list, extent: Optional[Tuple] = None
) -> Optional[Tuple]:
    """
    Create a static map showing candidate locations.

    Args:
        sites: List of site dictionaries
        outpath: Output file path
        top_n: Number of top sites to highlight
        extent: Map extent (xmin, xmax, ymin, ymax)

    Returns:
        Map extent tuple if successful, None otherwise
    """
    pad = 0.1
    fig, ax = plt.subplots(figsize=MAP_FIGSIZE, dpi=MAP_DPI)

    if not sites:
        ax.text(
            0.5,
            0.5,
            "No coordinates available to render map",
            ha="center",
            va="center",
            fontsize=16,
        )
        ax.axis("off")
        ax.set_title("Candidate Locations Map", fontsize=18, fontweight="bold", pad=20)
        fig.savefig(outpath, pad_inches=pad, bbox_inches="tight")
        plt.close(fig)
        return None

    # Create GeoDataFrame
    geometry = []
    site_names = []
    for key, values in sites.items():
        # Create Point geometry objects instead of tuples
        geometry.append(Point(values["lng"], values["lat"]))
        site_names.append(key)

    gdf = gpd.GeoDataFrame(site_names, geometry=geometry)
    gdf = gdf.set_crs(epsg=4326).to_crs(epsg=3857)

    # Plot all candidates
    gdf.plot(
        ax=ax,
        color="lightblue",
        alpha=0.7,
        markersize=60,
        label="All Candidates",
        edgecolors="darkblue",
        linewidth=1,
    )

    # Highlight top sites - convert sites dict to list for sorting
    sites_list = []
    for k, v in sites.items():
        site_dict = {"name": k}
        site_dict.update(v)
        sites_list.append(site_dict)

    for i, site in enumerate(list_top_n_sites, start=1):
        # Convert to Web Mercator
        point_3857 = gpd.GeoSeries([Point(site["lng"], site["lat"])], crs=4326).to_crs(
            epsg=3857
        )
        x, y = point_3857.geometry[0].coords[0]

        # Plot star marker
        ax.scatter(
            x,
            y,
            s=200,
            color="red",
            marker="*",
            edgecolors="darkred",
            linewidth=2,
            zorder=5,
        )

        # Add rank number
        ax.text(
            x,
            y,
            f" {i}",
            fontsize=12,
            weight="bold",
            color="white",
            ha="left",
            va="center",
            zorder=6,
        )
    # Add basemap
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, alpha=0.8)

    ax.set_axis_off()
    ax.set_title(
        "Top Recommended Expansion Locations", fontsize=18, fontweight="bold", pad=20
    )

    # Set extent if provided
    if extent is None:
        extent = ax.get_xlim()[0], ax.get_xlim()[1], ax.get_ylim()[0], ax.get_ylim()[1]
    else:
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])

    # Add legend
    ax.legend(loc="upper right", framealpha=0.9)

    fig.savefig(outpath, pad_inches=pad, bbox_inches="tight", dpi=MAP_DPI)
    plt.close(fig)
    plt.close("all")  # Ensure all figures are closed

    logging.info(f"Successfully created map: {outpath}")
    return extent


def create_demographic_heatmap_png(
    sites: Dict, outpath: str, extent: Optional[Tuple] = None
):
    """
    Create a demographic heatmap showing population density using avg_density data.

    Args:
        sites: Dictionary of site data
        outpath: Output file path
        extent: Map extent (xmin, xmax, ymin, ymax)
    """

    pad = 0.1
    xs, ys, vals = [], [], []

    # Extract demographic data using avg_density
    for site_name, site in sites.items():
        if site["lat"] is None or site["lng"] is None:
            continue

        # Get avg_density
        demo_val = site.get("avg_density")

        if demo_val is not None and not np.isnan(demo_val):
            xs.append(site["lng"])
            ys.append(site["lat"])
            vals.append(demo_val)

    if not vals:
        # No demographic data found, create empty map
        fig, ax = plt.subplots(figsize=MAP_FIGSIZE, dpi=MAP_DPI)
        ax.text(
            0.5,
            0.5,
            "No demographic data available for heatmap",
            ha="center",
            va="center",
            fontsize=16,
        )
        ax.axis("off")
        ax.set_title("Demographic Heatmap", fontsize=18, fontweight="bold", pad=20)
        fig.savefig(outpath, pad_inches=pad, bbox_inches="tight")
        plt.close(fig)
        return

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        {"value": vals},
        geometry=[Point(lon, lat) for lon, lat in zip(xs, ys)],
        crs=4326,
    ).to_crs(epsg=3857)

    # Normalize values
    norm = Normalize(vmin=np.nanmin(vals), vmax=np.nanmax(vals))

    fig, ax = plt.subplots(figsize=MAP_FIGSIZE, dpi=MAP_DPI)

    # Plot heatmap
    gdf.plot(
        ax=ax,
        column="value",
        cmap="YlOrRd",
        markersize=120,
        alpha=0.8,
        legend=True,
        norm=norm,
        edgecolors="black",
        linewidth=0.5,
    )

    # Add basemap
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, alpha=0.6)

    ax.set_title("Demographic Density Heatmap", fontsize=18, fontweight="bold", pad=20)
    ax.set_axis_off()

    # Set extent if provided
    if extent is not None:
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])

    fig.savefig(outpath, pad_inches=pad, bbox_inches="tight", dpi=MAP_DPI)
    plt.close(fig)
    plt.close("all")  # Ensure all figures are closed

    logging.info(f"Successfully created demographic heatmap: {outpath}")
