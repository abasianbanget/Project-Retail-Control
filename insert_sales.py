# insert_sales.py
from modules import database
from datetime import date

# Fungsi untuk menambah penjualan warehouse
def add_warehouse_sale(project_id, qty, customer, tanggal, keterangan):
    warehouse_id = 1
    product_id = 'telur'
    harga_jual = 30000  # asumsi
    metode = 'Cash'  # atau sesuai
    po = database.record_sale('warehouse', warehouse_id, product_id, qty, harga_jual, metode, 'partai', customer, keterangan)
    database.add_outbound(warehouse_id, product_id, qty, po, 'external', None, keterangan)
    print(f"Ditambahkan: {po} - {customer} - {qty} kg")

# Fungsi untuk menambah penjualan toko
def add_store_sale(project_id, qty, customer, tanggal, keterangan):
    store_id = 1
    product_id = 'telur'
    harga_jual = 30000
    metode = 'Cash'
    po = database.record_sale('store', store_id, product_id, qty, harga_jual, metode, 'retail', customer, keterangan)
    # Update stok kios manual (seharusnya sudah di record_sale? perlu di database.py)
    # Untuk sementara, kita update manual
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE store_inventory SET quantity = quantity - ?, last_updated = ?
        WHERE store_id = ? AND product_id = ?
    ''', (qty, tanggal.isoformat(), store_id, product_id))
    conn.commit()
    conn.close()
    print(f"Ditambahkan: {po} - {customer} - {qty} kg")

project_id = 1  # Pondok Cabe

# Data dari Bu Maydi
sales_data = [
    {'type': 'warehouse', 'tanggal': '2026-03-08', 'qty': 30, 'customer': 'Bu Maydi', 'ket': 'PO 1'},
    {'type': 'warehouse', 'tanggal': '2026-03-09', 'qty': 20, 'customer': 'Bu Maydi', 'ket': 'PO 2'},
    {'type': 'store', 'tanggal': '2026-03-10', 'qty': 43, 'customer': 'Toko', 'ket': 'PO 3'},
    {'type': 'store', 'tanggal': '2026-03-11', 'qty': 32, 'customer': 'Toko', 'ket': 'PO 4'},
    {'type': 'warehouse', 'tanggal': '2026-03-11', 'qty': 30, 'customer': 'Bu Maydi', 'ket': 'PO 5'},
    {'type': 'warehouse', 'tanggal': '2026-03-12', 'qty': 30, 'customer': 'Bu Maydi', 'ket': 'PO 6'},
    {'type': 'warehouse', 'tanggal': '2026-03-12', 'qty': 30, 'customer': 'Bu Maydi', 'ket': 'PO 7'},
    {'type': 'warehouse', 'tanggal': '2026-03-12', 'qty': 60, 'customer': 'Warung Madura', 'ket': 'PO 8'},
    {'type': 'store', 'tanggal': '2026-03-12', 'qty': 15, 'customer': 'Warung Madura', 'ket': 'PO 9'},
    {'type': 'store', 'tanggal': '2026-03-12', 'qty': 19.3, 'customer': 'Toko', 'ket': 'PO 10'},
]

for s in sales_data:
    tgl = date.fromisoformat(s['tanggal'])
    if s['type'] == 'warehouse':
        add_warehouse_sale(project_id, s['qty'], s['customer'], tgl, s['ket'])
    else:
        add_store_sale(project_id, s['qty'], s['customer'], tgl, s['ket'])

# Telur retak 73 butir (misal 1 butir = 0.05 kg? asumsi 20 butir/kg, jadi 73 butir = 3.65 kg)
# Atau catat sebagai penjualan terpisah dengan harga khusus
add_store_sale(project_id, 3.65, 'Telur Retak', date(2026,3,12), 'Telur retak 73 butir @1000')
print("Selesai.")