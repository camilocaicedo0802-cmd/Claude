import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from './componentes/Muneco';
import {Contrato, Expediente, JarraVotos, SELLOS_EXPEDIENTE} from './componentes/Recurrentes';
import {HITLER_TRAJE, PAPEN} from './componentes/Vestuario';
import {EscOficinaBerlin} from './escenarios/Epoca';
import {CONDENSADA} from './fuentes';
import {Barra, Copa, EscSalon, Senores} from './escenas/c0';
import {brazo} from './escenas/compartidas';

/* Portadas de YouTube (16:9, 1920x1080 → se entregan a 1280x720).
   Texto arriba y a la izquierda: la esquina de abajo a la derecha la tapa la duración del video.
   Sin esvásticas, banderas ni insignias. */

const TINTA = '#111114';
const AMARILLO = '#ffc21a';
const ROJO = '#d6262e';

const Titular: React.FC<{texto: string; tam: number; color?: string; rot?: number; alinear?: 'left' | 'center'}> = ({texto, tam, color = '#fff', rot = 0, alinear = 'left'}) => {
	const base: React.CSSProperties = {fontFamily: CONDENSADA, fontSize: tam, lineHeight: 0.95, letterSpacing: tam * 0.01, textAlign: alinear, whiteSpace: 'pre', textTransform: 'uppercase'};
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

const Bloque: React.FC<{left: number; top: number; children: React.ReactNode}> = ({left, top, children}) => <div style={{position: 'absolute', left, top}}>{children}</div>;

const Vineta: React.FC = () => <AbsoluteFill style={{background: 'radial-gradient(ellipse at 60% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.55) 100%)'}} />;

/* ---------- 1. LO CONTRATARON: Papen, el contrato y Hitler chiquito ---------- */

export const PortadaContrato: React.FC = () => (
	<AbsoluteFill style={{background: '#232a33'}}>
		<AbsoluteFill style={{transform: 'scale(1.12)', transformOrigin: '70% 40%'}}>
			<EscOficinaBerlin />
		</AbsoluteFill>
		{/* Papen, enorme y feliz, desde abajo */}
		<Actor x={1470} y={1330} alto={1280}>
			<Muneco ropa={PAPEN} pose={{...brazo(-1, alcanzar(-1, 40, 420)), mi: 'abierta', ...manosEn(undefined, [212, 420], {}, true), md: 'oculta', cabeza: -6}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
		</Actor>
		{/* el contrato, en primer plano */}
		<Contrato x={820} y={760} ancho={560} rot={-8} firma={1} />
		{/* Hitler chiquito sobre el contrato, mirando hacia arriba */}
		<Actor x={1090} y={1020} alto={330}>
			<Muneco ropa={HITLER_TRAJE} pose={{...manosFrente([170, 520], [230, 520]), mi: 'agarra', md: 'agarra', cabeza: -10}} ojos="grandes" cejas="preocupado" boca="o" />
		</Actor>
		<Vineta />
		<Bloque left={70} top={50}>
			<Titular texto="LO CONTRATARON" tam={170} color={AMARILLO} rot={-2} />
		</Bloque>
		<Bloque left={90} top={240}>
			<Titular texto={'…Y SE QUEDÓ\nCON LA EMPRESA'} tam={88} rot={-2} />
		</Bloque>
	</AbsoluteFill>
);

/* ---------- 2. NUNCA TUVO LA MAYORÍA: la jarra que no llega ---------- */

export const PortadaMayoria: React.FC = () => (
	<AbsoluteFill style={{background: '#2e2014'}}>
		<AbsoluteFill style={{transform: 'scale(1.05)'}}>
			<Barra />
		</AbsoluteFill>
		<JarraVotos x={1260} y={1010} alto={940} nivel={43.9} />
		{/* Hitler que estira el cuello para ver si llega */}
		<Actor x={1700} y={1180} alto={860} voltear>
			<Muneco ropa={HITLER_TRAJE} pose={{...brazo(1, alcanzar(1, 330, 300)), md: 'agarra', ...manosEn([150, 560]), mi: 'puno', cabeza: 8}} ojos="mirandoLado" cejas="enojado" boca="mueca" />
		</Actor>
		<Vineta />
		<Bloque left={70} top={60}>
			<Titular texto={'¿GANÓ LAS\nELECCIONES?'} tam={150} color="#ffffff" rot={-2} />
		</Bloque>
		<Bloque left={80} top={610}>
			<SelloGrande texto="MEDIO MITO" color={ROJO} tam={120} rot={-8} />
		</Bloque>
	</AbsoluteFill>
);

/* ---------- 3. «ESE YA NO LLEGA A NADA»: los señores se ríen, la sombra crece ---------- */

export const PortadaInofensivo: React.FC = () => (
	<AbsoluteFill style={{background: '#1a0e10'}}>
		<EscSalon />
		{/* la sombra de Hitler, enorme y oscura, crece detrás de los que se ríen */}
		<div style={{position: 'absolute', left: 900, top: -80, width: 1300, height: 1000, borderRadius: '50%', background: 'radial-gradient(ellipse at center, rgba(255,214,150,0.5) 0%, rgba(255,214,150,0) 62%)'}} />
		<div style={{position: 'absolute', inset: 0, opacity: 0.9}}>
			<Actor x={1520} y={1420} alto={1500}>
				<div style={{width: '100%', height: '100%', filter: 'brightness(0.24) saturate(0.6)'}}>
					<Muneco ropa={HITLER_TRAJE} pose={manosEn([150, 560], [250, 560])} sombra={false} ojos="entrecerrados" cejas="enojado" boca="seria" parpadea={false} />
				</div>
			</Actor>
		</div>
		<AbsoluteFill style={{transform: 'translate(300px, 300px) scale(0.86)', transformOrigin: '50% 100%'}}>
			<Senores />
		</AbsoluteFill>
		<Expediente x={430} y={800} ancho={640} rot={-7} sellos={[0, 1, 3].map((k) => ({...SELLOS_EXPEDIENTE[k], desde: -1e9}))} />
		<Vineta />
		<Bloque left={60} top={50}>
			<Titular texto={'“ESE YA NO\nLLEGA A NADA”'} tam={140} color={AMARILLO} rot={-2} />
		</Bloque>
	</AbsoluteFill>
);

export {Copa};

/* ---------- MINIATURA principal (con Hitler grande): «LO CONTRATARON» + «SIN GANAR» ----------
   Criterios de CTR: una sola cara grande con expresión clara, 2–4 palabras, mucho contraste,
   legible en miniatura y que complemente el título (no lo repite). Nada en la esquina inferior derecha. */

export const Miniatura: React.FC = () => (
	<AbsoluteFill style={{background: 'radial-gradient(ellipse at 72% 42%, #6a1a1e 0%, #2a0a0e 45%, #0a0a0e 100%)'}}>
		{/* rayos de luz detrás de él */}
		<svg viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
			{Array.from({length: 14}, (_, i) => {
				const a = (i / 14) * Math.PI * 2;
				return <path key={i} d={`M 1490 420 L ${1490 + Math.cos(a) * 1600} ${420 + Math.sin(a) * 1600} L ${1490 + Math.cos(a + 0.14) * 1600} ${420 + Math.sin(a + 0.14) * 1600} Z`} fill="rgba(255,190,110,0.07)" />;
			})}
		</svg>
		<div style={{position: 'absolute', left: 1090, top: 40, width: 800, height: 800, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,214,140,0.35) 0%, rgba(255,214,140,0) 65%)'}} />
		{/* Hitler, enorme, satisfecho, de brazos cruzados detrás del escritorio */}
		<Actor x={1490} y={1640} alto={1560}>
			<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([256, 446], [146, 432]), mi: 'oculta', md: 'puno', cabeza: -4}} ojos="entrecerrados" cejas="arrogante" boca="picara" />
		</Actor>
		{/* el escritorio y el contrato firmado delante */}
		<div style={{position: 'absolute', left: -20, top: 880, width: 1960, height: 260, background: 'linear-gradient(180deg, #6a3e26, #2e1a0e)', borderTop: `12px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 1100, top: 700, width: 520, height: 300, transform: 'perspective(900px) rotateX(48deg) rotate(-7deg)', transformOrigin: '50% 100%'}}>
			<Contrato x={260} y={-60} ancho={520} rot={0} firma={1} sombra={false} />
		</div>
		<Vineta />
		<Bloque left={70} top={70}>
			<Titular texto={'LO\nCONTRATARON'} tam={196} color={AMARILLO} rot={-3} />
		</Bloque>
		<Bloque left={110} top={600}>
			<SelloGrande texto="SIN GANAR" color={ROJO} tam={150} rot={-8} />
		</Bloque>
	</AbsoluteFill>
);
