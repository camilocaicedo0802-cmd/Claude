import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import "./fuentes";
import datos from "./datos/v1.json";
import { Subtitulos2, B2 } from "./Subtitulos2";
import { ARollL2, CierreFoto, DegradadoTexto, Segmento, TarjetaFoto, Chip } from "./Piezas";
import { ContadorAnios, Destellos, FlujoIconos, LogoPlaca, MemeRecorte, Pegatina, Tragamonedas, VisorREC, WhatsApp3D } from "./Graficos";

// Vídeo 1 del lote 2 · sketch "Bienvenida al equipo" (Chiqui y Gordi)
// Correcciones de la clienta: sin emojis, nada sobre las caras, más recursos de humor y sin etiquetas de personaje.
// Las posiciones salen de la detección de caras por toma (scripts/caras.py).
const A = datos.anclas as Record<string, { s: number; e: number; seg: number }>;
const SEG = datos.segmentos as Segmento[];
const ini = (i: number) => SEG[i].editStart;
const finSeg = (i: number) => SEG[i].editStart + SEG[i].dur;
export const V1_CIERRE = 2.7;
export const V1_DURACION = datos.duracionS + V1_CIERRE;

const GOLPES = [
  { t: A.chiste.s, fuerza: 0.1, dur: 0.6 },
  { t: A.abuela.s, fuerza: 0.12, dur: 0.6, temblor: 16 },
  { t: A.conservada.s - 0.1, fuerza: 0.1, dur: 0.8 },
  { t: A.grabar.s, fuerza: 0.06, dur: 0.6 },
  { t: A.ultima.s - 0.2, fuerza: 0.08, dur: 0.9 },
  { t: A.gym.s, fuerza: 0.1, dur: 0.9, temblor: 10 },
];

type Sfx = { t: number; src: string; vol: number };
// Sonidos de meme (fuentes que indicó la clienta: creatorset.com)
const SFX_MEME: Sfx[] = [
  { t: A.abuela.e - 0.05, src: "lote2/memes/boom.wav", vol: 0.2 },
  { t: A.final.e + 0.05, src: "lote2/memes/risas.wav", vol: 0.32 },
];
const SFX: Sfx[] = [
  { t: A.turquia.s - 0.08, src: "swoosh_4.wav", vol: 0.22 },
  { t: A.chiste.s - 0.05, src: "whip.wav", vol: 0.24 },
  { t: A.chiste.s + 0.25, src: "contador.wav", vol: 0.16 },
  { t: A.conservada.s + 0.05, src: "chasquido.wav", vol: 0.4 },
  { t: A.maquillaje.s - 0.06, src: "swoosh_6.wav", vol: 0.22 },
  { t: A.skincare.s - 0.06, src: "swoosh_7.wav", vol: 0.2 },
  { t: A.cabello.s - 0.06, src: "swoosh_6.wav", vol: 0.2 },
  { t: A.nutriplus.s - 0.06, src: "swoosh_std.wav", vol: 0.22 },
  { t: A.redes.s, src: "pop.wav", vol: 0.24 },
  { t: A.link.s, src: "pop.wav", vol: 0.24 },
  { t: A.compra.s, src: "pop.wav", vol: 0.24 },
  { t: A.casa.s, src: "pop.wav", vol: 0.24 },
  { t: A.descuento.s, src: "pop.wav", vol: 0.28 },
  { t: A.grabar.s - 0.6, src: "shutter.wav", vol: 0.3 },
  { t: A.agencia.s - 0.05, src: "swoosh_std.wav", vol: 0.24 },
  { t: A.ganar.s - 1.2, src: "contador.wav", vol: 0.22 },
  { t: A.whatsapp.s, src: "notif.wav", vol: 0.3 },
  { t: A.whatsapp.s - 0.1, src: "swoosh_6.wav", vol: 0.2 },
  { t: A.ultima.s - 0.35, src: "whoosh_2.wav", vol: 0.22 },
  { t: A.gym.s - 0.03, src: "whip.wav", vol: 0.26 },
  { t: ini(22) + 0.05, src: "error.wav", vol: 0.18 },
  { t: A.cafe.s - 0.1, src: "pop.wav", vol: 0.26 },
  { t: datos.duracionS - 0.15, src: "swoosh_std.wav", vol: 0.25 },
];

