import React from "react";
import { Composition } from "remotion";
import { VIDEO } from "../brand";
import { DatosCaras } from "../rutinas/Caras";
import { Aviso, Laterales, Resumen, Tiempo, Titulo } from "../rutinas/Graficos";
import {
  Aceite3D,
  Apagar3D,
  Flecha3D,
  FlechaCirculo3D,
} from "../rutinas/Objetos3D";
import { Efecto, Rutina } from "../rutinas/Rutina";
import { useT } from "../rutinas/util";
import caras from "./data/caras.json";
import clips from "./data/clips.json";
import { at, DURATION, TOTAL, WORDS } from "./timing";

// Reto de 21 días · Vídeo 4 "Adaptación de piernas y glúteos" (voz en off + tomas de apoyo del crudo largo).
// Cada tramo de la toma de apoyo coincide con la frase (scripts/rutinas/montar.py) y cada gráfico nace de su frase.

const ZONAS = {
  prep: 0,
  pantD: at("trabaja la pantorrilla").start,
  pantI: at("cambia de pierna").start,
  musloD: at("continúa con el muslo").start,
  musloI: at("cambia al muslo").start,
  gluteos: at("finaliza con dos").start,
  cierre: at("con esto terminamos").start,
};
const FIN = TOTAL + 1;

type Beat = { nombre: string; desde: number; hasta: number; Comp: React.FC };

// 0 · "Comenzamos preparando la piel. Aplica suficiente aceite para que el Luma Body pueda deslizarse fácilmente."
const Prep: React.FC = () => {
  const d = ZONAS.prep;
  const h = ZONAS.pantD;
  return (
    <>
      <Titulo
        desde={d}
        hasta={h}
        kicker="PIERNAS Y GLÚTEOS · 15 MIN"
        kickerAt={0}
        texto="prepara la piel"
        textoAt={at("preparando").start}
      />
      <Laterales
        desde={d}
        hasta={h}
        elementos={[
          {
            w: 260,
            h: 320,
            orden: ["der", "izq"],
            render: (pos) => (
              <Aceite3D
                desde={at("aplica suficiente").start}
                vierte={at("aceite").start}
                ancho={260}
                alto={320}
                style={pos}
              />
            ),
          },
          {
            w: 260,
            h: 110,
            orden: ["izq", "der"],
            render: (pos) => (
              <Aviso
                at={at("deslizarse").start}
                texto="Suficiente aceite para deslizar"
                style={pos}
              />
            ),
          },
        ]}
      />
    </>
  );
};

// Elemento lateral que aparece en un instante (y opcionalmente desaparece): objeto 3D o aviso
type Extra = {
  desde: number;
  hasta?: number;
  h: number;
  el: (pos: React.CSSProperties) => React.ReactNode;
};

// Zona con su tiempo: título + tarjeta de minutos (texto recurrente del guion) + objetos 3D y avisos según la frase.
// Todo va en la misma pila lateral, así nunca se pisan ni tocan la cara.
const Zona: React.FC<{
  desde: number;
  hasta: number;
  titulo: string;
  kicker: string;
  minutos: number;
  etiqueta: string;
  extras: Extra[];
}> = ({ desde, hasta, titulo, kicker: k, minutos, etiqueta, extras }) => {
  const { t } = useT();
  const activos = extras.filter(
    (e) => t >= e.desde - 0.05 && t < (e.hasta ?? hasta),
  );
  return (
    <>
      <Titulo desde={desde} hasta={hasta} kicker={k} texto={titulo} />
      <Laterales
        desde={desde}
        hasta={hasta}
        elementos={[
          {
            w: 260,
            h: 330,
            orden: ["izq", "der"],
            render: (pos) => (
              <Tiempo
                desde={desde}
                hasta={hasta}
                minutos={minutos}
                zona={etiqueta}
                style={pos}
              />
            ),
          },
          ...activos.map((e) => ({
            w: 260,
            h: e.h,
            orden: ["der", "izq"] as ("der" | "izq")[],
            render: e.el,
          })),
        ]}
      />
    </>
  );
};
const aviso = (
  frase: string,
  texto: string,
  tipo: "si" | "no" = "si",
  hasta?: number,
): Extra => ({
  desde: at(frase).start,
  hasta,
  h: 110,
  el: (pos) => (
    <Aviso at={at(frase).start} tipo={tipo} texto={texto} style={pos} />
  ),
});

