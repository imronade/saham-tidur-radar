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
# FUNGSI FILTER TANGGAL FLEKSIBEL (SINGLE / RANGE)
# ==========================================
def is_date_in_filter(date_str, filter_val):
    if not filter_val:
        return True
    try:
        if isinstance(date_str, str):
            d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        elif isinstance(date_str, (datetime.date, datetime.datetime)):
            d = date_str if isinstance(date_str, datetime.date) else date_str.date()
        else:
            return True
    except:
        return True
    
    if len(filter_val) == 1:
        return d == filter_val[0]
    elif len(filter_val) >= 2:
        start_d, end_d = filter_val[0], filter_val[1]
        if start_d > end_d:
            start_d, end_d = end_d, start_d
        return start_d <= d <= end_d
    return True

# ==========================================
# FUNGSI LOAD & SAVE DATA
# ==========================================
def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "active_stocks": [
                {
                    "ticker": "FINN",
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
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2)
        return initial_data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
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

if "is_editor" not in st.session_state:
    st.session_state["is_editor"] = False

data = st.session_state["data"]

# ==========================================
# SIDEBAR: AUTENTIKASI PASSWORD EDITOR
# ==========================================
with st.sidebar:
    st.header("🔐 Akses Editor")
    
    if st.session_state["is_editor"]:
        st.success("✅ **Mode: Editor Aktif ✍️**")
        st.caption("Anda memiliki hak akses menambah, mengedit tabel, centang hapus saham, update harga, dan membungkus cuan.")
        
        # TOMBOL EXIT / LOGOUT MODE EDITOR
        if st.button("🚪 Keluar / Exit Mode Editor", type="secondary", use_container_width=True, key="btn_logout_sidebar"):
            st.session_state["is_editor"] = False
            st.toast("Anda telah keluar dari Mode Editor.", icon="🔒")
            st.rerun()
    else:
        st.info("👁️ **Mode: Viewer (Hanya Lihat)**")
        st.caption("Pengunjung publik hanya dapat melihat data, memfilter syariah & tanggal, mengurutkan tabel, dan mengunduh CSV.")
        
        with st.form("form_login_editor", clear_on_submit=True):
            input_pass = st.text_input("Password Editor", type="password", placeholder="Ketik password...")
            btn_login = st.form_submit_button("🔓 Masuk Mode Editor", use_container_width=True)
            if btn_login:
                if input_pass == EDITOR_PASSWORD:
                    st.session_state["is_editor"] = True
                    st.toast("Berhasil masuk sebagai Editor!", icon="✅")
                    st.rerun()
                elif input_pass:
                    st.error("Password salah! Silakan coba lagi.")

    is_editor = st.session_state["is_editor"]

    st.markdown("---")
    st.markdown("### 📌 Fitur Dashboard")
    st.markdown("""
    - **Filter Tanggal**: Bisa pilih 1 tanggal spesifik atau rentang tanggal.
    - **Urutkan Tabel**: Klik judul kolom apa saja untuk beralih antara Ascending (⬆️) dan Descending (⬇️).
    - **Hari Kerja**: Dihitung otomatis (Senin-Jumat).
    - **Multi-Target TP**: TP 1, TP 2, TP 3 + indikator persentase.
    - **Bungkus Cuan**: Realisasi manual langsung pindah ke riwayat cuan.
    - **Export CSV**: Download tabel bersih tanpa kolom nama perusahaan.
    """)

# ==========================================
# HEADER UTAMA
# ==========================================
col_title, col_btn = st.columns([3, 1.5])
with col_title:
    st.title("💤 IDX Sleeping Stock Radar")
    st.caption("Pantau saham tidur, evaluasi **Winrate** & **Rata-rata Keuntungan**, filter Syariah & Tanggal, dan amankan profit.")

with col_btn:
    if is_editor:
        b_upd, b_exit = st.columns([1.3, 1])
        with b_upd:
            if st.button("🔄 Update Harga", type="primary", use_container_width=True):
                with st.spinner("Mengambil harga bursa..."):
                    updated_count = 0
                    for s in data["active_stocks"]:
                        price = fetch_latest_price(s["ticker"])
                        if price:
                            s["current_price"] = price
                            updated_count += 1
                    save_data(data)
                    st.toast(f"Berhasil update {updated_count} saham!", icon="✅")
                    st.rerun()
        with b_exit:
            if st.button("🚪 Exit Editor", type="secondary", use_container_width=True, key="btn_exit_header"):
                st.session_state["is_editor"] = False
                st.toast("Anda telah keluar dari Mode Editor.", icon="🔒")
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

# Hitung Siaga Dekat TP
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

# Filter Bar
f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 2])
with f_col1:
    syariah_filter = st.selectbox(
        "🕌 Filter Syariah:",
        ["Semua Saham", "Hanya Syariah (ISSI)", "Hanya Non-Syariah"],
        key="filter_active_syariah"
    )
