from unittest.mock import MagicMock, patch

import pytest
import requests

import off_client


def fake_response(json_data, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = json_data
    return resp


def test_fetch_by_barcode_found():
    payload = {
        "status": "success",
        "product": {"product_name": "Nutella", "brands": "Ferrero", "ingredients_text": "sugar", "extra": "x"},
    }
    with patch("off_client.requests.get", return_value=fake_response(payload)):
        result = off_client.fetch_by_barcode("3017620422003")
    assert result["status"] == 1
    assert result["product"] == {"product_name": "Nutella", "brands": "Ferrero", "ingredients_text": "sugar"}


def test_fetch_by_barcode_uses_v36_url_and_auth():
    with patch("off_client.requests.get", return_value=fake_response({})) as get:
        off_client.fetch_by_barcode("3274080005003")
    assert get.call_args[0][0] == "https://world.openfoodfacts.net/api/v3.6/product/3274080005003.json"
    assert get.call_args[1]["auth"] == ("off", "off")


def test_fetch_by_barcode_not_found():
    with patch("off_client.requests.get", return_value=fake_response({"status": "failure"}, 404)):
        assert off_client.fetch_by_barcode("000") == {"status": 0}


def test_fetch_by_barcode_network_error():
    with patch("off_client.requests.get", side_effect=requests.ConnectionError("boom")):
        with pytest.raises(off_client.OFFError):
            off_client.fetch_by_barcode("123")


def test_search_by_name_found():
    payload = {"products": [{"product_name": "Oat Milk", "brands": "Oatly", "ingredients_text": "oats"}]}
    with patch("off_client.requests.get", return_value=fake_response(payload)):
        result = off_client.search_by_name("oat milk")
    assert result["status"] == 1
    assert result["product"]["brands"] == "Oatly"


def test_search_by_name_empty():
    with patch("off_client.requests.get", return_value=fake_response({"products": []})):
        assert off_client.search_by_name("zzzz") == {"status": 0}


def test_search_by_name_network_error():
    with patch("off_client.requests.get", side_effect=requests.Timeout("slow")):
        with pytest.raises(off_client.OFFError):
            off_client.search_by_name("milk")
