import React from "react";
import { Composition } from "remotion";
import { COLORS, VIDEO } from "../brand";
import { DatosCaras, useCaras, zonasEn } from "../rutinas/Caras";
import { Efecto } from "../rutinas/Rutina";
import { ItemSubtitulo, lectura, Subtitulo } from "../rutinas/Graficos";
import { useT } from "../rutinas/util";
import { Elem, Lado } from "../dia6/Maqueta";
import { Zoom } from "../dia7/Base7";
import { Destellos, Nota, Pizarra } from "../dia9/Graficos";
import { ConRotulo, GotaZona3D, Medidor3D } from "../dia9/Objetos3D";
import { BaseComp, progresoTarjeta, Tarjeta } from "../comp/BaseComp";
import { ajustarComp, ColumnasComp } from "../comp/MaquetaComp";
import { Calor, CapPrep, Checks, Cronometro, MapaAbdomen, Orden, PasoPrep, PildoraPaso, Respira, TituloPrep } from "../comp/Graficos";
import caras from "./data/caras.json";
import clips from "./data/clips.json";
import { at, DURATION, TOTAL, WORDS } from "./timing";

// Vídeo complementario · Preparación del abdomen (masaje manual antes de la rutina con Luma Body). Voz en off sobre
// las tomas del crudo (scripts/comp/montar.py abdomen): solo tramos sin conversación, con la mirada en su cuerpo y
// la acción que dice la voz (estilo.md §10.21–24). Cada gráfico nace de su frase; lo largo va como subtítulo de
// lectura (§10.18) y las tarjetas solo llevan lo que se lee de un vistazo.

const FIN = TOTAL + 1;
const CARPETA = "comp_abdomen";
const FOTOGRAMAS = clips.reduce((n, c) => n + c.frames, 0);
const clip = (frase: string) => {
  const i = clips.findIndex((c) => c.frase === frase);
  if (i < 0) throw new Error(`Toma no encontrada: ${frase}`);
  return { desde: clips[i].outStart, hasta: i + 1 < clips.length ? clips[i + 1].outStart : TOTAL };
};
const IZQ: Lado = "izq";
const DER: Lado = "der";

// ---------- Tarjetas (la toma se encoge y arriba entra el título con los pasos) ----------
const TARJETAS: Tarjeta[] = [
  { desde: 0.12, hasta: clip("antes de comenzar").desde },
  { desde: clip("continua").desde, hasta: FIN + 2 },
];
const CAPS: CapPrep[] = [
  { desde: 0.12, kicker: "PREPARACIÓN MANUAL", titulo: "abdomen" },
  { desde: clip("continua").desde, kicker: "PIEL LISTA · AHORA SÍ", titulo: "tu rutina Luma Body" },
];
const PASOS: PasoPrep[] = [
  { nombre: "Aceite", at: at("aplica").start },
  { nombre: "Parte baja", at: at("ahora ubica").start },
  { nombre: "Ombligo", at: at("después lleva").start },
  { nombre: "Respira", at: at("acompaña").start },
  { nombre: "1–2 min", at: at("repite").start },
];

// ---------- Secciones y recursos en las columnas ----------
type Extra = { desde: number; hasta?: number; w?: number; h: number; escala?: number; lado?: Lado; el: (pos: React.CSSProperties) => React.ReactNode };
type Seccion = { nombre: string; desde: number; hasta: number; paso?: boolean; extras: Extra[] };
const S = {
  luma: clip("antes de comenzar").desde,
  aceite: clip("aplica").desde,
  baja: clip("ahora ubica").desde,
  presion: clip("no necesitas").desde,
  ombligo: clip("despues lleva").desde,
  respira: clip("acompana").desde,
  repite: clip("repite").desde,
  final: clip("continua").desde,
};
const MAPA = (hasta: number): Extra => ({
  desde: S.baja,
  hasta,
  w: 260,
  h: 300,
  lado: DER,
  el: (pos) => (
    <MapaAbdomen
      desde={S.baja + 0.15}
      pasos={[
        { t: S.baja, modo: "nada" },
        { t: at("parte baja").start, modo: "baja" },
        { t: at("deslizando").start, modo: "costados" },
        { t: at("círculos").start, modo: "ombligo" },
      ]}
      style={pos}
    />
  ),
});

