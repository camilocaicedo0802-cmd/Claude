// OPCIÓN B · formato «clase horizontal»: el plano horizontal va en una ventana y las tipografías y recursos
// viven ARRIBA (titulares, palabra clave gigante, notificación) y ABAJO (subtítulos, tarjetas, gráficos).
import { Easing } from "remotion";
import { keys, lerp, ramp } from "../anim";
import cabezaJson from "../data/cabeza.json";
import { BEHIND } from "../edit/captions";
import { ZOOMS } from "../edit/zooms";
import { W } from "../theme";
import { Segment, T, seg } from "../timeline";

/** Coronilla de Armando en cada momento «pop»: [t local, y (0–1 de la altura del plano)]. scripts/prep/cabeza_tope.py */
const CABEZA = cabezaJson as unknown as Record<string, [number, number][]>;

/** Ventana del vídeo (16:10) dentro del lienzo 1080×1920. */
export const WIN = { x: 28, y: 446, w: 1024, h: 640, r: 32 };
/** En los momentos de palabra clave gigante la ventana baja para dejarle sitio arriba. */
export const NUDGE = 92;

// Zona inferior (entre la ventana y la interfaz de Instagram): 1086 → ≈1545
export const LOWER_CY = 1312; // centro de los bloques de subtítulos
export const KEY_CY = 1356; // fila de continuación mientras la ventana está bajada
export const LABEL_CY = 1126; // rótulo pequeño encima de fichas y gráficos
export const TILES_CY = 1348;

// Zona superior (bajo la cabecera de Instagram): 236 → 446
export const HEAD_TOP = 246;

const io = Easing.inOut(Easing.cubic);
const S = (id: string) => seg(id);

/**
 * Momentos «pop»: la ventana baja, el plano se abre y la cabeza de Armando sobresale por encima de la ventana,
 * tapando parte de la palabra gigante que queda detrás (texto detrás del sujeto, en formato horizontal).
 * Los tiempos caben dentro de los recortes con transparencia de src/data/fg.json.
 */
type Pop = { seg: string; in: [number, number] | null; out: [number, number] };

/** Tamaño de la palabra gigante: lo más grande que cabe a lo ancho, con tope. */
export const keywordPx = (text: string) => Math.min(318, (W - 150) / (0.535 * text.length));
/** Cuánto sobresale la cabeza por encima de la ventana: proporcional a la palabra, para que nunca la tape de más. */
const popOut = (segId: string) => {
  const b = BEHIND.find((x) => x.seg === segId);
  return 0.24 * keywordPx(b ? b.big.map((w) => w.text).join(" ") : "xxxx");
};
export const POPS: Pop[] = [
  { seg: "s01_hook", in: null, out: [T("s01", 6) - 0.24, T("s01", 6) - 0.02] },
  { seg: "s05_decisiones", in: [S("s05").start + 0.03, S("s05").start + 0.5], out: [T("s05", 7) - 0.24, T("s05", 7) - 0.02] },
  { seg: "s06_bits", in: [S("s06").cuts[0] + 0.1, S("s06").cuts[0] + 0.58], out: [T("s06", 17) - 0.22, T("s06", 17)] },
  { seg: "s10_conflicto", in: [T("s10", 7) - 0.1, T("s10", 7) + 0.34], out: [S("s11").start, S("s11").start + 0.3] },
  { seg: "s13_repitas", in: null, out: [T("s13", 8) - 0.24, T("s13", 8) - 0.02] },
];

const popValue = (p: Pop, t: number) => {
  if (t < S(p.seg).start) return 0;
  const a = p.in ? ramp(t, p.in[0], p.in[1] - p.in[0], io) : 1;
  const b = 1 - ramp(t, p.out[0], p.out[1] - p.out[0], io);
  return a * b;
};

/** 0–1: cuánto ha bajado la ventana. */
export const nudge = (t: number) => Math.max(0, ...POPS.map((p) => popValue(p, t)));
export const winY = (t: number) => WIN.y + NUDGE * nudge(t);
/** 0–1: cuánto sobresale la cabeza en esta toma. */
export const popOf = (s: Segment, t: number) => {
  const p = POPS.find((x) => x.seg === s.id);
  return p ? popValue(p, t) : 0;
};

// ───────── Cámara dentro de la ventana ─────────
/** Zoom base sobre el «cover» de la ventana: plano medio corto. */
export const BASE_ZOOM = 1.6;
/** Los zooms del montaje vertical (edit/zooms.ts) se trasladan a multiplicadores de ventana. */
const mapZ = (v: number) => (v < 0.8 ? 0.88 + (v - 0.66) * 0.5 : 0.94 + (v - 0.92) * 0.9);
export const ZOOMS_H: Record<string, [number, number][]> = Object.fromEntries(Object.entries(ZOOMS).map(([id, ks]) => [id, ks.map(([t, v]) => [t, mapZ(v)] as [number, number])]));

const FACE_X = 0.46; // la cara un poco a la izquierda del centro (a la derecha queda el monitor)
const FACE_Y = 0.44;

export type HLayout = { left: number; top: number; vw: number; vh: number; sc: number };
/** Dónde cae el plano de una toma DENTRO de la ventana (lo comparten el vídeo base y el recorte del sujeto). */
export const hLayout = (s: Segment, t: number): HLayout => {
  const p = popOf(s, t);
  const zoom = BASE_ZOOM * keys(t, ZOOMS_H[s.id] ?? [[s.start, 1]]);
  const sc = Math.max(WIN.w / s.srcW, WIN.h / s.srcH) * zoom;
  const vw = s.srcW * sc;
  const vh = s.srcH * sc;
  // En plano normal el ancla es la posición media de la cara (cámara quieta); cuando sobresale, la sigue.
  const lt = t - s.start;
  const tr = s.track;
  const fx = tr && p > 0 ? lerp(s.face.x, keys(lt, tr.map((k) => [k[0], k[1]] as [number, number]), (v) => v), p) : s.face.x;
  const tx = lerp(FACE_X, 0.5, p) * WIN.w;
  const left = Math.min(0, Math.max(WIN.w - vw, tx - fx * vw));
  // Plano normal: la cara al 44 % de la altura. Pop: la coronilla queda `popOut` px por ENCIMA de la ventana.
  const topNormal = FACE_Y * WIN.h - s.face.y * vh;
  const head = CABEZA[s.id];
  const topPop = head && p > 0 ? -popOut(s.id) - keys(lt, head, (v) => v) * vh : topNormal;
  const top = Math.min(0, Math.max(WIN.h - vh, lerp(topNormal, topPop, p)));
  return { left, top, vw, vh, sc };
};
