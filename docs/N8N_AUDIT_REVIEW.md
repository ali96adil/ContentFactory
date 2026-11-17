# مراجعة npm audit لـn8n 2.47.7

تاريخ الفحص: 2026-11-17 (`Asia/Baghdad`). هذه مراجعة للـlockfile المثبت، لا اختبار اختراق ولا إثبات أن كل مسار قابل للوصول من التطبيق.

## النتيجة وطريقة إعادة الفحص

بدأ الفحص من `main` عند commit `a518e64`، شجرة Git نظيفة. بقي `n8n` متوقفاً؛ لم تُفتح واجهته ولم تُستورد Workflows ولم تُربط حسابات. الإصدار في `package.json` و`package-lock.json` هو `n8n@2.47.7`، وNode `v24.21.0`.

الأمر الذي أعاد التقرير التفصيلي:

```sh
cd /Users/aliadil/Projects/ContentFactory
npm --prefix lab/n8n-local audit --cache "$PWD/lab/n8n-local/.npm-cache" --omit=dev --json > lab/n8n-local/.npm-cache/audit-2.47.7.json
```

ملف JSON محفوظ في مخبأ محلي مستثنى من Git؛ لا يحوي أسراراً. npm استعلم عن metadata/advisories من registry أثناء الفحص، لكنه لم يثبّت أو يحدّث أي حزمة. النتائج:

| الشدة | إدخالات npm audit |
|---|---:|
| Critical | 7 |
| High | 69 |
| Moderate | 67 |
| Low | 2 |
| **المجموع** | **145** |

هذه **145 إدخال حزمة متأثرة وليست 145 CVE منفصلة**؛ الـJSON يحوي 125 advisory فريدة و204 مسارات package في شجرة الاعتماديات بسبب تكرار النسخة بمواقع مختلفة. من الإدخالات، `n8n@2.47.7` هو dependency الجذر المباشر الوحيد ويُعلّم `high` بسبب سلسلة اعتمادياته؛ الـ144 الأخرى انتقالية. شدة إدخال `@getzep/*` أو `@n8n/*` قد تكون موروثة من اعتماد أدنى، ولا تعني وجود CVE منفصل باسم كل حزمة.

## الحزم المصنفة حسب نتيجة التدقيق

الأسماء أدناه يتبعها إصدار/إصدارات lockfile؛ كلها انتقالية ما لم تُوسم `direct`. تكرار إصدارين يعني مسارين مثبتين.

### Critical — 7

`@getzep/zep-cloud@1.0.6`, `@getzep/zep-js@2.0.2`, `@langchain/community@1.1.27`, `@n8n/n8n-nodes-langchain@2.47.5`, `fast-xml-parser@5.2.5/4.4.1`, `form-data@4.0.0`, `tar@6.2.1`.

### High — 69

