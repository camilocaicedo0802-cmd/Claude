import React from "react";
import { evolvePath, getLength, getPointAtLength } from "@remotion/paths";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { MADEIRA } from "../data/mapas";
import { MANO, SANS, SERIF_ANCHA } from "../lib/fonts";
import { C, SOMBRA, SOMBRA_SUAVE } from "../lib/theme";
import { AnilloDiscontinuo } from "./decor";
import { Grano, Vineta } from "./base";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/* ------------------------------------------------------------------ */
/* Botón negro con la silueta de Madeira (equivalente al botón del logo) */
export const BotonIsla: React.FC<{
  cx: number;
  cy: number;
  d?: number;
  en: number;
  pinEn: number;
}> = ({ cx, cy, d = 480, en, pinEn }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - en,
    fps,
    config: { damping: 12, stiffness: 140, mass: 0.8 },
  });
  const blur = interpolate(frame - en, [0, 4], [12, 0], clamp);
  const pin = spring({
    frame: frame - pinEn,
    fps,
    config: { damping: 9, stiffness: 180, mass: 0.7 },
  });
  const iw = d * 0.72;
  const ih = (iw * MADEIRA.h) / MADEIRA.w;
  const flota = Math.sin((frame / fps) * 1.5) * 8;
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: cx - d / 2,
          top: cy - d / 2 + flota,
          width: d,
          height: d,
          borderRadius: "50%",
          background:
            "radial-gradient(circle at 40% 32%, #4b4b4b 0%, #1f1f1f 52%, #0a0a0a 100%)",
          boxShadow:
            "inset 0 -14px 34px rgba(0,0,0,0.7), inset 0 10px 24px rgba(255,255,255,0.08)",
          filter: `${SOMBRA}${blur > 0.3 ? ` blur(${blur}px)` : ""}`,
          scale: String(0.3 + 0.7 * p),
          translate: `${(1 - p) * 260}px 0px`,
          opacity: interpolate(frame - en, [0, 3], [0, 1], clamp),
        }}
      >
        <svg
          viewBox={`0 0 ${MADEIRA.w} ${MADEIRA.h}`}
          width={iw}
          height={ih}
          style={{
            position: "absolute",
            left: (d - iw) / 2,
            top: (d - ih) / 2,
            filter: "drop-shadow(0 0 16px rgba(255,255,255,0.75))",
          }}
        >
          <defs>
            <linearGradient id="isla-g" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#ffffff" />
              <stop offset="1" stopColor="#c9c9c9" />
            </linearGradient>
          </defs>
          <path d={MADEIRA.d} fill="url(#isla-g)" />
        </svg>
        {/* chincheta roja sobre Funchal (costa sur) */}
        <svg
          width={70}
          height={96}
          viewBox="0 0 70 96"
          style={{
            position: "absolute",
            left: (d - iw) / 2 + iw * 0.6 - 35,
            top: (d - ih) / 2 + ih * 0.72 - 92 + (1 - pin) * -260,
            opacity: frame >= pinEn ? 1 : 0,
            filter: "drop-shadow(6px 10px 8px rgba(0,0,0,0.55))",
          }}
        >
          <path
            d="M35 94 C35 94 4 54 4 33 A31 31 0 1 1 66 33 C66 54 35 94 35 94 Z"
            fill={C.rojoAcento}
          />
          <circle cx={35} cy={33} r={12} fill="#fff" />
        </svg>
      </div>
      <AnilloDiscontinuo cx={cx} cy={cy + flota} r={d / 2 + 34} en={en + 4} />
    </>
  );
};

