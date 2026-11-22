"""
SecureIoT Attack Simulation Module
Simulates 6 common IoT attacks in insecure and secure modes.
"""

import time
import random
import hashlib
import hmac as hmac_lib
import os
import base64
from modules import database as db


def _timestamp():
    return time.strftime("%H:%M:%S")


# ════════════════════════════════════════════
#  1. Replay Attack
# ════════════════════════════════════════════

def simulate_replay_attack(secure_mode=False):
    """
    Replay Attack: Attacker captures a legitimate message and re-sends it.
    Secure mode: Uses timestamp + nonce to detect replayed messages.
    """
    original_msg = '{"device":"TEMP-001","cmd":"set_temp","value":25}'
    steps = []

    if not secure_mode:
        steps.append(f"[{_timestamp()}] 📡 Legitimate message sent: {original_msg}")
        steps.append(f"[{_timestamp()}] 🕵️ Attacker captures the message")
        time.sleep(0.1)
        steps.append(f"[{_timestamp()}] 🔄 Attacker replays the captured message")
        steps.append(f"[{_timestamp()}] ✅ Server accepts the replayed message — ATTACK SUCCESSFUL")
        result = {
            "attack_type": "Replay Attack",
            "mode": "insecure",
            "result": "success",
            "severity": "High",
            "steps": steps,
            "details": "No timestamp or nonce validation — replayed message was accepted.",
            "impact": "Attacker can repeat commands (e.g., unlock door) without authorisation.",
        }
    else:
        nonce = base64.b64encode(os.urandom(8)).decode()
        timestamp = str(int(time.time()))
        secured_msg = f'{original_msg}|nonce={nonce}|ts={timestamp}'
        steps.append(f"[{_timestamp()}] 📡 Secure message sent with nonce and timestamp")
        steps.append(f"[{_timestamp()}]    Nonce: {nonce}")
        steps.append(f"[{_timestamp()}]    Timestamp: {timestamp}")
        steps.append(f"[{_timestamp()}] 🕵️ Attacker captures and replays the message")
        time.sleep(0.1)
        steps.append(f"[{_timestamp()}] 🛡️ Server checks: nonce already used? YES")
        steps.append(f"[{_timestamp()}] 🛡️ Server checks: timestamp expired? YES")
        steps.append(f"[{_timestamp()}] ❌ Server REJECTS the replayed message — ATTACK BLOCKED")
        result = {
            "attack_type": "Replay Attack",
            "mode": "secure",
            "result": "blocked",
            "severity": "High",
            "steps": steps,
            "details": "Timestamp and nonce validation detected the replay attempt.",
            "defense": "Each message includes a unique nonce and timestamp; server rejects duplicates.",
        }

    db.log_attack(result["attack_type"], result["mode"], result["result"], result["details"])
    return result


# ════════════════════════════════════════════
#  2. Spoofing Attack
# ════════════════════════════════════════════

def simulate_spoofing_attack(secure_mode=False):
    """
    Spoofing Attack: Attacker pretends to be a legitimate device.
    Secure mode: Uses HMAC authentication to verify device identity.
    """
    fake_device_id = "TEMP-001"
    fake_msg = '{"device":"TEMP-001","temp":99.9}'
    steps = []

    if not secure_mode:
        steps.append(f"[{_timestamp()}] 🎭 Attacker sends message as device {fake_device_id}")
        steps.append(f"[{_timestamp()}]    Fake data: {fake_msg}")
        steps.append(f"[{_timestamp()}] ✅ Server accepts data from unverified source — ATTACK SUCCESSFUL")
        result = {
            "attack_type": "Spoofing Attack",
            "mode": "insecure",
            "result": "success",
            "severity": "High",
            "steps": steps,
            "details": "No device authentication — fake device data was accepted.",
            "impact": "Attacker injects false sensor data, causing wrong decisions.",
        }
    else:
        secret_key = os.urandom(32)
        real_hmac = hmac_lib.new(secret_key, fake_msg.encode(), hashlib.sha256).hexdigest()
        fake_hmac = hashlib.sha256(b"attacker_does_not_know_key").hexdigest()

        steps.append(f"[{_timestamp()}] 🎭 Attacker sends spoofed message as {fake_device_id}")
        steps.append(f"[{_timestamp()}]    Attacker HMAC: {fake_hmac[:32]}...")
        steps.append(f"[{_timestamp()}] 🛡️ Server computes expected HMAC: {real_hmac[:32]}...")
        steps.append(f"[{_timestamp()}] 🛡️ HMAC mismatch detected!")
        steps.append(f"[{_timestamp()}] ❌ Server REJECTS spoofed message — ATTACK BLOCKED")
        result = {
            "attack_type": "Spoofing Attack",
            "mode": "secure",
            "result": "blocked",
            "severity": "High",
            "steps": steps,
            "details": "HMAC authentication detected the spoofed identity.",
            "defense": "Each device has a shared secret; messages are HMAC-signed for authentication.",
        }

    db.log_attack(result["attack_type"], result["mode"], result["result"], result["details"])
    return result


