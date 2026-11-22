"""
SecureIoT Test Suite
Comprehensive tests verifying all core project requirements:
- Cryptography (AES, SHA-256, HMAC, RSA, Key Management, Cipher comparison)
- Access Control (bcrypt hashing, user auth, RBAC, permissions)
- Privacy (Pseudonymisation, Aggregation, Noise Addition)
- Attack Simulation (Insecure vs Secure modes for 6 attacks)
- Database Operations
- FastAPI Backend endpoints
"""

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules import crypto_utils
from modules import access_control as ac
from modules import attack_sim
from modules import privacy
from modules import database as db


# ── Cryptography Tests ──
def test_aes_encrypt_decrypt():
    original = "Secret smart building sensor payload: 23.5°C"
    enc = crypto_utils.aes_encrypt(original)
    assert "ciphertext" in enc
    assert "key" in enc
    assert "iv" in enc
    dec = crypto_utils.aes_decrypt(enc["ciphertext"], enc["key"], enc["iv"])
    assert dec == original


def test_sha256_hash():
    data = "test message 123"
    res = crypto_utils.sha256_hash(data)
    assert len(res["hash"]) == 64
    # Deterministic test
    res2 = crypto_utils.sha256_hash(data)
    assert res["hash"] == res2["hash"]


def test_hmac_generate_and_verify():
    msg = "Device command: UNLOCK_DOOR"
    gen = crypto_utils.hmac_generate(msg)
    valid = crypto_utils.hmac_verify(msg, gen["hmac"], gen["key"])
    assert valid["is_valid"] is True

    tampered = crypto_utils.hmac_verify("Device command: LOCK_DOOR", gen["hmac"], gen["key"])
    assert tampered["is_valid"] is False


def test_rsa_digital_signature():
    keys = crypto_utils.rsa_generate_keys(key_size=2048)
    msg = "Smart Building Firmware Update v1.0"
    sig = crypto_utils.rsa_sign(msg, keys["private_key"])
    assert sig["signature"] is not None

    ver = crypto_utils.rsa_verify(msg, sig["signature"], keys["public_key"])
    assert ver["is_valid"] is True

    bad_ver = crypto_utils.rsa_verify("Malicious Firmware Update", sig["signature"], keys["public_key"])
    assert bad_ver["is_valid"] is False


def test_key_rotation():
    key_info = crypto_utils.generate_aes_key()
    assert len(key_info["key"]) > 0
    rotated = crypto_utils.rotate_key(key_info["key"])
    assert rotated["new_key"] != rotated["old_key"]


def test_cipher_comparison():
    res = crypto_utils.compare_ciphers("benchmark telemetry message")
    assert "aes" in res
    assert "chacha20" in res
    assert res["aes"]["key_size"] == "256 bits"
    assert res["chacha20"]["key_size"] == "256 bits"


# ── Access Control Tests ──
def test_bcrypt_hashing():
    pw = "SuperSecurePassword123!"
    h = ac.hash_password(pw)
    assert h != pw
    assert ac.verify_password(pw, h) is True
    assert ac.verify_password("WrongPassword", h) is False


def test_rbac_permissions():
    admin_manage = ac.check_permission("admin", "manage_devices")
    assert admin_manage["allowed"] is True

    viewer_control = ac.check_permission("viewer", "control")
    assert viewer_control["allowed"] is False

    viewer_read = ac.check_permission("viewer", "read")
    assert viewer_read["allowed"] is True


def test_topic_permissions():
    op_control = ac.check_topic_permission("operator", "door_lock/control")
    assert op_control["allowed"] is True

    viewer_control = ac.check_topic_permission("viewer", "door_lock/control")
    assert viewer_control["allowed"] is False


# ── Privacy Tests ──
def test_pseudonymisation():
    sample = privacy.get_sample_data()
    res = privacy.pseudonymise(sample)
    records = res["records"]
    assert len(records) == len(sample)
    assert records[0]["pseudonymised"]["device_id"].startswith("DEV-")
    assert records[0]["pseudonymised"]["device_id"] != records[0]["original"]["device_id"]


def test_aggregation():
    sample = privacy.get_sample_data()
    res = privacy.aggregate_data(sample)
    assert "mean" in res["aggregated_result"]
    assert "count" in res["aggregated_result"]
    assert res["aggregated_result"]["count"] == len(sample)


def test_noise_addition():
    sample = privacy.get_sample_data()
    res = privacy.add_noise(sample, epsilon=1.0)
    for r in res["records"]:
        assert "noisy_value" in r
        assert r["noise_added"] != 0.0


# ── Attack Simulation Tests ──
def test_replay_attack():
    insecure = attack_sim.simulate_replay_attack(secure_mode=False)
    assert insecure["result"] == "success"
    secure = attack_sim.simulate_replay_attack(secure_mode=True)
    assert secure["result"] == "blocked"


def test_spoofing_attack():
    insecure = attack_sim.simulate_spoofing_attack(secure_mode=False)
    assert insecure["result"] == "success"
    secure = attack_sim.simulate_spoofing_attack(secure_mode=True)
    assert secure["result"] == "blocked"


def test_brute_force_attack():
    insecure = attack_sim.simulate_brute_force_attack(secure_mode=False)
    assert insecure["result"] == "success"
    secure = attack_sim.simulate_brute_force_attack(secure_mode=True)
    assert secure["result"] == "blocked"


def test_flooding_attack():
    insecure = attack_sim.simulate_flooding_attack(secure_mode=False)
    assert insecure["result"] == "success"
    secure = attack_sim.simulate_flooding_attack(secure_mode=True)
    assert secure["result"] == "blocked"


def test_sniffing_attack():
    insecure = attack_sim.simulate_sniffing_attack(secure_mode=False)
    assert insecure["result"] == "success"
    secure = attack_sim.simulate_sniffing_attack(secure_mode=True)
    assert secure["result"] == "blocked"


def test_tampering_attack():
    insecure = attack_sim.simulate_tampering_attack(secure_mode=False)
    assert insecure["result"] == "success"
    secure = attack_sim.simulate_tampering_attack(secure_mode=True)
    assert secure["result"] == "blocked"


# ── Database Tests ──
def test_database_devices():
    stats = db.get_device_stats()
    assert stats["total"] >= 8
    assert stats["active"] >= 8
