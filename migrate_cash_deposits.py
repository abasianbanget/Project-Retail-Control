import sqlite3
from modules import database

def add_approved_by():
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE cash_deposits ADD COLUMN approved_by TEXT")
        print("✅ Kolom approved_by berhasil ditambahkan.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ Kolom approved_by sudah ada.")
        else:
            print("❌ Error:", e)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_approved_by()