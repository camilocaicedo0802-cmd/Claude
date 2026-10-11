import React from "react";
import { Composition } from "remotion";
import { VIDEO } from "../brand";
import { DatosCaras } from "../rutinas/Caras";
import {
  Aviso,
  ItemSubtitulo,
  Laterales,
  lectura,
  Resumen,
  Subtitulo,
  Tiempo,
  Titulo,
} from "../rutinas/Graficos";
import {
  Aceite3D,
  Apagar3D,
  Flecha3D,
  FlechaCirculo3D,
  Perilla3D,
} from "../rutinas/Objetos3D";
import { Efecto, Rutina } from "../rutinas/Rutina";
import { useT } from "../rutinas/util";
import caras from "./data/caras.json";
import clips from "./data/clips.json";
import { at, DURATION, TOTAL, WORDS } from "./timing";

// Reto de 21 días · Vídeo 5 "Abdomen y laterales" (voz en off + tomas de apoyo del crudo largo).

const ZONAS = {
  prep: 0,
  circulos: at("realiza círculos").start,
  latD: at("ahora trabajarás").start,
  latI: at("ahora vamos otros").start,
  bajo: at("finalizamos").start,
  cierre: at("y al finalizar").start,
};
const FIN = TOTAL + 1;

type Beat = { nombre: string; desde: number; hasta: number; Comp: React.FC };
type Lado = ("izq" | "der")[];

// 0 · "Prepara la piel durante un minuto. Distribuye el aceite… Recuerda mantener una intensidad baja y cómoda"
const PrepObjeto: React.FC<{ pos: React.CSSProperties }> = ({ pos }) => {
  const { t } = useT();
  const i = at("recuerda mantener una").start;
  return t < i ? (
    <Aceite3D
      desde={at("distribuye").start}
      vierte={at("aceite").start}
      ancho={260}
      alto={320}
      style={pos}
    />
  ) : (
    <Perilla3D
      desde={i}
      niveles={[[i, 1]]}
      ancho={260}
      alto={280}
      style={pos}
    />
  );
};
const Prep: React.FC = () => {
  return (
    <>
      <Titulo
        desde={0}
        hasta={ZONAS.circulos}
        kicker="ABDOMEN Y LATERALES · 15 MIN"
        kickerAt={0}
        texto="prepara la piel"
        textoAt={at("prepara la piel").start + 0.2}
      />
      <Laterales
        desde={0}
        hasta={ZONAS.circulos}
        elementos={[
          {
            w: 260,
            h: 330,
            orden: ["izq", "der"],
            render: (pos) => (
              <Tiempo
                desde={0}
                hasta={ZONAS.circulos}
                minutos={1}
                zona="Preparación"
                recordatorio={false}
                etiquetaGrande
                style={pos}
              />
            ),
          },
          {
            w: 260,
            h: 320,
            orden: ["der", "izq"],
            render: (pos) => <PrepObjeto pos={pos} />,
          },
        ]}
      />
      <Subtitulo
        items={[
          sub("intensidad baja", "Intensidad baja y cómoda para tu piel", "si"),
        ]}
      />
    </>
  );
};

type Extra = {
  desde: number;
  hasta?: number;
  h: number;
  el: (pos: React.CSSProperties) => React.ReactNode;
};
// Zona con su tiempo: título + tarjeta de minutos + objetos 3D y avisos en la misma pila lateral (nunca se pisan ni tocan la cara)
const Zona: React.FC<{
  desde: number;
  hasta: number;
  titulo: string;
  kicker: string;
  minutos: number;
  etiqueta: string;
  extras: Extra[];
  avisos?: ItemSubtitulo[];
}> = ({
  desde,
  hasta,
  titulo,
  kicker: k,
  minutos,
  etiqueta,
  extras,
  avisos = [],
}) => {
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
                recordatorio={false}
                etiquetaGrande
                style={pos}
              />
            ),
          },
          ...activos.map((e) => ({
            w: 260,
            h: e.h,
            orden: ["der", "izq"] as Lado,
            render: e.el,
          })),
        ]}
      />
      {/* Texto recurrente y avisos largos: subtítulo grande abajo, solo el tiempo que se tarda en leerlo */}
      <Subtitulo
        items={[
          {
            desde: desde + 1.2,
            hasta: Math.min(hasta, desde + 1.2 + lectura(RECURRENTE)),
            texto: RECURRENTE,
          },
          ...avisos,
        ]}
      />
    </>
  );
};
const RECURRENTE =
  "Continúa este movimiento hasta completar el tiempo indicado";
const sub = (
  frase: string,
  texto: string,
  tipo: "si" | "no",
  despues = 0,
): ItemSubtitulo => ({
  desde: at(frase, despues).start,
  hasta: at(frase, despues).start + lectura(texto),
  texto,
  tipo,
});
const aviso = (
  frase: string,
  texto: string,
  tipo: "si" | "no" = "si",
  hasta?: number,
  despues = 0,
): Extra => ({
  desde: at(frase, despues).start,
  hasta,
  h: 110,
  el: (pos) => (
    <Aviso
      at={at(frase, despues).start}
      tipo={tipo}
      texto={texto}
      tamano={30}
      style={pos}
    />
  ),
});

