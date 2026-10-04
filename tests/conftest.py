
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module  


@pytest.fixture

def client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DATA_FILE", str(tmp_path / "data" / "inventory.json"))
    app_module.app.config["TESTING"] = True
    app_module.reset_data()
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def auth_client(client):
    response = client.post("/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return client