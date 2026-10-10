import React from "react";
import { Composition, interpolate } from "remotion";
import { COLORS, FONTS, VIDEO } from "../brand";
import { DatosCaras, useCaras, zonasEn } from "../rutinas/Caras";
import { Aviso, Pop } from "../rutinas/Graficos";
import { Aceite3D, Flecha3D, Perilla3D } from "../rutinas/Objetos3D";
import { Efecto } from "../rutinas/Rutina";
import { CLAMP, useT } from "../rutinas/util";
import { ajustar, Columnas, Elem, Lado, Limites } from "../dia6/Maqueta";
import { Base7, Zoom } from "./Base7";
import caras from "./data/caras.json";
import clips from "./data/clips.json";
import {
  Anillo,
  Chips,
  Eleccion,
  PildoraZona,
  Racha,
  Tachado,
  TituloBajo,
  Velocidad,
} from "./Graficos";
import { Almohada3D, Bateria3D, Pluma3D, Sello3D } from "./Objetos3D";
import { at, DURATION, TOTAL, WORDS } from "./timing";

// Reto de 21 días · Vídeo 7 "Piernas ligeras" (voz en off + tomas de los dos crudos, scripts/dia7/montar.py).
// Cada gráfico nace de su frase. Para no repetir los días anteriores: título en la franja baja letra a letra,
// cortinas de color entre zonas, anillo de la rutina, cámara lenta en "lentos", timelapse en "4 minutos", la toma a
// ×3 en "rápido", pantalla partida en "ambas pantorrillas", reencuadres hacia la pierna y etalonaje por momento.

const S = {
  intro: 0,
  comoda: at("siéntate").start,
  prepara: at("prepara ambas").start,
  pantorrillas: at("trabajamos").start,
  ambas: at("después que").start,
  muslos: at("vas a continuar").start,
  descanso: at("cuando termines").start,
  cierre: at("incluso").start,
};
const FIN = TOTAL + 1;
const clip = (frase: string) => {
  const i = clips.findIndex((c) => c.frase === frase);
  const fin = i + 1 < clips.length ? clips[i + 1].outStart : TOTAL;
  return { desde: clips[i].outStart, hasta: fin };
};

// La cabeza está arriba en casi todas las tomas: columnas a los lados desde y = 210 y hasta 1160 (debajo va el título)
// Si al lado de la cabeza no cabe, siguen por debajo de ella; cuando el título se recoge, bajan hasta y = 1450 (§10.10)
const LIM: Limites = {
  arriba: 210,
  abajo: 1160,
  bajoTitulo: false,
  bajoCabeza: true,
};
const limEn = (s: Seccion, t: number): Limites =>
  s.titulo && t < s.desde + (s.titulo.dura ?? 2.4) + 0.3
    ? LIM
    : { ...LIM, abajo: 1450 };

// Tomas sin cabeza en el plano (tumbada con las piernas en alto; pantalla partida): la silueta marcaría las rodillas
const SIN_CABEZA = ["puedes descansar", "incluso", "después que"].map(clip);
const sinCabeza = (d: DatosCaras): DatosCaras => ({
  ...d,
  caras: d.caras.map((c) =>
    SIN_CABEZA.some(
      // ±0,1 s: zonaCara también mira la muestra justo antes y después de la toma
      (q) =>
        (c[0] as number) / 30 >= q.desde - 0.1 &&
        (c[0] as number) / 30 < q.hasta + 0.1,
    )
      ? [c[0], -3000, -3000, 10, 10]
      : c,
  ),
});
const IZQ: Lado = "izq";
const DER: Lado = "der";

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
  titulo?: { kicker: string; texto: string; dura?: number; pildora: string };
  anillo?: { activos: number[]; centro: string; pie: string; at?: number };
  extras: Extra[];
};

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
  escala: 0.95,
  lado,
  el: (pos) => <Aviso at={t0} tipo={tipo} texto={texto} style={pos} />,
});
const obj3d = (
  t0: number,
  el: (pos: React.CSSProperties) => React.ReactNode,
  hasta?: number,
  lado: Lado = IZQ,
  h = 280,
  w = 300,
): Extra => ({ desde: t0, hasta, w, h, escala: 1, lado, el });

