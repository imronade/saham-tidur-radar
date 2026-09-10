import streamlit as st
import pandas as pd
import datetime
import json
import os
import re
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
DEFAULT_PASSWORD = "password_rahasia_anda"
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
# FUNGSI PARSER HASIL SCREENER STOCKBIT
# ==========================================
def parse_stockbit_screener(text):
    if not text or not text.strip():
        return []

    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    results = []
    seen = set()

    # Metode 1: Format Markdown Link [TICKER](https://stockbit.com/symbol/TICKER)
    i = 0
    found_md = False
    while i < len(lines):
        line = lines[i]
        match = re.search(r'\[([A-Za-z]{4})\]\([^)]+\)', line)
        if match:
            found_md = True
            ticker = match.group(1).upper()
            price = None
            # Telusuri baris berikutnya untuk mencari angka harga (contoh: 66.00, 5,375.00)
            j = i + 1
            while j < min(i + 5, len(lines)):
                next_l = lines[j]
                if re.search(r'\[([A-Za-z]{4})\]', next_l):
                    break
                clean_val = next_l.replace(',', '').replace(' ', '')
                if re.fullmatch(r'\d+(\.\d+)?', clean_val):
                    p = float(clean_val)
                    if p > 0:
                        price = int(round(p))
                        break
                j += 1
            
            if ticker not in seen:
                seen.add(ticker)
                results.append({"ticker": ticker, "price": price})
        i += 1

    if found_md and results:
        return results

    # Metode 2: Baris berisi Ticker dan Harga (misal: "MSKY 66.00" atau "MSKY\t66.00")
    for line in lines:
        m_line = re.match(r'^([A-Za-z]{4})\s+([\d,\.]+)', line)
        if m_line:
            t = m_line.group(1).upper()
            p_str = m_line.group(2).replace(',', '')
            try:
                p_val = int(round(float(p_str)))
            except:
                p_val = None
            if t not in seen and t not in ["NAME", "CODE", "OPEN", "HIGH", "LOWS", "LAST"]:
                seen.add(t)
                results.append({"ticker": t, "price": p_val})

    if results:
        return results

    # Metode 3: Fallback - Deteksi seluruh kata 4 huruf kapital
    words = re.findall(r'\b[A-Za-z]{4}\b', text)
    excluded = {
        "OPEN", "HIGH", "LOWS", "LAST", "PREV", "CHG", "DIFF", "TIME", "DATE",
        "CORP", "ISSI", "YEAR", "WEEK", "DAYS", "VALU", "FREQ", "SPIK", "BAND",
        "MA20", "VOLU", "RETU", "PRIC", "SYMB", "TRUE", "NONE"
    }
    for w in words:
        ticker = w.upper()
        if ticker not in excluded and ticker not in seen:
            seen.add(ticker)
            results.append({"ticker": ticker, "price": None})

    return results

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
                    "sl": 48,
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
                    "sl": 48,
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
                    "sl": 58,
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
                    "sl": 48,
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
            ],
            "failed_history": [
                {
                    "ticker": "ZINC",
                    "is_syariah": True,
                    "entry_date": "2026-07-05",
                    "exit_date": "2026-07-18",
                    "hold_days": 10,
                    "entry_price": 50,
                    "exit_price": 47,
                    "loss_pct": -6.0,
                    "sl": 48,
                    "status_exit": "KENA SL 🛑",
                    "note": "Turun menembus level SL 48, cut loss disiplin"
                }
            ]
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, indent=2)
        return initial_data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "failed_history" not in data:
            data["failed_history"] = []
        for s in data.get("active_stocks", []):
            if "sl" not in s:
                s["sl"] = 0
        return data

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
# STATISTIK KARTU METRIK (ALL-TIME & BULAN PILIHAN)
# ==========================================
active_list = data["active_stocks"]
history_list = data["awakened_history"]
failed_list = data.get("failed_history", [])

today = datetime.date.today()
current_ym = today.strftime("%Y-%m")
MONTH_NAMES = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

def format_ym_label(ym_str):
    try:
        parts = str(ym_str).split("-")
        y = int(parts[0])
        m = int(parts[1])
        return f"{MONTH_NAMES.get(m, m)} {y}"
    except:
        return str(ym_str)

# Kumpulkan seluruh bulan yang ada di data (Bulan Ini + Histori Bangun + Histori Gagal + Aktif)
all_yms = set()
all_yms.add(current_ym)

for h in history_list:
    awk = h.get("awakened_date")
    if awk and len(str(awk)) >= 7:
        all_yms.add(str(awk)[:7])
    ent = h.get("entry_date")
    if ent and len(str(ent)) >= 7:
        all_yms.add(str(ent)[:7])

for f in failed_list:
    ex = f.get("exit_date")
    if ex and len(str(ex)) >= 7:
        all_yms.add(str(ex)[:7])
    ent = f.get("entry_date")
    if ent and len(str(ent)) >= 7:
        all_yms.add(str(ent)[:7])

for s in active_list:
    ent = s.get("entry_date")
    if ent and len(str(ent)) >= 7:
        all_yms.add(str(ent)[:7])

# Urutkan bulan dari yang terbaru ke terlama (Index 0 = Bulan Terbaru sebagai Default)
sorted_yms = sorted(list(all_yms), reverse=True)
month_options_map = {ym: format_ym_label(ym) for ym in sorted_yms}

