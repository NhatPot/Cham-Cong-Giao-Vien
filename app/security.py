import base64
import hmac
import hashlib
import time
from typing import Tuple
from app.main import settings


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def base64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def sign_token(session_id: int, exp_ts: int) -> str:
    payload = f"{session_id}|{exp_ts}".encode()
    payload_b64 = base64url_encode(payload)
    sig = hmac.new(settings.SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
    sig_b64 = base64url_encode(sig)
    return f"{payload_b64}.{sig_b64}"


def verify_token(token: str) -> Tuple[int, int]:
    try:
        payload_b64, sig_b64 = token.split(".")
        expected = hmac.new(settings.SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, base64url_decode(sig_b64)):
            raise ValueError("bad-signature")
        payload = base64url_decode(payload_b64).decode()
        session_id_str, exp_str = payload.split("|")
        session_id = int(session_id_str)
        exp_ts = int(exp_str)
        if int(time.time()) > exp_ts:
            raise ValueError("expired")
        return session_id, exp_ts
    except Exception as e:
        raise ValueError("invalid-token") from e
