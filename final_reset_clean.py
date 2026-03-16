# final_reset_clean.py
import sqlite3
from datetime import datetime, date
from modules import database

project_id = 1
warehouse_id = 1
store_id = 1
product_id = 'telur'

def reset_sales():
    """Hapus semua data penjualan dan shrinkage, lalu isi ulang berdasarkan rekap Bu Maydy."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Hapus semua sales
    cursor.execute("DELETE FROM sales WHERE project_id = ?", (project_id,))
    print("🗑️ Semua data sales dihapus.")

    # Hapus semua shrinkage_records
    cursor.execute("DELETE FROM shrinkage_records WHERE project_id = ?", (project_id,))
    print("🗑️ Semua data shrinkage dihapus.")

    # Hapus semua inventory_movements (kecuali inbound batch 1) karena akan kita hitung ulang
    cursor.execute("DELETE FROM inventory_movements WHERE warehouse_id = ? AND movement_type != 'inbound'", (warehouse_id,))
    cursor.execute("DELETE FROM inventory_movements WHERE store_id = ?", (store_id,))
    print("🗑️ Semua pergerakan stok selain inbound dihapus.")

    # Reset stok toko ke 0
    cursor.execute("UPDATE store_inventory SET quantity = 0, last_updated = ? WHERE store_id = ? AND product_id = ?", 
                   (datetime.now().date().isoformat(), store_id, product_id))
    print("🔄 Stok toko direset ke 0.")

    conn.commit()
    conn.close()
    print("✅ Database siap untuk diisi ulang.\n")

def add_warehouse_sale(tgl_str, qty, price, customer, lunas):
    """Tambahkan penjualan gudang."""
    conn = database.get_connection()
    cursor = conn.cursor()
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    total = qty * price
    po = f"WH-{customer.replace(' ','')}"
    cursor.execute('''
        INSERT INTO sales (po_number, date, project_id, source_type, source_id, product_id, quantity, price_per_unit, total_amount, payment_method, customer_name, notes)
        VALUES (?, ?, ?, 'warehouse', ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (po, date_obj.isoformat(), project_id, warehouse_id, product_id, qty, price, total, 'Transfer', customer, f"Lunas: {lunas}"))
    # Tambahkan inventory movement
    cursor.execute('''
        INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, notes)
        VALUES (?, ?, ?, 'warehouse_sale', ?, ?)
    ''', (date_obj.isoformat(), warehouse_id, product_id, -qty, f"Penjualan ke {customer}"))
    conn.commit()
    conn.close()
    print(f"✅ Penjualan gudang {customer} {qty} kg tgl {tgl_str} ditambahkan (lunas: {lunas}).")

def add_store_sale(tgl_str, qty, price, customer, lunas):
    """Tambahkan penjualan toko."""
    conn = database.get_connection()
    cursor = conn.cursor()
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    total = qty * price
    po = f"ST-{customer.replace(' ','')}"
    cursor.execute('''
        INSERT INTO sales (po_number, date, project_id, source_type, source_id, product_id, quantity, price_per_unit, total_amount, payment_method, customer_name, notes)
        VALUES (?, ?, ?, 'store', ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (po, date_obj.isoformat(), project_id, store_id, product_id, qty, price, total, 'Cash', customer, f"Lunas: {lunas}"))
    # Kurangi stok toko
    cursor.execute('''
        UPDATE store_inventory SET quantity = quantity - ?, last_updated = ?
        WHERE store_id = ? AND product_id = ?
    ''', (qty, date_obj.isoformat(), store_id, product_id))
    conn.commit()
    conn.close()
    print(f"✅ Penjualan toko {customer} {qty} kg tgl {tgl_str} ditambahkan (lunas: {lunas}).")

def add_transfer(tgl_str, qty):
    """Tambahkan transfer dari gudang ke toko."""
    conn = database.get_connection()
    cursor = conn.cursor()
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    cursor.execute('''
        INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, notes)
        VALUES (?, ?, ?, 'transfer_to_store', ?, ?)
    ''', (date_obj.isoformat(), warehouse_id, product_id, -qty, f"Transfer ke toko {qty} kg"))
    # Update stok toko
    cursor.execute('''
        INSERT INTO store_inventory (store_id, product_id, quantity, last_updated)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(store_id, product_id) DO UPDATE
        SET quantity = quantity + excluded.quantity, last_updated = excluded.last_updated
    ''', (store_id, product_id, qty, date_obj.isoformat()))
    conn.commit()
    conn.close()
    print(f"✅ Transfer {qty} kg tgl {tgl_str} ditambahkan.")

def add_shrinkage(tgl_str, butir, notes):
    """Tambahkan shrinkage."""
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    database.record_shrinkage(project_id, store_id, date_obj, butir, 1000, notes)
    print(f"✅ Shrinkage {butir} butir tgl {tgl_str} ditambahkan.")

def main():
    print("🚀 Memulai reset total data penjualan berdasarkan rekap Bu Maydy...\n")
    reset_sales()

    # Data dari rekap Bu Maydy (berdasarkan pesan di grup)
    # Format: (tanggal, jenis, qty, harga, pelanggan, lunas)
    warehouse_sales = [
        ("08/03/26", 30, 29000, "PO 1", True),
        ("09/03/26", 20, 29000, "PO 2", True),
        ("11/03/26", 30, 29000, "PO 5", False),
        ("12/03/26", 30, 29000, "PO 6", True),
        ("12/03/26", 30, 29000, "PO 7", True),
        ("12/03/26", 60, 29000, "PO 8", False),
        ("13/03/26", 500, 28000, "PO 11", True),  # lunas (dp 7jt)
        ("14/03/26", 30, 29000, "PO 13", True),
        ("15/03/26", 105, 29000, "Agen Pamulang", False),
        ("15/03/26", 60, 29000, "Cililitan", False),
        ("15/03/26", 15, 29000, "Warung Madura", False),
    ]
    for tgl, qty, harga, cust, lunas in warehouse_sales:
        add_warehouse_sale(tgl, qty, harga, cust, lunas)

    store_sales = [
        ("10/03/26", 43, 29500, "PO 3", True),
        ("11/03/26", 32, 28500, "PO 4", True),
        ("12/03/26", 15, 29000, "PO 9", True),
        ("12/03/26", 19.3, 29000, "PO 10", True),
        ("13/03/26", 29.5, 29000, "PO 12", True),
        ("14/03/26", 47, 29000, "PO 14", True),
        ("15/03/26", 15, 29000, "PO 15", True),
        ("15/03/26", 150, 29000, "PO 16", False),
        ("15/03/26", 38.5, 29000, "PO 17", True),
    ]
    for tgl, qty, harga, cust, lunas in store_sales:
        add_store_sale(tgl, qty, harga, cust, lunas)

    # Transfer dari gudang ke toko (berdasarkan laporan)
    # 260 kg (10/3), 240 kg (14/3), dan 90 kg (15/3) agar gudang kosong
    transfers = [
        ("10/03/26", 260),
        ("14/03/26", 240),
        ("15/03/26", 90),  # sisa stok agar gudang 0
    ]
    for tgl, qty in transfers:
        add_transfer(tgl, qty)

    # Shrinkage
    shrinkages = [
        ("12/03/26", 73, "Telur retak"),
        ("13/03/26", 25, "Telur pecah"),
    ]
    for tgl, butir, note in shrinkages:
        add_shrinkage(tgl, butir, note)

    # Hitung ulang stok gudang (seharusnya 0)
    conn = database.get_connection()
    cursor = conn.cursor()
    # Hapus adjustment sebelumnya
    cursor.execute("DELETE FROM inventory_movements WHERE warehouse_id = ? AND movement_type = 'adjustment'", (warehouse_id,))
    # Hitung stok gudang saat ini
    cursor.execute('''
        SELECT SUM(quantity) FROM inventory_movements
        WHERE warehouse_id = ? AND product_id = ?
    ''', (warehouse_id, product_id))
    stok_gudang = cursor.fetchone()[0] or 0
    if abs(stok_gudang) > 0.01:
        diff = -stok_gudang
        cursor.execute('''
            INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, notes)
            VALUES (?, ?, ?, 'adjustment', ?, ?)
        ''', (datetime.now().date().isoformat(), warehouse_id, product_id, diff, "Koreksi final: gudang kosong"))
        print(f"✅ Adjustment gudang {diff:+.2f} kg dilakukan. Stok gudang menjadi 0.")
    else:
        print("✅ Stok gudang sudah 0.")

    # Hitung stok toko berdasarkan transfer - penjualan toko - shrinkage
    cursor.execute('''
        SELECT SUM(-quantity) FROM inventory_movements
        WHERE store_id = ? AND movement_type = 'shrinkage'
    ''', (store_id,))
    shrinkage_total = cursor.fetchone()[0] or 0

    cursor.execute('''
        SELECT SUM(quantity) FROM sales
        WHERE source_type = 'store' AND product_id = ? AND project_id = ?
    ''', (product_id, project_id))
    sales_toko = cursor.fetchone()[0] or 0

    cursor.execute('''
        SELECT SUM(-quantity) FROM inventory_movements
        WHERE warehouse_id = ? AND movement_type = 'transfer_to_store'
    ''', (warehouse_id,))
    transfer_total = cursor.fetchone()[0] or 0

    stok_toko_seharusnya = transfer_total - sales_toko - shrinkage_total
    cursor.execute('''
        UPDATE store_inventory SET quantity = ?, last_updated = ?
        WHERE store_id = ? AND product_id = ?
    ''', (stok_toko_seharusnya, datetime.now().date().isoformat(), store_id, product_id))
    print(f"✅ Stok toko diset ke {stok_toko_seharusnya:.2f} kg.")

    conn.commit()
    conn.close()

    print("\n🎉 Reset selesai. Data penjualan sekarang sesuai rekap Bu Maydy.")
    # Tampilkan total penjualan
    total_wh = sum(q for _, q, _, _, _ in warehouse_sales)
    total_st = sum(q for _, q, _, _, _ in store_sales)
    print(f"Total penjualan gudang: {total_wh} kg, toko: {total_st} kg, total: {total_wh + total_st} kg")
    print(f"Stok gudang: 0 kg, stok toko: {stok_toko_seharusnya:.2f} kg")
    print("Silakan restart aplikasi Streamlit.")

if __name__ == "__main__":
    main()