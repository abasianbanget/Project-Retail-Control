import sqlite3
from modules import database

def add_paid_column():
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN paid INTEGER DEFAULT 0")
        print("✅ Kolom 'paid' ditambahkan ke tabel sales.")
    except sqlite3.OperationalError:
        print("ℹ️ Kolom 'paid' sudah ada.")
    conn.commit()
    conn.close()

def update_status_from_evidence():
    conn = database.get_connection()
    cursor = conn.cursor()

    # Berdasarkan rekap Bu Maydy dan konfirmasi Kalila, PO yang sudah lunas:
    lunas_po = [
        "PO 1", "PO 2", "PO 3", "PO 4", "PO 6", "PO 7",
        "PO 9", "PO 10", "PO 12", "PO 13", "PO 14", "PO 17"
    ]
    # PO yang belum lunas: PO 5, PO 8, PO 11 (hanya DP), PO 15, PO 16
    for po in lunas_po:
        cursor.execute('''
            UPDATE sales SET paid = 1 WHERE customer_name LIKE ? OR customer_name = ?
        ''', (f'%{po}%', po))
        print(f"✅ PO {po} ditandai lunas.")

    # PO 11 hanya DP 7jt, belum lunas
    cursor.execute('''
        UPDATE sales SET paid = 0 WHERE customer_name LIKE '%PO 11%'
    ''')
    print("ℹ️ PO 11 belum lunas (hanya DP).")

    # PO 5 dan PO 8 belum lunas
    cursor.execute('''
        UPDATE sales SET paid = 0 WHERE customer_name LIKE '%PO 5%' OR customer_name LIKE '%PO 8%'
    ''')
    print("ℹ️ PO 5 dan PO 8 belum lunas.")

    conn.commit()
    conn.close()
    print("🎉 Status payment diperbarui.")

if __name__ == "__main__":
    add_paid_column()
    update_status_from_evidence()