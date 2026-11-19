import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {GolpeSello, SelloGoma} from '../componentes/Recurrentes';
import {Toma} from '../componentes/Toma';
import {FUNCIONARIO, HINDENBURG, HITLER_BUROCRATA, HITLER_MESERO, HITLER_TRAJE, UNIFORME_MARRON} from '../componentes/Vestuario';
import {EscLiso, EscMesaArriba, Humo} from '../escenarios/Epoca';
import {CONDENSADA, SERIF, TITULAR} from '../fuentes';
import {P, Plano, TINTA, antes, centrar, fin, golpeCam, ini, mezclaCam, pal, pop} from './base';
import {PlanoMuletilla, brazo, golpeMuletilla} from './compartidas';
import {
	AYUDANTE,
	AYUDANTE_2,
	AlbumSellos,
	BandejaSopa,
	BigoteVivo,
	BotaGigante,
	CalendarioHojas,
	CartelCampana,
	EscComedor,
	EscImperial,
	EscLadrillo,
	EscVentanilla,
	EscritorioFrente,
	HindenburgSelloHabla,
	HojaSellos,
	LupaMundo,
	MapaBraunau,
	Medallas,
	MesaMantel,
	MontonPapeles,
	Papeleta,
	Pasaporte,
	RelojArena,
	SobreMatasellos,
	tr,
} from './utileria_c345';

/* CAPÍTULO 5 · EL CARTERO (frases 121–141). Paleta: azul imperial, oro de medallas, amarillo de correos. */

export {AlbumSellos};

/* ---------- el sobre con matasellos de 1932 (rótulo) ---------- */

const Sobre: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#1c2c5a" luz="255,226,160" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.12], r: [-2, 1]}}>
		<SobreMatasellos x={960} y={540} ancho={1080} matasellos={d + 8} />
	</Toma>
);

/* ---------- Hindenburg monumental; el bigote frunce el ceño ---------- */

const Monumental: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const b = pal(122, 'bigote') - 2;
	return (
		<Toma
			escena={<EscImperial brillo={0.5} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => golpeCam(ff, b, mezclaCam(centrar(960, 700, 1.08), centrar(960, 380, 1.12), tr(ff, d, b - 4)), centrar(960, 250, 1.9))}
			angulo={14}
		>
			<Actor x={960} y={1560} alto={1700}>
				<Muneco ropa={HINDENBURG} pose={{...manosEn([150, 560], [250, 560]), mi: 'puno', md: 'puno', cuerpo: 0}} ojos="normal" cejas="enojado" boca="seria" />
			</Actor>
			<Medallas x={800} y={590} tam={70} />
			<BigoteVivo x={960} y={246} ancho={540} frunce={tr(f, b, b + 6)} />
		</Toma>
	);
};

/* ---------- como quien mira a un mesero maleducado ---------- */

const Mesero: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const m = pal(123, 'mesero') - 4;
	const inclina = tr(f, m, m + 6);
	const mancha = tr(f, m + 4, m + 16);
	return (
		<Toma escena={<EscComedor />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.12], x: [30, -20]}} angulo={4}>
			<Actor x={640} y={1060} alto={900}>
				<Muneco ropa={HINDENBURG} pose={{...manosFrente([170, 600], [230, 600]), mi: 'puno', md: 'puno', cabeza: 6}} ojos="entrecerrados" cejas="enojado" boca={inclina > 0.5 ? 'mueca' : 'seria'} />
			</Actor>
			<Actor x={1310} y={1010} alto={820}>
				<Muneco ropa={HITLER_MESERO} pose={{...brazo(-1, alcanzar(-1, 20, 410)), mi: 'agarra', ...manosEn(undefined, [250, 540]), md: 'relajada', cuerpo: -4 * inclina}} objIzq={<BandejaSopa inclina={inclina} />} ojos={inclina > 0.5 ? 'grandes' : 'normal'} cejas="preocupado" boca={inclina > 0.5 ? 'o' : 'sonrisa'} />
			</Actor>
			<MesaMantel x={900} y={700} ancho={1300} />
			{/* la sopa derramada que chorrea por el mantel */}
			{mancha > 0 && (
				<svg width={600} height={400} viewBox="0 0 600 400" style={{position: 'absolute', left: 820, top: 690, overflow: 'visible'}}>
					<path d={`M 40 10 Q 200 ${-10} 360 12 L 340 ${20 + 160 * mancha} Q 320 ${40 + 190 * mancha} 300 ${20 + 160 * mancha} L 260 30 L 220 ${30 + 240 * mancha} Q 200 ${50 + 260 * mancha} 180 ${30 + 240 * mancha} L 150 30 L 90 ${30 + 120 * mancha} Q 70 ${50 + 130 * mancha} 56 ${30 + 120 * mancha} Z`} fill="#e9a03a" stroke={TINTA} strokeWidth={6} strokeLinejoin="round" />
				</svg>
			)}
			<div style={{position: 'absolute', left: 540, top: 682, width: 200, height: 30, borderRadius: '50%', background: '#fff', border: `6px solid ${TINTA}`}} />
		</Toma>
	);
};

