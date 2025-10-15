@echo off
chcp 65001 >nul
title دانلودر اینستاگرام
color 0A

echo.
echo ========================================
echo     📸 دانلودر اینستاگرام
echo ========================================
echo.

echo [1/3] بررسی نصب کتابخانه‌ها...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  کتابخانه‌ها نصب نشده‌اند!
    echo 📦 در حال نصب...
    pip install -r requirements.txt
)

echo.
echo [2/3] ساخت آیکون‌های PWA...
if not exist static\icon-192.png (
    python create_icons.py
)

echo.
echo [3/3] شروع سرور...
echo.
echo ✅ سرور آماده است!
echo 🌐 آدرس: http://localhost:5000
echo.
echo برای خروج Ctrl+C را فشار دهید
echo ========================================
echo.

python app.py
pause