/* ------------------------------------------------------------------ */
/* Escudo / insignia con sombra y entrada con rebote */
export const Insignia: React.FC<{
  src: string;
  x: number;
  y: number;
  size: number;
  en: number;
  redondo?: boolean;
}> = ({ src, x, y, size, en, redondo }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - en,
    fps,
    config: { damping: 10, stiffness: 170, mass: 0.7 },
  });
  if (frame < en) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: x - size / 2,
        top: y - size / 2 + Math.sin(frame / 9 + x) * 6,
        width: size,
        height: size,
        scale: String(p),
        rotate: `${(1 - p) * -25}deg`,
        filter: SOMBRA_SUAVE,
        borderRadius: redondo ? "50%" : undefined,
        overflow: redondo ? "hidden" : undefined,
        border: redondo ? "8px solid #fff" : undefined,
        background: redondo ? "#fff" : undefined,
      }}
    >
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: redondo ? "cover" : "contain",
        }}
      />
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Globo terráqueo de mesa en escala de grises que gira: eje inclinado 23,5°,
   aro meridiano con pivotes en los polos, cuello y peana. El contorno de la esfera
   se oscurece siempre para que no se funda con el fondo blanco. */
export const Globo: React.FC<{
  cx: number;
  cy: number;
  d: number;
  vel?: number;
  peana?: boolean;
  blur?: number;
  fase?: number;
}> = ({ cx, cy, d, vel = 2.2, peana = true, blur = 0, fase = 0 }) => {
  const frame = useCurrentFrame();
  const tex = staticFile("img/globo_textura.jpg");
  const R = d / 2;
  const off = -((frame * vel + fase) % (d * 2));
  const M = 70; // margen para el aro
  const ancho = d + M * 2;
  const alto = d + M + (peana ? 200 : M);
  const scx = M + R;
  const scy = M + R;
  const inc = -23.5; // inclinación del eje terrestre
  const Rm = R + 22; // radio del aro meridiano
  const pt = (ang: number, r: number) => {
    const a = (ang * Math.PI) / 180;
    return [scx + r * Math.cos(a), scy + r * Math.sin(a)] as const;
  };
  const aN = -90 + inc; // polo norte (arriba a la izquierda)
  const aS = 90 + inc; // polo sur
  const [nx, ny] = pt(aN, Rm);
  const [sx, sy] = pt(aS, Rm);
  const [bx, by] = pt(90, Rm); // punto más bajo del aro, donde nace el cuello
  const arco = `M ${nx.toFixed(1)} ${ny.toFixed(1)} A ${Rm} ${Rm} 0 1 1 ${bx.toFixed(1)} ${by.toFixed(1)}`;
  const [enx, eny] = pt(aN, R + 4);
  const [esx, esy] = pt(aS, R + 4);
  const baseY = scy + R + 150;
  return (
    <div
      style={{
        position: "absolute",
        left: cx - scx,
        top: cy - scy,
        width: ancho,
        height: alto,
        filter: `${SOMBRA}${blur ? ` blur(${blur}px)` : ""}`,
      }}
    >
      {peana ? (
        <svg
          width={ancho}
          height={alto}
          style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}
        >
          {/* cuello y peana */}
          <path
            d={`M ${scx - 9} ${by} L ${scx + 9} ${by} L ${scx + 16} ${baseY - 18} L ${scx - 16} ${baseY - 18} Z`}
            fill="#2a2a2a"
          />
          <ellipse cx={scx} cy={baseY} rx={R * 0.58} ry={26} fill="#161616" />
          <ellipse
            cx={scx}
            cy={baseY - 6}
            rx={R * 0.5}
            ry={18}
            fill="#3a3a3a"
          />
          <ellipse
            cx={scx}
            cy={baseY - 9}
            rx={R * 0.34}
            ry={10}
            fill="#4a4a4a"
          />
        </svg>
      ) : null}
      {/* esfera: el mapa gira a lo largo del ecuador inclinado */}
      <div
        style={{
          position: "absolute",
          left: M,
          top: M,
          width: d,
          height: d,
          borderRadius: "50%",
          overflow: "hidden",
          rotate: `${inc}deg`,
        }}
      >
        {[0, 1].map((k) => (
          <Img
            key={k}
            src={tex}
            style={{
              position: "absolute",
              top: 0,
              left: off + k * d * 2,
              width: d * 2,
              height: d,
            }}
          />
        ))}
      </div>
      {/* sombreado esférico + contorno siempre visible */}
      <div
        style={{
          position: "absolute",
          left: M,
          top: M,
          width: d,
          height: d,
          borderRadius: "50%",
          background:
            "radial-gradient(circle at 35% 30%, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0) 24%), radial-gradient(circle at 42% 38%, rgba(0,0,0,0) 44%, rgba(0,0,0,0.16) 70%, rgba(0,0,0,0.58) 100%)",
          boxShadow:
            "inset -20px -28px 54px rgba(0,0,0,0.35), inset 0 0 0 2px rgba(0,0,0,0.28)",
        }}
      />
      {peana ? (
        <svg
          width={ancho}
          height={alto}
          style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}
        >
          {/* aro meridiano con brillo metálico */}
          <path
            d={arco}
            fill="none"
            stroke="#262626"
            strokeWidth={13}
            strokeLinecap="round"
          />
          <path
            d={arco}
            fill="none"
            stroke="#7d7d7d"
            strokeWidth={3}
            strokeLinecap="round"
          />
          {/* eje y pivotes en los polos */}
          <line
            x1={enx}
            y1={eny}
            x2={nx}
            y2={ny}
            stroke="#262626"
            strokeWidth={7}
          />
          <line
            x1={esx}
            y1={esy}
            x2={sx}
            y2={sy}
            stroke="#262626"
            strokeWidth={7}
          />
          {[
            [nx, ny],
            [sx, sy],
          ].map(([x, y], k) => (
            <g key={k}>
              <circle cx={x} cy={y} r={14} fill="#262626" />
              <circle cx={x} cy={y} r={6} fill="#8a8a8a" />
            </g>
          ))}
        </svg>
      ) : null}
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Diálogo de interfaz tipo macOS + cursor que hace clic (estilo.md §4) */
export const DialogoUI: React.FC<{
  en: number;
  clicEn: number;
  cx?: number;
  cy?: number;
}> = ({ en, clicEn, cx = 540, cy = 1080 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - en,
    fps,
    config: { damping: 13, stiffness: 160, mass: 0.7 },
  });
  const blur = interpolate(frame - en, [0, 4], [14, 0], clamp);
  const W = 800,
    Hh = 470;
  const clic = frame >= clicEn;
  const flash = interpolate(frame - clicEn, [0, 2, 8], [0, 1, 0.35], clamp);
  // cursor: de abajo a la derecha hacia el botón "Entrenar"
  const cp = interpolate(frame, [en + 4, clicEn - 1], [0, 1], {
    ...clamp,
    easing: Easing.inOut(Easing.cubic),
  });
  const bx = cx + W / 4,
    by = cy + Hh / 2 - 64;
  const curX = interpolate(cp, [0, 1], [cx + 420, bx + 10]);
  const curY = interpolate(cp, [0, 1], [cy + 520, by + 6]);
  const curS = interpolate(frame - clicEn, [-1, 1, 4], [1, 0.82, 1], clamp);
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: cx - W / 2,
          top: cy - Hh / 2,
          width: W,
          height: Hh,
          borderRadius: 56,
          backgroundColor: C.dialogo,
          boxShadow: "0 40px 80px rgba(0,0,0,0.45)",
          scale: String(0.3 + 0.7 * p),
          translate: `${(1 - p) * 320}px ${(1 - p) * -80}px`,
          opacity: interpolate(frame - en, [0, 3], [0, 1], clamp),
          filter: blur > 0.3 ? `blur(${blur}px)` : undefined,
          overflow: "hidden",
          fontFamily: SANS,
          color: "#fff",
        }}
      >
        <div style={{ padding: "52px 54px 0" }}>
          <div
            style={{
              fontWeight: 700,
              fontSize: 52,
              letterSpacing: "-0.04em",
              lineHeight: 1,
            }}
          >
            Saltar{" "}
            <span
              style={{
                fontFamily: SERIF_ANCHA,
                fontStyle: "italic",
                fontSize: 62,
                letterSpacing: "-0.02em",
              }}
            >
              “Entrenamiento”
            </span>
          </div>
          <div
            style={{
              fontWeight: 700,
              fontSize: 27,
              letterSpacing: "-0.03em",
              lineHeight: 1.18,
              marginTop: 26,
              color: "#e9e9e9",
            }}
          >
            Saltar esto podría alejarte de tu objetivo.
            <br />
            ¿Estás seguro de querer descansar hoy?
          </div>
        </div>
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            bottom: 0,
            height: 128,
            display: "flex",
            borderTop: "2px solid #3a3a3a",
          }}
        >
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 700,
              fontSize: 50,
              color: C.teal,
              letterSpacing: "-0.04em",
            }}
          >
            Descansar
          </div>
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 700,
              fontSize: 50,
              letterSpacing: "-0.04em",
              color: clic ? "#ff3b47" : C.rojo,
              borderLeft: "2px solid #3a3a3a",
              backgroundColor: `rgba(120,12,22,${0.35 + flash * 0.5})`,
            }}
          >
            Entrenar
          </div>
        </div>
      </div>
      {frame >= en + 4 ? (
        <svg
          width={70}
          height={96}
          viewBox="0 0 24 33"
          style={{
            position: "absolute",
            left: curX,
            top: curY,
            scale: String(curS),
            transformOrigin: "0 0",
            filter: "drop-shadow(4px 6px 5px rgba(0,0,0,0.45))",
          }}
        >
          <path
            d="M1 1 L1 26 L7.5 20 L12 31 L16 29.5 L11.5 18.8 L20 18.8 Z"
            fill="#fff"
            stroke="#111"
            strokeWidth={1.6}
            strokeLinejoin="round"
          />
        </svg>
      ) : null}
    </>
  );
};

