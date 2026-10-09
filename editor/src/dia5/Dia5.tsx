import React from "react";
import { Composition } from "remotion";
import { VIDEO } from "../brand";
import { DatosCaras } from "../rutinas/Caras";
import { Aviso, Laterales, Resumen, Tiempo, Titulo } from "../rutinas/Graficos";
import { Aceite3D, Apagar3D, Flecha3D, FlechaCirculo3D, Perilla3D } from "../rutinas/Objetos3D";
import { Efecto, Rutina } from "../rutinas/Rutina";
import { useT } from "../rutinas/util";
import caras from "./data/caras.json";
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
    <Aceite3D desde={at("distribuye").start} vierte={at("aceite").start} ancho={300} alto={380} style={pos} />
  ) : (
    <Perilla3D desde={i} niveles={[[i, 1]]} ancho={300} alto={320} style={pos} />
  );
};
const Prep: React.FC = () => (
  <>
    <Titulo desde={0} hasta={ZONAS.circulos} kicker="ABDOMEN Y LATERALES · 15 MIN" kickerAt={0} texto="prepara la piel" textoAt={at("prepara la piel").start + 0.2} />
    <Laterales
      desde={0}
      hasta={ZONAS.circulos}
      elementos={[
        { w: 300, h: 360, orden: ["izq", "der"], render: (pos) => <Tiempo desde={0} hasta={ZONAS.circulos} minutos={1} zona="Preparación" recordatorio={false} style={pos} /> },
        { w: 300, h: 380, orden: ["der", "izq"], render: (pos) => <PrepObjeto pos={pos} /> },
      ]}
    />
  </>
);
const Intensidad: React.FC = () => (
  <Laterales desde={at("recuerda mantener una").start} hasta={ZONAS.circulos} elementos={[{ w: 300, h: 120, orden: ["izq", "der"], render: (pos) => <Aviso at={at("intensidad baja").start} texto="Intensidad baja y cómoda" style={{ ...pos, top: (pos.top as number) + 300 }} /> }]} />
);

const Zona: React.FC<{ desde: number; hasta: number; titulo: string; kicker: string; minutos: number; etiqueta: string; extra: (pos: React.CSSProperties) => React.ReactNode; extraH?: number; extraDesde?: number }> = ({ desde, hasta, titulo, kicker: k, minutos, etiqueta, extra, extraH = 340, extraDesde }) => {
  const { t } = useT();
  const con = t >= (extraDesde ?? desde) - 0.05;
  return (
    <>
      <Titulo desde={desde} hasta={hasta} kicker={k} texto={titulo} />
      <Laterales
        desde={desde}
        hasta={hasta}
        elementos={[
          { w: 300, h: 360, orden: ["izq", "der"], render: (pos) => <Tiempo desde={desde} hasta={hasta} minutos={minutos} zona={etiqueta} style={pos} /> },
          ...(con ? [{ w: 300, h: extraH, orden: ["der", "izq"] as Lado, render: extra }] : []),
        ]}
      />
    </>
  );
};
// Aviso que se coloca bajo el objeto 3D de la zona (misma columna, sin pisarlo)
const AvisoBajo: React.FC<{ desde: number; hasta: number; at: number; texto: string; tipo?: "si" | "no"; orden?: Lado; offset?: number }> = ({ desde, hasta, at: a, texto, tipo = "si", orden = ["der", "izq"], offset = 360 }) => (
  <Laterales desde={desde} hasta={hasta} elementos={[{ w: 300, h: 120, orden, render: (pos) => <Aviso at={a} tipo={tipo} texto={texto} style={{ ...pos, top: (pos.top as number) + offset }} /> }]} />
);

// 1 · "Realiza círculos grandes alrededor del ombligo sin pasar directamente sobre él. Luego… arrastre… durante 4 minutos"
const Circulos: React.FC = () => (
  <Zona desde={ZONAS.circulos} hasta={ZONAS.latD} titulo="círculos amplios" kicker="ALREDEDOR DEL OMBLIGO" minutos={4} etiqueta="Círculos y arrastres" extraDesde={at("círculos").start} extra={(pos) => <FlechaCirculo3D desde={at("círculos").start} ancho={300} alto={320} style={pos} />} />
);
const CirculosAvisos: React.FC = () => {
  const { t } = useT();
  const a = at("sin pasar").start;
  const b = at("arrastras y sueltas").start;
  const c = at("no sostener").start;
  return t < b ? (
    <AvisoBajo desde={a} hasta={b} at={a} tipo="no" texto="Sin pasar sobre el ombligo" />
  ) : t < c ? (
    <AvisoBajo desde={b} hasta={c} at={b} texto="Arrastras y sueltas" />
  ) : (
    <AvisoBajo desde={c} hasta={ZONAS.latD} at={c} tipo="no" texto="Nunca en un solo punto" />
  );
};

