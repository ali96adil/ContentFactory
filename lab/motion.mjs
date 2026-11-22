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
  },
  fieldnotes: {
    bg: '#f2efe6', panel: '#fffdf7', grid: '#ddd8c9', mint: '#147b78',
    cream: '#182f48', muted: '#41586b', copper: '#d35d3f', line: '#91aaa6'
  },
  typeplay: {
    bg: '#f3d868', panel: '#fff8df', grid: '#dfc759', mint: '#194f49',
    cream: '#24213b', muted: '#393651', copper: '#dc593d', line: '#766b48'
  },
  gallery: {
    bg: '#273ba7', panel: '#f3f0d7', grid: '#3449b6', mint: '#ddf16a',
    cream: '#fff5df', muted: '#e2e4fa', copper: '#ff775b', line: '#8592df'
  }
};
const newDirections = new Set(['fieldnotes', 'typeplay', 'gallery']);
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

function directionBackground(width, height, colors, direction) {
  const grid = direction === 'fieldnotes'
    ? `<path d="M0 96H${width}M0 192H${width}M96 0V${height}M192 0V${height}" stroke="${colors.grid}" stroke-width="1"/>`
    : direction === 'typeplay'
      ? `<path d="M0 0H${width}V${height}H0Z" fill="${colors.bg}"/><path d="M${width * .82} 0H${width}V${height}H${width * .94}Z" fill="${colors.grid}" opacity=".62"/>`
      : `<path d="M0 0H${width}V${height}H0Z" fill="${colors.bg}"/><circle cx="${width * .82}" cy="${height * .18}" r="${Math.min(width, height) * .29}" fill="${colors.grid}" opacity=".65"/>`;
  return `<rect width="100%" height="100%" fill="${colors.bg}"/>${grid}`;
}

function lineIllustration(cx, cy, scale, t, colors, variant = 0, small = false) {
  const s = scale;
  const wobble = Math.sin(t * 2.2 + variant) * 9;
  const cup = `<g transform="translate(${cx} ${cy}) scale(${s})">
    <path d="M-110 -62H58L78 68Q72 108 36 112H-78Q-112 106 -118 70Z" fill="${colors.panel}" stroke="${colors.cream}" stroke-width="7"/>
    <path d="M66 -30H105Q151 -30 140 22Q132 71 77 61" fill="none" stroke="${colors.panel}" stroke-width="17"/>
    <path d="M-106 22Q-30 ${18 + wobble} 75 22L78 66Q73 100 38 103H-75Q-104 100 -111 66Z" fill="${colors.copper}"/>
    <path d="M-42 -92C-82 -136 -38 -158 -50 -193M24 -94C-6 -128 32 -154 17 -184" fill="none" stroke="${colors.mint}" stroke-width="7" stroke-linecap="round"/>
  </g>`;
  if (small) return cup;
  if (variant % 3 === 0) return `${cup}<circle cx="${cx}" cy="${cy}" r="${220 * s}" fill="none" stroke="${colors.line}" stroke-width="3" stroke-dasharray="5 13"/><path d="M${cx - 270 * s} ${cy + 170 * s}H${cx - 160 * s}V${cy + 125 * s}" fill="none" stroke="${colors.mint}" stroke-width="4"/><circle cx="${cx - 270 * s}" cy="${cy + 170 * s}" r="7" fill="${colors.copper}"/>`;
  if (variant % 3 === 1) return `${cup}<path d="M${cx + 125 * s} ${cy - 140 * s}H${cx + 280 * s}M${cx + 205 * s} ${cy - 160 * s}V${cy - 120 * s}M${cx + 125 * s} ${cy + 150 * s}H${cx + 270 * s}" fill="none" stroke="${colors.mint}" stroke-width="5"/><circle cx="${cx + 280 * s}" cy="${cy - 140 * s}" r="10" fill="${colors.copper}"/>`;
  return `${cup}<path d="M${cx - 265 * s} ${cy - 175 * s}H${cx - 135 * s}V${cy - 130 * s}M${cx + 140 * s} ${cy + 160 * s}H${cx + 265 * s}" fill="none" stroke="${colors.copper}" stroke-width="5"/>`;
}

