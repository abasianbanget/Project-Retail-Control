import sqlite3
from modules import database

def add_paid_column():
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN paid INTEGER DEFAULT 0")
        print("✅ Kolom 'paid' berhasil ditambahkan.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ Kolom 'paid' sudah ada.")
        else:
            print("❌ Error:", e)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_paid_column()