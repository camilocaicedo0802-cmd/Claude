// Constantes de estilo. Cada valor sale de estilo.md (sección entre paréntesis).
// Si se cambia algo aquí, hay que reflejarlo en estilo.md.

export const FPS = 60;
export const ANCHO = 1080;
export const ALTO = 1920;

// ── Paleta del logo AgroKrack (estilo.md §12) ────────────────────────────────
export const COLOR = {
  verdeOscuro: "#0B211D",
  verdeFondo: "#17402F",
  verde: "#4BB54D",
  verdeVivo: "#4DC351",
  verdeClaro: "#B6E86A",
  naranja: "#DC8956",
  naranjaVivo: "#E69057",
  dorado: "#F2C48A",
  doradoClaro: "#F7DDB0",
  crema: "#DED5C8",
  blanco: "#FFFFFF",
};

// Degradado horizontal de los destacados (§5): naranja → dorado claro → naranja.
export const DEGRADADO_DESTACADO = `linear-gradient(90deg, ${COLOR.naranjaVivo} 0%, #EDA76B 28%, ${COLOR.dorado} 46%, ${COLOR.doradoClaro} 62%, #EFB57A 82%, ${COLOR.naranjaVivo} 100%)`;
// Segundo acento (verde del logo): tramo activo, checks y flechas.
export const DEGRADADO_VERDE = `linear-gradient(90deg, ${COLOR.verdeVivo} 0%, #86D95C 55%, ${COLOR.verdeClaro} 100%)`;

// ── Tipografía (§4, §5, §12) ─────────────────────────────────────────────────
// La referencia usa Helvetica Neue. Sustitutas libres:
//  · subtítulos → Inter Display Light (≈ Helvetica Neue Light)
//  · destacados y cita → TeX Gyre Heros Bold / Bold Italic (clon libre de Helvetica)
// Para usar Helvetica Neue original: cambia los archivos en src/fuentes.ts.
export const FUENTE = {
  normal: "AK Subtitulo",
  fuerte: "AK Destacado",
};

export const SUB = {
  tam: 70, // px (§4)
  interletraje: -0.05, // em
  separacionPalabras: 0.2, // em entre palabras
  caida: 12, // px que cae cada palabra al entrar
  giro: -3, // grados de inclinación inicial
  durEntrada: 0.1, // s
  adelanto: 0.0, // s respecto al inicio de palabra de Whisper ya afinado
  // Resplandor blanco suave + sombra negra. Más cerrada que en la referencia porque aquí el
  // texto cae sobre ropa clara y arroz amarillo, no sobre una camiseta oscura.
  sombra:
    "0 0 3px rgba(0,0,0,0.6), 0 2px 8px rgba(0,0,0,0.7), 0 0 24px rgba(0,0,0,0.6), 0 0 56px rgba(0,0,0,0.4), 0 0 14px rgba(255,255,255,0.22)",
};

export const DEST = {
  tam: 108, // px por defecto (§5: 90–115)
  interletraje: -0.04,
  separacionPalabras: 0.22,
  popDe: 1.1, // escala inicial del pop
  durPop: 0.12, // s
  atenuacionLineaAnterior: 0.62, // la referencia baja al 50 %; aquí algo menos por el fondo claro
  resplandor: "drop-shadow(0 0 22px rgba(232,135,58,0.55)) drop-shadow(0 6px 10px rgba(0,0,0,0.6))",
};

export const PILDORA = {
  alto: 78,
  margenX: 24,
  tam: 62,
  borde: 2,
  colorBorde: "#CFE9A8", // crema-verde: segundo acento del logo
  durBarrido: 0.07,
  retardoTexto: 0.13,
};

export const CITA = {
  tam: 66,
  interlineado: 1.08,
  opacidadPendiente: 0.35,
};

export const MARCA_DE_AGUA = {
  texto: "AgroKrack",
  tam: 54,
  y: 1832,
  opacidad: 0.3,
};

// ── Movimiento (§3, §9) ──────────────────────────────────────────────────────
export const ZOOM = {
  golpeInicio: 1.34,
  golpeTransicion: 1.28,
  golpeAcercar: 0.84, // 1/1,19: el plano empieza abierto y se acerca
  dur: 0.65,
  desenfoqueMax: 4.5, // px de desenfoque de movimiento al empezar el golpe
};

export const TRANSICION_LUZ = {
  durAnillo: 0.14,
  durSubida: 0.14, // la fuga cubre el cuadro antes del corte
  durBajada: 0.24, // y se disuelve sobre el plano nuevo
  opacidadMax: 0.9,
};

// ── Sonido (§11) ─────────────────────────────────────────────────────────────
// Volúmenes calibrados por pico (dBFS entre paréntesis). La voz está nivelada a -15 LUFS.
export const MEZCLA = {
  voz: 1.0,
  musica: 0.085, // ≈ 19 dB por debajo de la voz, como en la referencia
  musicaSinVoz: 0.5, // resumen final y logo
  tecla: 0.12, // (-19) tecleo de cada palabra
  swooshDestacado: 0.225, // (-13) palabra destacada
  swooshInicio: 0.36, // (-9) zoom del primer fotograma
  pop: 0.24, // (-13) iconos, píldoras, checks
  tick: 0.34, // (-14) números y tramos del gráfico
  whooshZoom: 0.46, // (-11) golpe de zoom en los cortes
  whooshTransicion: 1.0, // (-7) transición de fuga de luz
  golpeGrave: 0.37, // (-9) entrada de motion graphic
  golpeWhoosh: 0.37, // (-11)
  riser: 0.29, // (-13)
  brillo: 0.17, // (-16)
  tecleoRafaga: 0.42, // (-15) rótulos que se escriben
  boomLogo: 0.8, // (-7)
};
