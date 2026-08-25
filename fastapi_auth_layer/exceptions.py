from fastapi import HTTPException, status


class AuthException(HTTPException):
    pass


class TokenExpiredException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired'
        )


class InvalidTokenException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )


class UserNotFoundException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found using provider'
        )


class UserInactiveException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User inactive'
        )


class InsufficientPermissionsException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have enough permissions to access this resource'
        )
