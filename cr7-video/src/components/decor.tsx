import React from "react";
import { evolvePath } from "@remotion/paths";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../lib/theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Retícula de boceto 5x5 con cruces "+" y bordes desvanecidos (estilo.md §5.2). */
export const Reticula: React.FC<{
  cx: number;
  cy: number;
  size?: number;
  n?: number;
  en?: number;
  opacidad?: number;
}> = ({ cx, cy, size = 700, n = 5, en = 0, opacidad = 1 }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - en, [0, 10], [0, 1], {
    ...clamp,
    easing: Easing.out(Easing.cubic),
  });
  const paso = size / n;
  const id = `ret-${cx}-${cy}-${size}`;
  const lineas: React.ReactNode[] = [];
  for (let k = 0; k <= n; k++) {
    const v = k * paso;
    lineas.push(
      <line
        key={`h${k}`}
        x1={0}
        y1={v}
        x2={size}
        y2={v}
        stroke={C.reticula}
        strokeWidth={1.6}
      />,
    );
    lineas.push(
      <line
        key={`v${k}`}
        x1={v}
        y1={0}
        x2={v}
        y2={size}
        stroke={C.reticula}
        strokeWidth={1.6}
      />,
    );
  }
  const cruces: React.ReactNode[] = [];
  for (let a = 0; a <= n; a++)
    for (let b = 0; b <= n; b++) {
      const x = a * paso,
        y = b * paso;
      cruces.push(
        <path
          key={`c${a}-${b}`}
          d={`M${x - 9},${y} L${x + 9},${y} M${x},${y - 9} L${x},${y + 9}`}
          stroke="#6f6f6f"
          strokeWidth={2.2}
        />,
      );
    }
  return (
    <svg
      width={size}
      height={size}
      style={{
        position: "absolute",
        left: cx - size / 2,
        top: cy - size / 2,
        opacity: p * opacidad,
        scale: String(0.94 + 0.06 * p),
      }}
    >
      <defs>
        <radialGradient id={`${id}-g`}>
          <stop offset="0.55" stopColor="#fff" stopOpacity={1} />
          <stop offset="1" stopColor="#fff" stopOpacity={0} />
        </radialGradient>
        <mask id={`${id}-m`}>
          <rect width={size} height={size} fill={`url(#${id}-g)`} />
        </mask>
      </defs>
      <g mask={`url(#${id}-m)`}>
        {lineas}
        {cruces}
      </g>
    </svg>
  );
};

/** Forma negra desenfocada en primer plano (hojas/aspas en las esquinas). */
export const FormaDesenfocada: React.FC<{
  x: number;
  y: number;
  size?: number;
  rot?: number;
  vel?: number;
  blur?: number;
  opacidad?: number;
}> = ({ x, y, size = 560, rot = 0, vel = 8, blur = 16, opacidad = 0.88 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const r = rot + (frame / fps) * vel;
  const c = size / 2;
  return (
    <svg
      width={size}
      height={size}
      style={{
        position: "absolute",
        left: x - c,
        top: y - c,
        filter: `blur(${blur}px)`,
        opacity: opacidad,
        rotate: `${r}deg`,
      }}
    >
      {[0, 120, 240].map((a) => (
        <ellipse
          key={a}
          cx={c}
          cy={c - size * 0.26}
          rx={size * 0.075}
          ry={size * 0.24}
          fill="#0d0d0d"
          transform={`rotate(${a} ${c} ${c})`}
        />
      ))}
      <circle cx={c} cy={c} r={size * 0.07} fill="#0d0d0d" />
    </svg>
  );
};

/** Círculos grises desenfocados flotando (bokeh). */
export const Bokeh: React.FC<{
  puntos: Array<[number, number, number]>;
  en?: number;
}> = ({ puntos, en = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {puntos.map(([x, y, r], k) => {
        const p = interpolate(frame - en - k * 1.5, [0, 8], [0, 1], clamp);
        const dy = Math.sin((frame / fps) * 1.3 + k) * 12;
        return (
          <div
            key={k}
            style={{
              position: "absolute",
              left: x - r,
              top: y - r + dy,
              width: r * 2,
              height: r * 2,
              borderRadius: "50%",
              backgroundColor: C.bokeh,
              filter: `blur(${Math.max(2, r * 0.12)}px)`,
              opacity: p,
              scale: String(0.4 + 0.6 * p),
            }}
          />
        );
      })}
    </>
  );
};

/** Anillo discontinuo girando ~30°/s alrededor de un objeto circular. */
export const AnilloDiscontinuo: React.FC<{
  cx: number;
  cy: number;
  r: number;
  en?: number;
  color?: string;
  grosor?: number;
}> = ({ cx, cy, r, en = 0, color = "#151515", grosor = 4 }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - en, [0, 10], [0, 1], {
    ...clamp,
    easing: Easing.out(Easing.cubic),
  });
  const L = 2 * Math.PI * r;
  return (
    <svg
      width={r * 2 + 20}
      height={r * 2 + 20}
      style={{
        position: "absolute",
        left: cx - r - 10,
        top: cy - r - 10,
        rotate: `${frame * 1}deg`,
        opacity: p,
      }}
    >
      <circle
        cx={r + 10}
        cy={r + 10}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={grosor}
        strokeDasharray="16 12"
        strokeDashoffset={(1 - p) * L * 0.25}
      />
    </svg>
  );
};

