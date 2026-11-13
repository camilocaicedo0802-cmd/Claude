import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

/** Cuadros que dura una transición de latigazo (mitad antes del corte, mitad después). */
export const TRANS = 8;
const MEDIA = TRANS / 2;

export type Transicion = 'corte' | 'latigoDer' | 'latigoIzq' | 'latigoArriba' | 'zoom';

type Rango = [number, number];
export type Camara = {
	s: Rango;
	x?: Rango;
	y?: Rango;
	r?: Rango;
	curva?: 'suave' | 'salida' | 'lineal';
};

type Props = {
	fondo: string;
	/** cuadro (global) donde empieza la toma = momento del corte */
	desde: number;
	/** cuadro (global) donde termina la toma = siguiente corte */
	hasta: number;
	cam: Camara;
	/** cómo entra esta toma */
	entrada?: Transicion;
	/** cómo sale: debe coincidir con la "entrada" de la toma siguiente */
	salida?: Transicion;
	/** sacudida de cámara (px) según el cuadro global */
	sacudida?: (f: number) => number;
	/** golpes de zoom: [cuadro global, intensidad] */
	golpes?: [number, number][];
	/** capa encima del mundo que no se mueve con la cámara (p. ej. destellos) */
	encima?: React.ReactNode;
	/** tinte de color encima de todo (p. ej. luz fría de la morgue) */
	tinte?: string;
	children?: React.ReactNode;
};

const curvas = {
	suave: Easing.inOut(Easing.cubic),
	salida: Easing.out(Easing.cubic),
	lineal: (t: number) => t,
};

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/**
 * Una toma: fondo 3D + personajes, con cámara siempre en movimiento (como en la referencia)
 * y transiciones de "latigazo" con desenfoque de movimiento direccional.
 * Todo usa el cuadro GLOBAL, así personajes, subtítulos y sonidos comparten la misma línea de tiempo.
 */
export const Toma: React.FC<Props> = ({fondo, desde, hasta, cam, entrada = 'corte', salida = 'corte', sacudida, golpes = [], encima, tinte, children}) => {
	const f = useCurrentFrame();
	const {width, height} = useVideoConfig();
	const id = React.useId().replace(/:/g, '');
	const ini = desde - (entrada === 'corte' ? 0 : MEDIA);
	const fin = hasta + (salida === 'corte' ? 0 : MEDIA);
	if (f < ini || f >= fin) return null;

	// --- cámara del mundo ---
	const t = interpolate(f, [ini, fin], [0, 1], {...clamp, easing: curvas[cam.curva ?? 'suave']});
	let s = interpolate(t, [0, 1], cam.s);
	const x = interpolate(t, [0, 1], cam.x ?? [0, 0]);
	const y = interpolate(t, [0, 1], cam.y ?? [0, 0]);
	const r = interpolate(t, [0, 1], cam.r ?? [0, 0]);
	for (const [g, k] of golpes) {
		if (f >= g) s *= 1 + k * interpolate(f - g, [0, 4, 16], [0, 1, 0.8], {extrapolateRight: 'clamp', easing: Easing.out(Easing.quad)});
	}
	const amp = sacudida ? sacudida(f) : 0;
	const sx = amp * (Math.sin(f * 2.1) + 0.5 * Math.sin(f * 5.3));
	const sy = amp * (Math.cos(f * 1.7) + 0.5 * Math.sin(f * 4.1));

	// --- transiciones ---
	let tx = 0;
	let ty = 0;
	let escalaT = 1;
	let opacidad = 1;
	let desenfoque = 0;
	let vertical = false;
	let radial = false;
	const curvaT = Easing.inOut(Easing.cubic);

	if (entrada !== 'corte' && f < desde + MEDIA) {
		const u = interpolate(f, [desde - MEDIA, desde + MEDIA], [0, 1], clamp);
		const p = curvaT(u);
		desenfoque = Math.sin(Math.PI * u) * 80;
		if (entrada === 'latigoDer') tx = (1 - p) * width;
		if (entrada === 'latigoIzq') tx = -(1 - p) * width;
		if (entrada === 'latigoArriba') {
			ty = -(1 - p) * height;
			vertical = true;
		}
		if (entrada === 'zoom') {
			radial = true;
			escalaT = interpolate(p, [0, 1], [1.9, 1]);
			opacidad = interpolate(u, [0, 0.45], [0, 1], clamp);
			desenfoque = (1 - p) * 40;
		}
	}
	if (salida !== 'corte' && f >= hasta - MEDIA) {
		const u = interpolate(f, [hasta - MEDIA, hasta + MEDIA], [0, 1], clamp);
		const p = curvaT(u);
		desenfoque = Math.sin(Math.PI * u) * 80;
		if (salida === 'latigoDer') tx = -p * width;
		if (salida === 'latigoIzq') tx = p * width;
		if (salida === 'latigoArriba') {
			ty = p * height;
			vertical = true;
		}
		if (salida === 'zoom') {
			radial = true;
			escalaT = interpolate(p, [0, 1], [1, 2.4]);
			desenfoque = p * 40;
		}
	}

	const filtro = desenfoque < 0.5 ? 'none' : radial ? `blur(${desenfoque / 3}px)` : `url(#mb-${id})`;

	return (
		<AbsoluteFill style={{overflow: 'hidden', opacity: opacidad}}>
			<svg width={0} height={0} style={{position: 'absolute'}}>
				<filter id={`mb-${id}`} x="-30%" y="-30%" width="160%" height="160%">
					<feGaussianBlur stdDeviation={vertical ? `0 ${desenfoque}` : `${desenfoque} 0`} />
				</filter>
			</svg>
			<AbsoluteFill style={{transform: `translate(${tx}px, ${ty}px) scale(${escalaT})`, filter: filtro}}>
				<AbsoluteFill style={{transform: `translate(${x + sx}px, ${y + sy}px) scale(${s}) rotate(${r}deg)`, transformOrigin: '50% 50%'}}>
					<Img src={staticFile(`fondos/${fondo}`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
					{children}
				</AbsoluteFill>
				{tinte && <AbsoluteFill style={{background: tinte, mixBlendMode: 'soft-light'}} />}
				{encima}
			</AbsoluteFill>
			{/* viñeta fija (fuera de la transición, para que no se deforme en los zooms) */}
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.35) 100%)'}} />
		</AbsoluteFill>
	);
};

/** Coloca un personaje (o cualquier cosa) en coordenadas del mundo 1080x1920, anclado por los pies. */
export const EnMundo: React.FC<{
	x: number;
	y: number;
	alto: number;
	ancho?: number;
	voltear?: boolean;
	rot?: number;
	escala?: number;
	children: React.ReactNode;
}> = ({x, y, alto, ancho, voltear, rot = 0, escala = 1, children}) => {
	const w = ancho ?? (alto * 400) / 760;
	return (
		<div
			style={{
				position: 'absolute',
				left: x - w / 2,
				top: y - alto,
				width: w,
				height: alto,
				transform: `rotate(${rot}deg) scale(${voltear ? -escala : escala}, ${escala})`,
				transformOrigin: '50% 100%',
			}}
		>
			{children}
		</div>
	);
};
