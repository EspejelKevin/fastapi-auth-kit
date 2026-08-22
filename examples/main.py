from dataclasses import dataclass
from typing import Sequence

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_auth_layer.config import AuthConfig
from fastapi_auth_layer.core import Auth
from fastapi_auth_layer.protocols import AuthUser


@dataclass
class DummyUser:
    id: str
    username: str
    password: str
    is_active: bool = True
    roles: Sequence[str] = ()
    permissions: Sequence[str] = ()


FAKE_DB = {
    'usr_123': DummyUser(id='usr_123', username='admin', password='password123'),
    'usr_999': DummyUser(id='usr_999', username='banned_user', password='123', is_active=False)
}


class InMemoryUserProvider:
    async def get_by_id(self, user_id: str) -> AuthUser | None:
        '''Busca al usuario en la base de datos por su ID.'''
        return FAKE_DB.get(user_id)


auth_config = AuthConfig(
    secret_key='mi-secreto-super-seguro-para-desarrollo',
    access_token_expire_minutes=30
)

auth = Auth(config=auth_config, user_provider=InMemoryUserProvider())

app = FastAPI(title='FastAPI Auth Kit Example')

@app.post('/auth/login', tags=['Authentication'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    '''Endpoint para autenticarse y obtener el JWT.'''
    user = next((u for u in FAKE_DB.values() if u.username == form_data.username), None)
    
    if not user or user.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Incorrect username or password'
        )
    
    token = auth.jwt_handler.create_access_token(subject=user.id)
    return {'access_token': token, 'token_type': 'bearer'}

@app.get('/users/me', tags=['Users'])
async def get_current_user_profile(current_user: AuthUser = Depends(auth.current_user)):
    '''Endpoint protegido por fastapi-auth-kit.'''
    return {
        'message': 'Autenticación exitosa',
        'user_id': current_user.id,
        'is_active': current_user.is_active
    }