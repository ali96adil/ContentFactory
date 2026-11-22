# أقرب خطوة محلية في خط المصنع

تاريخ الفحص: 2026-11-17 (`Asia/Baghdad`)

## مطابقة الخطة مع الموجود

| المرحلة بالخطة | الموجود فعلياً | النقص العملي |
|---|---|---|
| اكتشاف الأفكار/Scout | ماكو Scout مربوط أو بيانات منصة مستوردة. | يتطلب مصدر بيانات مصرح به أو إدخال أفكار يدوي؛ ماكو API/أسرار أو سجل فرص محلي بعد. |
| جمع المصادر والحقوق | `lab/extract_sources.py` ودفاتر الحقوق والتكلفة، مع تقرير استخراج سابق. | المراجعة البشرية لصدق الادعاءات والحقوق ما زالت إلزامية؛ ماكو سير آلي يمرر الموافقات. |
| كتابة AR/EN | نصوص وموضوعات التجربة موجودة في تقارير المختبر ومشهد موشن ثابت. | ماكو سجل واحد للـbrief وإصدارات نص AR/EN وموافقته؛ مشهد `lab/motion.mjs` حالياً يحتوي نصوصه داخله. |
| الإنتاج والتنسيقات | `lab/motion.mjs`, `lab/render_mac.py`, `lab/render.py`, librsvg وFFmpeg؛ Motion Canvas مشروع موجود. | القوالب لا تقرأ عقد محتوى قياسي/queue حتى الآن. الحالية معاينات `TEST_ONLY` فقط. |
| QA والمراجعة | `lab/test_checkpoint.py` لحالات الاستئناف، FFprobe للمواصفات، وسجل تقييم الوسائط. | قرار بصري/لغوي بشري مستقل، قبول صوت، وبوابة حقوق موقعة غير مربوطين بسجل المهمة. |
| توزيع محلي/نشر | مخرجات محلية فقط؛ تعطيل النشر متسق مع التوجيه. | ماكو حزمة export لكل منصة أو نشر، ويبقى النشر مغلقاً. |
| قراءة الأداء والقرار | أضفت `tools/analyze_platform_metrics.py` لاستيراد CSV محلي وتحليل المقارنة والاقتراح. | ماكو قياسات حقيقية/تصدير حساب أو موصل قراءة؛ الأداة ما تتصل بالشبكة ولا تستورد مباشرة من منصة. |
| منسّق جاهز | `n8n@2.47.7` مثبت محلياً في `lab/n8n-local` على Node `24.21.0`. Prefect غير موجود ببيئة Python. Docker CLI موجود. | الواجهة اجتازت `HTTP 200` في اختبار سابق على loopback، ثم أوقفت الخدمة. هذه الجولة وجدت 145 package findings؛ التفاصيل وشروط الوصول في [`N8N_AUDIT_REVIEW.md`](N8N_AUDIT_REVIEW.md). `2.48.4` beta فقط وماكو stable أحدث موثق كحل؛ لا تشغّل n8n حالياً. ما استوردنا Workflow أو ربطنا حسابات. Docker daemon غير شغال؛ ما نزلنا صورة. |

## الخطوة العملية المنفذة

أقرب جزء يمكن إنجازه بأمان من حلقة «فكرة ← محتوى ← معاينة ← قياس ← الحلقة التالية» هو ذيل الحلقة: بعد توفر CSV يدوي من حساب مصرّح به، يقارن المرشح بآخر 10 منشورات من نفس المنصة والحساب واللغة والصيغة وبعمر قياس ضمن ساعة من عمره. يتطلب القرار الاستدلالي خمسة قياسات مماثلة على الأقل؛ إذا نقصت، النتيجة `exploratory`. لا توجد بيانات فعلية بهذه الجولة، لذلك أنشأت fixture اصطناعية موسومة `TEST_ONLY` فقط.

