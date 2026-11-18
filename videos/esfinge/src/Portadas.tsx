import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Esfinge, Martillo, narizEn} from './componentes/Egipto';
import {Actor, Muneco, POSES, Pose, ROPA_NAPOLEON, alcanzar, manosFrente} from './componentes/Muneco';
import {Papel} from './componentes/Objetos';
import {Lupa} from './componentes/Utileria';
import {ROPA_FANATICO} from './componentes/Vestuario';
import {EscDesierto} from './escenarios/Escenarios';
import {CONDENSADA, SERIF} from './fuentes';

/* Portadas del short de la nariz de la Esfinge (1080x1920). Textos y caras dentro de y = 260..1650. */

const TINTA = '#111114';
const AMARILLO = '#ffc21a';
const ROJO = '#e3262e';

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

/* ---------- 1. ¿NAPOLEÓN LE VOLÓ LA NARIZ? ¡ES UN MITO! ---------- */

const ESF1 = {x: 650, y: 1500, ancho: 1100};

export const PortadaMito: React.FC = () => {
	const [nx, ny] = narizEn(ESF1.x, ESF1.y, ESF1.ancho);
	return (
		<AbsoluteFill style={{background: '#4fa3e0'}}>
			<EscDesierto />
			<Esfinge {...ESF1} nariz={0} cara="triste" mira={-0.7} />
			<svg viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
				<circle cx={nx} cy={ny} r={92} fill="none" stroke={TINTA} strokeWidth={22} />
				<circle cx={nx} cy={ny} r={92} fill="none" stroke={ROJO} strokeWidth={12} strokeDasharray="30 16" />
			</svg>
			<Actor x={210} y={2240} alto={1300}>
				<Muneco ropa={ROPA_NAPOLEON} pose={{...manosFrente([186, 480]), ...brazo(1, alcanzar(1, 372, 330)), md: 'abierta', wd: -30}} ojos="mirandoLado" cejas="preocupado" boca="o" {...quieto} />
			</Actor>
			<Arriba>
				<Titular texto="¿NAPOLEÓN LE VOLÓ" tam={118} />
				<Titular texto="LA NARIZ?" tam={214} color={AMARILLO} />
			</Arriba>
			<Abajo top={1450} left={340}>
				<Sello texto="¡ES UN MITO!" color={ROJO} tam={124} rot={-7} />
			</Abajo>
		</AbsoluteFill>
	);
};

/* ---------- 2. 1737: ¡YA ESTABA CHATA! ---------- */

export const PortadaDibujo: React.FC = () => (
	<AbsoluteFill style={{background: '#4fa3e0'}}>
		<EscDesierto piramides={false} />
		<Papel x={520} y={1000} ancho={780} alto={760} rot={-3}>
			<Esfinge x={364} y={600} ancho={680} nariz={0} cara="normal" />
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 18, textAlign: 'center', fontFamily: SERIF, fontWeight: 700, fontStyle: 'italic', fontSize: 40, color: '#4a3018'}}>F. L. Norden · 1737</div>
		</Papel>
		<Lupa x={560} y={930} tam={340} desde={-30} radio={0} />
		<Actor x={880} y={2170} alto={1080}>
			<Muneco ropa={ROPA_NAPOLEON} pose={POSES.encogeHombros} ojos="normal" cejas="preocupado" boca="mueca" {...quieto} />
		</Actor>
		<Arriba>
			<Titular texto="¡YA ESTABA" tam={128} />
			<Titular texto="CHATA!" tam={220} color={AMARILLO} />
		</Arriba>
		<Abajo top={1420} right={440}>
			<Sello texto="EN 1737" color={ROJO} tam={104} rot={-6} />
		</Abajo>
		<Abajo top={1580} right={440}>
			<div style={{fontFamily: CONDENSADA, fontSize: 60, textAlign: 'center', lineHeight: 1.05, whiteSpace: 'pre', color: '#fff', WebkitTextStroke: `10px ${TINTA}`, paintOrder: 'stroke', textShadow: '0 5px 0 rgba(0,0,0,0.5)'}}>32 AÑOS ANTES{'\n'}DE NAPOLEÓN</div>
		</Abajo>
	</AbsoluteFill>
);

/* ---------- 3. EL VERDADERO CULPABLE ---------- */

export const PortadaCulpable: React.FC = () => (
	<AbsoluteFill style={{background: '#0e1430'}}>
		<EscDesierto tono="noche" />
		<Esfinge x={540} y={1360} ancho={920} nariz={0} cara="enojo" mira={0.6} />
		<div style={{position: 'absolute', left: 520, top: 900, width: 600, height: 1100, background: 'radial-gradient(ellipse at 50% 60%, rgba(255,240,190,0.5), rgba(255,240,190,0) 70%)'}} />
		<div style={{position: 'absolute', inset: 0, filter: 'brightness(0)'}}>
			<Actor x={820} y={2150} alto={1300}>
				<Muneco ropa={ROPA_FANATICO} pose={{...manosFrente([-10, 200], [270, 480]), mi: 'agarra', md: 'agarra'}} objIzq={<Martillo rot={20} />} ojos="normal" boca="seria" {...quieto} />
			</Actor>
		</div>
		<div style={{position: 'absolute', left: 740, top: 1040, fontFamily: CONDENSADA, fontSize: 260, color: AMARILLO, WebkitTextStroke: `14px ${TINTA}`, paintOrder: 'stroke', lineHeight: 1}}>?</div>
		<Actor x={250} y={2220} alto={1300}>
			<Muneco ropa={ROPA_NAPOLEON} pose={{...manosFrente([60, 330], [340, 330]), mi: 'abierta', md: 'abierta', wi: 20, wd: 20}} ojos="grandes" cejas="preocupado" boca="abierta" {...quieto} />
		</Actor>
		<div style={{position: 'absolute', left: 60, top: 760, padding: '14px 30px 18px', background: '#fff', border: `9px solid ${TINTA}`, borderRadius: 40, fontFamily: CONDENSADA, fontSize: 74, color: TINTA, boxShadow: '0 10px 0 rgba(0,0,0,0.4)'}}>¡NO FUI YO!</div>
		<Arriba>
			<Titular texto="EL VERDADERO" tam={130} />
			<Titular texto="CULPABLE" tam={230} color={ROJO} />
		</Arriba>
		<Abajo top={1480} left={420}>
			<Sello texto="AÑO 1378" color={ROJO} tam={96} rot={6} />
		</Abajo>
	</AbsoluteFill>
);
