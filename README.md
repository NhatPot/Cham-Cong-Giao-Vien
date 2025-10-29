# Hệ thống Chấm công Giáo viên

Hệ thống chấm công cho giáo viên với các tính năng:
- **Check-in/Check-out** bằng magic link hoặc quét QR code
- **Admin panel** để quản lý giáo viên, lớp học, buổi học
- **Kiosk QR** hiển thị mã QR tự động quay vòng
- **Tính giờ làm việc** theo phiên dạy (không tính tiền)

## Yêu cầu hệ thống

- **Python 3.11** (hoặc 3.10+)
- **SQLite** (tích hợp sẵn với Python, không cần cài thêm)
- **Trình duyệt hiện đại** (Chrome/Edge) để quét QR code
- **Windows 10/11** (hoặc Linux/Ubuntu)

## Cài đặt trên Windows

### ⚡ Cách nhanh nhất: Dùng script tự động

**Với PowerShell:**
```powershell
cd "C:\Users\MinhNhat\Desktop\Sao Viet\Cham-Cong-Giao-Vien"
.\setup.ps1
```

**Với CMD:**
```cmd
cd "C:\Users\MinhNhat\Desktop\Sao Viet\Cham-Cong-Giao-Vien"
setup.cmd
```

Script sẽ tự động:
- Tạo/xóa và kích hoạt `.venv`
- Cài đặt tất cả dependencies
- Tạo file `.env` (không có BOM)

Sau khi script chạy xong, chỉ cần chạy:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Cài đặt thủ công: Phương pháp 1: Dùng venv + pip (Khuyến nghị)

#### Với PowerShell:
```powershell
# Bước 1: Mở PowerShell tại thư mục dự án
cd "C:\Users\MinhNhat\Desktop\Sao Viet\Cham-Cong-Giao-Vien"

# Bước 2: Tạo môi trường ảo
python -m venv .venv

# Bước 3: Kích hoạt môi trường (nếu bị chặn, chạy lệnh ExecutionPolicy trước)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\.venv\Scripts\Activate.ps1

# Bước 4: Cập nhật pip và cài đặt phụ thuộc
python -m pip install --upgrade pip
pip install -r requirements.txt

# Bước 5: Tạo file .env (không có BOM để tránh lỗi)
[System.IO.File]::WriteAllText("$PWD\.env", "ADMIN_KEY=changeme-admin`nSECRET_KEY=changeme-secret`nTZ=Asia/Ho_Chi_Minh`nORG_NAME=Sao Viet IT", [System.Text.UTF8Encoding]::new($false))
```

#### Với CMD:
```cmd
REM Bước 1: Mở CMD tại thư mục dự án
cd "C:\Users\MinhNhat\Desktop\Sao Viet\Cham-Cong-Giao-Vien"

REM Bước 2: Tạo môi trường ảo
python -m venv .venv

REM Bước 3: Kích hoạt môi trường
.\.venv\Scripts\activate.bat

REM Bước 4: Cập nhật pip và cài đặt phụ thuộc
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Bước 5: Tạo file .env
echo ADMIN_KEY=changeme-admin > .env
echo SECRET_KEY=changeme-secret >> .env
echo TZ=Asia/Ho_Chi_Minh >> .env
echo ORG_NAME=Sao Viet IT >> .env
```

### Phương pháp 2: Dùng conda

**Lưu ý quan trọng**: Lần đầu sử dụng conda, bạn cần chấp nhận Terms of Service:
```cmd
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2
```

#### Với Anaconda Prompt (khuyến nghị):
```cmd
REM Bước 1: Mở Anaconda Prompt, vào thư mục dự án
cd "C:\Users\MinhNhat\Desktop\Sao Viet\Cham-Cong-Giao-Vien"

REM Bước 2: Tạo và kích hoạt môi trường
conda create -n chamcong python=3.11 -y
conda activate chamcong

REM Bước 3: Cài đặt phụ thuộc
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Bước 4: Tạo file .env
echo ADMIN_KEY=changeme-admin > .env
echo SECRET_KEY=changeme-secret >> .env
echo TZ=Asia/Ho_Chi_Minh >> .env
echo ORG_NAME=Sao Viet IT >> .env
```

#### Với PowerShell/CMD thường:
```powershell
# Bước 1: Khởi tạo conda cho PowerShell (chỉ cần 1 lần)
conda init powershell
# Hoặc với CMD:
conda init cmd.exe

