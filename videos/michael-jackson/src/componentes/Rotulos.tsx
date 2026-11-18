import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {CONDENSADA} from '../fuentes';

/*
 * Textos fijos de pantalla como en el video de referencia:
 *  - TituloArriba: titular grande condensado (blanco, con palabras clave en amarillo) arriba del todo.
 *  - Rotulo: cajita blanca pequeña con lugar / fecha / nombre.
 * Van por encima de la cámara (no se mueven con el mundo).
 */

const TINTA = '#141418';
export const AMARILLO = '#ffc21a';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** "¿NAPOLEÓN *BAJITO*?" → los trozos entre * van en amarillo (o en el color indicado con *texto|#hex*). */
const trozos = (texto: string) =>
	texto.split(/(\*[^*]+\*)/g).filter(Boolean).map((t) => {
		if (!t.startsWith('*')) return {t, color: '#ffffff'};
		const [cuerpo, color] = t.slice(1, -1).split('|');
		return {t: cuerpo, color: color ?? AMARILLO};
	});

export const TituloArriba: React.FC<{texto: string; desde: number; hasta?: number; y?: number; tam?: number}> = ({texto, desde, hasta = 1e9, y = 330, tam = 128}) => {
	const f = useCurrentFrame();
	if (f < desde || f >= hasta) return null;
	const s = interpolate(f, [desde, desde + 6], [0.55, 1], {...clamp, easing: Easing.out(Easing.back(2.4))});
	const o = interpolate(f, [desde, desde + 3], [0, 1], clamp);
	const lineas = texto.split('\n');
	return (
		<div style={{position: 'absolute', left: 30, right: 30, top: y, textAlign: 'center', transform: `scale(${s})`, transformOrigin: '50% 0%', opacity: o, filter: 'drop-shadow(0 8px 0 rgba(0,0,0,0.5))'}}>
			{lineas.map((l, i) => (
				<div key={i} style={{fontFamily: CONDENSADA, fontSize: tam, lineHeight: 1.04, letterSpacing: 1, textTransform: 'uppercase', position: 'relative'}}>
					<span style={{position: 'absolute', left: 0, right: 0, color: TINTA, WebkitTextStroke: `${tam * 0.16}px ${TINTA}`}}>{l.replace(/\*/g, '').replace(/\|#[0-9a-f]{6}/gi, '')}</span>
					<span style={{position: 'relative'}}>
						{trozos(l).map((p, k) => (
							<span key={k} style={{color: p.color}}>
								{p.t}
							</span>
						))}
					</span>
				</div>
			))}
		</div>
	);
};

export const Rotulo: React.FC<{texto: string; desde: number; hasta?: number; y?: number; x?: number; tam?: number}> = ({texto, desde, hasta = 1e9, y = 250, x = 540, tam = 40}) => {
	const f = useCurrentFrame();
	if (f < desde || f >= hasta) return null;
	const baja = interpolate(f, [desde, desde + 6], [-30, 0], {...clamp, easing: Easing.out(Easing.cubic)});
	const o = interpolate(f, [desde, desde + 5], [0, 1], clamp);
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y + baja,
				transform: 'translateX(-50%)',
				opacity: o,
				background: '#fbfaf5',
				color: TINTA,
				fontFamily: CONDENSADA,
				fontSize: tam,
				letterSpacing: 2,
				padding: '6px 22px 8px',
				borderRadius: 6,
				whiteSpace: 'nowrap',
				boxShadow: '0 6px 0 rgba(0,0,0,0.35), 0 0 0 4px rgba(20,20,24,0.85)',
			}}
		>
			{texto}
		</div>
	);
};
