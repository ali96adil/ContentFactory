# تسليم واستئناف مصنع المحتوى

آخر تحديث: 2026-11-17 (`Asia/Baghdad`)

## الحالة المحفوظة

- المجلد: `/Users/aliadil/Projects/ContentFactory`، الفرع `main`؛ نقطة البداية كانت commit `fd44f67`، والدفعات السابقة محفوظة حتى commit `654475b`.
- لا تغييرات خارج مجلد المشروع. لا لمس لـStageCore أو Kids Studio، ولا نشر أو رفع محتوى. ماكو أسرار مضافة.
- البيئة: macOS 27.0 / Apple Silicon M3 Max / ذاكرة 48 GB، مساحة حرة تقارب 199 GiB وقت الفحص. الأدوات الأساسية: Git 2.55.0، Node 24.21.0، Python 3.15.2، FFmpeg/FFprobe 7.1.1، librsvg/rsvg-convert 2.63.4. Python 3.12.9 موجود واستخدمته محلياً لصوت Piper. `n8n` و`espeak-ng` غير مثبتين.
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
