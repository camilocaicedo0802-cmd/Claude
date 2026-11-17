import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {CONDENSADA, SERIF} from '../fuentes';
import {Muneco, POSE_BASE, Pose, ROPA_NAPOLEON, animarPose} from './Muneco';

/*
 * Objetos que los personajes sostienen y usan.
 * "En la mano": coordenadas de la mano (origen en la muñeca, +y hacia los dedos, el puño en (0, 36)).
 * El resto va en coordenadas del mundo (1080 x 1920).
 */

const TINTA = '#1b1b1f';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const PUNO = 36;

const Giro: React.FC<{rot?: number; children: React.ReactNode}> = ({rot = 0, children}) => <g transform={`rotate(${rot} 0 ${PUNO})`}>{children}</g>;

/** Pluma de ganso para dibujar. */
export const Pluma: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<path d="M 6 70 Q -40 -30 -10 -170 Q 30 -70 16 60 Z" fill="#f7f3ea" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		<path d="M 10 60 Q 2 -40 -8 -156" stroke={TINTA} strokeWidth={3.5} fill="none" />
		{[-120, -90, -60, -30].map((y) => (
			<path key={y} d={`M ${-14 + y * 0.03} ${y} l -14 10`} stroke={TINTA} strokeWidth={3} />
		))}
		<line x1={8} y1={50} x2={12} y2={124} stroke={TINTA} strokeWidth={14} strokeLinecap="round" />
		<line x1={8} y1={50} x2={12} y2={124} stroke="#efe6d0" strokeWidth={7} strokeLinecap="round" />
		<path d="M 7 116 L 12 146 L 17 116 Z" fill="#20202a" />
	</Giro>
);

/** Sable. */
export const Espada: React.FC<{rot?: number; brillo?: number}> = ({rot = 0, brillo = 0}) => (
	<Giro rot={rot}>
		{brillo > 0 && <ellipse cx={0} cy={250} rx={60} ry={220} fill="#fff6c0" opacity={0.35 * brillo} />}
		<path d="M -11 70 L 11 70 L 14 330 Q 0 400 -14 330 Z" fill="#dfe6ee" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		<path d="M 0 78 L 0 340" stroke="#ffffff" strokeWidth={4} opacity={0.8} />
		<rect x={-44} y={58} width={88} height={16} rx={7} fill="#e0b23a" stroke={TINTA} strokeWidth={5} />
		<rect x={-9} y={-6} width={18} height={66} rx={6} fill="#5a3a1e" stroke={TINTA} strokeWidth={5} />
		<circle cx={0} cy={-10} r={12} fill="#e0b23a" stroke={TINTA} strokeWidth={5} />
	</Giro>
);

/** Dardo (el caricaturista se lo lanza al retrato). */
export const DardoMano: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<line x1={0} y1={10} x2={0} y2={120} stroke={TINTA} strokeWidth={14} strokeLinecap="round" />
		<line x1={0} y1={10} x2={0} y2={120} stroke="#c4262e" strokeWidth={7} strokeLinecap="round" />
		<path d="M -3 120 L 0 150 L 3 120 Z" fill="#9aa3ad" stroke={TINTA} strokeWidth={3} />
		<path d="M 0 30 L -22 -10 L 0 4 L 22 -10 Z" fill="#ffd84a" stroke={TINTA} strokeWidth={4} strokeLinejoin="round" />
	</Giro>
);

/** Mosquete con bayoneta, sostenido en vertical. */
export const Mosquete: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<path d="M -9 -430 L 9 -430 L 9 40 L -9 40 Z" fill="#5a5f66" stroke={TINTA} strokeWidth={5} />
		<path d="M -2 -430 L 0 -540 L 3 -430 Z" fill="#cfd6de" stroke={TINTA} strokeWidth={4} />
		<path d="M -14 -60 L 14 -60 L 18 60 L 26 170 L -22 170 L -16 60 Z" fill="#7a4a24" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		<rect x={-12} y={-250} width={24} height={14} fill="#e0b23a" stroke={TINTA} strokeWidth={3} />
	</Giro>
);

/** Bandera de Francia en un palito. */
export const Bandera: React.FC<{rot?: number}> = ({rot = 0}) => {
	const f = useCurrentFrame();
	return (
		<Giro rot={rot}>
			<line x1={0} y1={-30} x2={0} y2={330} stroke={TINTA} strokeWidth={12} strokeLinecap="round" />
			<line x1={0} y1={-30} x2={0} y2={330} stroke="#8a5a32" strokeWidth={6} strokeLinecap="round" />
			<g transform={`translate(0 230) skewY(${Math.sin(f / 4) * 5})`}>
				<rect x={0} y={0} width={50} height={100} fill="#1f3a7a" stroke={TINTA} strokeWidth={4} />
				<rect x={50} y={0} width={50} height={100} fill="#ffffff" stroke={TINTA} strokeWidth={4} />
				<rect x={100} y={0} width={50} height={100} fill="#e3262e" stroke={TINTA} strokeWidth={4} />
			</g>
		</Giro>
	);
};

