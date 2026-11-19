import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {CONDENSADA, SERIF, TITULAR} from '../fuentes';
import {Boca, CabezaSVG, Cejas, Diseno, Ojos} from './Personaje';
import {HINDENBURG, HITLER_TRAJE} from './Vestuario';

/* Los seis objetos que vuelven a lo largo del video:
   el contrato, el ratón del rincón, el sello de Hindenburg, el expediente INOFENSIVO, la jarra de votos y la chistera de Papen. */

const TINTA = '#14141a';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const pop = (f: number, desde: number, dur = 8) => {
	const t = (f - desde) / dur;
	if (t <= 0) return 0;
	if (t >= 1.6) return 1;
	return 1 - Math.exp(-5 * t) * Math.cos(7 * t);
};

/** Cabeza suelta de un personaje (para sellos, retratos y peones). viewBox de 400 x 400. */
export const Cara: React.FC<{d: Diseno; tam: number; ojos?: Ojos; cejas?: Cejas; boca?: Boca; style?: React.CSSProperties}> = ({d, tam, ojos = 'normal', cejas = 'neutral', boca = 'seria', style}) => (
	<svg width={tam} height={tam} viewBox="20 0 360 380" style={{overflow: 'visible', ...style}}>
		<CabezaSVG d={d} ojos={ojos} cejas={cejas} boca={boca} />
	</svg>
);

/* ---------------- 1. el contrato ---------------- */

export const Contrato: React.FC<{x: number; y: number; ancho: number; rot?: number; firma?: number; sombra?: boolean}> = ({x, y, ancho, rot = -3, firma = 0, sombra = true}) => {
	const k = ancho / 600;
	const largo = 520;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - (ancho * 1.3) / 2, width: ancho, height: ancho * 1.3, transform: `rotate(${rot}deg)`}}>
			<div style={{position: 'absolute', inset: 0, background: '#f6efdc', border: `${6 * k}px solid ${TINTA}`, borderRadius: 6 * k, boxShadow: sombra ? `${14 * k}px ${18 * k}px 0 rgba(0,0,0,0.28)` : undefined, padding: 34 * k, boxSizing: 'border-box', fontFamily: SERIF, color: '#2a2218'}}>
				<div style={{textAlign: 'center', fontFamily: CONDENSADA, fontSize: 60 * k, letterSpacing: 3 * k, lineHeight: 1}}>CONTRATO DE EMPLEO</div>
				<div style={{height: 4 * k, background: '#2a2218', margin: `${14 * k}px ${40 * k}px ${26 * k}px`}} />
				<div style={{fontSize: 40 * k, lineHeight: 1.5}}>
					<b>Puesto:</b> Canciller
					<br />
					<b>Empleado:</b> A. Hitler
				</div>
				{[0, 1, 2, 3, 4].map((i) => (
					<div key={i} style={{height: 7 * k, background: '#cfc4a8', borderRadius: 4 * k, margin: `${20 * k}px 0`, width: `${[92, 80, 88, 60, 74][i]}%`}} />
				))}
				<div style={{position: 'absolute', left: 40 * k, right: 40 * k, bottom: 70 * k, height: 3 * k, background: '#2a2218'}} />
				<div style={{position: 'absolute', left: 40 * k, bottom: 34 * k, fontSize: 26 * k, fontFamily: TITULAR, fontWeight: 600, letterSpacing: 2 * k}}>FIRMA</div>
				<svg viewBox="0 0 520 120" style={{position: 'absolute', left: 50 * k, bottom: 70 * k, width: 400 * k, height: 92 * k, overflow: 'visible'}}>
					<path
						d="M 10 90 C 40 10 70 10 60 80 C 55 110 100 30 130 50 C 160 70 150 100 190 60 C 220 30 240 90 280 60 C 310 40 330 80 370 50 C 400 30 430 70 500 40"
						stroke="#1d2a6b"
						strokeWidth={7}
						fill="none"
						strokeLinecap="round"
						strokeDasharray={largo + 200}
						strokeDashoffset={(largo + 200) * (1 - firma)}
					/>
				</svg>
			</div>
		</div>
	);
};

/* ---------------- 2. el ratón con bigote de cepillo ---------------- */

