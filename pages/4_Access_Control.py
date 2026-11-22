"""
SecureIoT — Access Control & Privacy Page
RBAC, authentication, device management, and privacy techniques.
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from styles.theme import get_css, section_title
from modules import access_control as ac
from modules import privacy
from modules import database as db

st.set_page_config(page_title="Access Control & Privacy — SecureIoT", page_icon="🛡️", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div style="text-align:center;padding:10px 0;">
    <h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;">🛡️ Access Control & Privacy</h1>
    <p style="color:#64748b;">User authentication, role-based access, and data privacy techniques</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

tab_auth, tab_rbac, tab_device, tab_privacy = st.tabs([
    "🔐 Authentication", "👥 Role-Based Access", "📟 Device Management", "🔒 Privacy Techniques",
])

# ════════════════════════════════════════════
#  Authentication
# ════════════════════════════════════════════
with tab_auth:
    st.markdown(section_title("User Registration & Login", "🔐"), unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111a35;border:1px solid #1e293b;border-radius:10px;padding:16px;margin-bottom:16px;">
        <div style="color:#94a3b8;font-size:0.9rem;">
            Passwords are hashed with <strong style="color:#3b82f6;">bcrypt</strong> (12 salt rounds)
            before storage. Plaintext passwords are never stored in the database.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_reg, col_login = st.columns(2)

    with col_reg:
        st.markdown("#### 📝 Register New User")
        with st.form("register_form"):
            reg_user = st.text_input("Username", key="reg_user")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            reg_role = st.selectbox("Role", ["viewer", "operator", "admin"], key="reg_role")
            if st.form_submit_button("📝 Register", use_container_width=True):
                result = ac.register_user(reg_user, reg_pass, reg_role)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(result["message"])

    with col_login:
        st.markdown("#### 🔑 Login")
        with st.form("login_form"):
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            if st.form_submit_button("🔑 Login", use_container_width=True):
                result = ac.authenticate_user(login_user, login_pass)
                if result["success"]:
                    st.success(f"{result['message']} (Role: {result['role']})")
                else:
                    st.error(result["message"])

    # Show registered users
    st.markdown("---")
    st.markdown("#### 👥 Registered Users")
    users = db.get_all_users()
    if users:
        df_users = pd.DataFrame(users)
        st.dataframe(df_users, use_container_width=True, hide_index=True)
    else:
        st.info("No users registered yet. Use the form above to create users.")

    # Password hashing demo
    st.markdown("---")
    st.markdown("#### 🔏 Password Hashing Demonstration")
    demo_pass = st.text_input("Enter a password to hash:", value="MySecurePass123", key="demo_pass")
    if st.button("🔏 Hash with bcrypt", key="hash_demo"):
        hashed = ac.hash_password(demo_pass)
        st.code(f"Password:  {demo_pass}\nbcrypt:    {hashed}", language=None)
        st.info("Each time you hash the same password, bcrypt produces a different hash (due to random salt) — but verification still works!")

        # Verify
        is_valid = ac.verify_password(demo_pass, hashed)
        st.success(f"Verification: {'✅ Match' if is_valid else '❌ No Match'}")

# ════════════════════════════════════════════
#  Role-Based Access Control
# ════════════════════════════════════════════
with tab_rbac:
    st.markdown(section_title("Role-Based Access Control (RBAC)", "👥"), unsafe_allow_html=True)

    # Roles comparison table
    st.markdown("#### Permission Matrix")
    comparison = ac.get_all_roles_comparison()
    df_comp = pd.DataFrame(comparison)
    df_comp.columns = ["Action", "Admin", "Operator", "Viewer"]
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # Test a permission
    st.markdown("---")
    st.markdown("#### 🧪 Test Permission")
    col1, col2, col3 = st.columns(3)
    with col1:
        test_role = st.selectbox("Role:", ["admin", "operator", "viewer"], key="test_role")
    with col2:
        test_action = st.selectbox("Action:", ["read", "write", "control", "manage_users", "manage_devices", "view_logs"], key="test_action")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧪 Check", use_container_width=True, key="check_perm"):
            result = ac.check_permission(test_role, test_action)
            if result["allowed"]:
                st.success(result["status"])
            else:
                st.error(result["status"])

    # Topic-level permissions
    st.markdown("---")
    st.markdown("#### 📋 Topic-Level Permissions")
    st.markdown("*Each device type has granular read/write/control permissions per role:*")
    topic_perms = ac.get_topic_permissions_table()
    df_topics = pd.DataFrame(topic_perms)
    df_topics.columns = ["Topic", "Admin", "Operator", "Viewer"]
    st.dataframe(df_topics, use_container_width=True, hide_index=True)

    # Test topic permission
    col1, col2, col3 = st.columns(3)
    with col1:
        t_role = st.selectbox("Role:", ["admin", "operator", "viewer"], key="topic_role")
    with col2:
        t_topic = st.selectbox("Topic:", [
            "temperature/read", "temperature/write", "temperature/control",
            "door_lock/read", "door_lock/write", "door_lock/control",
            "energy/read", "energy/write", "energy/control",
            "motion/read", "motion/write", "motion/control",
        ], key="topic_topic")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧪 Check Topic", use_container_width=True, key="check_topic"):
            result = ac.check_topic_permission(t_role, t_topic)
            if result["allowed"]:
                st.success(result["status"])
            else:
                st.error(result["status"])

# ════════════════════════════════════════════
#  Device Management
# ════════════════════════════════════════════
with tab_device:
    st.markdown(section_title("Device Registration & Revocation", "📟"), unsafe_allow_html=True)

    col_reg, col_revoke = st.columns(2)

    with col_reg:
        st.markdown("#### ➕ Register Device")
        with st.form("device_reg_form"):
            d_id = st.text_input("Device ID", value="TEMP-010", key="dreg_id")
            d_name = st.text_input("Device Name", value="New Temp Sensor", key="dreg_name")
            d_type = st.selectbox("Type", ["temperature", "door_lock", "energy", "motion"], key="dreg_type")
            d_loc = st.text_input("Location", value="Floor 3", key="dreg_loc")
            if st.form_submit_button("➕ Register Device", use_container_width=True):
                result = ac.register_device(d_id, d_name, d_type, d_loc)
                st.success(result["message"])

    with col_revoke:
        st.markdown("#### ❌ Revoke Device")
        devices = db.get_all_devices()
        active_devices = [d for d in devices if d["status"] == "active"]
        if active_devices:
            dev_options = {f"{d['id']} — {d['name']}": d["id"] for d in active_devices}
            selected = st.selectbox("Select device to revoke:", list(dev_options.keys()), key="revoke_sel")
            if st.button("❌ Revoke Device", use_container_width=True, key="revoke_btn"):
                device_id = dev_options[selected]
                result = ac.revoke_device(device_id)
                st.success(result["message"])
                st.rerun()
        else:
            st.info("No active devices to revoke.")

    # Device list
    st.markdown("---")
    st.markdown("#### 📋 All Registered Devices")
    devices = db.get_all_devices()
    if devices:
        df_dev = pd.DataFrame(devices)[["id", "name", "type", "location", "status", "reading"]]
        df_dev.columns = ["ID", "Name", "Type", "Location", "Status", "Reading"]
        st.dataframe(df_dev, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════
#  Privacy Techniques
# ════════════════════════════════════════════
with tab_privacy:
    st.markdown(section_title("Data Privacy Techniques", "🔒"), unsafe_allow_html=True)

    sample_data = privacy.get_sample_data()

    st.markdown("#### 📊 Original Data (Before Privacy)")
    st.dataframe(pd.DataFrame(sample_data), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Pseudonymisation ──
    st.markdown("#### 1️⃣ Pseudonymisation")
    if st.button("🔀 Apply Pseudonymisation", use_container_width=True, key="pseudo_btn"):
        result = privacy.pseudonymise(sample_data)
        st.info(result["description"])
        before_after = []
        for r in result["records"]:
            before_after.append({
                "Original Device ID": r["original"]["device_id"],
                "Pseudonym ID": r["pseudonymised"]["device_id"],
                "Original Location": r["original"]["location"],
                "Pseudonym Location": r["pseudonymised"]["location"],
                "Value (unchanged)": r["original"]["value"],
            })
        st.dataframe(pd.DataFrame(before_after), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Aggregation ──
    st.markdown("#### 2️⃣ Data Aggregation")
    if st.button("📊 Apply Aggregation", use_container_width=True, key="agg_btn"):
        result = privacy.aggregate_data(sample_data)
        st.info(result["description"])

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Individual Records (Before):**")
            st.dataframe(pd.DataFrame(result["individual_records"]), use_container_width=True, hide_index=True)
        with col2:
            st.markdown("**Aggregated Result (After):**")
            agg = result["aggregated_result"]
            for key, val in agg.items():
                st.metric(key.replace("_", " ").title(), val)

    st.markdown("---")

    # ── Noise Addition ──
    st.markdown("#### 3️⃣ Noise Addition (Differential Privacy)")
    epsilon = st.slider("Privacy parameter (ε) — lower = more privacy:", 0.1, 5.0, 1.0, 0.1, key="epsilon")
    if st.button("🎲 Add Noise", use_container_width=True, key="noise_btn"):
        result = privacy.add_noise(sample_data, epsilon=epsilon)
        st.info(result["description"])
        df_noise = pd.DataFrame(result["records"])
        df_noise.columns = ["Device ID", "Original Value", "Noise Added", "Noisy Value"]
        st.dataframe(df_noise, use_container_width=True, hide_index=True)