/* ------------------------------------------------------------------ */
/* Balón clásico en SVG con sombreado esférico */
export const Balon: React.FC<{ size: number; rot?: number }> = ({
  size,
  rot = 0,
}) => {
  const R = 100;
  const pent = (cx: number, cy: number, r: number, a0: number) =>
    Array.from({ length: 5 }, (_, k) => {
      const a = ((a0 + k * 72) * Math.PI) / 180;
      return `${(cx + r * Math.cos(a)).toFixed(1)},${(cy + r * Math.sin(a)).toFixed(1)}`;
    }).join(" ");
  const outer = Array.from({ length: 5 }, (_, k) => -54 + k * 72);
  return (
    <svg
      viewBox="-100 -100 200 200"
      width={size}
      height={size}
      style={{ rotate: `${rot}deg` }}
    >
      <defs>
        <radialGradient
          id="balon-g"
          cx={-32}
          cy={-38}
          r={160}
          gradientUnits="userSpaceOnUse"
        >
          <stop offset="0" stopColor="#ffffff" />
          <stop offset="0.55" stopColor="#e4e4e4" />
          <stop offset="1" stopColor="#8f8f8f" />
        </radialGradient>
        <clipPath id="balon-c">
          <circle r={R - 1} />
        </clipPath>
      </defs>
      <circle r={R} fill="url(#balon-g)" />
      <g
        clipPath="url(#balon-c)"
        fill="#141414"
        stroke="#2a2a2a"
        strokeWidth={1.5}
      >
        <polygon points={pent(0, 0, 30, -90)} />
        {outer.map((a) => {
          const rad = (a * Math.PI) / 180;
          return (
            <polygon
              key={a}
              points={pent(
                86 * Math.cos(rad),
                86 * Math.sin(rad),
                30,
                a + 180 - 90 + 54,
              )}
            />
          );
        })}
        {Array.from({ length: 5 }, (_, k) => {
          const a = ((-90 + k * 72) * Math.PI) / 180;
          return (
            <line
              key={k}
              x1={30 * Math.cos(a)}
              y1={30 * Math.sin(a)}
              x2={64 * Math.cos(a)}
              y2={64 * Math.sin(a)}
              stroke="#555"
              strokeWidth={2}
            />
          );
        })}
      </g>
      <circle r={R} fill="url(#balon-g)" opacity={0.25} />
      <circle r={R} fill="none" stroke="rgba(0,0,0,0.25)" strokeWidth={2} />
    </svg>
  );
};

