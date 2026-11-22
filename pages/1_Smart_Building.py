"""
SecureIoT — Smart Building Page
Displays 8+ virtual IoT devices and allows adding new ones.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from styles.theme import get_css, section_title, plotly_theme
from modules import database as db

st.set_page_config(page_title="Smart Building — SecureIoT", page_icon="🏢", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div style="text-align:center;padding:10px 0;">
    <h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;">🏢 Smart Building</h1>
    <p style="color:#64748b;">Virtual IoT devices in a smart building environment</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Load devices ──
devices = db.get_all_devices()

# ── Device Type Config ──
DEVICE_CONFIG = {
    "temperature": {"icon": "🌡️", "label": "Temperature Sensor", "color": "#3b82f6"},
    "door_lock": {"icon": "🔒", "label": "Smart Door Lock", "color": "#10b981"},
    "energy": {"icon": "⚡", "label": "Energy Meter", "color": "#f59e0b"},
    "motion": {"icon": "👁️", "label": "Motion Sensor", "color": "#8b5cf6"},
}

# ── Summary Metrics ──
st.markdown(section_title("Building Overview", "📊"), unsafe_allow_html=True)
cols = st.columns(4)
type_counts = {}
for d in devices:
    type_counts[d["type"]] = type_counts.get(d["type"], 0) + 1

for i, (dtype, cfg) in enumerate(DEVICE_CONFIG.items()):
    count = type_counts.get(dtype, 0)
    with cols[i]:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#111a35,#162040);border:1px solid #1e293b;
             border-left:4px solid {cfg['color']};border-radius:12px;padding:16px;text-align:center;">
            <div style="font-size:1.5rem;">{cfg['icon']}</div>
            <div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;">{cfg['label']}</div>
            <div style="color:#e2e8f0;font-size:1.5rem;font-weight:700;">{count}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Device Grid ──
st.markdown(section_title("IoT Devices", "📡"), unsafe_allow_html=True)

# Display in 4-column grid
for row_start in range(0, len(devices), 4):
    cols = st.columns(4)
    for j, col in enumerate(cols):
        idx = row_start + j
        if idx >= len(devices):
            break
        d = devices[idx]
        cfg = DEVICE_CONFIG.get(d["type"], {"icon": "📟", "label": d["type"], "color": "#64748b"})
        status_color = "#10b981" if d["status"] == "active" else "#ef4444" if d["status"] == "revoked" else "#f59e0b"
        status_text = d["status"].upper()

        with col:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#111a35,#162040);border:1px solid #1e293b;
                 border-radius:12px;padding:20px;margin-bottom:12px;min-height:200px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                    <span style="font-size:1.5rem;">{cfg['icon']}</span>
                    <span style="background:rgba({','.join(str(int(status_color[i:i+2],16)) for i in (1,3,5))},0.15);
                          color:{status_color};padding:3px 10px;border-radius:12px;font-size:0.7rem;
                          font-weight:600;text-transform:uppercase;">{status_text}</span>
                </div>
                <div style="color:#e2e8f0;font-size:0.95rem;font-weight:600;margin-bottom:4px;">{d['name']}</div>
                <div style="color:#64748b;font-size:0.8rem;margin-bottom:12px;">
                    📍 {d['location']}
                </div>
                <div style="background:#0b1120;border-radius:8px;padding:10px;text-align:center;">
                    <div style="color:#94a3b8;font-size:0.7rem;text-transform:uppercase;">Current Reading</div>
                    <div style="color:{cfg['color']};font-size:1.2rem;font-weight:700;">{d['reading']}</div>
                </div>
                <div style="color:#475569;font-size:0.7rem;margin-top:8px;">ID: {d['id']}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Add New Device ──
st.markdown("---")
st.markdown(section_title("Add New Virtual Device", "➕"), unsafe_allow_html=True)

with st.form("add_device_form"):
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("Device Name", placeholder="e.g., Temperature Sensor 3")
        new_type = st.selectbox("Device Type", ["temperature", "door_lock", "energy", "motion"])
    with col2:
        new_id = st.text_input("Device ID", placeholder="e.g., TEMP-003")
        new_location = st.text_input("Location", placeholder="e.g., Floor 3 - Conference Room")

    submitted = st.form_submit_button("➕ Add Device", use_container_width=True)
    if submitted:
        if new_name and new_id and new_location:
            # Check for duplicate
            existing = [d["id"] for d in devices]
            if new_id in existing:
                st.error(f"❌ Device ID '{new_id}' already exists.")
            else:
                db.add_device(new_id, new_name, new_type, new_location)
                db.log_security_event("device_added", "info", f"New device: {new_id} ({new_type})", "smart-building")
                st.success(f"✅ Device '{new_name}' ({new_id}) added successfully!")
                st.rerun()
        else:
            st.warning("⚠️ Please fill in all fields.")

# ── Security Requirements Table ──
st.markdown("---")
st.markdown(section_title("Security Requirements for Smart Building", "📋"), unsafe_allow_html=True)

requirements_data = {
    "Requirement": [
        "Confidentiality", "Integrity", "Authentication",
        "Availability", "Access Control", "Privacy",
    ],
    "Description": [
        "Sensor data must be encrypted during transmission",
        "Data must not be modified in transit",
        "Only registered devices should communicate",
        "System must remain operational under attack",
        "Role-based access to device controls",
        "Personal/device data must be anonymised",
    ],
    "Mechanism": [
        "AES-256 Encryption", "HMAC-SHA256 Integrity Check",
        "Challenge-Response + Device Registration",
        "Rate Limiting + DoS Protection", "RBAC (Admin/Operator/Viewer)",
        "Pseudonymisation + Noise Addition",
    ],
    "Status": ["✅ Implemented"] * 6,
}

import pandas as pd
st.dataframe(pd.DataFrame(requirements_data), use_container_width=True, hide_index=True)
