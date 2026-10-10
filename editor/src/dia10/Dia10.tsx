import { Audio, Video } from "@remotion/media";
import React from "react";
import { AbsoluteFill, Composition, Easing, interpolate, Sequence, staticFile } from "remotion";
import { FONT_FACES, VIDEO } from "../brand";
import { CarasProvider, DatosCaras } from "../rutinas/Caras";
import { Aceite3D } from "../rutinas/Objetos3D";
import { Efecto } from "../rutinas/Rutina";
import { CLAMP, useT } from "../rutinas/util";
import { Elem, Lado } from "../dia6/Maqueta";
import { useCaras, zonasEn } from "../rutinas/Caras";
import caras from "./data/caras.json";
import edit from "./data/edit.json";
import rutina from "./data/rutina.json";
import {
  Anillo21,
  Brillo,
  CamaraMovil,
  Comparar,
  Etiqueta,
  Ficha,
  Foto,
  Mensaje,
  Montaje,
  Panel,
  PANEL_ANCHO,
  Registro,
  TituloArriba,
  Ventana21,
} from "./Graficos";
import { ajustar10, Columnas10 } from "./Maqueta10";
import { Celular3D, CintaManiqui3D, Corazon3D, Dialogo3D, Espejo3D, Globos21, Semana3D } from "./Objetos3D";
import { at, DURATION, TOTAL, WORDS } from "./timing";

// Reto de 21 días · Vídeo 10 "Día 21 y continuidad" (el último; a cámara, scripts/dia10/preparar.py). Cada gráfico
// nace de su frase. Para no repetir los días anteriores: títulos pegatina, ventana con forma de 21 para abrir y cambiar
// de bloque, panel lateral (la toma se desliza) en medidas, comparación y continuidad, las 4 fotos en una cámara de
// móvil, montaje rápido de la rutina del día 9 como b-roll, mensajes de chat y 3D nuevos (globos 21, móvil en
// trípode, cinta métrica en el maniquí, corazón, semana, espejo y globo de diálogo).

const FIN = TOTAL + 1;
const IZQ: Lado = "izq";
const DER: Lado = "der";
const S = {
  intro: 0,
  registro: at("ahora vas").start,
  medidas: at("y si es").start,
  comparar: at("compara").start,
  montaje: at("debes").start,
  testimonio: at("ahora cuéntanos").start,
  final: at("hacer de su").start,
};

// ---------- Fotos (cámara de móvil) y montaje de la rutina ----------
const FOTOS: Foto[] = [
  { src: "dia8/foto_frente.jpg", at: at("frente").start, pose: "frente" },
  { src: "dia8/foto_costado.jpg", at: at("de costado").start + 0.12, pose: "costado" },
  { src: "dia8/foto_espalda.jpg", at: at("de espalda").start + 0.08, pose: "espalda" },
  { src: "dia8/foto_otro.jpg", at: at("otro costado").start, pose: "otro costado" },
];
const FOTOS_FIN = S.medidas;
const MONTAJE_FIN = S.montaje + rutina.reduce((a, f) => a + f.frames, 0) / VIDEO.fps;

// ---------- Paneles laterales: la toma se desliza 190 px y entra un panel Marfil ----------
type PanelDef = { lado: "izq" | "der"; desde: number; hasta: number; kicker: string; titulo: string };
const PANELES: PanelDef[] = [
  { lado: "der", desde: S.medidas, hasta: S.comparar, kicker: "SI LAS TOMASTE AL INICIO", titulo: "medidas" },
  { lado: "izq", desde: S.comparar, hasta: S.montaje + 0.3, kicker: "SIN FILTROS", titulo: "compara" },
  { lado: "der", desde: MONTAJE_FIN - 0.45, hasta: S.testimonio, kicker: "2 O 3 VECES POR SEMANA", titulo: "continuidad" },
];
const progresoPanel = (pn: PanelDef, t: number) =>
  interpolate(t, [pn.desde, pn.desde + 0.45, pn.hasta - 0.35, pn.hasta], [0, 1, 1, 0], {
    ...CLAMP,
    easing: Easing.inOut(Easing.cubic),
  });
