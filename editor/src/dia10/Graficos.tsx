import { Video } from "@remotion/media";
import React from "react";
import { Img, interpolate, Sequence, spring, staticFile } from "remotion";
import { COLORS, FONTS } from "../brand";
import { useCaras, zonasEn } from "../rutinas/Caras";
import { CLAMP, pop, useT } from "../rutinas/util";

// Gráficos 2D del día 10 "Día 21 y continuidad" (último del reto). Lenguaje nuevo frente a los días 1–9: títulos
// "pegatina" que se pegan con un golpe, ventana con la forma del 21 para abrir y cambiar de bloque, panel lateral
// Marfil (la toma se desliza) para los bloques con más contenido, inserciones de cámara de móvil para las fotos,
// anillo de 21 días que se completa, ficha de medidas que se rellena, Día 1 / Día 21 lado a lado y mensajes de chat.

export const SOMBRA10 = "0 16px 36px rgba(69,89,90,.3), 0 4px 10px rgba(69,89,90,.2)";
const golpe = (frame: number, fps: number, atSec: number) => {
  const f = frame - Math.round(atSec * fps);
  if (f < 0) return 0;
  return spring({ frame: f, fps, config: { damping: 9, stiffness: 190, mass: 0.7 } });
};

// ---------- Título pegatina ----------
/** Kicker en etiqueta Petróleo + título TAN Pearl sobre una pegatina Durazno con borde blanco, que se pega con un golpe. */
export const Pegatina: React.FC<{
  at: number;
  kicker?: string;
  texto: string;
  size: number;
  giro?: number;
  salida?: number;
  kickerSize?: number;
}> = ({ at: atSec, kicker, texto, size, giro = -3, salida, kickerSize = 30 }) => {
  const { frame, fps, t } = useT();
  const k = golpe(frame, fps, atSec);
  const kk = golpe(frame, fps, atSec - 0.12);
  const fuera = salida === undefined ? 0 : interpolate(t, [salida - 0.25, salida], [0, 1], CLAMP);
  if (k <= 0 && kk <= 0) return null;
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        opacity: 1 - fuera,
        transform: `scale(${1 - 0.25 * fuera})`,
      }}
    >
      {kicker ? (
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: kickerSize,
            letterSpacing: "0.2em",
            whiteSpace: "nowrap",
            color: COLORS.durazno,
            background: COLORS.petroleo,
            borderRadius: 12,
            padding: "8px 18px 6px",
            marginBottom: -10,
            zIndex: 1,
            boxShadow: SOMBRA10,
            opacity: Math.min(1, kk * 1.4),
            transform: `rotate(${3 - (1 - kk) * 10}deg) scale(${0.6 + 0.4 * kk})`,
          }}
        >
          {kicker}
        </div>
      ) : null}
      <div
        style={{
          fontFamily: FONTS.display,
          fontSize: size,
          lineHeight: 1.05,
          color: COLORS.petroleo,
          background: COLORS.durazno,
          border: `9px solid ${COLORS.marfil}`,
          borderRadius: 34,
          padding: `${size * 0.08}px ${size * 0.3}px ${size * 0.14}px`,
          whiteSpace: "nowrap",
          boxShadow: SOMBRA10,
          opacity: Math.min(1, k * 2),
          transform: `rotate(${giro - (1 - k) * 12}deg) scale(${1.6 - 0.6 * k})`,
        }}
      >
        {texto.split(/(\d+)/).map((parte, i) =>
          /^\d+$/.test(parte) ? (
            <span key={i} style={{ fontFamily: FONTS.body, fontWeight: 700 }}>
              {parte}
            </span>
          ) : (
            <React.Fragment key={i}>{parte}</React.Fragment>
          ),
        )}
      </div>
    </div>
  );
};

/** Título sobre la cabeza: la pegatina se apoya encima de la zona prohibida de la cara (nunca la toca). */
export const TituloArriba: React.FC<{
  desde: number;
  hasta: number;
  at?: number;
  kicker?: string;
  texto: string;
}> = ({ desde, hasta, at: atSec, kicker, texto }) => {
  const caras = useCaras();
  const { t } = useT();
  if (t < desde || t >= hasta) return null;
  const { actual } = zonasEn(caras, t, desde, hasta);
  const alto = actual.y0 - 40;
  const size = Math.min(104, (alto - (kicker ? 50 : 0)) / 1.4, 880 / (0.66 * texto.length + 0.6));
  if (size < 46) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 40,
        height: alto,
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-end",
        alignItems: "center",
      }}
    >
      <Pegatina at={atSec ?? desde} kicker={kicker} texto={texto} size={size} salida={hasta} />
    </div>
  );
};

