import {Ropa} from './Muneco';

/* Vestuario de «Los genios que contrataron a Hitler». Caricaturas de diseño propio.
   Sin esvásticas, banderas ni insignias: los brazaletes son rojos y lisos; los uniformes, sin símbolos. */

const cabeza = (extra: Partial<Ropa['cabeza']>): Ropa['cabeza'] => ({piel: '#ffffff', chaqueta: '', chaquetaSombra: '', botones: '', ...extra});

const CABEZA_HITLER = cabeza({pelo: 'hitler', colorPelo: '#1a1410', bigote: 'cepillo', colorBigote: '#1a1410'});

/** Hitler en 1919: uniforme gris verdoso del ejército, sin insignias */
export const HITLER_1919: Ropa = {cabeza: CABEZA_HITLER, casaca: '#7d8466', casacaSombra: '#5f6650', botones: '#c9c9c9', pantalon: '#6a7057', botas: '#2a2420', cinturon: '#3a2e22'};
/** de espía: gabardina y sombrero */
export const HITLER_ESPIA: Ropa = {cabeza: {...CABEZA_HITLER, gorra: 'fedora', colorGorra: '#3a3328', colorBanda: '#1a1410'}, casaca: '#a8946a', casacaSombra: '#86744e', botones: '#5a4a32', pantalon: '#4a4438', zapatos: '#2a1d14', cinturon: '#86744e'};
/** 1923: gabardina con brazalete rojo liso */
export const HITLER_1923: Ropa = {cabeza: CABEZA_HITLER, casaca: '#9a8a64', casacaSombra: '#7a6c4a', botones: '#4a3e2a', pantalon: '#4a4438', botas: '#2a2420', cinturon: '#5a4a32', brazalete: '#d6262e'};
/** de traje (1925-1932) */
export const HITLER_TRAJE: Ropa = {cabeza: CABEZA_HITLER, casaca: '#4a4038', casacaSombra: '#342c26', chaleco: '#e8e2d2', botones: '#2a2420', pantalon: '#4a4038', zapatos: '#1a1410', corbata: '#5a2a24'};
/** en la celda: camisa y tirantes */
export const HITLER_CELDA: Ropa = {cabeza: CABEZA_HITLER, casaca: '#f2ead8', casacaSombra: '#d9cfb6', botones: '#8a7a5a', pantalon: '#5a5048', zapatos: '#2a1d14', corbata: '#7a6a4a'};
/** de mesero torpe */
export const HITLER_MESERO: Ropa = {cabeza: CABEZA_HITLER, casaca: '#f4f4f4', casacaSombra: '#d9d9d9', chaleco: '#1b1b22', botones: '#1b1b22', pantalon: '#1b1b22', zapatos: '#141418', corbata: '#1b1b22'};
/** de vendedor de teletienda */
export const HITLER_VENDEDOR: Ropa = {cabeza: CABEZA_HITLER, casaca: '#c9a43a', casacaSombra: '#a8862a', chaleco: '#ffffff', botones: '#7a2a24', pantalon: '#4a4038', zapatos: '#1a1410', corbata: '#e3262e', rayas: '#a8862a'};
/** de burócrata con manguitos */
export const HITLER_BUROCRATA: Ropa = {cabeza: CABEZA_HITLER, casaca: '#e9e4d6', casacaSombra: '#cfc8b6', chaleco: '#5a5048', botones: '#2a2420', pantalon: '#5a5048', zapatos: '#1a1410', corbata: '#2a2420', punos: '#3a3530'};
/** canciller (1933): traje oscuro con brazalete rojo liso. Desde aquí ya no es ridículo. */
export const HITLER_CANCILLER: Ropa = {cabeza: CABEZA_HITLER, casaca: '#3a3530', casacaSombra: '#26221e', chaleco: '#e8e2d2', botones: '#1a1410', pantalon: '#3a3530', zapatos: '#141418', corbata: '#1a1410', brazalete: '#d6262e'};

/** Franz von Papen: chistera, guantes blancos, levita gris perla */
export const PAPEN: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#8a7a68', gorra: 'chistera', bigote: 'cepillo', colorBigote: '#8a7a68'}),
	casaca: '#5a5f6a', casacaSombra: '#40444d', chaleco: '#e9e4d6', botones: '#c9c9c9', faldones: true, punos: '#ffffff',
	pantalon: '#3a3d45', pantalonSombra: '#2a2c32', zapatos: '#141418', corbata: '#8a2f3a', guantes: '#ffffff',
};
export const PAPEN_SIN_SOMBRERO: Ropa = {...PAPEN, cabeza: {...PAPEN.cabeza, gorra: undefined}};

