import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {ATLANTE, Personaje, PLATON} from './componentes/Personaje';
import {EnMundo} from './componentes/Toma';
import {Icono, Rayos} from './componentes/Utileria';
import {EscCanales, EscCiudadAerea, EscTsunami} from './escenarios/Escenarios';
import {SERIF, TITULAR} from './fuentes';

/* Portadas del short de la Atlántida (1080x1920). Texto y caras dentro de y=260..1650. */

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

/** Escenario dibujado por código, escalado como fondo de portada. */
const Escena: React.FC<{escala?: number; y?: number; children: React.ReactNode}> = ({escala = 1.1, y = 0, children}) => (
	<AbsoluteFill style={{transform: `translate(0px, ${y}px) scale(${escala})`}}>{children}</AbsoluteFill>
);

/** Palabra en oro, como el título del video. */
const Oro: React.FC<{texto: string; tam: number}> = ({texto, tam}) => (
	<div
		style={{
			fontFamily: SERIF,
			fontWeight: 900,
			fontSize: tam,
			lineHeight: 1,
			background: 'linear-gradient(180deg,#fff6c8 0%,#f2c14e 45%,#b8761a 100%)',
			WebkitBackgroundClip: 'text',
			color: 'transparent',
			WebkitTextStroke: `5px ${TINTA}`,
			filter: 'drop-shadow(0 0 26px rgba(255,210,100,0.9)) drop-shadow(0 10px 0 rgba(0,0,0,0.5))',
			transform: 'rotate(-2deg)',
		}}
	>
		{texto}
	</div>
);

/* 1. Primera persona: "Yo viví en la Atlántida" */
export const PortadaYoVivi: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<Escena escala={1.25} y={140}>
			<EscCanales templo={1} />
		</Escena>
		<Rayos x={540} y={760} color="#ffe9a0" opacidad={0.3} />
		<Vineta fuerza={0.5} />
		<EnMundo x={560} y={2230} alto={1550}>
			<Personaje diseno={ATLANTE} ojos="entrecerrados" cejas="arrogante" boca="picara" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnMundo>
		<div style={{position: 'absolute', top: 250, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14}}>
			<Titular texto="YO VIVÍ EN" tam={130} rot={-2} />
			<Oro texto="ATLÁNTIDA" tam={150} />
		</div>
	</AbsoluteFill>
);

/* 2. Catástrofe: desapareció en una noche */
export const PortadaNoche: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<Escena escala={1.1}>
			<EscTsunami subida={0.62} />
		</Escena>
		<Vineta fuerza={0.55} />
		<EnMundo x={560} y={2150} alto={1250} rot={-4}>
			<Personaje diseno={ATLANTE} ojos="grandes" cejas="sorprendido" boca="grito" brazoIzq={150} brazoDer={150} />
		</EnMundo>
		<div style={{position: 'absolute', top: 250, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24}}>
			<Titular texto={'UNA CIUDAD\nENTERA'} tam={128} rot={-2} />
			<Cinta color={ROJO} rot={3}>
				<Titular texto="¡DESAPARECIÓ EN 1 NOCHE!" tam={62} color={AMARILLO} contorno={10} />
			</Cinta>
		</div>
	</AbsoluteFill>
);

/* 3. Quiz: ¿existió la Atlántida? */
export const PortadaQuiz: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<Escena escala={1.2} y={120}>
			<EscCiudadAerea revelar={1} />
		</Escena>
		<Vineta fuerza={0.55} />
		<EnMundo x={790} y={2150} alto={1250}>
			<Personaje diseno={PLATON} ojos="entrecerrados" cejas="arrogante" boca="picara" />
		</EnMundo>
		<EnMundo x={250} y={2150} alto={1150}>
			<Personaje diseno={ATLANTE} ojos="grandes" cejas="preocupado" boca="mueca" brazoIzq={60} codoIzq={-70} brazoDer={60} codoDer={-70} />
		</EnMundo>
		<div style={{position: 'absolute', top: 250, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12}}>
			<Titular texto="¿EXISTIÓ" tam={136} rot={-2} />
			<Oro texto="ATLÁNTIDA?" tam={130} />
		</div>
		<div style={{position: 'absolute', left: 120, top: 760}}>
			<Icono tipo="interrogacion" x={0} y={0} desde={-60} tam={170} rot={-12} />
		</div>
		<div style={{position: 'absolute', top: 1470, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 26}}>
			<Boton texto="VERDAD" icono="✓" color="#22a84f" rot={-4} />
			<Boton texto="MITO" icono="✗" color={ROJO} rot={3} />
		</div>
	</AbsoluteFill>
);
