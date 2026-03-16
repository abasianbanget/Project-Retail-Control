# cleanup_and_reinsert.py
import sqlite3
from datetime import datetime
from modules import database

project_id = 1
warehouse_id = 1
store_id = 1

def reset_database():
    """Hapus semua data yang tidak perlu dan reset stok."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Hapus semua sales, inventory_movements, shrinkage_records, store_inventory
    cursor.execute("DELETE FROM sales WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM inventory_movements WHERE warehouse_id = ? OR store_id = ?", (warehouse_id, store_id))
    cursor.execute("DELETE FROM shrinkage_records WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM store_inventory WHERE store_id = ?", (store_id,))

    # Reset store_inventory untuk telur dengan nilai 0
    cursor.execute('''
        INSERT INTO store_inventory (store_id, product_id, quantity, last_updated)
        VALUES (?, 'telur', 0, ?)
    ''', (store_id, datetime.now().date().isoformat()))

    conn.commit()
    conn.close()
    print("✅ Semua data transaksi dihapus. Stok direset.")

def add_batch_inbound():
    """Tambahkan inbound batch 001."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, reference_id, notes)
        VALUES (?, ?, ?, 'inbound', ?, ?, ?)
    ''', ('2026-03-07', warehouse_id, 'telur', 1500, 'BATCH-001', 'Penerimaan batch 001'))
    conn.commit()
    conn.close()
    print("✅ Batch 001 (1500 kg) ditambahkan.")

def add_warehouse_sale(tgl_str, qty, price, customer, payment_method='Transfer'):
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    database.record_warehouse_sale(project_id, warehouse_id, 'telur', qty, price, customer, payment_method)
    print(f"✅ Penjualan gudang {customer} {qty} kg tgl {tgl_str}")

def add_transfer(tgl_str, qty):
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    database.add_transfer_to_store(warehouse_id, store_id, 'telur', qty, f"Transfer ke toko {qty} kg")
    print(f"✅ Transfer {qty} kg tgl {tgl_str}")

def add_store_sale(tgl_str, qty, price, customer, payment_method='Cash', notes=''):
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    database.record_store_sale(project_id, store_id, 'telur', qty, price, customer, payment_method, notes)
    print(f"✅ Penjualan toko {customer} {qty} kg tgl {tgl_str}")

def add_shrinkage(tgl_str, butir, harga=1000, notes=''):
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    database.record_shrinkage(project_id, store_id, date_obj, butir, harga, notes)
    print(f"✅ Shrinkage {butir} butir tgl {tgl_str}")

def main():
    print("🚀 Membersihkan data dan memasukkan ulang transaksi yang benar...\n")
    
    reset_database()
    add_batch_inbound()

    # ===== PENJUALAN GUDANG =====
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
        ("15/03/26", 15, 29200, "Warung Madura Tales"),
    ]
    for tgl, qty, harga, cust in warehouse_sales:
        add_warehouse_sale(tgl, qty, harga, cust)

    # ===== TRANSFER KE TOKO =====
    transfers = [
        ("10/03/26", 260),
        ("14/03/26", 240),
    ]
    for tgl, qty in transfers:
        add_transfer(tgl, qty)

    # ===== PENJUALAN TOKO =====
    store_sales = [
        ("10/03/26", 43, 29500, "PO 3", "Cash+QR", "QR 430.000, Cash 933.000"),
        ("11/03/26", 32, 28500, "PO 4", "Cash", ""),
        ("12/03/26", 15, 29000, "PO 9", "Cash", ""),
        ("12/03/26", 19.3, 29000, "PO 10", "Cash", ""),
        ("13/03/26", 29.5, 29000, "PO 12", "Cash", ""),
        ("14/03/26", 47, 29000, "PO 14", "Cash+QR", "QR 430.000, Cash 933.000"),
    ]
    for tgl, qty, harga, cust, metode, note in store_sales:
        add_store_sale(tgl, qty, harga, cust, metode, note)

    # ===== SHRINKAGE =====
    shrinkages = [
        ("12/03/26", 73, "Telur retak"),
        ("13/03/26", 25, "Telur pecah"),
    ]
    for tgl, butir, note in shrinkages:
        add_shrinkage(tgl, butir, 1000, note)

    # ===== HITUNG ULANG STOK =====
    print("\n📊 Menghitung ulang stok...")
    total_inbound = 1500
    total_warehouse_sales = sum(q for _, q, _, _ in warehouse_sales)
    total_transfer = sum(q for _, q in transfers)
    stok_gudang = total_inbound - total_warehouse_sales - total_transfer
    # Stok gudang setelah semua pengeluaran = 1500 - (30+20+30+30+30+60+500+30+105+60+15) - (260+240)
    # Mari hitung manual:
    # warehouse_sales total = 30+20+30+30+30+60+500+30+105+60+15 = 30+20=50, +30=80, +30=110, +30=140, +60=200, +500=700, +30=730, +105=835, +60=895, +15=910 kg
    # transfer total = 260+240 = 500 kg
    # total keluar gudang = 910 + 500 = 1410 kg
    # stok gudang = 1500 - 1410 = 90 kg
    stok_gudang = 90.0

    # Stok toko = total transfer - penjualan toko - shrinkage
    total_store_sales = sum(q for _, q, _, _, _, _ in store_sales)
    total_shrinkage_butir = sum(b for _, b, _ in shrinkages)
    total_shrinkage_kg = total_shrinkage_butir / database.SHRINKAGE_CONVERSION  # 98/16 = 6.125 kg
    stok_toko = total_transfer - total_store_sales - total_shrinkage_kg

    # Penyesuaian jika ada perbedaan pembulatan
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE store_inventory SET quantity = ?, last_updated = ?
        WHERE store_id = ? AND product_id = 'telur'
    ''', (stok_toko, datetime.now().date().isoformat(), store_id))
    conn.commit()
    conn.close()

    print(f"✅ Stok gudang: {stok_gudang:.2f} kg")
    print(f"✅ Stok toko: {stok_toko:.2f} kg")

    print("\n🎉 Database telah diperbaiki.")

if __name__ == "__main__":
    main()