const DESLIZA = PANEL_ANCHO / 2;
const desliz = (t: number) => PANELES.reduce((acc, pn) => acc + (pn.lado === "der" ? -1 : 1) * DESLIZA * progresoPanel(pn, t), 0);

// ---------- Cámara: zoom suave solo en frases clave dichas con la voz alta (§10.12) ----------
const enPanel = (t: number) => PANELES.some((pn) => t >= pn.desde - 0.2 && t < pn.hasta + 0.2);
const tapado = (t: number) => enPanel(t) || (t >= FOTOS[0].at - 0.3 && t < FOTOS_FIN) || (t >= S.montaje - 0.3 && t < MONTAJE_FIN);
const FRASES_CLAVE = ["felicitaciones llegaste", "un gran logro", "lo más importante", "tu experiencia puede motivar", "una rutina"];
const ZOOMS = FRASES_CLAVE.map((f) => {
  const { start, end } = at(f, f === "una rutina" ? 60 : 0);
  const db = Math.max(...WORDS.filter((w) => w.start >= start - 0.01 && w.end <= end + 0.01).map((w) => w.db ?? 0));
  return { start, end: Math.min(end + 0.3, start + 2.2), db };
})
  .filter((z) => z.db >= 3.5 && !tapado(z.start) && !tapado(z.end))
  .sort((a, b) => b.db - a.db)
  .reduce<{ start: number; end: number; db: number }[]>((acc, z) => (acc.some((o) => Math.abs(o.start - z.start) < 4) ? acc : [...acc, z]), []);
const OX = 540;
const OY = 760;
const zoomEn = (t: number) =>
  ZOOMS.reduce((acc, z) => {
    const env = interpolate(t, [z.start, z.start + 10 / 30, z.end, z.end + 15 / 30], [0, 1, 1, 0], {
      ...CLAMP,
      easing: Easing.inOut(Easing.cubic),
    });
    return Math.max(acc, 1 + 0.12 * env);
  }, 1);
/** La cara sigue a la toma: mismo zoom y mismo deslizamiento. */
const carasMovidas = (d: DatosCaras): DatosCaras => ({
  ...d,
  caras: d.caras.map((c) => {
    if (c[1] === null) return c;
    const t = (c[0] as number) / 30;
    const s = zoomEn(t);
    const dx = desliz(t);
    const [n, x, y, w, h] = c as number[];
    return [n, Math.round(OX + (x - OX) * s + dx), Math.round(OY + (y - OY) * s), Math.round(w * s), Math.round(h * s)];
  }),
});

// ---------- Bloques con columnas a los lados de la cara ----------
type Extra = {
  desde: number;
  hasta?: number;
  w?: number;
  h: number;
  escala?: number;
  lado?: Lado;
  el: (pos: React.CSSProperties) => React.ReactNode;
};
type Bloque = {
  nombre: string;
  desde: number;
  hasta: number;
  titulo?: { kicker: string; texto: string; at?: number; hasta?: number }[];
  extras: Extra[];
};
const obj = (t0: number, el: (pos: React.CSSProperties) => React.ReactNode, hasta?: number, lado: Lado = DER, h = 300, w = 280): Extra => ({
  desde: t0,
  hasta,
  w,
  h,
  escala: 1,
  lado,
  el,
});
const etiqueta = (t0: number, texto: string, icono: "si" | "no" | "ojo" | "corazon" = "si", hasta?: number, lado: Lado = IZQ, h = 110): Extra => ({
  desde: t0,
  hasta,
  w: 280,
  h,
  escala: 0.95,
  lado,
  el: (pos) => <Etiqueta at={t0} texto={texto} icono={icono} giro={lado === IZQ ? -2 : 2} style={pos} />,
});

