import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { readFile } from 'node:fs/promises';

const palettes = {
  editorial: {
    bg: '#f3efe5', panel: '#fffaf0', grid: '#e3dccd', mint: '#12675d',
    cream: '#163d3a', muted: '#365b56', copper: '#ad5735', line: '#76958e'
  },
  spotlight: {
    bg: '#0e1c1e', panel: '#142628', grid: '#203538', mint: '#78e4c3',
    cream: '#f6edda', muted: '#b6ceca', copper: '#b9663e', line: '#527f7b'
  }
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
function textLines(value, { x, y, maxChars, maxLines = 3, size, lineHeight, fill, locale, anchor, opacity = 1, offsetY = 0, weight }) {
  const lines = wrap(value, maxChars, maxLines);
  const dir = isArabic(locale) ? 'rtl' : 'ltr';
  const actualAnchor = anchor ?? 'start';
  const spans = lines.map((line, i) => `<tspan x="${x}" dy="${i === 0 ? 0 : lineHeight}">${esc(line)}</tspan>`).join('');
  return `<text x="${x}" y="${y}" text-anchor="${actualAnchor}" direction="${dir}" unicode-bidi="plaintext" fill="${fill}" opacity="${opacity.toFixed(3)}" transform="translate(0 ${offsetY.toFixed(1)})" font-family="${fontFor(locale)}" font-size="${size}" font-weight="${weight ?? (size >= 48 ? 700 : 400)}">${spans}</text>`;
}
function baseSvg(width, height, inner, label, colors) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
  <defs><pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="${colors.grid}" stroke-width="1"/></pattern>
  <radialGradient id="glow"><stop stop-color="${colors.panel}"/><stop offset="1" stop-color="${colors.bg}"/></radialGradient></defs>
  <rect width="100%" height="100%" fill="${colors.bg}"/><rect width="100%" height="100%" fill="url(#grid)"/>
  ${inner}<text x="${width / 2}" y="${height - 42}" text-anchor="middle" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="22" letter-spacing="3">${esc(label)}</text>
</svg>`;
}
function cupGraphic(cx, cy, t = 0, scale = 1, colors = palettes.spotlight) {
  return `<g transform="translate(${cx} ${cy}) scale(${scale})">
    <circle r="220" fill="url(#glow)" stroke="${colors.line}" stroke-width="3"/>
    <circle r="184" fill="none" stroke="#4c8782" stroke-width="3" stroke-dasharray="3 15"/>
    <path d="M-82 -52 H76 L101 84 Q96 120 50 122 H-63 Q-102 120 -106 84Z" fill="#e7d4a4" stroke="${colors.cream}" stroke-width="6"/>
    <path d="M80 -20H112Q164 -20 151 34Q142 85 99 72" fill="none" stroke="#e7d4a4" stroke-width="18"/>
    <path d="M-94 39 Q-42 ${35 + 5 * Math.sin(t * 3)} 10 39 T93 39 L99 83 Q92 113 51 114H-63Q-90 113 -98 83Z" fill="${colors.copper}"/>
    <path d="M-45 -79 Q-83 -116 -47 -${145 + 12 * Math.sin(t * 2)}M18 -81 Q-15 -118 22 -${151 + 11 * Math.cos(t * 2)}" fill="none" stroke="${colors.mint}" stroke-width="6" stroke-linecap="round"/>
    <circle cx="${152 * Math.cos(t * 0.8)}" cy="${152 * Math.sin(t * 0.8)}" r="10" fill="${colors.mint}"/>
  </g>`;
}

function cueFocus(cx, cy, step, progress, colors, style) {
  const targets = [[0, 38], [134, -10], [0, -177]];
  const [dx, dy] = targets[step % targets.length];
  const appear = ease(Math.min(1, progress / 10));
  const radius = 16 + 36 * appear + 5 * Math.sin(progress / 5);
  if (style === 'spotlight') {
    return `<circle cx="${cx + dx}" cy="${cy + dy}" r="${radius}" fill="none" stroke="${colors.mint}" stroke-width="7" opacity="${0.88 * appear}"/><path d="M${cx + dx - radius * 1.5} ${cy + dy + radius * 1.5}L${cx + dx + radius * 1.5} ${cy + dy - radius * 1.5}" stroke="${colors.cream}" stroke-width="4" opacity="${0.5 * appear}"/>`;
  }
  return `<circle cx="${cx + dx}" cy="${cy + dy}" r="${radius}" fill="none" stroke="${colors.copper}" stroke-width="5" opacity="${0.7 * appear}"/>`;
}

function shortFrame(locale, item, frame, totalFrames, plan) {
  const ar = isArabic(locale);
  const style = plan.visual_direction ?? 'editorial';
  const colors = palettes[style] ?? palettes.editorial;
  const width = 1080, height = 1920, seconds = frame / plan.fps;
  const segmentFrames = totalFrames / item.on_screen_text.length;
  const step = Math.min(item.on_screen_text.length - 1, Math.floor(frame / segmentFrames));
  const progressInStep = Math.max(0, (frame - step * segmentFrames) % segmentFrames);
  const transition = ease(Math.min(1, progressInStep / 10));
  const sideX = ar ? 970 : 110;
  const align = 'start';
  const hook = textLines(item.hook, { x: sideX, y: 280, maxChars: ar ? 24 : 33, maxLines: 3, size: 65, lineHeight: 82, fill: colors.cream, locale, anchor: align, weight: 700 });
  const cx = style === 'editorial' ? 540 + [-48, 0, 48][step] : 540 + [-110, 0, 110][step];
  const cy = style === 'editorial' ? 875 : 850;
  const scale = style === 'editorial' ? 1.12 + 0.055 * Math.sin(seconds * 1.8) : 1.25 + 0.08 * Math.sin(seconds * 2.4);
  const graphic = cupGraphic(cx, cy, seconds, scale, colors);
  const focus = cueFocus(cx, cy, step, progressInStep, colors, style);
  const cardY = 1280 + (1 - transition) * 36;
  const card = style === 'editorial'
    ? `<rect x="72" y="1215" width="936" height="345" rx="28" fill="${colors.panel}" stroke="${colors.line}" stroke-width="3"/><path d="M${ar ? 1000 : 80} 1248V1528" stroke="${colors.copper}" stroke-width="14" stroke-linecap="round"/>`
    : `<path d="M0 1190H1080V1575H0Z" fill="${colors.panel}"/><path d="M0 1190H1080V1225L0 1350Z" fill="${colors.copper}" opacity="0.92"/><path d="M${ar ? 1000 : 80} 1370V1535" stroke="${colors.mint}" stroke-width="12"/>`;
  const cue = textLines(item.on_screen_text[step], { x: sideX, y: cardY + 42, maxChars: ar ? 25 : 34, maxLines: 2, size: 66, lineHeight: 78, fill: colors.cream, locale, anchor: align, opacity: transition, offsetY: 22 * (1 - transition), weight: 700 });
  const cta = textLines(item.call_to_action, { x: sideX, y: cardY + 180, maxChars: ar ? 36 : 46, maxLines: 2, size: 31, lineHeight: 42, fill: colors.muted, locale, anchor: align, opacity: transition, offsetY: 18 * (1 - transition) });
  const progress = 100 + 880 * (frame / Math.max(1, totalFrames - 1));
  const header = `<rect x="72" y="76" width="${ar ? 360 : 390}" height="58" rx="29" fill="${colors.panel}"/><text x="540" y="115" text-anchor="middle" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="25" letter-spacing="3">${ar ? 'معاينة قصيرة' : 'SHORT PREVIEW'} • TEST_ONLY</text>`;
  const inner = `${header}${hook}${graphic}${focus}${card}${cue}${cta}
  <path d="M100 1670H980" stroke="${colors.line}" stroke-width="5"/><path d="M100 1670H${progress}" stroke="${colors.mint}" stroke-width="11" stroke-linecap="round"/>
  <circle cx="${progress}" cy="1670" r="16" fill="${colors.cream}" stroke="${colors.panel}" stroke-width="4"/>`;
  return baseSvg(width, height, inner, `${ar ? 'AR WHITE' : 'ENGLISH'} • ${style.toUpperCase()} • SILENT TEST_ONLY`, colors);
}

function carouselSlide(locale, slide, index, total, carousel, plan) {
  const ar = isArabic(locale);
  const style = plan.visual_direction ?? 'editorial';
  const colors = palettes[style] ?? palettes.editorial;
  const width = 1080, height = 1350;
  const sideX = ar ? 966 : 114;
  const anchor = 'start';
  const isOpening = index === 0;
  const isEnding = index === total - 1;
  const titleY = style === 'spotlight' ? 245 : (isOpening ? 235 : 205);
  const heading = textLines(slide.heading, { x: sideX, y: titleY, maxChars: ar ? 24 : 33, maxLines: 2, size: 62, lineHeight: 76, fill: colors.cream, locale, anchor, weight: 700 });
  const body = textLines(slide.body, { x: sideX, y: titleY + 112, maxChars: ar ? 34 : 47, maxLines: 2, size: 38, lineHeight: 54, fill: colors.muted, locale, anchor });
  const cx = isOpening ? 540 : (index % 2 === 0 ? 680 : 420);
  const cy = isOpening ? 850 : (isEnding ? 850 : 810);
  const scale = isOpening ? 0.92 : (isEnding ? 0.92 : 0.82 + (index === 3 ? 0.12 : 0));
  const motif = cupGraphic(cx, cy, index * 0.75, scale, colors);
  const noteY = style === 'spotlight' ? 1185 : 1115;
  const noteCard = style === 'editorial'
    ? `<rect x="72" y="1060" width="936" height="166" rx="22" fill="${colors.panel}" stroke="${colors.line}" stroke-width="2"/>`
    : `<path d="M0 1050H1080V1240H0Z" fill="${colors.panel}"/><path d="M0 1050H1080V1083L0 1170Z" fill="${colors.copper}"/>`;
  const note = textLines(isEnding ? carousel.call_to_action : slide.visual_note, { x: sideX, y: noteY, maxChars: ar ? 32 : 46, maxLines: 2, size: 31, lineHeight: 42, fill: colors.cream, locale, anchor, weight: 600 });
  const progressWidth = 760;
  const dots = Array.from({ length: total }, (_, n) => {
    const active = n === index;
    const cxDot = 160 + n * (progressWidth / Math.max(1, total - 1));
    const r = active ? 13 : 8;
    return `<circle cx="${cxDot}" cy="1250" r="${r}" fill="${active ? colors.mint : colors.line}"/>`;
  }).join('');
  const number = `<text x="${ar ? 1008 : 72}" y="104" text-anchor="${ar ? 'end' : 'start'}" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="24" letter-spacing="2">TEST_ONLY • ${String(index + 1).padStart(2, '0')} / ${String(total).padStart(2, '0')}</text>`;
  const ribbon = style === 'editorial'
    ? `<path d="M72 150H1008" stroke="${colors.copper}" stroke-width="5"/>`
    : `<path d="M72 150L1008 150L958 164H72Z" fill="${colors.mint}"/>`;
  const inner = `${number}${ribbon}${heading}${body}${motif}${noteCard}${note}${dots}`;
  return baseSvg(width, height, inner, `${ar ? 'AR WHITE' : 'ENGLISH'} • ${style.toUpperCase()} CAROUSEL • TEST_ONLY`, colors);
}

function longPanel(locale, title, heading, points, index, total, plan) {
  const ar = isArabic(locale);
  const style = plan.visual_direction ?? 'editorial';
  const colors = palettes[style] ?? palettes.editorial;
  const width = 1920, height = 1080, sideX = ar ? 1760 : 910;
  const align = 'start';
  const titleSvg = textLines(title, { x: sideX, y: 145, maxChars: ar ? 34 : 38, maxLines: 2, size: 42, lineHeight: 54, fill: colors.mint, locale, anchor: align, weight: 600 });
  const headingSvg = textLines(heading, { x: sideX, y: 310, maxChars: ar ? 35 : 37, maxLines: 3, size: 50, lineHeight: 62, fill: colors.cream, locale, anchor: align, weight: 700 });
  let y = 510;
  const bullets = points.map((point) => {
    const bullet = textLines(`• ${point}`, { x: sideX, y, maxChars: 43, maxLines: 2, size: 34, lineHeight: 50, fill: colors.muted, locale, anchor: align });
    y += 118;
    return bullet;
  }).join('');
  const motif = cupGraphic(460, 760, index * 0.35, 0.7, colors);
  const inner = `<rect x="810" y="72" width="1010" height="818" rx="28" fill="${colors.panel}" stroke="${colors.line}" stroke-width="3" opacity="0.84"/><text x="${width - 100}" y="1000" text-anchor="end" fill="${colors.line}" font-family="Arial,sans-serif" font-size="30">${String(index + 1).padStart(2, '0')} / ${String(total).padStart(2, '0')}</text>${titleSvg}${headingSvg}${bullets}${motif}`;
  return baseSvg(width, height, inner, `${ar ? 'AR WHITE' : 'ENGLISH'} • LONG-FORM STORYBOARD • ${style.toUpperCase()} • TEST_ONLY`, colors);
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
  if (!['editorial', 'spotlight'].includes(plan.visual_direction ?? 'editorial')) {
    throw new Error(`unsupported visual direction: ${plan.visual_direction}`);
  }
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
      await saveSvg(join(root, locale, 'carousel', `slide-${String(i + 1).padStart(2, '0')}.svg`), carouselSlide(locale, slides[i], i, slides.length, copy.carousel, plan), written, interruptAfter);
    }
    const long = copy.youtube_long;
    const panels = [
      { heading: long.title, points: [long.opening] },
      ...long.sections.map((section) => ({ heading: section.heading, points: section.talking_points })),
      { heading: long.ending, points: [long.description] }
    ];
    for (let i = 0; i < panels.length; i++) {
      await saveSvg(join(root, locale, 'youtube_long', `panel-${String(i + 1).padStart(2, '0')}.svg`), longPanel(locale, long.title, panels[i].heading, panels[i].points, i, panels.length, plan), written, interruptAfter);
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
