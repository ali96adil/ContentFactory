import {Circle, Line, makeScene2D, Rect, Txt} from '@motion-canvas/2d';
import {all, createRef, waitFor} from '@motion-canvas/core';

export default makeScene2D(function* (view) {
  const title = createRef<Txt>();
  const subtitle = createRef<Txt>();
  const potLabel = createRef<Txt>();
  const sensorLabel = createRef<Txt>();
  const framesLabel = createRef<Txt>();
  const light = createRef<Circle>();
  const lens = createRef<Circle>();
  const frameA = createRef<Rect>();
  const frameB = createRef<Rect>();
  const frameC = createRef<Rect>();

  view.add(
    <>
      <Rect size={[1080, 1920]} fill="#0e1c1e" />
      <Txt
        ref={title}
        text="من الضوء إلى الصورة"
        position={[0, -670]}
        width={960}
        fontFamily="Geeza Pro, Arial, sans-serif"
        fontSize={76}
        fontWeight={700}
        fill="#f6edda"
        textAlign="center"
        textDirection="rtl"
        opacity={0}
      />
      <Txt
        ref={subtitle}
        text="لقطة كل بضع ثوانٍ تكشف التغيّر"
        position={[0, -520]}
        width={900}
        fontFamily="Geeza Pro, Arial, sans-serif"
        fontSize={40}
        fill="#b6ceca"
        textAlign="center"
        textDirection="rtl"
        opacity={0}
      />

      <Line points={[[-315, 0], [315, 0]]} stroke="#527f7b" lineWidth={7} lineCap="round" />
      <Circle
        ref={lens}
        position={[-320, 0]}
        size={230}
        fill="#183132"
        stroke="#78e4c3"
        lineWidth={9}
        scale={0.6}
      />
      <Circle position={[-320, 0]} size={112} fill="#0e1c1e" stroke="#426665" lineWidth={7} />
      <Circle
        ref={light}
        position={[315, 0]}
        size={34}
        fill="#f6edda"
        shadowColor="#78e4c3"
        shadowBlur={32}
        shadowOffset={0}
      />

      <Rect position={[300, 0]} size={[178, 210]} radius={36} fill="#b9663e" stroke="#f6edda" lineWidth={6} />
      <Rect position={[300, -116]} size={[126, 24]} radius={9} fill="#e7d4a4" />
      <Circle position={[393, -5]} size={102} fill="#0e1c1e" stroke="#e7d4a4" lineWidth={16} />

      <Txt ref={potLabel} text="الإبريق" position={[300, 190]} width={240} fontFamily="Geeza Pro" fontSize={34} fill="#f6edda" textAlign="center" textDirection="rtl" />
      <Txt ref={sensorLabel} text="الحساس" position={[-320, 190]} width={240} fontFamily="Geeza Pro" fontSize={34} fill="#f6edda" textAlign="center" textDirection="rtl" />

      <Rect ref={frameA} position={[-250, 530]} size={[190, 150]} radius={18} fill="#183132" stroke="#426665" lineWidth={5} />
      <Rect ref={frameB} position={[0, 530]} size={[190, 150]} radius={18} fill="#183132" stroke="#426665" lineWidth={5} />
      <Rect ref={frameC} position={[250, 530]} size={[190, 150]} radius={18} fill="#183132" stroke="#426665" lineWidth={5} />
      <Circle position={[-250, 530]} size={56} fill="#4c8782" opacity={0.5} />
      <Circle position={[0, 530]} size={74} fill="#78e4c3" opacity={0.5} />
      <Circle position={[250, 530]} size={94} fill="#e7d4a4" opacity={0.5} />
      <Txt ref={framesLabel} text="صور متتابعة" position={[0, 690]} fontFamily="Geeza Pro" fontSize={32} fill="#b6ceca" textAlign="center" textDirection="rtl" />
    </>,
  );

  yield* all(title().opacity(1, 0.35), subtitle().opacity(1, 0.45), lens().scale(1, 0.45));
  yield* all(
    light().position.x(-320, 1.35),
    lens().scale(1.08, 0.35).to(1, 0.35),
    frameA().stroke('#78e4c3', 0.4),
  );
  yield* all(
    frameB().stroke('#78e4c3', 0.4),
    frameC().stroke('#78e4c3', 0.4),
  );
  yield* waitFor(0.75);

  yield* all(title().opacity(0, 0.2), subtitle().opacity(0, 0.2));
  title().textDirection('ltr');
  subtitle().textDirection('ltr');
  title().fontFamily('Arial, sans-serif');
  subtitle().fontFamily('Arial, sans-serif');
  potLabel().fontFamily('Arial, sans-serif');
  sensorLabel().fontFamily('Arial, sans-serif');
  framesLabel().fontFamily('Arial, sans-serif');
  potLabel().textDirection('ltr');
  sensorLabel().textDirection('ltr');
  framesLabel().textDirection('ltr');
  title().text('From light to image');
  subtitle().text('A frame every few seconds reveals change');
  potLabel().text('Coffee pot');
  sensorLabel().text('Sensor');
  framesLabel().text('Image sequence');
  yield* all(title().opacity(1, 0.35), subtitle().opacity(1, 0.45));
  yield* all(
    light().position.x(315, 1.35),
    lens().scale(1.08, 0.35).to(1, 0.35),
    frameA().stroke('#426665', 0.4),
  );
  yield* all(
    frameB().stroke('#426665', 0.4),
    frameC().stroke('#426665', 0.4),
  );
  yield* waitFor(0.75);
});
