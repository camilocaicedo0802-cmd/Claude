import React from "react";
import { interpolate, spring } from "remotion";
import { COLORS, FONTS } from "../brand";
import { useCaras, zonasEn } from "../rutinas/Caras";
import { CARD, Pop, SOMBRA } from "../rutinas/Graficos";
import { CLAMP, useT } from "../rutinas/util";

// Gráficos 2D del día 7. Cambian el lenguaje de los días anteriores: títulos que entran letra a letra con el kicker
// en píldora, anillo de la rutina en vez de la tarjeta de minutos, racha de 7 días, elección silla/cama, chips que
// se encienden y una palabra que se tacha para dar paso a otra.

/**
 * Título grande del día 7. En este crudo la cabeza está casi en el borde superior (no cabe un título encima), así
 * que entra en la franja baja (y ≥ 1190, la zona de recursos de §10.10) letra a letra, con el kicker en píldora,
 * sobre una franja Verde petróleo suave; a los `dura` segundos se recoge (queda la píldora pequeña en la columna).
 */
export const TituloBajo: React.FC<{
  desde: number;
  kicker: string;
  texto: string;
  textoAt?: number;
  dura?: number;
}> = ({ desde, kicker, texto, textoAt, dura = 2.4 }) => {
  const caras = useCaras();
  const { t, frame, fps } = useT();
  const fin = desde + dura;
  if (t > fin + 0.4) return null;
  const { actual } = zonasEn(caras, t, desde, fin);
  const top = Math.max(1190, actual.y1 + 20);
  if (top > 1400) return null;
  const size = Math.min(124, 1000 / (0.74 * texto.length));
  const sale = interpolate(t, [fin, fin + 0.35], [1, 0], CLAMP);
  const entra = interpolate(t, [desde, desde + 0.25], [0, 1], CLAMP);
  const t0 = textoAt ?? desde + 0.1;
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: top - 90,
          height: size * 1.15 + 240,
          opacity: Math.min(entra, sale),
          background:
            "linear-gradient(180deg, rgba(69,89,90,0) 0%, rgba(69,89,90,.55) 35%, rgba(69,89,90,.55) 70%, rgba(69,89,90,0) 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 40,
          right: 40,
          top,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          opacity: sale,
          transform: `scale(${0.7 + 0.3 * sale})`,
          transformOrigin: "50% 0%",
        }}
      >
        <Pop at={desde} kind="scale">
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 30,
              letterSpacing: "0.2em",
              color: COLORS.petroleo,
              background: COLORS.durazno,
              borderRadius: 40,
              padding: "8px 22px 6px 26px",
              marginBottom: 6,
              boxShadow: "0 8px 24px rgba(69,89,90,.35)",
            }}
          >
            {kicker}
          </div>
        </Pop>
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: size,
            lineHeight: 1.05,
            color: COLORS.marfil,
            textShadow: SOMBRA,
            whiteSpace: "nowrap",
          }}
        >
          {texto.split("").map((ch, i) => {
            const f = frame - Math.round((t0 + i * 0.035) * fps);
            const p =
              f < 0
                ? 0
                : spring({ frame: f, fps, config: { damping: 15, mass: 0.5 } });
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  whiteSpace: "pre",
                  opacity: Math.min(1, p * 1.5),
                  transform: `translateY(${(1 - p) * 34}px)`,
                  filter: p < 0.9 ? `blur(${(1 - p) * 6}px)` : undefined,
                }}
              >
                {ch}
              </span>
            );
          })}
        </div>
      </div>
    </>
  );
};

/** Píldora con la zona actual (lo que queda del título cuando se recoge). */
export const PildoraZona: React.FC<{
  at: number;
  texto: string;
  style: React.CSSProperties;
}> = ({ at: atSec, texto, style }) => (
  <div style={{ position: "absolute", width: 300, ...style }}>
    <Pop at={atSec} kind="scale">
      <div
        style={{
          display: "inline-block",
          fontFamily: FONTS.body,
          fontWeight: 700,
          fontSize: 24,
          letterSpacing: "0.16em",
          color: COLORS.durazno,
          background: CARD,
          borderRadius: 30,
          padding: "10px 20px 8px",
          boxShadow: "0 8px 22px rgba(69,89,90,.3)",
          whiteSpace: "nowrap",
        }}
      >
        {texto}
      </div>
    </Pop>
  </div>
);

