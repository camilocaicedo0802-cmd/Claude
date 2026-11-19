import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, Pose, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {CabezaSVG} from '../componentes/Personaje';
import {ExpedienteSellado, SELLOS_EXPEDIENTE, SelloGoma, SelloPostal} from '../componentes/Recurrentes';
import {HINDENBURG, HITLER_1923, HITLER_ESPIA, HITLER_TRAJE, JUEZ} from '../componentes/Vestuario';
import {EscCerveceria, EscMesaArriba, EscTribunal, Humo, Jarra} from '../escenarios/Epoca';
import {Toma} from '../componentes/Toma';
import {CONDENSADA} from '../fuentes';
import {P, TINTA, clamp, pal} from './base';

/* Utilería que se sostiene en la mano (SVG en coordenadas de la mano: muñeca en el origen, dedos hacia +y)
   y los cuatro «adelantos» de la apertura, que vuelven en sus capítulos. */

export const brazo = (lado: -1 | 1, r: {a: number; c: number; k?: number}): Partial<Pose> => (lado < 0 ? {bi: r.a, ci: r.c, ai: r.k ?? 1} : {bd: r.a, cd: r.c, ad: r.k ?? 1});

/** pistola pequeña en la mano (cañón hacia +y) */
export const Pistola: React.FC<{rot?: number}> = ({rot = 0}) => (
	<g transform={`rotate(${rot} 0 36)`}>
		{/* empuñadura inclinada hacia atrás y cañón largo hacia los dedos: silueta de pistola en «L» */}
		<path d="M -14 36 L -74 6 L -84 34 L -22 74 Z" fill="#2a2a30" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		<path d="M -30 64 Q -46 84 -24 92" fill="none" stroke={TINTA} strokeWidth={6} />
		<rect x={-16} y={20} width={32} height={128} rx={5} fill="#3a3a42" stroke={TINTA} strokeWidth={6} />
		<rect x={-8} y={136} width={16} height={18} fill="#1a1a1e" stroke={TINTA} strokeWidth={4} />
	</g>
);

/** sello de goma en la mano, con su texto; `roto` lo parte en dos */
export const SelloGomaMano: React.FC<{texto: string; roto?: number; rot?: number}> = ({texto, roto = 0, rot = 0}) => {
	const sep = roto * 80;
	const giro = roto * 30;
	const mitad = (lado: -1 | 1) => (
		<g transform={`translate(${lado * sep} ${roto * 40}) rotate(${lado * giro} 0 90)`}>
			<g clipPath={`url(#mitad-${lado < 0 ? 'i' : 'd'})`}>
				<rect x={-16} y={10} width={32} height={70} fill="#8a5a32" stroke={TINTA} strokeWidth={6} />
				<rect x={-90} y={76} width={180} height={44} rx={6} fill="#5a3a22" stroke={TINTA} strokeWidth={6} />
				<rect x={-86} y={118} width={172} height={36} fill="#f4ecd6" stroke={TINTA} strokeWidth={5} />
				<text x={0} y={147} textAnchor="middle" fill="#c8202a" fontFamily={CONDENSADA} fontSize={30} letterSpacing={2}>
					{texto}
				</text>
			</g>
		</g>
	);
	return (
		<g transform={`rotate(${rot} 0 36)`}>
			<defs>
				<clipPath id="mitad-i">
					<polygon points="-120,0 4,0 -6,60 6,100 -4,170 -120,170" />
				</clipPath>
				<clipPath id="mitad-d">
					<polygon points="4,0 120,0 120,170 -4,170 6,100 -6,60" />
				</clipPath>
			</defs>
			{mitad(-1)}
			{mitad(1)}
		</g>
	);
};

