import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {Chistera, JarraVotos} from '../componentes/Recurrentes';
import {Toma} from '../componentes/Toma';
import {DOMADOR, HITLER_TRAJE, MINISTRO, SENOR_1, SENOR_2, SENOR_3} from '../componentes/Vestuario';
import {EscCerveceria, EscLiso, EscMapa, Hemiciclo, Jarra} from '../escenarios/Epoca';
import {CONDENSADA} from '../fuentes';
import {P, Plano, TINTA, antes, centrar, golpeCam, ini, pal, pop} from './base';
import {Barra} from './c0';
import {PlanoMuletilla, brazo, golpeMuletilla} from './compartidas';
import {CalendarioHojas, CaraGrande, CartelCirco, Cremallera, EscCirco, EscDespachoBavaro, EscLadrillo, EscMuseoSala, EscSalaJuntas, EscritorioFrente, Gatito, GraficoCaida, Latigo, LupaMundo, MarcoMuseo, Taburete, tr} from './utileria_c345';

/* CAPÍTULO 3 · LA FIERA DOMADA (frases 86–102). Paleta: rojo y dorado de circo. */

/* ---------- el cartel de circo (rótulo) ---------- */

const Cartel: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLadrillo />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => ({...centrar(960, 500, 1.22 + 0.14 * tr(ff, d, h)), r: -1 + 1.5 * tr(ff, d, h)})}>
		<CartelCirco x={960} y={120} ancho={620} rot={-2.5} />
	</Toma>
);

/* ---------- el despacho bávaro: Hitler va a ver al ministro ---------- */

/** papel de «PARTIDO PROHIBIDO» sobre el escritorio; `rasga` lo parte en dos */
const PapelProhibido: React.FC<{x: number; y: number; rasga?: number}> = ({x, y, rasga = 0}) => {
	const mitad = (l: -1 | 1) => (
		<div style={{position: 'absolute', left: x - 120 + (l > 0 ? 120 : 0) + l * rasga * 90, top: y - 80 - rasga * 40, width: 120, height: 160, overflow: 'hidden', transform: `rotate(${l * rasga * 25}deg)`}}>
			<div style={{position: 'absolute', left: l > 0 ? -120 : 0, top: 0, width: 240, height: 160, background: '#f4efe0', border: `5px solid ${TINTA}`, boxSizing: 'border-box', textAlign: 'center', fontFamily: CONDENSADA, color: '#2a2218'}}>
				<div style={{fontSize: 28, marginTop: 12}}>PARTIDO</div>
				<div style={{display: 'inline-block', marginTop: 10, padding: '2px 10px', border: '5px solid #c4262e', color: '#c4262e', fontSize: 34, transform: 'rotate(-8deg)'}}>PROHIBIDO</div>
			</div>
		</div>
	);
	return (
		<>
			{mitad(-1)}
			{mitad(1)}
		</>
	);
};

const Despacho: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const llega = tr(f, d + 4, d + 70);
	const hx = interpolate(llega, [0, 1], [240, 700]);
	return (
		<Toma escena={<EscDespachoBavaro />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(interpolate(tr(ff, d, h), [0, 1], [760, 940]), 520, 1.12)} angulo={2}>
			<Actor x={1180} y={1000} alto={780}>
				<Muneco ropa={MINISTRO} pose={{...manosFrente([170, 560], [230, 560]), mi: 'agarra', md: 'agarra'}} ojos="entrecerrados" cejas="arrogante" boca="seria" />
			</Actor>
			<EscritorioFrente x={1180} y={650} ancho={720}>
				<PapelProhibido x={1080} y={640} />
			</EscritorioFrente>
			<Actor x={hx} y={1040} alto={720}>
				<Muneco ropa={HITLER_TRAJE} camina={llega < 1 ? 1 : 0} pose={llega < 1 ? {} : {...manosFrente([190, 470], [210, 470]), mi: 'agarra', md: 'agarra', cabeza: 6}} ojos="normal" cejas="preocupado" boca="sonrisa" />
			</Actor>
		</Toma>
	);
};