# Header Ringkasan & Pemilih Bulan Fleksibel
col_stat_title, col_stat_sel = st.columns([3.5, 1.5])
with col_stat_title:
    st.markdown("##### 📈 Ringkasan Performa & Statistik Winrate")
with col_stat_sel:
    selected_ym = st.selectbox(
        "📅 Pilih Bulan Evaluasi:",
        options=sorted_yms,
        format_func=lambda x: month_options_map[x],
        index=0,  # Default: bulan terbaru
        key="select_eval_month",
        help="Pilih bulan untuk mengevaluasi performa dan winrate (Default: bulan terbaru)."
    )

selected_month_label = month_options_map[selected_ym]

# 1. Statistik All-Time (Seluruh Watchlist yang Selesai)
total_awakened = len(history_list)
total_failed = len(failed_list)
total_closed = total_awakened + total_failed

win_count = sum(1 for h in history_list if h.get("gain_pct", 0) >= 0)
loss_count = sum(1 for h in history_list if h.get("gain_pct", 0) < 0) + total_failed
winrate_all = (win_count / total_closed * 100) if total_closed > 0 else 0.0

total_gain = sum(h.get("gain_pct", 0) for h in history_list) + sum(f.get("loss_pct", 0) for f in failed_list)
avg_gain_all = (total_gain / total_closed) if total_closed > 0 else 0.0

active_total = len(active_list)
active_syariah = sum(1 for s in active_list if s.get("is_syariah", False))
active_win = sum(1 for s in active_list if s.get("current_price", 0) >= s.get("entry_price", 0))
active_winrate = (active_win / active_total * 100) if active_total > 0 else 0.0

# Saham aktif yang sudah menyentuh / di bawah batas SL
hit_sl_active = sum(1 for s in active_list if s.get("sl", 0) > 0 and s.get("current_price", 0) <= s.get("sl", 0))

grand_total_emiten = total_closed + active_total
grand_total_win = win_count + active_win
grand_winrate = (grand_total_win / grand_total_emiten * 100) if grand_total_emiten > 0 else 0.0

# 2. Statistik Khusus Bulan Terpilih (Default: Bulan Terbaru)
month_history = [h for h in history_list if str(h.get("awakened_date", "")).startswith(selected_ym)]
month_failed = [f for f in failed_list if str(f.get("exit_date", "")).startswith(selected_ym)]
month_closed = len(month_history) + len(month_failed)
month_win = sum(1 for h in month_history if h.get("gain_pct", 0) >= 0)
month_loss = month_closed - month_win
winrate_month = (month_win / month_closed * 100) if month_closed > 0 else 0.0
month_gain = sum(h.get("gain_pct", 0) for h in month_history) + sum(f.get("loss_pct", 0) for f in month_failed)
avg_gain_month = (month_gain / month_closed) if month_closed > 0 else 0.0

month_active_entered = [s for s in active_list if str(s.get("entry_date", "")).startswith(selected_ym)]
month_new_entries = len(month_active_entered)

# 3. Hitung Siaga Dekat TP / Floating Profit
near_tp_count = 0
for s in active_list:
    entry = s.get("entry_price", 0)
    curr = s.get("current_price", 0)
    tp1 = s.get("tp1") or 0
    if curr > entry:
        if tp1 == 0 or curr < tp1:
            near_tp_count += 1

# Tampilan 6 Kolom Kartu Metrik
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Saham Dipantau", f"{active_total} Emiten", f"{active_syariah} Syariah")
m2.metric(
    "Status Siaga ⚡",
    f"{near_tp_count} Dekat TP",
    f"🚨 {hit_sl_active} Kena SL!" if hit_sl_active > 0 else "Floating Profit"
)
m3.metric(
    "Hasil Selesai 🏁",
    f"{total_closed} Emiten",
    f"🏆 {total_awakened} Bangun | 🛑 {total_failed} SL"
)
m4.metric("Winrate Total 🎯", f"{winrate_all:.1f}%", f"{win_count} Win / {loss_count} Loss")
m5.metric(
    f"Winrate {selected_month_label} 📅",
    f"{winrate_month:.1f}%" if month_closed > 0 else "0.0%",
    f"{month_win} Win / {month_loss} Loss" if month_closed > 0 else "Belum ada exit"
)
m6.metric(
    "Rata-rata Cuan/Trade 📈",
    f"{avg_gain_all:+.2f}%",
    f"{selected_month_label}: {avg_gain_month:+.2f}%" if month_closed > 0 else "All-Time"
)

# Expander Rincian Statistik
with st.expander(f"📊 Rincian Komparasi Winrate: Seluruh Watchlist vs Periode {selected_month_label}"):
    c_stat1, c_stat2 = st.columns(2)
    with c_stat1:
        st.markdown(f"##### 🌐 Seluruh Watchlist (All-Time)")
        st.markdown(f"""
        - **Total Saham Selesai Trade**: **{total_closed} Emiten** (🏆 {total_awakened} Bangun Cuan / 🛑 {total_failed} Gagal Kena SL)
        - **Winrate Realisasi**: **{winrate_all:.1f}%** ({win_count} Menang / {loss_count} Kalah)
        - **Rata-rata Hasil Per Trade**: **{avg_gain_all:+.2f}%**
        - **Saham Aktif di Watchlist**: **{active_total} Emiten** ({active_win} emiten floating profit / **{active_winrate:.1f}%**)
        - **Posisi Aktif Kena SL**: **{hit_sl_active} Emiten**
        - **Winrate Akumulasi (Selesai + Aktif)**: **{grand_winrate:.1f}%** ({grand_total_win} dari {grand_total_emiten} posisi hijau)
        """)
    with c_stat2:
        st.markdown(f"##### 📅 Khusus Periode {selected_month_label}")
        st.markdown(f"""
        - **Saham Selesai di {selected_month_label}**: **{month_closed} Emiten** ({len(month_history)} Bangun Cuan / {len(month_failed)} Gagal SL)
        - **Winrate Periode Ini**: **{winrate_month:.1f}%** ({month_win} Menang / {month_loss} Kalah)
        - **Rata-rata Hasil Periode Ini**: **{avg_gain_month:+.2f}%**
        - **Saham Baru Masuk Watchlist di {selected_month_label}**: **{month_new_entries} Emiten**
        """)

