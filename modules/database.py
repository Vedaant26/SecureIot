"""
SecureIoT Database Module
Handles all SQLite operations — devices, users, events, logs.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "secureiot.db")


def get_connection():
    """Get a SQLite connection with row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=DELETE")
    except Exception:
        pass
    return conn


def init_db():
    """Create all tables and seed initial data."""
    conn = get_connection()
    cur = conn.cursor()

    # ── Create Tables ──
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            location TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            reading TEXT DEFAULT '',
            is_registered INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT DEFAULT '',
            source TEXT DEFAULT '',
            timestamp TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS attack_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attack_type TEXT NOT NULL,
            mode TEXT NOT NULL,
            result TEXT NOT NULL,
            details TEXT DEFAULT '',
            timestamp TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT DEFAULT '',
            action TEXT NOT NULL,
            resource TEXT DEFAULT '',
            result TEXT DEFAULT '',
            ip_address TEXT DEFAULT '127.0.0.1',
            timestamp TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            data_encrypted TEXT NOT NULL,
            timestamp TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS device_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            device_type TEXT NOT NULL,
            permission TEXT NOT NULL
        );
    """)

    # ── Seed Default IoT Devices (8 devices) ──
    default_devices = [
        ("TEMP-001", "Temperature Sensor 1", "temperature", "Floor 1 - Lobby", "active", "23.5°C"),
        ("TEMP-002", "Temperature Sensor 2", "temperature", "Floor 2 - Office", "active", "24.1°C"),
        ("LOCK-001", "Smart Door Lock 1", "door_lock", "Main Entrance", "active", "Locked"),
        ("LOCK-002", "Smart Door Lock 2", "door_lock", "Server Room", "active", "Locked"),
        ("ENERGY-001", "Energy Meter 1", "energy", "Floor 1", "active", "2.4 kWh"),
        ("ENERGY-002", "Energy Meter 2", "energy", "Floor 2", "active", "3.1 kWh"),
        ("MOTION-001", "Motion Sensor 1", "motion", "Corridor A", "active", "No Motion"),
        ("MOTION-002", "Motion Sensor 2", "motion", "Parking Lot", "active", "Motion Detected"),
    ]
    for d in default_devices:
        cur.execute(
            "INSERT OR IGNORE INTO devices (id, name, type, location, status, reading) VALUES (?,?,?,?,?,?)",
            d,
        )

    # ── Seed Default Permissions ──
    default_perms = [
        ("admin", "temperature", "read,write,control"),
        ("admin", "door_lock", "read,write,control"),
        ("admin", "energy", "read,write,control"),
        ("admin", "motion", "read,write,control"),
        ("operator", "temperature", "read,write"),
        ("operator", "door_lock", "read,control"),
        ("operator", "energy", "read"),
        ("operator", "motion", "read"),
        ("viewer", "temperature", "read"),
        ("viewer", "door_lock", "read"),
        ("viewer", "energy", "read"),
        ("viewer", "motion", "read"),
    ]
    cur.execute("SELECT COUNT(*) FROM device_permissions")
    if cur.fetchone()[0] == 0:
        for p in default_perms:
            cur.execute(
                "INSERT INTO device_permissions (role, device_type, permission) VALUES (?,?,?)", p
            )

    # ── Seed sample security events ──
    cur.execute("SELECT COUNT(*) FROM security_events")
    if cur.fetchone()[0] == 0:
        sample_events = [
            ("login", "info", "Admin user logged in", "auth-module"),
            ("device_added", "info", "New temperature sensor registered", "device-mgr"),
            ("attack_detected", "high", "Replay attack attempt blocked", "attack-monitor"),
            ("key_rotated", "info", "AES encryption key rotated", "crypto-module"),
            ("access_denied", "warning", "Viewer tried to control door lock", "rbac-module"),
        ]
        for ev in sample_events:
            cur.execute(
                "INSERT INTO security_events (event_type, severity, description, source) VALUES (?,?,?,?)",
                ev,
            )

    conn.commit()
    conn.close()


# ── Device Operations ──

def get_all_devices():
    """Return all devices as a list of dicts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM devices ORDER BY type, id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_device_stats():
    """Return counts: total, active, by type."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    active = conn.execute("SELECT COUNT(*) FROM devices WHERE status='active'").fetchone()[0]
    by_type = {}
    for row in conn.execute("SELECT type, COUNT(*) as cnt FROM devices GROUP BY type"):
        by_type[row["type"]] = row["cnt"]
    conn.close()
    return {"total": total, "active": active, "by_type": by_type}


def add_device(device_id, name, device_type, location):
    """Add a new virtual device."""
    conn = get_connection()
    readings_map = {
        "temperature": "22.0°C",
        "door_lock": "Locked",
        "energy": "0.0 kWh",
        "motion": "No Motion",
    }
    reading = readings_map.get(device_type, "N/A")
    conn.execute(
        "INSERT OR REPLACE INTO devices (id, name, type, location, status, reading) VALUES (?,?,?,?,?,?)",
        (device_id, name, device_type, location, "active", reading),
    )
    conn.commit()
    conn.close()
    return {"id": device_id, "name": name, "type": device_type, "status": "active"}


def update_device_status(device_id, status):
    """Update a device's status."""
    conn = get_connection()
    conn.execute("UPDATE devices SET status=? WHERE id=?", (status, device_id))
    conn.commit()
    conn.close()