# Sau đó ĐÓNG và mở lại PowerShell/CMD

# Bước 2: Vào thư mục dự án
cd "C:\Users\MinhNhat\Desktop\Sao Viet\Cham-Cong-Giao-Vien"

# Bước 3: Tạo và kích hoạt môi trường
conda create -n chamcong python=3.11 -y
conda activate chamcong

# Bước 4: Cài đặt phụ thuộc
python -m pip install --upgrade pip
pip install -r requirements.txt

# Bước 5: Tạo file .env (không có BOM để tránh lỗi)
[System.IO.File]::WriteAllText("$PWD\.env", "ADMIN_KEY=changeme-admin`nSECRET_KEY=changeme-secret`nTZ=Asia/Ho_Chi_Minh`nORG_NAME=Sao Viet IT", [System.Text.UTF8Encoding]::new($false))
```

## Chạy ứng dụng

Sau khi cài đặt xong, đảm bảo môi trường đã được kích hoạt (thấy `(.venv)` hoặc `(chamcong)` ở đầu dòng lệnh), sau đó chạy:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Kết quả mong đợi:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Hướng dẫn sử dụng

### 1. Truy cập Admin Panel

**⚠️ QUAN TRỌNG**: Admin panel yêu cầu header `X-ADMIN-KEY` để xác thực.

#### Cách 1: Dùng ModHeader (Tiện nhất - Khuyến nghị)

1. Cài tiện ích **ModHeader** trên trình duyệt:
   - Chrome: https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj
   - Edge: https://microsoftedge.microsoft.com/addons/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj

2. Mở ModHeader, thêm header:
   - **Name**: `X-ADMIN-KEY`
   - **Value**: `changeme-admin` (giá trị trong file `.env`)

3. Mở trình duyệt và truy cập: **http://localhost:8000/admin**

#### Cách 2: Dùng PowerShell để test
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/admin" -Headers @{"X-ADMIN-KEY"="changeme-admin"}
```

#### Cách 3: Dùng Postman/Insomnia
- **Method**: GET
- **URL**: http://localhost:8000/admin
- **Headers**: 
  ```
  X-ADMIN-KEY: changeme-admin
  ```

**Lưu ý**: Nếu không gửi header hoặc header sai, bạn sẽ nhận được lỗi `401 Unauthorized`.

### 2. Sử dụng Admin Panel

Sau khi truy cập thành công, bạn có thể:

1. **Tạo giáo viên mới**: Điền tên, mức lương/giờ, nhấn "Tạo giáo viên"
2. **Tạo lớp học**: Điền tên lớp, phòng (nếu có), nhấn "Tạo lớp"
3. **Tạo buổi học**: Chọn lớp, điền thời gian bắt đầu/kết thúc, chủ đề, nhấn "Tạo buổi"
4. **Gán giáo viên vào lớp**: Chọn lớp, chọn giáo viên, nhấn "Thêm giáo viên"
5. **Xem bảng công**: Chọn tháng, xem số giờ của từng giáo viên
6. **Xuất CSV**: Nhấn "Export CSV" để tải file Excel

**Magic Link cho giáo viên**: Sau khi tạo giáo viên, bạn sẽ nhận được magic link dạng `/t/{magic_token}`. Copy link này và gửi cho giáo viên.

### 3. Trang giáo viên (Teacher)

Giáo viên truy cập magic link được admin cung cấp:
- **Ví dụ**: http://localhost:8000/t/8257c9a4-1ad4-4541-969a-aa81be9606cd

Tại đây giáo viên có thể:
- **Check-in/Check-out** thủ công: Chọn buổi học, nhấn nút Check-in hoặc Check-out
- **Quét QR code**: Nhấn "Quét QR", cho phép camera, quét mã từ Kiosk
- **Xem lịch sử**: Nhấn "Lịch sử" để xem các buổi đã điểm danh trong tháng

**Quy tắc thời gian**:
- **Check-in**: Từ 15 phút trước đến 30 phút sau thời gian bắt đầu buổi học
- **Check-out**: Từ 30 phút trước đến 60 phút sau thời gian kết thúc buổi học

