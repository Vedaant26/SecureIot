"""
SecureIoT — Cryptography Page
Interactive demonstrations of AES, SHA-256, HMAC, RSA, key management.
"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from styles.theme import get_css, section_title
from modules import crypto_utils
from modules import database as db

st.set_page_config(page_title="Cryptography — SecureIoT", page_icon="🔐", layout="wide")
st.markdown(get_css(), unsafe_allow_html=True)

# ── Header ──
st.markdown("""
<div style="text-align:center;padding:10px 0;">
    <h1 style="color:#e2e8f0;font-size:2rem;font-weight:700;">🔐 Cryptography</h1>
    <p style="color:#64748b;">Interactive cryptographic operations for IoT security</p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Tabs ──
tab_aes, tab_hash, tab_hmac, tab_rsa, tab_keys, tab_compare = st.tabs([
    "🔒 AES Encryption", "🔑 SHA-256 Hash", "✅ HMAC Integrity",
    "📝 RSA Signatures", "🔄 Key Management", "📊 Cipher Comparison",
])

# ════════════════════════════════════════════
#  AES Encryption
# ════════════════════════════════════════════
with tab_aes:
    st.markdown(section_title("AES-256 Encryption & Decryption", "🔒"), unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111a35;border:1px solid #1e293b;border-radius:10px;padding:16px;margin-bottom:16px;">
        <div style="color:#94a3b8;font-size:0.9rem;">
            <strong style="color:#3b82f6;">AES-256-CBC</strong> is a symmetric block cipher that encrypts data in 128-bit blocks
            using a 256-bit key. It is the industry standard for protecting IoT data at rest and in transit.
        </div>
    </div>
    """, unsafe_allow_html=True)

    aes_input = st.text_area("Enter plaintext to encrypt:", value='{"device":"TEMP-001","temperature":23.5,"location":"Lobby"}', height=80, key="aes_input")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔒 Encrypt", use_container_width=True, key="aes_encrypt"):
            result = crypto_utils.aes_encrypt(aes_input)
            st.session_state["aes_result"] = result
            db.log_security_event("encryption", "info", "AES-256 encryption performed", "crypto-module")
            st.success("✅ Encryption successful!")
            st.code(f"Ciphertext: {result['ciphertext']}", language=None)
            st.code(f"Key (B64):  {result['key']}", language=None)
            st.code(f"IV (B64):   {result['iv']}", language=None)
            st.info(f"Algorithm: {result['algorithm']} | Key Size: {result['key_size']}")

    with col2:
        if st.button("🔓 Decrypt", use_container_width=True, key="aes_decrypt"):
            if "aes_result" in st.session_state:
                r = st.session_state["aes_result"]
                plaintext = crypto_utils.aes_decrypt(r["ciphertext"], r["key"], r["iv"])
                st.success("✅ Decryption successful!")
                st.code(f"Plaintext: {plaintext}", language=None)
            else:
                st.warning("⚠️ Encrypt something first!")

# ════════════════════════════════════════════
#  SHA-256 Hashing
# ════════════════════════════════════════════
with tab_hash:
    st.markdown(section_title("SHA-256 Hashing", "🔑"), unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111a35;border:1px solid #1e293b;border-radius:10px;padding:16px;margin-bottom:16px;">
        <div style="color:#94a3b8;font-size:0.9rem;">
            <strong style="color:#3b82f6;">SHA-256</strong> produces a fixed 256-bit hash from any input.
            It is a one-way function — the original data cannot be recovered from the hash.
            Used for password storage, data integrity verification, and digital fingerprinting.
        </div>
    </div>
    """, unsafe_allow_html=True)

    hash_input = st.text_input("Enter data to hash:", value="IoT sensor data: temperature=23.5", key="hash_input")

    if st.button("🔑 Compute SHA-256 Hash", use_container_width=True, key="hash_btn"):
        result = crypto_utils.sha256_hash(hash_input)
        st.code(f"Input:       {result['input']}", language=None)
        st.code(f"SHA-256:     {result['hash']}", language=None)
        st.info(f"Hash Length: {result['hash_length']}")

        # Demonstrate avalanche effect
        modified = hash_input + "."
        result2 = crypto_utils.sha256_hash(modified)
        st.markdown("#### Avalanche Effect")
        st.markdown("*Changing just one character produces a completely different hash:*")
        st.code(f"Modified:    {modified}", language=None)
        st.code(f"New Hash:    {result2['hash']}", language=None)
        matching = sum(1 for a, b in zip(result["hash"], result2["hash"]) if a == b)
        st.info(f"Only {matching}/64 hex characters match — demonstrating the avalanche effect.")

