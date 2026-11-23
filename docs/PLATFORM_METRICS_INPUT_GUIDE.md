# دليل تعبئة قالب مقاييس المنصات

القالب المحلي: `lab/imports/platform-metrics-24h.csv`. يحتوي صف مرشح `candidate` وستة صفوف مقارنة `baseline` لكل من YouTube وTikTok وInstagram وFacebook. الحقول الرقمية والتواريخ والتصنيفات التي تحتاج معلومات من المستخدم فارغة عمداً؛ ماكو أي أداء افتراضي أو بيانات `TEST_ONLY`.

## قبل التعبئة

- صدّر أو اقرأ أرقام منشورات تملك صلاحية الاطلاع عليها فقط. لا تضع اسم الحساب الحقيقي أو بريده أو روابطه؛ `account_id` و`post_id` في القالب أسماء مستعارة قابلة للتغيير.
- القالب مستثنى محلياً عبر `.git/info/exclude` حتى لا يدخل Git. أبقِ أي ملف خام آخر خارج Git أيضاً.
- حدد فترة القياس للمرشح بعد 24 ساعة تقريباً. املأ `observed_at` بوقت أخذ الأرقام بصيغة ISO 8601، مثل `2026-11-17T12:00:00Z`، و`age_hours` بعمر المنشور وقتها. يجب أن يكون عمر baseline ضمن ساعة من عمر المرشح؛ المقارنة تستخدم آخر 10 منشورات مؤهلة، وحدها الأدنى خمسة baseline صالحة. القالب يعطيك ستة لتقليل احتمال نقص الصفوف.
- استخدم نفس الحساب والمنصة واللغة وصيغة المحتوى لكل مجموعة مقارنة. لا تخلط ممولاً بعضوي، أو Shorts بـReels، أو فيديو بـCarousel.

## معنى الأعمدة المطلوبة

| العمود | ماذا تملأ |
|---|---|
| `platform` | معبأ مسبقاً بقيمة صغيرة الأحرف: `youtube`, `tiktok`, `instagram`, `facebook`. القيم المقبولة بالمحلل هي هذه الأربع فقط. |
| `account_id` | اترك الاسم المستعار الموجود أو استبدله باسم مستعار ثابت مثل `account_yt_01`؛ يجب أن يتطابق لكل صفوف الحساب نفسه. |
| `topic_id` | رمز موضوع غير كاشف مثل `topic_c01` أو `topic_b01`؛ لا تكتب عنواناً خاصاً أو بيانات شخصية. |
| `post_id` | اترك `candidate`/`baseline` alias أو استخدم رموزاً ثابتة مثل `ig_c01`, `ig_b01`، بدل الرابط العام للمنشور. |
| `language`, `format` | أدخل رمز اللغة (`ar` أو `en`) واسم صيغة ثابتاً داخل المجموعة، مثل `short_video`, `reel`, `carousel`. المحلل يقارن القيم النصية حرفياً ولا يتحقق من قاموس لها. |
| `role` | معبأ مسبقاً بـ`candidate` أو `baseline`؛ هذان المقبولان فقط بعد تحويل الأحرف إلى صغيرة. |
| `observed_at` | وقت أخذ القياس، بصيغة تاريخ/وقت ISO 8601؛ مثال الصيغة أعلاه توضيحي للتنسيق وليس بيانات أداء. |
| `age_hours` | عدد ساعات عمر المنشور عند أخذ القياس. رقم غير سالب؛ للمقارنة، الفرق بين candidate وbaseline لا يتجاوز ساعة. |
| `impressions` | عدد مرات الظهور بالمسمى والتعريف الذي تعرضه المنصة. لا تستبدله بـ`reach` أو مشاهدات إلا إذا كانت المنصة نفسها تسمي المقياس وتعرّفه كـimpressions. |
| `views` | عدد المشاهدات بالمقياس المتاح للمنشور نفسه. لا تخلط تعريفات المشاهدة بين صيغ المحتوى. |
| `avg_watch_seconds` | متوسط وقت المشاهدة بالثواني. إذا كانت المنصة تعرض دقائق أو milliseconds، حوّل الوحدة فقط مع الاحتفاظ بالقيمة كما تعرضها؛ لا تستنتجها من retention. |
| `duration_seconds` | مدة الفيديو المنشور بالثواني. للـCarousel أو منشور بلا مدة فيديو، المحلل الحالي لا يملك تعريفاً مناسباً له؛ لا تخترع مدة ولا تشغّل التحليل على صف ناقص. |
| `saves`, `shares` | أعداد الحفظ والمشاركة كما تعرضهما المنصة لنفس المنشور ونفس فترة/نطاق القياس. لا تستخدم likes أو comments بدلاً عنهما. |
| `rights_status` | اكتب `verified` فقط بعد مراجعة حقوق المحتوى فعلياً؛ وإلا اتركه فارغاً أو سجّل وصف حالة المراجعة. البوابة لا تمر إلا للقيمة `verified`. |
| `quality_status` | اكتب `human_approved` فقط إذا وافق مراجع بشري فعلاً؛ وإلا اتركه فارغاً أو سجّل الحالة. |
| `external_cost_usd` | الكلفة الفعلية المرتبطة بالمرشح بالدولار. اكتب `0` فقط إذا كانت فعلاً صفراً؛ لا تحول المجهول إلى صفر. |
| `data_origin` | `manual_export` إذا نقلت الأرقام من ملف تصدير رسمي، أو `manual_entry` إذا نسختها يدوياً من لوحة المنصة. لا تستخدم `synthetic` أو `TEST_ONLY` هنا. |