/** Insignia de velocidad en las tomas aceleradas (timelapse de "4 minutos", "rápido"). */
export const Velocidad: React.FC<{
  at: number;
  x: number;
  style: React.CSSProperties;
}> = ({ at: atSec, x, style }) => {
  const { t } = useT();
  return (
    <div style={{ position: "absolute", width: 170, ...style }}>
      <Pop at={atSec} kind="scale">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            background: COLORS.durazno,
            borderRadius: 40,
            padding: "8px 20px 8px 16px",
            boxShadow: "0 8px 22px rgba(69,89,90,.3)",
          }}
        >
          <svg width={46} height={30} viewBox="0 0 46 30">
            {[0, 1].map((i) => (
              <path
                key={i}
                d={`M${4 + i * 20} 3 L${22 + i * 20} 15 L${4 + i * 20} 27 Z`}
                fill={COLORS.petroleo}
                opacity={0.55 + 0.45 * Math.max(0, Math.sin(t * 10 - i * 1.4))}
              />
            ))}
          </svg>
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 40,
              color: COLORS.petroleo,
              lineHeight: 1,
            }}
          >
            ×{x}
          </div>
        </div>
      </Pop>
    </div>
  );
};

/** Anillo de la rutina: los 5 tramos del cuadro (1·4·4·3·3 min) como arcos; los de la zona actual se encienden y se llenan. */
export const TRAMOS = [
  { nombre: "Preparación", min: 1 },
  { nombre: "Pantorrilla der.", min: 4 },
  { nombre: "Pantorrilla izq.", min: 4 },
  { nombre: "Muslo der.", min: 3 },
  { nombre: "Muslo izq.", min: 3 },
];
export const Anillo: React.FC<{
  desde: number;
  hasta: number;
  activos: number[];
  centro: string;
  pie: string;
  style: React.CSSProperties;
}> = ({ desde, hasta, activos, centro, pie, style }) => {
  const { t } = useT();
  const R = 74;
  const total = 15;
  const hueco = 0.05; // radianes entre arcos
  const progreso = interpolate(t, [desde + 0.3, hasta], [0, 1], CLAMP);
  let a0 = -Math.PI / 2;
  const arcos = TRAMOS.map((tr, i) => {
    const ang = (tr.min / total) * Math.PI * 2;
    const arco = { i, a0: a0 + hueco / 2, a1: a0 + ang - hueco / 2 };
    a0 += ang;
    return arco;
  });
  const punto = (a: number) => [100 + R * Math.cos(a), 100 + R * Math.sin(a)];
  const path = (x0: number, x1: number) => {
    const [sx, sy] = punto(x0);
    const [ex, ey] = punto(x1);
    return `M ${sx} ${sy} A ${R} ${R} 0 ${x1 - x0 > Math.PI ? 1 : 0} 1 ${ex} ${ey}`;
  };
  const hechos = Math.min(...activos);
  return (
    <div style={{ position: "absolute", width: 260, ...style }}>
      <Pop at={desde} kind="scale">
        <div
          style={{
            background: CARD,
            borderRadius: 34,
            padding: "16px 14px 18px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            boxShadow: "0 16px 40px rgba(69,89,90,.35)",
          }}
        >
          <svg width={200} height={200}>
            {arcos.map(({ i, a0: x0, a1: x1 }) => {
              const activo = activos.includes(i);
              const hecho = i < hechos;
              return (
                <React.Fragment key={i}>
                  <path
                    d={path(x0, x1)}
                    stroke={hecho ? COLORS.salvia : "rgba(245,240,236,.22)"}
                    strokeWidth={16}
                    fill="none"
                    strokeLinecap="round"
                  />
                  {activo ? (
                    <path
                      d={path(x0, x0 + (x1 - x0) * Math.max(0.02, progreso))}
                      stroke={COLORS.durazno}
                      strokeWidth={16}
                      fill="none"
                      strokeLinecap="round"
                    />
                  ) : null}
                </React.Fragment>
              );
            })}
            <text
              x={100}
              y={104}
              textAnchor="middle"
              fontFamily="Glacial Indifference"
              fontWeight={700}
              fontSize={58}
              fill={COLORS.marfil}
            >
              {centro}
            </text>
            <text
              x={100}
              y={134}
              textAnchor="middle"
              fontFamily="Glacial Indifference"
              fontWeight={700}
              fontSize={20}
              letterSpacing="0.2em"
              fill={COLORS.durazno}
            >
              MIN
            </text>
          </svg>
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 27,
              color: COLORS.marfil,
              textAlign: "center",
              lineHeight: 1.12,
              marginTop: 2,
            }}
          >
            {pie}
          </div>
          <div
            style={{
              fontFamily: FONTS.body,
              fontSize: 18,
              letterSpacing: "0.14em",
              color: COLORS.durazno,
              marginTop: 6,
            }}
          >
            RUTINA DE 15 MIN
          </div>
        </div>
      </Pop>
    </div>
  );
};

