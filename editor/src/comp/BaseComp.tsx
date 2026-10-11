import { Audio } from "@remotion/media";
import React from "react";
import {
  AbsoluteFill,
  Img,
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
import { ESCALA, progresoTarjeta, Tarjeta, TARJETA_ARRIBA, TARJETA_IZQ } from "../dia9/Base9";

// Base de los vídeos complementarios: la del día 9 (src/dia9/Base9.tsx, que no se toca) con la carpeta de medios
// (public/<carpeta>/fotogramas, voz.wav y audio/) como parámetro. Lenguaje del día 9:
// - Tarjeta de capítulo: en cada cambio de zona el "escenario" (toma + gráficos colocados sobre ella) se encoge a una
//   tarjeta con esquinas redondeadas sobre fondo Marfil y, en el margen de arriba, entra el capítulo (número, zona y
//   minutos) con la barra de los 5 tramos de la rutina. Así el título nunca toca la cara.
// - Barrido (whip): en algunos cortes dentro de una zona la toma sale y entra con desenfoque horizontal (filtro SVG).
// - Reencuadres lentos hacia la zona que se trabaja (zoom CSS; la cabeza se recalcula con el mismo zoom).

export { progresoTarjeta, ESCALA, TARJETA_ARRIBA, TARJETA_IZQ };
export type { Tarjeta };

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

export const BaseComp: React.FC<{
  /** Carpeta de public/ con fotogramas/, voz.wav y audio/ */
  carpeta: string;
  /** Fotogramas de la toma de apoyo (suma de los de clips.json) */
  fotogramas: number;
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
  carpeta,
  fotogramas,
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
        <filter id="barridoComp" x="-10%" y="0%" width="120%" height="100%">
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
            filter: w.blur > 0.5 ? "url(#barridoComp)" : undefined,
          }}
        >
          {/* La toma de apoyo como secuencia de JPEG (public/<carpeta>/fotogramas, sacada de apoyo.mp4): el Chromium del
              entorno no decodifica H.264 y el respaldo de Remotion se colgaba; así el render es determinista. */}
          <Img
            src={staticFile(`${carpeta}/fotogramas/${String(Math.min(frame, fotogramas - 1)).padStart(5, "0")}.jpg`)}
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
      <Audio src={staticFile(`${carpeta}/voz.wav`)} />
      <Audio
        src={staticFile(`${carpeta}/audio/musica.wav`)}
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
          <Audio src={staticFile(`${carpeta}/audio/${e.src}.wav`)} volume={e.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
