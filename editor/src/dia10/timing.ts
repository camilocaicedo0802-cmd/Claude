import { crearAt, HOLD, Word } from "../rutinas/util";
import edit from "./data/edit.json";

// Línea de tiempo del vídeo del día 10 ya editado (scripts/dia10/preparar.py + scripts/dia10/retiempos.py)
export const WORDS: Word[] = edit.words;
export const DURATION: number = edit.duration;
export const TOTAL = DURATION + HOLD;
export const at = crearAt(WORDS);
