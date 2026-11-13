import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {SERIF, TITULAR} from '../fuentes';

/* Utilería de la Atlántida (coordenadas del mundo 1080x1920). */

const TINTA = '#1b1b1f';
const ORO = '#f2c14e';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Ola con carita que se levanta del mar "obedeciendo" y hace una reverencia. */
export const OlaObediente: React.FC<{x: number; base: number; desde: number}> = ({x, base, desde}) => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	const sube = spring({frame: f - desde, fps, config: {damping: 10, stiffness: 90, mass: 0.8}});
	const reverencia = interpolate(f - desde, [24, 34, 44], [0, 28, 18], clamp);
	const alto = 520 * sube;
	if (alto < 4) return null;
	return (
		<div style={{position: 'absolute', left: x - 200, top: base - alto, width: 400, height: alto + 40, transform: `rotate(${reverencia}deg)`, transformOrigin: '50% 100%'}}>
			<svg viewBox="0 0 400 560" width="100%" height="100%" preserveAspectRatio="none" style={{overflow: 'visible'}}>
				<defs>
					<linearGradient id="olaObed" x1={0} y1={0} x2={0} y2={1}>
						<stop offset={0} stopColor="#7fe6f0" />
						<stop offset={1} stopColor="#0f7fa0" />
					</linearGradient>
				</defs>
				<path d="M 0 560 Q 20 220 140 80 Q 230 -10 320 60 Q 380 110 330 160 Q 290 120 250 150 Q 300 260 400 560 Z" fill="url(#olaObed)" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
				<path d="M 150 110 Q 230 40 310 80" stroke="#eafcff" strokeWidth={14} fill="none" strokeLinecap="round" />
				{/* carita */}
				<path d="M 150 250 Q 165 238 180 250" stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />
				<path d="M 220 250 Q 235 238 250 250" stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />
				<path d="M 170 290 Q 200 316 230 290" stroke={TINTA} strokeWidth={8} fill="none" strokeLinecap="round" />
				<ellipse cx={140} cy={278} rx={16} ry={9} fill="#ff8fa3" opacity={0.5} />
				<ellipse cx={262} cy={278} rx={16} ry={9} fill="#ff8fa3" opacity={0.5} />
			</svg>
		</div>
	);
};

/** Lluvia de monedas de oro. */
export const LluviaMonedas: React.FC<{desde: number; n?: number; x?: number; y?: number}> = ({desde, n = 40, x = 540, y = 1500}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0) return null;
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			{Array.from({length: n}).map((_, i) => {
				const vx = (random(`mvx${i}`) - 0.5) * 34;
				const vy = -30 - random(`mvy${i}`) * 26;
				const t = (l + random(`mt${i}`) * 30) % 60;
				const px = x + vx * t;
				const py = y + vy * t + 1.1 * t * t;
				const giro = Math.cos(t / 2 + i);
				return (
					<div key={i} style={{position: 'absolute', left: px - 26, top: py - 26, width: 52, height: 52, borderRadius: '50%', background: 'radial-gradient(circle at 35% 35%, #fff2b0, #f2c14e 45%, #c98a1a)', border: `5px solid ${TINTA}`, transform: `scaleX(${giro})`}} />
				);
			})}
		</AbsoluteFill>
	);
};

/** Título "ATLÁNTIDA" en letras doradas que aparecen una por una. */
export const TituloDorado: React.FC<{texto: string; y: number; desde: number; tam?: number}> = ({texto, y, desde, tam = 150}) => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	if (f < desde) return null;
	const brillo = 0.6 + 0.4 * Math.sin((f - desde) / 6);
	return (
		<div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center', gap: 2}}>
			{texto.split('').map((c, i) => {
				const s = spring({frame: f - desde - i * 2, fps, config: {damping: 9, stiffness: 200, mass: 0.6}});
				return (
					<span
						key={i}
						style={{
							display: 'inline-block',
							fontFamily: SERIF,
							fontWeight: 900,
							fontSize: tam,
							transform: `translateY(${(1 - s) * 80}px) scale(${s})`,
							opacity: s,
							background: 'linear-gradient(180deg,#fff6c8 0%,#f2c14e 45%,#b8761a 100%)',
							WebkitBackgroundClip: 'text',
							color: 'transparent',
							WebkitTextStroke: `4px ${TINTA}`,
							filter: `drop-shadow(0 0 ${24 * brillo}px rgba(255,210,100,0.9)) drop-shadow(0 8px 0 rgba(0,0,0,0.45))`,
						}}
					>
						{c}
					</span>
				);
			})}
		</div>
	);
};

