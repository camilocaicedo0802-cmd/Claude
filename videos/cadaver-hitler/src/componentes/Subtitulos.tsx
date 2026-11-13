import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {TITULAR as fontFamily} from '../fuentes';
import datos from '../../public/voz-palabras.json';


type Palabra = {visible: string; inicio: number; duracion: number; frase: number};
type Grupo = {texto: string; inicio: number; fin: number};

const limpio = (s: string) => s.replace(/[^\p{L}\p{N}]/gu, '');

/**
 * Agrupa como la referencia: 1 palabra por pantalla, o 2 cuando la primera es cortita
 * ("a Hitler", "una idea", "un espía"). Nunca junta palabras de frases distintas.
 */
export const agruparPalabras = (palabras: Palabra[]): Grupo[] => {
	const grupos: {ps: Palabra[]}[] = [];
	let i = 0;
	while (i < palabras.length) {
		const g = [palabras[i]];
		while (
			g.length < 2 &&
			limpio(g[g.length - 1].visible).length <= 3 &&
			!/[,.:;!?…]$/.test(g[g.length - 1].visible) &&
			i + g.length < palabras.length &&
			palabras[i + g.length].frase === g[0].frase
		) {
			g.push(palabras[i + g.length]);
		}
		grupos.push({ps: g});
		i += g.length;
	}
	return grupos.map(({ps}, k) => {
		const inicio = ps[0].inicio;
		const ultimo = ps[ps.length - 1];
		const finPalabra = ultimo.inicio + ultimo.duracion;
		const siguiente = grupos[k + 1]?.ps[0].inicio ?? finPalabra + 0.4;
		const fin = siguiente - finPalabra > 0.35 ? finPalabra + 0.25 : siguiente;
		return {texto: ps.map((p) => p.visible).join(' '), inicio, fin};
	});
};

const GRUPOS = agruparPalabras(datos.palabras as Palabra[]);

export const Subtitulos: React.FC<{y?: number}> = ({y = 1310}) => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	const t = f / fps;
	const g = GRUPOS.find((x) => t >= x.inicio && t < x.fin);
	if (!g) return null;
	const local = f - g.inicio * fps;
	const escala = interpolate(local, [0, 3, 6], [0.78, 1.08, 1], {extrapolateRight: 'clamp', easing: Easing.out(Easing.quad)});
	const estiloBase: React.CSSProperties = {
		position: 'absolute',
		left: 0,
		right: 0,
		textAlign: 'center',
		fontFamily,
		fontWeight: 900,
		fontSize: 84,
		lineHeight: 1.05,
		letterSpacing: -1,
		padding: '0 70px',
	};
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: y, transform: `scale(${escala})`, transformOrigin: '50% 50%', filter: 'drop-shadow(0 7px 0 rgba(0,0,0,0.45))'}}>
				<div style={{...estiloBase, color: '#111', WebkitTextStroke: '18px #111'}}>{g.texto}</div>
				<div style={{...estiloBase, color: '#fff'}}>{g.texto}</div>
			</div>
		</AbsoluteFill>
	);
};
