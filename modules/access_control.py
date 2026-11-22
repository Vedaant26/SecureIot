"""
SecureIoT Access Control Module
User authentication, RBAC, device registration, challenge-response.
"""

import bcrypt
from modules import database as db


# ════════════════════════════════════════════
#  Password Hashing (bcrypt)
# ════════════════════════════════════════════

def hash_password(password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def verify_password(password, hashed):
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ════════════════════════════════════════════
#  User Registration & Authentication
# ════════════════════════════════════════════

def register_user(username, password, role="viewer"):
    """Register a new user with hashed password."""
    if not username or not password:
        return {"success": False, "message": "Username and password are required."}
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters."}
    if role not in ("admin", "operator", "viewer"):
        return {"success": False, "message": "Role must be admin, operator, or viewer."}

    pw_hash = hash_password(password)
    result = db.register_user(username, pw_hash, role)

    if result["success"]:
        db.log_audit(username, "user_registered", f"role={role}", "success")
        db.log_security_event("user_registered", "info", f"New user: {username} ({role})", "access-control")
    return result


def authenticate_user(username, password):
    """Authenticate a user by username and password."""
    user = db.get_user(username)
    if user is None:
        db.log_audit(username, "login_failed", "user not found", "failure")
        return {"success": False, "message": "User not found."}

    if verify_password(password, user["password_hash"]):
        db.log_audit(username, "login_success", f"role={user['role']}", "success")
        return {
            "success": True,
            "message": f"Welcome, {username}!",
            "role": user["role"],
            "username": username,
        }
    else:
        db.log_audit(username, "login_failed", "wrong password", "failure")
        return {"success": False, "message": "Incorrect password."}


# ════════════════════════════════════════════
#  Role-Based Access Control (RBAC)
# ════════════════════════════════════════════

ROLE_HIERARCHY = {
    "admin": ["read", "write", "control", "manage_users", "manage_devices", "view_logs"],
    "operator": ["read", "write", "control", "view_logs"],
    "viewer": ["read"],
}


def check_permission(role, action):
    """Check if a role has a specific permission."""
    allowed = ROLE_HIERARCHY.get(role, [])
    has_perm = action in allowed
    return {
        "role": role,
        "action": action,
        "allowed": has_perm,
        "status": f"✅ {role} CAN {action}" if has_perm else f"❌ {role} CANNOT {action}",
    }


def get_role_permissions(role):
    """Get all permissions for a role."""
    perms = ROLE_HIERARCHY.get(role, [])
    topic_perms = db.get_permissions(role)
    return {
        "role": role,
        "general_permissions": perms,
        "device_permissions": topic_perms,
    }


def get_all_roles_comparison():
    """Compare permissions across all roles."""
    all_actions = ["read", "write", "control", "manage_users", "manage_devices", "view_logs"]
    comparison = []
    for action in all_actions:
        row = {"action": action}
        for role in ["admin", "operator", "viewer"]:
            row[role] = "✅" if action in ROLE_HIERARCHY.get(role, []) else "❌"
        comparison.append(row)
    return comparison


# ════════════════════════════════════════════
#  Device Registration & Revocation
# ════════════════════════════════════════════

def register_device(device_id, name, device_type, location):
    """Register a new IoT device."""
    result = db.add_device(device_id, name, device_type, location)
    db.log_audit("system", "device_registered", device_id, "success")
    db.log_security_event("device_registered", "info", f"Device {device_id} registered", "device-mgr")
    return {"success": True, "message": f"Device '{device_id}' registered successfully.", "device": result}


def revoke_device(device_id):
    """Revoke a device's registration."""
    db.revoke_device(device_id)
    db.log_audit("system", "device_revoked", device_id, "success")
    db.log_security_event("device_revoked", "warning", f"Device {device_id} revoked", "device-mgr")
    return {"success": True, "message": f"Device '{device_id}' has been revoked."}


# ════════════════════════════════════════════
#  Topic-Level Permissions
# ════════════════════════════════════════════

TOPIC_PERMISSIONS = {
    "admin": {
        "temperature/read": True, "temperature/write": True, "temperature/control": True,
        "door_lock/read": True, "door_lock/write": True, "door_lock/control": True,
        "energy/read": True, "energy/write": True, "energy/control": True,
        "motion/read": True, "motion/write": True, "motion/control": True,
    },
    "operator": {
        "temperature/read": True, "temperature/write": True, "temperature/control": False,
        "door_lock/read": True, "door_lock/write": False, "door_lock/control": True,
        "energy/read": True, "energy/write": False, "energy/control": False,
        "motion/read": True, "motion/write": False, "motion/control": False,
    },
    "viewer": {
        "temperature/read": True, "temperature/write": False, "temperature/control": False,
        "door_lock/read": True, "door_lock/write": False, "door_lock/control": False,
        "energy/read": True, "energy/write": False, "energy/control": False,
        "motion/read": True, "motion/write": False, "motion/control": False,
    },
}


def check_topic_permission(role, topic):
    """Check if a role can access a specific topic."""
    perms = TOPIC_PERMISSIONS.get(role, {})
    allowed = perms.get(topic, False)
    return {
        "role": role,
        "topic": topic,
        "allowed": allowed,
        "status": f"✅ Allowed" if allowed else f"❌ Denied",
    }


def get_topic_permissions_table():
    """Get a full topic permissions table for all roles."""
    rows = []
    topics = sorted(set(t for perms in TOPIC_PERMISSIONS.values() for t in perms))
    for topic in topics:
        row = {"topic": topic}
        for role in ["admin", "operator", "viewer"]:
            row[role] = "✅" if TOPIC_PERMISSIONS.get(role, {}).get(topic, False) else "❌"
        rows.append(row)
    return rows
