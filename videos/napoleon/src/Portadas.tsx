import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {HojaCaricatura, Lagrimas, MarcaAltura} from './componentes/Napoleon';
import {FRANCES, NAPOLEON, Personaje} from './componentes/Personaje';
import {EnMundo} from './componentes/Toma';
import {Rayos} from './componentes/Utileria';
import {EscCelular, EscEstudio, EscMedidas, MEME, PISO, altoParaCm} from './escenarios/Escenarios';
import {TITULAR} from './fuentes';

/* Portadas del short de Napoleón (1080x1920). Texto y caras dentro de y=260..1650. */

const TINTA = '#111114';
const AMARILLO = '#ffd84a';
const ROJO = '#e3262e';

const Fondo: React.FC<{src: string; escala?: number; x?: number; y?: number; filtro?: string}> = ({src, escala = 1.1, x = 0, y = 0, filtro}) => (
	<AbsoluteFill style={{transform: `translate(${x}px, ${y}px) scale(${escala})`, filter: filtro}}>
		<Img src={staticFile(`fondos/${src}`)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
	</AbsoluteFill>
);

const Vineta: React.FC<{fuerza?: number}> = ({fuerza = 0.55}) => (
	<AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,${fuerza}) 100%)`}} />
);

/** Texto gordo con contorno negro y sombra dura, como las portadas de shorts. */
const Titular: React.FC<{
	texto: string;
	tam: number;
	color?: string;
	contorno?: number;
	rot?: number;
	estilo?: React.CSSProperties;
}> = ({texto, tam, color = '#fff', contorno, rot = 0, estilo}) => {
	const c = contorno ?? tam * 0.2;
	const base: React.CSSProperties = {
		fontFamily: TITULAR,
		fontWeight: 900,
		fontSize: tam,
		lineHeight: 0.98,
		letterSpacing: -tam * 0.02,
		textAlign: 'center',
		whiteSpace: 'pre',
	};
	return (
		<div style={{position: 'relative', transform: `rotate(${rot}deg)`, filter: `drop-shadow(0 ${tam * 0.09}px 0 rgba(0,0,0,0.55))`, ...estilo}}>
			<div style={{...base, color: TINTA, WebkitTextStroke: `${c}px ${TINTA}`}}>{texto}</div>
			<div style={{...base, color, position: 'absolute', inset: 0}}>{texto}</div>
		</div>
	);
};

/** Cinta de color detrás de una frase. */
const Cinta: React.FC<{color: string; rot?: number; children: React.ReactNode; padding?: string}> = ({color, rot = -3, children, padding = '10px 40px 22px'}) => (
	<div style={{background: color, border: `10px solid ${TINTA}`, borderRadius: 26, padding, transform: `rotate(${rot}deg)`, boxShadow: '0 14px 0 rgba(0,0,0,0.5)'}}>{children}</div>
);

const Estallido: React.FC<{tam: number; color: string; puntas?: number}> = ({tam, color, puntas = 18}) => {
	const pts = Array.from({length: puntas * 2})
		.map((_, i) => {
			const a = (i / (puntas * 2)) * Math.PI * 2;
			const r = i % 2 === 0 ? 100 : 66;
			return `${Math.cos(a) * r},${Math.sin(a) * r}`;
		})
		.join(' ');
	return (
		<svg viewBox="-110 -110 220 220" width={tam} height={tam} style={{overflow: 'visible'}}>
			<polygon points={pts} fill={color} stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
		</svg>
	);
};

const Gota: React.FC<{x: number; y: number; tam?: number}> = ({x, y, tam = 70}) => (
	<svg viewBox="0 0 60 80" width={tam} height={tam * 1.33} style={{position: 'absolute', left: x, top: y, overflow: 'visible'}}>
		<path d="M 30 4 Q 56 44 52 56 Q 46 76 30 76 Q 14 76 8 56 Q 4 44 30 4 Z" fill="#8fd3ff" stroke={TINTA} strokeWidth={6} />
		<ellipse cx={22} cy={52} rx={5} ry={9} fill="#fff" opacity={0.8} />
	</svg>
);


const Boton: React.FC<{texto: string; icono: string; color: string; rot: number}> = ({texto, icono, color, rot}) => (
	<div
		style={{
			display: 'flex',
			alignItems: 'center',
			gap: 18,
			background: color,
			border: `10px solid ${TINTA}`,
			borderRadius: 30,
			padding: '14px 34px 18px 24px',
			transform: `rotate(${rot}deg)`,
			boxShadow: '0 14px 0 rgba(0,0,0,0.55)',
		}}
	>
		<div style={{width: 92, height: 92, borderRadius: 18, background: '#fff', border: `8px solid ${TINTA}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: TITULAR, fontWeight: 900, fontSize: 76, color, lineHeight: 1}}>
			{icono}
		</div>
		<Titular texto={texto} tam={76} contorno={11} />
	</div>
);

const Escena: React.FC<{escala?: number; y?: number; children: React.ReactNode}> = ({escala = 1.1, y = 0, children}) => (
	<AbsoluteFill style={{transform: `translate(0px, ${y}px) scale(${escala})`}}>{children}</AbsoluteFill>
);

