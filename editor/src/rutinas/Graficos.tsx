import React from "react";
import { interpolate } from "remotion";
import { COLORS, FONTS } from "../brand";
import { colocar, Lugar, useCaras, zonasEn } from "./Caras";
import { CLAMP, pop, useT } from "./util";

// Gráficos de las rutinas con voz en off (días 4 y 5). Todos se colocan con la cara de la toma de apoyo en cuenta.
export const SOMBRA =
  "0 4px 24px rgba(69,89,90,.6), 0 2px 6px rgba(69,89,90,.45)";
export const CARD = "rgba(69,89,90,0.9)";

type Kind = "up" | "scale" | "left" | "right";
export const Pop: React.FC<{
  at: number;
  kind?: Kind;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ at: atSec, kind = "up", children, style }) => {
  const { frame, fps } = useT();
  const p = pop(frame, fps, atSec);
  const tr = {
    up: `translateY(${(1 - p) * 40}px)`,
    scale: `scale(${0.6 + 0.4 * p})`,
    left: `translateX(${(1 - p) * -160}px)`,
    right: `translateX(${(1 - p) * 160}px)`,
  }[kind];
  return (
    <div style={{ opacity: Math.min(1, p * 1.4), transform: tr, ...style }}>
      {children}
    </div>
  );
};

export const kicker: React.CSSProperties = {
  fontFamily: FONTS.body,
  fontWeight: 700,
  fontSize: 38,
  letterSpacing: "0.2em",
  color: COLORS.marfil,
  textShadow: SOMBRA,
  textAlign: "center",
};
export const display = (
  size: number,
  color: string = COLORS.marfil,
): React.CSSProperties => ({
  fontFamily: FONTS.display,
  fontSize: size,
  lineHeight: 1.02,
  color,
  textShadow: SOMBRA,
  textAlign: "center",
});

/** Título grande: arriba, pegado por encima de la cabeza y a su tamaño; si no hay sitio sobre la cabeza, se desvanece. */
export const Titulo: React.FC<{
  desde: number;
  hasta: number;
  kicker?: string;
  kickerAt?: number;
  texto: string;
  textoAt?: number;
  color?: string;
  max?: number;
}> = ({
  desde,
  hasta,
  kicker: k,
  kickerAt,
  texto,
  textoAt,
  color = COLORS.durazno,
  max = 118,
}) => {
  const caras = useCaras();
  const { t } = useT();
  const { actual, previa, k: mezcla } = zonasEn(caras, t, desde, hasta);
  // Alto libre sobre la cabeza (base del bloque = borde superior de la zona prohibida), animado en los cortes
  const y0 = previa.y0 + (actual.y0 - previa.y0) * mezcla;
  const conKicker = k && y0 - 70 >= 50 + 64 * 1.15;
  const disponible = y0 - 70 - (conKicker ? 56 : 0);
  // Una sola línea: TAN Pearl ocupa ~0,7 em por letra (medido en los renders; 0,78 deja margen)
  const size = Math.min(max, disponible / 1.15, 1000 / (0.78 * texto.length));
  // Si la cabeza deja poco sitio arriba, el título se desvanece (la zona sigue nombrada en la tarjeta de tiempo):
  // nunca baja a tapar las piernas ni la toma.
  const visible = Math.min(1, Math.max(0, (size - 44) / 14));
  if (visible <= 0) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 40,
        right: 40,
        top: 70,
        height: y0 - 70,
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-end",
        alignItems: "center",
        opacity: visible,
      }}
    >
      {conKicker ? (
        <Pop at={kickerAt ?? desde}>
          <div style={{ ...kicker, marginBottom: 8 }}>{k}</div>
        </Pop>
      ) : null}
      <Pop at={textoAt ?? desde} kind="scale">
        <div style={{ ...display(size, color), whiteSpace: "nowrap" }}>
          {texto}
        </div>
      </Pop>
    </div>
  );
};

