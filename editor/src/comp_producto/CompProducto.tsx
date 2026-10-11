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
import { GotaZona3D } from "../dia9/Objetos3D";
import { BaseComp, progresoTarjeta, Tarjeta } from "../comp/BaseComp";
import { ColumnasLibres } from "../comp/MaquetaComp";
import { CapPrep, Niveles, PanelLuma, PasoPrep, PildoraPaso, TituloPrep } from "../comp/Graficos";
import caras from "./data/caras.json";
import clips from "./data/clips.json";
import { at, DURATION, TOTAL, WORDS } from "./timing";

// Vídeo complementario · Cómo funciona el producto (los tres botones del Luma Body). Voz en off sobre los primeros
// planos del equipo en sus manos (crudo B: sin la cara a la vista; su audio era un programa que sonaba de fondo y no
// se usa) y, al final, el aceite y el equipo sobre el abdomen (crudo A). Cada botón se señala sobre el equipo real
// (pizarra en un congelado) y en un panel 2D que reproduce lo que pasa: se enciende, luz roja, barras de calor y de
// succión que suben y bajan con lo que dice la voz.

const FIN = TOTAL + 1;
const CARPETA = "comp_producto";
const FOTOGRAMAS = clips.reduce((n, c) => n + c.frames, 0);
const clip = (frase: string) => {
  const i = clips.findIndex((c) => c.frase === frase);
  if (i < 0) throw new Error(`Toma no encontrada: ${frase}`);
  return { desde: clips[i].outStart, hasta: i + 1 < clips.length ? clips[i + 1].outStart : TOTAL };
};
const IZQ: Lado = "izq";
const DER: Lado = "der";
// Columnas en las esquinas de arriba (bata blanca): el equipo y las manos ocupan el centro desde y ≈ 640
const ABAJO = 660;

// En los primeros planos del crudo B solo asoma la barbilla arriba al centro: esa es la zona de la cara
const enB = (f: number) => clips.some((c) => "b" in c && f >= Math.round(c.outStart * 30) && f < Math.round(c.outStart * 30) + c.frames);
const CARAS: DatosCaras = {
  ...(caras as DatosCaras),
  caras: (caras as DatosCaras).caras.map((c) => (enB(c[0] as number) ? [c[0], 420, -60, 240, 140] : c)),
  cortes: clips.map((c) => c.outStart),
};

// ---------- Tarjetas y pasos ----------
const TARJETAS: Tarjeta[] = [
  { desde: 0.12, hasta: clip("aprendamos").desde },
  { desde: clip("mantiene").desde, hasta: FIN + 2 },
];
const CAPS: CapPrep[] = [
  { desde: 0.12, kicker: "CÓMO FUNCIONA", titulo: "tu Luma Body" },
  { desde: clip("mantiene").desde, kicker: "MÁS ACEITE Y SIEMPRE", titulo: "en movimiento" },
];
const PASOS: PasoPrep[] = [
  { nombre: "Power", at: at("el primero").start },
  { nombre: "Heat", at: at("el segundo").start },
  { nombre: "Succión", at: at("el tercer").start },
  { nombre: "Niveles 1–3", at: at("si es").start },
  { nombre: "Sin dolor", at: at("recuerda").start },
];

