# تسليم واستئناف مصنع المحتوى

آخر تحديث: 2026-11-17 (`Asia/Baghdad`)

## الحالة المحفوظة

- المجلد: `جذر المستودع`، الفرع `main`؛ نقطة البداية كانت commit `fd44f67`، والدفعات السابقة محفوظة حتى commit `654475b`.
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
cd "$(git rev-parse --show-toplevel)"
uv pip install --python lab/voice-env/bin/python torch==2.15.0 misaki==0.9.4 espeakng-loader==0.2.4
```

إذا انحل عائق الترخيص، ولّد عينة عربية قصيرة `TEST_ONLY` بنفس نص `Majed`، وسجّل زمن التوليد والحجم. Nabra فصحى `MSA` وصوته الوحيد موصوف في البطاقة بأنه أنثوي؛ سجّل الجندر كبيانات فقط، ولا تعتمد الصوت قبل مقارنة الاستماع والطبيعية والوضوح واللهجة.

## استئناف 2026-11-17: مراجعة Habibi-TTS ومرشح بديل

- بدأ الفحص على `main` وبحالة نظيفة عند `9b22104`; المستودع هو `جذر المستودع`. بقيت الملفات السابقة دون تعديل قبل هذه الدفعة.
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
cd "$(git rev-parse --show-toplevel)"
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
cd "$(git rev-parse --show-toplevel)"
python3 tools/analyze_platform_metrics.py lab/imports/platform-metrics-24h.csv --output lab/evidence/performance-decision-run-01.json
```

- بعد ذلك راجع جودة المقترح بشرياً، ولا توسّع إلا بإشارة على موضوعين مع QA مقبول وصرف خارجي صفر. الصوت التجاري الطبيعي يبقى مستقلاً ومعلّقاً عند توثيق مصادر التدريب والرخصة.

## أوامر متابعة الموشن

تشغيل المحرر على localhost فقط:

