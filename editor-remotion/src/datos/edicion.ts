// Lista de decisiones de edición (EDL) del vídeo "Semilla certificada" de AgroKrack.
// Todo se define en segundos. La pista de voz manda: planos, subtítulos y efectos se
// colocan respecto a las palabras transcritas por Whisper (src/datos/palabras.json).

import { MEZCLA } from "../estilo";
import palabrasJson from "./palabras.json";

type PalabraOrigen = { text: string; startMs: number; endMs: number };
const PAL = palabrasJson as Record<string, PalabraOrigen[]>;

// ─────────────────────────────────────────────────────────────────────────────
// 1. PISTA DE VOZ — tramos de cada toma, en orden, con la pausa que les sigue.
// ─────────────────────────────────────────────────────────────────────────────
export type SegVoz = {
  id: string;
  clip: string; // archivo en public/voz y clave en palabras.json
  ini: number; // segundo de origen donde empieza
  fin: number; // segundo de origen donde acaba
  pausa: number; // silencio hasta el siguiente tramo
  t0: number; // inicio en la línea de tiempo
};

const TRAMOS: Omit<SegVoz, "t0">[] = [
  { id: "gancho", clip: "toma1_agro", ini: 1.72, fin: 5.98, pausa: 0.1 },
  { id: "contexto", clip: "wa_105147_0", ini: 1.46, fin: 10.72, pausa: 0.14 },
  { id: "presentacion", clip: "wa_105147_1", ini: 2.3, fin: 8.02, pausa: 0.06 },
  { id: "amtec", clip: "wa_105147_5", ini: 2.82, fin: 4.36, pausa: 0.3 },
  { id: "b1", clip: "wa_105147_2", ini: 2.16, fin: 5.12, pausa: 0.24 },
  { id: "b2", clip: "wa_105147_3", ini: 2.26, fin: 7.04, pausa: 0.24 },
  { id: "b3", clip: "wa_105147_4", ini: 1.47, fin: 5.7, pausa: 0.34 },
];

let acumulado = 0;
export const VOZ: SegVoz[] = TRAMOS.map((v) => {
  const s = { ...v, t0: acumulado };
  acumulado += v.fin - v.ini + v.pausa;
  return s;
});

const seg = (id: string): SegVoz => {
  const s = VOZ.find((v) => v.id === id);
  if (!s) throw new Error(`Tramo de voz desconocido: ${id}`);
  return s;
};

/** Segundo de la línea de tiempo que corresponde al segundo `src` del tramo. */
export const tl = (id: string, src: number) => seg(id).t0 + (src - seg(id).ini);
/** Inicio en la línea de tiempo de la palabra nº `i` del tramo. */
export const tw = (id: string, i: number) => tl(id, PAL[seg(id).clip][i].startMs / 1000);

// Hitos de la línea de tiempo
export const T_RECAP = acumulado; // fin de la voz (incluida su pausa)
export const DUR_RECAP = 2.45;
export const T_CIERRE = T_RECAP + DUR_RECAP;
export const DUR_CIERRE = 1.9;
export const DURACION = T_CIERRE + DUR_CIERRE;

// ─────────────────────────────────────────────────────────────────────────────
// 2. PISTA DE VÍDEO — planos
// ─────────────────────────────────────────────────────────────────────────────
/** Punto del original (fx, fy, de 0 a 1) que se lleva a la posición de pantalla (dx, dy). */
export type Encuadre = { escala: number; fx: number; fy: number; dx: number; dy: number };

export type Plano = {
  id: string;
  clip: string; // archivo en public/clips
  desde: number;
  hasta: number;
  src: number; // segundo del clip que se ve en `desde`
  encuadre: Encuadre;
  /** Golpe de zoom al entrar: la escala arranca multiplicada por `de` y llega a 1 en `dur` s. */
  zoom?: { de: number; dur: number };
  /** Deriva lenta de escala por segundo (0,01 = +1 %/s). */
  deriva?: number;
};