/** sello postal en la mano (OJO: en la mano DERECHA todo sale espejado; para objetos con texto usa la izquierda o pon el objeto en coordenadas del mundo) */
export const SelloMano: React.FC<{cara?: 'hindenburg' | 'hitler'; rot?: number; tam?: number}> = ({cara = 'hindenburg', rot = 0, tam = 1}) => {
	const d = cara === 'hindenburg' ? HINDENBURG.cabeza : HITLER_TRAJE.cabeza;
	return (
		<g transform={`rotate(${rot} 0 36) translate(0 40) scale(${tam})`}>
			<rect x={-70} y={0} width={140} height={170} fill="#f4ecd6" stroke={TINTA} strokeWidth={5} strokeDasharray="10 6" />
			<rect x={-58} y={12} width={116} height={146} fill={cara === 'hindenburg' ? '#24407a' : '#6e2c22'} />
			<rect x={-52} y={18} width={104} height={108} fill={cara === 'hindenburg' ? '#6f8fca' : '#b8664a'} />
			<g transform="translate(-46 24) scale(0.24)">
				<CabezaSVG d={d} ojos="normal" cejas="enojado" boca="seria" />
			</g>
			<text x={0} y={150} textAnchor="middle" fill="#f4ecd6" fontFamily={CONDENSADA} fontSize={20}>
				DEUTSCHES REICH
			</text>
		</g>
	);
};

/** silla de madera (de pie, vista de frente); `tambalea` la inclina */
export const Silla: React.FC<{x: number; y: number; alto: number; tambalea?: number; etiqueta?: string; color?: string}> = ({x, y, alto, tambalea = 0, etiqueta, color = '#7a5230'}) => {
	const f = useCurrentFrame();
	const r = tambalea * Math.sin(f / 2.2) * 6;
	const k = alto / 300;
	return (
		<div style={{position: 'absolute', left: x - 110 * k, top: y - alto, width: 220 * k, height: alto, transform: `rotate(${r}deg)`, transformOrigin: '50% 100%'}}>
			<svg width={220 * k} height={alto} viewBox="0 0 220 300" style={{overflow: 'visible'}}>
				<rect x={30} y={0} width={160} height={150} rx={10} fill={color} stroke={TINTA} strokeWidth={8} />
				<rect x={52} y={24} width={116} height={100} rx={8} fill="rgba(0,0,0,0.18)" />
				<rect x={14} y={150} width={192} height={30} rx={6} fill={color} stroke={TINTA} strokeWidth={8} />
				<line x1={36} y1={180} x2={30} y2={296} stroke={TINTA} strokeWidth={16} strokeLinecap="round" />
				<line x1={184} y1={180} x2={190} y2={296} stroke={TINTA} strokeWidth={16} strokeLinecap="round" />
			</svg>
			{etiqueta && (
				<div style={{position: 'absolute', left: 28 * k, top: 40 * k, width: 164 * k, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 30 * k, color: '#f4ecd6', letterSpacing: 2 * k}}>{etiqueta}</div>
			)}
		</div>
	);
};

/** pedazos de yeso que caen del techo desde el cuadro `desde` */
export const Yeso: React.FC<{x: number; y: number; desde: number; ancho?: number; suelo?: number}> = ({x, y, desde, ancho = 220, suelo = 1000}) => {
	const f = useCurrentFrame();
	const t = f - desde;
	if (t < 0) return null;
	return (
		<>
			{Array.from({length: 14}, (_, i) => {
				const v0 = 4 + (i % 4) * 2;
				const yy = Math.min(suelo, y + v0 * t + 0.9 * t * t * (0.6 + (i % 3) * 0.2));
				const xx = x + ((i * 53) % ancho) - ancho / 2 + Math.sin(i) * t * 0.8;
				const tam = 10 + (i % 5) * 7;
				return <div key={i} style={{position: 'absolute', left: xx, top: yy, width: tam, height: tam * 0.8, background: '#e9e2d0', border: `3px solid ${TINTA}`, borderRadius: 3, transform: `rotate(${i * 37 + t * 9}deg)`}} />;
			})}
			<div style={{position: 'absolute', left: x - 160, top: y - 40 + t * 3, width: 320, height: 200, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(240,234,220,0.6), rgba(240,234,220,0) 70%)', opacity: interpolate(t, [0, 30], [1, 0], clamp), filter: 'blur(6px)'}} />
		</>
	);
};

/** fogonazo de un disparo */
export const Fogonazo: React.FC<{x: number; y: number; desde: number; tam?: number}> = ({x, y, desde, tam = 220}) => {
	const f = useCurrentFrame();
	const t = f - desde;
	if (t < 0 || t > 5) return null;
	const s = interpolate(t, [0, 1, 5], [0.6, 1.2, 0.3]);
	return (
		<svg width={tam} height={tam} viewBox="-100 -100 200 200" style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, transform: `scale(${s})`, overflow: 'visible'}}>
			<polygon points="0,-100 22,-30 90,-40 34,8 70,80 0,36 -70,80 -34,8 -90,-40 -22,-30" fill="#ffd84a" stroke="#ff8a2a" strokeWidth={8} />
			<circle r={30} fill="#fffbe0" />
		</svg>
	);
};

