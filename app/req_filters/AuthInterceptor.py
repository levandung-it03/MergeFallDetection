import os
from dotenv import load_dotenv
from fastapi import Request, Response, FastAPI
from fastapi.responses import JSONResponse

load_dotenv()

admin_prefix = os.getenv("FAST_API_ADMIN_ENDPOINTS") or ""
user_prefix = os.getenv("FAST_API_USER_ENDPOINTS") or ""

class AuthInterceptor:
    def __init__(self, app: FastAPI):
        self.app = app

    def turn_on(self):
        @self.app.middleware("http")
        async def dispatch(request: Request, call_next):
            print(f"Request: {request.method} {request.url}")

            if request.method != "OPTIONS" and (user_prefix in request.url.path or admin_prefix in request.url.path):
                cur_session = getattr(request.state, "session", {})

                email = cur_session.get("email")
                role = cur_session.get("role")

                if not email or not role:
                    return JSONResponse(
                        content={"message": "Invalid session or insufficient permissions"},
                        status_code=403)

                role = str(role).upper()

                if admin_prefix in request.url.path and role != "ADMIN":
                    return JSONResponse(
                        content={"message": "Invalid session or insufficient permissions"},
                        status_code=403)
                if user_prefix in request.url.path and role != "USER":
                    return JSONResponse(
                        content={"message": "Invalid session or insufficient permissions"},
                        status_code=403)

            # Call the next middleware or actual request handler
            response: Response = await call_next(request)
            return response