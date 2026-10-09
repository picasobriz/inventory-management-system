import sys
import os
import argparse
import requests

HOST = os.getenv("API_HOST", "127.0.0.1")
PORT = os.getenv("API_PORT", "5000")
BASE_ENDPOINT = f"http://{HOST}:{PORT}"


def safe_request(method, path, **kwargs):
    url = f"{BASE_ENDPOINT}{path}"
    try:
        response = requests.request(method, url, **kwargs)
        if response.status_code >= 400:
            try:
                err_data = response.json()
                if "error" in err_data:
                    print(f"Error: {err_data['error']}")
                else:
                    print(response.text)
            except Exception:
                print(response.text)
            return 1

        try:
            print(response.json())
        except Exception:
            print(response.text)
        return 0

    except requests.RequestException:
        print("Error: cannot connect to API server.")
        return 1


def interactive_menu():
    while True:
        print("\n" + "=" * 35)
        print("    INVENTORY MANAGEMENT MENU    ")
        print("=" * 35)
        print("1. View All Items")
        print("2. View One Item")
        print("3. Add Item")
        print("4. Update Item")
        print("5. Delete Item")
        print("6. Find Product")
        print("7. Exit")
        print("=" * 35)

        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            safe_request("GET", "/inventory")
        elif choice == "2":
            item_id = input("Enter Item ID: ").strip()
            safe_request("GET", f"/inventory/{item_id}")
        elif choice == "3":
            name = input("Enter Product Name: ").strip()
            price = float(input("Enter Price: ").strip() or 0)
            stock = int(input("Enter Stock Quantity: ").strip() or 0)
            barcode = input("Enter Barcode (optional): ").strip()
            payload = {"product_name": name, "price": price, "stock": stock}
            if barcode:
                payload["barcode"] = barcode
            safe_request("POST", "/inventory", json=payload)
        elif choice == "4":
            item_id = input("Enter Item ID to update: ").strip()
            price_input = input("Enter New Price (leave blank to skip): ").strip()
            stock_input = input("Enter New Stock Quantity (leave blank to skip): ").strip()
            name_input = input("Enter New Product Name (leave blank to skip): ").strip()

            payload = {}
            if price_input:
                payload["price"] = float(price_input)
            if stock_input:
                payload["stock"] = int(stock_input)
            if name_input:
                payload["product_name"] = name_input

            if not payload:
                print("Error: Must specify price, stock, or name field to update.")
            else:
                safe_request("PATCH", f"/inventory/{item_id}", json=payload)
        elif choice == "5":
            item_id = input("Enter Item ID to delete: ").strip()
            safe_request("DELETE", f"/inventory/{item_id}")
        elif choice == "6":
            barcode = input("Enter Barcode (leave blank to search by name): ").strip()
            params = {}
            if barcode:
                params["barcode"] = barcode
            else:
                name = input("Enter Product Name: ").strip()
                if name:
                    params["name"] = name

            if not params:
                print("Error: Must specify --barcode or --name.")
            else:
                safe_request("GET", "/lookup", params=params)
        elif choice == "7":
            print("Exiting application. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please choose a number between 1 and 7.")


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if not args:
        interactive_menu()
        return 0

    parser = argparse.ArgumentParser(description="Inventory Management CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list")

    view_parser = subparsers.add_parser("view")
    view_parser.add_argument("id", type=str)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--name", type=str, required=False)
    add_parser.add_argument("--price", type=float, required=False)
    add_parser.add_argument("--stock", type=int, required=False)
    add_parser.add_argument("--barcode", type=str, required=False)

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("id", type=str)
    update_parser.add_argument("--name", type=str, required=False)
    update_parser.add_argument("--price", type=float, required=False)
    update_parser.add_argument("--stock", type=int, required=False)

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("id", type=str)

    find_parser = subparsers.add_parser("find")
    find_parser.add_argument("--barcode", type=str, required=False)
    find_parser.add_argument("--name", type=str, required=False)

    parsed = parser.parse_args(args)

    if parsed.command == "list":
        return safe_request("GET", "/inventory")

    elif parsed.command == "view":
        return safe_request("GET", f"/inventory/{parsed.id}")

    elif parsed.command == "add":
        payload = {}
        if parsed.name is not None:
            payload["product_name"] = parsed.name
        if parsed.price is not None:
            payload["price"] = parsed.price
        if parsed.stock is not None:
            payload["stock"] = parsed.stock
        if parsed.barcode is not None:
            payload["barcode"] = parsed.barcode
        return safe_request("POST", "/inventory", json=payload)

    elif parsed.command == "update":
        payload = {}
        if parsed.name is not None:
            payload["product_name"] = parsed.name
        if parsed.price is not None:
            payload["price"] = parsed.price
        if parsed.stock is not None:
            payload["stock"] = parsed.stock

        if not payload:
            print("Error: Must specify price, stock, or name field to update.")
            return 1

        return safe_request("PATCH", f"/inventory/{parsed.id}", json=payload)

    elif parsed.command == "delete":
        return safe_request("DELETE", f"/inventory/{parsed.id}")

    elif parsed.command == "find":
        params = {}
        if parsed.barcode:
            params["barcode"] = parsed.barcode
        if parsed.name:
            params["name"] = parsed.name

        if not params:
            print("Error: Must specify --barcode or --name.")
            return 1

        return safe_request("GET", "/lookup", params=params)

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())