```sh
cd $(git rev-parse --show-toplevel)/lab/motion-canvas
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
cd "$(git rev-parse --show-toplevel)"
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

## استئناف 2026-11-17: ثلاثة اتجاهات بصرية جديدة بعد رفض Spotlight

- بدأت من `main` وHEAD الفعلي `6915741`؛ كانت الشجرة نظيفة. راجعت `HANDOFF.md` و`AGENTS.md` وأوراق معاينة `Spotlight v3`. أتعامل مع Spotlight كمرجع للمشكلة فقط، ولا أوصي باعتماده أو متابعة ترقيعه. ما تغيّر `render-04` أو `review-02` أو مجلدات المخرجات القديمة.
- تشخيص Spotlight: تسلسل رأسي ثابت (عنوان، كوب مركزي، شريط سفلي) يترك فراغاً غير مقصود؛ خلفية داكنة مع شريط مائل متكرر؛ الرسم الصغير لا يوازن حجم الإطار؛ الكوب/الدائرة/البخار يتكررون كأنهم هوية؛ الحركة تغيّر موقع/مقياس/حلقة تركيز ولا تصنع انتقالاً سردياً كافياً؛ تبديل النص وحده لا يضمن إيقاعاً. التوافق بين Geeza Pro وArial يحتاج حكم بصري. التشغيل المتصل لـSpotlight لم يُشاهد.
- أضفت ثلاثة اتجاهات مختلفة عبر SVG مرسوم محلياً وخطوط النظام الموجودة فقط: `fieldnotes` (دفتر ملاحظات فاتح ورسوم للون/الضوء/البخار)، `typeplay` (ملصق طباعي هندسي متحرك)، و`gallery` (أشكال حلقية طبقية بهوية أزرق/مرجاني/ليموني). `fieldnotes` لا يعرض الكوب في كل مشهد، و`typeplay` يستبدل رسمه بأشكال في بعض مشاهد Carousel وStoryboard؛ `gallery` يبقي الحلقات متكررة وهذا قيد موثق. لم أغيّر النص أو معناه ولم أضف أصولاً خارجية أو صوتاً.
- عالجت عيوباً ظهرت في المعاينة التكرارية: انقصّ عنوان Carousel الإنكليزي في `typeplay` ثم خُفّض حد اللف ليظهر بسطرين؛ صار نص `gallery` السفلي أزرق داكناً فوق المساحة الفاتحة؛ نقلت التسميات اللاتينية لجهة آمنة حتى لا تخرج من الحافة العربية؛ فصلت نص Storyboard الإنكليزي عن الرسم؛ خفّضت حجم رسم الكوب في `gallery`. المخرجات الأقدم للاتجاهات التجريبية بقيت محفوظة، والمجلدات النهائية هي `fieldnotes-v3` و`typeplay-v4` و`gallery-v3`.
- المعاينات النهائية:
  - `fieldnotes`: Contact sheet `lab/evidence/content-package-demo-TEST_ONLY-visual-fieldnotes-v3-review-02/content-package-contact-sheet-TEST_ONLY.png`؛ فيديو AR/EN في `lab/evidence/content-package-demo-TEST_ONLY-visual-fieldnotes-v3/artifacts/`.
  - `typeplay`: Contact sheet `lab/evidence/content-package-demo-TEST_ONLY-visual-typeplay-v4-review-02/content-package-contact-sheet-TEST_ONLY.png`؛ فيديو AR/EN في `lab/evidence/content-package-demo-TEST_ONLY-visual-typeplay-v4/artifacts/`.
  - `gallery`: Contact sheet `lab/evidence/content-package-demo-TEST_ONLY-visual-gallery-v3-review-02/content-package-contact-sheet-TEST_ONLY.png`؛ فيديو AR/EN في `lab/evidence/content-package-demo-TEST_ONLY-visual-gallery-v3/artifacts/`.
  - المقارنة والتشخيص والقياسات في `lab/evidence/content-package-demo-TEST_ONLY-visual-comparison/visual-directions-comparison-TEST_ONLY.md` و`motion-frame-analysis-TEST_ONLY.json`. قوائم المراجعة في كل مجلد review؛ البنود كلها بانتظار المستخدم.
- فحوص كل اتجاه: `tools/review_content_package_render.py` PASS، 7/7 لكل مجموعة؛ فحص H.264 وفك كامل، 1080×1920 / 24fps / 120 إطاراً / 5 ثوانٍ، بلا صوت، عشر PNG Carousel و12 لوحة Storyboard بأبعادها الصحيحة، ووسم TEST_ONLY وتعطيل النشر. حللت الإطارات الـ120 لكل فيديو على نسخة 48×86 رمادية؛ تغيّر بكسل في 119/119 انتقالاً. هذه إشارة اختلاف بكسلي وليست حكماً على الحركة أو السلاسة.
- القياسات (الوقت، CPU أبناء، الحجم، التباين) مدونة في تقرير المقارنة: `fieldnotes` 40.608s و2,033,024 B؛ `typeplay` 40.849s و2,336,903 B؛ `gallery` 41.013s و2,813,228 B. تباين العنوان/النص الثانوي حسب الألوان الأساسية: fieldnotes 11.87:1 / 6.45:1، typeplay 10.94:1 / 8.15:1، gallery 8.54:1 / 7.36:1.
- شغّلت `python3 tools/test_content_package_pipeline.py`: PASS؛ رفض مدخلاً وحزمة ناقصين، استأنف render متوقفاً بـ`fieldnotes`، رفض استئناف بإعداد اتجاه مختلف، ورفض الكتابة فوق تقرير موجود. كما نجح `node --check lab/motion.mjs` و`python3 -m py_compile tools/render_content_package.py tools/test_content_package_pipeline.py tools/review_content_package_render.py`. فشل أمر توليد واحد بسبب كتابة `tools.render_content_package.py` بنقطة بدل `/`؛ صححته وأنتجت الاتجاهات بنجاح.
- README محدث. لم تُشاهد ملفات Short بتشغيل متصل داخل الجلسة؛ يجب على المستخدم تشغيل الفيديوهات ومراجعة السلاسة والذوق وسهولة القراءة على الهاتف وتوازن النص/الصورة والترجمة. الموصى بمشاهدتهما أولاً `fieldnotes` (وضوح معرفي) و`typeplay` (حركة طباعية)، وهذا ترتيب للمعاينة فقط، مو اعتماد أو اختيار نهائي. `gallery` ما زال خياراً للمقارنة.
- كل شيء `TEST_ONLY` ومحلي وصامت؛ الحقوق والجودة والتصدير والنشر غير معتمدة/مغلقة. لا n8n ولا حسابات ولا منصات. لا commit الآن بطلب المستخدم؛ الملفات المتعقبة معدّلة محلياً وغير محفوظة في commit. الخطوة التالية: اطلب اختيار المستخدم بعد فتح Contact sheets وتشغيل مقاطع `fieldnotes` و`typeplay`، ثم حدّث القرار/قائمة المراجعة وبعد موافقته احفظ التعديلات محلياً من دون push.

## استئناف 2026-11-17: مقارنة مكتبات موشن جاهزة

- البداية تحققت: `main`, HEAD `6915741`. ملفات العمل المتعقبة من الدفعة السابقة ظلت معدّلة كما هي؛ ما مسحتها ولا سويت commit. ما تغير محرك المصنع أو n8n، وما صار نشر.
- أنشأت معاينة معزولة تحت `lab/evidence/motion-engine-compare-TEST_ONLY/` واستخدمت Motion Canvas المثبت `3.17.2` مع Node/npm وFFmpeg الموجودين. استخدمت 3 تكوينات معرفية مترابطة (افتتاحية عدسة/بخار، بطاقات مقارنة، خاتمة طباعية/حلقية) بنص عربي أبيض وإنكليزي، ورسوم مرسومة بالكود وخطوط النظام. العرض المتصل شوهد داخل المحرر للغتين.
- أصلحت غلطة ظهور الشرح والخاتمة شفافة، وبعدها عالجت قصّ الكلمات العربية الصغيرة داخل البطاقة بأرقام تسلسل `01–03`؛ النص العربي الأساسي باقٍ بالعناوين والسطر المساند. contact sheet: `lab/evidence/motion-engine-compare-TEST_ONLY/motion-canvas-contact-sheet-TEST_ONLY.png`. MP4: `motion-canvas/motion-canvas-ar-v2-TEST_ONLY.mp4` و`motion-canvas/motion-canvas-en-TEST_ONLY.mp4` داخل مجلد المقارنة.
- النتيجة الفعلية لكل فيديو: H.264، `1080×1920`, `24fps`, 141 إطاراً، 5.875 ثانية، بلا صوت. decode كامل نجح؛ الأحجام 515,231 و575,869 بايت. كتابة تسلسل الإطارات حسب الطوابع الزمنية قرابة 1.69 و1.72 ثانية؛ تحويل FFmpeg قرابة 0.44 و0.45 ثانية؛ أقصى RSS للترميز 1.14GB تقريباً. ذروة ذاكرة مهمة المتصفح لم تُقَس. `tsc --noEmit` و`git diff --check` نجحا.
- راجعت Motion Canvas وأمثلة المشروع؛ الأمثلة MIT لكن مستودع الأمثلة يعتمد 3.15.0 وVite 4 وبعض الأصول تحتاج تدقيقاً منفصلاً. تقرير المقارنة: `lab/evidence/motion-engine-compare-TEST_ONLY/engine-comparison-TEST_ONLY.md`.
- RenderComp: راجعت commit `f648980` وثلاثة مكونات. الكود والقوالب MIT (11MB source-only)، لكن Remotion `4.0.518` له ترخيص proprietary منفصل؛ ما ثبتت أهليتنا للترخيص المجاني وما ثبتت الحزمة الكبيرة/المتصفح. لا زمن رندر أو ذاكرة مقاسة ولا تقييم عربية تنفيذي.
- OpenMontage: راجعت SHA `2e003e65` فقط. AGPL-3.0، والمتطلبات تشمل Python/FFmpeg وNode patched `24.22.1+` أو المسارات الموثقة الأخرى؛ الموجود `24.21.0`. `make setup` يثبت Python dependencies وPiper وRemotion composer؛ لذلك لا clone/install/run بهالدفعة ولا ترقية Node.
- التوصية العملية: استمر باختبار Motion Canvas الحالي كمرشح فقط، ولا تبدّل محرك المصنع ولا تعتمد تجارياً. RenderComp يبقى مشروطاً بحسم Remotion license؛ OpenMontage يبقى مؤجلاً لمتطلبات Node وAGPL وحجم التهيئة. بوابات الحقوق والجودة والتصدير والنشر بعدها مغلقة.
- الخطوة التالية المحددة: افتح contact sheet وشغّل فيديو AR/EN، ثم أعطني رأيك بالسلاسة والذوق وقراءة العربي على هاتف. لا يوجد تقييم بشري أو اختيار نهائي مسجل. ما صار commit، لأن مراجعة الاتجاهات البشرية بعدها معلقة؛ `HEAD` ما زال `6915741`.

## استئناف 2026-11-18: درجات موشن Motion Canvas

- بدأت من `main` عند HEAD `6915741`. بقيت تغييرات Git الموجودة من العمل السابق كما هي، وما سويت commit. ما غيرت محرك المصنع أو ملفات المخرجات القديمة، وما أضفت صوتاً أو نشراً أو اتصالاً بمنصة.
- جهزت مشروعاً معزولاً للمقارنة تحت `lab/evidence/motion-canvas-motion-levels-TEST_ONLY/motion-canvas/` وأعدت استخدام `Motion Canvas 3.17.2` واعتماديات `lab/motion-canvas/node_modules` عبر symlink؛ ما نزلت ولا ثبتت حزم. `tsc --noEmit` و`vite build` نجحا. محاولة `npm run build` فشلت لأن النسخة المعزولة ما بيها script بهذا الاسم؛ شغلت فحص TypeScript وVite مباشرة ونجحا. أضفت ضمن المشروع المعزول إعداد توافق Vite 7 الموجود أصلاً في مشروع Motion Canvas المحلي؛ أول تحميل استخدم اعتماداً مؤقتاً قديماً من Vite وأظهر 504، وبعد إعادة التحميل اشتغل المحرر وبدأ الرندر.
- `src/motion-kit.ts` يحدد إعدادات الظهور/الخروج والتأخير والرسم والتقريب/الانتقال الجانبي والـparallax ونوع الانتقال لكل درجة. `src/scene.tsx` يربطها بافتتاحية وشرح ومقارنة وخاتمة. النص يظهر كعقدة كاملة، بدون تحريك الحروف العربية منفردة. النص العربي المستخدم بلا تشكيل أصلاً. لم أبدّل المحرك ولم أربطه بمسار الإنتاج.
- من Motion Canvas صدّرت ستة تسلسلات PNG منفصلة `groupByScene` إلى `motion-canvas/output/project/{calm-ar,calm-en,medium-ar,medium-en,active-ar,active-en}/`. الأعداد: 516، 516، 374، 374، 280، 281 إطاراً (2341 إجمالي). الرندر استغرق قرابة 26 ثانية بحسب شاشة المحرر (23 ثانية ظاهرة مع ETA ثلاث ثوانٍ قبل الاكتمال). ذروة ذاكرة عملية المحرر لم تُقَس.
- ملفات الفيديو الجديدة وقياسات FFprobe/Ffmeg في مجلد مستقل لكل فيديو:
  - `lab/evidence/motion-canvas-motion-levels-TEST_ONLY/calm-ar-TEST_ONLY/motion-canvas-calm-ar-TEST_ONLY.mp4`
  - `lab/evidence/motion-canvas-motion-levels-TEST_ONLY/calm-en-TEST_ONLY/motion-canvas-calm-en-TEST_ONLY.mp4`
  - `lab/evidence/motion-canvas-motion-levels-TEST_ONLY/medium-ar-TEST_ONLY/motion-canvas-medium-ar-TEST_ONLY.mp4`
  - `lab/evidence/motion-canvas-motion-levels-TEST_ONLY/medium-en-TEST_ONLY/motion-canvas-medium-en-TEST_ONLY.mp4`
  - `lab/evidence/motion-canvas-motion-levels-TEST_ONLY/active-ar-TEST_ONLY/motion-canvas-active-ar-TEST_ONLY.mp4`
  - `lab/evidence/motion-canvas-motion-levels-TEST_ONLY/active-en-TEST_ONLY/motion-canvas-active-en-TEST_ONLY.mp4`
- كل المقاطع H.264، `1080×1920`, 24fps، بلا صوت، وفك كاملها نجح. مددها 21.500s للهادئة، 15.583s للمتوسطة، و11.667s للعربية النشطة / 11.708s للإنكليزية النشطة. أحجامها على الترتيب `544488`, `592535`, `583476`, `656756`, `540290`, `604304` بايت. التقرير: `lab/evidence/motion-canvas-motion-levels-TEST_ONLY/motion-canvas-motion-levels-checks-TEST_ONLY.md`. ملفات JSON لكل `ffprobe` ونتيجة فك الترميز بجانب كل فيديو. أسماء الستة كلها موسومة `TEST_ONLY`.
- ترميز FFmpeg المقاس بـ`/usr/bin/time -l` استغرق لكل ملف 0.72–1.23 ثانية (مجموع 5.49s)، والذروة القصوى المقاسة للتشفير 1.10–1.13 GiB RSS. هذه ذاكرة FFmpeg وقت التشفير، مو قياس ذاكرة Motion Canvas أثناء الرندر.
- شغّلت التسلسل الكامل في محرر Motion Canvas بوضوح `24 FPS` وشاهدت دورته المتواصلة التي تضم المشاهد الستة؛ تنقلت العربية والإنكليزية بين الافتتاحية والشرح والمقارنة والخاتمة. التسلسل الكلي 1:37.5، والمراجعة كانت بسرعة 2x. هذا يؤكد أن التشغيل تحرك عبر المقاطع، لكنه مو درجة بشرية للسلاسة أو الذوق. contact sheets مأخوذة من بدايات ووسط ونهايات المقاطع: `motion-levels-ar-contact-sheet-TEST_ONLY.png` و`motion-levels-en-contact-sheet-TEST_ONLY.png`.
- قائمة التقييم محفوظة في `lab/evidence/motion-canvas-motion-levels-TEST_ONLY/human-review-TEST_ONLY.md`، وكل معيار «بانتظار مراجعة المستخدم». الصورة الثابتة لا تبيّن الفرق الزمني بين المستويات؛ للمقارنة شغّل الملفات نفسها. الفروق المعلنة في الإعدادات: `calm` ظهور fade وانتقالات dissolve/soft-rise؛ `medium` rise مع push/wipe؛ `active` slide مع zoom/push/wipe. المدد الأقصر للنشطة تعني إيقاعاً أسرع، والحكم على ملاءمته متروك للمستخدم.
- أوامر الإعادة والتحقق:

```sh
cd lab/evidence/motion-canvas-motion-levels-TEST_ONLY/motion-canvas
./node_modules/.bin/tsc --noEmit -p tsconfig.json
./node_modules/.bin/vite build
npm run start -- --port 4175
```

افتح `http://127.0.0.1:4175/`، اضغط `RENDER` بعد التأكد أن مجلدات output جديدة أو استخدم مجلداً جديداً، ثم شفّر تسلسل كل مشهد بالأمر الآتي من مجلد المشروع:

