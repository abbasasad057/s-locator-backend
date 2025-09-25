# tests/integration/conftest.py
import pytest
import httpx
import os
from datetime import datetime
from firebase_admin import auth
from backend_common.auth import firebase_db
from .fixtures import (
    UserSeeder,
    AuthHelper,
    DatabaseSeeder,
)
import sys
# Add project root to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app_logger import get_logger
logger = get_logger(__name__)

# Generate unique test identifiers for each test run
TEST_RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]


@pytest.fixture(scope="session")
def test_run_id():
    """Unique test run identifier"""
    return TEST_RUN_ID


@pytest.fixture(scope="session")
def api_base_url():
    """API base URL for tests - dynamically determined from environment"""
    # Check if a custom port was set by the test runner
    test_port = os.environ.get("TEST_SERVER_PORT", "8080")
    base_url = f"http://localhost:{test_port}/fastapi"
    logger.info(f"🌐 Using API base URL: {base_url}")
    return base_url


@pytest.fixture(scope="function")
def fixture_http_client(api_base_url):
    """HTTP client for API calls"""
    return httpx.Client(base_url=api_base_url, timeout=60.0)


@pytest.fixture(scope="function")
def fixture_user_seeder(fixture_http_client, test_run_id):
    """User seeder for creating test users"""
    return UserSeeder(fixture_http_client, test_run_id)


@pytest.fixture(scope="function")
def fixture_auth_helper(fixture_http_client):
    """Authentication helper for login operations"""
    return AuthHelper(fixture_http_client)


@pytest.fixture(scope="function")
def fixture_database_seeder(test_run_id):
    """Single fixture that seeds DB and does all cleanup after test."""
    manager = DatabaseSeeder(test_run_id)
    try:
        yield manager
    finally:
        manager.cleanup_all_registered_firebase()
        manager.cleanup_all_registered_tables()


@pytest.fixture(scope="session", autouse=True)
def cleanup_existing_test_users():
    """Clean up any existing test users before and after test session"""
    _cleanup_test_users_by_pattern()
    yield
    _cleanup_test_users_by_pattern()


def _cleanup_test_users_by_pattern():
    """Clean up users with test email patterns"""
    try:
        page = auth.list_users()

        test_user_patterns = [
            "integration_user_",
            "login_test_user_",
            "update_test_user_",
            "multi_user_",
            "admin_user_",
            "regular_user_",
            "@test.com",
        ]

        users_to_delete = []
        for user in page.users:
            if user.email and any(
                pattern in user.email for pattern in test_user_patterns
            ):
                users_to_delete.append(user.uid)

        for user_id in users_to_delete:
            try:
                auth.delete_user(user_id)
                firebase_db.get_sync_client().collection(
                    "all_user_profiles"
                ).document(user_id).delete()
                firebase_db.get_sync_client().collection(
                    "firebase_stripe_mappings"
                ).document(user_id).delete()
            except Exception as e:
                logger.warning(
                    f"Error during pre-cleanup of user {user_id}: {e}"
                )

        if users_to_delete:
            logger.info(
                f"Pre-cleanup: Removed {len(users_to_delete)} test users"
            )

    except Exception as e:
        logger.warning(f"Error during test user cleanup: {e}")
