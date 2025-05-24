import os

from dotenv import load_dotenv

from fastapi import APIRouter, Request
from starlette import status
from starlette.responses import JSONResponse

from app.dtos.AccountRoutesDto import NewAccount, AuthAccount, UpdateAccount
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
        response.set_cookie(key="user_id", value=auth_result.id, max_age=24*3600, httponly=True, secure=True, samesite="None")
        return response
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={ "msg": "Failed to login" })

@router.get(public_endpoints + "/v1/find-user-id-by-email")
async def findUserIdByEmail(email: str):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content={ "user_id": AccountServices.findUserIdByEmail(email) })
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={ "msg": "Wrong Email" })

@router.get(user_endpoints + "/v1/find-user")
async def findUserByCookie(request: Request):
    try:
        user = AccountServices.findUserByCookie(request)
        if not user:
            raise ValueError("User not found")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={ 
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "esp32_url": user.esp32_url,
                    "account_id": user.account_id,
                    "email": user.account.email
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={ "msg": "User not found" }
        )

@router.put(user_endpoints + "/v1/change_esp32_url")
async def changeESP32Url(data: UpdateAccount, request: Request):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={ "updated_user": AccountServices.changeESP32Url(data, request).to_dict() }
    )