```sh
ffmpeg -framerate 24 -i output/project/<scene>/%06d.png -an -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart <new-TEST_ONLY.mp4>
ffprobe -v error -show_entries format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate,avg_frame_rate,nb_frames,pix_fmt -of json <new-TEST_ONLY.mp4>
ffmpeg -v error -i <new-TEST_ONLY.mp4> -f null -
```

- الوضع الحالي: لا commit إلى أن يختار المستخدم المستوى. لا توجد موافقة مسجلة على الجودة أو الحقوق أو الاستخدام التجاري أو التصدير والنشر. الخطوة المعلقة: افتح Contact sheets ثم شغّل المقاطع الستة، ودوّن أي مستوى تفضله أو ملاحظات الإيقاع والتنوع وقراءة العربي/الإنكليزي في قائمة `human-review-TEST_ONLY.md`. أبقِ كل شيء محلياً وموسوماً `TEST_ONLY`.

## استئناف 2026-11-18: اختيار موشن بحسب معنى المشهد

- بدأت من `main` عند `69157419920f5fac8d2e018ff499d8945d29d58c`. تعليمات `AGENTS.md` تقول اقرأ هذا الملف أولاً، واستخدم الموجود، واختبر وسجّل قبل commit. بقيت تغييرات Git التي كانت موجودة مسبقاً في `README.md` و`lab/motion.mjs` وأدوات الحزمة و`HANDOFF.md` دون استبدال أو إعادة ضبط. لم أعمل commit لأن المستخدم طلب مراجعة المعاينات أولاً.
- راجعت مخرجات مستويات الحركة السابقة وملفات Motion Canvas الحالي. الفجوة كانت اختيار حركات متقاربة تختلف غالباً بسرعة/مدة. التجربة الجديدة معزولة على Motion Canvas `3.17.2` المثبت، من دون تبديل المحرك أو تثبيت Remotion أو تنزيل حزم/أصول من المستودعات. كشف تدقيق الكود أن النسخة الأولى كانت تعيّن الحركة مسبقاً؛ لذلك أضفت قياساً قواعدياً من قائمة مرشحين حسب الدور وكلمات المعنى والتكوين والعنوان، وربطت معرّف الحركة المختارة بفروع الرندر. المقيّم محدود بهذه المفردات وليس فهماً لغوياً عاماً.
- التقرير التفصيلي، التراخيص، سجل الاختيار والدرجات والقياسات والقيود: `docs/MOTION_CONTENT_SELECTION_TEST_ONLY.md`. قائمة الدرجات البشرية: `lab/evidence/motion-content-selection-TEST_ONLY/human-review-TEST_ONLY.md` (كلها «بانتظار مراجعة المستخدم»). ناتج المقيّم: `lab/evidence/motion-content-selection-TEST_ONLY/motion-selection-rules-TEST_ONLY.json`. بقي ملف `motion-selection-TEST_ONLY.json` والمخرجات الأولية محفوظة للمقارنة.
- أُنتجت 4 معاينات أحدث غير مستبدلة: `lab/evidence/motion-content-selection-TEST_ONLY/renders-rules-TEST_ONLY/{concept-ar-white-rules-TEST_ONLY.mp4,concept-en-white-rules-TEST_ONLY.mp4,signals-ar-white-rules-TEST_ONLY.mp4,signals-en-white-rules-TEST_ONLY.mp4}`. أوراق المشاهد: `lab/evidence/motion-content-selection-TEST_ONLY/scene-contact-sheets-rules-TEST_ONLY/` (أربع ملفات لغة/موضوع). كل المخرجات محفوظة تحت `lab/evidence/` ومستثناة من Git.
- الاختيار القواعدي الناتج: `concept` افتتاحية `focal-aperture-reveal`، شرح `causal-curve-trace`، مقارنة `single-to-sequence-match`، وخاتمة `idea-line-carry`. `signals`: `signal-constellation-gather`، رسم اتجاه `trend-curve-build`، مقارنة `point-versus-trend-focus`، وخاتمة `pattern-to-thesis-carry`. لكل حركة انتقال ووتيرة وسبب ومصدر وتكييف موثق. AR وEN ينتجان اختياراً متطابقاً للمعنى نفسه.
- المستودعات الخارجية كانت مصادر أفكار فقط: أمثلة Motion Canvas MIT؛ Opus Motion Library MIT؛ RenderComp MIT للقوالب لكن Remotion بمحركه وترخيصه المنفصل؛ GTKottman MIT لكن مكوناته تعتمد Remotion. لم تُنسخ ملفات منها. راجع روابط وcommits وتواريخ الفحص في التقرير. لا اعتماد تجاري للمكونات بعد؛ الاعتماد على المكتبات كاملة غير مبرر حالياً.
- الفحوص الفعلية للنسخة القواعدية: `tsc --noEmit -p tsconfig.json` و`vite build` PASS (858 modules، نحو 1.10s)، JSON للمقيّم و`node --check` PASS. FFprobe أكد لكل MP4 H.264 بدقة `1080×1920` و`24fps` وبلا صوت: 226/226/239/240 إطاراً، ومدد `9.4167/9.4167/9.9583/10.000s`. فك الترميز الكامل بـ`ffmpeg -v error -i <video> -f null -` نجح للأربعة. الأسماء موسومة TEST_ONLY.
- شُغّل المحرر المحلي `http://127.0.0.1:4177/` وشوهد عند 24fps يتقدم إلى 733/930 إطاراً ثم يكمل ويلف إلى 144؛ التشغيل متصل على تسلسل 38.75 ثانية، وليس حكماً بشرياً على الذوق. `/usr/bin/time -l` لترميز FFmpeg بالتتابع سجل 0.62–0.73s لكل ملف، وذروة RSS 1,147,781,120–1,181,958,144 bytes وuser CPU 4.03–4.29s. لا قياس لذاكرة/زمن Motion Canvas أثناء تكوين الإطارات.
- الملاحظات الأولية: العربية متصلة كعقدة RTL، ولا يظهر قص في اللقطات الثابتة بالحجم الكامل؛ يلزم فحص القراءة على الهاتف من المستخدم. افتتاح `signals` لا يُظهر تجمّع كل النقاط بوضوح في اللقطة المختارة، ودائرته الخلفية مقصوصة طرفياً؛ سجّلتها عيباً بصرياً محتملاً. جسر الانتقال قد يظهر لوحتين جزئيتين. لا صوت ولا بيانات حقيقية ولا نشر. الجودة والحقوق والتصدير والنشر تبقى مغلقة.
- الخطوة المعلقة: المستخدم يشاهد MP4 الأربعة داخل `renders-rules-TEST_ONLY/` وأوراق المشاهد الأربعة داخل `scene-contact-sheets-rules-TEST_ONLY/`، ويسجل التفضيل/الملاحظات في `human-review-TEST_ONLY.md`. افتح الملفات بمشغل محلي أو المحرر على `http://127.0.0.1:4177/`. عيب افتتاح `signals` ما زال ظاهراً: بعض النقاط مفقودة من اللقطة الثابتة والدائرة الخلفية مقصوصة الطرف؛ راجعه قبل قرار الدمج. بعد التقييم فقط تتحدد الجولة التالية؛ لا تعمل commit حتى ذلك الحين.