الأداة تحسب محلياً نسب المشاهدات إلى مرات الظهور، والاحتفاظ (متوسط المشاهدة/مدة المحتوى)، ونسبة الحفظ والمشاركة. تقترح متغيراً واحداً للحلقة التالية: افتتاحية إذا ارتفع view-rate وانخفض retention، Carousel إذا ارتفعت saves/shares على Instagram/Facebook، أو تكرار/استكشاف عند ضعف الإشارة. ملفات `TEST_ONLY` للتأكد من عمل الأداة فقط: إذا ظهر `synthetic` أو `test_only` في `data_origin`، تمنع الأداة كل توصية تشغيلية (`test_only_no_action`) وتبقي `scale_eligible`, `export_allowed`, و`publish_allowed` على `false`. حتى مع بيانات فعلية، لا يصدر قرار توسع إلا بإشارات موجبة في موضوعين مختلفين، وموافقة بشرية للجودة، و`rights_status=verified`، وصرف خارجي صفر؛ التصدير والنشر دائماً `false` من هذه الأداة.

الـCSV المحلي يجب أن يحتوي على أعمدة [`platform-metrics-template.csv`](../lab/templates/platform-metrics-template.csv). استخدم `data_origin=manual_export` للبيانات المنقولة من تصدير محلي؛ عيّن `rights_status=verified` فقط بعد مراجعة الحقوق، و`quality_status=human_approved` فقط بعد الموافقة البشرية المطلوبة. لا تضع كلمات مرور أو Tokens أو روابط OAuth. طبّق anonymization على معرف الحساب إذا مو مطلوب التحليل بهويته.

```sh
cd "$(git rev-parse --show-toplevel)"
python3 tools/analyze_platform_metrics.py lab/fixtures/platform-metrics-TEST_ONLY.csv --output lab/evidence/performance-decisions-TEST_ONLY-run-03.json
```

## الاختبارات الفعلية في هذه الدفعة

- بداية العمل كانت الفرع `main` والـHEAD `e9b89ab` بحالة نظيفة.
- `python3 lab/test_checkpoint.py` — PASS للحالات الست: timeout/retry، إلغاء التكرار المتزامن، رفض الحقوق غير المؤكدة، منع الوجهة العامة، حد المحاولات، واستعادة SQLite.
- `(cd lab/motion-canvas && npm run build)` — PASS: TypeScript وVite، 847 module، انتهى Vite خلال 0.923 ثانية.
- تشغيل التحليل السابق قبل إضافة حاجز `TEST_ONLY` أنتج توصيات تجريبية لكل candidate رغم تعطيل التوسع والنشر؛ عولج هذا السلوك في استئناف 2026-11-17 أدناه.
- تحقق schema الـtemplate ورفض الكتابة فوق ملف JSON موجود سبق نجاحهما كما هو موثق في الاستئناف السابق.
- تحقق schema الـtemplate ورفض الكتابة فوق ملف JSON موجود — PASS؛ بقيت بصمة الملف الموجود مطابقة بعد الرفض.
- مراجعة FFprobe للمخرجات السابقة: Motion Canvas AR `1080×1920`, 24 fps, 71 frames, 2.958333s؛ EN 76 frames, 3.166667s. librsvg AR/EN `1080×1920`, 24 fps, 96 frames, 4s. كل المخرجات الموجودة بلا صوت بحسب مسار الرندر.
- أثناء التحقق الأول أخطأت كتابة التوقع بعدد الصفوف (26 بيانات + header) وأعطيت FFprobe أكثر من ملف بصيغة أمر غير صحيحة. صححت assertions وشغّلت FFprobe لكل ملف منفرداً؛ التحقق النهائي أعلاه ناجح.
- لا قياس حقيقي للأداء، ولا إخراج/قرار إنتاج أو صوت. ماكو أي خدمة أو API أو منصة اتصلنا بها.

## فحص هدف الصوت الجديد

