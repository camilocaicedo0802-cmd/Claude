import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {Personaje, VESNA} from './componentes/Personaje';
import {EnMundo} from './componentes/Toma';
import {Icono, Rayos} from './componentes/Utileria';
import {Carrito} from './componentes/Vuelo';
import {TITULAR} from './fuentes';

/* Portadas del short de Vesna (1080x1920). Texto y caras dentro de y=260..1650 (zona segura). */

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

const Rafagas: React.FC = () => (
	<AbsoluteFill>
		{Array.from({length: 18}).map((_, i) => (
			<div key={i} style={{position: 'absolute', left: (i * 61) % 1080, top: (i * 377) % 1700, width: 10, height: 260 + (i % 4) * 90, borderRadius: 6, background: 'rgba(255,255,255,0.6)'}} />
		))}
	</AbsoluteFill>
);

const ParacaidasNo: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => (
	<svg viewBox="0 0 200 200" width={tam} height={tam} style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, overflow: 'visible'}}>
		<path d="M 20 90 Q 100 -10 180 90 Q 160 76 140 90 Q 120 76 100 90 Q 80 76 60 90 Q 40 76 20 90 Z" fill="#ff7a1a" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
		{[20, 60, 100, 140, 180].map((x0) => (
			<line key={x0} x1={x0} y1={90} x2={100} y2={160} stroke={TINTA} strokeWidth={4} />
		))}
		<circle cx={100} cy={100} r={92} fill="none" stroke={ROJO} strokeWidth={18} />
		<line x1={36} y1={164} x2={164} y2={36} stroke={ROJO} strokeWidth={18} strokeLinecap="round" />
	</svg>
);

/* 1. Impacto: cayó 10.000 m sin paracaídas */
export const PortadaCaida: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<Fondo src="cielo_alto.jpg" escala={1.25} y={120} filtro="saturate(1.2)" />
		<Rafagas />
		<Vineta fuerza={0.5} />
		<EnMundo x={560} y={2250} alto={1600} rot={-8}>
			<Personaje diseno={VESNA} ojos="grandes" cejas="sorprendido" boca="grito" brazoIzq={150} brazoDer={150} sombra={false} />
		</EnMundo>
		<ParacaidasNo x={880} y={1150} tam={250} />
		<div style={{position: 'absolute', top: 250, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 26}}>
			<Titular texto={'CAYÓ'} tam={150} rot={-2} />
			<Titular texto={'10.000 METROS'} tam={118} color={AMARILLO} rot={-2} />
			<Cinta color={ROJO} rot={3}>
				<Titular texto="¡SIN PARACAÍDAS!" tam={80} color="#ffffff" contorno={12} />
			</Cinta>
		</div>
	</AbsoluteFill>
);

/* 2. Curiosidad: ¿un carrito le salvó la vida? */
export const PortadaCarrito: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<Fondo src="cola_interior.jpg" escala={1.2} y={80} filtro="saturate(1.2) brightness(0.9)" />
		<Rayos x={760} y={1300} color="#fff2a8" opacidad={0.3} />
		<Vineta fuerza={0.55} />
		<EnMundo x={300} y={2150} alto={1350} rot={-3}>
			<Personaje diseno={VESNA} acc={{vendas: true}} ojos="grandes" cejas="sorprendido" boca="o" brazoDer={95} codoDer={-10} />
		</EnMundo>
		<Carrito x={790} y={1640} ancho={500} ojos="guino" boca="grande" medalla />
		<div style={{position: 'absolute', top: 250, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}>
			<Titular texto={'¿UN CARRITO'} tam={132} rot={-2} />
			<Titular texto={'LE SALVÓ\nLA VIDA?'} tam={132} color={AMARILLO} rot={-2} />
		</div>
		<div style={{position: 'absolute', left: 700, top: 960}}>
			<Icono tipo="interrogacion" x={0} y={0} desde={-60} tam={170} rot={12} />
		</div>
	</AbsoluteFill>
);

/* 3. Quiz: ¿verdad o falso? */
export const PortadaQuiz: React.FC = () => (
	<AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
		<Fondo src="bosque_amanecer.jpg" escala={1.15} y={80} filtro="saturate(1.2)" />
		<Rayos x={540} y={1100} color="#fff2c4" opacidad={0.3} />
		<Vineta fuerza={0.5} />
		<EnMundo x={540} y={2200} alto={1500}>
			<Personaje diseno={VESNA} acc={{vendas: true}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={150} brazoDer={150} />
		</EnMundo>
		<div style={{position: 'absolute', top: 240, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10}}>
			<Titular texto="¿SOBREVIVIÓ" tam={128} rot={-2} />
			<Titular texto={'A UNA CAÍDA\nDE 10 KM?'} tam={118} color={AMARILLO} rot={-2} />
		</div>
		<div style={{position: 'absolute', top: 1470, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 26}}>
			<Boton texto="VERDAD" icono="✓" color="#22a84f" rot={-4} />
			<Boton texto="FALSO" icono="✗" color={ROJO} rot={3} />
		</div>
	</AbsoluteFill>
);
