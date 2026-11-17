# مصنع المحتوى الذكي

مختبر محلي لإنتاج ومراجعة معاينات AR/EN. الميزانية الخارجية صفر، النشر الخارجي معطّل، وStageCore وKids Studio خارج النطاق.

## الحالة

- توثيق المرجع وقالب الاعتمادات موجودان بجذر المشروع.
- ملفات المختبر مفكوكة داخل `lab/` بعد فحص ZIP وCRC والمسارات.
- اختبارات الاستئناف المحلية اجتازت ست حالات. عينات الفيديو الأصلية اجتازت FFprobe.
- الرندر الحديث يحتاج `librsvg` لأن `FFmpeg` المثبت لا يحتوي SVG decoder. `n8n@2.47.7` مثبت محلياً في `lab/n8n-local` والخدمة متوقفة؛ راجع `docs/N8N_AUDIT_REVIEW.md` قبل تشغيله.
- الحركة والتنسيقات متوفرة محلياً؛ لا يوجد موصل أداء منصة فعلي أو بيانات حسابات. للتحليل اليدوي بعد التصدير المحلي استخدم `tools/analyze_platform_metrics.py` مع أعمدة `lab/templates/platform-metrics-template.csv`.
- فجوة الصوت العربي الطبيعي المرخص تجارياً مفتوحة؛ مرشحو MSA لم يجتازوا بعد التحقق من مصدر بيانات التدريب. مافي صوت عربي معتمد للإنتاج.

## تشغيل المختبر

```sh
node lab/motion.mjs
python3 lab/test_checkpoint.py
python3 lab/render_mac.py
```

يتطلب `render_mac.py` الأمرين `rsvg-convert` و`ffmpeg`، ويتحقق من خرج الفيديو عبر `ffprobe`. تثبيت `librsvg` عبر Homebrew: `brew install librsvg`.

راجع [HANDOFF.md](HANDOFF.md) لاستئناف الخطوة المعلقة، و[ContentFactory_Implementation_Reference_AR.md](ContentFactory_Implementation_Reference_AR.md) للمواصفة.

مراجعة الخطوة المحلية والتحليل: [LOCAL_WORKFLOW_NEXT_STEP.md](docs/LOCAL_WORKFLOW_NEXT_STEP.md). مراجعة الصوت العربي الأبيض: [WHITE_ARABIC_VOICE_CANDIDATES.md](docs/WHITE_ARABIC_VOICE_CANDIDATES.md). قالب حزمة المحتوى الموحدة AR/EN وبوابات المراجعة: [CONTENT_PACKAGE_CONTRACT.md](docs/CONTENT_PACKAGE_CONTRACT.md) والقالب المحلي [content-package-template.json](lab/templates/content-package-template.json).

## رندر حزمة TEST_ONLY

المحوّل `tools/render_content_package.py` يتحقق من عقد الحزمة ووسم `TEST_ONLY` وبوابات النشر، ثم يمرر النص إلى `lab/motion.mjs` ويستخدم `lab/render_mac.py` وFFmpeg وFFprobe الموجودين. ينتج Short صامتاً، شرائح Carousel، ومخطط Storyboard؛ لا ينشئ صوتاً أو حلقة YouTube نهائية. تبقى بوابات الحقائق والحقوق والجودة والنشر مغلقة.

```sh
python3 tools/render_content_package.py \
  --input lab/evidence/content-package-demo-TEST_ONLY.json \
  --output lab/evidence/content-package-demo-TEST_ONLY-render-05 \
  --platform all --preview-seconds 5
python3 tools/test_content_package_pipeline.py
```

اختر اسم مخرج جديداً كل مرة؛ الأداة ترفض الكتابة فوق مجلد موجود. إذا انقطع توليد SVG، أعد الأمر نفسه مع `--resume` بعد فحص مجلد `.work` الخاص بالتجربة. المخرجات كاملةً موسومة `TEST_ONLY` ومستثناة من Git.

## مراجعة جودة TEST_ONLY

لإنشاء ورقة معاينة واحدة وفحوص FFprobe وPNG آلية للرندر الموجود:

```sh
python3 tools/review_content_package_render.py \
  --artifacts lab/evidence/content-package-demo-TEST_ONLY-render-04/artifacts \
  --output lab/evidence/content-package-demo-TEST_ONLY-review-03
open lab/evidence/content-package-demo-TEST_ONLY-review-03/content-package-contact-sheet-TEST_ONLY.png
```

الورقة تجمع أربع لقطات من كل Short، وكل شرائح Carousel، وكل لوحات Storyboard. ملف `human-review-TEST_ONLY.md` يبقي وضوح النص واتجاه العربية والتباين والقص والحركة والإيقاع والهوية والترجمة بانتظار مراجعتك. لا تمنح الفحوص الآلية اعتماد جودة بشرية. استخدم مجلد إخراج جديداً عند كل تشغيل لأن الأداة ترفض الاستبدال. لفحوص إعادة التشغيل والاستئناف ومنع الاستبدال شغّل `python3 tools/test_content_package_pipeline.py`.