with f_col2:
    search_query = st.text_input("🔍 Cari Kode Saham:", placeholder="misal: FINN", key="search_active")
with f_col3:
    date_filter_active = st.date_input(
        "📅 Filter Tgl Masuk (Rentang / 1 Hari):",
        value=(),
        key="date_filter_active",
        help="Pilih 1 tanggal (cth: 8 Juni 2026), atau pilih 2 tanggal untuk rentang periode (cth: 1-10 Agustus 2026). Kosongkan untuk semua."
    )

# Filter logic
filtered_active = []
for s in active_list:
    # Syariah filter
    if syariah_filter == "Hanya Syariah (ISSI)" and not s["is_syariah"]:
        continue
    if syariah_filter == "Hanya Non-Syariah" and s["is_syariah"]:
        continue
    # Search filter
    if search_query:
        q = search_query.upper().strip()
        if q not in s["ticker"].upper():
            continue
    # Date filter
    if not is_date_in_filter(s["entry_date"], date_filter_active):
        continue
    filtered_active.append(s)

# Default urutkan dari tanggal masuk terbaru ke terlama (descending)
filtered_active.sort(key=lambda x: str(x["entry_date"]), reverse=True)

# Siapkan DataFrame Tampilan (Tanpa Kolom Nama)
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
        status = f"DEKAT TP 1 (Sisa {diff_tp1} pt) ⚡"
    else:
        status = "MASIH TIDUR 💤"

    display_active.append({
        "Kode": s["ticker"],
        "Syariah": "🕌 Syariah" if s["is_syariah"] else "Non-Syariah",
        "Tgl Masuk": s["entry_date"],
        "Lama Hold": hold_work_days,
        "Harga Masuk": entry,
        "Harga Sekarang": curr,
        "Floating Gain (%)": round(gain_pct, 2),
        "TP 1": f"Rp {s['tp1']} (+{tp1_pct:.1f}%)",
        "TP 2": f"Rp {s['tp2']} (+{tp2_pct:.1f}%)",
        "TP 3": f"Rp {s['tp3']} (+{tp3_pct:.1f}%)",
        "Papan": "FCA" if s.get("is_fca") else "Reguler",
        "Status": status
    })

df_active = pd.DataFrame(display_active)
if not df_active.empty:
    st.dataframe(
        df_active,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Kode": st.column_config.TextColumn("Kode"),
            "Syariah": st.column_config.TextColumn("Syariah"),
            "Tgl Masuk": st.column_config.TextColumn("Tgl Masuk"),
            "Lama Hold": st.column_config.NumberColumn("Lama Hold", format="%d Hari Kerja"),
            "Harga Masuk": st.column_config.NumberColumn("Harga Masuk", format="Rp %d"),
            "Harga Sekarang": st.column_config.NumberColumn("Harga Sekarang", format="Rp %d"),
            "Floating Gain (%)": st.column_config.NumberColumn("Floating Gain", format="%.2f%%"),
            "TP 1": st.column_config.TextColumn("Target TP 1"),
            "TP 2": st.column_config.TextColumn("Target TP 2"),
            "TP 3": st.column_config.TextColumn("Target TP 3"),
            "Papan": st.column_config.TextColumn("Papan"),
            "Status": st.column_config.TextColumn("Status"),
        }
    )
else:
    st.info("Tidak ada saham yang sesuai dengan filter.")

