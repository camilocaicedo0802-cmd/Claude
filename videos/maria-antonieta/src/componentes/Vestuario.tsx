import {Ropa} from './Muneco';

/* Vestuario del short «¿María Antonieta dijo "que coman pasteles"?» */

const cabeza = (extra: Partial<Ropa['cabeza']>): Ropa['cabeza'] => ({piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', ...extra});

/** María Antonieta reina: peinado alto empolvado, vestido de corte azul pastel con lazos rosados */
export const ROPA_MARIA: Ropa = {
	cabeza: cabeza({pelo: 'pouf', colorPelo: '#efe9e1', adornoPelo: '#ff8fb8', pestanas: true, mejillas: true}),
	casaca: '#9ec9ea',
	casacaSombra: '#6f9fc4',
	chaleco: '#fbd3e0',
	punos: '#fbf8f1',
	pantalon: '#9ec9ea',
	zapatos: '#e88aa8',
	vestido: {color: '#9ec9ea', sombra: '#6f9fc4', ancho: 205, enagua: '#fbd3e0', lazos: '#ff8fb8'},
};

/** María Antonieta con 14 años, al llegar a Versalles (1770) */
export const ROPA_MARIA_JOVEN: Ropa = {
	cabeza: cabeza({pelo: 'mono', colorPelo: '#f0cc68', pestanas: true, mejillas: true}),
	casaca: '#f6b8cb',
	casacaSombra: '#d98fa6',
	chaleco: '#fff1c9',
	punos: '#fbf8f1',
	pantalon: '#f6b8cb',
	zapatos: '#c96b8a',
	vestido: {color: '#f6b8cb', sombra: '#d98fa6', ancho: 160, enagua: '#fff1c9', lazos: '#ffffff'},
};

/** María Antonieta niña, en Viena */
export const ROPA_MARIA_NINA: Ropa = {
	cabeza: cabeza({pelo: 'rizos', colorPelo: '#f0cc68', gorra: 'lazo', colorGorra: '#ff8fb8', pestanas: true, mejillas: true}),
	casaca: '#bfe6c4',
	casacaSombra: '#8fc49a',
	chaleco: '#ffffff',
	punos: '#ffffff',
	pantalon: '#bfe6c4',
	zapatos: '#ff8fb8',
	vestido: {color: '#bfe6c4', sombra: '#8fc49a', ancho: 120, lazos: '#ff8fb8'},
};

/** El delfín Luis (futuro Luis XVI) */
export const ROPA_LUIS: Ropa = {
	cabeza: cabeza({pelo: 'rizado', colorPelo: '#ece6da', mejillas: true}),
	casaca: '#2c4f9e',
	casacaSombra: '#1d3672',
	chaleco: '#e8c766',
	botones: '#e0b23a',
	faldones: true,
	punos: '#fbf8f1',
	pantalon: '#f1ece0',
	medias: '#ffffff',
	zapatos: '#2a1d14',
	hebilla: true,
	banda: '#7fb2e5',
	corbata: '#ffffff',
};

/** Damas de la corte (chismosas, con abanico) */
export const ROPA_DAMA_1: Ropa = {
	cabeza: cabeza({pelo: 'pouf', colorPelo: '#d9d3c7', adornoPelo: '#7fcf8a', pestanas: true}),
	casaca: '#c7e6b4',
	casacaSombra: '#93bf7d',
	chaleco: '#fff4d6',
	punos: '#fbf8f1',
	pantalon: '#c7e6b4',
	zapatos: '#6b8f4e',
	vestido: {color: '#c7e6b4', sombra: '#93bf7d', ancho: 180, enagua: '#fff4d6', lazos: '#7fcf8a'},
};

export const ROPA_DAMA_2: Ropa = {
	cabeza: cabeza({pelo: 'pouf', colorPelo: '#e9e1d2', adornoPelo: '#b48be0', pestanas: true}),
	casaca: '#d6c2ef',
	casacaSombra: '#a98fcf',
	chaleco: '#fff4d6',
	punos: '#fbf8f1',
	pantalon: '#d6c2ef',
	zapatos: '#7d5fae',
	vestido: {color: '#d6c2ef', sombra: '#a98fcf', ancho: 180, enagua: '#fff4d6', lazos: '#b48be0'},
};

/** El pueblo revolucionario (sans-culottes) */
export const ROPA_PUEBLO_1: Ropa = {
	cabeza: cabeza({gorra: 'frigio', bigote: 'manubrio', colorBigote: '#3a2414'}),
	casaca: '#7a5236',
	casacaSombra: '#57391f',
	chaleco: '#f1ece0',
	botones: '#3a2414',
	pantalon: '#3d5f95',
	pantalonSombra: '#2c4670',
	zapatos: '#3a2414',
	fajin: '#e3262e',
	corbata: '#e3262e',
};

export const ROPA_PUEBLO_2: Ropa = {
	cabeza: cabeza({gorra: 'frigio', pelo: 'corto', colorPelo: '#2a1c12'}),
	casaca: '#5f6b4a',
	casacaSombra: '#434d33',
	rayas: '#e3262e',
	pantalon: '#e6dcc2',
	pantalonSombra: '#c9bd9e',
	zapatos: '#3a2414',
	fajin: '#1f3a7a',
};

export const ROPA_PUEBLO_3: Ropa = {
	cabeza: cabeza({gorra: 'frigio', pelo: 'melena', colorPelo: '#5a3a22', pestanas: true}),
	casaca: '#b9714a',
	casacaSombra: '#8f5233',
	chaleco: '#f1ece0',
	punos: '#f1ece0',
	pantalon: '#6b4a32',
	zapatos: '#3a2414',
	vestido: {color: '#6b4a32', sombra: '#4a3222', ancho: 130, lazos: '#f1ece0'},
};

/** Jean-Jacques Rousseau, el filósofo */
export const ROPA_ROUSSEAU: Ropa = {
	cabeza: cabeza({pelo: 'rizado', colorPelo: '#bdb5a8'}),
	casaca: '#6e4f33',
	casacaSombra: '#4d3621',
	chaleco: '#e9dcc0',
	botones: '#c9a43a',
	faldones: true,
	punos: '#fbf8f1',
	pantalon: '#4d3621',
	medias: '#efeae0',
	zapatos: '#2a1d14',
	hebilla: true,
	corbata: '#ffffff',
};

/** María Teresa de Austria, la madre (de luto) */
export const ROPA_MARIA_TERESA: Ropa = {
	cabeza: cabeza({gorra: 'velo', mejillas: false}),
	casaca: '#2e2e38',
	casacaSombra: '#1c1c24',
	chaleco: '#f4f1e8',
	punos: '#f4f1e8',
	pantalon: '#2e2e38',
	zapatos: '#1c1c24',
	vestido: {color: '#2e2e38', sombra: '#1c1c24', ancho: 170, lazos: '#d8d2c4'},
};

/** María Antonieta al final: vestido blanco sencillo y cofia */
export const ROPA_MARIA_BLANCO: Ropa = {
	cabeza: cabeza({pelo: 'rizos', colorPelo: '#e9e6e0', pestanas: true}),
	casaca: '#f4f2ec',
	casacaSombra: '#d6d2c6',
	punos: '#ffffff',
	pantalon: '#f4f2ec',
	zapatos: '#2a2a32',
	vestido: {color: '#f4f2ec', sombra: '#d6d2c6', ancho: 120, lazos: '#ffffff'},
};