function fieldNoteGraphic(cx,cy,scale,t,colors,step) {
  if (step === 0 || step === 4) return lineIllustration(cx,cy,scale,t,colors,step);
  if (step === 1) return '<rect x="'+(cx-230*scale)+'" y="'+(cy-145*scale)+'" width="'+(180*scale)+'" height="'+(290*scale)+'" rx="18" fill="'+colors.copper+'"/><rect x="'+(cx-10*scale)+'" y="'+(cy-145*scale)+'" width="'+(180*scale)+'" height="'+(290*scale)+'" rx="18" fill="'+colors.mint+'"/><path d="M'+(cx-250*scale)+' '+(cy+190*scale)+'H'+(cx+240*scale)+'M'+(cx-250*scale)+' '+(cy+220*scale)+'H'+(cx+120*scale)+'" stroke="'+colors.cream+'" stroke-width="5"/>';
  if (step === 2) return '<path d="M'+(cx-260*scale)+' '+(cy-150*scale)+'L'+(cx-45*scale)+' '+cy+'L'+(cx-260*scale)+' '+(cy+150*scale)+'Z" fill="'+colors.copper+'" opacity=".8"/><path d="M'+(cx-45*scale)+' '+cy+'L'+(cx+250*scale)+' '+(cy-200*scale)+'M'+(cx-45*scale)+' '+cy+'H'+(cx+270*scale)+'M'+(cx-45*scale)+' '+cy+'L'+(cx+250*scale)+' '+(cy+200*scale)+'" stroke="'+colors.mint+'" stroke-width="8"/><circle cx="'+(cx-45*scale)+'" cy="'+cy+'" r="18" fill="'+colors.cream+'"/>';
  return '<path d="M'+(cx-180*scale)+' '+(cy+180*scale)+'C'+(cx-280*scale)+' '+(cy+40*scale)+' '+(cx-70*scale)+' '+(cy+20*scale)+' '+(cx-170*scale)+' '+(cy-120*scale)+'M'+cx+' '+(cy+180*scale)+'C'+(cx-90*scale)+' '+(cy+40*scale)+' '+(cx+120*scale)+' '+(cy+10*scale)+' '+(cx+20*scale)+' '+(cy-150*scale)+'M'+(cx+180*scale)+' '+(cy+180*scale)+'C'+(cx+80*scale)+' '+(cy+45*scale)+' '+(cx+280*scale)+' '+(cy+10*scale)+' '+(cx+190*scale)+' '+(cy-120*scale)+'" fill="none" stroke="'+colors.mint+'" stroke-width="13" stroke-linecap="round"/><path d="M'+(cx-250*scale)+' '+(cy+220*scale)+'H'+(cx+250*scale)+'" stroke="'+colors.line+'" stroke-width="5"/>';
}