/* 1. Desmentir: "Napoleón NO era bajito" */
export const PortadaNoEraBajito: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<Escena escala={1.25} y={-130}>
			<EscMedidas />
			<EnMundo x={330} y={PISO} alto={altoParaCm(169)}>
				<Personaje diseno={NAPOLEON} ojos="entrecerrados" cejas="arrogante" boca="picara" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
			</EnMundo>
			<EnMundo x={770} y={PISO} alto={altoParaCm(165)}>
				<Personaje diseno={FRANCES} ojos="grandes" cejas="sorprendido" boca="o" semilla={3} />
			</EnMundo>
			<MarcaAltura cm={169} desde={-60} color="#22a84f" lado="izq" x1={170} x2={560} />
			<MarcaAltura cm={165} desde={-60} color="#1f6fd1" lado="der" x1={560} x2={910} />
		</Escena>
		<Vineta fuerza={0.45} />
		<div style={{position: 'absolute', top: 250, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22}}>
			<Titular texto={'NAPOLEÓN\nNO ERA BAJITO'} tam={124} rot={-2} />
			<Cinta color={ROJO} rot={3}>
				<Titular texto="¡MEDÍA 1,69!" tam={86} color={AMARILLO} contorno={12} />
			</Cinta>
		</div>
	</AbsoluteFill>
);

/* 2. El primer meme de la historia */
export const PortadaMeme: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<AbsoluteFill style={{background: 'linear-gradient(135deg,#7b3fe4,#ff5f8f)'}} />
		<Escena escala={0.94} y={300}>
			<EscCelular reacciones={1} />
			<div style={{position: 'absolute', left: MEME.x, top: MEME.y, width: MEME.w, height: MEME.h, overflow: 'hidden', filter: 'grayscale(0.25) sepia(0.35) contrast(1.15)'}}>
				<div style={{position: 'absolute', top: 30, left: 0, right: 0, textAlign: 'center', fontFamily: TITULAR, fontWeight: 900, fontSize: 64, color: '#ffffff', WebkitTextStroke: `10px ${TINTA}`, paintOrder: 'stroke'}}>LITTLE BONEY</div>
				<EnMundo x={330} y={720} alto={480} rot={-8}>
					<Personaje diseno={NAPOLEON} ojos="cerrados" cejas="enojado" boca="grito" brazoIzq={160} brazoDer={140} />
				</EnMundo>
				<Lagrimas x={320} y={350} desde={-12} />
			</div>
			<EnMundo x={930} y={2080} alto={1050} rot={-10}>
				<Personaje diseno={NAPOLEON} ojos="entrecerrados" cejas="enojado" boca="mueca" />
			</EnMundo>
		</Escena>
		<div style={{position: 'absolute', top: 255, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}>
			<Titular texto="EL PRIMER MEME" tam={112} rot={-2} />
			<Cinta color={AMARILLO} rot={2} padding="4px 36px 14px">
				<Titular texto="DE LA HISTORIA" tam={84} color={ROJO} contorno={10} />
			</Cinta>
		</div>
	</AbsoluteFill>
);

/* 3. Comparación: la caricatura vs la realidad */
export const PortadaVersus: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<AbsoluteFill style={{clipPath: 'polygon(0 0, 58% 0, 42% 100%, 0 100%)'}}>
			<Escena escala={1.25} y={60}>
				<EscEstudio />
			</Escena>
			<HojaCaricatura x={270} y={1180} ancho={500} alto={700} rot={-4}>
				<EnMundo x={220} y={600} alto={420} rot={-6}>
					<Personaje diseno={NAPOLEON} ojos="cerrados" cejas="enojado" boca="grito" brazoIzq={160} brazoDer={140} />
				</EnMundo>
				<Lagrimas x={210} y={300} desde={-12} />
			</HojaCaricatura>
		</AbsoluteFill>
		<AbsoluteFill style={{clipPath: 'polygon(58% 0, 100% 0, 100% 100%, 42% 100%)'}}>
			<Escena escala={1.2}>
				<EscMedidas />
			</Escena>
			<Rayos x={800} y={1150} color="#ffe9a0" opacidad={0.2} />
			<EnMundo x={790} y={2120} alto={1250}>
				<Personaje diseno={NAPOLEON} ojos="entrecerrados" cejas="arrogante" boca="picara" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
			</EnMundo>
		</AbsoluteFill>
		<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0}}>
			<polyline points="626,0 540,700 600,760 520,1300 580,1360 454,1920" fill="none" stroke={TINTA} strokeWidth={46} strokeLinejoin="round" />
			<polyline points="626,0 540,700 600,760 520,1300 580,1360 454,1920" fill="none" stroke={AMARILLO} strokeWidth={22} strokeLinejoin="round" />
		</svg>
		<Vineta fuerza={0.4} />
		<div style={{position: 'absolute', top: 250, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6}}>
			<Titular texto="LO QUE TE CONTARON" tam={84} rot={-2} />
			<Titular texto="vs LA VERDAD" tam={104} color={AMARILLO} rot={-2} />
		</div>
		<div style={{position: 'absolute', left: 60, top: 640}}>
			<Cinta color={ROJO} rot={-6} padding="4px 26px 12px">
				<Titular texto="1,57 m" tam={76} color="#ffffff" contorno={10} />
			</Cinta>
		</div>
		<div style={{position: 'absolute', right: 60, top: 640}}>
			<Cinta color="#22a84f" rot={5} padding="4px 26px 12px">
				<Titular texto="1,69 m" tam={76} color="#ffffff" contorno={10} />
			</Cinta>
		</div>
	</AbsoluteFill>
);
