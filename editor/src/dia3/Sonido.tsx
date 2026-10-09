import { Audio } from "@remotion/media";
import { interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import { EVITA, SI_DUELE } from "./Beats";
import { PASOS } from "./Footage";
import { at, DURATION, WORDS } from "./timing";

// Música y efectos sintetizados por scripts/dia3/audio_dia3.py (propios, sin derechos de terceros).
// Regla (estilo.md §10.14): música ~16 dB bajo la voz; efectos solo en lo importante, variados y nunca dos a la vez.
const MUSICA = 0.1;
const MUSICA_CIERRE = 0.2;
const ANTES = { whoosh: 0.35, swish: 0.18, subida: 0.85 } as const;

type Efecto = { t: number; src: string; vol: number; dur?: number; nombre: string };

const EFECTOS: Efecto[] = [
  // Intro: entra "uso seguro"
  { nombre: "uso seguro · whoosh", t: at("instrucciones").start - ANTES.whoosh, src: "whoosh", vol: 0.28 },
  // Cada número de paso entra con una tarjeta
  ...[PASOS.uno, PASOS.dos, PASOS.tres, PASOS.cuatro, PASOS.cinco].map((t, i) => ({ nombre: `paso ${i + 1} · tarjeta`, t, src: "tarjeta", vol: 0.3 })),
  // 1 · la lupa recorre (swish) y cada zona prohibida entra con un pop
  { nombre: "lupa · swish", t: at("revisar").start - ANTES.swish + 0.2, src: "swish", vol: 0.24 },
  ...EVITA.map((e) => ({ nombre: `${e.texto} · pop`, t: at(e.frase).start, src: "pop", vol: 0.26 })),
  // 2 · "piel seca" se tacha; el aceite brilla al verterse; la barra de deslizamiento sube
  { nombre: "piel seca · tachado", t: at("piel seca").end, src: "tachado", vol: 0.28 },
  { nombre: "aceite · brillo", t: at("el aceite").start, src: "brillo", vol: 0.22 },
  { nombre: "desliza · escalones", t: at("entre más|mas aceite").start + 0.2, src: "escalones", vol: 0.24 },
  { nombre: "agua · impacto", t: at("agua").end, src: "impacto", vol: 0.18 },
  { nombre: "aceite masajes · campanita", t: at("un aceite para masajes").start + 0.1, src: "campanita", vol: 0.18 },
  // 3 · la perilla sube de nivel con blips
  { nombre: "intensidad · blips", t: at("aumenta").start + 0.2, src: "blips", vol: 0.22, dur: 0.6 },
  // 4 · los tres pasos de "si duele" (pop, pop, pop)
  ...SI_DUELE.map((s) => ({ nombre: `${s.texto} · pop`, t: at(s.frase).start, src: "pop", vol: 0.26 })),
  // 5 · "quieto" se tacha; las flechas entran con swish
  { nombre: "quieto · tachado", t: at("quieto").end, src: "tachado", vol: 0.26 },
  { nombre: "abajo · swish", t: at("de arriba hacia abajo").start - ANTES.swish, src: "swish", vol: 0.24 },
  { nombre: "círculos · whoosh", t: at("círculos").start - ANTES.whoosh, src: "whoosh", vol: 0.24 },
  // Cierre: subida, el botón se apaga (impacto suave) y brilla al limpiar
  { nombre: "cierre · subida", t: at("apagar").start - ANTES.subida, src: "subida", vol: 0.2 },
  { nombre: "apagar · impacto", t: at("apagar").start, src: "impacto", vol: 0.2 },
  { nombre: "limpiar · brillo", t: at("limpiar").start, src: "brillo", vol: 0.24 },
];

const FIN_VOZ = WORDS[WORDS.length - 1].end;

export const Sonido: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      <Audio
        src={staticFile("dia3/audio/musica.wav")}
        volume={(f) => interpolate(f / fps, [FIN_VOZ, Math.min(DURATION, FIN_VOZ + 0.4)], [MUSICA, MUSICA_CIERRE], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
      />
      {EFECTOS.map((e) => (
        <Sequence key={e.nombre} name={`SFX ${e.nombre}`} from={Math.max(0, Math.round(e.t * fps))} durationInFrames={Math.max(1, Math.round((e.dur ?? 2.5) * fps))}>
          <Audio src={staticFile(`dia3/audio/${e.src}.wav`)} volume={e.vol} />
        </Sequence>
      ))}
    </>
  );
};
