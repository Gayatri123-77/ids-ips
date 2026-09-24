import os
import sys
import time
import random
import subprocess
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Safe import for auto-refresh
try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

LOG_FILE = "blocked_ips.txt"

# ---------------------------------------------------------
# Page Configuration & Dark Cyberpunk Theme Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cyberpunk IDS/IPS Live Sentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cyberpunk Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #58a6ff;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Sample Data Pre-population for Immediate Dashboard Output
# ---------------------------------------------------------
def generate_initial_sample_data():
    """Generates realistic sample traffic flows if log file is empty."""
    rng = random.Random(42)
    sample_ips = ["10.0.3.69", "10.0.1.67", "10.0.2.15", "10.0.4.107", "10.0.4.207", "10.0.1.3", "10.0.2.229", "10.0.4.20", "10.0.0.158", "10.0.1.146"]
    blocked_ips_set = set()
    rows = []

    base_time = time.time() - 300 # 5 minutes ago

    for i in range(1, 51):
        t_str = time.strftime("%H:%M:%S", time.localtime(base_time + i * 6))
        src_ip = rng.choice(sample_ips)
        true_label = 1 if rng.random() < 0.44 else 0
        pred_label = true_label if rng.random() < 0.94 else (1 - true_label)
        confidence = round(rng.uniform(0.78, 1.00), 4)

        if pred_label == 1 and confidence >= 0.5:
            if src_ip not in blocked_ips_set:
                blocked_ips_set.add(src_ip)
                action = "blocked"
            else:
                action = "already_blocked"
        else:
            action = "allowed"

        rows.append(f"{t_str},{src_ip},{true_label},{pred_label},{confidence:.4f},{action}")

    with open(LOG_FILE, "w") as f:
        f.write("timestamp,src_ip,true_label,predicted,confidence,action\n")
        f.write("\n".join(rows) + "\n")


def load_log_data():
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) < 50:
        generate_initial_sample_data()

    try:
        df = pd.read_csv(LOG_FILE)
        if df.empty or "timestamp" not in df.columns:
            generate_initial_sample_data()
            df = pd.read_csv(LOG_FILE)

        df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0.0)
        df["true_label"] = pd.to_numeric(df["true_label"], errors="coerce").fillna(0).astype(int)
        df["predicted"] = pd.to_numeric(df["predicted"], errors="coerce").fillna(0).astype(int)
        df["src_ip"] = df["src_ip"].astype(str).str.strip()
        df["action"] = df["action"].astype(str).str.strip()
        return df
    except Exception:
        generate_initial_sample_data()
        return pd.read_csv(LOG_FILE)


def get_simulator_status():
    proc = st.session_state.get("simulator_proc", None)
    if proc is not None and proc.poll() is None:
        return True, proc.pid
    return False, None


def unblock_ip(ip_address):
    timestamp = time.strftime("%H:%M:%S")
    log_line = f"{timestamp},{ip_address},0,0,1.0000,unblocked\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)


def clear_logs():
    with open(LOG_FILE, "w") as f:
        f.write("timestamp,src_ip,true_label,predicted,confidence,action\n")


# ---------------------------------------------------------
# Sidebar Controls & Live Simulation Management
# ---------------------------------------------------------
st.sidebar.markdown("## 🛡️ Sentinel Control Center")
st.sidebar.markdown("---")

# Auto Refresh Settings
st.sidebar.subheader("🔄 Live Refresh Settings")
enable_refresh = st.sidebar.toggle("Auto-Refresh Dashboard", value=True)
refresh_interval = st.sidebar.select_slider(
    "Refresh Rate (seconds)",
    options=[1, 2, 3, 5, 10],
    value=2
)

if enable_refresh and HAS_AUTOREFRESH:
    st_autorefresh(interval=refresh_interval * 1000, key="ids_ips_autorefresh")

st.sidebar.markdown("---")

# Detector Simulator Process Controller
st.sidebar.subheader("⚡ Detector Simulator Controls")
is_running, pid = get_simulator_status()

if is_running:
    st.sidebar.success(f"🟢 Simulator RUNNING (PID: {pid})")
    if st.sidebar.button("🛑 Stop Simulator", type="primary"):
        proc = st.session_state.simulator_proc
        proc.terminate()
        st.session_state.simulator_proc = None
        st.toast("Detector simulator stopped!", icon="🛑")
        st.rerun()
else:
    st.sidebar.warning("🔴 Simulator STOPPED")

