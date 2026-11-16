# تسليم واستئناف مصنع المحتوى

آخر تحديث: 2026-11-17 (`Asia/Baghdad`)

## الحالة المحفوظة

- المجلد: `/Users/aliadil/Projects/ContentFactory`، الفرع `main`؛ نقطة البداية كانت commit `fd44f67`، وانحفظت دفعة الاختبار في commit `0d292f3`.
- لا تغييرات خارج مجلد المشروع. لا لمس لـStageCore أو Kids Studio، ولا نشر أو رفع محتوى. ماكو أسرار مضافة.
- البيئة: macOS 27.0 / Apple Silicon M3 Max / ذاكرة 48 GB، مساحة حرة تقارب 199 GiB وقت الفحص. الأدوات الأساسية: Git 2.55.0، Node 24.21.0، Python 3.15.2، FFmpeg/FFprobe 7.1.1، librsvg/rsvg-convert 2.63.4. Python 3.12.9 موجود واستخدمته محلياً لصوت Piper. `n8n` و`espeak-ng` غير مثبتين.
- المراجع والحزمة الأصلية تبقى تحت `lab/`. معاينتا librsvg السابقتان صالحتان تقنياً: `1080×1920`، `24fps`، `4s`، بلا صوت.

## اللي تهيّأ واختُبر بهالدفعة

- بيئة Piper `1.8.0` والنموذج الإنكليزي `en_US-ljspeech-medium` داخل `lab/voice-env` و`lab/models/`. ملفات تثبيت ومخازن التنزيل محلية للمشروع. نُزّل نموذج إنكليزي واحد فقط بعد فحص الحجم والترخيص؛ ما نُزّل نموذج عربي.
- ملفات الصوت الموسومة `TEST_ONLY`: `lab/evidence/en-piper-ljspeech-TEST_ONLY.wav`، `ar-macos-majed-TEST_ONLY.wav`، `en-macos-samantha-TEST_ONLY.wav`، `en-macos-daniel-TEST_ONLY.wav`. القياسات والأحجام والبصمات وملاحظات المصدر والترخيص في `docs/evaluation-results.csv`؛ درجات السماع البشرية بعدها فارغة.
- `lab/motion-canvas/` يحتوي المشهد القابل للتعديل ومشروع Motion Canvas `3.17.2`. التصدير من المحرر نجح إلى صور PNG محلية، وبعدها حُوّل بـFFmpeg. لقطتا العربية والإنكليزية اتراجعن بصرياً؛ تشكيل العربية صحيح وكل تسمية في مشهد EN إنكليزية.
- ملفات الفيديو الموسومة `TEST_ONLY`: `lab/evidence/motion-canvas-ar-TEST_ONLY.mp4` و`motion-canvas-en-TEST_ONLY.mp4` و`motion-canvas-bilingual-TEST_ONLY.mp4`. راجعها بـFFprobe في التقرير. لا صوت في موشن Canvas.
- `tools/record_media_evaluation.py` يسجل البصمة والحجم ومدة/مواصفات الوسيط ومصدره وترخيصه، ويترك درجات الجودة فارغة للمراجع البشري. التقرير الكامل والأوامر والمراجع الرسمية في `docs/LOCAL_AUDIO_MOTION_EVALUATION.md`.
- نتيجة الاختبار: `cd lab/motion-canvas && npm audit` = صفر ثغرات؛ `npm run build` نجح (TypeScript وVite). تنبيه: توافق Vite 7 مع إضافة Motion Canvas مثبت محلياً بتعديل إعداد تجريبي، فيحتاج مراجعة قبل اعتماد build إنتاجي.
- حالة الجودة: ما انحكم على وضوح النطق/طبيعية الصوت من القياسات وحدها. عينة Majed المحلية تخضع لترخيص macOS وغير مناسبة كأصل إنتاج للنشر التجاري. ماكو حالياً صوت عربي مفتوح المصدر ثبت أن ترخيصه واضح ومناسب؛ الفجوة العربية **مفتوحة**.

## الملفات المتغيرة أو المضافة بهالدفعة

- تحديث `.gitignore` لتجاهل البيئات والمخابئ والمخرجات المحلية.
- إضافة `lab/motion-canvas/` (المشروع، lockfile، مشهد AR/EN وإعداد Vite).
- إضافة `tools/record_media_evaluation.py`.
- إضافة `docs/evaluation-texts.md` و`docs/evaluation-results.csv` و`docs/LOCAL_AUDIO_MOTION_EVALUATION.md`.
- مخرجات WAV/MP4/PNG والنماذج وبيئات التثبيت تحت `lab/`؛ المستبعد منها من Git وفق `.gitignore`.

## أول خطوة معلّقة

استمع محلياً للعينات الأربع وسجّل حكم النطق والإيقاع والأخطاء في `docs/evaluation-results.csv` (الدرجات من 1 إلى 5، أو اتركها فارغة إذا ما ينطبق):

```sh
cd /Users/aliadil/Projects/ContentFactory
afplay lab/evidence/ar-macos-majed-TEST_ONLY.wav
afplay lab/evidence/en-piper-ljspeech-TEST_ONLY.wav
afplay lab/evidence/en-macos-samantha-TEST_ONLY.wav
afplay lab/evidence/en-macos-daniel-TEST_ONLY.wav
```

بعد التقييم البشري، الخطوة التالية هي البحث/الاختبار عن صوت عربي مفتوح المصدر بترخيص واضح للوزن ومجموعة البيانات، من دون تنزيله قبل فحص الحجم والاحتياجات. لا تختار جنس صوت مسبقاً؛ دوّن بيانات بطاقة الصوت وسبب اختيارها وثقة الاختيار بعد مقارنة السماع. راجع MP4s المحلية بمشغل فيديو وسجّل تقييم الحركة أيضاً.

## أوامر متابعة الموشن

تشغيل المحرر على localhost فقط:

```sh
cd /Users/aliadil/Projects/ContentFactory/lab/motion-canvas
npm run start -- --host 127.0.0.1 --port 9000 --strictPort
```

من الواجهة اضبط `1080×1920` و`24fps`، واضغط `RENDER`. تقرير الاختبارات والأوامر الكاملة: `docs/LOCAL_AUDIO_MOTION_EVALUATION.md`.
