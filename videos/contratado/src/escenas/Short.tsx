import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {Cara, JarraVotos, Raton} from '../componentes/Recurrentes';
import {DardoVolando} from '../componentes/Objetos';
import {Toma} from '../componentes/Toma';
import {Sello} from '../componentes/Utileria';
import {BANQUERO, FUNCIONARIO, GENERAL, HITLER_CANCILLER, HITLER_TRAJE, MINISTRO, PAPEN, SENOR_3, UNIFORME_MARRON} from '../componentes/Vestuario';
import {EscLiso, EscOficinaBerlin, EscRincon} from '../escenarios/Epoca';
import {CONDENSADA, TITULAR} from '../fuentes';
import {Montaje, P, Plano, TINTA, antes, clamp, fin, ini, pal, pop, tramo} from './base';
import {Barra, OficinaPapen} from './c0';
import {CuadroHindenburgSello, CuadroJuezDeportar, CuadroTiroTecho, Silla, brazo} from './compartidas';
import {EscSalonGenios} from './utileria_c67';
import {Bancadas, Cronometro, EscIncendio, ParlamentoMini, Silueta} from './utileria_c89';

/*
 * Short «Lo contrataron» (1080x1920, 30 fps): el resumen del video largo con sus mismas imágenes.
 * Las escenas del largo (16:9) se recomponen en vertical con `Vert`; lo nuevo se dibuja directo en vertical.
 * Sin esvásticas, banderas ni insignias. Sin cortes secos: barridos y zooms.
 */

/* ---------------- encuadre vertical de un mundo 16:9 ---------------- */

/** pone el mundo de 1920x1080 en el cuadro vertical con el punto (cx, cy) al centro y escala k.
 *  Si no llena el alto, detrás va una copia desenfocada del mismo mundo. */
const Vert: React.FC<{cx: number; cy: number; k: number; children: React.ReactNode}> = ({cx, cy, k, children}) => {
	const llena = k * 1080 >= 1920;
	const capa = (kk: number, estilo?: React.CSSProperties) => {
		const mx = 540 / kk;
		const x = Math.max(mx, Math.min(1920 - mx, cx));
		const my = 960 / kk;
		const y = kk * 1080 >= 1920 ? Math.max(my, Math.min(1080 - my, cy)) : 540;
		return <div style={{position: 'absolute', left: 540 - x * kk, top: 960 - y * kk, width: 1920, height: 1080, transform: `scale(${kk})`, transformOrigin: '0 0', ...estilo}}>{children}</div>;
	};
	return (
		<>
			{!llena && capa(1920 / 1080 * 1.04, {filter: 'blur(26px) brightness(0.5)'})}
			{capa(k)}
		</>
	);
};
type Encuadre = {cx: number; cy: number; k: number};
const mezclaEnc = (a: Encuadre, b: Encuadre, t: number): Encuadre => ({cx: a.cx + (b.cx - a.cx) * t, cy: a.cy + (b.cy - a.cy) * t, k: a.k + (b.k - a.k) * t});

const VENTANA: Encuadre = {cx: 410, cy: 400, k: 2.3};
const CONTRATO: Encuadre = {cx: 1190, cy: 560, k: 1.9};
const FINAL: Encuadre = {cx: 1250, cy: 520, k: 1.9};

/* ---------------- 0 · escena imposible ---------------- */

const OficinaMovil: React.FC<{d: number; h: number}> = ({d, h}) => {
	const f = useCurrentFrame();
	const e = mezclaEnc(VENTANA, CONTRATO, tramo(f, d, h + 6));
	return (
		<Vert {...e}>
			<OficinaPapen desliza={tramo(f, d + 20, h)} />
		</Vert>
	);
};

const S0: React.FC<P> = ({d, h, e, s}) => <Toma escena={<OficinaMovil d={d} h={h} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} angulo={4} />;

const S0b: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscLiso color="#000" foco={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1.08]}}>
			<Vert cx={1150} cy={790} k={2.3}>
				<EscRincon />
				<Raton x={1150} y={928} tam={170} chilla={f >= d + 2} />
			</Vert>
		</Toma>
	);
};

/* ---------------- 1 · mira: la jarra que no llega ---------------- */

const S1: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const nivel = 37 * tramo(f, d + 4, pal(1, 'mayoría'), (t) => 1 - Math.pow(1 - t, 2.4));
	return (
		<Toma escena={<EscLiso color="#000" foco={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [0, -20]}}>
			<Vert cx={930} cy={520} k={1.5}>
				<Barra />
				<JarraVotos x={960} y={880} alto={720} nivel={nivel} />
			</Vert>
		</Toma>
	);
};

