import {Video} from '@remotion/media';
import {AbsoluteFill, Freeze, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {FPS, H, clamp, easeInOut, fr} from './base';
import {DESENFOQUES, PLANOS, caraX} from './data';
import {SEGMENTS, SPEECH} from './timeline';

/** Escala del plano en el instante t (estilo.md §6). */
export const zoomAt = (t: number) => {
  const p = PLANOS.find((q) => t >= q.from && t < q.to) ?? PLANOS[PLANOS.length - 1];
  let s = interpolate(t, [p.from, p.to], [p.s0, p.s1], clamp);
  if (p.push) s *= interpolate(t, [p.push.at, p.push.at + p.push.dur], [1, p.push.to], {...clamp, easing: easeInOut});
  return s;
};

/** Desenfoque de lente de las transiciones (px). */
export const blurAt = (t: number) => {
  let b = 0;
  for (const d of DESENFOQUES) {
    if (d.intro) b = Math.max(b, interpolate(t, [0, d.dur * 0.5], [18, 0], clamp));
    else b = Math.max(b, interpolate(t, [d.at - d.dur / 2, d.at, d.at + d.dur / 2], [0, 18, 0], clamp));
  }
  return b;
};

const starts = SEGMENTS.map((s) => fr(s.start));
const durOf = (i: number) => (i < SEGMENTS.length - 1 ? starts[i + 1] : fr(SPEECH)) - starts[i];

/** La persona hablando, con los cortes de la voz y el zoom de cada plano (anclado abajo, centrado en la cara). */
export const Persona: React.FC<{zoom?: boolean}> = ({zoom = true}) => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const s = zoom ? zoomAt(t) : 1;
  const last = SEGMENTS[SEGMENTS.length - 1];
  return (
    <AbsoluteFill style={{transform: `scale(${s})`, transformOrigin: `${caraX(t)}px ${H}px`}}>
      {SEGMENTS.map((seg, i) => (
        <Sequence key={seg.idx} name={`Toma ${seg.take} · ${seg.idx}`} from={starts[i]} durationInFrames={durOf(i)} premountFor={30}>
          <Video src={staticFile(`clips/g4_${seg.take}.mp4`)} trimBefore={fr(seg.srcIn)} muted objectFit="cover" style={{width: '100%', height: '100%'}} />
        </Sequence>
      ))}
      {/* tras la última palabra se congela el último fotograma (el cierre lo tapa) */}
      <Sequence name="Último fotograma" from={fr(SPEECH)}>
        <Freeze frame={durOf(SEGMENTS.length - 1) - 1}>
          <Video src={staticFile(`clips/g4_${last.take}.mp4`)} trimBefore={fr(last.srcIn)} muted objectFit="cover" style={{width: '100%', height: '100%'}} />
        </Freeze>
      </Sequence>
    </AbsoluteFill>
  );
};
