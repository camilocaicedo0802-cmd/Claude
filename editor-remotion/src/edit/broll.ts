// B-roll (carpeta de recursos del cliente). Regla de estilo.md §4: ilustra literalmente la frase y dura una frase.
import { BEAT_PARTITURA, MODE, T } from "../timeline";

export const BROLL: { file: string; from: number; to: number; nota: string }[] = [
  { file: "media/broll/br_casting.mp4", from: T("s02", 0) - 0.02, to: T("s02", 6) - 0.04, nota: "«te llega un casting» · c63" },
  { file: "media/broll/br_piano.mp4", from: BEAT_PARTITURA.start - 0.05, to: BEAT_PARTITURA.end + 0.55, nota: "«partitura musical» · c298" },
  { file: "media/broll/br_tv.mp4", from: T("s11", 1) - 0.05, to: T("s11", 5) - 0.06, nota: "«en streaming» · c80" },
  { file: "media/broll/br_ojo.mp4", from: T("s11", 10) - 0.1, to: MODE.toTestimonio, nota: "«la atención de la audiencia» · Vídeo (7)" },
];