export const V1: React.FC = () => {
  const { fps } = useVideoConfig();
  const total = V1_DURACION;
  const musica = (f: number) =>
    interpolate(f / fps, [0, 0.4, datos.duracionS - 0.4, datos.duracionS + 0.3, total - 0.9, total], [0, 0.085, 0.085, 0.2, 0.2, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <ARollL2 src="lote2/edit/v1_aroll.mp4" segmentos={SEG} golpes={GOLPES} />
      <DegradadoTexto />

      <TarjetaFoto src="lote2/img/turquia.jpg" t={A.turquia.s - 0.1} hasta={finSeg(2) - 0.15} x={290} y={640} w={380} h={480} giro={-3} etiqueta="Turquía" />

      {/* "¿En 1950?": Gordi hace cuentas (a su derecha, lejos de su cara) */}
      <ContadorAnios t0={A.chiste.s} t1={A.abuela.s - 0.1} x={830} y={380} />
      {/* "más vieja que mi abuela": meme de la abuela bailando + "boom" */}
      <MemeRecorte src="lote2/memes/abuela.webm" t0={A.abuela.e - 0.05} dur={finSeg(3) - A.abuela.e + 0.03} x={835} y={250} ancho={400} alto={870} giro={3} />
      {/* "pero mejor conservada": destellos alrededor de Chiqui, sin tocar la cara */}
      <Destellos
        t0={A.conservada.s - 0.05}
        t1={finSeg(4)}
        puntos={[
          { x: 640, y: 560, tam: 90, d: 0 },
          { x: 1000, y: 640, tam: 70, d: 0.1 },
          { x: 650, y: 930, tam: 60, d: 0.2 },
          { x: 990, y: 980, tam: 80, d: 0.05 },
        ]}
      />

      {/* productos: tarjetas en el hueco entre las dos */}
      <TarjetaFoto src="lote2/img/farmasi_maquillaje.jpg" t={A.maquillaje.s - 0.1} hasta={A.skincare.s - 0.08} x={556} y={600} w={350} h={440} giro={-2} etiqueta="Maquillaje" />
      <TarjetaFoto src="lote2/img/farmasi_skincare.jpg" t={A.skincare.s - 0.1} hasta={A.cabello.s - 0.08} x={556} y={600} w={350} h={440} giro={2} etiqueta="Skin care" />
      <TarjetaFoto src="lote2/img/farmasi_cabello.jpg" t={A.cabello.s - 0.1} hasta={A.nutriplus.s - 0.08} x={556} y={600} w={350} h={440} giro={-2} etiqueta="Cabello" />
      <TarjetaFoto src="lote2/img/nutriplus.jpg" t={A.nutriplus.s - 0.1} hasta={finSeg(5) - 0.2} x={556} y={600} w={350} h={440} giro={2} foco="50% 40%" etiqueta="Nutriplus" />

      <FlujoIconos
        pasos={[
          { icono: "celular", t: A.redes.s, texto: "Redes" },
          { icono: "enlace", t: A.link.s, texto: "Link" },
          { icono: "bolsa", t: A.compra.s, texto: "Compra" },
          { icono: "casa", t: A.casa.s, texto: "A su casa" },
        ]}
        hasta={finSeg(8) - 0.15}
        y={790}
      />
      <Pegatina texto="% descuento" sub="en tus compras" t0={A.descuento.s} t1={finSeg(9) - 0.05} x={790} y={520} giro={-6} />
      <VisorREC t0={A.grabar.s - 0.6} t1={finSeg(11) - 0.05} />
      {/* logo de la agencia (enviado por la clienta) sobre las cabezas, entre las dos */}
      <LogoPlaca src="lote2/img/logo305.png" t0={A.agencia.s - 0.05} t1={finSeg(14) - 0.1} x={540} y={120} ancho={300} />
      <Tragamonedas t0={A.ganar.s - 1.25} t1={finSeg(15) - 0.05} x={790} y={420} />
      <Chip texto="Escríbeme al WhatsApp" t={A.whatsapp.s - 0.05} hasta={finSeg(19) - 0.05} x={540} y={360} color="#25D366" />
      {/* logo de WhatsApp en 3D a su lado (la cara de Chiqui está a la derecha del encuadre) */}
      <WhatsApp3D t0={A.whatsapp.s - 0.1} t1={finSeg(19) - 0.05} x={270} y={720} tam={280} />
      {/* "con que me acompañes al cafecito…": no es verdad → meme del chill guy tomando café (zona libre a la izquierda) */}
      <MemeRecorte src="lote2/memes/chillguy.webm" t0={A.cafe.s - 0.1} dur={finSeg(22) - A.cafe.s + 0.02} x={250} y={400} ancho={420} alto={445} giro={-3} bucle />

      <Subtitulos2 bloques={datos.bloques as B2[]} />

      <CierreFoto src="lote2/img/DSC09864.jpg" t={datos.duracionS} titulo="¿Te unes al equipo?" sub="Escríbeme al WhatsApp" />

      {/* sonido */}
      <Audio src={staticFile("lote2/edit/v1_voz.wav")} />
      <Audio src={staticFile("lote2/edit/v1_musica.wav")} volume={musica} />
      {SFX_MEME.map((s, i) => (
        <Sequence key={`m${i}`} from={Math.max(0, Math.round(s.t * fps))} durationInFrames={Math.round(3.3 * fps)}>
          <Audio src={staticFile(s.src)} volume={s.vol} />
        </Sequence>
      ))}
      {SFX.map((s, i) => (
        <Sequence key={i} from={Math.max(0, Math.round(s.t * fps))} durationInFrames={Math.round(2.2 * fps)}>
          <Audio src={staticFile(`sfx_sel/${s.src}`)} volume={s.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