const PantD: React.FC = () => (
  <Zona
    desde={ZONAS.pantD}
    hasta={ZONAS.pantI}
    titulo="pantorrilla derecha"
    kicker="DEL TOBILLO HACIA ARRIBA"
    minutos={2}
    etiqueta="Pantorrilla derecha"
    extras={[
      {
        desde: at("hacia arriba").start,
        h: 290,
        el: (pos) => (
          <Flecha3D
            desde={at("hacia arriba").start}
            dir="arriba"
            ancho={260}
            alto={290}
            style={pos}
          />
        ),
      },
      aviso("sin pasar", "Sin pasar detrás de la rodilla", "no"),
    ]}
  />
);
const PantI: React.FC = () => (
  <Zona
    desde={ZONAS.pantI}
    hasta={ZONAS.musloD}
    titulo="pantorrilla izquierda"
    kicker="CAMBIA DE PIERNA"
    minutos={2}
    etiqueta="Pantorrilla izquierda"
    extras={[
      aviso("velocidad constante", "Velocidad constante"),
      aviso("presión cómoda", "Presión cómoda"),
    ]}
  />
);
const MusloD: React.FC = () => (
  <Zona
    desde={ZONAS.musloD}
    hasta={ZONAS.musloI}
    titulo="muslo derecho"
    kicker="LÍNEAS ASCENDENTES"
    minutos={3}
    etiqueta="Muslo derecho"
    extras={[
      aviso("frente", "Frente", "si", at("terminando").start),
      aviso("costado", "Costado", "si", at("terminando").start),
      aviso(
        "parte posterior del muslo",
        "Parte posterior",
        "si",
        at("terminando").start,
      ),
      aviso("terminando", "Termina antes de la ingle", "no"),
      {
        desde: at("de abajo hacia arriba").start,
        h: 290,
        el: (pos) => (
          <Flecha3D
            desde={at("de abajo hacia arriba").start}
            dir="arriba"
            ancho={260}
            alto={290}
            style={pos}
          />
        ),
      },
    ]}
  />
);
const MusloI: React.FC = () => (
  <Zona
    desde={ZONAS.musloI}
    hasta={ZONAS.gluteos}
    titulo="muslo izquierdo"
    kicker="MISMO MOVIMIENTO"
    minutos={3}
    etiqueta="Muslo izquierdo"
    extras={[
      // "las líneas deben ir en forma ascendente" → flecha hacia arriba; "si no se desliza… aplica más aceite" → frasco
      {
        desde: at("ascendente").start,
        hasta: at("si es que no").start,
        h: 290,
        el: (pos) => (
          <Flecha3D
            desde={at("ascendente").start}
            dir="arriba"
            ancho={260}
            alto={290}
            style={pos}
          />
        ),
      },
      {
        desde: at("si es que no").start,
        h: 320,
        el: (pos) => (
          <Aceite3D
            desde={at("si es que no").start}
            vierte={at("aplica más|mas aceite").start}
            ancho={260}
            alto={320}
            style={pos}
          />
        ),
      },
      aviso("para y aplica", "Para y aplica más aceite"),
    ]}
  />
);
const Gluteos: React.FC = () => (
  <Zona
    desde={ZONAS.gluteos}
    hasta={ZONAS.cierre}
    titulo="glúteos"
    kicker="DOS MINUTOS EN CADA UNO"
    minutos={2}
    etiqueta="Cada glúteo"
    extras={[
      // "movimientos circulares amplios" → gira; "pasadas ascendentes" → sube; "combina círculos" → vuelve a girar
      {
        desde: at("circulares").start,
        hasta: at("pasadas ascendentes en").start,
        h: 280,
        el: (pos) => (
          <FlechaCirculo3D
            desde={at("circulares").start}
            ancho={260}
            alto={280}
            style={pos}
          />
        ),
      },
      {
        desde: at("pasadas ascendentes en").start,
        hasta: at("combina").start,
        h: 290,
        el: (pos) => (
          <Flecha3D
            desde={at("pasadas ascendentes en").start}
            dir="arriba"
            ancho={260}
            alto={290}
            style={pos}
          />
        ),
      },
      {
        desde: at("combina").start,
        h: 280,
        el: (pos) => (
          <FlechaCirculo3D
            desde={at("combina").start}
            ancho={260}
            alto={280}
            style={pos}
          />
        ),
      },
      aviso("no dejar", "Nunca en un solo punto", "no"),
    ]}
  />
);

// Cierre · "Completaste 15 minutos… Apaga el dispositivo y realiza pases suaves con tus manos… hacia los ganglios inguinales"
const Cierre: React.FC = () => {
  const { t } = useT();
  return (
    <>
      <Titulo
        desde={ZONAS.cierre}
        hasta={FIN}
        kicker="RUTINA"
        kickerAt={ZONAS.cierre}
        texto="terminada"
        textoAt={at("terminamos").start}
      />
      <Laterales
        desde={ZONAS.cierre}
        hasta={FIN}
        elementos={[
          {
            w: 280,
            h: 300,
            orden: ["izq", "der"],
            render: (pos) => (
              <Resumen
                at={at("completaste").start}
                filas={[
                  { texto: "Aceite", min: 1 },
                  { texto: "Pantorrillas", min: 4 },
                  { texto: "Muslos", min: 6 },
                  { texto: "Glúteos", min: 4 },
                ]}
                style={pos}
              />
            ),
          },
          {
            w: 260,
            h: 280,
            orden: ["der", "izq"],
            render: (pos) => (
              <Apagar3D
                desde={at("apaga el dispositivo").start - 0.3}
                apaga={at("apaga").start}
                limpia={at("pases suaves").start}
                ancho={260}
                alto={280}
                style={pos}
              />
            ),
          },
          ...(t >= at("realiza pases").start
            ? [
                {
                  w: 260,
                  h: 140,
                  orden: ["der", "izq"] as ("der" | "izq")[],
                  render: (pos: React.CSSProperties) => (
                    <Aviso
                      at={at("realiza pases").start}
                      texto="Pases suaves con las manos hacia la ingle"
                      style={pos}
                    />
                  ),
                },
              ]
            : []),
        ]}
      />
    </>
  );
};

