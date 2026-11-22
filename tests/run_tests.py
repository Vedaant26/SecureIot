"""
Simple Test Runner for SecureIoT
Runs test functions directly without requiring external pytest installation.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tests.test_all import (
    test_aes_encrypt_decrypt,
    test_sha256_hash,
    test_hmac_generate_and_verify,
    test_rsa_digital_signature,
    test_key_rotation,
    test_cipher_comparison,
    test_bcrypt_hashing,
    test_rbac_permissions,
    test_topic_permissions,
    test_pseudonymisation,
    test_aggregation,
    test_noise_addition,
    test_replay_attack,
    test_spoofing_attack,
    test_brute_force_attack,
    test_flooding_attack,
    test_sniffing_attack,
    test_tampering_attack,
    test_database_devices,
)

TESTS = [
    ("AES Encryption/Decryption", test_aes_encrypt_decrypt),
    ("SHA-256 Hashing", test_sha256_hash),
    ("HMAC Integrity & Auth", test_hmac_generate_and_verify),
    ("RSA-2048 Digital Signatures", test_rsa_digital_signature),
    ("Key Management & Rotation", test_key_rotation),
    ("Cipher Comparison (AES vs ChaCha20)", test_cipher_comparison),
    ("bcrypt Password Hashing", test_bcrypt_hashing),
    ("RBAC Policy Matrix", test_rbac_permissions),
    ("Topic-Level Permissions", test_topic_permissions),
    ("Privacy: Pseudonymisation", test_pseudonymisation),
    ("Privacy: Data Aggregation", test_aggregation),
    ("Privacy: Laplace Noise Addition", test_noise_addition),
    ("Attack Sim: Replay Attack", test_replay_attack),
    ("Attack Sim: Spoofing Attack", test_spoofing_attack),
    ("Attack Sim: Brute Force Attack", test_brute_force_attack),
    ("Attack Sim: Flooding (DoS) Attack", test_flooding_attack),
    ("Attack Sim: Sniffing Attack", test_sniffing_attack),
    ("Attack Sim: Tampering Attack", test_tampering_attack),
    ("Database Operations & 8 Devices", test_database_devices),
]

def run():
    passed = 0
    failed = 0
    print("=" * 60)
    print(" 🛡️ SecureIoT Automated Test Suite")
    print("=" * 60)
    for name, test_func in TESTS:
        try:
            test_func()
            print(f" ✅ PASS: {name}")
            passed += 1
        except Exception as e:
            print(f" ❌ FAIL: {name} -> {e}")
            failed += 1

    print("=" * 60)
    print(f" Summary: {passed} passed, {failed} failed out of {len(TESTS)} tests")
    print("=" * 60)
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run()
