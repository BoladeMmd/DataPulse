
from decimal import Decimal

from app.services.scoring import score_transaction


def test_low_risk_transaction():
    result = score_transaction(
        amount=Decimal("5000"),
        country="SN",
        transaction_type="payment",
    )

    assert result["risk_score"] == 0
    assert result["risk_level"] == "low"


def test_high_risk_transaction():
    result = score_transaction(
        amount=Decimal("600000"),
        country="FR",
        transaction_type="transfer",
    )

    assert result["risk_score"] == 80
    assert result["risk_level"] == "high"
