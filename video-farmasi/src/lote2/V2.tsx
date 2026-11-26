import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import "./fuentes";
import datos from "./datos/v2.json";
import { Subtitulos2, B2 } from "./Subtitulos2";
import { ARollL2, DegradadoTexto, Segmento, Chip } from "./Piezas";
import { BarraMG, CorteMG, Gotas, ListaMG, TituloMG } from "./Graficos";

// Vídeo 2 del lote 2 · unboxing (gel limpiador, línea Aqua, vaso Morning Glow)
// Correcciones de la clienta: sin emojis, nada sobre la cara, con motion graphics, iconos iguales en cada lista
// (no se mezclan iconos con fotos) y el vídeo termina cuando ella deja de hablar (sin tarjeta final).
const A = datos.anclas as Record<string, { s: number; e: number; seg: number }>;
const SEG = datos.segmentos as Segmento[];
const finSeg = (i: number) => SEG[i].editStart + SEG[i].dur;
export const V2_CIERRE = 0;
export const V2_DURACION = datos.duracionS + V2_CIERRE;

// cortes de motion graphics
const MG_AQUA: [number, number] = [A.toner.s - 0.25, A.calendula.e + 0.05];
const MG_HIDRATA: [number, number] = [A.hidrata.s - 0.2, finSeg(3)];

const GOLPES = [
  { t: A.esposo.s, fuerza: 0.05, dur: 0.8 },
  { t: A.parecido.s - 0.1, fuerza: 0.08, dur: 0.9, temblor: 8 },
];

type Sfx = { t: number; src: string; vol: number };
const SFX: Sfx[] = [
  { t: A.norecomiendo.s, src: "pop.wav", vol: 0.22 },
  { t: MG_AQUA[0] - 0.08, src: "swoosh_6.wav", vol: 0.24 },
  { t: A.toner.s, src: "pop.wav", vol: 0.24 },
  { t: A.tonico.s, src: "pop.wav", vol: 0.24 },
  { t: A.crema.s, src: "pop.wav", vol: 0.24 },
  { t: MG_AQUA[1] - 0.05, src: "swoosh_7.wav", vol: 0.2 },
  { t: MG_HIDRATA[0] - 0.08, src: "swoosh_6.wav", vol: 0.22 },
  { t: MG_HIDRATA[1] - 0.05, src: "swoosh_7.wav", vol: 0.2 },
  { t: A.vasito.s, src: "pop.wav", vol: 0.24 },
  { t: A.parecido.s - 0.05, src: "whip.wav", vol: 0.22 },
  { t: A.nuevo.s, src: "acierto.wav", vol: 0.16 },
];

export const V2: React.FC = () => {
  const { fps } = useVideoConfig();
  const total = V2_DURACION;
  const musica = (f: number) =>
    interpolate(f / fps, [0, 0.4, total - 0.7, total], [0, 0.09, 0.09, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <ARollL2 src="lote2/edit/v2_aroll.mp4" segmentos={SEG} golpes={GOLPES} luz={1.03} />
      <DegradadoTexto fuerza={0.5} />

      <Chip texto="No se los recomiendo, solo se los muestro" t={A.norecomiendo.s} hasta={A.norecomiendo.s + 2.4} x={540} y={300} tam={40} />
      <Chip texto="Vaso Morning Glow" t={A.vasito.s - 0.05} hasta={finSeg(5) - 0.05} x={540} y={200} />

      <Subtitulos2 bloques={datos.bloques as B2[]} sombraFuerte ocultar={[MG_AQUA, MG_HIDRATA]} />

      {/* MG 1 · línea Aqua: los productos aparecen al nombrarlos */}
      <CorteMG desde={MG_AQUA[0]} hasta={MG_AQUA[1]}>
        <TituloMG texto="Línea Aqua" sub="Lo que me llegó" t0={MG_AQUA[0]} y={430} />
        <ListaMG
          y={820}
          items={[
            { texto: "Tóner", t: A.toner.s, icono: "frasco" },
            { texto: "Tónico", t: A.tonico.s, icono: "gota" },
            { texto: "Crema facial de caléndula", t: A.crema.s, icono: "flor" },
          ]}
        />
      </CorteMG>

      {/* MG 2 · refresca e hidrata */}
      <CorteMG desde={MG_HIDRATA[0]} hasta={MG_HIDRATA[1]}>
        <Gotas t0={MG_HIDRATA[0]} />
        <TituloMG texto="Refresca e hidrata" t0={MG_HIDRATA[0]} y={560} tam={112} />
        <BarraMG t0={MG_HIDRATA[0] + 0.25} t1={MG_HIDRATA[1] - 0.25} y={900} etiqueta="Hidratación" />
      </CorteMG>

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