// ---------- Estados del panel (lo que dice la voz) ----------
const T = (frase: string, despues = 0) => at(frase, despues).start;
const SUCCION: [number, number][] = [
  [T("regulas"), 1],
  [T("presiones"), 2],
  [T("intensidad", T("presiones")), 3],
  [T("succión", T("presiones")), 4],
  [T("aumentará"), 5],
  [T("comienza", T("si es")), 0],
  [T("1"), 1],
  [T("a", T("1")), 2],
  [T("3"), 3],
  [T("prueba"), 1],
  [T("aumenta"), 2],
  [T("gradualmente"), 3],
  [T("fuerte"), 4],
  [T("baja"), 3],
  [T("intensidad", T("baja")), 2],
];
const PULSA: [number, "power" | "heat" | "presion"][] = [
  [T("una vez"), "power"],
  [T("ajustar"), "heat"],
  [T("intensidad", T("ajustar")), "heat"],
  [T("mayor"), "heat"],
  [T("calor", T("mayor")), "heat"],
  ...SUCCION.filter(([, n]) => n > 0).map(([ts]) => [ts, "presion"] as [number, "presion"]),
];
const panel = (desde: number, hasta: number): Extra => ({
  desde,
  hasta,
  w: 340,
  h: 408,
  lado: DER,
  el: (pos) => (
    <PanelLuma
      at={desde}
      encendido={T("encender")}
      calor={T("enciende")}
      nivelesCalor={[
        [T("ajustar"), 1],
        [T("intensidad", T("ajustar")), 2],
        [T("comodidad"), 3],
        [T("mayor"), 4],
        [T("calor", T("mayor")), 5],
      ]}
      succion={SUCCION}
      pulsa={PULSA}
      resalta={[
        [T("el primero"), T("el segundo"), "power"],
        [T("el segundo"), T("el tercer"), "heat"],
        [T("el tercer"), T("aplica"), "presion"],
      ]}
      ancho={340}
      style={pos}
    />
  ),
});

type Extra = { desde: number; hasta?: number; w?: number; h: number; escala?: number; lado?: Lado; el: (pos: React.CSSProperties) => React.ReactNode };
type Seccion = { nombre: string; desde: number; hasta: number; paso?: boolean; extras: Extra[] };
const S = {
  power: clip("el primero").desde,
  heat: clip("el segundo").desde,
  succion: clip("el tercer").desde,
  niveles: clip("si es").desde,
  prueba: clip("prueba siempre").desde,
  dolor: clip("recuerda").desde,
  baja: clip("si se siente").desde,
  aceite: clip("aplica").desde,
  final: clip("mantiene").desde,
};
const SECCIONES: Seccion[] = [
  // "El primero es el botón de Power. Presiónalo una vez para encender o apagar el dispositivo."
  { nombre: "Power", desde: S.power, hasta: S.heat, paso: true, extras: [panel(S.power, S.heat)] },
  // "El segundo es el botón Heat. Al activarlo, se enciende la luz roja y comienza la función de calor. Puedes ajustar
  // su intensidad según tu comodidad. Entre mayor sea el nivel, más calor sentirás sobre la piel."
  { nombre: "Heat", desde: S.heat, hasta: clip("el tercer").desde, paso: true, extras: [panel(S.heat, clip("el tercer").desde)] },
  // "El tercer botón es el Negative Pressure, con el que regulas el nivel de succión. Cada vez que lo presiones, la
  // intensidad de succión aumentará." (congelado con la pizarra en "el tercer")
  { nombre: "Succión", desde: S.succion, hasta: S.niveles, paso: true, extras: [panel(clip("con el que").desde, S.niveles)] },
  // "Si es tu primera vez utilizando Luma Body, comienza entre los niveles 1 a 3. Prueba siempre desde el nivel más
  // bajo y aumenta gradualmente según lo que tu piel tolere."
  {
    nombre: "Niveles",
    desde: S.niveles,
    hasta: S.dolor,
    paso: true,
    extras: [
      panel(S.niveles, S.dolor),
      { desde: T("primera") - 0.1, w: 300, h: 240, lado: IZQ, el: (pos) => <Niveles at={T("primera") - 0.1} rango={[1, 3]} resalta={T("niveles")} titulo="PRIMERA VEZ" style={pos} /> },
    ],
  },
  // "Recuerda, debes sentir la succión, pero nunca dolor. Si se siente demasiado fuerte, baja la intensidad."
  {
    nombre: "Dolor",
    desde: S.dolor,
    hasta: S.aceite,
    paso: true,
    extras: [
      panel(S.dolor, S.aceite),
      { desde: T("sentir"), w: 300, h: 100, escala: 0.95, lado: IZQ, el: (pos) => <Nota at={T("sentir")} texto="Sentir la succión" ancho={300} style={pos} /> },
      { desde: T("nunca"), w: 300, h: 100, escala: 0.95, lado: IZQ, el: (pos) => <Nota at={T("nunca")} texto="Nunca dolor" tipo="no" ancho={300} style={pos} /> },
      { desde: T("baja"), w: 300, h: 100, escala: 0.95, lado: IZQ, el: (pos) => <Nota at={T("baja")} texto="Baja la intensidad" ancho={300} style={pos} /> },
    ],
  },
  // "Aplica más aceite…"
  {
    nombre: "Aceite",
    desde: S.aceite,
    hasta: S.final,
    extras: [{ desde: S.aceite + 0.05, w: 300, h: 300, lado: DER, el: (pos) => <GotaZona3D desde={S.aceite + 0.05} cae={T("aceite")} desliza={999} ancho={300} alto={300} style={pos} /> }],
  },
];

