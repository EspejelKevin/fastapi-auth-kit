from typing import Protocol, runtime_checkable, Sequence


@runtime_checkable
class AuthUser(Protocol):
    id: str | int
    is_active: bool = True

    roles: Sequence[str] = []
    permissions: Sequence[str] = []


class UserProvider(Protocol):
    async def get_by_id(self, user_id: str | int) -> AuthUser | None:
        ...
