import { Audio, Video } from "@remotion/media";
import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  interpolate,
  Sequence,
  staticFile,
} from "remotion";
import { FONT_FACES, VIDEO } from "../brand";
import { CarasProvider, DatosCaras, useCaras, zonasEn } from "../rutinas/Caras";
import { Aviso } from "../rutinas/Graficos";
import { Lupa3D } from "../rutinas/Objetos3D";
import { Efecto } from "../rutinas/Rutina";
import { CLAMP, useT } from "../rutinas/util";
import { Camara3D } from "../dia2/Objetos3D";
import { Lista } from "../dia6/Graficos";
import { ajustar, Columnas, Elem, Lado, Limites } from "../dia6/Maqueta";
import caras from "./data/caras.json";
import edit from "./data/edit.json";
import {
  Camino21,
  Confeti,
  Escala,
  Evaluacion,
  Iris,
  LupaPiel,
  NoSi,
  Polaroids,
  TituloSubrayado,
} from "./Graficos";
import { Calendario3D, Crema3D, Pausa3D } from "./Objetos3D";
import { at, DURATION, TOTAL, WORDS } from "./timing";

// Reto de 21 días · Vídeo 8 "Evaluación del Día 10" (a cámara, scripts/dia8/preparar.py). Cada gráfico nace de su
// frase. Para no repetir los días anteriores: título que se revela con subrayado de pincel, transición en círculo,
// pasos de la evaluación que se van marcando, escala 1–5, polaroids de las fotos de control, lupa sobre fragmentos
// de piel, camino de 21 días con los días pendientes, tarjeta No/Sí, confeti y objetos 3D nuevos.

const S = {
  intro: 0,
  sensaciones: at("vuelve a calificar").start,
  fotos: at("vas a tomarte").start,
  piel: at("revisa si").start,
  seguir: at("de lo contrario").start,
  perfeccion: at("además recuerda").start,
  objetivos: at("y recuerda calificar").start,
};
const FIN = TOTAL + 1;

// ---------- Apoyos (fragmentos cortos, §10.16: entran en la palabra, con flash y obturador; sin títulos encima) ----
const FOTOS = [
  { src: "dia8/foto_frente.jpg", at: at("frente").start, etiqueta: "frente" },
  {
    src: "dia8/foto_costado.jpg",
    at: at("de costado").start,
    etiqueta: "costado",
  },
  {
    src: "dia8/foto_espalda.jpg",
    at: at("de espalda").start,
    etiqueta: "espalda",
  },
  {
    src: "dia8/foto_otro.jpg",
    at: at("otro costado").start,
    etiqueta: "otro costado",
  },
];
const FOTOS_FIN = S.piel - 0.05;
const PIEL1 = { desde: at("moretones").start, hasta: at("irritación").start };
const PIEL2 = { desde: at("irritación").start, hasta: at("y determina").start };
const RUTINA = {
  desde: at("puedes seguir").start,
  hasta: at("el resto").start,
};
// Intervalos en que manda un apoyo (sin títulos ni columnas encima)
const APOYOS = [
  { desde: FOTOS[0].at, hasta: FOTOS_FIN + 0.3 },
  { desde: PIEL1.desde, hasta: PIEL2.hasta },
  RUTINA,
];
const enApoyo = (t: number) => APOYOS.some((a) => t >= a.desde && t < a.hasta);

const Fragmento: React.FC<{ desde: number; hasta: number; src: string }> = ({
  desde,
  hasta,
  src,
}) => {
  const { fps } = useT();
  return (
    <Sequence
      from={Math.round(desde * fps)}
      durationInFrames={Math.max(1, Math.round((hasta - desde) * fps))}
      name={`Apoyo ${src}`}
    >
      <AbsoluteFill>
        <Video
          src={staticFile(src)}
          muted
          objectFit="cover"
          style={{ width: "100%", height: "100%" }}
        />
      </AbsoluteFill>
    </Sequence>
  );
};
const Flash: React.FC<{ en: number[] }> = ({ en }) => {
  const { frame, fps } = useT();
  const o = Math.max(
    0,
    ...en.map((t0) => {
      const d = frame - Math.round(t0 * fps);
      return d < 0 ? 0 : interpolate(d, [0, 1, 6], [0.85, 0.85, 0], CLAMP);
    }),
  );
  return o > 0 ? (
    <AbsoluteFill style={{ background: "#FFFFFF", opacity: o }} />
  ) : null;
};

