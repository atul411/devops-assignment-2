import os
import pytest
from app import create_app
from app.config import TestConfig

# Tests log in as admin/admin; pin the seed password so the seeded admin user has it.
os.environ.setdefault("ADMIN_INITIAL_PASSWORD", "admin")


@pytest.fixture
def app_v3(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"

    class Cfg(TestConfig):
        DATABASE = str(db_file)
        FEATURE_LEVEL = 3

    monkeypatch.setenv("FLASK_TESTING", "1")
    app = create_app(Cfg)
    yield app


@pytest.fixture
def app_v2(tmp_path):
    db_file = tmp_path / "test_v2.db"

    class Cfg(TestConfig):
        DATABASE = str(db_file)
        FEATURE_LEVEL = 2

    return create_app(Cfg)


@pytest.fixture
def app_v1(tmp_path):
    db_file = tmp_path / "test_v1.db"

    class Cfg(TestConfig):
        DATABASE = str(db_file)
        FEATURE_LEVEL = 1

    return create_app(Cfg)


@pytest.fixture
def client(app_v3):
    return app_v3.test_client()


@pytest.fixture
def client_v1(app_v1):
    return app_v1.test_client()


@pytest.fixture
def client_v2(app_v2):
    return app_v2.test_client()


@pytest.fixture
def auth_client(client):
    resp = client.post(
        "/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert resp.status_code in (200, 302)
    return client


@pytest.fixture
def seeded_client(auth_client):
    auth_client.post(
        "/clients/",
        json={"name": "Ravi", "age": 28, "weight": 75.0, "program": "MG"},
    )
    return auth_client
