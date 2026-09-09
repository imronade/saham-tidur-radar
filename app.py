import streamlit as st
import pandas as pd
import datetime
import json
import os
import yfinance as yf

# ==========================================
# KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="IDX Sleeping Stock Radar",
    page_icon="💤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Password Editor Rahasia
DEFAULT_PASSWORD = "akubahagiasehatkayaraya"
EDITOR_PASSWORD = st.secrets.get("EDITOR_PASSWORD", DEFAULT_PASSWORD) if hasattr(st, "secrets") else DEFAULT_PASSWORD

DATA_FILE = "stocks_data.json"

# ==========================================
# FUNGSI HITUNG HARI KERJA (SENIN - JUMAT)
# ==========================================
def calculate_working_days(start_date, end_date=None):
    if end_date is None:
        end_date = datetime.date.today()
    if isinstance(start_date, str):
        try:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        except:
            return 0
    if isinstance(end_date, str):
        try:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        except:
            end_date = datetime.date.today()
            
    if start_date > end_date:
        return 0

    count = 0
    cur = start_date
    while cur <= end_date:
        if cur.weekday() < 5:  # 0=Senin, 4=Jumat, 5=Sabtu, 6=Minggu
            count += 1
        cur += datetime.timedelta(days=1)
    return count

# ==========================================
# FUNGSI LOAD & SAVE DATA
# ==========================================
def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "active_stocks": [
                {
                    "ticker": "FINN",
                    "name": "First Indo American",
                    "is_syariah": True,
                    "entry_date": "2026-08-01",
                    "entry_price": 50,
                    "current_price": 54,
                    "tp1": 56,
                    "tp2": 62,
                    "tp3": 70,
                    "is_fca": True
                },
                {
                    "ticker": "KBAG",
                    "name": "Karya Bersama Anugerah",
                    "is_syariah": True,
                    "entry_date": "2026-06-15",
                    "entry_price": 50,
                    "current_price": 50,
                    "tp1": 58,
                    "tp2": 66,
                    "tp3": 75,
                    "is_fca": True
                },
                {
                    "ticker": "MDLN",
                    "name": "Modernland Realty",
                    "is_syariah": True,
                    "entry_date": "2026-05-20",
                    "entry_price": 62,
                    "current_price": 61,
                    "tp1": 70,
                    "tp2": 80,
                    "tp3": 92,
                    "is_fca": False
                },
                {
                    "ticker": "POLU",
                    "name": "Golden Flower Tbk",
                    "is_syariah": False,
                    "entry_date": "2026-04-12",
                    "entry_price": 50,
                    "current_price": 50,
                    "tp1": 60,
                    "tp2": 75,
                    "tp3": 90,
                    "is_fca": True
                }
            ],
            "awakened_history": [
                {
                    "ticker": "BUMI",
                    "name": "Bumi Resources Tbk",
                    "is_syariah": True,
                    "entry_date": "2026-06-02",
                    "awakened_date": "2026-07-24",
                    "hold_days": 38,
                    "entry_price": 80,
                    "exit_price": 88,
                    "gain_pct": 10.0,
                    "status_exit": "BUNGKUS MANUAL 💰",
                    "note": "Dekat TP 1 di 90, amankan cuan +10%"
                },
                {
                    "ticker": "KPIG",
                    "name": "MNC Land Tbk",
                    "is_syariah": True,
                    "entry_date": "2026-07-10",
                    "awakened_date": "2026-09-09",
                    "hold_days": 43,
                    "entry_price": 55,
                    "exit_price": 74,
                    "gain_pct": 34.55,
                    "status_exit": "TP 2 TEMBUS 🎯",
                    "note": "Target TP 2 Rp 72 berhasil dilewati"
                }
            ]
        }
        with open(DATA_FILE, "w") as f:
            json.dump(initial_data, f, indent=2)
        return initial_data

    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ==========================================
# FETCH HARGA TERAKHIR DARI YAHOO FINANCE
# ==========================================
def fetch_latest_price(ticker):
    try:
        symbol = ticker.strip().upper()
        if not symbol.endswith(".JK"):
            symbol += ".JK"
        stock = yf.Ticker(symbol)
        hist = stock.history(period="3d")
        if not hist.empty:
            return int(hist["Close"].iloc[-1])
    except:
        pass
    return None

# ==========================================
# INISIALISASI SESSION STATE
# ==========================================
if "data" not in st.session_state:
    st.session_state["data"] = load_data()

data = st.session_state["data"]

