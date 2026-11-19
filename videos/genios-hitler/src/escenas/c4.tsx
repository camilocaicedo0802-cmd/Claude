import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Microfono} from '../componentes/Objetos';
import {Actor, Muneco, POSES, alcanzar, manosEn} from '../componentes/Muneco';
import {JarraVotos} from '../componentes/Recurrentes';
import {Toma} from '../componentes/Toma';
import {COMENTARISTA, HITLER_TRAJE, HITLER_VENDEDOR, SENOR_2} from '../componentes/Vestuario';
import {EscLiso, Hemiciclo} from '../escenarios/Epoca';
import {CONDENSADA} from '../fuentes';
import {Cam, P, Plano, TINTA, antes, centrar, fin, golpeCam, ini, mezclaCam, pal, pop} from './base';
import {Barra} from './c0';
import {MapaAncho} from './c3';
import {brazo} from './compartidas';
import {AlemaniaEnferma, Banco, BolsaNY, Cohete, Estornudo, EscOficinaEmpleo, EscPasilloPresidente, Fila, GraficoCripto, ManoCuerda, Munequito, PuestoTeletienda, SobresCayendo, Teletipo, Trofeo, Urna, tr} from './utileria_c345';

/* CAPÍTULO 4 · LA CRISIS (frases 103–120). Paleta: gris y negro. */

/* ---------- Wall Street: la cinta del teletipo (rótulo) y el estornudo ---------- */

const CalleNY: React.FC = () => (
	<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #3a4252 0%, #6a7282 70%)'}}>
		{[0, 1, 2, 3, 4, 5, 6].map((i) => (
			<div key={i} style={{position: 'absolute', left: i * 290 - 60, bottom: 180, width: 220, height: 420 + ((i * 137) % 260), background: '#2e3440', border: `6px solid ${TINTA}`}}>
				{Array.from({length: 8}, (_, j) => (
					<div key={j} style={{position: 'absolute', left: 24, right: 24, top: 30 + j * 56, height: 16, background: 'rgba(255,230,160,0.25)'}} />
				))}
			</div>
		))}
		<div style={{position: 'absolute', left: 0, right: 0, top: 900, bottom: 0, background: '#3a3e46', borderTop: `8px solid ${TINTA}`}} />
	</div>
);

const WallStreet: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const E = pal(103, 'estornuda');
	const abre = antes(pal(103, 'Nueva'));
	return (
		<Toma
			escena={<CalleNY />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => mezclaCam(centrar(1180, 990, 2.1), centrar(960, 520, 1.02 + 0.04 * tr(ff, abre, h)), tr(ff, d + 8, abre))}
			sacudida={(ff) => (ff >= E && ff < E + 12 ? 10 * (1 - (ff - E) / 12) : 0)}
		>
			<BolsaNY x={960} y={900} ancho={880} estornudo={E} />
			<Estornudo x1={960} y1={230} x2={2300} y2={260} desde={E} dur={14} />
			<div style={{position: 'absolute', left: 300, top: 1010, width: 480, height: 80, background: '#2a2a30', border: `7px solid ${TINTA}`}} />
			<Teletipo x={540} y={990} ancho={520} desde={d - 30} />
		</Toma>
	);
};

/* ---------- Alemania se enferma; la Bolsa atraviesa el suelo ---------- */

const camMapa = (cx: number, s: number): Cam => {
	const x = -(cx - 960) * s;
	const lim = [1920 - 960 - (3840 - 960) * s, 960 * s - 960];
	return {s, x: Math.max(lim[0], Math.min(lim[1], x)), y: 0};
};

const LineaBolsa: React.FC<{desde: number}> = ({desde}) => {
	const f = useCurrentFrame();
	const t = tr(f, desde, desde + 12, (u) => u * u);
	if (f < desde - 1) return null;
	const largo = 2000;
	return (
		<svg width={3840} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
			<path d="M 2080 260 L 2260 200 L 2380 240 L 2480 170 L 2620 1200" stroke="#c4262e" strokeWidth={22} fill="none" strokeLinejoin="round" strokeLinecap="round" strokeDasharray={largo} strokeDashoffset={largo * (1 - t)} />
			{t > 0.9 && (
				<g transform="translate(2600 1060)">
					<path d="M -120 0 L -60 -20 L -20 10 L 30 -24 L 80 4 L 140 -10" stroke={TINTA} strokeWidth={10} fill="none" />
				</g>
			)}
			<text x={2100} y={180} fontFamily={CONDENSADA} fontSize={70} fill="#c4262e">
				BOLSA
			</text>
		</svg>
	);
};

