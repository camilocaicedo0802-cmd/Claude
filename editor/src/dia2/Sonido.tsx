import { Audio } from "@remotion/media";
import { interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import { PREPARA, SEG_POR_LETRA, ZONAS } from "./Beats";
import { APOYO } from "./Footage";
import { at, DURATION, WORDS } from "./timing";

// Música y efectos sintetizados por scripts/dia2/audio_dia2.py (propios, sin derechos de terceros).
// Regla (estilo.md §10.14): música ~16 dB bajo la voz; efectos solo en lo importante, variados y nunca dos a la vez.
const MUSICA = 0.1;
const MUSICA_CIERRE = 0.2;
const ANTES = { whoosh: 0.35, swish: 0.18, subida: 0.85 } as const;

type Efecto = { t: number; src: string; vol: number; dur?: number; nombre: string };

const EFECTOS: Efecto[] = [
  // Punto de partida: el título entra y el pin se clava en su base
  { nombre: "partida · whoosh", t: at("punto de partida").start - ANTES.whoosh, src: "whoosh", vol: 0.28 },
  { nombre: "pin · impacto", t: at("punto de partida").start + 0.05, src: "impacto", vol: 0.2 },
  // "sin filtros", "sin poses perfectas": cada etiqueta se tacha
  { nombre: "filtros · tachado", t: at("sin filtros").start + 0.25, src: "tachado", vol: 0.28 },
  { nombre: "poses · tachado", t: at("sin poses").start + 0.25, src: "tachado", vol: 0.28 },
  // Lista de preparación: tecleo mientras se escribe cada punto
  ...PREPARA.map((p) => ({ nombre: `${p.texto} · tecleo`, t: at(p.frase).start + 0.05, src: "tecleo", vol: 0.2, dur: p.texto.length * SEG_POR_LETRA })),
  // Celular 3D: obturador en "foto" y en cada una de las tres fotos (con el flash)
  { nombre: "foto · obturador", t: at("foto").start, src: "obturador", vol: 0.32 },
  ...APOYO.map((a) => ({ nombre: `${a.label} · obturador`, t: a.desde, src: "obturador", vol: 0.32 })),
  // Medidas: entra el título y la cinta se desenrolla; un pop por zona del cuerpo
  { nombre: "medidas · swish", t: at("tus medidas").start - ANTES.swish, src: "swish", vol: 0.26 },
  ...ZONAS.map((z) => ({ nombre: `${z.texto} · pop`, t: at(z.frase).start, src: "pop", vol: 0.28 })),
  // "cómo avanzas": la línea de progreso sube por escalones
  { nombre: "avance · escalones", t: at("cómo avanzas").start + 0.1, src: "escalones", vol: 0.26 },
  // "¿cómo te sientes?": título
  { nombre: "sientes · whoosh", t: at("cómo sientes").start - ANTES.whoosh, src: "whoosh", vol: 0.28 },
  // Ficha 1-5: blips cuando se rellenan los puntos
  { nombre: "pesados · blips", t: at("pesados").start, src: "blips", vol: 0.24, dur: 0.45 },
  { nombre: "inflamados · blips", t: at("inflamados").start, src: "blips", vol: 0.24, dur: 0.35 },
  // "anota": el lápiz escribe
  { nombre: "anota · tecleo", t: at("anota").start + 0.35, src: "tecleo", vol: 0.18, dur: 1.4 },
  // "21 días": calendario con tic-tac y cuenta 1→21
  { nombre: "calendario · tictac", t: at("al final").start, src: "tictac", vol: 0.2, dur: 1.0 },
  { nombre: "21 · impacto", t: at("21 días").start + 0.6, src: "impacto", vol: 0.2 },
  // "personales": brillo; el candado se cierra
  { nombre: "personales · brillo", t: at("personales").start, src: "brillo", vol: 0.24 },
  { nombre: "candado · tarjeta", t: at("personales").start + 0.5, src: "tarjeta", vol: 0.3 },
  // Cierre: "compararnos" se tacha y "con nadie más" entra con subida + campanita
  { nombre: "comparar · tachado", t: at("compararnos").end - 0.1, src: "tachado", vol: 0.26 },
  { nombre: "nadie más · subida", t: at("con nadie más").start - ANTES.subida, src: "subida", vol: 0.22 },
  { nombre: "nadie más · campanita", t: at("con nadie más").start + 0.05, src: "campanita", vol: 0.2 },
];

const FIN_VOZ = WORDS[WORDS.length - 1].end;

export const Sonido: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      <Audio
        src={staticFile("dia2/audio/musica.wav")}
        volume={(f) => interpolate(f / fps, [FIN_VOZ, Math.min(DURATION, FIN_VOZ + 0.4)], [MUSICA, MUSICA_CIERRE], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
      />
      {EFECTOS.map((e) => (
        <Sequence key={e.nombre} name={`SFX ${e.nombre}`} from={Math.max(0, Math.round(e.t * fps))} durationInFrames={Math.max(1, Math.round((e.dur ?? 2.5) * fps))}>
          <Audio src={staticFile(`dia2/audio/${e.src}.wav`)} volume={e.vol} />
        </Sequence>
      ))}
    </>
  );
};