# ==========================================
# SIDEBAR: AUTENTIKASI PASSWORD EDITOR
# ==========================================
with st.sidebar:
    st.header("🔐 Akses Editor")
    input_pass = st.text_input("Password Editor", type="password", placeholder="Ketik password...")
    
    is_editor = (input_pass == EDITOR_PASSWORD)
    
    if is_editor:
        st.success("✅ **Mode: Editor Aktif ✍️**")
        st.caption("Anda memiliki hak akses menambah, mengedit TP, update harga, dan membungkus cuan.")
    else:
        st.info("👁️ **Mode: Viewer (Hanya Lihat)**")
        st.caption("Pengunjung publik hanya dapat melihat data, memfilter syariah, dan mengunduh CSV.")

    st.markdown("---")
    st.markdown("### 📌 Petunjuk Penggunaan")
    st.markdown("""
    - **Hari Kerja**: Dihitung otomatis (Senin-Jumat).
    - **TP 1, 2, 3**: Dihitung persentasenya terhadap harga masuk.
    - **Bungkus Cuan**: Pindahkan saham yang sudah profit ke tabel histori.
    - **Export CSV**: Download tabel langsung dalam format Excel/CSV.
    """)

# ==========================================
# HEADER UTAMA
# ==========================================
col_title, col_btn = st.columns([3, 1.5])
with col_title:
    st.title("💤 IDX Sleeping Stock Radar")
    st.caption("Pantau saham tidur, evaluasi **Winrate** & **Rata-rata Keuntungan**, filter Syariah, dan amankan profit.")

with col_btn:
    if is_editor:
        if st.button("🔄 Update Harga Sekarang", type="primary", use_container_width=True):
            with st.spinner("Mengambil harga penutupan bursa..."):
                updated_count = 0
                for s in data["active_stocks"]:
                    price = fetch_latest_price(s["ticker"])
                    if price:
                        s["current_price"] = price
                        updated_count += 1
                save_data(data)
                st.toast(f"Berhasil update {updated_count} saham!", icon="✅")
                st.rerun()

# ==========================================
# STATISTIK KARTU METRIK
# ==========================================
active_list = data["active_stocks"]
history_list = data["awakened_history"]

# Hitung Winrate & Rata-rata Keuntungan
win_count = sum(1 for h in history_list if h["gain_pct"] >= 0)
total_closed = len(history_list)
winrate = (win_count / total_closed * 100) if total_closed > 0 else 0.0
total_gain = sum(h["gain_pct"] for h in history_list)
avg_gain = (total_gain / total_closed) if total_closed > 0 else 0.0

# Hitung Siaga
near_tp_count = 0
for s in active_list:
    if s["current_price"] > s["entry_price"] and s["current_price"] < s["tp1"]:
        near_tp_count += 1

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Saham Aktif Dipantau", f"{len(active_list)} Emiten", f"{sum(1 for s in active_list if s['is_syariah'])} Syariah")
m2.metric("Siaga / Dekat TP ⚡", f"{near_tp_count} Emiten", "Sedang Floating Profit")
m3.metric("Saham Sudah Bangun 🏆", f"{total_closed} Emiten", "Trade Selesai")
m4.metric("Winrate 🎯", f"{winrate:.1f}%", f"{win_count} Win / {total_closed - win_count} Loss")
m5.metric("Rata-rata Keuntungan 📈", f"+{avg_gain:.2f}%", "Rerata Gain per Emiten")

st.markdown("---")

# ==========================================
# TABEL 1: WATCHLIST SAHAM TIDUR (AKTIF)
# ==========================================
st.subheader("📋 Daftar Saham Tidur (Aktif Dipantau)")

# Filter Controls
f_col1, f_col2 = st.columns([2, 2])
with f_col1:
    syariah_filter = st.selectbox(
        "Filter Syariah:",
        ["Semua Saham", "🕌 Hanya Saham Syariah (ISSI)", "Hanya Non-Syariah"],
        key="filter_active_syariah"
    )
with f_col2:
    search_query = st.text_input("Cari Kode / Nama Saham:", placeholder="misal: FINN", key="search_active")

# Filter logic
filtered_active = []
for s in active_list:
    # Syariah filter
    if syariah_filter == "🕌 Hanya Saham Syariah (ISSI)" and not s["is_syariah"]:
        continue
    if syariah_filter == "Hanya Non-Syariah" and s["is_syariah"]:
        continue
    # Search filter
    if search_query:
        q = search_query.upper()
        if q not in s["ticker"].upper() and q not in s.get("name", "").upper():
            continue
    filtered_active.append(s)