# Export to CSV (Tanpa Kolom Nama)
if not df_active.empty:
    df_active_export = df_active.copy()
    df_active_export["Lama Hold"] = df_active_export["Lama Hold"].apply(lambda x: f"{x} Hari Kerja")
    csv_active = df_active_export.to_csv(index=False).encode('utf-8-sig')
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
    st.markdown("---")
    pe_title, pe_exit = st.columns([3.5, 1.2])
    with pe_title:
        st.markdown("### ✍️ Panel Aksi Editor")
    with pe_exit:
        if st.button("🚪 Keluar / Exit Editor", type="secondary", use_container_width=True, key="btn_exit_panel"):
            st.session_state["is_editor"] = False
            st.toast("Anda telah keluar dari Mode Editor.", icon="🔒")
            st.rerun()
    tab_bungkus, tab_add, tab_manage_active, tab_manage_hist = st.tabs([
        "💰 Bungkus Cuan (Realisasi)",
        "➕ Tambah Saham Tidur",
        "⚙️ Kelola Watchlist (Centang Hapus / Edit)",
        "📜 Kelola Histori Bangun (Centang Hapus / Edit)"
    ])

    # ----------------------------------------------------
    # TAB 1: BUNGKUS CUAN
    # ----------------------------------------------------
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
        else:
            st.info("Belum ada saham aktif di watchlist untuk dibungkus.")

    # ----------------------------------------------------
    # TAB 2: TAMBAH SAHAM BARU
    # ----------------------------------------------------
    with tab_add:
        with st.form("form_add_stock"):
            st.markdown("**Form Tambah Saham Tidur Baru:**")
            a1, a2, a3 = st.columns(3)
            with a1:
                new_ticker = st.text_input("Kode Saham (4 Huruf):", placeholder="cth: BUMI").upper().strip()
                new_syariah = st.checkbox("🕌 Saham Syariah (ISSI)", value=True)
                new_fca = st.checkbox("Masuk Papan FCA (Full Call Auction)", value=False)
            with a2:
                new_entry_date = st.date_input("Tanggal Masuk Watchlist:", datetime.date.today())
                new_entry_price = st.number_input("Harga Waktu Masuk (Rp):", min_value=1, value=50)
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

    # ----------------------------------------------------
    # TAB 3: KELOLA WATCHLIST (CENTANG HAPUS / EDIT TABEL)
    # ----------------------------------------------------
    with tab_manage_active:
        st.markdown("##### ⚙️ Edit & Hapus Saham Watchlist")
        st.caption("Centang kotak **Pilih Hapus** untuk menghapus saham yang diinginkan, atau ubah angka langsung di tabel lalu klik **Simpan Perubahan**.")
        
        if active_list:
            manage_rows = []
            for s in active_list:
                manage_rows.append({
                    "Hapus": False,
                    "Kode": s["ticker"],
                    "Tgl Masuk": s["entry_date"],
                    "Harga Masuk": int(s["entry_price"]),
                    "Harga Sekarang": int(s["current_price"]),
                    "TP 1": int(s["tp1"]),
                    "TP 2": int(s["tp2"]),
                    "TP 3": int(s["tp3"]),
                    "Syariah": bool(s["is_syariah"]),
                    "FCA": bool(s.get("is_fca", False))
                })
            df_manage_active = pd.DataFrame(manage_rows)

            edited_active_df = st.data_editor(
                df_manage_active,
                column_config={
                    "Hapus": st.column_config.CheckboxColumn("Pilih Hapus 🗑️", help="Centang baris yang ingin dihapus", default=False),
                    "Kode": st.column_config.TextColumn("Kode Saham", disabled=True),
                    "Tgl Masuk": st.column_config.TextColumn("Tgl Masuk", disabled=True),
                    "Harga Masuk": st.column_config.NumberColumn("Harga Masuk (Rp)", min_value=1, step=1, format="%d"),
                    "Harga Sekarang": st.column_config.NumberColumn("Harga Sekarang (Rp)", min_value=1, step=1, format="%d"),
                    "TP 1": st.column_config.NumberColumn("Target TP 1 (Rp)", min_value=1, step=1, format="%d"),
                    "TP 2": st.column_config.NumberColumn("Target TP 2 (Rp)", min_value=1, step=1, format="%d"),
                    "TP 3": st.column_config.NumberColumn("Target TP 3 (Rp)", min_value=1, step=1, format="%d"),
                    "Syariah": st.column_config.CheckboxColumn("Syariah (ISSI)"),
                    "FCA": st.column_config.CheckboxColumn("Papan FCA"),
                },
                hide_index=True,
                use_container_width=True,
                key="table_editor_active"
            )

            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button("🗑️ Hapus Saham yang Dicentang", type="secondary", use_container_width=True):
                    to_delete = edited_active_df[edited_active_df["Hapus"] == True]["Kode"].tolist()
                    if not to_delete:
                        st.warning("Silakan centang minimal satu saham di kolom 'Pilih Hapus 🗑️' terlebih dahulu.")
                    else:
                        data["active_stocks"] = [s for s in data["active_stocks"] if s["ticker"] not in to_delete]
                        save_data(data)
                        st.success(f"Berhasil menghapus {len(to_delete)} saham: {', '.join(to_delete)}")
                        st.rerun()

            with col_act2:
                if st.button("💾 Simpan Perubahan Watchlist", type="primary", use_container_width=True):
                    ticker_dict = {row["Kode"]: row for _, row in edited_active_df.iterrows()}
                    for s in data["active_stocks"]:
                        if s["ticker"] in ticker_dict:
                            r = ticker_dict[s["ticker"]]
                            s["entry_price"] = int(r["Harga Masuk"])
                            s["current_price"] = int(r["Harga Sekarang"])
                            s["tp1"] = int(r["TP 1"])
                            s["tp2"] = int(r["TP 2"])
                            s["tp3"] = int(r["TP 3"])
                            s["is_syariah"] = bool(r["Syariah"])
                            s["is_fca"] = bool(r["FCA"])
                    save_data(data)
                    st.success("Perubahan data watchlist berhasil disimpan!")
                    st.rerun()
        else:
            st.info("Watchlist kosong, belum ada saham untuk diedit/dihapus.")

    # ----------------------------------------------------
    # TAB 4: KELOLA HISTORI BANGUN (CENTANG HAPUS / EDIT TABEL)
    # ----------------------------------------------------
    with tab_manage_hist:
        st.markdown("##### 📜 Edit & Hapus Histori Saham Bangun")
        st.caption("Centang kolom **Pilih Hapus** untuk menghapus histori tertentu, atau sesuaikan harga jual / tgl / catatan lalu klik **Simpan Perubahan**.")

        if history_list:
            hist_rows = []
            for idx, h in enumerate(history_list):
                hist_rows.append({
                    "Hapus": False,
                    "_id": idx,
                    "Kode": h["ticker"],
                    "Tgl Masuk": h["entry_date"],
                    "Tgl Bangun": h["awakened_date"],
                    "Harga Masuk": int(h["entry_price"]),
                    "Harga Jual": int(h["exit_price"]),
                    "Status Exit": h.get("status_exit", "BUNGKUS MANUAL 💰"),
                    "Catatan": h.get("note", "")
                })
            df_manage_hist = pd.DataFrame(hist_rows)

            edited_hist_df = st.data_editor(
                df_manage_hist,
                column_config={
                    "Hapus": st.column_config.CheckboxColumn("Pilih Hapus 🗑️", help="Centang baris yang ingin dihapus", default=False),
                    "_id": None,  # disembunyikan
                    "Kode": st.column_config.TextColumn("Kode Saham", disabled=True),
                    "Tgl Masuk": st.column_config.TextColumn("Tgl Masuk (YYYY-MM-DD)"),
                    "Tgl Bangun": st.column_config.TextColumn("Tgl Bangun (YYYY-MM-DD)"),
                    "Harga Masuk": st.column_config.NumberColumn("Harga Masuk (Rp)", min_value=1, step=1, format="%d"),
                    "Harga Jual": st.column_config.NumberColumn("Harga Jual (Rp)", min_value=1, step=1, format="%d"),
                    "Status Exit": st.column_config.TextColumn("Status Exit"),
                    "Catatan": st.column_config.TextColumn("Catatan / Alasan Exit"),
                },
                hide_index=True,
                use_container_width=True,
                key="table_editor_hist"
            )

            hcol1, hcol2 = st.columns(2)
            with hcol1:
                if st.button("🗑️ Hapus Histori yang Dicentang", type="secondary", use_container_width=True):
                    delete_ids = edited_hist_df[edited_hist_df["Hapus"] == True]["_id"].tolist()
                    if not delete_ids:
                        st.warning("Silakan centang minimal satu baris histori di kolom 'Pilih Hapus 🗑️' terlebih dahulu.")
                    else:
                        data["awakened_history"] = [h for idx, h in enumerate(data["awakened_history"]) if idx not in delete_ids]
                        save_data(data)
                        st.success(f"Berhasil menghapus {len(delete_ids)} data histori.")
                        st.rerun()

            with hcol2:
                if st.button("💾 Simpan Perubahan Data Histori", type="primary", use_container_width=True):
                    new_hist_list = []
                    for _, r in edited_hist_df.iterrows():
                        entry_p = int(r["Harga Masuk"])
                        exit_p = int(r["Harga Jual"])
                        recalculated_gain = round(((exit_p - entry_p) / entry_p * 100), 2) if entry_p > 0 else 0.0
                        tgl_masuk = str(r["Tgl Masuk"]).strip()
                        tgl_bangun = str(r["Tgl Bangun"]).strip()
                        hold_days = calculate_working_days(tgl_masuk, tgl_bangun)
                        
                        orig_idx = int(r["_id"])
                        orig_syariah = data["awakened_history"][orig_idx].get("is_syariah", True) if orig_idx < len(data["awakened_history"]) else True
                        
                        new_hist_list.append({
                            "ticker": str(r["Kode"]),
                            "is_syariah": orig_syariah,
                            "entry_date": tgl_masuk,
                            "awakened_date": tgl_bangun,
                            "hold_days": hold_days,
                            "entry_price": entry_p,
                            "exit_price": exit_p,
                            "gain_pct": recalculated_gain,
                            "status_exit": str(r["Status Exit"]),
                            "note": str(r["Catatan"])
                        })
                    data["awakened_history"] = new_hist_list
                    save_data(data)
                    st.success("Perubahan data histori saham bangun berhasil disimpan!")
                    st.rerun()
        else:
            st.info("Belum ada histori saham bangun untuk diedit/dihapus.")

