from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.models.schema import Base

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    if "sqlite" in settings.DATABASE_URL:
        with engine.connect() as conn:
            for col, col_type in [
                ("evidence_ref", "VARCHAR(50)"),
                ("confidence", "VARCHAR(5) DEFAULT 'M'"),
                ("conflict_id", "VARCHAR(50)")
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE claims ADD COLUMN {col} {col_type}"))
                    conn.commit()
                except Exception:
                    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
