import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Colgante, EscHotel, Fortaleza, NEON_C, NEON_M, Stick} from './componentes/Hacker';
import {CONDENSADA, TITULAR} from './fuentes';
import {CuartoHotel} from './escenas/Historia';

/* Portadas del short del hacker (1080x1920). Textos y caras dentro de y = 260..1650.
   Sin nombre ni parecido con el chico, sin logos ni imágenes del juego. */

const TINTA = '#111114';
const AMARILLO = '#ffc21a';
const ROJO = '#e3262e';
const VERDE = '#1f9d48';

const Titular: React.FC<{texto: string; tam: number; color?: string; rot?: number}> = ({texto, tam, color = '#fff', rot = 0}) => {
	const base: React.CSSProperties = {fontFamily: CONDENSADA, fontSize: tam, lineHeight: 0.95, letterSpacing: tam * 0.01, textAlign: 'center', whiteSpace: 'pre', textTransform: 'uppercase'};
	return (
		<div style={{position: 'relative', transform: `rotate(${rot}deg)`, filter: `drop-shadow(0 ${tam * 0.07}px 0 rgba(0,0,0,0.6))`}}>
			<div style={{...base, color: TINTA, WebkitTextStroke: `${tam * 0.17}px ${TINTA}`}}>{texto}</div>
			<div style={{...base, color, position: 'absolute', inset: 0}}>{texto}</div>
		</div>
	);
};

const Sello: React.FC<{texto: string; color: string; tam: number; rot?: number}> = ({texto, color, tam, rot = -10}) => (
	<div style={{transform: `rotate(${rot}deg)`, border: `${tam * 0.09}px solid ${color}`, borderRadius: tam * 0.16, padding: `${tam * 0.16}px ${tam * 0.22}px ${tam * 0.08}px`, background: 'rgba(255,255,255,0.94)', boxShadow: '0 14px 0 rgba(0,0,0,0.45)'}}>
		<div style={{fontFamily: CONDENSADA, fontSize: tam, lineHeight: 1, color, letterSpacing: tam * 0.03, whiteSpace: 'nowrap'}}>{texto}</div>
	</div>
);

const Arriba: React.FC<{children: React.ReactNode; top?: number}> = ({children, top = 266}) => <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>{children}</div>;
const Abajo: React.FC<{children: React.ReactNode; top: number; left?: number; right?: number}> = ({children, top, left = 0, right = 0}) => <div style={{position: 'absolute', left, right, top, display: 'flex', justifyContent: 'center'}}>{children}</div>;

/* ---------- 1. HACKEÓ GTA 6 DESDE LA TELE DE UN HOTEL ---------- */

export const PortadaHotel: React.FC = () => (
	<AbsoluteFill style={{background: '#16224a'}}>
		<AbsoluteFill style={{transform: 'translateY(170px) scale(1.18)', transformOrigin: '50% 75%'}}>
			<EscHotel />
			<CuartoHotel abre={1} etiqueta={-30} />
		</AbsoluteFill>
		<Arriba>
			<Titular texto="HACKEÓ GTA 6" tam={170} color={AMARILLO} />
			<Titular texto={'DESDE LA TELE\nDE UN HOTEL'} tam={104} />
		</Arriba>
		<Abajo top={1470} right={300}>
			<Sello texto="¡ES REAL!" color={VERDE} tam={120} rot={-7} />
		</Abajo>
	</AbsoluteFill>
);

/* ---------- 2. HACKEÓ GTA 6 CON ESTO ---------- */