const SECCIONES: Seccion[] = [
  // "Antes de comenzar con nuestra rutina de Luma Body, vamos a preparar suavemente la piel con un pequeño masaje manual."
  {
    nombre: "Orden",
    desde: S.luma,
    hasta: S.aceite,
    extras: [
      {
        desde: S.luma + 0.1,
        w: 300,
        h: 190,
        lado: DER,
        el: (pos) => <Orden at={S.luma + 0.1} luma={at("luma").start} manual={at("masaje").start} style={pos} />,
      },
    ],
  },
  // "Aplica suficiente aceite en las manos y frótalas entre sí para distribuirlo y calentarlo ligeramente."
  {
    nombre: "Aceite",
    desde: S.aceite,
    hasta: S.baja,
    paso: true,
    extras: [
      {
        desde: S.aceite + 0.05,
        w: 300,
        h: 300,
        lado: DER,
        el: (pos) => (
          <GotaZona3D desde={S.aceite + 0.05} cae={at("aceite").start} desliza={999} ancho={300} alto={300} style={pos} />
        ),
      },
      { desde: at("calentarlo").start - 0.1, w: 260, h: 220, lado: IZQ, el: (pos) => <Calor at={at("calentarlo").start - 0.1} style={pos} /> },
    ],
  },
  // "Ahora ubica las manos en la parte baja del abdomen, cerca de la zona inguinal, y realiza movimientos circulares
  // muy suaves, deslizando las manos desde los costados hacia el frente."
  { nombre: "Parte baja", desde: S.baja, hasta: S.presion, paso: true, extras: [MAPA(S.presion)] },
  // "No necesitas hacer fuerza, la presión debe ser ligera, lenta y muy cómoda"
  {
    nombre: "Presión",
    desde: S.presion,
    hasta: S.ombligo,
    paso: true,
    extras: [
      {
        desde: at("presión").start - 0.1,
        w: 280,
        h: 306,
        lado: IZQ,
        el: (pos) => (
          <ConRotulo ancho={280} alto={250} rotulo="PRESIÓN LIGERA" rotuloAt={at("ligera").start} style={pos}>
            <Medidor3D
              desde={at("presión").start - 0.1}
              niveles={[
                [at("presión").start, 0.5],
                [at("ligera").start, 0.14],
              ]}
              ancho={280}
              alto={250}
              style={{ left: 0, top: 0 }}
            />
          </ConRotulo>
        ),
      },
      {
        desde: at("ligera").start - 0.1,
        w: 280,
        h: 200,
        lado: DER,
        el: (pos) => (
          <Checks
            items={[
              { texto: "Ligera", at: at("ligera").start },
              { texto: "Lenta", at: at("lenta").start },
              { texto: "Cómoda", at: at("cómoda").start },
            ]}
            style={pos}
          />
        ),
      },
    ],
  },
  // "Después lleva las manos hacia el abdomen y realiza círculos amplios alrededor del ombligo sin presionar
  // directamente sobre él" (congelado con la pizarra en "alrededor")
  { nombre: "Ombligo", desde: S.ombligo, hasta: S.respira, paso: true, extras: [MAPA(clip("alrededor").desde)] },
  // "Acompaña el movimiento con respiraciones lentas y profundas para relajar la zona"
  {
    nombre: "Respira",
    desde: S.respira,
    hasta: S.repite,
    paso: true,
    extras: [{ desde: at("respiraciones").start - 0.1, w: 260, h: 270, lado: IZQ, el: (pos) => <Respira at={at("respiraciones").start - 0.1} style={pos} /> }],
  },
  // "Repite esta preparación durante uno o dos minutos y cuando la piel tenga suficiente deslizamiento…"
  {
    nombre: "Repite",
    desde: S.repite,
    hasta: S.final,
    paso: true,
    extras: [
      { desde: at("durante").start - 0.1, w: 260, h: 290, lado: DER, el: (pos) => <Cronometro at={at("durante").start - 0.1} hasta={S.final} style={pos} /> },
      {
        desde: at("deslizamiento").start,
        w: 300,
        h: 110,
        escala: 0.95,
        lado: IZQ,
        el: (pos) => <Nota at={at("deslizamiento").start} texto="Piel con deslizamiento" ancho={300} style={pos} />,
      },
    ],
  },
];