const SECCIONES: Seccion[] = [
  // "La rutina de hoy es para esos días en los que estás cansada pero no quieres abandonar el hábito."
  {
    nombre: "Intro",
    desde: S.intro,
    hasta: S.comoda,
    titulo: {
      kicker: "DÍA 7 · 15 MIN",
      texto: "piernas ligeras",
      dura: 2.7,
      pildora: "PIERNAS LIGERAS",
    },
    extras: [
      obj3d(
        0.3,
        (pos) => <Pluma3D desde={0.3} ancho={300} alto={300} style={pos} />,
        at("cansada").start,
        DER,
        300,
      ),
      obj3d(
        at("cansada").start,
        (pos) => (
          <Bateria3D
            desde={at("cansada").start}
            carga={at("pero no quieres").start}
            ancho={300}
            alto={300}
            style={pos}
          />
        ),
        undefined,
        DER,
        300,
      ),
      {
        desde: at("hábito").start,
        w: 300,
        h: 120,
        escala: 0.9,
        lado: IZQ,
        el: (pos) => <Racha at={at("hábito").start} marca={1e9} style={pos} />,
      },
    ],
  },
  // "Siéntate o ponte cómoda con las piernas apoyadas sobre una silla o sobre la cama."
  {
    nombre: "Cómoda",
    desde: S.comoda,
    hasta: S.prepara,
    titulo: {
      kicker: "PIERNAS APOYADAS",
      texto: "ponte cómoda",
      pildora: "PONTE CÓMODA",
    },
    extras: [
      {
        desde: at("silla").start - 0.1,
        w: 240,
        h: 240,
        lado: IZQ,
        el: (pos) => (
          <Eleccion
            silla={at("silla").start}
            cama={at("cama").start}
            style={pos}
          />
        ),
      },
    ],
  },
  // "Prepara ambas piernas con suficiente aceite y selecciona una intensidad suave. Aplica aceite en pantorrillas y muslos."
  {
    nombre: "Prepara",
    desde: S.prepara,
    hasta: S.pantorrillas,
    titulo: {
      kicker: "PREPARACIÓN · 1 MIN",
      texto: "prepara la piel",
      pildora: "PREPARACIÓN",
    },
    anillo: {
      activos: [0],
      centro: "1",
      pie: "Preparación",
      at: S.prepara + 0.3,
    },
    extras: [
      obj3d(
        S.prepara + 0.2,
        (pos) => (
          <Aceite3D
            desde={S.prepara + 0.2}
            vierte={at("aceite").start}
            ancho={300}
            alto={320}
            style={pos}
          />
        ),
        at("selecciona").start,
        DER,
        320,
      ),
      // "selecciona una intensidad suave" → la perilla baja hasta el nivel 1
      obj3d(
        at("selecciona").start,
        (pos) => (
          <Perilla3D
            desde={at("selecciona").start}
            niveles={[
              [at("selecciona").start, 3],
              [at("intensidad").start, 3],
              [at("suave").start, 1],
            ]}
            ancho={300}
            alto={280}
            style={pos}
          />
        ),
        at("aplica aceite").start,
        DER,
      ),
      aviso(at("suave").start, "Intensidad suave", "si"),
      aviso(at("suave").start + 0.5, "Calor: opcional", "si"),
      {
        desde: at("pantorrillas").start,
        w: 250,
        h: 140,
        lado: DER,
        el: (pos) => (
          <Chips
            chips={[
              {
                texto: "Pantorrillas",
                at: at("pantorrillas").start,
                icono: "1",
              },
              { texto: "Muslos", at: at("muslos").start, icono: "2" },
            ]}
            style={pos}
          />
        ),
      },
    ],
  },
  // "Trabajamos 4 minutos por cada pantorrilla con movimientos ascendentes, lentos y continuos. Haz pasadas suaves
  // desde el tobillo hacia arriba, terminando antes de la parte posterior de la rodilla."
  {
    nombre: "Pantorrillas",
    desde: S.pantorrillas,
    hasta: S.ambas,
    titulo: {
      kicker: "4 MIN EN CADA UNA",
      texto: "pantorrillas",
      pildora: "PANTORRILLAS",
    },
    anillo: { activos: [1, 2], centro: "4", pie: "Cada pantorrilla" },
    extras: [
      {
        ...clip("trabajamos"),
        w: 170,
        h: 70,
        lado: DER,
        el: (pos) => (
          <Velocidad at={clip("trabajamos").desde + 0.2} x={2} style={pos} />
        ),
      },
      {
        desde: at("ascendentes").start,
        hasta: at("terminando").start,
        w: 250,
        h: 210,
        lado: DER,
        el: (pos) => (
          <Chips
            chips={[
              { texto: "Ascendentes", at: at("ascendentes").start, icono: "↑" },
              { texto: "Lentos", at: at("lentos").start, icono: "~" },
              { texto: "Continuos", at: at("continuos").start, icono: "∞" },
            ]}
            style={pos}
          />
        ),
      },
      obj3d(
        at("desde el tobillo").start,
        (pos) => (
          <Flecha3D
            desde={at("desde el tobillo").start}
            dir="arriba"
            ancho={300}
            alto={280}
            style={pos}
          />
        ),
        undefined,
        IZQ,
      ),
      aviso(at("terminando").start, "Antes de la rodilla", "no"),
    ],
  },
  // "Después que hayas terminado ambas pantorrillas…" → pantalla partida (sin título: no hay cabeza)
  { nombre: "Ambas", desde: S.ambas, hasta: S.muslos, extras: [] },
  // "…vas a continuar 3 minutos en cada muslo. No necesitas hacerlo rápido, necesitas mantener el movimiento.
  // Recuerda no dejar el dispositivo en un solo punto."
  {
    nombre: "Muslos",
    desde: S.muslos,
    hasta: S.descanso,
    titulo: {
      kicker: "3 MIN EN CADA UNO",
      texto: "muslos",
      pildora: "MUSLOS",
    },
    anillo: { activos: [3, 4], centro: "3", pie: "Cada muslo" },
    extras: [
      {
        ...clip("no necesitas"),
        w: 170,
        h: 70,
        lado: DER,
        el: (pos) => (
          <Velocidad at={clip("no necesitas").desde + 0.1} x={3} style={pos} />
        ),
      },
      {
        desde: at("no necesitas").start,
        hasta: at("recuerda no dejar").start,
        w: 300,
        h: 170,
        lado: DER,
        el: (pos) => (
          <Tachado
            at={at("no necesitas").start}
            tacha={at("rápido").start}
            cambia={at("mantener").start}
            antes="rápido"
            despues="mantén el movimiento"
            style={pos}
          />
        ),
      },
      aviso(at("recuerda no dejar").start, "Nunca en un solo punto", "no"),
    ],
  },
  // "Cuando termines cada pierna, puedes descansar unos minutos con las piernas cómodamente apoyadas sobre una almohada."
  {
    nombre: "Descanso",
    desde: S.descanso,
    hasta: S.cierre,
    titulo: {
      kicker: "OPCIONAL · AL TERMINAR",
      texto: "descansa",
      pildora: "DESCANSO OPCIONAL",
    },
    extras: [
      obj3d(
        at("descansar").start,
        (pos) => (
          <Almohada3D
            desde={at("descansar").start}
            apoya={at("apoyadas", S.descanso).start}
            ancho={300}
            alto={260}
            style={pos}
          />
        ),
        undefined,
        IZQ,
        260,
      ),
      aviso(at("unos minutos").start, "Unos minutos"),
      aviso(at("apoyadas", S.descanso).start, "Piernas sobre una almohada"),
    ],
  },
  // "Incluso en un día difícil, cumpliste con tus 15 minutos del día." (cuadro: "Marca el día cumplido")
  {
    nombre: "Cierre",
    desde: S.cierre,
    hasta: FIN,
    titulo: {
      kicker: "INCLUSO EN UN DÍA DIFÍCIL",
      texto: "día cumplido",
      dura: 1.8,
      pildora: "DÍA 7 CUMPLIDO",
    },
    anillo: {
      activos: [5],
      centro: "15",
      pie: "¡Completada!",
      at: at("15").start,
    },
    extras: [
      obj3d(
        at("cumpliste").start - 0.1,
        (pos) => (
          <Sello3D
            desde={at("cumpliste").start - 0.1}
            estampa={at("cumpliste").start}
            ancho={300}
            alto={300}
            style={pos}
          />
        ),
        undefined,
        DER,
        300,
      ),
      {
        desde: S.cierre + 0.4,
        w: 300,
        h: 120,
        escala: 0.9,
        lado: IZQ,
        el: (pos) => (
          <Racha at={S.cierre + 0.4} marca={at("15").start} style={pos} />
        ),
      },
    ],
  },
];

