import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../brand";
import { at, WORDS } from "./timing";

// Día 3: crudo 1080×1920 usado entero (sin recorte). Cara a ~50 % · 39 %.
const VIDEO_SRC = "dia3/editado.mp4";
const CARA = "50% 39%";
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ZOOM SOLO EN LO IMPORTANTE DICHO CON LA VOZ ALTA (estilo.md §10.12)
const FRASES_CLAVE = [
  "antes de empezar",
  "revisar muy bien tu piel",
  "sobre el hueso",
  "nunca nunca puede utilizarse",
  "no uses agua",
  "vas a empezar a usar",
  "aumenta solo si",
  "no debe doler",
  "vas a hacer primero una prueba",
  "si duele demasiado",
  "vas a aplicar más|mas aceite",
  "vas a mantener siempre",
  "de arriba hacia abajo",
  "debes apagar",
];
const UMBRAL_DB = 3.5;
const SEPARACION_MIN = 4;
const ZOOM = 1.12;
const ENTRA = 10;
const SALE = 15;

const ZOOMS = FRASES_CLAVE.map((f) => {
  const { start, end } = at(f);
  const db = Math.max(...WORDS.filter((w) => w.start >= start && w.end <= end + 0.01).map((w) => w.db ?? 0));
  return { start, end: Math.min(end + 0.3, start + 2.2), db };
})
  .filter((z) => z.db >= UMBRAL_DB)
  .sort((a, b) => b.db - a.db)
  .reduce<{ start: number; end: number; db: number }[]>(
    (acc, z) => (acc.some((o) => Math.abs(o.start - z.start) < SEPARACION_MIN) ? acc : [...acc, z]),
    [],
  );

// Cada paso del guion empieza con destello Durazno + desenfoque breve (sin zoom)
export const PASOS = {
  uno: at("primero").start,
  dos: at("2|dos").start,
  tres: at("3|tres").start,
  cuatro: at("cuarto").start,
  cinco: at("quinto").start,
  cierre: at("y al terminar").start,
};
const TRANSICIONES = Object.values(PASOS);

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
