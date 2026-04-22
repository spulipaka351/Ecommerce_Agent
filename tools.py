
from langchain.tools import tool
Store = [
    # Electronics
    {"sku": "ELEC-001", "name": "Smartphone X", "category": "Electronics", "price": 799.00, "stock": 50, "threshold": 10},
    {"sku": "ELEC-002", "name": "Wireless Earbuds", "category": "Electronics", "price": 129.50, "stock": 8, "threshold": 15},  # Low Stock
    {"sku": "ELEC-003", "name": "Laptop Pro 14", "category": "Electronics", "price": 1499.00, "stock": 25, "threshold": 5},
    {"sku": "ELEC-004", "name": "Bluetooth Speaker", "category": "Electronics", "price": 59.99, "stock": 100, "threshold": 20},
    {"sku": "ELEC-005", "name": "Smart Watch", "category": "Electronics", "price": 199.00, "stock": 5, "threshold": 5},    # Boundary Case (Exactly at threshold)
    
    # Home & Kitchen
    {"sku": "HOME-101", "name": "Coffee Maker", "category": "Home", "price": 89.00, "stock": 30, "threshold": 10},
    {"sku": "HOME-102", "name": "Air Fryer", "category": "Home", "price": 120.00, "stock": 12, "threshold": 15},   # Low Stock
    {"sku": "HOME-103", "name": "Blender", "category": "Home", "price": 45.00, "stock": 60, "threshold": 10},
    {"sku": "HOME-104", "name": "Toaster", "category": "Home", "price": 25.00, "stock": 40, "threshold": 8},
    {"sku": "HOME-105", "name": "Vacuum Cleaner", "category": "Home", "price": 250.00, "stock": 3, "threshold": 10}, # Low Stock
    
    # Apparel
    {"sku": "APP-201", "name": "Cotton T-Shirt", "category": "Apparel", "price": 19.99, "stock": 200, "threshold": 50},
    {"sku": "APP-202", "name": "Denim Jeans", "category": "Apparel", "price": 49.50, "stock": 85, "threshold": 20},
    {"sku": "APP-203", "name": "Hoodie", "category": "Apparel", "price": 35.00, "stock": 45, "threshold": 15},
    {"sku": "APP-204", "name": "Running Shoes", "category": "Apparel", "price": 85.00, "stock": 10, "threshold": 25}, # Low Stock
    {"sku": "APP-205", "name": "Winter Jacket", "category": "Apparel", "price": 120.00, "stock": 15, "threshold": 5},

    # Office Supplies
    {"sku": "OFF-301", "name": "Desk Lamp", "category": "Office", "price": 34.00, "stock": 22, "threshold": 10},
    {"sku": "OFF-302", "name": "Office Chair", "category": "Office", "price": 180.00, "stock": 7, "threshold": 5},
    {"sku": "OFF-303", "name": "Notebook (Set of 3)", "category": "Office", "price": 12.99, "stock": 150, "threshold": 30},
    {"sku": "OFF-304", "name": "Wireless Mouse", "category": "Office", "price": 29.00, "stock": 40, "threshold": 10},
    {"sku": "OFF-305", "name": "Mechanical Keyboard", "category": "Office", "price": 95.00, "stock": 18, "threshold": 5}
]
@tool
def get_price(item_name: str) -> int:
    """Get the price of an item from the store."""
    for item in Store:
        if item['name'] == item_name:
            return item['price']
    return -1  # Return -1 if the item is not found
@tool(return_direct=True)
def get_items() -> str:
    """Get the list of items in the store."""
    return ", ".join([item['name'] for item in Store])

@tool
def apply_discount(item_name: str, discount_percentage: float) -> int:
    """Apply a discount to an item and return the new price."""
    for item in Store:
        if item['name'] == item_name:
            discounted_price = item['price'] * (1 - discount_percentage / 100)
            return int(discounted_price)
    return -1  # Return -1 if the item is not found