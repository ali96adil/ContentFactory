# تسليم واستئناف مصنع المحتوى

آخر تحديث: 2026-11-17 (`Asia/Baghdad`)

## الحالة المحفوظة

- المجلد: `/Users/aliadil/Projects/ContentFactory`، الفرع `main`؛ نقطة البداية كانت commit `fd44f67`، والدفعات السابقة محفوظة حتى commit `654475b`.
- لا تغييرات خارج مجلد المشروع. لا لمس لـStageCore أو Kids Studio، ولا نشر أو رفع محتوى. ماكو أسرار مضافة.
- البيئة: macOS 27.0 / Apple Silicon M3 Max / ذاكرة 48 GB، مساحة حرة تقارب 199 GiB وقت الفحص. الأدوات الأساسية: Git 2.55.0، Node 24.21.0، Python 3.15.2، FFmpeg/FFprobe 7.1.1، librsvg/rsvg-convert 2.63.4. Python 3.12.9 موجود واستخدمته محلياً لصوت Piper. الحالة الحالية لـ`n8n@2.47.7` هي تثبيت محلي تحت `lab/n8n-local` لكن الخدمة متوقفة بسبب نتائج `npm audit`؛ التفاصيل والأوامر بأسفل الملف. `espeak-ng` غير مثبت.
- المراجع والحزمة الأصلية تبقى تحت `lab/`. معاينتا librsvg السابقتان صالحتان تقنياً: `1080×1920`، `24fps`، `4s`، بلا صوت.

## اللي تهيّأ واختُبر بهالدفعة

- بيئة Piper `1.8.0` والنموذج الإنكليزي `en_US-ljspeech-medium` داخل `lab/voice-env` و`lab/models/`. ملفات تثبيت ومخازن التنزيل محلية للمشروع. نُزّل نموذج إنكليزي واحد فقط بعد فحص الحجم والترخيص؛ ما نُزّل نموذج عربي.
- ملفات الصوت الموسومة `TEST_ONLY`: `lab/evidence/en-piper-ljspeech-TEST_ONLY.wav`، `ar-macos-majed-TEST_ONLY.wav`، `en-macos-samantha-TEST_ONLY.wav`، `en-macos-daniel-TEST_ONLY.wav`. المستخدم قيّم طبيعية صوت `Majed` بـ`1/5` (روبوتي جداً)، وسُجلت النتيجة في `docs/evaluation-results.csv`؛ تقييم صوت الإنكليزي بعده معلق.
- `lab/motion-canvas/` يحتوي المشهد القابل للتعديل ومشروع Motion Canvas `3.17.2`. التصدير من المحرر نجح إلى صور PNG محلية، وبعدها حُوّل بـFFmpeg. لقطتا العربية والإنكليزية اتراجعن بصرياً؛ تشكيل العربية صحيح وكل تسمية في مشهد EN إنكليزية.
- ملفات الفيديو الموسومة `TEST_ONLY`: `lab/evidence/motion-canvas-ar-TEST_ONLY.mp4` و`motion-canvas-en-TEST_ONLY.mp4` و`motion-canvas-bilingual-TEST_ONLY.mp4`. راجعها بـFFprobe في التقرير. لا صوت في موشن Canvas.
- `tools/record_media_evaluation.py` يسجل البصمة والحجم ومدة/مواصفات الوسيط ومصدره وترخيصه، ويترك درجات الجودة فارغة للمراجع البشري. التقرير الكامل والأوامر والمراجع الرسمية في `docs/LOCAL_AUDIO_MOTION_EVALUATION.md`.
- نتيجة الاختبار: `cd lab/motion-canvas && npm audit` = صفر ثغرات؛ `npm run build` نجح (TypeScript وVite). تنبيه: توافق Vite 7 مع إضافة Motion Canvas مثبت محلياً بتعديل إعداد تجريبي، فيحتاج مراجعة قبل اعتماد build إنتاجي.
- حالة الجودة: `Majed` مرفوض للطبيعية حسب ملاحظة المستخدم، وعينة macOS غير مناسبة كأصل إنتاج للنشر التجاري. Nabra-82M-INT8 حجمه `83.2 MB` وبطاقة النموذج تعلن Apache-2.0، لكن صفحة النموذج لا تذكر مجموعة التدريب أو رخصتها/مصدر التسجيل. حسب توجيه المستخدم، لم ننزّله أو نشغّله إلى أن يتضح هذا المصدر. فحص بيئة `lab/voice-env`: `piper-tts 1.8.0` و`onnxruntime 1.32.0` و`numpy 2.5.5` متوفرة؛ `torch` و`misaki` و`espeakng-loader` و`espeak-ng` غير مثبتة. تثبيت الاعتماديات السابق توقف بلا تقدم، وماكو حزم جديدة. المساحة الحرة وقت هذه الجولة `197 GiB`. فجوة الصوت العربي الطبيعي بعدها **مفتوحة**.

## الملفات المتغيرة أو المضافة بهالدفعة

- تحديث `.gitignore` لتجاهل البيئات والمخابئ والمخرجات المحلية.
- إضافة `lab/motion-canvas/` (المشروع، lockfile، مشهد AR/EN وإعداد Vite).
- إضافة `tools/record_media_evaluation.py`.
- إضافة `docs/evaluation-texts.md` و`docs/evaluation-results.csv` و`docs/LOCAL_AUDIO_MOTION_EVALUATION.md`.
- مخرجات WAV/MP4/PNG والنماذج وبيئات التثبيت تحت `lab/`؛ المستبعد منها من Git وفق `.gitignore`.

## أول خطوة معلّقة

الهدف الصوتي الحالي هو صوت عربي أبيض قريب من الفصحى المبسطة، مفهوم لأوسع جمهور وبإيقاع طبيعي بشري. لا صوت عربي صالح تجارياً وموثق المصدر حالياً؛ لا تختبر/تنزّل مرشحاً حتى تتضح حقوق بيانات التدريب والتسجيلات. Habibi IRQ/Lahgtna لا يُنزّلان حسب حالة المستخدم. تفاصيل المرشحين المفتوحين في [`docs/WHITE_ARABIC_VOICE_CANDIDATES.md`](docs/WHITE_ARABIC_VOICE_CANDIDATES.md).

أقرب خطوة سير محلية بعد الموشن هي تحليل ملف أداء تجريبي يدوي، لأن ماكو قياسات حسابات حقيقية. الأداة أصبحت موجودة في `tools/analyze_platform_metrics.py`، وعينة TEST_ONLY ونتيجة التشغيل في `lab/fixtures/` و`lab/evidence/`. النتيجة الاصطناعية ممنوع استخدامها كدليل سوق أو قرار توسع. فحص خط الإنتاج والمخرجات في [`docs/LOCAL_WORKFLOW_NEXT_STEP.md`](docs/LOCAL_WORKFLOW_NEXT_STEP.md).

