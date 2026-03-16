import sqlite3

conn = sqlite3.connect('data/finance.db')
cursor = conn.cursor()

# Hapus data stok kios lama
cursor.execute("DELETE FROM store_inventory")
print("🗑️ Data stok kios lama dihapus.")

# Hitung total transfer dari gudang ke kios (ambil nilai absolut karena di database tersimpan negatif)
cursor.execute("""
    SELECT SUM(ABS(quantity)) FROM inventory_movements 
    WHERE movement_type = 'transfer_to_store' AND warehouse_id = 1
""")
total_transfer = cursor.fetchone()[0] or 0
print(f"📦 Total transfer ke kios: {total_transfer} kg")

# Masukkan stok awal kios berdasarkan transfer
cursor.execute("""
    INSERT INTO store_inventory (store_id, product_id, quantity, last_updated)
    VALUES (1, 'telur', ?, date('now'))
""", (total_transfer,))

# Hitung total penjualan di kios dari tabel sales
cursor.execute("""
    SELECT SUM(quantity) FROM sales 
    WHERE source_type = 'store' AND source_id = 1
""")
total_sold = cursor.fetchone()[0] or 0
print(f"💰 Total penjualan kios: {total_sold} kg")

# Kurangi stok kios dengan penjualan
cursor.execute("""
    UPDATE store_inventory SET quantity = quantity - ? 
    WHERE store_id = 1 AND product_id = 'telur'
""", (total_sold,))

conn.commit()
conn.close()

stok_akhir = total_transfer - total_sold
print(f"✨ Stok kios sekarang: {stok_akhir} kg")
print("🎉 Perbaikan selesai.")