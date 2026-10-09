import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS } from "../brand";
import { at, WORDS } from "./timing";

// Día 2: el crudo es 1080×1920, se usa entero (sin recorte ni escalado). Cara a ~50 % · 40 %.
const VIDEO_SRC = "dia2/editado.mp4";
const CARA = "50% 40%";
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// ZOOM SOLO EN LO IMPORTANTE DICHO CON LA VOZ ALTA (estilo.md §10.12)
const FRASES_CLAVE = [
  "punto de partida",
  "sin filtros",
  "fondo neutro",
  "ver tu silueta",
  "tomar una foto",
  "llevar un reporte",
  "solo para llevar",
  "algo muy importante",
  "es cómo sientes",
  "si se sienten pesados",
  "cómo va a ser",
  "son personales",
  "sin compararnos",
];
const UMBRAL_DB = 3.5;
const SEPARACION_MIN = 4;
const ZOOM = 1.12;
const ENTRA = 10;
const SALE = 15;

// Toma de apoyo: tres fragmentos cortos, uno por foto, que entran en la palabra que la nombra
export const APOYO = [
  { src: "dia2/apoyo_perfil.mp4", desde: at("de perfil").start, label: "Perfil" },
  { src: "dia2/apoyo_frente.mp4", desde: at("de frente").start, label: "Frente" },
  { src: "dia2/apoyo_espalda.mp4", desde: at("una de espalda").start, label: "Espalda" },
];
export const FIN_APOYO = at("y si quieres").start;

const ZOOMS = FRASES_CLAVE.map((f) => {
  const { start, end } = at(f);
  const db = Math.max(...WORDS.filter((w) => w.start >= start && w.end <= end + 0.01).map((w) => w.db ?? 0));
  return { start, end: Math.min(end + 0.3, start + 2.2), db };
})
  .filter((z) => z.db >= UMBRAL_DB && (z.end + SALE / 30 < APOYO[0].desde || z.start > FIN_APOYO))
  .sort((a, b) => b.db - a.db)
  .reduce<{ start: number; end: number; db: number }[]>(
    (acc, z) => (acc.some((o) => Math.abs(o.start - z.start) < SEPARACION_MIN) ? acc : [...acc, z]),
    [],
  );

// Cambios de tema (los cortes entre tomas) → destello Durazno + desenfoque breve, sin zoom
const TRANSICIONES = ["usa un fondo", "y si quieres", "algo muy importante", "estos cambios"].map((p) => at(p).start);

// Fotos de la toma de apoyo: visor de cámara + destello blanco de flash en cada disparo
const Visor: React.FC<{ n: number; label: string }> = ({ n, label }) => {
  const L = 90;
  const esquina = (x: number, y: number, sx: number, sy: number) => (
    <path key={`${x}-${y}`} d={`M ${x} ${y + sy * L} L ${x} ${y} L ${x + sx * L} ${y}`} stroke={COLORS.marfil} strokeWidth={7} fill="none" strokeLinecap="round" />
  );
  return (
    <AbsoluteFill>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, filter: "drop-shadow(0 2px 8px rgba(69,89,90,.5))" }}>
        {esquina(70, 260, 1, 1)}
        {esquina(1010, 260, -1, 1)}
        {esquina(70, 1600, 1, -1)}
        {esquina(1010, 1600, -1, -1)}
      </svg>
      <div style={{ position: "absolute", top: 1440, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18, padding: "14px 34px 18px", borderRadius: 999, background: COLORS.durazno, boxShadow: "0 10px 30px rgba(69,89,90,.35)" }}>
          <span style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 30, letterSpacing: "0.18em", color: COLORS.salvia }}>FOTO {n}/3</span>
          <span style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 48, color: COLORS.petroleo }}>{label}</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

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
  // Flash de cámara (blanco, fuerte y muy corto) en cada foto
  let flash = 0;
  for (const a of APOYO) {
    const d = frame - Math.round(a.desde * fps);
    flash = Math.max(flash, interpolate(d, [0, 1, 6], [0, 0.85, 0], CLAMP));
  }

  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ transform: `scale(${escala})`, transformOrigin: CARA, filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}>
        <Video src={staticFile(VIDEO_SRC)} objectFit="cover" style={{ width: "100%", height: "100%" }} />
      </AbsoluteFill>
      {APOYO.map((a, i) => {
        const desde = Math.round(a.desde * fps);
        const hasta = Math.round((APOYO[i + 1]?.desde ?? FIN_APOYO) * fps);
        return (
          <Sequence key={a.src} name={`Apoyo ${a.label}`} from={desde} durationInFrames={hasta - desde}>
            <Video src={staticFile(a.src)} muted objectFit="cover" style={{ width: "100%", height: "100%" }} />
            <Visor n={i + 1} label={a.label} />
          </Sequence>
        );
      })}
      <AbsoluteFill style={{ backgroundColor: COLORS.durazno, opacity: destello }} />
      <AbsoluteFill style={{ backgroundColor: "#FFFFFF", opacity: flash }} />
    </AbsoluteFill>
  );
};