/** Puntero de maestro. */
export const Puntero: React.FC<{rot?: number; largo?: number}> = ({rot = 0, largo = 330}) => (
	<Giro rot={rot}>
		<line x1={0} y1={10} x2={0} y2={largo} stroke={TINTA} strokeWidth={16} strokeLinecap="round" />
		<line x1={0} y1={10} x2={0} y2={largo} stroke="#b07a40" strokeWidth={9} strokeLinecap="round" />
		<circle cx={0} cy={largo} r={8} fill="#e3262e" stroke={TINTA} strokeWidth={4} />
	</Giro>
);

/** Tiza. */
export const Tiza: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<line x1={0} y1={46} x2={0} y2={96} stroke={TINTA} strokeWidth={18} strokeLinecap="round" />
		<line x1={0} y1={46} x2={0} y2={96} stroke="#ffffff" strokeWidth={10} strokeLinecap="round" />
	</Giro>
);

/** Caja de la cinta métrica. */
export const CajaCinta: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<rect x={-34} y={6} width={68} height={62} rx={14} fill="#ffcf2e" stroke={TINTA} strokeWidth={6} />
		<circle cx={0} cy={37} r={14} fill="#1b1b1f" />
	</Giro>
);

/** Lápiz / pluma de escribir pequeña (para la libreta del médico). */
export const Lapiz: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<line x1={0} y1={0} x2={0} y2={110} stroke={TINTA} strokeWidth={16} strokeLinecap="round" />
		<line x1={0} y1={0} x2={0} y2={110} stroke="#ffcf2e" strokeWidth={9} strokeLinecap="round" />
		<path d="M -6 106 L 0 128 L 6 106 Z" fill={TINTA} />
	</Giro>
);

/* ---------------- objetos del mundo ---------------- */

/** Cinta métrica estirada entre dos puntos del mundo. */
export const CintaEntre: React.FC<{x1: number; y1: number; x2: number; y2: number}> = ({x1, y1, x2, y2}) => {
	const largo = Math.hypot(x2 - x1, y2 - y1);
	if (largo < 4) return null;
	const ang = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI;
	return (
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible', pointerEvents: 'none'}}>
			<g transform={`translate(${x1} ${y1}) rotate(${ang})`}>
				<rect x={0} y={-17} width={largo} height={34} fill="#ffd84a" stroke={TINTA} strokeWidth={5} />
				{Array.from({length: Math.floor(largo / 20)}).map((_, i) => (
					<line key={i} x1={i * 20} y1={-17} x2={i * 20} y2={i % 5 === 0 ? 6 : -4} stroke={TINTA} strokeWidth={i % 5 === 0 ? 3.5 : 2} />
				))}
			</g>
		</svg>
	);
};