type Elemento = {
  w: number;
  h: number;
  orden?: Lugar[];
  render: (pos: React.CSSProperties) => React.ReactNode;
};
const ORDEN_DEF: Lugar[] = ["izq", "der", "izqBajo", "derBajo"];
const colocarTodos = (
  zona: Parameters<typeof colocar>[0],
  elementos: Elemento[],
) => {
  // Columna izquierda o derecha (junto a la cabeza o, si no cabe, por debajo de ella); se apilan sin pisarse
  const ocupado: Record<string, number> = {};
  return elementos.map((e) => {
    const orden = e.orden ?? ORDEN_DEF;
    const conBajo = [
      ...orden,
      ...orden.map((l) =>
        l === "izq" ? "izqBajo" : l === "der" ? "derBajo" : l,
      ),
    ].filter((l, i, arr) => arr.indexOf(l) === i) as Lugar[];
    for (const lado of conBajo) {
      const pos = colocar(zona, e.w, e.h, [lado]);
      if (!pos) continue;
      const col = lado.startsWith("izq") ? "izq" : "der";
      const top = Math.max(pos.top, ocupado[col] ? ocupado[col] + 24 : 0);
      if (top + e.h > 1250) continue;
      ocupado[col] = top + e.h;
      return { left: pos.left, top };
    }
    return null;
  });
};
/** Coloca varios elementos a los lados de la cara sin que se pisen; en cada corte de la toma se deslizan a su nuevo sitio. */
export const Laterales: React.FC<{
  desde: number;
  hasta: number;
  elementos: Elemento[];
}> = ({ desde, hasta, elementos }) => {
  const caras = useCaras();
  const { t } = useT();
  const { actual, previa, k } = zonasEn(caras, t, desde, hasta);
  const ahora = colocarTodos(actual, elementos);
  const antes = colocarTodos(previa, elementos);
  return (
    <>
      {elementos.map((e, i) => {
        const a = ahora[i];
        if (!a) return null;
        const b = antes[i] ?? a;
        return (
          <React.Fragment key={i}>
            {e.render({
              left: b.left + (a.left - b.left) * k,
              top: b.top + (a.top - b.top) * k,
            })}
          </React.Fragment>
        );
      })}
    </>
  );
};

/** Tarjeta de tiempo: "2 min" con un anillo que se completa mientras dura el tramo de esa zona. */
export const Tiempo: React.FC<{
  desde: number;
  hasta: number;
  minutos: number;
  zona: string;
  recordatorio?: boolean;
  etiquetaGrande?: boolean;
  style: React.CSSProperties;
}> = ({
  desde,
  hasta,
  minutos,
  zona,
  recordatorio = true,
  etiquetaGrande = false,
  style,
}) => {
  const { t } = useT();
  const p = interpolate(t, [desde + 0.2, hasta], [0, 1], CLAMP);
  const R = 62;
  const C = 2 * Math.PI * R;
  return (
    <div style={{ position: "absolute", width: 260, ...style }}>
      <Pop at={desde} kind="scale">
        <div
          style={{
            background: CARD,
            borderRadius: 32,
            padding: "18px 14px 18px",
            boxShadow: "0 16px 40px rgba(69,89,90,.35)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 8,
          }}
        >
          <div style={{ position: "relative", width: 150, height: 150 }}>
            <svg
              width={150}
              height={150}
              style={{ position: "absolute", transform: "rotate(-90deg)" }}
            >
              <circle
                cx={75}
                cy={75}
                r={R}
                stroke="rgba(245,240,236,.25)"
                strokeWidth={12}
                fill="none"
              />
              <circle
                cx={75}
                cy={75}
                r={R}
                stroke={COLORS.durazno}
                strokeWidth={12}
                fill="none"
                strokeLinecap="round"
                strokeDasharray={C}
                strokeDashoffset={C * (1 - p)}
              />
            </svg>
            <div
              style={{
                position: "absolute",
                inset: 0,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <div
                style={{
                  fontFamily: FONTS.body,
                  fontWeight: 700,
                  fontSize: 70,
                  lineHeight: 1,
                  color: COLORS.marfil,
                }}
              >
                {minutos}
              </div>
              <div
                style={{
                  fontFamily: FONTS.body,
                  fontWeight: 700,
                  fontSize: 24,
                  letterSpacing: "0.2em",
                  color: COLORS.durazno,
                }}
              >
                MIN
              </div>
            </div>
          </div>
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: etiquetaGrande ? 36 : 28,
              color: COLORS.marfil,
              textAlign: "center",
              lineHeight: 1.1,
            }}
          >
            {zona}
          </div>
          {recordatorio ? (
            <div
              style={{
                fontFamily: FONTS.body,
                fontSize: 19,
                color: COLORS.durazno,
                textAlign: "center",
                lineHeight: 1.2,
                opacity: interpolate(
                  t,
                  [desde + 1.2, desde + 1.6],
                  [0, 1],
                  CLAMP,
                ),
              }}
            >
              Continúa este movimiento hasta completar el tiempo indicado
            </div>
          ) : null}
        </div>
      </Pop>
    </div>
  );
};

