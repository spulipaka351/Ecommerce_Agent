from langchain.tools import tool
from datetime import date

Store = [
    # Electronics
    {"sku": "ELEC-001", "name": "Smartphone X",        "category": "Electronics", "price": 799.00,  "stock": 50,  "threshold": 10},
    {"sku": "ELEC-002", "name": "Wireless Earbuds",    "category": "Electronics", "price": 129.50,  "stock": 8,   "threshold": 15},  # Low stock
    {"sku": "ELEC-003", "name": "Laptop Pro 14",       "category": "Electronics", "price": 1499.00, "stock": 25,  "threshold": 5},
    {"sku": "ELEC-004", "name": "Bluetooth Speaker",   "category": "Electronics", "price": 59.99,   "stock": 100, "threshold": 20},
    {"sku": "ELEC-005", "name": "Smart Watch",         "category": "Electronics", "price": 199.00,  "stock": 5,   "threshold": 5},   # Boundary case

    # Home & Kitchen
    {"sku": "HOME-101", "name": "Coffee Maker",        "category": "Home", "price": 89.00,  "stock": 30, "threshold": 10},
    {"sku": "HOME-102", "name": "Air Fryer",           "category": "Home", "price": 120.00, "stock": 12, "threshold": 15},  # Low stock
    {"sku": "HOME-103", "name": "Blender",             "category": "Home", "price": 45.00,  "stock": 60, "threshold": 10},
    {"sku": "HOME-104", "name": "Toaster",             "category": "Home", "price": 25.00,  "stock": 40, "threshold": 8},
    {"sku": "HOME-105", "name": "Vacuum Cleaner",      "category": "Home", "price": 250.00, "stock": 3,  "threshold": 10},  # Low stock

    # Apparel
    {"sku": "APP-201", "name": "Cotton T-Shirt",       "category": "Apparel", "price": 19.99,  "stock": 200, "threshold": 50},
    {"sku": "APP-202", "name": "Denim Jeans",          "category": "Apparel", "price": 49.50,  "stock": 85,  "threshold": 20},
    {"sku": "APP-203", "name": "Hoodie",               "category": "Apparel", "price": 35.00,  "stock": 45,  "threshold": 15},
    {"sku": "APP-204", "name": "Running Shoes",        "category": "Apparel", "price": 85.00,  "stock": 10,  "threshold": 25},  # Low stock
    {"sku": "APP-205", "name": "Winter Jacket",        "category": "Apparel", "price": 120.00, "stock": 15,  "threshold": 5},

    # Office Supplies
    {"sku": "OFF-301", "name": "Desk Lamp",            "category": "Office", "price": 34.00,  "stock": 22,  "threshold": 10},
    {"sku": "OFF-302", "name": "Office Chair",         "category": "Office", "price": 180.00, "stock": 7,   "threshold": 5},
    {"sku": "OFF-303", "name": "Notebook (Set of 3)",  "category": "Office", "price": 12.99,  "stock": 150, "threshold": 30},
    {"sku": "OFF-304", "name": "Wireless Mouse",       "category": "Office", "price": 29.00,  "stock": 40,  "threshold": 10},
    {"sku": "OFF-305", "name": "Mechanical Keyboard",  "category": "Office", "price": 95.00,  "stock": 18,  "threshold": 5},
]

# ---------------------------------------------------------------------------
# Discount code registry
# Each code has: percentage off, expiry date, and optionally a list of
# categories it applies to (None = store-wide).
# ---------------------------------------------------------------------------
DISCOUNT_CODES: dict = {
    "SAVE10":    {"percentage": 10.0, "expiry": date(2026, 12, 31), "categories": None},
    "ELEC20":    {"percentage": 20.0, "expiry": date(2026, 6, 30),  "categories": ["Electronics"]},
    "HOME15":    {"percentage": 15.0, "expiry": date(2026, 9, 30),  "categories": ["Home"]},
    "APPAREL5":  {"percentage": 5.0,  "expiry": date(2026, 8, 31),  "categories": ["Apparel"]},
    "EXPIRED50": {"percentage": 50.0, "expiry": date(2025, 1, 1),   "categories": None},   # intentionally expired
    "OFFICE25":  {"percentage": 25.0, "expiry": date(2026, 7, 31),  "categories": ["Office"]},
}

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _find_item(identifier: str) -> dict | None:
    """Return the Store dict for a given SKU or item name (case-insensitive)."""
    identifier = identifier.strip()
    for item in Store:
        if item["sku"].upper() == identifier.upper():
            return item
        if item["name"].lower() == identifier.lower():
            return item
    return None


# ---------------------------------------------------------------------------
# Existing tools (unchanged logic, boundary fix applied to check_low_stock)
# ---------------------------------------------------------------------------

