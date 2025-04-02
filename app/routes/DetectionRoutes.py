import os

from dotenv import load_dotenv

from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

load_dotenv()
admin_endpoints = str(os.getenv("FAST_API_ADMIN_ENDPOINTS"))
user_endpoints = str(os.getenv("FAST_API_USER_ENDPOINTS"))
router = APIRouter()

@router.get(user_endpoints + "/v1/test")
async def test():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={ "msg": "Test Successfully" }
    )
