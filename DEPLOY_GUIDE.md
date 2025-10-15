# 🚀 راهنمای Deploy روی Render.com (رایگان)

## مرحله 1: ساخت حساب Render

1. به https://render.com بروید
2. Sign Up با GitHub یا ایمیل
3. حساب رایگان کافی است!

---

## مرحله 2: Upload کد به GitHub

### گزینه A: از طریق GitHub Desktop (ساده‌تر)

1. GitHub Desktop را نصب کنید
2. این پوشه را به GitHub بفرستید

### گزینه B: از طریق خط فرمان

```powershell
cd C:\Users\Mesi\Desktop\instagram-downloader

# ایجاد Git repo
git init
git add .
git commit -m "Initial commit"

# اتصال به GitHub (ابتدا یک repo در GitHub بسازید)
git remote add origin https://github.com/YOUR_USERNAME/instagram-downloader.git
git push -u origin main
```

---

## مرحله 3: Deploy روی Render

1. وارد Dashboard Render شوید
2. کلیک روی **"New +"** → **"Web Service"**
3. GitHub repo خود را متصل کنید
4. تنظیمات:
   - **Name**: instagram-downloader
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

5. کلیک روی **"Create Web Service"**

---

## مرحله 4: منتظر Deploy بمانید

- حدود 5-10 دقیقه طول می‌کشد
- وقتی تمام شد، یک URL دریافت می‌کنید:
  ```
  https://instagram-downloader-xxxx.onrender.com
  ```

---

## مرحله 5: استفاده در اپ

در اپ Flutter، آدرس سرور را تغییر دهید:
```
instagram-downloader-xxxx.onrender.com
```

(بدون http:// یا https://)

---

## ✅ مزایا:

- ✅ کاملاً رایگان
- ✅ 750 ساعت/ماه (کافی است)
- ✅ Auto-deploy وقتی کد را تغییر دهید
- ✅ HTTPS رایگان
- ✅ لاگ‌های کامل

---

## ⚠️ محدودیت:

- بعد از 15 دقیقه بی‌استفاده، خاموش می‌شود
- اولین request بعد از خاموش شدن 30 ثانیه طول می‌کشد
- برای استفاده شخصی کافی است!

---

## 🔧 اگر مشکلی بود:

1. در Render Dashboard → Logs را چک کنید
2. مطمئن شوید requirements.txt درست است
3. مطمئن شوید Procfile وجود دارد
