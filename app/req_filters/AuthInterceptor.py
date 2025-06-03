import os
from dotenv import load_dotenv
from fastapi import Request, Response, FastAPI
from fastapi.responses import JSONResponse

from app.app_sql.setup_database import SessionLocal
from app.sql_crud import AccountCrud

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
                db_session = SessionLocal()

                user_id = request.cookies.get("user_id")
                if user_id is None:
                    user_id = request.headers.get("X-User-Id")
                print(user_id)
                if not user_id:
                    return JSONResponse(
                        content={"message": "Invalid session or insufficient permissions"},
                        status_code=403)

                account = AccountCrud.findByUserUserId(db_session, user_id)
                db_session.close()
                if not account.role:
                    return JSONResponse(
                        content={"message": "Invalid session or insufficient permissions"},
                        status_code=403)

                account.role = str(account.role).upper()
                if admin_prefix in request.url.path and account.role != "ADMIN":
                    return JSONResponse(
                        content={"message": "Invalid session or insufficient permissions"},
                        status_code=403)
                if user_prefix in request.url.path and account.role != "USER":
                    return JSONResponse(
                        content={"message": "Invalid session or insufficient permissions"},
                        status_code=403)

            # Call the next middleware or actual request handler
            response: Response = await call_next(request)
            return response