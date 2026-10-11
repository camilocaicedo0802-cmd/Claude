import React from "react";
import { Composition } from "remotion";
import { COLORS, VIDEO } from "../brand";
import { DatosCaras } from "../rutinas/Caras";
import { Efecto } from "../rutinas/Rutina";
import { ItemSubtitulo, lectura, Subtitulo } from "../rutinas/Graficos";
import { useT } from "../rutinas/util";
import { Elem, Lado } from "../dia6/Maqueta";
import { Zoom } from "../dia7/Base7";
import { Destellos, Nota, Pizarra } from "../dia9/Graficos";
import { Chevrones3D, ConRotulo, GotaZona3D, Medidor3D } from "../dia9/Objetos3D";
import { BaseComp, progresoTarjeta, Tarjeta } from "../comp/BaseComp";
import { ColumnasLibres } from "../comp/MaquetaComp";
import { CapPrep, Checks, Cronometro, Orden, PasoPrep, PildoraPaso, RutaPierna, TituloPrep } from "../comp/Graficos";
import caras from "./data/caras.json";
import clips from "./data/clips.json";
import { at, DURATION, TOTAL, WORDS } from "./timing";

// Vídeo complementario · Preparación de las piernas (masaje manual antes de la rutina con Luma Body). Voz en off sobre
// las tomas del crudo (scripts/comp/montar.py piernas): el pie sobre el banco, del tobillo hacia arriba; solo tramos
// sin conversación y con la mirada en la pierna (estilo.md §10.21–24). La pierna de perfil (2D) va dibujando la ruta
// del masaje frase a frase; dos pizarras sobre congelados marcan dónde se para (antes de la rodilla y de la ingle).

const FIN = TOTAL + 1;
const CARPETA = "comp_piernas";
const FOTOGRAMAS = clips.reduce((n, c) => n + c.frames, 0);
const clip = (frase: string) => {
  const i = clips.findIndex((c) => c.frase === frase);
  if (i < 0) throw new Error(`Toma no encontrada: ${frase}`);
  return { desde: clips[i].outStart, hasta: i + 1 < clips.length ? clips[i + 1].outStart : TOTAL };
};
const IZQ: Lado = "izq";
// Las columnas no bajan de aquí: la pierna (la acción) ocupa la mitad de abajo del cuadro
const ABAJO = 960;
const DER: Lado = "der";

// ---------- Tarjetas y pasos ----------
const TARJETAS: Tarjeta[] = [
  { desde: 0.12, hasta: clip("antes de utilizar").desde },
  { desde: clip("antes de comenzar").desde, hasta: FIN + 2 },
];
const CAPS: CapPrep[] = [
  { desde: 0.12, kicker: "PREPARACIÓN MANUAL", titulo: "piernas" },
  { desde: clip("antes de comenzar").desde, kicker: "PIEL LISTA · AHORA SÍ", titulo: "tu rutina Luma Body" },
];
const PASOS: PasoPrep[] = [
  { nombre: "Aceite", at: at("comienza").start },
  { nombre: "Pantorrilla", at: at("y distribuyelo").start },
  { nombre: "Rodilla", at: at("al llegar").start },
  { nombre: "Muslo", at: at("luego").start },
  { nombre: "Otra pierna", at: at("repite").start },
];

type Extra = { desde: number; hasta?: number; w?: number; h: number; escala?: number; lado?: Lado; el: (pos: React.CSSProperties) => React.ReactNode };
type Seccion = { nombre: string; desde: number; hasta: number; paso?: boolean; extras: Extra[] };
const S = {
  luma: clip("antes de utilizar").desde,
  aceite: clip("comienza").desde,
  pantorrilla: clip("desde la pantorrilla").desde,
  rodilla: clip("al llegar").desde,
  muslo: clip("luego").desde,
  ingle: clip("cuando te acerques").desde,
  repite: clip("repite").desde,
  recuerda: clip("recuerda").desde,
  final: clip("antes de comenzar").desde,
};
// La pierna de perfil acompaña de "desde la pantorrilla" a "otra pierna"
const RUTA = (hasta: number): Extra => ({
  desde: S.pantorrilla,
  hasta,
  w: 240,
  h: 360,
  lado: DER,
  el: (pos) => (
    <RutaPierna
      desde={S.pantorrilla + 0.1}
      pasos={[
        { t: S.pantorrilla, modo: "pantorrilla" },
        { t: at("al llegar").start, modo: "rodilla" },
        { t: at("luego").start, modo: "muslo" },
        { t: at("disminuye").start, modo: "ingle" },
        { t: at("otra pierna").start, modo: "otra" },
      ]}
      style={pos}
    />
  ),
});