المحلل يتطلب الأعمدة الـ19 كلها، وتاريخاً قابلاً للقراءة، وأرقاماً غير سالبة في `age_hours`, `impressions`, `views`, `avg_watch_seconds`, `duration_seconds`, `saves`, `shares`, `external_cost_usd`. الفراغ و`N/A` لا يصلحان مكان الرقم؛ **لا تعوّض قيمة غير متاحة بصفر أو تخمين**. إذا لم تعرض المنصة أحد المقاييس المطلوبة، اتركه فارغاً ولا تشغّل المحلل على ذلك الصف/القالب. يلزم عندها تعديل معلن للمحلل أو تضييق المقارنة بموافقة لاحقة؛ لا تغيّر تعريف القياس بنفسك.

## من أين تجيب الأرقام وما قد لا يتوفر

| المنصة | المصدر اليدوي الموصى به | انتبه إلى |
|---|---|---|
| YouTube | YouTube Studio → `Analytics` أو `Insights` → `Content` → `SEE MORE`/`ADVANCED MODE`، ثم اختر الفيديو والتقرير و`Export current view`. | YouTube يعرّف `impressions` كمرات ظهور الصورة المصغرة على أسطح محسوبة. تقرير Shorts الأساسي يعرض views/likes/subscribers و`Stayed to watch`؛ لا تعتبر `Stayed to watch` impressions ولا تنقله إلى عمودها. مقياس saves ليس من مقاييس الفيديو القياسية الموثقة في لوحة Analytics؛ اتركه فارغاً إن لم يظهر. تحقّق أيضاً من ظهور `shares` و`average view duration` للتقرير المحدد. [شرح YouTube للتقارير والتصدير](https://support.google.com/youtube/answer/9717005?hl=en-EN)، [فهم أداء المحتوى وShorts](https://support.google.com/youtube/answer/12220281?co=GENIE.Platform%3DDesktop). |
| TikTok | TikTok Studio → `Analytics`، أو `Posts` في TikTok Studio على الويب → `View analytics` بجانب منشورك. اكتب الأرقام يدوياً إذا لم يوجد تصدير عضوي رسمي في واجهتك. | TikTok يتيح تحليلات المنشورات، لكن التوفر والتسميات تختلف حسب الحساب والمنطقة والصيغة، ولم نثبت من التوثيق الرسمي مسار CSV لتحليلات المحتوى العضوي. لا تفترض أن `impressions` أو `saves` متاحان؛ `views`, `average watch time`, `shares` أو `favorites` لا تدخلها إلا إذا عرضتها الواجهة بوضوح وبنفس التعريف لكل الصفوف. تقارير CSV في Ads Manager تخص الإعلان المدفوع وليست بديلاً لبيانات العضوي. [TikTok Studio وتحليلات المنشور](https://support.tiktok.com/en/using-tiktok/growing-your-audience/comment-insights-on-tiktok)، [تقارير Ads Manager](https://ads.tiktok.com/resources/help/article/how-to-use-view-report-in-tiktok-ads-manager). |
| Instagram | Meta Business Suite → اختر حساب Instagram → `Insights` → `Content`/`Export data`، وحدد المحتوى والفترة؛ أو اعرض Insights للـReel/المنشور داخل Instagram. | Meta توثق `reach`, `views`, `shares`, `saves` لبعض مقاييس/أنواع Instagram، لكنها تختلف حسب نوع المحتوى والصلاحيات. `reach` ليس `impressions`; لا تضعه بعمود impressions. متوسط المشاهدة والمدة قد لا يظهران لبعض المنشورات أو التقارير. لا تخلط view count الخاص بـReel مع impressions. [Meta: Instagram Insights metrics](https://developers.facebook.com/docs/graph-api/reference/shadow-ig-user/insights/)، [حقول Instagram media](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/v21.0/)، [Meta Business Suite export](https://www.facebook.com/business/help/397273916756139). |
| Facebook | Meta Business Suite → اختر Facebook Page → `Insights` → `Content`/`Export data`. استخدم تقرير فيديو/ريلز لنفس النوع على كل صف. | توثيق Meta يذكر مقاييس فيديو مثل `total_video_impressions` و`total_video_avg_time_watched`، لكن المقياس المتاح يتغير حسب نوع المنشور والصلاحيات ونطاق القياس، وبعضها lifetime. لا تفترض توفر `saves` أو متوسط المشاهدة لأي منشور؛ إذا غير معروض اتركه فارغاً. [Meta: Video Insights metrics](https://developers.facebook.com/docs/graph-api/reference/video/video_insights/)، [Meta Business Suite export](https://www.facebook.com/business/help/397273916756139). |

قيم `views`, `impressions`, و`avg_watch_seconds` ليست قابلة للاستبدال بين المنصات. المحلل يقارن داخل كل مجموعة منصة/حساب/لغة/صيغة، لذا استخدم فقط المقاييس المتسقة داخل المجموعة. إذا بقي حقل مطلوب غير متاح، توقف عن التحليل واسأل قبل أي تغيير في قواعد الأداة.

## طريقة التعبئة والحفظ

- افتح `lab/imports/platform-metrics-24h.csv` ببرنامج جداول محلي مثل Numbers أو LibreOffice، واختَر UTF-8 عند الاستيراد/الحفظ.
- املأ صف `candidate` للمنشور بعد مرور 24 ساعة تقريباً. املأ صفوف `baseline` الستة بمنشورات سابقة قابلة للمقارنة من الحساب نفسه.
- لا تحذف عنوان عمود، ولا تضف عموداً، ولا تدمج خليتي المنصة/الحساب. خَلِّ كل صف لمنشور واحد، واحفظ بصيغة CSV مفصولة بفواصل.
- لا تشغّل `tools/analyze_platform_metrics.py` على القالب الفارغ. لا تشغّله لاحقاً إذا بقيت خلايا رقمية مطلوبة فارغة، أو إذا استخدمت `TEST_ONLY`/بيانات اصطناعية.

## سجل الاستيراد المحلي

بعد توفر CSV من حساب مصرّح به، احتفظ بنسخته المنقحة داخل `lab/imports/`، ثم أضف الصفوف إلى سجل SQLite المحلي:

```sh
python3 tools/import_platform_metrics.py lab/imports/platform-metrics-24h.csv \
  --database lab/imports/platform-metrics-ledger.sqlite3
```

السجل idempotent على مفتاح المنصة والحساب المستعار والمنشور ووقت القياس UTC. إعادة اللقطة المطابقة لا تكررها؛ اختلاف حقول اللقطة نفسها يرفض كامل الدفعة ويترك السجل السابق كما هو. المسار لا يتصل بالمنصة، ولا يقرر اعتماداً أو توسعاً أو تصديراً/نشراً. حلل CSV بعد ذلك فقط وفق الشروط أعلاه. احتفظ بقاعدة SQLite محلياً خارج Git.
