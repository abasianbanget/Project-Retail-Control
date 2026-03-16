import sqlite3
from modules.database import get_connection

def clean_duplicates():
    conn = get_connection()
    cursor = conn.cursor()

    # Hapus semua warehouse_sale tanggal 13 Maret yang bukan PO 11
    cursor.execute("""
        DELETE FROM inventory_movements 
        WHERE date = '2026-03-13' 
        AND movement_type = 'warehouse_sale' 
        AND notes NOT LIKE '%PO 11%'
    """)
    print(f"✅ Dihapus {cursor.rowcount} warehouse_sale duplikat (13 Maret)")

    # Hapus semua sales tanggal 13 Maret yang bukan PO 11
    cursor.execute("""
        DELETE FROM sales 
        WHERE date = '2026-03-13' 
        AND customer_name NOT LIKE '%PO 11%'
    """)
    print(f"✅ Dihapus {cursor.rowcount} sales duplikat (13 Maret)")

    # Hapus juga jika ada warehouse_sale dengan nama "Pembeli Tegal Danas" (duplikat PO 11)
    cursor.execute("""
        DELETE FROM inventory_movements 
        WHERE notes LIKE '%Pembeli Tegal Danas%'
    """)
    print(f"✅ Dihapus {cursor.rowcount} duplikat PO 11 (Tegal Danas)")

    conn.commit()
    conn.close()
    print("🎉 Pembersihan selesai. Stok akan otomatis terhitung ulang.")

if __name__ == "__main__":
    clean_duplicates()