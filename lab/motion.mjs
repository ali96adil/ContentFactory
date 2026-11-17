import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { readFile } from 'node:fs/promises';

const palette = {
  bg: '#0e1c1e', panel: '#142628', grid: '#203538', mint: '#78e4c3',
  cream: '#f6edda', muted: '#b6ceca', copper: '#b9663e', line: '#527f7b'
};
const ease = (x) => 1 - (1 - Math.max(0, Math.min(1, x))) ** 3;
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (ch) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;'
}[ch]));
const isArabic = (locale) => locale === 'ar_white';
const fontFor = (locale) => isArabic(locale) ? 'Geeza Pro, Noto Sans Arabic, sans-serif' : 'Arial, sans-serif';

function wrap(value, limit, maxLines = 4) {
  const words = String(value ?? '').trim().split(/\s+/).filter(Boolean);
  const lines = [];
  let current = '';
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > limit && current) {
      lines.push(current);
      current = word;
    } else current = next;
  }
  if (current) lines.push(current);
  if (lines.length > maxLines) {
    const clipped = lines.slice(0, maxLines);
    clipped[maxLines - 1] = `${clipped[maxLines - 1].slice(0, Math.max(1, limit - 1))}…`;
    return clipped;
  }
  return lines;
}
function textLines(value, { x, y, maxChars, maxLines = 3, size, lineHeight, fill, locale, anchor }) {
  const lines = wrap(value, maxChars, maxLines);
  const dir = isArabic(locale) ? 'rtl' : 'ltr';
  const actualAnchor = anchor ?? 'start';
  const spans = lines.map((line, i) => `<tspan x="${x}" dy="${i === 0 ? 0 : lineHeight}">${esc(line)}</tspan>`).join('');
  return `<text x="${x}" y="${y}" text-anchor="${actualAnchor}" direction="${dir}" unicode-bidi="plaintext" fill="${fill}" font-family="${fontFor(locale)}" font-size="${size}" font-weight="${size >= 48 ? 600 : 400}">${spans}</text>`;
}
function baseSvg(width, height, inner, label) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs><pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="${palette.grid}" stroke-width="1"/></pattern>
  <radialGradient id="glow"><stop stop-color="#204344"/><stop offset="1" stop-color="${palette.bg}"/></radialGradient></defs>
  <rect width="100%" height="100%" fill="${palette.bg}"/><rect width="100%" height="100%" fill="url(#grid)"/>
  ${inner}<text x="${width / 2}" y="${height - 42}" text-anchor="middle" fill="${palette.mint}" font-family="Arial,sans-serif" font-size="22" letter-spacing="3">${esc(label)}</text>