/** grieta en el techo (aparece en `desde`) */
export const Grieta: React.FC<{x: number; y: number; desde: number}> = ({x, y, desde}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	return (
		<svg width={300} height={160} viewBox="-150 0 300 160" style={{position: 'absolute', left: x - 150, top: y, overflow: 'visible'}}>
			<path d="M 0 0 L -20 40 L 10 60 L -30 110 M 10 60 L 60 90 L 50 140 M -20 40 L -80 50 L -110 90" stroke={TINTA} strokeWidth={7} fill="none" strokeLinecap="round" />
			<circle cx={0} cy={4} r={14} fill="#1a1410" />
		</svg>
	);
};

/* ===================== los cuatro adelantos (se repiten en sus capítulos) ===================== */

/** el espía escondido detrás de una jarra, con su libreta */
export const CuadroEspia: React.FC<{asoma?: number}> = ({asoma = 1}) => {
	const f = useCurrentFrame();
	const mira = Math.sin(f / 14) * 6;
	return (
		<>
			<EscCerveceria tono="sepia" vacia humo={0.14} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 780, height: 60, background: '#7a5230', borderTop: `9px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: 840, bottom: 0, background: '#4a3220'}} />
			<Actor x={1010 + 60 * (1 - asoma)} y={1430} alto={1100}>
				<Muneco ropa={HITLER_ESPIA} pose={{...manosFrente([220, 520], [320, 470]), mi: 'agarra', md: 'agarra', cabeza: mira}} ojos="mirandoLado" cejas="arrogante" boca="seria" objDer={<g transform="translate(-10 40) rotate(-10)"><rect x={-40} y={0} width={80} height={110} rx={6} fill="#f4ecd6" stroke={TINTA} strokeWidth={6} /><line x1={-28} y1={30} x2={24} y2={30} stroke="#8a7a5a" strokeWidth={5} /><line x1={-28} y1={52} x2={18} y2={52} stroke="#8a7a5a" strokeWidth={5} /></g>} />
			</Actor>
			<Jarra x={880} y={1080} alto={520} />
		</>
	);
};

/** el tiro al techo: Hitler sobre una silla que se tambalea, y el yeso que le cae encima */
export const CuadroTiroTecho: React.FC<{disparo: number; grita?: boolean}> = ({disparo, grita = true}) => {
	const f = useCurrentFrame();
	const tras = f >= disparo;
	return (
		<>
			<EscCerveceria tono="ambar" humo={0.2} vacia />
			<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 120, background: '#e3d6b8', borderBottom: `9px solid ${TINTA}`}} />
			<Grieta x={1010} y={110} desde={disparo} />
			<Silla x={960} y={1010} alto={300} tambalea={1} />
			<Actor x={960} y={760} alto={720} rot={Math.sin(f / 2.2) * 3}>
				<Muneco
					ropa={HITLER_1923}
					pose={{...brazo(1, {a: 168, c: 4}), md: 'agarra', ...manosEn([140, 500]), mi: 'puno', cabeza: tras ? -4 : 0}}
					objDer={<Pistola rot={0} />}
					ojos={tras ? 'cerrados' : 'grandes'}
					cejas="enojado"
					boca={grita ? 'grito' : 'abierta'}
				/>
			</Actor>
			<Fogonazo x={1010} y={150} desde={disparo} tam={240} />
			<Yeso x={980} y={130} desde={disparo + 1} suelo={1040} />
			<Humo densidad={0.12} />
		</>
	);
};

/** el juez que parte en dos el sello de DEPORTAR */
export const CuadroJuezDeportar: React.FC<{rompe: number}> = ({rompe}) => {
	const f = useCurrentFrame();
	const r = interpolate(f, [rompe, rompe + 8], [0, 1], clamp);
	return (
		<>
			<EscTribunal tono="munich" />
			<Actor x={960} y={1060} alto={860}>
				<Muneco
					ropa={JUEZ}
					pose={{...manosFrente([150, 330], [250, 330]), mi: 'agarra', md: 'agarra'}}
					objIzq={<SelloGomaMano texto="DEPORTAR" roto={r} rot={180} />}
					ojos={r > 0.3 ? 'feliz' : 'normal'}
					cejas="neutral"
					boca={r > 0.3 ? 'sonrisaGrande' : 'sonrisa'}
				/>
			</Actor>
			{/* el estrado por delante */}
			<div style={{position: 'absolute', left: 520, top: 760, width: 880, height: 330, background: 'linear-gradient(180deg, #4a3220, #2e1e12)', border: `9px solid ${TINTA}`, borderRadius: 8}} />
		</>
	);
};

/** Hindenburg, monumental, con el sello de su cara en la mano */
export const CuadroHindenburgSello: React.FC<{brillo?: number}> = ({brillo = 0}) => (
	<>
		<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #1c2c5a 0%, #2f4f8f 60%, #14203e 100%)'}} />
		{[0, 1, 2, 3].map((i) => (
			<div key={i} style={{position: 'absolute', left: 160 + i * 480, top: 0, width: 110, height: 1080, background: 'linear-gradient(90deg, #c9a43a, #f0d27a 50%, #a8862a)', opacity: 0.32}} />
		))}
		<div style={{position: 'absolute', left: 560, top: 60, width: 800, height: 800, borderRadius: '50%', background: `radial-gradient(circle, rgba(255,226,140,${0.25 + 0.3 * brillo}) 0%, rgba(255,226,140,0) 65%)`}} />
		<Actor x={960} y={1180} alto={1180}>
			<Muneco ropa={HINDENBURG} pose={{...brazo(1, alcanzar(1, 330, 300)), md: 'agarra', ...manosEn([160, 520]), mi: 'puno'}} ojos="normal" cejas="enojado" boca="seria" />
		</Actor>
		<SelloPostal x={1290} y={360} ancho={210} rot={8} brillo={brillo} />
	</>
);

/* ===================== «Ese ya no llega a nada»: el expediente y el sello (4 veces, idéntico) ===================== */

/** cuadro en que el sello golpea: en «nada» (el sonido 'sello' va aquí, siempre igual) */
export const golpeMuletilla = (i: number) => pal(i, 'nada') - 1;
const EXP = {x: 960, y: 560, ancho: 1000};

/**
 * La carpeta «EXPEDIENTE: A. HITLER» cae sobre el escritorio (vista desde arriba) y el sello de goma estampa INOFENSIVO
 * justo en «nada». `n` = número de la muletilla (1..4): trae los n-1 sellos anteriores ya puestos.
 * `postal`: la tercera vez lo que se estampa es un sello postal de Hindenburg (con matasellos INOFENSIVO).
 */
export const PlanoMuletilla: React.FC<P & {i: number; n: number; postal?: boolean}> = ({d, h, e, s, i, n}) => {
	const f = useCurrentFrame();
	const g = golpeMuletilla(i);
	const cae = interpolate(f, [d - 2, d + 7], [0, 1], {...clamp, easing: (u) => 1 - Math.pow(1 - u, 3)});
	const alto = EXP.ancho * 0.72;
	const pos = SELLOS_EXPEDIENTE[n - 1];
	const px = EXP.x - EXP.ancho / 2 + pos.u * EXP.ancho;
	const py = EXP.y - alto / 2 + pos.v * alto;
	return (
		<Toma escena={<EscMesaArriba tono="madera" luz={[960, 520]} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1], y: [0, 10]}} golpes={[[g, 0.05]]}>
			<div style={{position: 'absolute', inset: 0, transform: `scale(${1.25 - 0.25 * cae}) rotate(${(1 - cae) * 6}deg)`, opacity: interpolate(cae, [0, 0.2], [0, 1], clamp)}}>
				<ExpedienteSellado x={EXP.x} y={EXP.y} ancho={EXP.ancho} rot={-2} n={n} ultimo={g} />
			</div>
			<SelloGoma x={px} y={py} desde={g} tam={240} />
		</Toma>
	);
};
