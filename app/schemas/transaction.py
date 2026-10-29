
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TransactionCreate(BaseModel):
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    country: str = Field(
        min_length=2,
        max_length=2,
        pattern=r"^[A-Z]{2}$",
    )
    merchant: str = Field(
        min_length=1,
        max_length=100,
    )
    transaction_type: str = Field(
        min_length=1,
        max_length=30,
    )

    @field_validator("country", mode="before")
    @classmethod
    def normalize_country(cls, value):
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("merchant", "transaction_type", mode="before")
    @classmethod
    def strip_text_fields(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    country: str
    merchant: str
    transaction_type: str
    created_at: datetime
    risk_score: int | None = None
    risk_level: str | None = None
    risk_reasons: list[str] | None = None

    model_config = ConfigDict(from_attributes=True)


class TransactionScoreResponse(BaseModel):
    risk_score: int
    risk_level: str
    reasons: list[str]
