import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { GP, HN } from "./fuentes";

// Subtítulos del lote 2, calcados de la referencia "referencia_subs" (ver estilo.md · Subtítulos · Lote 2):
// - contexto en Helvetica Neue Medium (+ trazo 0,3 px), entreletrado −3,5 %
// - palabra clave en Georgia Pro SemiBold ≈ 1,6 × en su propia línea, −1,5 %, con línea de luz lila
// - cada palabra entra al 40 % de opacidad, desenfocada y 7 px por debajo; en 11 f queda blanca y nítida
// - la línea se recentra con suavidad al sumar palabras y el bloque sube al sumar una línea
// - el bloque sale con fundido + desenfoque en 7 f

export type P2 = { t: string; s: number; e: number; w: number }; // w = ancho en em (fuente real, con entreletrado)
export type L2 = { tipo: "ctx" | "clave"; p: P2[]; escala?: number };
export type B2 = {
  desde: number;
  hasta: number;
  x: number; // centro del bloque (px)
  y: number;
  quien?: "G" | "C" | null; // quién habla: el triángulo apunta hacia ese lado
  lado?: "izq" | "der" | null; // hacia dónde apunta el triángulo
  lineas: L2[];
};

export const TAM = { ctx: 64, clave: 104 };
export const TRACK = { ctx: -0.035, clave: -0.015 };
const ALTO = { ctx: 0.95, clave: 0.86 }; // interlineado muy cerrado: la línea grande casi toca la de arriba
const ESPACIO = 0.25; // espacio entre palabras en em
const ADELANTO = 3; // la palabra empieza a aparecer 3 f antes de decirse
const F_ENTRADA = { ctx: 11, clave: 14 };
const F_REFLUJO = 9;
const F_SALIDA = 7;
const F_LUZ = 20;
const eOut = Easing.bezier(0.16, 1, 0.3, 1);
const eInOut = Easing.bezier(0.65, 0, 0.35, 1);
const cl = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const COLOR_QUIEN = { G: "#F5A3C7", C: "#F6D25A" } as const;
const LILA_NUCLEO = "#EFE4FF";
const LILA_BRILLO = "#B184F5";

const SOMBRA =
  "0 2px 10px rgba(0,0,0,.35), 0 1px 3px rgba(0,0,0,.28), 0 6px 26px rgba(24,10,48,.30)";
// Sobre fondos muy claros (caja blanca) la referencia marca más la sombra proyectada (efecto 3D)
const SOMBRA_FUERTE =
  "0 2px 4px rgba(20,8,40,.45), 0 4px 14px rgba(0,0,0,.40), 0 8px 30px rgba(24,10,48,.38)";

// Trazo "pincel" bajo la palabra clave: afilado en las puntas, más grueso en el primer tercio, sube un poco a la derecha.
const pincel = (W: number, H: number) => {
  const n = 32;
  const arriba: string[] = [];
  const abajo: string[] = [];
  for (let i = 0; i <= n; i++) {
    const u = i / n;
    const x = u * W;
    const yc = H * 0.62 - H * 0.34 * u + H * 0.1 * Math.sin(Math.PI * u);
    const g = H * 0.46 * Math.pow(Math.sin(Math.PI * Math.min(1, Math.pow(u, 0.8))), 0.75) + 0.5;
    arriba.push(`${x.toFixed(1)},${(yc - g / 2).toFixed(2)}`);
    abajo.unshift(`${x.toFixed(1)},${(yc + g / 2).toFixed(2)}`);
  }
  return `M${arriba.join(" L")} L${abajo.join(" L")} Z`;
};

const LuzClave: React.FC<{ ancho: number; progreso: number; id: string }> = ({ ancho, progreso, id }) => {
  const W = ancho * 1.04;
  const H = 20;
  const d = pincel(W, H);
  return (
    <svg
      width={W + 40}
      height={H + 40}
      viewBox={`-20 -20 ${W + 40} ${H + 40}`}
      style={{ position: "absolute", left: -ancho * 0.03 - 20, top: -20, overflow: "visible" }}
    >
      <defs>
        <clipPath id={`c${id}`}>
          <rect x={-20} y={-20} width={20 + W * progreso + 4} height={H + 40} />
        </clipPath>
        <filter id={`b${id}`} x="-30%" y="-200%" width="160%" height="500%">
          <feGaussianBlur stdDeviation={6} />
        </filter>
      </defs>
      <g clipPath={`url(#c${id})`}>
        <path d={d} fill={LILA_BRILLO} filter={`url(#b${id})`} opacity={0.95} />
        <path d={d} fill={LILA_BRILLO} opacity={0.9} transform={`translate(0 0.6)`} />
        <path d={d} fill={LILA_NUCLEO} transform={`scale(1 0.55) translate(0 ${H * 0.4})`} />
      </g>
    </svg>
  );
};

const Triangulo: React.FC<{ color: string; lado: "izq" | "der"; p: number }> = ({ color, lado, p }) => (
  <svg
    width={22}
    height={26}
    viewBox="0 0 22 26"
    style={{
      position: "absolute",
      opacity: p,
      scale: String(0.6 + 0.4 * p),
      filter: "drop-shadow(0 2px 6px rgba(0,0,0,.35))",
    }}
  >
    <polygon points={lado === "izq" ? "22,0 22,26 0,13" : "0,0 0,26 22,13"} fill={color} />
  </svg>
);