st.markdown("---")

# ==========================================
# TABEL 1: WATCHLIST SAHAM TIDUR (AKTIF)
# ==========================================
col_tbl_title, col_tbl_refresh = st.columns([3.6, 1.4])
with col_tbl_title:
    st.subheader("📋 Daftar Saham Tidur (Aktif Dipantau)")
with col_tbl_refresh:
    if st.button("🔄 Refresh Harga Terkini", key="btn_refresh_watchlist_table", use_container_width=True, help="Klik untuk memperbarui harga bursa terkini secara manual"):
        with st.spinner("Mengambil harga penutupan bursa..."):
            updated_count = 0
            for s in data["active_stocks"]:
                price = fetch_latest_price(s["ticker"])
                if price:
                    s["current_price"] = price
                    updated_count += 1
            save_data(data)
            st.toast(f"Berhasil refresh {updated_count} harga saham!", icon="✅")
            st.rerun()

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
    
    sl_val = s.get("sl") or 0
    tp1_val = s.get("tp1") or 0
    tp2_val = s.get("tp2") or 0
    tp3_val = s.get("tp3") or 0

    sl_str = f"Rp {sl_val} ({((sl_val - entry) / entry * 100):.1f}%)" if sl_val > 0 else "-"
    tp1_str = f"Rp {tp1_val} (+{((tp1_val - entry) / entry * 100):.1f}%)" if tp1_val > 0 else "-"
    tp2_str = f"Rp {tp2_val} (+{((tp2_val - entry) / entry * 100):.1f}%)" if tp2_val > 0 else "-"
    tp3_str = f"Rp {tp3_val} (+{((tp3_val - entry) / entry * 100):.1f}%)" if tp3_val > 0 else "-"
    hold_work_days = calculate_working_days(s["entry_date"])

    # Status Dinamis (Prioritas: Kena SL > Dekat SL > TP > Floating Profit/Loss > Masih Tidur)
    if sl_val > 0 and curr <= sl_val:
        status = f"KENA SL (Rp {sl_val}) 🛑"
    elif sl_val > 0 and curr <= (sl_val * 1.03):
        diff_sl = curr - sl_val
        status = f"DEKAT SL (Sisa {diff_sl} pt) 🚨"
    elif tp3_val > 0 and curr >= tp3_val:
        status = "TP 3 TERCAPAI 🏆"
    elif tp2_val > 0 and curr >= tp2_val:
        status = "TP 2 TEMBUS 🎯"
    elif tp1_val > 0 and curr >= tp1_val:
        status = "TP 1 TERCAPAI 🎯"
    elif tp1_val > 0 and curr > entry:
        diff_tp1 = tp1_val - curr
        status = f"DEKAT TP 1 (Sisa {diff_tp1} pt) ⚡"
    elif curr > entry:
        status = f"FLOATING PROFIT 📈 (+{gain_pct:.1f}%)"
    elif curr < entry:
        status = f"FLOATING LOSS 🔻 ({gain_pct:.1f}%)"
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
        "SL": sl_str,
        "TP 1": tp1_str,
        "TP 2": tp2_str,
        "TP 3": tp3_str,
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
            "SL": st.column_config.TextColumn("Stop Loss (SL)"),
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
    tab_quick_import, tab_bungkus, tab_sl, tab_add, tab_manage_active, tab_manage_hist = st.tabs([
        "⚡ Quick Import Stockbit",
        "💰 Bungkus Cuan (Take Profit)",
        "🛑 Realisasi SL (Gagal Bangun)",
        "➕ Tambah Satuan",
        "⚙️ Kelola Watchlist (Centang Hapus / Edit)",
        "📜 Kelola Histori (Bangun & Gagal Bangun)"
    ])

    # ----------------------------------------------------
    # TAB 1: QUICK IMPORT STOCKBIT (DUAL SCREENER: SYARIAH & NON-SYARIAH)
    # ----------------------------------------------------
    with tab_quick_import:
        st.markdown("##### ⚡ Quick Import Hasil Screener Stockbit")
        st.markdown("""
        Salin langsung seluruh teks hasil tabel screener dari Stockbit ke kotak di bawah.
        Kedua kolom bersifat **fleksibel / opsional**: Anda dapat mengisi **salah satu saja** atau **kedua-duanya sekaligus**.
        """)

        st.info("🛡️ **Proteksi Anti-Duplikasi Aktif**: Saham yang sudah tercatat di watchlist tidak akan terduplikasi. Tanggal masuk pertama dan harga modal awal akan **tetap dikunci (dipertahankan)**.")

        col_syariah, col_non_syariah = st.columns(2)
        with col_syariah:
            st.markdown("##### 🕌 1. Screener Syariah (Universe: ISSI)")
            st.caption("Tempel hasil screener Stockbit dengan filter **Stock Universe: ISSI** di sini. Otomatis ditandai **Syariah**.")
            screener_syariah = st.text_area(
                "Teks Screener Syariah (ISSI):",
                height=190,
                placeholder="Contoh:\nSymbol\nPrice\n[MSKY](https://stockbit.com/symbol/MSKY)\n66.00\n[ASPR](https://stockbit.com/symbol/ASPR)\n146.00\n...",
                key="screener_syariah_area",
                help="Seluruh emiten di kolom ini otomatis dicatat sebagai Saham Syariah (ISSI)."
            )

        with col_non_syariah:
            st.markdown("##### 🏢 2. Screener IHSG / Non-Syariah *(Opsional)*")
            st.caption("Tempel hasil screener Stockbit dengan filter **Stock Universe: IHSG / All Stocks** di sini.")
            screener_non_syariah = st.text_area(
                "Teks Screener IHSG / Non-Syariah (Opsional):",
                height=190,
                placeholder="Contoh:\nSymbol\nPrice\n[BBRI](https://stockbit.com/symbol/BBRI)\n5000.00\n...",
                key="screener_non_syariah_area",
                help="Jika Kolom 1 diisi, emiten di Kolom 2 yang tidak ada di Kolom 1 otomatis ditandai Non-Syariah."
            )

        qc1, qc2 = st.columns(2)
        with qc1:
            batch_entry_date = st.date_input("Tanggal Masuk untuk Saham Baru:", datetime.date.today(), key="batch_date_in")
        with qc2:
            right_only_mode = "🏢 Tandai Seluruhnya sebagai Non-Syariah"
            if screener_non_syariah.strip() and not screener_syariah.strip():
                right_only_mode = st.radio(
                    "Perlakuan Kolom Kanan (karena Kolom Kiri kosong):",
                    ["🏢 Tandai Seluruhnya sebagai Non-Syariah", "🕌 Tandai Seluruhnya sebagai Syariah"],
                    index=0,
                    key="right_only_syariah_mode",
                    horizontal=True
                )
            else:
                st.caption("💡 **Auto-Deteksi**: Jika kedua kolom diisi, emiten yang hanya ada di Kolom Kanan otomatis diklasifikasikan sebagai **🏢 Non-Syariah**.")

        if st.button("🚀 Proses & Impor Saham ke Watchlist", type="primary", use_container_width=True, key="btn_process_batch_import"):
            text_syariah = screener_syariah.strip()
            text_non = screener_non_syariah.strip()

            if not text_syariah and not text_non:
                st.warning("Kedua kotak teks masih kosong. Silakan copy-paste tabel screener ke Kolom Kiri (Syariah), Kolom Kanan (Non-Syariah), atau keduanya.")
            else:
                with st.spinner("Mengekstrak kode saham, memilah status syariah & memeriksa status duplikasi..."):
                    parsed_syariah = parse_stockbit_screener(text_syariah) if text_syariah else []
                    parsed_non = parse_stockbit_screener(text_non) if text_non else []

                    combined_candidates = []
                    seen_in_batch = set()

                    # 1. Proses emiten dari Kolom Syariah (ISSI)
                    for item in parsed_syariah:
                        t = item["ticker"]
                        if t not in seen_in_batch:
                            seen_in_batch.add(t)
                            combined_candidates.append({
                                "ticker": t,
                                "price": item["price"],
                                "is_syariah": True,
                                "source": "🕌 Kolom Syariah (ISSI)"
                            })

                    # 2. Proses emiten dari Kolom Non-Syariah / IHSG
                    is_right_syariah_fallback = False
                    if text_non and not text_syariah:
                        is_right_syariah_fallback = ("Syariah" in right_only_mode and "Non-Syariah" not in right_only_mode)

                    for item in parsed_non:
                        t = item["ticker"]
                        if t not in seen_in_batch:
                            seen_in_batch.add(t)
                            syariah_flag = is_right_syariah_fallback if (not text_syariah) else False
                            src_label = "🏢 Kolom IHSG (Non-Syariah)" if not syariah_flag else "🕌 Kolom Kanan (Syariah)"
                            combined_candidates.append({
                                "ticker": t,
                                "price": item["price"],
                                "is_syariah": syariah_flag,
                                "source": src_label
                            })

                    if not combined_candidates:
                        st.error("Tidak ada kode saham yang terdeteksi dari teks yang ditempel. Pastikan teks memuat kode saham 4 huruf.")
                    else:
                        existing_active = {s["ticker"]: s for s in data["active_stocks"]}
                        new_added = []
                        skipped = []

                        for item in combined_candidates:
                            ticker = item["ticker"]
                            price = item["price"]
                            is_syariah = item["is_syariah"]

                            # Proteksi Anti-Duplikasi (First Entry Lock)
                            if ticker in existing_active:
                                old = existing_active[ticker]
                                skipped.append({
                                    "Kode": ticker,
                                    "Status": "🛡️ DILEWATI (SUDAH ADA)",
                                    "Keterangan": f"Sudah masuk sejak {old.get('entry_date')} @ Rp {old.get('entry_price')} (Data lama dipertahankan)"
                                })
                            else:
                                if price is None or price <= 0:
                                    live_p = fetch_latest_price(ticker)
                                    price = live_p if live_p else 50

                                is_fca = (price <= 50)
                                new_stock = {
                                    "ticker": ticker,
                                    "is_syariah": is_syariah,
                                    "entry_date": str(batch_entry_date),
                                    "entry_price": int(price),
                                    "current_price": int(price),
                                    "sl": 0,
                                    "tp1": 0,
                                    "tp2": 0,
                                    "tp3": 0,
                                    "is_fca": is_fca
                                }
                                data["active_stocks"].append(new_stock)
                                new_added.append({
                                    "Kode": ticker,
                                    "Harga Masuk": f"Rp {price}",
                                    "Tgl Masuk": str(batch_entry_date),
                                    "Kategori": "🕌 Syariah (ISSI)" if is_syariah else "🏢 Non-Syariah",
                                    "Sumber": item["source"],
                                    "Status": "✅ Baru Masuk Watchlist"
                                })

                        if new_added:
                            save_data(data)

                        st.markdown("---")
                        st.markdown("#### 📋 Laporan Hasil Import:")

                        if new_added:
                            syariah_count = sum(1 for x in new_added if "Syariah" in x["Kategori"] and "Non-Syariah" not in x["Kategori"])
                            non_count = len(new_added) - syariah_count
                            st.success(f"🎉 **{len(new_added)} Saham Baru Berhasil Ditambahkan ke Watchlist!** ({syariah_count} Syariah 🕌, {non_count} Non-Syariah 🏢)")
                            st.dataframe(pd.DataFrame(new_added), use_container_width=True, hide_index=True)

                        if skipped:
                            st.warning(f"🛡️ **{len(skipped)} Saham Dilewati (Anti-Duplikasi)**: Saham ini sudah ada sebelumnya di watchlist sehingga tanggal masuk dan modal awal tetap aman terlindungi.")
                            st.dataframe(pd.DataFrame(skipped), use_container_width=True, hide_index=True)

                        if st.button("🔄 Segarkan Tampilan Dashboard", type="secondary", key="btn_refresh_after_batch"):
                            st.rerun()

    # ----------------------------------------------------
    # TAB 2: BUNGKUS CUAN
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
                tp1_target = selected_stock.get("tp1") or 0
                new_hist = {
                    "ticker": selected_stock["ticker"],
                    "is_syariah": selected_stock["is_syariah"],
                    "entry_date": selected_stock["entry_date"],
                    "awakened_date": str(datetime.date.today()),
                    "hold_days": work_days,
                    "entry_price": entry_p,
                    "exit_price": exit_price,
                    "gain_pct": round(realized_gain, 2),
                    "status_exit": "TARGET TP TERCAPAI 🎯" if (tp1_target > 0 and exit_price >= tp1_target) else "BUNGKUS MANUAL 💰",
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
    # TAB 3: REALISASI SL (GAGAL BANGUN)
    # ----------------------------------------------------
    with tab_sl:
        st.markdown("**Eksekusi Cut Loss / Kena SL (Pindahkan ke Tabel Gagal Bangun):**")
        st.caption("Pilih saham yang terkena stop loss atau terpaksa di-cut loss untuk dipindahkan ke riwayat saham gagal bangun.")

        tickers_active = [s["ticker"] for s in active_list]
        if tickers_active:
            sl_breached = [s["ticker"] for s in active_list if s.get("sl", 0) > 0 and s.get("current_price", 0) <= s.get("sl", 0)]
            if sl_breached:
                st.warning(f"🚨 **Peringatan Siaga**: Saham **{', '.join(sl_breached)}** saat ini telah menyentuh atau berada di bawah level Stop Loss!")

            sl_col1, sl_col2, sl_col3 = st.columns(3)
            with sl_col1:
                default_idx = tickers_active.index(sl_breached[0]) if sl_breached else 0
                sel_sl_ticker = st.selectbox("Pilih Saham yang Mau Di-Cut Loss:", tickers_active, index=default_idx, key="sel_sl_ticker")
                sel_sl_stock = next(s for s in active_list if s["ticker"] == sel_sl_ticker)
            with sl_col2:
                default_cut_price = int(sel_sl_stock["current_price"])
                exit_sl_price = st.number_input("Harga Jual / Realisasi Cut Loss (Rp):", min_value=1, value=default_cut_price, key="input_exit_sl_price")
            with sl_col3:
                exit_sl_reason = st.selectbox("Alasan Cut Loss / Gagal Bangun:", [
                    "Terkena Level Stop Loss (Disiplin SL)",
                    "Menembus Support Kunci (Breakdown)",
                    "Volume Pembalikan Negatif",
                    "Sentimen Pasar / Fundamental Memburuk",
                    "Cut Loss Manual (Pindah Modal ke Emiten Lain)"
                ], key="sel_exit_sl_reason")

            entry_p = sel_sl_stock["entry_price"]
            realized_loss = ((exit_sl_price - entry_p) / entry_p * 100) if entry_p > 0 else 0.0
            sl_preset = sel_sl_stock.get("sl") or 0
            
            st.error(f"🛑 Estimasi Realisasi Kerugian: **{realized_loss:.2f}%** (Modal Rp {entry_p} ➔ Jual Rp {exit_sl_price} | Level SL: Rp {sl_preset if sl_preset > 0 else '-'})")

            if st.button("🛑 Konfirmasi Cut Loss ➔ Pindahkan ke Tabel Gagal Bangun", type="primary", key="btn_confirm_cut_loss"):
                work_days = calculate_working_days(sel_sl_stock["entry_date"])
                new_failed = {
                    "ticker": sel_sl_stock["ticker"],
                    "is_syariah": sel_sl_stock["is_syariah"],
                    "entry_date": sel_sl_stock["entry_date"],
                    "exit_date": str(datetime.date.today()),
                    "hold_days": work_days,
                    "entry_price": entry_p,
                    "exit_price": exit_sl_price,
                    "loss_pct": round(realized_loss, 2),
                    "sl": sl_preset,
                    "status_exit": "KENA SL 🛑" if (sl_preset > 0 and exit_sl_price <= sl_preset) else "CUT LOSS MANUAL ✂️",
                    "note": exit_sl_reason
                }
                if "failed_history" not in data:
                    data["failed_history"] = []
                data["failed_history"].insert(0, new_failed)
                data["active_stocks"] = [s for s in data["active_stocks"] if s["ticker"] != sel_sl_ticker]
                save_data(data)
                st.success(f"Saham {sel_sl_ticker} berhasil dipindahkan ke Tabel Saham Gagal Bangun!")
                st.rerun()
        else:
            st.info("Belum ada saham aktif di watchlist untuk di-cut loss.")

    # ----------------------------------------------------
    # TAB 4: TAMBAH SATUAN (MANUAL)
    # ----------------------------------------------------
    with tab_add:
        with st.form("form_add_stock", clear_on_submit=True):
            st.markdown("**Form Tambah Saham Tidur Baru:**")
            a1, a2, a3 = st.columns(3)
            with a1:
                new_ticker = st.text_input("Kode Saham (4 Huruf):", placeholder="cth: BUMI").upper().strip()
                new_syariah = st.checkbox("🕌 Saham Syariah (ISSI)", value=True)
                new_fca = st.checkbox("Masuk Papan FCA (Full Call Auction)", value=False)
            with a2:
                new_entry_date = st.date_input("Tanggal Masuk Watchlist:", datetime.date.today())
                new_entry_price = st.number_input("Harga Waktu Masuk (Rp):", min_value=1, value=50)
                new_sl = st.number_input("Stop Loss / SL (Rp) - Opsional:", min_value=0, value=0, step=1, help="Kosongkan atau isi 0 jika belum ada SL")
            with a3:
                new_tp1 = st.number_input("Target TP 1 (Rp) - Opsional:", min_value=0, value=0, step=1, help="Kosongkan atau isi 0 jika belum ada target TP 1")
                new_tp2 = st.number_input("Target TP 2 (Rp) - Opsional:", min_value=0, value=0, step=1, help="Kosongkan atau isi 0 jika belum ada target TP 2")
                new_tp3 = st.number_input("Target TP 3 (Rp) - Opsional:", min_value=0, value=0, step=1, help="Kosongkan atau isi 0 jika belum ada target TP 3")

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
                        "sl": int(new_sl) if new_sl > 0 else 0,
                        "tp1": int(new_tp1) if new_tp1 > 0 else 0,
                        "tp2": int(new_tp2) if new_tp2 > 0 else 0,
                        "tp3": int(new_tp3) if new_tp3 > 0 else 0,
                        "is_fca": new_fca
                    }
                    data["active_stocks"].append(new_item)
                    save_data(data)
                    st.success(f"Saham {new_ticker} berhasil ditambahkan!")
                    st.rerun()

    # ----------------------------------------------------
    # TAB 5: KELOLA WATCHLIST (CENTANG HAPUS / EDIT TABEL)
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
                    "SL": int(s.get("sl") or 0),
                    "TP 1": int(s.get("tp1") or 0),
                    "TP 2": int(s.get("tp2") or 0),
                    "TP 3": int(s.get("tp3") or 0),
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
                    "SL": st.column_config.NumberColumn("Stop Loss / SL (Rp)", min_value=0, step=1, format="%d", help="0 jika tidak ada"),
                    "TP 1": st.column_config.NumberColumn("Target TP 1 (Rp)", min_value=0, step=1, format="%d", help="0 jika tidak ada"),
                    "TP 2": st.column_config.NumberColumn("Target TP 2 (Rp)", min_value=0, step=1, format="%d", help="0 jika tidak ada"),
                    "TP 3": st.column_config.NumberColumn("Target TP 3 (Rp)", min_value=0, step=1, format="%d", help="0 jika tidak ada"),
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
                            s["sl"] = int(r["SL"]) if (pd.notna(r["SL"]) and r["SL"] > 0) else 0
                            s["tp1"] = int(r["TP 1"]) if (pd.notna(r["TP 1"]) and r["TP 1"] > 0) else 0
                            s["tp2"] = int(r["TP 2"]) if (pd.notna(r["TP 2"]) and r["TP 2"] > 0) else 0
                            s["tp3"] = int(r["TP 3"]) if (pd.notna(r["TP 3"]) and r["TP 3"] > 0) else 0
                            s["is_syariah"] = bool(r["Syariah"])
                            s["is_fca"] = bool(r["FCA"])
                    save_data(data)
                    st.success("Perubahan data watchlist berhasil disimpan!")
                    st.rerun()
        else:
            st.info("Watchlist kosong, belum ada saham untuk diedit/dihapus.")

    # ----------------------------------------------------
    # TAB 6: KELOLA HISTORI (BANGUN & GAGAL BANGUN)
    # ----------------------------------------------------
    with tab_manage_hist:
        st.markdown("##### 📜 Edit & Hapus Data Histori")
        st.caption("Kelola riwayat saham yang berhasil bangun maupun yang terkena cut loss/SL.")
        sub_hist_cuan, sub_hist_gagal = st.tabs(["🏆 Histori Saham Bangun (Cuan)", "🛑 Histori Gagal Bangun (Kena SL)"])

        with sub_hist_cuan:
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
                    if st.button("🗑️ Hapus Histori Cuan yang Dicentang", type="secondary", use_container_width=True, key="btn_del_hist_cuan"):
                        delete_ids = edited_hist_df[edited_hist_df["Hapus"] == True]["_id"].tolist()
                        if not delete_ids:
                            st.warning("Silakan centang minimal satu baris histori di kolom 'Pilih Hapus 🗑️' terlebih dahulu.")
                        else:
                            data["awakened_history"] = [h for idx, h in enumerate(data["awakened_history"]) if idx not in delete_ids]
                            save_data(data)
                            st.success(f"Berhasil menghapus {len(delete_ids)} data histori cuan.")
                            st.rerun()

                with hcol2:
                    if st.button("💾 Simpan Perubahan Data Histori Cuan", type="primary", use_container_width=True, key="btn_save_hist_cuan"):
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

        with sub_hist_gagal:
            failed_history_data = data.get("failed_history", [])
            if failed_history_data:
                gagal_rows = []
                for idx, g in enumerate(failed_history_data):
                    gagal_rows.append({
                        "Hapus": False,
                        "_id": idx,
                        "Kode": g["ticker"],
                        "Tgl Masuk": g.get("entry_date", "-"),
                        "Tgl Cut Loss": g.get("exit_date", "-"),
                        "Harga Masuk": int(g.get("entry_price", 0)),
                        "Harga Jual": int(g.get("exit_price", 0)),
                        "SL Terpasang": int(g.get("sl", 0)),
                        "Status Exit": g.get("status_exit", "KENA SL 🛑"),
                        "Catatan": g.get("note", "")
                    })
                df_manage_gagal = pd.DataFrame(gagal_rows)
                edited_gagal_df = st.data_editor(
                    df_manage_gagal,
                    column_config={
                        "Hapus": st.column_config.CheckboxColumn("Pilih Hapus 🗑️", help="Centang baris yang ingin dihapus", default=False),
                        "_id": None,
                        "Kode": st.column_config.TextColumn("Kode Saham", disabled=True),
                        "Tgl Masuk": st.column_config.TextColumn("Tgl Masuk (YYYY-MM-DD)"),
                        "Tgl Cut Loss": st.column_config.TextColumn("Tgl Cut Loss (YYYY-MM-DD)"),
                        "Harga Masuk": st.column_config.NumberColumn("Harga Masuk (Rp)", min_value=1, step=1, format="%d"),
                        "Harga Jual": st.column_config.NumberColumn("Harga Jual (Rp)", min_value=1, step=1, format="%d"),
                        "SL Terpasang": st.column_config.NumberColumn("SL Terpasang (Rp)", min_value=0, step=1, format="%d"),
                        "Status Exit": st.column_config.TextColumn("Status Exit"),
                        "Catatan": st.column_config.TextColumn("Catatan / Alasan Cut Loss"),
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="table_editor_gagal"
                )

                gcol1, gcol2 = st.columns(2)
                with gcol1:
                    if st.button("🗑️ Hapus Histori Gagal yang Dicentang", type="secondary", use_container_width=True, key="btn_del_gagal"):
                        del_gagal_ids = edited_gagal_df[edited_gagal_df["Hapus"] == True]["_id"].tolist()
                        if not del_gagal_ids:
                            st.warning("Silakan centang minimal satu baris yang ingin dihapus.")
                        else:
                            data["failed_history"] = [g for idx, g in enumerate(data["failed_history"]) if idx not in del_gagal_ids]
                            save_data(data)
                            st.success(f"Berhasil menghapus {len(del_gagal_ids)} data histori gagal bangun.")
                            st.rerun()

                with gcol2:
                    if st.button("💾 Simpan Perubahan Histori Gagal", type="primary", use_container_width=True, key="btn_save_gagal"):
                        new_failed_list = []
                        for _, r in edited_gagal_df.iterrows():
                            entry_p = int(r["Harga Masuk"])
                            exit_p = int(r["Harga Jual"])
                            recalculated_loss = round(((exit_p - entry_p) / entry_p * 100), 2) if entry_p > 0 else 0.0
                            tgl_masuk = str(r["Tgl Masuk"]).strip()
                            tgl_cut = str(r["Tgl Cut Loss"]).strip()
                            hold_days = calculate_working_days(tgl_masuk, tgl_cut)

                            orig_idx = int(r["_id"])
                            orig_syariah = data["failed_history"][orig_idx].get("is_syariah", True) if orig_idx < len(data["failed_history"]) else True

                            new_failed_list.append({
                                "ticker": str(r["Kode"]),
                                "is_syariah": orig_syariah,
                                "entry_date": tgl_masuk,
                                "exit_date": tgl_cut,
                                "hold_days": hold_days,
                                "entry_price": entry_p,
                                "exit_price": exit_p,
                                "loss_pct": recalculated_loss,
                                "sl": int(r["SL Terpasang"]),
                                "status_exit": str(r["Status Exit"]),
                                "note": str(r["Catatan"])
                            })
                        data["failed_history"] = new_failed_list
                        save_data(data)
                        st.success("Perubahan data histori gagal bangun berhasil disimpan!")
                        st.rerun()
            else:
                st.info("Belum ada histori saham gagal bangun untuk diedit/dihapus.")

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
        mime="text/csv",
        key="btn_download_csv_cuan"
    )
