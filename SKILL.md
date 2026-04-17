---
name: sportsbag-whitelabel
description: >
  تحويل مشروع حقيبة الرياضة CMS إلى منتج White-Label قابل للبيع لأي شركة.
  استخدم هذه المهارة عندما يطلب المستخدم:
  - بيع المشروع لعميل جديد بهوية مختلفة
  - تخصيص اسم الشركة والألوان والأيقونات والأقسام
  - تكييف النظام لقطاع مختلف (صرافة، صيدلية، مطعم، تجزئة...)
  - إنشاء نسخة جديدة من المشروع لعميل محدد
  - إضافة ميزات متقدمة للنظام الداخلي (تتبع شحنات، بطاقات موظفين، تحليلات، مساعد ذكي)
---

# مهارة White-Label — حقيبة الرياضة CMS

## نظرة عامة على النظام

نظام ERP/CMS متكامل مبني على React 19 + Tailwind 4 + tRPC 11 + MySQL (TiDB Cloud).
يُخصَّص لأي شركة بتعديل ملف واحد: `client/src/config/brand.ts`

### الوحدات الرئيسية المبنية

| الوحدة | المسار | الوصف |
|--------|--------|-------|
| الكاشير (POS) | `/cashier` | نقطة بيع كاملة — أول صفحة للموظف |
| إدارة المنتجات | `/products-new` | مصفوفة ألوان/مقاسات، دمج مواد، حركة مفصلة |
| تتبع الشحنات | `/shipment-tracking` | QR Code تلقائي + 17 مرحلة شحن + ماسح كاميرا |
| بطاقات الموظفين | `/employee-cards` | صورة، هوية، راتب، إنجازات، أخطاء، حقول مخصصة |
| تتبع الموقع الجغرافي | `/geo-attendance` | حضور تلقائي عند الوصول + إشعار ترحيبي |
| التحليل الاستراتيجي | `/business-analytics` | SWOT, BMC, PESTEL, 7Ps, تحليل المنافسين |
| تحليلات الشركاء | `/partners-analytics` | رسوم بيانية، نسب مشاركة، أرباح مستحقة |
| مولد الباركود | `/barcode-generator` | تخصيص كامل: نوع، ألوان، خط، تنزيل PNG/SVG |
| إعدادات النظام | `/system-settings` | مظهر، ألوان، خطوط، مراقبة الموظفين |
| المساعد الذكي | زر عائم | تحليل مبيعات حقيقية + تعديلات النظام للمدير |

---

## سير العمل: تخصيص لعميل جديد

### الخطوة 1: جمع معلومات العميل

اسأل عن (أو استنتج من السياق):
- اسم الشركة (عربي + إنجليزي)
- القطاع: `retail_sports | exchange | pharmacy | restaurant | general`
- المدينة والموقع
- اللون الرئيسي المفضّل
- الأقسام المطلوبة
- عدد الفروع وأسماؤها

### الخطوة 2: إنشاء ملف JSON للعميل

```json
{
  "name": "اسم الشركة",
  "nameEn": "Company Name",
  "tagline": "الشعار التسويقي",
  "industry": "exchange",
  "city": "حلب",
  "primary_color": "#1e40af",
  "dashboard_focus": "accounting",
  "modules": {
    "inventory": false,
    "accounting": true,
    "exchange": true
  }
}
```

مثال جاهز: `references/client_alyaqeen_example.json`

### الخطوة 3: تشغيل سكريبت التخصيص

```bash
python /home/ubuntu/skills/sportsbag-whitelabel/scripts/customize.py \
  <client_config.json> \
  /home/ubuntu/sportsbag-cms
```

يُعدّل تلقائياً: `brand.ts` + `manifest.json` + `index.html`

### الخطوة 4: التعديلات اليدوية حسب القطاع

**للصرافة (`exchange`):** فعّل `ExchangeDashboard.tsx` كصفحة رئيسية، أخفِ المتجر والمخزون

**للصيدلية (`pharmacy`):** أبقِ المخزون والمحاسبة، أخفِ المتجر والحملات

**للمطعم (`restaurant`):** أبقِ POS والمحاسبة، أخفِ المخزون التقليدي

---

## إضافة ميزات متقدمة للنظام

### نظام تتبع الشحنات (طلب 8)

**قاعدة البيانات:** جدول `orderStatusHistory` مع حقول: `orderId, status, note, changedBy, changedAt, latitude, longitude`

