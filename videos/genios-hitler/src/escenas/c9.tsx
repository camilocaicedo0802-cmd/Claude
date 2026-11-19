import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {Chistera, Cuenta, ExpedienteSellado, JarraVotos, SelloPostal} from '../componentes/Recurrentes';
import {Toma} from '../componentes/Toma';
import {Sello} from '../componentes/Utileria';
import {BANQUERO, GENERAL, HIJO, HITLER_CANCILLER, JUEZ, PAPEN, PAPEN_SIN_SOMBRERO, SENOR_3, SOLDADO, UNIFORME_MARRON} from '../componentes/Vestuario';
import {EscLiso, EscMapa, EscMesaArriba, EscTribunal, Humo} from '../escenarios/Epoca';
import {CONDENSADA, MONO, SERIF} from '../fuentes';
import {P, Plano, TINTA, antes, centrar, clamp, fin, golpeCam, ini, mezclaCam, pal, tramo} from './base';
import {Barra, ENCUADRE_CONTRATO, ENCUADRE_VENTANA, OficinaPapen} from './c0';
import {brazo} from './compartidas';
import {Regalo, Silueta} from './utileria_c89';

/* CAPÍTULO 9 · La cuenta (10:33–11:54). Azul noche, madera de Núremberg y, al final, la oficina del principio.
   Segundo (y último) corte seco: la Noche de los Cuchillos Largos. */

/* ---------- rótulo: la misma cuenta, ahora con «1934» ---------- */

const K1: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#0c0d12" luz="255,210,150" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.32], y: [-40, -90]}}>
		<div style={{position: 'absolute', left: -40, right: -40, top: 700, bottom: -40, background: 'linear-gradient(180deg, #2a1a10, #0a0604)', borderTop: `8px solid ${TINTA}`}} />
		<Cuenta x={980} y={330} ancho={420} rot={-6} anio="1934" />
	</Toma>
);

/* ---------- la Noche de los Cuchillos Largos: calle de noche, sombras largas (sin humor) ---------- */

const EscCalleLarga: React.FC = () => (
	<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #05070e 0%, #0e1426 55%, #141a2c 100%)'}}>
		{[0, 1, 2, 3, 4].map((i) => (
			<div key={i} style={{position: 'absolute', left: -60 + i * 420, top: 120 + (i % 2) * 60, width: 380, height: 640, background: '#0a0d18', border: '4px solid #05060c'}}>
				{Array.from({length: 6}, (_, k) => (
					<div key={k} style={{position: 'absolute', left: 40 + (k % 3) * 110, top: 60 + Math.floor(k / 3) * 180, width: 60, height: 100, background: k === (i * 2) % 6 ? 'rgba(255,214,140,0.45)' : '#141a2c'}} />
				))}
			</div>
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: 760, bottom: 0, background: 'linear-gradient(180deg, #1a2034, #0a0d18)'}} />
		{/* farol */}
		<div style={{position: 'absolute', left: 1500, top: 260, width: 14, height: 520, background: '#05060c'}} />
		<div style={{position: 'absolute', left: 1470, top: 230, width: 74, height: 60, background: 'rgba(255,220,150,0.9)', border: '6px solid #05060c', boxShadow: '0 0 80px 30px rgba(255,210,140,0.35)'}} />
		<div style={{position: 'absolute', left: 1140, top: 290, width: 760, height: 800, background: 'radial-gradient(ellipse at 50% 0%, rgba(255,214,150,0.22), rgba(255,214,150,0) 70%)'}} />
	</div>
);

const K2: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const avance = (f - d) * 1.4;
	return (
		<Toma escena={<EscCalleLarga />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.06], x: [10, -10]}}>
			{[0, 1, 2].map((i) => (
				<React.Fragment key={i}>
					{/* sombra alargada sobre el empedrado */}
					<div style={{position: 'absolute', left: 1250 - avance - i * 150, top: 900, width: 700, height: 70, background: 'rgba(0,0,0,0.55)', transform: 'skewX(60deg)', transformOrigin: '0 0', filter: 'blur(4px)'}} />
					<Silueta x={1300 - avance - i * 150} y={910} alto={520} ropa={UNIFORME_MARRON} camina={0.7} voltear tono={0.04} />
				</React.Fragment>
			))}
		</Toma>
	);
};