const Enferma: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const en = tr(f, pal(104, 'enferma') - 6, pal(104, 'enferma'));
	return (
		<Toma escena={<MapaAncho />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => camMapa(interpolate(tr(ff, d, h), [0, 1], [2700, 2780]), 1.0 + 0.08 * tr(ff, d, h))}>
			<Estornudo x1={1850} y1={300} x2={3120} y2={440} desde={d - 6} dur={14} texto={false} />
			<AlemaniaEnferma x={3170} y={470} tam={360} enferma={en} />
			<LineaBolsa desde={ini(105) - 2} />
		</Toma>
	);
};

/* ---------- los bancos estadounidenses piden su plata ---------- */

const Mano: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const tira = tr(f, pal(105, 'piden') - 4, pal(105, 'vuelta') + 4);
	return (
		<Toma escena={<MapaAncho />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => camMapa(interpolate(tr(ff, d, h), [0, 1], [2380, 2260]), 1.0)}>
			<Banco x={2840} y={720} ancho={220} vacio={tira} />
			<Banco x={3080} y={660} ancho={250} vacio={tira} />
			<ManoCuerda x={1700} y={540} tira={tira} />
			<div style={{position: 'absolute', left: 1500, top: 300, padding: '8px 22px', background: '#f4efe0', border: `6px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 44, color: '#2a3a5a', transform: `translateX(${-tira * 700}px) rotate(-4deg)`}}>BANCOS DE EE. UU.</div>
		</Toma>
	);
};

/* ---------- seis millones de desempleados (neutro, gris) ---------- */

const FilaEmpleo: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscOficinaEmpleo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(interpolate(tr(ff, d, h), [0, 1], [700, 1100]), 520, 1.1)} tinte="rgba(120,120,130,0.5)">
		<Fila x0={-120} y={960} n={10} paso={150} alto={560} />
	</Toma>
);

/* ---------- el vendedor de soluciones mágicas ---------- */

const Vendedor: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const ap = pal(106, 'aparece') - 2;
	const g = ini(107) - 2;
	const escala = pop(f, ap);
	return (
		<Toma
			escena={<EscOficinaEmpleo />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => golpeCam(ff, g, centrar(860, 540, 1.04 + 0.04 * tr(ff, d, g)), centrar(420, 470, 1.55))}
			angulo={-4}
			tinte="rgba(120,120,130,0.4)"
		>
			<Fila x0={820} y={960} n={8} paso={145} alto={560} giran={tr(f, g, g + 14)} />
			<PuestoTeletienda x={410} y={150} ancho={600} aparece={pop(f, ap + 2)} />
			{f >= ap && (
				<Actor x={410} y={1000} alto={720} escala={escala}>
					<Muneco ropa={HITLER_VENDEDOR} pose={{...manosEn([20, 360], [380, 360]), mi: 'abierta', md: 'abierta', wi: 20, wd: 20}} ojos="feliz" cejas="arrogante" boca={f >= g ? 'sonrisaGrande' : 'sonrisa'} hablando={false} />
				</Actor>
			)}
		</Toma>
	);
};

/* ---------- el 18 %: la jarra con cohete ---------- */

const JarraCohete: React.FC<{x: number; nivel: number; lift: number; llama: number; alto?: number}> = ({x, nivel, lift, llama, alto = 660}) => (
	<>
		<JarraVotos x={x} y={880 - lift} alto={alto} nivel={nivel} />
		<Cohete x={x + alto * 0.66} y={880 - lift - alto * 0.62} tam={alto * 0.3} llama={llama} />
		<div style={{position: 'absolute', left: x + alto * 0.3, top: 880 - lift - alto * 0.42, width: alto * 0.3, height: 14, background: '#8a6a3a', border: `5px solid ${TINTA}`, transform: 'rotate(-8deg)'}} />
	</>
);

const CoheteJarra: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sal = pal(108, 'SALTA');
	const nivel = 2.6 + 15.4 * tr(f, sal - 4, pal(108, '18') + 2);
	const lift = 110 * tr(f, sal - 6, sal + 8, (u) => u * u) - 10 * Math.sin(f / 4) * tr(f, sal, sal + 10);
	const llama = tr(f, sal - 8, sal - 4);
	return (
		<Toma escena={<Barra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(960, 520 - lift * 0.4, 1.06)} sacudida={() => 3 * llama}>
			<JarraCohete x={900} nivel={nivel} lift={lift} llama={llama} />
		</Toma>
	);
};

/* ---------- de doce diputados a ciento siete ---------- */

const Hemiciclo107: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const n = Math.round(12 + 95 * tr(f, pal(109, 'ciento') - 8, pal(109, 'siete') + 4));
	return (
		<Toma escena={<EscLiso color="#0e0e14" luz="200,200,230" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.14], r: [1, -0.5], y: [40, 70]}}>
			<div style={{position: 'absolute', inset: 0, transform: 'scaleX(-1)'}}>
				<Hemiciclo x={960} y={940} radio={760} encendidos={n} oscuro={1} color="#d6863a" apagado="#22222a" />
			</div>
			<div style={{position: 'absolute', left: 710, top: 50, width: 500, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 90, color: '#f4ecd6', letterSpacing: 3}}>{n} / 491</div>
		</Toma>
	);
};

/* ---------- ni las criptomonedas suben así ---------- */

const Cripto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<Barra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.08], x: [30, -30]}}>
			<JarraCohete x={620} nivel={18} lift={100 - 10 * Math.sin(f / 4)} llama={1} alto={600} />
			<GraficoCripto x={1370} y={820} ancho={560} dibuja={tr(f, d + 2, d + 22)} />
		</Toma>
	);
};

/* ---------- 37 %: el más votado (trofeo), y la espuma no llega ---------- */

const Trofeo37: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const nivel = 18 + 19 * tr(f, pal(111, '37') - 6, pal(111, '37') + 4);
	const entra = tr(f, ini(112) - 4, ini(112) + 14);
	const ox = interpolate(entra, [0, 1], [2200, 1560]);
	return (
		<Toma escena={<Barra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(interpolate(tr(ff, d, h), [0, 1], [960, 1100]), 520, 1.04 + 0.05 * tr(ff, d, h))}>
			<JarraVotos x={900} y={880} alto={700} nivel={nivel} />
			<Actor x={ox} y={1000} alto={760}>
				<Muneco ropa={SENOR_2} camina={entra > 0 && entra < 1 ? 1.4 : 0} pose={{...brazo(-1, alcanzar(-1, -30, 380)), mi: 'agarra', cabeza: -4}} ojos="feliz" cejas="neutral" boca="sonrisa" />
			</Actor>
			{entra > 0 && <Trofeo x={ox - 180} y={680} tam={200} rot={-6} />}
		</Toma>
	);
};

/* ---------- «Ah, entonces ganó»: el comentarista y el disco rayado ---------- */

const Comentarista: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const ah = pal(113, 'Ah') - 2;
	const g = ini(114) - 1;
	const salta = f >= ah && f < g ? Math.abs(Math.sin(((f - ah) / 14) * Math.PI)) * 70 : 0;
	return (
		<Toma
			escena={<Barra />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => golpeCam(ff, g, centrar(980, 520, 1.03 + 0.04 * tr(ff, d, g)), centrar(1300, 500, 2.4))}
		>
			<JarraVotos x={1350} y={930} alto={700} nivel={37} />
			<div style={{position: 'absolute', left: 260, top: 760, width: 620, height: 340, background: '#2f6fd1', border: `9px solid ${TINTA}`, borderRadius: 10}} />
			<Actor x={570} y={940} alto={720}>
				<Muneco
					ropa={COMENTARISTA}
					pose={f >= ah ? {...POSES.victoria, mi: 'agarra', salto: salta} : {...manosEn([150, 360]), mi: 'agarra', ...manosEn(undefined, [260, 520]), md: 'puno'}}
					objIzq={<Microfono rot={180} />}
					ojos={f >= ah ? 'feliz' : 'normal'}
					cejas="sorprendido"
					boca={f >= ah ? 'grito' : 'abierta'}
					hablando={f < ah}
				/>
			</Actor>
			<div style={{position: 'absolute', left: 260, top: 860, width: 620, height: 240, background: '#2f6fd1', border: `9px solid ${TINTA}`, borderTop: 'none'}}>
				<div style={{position: 'absolute', left: 30, right: 30, top: 40, padding: '6px 0', background: '#fff', border: `6px solid ${TINTA}`, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 52, color: '#2f6fd1', letterSpacing: 3}}>RADIO DEPORTES</div>
			</div>
		</Toma>
	);
};

/* ---------- seis de cada diez votaron por otro ---------- */

const Diez: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const enc = pal(115, '37') - 2;
	const seis = pal(115, 'seis') - 2;
	return (
		<Toma escena={<EscLiso color="#1d2028" luz="230,230,240" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1], x: [40, -40], y: [10, 30]}}>
			{Array.from({length: 10}, (_, i) => {
				const x = 330 + i * 140;
				const aparece = d + 4 + i * 2;
				const p = pop(f, aparece);
				const lit = i < 4 && f >= enc;
				return (
					<div key={i} style={{position: 'absolute', left: 0, top: 0, transform: `scale(${p})`, transformOrigin: `${x}px 760px`}}>
						<Munequito x={x} y={760} alto={300} color={lit ? '#d6863a' : '#5a5e6a'} opacidad={!lit && f >= seis ? 0.55 + 0.15 * Math.sin(f / 4) : 1} />
					</div>
				);
			})}
			{f >= seis && (
				<>
					<div style={{position: 'absolute', left: 870, top: 800, width: 800, height: 40, borderLeft: `8px solid #c9ced6`, borderRight: `8px solid #c9ced6`, borderBottom: `8px solid #c9ced6`, opacity: tr(f, seis, seis + 8)}} />
					<div style={{position: 'absolute', left: 870, top: 860, width: 800, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 72, color: '#c9ced6', letterSpacing: 4, opacity: tr(f, seis, seis + 8)}}>VOTARON POR OTRO</div>
				</>
			)}
			{f >= enc && <div style={{position: 'absolute', left: 300, top: 860, width: 480, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 72, color: '#d6863a', letterSpacing: 4, opacity: tr(f, enc, enc + 8)}}>37 %</div>}
		</Toma>
	);
};

