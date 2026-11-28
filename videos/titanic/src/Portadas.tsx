import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Actor, Muneco, alcanzar, manosFrente} from './componentes/Muneco';
import {Sello} from './componentes/Utileria';
import {CONDENSADA} from './fuentes';
import {brazo} from './escenas/compartidas';
import {Armario, CofaFrente, CuentaAtras, EscNocheMar, Iceberg, Llave, Titanic, VIGIA, VIGIA2} from './escenas/utileria_titanic';

/* Portadas del short del Titanic (1080x1920). Textos y caras dentro de y = 260..1650. */

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

const En: React.FC<{children: React.ReactNode; top: number}> = ({children, top}) => <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>{children}</div>;

/* ---------- 1. UNA LLAVE PUDO SALVAR EL TITANIC ---------- */

export const PortadaLlave: React.FC = () => (
	<AbsoluteFill>
		<EscNocheMar horizonte={1330} />
		<Titanic x={430} y={1330} ancho={860} luces={1} noche />
		<Iceberg x={960} y={1330} ancho={220} noche silueta={1} />
		<Llave x={560} y={830} tam={760} rot={-12} brillo={1} />
		<En top={270}>
			<Titular texto={'UNA LLAVE PUDO\nSALVAR EL TITANIC'} tam={122} color={AMARILLO} rot={-2} />
		</En>
		<En top={1470}>
			<Titular texto="¡Y NUNCA SUBIÓ AL BARCO!" tam={86} rot={-3} />
		</En>
	</AbsoluteFill>
);

/* ---------- 2. SOLO 37 SEGUNDOS ---------- */

export const Portada37: React.FC = () => (
	<AbsoluteFill>
		<EscNocheMar horizonte={1280} />
		<Iceberg x={880} y={1280} ancho={380} noche silueta={1} />
		<Actor x={330} y={1720} alto={1000}>
			<Muneco ropa={VIGIA} pose={{...brazo(1, alcanzar(1, 390, 290)), md: 'senala'}} ojos="grandes" cejas="sorprendido" boca="o" />
		</Actor>
		<Actor x={640} y={1720} alto={960}>
			<Muneco ropa={VIGIA2} pose={manosFrente([150, 520], [250, 520])} ojos="grandes" cejas="sorprendido" boca="o" />
		</Actor>
		<CofaFrente x={500} y={1280} ancho={880} campana={0.3} />
		<CuentaAtras x={540} y={420} ancho={560} segundos={37} />
		<En top={270}>
			<Titular texto="LES QUEDABAN…" tam={120} rot={-2} />
		</En>
		<En top={1500}>
			<Titular texto="¡Y SIN PRISMÁTICOS!" tam={104} color={AMARILLO} rot={-3} />
		</En>
	</AbsoluteFill>
);

/* ---------- 3. ¿Y LA LLAVE DE LOS PRISMÁTICOS? ---------- */

export const PortadaArmario: React.FC = () => (
	<AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, #5a4632, #1a120c 75%)'}}>
		<Armario x={540} y={560} ancho={700} cerradura={1} />
		<svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
			<rect x={790} y={980} width={240} height={120} rx={22} fill="none" stroke="#ffd66a" strokeWidth={7} strokeDasharray="20 13" />
			<text x={910} y={1064} textAnchor="middle" fontFamily={CONDENSADA} fontSize={74} fill="#ffd66a">?</text>
		</svg>
		<En top={270}>
			<Titular texto={'¿QUIÉN SE LLEVÓ\nLA LLAVE?'} tam={124} color={AMARILLO} rot={-2} />
		</En>
		<Sello x={540} y={1530} texto="MEDIO MITO" desde={-100} color="#e07a1a" tam={120} rot={-8} solido />
	</AbsoluteFill>
);
