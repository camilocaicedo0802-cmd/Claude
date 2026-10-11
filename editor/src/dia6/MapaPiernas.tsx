import React from "react";
import { interpolate } from "remotion";
import { COLORS, FONTS } from "../brand";
import { CARD, Pop } from "../rutinas/Graficos";
import { CLAMP, useT } from "../rutinas/util";

// Día 6 · mapa del cuerpo (cintura a pies) en 2D: silueta ilustrada, de frente o de espalda, sobre tarjeta
// Verde petróleo. Sustituye al maniquí 3D (giraba y a ratos se veía raro). La zona que se trabaja se enciende en
// salvia y encima se dibuja el movimiento que dice la voz: trazos que suben (barridos) o un círculo que gira
// (círculos amplios). "Evita pasar sobre la rodilla o la ingle" → cruces en esos puntos. Para cambiar de vista la
// tarjeta se voltea (como una carta), sin rotaciones en 3D.

export type ZonaCuerpo = "ninguna" | "todo" | "musloD" | "musloI" | "gluteos";
export type Modo = "nada" | "barridos" | "circulos";
export type Paso = { t: number; zona: ZonaCuerpo; modo?: Modo };

// Silueta en un lienzo de 200×340. Pierna derecha de ella = izquierda de la imagen (vista de frente).
const PELVIS =
  "M 64 12 C 62 30 48 46 45 70 C 44 86 52 98 64 104 C 76 110 90 114 100 114 C 110 114 124 110 136 104 C 148 98 156 86 155 70 C 152 46 138 30 136 12 Z";
// Pierna de la izquierda de la imagen: contorno exterior hacia abajo y vuelta por el interior hasta la ingle
const PIERNA =
  "M 45 70 C 41 100 44 142 56 184 C 59 196 55 206 54 216 C 51 242 58 272 68 298 C 70 306 64 314 70 320 C 78 324 92 323 93 315 C 94 305 90 297 92 285 C 96 258 99 234 93 212 C 91 202 93 194 95 186 C 99 160 101 134 100 114 C 90 114 76 110 64 104 C 52 98 44 86 45 70 Z";
const ESPEJO = "translate(200 0) scale(-1 1)";
// Glúteos (vista de espalda): mitad de la imagen a cada lado del pliegue central
const GLUTEO =
  "M 100 56 C 84 54 56 60 49 82 C 44 100 56 120 80 122 C 90 123 98 120 100 116 Z";

const MUSLO_Y = [104, 184] as const; // de justo debajo de la ropa interior a encima de la rodilla
const CENTRO_MUSLO = { x: 74, y: 132 };
const RODILLA = { x: 75, y: 194 };
const INGLE = { x: 95, y: 110 };
const CENTRO_GLUTEO = { x: 76, y: 90 };

const vistaDe = (z: ZonaCuerpo, t: number) =>
  z === "gluteos" ? 1 : z === "todo" ? Math.floor(t / 1.8) % 2 : 0; // 0 = frente, 1 = espalda
const luces = (z: ZonaCuerpo) => ({
  musloD: z === "musloD" || z === "todo" ? 1 : 0,
  musloI: z === "musloI" || z === "todo" ? 1 : 0,
  gluteos: z === "gluteos" || z === "todo" ? 1 : 0,
});

const Cruz: React.FC<{ x: number; y: number; s: number }> = ({ x, y, s }) =>
  s <= 0.01 ? null : (
    <g transform={`translate(${x} ${y}) scale(${s})`}>
      <circle
        r={9}
        fill={COLORS.petroleo}
        stroke={COLORS.durazno}
        strokeWidth={1.5}
      />
      <path
        d="M -4 -4 L 4 4 M 4 -4 L -4 4"
        stroke={COLORS.durazno}
        strokeWidth={2.4}
        strokeLinecap="round"
      />
    </g>
  );

