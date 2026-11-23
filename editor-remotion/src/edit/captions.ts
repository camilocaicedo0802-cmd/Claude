// Bloques de subtítulos. Regla (estilo.md §2.5): 4–7 palabras por bloque, 1 palabra clave, se omiten muletillas.
// Cada palabra lleva el instante exacto en que se pronuncia (Whisper, tiempos por palabra).
import { CapBlock, CapRow, CapWord } from "../components/Captions";
import { FULL_CY, LOWER_CY } from "../theme";
import { END, MODE, T, seg } from "../timeline";

const ws = (id: string, items: [number, string, CapWord["color"]?][]): CapWord[] =>
  items.map(([i, text, color]) => ({ t: T(id, i), text, color }));
const S = (id: string, items: [number, string, CapWord["color"]?][], align: CapRow["align"] = "left"): CapRow => ({ size: "S", align, words: ws(id, items) });
const M = (id: string, items: [number, string, CapWord["color"]?][], align: CapRow["align"] = "left", px?: number): CapRow => ({ size: "M", align, words: ws(id, items), px });
const L = (id: string, items: [number, string, CapWord["color"]?][], extra: Partial<CapRow> = {}): CapRow => ({ size: "L", align: "center", words: ws(id, items), ...extra });
const B = (start: number, end: number, cy: number, rows: CapRow[], extra: Partial<CapBlock> = {}): CapBlock => ({ start: start - 0.03, end, cy, rows, ...extra });

const TESTI_CY = 1390;
const TESTI = { maxW: 820, scale: 0.88 };