## استئناف 2026-11-18: إصلاح تغطية انتقالات Motion Canvas

- بدأت من `main` عند `6915741`، وقرأت تعليمات `AGENTS.md` و`HANDOFF.md`. بقيت تعديلات المستخدم السابقة في README وأدوات الحزمة والتقرير كما هي؛ لم ألمس StageCore أو Kids Studio، ولم أشغّل n8n أو أنشر شيئاً. ماكو commit جديد بناءً على طلب المستخدم.
- أظهر فحص إطارات الرندر السابق أن اللوحة الداخلة كانت تكشف الخلفية خارج حدودها أثناء الانتقال. تجربة المزج المباشر مع إعادة الكاميرا `motion-canvas-transition-repair-TEST_ONLY/` ما حققت الشرط، لذلك أبقيتها كدليل فشل ولم أستبدلها.
- التشخيص: الكاميرا المشتركة تحتفظ بتحويلات المشهد السابق عند حد الانتقال، والمزج المتزامن يخفّض اللوحة القديمة قبل ما تغطي الجديدة الإطار. في نسخة معزولة جديدة عدّلت `passTransition` فقط: إعادة الكاميرا لوضعها الافتراضي عند الحد، تثبيت اللوحتين على `[0,0]` وبحجم `[1080,1920]` و`scale=1` و`rotation=0`، إبقاء القديمة معتمة إلى أن تصل الجديدة للحجم/الموضع الكامل، واستخدام خط/حلقة الجسر كطبقة انتقال فقط. محتوى ومكونات وحركة المشاهد الداخلية ما تغيّرت. ماكو قناع يغيّر حجم مجموعة المشهد.
- النسخة الجديدة: `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-transition-overlay-repair-TEST_ONLY/`؛ المعاينات المشفّرة: `lab/evidence/motion-content-selection-TEST_ONLY/renders-transition-overlay-repair-TEST_ONLY/`. الملفات الأربعة `concept-ar-transition-overlay-repair-TEST_ONLY.mp4`, `concept-en-transition-overlay-repair-TEST_ONLY.mp4`, `signals-ar-transition-overlay-repair-TEST_ONLY.mp4`, `signals-en-transition-overlay-repair-TEST_ONLY.mp4`.
- أوراق إطارات الحد (قبل/أثناء/بعد لكل انتقال، لكل لغة): `lab/evidence/motion-content-selection-TEST_ONLY/transition-review-repair-TEST_ONLY/{concept-ar,concept-en,signals-ar,signals-en}-boundary-frames-v2-TEST_ONLY.png`. أرقام الإطارات المشتركة بين لغتي كل موضوع: `concept` (26/32/40)، (91/109/117)، (157/163/171)؛ `signals` (24/32/40)، (101/109/117)، (157/165/173). بمراجعة الإطارات يظهر كشف اتجاهي مقصود: الجزء الذي يدخل من اللوحة الجديدة يحل محل القديمة، والجزء غير المكشوف يبقى من اللوحة القديمة؛ ما ظهرت مساحة من خلفية الجذر أو نهاية ناقصة. هذا قص انتقالي عند حافة العرض، وليس تصغيراً أو قناعاً على المشهد. أرقام AFTER مختارة بعد اكتمال التغطية.
- اختبار التشغيل المحلي المتصل على `http://127.0.0.1:4180/`: شغّلت تسلسل Motion Canvas كامل (886 إطاراً، `1080×1920`, 24fps، قرابة 36.92s)، وتابعت وصوله لنهاية التسلسل ثم دورانه للبداية؛ الواجهة عرضت `24 FPS`. مشاهدة التشغيل المتصل أُجريت على التسلسل المركّب، بالإضافة لمراجعة أوراق حدود الانتقالات؛ هذا لا يمنح موافقة جودة أو ذوق.
- الفحوص: `./node_modules/.bin/tsc --noEmit -p tsconfig.json` PASS؛ `./node_modules/.bin/vite build` PASS (858 modules، نحو ثانية). حُوّلت الصور بـ`ffmpeg` إلى MP4 H.264؛ `ffprobe` أكد `1080×1920`, 24fps، بلا audio stream، ومدد/إطارات `concept` 9.1667s/220، `signals-ar` 9.2917s/223، `signals-en` 9.3333s/224. `ffmpeg -v error -i <file> -f null -` نجح للأربعة. الأسماء والمجلدات كلها `TEST_ONLY`، والمخرجات القديمة محفوظة.
- خطوات الإعادة: افتح MP4 بـ`open lab/evidence/motion-content-selection-TEST_ONLY/renders-transition-overlay-repair-TEST_ONLY/concept-ar-transition-overlay-repair-TEST_ONLY.mp4` (بدّل اسم اللغة/الموضوع لبقية الملفات). لإعادة بناء الصور افتح `http://127.0.0.1:4180/` واضغط `RENDER` بعد التأكد أن `output/project/` لم يعد مستخدماً لمخرجات سابقة؛ لتشفير sequence:

```sh
ffmpeg -framerate 24 -start_number 0 -i output/project/<scene>/%06d.png -c:v libx264 -crf 18 -pix_fmt yuv420p -an <new-TEST_ONLY.mp4>
ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate,nb_frames -show_entries format=duration,size -of default=noprint_wrappers=1 <new-TEST_ONLY.mp4>
```

- المطلوب من المستخدم: مراجعة الفيديوهات والانتقالات بصرياً، خصوصاً هل حركة الكشف مقبولة أم يفضّل انتقالاً مختلفاً. لا اعتماد إنتاج ولا فتح بوابات الحقوق أو الجودة أو التصدير. لا commit حتى تكتمل هذه المراجعة؛ بعد ذلك تُدمج آلية الانتقال المطلوبة بالمصدر القابل لإعادة الاستخدام إن وافق المستخدم.

## استئناف 2026-11-18: إزالة القوس العابر من الانتقال

