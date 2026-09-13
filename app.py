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
    page_title="IDX Stock Radar",
    page_icon="📡",
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
                    "ticker": "DIST",
                    "is_syariah": True,
                    "entry_date": "2026-09-10",
                    "entry_price": 50,
                    "current_price": 50,
                    "sl": 0,
                    "tp1": 0,
                    "tp2": 0,
                    "tp3": 0,
                    "is_fca": True
                },
                {
                    "ticker": "ROTI",
                    "is_syariah": True,
                    "entry_date": "2026-09-10",
                    "entry_price": 585,
                    "current_price": 585,
                    "sl": 0,
                    "tp1": 0,
                    "tp2": 0,
                    "tp3": 0,
                    "is_fca": False
                },
                {
                    "ticker": "GULA",
                    "is_syariah": True,
                    "entry_date": "2026-09-10",
                    "entry_price": 810,
                    "current_price": 810,
                    "sl": 0,
                    "tp1": 0,
                    "tp2": 0,
                    "tp3": 0,
                    "is_fca": False
                },
                {
                    "ticker": "BEEF",
                    "is_syariah": False,
                    "entry_date": "2026-09-10",
                    "entry_price": 438,
                    "current_price": 438,
                    "sl": 0,
                    "tp1": 0,
                    "tp2": 0,
                    "tp3": 0,
                    "is_fca": False
                },
                {
                    "ticker": "GWSA",
                    "is_syariah": True,
                    "entry_date": "2026-09-09",
                    "entry_price": 173,
                    "current_price": 172,
                    "sl": 0,
                    "tp1": 0,
                    "tp2": 0,
                    "tp3": 0,
                    "is_fca": False
                },
                {
                    "ticker": "MSKY",
                    "is_syariah": True,
                    "entry_date": "2026-09-09",
                    "entry_price": 66,
                    "current_price": 82,
                    "sl": 0,
                    "tp1": 0,
                    "tp2": 0,
                    "tp3": 0,
                    "is_fca": False
                },
                {
                    "ticker": "ATAP",
                    "is_syariah": True,
                    "entry_date": "2026-09-09",
                    "entry_price": 560,
                    "current_price": 565,
                    "sl": 0,
                    "tp1": 0,
                    "tp2": 0,
                    "tp3": 0,
                    "is_fca": False
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

    with open(DATA_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
        if "failed_history" not in data:
            data["failed_history"] = []
        for s in data.get("active_stocks", []):
            if "sl" not in s:
                s["sl"] = 0
            if "category" not in s:
                s["category"] = "Saham Tidur"
        for h in data.get("awakened_history", []):
            if "category" not in h:
                h["category"] = "Saham Tidur"
        for f in data.get("failed_history", []):
            if "category" not in f:
                f["category"] = "Saham Tidur"
        return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

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

        # BACKUP & RESTORE DATABASE JSON
        st.markdown("---")
        st.markdown("##### 💾 Backup Database")
        st.caption("Unduh salinan data untuk disimpan di laptop Anda:")
        json_backup_str = json.dumps(data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Download stocks_data.json",
            data=json_backup_str,
            file_name=f"stocks_data_backup_{datetime.date.today().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
            help="Download seluruh isi database saham aktif, riwayat cuan, dan cut loss dalam format JSON."
        )

        with st.expander("📤 Pulihkan / Restore Data JSON"):
            st.caption("Upload file backup JSON jika ingin mengembalikan data:")
            uploaded_json = st.file_uploader("Upload JSON Backup:", type=["json"], key="uploader_restore_json")
            if uploaded_json is not None:
                if st.button("♻️ Pulihkan Data Sekarang", type="primary", use_container_width=True, key="btn_apply_restore"):
                    try:
                        raw_bytes = uploaded_json.getvalue()
                        restored = json.loads(raw_bytes.decode("utf-8-sig"))
                        if "active_stocks" in restored:
                            save_data(restored)
                            st.session_state["data"] = restored
                            st.success("Data berhasil dipulihkan dari backup JSON!")
                            st.rerun()
                        else:
                            st.error("Format JSON tidak valid!")
                    except Exception as e:
                        st.error(f"Gagal memulihkan: {e}")
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
    st.title("📡 IDX Stock Radar")
    st.caption("Pantau saham, evaluasi, pantau, dan amankan profit")

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
# DATA LIST & HELPER STATISTIK
# ==========================================
active_list = data["active_stocks"]
history_list = data["awakened_history"]
failed_list = data.get("failed_history", [])

today = datetime.date.today()
current_month_real = today.month
current_year_real = today.year

MONTH_NAMES = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

SCREENER_CATEGORIES = [
    "Flow Masuk",
    "Flow Masuk + Fundamental OK",
    "Saham Tidur"
]

# ==========================================
# 1. PANEL STATISTIK & EVALUASI WIN RATE (COLLAPSIBLE / HIDE-SHOW)
# ==========================================
with st.expander("📊 Statistik & Evaluasi Win Rate (Klik untuk Buka / Tutup)", expanded=True):
    st.markdown("##### ⚙️ Filter Evaluasi Statistik")
    sc_c1, sc_c2, sc_c3 = st.columns([2, 1.5, 1.5])
    with sc_c1:
        stat_category = st.selectbox(
            "🎯 Filter Kategori Screener:",
            ["Semua Hasil Screener"] + SCREENER_CATEGORIES,
            key="stat_filter_category",
            help="Pilih kategori screener yang ingin dievaluasi performa dan win rate-nya."
        )
    with sc_c2:
        stat_month = st.selectbox(
            "📅 Pilih Bulan Evaluasi:",
            options=list(range(1, 13)),
            format_func=lambda m: MONTH_NAMES[m],
            index=current_month_real - 1,  # Default bulan real-time saat ini
            key="stat_filter_month",
            help="Default bulan mengikuti waktu riil saat ini."
        )
    with sc_c3:
        year_options = [current_year_real - 2, current_year_real - 1, current_year_real, current_year_real + 1]
        stat_year = st.selectbox(
            "🗓️ Pilih Tahun:",
            options=year_options,
            index=year_options.index(current_year_real),
            key="stat_filter_year"
        )

    # Filter data histori & gagal berdasarkan kategori
    if stat_category == "Semua Hasil Screener":
        hist_filtered_cat = history_list
        failed_filtered_cat = failed_list
        active_filtered_cat = active_list
    else:
        hist_filtered_cat = [h for h in history_list if h.get("category", "Saham Tidur") == stat_category]
        failed_filtered_cat = [f for f in failed_list if f.get("category", "Saham Tidur") == stat_category]
        active_filtered_cat = [s for s in active_list if s.get("category", "Saham Tidur") == stat_category]

    # 1. Kalkulasi All-Time untuk kategori terpilih
    total_awakened_cat = len(hist_filtered_cat)
    total_failed_cat = len(failed_filtered_cat)
    total_closed_cat = total_awakened_cat + total_failed_cat

    win_trades_cat = [h for h in hist_filtered_cat if h.get("gain_pct", 0) >= 0]
    loss_trades_cat = [h for h in hist_filtered_cat if h.get("gain_pct", 0) < 0] + failed_filtered_cat
    win_count_cat = len(win_trades_cat)
    loss_count_cat = len(loss_trades_cat)
    winrate_all_cat = (win_count_cat / total_closed_cat * 100) if total_closed_cat > 0 else 0.0

    total_gain_cat = sum(h.get("gain_pct", 0) for h in hist_filtered_cat) + sum(f.get("loss_pct", 0) for f in failed_filtered_cat)
    avg_gain_all_cat = (total_gain_cat / total_closed_cat) if total_closed_cat > 0 else 0.0

    # Posisi aktif dalam kategori
    act_total_cat = len(active_filtered_cat)
    act_profit_cat = sum(1 for s in active_filtered_cat if s.get("current_price", 0) > s.get("entry_price", 0))
    act_loss_cat = sum(1 for s in active_filtered_cat if s.get("current_price", 0) < s.get("entry_price", 0))
    act_bep_cat = act_total_cat - act_profit_cat - act_loss_cat

    # 2. Kalkulasi Khusus Bulan & Tahun Terpilih
    selected_ym = f"{stat_year:04d}-{stat_month:02d}"
    month_history_cat = [h for h in hist_filtered_cat if str(h.get("awakened_date", "")).startswith(selected_ym)]
    month_failed_cat = [f for f in failed_filtered_cat if str(f.get("exit_date", "")).startswith(selected_ym)]
    month_closed_cat = len(month_history_cat) + len(month_failed_cat)
    month_win_cat = sum(1 for h in month_history_cat if h.get("gain_pct", 0) >= 0)
    month_loss_cat = month_closed_cat - month_win_cat
    winrate_month_cat = (month_win_cat / month_closed_cat * 100) if month_closed_cat > 0 else 0.0
    month_gain_cat = sum(h.get("gain_pct", 0) for h in month_history_cat) + sum(f.get("loss_pct", 0) for f in month_failed_cat)
    avg_gain_month_cat = (month_gain_cat / month_closed_cat) if month_closed_cat > 0 else 0.0

    month_new_entries_cat = sum(1 for s in active_filtered_cat if str(s.get("entry_date", "")).startswith(selected_ym))

    st.markdown("---")
    # Tampilan Kartu All-Time
    st.markdown(f"###### 🌐 Performa All-Time — Kategori: **{stat_category}** (Sepanjang Masa)")
    m_all1, m_all2, m_all3, m_all4 = st.columns(4)
    m_all1.metric(
        "Win Rate All-Time 🎯",
        f"{winrate_all_cat:.1f}%",
        f"{win_count_cat} Win / {loss_count_cat} Loss"
    )
    m_all2.metric(
        "Total Selesai 🏁",
        f"{total_closed_cat} Emiten",
        f"🏆 {total_awakened_cat} Cuan | 🛑 {total_failed_cat} SL"
    )
    m_all3.metric(
        "Rata-rata Cuan/Trade 📈",
        f"{avg_gain_all_cat:+.2f}%",
        f"Total: {total_gain_cat:+.1f}%"
    )
    m_all4.metric(
        "Posisi Aktif Berjalan 💤",
        f"{act_total_cat} Emiten",
        f"🟢 {act_profit_cat} Profit | 🔴 {act_loss_cat} Loss"
    )

    st.markdown("---")
    month_lbl = f"{MONTH_NAMES[stat_month]} {stat_year}"
    st.markdown(f"###### 📅 Performa Periode Khusus — Kategori: **{stat_category}** ({month_lbl})")
    m_m1, m_m2, m_m3, m_m4 = st.columns(4)
    m_m1.metric(
        f"Win Rate {month_lbl} 🎯",
        f"{winrate_month_cat:.1f}%" if month_closed_cat > 0 else "0.0%",
        f"{month_win_cat} Win / {month_loss_cat} Loss" if month_closed_cat > 0 else "Belum ada exit"
    )
    m_m2.metric(
        f"Trade Selesai ({month_lbl}) 🏁",
        f"{month_closed_cat} Emiten",
        f"{month_win_cat} Cuan / {month_loss_cat} SL"
    )
    m_m3.metric(
        f"Rata-rata Cuan ({month_lbl}) 📈",
        f"{avg_gain_month_cat:+.2f}%" if month_closed_cat > 0 else "0.00%",
        f"Periode {month_lbl}"
    )
    m_m4.metric(
        f"Saham Baru Masuk ({month_lbl}) 📥",
        f"{month_new_entries_cat} Emiten",
        f"Kategori {stat_category}"
    )

st.markdown("---")

# ==========================================
# 2. FUNGSI RENDER TABEL HASIL SCREENER
# ==========================================
def render_screener_table(category_label, category_badge, tab_key, active_list, is_editor, data):
    stocks_cat = [s for s in active_list if s.get("category", "Saham Tidur") == category_label]

    # Header Tab Info & Refresh
    t_col1, t_col2 = st.columns([3.5, 1.5])
    with t_col1:
        st.markdown(f"##### {category_badge} Hasil Screener: **{category_label}** ({len(stocks_cat)} Emiten Dipantau)")
    with t_col2:
        if st.button(f"🔄 Refresh Harga ({tab_key})", key=f"btn_refresh_{tab_key}", use_container_width=True):
            with st.spinner("Mengambil harga bursa..."):
                updated_count = 0
                for s in data["active_stocks"]:
                    if s.get("category", "Saham Tidur") == category_label:
                        price = fetch_latest_price(s["ticker"])
                        if price:
                            s["current_price"] = price
                            updated_count += 1
                save_data(data)
                st.toast(f"Berhasil refresh {updated_count} harga saham {category_label}!", icon="✅")
                st.rerun()

    # Filter Bar
    f_pl, f_sya, f_date, f_search = st.columns([1.8, 1.5, 1.8, 1.5])
    with f_pl:
        filter_pl = st.selectbox(
            "📊 Filter Status P/L:",
            ["Semua Status P/L", "🟢 Hanya Profit", "🔴 Hanya Loss"],
            key=f"filter_pl_{tab_key}"
        )
    with f_sya:
        filter_syariah = st.selectbox(
            "🕌 Filter Syariah:",
            ["Semua Saham", "Hanya Syariah (ISSI)", "Hanya Non-Syariah"],
            key=f"filter_syariah_{tab_key}"
        )
    with f_date:
        filter_date = st.date_input(
            "📅 Filter Tgl Masuk:",
            value=(),
            key=f"filter_date_{tab_key}",
            help="Pilih 1 tanggal atau 2 tanggal untuk rentang periode masuk."
        )
    with f_search:
        search_query = st.text_input(
            "🔍 Cari Kode:",
            placeholder="misal: ROTI",
            key=f"filter_search_{tab_key}"
        )

    # Filter logic
    filtered = []
    for s in stocks_cat:
        entry = s.get("entry_price", 0)
        curr = s.get("current_price", 0)

        # Filter P/L
        if filter_pl == "🟢 Hanya Profit" and curr <= entry:
            continue
        if filter_pl == "🔴 Hanya Loss" and curr >= entry:
            continue

        # Filter Syariah
        if filter_syariah == "Hanya Syariah (ISSI)" and not s.get("is_syariah", False):
            continue
        if filter_syariah == "Hanya Non-Syariah" and s.get("is_syariah", False):
            continue

        # Filter Tanggal
        if not is_date_in_filter(s.get("entry_date"), filter_date):
            continue

        # Filter Search
        if search_query:
            q = search_query.upper().strip()
            if q not in s.get("ticker", "").upper():
                continue

        filtered.append(s)

    # Urutkan tanggal masuk terbaru
    filtered.sort(key=lambda x: str(x.get("entry_date", "")), reverse=True)

    # DataFrame rows
    display_rows = []
    for s in filtered:
        entry = s.get("entry_price", 0)
        curr = s.get("current_price", 0)
        gain_pct = ((curr - entry) / entry * 100) if entry > 0 else 0.0

        sl_val = s.get("sl") or 0
        tp1_val = s.get("tp1") or 0
        tp2_val = s.get("tp2") or 0
        tp3_val = s.get("tp3") or 0

        sl_str = f"Rp {sl_val} ({((sl_val - entry) / entry * 100):.0f}%)" if sl_val > 0 else "-"
        tp1_str = f"Rp {tp1_val} (+{((tp1_val - entry) / entry * 100):.0f}%)" if tp1_val > 0 else "-"
        tp2_str = f"Rp {tp2_val} (+{((tp2_val - entry) / entry * 100):.0f}%)" if tp2_val > 0 else "-"
        tp3_str = f"Rp {tp3_val} (+{((tp3_val - entry) / entry * 100):.0f}%)" if tp3_val > 0 else "-"
        hold_work_days = calculate_working_days(s.get("entry_date"))

        # Status P/L
        if gain_pct > 0:
            status_pl = f"🟢 Profit (+{gain_pct:.1f}%)"
        elif gain_pct < 0:
            status_pl = f"🔴 Loss ({gain_pct:.1f}%)"
        else:
            status_pl = "⚪ BEP (0.0%)"

        # Status Alert
        if sl_val > 0 and curr <= sl_val:
            status_alert = "KENA SL 🛑"
        elif sl_val > 0 and curr <= (sl_val * 1.03):
            status_alert = "DEKAT SL 🚨"
        elif tp3_val > 0 and curr >= tp3_val:
            status_alert = "TP 3 TERCAPAI 🏆"
        elif tp2_val > 0 and curr >= tp2_val:
            status_alert = "TP 2 TEMBUS 🎯"
        elif tp1_val > 0 and curr >= tp1_val:
            status_alert = "TP 1 TERCAPAI 🎯"
        elif tp1_val > 0 and curr > entry:
            diff_tp1 = tp1_val - curr
            status_alert = f"DEKAT TP 1 (-{diff_tp1}) ⚡"
        elif curr > entry:
            status_alert = "PROFIT 📈"
        elif curr < entry:
            status_alert = "LOSS 🔻"
        else:
            status_alert = "MASIH TIDUR 💤"

        display_rows.append({
            "Kode": s["ticker"],
            "Syariah": "✅" if s.get("is_syariah") else "-",
            "Tgl Masuk": s.get("entry_date", "-"),
            "Hold": hold_work_days,
            "Harga Masuk": entry,
            "Harga Sekarang": curr,
            "Floating Gain (%)": round(gain_pct, 2),
            "Status P/L": status_pl,
            "SL": sl_str,
            "TP 1": tp1_str,
            "TP 2": tp2_str,
            "TP 3": tp3_str,
            "Kondisi": status_alert
        })

    df_tab = pd.DataFrame(display_rows)
    if not df_tab.empty:
        st.dataframe(
            df_tab,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Kode": st.column_config.TextColumn("Kode", width="small"),
                "Syariah": st.column_config.TextColumn("Syariah", width="small", help="✅ = Syariah (ISSI), - = Non-Syariah"),
                "Tgl Masuk": st.column_config.TextColumn("Tgl Masuk", width="small"),
                "Hold": st.column_config.NumberColumn("Hold", format="%d hari", width="small", help="Lama simpan hari kerja bursa (Senin-Jumat)"),
                "Harga Masuk": st.column_config.NumberColumn("Modal", format="Rp %d", width="small"),
                "Harga Sekarang": st.column_config.NumberColumn("Harga", format="Rp %d", width="small"),
                "Floating Gain (%)": st.column_config.NumberColumn("Floating Gain", format="%+.2f%%", width="small"),
                "Status P/L": st.column_config.TextColumn("Status P/L", width="medium", help="Status pergerakan harga terhadap modal"),
                "SL": st.column_config.TextColumn("SL", width="small", help="Level Stop Loss (Batas Risiko)"),
                "TP 1": st.column_config.TextColumn("TP 1", width="small", help="Target Take Profit 1"),
                "TP 2": st.column_config.TextColumn("TP 2", width="small", help="Target Take Profit 2"),
                "TP 3": st.column_config.TextColumn("TP 3", width="small", help="Target Take Profit 3"),
                "Kondisi": st.column_config.TextColumn("Kondisi", width="medium", help="Status teknikal & level target"),
            }
        )

        df_export = df_tab.copy()
        df_export["Hold"] = df_export["Hold"].apply(lambda x: f"{x} Hari Kerja")
        csv_tab = df_export.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=f"📥 Export Tabel {category_label} ke .CSV",
            data=csv_tab,
            file_name=f"screener_{tab_key}_{datetime.date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key=f"btn_export_csv_{tab_key}"
        )
    else:
        st.info(f"Belum ada saham di kategori **{category_label}** yang sesuai dengan filter.")
        if is_editor:
            st.caption(f"💡 *Mode Editor*: Gunakan tab Quick Import / Tambah Satuan / Kelola Watchlist di Panel Editor untuk mengisi saham ke kategori **{category_label}**.")

