"""
SecureIoT Cryptography Module
AES, SHA-256, HMAC, RSA, key management, cipher comparison.
"""

import os
import base64
import hashlib
import hmac as hmac_lib
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import hashes, serialization


# ════════════════════════════════════════════
#  AES-256 Encryption / Decryption
# ════════════════════════════════════════════

def aes_encrypt(plaintext, key=None):
    """
    Encrypt plaintext with AES-256-CBC.
    Returns dict with ciphertext, key, and iv (all base64-encoded).
    """
    if key is None:
        key = os.urandom(32)  # 256-bit key
    elif isinstance(key, str):
        key = base64.b64decode(key)

    iv = os.urandom(16)

    # Pad plaintext to block size
    padder = sym_padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "key": base64.b64encode(key).decode(),
        "iv": base64.b64encode(iv).decode(),
        "algorithm": "AES-256-CBC",
        "key_size": "256 bits",
        "block_size": "128 bits",
    }


def aes_decrypt(ciphertext_b64, key_b64, iv_b64):
    """
    Decrypt AES-256-CBC ciphertext.
    Returns the plaintext string.
    """
    ciphertext = base64.b64decode(ciphertext_b64)
    key = base64.b64decode(key_b64)
    iv = base64.b64decode(iv_b64)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = sym_padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()

    return plaintext.decode()


# ════════════════════════════════════════════
#  SHA-256 Hashing
# ════════════════════════════════════════════

def sha256_hash(data):
    """Compute SHA-256 hash of data string."""
    h = hashlib.sha256(data.encode()).hexdigest()
    return {
        "input": data,
        "hash": h,
        "algorithm": "SHA-256",
        "hash_length": f"{len(h)} hex characters ({len(h)*4} bits)",
    }


# ════════════════════════════════════════════
#  HMAC Integrity Verification
# ════════════════════════════════════════════

def hmac_generate(message, key=None):
    """Generate HMAC-SHA256 for a message."""
    if key is None:
        key = os.urandom(32)
    elif isinstance(key, str):
        key = base64.b64decode(key)

    mac = hmac_lib.new(key, message.encode(), hashlib.sha256).hexdigest()
    return {
        "message": message,
        "hmac": mac,
        "key": base64.b64encode(key).decode(),
        "algorithm": "HMAC-SHA256",
    }


def hmac_verify(message, mac_hex, key_b64):
    """Verify HMAC-SHA256 for a message."""
    key = base64.b64decode(key_b64)
    expected = hmac_lib.new(key, message.encode(), hashlib.sha256).hexdigest()
    is_valid = hmac_lib.compare_digest(expected, mac_hex)
    return {
        "message": message,
        "provided_hmac": mac_hex,
        "computed_hmac": expected,
        "is_valid": is_valid,
        "status": "✅ Integrity verified" if is_valid else "❌ Integrity check FAILED",
    }


# ════════════════════════════════════════════
#  RSA Digital Signatures
# ════════════════════════════════════════════

