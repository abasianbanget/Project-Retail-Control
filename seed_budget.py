# seed_budget.py
import sqlite3
from modules import database

project_id = 1  # Pondok Cabe

# Data dari sheet "Toko Pd. Cabe"
budget_items = [
    # BELANJA MODAL (capex) - sekali
    ('capex', 'Peti @6000 (100 pcs)', 600000, 'once', None, 2026),
    ('capex', 'Tray @500 (500 pcs)', 250000, 'once', None, 2026),
    ('capex', 'Timbangan kap.300kg', 3000000, 'once', None, 2026),
    ('capex', 'Timbangan Digital (2 unit)', 600000, 'once', None, 2026),
    ('capex', 'Promosi (spanduk dll)', 500000, 'once', None, 2026),
    ('capex', 'Renovasi dan peralatan', 5000000, 'once', None, 2026),
    ('capex', 'Handphone admin', 2000000, 'once', None, 2026),
    ('capex', 'Uang Deposit Sewa Lahan', 4500000, 'once', None, 2026),
    
    # BIAYA OPERASIONAL BULAN PERTAMA (opex) - dianggap untuk bulan Maret 2026
    ('opex', 'Sewa Gudang (3 bulan) - bagian Maret', 25000000, 'monthly', 3, 2026),
    ('opex', 'Sewa Kios (3 bulan) - bagian Maret', 3000000, 'monthly', 3, 2026),
    ('opex', 'Listrik', 500000, 'monthly', 3, 2026),
    ('opex', 'BPP', 500000, 'monthly', 3, 2026),
    ('opex', 'BBM perbulan', 10000000, 'monthly', 3, 2026),
    ('opex', 'Tol', 5000000, 'monthly', 3, 2026),
    ('opex', 'Driver (2 orang)', 8000000, 'monthly', 3, 2026),
    ('opex', 'Helper/kenek (2 orang)', 5000000, 'monthly', 3, 2026),
    ('opex', 'Sortir dan Jaga gudang (2 orang)', 4000000, 'monthly', 3, 2026),
    ('opex', 'Penjaga Toko (2 orang)', 3000000, 'monthly', 3, 2026),
    ('opex', 'Konsultan', 10000000, 'monthly', 3, 2026),
    ('opex', 'Admin Gudang (2 orang)', 5000000, 'monthly', 3, 2026),
    
    # BIAYA OPERASIONAL BULAN KEDUA-KETIGA (opex) - untuk April, Mei 2026
    # (sebenarnya total 51jt/bulan, tapi kita bisa masukkan per item dengan nilai yang sama seperti di atas, atau total saja)
    # Agar sederhana, kita masukkan total opex bulanan 51jt sebagai satu item.
    ('opex', 'Total Biaya Operasional (Apr-Mei)', 51000000, 'monthly', 4, 2026),
    ('opex', 'Total Biaya Operasional (Apr-Mei)', 51000000, 'monthly', 5, 2026),
    
    # BIAYA MODAL (persediaan) - modal barang untuk 3 hari
    ('modal', 'Persediaan Telur (3 hari)', 124200000, 'once', None, 2026),
    
    # PROYEKSI PENDAPATAN (revenue_projection) - untuk referensi
    ('revenue_projection', 'Proyeksi Pendapatan Retail per bulan', 915000000, 'monthly', None, 2026),
    ('revenue_projection', 'Proyeksi Pendapatan Grosir per bulan', 435000000, 'monthly', None, 2026),
]

conn = database.get_connection()
cursor = conn.cursor()
for cat, desc, amt, period, month, year in budget_items:
    cursor.execute('''
        INSERT INTO budget (project_id, category, description, amount, period, month, year)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (project_id, cat, desc, amt, period, month, year))
conn.commit()
conn.close()
print("✅ Data anggaran berhasil dimasukkan.")