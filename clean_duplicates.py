import sqlite3
from modules import database

project_id = 1
warehouse_id = 1
store_id = 1

def hapus_duplikat_sales():
    """Hapus penjualan duplikat berdasarkan tanggal, jumlah, dan pelanggan, sisakan yang pertama."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Cari duplikat (berdasarkan date, source_type, quantity, customer_name)
    cursor.execute('''
        SELECT date, source_type, quantity, customer_name, MIN(id) as min_id, COUNT(*) as cnt
        FROM sales
        WHERE project_id = ? AND product_id = 'telur'
        GROUP BY date, source_type, quantity, customer_name
        HAVING COUNT(*) > 1
    ''', (project_id,))
    duplicates = cursor.fetchall()

    if not duplicates:
        print("✅ Tidak ada duplikat penjualan.")
    else:
        for dup in duplicates:
            date_str, source, qty, cust, min_id, cnt = dup
            # Hapus semua kecuali id terkecil
            cursor.execute('''
                DELETE FROM sales
                WHERE date = ? AND source_type = ? AND quantity = ? AND customer_name = ? AND id != ?
            ''', (date_str, source, qty, cust, min_id))
            print(f"🗑️ Dihapus {cnt-1} duplikat untuk {date_str} - {source} - {qty} kg - {cust}")

    conn.commit()
    conn.close()

def hapus_duplikat_inventory_movements():
    """Hapus pergerakan stok duplikat yang mencurigakan (misal adjustment ganda)."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Cari adjustment dengan notes yang sama
    cursor.execute('''
        SELECT date, movement_type, quantity, notes, MIN(id) as min_id, COUNT(*) as cnt
        FROM inventory_movements
        WHERE warehouse_id = ? AND product_id = 'telur'
        GROUP BY date, movement_type, quantity, notes
        HAVING COUNT(*) > 1
    ''', (warehouse_id,))
    duplicates = cursor.fetchall()

    if duplicates:
        for dup in duplicates:
            date_str, mtype, qty, notes, min_id, cnt = dup
            cursor.execute('''
                DELETE FROM inventory_movements
                WHERE date = ? AND movement_type = ? AND quantity = ? AND notes = ? AND id != ?
            ''', (date_str, mtype, qty, notes, min_id))
            print(f"🗑️ Dihapus {cnt-1} duplikat movement: {date_str} - {mtype} - {qty}")
    else:
        print("✅ Tidak ada duplikat inventory movements.")

    conn.commit()
    conn.close()

def hitung_ulang_stok():
    """Hitung stok gudang berdasarkan semua transaksi (tanpa adjustment) lalu set ke nilai yang benar."""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Hitung total inbound (batch)
    cursor.execute('''
        SELECT SUM(quantity) FROM inventory_movements
        WHERE warehouse_id = ? AND product_id = 'telur' AND movement_type = 'inbound'
    ''', (warehouse_id,))
    inbound = cursor.fetchone()[0] or 0

    # Hitung total outbound (semua pengurangan stok, kecuali inbound dan adjustment)
    cursor.execute('''
        SELECT SUM(quantity) FROM inventory_movements
        WHERE warehouse_id = ? AND product_id = 'telur' AND movement_type IN ('warehouse_sale', 'transfer_to_store', 'shrinkage')
    ''', (warehouse_id,))
    outbound = cursor.fetchone()[0] or 0
    outbound = -outbound  # karena quantity negatif

    stok_seharusnya = inbound - outbound
    print(f"📊 Stok gudang seharusnya: {inbound} - {outbound} = {stok_seharusnya:.2f} kg")

    # Set stok dengan adjustment (hapus semua adjustment dulu agar tidak double)
    cursor.execute("DELETE FROM inventory_movements WHERE warehouse_id = ? AND movement_type = 'adjustment'", (warehouse_id,))

    # Tambahkan adjustment yang benar
    diff = stok_seharusnya - database.get_warehouse_stock(warehouse_id, 'telur')
    if abs(diff) > 0.01:
        from datetime import datetime
        date_str = datetime.now().date().isoformat()
        cursor.execute('''
            INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, notes)
            VALUES (?, ?, ?, 'adjustment', ?, ?)
        ''', (date_str, warehouse_id, 'telur', diff, "Koreksi final setelah hapus duplikat"))
        print(f"✅ Adjustment {diff:+.2f} kg dilakukan.")
    else:
        print("✅ Stok sudah sesuai.")

    conn.commit()
    conn.close()

def koreksi_stok_toko():
    """Set stok toko ke nilai yang benar: 308.08 kg."""
    current = database.get_store_stock(store_id, 'telur')
    expected = 308.08
    if abs(current - expected) > 0.01:
        database.adjust_store_stock(store_id, 'telur', expected, "Koreksi final setelah hapus duplikat")
        print(f"✅ Stok toko disesuaikan dari {current:.2f} kg menjadi {expected:.2f} kg.")
    else:
        print("✅ Stok toko sudah sesuai.")

if __name__ == "__main__":
    print("🚀 Membersihkan duplikasi...")
    hapus_duplikat_sales()
    hapus_duplikat_inventory_movements()
    print("📊 Menghitung ulang stok...")
    hitung_ulang_stok()
    koreksi_stok_toko()
    print("🎉 Selesai.")