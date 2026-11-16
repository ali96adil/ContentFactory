import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
const words = {
  ar: ['مختبر كامبريدج', 'كاميرا لإبريق القهوة', 'من الشبكة الداخلية إلى الويب', 'الشبكة الداخلية', 'الويب'],
  en: ['CAMBRIDGE LAB', 'A camera for coffee', 'From the lab network to the web', 'LAB NETWORK', 'WORLD WIDE WEB']
};
const ease = (x) => 1 - (1 - Math.max(0, Math.min(1, x))) ** 3;
const layout = { short: [1080,1920], carousel: [1080,1350], landscape: [1920,1080] };
function scene(locale, w, h, t) {
  const ar = locale === 'ar';
  const [tag, title, sub, local, web] = words[locale];
  const anchor = ar ? 'end' : 'start';
  const x = ar ? w - 96 : 96;
  const sx = w / 2, sy = h * .49, endX = w - 150;
  const point = 150 + (endX - 150) * ease((t - .9) / 2.8);
  const dash = Math.max(0, ease(t / 1.2));
  const font = ar ? 'Noto Sans Arabic' : 'DejaVu Sans';
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
  <defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#213335"/></pattern>
  <radialGradient id="glow"><stop stop-color="#204344"/><stop offset="1" stop-color="#0e1c1e"/></radialGradient></defs>
  <rect width="100%" height="100%" fill="#0e1c1e"/><rect width="100%" height="100%" fill="url(#grid)"/>
  <text x="${x}" y="108" text-anchor="${anchor}" fill="#78e4c3" font-family="${font}" font-size="30">${tag}</text>
  <text x="${x}" y="220" text-anchor="${anchor}" fill="#f6edda" font-family="${font}" font-weight="bold" font-size="70">${title}</text>
  <text x="${x}" y="293" text-anchor="${anchor}" fill="#b6ceca" font-family="${font}" font-size="34">${sub}</text>
  <g transform="translate(${sx} ${sy})">
    <circle r="165" fill="url(#glow)" stroke="#426665"/>
    <circle r="${135 + 8 * Math.sin(t * 3)}" fill="none" stroke="#4c8782" stroke-dasharray="2 11"/>
    <path d="M-52 -35 H51 L67 53 Q64 80 33 81 H-43 Q-67 81 -69 54Z" fill="#e7d4a4" stroke="#f6edda" stroke-width="4"/>
    <path d="M54 -20H79Q107 -20 100 9Q94 40 67 39" fill="none" stroke="#e7d4a4" stroke-width="13"/>
    <path d="M-59 28 Q-25 ${26+4*Math.sin(t*5)} 7 28 T59 28 L65 55 Q60 76 34 77H-43Q-62 77 -65 52Z" fill="#b9663e"/>
    <path d="M-29 -52 Q-57 -70 -29 -${95+7*Math.sin(t*3)}M12 -52 Q-16 -73 12 -${101+8*Math.cos(t*3)}" fill="none" stroke="#78e4c3" stroke-width="4" stroke-linecap="round"/>
  </g>
  <g transform="translate(0 ${Math.round(h*.77)})" opacity="${dash}">
    <path d="M150 0H${endX}" stroke="#527f7b" stroke-width="3"/>
    <path d="M150 0H${point}" stroke="#78e4c3" stroke-width="5"/>
    <circle cx="${point}" r="11" fill="#78e4c3"/>
    <circle cx="150" r="17" fill="none" stroke="#78e4c3"/><circle cx="${endX}" r="17" fill="none" stroke="#78e4c3"/>
    <g text-anchor="middle" fill="#f6edda" font-family="DejaVu Sans" font-size="42"><text x="150" y="69">1991</text><text x="${endX}" y="69">1993</text></g>
    <g text-anchor="middle" fill="#b6ceca" font-family="${font}" font-size="25"><text x="150" y="118">${local}</text><text x="${endX}" y="118">${web}</text></g>
  </g>
  </svg>`;
}
for (const locale of ['ar','en']) {
  for (const [format, [width,height]] of Object.entries(layout)) {
    const dest = join('renders', locale, format);
    await mkdir(dest,{recursive:true});
    const frames = format === 'short' ? 96 : 1;
    for (let frame = 0; frame < frames; frame++) {
      const svg = scene(locale, width,height, frames===1 ? 3.8 : frame/24);
      await writeFile(join(dest,`frame-${String(frame).padStart(3,'0')}.svg`),svg);
    }
  }
}