سبق أن جُرّب الأمر التالي داخل بيئة المشروع، لكنه لم يتقدم لأكثر من دقيقتين وأُوقف قبل تثبيت أي حزمة؛ لا تعاوده قبل إزالة عائق الترخيص وفحص سلوك التنزيل:

```sh
cd /Users/aliadil/Projects/ContentFactory
uv pip install --python lab/voice-env/bin/python torch==2.15.0 misaki==0.9.4 espeakng-loader==0.2.4
```

إذا انحل عائق الترخيص، ولّد عينة عربية قصيرة `TEST_ONLY` بنفس نص `Majed`، وسجّل زمن التوليد والحجم. Nabra فصحى `MSA` وصوته الوحيد موصوف في البطاقة بأنه أنثوي؛ سجّل الجندر كبيانات فقط، ولا تعتمد الصوت قبل مقارنة الاستماع والطبيعية والوضوح واللهجة.

## استئناف 2026-11-17: مراجعة Habibi-TTS ومرشح بديل

- بدأ الفحص على `main` وبحالة نظيفة عند `9b22104`; المستودع هو `/Users/aliadil/Projects/ContentFactory`. بقيت الملفات السابقة دون تعديل قبل هذه الدفعة.
- قُرئت الورقة وبطاقات/مصادر Habibi الرسمية وفُحصت بيانات D1 المؤدية إلى `Specialized/IRQ`. تقرير المراجعة التفصيلي والجدول وروابط الترخيص: [`docs/HABIBI_IRQ_LICENSE_REVIEW.md`](docs/HABIBI_IRQ_LICENSE_REVIEW.md).
- قرار البوابة: لا تنزيل ولا تشغيل لـHabibi IRQ. الورقة تثبت استخدام `MGB-2` غير التجاري في مرحلة MSA، وتهيئة F5-TTS على Emilia ذات ترخيص `CC-BY-NC-4.0`، وتذكر `58.9h` من بيانات عراقية in-house بلا مصادر أو تراخيص/موافقات معلنة. يوجد أيضاً تعارض بين metadata العامة في Hub (`CC-BY-NC-SA-4.0`) وREADME الذي يعلن Apache-2.0 للنموذج المتخصص. Apache-2.0 للوزن وحده لا يحل ذلك.
- فُحص Lahgtna Chatterbox v1 كمرشح بديل ولم يُنزّل: يعلن MIT لكن لا يوثق بيانات التدريب أو مصدر التسجيل، وبطاقة النموذج لا تثبت استكمال العراقية (العراق ضمن roadmap غير المكتمل بينما README يذكر `iq`). بقي محجوباً للسبب نفسه.
- مواصفات الجهاز/المساحة: `arm64`, `Mac15,9`, RAM `48 GiB`, free space `197 GiB`. الحجم البعيد المعلن لـHabibi IRQ `1.35 GB` و`vocab.txt` `11.8 kB`؛ لم تُنشأ بصمات محلية لأن الملفات لم تُنزّل.
- فُحصت `lab/voice-env` كما هي: Python `3.12.9`, torch `2.15.0`, misaki `0.9.4`, espeakng-loader `0.2.4`; لا يوجد `torchaudio`, `f5_tts`, `habibi_tts`, أو `safetensors`. لم تُثبّت/تُرقّ أي حزمة في هذه الدفعة. هذا يختلف عن حالة التسليم السابقة حيث كان torch غير مثبت.
- ما لم يُختبر: توليد صوت Habibi أو Lahgtna، جودة/طبيعية الصوت، زمن التوليد، مدة/حجم العينة، وبصمة أوزان Habibi. لا توجد عينة عراقية جديدة؛ عينة Majed السابقة تبقى المرجع النصي، لا دليلاً على Habibi.
- فحص Habibi IRQ لهذه المرحلة منتهٍ ومؤرشف؛ لا تراسل الجهات ولا تنزّل Habibi IRQ أو Lahgtna. المتطلبات المكتوبة أعلاه تحفظ سبب الإيقاف فقط، وماكو متابعة نشطة لهذا الفحص.
- أي إعادة تقييم صوتية لاحقاً تبدأ بالهدف الحالي في [`docs/WHITE_ARABIC_VOICE_CANDIDATES.md`](docs/WHITE_ARABIC_VOICE_CANDIDATES.md)، وتتحقق من الترخيص التجاري ومصادر الصوت/التدريب قبل أي تثبيت أو تنزيل أو توليد.
- أوامر تحقق الحالة:

```sh
cd /Users/aliadil/Projects/ContentFactory
git status --short --branch
git log -5 --oneline
uv pip list --python lab/voice-env/bin/python
df -h .
```

## استئناف 2026-11-17: التحليل المحلي والحلقة التالية

- هدف الصوت تم تحديثه بتوجيه المستخدم إلى عربي أبيض قريب من الفصحى المبسطة وطبيعي للجمهور العربي الواسع. Habibi IRQ فحص منتهٍ حالياً؛ لا تراسل الجهات ولا تنزّله، ولا تنزّل Lahgtna. لم أجرِ أي تنزيل أو اختبار صوت. مراجعة SILMA/Nabra/Fasih/Habibi ومصادرهم المعلنة في [`docs/WHITE_ARABIC_VOICE_CANDIDATES.md`](docs/WHITE_ARABIC_VOICE_CANDIDATES.md). الخلاصة: لا مرشح اجتاز معاً وضوح المصدر والترخيص التجاري، فجوة الصوت مفتوحة.
- فحص الخطّة مقابل الموجود ووسائل الربط في [`docs/LOCAL_WORKFLOW_NEXT_STEP.md`](docs/LOCAL_WORKFLOW_NEXT_STEP.md). الأدوات: `n8n` غير مثبت، `prefect` غير مثبت، `docker` CLI موجود لكن Docker daemon متوقف (socket مفقود). ماكو بيانات أداء حقيقية مصدرة ولا موصلات منصة جاهزة. لم أحاول تنزيل صورة Docker.
- أضيفت أداة stdlib محلية `tools/analyze_platform_metrics.py`، fixture اصطناعي `lab/fixtures/platform-metrics-TEST_ONLY.csv`، وtemplate فارغ `lab/templates/platform-metrics-template.csv`. النتيجة الاختبارية ignored محلياً تحت `lab/evidence/`.
- أمر التحليل: `python3 tools/analyze_platform_metrics.py lab/fixtures/platform-metrics-TEST_ONLY.csv --output lab/evidence/performance-decisions-TEST_ONLY-run-03.json`. النتيجة: 26 صفاً اصطناعياً، 4 منصات: YouTube اقتراح hook واحد، Instagram تجربة Carousel، TikTok تكرار متغير واحد، وFacebook استكشافي لأن baseline أقل من خمسة. الحقوق غير متحققة وQA تقني فقط، لذلك `scale_eligible=false`, `export_allowed=false`, `publish_allowed=false`. هذه بيانات fixture وليست أداء حقيقياً.
- فحص template schema ومنع overwrite: PASS؛ إذا كان ملف JSON موجوداً يرفضه البرنامج ولم تتغير بصمته.
- اختبار `python3 lab/test_checkpoint.py`: PASS بست حالات الاستئناف السابقة. اختبار `(cd lab/motion-canvas && npm run build)`: PASS لـTypeScript/Vite (847 modules، Vite render 0.923s). FFprobe لكل فيديو على حدة اجتاز: Motion Canvas AR/EN 1080×1920,24fps,71/76 frames,2.958333/3.166667s؛ librsvg AR/EN 1080×1920,24fps,96 frames,4s. ماكو صوت في هذه المخرجات.
- أمر التحقق الأول للتوقع كتب صفاً زائداً (الملف فيه 26 صف بيانات + header)، وأمر FFprobe الأول مرّر عدة ملفات بطريقة غير مدعومة؛ صححت العدّ وشغلت كل فيديو منفرداً ونجح التحقق النهائي. ماكو تغييرات خارج المشروع أو أسرار أو اتصال خارجي.
- أول خطوة معلّقة: الحصول محلياً على ملف CSV لقياسات 24 ساعة من منشورات مُصرح بها، مع baseline مماثل كافٍ، أو ترك الأداء معلقاً إذا ماكو وصول. بعد إنشاء `lab/imports/platform-metrics-24h.csv`, شغّل:

