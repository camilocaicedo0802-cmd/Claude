import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Bombilla} from '../componentes/Efectos';
import {Actor, Muneco, Pose, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {GolpeSello, SelloGoma} from '../componentes/Recurrentes';
import {Toma} from '../componentes/Toma';
import {Lupa, Sello} from '../componentes/Utileria';
import {CONDENSADA} from '../fuentes';
import {Montaje, P, Plano, TINTA, antes, clamp, fin, golpeCam, ini, pal, pop, tramo} from './base';
import {brazo} from './compartidas';
import {Periodico} from './utileria_c89';
import {
	CH_ALTO,
	CH_DESCONFIADO,
	CH_DORMIDO,
	CH_GORDO,
	CH_LUPA,
	CabezaBalanza,
	Cartel,
	Certificado,
	ESPOSA,
	EscCafe,
	EscCasa,
	EscComisaria,
	EscHotelLujo,
	EscParisAtardecer,
	EscPasillo,
	Escritorio,
	LUSTIG,
	POISSON,
	POISSON_FRAC,
	POLICIA_FR,
	PapelMembrete,
	PlanoTorre,
	SobreGordo,
	TazaCafe,
	TorreEiffel,
	Vagon,
	Vapor,
} from './utileria_eiffel';

/*
 * Short «El hombre que vendió la Torre Eiffel» (1080x1920, 30 fps). Sin cortes secos: barridos y zooms.
 */

/* ---------------- piezas ---------------- */

/** cámara vertical: lleva el punto (wx, wy) del mundo a la altura `sy` de la pantalla, con escala s y sin ver bordes */
const centrarV = (wx: number, wy: number, s: number, sy = 960) => {
	const mx = Math.max(0, (s - 1) * 540);
	const my = Math.max(0, (s - 1) * 960);
	return {s, x: Math.max(-mx, Math.min(mx, -(wx - 540) * s)), y: Math.max(-my, Math.min(my, sy - 960 - (wy - 960) * s))};
};

/** bastón en la mano (SVG en coordenadas de la mano) */
const Baston: React.FC<{rot?: number}> = ({rot = 0}) => (
	<g transform={`rotate(${rot} 0 36)`}>
		<line x1={0} y1={20} x2={0} y2={420} stroke={TINTA} strokeWidth={20} strokeLinecap="round" />
		<line x1={0} y1={20} x2={0} y2={420} stroke="#3a2414" strokeWidth={11} strokeLinecap="round" />
		<path d="M 0 30 Q 0 -30 -50 -20" stroke="#c9a43a" strokeWidth={16} fill="none" strokeLinecap="round" />
	</g>
);

/** dedo sobre los labios («ni una palabra»): un dedo vertical que cruza la boca */
const DedoLabios: React.FC<{x: number; y: number; tam: number; desde: number}> = ({x, y, tam, desde}) => {
	const f = useCurrentFrame();
	const p = pop(f, desde, 6);
	if (p <= 0) return null;
	return (
		<div style={{position: 'absolute', left: x - tam * 0.18, top: y - tam * 0.55 + (1 - p) * tam * 0.4, width: tam * 0.36, height: tam * 1.1, opacity: Math.min(1, p * 1.5)}}>
			<div style={{position: 'absolute', left: 0, top: 0, width: '100%', height: '62%', background: '#ffffff', border: `${tam * 0.05}px solid ${TINTA}`, borderRadius: tam * 0.2}} />
			<div style={{position: 'absolute', left: '-40%', top: '50%', width: '180%', height: '55%', background: '#ffffff', border: `${tam * 0.05}px solid ${TINTA}`, borderRadius: tam * 0.3}} />
		</div>
	);
};

/** cara a la altura de la boca de un Actor: coordenadas en el cuadro */
const bocaDe = (x: number, y: number, alto: number) => ({bx: x, by: y - alto * (880 / 900) + alto * (258 / 900)});

/* ---------------- 0 · escena imposible ---------------- */

const SIGNO = {x: 560, y: 800, ancho: 520};

const ParisTorre: React.FC<{d: number; vendida: number; segundo: number}> = ({d, vendida, segundo}) => {
	const f = useCurrentFrame();
	const orbita = (f - d) * 3;
	return (
		<>
			<EscParisAtardecer desplaza={orbita} />
			<TorreEiffel x={540} y={1700} alto={1550} />
			<Cartel x={SIGNO.x} y={SIGNO.y} ancho={SIGNO.ancho} />
			{f >= vendida && <Sello x={SIGNO.x} y={SIGNO.y + 90} texto="VENDIDA" desde={vendida} color="#d6262e" tam={90} rot={-14} solido />}
			{f >= segundo && (
				<div style={{position: 'absolute', inset: 0, transform: `scale(${1 + 0.25 * Math.max(0, 1 - (f - segundo) / 5)})`, transformOrigin: `${SIGNO.x}px ${SIGNO.y + 80}px`}}>
					<Cartel x={SIGNO.x + 20} y={SIGNO.y + 40} ancho={SIGNO.ancho} rot={5} />
				</div>
			)}
		</>
	);
};

const E0: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<ParisTorre d={d} vendida={antes(pal(0, 'vendió'))} segundo={antes(ini(1))} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.15], x: [-30, 30], y: [60, 120], r: [-2, 1]}} />
);