// ---------- Cámara: zoom suave solo en frases clave dichas con la voz alta (§10.12) ----------
const FRASES_CLAVE = [
  "felicitaciones llegaste",
  "puedas adaptarte",
  "tus objetivos",
  "suspender el uso",
];
const ZOOMS = FRASES_CLAVE.map((f) => {
  const { start, end } = at(f);
  const db = Math.max(
    ...WORDS.filter((w) => w.start >= start && w.end <= end + 0.01).map(
      (w) => w.db ?? 0,
    ),
  );
  return { start, end: Math.min(end + 0.3, start + 2.2), db };
})
  .filter((z) => z.db >= 3.5 && !enApoyo(z.start) && !enApoyo(z.end))
  .sort((a, b) => b.db - a.db)
  .reduce<{ start: number; end: number; db: number }[]>(
    (acc, z) =>
      acc.some((o) => Math.abs(o.start - z.start) < 4) ? acc : [...acc, z],
    [],
  );
const Footage: React.FC = () => {
  const { frame, fps } = useT();
  const escala = ZOOMS.reduce((acc, z) => {
    const a = Math.round(z.start * fps);
    const b = Math.round(z.end * fps);
    const env = interpolate(frame, [a, a + 10, b, b + 15], [0, 1, 1, 0], {
      ...CLAMP,
      easing: Easing.inOut(Easing.cubic),
    });
    return Math.max(acc, 1 + 0.12 * env);
  }, 1);
  return (
    <AbsoluteFill
      style={{ transform: `scale(${escala})`, transformOrigin: "50% 40%" }}
    >
      {/* Audio ORIGINAL dentro del vídeo editado (scripts/dia8/preparar.py), sin recortes en Remotion */}
      <Video
        src={staticFile("dia8/editado.mp4")}
        objectFit="cover"
        style={{ width: "100%", height: "100%" }}
      />
    </AbsoluteFill>
  );
};

// ---------- Secciones ----------
const IZQ: Lado = "izq";
const DER: Lado = "der";
const LIM: Limites = {
  arriba: 240,
  abajo: 1500,
  bajoTitulo: true,
  bajoCabeza: true,
};
type Extra = {
  desde: number;
  hasta?: number;
  w?: number;
  h: number;
  escala?: number;
  lado?: Lado;
  el: (pos: React.CSSProperties) => React.ReactNode;
};
type Seccion = {
  nombre: string;
  desde: number;
  hasta: number;
  titulo?: { kicker: string; texto: string; at?: number };
  paso: number; // paso de la evaluación que se está haciendo
  marca?: number;
  extras: Extra[];
};
const obj3d = (
  t0: number,
  el: (pos: React.CSSProperties) => React.ReactNode,
  hasta?: number,
  lado: Lado = DER,
  h = 300,
): Extra => ({
  desde: t0,
  hasta,
  w: 300,
  h,
  escala: 1,
  lado,
  el,
});
const aviso = (
  t0: number,
  texto: string,
  tipo: "si" | "no" = "si",
  hasta?: number,
  lado: Lado = DER,
): Extra => ({
  desde: t0,
  hasta,
  h: 110,
  escala: 0.92,
  lado,
  el: (pos) => <Aviso at={t0} tipo={tipo} texto={texto} style={pos} />,
});