const BLOQUES: Bloque[] = [
  // "¡Felicitaciones! Llegaste al día 21 y más allá de cualquier logro en cuanto a nuestra parte estética, pudiste
  // hacer de esto una rutina y ese ya es un gran logro." (cuadro: "Marca el Día 21 como completado")
  {
    nombre: "Celebración",
    desde: S.intro,
    hasta: S.registro,
    titulo: [{ kicker: "¡FELICITACIONES!", texto: "día 21", at: at("día 21").start }],
    extras: [
      obj(0.85, (pos) => <Globos21 desde={0.85} fiesta={at("gran logro").start} ancho={280} alto={300} style={pos} />),
      etiqueta(at("logro").start, "Más allá de lo estético", "corazon", at("pudiste").start),
      {
        desde: at("pudiste").start,
        w: 280,
        h: 350,
        lado: IZQ,
        el: (pos) => <Anillo21 at={at("pudiste").start} completo={at("rutina").end} style={pos} />,
      },
    ],
  },
  // "Ahora vas a volver a revisar tus medidas, te vas a tomar las fotos en las mismas posiciones y vas a empezar a
  // mirar cuáles fueron los cambios que tuviste a nivel corporal." (cuadro: "Repite las fotografías del Día 1")
  {
    nombre: "Registro",
    desde: S.registro,
    hasta: FOTOS[0].at,
    titulo: [{ kicker: "COMO EL DÍA 1", texto: "registro final" }],
    extras: [
      {
        desde: at("revisar").start,
        w: 280,
        h: 190,
        lado: IZQ,
        el: (pos) => (
          <Registro
            at={at("revisar").start}
            filas={[
              { texto: "Medidas", at: at("medidas").start },
              { texto: "Fotos", at: at("fotos").start },
            ]}
            style={pos}
          />
        ),
      },
      obj(at("fotos").start - 0.1, (pos) => (
        <Celular3D desde={at("fotos").start - 0.1} dispara={at("posiciones").start} ancho={280} alto={320} style={pos} />
      ), undefined, DER, 320),
      etiqueta(at("mismas").start, "Mismas posiciones que el Día 1", "si", undefined, DER, 120),
      etiqueta(at("cuáles").start, "Observa los cambios", "ojo"),
    ],
  },
  // "Ahora, cuéntanos vía WhatsApp cómo viste este reto, cuáles fueron tus resultados y recuerda que tu experiencia
  // puede motivar a otras mujeres a sentirse mejor y hacer de su cuidado corporal una rutina."
  {
    nombre: "Testimonio",
    desde: S.testimonio,
    hasta: FIN,
    titulo: [
      { kicker: "CUÉNTANOS", texto: "tu experiencia", hasta: S.final },
      { kicker: "TU CUIDADO CORPORAL", texto: "una rutina", at: at("cuidado").start },
    ],
    extras: [
      obj(at("cuéntanos").start, (pos) => <Dialogo3D desde={at("cuéntanos").start} ancho={280} alto={250} style={pos} />, at("motivar").start, IZQ, 250),
      { desde: at("cómo viste").start, hasta: at("motivar").start, w: 280, h: 100, lado: DER, el: (pos) => <Mensaje at={at("cómo viste").start} texto="¿Cómo viviste el reto?" style={pos} /> },
      { desde: at("resultados").start, hasta: at("motivar").start, w: 280, h: 100, lado: DER, el: (pos) => <Mensaje at={at("resultados").start} texto="¡Mis resultados fueron…!" propio style={pos} /> },
      { desde: at("recuerda que").start, hasta: at("motivar").start, w: 280, h: 70, lado: DER, el: (pos) => <Mensaje at={at("recuerda que").start} escribiendo style={pos} /> },
      obj(at("motivar").start, (pos) => (
        <Corazon3D desde={at("motivar").start} multiplica={at("otras mujeres").start} ancho={280} alto={280} style={pos} />
      ), at("cuidado").start, IZQ, 280),
      etiqueta(at("mujeres").start, "Tu experiencia motiva a otras mujeres", "corazon", at("cuidado").start, DER, 120),
      obj(at("cuidado").start, (pos) => (
        <Globos21 desde={at("cuidado").start} fiesta={at("rutina", S.final).start} ancho={280} alto={300} style={pos} />
      )),
    ],
  },
];

