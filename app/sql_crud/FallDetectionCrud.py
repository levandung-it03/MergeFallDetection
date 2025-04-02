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

def updateById(db: Session, fallDetectionId: int, fallDetection: FallDetection):
    raw = db.query(FallDetection).filter(FallDetection.id == fallDetectionId).first()
    if raw is None:
        return None
    raw.user_id = fallDetection.user_id
    raw.detected_img_url = fallDetection.detected_img_url
    raw.detected_type = fallDetection.detected_type
    raw.created_time = fallDetection.created_time
    db.commit()
    db.refresh(raw)
    return fallDetection

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