/* ---------------- 1 · Papen: dardos a la cara del rival y el ábaco de votos ---------------- */

const Diana: React.FC<{x: number; y: number; r: number}> = ({x, y, r}) => (
	<div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2}}>
		<svg viewBox="-100 -100 200 200" width={r * 2} height={r * 2} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
			{[98, 82, 66, 50].map((rr, i) => (
				<circle key={rr} r={rr} fill={i % 2 ? '#2f7a4a' : '#c8202a'} stroke={TINTA} strokeWidth={4} />
			))}
			{Array.from({length: 20}, (_, i) => (
				<line key={i} x1={0} y1={0} x2={Math.sin((i * Math.PI) / 10) * 98} y2={Math.cos((i * Math.PI) / 10) * 98} stroke="rgba(0,0,0,0.35)" strokeWidth={2} />
			))}
			<circle r={40} fill="#f1e6c8" stroke={TINTA} strokeWidth={4} />
		</svg>
		<Cara d={GENERAL.cabeza} tam={r * 0.82} cejas="enojado" boca="mueca" style={{position: 'absolute', left: r * 0.59, top: r * 0.52}} />
	</div>
);

const S2: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const tiros = [d + 4, d + 22, d + 40];
	const lanza = tiros.some((t) => f >= t - 4 && f < t + 4);
	return (
		<Toma escena={<Vert cx={700} cy={500} k={1.9}><EscSalonGenios humo={0.12} /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [0, 30]}} angulo={4}>
			<Diana x={600} y={520} r={260} />
			<Actor x={300} y={2330} alto={1180}>
				<Muneco ropa={PAPEN} pose={{...brazo(1, lanza ? {a: 150, c: 50} : {a: 120, c: 60}), md: 'agarra', ...manosEn([150, 560]), mi: 'relajada', cabeza: -8}} ojos="entrecerrados" cejas="enojado" boca="picara" />
			</Actor>
			{tiros.map((t, i) => (
				<DardoVolando key={i} x1={480} y1={1560} x2={[510, 690, 600][i]} y2={[430, 480, 660][i]} desde={t} llega={t + 8} />
			))}
		</Toma>
	);
};

const Abaco: React.FC<{x: number; y: number; ancho: number; cuenta: number}> = ({x, y, ancho, cuenta}) => {
	const k = ancho / 760;
	const filas = 5;
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: 620 * k}}>
			<div style={{position: 'absolute', inset: 0, border: `${16 * k}px solid #7a4a26`, outline: `${6 * k}px solid ${TINTA}`, borderRadius: 12 * k, background: 'rgba(30,20,14,0.35)'}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: -88 * k, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 62 * k, color: '#f6efdc', letterSpacing: 3 * k, textShadow: `0 ${5 * k}px 0 ${TINTA}`}}>VOTOS DE HITLER</div>
			{Array.from({length: filas}, (_, fi) => {
				const yy = (90 + fi * 105) * k;
				const movidas = Math.max(0, Math.min(8, cuenta * 8 - fi * 3));
				return (
					<React.Fragment key={fi}>
						<div style={{position: 'absolute', left: 16 * k, right: 16 * k, top: yy - 4 * k, height: 8 * k, background: '#c9a43a', border: `${2 * k}px solid ${TINTA}`}} />
						{Array.from({length: 8}, (_, b) => {
							const derecha = b >= 8 - movidas;
							const bx = derecha ? 760 - 70 - (7 - b) * 58 : 60 + b * 58;
							return <div key={b} style={{position: 'absolute', left: bx * k, top: yy - 26 * k, width: 54 * k, height: 52 * k, borderRadius: '50%', background: ['#c8202a', '#e0b23a', '#2f7a4a', '#2f4f8f', '#7a3a8a'][fi], border: `${5 * k}px solid ${TINTA}`}} />;
						})}
					</React.Fragment>
				);
			})}
		</div>
	);
};

const S2b: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<Vert cx={700} cy={500} k={1.9}><EscSalonGenios humo={0.12} /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.12], y: [40, 60]}}>
			<Abaco x={540} y={380} ancho={820} cuenta={tramo(f, d + 2, h, (t) => t)} />
			<Actor x={540} y={2420} alto={1200}>
				<Muneco ropa={PAPEN} pose={{...manosFrente([110, 330], [300, 330]), mi: 'senala', md: 'abierta', cabeza: 6}} ojos="grandes" cejas="arrogante" boca="sonrisaGrande" />
			</Actor>
		</Toma>
	);
};

/* ---------------- 2 · la burla: Hindenburg y el cartero ---------------- */

