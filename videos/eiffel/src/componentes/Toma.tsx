import React from 'react';
import {AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

/** Cuadros que dura una transición de latigazo (mitad antes del corte, mitad después). */
export const TRANS = 8;
const MEDIA = TRANS / 2;

/** 'pantalla': la cámara se mete en una pantalla (tele, celular, monitor, ventana) apuntada por `foco` */
export type Transicion = 'corte' | 'latigoDer' | 'latigoIzq' | 'latigoArriba' | 'zoom' | 'pantalla' | 'fundido';
/** medio fundido encadenado (cuadros a cada lado del corte): para los momentos serios */
export const MEDIO_FUNDIDO = 10;
/** cuadros que dura el viaje hacia dentro de la pantalla al salir de una toma */
export const VIAJE = 14;

type Rango = [number, number];
export type Camara = {
	s: Rango;
	x?: Rango;
	y?: Rango;
	r?: Rango;
	curva?: 'suave' | 'salida' | 'lineal';
};

type Props = {
	/** imagen de fondo en public/fondos (o vacío si se usa `escena`) */
	fondo?: string;
	/** fondo dibujado por código (sustituye a la imagen) */
	escena?: React.ReactNode;
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
	/** ángulo de cámara en grados: positivo = contrapicado (desde abajo: el sujeto se ve grande), negativo = picado (desde arriba: pequeño) */
	angulo?: number;
	/** cámara libre (sustituye a `cam`): devuelve escala y desplazamientos según el cuadro global */
	camFn?: (f: number) => {s?: number; x?: number; y?: number; r?: number};
	/** punto de la pantalla (px) hacia el que se entra al salir con 'pantalla' (y desde el que se sale al entrar) */
	focoSalida?: [number, number];
	focoEntrada?: [number, number];
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
export const Toma: React.FC<Props> = ({fondo, escena, desde, hasta, cam, entrada = 'corte', salida = 'corte', sacudida, golpes = [], encima, tinte, camFn, focoSalida, focoEntrada, angulo = 0, children}) => {
	const f = useCurrentFrame();
	const {width, height} = useVideoConfig();
	const id = React.useId().replace(/:/g, '');
	const margen = (t: Transicion) => (t === 'corte' ? 0 : t === 'fundido' ? MEDIO_FUNDIDO : MEDIA);
	const ini = desde - margen(entrada);
	const fin = hasta + margen(salida);
	if (f < ini || f >= fin) return null;

	// --- cámara del mundo ---
	const t = interpolate(f, [ini, fin], [0, 1], {...clamp, easing: curvas[cam.curva ?? 'suave']});
	const libre = camFn ? camFn(f) : null;
	let s = libre?.s ?? interpolate(t, [0, 1], cam.s);
	const x = libre?.x ?? interpolate(t, [0, 1], cam.x ?? [0, 0]);
	const y = libre?.y ?? interpolate(t, [0, 1], cam.y ?? [0, 0]);
	const r = libre?.r ?? interpolate(t, [0, 1], cam.r ?? [0, 0]);
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

	let origen = '50% 50%';
	if (entrada === 'pantalla' && f < desde + 8) {
		const u = interpolate(f, [desde - MEDIA, desde + 8], [0, 1], clamp);
		escalaT = interpolate(u, [0, 1], [1.6, 1], {easing: Easing.out(Easing.cubic)});
		opacidad = interpolate(u, [0, 0.35], [0, 1], clamp);
		radial = true;
		desenfoque = (1 - u) * 18;
		if (focoEntrada) origen = `${focoEntrada[0]}px ${focoEntrada[1]}px`;
	}
	if (salida === 'pantalla' && f >= hasta - VIAJE) {
		const u = interpolate(f, [hasta - VIAJE, hasta + MEDIA], [0, 1], clamp);
		escalaT = interpolate(u, [0, 1], [1, 7], {easing: Easing.in(Easing.cubic)});
		radial = true;
		desenfoque = u * 10;
		if (focoSalida) origen = `${focoSalida[0]}px ${focoSalida[1]}px`;
	}
	if (entrada === 'fundido' && f < desde + MEDIO_FUNDIDO) {
		opacidad = interpolate(f, [desde - MEDIO_FUNDIDO, desde + MEDIO_FUNDIDO], [0, 1], {...clamp, easing: curvaT});
	}
	if (entrada !== 'corte' && entrada !== 'pantalla' && entrada !== 'fundido' && f < desde + MEDIA) {
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
	if (salida !== 'corte' && salida !== 'pantalla' && salida !== 'fundido' && f >= hasta - MEDIA) {
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
			<AbsoluteFill style={{transform: `translate(${tx}px, ${ty}px) scale(${escalaT})`, transformOrigin: origen, filter: filtro, overflow: 'hidden'}}>
				<AbsoluteFill style={{transform: `perspective(2400px) rotateX(${angulo}deg) translate(${x + sx}px, ${y + sy}px) scale(${s * (1 + Math.abs(angulo) * 0.006)}) rotate(${r}deg)`, transformOrigin: '50% 50%'}}>
					{escena ?? <Img src={staticFile(`fondos/${fondo}`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />}
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
	opacidad?: number;
	filtro?: string;
	children: React.ReactNode;
}> = ({x, y, alto, ancho, voltear, rot = 0, escala = 1, opacidad = 1, filtro, children}) => {
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
				opacity: opacidad,
				filter: filtro,
			}}
		>
			{children}
		</div>
	);
};
