import React from 'react';
import {AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {SERIF as serif, TITULAR as fontFamily} from '../fuentes';

const TINTA = '#1b1b1f';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const usePop = (desde: number, rigidez = 180) => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	return spring({frame: f - desde, fps, config: {damping: 9, stiffness: rigidez, mass: 0.6}});
};

/** Bombilla de "idea" que aparece con rebote y rayos. */
export const Bombilla: React.FC<{x: number; y: number; tam?: number; desde: number}> = ({x, y, tam = 220, desde}) => {
	const f = useCurrentFrame();
	const p = usePop(desde);
	if (f < desde) return null;
	const brillo = 0.75 + 0.25 * Math.sin((f - desde) / 2);
	return (
		<div style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, width: tam, height: tam, transform: `scale(${p}) rotate(${(1 - p) * -30}deg)`}}>
			<svg viewBox="0 0 200 200" width="100%" height="100%" style={{overflow: 'visible'}}>
				<g transform={`rotate(${(f - desde) * 2} 100 82)`} opacity={brillo}>
					{Array.from({length: 10}).map((_, i) => (
						<line key={i} x1={100} y1={-2} x2={100} y2={-30} stroke="#ffd84a" strokeWidth={10} strokeLinecap="round" transform={`rotate(${i * 36} 100 82)`} />
					))}
				</g>
				<circle cx={100} cy={82} r={80} fill="#fff6a8" opacity={0.35 * brillo} />
				<path d="M 100 20 C 48 20 30 66 50 100 C 62 120 72 128 72 150 L 128 150 C 128 128 138 120 150 100 C 170 66 152 20 100 20 Z" fill="#ffe14d" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
				<path d="M 82 120 Q 100 92 118 120" stroke="#e0a400" strokeWidth={7} fill="none" />
				<rect x={72} y={150} width={56} height={34} rx={8} fill="#9aa0a8" stroke={TINTA} strokeWidth={8} />
				<line x1={76} y1={164} x2={124} y2={164} stroke={TINTA} strokeWidth={5} />
				<ellipse cx={74} cy={62} rx={12} ry={20} fill="#fff" opacity={0.8} transform="rotate(25 74 62)" />
			</svg>
		</div>
	);
};

/** Hoja de calendario que pasa años rápido hasta caer en el último. */
export const Calendario: React.FC<{x: number; y: number; ancho: number; anios: number[]; cambios: number[]}> = ({x, y, ancho, anios, cambios}) => {
	const f = useCurrentFrame();
	let idx = 0;
	cambios.forEach((c, i) => {
		if (f >= c) idx = i + 1;
	});
	idx = Math.min(idx, anios.length - 1);
	const ultimoCambio = idx > 0 ? cambios[idx - 1] : -999;
	const giro = interpolate(f - ultimoCambio, [0, 5], [-75, 0], {...clamp, easing: Easing.out(Easing.back(2))});
	const esFinal = idx === anios.length - 1;
	const golpe = esFinal ? interpolate(f - ultimoCambio, [0, 3, 10], [1.25, 0.95, 1], clamp) : 1;
	const alto = ancho * 1.25;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: alto, perspective: 1200}}>
			{/* hoja que se va */}
			{idx > 0 && f - ultimoCambio < 6 && (
				<Hoja anio={anios[idx - 1]} ancho={ancho} alto={alto} estilo={{transform: `rotateX(${interpolate(f - ultimoCambio, [0, 6], [0, 100], clamp)}deg)`, transformOrigin: '50% 0%', zIndex: 2}} />
			)}
			<Hoja anio={anios[idx]} ancho={ancho} alto={alto} resaltado={esFinal} estilo={{transform: `rotateX(${idx > 0 ? giro * 0.15 : 0}deg) scale(${golpe})`, transformOrigin: '50% 0%'}} />
		</div>
	);
};

