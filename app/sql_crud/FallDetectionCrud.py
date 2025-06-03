from sqlalchemy.orm import Session

from app.app_sql.models import FallDetection

def save(db: Session, fallDetection: FallDetection):
    db.add(fallDetection)
    db.commit()
    db.refresh(fallDetection)
    return fallDetection

def findById(db: Session, fallDetectionId: int):
    return db.query(FallDetection).filter(FallDetection.id == fallDetectionId).first()

def deleteById(db: Session, fallDetectionId: int):
    db.delete(findById(db, fallDetectionId))
    db.commit()

def updateById(db: Session, fallDetection: FallDetection):
    raw = db.query(FallDetection).filter(FallDetection.id == fallDetection.id).first()
    if raw is None:
        return None
    raw.user_id = fallDetection.user_id
    raw.mpu6050_res = fallDetection.mpu6050_res
    raw.camera_res = fallDetection.camera_res
    raw.created_time = fallDetection.created_time
    db.commit()
    db.refresh(raw)
    return fallDetection


def updateCamPredResById(db: Session, detectId: int, cam_res: str):
    raw = db.query(FallDetection).filter(FallDetection.id == detectId).first()
    if raw is None:
        return None
    raw.camera_res = cam_res
    db.commit()
    db.refresh(raw)
    return raw

def findAll(db: Session):
    return db.query(FallDetection).all()

def findAllByFallDetectionId(db: Session, fallDetectionId: int):
    return db.query(FallDetection).filter(FallDetection.id == fallDetectionId).all()

def saveAll(db: Session, fallDetections: list[FallDetection]):
    for fallDetection in fallDetections:
        db.add(fallDetection)
    db.commit()
    for fallDetection in fallDetections:
        db.refresh(fallDetection)
    return fallDetections

def countAll(db: Session):
    return db.query(FallDetection).count()