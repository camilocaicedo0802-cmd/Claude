import React from "react";
import { interpolate } from "remotion";
import { COLORS, FONTS } from "../brand";
import { CLAMP, pop, useT } from "../rutinas/util";
import { TARJETA_ARRIBA } from "../dia9/Base9";
import { SOMBRA9 } from "../dia9/Graficos";

// Gráficos 2D de los vídeos complementarios (preparación manual del abdomen y de las piernas, cómo funciona el
// producto). Mismo lenguaje del día 9 (tarjeta de capítulo, notas claras, pizarra) con piezas nuevas: la barra de
// pasos de la preparación, el orden "1 masaje manual → 2 Luma Body", mapas 2D que se van dibujando (abdomen de frente
// y pierna de perfil: nada de maniquíes que giran, estilo.md §10.19), la respiración, el cronómetro de 1–2 minutos,
// el calor de las manos y una lista que se va marcando. Todo el texto a ≥ 30 px (§10.18); lo largo va como subtítulo.

const NOTA_BG = "rgba(245,240,236,0.95)";
const sube = (frame: number, fps: number, atSec: number) => pop(frame, fps, atSec, 15);
const suave = (x: number) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));

// ---------- Título de la tarjeta: kicker, título TAN Pearl y la barra de pasos de la preparación ----------
export type CapPrep = { desde: number; kicker: string; titulo: string };
export type PasoPrep = { nombre: string; at: number };

export const TituloPrep: React.FC<{ caps: CapPrep[]; pasos: PasoPrep[]; p: number }> = ({ caps, pasos, p }) => {
  const { t, frame, fps } = useT();
  if (p <= 0.01) return null;
  const cap = [...caps].reverse().find((c) => t >= c.desde - 0.01);
  if (!cap) return null;
  const k = sube(frame, fps, cap.desde);
  // El título se escribe de izquierda a derecha detrás de una línea Durazno que lo va descubriendo
  const rev = interpolate(t, [cap.desde + 0.1, cap.desde + 0.65], [0, 1], { ...CLAMP, easing: suave });
  const size = Math.min(112, 880 / (0.62 * cap.titulo.length));
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
        paddingBottom: 28,
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          fontFamily: FONTS.body,
          fontWeight: 700,
          fontSize: 30,
          letterSpacing: "0.2em",
          color: COLORS.marfil,
          background: COLORS.salvia,
          borderRadius: 30,
          padding: "8px 26px 6px",
          opacity: Math.min(1, k * 1.4),
          transform: `translateY(${(1 - k) * 20}px)`,
        }}
      >
        {cap.kicker}
      </div>
      <div style={{ position: "relative", marginTop: 10, marginBottom: 16 }}>
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: size,
            lineHeight: 1.08,
            color: COLORS.petroleo,
            whiteSpace: "nowrap",
            padding: "0 10px",
            clipPath: `inset(0 ${(1 - rev) * 100}% 0 0)`,
          }}
        >
          {cap.titulo}
        </div>
        <div
          style={{
            position: "absolute",
            bottom: -6,
            left: 10,
            height: 8,
            width: `calc(${rev * 100}% - 20px)`,
            background: COLORS.durazno,
            borderRadius: 4,
          }}
        />
      </div>
      <Pasos pasos={pasos} t={t} />
    </div>
  );
};