/* ---------- cara de niño bueno, con aureola que parpadea ---------- */

const NinoBueno: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const aureola = f >= pal(87, 'niño') - 2;
	const falla = f >= ini(88) && [0, 1, 5, 9, 10].includes((f - ini(88)) % 19);
	return (
		<Toma escena={<EscDespachoBavaro />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(960, 380, 1.25 + 0.15 * tr(ff, d, h))} angulo={-6}>
			<Actor x={960} y={1120} alto={980}>
				<Muneco
					ropa={HITLER_TRAJE}
					pose={{...manosEn([184, 430], [216, 430], {}, true), mi: 'abierta', md: 'abierta', wi: -70, wd: -70, cabeza: -5}}
					ojos="grandes"
					cejas="preocupado"
					boca="sonrisa"
					acc={{aureola: aureola && !falla}}
				/>
			</Actor>
		</Toma>
	);
};

/* ---------- el ministro se lo cree y rompe la prohibición ---------- */

const SeLoCree: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const rasga = tr(f, pal(90, 'Levanta'), pal(90, 'Levanta') + 8);
	const asiente = Math.sin(f / 5) * 4 * (f < ini(90) ? 1 : 0);
	return (
		<Toma escena={<EscDespachoBavaro />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(interpolate(tr(ff, d, h), [0, 1], [1100, 1040]), 470, 1.3)} angulo={5}>
			<Actor x={1080} y={1000} alto={800}>
				<Muneco
					ropa={MINISTRO}
					pose={rasga > 0 ? {...manosFrente([110, 600], [290, 600]), mi: 'agarra', md: 'agarra', cabeza: asiente} : {...manosFrente([150, 600], [250, 600]), mi: 'agarra', md: 'agarra', cabeza: asiente}}
					ojos="feliz"
					cejas="neutral"
					boca="sonrisaGrande"
				/>
			</Actor>
			<EscritorioFrente x={1080} y={650} ancho={760}>
				<PapelProhibido x={1080} y={600} rasga={rasga} />
			</EscritorioFrente>
		</Toma>
	);
};

/* ---------- una frase que debería estar en un museo ---------- */

const Museo: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscMuseoSala />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.16], y: [20, 40]}}>
		<MarcoMuseo x={960} y={150} ancho={720} placa="FRASE CÉLEBRE · 1925" texto="«…»" />
	</Toma>
);

/* ---------- el domador y el gatito ---------- */

const MANO_DOMADOR: [number, number] = [1102, 640];
const COLLAR: [number, number] = [712, 716];

const Cadena: React.FC<{suelta: number}> = ({suelta}) => {
	const fin: [number, number] = [interpolate(suelta, [0, 1], [MANO_DOMADOR[0], 930]), interpolate(suelta, [0, 1], [MANO_DOMADOR[1], 990])];
	const cx = (COLLAR[0] + fin[0]) / 2;
	const cy = Math.max(COLLAR[1], fin[1]) + 90 * (1 - suelta * 0.5);
	return (
		<svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
			<path d={`M ${COLLAR[0]} ${COLLAR[1]} Q ${cx} ${cy} ${fin[0]} ${fin[1]}`} stroke={TINTA} strokeWidth={16} fill="none" />
			<path d={`M ${COLLAR[0]} ${COLLAR[1]} Q ${cx} ${cy} ${fin[0]} ${fin[1]}`} stroke="#b8b8c0" strokeWidth={9} fill="none" strokeDasharray="18 8" />
		</svg>
	);
};