const ENC = {
  // Presentador (selfie): la cara queda a media altura y el texto va sobre el pecho.
  presentadorGancho: { escala: 1.22, fx: 0.63, fy: 0.585, dx: 0.55, dy: 0.495 },
  presentadorContexto: { escala: 1.22, fx: 0.58, fy: 0.6, dx: 0.52, dy: 0.512 },
  presentadorCerca: { escala: 1.36, fx: 0.58, fy: 0.6, dx: 0.52, dy: 0.47 },
  // Agrónomo (plano medio): cabeza arriba, texto sobre el pecho.
  agronomoMedio: { escala: 1.25, fx: 0.46, fy: 0.45, dx: 0.5, dy: 0.42 },
  agronomoCerca: { escala: 1.52, fx: 0.47, fy: 0.44, dx: 0.5, dy: 0.4 },
  agronomoAmtec: { escala: 1.18, fx: 0.52, fy: 0.42, dx: 0.5, dy: 0.4 },
  beneficio2: { escala: 1.3, fx: 0.5, fy: 0.45, dx: 0.5, dy: 0.42 },
  beneficio2Cerca: { escala: 1.55, fx: 0.47, fy: 0.45, dx: 0.5, dy: 0.4 },
  beneficio3: { escala: 1.08, fx: 0.48, fy: 0.45, dx: 0.5, dy: 0.44 },
  broll: { escala: 1.06, fx: 0.5, fy: 0.5, dx: 0.5, dy: 0.5 },
  cosechadora: { escala: 1.3, fx: 0.52, fy: 0.42, dx: 0.5, dy: 0.4 },
  mano: { escala: 1.08, fx: 0.55, fy: 0.55, dx: 0.5, dy: 0.5 },
} satisfies Record<string, Encuadre>;

// Cortes (segundos de la línea de tiempo)
const C = {
  contexto: seg("contexto").t0,
  cosechadora: tl("contexto", 3.86),
  vuelveContexto: tl("contexto", 5.9),
  mano: tl("contexto", 8.88),
  presentacion: seg("presentacion").t0,
  presentacionCerca: tl("presentacion", 5.08),
  amtec: seg("amtec").t0,
  graficoBeneficios: seg("b1").t0,
  beneficio2: tl("b2", 3.62),
  beneficio2Cerca: tl("b2", 4.72),
  graficoBeneficio3: seg("b3").t0,
  beneficio3: tl("b3", 2.82),
  grano: tl("b3", 4.08),
};
export const CORTES = C;

