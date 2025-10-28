"""
Authentication router module
Handles all authentication related endpoints including login, registration, password management
"""

from typing import Any
from fastapi import APIRouter, Request, Depends, HTTPException
from all_types.request_dtypes import ReqModel
from all_types.response_dtypes import ResModel
from backend_common.request_processor import request_handling
from backend_common.auth import (
    create_firebase_user,
    login_user,
    reset_password,
    confirm_reset,
    change_password,
    refresh_id_token,
    change_email,
    create_user_profile,
    JWTBearer,
)
from backend_common.dtypes.auth_dtypes import (
    ReqChangeEmail,
    ReqChangePassword,
    ReqConfirmReset,
    ReqCreateFirebaseUser,
    ReqResetPassword,
    ReqUserLogin,
    ReqUserProfile,
    ReqRefreshToken,
    ReqCreateUserProfile,
    UserProfileSettings,
)
from data_fetcher import get_user_profile, update_profile
from backend_common.stripe_backend import create_stripe_customer
from config_factory import CONF


auth_router = APIRouter()


@auth_router.post(
    CONF.login, response_model=ResModel[dict[str, Any]], tags=["Authentication"]
)
async def login(req: ReqModel[ReqUserLogin]):
    response = await request_handling(
        req.request_body,
        ReqUserLogin,
        ResModel[dict[str, Any]],
        login_user,
        wrap_output=True,
    )
    return response


@auth_router.post(
    CONF.refresh_token,
    response_model=ResModel[dict[str, Any]],
    tags=["Authentication"],
)
async def refresh_token(req: ReqModel[ReqRefreshToken]):

    response = await request_handling(
        req.request_body,
        ReqRefreshToken,
        ResModel[dict[str, Any]],
        refresh_id_token,
        wrap_output=True,
    )

    return response



@auth_router.post(
    CONF.reset_password,
    response_model=ResModel[dict[str, Any]],
    tags=["Authentication"],
)
async def reset_password_endpoint(req: ReqModel[ReqResetPassword]):
    response = await request_handling(
        req.request_body,
        ReqResetPassword,
        ResModel[dict[str, Any]],
        reset_password,
        wrap_output=True,
    )
    return response


@auth_router.post(
    CONF.confirm_reset,
    response_model=ResModel[dict[str, Any]],
    tags=["Authentication"],
)
async def confirm_reset_endpoint(req: ReqModel[ReqConfirmReset]):
    response = await request_handling(
        req.request_body,
        ReqConfirmReset,
        ResModel[dict[str, Any]],
        confirm_reset,
        wrap_output=True,
    )
    return response


@auth_router.post(
    CONF.change_password,
    response_model=ResModel[dict[str, Any]],
    dependencies=[Depends(JWTBearer())],
    tags=["Authentication"],
)
async def change_password_endpoint(
    req: ReqModel[ReqChangePassword], request: Request
):
    response = await request_handling(
        req.request_body,
        ReqChangePassword,
        ResModel[dict[str, Any]],
        change_password,
        wrap_output=True,
    )
    return response


@auth_router.post(
    CONF.change_email,
    response_model=ResModel[dict[str, Any]],
    dependencies=[Depends(JWTBearer())],
    tags=["Authentication"],
)
async def change_email_endpoint(
    req: ReqModel[ReqChangeEmail], request: Request
):
    response = await request_handling(
        req.request_body,
        ReqChangeEmail,
        ResModel[dict[str, Any]],
        change_email,
        wrap_output=True,
    )
    return response


@auth_router.post(
    CONF.user_profile,
    response_model=ResModel[dict[str, Any]],
    dependencies=[Depends(JWTBearer())],
)
async def get_user_profile_endpoint(
    req: ReqModel[ReqUserProfile], request: Request
):
    response = await request_handling(
        req.request_body,
        ReqUserProfile,
        ResModel[dict[str, Any]],
        get_user_profile,
        wrap_output=True,
    )
    return response


@auth_router.post(CONF.create_user_profile, response_model=list[dict[Any, Any]])
async def create_user_profile_endpoint(req: ReqModel[ReqCreateUserProfile]):

    response_1 = await request_handling(
        req.request_body,
        ReqCreateFirebaseUser,
        dict[Any, Any],
        create_firebase_user,
        wrap_output=True,
    )

    response_2 = await request_handling(
        response_1["data"]["user_id"],
        None,
        dict[Any, Any],
        create_stripe_customer,
        wrap_output=True,
    )

    req_user_profile = ReqCreateUserProfile(
        user_id=response_1["data"]["user_id"],
        username=req.request_body.username,
        password=req.request_body.password,
        email=req.request_body.email,
    )

    response_3 = await request_handling(
        req_user_profile,
        None,
        dict[Any, Any],
        create_user_profile,
        wrap_output=True,
    )
    response = [response_1, response_2, response_3]
    return response


@auth_router.post(
    "/fastapi/update_user_profile",
    response_model=ResModel[dict[str, Any]],
    dependencies=[Depends(JWTBearer())],
)
async def update_user_profile_endpoint(req: ReqModel[UserProfileSettings]):
    response = await request_handling(
        req.request_body,
        UserProfileSettings,
        ResModel[dict[str, Any]],
        update_profile,
        wrap_output=True,
    )
    return response
