# اختبار اختيار الحركة بحسب محتوى المشهد — TEST_ONLY

تاريخ الفحص: 2026-11-18. كل النتائج محلية وتجريبية؛ لا اعتماد للإنتاج أو فتح لبوابات الحقوق والجودة والتصدير.

## الخلاصة

تم اختبار طبقة اختيار قواعدية صغيرة فوق Motion Canvas المثبت (`3.17.2`) على موضوعين مختلفين (`concept` و`signals`) وبنسختين عربية بيضاء وإنكليزية. صار الاختيار فعلياً من قائمة مرشحين: يفلتر حسب دور المشهد، ويحسب تطابق الكلمات الدلالية في المعنى والتكوين والعنوان/الوصف، ويرفض تكرار الحركة أو الانتقال السابق. معايير الحركات والوتيرة موثقة داخل الكود، والاختيار المسجل هو ناتج التقييم لا تسمية ثابتة داخل وصف المشهد. المخرجات الأربعة مختلفة فعلياً في تكوينها: نقطة وحلقة، مسار سببي، مقارنة منفرد/متتابع، ومنحنى زمني؛ لذلك صار الاختلاف نابعاً من نوع المحتوى في هذه الأمثلة، لا من سرعة وصفة واحدة فقط.

هذا إثبات محدود: الاختيار قواعدي بالكلمات المفتاحية ولا يفهم المعنى المفتوح مثل نموذج لغوي، ومجموعة المشاهد والبدائل مضبوطة لهذه التجربة فقط. بعض الإطارات الانتقالية تجمع لوحتين ويظهر فيها القص/التداخل عمداً، ومشهد افتتاح `signals` لا يكشف كل النقاط بوضوح في اللقطة الساكنة المختارة. التشغيل المتصل يساعد على فهم التتابع لكنه لا يعوّض حكم المستخدم على السلاسة والذوق.

## المصادر والتوافق والترخيص

