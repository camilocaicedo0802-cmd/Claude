import React from "react";
import { Composition } from "remotion";
import { COLORS, FONTS, VIDEO } from "../brand";
import { DatosCaras, useCaras, zonasEn } from "../rutinas/Caras";
import { Efecto } from "../rutinas/Rutina";
import { useT } from "../rutinas/util";
import { Elem, Lado } from "../dia6/Maqueta";
import { Zoom } from "../dia7/Base7";
import { Base9, progresoTarjeta, Tarjeta } from "./Base9";
import { ajustar9, Columnas9 } from "./Maqueta9";
import caras from "./data/caras.json";
import clips from "./data/clips.json";
import mosaicos from "./data/mosaicos.json";
import {
  Alterna,
  Capitulo,
  Destellos,
  Interruptor,
  Mosaico,
  Movimiento,
  Nota,
  Pizarra,
  Ruta,
  SOMBRA9,
  TituloCapitulo,
  TRAMOS9,
} from "./Graficos";
import {
  Chevrones3D,
  ConRotulo,
  Espiral3D,
  GotaZona3D,
  Medalla3D,
  Medidor3D,
  RelojArena3D,
  Rompecabezas3D,
  TarjetasReloj3D,
  Torso3D,
} from "./Objetos3D";
import { at, DURATION, TOTAL, WORDS } from "./timing";

// Reto de 21 días · Vídeo 9 "Rutina integrada" (voz en off + tomas del crudo, scripts/dia9/montar.py).
// Cada gráfico nace de su frase. Para no repetir los días anteriores: mosaico 2×2 de las cuatro zonas que se abre en
// "una sola rutina", tarjeta de capítulo (la toma se encoge y el capítulo entra en el margen, con la barra de los 5
// tramos), barridos entre tomas, pizarra de análisis sobre fotogramas congelados (líneas en el muslo, ombligo, codo y
// axila), pantalla partida vertical en "alternando ambos lados", notas claras y objetos 3D nuevos.

const FIN = TOTAL + 1;
const clip = (frase: string) => {
  const i = clips.findIndex((c) => c.frase === frase);
  if (i < 0) throw new Error(`Toma no encontrada: ${frase}`);
  const fin = i + 1 < clips.length ? clips[i + 1].outStart : TOTAL;
  return { desde: clips[i].outStart, hasta: fin };
};
const IZQ: Lado = "izq";
const DER: Lado = "der";

// ---------- Tomas sin cabeza ----------
// Primeros planos (sin cara): una cabeza ficticia arriba en el centro, así las columnas quedan a los dos lados del
// cuerpo. Pantalla partida (dos cabezas): no se colocan columnas (solo la superposición de Alterna).
const PRIMEROS_PLANOS = ["aplica", "divide", "bajando"].map(clip);
const PARTIDA = clip("haz círculos");
const ajustarCaras = (d: DatosCaras): DatosCaras => ({
  ...d,
  caras: d.caras.map((c) => {
    const s = (c[0] as number) / 30;
    return PRIMEROS_PLANOS.some((q) => s >= q.desde - 0.1 && s < q.hasta + 0.1) ? [c[0], 400, -300, 280, 100] : c;
  }),
});

// ---------- Tarjetas de capítulo (la toma se encoge) y sus títulos ----------
const TARJETAS: Tarjeta[] = [
  { desde: at("una sola").start, hasta: clip("que vas").desde },
  { desde: clip("empezamos").desde, hasta: clip("empezamos").desde + 2.05 },
  { desde: clip("continúa").desde, hasta: clip("continúa").desde + 2.2 },
  { desde: clip("trabaja").desde, hasta: clip("trabaja").desde + 2.1 },
  { desde: clip("finaliza").desde, hasta: clip("finaliza").desde + 2.05 },
  { desde: at("tu rutina").start, hasta: at("para trabajar").start + 0.5 },
];
const CAPITULOS: Capitulo[] = [
  { desde: at("una sola").start, kicker: "DÍA 9 · 15 MIN", titulo: "rutina integrada" },
  { desde: clip("aplica").desde, numero: "1", kicker: "1 MINUTO", titulo: "preparación", tramo: 0 },
  { desde: clip("empezamos").desde, numero: "2", kicker: "3 MIN EN CADA PIERNA", titulo: "piernas", tramo: 1 },
  { desde: clip("continúa").desde, numero: "3", kicker: "Y LATERALES · 4 MIN", titulo: "abdomen", tramo: 2 },
  { desde: clip("trabaja").desde, numero: "4", kicker: "3 MINUTOS", titulo: "glúteos", tramo: 3 },
  { desde: clip("finaliza").desde, numero: "5", kicker: "30 S EN CADA BRAZO", titulo: "brazos", tramo: 4 },
  { desde: at("tu rutina").start, kicker: "15 MINUTOS", titulo: "rutina completa", tramo: "todos", cuenta: at("15").start },
];