/** Barra de pasos: puntos unidos por una línea; el paso actual se llena de Salvia y los anteriores quedan marcados. */
const Pasos: React.FC<{ pasos: PasoPrep[]; t: number }> = ({ pasos, t }) => {
  const actual = pasos.reduce((acc, ps, i) => (t >= ps.at ? i : acc), -1);
  return (
    <div style={{ display: "flex", alignItems: "flex-start", gap: 0 }}>
      {pasos.map((ps, i) => {
        const on = interpolate(t, [ps.at, ps.at + 0.3], [0, 1], CLAMP);
        const hecho = i < actual;
        return (
          <React.Fragment key={ps.nombre}>
            {i > 0 ? (
              <div style={{ width: 34, height: 4, marginTop: 17, background: i <= actual ? COLORS.salvia : "rgba(69,89,90,.2)" }} />
            ) : null}
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 150 }}>
              <div
                style={{
                  width: 38,
                  height: 38,
                  borderRadius: 19,
                  boxSizing: "border-box",
                  border: `4px solid ${on > 0.5 || hecho ? COLORS.salvia : "rgba(69,89,90,.3)"}`,
                  background: hecho ? COLORS.salvia : `rgba(109,139,116,${on})`,
                  color: COLORS.marfil,
                  fontFamily: FONTS.body,
                  fontWeight: 700,
                  fontSize: 20,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  transform: `scale(${1 + 0.18 * on * (i === actual ? 1 : 0)})`,
                }}
              >
                {hecho ? "✓" : i + 1}
              </div>
              <div
                style={{
                  marginTop: 6,
                  fontFamily: FONTS.body,
                  fontWeight: 700,
                  fontSize: 21,
                  letterSpacing: "0.08em",
                  color: i === actual ? COLORS.petroleo : "rgba(69,89,90,.55)",
                  textAlign: "center",
                  whiteSpace: "nowrap",
                }}
              >
                {ps.nombre.toUpperCase()}
              </div>
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};

// ---------- Píldora del paso actual (cuando la tarjeta se ha cerrado) ----------
export const PildoraPaso: React.FC<{ pasos: PasoPrep[]; style: React.CSSProperties }> = ({ pasos, style }) => {
  const { t, frame, fps } = useT();
  const i = pasos.reduce((acc, ps, j) => (t >= ps.at ? j : acc), -1);
  if (i < 0) return null;
  const k = sube(frame, fps, pasos[i].at);
  return (
    <div style={{ position: "absolute", width: 300, ...style }}>
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 12,
          background: NOTA_BG,
          border: `3px solid ${COLORS.durazno}`,
          borderRadius: 32,
          padding: "8px 18px 8px 8px",
          boxShadow: SOMBRA9,
          transform: `scale(${0.85 + 0.15 * k})`,
          transformOrigin: "0 50%",
        }}
      >
        <div
          style={{
            width: 42,
            height: 42,
            borderRadius: 21,
            background: COLORS.salvia,
            color: COLORS.marfil,
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 24,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {i + 1}
        </div>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 30, letterSpacing: "0.06em", color: COLORS.petroleo }}>
          {pasos[i].nombre}
        </div>
      </div>
    </div>
  );
};

// ---------- Orden: 1 masaje manual → 2 Luma Body ----------
// "manual": se enciende el paso 1 (es lo que se hace ahora). "luma": el paso 2 solo late cuando se nombra (va
// después); "lumaEncendido": se enciende al final, cuando la piel ya está lista.
export const Orden: React.FC<{ at: number; manual: number; luma: number; lumaEncendido?: number; style: React.CSSProperties }> = ({
  at: atSec,
  manual,
  luma,
  lumaEncendido,
  style,
}) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, atSec);
  if (k <= 0) return null;
  const fila = (n: string, texto: string, on: number, icono: React.ReactNode) => (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 14,
        padding: "12px 16px",
        borderRadius: 24,
        background: on > 0.5 ? COLORS.salvia : NOTA_BG,
        border: `3px solid ${on > 0.5 ? COLORS.salvia : COLORS.durazno}`,
        transform: `scale(${1 + 0.05 * on})`,
        boxShadow: SOMBRA9,
      }}
    >
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: 20,
          background: on > 0.5 ? COLORS.marfil : COLORS.petroleo,
          color: on > 0.5 ? COLORS.salvia : COLORS.marfil,
          fontFamily: FONTS.body,
          fontWeight: 700,
          fontSize: 23,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        {n}
      </div>
      <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 30, color: on > 0.5 ? COLORS.marfil : COLORS.petroleo, lineHeight: 1.05 }}>
        {texto}
      </div>
      <div style={{ marginLeft: "auto" }}>{icono}</div>
    </div>
  );
  const onManual = interpolate(t, [manual, manual + 0.3], [0, 1], CLAMP);
  const late = interpolate(t, [luma, luma + 0.18, luma + 0.5], [0, 1, 0], CLAMP);
  const onLuma = lumaEncendido === undefined ? 0 : interpolate(t, [lumaEncendido, lumaEncendido + 0.3], [0, 1], CLAMP);
  const flecha = interpolate(t, [atSec + 0.3, atSec + 0.7], [0, 1], CLAMP);
  return (
    <div style={{ position: "absolute", width: 300, ...style, opacity: Math.min(1, k * 1.4), transform: `${style.transform ?? ""} translateY(${(1 - k) * 24}px)` }}>
      {fila("1", "Masaje manual", onManual, <Manos color={onManual > 0.5 ? COLORS.marfil : COLORS.petroleo} />)}
      <svg width={300} height={46} style={{ display: "block" }}>
        <path
          d="M150 6 L150 34 M140 25 L150 37 L160 25"
          stroke={COLORS.petroleo}
          strokeWidth={4}
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - flecha}
        />
      </svg>
      <div style={{ transform: `scale(${1 + 0.08 * late})`, transformOrigin: "50% 50%" }}>
        {fila("2", "Luma Body", onLuma, <Equipo color={onLuma > 0.5 ? COLORS.marfil : COLORS.petroleo} />)}
      </div>
    </div>
  );
};

