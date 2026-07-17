from fastapi import FastAPI

from app.main import app


def test_app_imports_as_fastapi_instance():
    assert isinstance(app, FastAPI)
    assert app.title == "app-finanzas-api"


def test_health_endpoint_is_registered_under_api_prefix():
    paths = {route.path for route in app.routes}

    assert "/api/v1/health" in paths
    assert "/health" in paths
