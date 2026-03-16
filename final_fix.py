# final_fix.py
import sqlite3
import time
from datetime import date
from modules import database

def wait_for_db():
    """Tunggu sejenak untuk menghindari database lock."""
    time.sleep(2)

def fix_shrinkage():
    """Hapus data shrinkage yang salah dan tambahkan yang benar."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Hapus semua entri shrinkage yang salah (product_id='telur' dengan notes mengandung kata kunci)
    cursor.execute("""
        DELETE FROM sales 
        WHERE product_id = 'telur' 
        AND (notes LIKE '%pecah%' OR notes LIKE '%retak%')
    """)
    print(f"🗑️ Dihapus {cursor.rowcount} entri shrinkage salah dari sales.")

    # Hapus inventory movements shrinkage yang mungkin ada
    cursor.execute("DELETE FROM inventory_movements WHERE movement_type = 'shrinkage' AND store_id = 1")
    print(f"🗑️ Dihapus {cursor.rowcount} inventory movements shrinkage.")

    # Hapus juga shrinkage_records lama
    cursor.execute("DELETE FROM shrinkage_records WHERE project_id = 1")
    print(f"🗑️ Dihapus {cursor.rowcount} shrinkage_records.")

    conn.commit()
    conn.close()
    wait_for_db()

    # Tambahkan shrinkage yang benar menggunakan fungsi record_shrinkage
    shrinkage_data = [
        (date(2026, 3, 12), 73, "Telur retak"),
        (date(2026, 3, 13), 25, "Telur pecah"),
    ]
    for tgl, butir, note in shrinkage_data:
        database.record_shrinkage(1, 1, tgl, butir, 1000, note)
        print(f"✅ Shrinkage {butir} butir tgl {tgl} ditambahkan.")
        wait_for_db()

def fix_paid_status():
    """Set ulang status paid berdasarkan rekap Bu Maydy."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Reset semua paid ke 0
    cursor.execute("UPDATE sales SET paid = 0")
    print("🔄 Semua status paid direset ke 0.")

    # Daftar PO yang sudah lunas (✅) – pastikan sesuai rekap terbaru
    lunas_po = [
        "PO 1", "PO 2", "PO 3", "PO 4", "PO 6", "PO 7",
        "PO 9", "PO 10", "PO 12", "PO 13", "PO 14", "PO 15", "PO 17"
    ]
    for po in lunas_po:
        cursor.execute("UPDATE sales SET paid = 1 WHERE customer_name LIKE ?", (f'%{po}%',))
        print(f"✅ {po} ditandai lunas.")

    # Pastikan PO 5, 8, 11, 16 tetap 0 (belum lunas)
    conn.commit()
    conn.close()
    wait_for_db()

def verify_data():
    """Tampilkan ringkasan setelah perbaikan."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Total penjualan semua
    cursor.execute("SELECT SUM(total_amount) FROM sales")
    total_semua = cursor.fetchone()[0] or 0
    print(f"📊 Total penjualan semua: Rp {total_semua:,.0f}")

    # Total penjualan lunas
    cursor.execute("SELECT SUM(total_amount) FROM sales WHERE paid = 1")
    total_lunas = cursor.fetchone()[0] or 0
    print(f"💰 Total penjualan lunas: Rp {total_lunas:,.0f}")

    # Total penjualan belum lunas
    cursor.execute("SELECT SUM(total_amount) FROM sales WHERE paid = 0")
    total_belum = cursor.fetchone()[0] or 0
    print(f"⏳ Total penjualan belum lunas: Rp {total_belum:,.0f}")

    # Stok toko saat ini
    cursor.execute("SELECT quantity FROM store_inventory WHERE store_id = 1 AND product_id = 'telur'")
    stok_toko = cursor.fetchone()[0] or 0
    print(f"📦 Stok toko: {stok_toko:.2f} kg")

    # Stok gudang
    cursor.execute("SELECT SUM(quantity) FROM inventory_movements WHERE warehouse_id = 1 AND product_id = 'telur'")
    stok_gudang = cursor.fetchone()[0] or 0
    print(f"🏭 Stok gudang: {stok_gudang:.2f} kg")

    conn.close()

if __name__ == "__main__":
    print("🚀 Memulai perbaikan data... Pastikan aplikasi Streamlit TIDAK berjalan.\n")
    fix_shrinkage()
    fix_paid_status()
    print("\n📊 Verifikasi hasil:")
    verify_data()
    print("\n✅ Selesai. Silakan restart aplikasi Streamlit.")