import pytest
from core.security import hash_password, verify_password, create_access_token, decode_access_token
from datetime import datetime


def test_hash_and_verify_password():
    password = "secret123"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_token():
    data = {"sub": "1", "username": "testuser"}
    token = create_access_token(data)
    payload = decode_access_token(token)
    assert payload["sub"] == "1"
    assert payload["username"] == "testuser"
    assert "exp" in payload


def test_decode_invalid_token():
    assert decode_access_token("invalid.token.here") is None