from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


def test_hash_password_verifies_plain_password():
    hashed_password = hash_password("ValidPass123!")

    assert hashed_password != "ValidPass123!"
    assert verify_password("ValidPass123!", hashed_password)
    assert not verify_password("WrongPass123!", hashed_password)


def test_access_token_round_trip_contains_subject_and_roles():
    token = create_access_token("user-1", roles=["user"], expires_delta=1)

    payload = decode_access_token(token)

    assert payload["sub"] == "user-1"
    assert payload["typ"] == "access"
    assert payload["roles"] == ["user"]


def test_refresh_token_is_rejected_as_access_token():
    token = create_refresh_token("user-1", expires_delta=1)

    try:
        decode_access_token(token)
    except JWTError:
        return

    raise AssertionError("refresh token was accepted as an access token")


def test_refresh_token_round_trip_contains_subject():
    token = create_refresh_token("user-1", expires_delta=1)

    payload = decode_refresh_token(token)

    assert payload["sub"] == "user-1"
    assert payload["typ"] == "refresh"
