import os

from dotenv import load_dotenv

from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.dtos.AccountRoutesDto import NewAccount, AuthAccount
from app.services import AccountServices

load_dotenv()
admin_endpoints = str(os.getenv("FAST_API_ADMIN_ENDPOINTS"))
user_endpoints = str(os.getenv("FAST_API_USER_ENDPOINTS"))
public_endpoints = str(os.getenv("FAST_API_PUBLIC_ENDPOINTS"))
router = APIRouter()

@router.post(public_endpoints + "/v1/register")
async def register(request: NewAccount):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={ "new_user": AccountServices.register(request).to_dict() }
    )

@router.post(public_endpoints + "/v1/authenticate")
async def authenticate(dto: AuthAccount):
    try:
        auth_result = AccountServices.authenticate(dto)
        response = JSONResponse(status_code=status.HTTP_200_OK, content={"msg": "Successfully Authenticated"})
        response.set_cookie(key="user_id", value=auth_result.id, max_age=24*3600, httponly=True, secure=False, samesite="lax")
        return response
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={ "msg": "Failed to login" })

@router.get(public_endpoints + "/v1/find-user-id-by-email")
async def findUserIdByEmail(email: str):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content={ "user_id": AccountServices.findUserIdByEmail(email) })
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={ "msg": "Wrong Email" })