/** Dardo que vuela de (x1,y1) a (x2,y2) entre `desde` y `llega`, y se queda clavado. */
export const DardoVolando: React.FC<{x1: number; y1: number; x2: number; y2: number; desde: number; llega: number}> = ({x1, y1, x2, y2, desde, llega}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const t = interpolate(f, [desde, llega], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
	const x = x1 + (x2 - x1) * t;
	const y = y1 + (y2 - y1) * t - Math.sin(Math.PI * t) * 80;
	const vibra = f > llega ? Math.sin((f - llega) * 2.4) * 10 * Math.exp(-(f - llega) / 8) : 0;
	const ang = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI;
	return (
		<div style={{position: 'absolute', left: x - 90, top: y - 30, width: 120, height: 60, transform: `rotate(${ang + vibra}deg)`, transformOrigin: '75% 50%'}}>
			<svg viewBox="0 0 120 60" width="100%" height="100%" style={{overflow: 'visible'}}>
				<line x1={10} y1={30} x2={92} y2={30} stroke={TINTA} strokeWidth={14} strokeLinecap="round" />
				<line x1={10} y1={30} x2={92} y2={30} stroke="#c4262e" strokeWidth={7} strokeLinecap="round" />
				<path d="M 92 26 L 118 30 L 92 34 Z" fill="#9aa3ad" stroke={TINTA} strokeWidth={3} />
				<path d="M 30 30 L -10 8 L 4 30 L -10 52 Z" fill="#ffd84a" stroke={TINTA} strokeWidth={4} strokeLinejoin="round" />
			</svg>
		</div>
	);
};

/** El dibujo de "Little Boney": Napoleón cabezón y diminuto haciendo un berrinche (siempre el mismo dibujo). */
export const Caricatura: React.FC<{ancho: number; alto: number; desde?: number; berrinche?: number; titulo?: number; trazo?: boolean}> = ({ancho, alto, desde = -1e9, berrinche = -1e9, titulo = 1e9, trazo = true}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const revela = trazo ? interpolate(f, [desde, desde + 14], [0, 100], {...clamp, easing: Easing.inOut(Easing.quad)}) : 100;
	const enBerrinche = f >= berrinche;
	const l = f - berrinche;
	const pose: Partial<Pose> = enBerrinche
		? {
				bi: 150 + Math.sin(l * 0.42) * 18,
				ci: 20,
				bd: 150 + Math.cos(l * 0.42) * 18,
				cd: 20,
				mi: 'puno',
				md: 'puno',
				li: Math.max(0, Math.sin(l * 0.42)) * 0.5,
				ld: Math.max(0, -Math.sin(l * 0.42)) * 0.5,
				salto: Math.abs(Math.sin(l * 0.42)) * 16,
			}
		: animarPose(f, [[desde, {...POSE_BASE}]]);
	const letras = 'LITTLE BONEY';
	const nLetras = Math.floor(interpolate(f, [titulo, titulo + 10], [0, letras.length], clamp));
	return (
		<div style={{position: 'absolute', inset: 0, width: ancho, height: alto}}>
			<div style={{position: 'absolute', left: 0, top: 0, width: ancho, height: alto, clipPath: `inset(0 0 ${100 - revela}% 0)`}}>
				<div style={{position: 'absolute', left: ancho * 0.5 - alto * 0.25, top: alto * 0.33, width: alto * 0.5, height: alto * 0.62}}>
					<Muneco ropa={ROPA_NAPOLEON} pose={pose} escalaCabeza={1.5} ojos={enBerrinche ? 'cerrados' : 'grandes'} cejas={enBerrinche ? 'enojado' : 'sorprendido'} boca={enBerrinche ? 'grito' : 'o'} tiembla={0} sombra={false} />
				</div>
				{enBerrinche &&
					[0, 1].map((k) => {
						const ciclo = (l + k * 9) % 18;
						return (
							<div key={k} style={{position: 'absolute', left: ancho * 0.5 + (k ? 60 : -90) + (k ? 1 : -1) * ciclo * 3, top: alto * 0.33 + ciclo * ciclo * 0.5, width: 22, height: 30, borderRadius: '50% 50% 50% 50% / 60% 60% 40% 40%', background: '#7fd0ff', border: `4px solid ${TINTA}`, opacity: 1 - ciclo / 18}} />
						);
					})}
			</div>
			{nLetras > 0 && (
				<div style={{position: 'absolute', left: 0, right: 0, top: alto * 0.04, textAlign: 'center', fontFamily: SERIF, fontWeight: 900, fontStyle: 'italic', fontSize: ancho * 0.13, color: '#2a1f14', letterSpacing: 2, whiteSpace: 'nowrap'}}>
					{letras.slice(0, nLetras)}
				</div>
			)}
		</div>
	);
};

/** Hoja de papel envejecido (marco del dibujo). */
export const Papel: React.FC<{x: number; y: number; ancho: number; alto: number; rot?: number; children?: React.ReactNode; sepia?: boolean}> = ({x, y, ancho, alto, rot = 0, children, sepia = true}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`}}>
		<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(160deg,#f7eed6,#eadbb5)', border: `9px solid ${TINTA}`, boxShadow: '0 18px 30px rgba(0,0,0,0.4)'}} />
		<div style={{position: 'absolute', inset: 18, border: '4px solid rgba(60,40,20,0.5)'}} />
		<div style={{position: 'absolute', inset: 26, overflow: 'hidden', filter: sepia ? 'sepia(0.55) saturate(0.8) contrast(1.15)' : undefined}}>{children}</div>
	</div>
);

/** Atril de dibujo de madera con su hoja. */
export const Atril: React.FC<{x: number; y: number; ancho: number; alto: number; children?: React.ReactNode}> = ({x, y, ancho, alto, children}) => (
	<>
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
			<path d={`M ${x - ancho * 0.36} ${y + alto * 0.45} L ${x - ancho * 0.48} ${1920}`} stroke={TINTA} strokeWidth={34} strokeLinecap="round" />
			<path d={`M ${x - ancho * 0.36} ${y + alto * 0.45} L ${x - ancho * 0.48} ${1920}`} stroke="#8a5a32" strokeWidth={22} strokeLinecap="round" />
			<path d={`M ${x + ancho * 0.36} ${y + alto * 0.45} L ${x + ancho * 0.48} ${1920}`} stroke={TINTA} strokeWidth={34} strokeLinecap="round" />
			<path d={`M ${x + ancho * 0.36} ${y + alto * 0.45} L ${x + ancho * 0.48} ${1920}`} stroke="#8a5a32" strokeWidth={22} strokeLinecap="round" />
			<rect x={x - ancho / 2 - 24} y={y - alto / 2 - 24} width={ancho + 48} height={alto + 48} rx={14} fill="#a06a3c" stroke={TINTA} strokeWidth={9} />
			<rect x={x - ancho / 2 - 30} y={y + alto / 2 + 10} width={ancho + 60} height={34} rx={8} fill="#8a5a32" stroke={TINTA} strokeWidth={7} />
		</svg>
		<Papel x={x} y={y} ancho={ancho} alto={alto}>
			{children}
		</Papel>
	</>
);

/** Retrato enmarcado de Napoleón colgado en la pared (blanco de los dardos). */
export const Retrato: React.FC<{x: number; y: number; ancho: number; golpe?: number}> = ({x, y, ancho, golpe = 1e9}) => {
	const f = useCurrentFrame();
	const alto = ancho * 1.25;
	const sacude = f >= golpe ? Math.sin((f - golpe) * 1.8) * 6 * Math.exp(-(f - golpe) / 10) : 0;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${sacude}deg)`, transformOrigin: '50% 0%'}}>
			<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(135deg,#f6d36b,#c8901e)', border: `8px solid ${TINTA}`, borderRadius: 10}} />
			<div style={{position: 'absolute', inset: 30, background: 'radial-gradient(circle at 50% 35%, #6f8fb5, #2c3f5f)', border: `6px solid ${TINTA}`, overflow: 'hidden'}}>
				<div style={{position: 'absolute', left: '50%', top: '8%', width: (ancho - 60) * 1.15, height: (ancho - 60) * 1.15 * 2.25, transform: 'translateX(-50%)'}}>
					<Muneco ropa={ROPA_NAPOLEON} pose={{bi: 6, bd: 6, ci: 0, cd: 0}} ojos="entrecerrados" cejas="arrogante" boca="picara" sombra={false} respira={false} parpadea={false} />
				</div>
			</div>
		</div>
	);
};

