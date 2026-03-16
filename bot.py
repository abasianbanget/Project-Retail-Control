# bot.py
import asyncio
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime

# Import modul lokal
import config
from modules import database

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Ambil token dari config
TOKEN = config.TELEGRAM_TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Selamat datang di Bot Keuangan Pondok Cabe.\n\n"
        "Perintah yang tersedia:\n"
        "/tambah <volume> <harga> <bbm> <tol> <listrik> [catatan]\n"
        "Contoh: /tambah 1500 30500 350000 170000 40000 stok habis\n\n"
        "/ringkasan - Lihat ringkasan hari ini\n"
        "/alokasi - Lihat dana operasional tersedia"
    )

async def tambah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 5:
            await update.message.reply_text(
                "❌ Format salah. Gunakan:\n"
                "/tambah volume harga bbm tol listrik [catatan]"
            )
            return
        
        volume = float(args[0])
        harga = float(args[1])
        bbm = float(args[2])
        tol = float(args[3])
        listrik = float(args[4])
        catatan = " ".join(args[5:]) if len(args) > 5 else ""
        
        revenue = volume * harga
        var_expenses = {"bbm": bbm, "tol": tol, "listrik": listrik}
        
        # Ambil proyek default (Pondok Cabe)
        projects = database.get_all_projects()
        if not projects:
            await update.message.reply_text("❌ Tidak ada proyek di database.")
            return
        project_id = projects[0]['id']  # Ambil proyek pertama
        
        tanggal = datetime.now().date()
        database.add_daily_transaction(project_id, tanggal, volume, revenue, var_expenses, catatan)
        
        await update.message.reply_text(
            f"✅ Transaksi tersimpan!\n"
            f"Tanggal: {tanggal}\n"
            f"Volume: {volume} kg\n"
            f"Pendapatan: Rp {revenue:,.0f}\n"
            f"Biaya variabel: Rp {bbm+tol+listrik:,.0f}"
        )
    except Exception as e:
        logger.error(f"Error in tambah: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def ringkasan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        projects = database.get_all_projects()
        if not projects:
            await update.message.reply_text("❌ Tidak ada proyek.")
            return
        project_id = projects[0]['id']
        
        tanggal = datetime.now().date()
        txns = database.get_daily_transactions(project_id, tanggal, tanggal)
        if not txns:
            await update.message.reply_text(f"Belum ada transaksi untuk {tanggal}.")
            return
        
        total_revenue = sum(t['revenue'] for t in txns)
        total_var = 0
        for t in txns:
            expenses = json.loads(t['variable_expenses'])
            total_var += sum(expenses.values())
        
        # Fixed cost harian
        fixed_costs = database.get_fixed_costs(project_id)
        daily_fixed = sum(fc['amount']/30 for fc in fixed_costs if fc['frequency']=='monthly') + \
                      sum(fc['amount']/365 for fc in fixed_costs if fc['frequency']=='yearly')
        
        laba = total_revenue - total_var - daily_fixed
        
        await update.message.reply_text(
            f"📊 Ringkasan {tanggal}\n"
            f"Pendapatan: Rp {total_revenue:,.0f}\n"
            f"Biaya Variabel: Rp {total_var:,.0f}\n"
            f"Laba Bersih: Rp {laba:,.0f}"
        )
    except Exception as e:
        logger.error(f"Error in ringkasan: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def alokasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        projects = database.get_all_projects()
        if not projects:
            await update.message.reply_text("❌ Tidak ada proyek.")
            return
        project_id = projects[0]['id']
        
        bulan = datetime.now().strftime("%Y-%m")
        alloc = database.get_monthly_allocation(project_id, bulan)
        if not alloc:
            await update.message.reply_text("Belum ada data alokasi untuk bulan ini.")
            return
        
        await update.message.reply_text(
            f"💰 Alokasi Dana Operasional - {bulan}\n"
            f"Laba bulan lalu: Rp {alloc['net_profit']:,.0f}\n"
            f"Alokasi bulan ini: Rp {alloc['allocated_amount']:,.0f}\n"
            f"Sisa cadangan: Rp {alloc['remaining_balance']:,.0f}"
        )
    except Exception as e:
        logger.error(f"Error in alokasi: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("Silakan ganti TELEGRAM_TOKEN di config.py dengan token bot Anda.")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tambah", tambah))
    app.add_handler(CommandHandler("ringkasan", ringkasan))
    app.add_handler(CommandHandler("alokasi", alokasi))
    
    logger.info("🤖 Telegram Bot berjalan... Tekan Ctrl+C untuk berhenti.")
    app.run_polling()

if __name__ == "__main__":
    main()