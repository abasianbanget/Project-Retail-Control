# final_audit_clean.py
import sqlite3
from datetime import datetime
from modules import database

project_id = 1
warehouse_id = 1
store_id = 1
product_id = 'telur'

def hapus_duplikat_sales():
    """Hapus penjualan duplikat berdasarkan tanggal, sumber, jumlah, dan pelanggan, sisakan yang pertama."""
    conn = database.get_connection()
    cursor = conn.cursor()
    # Cari duplikat
    cursor.execute('''
        SELECT date, source_type, quantity, customer_name, MIN(id) as min_id, COUNT(*) as cnt
        FROM sales
        WHERE project_id = ? AND product_id = ?
        GROUP BY date, source_type, quantity, customer_name
        HAVING COUNT(*) > 1
    ''', (project_id, product_id))
    duplicates = cursor.fetchall()
    for dup in duplicates:
        date_str, source, qty, cust, min_id, cnt = dup
        cursor.execute('''
            DELETE FROM sales
            WHERE date = ? AND source_type = ? AND quantity = ? AND customer_name = ? AND id != ?
        ''', (date_str, source, qty, cust, min_id))
        print(f"🗑️ Dihapus {cnt-1} duplikat untuk {date_str} - {source} - {qty} kg - {cust}")
    conn.commit()
    conn.close()

def hapus_duplikat_inventory():
    """Hapus pergerakan stok duplikat (misal transfer dengan tanggal dan jumlah yang sama)."""
    conn = database.get_connection()
    cursor = conn.cursor()
    # Cari transfer duplikat
    cursor.execute('''
        SELECT date, movement_type, quantity, notes, MIN(id) as min_id, COUNT(*) as cnt
        FROM inventory_movements
        WHERE warehouse_id = ? AND movement_type = 'transfer_to_store'
        GROUP BY date, movement_type, quantity, notes
        HAVING COUNT(*) > 1
    ''', (warehouse_id,))
    duplicates = cursor.fetchall()
    for dup in duplicates:
        date_str, mtype, qty, notes, min_id, cnt = dup
        cursor.execute('''
            DELETE FROM inventory_movements
            WHERE date = ? AND movement_type = ? AND quantity = ? AND notes = ? AND id != ?
        ''', (date_str, mtype, qty, notes, min_id))
        print(f"🗑️ Dihapus {cnt-1} duplikat transfer pada {date_str} dengan jumlah {qty}")
    conn.commit()
    conn.close()

def tambah_transfer_502():
    """Tambahkan transfer 502 kg pada 15/3/2026 (sisa stok ke toko)."""
    conn = database.get_connection()
    cursor = conn.cursor()
    tgl = "2026-03-15"
    qty = 502
    # Cek apakah sudah ada transfer dengan jumlah 502 pada tanggal ini
    cursor.execute('''
        SELECT id FROM inventory_movements
        WHERE date = ? AND warehouse_id = ? AND movement_type = 'transfer_to_store' AND quantity = -?
    ''', (tgl, warehouse_id, qty))
    if not cursor.fetchone():
        # Tambahkan transfer
        cursor.execute('''
            INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, notes)
            VALUES (?, ?, ?, 'transfer_to_store', ?, ?)
        ''', (tgl, warehouse_id, product_id, -qty, f"Transfer ke toko {qty} kg"))
        # Update stok toko
        cursor.execute('''
            INSERT INTO store_inventory (store_id, product_id, quantity, last_updated)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(store_id, product_id) DO UPDATE
            SET quantity = quantity + excluded.quantity, last_updated = excluded.last_updated
        ''', (store_id, product_id, qty, tgl))
        print(f"✅ Transfer {qty} kg tanggal {tgl} ditambahkan.")
    else:
        print(f"⏩ Transfer {qty} kg tanggal {tgl} sudah ada.")
    conn.commit()
    conn.close()