### 4. Kiosk QR Code

Admin tạo buổi học xong, sẽ có link Kiosk:
- **Ví dụ**: http://localhost:8000/kiosk/session/2

Mở link này trên màn hình/máy tính công cộng để hiển thị QR code tự động quay vòng (30 giây/lần). Giáo viên dùng điện thoại quét để điểm danh.

### 5. API Documentation

Truy cập: **http://localhost:8000/docs** để xem tất cả API endpoints và test trực tiếp.

## Khắc phục sự cố

### Lỗi khi kích hoạt venv (PowerShell)
**Lỗi**: `cannot be loaded because running scripts is disabled on this system`

**Giải pháp**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### Lỗi ValidationError khi load Settings
**Lỗi**: `Extra inputs are not permitted [type=extra_forbidden, input_value='changeme-admin', input_type=str]` hoặc `\ufeffadmin_key`

**Nguyên nhân**: File `.env` có BOM (Byte Order Mark) do dùng `Out-File -Encoding utf8`

**Giải pháp**: Tạo lại file `.env` không có BOM:
```powershell
# Xóa file cũ (nếu có)
Remove-Item .env -Force

# Tạo file mới không có BOM
[System.IO.File]::WriteAllText("$PWD\.env", "ADMIN_KEY=changeme-admin`nSECRET_KEY=changeme-secret`nTZ=Asia/Ho_Chi_Minh`nORG_NAME=Sao Viet IT", [System.Text.UTF8Encoding]::new($false))
```

### Lỗi khi dùng conda
**Lỗi**: `CondaToSNonInteractiveError: Terms of Service have not been accepted`

**Giải pháp**: Chạy các lệnh chấp nhận ToS như đã hướng dẫn ở phần "Phương pháp 2: Dùng conda"

### Lỗi 401 Unauthorized khi truy cập /admin
**Nguyên nhân**: Thiếu hoặc sai header `X-ADMIN-KEY`

**Giải pháp**:
1. Kiểm tra file `.env` có `ADMIN_KEY=changeme-admin` không
2. Đảm bảo đã thêm header `X-ADMIN-KEY: changeme-admin` khi truy cập
3. Dùng ModHeader như hướng dẫn ở phần "Truy cập Admin Panel"

### Lỗi 404 Not Found
**Nguyên nhân**: Server chưa chạy hoặc địa chỉ sai

**Giải pháp**:
1. Kiểm tra server đang chạy: mở http://localhost:8000/docs
2. Nếu không mở được, kiểm tra log server có lỗi không
3. Đảm bảo đã chạy `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Cổng 8000 đã được sử dụng
**Lỗi**: `Address already in use`

**Giải pháp (Windows)**:
```cmd
REM Tìm process đang dùng port 8000
netstat -ano | findstr :8000

REM Kết thúc process (thay <PID> bằng số tìm được)
taskkill /PID <PID> /F
```

### Thiếu gói/phụ thuộc
**Lỗi**: `ModuleNotFoundError: No module named 'xxx'`

**Giải pháp**:
1. Đảm bảo môi trường đã được kích hoạt
2. Chạy lại: `pip install -r requirements.txt`
3. Kiểm tra Python version: `python --version` (nên dùng 3.11)

### QR code không quét được
**Nguyên nhân**:
- Token QR đã hết hạn (có hiệu lực 30 giây)
- Trình duyệt chưa cấp quyền camera
- Camera không hoạt động

**Giải pháp**:
1. Cho phép trình duyệt truy cập camera
2. Thử refresh trang Kiosk để lấy QR code mới
3. Thử trình duyệt khác (Chrome khuyến nghị)

## Cấu trúc dự án