/** la puerta abierta y el sombrero del general en el suelo. Sin cuerpos. */
const K3: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#0a0b10" foco={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.12], y: [0, 30]}}>
		<div style={{position: 'absolute', left: 700, top: 120, width: 520, height: 820, background: '#1a1408', border: '10px solid #050505'}} />
		<div style={{position: 'absolute', left: 708, top: 128, width: 504, height: 804, background: 'linear-gradient(180deg, rgba(255,226,170,0.55), rgba(255,226,170,0.2))'}} />
		<div style={{position: 'absolute', left: 1212, top: 128, width: 160, height: 804, background: '#3a2a1a', border: '6px solid #050505', transform: 'perspective(800px) rotateY(-55deg)', transformOrigin: '0 50%'}} />
		<div style={{position: 'absolute', left: 520, top: 930, width: 900, height: 170, background: 'linear-gradient(180deg, rgba(255,226,170,0.35), rgba(255,226,170,0))', clipPath: 'polygon(20% 0, 80% 0, 100% 100%, 0 100%)'}} />
		{/* la gorra del general, caída */}
		<svg width={260} height={130} viewBox="0 0 260 130" style={{position: 'absolute', left: 820, top: 900, transform: 'rotate(-8deg)'}}>
			<ellipse cx={130} cy={92} rx={118} ry={30} fill="#3a3e34" stroke={TINTA} strokeWidth={8} />
			<path d="M 40 90 Q 40 20 130 18 Q 220 20 220 90 Z" fill="#6a6f60" stroke={TINTA} strokeWidth={8} />
			<path d="M 60 96 Q 130 128 200 96 L 190 112 Q 130 130 70 112 Z" fill="#1a1a1a" stroke={TINTA} strokeWidth={6} />
		</svg>
	</Toma>
);

/** dos escritorios vacíos con papeles */
const K4: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#14161c" luz="200,210,230" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], x: [30, -30]}}>
		<div style={{position: 'absolute', left: 0, right: 0, top: 820, bottom: 0, background: '#0e0f14'}} />
		{[520, 1400].map((x, i) => (
			<React.Fragment key={i}>
				<div style={{position: 'absolute', left: x - 300, top: 640, width: 600, height: 40, background: '#4a3020', border: `7px solid ${TINTA}`}} />
				<div style={{position: 'absolute', left: x - 270, top: 680, width: 40, height: 200, background: '#3a2414', border: `6px solid ${TINTA}`}} />
				<div style={{position: 'absolute', left: x + 230, top: 680, width: 40, height: 200, background: '#3a2414', border: `6px solid ${TINTA}`}} />
				{[0, 1, 2].map((k) => (
					<div key={k} style={{position: 'absolute', left: x - 200 + k * 90, top: 600 - k * 6, width: 150, height: 40, background: '#e9e4d6', border: `4px solid ${TINTA}`, transform: `rotate(${(k - 1) * 9}deg)`}} />
				))}
				{/* silla apartada, vacía */}
				<div style={{position: 'absolute', left: x + (i ? -360 : 300), top: 560, width: 120, height: 300, transform: `rotate(${i ? -8 : 8}deg)`}}>
					<div style={{position: 'absolute', left: 10, top: 0, width: 100, height: 140, background: '#3a2414', border: `6px solid ${TINTA}`}} />
					<div style={{position: 'absolute', left: 0, top: 140, width: 120, height: 24, background: '#3a2414', border: `6px solid ${TINTA}`}} />
					<div style={{position: 'absolute', left: 8, top: 164, width: 10, height: 130, background: TINTA}} />
					<div style={{position: 'absolute', left: 102, top: 164, width: 10, height: 130, background: TINTA}} />
				</div>
			</React.Fragment>
		))}
	</Toma>
);