const S3: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Vert cx={1090} cy={470} k={1.85}><CuadroHindenburgSello brillo={0.4} /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [30, 60]}} angulo={9} />
);

const HITLER_CARTERO = {...HITLER_TRAJE, cabeza: {...HITLER_TRAJE.cabeza, gorra: 'militar' as const, colorGorra: '#2f4f8f', colorBanda: '#e0b23a'}};

const BolsaCartero: React.FC = () => (
	<g>
		<line x1={130} y1={300} x2={300} y2={560} stroke={TINTA} strokeWidth={30} strokeLinecap="round" />
		<line x1={130} y1={300} x2={300} y2={560} stroke="#7a4a26" strokeWidth={18} strokeLinecap="round" />
		<rect x={220} y={520} width={170} height={150} rx={18} fill="#8a5a32" stroke={TINTA} strokeWidth={9} />
		<path d="M 220 540 L 390 540 L 390 590 Q 305 620 220 590 Z" fill="#7a4a26" stroke={TINTA} strokeWidth={7} />
		{[0, 1, 2].map((i) => (
			<rect key={i} x={238 + i * 40} y={480 + (i % 2) * 10} width={70} height={46} fill="#f4ecd6" stroke={TINTA} strokeWidth={5} transform={`rotate(${-10 + i * 10} ${270 + i * 40} 500)`} />
		))}
	</g>
);

const S4: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Vert cx={960} cy={540} k={1.8}><EscLiso color="#c99a2a" luz="255,240,200" /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [-40, -60]}} angulo={-12}>
		{/* sobres gigantes en el suelo para que se vea diminuto */}
		{[[160, 1180, -14], [820, 1060, 12], [880, 1560, -6], [140, 1640, 9]].map(([x, y, r], i) => (
			<div key={i} style={{position: 'absolute', left: x - 170, top: y - 110, width: 340, height: 220, background: '#f4ecd6', border: `8px solid ${TINTA}`, transform: `rotate(${r}deg)`}}>
				<svg viewBox="0 0 100 62" style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}}>
					<polyline points="0,0 50,34 100,0" fill="none" stroke={TINTA} strokeWidth={2.4} />
				</svg>
			</div>
		))}
		<Actor x={540} y={1000} alto={620}>
			<Muneco ropa={HITLER_CARTERO} pose={{...manosEn([150, 560], [300, 560]), mi: 'agarra', md: 'agarra', cabeza: -10, cuerpo: 6}} objPecho={<BolsaCartero />} ojos="grandes" cejas="preocupado" boca="mueca" camina={0.6} />
		</Actor>
	</Toma>
);

/* ---------------- 2 · tres de once (mesa vista desde arriba) y la jaula ---------------- */

/** mesa del gabinete desde arriba: 11 sillas, 3 marrones (los nazis) y 8 grises */
export const MARRONES = [1, 6, 9];
const posSilla = (i: number): [number, number] => (i === 0 ? [540, 420] : i <= 5 ? [270, 560 + (i - 1) * 210] : [810, 560 + (i - 6) * 210]);

const MesaOnce: React.FC<{marca?: number; y0?: number; escala?: number}> = ({marca = 0, y0 = 0, escala = 1}) => (
	<div style={{position: 'absolute', inset: 0, transform: `translateY(${y0}px) scale(${escala})`, transformOrigin: '50% 0'}}>
		<div style={{position: 'absolute', left: 380, top: 480, width: 320, height: 1080, background: 'linear-gradient(90deg, #2a5a3a, #3a6a4a 50%, #2a5a3a)', border: `12px solid #4a2c1a`, outline: `6px solid ${TINTA}`, borderRadius: 26}} />
		{Array.from({length: 11}, (_, i) => {
			const [x, y] = posSilla(i);
			const marron = MARRONES.includes(i);
			const giro = i === 0 ? 0 : i <= 5 ? -90 : 90;
			return (
				<div key={i} style={{position: 'absolute', left: x - 80, top: y - 80, width: 160, height: 160, transform: `rotate(${giro}deg) scale(${marron ? 1 + 0.12 * marca : 1})`, filter: marron && marca > 0 ? `drop-shadow(0 0 ${22 * marca}px rgba(255,170,90,0.95))` : marca > 0 ? `brightness(${1 - 0.4 * marca})` : undefined}}>
					<div style={{position: 'absolute', left: 14, top: 0, width: 132, height: 40, background: marron ? '#7a5232' : '#8a8a92', border: `8px solid ${TINTA}`, borderRadius: 14}} />
					<div style={{position: 'absolute', left: 14, top: 44, width: 132, height: 110, background: marron ? '#8a6040' : '#9a9aa2', border: `8px solid ${TINTA}`, borderRadius: 18}} />
				</div>
			);
		})}
	</div>
);