const SECCIONES: Seccion[] = [
  // "Felicitaciones, llegaste al día 10 y antes de continuar vamos a revisar cómo se ha sentido tu cuerpo con la
  // rutina de los últimos días." (cuadro: "Marca el Día 10 en el calendario")
  {
    nombre: "Intro",
    desde: S.intro,
    hasta: S.sensaciones,
    titulo: {
      kicker: "¡FELICITACIONES!",
      texto: "día 10",
      at: at("día 10").start,
    },
    paso: -1,
    extras: [
      obj3d(
        0.2,
        (pos) => (
          <Calendario3D
            desde={0.2}
            diez={at("10").start}
            marca={at("10").end + 0.15}
            ancho={300}
            alto={320}
            style={pos}
          />
        ),
        undefined,
        DER,
        320,
      ),
      obj3d(
        at("revisar").start,
        (pos) => (
          <Lupa3D
            desde={at("revisar").start}
            ancho={300}
            alto={260}
            style={pos}
          />
        ),
        undefined,
        IZQ,
        260,
      ),
    ],
  },
  // "vuelve a calificar la sensación de pesadez, la suavidad de la piel o cómo sigues percibiendo la inflamación"
  {
    nombre: "Sensaciones",
    desde: S.sensaciones,
    hasta: S.fotos,
    titulo: { kicker: "ESCALA DEL 1 AL 5", texto: "vuelve a calificar" },
    paso: 0,
    marca: at("cuerpo", S.sensaciones).start,
    extras: [
      {
        desde: at("pesadez").start - 0.3,
        w: 280,
        h: 330,
        escala: 0.95,
        lado: DER,
        el: (pos) => (
          <Escala
            filas={[
              { texto: "Pesadez", at: at("pesadez").start },
              { texto: "Suavidad de la piel", at: at("suavidad").start },
              { texto: "Inflamación", at: at("inflamación").start },
            ]}
            style={pos}
          />
        ),
      },
    ],
  },
  // "vas a tomarte las mismas fotografías que el día número uno, de frente, de costado, de espalda y luego del otro
  // costado" (cuadro: "con la misma ropa, luz, distancia y postura del Día 1")
  {
    nombre: "Fotos",
    desde: S.fotos,
    hasta: S.piel,
    titulo: { kicker: "COMO EL DÍA 1", texto: "mismas fotos" },
    paso: 1,
    extras: [
      obj3d(
        at("fotografías").start,
        (pos) => (
          <Camara3D
            desde={at("fotografías").start}
            disparo={FOTOS[0].at - 0.15}
            ancho={300}
            alto={300}
            style={pos}
          />
        ),
        undefined,
        DER,
      ),
      {
        desde: at("número uno").start - 0.2,
        w: 300,
        h: 250,
        escala: 0.9,
        lado: IZQ,
        el: (pos) => (
          <Lista
            at={at("número uno").start - 0.2}
            titulo="IGUAL QUE EL DÍA 1"
            filas={[
              { texto: "Misma ropa", at: at("número uno").start },
              { texto: "Misma luz", at: at("número uno").start + 0.25 },
              { texto: "Misma distancia", at: at("número uno").start + 0.5 },
              { texto: "Misma postura", at: at("número uno").start + 0.75 },
            ]}
            style={pos}
          />
        ),
      },
    ],
  },
  // "revisa si aparecieron moretones, irritación y determina si es necesario suspender el uso del aceite y cambiarlo
  // por otro o por una crema más suave"
  {
    nombre: "Piel",
    desde: S.piel,
    hasta: S.seguir,
    titulo: { kicker: "MORETONES · IRRITACIÓN", texto: "revisa tu piel" },
    paso: 2,
    extras: [
      obj3d(
        at("suspender").start - 0.2,
        (pos) => (
          <Pausa3D
            desde={at("suspender").start - 0.2}
            pulsa={at("suspender").start}
            ancho={300}
            alto={260}
            style={pos}
          />
        ),
        at("o por una").start,
        DER,
        260,
      ),
      aviso(
        at("suspender").start,
        "Si es necesario, suspende",
        "si",
        undefined,
        IZQ,
      ),
      obj3d(
        at("o por una").start,
        (pos) => (
          <Crema3D
            desde={at("o por una").start}
            abre={at("crema").start}
            ancho={300}
            alto={300}
            style={pos}
          />
        ),
        undefined,
        DER,
      ),
    ],
  },
  // "de lo contrario puedes seguir con la rutina el resto de estos 10 días" (cuadro: "Muestra los días pendientes")
  {
    nombre: "Seguir",
    desde: S.seguir,
    hasta: S.perfeccion,
    paso: 2,
    marca: S.seguir,
    extras: [
      {
        desde: RUTINA.hasta,
        w: 300,
        h: 290,
        escala: 0.95,
        lado: DER,
        el: (pos) => <Camino21 at={RUTINA.hasta} style={pos} />,
      },
    ],
  },
  // "Además recuerda: no estamos buscando perfección ni los cambios en el menor tiempo posible, estamos buscando que
  // tú puedas adaptarte a una rutina."
  {
    nombre: "Perfección",
    desde: S.perfeccion,
    hasta: S.objetivos,
    titulo: {
      kicker: "SIN PRISA",
      texto: "adaptarte",
      at: at("adaptarte").start,
    },
    paso: 3,
    extras: [
      {
        desde: at("perfección").start - 0.2,
        w: 280,
        h: 300,
        escala: 0.95,
        lado: DER,
        el: (pos) => (
          <NoSi
            no={[
              { texto: "Perfección", at: at("perfección").start },
              { texto: "Cambios rápidos", at: at("menor tiempo").start },
            ]}
            si={{ texto: "Adaptarte a una rutina", at: at("adaptarte").start }}
            style={pos}
          />
        ),
      },
    ],
  },
  // "Y recuerda calificar tus objetivos según la constancia y un mejor manejo del producto, además de las mejores
  // sensaciones que vas teniendo en tu cuerpo."
  {
    nombre: "Objetivos",
    desde: S.objetivos,
    hasta: FIN,
    titulo: {
      kicker: "CALIFICA",
      texto: "tus objetivos",
      at: at("objetivos").start,
    },
    paso: 3,
    marca: at("sensaciones", S.objetivos).end,
    extras: [
      {
        desde: at("según").start,
        w: 300,
        h: 250,
        escala: 0.92,
        lado: DER,
        el: (pos) => (
          <Lista
            at={at("según").start}
            titulo="SEGÚN"
            filas={[
              { texto: "La constancia", at: at("constancia").start },
              { texto: "Manejo del producto", at: at("manejo").start },
              {
                texto: "Tus sensaciones",
                at: at("sensaciones", S.objetivos).start,
              },
            ]}
            style={pos}
          />
        ),
      },
    ],
  },
];