/** Lustig al pie de la torre, guiña un ojo */
const E0b: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscParisAtardecer desplaza={(f - d) * 3 + 300} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12], y: [0, 30]}} angulo={6}>
			<div style={{position: 'absolute', left: -700, top: -900, width: 2480, height: 2700}}>
				<TorreEiffel x={1240} y={2700} alto={2700} />
			</div>
			<Actor x={540} y={1960} alto={1500}>
				<Muneco ropa={LUSTIG} pose={{...brazo(1, alcanzar(1, 330, 520)), md: 'agarra', ...manosEn([150, 560]), mi: 'relajada', cabeza: -6}} objDer={<Baston rot={-10} />} ojos={f >= d + 6 ? 'guinoX' : 'normal'} cejas="arrogante" boca="picara" />
			</Actor>
		</Toma>
	);
};

/* ---------------- 1 · mira: óxido, pintor, plano «temporal» ---------------- */

const E1: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscParisAtardecer />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.0]}} camFn={(ff) => golpeCam(ff, antes(pal(2, 'oxidada')), {s: 1.1, x: 0, y: 0}, {s: 1.6, x: 0, y: 280})}>
			<TorreEiffel x={540} y={1800} alto={1650} oxido={tramo(f, antes(pal(2, 'oxidada')), pal(2, 'oxidada') + 12)} />
		</Toma>
	);
};

const E1b: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const largo = tramo(f, d + 2, h, (u) => u);
	return (
		<Toma escena={<EscParisAtardecer />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.2, 1.28], y: [100, 140]}}>
			<div style={{position: 'absolute', left: -500, top: -300, width: 2080, height: 2700}}>
				<TorreEiffel x={1040} y={2700} alto={2600} oxido={1} />
			</div>
			{/* la cuerda y el pintor */}
			<div style={{position: 'absolute', left: 380, top: 0, width: 8, height: 900, background: '#c9b48a'}} />
			<Actor x={384} y={1440} alto={760}>
				<Muneco ropa={{...CH_DORMIDO, cabeza: {...CH_DORMIDO.cabeza, gorra: 'boina', colorGorra: '#f4f4f0'}, casaca: '#f4f4f0', casacaSombra: '#d8d8d0', pantalon: '#f4f4f0'}} pose={{...brazo(1, alcanzar(1, 370, 330)), md: 'agarra', ...brazo(-1, alcanzar(-1, 30, 400)), mi: 'agarra'}} ojos="grandes" cejas="preocupado" boca="o" />
			</Actor>
			{/* la factura que se alarga como un pergamino */}
			<div style={{position: 'absolute', left: 620, top: 520, width: 340, height: 160 + 1000 * largo, background: '#fbf6e8', border: `8px solid ${TINTA}`, padding: 20, boxSizing: 'border-box', overflow: 'hidden', fontFamily: CONDENSADA, color: TINTA}}>
				<div style={{fontSize: 52, textAlign: 'center'}}>FACTURA</div>
				{Array.from({length: 16}, (_, i) => (
					<div key={i} style={{display: 'flex', justifyContent: 'space-between', fontSize: 30, margin: '10px 0'}}>
						<span>Pintura</span>
						<span>{(i + 1) * 1000} F</span>
					</div>
				))}
			</div>
		</Toma>
	);
};

const E1c: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<PlanoTorre />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [0, -30]}} encima={<Sello x={540} y={1450} texto="TEMPORAL: 20 AÑOS" desde={antes(pal(2, 'desmontada'))} color="#d6262e" tam={66} rot={-10} solido />} />
);

/* ---------------- 1 · Lustig en el café (y su idea) ---------------- */

const Cafe: React.FC<{guino?: number}> = ({guino}) => {
	const f = useCurrentFrame();
	return (
		<>
			<EscCafe />
			<div style={{position: 'absolute', left: 120, top: 1240, width: 840, height: 60, background: '#c9c4b8', border: `8px solid ${TINTA}`, borderRadius: 30}} />
			<Actor x={420} y={1900} alto={1350}>
				<Muneco ropa={LUSTIG} pose={{...manosFrente([110, 420], [290, 420]), mi: 'agarra', md: 'agarra', cabeza: guino !== undefined && f >= guino ? -10 : 4}} ojos={guino !== undefined && f >= guino ? 'guinoX' : 'mirandoLado'} cejas="arrogante" boca={guino !== undefined && f >= guino ? 'picara' : 'seria'} />
			</Actor>
			<Periodico x={720} y={760} ancho={560} titular="¿CUÁNTO NOS CUESTA LA TORRE?" fecha="1925" nombre="Le Journal" rot={6} />
			<TazaCafe x={880} y={1250} />
		</>
	);
};

