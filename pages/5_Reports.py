"""
SecureIoT — Reports Page
Attack history, security logs, comparison charts, CSV export.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from styles.theme import get_css, section_title, plotly_theme
from modules import database as db

st.set_page_config(page_title="Reports — SecureIoT", page_icon="📊", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div style="text-align:center;padding:10px 0;">
    <h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;">📊 Reports</h1>
    <p style="color:#64748b;">Security analytics, attack history, and downloadable reports</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

tab_attacks, tab_events, tab_audit, tab_compare, tab_export = st.tabs([
    "⚔️ Attack History", "🔔 Security Events", "📋 Audit Logs",
    "📊 Before/After Comparison", "💾 Export CSV",
])

# ════════════════════════════════════════════
#  Attack History
# ════════════════════════════════════════════
with tab_attacks:
    st.markdown(section_title("Attack Simulation History", "⚔️"), unsafe_allow_html=True)

    attack_logs = db.get_attack_logs(200)
    if attack_logs:
        df_attacks = pd.DataFrame(attack_logs)
        df_display = df_attacks[["timestamp", "attack_type", "mode", "result", "details"]].copy()
        df_display.columns = ["Time", "Attack Type", "Mode", "Result", "Details"]
        df_display["Result"] = df_display["Result"].apply(lambda x: "🔴 Success" if x == "success" else "🟢 Blocked")
        df_display["Mode"] = df_display["Mode"].apply(lambda x: "🔓 Insecure" if x == "insecure" else "🛡️ Secure")
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)

        # Stats
        attack_stats = db.get_attack_stats()
        if attack_stats:
            st.markdown("---")
            st.markdown("#### Attack Statistics")

            df_stats = pd.DataFrame(attack_stats)
            fig = go.Figure()
            for result_type, color, label in [("blocked", "#10b981", "Blocked"), ("success", "#ef4444", "Successful")]:
                f = df_stats[df_stats["result"] == result_type]
                if not f.empty:
                    fig.add_trace(go.Bar(x=f["attack_type"], y=f["count"], name=label, marker_color=color))
            fig.update_layout(**plotly_theme(), barmode="group", height=400, yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🔍 No attacks simulated yet. Go to **Attack Simulation** to generate data.")

# ════════════════════════════════════════════
#  Security Events
# ════════════════════════════════════════════
with tab_events:
    st.markdown(section_title("Security Events", "🔔"), unsafe_allow_html=True)

    events = db.get_security_events(200)
    if events:
        df_events = pd.DataFrame(events)
        df_display = df_events[["timestamp", "event_type", "severity", "description", "source"]].copy()
        df_display.columns = ["Time", "Event Type", "Severity", "Description", "Source"]

        severity_map = {"info": "🟢 Info", "warning": "🟡 Warning", "high": "🔴 High", "critical": "🔴 Critical"}
        df_display["Severity"] = df_display["Severity"].apply(lambda s: severity_map.get(s, s))
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)

        # Severity distribution
        severity_counts = df_events["severity"].value_counts().reset_index()
        severity_counts.columns = ["Severity", "Count"]
        fig = go.Figure(data=[go.Pie(
            labels=severity_counts["Severity"],
            values=severity_counts["Count"],
            hole=0.4,
            marker=dict(colors=["#10b981", "#f59e0b", "#ef4444", "#dc2626"]),
        )])
        fig.update_layout(**plotly_theme(), height=350, title="Event Severity Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No security events recorded yet.")

# ════════════════════════════════════════════
#  Audit Logs
# ════════════════════════════════════════════
with tab_audit:
    st.markdown(section_title("Audit Logs", "📋"), unsafe_allow_html=True)

    audit_logs = db.get_audit_logs(200)
    if audit_logs:
        df_audit = pd.DataFrame(audit_logs)
        df_display = df_audit[["timestamp", "username", "action", "resource", "result"]].copy()
        df_display.columns = ["Time", "User", "Action", "Resource", "Result"]
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("No audit logs yet. Register users or manage devices to generate logs.")

# ════════════════════════════════════════════
#  Before/After Comparison
# ════════════════════════════════════════════
with tab_compare:
    st.markdown(section_title("Before & After Security Comparison", "📊"), unsafe_allow_html=True)

    # Comparison table
    comparison_data = {
        "Security Aspect": [
            "Data Transmission", "Device Identity", "Password Security",
            "Traffic Management", "Data Privacy", "Data Integrity",
            "Access Control", "API Security", "Key Management",
        ],
        "Before (Insecure)": [
            "Plaintext — readable by anyone", "No authentication — any device accepted",
            "Unlimited login attempts", "No rate limiting — DoS possible",
            "Raw data exposed", "No integrity checks",
            "No access restrictions", "Open endpoints", "Static keys",
        ],
        "After (Secure)": [
            "AES-256 encrypted", "HMAC device authentication",
            "bcrypt hashing + account lockout", "Per-IP rate limiting",
            "Pseudonymised + noise added", "HMAC-SHA256 verification",
            "RBAC with 3 roles", "JWT + rate limiting + validation",
            "Regular key rotation",
        ],
        "Mechanism": [
            "AES-256-CBC", "HMAC-SHA256", "bcrypt + rate limiting",
            "Rate limiter", "Differential privacy", "HMAC",
            "Role-Based Access Control", "FastAPI + JWT", "Key rotation protocol",
        ],
    }
    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

    # Visual comparison
    st.markdown("---")
    st.markdown("#### Security Score Comparison")

    categories = ["Encryption", "Authentication", "Integrity", "Access Control", "Privacy", "Availability"]
    insecure_scores = [1, 1, 1, 1, 1, 2]
    secure_scores = [9, 9, 9, 8, 8, 8]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=categories, y=insecure_scores, name="Before (Insecure)", marker_color="#ef4444"))
    fig.add_trace(go.Bar(x=categories, y=secure_scores, name="After (Secure)", marker_color="#10b981"))
    fig.update_layout(**plotly_theme(), barmode="group", height=400, yaxis_title="Score (1-10)", yaxis=dict(range=[0, 10], gridcolor="#1e293b", zerolinecolor="#1e293b"))
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════
#  CSV Export
# ════════════════════════════════════════════
with tab_export:
    st.markdown(section_title("Export Reports as CSV", "💾"), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### ⚔️ Attack Logs")
        attack_data = db.get_attack_logs(500)
        if attack_data:
            df = pd.DataFrame(attack_data)
            csv = df.to_csv(index=False)
            st.download_button("💾 Download Attack Logs", csv, "attack_logs.csv", "text/csv", use_container_width=True)
            st.caption(f"{len(attack_data)} records")
        else:
            st.info("No data yet.")

    with col2:
        st.markdown("#### 🔔 Security Events")
        event_data = db.get_security_events(500)
        if event_data:
            df = pd.DataFrame(event_data)
            csv = df.to_csv(index=False)
            st.download_button("💾 Download Security Events", csv, "security_events.csv", "text/csv", use_container_width=True)
            st.caption(f"{len(event_data)} records")
        else:
            st.info("No data yet.")

    with col3:
        st.markdown("#### 📋 Audit Logs")
        audit_data = db.get_audit_logs(500)
        if audit_data:
            df = pd.DataFrame(audit_data)
            csv = df.to_csv(index=False)
            st.download_button("💾 Download Audit Logs", csv, "audit_logs.csv", "text/csv", use_container_width=True)
            st.caption(f"{len(audit_data)} records")
        else:
            st.info("No data yet.")

    # Full report
    st.markdown("---")
    st.markdown("#### 📄 Full Security Report")
    if st.button("📄 Generate Full Report", use_container_width=True, key="full_report"):
        report_lines = ["# SecureIoT Security Report", f"Generated: {pd.Timestamp.now()}", ""]

        report_lines.append("## Device Summary")
        stats = db.get_device_stats()
        report_lines.append(f"- Total Devices: {stats['total']}")
        report_lines.append(f"- Active Devices: {stats['active']}")
        report_lines.append(f"- Messages Received: {db.get_message_count()}")
        report_lines.append(f"- Attacks Simulated: {db.get_total_attacks()}")
        report_lines.append("")

        report_lines.append("## Attack Statistics")
        a_stats = db.get_attack_stats()
        if a_stats:
            for s in a_stats:
                report_lines.append(f"- {s['attack_type']} ({s['mode']}): {s['result']} × {s['count']}")
        report_lines.append("")

        report_lines.append("## Security Mechanisms Implemented")
        mechanisms = [
            "AES-256-CBC Encryption", "SHA-256 Hashing", "HMAC-SHA256 Integrity",
            "RSA Digital Signatures", "bcrypt Password Hashing", "RBAC (3 Roles)",
            "Challenge-Response Authentication", "Key Rotation", "Rate Limiting",
            "Pseudonymisation", "Data Aggregation", "Noise Addition",
            "JWT API Authentication", "Input Validation", "Encrypted Telemetry Storage",
        ]
        for m in mechanisms:
            report_lines.append(f"- ✅ {m}")

        report_text = "\n".join(report_lines)
        st.download_button("💾 Download Full Report", report_text, "security_report.md", "text/markdown", use_container_width=True)
        st.code(report_text, language="markdown")
