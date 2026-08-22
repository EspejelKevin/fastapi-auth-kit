from dataclasses import dataclass

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from fastapi_auth_layer.config import AuthConfig
from fastapi_auth_layer.core import Auth
from fastapi_auth_layer.protocols import AuthUser


@dataclass
class MockUser:
    id: str
    is_active: bool = True


class MockUserProvider:
    async def get_by_id(self, user_id: str) -> AuthUser | None:
        if user_id == 'active_user':
            return MockUser(id='active_user')
        elif user_id == 'banned_user':
            return MockUser(id='banned_user', is_active=False)
        return None


auth = Auth(
    config=AuthConfig(secret_key='test'),
    user_provider=MockUserProvider()
)

app = FastAPI()

@app.get('/me')
async def get_me(user: AuthUser = Depends(auth.current_user)):
    return {'id': user.id}

client = TestClient(app)

def test_missing_token_returns_401():
    response = client.get('/me')

    assert response.status_code == 401

def test_valid_token_returns_200():
    token = auth.jwt_handler.create_access_token('active_user')
    response = client.get('/me', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.json() == {'id': 'active_user'}

def test_inactive_user_returns_403():
    token = auth.jwt_handler.create_access_token('banned_user')
    response = client.get('/me', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 403