/* ------------------------------------------------------------------ */
/* Gráfica que se dispara y rompe el borde superior, con el balón en la punta */
export const GraficaImparable: React.FC<{ en: number; dur?: number }> = ({
  en,
  dur = 26,
}) => {
  const frame = useCurrentFrame();
  const d =
    "M 110 1500 L 270 1390 L 400 1440 L 540 1230 L 660 1280 L 800 980 L 900 1010 L 1010 640 L 1120 230";
  const p = interpolate(frame - en, [0, dur], [0, 1], {
    ...clamp,
    easing: Easing.in(Easing.quad),
  });
  const L = getLength(d);
  const pt = getPointAtLength(d, Math.max(0.001, p) * L);
  const evo = evolvePath(p, d);
  const vel = interpolate(p, [0.6, 1], [0, 1], clamp);
  return (
    <>
      <svg
        width={1080}
        height={1920}
        style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}
      >
        <path
          d={d}
          fill="none"
          stroke="#111"
          strokeWidth={9}
          strokeLinejoin="round"
          strokeLinecap="round"
          strokeDasharray={evo.strokeDasharray}
          strokeDashoffset={evo.strokeDashoffset}
        />
        {[
          [270, 1390],
          [540, 1230],
          [800, 980],
          [1010, 640],
        ].map(([x, y], k) => {
          const vis = interpolate(
            frame - en,
            [
              dur * [0.18, 0.45, 0.68, 0.88][k],
              dur * [0.18, 0.45, 0.68, 0.88][k] + 4,
            ],
            [0, 1],
            clamp,
          );
          return <circle key={k} cx={x} cy={y} r={14 * vis} fill="#111" />;
        })}
      </svg>
      {p > 0 && pt ? (
        <div
          style={{
            position: "absolute",
            left: pt.x - 80,
            top: pt.y - 80,
            filter: `${SOMBRA_SUAVE}${vel > 0.05 ? ` blur(${vel * 3}px)` : ""}`,
          }}
        >
          <Balon size={160} rot={frame * 14} />
        </div>
      ) : null}
    </>
  );
};