/** Trazo dibujado a mano que se va trazando (flechas, subrayados, arcos). */
export const Trazo: React.FC<{
  d: string;
  en: number;
  dur?: number;
  grosor?: number;
  color?: string;
  flecha?: boolean;
  ancho?: number;
  alto?: number;
  x?: number;
  y?: number;
  blur?: number;
}> = ({
  d,
  en,
  dur = 10,
  grosor = 4,
  color = "#111",
  flecha = false,
  ancho = 1080,
  alto = 1920,
  x = 0,
  y = 0,
  blur = 0,
}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame - en, [0, dur], [0, 1], {
    ...clamp,
    easing: Easing.inOut(Easing.cubic),
  });
  if (p <= 0) return null;
  const evo = evolvePath(p, d);
  return (
    <svg
      width={ancho}
      height={alto}
      style={{
        position: "absolute",
        left: x,
        top: y,
        overflow: "visible",
        filter: blur ? `blur(${blur}px)` : undefined,
      }}
    >
      <defs>
        <marker
          id={`fl-${en}-${x}`}
          viewBox="0 0 10 10"
          refX="6"
          refY="5"
          markerWidth="5"
          markerHeight="5"
          orient="auto-start-reverse"
        >
          <path
            d="M0,0 L10,5 L0,10"
            fill="none"
            stroke={color}
            strokeWidth={2}
          />
        </marker>
      </defs>
      <path
        d={d}
        fill="none"
        stroke={color}
        strokeWidth={grosor}
        strokeLinecap="round"
        strokeDasharray={evo.strokeDasharray}
        strokeDashoffset={evo.strokeDashoffset}
        markerEnd={flecha && p > 0.97 ? `url(#fl-${en}-${x})` : undefined}
      />
    </svg>
  );
};

/** Arcos negros gruesos que cruzan el encuadre (estilo.md §5.2). */
export const Arcos: React.FC<{ en?: number; variante?: number }> = ({
  en = 0,
  variante = 0,
}) => {
  const ds =
    variante === 0
      ? ["M -80 1500 Q 540 1150 1180 1700", "M 760 -60 Q 1000 700 1160 1100"]
      : ["M -100 520 Q 520 900 1200 380", "M -60 1880 Q 420 1300 1160 1460"];
  return (
    <>
      <Trazo
        d={ds[0]}
        en={en}
        dur={12}
        grosor={11}
        color="#1a1a1a"
        blur={1.5}
      />
      <Trazo
        d={ds[1]}
        en={en + 3}
        dur={12}
        grosor={8}
        color="#1a1a1a"
        blur={3}
      />
    </>
  );
};
