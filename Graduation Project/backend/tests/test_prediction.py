import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify /health returns HTTP 200 and {'status': 'ok'}."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_happy_path():
    """Verify valid 9-feature payload returns HTTP 200 and formatted price."""
    payload = {
        "location": "Whitefield",
        "carpet_area_sqft": 1200.0,
        "floor_num": 2,
        "bathroom": 2,
        "balcony": 1,
        "furnishing": "Semi-Furnished",
        "transaction": "Resale",
        "ownership": "Freehold",
        "facing": "East",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_price" in data
    assert isinstance(data["predicted_price"], (int, float))
    assert data["predicted_price"] > 0
    assert data.get("currency") == "INR"
    assert "formatted_price" in data


def test_predict_basement_floor():
    """Verify negative floor numbers (e.g. basement -1) are accepted and predicted."""
    payload = {
        "location": "Indiranagar",
        "carpet_area_sqft": 1500.0,
        "floor_num": -1,
        "bathroom": 2,
        "balcony": 0,
        "furnishing": "Furnished",
        "transaction": "Resale",
        "ownership": "Freehold",
        "facing": "North",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_price"] > 0


def test_predict_unseen_location_fallback():
    """Verify unseen location is accepted (mapped to 'other') and produces a valid prediction."""
    payload = {
        "location": "Some Unknown Village 999",
        "carpet_area_sqft": 950.0,
        "floor_num": 1,
        "bathroom": 1,
        "balcony": 1,
        "furnishing": "Unfurnished",
        "transaction": "New Property",
        "ownership": "Freehold",
        "facing": "North",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_price"] > 0


def test_predict_missing_required_fields():
    """Verify missing required fields triggers HTTP 422 Unprocessable Entity."""
    payload = {
        "location": "Whitefield",
        "bathroom": 2,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_invalid_negative_carpet_area():
    """Verify negative carpet area fails validation with HTTP 422."""
    payload = {
        "location": "Whitefield",
        "carpet_area_sqft": -250.0,
        "floor_num": 2,
        "bathroom": 2,
        "balcony": 1,
        "furnishing": "Furnished",
        "transaction": "Resale",
        "ownership": "Freehold",
        "facing": "East",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
