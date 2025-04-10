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

        while True:
            if not frame_queue.empty():
                frame = frame_queue.get()  # Lấy frame từ hàng đợi
                try:
                    # Kiểm tra và gửi frame đã xử lý
                    ret, jpeg = cv2.imencode('.jpg', frame)
                    if ret:
                        frame_bytes = jpeg.tobytes()
                        yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                except Exception as e:
                    logging.error(f"Error encoding frame: {str(e)}")
                    continue

            # Giảm độ trễ giữa các frame (có thể sử dụng time.sleep hoặc tinh chỉnh tốc độ lấy frame)
            time.sleep(0.01) 

    def stop_camera(self, request: Request):
        self.pose_stream_app.stop_stream()
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join()
        self.pose_stream_app.detection_result = ""
        self.camera_started = False

    def is_camera_running(self):
        return self.camera_started

    def get_camera_detection(self):
        if self.video_thread and self.pose_stream_app:
            detection_result = self.pose_stream_app.detection_result # Đợi cho đến khi có kết quả phát hiện
            while detection_result == "":
                detection_result = self.pose_stream_app.detection_result    # Đợi cho đến khi có kết quả phát hiện
            # Reset detection result after getting it
            self.pose_stream_app.detection_result = ""
            return detection_result
        return ""


camera_service = CameraService()

def handleMpu6050Prediction(mpu6050PredRes: Mpu6050Detection):
    db_session = SessionLocal()

    user = UserCrud.findByAccountId(db_session, mpu6050PredRes.user_id)

    # Nếu camera chưa được bật, bật camera và chờ
    if not camera_service.is_camera_running():
        camera_service.start_camera(user)

    time.sleep(4)  # Chờ 4 giây để camera có thể bắt đầu phát hiện đúng theo thời gian được ra tín hiệu (có thể điều chỉnh lại sau này)
    camera_prediction = camera_service.get_camera_detection()
    merged_prediction = FallDetection(user_id=user.id, detected_img_url=None,
                                      mpu6050_res=mpu6050PredRes.mpu_best_class,
                                      camera_res=camera_prediction,
                                      created_time=datetime.now())
    print(merged_prediction.to_dict())
    if camera_prediction != "" and mpu6050PredRes.mpu_best_class != "":
        db_session = SessionLocal()
        FallDetectionCrud.save(db_session, merged_prediction)

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
