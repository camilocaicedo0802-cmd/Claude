import React from "react";
import { Img, interpolate, spring, staticFile } from "remotion";
import { COLORS, FONTS } from "../brand";
import { useCaras, zonasEn } from "../rutinas/Caras";
import { CARD, Pop, SOMBRA } from "../rutinas/Graficos";
import { CLAMP, useT } from "../rutinas/util";

// Gráficos 2D del día 8 "Evaluación del Día 10". Lenguaje nuevo: título que se revela con un subrayado de pincel,
// pasos de la evaluación que se van marcando, escala 1–5, polaroids, lupa sobre la piel, camino de 21 días,
// tarjeta No/Sí, confeti y transición en círculo (iris).

/** Título sobre la cabeza: el texto sube desde una línea invisible y un trazo Durazno lo subraya. */
export const TituloSubrayado: React.FC<{
  desde: number;
  hasta: number;
  kicker?: string;
  texto: string;
  textoAt?: number;
  max?: number;
}> = ({ desde, hasta, kicker, texto, textoAt, max = 116 }) => {
  const caras = useCaras();
  const { t, frame, fps } = useT();
  const { actual, previa, k } = zonasEn(caras, t, desde, hasta);
  const y0 = previa.y0 + (actual.y0 - previa.y0) * k;
  const conKicker = kicker && y0 - 70 >= 50 + 64 * 1.15;
  const disponible = y0 - 90 - (conKicker ? 54 : 0);
  const size = Math.min(max, disponible / 1.15, 1000 / (0.78 * texto.length));
  if (size < 44) return null;
  const t0 = textoAt ?? desde;
  const f = frame - Math.round(t0 * fps);
  const p =
    f < 0 ? 0 : spring({ frame: f, fps, config: { damping: 18, mass: 0.6 } });
  const trazo = interpolate(t, [t0 + 0.25, t0 + 0.75], [0, 1], CLAMP);
  const ancho = Math.min(1000, 0.7 * size * texto.length);
  return (
    <div
      style={{
        position: "absolute",
        left: 40,
        right: 40,
        top: 60,
        height: y0 - 80,
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-end",
        alignItems: "center",
      }}
    >
      {conKicker ? (
        <Pop at={desde} kind="up">
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 34,
              letterSpacing: "0.24em",
              color: COLORS.durazno,
              textShadow: SOMBRA,
              marginBottom: 6,
            }}
          >
            {kicker}
          </div>
        </Pop>
      ) : null}
      <div style={{ overflow: "hidden", paddingBottom: size * 0.28 }}>
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: size,
            lineHeight: 1.02,
            color: COLORS.marfil,
            textShadow: SOMBRA,
            whiteSpace: "nowrap",
            transform: `translateY(${(1 - p) * size * 1.2}px)`,
          }}
        >
          {texto.split(/(\d+)/).map((parte, i) =>
            /^\d+$/.test(parte) ? (
              <span
                key={i}
                style={{
                  fontFamily: FONTS.body,
                  fontWeight: 700,
                  color: COLORS.durazno,
                }}
              >
                {parte}
              </span>
            ) : (
              <React.Fragment key={i}>{parte}</React.Fragment>
            ),
          )}
        </div>
      </div>
      <svg
        width={ancho}
        height={30}
        opacity={trazo > 0 ? 1 : 0}
        viewBox={`0 0 ${ancho} 30`}
        style={{ marginTop: -size * 0.3 }}
      >
        <path
          d={`M 6 20 C ${ancho * 0.3} 6, ${ancho * 0.6} 28, ${ancho - 6} 12`}
          stroke={COLORS.durazno}
          strokeWidth={10}
          fill="none"
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={1}
          strokeDashoffset={1 - trazo}
          opacity={0.9}
        />
      </svg>
    </div>
  );
};

