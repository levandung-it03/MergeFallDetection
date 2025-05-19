from datetime import datetime
from fastapi import Request, Response

from app.app_sql.models import User, Account
from app.app_sql.setup_database import SessionLocal
from app.enum.Enums import CameraStatus, VirtualDBFile
from app.routes.AccountRoutes import NewAccount, AuthAccount

from app.sql_crud import AccountCrud, UserCrud
from app.virtual_db import VirtualDBCrud
from app.dtos.AccountRoutesDto import UpdateAccount

def register(request: NewAccount):
    db_session = SessionLocal()

    new_account = Account(role="USER", email=request.email, password=request.password, created_time=datetime.now())
    new_account = AccountCrud.save(db_session, new_account)

    new_user = User(full_name=request.full_name, esp32_url=request.esp32_url, account_id=new_account.id)
    new_user = UserCrud.save(db_session, new_user)
    db_session.close()

    VirtualDBCrud.write_property(VirtualDBFile.USER, new_user.id, CameraStatus.PREDICT_OFF)
    return new_user

def authenticate(dto: AuthAccount):
    db_session = SessionLocal()
    try:
        user = UserCrud.findByAccountEmail(db_session, dto.email)
        if not user:
            raise Exception("User not found")
        return user
    finally:
        db_session.close()


def findUserIdByEmail(email):
    db_session = SessionLocal()
    user = UserCrud.findByAccountEmail(db_session, email)
    db_session.close()
    if not user:
        return None
    else:
        return user.id

def findUserByEmail(email):
    db_session = SessionLocal()
    user = UserCrud.findByAccountEmail(db_session, email)
    db_session.close()
    if not user:
        return None
    else:
        return user.id

def findUserByCookie(request: Request):
    user_id = request.cookies.get("user_id")
    db_session = SessionLocal()
    user = UserCrud.findById(db_session, user_id)
    db_session.close()
    if not user:
        return None
    else:
        return user
    
def changeESP32Url(data: UpdateAccount, request: Request):
    db_session = SessionLocal()
    user_id = request.cookies.get("user_id")

    updated_user = User(id=user_id,account_id=data.account_id,full_name=data.full_name, esp32_url=data.esp32_url)
    updated_user = UserCrud.updateById(db_session, updated_user)

    db_session.close()
    return updated_user
