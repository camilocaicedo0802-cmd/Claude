// Lista de montaje (EDL). 30 fps; 90 BPM => 1 pulso = 20 fotogramas, 1 compás = 80.
// Audio: estribillo de BOMBASTIK desde 67,245 s (compás 25, el drop) durante 8 compases.
// Estructura calcada de la referencia (ver estilo.md §2): general espalda → macros espalda →
// delantero → macros espalda → general espalda fijo → general delantero.

export const FPS = 30;
export const BEAT = 20;
export const DURATION = 32 * BEAT; // 640 f = 21,33 s

// Dos cortes van al acento real del dembow (medido), no a la rejilla: 5,90 s y 17,89 s.
// Igual que en la referencia, donde los cortes caen en el golpe fuerte y no en cuadrícula.
const ACENTO_1 = 9 * BEAT - 3; // 177
const ACENTO_2 = 27 * BEAT - 3; // 537

export type Shot = {
	take: string; // archivo en public/tomas
	from: number; // segundo de la toma donde empieza el plano
	start: number; // fotograma de entrada en el timeline
	end: number; // fotograma de salida (exclusivo)
	diseno: 'espalda' | 'delantero';
};

export const SHOTS: Shot[] = [
	// 1. General espalda, girada, termina con acercamiento rápido (el "acelerón" de la referencia)
	{take: 'IMG_6016', from: 1.0, start: 0, end: 4 * BEAT, diseno: 'espalda'},
	// 2. Macro espalda: grafiti "EL CANTANTE DEL GHETTO" + retrato, paneo lento
	{take: 'IMG_6017', from: 0.6, start: 4 * BEAT, end: ACENTO_1, diseno: 'espalda'},
	// 3. Macro cara (corto)
	{take: 'IMG_6019', from: 1.0, start: ACENTO_1, end: 12 * BEAT, diseno: 'espalda'},
	// 4. Delantero de cerca, el logo crece — entra en "loba, loba bombastik" (compás de respiro)
	{take: 'IMG_6024', from: 5.2, start: 12 * BEAT, end: 16 * BEAT, diseno: 'delantero'},
	// 5. Macro espalda: "CASTRO" → retrato → grafiti, vuelve el beat
	{take: 'IMG_6018', from: 2.4, start: 16 * BEAT, end: 20 * BEAT, diseno: 'espalda'},
	// 6. Macro cara, encuadre distinto (jump cut corto)
	{take: 'IMG_6019', from: 7.3, start: 20 * BEAT, end: 22 * BEAT, diseno: 'espalda'},
	// 7. General espalda, recta y casi fija
	{take: 'IMG_6022', from: 6.87, start: 22 * BEAT, end: ACENTO_2, diseno: 'espalda'},
	// 8. General delantero con etiqueta del cuello, girando — cierre en "loba, loba bombastik"
	{take: 'IMG_6023', from: 4.0, start: ACENTO_2, end: 32 * BEAT, diseno: 'delantero'},
];
