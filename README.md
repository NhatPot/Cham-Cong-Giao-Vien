# Chấm công giáo viên - Hướng dẫn nhanh

Mục tiêu: Teacher check-in/out (magic link + QR), Admin tạo dữ liệu, không tính tiền (chỉ tính giờ).

## 1) Chạy nhanh

### Linux (Ubuntu/Debian) - dùng conda (khuyến nghị)
```bash
conda create -n chamcong python=3.11 -y
conda activate chamcong
conda install -y -c conda-forge fastapi=0.115 pydantic=2.9 pydantic-core=2.23 uvicorn=0.30 sqlalchemy=2.0 jinja2 python-multipart python-dotenv qrcode pillow

cd "/home/nhat/Cong Viec/Cham Cong Giao Vien"
# Tạo .env (giá trị mẫu)
cat > .env << 'EOF'
ADMIN_KEY=changeme-admin
SECRET_KEY=changeme-secret
TZ=Asia/Ho_Chi_Minh
ORG_NAME=Sao Viet IT
EOF

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Windows - dùng conda
```cmd
conda create -n chamcong python=3.11 -y
conda activate chamcong
conda install -y -c conda-forge fastapi=0.115 pydantic=2.9 pydantic-core=2.23 uvicorn=0.30 sqlalchemy=2.0 jinja2 python-multipart python-dotenv qrcode pillow

cd "C:\path\to\Cham Cong Giao Vien"
(type nul > .env) & (echo ADMIN_KEY=changeme-admin>>.env) & (echo SECRET_KEY=changeme-secret>>.env) & (echo TZ=Asia/Ho_Chi_Minh>>.env) & (echo ORG_NAME=Sao Viet IT>>.env)

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ghi chú: Có thể dùng pip với `pip install -r requirements.txt` trong env conda nếu muốn.

## 2) Dùng hệ thống
- Admin: mở `http://localhost:8000/admin` với header `X-ADMIN-KEY: changeme-admin` (dùng ModHeader) để tạo giáo viên/lớp/buổi.
- Teacher: mở `http://localhost:8000/t/{magic_token}` (token lấy từ Admin hoặc seed).
- Kiosk QR: mở `http://localhost:8000/kiosk/session/{id}`.

Mẹo lấy nhanh token/ID (Linux):
```bash
sqlite3 database.db "select id,name,magic_token from teachers;"
sqlite3 database.db "select id,start_dt,end_dt from class_sessions;"
```

## 3) Tính giờ
- Công thức: min(checkout, end_dt) - max(checkin, start_dt), nếu âm thì 0.
- Lịch sử tháng và tổng giờ có tại `Teacher -> Lịch sử` và `Admin -> bảng công`.

## 4) Lỗi thường gặp (ngắn gọn)
- Lỗi pydantic/fastapi: tạo env conda mới và cài đúng phiên bản như trên.
- Không vào được Admin: thiếu header `X-ADMIN-KEY`.
- QR không quét: token hết hạn (30s) hoặc camera chưa cấp quyền.
- Port 8000 bận: Linux `sudo lsof -i :8000 && sudo kill -9 <PID>`; Windows `netstat -ano | findstr :8000` + `taskkill /PID <PID> /F`.

## 5) Cấu trúc thư mục (rút gọn)
```
app/
  main.py  db.py  models.py  schemas.py  security.py  seed.py
  routers/ (teacher.py, admin.py, qr.py)
  services/ (attendance.py, timesheet.py)
  templates/ (base.html, teacher_*.html, admin_home.html, kiosk_session.html)
  static/js/jsqr.min.js
requirements.txt  .env  database.db
```

## 6) Kiến trúc tổng thể (Demo mô hình)

### 6.1 Luồng chính
```
[Admin] --(X-ADMIN-KEY)--> /admin ----- tạo teacher/class/session -----> DB (SQLite)
     |                                                    |
     |                                                    +--> /kiosk/session/{id} (hiển thị QR xoay 25s)
     |
[Teacher] --(magic link)--> /t/{magic_token}
     |-- Manual: POST /t/{magic_token}/checkin|checkout
     |-- Scan QR: /t/{magic_token}/scan -> jsQR -> POST scan-checkin|scan-checkout

QR token: POST /qr/rotate hoặc GET /qr/generate/{id} -> token = base64url(session_id|exp).HMAC_SHA256
```

### 6.2 Mô hình dữ liệu (SQLite)
```
teachers(id, name, magic_token, hourly_rate, status)
classes(id, name, room)
class_teachers(id, class_id, teacher_id)        -- (N-N)
class_sessions(id, class_id, start_dt, end_dt, topic, status)
teacher_checkins(id, session_id, teacher_id, checkin_dt, checkout_dt, method)

Ràng buộc logic: 1 record mở duy nhất cho (session, teacher) khi checkout_dt IS NULL
```

### 6.3 Quy tắc thời gian
- Check-in: từ start_dt − 15' đến start_dt + 30'
- Check-out: từ end_dt − 30' đến end_dt + 60'
- Tính giờ một buổi: `max(0, min(checkout,end_dt) - max(checkin,start_dt))`
- Auto-close: khi quá `end_dt + 60'` mà còn mở thì đặt `checkout_dt = end_dt` (method="auto")

### 6.4 Bản đồ API (rút gọn)
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