/** Etiqueta corta (consejo o aviso) con icono ✓ o ✕ que se dibuja. */
export const Aviso: React.FC<{
  at: number;
  texto: string;
  tipo?: "si" | "no";
  ancho?: number;
  tamano?: number;
  style: React.CSSProperties;
}> = ({ at: atSec, texto, tipo = "si", ancho = 260, tamano = 25, style }) => {
  const { t } = useT();
  const d = interpolate(t, [atSec + 0.1, atSec + 0.4], [0, 1], CLAMP);
  return (
    <div style={{ position: "absolute", width: ancho, ...style }}>
      <Pop at={atSec} kind="up">
        <div
          style={{
            background: tipo === "si" ? COLORS.durazno : CARD,
            color: tipo === "si" ? COLORS.petroleo : COLORS.marfil,
            borderRadius: 26,
            padding: "14px 18px 16px",
            display: "flex",
            alignItems: "center",
            gap: 12,
            boxShadow: "0 10px 30px rgba(69,89,90,.35)",
          }}
        >
          <svg
            width={44}
            height={44}
            viewBox="0 0 56 56"
            style={{ flexShrink: 0 }}
          >
            <circle
              cx={28}
              cy={28}
              r={26}
              fill={tipo === "si" ? COLORS.salvia : COLORS.petroleo}
            />
            {tipo === "si" ? (
              <path
                d="M16 29 L25 38 L41 20"
                stroke={COLORS.marfil}
                strokeWidth={6}
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray={40}
                strokeDashoffset={40 * (1 - d)}
              />
            ) : (
              <path
                d="M19 19 L37 37 M37 19 L19 37"
                stroke={COLORS.durazno}
                strokeWidth={6}
                fill="none"
                strokeLinecap="round"
                strokeDasharray={52}
                strokeDashoffset={52 * (1 - d)}
              />
            )}
          </svg>
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: tamano,
              lineHeight: 1.15,
            }}
          >
            {texto}
          </div>
        </div>
      </Pop>
    </div>
  );
};

