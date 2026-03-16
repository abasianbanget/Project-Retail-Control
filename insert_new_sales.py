from modules import database
from datetime import date

project_id = 1
warehouse_id = 1
store_id = 1
product_id = 'telur'

def add_warehouse_sale(tanggal, qty, harga, customer, metode='Transfer'):
    tgl = date.fromisoformat(tanggal)
    po = database.record_warehouse_sale(
        warehouse_id, product_id, qty, harga,
        customer, metode
    )
    print(f"✅ {po} - Warehouse - {qty} kg @ Rp {harga:,} - {customer}")

def add_store_sale(tanggal, qty, harga, customer, metode='Cash', notes=''):
    tgl = date.fromisoformat(tanggal)
    po = database.record_store_sale(
        store_id, product_id, qty, harga,
        customer, metode, notes
    )
    print(f"✅ {po} - Store - {qty} kg @ Rp {harga:,} - {customer} | {notes}")

# Data penjualan baru
new_sales = [
    # PO 12 (store)
    ('2026-03-13', 29.5, 29000, 'PO 12', 'Cash', 'Penjualan toko 13/03'),
    # PO 13 (warehouse)
    ('2026-03-14', 30, 28000, 'PO 13 (Cililitan)', 'Transfer'),
    # PO 14 (store)
    ('2026-03-14', 47, 29000, 'PO 14', 'Cash', 'Penjualan toko 14/03'),
    # Telur pecah (store)
    ('2026-03-13', 1.25, 20000, 'Telur Pecah', 'Cash', '25 butir @1000'),
]

print("Menambahkan data penjualan baru...")
for tgl, qty, harga, cust, metode, notes in new_sales:
    if 'warehouse' in cust.lower() or cust in ['PO 13 (Cililitan)']:
        add_warehouse_sale(tgl, qty, harga, cust, metode)
    else:
        add_store_sale(tgl, qty, harga, cust, metode, notes)

print("🎉 Semua data baru berhasil dimasukkan.")