# Siapkan DataFrame Tampilan
display_active = []
for s in filtered_active:
    entry = s["entry_price"]
    curr = s["current_price"]
    gain_pct = ((curr - entry) / entry * 100) if entry > 0 else 0.0
    tp1_pct = ((s["tp1"] - entry) / entry * 100) if entry > 0 else 0.0
    tp2_pct = ((s["tp2"] - entry) / entry * 100) if entry > 0 else 0.0
    tp3_pct = ((s["tp3"] - entry) / entry * 100) if entry > 0 else 0.0
    hold_work_days = calculate_working_days(s["entry_date"])

    # Status
    if curr >= s["tp3"]:
        status = "TP 3 TERCAPAI 🏆"
    elif curr >= s["tp2"]:
        status = "TP 2 TEMBUS 🎯"
    elif curr >= s["tp1"]:
        status = "TP 1 TERCAPAI 🎯"
    elif curr > entry:
        diff_tp1 = s["tp1"] - curr
        status = f"DEKAT TP 1 (Sisa {diff_tp1} poin) ⚡"
    else:
        status = "MASIH TIDUR 💤"

    display_active.append({
        "Kode": s["ticker"],
        "Nama": s["name"],
        "Syariah": "🕌 Syariah" if s["is_syariah"] else "Non-Syariah",
        "Tgl Masuk": s["entry_date"],
        "Lama Hold": f"{hold_work_days} Hari Kerja",
        "Harga Masuk": f"Rp {entry}",
        "Harga Sekarang": f"Rp {curr}",
        "Floating Gain": f"{gain_pct:+.2f}%",
        "TP 1": f"Rp {s['tp1']} (+{tp1_pct:.1f}%)",
        "TP 2": f"Rp {s['tp2']} (+{tp2_pct:.1f}%)",
        "TP 3": f"Rp {s['tp3']} (+{tp3_pct:.1f}%)",
        "Papan": "FCA" if s.get("is_fca") else "Reguler",
        "Status": status
    })

df_active = pd.DataFrame(display_active)
if not df_active.empty:
    st.dataframe(df_active, use_container_width=True, hide_index=True)
else:
    st.info("Tidak ada saham yang sesuai dengan filter.")

# Export to CSV
if not df_active.empty:
    csv_active = df_active.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Export Watchlist ke .CSV",
        data=csv_active,
        file_name=f"watchlist_saham_tidur_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ==========================================