/** Racha de 7 días: del 1 al 6 marcados; el 7 late y se marca en `marca` ("cumpliste"). */
export const Racha: React.FC<{
  at: number;
  marca: number;
  style: React.CSSProperties;
}> = ({ at: atSec, marca, style }) => {
  const { t } = useT();
  return (
    <div style={{ position: "absolute", width: 300, ...style }}>
      <Pop at={atSec} kind="up">
        <div
          style={{
            background: CARD,
            borderRadius: 28,
            padding: "14px 16px 16px",
            boxShadow: "0 12px 34px rgba(69,89,90,.35)",
          }}
        >
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 20,
              letterSpacing: "0.2em",
              color: COLORS.durazno,
              marginBottom: 10,
              textAlign: "center",
            }}
          >
            EL HÁBITO
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            {[1, 2, 3, 4, 5, 6, 7].map((d) => {
              const entra = interpolate(
                t,
                [atSec + 0.15 + d * 0.06, atSec + 0.35 + d * 0.06],
                [0, 1],
                CLAMP,
              );
              const hecho = d < 7 || t >= marca;
              const dm = interpolate(t, [marca, marca + 0.3], [0, 1], CLAMP);
              const late = d === 7 && t < marca ? 1 + 0.1 * Math.sin(t * 6) : 1;
              const pop = d === 7 ? 1 + 0.35 * Math.sin(dm * Math.PI) : 1;
              return (
                <div
                  key={d}
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 4,
                    opacity: entra,
                    transform: `scale(${late * pop})`,
                  }}
                >
                  <svg width={34} height={34} viewBox="0 0 56 56">
                    <circle
                      cx={28}
                      cy={28}
                      r={25}
                      fill={hecho ? COLORS.salvia : "none"}
                      stroke={COLORS.durazno}
                      strokeWidth={hecho ? 0 : 4}
                      strokeDasharray={hecho ? undefined : "8 6"}
                    />
                    {hecho ? (
                      <path
                        d="M16 29 L25 38 L41 20"
                        stroke={COLORS.marfil}
                        strokeWidth={6}
                        fill="none"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeDasharray={40}
                        strokeDashoffset={d === 7 ? 40 * (1 - dm) : 0}
                      />
                    ) : null}
                  </svg>
                  <div
                    style={{
                      fontFamily: FONTS.body,
                      fontWeight: 700,
                      fontSize: 16,
                      color: d === 7 ? COLORS.durazno : COLORS.marfil,
                    }}
                  >
                    {d}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </Pop>
    </div>
  );
};

