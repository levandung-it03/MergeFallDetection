from datetime import datetime
import logging

from app.app_sql.models import FallDetection
from app.app_sql.setup_database import SessionLocal
from app.dtos.DetectionRoutesDto import Mpu6050Detection, TurnOnCameraPrediction
from fastapi import Request
import threading

from app.enum.Enums import CameraStatus, VirtualDBFile
from app.services.CameraModelServices import PoseStreamApp
from app.sql_crud import UserCrud, FallDetectionCrud
from app.virtual_db import VirtualDBCrud
from queue import Queue
import time
import cv2
import asyncio

frame_queue = Queue(maxsize=10)
class CameraService:
    def __init__(self):
        self.pose_stream_app = PoseStreamApp()
        self.video_thread = None
        self.camera_started = False

    def start_camera(self, request: Request):
        if self.camera_started:
            return

        db_session = SessionLocal()
        user_id = request.cookies.get("user_id")
        user = UserCrud.findById(db_session, user_id)
        db_session.close()

        self.video_thread = threading.Thread(target=self.pose_stream_app.start_stream, args=(user,), daemon=True)
        self.video_thread.start()

        self.camera_started = True
        self.pose_stream_app.detection_result = ""

    def stream_camera(self):
        while True:
            try:
                if not frame_queue.empty():
                    frame = frame_queue.get()
                    ret, jpeg = cv2.imencode('.jpg', frame)
                    if ret:
                        frame_bytes = jpeg.tobytes()
                        yield (
                            b"--frame\r\n"
                            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                        )
            except Exception as e:
                logging.exception("Streaming error")
            time.sleep(0.05)

    def stop_camera(self, request: Request):
        self.pose_stream_app.stop_stream()
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join()
        self.pose_stream_app.detection_result = ""
        self.camera_started = False

    def is_camera_running(self):
        return self.camera_started

    async def get_camera_detection(self, timeout_seconds=5):
        if self.video_thread and self.pose_stream_app:
            waited = 0
            interval = 0.1  # Kiểm tra mỗi 100ms
            while waited < timeout_seconds:
                detection_result = self.pose_stream_app.detection_result
                if detection_result != "":
                    self.pose_stream_app.detection_result = ""
                    return detection_result
                await asyncio.sleep(interval)
                waited += interval
        return ""

camera_service = CameraService()

async def handleMpu6050Prediction(request: Request, mpu6050PredRes: Mpu6050Detection):
    db_session = SessionLocal()

    user = UserCrud.findByAccountId(db_session, mpu6050PredRes.user_id)
    # Nếu camera chưa được bật, bật camera và chờ
    if not camera_service.is_camera_running():
        camera_service.start_camera(request)

    print("WAITING 4 SECONDS.....................................")
    time.sleep(4)  # Chờ 4 giây để camera có thể bắt đầu phát hiện đúng theo thời gian được ra tín hiệu (có thể điều chỉnh lại sau này)
    camera_prediction = await camera_service.get_camera_detection()   # None
    merged_prediction = FallDetection(user_id=user.id,
                                      mpu6050_res=mpu6050PredRes.mpu_best_class,
                                      camera_res=camera_prediction,
                                      created_time=datetime.now())
    print("PREDICTION RESULT:", merged_prediction.to_dict())
    if camera_prediction != "" and mpu6050PredRes.mpu_best_class != "":
        FallDetectionCrud.save(db_session, merged_prediction)
    VirtualDBCrud.write_property(VirtualDBFile.USER, user.id, CameraStatus.PREDICT_OFF) # Off prediction-mode
    db_session.close()

def turnOnCameraPrediction(request: TurnOnCameraPrediction):
    VirtualDBCrud.write_property(VirtualDBFile.USER, request.user_id, CameraStatus.PREDICT_ON)


def changeCameraStatus(request: Request):
    user_id = request.cookies.get("user_id")

    # Check current camera status by service (Thread's Properties)
    # if cam_sts == CameraStatus.CAM_ON:
        # Turn off cam by service
        # return CameraStatus.CAM_OFF
    # else:
        # Turn on cam by service
        # return CameraStatus.CAM_ON


def getCameraCurrentStatus(request: Request):
    user_id = request.cookies.get("user_id")
    # Check current camera status by service (Thread's Properties)
    return None
