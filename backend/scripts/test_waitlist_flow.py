from __future__ import annotations

import json
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_database
from app.database import Base
from app.main import app
from app.models.waitlist import WaitlistEntry

TEST_DB_URL = "sqlite:///./waitlist_test.db"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def override_db() -> Generator:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def override_get_database() -> Generator:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def log_step(step: str, payload: dict | None = None) -> None:
    message = {"step": step}
    if payload is not None:
        message["data"] = payload
    print(json.dumps(message, indent=2))


def run_waitlist_flow() -> None:
    app.dependency_overrides[get_database] = override_get_database

    with override_db():
        with TestClient(app, raise_server_exceptions=False) as client:
            test_email = f"waitlist-{uuid.uuid4().hex}@example.com"
            metadata = {"source": "script", "campaign": "go-cart-ci"}

            log_step("join_waitlist.request", {"email": test_email})
            response = client.post(
                "/api/v1/waitlist/",
                json={"email": test_email, "metadata": metadata},
            )
            log_step("join_waitlist.response", response.json())
            response.raise_for_status()

            duplicate = client.post(
                "/api/v1/waitlist/",
                json={"email": test_email},
            )
            log_step(
                "join_waitlist.duplicate",
                {"status": duplicate.status_code, "body": duplicate.json()},
            )

            session = TestingSessionLocal()
            try:
                entry = session.query(WaitlistEntry).filter_by(email=test_email).first()
                assert entry is not None, "Waitlist entry was not persisted"
                token = entry.verification_token
            finally:
                session.close()

            log_step("verify.request", {"token": token})
            verify = client.post(
                "/api/v1/waitlist/verify",
                json={"token": token},
            )
            log_step("verify.response", verify.json())
            verify.raise_for_status()

            status = client.get(
                "/api/v1/waitlist/status",
                params={"email": test_email},
            )
            log_step("status.response", status.json())
            status.raise_for_status()

            log_step("flow.complete", {"email": test_email})


if __name__ == "__main__":
    run_waitlist_flow()
