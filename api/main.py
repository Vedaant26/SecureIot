"""
SecureIoT FastAPI REST API
Cloud Security Layer:
- JWT Authentication
- Pydantic Input Validation
- Rate Limiting (SlowAPI)
- Encrypted Telemetry Storage
- Audit Logs
"""

import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import jwt
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from modules import database as db
from modules import crypto_utils
from modules import access_control as ac

JWT_SECRET = "secureiot-super-secret-key-change-in-production-2026"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="SecureIoT Cloud Gateway API",
    description="REST API for Secure IoT Telemetry, Device Control & Cloud Auditing",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ──
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field(default="viewer", pattern="^(admin|operator|viewer)$")


class LoginRequest(BaseModel):
    username: str
    password: str


class TelemetryRequest(BaseModel):
    device_id: str = Field(..., min_length=2, max_length=50)
    payload: str = Field(..., min_length=1, description="Raw plaintext sensor payload to encrypt and store")


class DeviceCreateRequest(BaseModel):
    device_id: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    device_type: str = Field(..., pattern="^(temperature|door_lock|energy|motion)$")
    location: str = Field(..., min_length=2, max_length=100)


# ── JWT Helpers ──
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRATION_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Bearer token",
        )
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role", "viewer")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
        return {"username": username, "role": role}
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


# ── Routes ──

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "SecureIoT Cloud Gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "login": "/api/v1/auth/login",
            "register": "/api/v1/auth/register",
            "telemetry": "/api/v1/telemetry",
            "devices": "/api/v1/devices",
            "audit_logs": "/api/v1/audit-logs",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy", "database": "connected"}


@app.post("/api/v1/auth/register")
@limiter.limit("5/minute")
def register(req: UserRegisterRequest, request: Request):
    res = ac.register_user(req.username, req.password, req.role)
    if not res["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res["message"])
    return res


@app.post("/api/v1/auth/login")
@limiter.limit("10/minute")
def login(req: LoginRequest, request: Request):
    res = ac.authenticate_user(req.username, req.password)
    if not res["success"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=res["message"])
    token = create_access_token({"sub": res["username"], "role": res["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": res["role"],
        "username": res["username"],
    }


@app.post("/api/v1/telemetry")
@limiter.limit("60/minute")
def ingest_telemetry(req: TelemetryRequest, request: Request, current_user: dict = Depends(get_current_user)):
    # Check if user has permission to write telemetry
    perm = ac.check_permission(current_user["role"], "write")
    if not perm["allowed"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not permitted to ingest telemetry")

    # Encrypt telemetry using AES-256 before saving to database
    enc = crypto_utils.aes_encrypt(req.payload)
    db.store_telemetry(req.device_id, enc["ciphertext"])
    db.log_audit(current_user["username"], "ingest_telemetry", req.device_id, "success")

    return {
        "status": "success",
        "device_id": req.device_id,
        "encrypted_ciphertext": enc["ciphertext"],
        "algorithm": enc["algorithm"],
        "message": "Telemetry encrypted and stored securely.",
    }


@app.get("/api/v1/telemetry")
def read_telemetry(current_user: dict = Depends(get_current_user)):
    perm = ac.check_permission(current_user["role"], "read")
    if not perm["allowed"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return db.get_telemetry(50)


@app.get("/api/v1/devices")
def list_devices():
    return db.get_all_devices()


@app.post("/api/v1/devices")
def add_device(req: DeviceCreateRequest, current_user: dict = Depends(get_current_user)):
    perm = ac.check_permission(current_user["role"], "manage_devices")
    if not perm["allowed"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required to add devices")
    res = ac.register_device(req.device_id, req.name, req.device_type, req.location)
    return res


@app.get("/api/v1/audit-logs")
def view_audit_logs(current_user: dict = Depends(get_current_user)):
    perm = ac.check_permission(current_user["role"], "view_logs")
    if not perm["allowed"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to view logs")
    return db.get_audit_logs(100)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