# ════════════════════════════════════════════
#  HMAC Integrity
# ════════════════════════════════════════════
with tab_hmac:
    st.markdown(section_title("HMAC Integrity Verification", "✅"), unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111a35;border:1px solid #1e293b;border-radius:10px;padding:16px;margin-bottom:16px;">
        <div style="color:#94a3b8;font-size:0.9rem;">
            <strong style="color:#3b82f6;">HMAC-SHA256</strong> uses a secret key with SHA-256 to create a
            message authentication code. If even one byte of the message changes, the HMAC will not match —
            proving the message has been tampered with.
        </div>
    </div>
    """, unsafe_allow_html=True)

    hmac_msg = st.text_input("Message:", value='{"device":"LOCK-001","command":"unlock"}', key="hmac_msg")

    if st.button("🔏 Generate HMAC", use_container_width=True, key="hmac_gen"):
        result = crypto_utils.hmac_generate(hmac_msg)
        st.session_state["hmac_result"] = result
        st.success("✅ HMAC generated!")
        st.code(f"HMAC:  {result['hmac']}", language=None)
        st.code(f"Key:   {result['key']}", language=None)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Verify (Original Message)", use_container_width=True, key="hmac_verify_ok"):
            if "hmac_result" in st.session_state:
                r = st.session_state["hmac_result"]
                v = crypto_utils.hmac_verify(r["message"], r["hmac"], r["key"])
                if v["is_valid"]:
                    st.success(v["status"])
                else:
                    st.error(v["status"])
            else:
                st.warning("⚠️ Generate an HMAC first!")

    with col2:
        if st.button("❌ Verify (Tampered Message)", use_container_width=True, key="hmac_verify_bad"):
            if "hmac_result" in st.session_state:
                r = st.session_state["hmac_result"]
                tampered = r["message"].replace("unlock", "UNLOCK_ALL")
                v = crypto_utils.hmac_verify(tampered, r["hmac"], r["key"])
                st.error(v["status"])
                st.code(f"Original: {r['message']}\nTampered: {tampered}", language=None)
            else:
                st.warning("⚠️ Generate an HMAC first!")

# ════════════════════════════════════════════
#  RSA Digital Signatures
# ════════════════════════════════════════════
with tab_rsa:
    st.markdown(section_title("RSA Digital Signatures", "📝"), unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111a35;border:1px solid #1e293b;border-radius:10px;padding:16px;margin-bottom:16px;">
        <div style="color:#94a3b8;font-size:0.9rem;">
            <strong style="color:#3b82f6;">RSA-PSS</strong> uses a private key to sign a message and a
            public key to verify it. This proves the message was sent by the key owner
            and was not modified — providing authentication and non-repudiation.
        </div>
    </div>
    """, unsafe_allow_html=True)

    rsa_msg = st.text_input("Message to sign:", value="Firmware update v2.1 — checksum verified", key="rsa_msg")

    if st.button("🔑 Generate RSA Keys & Sign", use_container_width=True, key="rsa_sign"):
        with st.spinner("Generating 2048-bit RSA keys..."):
            keys = crypto_utils.rsa_generate_keys()
            sig = crypto_utils.rsa_sign(rsa_msg, keys["private_key"])
            st.session_state["rsa_keys"] = keys
            st.session_state["rsa_sig"] = sig

        st.success("✅ Keys generated and message signed!")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Public Key (first 3 lines):**")
            pub_lines = keys["public_key"].strip().split("\n")[:3]
            st.code("\n".join(pub_lines) + "\n...", language=None)
        with col2:
            st.markdown("**Signature:**")
            st.code(sig["signature"][:80] + "...", language=None)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Verify Signature", use_container_width=True, key="rsa_verify_ok"):
            if "rsa_keys" in st.session_state:
                v = crypto_utils.rsa_verify(rsa_msg, st.session_state["rsa_sig"]["signature"], st.session_state["rsa_keys"]["public_key"])
                if v["is_valid"]:
                    st.success(v["status"])
                else:
                    st.error(v["status"])
            else:
                st.warning("⚠️ Generate keys and sign first!")

    with col2:
        if st.button("❌ Verify with Wrong Message", use_container_width=True, key="rsa_verify_bad"):
            if "rsa_keys" in st.session_state:
                v = crypto_utils.rsa_verify("TAMPERED MESSAGE", st.session_state["rsa_sig"]["signature"], st.session_state["rsa_keys"]["public_key"])
                st.error(v["status"])
            else:
                st.warning("⚠️ Generate keys and sign first!")

