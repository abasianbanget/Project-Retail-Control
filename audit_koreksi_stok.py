# audit_koreksi_stok.py
import sqlite3
from datetime import datetime
from modules import database

project_id = 1
warehouse_id = 1
store_id = 1

def get_existing_sales(date_str, source_type, quantity, customer_name=None):
    """Cek apakah penjualan dengan tanggal, sumber, jumlah dan (opsional) nama pelanggan sudah ada."""
    conn = database.get_connection()
    cursor = conn.cursor()
    query = "SELECT id FROM sales WHERE date = ? AND source_type = ? AND quantity = ?"
    params = [date_str, source_type, quantity]
    if customer_name:
        query += " AND customer_name = ?"
        params.append(customer_name)
    cursor.execute(query, params)
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_existing_transfer(date_str, qty):
    """Cek apakah transfer ke toko dengan tanggal dan jumlah sudah ada."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM inventory_movements
        WHERE date = ? AND movement_type = 'transfer_to_store' AND quantity = -? AND warehouse_id = ?
    ''', (date_str, qty, warehouse_id))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_existing_shrinkage(date_str, butir):
    """Cek apakah shrinkage dengan tanggal dan jumlah butir sudah ada."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM shrinkage_records
        WHERE date = ? AND quantity_butir = ?
    ''', (date_str, butir))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def add_warehouse_sale(tgl_str, qty, price, customer, payment_method='Transfer', notes=''):
    """Tambahkan penjualan dari gudang jika belum ada."""
    if get_existing_sales(tgl_str, 'warehouse', qty, customer):
        print(f"⚠️ Penjualan gudang {customer} tgl {tgl_str} sudah ada, lewati.")
        return
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    database.record_warehouse_sale(project_id, warehouse_id, 'telur', qty, price, customer, payment_method)
    print(f"✅ Penjualan gudang {customer} {qty} kg tgl {tgl_str} ditambahkan.")

def add_transfer(tgl_str, qty):
    """Tambahkan transfer dari gudang ke toko jika belum ada."""
    if get_existing_transfer(tgl_str, qty):
        print(f"⚠️ Transfer {qty} kg tgl {tgl_str} sudah ada, lewati.")
        return
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    database.add_transfer_to_store(warehouse_id, store_id, 'telur', qty, f"Transfer ke toko {qty} kg")
    print(f"✅ Transfer {qty} kg tgl {tgl_str} ditambahkan.")

def add_store_sale(tgl_str, qty, price, customer, payment_method='Cash', notes=''):
    """Tambahkan penjualan dari toko jika belum ada."""
    if get_existing_sales(tgl_str, 'store', qty, customer):
        print(f"⚠️ Penjualan toko {customer} tgl {tgl_str} sudah ada, lewati.")
        return
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    database.record_store_sale(project_id, store_id, 'telur', qty, price, customer, payment_method, notes)
    print(f"✅ Penjualan toko {customer} {qty} kg tgl {tgl_str} ditambahkan.")

def add_shrinkage(tgl_str, butir, harga=1000, notes=''):
    """Tambahkan catatan telur pecah jika belum ada."""
    if get_existing_shrinkage(tgl_str, butir):
        print(f"⚠️ Shrinkage {butir} butir tgl {tgl_str} sudah ada, lewati.")
        return
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    database.record_shrinkage(project_id, store_id, date_obj, butir, harga, notes)
    print(f"✅ Shrinkage {butir} butir tgl {tgl_str} ditambahkan.")

def main():
    print("🚀 Memulai audit dan koreksi stok...\n")

    # ===== 1. PENJUALAN GUDANG =====
    warehouse_sales = [
        ("08/03/26", 30, 28700, "PO 1"),
        ("09/03/26", 20, 28700, "PO 2"),
        ("11/03/26", 30, 28000, "PO 5"),
        ("12/03/26", 30, 28000, "PO 6"),
        ("12/03/26", 30, 28000, "PO 7"),
        ("12/03/26", 60, 28000, "PO 8"),
        ("13/03/26", 500, 28000, "PO 11"),
        ("14/03/26", 30, 28000, "PO 13"),
        ("15/03/26", 105, 29200, "Agen Pamulang"),
        ("15/03/26", 60, 29200, "Cililitan"),
        ("15/03/26", 15, 29200, "Warung Madura"),
    ]
    for tgl, qty, harga, cust in warehouse_sales:
        add_warehouse_sale(tgl, qty, harga, cust)

    # ===== 2. TRANSFER KE TOKO =====
    transfers = [
        ("10/03/26", 260),
        ("14/03/26", 240),
    ]
    for tgl, qty in transfers:
        add_transfer(tgl, qty)

    # ===== 3. PENJUALAN TOKO =====
    store_sales = [
        ("10/03/26", 43, 29500, "PO 3", "Cash+QR"),
        ("11/03/26", 32, 28500, "PO 4", "Cash"),
        ("12/03/26", 15, 29000, "PO 9", "Cash"),
        ("12/03/26", 19.3, 29000, "PO 10", "Cash"),
        ("13/03/26", 29.5, 29000, "PO 12", "Cash"),
        ("14/03/26", 47, 29000, "PO 14", "Cash+QR"),
    ]
    for tgl, qty, harga, cust, metode in store_sales:
        add_store_sale(tgl, qty, harga, cust, metode)

    # ===== 4. SHRINKAGE (TELUR PECAH) =====
    shrinkages = [
        ("12/03/26", 73, "Telur retak"),
        ("13/03/26", 25, "Telur pecah"),
    ]
    for tgl, butir, note in shrinkages:
        add_shrinkage(tgl, butir, 1000, note)

    print("\n📊 Menghitung ulang stok...")

    # ===== HITUNG STOK GUDANG =====
    current_warehouse = database.get_warehouse_stock(warehouse_id, 'telur')
    expected_warehouse = 90.0  # hasil perhitungan manual

    if abs(current_warehouse - expected_warehouse) > 0.01:
        print(f"⚠️ Stok gudang saat ini {current_warehouse:.2f} kg, seharusnya {expected_warehouse:.2f} kg. Melakukan adjustment...")
        database.adjust_warehouse_stock(warehouse_id, 'telur', expected_warehouse, "Koreksi audit stok berdasarkan data transaksi")
        print(f"✅ Stok gudang disesuaikan menjadi {expected_warehouse:.2f} kg.")
    else:
        print(f"✅ Stok gudang sudah sesuai: {current_warehouse:.2f} kg.")

    # ===== HITUNG STOK TOKO =====
    current_store = database.get_store_stock(store_id, 'telur')
    expected_store = 308.08  # hasil perhitungan manual (500 - 185.8 - 6.12)

    if abs(current_store - expected_store) > 0.01:
        print(f"⚠️ Stok toko saat ini {current_store:.2f} kg, seharusnya {expected_store:.2f} kg. Melakukan adjustment...")
        database.adjust_store_stock(store_id, 'telur', expected_store, "Koreksi audit stok berdasarkan data transaksi")
        print(f"✅ Stok toko disesuaikan menjadi {expected_store:.2f} kg.")
    else:
        print(f"✅ Stok toko sudah sesuai: {current_store:.2f} kg.")

    print("\n🎉 Audit selesai.")

if __name__ == "__main__":
    main()