const S5: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const marca = tramo(f, antes(pal(6, 'tres')), pal(6, 'tres') + 8);
	return (
		<Toma escena={<Vert cx={960} cy={540} k={1.8}><EscLiso color="#2a1a10" luz="255,214,150" /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}}>
			<MesaOnce marca={marca} y0={-60} />
			<div style={{position: 'absolute', left: 540 - 230, top: 1580, width: 460, padding: '10px 0', textAlign: 'center', background: '#efe8d4', border: `8px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 92, color: '#2a2218', transform: `scale(${pop(f, pal(6, 'tres'))})`}}>
				<span style={{color: '#8a4a22'}}>3</span> DE 11
			</div>
		</Toma>
	);
};

const S6: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const forma = tramo(f, d - 2, d + 14);
	const RONDA = [
		{r: MINISTRO, x: 170, inc: 14},
		{r: SENOR_3, x: 350, inc: 7},
		{r: BANQUERO, x: 730, inc: -7},
		{r: FUNCIONARIO, x: 910, inc: -14},
	];
	return (
		<Toma escena={<Vert cx={700} cy={500} k={1.9}><EscSalonGenios humo={0.14} /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.07], y: [20, 40]}} angulo={-4}>
			<Actor x={540} y={1500} alto={520}>
				<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno'}} ojos="mirandoLado" cejas="enojado" boca="seria" />
			</Actor>
			{RONDA.map(({r, x, inc}, i) => {
				const lado = x < 540 ? 1 : -1;
				const brazos = forma > 0 ? {...brazo(1, alcanzar(1, 200 + lado * 120 + 60, -40)), ...brazo(-1, alcanzar(-1, 200 + lado * 120 - 60, -40)), mi: 'abierta' as const, md: 'abierta' as const} : {};
				return (
					<Actor key={i} x={x + lado * 50 * (1 - forma)} y={1540} alto={1000} rot={inc * forma}>
						<Muneco ropa={r} pose={brazos} ojos="feliz" cejas="arrogante" boca="sonrisa" semilla={i} />
					</Actor>
				);
			})}
			<svg width={340} height={220} viewBox="0 0 300 200" style={{position: 'absolute', left: 370, top: 330, opacity: forma, overflow: 'visible'}}>
				<path d="M 40 200 Q 150 40 260 200" stroke="#c9a43a" strokeWidth={18} fill="none" />
				<circle cx={150} cy={70} r={36} stroke="#c9a43a" strokeWidth={16} fill="none" />
			</svg>
		</Toma>
	);
};

/* ---------------- 3 · arranca el reloj ---------------- */

const CalendarioDia: React.FC<{x: number; y: number; ancho: number; mes: string; dia: string; anio?: string; caida?: number}> = ({x, y, ancho, mes, dia, anio = '1933', caida = 0}) => {
	const k = ancho / 300;
	const hoja = (contenido: React.ReactNode, estilo?: React.CSSProperties) => (
		<div style={{position: 'absolute', inset: 0, background: '#f6efdc', border: `${8 * k}px solid ${TINTA}`, borderRadius: 8 * k, textAlign: 'center', fontFamily: CONDENSADA, color: '#2a2218', overflow: 'hidden', ...estilo}}>{contenido}</div>
	);
	return (
		<div style={{position: 'absolute', left: x - ancho / 2, top: y, width: ancho, height: ancho * 1.1, filter: `drop-shadow(${10 * k}px ${12 * k}px 0 rgba(0,0,0,0.35))`}}>
			{hoja(
				<>
					<div style={{background: '#a8262e', color: '#f6efdc', fontSize: 52 * k, letterSpacing: 4 * k, borderBottom: `${6 * k}px solid ${TINTA}`, lineHeight: 1.2}}>{mes}</div>
					<div style={{fontSize: 150 * k, lineHeight: 1.15}}>{dia}</div>
					<div style={{fontSize: 40 * k, marginTop: -10 * k}}>{anio}</div>
				</>,
			)}
			{caida > 0 && caida < 1 && hoja(null, {transform: `translateY(${caida * 260 * k}px) rotate(${caida * 40}deg)`, opacity: 1 - caida})}
		</div>
	);
};

const S7: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sienta = tramo(f, d + 4, pal(7, 'canciller'));
	return (
		<Toma escena={<Vert cx={1000} cy={420} k={1.9}><EscOficinaBerlin /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} golpes={[[antes(pal(8, 'Sin', 1)), 0.12]]}>
			<CalendarioDia x={830} y={270} ancho={290} mes="ENERO" dia="30" />
			<Silla x={480} y={1660} alto={520} etiqueta="CANCILLER" color="#6a3e26" />
			<Actor x={480} y={1630 - 150 * sienta} alto={1000}>
				<Muneco ropa={HITLER_CANCILLER} pose={{agacha: 0.55 * sienta, ...manosEn([150, 560], [250, 560]), mi: 'puno', md: 'puno', pi: 3 + 12 * sienta, pd: 3 + 12 * sienta}} ojos="entrecerrados" cejas="arrogante" boca="seria" />
			</Actor>
		</Toma>
	);
};

const S8: React.FC<P> = ({d, h, e, s}) => {
	const arranca = pal(8, 'ganar');
	return (
		<Toma escena={<Vert cx={960} cy={540} k={1.8}><EscLiso color="#2e3742" /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}} golpes={[[antes(pal(8, 'Sin', 2)), 0.12]]} angulo={4}>
			<Actor x={460} y={2050} alto={1500}>
				<Muneco ropa={PAPEN} pose={{...brazo(1, alcanzar(1, 330, 380)), md: 'agarra', ...manosEn([150, 560]), mi: 'abierta', cabeza: -6}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
			</Actor>
			<Cronometro x={790} y={860} tam={330} desde={arranca} />
		</Toma>
	);
};

/* ---------------- 4 · escalada en tres (calendario y cronómetro encima) ---------------- */

const FECHAS: [number, string, string][] = [
	[9, 'FEBRERO', '27'],
	[10, 'MARZO', '5'],
	[11, 'MARZO', '23'],
];

const Escalada: React.FC = () => {
	const f = useCurrentFrame();
	let k = 0;
	FECHAS.forEach(([i], j) => {
		if (f >= ini(i)) k = j;
	});
	const [i, mes, dia] = FECHAS[k];
	const caida = k > 0 ? tramo(f, ini(i), ini(i) + 8) : 0;
	return (
		<>
			<CalendarioDia x={190} y={280} ancho={230} mes={mes} dia={dia} caida={caida} />
			<Cronometro x={890} y={420} tam={230} desde={pal(8, 'ganar')} />
		</>
	);
};

const S9: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Vert cx={960} cy={540} k={1.85}><EscIncendio /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} encima={<Escalada />}>
		<Actor x={540} y={2150} alto={1350}>
			<div style={{width: '100%', height: '100%', filter: 'brightness(0.35) sepia(0.6) saturate(2) hue-rotate(-20deg)'}}>
				<Muneco ropa={HITLER_CANCILLER} pose={manosEn([150, 560], [250, 560])} ojos="entrecerrados" cejas="enojado" boca="seria" parpadea={false} />
			</div>
		</Actor>
	</Toma>
);

const S10: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const nivel = 43.9 * tramo(f, d + 4, pal(10, 'mayoría'), (t) => 1 - Math.pow(1 - t, 2.2));
	return (
		<Toma escena={<EscLiso color="#000" foco={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} angulo={6} encima={<Escalada />}>
			<Vert cx={1060} cy={500} k={1.6}>
				<Barra />
				<div style={{position: 'absolute', left: 1220, top: 220, width: 420, height: 700, opacity: 0.6}}>
					<Silueta x={210} y={700} alto={720} ropa={UNIFORME_MARRON} tono={0} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno'}} />
				</div>
				<div style={{position: 'absolute', left: 1360, top: 700, width: 220, height: 170, background: '#5a4a3a', border: `7px solid ${TINTA}`}}>
					<div style={{position: 'absolute', left: 50, top: -7, width: 120, height: 14, background: TINTA}} />
					<div style={{fontFamily: CONDENSADA, fontSize: 40, color: '#e9e4d6', textAlign: 'center', marginTop: 50}}>URNA</div>
				</div>
				<JarraVotos x={900} y={880} alto={720} nivel={nivel} />
			</Vert>
		</Toma>
	);
};

const Sala: React.FC<{paredes: number}> = ({paredes}) => (
	<div style={{position: 'absolute', inset: 0, background: '#141418'}}>
		<div style={{position: 'absolute', inset: 0, opacity: paredes, background: 'linear-gradient(180deg, #5a4a38 0%, #3a2e22 60%)'}}>
			{Array.from({length: 7}, (_, i) => (
				<div key={i} style={{position: 'absolute', left: 40 + i * 270, top: 30, width: 200, height: 400, border: '8px solid rgba(0,0,0,0.3)', borderRadius: '100px 100px 6px 6px'}} />
			))}
		</div>
	</div>
);

const S11: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const paredes = 1 - tramo(f, pal(11, 'vota'), h + 4);
	return (
		<Toma escena={<EscLiso color="#000" foco={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} angulo={11} encima={<Escalada />}>
			<Vert cx={960} cy={600} k={1.8}>
				<Sala paredes={paredes} />
				<div style={{position: 'absolute', inset: 0, filter: 'saturate(0.5)'}}>
					<Bancadas grupos={[{color: '#6a6a72', n: 40, levanta: pal(11, 'vota')}]} />
				</div>
			</Vert>
			{/* Hitler en la tribuna, desde abajo */}
			<Actor x={540} y={2080} alto={1250}>
				<Muneco ropa={HITLER_CANCILLER} pose={{...manosEn([120, 600], [280, 600]), mi: 'puno', md: 'puno'}} ojos="entrecerrados" cejas="enojado" boca="seria" />
			</Actor>
			<div style={{position: 'absolute', left: 260, top: 1640, width: 560, height: 320, background: 'linear-gradient(180deg, #5a3a22, #2e1e12)', border: `10px solid ${TINTA}`, borderRadius: 10}} />
		</Toma>
	);
};

/* ---------------- 5 · el giro ---------------- */

const S12: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#000" foco={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [-20, -40]}} angulo={-8}>
		<Vert cx={960} cy={560} k={1.8}>
			<Sala paredes={0.7} />
			<Bancadas grupos={[{color: '#3a4a6a', n: 30, levanta: pal(13, 'Votan'), entusiasmo: true}]} filas={3} y0={520} />
		</Vert>
		<Actor x={540} y={1840} alto={980}>
			<Muneco
				ropa={PAPEN}
				pose={useCurrentFrame() >= pal(13, 'Votan') ? {...brazo(1, {a: 160, c: 10}), md: 'abierta', ...manosEn([150, 560]), mi: 'agarra'} : {...manosFrente([170, 520], [230, 520]), mi: 'agarra', md: 'agarra'}}
				ojos="feliz"
				cejas="arrogante"
				boca="sonrisaGrande"
			/>
		</Actor>
	</Toma>
);

const S13: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sombra = tramo(f, d + 4, d + 30);
	return (
		<Toma escena={<EscLiso color="#000" foco={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08]}} angulo={9}>
			<Vert cx={1200} cy={640} k={1.9}>
				<EscRincon />
				<ParlamentoMini x={1240} y={930} ancho={420} />
				<div style={{position: 'absolute', left: 700 + 300 * (1 - sombra), top: -60, width: 900, height: 1100, opacity: 0.6 * sombra}}>
					<Silueta x={450} y={1100} alto={1150} ropa={HITLER_CANCILLER} tono={0} pose={manosEn([150, 560], [250, 560])} />
				</div>
			</Vert>
		</Toma>
	);
};

/* ---------------- 6 · el mecanismo: de una silla marrón, un cable hasta Prusia ---------------- */

const S14: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Vert cx={960} cy={540} k={1.8}><EscLiso color="#2a1a10" luz="255,214,150" /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.0]}}>
		<MesaOnce marca={0.6} y0={-60} />
	</Toma>
);

/** Alemania en 1932, estilizada: Prusia (el estado más grande) ocupa el norte, el este y la Renania; Prusia Oriental, aparte */
const ALEMANIA = 'M 180 140 L 300 60 L 330 40 L 380 90 L 520 60 L 700 40 L 680 70 L 700 170 L 820 420 L 760 470 L 700 450 L 620 540 L 640 610 L 580 700 L 380 760 L 240 720 L 190 640 L 180 600 L 130 420 L 110 300 Z';
const PRUSIA = 'M 180 140 L 300 60 L 330 40 L 380 90 L 520 60 L 700 40 L 680 70 L 700 170 L 820 420 L 760 470 L 700 430 L 620 400 L 520 380 L 430 330 L 340 380 L 300 470 L 240 560 L 175 610 L 130 420 L 110 300 Z';
const PRUSIA_ORIENTAL = 'M 760 60 L 960 20 L 985 120 L 830 160 L 770 110 Z';

const MapaPrusia: React.FC<{y: number; luz: number}> = ({y, luz}) => {
	const color = `rgb(${Math.round(110 + 120 * luz)},${Math.round(110 + 80 * luz)},${Math.round(118 + 10 * luz)})`;
	return (
		<svg width={1000} height={800} viewBox="0 0 1000 800" style={{position: 'absolute', left: 40, top: y, overflow: 'visible'}}>
			<path d={ALEMANIA} fill="#4a4a52" stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
			<path d={PRUSIA} fill={color} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" style={{filter: luz > 0 ? `drop-shadow(0 0 ${30 * luz}px rgba(255,200,90,0.7))` : undefined}} />
			<path d={PRUSIA_ORIENTAL} fill={color} stroke={TINTA} strokeWidth={9} strokeLinejoin="round" />
			<text x={440} y={190} textAnchor="middle" fill="#f6efdc" fontFamily={CONDENSADA} fontSize={96} letterSpacing={8} stroke={TINTA} strokeWidth={6} paintOrder="stroke">PRUSIA</text>
		</svg>
	);
};

/** casco de policía (sin símbolos) */
const Casco: React.FC<{x: number; y: number; tam: number; desde: number}> = ({x, y, tam, desde}) => {
	const f = useCurrentFrame();
	const p = pop(f, desde, 6);
	if (p <= 0) return null;
	return (
		<svg width={tam} height={tam * 0.8} viewBox="0 0 100 80" style={{position: 'absolute', left: x - tam / 2, top: y - tam * 0.4, transform: `scale(${p})`, overflow: 'visible'}}>
			<path d="M 12 60 Q 12 10 50 8 Q 88 10 88 60 Z" fill="#2a3a5a" stroke={TINTA} strokeWidth={6} />
			<rect x={4} y={56} width={92} height={14} rx={6} fill="#1a2238" stroke={TINTA} strokeWidth={5} />
			<path d="M 30 26 Q 40 18 50 18" stroke="rgba(255,255,255,0.35)" strokeWidth={6} fill="none" strokeLinecap="round" />
		</svg>
	);
};

const S15: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const policia = pal(16, 'policía');
	const cable = tramo(f, d + 6, policia, (t) => t);
	const luz = tramo(f, policia, policia + 12);
	const silla = posSilla(MARRONES[2]);
	// la mesa arriba (más chica) y el mapa abajo; el cable baja de una silla marrón
	const sx = 540 + (silla[0] - 540) * 0.4;
	const sy = 200 + silla[1] * 0.4;
	const largo = 1100;
	const camino = `M ${sx} ${sy} C ${sx + 220} ${sy + 120}, 980 760, 820 900 S 560 960, 600 1020`;
	const CASCOS: [number, number][] = [[200, 990], [170, 1160], [690, 870], [780, 990], [890, 820], [960, 1010], [300, 860]];
	return (
		<Toma escena={<Vert cx={960} cy={540} k={1.8}><EscLiso color="#14161c" luz="200,210,230" /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04], y: [0, -20]}}>
			<div style={{position: 'absolute', inset: 0, transform: 'translateY(200px) scale(0.4)', transformOrigin: '50% 0'}}>
				<MesaOnce marca={1} />
			</div>
			<MapaPrusia y={760} luz={luz} />
			<svg width={1080} height={1920} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
				<path d={camino} stroke={TINTA} strokeWidth={22} fill="none" strokeLinecap="round" strokeDasharray={largo} strokeDashoffset={largo * (1 - cable)} />
				<path d={camino} stroke="#ffd84a" strokeWidth={10} fill="none" strokeLinecap="round" strokeDasharray={largo} strokeDashoffset={largo * (1 - cable)} style={{filter: 'drop-shadow(0 0 14px rgba(255,216,74,0.9))'}} />
			</svg>
			{CASCOS.map(([x, y], i) => (
				<Casco key={i} x={x} y={y} tam={110} desde={policia + 2 + i * 3} />
			))}
		</Toma>
	);
};

/* ---------------- 7 · el remate: tres imágenes del video largo y la oficina final ---------------- */

const T1: React.FC<P> = ({d, h, e, s}) => <Toma escena={<Vert cx={990} cy={470} k={1.9}><CuadroTiroTecho disparo={d + 5} /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} golpes={[[d + 5, 0.06]]} />;
const T2: React.FC<P> = ({d, h, e, s}) => <Toma escena={<Vert cx={960} cy={520} k={1.9}><CuadroJuezDeportar rompe={d + 6} /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} />;
const T3: React.FC<P> = ({d, h, e, s}) => <Toma escena={<Vert cx={1090} cy={470} k={1.85}><CuadroHindenburgSello brillo={0.5} /></Vert>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}} angulo={8} />;

/** fin de la voz + 1,2 s: el sello de REAL ocupa el último segundo */
export const FIN_VIDEO = fin(18) + 36;
const SELLO_REAL = FIN_VIDEO - 30;

const OficinaFinal: React.FC<{d: number}> = ({d}) => {
	const f = useCurrentFrame();
	const e = mezclaEnc(FINAL, VENTANA, tramo(f, pal(18, 'contratado', 2), FIN_VIDEO - 8));
	return (
		<Vert {...e}>
			<OficinaPapen desliza={1} palmadas={false} papen={false} amigo={false} hitler sillaVacia />
		</Vert>
	);
};

const S16: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={<OficinaFinal d={d} />}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1, 1]}}
		angulo={7}
		encima={<Sello x={540} y={880} texto="REAL" desde={SELLO_REAL} color="#1f9d48" tam={190} rot={-10} solido />}
	/>
);

const PLANOS: Plano[] = [
	{n: 'oficina', d: 0, e: 'corte', C: S0},
	{n: 'raton', d: antes(pal(0, 'chillando')), e: 'latigoDer', C: S0b},
	{n: 'jarra', d: ini(1), e: 'latigoIzq', C: S1},
	{n: 'dardos', d: ini(2), e: 'latigoDer', C: S2},
	{n: 'abaco', d: antes(pal(2, 'necesitaba')), e: 'zoom', C: S2b},
	{n: 'hindenburg', d: ini(3), e: 'latigoArriba', C: S3},
	{n: 'cartero', d: antes(pal(4, 'cartero')), e: 'zoom', C: S4},
	{n: 'mesa', d: ini(5), e: 'latigoDer', C: S5},
	{n: 'jaula', d: antes(pal(6, 'Lo')), e: 'zoom', C: S6},
	{n: 'canciller', d: ini(7), e: 'latigoIzq', C: S7},
	{n: 'cronometro', d: antes(pal(8, 'Sin', 2)), e: 'zoom', C: S8},
	{n: 'incendio', d: ini(9), e: 'latigoDer', C: S9},
	{n: 'votos', d: ini(10), e: 'latigoIzq', C: S10},
	{n: 'ley', d: ini(11), e: 'latigoDer', C: S11},
	{n: 'conservadores', d: ini(12), e: 'latigoIzq', C: S12},
	{n: 'rincon', d: antes(ini(14)), e: 'latigoDer', C: S13},
	{n: 'rodeado', d: ini(15), e: 'zoom', C: S14},
	{n: 'prusia', d: antes(pal(16, 'Pero')), e: 'latigoArriba', C: S15},
	{n: 't1', d: ini(17), e: 'latigoDer', C: T1},
	{n: 't2', d: antes(pal(17, 'todavía')), e: 'latigoIzq', C: T2},
	{n: 't3', d: antes(pal(17, 'está')), e: 'latigoDer', C: T3},
	{n: 'final', d: ini(18) - 4, e: 'zoom', C: S16},
];

const WHOOSH: [string, number, number][] = PLANOS.filter((p) => p.e && p.e.startsWith('latigo')).map((p) => ['whoosh', p.d - 5, 0.35]);

export const SONIDOS: [string, number, number][] = [
	...WHOOSH,
	['chillido', antes(pal(0, 'chillando')) + 2, 0.9],
	['burbujas', ini(1) + 4, 0.6],
	['objeto', ini(2) + 12, 0.7],
	['objeto', ini(2) + 30, 0.7],
	['objeto', ini(2) + 48, 0.7],
	['tic', antes(pal(2, 'necesitaba')) + 4, 0.6],
	['tic', antes(pal(2, 'necesitaba')) + 12, 0.6],
	['tic', antes(pal(2, 'necesitaba')) + 20, 0.6],
	['tintineo', ini(3) + 6, 0.6],
	['sobres', antes(pal(4, 'cartero')) + 2, 0.7],
	['ding', pal(6, 'tres'), 0.7],
	['cierre', antes(pal(6, 'Lo')) + 6, 0.6],
	['clic', pal(8, 'ganar'), 1.0],
	['fuego', ini(9), 0.8],
	['burbujas', ini(10) + 4, 0.6],
	['aplausos', pal(13, 'Votan'), 0.5],
	['dundun', antes(ini(14)) + 8, 0.6],
	['chispas', antes(pal(16, 'Pero')) + 6, 0.6],
	['pop', pal(16, 'policía') + 2, 0.6],
	['disparo', ini(17) + 5, 0.6],
	['crack', antes(pal(17, 'todavía')) + 6, 0.8],
	['tintineo', antes(pal(17, 'está')) + 4, 0.6],
	['sello', SELLO_REAL, 1.0],
];

export const Historia: React.FC = () => <Montaje planos={PLANOS} fin={FIN_VIDEO} />;

export {TITULAR, clamp, interpolate};