const Domador: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const suelta = tr(f, pal(91, 'aflojarle'), pal(91, 'aflojarle') + 10);
	const chasq = Math.max(0, Math.sin((f - d) / 6));
	return (
		<Toma escena={<EscCirco foco={[1000, 560]} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(interpolate(tr(ff, d, h), [0, 1], [1000, 960]), 520, 1.08 + 0.06 * tr(ff, d, h))} angulo={7}>
			<Taburete x={700} y={1000} ancho={230} />
			<Gatito x={700} y={812} tam={300} />
			<Actor x={1250} y={1000} alto={820}>
				<Muneco
					ropa={DOMADOR}
					pose={{...brazo(-1, alcanzar(-1, 40, 470 + suelta * 60)), mi: suelta > 0.5 ? 'abierta' : 'agarra', ...brazo(1, {a: 140, c: 30}), md: 'agarra', cabeza: -4}}
					objDer={<Latigo rot={15} chasquido={chasq} />}
					ojos="feliz"
					cejas="arrogante"
					boca="sonrisa"
					hablando={f < ini(92) - 2}
				/>
			</Actor>
			<Cadena suelta={suelta} />
		</Toma>
	);
};

/* ---------- ¿Cuánto le duró? Semanas: el gatito ruge ---------- */

const DOMADOR_SIN_SOMBRERO = {...DOMADOR, cabeza: {...DOMADOR.cabeza, gorra: undefined, pelo: 'raya' as const, colorPelo: '#6b6b6b'}};

const Semanas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const g = ini(93) - 2;
	const ruge = tr(f, g - 3, g + 3);
	const vuela = f - g;
	return (
		<Toma
			escena={<EscCirco foco={[900, 560]} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => golpeCam(ff, g, centrar(1000, 540, 1.04), centrar(920, 520, 1.28))}
			sacudida={(ff) => (ff >= g && ff < g + 14 ? 9 * (1 - (ff - g) / 14) : 0)}
		>
			<CalendarioHojas x={300} y={300} ancho={300} textos={['SEMANA 1', 'SEMANA 2', 'SEMANA 3']} cambios={[ini(92) + 10, ini(92) + 22]} cabecera="1925" />
			<Taburete x={700} y={1000} ancho={230} rompe={tr(f, g, g + 8)} />
			<Gatito x={700} y={interpolate(tr(f, g, g + 8), [0, 1], [812, 1000])} tam={300} ruge={ruge} />
			<Actor x={1250} y={1000} alto={820}>
				<Muneco
					ropa={vuela >= 0 ? DOMADOR_SIN_SOMBRERO : DOMADOR}
					pose={vuela >= 0 ? {...manosEn([60, 300], [340, 300]), mi: 'abierta', md: 'abierta', cuerpo: 6} : {...brazo(-1, {a: 20, c: -10}), ...brazo(1, {a: 140, c: 30}), md: 'agarra'}}
					objDer={vuela >= 0 ? undefined : <Latigo rot={15} />}
					ojos={vuela >= 0 ? 'grandes' : 'feliz'}
					cejas={vuela >= 0 ? 'sorprendido' : 'arrogante'}
					boca={vuela >= 0 ? 'o' : 'sonrisa'}
				/>
			</Actor>
			{vuela >= 0 && <Chistera x={1250 + vuela * 14} y={260 - vuela * 26 + vuela * vuela * 0.6} ancho={170} rot={vuela * 22} />}
		</Toma>
	);
};

/* ---------- le prohíben hablar: la cremallera ---------- */

const CartelProhibidoHablar: React.FC<{desde: number}> = ({desde}) => {
	const f = useCurrentFrame();
	const p = pop(f, desde);
	if (f < desde) return null;
	return (
		<div style={{position: 'absolute', left: 1240, top: 170, width: 520, transform: `scale(${p}) rotate(4deg)`, transformOrigin: '50% 0'}}>
			<div style={{position: 'absolute', left: 120, top: -170, width: 6, height: 180, background: TINTA}} />
			<div style={{position: 'absolute', left: 390, top: -170, width: 6, height: 180, background: TINTA}} />
			<div style={{background: '#f4efe0', border: `9px solid ${TINTA}`, padding: '20px 0', textAlign: 'center', fontFamily: CONDENSADA, color: '#c4262e', boxShadow: '12px 14px 0 rgba(0,0,0,0.35)'}}>
				<div style={{fontSize: 74, lineHeight: 1}}>PROHIBIDO</div>
				<div style={{fontSize: 74, lineHeight: 1}}>HABLAR</div>
				<div style={{fontSize: 52, color: '#2a2218', marginTop: 8}}>1925 – 1927</div>
			</div>
		</div>
	);
};

