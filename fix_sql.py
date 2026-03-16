import sqlite3

# Koneksi ke database
conn = sqlite3.connect('data/finance.db')
cursor = conn.cursor()

# 1. Ubah semua outbound (penjualan, transfer) menjadi negatif
cursor.execute("""
    UPDATE inventory_movements 
    SET quantity = -ABS(quantity) 
    WHERE movement_type IN ('outbound', 'warehouse_sale', 'transfer_to_store') 
       OR (movement_type IS NULL AND quantity > 0 AND notes LIKE '%outbound%')
""")
print(f"✅ Outbound dikoreksi: {cursor.rowcount} baris")

# 2. Pastikan inbound positif
cursor.execute("""
    UPDATE inventory_movements 
    SET quantity = ABS(quantity) 
    WHERE movement_type = 'inbound' OR (movement_type IS NULL AND quantity < 0 AND notes LIKE '%inbound%')
""")
print(f"✅ Inbound dikoreksi: {cursor.rowcount} baris")

conn.commit()
conn.close()
print("🎉 Koreksi tanda selesai.")