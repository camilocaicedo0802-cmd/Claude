import React from 'react';
import {Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {CONDENSADA, SERIF} from '../fuentes';
import {CIUDADES, yDeCm} from '../escenarios/Escenarios';

/* Utilería del short de Napoleón (coordenadas del mundo 1080x1920). */

const TINTA = '#1b1b1f';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const usePop = (desde: number, rigidez = 200) => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	return spring({frame: f - desde, fps, config: {damping: 10, stiffness: rigidez, mass: 0.6}});
};

/** Línea de estatura sobre la tabla, con su etiqueta. */
export const MarcaAltura: React.FC<{cm: number; desde: number; color?: string; texto?: string; lado?: 'izq' | 'der'; x1?: number; x2?: number}> = ({
	cm,
	desde,
	color = '#e3262e',
	texto,
	lado = 'der',
	x1 = 110,
	x2 = 970,
}) => {
	const f = useCurrentFrame();
	const p = interpolate(f, [desde, desde + 8], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const etiqueta = usePop(desde + 4);
	if (f < desde) return null;
	const y = yDeCm(cm);
	const xa = lado === 'der' ? x1 : x2;
	const xb = xa + (x2 - x1) * p * (lado === 'der' ? 1 : -1);
	return (
		<>
			<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
				<line x1={xa} y1={y} x2={xb} y2={y} stroke={TINTA} strokeWidth={16} strokeLinecap="round" />
				<line x1={xa} y1={y} x2={xb} y2={y} stroke={color} strokeWidth={9} strokeLinecap="round" strokeDasharray="28 14" />
			</svg>
			<div
				style={{
					position: 'absolute',
					left: lado === 'der' ? x2 - 10 : x1 + 10,
					top: y,
					transform: `translate(${lado === 'der' ? '-100%' : '0'}, -120%) scale(${etiqueta})`,
					transformOrigin: lado === 'der' ? '100% 100%' : '0% 100%',
					background: color,
					border: `8px solid ${TINTA}`,
					borderRadius: 18,
					padding: '4px 22px 8px',
					fontFamily: CONDENSADA,
					fontSize: 64,
					letterSpacing: 1,
					color: '#ffffff',
					whiteSpace: 'nowrap',
					boxShadow: '0 8px 0 rgba(0,0,0,0.35)',
				}}
			>
				{texto ?? `${(cm / 100).toFixed(2).replace('.', ',')} m`}
			</div>
		</>
	);
};

/** Hoja de papel de caricatura (con borde de tinta) donde se "dibuja" a Napoleón. */
export const HojaCaricatura: React.FC<{x: number; y: number; ancho: number; alto: number; rot?: number; titulo?: string; children?: React.ReactNode}> = ({x, y, ancho, alto, rot = -2, titulo, children}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`}}>
		<div style={{position: 'absolute', inset: 0, background: '#f4ead2', border: `10px solid ${TINTA}`, boxShadow: '0 20px 34px rgba(0,0,0,0.45)'}} />
		<div style={{position: 'absolute', inset: 22, border: '4px solid rgba(40,30,20,0.55)'}} />
		<div style={{position: 'absolute', inset: 30, overflow: 'hidden', filter: 'grayscale(0.25) sepia(0.35) contrast(1.15)'}}>{children}</div>
		{titulo && (
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 44, textAlign: 'center', fontFamily: SERIF, fontWeight: 900, fontStyle: 'italic', fontSize: ancho * 0.09, color: '#2a1f14'}}>{titulo}</div>
		)}
	</div>
);

/** Pluma que "dibuja" moviéndose en zigzag. */
export const Pluma: React.FC<{x: number; y: number; desde: number; tam?: number}> = ({x, y, desde, tam = 300}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const l = f - desde;
	const dx = Math.sin(l / 2.2) * 40;
	const dy = Math.cos(l / 3.1) * 26;
	return (
		<div style={{position: 'absolute', left: x + dx, top: y + dy - tam, width: tam * 0.5, height: tam, transform: 'rotate(28deg)', transformOrigin: '0% 100%'}}>
			<svg viewBox="0 0 100 200" width="100%" height="100%" style={{overflow: 'visible'}}>
				<path d="M 4 196 Q 30 120 90 10 Q 60 90 40 120 Q 30 150 4 196 Z" fill="#f6f2e8" stroke={TINTA} strokeWidth={5} strokeLinejoin="round" />
				<path d="M 4 196 L 26 150" stroke={TINTA} strokeWidth={5} />
				<path d="M 0 200 L 10 186" stroke="#20202a" strokeWidth={8} strokeLinecap="round" />
			</svg>
		</div>
	);
};

/** Periódicos que vuelan desde Londres hacia las capitales. */
export const PeriodicosVolando: React.FC<{desde: number}> = ({desde}) => {
	const f = useCurrentFrame();
	const [lx, ly] = CIUDADES.LONDRES;
	const destinos = Object.entries(CIUDADES).filter(([n]) => n !== 'LONDRES');
	return (
		<>
			{destinos.map(([n, [x, y]], i) => {
				const ini = desde + i * 6;
				const p = interpolate(f, [ini, ini + 22], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
				if (f < ini) return null;
				const px = lx + (x - lx) * p;
				const py = ly + (y - ly) * p - Math.sin(p * Math.PI) * 160;
				return (
					<React.Fragment key={n}>
						<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
							<path d={`M ${lx} ${ly} Q ${(lx + x) / 2} ${(ly + y) / 2 - 260} ${x} ${y}`} stroke="#e3262e" strokeWidth={7} strokeDasharray="18 14" fill="none" opacity={0.85} pathLength={1} strokeDashoffset={0} />
						</svg>
						<div style={{position: 'absolute', left: px - 70, top: py - 90, width: 140, height: 180, transform: `rotate(${(1 - p) * 360 + (i % 2 ? 8 : -8)}deg) scale(${0.6 + p * 0.4})`, background: '#f4f1e6', border: `6px solid ${TINTA}`, boxShadow: '0 10px 16px rgba(0,0,0,0.3)', padding: 8, boxSizing: 'border-box'}}>
							<div style={{fontFamily: SERIF, fontWeight: 900, fontSize: 18, textAlign: 'center', borderBottom: `3px solid ${TINTA}`, lineHeight: 1.1}}>THE GAZETTE</div>
							<div style={{margin: '8px auto 0', width: 46, height: 46, borderRadius: '50%', border: `4px solid ${TINTA}`, position: 'relative'}}>
								<div style={{position: 'absolute', left: -8, top: -16, width: 62, height: 20, background: TINTA, borderRadius: '50% 50% 10px 10px'}} />
							</div>
							{[80, 64, 76].map((w, k) => (
								<div key={k} style={{height: 6, width: `${w}%`, background: 'rgba(0,0,0,0.45)', marginTop: 8, borderRadius: 3}} />
							))}
						</div>
					</React.Fragment>
				);
			})}
		</>
	);
};

/** Comparación de pulgadas en la pizarra (inglesa 2,54 cm vs francesa 2,71 cm). */
export const Pulgadas: React.FC<{desde: number; y0?: number; paso?: number}> = ({desde, y0 = 490, paso = 340}) => {
	const f = useCurrentFrame();
	const a = interpolate(f, [desde, desde + 12], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const b = interpolate(f, [desde + 12, desde + 26], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	const escala = 240; // px por cm
	const fila = (y: number, cm: number, p: number, etiqueta: string, color: string) => (
		<div style={{position: 'absolute', left: 130, top: y}}>
			<div style={{fontFamily: CONDENSADA, fontSize: 70, lineHeight: 1, letterSpacing: 1, textTransform: 'uppercase', color: 'rgba(250,250,245,0.95)', marginBottom: 14}}>{etiqueta}</div>
			<div style={{display: 'flex', alignItems: 'center', gap: 18}}>
				<div style={{width: cm * escala * p, height: 110, background: color, border: '6px solid rgba(250,250,245,0.95)', borderRadius: 10, boxSizing: 'border-box'}} />
				<div style={{fontFamily: CONDENSADA, fontSize: 80, color: color, opacity: p, whiteSpace: 'nowrap'}}>{`${cm.toFixed(2).replace('.', ',')} cm`}</div>
			</div>
		</div>
	);
	return (
		<>
			{fila(y0, 2.54, a, '1 pulgada inglesa', '#9fd3ff')}
			{fila(y0 + paso, 2.71, b, '1 pulgada francesa', '#ffd84a')}
		</>
	);
};

/** Cinta métrica que se estira horizontalmente. */
export const CintaMetrica: React.FC<{x: number; y: number; largo: number; desde: number}> = ({x, y, largo, desde}) => {
	const f = useCurrentFrame();
	const p = interpolate(f, [desde, desde + 18], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
	if (f < desde) return null;
	return (
		<div style={{position: 'absolute', left: x, top: y, width: largo * p, height: 46, background: '#ffd84a', border: `6px solid ${TINTA}`, overflow: 'hidden'}}>
			{Array.from({length: 40}).map((_, i) => (
				<div key={i} style={{position: 'absolute', left: i * 26, top: 0, width: 4, height: i % 5 === 0 ? 30 : 16, background: TINTA}} />
			))}
		</div>
	);
};

/** Corazones que suben flotando. */
export const Corazones: React.FC<{x: number; y: number; desde: number; n?: number}> = ({x, y, desde, n = 10}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	return (
		<>
			{Array.from({length: n}).map((_, i) => {
				const l = (f - desde + i * 9) % 60;
				const px = x + (random(`hx${i}`) - 0.5) * 700 + Math.sin(l / 6 + i) * 20;
				const py = y - l * 9;
				const t = 50 + random(`ht${i}`) * 40;
				return (
					<svg key={i} viewBox="0 0 100 100" width={t} height={t} style={{position: 'absolute', left: px - t / 2, top: py - t / 2, opacity: interpolate(l, [0, 8, 45, 60], [0, 1, 1, 0])}}>
						<path d="M 50 88 C 10 60 0 34 22 18 C 38 8 50 22 50 30 C 50 22 62 8 78 18 C 100 34 90 60 50 88 Z" fill="#ff4d6d" stroke={TINTA} strokeWidth={6} />
					</svg>
				);
			})}
		</>
	);
};

/** Lágrimas de berrinche que salen disparadas. */
export const Lagrimas: React.FC<{x: number; y: number; desde: number}> = ({x, y, desde}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	return (
		<>
			{Array.from({length: 8}).map((_, i) => {
				const l = (f - desde + i * 4) % 22;
				const lado = i % 2 ? 1 : -1;
				const px = x + lado * (60 + l * 9);
				const py = y + l * l * 0.7 - l * 6;
				return <div key={i} style={{position: 'absolute', left: px, top: py, width: 26, height: 34, background: '#8fd3ff', border: `4px solid ${TINTA}`, borderRadius: '50% 50% 50% 50% / 60% 60% 40% 40%', opacity: interpolate(l, [0, 3, 18, 22], [0, 1, 1, 0])}} />;
			})}
		</>
	);
};