export const CAPTIONS: CapBlock[] = [
  // ───────── 1 · GANCHO (pantalla completa, texto sobre el pecho) ─────────
  B(T("s01", 0), T("s01", 6), FULL_CY, [
    S("s01", [[0, "Hay"], [1, "actores"], [2, "que"], [3, "llevan"]]),
    L("s01", [[4, "Años"]]),
    M("s01", [[5, "interpretando"]], "right"),
  ]),
  B(T("s01", 6), T("s01", 9), FULL_CY, [S("s01", [[6, "el"], [7, "mismo"]]), L("s01", [[8, "Personaje"]])]),
  B(T("s01", 9), MODE.toWindow, FULL_CY, [
    S("s01", [[9, "aunque"], [10, "en"], [11, "el"], [12, "guion"]]),
    M("s01", [[13, "les"], [14, "cambien"], [15, "el"]]),
    L("s01", [[16, "Nombre"]]),
  ]),

  // ───────── 2 · PROBLEMA ─────────
  B(T("s02", 0), T("s02", 4), LOWER_CY, [S("s02", [[0, "te"], [1, "llega"], [2, "un"]]), L("s02", [[3, "Casting"]])]),
  B(T("s02", 4), T("s02", 12), LOWER_CY, [
    S("s02", [[4, "y"], [5, "terminas"], [6, "utilizando"]]),
    L("s02", [[7, "El"], [8, "mismo"], [9, "tono"]]),
    M("s02", [[10, "de"], [11, "siempre"]], "right"),
  ]),
  // «las mismas intenciones / herramientas / reacciones» → fichas con icono
  B(T("s02", 12), seg("s03").start, LOWER_CY - 190, [S("s02", [[12, "las"], [13, "mismas", "lime"]], "center")]),

  B(T("s03", 0), T("s03", 8), LOWER_CY, [
    M("s03", [[0, "cambies"], [1, "de"], [2, "personaje"]]),
    S("s03", [[3, "pero"], [4, "no"], [5, "cambies"], [6, "de"]]),
    L("s03", [[7, "Propuesta"]]),
  ]),
  B(T("s03", 8), seg("s03").end, LOWER_CY, [
    S("s03", [[8, "eso"], [9, "no"], [10, "tiene"]]),
    L("s03", [[11, "Sentido"]], { strikeAt: T("s03", 11) + 0.22 }),
  ]),

  B(T("s04", 0), T("s04", 7) - 0.08, LOWER_CY, [
    S("s04", [[0, "¿Y"], [1, "sabes"], [2, "qué"], [3, "es"], [4, "lo"], [5, "que"]]),
    L("s04", [[6, "Escucho?"]]),
  ]),
  // «a mí me tienen encasillado» / «mi mánager no me envía…» → tarjetas de alerta

  B(T("s05", 0), T("s05", 7), LOWER_CY, [
    S("s05", [[0, "pero"], [1, "realmente"]]),
    L("s05", [[2, "El"], [3, "problema"]]),
    M("s05", [[4, "está"], [5, "en"], [6, "las"]], "right"),
  ]),
  B(T("s05", 7), seg("s05").end + 0.08, LOWER_CY, [
    L("s05", [[7, "Decisiones"]]),
    M("s05", [[8, "que"], [9, "tú", "lime"], [10, "tomas"]]),
    S("s05", [[11, "enfrente"], [12, "de"], [13, "la"], [14, "cámara"]], "right"),
  ]),

  // ───────── 3 · SOLUCIÓN ─────────
  B(T("s06", 0), T("s06", 8), LOWER_CY, [
    S("s06", [[0, "si"], [1, "quieres"], [2, "interpretar"]]),
    L("s06", [[3, "Personajes"]]),
    M("s06", [[4, "más"], [5, "complejos"]], "right"),
    S("s06", [[6, "para"], [7, "streaming", "lime"]], "right"),
  ]),
  B(T("s06", 8), T("s06", 17), LOWER_CY, [
    S("s06", [[8, "necesitas"], [9, "aprender"], [10, "la"]]),
    M("s06", [[11, "estructura"], [12, "de"]]),
    L("s06", [[13, "BITS"]]),
    S("s06", [[14, "de"], [15, "una"], [16, "escena"]], "right"),
  ]),
  // «y sobre todo aprender a transitarlos» → línea de BITS (graphics.ts) con estas dos filas:
  B(T("s06", 17), seg("s06").end + 0.1, LOWER_CY - 190, [S("s06", [[17, "y"], [18, "sobre"], [19, "todo"], [20, "aprender"], [21, "a"]], "center")]),
  B(T("s06", 22), seg("s06").end + 0.1, LOWER_CY + 170, [L("s06", [[22, "Transitarlos"]])]),

  // «la combinación y la transición entre ellas es lo que crea la melodía» + pentagrama
  B(T("s08", 0), T("s08", 7), LOWER_CY + 120, [
    S("s08", [[0, "la"], [1, "combinación"], [2, "y"], [3, "la"]]),
    M("s08", [[4, "transición", "lime"], [5, "entre"], [6, "ellas"]]),
  ]),
  B(T("s08", 7), seg("s09").start, LOWER_CY + 120, [
    S("s08", [[7, "es"], [8, "lo"], [9, "que"], [10, "crea"], [11, "la"]]),
    L("s08", [[12, "Melodía"]]),
  ]),

  // «en actuación cada BIT es una acción que busca provocar un cambio» → fichas BIT · ACCIÓN · CAMBIO
  B(T("s09", 0), T("s09", 7), LOWER_CY - 190, [S("s09", [[0, "en"], [1, "actuación"], [2, "cada"], [3, "BIT", "lime"], [4, "es"], [5, "una"], [6, "acción"]], "center")]),
  B(T("s09", 7), seg("s10").start, LOWER_CY - 190, [S("s09", [[7, "que"], [8, "busca"], [9, "provocar"], [10, "un"], [11, "cambio", "lime"]], "center")]),

  B(T("s10", 0), T("s10", 7), LOWER_CY, [
    S("s10", [[0, "y"], [1, "esas"]]),
    L("s10", [[2, "Transiciones"]]),
    S("s10", [[3, "son"], [4, "las"], [5, "que"], [6, "permiten"]], "right"),
  ]),
  B(T("s10", 7), seg("s10").end, LOWER_CY, [
    S("s10", [[7, "que"], [8, "el"]]),
    M("s10", [[9, "conflicto"]]),
    L("s10", [[10, "Avance"]]),
  ]),

  B(T("s11", 0), T("s11", 4), LOWER_CY, [
    S("s11", [[0, "porque"], [1, "en"]]),
    L("s11", [[2, "Streaming"]]),
    M("s11", [[3, "necesitamos"]], "right"),
  ]),
  B(T("s11", 4), T("s11", 6), LOWER_CY, [S("s11", [[4, "personajes"]]), L("s11", [[5, "Multidimensionales"]])]),
  B(T("s11", 6), T("s11", 8), LOWER_CY, [S("s11", [[6, "que"]]), L("s11", [[7, "Sorprendan"]])]),
  B(T("s11", 8), seg("s11").end, LOWER_CY, [
    S("s11", [[8, "y"], [9, "mantengan"], [10, "la"]]),
    L("s11", [[11, "Atención"]]),
    M("s11", [[12, "de"], [13, "la"], [14, "audiencia"]], "right"),
  ]),

  // ───────── 4 · PRUEBA SOCIAL (testimonio de Alberto; subtítulos bajo la tarjeta) ─────────
  B(T("s12", 0), T("s12", 5), TESTI_CY, [S("s12", [[0, "hasta"], [1, "que"], [2, "conocí"], [3, "los"]]), L("s12", [[4, "BITS"]])], TESTI),
  B(T("s12", 5), T("s12", 14), TESTI_CY, [
    S("s12", [[5, "y"], [6, "cómo"], [7, "yo"], [8, "podía"]]),
    M("s12", [[9, "en"], [10, "cada"], [11, "uno"], [12, "de"], [13, "ellos"]]),
  ], TESTI),
  B(T("s12", 14), T("s12", 17), TESTI_CY, [S("s12", [[14, "tener"], [15, "una"]]), L("s12", [[16, "Acción"]])], TESTI),
  B(T("s12", 17), T("s12", 21), TESTI_CY, [S("s12", [[17, "que"], [18, "me"], [19, "llevara"]]), L("s12", [[20, "Directo"]])], TESTI),
  B(T("s12", 21), MODE.toFull, TESTI_CY, [
    S("s12", [[21, "a"], [22, "lo"], [23, "que"], [24, "yo"], [25, "quería"]]),
    M("s12", [[26, "obtener"], [27, "de"], [28, "mi"]]),
    L("s12", [[29, "Partner"]]),
  ], TESTI),

  // ───────── 5 · CTA ─────────
  B(T("s13", 0), T("s13", 8), FULL_CY, [
    S("s13", [[0, "así"], [1, "que"]]),
    L("s13", [[2, "No"], [3, "te"], [4, "repitas"]]),
    M("s13", [[5, "año"], [6, "tras"], [7, "año"]], "right"),
  ]),
  B(T("s13", 8), MODE.morphStart, FULL_CY, [S("s13", [[8, "en"], [9, "los"], [10, "mismos"]]), L("s13", [[11, "Personajes"]])]),

  // «Comenta BIT» → píldora verde tecleada
  B(T("s14", 0), T("s14", 2) - 0.02, LOWER_CY - 122, [M("s14", [[0, "Comenta"]], "center")]),
  B(T("s14", 2), T("s14", 7), LOWER_CY, [
    S("s14", [[2, "y"], [3, "te"], [4, "regalo"], [5, "la"]]),
    L("s14", [[6, "Masterclass"]]),
  ]),
  B(T("s14", 7), T("s14", 17), LOWER_CY - 170, [
    S("s14", [[7, "donde"], [8, "te"], [9, "enseño"], [10, "a"], [11, "identificar"]], "center"),
    S("s14", [[12, "los"], [13, "BITS", "lime"], [14, "de"], [15, "una"], [16, "escena"]], "center"),
  ]),
  B(T("s14", 17), END("s14") + 0.12, LOWER_CY, [
    S("s14", [[17, "para"], [18, "que"], [19, "los"], [20, "apliques"], [21, "en"]]),
    M("s14", [[22, "tu"], [23, "próximo"]]),
    L("s14", [[24, "Casting"]]),
  ]),
  // Cierre: se repite la llamada a la acción
  { start: END("s14") + 0.2, end: 999, cy: LOWER_CY - 122, rows: [{ size: "M", align: "center", words: [{ t: END("s14") + 0.24, text: "Comenta" }] }] },
  { start: END("s14") + 0.9, end: 999, cy: LOWER_CY + 170, rows: [{ size: "S", align: "center", words: [{ t: END("s14") + 0.95, text: "y" }, { t: END("s14") + 1.02, text: "te" }, { t: END("s14") + 1.09, text: "regalo" }, { t: END("s14") + 1.16, text: "la" }, { t: END("s14") + 1.23, text: "masterclass", color: "lime" }] }] },
];
