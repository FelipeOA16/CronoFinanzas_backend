from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from jose import jwt, JWTError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

from app.core.config import Settings

_ph = PasswordHasher()
settings = Settings()


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def create_access_token(
    subject: str,
    roles: Optional[List[str]] = None,
    expires_delta: Optional[int] = None,
) -> str:
    expire = datetime.utcnow() + timedelta(minutes=(expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "typ": "access",
        "roles": roles or [],
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str, expires_delta: Optional[int] = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=(expires_delta or settings.REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode: Dict[str, Any] = {"sub": str(subject), "exp": expire, "typ": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("typ") != "access":
            raise JWTError("token is not an access token")
        return payload
    except JWTError as e:
        raise e


def decode_refresh_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("typ") != "refresh":
            raise JWTError("token is not a refresh token")
        return payload
    except JWTError as e:
        raise e