const Manos: React.FC<{ color: string }> = ({ color }) => (
  <svg width={40} height={40} viewBox="0 0 40 40">
    <path
      d="M8 30 C6 24 6 16 9 11 C10 9 13 10 12 13 L11 19 M12 13 L14 7 C15 5 18 6 17 9 L16 16 M17 9 L19 5 C20 3 23 4 22 7 L20 16 M22 7 L24 6 C26 5 27 7 26 9 L23 18 C27 16 31 17 31 20 C27 22 24 26 22 31 C20 35 12 35 8 30 Z"
      stroke={color}
      strokeWidth={2.6}
      fill="none"
      strokeLinejoin="round"
      strokeLinecap="round"
    />
  </svg>
);
const Equipo: React.FC<{ color: string }> = ({ color }) => (
  <svg width={40} height={40} viewBox="0 0 40 40">
    <ellipse cx={20} cy={27} rx={15} ry={7} stroke={color} strokeWidth={2.6} fill="none" />
    <path d="M7 26 L9 14 C10 9 30 9 31 14 L33 26" stroke={color} strokeWidth={2.6} fill="none" strokeLinejoin="round" />
    <circle cx={20} cy={15} r={3.2} fill={color} />
  </svg>
);

// ---------- Mapa del abdomen (2D, de frente): parte baja, costados → frente, círculos alrededor del ombligo ----------
export type ModoAbdomen = "nada" | "baja" | "costados" | "ombligo";
export const MapaAbdomen: React.FC<{
  desde: number;
  pasos: { t: number; modo: ModoAbdomen }[];
  style: React.CSSProperties;
}> = ({ desde, pasos, style }) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, desde);
  if (k <= 0) return null;
  let i = 0;
  while (i + 1 < pasos.length && pasos[i + 1].t <= t) i++;
  const modo = pasos[i].modo;
  const dt = t - pasos[i].t;
  const f = suave(dt / 0.5);
  const W = 260;
  const H = 300;
  // Silueta del tronco (de bajo el pecho a la parte alta de los muslos) en un lienzo 200×230
  const TRONCO =
    "M 52 10 C 46 40 40 70 44 100 C 46 118 40 138 34 160 C 30 176 32 200 40 226 L 92 226 C 94 214 98 204 100 196 C 102 204 106 214 108 226 L 160 226 C 168 200 170 176 166 160 C 160 138 154 118 156 100 C 160 70 154 40 148 10 Z";
  const ombligo = { x: 100, y: 108 };
  const giro = (dt * 2.2) % 1; // el punto que da círculos
  return (
    <div style={{ position: "absolute", width: W, ...style, opacity: Math.min(1, k * 1.4), transform: `${style.transform ?? ""} scale(${0.9 + 0.1 * k})` }}>
      <div style={{ background: "rgba(69,89,90,0.92)", borderRadius: 30, padding: "12px 14px 8px", boxShadow: SOMBRA9 }}>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 24, letterSpacing: "0.16em", color: COLORS.durazno, textAlign: "center" }}>
          {modo === "baja" ? "PARTE BAJA" : modo === "costados" ? "COSTADOS → FRENTE" : modo === "ombligo" ? "ALREDEDOR" : "ABDOMEN"}
        </div>
        <svg width={W - 28} height={H - 60} viewBox="0 0 200 230">
          <path d={TRONCO} fill="rgba(250,237,205,0.18)" stroke={COLORS.durazno} strokeWidth={2.5} />
          {/* ropa interior como referencia */}
          <path d="M 38 176 C 70 186 130 186 162 176 L 160 200 C 130 206 112 214 100 222 C 88 214 70 206 40 200 Z" fill="rgba(69,89,90,0.9)" stroke={COLORS.durazno} strokeWidth={1.5} />
          <circle cx={ombligo.x} cy={ombligo.y} r={3.5} fill={COLORS.durazno} />
          {modo === "baja" ? (
            <>
              {/* franja baja junto a la ingle, encendida, con dos círculos suaves */}
              <path d="M 50 140 C 80 150 120 150 150 140 L 156 172 C 120 182 80 182 44 172 Z" fill={`rgba(109,139,116,${0.75 * f})`} />
              {[70, 130].map((cx) => (
                <g key={cx} opacity={f}>
                  <circle cx={cx} cy={158} r={13} fill="none" stroke={COLORS.marfil} strokeWidth={2.5} strokeDasharray="5 4" />
                  <circle cx={cx + 13 * Math.cos(giro * 6.283)} cy={158 + 13 * Math.sin(giro * 6.283)} r={4} fill={COLORS.marfil} />
                </g>
              ))}
            </>
          ) : null}
          {modo === "costados" ? (
            <>
              <path d="M 44 100 C 46 118 40 138 34 160 L 70 160 L 76 100 Z" fill={`rgba(109,139,116,${0.6 * f})`} />
              <path d="M 156 100 C 154 118 160 138 166 160 L 130 160 L 124 100 Z" fill={`rgba(109,139,116,${0.6 * f})`} />
              {[
                [44, 130, 90, 132],
                [156, 130, 110, 132],
              ].map(([x1, y1, x2, y2], j) => {
                const a = suave((dt - 0.2 - j * 0.15) / 0.6);
                const x = x1 + (x2 - x1) * a;
                return (
                  <g key={j}>
                    <line x1={x1} y1={y1} x2={x} y2={y1 + (y2 - y1) * a} stroke={COLORS.marfil} strokeWidth={4} strokeLinecap="round" />
                    {a > 0.9 ? <path d={j === 0 ? `M ${x2 - 9} ${y2 - 8} L ${x2} ${y2} L ${x2 - 9} ${y2 + 8}` : `M ${x2 + 9} ${y2 - 8} L ${x2} ${y2} L ${x2 + 9} ${y2 + 8}`} stroke={COLORS.marfil} strokeWidth={4} fill="none" strokeLinecap="round" strokeLinejoin="round" /> : null}
                  </g>
                );
              })}
            </>
          ) : null}
          {modo === "ombligo" ? (
            <>
              <circle cx={ombligo.x} cy={ombligo.y} r={38} fill={`rgba(109,139,116,${0.45 * f})`} />
              <circle cx={ombligo.x} cy={ombligo.y} r={38} fill="none" stroke={COLORS.marfil} strokeWidth={3} strokeDasharray="7 5" opacity={f} />
              <circle cx={ombligo.x + 38 * Math.cos(giro * 6.283)} cy={ombligo.y + 38 * Math.sin(giro * 6.283)} r={6} fill={COLORS.marfil} opacity={f} />
              {/* prohibido sobre el ombligo */}
              <g opacity={suave((dt - 0.6) / 0.3)}>
                <circle cx={ombligo.x} cy={ombligo.y} r={12} fill="rgba(69,89,90,.9)" stroke={COLORS.durazno} strokeWidth={3} />
                <line x1={ombligo.x - 8} y1={ombligo.y + 8} x2={ombligo.x + 8} y2={ombligo.y - 8} stroke={COLORS.durazno} strokeWidth={3} />
              </g>
            </>
          ) : null}
        </svg>
      </div>
    </div>
  );
};