# ==========================================
# 3. TIGA TAB HASIL SCREENER (FLOW, GOLDEN, TIDUR)
# ==========================================
st.markdown("### 🎯 Hasil Screener Saham")
st.caption("Pilih tab di bawah untuk memantau saham aktif berdasarkan kategori screener:")

tab_flow, tab_golden, tab_sleep = st.tabs([
    "🌊 Flow Masuk",
    "💎 Flow Masuk + Fundamental OK",
    "💤 Saham Tidur"
])

with tab_flow:
    render_screener_table("Flow Masuk", "🌊", "flow_masuk", active_list, is_editor, data)

with tab_golden:
    render_screener_table("Flow Masuk + Fundamental OK", "💎", "flow_fundamental", active_list, is_editor, data)

with tab_sleep:
    render_screener_table("Saham Tidur", "💤", "saham_tidur", active_list, is_editor, data)

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
    tab_quick_import, tab_bungkus, tab_sl, tab_add, tab_manage_active, tab_manage_cuan, tab_manage_gagal = st.tabs([
        "⚡ Quick Import Stockbit",
        "💰 Bungkus Cuan (Take Profit)",
        "🛑 Realisasi SL (Gagal Bangun)",
        "➕ Tambah Satuan",
        "⚙️ Kelola Watchlist (Centang Hapus / Edit)",
        "🏆 Kelola Histori Bangun (Centang Hapus / Edit)",
        "🛑 Kelola Gagal Bangun (Centang Hapus / Edit)"
    ])

    # ----------------------------------------------------
    # TAB 1: QUICK IMPORT STOCKBIT (DUAL SCREENER: SYARIAH & NON-SYARIAH)
    # ----------------------------------------------------
    with tab_quick_import:
        st.markdown("##### ⚡ Quick Import Hasil Screener Stockbit")
        st.markdown("""
        Salin langsung seluruh teks hasil tabel screener dari Stockbit ke kotak di bawah.
        Kedua kolom bersifat **fleksibel / opsional**: Anda dapat mengisi **salah satu saja** atau **kedua-duanya sekaligus**.
        Setelah tombol proses diklik, **kotak isian otomatis kembali kosong (blank)** agar siap untuk screening berikutnya.
        """)

        st.info("🛡️ **Proteksi Anti-Duplikasi Aktif**: Saham yang sudah tercatat di watchlist tidak akan terduplikasi. Tanggal masuk pertama dan harga modal awal akan **tetap dikunci (dipertahankan)**.")

        with st.form("form_quick_import_stockbit", clear_on_submit=True):
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

            qc1, qc2, qc3 = st.columns([1.5, 1.2, 1.8])
            with qc1:
                target_cat_opt = st.selectbox(
                    "🎯 Target Kategori Screener:",
                    ["🌊 Flow Masuk", "💎 Flow Masuk + Fundamental OK", "💤 Saham Tidur"],
                    index=2,
                    key="batch_cat_select",
                    help="Pilih tab / kategori hasil screener tempat saham-saham ini dimasukkan."
                )
            with qc2:
                batch_entry_date = st.date_input("Tanggal Masuk untuk Saham Baru:", datetime.date.today(), key="batch_date_in")
            with qc3:
                right_only_mode = st.radio(
                    "Perlakuan Kolom Kanan (karena Kolom Kiri kosong):",
                    ["🏢 Tandai Seluruhnya sebagai Non-Syariah", "🕌 Tandai Seluruhnya sebagai Syariah"],
                    index=0,
                    key="right_only_syariah_mode",
                    horizontal=True
                )
                st.caption("💡 **Auto-Deteksi**: Jika kedua kolom diisi, emiten yang hanya ada di Kolom Kanan otomatis diklasifikasikan sebagai **🏢 Non-Syariah**.")

            btn_submit_batch = st.form_submit_button("🚀 Proses & Impor Saham ke Watchlist", type="primary", use_container_width=True)

        if btn_submit_batch:
            text_syariah = screener_syariah.strip()
            text_non = screener_non_syariah.strip()
            target_cat_clean = target_cat_opt.replace("🌊 ", "").replace("💎 ", "").replace("💤 ", "").strip()

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
                                    "category": target_cat_clean,
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
                                    "Kategori": target_cat_clean,
                                    "Harga Masuk": f"Rp {price}",
                                    "Tgl Masuk": str(batch_entry_date),
                                    "Status Syariah": "🕌 Syariah (ISSI)" if is_syariah else "🏢 Non-Syariah",
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
            b_col1, b_col2 = st.columns([1.5, 1.5])
            with b_col1:
                sel_ticker = st.selectbox("Pilih Saham yang Mau Dibungkus:", tickers_active)
                selected_stock = next(s for s in active_list if s["ticker"] == sel_ticker)
            with b_col2:
                exit_price = st.number_input("Harga Jual / Realisasi (Rp):", min_value=1, value=int(selected_stock["current_price"]))

            b_col3, b_col4 = st.columns([1.5, 2])
            with b_col3:
                exit_reason_preset = st.selectbox("Pilihan Alasan Cepat:", [
                    "Ketik Manual Sendiri ✍️",
                    "Target TP resmi tercapai",
                    "Dekat TP 1 tapi antrean berat, amankan cuan",
                    "Amankan modal (Bungkus dulu)",
                    "Volume mulai sepi kembali",
                    "Pindah ke emiten lain"
                ], key="sel_exit_reason_preset")
            with b_col4:
                custom_exit_note = st.text_input(
                    "Catatan Manual (Ketik Sendiri):",
                    placeholder="Contoh: ARA hari kedua, amankan cuan dulu",
                    key="input_custom_exit_note",
                    help="Ketik catatan sendiri di sini. Jika dikosongkan, akan menggunakan alasan pilihan di sebelah kiri."
                )

            # Tentukan catatan akhir
            if custom_exit_note.strip():
                final_exit_note = custom_exit_note.strip()
            elif exit_reason_preset != "Ketik Manual Sendiri ✍️":
                final_exit_note = exit_reason_preset
            else:
                final_exit_note = "Bungkus cuan manual"

            entry_p = selected_stock["entry_price"]
            realized_gain = ((exit_price - entry_p) / entry_p * 100) if entry_p > 0 else 0.0
            st.info(f"💡 Estimasi Realisasi: **{realized_gain:+.2f}%** (Modal Rp {entry_p} ➔ Jual Rp {exit_price})")

            if st.button("🎉 Konfirmasi Bungkus Cuan ➔ Pindah ke Histori", type="primary"):
                work_days = calculate_working_days(selected_stock["entry_date"])
                tp1_target = selected_stock.get("tp1") or 0
                new_hist = {
                    "ticker": selected_stock["ticker"],
                    "category": selected_stock.get("category", "Saham Tidur"),
                    "is_syariah": selected_stock["is_syariah"],
                    "entry_date": selected_stock["entry_date"],
                    "awakened_date": str(datetime.date.today()),
                    "hold_days": work_days,
                    "entry_price": entry_p,
                    "exit_price": exit_price,
                    "gain_pct": round(realized_gain, 2),
                    "status_exit": "TARGET TP TERCAPAI 🎯" if (tp1_target > 0 and exit_price >= tp1_target) else "BUNGKUS MANUAL 💰",
                    "note": final_exit_note
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

            sl_col1, sl_col2 = st.columns([1.5, 1.5])
            with sl_col1:
                default_idx = tickers_active.index(sl_breached[0]) if sl_breached else 0
                sel_sl_ticker = st.selectbox("Pilih Saham yang Mau Di-Cut Loss:", tickers_active, index=default_idx, key="sel_sl_ticker")
                sel_sl_stock = next(s for s in active_list if s["ticker"] == sel_sl_ticker)
            with sl_col2:
                default_cut_price = int(sel_sl_stock["current_price"])
                exit_sl_price = st.number_input("Harga Jual / Realisasi Cut Loss (Rp):", min_value=1, value=default_cut_price, key="input_exit_sl_price")

            sl_col3, sl_col4 = st.columns([1.5, 2])
            with sl_col3:
                exit_sl_preset = st.selectbox("Pilihan Alasan Cepat:", [
                    "Ketik Manual Sendiri ✍️",
                    "Terkena Level Stop Loss (Disiplin SL)",
                    "Menembus Support Kunci (Breakdown)",
                    "Volume Pembalikan Negatif",
                    "Sentimen Pasar / Fundamental Memburuk",
                    "Cut Loss Manual (Pindah Modal ke Emiten Lain)"
                ], key="sel_exit_sl_preset")
            with sl_col4:
                custom_sl_note = st.text_input(
                    "Catatan Manual Cut Loss (Ketik Sendiri):",
                    placeholder="Contoh: Breakdown support MA20 dengan volume besar",
                    key="input_custom_sl_note",
                    help="Ketik catatan sendiri di sini. Jika dikosongkan, akan menggunakan alasan pilihan di sebelah kiri."
                )

            # Tentukan catatan akhir cut loss
            if custom_sl_note.strip():
                final_sl_note = custom_sl_note.strip()
            elif exit_sl_preset != "Ketik Manual Sendiri ✍️":
                final_sl_note = exit_sl_preset
            else:
                final_sl_note = "Kena SL / Cut Loss manual"

            entry_p = sel_sl_stock["entry_price"]
            realized_loss = ((exit_sl_price - entry_p) / entry_p * 100) if entry_p > 0 else 0.0
            sl_preset = sel_sl_stock.get("sl") or 0
            
            st.error(f"🛑 Estimasi Realisasi Kerugian: **{realized_loss:.2f}%** (Modal Rp {entry_p} ➔ Jual Rp {exit_sl_price} | Level SL: Rp {sl_preset if sl_preset > 0 else '-'})")

            if st.button("🛑 Konfirmasi Cut Loss ➔ Pindahkan ke Tabel Gagal Bangun", type="primary", key="btn_confirm_cut_loss"):
                work_days = calculate_working_days(sel_sl_stock["entry_date"])
                new_failed = {
                    "ticker": sel_sl_stock["ticker"],
                    "category": sel_sl_stock.get("category", "Saham Tidur"),
                    "is_syariah": sel_sl_stock["is_syariah"],
                    "entry_date": sel_sl_stock["entry_date"],
                    "exit_date": str(datetime.date.today()),
                    "hold_days": work_days,
                    "entry_price": entry_p,
                    "exit_price": exit_sl_price,
                    "loss_pct": round(realized_loss, 2),
                    "sl": sl_preset,
                    "status_exit": "KENA SL 🛑" if (sl_preset > 0 and exit_sl_price <= sl_preset) else "CUT LOSS MANUAL ✂️",
                    "note": final_sl_note
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
                new_cat_opt = st.selectbox(
                    "🎯 Kategori Screener:",
                    ["🌊 Flow Masuk", "💎 Flow Masuk + Fundamental OK", "💤 Saham Tidur"],
                    index=2,
                    key="form_add_cat_select"
                )
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
                    new_cat_clean = new_cat_opt.replace("🌊 ", "").replace("💎 ", "").replace("💤 ", "").strip()
                    new_item = {
                        "ticker": new_ticker,
                        "category": new_cat_clean,
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
                    st.success(f"Saham {new_ticker} ({new_cat_clean}) berhasil ditambahkan!")
                    st.rerun()

    # ----------------------------------------------------
    # TAB 5: KELOLA WATCHLIST (CENTANG HAPUS / EDIT TABEL)
    # ----------------------------------------------------
    with tab_manage_active:
        st.markdown("##### ⚙️ Edit & Hapus Saham Watchlist")
        st.caption("Centang kotak **Pilih Hapus** untuk menghapus saham, ubah kategori/angka langsung di tabel lalu klik **Simpan Perubahan**.")
        
        if active_list:
            manage_rows = []
            for s in active_list:
                manage_rows.append({
                    "Hapus": False,
                    "Kode": s["ticker"],
                    "Kategori": s.get("category", "Saham Tidur"),
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
                    "Kategori": st.column_config.SelectboxColumn(
                        "Kategori Screener",
                        options=["Flow Masuk", "Flow Masuk + Fundamental OK", "Saham Tidur"],
                        required=True,
                        help="Ubah kategori jika saham tidur terdeteksi flow / fundamental bagus"
                    ),
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
                            s["category"] = str(r["Kategori"])
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
    # TAB 6: KELOLA HISTORI SAHAM BANGUN (CUAN)
    # ----------------------------------------------------
    with tab_manage_cuan:
        st.markdown("##### 🏆 Kelola Histori Saham Bangun (Cuan)")
        st.caption("Edit data (Kategori, Harga Jual, Tanggal, Catatan) atau centang baris untuk menghapus histori.")
        if history_list:
            hist_rows = []
            for idx, h in enumerate(history_list):
                hist_rows.append({
                    "Hapus": False,
                    "_id": idx,
                    "Kode": h["ticker"],
                    "Kategori": h.get("category", "Saham Tidur"),
                    "Tgl Masuk": h["entry_date"],
                    "Tgl Bangun": h["awakened_date"],
                    "Harga Masuk": int(h["entry_price"]),
                    "Harga Jual": int(h["exit_price"]),
                    "Catatan": h.get("note", "")
                })
            df_manage_hist = pd.DataFrame(hist_rows)

            edited_hist_df = st.data_editor(
                df_manage_hist,
                column_config={
                    "Hapus": st.column_config.CheckboxColumn("Pilih Hapus 🗑️", help="Centang baris yang ingin dihapus", default=False),
                    "_id": None,  # disembunyikan
                    "Kode": st.column_config.TextColumn("Kode Saham", disabled=True),
                    "Kategori": st.column_config.SelectboxColumn(
                        "Kategori Screener",
                        options=["Flow Masuk", "Flow Masuk + Fundamental OK", "Saham Tidur"],
                        required=True
                    ),
                    "Tgl Masuk": st.column_config.TextColumn("Tgl Masuk (YYYY-MM-DD)"),
                    "Tgl Bangun": st.column_config.TextColumn("Tgl Bangun (YYYY-MM-DD)"),
                    "Harga Masuk": st.column_config.NumberColumn("Harga Masuk (Rp)", min_value=1, step=1, format="%d"),
                    "Harga Jual": st.column_config.NumberColumn("Harga Jual (Rp)", min_value=1, step=1, format="%d"),
                    "Catatan": st.column_config.TextColumn("Catatan / Alasan Exit (Ketik Manual)", help="Klik langsung di kolom ini untuk mengetik/mengubah catatan manual"),
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
                        orig_status = data["awakened_history"][orig_idx].get("status_exit", "BUNGKUS MANUAL 💰") if orig_idx < len(data["awakened_history"]) else "BUNGKUS MANUAL 💰"
                        
                        new_hist_list.append({
                            "ticker": str(r["Kode"]),
                            "category": str(r.get("Kategori", "Saham Tidur")),
                            "is_syariah": orig_syariah,
                            "entry_date": tgl_masuk,
                            "awakened_date": tgl_bangun,
                            "hold_days": hold_days,
                            "entry_price": entry_p,
                            "exit_price": exit_p,
                            "gain_pct": recalculated_gain,
                            "status_exit": orig_status,
                            "note": str(r["Catatan"])
                        })
                    data["awakened_history"] = new_hist_list
                    save_data(data)
                    st.success("Perubahan data histori saham bangun berhasil disimpan!")
                    st.rerun()
        else:
            st.info("Belum ada histori saham bangun untuk diedit/dihapus.")

    # ----------------------------------------------------
    # TAB 7: KELOLA GAGAL BANGUN (CUT LOSS / KENA SL)
    # ----------------------------------------------------
    with tab_manage_gagal:
        st.markdown("##### 🛑 Kelola Saham Gagal Bangun (Terkena SL / Cut Loss)")
        st.caption("Edit data (Kategori, Harga Cut Loss, Level SL, Tanggal, Status Exit, Alasan) atau centang baris untuk menghapus histori.")
        failed_history_data = data.get("failed_history", [])
        if failed_history_data:
            gagal_rows = []
            for idx, g in enumerate(failed_history_data):
                gagal_rows.append({
                    "Hapus": False,
                    "_id": idx,
                    "Kode": g["ticker"],
                    "Kategori": g.get("category", "Saham Tidur"),
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
                    "Kategori": st.column_config.SelectboxColumn(
                        "Kategori Screener",
                        options=["Flow Masuk", "Flow Masuk + Fundamental OK", "Saham Tidur"],
                        required=True
                    ),
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
                            "category": str(r.get("Kategori", "Saham Tidur")),
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

# ==========================================
# 4. RIWAYAT TRADE SELESAI (HISTORI CUAN & CUT LOSS)
# ==========================================
st.markdown("---")
with st.expander("📜 Riwayat Trade Selesai (Histori Cuan & Cut Loss)", expanded=False):
    st.caption("Riwayat seluruh emiten yang telah selesai ditradingkan (Realisasi Profit & Cut Loss)")

    # Filter bar
    hf_col1, hf_col2, hf_col3, hf_col4, hf_col5 = st.columns([1.6, 1.5, 1.4, 1.4, 1.5])
    with hf_col1:
        filter_closed_status = st.selectbox(
            "📊 Status Hasil:",
            ["Semua (Profit / Loss / BEP)", "🟢 Hanya Profit", "🔴 Hanya Loss", "⚪ Hanya BEP"],
            key="filter_closed_status"
        )
    with hf_col2:
        filter_closed_kat = st.selectbox(
            "🎯 Kategori Screener:",
            ["Semua Kategori"] + SCREENER_CATEGORIES,
            key="filter_closed_kat"
        )
    with hf_col3:
        filter_closed_syariah = st.selectbox(
            "🕌 Syariah:",
            ["Semua Histori", "Hanya Syariah (ISSI)", "Hanya Non-Syariah"],
            key="filter_closed_syariah"
        )
    with hf_col4:
        filter_closed_search = st.text_input(
            "🔍 Cari Kode:", placeholder="misal: MSKY", key="filter_closed_search"
        )
    with hf_col5:
        filter_closed_date = st.date_input(
            "📅 Filter Tgl Selesai:",
            value=(),
            key="filter_closed_date",
            help="Pilih 1 tanggal atau rentang tanggal selesai/exit."
        )

    # Satukan data history cuan dan failed/cut loss ke dalam 1 list
    combined_closed = []
    for h in history_list:
        gain_val = float(h.get("gain_pct", 0.0))
        if gain_val > 0:
            status_text = "Profit"
            trade_type = "PROFIT"
        elif gain_val < 0:
            status_text = "Loss"
            trade_type = "LOSS"
        else:
            status_text = "BEP"
            trade_type = "BEP"

        combined_closed.append({
            "type": trade_type,
            "ticker": h["ticker"],
            "category": h.get("category", "Saham Tidur"),
            "is_syariah": h.get("is_syariah", True),
            "entry_date": h.get("entry_date", "-"),
            "exit_date": h.get("awakened_date", "-"),
            "hold_days": int(h.get("hold_days", 0)),
            "entry_price": int(h.get("entry_price", 0)),
            "exit_price": int(h.get("exit_price", 0)),
            "return_pct": gain_val,
            "status_pl": status_text,
            "level_sl": "-",
            "note": h.get("note", "-")
        })

    for f in failed_list:
        loss_val = float(f.get("loss_pct", 0.0))
        sl_val = int(f.get("sl", 0))
        if loss_val > 0:
            status_text = "Profit"
            trade_type = "PROFIT"
        elif loss_val < 0:
            status_text = "Loss"
            trade_type = "LOSS"
        else:
            status_text = "BEP"
            trade_type = "BEP"

        combined_closed.append({
            "type": trade_type,
            "ticker": f["ticker"],
            "category": f.get("category", "Saham Tidur"),
            "is_syariah": f.get("is_syariah", True),
            "entry_date": f.get("entry_date", "-"),
            "exit_date": f.get("exit_date", "-"),
            "hold_days": int(f.get("hold_days", 0)),
            "entry_price": int(f.get("entry_price", 0)),
            "exit_price": int(f.get("exit_price", 0)),
            "return_pct": loss_val,
            "status_pl": status_text,
            "level_sl": f"Rp {sl_val}" if sl_val > 0 else "-",
            "note": f.get("note", "-")
        })

    # Filter logic
    filtered_closed = []
    for c in combined_closed:
        # Filter Profit / Loss / BEP
        if filter_closed_status == "🟢 Hanya Profit" and c["type"] != "PROFIT":
            continue
        if filter_closed_status == "🔴 Hanya Loss" and c["type"] != "LOSS":
            continue
        if filter_closed_status == "⚪ Hanya BEP" and c["type"] != "BEP":
            continue

        # Filter Kategori
        if filter_closed_kat != "Semua Kategori" and c["category"] != filter_closed_kat:
            continue

        # Filter Syariah
        if filter_closed_syariah == "Hanya Syariah (ISSI)" and not c["is_syariah"]:
            continue
        if filter_closed_syariah == "Hanya Non-Syariah" and c["is_syariah"]:
            continue

        # Filter Search
        if filter_closed_search and filter_closed_search.upper().strip() not in c["ticker"].upper():
            continue

        # Filter Date
        if not is_date_in_filter(c["exit_date"], filter_closed_date):
            continue

        filtered_closed.append(c)

    # Urutkan tanggal selesai terbaru ke terlama
    filtered_closed.sort(key=lambda x: str(x.get("exit_date", x.get("entry_date", ""))), reverse=True)

    display_closed = []
    for c in filtered_closed:
        display_closed.append({
            "Kode": c["ticker"],
            "Kategori": c["category"],
            "Syariah": "✅" if c["is_syariah"] else "-",
            "Tgl Masuk": c["entry_date"],
            "Tgl Selesai": c["exit_date"],
            "Hold": c["hold_days"],
            "Harga Masuk": c["entry_price"],
            "Harga Selesai": c["exit_price"],
            "Realisasi (%)": round(c["return_pct"], 2),
            "Level SL": c["level_sl"],
            "Status": c["status_pl"],
            "Catatan / Alasan Exit": c["note"]
        })

    df_closed = pd.DataFrame(display_closed)
    if not df_closed.empty:
        st.dataframe(
            df_closed,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Kode": st.column_config.TextColumn("Kode", width="small"),
                "Kategori": st.column_config.TextColumn("Kategori Screener", width="medium"),
                "Syariah": st.column_config.TextColumn("Syariah", width="small", help="✅ = Syariah (ISSI), - = Non-Syariah"),
                "Tgl Masuk": st.column_config.TextColumn("Tgl Masuk", width="small"),
                "Tgl Selesai": st.column_config.TextColumn("Tgl Selesai", width="small"),
                "Hold": st.column_config.NumberColumn("Hold", format="%d hari", width="small"),
                "Harga Masuk": st.column_config.NumberColumn("Modal", format="Rp %d", width="small"),
                "Harga Selesai": st.column_config.NumberColumn("Harga Selesai", format="Rp %d", width="small"),
                "Realisasi (%)": st.column_config.NumberColumn("Realisasi P/L", format="%+.2f%%", width="small"),
                "Level SL": st.column_config.TextColumn("Level SL", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small", help="Profit / Loss / BEP"),
                "Catatan / Alasan Exit": st.column_config.TextColumn("Catatan / Alasan Exit", width="large"),
            }
        )

        df_closed_export = df_closed.copy()
        df_closed_export["Hold"] = df_closed_export["Hold"].apply(lambda x: f"{x} Hari Kerja")
        csv_closed = df_closed_export.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Export Riwayat Trade Selesai ke .CSV",
            data=csv_closed,
            file_name=f"riwayat_trade_selesai_{datetime.date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="btn_download_csv_closed_all"
        )
    else:
        st.info("Tidak ada data riwayat trade selesai yang sesuai filter.")