/** Papen se asoma detrás de la cortina; guardias afuera. Desde arriba, pequeño. */
const K5: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const asoma = tramo(f, d + 6, d + 18);
	return (
		<Toma escena={<EscLiso color="#1a1c26" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.18], y: [-30, -50]}} angulo={-10}>
			{/* ventana con guardias en la calle */}
			<div style={{position: 'absolute', left: 560, top: 140, width: 800, height: 620, background: 'linear-gradient(180deg, #2a3450, #4a5470)', border: `12px solid ${TINTA}`}}>
				{[0, 1].map((i) => (
					<Silueta key={i} x={220 + i * 360} y={600} alto={420} ropa={UNIFORME_MARRON} voltear={i === 1} tono={0.1} />
				))}
				<div style={{position: 'absolute', left: 394, top: 0, width: 12, height: '100%', background: TINTA}} />
			</div>
			<Actor x={760 + 120 * asoma} y={1080} alto={700}>
				<Muneco ropa={PAPEN} pose={{...manosFrente([150, 420], [200, 420]), mi: 'agarra', md: 'agarra', cabeza: 10}} ojos="grandes" cejas="preocupado" boca="mueca" />
			</Actor>
			{/* cortina */}
			<div style={{position: 'absolute', left: 300, top: 80, width: 520 - 120 * asoma, height: 1000, background: 'linear-gradient(90deg, #5a1e24, #7a2a30 50%, #4a161c)', border: `8px solid ${TINTA}`, borderRadius: '0 0 30px 0'}} />
			<div style={{position: 'absolute', left: 1240, top: 80, width: 300, height: 1000, background: 'linear-gradient(90deg, #4a161c, #7a2a30 50%, #5a1e24)', border: `8px solid ${TINTA}`}} />
		</Toma>
	);
};

/* ---------- muere Hindenburg y Hitler se queda con todo ---------- */

const Sillon: React.FC<{x: number; y: number}> = ({x, y}) => (
	<svg width={420} height={520} viewBox="0 0 420 520" style={{position: 'absolute', left: x - 210, top: y - 520, overflow: 'visible'}}>
		<path d="M 60 300 L 70 40 Q 210 0 350 40 L 360 300 Z" fill="#7a2a30" stroke={TINTA} strokeWidth={10} />
		<rect x={20} y={260} width={380} height={90} rx={30} fill="#8a3038" stroke={TINTA} strokeWidth={10} />
		<rect x={0} y={200} width={70} height={190} rx={30} fill="#6a2028" stroke={TINTA} strokeWidth={10} />
		<rect x={350} y={200} width={70} height={190} rx={30} fill="#6a2028" stroke={TINTA} strokeWidth={10} />
		<rect x={60} y={350} width={30} height={160} fill="#c9a43a" stroke={TINTA} strokeWidth={8} />
		<rect x={330} y={350} width={30} height={160} fill="#c9a43a" stroke={TINTA} strokeWidth={8} />
		{[100, 160, 220, 280].map((cx) => (
			<circle key={cx} cx={cx} cy={90} r={8} fill="#c9a43a" />
		))}
	</svg>
);

const K6: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#1c2440" luz="230,220,200" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.14], y: [0, 20]}}>
		<div style={{position: 'absolute', left: 0, right: 0, top: 880, bottom: 0, background: '#14182a'}} />
		<Sillon x={960} y={960} />
		{/* el bastón y los guantes, solos */}
		<div style={{position: 'absolute', left: 1210, top: 560, width: 14, height: 400, background: '#2a1a10', border: `4px solid ${TINTA}`, transform: 'rotate(8deg)'}} />
	</Toma>
);

const MesaConsejo: React.FC = () => (
	<>
		<div style={{position: 'absolute', left: 260, right: 260, top: 760, height: 60, background: '#4a2c1a', border: `8px solid ${TINTA}`, borderRadius: 10}} />
		<div style={{position: 'absolute', left: 280, right: 280, top: 820, height: 300, background: 'linear-gradient(180deg, #3a2414, #1a0e06)', borderLeft: `8px solid ${TINTA}`, borderRight: `8px solid ${TINTA}`}} />
	</>
);