const BEATS: Beat[] = [
  { nombre: "Prep", desde: 0, hasta: ZONAS.pantD, Comp: Prep },
  {
    nombre: "Pantorrilla derecha",
    desde: ZONAS.pantD,
    hasta: ZONAS.pantI,
    Comp: PantD,
  },
  {
    nombre: "Pantorrilla izquierda",
    desde: ZONAS.pantI,
    hasta: ZONAS.musloD,
    Comp: PantI,
  },
  {
    nombre: "Muslo derecho",
    desde: ZONAS.musloD,
    hasta: ZONAS.musloI,
    Comp: MusloD,
  },
  {
    nombre: "Muslo izquierdo",
    desde: ZONAS.musloI,
    hasta: ZONAS.gluteos,
    Comp: MusloI,
  },
  {
    nombre: "Glúteos",
    desde: ZONAS.gluteos,
    hasta: ZONAS.cierre,
    Comp: Gluteos,
  },
  { nombre: "Cierre", desde: ZONAS.cierre, hasta: FIN, Comp: Cierre },
];

const Beats: React.FC = () => {
  const { t } = useT();
  return (
    <>
      {BEATS.filter((b) => t >= b.desde && t < b.hasta).map((b) => {
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
            <b.Comp />
          </div>
        );
      })}
    </>
  );
};

const ANTES = { whoosh: 0.35, swish: 0.18, subida: 0.85 } as const;
const EFECTOS: Efecto[] = [
  {
    nombre: "prep · whoosh",
    t: at("preparando").start - ANTES.whoosh,
    src: "whoosh",
    vol: 0.26,
  },
  { nombre: "aceite · brillo", t: at("aceite").start, src: "brillo", vol: 0.2 },
  ...[ZONAS.pantD, ZONAS.pantI, ZONAS.musloD, ZONAS.musloI, ZONAS.gluteos].map(
    (z, i) => ({
      nombre: `zona ${i} · tictac`,
      t: z + 0.1,
      src: "tictac",
      vol: 0.18,
      dur: 1.2,
    }),
  ),
  {
    nombre: "arriba · escalones",
    t: at("hacia arriba").start,
    src: "escalones",
    vol: 0.22,
  },
  { nombre: "rodilla · pop", t: at("sin pasar").start, src: "pop", vol: 0.24 },
  {
    nombre: "velocidad · pop",
    t: at("velocidad constante").start,
    src: "pop",
    vol: 0.22,
  },
  { nombre: "frente · pop", t: at("frente").start, src: "pop", vol: 0.22 },
  { nombre: "costado · pop", t: at("costado").start, src: "pop", vol: 0.22 },
  {
    nombre: "posterior · pop",
    t: at("parte posterior del muslo").start,
    src: "pop",
    vol: 0.22,
  },
  {
    nombre: "ingle · tachado",
    t: at("terminando").start + 0.2,
    src: "tachado",
    vol: 0.22,
  },
  {
    nombre: "abajo arriba · escalones",
    t: at("de abajo hacia arriba").start,
    src: "escalones",
    vol: 0.2,
  },
  {
    nombre: "más aceite · swish",
    t: at("si es que no").start - ANTES.swish,
    src: "swish",
    vol: 0.22,
  },
  {
    nombre: "circulares · whoosh",
    t: at("circulares").start - ANTES.whoosh,
    src: "whoosh",
    vol: 0.22,
  },
  {
    nombre: "un punto · tachado",
    t: at("no dejar").start + 0.2,
    src: "tachado",
    vol: 0.22,
  },
  {
    nombre: "terminada · subida",
    t: at("terminamos").start - ANTES.subida,
    src: "subida",
    vol: 0.2,
  },
  {
    nombre: "15 min · blips",
    t: at("completaste").start + 0.3,
    src: "blips",
    vol: 0.22,
    dur: 1.0,
  },
  { nombre: "apaga · impacto", t: at("apaga").start, src: "impacto", vol: 0.2 },
  {
    nombre: "manos · campanita",
    t: at("pases suaves").start,
    src: "campanita",
    vol: 0.18,
  },
];

export const Dia4Video: React.FC = () => (
  <Rutina
    dia="dia4"
    caras={{ ...(caras as DatosCaras), cortes: clips.map((c) => c.outStart) }}
    transiciones={Object.values(ZONAS).slice(1)}
    finVoz={WORDS[WORDS.length - 1].end}
    duracion={DURATION}
    efectos={EFECTOS}
  >
    <Beats />
  </Rutina>
);

export const Dia4 = () => (
  <Composition
    id="Dia4"
    component={Dia4Video}
    durationInFrames={Math.ceil(TOTAL * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