# PANEL OPERASI EDITOR (HANYA AKTIF SAAT LOGIN)
# ==========================================
if is_editor:
    st.markdown("### ✍️ Panel Aksi Editor")
    tab_bungkus, tab_add, tab_edit = st.tabs(["💰 Bungkus Cuan (Realisasi)", "➕ Tambah Saham Tidur", "⚙️ Kelola / Hapus Saham"])

    # TAB 1: BUNGKUS CUAN
    with tab_bungkus:
        st.markdown("**Amankan profit saham tidur (meski belum sentuh TP 1 resmi):**")
        tickers_active = [s["ticker"] for s in active_list]
        if tickers_active:
            b_col1, b_col2, b_col3 = st.columns(3)
            with b_col1:
                sel_ticker = st.selectbox("Pilih Saham yang Mau Dibungkus:", tickers_active)
                selected_stock = next(s for s in active_list if s["ticker"] == sel_ticker)
            with b_col2:
                exit_price = st.number_input("Harga Jual / Realisasi (Rp):", min_value=1, value=int(selected_stock["current_price"]))
            with b_col3:
                exit_reason = st.selectbox("Alasan Exit:", [
                    "Dekat TP 1 tapi antrean berat, amankan cuan",
                    "Amankan modal (Bungkus dulu)",
                    "Volume mulai sepi kembali",
                    "Pindah ke emiten lain",
                    "Target TP resmi tercapai"
                ])

            entry_p = selected_stock["entry_price"]
            realized_gain = ((exit_price - entry_p) / entry_p * 100) if entry_p > 0 else 0.0
            st.info(f"💡 Estimasi Realisasi: **{realized_gain:+.2f}%** (Modal Rp {entry_p} ➔ Jual Rp {exit_price})")

            if st.button("🎉 Konfirmasi Bungkus Cuan ➔ Pindah ke Histori", type="primary"):
                work_days = calculate_working_days(selected_stock["entry_date"])
                new_hist = {
                    "ticker": selected_stock["ticker"],
                    "name": selected_stock["name"],
                    "is_syariah": selected_stock["is_syariah"],
                    "entry_date": selected_stock["entry_date"],
                    "awakened_date": str(datetime.date.today()),
                    "hold_days": work_days,
                    "entry_price": entry_p,
                    "exit_price": exit_price,
                    "gain_pct": round(realized_gain, 2),
                    "status_exit": "BUNGKUS MANUAL 💰" if exit_price < selected_stock["tp1"] else "TARGET TP TERCAPAI 🎯",
                    "note": exit_reason
                }
                data["awakened_history"].insert(0, new_hist)
                data["active_stocks"] = [s for s in data["active_stocks"] if s["ticker"] != sel_ticker]
                save_data(data)
                st.success(f"Saham {sel_ticker} berhasil dibungkus dan masuk ke riwayat keuntungan!")
                st.rerun()

    # TAB 2: TAMBAH SAHAM BARU
    with tab_add:
        with st.form("form_add_stock"):
            st.markdown("**Form Tambah Saham Tidur Baru:**")
            a1, a2, a3 = st.columns(3)
            with a1:
                new_ticker = st.text_input("Kode Saham (4 Huruf):", placeholder="cth: BUMI").upper()
                new_name = st.text_input("Nama Perusahaan:", placeholder="cth: Bumi Resources")
                new_syariah = st.checkbox("🕌 Saham Syariah (ISSI)", value=True)
            with a2:
                new_entry_date = st.date_input("Tanggal Masuk Watchlist:", datetime.date.today())
                new_entry_price = st.number_input("Harga Waktu Masuk (Rp):", min_value=1, value=50)
                new_fca = st.checkbox("Masuk Papan FCA (Full Call Auction)", value=False)
            with a3:
                new_tp1 = st.number_input("Target TP 1 (Rp):", min_value=1, value=58)
                new_tp2 = st.number_input("Target TP 2 (Rp):", min_value=1, value=65)
                new_tp3 = st.number_input("Target TP 3 (Rp):", min_value=1, value=75)

            submitted = st.form_submit_button("Simpan Saham ke Watchlist 🚀")
            if submitted:
                if not new_ticker or len(new_ticker) != 4:
                    st.error("Kode saham harus 4 huruf!")
                elif any(s["ticker"] == new_ticker for s in active_list):
                    st.error("Kode saham sudah ada di watchlist!")
                else:
                    new_item = {
                        "ticker": new_ticker,
                        "name": new_name or "Perusahaan Terbuka",
                        "is_syariah": new_syariah,
                        "entry_date": str(new_entry_date),
                        "entry_price": int(new_entry_price),
                        "current_price": int(new_entry_price),
                        "tp1": int(new_tp1),
                        "tp2": int(new_tp2),
                        "tp3": int(new_tp3),
                        "is_fca": new_fca
                    }
                    data["active_stocks"].append(new_item)
                    save_data(data)
                    st.success(f"Saham {new_ticker} berhasil ditambahkan!")
                    st.rerun()

    # TAB 3: KELOLA / HAPUS SAHAM
    with tab_edit:
        st.markdown("**Hapus Saham dari Watchlist:**")
        del_ticker = st.selectbox("Pilih Saham yang Ingin Dihapus:", ["-"] + tickers_active)
        if del_ticker != "-":
            if st.button(f"🗑️ Hapus Saham {del_ticker}", type="secondary"):
                data["active_stocks"] = [s for s in data["active_stocks"] if s["ticker"] != del_ticker]
                save_data(data)
                st.success(f"Saham {del_ticker} telah dihapus dari daftar.")
                st.rerun()

st.markdown("---")

# ==========================================
# TABEL 2: SAHAM YANG SUDAH BANGUN (HISTORI)
# ==========================================
st.subheader("🏆 Saham yang Sudah Bangun / Dibungkus Cuan (Histori)")

h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    syariah_hist_filter = st.selectbox(
        "Filter Syariah Histori:",
        ["Semua Histori", "🕌 Hanya Syariah", "Hanya Non-Syariah"],
        key="filter_hist_syariah"
    )

display_hist = []
for h in history_list:
    if syariah_hist_filter == "🕌 Hanya Syariah" and not h["is_syariah"]:
        continue
    if syariah_hist_filter == "Hanya Non-Syariah" and h["is_syariah"]:
        continue

    display_hist.append({
        "Kode": h["ticker"],
        "Nama": h["name"],
        "Syariah": "🕌 Syariah" if h["is_syariah"] else "Non-Syariah",
        "Periode": f"{h['entry_date']} ➔ {h['awakened_date']}",
        "Lama Hold": f"{h['hold_days']} Hari Kerja",
        "Harga Masuk": f"Rp {h['entry_price']}",
        "Harga Jual": f"Rp {h['exit_price']}",
        "Realisasi Cuan": f"+{h['gain_pct']:.2f}%",
        "Status Exit": h["status_exit"],
        "Catatan": h.get("note", "-")
    })

df_hist = pd.DataFrame(display_hist)
if not df_hist.empty:
    st.dataframe(df_hist, use_container_width=True, hide_index=True)
    csv_hist = df_hist.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Export Histori Cuan ke .CSV",
        data=csv_hist,
        file_name=f"histori_saham_bangun_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info("Belum ada histori saham yang selesai.")
