# sync_excel.py
import pandas as pd
from datetime import datetime
import os
from modules import database

def sync_to_excel():
    """Mengekspor data dari database ke file Excel MASTER_PROJECT_CONTROL_2026.xlsx"""
    master_path = "MASTER_PROJECT_CONTROL_2026.xlsx"
    
    # Ambil data dari database
    batches = database.get_all_batches()
    project_id = 1  # default Pondok Cabe
    fixed_costs = database.get_fixed_costs(project_id)
    var_costs = database.get_variable_costs(project_id)
    sales_summary = database.get_sales_summary()
    
    with pd.ExcelWriter(master_path, engine='openpyxl') as writer:
        # Sheet Inventory
        inventory_data = []
        # contoh data manual, bisa diambil dari inventory_movements
        inventory_df = pd.DataFrame(inventory_data)
        inventory_df.to_excel(writer, sheet_name='Master_Inventory', index=False)
        
        # Sheet Sales Margin
        sales_data = []
        if sales_summary:
            for s in sales_summary:
                sales_data.append({
                    'Tanggal': s['date'],
                    'Sumber': s['source_type'],
                    'Qty (Kg)': s['total_qty'],
                    'Pendapatan': s['total_revenue']
                })
        sales_df = pd.DataFrame(sales_data)
        sales_df.to_excel(writer, sheet_name='Sales_Summary', index=False)
        
        # Sheet Batches
        if batches:
            batches_df = pd.DataFrame(batches)
            batches_df.to_excel(writer, sheet_name='Batches', index=False)
        
        # Sheet Fixed Costs
        if fixed_costs:
            fixed_df = pd.DataFrame(fixed_costs)
            fixed_df.to_excel(writer, sheet_name='FixedCosts', index=False)
        
        # Sheet Variable Costs
        if var_costs:
            var_df = pd.DataFrame(var_costs)
            var_df.to_excel(writer, sheet_name='VariableCosts', index=False)
    
    print(f"✅ Excel sync completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    sync_to_excel()