const E2: React.FC<P> = ({d, h, e, s}) => <Toma escena={<Cafe />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [0, 40]}} />;

const E3: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const divide = tramo(f, d + 4, d + 14);
	const lado = (etiqueta: string, color: string, x0: number) => (
		<div style={{position: 'absolute', left: x0, top: 0, width: 540, height: 1100, overflow: 'hidden', background: x0 === 0 ? '#3a4a6a' : '#5a3a4a', borderRight: x0 === 0 ? `8px solid ${TINTA}` : undefined}}>
			<TorreEiffel x={270} y={1040} alto={880} />
			<div style={{position: 'absolute', left: 90, top: 640, padding: '8px 24px', background: '#f6efdc', border: `7px solid ${TINTA}`, borderRadius: 12, fontFamily: CONDENSADA, fontSize: 64, color, transform: 'rotate(-8deg)'}}>{etiqueta}</div>
		</div>
	);
	return (
		<Toma escena={<EscCafe />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}}>
			<div style={{position: 'absolute', left: 0, top: 110, width: 1080, height: 1100, opacity: divide, transform: `translateY(${(1 - divide) * -80}px)`}}>
				{lado('DESMONTAR', '#1f2a4a', 0)}
				{lado('1.000.000 F', '#1f7a3a', 540)}
			</div>
			<Actor x={500} y={2480} alto={1250}>
				<Muneco ropa={LUSTIG} pose={{...manosFrente([150, 520], [250, 520]), mi: 'relajada', md: 'relajada', cabeza: -8}} ojos="entrecerrados" cejas="arrogante" boca="picara" />
			</Actor>
			<Bombilla x={840} y={1400} tam={170} desde={d + 2} />
		</Toma>
	);
};

/* ---------------- 2 · escalada: papeles falsos, el hotel, el anuncio ---------------- */

