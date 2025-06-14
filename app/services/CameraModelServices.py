import os.path
import cv2
import numpy as np
import mediapipe as mp
from keras._tf_keras.keras.models import load_model
import time
import queue
import threading

from app.enum.Enums import CameraStatus, VirtualDBFile
from app.virtual_db import VirtualDBCrud
from app.services import DetectionServices
import os
import requests
import re

from app.services.email_sender import send_email

SENDER_EMAIL = "n21dccn013@student.ptithcm.edu.vn"
RECEIVER_EMAIL = "n21dccn013@student.ptithcm.edu.vn"
EMAIL_PASSWORD = "mmay jfmj dgrc qxpq"

def read_mjpeg_stream(url):
    stream = requests.get(url, stream=True)
    boundary = b"--frame"
    buffer = b""

    for chunk in stream.iter_content(chunk_size=4096):
        buffer += chunk
        while True:
            start = buffer.find(boundary)
            end = buffer.find(boundary, start + len(boundary))
            if start == -1 or end == -1:
                break

            part = buffer[start + len(boundary):end]
            buffer = buffer[end:]

            header_end = part.find(b"\r\n\r\n")
            if header_end == -1:
                continue

            headers = part[:header_end].decode(errors="ignore")
            body = part[header_end+4:]

            # Tìm timestamp trong header nếu có
            match = re.search(r"X-Timestamp:\s*(\d+)", headers)
            timestamp = int(match.group(1)) if match else None

            img = cv2.imdecode(np.frombuffer(body, np.uint8), cv2.IMREAD_COLOR)
            yield img, timestamp

def get_single_frame(url):
    try:
        response = requests.get(url + "/capture", timeout=5)
        if response.status_code == 200:
            img = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
            return img
        else:
            print("❌ Lỗi lấy ảnh:", response.status_code)
            return None
    except Exception as e:
        print("❌ Exception khi lấy ảnh:", e)
        return None

# Load trained model
model_url = os.path.join(os.getcwd(), "app/machines/camera-model.h5")
model = load_model(model_url)

# Mediapipe Pose Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils
labels = ["Falling", "Sitting", "Standing"]

def extract_jpeg_comment(jpeg_bytes):
    # Duyệt qua bytes để tìm marker 0xFFFE (JPEG comment)
    i = 2  # Bỏ qua SOI (0xFFD8)
    while i < len(jpeg_bytes) - 4:
        if jpeg_bytes[i] == 0xFF and jpeg_bytes[i + 1] == 0xFE:
            length = (jpeg_bytes[i + 2] << 8) + jpeg_bytes[i + 3]
            comment = jpeg_bytes[i + 4:i + 4 + length - 2]
            return comment.decode('utf-8')
        i += 1
    return None

class PoseStreamApp:
    def __init__(self):
        self.result_label = None
        self.sequence = []
        self.no_of_time_steps = 10
        self.num_features = 132  # Ensure input shape matches model
        self.detection_result = ""
        self.running = False
        self.last_email_time = 0

    def start_stream(self, user):
        self.running = True

        while self.running:
            frame = get_single_frame(user.esp32_url)
            ts = int(time.time() * 1000)  # Lấy timestamp hiện tại, vì server không trả trong capture
            if frame is None:
                print("❌ Không lấy được frame, thử lại sau...")
                time.sleep(0.1)
                continue

            print("📸 Timestamp:", ts)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)

            try:
                # Loại bỏ frame cũ nếu có
                DetectionServices.frame_queue.get_nowait()
            except queue.Empty:
                pass

            try:
                # Đưa frame mới vào queue
                DetectionServices.frame_queue.put_nowait(frame)
            except queue.Full:
                pass


            if (results.pose_landmarks and 
                VirtualDBCrud.read_property(VirtualDBFile.USER, user.id) == CameraStatus.PREDICT_ON):
                print("Pose detected successfully")
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                landmarks = []
                for lm in results.pose_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y, lm.z, lm.visibility])

                while len(landmarks) < self.num_features:
                    landmarks.append(0.0)
                landmarks = np.array(landmarks[:self.num_features])
                self.sequence.append(landmarks)

                if len(self.sequence) > self.no_of_time_steps:
                    self.sequence.pop(0)
                if len(self.sequence) == self.no_of_time_steps:
                    prediction = model.predict(np.expand_dims(self.sequence, axis=0))
                    label = np.argmax(prediction)
                    self.detection_result = labels[label]

                    if self.detection_result == "Falling":
                        current_time = time.time()
                        if current_time - self.last_email_time >= 30:
                            self.last_email_time = current_time
                            email_thread = threading.Thread(target=send_email, args=(frame, SENDER_EMAIL, user.account.email, EMAIL_PASSWORD))
                            email_thread.start()
                        else:
                            print("⏳ Chưa đủ 30 giây, bỏ qua gửi email!")

                    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(f"[{timestamp_str}] Phát hiện: {self.detection_result}")
                print("Status: Online - Detection: Online")
            else:
                print("Status: Online - Detection: Offline")

            time.sleep(0.05)  # Tốc độ lấy frame, điều chỉnh tùy ý

        print("Stream đã kết thúc.")


    def stop_stream(self):
        self.running = False
        self.sequence.clear()
