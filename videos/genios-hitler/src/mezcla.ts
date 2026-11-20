import datos from '../public/voz-palabras.json';

/*
 * Mezcla: la voz siempre manda.
 * - Todos los efectos bajan GANANCIA_FX de base.
 * - Mientras suena la voz, efectos y música se "agachan" (ducking) y vuelven a subir en las pausas.
 * - Los efectos más densos (truenos, temblores, olas, explosiones) llevan un recorte extra.
 */

const FPS = 24;
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

/** silencio total en Dachau: un segundo antes de la frase, la frase y un segundo después (sin música ni efectos) */
const C = (seg: number) => Math.round(seg * FPS);
const FR = datos.frases as {texto: string; inicio: number; fin: number}[];
const iDachau = FR.findIndex((f) => f.texto.startsWith('22 de marzo'));
export const SILENCIO_DACHAU: [number, number] = [C(FR[iDachau].inicio - 1.0), C(FR[iDachau + 1].fin + 1.0)];

export const volumenFx = (archivo: string, base: number, fGlobal: number) => {
	if (fGlobal >= SILENCIO_DACHAU[0] && fGlobal < SILENCIO_DACHAU[1]) return 0;
	return base * GANANCIA_FX * (RECORTE[archivo] ?? 1) * (1 - (1 - DUCK_FX) * vozEn(fGlobal));
};

/** Música: ya viene armada por capítulos (con sus silencios); aquí solo el nivel bajo la voz y un leve ducking. */
export const MUSICA_BASE = 0.15;
export const volumenMusica = (f: number, total: number, base = MUSICA_BASE) => {
	const salida = Math.min(1, Math.max(0, (total - f) / 12));
	return base * salida * (1 - 0.2 * vozEn(f));
};
