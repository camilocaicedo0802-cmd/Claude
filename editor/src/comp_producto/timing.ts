import { crearAt, HOLD, Word } from "../rutinas/util";
import edit from "./data/edit.json";

// Línea de tiempo de la voz en off ya limpia (scripts/rutinas/preparar_voz.py comp_producto + scripts/dia9/retiempos.py)
export const WORDS: Word[] = edit.words;
export const DURATION: number = edit.duration;
export const TOTAL = DURATION + HOLD;
export const at = crearAt(WORDS);