/** Paul von Hindenburg: bigotazo, corte a cepillo, uniforme gris azulado con medallas */
export const HINDENBURG: Ropa = {
	cabeza: cabeza({pelo: 'plano', colorPelo: '#cfcfcf', bigote: 'mostacho', colorBigote: '#e9e9e9'}),
	casaca: '#4f5d72', casacaSombra: '#38445a', botones: '#e0b23a', solapas: '#7a2a24', cuello: '#7a2a24', punos: '#7a2a24',
	pantalon: '#3a4558', pantalonSombra: '#2a3242', botas: '#141418', charreteras: '#e0b23a', banda: '#e0b23a',
};

/** el amigo preocupado de Papen (apertura) */
export const AMIGO: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#4a3a2a', lentes: true}),
	casaca: '#2a3a4a', casacaSombra: '#1c2834', chaleco: '#e9e4d6', botones: '#9a9a9a', pantalon: '#2a3a4a', zapatos: '#141418', corbata: '#2a5a4a',
};

/** el fundador del partido (1919) */
export const FUNDADOR: Ropa = {
	cabeza: cabeza({pelo: 'corto', colorPelo: '#3a2a1e', lentes: true, bigote: 'manubrio', colorBigote: '#3a2a1e'}),
	casaca: '#5a4a3a', casacaSombra: '#42362a', chaleco: '#a8946a', botones: '#3a2e22', pantalon: '#4a4038', zapatos: '#2a1d14', corbata: '#2a2420',
};

/** el juez comprensivo */
export const JUEZ: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#d9d9d9', gorra: 'boina', colorGorra: '#141418', lentes: true}),
	casaca: '#1b1b22', casacaSombra: '#0e0e14', chaleco: '#ffffff', pantalon: '#1b1b22', zapatos: '#141418', corbata: '#ffffff',
};

/** el editor */
export const EDITOR: Ropa = {
	cabeza: cabeza({pelo: 'corto', colorPelo: '#2a1c12', bigote: 'manubrio', colorBigote: '#2a1c12'}),
	casaca: '#6b5a48', casacaSombra: '#4f4234', chaleco: '#e9e4d6', pantalon: '#4a4038', zapatos: '#1a1410', corbata: '#c4262e', punos: '#e9e4d6',
};

/** el primer ministro bávaro (de traje) y de domador de circo */
export const MINISTRO: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#6b6b6b', lentes: true}),
	casaca: '#2a2a34', casacaSombra: '#17171e', chaleco: '#e9e4d6', botones: '#9a9a9a', pantalon: '#2a2a34', zapatos: '#141418', corbata: '#1f3a7a',
};
export const DOMADOR: Ropa = {
	...MINISTRO,
	cabeza: {...MINISTRO.cabeza, gorra: 'chistera'},
	casaca: '#c4262e', casacaSombra: '#8e1a22', chaleco: '#e0b23a', botones: '#e0b23a', faldones: true, charreteras: '#e0b23a', pantalon: '#f4f1e8', botas: '#141418',
};

/** el general astuto (el del sombrero): uniforme gris, gorra de plato, sin insignias */
export const GENERAL: Ropa = {
	cabeza: cabeza({gorra: 'militar', colorGorra: '#6a6f60', colorBanda: '#3a3e34', monoculo: false}),
	casaca: '#6a6f60', casacaSombra: '#50544a', botones: '#c9c9c9', cuello: '#3a3e34', pantalon: '#5a5f52', botas: '#141418', cinturon: '#3a2e22',
};

/** el hijo del presidente */
export const HIJO: Ropa = {...GENERAL, cabeza: cabeza({pelo: 'corto', colorPelo: '#8a7a68'}), casaca: '#4f5d72', casacaSombra: '#38445a', pantalon: '#3a4558'};

/** el banquero */
export const BANQUERO: Ropa = {
	cabeza: cabeza({pelo: 'calvo', colorPelo: '#9a9a9a', bigote: 'manubrio', colorBigote: '#6b6b6b', monoculo: true}),
	casaca: '#1b1b22', casacaSombra: '#0e0e14', chaleco: '#c9a43a', botones: '#e0b23a', faldones: true, pantalon: '#2a2a34', zapatos: '#141418', corbata: '#1b1b22',
};

