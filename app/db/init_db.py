
from app.db.session import Base, engine
from app.models.transaction import Transaction  # noqa: F401

Base.metadata.create_all(bind=engine)

print("Tables DataPulse créées avec succès.")