**مراحل الشحن المدعومة (17 مرحلة):**
```
pending → confirmed → processing → ready_for_pickup
→ picked_up_by_courier → in_transit → arrived_at_hub
→ out_for_delivery → delivered → return_requested
→ return_in_transit → return_arrived → returned_to_store
→ exchange_requested → exchange_processing → cancelled → destroyed
```

**توليد QR Code:** عند إنشاء أي طلب، يُولَّد `trackingCode` تلقائياً:
```typescript
const trackingCode = `SB-${Date.now()}-${Math.random().toString(36).substr(2,6).toUpperCase()}`;
```

**ماسح QR:** استخدم مكتبة `html5-qrcode` للمسح بالكاميرا:
```bash
pnpm add html5-qrcode
```

### بطاقات الموظفين المفصلة (طلب 3)

**جدول قاعدة البيانات:** `employeeCards` مع الحقول:
- `employeeId, photoUrl, idCardUrl, nationalId`
- `salary, profitPercent, monthlyRating`
- `maxDebtLimit, whatsappNumber, emergencyContact`
- `achievements (JSON), negativeAchievements (JSON)`
- `customFields (JSON)` — حقول قابلة للإضافة ديناميكياً
- `hireDate, notes`

**Router:** `server/routers/employeeCards.ts`

### تتبع الموقع الجغرافي (طلب 2)

**الجداول المطلوبة في `drizzle/schema.ts`:**
```typescript
// إضافة لجدول workplaces:
latitude: decimal('latitude', { precision: 10, scale: 8 })
longitude: decimal('longitude', { precision: 11, scale: 8 })
radius: int('radius').default(200) // متر
```

**منطق الحضور التلقائي:**
```typescript
// احسب المسافة بـ Haversine formula
const distance = haversine(userLat, userLng, workLat, workLng);
if (distance <= workplace.radius) { /* تسجيل حضور تلقائي */ }
```

**الإشعار الترحيبي:** استخدم `Notification API` في المتصفح:
```typescript
new Notification("أهلاً بك في بيئة راحتك النفسية 💜", {
  body: "لا تستصغر نفسك!! أنت شريك نجاح لحقيبة الرياضة",
  icon: "/logo.png"
});
```

### المساعد الذكي مع تحليلات حقيقية

**في `adminChat` procedure بـ `server/routers.ts`:**
```typescript
// جلب بيانات المبيعات للشهر الحالي والسابق
const thisMonthSales = await db.select({ total: sum(salesInvoices.totalAmount) })
  .from(salesInvoices)
  .where(gte(salesInvoices.createdAt, startOfMonth));

// حساب نسبة التغيير
const changePercent = ((thisMonth - lastMonth) / lastMonth * 100).toFixed(1);
```

**صلاحيات تعديل النظام:** تُتاح فقط لمستخدم بدور `admin`:
```typescript
if (ctx.user?.role !== 'admin') {
  throw new TRPCError({ code: 'FORBIDDEN' });
}
```

### أدوات التحليل الاستراتيجي

**الأدوات المدعومة:** SWOT، BMC (Business Model Canvas)، PESTEL، 7Ps، تحليل المنافسين، تحليل المخاطر

**صفحة:** `client/src/pages/BusinessAnalytics.tsx`

**كل أداة تحتوي على:** نموذج إدخال بيانات + عرض بصري احترافي + زر تصدير PDF

---

## إضافة جداول قاعدة البيانات عبر SQL مباشر

عندما يفشل `pnpm db:push`، استخدم SQL مباشر:

```javascript
// add-tables.mjs
import mysql from 'mysql2/promise';
const conn = await mysql.createConnection(process.env.DATABASE_URL);
await conn.execute(`ALTER TABLE orders ADD COLUMN tracking_code VARCHAR(50)`);
await conn.execute(`CREATE TABLE IF NOT EXISTS order_status_history (...)`);
await conn.end();
```

```bash
cd /home/ubuntu/sportsbag-cms && node add-tables.mjs
```

---

## التخصيص المتقدم

### تغيير الشعار
1. ارفع الشعار: `manus-upload-file --webdev logo.png`
2. حدّث `BRAND.logo.main` في `brand.ts`

### تغيير الألوان
عدّل `client/src/index.css` في قسم `:root`:
```css
:root { --primary: <اللون>; }
```

