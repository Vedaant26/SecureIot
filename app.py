"""
SecureIoT — Dashboard (Home Page)
Main entry point for the Streamlit application.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

from styles.theme import get_css, metric_card, section_title, plotly_theme
from modules import database as db

# ── Page Config ──
st.set_page_config(
    page_title="SecureIoT Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Apply Theme ──
st.markdown(get_css(), unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("# 🛡️ SecureIoT")
    st.markdown("---")
    st.markdown("""
    <div style="color:#64748b;font-size:0.8rem;padding:8px 0;">
        <strong style="color:#94a3b8;">IoT Security Simulator</strong><br>
        Smart Building Security Platform<br><br>
        📊 Dashboard<br>
        🏢 Smart Building<br>
        ⚔️ Attack Simulation<br>
        🔐 Cryptography<br>
        🛡️ Access Control<br>
        📋 Reports
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        '<div style="color:#475569;font-size:0.7rem;text-align:center;">SecureIoT v1.0 • BTech Project</div>',
        unsafe_allow_html=True,
    )

# ── Dashboard Header ──
st.markdown("""
<div style="text-align:center;padding:20px 0 10px 0;">
    <h1 style="color:#e2e8f0;font-size:2.2rem;font-weight:700;margin-bottom:4px;">
        🛡️ SecureIoT Dashboard
    </h1>
    <p style="color:#64748b;font-size:1rem;">
        Real-time IoT Security Monitoring • Smart Building Environment
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Fetch Data ──
device_stats = db.get_device_stats()
message_count = db.get_message_count()
attack_count = db.get_total_attacks()
events = db.get_security_events(10)

# ── Metric Cards Row ──
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(metric_card("Total Devices", device_stats["total"], "📡", color="#3b82f6"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Active Devices", device_stats["active"], "✅", color="#10b981"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Messages", message_count, "📨", color="#8b5cf6"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Attacks Tested", attack_count, "⚔️", color="#f59e0b"), unsafe_allow_html=True)
with c5:
    sec_status = "Protected" if attack_count == 0 or True else "At Risk"
    st.markdown(metric_card("Security Status", sec_status, "🔒", color="#10b981"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row ──
col_left, col_right = st.columns(2)

with col_left:
    st.markdown(section_title("Device Distribution", "📊"), unsafe_allow_html=True)

    type_labels = {
        "temperature": "🌡️ Temperature",
        "door_lock": "🔒 Door Lock",
        "energy": "⚡ Energy",
        "motion": "👁️ Motion",
    }
    labels = [type_labels.get(t, t) for t in device_stats["by_type"].keys()]
    values = list(device_stats["by_type"].values())

    fig_pie = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"]),
        textinfo="label+value",
        textfont=dict(size=13, color="#e2e8f0"),
    )])
    fig_pie.update_layout(
        **plotly_theme(),
        height=350,
        showlegend=False,
        title=None,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.markdown(section_title("Security Overview", "🛡️"), unsafe_allow_html=True)

    # Attack stats
    attack_stats = db.get_attack_stats()
    if attack_stats:
        df_stats = pd.DataFrame(attack_stats)
        # Pivot for chart
        blocked = df_stats[df_stats["result"] == "blocked"].groupby("attack_type")["count"].sum().reset_index()
        successful = df_stats[df_stats["result"] == "success"].groupby("attack_type")["count"].sum().reset_index()

        fig_bar = go.Figure()
        if not blocked.empty:
            fig_bar.add_trace(go.Bar(
                x=blocked["attack_type"], y=blocked["count"],
                name="Blocked", marker_color="#10b981",
            ))
        if not successful.empty:
            fig_bar.add_trace(go.Bar(
                x=successful["attack_type"], y=successful["count"],
                name="Successful", marker_color="#ef4444",
            ))
        fig_bar.update_layout(
            **plotly_theme(),
            height=350,
            barmode="group",
            title=None,
            xaxis_title=None,
            yaxis_title="Count",
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("🔍 No attack simulations yet. Go to **Attack Simulation** to test security.")

# ── Recent Events Table ──
st.markdown(section_title("Recent Security Events", "📋"), unsafe_allow_html=True)

if events:
    df_events = pd.DataFrame(events)
    df_display = df_events[["timestamp", "event_type", "severity", "description", "source"]].copy()
    df_display.columns = ["Time", "Event", "Severity", "Description", "Source"]

    # Color severity
    def severity_emoji(s):
        return {"info": "🟢 Info", "warning": "🟡 Warning", "high": "🔴 High", "critical": "🔴 Critical"}.get(s, s)

    df_display["Severity"] = df_display["Severity"].apply(severity_emoji)
    st.dataframe(df_display, use_container_width=True, hide_index=True, height=250)
else:
    st.info("No security events recorded yet.")

# ── Footer ──
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#475569;font-size:0.8rem;padding:10px 0;">
    SecureIoT — IoT Security Simulation Platform • GGSIPU BTech Project<br>
    Built with Streamlit, Python, SQLite, FastAPI
</div>
""", unsafe_allow_html=True)
