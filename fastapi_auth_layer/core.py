from typing import Callable, Coroutine, Any

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

from .protocols import AuthUser, UserProvider
from .config import AuthConfig
from .jwt_handler import JWTHandler
from .exceptions import (AuthException, InvalidTokenException,
                         UserNotFoundException, UserInactiveException)


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