// Columnas de la sección en el instante t: píldora de la zona (cuando el título se recoge), anillo y extras activos
// en el orden en que se dicen. Si no caben, se retira lo más antiguo; nunca lo último que se ha dicho.
const useElementos = (s: Seccion): Elem[] => {
  const caras = useCaras();
  const { t } = useT();
  const { actual } = zonasEn(caras, t, s.desde, s.hasta);
  const lista: Elem[] = [];
  if (s.titulo) {
    const t0 = s.desde + (s.titulo.dura ?? 2.4) + 0.1;
    if (t >= t0)
      lista.push({
        w: 300,
        h: 56,
        lado: IZQ,
        render: (st) => (
          <PildoraZona at={t0} texto={s.titulo!.pildora} style={st} />
        ),
      });
  }
  if (s.anillo) {
    const t0 = s.anillo.at ?? s.desde + 0.3;
    const { activos, centro, pie } = s.anillo;
    if (t >= t0 - 0.05)
      lista.push({
        w: 260,
        h: 330,
        escala: 0.9,
        lado: IZQ,
        render: (st) => (
          <Anillo
            desde={t0}
            hasta={s.hasta}
            activos={activos}
            centro={centro}
            pie={pie}
            style={st}
          />
        ),
      });
  }
  for (const e of s.extras)
    if (t >= e.desde - 0.05 && t < (e.hasta ?? s.hasta))
      lista.push({
        w: e.w ?? 260,
        h: e.h,
        escala: e.escala,
        lado: e.lado,
        render: e.el,
      });
  return ajustar(actual, [], lista, limEn(s, t));
};