// ---------- Ventana "21": la toma aparece a través de un 21 que crece ----------
export const Ventana21: React.FC<{ en: { t: number; cierra?: boolean }[]; cx?: number; cy?: number }> = ({
  en,
  cx = 540,
  cy = 780,
}) => {
  const { t } = useT();
  return (
    <>
      {en.map((v) => {
        // Cierra (0,35 s antes): el Marfil entra desde los bordes hasta dejar solo un 21; abre: el 21 crece y desaparece
        const a = v.cierra ? interpolate(t, [v.t - 0.35, v.t], [0, 1], CLAMP) : 1;
        const b = interpolate(t, [v.t, v.t + 0.75], [0, 1], { ...CLAMP, easing: (x) => x * x * x });
        if (t < v.t - (v.cierra ? 0.35 : 0) || b >= 1) return null;
        const escala = t < v.t ? 30 - 29 * a : 1 + 40 * b;
        const id = `v21_${Math.round(v.t * 100)}`;
        return (
          <svg key={v.t} width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
            <defs>
              <mask id={id}>
                <rect width={1080} height={1920} fill="white" />
                <text
                  x={cx}
                  y={cy}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontFamily="'Glacial Indifference'"
                  fontWeight={700}
                  fontSize={420}
                  fill="black"
                  transform={`translate(${cx} ${cy}) scale(${escala}) translate(${-cx} ${-cy})`}
                >
                  21
                </text>
              </mask>
            </defs>
            <rect width={1080} height={1920} fill={COLORS.marfil} mask={`url(#${id})`} />
          </svg>
        );
      })}
    </>
  );
};

// ---------- Anillo de 21 días: "pudiste hacer de esto una rutina" ----------
export const Anillo21: React.FC<{ at: number; completo: number; style: React.CSSProperties }> = ({
  at: atSec,
  completo,
  style,
}) => {
  const { t, frame, fps } = useT();
  const k = pop(frame, fps, atSec, 14);
  if (k <= 0) return null;
  const R = 108;
  const encendidos = Math.round(interpolate(t, [atSec + 0.2, completo], [0, 21], CLAMP));
  const fin = interpolate(t, [completo, completo + 0.3], [0, 1], CLAMP);
  return (
    <div style={{ position: "absolute", width: 280, ...style, opacity: Math.min(1, k * 1.4) }}>
      <div
        style={{
          background: "rgba(245,240,236,0.95)",
          borderRadius: 34,
          padding: "16px 10px 14px",
          boxShadow: SOMBRA10,
          border: `3px solid ${COLORS.durazno}`,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          transform: `scale(${0.8 + 0.2 * k})`,
        }}
      >
        <svg width={260} height={260} viewBox="-130 -130 260 260">
          {[...Array(21)].map((_, i) => {
            const a = -Math.PI / 2 + (i / 21) * Math.PI * 2;
            const on = i < encendidos;
            return (
              <circle
                key={i}
                cx={Math.cos(a) * R}
                cy={Math.sin(a) * R}
                r={on ? 11 + 3 * fin : 9}
                fill={on ? COLORS.salvia : "rgba(69,89,90,.18)"}
              />
            );
          })}
          <text y={-6} textAnchor="middle" fontFamily="'Glacial Indifference'" fontWeight={700} fontSize={66} fill={COLORS.petroleo}>
            {encendidos}
          </text>
          <text y={34} textAnchor="middle" fontFamily="'Glacial Indifference'" fontWeight={700} fontSize={22} letterSpacing="3" fill={COLORS.salvia}>
            DE 21 DÍAS
          </text>
        </svg>
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 26,
            color: COLORS.petroleo,
            opacity: fin,
            transform: `translateY(${(1 - fin) * 10}px)`,
          }}
        >
          ¡Ya es una rutina!
        </div>
      </div>
    </div>
  );
};

