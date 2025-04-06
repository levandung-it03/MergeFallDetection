from pydantic import BaseModel

class Mpu6050Detection(BaseModel):
    user_id: int
    mpu_best_class: str

class ChangedCameraStatus(BaseModel):
    status: str

class TurnOnCameraPrediction(BaseModel):
    user_id: int