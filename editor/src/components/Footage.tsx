import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS } from "../brand";
import { at, DURATION, HOLD, SEGMENTS, WORDS } from "../lib/timing";

// Vídeo ya editado por scripts/preparar.py: silencios fuera, audio original, recorte 1620×2880 del 4K.
const VIDEO_SRC = "crudo/editado.mp4";
// Centro de la cara en el encuadre (origen de todos los zooms)
const CARA = "52% 43%";
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Niveles de cámara: plano medio, medio corto, primer plano. Se recorren sin repetir el anterior.
const NIVELES = [1.0, 1.22, 1.08, 1.36, 1.15, 1.28];
const PLANO_MAX = 2.4; // s: un plano más largo se parte con un zoom suave en el arranque de una palabra
const TRANSICION_ZOOM = 0.3; // s que tarda un zoom suave

// Palabras que reciben un "golpe" de zoom (+6 %) porque son el dato clave de su frase.
const ENFASIS = [
  at("21 días").start,
  at("3|tres semanas").start,
  at("15 minutos").start,
  at("una guía").end - 0.2,
  at("perfecto").start,
  at("constante").start,
  at("primer día").start,
];

// Cambios de tema → transición "whip" (zoom brusco + desenfoque + destello Durazno)
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

// Mientras señala el hueco del calendario la cámara se queda abierta (si no, el gesto sale de cuadro)
const SIN_ZOOM = [at("recuerda guardar").start, at("además").start] as const;

type Plano = { start: number; end: number; zoom: number; suave: boolean };

const construirPlanos = (): Plano[] => {
  const limites: { t: number; suave: boolean }[] = [];
  SEGMENTS.forEach((s, i) => {
    const fin = i < SEGMENTS.length - 1 ? SEGMENTS[i + 1].outStart : DURATION + HOLD;
    limites.push({ t: s.outStart, suave: false });
    let a = s.outStart;
    while (fin - a > PLANO_MAX) {
      const objetivo = a + Math.min(2.0, (fin - a) / 2);
      const candidatas = WORDS.filter((w) => w.start > a + 1.1 && w.start < fin - 1.0);
      if (candidatas.length === 0) break;
      const w = candidatas.reduce((m, x) => (Math.abs(x.start - objetivo) < Math.abs(m.start - objetivo) ? x : m));
      limites.push({ t: w.start, suave: true });
      a = w.start;
    }
  });
  return limites.map((l, i) => {
    const end = i < limites.length - 1 ? limites[i + 1].t : DURATION + HOLD;
    const enCalendario = l.t < SIN_ZOOM[1] && end > SIN_ZOOM[0];
    return { start: l.t, end, zoom: enCalendario ? 1 : NIVELES[i % NIVELES.length], suave: l.suave };
  });
};

const PLANOS = construirPlanos();

const camara = (t: number, fps: number, frame: number) => {
  const i = Math.max(0, PLANOS.findIndex((p) => t >= p.start && t < p.end));
  const p = PLANOS[i];
  const previo = i > 0 ? PLANOS[i - 1].zoom : p.zoom;
  const base = p.suave
    ? interpolate(t, [p.start, p.start + TRANSICION_ZOOM], [previo, p.zoom], { ...CLAMP, easing: Easing.inOut(Easing.cubic) })
    : p.zoom;
  const empuje = interpolate(t, [p.start, p.end], [1, 1.03], CLAMP);
  const golpe = ENFASIS.reduce((acc, e) => {
    const d = frame - Math.round(e * fps);
    return acc + interpolate(d, [0, 4, 16], [0, 0.06, 0], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  }, 0);
  let whip = 0;
  let blur = 0;
  for (const tr of TRANSICIONES) {
    const d = frame - Math.round(tr * fps);
    whip += interpolate(d, [-5, 0, 6], [0, 0.28, 0], { ...CLAMP, easing: Easing.inOut(Easing.quad) });
    blur += interpolate(d, [-5, 0, 6], [0, 14, 0], CLAMP);
  }
  return { escala: base * empuje + golpe + whip, blur };
};

export const Footage: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const { escala, blur } = camara(t, fps, frame);
  const destello = TRANSICIONES.reduce((acc, tr) => {
    const d = frame - Math.round(tr * fps);
    return Math.max(acc, interpolate(d, [-2, 0, 5], [0, 0.32, 0], CLAMP));
  }, 0);

  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ transform: `scale(${escala})`, transformOrigin: CARA, filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}>
        <Video src={staticFile(VIDEO_SRC)} objectFit="cover" style={{ width: "100%", height: "100%" }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: COLORS.durazno, opacity: destello }} />
    </AbsoluteFill>
  );
};