/* ---------- «el cabo bohemio»: el cartel del nombre ---------- */

const CartelNombre: React.FC<{x: number; y: number; tacha: number; escribe: number}> = ({x, y, tacha, escribe}) => {
	const f = useCurrentFrame();
	return (
		<div style={{position: 'absolute', left: x - 170, top: y, width: 340, height: 170}}>
			<svg width={340} height={60} style={{position: 'absolute', left: 0, top: -58}}>
				<path d="M 60 58 L 170 0 L 280 58" stroke={TINTA} strokeWidth={5} fill="none" />
			</svg>
			<div style={{position: 'absolute', inset: 0, background: '#f4efe0', border: `7px solid ${TINTA}`, textAlign: 'center', fontFamily: CONDENSADA, color: '#2a2218'}}>
				<div style={{fontSize: 52, marginTop: 8, position: 'relative', display: 'inline-block'}}>
					A. HITLER
					{f >= tacha && <div style={{position: 'absolute', left: -10, right: -10, top: '48%', height: 10, background: '#c4262e', transform: `scaleX(${tr(f, tacha, tacha + 5)})`, transformOrigin: '0 50%'}} />}
				</div>
				{f >= escribe && <div style={{fontFamily: "'Comic Sans MS', 'Bradley Hand', cursive", fontWeight: 700, fontSize: 40, color: '#c4262e', transform: 'rotate(-4deg)', clipPath: `inset(0 ${100 - 100 * tr(f, escribe, escribe + 10)}% 0 0)`}}>el cabo bohemio</div>}
			</div>
		</div>
	);
};

const Cabo: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscImperial />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(interpolate(tr(ff, d, h), [0, 1], [1000, 900]), 560, 1.06)} angulo={8}>
		<Actor x={1320} y={1300} alto={1300}>
			<Muneco ropa={HINDENBURG} pose={{...brazo(-1, alcanzar(-1, -40, 560)), mi: 'senala', ...manosEn(undefined, [260, 560]), md: 'puno', cabeza: 10}} ojos="entrecerrados" cejas="enojado" boca="mueca" />
		</Actor>
		<Actor x={560} y={1010} alto={420}>
			<Muneco ropa={HITLER_TRAJE} pose={{...manosFrente([180, 520], [220, 520]), mi: 'agarra', md: 'agarra', cabeza: -12}} ojos="grandes" cejas="enojado" boca="mueca" />
		</Actor>
		<CartelNombre x={560} y={790} tacha={pal(124, 'nombre') - 2} escribe={pal(124, 'cabo') - 3} />
	</Toma>
);

/* ---------- los dos Braunau ---------- */

const Braunau: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const x = pal(125, 'Bohemia') - 2;
	const ok = pal(125, 'Ni', 2) - 2;
	return (
		<Toma escena={<MapaBraunau marca={tr(f, d + 6, d + 12)} equis={x} check={ok} puntero={tr(f, d - 2, d + 10)} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => mezclaCam(centrar(760, 500, 1.2), centrar(1180, 600, 1.2), tr(ff, x + 4, ok))} />
	);
};