const useElementos = (b: Bloque): Elem[] => {
  const caras = useCaras();
  const { t } = useT();
  const { actual } = zonasEn(caras, t, b.desde, b.hasta);
  const lista: Elem[] = [];
  for (const e of b.extras)
    if (t >= e.desde - 0.05 && t < (e.hasta ?? b.hasta)) lista.push({ w: e.w ?? 280, h: e.h, escala: e.escala, lado: e.lado, render: e.el });
  return ajustar10(actual, [], lista);
};
const BloqueComp: React.FC<{ b: Bloque }> = ({ b }) => {
  const elementos = useElementos(b);
  return (
    <>
      {b.titulo?.map((ti, i) => (
        <TituloArriba
          key={ti.texto}
          desde={ti.at ?? (i === 0 ? b.desde : b.desde)}
          hasta={ti.hasta ?? b.hasta}
          at={ti.at}
          kicker={ti.kicker}
          texto={ti.texto}
        />
      ))}
      <Columnas10 desde={b.desde} hasta={b.hasta} elementos={elementos} />
    </>
  );
};

// ---------- Contenido de los paneles ----------
const ContenidoPanel: React.FC<{ i: number }> = ({ i }) => {
  if (i === 0)
    // "Y si es necesario, toma medidas, si fue que al principio las tomaste, y vuelve a revisar estas medidas para
    // saber qué tanto bajaste en esas medidas puntuales que necesitabas o qué más te importaba." (cuadro: "repítelas
    // sin apretar la cinta y utilizando exactamente los mismos puntos")
    return (
      <>
        <CintaManiqui3D
          desde={S.medidas + 0.3}
          cintura={at("toma medidas").start}
          cadera={at("vuelve").start}
          ancho={336}
          alto={340}
          style={{ left: 0, top: 0 }}
        />
        <Ficha
          at={at("principio").start}
          dia1={at("principio").start}
          dia21={at("vuelve").start}
          filas={[
            { texto: "Cintura", at: at("estas medidas").start },
            { texto: "Cadera", at: at("tanto").start },
            { texto: "Muslo", at: at("puntuales").start },
            { texto: "Lo que te importa", at: at("qué más").start },
          ]}
          style={{ position: "absolute", left: 0, right: 0, top: 350 }}
        />
        <Etiqueta at={at("puntuales").start} texto="Mismos puntos, sin apretar la cinta" icono="si" giro={-2} ancho={330} style={{ left: 3, top: 720 }} />
      </>
    );
  if (i === 1)
    // "Compara tus registros con los anteriores. Recuerda, no puedes frustrarte si los cambios no fueron lo que tú
    // esperabas" (cuadro: "Coloca las fotos lado a lado, sin alterar ni retocar")
    return (
      <>
        <Comparar at={S.comparar + 0.25} filtros={at("anteriores").start} style={{ position: "absolute", left: 6, right: 6, top: 0 }} />
        <Corazon3D desde={at("frustrarte").start} ancho={336} alto={300} style={{ left: 0, top: 380 }} />
        <Etiqueta at={at("esperabas").start} texto="No te frustres" icono="corazon" giro={2} ancho={300} style={{ left: 18, top: 700 }} />
      </>
    );
  // "aumentando la presión y sobre todo respetando las instrucciones del producto. Y lo más importante, revisando
  // cómo se va comportando tu piel y tu cuerpo." (cuadro: "calendario con dos o tres días señalados"; "respetando
  // siempre las indicaciones del producto y la respuesta de tu piel")
  return <ContenidoContinuidad />;
};
const ContenidoContinuidad: React.FC = () => {
  const { t } = useT();
  const prod = at("respetando").start;
  const piel = at("revisando").start;
  return (
    <>
      <Semana3D desde={MONTAJE_FIN - 0.2} marca={MONTAJE_FIN + 0.35} ancho={336} alto={240} style={{ left: 0, top: -20 }} />
      {t < piel ? (
        <>
          {/* Lienzo más grande que la columna: el frasco compartido (rutinas/Objetos3D) sale así a buen tamaño */}
          <Aceite3D desde={prod} vierte={at("instrucciones").start} ancho={460} alto={440} style={{ left: -62, top: 170 }} />
          <Etiqueta at={at("instrucciones").start} texto="Respeta las indicaciones del producto" icono="si" giro={-2} ancho={330} style={{ left: 3, top: 590 }} />
        </>
      ) : (
        <>
          <Espejo3D desde={piel} ancho={336} alto={330} style={{ left: 0, top: 230 }} />
          <Etiqueta at={at("piel", piel).start} texto="Observa tu piel y tu cuerpo" icono="ojo" giro={2} ancho={330} style={{ left: 3, top: 590 }} />
        </>
      )}
    </>
  );
};

