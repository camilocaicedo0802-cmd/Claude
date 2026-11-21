import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn} from './componentes/Muneco';
import {Sello} from './componentes/Utileria';
import {CONDENSADA} from './fuentes';
import {brazo} from './escenas/compartidas';
import {Cartel, Certificado, EscParisAtardecer, EscPasillo, Escritorio, LUSTIG, SobreGordo, TorreEiffel} from './escenas/utileria_eiffel';

/* Portadas del short de la Torre Eiffel (1080x1920). Textos y caras dentro de y = 260..1650. */

const TINTA = '#111114';
const AMARILLO = '#ffc21a';

const Titular: React.FC<{texto: string; tam: number; color?: string; rot?: number}> = ({texto, tam, color = '#fff', rot = 0}) => {
	const base: React.CSSProperties = {fontFamily: CONDENSADA, fontSize: tam, lineHeight: 0.95, letterSpacing: tam * 0.01, textAlign: 'center', whiteSpace: 'pre', textTransform: 'uppercase'};
	return (
		<div style={{position: 'relative', transform: `rotate(${rot}deg)`, filter: `drop-shadow(0 ${tam * 0.07}px 0 rgba(0,0,0,0.6))`}}>
			<div style={{...base, color: TINTA, WebkitTextStroke: `${tam * 0.17}px ${TINTA}`}}>{texto}</div>
			<div style={{...base, color, position: 'absolute', inset: 0}}>{texto}</div>
		</div>
	);
};

const Arriba: React.FC<{children: React.ReactNode; top?: number}> = ({children, top = 270}) => <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>{children}</div>;
const Abajo: React.FC<{children: React.ReactNode; top: number}> = ({children, top}) => <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>{children}</div>;

const Baston: React.FC = () => (
	<g>
		<line x1={0} y1={20} x2={0} y2={420} stroke={TINTA} strokeWidth={20} strokeLinecap="round" />
		<line x1={0} y1={20} x2={0} y2={420} stroke="#3a2414" strokeWidth={11} strokeLinecap="round" />
		<path d="M 0 30 Q 0 -30 -50 -20" stroke="#c9a43a" strokeWidth={16} fill="none" strokeLinecap="round" />
	</g>
);

/* ---------- 1. VENDIÓ LA TORRE EIFFEL ---------- */

export const PortadaVendida: React.FC = () => (
	<AbsoluteFill>
		<EscParisAtardecer />
		<TorreEiffel x={440} y={1900} alto={1500} />
		<Cartel x={430} y={670} ancho={520} />
		<Sello x={500} y={905} texto="VENDIDA" desde={-100} color="#d6262e" tam={80} rot={-12} solido />
		<Actor x={830} y={2130} alto={1250}>
			<Muneco ropa={LUSTIG} pose={{...brazo(1, alcanzar(1, 330, 520)), md: 'agarra', ...manosEn([150, 560]), mi: 'relajada', cabeza: -8}} objDer={<Baston />} ojos="guinoX" cejas="arrogante" boca="picara" />
		</Actor>
		<Arriba>
			<Titular texto={'VENDIÓ LA\nTORRE EIFFEL'} tam={150} color={AMARILLO} rot={-2} />
		</Arriba>
		<Abajo top={1480}>
			<Titular texto="¡Y QUISO REPETIRLO!" tam={104} rot={-3} />
		</Abajo>
	</AbsoluteFill>
);

/* ---------- 2. EL TRUCO DEL SOBORNO ---------- */

export const PortadaSoborno: React.FC = () => (
	<AbsoluteFill>
		<EscPasillo />
		<Actor x={470} y={2230} alto={1550}>
			<Muneco ropa={LUSTIG} pose={{...brazo(1, alcanzar(1, 380, 330)), md: 'abierta', ...manosEn([150, 560]), mi: 'relajada', cabeza: 6}} ojos="entrecerrados" cejas="arrogante" boca="picara" />
		</Actor>
		<SobreGordo x={830} y={1330} tam={330} rot={10} />
		<Arriba>
			<Titular texto={'PIDIÓ UN SOBORNO…'} tam={128} rot={-2} />
		</Arriba>
		<Abajo top={1500}>
			<Titular texto={'¡Y POR ESO LE CREYERON!'} tam={88} color={AMARILLO} rot={-3} />
		</Abajo>
	</AbsoluteFill>
);

/* ---------- 3. VENDEDOR APRENDIZ ---------- */

export const PortadaAprendiz: React.FC = () => (
	<AbsoluteFill>
		<Escritorio />
		<div style={{position: 'absolute', inset: 0, transform: 'rotate(-3deg)'}}>
			<Certificado x={540} y={560} ancho={960} escribe={1} />
			<svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
				<ellipse cx={668} cy={1092} rx={265} ry={66} fill="none" stroke="#d6262e" strokeWidth={12} transform="rotate(-2 668 1092)" />
			</svg>
		</div>
		<Arriba>
			<Titular texto={'¿SU PROFESIÓN\nOFICIAL?'} tam={130} color={AMARILLO} rot={-2} />
		</Arriba>
		<Sello x={540} y={1410} texto="REAL" desde={-100} color="#1f9d48" tam={190} rot={-10} solido />
	</AbsoluteFill>
);