export const PLANOS: Plano[] = [
  {
    id: "Gancho · presentador",
    clip: "presentador_gancho",
    desde: 0,
    hasta: C.contexto,
    src: seg("gancho").ini,
    encuadre: ENC.presentadorGancho,
    zoom: { de: 1.34, dur: 0.6 },
  },
  {
    id: "Contexto · presentador",
    clip: "presentador_contexto",
    desde: C.contexto,
    hasta: C.cosechadora,
    src: seg("contexto").ini,
    encuadre: ENC.presentadorContexto,
    zoom: { de: 1.28, dur: 0.8 },
  },
  {
    id: "B-roll · cosechadora a cámara lenta",
    clip: "broll_cosechadora_lenta",
    desde: C.cosechadora,
    hasta: C.vuelveContexto,
    src: 9.0,
    encuadre: ENC.cosechadora,
    zoom: { de: 1.14, dur: 0.5 },
    deriva: 0.02,
  },
  {
    id: "Contexto · presentador (más cerca)",
    clip: "presentador_contexto",
    desde: C.vuelveContexto,
    hasta: C.mano,
    src: seg("contexto").ini + (C.vuelveContexto - seg("contexto").t0),
    encuadre: ENC.presentadorCerca,
    zoom: { de: 0.86, dur: 0.7 },
  },
  {
    id: "B-roll · mano sobre el arroz",
    clip: "broll_mano_arroz",
    desde: C.mano,
    hasta: C.presentacion,
    src: 1.3,
    encuadre: ENC.mano,
    zoom: { de: 1.12, dur: 0.5 },
    deriva: 0.02,
  },
  {
    id: "Presentación · agrónomo",
    clip: "agronomo_presentacion",
    desde: C.presentacion,
    hasta: C.presentacionCerca,
    src: seg("presentacion").ini,
    encuadre: ENC.agronomoMedio,
    zoom: { de: 1.25, dur: 0.6 },
  },
  {
    id: "Presentación · agrónomo (más cerca)",
    clip: "agronomo_presentacion",
    desde: C.presentacionCerca,
    hasta: C.amtec,
    src: seg("presentacion").ini + (C.presentacionCerca - seg("presentacion").t0),
    encuadre: ENC.agronomoCerca,
  },
  {
    id: "AMTEC · agrónomo",
    clip: "agronomo_amtec",
    desde: C.amtec,
    hasta: C.graficoBeneficios,
    src: seg("amtec").ini,
    encuadre: ENC.agronomoAmtec,
    zoom: { de: 1.12, dur: 0.45 },
  },
  // (gráfico de beneficios: C.graficoBeneficios → C.beneficio2)
  {
    id: "Beneficio 2 · agrónomo",
    clip: "agronomo_beneficio2",
    desde: C.beneficio2,
    hasta: C.beneficio2Cerca,
    src: 3.62,
    encuadre: ENC.beneficio2,
    zoom: { de: 0.86, dur: 0.7 },
  },
  {
    id: "Beneficio 2 · agrónomo (más cerca)",
    clip: "agronomo_beneficio2",
    desde: C.beneficio2Cerca,
    hasta: C.graficoBeneficio3,
    src: 4.72,
    encuadre: ENC.beneficio2Cerca,
  },
  // (gráfico de beneficios: C.graficoBeneficio3 → C.beneficio3)
  {
    id: "Beneficio 3 · agrónomo",
    clip: "agronomo_beneficio3",
    desde: C.beneficio3,
    hasta: C.grano,
    src: 2.82,
    encuadre: ENC.beneficio3,
    zoom: { de: 1.22, dur: 0.6 },
  },
  {
    id: "B-roll · grano cosechado",
    clip: "broll_grano",
    desde: C.grano,
    hasta: T_RECAP,
    src: 2.0,
    encuadre: ENC.broll,
    zoom: { de: 1.14, dur: 0.5 },
    deriva: 0.025,
  },
];

/** Transiciones "anillo + fuga de luz" (estilo.md §9): solo en cambios de bloque. */
export const TRANSICIONES_LUZ: { t: number; semilla: number }[] = [
  { t: C.contexto, semilla: 3 },
  { t: C.presentacion, semilla: 7 },
  { t: T_CIERRE, semilla: 5 },
];

// ─────────────────────────────────────────────────────────────────────────────
// 3. MOTION GRAPHICS — barra de los 3 beneficios (estilo.md §7)
// ─────────────────────────────────────────────────────────────────────────────
export type PalabraTL = { texto: string; t: number };
export type EscenaBarra = {
  id: string;
  desde: number;
  hasta: number;
  /** La barra se construye al entrar (1.ª aparición) o entra ya hecha con zoom 3× → 1×. */
  construir: boolean;
  tramosYaEncendidos: number[];
  rotulosYaHechos: number[];
  encender: { tramo: number; t: number }[]; // t relativos al inicio de la escena
  rotulos: { tramo: number; tFlecha: number; lineas: PalabraTL[][] }[];
  checks: { tramo: number; t: number }[];
  pulsoFinal?: number;
};