const useElementos = (s: Seccion): Elem[] => {
  const caras = useCaras();
  const { t } = useT();
  const { actual } = zonasEn(caras, t, s.desde, s.hasta);
  const t0 = s.nombre === "Intro" ? at("revisar").start + 0.6 : s.desde + 0.2;
  const lista: Elem[] = [];
  if (t >= t0)
    lista.push({
      w: 260,
      h: 230,
      escala: 0.9,
      lado: IZQ,
      render: (st) => (
        <Evaluacion at={t0} paso={s.paso} marca={s.marca} style={st} />
      ),
    });
  for (const e of s.extras)
    if (t >= e.desde - 0.05 && t < (e.hasta ?? s.hasta))
      lista.push({
        w: e.w ?? 260,
        h: e.h,
        escala: e.escala,
        lado: e.lado,
        render: e.el,
      });
  return ajustar(actual, [], lista, LIM);
};

const SeccionComp: React.FC<{ s: Seccion }> = ({ s }) => {
  const elementos = useElementos(s);
  return (
    <>
      {s.titulo ? (
        <TituloSubrayado
          desde={s.desde}
          hasta={s.hasta}
          kicker={s.titulo.kicker}
          texto={s.titulo.texto}
          textoAt={s.titulo.at}
        />
      ) : null}
      <Columnas
        desde={s.desde}
        hasta={s.hasta}
        elementos={elementos}
        lim={LIM}
      />
    </>
  );
};

const Beats: React.FC = () => {
  const { t } = useT();
  const apoyo = enApoyo(t);
  return (
    <>
      {SECCIONES.filter((b) => t >= b.desde && t < b.hasta).map((b) => {
        const salida = Math.min(1, Math.max(0, (b.hasta - t) / 0.2));
        return (
          <div
            key={b.nombre}
            style={{
              position: "absolute",
              inset: 0,
              opacity: apoyo ? 0 : salida,
            }}
          >
            <SeccionComp s={b} />
          </div>
        );
      })}
    </>
  );
};