const Paneles: React.FC = () => {
  const { t } = useT();
  return (
    <>
      {PANELES.map((pn, i) => {
        const p = progresoPanel(pn, t);
        if (p <= 0.001) return null;
        return (
          <Panel key={i} lado={pn.lado} p={p} kicker={pn.kicker} titulo={pn.titulo} at={pn.desde + 0.25}>
            <ContenidoPanel i={i} />
          </Panel>
        );
      })}
    </>
  );
};

const Escenario: React.FC = () => {
  const { t } = useT();
  return (
    <>
      {BLOQUES.filter((b) => t >= b.desde && t < b.hasta).map((b) => {
        const salida = Math.min(1, Math.max(0, (b.hasta - t) / 0.2));
        return (
          <div key={b.nombre} style={{ position: "absolute", inset: 0, opacity: salida }}>
            <BloqueComp b={b} />
          </div>
        );
      })}
    </>
  );
};

// ---------- Efectos (§10.14) ----------
const ef = (nombre: string, t: number, src: string, vol = 0.22, dur?: number): Efecto => ({ nombre, t, src, vol, dur });
const EFECTOS: Efecto[] = [
  ef("apertura 21 · whoosh", 0, "whoosh", 0.22),
  ef("día 21 · impacto", at("día 21").start, "impacto", 0.2),
  ef("globos · subida", 0.85, "subida", 0.14),
  ef("estético · pop", at("logro").start, "pop", 0.2),
  ef("anillo · escalones", at("pudiste").start + 0.2, "escalones", 0.18),
  ef("rutina · campanita", at("rutina").end, "campanita", 0.16),
  ef("gran logro · brillo", at("gran logro").start, "brillo", 0.2),
  ef("registro · whoosh", S.registro - 0.2, "whoosh", 0.22),
  ef("registro · tarjeta", at("revisar").start, "tarjeta", 0.2),
  ef("medidas · pop", at("medidas").start, "pop", 0.18),
  ef("fotos · pop", at("fotos").start, "pop", 0.18),
  ef("móvil · obturador", at("posiciones").start, "obturador", 0.22),
  ef("cambios · swish", at("cuáles").start, "swish", 0.18),
  ...FOTOS.map((f, i) => ef(`foto ${i + 1} · obturador`, f.at, "obturador", 0.26)),
  ef("panel medidas · whoosh", S.medidas, "whoosh", 0.22),
  ef("cinta · tecleo", at("toma medidas").start, "tecleo", 0.14, 0.8),
  ef("ficha · tarjeta", at("principio").start, "tarjeta", 0.2),
  ef("cadera · tecleo", at("vuelve").start, "tecleo", 0.14, 0.8),
  ef("puntos · pop", at("puntuales").start, "pop", 0.2),
  ef("panel compara · whoosh", S.comparar - 0.1, "whoosh", 0.22),
  ef("sin filtros · tachado", at("anteriores").start, "tachado", 0.2),
  ef("corazón · brillo", at("frustrarte").start, "brillo", 0.16),
  ef("montaje · obturador", S.montaje, "obturador", 0.24),
  ...rutina.slice(1).map((f, i) => ef(`montaje ${i + 1} · whoosh`, S.montaje + f.desde / 30 - 0.15, "whoosh", 0.16)),
  ef("panel continuidad · swish", MONTAJE_FIN - 0.4, "swish", 0.2),
  ef("semana · escalones", MONTAJE_FIN + 0.35, "escalones", 0.18),
  ef("producto · brillo", at("instrucciones").start, "brillo", 0.16),
  ef("espejo · swish", at("revisando").start, "swish", 0.18),
  ef("testimonio 21 · whoosh", S.testimonio - 0.3, "whoosh", 0.22),
  ef("diálogo · pop", at("cuéntanos").start, "pop", 0.2),
  ef("mensaje 1 · pop", at("cómo viste").start, "pop", 0.18),
  ef("mensaje 2 · pop", at("resultados").start, "pop", 0.18),
  ef("escribiendo · tecleo", at("recuerda que").start, "tecleo", 0.12, 1),
  ef("corazones · campanita", at("otras mujeres").start, "campanita", 0.14),
  ef("una rutina · impacto", at("cuidado").start, "impacto", 0.2),
  ef("fiesta · brillo", at("rutina", S.final).start, "brillo", 0.2),
];