/** Trazos de luz que suben (barridos) entre y0 y y1 alrededor de x */
const Barridos: React.FC<{
  x: number;
  y0: number;
  y1: number;
  t: number;
  f: number;
  xs?: number[];
}> = ({ x, y0, y1, t, f, xs = [-11, 0, 11] }) => (
  <>
    {xs.map((dx, i) => {
      const k = (t * 0.8 + i * 0.33) % 1;
      const y = y0 + (y1 - y0) * k;
      return (
        <g key={i} opacity={f * Math.sin(k * Math.PI)}>
          <rect
            x={x + dx - 2.5}
            y={y - 9}
            width={5}
            height={18}
            rx={2.5}
            fill="#FFF6E6"
          />
          <path
            d={`M ${x + dx - 4} ${y - 7} L ${x + dx} ${y - 13} L ${x + dx + 4} ${y - 7}`}
            stroke="#FFF6E6"
            strokeWidth={2}
            fill="none"
            strokeLinecap="round"
          />
        </g>
      );
    })}
  </>
);
/** Círculo amplio: anillo discontinuo con un punto que lo recorre */
const Circulo: React.FC<{
  x: number;
  y: number;
  r?: number;
  t: number;
  f: number;
}> = ({ x, y, r = 14, t, f }) => {
  const a = -t * 4.2;
  return (
    <g opacity={f}>
      <circle
        cx={x}
        cy={y}
        r={r}
        fill="none"
        stroke="#FFF6E6"
        strokeWidth={2.5}
        strokeDasharray="5 4"
      />
      <circle
        cx={x + Math.cos(a) * r}
        cy={y + Math.sin(a) * r}
        r={4.2}
        fill={COLORS.durazno}
        stroke={COLORS.petroleo}
        strokeWidth={1.2}
      />
    </g>
  );
};

const Silueta: React.FC<{
  vista: number;
  luz: { musloD: number; musloI: number; gluteos: number };
  modo: Modo;
  activa: ZonaCuerpo;
  f: number;
  t: number;
  evita: number;
}> = ({ vista, luz, modo, activa, f, t, evita }) => {
  // De espalda, la pierna derecha de ella queda a la derecha de la imagen
  const ladoD = vista === 0 ? 0 : 1; // 0 = izquierda de la imagen
  const piernas = [0, 1].map((lado) => {
    const esD = lado === ladoD;
    const l = esD ? luz.musloD : luz.musloI;
    const zona: ZonaCuerpo = esD ? "musloD" : "musloI";
    return { lado, l, zona };
  });
  return (
    <>
      <defs>
        <linearGradient id="piel" x1="0" x2="1">
          <stop offset="0" stopColor="#E9DDD0" />
          <stop offset="0.45" stopColor="#F7F1EA" />
          <stop offset="1" stopColor="#E3D5C6" />
        </linearGradient>
        <clipPath id="musloRecorte">
          <rect
            x={0}
            y={MUSLO_Y[0]}
            width={200}
            height={MUSLO_Y[1] - MUSLO_Y[0]}
          />
        </clipPath>
        <filter id="brillo" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation={3.2} />
        </filter>
      </defs>
      {/* Sombra suave en el suelo */}
      <ellipse cx={100} cy={326} rx={52} ry={6} fill="rgba(0,0,0,.18)" />
      {piernas.map(({ lado, l }) => (
        <g key={lado} transform={lado ? ESPEJO : undefined}>
          <path
            d={PIERNA}
            fill="url(#piel)"
            stroke="rgba(69,89,90,.28)"
            strokeWidth={1.2}
          />
          {vista === 0 && l > 0 ? (
            <g clipPath="url(#musloRecorte)" opacity={l}>
              <path
                d={PIERNA}
                fill={COLORS.salvia}
                filter="url(#brillo)"
                opacity={0.55}
              />
              <path d={PIERNA} fill={COLORS.salvia} opacity={0.85} />
            </g>
          ) : null}
          {/* Rodilla y tobillo apenas marcados */}
          <path
            d="M 64 196 C 70 202 82 202 88 196"
            stroke="rgba(69,89,90,.22)"
            strokeWidth={1.4}
            fill="none"
          />
        </g>
      ))}
      <path
        d={PELVIS}
        fill="url(#piel)"
        stroke="rgba(69,89,90,.28)"
        strokeWidth={1.2}
      />
      {vista === 0 ? (
        // Ropa interior de frente (da escala y orienta la vista)
        <path
          d="M 52 62 C 74 70 126 70 148 62 C 146 80 126 104 100 112 C 74 104 54 80 52 62 Z"
          fill={COLORS.petroleo}
          opacity={0.9}
        />
      ) : (
        <>
          {[0, 1].map((lado) => (
            <g key={lado} transform={lado ? ESPEJO : undefined}>
              <path
                d={GLUTEO}
                fill="url(#piel)"
                stroke="rgba(69,89,90,.18)"
                strokeWidth={1}
              />
              {luz.gluteos > 0 ? (
                <g opacity={luz.gluteos}>
                  <path
                    d={GLUTEO}
                    fill={COLORS.salvia}
                    filter="url(#brillo)"
                    opacity={0.5}
                  />
                  <path d={GLUTEO} fill={COLORS.salvia} opacity={0.85} />
                </g>
              ) : null}
            </g>
          ))}
          <path
            d="M 64 52 C 80 60 120 60 136 52 L 134 62 C 118 68 82 68 66 62 Z"
            fill={COLORS.petroleo}
            opacity={0.9}
          />
        </>
      )}
      {/* Movimiento sobre la zona activa */}
      {piernas.map(({ lado, zona }) =>
        vista === 0 && activa === zona ? (
          <g key={`m${lado}`} transform={lado ? ESPEJO : undefined}>
            {modo === "barridos" ? (
              <Barridos x={CENTRO_MUSLO.x} y0={176} y1={92} t={t} f={f} />
            ) : null}
            {modo === "circulos" ? (
              <Circulo x={CENTRO_MUSLO.x} y={CENTRO_MUSLO.y} t={t} f={f} />
            ) : null}
            <Cruz x={RODILLA.x} y={RODILLA.y} s={evita} />
            <Cruz x={INGLE.x - 6} y={INGLE.y + 4} s={evita} />
          </g>
        ) : null,
      )}
      {vista === 1 && activa === "gluteos"
        ? [0, 1].map((lado) => (
            <g key={`g${lado}`} transform={lado ? ESPEJO : undefined}>
              {modo === "circulos" ? (
                <Circulo
                  x={CENTRO_GLUTEO.x}
                  y={CENTRO_GLUTEO.y}
                  r={12}
                  t={t + lado}
                  f={f}
                />
              ) : null}
              {modo === "barridos" ? (
                <Barridos
                  x={CENTRO_GLUTEO.x}
                  y0={118}
                  y1={70}
                  t={t + lado * 0.2}
                  f={f}
                  xs={[-8, 8]}
                />
              ) : null}
            </g>
          ))
        : null}
    </>
  );
};

