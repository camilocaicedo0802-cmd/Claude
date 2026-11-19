import datos from '../public/voz-palabras.json';

/*
 * Mezcla: la voz siempre manda.
 * - Todos los efectos bajan GANANCIA_FX de base.
 * - Mientras suena la voz, efectos y música se "agachan" (ducking) y vuelven a subir en las pausas.
 * - Los efectos más densos (truenos, temblores, olas, explosiones) llevan un recorte extra.
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
	// ataque rápido (~2 cuadros) y liberación suave (~10 cuadros), en ambos sentidos
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

/** 0 = silencio, 1 = la voz está sonando (suavizado). */
export const vozEn = (f: number) => envolvente[Math.max(0, Math.min(N - 1, Math.round(f)))];

export const GANANCIA_FX = 0.42; // ≈ -7,5 dB para todos los efectos
export const DUCK_FX = 0.3; // mientras habla, los efectos quedan al 30 % (≈ -10 dB)
const RECORTE: Record<string, number> = {choque: 0.55, sirena: 0.5, motor: 0.6, trueno: 0.55, temblor: 0.38, ola: 0.6, boom: 0.6, dundun: 0.45, sello: 0.6, aplausos: 0.7, viento: 0.6};

const FR = datos.frases;
const C = (seg: number) => Math.round(seg * FPS);
/** silencio total del giro: del fin de «Y Rockstar lo confirma:» al inicio de «los videos son reales» */
export const GIRO: [number, number] = [C(FR[12].fin), C(FR[13].inicio)];
/** el murmullo de la oficina se corta de golpe cuando empieza la amenaza */
const CORTE_MURMULLO = C(FR[11].inicio);
const REMATE = C(FR[19].inicio);
const ULTIMA = C(FR[21].inicio);

export const volumenFx = (archivo: string, base: number, fGlobal: number) => {
	if (fGlobal >= GIRO[0] && fGlobal < GIRO[1]) return 0;
	if (archivo === 'murmullo' && fGlobal >= CORTE_MURMULLO) return 0;
	return base * GANANCIA_FX * (RECORTE[archivo] ?? 1) * (1 - (1 - DUCK_FX) * vozEn(fGlobal));
};

/** Música (synthwave propia): 15–18 dB bajo la voz; se corta en el giro y vuelve más fuerte; se apaga en el remate. */
export const MUSICA_BASE = 0.147;
export const volumenMusica = (f: number, total: number, base = MUSICA_BASE) => {
	const entrada = Math.min(1, f / 4);
	if (f >= GIRO[0] && f < GIRO[1]) return 0;
	const despues = f >= GIRO[1] ? 1.3 : 1;
	const remate = f < REMATE ? 1 : Math.max(0, 1 - (f - REMATE) / Math.max(1, ULTIMA - REMATE));
	const salida = Math.min(1, Math.max(0, (total - f) / 30));
	return base * entrada * despues * remate * salida * (1 - 0.25 * vozEn(f));
};
