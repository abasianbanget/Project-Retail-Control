import sqlite3
from modules.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Tambah kolom project_id ke warehouses jika belum ada
try:
    cursor.execute("ALTER TABLE warehouses ADD COLUMN project_id INTEGER DEFAULT 1")
    print("✅ Kolom project_id ditambahkan ke warehouses.")
except:
    print("ℹ️ Kolom project_id sudah ada di warehouses.")

# Tambah kolom project_id ke stores jika belum ada
try:
    cursor.execute("ALTER TABLE stores ADD COLUMN project_id INTEGER DEFAULT 1")
    print("✅ Kolom project_id ditambahkan ke stores.")
except:
    print("ℹ️ Kolom project_id sudah ada di stores.")

# Update data lama (asumsikan project_id = 1 untuk data yang sudah ada)
cursor.execute("UPDATE warehouses SET project_id = 1 WHERE project_id IS NULL")
cursor.execute("UPDATE stores SET project_id = 1 WHERE project_id IS NULL")

# Buat tabel operational_expenses jika belum ada
cursor.execute('''
    CREATE TABLE IF NOT EXISTS operational_expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        evidence_path TEXT,
        status TEXT DEFAULT 'pending',
        requested_by TEXT,
        approved_by TEXT,
        notes TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
    )
''')
print("✅ Tabel operational_expenses siap.")

conn.commit()
conn.close()
print("🎉 Migrasi selesai.")