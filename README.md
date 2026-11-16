# مصنع المحتوى الذكي

مختبر محلي لإنتاج ومراجعة معاينات AR/EN. الميزانية الخارجية صفر، النشر الخارجي معطّل، وStageCore وKids Studio خارج النطاق.

## الحالة

- توثيق المرجع وقالب الاعتمادات موجودان بجذر المشروع.
- ملفات المختبر مفكوكة داخل `lab/` بعد فحص ZIP وCRC والمسارات.
- اختبارات الاستئناف المحلية اجتازت ست حالات. عينات الفيديو الأصلية اجتازت FFprobe.
- الرندر الحديث يحتاج `librsvg` لأن `FFmpeg` المثبت لا يحتوي SVG decoder. `n8n` غير مثبت.

## تشغيل المختبر

```sh
node lab/motion.mjs
python3 lab/test_checkpoint.py
python3 lab/render_mac.py
```

يتطلب `render_mac.py` الأمرين `rsvg-convert` و`ffmpeg`، ويتحقق من خرج الفيديو عبر `ffprobe`. تثبيت `librsvg` عبر Homebrew: `brew install librsvg`.

راجع [HANDOFF.md](HANDOFF.md) لاستئناف الخطوة المعلقة، و[ContentFactory_Implementation_Reference_AR.md](ContentFactory_Implementation_Reference_AR.md) للمواصفة.