const SECCIONES: Seccion[] = [
  // "Antes de utilizar el Luma Body, prepara ambas piernas con un masaje manual suave."
  {
    nombre: "Orden",
    desde: S.luma,
    hasta: S.aceite,
    extras: [
      { desde: S.luma + 0.1, w: 300, h: 190, lado: DER, el: (pos) => <Orden at={S.luma + 0.1} luma={at("luma").start} manual={at("masaje").start} style={pos} /> },
      { desde: at("ambas").start, w: 300, h: 110, escala: 0.95, lado: IZQ, el: (pos) => <Nota at={at("ambas").start} texto="Ambas piernas" ancho={300} style={pos} /> },
    ],
  },
  // "Comienza aplicando suficiente aceite desde la pantorrilla…"
  {
    nombre: "Aceite",
    desde: S.aceite,
    hasta: S.pantorrilla,
    paso: true,
    extras: [
      { desde: S.aceite + 0.05, w: 300, h: 300, lado: DER, el: (pos) => <GotaZona3D desde={S.aceite + 0.05} cae={at("aceite").start} desliza={999} ancho={300} alto={300} style={pos} /> },
    ],
  },
  // "…y distribúyelo con movimientos ascendentes, desde encima del tobillo hasta llegar justo antes de la parte
  // posterior de la rodilla." (congelado con la pizarra en "hasta llegar")
  { nombre: "Pantorrilla", desde: S.pantorrilla, hasta: S.rodilla, paso: true, extras: [RUTA(clip("hasta llegar").desde)] },
  // "Al llegar a esta zona, realiza unos movimientos circulares muy suaves, sin presionar directamente ni causar molestia."
  {
    nombre: "Rodilla",
    desde: S.rodilla,
    hasta: S.muslo,
    paso: true,
    extras: [
      RUTA(S.muslo),
      {
        desde: at("sin presionar").start - 0.1,
        w: 280,
        h: 306,
        lado: IZQ,
        el: (pos) => (
          <ConRotulo ancho={280} alto={250} rotulo="SIN PRESIONAR" rotuloAt={at("directamente").start} style={pos}>
            <Medidor3D
              desde={at("sin presionar").start - 0.1}
              niveles={[
                [at("sin presionar").start, 0.45],
                [at("directamente").start, 0.12],
              ]}
              ancho={280}
              alto={250}
              style={{ left: 0, top: 0 }}
            />
          </ConRotulo>
        ),
      },
    ],
  },
  // "Luego, continúa desde encima de la rodilla hacia la parte superior del muslo, deslizando las manos lentamente
  // en dirección ascendente."
  {
    nombre: "Muslo",
    desde: S.muslo,
    hasta: S.ingle,
    paso: true,
    extras: [
      RUTA(S.ingle),
      { desde: at("ascendente").start - 0.4, w: 280, h: 300, lado: IZQ, el: (pos) => <Chevrones3D desde={at("ascendente").start - 0.4} ancho={280} alto={300} style={pos} /> },
    ],
  },
  // "Cuando te acerques a la zona inguinal, disminuye la presión y termina el movimiento antes de llegar a la ingle."
  { nombre: "Ingle", desde: S.ingle, hasta: S.repite, paso: true, extras: [RUTA(clip("disminuye").desde)] },
  // "Repite la misma secuencia en la otra pierna durante aproximadamente 1 o 2 minutos."
  {
    nombre: "Repite",
    desde: S.repite,
    hasta: S.recuerda,
    paso: true,
    extras: [
      RUTA(S.recuerda),
      { desde: at("durante").start - 0.1, w: 260, h: 290, lado: IZQ, el: (pos) => <Cronometro at={at("durante").start - 0.1} hasta={S.recuerda} style={pos} /> },
    ],
  },
  // "Recuerda, esta preparación debe sentirse suave y agradable. No necesitas aplicar fuerza para dejar la piel lista…"
  {
    nombre: "Recuerda",
    desde: S.recuerda,
    hasta: S.final,
    extras: [
      {
        desde: at("suave", S.recuerda).start - 0.1,
        w: 280,
        h: 150,
        lado: DER,
        el: (pos) => (
          <Checks
            items={[
              { texto: "Suave", at: at("suave", S.recuerda).start },
              { texto: "Agradable", at: at("agradable").start },
            ]}
            style={pos}
          />
        ),
      },
      {
        desde: at("no necesitas").start - 0.1,
        w: 280,
        h: 306,
        lado: IZQ,
        el: (pos) => (
          <ConRotulo ancho={280} alto={250} rotulo="SIN FUERZA" rotuloAt={at("fuerza").start} style={pos}>
            <Medidor3D
              desde={at("no necesitas").start - 0.1}
              niveles={[[at("no necesitas").start, 0.14]]}
              tacha={at("fuerza").start}
              ancho={280}
              alto={250}
              style={{ left: 0, top: 0 }}
            />
          </ConRotulo>
        ),
      },
    ],
  },
];