/* ------------------------------------------------------------------ */
/* Botón contador de goles que se agrieta en "récords" */
export const BotonContador: React.FC<{
  cx: number;
  cy: number;
  d?: number;
  en: number;
  grietaEn: number;
  hasta?: number;
}> = ({ cx, cy, d = 560, en, grietaEn, hasta = 900 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - en,
    fps,
    config: { damping: 12, stiffness: 150, mass: 0.8 },
  });
  const n = Math.round(
    interpolate(frame, [en + 2, grietaEn], [0, hasta], {
      ...clamp,
      easing: Easing.out(Easing.cubic),
    }),
  );
  const temblor =
    frame >= grietaEn && frame < grietaEn + 6 ? Math.sin(frame * 9) * 10 : 0;
  const g = interpolate(frame - grietaEn, [0, 3], [0, 1], clamp);
  const grietas = [
    "M 340 190 L 300 120 L 318 60 L 280 0",
    "M 340 190 L 420 150 L 470 165 L 560 120",
    "M 340 190 L 380 270 L 360 330 L 400 420 L 380 520",
    "M 340 190 L 250 230 L 190 210 L 90 260 L 0 250",
    "M 340 190 L 310 260 L 240 330 L 200 440",
    "M 340 190 L 400 90 L 450 40",
    "M 300 120 L 240 110 L 200 60",
    "M 380 270 L 450 300 L 520 290",
  ];
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: cx - d / 2 + temblor,
          top: cy - d / 2,
          width: d,
          height: d,
          borderRadius: "50%",
          background:
            "radial-gradient(circle at 40% 32%, #4b4b4b 0%, #1f1f1f 52%, #0a0a0a 100%)",
          boxShadow: "inset 0 -14px 34px rgba(0,0,0,0.7)",
          filter: SOMBRA,
          scale: String(0.3 + 0.7 * p),
          opacity: interpolate(frame - en, [0, 3], [0, 1], clamp),
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: SANS,
          color: "#fff",
        }}
      >
        <div
          style={{
            fontWeight: 700,
            fontSize: 168,
            letterSpacing: "-0.08em",
            lineHeight: 0.9,
            textShadow:
              "0 0 18px rgba(255,255,255,0.75), 0 0 46px rgba(255,255,255,0.35)",
          }}
        >
          +{n}
        </div>
        <div
          style={{
            fontWeight: 700,
            fontSize: 40,
            letterSpacing: "0.22em",
            marginTop: 14,
            color: "#d8d8d8",
          }}
        >
          GOLES
        </div>
        {g > 0 ? (
          <svg
            width={d}
            height={d}
            viewBox="0 0 560 560"
            style={{ position: "absolute", left: 0, top: 0 }}
          >
            {grietas.map((gd, k) => {
              const evo = evolvePath(g, gd);
              return (
                <g key={k}>
                  <path
                    d={gd}
                    fill="none"
                    stroke="rgba(0,0,0,0.8)"
                    strokeWidth={6}
                    strokeDasharray={evo.strokeDasharray}
                    strokeDashoffset={evo.strokeDashoffset}
                  />
                  <path
                    d={gd}
                    fill="none"
                    stroke="rgba(255,255,255,0.9)"
                    strokeWidth={2.4}
                    strokeDasharray={evo.strokeDasharray}
                    strokeDashoffset={evo.strokeDashoffset}
                  />
                </g>
              );
            })}
            <circle
              cx={340}
              cy={190}
              r={10 * g}
              fill="rgba(255,255,255,0.85)"
            />
          </svg>
        ) : null}
      </div>
      <AnilloDiscontinuo cx={cx + temblor} cy={cy} r={d / 2 + 34} en={en + 4} />
    </>
  );
};