def rsa_generate_keys(key_size=2048):
    """Generate RSA key pair."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    return {
        "private_key": private_pem,
        "public_key": public_pem,
        "key_size": f"{key_size} bits",
        "algorithm": "RSA",
    }


def rsa_sign(message, private_pem):
    """Sign a message with RSA private key."""
    private_key = serialization.load_pem_private_key(private_pem.encode(), password=None)
    signature = private_key.sign(
        message.encode(),
        asym_padding.PSS(
            mgf=asym_padding.MGF1(hashes.SHA256()),
            salt_length=asym_padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return {
        "message": message,
        "signature": base64.b64encode(signature).decode(),
        "algorithm": "RSA-PSS with SHA-256",
    }


def rsa_verify(message, signature_b64, public_pem):
    """Verify an RSA signature."""
    public_key = serialization.load_pem_public_key(public_pem.encode())
    signature = base64.b64decode(signature_b64)
    try:
        public_key.verify(
            signature,
            message.encode(),
            asym_padding.PSS(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                salt_length=asym_padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return {"is_valid": True, "status": "✅ Signature is VALID — message is authentic"}
    except Exception:
        return {"is_valid": False, "status": "❌ Signature is INVALID — message may be tampered"}


# ════════════════════════════════════════════
#  Key Management
# ════════════════════════════════════════════

def generate_aes_key():
    """Generate a new AES-256 key."""
    key = os.urandom(32)
    return {
        "key": base64.b64encode(key).decode(),
        "algorithm": "AES-256",
        "size": "256 bits",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def rotate_key(old_key_b64):
    """Rotate an AES key — generate new key, return both."""
    new_key = os.urandom(32)
    return {
        "old_key": old_key_b64,
        "new_key": base64.b64encode(new_key).decode(),
        "status": "Key rotated successfully",
        "rotated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": "Old key should be securely destroyed after re-encrypting data",
    }


# ════════════════════════════════════════════
#  Challenge-Response Authentication
# ════════════════════════════════════════════

def challenge_response_demo():
    """Demonstrate challenge-response authentication."""
    # Server generates a random challenge
    challenge = base64.b64encode(os.urandom(16)).decode()

    # Shared secret (pre-shared key)
    shared_secret = base64.b64encode(os.urandom(32)).decode()

    # Client computes response = HMAC(challenge, shared_secret)
    response = hmac_lib.new(
        base64.b64decode(shared_secret),
        challenge.encode(),
        hashlib.sha256,
    ).hexdigest()

    # Server verifies by computing the same HMAC
    server_check = hmac_lib.new(
        base64.b64decode(shared_secret),
        challenge.encode(),
        hashlib.sha256,
    ).hexdigest()

    return {
        "challenge": challenge,
        "shared_secret": shared_secret,
        "client_response": response,
        "server_computed": server_check,
        "match": response == server_check,
        "status": "✅ Device authenticated" if response == server_check else "❌ Authentication failed",
        "steps": [
            "1. Server sends a random challenge to the device",
            "2. Device computes HMAC(challenge, shared_secret)",
            "3. Device sends the HMAC response back",
            "4. Server computes the same HMAC and compares",
            "5. If they match → device is authenticated",
        ],
    }


# ════════════════════════════════════════════
#  Cipher Comparison (AES vs ChaCha20)
# ════════════════════════════════════════════

def compare_ciphers(plaintext):
    """Compare AES-256-CBC and ChaCha20 encryption side by side."""
    data = plaintext.encode()

    # ── AES-256-CBC ──
    aes_key = os.urandom(32)
    aes_iv = os.urandom(16)
    padder = sym_padding.PKCS7(128).padder()
    aes_padded = padder.update(data) + padder.finalize()

    t0 = time.perf_counter()
    aes_cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv))
    aes_enc = aes_cipher.encryptor()
    aes_ct = aes_enc.update(aes_padded) + aes_enc.finalize()
    aes_time = (time.perf_counter() - t0) * 1000  # ms

    # ── ChaCha20 ──
    chacha_key = os.urandom(32)
    chacha_nonce = os.urandom(16)

    t0 = time.perf_counter()
    chacha_cipher = Cipher(algorithms.ChaCha20(chacha_key, chacha_nonce), mode=None)
    chacha_enc = chacha_cipher.encryptor()
    chacha_ct = chacha_enc.update(data) + chacha_enc.finalize()
    chacha_time = (time.perf_counter() - t0) * 1000  # ms

    return {
        "plaintext_length": len(data),
        "aes": {
            "algorithm": "AES-256-CBC",
            "key_size": "256 bits",
            "block_size": "128 bits",
            "type": "Block cipher",
            "ciphertext_length": len(aes_ct),
            "ciphertext_preview": base64.b64encode(aes_ct[:32]).decode() + "...",
            "time_ms": round(aes_time, 4),
            "padding": "PKCS7 required",
        },
        "chacha20": {
            "algorithm": "ChaCha20",
            "key_size": "256 bits",
            "block_size": "N/A (stream cipher)",
            "type": "Stream cipher",
            "ciphertext_length": len(chacha_ct),
            "ciphertext_preview": base64.b64encode(chacha_ct[:32]).decode() + "...",
            "time_ms": round(chacha_time, 4),
            "padding": "Not needed",
        },
    }
