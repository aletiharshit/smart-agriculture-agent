"""
Authentication and Security Module for Smart Agriculture Agent.
Provides PBKDF2 password hashing with cryptographically secure salts,
constant-time password verification, input validation, and session management.
Zero external dependencies (uses Python standard library: hashlib, secrets, hmac, re).
"""

import hashlib
import secrets
import hmac
import re
from typing import Tuple, Optional, Dict, Any

# Regular expression for a valid 10-digit Indian mobile number (starts with 6, 7, 8, or 9)
PHONE_REGEX = re.compile(r"^[6-9]\d{9}$")
HASH_ITERATIONS = 100_000


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with 100,000 iterations and a unique salt.
    Returns (password_hash_hex, salt_hex).
    Never stores or returns plaintext passwords.
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        HASH_ITERATIONS
    )
    return key.hex(), salt


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """
    Verifies a password against the stored salt and hash using constant-time comparison
    to prevent timing attacks.
    """
    computed_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(computed_hash, expected_hash)


def validate_phone_number(phone: str) -> bool:
    """
    Validates that a phone number is a valid 10-digit number.
    Strips leading +91 or 0 if present.
    """
    cleaned = clean_phone_number(phone)
    return bool(PHONE_REGEX.match(cleaned))


def clean_phone_number(phone: str) -> str:
    """
    Normalizes a phone number by stripping whitespace, dashes, and international prefixes.
    """
    if not phone:
        return ""
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone.strip())
    # Strip leading 91 (country code) if total is 12 digits
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    # Strip leading 0 if total is 11 digits
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    return digits


def validate_registration(
    full_name: str,
    phone: str,
    password: str,
    confirm_password: str
) -> Tuple[bool, str]:
    """
    Validates farmer registration input fields.
    Returns (is_valid, error_message).
    """
    name = (full_name or "").strip()
    if len(name) < 2:
        return False, "Please enter your full name (at least 2 characters)."

    cleaned_phone = clean_phone_number(phone)
    if not PHONE_REGEX.match(cleaned_phone):
        return False, "Please enter a valid 10-digit mobile number (e.g., 9876543210)."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    if password != confirm_password:
        return False, "Passwords do not match. Please verify and re-type."

    return True, ""