with st.sidebar.expander("⚙️ Simulation Parameters", expanded=not is_running):
    num_rows = st.number_input("Flows to Stream", min_value=50, max_value=5000, value=300, step=50)
    sleep_sec = st.slider("Stream Delay (sec)", min_value=0.01, max_value=0.5, value=0.03, step=0.01)
    threshold = st.slider("Confidence Threshold", min_value=0.1, max_value=1.0, value=0.5, step=0.05)
    seed = st.number_input("Random Seed", min_value=1, max_value=999, value=42)

if not is_running:
    if st.sidebar.button("🚀 Start Simulator Stream"):
        cmd = [
            sys.executable,
            "simulateDetector.py",
            "--num-rows", str(num_rows),
            "--sleep", str(sleep_sec),
            "--threshold", str(threshold),
            "--seed", str(seed)
        ]
        proc = subprocess.Popen(cmd, cwd=os.getcwd())
        st.session_state.simulator_proc = proc
        st.toast(f"Simulator launched with PID {proc.pid}!", icon="🚀")
        st.rerun()

st.sidebar.markdown("---")

# Data Management Buttons
if st.sidebar.button("🎲 Regenerate Initial Sample Flows"):
    generate_initial_sample_data()
    st.toast("Sample traffic flows re-generated!", icon="🎲")
    st.rerun()

if st.sidebar.button("🗑️ Clear All Logs"):
    clear_logs()
    st.toast("Logs cleared!", icon="🧹")
    st.rerun()


# ---------------------------------------------------------
# Main Dashboard Content
# ---------------------------------------------------------
st.title("🛡️ Cyberpunk IDS/IPS Live Sentinel Dashboard")
st.caption("Real-Time Machine Learning Intrusion Detection & Automated Firewall Deny-List Management")

df = load_log_data()

# Active Blocked IPs Calculation
if not df.empty:
    latest_ip_actions = df.groupby("src_ip").last()
    active_blocked_ips = latest_ip_actions[latest_ip_actions["action"].isin(["blocked", "already_blocked"])].index.tolist()
else:
    active_blocked_ips = []

# ---------------------------------------------------------
# KPI Metric Cards Row
# ---------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