const TARJ = (t: number) => progresoTarjeta(TARJETAS, t);
const useElementos = (s: Seccion): Elem[] => {
  const caras = useCaras();
  const { t } = useT();
  const { actual } = zonasEn(caras, t, s.desde, s.hasta);
  const fijos: Elem[] = s.paso ? [{ w: 300, h: 62, lado: IZQ, render: (st) => <PildoraPaso pasos={PASOS} style={st} /> }] : [];
  const lista: Elem[] = [];
  for (const e of s.extras)
    if (t >= e.desde - 0.05 && t < (e.hasta ?? s.hasta)) lista.push({ w: e.w ?? 300, h: e.h, escala: e.escala, lado: e.lado, render: e.el });
  return ajustarComp(actual, fijos, lista);
};
const SeccionComp: React.FC<{ s: Seccion }> = ({ s }) => <ColumnasComp desde={s.desde} hasta={s.hasta} elementos={useElementos(s)} />;

// ---------- Subtítulos de lectura (§10.18): solo las indicaciones clave, el tiempo justo para leerlas ----------
const sub = (frase: string, texto: string, tipo?: "si" | "no", despues = 0): ItemSubtitulo => {
  const desde = at(frase, despues).start;
  return { desde, hasta: desde + lectura(texto), texto, tipo };
};
const SUBS: ItemSubtitulo[] = [
  sub("frótalas", "Frótalas para calentar el aceite"),
  sub("cerca", "Parte baja, cerca de la ingle"),
  sub("deslizando", "De los costados hacia el frente"),
  sub("no necesitas", "No necesitas hacer fuerza", "si"),
  sub("respiraciones", "Respira lento y profundo"),
  sub("repite", "Repite durante 1 o 2 minutos"),
];

// ---------- Pizarra sobre el congelado: círculos alrededor del ombligo, nunca encima ----------
const PZ = clip("alrededor");
const OMB = { x: 520, y: 905 };
const Pizarras: React.FC = () => (
  <Pizarra
    desde={PZ.desde}
    hasta={PZ.hasta}
    foco={{ cx: OMB.x, cy: OMB.y, rx: 240, ry: 210 }}
    trazos={[
      {
        tipo: "flecha",
        pts: Array.from({ length: 25 }, (_, i) => {
          const a = -Math.PI / 2 + (i / 24) * Math.PI * 1.75;
          return [OMB.x + 150 * Math.cos(a), OMB.y + 120 * Math.sin(a)] as [number, number];
        }),
        at: PZ.desde + 0.2,
        dur: 0.8,
      },
      { tipo: "prohibido", x: OMB.x, y: OMB.y, r: 44, at: at("sin presionar").start },
      { tipo: "etiqueta", x: OMB.x, y: OMB.y - 210, texto: "Círculos amplios", at: PZ.desde + 0.3, ancla: "centro" },
      { tipo: "etiqueta", x: OMB.x, y: OMB.y + 200, texto: "Nunca sobre el ombligo", at: at("sin presionar").start + 0.15, ancla: "centro", tono: "no" },
    ]}
  />
);

const Escenario: React.FC = () => {
  const { t } = useT();
  return (
    <>
      <Pizarras />
      {SECCIONES.filter((b) => t >= b.desde && t < b.hasta).map((b) => {
        const salida = Math.min(1, Math.max(0, (b.hasta - t) / 0.2));
        return (
          <div key={b.nombre} style={{ position: "absolute", inset: 0, opacity: salida }}>
            <SeccionComp s={b} />
          </div>
        );
      })}
      <Subtitulo items={SUBS} limiteCara={1400} />
    </>
  );
};

const Fuera: React.FC = () => {
  const { t } = useT();
  return (
    <>
      <TituloPrep caps={CAPS} pasos={PASOS} p={TARJ(t)} />
      <Destellos
        en={[
          { t: PZ.desde, color: "#FFFFFF", max: 0.7 },
          { t: S.final, color: COLORS.durazno, max: 0.55 },
        ]}
      />
    </>
  );
};