const S1 = C.graficoBeneficios;
const S2 = C.graficoBeneficio3;
export const ESCENAS_BARRA: EscenaBarra[] = [
  {
    id: "Gráfico · beneficios 1 y 2",
    desde: S1,
    hasta: C.beneficio2,
    construir: true,
    tramosYaEncendidos: [],
    rotulosYaHechos: [],
    encender: [
      { tramo: 1, t: tw("b1", 2) - S1 }, // "uno"
      { tramo: 2, t: tw("b2", 2) - S1 }, // "dos"
    ],
    rotulos: [
      {
        tramo: 1,
        tFlecha: tw("b1", 3) - S1, // "semilla"
        lineas: [
          [
            { texto: "Libre", t: tw("b1", 4) - S1 },
            { texto: "de", t: tw("b1", 5) - S1 },
          ],
          [{ texto: "malezas", t: tw("b1", 6) - S1 }],
        ],
      },
    ],
    checks: [{ tramo: 1, t: tw("b1", 6) + 0.42 - S1 }],
  },
  {
    id: "Gráfico · beneficio 3",
    desde: S2,
    hasta: C.beneficio3,
    construir: false,
    tramosYaEncendidos: [1, 2],
    rotulosYaHechos: [1, 2],
    encender: [{ tramo: 3, t: tw("b3", 2) - S2 }], // "tres"
    rotulos: [],
    checks: [],
  },
  {
    id: "Gráfico · resumen",
    desde: T_RECAP,
    hasta: T_CIERRE,
    construir: false,
    tramosYaEncendidos: [1, 2, 3],
    rotulosYaHechos: [1, 2],
    encender: [],
    rotulos: [
      {
        tramo: 3,
        tFlecha: 0.32,
        lineas: [
          [
            { texto: "Sanidad", t: 0.58 },
            { texto: "y", t: 0.7 },
          ],
          [{ texto: "rendimiento", t: 0.82 }],
        ],
      },
    ],
    checks: [{ tramo: 3, t: 1.12 }],
    pulsoFinal: 1.45,
  },
];

// ─────────────────────────────────────────────────────────────────────────────
// 4. SUBTÍTULOS (estilo.md §4 y §5)
// ─────────────────────────────────────────────────────────────────────────────
export type Icono = "brote" | "sello" | "escudo" | "salud" | "grafico";

export type Bloque =
  | { tipo: "normal"; ini: number; fin: number; y: number; palabras: PalabraTL[] }
  | {
      tipo: "apilado";
      ini: number;
      fin: number;
      /** Centro vertical de la línea destacada. */
      y: number;
      linea1?: PalabraTL[];
      destacado: PalabraTL[][];
      cursiva: boolean;
      tam: number;
      alinear: "izquierda" | "centro";
      pildora?: PalabraTL[];
      tamPildora?: number;
      iconos?: { icono: Icono; t: number }[];
      /** El destacado ya está en pantalla al empezar (continúa del plano anterior). */
      destacadoFijo?: boolean;
    }
  | { tipo: "cita"; ini: number; fin: number; y: number; lineas: PalabraTL[][] };

const limpiar = (s: string) => s.replace(/[.,;:]+$/g, "");
/** Palabra nº `i` del tramo, con su tiempo. `texto` sustituye a lo que escribió Whisper. */
const p = (id: string, i: number, texto?: string): PalabraTL => ({
  texto: texto ?? limpiar(PAL[seg(id).clip][i].text),
  t: tw(id, i),
});
const ps = (id: string, indices: number[]) => indices.map((i) => p(id, i));

// Altura del texto según el plano: siempre sobre el pecho, nunca sobre la cara.
const Y = { presentador: 1390, agronomo: 1120, beneficio2: 1150, beneficio3: 1190, broll: 1060 };

const normal = (id: string, indices: number[], y: number, fin: number): Bloque => {
  const palabras = ps(id, indices);
  return { tipo: "normal", ini: palabras[0].t - 0.02, fin, y, palabras };
};