export const Raton: React.FC<{x: number; y: number; tam?: number; chilla?: boolean; voltear?: boolean}> = ({x, y, tam = 160, chilla = false, voltear = false}) => {
	const f = useCurrentFrame();
	const tiembla = chilla ? Math.sin(f * 2.3) * 3 : 0;
	return (
		<svg width={tam * 1.6} height={tam} viewBox="0 0 320 200" style={{position: 'absolute', left: x - tam * 0.8, top: y - tam, overflow: 'visible', transform: `${voltear ? 'scaleX(-1)' : ''} translate(${tiembla}px, 0)`}}>
			<path d="M 250 150 Q 320 160 300 110 Q 290 80 312 60" stroke={TINTA} strokeWidth={7} fill="none" strokeLinecap="round" />
			<ellipse cx={170} cy={140} rx={100} ry={56} fill="#9b9ba6" stroke={TINTA} strokeWidth={8} />
			<ellipse cx={80} cy={110} rx={62} ry={50} fill="#a9a9b4" stroke={TINTA} strokeWidth={8} />
			<circle cx={100} cy={52} r={34} fill="#c9a9b4" stroke={TINTA} strokeWidth={8} />
			<circle cx={100} cy={52} r={18} fill="#e6b9c6" />
			<circle cx={20} cy={112} r={11} fill={TINTA} />
			<circle cx={64} cy={92} r={chilla ? 11 : 8} fill="#fff" stroke={TINTA} strokeWidth={5} />
			<circle cx={chilla ? 62 : 60} cy={92} r={4} fill={TINTA} />
			{/* el bigotito de cepillo */}
			<rect x={22} y={118} width={30} height={14} rx={2} fill={TINTA} />
			{chilla ? <ellipse cx={40} cy={146} rx={14} ry={11} fill="#5a1a1a" stroke={TINTA} strokeWidth={4} /> : <path d="M 28 142 Q 40 148 52 140" stroke={TINTA} strokeWidth={4} fill="none" />}
			<line x1={150} y1={192} x2={140} y2={204} stroke={TINTA} strokeWidth={8} strokeLinecap="round" />
			<line x1={210} y1={192} x2={220} y2={204} stroke={TINTA} strokeWidth={8} strokeLinecap="round" />
			{chilla &&
				[0, 1, 2].map((i) => (
					<path key={i} d={`M ${-14 - i * 22} ${120 - i * 26} l ${-30} ${-12 - i * 6}`} stroke={TINTA} strokeWidth={6} strokeLinecap="round" opacity={0.5 + 0.5 * Math.abs(Math.sin(f / 3 + i))} />
				))}
		</svg>
	);
};

/* ---------------- 3. el sello postal ---------------- */

const bordePerforado = (() => {
	const W = 300;
	const H = 366;
	const r = 9;
	const nx = 11;
	const ny = 13;
	const px = W / nx;
	const py = H / ny;
	let d = 'M 0 0';
	for (let i = 0; i < nx; i++) d += ` L ${(i + 0.5) * px - r} 0 A ${r} ${r} 0 0 0 ${(i + 0.5) * px + r} 0`;
	d += ` L ${W} 0`;
	for (let i = 0; i < ny; i++) d += ` L ${W} ${(i + 0.5) * py - r} A ${r} ${r} 0 0 0 ${W} ${(i + 0.5) * py + r}`;
	d += ` L ${W} ${H}`;
	for (let i = 0; i < nx; i++) d += ` L ${W - (i + 0.5) * px + r} ${H} A ${r} ${r} 0 0 0 ${W - (i + 0.5) * px - r} ${H}`;
	d += ` L 0 ${H}`;
	for (let i = 0; i < ny; i++) d += ` L 0 ${H - (i + 0.5) * py + r} A ${r} ${r} 0 0 0 0 ${H - (i + 0.5) * py - r}`;
	return d + ' Z';
})();

