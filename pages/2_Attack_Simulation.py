"""
SecureIoT — Attack Simulation Page
Simulates 6 IoT attacks in insecure vs secure modes with comparison.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from styles.theme import get_css, section_title, plotly_theme
from modules import attack_sim
from modules import database as db

st.set_page_config(page_title="Attack Simulation — SecureIoT", page_icon="⚔️", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div style="text-align:center;padding:10px 0;">
    <h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;">⚔️ Attack Simulation</h1>
    <p style="color:#64748b;">Test IoT security by simulating real-world cyber attacks</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Attack Descriptions ──
ATTACK_INFO = {
    "Replay Attack": {
        "icon": "🔄", "color": "#3b82f6",
        "desc": "Captures and re-sends a legitimate message to repeat an action.",
        "defense": "Timestamps and nonces ensure each message is unique.",
    },
    "Spoofing Attack": {
        "icon": "🎭", "color": "#8b5cf6",
        "desc": "Attacker impersonates a legitimate IoT device.",
        "defense": "HMAC authentication verifies device identity.",
    },
    "Brute Force Attack": {
        "icon": "🔑", "color": "#ef4444",
        "desc": "Systematically tries passwords to gain access.",
        "defense": "Rate limiting locks the account after 3 failed attempts.",
    },
    "Flooding (DoS) Attack": {
        "icon": "🌊", "color": "#06b6d4",
        "desc": "Overwhelms the server with excessive traffic.",
        "defense": "Per-IP rate limiting drops excessive requests.",
    },
    "Sniffing Attack": {
        "icon": "🕵️", "color": "#f59e0b",
        "desc": "Intercepts network traffic to read sensitive data.",
        "defense": "AES-256 encryption makes intercepted data unreadable.",
    },
    "Tampering Attack": {
        "icon": "✏️", "color": "#10b981",
        "desc": "Modifies data while it is in transit.",
        "defense": "HMAC integrity check detects any modification.",
    },
}

ATTACK_FUNCTIONS = {
    "Replay Attack": attack_sim.simulate_replay_attack,
    "Spoofing Attack": attack_sim.simulate_spoofing_attack,
    "Brute Force Attack": attack_sim.simulate_brute_force_attack,
    "Flooding (DoS) Attack": attack_sim.simulate_flooding_attack,
    "Sniffing Attack": attack_sim.simulate_sniffing_attack,
    "Tampering Attack": attack_sim.simulate_tampering_attack,
}

# ── Mode Selection ──
st.markdown(section_title("Select Mode", "🔧"), unsafe_allow_html=True)
col_mode1, col_mode2, col_mode3 = st.columns([2, 2, 1])
with col_mode1:
    secure_mode = st.toggle("🛡️ Enable Security Protections", value=False)
with col_mode2:
    mode_text = "SECURE MODE" if secure_mode else "INSECURE MODE"
    mode_color = "#10b981" if secure_mode else "#ef4444"
    st.markdown(f"""
    <div style="background:rgba({','.join(str(int(mode_color[i:i+2],16)) for i in (1,3,5))},0.1);
         color:{mode_color};padding:8px 16px;border-radius:8px;font-weight:700;text-align:center;
         border:1px solid {mode_color};">
        {mode_text}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Individual Attack Simulation ──
st.markdown(section_title("Simulate Individual Attacks", "🎯"), unsafe_allow_html=True)

attack_tabs = st.tabs([f"{info['icon']} {name}" for name, info in ATTACK_INFO.items()])