const TARJ = (t: number) => progresoTarjeta(TARJETAS, t);
const SeccionComp: React.FC<{ s: Seccion }> = ({ s }) => {
  const { t } = useT();
  const fijos: Elem[] = s.paso ? [{ w: 300, h: 62, lado: IZQ, render: (st) => <PildoraPaso pasos={PASOS} style={st} /> }] : [];
  const extras: Elem[] = s.extras
    .filter((e) => t >= e.desde - 0.05 && t < (e.hasta ?? s.hasta))
    .map((e) => ({ w: e.w ?? 300, h: e.h, escala: e.escala, lado: e.lado, render: e.el }));
  // En el plano del aceite (crudo A, ella de cuerpo entero) las columnas pueden bajar más
  return <ColumnasLibres fijos={fijos} extras={extras} libre="ambos" abajo={t >= S.aceite ? 1300 : ABAJO} />;
};

// ---------- Subtítulos de lectura (§10.18) ----------
const sub = (frase: string, texto: string, tipo?: "si" | "no", despues = 0): ItemSubtitulo => {
  const desde = at(frase, despues).start;
  return { desde, hasta: desde + lectura(texto), texto, tipo };
};
const SUBS: ItemSubtitulo[] = [
  sub("presiónalo", "Un toque: enciende o apaga"),
  sub("al activarlo", "Se enciende la luz roja: calor"),
  sub("puedes ajustar", "Ajusta el calor a tu comodidad"),
  sub("cada vez", "Cada toque sube la succión"),
  sub("prueba siempre", "Empieza bajo y sube poco a poco"),
  sub("aplica", "Aplica más aceite"),
];

// ---------- Pizarras sobre el equipo real ----------
const BOT = { heat: { x: 490, y: 895 }, presion: { x: 712, y: 902 }, power: { x: 595, y: 1038 } };
const PZ_TRES = clip("aprendamos");
const PZ_PRESION = clip("el tercer");
const Pizarras: React.FC = () => (
  <>
    {/* "aprendamos a manejar sus tres botones" */}
    <Pizarra
      desde={PZ_TRES.desde}
      hasta={PZ_TRES.hasta}
      foco={{ cx: 600, cy: 960, rx: 300, ry: 260 }}
      trazos={[
        { tipo: "orbita", x: BOT.power.x, y: BOT.power.y, rx: 62, ry: 62, at: PZ_TRES.desde + 0.2 },
        { tipo: "etiqueta", x: BOT.power.x, y: BOT.power.y + 120, texto: "Power", at: PZ_TRES.desde + 0.3, ancla: "centro" },
        { tipo: "orbita", x: BOT.heat.x, y: BOT.heat.y, rx: 64, ry: 64, at: PZ_TRES.desde + 0.7 },
        { tipo: "etiqueta", x: BOT.heat.x - 120, y: BOT.heat.y - 110, texto: "Heat", at: PZ_TRES.desde + 0.8, ancla: "centro" },
        { tipo: "orbita", x: BOT.presion.x, y: BOT.presion.y, rx: 64, ry: 64, at: T("tres") },
        { tipo: "etiqueta", x: BOT.presion.x + 60, y: BOT.presion.y - 120, texto: "Negative pressure", at: T("tres") + 0.1, ancla: "centro" },
      ]}
    />
    {/* "El tercer botón es el Negative Pressure" */}
    <Pizarra
      desde={PZ_PRESION.desde}
      hasta={PZ_PRESION.hasta}
      foco={{ cx: BOT.presion.x, cy: BOT.presion.y, rx: 210, ry: 190 }}
      trazos={[
        { tipo: "orbita", x: BOT.presion.x, y: BOT.presion.y, rx: 64, ry: 64, at: PZ_PRESION.desde + 0.15 },
        { tipo: "etiqueta", x: BOT.presion.x, y: BOT.presion.y - 140, texto: "Negative pressure", at: T("negative"), ancla: "centro" },
        { tipo: "etiqueta", x: BOT.presion.x, y: BOT.presion.y + 140, texto: "Succión", at: T("pressure") + 0.2, ancla: "centro" },
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
          { t: PZ_TRES.desde, color: "#FFFFFF", max: 0.7 },
          { t: PZ_PRESION.desde, color: "#FFFFFF", max: 0.7 },
          { t: S.final, color: COLORS.durazno, max: 0.55 },
        ]}
      />
    </>
  );
};

