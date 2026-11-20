import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn} from './componentes/Muneco';
import {Contrato, Raton} from './componentes/Recurrentes';
import {BANQUERO, FUNCIONARIO, HITLER_CANCILLER, HITLER_TRAJE, MINISTRO, PAPEN, SENOR_3} from './componentes/Vestuario';
import {EscOficinaBerlin, EscRincon} from './escenarios/Epoca';
import {CONDENSADA} from './fuentes';
import {brazo} from './escenas/compartidas';
import {EscSalonGenios} from './escenas/utileria_c67';
import {Calendario60, Cronometro, ParlamentoMini} from './escenas/utileria_c89';

/* Portadas del short (1080x1920). Textos y caras dentro de y = 260..1650. Sin esvásticas, banderas ni insignias. */

const TINTA = '#111114';
const AMARILLO = '#ffc21a';
const ROJO = '#d6262e';

const Titular: React.FC<{texto: string; tam: number; color?: string; rot?: number}> = ({texto, tam, color = '#fff', rot = 0}) => {
	const base: React.CSSProperties = {fontFamily: CONDENSADA, fontSize: tam, lineHeight: 0.95, letterSpacing: tam * 0.01, textAlign: 'center', whiteSpace: 'pre', textTransform: 'uppercase'};
	return (
		<div style={{position: 'relative', transform: `rotate(${rot}deg)`, filter: `drop-shadow(0 ${tam * 0.07}px 0 rgba(0,0,0,0.6))`}}>
			<div style={{...base, color: TINTA, WebkitTextStroke: `${tam * 0.17}px ${TINTA}`}}>{texto}</div>
			<div style={{...base, color, position: 'absolute', inset: 0}}>{texto}</div>
		</div>
	);
};

const SelloGrande: React.FC<{texto: string; color: string; tam: number; rot?: number}> = ({texto, color, tam, rot = -10}) => (
	<div style={{transform: `rotate(${rot}deg)`, border: `${tam * 0.09}px solid ${color}`, borderRadius: tam * 0.16, padding: `${tam * 0.14}px ${tam * 0.24}px ${tam * 0.06}px`, background: 'rgba(255,255,255,0.95)', boxShadow: '0 14px 0 rgba(0,0,0,0.45)'}}>
		<div style={{fontFamily: CONDENSADA, fontSize: tam, lineHeight: 1, color, letterSpacing: tam * 0.03, whiteSpace: 'nowrap'}}>{texto}</div>
	</div>
);

const Arriba: React.FC<{children: React.ReactNode; top?: number}> = ({children, top = 270}) => <div style={{position: 'absolute', top, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>{children}</div>;
const En: React.FC<{children: React.ReactNode; top: number; left?: number; right?: number}> = ({children, top, left = 0, right = 0}) => <div style={{position: 'absolute', left, right, top, display: 'flex', justifyContent: 'center'}}>{children}</div>;

/** el mundo 16:9 del video recompuesto en vertical (punto (cx, cy) al centro, escala k) */
const Vert: React.FC<{cx: number; cy: number; k: number; children: React.ReactNode}> = ({cx, cy, k, children}) => (
	<div style={{position: 'absolute', left: 540 - cx * k, top: 960 - cy * k, width: 1920, height: 1080, transform: `scale(${k})`, transformOrigin: '0 0'}}>{children}</div>
);

const Vineta: React.FC = () => <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 55%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.55) 100%)'}} />;

/* ---------- 1. LO CONTRATÓ: Papen con el contrato y el ratón del rincón ---------- */

