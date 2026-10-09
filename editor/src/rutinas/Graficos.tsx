import React from "react";
import { interpolate } from "remotion";
import { COLORS, FONTS } from "../brand";
import { colocar, Lugar, useCaras, zonaCara } from "./Caras";
import { CLAMP, pop, useT } from "./util";

// Gráficos de las rutinas con voz en off (días 4 y 5). Todos se colocan con la cara de la toma de apoyo en cuenta.
export const SOMBRA = "0 4px 24px rgba(69,89,90,.6), 0 2px 6px rgba(69,89,90,.45)";
export const CARD = "rgba(69,89,90,0.9)";

type Kind = "up" | "scale" | "left" | "right";
export const Pop: React.FC<{ at: number; kind?: Kind; children: React.ReactNode; style?: React.CSSProperties }> = ({ at: atSec, kind = "up", children, style }) => {
  const { frame, fps } = useT();
  const p = pop(frame, fps, atSec);
  const tr = {
    up: `translateY(${(1 - p) * 40}px)`,
    scale: `scale(${0.6 + 0.4 * p})`,
    left: `translateX(${(1 - p) * -160}px)`,
    right: `translateX(${(1 - p) * 160}px)`,
  }[kind];
  return <div style={{ opacity: Math.min(1, p * 1.4), transform: tr, ...style }}>{children}</div>;
};

export const kicker: React.CSSProperties = { fontFamily: FONTS.body, fontWeight: 700, fontSize: 38, letterSpacing: "0.2em", color: COLORS.marfil, textShadow: SOMBRA, textAlign: "center" };
export const display = (size: number, color: string = COLORS.marfil): React.CSSProperties => ({ fontFamily: FONTS.display, fontSize: size, lineHeight: 1.02, color, textShadow: SOMBRA, textAlign: "center" });

/** Título grande: arriba, pegado por encima de la cabeza; si la cabeza está demasiado alta, baja a una tarjeta inferior. */
export const Titulo: React.FC<{ desde: number; hasta: number; kicker?: string; kickerAt?: number; texto: string; textoAt?: number; color?: string; max?: number }> = ({ desde, hasta, kicker: k, kickerAt, texto, textoAt, color = COLORS.durazno, max = 118 }) => {
  const caras = useCaras();
  const zona = zonaCara(caras, desde, hasta);
  const kh = k ? 50 : 0;
  const disponible = zona.y0 - 70 - kh;
  // Tamaño limitado por el alto libre sobre la cabeza y por el ancho (una sola línea, ~0,5 em por letra en TAN Pearl)
  const size = Math.min(max, disponible / 1.15, 1000 / (0.5 * texto.length));
  if (size >= 64) {
    // Arriba: la base del bloque queda en el borde superior de la zona prohibida (cara + pelo + 100 px)
    return (
      <div style={{ position: "absolute", left: 40, right: 40, top: 70, height: zona.y0 - 70, display: "flex", flexDirection: "column", justifyContent: "flex-end", alignItems: "center" }}>
        {k ? (
          <Pop at={kickerAt ?? desde}>
            <div style={kicker}>{k}</div>
          </Pop>
        ) : null}
        <Pop at={textoAt ?? desde} kind="scale">
          <div style={{ ...display(size, color), whiteSpace: "nowrap" }}>{texto}</div>
        </Pop>
      </div>
    );
  }
  // Abajo, en tarjeta (la cara nunca está tan abajo)
  const lugar = colocar(zona, 960, 230, ["abajo"]);
  if (!lugar) return null;
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: lugar.top + 40, display: "flex", justifyContent: "center" }}>
      <Pop at={textoAt ?? desde} kind="up">
        <div style={{ background: CARD, borderRadius: 32, padding: "18px 40px 24px", boxShadow: "0 16px 40px rgba(69,89,90,.35)", textAlign: "center" }}>
          {k ? <div style={{ ...kicker, fontSize: 30, textShadow: "none" }}>{k}</div> : null}
          <div style={{ ...display(Math.min(84, 880 / (0.5 * texto.length)), color), textShadow: "none", whiteSpace: "nowrap" }}>{texto}</div>
        </div>
      </Pop>
    </div>
  );
};

type Elemento = { w: number; h: number; orden?: Lugar[]; render: (pos: React.CSSProperties) => React.ReactNode };
/** Coloca varios elementos a los lados de la cara sin que se pisen: se apilan en la columna libre. */
export const Laterales: React.FC<{ desde: number; hasta: number; elementos: Elemento[] }> = ({ desde, hasta, elementos }) => {
  const caras = useCaras();
  const zona = zonaCara(caras, desde, hasta);
  const ocupado: Record<string, number> = { izq: 0, der: 0 };
  return (
    <>
      {elementos.map((e, i) => {
        for (const lado of e.orden ?? (["izq", "der"] as Lugar[])) {
          const pos = colocar(zona, e.w, e.h, [lado]);
          if (!pos) continue;
          const top = Math.max(pos.top, ocupado[lado] ? ocupado[lado] + 30 : 0);
          if (top + e.h > 1200) continue;
          ocupado[lado] = top + e.h;
          return <React.Fragment key={i}>{e.render({ left: pos.left, top })}</React.Fragment>;
        }
        return null;
      })}
    </>
  );
};