// ---------- Cámara: acercamiento al equipo, que en el crudo se ve pequeño hasta que lo enciende ----------
const z = (frase: string, z0: number, z1: number, ox: number, oy: number): Zoom => ({ ...clip(frase), z0, z1, ox, oy });
const ZOOMS: Zoom[] = [
  z("el primero", 1.0, 1.25, 560, 900),
  z("presionalo", 1.25, 1.3, 560, 900),
  z("puedes ajustar", 1.0, 1.12, 600, 950),
  z("prueba siempre", 1.0, 1.12, 600, 950),
];
const WHIPS = ["y comienza", "entre mayor", "si es", "recuerda"].map((f) => clip(f).desde);

// ---------- Efectos (estilo.md §10.14) ----------
const ef = (nombre: string, t: number, src: string, vol = 0.22, dur?: number): Efecto => ({ nombre, t, src, vol, dur });
const EFECTOS: Efecto[] = [
  ef("tarjeta", 0.1, "tarjeta", 0.22),
  ef("título · whoosh", 0.2, "whoosh", 0.22),
  ef("congela · obturador", PZ_TRES.desde, "obturador", 0.24),
  ef("botones · blips", PZ_TRES.desde + 0.2, "blips", 0.16, 1.2),
  ef("power · swish", S.power, "swish", 0.2),
  ef("enciende · brillo", T("encender"), "brillo", 0.18),
  ef("heat · swish", S.heat, "swish", 0.2),
  ef("luz roja · pop", T("enciende"), "pop", 0.18),
  ef("calor · escalones", T("ajustar"), "escalones", 0.16),
  ...WHIPS.map((w, i) => ef(`barrido ${i} · whoosh`, w - 0.2, "whoosh", 0.18)),
  ef("congela 2 · obturador", PZ_PRESION.desde, "obturador", 0.24),
  ef("succión · subida", T("presiones"), "subida", 0.16),
  ef("niveles · tarjeta", T("primera") - 0.1, "tarjeta", 0.18),
  ef("1 a 3 · blips", T("1"), "blips", 0.14, 0.8),
  ef("sentir · pop", T("sentir"), "pop", 0.16),
  ef("dolor · tachado", T("nunca") + 0.1, "tachado", 0.2),
  ef("baja · pop", T("baja"), "pop", 0.16),
  ef("gota · pop", T("aceite") + 0.42, "pop", 0.18),
  ef("final · campanita", S.final + 0.1, "campanita", 0.16),
];

// Voz en off a −22,7 LUFS (sin tocar): música y efectos ×0,49 para quedar ~16 dB por debajo.
const NIVEL = 0.49;

export const CompProductoVideo: React.FC = () => (
  <BaseComp
    carpeta={CARPETA}
    fotogramas={FOTOGRAMAS}
    caras={CARAS}
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

export const CompProducto = () => (
  <Composition
    id="ComoFuncionaProducto"
    component={CompProductoVideo}
    durationInFrames={Math.ceil(TOTAL * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
