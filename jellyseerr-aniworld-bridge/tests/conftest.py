import os
import pytest

@pytest.fixture(autouse=True)
def set_test_environment_variables():
    """Set dummy environment variables for tests."""
    os.environ["JELLYSEERR_URL"] = "http://localhost:5055"
    os.environ["JELLYSEERR_API_KEY"] = "test_key"
    yield
    del os.environ["JELLYSEERR_URL"]
    del os.environ["JELLYSEERR_API_KEY"]