/* ---------- serio: casi catorce millones. Eso pesa. ---------- */

const UrnaSeria: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#16181e" luz="220,222,232" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.07], y: [0, 10]}}>
		<SobresCayendo x={960} y={470} desde={d - 10} cada={7} n={30} />
		<Urna x={960} y={940} ancho={420} />
	</Toma>
);

/* ---------- el presidente: el pasillo y la puerta ---------- */

const Pasillo: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscPasilloPresidente silueta={0} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(960, 520, 1.0 + 0.12 * tr(ff, d, h))} />
);

const Puerta: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const P0 = pal(120, 'soportaba') + 2;
	const cerrada = f < P0 - 3 ? 0.86 : tr(f, P0 - 3, P0, (u) => u * u) * 0.14 + 0.86;
	const salto = f >= P0 ? Math.max(0, 1 - (f - P0) / 10) : 0;
	return (
		<Toma
			escena={<EscPasilloPresidente silueta={1} cerrada={cerrada} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => centrar(960, 560, 1.1 + 0.08 * tr(ff, d, P0))}
			angulo={-6}
			sacudida={(ff) => (ff >= P0 && ff < P0 + 10 ? 12 * (1 - (ff - P0) / 10) : 0)}
		>
			<Actor x={960} y={1075} alto={440} escala={1 - 0.06 * salto}>
				<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([170, 520], [230, 520]), mi: 'agarra', md: 'agarra', cabeza: -10, salto: salto * 30}} ojos={f >= P0 ? 'cerrados' : 'grandes'} cejas="preocupado" boca={f >= P0 ? 'mueca' : 'o'} />
			</Actor>
		</Toma>
	);
};