// ---------- Nota tipo etiqueta (Durazno con borde blanco, algo girada) ----------
export const Etiqueta: React.FC<{
  at: number;
  texto: string;
  icono?: "si" | "no" | "ojo" | "corazon";
  giro?: number;
  ancho?: number;
  style?: React.CSSProperties;
}> = ({ at: atSec, texto, icono = "si", giro = -2, ancho = 280, style }) => {
  const { frame, fps } = useT();
  const k = golpe(frame, fps, atSec);
  if (k <= 0) return null;
  const ico =
    icono === "si" ? (
      <path d="M16 29 L25 38 L41 20" stroke={COLORS.marfil} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    ) : icono === "no" ? (
      <path d="M19 19 L37 37 M37 19 L19 37" stroke={COLORS.durazno} strokeWidth={6} fill="none" strokeLinecap="round" />
    ) : icono === "ojo" ? (
      <>
        <path d="M10 28 Q28 12 46 28 Q28 44 10 28 Z" stroke={COLORS.marfil} strokeWidth={4} fill="none" />
        <circle cx={28} cy={28} r={6} fill={COLORS.marfil} />
      </>
    ) : (
      <path d="M28 42 C14 32 12 22 18 18 C23 15 27 18 28 21 C29 18 33 15 38 18 C44 22 42 32 28 42 Z" fill={COLORS.marfil} />
    );
  return (
    <div
      style={{
        position: "absolute",
        width: ancho,
        ...style,
        opacity: Math.min(1, k * 2),
        transform: `${style?.transform ?? ""} rotate(${giro - (1 - k) * 8}deg) scale(${1.3 - 0.3 * k})`,
        transformOrigin: style?.transformOrigin ?? "0 0",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          background: COLORS.durazno,
          border: `6px solid ${COLORS.marfil}`,
          borderRadius: 24,
          padding: "10px 16px 10px 10px",
          boxShadow: SOMBRA10,
        }}
      >
        <svg width={44} height={44} viewBox="0 0 56 56" style={{ flexShrink: 0 }}>
          <circle cx={28} cy={28} r={26} fill={icono === "no" ? COLORS.petroleo : COLORS.salvia} />
          {ico}
        </svg>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 27, lineHeight: 1.12, color: COLORS.petroleo }}>{texto}</div>
      </div>
    </div>
  );
};