const E4: React.FC<P> = ({d, h, e, s}) => {
	const golpes = [pal(5, 'falsifica'), pal(5, 'papeles'), pal(5, 'gobierno')];
	const POS: [number, number, string][] = [[330, 770, 'APROBADO'], [740, 960, 'OFICIAL'], [460, 1400, 'URGENTE']];
	return (
		<Toma escena={<div style={{position: 'absolute', inset: 0, background: '#3a2a1e'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}} golpes={golpes.map((g) => [g, 0.04] as [number, number])}>
			<PapelMembrete x={540} y={380} ancho={880} />
			{golpes.map((g, i) => (
				<React.Fragment key={i}>
					<GolpeSello x={POS[i][0]} y={POS[i][1]} desde={g} texto={POS[i][2]} tam={70} rot={[-12, 8, -4][i]} color={['#c8202a', '#1d2a6b', '#c8202a'][i]} />
					<SelloGoma x={POS[i][0]} y={POS[i][1]} desde={g} tam={220} />
				</React.Fragment>
			))}
		</Toma>
	);
};

type Rasgo = {ropa: typeof POISSON; x: number; y: number; alto: number; pose?: Partial<Pose>; ojos?: React.ComponentProps<typeof Muneco>['ojos']; cejas?: React.ComponentProps<typeof Muneco>['cejas']; boca?: React.ComponentProps<typeof Muneco>['boca']; extra?: React.ReactNode};

const SEIS: Rasgo[] = [
	{ropa: CH_GORDO, x: 150, y: 1520, alto: 760, ojos: 'feliz', boca: 'sonrisa', extra: null},
	{ropa: CH_ALTO, x: 330, y: 1500, alto: 980, ojos: 'normal', cejas: 'neutral'},
	{ropa: CH_LUPA, x: 520, y: 1520, alto: 780, ojos: 'grandes', cejas: 'sorprendido', boca: 'o'},
	{ropa: CH_DESCONFIADO, x: 700, y: 1520, alto: 790, ojos: 'entrecerrados', cejas: 'enojado', boca: 'mueca'},
	{ropa: CH_DORMIDO, x: 870, y: 1530, alto: 760, ojos: 'cerrados', boca: 'o'},
	{ropa: POISSON, x: 1010, y: 1540, alto: 770, ojos: 'grandes', cejas: 'preocupado', boca: 'mueca'},
];

const Seis: React.FC<{shh?: number}> = ({shh}) => {
	const f = useCurrentFrame();
	return (
		<>
			{SEIS.map((r, i) => {
				const callado = shh !== undefined && f >= shh;
				const {bx, by} = bocaDe(r.x, r.y, r.alto);
				return (
					<React.Fragment key={i}>
						<Actor x={r.x} y={r.y} alto={r.alto} voltear={i % 2 === 1}>
							<Muneco ropa={r.ropa} pose={callado ? {...manosEn(undefined, [212, 300], {}, true), md: 'puno', frenteD: 1} : manosFrente([170, 520], [230, 520])} ojos={r.ojos} cejas={r.cejas} boca={callado ? 'seria' : r.boca} />
						</Actor>
						{i === 2 && !callado && <Lupa x={r.x + 70} y={r.y - r.alto * 0.62} tam={120} desde={-100} />}
						{callado && <DedoLabios x={bx} y={by} tam={r.alto * 0.12} desde={shh + i} />}
					</React.Fragment>
				);
			})}
			{/* «Zzz» del dormido */}
			{!(shh !== undefined && f >= shh) && (
				<div style={{position: 'absolute', left: 900, top: 760 - ((f % 40) / 40) * 60, fontFamily: CONDENSADA, fontSize: 60, color: '#f6efdc', opacity: 1 - (f % 40) / 40}}>Zzz</div>
			)}
		</>
	);
};

const MesaHotel: React.FC = () => (
	<>
		<div style={{position: 'absolute', left: -40, right: -40, top: 1420, height: 60, background: '#5a2a1e', border: `9px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: -40, right: -40, top: 1480, height: 500, background: 'linear-gradient(180deg, #f2ead4, #d8ccb0)', borderTop: `8px solid ${TINTA}`}} />
		{/* mantel con encaje, el contrato y el café */}
		{Array.from({length: 14}, (_, i) => (
			<div key={i} style={{position: 'absolute', left: i * 80 - 20, top: 1478, width: 80, height: 40, borderRadius: '0 0 40px 40px', border: `5px solid #c9b48a`, borderTop: 'none'}} />
		))}
		<div style={{position: 'absolute', left: 390, top: 1600, width: 300, height: 200, background: '#fbf6e8', border: `7px solid ${TINTA}`, transform: 'rotate(-4deg)', padding: 18, boxSizing: 'border-box', fontFamily: CONDENSADA, fontSize: 40, color: '#c8202a', textAlign: 'center'}}>
			CONTRATO
			{[0, 1, 2].map((i) => (
				<div key={i} style={{height: 6, background: '#c9c0a8', margin: '16px 0'}} />
			))}
		</div>
		<TazaCafe x={190} y={1640} />
		<TazaCafe x={880} y={1660} />
	</>
);

const E5: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscHotelLujo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], x: [30, -30]}}>
		<Seis />
		<MesaHotel />
	</Toma>
);

const E6: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const chatarra = f >= antes(pal(8, 'chatarra')) && f < antes(pal(8, 'chatarra')) + 16 ? 1 : 0;
	const shh = antes(pal(8, 'palabra'));
	const L = {x: 540, y: 1360, alto: 1120};
	const {bx, by} = bocaDe(L.x, L.y, L.alto);
	return (
		<Toma escena={<EscHotelLujo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05], y: [0, 30]}} angulo={7}>
			{/* ventana con la torre detrás */}
			<div style={{position: 'absolute', left: 640, top: 250, width: 380, height: 560, background: 'linear-gradient(180deg, #8a4a8a, #f08a5a)', border: `12px solid #3a1e14`, outline: `5px solid ${TINTA}`, overflow: 'hidden'}}>
				<TorreEiffel x={190} y={560} alto={500} chatarra={chatarra} />
			</div>
			<Actor x={L.x} y={L.y} alto={L.alto}>
				<Muneco ropa={LUSTIG} pose={f >= shh ? {...manosEn(undefined, [212, 300], {}, true), md: 'puno', frenteD: 1, ...manosEn([150, 560])} : {...brazo(1, alcanzar(1, 330, 400)), md: 'abierta', ...manosEn([150, 560]), mi: 'relajada'}} ojos="entrecerrados" cejas="arrogante" boca={f >= shh ? 'seria' : 'picara'} hablando={f < shh} />
			</Actor>
			<DedoLabios x={bx} y={by} tam={L.alto * 0.12} desde={shh} />
			<div style={{position: 'absolute', inset: 0, transform: 'translateY(260px) scale(0.85)', transformOrigin: '50% 100%'}}>
				<Seis shh={shh + 6} />
			</div>
		</Toma>
	);
};

/* ---------------- 3 · la duda ---------------- */

