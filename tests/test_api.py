from unittest.mock import patch

import pytest

import data
import off_client
from app import app


@pytest.fixture(autouse=True)
def fresh_data():
    data.reset()


@pytest.fixture
def client():
    return app.test_client()


def test_get_all(client):
    resp = client.get("/inventory")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 3


def test_get_one(client):
    resp = client.get("/inventory/1")
    assert resp.status_code == 200
    assert resp.get_json()["product"]["product_name"] == "Coca-Cola"


def test_get_one_not_found(client):
    assert client.get("/inventory/999").status_code == 404


def test_post_adds_item(client):
    body = {"product_name": "Oat Milk", "brands": "Oatly", "price": 2.5, "stock": 10}
    resp = client.post("/inventory", json=body)
    assert resp.status_code == 201
    assert resp.get_json()["id"] == 4
    assert len(data.inventory) == 4


def test_post_missing_name(client):
    assert client.post("/inventory", json={"price": 1}).status_code == 400


def test_post_bad_price(client):
    resp = client.post("/inventory", json={"product_name": "X", "price": -5})
    assert resp.status_code == 400


def test_post_not_json(client):
    assert client.post("/inventory", data="hello").status_code == 400


def test_post_enriches_from_barcode(client):
    fake = {"status": 1, "product": {"product_name": "Fake Cola", "brands": "FakeCo", "ingredients_text": "water"}}
    with patch("off_client.fetch_by_barcode", return_value=fake):
        resp = client.post("/inventory", json={"barcode": "123", "price": 1, "stock": 1})
    assert resp.status_code == 201
    assert resp.get_json()["product"]["product_name"] == "Fake Cola"


def test_post_api_failure_without_name(client):
    with patch("off_client.fetch_by_barcode", side_effect=off_client.OFFError("down")):
        resp = client.post("/inventory", json={"barcode": "123"})
    assert resp.status_code == 502


def test_patch_updates_price_and_stock(client):
    resp = client.patch("/inventory/1", json={"price": 9.99, "stock": 5})
    assert resp.status_code == 200
    assert data.inventory[0]["price"] == 9.99
    assert data.inventory[0]["stock"] == 5


def test_patch_not_found(client):
    assert client.patch("/inventory/999", json={"price": 1}).status_code == 404


def test_patch_bad_stock(client):
    assert client.patch("/inventory/1", json={"stock": "lots"}).status_code == 400


def test_delete(client):
    assert client.delete("/inventory/1").status_code == 200
    assert len(data.inventory) == 2
    assert client.get("/inventory/1").status_code == 404


def test_delete_not_found(client):
    assert client.delete("/inventory/999").status_code == 404


def test_lookup_requires_query(client):
    assert client.get("/lookup").status_code == 400


def test_lookup_by_barcode(client):
    fake = {"status": 1, "product": {"product_name": "A", "brands": "B", "ingredients_text": "C"}}
    with patch("off_client.fetch_by_barcode", return_value=fake):
        resp = client.get("/lookup?barcode=123")
    assert resp.status_code == 200
    assert resp.get_json()["product"]["product_name"] == "A"


def test_lookup_not_found(client):
    with patch("off_client.search_by_name", return_value={"status": 0}):
        assert client.get("/lookup?name=zzz").status_code == 404


def test_lookup_api_down(client):
    with patch("off_client.search_by_name", side_effect=off_client.OFFError("down")):
        assert client.get("/lookup?name=milk").status_code == 502