</svg>`;
}
function cupGraphic(cx, cy, t = 0, scale = 1) {
  return `<g transform="translate(${cx} ${cy}) scale(${scale})">
    <circle r="220" fill="url(#glow)" stroke="${palette.line}" stroke-width="3"/>
    <circle r="184" fill="none" stroke="#4c8782" stroke-width="3" stroke-dasharray="3 15"/>
    <path d="M-82 -52 H76 L101 84 Q96 120 50 122 H-63 Q-102 120 -106 84Z" fill="#e7d4a4" stroke="${palette.cream}" stroke-width="6"/>
    <path d="M80 -20H112Q164 -20 151 34Q142 85 99 72" fill="none" stroke="#e7d4a4" stroke-width="18"/>
    <path d="M-94 39 Q-42 ${35 + 5 * Math.sin(t * 3)} 10 39 T93 39 L99 83 Q92 113 51 114H-63Q-90 113 -98 83Z" fill="${palette.copper}"/>
    <path d="M-45 -79 Q-83 -116 -47 -${145 + 12 * Math.sin(t * 2)}M18 -81 Q-15 -118 22 -${151 + 11 * Math.cos(t * 2)}" fill="none" stroke="${palette.mint}" stroke-width="6" stroke-linecap="round"/>
    <circle cx="${152 * Math.cos(t * 0.8)}" cy="${152 * Math.sin(t * 0.8)}" r="10" fill="${palette.mint}"/>
  </g>`;
}

function shortFrame(locale, item, frame, totalFrames, plan) {
  const ar = isArabic(locale);
  const width = 1080, height = 1920, seconds = frame / plan.fps;
  const step = Math.min(item.on_screen_text.length - 1, Math.floor((frame / totalFrames) * item.on_screen_text.length));
  const eased = ease((frame % Math.max(1, Math.floor(totalFrames / item.on_screen_text.length))) / 18);
  const sideX = ar ? 970 : 110;
  const align = 'start';
  const hook = textLines(item.hook, { x: sideX, y: 250, maxChars: ar ? 25 : 36, maxLines: 3, size: 52, lineHeight: 68, fill: palette.cream, locale, anchor: align });
  const stageText = textLines(item.on_screen_text[step], { x: sideX, y: 1495, maxChars: ar ? 24 : 34, maxLines: 2, size: 48, lineHeight: 62, fill: palette.mint, locale, anchor: align });
  const callToAction = textLines(item.call_to_action, { x: sideX, y: 1612, maxChars: ar ? 34 : 48, maxLines: 2, size: 27, lineHeight: 36, fill: palette.muted, locale, anchor: align });
  const progress = 100 + 880 * (frame / Math.max(1, totalFrames - 1));
  const graphic = cupGraphic(540, 935, seconds, 1 + 0.012 * Math.sin(seconds * 1.4));
  const inner = `<text x="540" y="102" text-anchor="middle" fill="${palette.mint}" font-family="Arial,sans-serif" font-size="25" letter-spacing="4">${ar ? 'معاينة قصيرة' : 'SHORT PREVIEW'} • TEST_ONLY</text>
  ${hook}${graphic}${stageText}${callToAction}
  <path d="M100 1700H980" stroke="${palette.line}" stroke-width="4"/><path d="M100 1700H${progress}" stroke="${palette.mint}" stroke-width="7"/>
  <circle cx="${progress}" cy="1700" r="11" fill="${palette.cream}" opacity="${0.55 + eased * 0.45}"/>`;
  return baseSvg(width, height, inner, `${ar ? 'AR WHITE' : 'ENGLISH'} • SILENT VISUAL DRAFT`);
}
function carouselSlide(locale, slide, index, total) {
  const ar = isArabic(locale);
  const width = 1080, height = 1350, sideX = ar ? 970 : 110;
  const align = 'start';
  const heading = textLines(slide.heading, { x: sideX, y: 225, maxChars: ar ? 24 : 34, maxLines: 2, size: 58, lineHeight: 72, fill: palette.cream, locale, anchor: align });
  const body = textLines(slide.body, { x: sideX, y: 360, maxChars: ar ? 32 : 46, maxLines: 3, size: 34, lineHeight: 50, fill: palette.muted, locale, anchor: align });
  const note = textLines(slide.visual_note, { x: sideX, y: 1125, maxChars: ar ? 30 : 44, maxLines: 2, size: 29, lineHeight: 38, fill: palette.cream, locale, anchor: align });
  const motif = cupGraphic(540, 840, index * 0.6, 0.78);
  const dots = Array.from({ length: total }, (_, n) => `<circle cx="${430 + n * 55}" cy="1190" r="${n === index ? 12 : 7}" fill="${n === index ? palette.mint : palette.line}"/>`).join('');
  const inner = `<text x="110" y="102" text-anchor="start" fill="${palette.mint}" font-family="Arial,sans-serif" font-size="24" letter-spacing="3">TEST_ONLY • ${String(index + 1).padStart(2, '0')} / ${String(total).padStart(2, '0')}</text>
  ${heading}${body}${motif}
  ${note}${dots}`;
  return baseSvg(width, height, inner, `${ar ? 'AR WHITE' : 'ENGLISH'} • CAROUSEL`);
}
function longPanel(locale, title, heading, points, index, total) {
  const ar = isArabic(locale);
  const width = 1920, height = 1080, sideX = ar ? 1780 : 140;
  const align = 'start';
  const titleSvg = textLines(title, { x: sideX, y: 145, maxChars: ar ? 36 : 54, maxLines: 2, size: 42, lineHeight: 54, fill: palette.mint, locale, anchor: align });
  const headingSvg = textLines(heading, { x: sideX, y: 340, maxChars: ar ? 30 : 42, maxLines: 2, size: 64, lineHeight: 82, fill: palette.cream, locale, anchor: align });
  let y = 505;
  const bullets = points.map((point) => {
    const bullet = textLines(`• ${point}`, { x: sideX, y, maxChars: ar ? 48 : 70, maxLines: 2, size: 36, lineHeight: 54, fill: palette.muted, locale, anchor: align });
    y += 125;
    return bullet;
  }).join('');
  const motif = cupGraphic(470, 760, index * 0.35, 0.62);
  const inner = `<text x="${width - 100}" y="1000" text-anchor="end" fill="${palette.line}" font-family="Arial,sans-serif" font-size="28">${String(index + 1).padStart(2, '0')} / ${String(total).padStart(2, '0')}</text>${titleSvg}${headingSvg}${bullets}${motif}`;
  return baseSvg(width, height, inner, `${ar ? 'AR WHITE' : 'ENGLISH'} • LONG-FORM STORYBOARD • TEST_ONLY`);
}

async function saveSvg(path, svg, written, interruptAfter) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, svg, { flag: 'wx' });
  written.count += 1;
  if (interruptAfter && written.count >= interruptAfter) {
    console.error(`SIMULATED_TEST_ONLY_INTERRUPTION after ${written.count} SVG files`);
    process.exit(75);
  }
}
async function renderPlan(planPath, outputDir, interruptAfter = 0) {
  const plan = JSON.parse(await readFile(planPath, 'utf-8'));
  const root = resolve(outputDir);
  const written = { count: 0 };
  const locales = ['ar_white', 'en'];
  for (const locale of locales) {
    const copy = plan.copy[locale];
    const seconds = Math.min(copy.short_video.target_duration_seconds, plan.preview_seconds ?? copy.short_video.target_duration_seconds);
    const frames = Math.round(seconds * plan.fps);
    for (let frame = 0; frame < frames; frame++) {
      await saveSvg(join(root, locale, 'short', `frame-${String(frame).padStart(5, '0')}.svg`), shortFrame(locale, copy.short_video, frame, frames, plan), written, interruptAfter);
    }
    const slides = copy.carousel.slides;
    for (let i = 0; i < slides.length; i++) {
      await saveSvg(join(root, locale, 'carousel', `slide-${String(i + 1).padStart(2, '0')}.svg`), carouselSlide(locale, slides[i], i, slides.length), written, interruptAfter);
    }
    const long = copy.youtube_long;
    const panels = [
      { heading: long.title, points: [long.opening] },
      ...long.sections.map((section) => ({ heading: section.heading, points: section.talking_points })),
      { heading: long.ending, points: [long.description] }
    ];
    for (let i = 0; i < panels.length; i++) {
      await saveSvg(join(root, locale, 'youtube_long', `panel-${String(i + 1).padStart(2, '0')}.svg`), longPanel(locale, long.title, panels[i].heading, panels[i].points, i, panels.length), written, interruptAfter);
    }
  }
  return written.count;
}

function parseArgs(argv) {
  const values = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) values[argv[i].slice(2)] = argv[++i];
  }
  return values;
}

const args = parseArgs(process.argv.slice(2));
if (args.plan) {
  if (!args.output) throw new Error('--output is required with --plan');
  await renderPlan(args.plan, args.output, Number(args['test-interrupt-after-svg-count'] ?? 0));
} else {
  // Legacy static preview generation, retained for the original package scenes.
  const words = {
    ar: ['مختبر كامبريدج', 'كاميرا لإبريق القهوة', 'من الشبكة الداخلية إلى الويب', 'الشبكة الداخلية', 'الويب'],
    en: ['CAMBRIDGE LAB', 'A camera for coffee', 'From the lab network to the web', 'LAB NETWORK', 'WORLD WIDE WEB']
  };
  const layout = { short: [1080,1920], carousel: [1080,1350], landscape: [1920,1080] };
  function legacyScene(locale, w, h, t) {
    const ar = locale === 'ar';
    const [tag, title, sub, local, web] = words[locale];
    const anchor = ar ? 'end' : 'start';
    const x = ar ? w - 96 : 96;
    const sx = w / 2, sy = h * .49, endX = w - 150;
    const point = 150 + (endX - 150) * ease((t - .9) / 2.8);
    const dash = Math.max(0, ease(t / 1.2));
    const font = ar ? 'Geeza Pro, Noto Sans Arabic, sans-serif' : 'DejaVu Sans';
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
    <defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#213335"/></pattern>
    <radialGradient id="glow"><stop stop-color="#204344"/><stop offset="1" stop-color="#0e1c1e"/></radialGradient></defs>
    <rect width="100%" height="100%" fill="#0e1c1e"/><rect width="100%" height="100%" fill="url(#grid)"/>
    <text x="${x}" y="108" text-anchor="${anchor}" fill="#78e4c3" font-family="${font}" font-size="30">${tag}</text>
    <text x="${x}" y="220" text-anchor="${anchor}" fill="#f6edda" font-family="${font}" font-weight="bold" font-size="70">${title}</text>
    <text x="${x}" y="293" text-anchor="${anchor}" fill="#b6ceca" font-family="${font}" font-size="34">${sub}</text>
    <g transform="translate(${sx} ${sy})"><circle r="165" fill="url(#glow)" stroke="#426665"/><circle r="${135 + 8 * Math.sin(t * 3)}" fill="none" stroke="#4c8782" stroke-dasharray="2 11"/>
    <path d="M-52 -35 H51 L67 53 Q64 80 33 81 H-43 Q-67 81 -69 54Z" fill="#e7d4a4" stroke="#f6edda" stroke-width="4"/><path d="M54 -20H79Q107 -20 100 9Q94 40 67 39" fill="none" stroke="#e7d4a4" stroke-width="13"/><path d="M-59 28 Q-25 ${26+4*Math.sin(t*5)} 7 28 T59 28 L65 55 Q60 76 34 77H-43Q-62 77 -65 52Z" fill="#b9663e"/><path d="M-29 -52 Q-57 -70 -29 -${95+7*Math.sin(t*3)}M12 -52 Q-16 -73 12 -${101+8*Math.cos(t*3)}" fill="none" stroke="#78e4c3" stroke-width="4" stroke-linecap="round"/></g>
    <g transform="translate(0 ${Math.round(h*.77)})" opacity="${dash}"><path d="M150 0H${endX}" stroke="#527f7b" stroke-width="3"/><path d="M150 0H${point}" stroke="#78e4c3" stroke-width="5"/><circle cx="${point}" r="11" fill="#78e4c3"/><circle cx="150" r="17" fill="none" stroke="#78e4c3"/><circle cx="${endX}" r="17" fill="none" stroke="#78e4c3"/><g text-anchor="middle" fill="#f6edda" font-family="DejaVu Sans" font-size="42"><text x="150" y="69">1991</text><text x="${endX}" y="69">1993</text></g><g text-anchor="middle" fill="#b6ceca" font-family="${font}" font-size="25"><text x="150" y="118">${local}</text><text x="${endX}" y="118">${web}</text></g></g></svg>`;
  }
  for (const locale of ['ar', 'en']) {
    for (const [format, [width, height]] of Object.entries(layout)) {
      const dest = join('renders', locale, format);
      await mkdir(dest, { recursive: true });
      const frames = format === 'short' ? 96 : 1;
      for (let frame = 0; frame < frames; frame++) {
        const svg = legacyScene(locale, width, height, frames === 1 ? 3.8 : frame / 24);
        await writeFile(join(dest, `frame-${String(frame).padStart(3, '0')}.svg`), svg);
      }
    }
  }
}
