import os.path
import cv2
import numpy as np
import mediapipe as mp
from keras._tf_keras.keras.models import load_model
import time

from app.enum.Enums import CameraStatus, VirtualDBFile
from app.virtual_db import VirtualDBCrud

# Load trained model
# model_url = os.path.join(os.getcwd(), "app/machines/camera-model.h5")
# model = load_model(model_url)
model = None

# Mediapipe Pose Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils
labels = ["Falling", "Sitting", "Standing"]

class PoseStreamApp:
    def __init__(self):
        self.result_label = None
        self.sequence = []
        self.no_of_time_steps = 100
        self.num_features = 132  # Ensure input shape matches model
        self.detection_result = ""
        self.running = False

    def start_stream(self, user):
        cap = cv2.VideoCapture(user.esp32_url)

        if not cap.isOpened() and self.running:
            print(f"Lỗi: Không mở được stream từ {user.esp32_url}")
            self.result_label.setText("Lỗi: Không mở được stream")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(frame_rgb)
                if (results.pose_landmarks
                and VirtualDBCrud.read_property(VirtualDBFile.USER, user.id) == CameraStatus.PREDICT_ON):
                    print("Pose detected successfully")
                    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    landmarks = []
                    for lm in results.pose_landmarks.landmark:
                        landmarks.append(lm.x)
                        landmarks.append(lm.y)
                        landmarks.append(lm.z)
                        landmarks.append(lm.visibility)

                    while len(landmarks) < self.num_features:
                        landmarks.append(0.0)
                    landmarks = np.array(landmarks[:self.num_features])
                    '''Save sequence of lank-marks until it reach no_of_time_steps'''
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
            else:
                print("Lỗi: Không đọc được frame từ stream")
                break
        cap.release()
        print("Stream đã kết thúc.")

    def stop_stream(self):
        self.running = False