// ---------- Secciones y recursos en las columnas ----------
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
  paso?: number;
  /** Lado de la píldora del paso (por defecto, izquierda); en los brazos depende de hacia dónde extiende el brazo. */
  pasoLado?: (t: number) => Lado;
  extras: Extra[];
};

const obj = (
  t0: number,
  el: (pos: React.CSSProperties) => React.ReactNode,
  hasta?: number,
  lado: Lado = DER,
  h = 300,
  w = 300,
): Extra => ({ desde: t0, hasta, w, h, escala: 1, lado, el });
const nota = (t0: number, texto: string, tipo: "si" | "no" = "si", hasta?: number, lado: Lado = IZQ, h = 120): Extra => ({
  desde: t0,
  hasta,
  w: 300,
  h,
  escala: 0.95,
  lado,
  el: (pos) => <Nota at={t0} texto={texto} tipo={tipo} ancho={300} style={pos} />,
});

const S = {
  intro: 0,
  prep: clip("aplica").desde,
  piernas: clip("empezamos").desde,
  abdomen: clip("continúa").desde,
  gluteos: clip("trabaja").desde,
  brazos: clip("finaliza").desde,
  cierre: clip("y listo").desde,
};

const SECCIONES: Seccion[] = [
  // "Hoy integraremos diferentes zonas en una sola rutina." → el rompecabezas encaja en "rutina"
  {
    nombre: "Intro",
    desde: S.intro,
    hasta: S.prep,
    extras: [
      obj(at("una sola").start + 0.1, (pos) => (
        <Rompecabezas3D desde={at("una sola").start + 0.1} encaja={at("rutina").start + 0.15} ancho={300} alto={300} style={pos} />
      )),
    ],
  },
  // "Aplica el aceite únicamente en la zona que vas a trabajar para conservar el deslizamiento."
  {
    nombre: "Preparación",
    desde: S.prep,
    hasta: S.piernas,
    paso: 0,
    extras: [
      obj(at("aceite").start - 0.1, (pos) => (
        <GotaZona3D desde={at("aceite").start - 0.1} cae={at("aceite").start} desliza={at("deslizamiento").start} ancho={300} alto={300} style={pos} />
      )),
      nota(at("zona").start, "Solo en la zona que vas a trabajar"),
    ],
  },
  // "Empezamos con 3 minutos en cada pierna. Divide la zona en líneas y trabaja siempre con movimientos ascendentes y
  // continuos. Realiza líneas ascendentes desde la parte baja hacia arriba del muslo."
  {
    nombre: "Piernas",
    desde: S.piernas,
    hasta: S.abdomen,
    paso: 1,
    extras: [
      obj(
        S.piernas + 0.2,
        (pos) => (
          <ConRotulo ancho={280} alto={300} rotulo="3 MIN · CADA PIERNA" rotuloAt={at("minutos", S.piernas).start} style={pos}>
            <RelojArena3D desde={S.piernas + 0.2} gira={at("3|tres", S.piernas).start} ancho={280} alto={300} style={{ left: 0, top: 0 }} />
          </ConRotulo>
        ),
        clip("divide").desde,
        IZQ,
        356,
        280,
      ),
      {
        desde: at("ascendentes").start - 0.05,
        hasta: clip("realiza líneas").desde,
        w: 300,
        h: 190,
        lado: DER,
        el: (pos) => <Movimiento sube={at("ascendentes").start} continuo={at("continuos").start} style={pos} />,
      },
      obj(clip("realiza líneas").desde + 0.1, (pos) => (
        <Chevrones3D desde={clip("realiza líneas").desde + 0.1} ancho={280} alto={300} style={pos} />
      ), undefined, DER, 300, 280),
      nota(at("parte baja").start, "De la parte baja hacia arriba del muslo", "si", undefined, DER),
    ],
  },
  // "Continúa durante 4 minutos en abdomen y laterales. Mantén una intensidad baja y evita pasar directamente sobre el
  // ombligo. Realiza círculos amplios y movimientos suaves. Movimientos de arrastre desde la espalda hacia la cintura
  // bajando por la ingle."
  {
    nombre: "Abdomen",
    desde: S.abdomen,
    hasta: S.gluteos,
    paso: 2,
    extras: [
      obj(
        S.abdomen + 0.2,
        (pos) => (
          <Torso3D
            desde={S.abdomen + 0.2}
            abdomen={at("abdomen").start}
            laterales={at("laterales").start}
            ombligo={at("evita").start}
            circulos={at("círculos", S.abdomen).start}
            arrastre={at("arrastre").start}
            hasta={S.gluteos}
            ancho={300}
            alto={400}
            style={pos}
          />
        ),
        undefined,
        DER,
        400,
      ),
      obj(
        at("mantén").start + 0.05,
        (pos) => (
          <ConRotulo ancho={280} alto={250} rotulo="INTENSIDAD BAJA" rotuloAt={at("baja", S.abdomen).start} style={pos}>
            <Medidor3D
              desde={at("mantén").start + 0.05}
              niveles={[
                [at("mantén").start, 0.2],
                [at("intensidad", S.abdomen).start, 0.72],
                [at("baja", S.abdomen).start, 0.14],
              ]}
              ancho={280}
              alto={250}
              style={{ left: 0, top: 0 }}
            />
          </ConRotulo>
        ),
        clip("y evita").desde,
        IZQ,
        306,
        280,
      ),
      nota(at("círculos", S.abdomen).start, "Círculos amplios y suaves", "si", clip("movimientos de").desde),
      {
        desde: clip("movimientos de").desde + 0.1,
        w: 300,
        h: 330,
        lado: IZQ,
        el: (pos) => (
          <Ruta
            at={clip("movimientos de").desde + 0.1}
            pasos={[
              { texto: "Espalda", at: at("espalda").start },
              { texto: "Cintura", at: at("cintura").start },
              { texto: "Ingle", at: at("ingle").start },
            ]}
            style={pos}
          />
        ),
      },
    ],
  },
  // "Trabaja los glúteos durante 3 minutos con movimientos circulares y barridos ascendentes. Haz círculos amplios
  // alternando ambos lados."
  {
    nombre: "Glúteos",
    desde: S.gluteos,
    hasta: PARTIDA.desde,
    paso: 3,
    extras: [
      obj(
        S.gluteos + 0.25,
        (pos) => (
          <ConRotulo ancho={280} alto={300} rotulo="3 MINUTOS" rotuloAt={at("minutos", S.gluteos).start} style={pos}>
            <RelojArena3D desde={S.gluteos + 0.25} gira={at("3|tres", S.gluteos).start} ancho={280} alto={300} style={{ left: 0, top: 0 }} />
          </ConRotulo>
        ),
        at("movimientos", S.gluteos).start,
        DER,
        356,
        280,
      ),
      obj(at("movimientos", S.gluteos).start, (pos) => (
        <ConRotulo ancho={300} alto={300} rotulo={undefined} style={pos}>
          <Espiral3D desde={at("movimientos", S.gluteos).start} barre={at("barridos").start} ancho={300} alto={300} style={{ left: 0, top: 0 }} />
        </ConRotulo>
      )),
      nota(at("barridos").start, "Barridos ascendentes", "si", undefined, DER, 100),
    ],
  },
  // Pantalla partida (sin columnas): Alterna
  { nombre: "Partida", desde: PARTIDA.desde, hasta: S.brazos, extras: [] },
  // "Finaliza con 30 segundos en cada brazo. Los brazos puedes hacerlo solo con tus manos o si lo vas a hacer con el
  // dispositivo, recuerda no pasar sobre las articulaciones."
  {
    nombre: "Brazos",
    desde: S.brazos,
    hasta: S.cierre,
    paso: 4,
    pasoLado: (t) => (t < clip("los brazos").desde ? IZQ : DER),
    extras: [
      obj(
        S.brazos + 0.2,
        (pos) => (
          <ConRotulo ancho={300} alto={260} rotulo="30 S · CADA BRAZO" rotuloAt={at("cada", S.brazos).start} style={pos}>
            <TarjetasReloj3D desde={S.brazos + 0.2} gira={at("30|treinta").start} ancho={300} alto={260} style={{ left: 0, top: 0 }} />
          </ConRotulo>
        ),
        clip("los brazos").desde,
        IZQ,
        316,
      ),
      {
        desde: at("puedes", S.brazos).start,
        hasta: clip("recuerda no").desde,
        w: 300,
        h: 150,
        lado: DER,
        el: (pos) => (
          <Interruptor at={at("puedes", S.brazos).start} manos={at("manos").start} dispositivo={at("dispositivo").start} style={pos} />
        ),
      },
    ],
  },
  // "¡Y listo! Tu rutina completa de 15 minutos para trabajar diferentes zonas sin necesidad de utilizar una
  // intensidad dolorosa." (cuadro: "Cierre: apaga y limpia el dispositivo")
  {
    nombre: "Cierre",
    desde: S.cierre,
    hasta: FIN,
    extras: [
      obj(at("15").start - 0.15, (pos) => (
        <Medalla3D desde={at("15").start - 0.15} llega={at("15").start} ancho={300} alto={300} style={pos} />
      ), at("para trabajar").start),
      obj(
        at("sin necesidad").start,
        (pos) => (
          <ConRotulo ancho={280} alto={250} rotulo="SIN DOLOR" rotuloAt={at("dolorosa").start} style={pos}>
            <Medidor3D
              desde={at("sin necesidad").start}
              niveles={[[at("sin necesidad").start, 0.14]]}
              tacha={at("dolorosa").start}
              ancho={280}
              alto={250}
              style={{ left: 0, top: 0 }}
            />
          </ConRotulo>
        ),
        undefined,
        DER,
        306,
        280,
      ),
      nota(at("utilizar").start, "Al terminar: apaga y limpia el equipo", "si", undefined, DER),
    ],
  },
];

