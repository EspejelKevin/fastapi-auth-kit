import pytest
import jwt
from datetime import datetime, timedelta, timezone

from fastapi_auth_layer.config import AuthConfig
from fastapi_auth_layer.jwt_handler import JWTHandler
from fastapi_auth_layer.exceptions import InvalidTokenException, TokenExpiredException


@pytest.fixture
def jwt_handler():
    config = AuthConfig(secret_key='test_secret', access_token_expire_minutes=1)
    return JWTHandler(config)

def test_create_and_decode_token(jwt_handler):
    token = jwt_handler.create_access_token(subject='admin_123')
    payload = jwt_handler.decode_token(token)

    assert payload['sub'] == 'admin_123'
    assert payload['iss'] == 'fastapi-auth-kit'
    assert 'exp' in payload

def test_invalid_signature_raises_exception(jwt_handler):
    invalid_token = jwt.encode({'sub': 'user_123'}, 'wrong_secret_key', algorithm='HS256')

    with pytest.raises(InvalidTokenException):
        jwt_handler.decode_token(invalid_token)

def test_expired_token_raises_exception(jwt_handler):
    token = jwt.encode(
        {
            'sub': 'user_123',
            'exp': datetime.now(timezone.utc) - timedelta(minutes=5),
            'iss': 'fastapi-auth-kit'
        },
        key='test_secret',
        algorithm='HS256'
    )

    with pytest.raises(TokenExpiredException):
        jwt_handler.decode_token(token)


    