/** Tarjeta de tiempo: "2 min" con un anillo que se completa mientras dura el tramo de esa zona. */
export const Tiempo: React.FC<{ desde: number; hasta: number; minutos: number; zona: string; recordatorio?: boolean; style: React.CSSProperties }> = ({ desde, hasta, minutos, zona, recordatorio = true, style }) => {
  const { t } = useT();
  const p = interpolate(t, [desde + 0.2, hasta], [0, 1], CLAMP);
  const R = 74;
  const C = 2 * Math.PI * R;
  return (
    <div style={{ position: "absolute", width: 300, ...style }}>
      <Pop at={desde} kind="scale">
        <div style={{ background: CARD, borderRadius: 32, padding: "22px 18px 22px", boxShadow: "0 16px 40px rgba(69,89,90,.35)", display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
          <div style={{ position: "relative", width: 180, height: 180 }}>
            <svg width={180} height={180} style={{ position: "absolute", transform: "rotate(-90deg)" }}>
              <circle cx={90} cy={90} r={R} stroke="rgba(245,240,236,.25)" strokeWidth={14} fill="none" />
              <circle cx={90} cy={90} r={R} stroke={COLORS.durazno} strokeWidth={14} fill="none" strokeLinecap="round" strokeDasharray={C} strokeDashoffset={C * (1 - p)} />
            </svg>
            <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
              <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 84, lineHeight: 1, color: COLORS.marfil }}>{minutos}</div>
              <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 24, letterSpacing: "0.2em", color: COLORS.durazno }}>MIN</div>
            </div>
          </div>
          <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 32, color: COLORS.marfil, textAlign: "center", lineHeight: 1.1 }}>{zona}</div>
          {recordatorio ? (
            <div style={{ fontFamily: FONTS.body, fontSize: 21, color: COLORS.durazno, textAlign: "center", lineHeight: 1.2, opacity: interpolate(t, [desde + 1.2, desde + 1.6], [0, 1], CLAMP) }}>
              Continúa este movimiento hasta completar el tiempo indicado
            </div>
          ) : null}
        </div>
      </Pop>
    </div>
  );
};

/** Etiqueta corta (consejo o aviso) con icono ✓ o ✕ que se dibuja. */
export const Aviso: React.FC<{ at: number; texto: string; tipo?: "si" | "no"; ancho?: number; style: React.CSSProperties }> = ({ at: atSec, texto, tipo = "si", ancho = 300, style }) => {
  const { t } = useT();
  const d = interpolate(t, [atSec + 0.1, atSec + 0.4], [0, 1], CLAMP);
  return (
    <div style={{ position: "absolute", width: ancho, ...style }}>
      <Pop at={atSec} kind="up">
        <div style={{ background: tipo === "si" ? COLORS.durazno : CARD, color: tipo === "si" ? COLORS.petroleo : COLORS.marfil, borderRadius: 26, padding: "14px 18px 16px", display: "flex", alignItems: "center", gap: 12, boxShadow: "0 10px 30px rgba(69,89,90,.35)" }}>
          <svg width={44} height={44} viewBox="0 0 56 56" style={{ flexShrink: 0 }}>
            <circle cx={28} cy={28} r={26} fill={tipo === "si" ? COLORS.salvia : COLORS.petroleo} />
            {tipo === "si" ? (
              <path d="M16 29 L25 38 L41 20" stroke={COLORS.marfil} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={40} strokeDashoffset={40 * (1 - d)} />
            ) : (
              <path d="M19 19 L37 37 M37 19 L19 37" stroke={COLORS.durazno} strokeWidth={6} fill="none" strokeLinecap="round" strokeDasharray={52} strokeDashoffset={52 * (1 - d)} />
            )}
          </svg>
          <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 28, lineHeight: 1.15 }}>{texto}</div>
        </div>
      </Pop>
    </div>
  );
};

/** Lista de pasos de la rutina con su tiempo; el actual se enciende (resumen al final). */
export const Resumen: React.FC<{ at: number; filas: { texto: string; min: number }[]; style: React.CSSProperties }> = ({ at: atSec, filas, style }) => {
  const { t } = useT();
  const total = filas.reduce((a, f) => a + f.min, 0);
  const cuenta = Math.round(interpolate(t, [atSec + 0.3, atSec + 1.3], [0, total], CLAMP));
  return (
    <div style={{ position: "absolute", width: 320, ...style }}>
      <Pop at={atSec} kind="up">
        <div style={{ background: CARD, borderRadius: 30, padding: "20px 22px", boxShadow: "0 16px 40px rgba(69,89,90,.35)" }}>
          <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 64, color: COLORS.durazno, lineHeight: 1 }}>
            {cuenta} <span style={{ fontSize: 26, letterSpacing: "0.18em" }}>MIN</span>
          </div>
          {filas.map((f, i) => (
            <div key={f.texto} style={{ display: "flex", justifyContent: "space-between", fontFamily: FONTS.body, fontSize: 24, color: COLORS.marfil, padding: "5px 0", opacity: interpolate(t, [atSec + 0.3 + i * 0.12, atSec + 0.5 + i * 0.12], [0, 1], CLAMP) }}>
              <span>{f.texto}</span>
              <span style={{ fontWeight: 700, color: COLORS.durazno }}>{f.min}′</span>
            </div>
          ))}
        </div>
      </Pop>
    </div>
  );
};
