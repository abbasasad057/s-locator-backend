from .fixtures.test_utils import create_parametrized_test
from .fixtures.test_generator import ConfigDrivenTest, Prerequisites, Endpoint
from all_types.request_dtypes import ReqIntelligenceData


# Catalog tests for comprehensive save catalog endpoint testing
CATALOG_MANAGEMENT_TESTS = [
    ConfigDrivenTest(
        name="test_viewport_population",
        description="Test viewport population with various catalog items",
        prerequisites=Prerequisites(
            requires_user=True,
            requires_auth=True,
            requires_database_seed=True,
            geospatial_seeds=True,
            user_type="admin",
            firebase_profile_seeds=["admin_profile_with_datasets"]
        ),
        endpoint=Endpoint(method="POST", path="/fetch_population_by_viewport"),
        input_data={
                "message": "",
                "request_info": {"request_id": ""},
                "request_body": ReqIntelligenceData(
                    top_lng=46.6500301,
                    top_lat=24.760447,
                    bottom_lng=46.632883,
                    bottom_lat=24.7314723,
                    zoom_level=12,
                    user_id="${user.user_id}",
                    population=True,
                    income=False
                ).model_dump()
        },
        expected_output_file="expected_responses/test_population_only_viewport.json"
    ),


]


# Create the parametrized test using the utility function
test_catalog_management = create_parametrized_test(CATALOG_MANAGEMENT_TESTS)