// ---------- Pierna de perfil (2D): ruta del masaje del tobillo a la ingle ----------
export type ModoPierna = "nada" | "pantorrilla" | "rodilla" | "muslo" | "ingle" | "otra";
export const RutaPierna: React.FC<{
  desde: number;
  pasos: { t: number; modo: ModoPierna }[];
  style: React.CSSProperties;
}> = ({ desde, pasos, style }) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, desde);
  if (k <= 0) return null;
  let i = 0;
  while (i + 1 < pasos.length && pasos[i + 1].t <= t) i++;
  const modo = pasos[i].modo;
  const dt = t - pasos[i].t;
  const W = 240;
  // Pierna de perfil en un lienzo 160×300: cadera arriba, rodilla en (78, 150), tobillo en (70, 262), pie a la derecha
  const PIERNA =
    "M 48 8 L 112 8 C 116 40 108 90 100 128 C 98 140 100 150 98 160 C 96 176 102 196 98 220 C 96 236 90 250 88 262 L 120 272 C 130 276 132 290 120 292 L 62 292 C 56 292 54 282 56 270 C 54 250 50 230 50 210 C 48 188 52 172 56 158 C 56 148 54 140 52 128 C 44 90 42 50 48 8 Z";
  const ascender = (y0: number, y1: number, x: number, a: number) => (
    <g>
      <line x1={x} y1={y0} x2={x} y2={y0 + (y1 - y0) * a} stroke={COLORS.marfil} strokeWidth={4.5} strokeLinecap="round" />
      {a > 0.95 ? <path d={`M ${x - 8} ${y1 + 9} L ${x} ${y1} L ${x + 8} ${y1 + 9}`} stroke={COLORS.marfil} strokeWidth={4.5} fill="none" strokeLinecap="round" strokeLinejoin="round" /> : null}
    </g>
  );
  const tope = (y: number, x0: number, x1: number, o: number) => (
    <line x1={x0} y1={y} x2={x1} y2={y} stroke={COLORS.durazno} strokeWidth={5} strokeLinecap="round" opacity={o} />
  );
  const a = suave((dt - 0.15) / 0.9);
  const giro = (dt * 2.2) % 1;
  const zona = (d: string, o: number) => <path d={d} fill={`rgba(109,139,116,${0.7 * o})`} />;
  const titulo: Record<ModoPierna, string> = {
    nada: "PIERNA",
    pantorrilla: "PANTORRILLA",
    rodilla: "TRAS LA RODILLA",
    muslo: "MUSLO",
    ingle: "ANTES DE LA INGLE",
    otra: "OTRA PIERNA",
  };
  const f = suave(dt / 0.4);
  return (
    <div style={{ position: "absolute", width: W, ...style, opacity: Math.min(1, k * 1.4), transform: `${style.transform ?? ""} scale(${0.9 + 0.1 * k})` }}>
      <div style={{ background: "rgba(69,89,90,0.92)", borderRadius: 30, padding: "12px 14px 8px", boxShadow: SOMBRA9 }}>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 23, letterSpacing: "0.14em", color: COLORS.durazno, textAlign: "center", whiteSpace: "nowrap" }}>
          {titulo[modo]}
        </div>
        <svg width={W - 28} height={300} viewBox="0 0 160 300" style={{ transform: modo === "otra" ? `scaleX(${Math.cos(Math.min(1, dt / 0.5) * Math.PI)})` : undefined }}>
          <path d={PIERNA} fill="rgba(250,237,205,0.18)" stroke={COLORS.durazno} strokeWidth={2.5} />
          <circle cx={78} cy={150} r={3} fill={COLORS.durazno} />
          {modo === "pantorrilla" ? (
            <>
              {zona("M 56 172 C 52 196 54 226 58 258 L 92 258 C 96 230 100 200 96 172 Z", f)}
              {ascender(258, 178, 76, a)}
              {tope(170, 56, 96, suave((dt - 0.9) / 0.3))}
            </>
          ) : null}
          {modo === "rodilla" ? (
            <>
              {zona("M 54 140 C 50 152 52 164 56 172 L 76 172 L 76 140 Z", f)}
              <circle cx={64} cy={156} r={13} fill="none" stroke={COLORS.marfil} strokeWidth={2.5} strokeDasharray="5 4" opacity={f} />
              <circle cx={64 + 13 * Math.cos(giro * 6.283)} cy={156 + 13 * Math.sin(giro * 6.283)} r={4.5} fill={COLORS.marfil} opacity={f} />
            </>
          ) : null}
          {modo === "muslo" || modo === "ingle" ? (
            <>
              {zona("M 50 30 C 44 70 48 100 54 132 L 100 132 C 108 100 114 60 112 30 Z", modo === "muslo" ? f : 1)}
              {ascender(134, 46, 80, modo === "muslo" ? a : 1)}
              {tope(36, 48, 112, modo === "ingle" ? f : 0)}
              {modo === "ingle" ? <rect x={48} y={8} width={64} height={26} fill={`rgba(250,237,205,${0.25 * f})`} /> : null}
            </>
          ) : null}
        </svg>
      </div>
    </div>
  );
};

