# Project Finance Dashboard - PALUGADA

Aplikasi dashboard keuangan untuk proyek penjualan telur (Pondok Cabe) dengan fitur:
- Input transaksi harian via Streamlit atau Telegram Bot.
- Perhitungan laba harian dan bulanan.
- Breakdown biaya tetap & variabel.
- Alokasi dana operasional berdasarkan laba bulan sebelumnya.
- Tampilan premium ala Power BI.

## Persyaratan
- Python 3.11 atau 3.12
- Install dependensi: `pip install -r requirements.txt`

## Struktur File
- `app.py` : Dashboard utama Streamlit.
- `bot.py` : Telegram bot untuk input cepat.
- `config.py` : Konfigurasi token, path, data awal.
- `init_db.py` : Inisialisasi database dan data default.
- `modules/` : Berisi modul database, perhitungan, utilitas.
- `data/finance.db` : Database SQLite (akan dibuat otomatis).

## Cara Menjalankan
1. **Inisialisasi database**:
   ```bash
   python init_db.py