const SeccionComp: React.FC<{ s: Seccion }> = ({ s }) => {
  const elementos = useElementos(s);
  const { t } = useT();
  return (
    <>
      {s.titulo ? (
        <TituloBajo
          desde={s.desde}
          kicker={s.titulo.kicker}
          texto={s.titulo.texto}
          dura={s.titulo.dura}
        />
      ) : null}
      <Columnas
        desde={s.desde}
        hasta={s.hasta}
        elementos={elementos}
        lim={limEn(s, t)}
      />
    </>
  );
};

// "Después que hayas terminado ambas pantorrillas" → la línea Durazno se abre entre las dos tomas y cada una se marca
const Partida: React.FC = () => {
  const { t } = useT();
  const { desde, hasta } = clip("después que");
  if (t < desde || t >= hasta) return null;
  const abre = interpolate(t, [desde, desde + 0.35], [0, 1], CLAMP);
  const marca = (at0: number, top: number) => (
    <div style={{ position: "absolute", left: 40, top }}>
      <Pop at={at0} kind="scale">
        <svg width={84} height={84} viewBox="0 0 56 56">
          <circle cx={28} cy={28} r={26} fill={COLORS.salvia} />
          <path
            d="M16 29 L25 38 L41 20"
            stroke={COLORS.marfil}
            strokeWidth={6}
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </Pop>
    </div>
  );
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: 540 - 540 * abre,
          width: 1080 * abre,
          top: 954,
          height: 12,
          background: COLORS.durazno,
          boxShadow: "0 0 18px rgba(69,89,90,.4)",
        }}
      />
      {marca(at("terminado").start, 60)}
      {marca(at("ambas pantorrillas").start, 1000)}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 922,
          display: "flex",
          justifyContent: "center",
        }}
      >
        <Pop at={at("ambas pantorrillas").start} kind="scale">
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 34,
              letterSpacing: "0.18em",
              color: COLORS.petroleo,
              background: COLORS.durazno,
              borderRadius: 40,
              padding: "12px 30px 10px",
              boxShadow: "0 10px 26px rgba(69,89,90,.35)",
            }}
          >
            AMBAS PANTORRILLAS
          </div>
        </Pop>
      </div>
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
            style={{ position: "absolute", inset: 0, opacity: salida }}
          >
            <SeccionComp s={b} />
          </div>
        );
      })}
      <Partida />
    </>
  );
};

