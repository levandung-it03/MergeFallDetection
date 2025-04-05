import os

from dotenv import load_dotenv

from fastapi import Request, APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.dtos.DetectionRoutesDto import Mpu6050Detection
from app.services import DetectionServices

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


@router.post(user_endpoints + "/v1/mpu6050-detection")
async def mpu6050Detection(request: Request, dto: Mpu6050Detection):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={ "msg": DetectionServices.handleMpu6050Prediction(request, dto) }
    )


@router.post(user_endpoints + "/v1/change-camera-status")
async def startCameraDetection(request: Request):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={ "msg": "Camera Status is changed to: " + DetectionServices.changeCameraStatus(request)})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={ "msg": "Camera failed to interaction"})


@router.post(user_endpoints + "/v1/get-camera-current-status")
async def getCameraCurrentStatus(request: Request):
    return JSONResponse(status_code=status.HTTP_200_OK, content={ "status": DetectionServices.getCameraCurrentStatus(request)})