/** Pasos de la evaluación: el actual se enciende, los anteriores quedan marcados. */
export const PASOS_EVAL = ["Sensaciones", "Fotografías", "Piel", "Constancia"];
export const Evaluacion: React.FC<{
  at: number;
  paso: number; // −1 = ninguno aún; 4 = todo hecho
  marca?: number; // instante en que se marca el último
  style: React.CSSProperties;
}> = ({ at: atSec, paso, marca, style }) => {
  const { t } = useT();
  return (
    <div style={{ position: "absolute", width: 260, ...style }}>
      <Pop at={atSec} kind="left">
        <div
          style={{
            background: CARD,
            borderRadius: 26,
            padding: "14px 16px 12px",
            boxShadow: "0 12px 30px rgba(69,89,90,.35)",
          }}
        >
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 19,
              letterSpacing: "0.2em",
              color: COLORS.durazno,
              marginBottom: 6,
            }}
          >
            EVALUACIÓN DÍA 10
          </div>
          {PASOS_EVAL.map((nombre, i) => {
            const hecho =
              i < paso || (marca !== undefined && i === paso && t >= marca);
            const activo = i === paso && !hecho;
            return (
              <div
                key={nombre}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "5px 0",
                  opacity: hecho || activo ? 1 : 0.5,
                }}
              >
                <div
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: 13,
                    background: hecho
                      ? COLORS.salvia
                      : activo
                        ? COLORS.durazno
                        : "transparent",
                    border:
                      hecho || activo ? "none" : `3px solid ${COLORS.durazno}`,
                    boxSizing: "border-box",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    transform: activo
                      ? `scale(${1 + 0.12 * Math.sin(t * 6)})`
                      : undefined,
                  }}
                >
                  {hecho ? (
                    <svg width={16} height={16} viewBox="0 0 56 56">
                      <path
                        d="M12 29 L24 41 L44 17"
                        stroke={COLORS.marfil}
                        strokeWidth={9}
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  ) : null}
                </div>
                <div
                  style={{
                    fontFamily: FONTS.body,
                    fontWeight: 700,
                    fontSize: 25,
                    color: activo ? COLORS.durazno : COLORS.marfil,
                  }}
                >
                  {nombre}
                </div>
              </div>
            );
          })}
        </div>
      </Pop>
    </div>
  );
};

/** Escala del 1 al 5 (cuadro: "completa nuevamente la escala"): cada fila entra en su palabra y un cursor la recorre
 *  sin quedarse en ningún valor (la nota es de cada persona). */
