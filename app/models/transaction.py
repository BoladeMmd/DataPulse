
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )

    merchant: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Informations de scoring
    risk_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    risk_level: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    risk_reasons: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
    )