- بدأت من `main` وHEAD `6915741`، وراجعت `AGENTS.md` و`HANDOFF.md` وحالة الملفات. لا commit ولا دمج بالمصدر بناءً على طلب المستخدم؛ أبقيت مخرجات انتقال التغطية السابقة ونسخ التجارب السابقة بلا تغيير.
- مصدر القوس الأصفر هو `Line ref={bridge}` الموضوع خارج لوحات المشهد داخل `<Camera>`، وليس رسماً من المشاهد: `passTransition` كان يغيّر نقاطه إلى Bézier أو دائرة، ثم يحرّك `end`/`scale`/`opacity`. لذلك كان يظهر أثناء الانتقال فقط فوق اللوحتين.
- أنشأت نسخة معزولة جديدة `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-transition-clean-TEST_ONLY/`. حذفت عنصر `bridge` وتعريفه وحركاته وتمريره إلى `passTransition` فقط. بقي كشف اللوحة الجديدة فوق القديمة، الاتجاهات والمدة كما هي، والكاميرا/أبعاد/مقياس/تدوير اللوحتين كما بالإصلاح المقبول السابق. احتُفظ بوقت الانتقال الإضافي نفسه بـ`waitFor` دون رسم عنصر زخرفي. محتوى المشاهد ورسمها وحركتها لم يتغير.
- صدّرت أربع معاينات جديدة إلى `lab/evidence/motion-content-selection-TEST_ONLY/renders-transition-clean-TEST_ONLY/`: `concept-ar-transition-clean-TEST_ONLY.mp4`, `concept-en-transition-clean-TEST_ONLY.mp4`, `signals-ar-transition-clean-TEST_ONLY.mp4`, `signals-en-transition-clean-TEST_ONLY.mp4`. ما استبدلت أي فيديو سابق.
- راجعت قبل/أثناء/بعد كل انتقال في كل لغة داخل `lab/evidence/motion-content-selection-TEST_ONLY/transition-review-clean-TEST_ONLY/{concept-ar,concept-en,signals-ar,signals-en}-boundary-frames-TEST_ONLY.png`. الإطارات المختارة: `concept` (26/32/40)، (96/104/116)، (152/156/164)؛ `signals` (24/32/40)، (96/104/120)، (160/164/168). خط/قوس الجسر غير موجود في المشاهد أثناء الكشف الجديد. أي خط آخر ظاهر أثناء حد الانتقال تابع للرسم الموجود فعلياً في اللوحة القديمة/الجديدة، مثل مسار مخطط `signals`، وتظهر مطابقته في الإطار قبل/بعد؛ ما أزلت شيئاً من المشاهد.
- الفحوص: `./node_modules/.bin/tsc --noEmit -p tsconfig.json` PASS؛ `./node_modules/.bin/vite build` PASS (858 modules، قرابة ثانية). `ffprobe` لكل فيديو: H.264، `1080×1920`, 24fps، بلا صوت؛ `concept` 215 إطاراً/8.9583s، `signals-ar` 223/9.2917s، `signals-en` 224/9.3333s. فك الترميز الكامل `ffmpeg -v error -i <file> -f null -` نجح للأربعة. المخرجات كلها محلية وموسومة `TEST_ONLY`.
- الأمر التالي للمراجعة: `open lab/evidence/motion-content-selection-TEST_ONLY/renders-transition-clean-TEST_ONLY/concept-ar-transition-clean-TEST_ONLY.mp4` (بدّل الاسم لبقية المقاطع). قارِن خصوصاً إطارات `during` في أوراق الحدود مع نسخة `transition-overlay-repair-TEST_ONLY`. مطلوب تقييم المستخدم، لذلك تظل النسخة الجديدة اختبارية ولا تعديل خارج مجلد evidence ولا commit.

## استئناف 2026-11-18: تدقيق حدود المشهد أثناء الانتقال

- بدأت من `main` عند `6915741`؛ راجعت `AGENTS.md` و`HANDOFF.md` وسجل المعاينات. أبقيت جميع تغييرات Git الموجودة قبل هذه الدفعة كما هي (`HANDOFF.md`, `README.md`, `lab/motion.mjs`, أدوات الحزمة، والتقرير غير المتعقب). لا commit ولا دمج بالمصدر القابل لإعادة الاستخدام، حسب طلب المستخدم. ما لمست StageCore أو Kids Studio.
- فحصت `src/video-scene.tsx` والـ`project.meta` في Motion Canvas `3.17.2`. السبب العام الذي وجدته: اللوحات الأربع كانت `Rect` بحجم كامل لكن من دون قصّ لأبنائها؛ أي رسم يتجاوز حدود لوحته يبقى تحت Camera ويُقص عند جذر المشهد/حافة الشاشة أثناء انتقال اللوحة. لذلك أضفت في نسخة TEST_ONLY فقط `clip={true}` إلى كل لوحات `Rect` القائمة ذات `1080×1920`. هذا يقيّد رسم الأبناء بمسار اللوحة الكامل، ولا يغيّر حجمها أو مركزها أو المقياس/التدوير، ويحافظ على اللوحة الداخلة فوق القديمة، والقديمة معتمة أسفلها، وإزالة `bridge` السابقة. لم أغيّر محتوى أي شكل أو نص.
- النسخة التشخيصية المعزولة: `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-transition-panel-clip-TEST_ONLY/`; المدخلات الناتجة من Motion Canvas في `output/project/`. فحص `node audit-panel-clip-TEST_ONLY.mjs` PASS: أربع لوحات محددة بالحجم نفسه، قص محلي لكل لوحة، ترتيب/تحويل الانتقال ثابت، و`bridge` غير موجود. ترميز الفيديو الكامل مع FFmpeg ثم `ffprobe` أكد H.264 و`1080×1920` و`24/1` وبلا صوت، الأعداد 215/215/223/224 إطاراً؛ فك الترميز PASS لكل فيديو.
- الفيديوهات الجديدة: `lab/evidence/motion-content-selection-TEST_ONLY/renders-transition-panel-clip-TEST_ONLY/{concept-ar,concept-en,signals-ar,signals-en}-transition-panel-clip-TEST_ONLY.mp4`. أحجامها بالبايت: 327258، 373719، 281421، 350652. القياسات المفصلة في `lab/evidence/motion-content-selection-TEST_ONLY/transition-review-panel-clip-v2-TEST_ONLY/technical-checks-panel-clip-v2-TEST_ONLY.json`.
- أوراق الإطارات الصحيحة: `lab/evidence/motion-content-selection-TEST_ONLY/transition-review-panel-clip-v2-TEST_ONLY/{concept-ar,concept-en,signals-ar,signals-en}-boundary-frames-panel-clip-v2-TEST_ONLY.png`. كل ورقة فيها ثلاثيات قبل/أثناء/بعد للانتقالات الثلاثة. إطارات `concept`: (26/32/40)، (96/104/116)، (152/156/164)؛ `signals`: (24/32/40)، (96/104/120)، (160/164/168). فحصت الصور بصرياً: ماكو gap من خلفية الجذر ولا عنصر bridge عابر؛ الدوائر والمسارات والنصوص نفسها ما زالت في طبقاتها. **حد الكشف المتحرك يحجب جزءاً من عناصر اللوحة عند مروره فوقها**؛ هذا سلوك التغطية المكانية، وليس تجاوزاً لحدود لوحة المشهد. الـclip يعالج خروج الرسم عن حد اللوحة، لكنه لا يجعل كل عنصر ظاهراً كاملاً خلال مرور حد الانتقال.
- شغّلت معاينة Motion Canvas باستمرار عند Preview `0.5x` و`24fps` عبر خط المشاهد الأربعة. قارنت ذلك بإطارات الرندر النهائي Full `1.0x` بالحجم `1080×1920`. قائمة مراجعة المستخدم محدّثة في `lab/evidence/motion-content-selection-TEST_ONLY/human-review-TEST_ONLY.md`؛ كل القيم بانتظار رأيه ولا توجد موافقة جودة.
- تجربة بديلة سريعة للعتامة الكاملة على Shape/حاوية `Layout` ظلت معزولة في مجلدات `motion-canvas-transition-composite-TEST_ONLY/`, `motion-canvas-transition-composite-v2-TEST_ONLY/`, `motion-canvas-transition-layout-clip-v3-TEST_ONLY/`, `motion-canvas-transition-layout-clip-v4-TEST_ONLY/`. رصدت بالصور أن أبعاد الـLayout/Cache تتبع مقياس معاينة المحرر وتنتج مساحة ربع إطار، لذلك لم أعتمدها ولم أعدّلها في المصدر. ملفا Contact Sheet الفاشلان من المحاولة الأولى محفوظان في `transition-review-panel-clip-TEST_ONLY/`؛ المعتمد للمراجعة هو مجلد `...panel-clip-v2...` لأن الصور فيه مضمّنة فعلياً.
- إعادة التشغيل بعد الرجوع للمراجعة: افتح فيديو `concept-ar-transition-panel-clip-TEST_ONLY.mp4` محلياً (أو بقية الملفات)، ثم راجع PNGs في `transition-review-panel-clip-v2-TEST_ONLY/`. لإعادة إنشاء التسلسلات تحتاج Motion Canvas UI على `http://127.0.0.1:4182/` من مجلد النسخة المعزولة ثم `RENDER`، مع مجلد إخراج جديد؛ للتحقق شغّل `node audit-panel-clip-TEST_ONLY.mjs`, `npx tsc --noEmit`, و`python3 review-transition-panel-clip-TEST_ONLY.py` من مجلد النسخة. لا تشغّل الرندر فوق مجلد مخرجات موجود.
- الخطوة المعلقة: المستخدم يراجع أوراق `DURING` خصوصاً حواف الدوائر والأقواس والنص. إذا كان المقصود منع أي شكل من أن يصبح جزئياً أثناء حركة الكشف، فهذا يتطلب تغيير نوع الانتقال نفسه (مثلاً قطع لحظي أو مزج كامل الإطار)، لأن كل كشف مكاني يحجب الشكل عندما تعبر حافته؛ لم أستبدل الانتقال بهذا القرار ولم أدمج أي تعديل. Commit يظل مؤجلاً حتى المراجعة.


