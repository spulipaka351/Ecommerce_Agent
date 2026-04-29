from langchain.tools import tool
from datetime import date
import database as db


@tool
def get_price(item_name: str) -> float:
    """
    Look up the current price of a single product.
    Use this when the user asks how much something costs or wants to know the price.
    Args:
        item_name: The product's full name (e.g. 'Laptop Pro 14') or SKU (e.g. 'ELEC-003').
    Returns the price as a float, or -1 if the product is not found.
    """
    product = db.get_product(item_name)
    return float(product["price"]) if product else -1


@tool
def get_inventory() -> str:
    """
    Retrieve the full list of all product names available in the store.
    Only call this tool when the user explicitly asks to see all products,
    the full inventory, or a complete list of items.
    Returns a comma-separated string of product names.
    """
    products = db.get_all_products()
    return ", ".join(p["name"] for p in products) if products else "No products found."


@tool
def apply_discount(item_name: str, discount_percentage: float) -> float:
    """
    Calculate the discounted price for a product given a percentage off.
    Use this when the user wants to know what a product would cost after a percentage discount.
    Args:
        item_name: The product's full name or SKU.
        discount_percentage: The percentage to discount, e.g. 20.0 for 20% off.
    Returns the discounted price as a float, or -1 if the product is not found.
    """
    product = db.get_product(item_name)
    if not product:
        return -1
    return round(float(product["price"]) * (1 - discount_percentage / 100), 2)


@tool
def check_low_stock(threshold: int = None) -> str:
    """
    Check which products are running low on stock.
    Use this when the user asks about stock levels, low inventory, or items needing reorder.
    Args:
        threshold: Optional integer. If provided, flags all items with stock below this number.
                   If not provided, each item's own reorder threshold is used instead.
    Returns a formatted report of all low-stock items, or a confirmation that all stock is healthy.
    """
    flagged = db.get_low_stock_products(threshold)
    if not flagged:
        return "✓ All items are above their stock thresholds."
    lines = [f"⚠ {len(flagged)} item(s) below threshold:"]
    for i in flagged:
        lines.append(
            f"  • [{i['sku']}] {i['name']} ({i['category']}): "
            f"{i['stock']} units (threshold: {i['threshold']}, {i['units_below']} below)"
        )
    return "\n".join(lines)


@tool
def update_stock_level(item_name: str, new_stock: int) -> str:
    """
    Set the stock quantity of a product to a new value.
    Only call this tool after the user has explicitly confirmed they want to proceed with the update.
    Args:
        item_name: The product's full name or SKU.
        new_stock: The new stock quantity as a non-negative integer.
    Returns a confirmation message showing the old and new stock values.
    """
    result = db.update_stock(item_name, new_stock)
    if not result["success"]:
        return f"Error: {result['error']}"
    return (
        f"Stock for '{result['name']}' updated from "
        f"{result['old_stock']} to {result['new_stock']}."
    )


@tool
def flag_items(item_name: str) -> str:
    """
    Mark a product as low stock so it can be prioritised for reordering.
    Use this when the user asks to flag, mark, or highlight an item for restocking.
    Args:
        item_name: The product's full name or SKU.
    Returns a confirmation message, or notes if the item was already flagged today.
    """
    result = db.flag_item(item_name)
    if not result["success"]:
        return f"Error: {result['error']}"
    if result["already_flagged"]:
        return f"'{result['name']}' is already flagged for low stock today."
    return f"Item '{result['name']}' [{result['sku']}] has been flagged for low stock."


@tool
def validate_discount_code(code: str, item_name: str) -> str:
    """
    Check whether a discount code is valid for a specific product and calculate the final price.
    Use this when the user provides a promo code and wants to apply it to a product.
    Checks that the code exists, has not expired, and applies to the product's category.
    Args:
        code: The discount code string, e.g. 'ELEC20' or 'SAVE10'.
        item_name: The product's full name or SKU to apply the discount to.
    Returns SUCCESS with the discounted price, or REJECTION with the reason.
    """
    code = code.strip().upper()
    today = date.today()

    promo = db.get_discount_code(code)
    if not promo:
        return f"REJECTION: '{code}' is not a recognised discount code."

    if today > date.fromisoformat(promo["expiry"]):
        return f"REJECTION: '{code}' expired on {promo['expiry']} and is no longer valid."

    product = db.get_product(item_name)
    if not product:
        return f"REJECTION: Item '{item_name}' not found in the store."

    if promo["categories"] and product["category"] not in promo["categories"]:
        applicable = ", ".join(promo["categories"])
        return (
            f"REJECTION: '{code}' is only valid for {applicable} items. "
            f"'{product['name']}' is in the {product['category']} category."
        )

    original = float(product["price"])
    discounted = round(original * (1 - promo["percentage"] / 100), 2)
    saving = round(original - discounted, 2)
    return (
        f"SUCCESS: '{code}' applied to [{product['sku']}] {product['name']}. "
        f"{promo['percentage']}% off — ${original:.2f} → ${discounted:.2f} "
        f"(saving ${saving:.2f}). Code valid until {promo['expiry']}."
    )