const Cremallera_: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const c0 = pal(94, 'hablar') - 2;
	const cierra = tr(f, c0, c0 + 12);
	const grita = cierra === 0;
	return (
		<Toma escena={<EscLiso color="#2a2028" luz="255,200,170" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(interpolate(tr(ff, d, h), [0, 1], [880, 960]), 560, 1.0 + 0.08 * tr(ff, d, h))} angulo={-5}>
			<CaraGrande x={720} y={520} tam={760} ojos={grita ? 'grandes' : 'entrecerrados'} cejas={grita ? 'enojado' : 'preocupado'} boca={grita ? 'grito' : 'seria'} />
			{!grita && <Cremallera x={720} y={520} tam={760} cierra={cierra} />}
			<CartelProhibidoHablar desde={antes(ini(95))} />
		</Toma>
	);
};

/* ---------- el 2,6 %: una gota que hay que buscar con lupa ---------- */

const Jarra26: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const g = ini(97) - 2;
	const nivel = 2.6 * tr(f, d + 8, g - 4);
	const lupa = tr(f, d + 20, g);
	return (
		<Toma escena={<Barra />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => golpeCam(ff, g, centrar(980, 540, 1.05 + 0.04 * tr(ff, d, g)), centrar(880, 790, 2.3))}>
			<JarraVotos x={1000} y={900} alto={720} nivel={nivel} />
			<LupaMundo x={interpolate(lupa, [0, 1], [1500, 958])} y={interpolate(lupa, [0, 1], [500, 760])} tam={260} rot={-28} />
		</Toma>
	);
};

/* ---------- doce diputados de casi quinientos ---------- */

const Hemiciclo12: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const n = Math.round(12 * tr(f, d + 4, d + 18));
	return (
		<Toma escena={<EscLiso color="#0e0e14" luz="200,200,230" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], r: [-1.5, 0.5], y: [40, 60]}}>
			<div style={{position: 'absolute', inset: 0, transform: 'scaleX(-1)'}}>
				<Hemiciclo x={960} y={940} radio={760} encendidos={n} oscuro={1} color="#d6863a" apagado="#22222a" />
			</div>
			<div style={{position: 'absolute', left: 710, top: 50, width: 500, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 90, color: '#f4ecd6', letterSpacing: 3}}>12 / 491</div>
		</Toma>
	);
};

/* ---------- si esto fuera una startup ---------- */

const Startup: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cae = tr(f, pal(99, 'startup'), pal(99, 'startup') + 10, (t) => t * t);
	const huye = tr(f, pal(99, 'inversionistas'), h);
	const inversor = (i: number, ropa: typeof SENOR_1) => {
		const x0 = 420 + i * 230;
		const x = x0 - huye * (x0 + 300) * (0.8 + i * 0.15);
		return (
			<Actor key={i} x={x} y={1000} alto={700} voltear={huye > 0}>
				<Muneco ropa={ropa} camina={huye > 0 ? 2.2 : 0} pose={huye > 0 ? {...manosEn([60, 320], [340, 320]), mi: 'abierta', md: 'abierta'} : {...manosFrente([180, 520], [220, 520]), mi: 'agarra', md: 'agarra'}} ojos={cae > 0.3 ? 'grandes' : 'normal'} cejas={cae > 0.3 ? 'sorprendido' : 'neutral'} boca={cae > 0.3 ? 'o' : 'seria'} semilla={i} />
			</Actor>
		);
	};
	return (
		<Toma escena={<EscSalaJuntas />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.12], x: [-30, 30]}} angulo={-3}>
			<GraficoCaida x={1230} y={220} ancho={560} cae={cae} titulo="PARTIDO S.A." />
			{inversor(0, SENOR_1)}
			{inversor(1, SENOR_2)}
			{inversor(2, SENOR_3)}
			<Actor x={1620} y={1010} alto={720}>
				<Muneco ropa={HITLER_TRAJE} pose={{...brazo(-1, alcanzar(-1, -60, 260)), mi: 'senala', ...manosEn(undefined, [260, 540]), md: 'puno'}} ojos={cae > 0.3 ? 'grandes' : 'feliz'} cejas={cae > 0.3 ? 'preocupado' : 'arrogante'} boca={cae > 0.3 ? 'mueca' : 'sonrisaGrande'} />
			</Actor>
		</Toma>
	);
};

