import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import "./fuentes";
import datos from "./datos/v3.json";
import { Subtitulos2, B2 } from "./Subtitulos2";
import { ARollL2, CierreFoto, DegradadoTexto, EmojiPop, Segmento, Chip } from "./Piezas";

// Vídeo 3 del lote 2 · línea de reparación intensiva para el cabello
const A = datos.anclas as Record<string, { s: number; e: number; seg: number }>;
const SEG = datos.segmentos as Segmento[];
const finSeg = (i: number) => SEG[i].editStart + SEG[i].dur;
export const V3_CIERRE = 2.6;
export const V3_DURACION = datos.duracionS + V3_CIERRE;

const GOLPES = [
  { t: A.mentira.s - 0.05, fuerza: 0.08, dur: 1.2 },
  { t: A.norecomiendo.s, fuerza: 0.04, dur: 1.0 },
];

type Sfx = { t: number; src: string; vol: number };
const SFX: Sfx[] = [
  { t: A.tinte.s, src: "pop.wav", vol: 0.26 },
  { t: A.plancha.s, src: "pop.wav", vol: 0.26 },
  { t: A.secador.s, src: "pop.wav", vol: 0.26 },
  { t: A.mentira.s - 0.05, src: "whip.wav", vol: 0.26 },
  { t: A.caemos.s, src: "pop.wav", vol: 0.28 },
  { t: A.farmasi.s, src: "swoosh_std.wav", vol: 0.2 },
  { t: A.reales.s, src: "acierto.wav", vol: 0.16 },
  { t: A.reparar.s, src: "pop.wav", vol: 0.24 },
  { t: A.intensiva.s, src: "pop.wav", vol: 0.26 },
  { t: datos.duracionS - 0.15, src: "swoosh_std.wav", vol: 0.24 },
];

export const V3: React.FC = () => {
  const { fps } = useVideoConfig();
  const total = V3_DURACION;
  const musica = (f: number) =>
    interpolate(f / fps, [0, 0.4, datos.duracionS - 0.4, datos.duracionS + 0.3, total - 0.9, total], [0, 0.08, 0.08, 0.2, 0.2, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <ARollL2 src="lote2/edit/v3_aroll.mp4" segmentos={SEG} golpes={GOLPES} luz={1.03} />
      <DegradadoTexto fuerza={0.5} />

      {/* gancho: tinte, plancha, secador… "es mentira" */}
      <EmojiPop icono="pelo" t={A.tinte.s} hasta={finSeg(1)} x={150} y={560} tam={150} giro={-8} />
      <EmojiPop icono="fuego" t={A.plancha.s} hasta={finSeg(1)} x={930} y={560} tam={140} giro={8} />
      <EmojiPop icono="viento" t={A.secador.s} hasta={finSeg(1)} x={150} y={800} tam={140} giro={-8} />
      <EmojiPop icono="risa" t={A.caemos.s} hasta={finSeg(1) + 0.15} x={925} y={820} tam={180} giro={10} />
      <Chip texto="No se los recomiendo, se los muestro" t={A.norecomiendo.s} hasta={A.norecomiendo.s + 2.4} x={540} y={290} tam={40} />
      <EmojiPop icono="check" t={A.reales.s} hasta={finSeg(4)} x={930} y={700} tam={140} giro={10} />
      <EmojiPop icono="brillo" t={A.reparar.s} hasta={finSeg(5)} x={830} y={520} tam={150} />
      <EmojiPop icono="brillo" t={A.intensiva.s} hasta={finSeg(8)} x={830} y={520} tam={150} />

      <Subtitulos2 bloques={datos.bloques as B2[]} sombraFuerte />

      <CierreFoto src="lote2/img/v3_cierre.jpg" t={datos.duracionS} titulo="Reparación intensiva" sub="Les voy contando" icono="brillo" />

      <Audio src={staticFile("lote2/edit/v3_voz.wav")} />
      <Audio src={staticFile("lote2/edit/v3_musica.wav")} volume={musica} />
      {SFX.map((s, i) => (
        <Sequence key={i} from={Math.max(0, Math.round(s.t * fps))} durationInFrames={Math.round(2.2 * fps)}>
          <Audio src={staticFile(`sfx_sel/${s.src}`)} volume={s.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