/** Periódico abierto con la caricatura en portada (se sostiene delante del pecho: coordenadas del lienzo del muñeco). */
export const PeriodicoPecho: React.FC<{x?: number; y?: number; ancho?: number; alto?: number}> = ({x = 200, y = 450, ancho = 330, alto = 300}) => (
	<foreignObject x={x - ancho / 2} y={y - alto / 2} width={ancho} height={alto} style={{overflow: 'visible'}}>
		<div style={{width: ancho, height: alto, background: '#f2ecdc', border: `7px solid ${TINTA}`, boxSizing: 'border-box', padding: 10, transform: 'rotate(-2deg)'}}>
			<div style={{fontFamily: SERIF, fontWeight: 900, fontSize: 34, textAlign: 'center', color: '#1b1b1f', borderBottom: '4px solid #1b1b1f', lineHeight: 1.1}}>The Gazette</div>
			<div style={{display: 'flex', gap: 8, marginTop: 8}}>
				<div style={{position: 'relative', width: ancho * 0.52, height: alto * 0.66, background: '#e9dfc4', border: '3px solid #1b1b1f', overflow: 'hidden', filter: 'sepia(0.6) contrast(1.2)'}}>
					<Caricatura ancho={ancho * 0.52} alto={alto * 0.66} berrinche={-1e9} titulo={-1e9} trazo={false} />
				</div>
				<div style={{flex: 1}}>
					<div style={{fontFamily: CONDENSADA, fontSize: 30, lineHeight: 1, color: '#1b1b1f'}}>LITTLE BONEY</div>
					{Array.from({length: 7}).map((_, i) => (
						<div key={i} style={{height: 6, background: '#8a8170', marginTop: 9, width: `${[100, 90, 96, 80, 100, 70, 88][i]}%`}} />
					))}
				</div>
			</div>
		</div>
	</foreignObject>
);