const E7: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const revienta = antes(ini(10));
	const burbuja = f < revienta ? tramo(f, d + 4, d + 14) : 0;
	const estallido = f >= revienta && f < revienta + 8 ? 1 - (f - revienta) / 8 : 0;
	return (
		<Toma escena={<EscCasa />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}}>
			<Actor x={330} y={1760} alto={1150}>
				<Muneco ropa={POISSON} pose={{...brazo(1, alcanzar(1, 330, 330)), md: 'agarra', ...manosEn([150, 560]), mi: 'relajada'}} ojos="grandes" cejas="preocupado" boca="sonrisa" />
			</Actor>
			{/* recorte de la torre en su mano */}
			<div style={{position: 'absolute', left: 430, top: 900, width: 200, height: 260, background: '#f6efdc', border: `6px solid ${TINTA}`, transform: 'rotate(8deg)', overflow: 'hidden'}}>
				<TorreEiffel x={100} y={250} alto={230} />
			</div>
			{/* gotas de sudor */}
			{[0, 1].map((i) => (
				<div key={i} style={{position: 'absolute', left: 170 + i * 260, top: 640 + ((f * 3 + i * 20) % 60), width: 18, height: 26, borderRadius: '50% 50% 50% 50% / 60% 60% 40% 40%', background: '#9fd8ff', border: `4px solid ${TINTA}`}} />
			))}
			<Actor x={810} y={1780} alto={1150} voltear>
				<Muneco ropa={ESPOSA} pose={{...manosEn([256, 446], [146, 432]), mi: 'oculta', md: 'puno'}} ojos="entrecerrados" cejas="arrogante" boca="seria" />
			</Actor>
			{/* burbuja de pensamiento: él de frac en una fiesta elegante */}
			{burbuja > 0 && (
				<div style={{position: 'absolute', left: 60, top: 220, width: 620, height: 440, transform: `scale(${burbuja})`, transformOrigin: '30% 100%'}}>
					<div style={{position: 'absolute', inset: 0, borderRadius: '50%', background: '#fff6e0', border: `9px solid ${TINTA}`, overflow: 'hidden'}}>
						<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 30%, #ffe8a0, #e0b860)'}} />
						<Actor x={310} y={520} alto={460}>
							<Muneco ropa={POISSON_FRAC} pose={{...brazo(1, alcanzar(1, 330, 260)), md: 'agarra'}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
						</Actor>
					</div>
					{[0, 1].map((i) => (
						<div key={i} style={{position: 'absolute', left: 230 + i * 30, top: 460 + i * 60, width: 50 - i * 18, height: 50 - i * 18, borderRadius: '50%', background: '#fff6e0', border: `7px solid ${TINTA}`}} />
					))}
				</div>
			)}
			{estallido > 0 && (
				<svg width={620} height={440} viewBox="-310 -220 620 440" style={{position: 'absolute', left: 60, top: 220, opacity: estallido}}>
					{Array.from({length: 12}, (_, i) => {
						const a = (i / 12) * Math.PI * 2;
						return <line key={i} x1={Math.cos(a) * 120} y1={Math.sin(a) * 80} x2={Math.cos(a) * 280} y2={Math.sin(a) * 200} stroke="#fff6e0" strokeWidth={14} strokeLinecap="round" />;
					})}
				</svg>
			)}
		</Toma>
	);
};

const E7b: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscCasa />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.0]}} camFn={(f) => centrarV(810, 918, 1.8 + 0.6 * tramo(f, d, h, (u) => u), 760)}>
		<Actor x={810} y={1780} alto={1150} voltear>
			<Muneco ropa={ESPOSA} pose={{...manosEn([256, 446], [146, 432]), mi: 'oculta', md: 'puno', cabeza: 6}} ojos="entrecerrados" cejas="arrogante" boca="o" hablando={useCurrentFrame() < fin(10)} />
		</Actor>
	</Toma>
);

/* ---------------- 4 · el giro: el soborno ---------------- */

const E8: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const soborno = antes(pal(11, 'soborno'));
	const frota = f >= soborno ? Math.sin(f * 1.6) * 6 : 0;
	return (
		<Toma escena={<EscPasillo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.18], y: [60, 90]}}>
			<Actor x={810} y={1800} alto={1200} voltear>
				<Muneco ropa={POISSON} pose={manosFrente([170, 520], [230, 520])} ojos="mirandoLado" cejas="preocupado" boca="mueca" />
			</Actor>
			<Actor x={290} y={1790} alto={1260}>
				<Muneco ropa={LUSTIG} pose={{...brazo(1, alcanzar(1, 380, 420)), md: 'agarra', ...(f >= soborno ? {...manosEn([150 + frota, 360]), mi: 'puno'} : manosEn([150, 560])), cabeza: 10}} ojos="entrecerrados" cejas="arrogante" boca="picara" hablando={f < fin(11)} />
			</Actor>
			{f >= soborno &&
				[0, 1, 2].map((i) => {
					const t = (f - soborno + i * 6) % 18;
					return (
						<div key={i} style={{position: 'absolute', left: 90 + i * 50, top: 1000 - t * 6, fontFamily: CONDENSADA, fontSize: 60, color: '#ffd84a', WebkitTextStroke: `4px ${TINTA}`, opacity: 1 - t / 18}}>
							F
						</div>
					);
				})}
		</Toma>
	);
};

