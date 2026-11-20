import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models  # noqa: F401  (реєструє таблиці в Base)
from database import Base, get_db
from main import app


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def register_and_login(client, name="alice"):
    r = client.post("/auth/register", json={"username": name, "email": f"{name}@x.com", "password": "secret123"})
    assert r.status_code == 201, r.text
    r = client.post("/auth/login", data={"username": name, "password": "secret123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_duplicate_registration_is_409(client):
    register_and_login(client)
    r = client.post("/auth/register", json={"username": "ALICE", "email": "new@x.com", "password": "secret123"})
    assert r.status_code == 409


def test_book_crud_and_ownership(client):
    alice, bob = register_and_login(client, "alice"), register_and_login(client, "bobby")

    r = client.post("/books/", json={"title": "Кобзар", "author": "Шевченко", "genre": "Поезія", "rating": 5}, headers=alice)
    assert r.status_code == 201
    book_id = r.json()["id"]

    assert client.patch(f"/books/{book_id}", json={"rating": 4}, headers=bob).status_code == 403
    assert client.patch(f"/books/{book_id}", json={"rating": 4}, headers=alice).json()["rating"] == 4
    assert client.delete(f"/books/{book_id}", headers=bob).status_code == 403
    assert client.delete(f"/books/{book_id}", headers=alice).status_code == 204
    assert client.get(f"/books/{book_id}").status_code == 404


def test_search_filter_and_pagination(client):
    h = register_and_login(client)
    for i in range(15):
        client.post("/books/", json={"title": f"Книга {i}", "author": "Автор", "genre": "Роман"}, headers=h)
    client.post("/books/", json={"title": "Зайва", "author": "Інший", "genre": "Поезія"}, headers=h)

    page = client.get("/books/", params={"size": 10}).json()
    assert page["total"] == 16 and len(page["items"]) == 10 and page["pages"] == 2
    assert client.get("/books/", params={"q": "зайва"}).json()["total"] == 1
    assert client.get("/books/", params={"genre": "поезія"}).json()["total"] == 1
    assert client.get("/books/my", headers=h).json()["total"] == 16
    assert client.get("/books/my").status_code == 401