function directionShortFrame(locale, item, frame, totalFrames, plan) {
  const ar = isArabic(locale), direction = plan.visual_direction, colors = palettes[direction];
  const seconds = frame / plan.fps, width = 1080, height = 1920;
  const segmentFrames = totalFrames / item.on_screen_text.length;
  const step = Math.min(item.on_screen_text.length - 1, Math.floor(frame / segmentFrames));
  const progressInStep = Math.max(0, (frame - step * segmentFrames) % segmentFrames);
  const enter = ease(Math.min(1, progressInStep / 11));
  const sideX = ar ? 970 : 110, anchor = 'start';
  const topLabel = ar ? 'ملاحظات بصرية • TEST_ONLY' : 'VISUAL NOTES • TEST_ONLY';
  let scene = '';
  if (direction === 'fieldnotes') {
    const cx = 540 + [-55, 0, 55][step], cy = 900, zoom = 1.05 + .025 * Math.sin(seconds * 1.5);
    scene = `${directionBackground(width,height,colors,direction)}<path d="M72 170H1008" stroke="${colors.cream}" stroke-width="3"/><circle cx="${cx}" cy="${cy}" r="330" fill="${colors.panel}" stroke="${colors.line}" stroke-width="3"/>${fieldNoteGraphic(cx,cy,zoom,seconds,colors,step)}<path d="M120 1260H960" stroke="${colors.line}" stroke-width="3"/><text x="110" y="1190" text-anchor="start" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="24" letter-spacing="3">FIELD NOTE 0${step + 1}</text>`;
  } else if (direction === 'typeplay') {
    const slideX = ((seconds * 230) % 1240) - 180;
    const cx = ar ? 170 : 910, cy = 1080, scale = .42 + .03 * Math.sin(seconds * 2);
    scene = `${directionBackground(width,height,colors,direction)}<path d="M${slideX} 720L${slideX + 260} 650L${slideX + 500} 1160L${slideX + 240} 1230Z" fill="${colors.copper}"/><circle cx="${ar ? 180 : 900}" cy="1020" r="240" fill="${colors.panel}"/><path d="M0 1460H1080V1690H0Z" fill="${colors.cream}"/>${lineIllustration(cx,cy,scale,seconds,colors,step,true)}<text x="${sideX}" y="1270" text-anchor="${anchor}" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="24" letter-spacing="3">OBSERVATION / 0${step + 1}</text>`;
  } else {
    const cx = (ar ? 250 : 830) + Math.sin(seconds * 1.5) * 115, cy = 890 + Math.cos(seconds * 1.3) * 48;
    scene = `${directionBackground(width,height,colors,direction)}<path d="M0 1120Q260 1010 520 1135T1080 1100V1680H0Z" fill="${colors.panel}"/><ellipse cx="${cx}" cy="${cy}" rx="350" ry="300" fill="${colors.copper}"/><ellipse cx="${cx}" cy="${cy}" rx="270" ry="220" fill="${colors.mint}" opacity=".78"/>${lineIllustration(cx,cy,.42 + .02 * Math.sin(seconds * 1.7),seconds,colors,step,true)}<path d="M70 1540H1010" stroke="${colors.line}" stroke-width="4"/>`;
  }
  const hookSize = direction === 'typeplay' ? 70 : 70;
  const hook = textLines(item.hook,{x:sideX,y:direction === 'gallery'?245:260,maxChars:ar?20:22,maxLines:4,size:hookSize,lineHeight:80,fill:colors.cream,locale,anchor,weight:700});
  const cueY = direction === 'typeplay' ? 1510 : 1400;
  const cue = textLines(item.on_screen_text[step],{x:sideX,y:cueY,maxChars:ar?20:22,maxLines:2,size:62,lineHeight:76,fill:direction==='gallery'?colors.bg:(direction==='typeplay'?colors.panel:colors.cream),locale,anchor,opacity:enter,offsetY:28*(1-enter),weight:700});
  const cta = textLines(item.call_to_action,{x:sideX,y:cueY+112,maxChars:ar?30:34,maxLines:2,size:32,lineHeight:43,fill:direction==='gallery'?colors.bg:(direction==='typeplay'?colors.panel:colors.muted),locale,anchor,opacity:enter,offsetY:18*(1-enter)});
  const progress = 100 + 880 * frame / Math.max(1,totalFrames-1);
  const header = `<text x="110" y="120" text-anchor="start" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="25" letter-spacing="3">${esc(topLabel)}</text>`;
  const footer = direction === 'typeplay' ? '' : `<path d="M100 1780H980" stroke="${colors.line}" stroke-width="4"/><path d="M100 1780H${progress}" stroke="${colors.mint}" stroke-width="10"/><circle cx="${progress}" cy="1780" r="14" fill="${colors.copper}"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">${scene}${header}${hook}${cue}${cta}${footer}<text x="540" y="1885" text-anchor="middle" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="20" letter-spacing="2">${ar?'AR WHITE':'ENGLISH'} • ${direction.toUpperCase()} • TEST_ONLY</text></svg>`;
}