const Hoja: React.FC<{anio: number; ancho: number; alto: number; resaltado?: boolean; estilo?: React.CSSProperties}> = ({anio, ancho, alto, resaltado, estilo}) => (
	<div
		style={{
			position: 'absolute',
			inset: 0,
			background: '#fbf6e9',
			border: `${ancho * 0.018}px solid ${TINTA}`,
			borderRadius: ancho * 0.04,
			boxShadow: '0 18px 30px rgba(0,0,0,0.35)',
			overflow: 'hidden',
			...estilo,
		}}
	>
		<div style={{height: alto * 0.2, background: '#c3342b', borderBottom: `${ancho * 0.018}px solid ${TINTA}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontFamily, fontWeight: 900, fontSize: ancho * 0.1, letterSpacing: 4}}>
			CALENDARIO
		</div>
		<div style={{textAlign: 'center', fontFamily: serif, fontWeight: 900, fontSize: ancho * 0.36, lineHeight: 1.6, color: resaltado ? '#c3342b' : TINTA}}>{anio}</div>
		<div style={{display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: ancho * 0.02, padding: `0 ${ancho * 0.08}px`}}>
			{Array.from({length: 21}).map((_, i) => (
				<div key={i} style={{height: ancho * 0.05, borderRadius: 4, background: 'rgba(27,27,31,0.14)'}} />
			))}
		</div>
	</div>
);

/** Flecha discontinua que se dibuja sola (mapas). */
export const Flecha: React.FC<{d: string; desde: number; duracion?: number; color?: string; grosor?: number}> = ({d, desde, duracion = 22, color = '#e3262e', grosor = 22}) => {
	const f = useCurrentFrame();
	const ref = React.useRef<SVGPathElement>(null);
	const [largo, setLargo] = React.useState(2000);
	React.useLayoutEffect(() => {
		if (ref.current) setLargo(ref.current.getTotalLength());
	}, [d]);
	const p = interpolate(f, [desde, desde + duracion], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
	if (f < desde) return null;
	let punta = {x: 0, y: 0, a: 0};
	if (ref.current && p > 0) {
		const L = largo * p;
		const a = ref.current.getPointAtLength(Math.max(0, L - 1));
		const b = ref.current.getPointAtLength(L);
		punta = {x: b.x, y: b.y, a: (Math.atan2(b.y - a.y, b.x - a.x) * 180) / Math.PI};
	}
	return (
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
			<mask id={`m-${desde}`}>
				<path d={d} stroke="#fff" strokeWidth={grosor + 20} fill="none" strokeDasharray={largo} strokeDashoffset={largo * (1 - p)} strokeLinecap="round" />
			</mask>
			<path ref={ref} d={d} stroke={TINTA} strokeWidth={grosor + 12} fill="none" strokeDasharray="46 26" strokeLinecap="round" mask={`url(#m-${desde})`} />
			<path d={d} stroke={color} strokeWidth={grosor} fill="none" strokeDasharray="46 26" strokeLinecap="round" mask={`url(#m-${desde})`} />
			{p > 0.05 && (
				<g transform={`translate(${punta.x} ${punta.y}) rotate(${punta.a})`}>
					<path d="M 34 0 L -26 -34 L -14 0 L -26 34 Z" fill={color} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
				</g>
			)}
		</svg>
	);
};

/** Etiqueta tipo "pin" de mapa con texto. */
export const Etiqueta: React.FC<{x: number; y: number; texto: string; desde: number; color?: string; tam?: number}> = ({x, y, texto, desde, color = '#ffffff', tam = 74}) => {
	const f = useCurrentFrame();
	const p = usePop(desde, 220);
	if (f < desde) return null;
	return (
		<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -100%) scale(${p})`, transformOrigin: '50% 100%', display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
			<div style={{background: color, border: `9px solid ${TINTA}`, borderRadius: 26, padding: '10px 34px 14px', fontFamily, fontWeight: 900, fontSize: tam, color: TINTA, boxShadow: '0 12px 0 rgba(0,0,0,0.35)', letterSpacing: 2}}>{texto}</div>
			<svg width={60} height={50} viewBox="0 0 60 50" style={{marginTop: -9}}>
				<path d="M 4 0 L 30 44 L 56 0 Z" fill={color} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
				<rect x={0} y={0} width={60} height={6} fill={color} />
			</svg>
		</div>
	);
};

/** Destello de explosión (bola de fuego + onda) en coordenadas del mundo. */
export const Explosion: React.FC<{x: number; y: number; desde: number; tam?: number}> = ({x, y, desde, tam = 420}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0 || l > 26) return null;
	const s = interpolate(l, [0, 6, 26], [0.2, 1, 1.25], {...clamp, easing: Easing.out(Easing.cubic)});
	const o = interpolate(l, [0, 3, 14, 26], [0, 1, 0.8, 0], clamp);
	return (
		<div style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, width: tam, height: tam, transform: `scale(${s})`, opacity: o, mixBlendMode: 'screen'}}>
			<div style={{position: 'absolute', inset: 0, borderRadius: '50%', background: 'radial-gradient(circle, #fffbe0 0%, #ffd23f 22%, #ff7a1a 45%, rgba(255,60,0,0.5) 62%, rgba(255,60,0,0) 72%)'}} />
		</div>
	);
};

/** Destello que ilumina toda la pantalla (para acompañar explosiones o golpes). */
export const Destello: React.FC<{desde: number; color?: string; fuerza?: number; duracion?: number}> = ({desde, color = '#ffb347', fuerza = 0.55, duracion = 10}) => {
	const f = useCurrentFrame();
	const o = interpolate(f - desde, [0, 2, duracion], [0, fuerza, 0], clamp);
	if (o <= 0) return null;
	return <AbsoluteFill style={{background: color, opacity: o, mixBlendMode: 'screen'}} />;
};

/** Moscas que revolotean alrededor de un punto (para el cadáver). */
export const Moscas: React.FC<{x: number; y: number; radio?: number; n?: number}> = ({x, y, radio = 150, n = 4}) => {
	const f = useCurrentFrame();
	return (
		<>
			{Array.from({length: n}).map((_, i) => {
				const a = f / (5 + i) + i * 2.1;
				const px = x + Math.cos(a) * radio * (0.7 + 0.3 * Math.sin(f / 9 + i));
				const py = y + Math.sin(a * 1.3) * radio * 0.55;
				const ala = Math.abs(Math.sin(f * 1.7 + i)) * 10 + 4;
				return (
					<svg key={i} viewBox="-30 -30 60 60" width={46} height={46} style={{position: 'absolute', left: px - 23, top: py - 23, overflow: 'visible'}}>
						<ellipse cx={-8} cy={-10} rx={ala} ry={6} fill="rgba(220,240,255,0.85)" stroke={TINTA} strokeWidth={2.5} />
						<ellipse cx={8} cy={-10} rx={ala} ry={6} fill="rgba(220,240,255,0.85)" stroke={TINTA} strokeWidth={2.5} />
						<ellipse cx={0} cy={0} rx={11} ry={8} fill={TINTA} />
					</svg>
				);
			})}
		</>
	);
};