st.markdown("---")

# ==========================================
# TABEL 2: SAHAM YANG SUDAH BANGUN (HISTORI)
# ==========================================
st.subheader("🏆 Saham yang Sudah Bangun / Dibungkus Cuan (Histori)")

# Filter Bar Histori
hf_col1, hf_col2, hf_col3 = st.columns([1.5, 1.5, 2])
with hf_col1:
    syariah_hist_filter = st.selectbox(
        "🕌 Filter Syariah Histori:",
        ["Semua Histori", "Hanya Syariah (ISSI)", "Hanya Non-Syariah"],
        key="filter_hist_syariah"
    )
with hf_col2:
    search_hist_query = st.text_input("🔍 Cari Kode Saham Histori:", placeholder="misal: BUMI", key="search_hist")
with hf_col3:
    date_filter_hist = st.date_input(
        "📅 Filter Tgl Bangun (Rentang / 1 Hari):",
        value=(),
        key="date_filter_hist",
        help="Pilih 1 tanggal untuk hari tertentu, atau pilih 2 tanggal untuk rentang periode bangun. Kosongkan untuk semua."
    )

# Filter logic Histori
filtered_hist = []
for h in history_list:
    if syariah_hist_filter == "Hanya Syariah (ISSI)" and not h["is_syariah"]:
        continue
    if syariah_hist_filter == "Hanya Non-Syariah" and h["is_syariah"]:
        continue
    if search_hist_query:
        qh = search_hist_query.upper().strip()
        if qh not in h["ticker"].upper():
            continue
    if not is_date_in_filter(h["awakened_date"], date_filter_hist):
        continue
    filtered_hist.append(h)

