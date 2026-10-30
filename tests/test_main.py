
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.db.session import get_db, settings


# ==========================================
# Configuration des tests
# ==========================================

client = TestClient(app)

TEST_API_KEY = settings.api_key
HEADERS = {
    "X-API-Key": TEST_API_KEY,
}


# ==========================================
# Tests des routes publiques
# ==========================================

def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Bienvenue sur DataPulse API"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ==========================================
# Tests des opérations sur les transactions
# ==========================================

def test_create_transaction():
    response = client.post(
        "/transactions",
        json={
            "amount": 75000,
            "country": "SN",
            "merchant": "Supermarche Dakar",
            "transaction_type": "payment",
        },
        headers=HEADERS,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == "75000.00"
    assert data["country"] == "SN"
    assert data["merchant"] == "Supermarche Dakar"
    assert data["risk_score"] == 0
    assert data["risk_level"] == "low"


def test_list_transactions():
    response = client.get(
        "/transactions",
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_score_transaction():
    response = client.post(
        "/transactions/score",
        json={
            "amount": 600000,
            "country": "FR",
            "merchant": "Amazon",
            "transaction_type": "transfer",
        },
        headers=HEADERS,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_score"] == 80
    assert data["risk_level"] == "high"


# ==========================================
# Tests de validation des données
# ==========================================

def test_reject_zero_amount():
    response = client.post(
        "/transactions",
        json={
            "amount": 0,
            "country": "SN",
            "merchant": "Supermarche Dakar",
            "transaction_type": "payment",
        },
        headers=HEADERS,
    )

    assert response.status_code == 422


def test_reject_negative_amount():
    response = client.post(
        "/transactions",
        json={
            "amount": -5000,
            "country": "SN",
            "merchant": "Supermarche Dakar",
            "transaction_type": "payment",
        },
        headers=HEADERS,
    )

    assert response.status_code == 422


def test_reject_invalid_country():
    response = client.post(
        "/transactions",
        json={
            "amount": 50000,
            "country": "SEN",
            "merchant": "Supermarche Dakar",
            "transaction_type": "payment",
        },
        headers=HEADERS,
    )

    assert response.status_code == 422


def test_reject_blank_merchant():
    response = client.post(
        "/transactions",
        json={
            "amount": 50000,
            "country": "SN",
            "merchant": "   ",
            "transaction_type": "payment",
        },
        headers=HEADERS,
    )

    assert response.status_code == 422


def test_reject_blank_transaction_type():
    response = client.post(
        "/transactions",
        json={
            "amount": 50000,
            "country": "SN",
            "merchant": "Supermarche Dakar",
            "transaction_type": "   ",
        },
        headers=HEADERS,
    )

    assert response.status_code == 422


# ==========================================
# Tests de sécurité API Key
# ==========================================

def test_reject_missing_api_key():
    response = client.get("/transactions")

    assert response.status_code == 401
    assert response.json()["detail"] == "Clé API invalide ou manquante"


def test_reject_invalid_api_key():
    response = client.get(
        "/transactions",
        headers={
            "X-API-Key": "wrong_test_key",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Clé API invalide ou manquante"


def test_accept_valid_api_key():
    response = client.get(
        "/transactions",
        headers=HEADERS,
    )

    assert response.status_code == 200


# ==========================================
# Test de gestion des erreurs PostgreSQL
# ==========================================

def test_transaction_database_error_returns_503():

    mock_db = MagicMock()

    mock_db.commit.side_effect = SQLAlchemyError(
        "Database failure"
    )

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
                headers=HEADERS,
            )

    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503

    assert (
        "indisponible"
        in response.json()["detail"].lower()
    )

    mock_db.rollback.assert_called_once()
