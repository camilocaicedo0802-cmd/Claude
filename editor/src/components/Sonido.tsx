import { Audio } from "@remotion/media";
import { interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import { at, DURATION, WORDS } from "../lib/timing";
import { SEG_POR_LETRA } from "./Beats";

// Música y efectos sintetizados por scripts/audio_marca.py (propios, sin derechos de terceros).
// Regla (estilo.md §10.14): música ~16 dB bajo la voz; efectos solo en las animaciones importantes,
// variados según lo que hace el gráfico, y nunca dos a la vez.

const MUSICA = 0.1; // ≈ −32 LUFS con la voz a −16 LUFS
const MUSICA_CIERRE = 0.2; // sube al terminar de hablar

// Desfase para que el pico del sonido caiga en el instante del gráfico
const ANTES = { whoosh: 0.35, swish: 0.18, subida: 0.85 } as const;

type Efecto = { t: number; src: string; vol: number; dur?: number; nombre: string };

const texto = (frase: string) => frase.length * SEG_POR_LETRA;

const EFECTOS: Efecto[] = [
  // "reto de 21 días": la cuenta 1→21 con blips ascendentes y un golpe suave al llegar
  { nombre: "21 · blips", t: at("21 días").start, src: "blips", vol: 0.3 },
  { nombre: "21 · impacto", t: at("21 días").start + 0.72, src: "impacto", vol: 0.22 },
  // "3 semanas": entra el título
  { nombre: "3 semanas · whoosh", t: at("3|tres semanas").start - ANTES.whoosh, src: "whoosh", vol: 0.3 },
  // "Luma Body + aceite": dos burbujas, una por etiqueta
  { nombre: "Luma Body · pop", t: at("luma body").start, src: "pop", vol: 0.32 },
  { nombre: "aceite · pop", t: at("nuestro aceite").start + 0.1, src: "pop", vol: 0.32 },
  // "de forma gradual": una nota de marimba por escalón
  { nombre: "gradual · escalones", t: at("gradual").start + 0.1, src: "escalones", vol: 0.3 },
  // "15 minutos": tic-tac mientras se llena el temporizador
  { nombre: "15 min · tictac", t: at("15 minutos").start, src: "tictac", vol: 0.22, dur: 0.95 },
  // "+ guía": entra el título con campanita
  { nombre: "guía · whoosh", t: at("una guía").start - ANTES.whoosh, src: "whoosh", vol: 0.3 },
  { nombre: "guía · campanita", t: at("una guía").start + 0.05, src: "campanita", vol: 0.2 },
  // Lista de la guía: tecleo mientras cada punto se escribe
  { nombre: "guía 1 · tecleo", t: at("qué rutina realizar").start + 0.05, src: "tecleo", vol: 0.22, dur: texto("Qué rutina hacer cada día") },
  { nombre: "guía 2 · tecleo", t: at("cómo usar este producto").start + 0.05, src: "tecleo", vol: 0.22, dur: texto("Cómo usar el producto") },
  { nombre: "guía 3 · tecleo", t: at("cómo avanzar").start + 0.05, src: "tecleo", vol: 0.22, dur: texto("Cómo avanzar según tu tolerancia") },
  // Plan semanal: cada tarjeta entra deslizándose
  { nombre: "semana 1 · tarjeta", t: at("primera semana").start, src: "tarjeta", vol: 0.35 },
  { nombre: "semana 2 · tarjeta", t: at("segunda").start, src: "tarjeta", vol: 0.35 },
  { nombre: "semana 3 · tarjeta", t: at("tercera").start, src: "tarjeta", vol: 0.35 },
  // "perfecto" se tacha con rotulador; "constante" brilla
  { nombre: "perfecto · tachado", t: at("perfecto").end, src: "tachado", vol: 0.3 },
  { nombre: "constante · brillo", t: at("constante").start, src: "brillo", vol: 0.28 },
  // Calendario 3D: nace del dedo y las agujas giran
  { nombre: "calendario · whoosh", t: at("calendario").start + 0.15 - ANTES.whoosh, src: "whoosh", vol: 0.3 },
  { nombre: "calendario · tictac", t: at("calendario").start + 0.15, src: "tictac", vol: 0.22 },
  // "prepara tu espacio": transición suave
  { nombre: "espacio · swish", t: at("el espacio").start - ANTES.swish, src: "swish", vol: 0.28 },
  // "día 1": subida + impacto + campanita (momento final)
  { nombre: "día 1 · subida", t: at("primer día").start - ANTES.subida, src: "subida", vol: 0.25 },
  { nombre: "día 1 · impacto", t: at("primer día").start, src: "impacto", vol: 0.22 },
  { nombre: "día 1 · campanita", t: at("primer día").start + 0.05, src: "campanita", vol: 0.22 },
];

const FIN_VOZ = WORDS[WORDS.length - 1].end;

export const Sonido: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      <Audio
        src={staticFile("audio/musica.wav")}
        volume={(f) => interpolate(f / fps, [FIN_VOZ, Math.min(DURATION, FIN_VOZ + 0.4)], [MUSICA, MUSICA_CIERRE], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
      />
      {EFECTOS.map((e) => (
        <Sequence key={e.nombre} name={`SFX ${e.nombre}`} from={Math.max(0, Math.round(e.t * fps))} durationInFrames={Math.max(1, Math.round((e.dur ?? 2.5) * fps))}>
          <Audio src={staticFile(`audio/${e.src}.wav`)} volume={e.vol} />
        </Sequence>
      ))}
    </>
  );
};
