import sqlite3
from modules import database

# Daftar PO yang sudah lunas (✅) berdasarkan rekap
lunas_po = [
    "PO 1", "PO 2", "PO 3", "PO 4", "PO 6", "PO 7",
    "PO 9", "PO 10", "PO 12", "PO 13", "PO 14", "PO 17"
]

conn = database.get_connection()
cursor = conn.cursor()
# Reset semua paid ke 0 dulu
cursor.execute("UPDATE sales SET paid = 0")
# Set yang lunas
for po in lunas_po:
    cursor.execute("UPDATE sales SET paid = 1 WHERE customer_name LIKE ?", (f'%{po}%',))
    print(f"✅ {po} ditandai lunas.")
conn.commit()
conn.close()
print("🎉 Status paid diperbarui.")