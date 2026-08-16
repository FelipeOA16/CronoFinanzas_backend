from fastapi import FastAPI

from app.main import app


def test_app_imports_as_fastapi_instance():
    assert isinstance(app, FastAPI)
    assert app.title == "app-finanzas-api"


def test_health_endpoint_is_registered_under_api_prefix():
    documented_paths = set(app.openapi()["paths"])
    direct_paths = {
        route.path
        for route in app.routes
        if isinstance(getattr(route, "path", None), str)
    }

    assert "/api/v1/health" in documented_paths
    assert "/health" in direct_paths