else:
    st.info("Tidak ada riwayat histori cuan yang sesuai dengan filter.")

st.markdown("---")

# ==========================================
# TABEL 3: SAHAM GAGAL BANGUN (TERKENA SL / CUT LOSS)
# ==========================================
st.subheader("🛑 Saham Gagal Bangun / Terkena SL (Histori Cut Loss)")

# Filter Bar Gagal Bangun
gf_col1, gf_col2, gf_col3 = st.columns([1.5, 1.5, 2])
with gf_col1:
    syariah_gagal_filter = st.selectbox(
        "🕌 Filter Syariah Gagal Bangun:",
        ["Semua Histori", "Hanya Syariah (ISSI)", "Hanya Non-Syariah"],
        key="filter_gagal_syariah"
    )
with gf_col2:
    search_gagal_query = st.text_input("🔍 Cari Kode Saham Gagal:", placeholder="misal: ZINC", key="search_gagal")
with gf_col3:
    date_filter_gagal = st.date_input(
        "📅 Filter Tgl Cut Loss (Rentang / 1 Hari):",
        value=(),
        key="date_filter_gagal",
        help="Pilih 1 tanggal atau 2 tanggal untuk rentang periode cut loss. Kosongkan untuk semua."
    )

# Filter logic Gagal Bangun
failed_list_data = data.get("failed_history", [])
filtered_gagal = []
for g in failed_list_data:
    if syariah_gagal_filter == "Hanya Syariah (ISSI)" and not g.get("is_syariah", True):
        continue
    if syariah_gagal_filter == "Hanya Non-Syariah" and g.get("is_syariah", True):
        continue
    if search_gagal_query:
        qg = search_gagal_query.upper().strip()
        if qg not in g["ticker"].upper():
            continue
    if not is_date_in_filter(g.get("exit_date"), date_filter_gagal):
        continue
    filtered_gagal.append(g)

