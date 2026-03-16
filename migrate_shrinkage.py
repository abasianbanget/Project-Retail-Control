# migrate_shrinkage.py
from modules import database

# Cukup inisialisasi ulang database untuk memastikan semua tabel ada
database.init_database()
print("✅ Database siap (termasuk shrinkage_records).")