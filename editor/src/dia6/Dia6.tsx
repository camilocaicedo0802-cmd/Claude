import React from "react";
import { Composition } from "remotion";
import { VIDEO } from "../brand";
import { DatosCaras, useCaras, zonasEn } from "../rutinas/Caras";
import {
  Aviso,
  ItemSubtitulo,
  lectura,
  Resumen,
  Subtitulo,
  Tiempo,
  Titulo,
} from "../rutinas/Graficos";
import {
  Aceite3D,
  Flecha3D,
  FlechaCirculo3D,
  Perilla3D,
} from "../rutinas/Objetos3D";
import { Efecto, Rutina } from "../rutinas/Rutina";
import { useT } from "../rutinas/util";
import caras from "./data/caras.json";
import clips from "./data/clips.json";
import { Lista } from "./Graficos";
import { ajustar, Columnas, Elem, Lado, Limites } from "./Maqueta";
import { MapaPiernas, Paso } from "./MapaPiernas";
import { at, DURATION, TOTAL, WORDS } from "./timing";

// Reto de 21 días · Vídeo 6 "Piernas y apariencia de la celulitis" (voz en off + tomas de apoyo del crudo).
// Cada tramo de la toma de apoyo coincide con la frase (scripts/rutinas/montar.py) y cada gráfico nace de su frase.
// Hilo conductor: el mapa de piernas y glúteos (MapaPiernas, 2D) enciende la zona que se trabaja y dibuja el movimiento.
// Corrección: el texto recurrente de las tarjetas y los avisos largos van como subtítulo grande abajo, solo el tiempo
// de lectura (como en los días 4 y 5); las tarjetas quedan con los minutos y la zona.

const ZONAS = {
  prep: 0,
  musloD: at("comenzamos").start,
  circD: at("continúa durante").start,
  musloI: at("ahora vamos a repetir").start,
  circI: at("y por otros").start,
  gluteos: at("para finalizar").start,
  cierre: at("terminamos").start,
};
const FIN = TOTAL + 1;

// "Aplica aceite generosamente en muslos y glúteos" → aparece el mapa con muslos y glúteos encendidos (gira para
// enseñarlos); en cada zona se enciende solo esa parte con su movimiento; al terminar, todo encendido (15 min completos).
const MUNECO_DESDE = at("muslos").start;
const PASOS: Paso[] = [
  { t: MUNECO_DESDE, zona: "todo" },
  { t: ZONAS.musloD, zona: "musloD", modo: "barridos" },
  { t: ZONAS.circD, zona: "musloD", modo: "circulos" },
  { t: ZONAS.musloI, zona: "musloI", modo: "barridos" },
  { t: ZONAS.circI, zona: "musloI", modo: "circulos" },
  { t: ZONAS.gluteos, zona: "gluteos", modo: "circulos" },
  { t: at("barridos de abajo").start, zona: "gluteos", modo: "barridos" },
  { t: ZONAS.cierre, zona: "todo" },
];
// "Evita pasar sobre la rodilla o la ingle" → cruces en la rodilla y la ingle hasta que cambia de movimiento
const EVITA: [number, number] = [at("evita").start, ZONAS.circD];

// Elemento que aparece en un instante (y opcionalmente desaparece): objeto 3D, aviso, tarjeta…
type Extra = {
  desde: number;
  hasta?: number;
  w?: number;
  h: number;
  lado?: Lado;
  escala?: number;
  el: (pos: React.CSSProperties) => React.ReactNode;
};
type Seccion = {
  nombre: string;
  desde: number;
  hasta: number;
  kicker: string;
  titulo: string;
  kickerAt?: number;
  tituloAt?: number;
  tiempo?: { minutos: number; zona: string };
  extras: Extra[];
  subs?: ItemSubtitulo[];
};

const IZQ: Lado = "izq";
const DER: Lado = "der";
// Frase larga → subtítulo grande abajo, el tiempo justo para leerla (§10, corrección de los días 4–6)
const sub = (
  frase: string,
  texto: string,
  tipo?: "si" | "no",
): ItemSubtitulo => ({
  desde: at(frase).start,
  hasta: at(frase).start + lectura(texto),
  texto,
  tipo,
});
const RECURRENTE =
  "Continúa este movimiento hasta completar el tiempo indicado";
