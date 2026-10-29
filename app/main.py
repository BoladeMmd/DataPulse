from app.schemas.transaction import TransactionScoreResponse
from app.services.scoring import score_transaction
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.db.session import Base, engine
from app.models.transaction import Transaction

from app.db.session import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionScoreResponse,
)

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


@app.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
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
        return transaction
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'enregistrement de la transaction.",
        ) from exc


@app.get(
    "/transactions",
    response_model=list[TransactionResponse],
    tags=["Transactions"],
)
def list_transactions(db: Session = Depends(get_db)):
    statement = (
        select(Transaction)
        .order_by(Transaction.id.desc())
    )
    return db.scalars(statement).all()


@app.post(
    "/transactions/score",
    response_model=TransactionScoreResponse,
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