# Default urutkan dari tanggal masuk terbaru ke terlama (descending)
filtered_hist.sort(key=lambda x: str(x["entry_date"]), reverse=True)

# Siapkan DataFrame Histori (Tanpa Kolom Nama)
display_hist = []
for h in filtered_hist:
    display_hist.append({
        "Kode": h["ticker"],
        "Syariah": "🕌 Syariah" if h["is_syariah"] else "Non-Syariah",
        "Tgl Masuk": h["entry_date"],
        "Tgl Bangun": h["awakened_date"],
        "Lama Hold": int(h.get("hold_days", 0)),
        "Harga Masuk": int(h["entry_price"]),
        "Harga Jual": int(h["exit_price"]),
        "Realisasi Cuan (%)": round(float(h["gain_pct"]), 2),
        "Status Exit": h["status_exit"],
        "Catatan": h.get("note", "-")
    })

df_hist = pd.DataFrame(display_hist)
if not df_hist.empty:
    st.dataframe(
        df_hist,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Kode": st.column_config.TextColumn("Kode"),
            "Syariah": st.column_config.TextColumn("Syariah"),
            "Tgl Masuk": st.column_config.TextColumn("Tgl Masuk"),
            "Tgl Bangun": st.column_config.TextColumn("Tgl Bangun"),
            "Lama Hold": st.column_config.NumberColumn("Lama Hold", format="%d Hari Kerja"),
            "Harga Masuk": st.column_config.NumberColumn("Harga Masuk", format="Rp %d"),
            "Harga Jual": st.column_config.NumberColumn("Harga Jual", format="Rp %d"),
            "Realisasi Cuan (%)": st.column_config.NumberColumn("Realisasi Cuan", format="+%.2f%%"),
            "Status Exit": st.column_config.TextColumn("Status Exit"),
            "Catatan": st.column_config.TextColumn("Catatan"),
        }
    )
    df_hist_export = df_hist.copy()
    df_hist_export["Lama Hold"] = df_hist_export["Lama Hold"].apply(lambda x: f"{x} Hari Kerja")
    csv_hist = df_hist_export.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Export Histori Cuan ke .CSV",
        data=csv_hist,
        file_name=f"histori_saham_bangun_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info("Tidak ada riwayat histori yang sesuai dengan filter.")
