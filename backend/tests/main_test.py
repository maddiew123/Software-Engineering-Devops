from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_app_exists():
    """Ensure FastAPI app is created."""
    assert app is not None

def test_app_docs_available():
    """FastAPI automatically provides docs."""
    response = client.get("/docs")

    assert response.status_code == 200


def test_openapi_schema():
    """Check OpenAPI schema endpoint."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "paths" in response.json()