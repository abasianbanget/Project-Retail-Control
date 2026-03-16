# final_audit.py
import sqlite3
from datetime import datetime
from modules import database

project_id = 1
warehouse_id = 1
store_id = 1
product_id_telur = 'telur'
product_id_pecah = 'telur_pecah'

def bersihkan_data_kacau():
    """Hapus semua data sales yang bermasalah (quantity negatif, product_id salah, duplikat)"""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Hapus semua sales dengan quantity negatif
    cursor.execute("DELETE FROM sales WHERE quantity < 0")
    print("🗑️ Semua penjualan dengan quantity negatif dihapus.")

    # Hapus sales dengan product_id 'telur_pecah' (karena akan dicatat via shrinkage)
    cursor.execute("DELETE FROM sales WHERE product_id = ?", (product_id_pecah,))
    print("🗑️ Semua penjualan telur pecah yang salah dihapus.")

    # Hapus duplikat berdasarkan tanggal, source, quantity, customer (sisakan yang pertama)
    cursor.execute('''
        DELETE FROM sales
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM sales
            WHERE project_id = ?
            GROUP BY date, source_type, quantity, customer_name
        )
    ''', (project_id,))
    print("🗑️ Duplikat penjualan dihapus (menyisakan satu per grup).")

    # Hapus semua inventory_movements yang bukan inbound/transfer (karena akan dihitung ulang)
    cursor.execute('''
        DELETE FROM inventory_movements
        WHERE warehouse_id = ? AND movement_type NOT IN ('inbound', 'transfer_to_store')
    ''', (warehouse_id,))
    print("🗑️ Semua pergerakan stok selain inbound/transfer dihapus (akan dihitung ulang).")

    conn.commit()
    conn.close()