| المصدر | النسخة/الحالة المفحوصة | الترخيص | التوافق وما استُخدم |
|---|---|---|---|
| [Motion Canvas](https://github.com/motion-canvas/motion-canvas) | `3.17.2` المثبت محلياً؛ هو محرك الرندر المستخدم | MIT للمحرك (راجع [LICENSE](https://github.com/motion-canvas/motion-canvas/blob/main/LICENSE)) | اختيار الرندر الأساسي. لم تتغير حزمة المصنع ولم تثبّت حزم جديدة. |
| [Motion Canvas examples](https://github.com/motion-canvas/examples) | `master` عند `8ffefed144368d33de4b0e451894c718eb95d574`، آخر نشاط مفحوص 2024-03-21 | MIT للمستودع ([LICENSE](https://github.com/motion-canvas/examples/blob/master/LICENSE)) | فكرة رسم الوصلات والنقاط من `signals.tsx` أعيد رسمها محلياً؛ لا استيراد مباشر للمثال أو أصوله. الحزم في المثال أقدم (`3.14/3.15`) من المثبت. |
| [GovinduSasanka/opus-motion-library](https://github.com/GovinduSasanka/opus-motion-library) | commit `8f1b78a25d0cf310c9bf904d434285046c4ed25a`؛ إصدار `1.2.0`؛ نشاط حديث مفحوص حتى 2026-10-28 | MIT للكود والقوالب بالمستودع | لا يعمل مباشرة مع Motion Canvas: يعتمد Remotion `4.0.532` وReact 19 وR3F/Three وNode `>=20`. استُخدمت فكرة عائلة الرسوم/المقارنة فقط وأعيد رسمها؛ لم تُثبت الحزمة. ترخيص Remotion منفصل عن MIT للقالب. |
| [RenderComp/free-remotion-templates](https://github.com/RenderComp/free-remotion-templates) | commit `f648980e528defb7594e24c6447055f0540f340b`؛ إصدار `1.0.0`؛ نشاط مفحوص حتى 2026-09-07 | MIT للقوالب بالمستودع | قوالب مثل line-chart وsplit-screen مصدر أفكار فقط، ورُسمت من جديد. القوالب لا تغيّر ترخيص المحرك: Remotion له [شروط ترخيص وتسعير منفصلة](https://www.remotion.dev/docs/license/pricing) و[شروط استخدام](https://www.remotion.dev/docs/terms). لم يثبت Remotion ولم يُستخدم. |
| [GTKottman/remotion-transitions](https://github.com/GTKottman/remotion-transitions) | commit `58df89999661dacef23bc23d05b9d2cd978bda45`؛ نشاط مفحوص حتى 2026-10-06 | MIT للمكتبة | أفكار iris/match/carry أعيد بناؤها بـMotion Canvas native shapes/camera؛ الاعتماد المباشر يتطلب Remotion، ولم تثبت الحزمة. |

المراجع الرسمية السابقة لا تعطي موافقة تلقائية لاستخدام تجاري لكل حزمة وأصل ومحرك. لم تُنسخ ملفات قوالب أو صور أو خطوط من أي مستودع. الرسوم الحالية مولدة من أشكال محلية وخطوط النظام؛ فحص الخطوط/الأصول التجاري النهائي ما زال ضمن بوابة الحقوق المغلقة.

## طبقة الاختيار

المنفذ المعزول: `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-selected-TEST_ONLY/src/motion-picker.mjs`، ويستعمله `src/video-scene.tsx`. كل مشهد يقدّم الدور والمعنى والتكوين والعنوان/الوصف؛ `selectCandidate()` يرشح الحركات بدور المشهد، ويعطي نقطة لكل كلمة مطابقة في حقول النص، ويرتب المرشحين، ثم يرفض الحركة/الانتقال السابق. معرّف الحركة المختارة يقود فروع الحركة/الانتقال في renderer. كل سجل خروج يضم الحركة والانتقال والوتيرة والدرجة وسبب الاختيار والمصدر والتكييف. النص العربي/الإنكليزي عقدة نص كاملة؛ لا يوجد تحريك حرفي منفصل.

| نوع الفيديو / اللغة | الدور والمحتوى والتكوين | الحركة والانتقال المختاران | سبب الاختيار والمصدر والتكييف |
|---|---|---|---|
| `concept` / AR وEN | افتتاحية: فكرة من نقطة مركزية ومساحة واسعة | `focal-aperture-reveal` / `iris-to-focus`، score AR 3 / EN 5 | يطابق معنى النقطة والفكرة والتكوين المركزي؛ تكبير الحلقة حول النواة. إلهام Motion Canvas `signals` وiris من GTKottman؛ الحلقة مرسومة محلياً. |
| `concept` / AR وEN | شرح: ثلاث محطات على مسار منحني | `causal-curve-trace` / `path-carry`، score AR 4 / EN 8 | تطابق المسار والمحطات والنقاط والوصل؛ رسم Bézier ثم كشف المحطات. مثال `signals` وline-chart من RenderComp كمفهوم. |
| `concept` / AR وEN | مقارنة: لقطة منفردة مقابل مجموعة لقطات | `single-to-sequence-match` / `split-match`، score AR 3 / EN 5 | تطابق اللقطات/التسلسل/المجموعة؛ انقسام ومطابقة مع أشكال محلية. split-screen وmatch-cut كمفهوم. |
| `concept` / AR وEN | خاتمة: مسار يلتف قرب خلاصة الفكرة | `idea-line-carry` / `line-led-close`، score AR 3 / EN 3 | تطابق الصورة/المعنى/الخطوة؛ حمل الخط إلى الخاتمة. GTKottman carry مع خطوط Motion Canvas. |
| `signals` / AR وEN | افتتاحية: ملاحظات متفرقة تتقارب | `signal-constellation-gather` / `soft-convergence`، score AR 4 / EN 5 | تطابق إشارات/ملاحظات/متفرقة/تقارب؛ نقاط تتقارب. Motion Canvas `signals` وفكرة parallax من RenderComp. |
| `signals` / AR وEN | رسم اتجاه نوعي عبر الزمن بلا أرقام | `trend-curve-build` / `axis-before-curve`، score AR 3 / EN 4 | تطابق زمن/اتجاه/محاور؛ المحاور أولاً ثم المنحنى. line-chart من RenderComp وعائلة الرسوم من Opus كمفهوم؛ لا بيانات أداء. |
| `signals` / AR وEN | مقارنة: نقطة مفردة مقابل خط اتجاه | `point-versus-trend-focus` / `focus-contrast`، score AR 4 / EN 6 | تطابق قراءة/اتجاه/سياق/خط؛ تثبيت النقطة ثم اكتمال المنحنى. split-screen وcomparison/chart كمفهوم. |
| `signals` / AR وEN | خاتمة: اتصال النقاط يتحول إلى مسار جامع | `pattern-to-thesis-carry` / `trend-line-carry`، score AR 4 / EN 5 | تطابق نمط/إشارات/ربط/أوسع؛ جمع النقاط في مسار. GTKottman carry مع رسم محلي. |

تفاصيل قرار كل لغة ودرجات المطابقة محفوظة في `lab/evidence/motion-content-selection-TEST_ONLY/motion-selection-rules-TEST_ONLY.json`. السجل الإنكليزي يعيد سبباً دلالياً بالعربية في بعض الحقول الوصفية؛ هذا حقل مراجعة/تعليل وليس نصاً معروضاً بالفيديو.

## نتائج المخرجات

المعاينات الأخيرة (بعد ربط مخرجات المقيّم بفروع الحركة الفعلية):

- `lab/evidence/motion-content-selection-TEST_ONLY/renders-rules-TEST_ONLY/concept-ar-white-rules-TEST_ONLY.mp4` — 9.416667s، 362,433 bytes.
- `lab/evidence/motion-content-selection-TEST_ONLY/renders-rules-TEST_ONLY/concept-en-white-rules-TEST_ONLY.mp4` — 9.416667s، 439,315 bytes.
- `lab/evidence/motion-content-selection-TEST_ONLY/renders-rules-TEST_ONLY/signals-ar-white-rules-TEST_ONLY.mp4` — 9.958333s، 262,277 bytes.
- `lab/evidence/motion-content-selection-TEST_ONLY/renders-rules-TEST_ONLY/signals-en-white-rules-TEST_ONLY.mp4` — 10.000s، 319,785 bytes.

كل الملفات الأربعة H.264، `1080×1920`، `24/1 fps`، بلا stream صوت؛ `nb_frames`: 226، 226، 239، 240. اكتمل فك الترميز لكل فيديو بـFFmpeg من دون أخطاء. فحص الأسماء أكد وسم `TEST_ONLY` وعدم وجود مؤشرات تسمية نشر مثل `final/production/approved`. أوراق المشاهد الأربع النهائية موجودة في `lab/evidence/motion-content-selection-TEST_ONLY/scene-contact-sheets-rules-TEST_ONLY/`، ومثال الإطار بالحجم الكامل من الرندر الجديد: `review-frames-TEST_ONLY/signals-ar-rules-frame-100-TEST_ONLY.png`. بقيت أول مجموعة أوراق/رندرات محفوظة بمساراتها الأصلية.

شغّلت محرر Motion Canvas المتصل على `http://127.0.0.1:4177/` وشاهدت التشغيل يتقدم عند 24fps إلى الإطار 733 من 930 ثم يكمل ويلفّ إلى الإطار 144؛ هذه مشاهدة متصلة للتسلسل الكامل (38.75 ثانية) داخل المحرر. ليست درجة قبول للجودة. لا يوجد صوت.

زمن بناء Vite بعد ربط الاختيار الفعلي قرابة 1.10 ثانية، ونجح TypeScript. أُعيد إنشاء مجموعة إطارات جديدة في المشروع المعزول بعد التغيير: 226/226/239/240 PNG. تشفير MP4 بالتتابع استغرق 0.62–0.73 ثانية لكل فيديو؛ `/usr/bin/time -l` سجل 1,147,781,120–1,181,958,144 bytes maximum RSS، و4.03–4.29s user CPU و0.52–0.60s sys. قياس الذاكرة يخص FFmpeg أثناء فك PNG/الترميز، ولا يوجد قياس لذاكرة Motion Canvas أثناء إنشاء الإطارات.

الأوامر والفحوص المستخدمة (من جذر المشروع):

```sh
cd lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-selected-TEST_ONLY
./node_modules/.bin/tsc --noEmit -p tsconfig.json
./node_modules/.bin/vite build
```

فتح المحرر المحلي للمراجعة/إعادة تصدير إطارات جديدة (المجلد الحالي احتوى الرندر، فلا تعِد الضغط على `RENDER` فوقه):

```sh
cd lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-selected-TEST_ONLY
./node_modules/.bin/vite --host 127.0.0.1 --port 4177 --strictPort
```

```sh
ffprobe -v error -show_entries format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate,avg_frame_rate,nb_frames,sample_rate,channels -of json <video-TEST_ONLY.mp4>
ffmpeg -v error -i <video-TEST_ONLY.mp4> -f null -
```

نتيجة البناء: PASS (858 modules، نحو 1.10s). نتيجة FFprobe وفك الترميز: PASS للملفات الأربعة؛ الصوت غير موجود كما هو مقصود. ملف الخطة JSON وفحص syntax لـ`motion-picker.mjs`: PASS.

## مراجعة بصرية أولية وحدودها

- النص العربي متصل كعقدة RTL واحدة، والتشكيل الموجود في عينة النص ظاهر؛ لا يظهر قصّ في الإطارات المختارة بالحجم الكامل، لكن القراءة على هاتف تحتاج حكم المستخدم على جهازه.
- تباين العناوين واضح في الإطارات الساكنة. اللقطات الصغيرة في contact sheet تقلل وضوح التسميات الثانوية؛ لا يُستنتج منها وحدها حكم على قراءة الهاتف.
- افتتاح `concept` يستخدم الحلقة كعنصر رئيسي في مشهد واحد فقط، بينما مشاهد الشرح والمقارنة والبيانات تستخدم مسارات وأشكال مختلفة.
- افتتاح `signals` يبدأ بتقارب نقاط، لكن العينة الثابتة تظهر نقطتين أو ثلاثاً فقط، والخلفية الدائرية الكبيرة مقصوصة عند طرف الإطار. هذا عيب بصري يحتاج تعديل حركة/تكوين لاحقاً ولا يثبت أن التكوين الحالي جذاب.
- الانتقالات تبين تغير تكوين فعلياً، لكن إطارات الجسر قد تعرض اللوحتين متداخلتين أو جزئيتين، وهذا مقصود للانتقال ويستحق مراجعة بالسلاسة. لم تُعتمد جودة الحركة أو الترجمة.
- لا بيانات فعلية ولا أرقام مختلقة في رسم الاتجاه؛ الرسم توضيحي نوعي موسوم TEST_ONLY.

قائمة التقييم البشري: `lab/evidence/motion-content-selection-TEST_ONLY/human-review-TEST_ONLY.md`؛ كل المعايير ما زالت «بانتظار مراجعة المستخدم».

## قرار الدمج المقترح

الأفضل حالياً إبقاء Motion Canvas واستخدام أفكار محددة لا المكتبات كاملة: رسم الوصلات من مثال Motion Canvas، كشف المسار/المقارنة من RenderComp/Opus كأفكار مرسومة محلياً، وiris/carry من GTKottman كفكرة انتقال. هذه المجموعة المختارة صارت نتائج فعلية لمقيّم قواعدي للكلمات والمعنى، وليست معرّفات ثابتة في وصف المشهد، ولا تضيف محرك Remotion أو اعتماديات كبيرة. لا دمج في مسار الإنتاج قبل مراجعة المعاينات البشرية وحسم الترخيص لكل اعتماد/خط عند الاستخدام المقصود، وتحسين وضوح تجمّع الافتتاحية في `signals`.

النشر والرفع وربط الحسابات والصوت معطلة. StageCore وKids Studio خارج النطاق. لا commit لهذه الدفعة حتى يراجع المستخدم المعاينات ويختار أو يطلب تعديلاً.
