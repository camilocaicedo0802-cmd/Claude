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

/* ================= variantes más llamativas (para probar en vidIQ) =================
   Más emoción, sujeto más grande, colores saturados y tensión entre dos personajes. */

/** contrato en la mano izquierda (SVG en coordenadas de la mano; la izquierda no sale espejada) */
const ContratoMano: React.FC<{rot?: number; tam?: number}> = ({rot = 0, tam = 1}) => (
	<g transform={`rotate(${rot} 0 36) translate(0 30) scale(${tam})`}>
		<rect x={-110} y={0} width={220} height={290} rx={8} fill="#f6efdc" stroke={TINTA} strokeWidth={8} />
		<text x={0} y={52} textAnchor="middle" fontFamily={CONDENSADA} fontSize={34} fill="#2a2218">CONTRATO</text>
		<line x1={-80} y1={70} x2={80} y2={70} stroke="#2a2218" strokeWidth={4} />
		<text x={-84} y={112} fontFamily={CONDENSADA} fontSize={30} fill="#c8202a">CANCILLER</text>
		{[140, 165, 190].map((y) => (
			<line key={y} x1={-84} y1={y} x2={70} y2={y} stroke="#cfc4a8" strokeWidth={6} strokeLinecap="round" />
		))}
		<path d="M -80 250 C -60 215 -40 215 -45 245 C -40 265 0 225 20 240 C 40 255 60 230 84 238" stroke="#1d2a6b" strokeWidth={6} fill="none" strokeLinecap="round" />
	</g>
);

const Rayos: React.FC<{cx: number; cy: number; color: string}> = ({cx, cy, color}) => (
	<svg viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
		{Array.from({length: 16}, (_, i) => {
			const a = (i / 16) * Math.PI * 2;
			return <path key={i} d={`M ${cx} ${cy} L ${cx + Math.cos(a) * 2000} ${cy + Math.sin(a) * 2000} L ${cx + Math.cos(a + 0.13) * 2000} ${cy + Math.sin(a + 0.13) * 2000} Z`} fill={color} />;
		})}
	</svg>
);

/** flecha gruesa amarilla con borde negro */
const Flecha: React.FC<{x: number; y: number; ancho: number; rot: number}> = ({x, y, ancho, rot}) => (
	<svg width={ancho} height={ancho * 0.6} viewBox="0 0 300 180" style={{position: 'absolute', left: x, top: y, transform: `rotate(${rot}deg)`, overflow: 'visible', filter: 'drop-shadow(0 10px 0 rgba(0,0,0,0.5))'}}>
		<path d="M 10 70 L 180 70 L 180 20 L 290 90 L 180 160 L 180 110 L 10 110 Z" fill={AMARILLO} stroke={TINTA} strokeWidth={12} strokeLinejoin="round" />
	</svg>
);

/* ----- A · el que se ríe y el que se va a quedar con todo (frío contra fuego) ----- */

export const MiniaturaA: React.FC = () => (
	<AbsoluteFill style={{background: '#0a0a10'}}>
		{/* mitad fría (Papen) y mitad de fuego (Hitler), en diagonal */}
		<AbsoluteFill style={{background: 'linear-gradient(135deg, #1d3a6a 0%, #13284a 42%, #000 42.2%, #000 43%, #ff5a1a 43.2%, #c81e10 70%, #4a0806 100%)'}} />
		<Rayos cx={1450} cy={380} color="rgba(255,220,120,0.12)" />
		<div style={{position: 'absolute', left: 1050, top: -40, width: 820, height: 820, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,230,150,0.55) 0%, rgba(255,230,150,0) 65%)'}} />
		{/* Hitler enorme, sonrisa de villano */}
		<Actor x={1460} y={1830} alto={1900}>
			<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([256, 446], [146, 432]), mi: 'oculta', md: 'puno', cabeza: -5}} ojos="entrecerrados" cejas="enojado" boca="dientes" />
		</Actor>
		{/* Papen, muerto de risa, con el contrato firmado */}
		<Actor x={500} y={1500} alto={1150}>
			<Muneco ropa={PAPEN} pose={{...brazo(-1, alcanzar(-1, 30, 300)), mi: 'agarra', ...brazo(1, alcanzar(1, 360, 360)), md: 'pulgar', cabeza: 8}} objIzq={<ContratoMano rot={170} tam={0.9} />} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
		</Actor>
		<Vineta />
		<Bloque left={60} top={40}>
			<Titular texto="LO CONTRATARON" tam={170} color={AMARILLO} rot={-3} />
		</Bloque>
	</AbsoluteFill>
);

/* ----- B · Hitler enorme mostrando el contrato, flecha y «SIN GANAR» ----- */

