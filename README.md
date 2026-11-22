# ContentFactory

# مصنع المحتوى الذكي

مختبر محلي لحزم محتوى معرفي أصلية بالعربية البيضاء والإنكليزية. الميزانية الخارجية صفر، النشر الخارجي معطّل، وStageCore وKids Studio خارج النطاق. الفيديوهات والتقارير البصرية تحت `lab/evidence/` تجريبية محلية وليست معتمدة للإنتاج.

## الحالة والقيود

- العقد والقالب: `docs/CONTENT_PACKAGE_CONTRACT.md` و`lab/templates/content-package-template.json`.
- الصوت العربي الطبيعي المرخص تجارياً فجوة مفتوحة؛ لا يوجد صوت عربي معتمد للإنتاج.
- n8n `2.47.7` مثبت كحزمة محلية لكن الخدمة متوقفة بسبب مراجعة الثغرات؛ لا تشغّله قبل مراجعة `docs/N8N_AUDIT_REVIEW.md`.
- لا توجد موصلات أداء منصة فعلية. بيانات المنصات في `lab/fixtures/` اصطناعية للاختبار فقط؛ صادرات المستخدم الحقيقية تحفظ محلياً تحت `lab/imports/` ولا تدخل Git.
- بوابات الحقائق والحقوق والجودة والتصدير والنشر تبقى مغلقة إلى أن تُراجع منفصلة. إنشاء MP4 أو نجاح الاختبارات التقنية لا يعني اعتماد الحركة أو جودة المحتوى.

## التطوير على جهاز جديد

المسار مدعوم على macOS وLinux. Windows يحتاج WSL2 أو بيئة POSIX مشابهة؛ Windows الأصلي غير مختبر. لا يحتاج مسار Python حزم pip خارج المكتبة القياسية.

| الأداة | النسخة المرجعية/المتطلب | الاستخدام |
|---|---|---|
| Git | أي نسخة حديثة تدعم bundle وmerge | المصدر والإصدارات |
| Python | `3.12+` | الرندر، QA والاختبارات |
| Node.js | `24.21.0` من `.nvmrc` | Motion Canvas فقط |
| npm | `11.x` | تثبيت Motion Canvas عبر lockfile |
| FFmpeg وFFprobe | `7.1.1` مرجعي؛ يلزم H.264/libx264 | ترميز وفحص الفيديو |
| `rsvg-convert` | `librsvg 2.63.4` مرجعي | تحويل SVG إلى صور |

هذه النسخ سُجلت من جهاز التطوير الحالي (macOS/arm64)؛ ما عدا اختبارات المشروع على POSIX، لم تُختبر بعد على كل توزيعة Linux أو Windows/WSL. على Debian/Ubuntu أسماء الحزم المعتادة هي `python3`, `python3-venv`, `nodejs`, `npm`, `ffmpeg`, و`librsvg2-bin`. ثبّت أدوات النظام من مدير الحزم المعتمد عندك، وتأكد أن `ffmpeg -encoders` يعرض `libx264` وأن الأوامر `python3`, `node`, `npm`, `ffmpeg`, `ffprobe`, و`rsvg-convert` موجودة في `PATH`.

```sh
git clone https://github.com/ali96adil/ContentFactory.git
cd ContentFactory
git switch main
python3 --version
node --version
npm --version
ffmpeg -version
ffprobe -version
rsvg-convert --version
```

لا حاجة إلى `.env` لتشغيل الرندر والاختبارات المحلية؛ لا تحفظ مفاتيح أو بيانات دخول في الملفات. لا تثبّت n8n أو تربط حسابات أثناء إعداد بيئة الاختبار.

## تشغيل واختبار المسار المحلي

ابدأ باختبارات الاستئناف والمحوّل من جذر المستودع:

