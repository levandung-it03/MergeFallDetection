from datetime import datetime

from app.app_sql.models import FallDetection
from app.app_sql.setup_database import SessionLocal
from app.dtos.DetectionRoutesDto import Mpu6050Detection
from fastapi import Request
import threading

from app.enum.Enums import CameraStatus, VirtualDBFile
from app.services.CameraModelServices import PoseStreamApp
from app.sql_crud import UserCrud, FallDetectionCrud
from app.virtual_db import VirtualDBCrud


class CameraService:
    def __init__(self):
        self.pose_stream_app = PoseStreamApp()
        self.video_thread = None

    def start_camera(self, request: Request):
        db_session = SessionLocal()
        cur_session = getattr(request.state, "session", {})
        user = UserCrud.findByAccountEmail(db_session, cur_session.get("email"))
        db_session.close()

        self.video_thread = threading.Thread(target=self.pose_stream_app.start_stream, args=(user,), daemon=True)
        self.video_thread.start()

        self.pose_stream_app.start_stream()
        self.pose_stream_app.detection_result = ""

    def stop_camera(self, request: Request):
        self.pose_stream_app.stop_stream()
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join()
        self.pose_stream_app.detection_result = ""

    def get_camera_detection(self):
        if self.video_thread and self.pose_stream_app:
            if self.pose_stream_app.detection_result != "":
                return self.pose_stream_app.detection_result
        return ""

def handleMpu6050Prediction(request: Request, mpu6050PredRes: Mpu6050Detection):
    db_session = SessionLocal()
    cur_session = getattr(request.state, "session", {})

    user = UserCrud.findByAccountEmail(db_session, cur_session.get("email"))
    user.camera_status = CameraStatus.PREDICT_ON
    UserCrud.updateById(user)

    db_session.close()

    camera_prediction = CameraService.get_camera_detection()
    merged_prediction = FallDetection(user_id=user.id, detected_img_url=None,
                                      mpu6050_res=mpu6050PredRes.mpu_best_class,
                                      camera_res=camera_prediction,
                                      created_time=datetime.now())
    if camera_prediction != "" and mpu6050PredRes.mpu_best_class != "":
        db_session = SessionLocal()
        FallDetectionCrud.save(db_session, merged_prediction)
        db_session.close()


def changeCameraStatus(request: Request):
    db_session = SessionLocal()
    cur_session = getattr(request.state, "session", {})
    user = UserCrud.findByAccountEmail(db_session, cur_session.get("email"))
    db_session.close()

    cam_status = VirtualDBCrud.read_property(VirtualDBFile.USER, user.id)
    if cam_status == CameraStatus.PREDICT_ON:
        VirtualDBCrud.write_property(VirtualDBFile.USER, user.id, CameraStatus.PREDICT_OFF)
        return CameraStatus.PREDICT_OFF
    else:
        VirtualDBCrud.write_property(VirtualDBFile.USER, user.id, CameraStatus.PREDICT_OFF)
        return CameraStatus.PREDICT_ON


def getCameraCurrentStatus(request: Request):
    cur_session = getattr(request.state, "session", {})
    user = UserCrud.findByAccountEmail(SessionLocal(), cur_session.get("email"))
    return VirtualDBCrud.read_property(VirtualDBFile.USER, user.id)