const K7: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#2a2028" luz="255,220,170" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.16], y: [80, 110]}} angulo={9}>
		{[420, 640, 1280, 1500].map((x, i) => (
			<div key={i} style={{position: 'absolute', left: x - 70, top: 520, width: 140, height: 260, background: i < 2 ? '#6a6a72' : '#6a6a72', border: `7px solid ${TINTA}`, borderRadius: '20px 20px 0 0'}} />
		))}
		<div style={{position: 'absolute', left: 860, top: 300, width: 200, height: 480, background: '#3a2a22', border: `8px solid ${TINTA}`, borderRadius: '30px 30px 0 0'}} />
		<Actor x={960} y={1120} alto={900}>
			<Muneco ropa={HITLER_CANCILLER} pose={{...manosEn([130, 600], [270, 600]), mi: 'puno', md: 'puno'}} ojos="entrecerrados" cejas="enojado" boca="seria" />
		</Actor>
		<MesaConsejo />
	</Toma>
);

/** un ejército que le jura lealtad a él: mano alzada de juramento (vertical, junto a la cabeza) */
const K8: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const jura = pal(220, 'jura');
	return (
		<Toma escena={<EscLiso color="#2a2a30" luz="220,220,230" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.14], y: [40, 60]}} angulo={8}>
			{[0, 1, 2].map((fila) =>
				Array.from({length: 9}, (_, i) => {
					const t = tramo(f, jura + i + fila * 2, jura + i + fila * 2 + 8);
					return (
						<Actor key={`${fila}-${i}`} x={140 + i * 205 + (fila % 2) * 100} y={620 + fila * 150} alto={360 + fila * 60}>
							<Muneco ropa={SOLDADO} pose={{bd: 12 + 140 * t, cd: -10 - 30 * t, md: t > 0.5 ? 'abierta' : 'relajada', ...manosEn([150, 560])}} ojos="normal" cejas="neutral" boca="seria" parpadea={false} respira={false} />
						</Actor>
					);
				}),
			)}
		</Toma>
	);
};

/* ---------- los sellos vuelven ---------- */

const AlbumPagina: React.FC<{despega: number; abre: number}> = ({despega, abre}) => (
	<div style={{position: 'absolute', left: 360, top: 150, width: 1200, height: 780, transform: `perspective(1600px) rotateX(${(1 - abre) * 70}deg)`, transformOrigin: '50% 100%'}}>
		<div style={{position: 'absolute', inset: 0, background: '#1f3a2a', border: `10px solid ${TINTA}`, borderRadius: 14}} />
		<div style={{position: 'absolute', left: 30, top: 30, right: 30, bottom: 30, background: '#f2ead4', border: `6px solid ${TINTA}`}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 24, textAlign: 'center', fontFamily: SERIF, fontStyle: 'italic', fontSize: 44, color: '#2a2218'}}>Deutsches Reich</div>
			{[0, 1, 2, 3].map((i) => (
				<div key={i} style={{position: 'absolute', left: 60 + i * 270, top: 120, width: 230, height: 4, background: '#cfc4a8'}} />
			))}
			<SelloPostal x={570} y={420} ancho={250} cara="hitler" valor="12" />
			<div style={{position: 'absolute', inset: 0, transform: `translate(${despega * 520}px, ${-despega * 260}px) rotate(${despega * 38}deg)`, transformOrigin: '570px 420px', opacity: 1 - Math.max(0, despega - 0.8) * 5}}>
				<SelloPostal x={570} y={420} ancho={250} cara="hindenburg" valor="12" />
			</div>
		</div>
	</div>
);

const K9: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscMesaArriba tono="oscura" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], y: [0, 20]}}>
			<AlbumPagina abre={tramo(f, d + 2, d + 18)} despega={0} />
		</Toma>
	);
};

const K10: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sale = pal(223, 'Hitler');
	return (
		<Toma escena={<EscMesaArriba tono="oscura" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => golpeCam(ff, antes(sale), centrar(930, 570, 1.25), centrar(930, 570, 1.7))}>
			<AlbumPagina abre={1} despega={tramo(f, ini(223), sale - 2)} />
		</Toma>
	);
};

/** miles de sobres vuelan con el sello de Hitler */
const Sobre: React.FC<{x: number; y: number; rot: number; tam: number}> = ({x, y, rot, tam}) => (
	<div style={{position: 'absolute', left: x, top: y, width: tam, height: tam * 0.62, background: '#efe6cf', border: `${tam * 0.03}px solid ${TINTA}`, transform: `rotate(${rot}deg)`}}>
		<svg viewBox="0 0 100 62" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
			<polyline points="0,0 50,34 100,0" fill="none" stroke={TINTA} strokeWidth={2} />
		</svg>
		<div style={{position: 'absolute', right: tam * 0.06, top: tam * 0.06, width: tam * 0.2, height: tam * 0.24, background: '#a85a42', border: `${tam * 0.012}px solid ${TINTA}`}} />
	</div>
);

