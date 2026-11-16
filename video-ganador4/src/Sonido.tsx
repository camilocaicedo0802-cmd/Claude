import {Audio} from '@remotion/media';
import {Sequence, interpolate, staticFile} from 'remotion';
import {FPS, clamp, fr, ws, we} from './base';
import {BLOQUES, LISTA, MUSICA, SFX, Sfx} from './data';
import {SEGMENTS, SPEECH, WORDS} from './timeline';

/** Voz: los mismos cortes que la imagen. */
export const Voz: React.FC = () => (
  <>
    {SEGMENTS.map((s, i) => {
      const from = fr(s.start);
      const to = i < SEGMENTS.length - 1 ? fr(SEGMENTS[i + 1].start) : fr(SPEECH);
      return (
        <Sequence key={s.idx} name={`Voz ${s.take} · ${s.idx}`} from={from} durationInFrames={to - from}>
          <Audio src={staticFile(`clips/g4_${s.take}.mp4`)} trimBefore={fr(s.srcIn)} />
        </Sequence>
      );
    })}
  </>
);

/** Tecleo en los textos (petición del cliente): un toque de tecla por palabra que aparece y por letra en las palabras escritas. */
const tecleo = (): Sfx[] => {
  const out: Sfx[] = [];
  const add = (t: number, vol: number) => {
    if (SFX.some((s) => Math.abs(s.at - t) < 0.1)) return; // no pisar efectos fuertes
    if (out.length && t - out[out.length - 1].at < 0.085) return;
    out.push({src: `sfx/${out.length % 2 ? 'g4_tecla_mec' : 'g4_tecla'}.wav`, at: t, vol, dur: 0.25});
  };
  const ids = new Set<number>();
  for (const b of BLOQUES) for (const l of b.lines) for (const w of l.words) ids.add(w);
  for (const l of LISTA) for (const w of l.words) ids.add(w);
  const typed = new Set(BLOQUES.flatMap((b) => b.lines.filter((l) => l.typed).flatMap((l) => l.words)));
  for (const i of [...ids].sort((a, b) => a - b)) {
    if (typed.has(i)) {
      const n = WORDS[i].text.replace(/[.,]/g, '').length;
      const step = Math.min(0.07, (we(i) - ws(i)) / n);
      for (let k = 0; k < n; k++) add(ws(i) - 0.04 + k * step, 0.17);
    } else add(ws(i) - 0.06, 0.13);
  }
  return out;
};
const TECLEO = tecleo();

export const Sonido: React.FC = () => (
  <>
    <Voz />
    <Audio
      name="Música · ANBR – Quantum"
      src={staticFile(MUSICA.src)}
      volume={(f) => {
        const t = f / FPS;
        const corte = interpolate(t, [MUSICA.corte.from - 0.05, MUSICA.corte.from, MUSICA.corte.to, MUSICA.corte.to + 0.25], [1, 0, 0, 1], clamp);
        const fin = interpolate(t, [MUSICA.fadeOut, MUSICA.fadeOut + 1.0], [1, 0], clamp);
        const entrada = interpolate(t, [0, 0.25], [0.4, 1], clamp);
        return MUSICA.vol * corte * fin * entrada;
      }}
    />
    {[...SFX, ...TECLEO].map((s, i) => (
      <Sequence key={i} name={`SFX ${s.src}`} from={Math.max(0, fr(s.at))} durationInFrames={fr(s.dur ?? 1.2)}>
        <Audio src={staticFile(s.src)} volume={s.vol} trimBefore={fr(s.trim ?? 0)} />
      </Sequence>
    ))}
  </>
);
