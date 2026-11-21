import datos from '../public/voz-palabras.json';

/*
 * Mezcla del short: la voz siempre manda. Efectos y música se agachan mientras habla.
 * La música (piano de cabaret + tic-tac en la escalada) se corta en el giro y ya no vuelve.
 */

const FPS = 30;
const N = Math.ceil(datos.duracion * FPS) + 120;

const envolvente = (() => {
	const activo = new Float32Array(N);
	for (const p of datos.palabras) {
		const a = Math.floor(p.inicio * FPS) - 3;
		const b = Math.ceil((p.inicio + p.duracion) * FPS) + 3;
		for (let i = Math.max(0, a); i < Math.min(N, b); i++) activo[i] = 1;
	}
	const env = new Float32Array(N);
	let v = 0;
	for (let i = 0; i < N; i++) {
		v = activo[i] > v ? Math.min(1, v + 0.5) : Math.max(0, v - 0.1);
		env[i] = v;
	}
	let w = 0;
	for (let i = N - 1; i >= 0; i--) {
		w = activo[i] > w ? Math.min(1, w + 0.5) : Math.max(0, w - 0.34);
		env[i] = Math.max(env[i], w);
	}
	return env;
})();

export const vozEn = (f: number) => envolvente[Math.max(0, Math.min(N - 1, Math.round(f)))];

export const GANANCIA_FX = 0.42;
export const DUCK_FX = 0.3;
const RECORTE: Record<string, number> = {sello: 0.6, fuego: 0.6, aplausos: 0.7, chillido: 0.7};

export const volumenFx = (archivo: string, base: number, fGlobal: number) => base * GANANCIA_FX * (RECORTE[archivo] ?? 1) * (1 - (1 - DUCK_FX) * vozEn(fGlobal));

/** la música ya viene cortada en el giro (musica.wav); aquí solo su nivel bajo la voz */
export const MUSICA_BASE = 0.13;
export const volumenMusica = (f: number, total: number, base = MUSICA_BASE) => {
	const salida = Math.min(1, Math.max(0, (total - f) / 12));
	return base * salida * (1 - 0.35 * vozEn(f));
};