total_flows = len(df)
alerts_raised = len(df[df["predicted"] == 1]) if total_flows > 0 else 0
unique_blocked = len(active_blocked_ips)
accuracy = (df["true_label"] == df["predicted"]).mean() * 100 if total_flows > 0 else 100.0
attack_rate = (alerts_raised / total_flows * 100) if total_flows > 0 else 0.0

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Flows Analyzed</div>
        <div class="metric-value">{total_flows:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Alerts Triggered</div>
        <div class="metric-value" style="color: #ff7b72;">{alerts_raised:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Active Blocked IPs</div>
        <div class="metric-value" style="color: #f0883e;">{unique_blocked}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Model Accuracy</div>
        <div class="metric-value" style="color: #3fb950;">{accuracy:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Threat Level</div>
        <div class="metric-value" style="color: {'#ff7b72' if attack_rate > 30 else '#d29922' if attack_rate > 10 else '#3fb950'};">{attack_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Tabbed Analytics Interface
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Live Threat Analytics",
    "🚫 Blocked IP Deny-List",
    "📜 Real-Time Stream Inspector"
])

# TAB 1: Live Threat Analytics
with tab1:
    chart_col1, chart_col2 = st.columns([2, 1])

    with chart_col1:
        st.subheader("📈 Traffic & Threat Volume Timeline")
        time_df = df.groupby(["timestamp", "action"]).size().reset_index(name="count")
        
        fig_timeline = px.bar(
            time_df,
            x="timestamp",
            y="count",
            color="action",
            color_discrete_map={
                "blocked": "#ff7b72",
                "already_blocked": "#d29922",
                "allowed": "#2ea043",
                "unblocked": "#58a6ff"
            },
            title="Flow Volume by Firewall Action Over Time",
            barmode="stack"
        )
        fig_timeline.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d1117",
            plot_bgcolor="#161b22",
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

    with chart_col2:
        st.subheader("🎯 Action Breakdown")
        action_counts = df["action"].value_counts().reset_index()
        action_counts.columns = ["action", "count"]
        
        fig_pie = px.pie(
            action_counts,
            names="action",
            values="count",
            color="action",
            color_discrete_map={
                "blocked": "#ff7b72",
                "already_blocked": "#d29922",
                "allowed": "#2ea043",
                "unblocked": "#58a6ff"
            },
            hole=0.4
        )
        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d1117",
            plot_bgcolor="#161b22",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    st.subheader("🔥 Top Malicious IP Sources")
    attack_ips = df[df["predicted"] == 1].groupby("src_ip").agg(
        total_attacks=("predicted", "count"),
        avg_confidence=("confidence", "mean"),
        last_seen=("timestamp", "max")
    ).reset_index().sort_values(by="total_attacks", ascending=False).head(10)

    if attack_ips.empty:
        st.write("No attack traffic detected yet.")
    else:
        fig_bar = px.bar(
            attack_ips,
            x="total_attacks",
            y="src_ip",
            orientation="h",
            color="avg_confidence",
            color_continuous_scale="Reds",
            title="Top 10 Attack Generating Source IPs",
            labels={"src_ip": "Source IP Address", "total_attacks": "Attack Count", "avg_confidence": "Avg Confidence"}
        )
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d1117",
            plot_bgcolor="#161b22",
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_bar, use_container_width=True)


# TAB 2: Blocked IP Deny-List Management
with tab2:
    st.subheader("🚫 Firewall Deny-List & Active Rule Management")
    
    if not active_blocked_ips:
        st.success("✅ Firewall Deny-List is clean. No active blocked IPs.")
    else:
        blocked_df = df[df["src_ip"].isin(active_blocked_ips)].groupby("src_ip").agg(
            total_alerts=("predicted", lambda x: (x == 1).sum()),
            avg_confidence=("confidence", "mean"),
            first_blocked=("timestamp", "min"),
            last_seen=("timestamp", "max")
        ).reset_index()

        st.dataframe(
            blocked_df.style.format({
                "avg_confidence": "{:.2%}"
            }),
            column_config={
                "src_ip": "Blocked IP Address",
                "total_alerts": "Total Attack Alerts",
                "avg_confidence": "Avg Threat Confidence",
                "first_blocked": "First Detected",
                "last_seen": "Last Active"
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### 🔓 Unblock Firewall Rule")
        ip_to_unblock = st.selectbox("Select IP Address to Unblock", options=active_blocked_ips)
        
        if st.button("🔓 Remove Block Rule for Selected IP", type="primary"):
            unblock_ip(ip_to_unblock)
            st.toast(f"IP {ip_to_unblock} successfully unblocked!", icon="🔓")
            st.rerun()


# TAB 3: Real-Time Stream Inspector
with tab3:
    st.subheader("📜 Live Network Flow Log")

    filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])
    with filter_col1:
        action_filter = st.multiselect("Action Filter", options=["blocked", "already_blocked", "allowed", "unblocked"], default=[])
    with filter_col2:
        min_conf = st.slider("Min Confidence Filter", 0.0, 1.0, 0.0, 0.05)
    with filter_col3:
        search_ip = st.text_input("Search IP Address", placeholder="e.g. 10.0.3.69")

    filtered_df = df.copy()

    if action_filter:
        filtered_df = filtered_df[filtered_df["action"].isin(action_filter)]
    if min_conf > 0.0:
        filtered_df = filtered_df[filtered_df["confidence"] >= min_conf]
    if search_ip:
        filtered_df = filtered_df[filtered_df["src_ip"].str.contains(search_ip, case=False)]

    if filtered_df.empty:
        st.info("No logs match the current filter criteria.")
    else:
        st.markdown(f"Displaying **{len(filtered_df)}** matching flows (latest on top):")

        def highlight_action(val):
            if val == "blocked":
                return "background-color: rgba(248, 81, 73, 0.2); color: #ff7b72; font-weight: bold;"
            elif val == "already_blocked":
                return "background-color: rgba(210, 153, 34, 0.2); color: #d29922;"
            elif val == "allowed":
                return "background-color: rgba(46, 160, 67, 0.2); color: #3fb950;"
            elif val == "unblocked":
                return "background-color: rgba(88, 166, 255, 0.2); color: #58a6ff; font-weight: bold;"
            return ""

        styler = filtered_df.iloc[::-1].style
        if hasattr(styler, "map"):
            styled_df = styler.map(highlight_action, subset=["action"])
        elif hasattr(styler, "applymap"):
            styled_df = styler.applymap(highlight_action, subset=["action"])
        else:
            styled_df = styler
        styled_df = styled_df.format({"confidence": "{:.4f}"})

        st.dataframe(styled_df, use_container_width=True, height=450, hide_index=True)

        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Log CSV",
            data=csv_data,
            file_name="ids_ips_filtered_logs.csv",
            mime="text/csv"
        )
