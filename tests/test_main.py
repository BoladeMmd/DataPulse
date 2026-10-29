
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Bienvenue sur DataPulse API",
        "version": "0.1.0",
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "DataPulse API",
    }


def test_score_transaction():
    response = client.post(
        "/transactions/score",
        json={
            "amount": 600000,
            "country": "FR",
            "merchant": "International Shop",
            "transaction_type": "transfer",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] == 80
    assert data["risk_level"] == "high"
