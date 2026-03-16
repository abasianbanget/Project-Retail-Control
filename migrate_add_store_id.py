import sqlite3
from modules.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Tambah kolom store_id ke inventory_movements jika belum ada
try:
    cursor.execute("ALTER TABLE inventory_movements ADD COLUMN store_id INTEGER")
    print("✅ Kolom store_id berhasil ditambahkan ke inventory_movements.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("ℹ️ Kolom store_id sudah ada.")
    else:
        print("❌ Error:", e)

conn.commit()
conn.close()