// 1 · "Realiza círculos grandes alrededor del ombligo sin pasar directamente sobre él. Luego… arrastre… durante 4 minutos"
const Circulos: React.FC = () => (
  <Zona
    desde={ZONAS.circulos}
    hasta={ZONAS.latD}
    titulo="círculos amplios"
    kicker="ALREDEDOR DEL OMBLIGO"
    minutos={4}
    etiqueta="Círculos y arrastres"
    extras={[
      {
        desde: at("círculos").start,
        h: 280,
        el: (pos) => (
          <FlechaCirculo3D
            desde={at("círculos").start}
            ancho={260}
            alto={280}
            style={pos}
          />
        ),
      },
      aviso(
        "arrastras y sueltas",
        "Arrastras y sueltas",
        "si",
        at("no sostener").start,
      ),
    ]}
    avisos={[
      sub("sin pasar", "Sin pasar directamente sobre el ombligo", "no"),
      sub(
        "no sostener",
        "Nunca sostengas el dispositivo en un solo punto",
        "no",
      ),
    ]}
  />
);
// 2 · "lateral derecho… desde el costado… barridos suaves hacia la parte frontal… llevando al ganglio inguinal"
const LatD: React.FC = () => (
  <Zona
    desde={ZONAS.latD}
    hasta={ZONAS.latI}
    titulo="lateral derecho"
    kicker="DESDE EL COSTADO"
    minutos={3}
    etiqueta="Lateral derecho"
    extras={[
      {
        desde: at("barridos suaves").start,
        h: 280,
        el: (pos) => (
          <Flecha3D
            desde={at("barridos suaves").start}
            dir="izq"
            ancho={260}
            alto={280}
            style={pos}
          />
        ),
      },
      aviso("movimientos lentos", "Lentos y controlados", "si"),
    ]}
    avisos={[
      sub(
        "ganglio inguinal",
        "Lleva los líquidos hacia el ganglio inguinal",
        "si",
      ),
    ]}
  />
);
// 3 · "otros tres minutos en el lateral izquierdo… desde la espalda pasando por tu cintura… hacia el ganglio inguinal"
const LatI: React.FC = () => (
  <Zona
    desde={ZONAS.latI}
    hasta={ZONAS.bajo}
    titulo="lateral izquierdo"
    kicker="MISMO MOVIMIENTO"
    minutos={3}
    etiqueta="Lateral izquierdo"
    extras={[
      {
        desde: at("repetir").start,
        h: 280,
        el: (pos) => (
          <Flecha3D
            desde={at("repetir").start}
            dir="der"
            ancho={260}
            alto={280}
            style={pos}
          />
        ),
      },
    ]}
    avisos={[
      sub(
        "arrastras desde",
        "Arrastra desde la espalda hacia el ganglio inguinal",
        "si",
      ),
    ]}
  />
);
// 4 · "4 minutos de barridos suaves en el abdomen bajo. Recuerda mantener siempre el dispositivo en movimiento"
const Bajo: React.FC = () => (
  <Zona
    desde={ZONAS.bajo}
    hasta={ZONAS.cierre}
    titulo="abdomen bajo"
    kicker="BARRIDOS SUAVES"
    minutos={4}
    etiqueta="Abdomen bajo"
    extras={[
      {
        desde: at("barridos suaves", ZONAS.bajo).start,
        h: 280,
        el: (pos) => (
          <Flecha3D
            desde={at("barridos suaves", ZONAS.bajo).start}
            dir="der"
            ancho={260}
            alto={280}
            style={pos}
          />
        ),
      },
    ]}
    avisos={[
      sub(
        "recuerda mantener siempre",
        "Mantén siempre el dispositivo en movimiento",
        "si",
      ),
    ]}
  />
);

