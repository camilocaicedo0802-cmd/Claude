import { Video } from "@remotion/media";
import React from "react";
import { interpolate, Sequence, spring, staticFile } from "remotion";
import { COLORS, FONTS } from "../brand";
import { CLAMP, pop, useT } from "../rutinas/util";
import { TARJETA_ARRIBA } from "./Base9";

// Gráficos 2D del día 9 "Rutina integrada". Lenguaje nuevo frente a los días anteriores: capítulos numerados en el
// margen de la tarjeta con una barra de los 5 tramos, título que se revela tras un bloque de color, mosaicos 2×2
// de las zonas, pizarra de análisis sobre fotogramas congelados (líneas, prohibido, cruces), notas claras (Marfil
// con borde Durazno, en vez de las tarjetas oscuras), ruta del arrastre e interruptor manos/dispositivo.

export const SOMBRA9 = "0 14px 34px rgba(69,89,90,.28), 0 3px 8px rgba(69,89,90,.18)";
const NOTA_BG = "rgba(245,240,236,0.94)";
const sube = (frame: number, fps: number, atSec: number) => pop(frame, fps, atSec, 15);

/** Los 5 tramos del cuadro del día 9: Preparación 1 · Piernas 6 · Abdomen y laterales 4 · Glúteos 3 · Brazos 1. */
export const TRAMOS9 = [
  { nombre: "Preparación", min: 1 },
  { nombre: "Piernas", min: 6 },
  { nombre: "Abdomen", min: 4 },
  { nombre: "Glúteos", min: 3 },
  { nombre: "Brazos", min: 1 },
];

export type Capitulo = {
  desde: number;
  numero?: string;
  kicker: string;
  titulo: string;
  /** Tramo que se llena (0–4); "todos" en el cierre; undefined en la intro. */
  tramo?: number | "todos";
  /** En el cierre: los minutos cuentan hasta 15 desde este instante. */
  cuenta?: number;
};

/** Barra de los 5 tramos (ancho proporcional a los minutos): el actual se llena, los anteriores quedan Salvia. */
const Barra: React.FC<{ cap: Capitulo; t: number }> = ({ cap, t }) => {
  const ANCHO = 780;
  const total = TRAMOS9.reduce((a, b) => a + b.min, 0);
  let x = 0;
  return (
    <div style={{ position: "relative", width: ANCHO, height: 40 }}>
      {TRAMOS9.map((tr, i) => {
        const w = (tr.min / total) * ANCHO - 8;
        const left = x;
        x += w + 8;
        const todos = cap.tramo === "todos";
        const actual = cap.tramo === i;
        const hecho = todos || (typeof cap.tramo === "number" && i < cap.tramo);
        const llena = todos
          ? interpolate(t, [cap.desde + 0.3 + i * 0.12, cap.desde + 0.55 + i * 0.12], [0, 1], CLAMP)
          : actual
            ? interpolate(t, [cap.desde + 0.35, cap.desde + 1.6], [0, 1], CLAMP)
            : hecho
              ? 1
              : 0;
        return (
          <div
            key={tr.nombre}
            style={{
              position: "absolute",
              left,
              top: 0,
              width: w,
              height: 40,
              borderRadius: 20,
              border: `3px solid ${actual ? COLORS.salvia : "rgba(69,89,90,.25)"}`,
              boxSizing: "border-box",
              overflow: "hidden",
              background: "rgba(255,255,255,.55)",
            }}
          >
            <div
              style={{
                position: "absolute",
                left: 0,
                top: 0,
                bottom: 0,
                width: `${llena * 100}%`,
                background: actual ? COLORS.salvia : hecho ? "rgba(109,139,116,.75)" : "transparent",
              }}
            />
            <div
              style={{
                position: "absolute",
                inset: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontFamily: FONTS.body,
                fontWeight: 700,
                fontSize: 21,
                color: llena > 0.5 ? COLORS.marfil : COLORS.petroleo,
                whiteSpace: "nowrap",
              }}
            >
              {w > 120 ? `${tr.nombre.toUpperCase()} · ${tr.min}′` : `${tr.min}′`}
            </div>
          </div>
        );
      })}
    </div>
  );
};

