# seed_expenses.py
import sqlite3
from modules import database

project_id = 1  # Pondok Cabe

# Data pengajuan pertama (5 Maret 2026)
expenses1 = [
    ("Peti @6000 (100 pcs)", 600000, "Peralatan"),
    ("Tray @500 (500 pcs)", 250000, "Peralatan"),
    ("Timbangan kap.300kg", 3000000, "Peralatan"),
    ("Timbangan Digital (2 unit)", 600000, "Peralatan"),
    ("Promosi (Spanduk dll)", 500000, "Promosi"),
    ("Renovasi dan peralatan", 5000000, "Renovasi"),
    ("Handphone admin", 2000000, "Peralatan"),
    ("Uang Deposit Sewa Lahan", 4500000, "Sewa"),
    ("Sewa Gudang", 75000000, "Sewa"),
    ("Sewa Kios", 9000000, "Sewa"),
]

# Data pengajuan kedua (asumsi tanggal 10 Maret 2026)
expenses2 = [
    ("Biaya Renovasi + Material", 25000000, "Renovasi"),
    ("Pembelian Kipas Angin (2)", 1000000, "Peralatan"),
    ("Pembelian Terminal listrik (2)", 200000, "Peralatan"),
    ("Pembelian Exhaust Fan (3)", 1500000, "Peralatan"),
    ("Pembelian Meja Sortir (3)", 1500000, "Peralatan"),
    ("Pembelian Kursi Sortir (3)", 100000, "Peralatan"),
    ("Pembelian white board (2)", 100000, "Peralatan"),
    ("Pembuatan Spanduk", 1500000, "Promosi"),
    ("Pembelian Gembok (5)", 750000, "Peralatan"),
]

def insert_expenses(exp_list, tgl, status='approved', approved_by='Kalila'):
    conn = database.get_connection()
    cursor = conn.cursor()
    for desc, amount, cat in exp_list:
        cursor.execute('''
            INSERT INTO operational_expenses 
            (project_id, date, description, amount, category, status, requested_by, approved_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, tgl, desc, amount, cat, status, 'Maydi', approved_by, ''))
    conn.commit()
    conn.close()
    print(f"✅ {len(exp_list)} item untuk tanggal {tgl} berhasil dimasukkan.")

if __name__ == "__main__":
    insert_expenses(expenses1, '2026-03-05')
    insert_expenses(expenses2, '2026-03-10')
    print("🎉 Semua data cash advance telah ditambahkan.")