`@asteasolutions/zod-to-openapi@7.3.4`, `@azure/msal-node@3.8.10/5.1.5`, `@browserbasehq/stagehand@1.14.0`, `@microsoft/agents-activity@1.6.1`, `@microsoft/agents-hosting@1.6.1`, `@modelcontextprotocol/node@2.0.0`, `@n8n/agents@0.32.4`, `@n8n/ai-node-sdk@0.37.4`, `@n8n/ai-utilities@0.40.4`, `@n8n/ai-workflow-builder@1.47.4`, `@n8n/api-types@1.47.4`, `@n8n/backend-common@1.47.4`, `@n8n/backend-module-apps@0.3.6`, `@n8n/backend-module-data-table@0.2.6`, `@n8n/backend-module-execution-limits@0.2.4`, `@n8n/backend-module-insights@0.5.6`, `@n8n/backend-module-quick-connect@0.4.4`, `@n8n/backend-module-workflow-builder@0.4.4`, `@n8n/backend-network@1.21.4`, `@n8n/backend-services@1.7.6`, `@n8n/blob-storage@1.15.4`, `@n8n/chat-hub@1.40.4`, `@n8n/composables@1.37.5`, `@n8n/config@2.45.1`, `@n8n/db@1.47.4`, `@n8n/decorators@1.47.4`, `@n8n/design-system@2.46.5`, `@n8n/engine@0.27.1`, `@n8n/expression-runtime@0.38.2`, `@n8n/i18n@2.47.4`, `@n8n/inbound-auth@0.6.2`, `@n8n/instance-ai@1.32.4`, `@n8n/json-schema-to-zod@1.18.0`, `@n8n/mcp-apps@0.24.5`, `@n8n/mcp-browser@0.26.0`, `@n8n/node-engine-compatibility@0.15.4`, `@n8n/permissions@0.84.0`, `@n8n/scheduler@1.16.3`, `@n8n/syslog-client@1.12.0`, `@n8n/task-runner@2.47.4`, `@n8n/telemetry@1.15.4`, `@n8n/typeorm@0.3.20-16/0.14.0`, `@n8n/workflow-sdk@0.40.2`, `@rudderstack/rudder-sdk-node@3.0.5`, `adm-zip@0.5.18`, `axios@1.15.1`, `cacache@15.3.0`, `epub2@3.0.2`, `langsmith@0.4.12`, `linkify-it@4.0.1/5.0.0`, `mailparser@3.9.3`, `make-fetch-happen@9.1.0`, `markdown-it@13.0.2`, `n8n@2.47.7` **direct**, `n8n-core@2.47.4`, `n8n-nodes-base@2.47.5`, `n8n-workflow@2.47.2`, `node-gyp@8.4.1`, `nodemailer@7.0.13/10.0.14`, `openai@4.104.0`, `snowflake-sdk@3.3.0`, `sqlite3@5.1.7`, `toml@3.0.0`, `ts-ics@1.2.2`, `undici@7.29.1`, `ws@8.20.1`, `zod@3.25.75/3.25.76`, `zod-from-json-schema@0.0.5`, `zod-to-json-schema@3.23.3`.

### Moderate — 67

`@1password/connect@1.4.2`, `@aws-sdk/client-bedrock-runtime@3.938.0`, `@aws-sdk/client-cognito-identity@3.808.0`, `@aws-sdk/client-s3@3.808.0`, `@aws-sdk/client-secrets-manager@3.808.0`, `@aws-sdk/client-sso@3.936.0/3.808.0`, `@aws-sdk/core@3.936.0/3.808.0`, `@aws-sdk/credential-provider-cognito-identity@3.808.0`, `@aws-sdk/credential-provider-env@3.936.0/3.808.0`, `@aws-sdk/credential-provider-http@3.936.0/3.808.0`, `@aws-sdk/credential-provider-ini@3.936.0/3.808.0`, `@aws-sdk/credential-provider-login@3.936.0`, `@aws-sdk/credential-provider-node@3.936.0/3.808.0`, `@aws-sdk/credential-provider-process@3.936.0/3.808.0`, `@aws-sdk/credential-provider-sso@3.936.0/3.808.0`, `@aws-sdk/credential-provider-web-identity@3.936.0/3.808.0`, `@aws-sdk/credential-providers@3.808.0`, `@aws-sdk/middleware-flexible-checksums@3.808.0`, `@aws-sdk/middleware-sdk-s3@3.808.0`, `@aws-sdk/middleware-user-agent@3.936.0/3.808.0`, `@aws-sdk/nested-clients@3.936.0/3.808.0`, `@aws-sdk/signature-v4-multi-region@3.808.0`, `@aws-sdk/token-providers@3.936.0/3.808.0`, `@aws-sdk/util-user-agent-node@3.936.0/3.808.0`, `@aws-sdk/xml-builder@3.930.0`, `@azure/identity@4.13.0`, `@daytona/sdk@0.205.1`, `@hono/node-server@1.19.19`, `@kafkajs/confluent-schema-registry@3.8.0`, `@langchain/classic@1.0.27`, `@langchain/cohere@1.0.1`, `@langchain/google-common@2.1.24`, `@langchain/google-gauth@2.1.24`, `@langchain/google-vertexai@2.1.24`, `@langchain/ollama@1.2.6`, `@langchain/pinecone@1.0.1`, `@langchain/qdrant@1.0.1`, `@langchain/redis@1.1.1`, `@langchain/weaviate@1.0.1`, `@microsoft/opentelemetry@1.5.0`, `@n8n/client-oauth2@1.29.4`, `@opentelemetry/instrumentation-http@0.221.0`, `@oracle/langchain-oracledb@0.2.0`, `@qdrant/js-client-rest@1.20.0`, `@sentry/bundler-plugins@11.8.0`, `@sentry/node@11.8.0`, `@sentry/node-native@11.8.0`, `@sentry/profiling-node@11.8.0`, `ajv@7.2.4`, `bull@4.16.5/4.16.4`, `cohere-ai@7.14.0`, `element-plus@2.4.3`, `express-handlebars@8.0.1`, `gaxios@6.7.1/7.1.3`, `gcp-metadata@8.1.4`, `glob@13.0.7/11.1.0/10.5.0`, `google-gax@5.0.8`, `minifaker@1.34.1`, `minimatch@10.2.6/9.0.9`, `qs@6.11.2/6.16.0`, `rimraf@5.0.10`, `sanitize-html@2.18.0`, `showdown@2.1.0`, `stream-json@1.9.1`, `sucrase@3.35.0`, `uuid@9.0.1/8.3.2/10.0.0/11.1.0`, `weaviate-client@3.9.0`.