export const Escala: React.FC<{
  filas: { texto: string; at: number }[];
  style: React.CSSProperties;
}> = ({ filas, style }) => {
  const { t } = useT();
  return (
    <div style={{ position: "absolute", width: 280, ...style }}>
      <Pop at={filas[0].at - 0.3} kind="up">
        <div
          style={{
            background: COLORS.durazno,
            borderRadius: 28,
            padding: "14px 18px 10px",
            boxShadow: "0 12px 30px rgba(69,89,90,.35)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 18,
              letterSpacing: "0.18em",
              color: COLORS.petroleo,
              marginBottom: 4,
            }}
          >
            <span>DEL 1 AL 5</span>
            <span>¿HOY?</span>
          </div>
          {filas.map((f, i) => {
            const entra = interpolate(t, [f.at, f.at + 0.25], [0, 1], CLAMP);
            // Cursor que va y vuelve 1→5→1 (ping-pong) desde que se nombra la fila
            const fase = Math.max(0, t - f.at) * 2.2 + i * 0.9;
            const pos = 2 - 2 * Math.cos((fase * Math.PI) / 4);
            return (
              <div key={f.texto} style={{ opacity: entra, padding: "6px 0" }}>
                <div
                  style={{
                    fontFamily: FONTS.body,
                    fontWeight: 700,
                    fontSize: 25,
                    color: COLORS.petroleo,
                    marginBottom: 4,
                  }}
                >
                  {f.texto}
                </div>
                <div
                  style={{ display: "flex", justifyContent: "space-between" }}
                >
                  {[0, 1, 2, 3, 4].map((n) => {
                    const cerca = Math.max(0, 1 - Math.abs(pos - n));
                    return (
                      <div
                        key={n}
                        style={{
                          width: 40,
                          height: 40,
                          borderRadius: 20,
                          background:
                            cerca > 0.5 ? COLORS.salvia : "rgba(69,89,90,.14)",
                          color: cerca > 0.5 ? COLORS.marfil : COLORS.petroleo,
                          fontFamily: FONTS.body,
                          fontWeight: 700,
                          fontSize: 22,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          transform: `scale(${1 + 0.18 * cerca})`,
                        }}
                      >
                        {n + 1}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </Pop>
    </div>
  );
};

/** Polaroids: cada foto cae girando en su palabra con un flash; las anteriores quedan debajo como un montón. */
export type Foto = { src: string; at: number; etiqueta: string };
export const Polaroids: React.FC<{ fotos: Foto[]; hasta: number }> = ({
  fotos,
  hasta,
}) => {
  const { t, frame, fps } = useT();
  if (t < fotos[0].at - 0.05 || t > hasta + 0.35) return null;
  const sale = interpolate(t, [hasta, hasta + 0.35], [0, 1], CLAMP);
  const fondo = Math.min(
    interpolate(t, [fotos[0].at - 0.05, fotos[0].at + 0.15], [0, 1], CLAMP),
    1 - sale,
  );
  const giros = [-6, 5, -3, 7];
  const desp = [
    [-40, 10],
    [36, -18],
    [-20, 26],
    [44, 6],
  ];
  return (
    <>
      {/* Fondo: la toma se apaga en Verde petróleo para que las fotos manden */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "rgba(69,89,90,.78)",
          opacity: fondo,
          backdropFilter: "blur(10px)",
        }}
      />
      {fotos.map((f, i) => {
        if (t < f.at) return null;
        const loc = frame - Math.round(f.at * fps);
        const p = spring({
          frame: loc,
          fps,
          config: { damping: 13, mass: 0.7 },
        });
        const flash = interpolate(loc, [0, 1, 6], [0.9, 0.9, 0], CLAMP);
        const ultima = fotos.filter((g) => t >= g.at).length - 1 === i;
        return (
          <React.Fragment key={f.src}>
            <div
              style={{
                position: "absolute",
                left: 540 - 330 + desp[i][0],
                top: 300 + desp[i][1] - sale * 1600,
                width: 660,
                padding: "26px 26px 0",
                background: "#FBF8F4",
                borderRadius: 10,
                boxShadow: "0 30px 60px rgba(0,0,0,.35)",
                transform: `rotate(${giros[i] * p + (1 - p) * 25}deg) scale(${1.25 - 0.25 * p}) translateY(${(1 - p) * -700}px)`,
                opacity: Math.min(1, p * 2),
                filter: ultima ? undefined : "brightness(.92)",
              }}
            >
              <Img
                src={staticFile(f.src)}
                style={{
                  width: 608,
                  height: 912,
                  objectFit: "cover",
                  display: "block",
                }}
              />
              <div
                style={{
                  height: 130,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0 10px",
                }}
              >
                <div
                  style={{
                    fontFamily: FONTS.display,
                    fontSize: Math.min(64, 440 / (0.7 * f.etiqueta.length)),
                    color: COLORS.petroleo,
                    whiteSpace: "nowrap",
                  }}
                >
                  {f.etiqueta}
                </div>
                <div
                  style={{
                    fontFamily: FONTS.body,
                    fontWeight: 700,
                    fontSize: 24,
                    letterSpacing: "0.18em",
                    color: COLORS.salvia,
                  }}
                >
                  {`${i + 1} / ${fotos.length}`}
                </div>
              </div>
            </div>
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: "#FFFFFF",
                opacity: flash,
              }}
            />
          </React.Fragment>
        );
      })}
    </>
  );
};

/** Lupa que recorre un fragmento de piel ("revisa si aparecieron moretones, irritación"). */
export const LupaPiel: React.FC<{
  desde: number;
  hasta: number;
  etiqueta: string;
}> = ({ desde, hasta, etiqueta }) => {
  const { t } = useT();
  if (t < desde || t >= hasta) return null;
  const k = (t - desde) / (hasta - desde);
  const x = 380 + Math.sin(k * Math.PI * 1.6) * 220;
  const y = 980 + Math.cos(k * Math.PI * 1.2) * 160;
  return (
    <>
      <svg
        width={1080}
        height={1920}
        style={{ position: "absolute", inset: 0 }}
      >
        <circle
          cx={x}
          cy={y}
          r={150}
          fill="rgba(250,237,205,.12)"
          stroke={COLORS.marfil}
          strokeWidth={14}
        />
        <circle
          cx={x}
          cy={y}
          r={150}
          fill="none"
          stroke={COLORS.petroleo}
          strokeWidth={4}
          strokeDasharray="10 14"
        />
        <line
          x1={x + 106}
          y1={y + 106}
          x2={x + 230}
          y2={y + 230}
          stroke={COLORS.salvia}
          strokeWidth={34}
          strokeLinecap="round"
        />
      </svg>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 1440,
          display: "flex",
          justifyContent: "center",
        }}
      >
        <Pop at={desde} kind="up">
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 54,
              color: COLORS.petroleo,
              background: COLORS.durazno,
              borderRadius: 50,
              padding: "14px 40px 12px",
              boxShadow: "0 12px 30px rgba(69,89,90,.35)",
            }}
          >
            {etiqueta}
          </div>
        </Pop>
      </div>
    </>
  );
};

/** Camino de 21 días (cuadro: "muestra los días pendientes"): 1–10 marcados, el 10 "hoy", 11–21 por delante. */
export const Camino21: React.FC<{ at: number; style: React.CSSProperties }> = ({
  at: atSec,
  style,
}) => {
  const { t } = useT();
  const W = 300;
  const pts = Array.from({ length: 21 }, (_, i) => {
    const fila = Math.floor(i / 7);
    const col = i % 7;
    const x = 26 + (fila % 2 === 0 ? col : 6 - col) * 41;
    return [x, 40 + fila * 62];
  });
  const d = pts.map(([x, y], i) => `${i ? "L" : "M"} ${x} ${y}`).join(" ");
  return (
    <div style={{ position: "absolute", width: W, ...style }}>
      <Pop at={atSec} kind="up">
        <div
          style={{
            background: CARD,
            borderRadius: 28,
            padding: "14px 10px 10px",
            boxShadow: "0 12px 30px rgba(69,89,90,.35)",
          }}
        >
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 19,
              letterSpacing: "0.2em",
              color: COLORS.durazno,
              textAlign: "center",
            }}
          >
            TU RETO DE 21 DÍAS
          </div>
          <svg width={W - 20} height={190} viewBox={`0 0 ${W - 20} 190`}>
            <path
              d={d}
              stroke="rgba(245,240,236,.25)"
              strokeWidth={4}
              fill="none"
              strokeDasharray="6 8"
            />
            {pts.map(([x, y], i) => {
              const dia = i + 1;
              const entra = interpolate(
                t,
                [atSec + 0.1 + i * 0.03, atSec + 0.25 + i * 0.03],
                [0, 1],
                CLAMP,
              );
              const hecho = dia <= 10;
              const hoy = dia === 10;
              const pend = interpolate(
                Math.sin(t * 3 - i * 0.5),
                [-1, 1],
                [0.35, 0.8],
              );
              return (
                <g key={i} opacity={entra}>
                  <circle
                    cx={x}
                    cy={y}
                    r={hoy ? 17 : 13}
                    fill={
                      hecho ? (hoy ? COLORS.durazno : COLORS.salvia) : "none"
                    }
                    stroke={hecho ? "none" : COLORS.durazno}
                    strokeWidth={3}
                    opacity={hecho ? 1 : pend}
                  />
                  <text
                    x={x}
                    y={y + 5}
                    textAnchor="middle"
                    fontFamily="Glacial Indifference"
                    fontWeight={700}
                    fontSize={hoy ? 16 : 13}
                    fill={hoy ? COLORS.petroleo : COLORS.marfil}
                  >
                    {dia}
                  </text>
                </g>
              );
            })}
          </svg>
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 24,
              color: COLORS.marfil,
              textAlign: "center",
              marginTop: 2,
            }}
          >
            <span style={{ color: COLORS.durazno }}>10</span> hechos ·{" "}
            <span style={{ color: COLORS.durazno }}>11</span> por delante
          </div>
        </div>
      </Pop>
    </div>
  );
};