def hapus_transfer_260_240_15():
    """Hapus transfer 260 dan 240 pada 15/3 jika ada (duplikasi)."""
    conn = database.get_connection()
    cursor = conn.cursor()
    for qty in [260, 240]:
        cursor.execute('''
            DELETE FROM inventory_movements
            WHERE date = '2026-03-15' AND warehouse_id = ? AND movement_type = 'transfer_to_store' AND quantity = -?
        ''', (warehouse_id, qty))
        if cursor.rowcount > 0:
            print(f"🗑️ Dihapus transfer {qty} kg tanggal 2026-03-15 (duplikat).")
    conn.commit()
    conn.close()

def hitung_ulang_stok():
    """Hitung stok gudang dan toko berdasarkan data yang valid, lalu adjustment ke nilai sebenarnya."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Hitung stok gudang dari movements
    cursor.execute('''
        SELECT SUM(quantity) FROM inventory_movements
        WHERE warehouse_id = ? AND product_id = ?
    ''', (warehouse_id, product_id))
    stok_gudang = cursor.fetchone()[0] or 0
    print(f"📊 Stok gudang saat ini (dari movements): {stok_gudang:.2f} kg")

    # Seharusnya 0 kg
    if abs(stok_gudang) > 0.01:
        diff = -stok_gudang
        date_str = datetime.now().date().isoformat()
        cursor.execute('''
            INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, notes)
            VALUES (?, ?, ?, 'adjustment', ?, ?)
        ''', (date_str, warehouse_id, product_id, diff, "Koreksi final: gudang kosong"))
        print(f"✅ Adjustment gudang {diff:+.2f} kg dilakukan. Stok gudang menjadi 0.")
    else:
        print("✅ Stok gudang sudah 0.")

    # Hitung stok toko dari transfer - penjualan - shrinkage
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

    # Ambil stok toko saat ini
    cursor.execute('''
        SELECT quantity FROM store_inventory WHERE store_id = ? AND product_id = ?
    ''', (store_id, product_id))
    current_stok_toko = cursor.fetchone()[0] or 0

    if abs(current_stok_toko - stok_toko_seharusnya) > 0.01:
        cursor.execute('''
            UPDATE store_inventory SET quantity = ?, last_updated = ?
            WHERE store_id = ? AND product_id = ?
        ''', (stok_toko_seharusnya, datetime.now().date().isoformat(), store_id, product_id))
        print(f"✅ Stok toko dikoreksi dari {current_stok_toko:.2f} kg menjadi {stok_toko_seharusnya:.2f} kg.")
    else:
        print(f"✅ Stok toko sudah sesuai: {current_stok_toko:.2f} kg.")

    conn.commit()
    conn.close()

def bersihkan_shrinkage_salah():
    """Hapus entri shrinkage yang mungkin tercatat ganda atau salah (karena akan dihitung ulang)."""
    conn = database.get_connection()
    cursor = conn.cursor()
    # Hapus semua shrinkage records (akan ditambahkan ulang nanti jika perlu)
    cursor.execute("DELETE FROM shrinkage_records WHERE project_id = ?", (project_id,))
    # Hapus juga inventory movements shrinkage yang mungkin ada
    cursor.execute("DELETE FROM inventory_movements WHERE movement_type = 'shrinkage' AND store_id = ?", (store_id,))
    print("🗑️ Semua data shrinkage lama dihapus.")
    conn.commit()
    conn.close()

def tambah_shrinkage_yang_benar():
    """Tambahkan shrinkage sesuai laporan: 73 butir (12/3) dan 25 butir (13/3)."""
    from datetime import date
    shrinkage_data = [
        (date(2026, 3, 12), 73, "Telur retak"),
        (date(2026, 3, 13), 25, "Telur pecah"),
    ]
    for tgl, butir, note in shrinkage_data:
        database.record_shrinkage(project_id, store_id, tgl, butir, 1000, note)
        print(f"✅ Shrinkage {butir} butir tanggal {tgl} ditambahkan.")

if __name__ == "__main__":
    print("🚀 Memulai audit forensik dan perbaikan...\n")
    hapus_duplikat_sales()
    hapus_duplikat_inventory()
    hapus_transfer_260_240_15()
    tambah_transfer_502()
    bersihkan_shrinkage_salah()
    tambah_shrinkage_yang_benar()
    hitung_ulang_stok()
    print("\n🎉 Selesai. Silakan restart aplikasi Streamlit.")