// Las columnas no bajan hasta la franja del subtítulo (y ≥ 1420)
const LIM: Limites = { arriba: 240, abajo: 1400, bajoTitulo: true };
const aviso = (
  frase: string,
  texto: string,
  tipo: "si" | "no" = "si",
  hasta?: number,
  orden: Lado = DER,
  desdeSeg = 0,
): Extra => {
  const t0 = at(frase, desdeSeg).start;
  return {
    desde: t0,
    hasta,
    h: 110,
    escala: 0.9,
    lado: orden,
    el: (pos) => (
      <Aviso at={t0} tipo={tipo} texto={texto} tamano={30} style={pos} />
    ),
  };
};
const flecha = (t0: number, hasta?: number, orden: Lado = IZQ): Extra => ({
  desde: t0,
  hasta,
  h: 290,
  escala: 0.8,
  lado: orden,
  el: (pos) => (
    <Flecha3D desde={t0} dir="arriba" ancho={260} alto={290} style={pos} />
  ),
});
const circulo = (t0: number, hasta?: number, orden: Lado = IZQ): Extra => ({
  desde: t0,
  hasta,
  h: 280,
  escala: 0.8,
  lado: orden,
  el: (pos) => (
    <FlechaCirculo3D desde={t0} ancho={260} alto={280} style={pos} />
  ),
});
const perilla = (
  t0: number,
  niveles: [number, number][],
  orden: Lado = IZQ,
): Extra => ({
  desde: t0,
  h: 280,
  escala: 0.8,
  lado: orden,
  el: (pos) => (
    <Perilla3D
      desde={t0}
      niveles={niveles}
      ancho={260}
      alto={280}
      style={pos}
    />
  ),
});