const BloqueSub: React.FC<{ b: B2; t: number; fps: number; idx: number; sombra: string }> = ({ b, t, fps, idx, sombra }) => {
  const fr = (s: number) => s * fps;
  const ahora = fr(t);
  // salida
  const pe = interpolate(ahora, [fr(b.hasta), fr(b.hasta) + F_SALIDA], [0, 1], { ...cl, easing: eInOut });
  if (pe >= 1) return null;

  // progreso de aparición de cada línea (= su primera palabra) para el desplazamiento vertical del bloque
  const altos = b.lineas.map((l) => TAM[l.tipo] * (l.escala ?? 1) * ALTO[l.tipo]);
  const pLinea = b.lineas.map((l) =>
    interpolate(ahora, [fr(l.p[0].s) - ADELANTO, fr(l.p[0].s) - ADELANTO + F_REFLUJO], [0, 1], { ...cl, easing: eOut }),
  );
  const altoTotal = altos.reduce((a, h, i) => a + h * pLinea[i], 0);
  const top0 = b.y - altoTotal / 2;

  let yAcum = 0;
  const lineas = b.lineas.map((l, li) => {
    const size = TAM[l.tipo] * (l.escala ?? 1);
    const esp = ESPACIO * size;
    const anchos = l.p.map((p) => p.w * size);
    const pr = l.p.map((p) =>
      interpolate(ahora, [fr(p.s) - ADELANTO, fr(p.s) - ADELANTO + F_REFLUJO], [0, 1], { ...cl, easing: eOut }),
    );
    // ancho animado de la línea → recentrado suave
    const W = anchos.reduce((a, w, i) => a + (w + (i > 0 ? esp : 0)) * pr[i], 0);
    const izq = b.x - W / 2;
    const topL = top0 + yAcum;
    yAcum += altos[li];
    if (pLinea[li] <= 0) return null;
    let xAcum = 0;
    const palabras = l.p.map((p, i) => {
      const x = izq + xAcum;
      xAcum += anchos[i] + esp;
      const ini = fr(p.s) - ADELANTO;
      if (ahora < ini) return null;
      const dur = F_ENTRADA[l.tipo];
      const a = interpolate(ahora, [ini, ini + dur], [0, 1], { ...cl, easing: eOut });
      const base = interpolate(ahora, [ini, ini + 2], [0, 0.4], cl);
      const op = Math.min(1, base + 0.6 * a);
      const blur = 3.5 * (1 - a);
      const dy = 7 * (1 - a);
      const estilo: React.CSSProperties =
        l.tipo === "ctx"
          ? { fontFamily: HN, fontWeight: 500, fontSize: size, letterSpacing: `${TRACK.ctx}em`, WebkitTextStroke: "0.3px #fff" }
          : { fontFamily: GP, fontWeight: 600, fontSize: size, letterSpacing: `${TRACK.clave}em` };
      return (
        <div
          key={i}
          style={{
            position: "absolute",
            left: x,
            top: topL,
            height: altos[li],
            lineHeight: `${altos[li]}px`,
            whiteSpace: "nowrap",
            color: "#fff",
            opacity: op,
            filter: blur > 0.05 ? `blur(${blur.toFixed(2)}px)` : undefined,
            translate: `0px ${dy.toFixed(2)}px`,
            textShadow: sombra,
            ...estilo,
          }}
        >
          {p.t}
        </div>
      );
    });

    // línea de luz bajo la palabra clave
    let luz: React.ReactNode = null;
    if (l.tipo === "clave") {
      const ini = fr(l.p[0].s) - ADELANTO + 4;
      const u = interpolate(ahora, [ini, ini + F_LUZ], [0, 1], { ...cl, easing: eInOut });
      const Wfin = anchos.reduce((a, w, i) => a + w + (i > 0 ? esp : 0), 0);
      if (u > 0)
        luz = (
          <div style={{ position: "absolute", left: b.x - Wfin / 2, top: topL + altos[li] * 0.9 }}>
            <LuzClave ancho={Wfin} progreso={u} id={`${idx}-${li}`} />
          </div>
        );
    }

    // triángulo que apunta a quien habla, pegado al borde de la primera línea
    let tri: React.ReactNode = null;
    if (li === 0 && b.quien && b.lado) {
      const pt = pr[0];
      const tx = b.lado === "izq" ? izq - 22 - 16 : izq + W + 16;
      tri = (
        <div style={{ position: "absolute", left: tx, top: topL + altos[li] / 2 - 13 + 2 }}>
          <Triangulo color={COLOR_QUIEN[b.quien]} lado={b.lado} p={pt} />
        </div>
      );
    }
    return (
      <React.Fragment key={li}>
        {luz}
        {palabras}
        {tri}
      </React.Fragment>
    );
  });

  return (
    <AbsoluteFill
      style={{
        opacity: 1 - pe,
        filter: pe > 0.01 ? `blur(${(7 * pe).toFixed(2)}px)` : undefined,
        translate: `0px ${(-6 * pe).toFixed(2)}px`,
      }}
    >
      {lineas}
    </AbsoluteFill>
  );
};

export const Subtitulos2: React.FC<{ bloques: B2[]; sombraFuerte?: boolean }> = ({ bloques, sombraFuerte = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {bloques.map((b, i) =>
        t >= b.desde - 0.1 && t <= b.hasta + 0.2 ? <BloqueSub key={i} b={b} t={t} fps={fps} idx={i} sombra={sombraFuerte ? SOMBRA_FUERTE : SOMBRA} /> : null,
      )}
    </AbsoluteFill>
  );
};