export const BLOQUES: Bloque[] = [
  // ── Gancho ────────────────────────────────────────────────────────────────
  {
    tipo: "apilado",
    ini: tw("gancho", 0) - 0.02,
    fin: tw("gancho", 3) - 0.02,
    y: Y.presentador + 40,
    linea1: ps("gancho", [0, 1]),
    destacado: [[p("gancho", 2, "KRACKS")]],
    cursiva: false,
    tam: 112,
    alinear: "centro",
  },
  normal("gancho", [3, 4], Y.presentador, tw("gancho", 5) - 0.02),
  normal("gancho", [5, 6, 7], Y.presentador, tw("gancho", 8) - 0.02),
  {
    tipo: "apilado",
    ini: tw("gancho", 8) - 0.02,
    fin: C.contexto,
    y: Y.presentador,
    linea1: ps("gancho", [8, 9]),
    destacado: [[p("gancho", 10, "SEMILLA")]],
    cursiva: true,
    tam: 118,
    alinear: "izquierda",
    pildora: [p("gancho", 11, "certificada")],
    iconos: [
      { icono: "brote", t: tw("gancho", 10) + 0.14 },
      { icono: "sello", t: tw("gancho", 11) + 0.12 },
    ],
  },

  // ── Contexto ──────────────────────────────────────────────────────────────
  normal("contexto", [0, 1], Y.presentador, tw("contexto", 2) - 0.02),
  normal("contexto", [2, 3, 4], Y.presentador, tw("contexto", 5) - 0.02),
  {
    tipo: "apilado",
    ini: tw("contexto", 5) - 0.02,
    fin: C.cosechadora,
    y: Y.presentador + 40,
    linea1: ps("contexto", [5, 6, 7]),
    destacado: [[p("contexto", 8, "FEDEARROZ")]],
    cursiva: false,
    tam: 104,
    alinear: "centro",
  },
  // (b-roll cosechadora)
  {
    tipo: "normal",
    ini: C.cosechadora + 0.04,
    fin: tw("contexto", 11) - 0.02,
    y: Y.broll,
    palabras: [
      { texto: "el", t: C.cosechadora + 0.06 },
      p("contexto", 10),
    ],
  },
  normal("contexto", [11, 12], Y.broll, tw("contexto", 13) - 0.02),
  normal("contexto", [13, 14], Y.broll, C.vuelveContexto),
  // (vuelve el presentador)
  normal("contexto", [16, 17, 18, 19], Y.presentador - 20, tw("contexto", 20) - 0.02),
  normal("contexto", [20, 21], Y.presentador - 20, tw("contexto", 22) - 0.02),
  {
    tipo: "apilado",
    ini: tw("contexto", 22) - 0.02,
    fin: C.mano,
    y: Y.presentador + 20,
    linea1: ps("contexto", [22, 23]),
    destacado: [[p("contexto", 24, "VENTAJAS")]],
    cursiva: false,
    tam: 112,
    alinear: "centro",
  },
  // (b-roll mano)
  {
    tipo: "normal",
    ini: C.mano + 0.04,
    fin: tw("contexto", 27) - 0.02,
    y: Y.broll,
    palabras: [
      { texto: "de", t: C.mano + 0.06 },
      p("contexto", 26),
    ],
  },
  normal("contexto", [27, 28], Y.broll, C.presentacion),

  // ── Presentación del agrónomo ─────────────────────────────────────────────
  normal("presentacion", [0, 1], Y.agronomo, tw("presentacion", 2) - 0.02),
  {
    tipo: "apilado",
    ini: tw("presentacion", 2) - 0.02,
    fin: C.presentacionCerca,
    y: Y.agronomo,
    linea1: ps("presentacion", [2, 3, 4]),
    destacado: [
      [p("presentacion", 5, "LUIS"), p("presentacion", 6, "BERNAL")],
      [p("presentacion", 7, "GUTIÉRREZ")],
    ],
    cursiva: true,
    tam: 98,
    alinear: "izquierda",
    pildora: ps("presentacion", [8, 9]),
  },
  normal("presentacion", [10, 11], Y.agronomo + 40, tw("presentacion", 12) - 0.02),
  normal("presentacion", [12, 13, 14], Y.agronomo + 40, tw("presentacion", 15) - 0.02),
  normal("presentacion", [15, 16], Y.agronomo + 40, tw("presentacion", 17) - 0.02),
  {
    tipo: "apilado",
    ini: tw("presentacion", 17) - 0.02,
    fin: C.amtec,
    y: Y.agronomo + 70,
    linea1: ps("presentacion", [17, 18]),
    destacado: [[p("presentacion", 19, "AMTEC")]],
    cursiva: false,
    tam: 124,
    alinear: "centro",
  },

  // ── AMTEC: adopción masiva de tecnología ──────────────────────────────────
  {
    tipo: "apilado",
    ini: C.amtec,
    fin: C.graficoBeneficios,
    y: Y.agronomo + 70,
    destacado: [[{ texto: "AMTEC", t: C.amtec }]],
    destacadoFijo: true,
    cursiva: false,
    tam: 124,
    alinear: "centro",
    pildora: [p("amtec", 1), p("amtec", 2), p("amtec", 3), p("amtec", 4)],
    tamPildora: 52,
  },

  // ── Beneficio 1: todo ocurre en el gráfico (sin subtítulos) ───────────────

  // ── Beneficio 2 ───────────────────────────────────────────────────────────
  {
    tipo: "apilado",
    ini: C.beneficio2 + 0.02,
    fin: C.beneficio2Cerca,
    y: Y.beneficio2,
    destacado: [[p("b2", 3, "GARANTÍA")]],
    cursiva: false,
    tam: 116,
    alinear: "centro",
    iconos: [{ icono: "escudo", t: tw("b2", 3) + 0.16 }],
  },
  {
    tipo: "cita",
    ini: C.beneficio2Cerca + 0.02,
    fin: C.graficoBeneficio3,
    y: Y.beneficio2 + 30,
    lineas: [
      [p("b2", 6, "“lo"), p("b2", 7), p("b2", 8), p("b2", 9)],
      [p("b2", 10), p("b2", 11), p("b2", 12), p("b2", 13), p("b2", 14, "lleva”")],
    ],
  },

  // ── Beneficio 3 ───────────────────────────────────────────────────────────
  {
    tipo: "apilado",
    ini: C.beneficio3 + 0.02,
    fin: C.grano,
    y: Y.beneficio3,
    linea1: [p("b3", 3)],
    destacado: [[p("b3", 4, "SANIDAD")]],
    cursiva: false,
    tam: 116,
    alinear: "centro",
    iconos: [{ icono: "salud", t: tw("b3", 4) + 0.14 }],
  },
  {
    tipo: "apilado",
    ini: C.grano + 0.04,
    fin: T_RECAP,
    y: Y.broll + 30,
    linea1: ps("b3", [6, 7, 8]),
    destacado: [[p("b3", 9, "RENDIMIENTO")]],
    cursiva: false,
    tam: 104,
    alinear: "centro",
    iconos: [{ icono: "grafico", t: tw("b3", 9) + 0.14 }],
  },
];