const SECCIONES: Seccion[] = [
  // "Prepara la piel durante un minuto. Aplica aceite generosamente en muslos y glúteos. Hoy nos concentraremos en
  // las zonas donde suele notarse más la celulitis."
  {
    nombre: "Preparación",
    desde: ZONAS.prep,
    hasta: ZONAS.musloD,
    kicker: "PIERNAS Y CELULITIS · 15 MIN",
    titulo: "prepara la piel",
    kickerAt: 0,
    tituloAt: at("prepara").start,
    tiempo: { minutos: 1, zona: "Preparación" },
    extras: [
      {
        desde: at("aplica aceite").start,
        h: 320,
        escala: 0.8,
        lado: IZQ,
        el: (pos) => (
          <Aceite3D
            desde={at("aplica aceite").start}
            vierte={at("generosamente").start}
            ancho={260}
            alto={320}
            style={pos}
          />
        ),
      },
    ],
    subs: [sub("celulitis", "Las zonas donde más se nota la celulitis", "si")],
  },
  // "Comenzamos con tres minutos de barridos largos en el muslo derecho. Desliza desde encima de la rodilla hacia la
  // parte alta del muslo. Trabaja por líneas y evita pasar sobre la rodilla o la ingle."
  {
    nombre: "Muslo derecho · barridos",
    desde: ZONAS.musloD,
    hasta: ZONAS.circD,
    kicker: "BARRIDOS LARGOS",
    titulo: "muslo derecho",
    tiempo: { minutos: 3, zona: "Muslo derecho" },
    extras: [
      flecha(at("hacia la parte alta").start, at("evita").start),
      aviso("trabaja por líneas", "Trabaja por líneas"),
    ],
    subs: [sub("evita", "Evita pasar sobre la rodilla o la ingle", "no")],
  },
  // "Continúa durante dos minutos más con círculos amplios en el mismo muslo, sin detener el dispositivo en un solo
  // lugar. Haz círculos amplios, no pequeños ni agresivos. Recuerda verificar la intensidad… y si es necesario baja
  // la intensidad de succión."
  {
    nombre: "Muslo derecho · círculos",
    desde: ZONAS.circD,
    hasta: ZONAS.musloI,
    kicker: "MUSLO DERECHO",
    titulo: "círculos amplios",
    tiempo: { minutos: 2, zona: "Muslo derecho" },
    extras: [
      circulo(at("círculos amplios").start, at("recuerda verificar").start),
      // La perilla sube al "verificar la intensidad" y baja en "baja la intensidad de succión"
      perilla(at("recuerda verificar").start, [
        [at("recuerda verificar").start, 2],
        [at("intensidad").start, 3],
        [at("baja").start, 3],
        [at("baja").start + 0.8, 1],
      ]),
    ],
    subs: [
      sub("sin detener", "No dejes el dispositivo en un solo lugar", "no"),
      sub("no pequeños", "Círculos amplios: ni pequeños ni agresivos", "no"),
      sub("baja", "Si es necesario, baja la intensidad de succión", "si"),
    ],
  },
  // "Ahora vamos a repetir la misma secuencia en el muslo izquierdo. Deslizas desde encima de la rodilla hacia la
  // parte alta del muslo…"
  {
    nombre: "Muslo izquierdo · barridos",
    desde: ZONAS.musloI,
    hasta: ZONAS.circI,
    kicker: "MISMA SECUENCIA",
    titulo: "muslo izquierdo",
    tiempo: { minutos: 3, zona: "Muslo izquierdo" },
    extras: [flecha(at("hacia la parte alta", ZONAS.musloI).start)],
  },
  // "…y por otros dos minutos vamos a hacer movimientos amplios circulares."
  {
    nombre: "Muslo izquierdo · círculos",
    desde: ZONAS.circI,
    hasta: ZONAS.gluteos,
    kicker: "MUSLO IZQUIERDO",
    titulo: "círculos amplios",
    tiempo: { minutos: 2, zona: "Muslo izquierdo" },
    extras: [circulo(at("movimientos amplios").start)],
  },
  // "Para finalizar vamos a hacerlo con dos minutos en cada glúteo, el masaje debe sentirse firme pero nunca doloroso,
  // trabaja… con círculos amplios y barridos de abajo hacia arriba para ayudar con el levantamiento."
  {
    nombre: "Glúteos",
    desde: ZONAS.gluteos,
    hasta: ZONAS.cierre,
    kicker: "DOS MINUTOS EN CADA UNO",
    titulo: "glúteos",
    tiempo: { minutos: 2, zona: "Cada glúteo" },
    extras: [
      circulo(at("círculos amplios", 70).start, at("barridos de abajo").start),
      flecha(at("barridos de abajo").start),
    ],
    subs: [
      sub("firme", "Firme, pero nunca doloroso", "si"),
      sub("levantamiento", "Para ayudar con el levantamiento", "si"),
    ],
  },
  // "Terminamos los 15 minutos del día. Una mayor intensidad no significa mejores resultados, así que prioriza la
  // técnica, el movimiento y la constancia."
  {
    nombre: "Cierre",
    desde: ZONAS.cierre,
    hasta: FIN,
    kicker: "15 MINUTOS DEL DÍA",
    titulo: "terminamos",
    tituloAt: at("terminamos").start,
    extras: [
      {
        desde: at("15").start,
        hasta: at("prioriza").start,
        w: 280,
        h: 300,
        escala: 0.85,
        lado: IZQ,
        el: (pos) => (
          <Resumen
            at={at("15").start}
            filas={[
              { texto: "Preparación", min: 1 },
              { texto: "Muslo derecho", min: 5 },
              { texto: "Muslo izquierdo", min: 5 },
              { texto: "Glúteos", min: 4 },
            ]}
            style={pos}
          />
        ),
      },
      {
        desde: at("prioriza").start,
        w: 300,
        h: 250,
        escala: 0.85,
        lado: IZQ,
        el: (pos) => (
          <Lista
            at={at("prioriza").start}
            titulo="PRIORIZA"
            filas={[
              { texto: "La técnica", at: at("técnica").start },
              { texto: "El movimiento", at: at("movimiento").start },
              { texto: "La constancia", at: at("constancia").start },
            ]}
            style={pos}
          />
        ),
      },
      // "Una mayor intensidad no significa mejores resultados" → la perilla baja del máximo
      perilla(
        at("una mayor").start,
        [
          [at("una mayor").start, 5],
          [at("no significa").start, 5],
          [at("no significa").start + 0.8, 2],
        ],
        DER,
      ),
    ],
    subs: [
      sub(
        "no significa",
        "Más intensidad no significa mejores resultados",
        "no",
      ),
    ],
  },
];

