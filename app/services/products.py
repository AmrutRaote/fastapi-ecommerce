import json
from pathlib import Path
from typing import List, Dict

# Path to the JSON file where all product records are stored
DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"


def load_products() -> List[Dict]:
    """
    Reads and parses products from the JSON database file.
    Returns an empty list if the file does not exist yet.
    """
    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, 'r', encoding="utf-8") as file:
        return json.load(file)


def get_all_products() -> List[dict]:
    """Helper function to fetch all products."""
    return load_products()


def save_products(products: List[Dict]) -> None:
    """
    Saves the entire list of products back to the JSON file.
    Uses indent=2 for clean, human-readable formatting.
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)


def add_product(product: Dict) -> Dict:
    """
    Adds a new product to storage.
    Ensures SKU uniqueness across all existing products before saving.
    """
    products = get_all_products()

    # Reject if another product already uses this SKU
    if any(p["sku"] == product["sku"] for p in products):
        raise ValueError("SKU already exists")

    products.append(product)
    save_products(products)

    return product 


def remove_product(id: str) -> dict:
    """
    Deletes a product by its ID and returns the deleted record.
    Raises ValueError if the ID does not match any product.
    """
    products = get_all_products()  

    for idx, p in enumerate(products):
        if p["id"] == str(id):
            deleted = products.pop(idx)
            save_products(products)
            return {"message": "product deleted successfully", "data": deleted}

    raise ValueError("Product not found!")


def change_product(product_id: str, update_data: dict):
    """
    Updates fields of an existing product.
    - Skips fields that are None.
    - Deep-merges nested dictionaries (like dimensions_cm or seller).
    """
    products = get_all_products()  

    for index, product in enumerate(products):
        if product_id == product.get("id"):
            # Apply only the provided update fields
            for key, value in update_data.items():
                if value is None:
                    continue

                # If both are nested dicts (e.g. dimensions_cm), merge instead of overwrite
                if isinstance(value, dict) and isinstance(product.get(key), dict):
                    product[key].update(value)
                else:
                    product[key] = value 

            products[index] = product
            save_products(products)

            return product

    raise ValueError("Product not found!")