export const SelloPostal: React.FC<{x: number; y: number; ancho: number; cara?: 'hindenburg' | 'hitler'; valor?: string; rot?: number; brillo?: number; style?: React.CSSProperties}> = ({
	x,
	y,
	ancho,
	cara = 'hindenburg',
	valor = '12',
	rot = 0,
	brillo = 0,
	style,
}) => {
	const alto = ancho * 1.22;
	const k = ancho / 300;
	const marco = cara === 'hindenburg' ? '#24407a' : '#6e2c22';
	const cielo = cara === 'hindenburg' ? '#6f8fca' : '#b8664a';
	const d = cara === 'hindenburg' ? HINDENBURG.cabeza : HITLER_TRAJE.cabeza;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`, filter: brillo > 0 ? `drop-shadow(0 0 ${30 * brillo * k}px rgba(255,214,102,${brillo}))` : `drop-shadow(${6 * k}px ${8 * k}px 0 rgba(0,0,0,0.3))`, ...style}}>
			<svg width={ancho} height={alto} viewBox="0 0 300 366" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
				<path d={bordePerforado} fill="#f4ecd6" stroke={TINTA} strokeWidth={4} />
				<rect x={24} y={24} width={252} height={318} fill={marco} stroke={TINTA} strokeWidth={5} />
				<rect x={38} y={38} width={224} height={240} fill={cielo} />
			</svg>
			<Cara d={d} tam={196 * k} cejas={cara === 'hindenburg' ? 'enojado' : 'arrogante'} style={{position: 'absolute', left: 52 * k, top: 58 * k}} />
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 34 * k, textAlign: 'center', color: '#f4ecd6', fontFamily: CONDENSADA, fontSize: 38 * k, letterSpacing: 4 * k}}>DEUTSCHES REICH</div>
			<div style={{position: 'absolute', right: 46 * k, top: 42 * k, color: '#f4ecd6', fontFamily: CONDENSADA, fontSize: 46 * k, textShadow: `0 ${3 * k}px 0 ${TINTA}`}}>{valor}</div>
		</div>
	);
};

/* ---------------- 4. el expediente ---------------- */

/** Sello de goma INOFENSIVO: cae, golpea y queda. */
export const GolpeSello: React.FC<{x: number; y: number; desde: number; texto?: string; tam?: number; rot?: number; color?: string}> = ({x, y, desde, texto = 'INOFENSIVO', tam = 60, rot = -10, color = '#c8202a'}) => {
	const f = useCurrentFrame();
	if (f < desde - 6) return null;
	const caida = interpolate(f, [desde - 6, desde], [1, 0], clamp);
	const escala = f < desde ? 1.6 - 0.6 * (1 - caida) : 1 + 0.18 * Math.max(0, 1 - (f - desde) / 5);
	const op = f < desde ? 0.35 : 1;
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y,
				transform: `translate(-50%, -50%) rotate(${rot}deg) scale(${escala})`,
				border: `${tam * 0.1}px solid ${color}`,
				borderRadius: tam * 0.16,
				padding: `${tam * 0.06}px ${tam * 0.26}px`,
				color,
				fontFamily: CONDENSADA,
				fontSize: tam,
				letterSpacing: tam * 0.06,
				lineHeight: 1.1,
				opacity: op * 0.92,
				whiteSpace: 'nowrap',
				mixBlendMode: 'multiply',
			}}
		>
			{texto}
		</div>
	);
};

/** El sello de goma (el objeto) que baja y estampa. */
export const SelloGoma: React.FC<{x: number; y: number; desde: number; tam?: number}> = ({x, y, desde, tam = 220}) => {
	const f = useCurrentFrame();
	const t = f - desde;
	if (t < -14 || t > 14) return null;
	const alto = t < 0 ? interpolate(t, [-14, -2, 0], [-500, -60, 0], clamp) : interpolate(t, [0, 3, 14], [0, 0, -520], clamp);
	return (
		<svg width={tam} height={tam * 1.3} viewBox="0 0 200 260" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 1.3 + alto, overflow: 'visible'}}>
			<ellipse cx={100} cy={40} rx={42} ry={36} fill="#7a4a2a" stroke={TINTA} strokeWidth={8} />
			<rect x={84} y={60} width={32} height={120} fill="#8a5a32" stroke={TINTA} strokeWidth={8} />
			<rect x={20} y={176} width={160} height={44} rx={6} fill="#5a3a22" stroke={TINTA} strokeWidth={8} />
			<rect x={26} y={218} width={148} height={22} fill="#c8202a" stroke={TINTA} strokeWidth={6} />
		</svg>
	);
};

export const Expediente: React.FC<{
	x: number;
	y: number;
	ancho: number;
	rot?: number;
	/** sellos ya puestos (posiciones relativas 0..1) y el cuadro en que cae cada uno */
	sellos?: {u: number; v: number; desde: number; rot?: number; texto?: string; color?: string}[];
	abierto?: boolean;
}> = ({x, y, ancho, rot = 0, sellos = [], abierto = false}) => {
	const alto = ancho * 0.72;
	const k = ancho / 800;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`}}>
			<div style={{position: 'absolute', left: 0, top: -50 * k, width: 260 * k, height: 80 * k, background: '#c99a4a', border: `${7 * k}px solid ${TINTA}`, borderRadius: `${16 * k}px ${16 * k}px 0 0`}} />
			<div style={{position: 'absolute', inset: 0, background: abierto ? '#f2e8cf' : '#d9ab58', border: `${7 * k}px solid ${TINTA}`, borderRadius: 10 * k, boxShadow: `${18 * k}px ${22 * k}px 0 rgba(0,0,0,0.3)`}} />
			{!abierto && (
				<div style={{position: 'absolute', left: 60 * k, top: 60 * k, padding: `${10 * k}px ${22 * k}px`, background: '#f6efdc', border: `${5 * k}px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 64 * k, color: '#2a2218', letterSpacing: 2 * k}}>
					EXPEDIENTE: A. HITLER
				</div>
			)}
			{sellos.map((s, i) => (
				<GolpeSello key={i} x={s.u * ancho} y={s.v * alto} desde={s.desde} tam={(s.texto === undefined ? 92 : 80) * k} rot={s.rot ?? -10 + i * 7} texto={s.texto} color={s.color} />
			))}
		</div>
	);
};

/** posiciones de los cuatro sellos INOFENSIVO en el expediente (siempre las mismas) */
export const SELLOS_EXPEDIENTE = [
	{u: 0.5, v: 0.55, rot: -10},
	{u: 0.3, v: 0.78, rot: 6},
	{u: 0.8, v: 0.5, rot: -4},
	{u: 0.66, v: 0.82, rot: 12},
];

/* ---------------- 5. la jarra de votos ---------------- */

/** La jarra de cerveza que mide los votos: la línea de MAYORÍA está en 50 % y la espuma nunca llega. */
export const JarraVotos: React.FC<{x: number; y: number; alto: number; nivel: number; etiqueta?: boolean; mayoria?: boolean; tono?: number}> = ({x, y, alto, nivel, etiqueta = true, mayoria = true, tono = 0}) => {
	const f = useCurrentFrame();
	const ancho = alto * 0.78;
	// interior del vaso: de y=70 (borde) a y=470 (fondo); 0 % abajo, 62 % arriba
	const TOPE = 62;
	const yN = (p: number) => 470 - (p / TOPE) * 400;
	const ny = yN(Math.max(0, nivel));
	const ola = Math.sin(f / 5) * 4;
	const cerveza = tono > 0 ? `rgb(${Math.round(232 - 120 * tono)},${Math.round(165 - 80 * tono)},${Math.round(40 + 40 * tono)})` : '#e8a528';
	return (
		<svg width={ancho} height={alto} viewBox="0 0 390 500" style={{position: 'absolute', left: x - ancho / 2, top: y - alto, overflow: 'visible'}}>
			<defs>
				<clipPath id={`vaso-${Math.round(x)}-${Math.round(y)}`}>
					<path d="M 46 60 L 60 470 Q 62 488 80 488 L 250 488 Q 268 488 270 470 L 284 60 Z" />
				</clipPath>
			</defs>
			{/* asa */}
			<path d="M 280 140 Q 380 140 376 250 Q 372 350 270 352" stroke={TINTA} strokeWidth={34} fill="none" strokeLinecap="round" />
			<path d="M 280 140 Q 380 140 376 250 Q 372 350 270 352" stroke="#dfe9ee" strokeWidth={18} fill="none" strokeLinecap="round" />
			<path d="M 46 60 L 60 470 Q 62 488 80 488 L 250 488 Q 268 488 270 470 L 284 60 Z" fill="rgba(220,236,242,0.35)" />
			<g clipPath={`url(#vaso-${Math.round(x)}-${Math.round(y)})`}>
				{nivel > 0.05 && (
					<>
						<rect x={0} y={ny} width={390} height={500} fill={cerveza} />
						{[0, 1, 2, 3, 4, 5].map((i) => {
							const by = 470 - ((f * (2 + (i % 3)) + i * 70) % Math.max(20, 470 - ny));
							return by > ny + 10 ? <circle key={i} cx={90 + i * 32} cy={by} r={6} fill="rgba(255,255,255,0.55)" /> : null;
						})}
						{/* espuma */}
						<path d={`M 0 ${ny + 14} Q 60 ${ny - 26 + ola} 110 ${ny - 6} Q 170 ${ny - 34 - ola} 220 ${ny - 8} Q 280 ${ny - 28 + ola} 390 ${ny + 10} L 390 ${ny + 26} L 0 ${ny + 26} Z`} fill="#fbf6ea" />
					</>
				)}
			</g>
			<path d="M 46 60 L 60 470 Q 62 488 80 488 L 250 488 Q 268 488 270 470 L 284 60 Z" fill="none" stroke={TINTA} strokeWidth={12} strokeLinejoin="round" />
			<path d="M 72 90 L 84 440" stroke="rgba(255,255,255,0.6)" strokeWidth={10} strokeLinecap="round" />
			{mayoria && (
				<g>
					<line x1={20} y1={yN(50)} x2={310} y2={yN(50)} stroke="#c8202a" strokeWidth={9} strokeDasharray="22 12" />
					<text x={-10} y={yN(50) - 16} fill="#c8202a" fontFamily={CONDENSADA} fontSize={40} letterSpacing={2}>
						MAYORÍA
					</text>
				</g>
			)}
			{etiqueta && nivel > 0.05 && (
				<g transform={`translate(${-150} ${Math.max(ny, 90) - 30})`}>
					<rect x={0} y={0} width={150} height={64} rx={10} fill="#f6efdc" stroke={TINTA} strokeWidth={6} />
					<text x={75} y={47} textAnchor="middle" fill="#2a2218" fontFamily={CONDENSADA} fontSize={44}>
						{nivel < 10 ? nivel.toFixed(1).replace('.', ',') : nivel >= 43 && nivel < 44 ? '43,9' : Math.round(nivel)} %
					</text>
				</g>
			)}
		</svg>
	);
};

/* ---------------- 6. la chistera de Papen ---------------- */

export const Chistera: React.FC<{x: number; y: number; ancho: number; rot?: number; brillo?: boolean}> = ({x, y, ancho, rot = 0, brillo = true}) => (
	<svg width={ancho} height={ancho * 0.95} viewBox="0 0 300 285" style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.95, transform: `rotate(${rot}deg)`, transformOrigin: '50% 100%', overflow: 'visible'}}>
		<ellipse cx={150} cy={250} rx={140} ry={30} fill="#1c1c22" stroke={TINTA} strokeWidth={9} />
		<path d="M 64 250 L 74 30 Q 150 6 226 30 L 236 250 Q 150 274 64 250 Z" fill="#26262e" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
		<path d="M 68 200 Q 150 222 232 200 L 234 236 Q 150 258 66 236 Z" fill="#8a2f3a" stroke={TINTA} strokeWidth={7} />
		{brillo && <path d="M 100 46 L 94 190" stroke="rgba(255,255,255,0.22)" strokeWidth={14} strokeLinecap="round" />}
		<ellipse cx={150} cy={30} rx={76} ry={16} fill="#33333c" stroke={TINTA} strokeWidth={8} />
	</svg>
);

/* ---------------- utilería que vuelve: sobre, cuenta, calendario ---------------- */

export const Cuenta: React.FC<{x: number; y: number; ancho: number; rot?: number; anio?: string}> = ({x, y, ancho, rot = 0, anio}) => {
	const k = ancho / 360;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, transform: `rotate(${rot}deg)`, background: '#fbf8ef', border: `${5 * k}px solid ${TINTA}`, padding: `${24 * k}px ${26 * k}px ${34 * k}px`, boxShadow: `${12 * k}px ${14 * k}px 0 rgba(0,0,0,0.3)`, fontFamily: TITULAR, color: '#2a2218'}}>
			<div style={{fontFamily: CONDENSADA, fontSize: 62 * k, textAlign: 'center', letterSpacing: 4 * k}}>LA CUENTA</div>
			<div style={{borderTop: `${3 * k}px dashed #2a2218`, margin: `${14 * k}px 0`}} />
			{['Mesa 1933', 'Servicio', 'Propina'].map((t, i) => (
				<div key={i} style={{display: 'flex', justifyContent: 'space-between', fontSize: 26 * k, fontWeight: 600, margin: `${8 * k}px 0`}}>
					<span>{t}</span>
					<span>· · ·</span>
				</div>
			))}
			<div style={{borderTop: `${3 * k}px dashed #2a2218`, margin: `${14 * k}px 0`}} />
			<div style={{display: 'flex', justifyContent: 'space-between', fontSize: 34 * k, fontWeight: 800}}>
				<span>TOTAL</span>
				<span>{anio ?? '???'}</span>
			</div>
		</div>
	);
};

export {pop as popRecurrente};
