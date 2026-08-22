# FastAPI Auth Kit

Authentication & Authorization as a FastAPI dependency layer. 
Stop rewriting JWT validation, user dependencies, and security exceptions in every project.

## 🚀 Features

* **FastAPI-Native:** Integrates seamlessly with `Depends()` and Swagger UI.
* **Database Agnostic:** Works with SQLAlchemy, MongoDB, Redis, or simple memory structures via Python Protocols.
* **Secure by Default:** Strict JWT algorithm enforcement, expiration handling, and standard HTTP security codes.

## 📦 Installation

```bash
pip install fastapi-auth-kit
# or using uv
uv add fastapi-auth-kit
```

## 🛠️ Quickstart

1. Define your UserProvider:

```python
from fastapi_auth_kit.protocols import AuthUser, UserProvider

class MyUserProvider(UserProvider):
    async def get_by_id(self, user_id: str) -> AuthUser | None:
        # Tu lógica de base de datos aquí (SQLAlchemy, Motor, etc.)
        return await db.users.find_one({"id": user_id})
```

2. Configure and secure your routes:

```python
from fastapi import FastAPI, Depends
from fastapi_auth_kit import Auth, AuthConfig

auth = Auth(
    config=AuthConfig(secret_key="your-super-secret-key"),
    user_provider=MyUserProvider()
)

app = FastAPI()

@app.get("/me")
async def get_profile(user = Depends(auth.current_user)):
    return {"id": user.id, "active": user.is_active}
```

## License Agreement
`fastapi-auth-kit` is open source and free to use. Can be used for commercial purposes for free, but please clearly display the copyright information about **FastAPI-Auth-Kit** in the display interface.

## Copyright
Copyright (c) 2026 Kevin Manuel Espejel Martinez. All rights reserved.