// 2 · "lateral derecho… desde el costado… barridos suaves hacia la parte frontal… llevando al ganglio inguinal"
const LatD: React.FC = () => (
  <Zona desde={ZONAS.latD} hasta={ZONAS.latI} titulo="lateral derecho" kicker="DESDE EL COSTADO" minutos={3} etiqueta="Lateral derecho" extraDesde={at("barridos suaves").start} extra={(pos) => <Flecha3D desde={at("barridos suaves").start} dir="izq" ancho={300} alto={320} style={pos} />} />
);
const LatDAvisos: React.FC = () => {
  const { t } = useT();
  const a = at("movimientos lentos").start;
  const b = at("ganglio inguinal").start;
  return t < b ? <AvisoBajo desde={a} hasta={b} at={a} texto="Lentos y controlados" /> : <AvisoBajo desde={b} hasta={ZONAS.latI} at={b} texto="Hacia el ganglio inguinal" />;
};
// 3 · "otros tres minutos en el lateral izquierdo… desde la espalda pasando por tu cintura… hacia el ganglio inguinal"
const LatI: React.FC = () => (
  <Zona desde={ZONAS.latI} hasta={ZONAS.bajo} titulo="lateral izquierdo" kicker="MISMO MOVIMIENTO" minutos={3} etiqueta="Lateral izquierdo" extraDesde={at("repetir").start} extra={(pos) => <Flecha3D desde={at("repetir").start} dir="der" ancho={300} alto={320} style={pos} />} />
);
const LatIAviso: React.FC = () => <AvisoBajo desde={at("arrastras desde").start} hasta={ZONAS.bajo} at={at("arrastras desde").start} texto="De la espalda a la ingle" />;
// 4 · "4 minutos de barridos suaves en el abdomen bajo. Recuerda mantener siempre el dispositivo en movimiento"
const Bajo: React.FC = () => (
  <Zona desde={ZONAS.bajo} hasta={ZONAS.cierre} titulo="abdomen bajo" kicker="BARRIDOS SUAVES" minutos={4} etiqueta="Abdomen bajo" extraDesde={at("barridos suaves", ZONAS.bajo).start} extra={(pos) => <Flecha3D desde={at("barridos suaves", ZONAS.bajo).start} dir="der" ancho={300} alto={320} style={pos} />} />
);
const BajoAviso: React.FC = () => <AvisoBajo desde={at("recuerda mantener siempre").start} hasta={ZONAS.cierre} at={at("recuerda mantener siempre").start} texto="Siempre en movimiento" />;

