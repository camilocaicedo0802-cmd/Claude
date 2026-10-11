import React from "react";
import { Easing, interpolate, interpolateColors } from "remotion";
import { palabras } from "../data/palabras";
import { SANS, SERIF, SERIF_ANCHA } from "../lib/fonts";
import { C } from "../lib/theme";
import { ADELANTO, pf } from "../lib/timing";
import { Modo, useEscena, useFrameGlobal } from "./base";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const easeOut = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * Tipos de línea (estilo.md §3.1–3.2):
 * peq      → sans Bold 50 px (línea pequeña)
 * med      → sans Bold 72 px (pilas, etiquetas)
 * heroSans → sans Bold 160 px, interletrado −0,08 em ("estaba", "1997")
 * hero     → serif Bold Italic condensada, MAYÚSCULAS, revelado letra a letra
 * serifMin → serif Bold Italic sin condensar, minúsculas ("Demaciados", "decisión")
 */
export type Tipo = "peq" | "med" | "heroSans" | "hero" | "serifMin";
export type PalabraSpec = { i: number; t?: string };
export type LineaSpec = {
  w: PalabraSpec[];
  tipo: Tipo;
  align?: "left" | "right" | "center";
  size?: number;
  dx?: number;
  mb?: number;
};

const TAM: Record<Tipo, number> = {
  peq: 50,
  med: 72,
  heroSans: 160,
  hero: 180,
  serifMin: 92,
};

const estiloBase = (
  tipo: Tipo,
  size: number,
  modo: Modo,
): React.CSSProperties => {
  const glow =
    modo === "oscuro"
      ? `0 0 ${Math.round(size * 0.1)}px ${C.glow}, 0 0 ${Math.round(size * 0.25)}px ${C.glow2}`
      : undefined;
  if (tipo === "hero")
    return {
      fontFamily: SERIF,
      fontStyle: "italic",
      fontWeight: 700,
      fontSize: size,
      lineHeight: 0.86,
      letterSpacing: "-0.03em",
      textTransform: "uppercase",
      WebkitTextStroke: `${(size * 0.014).toFixed(1)}px currentColor`,
      textShadow: glow,
    };
  if (tipo === "serifMin")
    return {
      fontFamily: SERIF_ANCHA,
      fontStyle: "italic",
      fontWeight: 700,
      fontSize: size,
      lineHeight: 0.95,
      letterSpacing: "-0.02em",
      textShadow: glow,
    };
  return {
    fontFamily: SANS,
    fontWeight: 700,
    fontSize: size,
    lineHeight: tipo === "heroSans" ? 0.82 : 0.95,
    letterSpacing: tipo === "heroSans" ? "-0.08em" : "-0.06em",
    textShadow: glow,
  };
};

const colores = (modo: Modo) =>
  modo === "claro"
    ? [C.grisEntrando, C.negro]
    : ["rgba(255,255,255,0.35)", "#FFFFFF"];

/** Palabra normal: opacidad 0→1, desenfoque 10→0, escala 0,92→1 (7 fr) y gris→negro (12 fr). */
const Palabra: React.FC<{
  spec: PalabraSpec;
  tipo: Tipo;
  size: number;
  modo: Modo;
  ultima: boolean;
}> = ({ spec, tipo, size, modo, ultima }) => {
  const frame = useFrameGlobal();
  const s = pf(spec.i) - ADELANTO;
  const p = interpolate(frame, [s, s + 7], [0, 1], {
    ...clamp,
    easing: easeOut,
  });
  const c = interpolate(frame, [s, s + 12], [0, 1], clamp);
  const texto = (spec.t ?? palabras[spec.i].text.trim()).normalize("NFC");
  return (
    <span
      style={{
        display: "inline-block",
        opacity: p,
        filter: p < 0.98 ? `blur(${((1 - p) * 10).toFixed(2)}px)` : undefined,
        scale: String(0.92 + 0.08 * p),
        color: interpolateColors(c, [0, 1], colores(modo)),
        marginRight: ultima ? 0 : `${tipo === "heroSans" ? 0.12 : 0.22}em`,
        ...estiloBase(tipo, size, modo),
      }}
    >
      {texto}
    </span>
  );
};

/** Palabra destacada: revelado letra a letra de izquierda a derecha (1,2 fr de desfase por letra). */
const PalabraHero: React.FC<{
  spec: PalabraSpec;
  tipo: Tipo;
  size: number;
  modo: Modo;
  ultima: boolean;
}> = ({ spec, tipo, size, modo, ultima }) => {
  const frame = useFrameGlobal();
  const texto = (spec.t ?? palabras[spec.i].text.trim()).normalize("NFC");
  const base = pf(spec.i) - ADELANTO;
  const letras = Array.from(texto);
  return (
    <span
      style={{
        display: "inline-block",
        whiteSpace: "pre",
        marginRight: ultima ? 0 : "0.18em",
        ...estiloBase(tipo, size, modo),
      }}
    >
      {letras.map((ch, j) => {
        const s = base + j * 1.2;
        const p = interpolate(frame, [s, s + 6], [0, 1], {
          ...clamp,
          easing: easeOut,
        });
        const c = interpolate(frame, [s, s + 9], [0, 1], clamp);
        const mov = modo === "oscuro" ? (1 - p) * -28 : 0;
        return (
          <span
            key={j}
            style={{
              display: "inline-block",
              opacity: Math.min(1, p * 1.6),
              filter:
                p < 0.98 ? `blur(${((1 - p) * 9).toFixed(2)}px)` : undefined,
              translate: `${mov}px 0px`,
              color: interpolateColors(c, [0, 1], colores(modo)),
            }}
          >
            {ch}
          </span>
        );
      })}
    </span>
  );
};

/**
 * Bloque tipográfico escalonado (estilo.md §3.3): pequeña izq. → DESTACADA → pequeña der.
 * `top` es la y del borde superior del bloque; `cx` su centro horizontal.
 */
export const Bloque: React.FC<{
  lineas: LineaSpec[];
  top: number;
  cx?: number;
  modo?: Modo;
  ancho?: number;
}> = ({ lineas, top, cx = 540, modo, ancho }) => {
  const esc = useEscena();
  const m = modo ?? esc.modo;
  return (
    <div
      style={{
        position: "absolute",
        top,
        left: cx,
        translate: "-50% 0px",
        display: "inline-flex",
        flexDirection: "column",
        width: ancho,
        whiteSpace: "nowrap",
      }}
    >
      {lineas.map((l, k) => {
        const size = l.size ?? TAM[l.tipo];
        const Comp = l.tipo === "hero" ? PalabraHero : Palabra;
        return (
          <div
            key={k}
            style={{
              textAlign: l.align ?? "center",
              paddingLeft: l.align === "left" ? (l.dx ?? 14) : 0,
              paddingRight: l.align === "right" ? (l.dx ?? 6) : 0,
              marginBottom:
                l.mb ?? (l.tipo === "peq" ? 2 : l.tipo === "med" ? -4 : 2),
              lineHeight: 0.9,
            }}
          >
            {l.w.map((spec, j) => (
              <Comp
                key={j}
                spec={spec}
                tipo={l.tipo}
                size={size}
                modo={m}
                ultima={j === l.w.length - 1}
              />
            ))}
          </div>
        );
      })}
    </div>
  );
};
