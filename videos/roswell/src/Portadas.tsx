import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Actor, Muneco, alcanzar} from './componentes/Muneco';
import {Sello} from './componentes/Utileria';
import {CONDENSADA} from './fuentes';
import {brazo} from './escenas/compartidas';
import {Periodico} from './escenas/utileria_c89';
import {EscDesiertoNoche, GloboRisa, Informe1994, OvniBrillante, Red, SOLDADO_47} from './escenas/utileria_roswell';

/* Portadas del short de Roswell (1080x1920). Textos y caras dentro de y = 260..1650. */

const TINTA = '#111114';
const AMARILLO = '#ffc21a';
const VERDE = '#7dffb8';

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

/* ---------- 1. CAPTURARON UN OVNI… ERA SU GLOBO ---------- */

export const PortadaGlobo: React.FC = () => (
	<AbsoluteFill>
		<EscDesiertoNoche />
		<Actor x={330} y={1700} alto={1000}>
			<Muneco ropa={SOLDADO_47} pose={{...brazo(1, alcanzar(1, 340, 200)), md: 'agarra', ...brazo(-1, alcanzar(-1, 150, 380)), mi: 'agarra', cabeza: -8}} ojos="grandes" cejas="sorprendido" boca="o" />
		</Actor>
		<Red x1={470} y1={1300} x2={660} y2={1080} radio={200} />
		<OvniBrillante x={660} y={880} tam={440} revela={1} />
		<Arriba>
			<Titular texto={'CAPTURARON\nUN OVNI…'} tam={150} color={VERDE} rot={-2} />
		</Arriba>
		<div style={{position: 'absolute', left: 0, right: 0, top: 1440, display: 'flex', justifyContent: 'center'}}>
			<Titular texto="¡Y ERA SU GLOBO!" tam={110} color={AMARILLO} rot={-3} />
		</div>
	</AbsoluteFill>
);

/* ---------- 2. EL PERIÓDICO DE 1947 + MITO ---------- */

export const PortadaPeriodico: React.FC = () => (
	<AbsoluteFill>
		<EscDesiertoNoche />
		<div style={{position: 'absolute', inset: 0, transform: 'rotate(-6deg)'}}>
			<Periodico x={540} y={560} ancho={940} titular="¡CAPTURAN UN PLATILLO VOLADOR!" fecha="8 DE JULIO DE 1947" nombre="Roswell Daily Record" />
		</div>
		<Arriba>
			<Titular texto="ROSWELL 1947" tam={150} color={AMARILLO} rot={-2} />
		</Arriba>
		<Sello x={560} y={1360} texto="MITO" desde={-100} color="#d6262e" tam={220} rot={-12} solido />
	</AbsoluteFill>
);

/* ---------- 3. SÍ HABÍA UN SECRETO (pero no era un ovni) ---------- */

export const PortadaSecreto: React.FC = () => (
	<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, #2a3048 0%, #10121c 75%)'}}>
		<div style={{position: 'absolute', inset: 0, transform: 'rotate(4deg)'}}>
			<Informe1994 x={540} y={560} ancho={860} tacha={1} />
		</div>
		<GloboRisa x={800} y={1470} tam={340} />
		<Arriba>
			<Titular texto={'SÍ HABÍA\nUN SECRETO'} tam={140} color={AMARILLO} rot={-2} />
		</Arriba>
		<Sello x={420} y={1540} texto="NO ERA UN OVNI" desde={-100} color="#d6262e" tam={58} rot={-8} solido />
	</AbsoluteFill>
);