/** Capítulo en el margen superior de la tarjeta: número + kicker, título que se revela tras un bloque, barra. */
export const TituloCapitulo: React.FC<{ caps: Capitulo[]; p: number }> = ({ caps, p }) => {
  const { t, frame, fps } = useT();
  if (p <= 0.01) return null;
  const cap = [...caps].reverse().find((c) => t >= c.desde - 0.01);
  if (!cap) return null;
  // Bloque Durazno: crece de izquierda a derecha y se retira hacia la derecha descubriendo el título
  const crece = interpolate(t, [cap.desde + 0.05, cap.desde + 0.3], [0, 1], CLAMP);
  const retira = interpolate(t, [cap.desde + 0.32, cap.desde + 0.58], [0, 1], CLAMP);
  const visible = retira > 0;
  const size = Math.min(124, 900 / (0.62 * cap.titulo.length));
  const k = sube(frame, fps, cap.desde);
  const cuenta =
    cap.cuenta !== undefined ? Math.round(interpolate(t, [cap.cuenta, cap.cuenta + 0.9], [0, 15], CLAMP)) : null;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 0,
        height: TARJETA_ARRIBA,
        opacity: p,
        transform: `translateY(${(1 - p) * -40}px)`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-end",
        paddingBottom: 30,
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 14,
          opacity: Math.min(1, k * 1.4),
          transform: `translateY(${(1 - k) * 20}px)`,
        }}
      >
        {cap.numero ? (
          <div
            style={{
              width: 58,
              height: 58,
              borderRadius: 29,
              background: COLORS.salvia,
              color: COLORS.marfil,
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 27,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {cap.numero}
          </div>
        ) : null}
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 30,
            letterSpacing: "0.2em",
            color: COLORS.salvia,
          }}
        >
          {cuenta !== null ? `${cuenta} MINUTOS` : cap.kicker}
        </div>
      </div>
      <div style={{ position: "relative", marginTop: 6, marginBottom: 18 }}>
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: size,
            lineHeight: 1.08,
            color: COLORS.petroleo,
            whiteSpace: "nowrap",
            opacity: visible ? 1 : 0,
            padding: "0 10px",
          }}
        >
          {cap.titulo}
        </div>
        <div
          style={{
            position: "absolute",
            top: "8%",
            bottom: "4%",
            left: `${retira * 100}%`,
            width: `${(crece - retira) * 100}%`,
            background: COLORS.durazno,
            borderRadius: 10,
          }}
        />
      </div>
      <Barra cap={cap} t={t} />
    </div>
  );
};

