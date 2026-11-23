// B-roll a pantalla completa en vertical. Regla de estilo.md §4: ilustra literalmente la frase y dura una frase.
import { BEAT_PARTITURA, CUTS, T } from "../timeline";

export const BROLL: { file: string; from: number; to: number; nota: string }[] = [
  { file: "media/broll/br_casting.mp4", from: T("s02", 0) - 0.02, to: T("s02", 6) - 0.04, nota: "«te llega un casting» · carpeta de recursos (c63)" },
  { file: "media/broll/br_partitura.mp4", from: BEAT_PARTITURA.start - 0.05, to: BEAT_PARTITURA.end + 0.5, nota: "«partitura» · Mixkit 41678, licencia libre" },
  { file: "media/broll/br_actriz.mp4", from: T("s11", 1) - 0.05, to: T("s11", 5) + 0.35, nota: "«personajes multidimensionales» · Mixkit 43403, licencia libre" },
  { file: "media/broll/br_ojo.mp4", from: T("s11", 10) - 0.1, to: CUTS.testimonio, nota: "«la atención de la audiencia» · carpeta de recursos (Vídeo 7)" },
];