// Voz original a −28,9 LUFS (como la del día 8): música y efectos bajan ≈ −13 dB, la voz no se toca.
const NIVEL = 0.22;
const FIN_VOZ = WORDS[WORDS.length - 1].end;

export const Dia10Video: React.FC = () => {
  const { t, fps } = useT();
  const s = zoomEn(t);
  const dx = desliz(t);
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <style>{FONT_FACES}</style>
      <AbsoluteFill style={{ transform: `translateX(${dx}px) scale(${s})`, transformOrigin: `${OX}px ${OY}px` }}>
        {/* Vídeo editado en VP9 sin audio (el Chromium del entorno no decodifica H.264): ver scripts/dia10/preparar.py */}
        <Video src={staticFile("dia10/editado_video.webm")} muted objectFit="cover" style={{ width: "100%", height: "100%" }} />
      </AbsoluteFill>
      {/* Velo Verde petróleo arriba: legibilidad del título sobre la pared clara */}
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(69,89,90,.32) 0%, rgba(69,89,90,.12) 14%, rgba(69,89,90,0) 24%)" }} />
      <CarasProvider datos={carasMovidas({ ...(caras as DatosCaras), cortes: edit.segments.map((sg) => sg.outStart) })}>
        <Escenario />
      </CarasProvider>
      <Paneles />
      <Montaje desde={S.montaje} fragmentos={rutina} etiqueta="DE AQUÍ EN ADELANTE" />
      <CamaraMovil fotos={FOTOS} hasta={FOTOS_FIN} />
      <Brillo en={[at("gran logro").start, at("rutina", S.final).start]} />
      <Ventana21 en={[{ t: 0 }, { t: S.registro, cierra: true }, { t: S.testimonio, cierra: true }]} />
      {/* Voz ORIGINAL, cortada a muestra exacta con los mismos tramos (preparar.py --solo-audio), sin recortes en Remotion */}
      <Audio src={staticFile("dia10/voz.wav")} />
      <Audio
        src={staticFile("dia10/audio/musica.wav")}
        volume={(f) => interpolate(f / fps, [FIN_VOZ, FIN_VOZ + 0.4], [0.1 * NIVEL, 0.2 * NIVEL], CLAMP)}
      />
      {EFECTOS.map((e) => (
        <Sequence key={e.nombre} name={`SFX ${e.nombre}`} from={Math.max(0, Math.round(e.t * fps))} durationInFrames={Math.max(1, Math.round((e.dur ?? 2.5) * fps))}>
          <Audio src={staticFile(`dia10/audio/${e.src}.wav`)} volume={e.vol * NIVEL} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const Dia10 = () => (
  <Composition
    id="Dia10"
    component={Dia10Video}
    durationInFrames={Math.ceil(TOTAL * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);

export { DURATION };
