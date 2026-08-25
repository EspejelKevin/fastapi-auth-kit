from dataclasses import dataclass
from typing import Sequence

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from fastapi_auth_layer.config import AuthConfig
from fastapi_auth_layer.core import Auth
from fastapi_auth_layer.protocols import AuthUser


@dataclass
class MockUser:
    id: str
    is_active: bool = True
    roles: Sequence[str] = ()
    permissions: Sequence[str] = ()


class MockUserProvider:
    async def get_by_id(self, user_id: str) -> AuthUser | None:
        users = {
            'admin_user': MockUser(id='admin_user', roles=['admin'], permissions=['read', 'write', 'delete']),
            'editor_user': MockUser(id='editor_user', roles=['editor'], permissions=['read', 'write']),
            'viewer_user': MockUser(id='viewer_user', roles=['viewer'], permissions=['read']),
        }
        return users.get(user_id)


auth = Auth(
    config=AuthConfig(secret_key='test-secret'), 
    user_provider=MockUserProvider()
)

app = FastAPI()

@app.get('/require-admin')
async def require_admin(user = Depends(auth.require_roles(['admin']))):
    return {'status': 'ok'}

@app.get('/require-any-role')
async def require_any_role(user = Depends(auth.require_roles(['admin', 'editor'], mode='ANY'))):
    return {'status': 'ok'}

@app.get('/require-all-perms')
async def require_all_perms(user = Depends(auth.require_permissions(['read', 'write'], mode='ALL'))):
    return {'status': 'ok'}

@app.get('/require-write-perm')
async def require_write_perm(user = Depends(auth.require_permissions(['write']))):
    return {'status': 'ok'}

@app.get('/invalid-mode')
async def invalid_mode(user = Depends(auth.require_permissions(['write'], mode='INVALID_MODE'))):
    return {'status': 'ok'}

client = TestClient(app)

def get_headers(user_id: str) -> dict:
    token = auth.jwt_handler.create_access_token(user_id)
    return {'Authorization': f'Bearer {token}'}

def test_role_authorization_success():
    '''Un admin debe poder entrar a una ruta de admin.'''
    response = client.get('/require-admin', headers=get_headers('admin_user'))
    assert response.status_code == 200

def test_role_authorization_forbidden():
    '''Un editor NO debe poder entrar a una ruta de admin.'''
    response = client.get('/require-admin', headers=get_headers('editor_user'))
    assert response.status_code == 403

def test_any_role_authorization():
    '''Tanto un admin como un editor deben poder entrar si se requiere CUALQUIERA de los dos roles.'''
    assert client.get('/require-any-role', headers=get_headers('admin_user')).status_code == 200
    assert client.get('/require-any-role', headers=get_headers('editor_user')).status_code == 200
    assert client.get('/require-any-role', headers=get_headers('viewer_user')).status_code == 403

def test_all_permissions_authorization():
    '''El usuario debe tener TODOS los permisos solicitados.'''
    assert client.get('/require-all-perms', headers=get_headers('editor_user')).status_code == 200
    assert client.get('/require-all-perms', headers=get_headers('viewer_user')).status_code == 403

def test_single_permission_authorization():
    '''Validación de un solo permiso por defecto (modo ALL).'''
    assert client.get('/require-write-perm', headers=get_headers('editor_user')).status_code == 200
    assert client.get('/require-write-perm', headers=get_headers('viewer_user')).status_code == 403

def test_invalid_mode():
    '''Validación de un mode incorrecto (modo INVALID_MODE).'''
    assert client.get('/invalid-mode', headers=get_headers('editor_user')).status_code == 403
