import os.path
import cv2
import numpy as np
import mediapipe as mp
from keras._tf_keras.keras.models import load_model
import time
import queue

from app.enum.Enums import CameraStatus, VirtualDBFile
from app.virtual_db import VirtualDBCrud
from app.services import DetectionServices
import os
import requests
import re

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


frame_queue = queue.Queue(maxsize=10)

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
        self.no_of_time_steps = 100
        self.num_features = 132  # Ensure input shape matches model
        self.detection_result = ""
        self.running = False

    def start_stream(self, user):
        self.running = True

        for frame, ts in read_mjpeg_stream(user.esp32_url):
            if not self.running:
                break

            if ts:
                print("📸 Timestamp từ ESP32:", ts)
            else:
                print("❌ Không tìm thấy timestamp")

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)

            if not frame_queue.full():
                DetectionServices.frame_queue.put(frame)

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

                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(f"[{timestamp}] Phát hiện: {self.detection_result}")
                print("Status: Online - Detection: Online")
            else:
                print("Status: Online - Detection: Offline")

        print("Stream đã kết thúc.")


    def stop_stream(self):
        self.running = False
        self.sequence.clear()
