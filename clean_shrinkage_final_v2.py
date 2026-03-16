# clean_shrinkage_final_v2.py
import sqlite3
from datetime import date
from modules import database
import time

def wait():
    time.sleep(1)

def clean_all():
    conn = database.get_connection()
    cursor = conn.cursor()

    # 1. Hapus semua sales yang merupakan shrinkage salah (product_id='telur' atau notes mengandung kata kunci)
    cursor.execute("""
        DELETE FROM sales 
        WHERE product_id = 'telur' 
        AND (notes LIKE '%pecah%' OR notes LIKE '%retak%' OR notes LIKE '%shrink%')
    """)
    print(f"🗑️ Dihapus {cursor.rowcount} entri shrinkage salah dari sales.")

    # 2. Hapus juga sales dengan product_id='telur_pecah' (akan diisi ulang)
    cursor.execute("DELETE FROM sales WHERE product_id = 'telur_pecah'")
    print(f"🗑️ Dihapus {cursor.rowcount} entri telur_pecah.")

    # 3. Hapus semua inventory_movements dengan movement_type='shrinkage'
    cursor.execute("DELETE FROM inventory_movements WHERE movement_type = 'shrinkage'")
    print(f"🗑️ Dihapus {cursor.rowcount} inventory movements shrinkage.")

    # 4. Hapus semua shrinkage_records
    cursor.execute("DELETE FROM shrinkage_records")
    print(f"🗑️ Dihapus {cursor.rowcount} shrinkage_records.")

    conn.commit()
    conn.close()
    wait()

    # 5. Tambahkan shrinkage yang benar menggunakan fungsi record_shrinkage
    shrinkage_data = [
        (date(2026, 3, 12), 73, "Telur retak"),
        (date(2026, 3, 13), 25, "Telur pecah"),
    ]
    for tgl, butir, note in shrinkage_data:
        database.record_shrinkage(1, 1, tgl, butir, 1000, note)
        print(f"✅ Shrinkage {butir} butir tgl {tgl} ditambahkan.")
        wait()

if __name__ == "__main__":
    print("🚀 Memulai pembersihan data shrinkage...\n")
    clean_all()
    print("\n✅ Selesai. Silakan restart aplikasi.")