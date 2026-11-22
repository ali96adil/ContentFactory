# اختبار الصوت والموشن محلياً

تاريخ الفحص: 2026-11-17، `Asia/Baghdad`

المجلد: `جذر المستودع`

الحالة: كل الناتج موسوم `TEST_ONLY`؛ لا اعتماد إنتاجياً ولا نشر.

## النتيجة التنفيذية

- **الصوت الإنكليزي:** اختُبر Piper `1.8.0` بصوت `en_US-ljspeech-medium`، واختُبر صوتا macOS `Samantha` و`Daniel` محلياً. القياس يسجل وضوحاً/طبيعيةً بشريين كحقول فارغة عمداً؛ يحتاجان استماعاً بشرياً.
- **الصوت العربي:** أُنتجت عينة `macOS say` بصوت `Majed` للتقييم المحلي فقط. بعد الاستماع، قيّم المستخدم طبيعية الصوت `1/5` ووصفه بأنه روبوتي جداً؛ رُفض هذا المرشح. لم يُختبر صوت عربي مفتوح المصدر بعد.
- **الترخيص:** محرك Piper تحت `GPL-3.0-or-later`، وترخيص كل صوت مستقل. `LJ Speech` معلن Public Domain في بطاقة الصوت. صوت `ar_JO-kareem-medium` يظهر ببيانات مصدر مجموعة تدريب لكن الترخيص مكتوب `See URL`؛ لا يُنزّل ولا يُستخدم إلى أن يتضح الترخيص والحقوق. أصوات `say` تخضع لترخيص macOS ولا تصلح لهذا المشروع كأصول نشر تجاري.
- **الموشن:** أُنشئ مشهد قابل للتعديل بـMotion Canvas `3.17.2`، بالعربية والإنكليزية، ثم صُدّر إلى تسلسل صور وMP4. راجعت لقطتي معاينة: تشكيل العربية واتجاهها صحيحان، والتسميات الإنكليزية كلها إنكليزية. المشهد تجربة تصميمية بسيطة، وليس حكماً على جودة إنتاج نهائية.

## البيئة والأدوات

- macOS `27.0`، Apple Silicon `arm64`، `M3 Max`، ذاكرة موحّدة `48 GB`، ومساحة فارغة نحو `199 GiB` وقت الفحص.
- Python `3.12.9` استُخدم لبيئة Piper المحلية (`lab/voice-env`) لأن عجلة `onnxruntime` المناسبة غير متاحة لـPython `3.15` في هذه البيئة.
- Node.js `24.21.0`، FFmpeg/FFprobe `7.1.1`، `librsvg 2.63.4`، `rsvg-convert 2.63.4`.
- `espeak-ng` غير موجود كأداة مثبتة؛ لم يُثبّت أو يُبنَ في هذه الدفعة.
- تم تنزيل حزمة Piper الصوتية الإنكليزية فقط بعد فحص حجمها: ملف ONNX قرابة `63.5 MB` وملف إعداد صغير. لم يُنزّل نموذج عربي. hash ملف ONNX: `6f52a751e2349abe7a76735eb09dc1875298c77ea2342ffd2fef79ff81b87f22`.
- حزم Node ومخبأ npm وبيئة Python ومخبأ uv كلها داخل `lab/`. اختبار `npm audit`: صفر ثغرات. بناء Motion Canvas نجح مع Vite `7.3.8`، لكن إضافة Motion Canvas تعلن توافق peer أقدم؛ إعداد التوافق محلي وتجريبي ويحتاج مراجعة قبل اعتماد سير بناء إنتاجي.

## نصوص العينات

النصان أصليان ومترجمان على المعنى نفسه، ومحايدان لصانع محتوى معرفي، ولا يقلدان شخصاً ولا يستخدمان صوت طفل:

- AR: «في تجربة صغيرة، تراقب كاميرا إبريق القهوة وتلتقط صورة كل بضع ثوانٍ. بعد ذلك، يرتّب الفريق الصور ليُظهر كيف يتغيّر الضوء مع الوقت.»
- EN: “In a small experiment, a camera watches a coffee pot and takes a picture every few seconds. The team then arranges the images to show how the light changes over time.”

نسخة النص القابلة لإعادة الاستخدام: [`evaluation-texts.md`](evaluation-texts.md).