/** "No estamos buscando perfección ni los cambios en el menor tiempo posible, estamos buscando que tú puedas
 *  adaptarte a una rutina" → dos columnas No / Sí que se llenan en sus palabras. */
export const NoSi: React.FC<{
  no: { texto: string; at: number }[];
  si: { texto: string; at: number };
  style: React.CSSProperties;
}> = ({ no, si, style }) => {
  const { t } = useT();
  const fila = (texto: string, at: number, tipo: "no" | "si") => {
    const d = interpolate(t, [at, at + 0.3], [0, 1], CLAMP);
    return (
      <div
        key={texto}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "6px 0",
          opacity: interpolate(t, [at - 0.05, at + 0.15], [0, 1], CLAMP),
        }}
      >
        <svg
          width={34}
          height={34}
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
            position: "relative",
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 26,
            lineHeight: 1.1,
            color: tipo === "si" ? COLORS.petroleo : "rgba(69,89,90,.75)",
          }}
        >
          {texto}
          {tipo === "no" ? (
            <div
              style={{
                position: "absolute",
                left: -2,
                top: "50%",
                height: 4,
                width: `${d * 100}%`,
                background: COLORS.petroleo,
                borderRadius: 2,
              }}
            />
          ) : null}
        </div>
      </div>
    );
  };
  return (
    <div style={{ position: "absolute", width: 280, ...style }}>
      <Pop at={no[0].at - 0.2} kind="up">
        <div
          style={{
            background: COLORS.durazno,
            borderRadius: 28,
            padding: "14px 16px 12px",
            boxShadow: "0 12px 30px rgba(69,89,90,.35)",
          }}
        >
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 18,
              letterSpacing: "0.2em",
              color: COLORS.petroleo,
            }}
          >
            NO BUSCAMOS
          </div>
          {no.map((n) => fila(n.texto, n.at, "no"))}
          <div
            style={{
              height: 2,
              background: "rgba(69,89,90,.2)",
              margin: "8px 0",
              opacity: interpolate(
                t,
                [si.at - 0.1, si.at + 0.1],
                [0, 1],
                CLAMP,
              ),
            }}
          />
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 18,
              letterSpacing: "0.2em",
              color: COLORS.salvia,
              opacity: interpolate(
                t,
                [si.at - 0.1, si.at + 0.1],
                [0, 1],
                CLAMP,
              ),
            }}
          >
            BUSCAMOS
          </div>
          {fila(si.texto, si.at, "si")}
        </div>
      </Pop>
    </div>
  );
};

