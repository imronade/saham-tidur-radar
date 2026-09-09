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
  * Menambah saham tidur baru ke watchlist.
  * Mengupdate harga live secara manual via Yahoo Finance (`.JK`).
  * Membungkus cuan (*early exit* / target TP) dan memindahkannya ke tabel histori.
  * Mengedit angka TP/harga dan menghapus baris data dengan sistem **centang tabel (*checkbox*)**.
  * Dilengkapi tombol **Exit / Keluar Mode Editor** untuk kembali ke mode publik dengan aman.

### 2. 🎯 Multi-Target Take Profit (TP 1, TP 2, TP 3) Bersifat Opsional
* Pengisian target Take Profit bersifat **fleksibel / opsional**: bisa diisi lengkap, sebagian, atau dikosongkan (ditampilkan tanda strip `-`).
* Menghitung persentase potensi keuntungan terhadap harga masuk secara otomatis.
* Status saham dinamis: mendeteksi `MASIH TIDUR 💤`, `FLOATING PROFIT 📈`, `DEKAT TP 1 ⚡`, hingga `TP 1/2/3 TERCAPAI 🎯/🏆`.

### 3. 📅 Perhitungan Durasi Hold Hari Kerja (Working Days)
* Menghitung lama hold hanya pada **hari kerja aktif bursa (Senin – Jumat)**, tidak terdistorsi oleh hari libur akhir pekan (Sabtu & Minggu).

### 4. 📈 Evaluasi Win Rate & Rata-rata Cuan (All-Time & Bulanan)
* **Winrate Total (All-Time)**: Menghitung persentase kemenangan dari seluruh riwayat trade yang pernah ada.
* **Winrate Bulanan Dinamis**: Menampilkan performa khusus bulan terbaru secara default, serta dilengkapi dropdown untuk memilih dan mengevaluasi bulan-bulan sebelumnya.
* **Komparasi Mendalam**: Panel rincian komparasi performa All-Time vs Bulan Terpilih, termasuk status floating profit saham aktif.

### 5. 🕌 Filter Saham Syariah (ISSI) & Papan FCA
* Indikator jelas untuk saham Syariah (ISSI) dan saham Non-Syariah.
* Penanda saham yang masuk **Papan Pemantauan Khusus / Full Call Auction (FCA)**.

### 6. 📥 Export ke File CSV
* Tombol export instan untuk tabel **Watchlist Aktif** maupun **Histori Saham Bangun**.
* Format UTF-8 BOM yang langsung terbaca rapi di Microsoft Excel.
* **100% mengikuti filter yang sedang diterapkan di layar**.

---

## 🛠️ Struktur Proyek

```text
saham-tidur-dashboard/
├── app.py              # File utama aplikasi Streamlit
├── requirements.txt    # Daftar pustaka Python (Streamlit, Pandas, yfinance, requests)
├── README.md           # Dokumentasi proyek
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
2. Upload file `app.py`, `requirements.txt`, `README.md`, dan `LICENSE` ke repository tersebut.
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