/** la pausa: la cara del chatarrero pasa de la desconfianza al alivio; en «convence», suelta el aire */
const E9: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const alivio = f >= pal(12, 'convence');
	const medio = f >= d + 10;
	return (
		<Toma escena={<EscPasillo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.6, 1.6], y: [520, 520]}}>
			<Actor x={540} y={1900} alto={1250}>
				<Muneco ropa={POISSON} pose={manosFrente([170, 520], [230, 520])} ojos={alivio ? 'feliz' : medio ? 'normal' : 'entrecerrados'} cejas={alivio ? 'neutral' : medio ? 'preocupado' : 'enojado'} boca={alivio ? 'sonrisaGrande' : medio ? 'seria' : 'mueca'} />
			</Actor>
			{alivio && (
				<div style={{position: 'absolute', left: 690, top: 960, width: 160, height: 90, borderRadius: '50%', background: 'rgba(255,255,255,0.85)', opacity: interpolate(f - pal(12, 'convence'), [0, 12], [1, 0], clamp), transform: `scale(${1 + (f - pal(12, 'convence')) / 10})`}} />
			)}
		</Toma>
	);
};

/* ---------------- 5 · el mecanismo ---------------- */

const E10: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cae = tramo(f, antes(pal(13, 'soborno')), pal(13, 'soborno') + 6, (u) => u * u);
	const inclina = tramo(f, pal(13, 'soborno') + 4, pal(13, 'soborno') + 14);
	const real = f >= antes(pal(13, 'sí')) ? 1 : 0;
	return (
		<Toma escena={<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 50%, #3a4a6a, #141a2a)'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}}>
			<div style={{position: 'absolute', inset: 0, transform: 'scale(0.85)', transformOrigin: '50% 0%'}}>
				<CabezaBalanza inclina={inclina} cae={cae} real={real} />
			</div>
		</Toma>
	);
};

const E11: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const uno = tramo(f, antes(pal(14, 'torre')), pal(14, 'torre') + 8);
	const dos = tramo(f, antes(pal(15, 'encima')), pal(15, 'encima') + 8);
	const zoom = antes(pal(15, 'soborno'));
	return (
		<Toma escena={<EscPasillo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => golpeCam(ff, zoom, {s: 1.0, x: 0, y: 0}, centrarV(330, 880, 1.8, 760))}>
			<Actor x={760} y={1800} alto={1200} voltear>
				<Muneco ropa={POISSON} pose={{...brazo(1, alcanzar(1, 360, 330)), md: 'abierta'}} ojos="feliz" cejas="neutral" boca="sonrisa" />
			</Actor>
			<Actor x={330} y={1790} alto={1260}>
				<Muneco ropa={LUSTIG} pose={{...brazo(1, alcanzar(1, 380, 330)), md: 'abierta'}} ojos={f >= zoom ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={f >= zoom ? 'sonrisaGrande' : 'picara'} />
			</Actor>
			<SobreGordo x={interpolate(uno, [0, 1], [720, 540])} y={980} tam={200} rot={-8} />
			{dos > 0 && <SobreGordo x={interpolate(dos, [0, 1], [720, 560])} y={880} tam={190} rot={10} />}
		</Toma>
	);
};

/** la salida, solo en imagen: Lustig en el tren con la maleta llena, saluda con el bastón */
const E12: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const va = tramo(f, d + 8, h + 4, (u) => u * u) * 1400;
	return (
		<Toma escena={<EscParisAtardecer />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 1340, height: 30, background: '#2a2a30'}} />
			<div style={{position: 'absolute', left: -va, top: 0, width: 1080, height: 1920}}>
				<Vagon x={90} y={860} ancho={900}>
					<Actor x={240} y={560} alto={520}>
						<Muneco ropa={LUSTIG} pose={{...brazo(1, {a: 150, c: 20}), md: 'agarra'}} objDer={<Baston rot={0} />} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
					</Actor>
					<div style={{position: 'absolute', left: 280, top: 160, width: 140, height: 90, background: '#7a4a26', border: `6px solid ${TINTA}`, borderRadius: 10}}>
						{[0, 1, 2].map((i) => (
							<div key={i} style={{position: 'absolute', left: 10 + i * 34, top: -26 + (i % 2) * 6, width: 60, height: 30, background: '#7fb07a', border: `4px solid ${TINTA}`, transform: `rotate(${-10 + i * 10}deg)`}} />
						))}
					</div>
				</Vagon>
			</div>
			<Vapor x={540 - va * 0.4} y={820} desde={d + 6} />
		</Toma>
	);
};