// ---------- Respiración: un círculo que se llena (inhala) y se vacía (exhala), 4 s por ciclo ----------
export const Respira: React.FC<{ at: number; style: React.CSSProperties }> = ({ at: atSec, style }) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, atSec);
  if (k <= 0) return null;
  const fase = ((t - atSec) % 4) / 4; // 0–0,5 inhala, 0,5–1 exhala
  const inhala = fase < 0.5;
  const r = 52 + 34 * (inhala ? suave(fase / 0.5) : 1 - suave((fase - 0.5) / 0.5));
  return (
    <div style={{ position: "absolute", width: 260, ...style, opacity: Math.min(1, k * 1.4) }}>
      <div style={{ background: NOTA_BG, border: `3px solid ${COLORS.durazno}`, borderRadius: 30, padding: "12px 0 14px", boxShadow: SOMBRA9, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <svg width={200} height={190} viewBox="0 0 200 190">
          <circle cx={100} cy={95} r={86} fill="none" stroke="rgba(109,139,116,.25)" strokeWidth={3} strokeDasharray="6 6" />
          <circle cx={100} cy={95} r={r} fill="rgba(109,139,116,.85)" />
          <circle cx={100} cy={95} r={r * 0.62} fill="rgba(250,237,205,.5)" />
        </svg>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 32, letterSpacing: "0.12em", color: COLORS.petroleo, marginTop: 4 }}>
          {inhala ? "INHALA" : "EXHALA"}
        </div>
      </div>
    </div>
  );
};