// Columnas laterales de una sección en el instante t: el mapa 3D primero (es el hilo conductor), luego la tarjeta de
// tiempo y los extras activos en el orden en que se dicen. Si no caben, se retira lo más antiguo (la tarjeta de
// tiempo incluida), nunca lo último que se ha dicho.
const useElementos = (s: Seccion): Elem[] => {
  const caras = useCaras();
  const { t } = useT();
  const { actual } = zonasEn(caras, t, s.desde, s.hasta);
  const muneco: Elem = {
    w: 240,
    h: 400,
    lado: DER,
    render: (style) => (
      <MapaPiernas
        desde={MUNECO_DESDE}
        pasos={PASOS}
        evita={EVITA}
        style={style}
      />
    ),
  };
  const tiempo: Elem[] = s.tiempo
    ? [
        {
          w: 260,
          h: 310,
          escala: 0.85,
          lado: IZQ,
          render: (style) => (
            <Tiempo
              desde={s.desde}
              hasta={s.hasta}
              minutos={s.tiempo!.minutos}
              zona={s.tiempo!.zona}
              recordatorio={false}
              etiquetaGrande
              style={style}
            />
          ),
        },
      ]
    : [];
  const extras: Elem[] = s.extras
    .filter((e) => t >= e.desde - 0.05 && t < (e.hasta ?? s.hasta))
    .map((e) => ({
      w: e.w ?? 260,
      h: e.h,
      escala: e.escala,
      lado: e.lado,
      render: e.el,
    }));
  return ajustar(actual, [muneco], [...tiempo, ...extras], LIM);
};

const SeccionComp: React.FC<{ s: Seccion }> = ({ s }) => {
  const elementos = useElementos(s);
  return (
    <>
      <Titulo
        desde={s.desde}
        hasta={s.hasta}
        kicker={s.kicker}
        kickerAt={s.kickerAt}
        texto={s.titulo}
        textoAt={s.tituloAt}
      />
      <Columnas
        desde={s.desde}
        hasta={s.hasta}
        elementos={elementos}
        dibujar={(i) => i > 0}
        lim={LIM}
      />
    </>
  );
};

const Beats: React.FC = () => {
  const { t } = useT();
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
              opacity: salida,
              transform: `translateY(${(1 - salida) * -20}px)`,
            }}
          >
            <SeccionComp s={b} />
          </div>
        );
      })}
    </>
  );
};

// El mapa 3D va fuera de las secciones: es el mismo objeto todo el vídeo (no se vuelve a montar en cada zona) y se
// coloca con la misma maqueta que la sección activa.
const MunecoSeccion: React.FC<{ s: Seccion }> = ({ s }) => (
  <Columnas
    desde={s.desde}
    hasta={s.hasta}
    elementos={useElementos(s)}
    dibujar={(i) => i === 0}
    lim={LIM}
  />
);
const Muneco: React.FC = () => {
  const { t } = useT();
  const s = SECCIONES.find((b) => t >= b.desde && t < b.hasta);
  return s ? <MunecoSeccion s={s} /> : null;
};