// ---------- Cámara: reencuadres lentos hacia la zona que se trabaja ----------
const z = (frase: string, z0: number, z1: number, ox: number, oy: number): Zoom => ({ ...clip(frase), z0, z1, ox, oy });
const ZOOMS: Zoom[] = [
  z("antes de comenzar", 1.0, 1.12, 520, 950),
  z("ahora ubica", 1.0, 1.18, 530, 1030),
  z("y realiza movimientos", 1.12, 1.0, 530, 1030),
  z("despues lleva", 1.0, 1.15, 520, 900),
  z("acompana", 1.1, 1.0, 520, 900),
];
const WHIPS = ["y frotalas", "deslizando", "acompana"].map((f) => clip(f).desde);

// ---------- Efectos (estilo.md §10.14) ----------
const ef = (nombre: string, t: number, src: string, vol = 0.22, dur?: number): Efecto => ({ nombre, t, src, vol, dur });
const EFECTOS: Efecto[] = [
  ef("tarjeta", 0.1, "tarjeta", 0.22),
  ef("título · whoosh", 0.2, "whoosh", 0.22),
  ef("orden · tarjeta", S.luma + 0.1, "tarjeta", 0.2),
  ef("luma · pop", at("luma").start, "pop", 0.18),
  ef("manual · brillo", at("masaje").start, "brillo", 0.18),
  ef("paso 1 · swish", S.aceite, "swish", 0.2),
  ef("gota · pop", at("aceite").start + 0.42, "pop", 0.2),
  ef("calor · brillo", at("calentarlo").start, "brillo", 0.16),
  ...WHIPS.map((w, i) => ef(`barrido ${i} · whoosh`, w - 0.2, "whoosh", 0.18)),
  ef("paso 2 · swish", S.baja, "swish", 0.2),
  ef("mapa · tarjeta", S.baja + 0.15, "tarjeta", 0.18),
  ef("costados · swish", at("deslizando").start, "swish", 0.16),
  ef("medidor · tarjeta", at("presión").start - 0.1, "tarjeta", 0.2),
  ef("baja · blips", at("ligera").start, "blips", 0.14, 0.8),
  ef("cómoda · pop", at("cómoda").start, "pop", 0.18),
  ef("paso 3 · swish", S.ombligo, "swish", 0.2),
  ef("congela · obturador", PZ.desde, "obturador", 0.24),
  ef("ombligo · tachado", at("sin presionar").start + 0.12, "tachado", 0.2),
  ef("paso 4 · swish", S.respira, "swish", 0.18),
  ef("respira · brillo", at("respiraciones").start, "brillo", 0.14),
  ef("paso 5 · swish", S.repite, "swish", 0.18),
  ef("cronómetro · tictac", at("durante").start, "tictac", 0.16, 1.6),
  ef("deslizamiento · pop", at("deslizamiento").start, "pop", 0.18),
  ef("final · campanita", S.final + 0.1, "campanita", 0.16),
];

// Voz en off a −23,7 LUFS (sin tocar): música y efectos ×0,43 para quedar ~16 dB por debajo (como el día 9).
const NIVEL = 0.43;

export const CompAbdomenVideo: React.FC = () => (
  <BaseComp
    carpeta={CARPETA}
    fotogramas={FOTOGRAMAS}
    caras={{ ...(caras as DatosCaras), cortes: clips.map((c) => c.outStart) }}
    zooms={ZOOMS}
    tarjetas={TARJETAS}
    whips={WHIPS}
    finVoz={WORDS[WORDS.length - 1].end}
    duracion={DURATION}
    efectos={EFECTOS.map((e) => ({ ...e, vol: e.vol * NIVEL }))}
    musica={0.1 * NIVEL}
    musicaCierre={0.2 * NIVEL}
    escenario={<Escenario />}
  >
    <Fuera />
  </BaseComp>
);

export const CompAbdomen = () => (
  <Composition
    id="PreparacionAbdomen"
    component={CompAbdomenVideo}
    durationInFrames={Math.ceil(TOTAL * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
