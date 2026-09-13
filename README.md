# 📡 IDX Stock Radar

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://radar-saham-tidur.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

Web dashboard interaktif untuk memantau, menganalisis, dan mencatat pergerakan saham di Bursa Efek Indonesia (IDX / BEI) dengan prinsip: **Pantau saham, evaluasi, pantau, dan amankan profit**. Mendukung 3 kategori screener strategi (**Flow Masuk**, **Flow Masuk + Fundamental OK**, dan **Saham Tidur**), sistem target multi-level Take Profit & Stop Loss, kalkulasi hari kerja bursa, serta pencatatan histori realisasi profit/loss terpadu.

🌐 **Aplikasi Live Online**: [IDX Stock Radar · Streamlit](https://radar-saham-tidur.streamlit.app/)

---

## ✨ Fitur Utama

### 1. 👁️ Mode Publik (Viewer) vs 🔐 Mode Terproteksi (Editor)
* **Mode Viewer (Publik)**:
  * Siapa pun dapat mengakses website untuk memantau watchlist emiten secara live.
  * Memfilter saham Syariah (ISSI) dan rentang tanggal masuk/bangun.
  * Mengurutkan tabel secara interaktif (klik judul kolom untuk Ascending ⇄ Descending).
  * Mengunduh data tabel ke format `.CSV` (otomatis mengikuti filter yang aktif).
* **Mode Editor**:
  * Diproteksi password rahasia (`akubahagiasehatkayaraya` atau via Streamlit Secrets).
  * Menambah saham tidur baru ke watchlist (satuan maupun Quick Import massal).
  * Mengupdate harga live secara manual via Yahoo Finance (`.JK`).
  * Membungkus cuan (*early exit* / target TP) dengan **input catatan manual bebas (ketik sendiri)** dan memindahkannya ke tabel histori.
  * Realisasi Cut Loss / Stop Loss dengan **input catatan manual bebas**.
  * Mengedit angka TP/SL/harga/catatan dan menghapus baris data dengan sistem **centang tabel (*checkbox*)**.
  * Tombol **Backup & Restore Database JSON** di sidebar untuk menjamin data aman 100%.
  * Dilengkapi tombol **Exit / Keluar Mode Editor** untuk kembali ke mode publik dengan aman.

### 2. 🎯 Tiga Tab Hasil Screener & Status Profit / Loss
* **Tiga Kategori Screener Terpisah**:
  * **🌊 Flow Masuk**: Saham-saham yang mulai terdeteksi aliran dana besar (*smart money / broker accumulation / foreign flow*).
  * **💎 Flow Masuk + Fundamental OK**: Saham pilihan terbaik (*Golden Setup*) yang menggabungkan aliran dana aktif dan kondisi perusahaan yang sehat bebas redflag.
  * **💤 Saham Tidur**: Saham fase konsolidasi/sepi murni yang siap dipantau atau dicicil santai.
* **Kolom Status Profit / Loss (P/L)**: Menampilkan status pergerakan harga saham secara visual:
  * `🟢 Profit (+X.X%)` jika harga saham sedang mengambang di atas modal.
  * `🔴 Loss (-X.X%)` jika harga saham berada di bawah modal awal.
  * `⚪ BEP (0.0%)` jika harga saham sama persis dengan modal awal.
* **Filter Interaktif Status P/L**: Filter dropdown di atas setiap tabel untuk menyaring: `Semua Status P/L`, `🟢 Hanya Profit`, atau `🔴 Hanya Loss`.
* **Multi-Target Take Profit (TP 1, TP 2, TP 3) & Stop Loss (SL)**: Pengisian level target TP dan batas risiko manual (Rp).
* **Status Saham Dinamis**: Otomatis mendeteksi `KENA SL 🛑`, `DEKAT SL 🚨`, `MASIH TIDUR 💤`, `PROFIT 📈`, `LOSS 🔻`, `DEKAT TP 1 ⚡`, hingga `TP 1/2/3 TERCAPAI 🎯/🏆`.

### 3. 📅 Perhitungan Durasi Hold Hari Kerja (Working Days)
* Menghitung lama hold hanya pada **hari kerja aktif bursa (Senin – Jumat)**, tidak terdistorsi oleh hari libur akhir pekan (Sabtu & Minggu).

### 4. 📊 Statistik & Evaluasi Win Rate Fleksibel (Collapsible / Buka-Tutup)
* **Bisa di-Hide / Tampilkan**: Berada di expander bagian atas yang bisa dibuka atau ditutup agar layar tetap bersih dan fokus.
* **Filter Kategori Screener**: Statistik dapat difilter berdasarkan `Semua Hasil Screener`, `Flow Masuk`, `Flow Masuk + Fundamental OK`, atau `Saham Tidur`.
* **Win Rate All-Time**: Menghitung persentase kemenangan dari seluruh riwayat trade yang selesai (Win vs Loss) serta rata-rata keuntungan per trade.
* **Win Rate Bulanan Real-Time**: Otomatis default mengikuti **bulan dan tahun riil saat ini**, serta dilengkapi pemilih bulan dan tahun fleksibel untuk evaluasi historis.

### 5. 🕌 Filter & Tampilan Single-View Saham Syariah (ISSI)
* **Penanda Ringkas**: Ikon centang (**✅**) untuk saham Syariah (ISSI) dan tanda hubung (**-**) untuk Non-Syariah.
* **Layout Satu Layar (Single-View)**: Seluruh data dari Kode, Modal, Target TP/SL, Status P/L, hingga Alert langsung terbaca rapi dalam satu tampilan layar tanpa perlu scroll horizontal.

### 6. 📥 Export ke File CSV
* Tombol export instan untuk setiap tab screener (**Flow Masuk**, **Flow Masuk + Fundamental OK**, **Saham Tidur**) maupun riwayat trade selesai.
* Format UTF-8 BOM yang langsung terbaca rapi di Microsoft Excel.
* **100% mengikuti filter yang sedang diterapkan di layar**.

### 7. ⚡ Quick Import Stockbit (Dukungan Kategori Screener & Syariah/Non-Syariah)
* **Pilihan Target Kategori**: Emiten yang diimpor dapat langsung diarahkan ke tab `Flow Masuk`, `Flow Masuk + Fundamental OK`, atau `Saham Tidur`.
* **Dua Kolom Fleksibel (Kiri & Kanan)**:
  * **Kolom Kiri (🕌 Syariah ISSI)**: Hasil screener Stockbit dengan filter Stock Universe = `ISSI` (otomatis ditandai Syariah).
  * **Kolom Kanan (🏢 IHSG / Non-Syariah - Opsional)**: Hasil screener Stockbit dengan filter Universe `All Stocks` atau Non-Syariah.
* **Auto-Reset Form ke Blank**: Setelah tombol *Proses & Impor* diklik, kedua kotak teks otomatis bersih kembali (kosong/blank) sehingga siap untuk aktivitas screening berikutnya.
* **Proteksi Anti-Duplikasi (*First Entry Lock*)**: Emiten yang sudah ada di watchlist aktif tidak akan terduplikasi atau tertimpa, sehingga tanggal awal masuk dan modal harga awal tetap aman terlindungi.

### 8. 📜 Riwayat Trade Selesai (Satu Tabel Terpadu Histori Cuan & Cut Loss)
* Menggabungkan riwayat take profit (cuan) dan cut loss (stop loss) ke dalam **satu tabel tunggal** yang ringkas dan rapi.
* **Kolom Status Hasil**: Memberikan label visual jelas `🟢 Profit (+X.XX%)` atau `🔴 Loss (-X.XX%)`.
* **Filter Interaktif Lengkap**: Filter dropdown status (`Semua (Profit & Loss)`, `🟢 Hanya Profit`, `🔴 Hanya Loss`), Kategori Screener, Syariah ISSI, pencarian kode saham, dan rentang tanggal keluar/selesai.
* Dilengkapi kolom Kategori Screener untuk menganalisis strategi mana yang paling efektif.
* **Pengelolaan Penuh di Mode Editor**: Edit data, isi catatan manual, atau centang baris untuk menghapus histori.
* **Export CSV Sekali Klik**: Unduh seluruh riwayat trade selesai yang tersaring ke file `.CSV`.

### 9. 💾 Backup & Restore Database JSON (Perlindungan Data Anti-Hilang)
* **1-Click Backup**: Di sidebar saat login Editor, tersedia tombol **📥 Download stocks_data.json** untuk mengunduh seluruh database ke laptop Anda kapan saja.
* **Restore Fleksibel**: Dilengkapi fitur upload JSON cadangan dengan dukungan UTF-8 tanpa BOM.

---

## 🛠️ Struktur Proyek

```text
saham-tidur-dashboard/
├── app.py              # File utama aplikasi Streamlit
├── stocks_data.json    # Database saham aktif & histori (bisa di-commit ke GitHub)
├── requirements.txt    # Daftar pustaka Python (Streamlit, Pandas, yfinance, requests)
├── README.md           # Dokumentasi lengkap proyek
└── LICENSE             # Lisensi MIT (Open Public)
```

---

## 🚀 Cara Menjalankan di Lokal (Opsional)

Jika Anda ingin menjalankan aplikasi ini di laptop Anda:

1. **Clone atau download repository ini**:
   ```bash
   git clone https://github.com/username-anda/saham-tidur-radar.git
   cd saham-tidur-radar
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan Streamlit**:
   ```bash
   streamlit run app.py
   ```
   Aplikasi akan terbuka di browser pada alamat `http://localhost:8501`.

---

## ☁️ Cara Deploy ke Streamlit Community Cloud (Gratis)

1. Buat repository baru di [GitHub](https://github.com/) (contoh: `saham-tidur-radar`).
2. Upload file `app.py`, `stocks_data.json` (database awal agar permanen), `requirements.txt`, `README.md`, dan `LICENSE` ke repository tersebut.
3. Buka [share.streamlit.io](https://share.streamlit.io) dan login dengan akun GitHub Anda.
4. Klik **New app**, pilih repository Anda, set branch `main`, dan main file path `app.py`.
5. Klik **Deploy!** 🎈.
6. *(Opsional)* Pada menu **Settings > Secrets** di Streamlit Cloud, Anda dapat mengubah password editor default:
   ```toml
   EDITOR_PASSWORD = "password_rahasia_anda"
   ```

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [Lisensi MIT](LICENSE) — lisensi terbuka untuk publik (*open public*). Siapa pun diperbolehkan untuk menggunakan, mempelajari, mengedit, mengembangkan ulang, dan mendistribusikannya secara bebas.
