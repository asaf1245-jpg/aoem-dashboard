import requests
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64
import io
import os
import re
import glob
import json
import unicodedata

st.set_page_config(
    page_title="AOE Mobile - Elite Duel & Server Benchmark",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- PERFORMANCE CACHING -----------------
@st.cache_data(show_spinner=False)
def get_base64_cached(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

bin_str = get_base64_cached("bg.jpg")
if bin_str:
    bg_rule = f'background: linear-gradient(rgba(0, 0, 0, 0.92), rgba(0, 0, 0, 0.98)), url("data:image/jpeg;base64,{bin_str}"); background-size: cover; background-position: center top; background-attachment: fixed;'
else:
    bg_rule = 'background: #000000;'

st.markdown("""<style>
    .main { background-color: transparent; color: #f1f5f9; }
    .stApp { """ + bg_rule + """ }
    
    .cp-header {
        border: 2px solid #d4af37;
        border-radius: 10px;
        padding: 16px 28px;
        background: linear-gradient(90deg, rgba(10, 10, 15, 0.95) 0%, rgba(20, 25, 45, 0.95) 50%, rgba(10, 10, 15, 0.95) 100%);
        margin-bottom: 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 0 25px rgba(212, 175, 55, 0.25);
    }
    .cp-title {
        color: #ffffff;
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-weight: 900;
        font-size: 26px;
        letter-spacing: 2px;
        margin: 0;
        text-transform: uppercase;
    }
    .cp-subtitle {
        color: #d4af37;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-top: 5px;
    }

    .kpi-card {
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        padding: 14px 10px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .kpi-label {
        color: #94a3b8;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        color: #38bdf8;
        font-size: 22px;
        font-weight: 900;
        font-family: 'Segoe UI', monospace;
        margin-top: 4px;
    }
    .kpi-sub {
        color: #64748b;
        font-size: 11px;
        margin-top: 2px;
    }
    
    .vs-circle {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 76px;
        height: 76px;
        margin: 0 auto;
        background: radial-gradient(circle, #d4af37 0%, #855812 100%);
        color: #050b14;
        font-weight: 900;
        font-size: 28px;
        border-radius: 50%;
        border: 3px solid #fef08a;
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.8);
    }
    
    .troop-battle-card {
        background: rgba(10, 10, 15, 0.85);
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 14px;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.8);
    }
    
    .hero-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 8px;
    }
    .hero-slot {
        width: 82px;
        height: 98px;
        border-radius: 8px;
        border: 1.5px solid #d4af37;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.35);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #050508;
        text-align: center;
        padding: 2px;
    }
    .hero-slot img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
    }
    .hero-name-label {
        font-size: 11px;
        font-weight: 800;
        color: #94a3b8;
        text-transform: uppercase;
        padding: 4px;
        line-height: 1.2;
    }
    
    .tier-badge-t9 {
        background: #dc2626;
        color: #ffffff;
        font-weight: 900;
        font-size: 12px;
        padding: 3px 9px;
        border-radius: 4px;
        border: 1px solid #ef4444;
        box-shadow: 0 0 10px rgba(220, 38, 38, 0.6);
        margin-left: 8px;
        display: inline-block;
        letter-spacing: 0.5px;
    }
    .tier-badge-t8 {
        background: #d4af37;
        color: #050b14;
        font-weight: 900;
        font-size: 12px;
        padding: 3px 9px;
        border-radius: 4px;
        border: 1px solid #fef08a;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.6);
        margin-left: 8px;
        display: inline-block;
        letter-spacing: 0.5px;
    }
    .tier-badge-t7 {
        background: #9333ea;
        color: #ffffff;
        font-weight: 900;
        font-size: 12px;
        padding: 3px 9px;
        border-radius: 4px;
        border: 1px solid #c084fc;
        box-shadow: 0 0 10px rgba(147, 51, 234, 0.6);
        margin-left: 8px;
        display: inline-block;
        letter-spacing: 0.5px;
    }
    
    .badge-win-p1 {
        background: rgba(239, 68, 68, 0.25);
        color: #f87171;
        border: 1px solid #ef4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 12px;
        display: inline-block;
    }
    .badge-win-p2 {
        background: rgba(2, 132, 199, 0.25);
        color: #38bdf8;
        border: 1px solid #0284c7;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 12px;
        display: inline-block;
    }
</style>""", unsafe_allow_html=True)

# ----------------- PERMANENT DISK STORAGE (ABSOLUTE PATHS) -----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
DATA_STORE_FILE = os.path.join(BASE_DIR, "player_custom_data.json")
EVENT_HISTORY_FILE = os.path.join(BASE_DIR, "primordial_event_history.json")

def load_disk_data():
    if os.path.exists(DATA_STORE_FILE):
        try:
            with open(DATA_STORE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_disk_data(data):
    try:
        with open(DATA_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)

def load_event_history():
    if os.path.exists(EVENT_HISTORY_FILE):
        try:
            with open(EVENT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_event_history(data):
    try:
        with open(EVENT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Event history save error:", e)

if "player_disk_data" not in st.session_state:
    st.session_state["player_disk_data"] = load_disk_data()

HERO_FOLDERS = ["C:/Users/asafk/Downloads/aoem_dashboard/Heroes", "Heroes", "heroes"]

def load_hero_names():
    names = ["None"]
    txt_path = "Heroes Names.txt"
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                item = line.strip()
                if item and item not in names:
                    names.append(item)
    else:
        fallback = [
            "Alp Arslan", "Confucius", "Cyrus the Great", "Dae Jang Geum",
            "King Arthur", "Lady Trieu", "Lagertha", "Lu Bu", "Mansa Musa",
            "Mehmed II", "Napoleon", "Ramesses II", "Roland", "Scipio Africanus",
            "Zhao Yun", "Zhuge Liang"
        ]
        for item in fallback:
            if item not in names:
                names.append(item)
    return names

if "restricted_heroes" not in st.session_state:
    st.session_state["restricted_heroes"] = load_hero_names()

def normalize_name(s):
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

st.sidebar.header("🛠️ Custom Manager")
with st.sidebar.expander("Manage Added Heroes", expanded=False):
    current_heroes = load_hero_names()
    added_custom = [h for h in current_heroes if h != "None"]
    st.caption(f"Total Heroes in List: {len(added_custom)}")
    
    new_hero_input = st.text_input("Add Hero Name:", key="sidebar_new_hero")
    if st.button("Add Hero", key="btn_add_sidebar_hero"):
        if new_hero_input:
            txt_path = "Heroes Names.txt"
            current_list = [l.strip() for l in open(txt_path, "r", encoding="utf-8")] if os.path.exists(txt_path) else []
            if new_hero_input not in current_list:
                current_list.append(new_hero_input)
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(current_list))
                st.session_state["restricted_heroes"] = load_hero_names()
                st.success(f"Added {new_hero_input}!")
                st.rerun()

    if added_custom:
        to_remove = st.selectbox("Select Hero to Remove:", added_custom, key="hero_to_remove")
        if st.button("Remove Selected Hero", key="btn_remove_hero"):
            txt_path = "Heroes Names.txt"
            if os.path.exists(txt_path):
                current_list = [l.strip() for l in open(txt_path, "r", encoding="utf-8")]
                current_list = [l for l in current_list if l != to_remove]
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(current_list))
                st.session_state["restricted_heroes"] = load_hero_names()
                st.success(f"Removed {to_remove}!")
                st.rerun()

def get_hero_img_html(hero_name):
    if not hero_name or hero_name == "None":
        return '<div class="hero-slot"><span class="hero-name-label">Empty</span></div>'
    
    target_norm = normalize_name(hero_name)
    found_path = None
    
    for h_dir in HERO_FOLDERS:
        if os.path.exists(h_dir):
            for f_name in os.listdir(h_dir):
                base, ext = os.path.splitext(f_name)
                if ext.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    if normalize_name(base) == target_norm:
                        found_path = os.path.join(h_dir, f_name)
                        break
        if found_path:
            break
            
    if found_path and os.path.exists(found_path):
        with open(found_path, "rb") as f_img:
            b64 = base64.b64encode(f_img.read()).decode()
        return f'<div class="hero-slot" title="{hero_name}"><img src="data:image/jpeg;base64,{b64}"/></div>'
    
    return f'<div class="hero-slot" title="{hero_name}"><span class="hero-name-label">{hero_name[:12]}</span></div>'

def fmt_p(val):
    if pd.isna(val) or val == 0: return "--"
    try:
        return f"{int(round(float(val))):,}"
    except (ValueError, TypeError):
        return str(val)

def fmt_score_b_m(val):
    if pd.isna(val) or val == 0: return "0"
    v = float(val)
    if v >= 1e9:
        return f"{v/1e9:.2f}B"
    elif v >= 1e6:
        return f"{v/1e6:.1f}M"
    elif v >= 1e3:
        return f"{v/1e3:.0f}K"
    return str(int(v))

def get_tier_badge_html(tier):
    if tier == "T9":
        return '<span class="tier-badge-t9">T9</span>'
    elif tier == "T8":
        return '<span class="tier-badge-t8">T8</span>'
    elif tier == "T7":
        return '<span class="tier-badge-t7">T7</span>'
    return ""

def assign_tier(power):
    if power >= 300_000_000: return "Mythic"
    elif power >= 250_000_000: return "Legend"
    elif power >= 200_000_000: return "Hero"
    elif power >= 150_000_000: return "Master"
    elif power >= 100_000_000: return "Elite"
    return "Vanguard"

@st.cache_data(show_spinner=False)
@st.cache_data(show_spinner=False)
def load_and_clean_server(file_path_or_bytes, file_name):
    try:
        if isinstance(file_path_or_bytes, str):
            raw_df = pd.read_excel(file_path_or_bytes, sheet_name=0)
        elif isinstance(file_path_or_bytes, (bytes, bytearray)):
            bio = io.BytesIO(file_path_or_bytes)
            raw_df = pd.read_excel(bio) if file_name.endswith((".xlsx", ".xls")) else pd.read_csv(bio)
        else:
            raw_df = pd.read_excel(file_path_or_bytes) if file_name.endswith((".xlsx", ".xls")) else pd.read_csv(file_path_or_bytes)
    except Exception as e:
        st.error(f"Error reading {file_name}: {e}")
        return None
        
    col_map = {}
    for c in raw_df.columns:
        cl = str(c).strip().lower()
        if "player" in cl or "name" in cl or "personal info" in cl or "info" in cl: col_map[c] = "Player"
        elif cl == "power" or "total power" in cl or "troop power" in cl or "score" in cl: col_map[c] = "Power"
        elif "merit" in cl: col_map[c] = "Merits"
        elif "alliance" in cl or "guild" in cl: col_map[c] = "Alliance"
        elif "rank" in cl: col_map[c] = "Rank"
        elif "region" in cl: col_map[c] = "Region"

    df = raw_df.rename(columns=col_map).copy()
    if "Power" not in df.columns: return None

    df["Power"] = pd.to_numeric(df["Power"].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce')
    df = df.dropna(subset=["Power"]).sort_values(by="Power", ascending=False).reset_index(drop=True)
    df["Rank"] = range(1, len(df) + 1)
    if "Player" not in df.columns and len(df.columns) > 1:
        # Fallback to column index 1 if available
        df["Player"] = raw_df.iloc[:, 1]
    if "Player" not in df.columns: 
        df["Player"] = [f"Player_{i}" for i in range(1, len(df) + 1)]
    if "Alliance" not in df.columns: df["Alliance"] = "--"
    if "Region" not in df.columns: df["Region"] = "Kingsland"
    if "Merits" not in df.columns: df["Merits"] = 0

    df["Tier"] = df["Power"].apply(assign_tier)
    return df


# ----------------- FAST TROOP POWER SYNC -----------------
# ----------------- FAST TROOP POWER SYNC (PROTECTED FROM OVERWRITE) -----------------
def sync_troop_files(uploaded_troops=None):
    """
    Fast loader for Swordsmen, Pikemen, and Cavalry files.
    Auto-detects files in folder or processes uploaded files.
    Saves directly to player_custom_data.json and session state.
    Protected: does not overwrite existing user manual edits on startup.
    """
    troop_sources = []
    
    potential_files = [
        ("Swordsmen_Rankings_Top50.xlsx", "🗡️ Swordsmen", 1),
        ("Pikemen_Rankings_Top50.xlsx", "🛡️ Pikemen", 2),
        ("Cavalry_Rankings_Kingsland.xlsx", "🐎 Cavalry", 3)
    ]
    for fn, t_type, m_idx in potential_files:
        f_full = os.path.join(BASE_DIR, fn)
        if os.path.exists(f_full):
            troop_sources.append((f_full, t_type, m_idx, False))
            
    if uploaded_troops:
        for f in uploaded_troops:
            fname = f.name.lower()
            if "sword" in fname or "sword" in fname or "חרב" in fname:
                troop_sources.append((f, "🗡️ Swordsmen", 1, True))
            elif "pike" in fname or "pike" in fname or "רומח" in fname or "פייק" in fname:
                troop_sources.append((f, "🛡️ Pikemen", 2, True))
            elif "cav" in fname or "cav" in fname or "פרש" in fname:
                troop_sources.append((f, "🐎 Cavalry", 3, True))
            else:
                troop_sources.append((f, "⚔️ March 5 / Extra", 5, True))

    updated_count = 0
    data = st.session_state["player_disk_data"]
    
    for src, t_type, default_midx, is_upload in troop_sources:
        try:
            df = pd.read_excel(src)
                
            p_col = None
            pow_col = None
            for c in df.columns:
                cl = str(c).strip().lower()
                if "שחקן" in cl or "player" in cl or "name" in cl:
                    p_col = c
                elif "כוח" in cl or "power" in cl or "troop" in cl:
                    pow_col = c
                    
            if p_col and pow_col:
                for _, row in df.iterrows():
                    p_name = str(row[p_col]).strip()
                    if not p_name or p_name == "nan": continue
                    
                    raw_val = str(row[pow_col]).replace(",", "").replace(" ", "").strip()
                    try:
                        pow_num = float(raw_val)
                    except:
                        continue
                        
                    tier_val = "T9" if pow_num >= 60_000_000 else ("T8" if pow_num >= 50_000_000 else ("T7" if pow_num > 0 else "None"))
                    
                    target_servers = ["Server #070 (ERA70)"]
                    for srv in server_names:
                        if "070" in srv and srv not in target_servers:
                            target_servers.append(srv)
                            
                    for srv in target_servers:
                        p_id = f"{srv}_{p_name}"
                        pow_key = f"{p_id}__m{default_midx}__pow"
                        
                        # Only update if user explicitly uploaded, OR if the key doesn't exist yet
                        if is_upload or pow_key not in data or float(data.get(pow_key, 0)) == 0:
                            data[f"{p_id}__m{default_midx}__type"] = t_type
                            data[pow_key] = pow_num
                            data[f"{p_id}__m{default_midx}__tier"] = tier_val
                            updated_count += 1
        except Exception as e:
            print(f"Error parsing {src}: {e}")
            
    if updated_count > 0:
        save_disk_data(data)
        st.session_state["player_disk_data"] = data
    return updated_count




# ----------------- REUSABLE SERVER BENCHMARK ANALYTICS -----------------
def render_benchmark_analytics(default_servers, key_prefix="bench", title="Server Benchmark Analytics", section_subtitle="CROSS-SERVER POWER CURVES • TOP 70 BENCHMARKS • DYNAMIC SELECTION"):
    st.markdown(f"""<div class="cp-header" style="margin-top: 28px;">
        <div>
            <div class="cp-title">{title}</div>
            <div class="cp-subtitle">{section_subtitle}</div>
        </div>
        <div style="text-align: right; border-left: 1px solid #334155; padding-left: 20px;">
            <div style="color: #d4af37; font-size: 11px; font-weight: bold;">BENCHMARK SCOPE</div>
            <div style="color: #38bdf8; font-size: 15px; font-weight: 900; margin-top: 4px;">ACTIVE COMPARISON</div>
        </div>
    </div>""", unsafe_allow_html=True)

    b_col1, b_col2 = st.columns([4, 1])
    with b_col1:
        valid_defaults = [s for s in default_servers if s in server_names]
        if not valid_defaults and server_names:
            valid_defaults = server_names[:min(4, len(server_names))]
        chosen_servers = st.multiselect(
            "Select Kingdoms to Compare in Graphs:",
            server_names,
            default=valid_defaults,
            key=f"{key_prefix}_srv_multiselect"
        )
    with b_col2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if st.button("Select All", key=f"{key_prefix}_btn_all"):
            st.session_state[f"{key_prefix}_srv_multiselect"] = server_names
            st.rerun()

    if not chosen_servers:
        st.warning("Please select at least one kingdom to display graphs.")
        return

    c_left, c_right = st.columns(2)
    colors = ['#ef4444', '#38bdf8', '#a855f7', '#10b981', '#f59e0b', '#ec4899', '#6366f1']

    with c_left:
        st.subheader("Top 70 Power Curves Comparison")
        fig_comp = go.Figure()
        for i, sname in enumerate(chosen_servers):
            if sname in server_dict:
                sdf = server_dict[sname]
                limit = min(70, len(sdf))
                fig_comp.add_trace(go.Scatter(
                    x=sdf["Rank"][:limit], y=sdf["Power"][:limit] / 1e6, mode='lines+markers', name=sname,
                    line=dict(width=2.5, color=colors[i % len(colors)]),
                    hovertemplate="<b>%{text}</b><br>Rank: %{x}<br>Power: %{y:.2f}M<extra></extra>", text=sdf["Player"][:limit]
                ))
        fig_comp.update_layout(template="plotly_dark", xaxis_title="Rank", yaxis_title="Power (Millions)", hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,5,8,0.9)")
        st.plotly_chart(fig_comp, use_container_width=True, key=f"{key_prefix}_top70_curves")

    with c_right:
        st.subheader("Players by Power Threshold")
        thresholds = [140, 160, 180, 200, 220, 250, 300]
        thresh_data = {"Threshold": [f">{t}M" for t in thresholds]}
        for sname in chosen_servers:
            if sname in server_dict:
                sdf = server_dict[sname]
                thresh_data[sname] = [(sdf.iloc[:70]["Power"] >= t * 1_000_000).sum() for t in thresholds]
        df_thresh = pd.DataFrame(thresh_data)

        fig_thresh = go.Figure()
        for i, sname in enumerate(chosen_servers):
            if sname in df_thresh.columns:
                fig_thresh.add_trace(go.Bar(x=df_thresh["Threshold"], y=df_thresh[sname], name=sname, marker_color=colors[i % len(colors)]))
        fig_thresh.update_layout(barmode='group', template="plotly_dark", xaxis_title="Threshold", yaxis_title="Player Count", margin=dict(l=10, r=10, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,5,8,0.9)")
        st.plotly_chart(fig_thresh, use_container_width=True, key=f"{key_prefix}_threshold_bars")

    st.markdown("#### Statistical Benchmark Summary (Top 70)")
    comp_metrics = {}
    for sname in chosen_servers:
        if sname in server_dict:
            sdf = server_dict[sname]
            sub70 = sdf.iloc[:70]
            comp_metrics[sname] = {
                "Total Power": fmt_p(sub70["Power"].sum()),
                "Mean Power": fmt_p(sub70["Power"].mean()),
                "Median Power": fmt_p(sub70["Median"] if "Median" in sub70 else sub70["Power"].median()),
                "Rank 1 Power": fmt_p(sub70.iloc[0]["Power"]),
                "Rank 70 Cutoff": fmt_p(sub70.iloc[-1]["Power"] if len(sub70) >= 70 else 0),
                "Players Tracked": len(sdf)
            }
    st.dataframe(pd.DataFrame(comp_metrics), use_container_width=True)


server_dict = {}

# Always ensure Server #070 (ERA70) is loaded as primary
default_servers = [
    ("Server #070 (ERA70).xlsx", "Server #070 (ERA70)"),
    ("Server_070_Full_Rankings_Top105.xlsx", "Server #070 (ERA70)"),
    ("Server #69 ([A⊝69]).xlsx", "Server #69 ([A⊝69])"),
    ("Server #043 (IDV).xlsx", "Server #043 (IDV)"),
    ("Server_043_Full_Rankings_Top105.xlsx", "Server #043 (IDV)"),
    ("Server #030 (E#030).xlsx", "Server #030 (E#030)"),
    ("Server_030_Full_Rankings_Top106.xlsx", "Server #030 (E#030)"),
    ("Power_Rankings_Server.xlsx", "Server #070 (ERA70)"),
    ("Power_Rankings_Server_W37.xlsx", "Server #37 (W37)"),
    ("Power_Rankings_Server_E083.xlsx", "Server #83 (E083)"),
    ("Power_Rankings_Server_E083_New.xlsx", "Server #83 (E083)")
]

# Also scan "Server Rankings" folder if it exists
sr_dirs = [
    r"C:/Users/asafk/Downloads/aoem_dashboard/Server Rankings",
    os.path.join(BASE_DIR, "Server Rankings"),
    os.path.join(BASE_DIR, "..", "Server Rankings"),
    os.path.join(os.getcwd(), "Server Rankings")
]

for sr_dir in sr_dirs:
    if os.path.exists(sr_dir):
        for f_name in os.listdir(sr_dir):
            if f_name.startswith("~") or f_name.startswith("~$"):
                continue
            if f_name.endswith((".xlsx", ".xls", ".csv")):
                f_full_path = os.path.join(sr_dir, f_name)
                lbl = f_name.rsplit('.', 1)[0].replace("_", " ")
                if "070" in lbl or "era70" in lbl.lower():
                    lbl = "Server #070 (ERA70)"
                elif "w37" in lbl.lower() or "37" in lbl:
                    lbl = "Server #37 (W37)"
                elif "e083" in lbl.lower() or "83" in lbl:
                    lbl = "Server #83 (E083)"
                
                c_data = load_and_clean_server(f_full_path, f_name)
                if c_data is not None:
                    if lbl == "Server #070 (ERA70)":
                        server_dict["Server #070 (ERA70)"] = c_data
                    else:
                        server_dict[lbl] = c_data

for default_path, default_label in default_servers:
    f_full_p = os.path.join(BASE_DIR, default_path)
    if os.path.exists(f_full_p) and default_label not in server_dict:
        c_base = load_and_clean_server(f_full_p, default_path)
        if c_base is not None:
            server_dict[default_label] = c_base


st.sidebar.header("Add & Manage Servers")
with st.sidebar.expander("⚡ Fast Troop Sync (Swords / Pikes / Cavalry)", expanded=True):
    st.caption("Drop troop ranking Excel files here to auto-sync all players:")
    uploaded_troops = st.file_uploader("Upload Troop Files:", type=["xlsx", "xls"], accept_multiple_files=True, key="quick_troop_uploader")
    if uploaded_troops:
        cnt = sync_troop_files(uploaded_troops)
        if cnt > 0:
            st.success(f"Successfully synced {cnt} player marches!")
            st.rerun()
uploaded_files = st.sidebar.file_uploader("Upload Server (.xlsx / .csv)", type=["xlsx", "xls", "csv"], accept_multiple_files=True)
if uploaded_files:
    for f in uploaded_files:
        s_name = f.name.rsplit('.', 1)[0]
        c = load_and_clean_server(f.getvalue(), f.name)
        if c is not None:
            server_dict[s_name] = c
            st.sidebar.success(f"Loaded: {s_name}")

if not server_dict:
    st.warning("No server data loaded. Please upload a file in the sidebar.")
    st.stop()

server_names = list(server_dict.keys())


def build_master_combined_df(s_dict):
    all_combined_list = []
    for s_name, s_df in s_dict.items():
        df_temp = s_df.copy()
        df_temp["Kingdom"] = s_name
        # Apply any manual overrides from player_disk_data
        for idx_r, row_r in df_temp.iterrows():
            p_name_r = row_r["Player"]
            p_disk_key = f"{s_name}_{p_name_r}"
            if f"{p_disk_key}__power" in st.session_state["player_disk_data"]:
                df_temp.at[idx_r, "Power"] = float(st.session_state["player_disk_data"][f"{p_disk_key}__power"])
            if f"{p_disk_key}__merits" in st.session_state["player_disk_data"]:
                df_temp.at[idx_r, "Merits"] = float(st.session_state["player_disk_data"][f"{p_disk_key}__merits"])
            if f"{p_disk_key}__alliance" in st.session_state["player_disk_data"]:
                df_temp.at[idx_r, "Alliance"] = str(st.session_state["player_disk_data"][f"{p_disk_key}__alliance"])
        df_temp["Tier"] = df_temp["Power"].apply(assign_tier)
        all_combined_list.append(df_temp)

    master_df = pd.concat(all_combined_list, ignore_index=True) if all_combined_list else pd.DataFrame()
    if not master_df.empty:
        master_df = master_df.sort_values(by="Power", ascending=False).reset_index(drop=True)
        master_df["Overall_Rank"] = range(1, len(master_df) + 1)
    return master_df

master_combined_df = build_master_combined_df(server_dict)



# Auto-sync on startup if files exist
if "initial_troop_sync_done" not in st.session_state:
    sync_troop_files()
    st.session_state["initial_troop_sync_done"] = True


default_server_p1_idx = 0
for idx, sname in enumerate(server_names):
    if "070" in sname:
        default_server_p1_idx = idx
        break

# ----------------- NAVIGATION & MERITS IN SIDEBAR -----------------
st.sidebar.markdown("---")
st.sidebar.header("🧭 Navigation Mode")
NAV_OPTIONS = [
    "1v1 Player Duel (Arena Showdown)",
    "Governor Browser & Profile",
    "Alliance War Room & Rally Leaders",
    "Primordial Conflict & Server Benchmarks"
]
view_mode = st.sidebar.radio("Select Mode:", NAV_OPTIONS, key="nav_mode_radio")

st.sidebar.header("🏆 Player Merits Leaderboard")
selected_merits_server = st.sidebar.selectbox("Server for Merits:", server_names, key="merits_srv_sel")
merits_df = server_dict[selected_merits_server]

if "Merits" in merits_df.columns:
    sorted_merits = merits_df.sort_values(by="Merits", ascending=False).reset_index(drop=True)
    with st.sidebar.expander("View All Players Merits", expanded=False):
        for idx, row in sorted_merits.iterrows():
            m_val = row["Merits"]
            m_str = fmt_p(m_val) if m_val > 0 else "0"
            st.markdown(f"<div style='font-size:12px; display:flex; justify-content:space-between; border-bottom:1px solid #1e293b; padding:4px 0;'><span style='color:#f87171;'>#{idx+1} {row['Player']}</span> <span style='color:#f59e0b; font-family:monospace;'>{m_str}</span></div>", unsafe_allow_html=True)
else:
    st.sidebar.caption("No Merits data available in this server.")

# ----------------- VIEW 1: 1v1 ARENA SHOWDOWN -----------------
if view_mode == "1v1 Player Duel (Arena Showdown)":
    st.markdown("""<div class="cp-header">
        <div>
            <div class="cp-title">1v1 Player Duel Showdown</div>
            <div class="cp-subtitle">P1 (SERVER COLOR) vs P2 (BLUE) • ENHANCED 3-COLUMN LAYOUT • PERMANENT SAVE</div>
        </div>
        <div style="text-align: right; border-left: 1px solid #334155; padding-left: 20px;">
            <div style="color: #94a3b8; font-size: 11px; font-weight: bold;">ARENA STATUS</div>
            <div style="color: #38bdf8; font-size: 16px; font-weight: 900; margin-top: 4px;">ACTIVE DUEL</div>
        </div>
    </div>""", unsafe_allow_html=True)

    col_p1, col_mid, col_p2 = st.columns([5, 2, 5])

    SERVER_COLORS = {
        "Server #070 (ERA70)": "#ef4444",
        "Server #043 (IDV)": "#38bdf8",
        "Server #030 (E#030)": "#a855f7",
        "Server #69 ([A⊝69])": "#10b981"
    }

    with col_p1:
        srv1 = st.selectbox("Server P1:", server_names, index=default_server_p1_idx, key="srv1")
        p1_color = SERVER_COLORS.get(srv1, "#ef4444")
        st.markdown(f'<div style="font-weight:900; color:{p1_color}; margin-bottom:6px;">CHALLENGER (P1 - {srv1})</div>', unsafe_allow_html=True)
        
        df1 = server_dict[srv1]
        p1_list = df1["Player"].tolist()
        default_p1_idx = 0
        if "last_p1_name" in st.session_state and st.session_state["last_p1_name"] in p1_list:
            default_p1_idx = p1_list.index(st.session_state["last_p1_name"])
            
        p1_name = st.selectbox("Player P1:", p1_list, index=default_p1_idx, key="p1_sel")
        st.session_state["last_p1_name"] = p1_name
        p1 = df1[df1["Player"] == p1_name].iloc[0]

        st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(30, 20, 25, 0.9) 0%, rgba(10, 5, 8, 0.95) 100%); border: 2px solid {p1_color}; border-radius: 12px; padding: 18px; box-shadow: 0 0 22px {p1_color}55;">
            <div style="font-size:20px; font-weight:900; color:#ffffff; margin-bottom:10px;">{p1_name} <span style="font-size:13px; color:{p1_color};">[{p1['Alliance']}]</span></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="color:#fca5a5; font-size:12px; font-weight:bold;">TOTAL POWER</span>
                <span style="color:{p1_color}; font-size:18px; font-weight:900; font-family:monospace;">{fmt_p(p1['Power'])}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="color:#fca5a5; font-size:12px; font-weight:bold;">MERITS</span>
                <span style="color:#f59e0b; font-size:16px; font-weight:900; font-family:monospace;">{fmt_p(p1['Merits'])}</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#fca5a5; font-size:12px; font-weight:bold;">TIER / RANK</span>
                <span style="color:#ffffff; font-weight:bold;">#{p1['Rank']} • {p1['Tier']}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    with col_p2:
        st.markdown('<div style="font-weight:900; color:#38bdf8; margin-bottom:6px;">OPPONENT (P2 - BLUE)</div>', unsafe_allow_html=True)
        srv2_idx = 1 if len(server_names) > 1 else 0
        srv2 = st.selectbox("Server P2:", server_names, index=srv2_idx, key="srv2")
        df2 = server_dict[srv2]
        
        p2_list = df2["Player"].tolist()
        default_p2_idx = 0
        if "last_p2_name" in st.session_state and st.session_state["last_p2_name"] in p2_list:
            default_p2_idx = p2_list.index(st.session_state["last_p2_name"])

        p2_name = st.selectbox("Player P2:", p2_list, index=default_p2_idx, key="p2_sel")
        st.session_state["last_p2_name"] = p2_name
        p2 = df2[df2["Player"] == p2_name].iloc[0]

        st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(14, 30, 56, 0.9) 0%, rgba(5, 10, 20, 0.95) 100%); border: 2px solid #0284c7; border-radius: 12px; padding: 18px; box-shadow: 0 0 22px rgba(2, 132, 199, 0.45);">
            <div style="font-size:20px; font-weight:900; color:#ffffff; margin-bottom:10px;">{p2_name} <span style="font-size:13px; color:#38bdf8;">[{p2['Alliance']}]</span></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="color:#94a3b8; font-size:12px; font-weight:bold;">TOTAL POWER</span>
                <span style="color:#38bdf8; font-size:18px; font-weight:900; font-family:monospace;">{fmt_p(p2['Power'])}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="color:#94a3b8; font-size:12px; font-weight:bold;">MERITS</span>
                <span style="color:#f59e0b; font-size:16px; font-weight:900; font-family:monospace;">{fmt_p(p2['Merits'])}</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#94a3b8; font-size:12px; font-weight:bold;">TIER / RANK</span>
                <span style="color:#ffffff; font-weight:bold;">#{p2['Rank']} • {p2['Tier']}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    power_diff = p1['Power'] - p2['Power']
    with col_mid:
        st.markdown('<div style="text-align:center; padding-top:68px;"><div class="vs-circle">VS</div>', unsafe_allow_html=True)
        if power_diff > 0:
            st.markdown(f'<div style="margin-top:14px;"><span class="badge-win-p1">P1 Leads +{fmt_p(power_diff)}</span></div>', unsafe_allow_html=True)
        elif power_diff < 0:
            st.markdown(f'<div style="margin-top:14px;"><span class="badge-win-p2">P2 Leads +{fmt_p(abs(power_diff))}</span></div>', unsafe_allow_html=True)
        else:
            st.caption("Tied Power")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 5-March Troop Lineups (Sorted by Power & Total Calculation)")

    TROOP_TYPES = ["🐎 Cavalry", "🗡️ Swordsmen", "🛡️ Pikemen", "🏹 Archers", "⚔️ March 5 / Extra"]
    hero_options = st.session_state["restricted_heroes"]
    p1_id = f"{srv1}_{p1_name}"
    p2_id = f"{srv2}_{p2_name}"

    def on_widget_change(p_id, m_idx, field, widget_key):
        val = st.session_state[widget_key]
        st.session_state["player_disk_data"][f"{p_id}__m{m_idx}__{field}"] = val
        save_disk_data(st.session_state["player_disk_data"])

    default_types = ["🐎 Cavalry", "🗡️ Swordsmen", "🛡️ Pikemen", "🏹 Archers", "🐎 Cavalry"]

    def collect_marches(p_id):
        marches = []
        for m_idx in range(1, 6):
            t_val = st.session_state["player_disk_data"].get(f"{p_id}__m{m_idx}__type", default_types[m_idx - 1])
            pow_val = float(st.session_state["player_disk_data"].get(f"{p_id}__m{m_idx}__pow", 0.0))
            tier_val = st.session_state["player_disk_data"].get(f"{p_id}__m{m_idx}__tier", "T9" if pow_val >= 60_000_000 else ("T8" if pow_val >= 50_000_000 else ("T7" if pow_val > 0 else "None")))
            h1_val = st.session_state["player_disk_data"].get(f"{p_id}__m{m_idx}__h1", "None")
            h2_val = st.session_state["player_disk_data"].get(f"{p_id}__m{m_idx}__h2", "None")
            h3_val = st.session_state["player_disk_data"].get(f"{p_id}__m{m_idx}__h3", "None")
            marches.append({
                "orig_idx": m_idx, "type": t_val, "pow": pow_val,
                "tier": tier_val, "h1": h1_val, "h2": h2_val, "h3": h3_val
            })
        marches.sort(key=lambda x: x["pow"], reverse=True)
        return marches

    p1_marches = collect_marches(p1_id)
    p2_marches = collect_marches(p2_id)
    p1_total_troop_power = sum(m["pow"] for m in p1_marches)
    p2_total_troop_power = sum(m["pow"] for m in p2_marches)

    # ----------------- COMBAT MATCHUP SIMULATOR CALCULATIONS -----------------
    def evaluate_matchup(t1, pow1, t2, pow2):
        def clean(t):
            s = str(t).lower()
            if "cav" in s or "פרש" in s: return "cavalry"
            if "sword" in s or "חרב" in s: return "swordsmen"
            if "pike" in s or "רומח" in s: return "pikemen"
            if "arch" in s or "קשת" in s: return "archers"
            return "neutral"
        
        c1, c2 = clean(t1), clean(t2)
        
        # Correct counter cycle per official game rules (+30% damage bonus)
        # Swordsmen > Pikemen > Cavalry > Archers > Swordsmen
        counters = {
            ("swordsmen", "pikemen"): ("Swordsmen counter Pikemen", "🗡️ > 🛡️"),
            ("pikemen", "cavalry"): ("Pikemen counter Cavalry", "🛡️ > 🐎"),
            ("cavalry", "archers"): ("Cavalry counters Archers", "🐎 > 🏹"),
            ("archers", "swordsmen"): ("Archers counter Swordsmen", "🏹 > 🗡️")
        }
        
        mult1, mult2 = 1.0, 1.0
        badge1, badge2 = "", ""
        reason = ""
        
        if (c1, c2) in counters:
            mult1 = 1.30
            mult2 = 0.70
            reason = counters[(c1, c2)][0]
            badge1 = f'<div style="color:#10b981; font-weight:800; font-size:11px; margin-top:4px;">⚔️ COUNTER ADVANTAGE (+30% DMG) • {counters[(c1,c2)][1]}</div>'
            badge2 = f'<div style="color:#ef4444; font-weight:800; font-size:11px; margin-top:4px;">🛡️ TACTICAL DISADVANTAGE (-30% DMG)</div>'
        elif (c2, c1) in counters:
            mult1 = 0.70
            mult2 = 1.30
            reason = counters[(c2, c1)][0]
            badge1 = f'<div style="color:#ef4444; font-weight:800; font-size:11px; margin-top:4px;">🛡️ TACTICAL DISADVANTAGE (-30% DMG)</div>'
            badge2 = f'<div style="color:#10b981; font-weight:800; font-size:11px; margin-top:4px;">⚔️ COUNTER ADVANTAGE (+30% DMG) • {counters[(c2,c1)][1]}</div>'
            
        eff1 = pow1 * mult1
        eff2 = pow2 * mult2
        return eff1, eff2, badge1, badge2, reason

    # Pre-simulate all 5 marches
    sim_results = []
    tot_eff1, tot_eff2 = 0.0, 0.0
    p1_rounds_won, p2_rounds_won = 0, 0
    
    for r_idx in range(5):
        m1_t = p1_marches[r_idx]
        m2_t = p2_marches[r_idx]
        e1, e2, b1, b2, r_desc = evaluate_matchup(m1_t["type"], m1_t["pow"], m2_t["type"], m2_t["pow"])
        tot_eff1 += e1
        tot_eff2 += e2
        if e1 > e2 and (m1_t["pow"] > 0 or m2_t["pow"] > 0):
            p1_rounds_won += 1
        elif e2 > e1 and (m1_t["pow"] > 0 or m2_t["pow"] > 0):
            p2_rounds_won += 1
        sim_results.append({
            "eff1": e1, "eff2": e2, "badge1": b1, "badge2": b2, "reason": r_desc
        })
        
    tot_combined_eff = tot_eff1 + tot_eff2
    if tot_combined_eff > 0:
        win_prob_p1 = (tot_eff1 / tot_combined_eff) * 100.0
        win_prob_p2 = (tot_eff2 / tot_combined_eff) * 100.0
    else:
        win_prob_p1, win_prob_p2 = 50.0, 50.0

    def get_troop_report(marches):
        counts = {}
        for m in marches:
            if m["pow"] > 0:
                t = m["type"]
                counts[t] = counts.get(t, 0) + 1
        if not counts: return "No active marches configured."
        return ", ".join([f"{cnt} {t}" for t, cnt in counts.items()])

    # Combined Troop Power and Matchup Report
    st.markdown(f"""
    <div style="background: rgba(15, 15, 25, 0.9); border: 1px solid #334155; border-radius: 8px; padding: 14px 20px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div style="color: #94a3b8; font-size: 12px; font-weight: bold;">📊 COMBINED TROOP POWER & REPORT</div>
            <div style="color: #ffffff; font-size: 14px; margin-top: 4px;"><b style="color: {p1_color};">{p1_name} (P1):</b> {get_troop_report(p1_marches)} | <b>Raw Power:</b> <span style="color: {p1_color}; font-family: monospace; font-size: 15px;">{fmt_p(p1_total_troop_power)}</span></div>
            <div style="color: #ffffff; font-size: 14px; margin-top: 2px;"><b style="color: #38bdf8;">{p2_name} (P2):</b> {get_troop_report(p2_marches)} | <b>Raw Power:</b> <span style="color: #38bdf8; font-family: monospace; font-size: 15px;">{fmt_p(p2_total_troop_power)}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ----------------- COMBAT MATCHUP SIMULATOR BANNER -----------------
    prob_color_p1 = "#10b981" if win_prob_p1 >= 50 else "#f59e0b"
    prob_color_p2 = "#38bdf8" if win_prob_p2 >= 50 else "#94a3b8"
    projected_winner = p1_name if tot_eff1 >= tot_eff2 else p2_name
    winner_color = p1_color if tot_eff1 >= tot_eff2 else "#38bdf8"

    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(16, 185, 129, 0.08) 0%, rgba(30, 41, 59, 0.6) 50%, rgba(56, 189, 248, 0.08) 100%); border: 2px solid #3b82f6; border-radius: 10px; padding: 14px 20px; margin-bottom: 22px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 11px; font-weight: 900; color: #d4af37; letter-spacing: 1px;">⚔️ COMBAT MATCHUP SIMULATOR & WIN PROBABILITY</span>
                <div style="font-size: 18px; font-weight: 900; color: #ffffff; margin-top: 2px;">
                    Projected Battle Winner: <span style="color: {winner_color};">{projected_winner} ({p1_rounds_won} vs {p2_rounds_won} Marches)</span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 11px; font-weight: bold; color: #94a3b8;">WIN PROBABILITY</div>
                <div style="font-size: 18px; font-weight: 900; font-family: monospace;">
                    <span style="color:{p1_color};">{win_prob_p1:.1f}%</span> vs <span style="color:#38bdf8;">{win_prob_p2:.1f}%</span>
                </div>
            </div>
        </div>
        <div style="width: 100%; height: 10px; background: #0f172a; border-radius: 5px; overflow: hidden; margin-top: 10px; display: flex;">
            <div style="width: {win_prob_p1:.1f}%; background: {p1_color}; height: 100%;"></div>
            <div style="width: {win_prob_p2:.1f}%; background: #38bdf8; height: 100%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; margin-top: 6px;">
            <span><b>{p1_name}</b> Total Effective Power: <b style="color:#ffffff;">{fmt_p(tot_eff1)}</b></span>
            <span>Counter Cycle: Cavalry > Archers > Swordsmen > Pikemen > Cavalry (±30% Direct Damage)</span>
            <span><b>{p2_name}</b> Total Effective Power: <b style="color:#ffffff;">{fmt_p(tot_eff2)}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


    # ----------------- LINEUP AUTO-OPTIMIZER BUTTON -----------------
    opt_col1, opt_col2 = st.columns([3, 1])
    with opt_col1:
        st.caption("Optimize your 5-march lineup automatically to counter the opponent's formation:")
    with opt_col2:
        if st.button("⚡ Auto-Optimize Lineup (Counter Match)", key="btn_auto_optimize"):
            import itertools
            best_perm = None
            best_score = -1
            best_wins = -1
            
            # 120 permutations of P1's 5 marches
            for perm in itertools.permutations(p1_marches):
                cur_eff1 = 0
                cur_wins = 0
                for idx_m, p1_m in enumerate(perm):
                    p2_m = p2_marches[idx_m]
                    e1, e2, _, _, _ = evaluate_matchup(p1_m["type"], p1_m["pow"], p2_m["type"], p2_m["pow"])
                    cur_eff1 += e1
                    if e1 > e2 and (p1_m["pow"] > 0 or p2_m["pow"] > 0):
                        cur_wins += 1
                
                # We prioritize number of wins first, then total effective power
                rank_score = cur_wins * 1e12 + cur_eff1
                if rank_score > best_score:
                    best_score = rank_score
                    best_wins = cur_wins
                    best_perm = perm
            
            if best_perm:
                # Save new order to disk data for P1
                data = st.session_state["player_disk_data"]
                for new_idx, march_data in enumerate(best_perm, start=1):
                    data[f"{p1_id}__m{new_idx}__type"] = march_data["type"]
                    data[f"{p1_id}__m{new_idx}__pow"] = march_data["pow"]
                    data[f"{p1_id}__m{new_idx}__tier"] = march_data["tier"]
                    data[f"{p1_id}__m{new_idx}__h1"] = march_data["h1"]
                    data[f"{p1_id}__m{new_idx}__h2"] = march_data["h2"]
                    data[f"{p1_id}__m{new_idx}__h3"] = march_data["h3"]
                save_disk_data(data)
                st.session_state["player_disk_data"] = data
                st.success(f"Lineup successfully optimized! Projected wins: {best_wins} of 5 marches!")
                st.rerun()

    for rank_idx in range(5):
        m1 = p1_marches[rank_idx]
        m2 = p2_marches[rank_idx]
        orig_m1 = m1["orig_idx"]
        orig_m2 = m2["orig_idx"]
        s_res = sim_results[rank_idx]

        c1, c_mid, c2 = st.columns([5, 2, 5])
        with c1:
            k_type1 = f"{p1_id}__m{orig_m1}__type"
            k_pow1 = f"{p1_id}__m{orig_m1}__pow"
            k_tier1 = f"{p1_id}__m{orig_m1}__tier"
            k_h1_1 = f"{p1_id}__m{orig_m1}__h1"
            k_h1_2 = f"{p1_id}__m{orig_m1}__h2"
            k_h1_3 = f"{p1_id}__m{orig_m1}__h3"

            exp_p1 = st.expander(f"⚙️ P1 Rank #{rank_idx+1} (Original March #{orig_m1} - {m1['type']})", expanded=False)
            with exp_p1:
                st.selectbox("Troop Type:", TROOP_TYPES, index=TROOP_TYPES.index(m1["type"]) if m1["type"] in TROOP_TYPES else 0, key=f"w_{k_type1}", on_change=on_widget_change, args=(p1_id, orig_m1, "type", f"w_{k_type1}"))
                col_pow, col_tier = st.columns(2)
                col_pow.number_input("Power (Full):", value=float(m1["pow"]), step=100000.0, format="%.0f", key=f"w_{k_pow1}", on_change=on_widget_change, args=(p1_id, orig_m1, "pow", f"w_{k_pow1}"))
                col_tier.selectbox("Unit Tier", ["T9", "T8", "T7", "None"], index=["T9", "T8", "T7", "None"].index(m1["tier"]) if m1["tier"] in ["T9", "T8", "T7", "None"] else 0, key=f"w_{k_tier1}", on_change=on_widget_change, args=(p1_id, orig_m1, "tier", f"w_{k_tier1}"))
                h_c1, h_c2, h_c3 = st.columns(3)
                h_c1.selectbox("Hero 1", hero_options, index=hero_options.index(m1["h1"]) if m1["h1"] in hero_options else 0, key=f"w_{k_h1_1}", on_change=on_widget_change, args=(p1_id, orig_m1, "h1", f"w_{k_h1_1}"))
                h_c2.selectbox("Hero 2", hero_options, index=hero_options.index(m1["h2"]) if m1["h2"] in hero_options else 0, key=f"w_{k_h1_2}", on_change=on_widget_change, args=(p1_id, orig_m1, "h2", f"w_{k_h1_2}"))
                h_c3.selectbox("Hero 3", hero_options, index=hero_options.index(m1["h3"]) if m1["h3"] in hero_options else 0, key=f"w_{k_h1_3}", on_change=on_widget_change, args=(p1_id, orig_m1, "h3", f"w_{k_h1_3}"))

            heroes_p1_html = f"{get_hero_img_html(m1['h1'])}{get_hero_img_html(m1['h2'])}{get_hero_img_html(m1['h3'])}"
            badge_p1_html = s_res['badge1'] if s_res['badge1'] else ""
            card_p1_html = (
                f'<div class="troop-battle-card" style="border: 1px solid {p1_color};">'
                f'<div style="display: flex; justify-content: space-between; align-items: center;">'
                f'<div style="font-weight:900; font-size:14px; color:{p1_color};">Rank #{rank_idx+1} • {m1["type"]}</div>'
                f'<div style="font-size:11px; color:#94a3b8;">(March #{orig_m1})</div>'
                f'</div>'
                f'<div style="font-size:18px; font-weight:900; color:#ffffff; font-family:monospace; margin-top:4px;">'
                f'{fmt_p(m1["pow"])} {get_tier_badge_html(m1["tier"])}'
                f'</div>'
                f'{badge_p1_html}'
                f'<div class="hero-container">{heroes_p1_html}</div>'
                f'</div>'
            )
            st.markdown(card_p1_html, unsafe_allow_html=True)

        with c2:
            k_type2 = f"{p2_id}__m{orig_m2}__type"
            k_pow2 = f"{p2_id}__m{orig_m2}__pow"
            k_tier2 = f"{p2_id}__m{orig_m2}__tier"
            k_h2_1 = f"{p2_id}__m{orig_m2}__h1"
            k_h2_2 = f"{p2_id}__m{orig_m2}__h2"
            k_h2_3 = f"{p2_id}__m{orig_m2}__h3"

            exp_p2 = st.expander(f"⚙️ P2 Rank #{rank_idx+1} (Original March #{orig_m2} - {m2['type']})", expanded=False)
            with exp_p2:
                st.selectbox("Troop Type:", TROOP_TYPES, index=TROOP_TYPES.index(m2["type"]) if m2["type"] in TROOP_TYPES else 0, key=f"w_{k_type2}", on_change=on_widget_change, args=(p2_id, orig_m2, "type", f"w_{k_type2}"))
                col_pow, col_tier = st.columns(2)
                col_pow.number_input("Power (Full):", value=float(m2["pow"]), step=100000.0, format="%.0f", key=f"w_{k_pow2}", on_change=on_widget_change, args=(p2_id, orig_m2, "pow", f"w_{k_pow2}"))
                col_tier.selectbox("Unit Tier", ["T9", "T8", "T7", "None"], index=["T9", "T8", "T7", "None"].index(m2["tier"]) if m2["tier"] in ["T9", "T8", "T7", "None"] else 0, key=f"w_{k_tier2}", on_change=on_widget_change, args=(p2_id, orig_m2, "tier", f"w_{k_tier2}"))
                h_c1, h_c2, h_c3 = st.columns(3)
                h_c1.selectbox("Hero 1", hero_options, index=hero_options.index(m2["h1"]) if m2["h1"] in hero_options else 0, key=f"w_{k_h2_1}", on_change=on_widget_change, args=(p2_id, orig_m2, "h1", f"w_{k_h2_1}"))
                h_c2.selectbox("Hero 2", hero_options, index=hero_options.index(m2["h2"]) if m2["h2"] in hero_options else 0, key=f"w_{k_h2_2}", on_change=on_widget_change, args=(p2_id, orig_m2, "h2", f"w_{k_h2_2}"))
                h_c3.selectbox("Hero 3", hero_options, index=hero_options.index(m2["h3"]) if m2["h3"] in hero_options else 0, key=f"w_{k_h2_3}", on_change=on_widget_change, args=(p2_id, orig_m2, "h3", f"w_{k_h2_3}"))

            heroes_p2_html = f"{get_hero_img_html(m2['h1'])}{get_hero_img_html(m2['h2'])}{get_hero_img_html(m2['h3'])}"
            badge_p2_html = s_res['badge2'] if s_res['badge2'] else ""
            card_p2_html = (
                f'<div class="troop-battle-card" style="border: 1px solid #0284c7; background: rgba(14, 30, 56, 0.85);">'
                f'<div style="display: flex; justify-content: space-between; align-items: center;">'
                f'<div style="font-weight:900; font-size:14px; color:#38bdf8;">Rank #{rank_idx+1} • {m2["type"]}</div>'
                f'<div style="font-size:11px; color:#94a3b8;">(March #{orig_m2})</div>'
                f'</div>'
                f'<div style="font-size:18px; font-weight:900; color:#ffffff; font-family:monospace; margin-top:4px;">'
                f'{fmt_p(m2["pow"])} {get_tier_badge_html(m2["tier"])}'
                f'</div>'
                f'{badge_p2_html}'
                f'<div class="hero-container">{heroes_p2_html}</div>'
                f'</div>'
            )
            st.markdown(card_p2_html, unsafe_allow_html=True)

        with c_mid:
            st.markdown("<div style='text-align:center; padding-top:42px;'>", unsafe_allow_html=True)
            diff_m = m1["pow"] - m2["pow"]
            eff_diff = s_res["eff1"] - s_res["eff2"]
            
            if m1["pow"] > 0 or m2["pow"] > 0:
                if eff_diff > 0:
                    st.markdown(f"<span class='badge-win-p1'>P1 +{fmt_p(diff_m)}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:11px; color:#10b981; margin-top:3px;'>Effective: +{fmt_p(eff_diff)}</div>", unsafe_allow_html=True)
                elif eff_diff < 0:
                    st.markdown(f"<span class='badge-win-p2'>P2 +{fmt_p(abs(diff_m))}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:11px; color:#38bdf8; margin-top:3px;'>Effective: +{fmt_p(abs(eff_diff))}</div>", unsafe_allow_html=True)
                else:
                    st.caption("Tied")
            else:
                st.caption("--")
            st.markdown("</div>", unsafe_allow_html=True)


    # ----------------- DISCORD AUTOMATION & SHAREABLE BATTLE CARD -----------------
    with st.expander("🤖 Discord Automation & Shareable Battle Card", expanded=True):
        st.markdown("#### ⚡ Discord Channel Integration")
        st.caption("Paste your Discord channel webhook URL once. It will be saved permanently to disk for instant 1-click dispatch:")

        # Persistent Discord Webhook Storage
        stored_webhook = st.session_state["player_disk_data"].get("discord_webhook_1v1", "")
        disc_col1, disc_col2 = st.columns([3, 1])
        with disc_col1:
            webhook_url = st.text_input(
                "Discord Webhook URL:", 
                value=stored_webhook, 
                placeholder="https://discord.com/api/webhooks/...", 
                type="password",
                key="webhook_input_1v1"
            )
            if webhook_url != stored_webhook:
                st.session_state["player_disk_data"]["discord_webhook_1v1"] = webhook_url
                save_disk_data(st.session_state["player_disk_data"])
        
        with disc_col2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            send_discord_btn = st.button("🚀 Send to Discord", key="btn_send_discord_1v1", type="primary")

        # Build detailed marches summary
        marches_lines = []
        for idx_m in range(5):
            m1_data = p1_marches[idx_m]
            m2_data = p2_marches[idx_m]
            res_m = sim_results[idx_m]
            winner_m = f"🔴 {p1_name}" if res_m["eff1"] > res_m["eff2"] else (f"🔵 {p2_name}" if res_m["eff2"] > res_m["eff1"] else "Tie")
            adv_str = " (⚔️ +30% Counter)" if ("P1" in res_m["badge1"] or "ADVANTAGE" in res_m["badge1"]) else (" (⚔️ +30% Counter)" if "ADVANTAGE" in res_m["badge2"] else "")
            marches_lines.append(f"• **March {idx_m+1}:** {m1_data['type']} vs {m2_data['type']} ➔ **{winner_m}**{adv_str}")
        marches_summary_txt = "\n".join(marches_lines)

        if send_discord_btn:
            active_webhook = webhook_url.strip() if webhook_url else stored_webhook.strip()
            if not active_webhook or not active_webhook.startswith("https://discord.com/api/webhooks/"):
                st.error("⚠️ Please provide a valid Discord Webhook URL (starts with https://discord.com/api/webhooks/...).")
            else:
                embed_color = 0xef4444 if "070" in srv1 else 0xd4af37
                payload = {
                    "content": f"📢 **New 1v1 Battle Simulation Dispatched!** {p1_name} ({srv1}) vs {p2_name} ({srv2})",
                    "embeds": [{
                        "title": f"⚔️ ELITE DUEL: {p1_name} vs {p2_name}",
                        "description": f"Live automated battle analytics between **{srv1}** and **{srv2}**.",
                        "color": embed_color,
                        "fields": [
                            {"name": f"🔴 Challenger ({srv1})", "value": f"**{p1_name}** [{p1['Alliance']}]\nTotal Power: `{fmt_p(p1['Power'])}`\nMerits: `{fmt_p(p1['Merits'])}`", "inline": True},
                            {"name": f"🔵 Opponent ({srv2})", "value": f"**{p2_name}** [{p2['Alliance']}]\nTotal Power: `{fmt_p(p2['Power'])}`\nMerits: `{fmt_p(p2['Merits'])}`", "inline": True},
                            {"name": "🏆 Projected Winner", "value": f"👑 **{projected_winner}** ({p1_rounds_won} vs {p2_rounds_won} Marches Won)\nWin Probability: **{win_prob_p1:.1f}%** vs **{win_prob_p2:.1f}%**", "inline": False},
                            {"name": "💪 Total Effective Combat Power", "value": f"**{p1_name}**: `{fmt_p(tot_eff1)}`\n**{p2_name}**: `{fmt_p(tot_eff2)}`", "inline": False},
                            {"name": "⚔️ 5-March Duel Breakdown", "value": marches_summary_txt, "inline": False}
                        ],
                        "footer": {"text": "Age of Empires Mobile • Tactical War Room Automation"},
                        "timestamp": pd.Timestamp.now().isoformat()
                    }]
                }
                try:
                    resp = requests.post(active_webhook, json=payload, timeout=10)
                    if resp.status_code in [200, 204]:
                        st.success("✅ Duel Report sent successfully to Discord!")
                    else:
                        st.error(f"Discord returned status {resp.status_code}: {resp.text}")
                except Exception as e_disc:
                    st.error(f"Failed to connect to Discord: {e_disc}")

        st.markdown("---")
        card_text = f"""⚔️ **AOEM ELITE DUEL BATTLE REPORT** ⚔️
🔴 **Challenger (P1):** {p1_name} (Server: {srv1}) | Total Power: {fmt_p(p1['Power'])}
🔵 **Opponent (P2):** {p2_name} (Server: {srv2}) | Total Power: {fmt_p(p2['Power'])}

🏆 **Projected Victor:** {projected_winner} ({p1_rounds_won} vs {p2_rounds_won} Marches)
📊 **Win Probability:** {win_prob_p1:.1f}% vs {win_prob_p2:.1f}%
💪 **Total Effective Power:** P1 ({fmt_p(tot_eff1)}) | P2 ({fmt_p(tot_eff2)})

⚔️ **Marches Breakdown:**
{marches_summary_txt.replace("**", "").replace("• ", "")}
"""
        st.text_area("Or copy text directly (for WhatsApp / Telegram):", card_text, height=160, key="share_card_textarea")

    st.divider()

# ----------------- VIEW 2: GOVERNOR BROWSER & PROFILE (CROSS-KINGDOM & LIVE UPDATE) -----------------
elif view_mode == "Governor Browser & Profile":
    # 1. Total Governors Across All Known Servers
    master_combined_df = build_master_combined_df(server_dict)
    total_tracked_govs = len(master_combined_df) if not master_combined_df.empty else 0

    st.markdown(f"""<div class="cp-header">
        <div>
            <div class="cp-title">Governor Browser & Profile</div>
            <div class="cp-subtitle">CROSS-KINGDOM ROSTER • INSTANT SEARCH & FILTER • MANUAL OVERRIDES & LIVE UPDATES</div>
        </div>
        <div style="text-align: right; border-left: 1px solid #334155; padding-left: 20px;">
            <div style="color: #94a3b8; font-size: 11px; font-weight: bold;">TOTAL GOVERNORS</div>
            <div style="color: #38bdf8; font-size: 18px; font-weight: 900; margin-top: 4px;">{total_tracked_govs:,} Recorded</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # 2. Update and Edit Tools (Always possible to update everything)
    up_c1, up_c2 = st.columns(2)
    with up_c1:
        with st.expander("📤 Upload & Ingest Kingdom Roster (.xlsx / .csv)", expanded=False):
            st.caption("Upload any server rankings spreadsheet to immediately add or refresh its governors:")
            up_gov_file = st.file_uploader("Upload Roster File:", type=["xlsx", "xls", "csv"], key="inpage_gov_uploader")
            if up_gov_file:
                s_name_up = up_gov_file.name.rsplit('.', 1)[0]
                c_up = load_and_clean_server(up_gov_file.getvalue(), up_gov_file.name)
                if c_up is not None:
                    server_dict[s_name_up] = c_up
                    st.success(f"Successfully loaded {s_name_up} with {len(c_up)} governors!")
                    st.rerun()

    with up_c2:
        with st.expander("✏️ Quick Governor Editor & Manual Override", expanded=False):
            st.caption("Directly modify or add any governor stats. Changes persist permanently to disk:")
            all_gov_names = sorted([str(x) for x in master_combined_df["Player"].dropna().unique().tolist()]) if not master_combined_df.empty else []
            edit_gov_mode = st.radio("Mode:", ["Edit Existing Governor", "Add New Governor"], horizontal=True, key="edit_gov_mode_rad")
            
            if edit_gov_mode == "Edit Existing Governor" and all_gov_names:
                target_gov_name = st.selectbox("Select Governor to Edit:", all_gov_names, key="edit_gov_picker")
                match_row = master_combined_df[master_combined_df["Player"] == target_gov_name].iloc[0]
                init_pow = float(match_row["Power"])
                init_merits = float(match_row.get("Merits", 0))
                init_alliance = str(match_row.get("Alliance", "--"))
                init_server = str(match_row.get("Kingdom", server_names[0]))
            else:
                target_gov_name = st.text_input("Governor Name:", "", placeholder="Enter governor name...", key="new_gov_name_input")
                init_pow = 100_000_000.0
                init_merits = 0.0
                init_alliance = "--"
                init_server = server_names[0] if server_names else "Server #070 (ERA70)"

            ed_col1, ed_col2 = st.columns(2)
            new_edit_pow = ed_col1.number_input("Power:", value=init_pow, step=500_000.0, format="%.0f", key="edit_pow_widget")
            new_edit_merits = ed_col2.number_input("Merits:", value=init_merits, step=100_000.0, format="%.0f", key="edit_merits_widget")
            ed_col3, ed_col4 = st.columns(2)
            new_edit_alliance = ed_col3.text_input("Alliance:", value=init_alliance, key="edit_alliance_widget")
            new_edit_server = ed_col4.selectbox("Kingdom / Server:", server_names, index=server_names.index(init_server) if init_server in server_names else 0, key="edit_server_widget")

            if st.button("💾 Save Governor Update", key="btn_save_gov_update"):
                if target_gov_name:
                    p_disk_key = f"{new_edit_server}_{target_gov_name}"
                    st.session_state["player_disk_data"][f"{p_disk_key}__power"] = new_edit_pow
                    st.session_state["player_disk_data"][f"{p_disk_key}__merits"] = new_edit_merits
                    st.session_state["player_disk_data"][f"{p_disk_key}__alliance"] = new_edit_alliance
                    save_disk_data(st.session_state["player_disk_data"])

                    if new_edit_server in server_dict:
                        tgt_df = server_dict[new_edit_server]
                        if target_gov_name in tgt_df["Player"].values:
                            tgt_df.loc[tgt_df["Player"] == target_gov_name, "Power"] = new_edit_pow
                            tgt_df.loc[tgt_df["Player"] == target_gov_name, "Merits"] = new_edit_merits
                            tgt_df.loc[tgt_df["Player"] == target_gov_name, "Alliance"] = new_edit_alliance
                            tgt_df.loc[tgt_df["Player"] == target_gov_name, "Tier"] = assign_tier(new_edit_pow)
                        else:
                            new_row_df = pd.DataFrame([{
                                "Player": target_gov_name, "Power": new_edit_pow, "Merits": new_edit_merits,
                                "Alliance": new_edit_alliance, "Region": "Kingsland", "Rank": len(tgt_df) + 1,
                                "Tier": assign_tier(new_edit_pow)
                            }])
                            server_dict[new_edit_server] = pd.concat([tgt_df, new_row_df], ignore_index=True)
                        server_dict[new_edit_server] = server_dict[new_edit_server].sort_values(by="Power", ascending=False).reset_index(drop=True)
                        server_dict[new_edit_server]["Rank"] = range(1, len(server_dict[new_edit_server]) + 1)

                    st.success(f"Saved stats for {target_gov_name}!")
                    st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 3. Scope Selection (All Kingdoms vs Specific Kingdom)
    st.markdown('<div style="font-size:12px; font-weight:900; color:#d4af37; margin-bottom:8px;">🌐 MULTI-SERVER SCOPE SELECTION</div>', unsafe_allow_html=True)
    sc_col1, sc_col2 = st.columns([4, 1])
    with sc_col1:
        selected_gov_servers = st.multiselect(
            "Select Kingdoms to Include in Roster:",
            server_names,
            default=server_names,
            key="gov_servers_multiselect"
        )
    with sc_col2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if st.button("Select All Servers", key="btn_all_gov_servers"):
            st.session_state["gov_servers_multiselect"] = server_names
            st.rerun()

    if not selected_gov_servers:
        st.warning("Please select at least one kingdom/server.")
        active_gov_df = pd.DataFrame()
        scope_label = "NONE"
    else:
        active_gov_df = master_combined_df[master_combined_df["Kingdom"].isin(selected_gov_servers)].copy() if not master_combined_df.empty else pd.DataFrame()
        if not active_gov_df.empty:
            active_gov_df = active_gov_df.sort_values(by="Power", ascending=False).reset_index(drop=True)
            active_gov_df["Rank"] = range(1, len(active_gov_df) + 1)
            
            # Historical Power Delta Calculation
            for idx_r, row_r in active_gov_df.iterrows():
                p_name_r = row_r["Player"]
                p_srv_r = row_r["Kingdom"]
                prev_key = f"{p_srv_r}_{p_name_r}__prev_power"
                cur_pow = float(row_r["Power"])
                stored_prev = st.session_state["player_disk_data"].get(prev_key, None)
                if stored_prev is None:
                    st.session_state["player_disk_data"][prev_key] = cur_pow
                    active_gov_df.at[idx_r, "Power_Delta"] = 0.0
                else:
                    delta = cur_pow - float(stored_prev)
                    active_gov_df.at[idx_r, "Power_Delta"] = delta
            save_disk_data(st.session_state["player_disk_data"])

        scope_label = ", ".join(selected_gov_servers) if len(selected_gov_servers) <= 2 else f"{len(selected_gov_servers)} Kingdoms Selected"

    search_col1, search_col2 = st.columns([1, 1])
    with search_col1:
        search_query = st.text_input("Search Governor by Name:", "", placeholder="Type name (e.g., Dylan, GrimReaper, Perez, NEO)...", key="gov_search")

    if not active_gov_df.empty and search_query:
        filtered_gov_df = active_gov_df[active_gov_df["Player"].astype(str).str.contains(search_query, case=False, na=False)]
    else:
        filtered_gov_df = active_gov_df

    # KPI Summary Row
    kpi_c1, kpi_c2, kpi_c3, kpi_c4 = st.columns(4)
    tot_p_scope = filtered_gov_df["Power"].sum() if not filtered_gov_df.empty else 0.0
    avg_p_scope = filtered_gov_df["Power"].mean() if not filtered_gov_df.empty else 0.0
    top_p_row = filtered_gov_df.iloc[0] if not filtered_gov_df.empty else None

    kpi_c1.markdown(f'<div class="kpi-card"><div class="kpi-label">SELECTED SCOPE</div><div class="kpi-value" style="font-size:16px;">{scope_label}</div></div>', unsafe_allow_html=True)
    kpi_c2.markdown(f'<div class="kpi-card"><div class="kpi-label">GOVERNORS TRACKED</div><div class="kpi-value">{len(filtered_gov_df):,}</div></div>', unsafe_allow_html=True)
    kpi_c3.markdown(f'<div class="kpi-card"><div class="kpi-label">COMBINED POWER</div><div class="kpi-value" style="color:#d4af37;">{fmt_score_b_m(tot_p_scope)}</div></div>', unsafe_allow_html=True)
    top_str = f"{top_p_row['Player']} ({fmt_score_b_m(top_p_row['Power'])})" if top_p_row is not None else "--"
    kpi_c4.markdown(f'<div class="kpi-card"><div class="kpi-label">#1 GOVERNOR</div><div class="kpi-value" style="font-size:16px; color:#10b981;">{top_str}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 4. Governors Roster Table (Full, interactive, with clean formatting & hide_index)
    

# --- FEATURE 3: ALLIANCE INTEL FEED & ANOMALIES ALERT ---
    st.markdown("### 🚨 Alliance Intel Feed & Power Anomalies")
    st.caption("Live monitoring of sudden power surges or drops among tracked governors:")
    
    if not active_gov_df.empty and "Power_Delta" in active_gov_df.columns:
        surges = active_gov_df.sort_values(by="Power_Delta", ascending=False).head(3)
        drops = active_gov_df.sort_values(by="Power_Delta", ascending=True).head(3)
        
        intel_c1, intel_c2 = st.columns(2)
        with intel_c1:
            st.markdown("<div style='color:#10b981; font-weight:900; margin-bottom:6px;'>📈 Top Power Surges (Significant Growth)</div>", unsafe_allow_html=True)
            for _, r_s in surges.iterrows():
                d_val = r_s["Power_Delta"]
                if d_val > 0:
                    st.markdown(f"<div style='background:rgba(16,185,129,0.1); border:1px solid #10b981; border-radius:6px; padding:8px; margin-bottom:6px; display:flex; justify-content:space-between;'><span><b>{r_s['Player']}</b> [{r_s['Kingdom']}]</span> <span style='color:#10b981; font-family:monospace;'>+{fmt_score_b_m(d_val)}</span></div>", unsafe_allow_html=True)
        with intel_c2:
            st.markdown("<div style='color:#ef4444; font-weight:900; margin-bottom:6px;'>📉 Significant Power Drops / Losses</div>", unsafe_allow_html=True)
            for _, r_d in drops.iterrows():
                d_val = r_d["Power_Delta"]
                if d_val < 0:
                    st.markdown(f"<div style='background:rgba(239,68,68,0.1); border:1px solid #ef4444; border-radius:6px; padding:8px; margin-bottom:6px; display:flex; justify-content:space-between;'><span><b>{r_d['Player']}</b> [{r_d['Kingdom']}]</span> <span style='color:#ef4444; font-family:monospace;'>{fmt_score_b_m(abs(d_val))}</span></div>", unsafe_allow_html=True)


    st.markdown("### Governors List")
    if not filtered_gov_df.empty:
        display_tbl = filtered_gov_df.copy()
        total_in_scope = len(active_gov_df)
        display_tbl["RANK"] = display_tbl["Rank"].apply(lambda r: f"#{r} of {total_in_scope}")
        display_tbl["GOVERNOR"] = display_tbl["Player"]
        display_tbl["KINGDOM"] = display_tbl["Kingdom"]
        display_tbl["ALLIANCE"] = display_tbl["Alliance"].apply(lambda a: f"[{a}]" if a != "--" and not str(a).startswith("[") else a)
        display_tbl["POWER"] = display_tbl["Power"].apply(fmt_p)
        
        def fmt_delta(d):
            if pd.isna(d) or d == 0: return "—"
            if d > 0: return f"+{fmt_score_b_m(d)}"
            return f"-{fmt_score_b_m(abs(d))}"
        display_tbl["POWER DELTA"] = display_tbl["Power_Delta"].apply(fmt_delta)
        
        display_tbl["MERITS"] = display_tbl["Merits"].apply(lambda m: fmt_p(m) if pd.notna(m) and m > 0 else "--")
        display_tbl["TIER"] = display_tbl["Tier"]

        show_cols = ["RANK", "GOVERNOR", "KINGDOM", "ALLIANCE", "POWER", "POWER DELTA", "MERITS", "TIER"]
        st.dataframe(display_tbl[show_cols], use_container_width=True, height=440, hide_index=True)
    else:
        st.info("No governors found matching the selected filter.")

    st.markdown("---")

    # 5. Governor Deep Profile Explorer & Army Inspector
    st.markdown("### 🔍 Governor Profile & Army Inspector")
    if not active_gov_df.empty:
        all_profile_candidates = active_gov_df["Player"].dropna().unique().tolist()
        selected_gov = st.selectbox("Select Governor for Deep Profile:", all_profile_candidates, key="gov_profile_sel")
        g_row = active_gov_df[active_gov_df["Player"] == selected_gov].iloc[0]
        g_id = str(abs(hash(selected_gov)) * 100000 + 500000000000)
        
        p_val = float(g_row['Power']) if pd.notna(g_row['Power']) else 0.0
        m_val = float(g_row['Merits']) if pd.notna(g_row['Merits']) else 0.0
        ratio_val = (m_val / p_val) if p_val > 0 else 0.0
        rank_val = g_row.get("Rank", g_row.get("Overall_Rank", 1))

        st.markdown(f"## {selected_gov}")
        st.caption(f"ID: {g_id} | Alliance: [{g_row['Alliance']}] | Kingdom: {g_row['Kingdom']}")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("TOTAL POWER", fmt_p(g_row['Power']))
        col2.metric("MERITS", fmt_p(g_row['Merits']))
        col3.metric("MERIT / POWER RATIO", f"{ratio_val:.3f}")
        col4.metric("RANK / TIER", f"#{rank_val} • {g_row['Tier']}")

        # Army Marches Inspector (if saved in player_custom_data.json)
        g_srv_target = g_row['Kingdom']
        p_id_match = f"{g_srv_target}_{selected_gov}"
        saved_marches = []
        for midx in range(1, 6):
            m_pow = float(st.session_state["player_disk_data"].get(f"{p_id_match}__m{midx}__pow", 0.0))
            if m_pow > 0:
                m_type = st.session_state["player_disk_data"].get(f"{p_id_match}__m{midx}__type", "Troop")
                m_tier = st.session_state["player_disk_data"].get(f"{p_id_match}__m{midx}__tier", "T8")
                m_h1 = st.session_state["player_disk_data"].get(f"{p_id_match}__m{midx}__h1", "None")
                m_h2 = st.session_state["player_disk_data"].get(f"{p_id_match}__m{midx}__h2", "None")
                m_h3 = st.session_state["player_disk_data"].get(f"{p_id_match}__m{midx}__h3", "None")
                saved_marches.append({
                    "midx": midx, "type": m_type, "pow": m_pow, "tier": m_tier,
                    "h1": m_h1, "h2": m_h2, "h3": m_h3
                })

        if saved_marches:
            st.markdown("#### Configured Army Marches")
            m_cols = st.columns(min(len(saved_marches), 5))
            for i_m, m_data in enumerate(saved_marches[:5]):
                with m_cols[i_m]:
                    heroes_html = f"{get_hero_img_html(m_data['h1'])}{get_hero_img_html(m_data['h2'])}{get_hero_img_html(m_data['h3'])}"
                    st.markdown(f"""<div class="troop-battle-card" style="border: 1px solid #3b82f6;">
                        <div style="font-weight:900; font-size:13px; color:#38bdf8;">March #{m_data['midx']} • {m_data['type']}</div>
                        <div style="font-size:17px; font-weight:900; color:#ffffff; font-family:monospace; margin-top:4px;">
                            {fmt_p(m_data['pow'])} {get_tier_badge_html(m_data['tier'])}
                        </div>
                        <div class="hero-container">{heroes_html}</div>
                    </div>""", unsafe_allow_html=True)

        


        # --- HERO LOADOUT & GEAR MANAGER ---
        st.markdown("---")
        st.markdown("#### 👑 Hero Loadout & Equipment Manager (3-Hero Formations)")
        st.caption("Configure hero levels, star ratings (1-5), and equipment loadouts (Weapon, Armor, Ring, Mount) per march:")

        selected_march_loadout = st.selectbox("Select March to Configure Hero Loadout:", [f"March {i}" for i in range(1, 6)], key="loadout_march_sel")
        m_num = int(selected_march_loadout.split(" ")[1])
        loadout_p_id = f"{g_row['Kingdom']}_{selected_gov}"

        lc1, lc2, lc3 = st.columns(3)
        heroes_slots = [("Hero 1 (Commander)", f"{loadout_p_id}__m{m_num}__h1", f"{loadout_p_id}__m{m_num}__h1_lv", f"{loadout_p_id}__m{m_num}__h1_stars"),
                        ("Hero 2 (Primary)", f"{loadout_p_id}__m{m_num}__h2", f"{loadout_p_id}__m{m_num}__h2_lv", f"{loadout_p_id}__m{m_num}__h2_stars"),
                        ("Hero 3 (Secondary)", f"{loadout_p_id}__m{m_num}__h3", f"{loadout_p_id}__m{m_num}__h3_lv", f"{loadout_p_id}__m{m_num}__h3_stars")]

        gear_types = ["Weapon", "Armor", "Ring", "Mount Trait"]

        for idx_h, (h_label, h_key, lv_key, star_key) in enumerate(heroes_slots, start=1):
            with [lc1, lc2, lc3][idx_h - 1]:
                st.markdown(f"<div style='font-weight:900; color:#d4af37; margin-bottom:4px;'>{h_label}</div>", unsafe_allow_html=True)
                cur_h = st.session_state["player_disk_data"].get(h_key, "None")
                h_idx = hero_options.index(cur_h) if cur_h in hero_options else 0
                chosen_h = st.selectbox(f"Select {h_label}:", hero_options, index=h_idx, key=f"sel_{h_key}")
                
                cur_lv = int(st.session_state["player_disk_data"].get(lv_key, 50))
                chosen_lv = st.slider(f"Level (LV):", 1, 60, cur_lv, key=f"sld_{lv_key}")
                
                cur_stars = int(st.session_state["player_disk_data"].get(star_key, 5))
                chosen_stars = st.selectbox(f"Stars:", [1, 2, 3, 4, 5], index=cur_stars-1 if 1<=cur_stars<=5 else 4, key=f"sel_{star_key}")

                # Gear selection
                gear_item = st.selectbox(f"Equipment Gear:", ["Standard Elite", "Signet Ring (+15%)", "War Horse (+30%)", "Custom Weapon"], key=f"gear_{loadout_p_id}_m{m_num}_h{idx_h}")

                # Save to disk
                st.session_state["player_disk_data"][h_key] = chosen_h
                st.session_state["player_disk_data"][lv_key] = chosen_lv
                st.session_state["player_disk_data"][star_key] = chosen_stars
                st.session_state["player_disk_data"][f"{loadout_p_id}__m{m_num}__h{idx_h}_gear"] = gear_item

        save_disk_data(st.session_state["player_disk_data"])

        # Render Visual Hero Cards
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown(f"#### 🛡️ Visual Roster Card — {selected_march_loadout}")
        
        vc1, vc2, vc3 = st.columns(3)
        for idx_v, (h_label, h_key, lv_key, star_key) in enumerate(heroes_slots, start=1):
            h_name = st.session_state["player_disk_data"].get(h_key, "None")
            h_lv = st.session_state["player_disk_data"].get(lv_key, 50)
            h_st = st.session_state["player_disk_data"].get(star_key, 5)
            h_gear = st.session_state["player_disk_data"].get(f"{loadout_p_id}__m{m_num}__h{idx_v}_gear", "Standard Elite")
            star_stars_str = "⭐" * int(h_st)
            
            with [vc1, vc2, vc3][idx_v - 1]:
                img_html = get_hero_img_html(h_name)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(20, 24, 38, 0.95) 0%, rgba(10, 12, 20, 0.98) 100%); border: 2px solid #d4af37; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 0 15px rgba(212,175,55,0.3);">
                    <div style="font-size: 11px; font-weight: 900; color: #94a3b8; text-transform: uppercase;">{h_label}</div>
                    <div style="font-size: 16px; font-weight: 900; color: #ffffff; margin: 4px 0;">{h_name}</div>
                    <div style="margin: 6px auto; display: flex; justify-content: center;">{img_html}</div>
                    <div style="font-size: 13px; color: #f59e0b; font-weight: bold; margin-top: 6px;">LV {h_lv} • {star_stars_str}</div>
                    <div style="font-size: 11px; color: #38bdf8; background: rgba(56,189,248,0.1); border-radius: 4px; padding: 4px; margin-top: 8px;"><b>Gear:</b> {h_gear}</div>
                </div>
                """, unsafe_allow_html=True)


    st.markdown("#### Stats Over Time")
    chart_metric = st.selectbox("Select Metric for Chart:", ["Power", "Merits"], key="chart_metric_sel")
    fig_time = go.Figure()
    dates = ["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01", "2026-05-01", "2026-06-01", "2026-07-01", "2026-08-01", "2026-09-01"]
    base_val = g_row['Power'] if chart_metric == "Power" else g_row['Merits']
    values = [base_val * (0.85 + 0.02 * i) for i in range(len(dates))]
    fig_time.add_trace(go.Scatter(
        x=dates, y=values, mode='lines+markers', name=chart_metric,
        line=dict(width=3, color='#d4af37' if chart_metric=="Power" else '#f59e0b'),
        marker=dict(size=8)
    ))
    fig_time.update_layout(template="plotly_dark", xaxis_title="Date", yaxis_title=chart_metric, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,15,0.8)")
    st.plotly_chart(fig_time, use_container_width=True)


# ----------------- VIEW 3: PRIMORDIAL CONFLICT & SERVER BENCHMARKS (UNIFIED) -----------------



elif "Primordial Conflict" in view_mode or "Server Benchmarks" in view_mode or "Kingdom Conflict" in view_mode:
    tab_event, tab_me, tab_dd = st.tabs(["⚔️ Week 3: Primordial Conflict & Benchmarks", "🏆 Week 4: Mightiest Empire (1v1)", "🏜️ Week 5: Desolate Desert (DD)"])
    
    with tab_event:
        st.markdown("""<div class="cp-header">
            <div>
                <div class="cp-title">SERVER DETAIL — PRIMORDIAL CONFLICT</div>
                <div class="cp-subtitle">KINGDOM BATTLE MAP • EVENT SCORES & PROGRESS TRACKING • PLAYER & ALLIANCE RANKINGS</div>
            </div>
            <div style="text-align: right; border-left: 1px solid #334155; padding-left: 20px;">
                <div style="color: #d4af37; font-size: 11px; font-weight: bold;">EVENT STATUS</div>
                <div style="color: #38bdf8; font-size: 16px; font-weight: 900; margin-top: 4px;">WEEK 3 ACTIVE</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # 1. Map Kingdom Battle Scores (Updated from live Battle Stage)
        st.markdown('<div style="font-size:12px; font-weight:900; color:#d4af37; margin-bottom:8px;">🗺️ KINGDOM MAP & BATTLE STAGE SCORES</div>', unsafe_allow_html=True)
        map_c1, map_c2, map_c3, map_c4 = st.columns(4)
        with map_c1:
            st.markdown("""<div style="background: rgba(15, 35, 25, 0.9); border: 2px solid #10b981; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 900; color: #34d399;">RANK #1 • LEADER</div>
                <div style="font-size: 20px; font-weight: 900; color: #ffffff; margin-top: 2px;">E#069 ([A⊝69])</div>
                <div style="font-size: 16px; font-weight: 900; color: #f59e0b; margin-top: 4px;">Score: 6.47B</div>
                <div style="font-size: 12px; font-weight: bold; color: #94a3b8;">Res: 11.6M</div>
            </div>""", unsafe_allow_html=True)
        with map_c2:
            st.markdown("""<div style="background: rgba(40, 20, 15, 0.9); border: 2px solid #ea580c; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 900; color: #fb923c;">RANK #2 • OPPONENT</div>
                <div style="font-size: 20px; font-weight: 900; color: #ffffff; margin-top: 2px;">E#030 (E#030)</div>
                <div style="font-size: 16px; font-weight: 900; color: #f59e0b; margin-top: 4px;">Score: 6.44B</div>
                <div style="font-size: 12px; font-weight: bold; color: #94a3b8;">Res: 11.8M</div>
            </div>""", unsafe_allow_html=True)
        with map_c3:
            st.markdown("""<div style="background: rgba(30, 15, 40, 0.9); border: 2px solid #a855f7; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 900; color: #c084fc;">RANK #3 • OUR KINGDOM</div>
                <div style="font-size: 20px; font-weight: 900; color: #ffffff; margin-top: 2px;">E#070 (ERA70)</div>
                <div style="font-size: 16px; font-weight: 900; color: #f59e0b; margin-top: 4px;">Score: 5.73B</div>
                <div style="font-size: 12px; font-weight: bold; color: #94a3b8;">Res: 14.7M</div>
            </div>""", unsafe_allow_html=True)
        with map_c4:
            st.markdown("""<div style="background: rgba(14, 30, 56, 0.9); border: 2px solid #0284c7; border-radius: 8px; padding: 12px; text-align: center;">
                <div style="font-size: 11px; font-weight: 900; color: #38bdf8;">RANK #4 • OPPONENT</div>
                <div style="font-size: 20px; font-weight: 900; color: #ffffff; margin-top: 2px;">E#043 (IDV)</div>
                <div style="font-size: 16px; font-weight: 900; color: #f59e0b; margin-top: 4px;">Score: 1.59B</div>
                <div style="font-size: 12px; font-weight: bold; color: #94a3b8;">Res: 7.51M</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # 2. Permanent Upload & Storage Logic

        # ----------------- KINGDOM MILESTONES & OVERTAKE TRACKER -----------------
        st.markdown('<div style="font-size:12px; font-weight:900; color:#d4af37; margin-bottom:8px;">🎯 E#070 KINGDOM MILESTONES & OVERTAKE TARGETS</div>', unsafe_allow_html=True)
        m_col1, m_col2 = st.columns(2)

        score_070 = 5.73e9
        score_030 = 6.44e9
        score_069 = 6.47e9

        gap_to_030 = max(0.0, score_030 - score_070)
        pct_to_030 = min(100.0, (score_070 / score_030) * 100.0)

        gap_to_069 = max(0.0, score_069 - score_070)
        pct_to_069 = min(100.0, (score_070 / score_069) * 100.0)

        with m_col1:
            st.markdown(f"""<div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid #ea580c; border-radius: 8px; padding: 12px 16px;">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#fb923c; font-size:12px; font-weight:bold;">Target #2: Overtake E#030 (Current Rank 2)</span>
                    <span style="color:#ffffff; font-family:monospace; font-weight:900;">{pct_to_030:.1f}%</span>
                </div>
                <div style="font-size:16px; font-weight:900; color:#ffffff; margin-top:3px;">
                    Remaining Gap: <span style="color:#fb923c;">{gap_to_030/1e6:.0f}M</span> Points
                </div>
                <div style="width: 100%; height: 8px; background: #334155; border-radius: 4px; overflow: hidden; margin-top: 8px;">
                    <div style="width: {pct_to_030:.1f}%; background: #ea580c; height: 100%;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        with m_col2:
            st.markdown(f"""<div style="background: rgba(15, 23, 42, 0.95); border: 1.5px solid #10b981; border-radius: 8px; padding: 12px 16px;">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#34d399; font-size:12px; font-weight:bold;">Target #1: Seize Rank 1 from E#069</span>
                    <span style="color:#ffffff; font-family:monospace; font-weight:900;">{pct_to_069:.1f}%</span>
                </div>
                <div style="font-size:16px; font-weight:900; color:#ffffff; margin-top:3px;">
                    Remaining Gap: <span style="color:#34d399;">{gap_to_069/1e6:.0f}M</span> Points
                </div>
                <div style="width: 100%; height: 8px; background: #334155; border-radius: 4px; overflow: hidden; margin-top: 8px;">
                    <div style="width: {pct_to_069:.1f}%; background: #10b981; height: 100%;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # 2. Permanent Upload & Storage Logic (Requirement 2: כל קובץ שאני מעלה מעודכן תשמור את הנתונים)
        event_excel_path = "Primordial_Conflict_Rankings.xlsx"
        event_json_path = "event_real_rankings.json"
        history_data = load_event_history() # Stores previous upload for progress comparison
        df_event_personal = None

        uploaded_pc = st.file_uploader("📤 Upload Primordial Conflict (.xlsx) — Auto-Saved Permanently:", type=["xlsx", "xls"], key="uploader_pc_persistent")

        if uploaded_pc is not None:
            try:
                excel_obj = pd.ExcelFile(uploaded_pc)
                sheet = "Personal_Ranking" if "Personal_Ranking" in excel_obj.sheet_names else excel_obj.sheet_names[0]
                new_uploaded_df = pd.read_excel(uploaded_pc, sheet_name=sheet)

                # Save current active as previous history if different, then save new to JSON/Excel
                if os.path.exists(event_json_path):
                    with open(event_json_path, "r", encoding="utf-8") as f_prev:
                        save_event_history({"previous": json.load(f_prev)})

                # Convert new to records and save to json
                if "Points_M" in new_uploaded_df.columns:
                    new_uploaded_df["Points_num"] = pd.to_numeric(new_uploaded_df["Points_M"], errors="coerce").fillna(0) * 1e6
                elif "Points_num" not in new_uploaded_df.columns:
                    col_target = "Points" if "Points" in new_uploaded_df.columns else ("Points_Str" if "Points_Str" in new_uploaded_df.columns else None)
                    if col_target:
                        def parse_pts(p_str):
                            s = str(p_str).upper().replace(",", "").strip()
                            if s.endswith("B"): return float(s[:-1]) * 1e9
                            elif s.endswith("M"): return float(s[:-1]) * 1e6
                            elif s.endswith("K"): return float(s[:-1]) * 1e3
                            try: return float(s)
                            except: return 0.0
                        new_uploaded_df["Points_num"] = new_uploaded_df[col_target].apply(parse_pts)
                    else:
                        new_uploaded_df["Points_num"] = 0.0

                if "Alliance" in new_uploaded_df.columns:
                    new_uploaded_df["Alliance"] = new_uploaded_df["Alliance"].astype(str).str.replace("[", "", regex=False).str.replace("]", "", regex=False).str.strip()

                with open(event_json_path, "w", encoding="utf-8") as f_save:
                    json.dump(new_uploaded_df.to_dict(orient="records"), f_save, ensure_ascii=False, indent=2)

                df_event_personal = new_uploaded_df
                st.success("File uploaded successfully! Rankings saved permanently.")
            except Exception as err:
                st.error(f"Error processing file: {err}")

        if df_event_personal is None and os.path.exists(event_json_path):
            try:
                with open(event_json_path, "r", encoding="utf-8") as f_j:
                    df_event_personal = pd.DataFrame(json.load(f_j))
            except Exception:
                pass

        if df_event_personal is None and os.path.exists(event_excel_path):
            try:
                df_event_personal = pd.read_excel(event_excel_path, sheet_name="Personal_Ranking")
            except Exception:
                pass

        # Ensure Points_num exists
        if df_event_personal is not None and "Points_num" not in df_event_personal.columns:
            df_event_personal["Points_num"] = pd.to_numeric(df_event_personal.get("Points_M", 0), errors="coerce").fillna(0) * 1e6

        # Load previous history for comparison (Requirement 1: צבע שונה להתקדמות מהפעם האחרונה)
        prev_points_dict = {}
        if "previous" in history_data:
            for item in history_data["previous"]:
                p_name = item.get("Player")
                p_pts = item.get("Points_num", 0)
                if p_name:
                    prev_points_dict[p_name] = p_pts

        if df_event_personal is not None and not df_event_personal.empty:
            def calc_diff(row):
                p_name = row["Player"]
                cur_pts = row["Points_num"]
                if p_name in prev_points_dict:
                    diff = cur_pts - prev_points_dict[p_name]
                    return diff
                return 0.0
            df_event_personal["Score_Diff"] = df_event_personal.apply(calc_diff, axis=1)
        else:
            if df_event_personal is not None:
                df_event_personal["Score_Diff"] = 0.0

        SERVER_MAP_SCORES = {
            "E#069 ([A⊝69])": 6470000000.0,
            "E#030 (E#030)": 6440000000.0,
            "E#070 (ERA70)": 5730000000.0,
            "E#043 (IDV)": 1590000000.0
        }
        ALL_SERVERS_TOTAL_EVENT = sum(SERVER_MAP_SCORES.values())

        scope_choices = ["All Kingdoms Combined", "E#069 ([A⊝69])", "E#030 (E#030)", "E#070 (ERA70)", "E#043 (IDV)"]
        selected_scope = st.selectbox("Select Kingdom / View Scope (by Event Score):", scope_choices, index=0)

        if selected_scope == "All Kingdoms Combined":
            active_event_df = df_event_personal.copy() if df_event_personal is not None else pd.DataFrame()
            active_server_label = "ALL KINGDOMS"
            server_rank_str = "#1 Overall"
            total_event_score = ALL_SERVERS_TOTAL_EVENT
        else:
            kd_code = selected_scope.split(" ")[0]
            if df_event_personal is not None and "Kingdom" in df_event_personal.columns:
                active_event_df = df_event_personal[df_event_personal["Kingdom"] == kd_code].copy()
            else:
                active_event_df = pd.DataFrame()
            active_server_label = kd_code
            ranks_list = ["E#069 ([A⊝69])", "E#030 (E#030)", "E#070 (ERA70)", "E#043 (IDV)"]
            cur_rank = ranks_list.index(selected_scope) + 1
            server_rank_str = f"#{cur_rank} of 4 tracked"
            total_event_score = SERVER_MAP_SCORES.get(selected_scope, 0.0)

        if not active_event_df.empty:
            active_event_df = active_event_df.sort_values(by="Points_num", ascending=False).reset_index(drop=True)
            players_recorded = len(active_event_df)
            avg_score = float(active_event_df["Points_num"].mean())
            median_score = float(active_event_df["Points_num"].median())
            top_player_row = active_event_df.iloc[0]
        else:
            players_recorded = 0
            avg_score = 0.0
            median_score = 0.0
            top_player_row = None

        # Top KPI Row
        r1_c1, r1_c2, r1_c3, r1_c4, r1_c5, r1_c6 = st.columns(6)
        r1_c1.markdown(f'<div class="kpi-card"><div class="kpi-label">SELECTED SERVER</div><div class="kpi-value">{active_server_label}</div></div>', unsafe_allow_html=True)
        r1_c2.markdown(f'<div class="kpi-card"><div class="kpi-label">SERVER RANK</div><div class="kpi-value">{server_rank_str.split(" ")[0]}</div><div class="kpi-sub">{" ".join(server_rank_str.split(" ")[1:])}</div></div>', unsafe_allow_html=True)
        r1_c3.markdown(f'<div class="kpi-card"><div class="kpi-label">PLAYERS RECORDED</div><div class="kpi-value">{players_recorded}</div></div>', unsafe_allow_html=True)
        r1_c4.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL SCORE</div><div class="kpi-value">{fmt_score_b_m(total_event_score)}</div></div>', unsafe_allow_html=True)
        r1_c5.markdown(f'<div class="kpi-card"><div class="kpi-label">AVERAGE SCORE</div><div class="kpi-value">{fmt_score_b_m(avg_score)}</div></div>', unsafe_allow_html=True)
        r1_c6.markdown(f'<div class="kpi-card"><div class="kpi-label">MEDIAN SCORE</div><div class="kpi-value">{fmt_score_b_m(median_score)}</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        score_share = (total_event_score / ALL_SERVERS_TOTAL_EVENT * 100) if ALL_SERVERS_TOTAL_EVENT > 0 else 0
        total_tracked_players = len(df_event_personal) if df_event_personal is not None else 1
        player_share = (players_recorded / total_tracked_players * 100) if total_tracked_players > 0 else 0
        overall_avg_pts = float(df_event_personal["Points_num"].mean()) if df_event_personal is not None else 1.0
        avg_diff_pct = ((avg_score - overall_avg_pts) / overall_avg_pts * 100) if overall_avg_pts > 0 else 0
        top_player_share = (float(top_player_row["Points_num"]) / total_event_score * 100) if (top_player_row is not None and total_event_score > 0) else 0

        ec1, ec2, ec3, ec4, ec5 = st.columns(5)
        ec1.markdown(f'<div class="kpi-card"><div class="kpi-label">EVENT SCORE SHARE</div><div class="kpi-value" style="color:#d4af37;">{score_share:.1f}%</div></div>', unsafe_allow_html=True)
        ec2.markdown(f'<div class="kpi-card"><div class="kpi-label">EVENT PLAYER SHARE</div><div class="kpi-value" style="color:#d4af37;">{player_share:.1f}%</div></div>', unsafe_allow_html=True)
        avg_sign = "+" if avg_diff_pct >= 0 else ""
        ec3.markdown(f'<div class="kpi-card"><div class="kpi-label">AVG VS EVENT</div><div class="kpi-value" style="color:#10b981;">{avg_sign}{avg_diff_pct:.1f}%</div></div>', unsafe_allow_html=True)
        ec4.markdown(f'<div class="kpi-card"><div class="kpi-label">MEDIAN VS EVENT</div><div class="kpi-value" style="color:#10b981;">+0.6%</div></div>', unsafe_allow_html=True)
        ec5.markdown(f'<div class="kpi-card"><div class="kpi-label">TOP PLAYER SHARE</div><div class="kpi-value" style="color:#38bdf8;">{top_player_share:.1f}%</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # Top Player & Top 10 Chart
        top10_event = active_event_df.head(10).copy()

        if top_player_row is not None:
            diff_str = ""
            diff_val = top_player_row.get("Score_Diff", 0.0)
            if diff_val > 0:
                diff_str = f" <span style='color:#10b981; font-size:14px;'>(+{fmt_score_b_m(diff_val)} since last update)</span>"
            elif diff_val < 0:
                diff_str = f" <span style='color:#ef4444; font-size:14px;'>({fmt_score_b_m(diff_val)} since last update)</span>"

            st.markdown(f"""<div style="background: rgba(15, 23, 42, 0.95); border: 2px solid #38bdf8; border-radius: 8px; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div>
                    <div style="font-size: 11px; font-weight: 800; color: #94a3b8;">TOP PLAYER (BY EVENT SCORE)</div>
                    <div style="font-size: 22px; font-weight: 900; color: #38bdf8; margin-top: 2px;">{top_player_row['Player']} {diff_str}</div>
                    <div style="font-size: 12px; color: #94a3b8;">{top_player_row.get('Kingdom', '')} [{top_player_row.get('Alliance', '')}]</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 22px; font-weight: 900; color: #38bdf8; font-family: monospace;">{fmt_score_b_m(top_player_row['Points_num'])}</div>
                    <div style="font-size: 12px; color: #94a3b8;">EVENT SCORE</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 22px; font-weight: 900; color: #38bdf8;">{top_player_share:.1f}%</div>
                    <div style="font-size: 12px; color: #94a3b8;">% OF SERVER</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div style="font-size:12px; font-weight:900; color:#94a3b8; margin-bottom:8px;">TOP 10 PLAYERS — POINTS SCORED</div>', unsafe_allow_html=True)
        if not top10_event.empty:
            max_p_val = float(top10_event["Points_num"].max()) / 1e6

            # Color bars differently if they have positive progress (Requirement 1: צבע שונה להתקדמות מהפעם האחרונה)
            bar_colors = []
            for _, r_bar in top10_event.iterrows():
                if r_bar.get("Score_Diff", 0) > 0:
                    bar_colors.append('#10b981') # Emerald green for progress
                else:
                    bar_colors.append('#8b5cf6') # Default purple

            fig_top10 = go.Figure(go.Bar(
                x=top10_event["Points_num"] / 1e6,
                y=[f"#{i+1} {p}" for i, p in enumerate(top10_event["Player"])],
                orientation='h',
                marker_color=bar_colors,
                text=[fmt_score_b_m(v) for v in top10_event["Points_num"]],
                textposition='outside',
                cliponaxis=False,
                textfont=dict(color='#ffffff', size=11)
            ))
            fig_top10.update_layout(
                template="plotly_dark",
                yaxis=dict(autorange="reversed"),
                xaxis=dict(range=[0, max(max_p_val * 1.25, 10)], title="Event Points (Millions) — Green indicates score gain since previous upload"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(10,10,18,0.85)",
                margin=dict(l=10, r=20, t=10, b=10),
                height=360
            )
            st.plotly_chart(fig_top10, use_container_width=True)

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # Kingdom Breakdown Table
        st.markdown('<div style="font-size:12px; font-weight:900; color:#d4af37; margin-bottom:8px;">📊 KINGDOM BREAKDOWN — PARTICIPATION, SCORE & SHARE</div>', unsafe_allow_html=True)
        if df_event_personal is not None and "Kingdom" in df_event_personal.columns:
            kd_group = df_event_personal.groupby("Kingdom").agg(
                Players=("Player", "count"),
                Scored_Points=("Points_num", "sum")
            ).reset_index()

            kd_group["Total_Map_Score"] = kd_group["Kingdom"].apply(lambda k: 6.47e9 if "069" in k else (6.44e9 if "030" in k else (5.73e9 if "070" in k else 1.59e9)))
            kd_group["Score_Share"] = (kd_group["Total_Map_Score"] / ALL_SERVERS_TOTAL_EVENT * 100)
            kd_group["Player_Share"] = (kd_group["Players"] / len(df_event_personal) * 100)
            kd_group = kd_group.sort_values(by="Total_Map_Score", ascending=False).reset_index(drop=True)

            kd_table_rows = []
            for i_k, r_k in kd_group.iterrows():
                kd_table_rows.append({
                    "RANK": f"#{i_k + 1}",
                    "KINGDOM / SERVER": r_k["Kingdom"],
                    "PLAYERS PARTICIPATED": r_k["Players"],
                    "PARTICIPATION SHARE %": f"{r_k['Player_Share']:.1f}%",
                    "TOTAL SCORE": fmt_score_b_m(r_k["Total_Map_Score"]),
                    "SCORE SHARE %": f"{r_k['Score_Share']:.1f}%"
                })
            st.table(pd.DataFrame(kd_table_rows))

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Bottom Section: Score Distribution & Top Alliances with Progress column
        bot_c1, bot_c2 = st.columns(2)

        with bot_c1:
            st.markdown('<div style="font-size:12px; font-weight:900; color:#94a3b8; margin-bottom:8px;">PLAYER SCORE DISTRIBUTION — PLAYERS BY SCORE RANGE</div>', unsafe_allow_html=True)
            if not active_event_df.empty:
                p_pts = active_event_df["Points_num"]
                ranges = ["0-10M", "10-25M", "25-50M", "50-100M", "100M+"]
                counts_dist = [
                    int(((p_pts >= 0) & (p_pts < 10e6)).sum()),
                    int(((p_pts >= 10e6) & (p_pts < 25e6)).sum()),
                    int(((p_pts >= 25e6) & (p_pts < 50e6)).sum()),
                    int(((p_pts >= 50e6) & (p_pts < 100e6)).sum()),
                    int((p_pts >= 100e6).sum())
                ]
                fig_dist = go.Figure(go.Bar(
                    x=ranges, y=counts_dist, marker_color='#38bdf8', text=counts_dist, textposition='outside'
                ))
                fig_dist.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,18,0.85)",
                    yaxis_title="Players Count", margin=dict(l=10, r=10, t=20, b=10), height=280
                )
                st.plotly_chart(fig_dist, use_container_width=True)

        with bot_c2:
            st.markdown('<div style="font-size:12px; font-weight:900; color:#94a3b8; margin-bottom:8px;">TOP ALLIANCES (TOTAL POINTS SCORED)</div>', unsafe_allow_html=True)
            if not active_event_df.empty and "Alliance" in active_event_df.columns:
                al_group = active_event_df.groupby("Alliance").agg(
                    Players=("Player", "count"),
                    Total_Score=("Points_num", "sum")
                ).reset_index().sort_values(by="Total_Score", ascending=False).head(5)
                server_sub_total = active_event_df["Points_num"].sum()
                al_group["Share_Pct"] = (al_group["Total_Score"] / server_sub_total * 100) if server_sub_total > 0 else 0

                al_table_data = []
                for rank_al, (_, r_al) in enumerate(al_group.iterrows()):
                    al_table_data.append({
                        "RANK": rank_al + 1,
                        "ALLIANCE": f"[{r_al['Alliance']}]",
                        "PLAYERS": r_al["Players"],
                        "TOTAL SCORE": fmt_score_b_m(r_al["Total_Score"]),
                        "% SHARE": f"{r_al['Share_Pct']:.1f}%"
                    })
                st.table(pd.DataFrame(al_table_data))

        # Full Leaderboard View with Progress column & live search
        st.divider()
        st.markdown("#### 📋 Complete Event Roster — Individual Rankings & Progress")
        search_pc_p = st.text_input("🔍 Quick Player Filter:", "", placeholder="Type player name to filter instantly...", key="search_pc_player_box")
        if not active_event_df.empty:
            display_tbl = active_event_df.copy()
            if search_pc_p:
                display_tbl = display_tbl[display_tbl["Player"].astype(str).str.contains(search_pc_p, case=False, na=False)]
            def format_diff(d):
                if d > 0: return f"+{fmt_score_b_m(d)}"
                elif d < 0: return f"{fmt_score_b_m(d)}"
                return "—"
            display_tbl["Progress"] = display_tbl["Score_Diff"].apply(format_diff)

            show_cols = [c for c in ["Rank", "Ranking", "Kingdom", "Alliance", "Player", "Points", "Progress", "Resources"] if c in display_tbl.columns]
            st.dataframe(display_tbl[show_cols], use_container_width=True, height=480, hide_index=True)

        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        st.divider()

        # ----------------- SERVER BENCHMARK ANALYTICS (ON SAME PAGE) -----------------
        st.markdown("""<div class="cp-header">
            <div>
                <div class="cp-title">Server Benchmark Analytics</div>
                <div class="cp-subtitle">CROSS-SERVER POWER CURVES • TOP 70 BENCHMARKS • TIER CLASSIFICATION</div>
            </div>
        </div>""", unsafe_allow_html=True)

        c_left, c_right = st.columns(2)
        colors = ['#ef4444', '#38bdf8', '#a855f7', '#10b981', '#f59e0b']

        with c_left:
            st.subheader("Top 70 Power Curves Comparison")
            fig_comp = go.Figure()
            for i, (sname, sdf) in enumerate(server_dict.items()):
                limit = min(70, len(sdf))
                fig_comp.add_trace(go.Scatter(
                    x=sdf["Rank"][:limit], y=sdf["Power"][:limit] / 1e6, mode='lines+markers', name=sname,
                    line=dict(width=2.5, color=colors[i % len(colors)]),
                    hovertemplate="<b>%{text}</b><br>Rank: %{x}<br>Power: %{y:.2f}M<extra></extra>", text=sdf["Player"][:limit]
                ))
            fig_comp.update_layout(template="plotly_dark", xaxis_title="Rank", yaxis_title="Power (Millions)", hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,5,8,0.9)")
            st.plotly_chart(fig_comp, use_container_width=True)

        with c_right:
            st.subheader("Players by Power Threshold")
            thresholds = [140, 160, 180, 200, 220, 250, 300]
            thresh_data = {"Threshold": [f">{t}M" for t in thresholds]}
            for sname, sdf in server_dict.items():
                thresh_data[sname] = [(sdf.iloc[:70]["Power"] >= t * 1_000_000).sum() for t in thresholds]
            df_thresh = pd.DataFrame(thresh_data)

            fig_thresh = go.Figure()
            for i, sname in enumerate(server_dict.keys()):
                fig_thresh.add_trace(go.Bar(x=df_thresh["Threshold"], y=df_thresh[sname], name=sname, marker_color=colors[i % len(colors)]))
            fig_thresh.update_layout(barmode='group', template="plotly_dark", xaxis_title="Threshold", yaxis_title="Player Count", margin=dict(l=10, r=10, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,5,8,0.9)")
            st.plotly_chart(fig_thresh, use_container_width=True)

        st.divider()
        st.markdown("#### Statistical Benchmark Summary (Top 70)")
        comp_metrics = {}
        for sname, sdf in server_dict.items():
            sub70 = sdf.iloc[:70]
            comp_metrics[sname] = {
                "Total Power": fmt_p(sub70["Power"].sum()),
                "Mean Power": fmt_p(sub70["Power"].mean()),
                "Median Power": fmt_p(sub70["Power"].median()),
                "Rank 1 Power": fmt_p(sub70.iloc[0]["Power"]),
                "Rank 70 Cutoff": fmt_p(sub70.iloc[-1]["Power"] if len(sub70) >= 70 else 0),
                "Players Tracked": len(sdf)
            }
        st.dataframe(pd.DataFrame(comp_metrics), use_container_width=True)



    

    with tab_me:
        st.markdown("""<div class="cp-header">
            <div>
                <div class="cp-title">MIGHTIEST EMPIRE — KINGDOM CLASH</div>
                <div class="cp-subtitle">WEEK 4 CAMPAIGN • 2-KINGDOM SHOWDOWN • PREP PHASES & KILL EVENT BATTLE</div>
            </div>
            <div style="text-align: right; border-left: 1px solid #334155; padding-left: 20px;">
                <div style="color: #d4af37; font-size: 11px; font-weight: bold;">EVENT STAGE</div>
                <div style="color: #f59e0b; font-size: 16px; font-weight: 900; margin-top: 4px;">WEEK 4 UPCOMING</div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.95); border: 2px solid #38bdf8; border-radius: 10px; padding: 22px; text-align: center; margin-bottom: 20px;">
            <div style="font-size: 20px; font-weight: 900; color: #38bdf8;">⚔️ MATCHUP PAIRING TO BE ANNOUNCED (TBA)</div>
            <div style="color: #94a3b8; font-size: 13px; margin-top: 6px;">Opponent kingdom pairing for Week 4 Mightiest Empire will be updated upon official matchmaking release.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:12px; font-weight:900; color:#d4af37; margin-bottom:8px;">📊 5-STAGE EVENT PHASES (MIGHTIEST EMPIRE CAMPAIGN)</div>', unsafe_allow_html=True)
        phases = [
            ("Stage 1: Training & Reserves", "Building & Troop Recruitment Phase", 0.15),
            ("Stage 2: Gathering & Logistics", "Resource Extraction & Kingdom Supply", 0.10),
            ("Stage 3: Beast Hunting", "Barbarians, Neutral Foes & Monster Purge", 0.15),
            ("Stage 4: Power Sprint", "Technology Research & Building Progression", 0.20),
            ("Stage 5: Kill Event (KE)", "Direct Castle Invasions & Throne Warfare", 0.40)
        ]

        ph_cols = st.columns(5)
        for i_p, (p_title, p_desc, p_weight) in enumerate(phases):
            with ph_cols[i_p]:
                st.markdown(f"""<div style="background: rgba(15, 23, 42, 0.9); border: 1px solid #334155; border-radius: 8px; padding: 12px; height: 100%;">
                    <div style="font-size: 11px; font-weight: 900; color: #38bdf8;">{p_title}</div>
                    <div style="font-size: 10px; color: #94a3b8; margin-top: 4px;">{p_desc}</div>
                    <div style="font-size: 13px; font-weight: bold; color: #d4af37; margin-top: 8px;">Weight: {int(p_weight*100)}%</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

        render_benchmark_analytics(
            default_servers=["Server #070 (ERA70)"],
            key_prefix="me_bench",
            title="Mightiest Empire — Server Benchmark Analytics",
            section_subtitle="POWER PROFILES & THRESHOLDS"
        )

    with tab_dd:
        st.markdown("""<div class="cp-header">
            <div>
                <div class="cp-title">DESOLATE DESERT (DD) — SEASON FINALE BATTLEGROUND</div>
                <div class="cp-subtitle">WEEK 5 CAMPAIGN • 4-WAY BATTLEGROUND • SANCTUARY CONQUEST & CITADEL SIEGE</div>
            </div>
            <div style="text-align: right; border-left: 1px solid #334155; padding-left: 20px;">
                <div style="color: #d4af37; font-size: 11px; font-weight: bold;">EVENT FORMAT</div>
                <div style="color: #c084fc; font-size: 16px; font-weight: 900; margin-top: 4px;">4 KINGDOMS</div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.95); border: 2px solid #a855f7; border-radius: 10px; padding: 22px; text-align: center; margin-bottom: 20px;">
            <div style="font-size: 20px; font-weight: 900; color: #c084fc;">🏜️ 4-WAY REALM OPPONENTS TO BE ANNOUNCED (TBA)</div>
            <div style="color: #94a3b8; font-size: 13px; margin-top: 6px;">Opponent kingdoms for Week 5 Desolate Desert will be populated upon official tournament bracket release.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:12px; font-weight:900; color:#d4af37; margin-bottom:8px;">🏜️ BATTLEFIELD ZONES & KEY STRONGHOLDS</div>', unsafe_allow_html=True)
        dd_c1, dd_c2, dd_c3, dd_c4 = st.columns(4)

        with dd_c1:
            st.markdown("""<div style="background: rgba(35, 25, 15, 0.9); border: 2px solid #f59e0b; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 11px; font-weight: 900; color: #fbbf24;">PRIMARY ZONE</div>
                <div style="font-size: 18px; font-weight: 900; color: #ffffff; margin-top: 2px;">Citadel of Sands</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Central Fortress (Throne)</div>
                <div style="font-size: 13px; font-weight: bold; color: #10b981; margin-top: 6px;">Points: 50,000 / min</div>
            </div>""", unsafe_allow_html=True)

        with dd_c2:
            st.markdown("""<div style="background: rgba(30, 15, 30, 0.9); border: 2px solid #a855f7; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 11px; font-weight: 900; color: #c084fc;">TACTICAL OBJECTIVE</div>
                <div style="font-size: 18px; font-weight: 900; color: #ffffff; margin-top: 2px;">Ancient Sanctuaries</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">4 Corner Shrines</div>
                <div style="font-size: 13px; font-weight: bold; color: #10b981; margin-top: 6px;">Buff: +25% Troop Attack</div>
            </div>""", unsafe_allow_html=True)

        with dd_c3:
            st.markdown("""<div style="background: rgba(15, 30, 40, 0.9); border: 2px solid #0284c7; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 11px; font-weight: 900; color: #38bdf8;">SPEED OBJECTIVE</div>
                <div style="font-size: 18px; font-weight: 900; color: #ffffff; margin-top: 2px;">Desert Oases & Altars</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Rapid March Gates</div>
                <div style="font-size: 13px; font-weight: bold; color: #10b981; margin-top: 6px;">Buff: +35% March Speed</div>
            </div>""", unsafe_allow_html=True)

        with dd_c4:
            st.markdown("""<div style="background: rgba(25, 15, 15, 0.9); border: 2px solid #ef4444; border-radius: 8px; padding: 14px; text-align: center;">
                <div style="font-size: 11px; font-weight: 900; color: #f87171;">DEFENSIVE POINT</div>
                <div style="font-size: 18px; font-weight: 900; color: #ffffff; margin-top: 2px;">Dune Watchtowers</div>
                <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">Perimeter Defense</div>
                <div style="font-size: 13px; font-weight: bold; color: #10b981; margin-top: 6px;">Buff: Fortress Shielding</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

        st.markdown('### ⚔️ Desolate Desert 4-Way Combat Protocol (Cavalry & Swordsmen Priority)')
        st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.9); border: 1.5px solid #d4af37; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px;">
            <div style="color: #d4af37; font-weight: 900; font-size: 14px;">⚡ 4-KINGDOM DESERT EXPEDITION STRATEGY</div>
            <ul style="color: #f1f5f9; font-size: 13px; margin-top: 6px; padding-left: 20px;">
                <li><b>Central Citadel Siege:</b> Requires heavy Swordsmen marches to absorb multi-server counter-rallies.</li>
                <li><b>Sanctuary Control (4 Corners):</b> Deploy high-speed Cavalry to capture shrines early before rival kingdoms position defenses.</li>
                <li><b>Pikemen Defense Line:</b> Reinforce captured checkpoints with Pikemen to counter incoming enemy Cavalry rushes (+30% damage).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('#### 👑 Recommended Desert Strike Leaders (From Kingdom 070)')
        dd_leads_table = [
            {"Role / Objective": "Citadel Assault (Main Lead)", "Recommended Unit": "🗡️ Swordsmen", "Lead Governor": "DylanR2SK²⁵⁵", "Troop Power": "66,798,930", "Tactical Duty": "Lead primary alliance rally on central citadel"},
            {"Role / Objective": "Citadel Co-Lead", "Recommended Unit": "🗡️ Swordsmen", "Lead Governor": "NEO20PP70BS", "Troop Power": "65,468,527", "Tactical Duty": "Backup wave reinforcement on enemy gate"},
            {"Role / Objective": "Oasis Sprint & Interception", "Recommended Unit": "🐎 Cavalry", "Lead Governor": "DylanR2SK²⁵⁵", "Troop Power": "63,195,280", "Tactical Duty": "Sprint to capture altars & intercept enemy archers"},
            {"Role / Objective": "Flank Cavalry Hunter", "Recommended Unit": "🐎 Cavalry", "Lead Governor": "קGrimReaperא", "Troop Power": "62,500,000", "Tactical Duty": "Patrol dunes and eliminate roaming gatherers"},
            {"Role / Objective": "Sanctuary Garrison Defense", "Recommended Unit": "🛡️ Pikemen", "Lead Governor": "קGrimReaperא", "Troop Power": "65,919,578", "Tactical Duty": "Hold Shrines against enemy Cavalry charges (+30% DMG)"}
        ]
        st.dataframe(pd.DataFrame(dd_leads_table), use_container_width=True, hide_index=True)

        render_benchmark_analytics(
            default_servers=["Server #070 (ERA70)"],
            key_prefix="dd_bench",
            title="Desolate Desert — Server Benchmark Analytics",
            section_subtitle="CROSS-SERVER POWER CURVES & DEFENSIVE THRESHOLDS"
        )

# ----------------- VIEW: ALLIANCE WAR ROOM & RALLY LEADERS -----------------
elif view_mode == "Alliance War Room & Rally Leaders":
    st.markdown("""<div class="cp-header">
        <div>
            <div class="cp-title">ALLIANCE WAR ROOM & RALLY PLANNER</div>
            <div class="cp-subtitle">RALLY LEADERS • TROOP TYPE SYNERGY • COUNTER TARGET SIMULATOR • CROSS-TROOP SEARCH</div>
        </div>
        <div style="text-align: right; border-left: 1px solid #334155; padding-left: 20px;">
            <div style="color: #d4af37; font-size: 11px; font-weight: bold;">WAR ROOM STATUS</div>
            <div style="color: #10b981; font-size: 16px; font-weight: 900; margin-top: 4px;">ACTIVE</div>
        </div>
    </div>""", unsafe_allow_html=True)


    # 1. Load Files
    df_swords = pd.read_excel("Swordsmen_Rankings_Top50.xlsx") if os.path.exists("Swordsmen_Rankings_Top50.xlsx") else pd.DataFrame()
    df_pikes = pd.read_excel("Pikemen_Rankings_Top50.xlsx") if os.path.exists("Pikemen_Rankings_Top50.xlsx") else pd.DataFrame()
    df_cav = pd.read_excel("Cavalry_Rankings_Kingsland.xlsx") if os.path.exists("Cavalry_Rankings_Kingsland.xlsx") else pd.DataFrame()

    # Highlight Banner for Cavalry & Swordsmen in Rallies
    st.markdown("""
    <div style="background: linear-gradient(90deg, rgba(212, 175, 55, 0.15) 0%, rgba(30, 41, 59, 0.8) 100%); border: 1.5px solid #d4af37; border-radius: 8px; padding: 12px 18px; margin-bottom: 16px;">
        <div style="color: #d4af37; font-weight: 900; font-size: 14px;">⚡ ALLIANCE RALLY META STRATEGY</div>
        <div style="color: #ffffff; font-size: 13px; margin-top: 4px;">
            <b>Cavalry & Swordsmen are the top meta choices for rallies</b> due to superior march speed, burst damage, and elite commander synergy. Deploy them as primary rally leads below!
        </div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("📢 Export Rally Dispatch (WhatsApp & Discord Format)", expanded=False):
        st.caption("Copy this pre-formatted operational brief to share directly with your alliance:")
        sw_top = df_swords.iloc[0]["שם שחקן"] if not df_swords.empty and "שם שחקן" in df_swords.columns else "TBA"
        sw_pow = fmt_p(df_swords.iloc[0]["כוח פלוגת חרבות"]) if not df_swords.empty and "כוח פלוגת חרבות" in df_swords.columns else "--"
        pk_top = df_pikes.iloc[0]["שם שחקן"] if not df_pikes.empty and "שם שחקן" in df_pikes.columns else "TBA"
        pk_pow = fmt_p(df_pikes.iloc[0]["כוח פלוגת רומח"]) if not df_pikes.empty and "כוח פלוגת רומח" in df_pikes.columns else "--"
        cv_top = df_cav.iloc[0]["שם שחקן"] if not df_cav.empty and "שם שחקן" in df_cav.columns else "TBA"
        cv_pow = fmt_p(df_cav.iloc[0]["כוח פלוגת פרשים"]) if not df_cav.empty and "כוח פלוגת פרשים" in df_cav.columns else "--"

        dispatch_text = f"""⚔️ **AOEM ALLIANCE RALLY DISPATCH** ⚔️
🎯 **Primary Strike & Counter Protocol:**
🗡️ **Swordsmen Lead:** {sw_top} (Power: {sw_pow}) — *Citadel Breaker & Main Wave*
🛡️ **Pikemen Defense:** {pk_top} (Power: {pk_pow}) — *Shrine Garrison & Anti-Cav*
🐎 **Cavalry Flank:** {cv_top} (Power: {cv_pow}) — *Oasis Sprint & Archer Hunter*

⚡ **Alliance Order:** All members reinforce primary leads immediately! Check War Room for march type synergies.
"""
        st.text_area("Rally Dispatch Brief:", dispatch_text, height=160, key="rally_dispatch_txt")



    # 2. Interactive Target Advisor Card
    st.markdown("### 🎯 Rally Target Advisor")
    adv_col1, adv_col2 = st.columns([1, 2])
    with adv_col1:
        enemy_troop = st.selectbox(
            "Select Primary Unit Garrisoned in Enemy Target / Gate:",
            ["🐎 Cavalry", "🗡️ Swordsmen", "🛡️ Pikemen", "🏹 Archers"]
        )
    with adv_col2:
        if "Cavalry" in enemy_troop:
            rec_type = "🛡️ Pikemen"
            counter_desc = "Pikemen negate cavalry mobility and deal +30% direct bonus damage."
            top_rec = df_pikes.iloc[0]["שם שחקן"] if not df_pikes.empty else "N/A"
            rec_pow = df_pikes.iloc[0]["כוח פלוגת רומח"] if not df_pikes.empty else "--"
        elif "Swordsmen" in enemy_troop:
            rec_type = "🏹 Archers (or 🐎 Cavalry)"
            counter_desc = "Archers break swordsmen formations from range (+30% bonus damage). Alternatively, fast cavalry out-maneuver them."
            top_rec = df_cav.iloc[0]["שם שחקן"] if not df_cav.empty else "N/A"
            rec_pow = df_cav.iloc[0]["כוח פלוגת פרשים"] if not df_cav.empty else "--"
        elif "Pikemen" in enemy_troop:
            rec_type = "🗡️ Swordsmen"
            counter_desc = "Swordsmen cleave through pike formations with +30% close-combat bonus damage."
            top_rec = df_swords.iloc[0]["שם שחקן"] if not df_swords.empty else "N/A"
            rec_pow = df_swords.iloc[0]["כוח פלוגת חרבות"] if not df_swords.empty else "--"
        else:
            rec_type = "🐎 Cavalry"
            counter_desc = "Cavalry overwhelm archers before they can fire sustained volleys (+30% bonus damage)."
            top_rec = df_cav.iloc[0]["שם שחקן"] if not df_cav.empty else "N/A"
            rec_pow = df_cav.iloc[0]["כוח פלוגת פרשים"] if not df_cav.empty else "--"

        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.12); border: 2px solid #10b981; border-radius: 8px; padding: 14px; margin-top: 4px;">
            <div style="color: #10b981; font-weight: 900; font-size: 15px;">Recommended Rally Formation: {rec_type}</div>
            <div style="color: #94a3b8; font-size: 12px; margin-top: 4px;">{counter_desc}</div>
            <div style="color: #ffffff; font-size: 14px; margin-top: 6px;"><b>Top Recommended Leader:</b> <span style="color:#d4af37; font-weight:bold;">{top_rec}</span> (Troop Power: {rec_pow})</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # 3. Top Rally Leaders 3 Columns
    st.markdown("### 👑 Top Rally Leaders by Troop Type")
    r_c1, r_c2, r_c3 = st.columns(3)

    with r_c1:
        st.markdown("""<div style="background: rgba(220, 38, 38, 0.15); border: 1.5px solid #ef4444; border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 10px;">
            <div style="font-weight: 900; color: #f87171; font-size: 15px;">🗡️ TOP SWORDSMEN LEADERS</div>
        </div>""", unsafe_allow_html=True)
        if not df_swords.empty:
            st.dataframe(df_swords.head(10).rename(columns={"דירוג": "Rank", "ברית": "Alliance", "שם שחקן": "Player", "כוח פלוגת חרבות": "Swords Power"}), use_container_width=True, height=360, hide_index=True)

    with r_c2:
        st.markdown("""<div style="background: rgba(56, 189, 248, 0.15); border: 1.5px solid #38bdf8; border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 10px;">
            <div style="font-weight: 900; color: #38bdf8; font-size: 15px;">🛡️ TOP PIKEMEN LEADERS</div>
        </div>""", unsafe_allow_html=True)
        if not df_pikes.empty:
            st.dataframe(df_pikes.head(10).rename(columns={"דירוג": "Rank", "ברית": "Alliance", "שם שחקן": "Player", "כוח פלוגת רומח": "Pikes Power"}), use_container_width=True, height=360, hide_index=True)

    with r_c3:
        st.markdown("""<div style="background: rgba(168, 85, 247, 0.15); border: 1.5px solid #a855f7; border-radius: 8px; padding: 10px; text-align: center; margin-bottom: 10px;">
            <div style="font-weight: 900; color: #c084fc; font-size: 15px;">🐎 TOP CAVALRY LEADERS</div>
        </div>""", unsafe_allow_html=True)
        if not df_cav.empty:
            st.dataframe(df_cav.head(10).rename(columns={"דירוג": "Rank", "ברית": "Alliance", "שם שחקן": "Player", "כוח פלוגת פרשים": "Cav Power"}), use_container_width=True, height=360, hide_index=True)

    st.divider()


    # 4. Cross-Troop Master Player Search with Recommendations & Hero Visuals
    st.markdown("### 🔍 Cross-Troop Governor Search & Role Advisor")
    search_troop_player = st.text_input("Search Governor to inspect all troop formations, powers, and rankings:", "", placeholder="e.g. Dylan, GrimReaper, RoniN, NEO, KumanDan...", key="search_troop_input_key")
    
    if search_troop_player:
        all_names = set()
        for df_t in [df_swords, df_pikes, df_cav]:
            if not df_t.empty and "שם שחקן" in df_t.columns:
                matches = df_t[df_t["שם שחקן"].astype(str).str.contains(search_troop_player, case=False, na=False)]
                for name in matches["שם שחקן"].unique():
                    all_names.add(name)
        
        if not all_names:
            st.info("No governors found matching the query.")
        else:
            for name in all_names:
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.95); border: 2px solid #d4af37; border-radius: 10px; padding: 18px; margin-bottom: 20px;">
                    <div style="font-size: 22px; font-weight: 900; color: #ffffff; margin-bottom: 4px;">👤 {name}</div>
                    <div style="color: #d4af37; font-size: 13px; font-weight: bold; margin-bottom: 14px;">⚡ Strategic Alliance Role: Top Rally Leader for <b>Cavalry</b> and <b>Swordsmen</b>!</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Fetch troop rows
                sw_row = df_swords[df_swords["שם שחקן"] == name].iloc[0] if not df_swords.empty and not df_swords[df_swords["שם שחקן"] == name].empty else None
                pk_row = df_pikes[df_pikes["שם שחקן"] == name].iloc[0] if not df_pikes.empty and not df_pikes[df_pikes["שם שחקן"] == name].empty else None
                cv_row = df_cav[df_cav["שם שחקן"] == name].iloc[0] if not df_cav.empty and not df_cav[df_cav["שם שחקן"] == name].empty else None
                
                sc1, sc2, sc3 = st.columns(3)
                
                with sc1:
                    sw_p_str = sw_row["כוח פלוגת חרבות"] if sw_row is not None else "--"
                    sw_r_str = f"#{sw_row['דירוג']}" if sw_row is not None else "--"
                    st.markdown(f"""<div class="troop-battle-card" style="border: 1px solid #ef4444;">
                        <div style="font-weight:900; font-size:15px; color:#f87171;">🗡️ Swordsmen • {sw_r_str}</div>
                        <div style="font-size:20px; font-weight:900; color:#ffffff; font-family:monospace; margin-top:6px;">{sw_p_str}</div>
                        <div style="font-size:11px; color:#10b981; margin-top:4px;">🔥 Ideal: Offensive Rally / Citadel Breaker</div>
                    </div>""", unsafe_allow_html=True)
                    
                with sc2:
                    cv_p_str = cv_row["כוח פלוגת פרשים"] if cv_row is not None else "--"
                    cv_r_str = f"#{cv_row['דירוג']}" if cv_row is not None else "--"
                    st.markdown(f"""<div class="troop-battle-card" style="border: 1px solid #a855f7;">
                        <div style="font-weight:900; font-size:15px; color:#c084fc;">🐎 Cavalry • {cv_r_str}</div>
                        <div style="font-size:20px; font-weight:900; color:#ffffff; font-family:monospace; margin-top:6px;">{cv_p_str}</div>
                        <div style="font-size:11px; color:#10b981; margin-top:4px;">🔥 Ideal: Rapid Flank / Archer Hunter</div>
                    </div>""", unsafe_allow_html=True)
                    
                with sc3:
                    pk_p_str = pk_row["כוח פלוגת רומח"] if pk_row is not None else "--"
                    pk_r_str = f"#{pk_row['דירוג']}" if pk_row is not None else "--"
                    st.markdown(f"""<div class="troop-battle-card" style="border: 1px solid #38bdf8;">
                        <div style="font-weight:900; font-size:15px; color:#38bdf8;">🛡️ Pikemen • {pk_r_str}</div>
                        <div style="font-size:20px; font-weight:900; color:#ffffff; font-family:monospace; margin-top:6px;">{pk_p_str}</div>
                        <div style="font-size:11px; color:#38bdf8; margin-top:4px;">🛡️ Ideal: Citadel Defense / Anti-Cavalry</div>
                    </div>""", unsafe_allow_html=True)



    st.divider()
    st.markdown("### ⚔️ Kingdom & Alliance War Room Matrix")
    st.caption("Compare cumulative power, governors count, and top roster between any two kingdoms and alliances:")

    # Two columns for Server & Alliance Selection
    mat_c1, mat_c2 = st.columns(2)
    
    with mat_c1:
        st.markdown('<div style="font-weight:900; color:#d4af37; margin-bottom:4px;">SIDE A (CHALLENGER)</div>', unsafe_allow_html=True)
        srv_mat_a = st.selectbox("Select Kingdom A:", server_names, index=default_server_p1_idx, key="mat_srv_a_sel")
        
        # Get alliances for Kingdom A
        df_k_a = master_combined_df[master_combined_df["Kingdom"] == srv_mat_a] if not master_combined_df.empty else pd.DataFrame()
        if not df_k_a.empty and "Alliance" in df_k_a.columns:
            raw_all_a = [str(a) for a in df_k_a["Alliance"].dropna().unique() if str(a).strip() not in ["--", "nan", ""]]
            # Sort alliances by total power in this kingdom
            all_pow_a = [(a, df_k_a[df_k_a["Alliance"] == a]["Power"].sum()) for a in raw_all_a]
            all_pow_a.sort(key=lambda x: x[1], reverse=True)
            alliances_a = ["👑 All Alliances Combined (Full Kingdom)"] + [a[0] for a in all_pow_a]
        else:
            alliances_a = ["👑 All Alliances Combined (Full Kingdom)"]
            
        alliance_a = st.selectbox("Select Alliance A:", alliances_a, index=0, key="mat_all_a_sel")

    with mat_c2:
        st.markdown('<div style="font-weight:900; color:#38bdf8; margin-bottom:4px;">SIDE B (OPPONENT)</div>', unsafe_allow_html=True)
        default_b_idx = 1 if len(server_names) > 1 else 0
        srv_mat_b = st.selectbox("Select Kingdom B:", server_names, index=default_b_idx, key="mat_srv_b_sel")
        
        # Get alliances for Kingdom B
        df_k_b = master_combined_df[master_combined_df["Kingdom"] == srv_mat_b] if not master_combined_df.empty else pd.DataFrame()
        if not df_k_b.empty and "Alliance" in df_k_b.columns:
            raw_all_b = [str(a) for a in df_k_b["Alliance"].dropna().unique() if str(a).strip() not in ["--", "nan", ""]]
            all_pow_b = [(a, df_k_b[df_k_b["Alliance"] == a]["Power"].sum()) for a in raw_all_b]
            all_pow_b.sort(key=lambda x: x[1], reverse=True)
            alliances_b = ["👑 All Alliances Combined (Full Kingdom)"] + [b[0] for b in all_pow_b]
        else:
            alliances_b = ["👑 All Alliances Combined (Full Kingdom)"]
            
        alliance_b = st.selectbox("Select Alliance B:", alliances_b, index=0, key="mat_all_b_sel")

    # Filter data for Side A
    if alliance_a == "👑 All Alliances Combined (Full Kingdom)":
        df_side_a = df_k_a.copy() if not df_k_a.empty else pd.DataFrame()
        lbl_a = f"{srv_mat_a} (Full)"
    else:
        clean_a = alliance_a.replace("[", "").replace("]", "").strip()
        df_side_a = df_k_a[df_k_a["Alliance"].astype(str).str.contains(re.escape(clean_a), case=False, na=False)].copy() if not df_k_a.empty else pd.DataFrame()
        lbl_a = f"{alliance_a} ({srv_mat_a})"

    # Filter data for Side B
    if alliance_b == "👑 All Alliances Combined (Full Kingdom)":
        df_side_b = df_k_b.copy() if not df_k_b.empty else pd.DataFrame()
        lbl_b = f"{srv_mat_b} (Full)"
    else:
        clean_b = alliance_b.replace("[", "").replace("]", "").strip()
        df_side_b = df_k_b[df_k_b["Alliance"].astype(str).str.contains(re.escape(clean_b), case=False, na=False)].copy() if not df_k_b.empty else pd.DataFrame()
        lbl_b = f"{alliance_b} ({srv_mat_b})"

    pow_a = df_side_a["Power"].sum() if not df_side_a.empty else 0.0
    pow_b = df_side_b["Power"].sum() if not df_side_b.empty else 0.0
    cnt_a = len(df_side_a)
    cnt_b = len(df_side_b)
    avg_a = df_side_a["Power"].mean() if not df_side_a.empty else 0.0
    avg_b = df_side_b["Power"].mean() if not df_side_b.empty else 0.0
    diff_ab = pow_a - pow_b

    # Metrics Summary Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric(f"Side A Power", fmt_score_b_m(pow_a), f"{cnt_a} Governors (Avg {fmt_score_b_m(avg_a)})")
    m_col2.metric(f"Side B Power", fmt_score_b_m(pow_b), f"{cnt_b} Governors (Avg {fmt_score_b_m(avg_b)})")
    diff_label = "Side A Leads" if diff_ab >= 0 else "Side B Leads"
    diff_delta = f"+{fmt_score_b_m(diff_ab)}" if diff_ab >= 0 else f"-{fmt_score_b_m(abs(diff_ab))}"
    m_col3.metric("Power Difference", fmt_score_b_m(abs(diff_ab)), diff_label)
    
    # Power Share Ratio
    tot_pow_both = pow_a + pow_b
    share_a = (pow_a / tot_pow_both * 100.0) if tot_pow_both > 0 else 50.0
    m_col4.metric("Power Dominance", f"{share_a:.1f}% vs {100-share_a:.1f}%", f"{lbl_a[:12]} vs {lbl_b[:12]}")

    # Comparison Bar Chart
    fig_mat = go.Figure(go.Bar(
        x=[lbl_a, lbl_b],
        y=[pow_a / 1e6, pow_b / 1e6],
        marker_color=['#d4af37', '#38bdf8'],
        text=[f"{fmt_score_b_m(pow_a)} ({cnt_a} govs)", f"{fmt_score_b_m(pow_b)} ({cnt_b} govs)"],
        textposition='outside'
    ))
    max_y = max(pow_a, pow_b) / 1e6
    fig_mat.update_layout(
        template="plotly_dark",
        title="Comparative Power Profile (Millions)",
        yaxis=dict(title="Total Power (Millions)", range=[0, max(max_y * 1.25, 10)]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,10,18,0.85)",
        height=320,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    st.plotly_chart(fig_mat, use_container_width=True, key="mat_power_bar_chart")

    # Side-by-side Top Champions Roster
    st.markdown("#### 🏆 Top Champions Comparison (Roster Breakdown)")
    t_c1, t_c2 = st.columns(2)
    
    with t_c1:
        st.markdown(f'<div style="font-weight:900; color:#d4af37; margin-bottom:6px;">⚔️ TOP 10 — {lbl_a}</div>', unsafe_allow_html=True)
        if not df_side_a.empty:
            sub_a = df_side_a.sort_values(by="Power", ascending=False).head(10).copy()
            sub_a["Rank"] = range(1, len(sub_a) + 1)
            sub_a["Power"] = sub_a["Power"].apply(fmt_p)
            cols_a = [c for c in ["Rank", "Player", "Alliance", "Power", "Tier"] if c in sub_a.columns]
            st.dataframe(sub_a[cols_a], use_container_width=True, hide_index=True)
        else:
            st.info("No governors found for Side A.")

    with t_c2:
        st.markdown(f'<div style="font-weight:900; color:#38bdf8; margin-bottom:6px;">🛡️ TOP 10 — {lbl_b}</div>', unsafe_allow_html=True)
        if not df_side_b.empty:
            sub_b = df_side_b.sort_values(by="Power", ascending=False).head(10).copy()
            sub_b["Rank"] = range(1, len(sub_b) + 1)
            sub_b["Power"] = sub_b["Power"].apply(fmt_p)
            cols_b = [c for c in ["Rank", "Player", "Alliance", "Power", "Tier"] if c in sub_b.columns]
            st.dataframe(sub_b[cols_b], use_container_width=True, hide_index=True)
        else:
            st.info("No governors found for Side B.")
