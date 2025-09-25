# tests/integration/fixtures/test_utils.py
import pytest
from .test_generator import ConfigTestGenerator

def create_parametrized_test(test_configs):
    """Factory function to create a parametrized test function"""

    @pytest.mark.parametrize("test_config", test_configs, ids=lambda config: config.name)
    def test_function(test_config, fixture_http_client, fixture_user_seeder, fixture_auth_helper, fixture_database_seeder):
        # Directly execute the test here, combining both functions
        generator = ConfigTestGenerator(
            fixture_instance_http_client=fixture_http_client, 
            fixture_instance_user_seeder=fixture_user_seeder, 
            fixture_instance_auth_helper=fixture_auth_helper,
            fixture_instance_database_seeder=fixture_database_seeder
        )
        success = generator.execute_test(test_config)
        assert success, f"Configuration-driven test failed: {test_config.name}"

    return test_function