// ---------- Cronómetro "1–2 min": la aguja da la vuelta y los minutos cuentan hasta 2 ----------
export const Cronometro: React.FC<{ at: number; hasta: number; style: React.CSSProperties }> = ({ at: atSec, hasta, style }) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, atSec);
  if (k <= 0) return null;
  const p = interpolate(t, [atSec + 0.3, hasta - 0.3], [0, 1], CLAMP);
  const seg = Math.round(p * 120);
  const ang = (seg / 60) * 2 * Math.PI;
  return (
    <div style={{ position: "absolute", width: 260, ...style, opacity: Math.min(1, k * 1.4), transform: `${style.transform ?? ""} scale(${0.9 + 0.1 * k})` }}>
      <div style={{ background: NOTA_BG, border: `3px solid ${COLORS.durazno}`, borderRadius: 30, padding: "14px 0 12px", boxShadow: SOMBRA9, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <svg width={180} height={180} viewBox="0 0 180 180">
          <rect x={80} y={0} width={20} height={14} rx={4} fill={COLORS.petroleo} />
          <circle cx={90} cy={98} r={74} fill="#FFFFFF" stroke={COLORS.petroleo} strokeWidth={6} />
          <circle
            cx={90}
            cy={98}
            r={64}
            fill="none"
            stroke={COLORS.salvia}
            strokeWidth={12}
            strokeDasharray={2 * Math.PI * 64}
            strokeDashoffset={2 * Math.PI * 64 * (1 - p)}
            transform="rotate(-90 90 98)"
            strokeLinecap="round"
          />
          <line x1={90} y1={98} x2={90 + 50 * Math.sin(ang)} y2={98 - 50 * Math.cos(ang)} stroke={COLORS.petroleo} strokeWidth={5} strokeLinecap="round" />
          <circle cx={90} cy={98} r={6} fill={COLORS.petroleo} />
        </svg>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 40, color: COLORS.petroleo, marginTop: 2 }}>
          {Math.floor(seg / 60)}:{String(seg % 60).padStart(2, "0")}
        </div>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 26, letterSpacing: "0.16em", color: COLORS.salvia }}>1–2 MIN</div>
      </div>
    </div>
  );
};

// ---------- Calor: ondas que suben de las palmas ----------
export const Calor: React.FC<{ at: number; style: React.CSSProperties }> = ({ at: atSec, style }) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, atSec);
  if (k <= 0) return null;
  const dt = t - atSec;
  return (
    <div style={{ position: "absolute", width: 260, ...style, opacity: Math.min(1, k * 1.4) }}>
      <div style={{ background: NOTA_BG, border: `3px solid ${COLORS.durazno}`, borderRadius: 30, padding: "10px 0 12px", boxShadow: SOMBRA9, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <svg width={200} height={150} viewBox="0 0 200 150">
          {[0, 1, 2].map((j) => {
            const fase = (dt * 0.9 + j / 3) % 1;
            const y = 110 - fase * 90;
            const x = 60 + j * 40;
            return (
              <path
                key={j}
                d={`M ${x} ${y + 30} C ${x - 12} ${y + 20} ${x + 12} ${y + 10} ${x} ${y}`}
                stroke={j === 1 ? COLORS.salvia : "#D9A15E"}
                strokeWidth={6}
                fill="none"
                strokeLinecap="round"
                opacity={Math.sin(fase * Math.PI)}
              />
            );
          })}
          {/* palmas juntas */}
          <path d="M 70 150 C 72 128 86 118 100 112 C 114 118 128 128 130 150 Z" fill={COLORS.durazno} stroke={COLORS.petroleo} strokeWidth={3} />
          <line x1={100} y1={113} x2={100} y2={150} stroke={COLORS.petroleo} strokeWidth={3} />
        </svg>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 30, letterSpacing: "0.1em", color: COLORS.petroleo }}>CALIENTA</div>
      </div>
    </div>
  );
};