// ---------- Mosaico 2×2 de las zonas (fuera del escenario, a pantalla completa) ----------
const ZONAS = ["piernas", "abdomen", "glúteos", "brazos"];
export const Mosaico: React.FC<{
  src: string;
  desde: number;
  hasta: number;
  /** Instante en que entra cada celda y en que aparece su rótulo (o su ✓ en el cierre). */
  entra: number[];
  rotulo: number[];
  check?: boolean;
  /** Las celdas se van hacia sus esquinas y descubren la toma de debajo. */
  abre: number;
}> = ({ src, desde, hasta, entra, rotulo, check = false, abre }) => {
  const { t, frame, fps } = useT();
  if (t < desde - 0.05 || t > hasta) return null;
  const sale = interpolate(t, [abre, abre + 0.42], [0, 1], { ...CLAMP, easing: (x) => x * x });
  const fondo = 1 - interpolate(t, [abre, abre + 0.2], [0, 1], CLAMP);
  return (
    <>
      <div style={{ position: "absolute", inset: 0, background: COLORS.marfil, opacity: fondo }} />
      <Sequence from={Math.round(desde * fps)} durationInFrames={Math.round((hasta - desde) * fps) + 2} layout="none">
        {ZONAS.map((z, i) => {
          const qx = i % 2;
          const qy = Math.floor(i / 2);
          const k = spring({ frame: frame - Math.round(entra[i] * fps), fps, config: { damping: 14, mass: 0.6 } });
          const kr = sube(frame, fps, rotulo[i]);
          const dx = (qx ? 1 : -1) * 760 * sale;
          const dy = (qy ? 1 : -1) * 1100 * sale;
          const left = qx * 540 + 8;
          const top = qy * 960 + 8;
          if (frame < Math.round(entra[i] * fps)) return null;
          return (
            <div
              key={z}
              style={{
                position: "absolute",
                left,
                top,
                width: 524,
                height: 944,
                borderRadius: 34,
                overflow: "hidden",
                boxShadow: SOMBRA9,
                transform: `translate(${dx}px, ${dy}px) rotate(${(qx ? 1 : -1) * (qy ? 1 : -1) * 8 * sale}deg) scale(${0.82 + 0.18 * k})`,
                opacity: Math.min(1, k * 1.5),
              }}
            >
              <Video
                src={staticFile(src)}
                muted
                style={{ position: "absolute", left: -left, top: -top, width: 1080, height: 1920 }}
              />
              {kr > 0 ? (
                <div
                  style={{
                    position: "absolute",
                    left: 26,
                    bottom: qy ? 230 : 36,
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "10px 22px 8px 12px",
                    borderRadius: 40,
                    background: COLORS.durazno,
                    boxShadow: SOMBRA9,
                    opacity: Math.min(1, kr * 1.5),
                    transform: `translateX(${(1 - kr) * -40}px)`,
                  }}
                >
                  <div
                    style={{
                      width: 38,
                      height: 38,
                      borderRadius: 19,
                      background: check ? COLORS.salvia : COLORS.petroleo,
                      color: COLORS.marfil,
                      fontFamily: FONTS.body,
                      fontWeight: 700,
                      fontSize: 22,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    {check ? (
                      <svg width={24} height={24} viewBox="0 0 24 24">
                        <path
                          d="M4 12.5 L10 18 L20 6"
                          stroke={COLORS.marfil}
                          strokeWidth={3.4}
                          fill="none"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          pathLength={1}
                          strokeDasharray={1}
                          strokeDashoffset={1 - Math.min(1, kr)}
                        />
                      </svg>
                    ) : (
                      i + 1
                    )}
                  </div>
                  <div
                    style={{
                      fontFamily: FONTS.body,
                      fontWeight: 700,
                      fontSize: 30,
                      letterSpacing: "0.12em",
                      color: COLORS.petroleo,
                    }}
                  >
                    {z.toUpperCase()}
                  </div>
                </div>
              ) : null}
            </div>
          );
        })}
      </Sequence>
    </>
  );
};

// ---------- Pizarra: análisis sobre un fotograma congelado (dentro del escenario, coordenadas de la toma) ----------
export type Trazo =
  | { tipo: "flecha"; pts: [number, number][]; at: number; dur?: number; color?: string; ancho?: number }
  | { tipo: "banda"; pts: [number, number][]; at: number; ancho: number }
  | { tipo: "prohibido"; x: number; y: number; r: number; at: number }
  | { tipo: "cruz"; x: number; y: number; r: number; at: number }
  | { tipo: "orbita"; x: number; y: number; rx: number; ry: number; at: number }
  | { tipo: "etiqueta"; x: number; y: number; texto: string; at: number; ancla?: "izq" | "der" | "centro"; tono?: "si" | "no" };

const camino = (pts: [number, number][]) => pts.map(([x, y], i) => `${i ? "L" : "M"} ${x} ${y}`).join(" ");

export const Pizarra: React.FC<{
  desde: number;
  hasta: number;
  foco: { cx: number; cy: number; rx: number; ry: number };
  trazos: Trazo[];
}> = ({ desde, hasta, foco, trazos }) => {
  const { t, frame, fps } = useT();
  if (t < desde || t >= hasta) return null;
  const velo = interpolate(t, [desde + 0.05, desde + 0.4, hasta - 0.12, hasta], [0, 1, 1, 0], CLAMP);
  // Esquinas de visor (modo análisis)
  const esq = interpolate(t, [desde, desde + 0.25], [0, 1], CLAMP);
  const m = 40 + (1 - esq) * 40;
  const L = 90;
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
        <defs>
          <mask id={`foco${Math.round(desde * 100)}`}>
            <rect width={1080} height={1920} fill="white" />
            <ellipse cx={foco.cx} cy={foco.cy} rx={foco.rx} ry={foco.ry} fill="black" />
          </mask>
          <filter id="difumina9">
            <feGaussianBlur stdDeviation={40} />
          </filter>
        </defs>
        <g mask={`url(#foco${Math.round(desde * 100)})`}>
          <rect width={1080} height={1920} fill={`rgba(46,60,61,${0.5 * velo})`} />
        </g>
        {[
          [m, m, 1, 1],
          [1080 - m, m, -1, 1],
          [m, 1920 - m - 260, 1, -1],
          [1080 - m, 1920 - m - 260, -1, -1],
        ].map(([x, y, sx, sy], i) => (
          <path
            key={i}
            d={`M ${x} ${y + sy * L} L ${x} ${y} L ${x + sx * L} ${y}`}
            stroke={COLORS.durazno}
            strokeWidth={9}
            fill="none"
            strokeLinecap="round"
            opacity={esq}
          />
        ))}
        {trazos.map((tr, i) => {
          if (tr.tipo === "flecha" || tr.tipo === "banda") {
            const d = interpolate(t, [tr.at, tr.at + ("dur" in tr && tr.dur ? tr.dur : 0.45)], [0, 1], CLAMP);
            if (d <= 0) return null;
            if (tr.tipo === "banda")
              return (
                <path
                  key={i}
                  d={camino(tr.pts)}
                  stroke={COLORS.salvia}
                  strokeOpacity={0.55}
                  strokeWidth={tr.ancho}
                  fill="none"
                  strokeLinecap="round"
                  pathLength={1}
                  strokeDasharray={1}
                  strokeDashoffset={1 - d}
                />
              );
            const [ax, ay] = tr.pts[tr.pts.length - 2];
            const [bx, by] = tr.pts[tr.pts.length - 1];
            const ang = (Math.atan2(by - ay, bx - ax) * 180) / Math.PI;
            const color = tr.color ?? COLORS.durazno;
            const w = tr.ancho ?? 12;
            return (
              <g key={i}>
                <path
                  d={camino(tr.pts)}
                  stroke="rgba(46,60,61,.45)"
                  strokeWidth={w + 8}
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  pathLength={1}
                  strokeDasharray={1}
                  strokeDashoffset={1 - d}
                />
                <path
                  d={camino(tr.pts)}
                  stroke={color}
                  strokeWidth={w}
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  pathLength={1}
                  strokeDasharray={1}
                  strokeDashoffset={1 - d}
                />
                {d >= 1 ? (
                  <path
                    d={`M -16 -18 L 14 0 L -16 18 Z`}
                    fill={color}
                    stroke="rgba(46,60,61,.45)"
                    strokeWidth={3}
                    transform={`translate(${bx} ${by}) rotate(${ang})`}
                  />
                ) : null}
              </g>
            );
          }
          if (tr.tipo === "prohibido" || tr.tipo === "cruz") {
            const k = sube(frame, fps, tr.at);
            const d = interpolate(t, [tr.at + 0.12, tr.at + 0.4], [0, 1], CLAMP);
            if (k <= 0) return null;
            const r = tr.r;
            return (
              <g key={i} transform={`translate(${tr.x} ${tr.y}) scale(${0.6 + 0.4 * k})`} opacity={Math.min(1, k * 1.5)}>
                <circle r={r} fill="rgba(46,60,61,.25)" stroke={COLORS.durazno} strokeWidth={10} />
                {tr.tipo === "prohibido" ? (
                  <path
                    d={`M ${-r * 0.7} ${-r * 0.7} L ${r * 0.7} ${r * 0.7}`}
                    stroke={COLORS.durazno}
                    strokeWidth={10}
                    strokeLinecap="round"
                    pathLength={1}
                    strokeDasharray={1}
                    strokeDashoffset={1 - d}
                  />
                ) : (
                  <path
                    d={`M ${-r * 0.5} ${-r * 0.5} L ${r * 0.5} ${r * 0.5} M ${r * 0.5} ${-r * 0.5} L ${-r * 0.5} ${r * 0.5}`}
                    stroke={COLORS.durazno}
                    strokeWidth={10}
                    strokeLinecap="round"
                    pathLength={1}
                    strokeDasharray={1}
                    strokeDashoffset={1 - d}
                  />
                )}
              </g>
            );
          }
          if (tr.tipo === "orbita") {
            const d = interpolate(t, [tr.at, tr.at + 0.6], [0, 1], CLAMP);
            if (d <= 0) return null;
            const a = (t - tr.at) * 4;
            return (
              <g key={i}>
                <ellipse
                  cx={tr.x}
                  cy={tr.y}
                  rx={tr.rx}
                  ry={tr.ry}
                  fill="none"
                  stroke={COLORS.marfil}
                  strokeWidth={7}
                  strokeDasharray="18 16"
                  opacity={0.9 * d}
                />
                <circle cx={tr.x + Math.cos(-a) * tr.rx} cy={tr.y + Math.sin(-a) * tr.ry} r={16} fill={COLORS.durazno} opacity={d} />
              </g>
            );
          }
          return null;
        })}
      </svg>
      {trazos.map((tr, i) => {
        if (tr.tipo !== "etiqueta") return null;
        const k = sube(frame, fps, tr.at);
        if (k <= 0) return null;
        const ancla = tr.ancla ?? "izq";
        return (
          <div
            key={`e${i}`}
            style={{
              position: "absolute",
              left: tr.x,
              top: tr.y,
              transform: `translate(${ancla === "izq" ? 0 : ancla === "der" ? -100 : -50}%, -50%) scale(${0.7 + 0.3 * k})`,
              opacity: Math.min(1, k * 1.5),
            }}
          >
            <Nota texto={tr.texto} tipo={tr.tono ?? "si"} compacta />
          </div>
        );
      })}
    </div>
  );
};

// ---------- Nota: etiqueta clara (Marfil, borde Durazno) con ✓ Salvia o ✕ Petróleo ----------
export const Nota: React.FC<{
  texto: string;
  tipo?: "si" | "no" | "info";
  compacta?: boolean;
  at?: number;
  ancho?: number;
  style?: React.CSSProperties;
}> = ({ texto, tipo = "si", compacta = false, at, ancho, style }) => {
  const { t, frame, fps } = useT();
  const k = at === undefined ? 1 : sube(frame, fps, at);
  const d = at === undefined ? 1 : interpolate(t, [at + 0.1, at + 0.4], [0, 1], CLAMP);
  if (k <= 0) return null;
  const tam = compacta ? 40 : 46;
  return (
    <div
      style={{
        position: style ? "absolute" : "relative",
        width: ancho,
        ...style,
        opacity: Math.min(1, k * 1.4),
        transform: `${style?.transform ?? ""} translateY(${(1 - k) * 26}px)`,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          background: NOTA_BG,
          border: `3px solid ${COLORS.durazno}`,
          borderRadius: 26,
          padding: compacta ? "8px 18px 8px 10px" : "12px 18px 12px 12px",
          boxShadow: SOMBRA9,
          whiteSpace: compacta ? "nowrap" : undefined,
        }}
      >
        <svg width={tam} height={tam} viewBox="0 0 56 56" style={{ flexShrink: 0 }}>
          <circle cx={28} cy={28} r={26} fill={tipo === "no" ? COLORS.petroleo : COLORS.salvia} />
          {tipo === "no" ? (
            <path
              d="M19 19 L37 37 M37 19 L19 37"
              stroke={COLORS.durazno}
              strokeWidth={6}
              fill="none"
              strokeLinecap="round"
              pathLength={1}
              strokeDasharray={1}
              strokeDashoffset={1 - d}
            />
          ) : tipo === "si" ? (
            <path
              d="M16 29 L25 38 L41 20"
              stroke={COLORS.marfil}
              strokeWidth={6}
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              pathLength={1}
              strokeDasharray={1}
              strokeDashoffset={1 - d}
            />
          ) : (
            <circle cx={28} cy={28} r={7} fill={COLORS.marfil} />
          )}
        </svg>
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: compacta ? 26 : 27,
            lineHeight: 1.15,
            color: COLORS.petroleo,
          }}
        >
          {texto}
        </div>
      </div>
    </div>
  );
};

