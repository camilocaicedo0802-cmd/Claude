import { Audio, Video } from "@remotion/media";
import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { COLORS, FONT_FACES } from "../brand";
import { CarasProvider, DatosCaras } from "../rutinas/Caras";
import { Efecto } from "../rutinas/Rutina";
import { CLAMP } from "../rutinas/util";
import { carasConZoom, Zoom } from "../dia7/Base7";

// Base del día 9 "Rutina integrada". Lenguaje nuevo frente a los días 4–8:
// - Tarjeta de capítulo: en cada cambio de zona el "escenario" (toma + gráficos colocados sobre ella) se encoge a una
//   tarjeta con esquinas redondeadas sobre fondo Marfil y, en el margen de arriba, entra el capítulo (número, zona y
//   minutos) con la barra de los 5 tramos de la rutina. Así el título nunca toca la cara.
// - Barrido (whip): en algunos cortes dentro de una zona la toma sale y entra con desenfoque horizontal (filtro SVG).
// - Reencuadres lentos hacia la zona que se trabaja (zoom CSS; la cabeza se recalcula con el mismo zoom).

/** Tarjeta: el escenario se reduce a ESCALA y se coloca en (IZQ, ARRIBA). */
export const ESCALA = 0.68;
export const TARJETA_IZQ = (1080 * (1 - ESCALA)) / 2;
export const TARJETA_ARRIBA = 440;
export type Tarjeta = { desde: number; hasta: number };

export const progresoTarjeta = (tarjetas: Tarjeta[], t: number) =>
  tarjetas.reduce((acc, c) => {
    const p = interpolate(
      t,
      [c.desde, c.desde + 0.4, c.hasta - 0.35, c.hasta],
      [0, 1, 1, 0],
      { ...CLAMP, easing: Easing.inOut(Easing.cubic) },
    );
    return Math.max(acc, p);
  }, 0);

const zoomEn = (zooms: Zoom[], t: number) => {
  const z = zooms.find((q) => t >= q.desde && t < q.hasta);
  if (!z) return { s: 1, ox: 540, oy: 960 };
  const k = (t - z.desde) / (z.hasta - z.desde);
  const e = k * k * (3 - 2 * k);
  return { s: z.z0 + (z.z1 - z.z0) * e, ox: z.ox, oy: z.oy };
};

/** Barrido en un corte: la toma sale hacia la izquierda y la nueva entra desde la derecha, con desenfoque horizontal. */
const barrido = (whips: number[], frame: number, fps: number) => {
  for (const w of whips) {
    const d = frame - Math.round(w * fps);
    if (d < -5 || d > 5) continue;
    const k = d < 0 ? (d + 5) / 5 : (5 - d) / 5; // 0 → 1 en el corte → 0
    const e = k * k;
    return { dx: (d < 0 ? -1 : 1) * 140 * e, blur: 55 * e, s: 1 + 0.18 * e };
  }
  return { dx: 0, blur: 0, s: 1 };
};

export const Base9: React.FC<{
  caras: DatosCaras;
  zooms: Zoom[];
  tarjetas: Tarjeta[];
  whips: number[];
  finVoz: number;
  duracion: number;
  efectos: Efecto[];
  musica: number;
  musicaCierre: number;
  /** Dentro del escenario (se encoge con la tarjeta): gráficos colocados sobre la toma. */
  escenario: React.ReactNode;
  /** Fuera del escenario: título del capítulo, mosaicos, destellos. */
  children: React.ReactNode;
}> = ({
  caras,
  zooms,
  tarjetas,
  whips,
  finVoz,
  duracion,
  efectos,
  musica,
  musicaCierre,
  escenario,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const p = progresoTarjeta(tarjetas, t);
  const s = 1 - (1 - ESCALA) * p;
  const z = zoomEn(zooms, t);
  const w = barrido(whips, frame, fps);
  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.marfil }}>
      <style>{FONT_FACES}</style>
      {/* Fondo de la tarjeta: Marfil con dos halos Durazno y Salvia muy suaves */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at 12% 8%, rgba(250,237,205,.95) 0%, rgba(250,237,205,0) 45%), radial-gradient(circle at 92% 96%, rgba(109,139,116,.22) 0%, rgba(109,139,116,0) 45%), ${COLORS.marfil}`,
        }}
      />
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id="barrido9" x="-10%" y="0%" width="120%" height="100%">
          <feGaussianBlur stdDeviation={`${w.blur} 0`} edgeMode="duplicate" />
        </filter>
      </svg>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: 1080,
          height: 1920,
          transformOrigin: "0 0",
          transform: `translate(${TARJETA_IZQ * p}px, ${TARJETA_ARRIBA * p}px) scale(${s})`,
          borderRadius: 64 * p,
          overflow: "hidden",
          boxShadow:
            p > 0.01
              ? `0 ${40 * p}px ${90 * p}px rgba(69,89,90,${0.35 * p})`
              : undefined,
          backgroundColor: "#000",
        }}
      >
        <AbsoluteFill
          style={{
            transform: `translateX(${w.dx}px) scale(${z.s * w.s})`,
            transformOrigin: `${z.ox}px ${z.oy}px`,
            filter: w.blur > 0.5 ? "url(#barrido9)" : undefined,
          }}
        >
          <Video
            src={staticFile("dia9/apoyo.mp4")}
            muted
            objectFit="cover"
            style={{ width: "100%", height: "100%" }}
          />
        </AbsoluteFill>
        {/* Estela Durazno del barrido */}
        {w.blur > 0.5 ? (
          <AbsoluteFill
            style={{
              opacity: w.blur / 55,
              background:
                "linear-gradient(90deg, rgba(250,237,205,0) 0%, rgba(250,237,205,.35) 45%, rgba(250,237,205,.35) 55%, rgba(250,237,205,0) 100%)",
            }}
          />
        ) : null}
        <CarasProvider datos={carasConZoom(caras, zooms, fps)}>
          {escenario}
        </CarasProvider>
      </div>
      {children}
      {/* Voz en off ya limpia (scripts/rutinas/preparar_voz.py): un solo archivo, sin recortes en Remotion */}
      <Audio src={staticFile("dia9/voz.wav")} />
      <Audio
        src={staticFile("dia9/audio/musica.wav")}
        volume={(f) =>
          interpolate(
            f / fps,
            [finVoz, Math.min(duracion, finVoz + 0.4)],
            [musica, musicaCierre],
            CLAMP,
          )
        }
      />
      {efectos.map((e) => (
        <Sequence
          key={e.nombre}
          name={`SFX ${e.nombre}`}
          from={Math.max(0, Math.round(e.t * fps))}
          durationInFrames={Math.max(1, Math.round((e.dur ?? 2.5) * fps))}
        >
          <Audio src={staticFile(`dia9/audio/${e.src}.wav`)} volume={e.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
