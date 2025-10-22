#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path
from time import sleep

import requests

from utils.utils import DIR_TRAFFIC_SCREENSHOTS

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

API_BASE_URL = "http://49.12.190.229:8000"
LOGIN_ENDPOINT = f"{API_BASE_URL}/login"
ANALYZE_ENDPOINT = f"{API_BASE_URL}/analyze-batch"
JOB_STATUS_ENDPOINT = f"{API_BASE_URL}/job"


# Login to get token (you might want to move this outside the function)
def get_auth_token() -> str:
    """Get authentication token from the API"""
    try:
        login_data = {
            "username": os.getenv(
                "ADMIN_USERNAME", "admin"
            ),  # Replace with your username
            "password": os.getenv(
                "ADMIN_PASSWORD", "123456"
            ),  # Replace with your password
        }
        response = requests.post(LOGIN_ENDPOINT, data=login_data, timeout=30)
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    except Exception as e:
        logger.error(f"Failed to get auth token: {e}")
        raise


def submit_traffic_job(locations_batch, token) -> str | None:
    """Submit a batch of locations for traffic analysis"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "locations": [
                {
                    "lat": loc.get("lat", 0),
                    "lng": loc.get("lng", 0),
                    "storefront_direction": loc.get(
                        "storefront_direction", "north"
                    ),  # Default direction
                    "day": loc.get("day", "Monday"),  # Default day
                    "time": loc.get("time", "6PM"),  # Default time (6:00 PM)
                }
                for loc in locations_batch[:20]
            ]
        }
        response = requests.post(
            ANALYZE_ENDPOINT, json=payload, headers=headers, timeout=30
        )
        response.raise_for_status()
        return response.json()["job_id"]
    except Exception as e:
        logger.error(f"Failed to submit traffic job: {e}")
        raise


def poll_job_status(job_id, token) -> dict | None:
    """Poll job status until completion"""
    headers = {"Authorization": f"Bearer {token}"}
    max_attempts = 60  # 5 minutes with 5-second intervals
    attempt = 0

    while attempt < max_attempts:
        try:
            response = requests.get(
                f"{JOB_STATUS_ENDPOINT}/{job_id}", headers=headers, timeout=30
            )
            response.raise_for_status()
            job_data = response.json()

            status = job_data.get("status")

            if status == "done":
                return job_data
            elif status in ("failed", "canceled"):
                error_msg = job_data.get("error", "Unknown error")
                raise Exception(f"Job {status}: {error_msg}")
            elif status in ("pending", "running"):
                remaining = job_data.get("remaining", 0)
                logger.info(f"Job {job_id} status: {status}, remaining: {remaining}")
                sleep(5)  # Wait 5 seconds before polling again
                attempt += 1
            else:
                logger.warning(f"Unknown job status: {status}")
                sleep(5)
                attempt += 1

        except Exception as e:
            logger.error(f"Error polling job status: {e}")
            if attempt >= max_attempts - 1:
                raise
            sleep(5)
            attempt += 1

    raise Exception(f"Job {job_id} timed out after {max_attempts} attempts")


def process_traffic_batch(locations_batch: list):
    """Process a batch of locations through the API"""
    try:
        # Ignore exists traffic map screenshot
        locations_batch_copy = locations_batch.copy()
        for i, loc in enumerate(locations_batch):
            cur_screenshot_url = (
                Path(DIR_TRAFFIC_SCREENSHOTS)
                / f"traffic_{loc.get("lat", 0)},{loc.get("lng", 0)}_pinned.png"
            )
            if os.path.exists(cur_screenshot_url):
                locations_batch_copy.pop(i)

        if len(locations_batch_copy) < 1:
            return

        # Login/token
        token = get_auth_token()

        # Submit job
        job_id = submit_traffic_job(locations_batch_copy, token)
        logger.info(f"Submitted job {job_id} for {len(locations_batch_copy)} locations")

        # Poll for results
        job_result = poll_job_status(job_id, token)

        # Extract and format results
        results = job_result.get("result", {}).get("results", [])

        for res in results:
            screenshot_url = res.get("screenshot_url", "")
            with open(
                Path(DIR_TRAFFIC_SCREENSHOTS)
                / f"traffic_{res['coordinates']['lat']},{res['coordinates']['lng']}_pinned.png",
                "wb",
            ) as fw:
                fw.write(requests.get(screenshot_url).content)

    except Exception as e:
        logger.error(f"Failed to process traffic batch: {e}")