// ---------- Lista del registro final: medidas y fotos ----------
export const Registro: React.FC<{ at: number; filas: { texto: string; at: number }[]; style: React.CSSProperties }> = ({
  at: atSec,
  filas,
  style,
}) => {
  const { t, frame, fps } = useT();
  const k = pop(frame, fps, atSec, 14);
  if (k <= 0) return null;
  return (
    <div style={{ position: "absolute", width: 280, ...style, opacity: Math.min(1, k * 1.4) }}>
      <div
        style={{
          background: "rgba(245,240,236,0.95)",
          border: `3px solid ${COLORS.durazno}`,
          borderRadius: 28,
          padding: "16px 18px 12px",
          boxShadow: SOMBRA10,
          transform: `translateY(${(1 - k) * 24}px)`,
        }}
      >
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 21, letterSpacing: "0.2em", color: COLORS.salvia, marginBottom: 8 }}>
          REGISTRO FINAL
        </div>
        {filas.map((f) => {
          const d = interpolate(t, [f.at, f.at + 0.3], [0, 1], CLAMP);
          return (
            <div key={f.texto} style={{ display: "flex", alignItems: "center", gap: 12, padding: "6px 0" }}>
              <svg width={38} height={38} viewBox="0 0 38 38">
                <rect x={3} y={3} width={32} height={32} rx={9} fill={d > 0.1 ? COLORS.salvia : "none"} stroke={COLORS.salvia} strokeWidth={4} />
                <path
                  d="M10 19 L16 25 L28 12"
                  stroke={COLORS.marfil}
                  strokeWidth={4.5}
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  pathLength={1}
                  strokeDasharray={1}
                  strokeDashoffset={1 - d}
                />
              </svg>
              <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 30, color: COLORS.petroleo }}>{f.texto}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ---------- Inserción de cámara de móvil: las 4 fotos (fragmentos cortos con destello, §10.16) ----------
export type Foto = { src: string; at: number; pose: string };
export const CamaraMovil: React.FC<{ fotos: Foto[]; hasta: number }> = ({ fotos, hasta }) => {
  const { t, frame, fps } = useT();
  if (t < fotos[0].at || t >= hasta) return null;
  const i = fotos.reduce((acc, f, k) => (t >= f.at ? k : acc), 0);
  const f = fotos[i];
  const entra = pop(frame, fps, fotos[0].at, 16);
  const sale = interpolate(t, [hasta - 0.2, hasta], [0, 1], CLAMP);
  const destello = interpolate(frame - Math.round(f.at * fps), [0, 7], [0.9, 0], CLAMP);
  const W = 690;
  const H = 1230;
  const top = 250;
  return (
    <div style={{ position: "absolute", inset: 0, opacity: 1 - sale }}>
      <div style={{ position: "absolute", inset: 0, background: `radial-gradient(circle at 50% 40%, ${COLORS.durazno} 0%, ${COLORS.marfil} 60%)` }} />
      {/* Pose actual */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 120, display: "flex", justifyContent: "center" }}>
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 40,
            letterSpacing: "0.2em",
            color: COLORS.marfil,
            background: COLORS.petroleo,
            borderRadius: 40,
            padding: "12px 34px 10px",
            boxShadow: SOMBRA10,
          }}
        >
          {f.pose.toUpperCase()} · {i + 1}/{fotos.length}
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: (1080 - W) / 2,
          top,
          width: W,
          height: H,
          borderRadius: 80,
          background: COLORS.petroleo,
          padding: 20,
          boxSizing: "border-box",
          boxShadow: "0 40px 80px rgba(69,89,90,.4)",
          transform: `translateY(${(1 - entra) * 200}px) scale(${0.9 + 0.1 * entra})`,
        }}
      >
        <div style={{ position: "relative", width: "100%", height: "100%", borderRadius: 62, overflow: "hidden", background: "#111" }}>
          <Img src={staticFile(f.src)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
          {/* Cuadrícula de la cámara */}
          <svg width={W - 40} height={H - 40} style={{ position: "absolute", inset: 0 }}>
            {[1, 2].map((k) => (
              <React.Fragment key={k}>
                <line x1={((W - 40) * k) / 3} y1={0} x2={((W - 40) * k) / 3} y2={H - 40} stroke="rgba(255,255,255,.45)" strokeWidth={2} />
                <line x1={0} y1={((H - 40) * k) / 3} x2={W - 40} y2={((H - 40) * k) / 3} stroke="rgba(255,255,255,.45)" strokeWidth={2} />
              </React.Fragment>
            ))}
          </svg>
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: 0,
              padding: "26px 0 18px",
              textAlign: "center",
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 26,
              letterSpacing: "0.22em",
              color: COLORS.marfil,
              background: "linear-gradient(180deg, rgba(0,0,0,.45), rgba(0,0,0,0))",
            }}
          >
            IGUAL QUE EL DÍA 1
          </div>
          {/* Disparador y miniaturas de las fotos ya hechas */}
          <div style={{ position: "absolute", left: 0, right: 0, bottom: 34, display: "flex", justifyContent: "center", alignItems: "center", gap: 18 }}>
            {fotos.slice(0, i).map((g) => (
              <Img key={g.src} src={staticFile(g.src)} style={{ width: 58, height: 80, objectFit: "cover", borderRadius: 10, border: `3px solid ${COLORS.marfil}` }} />
            ))}
            <div style={{ width: 96, height: 96, borderRadius: 48, border: `7px solid ${COLORS.marfil}`, boxSizing: "border-box", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ width: 70, height: 70, borderRadius: 35, background: COLORS.marfil, transform: `scale(${1 - 0.15 * destello})` }} />
            </div>
          </div>
          <div style={{ position: "absolute", inset: 0, background: "#FFFFFF", opacity: destello }} />
        </div>
      </div>
    </div>
  );
};