export const PortadaContrato: React.FC = () => (
	<AbsoluteFill style={{background: '#232a33'}}>
		<Vert cx={1000} cy={420} k={1.95}>
			<EscOficinaBerlin />
		</Vert>
		<Actor x={560} y={2330} alto={1650}>
			<Muneco ropa={PAPEN} pose={{...brazo(-1, alcanzar(-1, 40, 400)), mi: 'abierta', ...manosEn(undefined, [212, 420], {}, true), md: 'oculta', cabeza: -6}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
		</Actor>
		<Contrato x={330} y={1360} ancho={420} rot={-10} firma={1} />
		<Raton x={830} y={1620} tam={180} chilla voltear />
		<Vineta />
		<Arriba>
			<Titular texto={'LE DIERON\nEL PODER'} tam={150} color={AMARILLO} rot={-2} />
			<Titular texto={'“VA A CHILLAR\nEN UN RINCÓN”'} tam={88} rot={-2} />
		</Arriba>
	</AbsoluteFill>
);

/* ---------- 2. «LO TENEMOS RODEADO»: la jaula de ministros ---------- */

export const PortadaRodeado: React.FC = () => {
	const RONDA = [
		{r: MINISTRO, x: 170, inc: 14},
		{r: SENOR_3, x: 350, inc: 7},
		{r: BANQUERO, x: 730, inc: -7},
		{r: FUNCIONARIO, x: 910, inc: -14},
	];
	return (
		<AbsoluteFill style={{background: '#1e120a'}}>
			<Vert cx={700} cy={500} k={1.9}>
				<EscSalonGenios humo={0.14} />
			</Vert>
			{RONDA.map(({r, x, inc}, i) => {
				const lado = x < 540 ? 1 : -1;
				return (
					<Actor key={i} x={x} y={1560} alto={980} rot={inc}>
						<Muneco ropa={r} pose={{...brazo(1, alcanzar(1, 200 + lado * 120 + 60, -40)), ...brazo(-1, alcanzar(-1, 200 + lado * 120 - 60, -40)), mi: 'abierta', md: 'abierta'}} ojos="feliz" cejas="arrogante" boca="sonrisa" />
					</Actor>
				);
			})}
			<Actor x={540} y={1700} alto={820}>
				<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno'}} ojos="entrecerrados" cejas="arrogante" boca="picara" />
			</Actor>
			<Vineta />
			<Arriba>
				<Titular texto={'“LO TENEMOS\nRODEADO”'} tam={140} color={AMARILLO} rot={-2} />
			</Arriba>
			<En top={1500} right={-420}>
				<SelloGrande texto="SPOILER: NO" color={ROJO} tam={84} rot={-9} />
			</En>
		</AbsoluteFill>
	);
};

/* ---------- 3. EN 52 DÍAS: el Parlamento en el rincón y la sombra de Hitler ---------- */

export const Portada52: React.FC = () => (
	<AbsoluteFill style={{background: '#1e2228'}}>
		<Vert cx={1200} cy={640} k={1.9}>
			<EscRincon />
			<ParlamentoMini x={1240} y={930} ancho={420} />
			<div style={{position: 'absolute', left: 820, top: -60, width: 900, height: 1100, opacity: 0.62}}>
				<Actor x={450} y={1100} alto={1150}>
					<div style={{width: '100%', height: '100%', filter: 'brightness(0)'}}>
						<Muneco ropa={HITLER_CANCILLER} pose={manosEn([150, 560], [250, 560])} sombra={false} />
					</div>
				</Actor>
			</div>
		</Vert>
		<div style={{position: 'absolute', left: 40, top: 760, transform: 'scale(0.4) rotate(-4deg)', transformOrigin: '0 0'}}>
			<div style={{position: 'relative', width: 1000, height: 900}}>
				<Calendario60 x={500} y={0} ancho={1000} tachados={52} marca={52} />
			</div>
		</div>
		<Cronometro x={880} y={880} tam={240} desde={-1e9} para={0} brillo={0.6} />
		<Vineta />
		<Arriba>
			<Titular texto="EN 52 DÍAS" tam={170} color={AMARILLO} rot={-2} />
			<Titular texto={'EL QUE CHILLÓ\nFUE EL PARLAMENTO'} tam={84} rot={-2} />
		</Arriba>
	</AbsoluteFill>
);
