from typing import Literal

from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field, ConfigDict


class AuthConfig(BaseSettings):
    secret_key: SecretStr = Field(..., description='JWT Secret Key')
    algorithm: Literal['HS256', 'RS256'] = 'HS256'
    access_token_expire_minutes: int = Field(15, ge=1)
    issuer: str = 'fastapi-auth-kit'

    token_url: str = '/auth/login'

    model_config = ConfigDict(env_prefix='AUTH_')
    