function directionCarouselSlide(locale, slide, index, total, carousel, plan) {
  const ar = isArabic(locale), direction = plan.visual_direction, colors = palettes[direction];
  const width=1080,height=1350, sideX=ar?970:110, anchor='start';
  const bg=directionBackground(width,height,colors,direction);
  const headingSize = direction==='typeplay'?74:68;
  let composition='';
  if(direction==='fieldnotes') {
    const cx=index%2===0?730:360, cy=810, scale=index===0||index===total-1?.63:.54;
    composition=`<path d="M72 160H1008" stroke="${colors.cream}" stroke-width="3"/><rect x="72" y="620" width="936" height="390" rx="18" fill="${colors.panel}" stroke="${colors.line}" stroke-width="3"/>${fieldNoteGraphic(cx,cy,scale,index*.8,colors,index)}<text x="110" y="1090" text-anchor="start" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="23" letter-spacing="3">FIELD NOTE 0${index+1} / 0${total}</text>`;
  } else if(direction==='typeplay') {
    const cx=ar?180:900, cy=820, scale=index===0?.52:.4;
    const motif=index===0||index===total-1
      ? `<circle cx="${cx}" cy="${cy}" r="170" fill="${colors.panel}"/>${lineIllustration(cx,cy,scale,index*.7,colors,index,true)}`
      : `<circle cx="${cx}" cy="${cy}" r="140" fill="${colors.panel}"/><path d="M${cx-230} ${cy+92}Q${cx-120} ${cy-45} ${cx} ${cy+42}T${cx+230} ${cy-12}" fill="none" stroke="${colors.mint}" stroke-width="18" stroke-linecap="round"/><circle cx="${cx-170}" cy="${cy-115}" r="14" fill="${colors.copper}"/><circle cx="${cx+180}" cy="${cy+130}" r="10" fill="${colors.copper}"/>`;
    composition=`<path d="M0 690H1080V1030H0Z" fill="${colors.cream}"/><path d="M${index%2?450:0} 700L${index%2?730:280} 700L${index%2?520:70} 1030H${index%2?240:0}Z" fill="${colors.copper}"/>${motif}<text x="110" y="1110" text-anchor="start" fill="${colors.cream}" font-family="Arial,sans-serif" font-size="24" letter-spacing="3">OBSERVATION 0${index+1}</text>`;
  } else {
    const cx=ar?265:815, cy=900, radius=index===0||index===total-1?238:190;
    composition=`<circle cx="${cx}" cy="${cy}" r="${radius+105}" fill="${colors.panel}"/><circle cx="${cx}" cy="${cy}" r="${radius+55}" fill="${colors.copper}"/><circle cx="${cx}" cy="${cy}" r="${radius}" fill="${colors.mint}"/>${lineIllustration(cx,cy,index===0?.62:.48,index*.9,colors,index,true)}<path d="M72 1090H1008" stroke="${colors.mint}" stroke-width="4"/>`;
  }
  const heading=textLines(slide.heading,{x:sideX,y:direction==='gallery'?260:245,maxChars:direction==='typeplay'?(ar?16:18):(ar?20:26),maxLines:2,size:headingSize,lineHeight:85,fill:colors.cream,locale,anchor,weight:700});
  const body=textLines(slide.body,{x:sideX,y:420,maxChars:ar?30:43,maxLines:2,size:42,lineHeight:57,fill:colors.muted,locale,anchor});
  const note=textLines(index===total-1?carousel.call_to_action:slide.visual_note,{x:sideX,y:direction==='fieldnotes'?1170:1195,maxChars:ar?30:34,maxLines:2,size:32,lineHeight:44,fill:colors.cream,locale,anchor,weight:600});
  const marker=`<text x="110" y="110" text-anchor="start" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="25" letter-spacing="3">${String(index+1).padStart(2,'0')} / ${String(total).padStart(2,'0')} • TEST_ONLY</text>`;
  const stepLine=`<path d="M110 1270H970" stroke="${colors.line}" stroke-width="4"/><path d="M110 1270H${110+860*(index+1)/total}" stroke="${colors.copper}" stroke-width="10"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">${bg}${composition}${marker}${heading}${body}${note}${stepLine}<text x="540" y="1330" text-anchor="middle" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="18">${direction.toUpperCase()} • TEST_ONLY</text></svg>`;
}