// ---------- Movimiento: "ascendentes" (flecha que se dibuja hacia arriba) y "continuos" (infinito que se recorre) ----
export const Movimiento: React.FC<{
  sube: number;
  continuo: number;
  style: React.CSSProperties;
}> = ({ sube: tSube, continuo, style }) => {
  const { t, frame, fps } = useT();
  const fila = (atSec: number, icono: React.ReactNode, texto: string) => {
    const k = sube(frame, fps, atSec);
    if (k <= 0) return null;
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 14,
          background: NOTA_BG,
          border: `3px solid ${COLORS.durazno}`,
          borderRadius: 26,
          padding: "10px 20px 10px 12px",
          boxShadow: SOMBRA9,
          opacity: Math.min(1, k * 1.4),
          transform: `translateX(${(1 - k) * -40}px)`,
          marginBottom: 14,
        }}
      >
        <div
          style={{
            width: 64,
            height: 64,
            borderRadius: 18,
            background: COLORS.salvia,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {icono}
        </div>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 30, color: COLORS.petroleo }}>{texto}</div>
      </div>
    );
  };
  const ds = interpolate(t, [tSube + 0.1, tSube + 0.5], [0, 1], CLAMP);
  const ciclo = (t - continuo) * 0.8;
  const inf = "M 32 22 C 24 10 8 10 8 22 C 8 34 24 34 32 22 C 40 10 56 10 56 22 C 56 34 40 34 32 22 Z";
  return (
    <div style={{ position: "absolute", width: 300, ...style }}>
      {fila(
        tSube,
        <svg width={48} height={48} viewBox="0 0 48 48">
          <path
            d="M24 42 L24 8 M12 20 L24 8 L36 20"
            stroke={COLORS.marfil}
            strokeWidth={6}
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - ds}
            transform={`translate(0 ${-4 * Math.sin(t * 6)})`}
          />
        </svg>,
        "Ascendentes",
      )}
      {fila(
        continuo,
        <svg width={56} height={44} viewBox="0 0 64 44">
          <path d={inf} stroke="rgba(245,240,236,.45)" strokeWidth={5} fill="none" />
          <path
            d={inf}
            stroke={COLORS.marfil}
            strokeWidth={6}
            fill="none"
            strokeLinecap="round"
            pathLength={1}
            strokeDasharray="0.3 0.7"
            strokeDashoffset={-ciclo}
          />
        </svg>,
        "Continuos",
      )}
    </div>
  );
};

