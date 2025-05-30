import os

from dotenv import load_dotenv

from fastapi import Request, APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.dtos.DetectionRoutesDto import Mpu6050Detection, TurnOnCameraPrediction
from app.routes.AccountRoutes import public_endpoints
from app.services import DetectionServices

load_dotenv()
admin_endpoints = str(os.getenv("FAST_API_ADMIN_ENDPOINTS"))
user_endpoints = str(os.getenv("FAST_API_USER_ENDPOINTS"))
router = APIRouter()


@router.post(public_endpoints + "/v1/mpu-pred-cls")
async def mpu6050Detection(dto: Mpu6050Detection):
    DetectionServices.handleMpu6050Prediction(dto)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={ "msg": "Received Data" }
    )


# This Route belongs to MPU6050.
@router.post(public_endpoints + "/v1/on-cam-pred-sts")
async def turnOnCameraPrediction(request: TurnOnCameraPrediction):
    try:
        DetectionServices.turnOnCameraPrediction(request)
        return JSONResponse(status_code=status.HTTP_200_OK, content={ "msg": "Turned On Prediction Cam Mode"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={ "msg": "Camera failed to interaction"})


# This Route belongs to User.
@router.post(user_endpoints + "/v1/change-camera-status")
async def changeCameraStatus(request: Request):
    try:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={ "msg": DetectionServices.changeCameraStatus(request)})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={ "msg": "Camera failed to interaction"})


@router.post(user_endpoints + "/v1/get-camera-current-status")
async def getCameraCurrentStatus(request: Request):
    return JSONResponse(status_code=status.HTTP_200_OK, content={ "status": DetectionServices.getCameraCurrentStatus(request)})