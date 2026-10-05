"""تشفير كلمات المرور والتحقق منها.

نستخدم PBKDF2-HMAC-SHA256 من المكتبة القياسية — لا يحتاج أي حزمة خارجية،
ويُخزَّن الناتج بصيغة:  salt$hash
"""

import hashlib
import hmac
import os

ITERATIONS = 260_000


def hash_password(password: str) -> str:
    """توليد بصمة آمنة لكلمة المرور."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """مقارنة كلمة المرور المدخلة بالبصمة المخزنة."""
    try:
        salt_hex, digest_hex = stored.split("$")
    except ValueError:
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), ITERATIONS
    )
    return hmac.compare_digest(digest.hex(), digest_hex)
