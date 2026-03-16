import sqlite3
from modules.database import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE inventory_movements ADD COLUMN store_id INTEGER REFERENCES stores(id)")
    print("✅ Kolom store_id berhasil ditambahkan ke inventory_movements.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ Kolom store_id sudah ada.")
    else:
        raise

conn.commit()
conn.close()