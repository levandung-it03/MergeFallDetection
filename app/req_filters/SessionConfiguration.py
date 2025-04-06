import os
from uuid import UUID

from fastapi import HTTPException
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import CookieParameters, SessionCookie
from fastapi_sessions.session_verifier import SessionVerifier
from pydantic import BaseModel


class SessionData(BaseModel):
    email: str
    user_id: int
    role: str


cookie_params = CookieParameters()

backend = InMemoryBackend[UUID, SessionData]()
session_cookie = SessionCookie(
    cookie_name="session",
    identifier="session_cookie",
    auto_error=True,
    secret_key=os.getenv("SESSION_SECRET_KEY", "SECRET_KEY"),
    cookie_params=cookie_params,
)


class BasicSessionVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True

    async def verify_session(self, model: SessionData) -> bool:
        return bool(model.email and model.role and model.user_id)


verifier = BasicSessionVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
)