from modules import database
from datetime import date

project_id = 1
warehouse_id = 1
store_id = 1
product_id = 'telur'

def add_warehouse_sale(tanggal, qty, harga, customer):
    tgl = date.fromisoformat(tanggal)
    po = database.record_warehouse_sale(
        warehouse_id, product_id, qty, harga,
        customer, 'Transfer'
    )
    print(f"✅ {po} - Warehouse - {qty} kg - Rp {qty*harga:,.0f} - {customer}")

def add_store_sale(tanggal, qty, harga, customer):
    tgl = date.fromisoformat(tanggal)
    po = database.record_store_sale(
        store_id, product_id, qty, harga,
        customer, 'Cash'
    )
    print(f"✅ {po} - Store - {qty} kg - Rp {qty*harga:,.0f} - {customer}")

# Data penjualan: (tanggal, qty, harga, customer, type)
# type: 'w' untuk warehouse, 's' untuk store
sales = [
    ('2026-03-08', 30, 30000, 'PO 1', 'w'),
    ('2026-03-09', 20, 30000, 'PO 2', 'w'),
    ('2026-03-10', 43, 30000, 'PO 3', 's'),
    ('2026-03-11', 32, 30000, 'PO 4', 's'),
    ('2026-03-11', 30, 30000, 'PO 5', 'w'),
    ('2026-03-12', 30, 30000, 'PO 6', 'w'),
    ('2026-03-12', 30, 30000, 'PO 7', 'w'),
    ('2026-03-12', 60, 30000, 'PO 8', 'w'),
    ('2026-03-12', 15, 30000, 'PO 9', 's'),
    ('2026-03-12', 19.3, 30000, 'PO 10', 's'),
    ('2026-03-13', 500, 28000, 'PO 11 (DP 7jt, lunas 18/03)', 'w'),
    ('2026-03-12', 3.65, 20000, 'Telur Retak 73 butir', 's'),
]

print("Memasukkan data penjualan...")
for tgl, qty, harga, cust, typ in sales:
    if typ == 'w':
        add_warehouse_sale(tgl, qty, harga, cust)
    else:
        add_store_sale(tgl, qty, harga, cust)

print("🎉 Semua data berhasil dimasukkan.")