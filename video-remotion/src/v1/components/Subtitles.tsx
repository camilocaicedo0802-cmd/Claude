import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {NO_SUBS, TITLES} from '../data';
import {clamp, easeOut} from '../helpers';
import {C, OUTFIT} from '../theme';
import {WORDS} from '../timeline';

type Block = {text: string; s: number; e: number};

const covered = new Set(TITLES.flatMap((t) => t.covers));
const inTitle = (s: number) => TITLES.some((t) => s >= t.start - 0.02 && s < t.end);
const hidden = (s: number) => NO_SUBS.some(([a, b]) => s >= a && s < b) || inTitle(s);

// Bloques de 1-4 palabras, se cortan en puntuación, pausas y títulos (estilo.md §2)
const BLOCKS: Block[] = (() => {
  const out: {words: typeof WORDS}[] = [];
  let cur: typeof WORDS = [];
  WORDS.forEach((w, i) => {
    if (covered.has(i) || hidden(w.s)) {
      if (cur.length) out.push({words: cur});
      cur = [];
      return;
    }
    const prev = cur[cur.length - 1];
    if (prev && (w.s - prev.e > 0.35 || cur.length >= 4 || w.seg !== prev.seg)) {
      out.push({words: cur});
      cur = [];
    }
    cur.push(w);
    if (/[,.?]$/.test(w.text)) {
      out.push({words: cur});
      cur = [];
    }
  });
  if (cur.length) out.push({words: cur});
  return out.map((b, i, arr) => {
    const s = b.words[0].s;
    const natural = b.words[b.words.length - 1].e + 0.3;
    const next = arr[i + 1]?.words[0].s ?? natural;
    return {text: b.words.map((w) => w.text).join(' '), s, e: Math.min(natural, next)};
  });
})();

/** Subtítulos pequeños sincronizados palabra a palabra (aparece el bloque al empezar su primera palabra). */
export const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const b = BLOCKS.find((x) => t >= x.s && t < x.e && !hidden(t));
  if (!b) return null;
  const p = interpolate(frame - b.s * fps, [0, 4], [0, 1], {...clamp, easing: easeOut});
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 60,
          top: 950,
          translate: '0 -50%',
          textAlign: 'center',
          fontFamily: OUTFIT,
          fontWeight: 600,
          fontSize: 36,
          letterSpacing: '-0.02em',
          color: C.subWhite,
          textShadow: '0 2px 8px rgba(0,0,0,0.45)',
          opacity: p,
          scale: String(interpolate(p, [0, 1], [0.92, 1])),
        }}
      >
        {b.text}
      </div>
    </AbsoluteFill>
  );
};