/** Ventana en la que la música pierde los graves (cita textual, estilo.md §11). */
export const VENTANA_CITA = { ini: C.beneficio2Cerca, fin: C.graficoBeneficio3 };

// ─────────────────────────────────────────────────────────────────────────────
// 5. EFECTOS DE SONIDO — solo archivos del pack del cliente (public/sfx/ORIGEN.md)
// ─────────────────────────────────────────────────────────────────────────────
export type Sfx = {
  archivo: string;
  t: number; // instante en que debe sonar el golpe
  vol: number;
  adelanto?: number; // s entre el inicio del archivo (tras `recorte`) y su golpe
  recorte?: number; // s que se saltan del principio del archivo
  dur?: number; // s que se dejan sonar
};

const sfx: Sfx[] = [];
const TECLAS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => `tecla_${String(n).padStart(2, "0")}.wav`);
const SWOOSH = ["swoosh_a.wav", "swoosh_b.wav", "swoosh_c.wav", "swoosh_d.wav"];
let nTecla = 0;
let nSwoosh = 0;
const tecla = (t: number, vol = MEZCLA.tecla) =>
  sfx.push({ archivo: TECLAS[(nTecla++ * 3) % TECLAS.length], t, vol, adelanto: 0.01 });
const swoosh = (t: number) =>
  sfx.push({ archivo: SWOOSH[nSwoosh++ % SWOOSH.length], t, vol: MEZCLA.swooshDestacado, adelanto: 0.05 });
const pop = (t: number, vol = MEZCLA.pop) =>
  sfx.push({ archivo: "pop.mp3", t, vol, recorte: 0.12, adelanto: 0.04, dur: 0.5 });
