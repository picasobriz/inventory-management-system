"""Mock database: a plain Python list that mimics OpenFoodFacts data.

Each item has an `id`, our own `price` and `stock`, and the OpenFoodFacts
style `status` + `product` fields.
"""

SEED_ITEMS = [
    {
        "id": 1,
        "barcode": "5449000000996",
        "price": 1.50,
        "stock": 40,
        "status": 1,
        "product": {
            "product_name": "Coca-Cola",
            "brands": "Coca-Cola",
            "ingredients_text": "Carbonated water, sugar, colour (caramel E150d), phosphoric acid, natural flavourings including caffeine",
        },
    },
    {
        "id": 2,
        "barcode": "3017620422003",
        "price": 4.20,
        "stock": 25,
        "status": 1,
        "product": {
            "product_name": "Nutella",
            "brands": "Ferrero",
            "ingredients_text": "Sugar, palm oil, hazelnuts, skimmed milk powder, cocoa, soy lecithin, vanillin",
        },
    },
    {
        "id": 3,
        "barcode": "0000000000001",
        "price": 3.99,
        "stock": 12,
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar, sea salt",
        },
    },
]

# The "database" the API reads and writes.
inventory = [dict(item, product=dict(item["product"])) for item in SEED_ITEMS]


def reset():
    """Put the array back to its starting state (used by the tests)."""
    inventory.clear()
    for item in SEED_ITEMS:
        inventory.append(dict(item, product=dict(item["product"])))


def next_id():
    """Return the next free ID."""
    return max((item["id"] for item in inventory), default=0) + 1
