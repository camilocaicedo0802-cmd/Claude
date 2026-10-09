import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../brand";
import { at, WORDS } from "../lib/timing";

// Vídeo ya editado por scripts/preparar.py: silencios fuera, audio original, recorte 1620×2880 del 4K.
const VIDEO_SRC = "crudo/editado.mp4";
// Centro de la cara en el encuadre (origen del zoom)
const CARA = "52% 43%";
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ZOOM SOLO EN LO IMPORTANTE DICHO CON LA VOZ ALTA (estilo.md §10.12):
// frase clave del guion + pico de volumen ≥ UMBRAL_DB sobre la mediana de su voz.
const FRASES_CLAVE = [
  "reto de 21 días",
  "3|tres semanas",
  "de forma gradual",
  "15 minutos diarios",
  "rutina para ti",
  "no recibiste solamente un producto",
  "una guía",
  "aprenderemos la técnica",
  "aumentaremos el tiempo de trabajo",
  "integraremos diferentes zonas del cuerpo",
  "hacerlo perfecto",
  "ser constante",
  "escuchar tu cuerpo",
  "adecua muy bien el espacio",
  "acompáñame a comenzar",
];
const UMBRAL_DB = 3.5;
const SEPARACION_MIN = 4; // s entre dos zooms: si chocan, gana la frase más fuerte
const ZOOM = 1.12;
const ENTRA = 10; // fotogramas
const SALE = 15; // fotogramas

// Mientras señala el hueco del calendario la cámara no se mueve (el gesto saldría de cuadro)
const SIN_ZOOM = [at("recuerda guardar").start, at("además").start] as const;

const ZOOMS = FRASES_CLAVE.map((f) => {
  const { start, end } = at(f);
  const db = Math.max(...WORDS.filter((w) => w.start >= start && w.end <= end + 0.01).map((w) => w.db ?? 0));
  return { start, end: end + 0.3, db };
})
  .filter((z) => z.db >= UMBRAL_DB && (z.end < SIN_ZOOM[0] || z.start > SIN_ZOOM[1]))
  .sort((a, b) => b.db - a.db)
  .reduce<{ start: number; end: number; db: number }[]>(
    (acc, z) => (acc.some((o) => Math.abs(o.start - z.start) < SEPARACION_MIN) ? acc : [...acc, z]),
    [],
  );

// Cambios de tema → transición suave SIN zoom: destello Durazno + desenfoque breve
const TRANSICIONES = [
  "durante",
  "y podrás hacer",
  "no recibiste",
  "en la primera semana",
  "no necesitas hacerlo",
  "recuerda guardar",
  "además",
  "acompáñame",
].map((p) => at(p).start);

export const Footage: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const escala = ZOOMS.reduce((acc, z) => {
    const a = Math.round(z.start * fps);
    const b = Math.round(z.end * fps);
    const env = interpolate(frame, [a, a + ENTRA, b, b + SALE], [0, 1, 1, 0], { ...CLAMP, easing: Easing.inOut(Easing.cubic) });
    return Math.max(acc, 1 + (ZOOM - 1) * env);
  }, 1);

  let blur = 0;
  let destello = 0;
  for (const tr of TRANSICIONES) {
    const d = frame - Math.round(tr * fps);
    blur = Math.max(blur, interpolate(d, [-4, 0, 5], [0, 8, 0], CLAMP));
    destello = Math.max(destello, interpolate(d, [-2, 0, 5], [0, 0.22, 0], CLAMP));
  }

  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ transform: `scale(${escala})`, transformOrigin: CARA, filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}>
        <Video src={staticFile(VIDEO_SRC)} objectFit="cover" style={{ width: "100%", height: "100%" }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: COLORS.durazno, opacity: destello }} />
    </AbsoluteFill>
  );
};