### Low — 2

`@tootallnate/once@1.1.2`, `http-proxy-agent@4.0.1` (انتقاليتان).

## شنو يعني هذا الخطر بالتشغيل المحلي؟

ربط الخدمة بـ`127.0.0.1` يمنع الاتصالات المباشرة من أجهزة الشبكة، لكنه مو عزل كامل: أي برنامج محلي يقدر يوصل لها، وقد تحاول صفحة ويب خبيثة الوصول إلى منافذ localhost من متصفح المستخدم. وماكو Workflow أو credentials يقلل مسارات تنفيذ العقد الخارجية وOAuth والبريد والسحابة، لكنه ما يثبت عدم وجود مسار عبر واجهة المحرر أو WebSocket. لذلك الخطر أقل من خدمة عامة لكنه مو صفر، والخيار الحالي هو إبقاء الخدمة متوقفة.

| العائلة/الحزمة والإصدار المتأثر | شرط الاستغلال العملي | الأثر في وضعنا الحالي |
|---|---|---|
| `ws@8.20.1` — تجزئة WebSocket صغيرة بكثافة تستنزف ذاكرة العملية | مهاجم يحتاج اتصال WebSocket بالخدمة؛ لا يحتاج Workflow أو credential. | أكثر ما يبقى ذا صلة إذا شُغّلت الواجهة. loopback يصد الشبكة المباشرة، لكنه ما يصد عملية محلية أو كل هجمات المتصفح؛ الخدمة متوقفة حالياً. [GHSA-96hv-2xvq-fx4p](https://github.com/advisories/GHSA-96hv-2xvq-fx4p) |
| `zod@3.25.75/3.25.76` | تمرير مصفوفة ضخمة فيها عناصر تفشل مخططاً بلا حد طول؛ تتراكم أخطاء التحقق وتنفد الذاكرة. | عدم وجود Workflow يقلل البيانات التي تصل للمحلل، لكنه ما ينفي وجود endpoint أو إدخال بالواجهة. يخفف الاستغلال ولا يزيله. [GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5) |
| `fast-xml-parser@4.4.1/5.2.5` | XML غير موثوق مع DOCTYPE/entity؛ قد يُتجاوز ترميز entities، ويصير XSS إذا عُرض الناتج كـHTML؛ وبعض الحالات DoS. | لا يوجد سير XML/Workflow مهيأ عندنا، لذلك لا مسار استعمال مقصود حالياً. لا نعتبر عدم وجود Workflow برهاناً على أن كل code path مغلق. [GHSA-m7jm-9gc2-mpf2](https://github.com/advisories/GHSA-m7jm-9gc2-mpf2) |
| `form-data@4.0.0` | المهاجم يتحكم بحق في multipart request، ويستطيع ملاحظة قيم `Math.random()` لتوقع boundary؛ توجد أيضاً CRLF injection في حقول/أسماء الملفات. | يتطلب مساراً يرسل طلب multipart إلى خدمة أخرى ببيانات المهاجم؛ لا توجد حالياً Workflows أو credentials أو منصة متصلة، فينخفض احتمال الوصول لهذا المسار. [GHSA-fjxv-7rqg-78g4](https://github.com/advisories/GHSA-fjxv-7rqg-78g4) |
| `tar@6.2.1` تحت `cacache`, `node-gyp`, `sqlite3` | معالجة/استخراج archive خبيث؛ تشمل advisories اجتياز hardlink/symlink، overwrite، وgzip bomb تستهلك disk/CPU. | مسار package installation/archive هو الأوضح؛ ماكو Workflow أو رفع archive عندنا. لا تشغّل تثبيت community packages أو مدخلات أرشيف غير موثوقة. [GHSA-23hp-3jrh-7fpw](https://github.com/advisories/GHSA-23hp-3jrh-7fpw)، [GHSA-34x7-hfp2-rc4v](https://github.com/advisories/GHSA-34x7-hfp2-rc4v) |
| `adm-zip@0.5.18` | ZIP crafted يعلن حجم فك كبيراً أو مسارات/permissions خاصة، والبرنامج يفكّه. | ماكو ملف ZIP أو Workflow يمرره حالياً؛ لا ترفع/تفك ZIP غير موثوق عبر أي عقدة. [GHSA-xcpc-8h2w-3j85](https://github.com/advisories/GHSA-xcpc-8h2w-3j85) |
| `@azure/msal-node@5.1.5` | لازم يبدأ OAuth authorization-code flow ويُمرر جزء من التدفق إلى endpoint يتحكم به المهاجم. النسخة `3.8.10` المثبتة أيضاً لا تعني تلقائياً أن نفس advisory ينطبق عليها؛ النطاق المنشور يبدأ `5.0.0-beta.0`. | لا حسابات ولا OAuth connections؛ هذا المسار غير مهيأ. [GHSA-xcx6-jx8p-x3h5](https://github.com/advisories/GHSA-xcx6-jx8p-x3h5) |
| `@modelcontextprotocol/node@2.0.0` | استخدام HTTP server transport/handlers مع طلب أو JSON-RPC batch ضخم؛ package finding لا يثبت أن n8n يشغّل هذا transport تلقائياً. | لا Workflow أو MCP server مهيأ، لذلك ماكو route مقصود حالياً. [GHSA-f897-62hf-6gxq](https://github.com/advisories/GHSA-f897-62hf-6gxq) |
| `axios@1.15.1`, `undici@7.29.1` | أكثر advisories تتطلب redirect/DNS/proxy أو HTTP response غير موثوق أو استعمال مسار HTTP/2/stream المتأثر؛ بعضها قد يكشف headers/بيانات أو يسبب DoS. | الاتصال outbound المحتمل يعتمد على عقد/تكامل/طلب؛ ماكو Workflow أو API credentials. لا تُستخدم هذه الحقيقة كضمان ضد كل طلب داخلي من التطبيق. |
| `nodemailer@7.0.13/10.0.14` | إرسال بريد، OAuth2 token fetch، SMTP server خبيث، recipient/header crafted، أو استعمال raw/file/URL في بناء الرسالة، حسب advisory. | لا SMTP credentials ولا Workflow بريد؛ ماكو مسار إرسال مُعدّ. |
| AWS SDK وLangChain/Zep وAzure وGoogle وغيرها من integrations | الطلبات/الـparsers/credential flows المحددة لكل SDK؛ جزء كبير من نتائجها يعيد تضخيم `uuid`, `zod`, XML/HTTP advisories الموروثة، مو CVE مستقل لكل wrapper. | ماكو خدمات أو credentials أو عقد منفذة. تأثيرها التشغيلي الحالي أقل، لكنها تبقى في شجرة مثبتة وتظهر بالتدقيق. |

### تفسير أرقام critical

السبعة `critical` مو سبعة ثغرات أصلية مختلفة. أقوى جذور الـcritical الظاهرة من بيانات npm هي: `fast-xml-parser` entity-encoding bypass (CVSS 9.3) و`form-data` boundary randomness (شرطه ملاحظة PRNG والتحكم بطلب multipart) و`tar` archive decompression/parse DoS (CVSS 7.5). إدخالات `@getzep/zep-cloud`, `@getzep/zep-js`, `@langchain/community` و`@n8n/n8n-nodes-langchain` موروثة من شجرة SDK (مثل `form-data`, `qs`, `zod`)، وليست advisories مستقلة مثبتة على هذه الأسماء. [شرح fast-xml-parser](https://github.com/advisories/GHSA-m7jm-9gc2-mpf2)، [شرح form-data وشروطه](https://github.com/form-data/form-data/security/advisories/GHSA-fjxv-7rqg-78g4)، [شرح tar](https://github.com/advisories/GHSA-23hp-3jrh-7fpw).

## مقارنة الإصدار الأحدث والمسار الآمن

فحص npm وقت الجولة أعطى dist-tags: `stable=2.47.7`, `latest=2.47.7`, و`beta=next=2.48.4`. إذن ماكو stable أحدث من المثبت حالياً. GitHub يوسم `2.48.4` صراحةً **Pre-release**؛ ملاحظته المنشورة إصلاح bug في redaction، مو إعلان معالجة advisories التي كشفها audit. إصدار `2.48.4` يعلن Node `>=24.0.0` وترخيص npm `SEE LICENSE IN LICENSE.md` مثل الحالي، لكن كونه pre-release وعدم وجود audit لشجرته يمنع التوصية بنقله الآن. [Release 2.47.7](https://github.com/n8n-io/n8n/releases/tag/n8n%402.47.7)، [Pre-release 2.48.4](https://github.com/n8n-io/n8n/releases/tag/n8n%402.48.4)، [متطلبات npm الرسمية](https://docs.n8n.io/deploy/host-n8n/install-options/install-with-npm/).

الترخيص للمثبت `Sustainable Use License 1.0`؛ ليس Apache/MIT. وثيقة npm الرسمية تسمح بـNode `20.19` إلى `24.x` شامل، وهذا الجهاز على Node 24.21.0 متوافق. الوثيقة نفسها تحذر من إهمال تثبيت npm بدءاً من n8n 3.0؛ لأن Docker خارج النطاق، ما نعتبر الترقية لأي major مستقبلي خطوة تلقائية.

`npm audit fix` اقترح `n8n@1.17.0` كتغيير major ورجوع إلى نسخة أقدم. لم يُنفذ أي إصلاح أو تخفيض. وماكو patch stable أحدث مثبت أنه يسد هذه السلسلة الآن.

**التوصية:** إبقاء n8n متوقفاً، واستخدام مسار التحليل المحلي الموجود `python3 tools/analyze_platform_metrics.py` مع CSV يدوي مصرح به. ما يحتاج المشروع orchestration daemon حتى ينفذ هذه الخطوة؛ CSV + سكربت Python stdlib الحالي أقل سطحاً وأسهل تدقيقاً. إذا ظهر إصدار stable أحدث، قارن lockfile و`npm audit` له في مساحة candidate منفصلة، وتأكد من معالجة `ws`, `fast-xml-parser`, `form-data`, `tar`, `zod` وبقية advisories قبل تحديث مجلد التثبيت؛ بعدها فقط أعد فحص التشغيل على loopback. لا تشغل beta أو `npm audit fix --force` بهذه المرحلة.

## أوامر تحقق محلي لا تشغّل n8n

```sh
cd /Users/aliadil/Projects/ContentFactory
git status --short --branch
node lab/n8n-local/node_modules/n8n/bin/n8n --version
npm --prefix lab/n8n-local audit --cache "$PWD/lab/n8n-local/.npm-cache" --omit=dev --json
```

الخطوة المعلقة القادمة: استعمل `tools/analyze_platform_metrics.py` على CSV فعلي مصرح به إذا توفر؛ اترك n8n متوقفاً. لا تستورد Workflow أو credentials.