const tick = (t: number, vol = MEZCLA.tick) => sfx.push({ archivo: "tick.mp3", t, vol, adelanto: 0.05 });
const whooshZoom = (t: number, vol = MEZCLA.whooshZoom) =>
  sfx.push({ archivo: "whoosh_zoom.mp3", t, vol, recorte: 0.36, adelanto: 0.18, dur: 0.7 });

// Subtítulos: cada palabra teclea; cada destacado hace swoosh; iconos y píldoras hacen pop.
for (const b of BLOQUES) {
  if (b.tipo === "normal") b.palabras.forEach((w) => tecla(w.t));
  if (b.tipo === "cita") b.lineas.flat().forEach((w) => tecla(w.t, MEZCLA.tecla * 1.25));
  if (b.tipo === "apilado") {
    b.linea1?.forEach((w) => tecla(w.t));
    if (!b.destacadoFijo) b.destacado.flat().forEach((w) => swoosh(w.t));
    b.iconos?.forEach((i) => pop(i.t));
    if (b.pildora) {
      pop(b.pildora[0].t - 0.13, MEZCLA.pop * 0.8);
      b.pildora.forEach((w) => tecla(w.t));
    }
  }
}

// Zoom del primer fotograma
sfx.push({ archivo: "swoosh_inicio.wav", t: 0.06, vol: MEZCLA.swooshInicio, adelanto: 0.06 });
// Destello de la píldora del gancho (cierra el bloque de título, como en la referencia)
sfx.push({ archivo: "brillo.wav", t: tw("gancho", 11) + 0.22, vol: MEZCLA.brillo, recorte: 0.55, adelanto: 0.2, dur: 1.2 });

// Transiciones de fuga de luz
for (const tr of TRANSICIONES_LUZ)
  sfx.push({ archivo: "whoosh_transicion.wav", t: tr.t, vol: MEZCLA.whooshTransicion, adelanto: 0.38, dur: 1.6 });

// Cortes con golpe de zoom
[C.cosechadora, C.vuelveContexto, C.mano, C.amtec, C.beneficio2, C.beneficio3, C.grano].forEach((t) => whooshZoom(t));
whooshZoom(C.presentacionCerca, MEZCLA.whooshZoom * 0.6);
whooshZoom(C.beneficio2Cerca, MEZCLA.whooshZoom * 0.6);

// Subida antes del bloque de beneficios
sfx.push({ archivo: "riser.mp3", t: C.graficoBeneficios, vol: MEZCLA.riser, adelanto: 1.79, dur: 2.0 });

// Motion graphics: golpe de entrada, ticks de números y tramos, tecleo de rótulos, pops de checks
for (const e of ESCENAS_BARRA) {
  sfx.push({ archivo: "golpe_grave.wav", t: e.desde, vol: MEZCLA.golpeGrave, adelanto: 0.01 });
  sfx.push({ archivo: "golpe_whoosh.wav", t: e.desde, vol: MEZCLA.golpeWhoosh, adelanto: 0.07 });
  if (e.construir) [0.13, 0.23, 0.43].forEach((d) => tick(e.desde + d, MEZCLA.tick * 0.8));
  e.encender.forEach((x) => {
    tick(e.desde + x.t);
    swoosh(e.desde + x.t);
  });
  e.rotulos.forEach((r) => {
    sfx.push({
      archivo: "tecleo_rafaga.wav",
      t: e.desde + r.lineas[0][0].t,
      vol: MEZCLA.tecleoRafaga,
      adelanto: 0.02,
      dur: Math.min(1.4, r.lineas.flat().slice(-1)[0].t - r.lineas[0][0].t + 0.45),
    });
  });
  e.checks.forEach((c) => pop(e.desde + c.t));
  if (e.pulsoFinal !== undefined) [0, 0.16, 0.32].forEach((d) => tick(e.desde + e.pulsoFinal! + d));
}

// Logo final
sfx.push({ archivo: "boom_logo.mp3", t: T_CIERRE + 0.02, vol: MEZCLA.boomLogo, adelanto: 0.06 });

export const EFECTOS: Sfx[] = sfx.sort((a, b) => a.t - b.t);