export const MiniaturaB: React.FC = () => (
	<AbsoluteFill style={{background: 'radial-gradient(ellipse at 65% 45%, #ff3b1f 0%, #b3120c 40%, #3a0404 100%)'}}>
		<Rayos cx={1250} cy={420} color="rgba(255,236,160,0.16)" />
		<Actor x={1250} y={1900} alto={1950}>
			<Muneco ropa={HITLER_TRAJE} pose={{...brazo(-1, alcanzar(-1, -10, 330)), mi: 'agarra', ...manosEn(undefined, [212, 430], {}, true), md: 'oculta', cabeza: 6}} objIzq={<ContratoMano rot={-5} tam={1.05} />} ojos="entrecerrados" cejas="enojado" boca="dientes" />
		</Actor>
		<Vineta />
		<Bloque left={60} top={60}>
			<Titular texto={'SIN\nGANAR'} tam={260} color={AMARILLO} rot={-4} />
		</Bloque>
		<Flecha x={300} y={600} ancho={330} rot={-8} />
	</AbsoluteFill>
);

/* ----- C · Papen en shock y la sombra gigante de Hitler detrás ----- */

export const MiniaturaC: React.FC = () => (
	<AbsoluteFill style={{background: 'linear-gradient(180deg, #2a0a40 0%, #140620 60%, #05020a 100%)'}}>
		<div style={{position: 'absolute', left: 820, top: -120, width: 1200, height: 1200, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,90,40,0.75) 0%, rgba(200,20,10,0.25) 45%, rgba(0,0,0,0) 70%)'}} />
		{/* la sombra gigante de Hitler, con los ojos encendidos */}
		<Actor x={1400} y={2100} alto={2300}>
			<div style={{width: '100%', height: '100%', filter: 'brightness(0.12)'}}>
				<Muneco ropa={HITLER_TRAJE} pose={manosEn([150, 560], [250, 560])} sombra={false} ojos="entrecerrados" cejas="enojado" boca="dientes" parpadea={false} />
			</div>
		</Actor>
		{[1270, 1500].map((x) => (
			<div key={x} style={{position: 'absolute', left: x - 40, top: 330, width: 80, height: 26, borderRadius: 13, background: '#ffe27a', boxShadow: '0 0 40px 18px rgba(255,200,60,0.85)'}} />
		))}
		{/* Papen en primer plano, en shock */}
		<Actor x={720} y={2050} alto={1500}>
			<Muneco ropa={PAPEN} pose={{...manosEn([90, 330], [310, 330]), mi: 'abierta', md: 'abierta', cabeza: -6}} objIzq={<ContratoMano rot={150} tam={0.8} />} ojos="grandes" cejas="sorprendido" boca="grito" />
		</Actor>
		<Vineta />
		<Bloque left={70} top={50}>
			<Titular texto={'ERROR\nFATAL'} tam={230} color={AMARILLO} rot={-4} />
		</Bloque>
	</AbsoluteFill>
);

/* ----- A2 · la versión A pulida: contorno blanco que despega a los personajes, Papen más grande, contrato legible ----- */

const Contorno: React.FC<{children: React.ReactNode}> = ({children}) => (
	<div style={{position: 'absolute', inset: 0, filter: 'drop-shadow(0 0 0 #fff) drop-shadow(7px 0 0 #fff) drop-shadow(-7px 0 0 #fff) drop-shadow(0 7px 0 #fff) drop-shadow(0 -7px 0 #fff) drop-shadow(0 18px 24px rgba(0,0,0,0.55))'}}>{children}</div>
);

export const MiniaturaA2: React.FC = () => (
	<AbsoluteFill style={{background: '#0a0a10'}}>
		<AbsoluteFill style={{background: 'linear-gradient(135deg, #2458a8 0%, #163a78 40%, #000 40.2%, #000 41%, #ff6a1a 41.2%, #e0240f 66%, #5a0806 100%)', filter: 'saturate(1.15)'}} />
		<Rayos cx={1450} cy={380} color="rgba(255,230,140,0.16)" />
		<div style={{position: 'absolute', left: 1030, top: -60, width: 860, height: 860, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,236,160,0.6) 0%, rgba(255,236,160,0) 65%)'}} />
		<Contorno>
			<Actor x={1470} y={1830} alto={1900}>
				<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([256, 446], [146, 432]), mi: 'oculta', md: 'puno', cabeza: -5}} ojos="entrecerrados" cejas="enojado" boca="dientes" />
			</Actor>
		</Contorno>
		<Contorno>
			<Actor x={540} y={1720} alto={1420}>
				<Muneco ropa={PAPEN} pose={{...brazo(-1, alcanzar(-1, 30, 300)), mi: 'agarra', ...brazo(1, alcanzar(1, 360, 360)), md: 'pulgar', cabeza: 8}} objIzq={<ContratoMano rot={170} tam={1.05} />} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
			</Actor>
		</Contorno>
		<Vineta />
		<Bloque left={50} top={30}>
			<Titular texto="LO CONTRATARON" tam={182} color={AMARILLO} rot={-3} />
		</Bloque>
	</AbsoluteFill>
);
