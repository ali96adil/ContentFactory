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

الاختبار متوقف عند مصدر بيانات التدريب: لا تنزيل أو تثبيت لـNabra حتى يقدّم الناشر توثيقاً يوضح بيانات التدريب ورخصتها ومصدر التسجيل. صفحة وزن ONNX تعلن Apache-2.0، لكنها ترجع إلى نموذج Nabra الأساسي ولا تسد فجوة بيانات التدريب. ما يحتاج قراراً من المستخدم حالياً؛ إذا ظهر توثيق رسمي واضح، أعد فحص المتطلبات والأحجام أولاً، ثم ثبّت حصراً داخل `lab/voice-env` ونزّل ملف النموذج `83.2 MB` وملف الصوت اللازم فقط.

سبق أن جُرّب الأمر التالي داخل بيئة المشروع، لكنه لم يتقدم لأكثر من دقيقتين وأُوقف قبل تثبيت أي حزمة؛ لا تعاوده قبل إزالة عائق الترخيص وفحص سلوك التنزيل:

```sh
cd /Users/aliadil/Projects/ContentFactory
uv pip install --python lab/voice-env/bin/python torch==2.15.0 misaki==0.9.4 espeakng-loader==0.2.4
```

إذا انحل عائق الترخيص، ولّد عينة عربية قصيرة `TEST_ONLY` بنفس نص `Majed`، وسجّل زمن التوليد والحجم. Nabra فصحى `MSA` وصوته الوحيد موصوف في البطاقة بأنه أنثوي؛ سجّل الجندر كبيانات فقط، ولا تعتمد الصوت قبل مقارنة الاستماع والطبيعية والوضوح واللهجة.

## أوامر متابعة الموشن

تشغيل المحرر على localhost فقط:

```sh
cd /Users/aliadil/Projects/ContentFactory/lab/motion-canvas
npm run start -- --host 127.0.0.1 --port 9000 --strictPort
```

من الواجهة اضبط `1080×1920` و`24fps`، واضغط `RENDER`. تقرير الاختبارات والأوامر الكاملة: `docs/LOCAL_AUDIO_MOTION_EVALUATION.md`.