// ---------- Panel lateral: la toma se desliza y entra un panel Marfil con el contenido ----------
export const PANEL_ANCHO = 380;
export const Panel: React.FC<{
  lado: "izq" | "der";
  p: number;
  kicker: string;
  titulo: string;
  at: number;
  children: React.ReactNode;
}> = ({ lado, p, kicker, titulo, at: atSec, children }) => {
  if (p <= 0.001) return null;
  const x = lado === "der" ? 1080 - PANEL_ANCHO * p : -PANEL_ANCHO * (1 - p);
  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: x,
        width: PANEL_ANCHO,
        height: 1920,
        background: `linear-gradient(180deg, ${COLORS.marfil} 0%, #F1E8DF 100%)`,
        boxShadow: lado === "der" ? "-20px 0 50px rgba(69,89,90,.25)" : "20px 0 50px rgba(69,89,90,.25)",
      }}
    >
      <div style={{ position: "absolute", top: 0, bottom: 0, [lado === "der" ? "left" : "right"]: 0, width: 10, background: COLORS.durazno }} />
      <div style={{ position: "absolute", left: 30, right: 30, top: 150, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <Pegatina
          at={atSec}
          kicker={kicker}
          kickerSize={Math.min(24, 300 / (0.72 * kicker.length))}
          texto={titulo}
          size={Math.min(84, 300 / (0.62 * titulo.length + 0.6))}
          giro={lado === "der" ? -3 : 3}
        />
      </div>
      <div style={{ position: "absolute", left: 22, right: 22, top: 400, bottom: 300 }}>{children}</div>
    </div>
  );
};

