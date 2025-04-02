from datetime import datetime
from fastapi import Request

from app.app_sql.models import User, Account
from app.app_sql.setup_database import SessionLocal
from app.routes.AccountRoutes import NewAccount, AuthAccount

from app.sql_crud import AccountCrud, UserCrud


def register(request: NewAccount):
    db_session = SessionLocal()

    new_account = Account(role="USER", email=request.email, password=request.password, created_time=datetime.now())
    new_account = AccountCrud.save(db_session, new_account)

    new_user = User(full_name=request.full_name, esp32_url=request.esp32_url, account_id=new_account.id)
    new_user = AccountCrud.save(db_session, new_user)

    return new_user

def authenticate(request: Request, dto: AuthAccount):
    db_session = SessionLocal()

    try:
        cur_account = AccountCrud.findByEmail(db_session, dto.email)
        if not cur_account:
            return None  # No account found

        # Store session data (You should use a proper session system like Redis)
        request.state.session = {
            "email": cur_account.email,
            "role": cur_account.role
        }

        # Fetch user by correct account ID
        return UserCrud.findByAccountId(db_session, cur_account.id)  # ✅ Fix: Use cur_account.id

    finally:
        db_session.close()

