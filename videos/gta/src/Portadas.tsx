import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Atril, AutoA, Barrido, Bicho, CajaJuego, ChoqueSVG, MapaJuego, Monitor, pantallaDe} from './componentes/Gamer';
import {Actor, Muneco, Pose, alcanzar, manosFrente} from './componentes/Muneco';
import {Bocadillo} from './componentes/Utileria';
import {ROPA_DISTRIBUIDOR, ROPA_POLITICO, ROPA_PROGRAMADOR} from './componentes/Vestuario';
import {EscOficina90, EscParlamento} from './escenarios/Escenarios';
import {CONDENSADA} from './fuentes';

/* Portadas del short «GTA existe por un bug» (1080x1920). Textos y caras dentro de y = 260..1650.
   Sin logo ni arte oficial: rotulación y dibujos propios. */

const TINTA = '#111114';
const AMARILLO = '#ffc21a';
const ROJO = '#e3262e';
const VERDE = '#1f9d48';

const brazo = (lado: -1 | 1, r: {a: number; c: number; k?: number}): Partial<Pose> => (lado < 0 ? {bi: r.a, ci: r.c, ai: r.k ?? 1} : {bd: r.a, cd: r.c, ad: r.k ?? 1});

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

const quieto = {parpadea: false, respira: false} as const;

const Estrellas: React.FC<{y: number; tam?: number}> = ({y, tam = 96}) => (
	<div style={{position: 'absolute', left: 0, right: 0, top: y, display: 'flex', justifyContent: 'center', gap: tam * 0.12}}>
		{Array.from({length: 5}).map((_, i) => (
			<svg key={i} width={tam} height={tam} viewBox="-50 -50 100 100" style={{filter: 'drop-shadow(0 6px 0 rgba(0,0,0,0.5))'}}>
				<polygon points="0,-44 12,-14 44,-14 18,6 28,40 0,20 -28,40 -18,6 -44,-14 -12,-14" fill="#ffd23f" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
			</svg>
		))}
	</div>
);

/* ---------- 1. GTA EXISTE POR UN BUG · ¡ES REAL! ---------- */

export const PortadaBug: React.FC = () => {
	const ancho = 900;
	const {w, h} = pantallaDe(ancho);
	const autos: AutoA[] = [
		{x: 40, y: 1500, rot: 0, color: '#e3262e', jugador: true},
		{x: -30, y: 1720, rot: 35, policia: true},
		{x: 90, y: 1300, rot: 200, policia: true},
	];
	return (
		<AbsoluteFill style={{background: '#6f8796'}}>
			<EscOficina90 />
			<Monitor x={540} y={1010} ancho={ancho}>
				<MapaJuego cx={20} cy={1500} zoom={0.55} ancho={w} alto={h} autos={autos} />
			</Monitor>
			<div style={{position: 'absolute', left: -40, right: -40, top: 1420, height: 54, background: '#9a6a3a', border: `8px solid ${TINTA}`, borderRadius: 10}} />
			<div style={{position: 'absolute', left: 30, right: 30, top: 1474, bottom: 0, background: '#7a4a24', borderLeft: `8px solid ${TINTA}`, borderRight: `8px solid ${TINTA}`}} />
			<Bicho x={470} y={1000} tam={400} rot={-8} camina={false} cara="picaro" />
			<Actor x={900} y={2170} alto={1220}>
				<Muneco ropa={ROPA_PROGRAMADOR} pose={{...manosFrente([96, 250], [304, 250]), mi: 'abierta', md: 'abierta', wi: -20, wd: -20}} ojos="grandes" cejas="sorprendido" boca="o" {...quieto} />
			</Actor>
			<Arriba>
				<Titular texto="GTA EXISTE" tam={150} />
				<Titular texto="POR UN BUG" tam={196} color={AMARILLO} />
			</Arriba>
			<Abajo top={1470} right={360}>
				<Sello texto="¡ES REAL!" color={VERDE} tam={120} rot={-7} />
			</Abajo>
		</AbsoluteFill>
	);
};

/* ---------- 2. LA POLICÍA SE VOLVIÓ LOCA ---------- */

export const PortadaPolicia: React.FC = () => {
	const autos: AutoA[] = [
		{x: 40, y: 1820, rot: 0, policia: true},
		{x: 20, y: 1440, rot: 200, policia: true},
		{x: -70, y: 1600, rot: 14, policia: true},
		{x: 70, y: 1630, rot: 22, color: '#e3262e', jugador: true},
	];
	return (
		<AbsoluteFill style={{background: '#5d6470'}}>
			<MapaJuego cx={30} cy={1580} zoom={1.4} ancho={1080} alto={1920} autos={autos}>
				<ChoqueSVG x={30} y={1520} desde={-6} tam={1.2} />
				<ChoqueSVG x={60} y={1730} desde={-5} tam={0.9} />
			</MapaJuego>
			<Barrido fuerza={0.6} />
			<Arriba>
				<Titular texto="LA POLICÍA" tam={150} />
				<Titular texto="SE VOLVIÓ LOCA" tam={150} color={AMARILLO} />
			</Arriba>
			<Estrellas y={575} tam={100} />
			<Abajo top={1450}>
				<Sello texto="Y ASÍ NACIÓ GTA" color={ROJO} tam={108} rot={-6} />
			</Abajo>
		</AbsoluteFill>
	);
};

/* ---------- 3. LA POLÉMICA ERA FALSA ---------- */

export const PortadaPolemica: React.FC = () => (
	<AbsoluteFill style={{background: '#8c96a6'}}>
		<EscParlamento />
		<CajaJuego x={820} y={880} ancho={300} rot={8} prohibido={1} />
		<Actor x={320} y={2000} alto={1150}>
			<Muneco ropa={ROPA_POLITICO} pose={{...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 300, 130)), md: 'puno'}} ojos="grandes" cejas="enojado" boca="grito" {...quieto} />
		</Actor>
		<Atril x={320} y={2000} ancho={400} alto={500} />
		<Actor x={860} y={2170} alto={1160}>
			<Muneco ropa={ROPA_DISTRIBUIDOR} pose={{...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 236, 392)), md: 'pulgar'}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" {...quieto} />
		</Actor>
		<Bocadillo x={300} y={700} texto="¡PROHÍBANLO!" desde={-30} cola="izq" ancho={500} tam={62} />
		<Arriba>
			<Titular texto="LA POLÉMICA" tam={150} />
			<Titular texto="ERA FALSA" tam={196} color={ROJO} />
		</Arriba>
		<Abajo top={1480}>
			<Sello texto="¡TODO FUE MARKETING!" color={VERDE} tam={92} rot={-5} />
		</Abajo>
	</AbsoluteFill>
);
