import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import "./fuentes";
import datos from "./datos/v2.json";
import { Subtitulos2, B2 } from "./Subtitulos2";
import { ARollL2, CierreFoto, DegradadoTexto, EmojiPop, Segmento, TarjetaFoto, Chip } from "./Piezas";

// Vídeo 2 del lote 2 · unboxing (gel limpiador, línea Aqua, vaso Morning Glow)
const A = datos.anclas as Record<string, { s: number; e: number; seg: number }>;
const SEG = datos.segmentos as Segmento[];
const finSeg = (i: number) => SEG[i].editStart + SEG[i].dur;
export const V2_CIERRE = 2.6;
export const V2_DURACION = datos.duracionS + V2_CIERRE;

const GOLPES = [
  { t: A.esposo.s, fuerza: 0.05, dur: 0.8 },
  { t: A.parecido.s - 0.1, fuerza: 0.08, dur: 0.9 },
];

type Sfx = { t: number; src: string; vol: number };
const SFX: Sfx[] = [
  { t: A.gel.s, src: "pop.wav", vol: 0.28 },
  { t: A.esposo.s, src: "pop.wav", vol: 0.28 },
  { t: A.hidratada.s, src: "pop.wav", vol: 0.24 },
  { t: A.aqua.s, src: "pop.wav", vol: 0.26 },
  { t: A.calendula.s - 0.08, src: "swoosh_6.wav", vol: 0.22 },
  { t: A.investigar.s, src: "pop.wav", vol: 0.24 },
  { t: A.vasito.s - 0.06, src: "swoosh_std.wav", vol: 0.22 },
  { t: A.parecido.s - 0.05, src: "whip.wav", vol: 0.22 },
  { t: A.nuevo.s, src: "acierto.wav", vol: 0.18 },
  { t: datos.duracionS - 0.15, src: "swoosh_std.wav", vol: 0.24 },
];

export const V2: React.FC = () => {
  const { fps } = useVideoConfig();
  const total = V2_DURACION;
  const musica = (f: number) =>
    interpolate(f / fps, [0, 0.4, datos.duracionS - 0.4, datos.duracionS + 0.3, total - 0.9, total], [0, 0.09, 0.09, 0.2, 0.2, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <ARollL2 src="lote2/edit/v2_aroll.mp4" segmentos={SEG} golpes={GOLPES} luz={1.03} />
      <DegradadoTexto fuerza={0.5} />

      <EmojiPop icono="jabon" t={A.gel.s} hasta={finSeg(0)} x={820} y={760} tam={160} giro={10} />
      <Chip texto="Solo se los muestro" icono="guino" t={A.norecomiendo.s} hasta={A.norecomiendo.s + 2.2} x={540} y={300} />
      <EmojiPop icono="hombre" t={A.esposo.s} hasta={A.esposo.s + 1.6} x={830} y={720} tam={160} giro={10} />
      <EmojiPop icono="gotita" t={A.hidratada.s} hasta={finSeg(1)} x={820} y={760} tam={150} giro={10} />
      <EmojiPop icono="gotita" t={A.aqua.s} hasta={finSeg(2)} x={830} y={560} tam={150} giro={10} />
      <TarjetaFoto src="lote2/img/calendula.jpg" t={A.calendula.s - 0.1} hasta={A.calendula.s + 1.9} x={800} y={640} w={340} h={430} giro={4} />
      <EmojiPop icono="brillo" t={A.refrescante.s} hasta={finSeg(3)} x={260} y={700} tam={140} />
      <EmojiPop icono="lupa" t={A.investigar.s} hasta={finSeg(4)} x={830} y={720} tam={160} giro={10} />
      <EmojiPop icono="vaso" t={A.vasito.s} hasta={finSeg(5)} x={830} y={560} tam={170} giro={10} />
      <EmojiPop icono="nariz" t={A.parecido.s} hasta={finSeg(6) + 0.2} x={820} y={700} tam={170} giro={10} />
      <EmojiPop icono="brillo" t={A.nuevo.s} hasta={finSeg(7)} x={820} y={700} tam={150} />

      <Subtitulos2 bloques={datos.bloques as B2[]} sombraFuerte />

      <CierreFoto src="lote2/img/DSC09898.jpg" t={datos.duracionS} titulo="Les voy contando" sub="Sígueme para ver qué tal" icono="brillo" />

      <Audio src={staticFile("lote2/edit/v2_voz.wav")} />
      <Audio src={staticFile("lote2/edit/v2_musica.wav")} volume={musica} />
      {SFX.map((s, i) => (
        <Sequence key={i} from={Math.max(0, Math.round(s.t * fps))} durationInFrames={Math.round(2.2 * fps)}>
          <Audio src={staticFile(`sfx_sel/${s.src}`)} volume={s.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
