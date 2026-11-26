import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import "./fuentes";
import datos from "./datos/v3.json";
import { Subtitulos2, B2 } from "./Subtitulos2";
import { ARollL2, DegradadoTexto, Segmento, Chip } from "./Piezas";
import { CabelloMG, CorteMG, ListaMG, PanelBarra, Sello, TituloMG } from "./Graficos";

// Vídeo 3 del lote 2 · línea de reparación intensiva para el cabello
// Correcciones de la clienta: sin emojis, nada sobre la cara, con motion graphics y el vídeo termina cuando ella
// deja de hablar (sin foto ni tarjeta final).
const A = datos.anclas as Record<string, { s: number; e: number; seg: number }>;
const SEG = datos.segmentos as Segmento[];
const finSeg = (i: number) => SEG[i].editStart + SEG[i].dur;
export const V3_CIERRE = 0;
export const V3_DURACION = datos.duracionS + V3_CIERRE;

const MG_PROMESAS: [number, number] = [A.promesa.s - 0.1, A.mentira.e + 0.1];
const MG_CABELLO: [number, number] = [A.rubio.s - 0.35, A.recuperando.e + 0.25];

const GOLPES = [
  { t: A.caemos.s - 0.05, fuerza: 0.08, dur: 1.0, temblor: 8 },
  { t: A.norecomiendo.s, fuerza: 0.04, dur: 1.0 },
];

type Sfx = { t: number; src: string; vol: number };
const SFX: Sfx[] = [
  { t: MG_PROMESAS[0] - 0.08, src: "swoosh_6.wav", vol: 0.24 },
  { t: A.tinte.s, src: "pop.wav", vol: 0.24 },
  { t: A.plancha.s, src: "pop.wav", vol: 0.24 },
  { t: A.secador.s, src: "pop.wav", vol: 0.24 },
  { t: A.mentira.s - 0.03, src: "error.wav", vol: 0.2 },
  { t: MG_PROMESAS[1] - 0.05, src: "whip.wav", vol: 0.24 },
  { t: A.farmasi.s, src: "swoosh_std.wav", vol: 0.18 },
  { t: A.norecomiendo.s, src: "pop.wav", vol: 0.22 },
  { t: A.reales.s, src: "acierto.wav", vol: 0.15 },
  { t: MG_CABELLO[0] - 0.08, src: "swoosh_6.wav", vol: 0.24 },
  { t: MG_CABELLO[1] - 0.05, src: "swoosh_7.wav", vol: 0.2 },
  { t: A.reparacion.s - 0.35, src: "pop.wav", vol: 0.24 },
];

export const V3: React.FC = () => {
  const { fps } = useVideoConfig();
  const total = V3_DURACION;
  const musica = (f: number) =>
    interpolate(f / fps, [0, 0.4, total - 0.7, total], [0, 0.08, 0.08, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  const m = A.mentira.s;
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <ARollL2 src="lote2/edit/v3_aroll.mp4" segmentos={SEG} golpes={GOLPES} luz={1.03} />
      <DegradadoTexto fuerza={0.5} />

      <Chip texto="No se los recomiendo, se los muestro" t={A.norecomiendo.s} hasta={A.norecomiendo.s + 2.4} x={540} y={290} tam={40} />
      {/* panel en la zona libre (a la derecha de la cara) mientras enseña los productos */}
      <PanelBarra titulo="Reparación intensiva" etiqueta="Reparación" t0={A.reparacion.s - 0.35} t1={finSeg(8) - 0.05} tLlenar={[A.reparacion.s, A.intensiva.e + 0.1]} x={850} y={240} w={380} />

      <Subtitulos2 bloques={datos.bloques as B2[]} sombraFuerte ocultar={[MG_PROMESAS, MG_CABELLO]} />

      {/* MG 1 · las promesas que siempre rompemos */}
      <CorteMG desde={MG_PROMESAS[0]} hasta={MG_PROMESAS[1]}>
        <TituloMG texto="Lo que decimos" sub="Por más que digamos…" t0={MG_PROMESAS[0]} y={380} tam={112} />
        <ListaMG
          y={720}
          items={[
            { texto: "No me vuelvo a tinturar", t: A.tinte.s - 0.1, icono: "tinte", tachar: m + 0.05 },
            { texto: "Nada de plancha", t: A.plancha.s - 0.05, icono: "plancha", tachar: m + 0.12 },
            { texto: "Ni secador", t: A.secador.s - 0.05, icono: "secador", tachar: m + 0.19 },
          ]}
        />
        <Sello texto="¡MENTIRA!" t0={m} y={1320} />
      </CorteMG>

      {/* MG 2 · del rubio a recuperar el cabello */}
      <CorteMG desde={MG_CABELLO[0]} hasta={MG_CABELLO[1]}>
        <TituloMG texto="Mi cabello" t0={MG_CABELLO[0]} y={660} tam={120} />
        <CabelloMG t0={MG_CABELLO[0] + 0.1} tRubio={A.rubio.s} tPoco={A.poco.s} tRecupera={A.recuperando.s} y={920} />
      </CorteMG>

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