/* ---------------- 6 · el remate ---------------- */

const E13: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const verguenza = antes(pal(17, 'vergüenza'));
	const vuelta = f >= verguenza;
	const sale = tramo(f, verguenza + 6, h, (u) => u);
	return (
		<Toma escena={<EscComisaria />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}}>
			<Actor x={680 - sale * 500} y={1700} alto={1100} voltear={vuelta}>
				<Muneco ropa={POISSON} camina={vuelta ? 1 : 0} pose={vuelta ? {cabeza: 18} : {...brazo(1, alcanzar(1, 360, 400)), md: 'agarra'}} ojos={vuelta ? 'cerrados' : 'grandes'} cejas="preocupado" boca={vuelta ? 'mueca' : 'seria'} />
			</Actor>
			{/* se pone rojo de vergüenza: solo la cara */}
			<div style={{position: 'absolute', left: 680 - sale * 500 - 150, top: 1700 - 1100 * (880 / 900) + 1100 * (95 / 900), width: 300, height: 300, borderRadius: '50%', background: 'radial-gradient(circle, rgba(235,40,40,0.75) 0%, rgba(235,40,40,0.55) 55%, rgba(235,40,40,0) 72%)', mixBlendMode: 'multiply', opacity: tramo(f, verguenza, verguenza + 8)}} />
		</Toma>
	);
};

const E14: React.FC<P> = ({d, h, e, s}) => <Toma escena={<Cafe guino={d + 6} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [0, 40]}} />;

const E15: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const corre = (f - d) * 16;
	return (
		<Toma escena={<EscParisAtardecer desplaza={-corre} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}}>
			<Actor x={620} y={1760} alto={1150}>
				<Muneco ropa={LUSTIG} camina={2} pose={{...brazo(-1, alcanzar(-1, 120, 60)), mi: 'agarra', ...brazo(1, alcanzar(1, 320, 520)), md: 'agarra', cuerpo: 10}} objDer={<Baston rot={-40} />} ojos="grandes" cejas="sorprendido" boca="o" />
			</Actor>
			{[0, 1].map((i) => (
				<Actor key={i} x={90 + i * 240 - ((f - d) % 6)} y={1800} alto={900}>
					<Muneco ropa={POLICIA_FR} camina={2} pose={{...brazo(1, alcanzar(1, 250, 260)), md: 'agarra', cuerpo: 8}} ojos="entrecerrados" cejas="enojado" boca="o" />
				</Actor>
			))}
		</Toma>
	);
};

const E16: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Escritorio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.25], y: [0, -120]}}>
		<div style={{position: 'absolute', left: 230, top: 760, width: 620, height: 280, background: '#f2ead4', border: `8px solid ${TINTA}`, transform: 'perspective(800px) rotateX(55deg)'}} />
		{/* tintero y pluma */}
		<div style={{position: 'absolute', left: 780, top: 820, width: 110, height: 90, background: '#1c1c28', border: `7px solid ${TINTA}`, borderRadius: '20px 20px 30px 30px'}} />
		<div style={{position: 'absolute', left: 860, top: 600, width: 18, height: 260, background: '#f4f0e6', border: `5px solid ${TINTA}`, borderRadius: '50% 50% 4px 4px', transform: 'rotate(18deg)', transformOrigin: '50% 100%'}} />
	</Toma>
);

const E17: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const escribe = tramo(f, antes(pal(21, 'vendedor')), fin(21), (u) => u);
	return (
		<Toma escena={<Escritorio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => {
			const u = tramo(ff, d, pal(21, 'vendedor'));
			return centrarV(540, interpolate(u, [0, 1], [900, 1000]), 1.12 + 0.16 * u, interpolate(u, [0, 1], [900, 760]));
		}}>
			<Certificado x={540} y={480} ancho={920} escribe={escribe} />
		</Toma>
	);
};

/** cierre: a través de la ventana, París al atardecer con la torre y su cartel: el mismo encuadre del primer cuadro */
const Ventana: React.FC<{abre: number}> = ({abre}) => {
	if (abre >= 1) return null;
	const k = 1 + 2.6 * abre * abre;
	return (
		<svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, transform: `scale(${k})`, transformOrigin: '540px 900px'}}>
			<path d="M -400 -400 H 1480 V 2320 H -400 Z M 230 380 V 1420 H 850 V 380 Z" fill="#2a1a12" fillRule="evenodd" />
			<rect x={215} y={365} width={650} height={1070} fill="none" stroke="#5a3a22" strokeWidth={34} />
			<rect x={198} y={348} width={684} height={1104} fill="none" stroke={TINTA} strokeWidth={8} />
			<rect x={170} y={1430} width={740} height={60} fill="#5a3a22" stroke={TINTA} strokeWidth={8} />
		</svg>
	);
};

