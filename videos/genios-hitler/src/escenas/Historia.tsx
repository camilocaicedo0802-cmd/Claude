import React from 'react';
import {Montaje, Plano, fin} from './base';
import {PLANOS_C0, SONIDOS_C0} from './c0';
import {PLANOS_C1, SONIDOS_C1} from './c1';
import {PLANOS_C2, SONIDOS_C2} from './c2';
import {PLANOS_C3, SONIDOS_C3} from './c3';
import {PLANOS_C4, SONIDOS_C4} from './c4';
import {PLANOS_C5, SONIDOS_C5} from './c5';
import {PLANOS_C6, SONIDOS_C6} from './c6';
import {PLANOS_C7, SONIDOS_C7} from './c7';
import {PLANOS_C8, SONIDOS_C8} from './c8';
import {PLANOS_C9, SONIDOS_C9} from './c9';

/*
 * «Los genios que contrataron a Hitler» (16:9, 24 fps).
 * Sin esvásticas, banderas ni insignias; las víctimas nunca son parte del chiste.
 * Solo dos cortes secos: Dachau y la Noche de los Cuchillos Largos. Todo lo demás, barridos, zooms o fundidos.
 */

const PLANOS: Plano[] = [...PLANOS_C0, ...PLANOS_C1, ...PLANOS_C2, ...PLANOS_C3, ...PLANOS_C4, ...PLANOS_C5, ...PLANOS_C6, ...PLANOS_C7, ...PLANOS_C8, ...PLANOS_C9];

/** fin de la voz + 2 s para el último acorde */
export const FIN_VIDEO = fin(238) + 48;

/** barrido: un «whoosh» suave en cada latigazo */
const WHOOSH: [string, number, number][] = PLANOS.filter((p) => p.e && p.e.startsWith('latigo')).map((p) => ['whoosh', p.d - 5, 0.35]);

export const SONIDOS: [string, number, number][] = [
	...WHOOSH,
	...SONIDOS_C0,
	...SONIDOS_C1,
	...SONIDOS_C2,
	...SONIDOS_C3,
	...SONIDOS_C4,
	...SONIDOS_C5,
	...SONIDOS_C6,
	...SONIDOS_C7,
	...SONIDOS_C8,
	...SONIDOS_C9,
];

export const Historia: React.FC = () => <Montaje planos={PLANOS} fin={FIN_VIDEO} />;
