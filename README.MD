# Inventory Manager

A simple inventory management system for a small retail company.

- **Flask REST API** with full CRUD (data is kept in a Python list, see `data.py`)
- **OpenFoodFacts integration** (API v3.6, `world.openfoodfacts.net`, login `off`/`off`) to look up products by barcode or name and fill in missing details
- **CLI** to use the API from the terminal
- **Unit tests** (pytest) for the API, the CLI and the OpenFoodFacts client

## Project structure

```
app.py            Flask API
data.py           mock database (list of items + helpers)
off_client.py     OpenFoodFacts API client
cli.py            command line interface
tests/            unit tests
docs/route-plan.md  planned routes, inputs/outputs
```

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the API

```bash
python app.py
```

It runs at http://127.0.0.1:5000.

## Use the CLI (in a second terminal)

```bash
python cli.py list
python cli.py view 1
python cli.py add --name "Oat Milk" --brand Oatly --price 2.5 --stock 10
python cli.py add --barcode 3017620422003 --price 4.2 --stock 15   # details come from OpenFoodFacts
python cli.py update 1 --price 1.75 --stock 30
python cli.py delete 2
python cli.py find --barcode 3274080005003
python cli.py find --name "almond milk"
```

## API endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/inventory` | all items |
| GET | `/inventory/<id>` | one item |
| POST | `/inventory` | add item |
| PATCH | `/inventory/<id>` | update item |
| DELETE | `/inventory/<id>` | delete item |
| GET | `/lookup?barcode=...` or `?name=...` | search OpenFoodFacts |

See `docs/route-plan.md` for inputs, outputs and error codes.

## Run the tests

```bash
pytest
```

The tests mock all network calls, so they work offline.

## Notes
- Data is stored in memory, so changes reset when the server restarts.
- If OpenFoodFacts is unreachable, the API returns a clear error (or still adds the item if you gave a name).