// ---------- Sonido ----------
const ANTES = { whoosh: 0.35, swish: 0.18, subida: 0.85 } as const;
const TRANSICIONES = [
  S.sensaciones,
  S.fotos,
  S.piel,
  S.perfeccion,
  S.objetivos,
];
const EFECTOS: Efecto[] = [
  {
    nombre: "felicitaciones · campanita",
    t: at("felicitaciones").start + 0.1,
    src: "campanita",
    vol: 0.2,
  },
  {
    nombre: "día 10 · blips",
    t: at("10").start - 0.66,
    src: "blips",
    vol: 0.2,
    dur: 0.8,
  },
  {
    nombre: "día 10 · impacto",
    t: at("10").end + 0.15,
    src: "impacto",
    vol: 0.22,
  },
  {
    nombre: "revisar · swish",
    t: at("revisar").start - ANTES.swish,
    src: "swish",
    vol: 0.2,
  },
  ...TRANSICIONES.map((tr, i) => ({
    nombre: `iris ${i} · whoosh`,
    t: tr - 0.25,
    src: "whoosh",
    vol: 0.24,
  })),
  { nombre: "pesadez · pop", t: at("pesadez").start, src: "pop", vol: 0.2 },
  { nombre: "suavidad · pop", t: at("suavidad").start, src: "pop", vol: 0.2 },
  {
    nombre: "inflamación · pop",
    t: at("inflamación").start,
    src: "pop",
    vol: 0.2,
  },
  {
    nombre: "día 1 · tecleo",
    t: at("número uno").start,
    src: "tecleo",
    vol: 0.14,
    dur: 1.0,
  },
  ...FOTOS.map((f, i) => ({
    nombre: `foto ${i} · obturador`,
    t: f.at,
    src: "obturador",
    vol: 0.32,
  })),
  { nombre: "moretones · tarjeta", t: PIEL1.desde, src: "tarjeta", vol: 0.22 },
  { nombre: "irritación · tarjeta", t: PIEL2.desde, src: "tarjeta", vol: 0.22 },
  {
    nombre: "suspender · tachado",
    t: at("suspender").start + 0.15,
    src: "tachado",
    vol: 0.2,
  },
  { nombre: "crema · brillo", t: at("crema").start, src: "brillo", vol: 0.2 },
  {
    nombre: "seguir · swish",
    t: RUTINA.desde - ANTES.swish,
    src: "swish",
    vol: 0.22,
  },
  {
    nombre: "camino · escalones",
    t: RUTINA.hasta + 0.1,
    src: "escalones",
    vol: 0.2,
  },
  {
    nombre: "perfección · tachado",
    t: at("perfección").start + 0.2,
    src: "tachado",
    vol: 0.2,
  },
  {
    nombre: "rápidos · tachado",
    t: at("menor tiempo").start + 0.2,
    src: "tachado",
    vol: 0.18,
  },
  {
    nombre: "adaptarte · brillo",
    t: at("adaptarte").start,
    src: "brillo",
    vol: 0.2,
  },
  {
    nombre: "constancia · pop",
    t: at("constancia").start,
    src: "pop",
    vol: 0.2,
  },
  { nombre: "manejo · pop", t: at("manejo").start, src: "pop", vol: 0.2 },
  {
    nombre: "sensaciones · campanita",
    t: at("sensaciones", S.objetivos).start,
    src: "campanita",
    vol: 0.18,
  },
];
// La voz del día 8 está a −29 LUFS (≈ 13 dB por debajo de la del día 1) y no se normaliza (§10.5):
// música y efectos bajan lo mismo para mantener la mezcla de marca.
const NIVEL = 0.25;
const FIN_VOZ = WORDS[WORDS.length - 1].end;

export const Dia8Video: React.FC = () => {
  const { fps } = useT();
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <style>{FONT_FACES}</style>
      <Footage />
      <Fragmento {...PIEL1} src="dia8/apoyo_piel1.mp4" />
      <Fragmento {...PIEL2} src="dia8/apoyo_piel2.mp4" />
      <Fragmento {...RUTINA} src="dia8/apoyo_rutina.mp4" />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(69,89,90,.5) 0%, rgba(69,89,90,.25) 18%, rgba(69,89,90,0) 30%)",
        }}
      />
      <CarasProvider
        datos={{
          ...(caras as DatosCaras),
          cortes: edit.segments.map((s) => s.outStart),
        }}
      >
        <Beats />
      </CarasProvider>
      <Confeti at={at("felicitaciones").start + 0.1} x={540} y={420} />
      <LupaPiel {...PIEL1} etiqueta="¿Moretones?" />
      <LupaPiel {...PIEL2} etiqueta="¿Irritación?" />
      <LupaPielRutina />
      <Polaroids fotos={FOTOS} hasta={FOTOS_FIN} />
      <Flash en={[PIEL1.desde, PIEL2.desde, RUTINA.desde]} />
      <Iris en={TRANSICIONES} />
      <Audio
        src={staticFile("dia8/audio/musica.wav")}
        volume={(f) =>
          interpolate(
            f / fps,
            [FIN_VOZ, FIN_VOZ + 0.4],
            [0.1 * NIVEL, 0.2 * NIVEL],
            CLAMP,
          )
        }
      />
      {EFECTOS.map((e) => (
        <Sequence
          key={e.nombre}
          name={`SFX ${e.nombre}`}
          from={Math.max(0, Math.round(e.t * fps))}
          durationInFrames={Math.max(1, Math.round((e.dur ?? 2.5) * fps))}
        >
          <Audio
            src={staticFile(`dia8/audio/${e.src}.wav`)}
            volume={e.vol * NIVEL}
          />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

// Etiqueta del fragmento de la rutina ("puedes seguir con la rutina")
const LupaPielRutina: React.FC = () => {
  const { t } = useT();
  if (t < RUTINA.desde || t >= RUTINA.hasta) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 1440,
        display: "flex",
        justifyContent: "center",
      }}
    >
      <Aviso
        at={RUTINA.desde}
        texto="Sigue con tu rutina"
        ancho={430}
        style={{ position: "relative" }}
      />
    </div>
  );
};

export const Dia8 = () => (
  <Composition
    id="Dia8"
    component={Dia8Video}
    durationInFrames={Math.ceil(TOTAL * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);

export { DURATION };