@tool
def get_price(item_name: str) -> float:
    """Get the current price of an item by name."""
    item = _find_item(item_name)
    return item["price"] if item else -1


@tool
def get_inventory() -> str:
    """Get the full list of items currently in the store."""
    return ", ".join([item["name"] for item in Store])


@tool
def apply_discount(item_name: str, discount_percentage: float) -> float:
    """
    Apply a raw percentage discount to an item and return the new price.
    Use validate_discount_code first when the user supplies a discount code.
    """
    item = _find_item(item_name)
    if not item:
        return -1
    return round(item["price"] * (1 - discount_percentage / 100), 2)


@tool
def check_low_stock(threshold: int = None) -> str:
    """
    Check stock levels and flag items AT OR BELOW their threshold.
    If a custom threshold integer is provided it overrides each item's individual threshold.
    """
    flagged = []
    for item in Store:
        check_threshold = threshold if threshold is not None else item["threshold"]
        if item["stock"] <= check_threshold:   # fixed: was strictly <
            flagged.append({
                "sku":           item["sku"],
                "name":          item["name"],
                "category":      item["category"],
                "current_stock": item["stock"],
                "threshold":     item["threshold"],
                "units_below":   check_threshold - item["stock"],
            })

    if not flagged:
        return "✓ All items are above their stock thresholds."

    result = f"⚠ {len(flagged)} item(s) at or below threshold:\n"
    for i in flagged:
        result += (
            f"  • [{i['sku']}] {i['name']} ({i['category']}): "
            f"{i['current_stock']} units (threshold: {i['threshold']}, "
            f"{i['units_below']} below)\n"
        )
    return result


# ---------------------------------------------------------------------------
# NEW — Milestone 2 tools
# ---------------------------------------------------------------------------

@tool
def update_stock_level(identifier: str, new_stock: int) -> str:
    """
    Update the stock level for a single SKU or item name.

    The agent MUST ask the user for confirmation before calling this tool.
    Returns a success message with old and new stock, or an error string.

    Args:
        identifier: SKU (e.g. 'ELEC-001') or exact item name.
        new_stock:  The new stock quantity (must be >= 0).
    """
    if new_stock < 0:
        return "REJECTION: new_stock cannot be negative."

    item = _find_item(identifier)
    if not item:
        return f"REJECTION: SKU or item '{identifier}' not found. Please clarify."

    old_stock = item["stock"]
    item["stock"] = new_stock

    # Proactive low-stock warning after the write
    warning = ""
    if new_stock <= item["threshold"]:
        warning = (
            f"\n  ⚠ Warning: new stock ({new_stock}) is at or below "
            f"the threshold ({item['threshold']}) for this SKU."
        )

    return (
        f"SUCCESS: [{item['sku']}] {item['name']} stock updated "
        f"{old_stock} → {new_stock}.{warning}"
    )


@tool
def validate_discount_code(code: str, item_name: str) -> str:
    """
    Validate a discount code for a specific item and return the discounted price
    if valid, or a rejection reason if not.

    Checks performed (in order):
      1. Code exists in the registry.
      2. Code has not expired (compared against today's date).
      3. Code is applicable to the item's category.
      4. Item exists in the store.

    Args:
        code:      The discount code string (case-insensitive).
        item_name: The exact item name or SKU to apply the discount to.
    """
    code = code.strip().upper()
    today = date.today()

    # 1. Does the code exist?
    if code not in DISCOUNT_CODES:
        return f"REJECTION: '{code}' is not a recognised discount code."

    promo = DISCOUNT_CODES[code]

    # 2. Has it expired?
    if today > promo["expiry"]:
        return (
            f"REJECTION: '{code}' expired on {promo['expiry'].strftime('%B %d, %Y')} "
            f"and is no longer valid."
        )

    # 3. Does the item exist?
    item = _find_item(item_name)
    if not item:
        return f"REJECTION: Item '{item_name}' not found in the store."

    # 4. Is the code applicable to this item's category?
    if promo["categories"] is not None:
        if item["category"] not in promo["categories"]:
            applicable = ", ".join(promo["categories"])
            return (
                f"REJECTION: '{code}' is only valid for {applicable} items. "
                f"'{item['name']}' is in the {item['category']} category."
            )

    # All checks passed — apply discount
    original_price = item["price"]
    discounted_price = round(original_price * (1 - promo["percentage"] / 100), 2)
    saving = round(original_price - discounted_price, 2)

    return (
        f"SUCCESS: '{code}' applied to [{item['sku']}] {item['name']}. "
        f"{promo['percentage']}% off — "
        f"${original_price:.2f} → ${discounted_price:.2f} (saving ${saving:.2f}). "
        f"Code valid until {promo['expiry'].strftime('%B %d, %Y')}."
    )