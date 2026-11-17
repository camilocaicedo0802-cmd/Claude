import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Actor, Muneco, POSES, Pose, alcanzar, manosFrente, senalar} from './componentes/Muneco';
import {Muneca, PastelMesa, PlatoPastel} from './componentes/Objetos';
import {ROPA_MARIA, ROPA_MARIA_NINA} from './componentes/Vestuario';
import {EscVersalles, EscViena} from './escenarios/Escenarios';
import {CONDENSADA, TITULAR} from './fuentes';

/* Portadas del short de María Antonieta (1080x1920). Textos y caras dentro de y = 260..1650. */

const TINTA = '#111114';
const AMARILLO = '#ffc21a';
const ROJO = '#e3262e';
const VERDE = '#22c55e';

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

const Vineta: React.FC<{fuerza?: number}> = ({fuerza = 0.5}) => <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,${fuerza}) 100%)`}} />;

/* ---------- 1. «¿QUE COMAN PASTELES?» ¡NUNCA LO DIJO! ---------- */

export const PortadaNuncaLoDijo: React.FC = () => (
	<AbsoluteFill style={{background: '#e1bf78'}}>
		<AbsoluteFill style={{transform: 'scale(1.08)'}}>
			<EscVersalles />
		</AbsoluteFill>
		<PastelMesa x={860} y={1960} ancho={420} />
		<Actor x={470} y={2170} alto={1320}>
			<Muneco ropa={ROPA_MARIA} pose={{...manosFrente([58, 230], [342, 230]), mi: 'abierta', md: 'abierta', wi: 15, wd: 15}} ojos="grandes" cejas="sorprendido" boca="grito" parpadea={false} respira={false} />
		</Actor>
		<Vineta fuerza={0.45} />
		<div style={{position: 'absolute', top: 266, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
			<Titular texto="¿«QUE COMAN" tam={150} />
			<Titular texto="PASTELES»?" tam={200} color={AMARILLO} />
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 1470, display: 'flex', justifyContent: 'center'}}>
			<Sello texto="¡NUNCA LO DIJO!" color={ROJO} tam={140} rot={-7} />
		</div>
	</AbsoluteFill>
);

/* ---------- 2. LA FAKE NEWS MÁS VIRAL DE LA HISTORIA ---------- */

export const PortadaFakeNews: React.FC = () => (
	<AbsoluteFill style={{background: 'linear-gradient(160deg,#7b3fe4,#ff5f8f)'}}>
		{/* celular con la publicación viral */}
		<div style={{position: 'absolute', left: 110, top: 620, width: 700, height: 1180, background: '#16161c', borderRadius: 64, border: `10px solid ${TINTA}`, transform: 'rotate(-5deg)', boxShadow: '0 24px 0 rgba(0,0,0,0.35)'}}>
			<div style={{position: 'absolute', inset: 26, background: '#ffffff', borderRadius: 40, overflow: 'hidden'}}>
				<div style={{display: 'flex', alignItems: 'center', gap: 16, padding: '26px 26px 10px'}}>
					<div style={{width: 72, height: 72, borderRadius: '50%', background: 'radial-gradient(circle,#1f3a7a 30%,#fff 31%,#fff 60%,#e3262e 61%)', border: `4px solid ${TINTA}`}} />
					<div>
						<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 34, color: '#16161c'}}>revolucion_1789</div>
						<div style={{fontFamily: TITULAR, fontWeight: 700, fontSize: 24, color: '#8a8a96'}}>París · hace 235 años</div>
					</div>
				</div>
				<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 44, color: '#16161c', padding: '8px 28px 14px', lineHeight: 1.1}}>«¡Que coman pasteles!» —la reina 😡</div>
				<div style={{position: 'relative', margin: '0 26px', height: 560, borderRadius: 18, overflow: 'hidden', background: 'linear-gradient(180deg,#f6e2b0,#e1bf78)'}}>
					<div style={{position: 'absolute', left: 150, top: 40, width: 350, height: 788}}>
						<Muneco ropa={ROPA_MARIA} pose={{...brazo(-1, alcanzar(-1, 150, 420)), mi: 'agarra', ...brazo(1, alcanzar(1, 360, 200)), md: 'abierta'}} objIzq={<PlatoPastel rot={180} />} ojos="entrecerrados" cejas="arrogante" boca="picara" parpadea={false} respira={false} sombra={false} />
					</div>
				</div>
				<div style={{fontFamily: TITULAR, fontWeight: 900, fontSize: 34, color: '#16161c', padding: '18px 28px 0'}}>❤️ 1,2 M · 🔁 870 mil</div>
			</div>
		</div>
		{/* la reina real, indignada, señala el celular */}
		<Actor x={900} y={2330} alto={1360}>
			<Muneco ropa={ROPA_MARIA} pose={{...manosFrente([186, 480]), ...brazo(-1, senalar(-1, -280, 120, 0.9)), mi: 'senala', md: 'puno'}} ojos="grandes" cejas="enojado" boca="grito" parpadea={false} respira={false} />
		</Actor>
		<div style={{position: 'absolute', left: 10, width: 900, top: 1490, transform: 'rotate(-6deg)', background: ROJO, border: `9px solid ${TINTA}`, borderRadius: 18, padding: '10px 20px 16px', textAlign: 'center', boxShadow: '0 14px 0 rgba(0,0,0,0.45)'}}>
			<div style={{fontFamily: CONDENSADA, fontSize: 84, color: '#fff', lineHeight: 1.05, whiteSpace: 'nowrap'}}>⚠ INFORMACIÓN FALSA</div>
		</div>
		<div style={{position: 'absolute', top: 262, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
			<Titular texto="LA FAKE NEWS" tam={160} color={AMARILLO} />
			<Titular texto="MÁS VIRAL DE LA HISTORIA" tam={86} />
		</div>
	</AbsoluteFill>
);

/* ---------- 3. LO QUE TE CONTARON vs LA VERDAD ---------- */

export const PortadaVersus: React.FC = () => (
	<AbsoluteFill style={{background: '#000'}}>
		{/* izquierda: la reina "sin corazón" con su pastel */}
		<div style={{position: 'absolute', left: 0, top: 0, width: 540, height: 1920, overflow: 'hidden', background: 'linear-gradient(180deg,#5a1a1a,#1e0808)'}}>
			<Actor x={290} y={1820} alto={980}>
				<Muneco ropa={ROPA_MARIA} pose={{...brazo(-1, alcanzar(-1, 150, 420)), mi: 'agarra', ...brazo(1, alcanzar(1, 372, 330)), md: 'abierta', wd: 20}} objIzq={<PlatoPastel rot={180} />} ojos="entrecerrados" cejas="arrogante" boca="picara" parpadea={false} respira={false} />
			</Actor>
		</div>
		{/* derecha: la niña en Viena */}
		<div style={{position: 'absolute', left: 540, top: 0, width: 540, height: 1920, overflow: 'hidden'}}>
			<div style={{position: 'absolute', left: -270, top: 0, width: 1080, height: 1920}}>
				<EscViena />
				<Actor x={540} y={1800} alto={820}>
					<Muneco ropa={ROPA_MARIA_NINA} pose={{...manosFrente([170, 450]), mi: 'agarra', ...brazo(1, alcanzar(1, 330, 170)), md: 'abierta', salto: 20}} objIzq={<Muneca />} ojos="feliz" cejas="neutral" boca="sonrisaGrande" parpadea={false} respira={false} />
				</Actor>
			</div>
		</div>
		<div style={{position: 'absolute', left: 528, top: 0, width: 24, height: 1920, background: TINTA}} />
		<div style={{position: 'absolute', left: 540, top: 960, transform: 'translate(-50%,-50%) rotate(-8deg)', width: 230, height: 230, borderRadius: '50%', background: AMARILLO, border: `12px solid ${TINTA}`, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 14px 0 rgba(0,0,0,0.5)'}}>
			<div style={{fontFamily: CONDENSADA, fontSize: 130, color: TINTA, lineHeight: 1}}>VS</div>
		</div>
		<div style={{position: 'absolute', top: 268, left: 0, width: 540, display: 'flex', justifyContent: 'center'}}>
			<Titular texto={'LO QUE TE\nCONTARON'} tam={100} color="#ff8a80" />
		</div>
		<div style={{position: 'absolute', top: 268, left: 540, width: 540, display: 'flex', justifyContent: 'center'}}>
			<Titular texto={'LA\nVERDAD'} tam={100} color={VERDE} />
		</div>
		<div style={{position: 'absolute', top: 1470, left: 0, width: 540, display: 'flex', justifyContent: 'center'}}>
			<Sello texto="«¡PASTELES!»" color={ROJO} tam={74} rot={-6} />
		</div>
		<div style={{position: 'absolute', top: 1470, left: 540, width: 540, display: 'flex', justifyContent: 'center'}}>
			<Sello texto="¡ERA UNA NIÑA!" color="#1f9d48" tam={70} rot={5} />
		</div>
	</AbsoluteFill>
);

// evita advertencias si alguna pose con nombre no se usa
void POSES;
