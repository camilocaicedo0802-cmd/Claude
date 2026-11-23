// Qué ocupa la zona SUPERIOR en cada momento de la opción B.
import { BEHIND } from "../edit/captions";
import { CUTS, T, TOTAL_SECONDS, seg } from "../timeline";
import { HeadlineT } from "./TopZone";

const k = (id: string) => {
  const b = BEHIND.find((x) => x.seg.startsWith(id));
  if (!b) throw new Error(`Sin palabra clave para ${id}`);
  return b;
};

/** Titulares de capítulo. Se retiran mientras la palabra gigante ocupa la zona y vuelven sin teclearse otra vez. */
export const HEADLINES: HeadlineT[] = [
  { start: T("s02", 6), end: k("s05").start - 0.1, eyebrow: "Perfil actoral", text: "El actor encasillado" },
  { start: k("s05").end + 0.14, end: CUTS.solucion - 0.12, eyebrow: "Perfil actoral", text: "El actor encasillado", typed: false },
  { start: CUTS.solucion, end: seg("s06").cuts[0], eyebrow: "La solución", text: "Personajes complejos" },
  { start: k("s06").end + 0.14, end: k("s10").start - 0.12, eyebrow: "La solución", text: "La estructura de BITS" },
  { start: seg("s11").start + 0.22, end: CUTS.testimonio - 0.17, eyebrow: "La solución", text: "La estructura de BITS", typed: false },
  { start: k("s13").end + 0.14, end: TOTAL_SECONDS + 1, eyebrow: "Masterclass gratis", text: "Qué es un BIT" },
];

/** Globo «PERSONAJE» del gancho: aparece con «el mismo personaje» y el nombre cambia tres veces. */
export const NAMES = [
  { t: T("s01", 8) + 0.2, text: "CARLOS" },
  { t: T("s01", 13), text: "ANDRÉS" },
  { t: T("s01", 14) + 0.12, text: "MATEO" },
  { t: T("s01", 16), text: "JULIÁN" },
];
