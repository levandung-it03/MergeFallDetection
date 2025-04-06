from pydantic import BaseModel

class Mpu6050Detection(BaseModel):
    mpu_best_class: str

class ChangedCameraStatus(BaseModel):
    status: str

class TurnOnCameraPrediction(BaseModel):
    user_id: str