// ---------- Ruta del arrastre: espalda → cintura → ingle (cada punto se enciende en su palabra) ----------
export const Ruta: React.FC<{
  at: number;
  pasos: { texto: string; at: number }[];
  style: React.CSSProperties;
}> = ({ at: atSec, pasos, style }) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, atSec);
  if (k <= 0) return null;
  const H = 86;
  const avance = pasos.reduce((acc, p, i) => (t >= p.at ? i : acc), -1);
  const prog =
    avance < 0
      ? 0
      : avance >= pasos.length - 1
        ? pasos.length - 1
        : avance + interpolate(t, [pasos[avance].at, pasos[avance + 1].at], [0, 1], CLAMP);
  return (
    <div
      style={{
        position: "absolute",
        width: 300,
        ...style,
        opacity: Math.min(1, k * 1.4),
        transform: `${style.transform ?? ""} translateY(${(1 - k) * 26}px)`,
      }}
    >
      <div
        style={{
          background: NOTA_BG,
          border: `3px solid ${COLORS.durazno}`,
          borderRadius: 30,
          padding: "18px 22px 16px",
          boxShadow: SOMBRA9,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 22,
            letterSpacing: "0.2em",
            color: COLORS.salvia,
            marginBottom: 10,
          }}
        >
          ARRASTRE
        </div>
        <div style={{ position: "relative", height: H * (pasos.length - 1) + 40 }}>
          <div
            style={{
              position: "absolute",
              left: 18,
              top: 20,
              width: 6,
              height: H * (pasos.length - 1),
              background: "rgba(69,89,90,.18)",
              borderRadius: 3,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: 18,
              top: 20,
              width: 6,
              height: H * prog,
              background: COLORS.salvia,
              borderRadius: 3,
            }}
          />
          {pasos.map((p, i) => {
            const on = interpolate(t, [p.at, p.at + 0.2], [0, 1], CLAMP);
            return (
              <div key={p.texto} style={{ position: "absolute", left: 0, top: i * H, display: "flex", alignItems: "center", gap: 16 }}>
                <div
                  style={{
                    width: 42,
                    height: 42,
                    borderRadius: 21,
                    background: on > 0.5 ? COLORS.salvia : COLORS.marfil,
                    border: `4px solid ${on > 0.5 ? COLORS.salvia : "rgba(69,89,90,.3)"}`,
                    boxSizing: "border-box",
                    transform: `scale(${1 + 0.25 * Math.sin(on * Math.PI)})`,
                  }}
                />
                <div
                  style={{
                    fontFamily: FONTS.body,
                    fontWeight: 700,
                    fontSize: 30,
                    color: on > 0.5 ? COLORS.petroleo : "rgba(69,89,90,.45)",
                  }}
                >
                  {p.texto}
                </div>
              </div>
            );
          })}
          {/* Bola que viaja por la ruta */}
          <div
            style={{
              position: "absolute",
              left: 11,
              top: 20 + H * prog - 10,
              width: 20,
              height: 20,
              borderRadius: 10,
              background: COLORS.durazno,
              boxShadow: "0 0 14px rgba(250,237,205,.9)",
              opacity: avance >= 0 ? 1 : 0,
            }}
          />
        </div>
      </div>
    </div>
  );
};