export const PortadaAparatito: React.FC = () => (
	<AbsoluteFill style={{background: 'radial-gradient(ellipse at 45% 55%, #3a1470 0%, #0b0418 70%)'}}>
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
			{Array.from({length: 12}).map((_, i) => (
				<line key={i} x1={0} y1={1500 + i * i * 4} x2={1080} y2={1500 + i * i * 4} stroke="#ff4fa3" strokeWidth={3} opacity={0.4} />
			))}
			{Array.from({length: 11}).map((_, i) => (
				<line key={`v${i}`} x1={540 + (i - 5) * 30} y1={1500} x2={540 + (i - 5) * 260} y2={1920} stroke="#ff4fa3" strokeWidth={3} opacity={0.35} />
			))}
			<path d="M 760 1020 C 900 900, 860 1250, 840 1330" stroke={NEON_C} strokeWidth={16} fill="none" strokeLinecap="round" style={{filter: `drop-shadow(0 0 18px ${NEON_C})`}} />
		</svg>
		<Fortaleza x={840} y={1640} ancho={380} abre={1} />
		<Stick x={430} y={960} largo={700} rot={-12} etiqueta="40 USD" etiquetaDesde={-30} tamEtiqueta={0.62} />
		<Arriba>
			<Titular texto="HACKEÓ GTA 6" tam={150} />
			<Titular texto="CON ESTO" tam={210} color={AMARILLO} />
		</Arriba>
		{/* flecha hacia el aparatito */}
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%', overflow: 'visible'}}>
			<path d="M 180 640 Q 120 760 210 860" stroke={TINTA} strokeWidth={34} fill="none" strokeLinecap="round" />
			<path d="M 180 640 Q 120 760 210 860" stroke={AMARILLO} strokeWidth={20} fill="none" strokeLinecap="round" />
			<path d="M 160 860 L 250 880 L 215 800 Z" fill={AMARILLO} stroke={TINTA} strokeWidth={10} strokeLinejoin="round" />
		</svg>
	</AbsoluteFill>
);

/* ---------- 3. LA POLICÍA LE DIO EL CUARTO PERFECTO ---------- */

export const PortadaPuerta: React.FC = () => (
	<AbsoluteFill style={{background: '#16224a'}}>
		{/* luz morada de la tele que sale por debajo de la puerta */}
		<div style={{position: 'absolute', left: 120, right: 120, top: 1560, height: 300, background: `radial-gradient(ellipse at 50% 0%, ${NEON_M}cc, ${NEON_M}00 70%)`}} />
		<div style={{position: 'absolute', left: 200, top: 300, width: 680, height: 1460, background: '#1f2a55', border: `14px solid ${TINTA}`}}>
			<div style={{position: 'absolute', left: 60, right: 60, top: 60, height: 520, border: `8px solid ${TINTA}`, opacity: 0.4}} />
			<div style={{position: 'absolute', left: 60, right: 60, top: 760, height: 560, border: `8px solid ${TINTA}`, opacity: 0.4}} />
			<div style={{position: 'absolute', left: 46, top: 690, width: 50, height: 50, borderRadius: '50%', background: '#c9a43a', border: `8px solid ${TINTA}`}} />
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 1754, height: 30, background: `${NEON_M}`, opacity: 0.55, filter: 'blur(6px)'}} />
		<Colgante x={271} y={740} texto={'NO\nMOLESTAR'} tam={1.2} />
		<div style={{position: 'absolute', left: 392, top: 690, width: 440, transform: 'rotate(-3deg)', background: '#fff8e1', border: `10px solid ${TINTA}`, borderRadius: 10, padding: '26px 26px', textAlign: 'center', boxShadow: '0 16px 0 rgba(0,0,0,0.4)'}}>
			<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 34, letterSpacing: 6, color: '#1f3a7a'}}>POLICÍA</div>
			<div style={{fontFamily: CONDENSADA, fontSize: 86, lineHeight: 1, color: TINTA, marginTop: 8}}>PROTECCIÓN POLICIAL</div>
		</div>
		<Abajo top={1150}>
			<div style={{transform: 'rotate(-6deg)', background: '#ffd23f', border: `10px solid ${TINTA}`, borderRadius: 24, padding: '20px 40px', textAlign: 'center', boxShadow: '0 14px 0 rgba(0,0,0,0.4)'}}>
				<div style={{fontFamily: CONDENSADA, fontSize: 88, color: TINTA, letterSpacing: 8, lineHeight: 1}}>★★★★★</div>
				<div style={{fontFamily: CONDENSADA, fontSize: 70, color: TINTA, lineHeight: 1.05}}>IDEAL PARA HACKEAR</div>
			</div>
		</Abajo>
		<Arriba>
			<Titular texto="LA POLICÍA LE DIO" tam={118} />
			<Titular texto={'EL CUARTO\nPERFECTO'} tam={150} color={AMARILLO} />
		</Arriba>
		<Abajo top={1470}>
			<Sello texto="REAL" color={ROJO} tam={110} rot={8} />
		</Abajo>
	</AbsoluteFill>
);