```sh
cd /Users/aliadil/Projects/ContentFactory
python3 tools/analyze_platform_metrics.py lab/imports/platform-metrics-24h.csv --output lab/evidence/performance-decision-run-01.json
```

- بعد ذلك راجع جودة المقترح بشرياً، ولا توسّع إلا بإشارة على موضوعين مع QA مقبول وصرف خارجي صفر. الصوت التجاري الطبيعي يبقى مستقلاً ومعلّقاً عند توثيق مصادر التدريب والرخصة.

## أوامر متابعة الموشن

تشغيل المحرر على localhost فقط:

```sh
cd /Users/aliadil/Projects/ContentFactory/lab/motion-canvas
npm run start -- --host 127.0.0.1 --port 9000 --strictPort
```

من الواجهة اضبط `1080×1920` و`24fps`، واضغط `RENDER`. تقرير الاختبارات والأوامر الكاملة: `docs/LOCAL_AUDIO_MOTION_EVALUATION.md`.

## استئناف 2026-11-17: تهيئة n8n محلياً

- بداية هذه الخطوة كانت على `main` عند `517f805` وبحالة نظيفة. Node `v24.21.0` وnpm `11.19.0` على `darwin arm64`، و197 GiB متاحة. n8n مثبت بنسخة ثابتة `2.47.7` داخل `lab/n8n-local` (`package.json` و`package-lock.json`)؛ لا تثبيت عالمي ولا Docker ولا `sudo`. هذه النسخة آخر stable التي أظهرها `npm view n8n@latest` أثناء الفحص؛ سجل الإصدار الرسمي يذكر نشرها 2026-11-13.
- التثبيت شمل 2,259 حزمة أول مرة، استغرق 34 دقيقة، ثم تحديث patch إلى 2.47.7 استغرق 5 دقائق. الحجم المحلي وقت الفحص: `node_modules` نحو 2.5 GiB، npm cache نحو 1.3 GiB، وبيانات SQLite المحلية نحو 54 MiB. مخبأ npm والإعدادات والبيانات تحت المشروع ومضافة إلى `.gitignore`؛ لا تضع محتواها في Git.
- ملاحظة صريحة: أول محاولة npm استخدمت cache الافتراضي خارج المشروع قبل أن ألاحظ ذلك؛ أوقفتها، ونقلت التثبيت الناجح ومخه إلى `lab/n8n-local/.npm-cache`. قد تكون محاولة التوقف أضافت عناصر cache إلى `~/.npm`؛ لم أمسح مخزن المستخدم العام كي لا أحذف cache سابقاً أو مشتركاً. لم تتغير إعدادات نظام أو حزم نظام.
- نسخة npm تذكر `SEE LICENSE IN LICENSE.md`. ترخيص المصدر المرفق هو Sustainable Use License 1.0؛ يسمح باستخدام البرامج لأغراض العمل الداخلية، لكنه ليس Apache/MIT ولا يمنح حق تشغيل n8n كخدمة مستضافة للغير أو إعادة بيعه. راجع [الترخيص عند tag 2.47.7](https://github.com/n8n-io/n8n/blob/n8n%402.47.7/LICENSE.md) و[تعليمات npm الرسمية](https://docs.n8n.io/hosting/installation/npm/)؛ الوثائق الحالية تحدد Node `20.19` إلى `24.x`، وتحذر من إهمال طريقة npm بدءاً من n8n 3.0. المصدر الرسمي يسجل إصدار `2.47.7` بتاريخ 2026-11-13: [release](https://github.com/n8n-io/n8n/releases/tag/n8n%402.47.7).
- الأمر `node lab/n8n-local/node_modules/n8n/bin/n8n --version` رجع `2.47.7`، و`npm --prefix lab/n8n-local ls n8n --depth=0` أكد الإصدار. شغّلت الخدمة مع `N8N_LISTEN_ADDRESS=127.0.0.1` و`N8N_HOST=127.0.0.1` و`N8N_PORT=5678` و`N8N_USER_FOLDER=$PWD/lab/n8n-local/data`، وعطّلت diagnostics/personalization/version notifications/templates. فحص `curl http://127.0.0.1:5678/` رجع `HTTP 200`، و`lsof` أكد أن 5678 و5679 يستمعان على `127.0.0.1` فقط. الإصدار 2.47.7 أقلع وبنى SQLite، وعرض الواجهة؛ الفهرس أكد 0 workflows. بعدها أوقفت الخدمة بـ`Ctrl+C`، فالمنافذ حالياً غير مستمعة.
- لا حساب مالك أُنشئ، ولا Workflow مستورد، ولا اتصال حسابات، ولا أسرار أُضيفت. `data/.n8n/config` يحوي مفتاح التشفير الذي أنشأه n8n تلقائياً؛ بقي محلياً ومستثنى من Git.
- تدقيق `npm --prefix lab/n8n-local audit --cache "$PWD/lab/n8n-local/.npm-cache" --omit=dev --json` سجّل 145 إدخال حزمة متأثرة (2 منخفضة، 67 متوسطة، 69 عالية، 7 حرجة)، موزعة على 125 advisory فريدة. ما شغّلت `npm audit fix` أو `--force`؛ اقترح npm تثبيت n8n `1.17.0` كتغيير مكسور/رجوع إصدار، وهذا غير مقبول. لا تترك الخدمة قيد التشغيل قبل مراجعة التنبيهات وتوفر تحديث مناسب. ظهرت أيضاً تعارضات peer/deprecation، وتحذير من 15 install scripts غير مغطاة بسياسة `allowScripts`؛ الإقلاع والواجهة نجحا رغم ذلك. لا توافق scripts جماعياً قبل مراجعة كل واحدة.
- حدود النسخة: JavaScript Task Runner تسجل واشتغل؛ Python task runner لم يبدأ لأن بيئته المعزولة غير موجودة. سجل n8n يحذر أن تشغيل npm مباشرة على المضيف سيُلغى في إصدار مستقبلي ويتطلب Docker؛ لا تثبت Docker حسب التوجيه، وأعد تقييم n8n قبل أي ترقية مستقبلية.

لتشغيله يدوياً من جذر المشروع بعد مراجعة التنبيهات:

```sh
cd /Users/aliadil/Projects/ContentFactory
N8N_LISTEN_ADDRESS=127.0.0.1 N8N_HOST=127.0.0.1 N8N_PORT=5678 N8N_PROTOCOL=http N8N_USER_FOLDER="$PWD/lab/n8n-local/data" N8N_DIAGNOSTICS_ENABLED=false N8N_PERSONALIZATION_ENABLED=false N8N_VERSION_NOTIFICATIONS_ENABLED=false N8N_TEMPLATES_ENABLED=false ./lab/n8n-local/node_modules/.bin/n8n start
```

افتح `http://127.0.0.1:5678`. الإيقاف: `Ctrl+C` في نفس الطرفية. الاستئناف: أعد أمر التشغيل أعلاه. أول خطوة معلقة: راجع قائمة advisories للإصدار المثبت وتحقق من release ثابت أحدث يعالجها، بدون `npm audit fix --force`؛ أعد `npm audit` ثم اختبر الإقلاع والواجهة قبل أي Workflow. لا تستورد Workflow أو تضف Credentials حتى تُراجع التنبيهات وتُفعّل الحاجة صراحةً.

## استئناف 2026-11-17: مراجعة npm audit وتقييم التحديث

- بدأنا من `main` عند `a518e64`، Git نظيف. لم أشغّل n8n، ولم أربط حسابات أو أستورد Workflows، ولم أغيّر `package.json`, `package-lock.json`, أو `node_modules`.
- أعدت `npm audit --omit=dev --json` لمثبت `n8n@2.47.7`. النتيجة: 145 إدخال (7 critical، 69 high، 67 moderate، 2 low)، 125 advisory فريدة، 204 عقدة اعتماد مكررة؛ واحد direct هو `n8n` نفسه بسبب سلسلة اعتمادياته، والباقي انتقالية. JSON محفوظ فقط بمخبأ npm المستثنى من Git: `lab/n8n-local/.npm-cache/audit-2.47.7.json`.
- شروط أهم advisories، الحزم وإصداراتها المصنفة، وتحليل وصولها في localhost-only بلا Workflow/credentials موثق في [`docs/N8N_AUDIT_REVIEW.md`](docs/N8N_AUDIT_REVIEW.md). `127.0.0.1` يحد الاتصال المباشر من الشبكة لكنه لا يساوي عزل كامل؛ `ws` وعمليات محلية/متصفح تبقى ضمن نموذج الخطر. الخدمة بقيت متوقفة.
- فحص dist-tags بعد الإصدار الحالي: `stable/latest=2.47.7`، و`beta/next=2.48.4`. إصدار `2.48.4` مصنف رسمياً Pre-release، ومتطلبات Node `>=24.0.0`، وما ملاحظته المنشورة لا يثبت حل الـadvisories. ماكو stable أحدث مناسب مثبت أنه يعالجها، فلا ترقية أو تخفيض الآن. `npm audit fix` يقترح `1.17.0` كتغيير major رجوعي؛ ما انشغل.
- لا تحديث أو تعديل إعدادات خارج المشروع بهذه الجولة. `npm audit` استخدم cache المشروع. لم أغيّر الملفات المثبتة أو أشغّل scripts جديدة.
- الخطوة المعلقة الآن: إبقاء n8n متوقفاً، ومتابعة مسار الأداء بالبديل المحلي الموجود: بعد CSV مصرح به شغّل `python3 tools/analyze_platform_metrics.py lab/imports/platform-metrics-24h.csv --output lab/evidence/performance-decision-run-01.json`. لا حاجة إلى n8n لهذا التحليل. إذا ظهر stable أحدث، راجع dependency tree وaudit له في candidate منفصل أولاً، وتحقق تحديداً من `ws`, `fast-xml-parser`, `form-data`, `tar`, `zod` قبل أي تغيير.

## استئناف 2026-11-17: منع قرارات TEST_ONLY التشغيلية

- تابعت من `main` عند commit `95cd1aa`، وكانت الشجرة نظيفة. راجعت مسارات خط الإنتاج. n8n بقي متوقفاً؛ لم أنتظر ملف أداء أو صوت ولم أستخدم بيانات خارج fixture التجربة.
- استعملت محلل المقاييس المحلي الموجود `tools/analyze_platform_metrics.py`. لاحظت أن الكود السابق يمنع توسع/نشر بيانات synthetic لكنه كان يظل يخرج توصيات hook/Carousel/تكرار؛ هذا يتيح إساءة قراءة نتيجة TEST_ONLY كتوجيه إنتاجي.
- عدلت المحلل: إذا كان `data_origin` يحوي `synthetic` أو `test_only`، تصبح كل candidate recommendation=`test_only_no_action` مع سبب يمنع استخدامها للنشر أو التوسع أو قرار إنتاج. يستمر إخراج المقاييس والبوابات للتجربة فقط؛ تظل `scale_eligible=false`, `export_allowed=false`, `publish_allowed=false`.
- تحقق التشغيل الفعلي: `python3 tools/analyze_platform_metrics.py lab/fixtures/platform-metrics-TEST_ONLY.csv | python3 -c 'import json,sys; r=json.load(sys.stdin); assert r["mode"]=="TEST_ONLY_SYNTHETIC"; assert r["scale_eligible"] is False and r["export_allowed"] is False and r["publish_allowed"] is False; assert all(d["recommendation"]=="test_only_no_action" for d in r["decisions"]); print({"mode":r["mode"],"source_rows":r["source_rows"],"candidate_count":r["candidate_count"],"recommendations":sorted(set(d["recommendation"] for d in r["decisions"])),"scale_eligible":r["scale_eligible"],"export_allowed":r["export_allowed"],"publish_allowed":r["publish_allowed"]})'` — PASS: `TEST_ONLY_SYNTHETIC`, 26 صفاً، 4 candidates، لا توصية تشغيلية، والتوسع/التصدير/النشر جميعها `false`.
- الوثائق: حدثت `docs/LOCAL_WORKFLOW_NEXT_STEP.md` لتوضح حاجز TEST_ONLY. الملفات المتغيرة بهذه الدفعة: `tools/analyze_platform_metrics.py`, `docs/LOCAL_WORKFLOW_NEXT_STEP.md`, `HANDOFF.md`.
- الخطوة التالية: إذا توفر تصدير أداء محلي مُصرح به، انسخه إلى `lab/imports/platform-metrics-24h.csv` بعد إزالة أي معرفات غير لازمة ووثّق `data_origin=manual_export`؛ ثم شغّل `python3 tools/analyze_platform_metrics.py lab/imports/platform-metrics-24h.csv --output lab/evidence/performance-decision-run-01.json`. إذا لم يتوفر، لا تستخدم fixture التجريبية كدليل أو لاتخاذ قرار. لا تشغّل n8n.

## استئناف 2026-11-17: قالب إدخال محلي لبيانات الأداء

- البداية على `main` عند `0fecb28` وشجرة Git كانت نظيفة. راجعت `tools/analyze_platform_metrics.py`: الأعمدة الإلزامية هي 19 اسماً من `platform` إلى `data_origin`، والمنصات المقبولة youtube/tiktok/instagram/facebook، والأدوار candidate/baseline؛ التاريخ ISO؛ الحقول الرقمية غير سالبة. المحلل يتطلب كل الخانات الرقمية كأرقام، ولا يقبل الفراغ أو N/A كقيمة رقمية. قيم البوابات المعتمدة `rights_status=verified` و`quality_status=human_approved`.
- أنشأت `lab/imports/platform-metrics-24h.csv` بـ28 صفاً فارغ المقاييس: لكل منصة candidate واحد وستة baseline. ملأت `platform` و`role` وأسماء مستعارة للحساب/المنشور فقط. ماكو أرقام أداء أو بيانات TEST_ONLY أو حسابات حقيقية أو أسرار. `lab/imports/platform-metrics-24h.csv` مستثنى عبر `.git/info/exclude` ومحفوظ خارج Git.
- أضفت شرح التعبئة والمصادر الرسمية وتوفر المقاييس والحقول التي قد تغيب حسب المنصة في `docs/PLATFORM_METRICS_INPUT_GUIDE.md`. يوضح أن `reach` لا يُستبدل بـ`impressions`، وأن المقاييس الناقصة تبقى فارغة ولا يجوز تعويضها بصفر/تخمين. لا يُشغّل المحلل حتى تكتمل الأرقام المطلوبة؛ وقد تكون المقارنة غير قابلة للتشغيل على منصات/صيغ لا تعرض كل الحقول.
- تحققت بنيوياً من الملف: رؤوس الأعمدة مطابقة للأداة، 28 صف بيانات، لكل منصة 1 candidate و6 baseline، وحقول القياس/الحساسية فارغة؛ وتأكدت من تجاهله بواسطة Git. لم أشغل محلل الأداء على القالب الفارغ، ولم أتصل بحسابات أو منصات.
- الملفات: قالب محلي مستثنى `lab/imports/platform-metrics-24h.csv`؛ شرح متعقب `docs/PLATFORM_METRICS_INPUT_GUIDE.md`؛ هذا التحديث لـ`HANDOFF.md`.
- الخطوة التالية: افتح القالب محلياً ببرنامج جداول، واملأه من تقاريرك المصرح بها وفق `docs/PLATFORM_METRICS_INPUT_GUIDE.md`. إذا لم توفر المنصة حقلاً رقمياً مطلوباً مثل impressions أو saves، اتركه فارغاً ولا تشغّل المحلل ولا تخمّن قيمة؛ أوقف ذلك الصف لحين تقرير لاحق عن توافق الأداة.

## استئناف 2026-11-17: اختبار TEST_ONLY لمحلل الأداء

- بدأت على `main` عند commit `b685caf`؛ راجعت HANDOFF والمحلل والقالب. لم أستخدم حسابات أو بيانات أداء من الإنترنت، ولم أنشر أو أتصل بأي منصة.
- أبقيت `lab/imports/platform-metrics-24h.csv` بدون تغيير. هو قالب تعبئة من 28 صفاً (وليس ملفاً بلا صفوف): 4 منصات مع aliases وأدوار جاهزة، وكل قياسات الأداء والتاريخ والحقول الحساسة فارغة. تحقق مستقل أكد ذلك قبل وبعد التشغيل.
- أنشأت fixture مستقلة `lab/evidence/platform-metrics-TEST_ONLY.csv` تضم 28 صفاً اصطناعياً كاملاً: لكل منصة مرشح واحد وستة baseline، بمعرفات مثل `account_yt_test` و`post_yt_test_01`، وكل صف موسوم `data_origin=synthetic_TEST_ONLY`. لم أغير المحلل لأن حاجز `synthetic`/`TEST_ONLY` كان موجوداً بالفعل.
- أمر التشغيل الوحيد للمحلل كان على fixture التجريبية: `python3 tools/analyze_platform_metrics.py lab/evidence/platform-metrics-TEST_ONLY.csv --output lab/evidence/platform-metrics-TEST_ONLY-result.json`.
- النتيجة PASS: `mode=TEST_ONLY_SYNTHETIC`، 28 صفاً، 4 candidates، وكل التوصيات `test_only_no_action`؛ `scale_eligible=false`, `export_allowed=false`, `publish_allowed=false`. تحققنا برمجياً من القيم بعد إنشاء النتيجة.
- ملفات الإدخال والنتيجة تحت `lab/evidence/` مستثناة بـ`.gitignore`؛ القالب الحقيقي مستثنى عبر `.git/info/exclude`. لن تدخل بيانات الاختبار أو الإدخال الحقيقي في Git. ماكو أسرار أو حسابات أو اتصال خارجي.
- الخطوة التالية: اختبار آخر إن رغبت، أو ابدأ تعبئة القالب الحقيقي يدوياً من بيانات مصرح بها. لا تستخدم fixture كأداء فعلي ولا تتخذ منها قرار نشر/توسع.

## استئناف 2026-11-17: عقد حزمة محتوى AR/EN متعدد التنسيقات

- بدأت من `main` عند `ccbd962`، Git كان نظيفاً. راجعت مرجع التنفيذ وملفات `lab/motion.mjs`, `lab/render_mac.py`, `tools/record_media_evaluation.py`, وسجل حالات `lab/checkpoint.py`. الموجود يوفر رندر ثابت وتسجيل ميتاداتا للوسائط، لكنه لا يقرأ عقد محتوى موحداً؛ لذلك أنشأت قالب JSON ودليل عقد ومثالاً محلياً بدلاً من تعديل renderer أو بناء نظام كبير.
- أضيف `lab/templates/content-package-template.json`: يجمع fact base ومصادره، AR-white وEN، short video وCarousel وYouTube long، سجل assets وترخيصها وبصمتها، overrides منفصلة للمنصات الأربع، ومراجعات fact/rights/quality/language/audio/technical. الحساب والوجهة فارغان؛ المعاينة المحلية مسموحة والنشر الخارجي false ومقفول افتراضياً.
- أضيف `lab/evidence/content-package-demo-TEST_ONLY.json`: مثال مسودة ثنائي اللغة أصلي عن ملاحظة مشهد كوب، بلا أصول أو ادعاءات واقعية أو مواد مقتبسة، موسوم TEST_ONLY. بوابات الحقائق والحقوق والجودة والصوت غير معتمدة والنشر blocked. لم يُنشأ فيديو؛ الرندر الموجود ثابت ولا يقرأ الحزمة.
- أضيف `docs/CONTENT_PACKAGE_CONTRACT.md` لشرح بنية السجل والحقول وبوابات المرور/الإيقاف وكيفية حفظ provenance والترخيص.
- أمر التحقق الهيكلي الناجح بـPython stdlib (لا يشغّل renderer أو محلل أداء):

```sh
python3 - <<'PY'
import json
from pathlib import Path

t = json.loads(Path("lab/templates/content-package-template.json").read_text())
s = json.loads(Path("lab/evidence/content-package-demo-TEST_ONLY.json").read_text())
formats = {"short_video", "carousel", "youtube_long"}
platforms = {"youtube", "tiktok", "instagram", "facebook"}
assert set(t["copy"]["ar_white"]) == set(t["copy"]["en"]) == formats
assert set(t["platform_adaptations"]) == set(s["platform_adaptations"]) == platforms
assert s["lifecycle"]["test_only"] is True
assert all(t["release_control"][k] is False for k in ("external_publication_enabled", "external_publication_approved"))
assert all(s["release_control"][k] is False for k in ("external_publication_enabled", "external_publication_approved"))
assert all(g["status"] != "approved" for g in s["review_gates"].values())
assert s["sources"] == s["assets"] == s["fact_base"]["claims"] == []
assert all(not a["account_alias"] and not a["publishing_enabled"] for a in s["platform_adaptations"].values())
print("PASS")
PY
```

- نتيجة التحقق: PASS: لغتان، ثلاثة تنسيقات، أربعة adapters، والنشر غير مفعّل ولا معتمد؛ العينة بلا حسابات أو مصادر أو أصول أو ادعاءات.

- الملفات المضافة/المعدلة: `lab/templates/content-package-template.json`, `lab/evidence/content-package-demo-TEST_ONLY.json` (ignored محلياً), `docs/CONTENT_PACKAGE_CONTRACT.md`, `README.md`, و`HANDOFF.md`. هذه دفعة عقد وتوثيق؛ لا كود تشغيل جديد.
- الخطوة التالية: بناء adapter محلي صغير يقرأ حزمة JSON **بعد اعتمادها** ويغذي `lab/motion.mjs` أو مشهد Motion Canvas الحالي؛ قبل ذلك حدد أي renderer تريد وصمم ربطاً لا يفتح بوابة نشر. لا تُنشئ حسابات ولا تشغّل n8n.

## استئناف 2026-11-17: مسار محلي من الحزمة إلى المخرجات

- بدأت من `main` عند أحدث commit فعلي `7018f78`، وكانت الشجرة نظيفة. راجعت HANDOFF والعقد `lab/templates/content-package-template.json` وعينة `lab/evidence/content-package-demo-TEST_ONLY.json` والرندر `lab/motion.mjs` وأدوات SVG/FFmpeg/FFprobe. ما شغّلت n8n، ولا اتصلت بمنصة، وما لمست StageCore أو Kids Studio.
- أضفت `tools/render_content_package.py` كمحوّل/مدقق صغير يربط العقد بالرندر الموجود. يرفض الحزمة غير المكتملة، اللغة أو التنسيق غير المدعوم، وغياب وسم TEST_ONLY، أو إعدادات حساب/نشر؛ ويتحقق من ادعاءات الحقائق والأصول المرخصة وبصمتها إذا وُجدت. يقصر المدخلات على `lab/` والمخرجات على `lab/evidence/`، ويرفض استبدال المخرج. يكتب حالة مرحلة وبصمة إدخال لاستئناف آمن بعد الانقطاع.
- وسّعت `lab/motion.mjs` ليقرأ خطة المحوّل، مع الإبقاء على وضع الرندر القديم بلا معاملات. `lab/render_mac.py` يستخدم `rsvg-convert` وFFmpeg وFFprobe الموجودة لإنتاج الوسائط والميتاداتا. لا توجد أصول خارجية؛ رسمة الكوب SVG محلية. أصلحت اتجاه دعوة الإجراء العربية بعد أن أظهر الفحص البصري قصّاً عند حافة الإطار.
- أنشأت `tools/test_content_package_pipeline.py` لاختبار ملف إدخال مفقود، حزمة ناقصة، مقاطعة توليد SVG ثم الاستئناف، ورفض استبدال تقرير موجود. الاختبار يستخدم مؤقتاً داخل `lab/evidence/` ويحذفه بعده. النتيجة الفعلية: PASS؛ نتج Shortان صامتان و10 شرائح Carousel ومخططا Storyboard، وكل بوابات النشر والصوت `false`.
- الرندر النهائي المحلي الحالي موجود في `lab/evidence/content-package-demo-TEST_ONLY-render-04/` (مستثنى من Git). التقرير: `artifacts/render-report.json`. أمره:

```sh
/usr/bin/time -l python3 tools/render_content_package.py \
  --input lab/evidence/content-package-demo-TEST_ONLY.json \
  --output lab/evidence/content-package-demo-TEST_ONLY-render-04 \
  --platform all --preview-seconds 5
```

- النتيجة المقاسة: زمن 40.211 ثانية؛ CPU للأبناء 30.587 ثانية user و3.592 ثانية system؛ ذروة RSS المسجلة 432.47 MiB. خرجا الفيديو `artifacts/short-ar-TEST_ONLY.mp4` و`artifacts/short-en-TEST_ONLY.mp4`، كل واحد 1080×1920 و24fps و5 ثوانٍ/120 إطاراً، بلا صوت؛ حجماهما 119,579 و128,708 بايت. Carousel: 5 PNG لكل لغة، 1080×1350؛ Storyboard: 6 لوحات PNG لكل لغة بدقة 1920×1080 وملف Markdown لكل لغة. مجموع أحجام مخرجات التقرير الـ26 نحو 2.44 MiB؛ التقرير يسجل حجم كل عنصر.
- راجعت إطارات Short العربية والإنكليزية، شرائح Carousel عربية، ولوحة Storyboard عربية. معالجة RTL/تشكيل Geeza Pro ظاهرة والنصوص المقروءة في العينات المحددة داخل الإطار بتباين واضح. هذا فحص بصري جزئي؛ يلزم حكم بشري على جمال الحركة، تقطيع الأسطر، ملاءمة المحتوى والترجمة واتساق النص. نسخة Short معاينة 5 ثوانٍ من هدف 20 ثانية؛ لا صوت ولا حلقة YouTube نهائية. ادعاءات/حقوق العينة غير معتمدة، والجودة تنتظر مراجعة بشرية. الصوت العربي الطبيعي المرخص تجارياً ما زال فجوة مفتوحة.
- الفحوص الأخيرة: `python3 tools/test_content_package_pipeline.py` PASS؛ `python3 -m py_compile tools/render_content_package.py tools/test_content_package_pipeline.py lab/render_mac.py` PASS؛ `node --check lab/motion.mjs` PASS؛ `git diff --check` PASS. الملفات المتعقبة المعدلة/المضافة: `README.md`, `HANDOFF.md`, `lab/motion.mjs`, `lab/render_mac.py`, `tools/render_content_package.py`, `tools/test_content_package_pipeline.py`. لا تُضف مجلدات الرندر أو fixture إلى Git.
- إعادة التشغيل: استعمل اسم إخراج جديداً، مثلاً `lab/evidence/content-package-demo-TEST_ONLY-render-05`، مع الأمر أعلاه وبدّل `--output`. الاختبار: `python3 tools/test_content_package_pipeline.py`. للاستئناف بعد مقاطعة مقصودة/غير مكتملة، افحص `.content-package-demo-TEST_ONLY-render-05.work` ثم أعد الأمر مع `--resume`؛ لا تغيّر الإدخال أو إعداداته.
- الخطوة التالية: افتح فيديوهَي Short والـCarousel والـStoryboard محلياً لحكم بشري على الخط والإيقاع وترجمة AR/EN، ثم حدّث حالة `review_gates` في نسخة العمل بعد المراجعة فقط. لا تشغّل n8n ولا تفتح بوابات الحقوق/الصوت/النشر من هذا الرندر. احتفظ ببيانات TEST_ONLY للتجارب وحدها.

## استئناف 2026-11-17: تأهيل جودة رندر حزمة TEST_ONLY

- بدأت من أحدث commit فعلي `875f564` على `main`، وحالة Git كانت نظيفة. قرأت التعليمات وهذا الملف، وفحصت `lab/evidence/content-package-demo-TEST_ONLY-render-04/artifacts/`. ما شغّلت n8n، ولا اتصلت بحساب، ولا نشرت محتوى أو أضفت صوتاً.
- أضفت `tools/review_content_package_render.py` بأدوات Python وFFmpeg/FFprobe و`rsvg-convert` الموجودة فقط. يفحص فك H.264 والأبعاد والمدة والإطارات وFPS والصوت، مقاسات PNG وعدد الشرائح واللوحات، manifest، ووسم TEST_ONLY وأسماء الملفات. ينشئ Contact Sheet واحداً يضم أربع لقطات زمنية من كل Short وكل شرائح Carousel ولوحات Storyboard. ما ثبّت اعتماديات.
- ملف المعاينة النهائي: `lab/evidence/content-package-demo-TEST_ONLY-review-02/content-package-contact-sheet-TEST_ONLY.png`. قائمة المستخدم: `human-review-TEST_ONLY.md`؛ النتائج التقنية: `technical-checks-TEST_ONLY.json`. جميع قيم وضوح النص واتجاه العربية والتباين والقص وتنوع الحركة والإيقاع والهوية والترجمة «بانتظار مراجعة المستخدم»؛ ما أعطيت درجة بشرية.
- ظهر في `review-01` تداخل أسماء ملفات Storyboard الطويلة أسفل مصغرات Contact Sheet. عدّلت labels في أداة المعاينة إلى `Panel 01`/`Slide 01` مع إظهار اللغة في عنوان المجموعة، وأنتجت `review-02` باسم جديد؛ المخرجات القديمة بقيت كما هي. بالفحص البصري للـcontact sheet وعينات بالحجم الكامل من Carousel العربية وStoryboard العربية، ما ظهر قص أو خلل RTL موضوعي في المجموعة `render-04`؛ لذلك ما غيّرت نص الرندر أو معناه وما احتجت إعادة إنتاج ميديا. التباين واضح بالعينات، أما اعتماده فيبقى للمستخدم.
- فحوص `review-02` الفعلية: 7 من 7 PASS. الفيديوهان كلاهما H.264، `1080×1920`, 24fps، 120 إطاراً، 5.0 ثانية، والصوت 0 streams؛ فك الترميز بـFFmpeg نجح. أخذت 4 لقطات من كل فيديو، وكلها متميزة (فحص آلي يؤكد تغيّر الصورة عبر الزمن، مو تقييم سلاسة). عشر شرائح Carousel `1080×1350`، و12 لوحة Storyboard `1920×1080`. 28 ملفاً مفحوصاً، وأسماء الميديا موسومة `TEST_ONLY` وخالية من كلمات مثل `final` و`production` و`approved`؛ تقرير الرندر يؤكد تعطيل النشر والصوت. الحالة `PENDING_USER_REVIEW`.
- قست الرندر السابق المحفوظ نفسه `render-04`: 40.211 ثانية، CPU أبناء 30.587 user + 3.592 system، ذروة RSS 432.47 MiB، مجموع 2,555,498 بايت لـ26 مخرجاً. المقارنة مع `render-03` عادلة تقريباً كتشغيلين متقاربين: نفس الحزمة والإعدادات ومجموعة 5 ثوانٍ؛ `render-03` كان 40.444 ثانية و30.766 + 3.592 CPU و432.92 MiB و2,554,341 بايت. الفرق صغير، وهي قراءة تشغيلين وليست benchmark مضبوطاً. أداة المعاينة نفسها لا تعيد الرندر.
- الفحص الحالي لمسار الإعادة/الاستئناف/منع الاستبدال هو `python3 tools/test_content_package_pipeline.py`: يجب أن يرفض المدخل والحزمة الناقصين، يستأنف بعد المقاطعة، ويرفض استبدال المخرج. يترك الميديا السابقة كما هي. أمر فحص وإنشاء معاينة جديدة:

```sh
python3 tools/review_content_package_render.py \
  --artifacts lab/evidence/content-package-demo-TEST_ONLY-render-04/artifacts \
  --output lab/evidence/content-package-demo-TEST_ONLY-review-03
open lab/evidence/content-package-demo-TEST_ONLY-review-03/content-package-contact-sheet-TEST_ONLY.png
python3 tools/test_content_package_pipeline.py
```

- تظل معاينة الحركة الزمنية محدودة: راجعت لقطات موزعة وأكدت تغير العناصر، لكن ما قيّمت سلاسة التشغيل بمشاهدة متصلة. يلزم المستخدم أن يشاهد الفيديوين فعلياً ويراجع الإيقاع وتنوع الحركة وجودة AR/EN. حقوق العينة والجودة والصوت والتصدير والنشر غير معتمدة؛ الصوت العربي الطبيعي المرخص تجارياً ما زال فجوة.

## استئناف 2026-11-17: تحسين اتجاه الموشن ووضوح النص

- البداية على `main` عند `fe95b60` وبحالة نظيفة. فتحت أولاً ورقة `review-02` ومخرجات `render-04`: كان المشهد صغيراً وسط فراغ، والكوب مكرراً بنفس الحجم، والنص أقل بروزاً من المطلوب. لا تغيير في `render-04` أو `review-02`، ولا n8n أو حسابات أو نشر أو صوت، ولا لمس لـStageCore أو Kids Studio.
- أنشأت اتجاهين مرئيين باستعمال رسوم SVG المحلية نفسها والألوان والخطوط الموجودة، من دون أصل خارجي: `editorial` بخلفية ورقية وبطاقات هادئة، و`spotlight` بخلفية داكنة وأشرطة لونية ومناطق تركيز. النصوص والمعنى بقيا من العينة؛ لم أضف ادعاءً أو أغيّر ترجمة.
- ضفت خيار `--visual-direction editorial|spotlight` للمحوّل، ويُسجل الاتجاه في خطة الرندر وحالته وتقريره؛ يتأكد الاستئناف من عدم تبدّل الاتجاه خلال العمل. زدت حجم العنوان والإشارة، وزّعت Hook/الكوب/بطاقة المشهد/CTA على الإطار، وأضفت انتقالاً للنصوص (انزلاق وظهور قصير)، تحريكاً أوسع للكوب، ونقطة تركيز تنتقل بين اللون والضوء والبخار. صارت شرائح Carousel خمس لقطات متتابعة مع حركة/موضع مختلف للكوب، مؤشر تقدم، ونهاية تستخدم CTA الموجودة بالحزمة. كبرت مساحة storyboard وفصلت رسم الكوب عن بطاقة النص.
- كررت الفحص بعد كل عيب ظاهر: في Editorial الأول تلامست نقاط Carousel مع التذييل؛ نقلتها للأعلى وأعدت الرندر. في الجيل الثاني انقصّ عنوان نهاية الحلقة الإنكليزي؛ سمحت بثلاثة أسطر بحجم مقروء وأعدت الاتجاهين. في Spotlight ظهر شريط العنوان فوق حروف عنوان Carousel؛ أزحت العنوان وخفضت موضع الملاحظة تحت الشريط وأعدت الرندر. غيّرت لقطات المعاينة من أزمنة انتقال يظهر فيها النص خافتاً إلى `0.5, 2.4, 4.0, 4.8` ثانية لعرض المراحل الثلاث.
- مجموعتا المقارنة النهائيتان الجديدتان (كل الملفات داخل المسارات موسومة `TEST_ONLY`): `lab/evidence/content-package-demo-TEST_ONLY-direction-editorial-v3/` و`lab/evidence/content-package-demo-TEST_ONLY-direction-spotlight-v3/`. ورقتا المعاينة: `...editorial-v3-review-02/content-package-contact-sheet-TEST_ONLY.png` و`...spotlight-v3-review-02/content-package-contact-sheet-TEST_ONLY.png`. بيانات المقارنة والمعايير: `design-direction-decision-TEST_ONLY.md` داخل مجلد المراجعة الأخير.
- اخترت `spotlight` لهذه الدفعة لأن تباين العنوان/الخلفية المقاس 14.99:1 مقابل 10.38:1 في Editorial، وتباين النص الثانوي 10.53:1 مقابل 7.24:1، وحركة الكوب أوسع (±110px و±0.08 scale مقابل ±48px و±0.055). Editorial أهدأ في القراءة؛ الاتجاه المختار يحقق طلب حركة أوضح واستغلال أكبر للمساحة. هذا اختيار تصميم تجريبي، مو موافقة جودة بشرية.
- التقارير تقيس التشغيل على الحزمة نفسها و5 ثوانٍ و24fps: Spotlight `45.156s`, CPU للأبناء `34.001 user + 4.623 system`, ذروة RSS `434.28 MiB`, وحجم 26 مخرجاً `2,864,064 bytes` (~2.73 MiB). Editorial `49.430s`, `35.401 + 4.865s`, `434.20 MiB`, `2,873,714 bytes`. مقارنة `render-04` السابق `40.211s`, `30.587 + 3.592s`, `432.47 MiB`, `2,555,498 bytes`: المختار زاد 4.945s وقرابة 0.45% في الذروة و308,566 bytes؛ هذا اتجاه مقاس لا benchmark مضبوط بسبب تعقيد الرسوم المختلف.
- فيديوهات Spotlight الجديدة: `artifacts/short-ar-TEST_ONLY.mp4` (275,778 B) و`short-en-TEST_ONLY.mp4` (302,410 B)، H.264، `1080×1920`, 24fps، 120 إطاراً، 5.0s، بلا صوت. كل مجموعة بيها 10 Carousel PNG (1080×1350)، 12 لوحة Storyboard PNG (1920×1080)، وملفان نصيان للـStoryboard.
- شغّلت `tools/review_content_package_render.py` على الاتجاهين: 7/7 فحوص آلية PASS لكل اتجاه (فك الفيديو، الأبعاد/المدة/FPS/الإطارات/الصوت، اختلاف أربع لقطات زمنية، أبعاد وعدد PNG، paths، وسم TEST_ONLY، وعدم التباس الإنتاج، تعطيل النشر). `python3 tools/test_content_package_pipeline.py` PASS؛ رفض ملف/حزمة ناقصة، استأنف الانقطاع، ورفض الاستبدال. `py_compile`, `node --check lab/motion.mjs`, و`git diff --check` PASS.
- فتحت الفيديو العربي والإنكليزي محلياً في QuickTime، لكن واجهة المراجعة لم تتيح لي معاينة/تأكيد تشغيل متصل داخل الجلسة؛ لذلك لا أسجل أن السلاسة اجتازت الفحص. Contact Sheet يعرض لقطات ساكنة موزعة من الفيديوين فقط. اطلب من المستخدم تشغيلهما فعلياً ومراجعة الذوق والسلاسة والإيقاع. قائمة `human-review-TEST_ONLY.md` الجديدة تبقي كل البنود بانتظار المستخدم: وضوح/حجم النص، RTL، التباين والقص، التنوع والسلاسة، الإيقاع، الذوق، ترابط Carousel، وضوح Storyboard والترجمة.
- التعليمات المختصرة في README. إعادة التشغيل باختيار `--visual-direction spotlight` واستخدام مجلد `TEST_ONLY` جديد؛ لا تستبدل أي إخراج قديم. بوابات الحقوق والجودة والتصدير والنشر بقيت مغلقة، والصوت غير موجود. الخطوة التالية: شغّل فيديوهَي Spotlight وشاهد كل واحد كاملاً؛ بعد رأيك حدّث قائمة المراجعة يدوياً فقط ولا تغيّر اعتماد البوابات قبل موافقتك الصريحة.