// ---------- Ficha de medidas (Día 1 · Día 21) que se va rellenando ----------
export const Ficha: React.FC<{
  at: number;
  dia1: number;
  dia21: number;
  filas: { texto: string; at: number }[];
  style?: React.CSSProperties;
}> = ({ at: atSec, dia1, dia21, filas, style }) => {
  const { t, frame, fps } = useT();
  const k = pop(frame, fps, atSec, 14);
  if (k <= 0) return null;
  const col = (on: number) => ({
    width: 84,
    textAlign: "center" as const,
    fontFamily: FONTS.body,
    fontWeight: 700,
    fontSize: 20,
    letterSpacing: "0.12em",
    color: on > 0.5 ? COLORS.marfil : COLORS.petroleo,
    background: on > 0.5 ? COLORS.salvia : "rgba(69,89,90,.1)",
    borderRadius: 10,
    padding: "6px 0 4px",
  });
  const d1 = interpolate(t, [dia1, dia1 + 0.2], [0, 1], CLAMP);
  const d21 = interpolate(t, [dia21, dia21 + 0.2], [0, 1], CLAMP);
  return (
    <div style={{ position: "relative", ...style, opacity: Math.min(1, k * 1.4), transform: `translateY(${(1 - k) * 30}px)` }}>
      <div style={{ background: "#FFFFFF", borderRadius: 26, padding: "16px 16px 10px", boxShadow: SOMBRA10, border: `3px solid ${COLORS.durazno}` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
          <div style={{ flex: 1, fontFamily: FONTS.body, fontWeight: 700, fontSize: 20, letterSpacing: "0.18em", color: COLORS.salvia }}>MEDIDAS</div>
          <div style={col(d1)}>DÍA 1</div>
          <div style={col(d21)}>DÍA 21</div>
        </div>
        {filas.map((f) => {
          const on = interpolate(t, [f.at, f.at + 0.25], [0, 1], CLAMP);
          return (
            <div key={f.texto} style={{ display: "flex", alignItems: "center", gap: 8, padding: "9px 0", borderTop: "2px solid rgba(69,89,90,.1)" }}>
              <div style={{ flex: 1, fontFamily: FONTS.body, fontWeight: 700, fontSize: 25, color: on > 0.5 ? COLORS.petroleo : "rgba(69,89,90,.5)" }}>{f.texto}</div>
              {[d1, d21].map((d, i) => (
                <svg key={i} width={84} height={30} viewBox="0 0 84 30">
                  <line x1={8} y1={24} x2={76} y2={24} stroke="rgba(69,89,90,.3)" strokeWidth={3} />
                  {/* Trazo a lápiz: se escribe al encenderse la fila (cada una lo escribe en su ficha) */}
                  <path
                    d="M10 20 C 22 6, 30 26, 42 14 S 62 10, 74 18"
                    stroke={i === 0 ? COLORS.salvia : COLORS.petroleo}
                    strokeWidth={4}
                    fill="none"
                    strokeLinecap="round"
                    pathLength={1}
                    strokeDasharray={1}
                    strokeDashoffset={1 - Math.min(on, d)}
                  />
                </svg>
              ))}
            </div>
          );
        })}
        <div style={{ fontFamily: FONTS.body, fontSize: 19, color: COLORS.salvia, textAlign: "right", marginTop: 4 }}>cm</div>
      </div>
    </div>
  );
};

// ---------- Día 1 / Día 21 lado a lado, sin filtros ----------
const Silueta: React.FC<{ color: string }> = ({ color }) => (
  <svg width={110} height={210} viewBox="0 0 110 210">
    <circle cx={55} cy={30} r={22} fill={color} />
    <path d="M22 66 Q55 54 88 66 L94 130 L80 202 L62 202 L55 140 L48 202 L30 202 L16 130 Z" fill={color} />
  </svg>
);
export const Comparar: React.FC<{ at: number; filtros: number; style?: React.CSSProperties }> = ({ at: atSec, filtros, style }) => {
  const { t, frame, fps } = useT();
  const k1 = pop(frame, fps, atSec, 14);
  const k2 = pop(frame, fps, atSec + 0.2, 14);
  const kf = golpe(frame, fps, filtros);
  if (k1 <= 0) return null;
  const marco = (k: number, dia: string, desde: -1 | 1, color: string) => (
    <div
      style={{
        width: 158,
        height: 268,
        background: "#FFFFFF",
        borderRadius: 18,
        padding: 10,
        boxSizing: "border-box",
        boxShadow: SOMBRA10,
        opacity: Math.min(1, k * 1.4),
        transform: `translateX(${(1 - k) * desde * 80}px) rotate(${desde * 2}deg)`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <div style={{ width: 138, height: 206, borderRadius: 10, background: "rgba(109,139,116,.12)", display: "flex", alignItems: "flex-end", justifyContent: "center" }}>
        <Silueta color={color} />
      </div>
      <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 24, letterSpacing: "0.12em", color: COLORS.petroleo, marginTop: 8 }}>{dia}</div>
    </div>
  );
  const sweep = interpolate(t, [atSec + 0.5, atSec + 1.2], [0, 1], CLAMP);
  return (
    <div style={{ position: "relative", ...style }}>
      <div style={{ display: "flex", justifyContent: "space-between", position: "relative" }}>
        {marco(k1, "DÍA 1", -1, "rgba(69,89,90,.55)")}
        {marco(k2, "DÍA 21", 1, COLORS.salvia)}
        {/* Flecha de comparación */}
        <svg width={60} height={40} style={{ position: "absolute", left: "50%", top: 110, marginLeft: -30, opacity: sweep }}>
          <path d="M6 20 H50 M38 8 L52 20 L38 32" stroke={COLORS.durazno} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
      {kf > 0 ? (
        <div style={{ display: "flex", gap: 10, justifyContent: "center", marginTop: 16 }}>
          {["SIN FILTROS", "SIN RETOQUES"].map((txt, i) => (
            <div
              key={txt}
              style={{
                fontFamily: FONTS.body,
                fontWeight: 700,
                fontSize: 19,
                letterSpacing: "0.12em",
                color: COLORS.marfil,
                background: COLORS.petroleo,
                borderRadius: 20,
                padding: "8px 12px 6px",
                transform: `rotate(${i ? 3 : -3}deg) scale(${1.4 - 0.4 * kf})`,
                opacity: Math.min(1, kf * 2),
              }}
            >
              {txt}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
};

// ---------- Montaje de la rutina (b-roll a pantalla completa) ----------
export const Montaje: React.FC<{
  desde: number;
  fragmentos: { zona: string; desde: number; frames: number }[];
  etiqueta: string;
}> = ({ desde, fragmentos, etiqueta }) => {
  const { t, frame, fps } = useT();
  const total = fragmentos.reduce((a, f) => a + f.frames, 0);
  const hasta = desde + total / fps;
  if (t < desde || t >= hasta) return null;
  const local = frame - Math.round(desde * fps);
  const i = fragmentos.reduce((acc, f, k) => (local >= f.desde ? k : acc), 0);
  const f = fragmentos[i];
  // Barrido entre fragmentos
  const dCorte = local - f.desde;
  const dSig = i + 1 < fragmentos.length ? fragmentos[i + 1].desde - local : 99;
  const borr = Math.max(interpolate(dCorte, [0, 4], [1, 0], CLAMP) * (i > 0 ? 1 : 0), interpolate(dSig, [0, 4], [1, 0], CLAMP));
  const dir = dSig < 4 ? -1 : 1;
  const kl = pop(frame, fps, desde + 0.1, 14);
  return (
    <div style={{ position: "absolute", inset: 0, background: "#000" }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translateX(${dir * 120 * borr * borr}px) scale(${1 + 0.15 * borr})`,
          filter: borr > 0.05 ? `blur(${10 * borr}px)` : undefined,
        }}
      >
        <Sequence from={Math.round(desde * fps)} durationInFrames={total} layout="none">
          <Video src={staticFile("dia10/rutina.webm")} muted style={{ width: "100%", height: "100%" }} />
        </Sequence>
      </div>
      <div style={{ position: "absolute", inset: 0, background: "#FFFFFF", opacity: interpolate(local, [0, 6], [0.8, 0], CLAMP) }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 1300, display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 30,
            letterSpacing: "0.2em",
            color: COLORS.durazno,
            background: COLORS.petroleo,
            borderRadius: 14,
            padding: "10px 22px 8px",
            boxShadow: SOMBRA10,
            opacity: Math.min(1, kl * 1.4),
            transform: `rotate(-2deg) scale(${0.7 + 0.3 * kl})`,
          }}
        >
          {etiqueta}
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          {fragmentos.map((g, k) => (
            <div
              key={g.zona}
              style={{
                fontFamily: FONTS.body,
                fontWeight: 700,
                fontSize: 26,
                letterSpacing: "0.1em",
                color: k === i ? COLORS.petroleo : COLORS.marfil,
                background: k === i ? COLORS.durazno : "rgba(69,89,90,.55)",
                borderRadius: 30,
                padding: "8px 16px 6px",
                transform: `scale(${k === i ? 1.08 : 1})`,
              }}
            >
              {g.zona.toUpperCase()}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ---------- Mensajes de chat que suben ("cuéntanos vía WhatsApp") ----------
export const Mensaje: React.FC<{
  at: number;
  texto?: string;
  propio?: boolean;
  escribiendo?: boolean;
  style?: React.CSSProperties;
}> = ({ at: atSec, texto, propio = false, escribiendo = false, style }) => {
  const { t, frame, fps } = useT();
  const k = pop(frame, fps, atSec, 13);
  if (k <= 0) return null;
  return (
    <div style={{ position: "absolute", width: 280, ...style, opacity: Math.min(1, k * 1.5) }}>
      <div style={{ display: "flex", justifyContent: propio ? "flex-end" : "flex-start", transform: `translateY(${(1 - k) * 40}px) scale(${0.85 + 0.15 * k})` }}>
        <div
          style={{
            maxWidth: 270,
            background: propio ? COLORS.salvia : "#FFFFFF",
            color: propio ? COLORS.marfil : COLORS.petroleo,
            borderRadius: 26,
            [propio ? "borderBottomRightRadius" : "borderBottomLeftRadius"]: 6,
            padding: escribiendo ? "16px 22px" : "14px 18px 12px",
            boxShadow: SOMBRA10,
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 26,
            lineHeight: 1.18,
          }}
        >
          {escribiendo ? (
            <div style={{ display: "flex", gap: 8 }}>
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  style={{
                    width: 14,
                    height: 14,
                    borderRadius: 7,
                    background: COLORS.salvia,
                    transform: `translateY(${-6 * Math.max(0, Math.sin(t * 9 - i * 0.9))}px)`,
                  }}
                />
              ))}
            </div>
          ) : (
            texto
          )}
        </div>
      </div>
    </div>
  );
};

/** Velo dorado suave (celebración) y destellos. */
export const Brillo: React.FC<{ en: number[] }> = ({ en }) => {
  const { t } = useT();
  const o = en.reduce((acc, c) => Math.max(acc, interpolate(t, [c - 0.05, c + 0.15, c + 1.1], [0, 0.45, 0], CLAMP)), 0);
  if (o <= 0) return null;
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        opacity: o,
        background: "radial-gradient(circle at 50% 30%, rgba(250,237,205,.95) 0%, rgba(243,207,160,.5) 35%, rgba(243,207,160,0) 70%)",
      }}
    />
  );
};