# Default urutkan dari tanggal cut loss terbaru ke terlama (descending)
filtered_gagal.sort(key=lambda x: str(x.get("exit_date", x.get("entry_date", ""))), reverse=True)

# Siapkan DataFrame Gagal Bangun (Tanpa Kolom Nama)
display_gagal = []
for g in filtered_gagal:
    entry_p = int(g.get("entry_price", 0))
    exit_p = int(g.get("exit_price", 0))
    loss_p = float(g.get("loss_pct", 0.0))
    sl_val = int(g.get("sl", 0))
    hold_days = int(g.get("hold_days", 0))

    display_gagal.append({
        "Kode": g["ticker"],
        "Syariah": "🕌 Syariah" if g.get("is_syariah", True) else "Non-Syariah",
        "Tgl Masuk": g.get("entry_date", "-"),
        "Tgl Cut Loss": g.get("exit_date", "-"),
        "Lama Hold": hold_days,
        "Harga Masuk": entry_p,
        "Harga Cut Loss": exit_p,
        "Realisasi Rugi (%)": round(loss_p, 2),
        "Target SL Terpasang": f"Rp {sl_val}" if sl_val > 0 else "-",
        "Status Exit": g.get("status_exit", "KENA SL 🛑"),
        "Catatan": g.get("note", "-")
    })

