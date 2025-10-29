# Chấm công giáo viên

Hệ thống chấm công cho giáo viên: check-in/out bằng magic link hoặc quét QR; Admin tạo dữ liệu vận hành; tính giờ làm việc theo phiên dạy (không tính tiền).

## Yêu cầu hệ thống
- Python 3.11
- SQLite (tích hợp sẵn, không cần cài thêm)
- Trình duyệt hiện đại (Chrome/Edge) để quét QR

Khuyến nghị Windows dùng PowerShell và một trong hai cách quản lý môi trường:
- venv + pip (đơn giản, mặc định)
- conda (nếu đã dùng Anaconda/Miniconda)

## Cài đặt trên Windows (PowerShell)

### Cách 1: Dùng venv + pip (khuyến nghị)
```powershell
# 1) Mở PowerShell tại thư mục dự án
cd "C:\Users\MinhNhat\Desktop\Sao Viet\Cham-Cong-Giao-Vien"

# 2) Tạo và kích hoạt môi trường ảo
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
./.venv/Scripts/Activate.ps1

# 3) Cập nhật pip và cài phụ thuộc
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4) Tạo file .env (giá trị mẫu)
@'
ADMIN_KEY=changeme-admin
SECRET_KEY=changeme-secret
TZ=Asia/Ho_Chi_Minh
ORG_NAME=Sao Viet IT
'@ | Out-File -Encoding utf8 .env
```

### Cách 2: Dùng conda
```powershell
conda create -n chamcong python=3.11 -y
conda activate chamcong
pip install -r requirements.txt

# Hoặc cài theo phiên bản cố định (nếu không dùng requirements.txt)
# conda install -y -c conda-forge fastapi=0.115 pydantic=2.9 pydantic-core=2.23 uvicorn=0.30 sqlalchemy=2.0 jinja2 python-multipart python-dotenv qrcode pillow

# Tạo file .env
@'
ADMIN_KEY=changeme-admin
SECRET_KEY=changeme-secret
TZ=Asia/Ho_Chi_Minh
ORG_NAME=Sao Viet IT
'@ | Out-File -Encoding utf8 .env
```

## Chạy ứng dụng
```powershell
# Từ thư mục dự án, khi môi trường đã được kích hoạt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Sau khi chạy, mở:
- Admin: http://localhost:8000/admin (dùng header `X-ADMIN-KEY: <ADMIN_KEY>`)
- Giáo viên: http://localhost:8000/t/{magic_token}
- Kiosk QR: http://localhost:8000/kiosk/session/{id}

Gợi ý cài tiện ích ModHeader trên trình duyệt để gửi header `X-ADMIN-KEY` khi truy cập trang Admin.

## Sử dụng nhanh cho Admin/Giáo viên
- Admin: tạo giáo viên, lớp, buổi học; xem bảng công theo tháng; xuất CSV.
- Giáo viên: nhận magic link, vào trang cá nhân để check-in/out hoặc quét QR.
- Kiosk: hiển thị QR tự xoay định kỳ, giáo viên quét để điểm danh.

## Cách tính giờ
- Công thức mỗi phiên: `max(0, min(checkout, end_dt) - max(checkin, start_dt))`
- Quy tắc thời gian:
  - Check-in: từ start_dt − 15' đến start_dt + 30'
  - Check-out: từ end_dt − 30' đến end_dt + 60'
  - Auto-close: quá `end_dt + 60'` mà còn mở thì đặt `checkout_dt = end_dt` (method="auto")

## Khắc phục sự cố trên Windows
- Không kích hoạt được venv do ExecutionPolicy: chạy lệnh đặt `RemoteSigned` như ở bước cài đặt.
- Thiếu gói/phụ thuộc: đảm bảo dùng Python 3.11 và cài bằng `pip install -r requirements.txt`.
- Không vào được Admin: kiểm tra đã gửi header `X-ADMIN-KEY` khớp với `ADMIN_KEY` trong `.env`.
- QR không quét: token hết hạn (30s) hoặc trình duyệt chưa cấp quyền camera.
- Cổng 8000 bận:
  - Kiểm tra PID: `netstat -ano | findstr :8000`
  - Kết thúc tiến trình: `taskkill /PID <PID> /F`

## Cấu trúc thư mục (rút gọn)
```
app/
  main.py  db.py  models.py  schemas.py  security.py  seed.py
  routers/ (teacher.py, admin.py, qr.py)
  services/ (attendance.py, timesheet.py)
  templates/ (base.html, teacher_*.html, admin_home.html, kiosk_session.html)
  static/js/jsqr.min.js
requirements.txt  .env  database.db
```

## Kiến trúc & API (rút gọn)

### Luồng chính
```
[Admin] --(X-ADMIN-KEY)--> /admin ---- tạo teacher/class/session -----> DB (SQLite)
     |                                                     |
     |                                                     +--> /kiosk/session/{id} (hiển thị QR xoay định kỳ)
     |
[Teacher] --(magic link)--> /t/{magic_token}
     |-- Manual: POST /t/{magic_token}/checkin|checkout
     |-- Scan QR: /t/{magic_token}/scan -> jsQR -> POST scan-checkin|scan-checkout

QR token: POST /qr/rotate hoặc GET /qr/generate/{id} -> token = base64url(session_id|exp).HMAC_SHA256
```

### Mô hình dữ liệu (SQLite)
```
teachers(id, name, magic_token, hourly_rate, status)
classes(id, name, room)
class_teachers(id, class_id, teacher_id)        -- (N-N)
class_sessions(id, class_id, start_dt, end_dt, topic, status)
teacher_checkins(id, session_id, teacher_id, checkin_dt, checkout_dt, method)

Ràng buộc logic: 1 record mở duy nhất cho (session, teacher) khi checkout_dt IS NULL
```

### Bản đồ API (rút gọn)
```
Teacher
- GET  /t/{magic_token}
- GET  /t/{magic_token}/scan
- GET  /t/{magic_token}/history?month=YYYY-MM
- POST /t/{magic_token}/checkin      (form: session_id)
- POST /t/{magic_token}/checkout     (form: session_id)
- POST /t/{magic_token}/scan-checkin (json: {session_id, qr_token})
- POST /t/{magic_token}/scan-checkout(json: {session_id, qr_token})

QR/Kiosk
- GET  /kiosk/session/{id}
- POST /qr/rotate        (form: session_id -> {token, expires_at})
- GET  /qr/generate/{id} (-> {token, expires_at, qr_image})

Admin (Header: X-ADMIN-KEY)
- GET  /admin
- POST /admin/teacher
- POST /admin/class
- POST /admin/class/{id}/add-teacher
- POST /admin/session
- GET  /admin/timesheet?month=YYYY-MM
- GET  /admin/timesheet/export.csv?month=YYYY-MM
```