function directionLongPanel(locale,title,heading,points,index,total,plan) {
  const ar=isArabic(locale),direction=plan.visual_direction,colors=palettes[direction],width=1920,height=1080;
  const sideX=ar?1770:(direction==='fieldnotes'?850:(direction==='gallery'?960:150)),anchor='start';
  const bg=directionBackground(width,height,colors,direction);
  let art='';
  if(direction==='fieldnotes') art=`<rect x="70" y="75" width="700" height="900" rx="24" fill="${colors.panel}" stroke="${colors.line}" stroke-width="4"/><path d="M125 820H700M125 850H420M125 880H650" stroke="${colors.line}" stroke-width="4"/>${lineIllustration(420,470,.92,index*.5,colors,index)}`;
  else if(direction==='typeplay') {
    const artMotif=index===0||index===total-1?lineIllustration(360,530,.52,index*.6,colors,index,true):`<path d="M90 650Q220 310 360 650T650 650" fill="none" stroke="${colors.mint}" stroke-width="28"/><circle cx="200" cy="320" r="42" fill="${colors.copper}"/><circle cx="520" cy="770" r="26" fill="${colors.copper}"/>`;
    art=`<path d="M0 0H720V1080H0Z" fill="${colors.cream}"/><circle cx="360" cy="530" r="230" fill="${colors.copper}"/><circle cx="360" cy="530" r="165" fill="${colors.panel}"/>${artMotif}`;
  }
  else art=`<circle cx="390" cy="500" r="470" fill="${colors.panel}"/><circle cx="390" cy="500" r="355" fill="${colors.copper}"/><circle cx="390" cy="500" r="260" fill="${colors.mint}"/>${lineIllustration(390,500,.4,index*.6,colors,index,true)}`;
  const textX=direction==='typeplay'&&!ar?820:sideX;
  const titleSvg=textLines(title,{x:textX,y:145,maxChars:ar?30:32,maxLines:2,size:45,lineHeight:58,fill:colors.mint,locale,anchor,weight:600});
  const headingSvg=textLines(heading,{x:textX,y:320,maxChars:ar?30:27,maxLines:3,size:62,lineHeight:76,fill:colors.cream,locale,anchor,weight:700});
  let y=560;
  const bullets=points.map(point=>{const row=textLines(`• ${point}`,{x:textX,y,maxChars:ar?36:38,maxLines:2,size:36,lineHeight:49,fill:colors.muted,locale,anchor});y+=120;return row;}).join('');
  const progress=`<text x="${ar?1820:100}" y="1010" text-anchor="${anchor}" fill="${colors.line}" font-family="Arial,sans-serif" font-size="28">${String(index+1).padStart(2,'0')} / ${String(total).padStart(2,'0')} • TEST_ONLY</text>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">${bg}${art}${titleSvg}${headingSvg}${bullets}${progress}<text x="960" y="1060" text-anchor="middle" fill="${colors.mint}" font-family="Arial,sans-serif" font-size="20">${direction.toUpperCase()} • STORYBOARD • TEST_ONLY</text></svg>`;
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
  if (newDirections.has(plan.visual_direction)) return directionShortFrame(locale,item,frame,totalFrames,plan);
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
  if (newDirections.has(plan.visual_direction)) return directionCarouselSlide(locale,slide,index,total,carousel,plan);
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
  if (newDirections.has(plan.visual_direction)) return directionLongPanel(locale,title,heading,points,index,total,plan);
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
  if (!['editorial', 'spotlight', ...newDirections].includes(plan.visual_direction ?? 'editorial')) {
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