```sh
python3 lab/test_checkpoint.py
python3 tools/test_content_package_pipeline.py
python3 -m py_compile tools/render_content_package.py tools/review_content_package_render.py tools/test_content_package_pipeline.py tools/test_content_package_recovery.py
node --check lab/motion.mjs
```

لتثبيت Motion Canvas (اختياري للمحرر فقط)، استخدم Node المحدد في `.nvmrc` ثم lockfile:

```sh
cd lab/motion-canvas
npm ci
npm run build
npm run start -- --host 127.0.0.1 --port 9000
```

استخدم `Ctrl+C` للإيقاف. تشغيل Motion Canvas لا يرفع المحتوى ولا يتصل بحسابات المنصات.

## رندر حزمة TEST_ONLY

ملف المثال الاصطناعي في `lab/fixtures/content-package-demo-TEST_ONLY.json` لا يحتوي أصولاً خارجية أو قياسات أداء حقيقية. كل رندر يجب أن يذهب إلى اسم جديد داخل `lab/evidence/`؛ الأداة ترفض الكتابة فوق مخرج سابق.

```sh
python3 tools/render_content_package.py \
  --input lab/fixtures/content-package-demo-TEST_ONLY.json \
  --output lab/evidence/content-package-demo-TEST_ONLY-render-05 \
  --platform all --preview-seconds 5
python3 tools/review_content_package_render.py \
  --artifacts lab/evidence/content-package-demo-TEST_ONLY-render-05/artifacts \
  --output lab/evidence/content-package-demo-TEST_ONLY-review-05
python3 tools/test_content_package_recovery.py \
  --run-name content-package-recovery-v3-TEST_ONLY
```

الناتج معاينة Short صامتة وشرائح Carousel ومخطط Storyboard؛ لا ينتج حلقة YouTube نهائية. جميعها موسومة `TEST_ONLY`، ومجلد `lab/evidence/` مستثنى من Git.

## البيانات والأدلة

- `lab/templates/`: قوالب الإدخال الفارغة.
- `lab/fixtures/`: بيانات اصطناعية صغيرة قابلة للمشاركة لإعادة الاختبارات؛ لا تستخدمها كأداء سوقي.
- `lab/imports/`: صادرات أداء محلية مصرح بها، مستثناة من Git. أبقِ الحقول أو المقاييس غير المتاحة فارغة ولا تخمّنها.
- `lab/evidence/`: الفيديوهات والصور وتقارير الرندر وبيانات التشغيل المحلية؛ مستثناة من Git كي لا تُرفع معاينات أو قواعد بيانات أو مخرجات كبيرة.
- `HANDOFF.md`: سجل آخر حالة فعلية والخطوة التالية. انظر أيضاً `docs/LOCAL_WORKFLOW_NEXT_STEP.md`.

أوامر التحليل اليدوي لا تُشغّل إلا على CSV أُخذ من تصدير مصرح به. لا تدخل حسابات أو رموز API.

## الحركة والمراجعة

`Spotlight v3` مرفوض حسب مراجعة المستخدم. اتجاهات `fieldnotes` و`typeplay` و`gallery` تجارب محفوظة محلياً تحت `lab/evidence/`، وتفاصيلها في `docs/MOTION_CONTENT_SELECTION_TEST_ONLY.md`. آخر مراجعة لطبقات الحركة والانتقالات موثقة في `docs/MOTION_VISUAL_SYSTEM_REVIEW_V9_TEST_ONLY.md`، مع معاينات v9 المحلية في `lab/evidence/motion-content-selection-TEST_ONLY/`. قياسات الإطار لا تستبدل الاستماع أو المشاهدة البشرية المتصلة؛ جميع تقييمات الحركة والجودة بانتظار المستخدم.

للتفاصيل التشغيلية والقيود راجع [HANDOFF.md](HANDOFF.md) و[مرجع التنفيذ](ContentFactory_Implementation_Reference_AR.md). لا توجد موافقة جودة أو حقوق أو تصدير أو نشر مسجلة.
