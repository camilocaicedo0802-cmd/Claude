import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {CONDENSADA} from '../fuentes';
import {AMARILLO} from './Rotulos';
import datos from '../../public/voz-palabras.json';

/*
 * Subtítulos tipo karaoke, como en el video de referencia:
 * letra condensada en mayúsculas, hasta 3 palabras por pantalla, y la palabra que se está diciendo en amarillo.
 */

type Palabra = {visible: string; inicio: number; duracion: number; frase: number; enfasis?: boolean};
type Grupo = {ps: Palabra[]; inicio: number; fin: number};

const limpio = (s: string) => s.replace(/[^\p{L}\p{N}]/gu, '');
const MAX_PALABRAS = 3;
const MAX_LETRAS = 17;

export const agruparPalabras = (palabras: Palabra[]): Grupo[] => {
	const grupos: Palabra[][] = [];
	let actual: Palabra[] = [];
	const cerrar = () => {
		if (actual.length) grupos.push(actual);
		actual = [];
	};
	for (const p of palabras) {
		if (actual.length && actual[0].frase !== p.frase) cerrar();
		const letras = actual.reduce((n, q) => n + limpio(q.visible).length + 1, 0) + limpio(p.visible).length;
		if (actual.length >= MAX_PALABRAS || (actual.length && letras > MAX_LETRAS)) cerrar();
		actual.push(p);
		if (/[,.:;!?…]$/.test(p.visible)) cerrar();
	}
	cerrar();
	return grupos.map((ps, k) => {
		const inicio = ps[0].inicio;
		const ultimo = ps[ps.length - 1];
		const finPalabra = ultimo.inicio + ultimo.duracion;
		const siguiente = grupos[k + 1]?.[0].inicio ?? finPalabra + 0.5;
		const fin = siguiente - finPalabra > 0.4 ? finPalabra + 0.3 : siguiente;
		return {ps, inicio, fin};
	});
};

const GRUPOS = agruparPalabras(datos.palabras as Palabra[]);

export const Subtitulos: React.FC<{y?: number}> = ({y = 1290}) => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	const t = f / fps;
	const g = GRUPOS.find((x) => t >= x.inicio && t < x.fin);
	if (!g) return null;
	const local = f - g.inicio * fps;
	const escala = interpolate(local, [0, 3, 6], [0.8, 1.06, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.quad)});
	const activa = g.ps.reduce((a, p, i) => (t >= p.inicio - 0.02 ? i : a), 0);
	const tam = 112;
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			<div
				style={{
					position: 'absolute',
					left: 60,
					right: 60,
					top: y,
					display: 'flex',
					flexWrap: 'wrap',
					justifyContent: 'center',
					columnGap: 24,
					rowGap: 0,
					transform: `scale(${escala})`,
					transformOrigin: '50% 50%',
					filter: 'drop-shadow(0 8px 0 rgba(0,0,0,0.5))',
				}}
			>
				{g.ps.map((p, i) => {
					const encendida = i === activa;
					const pop = encendida ? interpolate(t - p.inicio, [0, 0.08, 0.16], [1, 1.1, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
					return (
						<span
							key={i}
							style={{
								fontFamily: CONDENSADA,
								fontSize: tam,
								lineHeight: 1.08,
								letterSpacing: 1,
								textTransform: 'uppercase',
								color: encendida ? AMARILLO : '#ffffff',
								WebkitTextStroke: `${tam * 0.15}px #111`,
								paintOrder: 'stroke fill',
								display: 'inline-block',
								transform: `scale(${pop})`,
							}}
						>
							{p.visible}
						</span>
					);
				})}
			</div>
		</AbsoluteFill>
	);
};
