import datos from '../public/voz-palabras.json';

export const FPS = 30;
export const cuadro = (seg: number) => Math.round(seg * FPS);

const limpio = (s: string) => s.replace(/[^\p{L}\p{N}]/gu, '').toLowerCase();

/** Cuadro en que empieza a sonar `texto` dentro de la frase número `frase` del guion. */
export const palabra = (frase: number, texto: string, aparicion = 1): number => {
	const lista = datos.palabras.filter((p) => p.frase === frase && limpio(p.visible) === limpio(texto));
	const p = lista[aparicion - 1];
	if (!p) throw new Error(`No encontré "${texto}" en la frase ${frase}`);
	return cuadro(p.inicio);
};

export const inicioFrase = (frase: number) => cuadro(datos.frases[frase].inicio);
export const finFrase = (frase: number) => cuadro(datos.frases[frase].fin);
export const DURACION_TOTAL = cuadro(datos.duracion);
