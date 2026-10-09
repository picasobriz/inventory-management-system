import requests


class OFFError(Exception):
    pass


def _clean_product(raw_product):
    if not isinstance(raw_product, dict):
        return {}
    
    cleaned = {}
    for key in ("product_name", "brands", "ingredients_text"):
        if key in raw_product:
            cleaned[key] = raw_product[key]
    return cleaned


def fetch_by_barcode(barcode):
    url = f"https://world.openfoodfacts.net/api/v3.6/product/{barcode}.json"
    headers = {"User-Agent": "InventoryApp - Version 1.0"}

    try:
        response = requests.get(url, headers=headers, auth=("off", "off"), timeout=5)
    except (requests.ConnectionError, requests.Timeout, requests.RequestException) as err:
        raise OFFError(f"Network error fetching barcode {barcode}: {err}") from err

    if response.status_code != 200:
        return {"status": 0}

    data = response.json()
    if not data or data.get("status") in (0, "failure"):
        return {"status": 0}

    raw_product = data.get("product", {})
    return {
        "status": 1,
        "product": _clean_product(raw_product)
    }


def search_by_name(name):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {"search_terms": name, "json": 1}
    headers = {"User-Agent": "InventoryApp - Version 1.0"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
    except (requests.ConnectionError, requests.Timeout, requests.RequestException) as err:
        raise OFFError(f"Network error searching for '{name}': {err}") from err

    if response.status_code != 200:
        return {"status": 0}

    data = response.json()
    products = data.get("products", [])
    if not products:
        return {"status": 0}

    first_product = products[0]
    return {
        "status": 1,
        "product": _clean_product(first_product)
    }