import pytest
import json
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_json(client):
    response = client.get("/health")
    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert data["service"] == "qrcode-generator"


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_returns_html(client):
    response = client.get("/")
    assert b"QR Code Generator" in response.data


# ---------------------------------------------------------------------------
# Generate — happy path
# ---------------------------------------------------------------------------

def test_generate_returns_png(client):
    response = client.post(
        "/generate",
        json={"data": "https://example.com"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "image/png"


def test_generate_with_custom_size(client):
    response = client.post(
        "/generate",
        json={"data": "https://example.com", "size": 5},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "image/png"


def test_generate_with_custom_border(client):
    response = client.post(
        "/generate",
        json={"data": "https://example.com", "border": 2},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "image/png"


def test_generate_plain_text(client):
    response = client.post(
        "/generate",
        json={"data": "Hello, World!"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.content_type == "image/png"


# ---------------------------------------------------------------------------
# Generate — validation errors
# ---------------------------------------------------------------------------

def test_generate_missing_data_field(client):
    response = client.post(
        "/generate",
        json={"size": 10},
        content_type="application/json",
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_generate_empty_data(client):
    response = client.post(
        "/generate",
        json={"data": "   "},
        content_type="application/json",
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_generate_no_body(client):
    response = client.post("/generate", content_type="application/json")
    assert response.status_code == 400


def test_generate_size_too_large(client):
    response = client.post(
        "/generate",
        json={"data": "test", "size": 999},
        content_type="application/json",
    )
    assert response.status_code == 400


def test_generate_size_too_small(client):
    response = client.post(
        "/generate",
        json={"data": "test", "size": 0},
        content_type="application/json",
    )
    assert response.status_code == 400


def test_generate_border_too_large(client):
    response = client.post(
        "/generate",
        json={"data": "test", "border": 99},
        content_type="application/json",
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

def test_404_returns_json(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data


def test_get_to_generate_not_allowed(client):
    response = client.get("/generate")
    assert response.status_code in (404, 405)