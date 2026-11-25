import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, staticFile, useVideoConfig } from "remotion";
import "./fuentes";
import datos from "./datos/v1.json";
import { Subtitulos2, B2 } from "./Subtitulos2";
import { ARollL2, CadenaIconos, CierreFoto, DegradadoTexto, EmojiPop, Segmento, TarjetaFoto, Chip } from "./Piezas";

// Vídeo 1 del lote 2 · sketch "Bienvenida al equipo" (Chiqui y Gordi)
const A = datos.anclas as Record<string, { s: number; e: number; seg: number }>;
const SEG = datos.segmentos as Segmento[];
const finSeg = (i: number) => SEG[i].editStart + SEG[i].dur;
export const V1_CIERRE = 2.7; // tarjeta final
export const V1_DURACION = datos.duracionS + V1_CIERRE;

const GOLPES = [
  { t: A.chiste.s, fuerza: 0.12, dur: 0.7 },
  { t: A.abuela.s, fuerza: 0.06, dur: 0.6 },
  { t: A.conservada.s - 0.1, fuerza: 0.1, dur: 0.8 },
  { t: A.gym.s, fuerza: 0.09, dur: 0.9 },
];

type Sfx = { t: number; src: string; vol: number };
const SFX: Sfx[] = [
  { t: A.chiste.s - 0.05, src: "whip.wav", vol: 0.28 },
  { t: A.abuela.s, src: "pop.wav", vol: 0.32 },
  { t: A.conservada.s + 0.05, src: "chasquido.wav", vol: 0.4 },
  { t: A.turquia.s - 0.08, src: "swoosh_4.wav", vol: 0.22 },
  { t: A.maquillaje.s - 0.06, src: "swoosh_6.wav", vol: 0.22 },
  { t: A.skincare.s - 0.06, src: "swoosh_7.wav", vol: 0.2 },
  { t: A.cabello.s - 0.06, src: "swoosh_6.wav", vol: 0.2 },
  { t: A.nutriplus.s - 0.06, src: "swoosh_std.wav", vol: 0.22 },
  { t: A.redes.s, src: "pop.wav", vol: 0.26 },
  { t: A.link.s, src: "pop.wav", vol: 0.26 },
  { t: A.compra.s, src: "pop.wav", vol: 0.26 },
  { t: A.casa.s, src: "pop.wav", vol: 0.26 },
  { t: A.descuento.s, src: "pop.wav", vol: 0.3 },
  { t: A.grabar.s, src: "pop.wav", vol: 0.3 },
  { t: A.ganar.s, src: "contador.wav", vol: 0.2 },
  { t: A.sola.s, src: "pop.wav", vol: 0.28 },
  { t: A.encanta.s, src: "pop.wav", vol: 0.28 },
  { t: A.whatsapp.s, src: "notif.wav", vol: 0.3 },
  { t: A.ultima.s - 0.35, src: "whoosh_2.wav", vol: 0.22 },
  { t: A.gym.s - 0.03, src: "whip.wav", vol: 0.26 },
  { t: SEG[22].editStart + 0.02, src: "error.wav", vol: 0.16 },
  { t: A.cafe.s, src: "pop.wav", vol: 0.3 },
  { t: A.final.s, src: "acierto.wav", vol: 0.22 },
  { t: datos.duracionS - 0.15, src: "swoosh_std.wav", vol: 0.25 },
];