/** Confeti de marca que estalla desde un punto ("¡Felicitaciones!"). Determinista: cada pieza tiene su semilla. */
const azar = (i: number, k: number) => {
  const x = Math.sin(i * 127.1 + k * 311.7) * 43758.5453;
  return x - Math.floor(x);
};
export const Confeti: React.FC<{ at: number; x: number; y: number }> = ({
  at: atSec,
  x,
  y,
}) => {
  const { t } = useT();
  const d = t - atSec;
  if (d < 0 || d > 2.4) return null;
  const colores = [
    COLORS.durazno,
    COLORS.salvia,
    COLORS.marfil,
    "#F3CFA0",
    COLORS.petroleo,
  ];
  return (
    <>
      {Array.from({ length: 70 }, (_, i) => {
        const ang = -Math.PI / 2 + (azar(i, 1) - 0.5) * Math.PI * 1.5;
        const v = 900 + azar(i, 2) * 900;
        const px = x + Math.cos(ang) * v * d * 0.9 + Math.sin(d * 6 + i) * 20;
        const py = y + Math.sin(ang) * v * d + 1100 * d * d;
        const rot = (azar(i, 3) - 0.5) * 900 * d;
        const w = 12 + azar(i, 4) * 14;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: px,
              top: py,
              width: w,
              height: w * (0.45 + azar(i, 5) * 0.4),
              background: colores[i % colores.length],
              borderRadius: i % 3 === 0 ? w : 3,
              transform: `rotate(${rot}deg) rotateX(${d * 500 + i * 30}deg)`,
              opacity: interpolate(d, [0, 0.1, 1.8, 2.4], [0, 1, 1, 0], CLAMP),
              boxShadow: "0 2px 4px rgba(0,0,0,.12)",
            }}
          />
        );
      })}
    </>
  );
};

/** Transición en círculo (iris): un disco Durazno crece desde el centro, tapa el corte y se abre en anillo. */
export const Iris: React.FC<{ en: number[] }> = ({ en }) => {
  const { frame, fps } = useT();
  return (
    <>
      {en.map((tr) => {
        const d = frame - Math.round(tr * fps);
        if (d < -7 || d > 8) return null;
        const r2 = interpolate(d, [-7, 0], [0, 1250], CLAMP);
        const r1 = interpolate(d, [0, 8], [0, 1300], CLAMP);
        return (
          <div
            key={tr}
            style={{
              position: "absolute",
              inset: 0,
              background: `radial-gradient(circle at 50% 42%, rgba(0,0,0,0) ${r1}px, ${COLORS.durazno} ${r1 + 1}px, ${COLORS.durazno} ${r2}px, rgba(0,0,0,0) ${r2 + 1}px)`,
              boxShadow: "inset 0 0 0 0 transparent",
            }}
          />
        );
      })}
    </>
  );
};