## نتائج الصوت المقاسة

كل ملفات WAV بصيغة PCM mono، `22,050 Hz`، 16-bit. المقارنة بالمعنى نفسه، وليس بعدد كلمات مطابق بسبب اختلاف اللغتين.

| اللغة | العينة | زمن التوليد | المدة | الحجم |
|---|---|---:|---:|---:|
| AR | [Majed](../lab/evidence/ar-macos-majed-TEST_ONLY.wav) | 0.999s | 15.137s | 667,604 B |
| EN | [Piper LJSpeech](../lab/evidence/en-piper-ljspeech-TEST_ONLY.wav) | 0.982s | 10.147s | 447,532 B |
| EN | [Samantha](../lab/evidence/en-macos-samantha-TEST_ONLY.wav) | 0.946s | 9.552s | 421,320 B |
| EN | [Daniel](../lab/evidence/en-macos-daniel-TEST_ONLY.wav) | 0.696s | 9.941s | 438,490 B |

القياسات تُظهر زمن وحجم الملف فقط، ولا تقيس وضوح النطق أو سلاسة الإيقاع أو الأخطاء اللغوية. الحقول البشرية في [`evaluation-results.csv`](evaluation-results.csv) فارغة عدا تقييم المستخدم لعينة `Majed`. بطاقة Piper تصف LJSpeech بأنها أنثى؛ بيانات macOS لا تعلن الجندر، فسُجلت `unspecified`.

**تصحيح بعد الاستماع:** قيّم المستخدم طبيعية `Majed` بـ`1/5` (روبوتي جداً). الدرجة مسجلة في CSV؛ الوضوح والأخطاء اللغوية لم تُقيّم بعد. لا تعتمد العينة.

## اختبار الموشن

المشهد يشرح انتقال الضوء من إبريق القهوة إلى حساس ثم تسلسل صور. يرسم الأشكال والرسوم داخل Motion Canvas، من دون أصول صور/فيديو خارجية.

| الملف | القياس FFprobe | الحجم | SHA-256 |
|---|---|---:|---|
| [AR MP4](../lab/evidence/motion-canvas-ar-TEST_ONLY.mp4) | `1080×1920`, `24fps`, `71` frames, `2.958333s` | 72,754 B | `2834b696b06f80869be60f197209991e03c0b472cd5060a5f71d9425494233c5` |
| [EN MP4](../lab/evidence/motion-canvas-en-TEST_ONLY.mp4) | `1080×1920`, `24fps`, `76` frames, `3.166667s` | 95,243 B | `69f17aaf69c759324ba65354b9a14e95292d9b3b2bb5541fdcee7e6098977d4a` |
| [Bilingual MP4](../lab/evidence/motion-canvas-bilingual-TEST_ONLY.mp4) | `1080×1920`, `24fps`, `147` frames, `6.125s` | 142,332 B | `460de3fb09fdc90564800ab7d341cf622bfb8d7f71d522a66dd521034c0d83eb` |

المعاينتان الثابتتان: [AR](../lab/evidence/motion-canvas-ar-preview-TEST_ONLY.png) و[EN](../lab/evidence/motion-canvas-en-preview-TEST_ONLY.png). المقابل السابق المعتمد على SVG/librsvg موجود في `lab/evidence/librsvg-*-TEST_ONLY.mp4`، وهو أسرع وأخف اعتماداً ومفيد لتبديل النص والألوان والمقاس بقوالب محدودة. Motion Canvas يتيح تركيباً زمنياً وحركة أدق ومراجعة مرئية ضمن المحرر، مقابل اعتماديات JavaScript أكثر. كلاهما بلا صوت. الحقول البشرية للحركة متروكة فارغة إلى حين مراجعة السرعة والراحة البصرية.

## الأدوات والتراخيص التي راجعتها

