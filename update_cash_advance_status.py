# update_cash_advance_status.py
from modules import database

def update_status():
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Pengajuan pertama (5 Maret 2026) – disetujui
    cursor.execute("UPDATE operational_expenses SET status = 'approved' WHERE date = '2026-03-05'")
    print(f"✅ {cursor.rowcount} item pengajuan pertama (5 Maret) di-set approved.")
    
    # Pengajuan kedua (10 Maret 2026) – pending (belum dieksekusi)
    cursor.execute("UPDATE operational_expenses SET status = 'pending' WHERE date = '2026-03-10'")
    print(f"✅ {cursor.rowcount} item pengajuan kedua (10 Maret) di-set pending.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_status()