/** Paso actual (fuera de la tarjeta): píldora con el número y los 5 puntos de la rutina. */
const Paso: React.FC<{ paso: number; at: number; style: React.CSSProperties }> = ({ paso, at: atSec, style }) => {
  const { t } = useT();
  const k = Math.min(1, Math.max(0, (t - atSec) / 0.3));
  return (
    <div style={{ position: "absolute", width: 300, ...style, opacity: k }}>
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 12,
          background: "rgba(245,240,236,0.94)",
          border: `3px solid ${COLORS.durazno}`,
          borderRadius: 30,
          padding: "8px 16px 8px 8px",
          boxShadow: SOMBRA9,
        }}
      >
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: 20,
            background: COLORS.salvia,
            color: COLORS.marfil,
            fontFamily: FONTS.body,
            fontWeight: 700,
            fontSize: 22,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {paso + 1}
        </div>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 22, letterSpacing: "0.14em", color: COLORS.petroleo }}>
          {TRAMOS9[paso].nombre.toUpperCase()}
        </div>
        <div style={{ display: "flex", gap: 5 }}>
          {TRAMOS9.map((_, i) => (
            <div
              key={i}
              style={{
                width: 10,
                height: 10,
                borderRadius: 5,
                background: i <= paso ? COLORS.salvia : "rgba(69,89,90,.22)",
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const TARJ = (t: number) => progresoTarjeta(TARJETAS, t);
const useElementos = (s: Seccion): Elem[] => {
  const caras = useCaras();
  const { t } = useT();
  const { actual } = zonasEn(caras, t, s.desde, s.hasta);
  const fijos: Elem[] = [];
  // Píldora del paso cuando la tarjeta se ha cerrado
  const fin = TARJETAS.find((c) => c.hasta > s.desde && c.desde < s.hasta)?.hasta ?? s.desde;
  if (s.paso !== undefined && t >= fin - 0.1)
    fijos.push({ w: 300, h: 58, lado: s.pasoLado?.(t) ?? IZQ, render: (st) => <Paso paso={s.paso!} at={fin - 0.1} style={st} /> });
  const lista: Elem[] = [];
  for (const e of s.extras)
    if (t >= e.desde - 0.05 && t < (e.hasta ?? s.hasta))
      lista.push({ w: e.w ?? 300, h: e.h, escala: e.escala, lado: e.lado, render: e.el });
  return ajustar9(actual, fijos, lista);
};
const SeccionComp: React.FC<{ s: Seccion }> = ({ s }) => {
  const elementos = useElementos(s);
  return <Columnas9 desde={s.desde} hasta={s.hasta} elementos={elementos} />;
};

// ---------- Pizarras sobre los congelados ----------
const PZ_LINEAS = clip("divide");
const PZ_OMBLIGO = clip("y evita");
const PZ_BRAZO = clip("recuerda no");
const lineas = at("líneas").start;
const Pizarras: React.FC = () => (
  <>
    {/* "Divide la zona en líneas y trabaja siempre con movimientos ascendentes" (muslo izquierdo de la imagen) */}
    <Pizarra
      desde={PZ_LINEAS.desde}
      hasta={PZ_LINEAS.hasta}
      foco={{ cx: 265, cy: 1270, rx: 230, ry: 260 }}
      trazos={[
        { tipo: "flecha", pts: [[170, 1420], [180, 1150]], at: lineas - 0.25, dur: 0.35 },
        { tipo: "flecha", pts: [[262, 1430], [268, 1135]], at: lineas, dur: 0.35 },
        { tipo: "flecha", pts: [[350, 1420], [352, 1145]], at: lineas + 0.25, dur: 0.35 },
        { tipo: "etiqueta", x: 520, y: 1090, texto: "Divide en líneas", at: at("divide").start + 0.15, ancla: "izq" },
        { tipo: "etiqueta", x: 520, y: 1200, texto: "Siempre hacia arriba", at: at("trabaja", PZ_LINEAS.desde).start, ancla: "izq" },
      ]}
    />
    {/* "Evita pasar directamente sobre el ombligo" */}
    <Pizarra
      desde={PZ_OMBLIGO.desde}
      hasta={PZ_OMBLIGO.hasta}
      foco={{ cx: 470, cy: 930, rx: 270, ry: 230 }}
      trazos={[
        { tipo: "prohibido", x: 470, y: 924, r: 64, at: at("evita").start },
        { tipo: "etiqueta", x: 610, y: 1110, texto: "Evita el ombligo", at: at("ombligo").start - 0.25, ancla: "izq", tono: "no" },
      ]}
    />
    {/* "Recuerda no pasar sobre las articulaciones" (cuadro: desde encima del codo hacia el hombro, evitando axila) */}
    <Pizarra
      desde={PZ_BRAZO.desde}
      hasta={PZ_BRAZO.hasta}
      foco={{ cx: 740, cy: 620, rx: 330, ry: 170 }}
      trazos={[
        { tipo: "banda", pts: [[860, 598], [640, 600]], at: at("recuerda", PZ_BRAZO.desde).start, ancho: 70 },
        { tipo: "flecha", pts: [[860, 520], [660, 520]], at: at("recuerda", PZ_BRAZO.desde).start + 0.2, dur: 0.4, color: COLORS.marfil, ancho: 9 },
        { tipo: "cruz", x: 945, y: 596, r: 46, at: at("sobre", PZ_BRAZO.desde).start },
        { tipo: "cruz", x: 560, y: 665, r: 40, at: at("articulaciones").start },
        { tipo: "etiqueta", x: 945, y: 690, texto: "Codo", at: at("sobre", PZ_BRAZO.desde).start + 0.1, ancla: "centro", tono: "no" },
        { tipo: "etiqueta", x: 560, y: 755, texto: "Axila", at: at("articulaciones").start + 0.1, ancla: "centro", tono: "no" },
        { tipo: "etiqueta", x: 830, y: 450, texto: "Del codo al hombro", at: at("recuerda", PZ_BRAZO.desde).start + 0.4, ancla: "centro" },
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
      <Alterna
        desde={PARTIDA.desde}
        hasta={PARTIDA.hasta}
        cambios={[at("alternando").start, at("ambos").start, at("lados").start]}
        centros={[
          [235, 1035],
          [795, 1045],
        ]}
      />
    </>
  );
};

const Fuera: React.FC = () => {
  const { t } = useT();
  const mi = mosaicos.intro;
  const mc = mosaicos.cierre;
  return (
    <>
      <TituloCapitulo caps={CAPITULOS} p={TARJ(t)} />
      {/* "Hoy integraremos diferentes zonas en una sola rutina": 4 celdas → se abren en "una sola" */}
      <Mosaico
        src="dia9/mosaico_intro.mp4"
        desde={mi.desde}
        hasta={mi.hasta}
        entra={[0, 0.25, 0.5, 0.75]}
        rotulo={[at("diferentes").start, at("diferentes").start + 0.3, at("zonas").start, at("zonas").start + 0.25]}
        abre={at("una sola").start}
      />
      {/* "para trabajar diferentes zonas": las 4 celdas vuelven, cada una con su ✓ */}
      <Mosaico
        src="dia9/mosaico_cierre.mp4"
        desde={mc.desde}
        hasta={mc.hasta}
        entra={[mc.desde, mc.desde + 0.12, mc.desde + 0.24, mc.desde + 0.36]}
        rotulo={[at("trabajar", mc.desde - 0.1).start, at("diferentes", mc.desde).start, at("diferentes", mc.desde).start + 0.3, at("zonas", mc.desde).start]}
        check
        abre={at("sin necesidad").start}
      />
      <Destellos
        en={[
          { t: PZ_LINEAS.desde, color: "#FFFFFF", max: 0.7 },
          { t: PZ_OMBLIGO.desde, color: "#FFFFFF", max: 0.7 },
          { t: PZ_BRAZO.desde, color: "#FFFFFF", max: 0.7 },
          { t: at("y listo").start, color: COLORS.durazno, max: 0.55 },
        ]}
      />
    </>
  );
};

// ---------- Cámara ----------
const z = (frase: string, z0: number, z1: number, ox: number, oy: number): Zoom => ({ ...clip(frase), z0, z1, ox, oy });
const ZOOMS: Zoom[] = [
  z("hacia arriba", 1.0, 1.18, 450, 1200),
  z("realiza círculos", 1.0, 1.12, 470, 950),
  z("movimientos de", 1.0, 1.07, 540, 1000),
  z("y listo", 1.08, 1.0, 540, 900),
  z("para trabajar", 1.0, 1.08, 500, 800),
];
const WHIPS = ["movimientos ascendentes", "hacia arriba", "laterales", "hacia la cintura", "barridos", "o si"].map((f) => clip(f).desde);

// ---------- Efectos (estilo.md §10.14: según lo que hace el gráfico, sin apilarlos) ----------
const ef = (nombre: string, t: number, src: string, vol = 0.22, dur?: number): Efecto => ({ nombre, t, src, vol, dur });
const EFECTOS: Efecto[] = [
  ef("mosaico · tarjeta", 0.05, "tarjeta", 0.22),
  ef("zonas · blips", at("diferentes").start, "blips", 0.18, 1),
  ef("se abre · whoosh", at("una sola").start - 0.15, "whoosh", 0.24),
  ef("encaja · pop", at("rutina").start + 0.5, "pop", 0.22),
  ef("cap 1 · swish", S.prep, "swish", 0.22),
  ef("gota · pop", at("aceite").start + 0.42, "pop", 0.2),
  ef("zona · brillo", at("zona").start, "brillo", 0.18),
  ef("desliza · swish", at("deslizamiento").start, "swish", 0.18),
  ef("cap 2 · whoosh", S.piernas - 0.2, "whoosh", 0.24),
  ef("reloj · tictac", at("3|tres", S.piernas).start, "tictac", 0.18, 1.4),
  ef("congela · obturador", PZ_LINEAS.desde, "obturador", 0.24),
  ef("líneas · escalones", lineas - 0.25, "escalones", 0.18),
  ...WHIPS.map((w, i) => ef(`barrido ${i} · whoosh`, w - 0.2, "whoosh", 0.2)),
  ef("ascendentes · swish", at("ascendentes").start, "swish", 0.2),
  ef("continuos · pop", at("continuos").start, "pop", 0.2),
  ef("chevrones · subida", clip("realiza líneas").desde + 0.1, "subida", 0.16),
  ef("parte baja · pop", at("parte baja").start, "pop", 0.2),
  ef("cap 3 · whoosh", S.abdomen - 0.2, "whoosh", 0.24),
  ef("abdomen · brillo", at("abdomen").start, "brillo", 0.18),
  ef("medidor · tarjeta", at("mantén").start + 0.05, "tarjeta", 0.22),
  ef("baja · blips", at("baja", S.abdomen).start, "blips", 0.16, 0.8),
  ef("congela · obturador 2", PZ_OMBLIGO.desde, "obturador", 0.24),
  ef("ombligo · tachado", at("evita").start + 0.12, "tachado", 0.22),
  ef("círculos · swish", at("círculos", S.abdomen).start, "swish", 0.2),
  ef("ruta · tarjeta", clip("movimientos de").desde + 0.1, "tarjeta", 0.2),
  ef("espalda · pop", at("espalda").start, "pop", 0.18),
  ef("cintura · pop", at("cintura").start, "pop", 0.18),
  ef("ingle · pop", at("ingle").start, "pop", 0.18),
  ef("cap 4 · whoosh", S.gluteos - 0.2, "whoosh", 0.24),
  ef("reloj 2 · tictac", at("3|tres", S.gluteos).start, "tictac", 0.18, 1.4),
  ef("espiral · swish", at("movimientos", S.gluteos).start, "swish", 0.2),
  ef("partida · tarjeta", PARTIDA.desde, "tarjeta", 0.22),
  ef("alternando · swish", at("alternando").start, "swish", 0.18),
  ef("ambos · pop", at("ambos").start, "pop", 0.18),
  ef("cap 5 · whoosh", S.brazos - 0.2, "whoosh", 0.24),
  ef("30 s · tarjeta", at("30|treinta").start + 0.05, "tarjeta", 0.22),
  ef("interruptor · pop", at("puedes", S.brazos).start, "pop", 0.2),
  ef("equipo · swish", at("dispositivo").start, "swish", 0.18),
  ef("congela · obturador 3", PZ_BRAZO.desde, "obturador", 0.24),
  ef("codo · tachado", at("sobre", PZ_BRAZO.desde).start + 0.12, "tachado", 0.22),
  ef("axila · pop", at("articulaciones").start, "pop", 0.2),
  ef("listo · campanita", at("y listo").start + 0.05, "campanita", 0.16),
  ef("cap final · whoosh", at("tu rutina").start - 0.2, "whoosh", 0.22),
  ef("15 · impacto", at("15").start + 0.25, "impacto", 0.22),
  ef("mosaico cierre · escalones", mosaicos.cierre.desde + 0.05, "escalones", 0.18),
  ef("se abre 2 · whoosh", at("sin necesidad").start - 0.15, "whoosh", 0.2),
  ef("dolorosa · tachado", at("dolorosa").start + 0.1, "tachado", 0.22),
];

// Voz en off a −25,8 LUFS (como la de los días 6 y 7): música y efectos bajan ≈ −9 dB, la voz no se toca.
const NIVEL = 0.34;

export const Dia9Video: React.FC = () => (
  <Base9
    caras={ajustarCaras({ ...(caras as DatosCaras), cortes: clips.map((c) => c.outStart) })}
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
  </Base9>
);

export const Dia9 = () => (
  <Composition
    id="Dia9"
    component={Dia9Video}
    durationInFrames={Math.ceil(TOTAL * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
