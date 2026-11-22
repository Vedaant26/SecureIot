# 🛡️ SecureIoT: Smart Building IoT Security Simulator
> **BTech University Project** | GGSIPU IoT Security Assignment Implementation

A modular, aesthetic, and fully functional IoT Security monitoring and simulation platform developed using **Python, Streamlit, SQLite, and FastAPI**.

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation
Ensure you have **Python 3.10+** installed. Then open PowerShell / Command Prompt and run:

```bash
cd "c:\Users\pushp\OneDrive\Desktop\iot projecyt\SecureIoT"
pip install -r requirements.txt
```

---

### 2. Running the Streamlit Web Application (Frontend)
To launch the interactive cybersecurity monitoring dashboard:

```bash
streamlit run app.py
```
> The dashboard will automatically open in your browser at: **`http://localhost:8501`**

---

### 3. Running the FastAPI Cloud Gateway (Backend)
To launch the REST API cloud gateway:

```bash
python -m uvicorn api.main:app --reload --port 8000
```
> Interactive Swagger API documentation will be available at: **`http://localhost:8000/docs`**

---

### 4. Running the Automated Test Suite
To verify all cryptographic routines, RBAC policies, and attack simulation engines:

```bash
pytest tests/test_all.py -v
```

---

## 📁 Project Architecture & Structure

```
SecureIoT/
├── app.py                      # Main Streamlit Dashboard (Dashboard Page)
├── requirements.txt            # Python dependencies
├── secureiot.db                # SQLite Database (auto-initialized)
│
├── .streamlit/
│   └── config.toml             # Custom Dark Navy / Blue Cyber Theme config
│
├── styles/
│   ├── __init__.py
│   └── theme.py                # CSS styles, metric cards, Plotly dark theme
│
├── modules/
│   ├── __init__.py
│   ├── database.py             # SQLite models, device stats, audit & attack logs
│   ├── crypto_utils.py         # AES-256, SHA-256, HMAC, RSA, Key rotation
│   ├── access_control.py       # bcrypt hashing, JWT, RBAC, Topic permissions
│   ├── attack_sim.py           # 6 local attack simulators (Insecure vs Secure)
│   └── privacy.py              # Pseudonymisation, Aggregation, Noise addition
│
├── pages/
│   ├── 1_Smart_Building.py     # 8 Virtual IoT devices + Add Device UI
│   ├── 2_Attack_Simulation.py  # 6 Attack modules + Before/After Comparison
│   ├── 3_Cryptography.py       # Interactive AES, SHA-256, HMAC, RSA, Key rotation
│   ├── 4_Access_Control.py     # User auth, RBAC matrix, Device registration, Privacy
│   └── 5_Reports.py            # Attack history, Security events, CSV export
│
├── api/
│   ├── __init__.py
│   └── main.py                 # FastAPI REST API (JWT auth, Rate limiting, Audit)
│
├── tests/
│   ├── __init__.py
│   └── test_all.py             # Automated unit & integration tests
│
└── docs/
    ├── project_report.md       # Full University Project Report
    └── presentation.md         # Viva Presentation Outline & Slides
```

---

## 🌟 Key Features

1. **Dashboard (`app.py`)**: Real-time KPI metric cards (Total Devices, Active Devices, Messages, Attacks Tested, Security Status), donut charts for device distribution, and security events feed.
2. **Smart Building (`pages/1_Smart_Building.py`)**: 8 pre-seeded virtual IoT devices (Temperature sensors, Door locks, Energy meters, Motion detectors) with live readings and the ability to add new virtual devices.
3. **Attack Simulation (`pages/2_Attack_Simulation.py`)**: Realistic local simulation of **Replay, Spoofing, Brute Force, Flooding (DoS), Sniffing, and Tampering** attacks with an interactive toggle between Insecure Mode and Secure Mode.
4. **Cryptography (`pages/3_Cryptography.py`)**: Functional cryptographic tools including AES-256-CBC encryption/decryption, SHA-256 with avalanche effect demonstration, HMAC-SHA256 message integrity, 2048-bit RSA digital signatures, dynamic key rotation, challenge-response authentication, and AES vs ChaCha20 benchmarks.
5. **Access Control & Privacy (`pages/4_Access_Control.py`)**: User registration/login with 12-round bcrypt salt, Role-Based Access Control (`admin`, `operator`, `viewer`), device registration/revocation, topic-level permissions, and 3 data privacy techniques (Pseudonymisation, Aggregation, Laplace Differential Privacy).
6. **Reports & Exports (`pages/5_Reports.py`)**: Full historical audit logs, attack simulation logs, security event distribution, and instant 1-click CSV download.
7. **Cloud API (`api/main.py`)**: Production-grade FastAPI REST API with JWT Bearer authentication, SlowAPI rate limiting (IP-based protection), input schema validation, and encrypted telemetry storage.

---

## 🎓 University Viva Checklist & Tips

- **Question: Why is AES-256-CBC chosen for telemetry?**
  *Answer:* AES is the NIST-approved symmetric cipher standard offering strong security with low hardware overhead on microcontroller/IoT gateways. CBC mode with PKCS7 ensures identical blocks produce distinct ciphertexts through random Initialization Vectors (IV).
- **Question: How does secure mode defeat the Replay attack?**
  *Answer:* Secure mode attaches a unique pseudo-random nonce and a millisecond timestamp to every packet. The server maintains a nonce cache and rejects previously observed nonces or expired timestamps.
- **Question: How does HMAC guarantee integrity?**
  *Answer:* HMAC uses a pre-shared secret key combined with SHA-256. If a man-in-the-middle alters even 1 bit of the sensor reading, the cryptographic hash computed on the server will not match the transmitted MAC.
