# seed_sales_data.py
from modules import database
from datetime import datetime

project_id = 1  # Pondok Cabe
warehouse_id = 1
store_id = 1
product_id = 'telur'

def add_sale(date_str, source, qty, price, customer, payment_method, notes=""):
    date_obj = datetime.strptime(date_str, "%d/%m/%y").date()
    if source == 'warehouse':
        database.record_warehouse_sale(project_id, warehouse_id, product_id, qty, price, customer, payment_method)
    elif source == 'store':
        database.record_store_sale(project_id, store_id, product_id, qty, price, customer, payment_method, notes)
    print(f"Added: {date_str} - {source} - {qty}kg - Rp{price}")

# Data dari rekap
sales_data = [
    ("08/03/26", "warehouse", 30, 29000, "PO 1", "Transfer"),
    ("09/03/26", "warehouse", 20, 29000, "PO 2", "Transfer"),
    ("10/03/26", "store", 43, 29000, "PO 3", "Cash"),
    ("11/03/26", "store", 32, 29000, "PO 4", "Cash"),
    ("11/03/26", "warehouse", 30, 29000, "PO 5", "Transfer"),
    ("12/03/26", "warehouse", 30, 29000, "PO 6", "Transfer"),
    ("12/03/26", "warehouse", 30, 29000, "PO 7", "Transfer"),
    ("12/03/26", "warehouse", 60, 29000, "PO 8", "Transfer"),
    ("12/03/26", "store", 15, 29000, "PO 9", "Cash"),
    ("12/03/26", "store", 19.3, 29000, "PO 10", "Cash"),
    ("13/03/26", "warehouse", 500, 28000, "PO 11", "Transfer"),
    ("13/03/26", "store", 29.5, 29000, "PO 12", "Cash"),
    ("14/03/26", "warehouse", 30, 29000, "PO 13", "Transfer"),
    ("14/03/26", "store", 47, 29000, "PO 14", "Cash+QR"),
]

for date_str, source, qty, price, customer, payment, *notes in sales_data:
    notes_str = notes[0] if notes else ""
    add_sale(date_str, source, qty, price, customer, payment, notes_str)

print("✅ Semua data penjualan berhasil dimasukkan.")