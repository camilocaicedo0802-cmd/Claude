import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {MEDIO_FUNDIDO, Transicion, VIAJE} from '../componentes/Toma';
import {finFrase, inicioFrase, palabra} from '../tiempos';

/* Piezas comunes del montaje del video largo. Cada capítulo exporta una lista de planos;
   un plano dura hasta que empieza el siguiente y su salida es la entrada del siguiente. */

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const suave = Easing.inOut(Easing.cubic);
export const TINTA = '#14141a';
/** cuadros de anticipación: la imagen llega un pelín antes que la palabra */
export const antes = (n: number) => n - 3;
export const pal = palabra;
export const ini = inicioFrase;
export const fin = finFrase;
export const tramo = (f: number, a: number, b: number, curva: (t: number) => number = suave) => interpolate(f, [a, b], [0, 1], {...clamp, easing: curva});
/** rebote de aparición (0 → 1 con un pequeño sobrepaso) */
export const pop = (f: number, desde: number, dur = 8) => {
	const t = (f - desde) / dur;
	if (t <= 0) return 0;
	if (t >= 1.6) return 1;
	return 1 - Math.exp(-5 * t) * Math.cos(7 * t);
};

export type P = {d: number; h: number; e: Transicion; s: Transicion};
export type Plano = {
	/** cuadro (global) del corte de entrada */
	d: number;
	/** cómo entra (por defecto, barrido a la derecha) */
	e?: Transicion;
	/** nombre para buscarlo al revisar */
	n: string;
	C: React.FC<P>;
};

export type Cam = {s: number; x: number; y: number};
/** cámara que centra el punto del mundo (wx, wy) con escala s, sin dejar ver el borde del mundo */
export const centrar = (wx: number, wy: number, s: number): Cam => {
	const mx = Math.max(0, (s - 1) * 960);
	const my = Math.max(0, (s - 1) * 540);
	return {s, x: Math.max(-mx, Math.min(mx, -(wx - 960) * s)), y: Math.max(-my, Math.min(my, -(wy - 540) * s))};
};
export const mezclaCam = (a: Cam, b: Cam, t: number): Cam => ({s: a.s + (b.s - a.s) * t, x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t});
/** zoom de golpe: de la cámara a a la b en 5 cuadros a partir de `g` */
export const golpeCam = (f: number, g: number, a: Cam, b: Cam) => mezclaCam(a, b, interpolate(f, [g, g + 5], [0, 1], {...clamp, easing: (u) => 1 - Math.pow(1 - u, 3)}));

/** Mezcla dos colores hex (t = 0 → a, 1 → b). */
export const mezcla = (a: string, b: string, t: number) => {
	const h = (c: string) => [1, 3, 5].map((i) => parseInt(c.slice(i, i + 2), 16));
	const [x, y] = [h(a), h(b)];
	const k = Math.max(0, Math.min(1, t));
	return `rgb(${x.map((v, i) => Math.round(v + (y[i] - v) * k)).join(',')})`;
};

/** Monta una lista de planos en el orden de sus cuadros de inicio. Solo dibuja el que se ve (y el vecino durante la transición). */
export const Montaje: React.FC<{planos: Plano[]; fin: number}> = ({planos, fin: finTotal}) => {
	const f = useCurrentFrame();
	const lista = [...planos].sort((a, b) => a.d - b.d);
	return (
		<>
			{lista.map((p, i) => {
				const sig = lista[i + 1];
				const h = sig ? sig.d : finTotal;
				const e = p.e ?? 'latigoDer';
				const s = sig ? (sig.e ?? 'latigoDer') : 'corte';
				const margen = Math.max(MEDIO_FUNDIDO, VIAJE) + 2;
				if (f < p.d - margen || f >= h + margen) return null;
				return <p.C key={p.n} d={p.d} h={h} e={e} s={s} />;
			})}
		</>
	);
};
