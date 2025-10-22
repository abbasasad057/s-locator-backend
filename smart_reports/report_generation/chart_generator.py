"""
Chart generation utilities for target business site selection analysis.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from typing import List, Dict
from all_types.request_dtypes import Reqsmartreport
import arabic_reshaper
from bidi.algorithm import get_display
from .report_config import CHART_DPI, CHART_FIGSIZE
import logging


# Set up matplotlib for Arabic text
from matplotlib import rcParams

rcParams["font.family"] = "Arial"
rcParams["axes.unicode_minus"] = False


def setup_arabic_text(text: str) -> str:
    """Process Arabic text for proper display in matplotlib."""
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    except:
        return text


def plot_top_stacked(
    sites: List[Dict], top_n: int, outpath: str, req: Reqsmartreport
):
    """Generate stacked bar chart of top performing sites."""
    top = sorted(
        sites.values(), key=lambda s: s.get("total_score", 0), reverse=True
    )[:top_n]
    if not top:
        return

    # Process Arabic labels
    labels = [setup_arabic_text(s["display_name"]) for s in top]

    # Prepare data for stacking
    criterions = list(req.evaluation_metrics.__class__.model_fields.keys())
    comps = [f"{c}_score" for c in criterions]
    data = np.array([[s["scores"].get(c, 0) for s in top] for c in comps])

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE, dpi=CHART_DPI)
    bottoms = np.zeros(len(labels))
    cmap = cm.get_cmap("tab20")

    # Create stacked bars
    for i in range(data.shape[0]):
        ax.bar(
            labels,
            data[i],
            bottom=bottoms,
            label=criterions[i].capitalize(),
            color=cmap(i),
        )
        bottoms += data[i]

    ax.set_title(
        f"Top {top_n} Locations — Component Scores (Stacked)",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_ylabel("Weighted Points", fontsize=12)
    ax.legend(loc="upper right", fontsize="small")

    # Format x-axis
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=10)

    # Add grid for better readability
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_axisbelow(True)

    plt.subplots_adjust(bottom=0.25, top=0.9, left=0.1, right=0.9)
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_score_vs_price(top_sites: List[Dict], outpath: str):
    """Scatter plot of Final Score vs Price for top N sites with colored points like the example."""
    CHART_FIGSIZE = (10, 6)
    CHART_DPI = 100

    # Sites are already pre-filtered and assumed to have valid prices
    top_sites = top_sites
    if not top_sites:
        return

    # Extract data
    scores = [s["total_score"] for s in top_sites]
    prices = [s.get("price", 0) for s in top_sites]
    names = [f"  Number {i}" for i, _ in enumerate(top_sites)]

    # Color points based on score tier
    colors = []
    for score in scores:
        if score >= 75:
            colors.append("green")
        elif score >= 70:
            colors.append("orange")
        else:
            colors.append("red")

    fig, ax = plt.subplots(figsize=CHART_FIGSIZE, dpi=CHART_DPI)

    # Scatter plot
    ax.scatter(
        prices,
        scores,
        color=colors,
        s=80,
        edgecolor="black",
        linewidth=0.5,
        zorder=3,
    )

    # Optional: add labels next to points
    for x, y, label in zip(prices, scores, names):
        ax.text(x, y, f" {label}", fontsize=9, ha="left", va="center", zorder=4)

    ax.set_xlabel("Rent Price (SAR)", fontsize=12)
    ax.set_ylabel("Final Score", fontsize=12)
    ax.set_title(
        "Rent Price vs Final Score — Top Sites",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    plt.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def plot_complementary_vs_competition(
    top_n_sites: List[Dict], outpath: str
):
    """
    Generates a scatter plot of complementary facility count vs. competition for the top N sites.

    Args:
        sites (List[Dict]): A list of pre-filtered site data dictionaries (already top N).
        outpath (str): The file path to save the generated chart image.
        top_n (int): The number of top sites (for labeling purposes).
    """
    CHART_FIGSIZE = (10, 6)
    CHART_DPI = 100
    if not top_n_sites:
        logging.warning("No sites to plot for complementary vs competition chart.")
        return

    # Extract data for the plot, defaulting to 0 if keys are missing or values are None
    complementary_counts = []
    competition_counts = []
    
    for site in top_n_sites:
        # X-axis: Sum of hospitals and dentists from complementary data
        num_hospitals = site.get("num_of_hospital", 0) or 0
        num_dentists = site.get("num_of_dentist", 0) or 0
        complementary_total = num_hospitals + num_dentists
        complementary_counts.append(complementary_total)
        
        # Y-axis: Number of competing pharmacy
        num_target_business = site.get("num_of_pharmacy", 0) or 0
        competition_counts.append(num_target_business)

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=CHART_FIGSIZE, dpi=CHART_DPI)

    # Create the scatter plot with styling similar to the example image
    ax.scatter(
        complementary_counts,
        competition_counts,
        s=100,  # Marker size
        c="#3498db",  # A clear, medium blue color
        alpha=0.8,  # Semi-transparent markers
        edgecolors="#2980b9",  # A slightly darker edge for definition
    )

    # --- Titles and Labels ---
    ax.set_title(
        "Complementary Facilities vs Competition",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel(
        "Number of Complementary Facilities (Hospitals & Dentists)", fontsize=12
    )
    ax.set_ylabel("Number of Competing target business", fontsize=12)

    # --- Grid and Layout ---
    ax.grid(True, which="both", linestyle="--", linewidth=0.5, color="gray")
    ax.set_axisbelow(True)  # Ensure the grid is drawn behind the plot elements

    # Set axis limits to start from 0 and add some padding for clarity
    ax.set_xlim(left=-1, right=max(complementary_counts or [0]) * 1.1 + 2)
    ax.set_ylim(bottom=-1, top=max(competition_counts or [0]) * 1.1 + 2)

    # --- Save Figure ---
    plt.tight_layout()
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)
    logging.info(
        f"Successfully generated complementary vs competition chart at {outpath}"
    )
