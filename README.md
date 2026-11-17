# مصنع المحتوى الذكي

مختبر محلي لإنتاج ومراجعة معاينات AR/EN. الميزانية الخارجية صفر، النشر الخارجي معطّل، وStageCore وKids Studio خارج النطاق.

## الحالة

- توثيق المرجع وقالب الاعتمادات موجودان بجذر المشروع.
- ملفات المختبر مفكوكة داخل `lab/` بعد فحص ZIP وCRC والمسارات.
- اختبارات الاستئناف المحلية اجتازت ست حالات. عينات الفيديو الأصلية اجتازت FFprobe.
- الرندر الحديث يحتاج `librsvg` لأن `FFmpeg` المثبت لا يحتوي SVG decoder. `n8n@2.47.7` مثبت محلياً في `lab/n8n-local`، لكن تشغيله متوقف حالياً إلى أن تُراجع تنبيهات `npm audit`؛ التفاصيل في `HANDOFF.md`.
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

مراجعة الخطوة المحلية والتحليل: [LOCAL_WORKFLOW_NEXT_STEP.md](docs/LOCAL_WORKFLOW_NEXT_STEP.md). مراجعة الصوت العربي الأبيض: [WHITE_ARABIC_VOICE_CANDIDATES.md](docs/WHITE_ARABIC_VOICE_CANDIDATES.md).
