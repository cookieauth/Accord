# app/middleware.py
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.auth import get_current_user

class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            user = await get_current_user(request)
            request.state.user = user
        except HTTPException:
            request.state.user = None
        response = await call_next(request)
        return response
