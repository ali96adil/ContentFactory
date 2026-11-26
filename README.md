# ContentFactory

# مصنع المحتوى الذكي

مختبر محلي لحزم محتوى معرفي أصلية بالعربية البيضاء والإنكليزية. الميزانية الخارجية صفر، والنشر الخارجي معطّل، وStageCore وKids Studio خارج النطاق. فيديوهات وتجارب `TEST_ONLY` لا تعني اعتماد الجودة أو الحقوق أو التصدير.

## الحالة والقيود

- عقد المحتوى: `docs/CONTENT_PACKAGE_CONTRACT.md`؛ القالب: `lab/templates/content-package-template.json`.
- الصوت العربي الطبيعي المرخص تجارياً فجوة مفتوحة؛ لا يوجد صوت عربي معتمد للإنتاج.
- n8n `2.47.7` مثبت محلياً والخدمة متوقفة بسبب مراجعة الثغرات. لا تشغّله قبل مراجعة `docs/N8N_AUDIT_REVIEW.md`.
- لا توجد موصلات أداء منصة فعلية. `lab/fixtures/` للاختبارات الاصطناعية فقط؛ صادرات الأداء الحقيقية تبقى محلية في `lab/imports/`.
- بوابات الحقائق والحقوق والجودة والتصدير والنشر مغلقة. فحوص الترميز لا تمنح موافقة بشرية.

## التطوير من جهاز جديد

المسار مدعوم على macOS وLinux. على Windows استخدم WSL2 أو بيئة POSIX مشابهة؛ Windows الأصلي غير مختبر. أدوات Python تستخدم المكتبة القياسية فقط، ولا تحتاج حزم `pip`.

| الأداة | النسخة المرجعية أو المتطلب | الاستخدام |
|---|---|---|
| Git | حديثة، تدعم bundle وmerge | المصدر والإصدارات |
| Python | `3.12+` | الرندر، QA والاختبارات |
| Node.js | `24.21.0` حسب `.nvmrc` | Motion Canvas الاختياري |
| npm | `11.x` | اعتماديات Motion Canvas المثبتة بالـlockfile |
| FFmpeg وFFprobe | `7.1.1` مرجعي؛ مطلوب encoder `libx264` | ترميز الفيديو والتحقق |
| `rsvg-convert` | `librsvg 2.63.4` مرجعي | تحويل SVG |

هذه نسخ مسجلة من جهاز التطوير الحالي macOS/arm64. وثائق POSIX مناسبة لـLinux/WSL، لكن ما صار اختبار على كل توزيعة. على Debian/Ubuntu أسماء الحزم المعتادة: `python3`, `python3-venv`, `nodejs`, `npm`, `ffmpeg`, `librsvg2-bin`. ثبّت الأدوات من مدير الحزم المعتمد عندك، وتأكد أن `ffmpeg -encoders` يعرض `libx264` وأن الأوامر التالية متاحة في `PATH`:

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

لا يحتاج الرندر المحلي ملف `.env` أو حساب منصة. لا تحفظ مفاتيح أو كلمات مرور في الملفات. لا تثبّت أو تشغّل n8n لإجراء الاختبارات الحالية.

## فحص المستودع الكامل

شغّل من جذر المستودع:

```sh
python3 tools/verify_repo.py
```

يفحص الأمر توفر FFmpeg/FFprobe وlibrsvg وNode/npm، ثم يشغّل اختبارات checkpoint ومحلل الأداء والحزمة واحتواء مسارات manifest واستيراد سجل القياسات ونسخه/استعادته، وفحوص Python/Node، وتثبيت Motion Canvas وبناءه. ينشئ مجلد أدلة `TEST_ONLY` باسم جديد لكل استعادة حتى لا يستبدل نتيجة قديمة. GitHub Actions يستعمل أمر التحقق نفسه داخل حاوية Ubuntu مؤقتة؛ بذلك تكون خطوة CI المحلية وCI موحّدة.

Motion Canvas اختياري. لاستخدام المحرر، من جذر المستودع اختر Node عبر `nvm use` ثم:

```sh
cd lab/motion-canvas
npm ci --legacy-peer-deps
npm run build
npm run start -- --host 127.0.0.1 --port 9000
```

يحتاج التثبيت حالياً إلى `--legacy-peer-deps` لأن إضافة Motion Canvas `3.17.2` تعلن توافق Vite حتى الإصدار 5، بينما المشروع يختبر Vite 7. نجاح البناء يتحقق فعلياً في CI؛ لا يعني هذا أن نطاق peer المعلن صار متوافقاً. أوقف المحرر بـ`Ctrl+C`. تثبيت npm يخص Motion Canvas فقط؛ الرندر القياسي لا يحتاج حزم npm. فحوص GitHub Actions تعمل على runner قياسي عام، وتثبت أدوات الوسائط داخل بيئة CI المعزولة.

## رندر حزمة TEST_ONLY