def tambah_data_yang_benar():
    """Masukkan semua penjualan, transfer, dan shrinkage yang benar berdasarkan rekap"""

    # 1. Transfer ke toko (sudah ada di inventory_movements, tapi kita pastikan)
    # Sebenarnya transfer sudah ada, tapi kita akan biarkan karena tidak dihapus.
    # Jika belum ada, kita tambahkan.
    conn = database.get_connection()
    cursor = conn.cursor()

    # Cek apakah transfer 260 kg dan 240 kg sudah ada
    for tgl, qty in [("2026-03-10", 260), ("2026-03-14", 240)]:
        cursor.execute('''
            SELECT id FROM inventory_movements
            WHERE date = ? AND warehouse_id = ? AND movement_type = 'transfer_to_store' AND quantity = -?
        ''', (tgl, warehouse_id, qty))
        if not cursor.fetchone():
            # Tambahkan
            cursor.execute('''
                INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, notes)
                VALUES (?, ?, ?, 'transfer_to_store', ?, ?)
            ''', (tgl, warehouse_id, product_id_telur, -qty, f"Transfer ke toko {qty} kg"))
            # Update stok toko
            cursor.execute('''
                INSERT INTO store_inventory (store_id, product_id, quantity, last_updated)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(store_id, product_id) DO UPDATE
                SET quantity = quantity + excluded.quantity, last_updated = excluded.last_updated
            ''', (store_id, product_id_telur, qty, tgl))
            print(f"✅ Transfer {qty} kg tgl {tgl} ditambahkan.")

    # 2. Penjualan Gudang
    warehouse_sales = [
        ("2026-03-08", 30, 29000, "PO 1", "Transfer", True),
        ("2026-03-09", 20, 29000, "PO 2", "Transfer", True),
        ("2026-03-11", 30, 29000, "PO 5", "Transfer", False),  # belum lunas
        ("2026-03-12", 30, 29000, "PO 6", "Transfer", True),
        ("2026-03-12", 30, 29000, "PO 7", "Transfer", True),
        ("2026-03-12", 60, 29000, "PO 8", "Transfer", False),
        ("2026-03-13", 500, 28000, "PO 11", "Transfer", True),  # dp 7jt, dianggap lunas? sementara lunas
        ("2026-03-14", 30, 29000, "PO 13", "Transfer", True),
        ("2026-03-15", 105, 29000, "Agen Pamulang", "Transfer", False),
        ("2026-03-15", 60, 29000, "Cililitan", "Transfer", False),
        ("2026-03-15", 15, 29000, "Warung Madura", "Transfer", False),
    ]
    for tgl, qty, harga, cust, metode, lunas in warehouse_sales:
        # Cek apakah sudah ada
        cursor.execute('''
            SELECT id FROM sales WHERE date = ? AND source_type = 'warehouse' AND quantity = ? AND customer_name = ?
        ''', (tgl, qty, cust))
        if not cursor.fetchone():
            # Tambahkan penjualan
            po = database.get_next_po_number()  # kita perlu fungsi ini, tapi kita bisa generate manual
            # Untuk sementara, kita generate PO number sendiri
            cursor.execute('''
                INSERT INTO sales (po_number, date, project_id, source_type, source_id, product_id, quantity, price_per_unit, total_amount, payment_method, customer_name, notes)
                VALUES (?, ?, ?, 'warehouse', ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"PO-WH-{cust.replace(' ','')}", tgl, project_id, warehouse_id, product_id_telur, qty, harga, qty*harga, metode, cust, ""))
            # Tambahkan inventory movement (keluar)
            cursor.execute('''
                INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, notes)
                VALUES (?, ?, ?, 'warehouse_sale', ?, ?)
            ''', (tgl, warehouse_id, product_id_telur, -qty, f"Penjualan ke {cust}"))
            print(f"✅ Penjualan gudang {cust} {qty} kg tgl {tgl} ditambahkan.")
        else:
            print(f"⏩ Penjualan gudang {cust} {qty} kg tgl {tgl} sudah ada.")

    # 3. Penjualan Toko
    store_sales = [
        ("2026-03-10", 43, 29500, "PO 3", "Cash+QR", True),
        ("2026-03-11", 32, 28500, "PO 4", "Cash", True),
        ("2026-03-12", 15, 29000, "PO 9", "Cash", True),
        ("2026-03-12", 19.3, 29000, "PO 10", "Cash", True),
        ("2026-03-13", 29.5, 29000, "PO 12", "Cash", True),
        ("2026-03-14", 47, 29000, "PO 14", "Cash+QR", True),
        ("2026-03-15", 15, 29000, "PO 15", "Cash", True),   # ✅
        ("2026-03-15", 150, 29000, "PO 16", "Cash", False), # belum lunas
        ("2026-03-15", 38.5, 29000, "PO 17", "Cash", True), # ✅
    ]
    for tgl, qty, harga, cust, metode, lunas in store_sales:
        cursor.execute('''
            SELECT id FROM sales WHERE date = ? AND source_type = 'store' AND quantity = ? AND customer_name = ?
        ''', (tgl, qty, cust))
        if not cursor.fetchone():
            # Tambahkan penjualan
            cursor.execute('''
                INSERT INTO sales (po_number, date, project_id, source_type, source_id, product_id, quantity, price_per_unit, total_amount, payment_method, customer_name, notes)
                VALUES (?, ?, ?, 'store', ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"PO-ST-{cust.replace(' ','')}", tgl, project_id, store_id, product_id_telur, qty, harga, qty*harga, metode, cust, ""))
            # Kurangi stok toko
            cursor.execute('''
                UPDATE store_inventory SET quantity = quantity - ?, last_updated = ?
                WHERE store_id = ? AND product_id = ?
            ''', (qty, tgl, store_id, product_id_telur))
            print(f"✅ Penjualan toko {cust} {qty} kg tgl {tgl} ditambahkan.")
        else:
            print(f"⏩ Penjualan toko {cust} {qty} kg tgl {tgl} sudah ada.")

    # 4. Shrinkage (telur pecah)
    shrinkages = [
        ("2026-03-12", 73, "Telur retak"),
        ("2026-03-13", 25, "Telur pecah"),
    ]
    for tgl, butir, note in shrinkages:
        cursor.execute('''
            SELECT id FROM shrinkage_records WHERE date = ? AND quantity_butir = ?
        ''', (tgl, butir))
        if not cursor.fetchone():
            # Gunakan fungsi record_shrinkage (tapi kita perlu implementasi di sini)
            kg = butir / database.SHRINKAGE_CONVERSION
            total = butir * 1000
            # Kurangi stok toko
            cursor.execute('''
                UPDATE store_inventory SET quantity = quantity - ?, last_updated = ?
                WHERE store_id = ? AND product_id = ?
            ''', (kg, tgl, store_id, product_id_telur))
            # Catat inventory movement
            cursor.execute('''
                INSERT INTO inventory_movements (date, warehouse_id, store_id, product_id, movement_type, quantity, notes)
                VALUES (?, NULL, ?, ?, 'shrinkage', ?, ?)
            ''', (tgl, store_id, product_id_telur, -kg, note))
            # Catat penjualan telur pecah (produk khusus)
            po = f"SHR-{butir}-{tgl.replace('-','')}"
            cursor.execute('''
                INSERT INTO sales (po_number, date, project_id, source_type, source_id, product_id, quantity, price_per_unit, total_amount, payment_method, customer_name, notes)
                VALUES (?, ?, ?, 'store', ?, ?, ?, ?, ?, 'Cash', 'Telur Pecah', ?)
            ''', (po, tgl, project_id, store_id, product_id_pecah, butir, 1000, total, note))
            # Catat shrinkage_records
            cursor.execute('''
                INSERT INTO shrinkage_records (project_id, date, store_id, quantity_butir, price_per_unit, total_amount, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (project_id, tgl, store_id, butir, 1000, total, note))
            print(f"✅ Shrinkage {butir} butir tgl {tgl} ditambahkan.")
        else:
            print(f"⏩ Shrinkage {butir} butir tgl {tgl} sudah ada.")

    conn.commit()
    conn.close()

def hitung_ulang_stok():
    """Hitung ulang stok gudang dan toko berdasarkan data yang valid"""
    conn = database.get_connection()
    cursor = conn.cursor()

    # Stok gudang: inbound - outbound (warehouse_sale + transfer_to_store)
    cursor.execute('''
        SELECT SUM(CASE WHEN movement_type = 'inbound' THEN quantity ELSE 0 END) as inbound,
               SUM(CASE WHEN movement_type IN ('warehouse_sale', 'transfer_to_store') THEN quantity ELSE 0 END) as outbound
        FROM inventory_movements
        WHERE warehouse_id = ? AND product_id = ?
    ''', (warehouse_id, product_id_telur))
    row = cursor.fetchone()
    inbound = row[0] or 0
    outbound = row[1] or 0
    stok_gudang = inbound + outbound  # outbound negatif

    # Update stok gudang via adjustment (hapus semua adjustment dulu)
    cursor.execute("DELETE FROM inventory_movements WHERE warehouse_id = ? AND movement_type = 'adjustment'", (warehouse_id,))
    current_stok = database.get_warehouse_stock(warehouse_id, product_id_telur)
    diff = stok_gudang - current_stok
    if abs(diff) > 0.01:
        date_str = datetime.now().date().isoformat()
        cursor.execute('''
            INSERT INTO inventory_movements (date, warehouse_id, product_id, movement_type, quantity, notes)
            VALUES (?, ?, ?, 'adjustment', ?, ?)
        ''', (date_str, warehouse_id, product_id_telur, diff, "Koreksi audit final"))
        print(f"✅ Adjustment gudang {diff:+.2f} kg dilakukan. Stok sekarang {stok_gudang:.2f} kg.")
    else:
        print(f"✅ Stok gudang sudah sesuai: {current_stok:.2f} kg.")

    # Stok toko: dari transfer - penjualan toko - shrinkage
    cursor.execute('''
        SELECT SUM(quantity) FROM store_inventory WHERE store_id = ? AND product_id = ?
    ''', (store_id, product_id_telur))
    current_stok_toko = cursor.fetchone()[0] or 0

    # Hitung ulang stok toko dari awal
    cursor.execute('''
        SELECT SUM(-quantity) FROM inventory_movements
        WHERE store_id = ? AND movement_type = 'shrinkage'
    ''', (store_id,))
    shrinkage_total = cursor.fetchone()[0] or 0

    cursor.execute('''
        SELECT SUM(quantity) FROM sales
        WHERE source_type = 'store' AND product_id = ? AND project_id = ?
    ''', (product_id_telur, project_id))
    sales_toko = cursor.fetchone()[0] or 0

    cursor.execute('''
        SELECT SUM(quantity) FROM inventory_movements
        WHERE warehouse_id = ? AND movement_type = 'transfer_to_store'
    ''', (warehouse_id,))
    transfer_total = cursor.fetchone()[0] or 0
    transfer_total = -transfer_total  # karena negatif

    stok_toko_seharusnya = transfer_total - sales_toko - shrinkage_total

    if abs(current_stok_toko - stok_toko_seharusnya) > 0.01:
        # Update store_inventory langsung
        cursor.execute('''
            UPDATE store_inventory SET quantity = ?, last_updated = ?
            WHERE store_id = ? AND product_id = ?
        ''', (stok_toko_seharusnya, datetime.now().date().isoformat(), store_id, product_id_telur))
        print(f"✅ Stok toko dikoreksi dari {current_stok_toko:.2f} kg menjadi {stok_toko_seharusnya:.2f} kg.")
    else:
        print(f"✅ Stok toko sudah sesuai: {current_stok_toko:.2f} kg.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("🚀 Memulai audit final...")
    bersihkan_data_kacau()
    tambah_data_yang_benar()
    hitung_ulang_stok()
    print("🎉 Selesai. Silakan jalankan ulang aplikasi.")