def revoke_device(device_id):
    """Revoke (deactivate) a device."""
    conn = get_connection()
    conn.execute("UPDATE devices SET status='revoked', is_registered=0 WHERE id=?", (device_id,))
    conn.commit()
    conn.close()


# ── Security Events ──

def log_security_event(event_type, severity, description, source="system"):
    """Log a security event."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO security_events (event_type, severity, description, source) VALUES (?,?,?,?)",
        (event_type, severity, description, source),
    )
    conn.commit()
    conn.close()


def get_security_events(limit=50):
    """Get recent security events."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM security_events ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Attack Logs ──

def log_attack(attack_type, mode, result, details=""):
    """Log an attack simulation result."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO attack_logs (attack_type, mode, result, details) VALUES (?,?,?,?)",
        (attack_type, mode, result, details),
    )
    # Also log as security event
    severity = "high" if result == "success" else "info"
    conn.execute(
        "INSERT INTO security_events (event_type, severity, description, source) VALUES (?,?,?,?)",
        ("attack_simulation", severity, f"{attack_type} ({mode}) → {result}", "attack-simulator"),
    )
    conn.commit()
    conn.close()


def get_attack_logs(limit=100):
    """Get attack simulation logs."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM attack_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_attack_stats():
    """Get attack statistics grouped by type and mode."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT attack_type, mode, result, COUNT(*) as count
        FROM attack_logs
        GROUP BY attack_type, mode, result
        ORDER BY attack_type
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Users ──

def register_user(username, password_hash, role="viewer"):
    """Register a new user."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            (username, password_hash, role),
        )
        conn.commit()
        return {"success": True, "message": f"User '{username}' registered as {role}"}
    except sqlite3.IntegrityError:
        return {"success": False, "message": f"Username '{username}' already exists"}
    finally:
        conn.close()


def get_user(username):
    """Get a user by username."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users():
    """Get all users."""
    conn = get_connection()
    rows = conn.execute("SELECT id, username, role, created_at FROM users ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Audit Logs ──

def log_audit(username, action, resource="", result="success"):
    """Log an audit entry."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO audit_logs (username, action, resource, result) VALUES (?,?,?,?)",
        (username, action, resource, result),
    )
    conn.commit()
    conn.close()


def get_audit_logs(limit=100):
    """Get audit logs."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Telemetry ──

def store_telemetry(device_id, encrypted_data):
    """Store encrypted telemetry data."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO telemetry (device_id, data_encrypted) VALUES (?,?)",
        (device_id, encrypted_data),
    )
    conn.commit()
    conn.close()


def get_telemetry(limit=50):
    """Get telemetry records."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Permissions ──

def get_permissions(role):
    """Get permissions for a role."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM device_permissions WHERE role=?", (role,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_permissions():
    """Get all role permissions."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM device_permissions ORDER BY role, device_type"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_message_count():
    """Get total telemetry messages received."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0]
    conn.close()
    return count


def get_total_attacks():
    """Get total attack simulations run."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM attack_logs").fetchone()[0]
    conn.close()
    return count


# Initialise the database when this module is first imported
init_db()