## استئناف 2026-11-18: مراجعة بصرية شاملة للخطوط والمسارات والانتقالات

- بدأت من `main` وHEAD الفعلي `6915741`. راجعت `AGENTS.md` و`HANDOFF.md` وأوراق v3 الموجودة. بقيت تغييرات المستخدم السابقة كما كانت؛ لم أعدّلها، ولم أعمل commit أو دمج. كل النسخ الجديدة داخل `lab/evidence/` والمعاينات موسومة `TEST_ONLY`.
- أسباب العيوب التي ثبتت: النقاط كانت تملك إحداثيات/توقيتاً منفصلاً عن الخط؛ هالة افتتاح `signals` تجاوزت الحد الأيسر؛ خطوط النظام السابقة Geeza Pro/Arial بسيطة وغير متناسقة؛ وحد الكشف المكاني يقصّ العناصر التي تعبره. الخط والمسار صارا يستخدمان نقاط Bézier وتقدماً واحداً، والهالة صارت داخل viewport.
- استخدمت الخطوط الموجودة محلياً: Cairo للعربية وPoppins للاتينية (SIL OFL 1.1 حسب [Cairo OFL](https://github.com/google/fonts/blob/main/ofl/cairo/OFL.txt) و[Poppins OFL](https://github.com/google/fonts/blob/main/ofl/poppins/OFL.txt)). لم أنزّل الخطوط ولم أضف ملفاتها للمستودع.
- اختبرت حلول انتقال معزولة متتابعة `v4` إلى `v7`: فصل مجموعة المحتوى، إخفاء المحتوى أثناء كشف الخلفية، ترتيب طبقات `zIndex` صريح، وأخيراً إزالة `clip` من مستطيلات الخلفيات الصلبة فقط مع إبقاء طبقات المحتوى ثابتة ومقصوصة على إطار `1080×1920`. انتقال الغطاء نفسه لم يتغير. `v7` أفضل في عينات `signals`، لكن لم ينهِ المشكلة بكل المشاهد: ورقتا `concept-ar` و`concept-en` تعرضان جزءاً من عنوان الخاتمة عند الإطار 162، ثم يظهر العنوان كاملاً عند 168. لذلك تبقى صلاحية الانتقال الثالث لموضوع `concept` غير محسومة ولا أوصي بدمج أي تغيير للمصدر.
- النسخة المعزولة الأخيرة: `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-audit-v7-TEST_ONLY/`. المصدر التجريبي فقط: `src/video-scene.tsx`. الأوراق الأربع في `visual-review-v7-TEST_ONLY/`، وقائمة المراجعة `human-review-TEST_ONLY.md` والتقرير الموحّد `visual-audit-report-TEST_ONLY.md`. نتائج الفحص التقني في `technical-checks-v7-TEST_ONLY.json`.
- فيديوهات v7: `renders-visual-audit-v7-TEST_ONLY/concept-ar-visual-audit-v7-TEST_ONLY.mp4`، `concept-en-visual-audit-v7-TEST_ONLY.mp4`، `signals-ar-visual-audit-v7-TEST_ONLY.mp4`، `signals-en-visual-audit-v7-TEST_ONLY.mp4`. كلها H.264، `1080×1920`, `24fps`, بلا صوت، فك الترميز بـFFmpeg ناجح، والأسماء موسومة `TEST_ONLY`. سجّل FFprobe العدد والمدة والحجم في JSON.
- الفحوص الفعلية: `tsc --noEmit` PASS، `vite build` PASS (858 modules)، `node audit-visual-geometry-TEST_ONLY.mjs` PASS (`18/18`)، `python3 build-visual-review-TEST_ONLY.py` PASS، `ffprobe` و`ffmpeg -v error -i <file> -f null -` PASS لكل فيديو. ترميز FFmpeg بين 0.61–0.72 ثانية للفيديو؛ ذروة RSS للترميز فقط 1.15–1.16 GB، ولا تشمل ذاكرة Motion Canvas.
- تم تشغيل ملفات v3 السابقة الأربعة حتى نهايتها في QuickTime؛ لم أسجل تقييماً للحركة، ولم أشاهد v7 المتصل بعد. مراجعة v7 الحالية مبنية على أوراق إطارات، وبالتالي سلاسة v7 ما زالت بانتظار التشغيل/التقييم البشري. كل بنود الذوق والقراءة والجودة بانتظار المستخدم.
- **أول خطوة معلّقة:** دقّق `concept-ar` و`concept-en` إطارياً من 156 إلى 170، واعرف هل القصّ بسبب حافة الكشف أم ترتيب/توقيت طبقة الخاتمة. لا تعدّل المصدر القابل لإعادة الاستخدام ولا تدمج، ولا تفتح بوابات الحقوق أو الجودة أو التصدير أو النشر. أمر فتح الورقة: `open lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-audit-v7-TEST_ONLY/visual-review-v7-TEST_ONLY/concept-ar-visual-audit-v7-TEST_ONLY.png`. لتشغيل فيديوها محلياً: `open lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-audit-v7-TEST_ONLY/renders-visual-audit-v7-TEST_ONLY/concept-ar-visual-audit-v7-TEST_ONLY.mp4`.


## استئناف 2026-11-18: مراجعة الحركة وإكمال اختبار الاستعادة المحلي

- بدأت من `main` عند `6915741`؛ احتفظت بكل التغييرات غير المحفوظة الموجودة مسبقاً. لم أعمل commit أو push أو أدمج الحركة بالمصدر. قرأت `AGENTS.md` و`HANDOFF.md` والخارطة، وتحققت من المخرجات الحالية. n8n بقي متوقفاً (لا يوجد listener على `127.0.0.1:5678`).
- أكملت الجولة المعزولة `motion-canvas-visual-system-v9-TEST_ONLY`: السبب الجذري لقص عنوان خاتمة concept كان عرضه أثناء عبور حد الكشف؛ أخفي المحتوى الأمامي حتى تستقر لوحة السلايد، مع إبقاء كشف السلايد الجديد فوق القديم. سبب حواف الخلفية كان سطح جذر ثابتاً بلون مختلف ينكشف عند camera pan؛ صار سطح bleed يتبع لون المشهد بلا توسيع viewport. لم تُحذف عناصر. مسار Bézier والنقاط يستخدمان مرجعاً هندسياً وتقدماً واحداً. الخطان المحليان Cairo/Poppins مرخصان SIL OFL 1.1 حسب مصدري Google Fonts الرسميين؛ لم أضف أو أنزّل خطوطاً.
- أُنتجت أربع معاينات `TEST_ONLY` AR/EN لمشاهد `concept` و`signals`، وأربع أوراق إطارات `visual-review-v9b-TEST_ONLY/`. إطارات transition 1/2/3 لكل مشهد تعرض قبل/أثناء/بعد. فحص الأوراق بصرياً أكد اكتمال عنوان الختام بعد الانتقال، سلامة RTL الظاهرة، وتطابق المسار والنقطة؛ التشغيل المتصل والسلاسة والجمال وقراءة الهاتف ما زالت تنتظر المستخدم. قائمة `human-review-TEST_ONLY.md` كلها بانتظار تقييمه. التفاصيل، المسارات والأحجام في [`docs/MOTION_VISUAL_SYSTEM_REVIEW_V9_TEST_ONLY.md`](docs/MOTION_VISUAL_SYSTEM_REVIEW_V9_TEST_ONLY.md).
- الفحوص: TypeScript/Vite build PASS (858 modules)، `node audit-visual-system-v9-TEST_ONLY.mjs` PASS 13/13، و`python3 check-videos-v9-TEST_ONLY.py` PASS للأربعة: H.264، 1080×1920، 24fps، فك كامل، بلا صوت. تحقق 2,460 زاوية إطار مستقرة؛ ما ظهر لون جذر أو حافة مكشوفة، وتجاوز المسارات/النقاط 0px. لا اعتبار لهذا اعتماداً بصرياً بشرياً. ترميز FFmpeg 0.52–0.56s لكل ملف وRSS الذروة للمرمّز قرابة 1.03GB؛ لا يقيس ذاكرة Motion Canvas.
- بعد تجهيز المعاينات واصلت أعلى خطوة محلية قابلة للتنفيذ من خارطة Day 3: اختبار استعادة مخرجات المصنع. أضفت `tools/test_content_package_recovery.py`؛ يرندر حزمة TEST_ONLY ذات 5 ثوانٍ، ينشئ `tar.gz`، يستعيد إلى مسار جديد، يقارن قائمة الملفات والأحجام وSHA-256، ثم يعيد QA وFFprobe. تشغيل ناجح: `python3 tools/test_content_package_recovery.py --run-name content-package-recovery-v2-2026-11-18-TEST_ONLY`. نتج 31 ملفاً في حزمة حجمها 1,857,571 بايت؛ hashes متطابقة؛ فحوص الأصل والاستعادة 7/7 متطابقة، وفيديو AR/EN كل منهما 120 إطاراً/5s/بلا صوت. النشر والصوت والأسرار وn8n غير مشمولة.
- محاولة أولى محفوظة باسم `content-package-recovery-2026-11-18-TEST_ONLY` استخدمت معاينة ثانية واحدة وفشلت لأن المراجع الموجود يفرض عقد 5 ثوانٍ؛ قُيّد خيار الأداة إلى 5، وأعيد الاختبار في مجلد `v2` الجديد ونجح. لم تُحذف مخرجات الفشل. هذا اختبار استعادة حزمة محتوى فقط، وليس نسخة احتياطية كاملة للنظام أو قاعدة بيانات n8n؛ بقي n8n متوقفاً ولم تدخل بيانات اعتماد ضمنه.
- الفحوص الإضافية: `python3 tools/test_content_package_pipeline.py` PASS (رفض ملف/حزمة ناقصة، استئناف الانقطاع، رفض الاتجاه المتغير والكتابة فوق الموجود)، `python3 lab/test_checkpoint.py` PASS للحالات الست، `python3 -m py_compile tools/test_content_package_recovery.py` و`node --check lab/motion.mjs` PASS. لم تُستخدم شبكة أو API أو منصة ولم تضاف خدمة مدفوعة.
- **الخطوة التالية:** شغّل فيديوهات v9 الأربعة وشاهدها كاملة، ثم عبّئ `human-review-TEST_ONLY.md`. بعدها يمكن إصلاح عيب مرئي محدد أو إبقاء التغييرات تجريبية. لا تدمج الحركة ولا تفتح بوابات الجودة/الحقوق/التصدير/النشر قبل المراجعة البشرية. اختبار الاستعادة الحالي مكتمل ضمن نطاقه؛ استعادة النظام الكاملة تبقى مؤجلة حتى توجد سياسة ومصدر محلي آمن لنسخة البيانات، مع إبقاء n8n متوقفاً.

## استئناف 2026-11-22: تجهيز التطوير من جهاز آخر ورفع GitHub

- تأكدت أن المشروع هو المستودع المحلي على الفرع `main`. أخذت نسخة محلية قبل الدمج في `lab/repository/backup-before-github-merge-2026-11-22/`: Git bundle كامل للتحقق والاستعادة، patch لكل تغييرات الملفات المتعقبة، tar للملفات الجديدة، ونسخة من الحالة والسجل وفهرس ملفات `lab/evidence/` التي بقيت مكانها. تحقق `git bundle verify` بنجاح. لم تنسخ المعاينات الكبيرة إلى Git.
- كان `origin` غير مهيأ أول الجلسة. المستودع `https://github.com/ali96adil/ContentFactory` كان عاماً، فغيّرت ظهوره إلى private وتحققت منه عبر API؛ الحالة الحالية private. الـremote كان يحتوي commit ابتدائي `e0e6721` وسطر `# ContentFactory` فقط في README، وتاريخ المحلي عند `6915741` مستقل عنه. راجعت محتوى README للطرفين ثم نفذت `git merge --allow-unrelated-histories --no-commit origin/main` وعالجت add/add يدوياً: احتفظت بعنوان README البعيد وأضفت إليه محتوى المصنع المفيد وتعليمات التشغيل الحديثة. merge commit الناتج `495bee4`; والداه المحلي `6915741` والبعيد `e0e6721`. لم أستخدم rebase أو force.
- أضفت تعليمات التطوير في README على macOS/Linux، مع WSL2 كخيار Windows، نسخ الأدوات، أوامر التثبيت والفحص وتشغيل Motion Canvas والرندر. أضفت `.nvmrc` لنسخة Node `24.21.0`، وحولت المسارات الخاصة بحساب/ماك التطوير إلى مسارات نسبية في الوثائق وسجل التقييم. لا حاجة لملف `.env.example` لأن مسار الرندر الحالي لا يقرأ متغيرات بيئة.
- كان مثال الحزمة موجوداً فقط في `lab/evidence/` المستثنى من Git، وهذا يمنع الاختبار بعد clone. أضفت نسخة نصية اصطناعية خالية من المصادر والأصول والقياسات الحقيقية في `lab/fixtures/content-package-demo-TEST_ONLY.json`، وربطت اختباري pipeline/recovery بها، وجعلتهما ينشئان مجلد الأدلة عند الحاجة. حدّثت عقد الحزمة، وأضاف `.gitignore` تجاهل `lab/imports/`, `.npmrc`, مخازن الاعتماد وملفات قواعد البيانات والسجلات. `lab/evidence/` والمعاينات وقواعد البيانات والبيانات الشخصية مستثناة.
- فحص الأسرار: استخدمت Gitleaks `8.30.1` الرسمي. تحققت من SHA-256 للأصل `b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5`، ونتائج الفحص محفوظة محلياً تحت `lab/repository/secret-scan-2026-11-22/` (مستثناة من Git). فحص 56 ملفاً متعقباً في شجرة العمل: صفر اكتشافات؛ فحص تاريخ `main` ذي 17 commit: صفر اكتشافات. لم يُطبع أي secret. `lab/repository/` يحوي الأداة والتقارير الاحتياطية فقط ولا يدخل قائمة الإيداع.
- الفحوص الفعلية على ملفات الاختبار: `python3 lab/test_checkpoint.py` PASS (6 حالات)، `python3 tools/test_content_package_pipeline.py` PASS (رفض النقص، الاستئناف، منع تغيير الإعدادات والاستبدال)، و`python3 tools/test_content_package_recovery.py --run-name content-package-recovery-2026-11-22-TEST_ONLY` PASS: 31 ملفاً، archive `1,857,567` بايت، SHA-256 متطابقة واستعادة ومراجعة FFprobe متطابقتان. `(cd lab/motion-canvas && npm run build)` PASS (847 modules، 0.978s)، و`py_compile`, `node --check lab/motion.mjs`, و`git diff --check` PASS.
- ملفات الفيديو والصور/المعاينات والتقارير التشغيلية الكبيرة تبقى محلياً تحت `lab/evidence/`، وعدد ملفات evidence وقت النسخ كان 38,111؛ لم تدخل Git. بيانات الاعتماد وقاعدة n8n وNode/Python environments مستثناة كذلك. لم يجرِ اتصال منصة أو نشر. جودة الحركة تبقى بانتظار تقييم المستخدم.
- بعد `495bee4` أُعيدت تغييرات العمل المحفوظة، وREADME حُلّ يدوياً مرة ثانية ليجمع تعليمات الجهاز الآخر وملاحظات الاتجاهات المحلية. **الخطوة الحالية:** افحص staged changes، شغّل Gitleaks على الملفات المرحّلة، ثم أنشئ commit واضحاً للتغييرات المحلية وارفع `main` بـ`git push origin main` عادي. بعد الرفع تحقق أن `origin/main` يطابق HEAD ويحوي merge الأبويْن.

## تحقق ما بعد الرفع — 2026-11-22

- تم دفع commit التغييرات المحلية `8ebbbd2` إلى الريبو الخاص عبر `git push origin main` عادي بعد merge commit `495bee4`.
- بعد الرفع أُعيدت الفحوص: `python3 lab/test_checkpoint.py` PASS (6/6)، `python3 tools/test_content_package_pipeline.py` PASS، `python3 tools/test_content_package_recovery.py --run-name content-package-recovery-post-push-2026-11-22-TEST_ONLY` PASS (31 ملفاً، SHA-256 متطابقة، مراجعة الأصل/الاستعادة متطابقة)، `py_compile` PASS، `node --check lab/motion.mjs` PASS، `git diff --check` PASS، و`(cd lab/motion-canvas && npm run build)` PASS (847 modules، 0.945s).
- آخر فحص رؤية للحركة ما زال بانتظار المستخدم. فيديوهات v9 والـcontact sheets تحت `lab/evidence/motion-content-selection-TEST_ONLY/` محلية ومستثناة من Git. لا صوت أو نشر، وبوابات الحقوق والجودة والتصدير مغلقة.
- بيانات التشغيل الخاصة وقواعد البيانات والاعتمادات مستثناة؛ ملفات الأداء الحقيقية توضع في `lab/imports/` وتبقى محلية. بداية التطوير على جهاز آخر: clone الريبو الخاص، تأكد من الأدوات حسب README، ثم شغّل أوامر الفحوص الأساسية من جذر المشروع. n8n يبقى متوقفاً.

## استئناف 2026-11-24: أول CI على المستودع العام

- تحقق GitHub API من أن `ali96adil/ContentFactory` صار `public`. تم clone من `origin/main` عند `d60148c08625e88d36ec357a1621ced92a670ea8`؛ شجرة `main` كانت نظيفة. بدأ العمل على فرع محلي `codex/public-ci-baseline`.
- لم يكن بالمستودع workflow تحت `.github/workflows/`، ولم تظهر CI runs على الرأس الحالي. أضيف `.github/workflows/ci.yml` لفحوص Python والـpipeline والاستعادة وTypeScript/Vite على runner قياسي عام، بأقل صلاحيات `contents: read`، ونسخ GitHub Actions مثبتة على SHA. أدوات الوسائط تُثبت داخل container مؤقت بـUbuntu 24.04.
- نتيجة البيئة المحلية: `python3 lab/test_checkpoint.py` PASS (6 حالات)، `py_compile` و`node --check lab/motion.mjs` و`git diff --check` PASS. نجح `npm ci --legacy-peer-deps` ثم `npm run build` (847 modules؛ Vite 1.40s). التثبيت النظيف `npm ci` بلا الخيار فشل بـ`ERESOLVE`: `@motion-canvas/vite-plugin@3.17.2` يعلن Vite 4/5 بينما المشروع يستخدم Vite 7. وثّقت workaround وحدوده في README؛ ما اعتبرنا peer range محلولاً.
- تعذر تشغيل `tools/test_content_package_pipeline.py` محلياً لأن `rsvg-convert` غير موجود في بيئة Codex (FFmpeg وFFprobe موجودان). الـworkflow يثبت `librsvg2-bin` وFFmpeg لعزل هذا الاعتماد؛ يجب انتظار نتيجة GitHub Actions بعد push قبل اعتبار CI ناجحاً.
- لا يشمل هذا التغيير اعتماد جودة بشرية أو حقوق أو تصدير أو نشر؛ تبقى مراجعة حركة الفيديوهات والبيانات الفعلية والصوت العربي معلّقة كما سبق. لا تشغّل n8n؛ لا تضع مفاتيح أو بيانات شخصية في Git.
- الخطوة التالية: ارفع فرع `codex/public-ci-baseline` إلى GitHub، تأكد أن workflow ينجح على clone عام نظيف، أصلح أي مشكلة تظهر، ثم أنشئ PR للمراجعة. بعد نجاحه استمر بجلسة التطوير من الفجوات القابلة للإثبات برمجياً، وسجّل ما يتطلب بيانات/استماع/موافقة بشرية كحواجز واضحة.

## استئناف 2026-11-24: إصلاح أول فشل CI وتغطية محلل الأداء

- فحص GitHub Actions للـPR #1 أظهر أن التثبيت وتجهيز الأدوات نجحا، لكن `python lab/test_checkpoint.py` توقف قبل الاختبارات لأن صورة `ubuntu:24.04` لا تتضمن `libsqlite3.so.0` التي يحتاجها Python المجهز. أضفت `libsqlite3-0` إلى التثبيت داخل الحاوية. مصدر النتيجة: سجل job `138029732103` في run `45270792883`.
- أضفت `tools/test_analyze_platform_metrics.py`: ثلاث حالات تغطي قفل `TEST_ONLY` على `test_only_no_action` ومنع التوسع/التصدير/النشر، رفض القيم الرقمية الفارغة وغير الرقمية والسالبة وغير المنتهية، وقبول القيم المحدودة. اكتشف الاختبار أن `NaN` و`Infinity` كانت تمر من التحقق الرقمي؛ صار المحلل يرفض كل القيم غير المحدودة عبر `math.isfinite`.
- الفحوص المحلية بعد التعديل: `python3 tools/test_analyze_platform_metrics.py` PASS (3/3)، `python3 lab/test_checkpoint.py` PASS (6/6)، `python3 -m py_compile tools/analyze_platform_metrics.py tools/test_analyze_platform_metrics.py` PASS، و`git diff --check` PASS. لم يُعد تشغيل GitHub Actions على التعديل بعد؛ لذلك لا يُعلن CI ناجحاً حتى تظهر نتيجة جديدة.
- بعد رفع الإصلاح، نجح GitHub Actions على run `45271691934` والرأس `d01fda4fbca0977889a040ca8addb4b14166c001`: تجهيز Ubuntu، SQLite، فحوص Python، اختبار pipeline والاستعادة، وبناء Motion Canvas كلها PASS.
- في مراجعة مدخلات CSV، أضفت رفض الصفوف القصيرة/الزائدة، وعناوين الأعمدة المكررة، و`data_origin` الفارغ أو غير المعروف، ورسالة مفهومة لتاريخ غير ISO 8601. المصادر المعروفة هي `manual_export` و`manual_entry`؛ وتظل بيانات `synthetic`/`TEST_ONLY` محجوبة كما كانت.
- الفحوص المحلية بعد دفعة التحقق: `python3 tools/test_analyze_platform_metrics.py` PASS (5/5)، تشغيل CLI على fixture تحقق من `TEST_ONLY_SYNTHETIC` ومنع النشر وكل التوصيات `test_only_no_action` PASS، `python3 -m py_compile tools/analyze_platform_metrics.py tools/test_analyze_platform_metrics.py` PASS، و`git diff --check` PASS. لم تصل هذه الدفعة الأخيرة إلى GitHub بعد.
- الملفات المتغيرة في الدفعة التالية: `tools/analyze_platform_metrics.py`, `tools/test_analyze_platform_metrics.py`, و`HANDOFF.md`. لا بيانات أو أسرار أو اتصال منصات أو نشر. PR #1 يبقى Draft وبلا دمج.
- الخطوة التالية: ارفع دفعة التحقق إلى نفس فرع PR #1، وتأكد من نجاح CI على الرأس الجديد. بعد ذلك راجع تغطية المستودع المتبقية وواصل مهمة محلية قابلة للإثبات؛ اترك الحركة والصوت والحقوق وبيانات الأداء الحقيقية كبوابات تحتاج المدخلات/المراجعة المناسبة.

## استئناف 2026-11-24: أمر تحقق موحد قبل جولة التأهيل

- أضفت `tools/verify_repo.py` كمدخل واحد لتشغيل checkpoint، واختبارات محلل المقاييس والحزمة والاستعادة، و`py_compile` و`node --check`، ثم `npm ci --legacy-peer-deps` وبناء Motion Canvas. يفحص الأدوات المطلوبة مسبقاً، وينشئ اسماً زمنياً فريداً لأدلة الاستعادة لتفادي الكتابة فوق تجربة سابقة.
- حدّثت CI ليشغّل الأمر نفسه داخل حاوية Ubuntu بعد تثبيت FFmpeg وSQLite وlibrsvg، وحدّثت README بأمر التحقق الكامل. الهدف توحيد الفحص المحلي مع CI على أجهزة التطوير.
- الفحص المحلي حتى الآن: `python3 -m py_compile tools/verify_repo.py` PASS، و`git diff --check` PASS. محاولة `python3 tools/verify_repo.py` توقفت قبل الاختبارات بسبب غياب `rsvg-convert` في بيئة التنفيذ الحالية؛ لم أستخدم `sudo` أو أثبت حزم النظام. سيتم تشغيل التحقق الكامل على GitHub Actions حيث يثبت الـworkflow `librsvg2-bin` داخل الحاوية المؤقتة.
- لم تُرفع هذه الدفعة بعد. بعد دفعها سننتظر CI على الرأس نفسه، وإذا نجح يكون فحص القبول البرمجي الموحد مكتملاً لهذه الجولة. لا يشمل ذلك اعتماداً بشرياً للحركة/الصوت/الحقوق أو تحققاً ببيانات منصات حقيقية.