/* ------------------------------------------------------------------ */
/* Polaroid con cinta adhesiva y rótulo a mano que cae sobre la mesa */
export const Polaroid: React.FC<{
  src: string;
  texto: string;
  x: number;
  y: number;
  rot: number;
  en: number;
  ancho?: number;
  foco?: string;
}> = ({ src, texto, x, y, rot, en, ancho = 500, foco = "50% 40%" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - en,
    fps,
    config: { damping: 14, stiffness: 190, mass: 0.8 },
  });
  if (frame < en) return null;
  const foto = ancho - 44;
  const cinta: React.CSSProperties = {
    position: "absolute",
    width: 150,
    height: 46,
    background:
      "repeating-linear-gradient(90deg, rgba(236,226,200,0.86) 0 6px, rgba(226,214,186,0.86) 6px 9px)",
    boxShadow: "0 2px 4px rgba(0,0,0,0.15)",
  };
  return (
    <div
      style={{
        position: "absolute",
        left: x - ancho / 2,
        top: y - (foto + 120) / 2,
        width: ancho,
        padding: "22px 22px 0",
        background: "linear-gradient(160deg, #f4eedd 0%, #e8dec5 100%)",
        boxShadow: `${18 * p}px ${28 * p}px ${36 * p}px rgba(0,0,0,${0.18 + 0.2 * p})`,
        rotate: `${rot + (1 - p) * 18}deg`,
        scale: String(1 + (1 - p) * 0.3),
        translate: `0px ${(1 - p) * -420}px`,
        opacity: interpolate(frame - en, [0, 2], [0, 1], clamp),
      }}
    >
      <Img
        src={staticFile(src)}
        style={{
          width: foto,
          height: foto,
          objectFit: "cover",
          objectPosition: foco,
          filter: "sepia(0.25) contrast(1.06) saturate(0.85)",
        }}
      />
      <div
        style={{
          height: 100,
          display: "flex",
          alignItems: "center",
          paddingLeft: 10,
          fontFamily: MANO,
          fontSize: 36,
          color: "#1d1d1d",
          rotate: "-2deg",
        }}
      >
        {texto}
      </div>
      <div style={{ ...cinta, left: -40, top: -6, rotate: "-38deg" }} />
      <div style={{ ...cinta, right: -40, top: -6, rotate: "36deg" }} />
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Firma que se escribe de izquierda a derecha */
export const Firma: React.FC<{
  x: number;
  y: number;
  ancho: number;
  en: number;
  dur?: number;
}> = ({ x, y, ancho, en, dur = 20 }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - en, [0, dur], [0, 1], {
    ...clamp,
    easing: Easing.inOut(Easing.quad),
  });
  const alto = (ancho * 46.8) / 75.03;
  return (
    <div
      style={{
        position: "absolute",
        left: x - ancho / 2,
        top: y - alto / 2,
        width: ancho,
        height: alto,
        clipPath: `inset(0 ${(100 - p * 100).toFixed(2)}% 0 0)`,
        filter: "drop-shadow(10px 14px 10px rgba(0,0,0,0.25))",
      }}
    >
      <Img
        src={staticFile("img/firma.svg")}
        style={{ width: "100%", height: "100%" }}
      />
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Puntos negros alrededor de un centro que aparecen y luego salen disparados "más allá" */
export const Puntos: React.FC<{
  cx: number;
  cy: number;
  en: number;
  salenEn: number;
  n?: number;
  rMin?: number;
  rMax?: number;
}> = ({ cx, cy, en, salenEn, n = 34, rMin = 330, rMax = 470 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {Array.from({ length: n }, (_, k) => {
        const ang = k * 2.39996 + 0.4;
        const r = rMin + (((k * 37) % 100) / 100) * (rMax - rMin);
        const tam = 22 + ((k * 13) % 14);
        const sp = spring({
          frame: frame - en - k * 0.7,
          fps,
          config: { damping: 11, stiffness: 200, mass: 0.6 },
        });
        const sale = interpolate(frame - salenEn - (k % 6), [0, 14], [0, 1], {
          ...clamp,
          easing: Easing.in(Easing.cubic),
        });
        const rr = r * (1 + sale * 2.4);
        const x = cx + Math.cos(ang) * rr * 0.92;
        const y = cy + Math.sin(ang) * rr;
        if (frame < en + k * 0.7) return null;
        return (
          <div
            key={k}
            style={{
              position: "absolute",
              left: x - tam / 2,
              top: y - tam / 2,
              width: tam,
              height: tam,
              borderRadius: "50%",
              backgroundColor: "#121212",
              scale: String(sp * (1 + sale * 0.6)),
              filter: `drop-shadow(8px 12px 7px rgba(0,0,0,0.35))${sale > 0.05 ? ` blur(${sale * 5}px)` : ""}`,
            }}
          />
        );
      })}
    </>
  );
};

/* ------------------------------------------------------------------ */
/* Foto de archivo en B&N con trama de semitono (estilo.md §5.2) */
export const FotoSemitono: React.FC<{
  src: string;
  dur: number;
  origen?: string;
  empuje?: number;
}> = ({ src, dur, origen = "50% 35%", empuje = 0.06 }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: origen,
          filter: "grayscale(1) contrast(1.5) brightness(0.9)",
          scale: String(interpolate(frame, [0, dur], [1, 1 + empuje], clamp)),
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage:
            "radial-gradient(circle, rgba(0,0,0,0.55) 0 1.8px, transparent 2.4px)",
          backgroundSize: "7px 7px",
          mixBlendMode: "multiply",
        }}
      />
      <AbsoluteFill
        style={{
          backgroundImage:
            "radial-gradient(circle, rgba(255,255,255,0.32) 0 1.2px, transparent 1.9px)",
          backgroundSize: "7px 7px",
          backgroundPosition: "3.5px 3.5px",
          mixBlendMode: "screen",
        }}
      />
      <Vineta fuerza={0.45} />
      <Grano opacidad={0.1} />
    </AbsoluteFill>
  );
};

/** Mancha oscura radial detrás de una palabra suelta sobre foto (legibilidad). */
export const ManchaOscura: React.FC<{
  cx: number;
  cy: number;
  ancho?: number;
  alto?: number;
}> = ({ cx, cy, ancho = 640, alto = 320 }) => (
  <div
    style={{
      position: "absolute",
      left: cx - ancho / 2,
      top: cy - alto / 2,
      width: ancho,
      height: alto,
      background:
        "radial-gradient(ellipse at center, rgba(0,0,0,0.62) 0%, rgba(0,0,0,0.35) 45%, rgba(0,0,0,0) 72%)",
    }}
  />
);

/** Recorte (persona/objeto sin fondo) con sombra larga. */
export const Recorte: React.FC<{
  src: string;
  x: number;
  y: number;
  alto: number;
  style?: React.CSSProperties;
}> = ({ src, x, y, alto, style }) => (
  <Img
    src={staticFile(src)}
    style={{
      position: "absolute",
      left: x,
      top: y,
      height: alto,
      filter: SOMBRA,
      ...style,
    }}
  />
);
