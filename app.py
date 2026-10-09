from flask import Flask, jsonify, request

import data
import off_client

app = Flask(__name__)


def error(message, code):
    return jsonify({"error": message}), code


def find_item(item_id):
    for item in data.inventory:
        if item["id"] == item_id:
            return item
    return None


def validate_price_stock(body):
    if "price" in body:
        p = body["price"]
        if isinstance(p, bool) or not isinstance(p, (int, float)) or p < 0:
            return "price must be a number >= 0"
    if "stock" in body:
        s = body["stock"]
        if isinstance(s, bool) or not isinstance(s, int) or s < 0:
            return "stock must be a whole number >= 0"
    return None


@app.route("/inventory", methods=["GET"])
def get_all():
    return jsonify(data.inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_one(item_id):
    item = find_item(item_id)
    if item is None:
        return error("Item not found", 404)
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return error("Request body must be JSON", 400)

    msg = validate_price_stock(body)
    if msg:
        return error(msg, 400)

    product = {
        "product_name": body.get("product_name", ""),
        "brands": body.get("brands", ""),
        "ingredients_text": body.get("ingredients_text", ""),
    }
    barcode = body.get("barcode", "")

    if barcode:
        try:
            result = off_client.fetch_by_barcode(barcode)
            if result["status"] == 1:
                for key, value in result["product"].items():
                    if not product.get(key):
                        product[key] = value
        except off_client.OFFError:
            if not product["product_name"]:
                return error("Could not reach OpenFoodFacts and no product_name given", 502)

    if not product["product_name"]:
        return error("product_name is required (or give a valid barcode)", 400)

    item = {
        "id": data.next_id(),
        "barcode": barcode,
        "price": body.get("price", 0),
        "stock": body.get("stock", 0),
        "status": 1,
        "product": product,
    }
    data.inventory.append(item)
    return jsonify(item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return error("Item not found", 404)

    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not body:
        return error("Request body must be JSON with fields to update", 400)

    msg = validate_price_stock(body)
    if msg:
        return error(msg, 400)

    for key in ("price", "stock", "barcode"):
        if key in body:
            item[key] = body[key]
    for key in ("product_name", "brands", "ingredients_text"):
        if key in body:
            item["product"][key] = body[key]
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return error("Item not found", 404)
    data.inventory.remove(item)
    return jsonify({"message": f"Item {item_id} deleted"}), 200


@app.route("/lookup", methods=["GET"])
def lookup():
    barcode = request.args.get("barcode")
    name = request.args.get("name")
    if not barcode and not name:
        return error("Provide a barcode or name query parameter", 400)
    try:
        result = (
            off_client.fetch_by_barcode(barcode)
            if barcode
            else off_client.search_by_name(name)
        )
    except off_client.OFFError as err:
        return error(str(err), 502)
    if result["status"] != 1:
        return error("Product not found on OpenFoodFacts", 404)
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)