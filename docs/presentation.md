# 🎤 SecureIoT: University Viva & Presentation Guide

## Presentation Outline (10-15 Minutes)

### Slide 1: Title & Introduction
- **Project Name:** SecureIoT — Smart Building Security Platform
- **Objective:** Demonstrating vulnerabilities in IoT architectures and implementing cryptographic and access control defenses.
- **Technology Stack:** Python, Streamlit, SQLite, FastAPI, Cryptography (AES, RSA, SHA, HMAC), bcrypt, JWT.

---

### Slide 2: Problem Statement
- IoT devices have limited compute/battery resources.
- Manufacturers often omit encryption, authentication, and rate limiting.
- Vulnerabilities leave smart buildings open to sniffing, spoofing, tampering, replay, and DoS attacks.

---

### Slide 3: Smart Building Architecture
- 8 virtual devices across 4 functional domains:
  - 🌡️ Temperature Sensors (`TEMP-001`, `TEMP-002`)
  - 🔒 Smart Door Locks (`LOCK-001`, `LOCK-002`)
  - ⚡ Energy Meters (`ENERGY-001`, `ENERGY-002`)
  - 👁️ Motion Detectors (`MOTION-001`, `MOTION-002`)
- Multi-tier structure: Perception Layer → Gateway → Cloud REST API → Streamlit UI.

---

### Slide 4: Attack Simulation Demonstrations (6 Attacks)
1. **Replay Attack:** Intercepting a door unlock packet and resending it. Defeated using nonces + timestamps.
2. **Spoofing Attack:** Fake sensor injecting high temperature readings. Defeated using HMAC pre-shared key.
3. **Brute Force:** Automated credential guessing. Defeated by rate limiting + 3-attempt account lockout.
4. **Flooding (DoS):** Overwhelming the server with 50 req/sec. Defeated by token bucket rate limiter dropping excess packets.
5. **Sniffing Attack:** Intercepting unencrypted LAN traffic. Defeated with AES-256-CBC encryption.
6. **Tampering Attack:** Altering energy meter values in transit. Defeated by HMAC integrity verification.

---

### Slide 5: Cryptography Module
- **AES-256-CBC:** Symmetric encryption with random IVs and PKCS7 padding.
- **SHA-256:** One-way hash function showing the Avalanche Effect (1 bit change = completely different hash).
- **HMAC-SHA256:** Data integrity and message authenticity.
- **RSA-2048:** Digital signature with RSA-PSS for non-repudiation and firmware integrity.
- **Cipher Comparison:** AES-256-CBC (Block cipher) vs ChaCha20 (Stream cipher).

---

### Slide 6: Access Control & Privacy
- **User Authentication:** Passwords hashed with 12 salt rounds of `bcrypt`.
- **RBAC Matrix:** 3 Roles — `admin` (full control), `operator` (monitor & operate), `viewer` (read-only).
- **Topic-Level Permissions:** Granular access rules (e.g., `door_lock/control`).
- **Privacy Techniques:**
  1. *Pseudonymisation:* Masking device IDs with cryptographic hashes.
  2. *Data Aggregation:* Computing mean, median, min, max instead of publishing raw readings.
  3. *Differential Privacy:* Adding calibrated Laplace noise ($\epsilon$).

---

### Slide 7: Cloud Gateway & REST API
- Built with **FastAPI**.
- Secured with **JWT Bearer Tokens**.
- Input validation via **Pydantic Models**.
- Denial-of-Service protection via **SlowAPI Rate Limiting**.
- Telemetry payloads encrypted with AES-256 before storage in **SQLite**.

---

## 💡 Top Viva Questions & Confident Answers

1. **Q: Why is AES-256 used instead of DES or 3DES?**
   - *Answer:* DES has a 56-bit key which is susceptible to brute-force within hours. 3DES is computationally slow and vulnerable to Sweet32. AES-256 is the current NIST symmetric standard, secure against quantum attacks (Grover's algorithm), and hardware-accelerated (AES-NI).

2. **Q: What is a Nonce and why is it needed in Replay defense?**
   - *Answer:* A Nonce is a "Number used ONCE". By including a unique random token and timestamp in every message, the server ensures that any identical duplicated packet intercepted by an adversary is recognized as expired and immediately rejected.

3. **Q: How does differential privacy protect sensor data?**
   - *Answer:* Differential privacy injects controlled mathematical noise (e.g., Laplace noise) into query outputs. An attacker cannot ascertain whether a specific device contributed to the dataset, while aggregate trends remain statistically accurate.