/** Lista de pasos de la rutina con su tiempo; el actual se enciende (resumen al final). */
export const Resumen: React.FC<{
  at: number;
  filas: { texto: string; min: number }[];
  style: React.CSSProperties;
}> = ({ at: atSec, filas, style }) => {
  const { t } = useT();
  const total = filas.reduce((a, f) => a + f.min, 0);
  const cuenta = Math.round(
    interpolate(t, [atSec + 0.3, atSec + 1.3], [0, total], CLAMP),
  );
  return (
    <div style={{ position: "absolute", width: 280, ...style }}>
      <Pop at={atSec} kind="up">
        <div
          style={{
            background: CARD,
            borderRadius: 30,
            padding: "18px 20px",
            boxShadow: "0 16px 40px rgba(69,89,90,.35)",
          }}
        >
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 64,
              color: COLORS.durazno,
              lineHeight: 1,
            }}
          >
            {cuenta}{" "}
            <span style={{ fontSize: 26, letterSpacing: "0.18em" }}>MIN</span>
          </div>
          {filas.map((f, i) => (
            <div
              key={f.texto}
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontFamily: FONTS.body,
                fontSize: 24,
                color: COLORS.marfil,
                padding: "5px 0",
                opacity: interpolate(
                  t,
                  [atSec + 0.3 + i * 0.12, atSec + 0.5 + i * 0.12],
                  [0, 1],
                  CLAMP,
                ),
              }}
            >
              <span>{f.texto}</span>
              <span style={{ fontWeight: 700, color: COLORS.durazno }}>
                {f.min}′
              </span>
            </div>
          ))}
        </div>
      </Pop>
    </div>
  );
};

/** Subtítulo inferior para frases largas (texto recurrente del guion y avisos), legible a tamaño grande.
 *  Muestra el elemento activo que empezó más tarde; base en y = 1560 (fuera de la interfaz de Reels) y nunca sobre la cara. */
export type ItemSubtitulo = {
  desde: number;
  hasta: number;
  texto: string;
  tipo?: "si" | "no";
};
export const Subtitulo: React.FC<{ items: ItemSubtitulo[] }> = ({ items }) => {
  const caras = useCaras();
  const { t, frame, fps } = useT();
  const activos = items.filter((i) => t >= i.desde && t < i.hasta);
  if (!activos.length) return null;
  const item = activos.reduce((a, b) => (b.desde > a.desde ? b : a));
  const { actual } = zonasEn(caras, t, item.desde, item.hasta);
  if (actual.y1 > 1330) return null; // la cara nunca baja tanto, pero si pasara, el subtítulo no se muestra
  const p = pop(frame, fps, item.desde, 16);
  const salida = interpolate(t, [item.hasta - 0.2, item.hasta], [1, 0], CLAMP);
  const d = interpolate(t, [item.desde + 0.1, item.desde + 0.4], [0, 1], CLAMP);
  return (
    <div
      style={{
        position: "absolute",
        left: 50,
        right: 50,
        bottom: 1920 - 1560,
        display: "flex",
        justifyContent: "center",
        opacity: Math.min(1, p * 1.4) * salida,
        transform: `translateY(${(1 - p) * 30}px)`,
      }}
    >
      <div
        style={{
          background: "rgba(69,89,90,0.92)",
          borderRadius: 30,
          padding: "18px 30px 22px",
          display: "flex",
          alignItems: "center",
          gap: 18,
          maxWidth: 980,
          boxShadow: "0 14px 36px rgba(69,89,90,.4)",
        }}
      >
        {item.tipo ? (
          <svg
            width={52}
            height={52}
            viewBox="0 0 56 56"
            style={{ flexShrink: 0 }}
          >
            <circle
              cx={28}
              cy={28}
              r={26}
              fill={item.tipo === "si" ? COLORS.salvia : COLORS.durazno}
            />
            {item.tipo === "si" ? (
              <path
                d="M16 29 L25 38 L41 20"
                stroke={COLORS.marfil}
                strokeWidth={6}
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray={40}
                strokeDashoffset={40 * (1 - d)}
              />
            ) : (
              <path
                d="M19 19 L37 37 M37 19 L19 37"
                stroke={COLORS.petroleo}
                strokeWidth={6}
                fill="none"
                strokeLinecap="round"
                strokeDasharray={52}
                strokeDashoffset={52 * (1 - d)}
              />
            )}
          </svg>
        ) : null}
        <div
          style={{
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 42,
            lineHeight: 1.18,
            color: COLORS.marfil,
            textAlign: item.tipo ? "left" : "center",
          }}
        >
          {item.texto}
        </div>
      </div>
    </div>
  );
};
