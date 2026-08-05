"""Tests des règles métier critiques (voir docs/endpoints-biblioexchange.md).

Utilise une base SQLite en mémoire dédiée aux tests, injectée via
l'override de la dépendance get_db (ne touche jamais PostgreSQL).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _register_and_login(client, email, nom="Test"):
    client.post("/auth/register", json={"email": email, "password": "pass1234", "nom": nom})
    token = client.post("/auth/login", data={"username": email, "password": "pass1234"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _make_admin(client, email):
    with TestingSessionLocal() as db:
        from app.models.user import User, UserRole
        user = db.query(User).filter(User.email == email).first()
        user.role = UserRole.admin
        db.commit()
    return client.post("/auth/login", data={"username": email, "password": "pass1234"}).json()["access_token"]


def test_book_hidden_until_admin_validates(client):
    headers = _register_and_login(client, "a@test.com")
    client.post("/books", json={"titre": "Livre A", "auteur": "Auteur"}, headers=headers)
    assert client.get("/books").json() == []


def test_non_admin_cannot_validate_books(client):
    headers = _register_and_login(client, "a@test.com")
    book_id = client.post("/books", json={"titre": "Livre A", "auteur": "Auteur"}, headers=headers).json()["id"]
    response = client.patch(f"/admin/books/{book_id}/validate", headers=headers)
    assert response.status_code == 403


def test_cannot_propose_already_negotiated_book(client):
    headers_a = _register_and_login(client, "a@test.com")
    headers_b = _register_and_login(client, "b@test.com")
    token_admin = _make_admin(client, "a@test.com")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    book_a = client.post("/books", json={"titre": "A", "auteur": "X"}, headers=headers_a).json()["id"]
    book_b = client.post("/books", json={"titre": "B", "auteur": "X"}, headers=headers_b).json()["id"]
    book_c = client.post("/books", json={"titre": "C", "auteur": "X"}, headers=headers_b).json()["id"]
    for bid in (book_a, book_b, book_c):
        client.patch(f"/admin/books/{bid}/validate", headers=headers_admin)

    r = client.post("/exchanges", json={"book_offered_id": book_a, "book_requested_id": book_b}, headers=headers_admin)
    assert r.status_code == 201

    r = client.post("/exchanges", json={"book_offered_id": book_c, "book_requested_id": book_a}, headers=headers_b)
    assert r.status_code == 409


def test_suspended_user_is_blocked(client):
    headers = _register_and_login(client, "a@test.com")
    token_admin = _make_admin(client, "a@test.com")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    headers_c = _register_and_login(client, "c@test.com")
    with TestingSessionLocal() as db:
        from app.models.user import User
        target = db.query(User).filter(User.email == "c@test.com").first()
        user_id = str(target.id)

    r = client.patch(f"/admin/users/{user_id}/suspend", headers=headers_admin)
    assert r.status_code == 200

    r = client.post("/books", json={"titre": "X", "auteur": "Y"}, headers=headers_c)
    assert r.status_code == 403