export const MapaPiernas: React.FC<{
  desde: number;
  pasos: Paso[];
  evita?: [number, number];
  style: React.CSSProperties;
}> = ({ desde, pasos, evita, style }) => {
  const { t } = useT();
  if (t < desde - 0.05) return null;
  let i = 0;
  while (i + 1 < pasos.length && pasos[i + 1].t <= t) i++;
  const actual = pasos[i];
  const previo = pasos[Math.max(0, i - 1)];
  const k =
    i === 0 ? 1 : interpolate(t, [actual.t, actual.t + 0.5], [0, 1], CLAMP);
  const la = luces(actual.zona);
  const lp = luces(previo.zona);
  const luz = {
    musloD: lp.musloD + (la.musloD - lp.musloD) * k,
    musloI: lp.musloI + (la.musloI - lp.musloI) * k,
    gluteos: lp.gluteos + (la.gluteos - lp.gluteos) * k,
  };
  // Vista: si cambia, la tarjeta se voltea (0,4 s); en "todo" alterna frente/espalda
  const v1 = vistaDe(actual.zona, t);
  const cambio = (() => {
    if (actual.zona === "todo") {
      const fase = (t / 1.8) % 1;
      return fase < 0.12 ? fase / 0.12 : 1;
    }
    const v0 = vistaDe(previo.zona, actual.t);
    return v0 === v1
      ? 1
      : interpolate(t, [actual.t, actual.t + 0.4], [0, 1], CLAMP);
  })();
  const v0 = actual.zona === "todo" ? 1 - v1 : vistaDe(previo.zona, actual.t);
  const vista = cambio < 0.5 ? v0 : v1;
  const giro = Math.abs(Math.cos(cambio * Math.PI));
  const modo = actual.modo ?? "nada";
  const f = interpolate(t, [actual.t + 0.3, actual.t + 0.7], [0, 1], CLAMP);
  const sEvita = evita
    ? interpolate(t, [evita[0], evita[0] + 0.25], [0, 1], CLAMP) *
      interpolate(t, [evita[1], evita[1] + 0.25], [1, 0], CLAMP)
    : 0;
  return (
    <div style={{ position: "absolute", width: 240, ...style }}>
      <Pop at={desde} kind="scale">
        <div
          style={{
            background: CARD,
            borderRadius: 32,
            padding: "12px 15px 10px",
            boxShadow: "0 16px 40px rgba(69,89,90,.35)",
          }}
        >
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 17,
              letterSpacing: "0.22em",
              color: COLORS.durazno,
              textAlign: "center",
            }}
          >
            {vista === 0 ? "VISTA DE FRENTE" : "VISTA DE ESPALDA"}
          </div>
          <svg
            width={210}
            height={357}
            viewBox="0 0 200 340"
            style={{
              display: "block",
              transform: `scaleX(${Math.max(0.02, giro)})`,
            }}
          >
            <Silueta
              vista={vista}
              luz={luz}
              modo={modo}
              activa={actual.zona}
              f={f}
              t={t}
              evita={sEvita}
            />
          </svg>
        </div>
      </Pop>
    </div>
  );
};
