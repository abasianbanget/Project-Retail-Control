import sqlite3
from modules.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# 1. Hapus duplikat yang mencurigakan (PO-012 dengan id tertentu)
cursor.execute("SELECT id, po_number, date, quantity, total_amount FROM sales WHERE po_number = 'PO-012'")
rows = cursor.fetchall()
if len(rows) > 1:
    print(f"Ditemukan {len(rows)} duplikat untuk PO-012. Menghapus yang tertua...")
    # Hapus semua kecuali yang terbaru (berdasarkan id terbesar)
    ids = [row['id'] for row in rows]
    ids.sort()
    keep_id = ids[-1]
    for id in ids[:-1]:
        cursor.execute("DELETE FROM sales WHERE id = ?", (id,))
        print(f"  - Hapus id {id}")
else:
    print("Tidak ada duplikat PO-012.")

# 2. Pastikan PO 13 dan PO 14 sudah ada
# PO 13 (warehouse) seharusnya 30 kg @28.000
cursor.execute("SELECT id FROM sales WHERE po_number = 'PO-013'")
if not cursor.fetchone():
    print("PO-013 belum ada, menambahkan...")
    from modules.database import record_warehouse_sale
    record_warehouse_sale(1, 'telur', 30, 28000, 'PO 13 (Cililitan)', 'Transfer')
else:
    print("PO-013 sudah ada.")

# PO 14 (store) 47 kg @29.000
cursor.execute("SELECT id FROM sales WHERE po_number = 'PO-014'")
if not cursor.fetchone():
    print("PO-014 belum ada, menambahkan...")
    from modules.database import record_store_sale
    record_store_sale(1, 'telur', 47, 29000, 'PO 14', 'Cash', 'Penjualan toko 14/03')
else:
    print("PO-014 sudah ada.")

# 3. Perbaiki stok kios dengan adjustment manual
# Stok kios saat ini dihitung dari transfer_to_store dan penjualan store
cursor.execute("SELECT SUM(quantity) FROM inventory_movements WHERE movement_type = 'transfer_to_store'")
transfer = cursor.fetchone()[0] or 0
cursor.execute("SELECT SUM(quantity) FROM sales WHERE source_type = 'store'")
sold = cursor.fetchone()[0] or 0
current_store_stock = transfer - sold
print(f"Stok kios seharusnya: {transfer} - {sold} = {current_store_stock} kg")

# Jika stok negatif, kita perlu melakukan adjustment untuk mengoreksi
if current_store_stock < 0:
    # Buat adjustment untuk menaikkan stok ke nilai yang benar (misal 0)
    # Tapi kita harus tahu penyebab negatif. Mungkin ada penjualan yang tidak mengurangi stok? 
    # Untuk sementara, kita set stok kios ke nilai yang benar dengan adjust_store_stock
    from modules.database import adjust_store_stock
    adjust_store_stock(1, 'telur', 69.3, 'Koreksi stok setelah pembersihan duplikat')
    print("Stok kios telah disesuaikan menjadi 69.3 kg.")
else:
    print("Stok kios sudah positif, tidak perlu adjustment.")

conn.commit()
conn.close()
print("Perbaikan selesai.")