// Reencuadres: se acercan despacio a la pierna que se trabaja (o se alejan) para variar el plano fijo
const z = (frase: string, z0: number, z1: number, ox: number, oy: number) => ({
  ...clip(frase),
  z0,
  z1,
  ox,
  oy,
});
const ZOOMS: Zoom[] = [
  z("siéntate", 1.0, 1.06, 540, 1300),
  z("aplica aceite", 1.0, 1.14, 500, 1500),
  z("haz pasadas", 1.12, 1.3, 520, 1650),
  z("vas a continuar", 1.0, 1.12, 540, 1200),
  z("recuerda no dejar", 1.12, 1.0, 540, 1200),
  z("incluso", 1.0, 1.1, 540, 900),
];

// Etalonaje: "cansada" apagada y fría que se calienta en "pero no quieres abandonar"; el descanso, cálido
const DESC = clip("puedes descansar").desde;
const filtro = (t: number) => {
  const sat = interpolate(t, [3.4, 4.3], [0.55, 1], CLAMP);
  const bri = interpolate(t, [3.4, 4.3], [0.9, 1], CLAMP);
  const calido = interpolate(t, [DESC - 0.2, DESC + 0.5], [0, 1], CLAMP);
  if (sat >= 1 && calido <= 0) return undefined;
  return `saturate(${sat * (1 + 0.06 * calido)}) brightness(${bri * (1 + 0.03 * calido)}) sepia(${0.14 * calido})`;
};
const velo = (t: number) =>
  Math.max(
    interpolate(t, [3.4, 4.3], [0.7, 0], CLAMP),
    interpolate(t, [DESC - 0.2, DESC + 0.5], [0, 0.75], CLAMP),
  );