# ════════════════════════════════════════════
#  3. Brute Force Attack
# ════════════════════════════════════════════

def simulate_brute_force_attack(secure_mode=False):
    """
    Brute Force Attack: Attacker tries many passwords to gain access.
    Secure mode: Rate limiting + account lockout after 3 failed attempts.
    """
    target_user = "admin"
    passwords = ["123456", "password", "admin", "admin123", "letmein", "qwerty", "root", "test"]
    correct_pw = "S3cur3!IoT#2024"
    steps = []

    if not secure_mode:
        for i, pw in enumerate(passwords):
            steps.append(f"[{_timestamp()}] 🔑 Attempt {i+1}: Trying '{pw}' → Failed")
            time.sleep(0.02)
        steps.append(f"[{_timestamp()}] 🔑 Attempt {len(passwords)+1}: Trying '{correct_pw}' → Success!")
        steps.append(f"[{_timestamp()}] ✅ Attacker gained access — ATTACK SUCCESSFUL")
        result = {
            "attack_type": "Brute Force Attack",
            "mode": "insecure",
            "result": "success",
            "severity": "Critical",
            "steps": steps,
            "details": f"No rate limiting — attacker tried {len(passwords)+1} passwords and gained access.",
            "impact": "Full system access with admin privileges.",
        }
    else:
        max_attempts = 3
        for i, pw in enumerate(passwords[:max_attempts]):
            steps.append(f"[{_timestamp()}] 🔑 Attempt {i+1}: Trying '{pw}' → Failed")
            time.sleep(0.02)
        steps.append(f"[{_timestamp()}] 🛡️ Rate limiter: {max_attempts} failed attempts detected")
        steps.append(f"[{_timestamp()}] 🛡️ Account '{target_user}' LOCKED for 15 minutes")
        steps.append(f"[{_timestamp()}] 🛡️ Alert sent to administrator")
        steps.append(f"[{_timestamp()}] ❌ Further attempts blocked — ATTACK BLOCKED")
        result = {
            "attack_type": "Brute Force Attack",
            "mode": "secure",
            "result": "blocked",
            "severity": "Critical",
            "steps": steps,
            "details": f"Rate limiting locked the account after {max_attempts} failed attempts.",
            "defense": "Rate limiting (3 attempts max) + account lockout + admin alerts.",
        }

    db.log_attack(result["attack_type"], result["mode"], result["result"], result["details"])
    return result


# ════════════════════════════════════════════
#  4. Flooding (DoS) Attack
# ════════════════════════════════════════════

def simulate_flooding_attack(secure_mode=False):
    """
    Flooding / DoS Attack: Attacker sends massive traffic to overwhelm the server.
    Secure mode: Rate limiting drops excessive requests.
    """
    num_requests = 50
    steps = []

    if not secure_mode:
        steps.append(f"[{_timestamp()}] 🌊 Attacker begins flooding — sending {num_requests} requests/sec")
        accepted = 0
        for i in range(num_requests):
            accepted += 1
        steps.append(f"[{_timestamp()}] 📥 Server accepted all {accepted} requests")
        steps.append(f"[{_timestamp()}] 💀 Server resources exhausted — legitimate users denied service")
        steps.append(f"[{_timestamp()}] ✅ Denial of Service achieved — ATTACK SUCCESSFUL")
        result = {
            "attack_type": "Flooding (DoS) Attack",
            "mode": "insecure",
            "result": "success",
            "severity": "High",
            "steps": steps,
            "details": f"All {num_requests} requests accepted — no rate limiting.",
            "impact": "Server becomes unresponsive to legitimate users.",
        }
    else:
        rate_limit = 10
        steps.append(f"[{_timestamp()}] 🌊 Attacker begins flooding — sending {num_requests} requests/sec")
        steps.append(f"[{_timestamp()}] 🛡️ Rate limiter active: max {rate_limit} requests/sec per IP")
        accepted = rate_limit
        dropped = num_requests - rate_limit
        steps.append(f"[{_timestamp()}] ✅ Accepted: {accepted} requests (within limit)")
        steps.append(f"[{_timestamp()}] 🚫 Dropped: {dropped} requests (over limit)")
        steps.append(f"[{_timestamp()}] 🛡️ Attacker IP added to temporary blacklist")
        steps.append(f"[{_timestamp()}] ❌ Server remains operational — ATTACK BLOCKED")
        result = {
            "attack_type": "Flooding (DoS) Attack",
            "mode": "secure",
            "result": "blocked",
            "severity": "High",
            "steps": steps,
            "details": f"Rate limiter accepted {accepted}, dropped {dropped} out of {num_requests} requests.",
            "defense": "Per-IP rate limiting + temporary IP blacklisting.",
        }

    db.log_attack(result["attack_type"], result["mode"], result["result"], result["details"])
    return result


# ════════════════════════════════════════════
#  5. Sniffing Attack
# ════════════════════════════════════════════

