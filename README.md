# 💤 IDX Sleeping Stock Radar

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://radar-saham-tidur.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

Web dashboard interaktif untuk memantau, menganalisis, dan mencatat pergerakan **saham tidur (*dormant stocks*)** di Bursa Efek Indonesia (IDX / BEI). Aplikasi ini dirancang khusus untuk memonitor potensi bangunnya saham gocap/tidur dengan sistem target multi-level Take Profit, kalkulasi hari kerja bursa, serta pencatatan histori realisasi profit.

🌐 **Aplikasi Live Online**: [IDX Sleeping Stock Radar · Streamlit](https://radar-saham-tidur.streamlit.app/)

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

### 2. 🎯 Multi-Target Take Profit (TP) & Stop Loss (SL) Manual
* **Stop Loss (SL)**: Pengisian batas risiko manual (Rp) bersifat opsional. Mendeteksi status siaga `DEKAT SL 🚨` hingga `KENA SL 🛑`.
* **Multi-Target Take Profit (TP 1, TP 2, TP 3)**: Pengisian target Take Profit fleksibel/opsional (bisa diisi lengkap, sebagian, atau dikosongkan `-`).
* **Status Saham Dinamis Real-Time**: Otomatis mendeteksi `KENA SL 🛑`, `DEKAT SL 🚨`, `MASIH TIDUR 💤`, `FLOATING PROFIT 📈`, `FLOATING LOSS 🔻`, `DEKAT TP 1 ⚡`, hingga `TP 1/2/3 TERCAPAI 🎯/🏆`.

### 3. 📅 Perhitungan Durasi Hold Hari Kerja (Working Days)
* Menghitung lama hold hanya pada **hari kerja aktif bursa (Senin – Jumat)**, tidak terdistorsi oleh hari libur akhir pekan (Sabtu & Minggu).

### 4. 📈 Evaluasi Win Rate & Rata-rata Cuan (All-Time & Bulanan)
* **Winrate Total (All-Time)**: Menghitung persentase kemenangan dari seluruh riwayat trade yang pernah selesai (Saham Bangun Cuan vs Saham Gagal Kena SL).
* **Winrate Bulanan Dinamis**: Menampilkan performa khusus bulan terbaru secara default, serta dilengkapi dropdown untuk memilih dan mengevaluasi bulan-bulan sebelumnya.
* **Komparasi Mendalam**: Panel rincian komparasi performa All-Time vs Bulan Terpilih, termasuk status floating profit saham aktif dan siaga emiten yang terkena SL.

### 5. 🕌 Filter & Tampilan Single-View Saham Syariah (ISSI)
* **Penanda Ringkas**: Ikon centang (**✅**) untuk saham Syariah (ISSI) dan tanda hubung (**-**) untuk Non-Syariah.
* **Layout Satu Layar (Single-View)**: Kolom papan telah diringkas/dihapus dan lebar kolom dioptimalkan agar seluruh data dari Kode, Modal, Target TP/SL, hingga Status langsung terbaca rapi dalam satu tampilan layar tanpa perlu scroll horizontal.

### 6. 📥 Export ke File CSV
* Tombol export instan untuk **Watchlist Aktif**, **Histori Saham Bangun**, maupun **Histori Saham Gagal Bangun (SL)**.
* Format UTF-8 BOM yang langsung terbaca rapi di Microsoft Excel.
* **100% mengikuti filter yang sedang diterapkan di layar**.

### 7. ⚡ Quick Import Stockbit (Dual Screener: Syariah & Non-Syariah)
* **Dua Kolom Fleksibel (Kiri & Kanan)**:
  * **Kolom Kiri (🕌 Syariah ISSI)**: Hasil screener Stockbit dengan filter Stock Universe = `ISSI` (otomatis ditandai Syariah).
  * **Kolom Kanan (🏢 IHSG / Non-Syariah - Opsional)**: Hasil screener Stockbit dengan filter Universe `All Stocks` atau Non-Syariah.
* **Bisa Diisi Salah Satu Saja atau Keduanya Sekaligus**:
  * Cukup isi kolom kiri $\rightarrow$ seluruhnya masuk sebagai Syariah.
  * Cukup isi kolom kanan $\rightarrow$ seluruhnya masuk sebagai Non-Syariah.
  * Isi kedua kolom sekaligus $\rightarrow$ sistem otomatis memilah mana yang Syariah dan mana yang Non-Syariah secara cerdas dalam 1x klik.
* **Auto-Reset Form ke Blank**: Setelah tombol *Proses & Impor* diklik, kedua kotak teks otomatis bersih kembali (kosong/blank) sehingga siap untuk aktivitas screening berikutnya.
* **Ekstraksi Cerdas & Otomatis**: Mendukung format tabel mentah maupun markdown link Stockbit `[KODE](url)` dan otomatis mengambil harga di baris bawahnya.
* **Proteksi Anti-Duplikasi (*First Entry Lock*)**: Emiten yang sudah ada di watchlist aktif tidak akan terduplikasi atau tertimpa, sehingga tanggal awal masuk dan modal harga awal tetap aman terlindungi.

### 8. 🛑 Tabel Saham Gagal Bangun (Histori Terkena SL / Cut Loss)
* Tabel histori terpisah khusus mencatat saham-saham yang tidak berhasil bangun atau terpaksa di-cut loss karena menembus level Stop Loss.
* **Pengelolaan Penuh di Mode Editor**: Dilengkapi tab khusus **🛑 Kelola Gagal Bangun** untuk mengedit angka realisasi rugi, level SL, tanggal cut loss, catatan/alasan, serta fitur centang hapus baris (*checkbox delete*).
* Dilengkapi filter Syariah, pencarian kode saham, filter tanggal cut loss, dan tombol unduh CSV.
* Terintegrasi langsung ke perhitungan statistik Win Rate trading agar hasil evaluasi performa trading selalu objektif dan realistis.

### 9. 💾 Backup & Restore Database JSON (Perlindungan Data Anti-Hilang)
* **1-Click Backup**: Di sidebar saat login Editor, tersedia tombol **📥 Download stocks_data.json** untuk mengunduh seluruh database (watchlist aktif, riwayat cuan, dan cut loss) ke laptop Anda kapan saja.
* **Restore Fleksibel**: Dilengkapi fitur upload JSON cadangan untuk memulihkan seluruh data secara instan jika sewaktu-waktu dibutuhkan.
* **Keamanan Permanen**: File `stocks_data.json` hasil unduhan dapat diunggah langsung ke repositori GitHub agar data tersimpan permanen dan kebal dari reboot server cloud.

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
