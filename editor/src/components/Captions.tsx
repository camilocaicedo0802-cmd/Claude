import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS } from "../brand";
import { pop, Word, WORDS } from "../lib/timing";

// Subtítulos palabra a palabra (estilo.md §3)
const MAX_PALABRAS = 3;
const MAX_CARACTERES = 18;
const SOMBRA = "0 4px 22px rgba(69,89,90,.55), 0 2px 4px rgba(69,89,90,.45)";

type Grupo = { words: Word[]; start: number; end: number };

const agrupar = (words: Word[]): Grupo[] => {
  const grupos: Grupo[] = [];
  let cur: Word[] = [];
  words.forEach((w, i) => {
    cur.push(w);
    const next = words[i + 1];
    const chars = cur.map((x) => x.text).join(" ").length;
    const corta =
      !next ||
      cur.length >= MAX_PALABRAS ||
      /[.,;:?!]$/.test(w.text) ||
      next.start - w.end > 0.25 ||
      chars + next.text.length + 1 > MAX_CARACTERES;
    if (corta) {
      grupos.push({ words: cur, start: cur[0].start, end: w.end });
      cur = [];
    }
  });
  return grupos.map((g, i) => ({
    ...g,
    end: i < grupos.length - 1 ? Math.min(grupos[i + 1].start, g.end + 0.6) : g.end + 0.6,
  }));
};

const GRUPOS = agrupar(WORDS);
const limpiar = (t: string) => t.replace(/[.,;:]+$/, "");

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const grupo = GRUPOS.find((g) => t >= g.start && t < g.end);
  if (!grupo) return null;

  const entrada = interpolate(t, [grupo.start, grupo.start + 4 / fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const activa = grupo.words.reduce((idx, w, i) => (t >= w.start ? i : idx), 0);

  return (
    <div
      style={{
        position: "absolute",
        top: 1390, // sobre el pantalón oscuro: contraste alto y dentro de la zona segura de Reels
        left: 90,
        right: 90,
        textAlign: "center",
        fontFamily: FONTS.body,
        fontWeight: 700,
        fontSize: 76,
        lineHeight: 1.25,
        opacity: entrada,
        transform: `translateY(${(1 - entrada) * 12}px)`,
      }}
    >
      {grupo.words.map((w, i) => {
        const esActiva = i === activa;
        const s = esActiva ? 0.9 + 0.1 * pop(frame, fps, w.start) : 1;
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              margin: "0 8px",
              padding: "2px 18px 8px",
              borderRadius: 18,
              color: esActiva ? COLORS.durazno : COLORS.marfil,
              background: esActiva ? COLORS.petroleo : "transparent",
              textShadow: esActiva ? "none" : SOMBRA,
              transform: `scale(${s})`,
            }}
          >
            {limpiar(w.text)}
          </span>
        );
      })}
    </div>
  );
};
