import React, { createContext, useContext } from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C } from "../lib/theme";

export type Modo = "claro" | "oscuro";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

type Ctx = { from: number; dur: number; modo: Modo };
const EscenaCtx = createContext<Ctx>({ from: 0, dur: 1, modo: "claro" });
export const useEscena = () => useContext(EscenaCtx);

// Fotograma global (para sincronizar con las palabras de la locución) dentro de una escena.
export const useFrameGlobal = () => {
  const { from } = useEscena();
  return useCurrentFrame() + from;
};

/**
 * Escena = 1 frase. Incluye (estilo.md §6 y §7):
 * - empuje de cámara continuo 1,00 → 1+empuje
 * - entrada desenfocada (16 px → 0 y 1,07 → 1 en 6 fotogramas)
 * - salida zoom-blur (1 → 1,16 y 0 → 22 px en los últimos 5 fotogramas) + corte seco
 */
export const Escena: React.FC<{
  nombre: string;
  from: number;
  dur: number;
  modo?: Modo;
  empuje?: number;
  entrada?: boolean;
  salida?: boolean;
  fondo?: string;
  children: React.ReactNode;
}> = ({
  nombre,
  from,
  dur,
  modo = "claro",
  empuje = 0.05,
  entrada = true,
  salida = true,
  fondo,
  children,
}) => {
  const { fps } = useVideoConfig();
  return (
    <Sequence
      name={nombre}
      from={from}
      durationInFrames={dur}
      premountFor={fps}
    >
      <EscenaCtx.Provider value={{ from, dur, modo }}>
        <EscenaInterior
          dur={dur}
          empuje={empuje}
          entrada={entrada}
          salida={salida}
          fondo={fondo ?? (modo === "claro" ? C.blanco : "#000")}
        >
          {children}
        </EscenaInterior>
      </EscenaCtx.Provider>
    </Sequence>
  );
};

const EscenaInterior: React.FC<{
  dur: number;
  empuje: number;
  entrada: boolean;
  salida: boolean;
  fondo: string;
  children: React.ReactNode;
}> = ({ dur, empuje, entrada, salida, fondo, children }) => {
  const frame = useCurrentFrame();
  const empujeS = interpolate(frame, [0, dur], [1, 1 + empuje], {
    ...clamp,
    easing: Easing.inOut(Easing.quad),
  });
  const salidaS = salida
    ? interpolate(frame, [dur - 5, dur], [1, 1.16], {
        ...clamp,
        easing: Easing.in(Easing.cubic),
      })
    : 1;
  const salidaB = salida
    ? interpolate(frame, [dur - 5, dur], [0, 22], {
        ...clamp,
        easing: Easing.in(Easing.quad),
      })
    : 0;
  const entradaS = entrada
    ? interpolate(frame, [0, 6], [1.07, 1], {
        ...clamp,
        easing: Easing.out(Easing.cubic),
      })
    : 1;
  const entradaB = entrada
    ? interpolate(frame, [0, 6], [16, 0], {
        ...clamp,
        easing: Easing.out(Easing.quad),
      })
    : 0;
  const blur = Math.max(salidaB, entradaB);
  return (
    <AbsoluteFill style={{ backgroundColor: fondo, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          scale: String(empujeS * salidaS * entradaS),
          filter: blur > 0.3 ? `blur(${blur.toFixed(2)}px)` : undefined,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Grano de película: 6 texturas que se alternan cada fotograma. */
export const Grano: React.FC<{ opacidad?: number }> = ({ opacidad = 0.14 }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        mixBlendMode: "overlay",
        opacity: opacidad,
        pointerEvents: "none",
      }}
    >
      <Img
        src={staticFile(`img/grano_${frame % 6}.png`)}
        style={{ width: "100%", height: "100%" }}
      />
    </AbsoluteFill>
  );
};

export const Vineta: React.FC<{ fuerza?: number }> = ({ fuerza = 0.7 }) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse 75% 60% at 50% 48%, rgba(0,0,0,0) 40%, rgba(0,0,0,${fuerza}) 100%)`,
      pointerEvents: "none",
    }}
  />
);

/** Fondo fotográfico del modo oscuro (gradación ya aplicada en scripts/preparar_fondos.py). */
export const FotoOscura: React.FC<{
  src: string;
  empuje?: number;
  dur?: number;
  origen?: string;
}> = ({ src, empuje = 0.06, dur = 45, origen = "50% 50%" }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transformOrigin: origen,
          scale: String(interpolate(frame, [0, dur], [1, 1 + empuje], clamp)),
        }}
      />
      <Vineta />
      <Grano />
    </AbsoluteFill>
  );
};

/**
 * Entrada de objeto (estilo.md §5.3): escala 0,3 → 1 con rebote, rotación inicial,
 * desenfoque los primeros 4 fotogramas. `en` es el fotograma LOCAL de la escena.
 */
export const Aparece: React.FC<{
  en: number;
  desde?: number;
  rot?: number;
  dx?: number;
  dy?: number;
  flotar?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({
  en,
  desde = 0.3,
  rot = -20,
  dx = 0,
  dy = 0,
  flotar = 10,
  style,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame - en;
  const p = spring({
    frame: t,
    fps,
    config: { damping: 12, stiffness: 150, mass: 0.8 },
  });
  const blur = interpolate(t, [0, 4], [12, 0], clamp);
  const op = interpolate(t, [0, 3], [0, 1], clamp);
  const flota = Math.sin((frame / fps) * 1.6) * flotar;
  return (
    <div
      style={{
        position: "absolute",
        opacity: op,
        scale: String(desde + (1 - desde) * p),
        rotate: `${(1 - p) * rot}deg`,
        translate: `${(1 - p) * dx}px ${(1 - p) * dy + flota}px`,
        filter: blur > 0.3 ? `blur(${blur}px)` : undefined,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Destello blanco (fotograma 0 del vídeo, estilo.md §6). */
export const DestelloBlanco: React.FC<{ dur?: number }> = ({ dur = 5 }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#fff",
        opacity: interpolate(frame, [0, dur], [1, 0], clamp),
        pointerEvents: "none",
      }}
    />
  );
};

/** Punch-in: golpe de zoom con rebote en un momento concreto (fotograma LOCAL). */
export const Golpe: React.FC<{
  en: number;
  cuanto?: number;
  origen?: string;
  children: React.ReactNode;
}> = ({ en, cuanto = 0.1, origen = "50% 60%", children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - en,
    fps,
    config: { damping: 16, stiffness: 210, mass: 0.7 },
  });
  return (
    <AbsoluteFill
      style={{ scale: String(1 + cuanto * p), transformOrigin: origen }}
    >
      {children}
    </AbsoluteFill>
  );
};