/* ---------- presentarse a presidente contra él: los carteles ---------- */

const Brocha: React.FC = () => (
	<g transform="rotate(180 0 36)">
		<rect x={-8} y={-60} width={16} height={100} rx={6} fill="#7a5230" stroke={TINTA} strokeWidth={5} />
		<rect x={-30} y={-100} width={60} height={44} rx={6} fill="#e6dcc0" stroke={TINTA} strokeWidth={5} />
	</g>
);

const Carteles: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const pega = tr(f, d + 6, d + 40);
	return (
		<Toma escena={<EscLadrillo tono="#5a4a44" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1], x: [40, -20]}} angulo={-2}>
			<CartelCampana x={620} y={120} ancho={460} cara="hindenburg" nombre="HINDENBURG" />
			<CartelCampana x={1190} y={250} ancho={330} cara="hitler" nombre="HITLER" pega={pega} />
			<Actor x={1520} y={1000} alto={700}>
				<Muneco ropa={HITLER_TRAJE} pose={{...brazo(-1, alcanzar(-1, -30, 300 + Math.sin(f / 4) * 30)), mi: 'agarra', ...manosEn(undefined, [260, 540]), md: 'relajada'}} objIzq={<Brocha />} ojos="feliz" cejas="arrogante" boca="sonrisa" />
			</Actor>
		</Toma>
	);
};

/* ---------- un detallito: la letra chica ---------- */

const Detallito: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const g = ini(128) - 2;
	const lupa = tr(f, d + 4, g);
	return (
		<Toma escena={<EscLadrillo tono="#5a4a44" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => golpeCam(ff, g, centrar(960, 470, 1.08), centrar(960, 778, 2.7))}>
			<CartelCampana x={960} y={60} ancho={560} cara="hitler" nombre="HITLER" letraChica="Candidato: A. Hitler · Profesión: escritor · NACIONALIDAD: NINGUNA" />
			<LupaMundo x={interpolate(lupa, [0, 1], [1500, 1010])} y={interpolate(lupa, [0, 1], [900, 740])} tam={240} rot={-24} />
		</Toma>
	);
};

/* ---------- renunció a ser austríaco: siete años sin nacionalidad ---------- */

