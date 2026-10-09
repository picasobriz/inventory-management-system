from unittest.mock import MagicMock, patch

import requests

import cli


def fake_response(json_data, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = json_data
    return resp


def test_list_calls_get(capsys):
    with patch("cli.requests.request", return_value=fake_response([])) as req:
        assert cli.main(["list"]) == 0
    assert req.call_args[0][0] == "GET"
    assert req.call_args[0][1].endswith("/inventory")


def test_view_calls_get_with_id():
    with patch("cli.requests.request", return_value=fake_response({"id": 2})) as req:
        assert cli.main(["view", "2"]) == 0
    assert req.call_args[0][1].endswith("/inventory/2")


def test_add_sends_post_body():
    with patch("cli.requests.request", return_value=fake_response({"id": 4}, 201)) as req:
        code = cli.main(["add", "--name", "Oat Milk", "--price", "2.5", "--stock", "10"])
    assert code == 0
    assert req.call_args[0][0] == "POST"
    body = req.call_args[1]["json"]
    assert body["product_name"] == "Oat Milk"
    assert body["price"] == 2.5
    assert body["stock"] == 10


def test_update_sends_patch():
    with patch("cli.requests.request", return_value=fake_response({"id": 1})) as req:
        assert cli.main(["update", "1", "--price", "5"]) == 0
    assert req.call_args[0][0] == "PATCH"
    assert req.call_args[1]["json"] == {"price": 5.0}


def test_update_without_fields_fails(capsys):
    assert cli.main(["update", "1"]) == 1
    assert "price" in capsys.readouterr().out


def test_delete_sends_delete():
    with patch("cli.requests.request", return_value=fake_response({"message": "ok"})) as req:
        assert cli.main(["delete", "1"]) == 0
    assert req.call_args[0][0] == "DELETE"


def test_find_by_barcode():
    with patch("cli.requests.request", return_value=fake_response({"status": 1})) as req:
        assert cli.main(["find", "--barcode", "123"]) == 0
    assert req.call_args[1]["params"] == {"barcode": "123"}


def test_find_by_name():
    with patch("cli.requests.request", return_value=fake_response({"status": 1})) as req:
        assert cli.main(["find", "--name", "milk"]) == 0
    assert req.call_args[1]["params"] == {"name": "milk"}


def test_find_without_args_fails(capsys):
    assert cli.main(["find"]) == 1


def test_api_error_message_shown(capsys):
    with patch("cli.requests.request", return_value=fake_response({"error": "Item not found"}, 404)):
        assert cli.main(["view", "99"]) == 1
    assert "Item not found" in capsys.readouterr().out


def test_connection_error(capsys):
    with patch("cli.requests.request", side_effect=requests.ConnectionError()):
        assert cli.main(["list"]) == 1
    assert "cannot connect" in capsys.readouterr().out
