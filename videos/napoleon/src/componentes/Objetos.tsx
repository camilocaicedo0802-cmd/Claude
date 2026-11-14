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
