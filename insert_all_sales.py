import sqlite3
from modules.database import get_connection
from datetime import date

def reset_and_insert():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Hapus semua data penjualan (sales) dan pergerakan stok yang terkait dengan penjualan
    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM inventory_movements WHERE movement_type IN ('warehouse_sale', 'outbound')")
    # Reset stok toko juga? Jangan, karena transfer masih ada.
    # Tapi kita perlu mengembalikan stok toko ke nilai awal (transfer saja)
    cursor.execute("UPDATE store_inventory SET quantity = (SELECT SUM(quantity) FROM inventory_movements WHERE movement_type = 'transfer_to_store')")
    print("Data penjualan lama dihapus.")
    
    conn.commit()
    
    # Sekarang insert ulang semua penjualan dengan urutan yang benar
    from modules.database import record_warehouse_sale, record_store_sale
    
    warehouse_id = 1
    store_id = 1
    product_id = 'telur'
    
    # Fungsi bantu
    def add_warehouse(tgl, qty, harga, cust, metode='Transfer'):
        po = record_warehouse_sale(warehouse_id, product_id, qty, harga, cust, metode)
        print(f"✅ {po} - Warehouse - {qty} kg @ Rp {harga} - {cust}")
    
    def add_store(tgl, qty, harga, cust, metode='Cash', notes=''):
        po = record_store_sale(store_id, product_id, qty, harga, cust, metode, notes)
        print(f"✅ {po} - Store - {qty} kg @ Rp {harga} - {cust} | {notes}")
    
    # Data dalam urutan kronologis
    sales = [
        # PO 1-4
        ('2026-03-08', 30, 30000, 'PO 1', 'warehouse'),
        ('2026-03-09', 20, 30000, 'PO 2', 'warehouse'),
        ('2026-03-10', 43, 30000, 'PO 3', 'store'),
        ('2026-03-11', 32, 30000, 'PO 4', 'store'),
        # PO 5
        ('2026-03-11', 30, 30000, 'PO 5', 'warehouse'),
        # PO 6-8 (gunakan harga 28000 sesuai pembayaran)
        ('2026-03-12', 30, 28000, 'PO 6', 'warehouse'),
        ('2026-03-12', 30, 28000, 'PO 7', 'warehouse'),
        ('2026-03-12', 60, 28000, 'PO 8', 'warehouse'),
        # PO 9-10
        ('2026-03-12', 15, 29000, 'PO 9', 'store'),
        ('2026-03-12', 19.3, 30000, 'PO 10', 'store'),
        # Telur retak (73 butir)
        ('2026-03-12', 3.65, 20000, 'Telur Retak', 'store'),
        # PO 11
        ('2026-03-13', 500, 28000, 'PO 11 (DP 7jt, lunas 18/03)', 'warehouse'),
        # PO 12
        ('2026-03-13', 29.5, 29000, 'PO 12', 'store'),
        # Telur pecah (25 butir)
        ('2026-03-13', 1.25, 20000, 'Telur Pecah', 'store'),
        # PO 13
        ('2026-03-14', 30, 28000, 'PO 13 (Cililitan)', 'warehouse'),
        # PO 14
        ('2026-03-14', 47, 29000, 'PO 14', 'store'),
    ]
    
    print("\nMemasukkan data penjualan...")
    for tgl, qty, harga, cust, typ in sales:
        if typ == 'warehouse':
            add_warehouse(tgl, qty, harga, cust)
        else:
            add_store(tgl, qty, harga, cust, notes='')
    
    print("\n🎉 Semua data berhasil dimasukkan ulang.")

if __name__ == "__main__":
    # Backup dulu!
    print("PERINGATAN: Script ini akan menghapus semua data penjualan yang ada dan menggantinya dengan data baru.")
    confirm = input("Apakah Anda yakin? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_and_insert()
    else:
        print("Dibatalkan.")