/** Pergamino enrollado con su título. */
export const Pergamino: React.FC<{x: number; y: number; titulo: string; desde: number; rot?: number}> = ({x, y, titulo, desde, rot = 0}) => {
	const f = useCurrentFrame();
	const abre = interpolate(f, [desde, desde + 10], [0.1, 1], {...clamp, easing: Easing.out(Easing.back(1.5))});
	if (f < desde) return null;
	const ancho = 360;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, transform: `rotate(${rot}deg)`}}>
			<div style={{height: 380 * abre, background: 'linear-gradient(90deg,#e8d3a3,#f6e8c4 30%,#f6e8c4 70%,#e3c890)', border: `8px solid ${TINTA}`, borderTop: 'none', borderBottom: 'none', overflow: 'hidden', margin: '0 18px', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 40}}>
				<div style={{fontFamily: SERIF, fontWeight: 900, fontSize: 54, color: '#5a3416', letterSpacing: 4}}>{titulo}</div>
				{Array.from({length: 7}).map((_, i) => (
					<div key={i} style={{height: 10, width: `${[80, 70, 86, 64, 78, 60, 72][i]}%`, background: 'rgba(90,52,22,0.45)', borderRadius: 4, marginTop: 18}} />
				))}
			</div>
			{[0, 1].map((k) => (
				<div key={k} style={{position: 'absolute', left: 0, right: 0, top: k === 0 ? -26 : 380 * abre - 26, height: 52, borderRadius: 26, background: 'linear-gradient(180deg,#d9b779,#a57a3a)', border: `8px solid ${TINTA}`}} />
			))}
		</div>
	);
};

/** Tridente de Poseidón. */
export const Tridente: React.FC<{x: number; y: number; alto?: number; rot?: number; brilla?: boolean}> = ({x, y, alto = 1100, rot = 0, brilla}) => {
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', left: x - alto * 0.15, top: y - alto, width: alto * 0.3, height: alto, transform: `rotate(${rot}deg)`, transformOrigin: '50% 100%', filter: brilla ? `drop-shadow(0 0 ${20 + Math.sin(f / 2) * 10}px rgba(160,230,255,0.95))` : undefined}}>
			<svg viewBox="0 0 120 400" width="100%" height="100%" style={{overflow: 'visible'}}>
				<rect x={54} y={90} width={12} height={310} rx={6} fill={ORO} stroke={TINTA} strokeWidth={4} />
				<path d="M 20 100 L 20 30 L 10 40 L 20 4 L 30 40 L 20 30 M 20 100 Q 60 120 100 100 L 100 30 L 90 40 L 100 4 L 110 40 L 100 30 M 60 110 L 60 20 L 50 30 L 60 -10 L 70 30 L 60 20" fill={ORO} stroke={TINTA} strokeWidth={5} strokeLinejoin="round" />
			</svg>
		</div>
	);
};

/** Trozos de columna que caen y rebotan. */
export const ColumnasCayendo: React.FC<{desde: number}> = ({desde}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	if (l < 0) return null;
	return (
		<>
			{[0, 1, 2, 3].map((i) => {
				const x = [180, 860, 320, 720][i];
				const inicio = i * 6;
				const t = Math.max(0, l - inicio);
				const suelo = [1500, 1460, 1720, 1680][i];
				const y = Math.min(suelo, -200 + 0.9 * t * t * 3);
				const rot = t * (i % 2 ? 9 : -7);
				return (
					<div key={i} style={{position: 'absolute', left: x - 60, top: y - 110, width: 120, height: 220, transform: `rotate(${rot}deg)`}}>
						<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg,#f6f0e4 60%,#dcd0bb 60%)', border: `6px solid ${TINTA}`, borderRadius: 8}} />
						{[0.33, 0.66].map((k) => (
							<div key={k} style={{position: 'absolute', left: `${k * 100}%`, top: 10, bottom: 10, width: 5, background: '#dcd0bb'}} />
						))}
					</div>
				);
			})}
		</>
	);
};

/** Banda de mar en primer plano (tapa lo que está "detrás del horizonte"). */
export const MarDelante: React.FC<{y: number; tormenta?: boolean}> = ({y, tormenta}) => {
	const f = useCurrentFrame();
	const puntos = Array.from({length: 25}).map((_, i) => `${(i / 24) * 1180 - 50},${y + Math.sin(i * 0.9 + f / 6) * 10}`);
	return (
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
			<defs>
				<linearGradient id={`mar-${tormenta ? 't' : 'n'}`} x1={0} y1={0} x2={0} y2={1}>
					<stop offset={0} stopColor={tormenta ? '#2b3d63' : '#4fc6dc'} />
					<stop offset={1} stopColor={tormenta ? '#121b33' : '#0d6f93'} />
				</linearGradient>
			</defs>
			<polygon points={`${puntos.join(' ')} 1130,1970 -50,1970`} fill={`url(#mar-${tormenta ? 't' : 'n'})`} />
			<polyline points={puntos.join(' ')} fill="none" stroke="rgba(230,250,255,0.8)" strokeWidth={8} />
		</svg>
	);
};

/** Nombre que se "borra" con signos de pregunta. */
export const Desconocido: React.FC<{x: number; y: number; desde: number}> = ({x, y, desde}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const s = interpolate(f, [desde, desde + 6], [0.3, 1], {...clamp, easing: Easing.out(Easing.back(2))});
	return (
		<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) scale(${s}) rotate(-4deg)`, fontFamily: TITULAR, fontWeight: 900, fontSize: 110, color: '#ffd84a', WebkitTextStroke: `10px ${TINTA}`, paintOrder: 'stroke', letterSpacing: 6}}>
			¿¿???
		</div>
	);
};