- [Piper](https://github.com/OHF-Voice/piper1-gpl) و[ترخيص المحرك والأصوات](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/LICENSING.md): المحرك `GPL-3.0-or-later`، ويجب تقييم حقوق الصوت منفصلة. إصدار PyPI المستخدم `piper-tts 1.8.0`.
- [بطاقة صوت Piper LJSpeech](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/ljspeech/medium): `en_US`، متحدث واحد، جودة medium، `22,050 Hz`، dataset Public Domain؛ تصف البطاقة الصوت بأنه أنثى.
- [بطاقة Piper Kareem العربية](https://huggingface.co/rhasspy/piper-voices/tree/main/ar/ar_JO/kareem/medium): `ar_JO`، متحدث واحد، جودة medium، `22,050 Hz`؛ ترخيص مجموعة التدريب غير محدد بوضوح في البطاقة. لذلك لم أحمّله.
- [Nabra-82M Arabic](https://huggingface.co/oddadmix/Nabra-82M-v0.1): نموذج `MSA` عربي بصوت واحد، بطاقة النموذج تعلن Apache-2.0؛ يشترط الواجهة نطق/تشكيل عربي وeSpeak G2P. لم يُختبر بعد.
- [Nabra ONNX INT8](https://huggingface.co/marwanelamami/nabra-82m-int8-onnx): نسخة 82M بحجم `83.2 MB` تقريباً، وبطاقة الناشر تعلن Apache-2.0 وترصد زمن تشغيل مرجعياً على Snapdragon؛ لم تُقَس على هذا الماك.
- [Nabra-7M-Distill](https://huggingface.co/oddadmix/Nabra-7M-Distill): نسخة عربية `MSA` أصغر (`30.9 MB` لكل ملفات المستودع)، وبطاقة Apache-2.0؛ ما زالت تحتاج PyTorch وeSpeak G2P.
- راجعت ملفات النموذج قبل أي تنزيل: ONNX INT8 `83.2 MB`؛ وزن الصوت المرافق نحو `524 kB`. عجلات ARM64 macOS التي حلّها `uv` كانت `torch 2.15.0` بحجم `138.6 MB` و`misaki 0.9.4` بحجم `3.6 MB` و`espeakng-loader 0.2.4` بحجم `9.9 MB`، إضافة لاعتماديات أصغر. المساحة الحرة نحو `197 GiB` وقت المحاولة.
- محاولة `uv pip install --python lab/voice-env/bin/python torch==2.15.0 misaki==0.9.4 espeakng-loader==0.2.4` لم تُظهر تقدماً بعد انتظار يزيد على دقيقتين؛ أوقفتها. تحققت لاحقاً أن الحزم الثلاث غير مثبتة، ولم يُنزّل Nabra ولا تُنتج عينة جديدة.
- قرار هذه الدفعة: لم ننزّل النموذج ولم نعد محاولة تثبيت الاعتماديات. صفحة Nabra ونسخة ONNX تعلنان Apache-2.0 للوزن، لكن صفحة النموذج لا تسمي بيانات التدريب أو رخصتها ومصدر تسجيل الصوت؛ لهذا بقي شك مصدر البيانات قائماً حسب شرط المشروع. يلزم توثيق من ناشر النموذج قبل التنزيل أو التشغيل.
- [Kokoro](https://github.com/hexgrad/kokoro): `Apache-2.0`، لكن اللغات المعلنة لا تشمل العربية، لذلك لم يُحمّل ولم يُختبر للعربية.
- [Motion Canvas](https://github.com/motion-canvas/motion-canvas) ورخصته `MIT`؛ دليل [التصدير](https://motioncanvas.io/docs/rendering/) يوضح إخراج تسلسل الصور واستخدام FFmpeg للفيديو.
- [شروط Apple](https://www.apple.com/legal/sla/): عينة `say` مرجع محلي لتجربة السماع فقط؛ لا تُعتمد للتوزيع أو الإنتاج التجاري.
- [eSpeak NG](https://github.com/espeak-ng/espeak-ng): مرشح مفتوح المصدر لم يُختبر في هذه الدفعة؛ لم يكن مثبتاً، وبقيت عينة Majed المحلية فقط للعربية دون اجتياز ترخيص تجاري.

## أوامر إعادة التشغيل

توليد عينة Piper الإنكليزية (البيئة والنموذج موجودان محلياً):

```sh
cd "$(git rev-parse --show-toplevel)"
printf '%s' 'In a small experiment, a camera watches a coffee pot and takes a picture every few seconds. The team then arranges the images to show how the light changes over time.' | lab/voice-env/bin/piper -m lab/models/en_US-ljspeech-medium.onnx -f lab/evidence/en-piper-ljspeech-TEST_ONLY.wav
```

إعادة توليد عينة macOS العربية وإنشاء WAV بترميز المشروع:

```sh
cd "$(git rev-parse --show-toplevel)"
say -v Majed -o lab/evidence/ar-macos-majed-TEST_ONLY.aiff 'في تجربة صغيرة، تراقب كاميرا إبريق القهوة وتلتقط صورة كل بضع ثوانٍ. بعد ذلك، يرتّب الفريق الصور ليُظهر كيف يتغيّر الضوء مع الوقت.'
ffmpeg -y -i lab/evidence/ar-macos-majed-TEST_ONLY.aiff -ac 1 -ar 22050 -sample_fmt s16 lab/evidence/ar-macos-majed-TEST_ONLY.wav
```

إعادة إنشاء بيئة Motion Canvas المحلية وتشغيل المحرر:

```sh
cd $(git rev-parse --show-toplevel)/lab/motion-canvas
npm install
npm run start -- --host 127.0.0.1 --port 9000 --strictPort
```

من المحرر اضبط `resolution` إلى `1080×1920` و`Rendering frame rate` إلى `24`، ثم اضغط `RENDER` ليخرج PNG إلى `output/project/`. لتشفير تسلسل كامل (من `000000.png`):

```sh
cd "$(git rev-parse --show-toplevel)"
ffmpeg -y -framerate 24 -i 'lab/motion-canvas/output/project/%06d.png' -c:v libx264 -crf 22 -pix_fmt yuv420p lab/evidence/motion-canvas-bilingual-TEST_ONLY.mp4
```

لإضافة نتيجة ملف إلى سجل CSV، استخدم [`record_media_evaluation.py`](../tools/record_media_evaluation.py). مثال:

```sh
python3 tools/record_media_evaluation.py --kind audio --language en --candidate 'Piper 1.8.0 / en_US-ljspeech-medium' --asset lab/evidence/en-piper-ljspeech-TEST_ONLY.wav --source-url https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/ljspeech/medium --license 'Public Domain dataset; Piper engine GPL-3.0-or-later' --generation-seconds 0.982 --gender-metadata 'female (voice card)' --notes 'human listening review pending'
```

## التوصية والخطوة التالية

أبقِ Motion Canvas مرشحاً للتجارب القابلة للتحرير، واحتفظ بـlibrsvg للقوالب القصيرة ذات الاحتياجات البسيطة. قبل اعتماد أي منهما، أعد بناءً نظيفاً بتوافقات إصدارات مدعومة واختبر سهولة تحريك مشهدين إضافيين.

لا تدمج Piper LJSpeech قبل استماع بشري ومراجعة متطلبات ترخيص المحرك GPL. صوت `Majed` مرفوض للطبيعية حسب الاستماع. لم يبدأ اختبار Nabra-82M-INT8 لأن بطاقة النموذج لا تحدد بيانات التدريب أو رخصتها/مصدر التسجيل، وهذا سبب كافٍ لإيقاف التنزيل بموجب ضوابط المشروع. كذلك تحتاج بيئة التشغيل محلياً `torch` و`misaki` وeSpeak NG؛ محاولة تثبيتها سابقاً توقفت بلا تقدم ولم تُثبّت حزم جديدة. استأنف فقط بعد ظهور توثيق يزيل شك المصدر والترخيص؛ عندها أعد فحص أحجام الحزم والمساحة وأعد استخدام البيئة المحلية.

## متابعة لاحقة: فحص Habibi-TTS للهجة العراقية

بتاريخ 2026-11-17 فُحص المرشح `Specialized/IRQ` ومصادر بيانات تدريبه. **لم يُنزّل ولم يُشغّل** بسبب قيود غير تجارية مثبتة في سلسلة التدريب، وبيانات عراقية داخلية مجهولة provenance، وتضارب بيانات ترخيص checkpoint. تفاصيل الجدول وقياسات الجهاز والاعتماديات ونتيجة فحص Lahgtna Chatterbox v1 في [`HABIBI_IRQ_LICENSE_REVIEW.md`](HABIBI_IRQ_LICENSE_REVIEW.md). لا توجد عينة أو قياسات صوت جديدة في هذه المتابعة.