// Cierre · "haz masajes suaves con tus manos… completaste tus 15 minutos… la constancia… Apaga el equipo y retira el exceso de aceite"
const Manos: React.FC = () => <AvisoBajo desde={ZONAS.cierre} hasta={at("ahora ya completaste").start} at={at("masajes suaves").start} texto="Masaje suave con las manos" orden={["izq", "der"]} offset={0} />;
const Cierre: React.FC = () => {
  const c = at("ahora ya completaste").start;
  return (
    <>
      <Titulo desde={c} hasta={FIN} kicker="COMPLETASTE" kickerAt={c} texto="15 minutos" textoAt={at("15").start} />
      <Laterales
        desde={c}
        hasta={FIN}
        elementos={[
          {
            w: 320,
            h: 360,
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
          { w: 300, h: 320, orden: ["der", "izq"], render: (pos) => <Apagar3D desde={at("apaga el equipo").start - 0.3} apaga={at("apaga").start} limpia={at("retira").start} ancho={300} alto={320} style={pos} /> },
        ]}
      />
    </>
  );
};
const Constancia: React.FC = () => <AvisoBajo desde={at("constancia").start} hasta={FIN} at={at("constancia").start} texto="Constancia antes que intensidad" orden={["izq", "der"]} offset={390} />;

const BEATS: Beat[] = [
  { nombre: "Prep", desde: 0, hasta: ZONAS.circulos, Comp: Prep },
  { nombre: "Intensidad", desde: at("recuerda mantener una").start, hasta: ZONAS.circulos, Comp: Intensidad },
  { nombre: "Círculos", desde: ZONAS.circulos, hasta: ZONAS.latD, Comp: Circulos },
  { nombre: "Círculos avisos", desde: at("sin pasar").start, hasta: ZONAS.latD, Comp: CirculosAvisos },
  { nombre: "Lateral derecho", desde: ZONAS.latD, hasta: ZONAS.latI, Comp: LatD },
  { nombre: "Lateral derecho avisos", desde: at("movimientos lentos").start, hasta: ZONAS.latI, Comp: LatDAvisos },
  { nombre: "Lateral izquierdo", desde: ZONAS.latI, hasta: ZONAS.bajo, Comp: LatI },
  { nombre: "Lateral izquierdo aviso", desde: at("arrastras desde").start, hasta: ZONAS.bajo, Comp: LatIAviso },
  { nombre: "Abdomen bajo", desde: ZONAS.bajo, hasta: ZONAS.cierre, Comp: Bajo },
  { nombre: "Abdomen bajo aviso", desde: at("recuerda mantener siempre").start, hasta: ZONAS.cierre, Comp: BajoAviso },
  { nombre: "Manos", desde: ZONAS.cierre, hasta: at("ahora ya completaste").start, Comp: Manos },
  { nombre: "Cierre", desde: at("ahora ya completaste").start, hasta: FIN, Comp: Cierre },
  { nombre: "Constancia", desde: at("constancia").start, hasta: FIN, Comp: Constancia },
];

const Beats: React.FC = () => {
  const { t } = useT();
  return (
    <>
      {BEATS.filter((b) => t >= b.desde && t < b.hasta).map((b) => {
        const salida = Math.min(1, Math.max(0, (b.hasta - t) / 0.2));
        return (
          <div key={b.nombre} style={{ position: "absolute", inset: 0, opacity: salida, transform: `translateY(${(1 - salida) * -20}px)` }}>
            <b.Comp />
          </div>
        );
      })}
    </>
  );
};

const ANTES = { whoosh: 0.35, swish: 0.18, subida: 0.85 } as const;
const EFECTOS: Efecto[] = [
  { nombre: "prep · whoosh", t: at("prepara la piel").start + 0.2 - ANTES.whoosh, src: "whoosh", vol: 0.26 },
  { nombre: "aceite · brillo", t: at("aceite").start, src: "brillo", vol: 0.2 },
  { nombre: "intensidad · blips", t: at("intensidad baja").start, src: "blips", vol: 0.2, dur: 0.4 },
  ...[ZONAS.circulos, ZONAS.latD, ZONAS.latI, ZONAS.bajo].map((z, i) => ({ nombre: `zona ${i} · tictac`, t: z + 0.1, src: "tictac", vol: 0.18, dur: 1.2 })),
  { nombre: "círculos · whoosh", t: at("círculos").start - ANTES.whoosh + 0.3, src: "whoosh", vol: 0.22 },
  { nombre: "ombligo · tachado", t: at("sin pasar").start + 0.2, src: "tachado", vol: 0.22 },
  { nombre: "arrastras · pop", t: at("arrastras y sueltas").start, src: "pop", vol: 0.22 },
  { nombre: "un punto · tachado", t: at("no sostener").start + 0.2, src: "tachado", vol: 0.22 },
  { nombre: "barridos D · swish", t: at("barridos suaves").start - ANTES.swish, src: "swish", vol: 0.22 },
  { nombre: "lentos · pop", t: at("movimientos lentos").start, src: "pop", vol: 0.22 },
  { nombre: "ganglio · campanita", t: at("ganglio inguinal").start, src: "campanita", vol: 0.16 },
  { nombre: "repetir · swish", t: at("repetir").start - ANTES.swish, src: "swish", vol: 0.22 },
  { nombre: "espalda · pop", t: at("arrastras desde").start, src: "pop", vol: 0.22 },
  { nombre: "bajo · swish", t: at("barridos suaves", ZONAS.bajo).start - ANTES.swish, src: "swish", vol: 0.22 },
  { nombre: "movimiento · pop", t: at("recuerda mantener siempre").start, src: "pop", vol: 0.22 },
  { nombre: "manos · pop", t: at("masajes suaves").start, src: "pop", vol: 0.2 },
  { nombre: "15 · subida", t: at("15").start - ANTES.subida, src: "subida", vol: 0.2 },
  { nombre: "15 · blips", t: at("ahora ya completaste").start + 0.3, src: "blips", vol: 0.22, dur: 1.0 },
  { nombre: "constancia · brillo", t: at("constancia").start, src: "brillo", vol: 0.2 },
  { nombre: "apaga · impacto", t: at("apaga").start, src: "impacto", vol: 0.2 },
];

export const Dia5Video: React.FC = () => (
  <Rutina dia="dia5" caras={caras as DatosCaras} transiciones={Object.values(ZONAS).slice(1)} finVoz={WORDS[WORDS.length - 1].end} duracion={DURATION} efectos={EFECTOS}>
    <Beats />
  </Rutina>
);

export const Dia5 = () => <Composition id="Dia5" component={Dia5Video} durationInFrames={Math.ceil(TOTAL * VIDEO.fps)} fps={VIDEO.fps} width={VIDEO.width} height={VIDEO.height} />;
