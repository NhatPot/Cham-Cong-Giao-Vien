# Script tự động setup dự án trên Windows PowerShell

Write-Host "=== Setup Hệ thống Chấm công Giáo viên ===" -ForegroundColor Green

# Kiểm tra Python
Write-Host "`n[1/5] Kiểm tra Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "LỖI: Python chưa được cài đặt hoặc chưa có trong PATH!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Tìm thấy: $pythonVersion" -ForegroundColor Green

# Xóa venv cũ (nếu có) và tạo mới
Write-Host "`n[2/5] Tạo môi trường ảo..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  Xóa .venv cũ..." -ForegroundColor Gray
    Remove-Item -Recurse -Force .venv
}
python -m venv .venv
Write-Host "✓ Đã tạo .venv" -ForegroundColor Green

# Kích hoạt venv
Write-Host "`n[3/5] Kích hoạt môi trường..." -ForegroundColor Yellow
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force -ErrorAction SilentlyContinue
& .\.venv\Scripts\Activate.ps1
Write-Host "✓ Đã kích hoạt .venv" -ForegroundColor Green

# Cài đặt dependencies
Write-Host "`n[4/5] Cài đặt phụ thuộc (có thể mất vài phút)..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "LỖI: Không thể cài đặt dependencies!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Đã cài đặt xong dependencies" -ForegroundColor Green

# Tạo file .env (không có BOM)
Write-Host "`n[5/5] Tạo file .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  File .env đã tồn tại, bỏ qua..." -ForegroundColor Gray
} else {
    [System.IO.File]::WriteAllText(
        "$PWD\.env", 
        "ADMIN_KEY=changeme-admin`nSECRET_KEY=changeme-secret`nTZ=Asia/Ho_Chi_Minh`nORG_NAME=Sao Viet IT", 
        [System.Text.UTF8Encoding]::new($false)
    )
    Write-Host "✓ Đã tạo file .env" -ForegroundColor Green
}

Write-Host "`n=== HOÀN TẤT ===" -ForegroundColor Green
Write-Host "`nĐể chạy server, gõ lệnh:" -ForegroundColor Cyan
Write-Host "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host "`nLưu ý: Môi trường .venv đã được kích hoạt trong shell này." -ForegroundColor Yellow

