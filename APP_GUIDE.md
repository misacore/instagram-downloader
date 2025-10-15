# راهنمای تبدیل به اپلیکیشن موبایل

## روش 1: نصب PWA (ساده‌ترین) ⭐

### اندروید:
1. سایت را در Chrome باز کنید
2. منو (⋮) > "Add to Home screen"
3. نام دلخواه انتخاب کنید
4. روی صفحه اصلی ایجاد می‌شود

### iOS:
1. سایت را در Safari باز کنید
2. دکمه Share > "Add to Home Screen"
3. نام را تأیید کنید

---

## روش 2: ساخت اپ با Capacitor

### نصب Capacitor:
```bash
npm install @capacitor/core @capacitor/cli
npx cap init
```

### اضافه کردن پلتفرم‌ها:
```bash
# Android
npx cap add android
npm install @capacitor/android

# iOS
npx cap add ios
npm install @capacitor/ios
```

### Build کردن:
```bash
# Build web files
npm run build

# Sync با native
npx cap sync

# باز کردن Android Studio
npx cap open android

# باز کردن Xcode
npx cap open ios
```

---

## روش 3: آپلود به Google Play

### پیش‌نیازها:
1. حساب Google Play Developer ($25 یکبار)
2. فایل APK یا AAB
3. آیکون‌ها و اسکرین‌شات‌ها
4. توضیحات و سیاست حریم خصوصی

### مراحل:
1. ساخت اپ با Capacitor یا React Native
2. امضای اپ (Signed APK/AAB)
3. آپلود به Google Play Console
4. تکمیل اطلاعات (توضیحات، تصاویر، ...)
5. ارسال برای بررسی

**زمان بررسی:** معمولاً 2-7 روز

---

## روش 4: استفاده از سرویس‌های آماده

### PWABuilder.com
- رایگان
- تبدیل PWA به Android/iOS/Windows
- لینک: https://www.pwabuilder.com/

### مراحل:
1. به https://www.pwabuilder.com بروید
2. لینک سایت را وارد کنید
3. "Build Package" را بزنید
4. پلتفرم Android را انتخاب کنید
5. فایل APK دانلود می‌شود

---

## پیشنهاد من:

### برای الان:
✅ از PWA استفاده کنید (نصب از سایت)

### برای آینده:
✅ اگر خواستید در Google Play باشید، از Capacitor استفاده کنید

---

## لینک‌های مفید:
- PWA Builder: https://www.pwabuilder.com/
- Capacitor: https://capacitorjs.com/
- Google Play Console: https://play.google.com/console/
