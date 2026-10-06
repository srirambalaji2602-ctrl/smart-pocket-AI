import hashlib
import hmac
import secrets

from datetime import datetime, timedelta, timezone

import jwt

from ..config import get_settings


settings = get_settings()

ALGORITHM = "HS256"


def hash_password(password: str) -> str:

    salt = secrets.token_bytes(16)

    digest = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
    )

    return (
        f"scrypt$"
        f"{salt.hex()}$"
        f"{digest.hex()}"
    )


def verify_password(
    password: str,
    encoded: str,
) -> bool:

    try:

        scheme, salt_hex, digest_hex = (
            encoded.split("$", 2)
        )

        if scheme != "scrypt":
            return False

        salt = bytes.fromhex(
            salt_hex
        )

        expected = bytes.fromhex(
            digest_hex
        )

        actual = hashlib.scrypt(
            password.encode(),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
        )

        return hmac.compare_digest(
            actual,
            expected,
        )

    except (
        ValueError,
        TypeError,
    ):

        return False


def create_access_token(
    user_id: int,
    email: str,
) -> str:

    expires = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expires,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict:

    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[ALGORITHM],
    )