/* ---------- y probablemente ahí se habría quedado ---------- */

const Quedado: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscCerveceria tono="sepia" vacia humo={0.14} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.3, 1.18], y: [60, 40]}} angulo={-7}>
			<Actor x={900} y={1080} alto={720}>
				<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([170, 300]), mi: 'puno', frenteI: 1, ...manosFrente(undefined, [300, 560 + Math.abs(Math.sin(f / 3)) * 8]), md: 'relajada', cabeza: 8}} ojos="entrecerrados" cejas="preocupado" boca="mueca" />
			</Actor>
			<div style={{position: 'absolute', left: 560, top: 760, width: 800, height: 40, background: '#7a5230', border: `8px solid ${TINTA}`, borderRadius: 6}} />
			<div style={{position: 'absolute', left: 600, top: 800, width: 720, height: 300, background: '#5a3a1e', border: `8px solid ${TINTA}`}} />
			<Jarra x={1120} y={762} alto={110} espuma={0.2} />
		</Toma>
	);
};

/* ---------- el barrido sobre el océano hasta Nueva York, 1929 ---------- */

const Skyline: React.FC<{x: number; y: number; sube: number}> = ({x, y, sube}) => (
	<div style={{position: 'absolute', left: x - 260, top: y - 420, width: 520, height: 420, transform: `scaleY(${sube})`, transformOrigin: '50% 100%'}}>
		{[
			[0, 160, 70],
			[80, 300, 80],
			[180, 420, 70],
			[260, 260, 90],
			[360, 340, 70],
			[440, 200, 80],
		].map(([l, a, w], i) => (
			<div key={i} style={{position: 'absolute', left: l, bottom: 0, width: w, height: a, background: '#3a3a48', border: `6px solid ${TINTA}`}}>
				{i === 2 && <div style={{position: 'absolute', left: w / 2 - 14, top: -90, width: 16, height: 90, background: '#3a3a48', border: `5px solid ${TINTA}`, clipPath: 'polygon(50% 0, 100% 100%, 0 100%)'}} />}
				{Array.from({length: Math.floor(a / 40)}, (_, j) => (
					<div key={j} style={{position: 'absolute', left: 12, top: 16 + j * 40, width: w - 36, height: 12, background: 'rgba(255,230,150,0.5)'}} />
				))}
			</div>
		))}
	</div>
);

const Nubarrones: React.FC<{x: number; y: number; rayo: number}> = ({x, y, rayo}) => {
	const f = useCurrentFrame();
	const t = f - rayo;
	return (
		<>
			{[-240, -80, 80, 240].map((dx, i) => (
				<div key={i} style={{position: 'absolute', left: x + dx - 170 + Math.sin(f / 20 + i) * 10, top: y - 90 + (i % 2) * 30, width: 340, height: 180, borderRadius: '50%', background: '#3a3e4a', border: `7px solid ${TINTA}`}} />
			))}
			{t >= 0 && t < 8 && (
				<svg width={200} height={420} viewBox="0 0 200 420" style={{position: 'absolute', left: x - 100, top: y + 40, overflow: 'visible'}}>
					<polygon points="110,0 40,190 100,190 50,420 170,150 110,150 160,0" fill="#ffe86a" stroke={TINTA} strokeWidth={8} />
				</svg>
			)}
		</>
	);
};