df_gagal = pd.DataFrame(display_gagal)
if not df_gagal.empty:
    st.dataframe(
        df_gagal,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Kode": st.column_config.TextColumn("Kode"),
            "Syariah": st.column_config.TextColumn("Syariah"),
            "Tgl Masuk": st.column_config.TextColumn("Tgl Masuk"),
            "Tgl Cut Loss": st.column_config.TextColumn("Tgl Cut Loss"),
            "Lama Hold": st.column_config.NumberColumn("Lama Hold", format="%d Hari Kerja"),
            "Harga Masuk": st.column_config.NumberColumn("Harga Masuk", format="Rp %d"),
            "Harga Cut Loss": st.column_config.NumberColumn("Harga Cut Loss", format="Rp %d"),
            "Realisasi Rugi (%)": st.column_config.NumberColumn("Realisasi Rugi", format="%.2f%%"),
            "Target SL Terpasang": st.column_config.TextColumn("Level SL"),
            "Status Exit": st.column_config.TextColumn("Status Exit"),
            "Catatan": st.column_config.TextColumn("Catatan / Alasan"),
        }
    )
    df_gagal_export = df_gagal.copy()
    df_gagal_export["Lama Hold"] = df_gagal_export["Lama Hold"].apply(lambda x: f"{x} Hari Kerja")
    csv_gagal = df_gagal_export.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Export Histori Gagal Bangun ke .CSV",
        data=csv_gagal,
        file_name=f"histori_saham_gagal_bangun_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="btn_download_csv_gagal"
    )
else:
    st.info("Tidak ada riwayat saham gagal bangun (terkena SL) yang sesuai dengan filter.")