// Cierre · "haz masajes suaves con tus manos… completaste tus 15 minutos… la constancia… Apaga el equipo y retira el exceso de aceite"
const Manos: React.FC = () => (
  <Subtitulo
    items={[
      sub(
        "masajes suaves",
        "Masaje suave con tus manos para relajar la piel",
        "si",
      ),
    ]}
  />
);
const Cierre: React.FC = () => {
  const c = at("ahora ya completaste").start;
  return (
    <>
      <Titulo
        desde={c}
        hasta={FIN}
        kicker="COMPLETASTE"
        kickerAt={c}
        texto="15 minutos"
        textoAt={at("15").start}
      />
      <Laterales
        desde={c}
        hasta={FIN}
        elementos={[
          {
            w: 280,
            h: 330,
            orden: ["izq", "der"],
            render: (pos) => (
              <Resumen
                at={c}
                filas={[
                  { texto: "Preparación", min: 1 },
                  { texto: "Círculos", min: 4 },
                  { texto: "Lateral der.", min: 3 },
                  { texto: "Lateral izq.", min: 3 },
                  { texto: "Abdomen bajo", min: 4 },
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
                desde={at("apaga el equipo").start - 0.3}
                apaga={at("apaga").start}
                limpia={at("retira").start}
                ancho={260}
                alto={280}
                style={pos}
              />
            ),
          },
        ]}
      />
      <Subtitulo
        items={[
          sub(
            "constancia",
            "La constancia es más importante que una intensidad alta",
            "si",
          ),
        ]}
      />
    </>
  );
};
const BEATS: Beat[] = [
  { nombre: "Prep", desde: 0, hasta: ZONAS.circulos, Comp: Prep },
  {
    nombre: "Círculos",
    desde: ZONAS.circulos,
    hasta: ZONAS.latD,
    Comp: Circulos,
  },
  {
    nombre: "Lateral derecho",
    desde: ZONAS.latD,
    hasta: ZONAS.latI,
    Comp: LatD,
  },
  {
    nombre: "Lateral izquierdo",
    desde: ZONAS.latI,
    hasta: ZONAS.bajo,
    Comp: LatI,
  },
  {
    nombre: "Abdomen bajo",
    desde: ZONAS.bajo,
    hasta: ZONAS.cierre,
    Comp: Bajo,
  },
  {
    nombre: "Manos",
    desde: ZONAS.cierre,
    hasta: at("ahora ya completaste").start,
    Comp: Manos,
  },
  {
    nombre: "Cierre",
    desde: at("ahora ya completaste").start,
    hasta: FIN,
    Comp: Cierre,
  },
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
    t: at("prepara la piel").start + 0.2 - ANTES.whoosh,
    src: "whoosh",
    vol: 0.26,
  },
  { nombre: "aceite · brillo", t: at("aceite").start, src: "brillo", vol: 0.2 },
  {
    nombre: "intensidad · blips",
    t: at("intensidad baja").start,
    src: "blips",
    vol: 0.2,
    dur: 0.4,
  },
  ...[ZONAS.circulos, ZONAS.latD, ZONAS.latI, ZONAS.bajo].map((z, i) => ({
    nombre: `zona ${i} · tictac`,
    t: z + 0.1,
    src: "tictac",
    vol: 0.18,
    dur: 1.2,
  })),
  {
    nombre: "círculos · whoosh",
    t: at("círculos").start - ANTES.whoosh + 0.3,
    src: "whoosh",
    vol: 0.22,
  },
  {
    nombre: "ombligo · tachado",
    t: at("sin pasar").start + 0.2,
    src: "tachado",
    vol: 0.22,
  },
  {
    nombre: "arrastras · pop",
    t: at("arrastras y sueltas").start,
    src: "pop",
    vol: 0.22,
  },
  {
    nombre: "un punto · tachado",
    t: at("no sostener").start + 0.2,
    src: "tachado",
    vol: 0.22,
  },
  {
    nombre: "barridos D · swish",
    t: at("barridos suaves").start - ANTES.swish,
    src: "swish",
    vol: 0.22,
  },
  {
    nombre: "lentos · pop",
    t: at("movimientos lentos").start,
    src: "pop",
    vol: 0.22,
  },
  {
    nombre: "ganglio · campanita",
    t: at("ganglio inguinal").start,
    src: "campanita",
    vol: 0.16,
  },
  {
    nombre: "repetir · swish",
    t: at("repetir").start - ANTES.swish,
    src: "swish",
    vol: 0.22,
  },
  {
    nombre: "espalda · pop",
    t: at("arrastras desde").start,
    src: "pop",
    vol: 0.22,
  },
  {
    nombre: "bajo · swish",
    t: at("barridos suaves", ZONAS.bajo).start - ANTES.swish,
    src: "swish",
    vol: 0.22,
  },
  {
    nombre: "movimiento · pop",
    t: at("recuerda mantener siempre").start,
    src: "pop",
    vol: 0.22,
  },
  {
    nombre: "manos · pop",
    t: at("masajes suaves").start,
    src: "pop",
    vol: 0.2,
  },
  {
    nombre: "15 · subida",
    t: at("15").start - ANTES.subida,
    src: "subida",
    vol: 0.2,
  },
  {
    nombre: "15 · blips",
    t: at("ahora ya completaste").start + 0.3,
    src: "blips",
    vol: 0.22,
    dur: 1.0,
  },
  {
    nombre: "constancia · brillo",
    t: at("constancia").start,
    src: "brillo",
    vol: 0.2,
  },
  { nombre: "apaga · impacto", t: at("apaga").start, src: "impacto", vol: 0.2 },
];

export const Dia5Video: React.FC = () => (
  <Rutina
    dia="dia5"
    caras={{ ...(caras as DatosCaras), cortes: clips.map((c) => c.outStart) }}
    transiciones={Object.values(ZONAS).slice(1)}
    finVoz={WORDS[WORDS.length - 1].end}
    duracion={DURATION}
    efectos={EFECTOS}
  >
    <Beats />
  </Rutina>
);

export const Dia5 = () => (
  <Composition
    id="Dia5"
    component={Dia5Video}
    durationInFrames={Math.ceil(TOTAL * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