const PapelRasgado: React.FC<{x: number; y: number; ancho: number; rasga: number; lineas: string[]}> = ({x, y, ancho, rasga, lineas}) => {
	const alto = ancho * 0.66;
	const mitad = (l: -1 | 1) => (
		<div style={{position: 'absolute', left: x - ancho / 2 + (l > 0 ? ancho / 2 : 0) + l * rasga * 120, top: y - alto / 2 + rasga * 80, width: ancho / 2, height: alto, overflow: 'hidden', transform: `rotate(${l * rasga * 30}deg)`, opacity: interpolate(rasga, [0.7, 1], [1, 0.0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
			<div style={{position: 'absolute', left: l > 0 ? -ancho / 2 : 0, top: 0, width: ancho, height: alto, background: '#f4efe0', border: `6px solid ${TINTA}`, boxSizing: 'border-box', textAlign: 'center', fontFamily: CONDENSADA, color: '#2a2218', paddingTop: alto * 0.14}}>
				{lineas.map((t, i) => (
					<div key={i} style={{fontSize: ancho * (i ? 0.08 : 0.11), lineHeight: 1.1}}>
						{t}
					</div>
				))}
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

const Renuncia: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const r = pal(129, 'renunciado') - 2;
	const rasga = tr(f, r, r + 14);
	const sie = pal(129, 'siete') - 8;
	return (
		<Toma escena={<EscLiso color="#2a3048" luz="230,230,240" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.12], x: [-20, -60]}} angulo={-4}>
			<Actor x={700} y={1010} alto={760}>
				<Muneco ropa={HITLER_TRAJE} pose={rasga > 0 ? {...manosEn([40, 380], [360, 380]), mi: 'agarra', md: 'agarra'} : {...manosFrente([140, 440], [260, 440]), mi: 'agarra', md: 'agarra'}} ojos={rasga > 0.3 ? 'entrecerrados' : 'normal'} cejas="arrogante" boca="seria" />
			</Actor>
			<PapelRasgado x={700} y={610} ancho={300} rasga={rasga} lineas={['CIUDADANÍA', 'AUSTRÍACA']} />
			<CalendarioHojas x={1400} y={300} ancho={380} textos={['1925', '1926', '1927', '1928', '1929', '1930', '1931', '1932']} cambios={[0, 1, 2, 3, 4, 5, 6].map((i) => sie + i * 4)} cabecera="SIN NACIONALIDAD" color="#5a5e6a" />
		</Toma>
	);
};

/* ---------- la ventanilla: SIN NACIONALIDAD ---------- */

const Ventanilla: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const st = pal(131, 'PASAPORTE');
	return (
		<Toma escena={<EscVentanilla />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.14], y: [-20, -40]}} angulo={-6}>
			<Actor x={1180} y={980} alto={760}>
				<Muneco ropa={FUNCIONARIO} pose={{...manosFrente([150, 560], [250, 520 + (f >= st - 6 && f < st + 4 ? 60 : 0)]), mi: 'agarra', md: 'puno'}} ojos="entrecerrados" cejas="neutral" boca="seria" />
			</Actor>
			<div style={{position: 'absolute', left: 0, right: 0, top: 680, height: 60, background: '#6a4a2a', border: `9px solid ${TINTA}`}} />
			<Pasaporte x={1130} y={640} ancho={330} rot={-3} sello={{texto: 'SIN NACIONALIDAD', desde: st, color: '#c4262e'}} />
			<SelloGoma x={1220} y={680} desde={st} tam={170} />
			<Actor x={520} y={1150} alto={720}>
				<Muneco ropa={HITLER_TRAJE} pose={{...manosFrente([140, 470], [260, 470]), mi: 'agarra', md: 'agarra', cabeza: 6}} ojos={f >= st ? 'grandes' : 'normal'} cejas={f >= st ? 'preocupado' : 'arrogante'} boca={f >= st ? 'o' : 'sonrisa'} />
			</Actor>
			<div style={{position: 'absolute', left: 340, top: 640, width: 360, padding: '10px 0', background: '#f4efe0', border: `7px solid ${TINTA}`, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 40, lineHeight: 1.05, color: '#2a2218', transform: 'rotate(-3deg)'}}>
				«ALEMANIA PARA
				<br />
				LOS ALEMANES»
			</div>
		</Toma>
	);
};

/* ---------- el estado de Brunswick lo nombra funcionario ---------- */

const Brunswick: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #8a96a8, #c9cfd6)'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(960, interpolate(tr(ff, d, h), [0, 1], [380, 560]), 1.1)}>
		<div style={{position: 'absolute', left: 260, top: 120, width: 1400, height: 900, background: '#d9d2bc', border: `10px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 200, top: 60, width: 1520, height: 90, background: '#cfc8b0', border: `10px solid ${TINTA}`, clipPath: 'polygon(0 100%, 6% 0, 94% 0, 100% 100%)'}} />
		{[0, 1, 2, 3].map((i) => (
			<React.Fragment key={i}>
				<div style={{position: 'absolute', left: 360 + i * 340, top: 300, width: 200, height: 280, background: '#2a3040', border: `8px solid ${TINTA}`, overflow: 'hidden'}}>
					{(i === 1 || i === 2) && (
						<div style={{position: 'absolute', left: -60, top: 30, width: 320, height: 720}}>
							<Actor x={160} y={700} alto={640}>
								<Muneco ropa={UNIFORME_MARRON} pose={{...manosFrente([170, 540], [230, 540]), mi: 'puno', md: 'puno'}} ojos="entrecerrados" cejas="enojado" boca="seria" semilla={i} />
							</Actor>
						</div>
					)}
				</div>
			</React.Fragment>
		))}
		<div style={{position: 'absolute', left: 560, top: 180, width: 800, padding: '10px 0', background: '#2a2218', border: `6px solid ${TINTA}`, textAlign: 'center', fontFamily: SERIF, fontWeight: 900, fontSize: 40, color: '#e9c46a', letterSpacing: 3}}>GOBIERNO DEL ESTADO · BRUNSWICK</div>
		<div style={{position: 'absolute', left: 840, top: 700, width: 240, height: 320, background: '#3a2414', border: `9px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: 1010, bottom: -40, background: '#6a6a70', borderTop: `8px solid ${TINTA}`}} />
	</Toma>
);