const TARJ = (t: number) => progresoTarjeta(TARJETAS, t);
// Lado libre en cada toma (la cabeza se mueve mucho al inclinarse; comprobado con src/comp_piernas/data/caras.json:
// la columna queda siempre fuera de la caja de la cara)
const LIBRE: Record<string, Lado | "ambos"> = {
  ahora: DER,
  "antes de utilizar": IZQ,
  "prepara ambas": IZQ,
  comienza: DER,
  "desde la pantorrilla": IZQ,
  "y distribuyelo": IZQ,
  "desde encima del tobillo": DER,
  "hasta llegar": DER,
  "al llegar": DER,
  "sin presionar": DER,
  luego: DER,
  deslizando: DER,
  "cuando te acerques": DER,
  disminuye: DER,
  repite: DER,
  recuerda: DER,
  "no necesitas": DER,
  "antes de comenzar": IZQ,
};
const libreEn = (t: number) => {
  const i = clips.reduce((acc, c, j) => (t >= c.outStart ? j : acc), 0);
  return LIBRE[clips[i].frase] ?? "ambos";
};
const SeccionComp: React.FC<{ s: Seccion }> = ({ s }) => {
  const { t } = useT();
  const fijos: Elem[] = s.paso ? [{ w: 300, h: 62, render: (st) => <PildoraPaso pasos={PASOS} style={st} /> }] : [];
  const extras: Elem[] = s.extras
    .filter((e) => t >= e.desde - 0.05 && t < (e.hasta ?? s.hasta))
    .map((e) => ({ w: e.w ?? 300, h: e.h, escala: e.escala, lado: e.lado, render: e.el }));
  return <ColumnasLibres fijos={fijos} extras={extras} libre={libreEn(t)} abajo={ABAJO} />;
};

// ---------- Subtítulos de lectura (§10.18) ----------
const sub = (frase: string, texto: string, tipo?: "si" | "no", despues = 0): ItemSubtitulo => {
  const desde = at(frase, despues).start;
  return { desde, hasta: desde + lectura(texto), texto, tipo };
};
const SUBS: ItemSubtitulo[] = [
  sub("y distribuyelo", "Con movimientos hacia arriba"),
  sub("sin presionar", "Sin presionar ni causar molestia"),
  sub("lentamente", "Lento y hacia arriba"),
  sub("repite", "Repite en la otra pierna"),
  sub("no necesitas", "No necesitas aplicar fuerza", "si"),
];

// ---------- Pizarras sobre los congelados ----------
const PZ_RODILLA = clip("hasta llegar");
const PZ_INGLE = clip("disminuye");
const Pizarras: React.FC = () => (
  <>
    {/* "desde encima del tobillo hasta llegar justo antes de la parte posterior de la rodilla" */}
    <Pizarra
      desde={PZ_RODILLA.desde}
      hasta={PZ_RODILLA.hasta}
      foco={{ cx: 630, cy: 1170, rx: 250, ry: 270 }}
      trazos={[
        { tipo: "flecha", pts: [[712, 1330], [636, 1200], [562, 1078]], at: PZ_RODILLA.desde + 0.25, dur: 0.6 },
        { tipo: "banda", pts: [[502, 1084], [596, 1030]], at: at("antes", PZ_RODILLA.desde).start, ancho: 16 },
        { tipo: "etiqueta", x: 860, y: 1450, texto: "Desde el tobillo", at: PZ_RODILLA.desde + 0.2, ancla: "centro" },
        { tipo: "etiqueta", x: 800, y: 1010, texto: "Hasta antes de la rodilla", at: at("antes", PZ_RODILLA.desde).start + 0.1, ancla: "centro" },
      ]}
    />
    {/* "disminuye la presión y termina el movimiento antes de llegar a la ingle" */}
    <Pizarra
      desde={PZ_INGLE.desde}
      hasta={PZ_INGLE.hasta}
      foco={{ cx: 490, cy: 950, rx: 280, ry: 200 }}
      trazos={[
        { tipo: "flecha", pts: [[640, 918], [530, 946], [430, 972]], at: PZ_INGLE.desde + 0.2, dur: 0.6 },
        { tipo: "banda", pts: [[384, 916], [416, 1034]], at: at("termina").start, ancho: 16 },
        { tipo: "etiqueta", x: 660, y: 790, texto: "Menos presión", at: at("presión", PZ_INGLE.desde).start, ancla: "centro" },
        { tipo: "etiqueta", x: 340, y: 1130, texto: "Termina antes de la ingle", at: at("termina").start + 0.1, ancla: "centro", tono: "no" },
      ]}
    />
  </>
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
          { t: PZ_RODILLA.desde, color: "#FFFFFF", max: 0.7 },
          { t: PZ_INGLE.desde, color: "#FFFFFF", max: 0.7 },
          { t: S.final, color: COLORS.durazno, max: 0.55 },
        ]}
      />
    </>
  );
};