export const V1: React.FC = () => {
  const { fps } = useVideoConfig();
  const total = V1_DURACION;
  const musica = (f: number) => {
    const t = f / fps;
    return interpolate(t, [0, 0.4, datos.duracionS - 0.4, datos.duracionS + 0.3, total - 0.9, total], [0, 0.085, 0.085, 0.2, 0.2, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  };
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <ARollL2 src="lote2/edit/v1_aroll.mp4" segmentos={SEG} golpes={GOLPES} />
      <DegradadoTexto />

      {/* apoyo visual */}
      <EmojiPop icono="pensando" t={A.pregunta.s - 0.2} hasta={A.pregunta.e + 0.5} x={330} y={560} tam={140} />
      <TarjetaFoto src="lote2/img/turquia.jpg" t={A.turquia.s - 0.1} hasta={finSeg(2) - 0.15} x={300} y={640} w={400} h={500} giro={-3} />
      <EmojiPop icono="abuela" t={A.abuela.s} hasta={finSeg(3) + 0.2} x={760} y={620} tam={190} giro={10} />
      <TarjetaFoto src="lote2/img/maquillaje.jpg" t={A.maquillaje.s - 0.1} hasta={A.skincare.s - 0.08} x={540} y={640} w={420} h={520} giro={-2} />
      <TarjetaFoto src="lote2/img/skincare.jpg" t={A.skincare.s - 0.1} hasta={A.cabello.s - 0.08} x={540} y={640} w={420} h={520} giro={2} />
      <TarjetaFoto src="lote2/img/cabello.jpg" t={A.cabello.s - 0.1} hasta={A.nutriplus.s - 0.08} x={540} y={640} w={420} h={520} giro={-2} />
      <TarjetaFoto src="lote2/img/nutriplus.jpg" t={A.nutriplus.s - 0.1} hasta={finSeg(5) - 0.2} x={540} y={640} w={420} h={520} giro={2} foco="50% 40%" />
      <EmojiPop icono="mono" t={A.influencer.s - 0.15} hasta={finSeg(6)} x={330} y={600} tam={150} />
      <CadenaIconos
        pasos={[
          { icono: "celular", t: A.redes.s },
          { icono: "enlace", t: A.link.s },
          { icono: "bolsas", t: A.compra.s },
          { icono: "casa", t: A.casa.s },
        ]}
        hasta={finSeg(8) - 0.15}
        y={560}
      />
      <EmojiPop icono="etiqueta" t={A.descuento.s} hasta={finSeg(9)} x={760} y={620} tam={160} giro={12} />
      <EmojiPop icono="dinero" t={A.bille.s} hasta={finSeg(10) - 0.05} x={300} y={600} tam={160} />
      <EmojiPop icono="claqueta" t={A.grabar.s} hasta={finSeg(11)} x={760} y={620} tam={160} giro={10} />
      <EmojiPop icono="estrellas" t={A.agencia.s + 0.1} hasta={finSeg(13) - 0.1} x={540} y={560} tam={150} />
      <EmojiPop icono="billetes" t={A.ganar.s} hasta={finSeg(15)} x={760} y={620} tam={170} giro={10} />
      <EmojiPop icono="manos" t={A.sola.s} hasta={finSeg(17) - 0.05} x={540} y={600} tam={170} />
      <EmojiPop icono="corazon_lila" t={A.encanta.s} hasta={finSeg(18)} x={760} y={600} tam={160} giro={10} />
      <Chip texto="Escríbeme al WhatsApp" icono="globo" t={A.whatsapp.s - 0.05} hasta={finSeg(19) - 0.05} x={540} y={430} color="#25D366" />
      <EmojiPop icono="pesas" t={A.gym.s} hasta={finSeg(21)} x={760} y={600} tam={180} giro={10} />
      <EmojiPop icono="cafe" t={A.cafe.s} hasta={finSeg(22) - 0.05} x={300} y={600} tam={170} />

      <Subtitulos2 bloques={datos.bloques as B2[]} />

      <CierreFoto src="lote2/img/DSC09864.jpg" t={datos.duracionS} titulo="¿Te unes al equipo?" sub="Escríbeme al WhatsApp" icono="globo" />

      {/* sonido */}
      <Audio src={staticFile("lote2/edit/v1_voz.wav")} />
      <Audio src={staticFile("lote2/edit/v1_musica.wav")} volume={musica} />
      {SFX.map((s, i) => (
        <Sequence key={i} from={Math.max(0, Math.round(s.t * fps))} durationInFrames={Math.round(2.2 * fps)}>
          <Audio src={staticFile(`sfx_sel/${s.src}`)} volume={s.vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
