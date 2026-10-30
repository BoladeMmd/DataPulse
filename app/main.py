
import logging
import secrets
from contextlib import asynccontextmanager

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    status,
)
from fastapi.security import APIKeyHeader
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import Base, engine, get_db, settings
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionScoreResponse,
)
from app.services.scoring import score_transaction


logger = logging.getLogger(__name__)


# =========================
# Cycle de vie de l'application
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="DataPulse API",
    description="API d'analyse et de scoring des transactions.",
    version="0.1.0",
    lifespan=lifespan,
)


# =========================
# Configuration API Key
# =========================

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


def verify_api_key(
    api_key: str = Depends(api_key_header),
):
    if not api_key or not secrets.compare_digest(
        api_key,
        settings.api_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou manquante",
        )


# =========================
# Monitoring Prometheus
# =========================

Instrumentator().instrument(app).expose(app)


# =========================
# Routes publiques
# =========================

@app.get("/", tags=["Accueil"])
def home():
    return {
        "message": "Bienvenue sur DataPulse API",
        "version": "0.1.0",
    }


@app.get("/health", tags=["Santé"])
def health_check():
    return {
        "status": "healthy",
        "service": "DataPulse API",
    }


# =========================
# Routes protégées
# =========================

@app.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
    tags=["Transactions"],
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
):
    result = score_transaction(
        amount=transaction_data.amount,
        country=transaction_data.country,
        transaction_type=transaction_data.transaction_type,
    )

    transaction = Transaction(
        **transaction_data.model_dump(),
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        risk_reasons=result["reasons"],
    )

    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

    except SQLAlchemyError:
        db.rollback()

        logger.exception(
            "Échec de l'enregistrement d'une transaction"
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Service temporairement indisponible. "
                "Veuillez réessayer plus tard."
            ),
        )

    return transaction


@app.get(
    "/transactions",
    response_model=list[TransactionResponse],
    dependencies=[Depends(verify_api_key)],
    tags=["Transactions"],
)
def list_transactions(
    db: Session = Depends(get_db),
):
    statement = (
        select(Transaction)
        .order_by(Transaction.id.desc())
    )

    return db.scalars(statement).all()


@app.post(
    "/transactions/score",
    response_model=TransactionScoreResponse,
    dependencies=[Depends(verify_api_key)],
    tags=["Scoring"],
)
def score_transaction_endpoint(
    transaction_data: TransactionCreate,
):
    result = score_transaction(
        amount=transaction_data.amount,
        country=transaction_data.country,
        transaction_type=transaction_data.transaction_type,
    )

    return result