// ---------- Cámara ----------
const z = (frase: string, z0: number, z1: number, ox: number, oy: number): Zoom => ({ ...clip(frase), z0, z1, ox, oy });
const ZOOMS: Zoom[] = [
  z("antes de utilizar", 1.0, 1.1, 640, 1250),
  z("desde encima del tobillo", 1.0, 1.12, 640, 1250),
  z("luego", 1.0, 1.1, 560, 1000),
  z("recuerda", 1.08, 1.0, 560, 1100),
];
const WHIPS = ["y distribuyelo", "luego", "recuerda"].map((f) => clip(f).desde);

// ---------- Efectos (estilo.md §10.14) ----------
const ef = (nombre: string, t: number, src: string, vol = 0.22, dur?: number): Efecto => ({ nombre, t, src, vol, dur });
const EFECTOS: Efecto[] = [
  ef("tarjeta", 0.1, "tarjeta", 0.22),
  ef("título · whoosh", 0.2, "whoosh", 0.22),
  ef("orden · tarjeta", S.luma + 0.1, "tarjeta", 0.2),
  ef("luma · pop", at("luma").start, "pop", 0.18),
  ef("ambas · pop", at("ambas").start, "pop", 0.16),
  ef("manual · brillo", at("masaje").start, "brillo", 0.18),
  ef("paso 1 · swish", S.aceite, "swish", 0.2),
  ef("gota · pop", at("aceite").start + 0.42, "pop", 0.2),
  ef("ruta · tarjeta", S.pantorrilla + 0.1, "tarjeta", 0.18),
  ...WHIPS.map((w, i) => ef(`barrido ${i} · whoosh`, w - 0.2, "whoosh", 0.18)),
  ef("congela 1 · obturador", PZ_RODILLA.desde, "obturador", 0.24),
  ef("tope 1 · tachado", at("antes", PZ_RODILLA.desde).start + 0.1, "tachado", 0.18),
  ef("paso 3 · swish", S.rodilla, "swish", 0.2),
  ef("medidor · tarjeta", at("sin presionar").start - 0.1, "tarjeta", 0.18),
  ef("baja · blips", at("directamente").start, "blips", 0.14, 0.8),
  ef("paso 4 · swish", S.muslo, "swish", 0.2),
  ef("chevrones · subida", at("ascendente").start - 0.4, "subida", 0.16),
  ef("congela 2 · obturador", PZ_INGLE.desde, "obturador", 0.24),
  ef("tope 2 · tachado", at("termina").start + 0.1, "tachado", 0.18),
  ef("paso 5 · swish", S.repite, "swish", 0.18),
  ef("cronómetro · tictac", at("durante").start, "tictac", 0.16, 1.6),
  ef("suave · pop", at("suave", S.recuerda).start, "pop", 0.16),
  ef("agradable · pop", at("agradable").start, "pop", 0.16),
  ef("fuerza · tachado", at("fuerza").start + 0.1, "tachado", 0.2),
  ef("final · campanita", S.final + 0.1, "campanita", 0.16),
];

// Voz en off a −25,1 LUFS (sin tocar): música y efectos ×0,37 para quedar ~16 dB por debajo.
const NIVEL = 0.37;

export const CompPiernasVideo: React.FC = () => (
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

export const CompPiernas = () => (
  <Composition
    id="PreparacionPiernas"
    component={CompPiernasVideo}
    durationInFrames={Math.ceil(TOTAL * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
