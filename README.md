# 📡 IDX Stock Radar

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://radar-saham-tidur.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

Web dashboard interaktif untuk memantau, menganalisis, dan mencatat pergerakan saham di Bursa Efek Indonesia (IDX / BEI) dengan prinsip: **Pantau saham, evaluasi, pantau, dan amankan profit**. Dilengkapi integrasi langsung **Google Sheets Live Sync**, kalender bursa interaktif multi-saham, visualisasi sinyal confluence, deteksi frekuensi kemunculan screener, dan sistem manajemen watchlist terpadu.

🌐 **Aplikasi Live Online**: [IDX Stock Radar · Streamlit](https://radar-saham-tidur.streamlit.app/)

---

## ✨ Fitur Utama

### 1. 🔗 Auto-Sync & Integrasi Google Sheets (Live Data Linking)
* **Auto-Sync Otomatis**: Setiap kali web dibuka atau sesi browser di-refresh, sistem otomatis menarik dan menyinkronkan data terbaru dari tautan Google Sheets tanpa perlu upload file manual lagi.
* **Mendukung 2 Sumber Spreadsheet Sekaligus**:
  * 📈 **Screener Flow**: Menampung emiten dengan aliran dana masuk / akumulasi volume.
  * 💤 **Screener Saham Tidur**: Menampung emiten fase konsolidasi / baru bangun tidur.
* **Tombol Sinkronisasi Cepat (1-Click Sync)**:
  * Tombol **`📥 Sinkronkan Data dari Google Sheets`** di bagian atas mode Viewer.
  * Tombol **`📥 Sync GSheets`** di header Mode Editor.
* **Parser Cerdas Spreadsheet**:
  * Mendukung sel tanggal gabungan (*merged/blank cells*).
  * Mengharmonisasikan ragam format tanggal (`DD/MM/YYYY`, `MM/DD/YYYY`, tahun 2 digit).
  * Otomatis memisahkan saham aktif vs saham berstatus `Done`.
  * Mengakumulasikan hitungan kemunculan harian (*multi-hit dates*).
* **Konfigurasi URL Fleksibel**: URL Google Sheets dapat dilihat, diuji (*test connection*), atau diubah kapan saja melalui tab **`🔗 Sinkronisasi Google Sheets`** pada panel Mode Editor.

### 2. 📅 Kalender View Multi-Saham Interaktif (Senin - Minggu)
* **Multi-Select Saham Sekaligus**: Anda dapat mengetik dan memilih satu, dua, atau banyak saham sekaligus dari daftar pencarian dropdown untuk dibandingkan di dalam satu kalender.
* **Kalender Format Bursa (Senin - Minggu)**:
  * Susunan hari Senin sampai Jumat, dengan penanda khusus akhir pekan (*Sabtu & Minggu - Libur Bursa*).
  * **Highlight Tanggal Screener**: Setiap hari kemunculan ditandai dengan badge kategori screener (`🌊 Flow Masuk`, `💤 Saham Tidur`), harga penutupan, dan keterangan pergerakan.
  * Jika beberapa saham terdeteksi di hari yang sama, kartu kalender memuat badge untuk setiap saham terpilih secara rapi.
* **Navigasi Waktu Fleksibel**: Tombol **◀ Sebelumnya**, **Berikutnya ▶**, dropdown pemilihan Bulan/Tahun, serta tombol pintas **📅 Bulan Ini**.
* **Rekap Tabular Detail**: Menampilkan tabel rangkuman seluruh tanggal kemunculan saham terpilih beserta harga masuk dan kategorinya.

### 3. 🔥 Sinyal & Indikator Screener Modern
* **Multi-Screener Confluence (Sinyal Berlapis)**: Menampilkan kartu interaktif emiten yang muncul bersamaan di lebih dari satu kategori screener (misal: *Saham Tidur + Flow Masuk*).
* **⚡ Sering Terdeteksi Screener (Multi-Hit Tracker)**: Menampilkan kartu ringkasan emiten yang terdeteksi berulang kali di berbagai tanggal screener lengkap dengan jumlah kemunculan dan tanggal-tanggalnya.
* **Desain Kartu Badge Ringkas**: Menggantikan teks panjang berantakan dengan kartu visual yang bersih, menarik, dan mudah dipindai mata.

### 4. 👁️ Mode Publik (Viewer) vs 🔐 Mode Terproteksi (Editor)
* **Mode Viewer (Publik)**:
  * Akses cepat dan aman untuk memantau watchlist emiten secara live.
  * Kalender View multi-saham.
  * Filter saham Syariah (ISSI) dan rentang tanggal.
  * Mengurutkan tabel interaktif (klik judul kolom untuk Ascending ⇄ Descending).
  * Ekspor data tabel ke file `.CSV` (mengikuti filter aktif).
* **Mode Editor**:
  * Diproteksi password rahasia (bisa diatur via Streamlit Secrets).
  * Update harga live dari bursa secara manual via Yahoo Finance (`.JK`).
  * Tambah/edit saham baru, kelola status, dan realisasi keuntungan/cut loss.
  * Tab khusus **Upload Excel / CSV** jika ingin memasukkan file manual.
  * Tombol **Backup & Restore Database JSON** untuk keamanan data 100%.

### 5. 🎯 Tabel Screener Bersih & Fokus
* **Penyajian Data Rapi**: Kolom-kolom disederhanakan agar fokus pada evaluasi utama:
  * Kode Emiten, Status Syariah (ISSI), Tanggal Masuk, Frekuensi Muncul (Icon `🌱`, `⚡`, `🔥`), Durasi Hold (Hari Kerja Bursa), Harga Awal, Harga Terkini, Floating Gain (%), Keterangan, dan Status Posisi.
* **Filter Interaktif Lengkap**: Filter status posisi (`Semua`, `📈 Profit`, `🔻 Loss`, `⚖️ BEP`), filter frekuensi hit, filter tanggal, dan pencarian cepat kode emiten.

### 6. 🕌 Dukungan Saham Syariah (ISSI)
* Penanda visual ringkas ikon centang (**✅**) untuk saham Syariah (ISSI) dan tanda hubung (**-**) untuk Non-Syariah.
* Tombol filter satu klik untuk hanya menampilkan saham-saham Syariah.

---

## 🛠️ Struktur Proyek

```text
saham-tidur-dashboard/
├── app.py                # File utama aplikasi Streamlit
├── stocks_data.json      # Database lokal saham aktif & histori
├── gsheet_config.json    # Konfigurasi URL Google Sheets yang terhubung
├── requirements.txt      # Daftar dependensi Python (streamlit, pandas, yfinance, openpyxl, dll.)
├── README.md             # Dokumentasi lengkap proyek
├── LICENSE               # Lisensi MIT (Open Source)
└── .gitignore            # Pengaturan file git ignore
```

---

## 🚀 Cara Menjalankan di Lokal (Local Setup)

1. **Clone repository ini**:
   ```bash
   git clone https://github.com/username-anda/saham-tidur-radar.git
   cd saham-tidur-radar
   ```

2. **Buat virtual environment (opsional tapi disarankan)**:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate   # Windows
   # source .venv/bin/activate # Linux/Mac
   ```

3. **Install dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi Streamlit**:
   ```bash
   streamlit run app.py
   ```
   Aplikasi akan terbuka otomatis di browser Anda pada alamat `http://localhost:8501`.

---

## ☁️ Panduan Deploy ke Streamlit Community Cloud (Gratis)

1. **Upload ke GitHub**:
   Upload file-file berikut ke repository GitHub Anda:
   - `app.py`
   - `stocks_data.json`
   - `gsheet_config.json`
   - `requirements.txt`
   - `README.md`
   - `LICENSE`
2. **Koneksikan ke Streamlit Community Cloud**:
   - Buka [share.streamlit.io](https://share.streamlit.io) dan masuk dengan akun GitHub Anda.
   - Klik **New app**, pilih repository dan branch Anda (`main`), lalu isi *Main file path* dengan `app.py`.
   - Klik **Deploy!** 🎈.
3. **Konfigurasi Password Editor (Streamlit Secrets)**:
   - Di dashboard aplikasi Anda di Streamlit Cloud, buka **App Settings** > **Secrets**.
   - Tambahkan kunci password:
     ```toml
     EDITOR_PASSWORD = "password_rahasia_pilihan_anda"
     ```

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [Lisensi MIT](LICENSE) — bebas digunakan, dikembangkan, dan dimodifikasi secara terbuka.