```
Cham-Cong-Giao-Vien/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point, FastAPI app
│   ├── db.py                # Database connection (SQLite)
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── security.py          # QR token signing/verification
│   ├── seed.py              # Initial data seeding
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── admin.py         # Admin endpoints
│   │   ├── teacher.py        # Teacher endpoints
│   │   └── qr.py            # QR/Kiosk endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── attendance.py    # Check-in/out logic
│   │   └── timesheet.py     # Hours calculation
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── admin_home.html
│   │   ├── teacher_home.html
│   │   ├── teacher_history.html
│   │   ├── teacher_scan.html
│   │   └── kiosk_session.html
│   └── static/
│       └── js/
│           └── jsqr.min.js  # QR code scanner library
├── .env                     # Environment variables (tạo sau khi cài)
├── database.db              # SQLite database (tự động tạo)
├── requirements.txt         # Python dependencies
└── README.md                # File này
```

## Kiến trúc hệ thống

### Sơ đồ kiến trúc

```mermaid
flowchart LR
    subgraph Clients
        A[Admin\nBrowser]
        T[Teacher\nBrowser]
        K[Kiosk\nBrowser]
    end

    subgraph App[FastAPI Application]
        R[Routers\n(admin, teacher, qr, kiosk)]
        S[Services\n(attendance, timesheet)]
        V[Templates\n(Jinja2 views)]
    end

    DB[(SQLite\ndatabase.db)]

    A <--> R
    T <--> R
    K <--> R
    R --> S
    R --> V
    S <--> DB
```

### Luồng hoạt động

1. **Admin** tạo dữ liệu (giáo viên, lớp, buổi học) → Lưu vào SQLite
2. **Admin** mở Kiosk → Hiển thị QR code tự động quay vòng
3. **Giáo viên** nhận magic link → Truy cập trang cá nhân
4. **Giáo viên** check-in/out (thủ công hoặc quét QR) → Lưu vào database
5. **Hệ thống** tính giờ làm việc tự động

### Mô hình dữ liệu

**Bảng chính:**
- `teachers`: Thông tin giáo viên (id, name, magic_token, hourly_rate, status)
- `classes`: Thông tin lớp học (id, name, room)
- `class_teachers`: Quan hệ N-N giữa lớp và giáo viên
- `class_sessions`: Buổi học (id, class_id, start_dt, end_dt, topic, status)
- `teacher_checkins`: Lịch sử điểm danh (id, session_id, teacher_id, checkin_dt, checkout_dt, method)

**Ràng buộc:**
- Mỗi (session, teacher) chỉ có 1 record mở (checkout_dt IS NULL) tại một thời điểm

### Công thức tính giờ

```
Giờ làm việc = max(0, min(checkout_dt, end_dt) - max(checkin_dt, start_dt))
```

- Nếu check-in trước `start_dt`, chỉ tính từ `start_dt`
- Nếu check-out sau `end_dt`, chỉ tính đến `end_dt`
- Nếu âm hoặc không hợp lệ, trả về 0

## API Endpoints

Xem chi tiết tại: http://localhost:8000/docs

**Tóm tắt:**
- **Admin** (yêu cầu header `X-ADMIN-KEY`): `/admin`, `/admin/teacher`, `/admin/class`, `/admin/session`, `/admin/timesheet`
  - Tạo: `POST /admin/teacher`, `POST /admin/class`, `POST /admin/session`
  - Xóa: `DELETE /admin/teacher/{id}`, `DELETE /admin/class/{id}`, `DELETE /admin/session/{id}`
- **Teacher** (dùng magic_token): `/t/{magic_token}`, `/t/{magic_token}/checkin`, `/t/{magic_token}/checkout`, `/t/{magic_token}/scan`
- **QR/Kiosk**: `/kiosk/session/{id}`, `/qr/rotate`, `/qr/generate/{id}`

## Lưu ý bảo mật

⚠️ **Quan trọng**: Đây là hệ thống demo, chưa sẵn sàng cho production.

1. **Đổi `ADMIN_KEY` và `SECRET_KEY`** trong file `.env` thành giá trị mạnh, ngẫu nhiên
2. **Bảo vệ file `.env`** - không commit lên Git
3. **Sử dụng HTTPS** trong môi trường production
4. **Backup database** thường xuyên (file `database.db`)
5. **Xem xét thêm** authentication/authorization cho production

## Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra lại các bước cài đặt
2. Xem phần "Khắc phục sự cố"
3. Kiểm tra log server để xem lỗi chi tiết
4. Truy cập http://localhost:8000/docs để test API trực tiếp

---

**Chúc bạn sử dụng thành công! 🎉**