/* ---------- el nombramiento ---------- */

const Nombramiento: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscMesaArriba tono="madera" luz={[960, 500]} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], r: [2, -1]}}>
		<div style={{position: 'absolute', left: 560, top: 110, width: 800, height: 880, background: '#f6efdc', border: `8px solid ${TINTA}`, boxShadow: '18px 22px 0 rgba(0,0,0,0.3)', transform: 'rotate(-2deg)', padding: 50, boxSizing: 'border-box', fontFamily: SERIF, color: '#2a2218'}}>
			<div style={{textAlign: 'center', fontFamily: CONDENSADA, fontSize: 86, letterSpacing: 4}}>NOMBRAMIENTO</div>
			<div style={{height: 5, background: '#2a2218', margin: '10px 60px 40px'}} />
			<div style={{fontSize: 48, lineHeight: 1.5}}>
				<b>Sr. A. Hitler</b>
				<br />
				Funcionario público del Estado de Brunswick
			</div>
			{[0, 1, 2].map((i) => (
				<div key={i} style={{height: 9, background: '#cfc4a8', borderRadius: 5, margin: '30px 0', width: `${[90, 76, 84][i]}%`}} />
			))}
			<GolpeSello x={520} y={700} desde={pal(132, 'público') - 2} texto="APROBADO" tam={86} rot={-10} color="#c8202a" />
			<GolpeSello x={300} y={600} desde={pal(132, 'ciudadanía') - 2} texto="+ CIUDADANÍA" tam={64} rot={8} color="#2f8a4a" />
		</div>
	</Toma>
);

/* ---------- Hitler de burócrata ---------- */

const Burocrata: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sube = Math.abs(Math.sin(f / 4));
	const pas = tr(f, pal(133, 'escritorio') - 6, pal(133, 'escritorio') + 6);
	return (
		<Toma escena={<EscLiso color="#4a4438" luz="255,236,190" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.18], y: [-20, -40]}} angulo={-8}>
			<Actor x={960} y={1060} alto={780}>
				<Muneco ropa={HITLER_BUROCRATA} pose={{...manosFrente([170, 600], [260, 560 + sube * 40]), mi: 'relajada', md: 'agarra', cabeza: 8}} objDer={<g transform="rotate(180 0 36)"><rect x={-8} y={-50} width={16} height={50} fill="#8a5a32" stroke={TINTA} strokeWidth={4} /><rect x={-24} y={-62} width={48} height={16} fill="#5a3a22" stroke={TINTA} strokeWidth={4} /></g>} ojos="entrecerrados" cejas="preocupado" boca="mueca" />
			</Actor>
			<EscritorioFrente x={960} y={660} ancho={760} color="#5a4a3a" />
			<MontonPapeles x={700} y={668} ancho={230} alto={420} />
			<MontonPapeles x={1220} y={668} ancho={230} alto={460} />
			<Pasaporte x={interpolate(pas, [0, 1], [2200, 1000])} y={630} ancho={260} rot={-6} sello={{texto: 'CIUDADANO', desde: -1e9, color: '#2f8a4a'}} />
		</Toma>
	);
};

/* ---------- y Hindenburg lo aplasta (y Hitler vuelve a inflarse) ---------- */

