import { Audio, Video } from "@remotion/media";
import React from "react";
import {
  AbsoluteFill,
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

// Base del día 7: como rutinas/Rutina.tsx (toma de apoyo + voz en off + música + efectos), con tres cambios para
// que no se vea igual que los días anteriores:
// - Reencuadres: cada toma puede acercarse despacio a la pierna que se trabaja (zoom CSS); la cara se recalcula
//   con el mismo zoom para que ningún gráfico la toque.
// - Etalonaje por momento: el arranque ("cansada") apagado y frío que se calienta; el descanso, cálido y suave.
// - Cortinas: en los cambios de zona una franja diagonal Durazno/Salvia barre la pantalla y tapa el corte.

export type Zoom = {
  desde: number;
  hasta: number;
  z0: number;
  z1: number;
  ox: number;
  oy: number;
};
const zoomEn = (zooms: Zoom[], t: number) => {
  const z = zooms.find((q) => t >= q.desde && t < q.hasta);
  if (!z) return { s: 1, ox: 540, oy: 960 };
  const k = (t - z.desde) / (z.hasta - z.desde);
  const e = k * k * (3 - 2 * k);
  return { s: z.z0 + (z.z1 - z.z0) * e, ox: z.ox, oy: z.oy };
};

/** Aplica a las cajas de la cara el mismo zoom que se le hace a la toma. */
export const carasConZoom = (
  datos: DatosCaras,
  zooms: Zoom[],
  fps = 30,
): DatosCaras => ({
  ...datos,
  caras: datos.caras.map((c) => {
    if (c[1] === null) return c;
    const { s, ox, oy } = zoomEn(zooms, (c[0] as number) / fps);
    const [n, x, y, w, h] = c as number[];
    return [
      n,
      Math.round(ox + (x - ox) * s),
      Math.round(oy + (y - oy) * s),
      Math.round(w * s),
      Math.round(h * s),
    ];
  }),
});

const Cortina: React.FC<{ en: number[] }> = ({ en }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <>
      {en.map((tr) => {
        const d = frame - Math.round(tr * fps);
        if (d < -8 || d > 8) return null;
        const x = interpolate(d, [-8, 8], [-1900, 1500]);
        return (
          <div
            key={tr}
            style={{
              position: "absolute",
              top: -300,
              bottom: -300,
              left: x,
              width: 1500,
              transform: "rotate(14deg)",
              display: "flex",
            }}
          >
            <div style={{ width: 140, background: COLORS.salvia }} />
            <div style={{ flex: 1, background: COLORS.durazno }} />
            <div style={{ width: 70, background: COLORS.marfil }} />
          </div>
        );
      })}
    </>
  );
};

export const Base7: React.FC<{
  caras: DatosCaras;
  zooms: Zoom[];
  filtro: (t: number) => string | undefined;
  velo: (t: number) => number;
  cortinas: number[];
  finVoz: number;
  duracion: number;
  efectos: Efecto[];
  musica: number;
  musicaCierre: number;
  children: React.ReactNode;
}> = ({
  caras,
  zooms,
  filtro,
  velo,
  cortinas,
  finVoz,
  duracion,
  efectos,
  musica,
  musicaCierre,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const { s, ox, oy } = zoomEn(zooms, t);
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <style>{FONT_FACES}</style>
      <AbsoluteFill
        style={{
          filter: filtro(t),
          transform: s !== 1 ? `scale(${s})` : undefined,
          transformOrigin: `${ox}px ${oy}px`,
        }}
      >
        <Video
          src={staticFile("dia7/apoyo.mp4")}
          muted
          objectFit="cover"
          style={{ width: "100%", height: "100%" }}
        />
      </AbsoluteFill>
      {/* Viñeta cálida (descanso) */}
      <AbsoluteFill
        style={{
          opacity: velo(t),
          background:
            "radial-gradient(ellipse at 50% 55%, rgba(250,237,205,0) 45%, rgba(69,89,90,.55) 100%)",
        }}
      />
      <CarasProvider datos={carasConZoom(caras, zooms, fps)}>
        {children}
      </CarasProvider>
      <Cortina en={cortinas} />
      <Audio src={staticFile("dia7/voz.wav")} />
      <Audio
        src={staticFile("dia7/audio/musica.wav")}
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
          <Audio src={staticFile(`dia7/audio/${e.src}.wav`)} volume={e.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
