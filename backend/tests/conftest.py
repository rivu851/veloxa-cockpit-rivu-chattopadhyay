import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models.schema import Base
from backend.app.services.ingest import seed_day1_data, seed_day2_data
from backend.app.db import session as db_session
from backend.app.db.session import get_db
from backend.app.main import app

TEST_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_veloxa_isolated.db"))
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Rebind session module's engine and SessionLocal so all direct imports use test_engine
db_session.engine = test_engine
db_session.SessionLocal = TestSessionLocal

@pytest.fixture(scope="session", autouse=True)
def setup_isolated_test_database():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    seed_day1_data(db)
    seed_day2_data(db)
    db.close()

    def override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    test_engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