# ════════════════════════════════════════════
#  Key Management
# ════════════════════════════════════════════
with tab_keys:
    st.markdown(section_title("Key Generation & Rotation", "🔄"), unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111a35;border:1px solid #1e293b;border-radius:10px;padding:16px;margin-bottom:16px;">
        <div style="color:#94a3b8;font-size:0.9rem;">
            <strong style="color:#3b82f6;">Key Management</strong> ensures encryption keys are regularly
            generated and rotated. Old keys are replaced to limit exposure if a key is compromised.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Generate New AES Key", use_container_width=True, key="keygen"):
            key_info = crypto_utils.generate_aes_key()
            st.session_state["current_key"] = key_info
            st.success("✅ New AES-256 key generated!")
            st.code(f"Key:       {key_info['key']}", language=None)
            st.code(f"Algorithm: {key_info['algorithm']}", language=None)
            st.code(f"Size:      {key_info['size']}", language=None)
            st.code(f"Generated: {key_info['generated_at']}", language=None)
            db.log_security_event("key_generated", "info", "New AES-256 key generated", "crypto-module")

    with col2:
        if st.button("🔄 Rotate Key", use_container_width=True, key="keyrotate"):
            if "current_key" in st.session_state:
                rotation = crypto_utils.rotate_key(st.session_state["current_key"]["key"])
                st.session_state["current_key"]["key"] = rotation["new_key"]
                st.success("✅ Key rotated!")
                st.code(f"Old Key: {rotation['old_key'][:40]}...", language=None)
                st.code(f"New Key: {rotation['new_key'][:40]}...", language=None)
                st.info(rotation["note"])
                db.log_security_event("key_rotated", "info", "AES key rotated", "crypto-module")
            else:
                st.warning("⚠️ Generate a key first!")

    # Challenge-Response Demo
    st.markdown("---")
    st.markdown(section_title("Challenge-Response Authentication", "🤝"), unsafe_allow_html=True)

    if st.button("▶ Run Challenge-Response Demo", use_container_width=True, key="challenge"):
        result = crypto_utils.challenge_response_demo()
        st.success(result["status"])

        for step in result["steps"]:
            st.markdown(f"- {step}")

        st.markdown("**Details:**")
        st.code(f"Challenge:       {result['challenge']}", language=None)
        st.code(f"Client Response: {result['client_response'][:50]}...", language=None)
        st.code(f"Server Computed: {result['server_computed'][:50]}...", language=None)
        st.code(f"Match:           {result['match']}", language=None)

# ════════════════════════════════════════════
#  Cipher Comparison
# ════════════════════════════════════════════
with tab_compare:
    st.markdown(section_title("Cipher Comparison: AES vs ChaCha20", "📊"), unsafe_allow_html=True)

    compare_input = st.text_input("Text to encrypt with both ciphers:", value="Smart building sensor data: temp=23.5, humidity=45%", key="compare_input")

    if st.button("📊 Compare Ciphers", use_container_width=True, key="compare_btn"):
        result = crypto_utils.compare_ciphers(compare_input)

        col1, col2 = st.columns(2)
        with col1:
            aes = result["aes"]
            st.markdown(f"""
            <div style="background:#111a35;border:1px solid #3b82f6;border-radius:10px;padding:20px;">
                <div style="color:#3b82f6;font-weight:700;font-size:1.1rem;margin-bottom:12px;">
                    🔒 {aes['algorithm']}
                </div>
                <div style="color:#94a3b8;font-size:0.85rem;line-height:1.8;">
                    Type: {aes['type']}<br>
                    Key Size: {aes['key_size']}<br>
                    Block Size: {aes['block_size']}<br>
                    Padding: {aes['padding']}<br>
                    Output Size: {aes['ciphertext_length']} bytes<br>
                    Time: {aes['time_ms']} ms
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            cc = result["chacha20"]
            st.markdown(f"""
            <div style="background:#111a35;border:1px solid #10b981;border-radius:10px;padding:20px;">
                <div style="color:#10b981;font-weight:700;font-size:1.1rem;margin-bottom:12px;">
                    🔐 {cc['algorithm']}
                </div>
                <div style="color:#94a3b8;font-size:0.85rem;line-height:1.8;">
                    Type: {cc['type']}<br>
                    Key Size: {cc['key_size']}<br>
                    Block Size: {cc['block_size']}<br>
                    Padding: {cc['padding']}<br>
                    Output Size: {cc['ciphertext_length']} bytes<br>
                    Time: {cc['time_ms']} ms
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Comparison table
        st.markdown("<br>", unsafe_allow_html=True)
        comp_df = pd.DataFrame({
            "Property": ["Type", "Key Size", "Block Size", "Padding", "Output Size", "Speed"],
            "AES-256-CBC": [aes["type"], aes["key_size"], aes["block_size"], aes["padding"], f"{aes['ciphertext_length']} bytes", f"{aes['time_ms']} ms"],
            "ChaCha20": [cc["type"], cc["key_size"], cc["block_size"], cc["padding"], f"{cc['ciphertext_length']} bytes", f"{cc['time_ms']} ms"],
        })
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
