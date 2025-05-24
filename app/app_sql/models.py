import logging
from sqlalchemy import Integer, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.app_sql.setup_database import Base, engine

class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    created_time = Column(DateTime)
    role = Column(String(10), nullable=False)

    user = relationship("User", back_populates="account", uselist=False, cascade="all, delete")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "password": self.password,
            "created_time": self.created_time,
            "role": self.role,
        }


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    esp32_url = Column(String(255), nullable=False)

    account_id = Column(Integer, ForeignKey("account.id", ondelete="CASCADE"), unique=True, nullable=False)
    account = relationship("Account", back_populates="user", lazy='joined')

    fall_detections = relationship("FallDetection", back_populates="user", cascade="all, delete")

    def to_dict(self):
        logging.info(f"Account: {self.account}")
        return {
            "id": self.id,
            "full_name": self.full_name,
            "account_id": self.account_id,
            "esp32_url": self.esp32_url,
            "email": self.account.email if self.account else None
        }

class FallDetection(Base):
    __tablename__ = "fall_detection"

    id = Column(Integer, primary_key=True, autoincrement=True)
    detected_img_url = Column(String(255))
    mpu6050_res = Column(String(20), nullable=False)
    camera_res = Column(String(20), nullable=False)
    created_time = Column(DateTime)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="fall_detections")

    def to_dict(self):
        return {
            "id": self.id,
            "detected_img_url": self.detected_img_url,
            "mpu6050_res": self.mpu6050_res,
            "camera_res": self.camera_res,
            "created_time": self.created_time,
            "user_id": self.user_id,
        }

Base.metadata.create_all(engine)