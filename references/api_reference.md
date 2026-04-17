# مرجع API — حقيبة الرياضة CMS

## جداول قاعدة البيانات الرئيسية

| الجدول | الوصف | الحقول الرئيسية |
|--------|-------|----------------|
| `localUsers` | الموظفون | id, username, password, role, branchId |
| `materials` | المنتجات/المواد | id, name, code, purchasePrice, consumerPrice, qualityGrade |
| `salesInvoices` | فواتير المبيعات | id, totalAmount, createdAt, createdBy, branchId |
| `purchaseInvoices` | فواتير المشتريات | id, totalAmount, supplierId |
| `orders` | الطلبات | id, trackingCode, status, isManagerOrder, priority, assignedTo |
| `orderStatusHistory` | تاريخ حالات الطلب | id, orderId, status, note, changedBy, changedAt |
| `shipments` | الشحنات | id, orderId, qrCode, currentStage, stages (JSON) |
| `workplaces` | أماكن العمل | id, name, latitude, longitude, radius |
| `attendanceLogs` | سجلات الحضور | id, employeeId, checkIn, checkOut, workplaceId |
| `employeeCards` | بطاقات الموظفين | id, employeeId, salary, achievements, negativeAchievements, customFields |
| `partners` | الشركاء | id, name, sharePercent, balance, whatsappNumber |
| `partnerTransactions` | معاملات الشركاء | id, partnerId, type, amount, date, note |
| `systemSettings` | إعدادات النظام | id, settingKey, settingValue, category |
| `staffSessions` | جلسات الموظفين | id, userId, loginAt, logoutAt, duration |
| `expenses` | المصاريف | id, amount, category, date, description |

---

## tRPC Procedures الرئيسية

### `trpc.materials`
- `list` — قائمة المواد مع فلاتر (بحث، فئة، مستودع)
- `getById` — تفاصيل مادة واحدة مع مصفوفة الألوان/المقاسات
- `create` — إنشاء مادة جديدة
- `update` — تحديث مادة
- `merge` — دمج مادتين
- `getMovements` — حركة مادة مفصلة (مشتريات، مبيعات، تحويلات)
- `inquire` — استعلام سريع عن مادة

### `trpc.orders`
- `list` — قائمة الطلبات مع فلاتر
- `create` — إنشاء طلب (يولّد trackingCode تلقائياً)
- `updateStatus` — تحديث حالة الطلب مع تسجيل التاريخ
- `getStatusHistory` — تاريخ حالات طلب معين
- `getByTrackingCode` — جلب طلب بكود التتبع (للزبون)

### `trpc.shipments`
- `list` — قائمة الشحنات
- `getByQR` — جلب شحنة بكود QR (للماسح)
- `updateStage` — تحديث مرحلة الشحنة مع تسجيل الوقت والمسؤول
- `generateQR` — توليد QR Code لشحنة

### `trpc.attendance`
- `checkIn` — تسجيل حضور
- `checkOut` — تسجيل انصراف
- `getTodayLogs` — سجلات اليوم
- `allStaffAttendance` — حضور جميع الموظفين (للمدير)

### `trpc.employeeCards`
- `getAll` — جميع بطاقات الموظفين
- `getByEmployeeId` — بطاقة موظف محدد
- `upsert` — إنشاء أو تحديث بطاقة
- `addCustomField` — إضافة حقل مخصص

### `trpc.systemSettings`
- `get` — جلب إعداد بمفتاحه
- `getAll` — جميع الإعدادات
- `set` — حفظ إعداد
- `getStaffSessions` — جلسات الموظفين النشطة

### `trpc.ai.adminChat`
- **للمدير فقط** (role === 'admin')
- يجلب: مبيعات الشهر الحالي والسابق، أرباح، مصاريف، مخزون منخفض
- يدعم: تعديلات النظام، ترتيب الأقسام، صلاحيات الموظفين
- يُرجع: `{ message, navigationPath?, action? }`

### `trpc.partnersEnhanced`
- `list` — قائمة الشركاء مع الأرصدة
- `getAnalytics` — تحليلات الشريك (أرباح، معاملات، نسب)
- `addTransaction` — إضافة معاملة (إيداع/سحب)
- `updateStatus` — تغيير حالة الشريك (نشط/طلب خروج)

---

## مراحل الشحن (17 مرحلة)

```typescript
type ShipmentStage =
  | 'pending'              // في انتظار التأكيد
  | 'confirmed'            // تم التأكيد
  | 'processing'           // قيد التجهيز
  | 'ready_for_pickup'     // جاهز للاستلام
  | 'picked_up_by_courier' // استلمه المندوب
  | 'in_transit'           // في الطريق
  | 'arrived_at_hub'       // وصل مركز الاستلام
  | 'out_for_delivery'     // في طريقه للزبون
  | 'delivered'            // تم التسليم
  | 'return_requested'     // طلب إرجاع
  | 'return_in_transit'    // مرتجع في الطريق
  | 'return_arrived'       // مرتجع وصل المركز
  | 'returned_to_store'    // تم تسليمه للمتجر
  | 'exchange_requested'   // طلب استبدال
  | 'exchange_processing'  // قيد الاستبدال
  | 'cancelled'            // ملغي
  | 'destroyed';           // إتلاف
```

---

## قواعد الأمان

- `protectedProcedure` — يتطلب تسجيل دخول
- `adminProcedure` — يتطلب `role === 'admin'`
- تعديلات المساعد الذكي: `adminChat` محمي بـ `role === 'admin'` حصراً
- بطاقات الموظفين: يراها المدير فقط، الموظف يرى بطاقته فقط

---

## المكتبات المثبّتة

```bash
pnpm add jsbarcode             # توليد باركود
pnpm add qrcode @types/qrcode  # توليد QR Code
pnpm add html5-qrcode          # ماسح QR بالكاميرا
# recharts مثبّتة مسبقاً للرسوم البيانية
```

---

## إضافة جداول قاعدة البيانات عبر SQL مباشر

عندما يفشل `pnpm db:push`، استخدم هذا النمط:

```javascript
// add-tables.mjs
import mysql from 'mysql2/promise';
const conn = await mysql.createConnection(process.env.DATABASE_URL);
await conn.execute(`ALTER TABLE orders ADD COLUMN IF NOT EXISTS tracking_code VARCHAR(50)`);
await conn.execute(`
  CREATE TABLE IF NOT EXISTS order_status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    note TEXT,
    changed_by INT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8)
  )
`);
await conn.end();
console.log('✅ تم إنشاء الجداول');
```

```bash
cd /home/ubuntu/sportsbag-cms && node add-tables.mjs
```
