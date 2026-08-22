from datetime import datetime, timedelta, timezone

import jwt

from .config import AuthConfig
from .exceptions import TokenExpiredException, InvalidTokenException


class JWTHandler:
    def __init__(self, config: AuthConfig) -> None:
        self.config = config

    def create_access_token(self, subject: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            'sub': str(subject),
            'exp': now + timedelta(minutes=self.config.access_token_expire_minutes),
            'iat': now,
            'iss': self.config.issuer
        }
        return jwt.encode(
            payload=payload,
            key=self.config.secret_key.get_secret_value(),
            algorithm=self.config.algorithm
        )

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                jwt=token,
                key=self.config.secret_key.get_secret_value(),
                algorithms=[self.config.algorithm],
                issuer=self.config.issuer
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException()
        except jwt.InvalidTokenError:
            raise InvalidTokenException()