/** Pedestal del veredicto. */
export const Pedestal: React.FC<{x: number; y: number; ancho?: number; alto?: number}> = ({x, y, ancho = 520, alto = 220}) => (
	<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
		<rect x={x - ancho / 2 - 30} y={y} width={ancho + 60} height={44} rx={8} fill="#7a4a24" stroke={TINTA} strokeWidth={8} />
		<rect x={x - ancho / 2} y={y + 44} width={ancho} height={alto} fill="#8a5a32" stroke={TINTA} strokeWidth={8} />
		<rect x={x - ancho / 2 + 30} y={y + 74} width={ancho - 60} height={alto - 60} fill="none" stroke="#5e3a1c" strokeWidth={6} />
		<rect x={x - ancho / 2 - 40} y={y + 44 + alto} width={ancho + 80} height={50} rx={8} fill="#6b4020" stroke={TINTA} strokeWidth={8} />
	</svg>
);

/** Nota de papel con texto manuscrito. */
export const Nota: React.FC<{x: number; y: number; texto: string; desde: number; rot?: number; tam?: number}> = ({x, y, texto, desde, rot = -4, tam = 54}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const s = interpolate(f, [desde, desde + 7], [0.3, 1], {...clamp, easing: Easing.out(Easing.back(2))});
	const n = Math.floor(interpolate(f, [desde + 3, desde + 18], [0, texto.length], clamp));
	return (
		<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) scale(${s}) rotate(${rot}deg)`, background: '#fbf6e6', border: `7px solid ${TINTA}`, borderRadius: 8, padding: '14px 30px 18px', boxShadow: '0 12px 0 rgba(0,0,0,0.35)', whiteSpace: 'nowrap'}}>
			<span style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 900, fontSize: tam, color: '#1b2a6b'}}>{texto.slice(0, n)}</span>
			<span style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 900, fontSize: tam, color: 'transparent'}}>{texto.slice(n)}</span>
		</div>
	);
};

export {POSE_BASE};

/* =================== María Antonieta =================== */

/** Abanico abierto (en la mano). */
export const Abanico: React.FC<{color?: string; rot?: number; abre?: number}> = ({color = '#ffd3e2', rot = 0, abre = 1}) => {
	const varillas = 9;
	const apertura = 120 * abre;
	return (
		<Giro rot={rot}>
			<g transform={`translate(0 ${PUNO})`}>
				<path d={`M 0 0 L ${Math.sin(((-apertura / 2) * Math.PI) / 180) * 120} ${Math.cos(((-apertura / 2) * Math.PI) / 180) * 120} A 120 120 0 0 0 ${Math.sin(((apertura / 2) * Math.PI) / 180) * 120} ${Math.cos(((apertura / 2) * Math.PI) / 180) * 120} Z`} fill={color} stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
				{Array.from({length: varillas}).map((_, i) => {
					const a = ((-apertura / 2 + (apertura * i) / (varillas - 1)) * Math.PI) / 180;
					return <line key={i} x1={0} y1={0} x2={Math.sin(a) * 118} y2={Math.cos(a) * 118} stroke={TINTA} strokeWidth={2.5} opacity={0.5} />;
				})}
				<path d={`M ${Math.sin(((-apertura / 2) * Math.PI) / 180) * 84} ${Math.cos(((-apertura / 2) * Math.PI) / 180) * 84} A 84 84 0 0 0 ${Math.sin(((apertura / 2) * Math.PI) / 180) * 84} ${Math.cos(((apertura / 2) * Math.PI) / 180) * 84}`} stroke="#ffffff" strokeWidth={6} fill="none" opacity={0.8} />
			</g>
		</Giro>
	);
};

/** Antorcha encendida (en la mano, apuntando hacia los dedos). */
export const Antorcha: React.FC<{rot?: number}> = ({rot = 0}) => {
	const f = useCurrentFrame();
	const l = Math.sin(f / 5) * 6;
	return (
		<Giro rot={rot}>
			<line x1={0} y1={-60} x2={0} y2={170} stroke={TINTA} strokeWidth={22} strokeLinecap="round" />
			<line x1={0} y1={-60} x2={0} y2={170} stroke="#7a4a24" strokeWidth={13} strokeLinecap="round" />
			<rect x={-20} y={150} width={40} height={36} rx={6} fill="#5a5f66" stroke={TINTA} strokeWidth={5} />
			<circle cx={0} cy={230} r={90} fill="#ffb347" opacity={0.18} />
			<path d={`M -30 186 Q -40 ${240 + l} 0 ${290 + l} Q 40 ${240 - l} 30 186 Z`} fill="#ff8a1e" stroke={TINTA} strokeWidth={5} strokeLinejoin="round" />
			<path d={`M -14 190 Q -16 ${230 + l} 0 ${256 + l} Q 16 ${230 - l} 14 190 Z`} fill="#ffe066" />
		</Giro>
	);
};

/** Canasta vacía colgando de la mano. */
export const Canasta: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<path d="M -60 120 Q 0 -10 60 120" stroke={TINTA} strokeWidth={14} fill="none" />
		<path d="M -60 120 Q 0 -10 60 120" stroke="#b07a40" strokeWidth={7} fill="none" />
		<path d="M -80 110 L 80 110 L 62 200 Q 0 214 -62 200 Z" fill="#c9904a" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
		{[-50, -20, 10, 40].map((x) => (
			<line key={x} x1={x} y1={116} x2={x + 6} y2={200} stroke="#8a5a2a" strokeWidth={5} />
		))}
		<path d="M -78 140 L 78 140 M -72 170 L 72 170" stroke="#8a5a2a" strokeWidth={5} />
	</Giro>
);

/** Muñeca de trapo (en la mano). */
export const Muneca: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<g transform="translate(0 20) scale(0.9)">
			<path d="M -36 40 L 36 40 L 56 150 Q 0 166 -56 150 Z" fill="#ff8fb8" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
			<circle cx={0} cy={6} r={36} fill="#fff4e6" stroke={TINTA} strokeWidth={6} />
			<path d="M -36 0 Q 0 -50 36 0 Q 20 -16 0 -18 Q -20 -16 -36 0 Z" fill="#f0cc68" stroke={TINTA} strokeWidth={5} />
			<circle cx={-12} cy={8} r={4} fill={TINTA} />
			<circle cx={12} cy={8} r={4} fill={TINTA} />
			<path d="M -8 22 Q 0 28 8 22" stroke={TINTA} strokeWidth={3} fill="none" />
		</g>
	</Giro>
);

/** Libro cerrado (en la mano). */
export const LibroMano: React.FC<{rot?: number; color?: string}> = ({rot = 0, color = '#8a2f2f'}) => (
	<Giro rot={rot}>
		<rect x={-58} y={-10} width={116} height={150} rx={8} fill={color} stroke={TINTA} strokeWidth={6} />
		<rect x={-58} y={-10} width={18} height={150} fill="#5e1f1f" stroke={TINTA} strokeWidth={4} />
		<rect x={-28} y={30} width={70} height={40} fill="#e0b23a" stroke={TINTA} strokeWidth={3} />
	</Giro>
);

/** Plato con un trozo de pastel (en la mano). */
export const PlatoPastel: React.FC<{rot?: number}> = ({rot = 0}) => (
	<Giro rot={rot}>
		<ellipse cx={0} cy={60} rx={80} ry={20} fill="#ffffff" stroke={TINTA} strokeWidth={6} />
		<path d="M -46 54 L -46 6 L 46 -6 L 46 46 Q 0 64 -46 54 Z" fill="#ffd9e6" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		<path d="M -46 6 L 46 -6 L 30 -26 L -60 -12 Z" fill="#ffffff" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		<path d="M -46 28 L 46 18" stroke="#ff8fb8" strokeWidth={8} />
		<circle cx={-10} cy={-26} r={12} fill="#e3262e" stroke={TINTA} strokeWidth={4} />
	</Giro>
);

/** Brioche dorado (en el mundo). */
export const Brioche: React.FC<{x: number; y: number; tam?: number; desde?: number; rot?: number}> = ({x, y, tam = 260, desde = -1e9, rot = 0}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const s = interpolate(f, [desde, desde + 8], [0.2, 1], {...clamp, easing: Easing.out(Easing.back(2.2))});
	return (
		<div style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, width: tam, height: tam, transform: `scale(${s}) rotate(${rot}deg)`}}>
			<svg viewBox="-100 -100 200 200" width="100%" height="100%" style={{overflow: 'visible'}}>
				<ellipse cx={0} cy={50} rx={90} ry={22} fill="rgba(0,0,0,0.25)" />
				<path d="M -84 40 Q -96 -20 -50 -30 Q 0 -50 50 -30 Q 96 -20 84 40 Q 0 64 -84 40 Z" fill="#e8a33a" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
				{[-48, -16, 16, 48].map((dx) => (
					<path key={dx} d={`M ${dx} -34 Q ${dx + 6} 6 ${dx} 44`} stroke="#b9741f" strokeWidth={6} fill="none" />
				))}
				<circle cx={0} cy={-52} r={34} fill="#f0b44a" stroke={TINTA} strokeWidth={7} />
				<path d="M -60 -14 Q -40 -26 -20 -20" stroke="#fff3c4" strokeWidth={8} fill="none" strokeLinecap="round" opacity={0.8} />
				<circle cx={-10} cy={-62} r={8} fill="#fff3c4" opacity={0.8} />
			</svg>
		</div>
	);
};

/** Pastel de varios pisos sobre una mesa (en el mundo). */
export const PastelMesa: React.FC<{x: number; y: number; ancho?: number}> = ({x, y, ancho = 420}) => (
	<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.9, width: ancho, height: ancho}}>
		<svg viewBox="-200 -330 400 400" width="100%" height="100%" style={{overflow: 'visible'}}>
			<rect x={-200} y={40} width={400} height={30} rx={8} fill="#8a5a32" stroke={TINTA} strokeWidth={6} />
			<path d="M -180 70 L -150 300 M 180 70 L 150 300" stroke={TINTA} strokeWidth={16} />
			<ellipse cx={0} cy={36} rx={170} ry={22} fill="#ffffff" stroke={TINTA} strokeWidth={6} />
			{[
				[150, 90, '#ffd9e6'],
				[112, 80, '#c9e8ff'],
				[76, 70, '#ffd9e6'],
			].map(([w, h, c], i) => {
				const base = 30 - [0, 90, 170][i];
				return (
					<g key={i}>
						<rect x={-(w as number)} y={base - (h as number)} width={(w as number) * 2} height={h as number} rx={14} fill={c as string} stroke={TINTA} strokeWidth={6} />
						<path d={`M ${-(w as number)} ${base - (h as number) + 18} ${Array.from({length: 6}).map(() => `q ${(w as number) / 6} 22 ${(w as number) / 3} 0`).join(' ')}`} stroke="#ffffff" strokeWidth={10} fill="none" />
					</g>
				);
			})}
			{[-40, 0, 40].map((dx) => (
				<circle key={dx} cx={dx} cy={-218} r={13} fill="#e3262e" stroke={TINTA} strokeWidth={4} />
			))}
			<path d="M 0 -232 L 0 -290" stroke={TINTA} strokeWidth={6} />
			<path d="M 0 -290 q 10 -14 0 -28 q -10 14 0 28" fill="#ffb02e" />
		</svg>
	</div>
);

/** Libro abierto con texto manuscrito que aparece (en el mundo). */
export const LibroAbierto: React.FC<{x: number; y: number; ancho: number; titulo?: string; lineas: {texto: string; desde: number; resaltar?: boolean}[]; rot?: number}> = ({x, y, ancho, titulo, lineas, rot = -3}) => {
	const f = useCurrentFrame();
	const alto = ancho * 0.66;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - alto / 2, width: ancho, height: alto, transform: `rotate(${rot}deg)`, filter: 'drop-shadow(0 20px 0 rgba(0,0,0,0.35))'}}>
			<div style={{position: 'absolute', inset: 0, background: '#7a2f2f', borderRadius: 18, border: `8px solid ${TINTA}`}} />
			{[0, 1].map((k) => (
				<div key={k} style={{position: 'absolute', top: 16, bottom: 22, left: k ? '50%' : 18, right: k ? 18 : '50%', background: 'linear-gradient(90deg,#f3e8cc,#fbf4e2)', border: `5px solid ${TINTA}`, borderRadius: k ? '0 10px 10px 0' : '10px 0 0 10px'}} />
			))}
			{titulo && <div style={{position: 'absolute', left: 40, width: ancho / 2 - 70, top: 50, fontFamily: SERIF, fontWeight: 900, fontSize: ancho * 0.05, color: '#3a2414', textAlign: 'center'}}>{titulo}</div>}
			{titulo &&
				Array.from({length: 6}).map((_, i) => (
					<div key={i} style={{position: 'absolute', left: 50, width: ancho / 2 - 90 - (i % 3) * 20, top: 130 + i * 34, height: 7, background: 'rgba(60,40,20,0.35)', borderRadius: 4}} />
				))}
			<div style={{position: 'absolute', left: ancho / 2 + 22, right: 40, top: 46, display: 'flex', flexDirection: 'column', gap: 12}}>
				{lineas.map((l, i) => {
					const n = Math.floor(interpolate(f, [l.desde, l.desde + 14], [0, l.texto.length], clamp));
					return (
						<div key={i} style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 700, fontSize: ancho * 0.042, lineHeight: 1.15, color: '#2a1f14', background: l.resaltar && n > 0 ? 'rgba(255,216,74,0.75)' : undefined, borderRadius: 6, padding: '0 4px'}}>
							{l.texto.slice(0, n)}
							<span style={{color: 'transparent'}}>{l.texto.slice(n)}</span>
						</div>
					);
				})}
			</div>
		</div>
	);
};

/** Carta manuscrita que se va escribiendo (en el mundo). */
export const Carta: React.FC<{x: number; y: number; ancho: number; encabezado: string; texto: string; desde: number; duracion?: number; resaltar?: string; rot?: number}> = ({x, y, ancho, encabezado, texto, desde, duracion = 60, resaltar, rot = 2}) => {
	const f = useCurrentFrame();
	const n = Math.floor(interpolate(f, [desde, desde + duracion], [0, texto.length], clamp));
	const visible = texto.slice(0, n);
	const partes = resaltar && visible.includes(resaltar.slice(0, 1)) ? visible.split(resaltar) : [visible];
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, transform: `rotate(${rot}deg)`, background: 'linear-gradient(160deg,#fbf3dc,#efdfb8)', border: `8px solid ${TINTA}`, borderRadius: 10, padding: '30px 40px 44px', boxShadow: '0 18px 0 rgba(0,0,0,0.35)'}}>
			<div style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 900, fontSize: ancho * 0.06, color: '#3a2414', marginBottom: 14}}>{encabezado}</div>
			<div style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 700, fontSize: ancho * 0.05, lineHeight: 1.3, color: '#1b2a6b'}}>
				{partes.length > 1
					? partes.map((p, i) => (
							<React.Fragment key={i}>
								{p}
								{i < partes.length - 1 && <span style={{background: 'rgba(255,216,74,0.8)', borderRadius: 6}}>{resaltar}</span>}
							</React.Fragment>
						))
					: visible}
			</div>
		</div>
	);
};

/** Cofre del tesoro del que se escapan monedas (la ruina de Francia). */
export const Cofre: React.FC<{x: number; y: number; ancho?: number; desde: number}> = ({x, y, ancho = 300, desde}) => {
	const f = useCurrentFrame();
	const l = f - desde;
	return (
		<>
			{l > 0 &&
				Array.from({length: 22}).map((_, i) => {
					const t = (l * 0.9 + i * 7) % 46;
					const vx = (((i * 37) % 21) - 10) * 2.4;
					const px = x + vx * t;
					const py = y - 40 - 26 * t + 0.95 * t * t;
					return <div key={i} style={{position: 'absolute', left: px - 22, top: py - 22, width: 44, height: 44, borderRadius: '50%', background: 'radial-gradient(circle at 35% 35%, #fff2b0, #f2c14e 45%, #c98a1a)', border: `4px solid ${TINTA}`, transform: `scaleX(${Math.cos(t / 3 + i)})`}} />;
				})}
			<div style={{position: 'absolute', left: x - ancho / 2, top: y - ancho * 0.45, width: ancho, height: ancho * 0.7}}>
				<svg viewBox="0 0 300 210" width="100%" height="100%" style={{overflow: 'visible'}}>
					<path d="M 10 70 L 290 70 L 280 200 L 20 200 Z" fill="#8a5a2a" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
					<path d="M 10 70 Q 150 -40 290 70 Z" fill="#a06a3c" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" transform="rotate(-24 10 70)" />
					<rect x={10} y={110} width={280} height={18} fill="#e0b23a" stroke={TINTA} strokeWidth={5} />
					<rect x={130} y={100} width={40} height={44} rx={6} fill="#e0b23a" stroke={TINTA} strokeWidth={5} />
				</svg>
			</div>
		</>
	);
};

/** Carruaje pequeño (para el mapa). */
export const Carruaje: React.FC<{x: number; y: number; tam?: number; voltear?: boolean}> = ({x, y, tam = 170, voltear}) => {
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.7, width: tam, height: tam * 0.8, transform: `scaleX(${voltear ? -1 : 1}) translateY(${Math.abs(Math.sin(f / 3)) * -4}px)`}}>
			<svg viewBox="0 0 200 160" width="100%" height="100%" style={{overflow: 'visible'}}>
				<path d="M 40 40 Q 40 10 100 10 Q 160 10 160 40 L 170 110 L 30 110 Z" fill="#f2c14e" stroke={TINTA} strokeWidth={7} strokeLinejoin="round" />
				<rect x={70} y={36} width={60} height={40} rx={8} fill="#9ec9ea" stroke={TINTA} strokeWidth={5} />
				<circle cx={100} cy={4} r={10} fill="#e0b23a" stroke={TINTA} strokeWidth={4} />
				{[55, 145].map((cx) => (
					<g key={cx} transform={`rotate(${f * 8} ${cx} 124)`}>
						<circle cx={cx} cy={124} r={28} fill="#ffffff" stroke={TINTA} strokeWidth={7} />
						<line x1={cx - 24} y1={124} x2={cx + 24} y2={124} stroke={TINTA} strokeWidth={4} />
						<line x1={cx} y1={100} x2={cx} y2={148} stroke={TINTA} strokeWidth={4} />
					</g>
				))}
			</svg>
		</div>
	);
};
