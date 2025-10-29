@echo off
REM Script tự động setup dự án trên Windows CMD

echo === Setup Hệ thống Chấm công Giáo viên ===

echo.
echo [1/5] Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo LỖI: Python chưa được cài đặt hoặc chưa có trong PATH!
    pause
    exit /b 1
)
python --version
echo OK: Python đã được cài đặt

echo.
echo [2/5] Tạo môi trường ảo...
if exist .venv (
    echo   Xóa .venv cũ...
    rmdir /s /q .venv
)
python -m venv .venv
if errorlevel 1 (
    echo LỖI: Không thể tạo .venv!
    pause
    exit /b 1
)
echo OK: Đã tạo .venv

echo.
echo [3/5] Kích hoạt môi trường...
call .\.venv\Scripts\activate.bat
if errorlevel 1 (
    echo LỖI: Không thể kích hoạt .venv!
    pause
    exit /b 1
)
echo OK: Đã kích hoạt .venv

echo.
echo [4/5] Cài đặt phụ thuộc (có thể mất vài phút)...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo LỖI: Không thể cài đặt dependencies!
    pause
    exit /b 1
)
echo OK: Đã cài đặt xong dependencies

echo.
echo [5/5] Tạo file .env...
if exist .env (
    echo   File .env đã tồn tại, bỏ qua...
) else (
    echo ADMIN_KEY=changeme-admin > .env
    echo SECRET_KEY=changeme-secret >> .env
    echo TZ=Asia/Ho_Chi_Minh >> .env
    echo ORG_NAME=Sao Viet IT >> .env
    echo OK: Đã tạo file .env
)

echo.
echo === HOÀN TẤT ===
echo.
echo Để chạy server, gõ lệnh:
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo Lưu ý: Môi trường .venv đã được kích hoạt.
pause

