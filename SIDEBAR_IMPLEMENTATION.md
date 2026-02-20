# Sidebar Component Implementation

## خلاصه پیاده‌سازی

یک کامپوننت Sidebar مدرن و واکنش‌گرا با قابلیت باز/بسته شدن برای برنامه Clinic CRM ایجاد شد.

## فایل‌های ایجاد شده

### Frontend

1. **`frontend/src/components/Sidebar.tsx`**
   - کامپوننت اصلی Sidebar با React Hooks
   - استفاده از `react-icons` برای آیکون‌ها
   - پشتیبانی از دو حالت: Expanded (250px) و Collapsed (70px)
   - نمایش آیتم‌های منو به فارسی

2. **`frontend/src/components/Sidebar.module.css`**
   - استایل‌های CSS با تم بنفش تیره (#1a0b40)
   - انیمیشن‌های نرم برای تغییر عرض
   - استایل‌های مخصوص حالت Collapsed

3. **`frontend/src/components/Layout.tsx`** (به‌روزرسانی شده)
   - ادغام Sidebar در Layout اصلی
   - مدیریت state برای باز/بسته شدن Sidebar
   - تنظیم margin برای محتوای اصلی

4. **`frontend/src/components/Layout.module.css`** (به‌روزرسانی شده)
   - اضافه شدن `.contentWrapper` برای مدیریت فاصله با Sidebar
   - Transition برای تغییرات نرم

### Backend

5. **`app/api/routes/navigation.py`**
   - Endpoint جدید: `GET /api/navigation/menu`
   - بازگرداندن ساختار منو به صورت JSON
   - شامل تمام آیتم‌های منو با برچسب‌های فارسی و انگلیسی

6. **`app/api/server.py`** (به‌روزرسانی شده)
   - اضافه شدن router برای navigation

## ویژگی‌ها

### ✅ طراحی و UI
- ✅ تم بنفش تیره (#1a0b40) با متن سفید
- ✅ دو حالت: Expanded (250px) و Collapsed (70px)
- ✅ Transition نرم برای تغییر عرض
- ✅ آیکون‌های زیبا از react-icons
- ✅ Highlight برای آیتم فعال

### ✅ عملکرد
- ✅ دکمه Toggle برای باز/بسته شدن
- ✅ Tooltip در حالت Collapsed
- ✅ دکمه‌های تبلیغاتی (فقط در حالت Expanded)
- ✅ لینک‌های Footer (Invite, Help)
- ✅ Responsive و سازگار با RTL

### ✅ Backend Integration
- ✅ API endpoint برای دریافت ساختار منو
- ✅ JSON Schema با Pydantic
- ✅ مستندات Swagger خودکار

## نحوه استفاده

### Frontend

```tsx
import Sidebar from './components/Sidebar'

function App() {
  const [sidebarExpanded, setSidebarExpanded] = useState(true)
  
  return (
    <Sidebar 
      isExpanded={sidebarExpanded} 
      onToggle={() => setSidebarExpanded(!sidebarExpanded)} 
    />
  )
}
```

### Backend API

```bash
# دریافت ساختار منو
GET /api/navigation/menu

# پاسخ:
[
  {
    "id": "patients",
    "label": "Patients",
    "label_fa": "بیماران",
    "icon_name": "FiUsers",
    "route": "/patients",
    "is_bottom_section": false
  },
  ...
]
```

## آیتم‌های منو

### منوی اصلی
1. شروع (Get started) - `/`
2. تقویم (Calendar) - `/appointments`
3. صندوق ورودی (Inbox) - `/inbox`
4. بیماران (Clients) - `/patients`
5. صورتحساب (Billing) - `/billing`
6. تیم شما (Your team) - `/team`
7. مخاطبین (Contacts) - `/contacts`
8. قالب‌ها (Templates) - `/templates`
9. گردش کار (Workflows) - `/workflows`
10. تنظیمات (Settings) - `/settings`

### Footer
- دعوت (Invite) - `/invite`
- راهنما (Help) - `/help`

## دکمه‌های تبلیغاتی

1. **"۵۰٪ تخفیف بگیرید!"**
   - گرادیان بنفش به نارنجی
   - آیکون شعله

2. **"رزرو تماس راه‌اندازی"**
   - پس‌زمینه سفید
   - آیکون تلفن

## وابستگی‌ها

```json
{
  "react-icons": "^latest"
}
```

نصب شده با:
```bash
npm install react-icons
```

## نکات مهم

1. **موقعیت Sidebar**: در سمت راست صفحه قرار دارد (متناسب با RTL)
2. **State Management**: State در Layout مدیریت می‌شود
3. **Responsive**: در موبایل می‌تواند به صورت Overlay نمایش داده شود
4. **Accessibility**: شامل aria-label و title برای دسترسی بهتر

## مراحل بعدی (پیشنهادی)

- [ ] اضافه کردن localStorage برای ذخیره state Sidebar
- [ ] اضافه کردن Overlay در حالت موبایل
- [ ] اضافه کردن Badge برای اعلان‌ها
- [ ] اضافه کردن Search در Sidebar
- [ ] اضافه کردن User Profile در بالای Sidebar
