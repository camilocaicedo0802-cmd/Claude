import {Ropa} from './Muneco';

/* Vestuario del short «La nariz de la Esfinge».
   Cabezas blancas, como en el short de Napoleón (Napoleón, granaderos e inglés vienen de Muneco.tsx). */

const cabeza = (extra: Partial<Ropa['cabeza']>): Ropa['cabeza'] => ({piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', ...extra});

/** Frederik Norden, explorador danés (1737): tricornio, peluca empolvada, casaca azul marino */
export const ROPA_NORDEN: Ropa = {
	cabeza: cabeza({pelo: 'rizado', colorPelo: '#ebe5d8', gorra: 'tricornio', colorGorra: '#18181e', colorBanda: '#d9a032'}),
	casaca: '#2a4a7a',
	casacaSombra: '#1a3256',
	chaleco: '#d9b45a',
	botones: '#e0b23a',
	faldones: true,
	punos: '#f4f1e8',
	pantalon: '#e6dcc2',
	medias: '#f4f1e8',
	zapatos: '#2a1d14',
	hebilla: true,
	corbata: '#ffffff',
};

/** Guía turístico del siglo XIX: fez rojo, galabiya blanca y chaleco */
export const ROPA_GUIA: Ropa = {
	cabeza: cabeza({gorra: 'fez', bigote: 'manubrio', colorBigote: '#2a1c12'}),
	casaca: '#f4f1e8',
	casacaSombra: '#d9d3c2',
	chaleco: '#2f5a8a',
	botones: '#e0b23a',
	pantalon: '#f4f1e8',
	pantalonSombra: '#d9d3c2',
	zapatos: '#7a4a24',
	fajin: '#c4262e',
	vestido: {color: '#f4f1e8', sombra: '#d9d3c2', ancho: 92, lazos: '#d9d3c2'},
};

/** Turistas con casco de explorador */
export const ROPA_TURISTA: Ropa = {
	cabeza: cabeza({gorra: 'casco', colorGorra: '#efe6cf', bigote: 'manubrio', colorBigote: '#a8743a'}),
	casaca: '#c9b48a',
	casacaSombra: '#a08c66',
	chaleco: '#f4f1e8',
	botones: '#6b5a48',
	pantalon: '#e6dcc2',
	botas: '#5a3a1e',
	corbata: '#c4262e',
};
export const ROPA_TURISTA_2: Ropa = {
	cabeza: cabeza({pelo: 'melena', colorPelo: '#b5651d', gorra: 'lazo', colorGorra: '#ff8fb8', pestanas: true}),
	casaca: '#8fb3d9',
	casacaSombra: '#6a90ba',
	pantalon: '#8fb3d9',
	zapatos: '#2a1d14',
	vestido: {color: '#8fb3d9', sombra: '#6a90ba', ancho: 120, lazos: '#ffffff'},
};

/** El fanático de 1378: turbante, barba y túnica */
export const ROPA_FANATICO: Ropa = {
	cabeza: cabeza({gorra: 'turbante', colorGorra: '#f4f1e8', colorBanda: '#2fa36b', barba: '#2a1c12'}),
	casaca: '#6b5a44',
	casacaSombra: '#4f412f',
	pantalon: '#6b5a44',
	pantalonSombra: '#4f412f',
	zapatos: '#3a2a1e',
	fajin: '#2fa36b',
	vestido: {color: '#6b5a44', sombra: '#4f412f', ancho: 92, lazos: '#4f412f'},
};

/** Aldeanos que le llevan ofrendas a la Esfinge */
export const ROPA_ALDEANO: Ropa = {
	cabeza: cabeza({gorra: 'turbante', colorGorra: '#e8dcc0', colorBanda: '#c4262e', bigote: 'manubrio', colorBigote: '#2a1c12'}),
	casaca: '#e9e2cf',
	casacaSombra: '#cfc6ae',
	pantalon: '#e9e2cf',
	pantalonSombra: '#cfc6ae',
	zapatos: '#7a4a24',
	fajin: '#c4262e',
	vestido: {color: '#e9e2cf', sombra: '#cfc6ae', ancho: 92, lazos: '#cfc6ae'},
};
export const ROPA_ALDEANA: Ropa = {
	cabeza: cabeza({pelo: 'melena', colorPelo: '#2a1c12', pestanas: true}),
	casaca: '#3f6fa8',
	casacaSombra: '#2c5286',
	pantalon: '#3f6fa8',
	zapatos: '#7a4a24',
	vestido: {color: '#3f6fa8', sombra: '#2c5286', ancho: 120, lazos: '#e0b23a'},
};