const ANTES = { whoosh: 0.35, swish: 0.18, subida: 0.85 } as const;
const EFECTOS: Efecto[] = [
  {
    nombre: "prep · whoosh",
    t: at("prepara").start - ANTES.whoosh,
    src: "whoosh",
    vol: 0.26,
  },
  { nombre: "aceite · brillo", t: at("aceite").start, src: "brillo", vol: 0.2 },
  {
    nombre: "mapa · swish",
    t: MUNECO_DESDE - ANTES.swish,
    src: "swish",
    vol: 0.2,
  },
  {
    nombre: "celulitis · pop",
    t: at("celulitis").start,
    src: "pop",
    vol: 0.22,
  },
  ...[ZONAS.musloD, ZONAS.circD, ZONAS.musloI, ZONAS.circI, ZONAS.gluteos].map(
    (z, i) => ({
      nombre: `zona ${i} · tictac`,
      t: z + 0.1,
      src: "tictac",
      vol: 0.18,
      dur: 1.2,
    }),
  ),
  {
    nombre: "parte alta · escalones",
    t: at("hacia la parte alta").start,
    src: "escalones",
    vol: 0.22,
  },
  {
    nombre: "líneas · pop",
    t: at("trabaja por líneas").start,
    src: "pop",
    vol: 0.22,
  },
  {
    nombre: "rodilla ingle · tachado",
    t: at("evita").start + 0.2,
    src: "tachado",
    vol: 0.22,
  },
  {
    nombre: "círculos · whoosh",
    t: at("círculos amplios").start - ANTES.whoosh,
    src: "whoosh",
    vol: 0.22,
  },
  {
    nombre: "un solo lugar · tachado",
    t: at("sin detener").start + 0.2,
    src: "tachado",
    vol: 0.22,
  },
  {
    nombre: "agresivos · pop",
    t: at("no pequeños").start,
    src: "pop",
    vol: 0.22,
  },
  {
    nombre: "verificar · tarjeta",
    t: at("recuerda verificar").start,
    src: "tarjeta",
    vol: 0.22,
  },
  {
    nombre: "baja · blips",
    t: at("baja").start,
    src: "blips",
    vol: 0.2,
    dur: 1.0,
  },
  {
    nombre: "muslo izq · escalones",
    t: at("hacia la parte alta", ZONAS.musloI).start,
    src: "escalones",
    vol: 0.22,
  },
  {
    nombre: "círculos izq · whoosh",
    t: at("movimientos amplios").start - ANTES.whoosh,
    src: "whoosh",
    vol: 0.22,
  },
  { nombre: "firme · pop", t: at("firme").start, src: "pop", vol: 0.22 },
  {
    nombre: "doloroso · tachado",
    t: at("nunca doloroso").start + 0.2,
    src: "tachado",
    vol: 0.22,
  },
  {
    nombre: "círculos glúteo · swish",
    t: at("círculos amplios", 70).start - ANTES.swish,
    src: "swish",
    vol: 0.22,
  },
  {
    nombre: "abajo arriba · escalones",
    t: at("barridos de abajo").start,
    src: "escalones",
    vol: 0.22,
  },
  {
    nombre: "levantamiento · brillo",
    t: at("levantamiento").start,
    src: "brillo",
    vol: 0.2,
  },
  {
    nombre: "terminamos · subida",
    t: at("terminamos").start - ANTES.subida,
    src: "subida",
    vol: 0.2,
  },
  {
    nombre: "15 min · blips",
    t: at("15").start + 0.3,
    src: "blips",
    vol: 0.22,
    dur: 1.0,
  },
  {
    nombre: "intensidad · tachado",
    t: at("no significa").start + 0.2,
    src: "tachado",
    vol: 0.22,
  },
  { nombre: "técnica · pop", t: at("técnica").start, src: "pop", vol: 0.2 },
  {
    nombre: "movimiento · pop",
    t: at("movimiento").start,
    src: "pop",
    vol: 0.2,
  },
  {
    nombre: "constancia · campanita",
    t: at("constancia").start,
    src: "campanita",
    vol: 0.18,
  },
];

// La voz en off del día 6 está grabada más baja (−25,2 LUFS frente a ≈ −16 de los otros días) y no se normaliza
// (estilo.md §10.5): música y efectos bajan lo mismo (≈ −9 dB) para mantener la mezcla de marca
// (música ≈ 16 dB bajo la voz, ningún efecto por encima de ella).
const NIVEL = 0.35;

// Subtítulos: el texto recurrente de cada zona (si hay un aviso justo antes, espera a que termine) y los avisos largos
const SUBS: ItemSubtitulo[] = (() => {
  const avisos = SECCIONES.flatMap((s) => s.subs ?? []);
  const recurrentes = SECCIONES.filter((s) => s.tiempo).map((s) => {
    const previos = avisos.filter(
      (a) => a.desde < s.desde + 1.2 && a.hasta > s.desde,
    );
    const desde = Math.max(s.desde + 1.2, ...previos.map((a) => a.hasta + 0.2));
    return {
      desde,
      hasta: Math.min(s.hasta, desde + lectura(RECURRENTE)),
      texto: RECURRENTE,
    };
  });
  return [...recurrentes, ...avisos];
})();
const Subtitulos: React.FC = () => <Subtitulo items={SUBS} limiteCara={1400} />;

export const Dia6Video: React.FC = () => (
  <Rutina
    dia="dia6"
    caras={{ ...(caras as DatosCaras), cortes: clips.map((c) => c.outStart) }}
    transiciones={Object.values(ZONAS).slice(1)}
    finVoz={WORDS[WORDS.length - 1].end}
    duracion={DURATION}
    efectos={EFECTOS.map((e) => ({ ...e, vol: e.vol * NIVEL }))}
    musica={0.1 * NIVEL}
    musicaCierre={0.2 * NIVEL}
  >
    <Beats />
    <Muneco />
    <Subtitulos />
  </Rutina>
);

export const Dia6 = () => (
  <Composition
    id="Dia6"
    component={Dia6Video}
    durationInFrames={Math.ceil(TOTAL * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