const K11: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const t = f - d;
	return (
		<Toma escena={<EscLiso color="#3a3028" luz="255,226,170" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08]}}>
			{Array.from({length: 46}, (_, i) => {
				const vel = 8 + (i % 5) * 3;
				const x = ((i * 211 + t * vel) % 2300) - 200;
				const y = ((i * 97) % 1000) - 40 + Math.sin(t / 8 + i) * 30;
				return <Sobre key={i} x={x} y={y} rot={Math.sin(t / 6 + i) * 25} tam={110 + (i % 4) * 40} />;
			})}
			<SelloPostal x={960} y={540} ancho={260 + 20 * Math.sin(t / 6)} cara="hitler" rot={-4} />
		</Toma>
	);
};

/* ---------- Papen sobrevive a todo: Núremberg y las memorias ---------- */

const K12: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscTribunal tono="nuremberg" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.16], x: [-40, 20], y: [0, 20]}}>
		<Actor x={960} y={760} alto={520}>
			<Muneco ropa={JUEZ} pose={manosFrente([160, 470], [240, 470])} ojos="entrecerrados" cejas="neutral" boca="seria" />
		</Actor>
		<div style={{position: 'absolute', left: 520, top: 760, width: 880, height: 330, background: 'linear-gradient(180deg, #3a2414, #1e140a)', border: `9px solid ${TINTA}`}} />
		<Actor x={420} y={1080} alto={600}>
			<Muneco ropa={PAPEN_SIN_SOMBRERO} pose={{...manosFrente([170, 520], [230, 520]), mi: 'agarra', md: 'agarra'}} ojos="mirandoLado" cejas="arrogante" boca="seria" />
		</Actor>
	</Toma>
);

