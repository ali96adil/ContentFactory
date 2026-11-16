# تسليم واستئناف مصنع المحتوى

آخر تحديث: 2026-11-17 (Asia/Baghdad)

## البيئة ونقطة Git

- المجلد: `/Users/aliadil/Projects/ContentFactory`
- macOS 27.0، Apple Silicon `arm64`، المساحة المتاحة وقت الفحص قرابة 200 GiB.
- الأدوات: Git 2.55.0، Node.js 24.21.0، Python 3.15.2، FFmpeg/FFprobe 7.1.1.
- `n8n` و`rsvg-convert` غير متاحين في PATH. Homebrew 7.0.14 موجود. محاولة `brew install librsvg` توقفت بعد تعليق التنزيل عند `Downloading Homebrew API data`، وأوقفتها دون صلاحيات إدارية.
- Git المحلي تهيأ في هذا المشروع؛ الـcommit المحلي الحالي يظهر بـ`git log -1 --oneline`.
- لا توجد أسرار في Git. ملف قالب الاعتمادات يحفظ أسماء الحالات فقط.

## آخر بوابة وحالتها

- بوابة فحص الملفات والبيئة: **PASS جزئي**. المرجع `ContentFactory_Implementation_Reference_AR.md` وقالب `ContentFactory_Credentials_Template.md` موجودان وقُرئا.
- الحزمة `ContentFactory_Lab_2026-11-16.zip`: **PASS**. فحص CRC نجح لـ44 مدخلاً و2,795,408 بايت غير مضغوط؛ لا مسارات مطلقة/اجتياز مجلد ولا روابط رمزية. فُكّت إلى `lab/`.
- توليد مصادر المشاهد: **PASS** بالأمر `cd lab && node motion.mjs`؛ ملفات SVG AR/EN موجودة تحت `lab/renders/`.
- اختبار الحالة والاستئناف: **PASS** بالأمر `cd lab && python3 test_checkpoint.py`: timeout/retry، إزالة تكرار متزامن، حجب الحقوق غير المثبتة، حجب وجهة public، سقف الإعادة، واستعادة SQLite.
- عينات MP4 المرفقة اجتازت FFprobe: H.264، 1080×1920، 24fps، 96 إطاراً، 4.0 ثوانٍ. هي أدلة سابقة داخل `lab/evidence/` وليست رندراً جديداً على هذا الماك.
- الرندر الجديد: **BLOCKED**. `python3 lab/render.py` فشل لأن بناء FFmpeg الحالي لا يحتوي SVG decoder؛ `rsvg-convert` غير مثبت. أُضيف `lab/render_mac.py` ليحوّل SVG عبر librsvg ثم يرمّز ويفحص MP4 عبر FFprobe، مع إبقاء سكربت الحزمة الأصلي دون تعديل.
- n8n: **BLOCKED / غير مثبت**؛ لذلك لم يُربط Workflow أو Data Tables ولم تُختبر دورة محلية عبر n8n. لم تُدخل اعتمادات.
- الميزانية الخارجية صفر، النشر الخارجي معطّل، وStageCore وKids Studio خارج النطاق.

## الأدلة والمخرجات

- الشيفرات والمواد المفكوكة: `lab/`
- معاينات الحزمة السابقة: `lab/evidence/librsvg-ar-TEST_ONLY.mp4` و`lab/evidence/librsvg-en-TEST_ONLY.mp4`
- تقرير القياسات السابقة: `lab/evidence/motion-metrics.json`
- مصادر SVG التي وُلّدت على هذا الماك: `lab/renders/ar/short/` و`lab/renders/en/short/`
- سجل هذه الجولة وحالة Git: هذا الملف و`git log -1 --oneline`.

## أول خطوة معلقة

أعد تشغيل تثبيت librsvg من Terminal كمستخدم عادي؛ المحاولة السابقة علقت أثناء تنزيل بيانات Homebrew:

```sh
cd /Users/aliadil/Projects/ContentFactory
brew install librsvg
python3 lab/render_mac.py
```

المتوقع: إنشاء معاينتي AR/EN حديثتين في `lab/evidence/` واجتياز تحقق FFprobe المضمن. بعد ذلك افحصهما، وسجّل المدة والحجم والبصمات. إذا ظل Homebrew معلقاً، سجّل ذلك كعائق تثبيت وانقل طلب المساعدة لمشغّل الماك؛ لا تستخدم `sudo`.

بعدها فقط، إذا تقرر إكمال ربط سير العمل، يلزم تثبيت n8n محلياً والتحقق من رخصته وملاءمته، ثم إعداد حساب المشغل ومفتاح التثبيت عبر واجهته/Keychain. لا تنسخ قيمة أي سر إلى Git أو المحادثة. استخدم العقد الجاهزة من n8n، ولا تنشئ Workflow قبل أن يصبح n8n متاحاً.