### تغيير توجيه الموظف بعد تسجيل الدخول
في `client/src/pages/Login.tsx`:
```typescript
// وجّه للكاشير بدلاً من لوحة التحكم
setLocation('/cashier');
```

---

## قائمة التحقق قبل التسليم

- [ ] تحديث `brand.ts` بمعلومات العميل
- [ ] تشغيل `scripts/customize.py` مع ملف JSON العميل
- [ ] تحديث الشعار والأيقونات
- [ ] تعطيل الأقسام غير المطلوبة في `DashboardLayout.tsx`
- [ ] اختبار PWA على الجوال
- [ ] تحديث أرقام واتساب في `brand.ts`
- [ ] التحقق من عدم وجود أخطاء TypeScript: `npx tsc --noEmit --skipLibCheck`
- [ ] `webdev_save_checkpoint` وإعطاء العميل رابط النشر

---

## ملاحظات تقنية مهمة

- لا تعدّل `server/_core/` أبداً
- بيانات الشركة في `brand.ts` تُستخدم في 41+ ملف
- قاعدة البيانات سحابية TiDB Cloud — لا تحتاج إعداداً
- جميع الـ routers في `server/routers/` — أضف router جديد وسجّله في `server/routers.ts`
- استخدم `sql template literals` بدلاً من `db.execute()` مباشرة
- للـ QR Code: `pnpm add qrcode @types/qrcode`
- للباركود: `pnpm add jsbarcode`
- للماسح: `pnpm add html5-qrcode`
- للرسوم البيانية: `recharts` مثبّتة مسبقاً

## مرجع الملفات الرئيسية

راجع `references/api_reference.md` للتفاصيل الكاملة لكل procedure وجدول في قاعدة البيانات.

---

## الرؤية المستقبلية — يزن مقرش (أبو البراء)

> هذا النظام ليس مجرد برنامج إدارة — بل بنية تحتية لشركة رياضية سورية تسعى لقيادة السوق محلياً والتوسع إقليمياً.

### المرحلة القادمة: التوسع الجغرافي
- **نسخ White-Label** لشركات رياضية أخرى في سوريا والشرق الأوسط
- **تكامل مع منصات التجارة الإلكترونية** (Shopify، WooCommerce) لربط المخزون الرقمي بالمتاجر الفعلية
- **تطبيق موبايل** للموظفين يعمل مع نظام الحضور الجغرافي

### الأقسام المخطط بناؤها
- **بوابة الزبائن** — تتبع الطلبات + سجل الشراء + نقاط الولاء
- **نظام المحاسبة الكامل** — ميزانية عمومية، قائمة دخل، تدفقات نقدية
- **صندوق الرسائل الموحد** — Facebook + Instagram + WhatsApp في مكان واحد
- **تقارير PDF تلقائية** — تقرير يومي/أسبوعي/شهري يُرسل للمدير تلقائياً
- **نظام نقاط الولاء** — مكافأة الزبائن المتكررين وتحفيز المبيعات

### القيم الجوهرية للنظام
- **الدقة أولاً** — لا خلط بين موديل وآخر، لا بيانات وهمية
- **الموظف شريك** — النظام يُقدّر الموظف ويتتبع إنجازاته لا فقط أخطاءه
- **الشفافية الكاملة** — المدير يرى كل شيء في الوقت الفعلي
- **التوسع المدروس** — كل ميزة جديدة تُبنى على أساس متين

---

## ⚠️ ملاحظات الحفظ الدائم

**هذه المهارة تلخّص مئات ساعات العمل المشترك مع يزن مقرش (أبو البراء). يجب:**

1. **عدم حذفها أو استبدالها** — هي المرجع الأساسي لكل تطوير مستقبلي
2. **قراءتها قبل أي تطوير** — تحتوي على قرارات تصميمية مهمة ومبررة
3. **تحديثها بعد كل جلسة تطوير كبيرة** — لتبقى دائماً محدّثة
4. **مزامنتها مع GitHub** — لضمان نسخة احتياطية خارج البيئة المحلية

**الموقع الرسمي للنظام:** `sport-store.net`
**المستودع:** `github.com/yazanmaqrash/sportsbag-cms-skill` (بعد المزامنة)
**آخر تحديث:** أبريل 2026 — بعد إضافة تتبع الشحنات، بطاقات الموظفين، المساعد الذكي، الباركود، والتحليلات الاستراتيجية