const Aplasta: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const a = pal(134, 'aplasta') - 2;
	const sube = ini(135) - 4;
	const baja = f < sube ? tr(f, a - 6, a, (u) => u * u) : 1 - tr(f, sube, sube + 8);
	const aplastado = f >= a && f < sube + 8;
	const infla = f >= sube + 8 ? Math.min(1.08, 0.12 + pop(f, sube + 8, 10) * 0.88) : aplastado ? 0.12 : 1;
	return (
		<Toma escena={<EscLiso color="#2a3048" luz="230,230,240" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(960, 600, 1.05)} sacudida={(ff) => (ff >= a && ff < a + 10 ? 14 * (1 - (ff - a) / 10) : 0)}>
			<Papeleta x={960} y={1000} ancho={1100} />
			<div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transform: `scaleY(${infla})`, transformOrigin: '960px 930px'}}>
				<Actor x={960} y={930} alto={330}>
					<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([60, 300], [340, 300]), mi: 'abierta', md: 'abierta'}} ojos={aplastado ? 'x' : 'grandes'} cejas="preocupado" boca="o" />
				</Actor>
			</div>
			<BotaGigante x={960} y={940} baja={baja} />
		</Toma>
	);
};

/* ---------- le exige que lo nombre jefe de gobierno ---------- */

const Exige: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const golpe = Math.abs(Math.sin(f / 4));
	return (
		<Toma escena={<EscImperial />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.12], x: [-30, 20]}} angulo={5}>
			<Actor x={1260} y={1120} alto={960}>
				<Muneco ropa={HINDENBURG} pose={{...manosFrente([170, 600], [230, 600]), mi: 'puno', md: 'puno'}} ojos="entrecerrados" cejas="enojado" boca="seria" />
			</Actor>
			<EscritorioFrente x={1260} y={680} ancho={800} color="#4a2a1a" />
			<Actor x={560} y={1030} alto={700}>
				<Muneco ropa={HITLER_TRAJE} pose={{...brazo(1, {a: 60 + 50 * golpe, c: 50}), md: 'puno', ...manosEn([140, 540]), mi: 'puno', cuerpo: 4}} ojos="grandes" cejas="enojado" boca="grito" />
			</Actor>
		</Toma>
	);
};

/* ---------- lo escucha un rato: reloj de arena cortísimo ---------- */

const RelojCorto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscImperial />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.18], x: [0, -30]}} angulo={4}>
			<Actor x={1250} y={1200} alto={1060}>
				<Muneco ropa={HINDENBURG} pose={{...manosFrente([170, 640], [230, 640]), mi: 'puno', md: 'puno', cabeza: -6}} ojos="cerrados" cejas="neutral" boca="seria" />
			</Actor>
			<EscritorioFrente x={960} y={840} ancho={1900} color="#4a2a1a" />
			<RelojArena x={700} y={846} alto={240} t={tr(f, d + 4, d + 22)} />
		</Toma>
	);
};

/* ---------- y le dice que no: la puerta en la cara ---------- */

const PuertaEnLaCara: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const P0 = pal(137, 'NO') - 1;
	const cierra = tr(f, P0 - 6, P0, (u) => u * u);
	return (
		<Toma escena={<EscImperial />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.12, 1.18]}} angulo={-6} sacudida={(ff) => (ff >= P0 && ff < P0 + 10 ? 14 * (1 - (ff - P0) / 10) : 0)}>
			{/* marco de la puerta con el pasillo iluminado */}
			<div style={{position: 'absolute', left: 680, top: 140, width: 560, height: 860, background: '#e6d6b0', border: `14px solid #3a2414`, outline: `7px solid ${TINTA}`}} />
			<Actor x={960} y={1000} alto={640}>
				<Muneco ropa={HITLER_TRAJE} pose={{...manosFrente([150, 470], [250, 470]), mi: 'agarra', md: 'agarra'}} ojos={f >= P0 ? 'cerrados' : 'normal'} cejas="enojado" boca={f >= P0 ? 'mueca' : 'abierta'} />
			</Actor>
			{/* la hoja de la puerta (de espaldas: sin placa) */}
			<div style={{position: 'absolute', left: 690, top: 150, width: 540, height: 850, perspective: 1600}}>
				<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(90deg, #5a321a, #7a4a28 50%, #4a2812)', border: `8px solid ${TINTA}`, transformOrigin: '0 50%', transform: `rotateY(${(1 - cierra) * -82}deg)`}}>
					{[0, 1].map((i) => (
						<div key={i} style={{position: 'absolute', left: 60, right: 60, top: 70 + i * 380, height: 300, border: `6px solid ${TINTA}`, opacity: 0.6}} />
					))}
				</div>
			</div>
		</Toma>
	);
};

