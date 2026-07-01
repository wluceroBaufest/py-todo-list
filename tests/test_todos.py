import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_create_todo(client):
    response = client.post("/todos/", json={"title": "Test todo"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test todo"
    assert data["description"] is None
    assert data["completed"] is False
    assert "id" in data


def test_create_todo_with_description(client):
    response = client.post(
        "/todos/", json={"title": "Test todo", "description": "A description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test todo"
    assert data["description"] == "A description"


def test_list_todos_empty(client):
    response = client.get("/todos/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_todos(client):
    client.post("/todos/", json={"title": "Todo 1"})
    client.post("/todos/", json={"title": "Todo 2"})
    response = client.get("/todos/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_todos_filter_completed(client):
    r1 = client.post("/todos/", json={"title": "Todo 1"})
    client.post("/todos/", json={"title": "Todo 2"})
    client.put(f"/todos/{r1.json()['id']}", json={"completed": True})

    response = client.get("/todos/?completed=true")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["completed"] is True

    response = client.get("/todos/?completed=false")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["completed"] is False


def test_get_todo(client):
    created = client.post("/todos/", json={"title": "Test todo"}).json()
    response = client.get(f"/todos/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["title"] == "Test todo"


def test_get_todo_not_found(client):
    response = client.get("/todos/999")
    assert response.status_code == 404


def test_update_todo(client):
    created = client.post("/todos/", json={"title": "Original"}).json()
    response = client.put(
        f"/todos/{created['id']}",
        json={"title": "Updated", "completed": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["completed"] is True


def test_update_todo_not_found(client):
    response = client.put("/todos/999", json={"title": "Updated"})
    assert response.status_code == 404


def test_delete_todo(client):
    created = client.post("/todos/", json={"title": "To delete"}).json()
    response = client.delete(f"/todos/{created['id']}")
    assert response.status_code == 204

    response = client.get(f"/todos/{created['id']}")
    assert response.status_code == 404


def test_delete_todo_not_found(client):
    response = client.delete("/todos/999")
    assert response.status_code == 404
