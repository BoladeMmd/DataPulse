
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    country: str = Field(min_length=2, max_length=2)
    merchant: str = Field(min_length=1, max_length=100)
    transaction_type: str = Field(min_length=1, max_length=30)


class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    country: str
    merchant: str
    transaction_type: str
    created_at: datetime

    # Champs de scoring
    risk_score: int | None = None
    risk_level: str | None = None
    risk_reasons: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)


class TransactionScoreResponse(BaseModel):
    risk_score: int
    risk_level: str
    reasons: list[str]
