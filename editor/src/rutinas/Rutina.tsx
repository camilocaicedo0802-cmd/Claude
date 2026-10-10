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
import { CarasProvider, DatosCaras } from "./Caras";
import { CLAMP } from "./util";

export type Efecto = {
  t: number;
  src: string;
  vol: number;
  dur?: number;
  nombre: string;
};
const MUSICA = 0.1; // ~16 dB bajo la voz (estilo.md §10.14)
const MUSICA_CIERRE = 0.2;

/** Base de las rutinas con voz en off: toma de apoyo + voz en off + música + efectos + gráficos. */
export const Rutina: React.FC<{
  dia: string;
  caras: DatosCaras;
  transiciones: number[];
  finVoz: number;
  duracion: number;
  efectos: Efecto[];
  /** Volumen de la música (por defecto 0,1 ≈ 16 dB bajo una voz de ≈ −16 LUFS) y al acabar de hablar. */
  musica?: number;
  musicaCierre?: number;
  children: React.ReactNode;
}> = ({
  dia,
  caras,
  transiciones,
  finVoz,
  duracion,
  efectos,
  musica = MUSICA,
  musicaCierre = MUSICA_CIERRE,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  // Cambios de zona del cuerpo → destello Durazno + desenfoque breve (estilo.md §10.12)
  let blur = 0;
  let destello = 0;
  for (const tr of transiciones) {
    const d = frame - Math.round(tr * fps);
    blur = Math.max(blur, interpolate(d, [-4, 0, 5], [0, 8, 0], CLAMP));
    destello = Math.max(
      destello,
      interpolate(d, [-2, 0, 5], [0, 0.22, 0], CLAMP),
    );
  }
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <style>{FONT_FACES}</style>
      <AbsoluteFill
        style={{ filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}
      >
        <Video
          src={staticFile(`${dia}/apoyo.mp4`)}
          muted
          objectFit="cover"
          style={{ width: "100%", height: "100%" }}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{ backgroundColor: COLORS.durazno, opacity: destello }}
      />
      {/* Velo Verde petróleo arriba: legibilidad de los títulos sobre la cortina clara */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(69,89,90,.6) 0%, rgba(69,89,90,.32) 20%, rgba(69,89,90,0) 34%)",
        }}
      />
      <CarasProvider datos={caras}>{children}</CarasProvider>
      {/* Voz en off ya limpia (scripts/rutinas/preparar_voz.py): un solo archivo, sin recortes en Remotion */}
      <Audio src={staticFile(`${dia}/voz.wav`)} />
      <Audio
        src={staticFile(`${dia}/audio/musica.wav`)}
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
          <Audio src={staticFile(`${dia}/audio/${e.src}.wav`)} volume={e.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