`lab/fixtures/content-package-demo-TEST_ONLY.json` نص اصطناعي صغير بلا أصول خارجية أو قياسات أداء. استخدم اسم مجلد جديد لكل تشغيل؛ المحوّل يرفض استبدال المخرجات السابقة.

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

ينتج المسار Short صامتاً وشرائح Carousel ومخطط Storyboard؛ لا ينتج حلقة YouTube نهائية. للاستئناف بعد انقطاع، راجع مجلد `.work` ثم أعد أمر الرندر نفسه مع `--resume` دون تغيير الإدخال. المخرجات موسومة `TEST_ONLY`.

## البيانات والأدلة

- `lab/templates/`: قوالب الإدخال.
- `lab/fixtures/`: أمثلة اختبار اصطناعية صغيرة، لا تستخدمها كقياس سوقي.
- `lab/imports/`: ملفات أداء محلية مصرح بها، مستثناة من Git؛ اترك المقاييس غير المتوفرة فارغة ولا تخمّنها.
- `lab/evidence/`: الفيديوهات والصور والتقارير وبيانات التشغيل المحلية؛ مستثناة من Git لأنها قد تكون كبيرة أو شخصية.
- `HANDOFF.md`: سجل البيئة والنتائج والخطوة التالية. راجع أيضاً `docs/LOCAL_WORKFLOW_NEXT_STEP.md`.

لاستيراد CSV أداء مصرح به إلى سجل محلي idempotent، استخدم ملف SQLite جديداً داخل `lab/imports/`، ثم حلل كل اللقطات المتراكمة من السجل:

```sh
python3 tools/import_platform_metrics.py lab/imports/platform-metrics-24h.csv \
  --database lab/imports/platform-metrics-ledger.sqlite3
python3 tools/analyze_platform_metrics.py --ledger lab/imports/platform-metrics-ledger.sqlite3
python3 tools/backup_platform_metrics_ledger.py backup \
  lab/imports/platform-metrics-ledger.sqlite3 \
  --destination lab/evidence/platform-metrics-ledger-backup-01.sqlite3
python3 tools/backup_platform_metrics_ledger.py restore \
  lab/evidence/platform-metrics-ledger-backup-01.sqlite3 \
  --destination lab/imports/platform-metrics-ledger-restored.sqlite3
```

إعادة الملف نفسه لا تضيف صفوفاً ثانية؛ نفس المنشور/وقت القياس بقيم مختلفة يرفض الدفعة كلها. تهيئة المخطط وإضافة الصفوف تجريان ضمن معاملة كتابة واحدة، حتى تتسلسل الاستيرادات المتزامنة عند إنشاء السجل لأول مرة. `--ledger` يحلل كل اللقطات المستوردة ويتحقق من بصماتها. أداة النسخ تستعمل SQLite online backup، تتحقق من صفوفه قبل تثبيته، ولا تستبدل وجهة موجودة. الأدوات لا تستدعي منصة ولا تصدر أو تنشر. لا تستخدم fixture التجريبية كبيانات سوق.

## سجل المهام المحلي

يوفر `tools/job_ledger.py` نموذجاً محلياً ذرياً لحالات العمل وleases حتى `review_required`. يستخدم SQLite تحت `lab/imports/` أو `lab/evidence/` فقط، ويرفض أي وجهة غير `local`. ملفات القاعدة وjournal خاصة بالمالك (`0600`). عند الاكتمال يتحقق من وجود أثر غير فارغ تحت `lab/evidence/` ويطابق الحجم وSHA-256 ويرفض symlinks. لا يفتح API، ولا يمنح موافقة بشرية، ولا يصدر أو ينشر. اختباره ضمن `python3 tools/verify_repo.py`؛ تفاصيل الحدود في [`LOCAL_WORKFLOW_NEXT_STEP.md`](docs/LOCAL_WORKFLOW_NEXT_STEP.md).

## الحركة والمراجعة

`Spotlight v3` مرفوض. اتجاهات `fieldnotes` و`typeplay` و`gallery` محفوظة كاختبارات محلية؛ تفاصيل اختيار الحركة في `docs/MOTION_CONTENT_SELECTION_TEST_ONLY.md`. تقرير حدود المشهد والانتقالات في `docs/MOTION_VISUAL_SYSTEM_REVIEW_V9_TEST_ONLY.md`. المعاينات في `lab/evidence/motion-content-selection-TEST_ONLY/` محلية ومستثناة من Git؛ تقييم السلاسة والذوق وقراءة الهاتف ما زال بانتظار مراجعة المستخدم.

للتفاصيل راجع [HANDOFF.md](HANDOFF.md)، و[مرجع التنفيذ](ContentFactory_Implementation_Reference_AR.md)، و[عقد الحزمة](docs/CONTENT_PACKAGE_CONTRACT.md). لا توجد موافقة جودة أو حقوق أو تصدير أو نشر مسجلة.
