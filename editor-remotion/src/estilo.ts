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
  desenfoqueMax: 7, // px en el primer fotograma del golpe
};

export const TRANSICION_LUZ = {
  durAnillo: 0.14,
  durSubida: 0.14, // la fuga cubre el cuadro antes del corte
  durBajada: 0.24, // y se disuelve sobre el plano nuevo
  opacidadMax: 0.9,
};

// ── Sonido (§11) ─────────────────────────────────────────────────────────────
export const MEZCLA = {
  voz: 1.0,
  musica: 0.085, // ≈ 20 dB por debajo de la voz
  musicaSinVoz: 0.3, // cierre
  tecla: 0.16,
  swooshDestacado: 0.3,
  pop: 0.34,
  tick: 0.3,
  whooshZoom: 0.5,
  whooshTransicion: 0.62,
  golpeGrave: 0.38,
  riser: 0.3,
  brillo: 0.22,
  tecleoRafaga: 0.3,
};
