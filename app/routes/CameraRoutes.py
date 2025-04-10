from fastapi import APIRouter, BackgroundTasks, Request
import os
from starlette import status
from dotenv import load_dotenv
from app.services.DetectionServices import camera_service
from starlette.responses import JSONResponse
from fastapi.responses import StreamingResponse

# Load biến môi trường
load_dotenv()
public_endpoints = str(os.getenv("FAST_API_PUBLIC_ENDPOINTS"))
admin_endpoints = str(os.getenv("FAST_API_ADMIN_ENDPOINTS"))
user_endpoints = str(os.getenv("FAST_API_USER_ENDPOINTS"))

# Khởi tạo Router
router = APIRouter()

# Route lấy video từ camera
@router.get(user_endpoints + "/v1/video_feed")
async def video_feed(request: Request):
    return StreamingResponse(camera_service.start_camera(request), media_type="multipart/x-mixed-replace; boundary=frame")


@router.get(public_endpoints + "/v1/prediction")
async def prediction():
    if not camera_service.is_camera_running():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Camera is not running yet."}
        )
    
    label = camera_service.get_camera_detection()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"label": label}
    )

# @router.post(user_endpoints + "/v1/start")
# def start_processing():
#     CameraServices.start_processing()
#     return {"status": "started"}

# @router.post(user_endpoints + "/v1/stop")
# def stop_processing():
#     CameraServices.stop_processing()
#     return {"status": "stopped"}