import {Ropa} from './Muneco';

/* Vestuario del short «GTA existe por un bug». Cabezas blancas, como en los demás shorts. */

const cabeza = (extra: Partial<Ropa['cabeza']>): Ropa['cabeza'] => ({piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', ...extra});

/** Programador de los 90: pelo largo, lentes, sudadera verde y jeans */
export const ROPA_PROGRAMADOR: Ropa = {
	cabeza: cabeza({pelo: 'melena', colorPelo: '#6b4a2b', lentes: true}),
	casaca: '#3f8a5a',
	casacaSombra: '#2c6440',
	pantalon: '#3d5f95',
	pantalonSombra: '#2c4670',
	zapatos: '#f4f4f4',
};

/** Segundo programador: camisa de cuadros roja */
export const ROPA_PROGRAMADOR_2: Ropa = {
	cabeza: cabeza({pelo: 'corto', colorPelo: '#2a1c12', bigote: 'manubrio', colorBigote: '#2a1c12'}),
	casaca: '#b8323a',
	casacaSombra: '#8a222a',
	rayas: '#7a1a22',
	pantalon: '#4a4a55',
	zapatos: '#2a1d14',
};

/** Probador (tester) con camiseta amarilla */
export const ROPA_PROBADOR: Ropa = {
	cabeza: cabeza({pelo: 'rizado', colorPelo: '#2a1c12'}),
	casaca: '#f2c14e',
	casacaSombra: '#d4a032',
	pantalon: '#3d5f95',
	zapatos: '#e3262e',
};
export const ROPA_PROBADORA: Ropa = {
	cabeza: cabeza({pelo: 'liso', colorPelo: '#b5651d', pestanas: true}),
	casaca: '#7b3fe4',
	casacaSombra: '#5a2cb0',
	pantalon: '#2e2e36',
	zapatos: '#f4f4f4',
};

/** El jefe del estudio, de traje */
export const ROPA_JEFE: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#7a7a7a', lentes: true}),
	casaca: '#4a4a55',
	casacaSombra: '#33333c',
	chaleco: '#ffffff',
	botones: '#c9c9c9',
	pantalon: '#4a4a55',
	zapatos: '#141418',
	corbata: '#c4262e',
};

/** Policía (el del juego) */
export const ROPA_POLICIA: Ropa = {
	cabeza: cabeza({gorra: 'militar', colorGorra: '#1f2e52', colorBanda: '#141418', bigote: 'manubrio', colorBigote: '#3a2414'}),
	casaca: '#1f2e52',
	casacaSombra: '#121c36',
	botones: '#e0b23a',
	pantalon: '#1f2e52',
	zapatos: '#141418',
	cinturon: '#141418',
	corbata: '#141418',
};

/** Ladrón: camiseta a rayas, gorro y antifaz */
export const ROPA_LADRON: Ropa = {
	cabeza: cabeza({gorra: 'boina', colorGorra: '#1b1b22'}),
	casaca: '#f4f4f4',
	casacaSombra: '#d9d6cc',
	rayas: '#1b1b22',
	pantalon: '#2e2e36',
	zapatos: '#141418',
	guantes: '#1b1b22',
};

/** Político británico indignado */
export const ROPA_POLITICO: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#d9d9d9', lentes: true}),
	casaca: '#2a2a34',
	casacaSombra: '#17171e',
	chaleco: '#ffffff',
	botones: '#9a9a9a',
	pantalon: '#2a2a34',
	zapatos: '#141418',
	corbata: '#1f3a7a',
};

/** El publicista experto en escándalos: traje morado y corbata dorada */
export const ROPA_PUBLICISTA: Ropa = {
	cabeza: cabeza({pelo: 'liso', colorPelo: '#1a1210'}),
	casaca: '#7b3fe4',
	casacaSombra: '#5a2cb0',
	chaleco: '#f4f4f4',
	botones: '#ffd23f',
	pantalon: '#2e2e36',
	zapatos: '#141418',
	corbata: '#ffd23f',
};

/** El ejecutivo de la distribuidora */
export const ROPA_DISTRIBUIDOR: Ropa = {
	cabeza: cabeza({pelo: 'corto', colorPelo: '#3a2a1e', bigote: 'manubrio', colorBigote: '#3a2a1e'}),
	casaca: '#1f3a7a',
	casacaSombra: '#132552',
	chaleco: '#ffffff',
	botones: '#e0b23a',
	pantalon: '#1f3a7a',
	zapatos: '#141418',
	corbata: '#e3262e',
};