const E18: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<ParisTorre d={0} vendida={1e9} segundo={1e9} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.0], x: [-30, -30], y: [60, 60], r: [-2, -2]}} encima={<><Ventana abre={tramo(f, d + 2, d + 16, (u) => u)} /><Sello x={540} y={600} texto="REAL" desde={SELLO_REAL} color="#1f9d48" tam={200} rot={-10} solido /></>} />
	);
};

/** fin de la voz + 1,5 s: la cámara sale por la ventana y el sello de REAL ocupa el último segundo */
export const FIN_VIDEO = fin(21) + 45;
const SELLO_REAL = FIN_VIDEO - 30;

const PLANOS: Plano[] = [
	{n: 'torre', d: 0, e: 'corte', C: E0},
	{n: 'lustig', d: antes(pal(1, 'repetirlo')), e: 'latigoArriba', C: E0b},
	{n: 'oxido', d: ini(2), e: 'zoom', C: E1},
	{n: 'pintor', d: antes(pal(2, 'cuesta')), e: 'latigoDer', C: E1b},
	{n: 'plano', d: antes(pal(2, 'había')), e: 'latigoIzq', C: E1c},
	{n: 'cafe', d: ini(3), e: 'zoom', C: E2},
	{n: 'idea', d: ini(4), e: 'zoom', C: E3},
	{n: 'papeles', d: ini(5), e: 'latigoDer', C: E4},
	{n: 'hotel', d: ini(6), e: 'latigoIzq', C: E5},
	{n: 'anuncio', d: ini(7), e: 'latigoDer', C: E6},
	{n: 'casa', d: ini(9), e: 'latigoIzq', C: E7},
	{n: 'esposa', d: ini(10), e: 'zoom', C: E7b},
	{n: 'pasillo', d: ini(11), e: 'latigoDer', C: E8},
	{n: 'alivio', d: fin(11) + 2, e: 'zoom', C: E9},
	{n: 'balanza', d: ini(13), e: 'latigoIzq', C: E10},
	{n: 'pago', d: ini(14), e: 'latigoDer', C: E11},
	{n: 'tren', d: fin(15) - 2, e: 'latigoIzq', C: E12},
	{n: 'comisaria', d: antes(ini(17)), e: 'latigoDer', C: E13},
	{n: 'otra-vez', d: ini(18), e: 'latigoIzq', C: E14},
	{n: 'huye', d: antes(pal(18, 'tuvo')), e: 'latigoDer', C: E15},
	{n: 'mesa', d: ini(19), e: 'zoom', C: E16},
	{n: 'certificado', d: ini(20), e: 'zoom', C: E17},
	{n: 'paris', d: fin(21) + 3, e: 'zoom', C: E18},
];

const WHOOSH: [string, number, number][] = PLANOS.filter((p) => p.e && p.e.startsWith('latigo')).map((p) => ['whoosh', p.d - 5, 0.35]);

export const SONIDOS: [string, number, number][] = [
	...WHOOSH,
	['sello', antes(pal(0, 'vendió')), 0.9],
	['pop', antes(ini(1)), 0.7],
	['hoja', antes(pal(2, 'cuesta')) + 4, 0.6],
	['sello', antes(pal(2, 'desmontada')), 0.7],
	['ding', ini(4) + 2, 0.7],
	['sello', pal(5, 'falsifica'), 0.8],
	['sello', pal(5, 'papeles'), 0.8],
	['sello', pal(5, 'gobierno'), 0.8],
	['chatarra', antes(pal(8, 'chatarra')), 0.6],
	['shh', antes(pal(8, 'palabra')) + 4, 0.7],
	['pop', antes(ini(10)), 0.8],
	['suspiro', pal(12, 'convence'), 0.8],
	['clic', pal(13, 'soborno') + 4, 0.8],
	['ding', antes(pal(13, 'sí')), 0.8],
	['sobres', antes(pal(14, 'torre')), 0.6],
	['sobres', antes(pal(15, 'encima')), 0.6],
	['tren', fin(15) - 2, 0.7],
	['silbato', antes(pal(18, 'tuvo')), 0.8],
	['teclas', antes(pal(21, 'vendedor')), 0.3],
	['sello', SELLO_REAL, 1.0],
];

export const Historia: React.FC = () => <Montaje planos={PLANOS} fin={FIN_VIDEO} />;
