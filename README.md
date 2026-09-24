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
* **Kolom Status di Ujung Tabel (Setelah TP 3)**: Menampilkan status pergerakan harga saham secara visual:
  * `📈 Profit (+X.X%)` jika harga saham sedang mengambang di atas modal.
  * `🔻 Loss (-X.X%)` jika harga saham berada di bawah modal awal.
  * `⚖️ BEP (0.0%)` jika harga saham sama persis dengan modal awal.
* **Filter Interaktif Status**: Filter dropdown di atas setiap tabel untuk menyaring: `Semua Status`, `📈 Hanya Profit`, `🔻 Hanya Loss`, atau `⚖️ Hanya BEP`.
* **Multi-Target Take Profit (TP 1, TP 2, TP 3) & Stop Loss (SL)**: Pengisian level target TP dan batas risiko manual (Rp).

### 3. 📅 Perhitungan Durasi Hold Hari Kerja (Working Days)
* Menghitung lama hold hanya pada **hari kerja aktif bursa (Senin – Jumat)**, tidak terdistorsi oleh hari libur akhir pekan (Sabtu & Minggu).

### 4. 📊 Statistik & Evaluasi Win Rate Fleksibel (Collapsible / Buka-Tutup)
* **Bisa di-Hide / Tampilkan**: Berada di expander bagian atas yang bisa dibuka atau ditutup agar layar tetap bersih dan fokus.
* **Filter Kategori Screener**: Statistik dapat difilter berdasarkan `Semua Hasil Screener`, `Flow Masuk`, `Flow Masuk + Fundamental OK`, atau `Saham Tidur`.
* **Win Rate All-Time**: Menghitung persentase kemenangan dari seluruh riwayat trade yang selesai (Win vs Loss) serta rata-rata keuntungan per trade.
* **Win Rate Bulanan Real-Time**: Otomatis default mengikuti **bulan dan tahun riil saat ini**, serta dilengkapi pemilih bulan dan tahun fleksibel untuk evaluasi historis.

### 5. 🕌 Filter & Tampilan Single-View Saham Syariah (ISSI)
* **Penanda Ringkas**: Ikon centang (**✅**) untuk saham Syariah (ISSI) dan tanda hubung (**-**) untuk Non-Syariah.
* **Layout Satu Layar (Single-View)**: Seluruh data dari Kode, Tgl Masuk, Kemunculan, Hold, Harga Sekarang, Floating Gain, Target TP/SL, Keterangan, hingga Status langsung terbaca rapi dalam satu tampilan layar tanpa perlu scroll horizontal.

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
* **Proteksi Anti-Duplikasi per Kategori (*First Entry Lock per Kategori*)**: Emiten yang sama diperbolehkan masuk ke beberapa kategori berbeda secara independen (misal tgl 1 Sept di `Saham Tidur` @ Rp 50, lalu tgl 2 Sept masuk di `Flow Masuk` @ Rp 54) tanpa saling menimpa. Duplikasi hanya dicegah jika diimpor ke kategori yang sama.
* **Deteksi Saham Beririsan (*Multi-Screener Confluence*)**: Saham yang aktif di lebih dari 1 kategori secara otomatis diberi penanda visual di tabel (`🔥 [2 Tab]` atau `⭐ [COMBO 3 Tab]`), lengkap dengan banner rekap saham multi-setup di atas tab screener.
* **Exit Fleksibel (Bungkus Cuan / Cut Loss Satuan vs Borongan)**: Saat menutup posisi emiten yang aktif di beberapa kategori, pengguna dapat memilih untuk merealisasikan kategori tertentu saja atau keluar dari semua posisi sekaligus.

### 8. 📁 Upload File Screener (Excel .xlsx / CSV)
* **Import File Sekali Klik**: Tersedia tab khusus **Upload Excel / CSV** di Panel Editor untuk mengunggah file hasil screener seperti file `HASIL SCREENER SAHAM BARU BANGUN TIDUR.xlsx` (mendukung sheet `AGUS-SEPT`).
* **Auto-Routing Status `Done`**:
  * Baris dengan keterangan **Done** otomatis dialihkan langsung ke tabel **Riwayat Trade Selesai** (meskipun harga exit / persentase cuan belum tercatat).
  * Baris tanpa status Done otomatis masuk ke **Watchlist Aktif** dengan riwayat hitungan kemunculan yang tersimpan.
* **Auto-Deteksi Format Kolom & Tanggal**: Mengenali kolom *Hari, Tanggal, Emiten Saham, Harga Penutupan, Keterangan*, serta menangani format tanggal Indonesia maupun Excel timestamp.

### 9. 📝 Kolom Keterangan & Pemindahan Cepat Saham Selesai
* **Kolom Keterangan di Seluruh Tabel**:
  * Terletak tepat sebelum kolom **Status** di ketiga tab hasil screener maupun tabel **Riwayat Trade Selesai**.
  * Berisi label dinamis seperti `Mulai gerak`, `Done`, atau catatan pergerakan bebas lainnya.
* **Fitur Ubah ke `Done` di Kelola Watchlist**:
  * Di tab **Kelola Watchlist**, Anda dapat langsung mengetikkan `Done` pada kolom Keterangan suatu saham lalu klik **Simpan Perubahan**.
  * Sistem akan secara otomatis memindahkan saham tersebut dari Watchlist Aktif ke **Riwayat Trade Selesai**.

### 10. 🧹 Reset Seluruh Data Tabel
* Di sidebar saat login Editor, tersedia fitur **Reset Seluruh Data Tabel** dengan konfirmasi pengamanan.
* Menghapus dan mengosongkan seluruh isi database (Watchlist Aktif, Histori Cuan, dan Histori Cut Loss) secara instan saat Anda ingin memulai musim screening baru atau setelah mengosongkan data lama.

### 11. 🔍 Pelacakan Frekuensi & Tanggal Kemunculan Screener (Hit Tracker)
* **Pencatatan Otomatis Kemunculan Berulang**: Saat melakukan import harian, jika emiten yang sudah ada di watchlist terdeteksi kembali pada tanggal baru, sistem secara otomatis mencatat tanggal kemunculan (`hit_dates`) dan meningkatkan hitungan kemunculan (`hit_count`).
* **Kolom Kemunculan di Seluruh Tabel**: Ditampilkan dengan format ringkas tanggal (`DD/MM`) seperti `1x (01/09)`, `⚡ 2x (01/09, 03/09)`, `🔥 3x (01/09, 03/09, 08/09)`.

### 12. 📜 Riwayat Trade Selesai (Satu Tabel Terpadu)
* Menggabungkan riwayat take profit, cut loss, dan saham berstatus `Done` ke dalam **satu tabel tunggal** yang ringkas dan rapi.
* Filter interaktif lengkap untuk menyaring status hasil, kategori, syariah, pencarian emiten, dan rentang tanggal keluar/selesai.

### 13. 💾 Backup & Restore Database JSON (Perlindungan Data Anti-Hilang)
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