for tab, (attack_name, info) in zip(attack_tabs, ATTACK_INFO.items()):
    with tab:
        col_desc, col_btn = st.columns([3, 1])
        with col_desc:
            st.markdown(f"""
            <div style="background:#111a35;border:1px solid #1e293b;border-left:4px solid {info['color']};
                 border-radius:8px;padding:16px;">
                <div style="color:#e2e8f0;font-weight:600;font-size:1rem;">{info['icon']} {attack_name}</div>
                <div style="color:#94a3b8;font-size:0.9rem;margin-top:4px;">{info['desc']}</div>
                <div style="color:#10b981;font-size:0.85rem;margin-top:8px;">
                    🛡️ <strong>Defense:</strong> {info['defense']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"▶ Run {attack_name}", key=f"btn_{attack_name}", use_container_width=True):
                func = ATTACK_FUNCTIONS[attack_name]
                with st.spinner(f"Simulating {attack_name}..."):
                    result = func(secure_mode=secure_mode)

                # Display result
                result_color = "#ef4444" if result["result"] == "success" else "#10b981"
                result_icon = "⚠️" if result["result"] == "success" else "✅"
                result_text = "ATTACK SUCCESSFUL" if result["result"] == "success" else "ATTACK BLOCKED"

                st.markdown(f"""
                <div style="background:rgba({','.join(str(int(result_color[i:i+2],16)) for i in (1,3,5))},0.1);
                     border:1px solid {result_color};border-radius:10px;padding:16px;margin:12px 0;">
                    <div style="color:{result_color};font-weight:700;font-size:1.1rem;">
                        {result_icon} {result_text}
                    </div>
                    <div style="color:#94a3b8;font-size:0.9rem;margin-top:4px;">
                        {result['details']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Show steps
                with st.expander("📋 View Detailed Steps", expanded=True):
                    for step in result["steps"]:
                        st.text(step)

# ── Run All Attacks ──
st.markdown("---")
st.markdown(section_title("Run All Attacks (Comparison)", "📊"), unsafe_allow_html=True)

col_run1, col_run2 = st.columns(2)
with col_run1:
    run_insecure = st.button("▶ Run All in INSECURE Mode", use_container_width=True, key="run_all_insecure")
with col_run2:
    run_secure = st.button("▶ Run All in SECURE Mode", use_container_width=True, key="run_all_secure")

if run_insecure or run_secure:
    mode = run_secure
    with st.spinner("Running all 6 attack simulations..."):
        results = attack_sim.run_all_attacks(secure_mode=mode)

    mode_label = "Secure" if mode else "Insecure"
    st.markdown(f"### Results — {mode_label} Mode")

    comparison_data = []
    for r in results:
        comparison_data.append({
            "Attack": r["attack_type"],
            "Mode": r["mode"].upper(),
            "Result": "🔴 Successful" if r["result"] == "success" else "🟢 Blocked",
            "Severity": r["severity"],
            "Details": r["details"],
        })

    st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

# ── Before/After Comparison ──
st.markdown("---")
st.markdown(section_title("Before & After Comparison", "🔀"), unsafe_allow_html=True)

comparison_table = {
    "Attack Type": [
        "Replay Attack", "Spoofing Attack", "Brute Force",
        "Flooding (DoS)", "Sniffing", "Tampering",
    ],
    "Without Security (Before)": [
        "Replayed messages accepted",
        "Fake device data accepted",
        "Unlimited password attempts",
        "All requests processed",
        "Data visible in plaintext",
        "Modified data accepted",
    ],
    "With Security (After)": [
        "Nonce + timestamp rejects replay",
        "HMAC rejects unauthenticated devices",
        "Account locked after 3 attempts",
        "Rate limiter drops excess traffic",
        "AES-256 encryption protects data",
        "HMAC detects data tampering",
    ],
    "Security Mechanism": [
        "Nonce & Timestamp", "HMAC Authentication",
        "Rate Limiting & Lockout", "IP-based Rate Limiting",
        "AES-256 Encryption", "HMAC Integrity",
    ],
}

st.dataframe(pd.DataFrame(comparison_table), use_container_width=True, hide_index=True)

# ── Attack Stats Chart ──
attack_stats = db.get_attack_stats()
if attack_stats:
    st.markdown(section_title("Attack Statistics", "📈"), unsafe_allow_html=True)

    df_stats = pd.DataFrame(attack_stats)

    fig = go.Figure()
    for result_type, color in [("blocked", "#10b981"), ("success", "#ef4444")]:
        filtered = df_stats[df_stats["result"] == result_type]
        if not filtered.empty:
            fig.add_trace(go.Bar(
                x=filtered["attack_type"],
                y=filtered["count"],
                name=result_type.capitalize(),
                marker_color=color,
            ))

    fig.update_layout(**plotly_theme(), barmode="group", height=400, yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)
