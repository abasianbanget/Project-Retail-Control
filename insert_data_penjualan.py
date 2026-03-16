import sqlite3
from datetime import datetime
from modules import database

project_id = 1  # Pondok Cabe
warehouse_id = 1
store_id = 1

def transfer_exists(tgl_str, qty):
    """Cek apakah transfer dengan tanggal dan jumlah sudah ada (untuk menghindari duplikasi)"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM inventory_movements
        WHERE date = ? AND movement_type = 'transfer_to_store' AND quantity = -? AND warehouse_id = ?
    ''', (datetime.strptime(tgl_str, "%d/%m/%y").date().isoformat(), qty, warehouse_id))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def sale_exists(po_ref=None, tgl_str=None, qty=None, source='warehouse'):
    """Cek apakah penjualan sudah ada (berdasarkan po_number atau kombinasi)"""
    conn = database.get_connection()
    cursor = conn.cursor()
    if po_ref:
        cursor.execute("SELECT id FROM sales WHERE po_number LIKE ?", (f"%{po_ref}%",))
    else:
        date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
        cursor.execute('''
            SELECT id FROM sales
            WHERE date = ? AND source_type = ? AND quantity = ?
        ''', (date_obj.isoformat(), source, qty))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def shrinkage_exists(tgl_str, butir):
    """Cek apakah shrinkage sudah ada"""
    conn = database.get_connection()
    cursor = conn.cursor()
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    cursor.execute('''
        SELECT id FROM shrinkage_records
        WHERE date = ? AND quantity_butir = ?
    ''', (date_obj.isoformat(), butir))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def cash_deposit_exists(tgl_setor, amount):
    """Cek apakah setoran sudah ada"""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM cash_deposits
        WHERE deposit_date = ? AND amount = ?
    ''', (datetime.strptime(tgl_setor, "%d/%m/%y").date().isoformat(), amount))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def add_transfer(tgl_str, qty_kg):
    if transfer_exists(tgl_str, qty_kg):
        print(f"⏩ Transfer {qty_kg} kg tanggal {tgl_str} sudah ada, dilewati.")
        return
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    conn = database.get_connection()
    cursor = conn.cursor()
    # Catat inventory movement
    cursor.execute('''
        INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, notes)
        VALUES (?, ?, 'telur', 'transfer_to_store', ?, ?)
    ''', (date_obj.isoformat(), warehouse_id, -qty_kg, f"Transfer ke toko {qty_kg} kg"))
    # Update store_inventory
    cursor.execute('''
        INSERT INTO store_inventory (store_id, product_id, quantity, last_updated)
        VALUES (?, 'telur', ?, ?)
        ON CONFLICT(store_id, product_id) DO UPDATE
        SET quantity = quantity + excluded.quantity, last_updated = excluded.last_updated
    ''', (store_id, qty_kg, date_obj.isoformat()))
    conn.commit()
    conn.close()
    print(f"✅ Transfer {qty_kg} kg tanggal {tgl_str} dicatat.")

def add_sale(source, tgl_str, qty_kg, price, customer, payment, notes=""):
    # Cek apakah sudah ada
    if sale_exists(tgl_str=tgl_str, qty=qty_kg, source=source):
        print(f"⏩ Penjualan {source} {qty_kg} kg tanggal {tgl_str} sudah ada, dilewati.")
        return
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    if source == 'warehouse':
        database.record_warehouse_sale(project_id, warehouse_id, 'telur', qty_kg, price, customer, payment)
    else:
        database.record_store_sale(project_id, store_id, 'telur', qty_kg, price, customer, payment, notes)
    print(f"✅ Penjualan {source} {qty_kg} kg tanggal {tgl_str} dicatat.")

def add_shrinkage(tgl_str, butir, harga_per_butir=1000, notes=""):
    if shrinkage_exists(tgl_str, butir):
        print(f"⏩ Shrinkage {butir} butir tanggal {tgl_str} sudah ada, dilewati.")
        return
    date_obj = datetime.strptime(tgl_str, "%d/%m/%y").date()
    database.record_shrinkage(project_id, store_id, date_obj, butir, harga_per_butir, notes)
    print(f"✅ Shrinkage {butir} butir tanggal {tgl_str} dicatat.")

def add_cash_deposit(tgl_sale, tgl_setor, amount, status='confirmed', notes=""):
    if cash_deposit_exists(tgl_setor, amount):
        print(f"⏩ Setoran {amount} tanggal {tgl_setor} sudah ada, dilewati.")
        return
    sale_date_obj = datetime.strptime(tgl_sale, "%d/%m/%y").date()
    deposit_date_obj = datetime.strptime(tgl_setor, "%d/%m/%y").date()
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cash_deposits (project_id, sale_date, deposit_date, amount, status, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (project_id, sale_date_obj.isoformat(), deposit_date_obj.isoformat(), amount, status, notes))
    conn.commit()
    conn.close()
    print(f"✅ Setoran {amount} tanggal {tgl_setor} dicatat.")

def add_po11_sale():
    """Catat PO 11 (500kg) jika belum ada"""
    if not sale_exists(po_ref="PO 11"):
        database.record_warehouse_sale(project_id, warehouse_id, 'telur', 500, 28000, "PO 11", "Transfer")
        print("✅ Penjualan PO 11 (500kg) dicatat.")
    else:
        print("⏩ PO 11 sudah ada.")

# ===== DATA TRANSFER =====
add_transfer("10/03/26", 260)
add_transfer("14/03/26", 240)

# ===== PENJUALAN YANG BELUM TERCATAT =====
# PO 5 (11/03) 30kg warehouse
add_sale('warehouse', "11/03/26", 30, 29000, "PO 5", "Transfer")
# PO 8 (12/03) 60kg warehouse
add_sale('warehouse', "12/03/26", 60, 29000, "PO 8", "Transfer")
# PO 15/03: 105kg, 60kg, 15kg ke agen
add_sale('warehouse', "15/03/26", 105, 29200, "Agen Pamulang", "Transfer")
add_sale('warehouse', "15/03/26", 60, 29200, "Cililitan", "Transfer")
add_sale('warehouse', "15/03/26", 15, 29200, "Warung Madura Tales", "Transfer")

# ===== TELUR PECAH =====
add_shrinkage("12/03/26", 73, 1000, "Telur retak dijual 1000/butir")
add_shrinkage("13/03/26", 25, 1000, "Telur pecah dijual")

# ===== PO 11 (500kg) DAN PEMBAYARAN =====
add_po11_sale()
add_cash_deposit("13/03/26", "13/03/26", 7000000, 'confirmed', 'DP 50% PO 11')

# ===== KOREKSI STOK TOKO =====
print("\n📊 Menghitung stok toko yang benar...")
conn = database.get_connection()
cursor = conn.cursor()

# Hitung total transfer ke toko
cursor.execute('''
    SELECT SUM(-quantity) FROM inventory_movements
    WHERE warehouse_id = ? AND movement_type = 'transfer_to_store'
''', (warehouse_id,))
total_transfer = cursor.fetchone()[0] or 0

# Hitung total penjualan toko (termasuk shrinkage? shrinkage sudah mengurangi stok)
cursor.execute('''
    SELECT SUM(quantity) FROM sales
    WHERE project_id = ? AND source_type = 'store' AND product_id = 'telur'
''', (project_id,))
total_store_sales = cursor.fetchone()[0] or 0

# Hitung total shrinkage (yang mengurangi stok)
cursor.execute('''
    SELECT SUM(quantity_butir) FROM shrinkage_records WHERE project_id = ?
''', (project_id,))
total_shrinkage_butir = cursor.fetchone()[0] or 0
total_shrinkage_kg = total_shrinkage_butir / database.SHRINKAGE_CONVERSION

stok_seharusnya = total_transfer - total_store_sales - total_shrinkage_kg

# Update store_inventory
cursor.execute('''
    UPDATE store_inventory SET quantity = ?, last_updated = ?
    WHERE store_id = ? AND product_id = 'telur'
''', (stok_seharusnya, datetime.now().date().isoformat(), store_id))
conn.commit()
conn.close()

print(f"✅ Stok toko dikoreksi menjadi {stok_seharusnya:.2f} kg.")
print("\n🎉 Semua data berhasil diproses.")