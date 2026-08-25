from typing import Callable, Coroutine, Any, Sequence, Literal

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

from .protocols import AuthUser, UserProvider
from .config import AuthConfig
from .jwt_handler import JWTHandler
from .exceptions import (AuthException, InvalidTokenException,
                         UserNotFoundException, UserInactiveException,
                         InsufficientPermissionsException)


class Auth:
    current_user: Callable[..., Coroutine[Any, Any, AuthUser]]

    def __init__(self, config: AuthConfig, user_provider: UserProvider) -> None:
        self.config = config
        self.user_provider = user_provider
        self.jwt_handler = JWTHandler(self.config)

        self.oauth2_bearer_schema = OAuth2PasswordBearer(tokenUrl=self.config.token_url)

        async def _current_user_dependency(token: str = Depends(self.oauth2_bearer_schema)) -> AuthUser:
            try:
                payload = self.jwt_handler.decode_token(token)
            except AuthException as ex:
                raise ex

            user_id: str = payload.get('sub', '')
            if not user_id:
                raise InvalidTokenException()

            user = await self.user_provider.get_by_id(user_id)
            if not user:
                raise UserNotFoundException()

            if not getattr(user, 'is_active', True):
                raise UserInactiveException()

            return user

        self.current_user = _current_user_dependency

    def require_roles(self, roles: Sequence[str], mode: Literal['ALL', 'ANY'] = 'ALL') -> Callable[..., Coroutine[Any, Any, AuthUser]]:
        async def _role_dependency(user: AuthUser = Depends(self.current_user)) -> AuthUser:
            user_roles = getattr(user, 'roles', [])

            if mode == 'ALL':
                has_roles = all(role in user_roles for role in roles)
            elif mode == 'ANY':
                has_roles = any(role in user_roles for role in roles)
            else:
                has_roles = False

            if not has_roles:
                raise InsufficientPermissionsException()

            return user

        return _role_dependency

    def require_permissions(self, permissions: Sequence[str], mode: Literal['ALL', 'ANY'] = 'ALL') -> Callable[..., Coroutine[Any, Any, AuthUser]]:
        async def _permission_dependency(user: AuthUser = Depends(self.current_user)) -> AuthUser:
            user_permissions = getattr(user, 'permissions', [])

            if mode == 'ALL':
                has_permissions = all(permission in user_permissions for permission in permissions)
            elif mode == 'ANY':
                has_permissions = any(permission in user_permissions for permission in permissions)
            else:
                has_permissions = False

            if not has_permissions:
                raise InsufficientPermissionsException()

            return user

        return _permission_dependency
