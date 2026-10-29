
from decimal import Decimal


def score_transaction(
    amount: Decimal,
    country: str,
    transaction_type: str,
) -> dict:
    score = 0
    reasons = []

    # Règle 1 : montant élevé
    if amount >= Decimal("500000"):
        score += 50
        reasons.append("Montant très élevé")
    elif amount >= Decimal("100000"):
        score += 25
        reasons.append("Montant élevé")

    # Règle 2 : pays différent du Sénégal
    if country.upper() != "SN":
        score += 20
        reasons.append("Transaction hors Sénégal")

    # Règle 3 : type de transaction inhabituel
    if transaction_type.lower() in {"withdrawal", "transfer"}:
        score += 10
        reasons.append("Type de transaction à surveiller")

    score = min(score, 100)

    if score >= 50:
        risk_level = "high"
    elif score >= 25:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
    }
