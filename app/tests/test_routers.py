from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.api.routers import get_session
import os


if os.path.exists("./test.db"):
    os.remove("./test.db")

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_session] = override_get_session


client = TestClient(app)


def test_create_worker():
    response = client.post(
        "/workers",
        json={"id": 1, "name": "Bob"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Bob"
    worker_id = data["id"]

    response = client.get(f"/workers/{worker_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == worker_id
    assert data["name"] == "Bob"


def test_delete_worker():
    client.post(
        "/workers",
        json={"id": 1, "name": "Bob"},
    )
    client.delete("workers/1")
    response = client.get("/workers/1")
    assert response.status_code == 404, response.text


def test_create_worker_shift():
    client.post(
        "/workers",
        json={"id": 1, "name": "Bob"},
    )
    response = client.post(
        "/shifts",
        json={"worker_id": 1, "slot": 1, "date": "2020-10-10"},
    )
    assert response.status_code == 201, response.text
    response = client.get("/shifts/worker/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data[0]["date"] == "2020-10-10"
    assert data[0]["slot"] == 1


def test_no_two_shifts_on_same_day():
    client.post(
        "/workers",
        json={"id": 1, "name": "Bob"},
    )
    client.post(
        "/shifts",
        json={"worker_id": 1, "slot": 1, "date": "2020-01-10"},
    )
    response = client.post(
        "/shifts",
        json={"worker_id": 1, "slot": 2, "date": "2020-01-10"},
    )
    assert response.status_code == 400, response.text
    assert response.text == '{"detail":"Worker already has a shift for 2020-01-10"}'


def test_no_consecutive_shifts_on_previous_day():
    client.post(
        "/workers",
        json={"id": 1, "name": "Bob"},
    )
    client.post(
        "/shifts",
        json={"worker_id": 1, "slot": 3, "date": "2020-02-10"},
    )
    response = client.post(
        "/shifts",
        json={"worker_id": 1, "slot": 1, "date": "2020-02-11"},
    )
    assert response.status_code == 400, response.text
    assert (
        response.text
        == '{"detail":"Worker has a shift on the previous day from 16 to 24, leading to two consecutive shifts"}'
    )


def test_no_consecutive_shifts_on_next_day():
    client.post(
        "/workers",
        json={"id": 1, "name": "Bob"},
    )
    client.post(
        "/shifts",
        json={"worker_id": 1, "slot": 1, "date": "2020-03-10"},
    )
    response = client.post(
        "/shifts",
        json={"worker_id": 1, "slot": 3, "date": "2020-03-09"},
    )
    assert response.status_code == 400, response.text
    assert (
        response.text
        == '{"detail":"Worker has a shift on the next day from 0 to 8, leading to two consecutive shifts"}'
    )
