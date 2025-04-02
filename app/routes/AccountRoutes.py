import os

from dotenv import load_dotenv

from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse
from fastapi import Request

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
async def register(request: Request, dto: AuthAccount):
    auth_result = AccountServices.authenticate(request, dto)
    if auth_result is None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={ "err_message": "Invalid credentials" })
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={ "user": auth_result.to_dict() }
        )