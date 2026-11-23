// Bloques de subtítulos. Regla (estilo.md §2.5): 4–7 palabras por bloque, 1 palabra clave, se omiten muletillas.
// Cada palabra lleva el instante exacto en que se pronuncia (Whisper, tiempos por palabra).
import { BehindBlockT, CapBlock, CapRow, CapWord } from "../components/Captions";
import { CHEST_CY, GFX_CY, LOW_CY, TOP_CY } from "../theme";
import { CUTS, END, T, seg } from "../timeline";

type Item = [number, string, CapWord["color"]?];
const ws = (id: string, items: Item[]): CapWord[] => items.map(([i, text, color]) => ({ t: T(id, i), text, color }));
const S = (id: string, items: Item[], align: CapRow["align"] = "left"): CapRow => ({ size: "S", align, words: ws(id, items) });
/** Fila pequeña partida: un grupo a la izquierda y otro a la derecha, encajados sobre la palabra clave. */
const S2 = (id: string, left: Item[], right: Item[]): CapRow => ({ size: "S", words: ws(id, left), right: ws(id, right) });
const M = (id: string, items: Item[], align: CapRow["align"] = "left", px?: number): CapRow => ({ size: "M", align, words: ws(id, items), px });
const L = (id: string, items: Item[], extra: Partial<CapRow> = {}): CapRow => ({ size: "L", align: "center", words: ws(id, items), ...extra });
const B = (start: number, end: number, cy: number, rows: CapRow[], extra: Partial<CapBlock> = {}): CapBlock => ({ start: start - 0.03, end, cy, rows, ...extra });

const TESTI = { maxW: 860, scale: 0.9 };
const WIDE_CY = 1215; // plano abierto: fila de continuación sobre el pecho

// ───────── Texto DETRÁS del sujeto (plano abierto; la cabeza tapa parte de la palabra gigante) ─────────
export const BEHIND: BehindBlockT[] = [
  { seg: "s01_hook", start: T("s01", 0) - 0.03, end: T("s01", 6), top: 205, small: ws("s01", [[0, "Hay"], [1, "actores"], [2, "que"], [3, "llevan"]]), big: ws("s01", [[4, "Años"]]) },
  { seg: "s05_decisiones", start: T("s05", 0) - 0.03, end: T("s05", 7), top: 255, small: ws("s05", [[0, "pero"], [1, "realmente"], [2, "el"]]), big: ws("s05", [[3, "Problema"]]) },
  { seg: "s06_bits", start: T("s06", 11) - 0.03, end: T("s06", 17), top: 205, small: ws("s06", [[11, "estructura"], [12, "de"]]), big: ws("s06", [[13, "BITS"]]) },
  { seg: "s10_conflicto", start: T("s10", 7) - 0.03, end: seg("s11").start, top: 235, small: ws("s10", [[7, "que"], [8, "el"], [9, "conflicto"]]), big: ws("s10", [[10, "Avance"]]) },
  { seg: "s13_repitas", start: T("s13", 0) - 0.03, end: T("s13", 8), top: 290, small: ws("s13", [[0, "así"], [1, "que"], [2, "no"], [3, "te"]]), big: ws("s13", [[4, "Repitas"]]) },
];