export const PLANOS_C4: Plano[] = [
	{n: 'c4-wallstreet', d: fin(102) + 1, e: 'zoom', C: WallStreet},
	{n: 'c4-enferma', d: ini(104), e: 'latigoDer', C: Enferma},
	{n: 'c4-mano', d: antes(pal(105, 'bancos')), e: 'latigoIzq', C: Mano},
	{n: 'c4-fila', d: antes(pal(105, 'Alemania')), e: 'latigoDer', C: FilaEmpleo},
	{n: 'c4-vendedor', d: antes(pal(106, 'quién')), e: 'latigoIzq', C: Vendedor},
	{n: 'c4-cohete', d: ini(108), e: 'latigoDer', C: CoheteJarra},
	{n: 'c4-hemiciclo107', d: ini(109), e: 'latigoArriba', C: Hemiciclo107},
	{n: 'c4-cripto', d: ini(110), e: 'latigoIzq', C: Cripto},
	{n: 'c4-trofeo', d: ini(111), e: 'latigoDer', C: Trofeo37},
	{n: 'c4-comentarista', d: ini(113), e: 'latigoIzq', C: Comentarista},
	{n: 'c4-diez', d: ini(115), e: 'latigoDer', C: Diez},
	{n: 'c4-urna', d: ini(116), e: 'fundido', C: UrnaSeria},
	{n: 'c4-pasillo', d: ini(118), e: 'fundido', C: Pasillo},
	{n: 'c4-puerta', d: ini(119), e: 'zoom', C: Puerta},
];

export const SONIDOS_C4: [string, number, number][] = [
	['teclas', fin(102) + 2, 0.5],
	['estornudo', pal(103, 'estornuda') - 8, 1.0],
	['crack', ini(105) + 8, 0.6],
	['caja', pal(105, 'piden'), 0.7],
	['pop', pal(106, 'aparece') - 2, 0.7],
	['ding', ini(107) - 1, 0.6],
	['cohete', pal(108, 'SALTA') - 8, 0.9],
	['chispas', pal(109, 'ciento') - 8, 0.5],
	['ding', pal(109, 'siete') + 4, 0.5],
	['ding', ini(112), 0.7],
	['aplausos', pal(113, 'Ah') - 2, 0.6],
	['rayado', ini(114) - 1, 1.0],
	['pop', pal(115, '37') - 2, 0.5],
	['sobres', ini(116), 0.35],
	['puerta', pal(120, 'soportaba') + 2, 1.0],
];