/* ---------- con los suyos, soltó: ---------- */

const Sillon: React.FC<{x: number; y: number}> = ({x, y}) => (
	<div style={{position: 'absolute', left: x - 260, top: y - 640, width: 520, height: 640}}>
		<div style={{position: 'absolute', left: 60, right: 60, top: 0, height: 520, background: '#7a1a22', border: `9px solid ${TINTA}`, borderRadius: '120px 120px 20px 20px'}} />
		<div style={{position: 'absolute', left: 0, top: 300, width: 110, height: 300, background: '#8a2a30', border: `9px solid ${TINTA}`, borderRadius: 40}} />
		<div style={{position: 'absolute', right: 0, top: 300, width: 110, height: 300, background: '#8a2a30', border: `9px solid ${TINTA}`, borderRadius: 40}} />
	</div>
);

const Suyos: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscImperial />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1], y: [20, 40]}} angulo={6}>
		<Sillon x={960} y={1000} />
		<Actor x={600} y={1010} alto={800}>
			<Muneco ropa={AYUDANTE} pose={{...manosFrente([180, 520], [220, 520]), mi: 'agarra', md: 'agarra', cuerpo: 8, cabeza: 8}} ojos="feliz" cejas="arrogante" boca="sonrisa" />
		</Actor>
		<Actor x={1330} y={1010} alto={800}>
			<Muneco ropa={AYUDANTE_2} pose={{...manosFrente([180, 520], [220, 520]), mi: 'agarra', md: 'agarra', cuerpo: -8, cabeza: -8}} ojos="feliz" cejas="arrogante" boca="sonrisa" semilla={2} />
		</Actor>
		<Actor x={960} y={1100} alto={900}>
			<Muneco ropa={HINDENBURG} pose={{...manosEn([60, 560], [340, 560]), mi: 'puno', md: 'puno'}} ojos="entrecerrados" cejas="arrogante" boca="picara" />
		</Actor>
		<Humo densidad={0.14} color="230,230,240" />
	</Toma>
);

/* ---------- «Como mucho lo hago director de Correos…»: la imagen del adelanto ---------- */

const SelloCara: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return <Toma escena={<HindenburgSelloHabla habla={f < fin(139)} brillo={0.4 + 0.2 * Math.sin(f / 6)} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], y: [80, 120]}} angulo={8} />;
};

/* ---------- «Para que lama los sellos con mi cara» ---------- */

