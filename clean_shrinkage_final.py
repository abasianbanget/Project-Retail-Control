# clean_shrinkage_final.py
import sqlite3
from datetime import date
from modules import database
import time

def wait():
    time.sleep(1)

def clean_all():
    conn = database.get_connection()
    cursor = conn.cursor()

    # 1. Hapus semua sales yang merupakan shrinkage salah (product_id='telur' dan notes mengandung kata kunci)
    cursor.execute("""
        DELETE FROM sales 
        WHERE product_id = 'telur' 
        AND (notes LIKE '%pecah%' OR notes LIKE '%retak%' OR notes LIKE '%shrink%')
    """)
    print(f"🗑️ Dihapus {cursor.rowcount} entri shrinkage salah dari sales.")

    # 2. Hapus semua inventory_movements dengan movement_type='shrinkage'
    cursor.execute("DELETE FROM inventory_movements WHERE movement_type = 'shrinkage'")
    print(f"🗑️ Dihapus {cursor.rowcount} inventory movements shrinkage.")

    # 3. Hapus semua shrinkage_records
    cursor.execute("DELETE FROM shrinkage_records")
    print(f"🗑️ Dihapus {cursor.rowcount} shrinkage_records.")

    conn.commit()
    conn.close()
    wait()

    # 4. Tambahkan shrinkage yang benar menggunakan fungsi record_shrinkage
    shrinkage_data = [
        (date(2026, 3, 12), 73, "Telur retak"),
        (date(2026, 3, 13), 25, "Telur pecah"),
    ]
    for tgl, butir, note in shrinkage_data:
        database.record_shrinkage(1, 1, tgl, butir, 1000, note)
        print(f"✅ Shrinkage {butir} butir tgl {tgl} ditambahkan.")
        wait()

def fix_paid_status():
    conn = database.get_connection()
    cursor = conn.cursor()

    # Reset semua paid ke 0
    cursor.execute("UPDATE sales SET paid = 0")
    print("🔄 Semua status paid direset ke 0.")

    # Daftar PO yang sudah lunas (✅)
    lunas_po = [
        "PO 1", "PO 2", "PO 3", "PO 4", "PO 6", "PO 7",
        "PO 9", "PO 10", "PO 12", "PO 13", "PO 14", "PO 15", "PO 17"
    ]
    for po in lunas_po:
        cursor.execute("UPDATE sales SET paid = 1 WHERE customer_name LIKE ?", (f'%{po}%',))
        print(f"✅ {po} ditandai lunas.")

    conn.commit()
    conn.close()
    wait()

def adjust_stock():
    """Hitung ulang stok toko dan sesuaikan ke 194.58 kg."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Hitung stok toko dari transfer - penjualan - shrinkage
    # Transfer ke toko
    cursor.execute("""
        SELECT SUM(-quantity) FROM inventory_movements
        WHERE warehouse_id = 1 AND movement_type = 'transfer_to_store'
    """)
    transfer = cursor.fetchone()[0] or 0

    # Penjualan toko (semua, termasuk yang belum lunas)
    cursor.execute("""
        SELECT SUM(quantity) FROM sales
        WHERE source_type = 'store' AND product_id = 'telur'
    """)
    sales_toko = cursor.fetchone()[0] or 0

    # Shrinkage dalam kg (dari shrinkage_records)
    cursor.execute("""
        SELECT SUM(quantity_butir) FROM shrinkage_records
    """)
    total_butir = cursor.fetchone()[0] or 0
    shrinkage_kg = total_butir / database.SHRINKAGE_CONVERSION

    stok_seharusnya = transfer - sales_toko - shrinkage_kg

    # Ambil stok saat ini
    cursor.execute("SELECT quantity FROM store_inventory WHERE store_id = 1 AND product_id = 'telur'")
    current_stok = cursor.fetchone()[0] or 0

    if abs(current_stok - stok_seharusnya) > 0.01:
        # Update store_inventory
        cursor.execute("""
            UPDATE store_inventory SET quantity = ?, last_updated = ?
            WHERE store_id = 1 AND product_id = 'telur'
        """, (stok_seharusnya, date.today().isoformat()))
        print(f"✅ Stok toko dikoreksi dari {current_stok:.2f} kg menjadi {stok_seharusnya:.2f} kg.")
    else:
        print(f"✅ Stok toko sudah sesuai: {current_stok:.2f} kg.")

    conn.commit()
    conn.close()

def verify():
    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(quantity_butir) FROM shrinkage_records")
    total_butir = cursor.fetchone()[0] or 0
    print(f"📊 Total butir shrinkage: {total_butir}")

    cursor.execute("SELECT quantity FROM store_inventory WHERE store_id = 1 AND product_id = 'telur'")
    stok_toko = cursor.fetchone()[0] or 0
    print(f"📦 Stok toko saat ini: {stok_toko:.2f} kg")

    cursor.execute("SELECT SUM(quantity) FROM sales WHERE source_type='store' AND product_id='telur'")
    sales_toko = cursor.fetchone()[0] or 0
    print(f"🛒 Total penjualan toko: {sales_toko:.2f} kg")

    cursor.execute("SELECT SUM(-quantity) FROM inventory_movements WHERE movement_type='transfer_to_store'")
    transfer = cursor.fetchone()[0] or 0
    print(f"🚛 Total transfer ke toko: {transfer:.2f} kg")

    conn.close()

if __name__ == "__main__":
    print("🚀 Memulai pembersihan data shrinkage...\n")
    clean_all()
    fix_paid_status()
    adjust_stock()
    print("\n📊 Verifikasi:")
    verify()
    print("\n✅ Selesai. Silakan restart aplikasi Streamlit.")