def simulate_sniffing_attack(secure_mode=False):
    """
    Sniffing Attack: Attacker intercepts network traffic to read data.
    Secure mode: AES encryption makes intercepted data unreadable.
    """
    sensitive_data = '{"device":"LOCK-001","action":"unlock","pin":"4829"}'
    steps = []

    if not secure_mode:
        steps.append(f"[{_timestamp()}] 📡 IoT device sends data in plaintext")
        steps.append(f"[{_timestamp()}]    Data: {sensitive_data}")
        steps.append(f"[{_timestamp()}] 🕵️ Attacker intercepts the network traffic")
        steps.append(f"[{_timestamp()}] 👁️ Attacker reads: {sensitive_data}")
        steps.append(f"[{_timestamp()}] ✅ Sensitive data exposed — ATTACK SUCCESSFUL")
        result = {
            "attack_type": "Sniffing Attack",
            "mode": "insecure",
            "result": "success",
            "severity": "Critical",
            "steps": steps,
            "details": "Data sent in plaintext — attacker read the door PIN.",
            "impact": "Credentials, PINs, and sensitive commands exposed.",
        }
    else:
        from modules.crypto_utils import aes_encrypt
        encrypted = aes_encrypt(sensitive_data)
        steps.append(f"[{_timestamp()}] 📡 IoT device encrypts data with AES-256 before sending")
        steps.append(f"[{_timestamp()}] 🕵️ Attacker intercepts the network traffic")
        steps.append(f"[{_timestamp()}] 👁️ Attacker sees: {encrypted['ciphertext'][:50]}...")
        steps.append(f"[{_timestamp()}] 🔒 Data is encrypted — attacker cannot read it")
        steps.append(f"[{_timestamp()}] ❌ Sensitive data protected — ATTACK BLOCKED")
        result = {
            "attack_type": "Sniffing Attack",
            "mode": "secure",
            "result": "blocked",
            "severity": "Critical",
            "steps": steps,
            "details": "AES-256 encryption made intercepted data unreadable.",
            "defense": "All IoT data is encrypted with AES-256-CBC before transmission.",
        }

    db.log_attack(result["attack_type"], result["mode"], result["result"], result["details"])
    return result


# ════════════════════════════════════════════
#  6. Tampering Attack
# ════════════════════════════════════════════

def simulate_tampering_attack(secure_mode=False):
    """
    Tampering Attack: Attacker modifies data in transit.
    Secure mode: HMAC integrity check detects modification.
    """
    original_msg = '{"device":"ENERGY-001","reading":2.4}'
    tampered_msg = '{"device":"ENERGY-001","reading":0.0}'
    steps = []

    if not secure_mode:
        steps.append(f"[{_timestamp()}] 📡 Original message: {original_msg}")
        steps.append(f"[{_timestamp()}] 🕵️ Attacker intercepts and modifies the message")
        steps.append(f"[{_timestamp()}] ✏️  Tampered message: {tampered_msg}")
        steps.append(f"[{_timestamp()}] ✅ Server accepts tampered data — ATTACK SUCCESSFUL")
        result = {
            "attack_type": "Tampering Attack",
            "mode": "insecure",
            "result": "success",
            "severity": "High",
            "steps": steps,
            "details": "No integrity check — tampered energy reading was accepted.",
            "impact": "False sensor data leads to incorrect billing or decisions.",
        }
    else:
        key = os.urandom(32)
        original_hmac = hmac_lib.new(key, original_msg.encode(), hashlib.sha256).hexdigest()
        tampered_hmac_check = hmac_lib.new(key, tampered_msg.encode(), hashlib.sha256).hexdigest()

        steps.append(f"[{_timestamp()}] 📡 Original message sent with HMAC: {original_hmac[:32]}...")
        steps.append(f"[{_timestamp()}] 🕵️ Attacker modifies the message to: {tampered_msg}")
        steps.append(f"[{_timestamp()}] 🛡️ Server recomputes HMAC of received message: {tampered_hmac_check[:32]}...")
        steps.append(f"[{_timestamp()}] 🛡️ HMAC mismatch! Original ≠ received")
        steps.append(f"[{_timestamp()}] ❌ Server REJECTS tampered data — ATTACK BLOCKED")
        result = {
            "attack_type": "Tampering Attack",
            "mode": "secure",
            "result": "blocked",
            "severity": "High",
            "steps": steps,
            "details": "HMAC integrity check detected data modification.",
            "defense": "HMAC-SHA256 attached to every message verifies data integrity.",
        }

    db.log_attack(result["attack_type"], result["mode"], result["result"], result["details"])
    return result


# ════════════════════════════════════════════
#  Run All Attacks (for comparison)
# ════════════════════════════════════════════

ALL_ATTACKS = [
    ("Replay Attack", simulate_replay_attack),
    ("Spoofing Attack", simulate_spoofing_attack),
    ("Brute Force Attack", simulate_brute_force_attack),
    ("Flooding (DoS) Attack", simulate_flooding_attack),
    ("Sniffing Attack", simulate_sniffing_attack),
    ("Tampering Attack", simulate_tampering_attack),
]


def run_all_attacks(secure_mode=False):
    """Run all 6 attacks and return results."""
    results = []
    for name, func in ALL_ATTACKS:
        results.append(func(secure_mode=secure_mode))
    return results