// ---------- Lista que se va marcando (cada elemento en su palabra) ----------
export const Checks: React.FC<{ titulo?: string; items: { texto: string; at: number }[]; style: React.CSSProperties }> = ({
  titulo,
  items,
  style,
}) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, items[0].at - 0.1);
  if (k <= 0) return null;
  return (
    <div style={{ position: "absolute", width: 280, ...style, opacity: Math.min(1, k * 1.4) }}>
      <div style={{ background: NOTA_BG, border: `3px solid ${COLORS.durazno}`, borderRadius: 30, padding: "14px 18px 10px", boxShadow: SOMBRA9 }}>
        {titulo ? (
          <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 24, letterSpacing: "0.16em", color: COLORS.salvia, marginBottom: 4 }}>{titulo}</div>
        ) : null}
        {items.map((it) => {
          const on = interpolate(t, [it.at, it.at + 0.25], [0, 1], CLAMP);
          return (
            <div key={it.texto} style={{ display: "flex", alignItems: "center", gap: 12, padding: "6px 0", opacity: 0.35 + 0.65 * on }}>
              <svg width={36} height={36} viewBox="0 0 36 36" style={{ flexShrink: 0 }}>
                <circle cx={18} cy={18} r={16} fill={on > 0.5 ? COLORS.salvia : "rgba(69,89,90,.15)"} />
                <path d="M10 18.5 L16 24 L26 12" stroke={COLORS.marfil} strokeWidth={4} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={26} strokeDashoffset={26 * (1 - on)} />
              </svg>
              <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 32, color: COLORS.petroleo }}>{it.texto}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ---------- Panel del Luma Body (2D, como el real): ovalado negro, Heat y Negative pressure, Power rojo y barras ----------
// "encendido": la pantalla se enciende (Power). "calor": el botón Heat y su luz roja; "nivelCalor": barras rojas de la
// izquierda (0–5). "succion": niveles de succión de la derecha [instante, nivel]; "pulsa": instantes en que un dedo
// pulsa un botón (efecto de pulsación). "resalta": botón que se rodea con un anillo Durazno.
export type BotonLuma = "power" | "heat" | "presion";
export const PanelLuma: React.FC<{
  at: number;
  encendido: number;
  calor?: number;
  nivelesCalor?: [number, number][];
  succion?: [number, number][];
  pulsa?: [number, BotonLuma][];
  resalta?: [number, number, BotonLuma][];
  ancho?: number;
  style: React.CSSProperties;
}> = ({ at: atSec, encendido, calor, nivelesCalor = [], succion = [], pulsa = [], resalta = [], ancho = 340, style }) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, atSec);
  if (k <= 0) return null;
  const on = interpolate(t, [encendido, encendido + 0.3], [0, 1], CLAMP);
  const heat = calor === undefined ? 0 : interpolate(t, [calor, calor + 0.25], [0, 1], CLAMP);
  const nivel = (lista: [number, number][]) => lista.reduce((acc, [ts, n]) => (t >= ts ? n : acc), 0);
  const nC = nivel(nivelesCalor);
  const nS = nivel(succion);
  const pulsado = (b: BotonLuma) =>
    pulsa.reduce((acc, [ts, bb]) => (bb === b ? Math.max(acc, interpolate(t, [ts, ts + 0.08, ts + 0.3], [0, 1, 0], CLAMP)) : acc), 0);
  const anillo = (b: BotonLuma) =>
    resalta.reduce((acc, [a, z, bb]) => (bb === b ? Math.max(acc, interpolate(t, [a, a + 0.2, z - 0.2, z], [0, 1, 1, 0], CLAMP)) : acc), 0);
  const W = 300;
  const H = 360;
  const BOT = { heat: { x: 105, y: 190 }, presion: { x: 195, y: 190 }, power: { x: 150, y: 262 } };
  // Barras en arco a cada lado (5 por lado)
  const barras = (lado: -1 | 1, n: number, color: string) =>
    Array.from({ length: 5 }, (_, i) => {
      const a = (lado === -1 ? Math.PI : 0) + lado * (-0.62 + i * 0.31);
      const r0 = 112;
      const r1 = 128;
      const cx = 150;
      const cy = 180;
      const encend = on > 0.5 && i < n;
      return (
        <line
          key={`${lado}${i}`}
          x1={cx + r0 * Math.cos(a)}
          y1={cy - r0 * Math.sin(a) * 1.25}
          x2={cx + r1 * Math.cos(a)}
          y2={cy - r1 * Math.sin(a) * 1.25}
          stroke={encend ? color : "rgba(255,255,255,.18)"}
          strokeWidth={9}
          strokeLinecap="round"
        />
      );
    });
  const triangulo = (x: number, y: number, b: BotonLuma, luz: number) => (
    <g transform={`translate(${x} ${y}) scale(${1 - 0.12 * pulsado(b)})`}>
      <circle r={24} fill={luz > 0.5 ? "rgba(255,255,255,.95)" : "rgba(255,255,255,.12)"} stroke="rgba(255,255,255,.6)" strokeWidth={2} />
      <path d="M -10 7 L 0 -9 L 10 7 Z" fill={luz > 0.5 ? "#1D2526" : "rgba(255,255,255,.75)"} />
      {anillo(b) > 0 ? <circle r={30} fill="none" stroke={COLORS.durazno} strokeWidth={5} opacity={anillo(b)} /> : null}
    </g>
  );
  return (
    <div style={{ position: "absolute", width: ancho, ...style, opacity: Math.min(1, k * 1.4), transform: `${style.transform ?? ""} scale(${0.88 + 0.12 * k})` }}>
      <svg width={ancho} height={(ancho * H) / W} viewBox={`0 0 ${W} ${H}`}>
        {/* cuerpo blanco con aro dorado */}
        <ellipse cx={150} cy={185} rx={146} ry={172} fill="#F7F5F2" stroke="#C9A35B" strokeWidth={6} />
        {/* panel negro */}
        <ellipse cx={150} cy={182} rx={104} ry={136} fill="#141A1B" />
        <text x={150} y={92} textAnchor="middle" fontFamily="Glacial Indifference, sans-serif" fontWeight={700} fontSize={20} letterSpacing={2} fill={`rgba(255,255,255,${0.35 + 0.65 * on})`}>
          LUMA BODY
        </text>
        {barras(-1, nC, "#E0473B")}
        {barras(1, nS, COLORS.salvia)}
        {triangulo(BOT.heat.x, BOT.heat.y, "heat", heat)}
        {triangulo(BOT.presion.x, BOT.presion.y, "presion", nS > 0 ? 1 : 0)}
        <text x={BOT.heat.x} y={BOT.heat.y + 46} textAnchor="middle" fontFamily="Glacial Indifference, sans-serif" fontWeight={700} fontSize={19} fill="rgba(255,255,255,.9)">Heat</text>
        <text x={BOT.presion.x} y={BOT.presion.y + 45} textAnchor="middle" fontFamily="Glacial Indifference, sans-serif" fontWeight={700} fontSize={16} fill="rgba(255,255,255,.9)">
          <tspan x={BOT.presion.x}>Negative</tspan>
          <tspan x={BOT.presion.x} dy={16}>pressure</tspan>
        </text>
        {/* Power: rojo */}
        <g transform={`translate(${BOT.power.x} ${BOT.power.y}) scale(${1 - 0.12 * pulsado("power")})`}>
          <circle r={20} fill={on > 0.5 ? "#E0473B" : "#7A2A24"} stroke="rgba(255,255,255,.6)" strokeWidth={2} />
          <path d="M -6 -5 A 8 8 0 1 0 6 -5 M 0 -10 L 0 -1" stroke="#FFFFFF" strokeWidth={2.5} fill="none" strokeLinecap="round" />
          {anillo("power") > 0 ? <circle r={30} fill="none" stroke={COLORS.durazno} strokeWidth={5} opacity={anillo("power")} /> : null}
        </g>
        <text x={BOT.power.x} y={BOT.power.y + 36} textAnchor="middle" fontFamily="Glacial Indifference, sans-serif" fontWeight={700} fontSize={19} fill="rgba(255,255,255,.9)">Power</text>
        {/* luz roja del calor */}
        <circle cx={150} cy={130} r={7} fill="#E0473B" opacity={heat} />
        <circle cx={150} cy={130} r={16} fill="#E0473B" opacity={0.25 * heat * (0.6 + 0.4 * Math.sin(t * 6))} />
      </svg>
    </div>
  );
};