const CORTINAS = [S.comoda, S.pantorrillas, S.muslos, S.descanso, S.cierre];
const EFECTOS: Efecto[] = [
  { nombre: "título · whoosh", t: 0, src: "whoosh", vol: 0.24 },
  { nombre: "cansada · pop", t: at("cansada").start, src: "pop", vol: 0.22 },
  {
    nombre: "recarga · escalones",
    t: at("pero no quieres").start + 0.1,
    src: "escalones",
    vol: 0.2,
  },
  {
    nombre: "hábito · blips",
    t: at("hábito").start + 0.2,
    src: "blips",
    vol: 0.2,
    dur: 1,
  },
  ...CORTINAS.map((c, i) => ({
    nombre: `cortina ${i} · whoosh`,
    t: c - 0.25,
    src: "whoosh",
    vol: 0.24,
  })),
  { nombre: "silla · pop", t: at("silla").start, src: "pop", vol: 0.22 },
  { nombre: "cama · pop", t: at("cama").start, src: "pop", vol: 0.22 },
  { nombre: "prepara · swish", t: S.prepara - 0.18, src: "swish", vol: 0.22 },
  { nombre: "aceite · brillo", t: at("aceite").start, src: "brillo", vol: 0.2 },
  {
    nombre: "intensidad · tarjeta",
    t: at("selecciona").start,
    src: "tarjeta",
    vol: 0.22,
  },
  {
    nombre: "suave · blips",
    t: at("suave").start,
    src: "blips",
    vol: 0.18,
    dur: 1,
  },
  {
    nombre: "pantorrillas · pop",
    t: at("pantorrillas").start,
    src: "pop",
    vol: 0.2,
  },
  { nombre: "muslos · pop", t: at("muslos").start, src: "pop", vol: 0.2 },
  {
    nombre: "4 min · tictac",
    t: at("4").start,
    src: "tictac",
    vol: 0.18,
    dur: 1.4,
  },
  {
    nombre: "ascendentes · escalones",
    t: at("ascendentes").start,
    src: "escalones",
    vol: 0.2,
  },
  { nombre: "lentos · pop", t: at("lentos").start, src: "pop", vol: 0.2 },
  { nombre: "continuos · pop", t: at("continuos").start, src: "pop", vol: 0.2 },
  {
    nombre: "tobillo · swish",
    t: at("desde el tobillo").start - 0.18,
    src: "swish",
    vol: 0.22,
  },
  {
    nombre: "rodilla · tachado",
    t: at("terminando").start + 0.2,
    src: "tachado",
    vol: 0.22,
  },
  { nombre: "partida · tarjeta", t: S.ambas, src: "tarjeta", vol: 0.22 },
  {
    nombre: "ambas · campanita",
    t: at("ambas pantorrillas").start,
    src: "campanita",
    vol: 0.16,
  },
  {
    nombre: "rápido · tachado",
    t: at("rápido").start + 0.2,
    src: "tachado",
    vol: 0.22,
  },
  {
    nombre: "mantener · brillo",
    t: at("mantener").start,
    src: "brillo",
    vol: 0.2,
  },
  {
    nombre: "un punto · pop",
    t: at("recuerda no dejar").start,
    src: "pop",
    vol: 0.22,
  },
  {
    nombre: "descansar · swish",
    t: at("descansar").start - 0.18,
    src: "swish",
    vol: 0.2,
  },
  {
    nombre: "minutos · pop",
    t: at("unos minutos").start,
    src: "pop",
    vol: 0.2,
  },
  {
    nombre: "sello · impacto",
    t: at("cumpliste").start + 0.35,
    src: "impacto",
    vol: 0.22,
  },
  {
    nombre: "15 · campanita",
    t: at("15").start + 0.1,
    src: "campanita",
    vol: 0.18,
  },
];

// Voz en off a −25,6 LUFS (como la del día 6): música y efectos bajan lo mismo (≈ −9 dB), la voz no se toca
const NIVEL = 0.35;

export const Dia7Video: React.FC = () => (
  <Base7
    caras={sinCabeza({
      ...(caras as DatosCaras),
      cortes: clips.map((c) => c.outStart),
    })}
    zooms={ZOOMS}
    filtro={filtro}
    velo={velo}
    cortinas={CORTINAS}
    finVoz={WORDS[WORDS.length - 1].end}
    duracion={DURATION}
    efectos={EFECTOS.map((e) => ({ ...e, vol: e.vol * NIVEL }))}
    musica={0.1 * NIVEL}
    musicaCierre={0.2 * NIVEL}
  >
    <Beats />
  </Base7>
);

export const Dia7 = () => (
  <Composition
    id="Dia7"
    component={Dia7Video}
    durationInFrames={Math.ceil(TOTAL * VIDEO.fps)}
    fps={VIDEO.fps}
    width={VIDEO.width}
    height={VIDEO.height}
  />
);
