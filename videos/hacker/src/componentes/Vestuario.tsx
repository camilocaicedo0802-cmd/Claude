import {Ropa} from './Muneco';

/* Vestuario del short «Hackeó GTA 6 desde la tele de un hotel».
   El chico es genérico y con capucha: no se parece a nadie real (era menor de edad). */

const cabeza = (extra: Partial<Ropa['cabeza']>): Ropa['cabeza'] => ({piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', ...extra});

/** El chico: sudadera gris oscura con la capucha puesta */
export const ROPA_CHICO: Ropa = {
	cabeza: cabeza({gorra: 'capucha', colorGorra: '#3a3f4a'}),
	casaca: '#3a3f4a',
	casacaSombra: '#272b34',
	pantalon: '#1f2230',
	zapatos: '#e9e9ee',
	guantes: '#ffffff',
};

/** Empleados de la oficina (sin marcas) */
export const ROPA_EMPLEADO_1: Ropa = {
	cabeza: cabeza({pelo: 'corto', colorPelo: '#2a1c12', lentes: true}),
	casaca: '#5f7a9a',
	casacaSombra: '#46607e',
	pantalon: '#2e2e36',
	zapatos: '#141418',
};
export const ROPA_EMPLEADA_2: Ropa = {
	cabeza: cabeza({pelo: 'liso', colorPelo: '#6b3a1e', pestanas: true}),
	casaca: '#c9a46a',
	casacaSombra: '#a8854e',
	pantalon: '#3a3a44',
	zapatos: '#141418',
};
export const ROPA_EMPLEADO_3: Ropa = {
	cabeza: cabeza({pelo: 'rizado', colorPelo: '#1a1210', bigote: 'manubrio', colorBigote: '#1a1210'}),
	casaca: '#3f8a5a',
	casacaSombra: '#2c6440',
	pantalon: '#2e2e36',
	zapatos: '#141418',
};

/** La gente de internet que se ríe (cabezas en las ventanas) */
export const VECINOS: Ropa[] = [
	{...ROPA_EMPLEADO_1, cabeza: cabeza({pelo: 'mono', colorPelo: '#2a1c12'}), casaca: '#e3262e', casacaSombra: '#a81e26'},
	{...ROPA_EMPLEADO_1, cabeza: cabeza({pelo: 'melena', colorPelo: '#e8c25a', pestanas: true}), casaca: '#7b3fe4', casacaSombra: '#5a2cb0'},
	{...ROPA_EMPLEADO_1, cabeza: cabeza({pelo: 'corto', colorPelo: '#1a1210', lentes: true}), casaca: '#1f9d48', casacaSombra: '#16743a'},
	{...ROPA_EMPLEADO_1, cabeza: cabeza({pelo: 'rizos', colorPelo: '#b5651d'}), casaca: '#ff8a1e', casacaSombra: '#c96a12'},
	{...ROPA_EMPLEADO_1, cabeza: cabeza({gorra: 'fedora', colorGorra: '#2a2a32', colorBanda: '#e3262e'}), casaca: '#2f7fd1', casacaSombra: '#1f5fa8'},
	{...ROPA_EMPLEADO_1, cabeza: cabeza({pelo: 'afro', colorPelo: '#1a1210'}), casaca: '#ff6fb5', casacaSombra: '#d94a92'},
	{...ROPA_EMPLEADO_1, cabeza: cabeza({pelo: 'raya', colorPelo: '#7a7a7a', bigote: 'manubrio', colorBigote: '#7a7a7a'}), casaca: '#c9a46a', casacaSombra: '#a8854e'},
	{...ROPA_EMPLEADO_1, cabeza: cabeza({pelo: 'liso', colorPelo: '#141010', pestanas: true}), casaca: '#22c5b8', casacaSombra: '#169a90'},
];
