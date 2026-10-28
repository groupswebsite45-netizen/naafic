from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
)


def test_password_hashing():
    plain = "SecurePassword123!"
    hashed = get_password_hash(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_flow():
    user_id = 42
    claims = {"email": "test@example.com", "roles": ["ADMIN"]}
    token = create_access_token(subject=user_id, claims=claims)

    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "42"
    assert decoded["email"] == "test@example.com"
    assert decoded["roles"] == ["ADMIN"]
    assert decoded["type"] == "access"


def test_invalid_jwt_token():
    assert decode_token("invalid.jwt.token") is None