const Lame: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const lame = Math.sin(f / 3) * 40;
	return (
		<Toma escena={<EscLiso color="#c99a2a" luz="255,240,200" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.1], x: [-20, 20]}} angulo={-6}>
			<div style={{position: 'absolute', left: 1240, top: 110, padding: '10px 26px', background: '#24407a', border: `7px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 52, color: '#e9c46a', letterSpacing: 4}}>CORREOS</div>
			<Actor x={760} y={1260} alto={1100}>
				<Muneco ropa={HITLER_TRAJE} pose={{...manosFrente([250, 470], [330, 470]), mi: 'agarra', md: 'agarra', cabeza: 8}} ojos="cerrados" cejas="preocupado" boca="lengua" />
			</Actor>
			<HojaSellos x={1080} y={250 + lame} ancho={460} rot={-4} />
			<EscritorioFrente x={960} y={900} ancho={1500} color="#24407a">
				<div style={{position: 'absolute', left: 760, top: 930, width: 400, padding: '8px 0', background: 'linear-gradient(180deg, #e9c46a, #b8862a)', border: `6px solid ${TINTA}`, textAlign: 'center', fontFamily: TITULAR, fontWeight: 900, fontSize: 30, color: '#3a2a10', letterSpacing: 2}}>DIRECTOR DE CORREOS</div>
			</EscritorioFrente>
		</Toma>
	);
};

/* ---------- muletilla 3: el sello postal ---------- */

const Muletilla: React.FC<P> = (p) => <PlanoMuletilla {...p} i={140} n={3} postal />;

/* ---------- acuérdate de los sellos: el álbum se cierra ---------- */

const Album: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cierra = tr(f, pal(141, 'Van') - 2, pal(141, 'Van') + 12);
	return (
		<Toma escena={<EscLiso color="#1c2c5a" luz="255,226,160" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => centrar(960, 560, 1.0 + 0.16 * tr(ff, d, h))}>
			<AlbumSellos x={960} y={560} ancho={520} abre={1 - cierra} entra={tr(f, d + 2, d + 16)} brillo={0.5 + 0.4 * Math.sin(f / 4)} />
		</Toma>
	);
};

export const PLANOS_C5: Plano[] = [
	{n: 'c5-sobre', d: fin(120) + 1, e: 'latigoArriba', C: Sobre},
	{n: 'c5-monumental', d: ini(122), e: 'zoom', C: Monumental},
	{n: 'c5-mesero', d: ini(123), e: 'latigoDer', C: Mesero},
	{n: 'c5-cabo', d: ini(124), e: 'latigoIzq', C: Cabo},
	{n: 'c5-braunau', d: ini(125), e: 'latigoDer', C: Braunau},
	{n: 'c5-carteles', d: ini(126), e: 'latigoIzq', C: Carteles},
	{n: 'c5-detallito', d: ini(127), e: 'zoom', C: Detallito},
	{n: 'c5-renuncia', d: ini(129), e: 'latigoDer', C: Renuncia},
	{n: 'c5-ventanilla', d: ini(130), e: 'latigoIzq', C: Ventanilla},
	{n: 'c5-brunswick', d: ini(132), e: 'latigoDer', C: Brunswick},
	{n: 'c5-nombramiento', d: antes(pal(132, 'nombra')), e: 'zoom', C: Nombramiento},
	{n: 'c5-burocrata', d: ini(133), e: 'latigoIzq', C: Burocrata},
	{n: 'c5-aplasta', d: ini(134), e: 'latigoArriba', C: Aplasta},
	{n: 'c5-exige', d: antes(pal(135, 'Hitler')), e: 'latigoDer', C: Exige},
	{n: 'c5-reloj', d: ini(136), e: 'zoom', C: RelojCorto},
	{n: 'c5-portazo', d: ini(137), e: 'latigoIzq', C: PuertaEnLaCara},
	{n: 'c5-suyos', d: ini(138), e: 'latigoDer', C: Suyos},
	{n: 'c5-sellocara', d: ini(139), e: 'zoom', C: SelloCara},
	{n: 'c5-lame', d: antes(pal(139, 'Para')), e: 'latigoIzq', C: Lame},
	{n: 'c5-muletilla', d: ini(140), e: 'zoom', C: Muletilla},
	{n: 'c5-album', d: ini(141), e: 'latigoDer', C: Album},
];

export const SONIDOS_C5: [string, number, number][] = [
	['objeto', fin(120) + 9, 0.8],
	['tintineo', ini(122) + 4, 0.7],
	['salpica', pal(123, 'mesero'), 0.8],
	['garabato', pal(124, 'cabo') - 3, 0.6],
	['beep', pal(125, 'Bohemia') - 2, 0.6],
	['ding', pal(125, 'Ni', 2) - 2, 0.7],
	['hoja', ini(126) + 8, 0.5],
	['rasga', pal(129, 'renunciado') - 2, 0.8],
	['objeto', pal(131, 'PASAPORTE'), 0.9],
	['objeto', pal(132, 'público') - 2, 0.8],
	['objeto', pal(132, 'ciudadanía') - 2, 0.8],
	['aplasta', pal(134, 'aplasta') - 2, 1.0],
	['boing', ini(135) + 4, 0.7],
	['tic', ini(136) + 4, 0.6],
	['puerta', pal(137, 'NO') - 1, 1.0],
	['lamida', antes(pal(139, 'Para')) + 4, 0.7],
	['sello', golpeMuletilla(140), 1.0],
	['chispas', ini(141) + 2, 0.5],
	['cierre', pal(141, 'Van') + 10, 0.8],
];
