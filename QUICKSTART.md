# راهنمای سریع - Clinic CRM

## شروع سریع برای کاربران

### نصب و اجرا

```bash
# 1. نصب وابستگی‌ها
pip install -r requirements.txt

# 2. کپی تنظیمات
cp .env.example .env

# 3. اجرای برنامه دسکتاپ
python run.py
```

## شروع سریع برای توسعه‌دهندگان

### ساختار پروژه

```
clinic-crm/
├── app/
│   ├── main.py              # Entry point اصلی
│   ├── config.py            # تنظیمات
│   ├── database/            # مدیریت دیتابیس
│   ├── services/            # منطق تجاری
│   ├── ui/                  # رابط کاربری
│   └── api/                 # REST API
├── docs/                    # مستندات
├── requirements.txt         # Dependencies
└── run.py                   # Launcher
```

### اجرا در حالت‌های مختلف

```bash
# حالت دسکتاپ
python run.py

# حالت سرور API
python run_server.py

# تست import
python -c "from app.database.local_db import local_db; print('OK')"
```

### Build برای Production

```bash
# نصب PyInstaller
pip install pyinstaller

# Build
pyinstaller clinic_crm.spec

# فایل exe در:
dist/ClinicCRM/ClinicCRM.exe
```

## ویژگی‌های کلیدی

- **Local-First**: کار بدون اینترنت
- **Auto Sync**: همگام‌سازی خودکار با Supabase
- **Desktop App**: PySide6
- **REST API**: FastAPI
- **Database**: SQLite + PostgreSQL

## تنظیمات مهم (.env)

```env
APP_MODE=offline              # offline | online | hybrid
LOCAL_DB_PATH=./data/clinic.db
SUPABASE_URL=your-url
SUPABASE_ANON_KEY=your-key
AUTO_SYNC_ENABLED=true
```

## مستندات کامل

- [README.md](README.md) - معرفی کامل
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - معماری سیستم
- [BUILD_GUIDE.md](docs/BUILD_GUIDE.md) - راهنمای build
- [USAGE.md](docs/USAGE.md) - راهنمای استفاده

## پشتیبانی

مشکل دارید؟
1. مستندات را بخوانید
2. در بخش Issues سوال بپرسید
3. با تیم پشتیبانی تماس بگیرید

---

**نکته**: این یک پروژه MVP است. برای استفاده تجاری، تست و بهینه‌سازی بیشتری نیاز دارد.