export const CAPTIONS: CapBlock[] = [
  // ───────── 1 · GANCHO ─────────
  // «Hay actores que llevan AÑOS» → detrás del sujeto (BEHIND); la continuación va delante, sobre el pecho
  B(T("s01", 5), T("s01", 6), WIDE_CY, [M("s01", [[5, "interpretando"]], "center")]),
  B(T("s01", 6), T("s01", 9), CHEST_CY, [S("s01", [[6, "el"], [7, "mismo"]]), L("s01", [[8, "Personaje"]])]),
  B(T("s01", 9), CUTS.problema, CHEST_CY, [
    S("s01", [[9, "aunque"], [10, "en"], [11, "el"], [12, "guion"]]),
    M("s01", [[13, "les"], [14, "cambien"], [15, "el"]]),
    L("s01", [[16, "Nombre"]]),
  ]),

  // ───────── 2 · PROBLEMA ─────────
  B(T("s02", 0), T("s02", 4), LOW_CY, [S("s02", [[0, "te"], [1, "llega"], [2, "un"]]), L("s02", [[3, "Casting"]])]),
  B(T("s02", 4), T("s02", 12), CHEST_CY, [
    S2("s02", [[4, "y"], [5, "terminas"]], [[6, "utilizando"]]),
    L("s02", [[7, "El"], [8, "mismo"], [9, "tono"]]),
    M("s02", [[10, "de"], [11, "siempre"]], "right"),
  ]),
  // «las mismas intenciones / herramientas / reacciones» → fichas con icono
  B(T("s02", 12), seg("s03").start, GFX_CY - 205, [S("s02", [[12, "las"], [13, "mismas", "accent"]], "center")]),

  B(T("s03", 0), T("s03", 8), CHEST_CY, [
    M("s03", [[0, "cambies"], [1, "de"], [2, "personaje"]]),
    S("s03", [[3, "pero"], [4, "no"], [5, "cambies"], [6, "de"]]),
    L("s03", [[7, "Propuesta"]]),
  ]),
  B(T("s03", 8), seg("s03").end, CHEST_CY, [S("s03", [[8, "eso"], [9, "no"], [10, "tiene"]]), L("s03", [[11, "Sentido"]], { strikeAt: T("s03", 11) + 0.22 })]),

  B(T("s04", 0), T("s04", 7) - 0.08, CHEST_CY, [S2("s04", [[0, "¿Y"], [1, "sabes"]], [[2, "qué"], [3, "es"], [4, "lo"], [5, "que"]]), L("s04", [[6, "Escucho?"]])]),
  // «a mí me tienen encasillado» / «mi mánager no me envía…» → tarjetas de alerta

  // «pero realmente el PROBLEMA» → detrás del sujeto (BEHIND)
  B(T("s05", 4), T("s05", 7), WIDE_CY, [M("s05", [[4, "está"], [5, "en"], [6, "las"]], "center")]),
  B(T("s05", 7), CUTS.solucion, CHEST_CY, [
    L("s05", [[7, "Decisiones"]]),
    M("s05", [[8, "que"], [9, "tú", "accent"], [10, "tomas"]]),
    S("s05", [[11, "enfrente"], [12, "de"], [13, "la"], [14, "cámara"]], "right"),
  ]),

  // ───────── 3 · SOLUCIÓN ─────────
  B(T("s06", 0), T("s06", 8), CHEST_CY, [
    S2("s06", [[0, "si"], [1, "quieres"]], [[2, "interpretar"]]),
    L("s06", [[3, "Personajes"]]),
    M("s06", [[4, "más"], [5, "complejos"]], "right"),
    S("s06", [[6, "para"], [7, "streaming", "accent"]], "right"),
  ]),
  B(T("s06", 8), T("s06", 11), CHEST_CY, [M("s06", [[8, "necesitas"], [9, "aprender"]]), S("s06", [[10, "la"]], "right")]),
  // «estructura de BITS» → detrás del sujeto (BEHIND)
  B(T("s06", 14), T("s06", 17), WIDE_CY, [M("s06", [[14, "de"], [15, "una"], [16, "escena"]], "center")]),
  // «y sobre todo aprender a transitarlos» → línea de BITS con estas dos filas:
  B(T("s06", 17), seg("s06").end + 0.1, GFX_CY - 200, [S("s06", [[17, "y"], [18, "sobre"], [19, "todo"], [20, "aprender"], [21, "a"]], "center")]),
  B(T("s06", 22), seg("s06").end + 0.1, GFX_CY + 168, [L("s06", [[22, "Transitarlos"]])]),

  // «la combinación y la transición entre ellas es lo que crea la melodía» + pentagrama
  B(T("s08", 0), T("s08", 7), GFX_CY + 110, [S("s08", [[0, "la"], [1, "combinación"], [2, "y"], [3, "la"]]), M("s08", [[4, "transición", "accent"], [5, "entre"], [6, "ellas"]])]),
  B(T("s08", 7), seg("s09").start, GFX_CY + 110, [S("s08", [[7, "es"], [8, "lo"], [9, "que"], [10, "crea"], [11, "la"]]), L("s08", [[12, "Melodía"]])]),

  // «en actuación cada BIT es una acción que busca provocar un cambio» → fichas BIT · ACCIÓN · CAMBIO
  B(T("s09", 0), T("s09", 7), GFX_CY - 205, [S("s09", [[0, "en"], [1, "actuación"], [2, "cada"], [3, "BIT", "accent"], [4, "es"], [5, "una"], [6, "acción"]], "center")]),
  B(T("s09", 7), seg("s10").start, GFX_CY - 205, [S("s09", [[7, "que"], [8, "busca"], [9, "provocar"], [10, "un"], [11, "cambio", "accent"]], "center")]),

  B(T("s10", 0), T("s10", 7), CHEST_CY, [S("s10", [[0, "y"], [1, "esas"]]), L("s10", [[2, "Transiciones"]]), S("s10", [[3, "son"], [4, "las"], [5, "que"], [6, "permiten"]], "right")]),
  // «que el conflicto AVANCE» → detrás del sujeto (BEHIND)

  B(T("s11", 0), T("s11", 4), LOW_CY, [S("s11", [[0, "porque"], [1, "en"]]), L("s11", [[2, "Streaming"]]), M("s11", [[3, "necesitamos"]], "right")]),
  B(T("s11", 4), T("s11", 6), LOW_CY, [S("s11", [[4, "personajes"]]), L("s11", [[5, "Multidimensionales"]])]),
  B(T("s11", 6), T("s11", 8), CHEST_CY, [S("s11", [[6, "que"]]), L("s11", [[7, "Sorprendan"]])]),
  B(T("s11", 8), CUTS.testimonio, LOW_CY, [S("s11", [[8, "y"], [9, "mantengan"], [10, "la"]]), L("s11", [[11, "Atención"]]), M("s11", [[12, "de"], [13, "la"], [14, "audiencia"]], "right")]),

  // ───────── 4 · PRUEBA SOCIAL (testimonio de Alberto, pantalla completa; subtítulos arriba, sobre la pared) ─────────
  B(T("s12", 0), T("s12", 3), TOP_CY, [S("s12", [[0, "parcero,"], [1, "actor,"]]), L("s12", [[2, "Camarada"]])], TESTI),
  B(T("s12", 3), T("s12", 12), TOP_CY, [S("s12", [[3, "oigan,"], [4, "les"], [5, "cuento"], [6, "que"]]), S("s12", [[7, "cuando"], [8, "estoy"], [9, "presentando"]]), L("s12", [[10, "Mis"], [11, "castings"]])], TESTI),
  B(T("s12", 12), T("s12", 20), TOP_CY, [S("s12", [[12, "o"], [13, "cuando"], [14, "estoy"], [15, "en"], [16, "medio"], [17, "de"]]), L("s12", [[18, "Alguna"], [19, "escena"]])], TESTI),
  B(T("s12", 20), T("s12", 28), TOP_CY, [S("s12", [[20, "lo"], [21, "que"], [22, "más"]]), L("s12", [[23, "Me"], [24, "costaba"]]), S("s12", [[25, "a"], [26, "mí"], [27, "era"]], "right")], TESTI),
  B(T("s12", 28), T("s12", 34), TOP_CY, [M("s12", [[28, "mantenerme"]]), S("s12", [[29, "durante"], [30, "toda"], [31, "la"], [32, "escena"]]), L("s12", [[33, "Arriba"]])], TESTI),
  B(T("s12", 34), T("s12", 37), TOP_CY, [S("s12", [[34, "sin"], [35, "dejarla"]]), L("s12", [[36, "Caer"]])], TESTI),
  B(T("s12", 37), T("s12", 42), TOP_CY, [S("s12", [[37, "hasta"], [38, "que"], [39, "conocí"], [40, "los"]]), L("s12", [[41, "BITS"]])], TESTI),
  B(T("s12", 42), T("s12", 49), TOP_CY, [S("s12", [[42, "y"], [43, "ahí"], [44, "aprendí"], [45, "que"]]), M("s12", [[46, "en"], [47, "cada"]]), L("s12", [[48, "Línea"]])], TESTI),
  B(T("s12", 49), T("s12", 55), TOP_CY, [S("s12", [[49, "iba"], [50, "siguiendo"], [51, "con"]]), M("s12", [[52, "una"], [53, "acción", "accent"]]), L("s12", [[54, "Diferente"]])], TESTI),
  B(T("s12", 55), T("s12", 62), TOP_CY, [S("s12", [[55, "que"], [56, "me"], [57, "iba"], [58, "llevando"], [59, "a"]]), M("s12", [[60, "ese"]]), L("s12", [[61, "Objetivo"]])], TESTI),
  B(T("s12", 62), CUTS.cta, TOP_CY, [S("s12", [[62, "que"], [63, "era"], [64, "obtener"]]), M("s12", [[65, "la"], [66, "respuesta"], [67, "de"], [68, "mi"]], "left", 74), L("s12", [[69, "Partner"]])], TESTI),

  // ───────── 5 · CTA ─────────
  // «Así que no te REPITAS» → detrás del sujeto (BEHIND)
  B(T("s13", 5), T("s13", 8), WIDE_CY, [M("s13", [[5, "año"], [6, "tras"], [7, "año"]], "center")]),
  B(T("s13", 8), seg("s14").start, CHEST_CY, [S("s13", [[8, "en"], [9, "los"], [10, "mismos"]]), L("s13", [[11, "Personajes"]])]),

  // «Comenta BIT» → píldora tecleada
  B(T("s14", 0), T("s14", 2) - 0.02, GFX_CY - 128, [M("s14", [[0, "Comenta"]], "center")]),
  B(T("s14", 2), T("s14", 7), CHEST_CY, [S("s14", [[2, "y"], [3, "te"], [4, "regalo"], [5, "la"]]), L("s14", [[6, "Masterclass"]])]),
  B(T("s14", 7), T("s14", 17), GFX_CY - 150, [
    S("s14", [[7, "donde"], [8, "te"], [9, "enseño"], [10, "a"], [11, "identificar"]], "center"),
    S("s14", [[12, "los"], [13, "BITS", "accent"], [14, "de"], [15, "una"], [16, "escena"]], "center"),
  ]),
  B(T("s14", 17), END("s14") + 1, CHEST_CY, [S("s14", [[17, "para"], [18, "que"], [19, "los"], [20, "apliques"], [21, "en"]]), M("s14", [[22, "tu"], [23, "próximo"]]), L("s14", [[24, "Casting"]])]),
];