الهدف صار «صوت عربي أبيض قريب من الفصحى المبسطة، مفهوم لأوسع جمهور وبإيقاع بشري طبيعي». فُحصت البطاقات الرسمية فقط؛ ماكو تنزيل أو توليد. `SILMA TTS v1` أقرب مرشح معلن للفصحى وله Apache-2.0 على الأوزان، لكن ناشره لا يكشف مصادر بيانات التدريب العامة/الملكية أو حقوق التسجيلات. بطاقة Nabra تعلن Apache وMSA وصوت واحد، لكنها لا تسمي مصدر بيانات التدريب. `Fasih-TTS-V1` يعلن ترخيصاً غير تجاري. ولا تزال Habibi ممنوعة من التنزيل/الاختبار، بما يشمل IRQ حسب التوجيه. التفاصيل في [`WHITE_ARABIC_VOICE_CANDIDATES.md`](WHITE_ARABIC_VOICE_CANDIDATES.md). فجوة الصوت الطبيعي التجاري مفتوحة. لا جندر مفضل مسجلاً.

## الخطوة التالية المحددة

استورد المستخدم أو مشغّل مخوّل ملف أداء محلياً بعد 24 ساعة على الأقل من منشور تجريبي مُصرح به، مع ستة baseline comparables على الأقل لكل منصة/لغة/صيغة. ابدأ من نسخة الملف، دون ضبط credentials أو API:

```sh
cd "$(git rev-parse --show-toplevel)"
python3 tools/analyze_platform_metrics.py lab/imports/platform-metrics-24h.csv --output lab/evidence/performance-decision-run-01.json
```

إذا ما توفر تصدير أو صلاحية قراءة، لا تستخدم synthetic fixture كدليل سوق؛ يبقى الجزء التالي يدوياً ومعلقاً. ربط n8n يبقى مؤجلاً إلى أن تُراجع advisories وتُختبر عقد محلية آمنة؛ التشغيل الحالي يقتصر على localhost، ولا نحتاج Docker بهذه النسخة لكن سجل التشغيل يحذر من إلغاء npm-host mode مستقبلاً. لا تجرّب Docker عبر تنزيل image.


## استئناف 2026-11-17: حصر بيانات TEST_ONLY بالتجارب

- بقي n8n متوقفاً، ولم أستخدم انتظار بيانات أداء أو صوت. راجعت `main` عند `95cd1aa` وكانت شجرة Git نظيفة. استخدمت محلل المقاييس الموجود؛ لم أبنِ أداة جديدة.
- وجدت أن المحلل كان يمنع `scale_eligible` والتصدير والنشر للـfixture الاصطناعية، لكنه ما زال يعطي candidate توصيات مثل `hook_experiment`. شدّدت الحاجز في `tools/analyze_platform_metrics.py`: أي `data_origin` يتضمن `synthetic` أو `test_only` ينتج `recommendation=test_only_no_action` وتعليمة صريحة بعدم استخدام النتائج للنشر أو التوسع أو قرارات الإنتاج. بقيت مقاييس المنصة وحقوق/QA ظاهرة للمراجعة، لكن لا توجد توصية تحريرية عملية.
- تحقق التشغيل على `lab/fixtures/platform-metrics-TEST_ONLY.csv` مرّ: 26 صفاً، 4 candidates، وضع `TEST_ONLY_SYNTHETIC`، كل التوصيات `test_only_no_action`، و`scale_eligible=false`, `export_allowed=false`, `publish_allowed=false`. الأمر لا يكتب ملف نتيجة: `python3 tools/analyze_platform_metrics.py lab/fixtures/platform-metrics-TEST_ONLY.csv`.
- الملفات المتغيرة في هذه الدفعة: `tools/analyze_platform_metrics.py`, `docs/LOCAL_WORKFLOW_NEXT_STEP.md`, و`HANDOFF.md`. لم يتغير n8n أو بيانات التجربة، ولا اتصال شبكة/حسابات أو نشر.
- الخطوة التالية: عند توفر تصدير أداء محلي مصرح به فقط، جهّز نسخة من `lab/templates/platform-metrics-template.csv` تحت `lab/imports/platform-metrics-24h.csv` وعلّم المصدر `manual_export` بعد إزالة/تعمية معرفات الحساب غير اللازمة، ثم شغّل: `python3 tools/analyze_platform_metrics.py lab/imports/platform-metrics-24h.csv --output lab/evidence/performance-decision-run-01.json`. إذا بقي التصدير غير متوفر، لا تستخدم fixture لاتخاذ قرار.
