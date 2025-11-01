"""
Analysis & Intelligence router module
Handles analysis operations, intelligence data, sales optimization, and special features
"""

from typing import Any, Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from all_types.request_dtypes import (
    ReqModel,
    ReqSrcDistination,
    ReqIntelligenceViewport,
    ReqClustersForSalesManData,
    Reqsmartreport
)
from all_types.response_dtypes import (
    ResModel,
    ResSrcDistination
)
from backend_common.request_processor import request_handling
from backend_common.auth import JWTBearer
from data_fetcher import load_distance_drive_time_polygon
from storage_methods import fetch_intelligence_by_viewport
from sales_man_problem import get_clusters_for_sales_man
from hub_expansion_analysis import (
    analyze_hub_expansion,
    ReqHubExpansion,
    ResHubExpansion,
)
from config_factory import CONF

from all_types.response_dtypes import ResIntelligenceViewport
from smart_reports.reports import generate_html_report
# from traffic_data import get_here_traffic_score
from standalone_google_maps_traffic import analyze_traffic_at_location
from pydantic import BaseModel

analysis_router = APIRouter()


@analysis_router.post(
    CONF.distance_drive_time_polygon, response_model=ResModel[ResSrcDistination]
)
async def distance_drivetime_polygon(req: ReqModel[ReqSrcDistination]):
    response = await request_handling(
        req.request_body,
        ReqSrcDistination,
        ResModel[ResSrcDistination],
        load_distance_drive_time_polygon,
        wrap_output=True,
    )
    return response


@analysis_router.post(
    CONF.fetch_population_by_viewport,
    response_model=ResModel[ResIntelligenceViewport],
    dependencies=[Depends(JWTBearer())],
)
async def ep_fetch_population_by_viewport(
    req: ReqModel[ReqIntelligenceViewport], request: Request
):
    response = await request_handling(
        req.request_body,
        ReqIntelligenceViewport,
        ResModel[ResIntelligenceViewport],
        fetch_intelligence_by_viewport,
        wrap_output=True,
    )
    return response


@analysis_router.post(
    CONF.temp_sales_man_problem,
    response_model=ResModel[Any],
    dependencies=[Depends(JWTBearer())],
)
async def ep_fetch_clusters_for_sales_man(
    req: ReqModel[ReqClustersForSalesManData], request: Request
):
    response = await request_handling(
        req.request_body,
        ReqClustersForSalesManData,
        ResModel[Any],
        get_clusters_for_sales_man,
        wrap_output=True,
    )
    return response


@analysis_router.post(
    CONF.hub_expansion_analysis,
    response_model=ResModel[ResHubExpansion],
    dependencies=[Depends(JWTBearer())],
)
async def ep_hub_expansion_analysis(
    req: ReqModel[ReqHubExpansion], request: Request
):
    response = await request_handling(
        req.request_body,
        ReqHubExpansion,
        ResModel[ResHubExpansion],
        analyze_hub_expansion,
        wrap_output=True,
    )
    return response


@analysis_router.post(
    CONF.smart_pharmacy_report,   # <-- add a new path constant in CONF
    response_model=ResModel[dict[str, Any]],   # assuming your function returns a file path (string)
    dependencies=[Depends(JWTBearer())],
)
async def ep_pharmacy_site_selection(
    req: ReqModel[Reqsmartreport], request: Request
):
    response = await request_handling(
        req.request_body,
        Reqsmartreport,         # request schema
        ResModel[dict[str, Any]],  
        generate_html_report,
        wrap_output=True,
    )
    return response