/** el socio conservador arrepentido (bigote de morsa) */
export const SOCIO: Ropa = {
	cabeza: cabeza({pelo: 'corto', colorPelo: '#e6e6e6', bigote: 'morsa', colorBigote: '#f0f0f0', lentes: true}),
	casaca: '#3a3530', casacaSombra: '#26221e', chaleco: '#e8e2d2', botones: '#9a9a9a', pantalon: '#3a3530', zapatos: '#141418', corbata: '#1a1410',
};

/** el líder socialdemócrata: digno, sin caricatura */
export const LIDER_SPD: Ropa = {
	cabeza: cabeza({pelo: 'raya', colorPelo: '#7a7a7a', bigote: 'manubrio', colorBigote: '#7a7a7a', lentes: true}),
	casaca: '#2a2a30', casacaSombra: '#1a1a20', chaleco: '#e9e4d6', pantalon: '#2a2a30', zapatos: '#141418', corbata: '#5a1a1a',
};

/** gente de los años 20 (inversores, público, funcionarios) */
export const SENOR_1: Ropa = {cabeza: cabeza({pelo: 'raya', colorPelo: '#3a2a1e', gorra: 'fedora', colorGorra: '#3a3a44'}), casaca: '#4a4a55', casacaSombra: '#33333c', chaleco: '#e9e4d6', pantalon: '#4a4a55', zapatos: '#141418', corbata: '#7a2a24'};
export const SENOR_2: Ropa = {cabeza: cabeza({pelo: 'corto', colorPelo: '#6b4a2b', bigote: 'manubrio', colorBigote: '#6b4a2b'}), casaca: '#6b5a48', casacaSombra: '#4f4234', chaleco: '#c9b48a', pantalon: '#4a4038', zapatos: '#2a1d14', corbata: '#1f3a7a'};
export const SENOR_3: Ropa = {cabeza: cabeza({pelo: 'calvo', colorPelo: '#8a8a8a', lentes: true}), casaca: '#2f4a3a', casacaSombra: '#21362a', chaleco: '#e9e4d6', pantalon: '#2f4a3a', zapatos: '#141418', corbata: '#c9a43a'};
export const FUNCIONARIO: Ropa = {cabeza: cabeza({pelo: 'raya', colorPelo: '#2a1c12', lentes: true}), casaca: '#e9e4d6', casacaSombra: '#cfc8b6', chaleco: '#4a4a55', pantalon: '#4a4a55', zapatos: '#141418', corbata: '#2a2420', punos: '#3a3530'};
export const PRESENTADOR: Ropa = {cabeza: cabeza({pelo: 'liso', colorPelo: '#141010'}), casaca: '#1b1b22', casacaSombra: '#0e0e14', chaleco: '#ffffff', botones: '#ffffff', pantalon: '#1b1b22', zapatos: '#141418', corbata: '#1b1b22'};
export const COMENTARISTA: Ropa = {cabeza: cabeza({pelo: 'corto', colorPelo: '#2a1c12', gorra: 'boina', colorGorra: '#c9a43a'}), casaca: '#2f6fd1', casacaSombra: '#1f4fa8', chaleco: '#ffffff', pantalon: '#e6dcc2', zapatos: '#2a1d14', corbata: '#e3262e', rayas: '#ffffff'};
export const POLICIA_1923: Ropa = {cabeza: cabeza({gorra: 'casco', colorGorra: '#2a3a2a'}), casaca: '#3a4a3a', casacaSombra: '#26322a', botones: '#c9c9c9', pantalon: '#2a3a2a', botas: '#141418', cinturon: '#1a1410'};
export const UNIFORME_MARRON: Ropa = {cabeza: cabeza({gorra: 'militar', colorGorra: '#6b4a2b', colorBanda: '#3a2a1a'}), casaca: '#7a5a3a', casacaSombra: '#5a4228', botones: '#3a2a1a', pantalon: '#3a2e22', botas: '#141418', cinturon: '#2a1d14', brazalete: '#d6262e'};
export const SOLDADO: Ropa = {cabeza: cabeza({gorra: 'stahlhelm', colorGorra: '#5c6150'}), casaca: '#6a6f60', casacaSombra: '#50544a', botones: '#9a9a9a', pantalon: '#5a5f52', botas: '#141418', cinturon: '#2a2420'};
