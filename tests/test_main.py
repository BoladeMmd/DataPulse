
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

def test_reject_zero_amount():
    response = client.post(
        "/transactions/score",
        json={
            "amount": 0,
            "country": "SN",
            "merchant": "Boutique Dakar",
            "transaction_type": "payment",
        },
    )
    assert response.status_code == 422


def test_reject_negative_amount():
    response = client.post(
        "/transactions/score",
        json={
            "amount": -100,
            "country": "SN",
            "merchant": "Boutique Dakar",
            "transaction_type": "payment",
        },
    )
    assert response.status_code == 422


def test_reject_invalid_country():
    response = client.post(
        "/transactions/score",
        json={
            "amount": 1000,
            "country": "123",
            "merchant": "Boutique Dakar",
            "transaction_type": "payment",
        },
    )
    assert response.status_code == 422


def test_reject_blank_merchant():
    response = client.post(
        "/transactions/score",
        json={
            "amount": 1000,
            "country": "SN",
            "merchant": "   ",
            "transaction_type": "payment",
        },
    )
    assert response.status_code == 422


def test_reject_blank_transaction_type():
    response = client.post(
        "/transactions/score",
        json={
            "amount": 1000,
            "country": "SN",
            "merchant": "Boutique Dakar",
            "transaction_type": "   ",
        },
    )
    assert response.status_code == 422




from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.db.session import get_db


def test_transaction_database_error_returns_503():
    mock_db = MagicMock()
    mock_db.commit.side_effect = SQLAlchemyError("Database failure")

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            response = test_client.post(
                "/transactions",
                json={
                    "amount": 250000,
                    "country": "SN",
                    "merchant": "Supermarche Dakar",
                    "transaction_type": "payment",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert "indisponible" in response.json()["detail"].lower()
    mock_db.rollback.assert_called_once()


