# Project setup script for Windows PowerShell

try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($true) } catch {}
Write-Host "=== Setup He thong Cham cong Giao vien ===" -ForegroundColor Green

# Check Python
Write-Host "`n[1/5] Kiem tra Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "LOI: Python chua duoc cai dat hoac chua co trong PATH!" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Tim thay $pythonVersion" -ForegroundColor Green

# Create fresh venv
Write-Host "`n[2/5] Tao moi truong ao..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "  Xoa .venv cu..." -ForegroundColor Gray
    Remove-Item -Recurse -Force .venv
}
python -m venv .venv
if ($LASTEXITCODE -ne 0 -or -not (Test-Path ".venv")) {
    Write-Host "LOI: Khong the tao .venv!" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Da tao .venv" -ForegroundColor Green

# Prepare venv (no activation required)
Write-Host "`n[3/5] Chuan bi moi truong (khong can kich hoat)..." -ForegroundColor Yellow
$venvPython = Join-Path ".venv" "Scripts/python.exe"
$venvPip = Join-Path ".venv" "Scripts/pip.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "LOI: Khong tim thay python trong .venv!" -ForegroundColor Red
    exit 1
}
# Optional activation; ignore policy errors
try { if (Test-Path ".venv/Scripts/Activate.ps1") { & .\.venv\Scripts\Activate.ps1 | Out-Null } } catch {}
Write-Host "OK: Da san sang su dung .venv" -ForegroundColor Green

# Install dependencies
Write-Host "`n[4/5] Cai dat phu thuoc (co the mat vai phut)..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "LOI: Khong the nang cap pip trong .venv!" -ForegroundColor Red
    exit 1
}
& $venvPip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "LOI: Khong the cai dat dependencies!" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Da cai dat xong dependencies" -ForegroundColor Green

# Create .env (no BOM)
Write-Host "`n[5/5] Tao file .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  File .env da ton tai, bo qua..." -ForegroundColor Gray
} else {
    $envContent = @'
ADMIN_KEY=changeme-admin
SECRET_KEY=changeme-secret
TZ=Asia/Ho_Chi_Minh
ORG_NAME=Sao Viet IT
'@
    $scriptRoot = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
    $envPath = Join-Path -Path $scriptRoot -ChildPath ".env"
    [System.IO.File]::WriteAllText($envPath, $envContent.TrimEnd(), [System.Text.UTF8Encoding]::new($false))
    Write-Host "OK: Da tao file .env" -ForegroundColor Green
}

Write-Host "`n=== HOAN TAT ===" -ForegroundColor Green
Write-Host "`nDe chay server, go lenh:" -ForegroundColor Cyan
Write-Host "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host "`nLuu y: Moi truong .venv khong can kich hoat de cai dat." -ForegroundColor Yellow

