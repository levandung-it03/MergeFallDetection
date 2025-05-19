# I Lý thuyết #
## 1. Phần cứng ##
### a. MPU6050 ###
### b. ESP32 .... ###
### c. ESP23Camera ###

## 2. Phần mềm ##
### a. CNN-1D ###
- Viết tắt của cái gì? Hoạt động thế nào (Dựa trên Neurol Network + Convolution).
- Vì sao chọn (Gen GPT: Trong MPU6050 nêu lý do chọn, vì cần realtime, vì nhẹ nhúng được,..)
### b. FreeRTOS ###
- Kêu GPT: giới thiệu.
- Tại sao dùng:
  + Vì ESP32 có hỗ trợ 2 core (nếu sai thì sửa).
  + Chạy 2 tasks song song (liên quan đến đồ án):
    + 1 Task lấy data (lưu vào Buffer) + trigger cam (video prediction)
    + Task còn lại chạy model predict + gửi kết quả cho backend
### b. Bộ nhớ trong của ESP32 (Preferences) và WiFi Manager ###
### d. <Model của Tuấn Anh> ###

# II Kết quả nghiên cứu #
## 1. Liên quan tới đoạn mã (code) ##
### a. Model CNN-1D ###
- Cách lấy dataset:
  - Lấy 4 nhãn gồm chill, fall-back (ngã ngửa), fall-forward (ngã sấp), stand.
  -> Lý do: phối hợp với camera (vì các động tác này camera khó nắm bắt).
  - Mỗi file gồm 25 dòng, mỗi dòng cách nhau 50ms.
  - Giả lập đúng cách động tác và giống nhau nhất có thể.
- Tiền xử lý dữ liệu:
  - Import file train và test (đo riêng để đạt hiệu quả tốt nhất, không dùng train_split_test vì sẽ làm hỏng dataset thông qua cách đo)
  - Gộp toàn bộ file dataset của 4 nhãn (các file cách nhau 1 line trống không có data)
  - Gắn nhãn tương ứng cho từng lines (tương ứng với files).
  - Đơn giản hoá data: chuyển toàn bộ dữ liệu nằm trong khoảng [0, 1] bằng cách
    - Gia tốc: (acceleration + 40) / 80
    - Gia tốc góc: (gyro + 40) / 80
  - Trải phẳng toàn bộ dữ liệu để chạy model CNN-1D.
- Thông số model:
  - Input gồm 15 lines (PREDICT_WINDOW), mỗi line cách nhau 50ms.
  - Dựng 1 layer gồm: 48 filters, kernel_size=3, activation=relu để:
    - Trải phẳng data input về mảng 1D
    - Bước đầu xây dựng các đặc trưng quan trọng
  - Dựng 1 layer gồm: 24 filters, kernel_size=3, activation=relu để:
    - Tập hợp các đặc trưng bị bỏ sót.
    - Tối ưu lại kết quả.
  - Dựng 1 layer output "Flatten" (hỏi GPT).
  - Huấn luyện với: epochs=125, bactch_size=15 (kích thước PREDICT_WINDOW).
  - CLASS_WEIGHTS = {
    fall_backward: 2.0,
    fall_forward: 1.5,
    stand: 1.0,
    chill: 1.0
  }

### b. Liên quan tới <Model Camera của Tuấn Anh> ###
