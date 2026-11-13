import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {Moscas} from './componentes/Efectos';
import {ESPIA_MUERTO, HITLER, Personaje} from './componentes/Personaje';
import {EnMundo} from './componentes/Toma';
import {Documento, Icono, Rayos} from './componentes/Utileria';
import {TITULAR} from './fuentes';

/*
 * Portadas (miniaturas) del short, 1080x1920.
 * Zona segura: el texto y las caras importantes van entre y=260 y y=1650, que es lo que se ve
 * en la cuadrícula de perfil de Instagram (recorte 3:4) y en la vista previa de Shorts/TikTok.
 */

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

/* ------------------------------------------------------------------ */
/* 1. La paradoja: "Engañó a Hitler... ¡estando muerto!"               */
/* ------------------------------------------------------------------ */
export const PortadaParadoja: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<Fondo src="callejon.jpg" escala={1.18} y={60} filtro="saturate(1.25) brightness(0.9)" />
		<Rayos x={640} y={1080} color="#ffb347" opacidad={0.28} />
		<Vineta fuerza={0.6} />
		{/* espía protagonista */}
		<EnMundo x={640} y={2200} alto={1500}>
			<Personaje diseno={ESPIA_MUERTO} acc={{gafas: true, medalla: true}} ojos="x" cejas="ninguna" boca="picara" respira={false} parpadea={false} cabeza={-6} />
		</EnMundo>
		<Moscas x={640} y={1080} radio={330} n={3} />
		{/* Hitler asomado, en shock */}
		<EnMundo x={170} y={2110} alto={1000} rot={8}>
			<Personaje diseno={HITLER} ojos="grandes" cejas="sorprendido" boca="o" brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnMundo>
		<Gota x={290} y={1250} />
		<div style={{position: 'absolute', left: 345, top: 1110}}>
			<Icono tipo="exclamacion" x={0} y={0} desde={-60} tam={200} rot={14} />
		</div>
		{/* titular */}
		<div style={{position: 'absolute', top: 250, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 34}}>
			<Titular texto={'ENGAÑÓ\nA HITLER'} tam={168} rot={-2} />
			<Cinta color={ROJO} rot={3}>
				<Titular texto="¡ESTANDO MUERTO!" tam={84} color={AMARILLO} contorno={13} />
			</Cinta>
		</div>
	</AbsoluteFill>
);

/* ------------------------------------------------------------------ */
/* 2. El versus: Hitler contra un cadáver                              */
/* ------------------------------------------------------------------ */
export const PortadaVersus: React.FC = () => {
	const corte = 'polygon(0 0, 62% 0, 38% 100%, 0 100%)';
	const corteDer = 'polygon(62% 0, 100% 0, 100% 100%, 38% 100%)';
	return (
		<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
			<AbsoluteFill style={{clipPath: corte}}>
				<Fondo src="bunker.jpg" escala={1.2} filtro="saturate(1.2)" />
				<AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(200,30,30,0.15), rgba(160,0,0,0.45))', mixBlendMode: 'multiply'}} />
				<EnMundo x={290} y={2080} alto={1320}>
					<Personaje diseno={HITLER} ojos="normal" cejas="enojado" boca="dientes" cabeza={6} brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
				</EnMundo>
			</AbsoluteFill>
			<AbsoluteFill style={{clipPath: corteDer}}>
				<Fondo src="morgue.jpg" escala={1.2} filtro="saturate(1.2)" />
				<AbsoluteFill style={{background: 'rgba(40,200,190,0.25)', mixBlendMode: 'soft-light'}} />
				<EnMundo x={800} y={2080} alto={1320}>
					<Personaje diseno={ESPIA_MUERTO} ojos="x" cejas="ninguna" boca="lengua" respira={false} parpadea={false} cabeza={-10} />
				</EnMundo>
				<Moscas x={800} y={1110} radio={260} n={3} />
			</AbsoluteFill>
			{/* rayo divisor */}
			<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0}}>
				<polyline points="670,0 560,620 640,700 500,1300 590,1370 410,1920" fill="none" stroke={TINTA} strokeWidth={46} strokeLinejoin="round" />
				<polyline points="670,0 560,620 640,700 500,1300 590,1370 410,1920" fill="none" stroke={AMARILLO} strokeWidth={22} strokeLinejoin="round" />
			</svg>
			<Vineta fuerza={0.45} />
			{/* VS central */}
			{/* titular arriba: HITLER / VS / UN CADÁVER, las caras quedan libres debajo */}
			<div style={{position: 'absolute', top: 240, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
				<Titular texto="HITLER" tam={150} rot={-3} />
			</div>
			<div style={{position: 'absolute', left: 540 - 175, top: 555 - 175, width: 350, height: 350, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
				<div style={{position: 'absolute', inset: 0}}>
					<Estallido tam={350} color={ROJO} />
				</div>
				<Titular texto="VS" tam={170} color={AMARILLO} rot={-8} contorno={28} />
			</div>
			<div style={{position: 'absolute', top: 700, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
				<Titular texto="UN CADÁVER" tam={128} color={AMARILLO} rot={-3} />
			</div>
			<div style={{position: 'absolute', top: 1500, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
				<Cinta color="#ffffff" rot={2} padding="6px 40px 16px">
					<Titular texto="¿QUIÉN GANÓ?" tam={84} color={ROJO} contorno={10} />
				</Cinta>
			</div>
		</AbsoluteFill>
	);
};

/* ------------------------------------------------------------------ */
/* 3. El quiz: ¿verdad o falso? (invita a comentar)                    */
/* ------------------------------------------------------------------ */
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

export const PortadaQuiz: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<Fondo src="bunker.jpg" escala={1.15} y={120} filtro="saturate(1.25) brightness(0.95)" />
		<Vineta fuerza={0.6} />
		{/* Hitler leyendo los documentos, sudando */}
		<EnMundo x={470} y={2150} alto={1450}>
			<Personaje diseno={HITLER} ojos="grandes" cejas="preocupado" boca="mueca" cabeza={-6} brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
		</EnMundo>
		<Gota x={690} y={980} tam={80} />
		<Gota x={225} y={1030} tam={60} />
		<Documento x={470} y={1790} ancho={400} desde={-60} rot={-6} />
		{/* el espía muerto asomándose con guiño */}
		<EnMundo x={1010} y={1720} alto={980} rot={-14}>
			<Personaje diseno={ESPIA_MUERTO} ojos="guinoX" cejas="ninguna" boca="picara" respira={false} parpadea={false} />
		</EnMundo>
		<div style={{position: 'absolute', left: 105, top: 860}}>
			<Icono tipo="interrogacion" x={0} y={0} desde={-60} tam={200} rot={-14} />
		</div>
		{/* titular */}
		<div style={{position: 'absolute', top: 240, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}>
			<Titular texto="¿UN MUERTO" tam={138} rot={-2} />
			<Titular texto={'ENGAÑÓ\nA HITLER?'} tam={138} color={AMARILLO} rot={-2} />
		</div>
		{/* opciones tipo quiz */}
		<div style={{position: 'absolute', top: 1470, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 26}}>
			<Boton texto="VERDAD" icono="✓" color="#22a84f" rot={-4} />
			<Boton texto="FALSO" icono="✗" color={ROJO} rot={3} />
		</div>
	</AbsoluteFill>
);
