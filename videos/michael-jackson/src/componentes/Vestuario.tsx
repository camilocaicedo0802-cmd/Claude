import {Ropa} from './Muneco';

/* Vestuario del short «¿Michael Jackson se quiso volver blanco?»
   En este video la piel tiene su tono real: es el tema de la historia (vitiligo). */

const cabeza = (extra: Partial<Ropa['cabeza']>): Ropa['cabeza'] => ({piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', ...extra});

export const PIEL_MJ = '#8a5a3c';
export const PIEL_MJ_CLARA = '#f1dccb';
export const MANCHA = '#f2dccb';

/** Michael en 1978 (20 años): piel morena, afro, esmoquin */
export const ROPA_MJ_1978: Ropa = {
	cabeza: cabeza({piel: PIEL_MJ, pelo: 'afro', colorPelo: '#1a1210'}),
	guantes: PIEL_MJ,
	casaca: '#1b1b22',
	casacaSombra: '#0e0e14',
	chaleco: '#ffffff',
	botones: '#1b1b22',
	punos: '#ffffff',
	pantalon: '#1b1b22',
	zapatos: '#0e0e14',
	corbata: '#1b1b22',
};

/** Michael en 1982 (Thriller): chaqueta roja con galones en V */
export const ROPA_MJ_1982: Ropa = {
	cabeza: cabeza({piel: PIEL_MJ, pelo: 'rizos', colorPelo: '#1a1210', colorManchas: MANCHA}),
	guantes: PIEL_MJ,
	colorManchas: MANCHA,
	casaca: '#c8102e',
	casacaSombra: '#8e0a20',
	cheurones: '#1b1b22',
	botones: '#e0b23a',
	pantalon: '#c8102e',
	pantalonSombra: '#8e0a20',
	medias: '#ffffff',
	zapatos: '#141418',
	cinturon: '#1b1b22',
};

/** Michael en los 90 (33 años): tono parejo y claro, sombrero, chaqueta negra y un guante blanco */
export const ROPA_MJ_1991: Ropa = {
	cabeza: cabeza({piel: PIEL_MJ_CLARA, pelo: 'liso', colorPelo: '#141010', gorra: 'fedora', colorGorra: '#141418', colorBanda: '#f4f4f4'}),
	guantes: PIEL_MJ_CLARA,
	guanteDer: '#ffffff',
	brillosGuante: true,
	casaca: '#1b1b22',
	casacaSombra: '#0e0e14',
	chaleco: '#ffffff',
	botones: '#e0b23a',
	punos: '#ffffff',
	pantalon: '#1b1b22',
	medias: '#ffffff',
	zapatos: '#141418',
	cinturon: '#e0b23a',
	banda: undefined,
};

/** Michael de los 90 sin sombrero (entrevista) */
export const ROPA_MJ_1993: Ropa = {...ROPA_MJ_1991, cabeza: {...ROPA_MJ_1991.cabeza, gorra: undefined}, casaca: '#c8102e', casacaSombra: '#8e0a20', cinturon: '#1b1b22'};

/** Paparazzi */
export const ROPA_PAPARAZZI_1: Ropa = {
	cabeza: cabeza({piel: '#e8b98f', gorra: 'fedora', colorGorra: '#6b5a48', colorBanda: '#2a2a32', bigote: 'manubrio', colorBigote: '#4a3020'}),
	guantes: '#e8b98f',
	casaca: '#c9b48a',
	casacaSombra: '#a08c66',
	cinturon: '#6b5a48',
	pantalon: '#4a4a55',
	zapatos: '#2a1d14',
};
export const ROPA_PAPARAZZI_2: Ropa = {
	cabeza: cabeza({piel: '#b97a4c', pelo: 'corto', colorPelo: '#1e140e', lentes: true}),
	guantes: '#b97a4c',
	casaca: '#3e5a7a',
	casacaSombra: '#2a4058',
	pantalon: '#2e2e36',
	zapatos: '#141418',
	corbata: '#e3262e',
};

/** Médico forense (2009) */
export const ROPA_FORENSE: Ropa = {
	cabeza: cabeza({piel: '#f1c8a5', pelo: 'raya', colorPelo: '#6b6b6b', lentes: true}),
	guantes: '#f1c8a5',
	casaca: '#f7f7f4',
	casacaSombra: '#d8d8d2',
	chaleco: '#7fb2e5',
	pantalon: '#3e4a5a',
	zapatos: '#141418',
	corbata: '#1f3a7a',
};

/** Presentador de televisión (genérico) */
export const ROPA_PRESENTADOR: Ropa = {
	cabeza: cabeza({piel: '#d9a27a', pelo: 'corto', colorPelo: '#2a1c12'}),
	guantes: '#d9a27a',
	casaca: '#1f2e52',
	casacaSombra: '#121c36',
	chaleco: '#ffffff',
	botones: '#c9c9c9',
	pantalon: '#1f2e52',
	zapatos: '#141418',
	corbata: '#c4262e',
};

/** Espectadores incrédulos */
export const ROPA_ESPECTADOR_1: Ropa = {
	cabeza: cabeza({piel: '#5e3b26', pelo: 'corto', colorPelo: '#120c08'}),
	guantes: '#5e3b26',
	casaca: '#3f8a5a',
	casacaSombra: '#2c6440',
	pantalon: '#3d5f95',
	zapatos: '#2a1d14',
};
export const ROPA_ESPECTADORA_2: Ropa = {
	cabeza: cabeza({piel: '#f2c9a8', pelo: 'melena', colorPelo: '#b5651d', pestanas: true}),
	guantes: '#f2c9a8',
	casaca: '#e88aa8',
	casacaSombra: '#c4678a',
	pantalon: '#3d3d48',
	zapatos: '#2a1d14',
};