const IconoSilla = () => (
  <svg width={44} height={44} viewBox="0 0 48 48">
    <path
      d="M14 6 V26 H36 M14 26 V42 M34 26 V42 M14 34 H34 M14 18 H30"
      stroke={COLORS.petroleo}
      strokeWidth={4.5}
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);
const IconoCama = () => (
  <svg width={44} height={44} viewBox="0 0 48 48">
    <path
      d="M5 12 V40 M5 30 H43 V40 M5 24 H43 V30 M10 24 V18 H22 V24"
      stroke={COLORS.petroleo}
      strokeWidth={4.5}
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);
/** "Sobre una silla o sobre la cama": dos opciones que se encienden cada una en su palabra. */
export const Eleccion: React.FC<{
  silla: number;
  cama: number;
  style: React.CSSProperties;
}> = ({ silla, cama, style }) => {
  const { t } = useT();
  const opcion = (at: number, texto: string, Icono: React.FC) => {
    const on = interpolate(t, [at, at + 0.25], [0, 1], CLAMP);
    return (
      <Pop at={at} kind="left">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            background: COLORS.durazno,
            borderRadius: 24,
            padding: "8px 16px",
            boxShadow: `0 0 0 ${4 * on}px ${COLORS.salvia}, 0 10px 26px rgba(69,89,90,.3)`,
          }}
        >
          <Icono />
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 30,
              color: COLORS.petroleo,
            }}
          >
            {texto}
          </div>
        </div>
      </Pop>
    );
  };
  return (
    <div
      style={{
        position: "absolute",
        width: 240,
        display: "flex",
        flexDirection: "column",
        gap: 8,
        ...style,
      }}
    >
      {opcion(silla, "Silla", IconoSilla)}
      <div
        style={{
          fontFamily: FONTS.display,
          fontSize: 40,
          color: COLORS.marfil,
          textShadow: SOMBRA,
          textAlign: "center",
          opacity: interpolate(t, [silla + 0.2, silla + 0.4], [0, 1], CLAMP),
          lineHeight: 0.9,
        }}
      >
        o
      </div>
      {opcion(cama, "Cama", IconoCama)}
    </div>
  );
};

/** Chips que se encienden uno a uno en la palabra que los nombra (p. ej. ascendentes · lentos · continuos). */
export const Chips: React.FC<{
  chips: { texto: string; at: number; icono?: string }[];
  style: React.CSSProperties;
}> = ({ chips, style }) => (
  <div
    style={{
      position: "absolute",
      width: 250,
      display: "flex",
      flexDirection: "column",
      gap: 12,
      ...style,
    }}
  >
    {chips.map((c) => (
      <Pop key={c.texto} at={c.at} kind="right">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            background: CARD,
            borderRadius: 40,
            padding: "10px 20px 10px 12px",
            boxShadow: "0 10px 26px rgba(69,89,90,.3)",
          }}
        >
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 22,
              background: COLORS.durazno,
              color: COLORS.petroleo,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 26,
            }}
          >
            {c.icono ?? "•"}
          </div>
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 30,
              color: COLORS.marfil,
            }}
          >
            {c.texto}
          </div>
        </div>
      </Pop>
    ))}
  </div>
);

/** Una palabra se tacha y da paso a otra: "rápido" → "mantén el movimiento". */
export const Tachado: React.FC<{
  at: number;
  tacha: number;
  cambia: number;
  antes: string;
  despues: string;
  style: React.CSSProperties;
}> = ({ at: atSec, tacha, cambia, antes, despues, style }) => {
  const { t } = useT();
  const raya = interpolate(t, [tacha, tacha + 0.3], [0, 1], CLAMP);
  const nueva = interpolate(t, [cambia, cambia + 0.3], [0, 1], CLAMP);
  return (
    <div style={{ position: "absolute", width: 300, ...style }}>
      <Pop at={atSec} kind="up">
        <div
          style={{
            background: COLORS.durazno,
            borderRadius: 28,
            padding: "14px 18px 16px",
            boxShadow: "0 12px 34px rgba(69,89,90,.35)",
            textAlign: "center",
          }}
        >
          <div
            style={{
              position: "relative",
              display: "inline-block",
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 38,
              color: COLORS.petroleo,
              opacity: 1 - 0.45 * nueva,
            }}
          >
            {antes}
            <div
              style={{
                position: "absolute",
                left: -6,
                top: "52%",
                height: 6,
                borderRadius: 3,
                width: `calc(${raya * 100}% + 12px)`,
                background: COLORS.salvia,
              }}
            />
          </div>
          <div
            style={{
              fontFamily: FONTS.display,
              fontSize: 31,
              lineHeight: 1.05,
              color: COLORS.petroleo,
              opacity: nueva,
              transform: `translateY(${(1 - nueva) * 14}px)`,
              marginTop: 4,
            }}
          >
            {despues.split(" ").length > 2
              ? [
                  despues.split(" ").slice(0, -1).join(" "),
                  despues.split(" ").slice(-1)[0],
                ].map((l) => <div key={l}>{l}</div>)
              : despues}
          </div>
        </div>
      </Pop>
    </div>
  );
};
