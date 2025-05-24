import smtplib
import cv2
import numpy as np
from email.message import EmailMessage

def send_email(image, sender_email, receiver_email, password):
    if image is None or not isinstance(image, np.ndarray):
        print("❌ Ảnh không hợp lệ để gửi email")
        return
    
    # Chuyển ảnh từ OpenCV sang định dạng JPEG
    _, buffer = cv2.imencode(".jpg", image)
    img_bytes = buffer.tobytes()

    msg = EmailMessage()
    msg["Subject"] = "⚠️ Cảnh báo té ngã"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Phát hiện té ngã! Hình ảnh được đính kèm.")

    # Đính kèm ảnh từ bộ nhớ
    msg.add_attachment(img_bytes, maintype="image", subtype="jpeg", filename="fall_detected.jpg")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        print("✅ Email đã được gửi thành công!")
    except Exception as e:
        print(f"❌ Lỗi khi gửi email: {e}")
