# مراجعة الحركة والتصميم v9 — TEST_ONLY

التاريخ: 2026-11-18. البداية: `main` عند `6915741`. هذه نسخة مراجعة معزولة فقط؛ لا دمج لمصدر الحركة ولا commit، وبوابات الجودة والحقوق والتصدير والنشر مغلقة.

## السبب الجذري والإصلاح

- قص عنوان خاتمة `concept`: كان محتوى اللوحة القادمة يظهر أثناء كشفها مكانياً، فكان العنوان يتقاطع مع حد الكشف. بقي انتقال كشف السلايد الجديد فوق القديم كما هو؛ صار المحتوى الأمامي تابعاً لمجموعة اللوحة كاملة، ويبقى مخفياً حتى تستقر اللوحة، ثم يظهر العنوان كاملاً.
- الشرائط التي ظهرت عند حركة الكاميرا: سطح الجذر كان ثابتاً بلون الحبر، وعند تحريك لوحة المشهد بالحجم الكامل انكشفت حواف بلون غير خلفية اللوحة. أضيف سطح bleed أكبر من الإطار يتبع لون المشهد النشط؛ لم يتغير الـviewport ولم تُخفَ أو تُحذف عناصر تصميم.
- اتصال النقاط بالمسارات: كانت النقطة والخط يستخدمان تحريكاً مستقلاً. الآن يستخدمان نقاط Bézier المأخوذة عينياً من المسار نفسه وتقدماً ميسّراً واحداً. تحريك خاتمة concept يتبع الآلية نفسها.
- حدود القص: كل خلفية ومحتوى أمامي تابعان لمجموعة المشهد نفسها ذات أبعاد `1080×1920`. قصّ المحتوى مقصور على اللوحة؛ خلفية اللون الصلبة وحدها بلا قص محلي حتى لا تظهر حافتها مع حركة الكاميرا. انتقال الغطاء لم يتغير.
- الخطوط: استخدمت Cairo للعربية وPoppins للاتينية من الخطوط المحلية المثبتة، وفق SIL Open Font License 1.1؛ لم يُنزّل أو يُضاف خط للمستودع. المرجعان الرسميان: [Cairo OFL](https://github.com/google/fonts/blob/main/ofl/cairo/OFL.txt) و[Poppins OFL](https://github.com/google/fonts/blob/main/ofl/poppins/OFL.txt). عُرضت العربية كنص كامل RTL، بلا تحريك حروف منفردة.

## المعاينات الجديدة

كل فيديو H.264 عمودي، `1080×1920`, `24fps`, بلا صوت، وموسوم `TEST_ONLY`:

| المشهد/اللغة | الملف | المدة/الإطارات | الحجم |
|---|---|---:|---:|
| Concept AR | `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-system-v9-TEST_ONLY/renders-visual-system-v9-TEST_ONLY/concept-ar-visual-system-v9-TEST_ONLY.mp4` | 8.6667s / 208 | 224,454 B |
| Concept EN | `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-system-v9-TEST_ONLY/renders-visual-system-v9-TEST_ONLY/concept-en-visual-system-v9-TEST_ONLY.mp4` | 8.6667s / 208 | 273,704 B |
| Signals AR | `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-system-v9-TEST_ONLY/renders-visual-system-v9-TEST_ONLY/signals-ar-visual-system-v9-TEST_ONLY.mp4` | 10s / 240 | 158,622 B |
| Signals EN | `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-system-v9-TEST_ONLY/renders-visual-system-v9-TEST_ONLY/signals-en-visual-system-v9-TEST_ONLY.mp4` | 10.0417s / 241 | 211,248 B |

أوراق المراجعة والانتقالات:

- `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-system-v9-TEST_ONLY/visual-review-v9b-TEST_ONLY/concept-ar-visual-review-v9b-TEST_ONLY.png`
- `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-system-v9-TEST_ONLY/visual-review-v9b-TEST_ONLY/concept-en-visual-review-v9b-TEST_ONLY.png`
- `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-system-v9-TEST_ONLY/visual-review-v9b-TEST_ONLY/signals-ar-visual-review-v9b-TEST_ONLY.png`
- `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-system-v9-TEST_ONLY/visual-review-v9b-TEST_ONLY/signals-en-visual-review-v9b-TEST_ONLY.png`
- قائمة التقييم البشري: `lab/evidence/motion-content-selection-TEST_ONLY/motion-canvas-visual-system-v9-TEST_ONLY/visual-review-v9b-TEST_ONLY/human-review-TEST_ONLY.md`.

فُحصت الأوراق بصرياً: العنوان كامل بعد استقرار الانتقال، التشكيل واتجاه AR ظاهرين، والمسار والنقاط متراكبان. أثناء wipe تبقى اللوحة الجزئية مقصودة كجزء من الانتقال. لا توجد موافقة بشرية على القراءة/الذوق أو السلاسة؛ لم تُشاهد هذه الفيديوهات بتشغيل متصل.

## الفحوص والقياسات

- `node audit-visual-system-v9-TEST_ONLY.mjs`: `PASS 13/13`، بما فيها مجموعة المشهد الكاملة، ظهور العنوان بعد استقرار اللوحة، تتبع لون الخلفية، مسار/ساعة موحّدان للنقطة والخط، RTL، واحتواء المسار والنقاط داخل الإطار (تجاوز مقاسه 0px).
- `python3 check-videos-v9-TEST_ONLY.py`: PASS للفيديوهات الأربعة، اكتمال فك H.264، توافق الإطار/العدد، عدم وجود صوت؛ فحص 16 مسار زاوية على 2,460 إطاراً مستقراً طابق لون خلفية المشهد ضمن السماحية المحددة. إطارات الانتقال نفسها فُحصت في أوراق المراجعة.
- Vite build وTypeScript: PASS (858 modules). ملفات التفاصيل: `technical-review-v9-TEST_ONLY.json` و`audit-visual-system-v9-TEST_ONLY.json`.
- زمن ترميز FFmpeg للفيديو الواحد 0.52–0.56s، وذروة RSS للمرمّز قرابة 1.03 GB. هذا قياس FFmpeg وحده ولا يمثل استهلاك Motion Canvas. مجموع MP4 الأربعة 868,028 B.
- لم يُشغّل n8n ولم يُضف صوت. اختبارات الاستعادة للمسار أدناه منفصلة عن جودة الموشن.

## الحالة

المخرجات جاهزة لمراجعة المستخدم فقط؛ ليست مؤهلة أو معتمدة للإنتاج. لا تستبدل المخرجات السابقة. لا تدمج المصدر القابل لإعادة الاستخدام قبل المراجعة. افتح الفيديوهات محلياً عند الحاجة مثلاً: `open <path-to-TEST_ONLY.mp4>`، ثم املأ قائمة المراجعة البشرية بعد المشاهدة.
