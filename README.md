# Clinic CRM - سیستم مدیریت مطب

یک نرم‌افزار CRM سبک و کاربردی برای مطب‌های کوچک پزشکی با قابلیت اجرای آفلاین و آنلاین

## ویژگی‌های کلیدی

- **Local-First Architecture**: تمام داده‌ها ابتدا در SQLite محلی ذخیره می‌شوند
- **اجرای کاملاً آفلاین**: بدون نیاز به اینترنت قابل استفاده است
- **همگام‌سازی خودکار**: در صورت وجود اینترنت، داده‌ها با Supabase همگام می‌شوند
- **رابط کاربری دسکتاپ**: با PySide6 برای Windows
- **مصرف منابع پایین**: مناسب برای سیستم‌های ضعیف
- **API Backend**: FastAPI برای دسترسی از راه دور

## پیش‌نیازها

- Python 3.10 یا بالاتر
- pip (Python package manager)

## نصب و راه‌اندازی

### 1. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 2. تنظیمات محیطی

فایل `.env` را از `.env.example` کپی کرده و تنظیمات را انجام دهید:

```bash
cp .env.example .env
```

تنظیمات مهم در `.env`:

```env
# حالت اجرا: offline | online | hybrid
APP_MODE=offline

# مسیر دیتابیس محلی
LOCAL_DB_PATH=./data/clinic.db

# تنظیمات Supabase (فقط برای حالت آنلاین/هیبرید)
SUPABASE_URL=your-project-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# فعال/غیرفعال کردن همگام‌سازی خودکار
AUTO_SYNC_ENABLED=true
SYNC_INTERVAL_MINUTES=5
```

### 3. اجرای برنامه

#### حالت دسکتاپ (پیش‌فرض)

```bash
python -m app.main
```

#### حالت سرور API

```bash
uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8000
```

## ساخت فایل اجرایی (EXE)

برای ساخت فایل EXE برای ویندوز از PyInstaller استفاده می‌کنیم:

### 1. نصب PyInstaller

```bash
pip install pyinstaller
```

### 2. ایجاد Spec File

فایل `clinic_crm.spec` ایجاد شده است. محتوای آن را مشاهده کنید.

### 3. Build کردن

```bash
pyinstaller clinic_crm.spec
```

فایل EXE در پوشه `dist/ClinicCRM/` ایجاد خواهد شد.

### 4. توزیع

تمام محتویات پوشه `dist/ClinicCRM/` را به همراه هم توزیع کنید.

## ساختار پروژه

```
clinic-crm/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point برنامه دسکتاپ
│   ├── config.py            # تنظیمات برنامه
│   │
│   ├── database/            # لایه دیتابیس
│   │   ├── models.py        # مدل‌های SQLAlchemy
│   │   ├── local_db.py      # کانکشن SQLite
│   │   ├── remote_db.py     # کانکشن Supabase
│   │   └── sync.py          # موتور همگام‌سازی
│   │
│   ├── services/            # منطق تجاری
│   │   ├── patient_service.py
│   │   ├── appointment_service.py
│   │   └── report_service.py
│   │
│   ├── ui/                  # رابط کاربری PySide6
│   │   ├── main_window.py
│   │   └── widgets/
│   │       ├── patient_widget.py
│   │       ├── appointment_widget.py
│   │       └── report_widget.py
│   │
│   └── api/                 # FastAPI Backend
│       ├── server.py
│       └── routes/
│           ├── auth.py
│           ├── sync.py
│           └── appointments.py
│
├── data/                    # دیتابیس محلی (ایجاد خودکار)
├── requirements.txt
├── .env.example
└── README.md
```

## حالت‌های اجرا

### 1. Offline Mode (پیش‌فرض)

- همه چیز روی SQLite محلی کار می‌کند
- نیازی به اینترنت ندارد
- مناسب برای مطب‌های بدون اینترنت پایدار

### 2. Online Mode

- داده‌ها هم در SQLite و هم در Supabase ذخیره می‌شوند
- همگام‌سازی مداوم با سرور
- نیاز به اتصال دائم به اینترنت

### 3. Hybrid Mode (پیشنهادی)

- عملکرد اصلی بر روی SQLite محلی
- در صورت وجود اینترنت، همگام‌سازی خودکار
- بهترین حالت برای اکثر مطب‌ها

## API Documentation

پس از اجرای سرور، مستندات API در آدرس زیر در دسترس است:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### نمونه API Endpoints

```
GET  /                           - وضعیت برنامه
GET  /health                     - بررسی سلامت
POST /sync/trigger               - همگام‌سازی دستی

POST /api/auth/login             - ورود
POST /api/auth/logout            - خروج

POST /api/sync/manual            - همگام‌سازی دستی
GET  /api/sync/status            - وضعیت همگام‌سازی

POST /api/appointments/          - ایجاد نوبت
GET  /api/appointments/date/{clinic_id}/{date}  - نوبت‌های یک روز
GET  /api/appointments/upcoming/{clinic_id}     - نوبت‌های آینده
```

## ویژگی‌های برنامه

### مدیریت بیماران

- ثبت بیمار جدید با اطلاعات کامل
- جستجو بر اساس نام، کد ملی، تلفن
- ویرایش و حذف بیمار
- مدیریت سابقه پزشکی و حساسیت‌ها

### نوبت‌دهی

- مشاهده تقویم نوبت‌ها
- ثبت نوبت جدید
- تکمیل و لغو نوبت
- یادداشت‌های ویزیت
- مدیریت هزینه و پرداخت

### گزارشات

- گزارش درآمد روزانه
- گزارش درآمد ماهانه
- آمار کلی مطب
- سابقه ویزیت بیماران

### همگام‌سازی

- همگام‌سازی خودکار (قابل تنظیم)
- همگام‌سازی دستی
- لاگ همگام‌سازی
- مدیریت تعارض‌ها

## امنیت

- تمام داده‌ها در SQLite محلی به صورت ایمن ذخیره می‌شوند
- ارتباط با Supabase از طریق HTTPS
- Row Level Security (RLS) در Supabase
- JWT Authentication برای API
- Soft Delete برای جلوگیری از حذف تصادفی داده‌ها

## پشتیبانی و توسعه

### گزارش باگ

مشکلات و باگ‌ها را در بخش Issues گزارش دهید.

### توسعه

برای توسعه برنامه:

1. Fork کنید
2. یک branch جدید بسازید: `git checkout -b feature/amazing-feature`
3. تغییرات را commit کنید: `git commit -m 'Add amazing feature'`
4. Push کنید: `git push origin feature/amazing-feature`
5. Pull Request ایجاد کنید

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

## تماس و پشتیبانی

برای سوالات و پشتیبانی با ما تماس بگیرید.

---

**نکته مهم**: این برنامه به صورت Local-First طراحی شده که یعنی داده‌های شما همیشه در کنترل شماست و روی سیستم خودتان ذخیره می‌شود. همگام‌سازی با سرور اختیاری است.