/** el mapa del Atlántico con el mar extendido a todo su ancho (EscMapa solo pinta 1920 px de fondo) */
export const MapaAncho: React.FC<{tono?: 'pergamino' | 'oscuro'}> = ({tono = 'pergamino'}) => (
	<>
		<div style={{position: 'absolute', left: -400, top: -200, width: 4640, height: 1480, background: tono === 'pergamino' ? '#c9b98a' : '#14181e'}} />
		<EscMapa tono={tono} />
	</>
);

const Oceano: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const llega = pal(102, 'Nueva');
	const s0 = 1.15;
	const viaje = tr(f, d + 2, llega - 4);
	return (
		<Toma
			escena={<MapaAncho />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => {
				const v = tr(ff, d + 2, llega - 4);
				return {s: s0 + 0.12 * tr(ff, llega, h), x: interpolate(v, [0, 1], [-(3170 - 960) * s0, 100]), y: 40};
			}}
			encima={f >= llega && f < llega + 10 ? <div style={{position: 'absolute', inset: 0, background: 'rgba(255,255,240,1)', opacity: interpolate(f, [llega, llega + 1, llega + 10], [0, 0.35, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}} /> : undefined}
			tinte={`rgba(30,30,60,${0.6 * tr(f, d + 2 + (llega - 4 - d - 2) * 0.7, llega - 4)})`}
		>
			<Skyline x={430} y={470} sube={tr(f, llega - 10, llega + 4)} />
			<Nubarrones x={430} y={150} rayo={llega} />
		</Toma>
	);
};

/* ---------- muletilla 2 ---------- */

const Muletilla: React.FC<P> = (p) => <PlanoMuletilla {...p} i={100} n={2} />;

export const PLANOS_C3: Plano[] = [
	{n: 'c3-cartel', d: antes(ini(86)), e: 'latigoDer', C: Cartel},
	{n: 'c3-despacho', d: antes(pal(86, 'ir')), e: 'latigoIzq', C: Despacho},
	{n: 'c3-nino', d: ini(87), e: 'zoom', C: NinoBueno},
	{n: 'c3-cree', d: ini(89), e: 'latigoDer', C: SeLoCree},
	{n: 'c3-museo', d: antes(pal(90, 'frase')), e: 'latigoIzq', C: Museo},
	{n: 'c3-domador', d: ini(91), e: 'latigoDer', C: Domador},
	{n: 'c3-semanas', d: ini(92), e: 'zoom', C: Semanas},
	{n: 'c3-cremallera', d: antes(pal(94, 'prohíben')), e: 'latigoIzq', C: Cremallera_},
	{n: 'c3-jarra26', d: ini(96), e: 'latigoDer', C: Jarra26},
	{n: 'c3-hemiciclo12', d: ini(98), e: 'latigoArriba', C: Hemiciclo12},
	{n: 'c3-startup', d: ini(99), e: 'latigoIzq', C: Startup},
	{n: 'c3-muletilla', d: ini(100), e: 'zoom', C: Muletilla},
	{n: 'c3-quedado', d: ini(101), e: 'latigoDer', C: Quedado},
	{n: 'c3-oceano', d: ini(102), e: 'latigoIzq', C: Oceano},
];

export const SONIDOS_C3: [string, number, number][] = [
	['tintineo', pal(87, 'niño') - 2, 0.6],
	['chispas', ini(88) + 1, 0.4],
	['rasga', pal(90, 'Levanta'), 0.8],
	['latigo', ini(91) + 6, 0.8],
	['ronroneo', ini(91) + 2, 0.6],
	['cadena', pal(91, 'aflojarle'), 0.8],
	['hoja', ini(92) + 10, 0.6],
	['hoja', ini(92) + 22, 0.6],
	['rugido', ini(93) - 4, 1.0],
	['crack', ini(93) - 1, 0.8],
	['cremallera', pal(94, 'hablar') - 2, 0.9],
	['pop', antes(ini(95)), 0.6],
	['burbujas', ini(96) + 8, 0.4],
	['boing', ini(97) - 2, 0.5],
	['derrape', pal(99, 'inversionistas'), 0.6],
	['sello', golpeMuletilla(100), 1.0],
	['trueno', pal(102, 'Nueva'), 0.9],
];