// ---------- Niveles 1–5 con el rango recomendado resaltado ("comienza entre los niveles 1 a 3") ----------
export const Niveles: React.FC<{ at: number; rango: [number, number]; resalta: number; titulo: string; style: React.CSSProperties }> = ({
  at: atSec,
  rango,
  resalta,
  titulo,
  style,
}) => {
  const { t, frame, fps } = useT();
  const k = sube(frame, fps, atSec);
  if (k <= 0) return null;
  const on = interpolate(t, [resalta, resalta + 0.35], [0, 1], CLAMP);
  return (
    <div style={{ position: "absolute", width: 300, ...style, opacity: Math.min(1, k * 1.4), transform: `${style.transform ?? ""} translateY(${(1 - k) * 24}px)` }}>
      <div style={{ background: NOTA_BG, border: `3px solid ${COLORS.durazno}`, borderRadius: 30, padding: "14px 16px 12px", boxShadow: SOMBRA9 }}>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 24, letterSpacing: "0.16em", color: COLORS.salvia, textAlign: "center" }}>{titulo}</div>
        <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "center", gap: 8, marginTop: 10, height: 120 }}>
          {[1, 2, 3, 4, 5].map((n) => {
            const dentro = n >= rango[0] && n <= rango[1];
            const aparece = interpolate(t, [atSec + 0.1 + n * 0.08, atSec + 0.3 + n * 0.08], [0, 1], CLAMP);
            return (
              <div key={n} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
                <div
                  style={{
                    width: 40,
                    height: (30 + n * 17) * aparece,
                    borderRadius: 10,
                    background: dentro && on > 0.5 ? COLORS.salvia : "rgba(69,89,90,.18)",
                    transform: `scale(${dentro ? 1 + 0.08 * on : 1})`,
                  }}
                />
                <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 30, color: dentro && on > 0.5 ? COLORS.petroleo : "rgba(69,89,90,.45)" }}>{n}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
