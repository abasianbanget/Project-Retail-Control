# init_db.py
import sqlite3
import os
from config import DB_PATH, DEFAULT_PROJECT, DEFAULT_FIXED_COSTS, DEFAULT_VARIABLE_COSTS

def init_db():
    # Buat folder data jika belum ada
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tabel proyek
    c.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        target_volume_per_day REAL,
        hpp REAL,
        selling_price REAL,
        operational_allocation_percent REAL
    )
    ''')
    
    # Tabel biaya tetap
    c.execute('''
    CREATE TABLE IF NOT EXISTS fixed_costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        description TEXT,
        amount REAL,
        frequency TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    ''')
    
    # Tabel biaya variabel
    c.execute('''
    CREATE TABLE IF NOT EXISTS variable_costs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        description TEXT,
        estimated_monthly REAL,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    ''')
    
    # Tabel transaksi harian
    c.execute('''
    CREATE TABLE IF NOT EXISTS daily_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        date TEXT,
        volume_sold REAL,
        revenue REAL,
        variable_expenses TEXT,
        notes TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    ''')
    
    # Tabel alokasi bulanan
    c.execute('''
    CREATE TABLE IF NOT EXISTS monthly_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        month TEXT,
        net_profit REAL,
        allocated_amount REAL,
        remaining_balance REAL,
        UNIQUE(project_id, month),
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
    ''')
    
    # Cek apakah proyek default sudah ada
    c.execute("SELECT id FROM projects WHERE name = ?", (DEFAULT_PROJECT['name'],))
    if not c.fetchone():
        # Insert proyek default
        c.execute('''
            INSERT INTO projects (name, target_volume_per_day, hpp, selling_price, operational_allocation_percent)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            DEFAULT_PROJECT['name'],
            DEFAULT_PROJECT['target_volume_per_day'],
            DEFAULT_PROJECT['hpp'],
            DEFAULT_PROJECT['selling_price'],
            DEFAULT_PROJECT['operational_allocation_percent']
        ))
        project_id = c.lastrowid
        
        # Insert fixed costs
        for fc in DEFAULT_FIXED_COSTS:
            c.execute('''
                INSERT INTO fixed_costs (project_id, description, amount, frequency)
                VALUES (?, ?, ?, ?)
            ''', (project_id, fc['description'], fc['amount'], fc['frequency']))
        
        # Insert variable costs
        for vc in DEFAULT_VARIABLE_COSTS:
            c.execute('''
                INSERT INTO variable_costs (project_id, description, estimated_monthly)
                VALUES (?, ?, ?)
            ''', (project_id, vc['description'], vc['estimated_monthly']))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()