const K13: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const absuelve = pal(228, 'absuelven');
	const sale = tramo(f, absuelve + 4, h);
	const sombrero = f >= absuelve + 10;
	return (
		<Toma escena={<EscTribunal tono="nuremberg" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.14], x: [0, -160 * sale]}} golpes={[[absuelve, 0.05]]}>
			{/* el mazo */}
			<div style={{position: 'absolute', left: 1180, top: f >= absuelve - 2 && f < absuelve + 4 ? 600 : 520, width: 160, height: 60, background: '#5a3420', border: `7px solid ${TINTA}`, borderRadius: 14}} />
			<div style={{position: 'absolute', left: 1250, top: f >= absuelve - 2 && f < absuelve + 4 ? 650 : 570, width: 20, height: 140, background: '#7a4a2a', border: `5px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 1140, top: 730, width: 240, height: 40, background: '#5a3420', border: `6px solid ${TINTA}`, borderRadius: 8}} />
			<Actor x={760 + 900 * sale} y={1080} alto={640}>
				<Muneco
					ropa={sombrero ? PAPEN : PAPEN_SIN_SOMBRERO}
					camina={sale > 0.02 ? 1 : 0}
					pose={sombrero ? manosEn([150, 560], [250, 560]) : {...brazo(1, alcanzar(1, 260, 150)), md: 'agarra', ...manosEn([150, 560])}}
					ojos="feliz"
					cejas="arrogante"
					boca="o"
				/>
			</Actor>
			{!sombrero && f >= absuelve && <Chistera x={760 + 900 * sale + 60} y={420 - 40 * tramo(f, absuelve, absuelve + 10)} ancho={150} />}
		</Toma>
	);
};

const K14: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const texto = 'MIS MEMORIAS\n\nYo no tuve la culpa de nada.';
	const n = Math.floor(interpolate(f, [d + 8, fin(229)], [0, texto.length], clamp));
	return (
		<Toma escena={<EscLiso color="#2a2420" luz="255,214,150" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.2], y: [60, 90]}}>
			<Actor x={1400} y={1100} alto={760}>
				<Muneco ropa={PAPEN} pose={{...manosFrente([150, 600], [250, 600]), mi: 'relajada', md: 'relajada', cabeza: -6}} ojos="feliz" cejas="arrogante" boca="sonrisa" />
			</Actor>
			{/* máquina de escribir y su hoja */}
			<div style={{position: 'absolute', left: 520, top: 260, width: 620, height: 470, background: '#fbf8ef', border: `7px solid ${TINTA}`, padding: 40, boxSizing: 'border-box', fontFamily: MONO, fontSize: 40, whiteSpace: 'pre-wrap', color: '#1a1a1a'}}>
				{texto.slice(0, n)}
				<span style={{opacity: f % 12 < 6 ? 1 : 0}}>▌</span>
			</div>
			<div style={{position: 'absolute', left: 420, top: 690, width: 820, height: 220, background: '#2a2a30', border: `8px solid ${TINTA}`, borderRadius: '30px 30px 10px 10px'}}>
				{Array.from({length: 3}, (_, r) =>
					Array.from({length: 10}, (_, c) => <div key={`${r}-${c}`} style={{position: 'absolute', left: 50 + c * 72 + r * 18, top: 40 + r * 54, width: 44, height: 40, borderRadius: '50%', background: '#e9e4d6', border: `4px solid ${TINTA}`}} />),
				)}
			</div>
			<div style={{position: 'absolute', left: -40, right: -40, top: 900, bottom: -40, background: '#3a2414', borderTop: `8px solid ${TINTA}`}} />
		</Toma>
	);
};

/* ---------- serio: el expediente INOFENSIVO cae sobre el mapa oscuro de Europa ---------- */

const MapaEuropa: React.FC = () => (
	<div style={{position: 'absolute', inset: 0, overflow: 'hidden'}}>
		<div style={{position: 'absolute', left: -1980, top: 60, width: 3840, height: 1080, transform: 'scale(1.0)'}}>
			<EscMapa tono="oscuro" marcas={false} />
		</div>
	</div>
);


const K15: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cae = tramo(f, d + 6, d + 30, (u) => 1 - Math.pow(1 - u, 2));
	return (
		<Toma escena={<MapaEuropa />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}}>
			<div style={{position: 'absolute', inset: 0, transform: `scale(${1.5 - 0.5 * cae}) rotate(${(1 - cae) * 10}deg)`, opacity: interpolate(cae, [0, 0.3], [0, 1], clamp)}}>
				<ExpedienteSellado x={1000} y={560} ancho={860} rot={-6} n={4} />
			</div>
			<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.6) 90%)'}} />
		</Toma>
	);
};

const K16: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<MapaEuropa />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.25, 1.4], x: [-40, -80], y: [60, 90]}}>
		<ExpedienteSellado x={1000} y={560} ancho={860} rot={-6} n={4} />
		<div style={{position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.35)'}} />
	</Toma>
);

/* ---------- el veredicto ---------- */

const K17: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Barra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], y: [0, 30]}} encima={<Sello x={960} y={520} texto="MEDIO MITO" desde={antes(pal(233, 'medio'))} tam={130} rot={-10} solido />}>
		<JarraVotos x={960} y={880} alto={720} nivel={43.9} />
	</Toma>
);

const K18: React.FC<P> = ({d, h, e, s}) => {
	const g = antes(pal(234, 'nunca'));
	return (
		<Toma escena={<Barra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(f) => golpeCam(f, g, centrar(960, 540, 1.08 - 0.05 * tramo(f, d, g)), centrar(960, 330, 2.4))}>
			<JarraVotos x={960} y={880} alto={720} nivel={43.9} />
		</Toma>
	);
};

/** la caja de regalo pasa de mano en mano entre chisteras hasta llegar a Hitler */
const K19: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const fila = [
		{x: 260, ropa: BANQUERO},
		{x: 600, ropa: PAPEN},
		{x: 940, ropa: {...SENOR_3, cabeza: {...SENOR_3.cabeza, gorra: 'chistera' as const}}},
		{x: 1280, ropa: {...HIJO, cabeza: {...HIJO.cabeza, gorra: 'chistera' as const}}},
	];
	const t = tramo(f, d + 6, pal(235, 'listos'), (u) => u);
	const xs = [...fila.map((p) => p.x), 1660];
	const pos = t * (xs.length - 1);
	const i = Math.min(xs.length - 2, Math.floor(pos));
	const u = pos - i;
	const bx = xs[i] + (xs[i + 1] - xs[i]) * u;
	const by = 560 - Math.sin(u * Math.PI) * 70;
	return (
		<Toma escena={<EscLiso color="#3a2026" luz="255,226,170" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(260 + 1400 * tramo(ff, d, h), 560, 1.35)}>
			<div style={{position: 'absolute', left: -200, right: -200, top: 900, bottom: -40, background: '#1e1014'}} />
			{fila.map((p, k) => (
				<Actor key={k} x={p.x} y={1060} alto={820} voltear={k % 2 === 1}>
					<Muneco ropa={p.ropa} pose={manosFrente([110, 420], [290, 420])} ojos="feliz" cejas="arrogante" boca="sonrisa" />
				</Actor>
			))}
			<Actor x={1660} y={1060} alto={820}>
				<Muneco ropa={HITLER_CANCILLER} pose={manosFrente([110, 420], [290, 420])} ojos="entrecerrados" cejas="arrogante" boca="seria" />
			</Actor>
			<Regalo x={bx} y={by} tam={170} rot={Math.sin(f / 4) * 6} />
		</Toma>
	);
};

/** el final: la misma oficina y el mismo encuadre; la silla de Papen vacía y Hitler detrás del escritorio (desde abajo).
 *  La cámara hace el recorrido inverso al de la apertura: del contrato a la ventana nevada. */
const K20: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={<OficinaPapen desliza={1} palmadas={false} papen={false} amigo={false} hitler sillaVacia />}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1, 1]}}
		angulo={7}
		camFn={(f) => mezclaCam(ENCUADRE_CONTRATO, ENCUADRE_VENTANA, tramo(f, ini(237), h - 6))}
	/>
);

export const PLANOS_C9: Plano[] = [
	{n: 'c9-cuenta', d: ini(213) - 8, e: 'fundido', C: K1},
	{n: 'c9-noche', d: antes(pal(213, 'Noche', 2)), e: 'corte', C: K2},
	{n: 'c9-general', d: ini(214), e: 'fundido', C: K3},
	{n: 'c9-escritorios', d: ini(215), e: 'fundido', C: K4},
	{n: 'c9-cortina', d: ini(216), e: 'fundido', C: K5},
	{n: 'c9-sillon', d: ini(218), e: 'fundido', C: K6},
	{n: 'c9-cabecera', d: antes(pal(218, 'Hitler')), e: 'zoom', C: K7},
	{n: 'c9-juramento', d: ini(220), e: 'latigoDer', C: K8},
	{n: 'c9-album', d: ini(221), e: 'latigoIzq', C: K9},
	{n: 'c9-despega', d: ini(223), e: 'zoom', C: K10},
	{n: 'c9-sobres', d: ini(224), e: 'latigoDer', C: K11},
	{n: 'c9-nuremberg', d: ini(225), e: 'latigoIzq', C: K12},
	{n: 'c9-absuelto', d: ini(227), e: 'zoom', C: K13},
	{n: 'c9-memorias', d: ini(229), e: 'latigoDer', C: K14},
	{n: 'c9-expediente', d: ini(230), e: 'fundido', C: K15},
	{n: 'c9-decenas', d: ini(231), e: 'fundido', C: K16},
	{n: 'c9-jarra', d: ini(232), e: 'fundido', C: K17},
	{n: 'c9-nunca', d: ini(234), e: 'zoom', C: K18},
	{n: 'c9-regalo', d: ini(235), e: 'latigoDer', C: K19},
	{n: 'c9-final', d: ini(236), e: 'fundido', C: K20},
];

export const SONIDOS_C9: [string, number, number][] = [
	['puerta', ini(214) + 4, 0.5],
	['caja', pal(223, 'Hitler'), 1.0],
	['sobres', ini(224), 0.9],
	['mazo', pal(228, 'absuelven'), 1.0],
	['silbido', pal(228, 'absuelven') + 14, 0.7],
	['teclas', ini(229) + 8, 0.6],
	['sello', antes(pal(233, 'medio')), 1.0],
	['pop', pal(235, 'listos'), 0.5],
];