// ---------- Interruptor: "solo con tus manos" / "o con el dispositivo" ----------
export const Interruptor: React.FC<{
  at: number;
  manos: number;
  dispositivo: number;
  style: React.CSSProperties;
}> = ({ at: atSec, manos, dispositivo, style }) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, atSec);
  if (k <= 0) return null;
  const x = interpolate(t, [dispositivo, dispositivo + 0.35], [0, 1], { ...CLAMP, easing: (v) => v * v * (3 - 2 * v) });
  const encendido = interpolate(t, [manos, manos + 0.25], [0, 1], CLAMP);
  const W = 300;
  return (
    <div
      style={{
        position: "absolute",
        width: W,
        ...style,
        opacity: Math.min(1, k * 1.4),
        transform: `${style.transform ?? ""} translateY(${(1 - k) * 26}px)`,
      }}
    >
      <div
        style={{
          background: NOTA_BG,
          border: `3px solid ${COLORS.durazno}`,
          borderRadius: 30,
          padding: "16px 16px 18px",
          boxShadow: SOMBRA9,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 22,
            letterSpacing: "0.2em",
            color: COLORS.salvia,
            marginBottom: 12,
            textAlign: "center",
          }}
        >
          BRAZOS · PUEDES USAR
        </div>
        <div style={{ position: "relative", height: 62, borderRadius: 31, background: "rgba(69,89,90,.12)" }}>
          <div
            style={{
              position: "absolute",
              top: 4,
              left: 4 + x * (W - 40 - 8) * 0.5,
              width: (W - 40 - 8) * 0.5,
              height: 54,
              borderRadius: 27,
              background: COLORS.salvia,
              opacity: encendido,
              boxShadow: "0 6px 14px rgba(69,89,90,.3)",
            }}
          />
          {["Manos", "Equipo"].map((txt, i) => {
            const activo = i === 0 ? encendido * (1 - x) : x;
            return (
              <div
                key={txt}
                style={{
                  position: "absolute",
                  top: 0,
                  height: 62,
                  left: i * ((W - 40) / 2),
                  width: (W - 40) / 2,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: FONTS.body,
                  fontWeight: 700,
                  fontSize: 27,
                  color: activo > 0.5 ? COLORS.marfil : COLORS.petroleo,
                }}
              >
                {txt}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// ---------- Pantalla partida: "alternando ambos lados" ----------
export const Alterna: React.FC<{
  desde: number;
  hasta: number;
  /** Instantes en que cambia el lado activo (empieza el izquierdo). */
  cambios: number[];
  centros: [[number, number], [number, number]];
}> = ({ desde, hasta, cambios, centros }) => {
  const { t, frame, fps } = useT();
  if (t < desde || t >= hasta) return null;
  const linea = interpolate(t, [desde, desde + 0.35], [0, 1], CLAMP);
  const n = cambios.filter((c) => t >= c).length;
  const activo = n % 2; // 0: izquierdo, 1: derecho
  const ultimo = n ? cambios[n - 1] : desde;
  const f = interpolate(t, [ultimo, ultimo + 0.2], [0, 1], CLAMP);
  const kp = sube(frame, fps, desde + 0.3);
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      {[0, 1].map((lado) => {
        const on = lado === activo ? f : 1 - f;
        const [cx, cy] = centros[lado];
        const a = (t - desde) * 3.2 * (lado ? -1 : 1);
        return (
          <React.Fragment key={lado}>
            <div
              style={{
                position: "absolute",
                left: lado * 540,
                top: 0,
                width: 540,
                height: 1920,
                background: "rgba(46,60,61,.5)",
                opacity: n === 0 ? 0 : 1 - on,
              }}
            />
            <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, opacity: n === 0 ? 0.9 : 0.25 + 0.75 * on }}>
              <circle cx={cx} cy={cy} r={130} fill="none" stroke={COLORS.durazno} strokeWidth={9} strokeDasharray="30 22" transform={`rotate(${(a * 180) / Math.PI} ${cx} ${cy})`} />
              <path
                d={`M ${cx + 130} ${cy - 8} l -22 -26 m 22 26 l 26 -20`}
                stroke={COLORS.durazno}
                strokeWidth={9}
                fill="none"
                strokeLinecap="round"
                transform={`rotate(${(a * 180) / Math.PI} ${cx} ${cy})`}
              />
            </svg>
          </React.Fragment>
        );
      })}
      <div
        style={{
          position: "absolute",
          left: 535,
          top: 0,
          width: 10,
          height: 1920 * linea,
          background: COLORS.durazno,
          boxShadow: "0 0 18px rgba(69,89,90,.4)",
        }}
      />
      <div style={{ position: "absolute", left: 0, right: 0, top: 1330, display: "flex", justifyContent: "center", opacity: Math.min(1, kp * 1.4), transform: `scale(${0.7 + 0.3 * kp})` }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 32,
            letterSpacing: "0.16em",
            color: COLORS.petroleo,
            background: COLORS.durazno,
            borderRadius: 40,
            padding: "12px 30px 10px",
            boxShadow: SOMBRA9,
          }}
        >
          <svg width={40} height={30} viewBox="0 0 40 30">
            <path d="M4 10 H34 l-7 -7 M36 20 H6 l7 7" stroke={COLORS.petroleo} strokeWidth={4} fill="none" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          ALTERNA AMBOS LADOS
        </div>
      </div>
    </div>
  );
};

/** Destellos sobre todo el vídeo: blanco (congelado, con obturador) o Durazno ("¡Y listo!"). */
export const Destellos: React.FC<{ en: { t: number; color: string; max?: number }[] }> = ({ en }) => {
  const { frame, fps } = useT();
  return (
    <>
      {en.map((d) => {
        const k = frame - Math.round(d.t * fps);
        if (k < -1 || k > 9) return null;
        const o = interpolate(k, [-1, 0, 9], [0, d.max ?? 0.75, 0], CLAMP);
        return <div key={d.t} style={{ position: "absolute", inset: 0, background: d.color, opacity: o }} />;
      })}
    </>
  );
};
