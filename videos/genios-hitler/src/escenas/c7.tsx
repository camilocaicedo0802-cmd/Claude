import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {Microfono} from '../componentes/Objetos';
import {Chistera, Contrato, JarraVotos, SelloPostal} from '../componentes/Recurrentes';
import {Toma} from '../componentes/Toma';
import {BANQUERO, FUNCIONARIO, GENERAL, HIJO, HINDENBURG, HITLER_CANCILLER, HITLER_TRAJE, MINISTRO, PAPEN, PRESENTADOR, SENOR_2, SENOR_3, SOCIO} from '../componentes/Vestuario';
import {EscLiso, EscMesaArriba, Hemiciclo} from '../escenarios/Epoca';
import {CONDENSADA} from '../fuentes';
import {P, Plano, TINTA, antes, centrar, clamp, fin, ini, mezclaCam, pal, tramo} from './base';
import {ANGULO_PAPEN, ENCUADRE_CONTRATO, ENCUADRE_VENTANA, OficinaPapen} from './c0';
import {Silla, brazo} from './compartidas';
import {
	BandejaTarjeta,
	Caballo,
	EscCasaNoche,
	EscDesayuno,
	EscEstudioTV,
	EscSalonGenios,
	Grillo,
	ManoPluma,
	Marcador,
	MesaConsejo,
	MesaDesayuno,
	PeonBigote,
	Periodico,
	PuertaPuros,
	SombraHitler,
	Tablero,
	UrnaCerrada,
	Vela,
	aMundo,
} from './utileria_c67';

/* CAPÍTULO 7: LOS GENIOS (1932-1933). Paleta: madera oscura, terciopelo verde, humo de puros, luz de velas. */

/* ---------- rótulo: la tarjeta de visita en bandeja de plata ---------- */

const C7Tarjeta: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscMesaArriba tono="oscura" luz={[960, 520]} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.14], r: [2, -1], y: [0, 20]}}>
		<div style={{position: 'absolute', left: 300, top: 120, width: 1400, height: 1000, background: 'radial-gradient(ellipse, rgba(36,64,44,0.9), rgba(24,48,32,0) 70%)'}} />
		<BandejaTarjeta x={960} y={560} ancho={1100} />
		{/* el guante del mayordomo que la presenta */}
		<div style={{position: 'absolute', left: 1480, top: 640, width: 260, height: 150, background: '#ffffff', border: `8px solid ${TINTA}`, borderRadius: '70px 60px 50px 70px', transform: 'rotate(-14deg)'}} />
		<div style={{position: 'absolute', left: 1680, top: 600, width: 300, height: 170, background: '#1b1b22', border: `8px solid ${TINTA}`, transform: 'rotate(-14deg)'}} />
	</Toma>
);

/* ---------- el concurso: presentación de Papen (aplausos… y grillos) ---------- */

const C7Concurso: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const corte = ini(158);
	const luces = interpolate(f, [corte, corte + 16], [1, 0.35], clamp);
	const reverencia = f < corte ? 18 * Math.max(0, Math.sin(((f - d) / 22) * Math.PI)) : 18;
	return (
		<Toma escena={<EscEstudioTV luces={luces} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.12], x: [-40, 30], y: [30, 50]}} angulo={6}>
			<Caballo x={1290} y={900} tam={360} />
			<Actor x={420} y={1000} alto={720}>
				<Muneco ropa={PRESENTADOR} pose={{...brazo(-1, alcanzar(-1, 150, 300)), mi: 'agarra', ...brazo(1, alcanzar(1, 400, 360)), md: 'abierta', cabeza: 6}} objIzq={<Microfono rot={180} />} ojos={f < corte ? 'feliz' : 'grandes'} cejas={f < corte ? 'neutral' : 'preocupado'} boca={f < corte ? 'sonrisaGrande' : 'mueca'} />
			</Actor>
			<Actor x={960} y={1010} alto={740}>
				<Muneco ropa={PAPEN} pose={{cuerpo: reverencia, cabeza: reverencia * 0.6, ...manosEn([110, 520], [212, 420], {}, true), mi: 'abierta', md: 'oculta'}} ojos={f < corte ? 'feliz' : 'normal'} cejas="arrogante" boca={f < corte ? 'sonrisaGrande' : 'sonrisa'} />
			</Actor>
			{f >= corte + 10 && <Grillo x={640} y={1010} tam={70} />}
		</Toma>
	);
};

/* ---------- 512 a 42 ---------- */

const C7Gobierno: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={
			<>
				<EscSalonGenios humo={0.08} />
				<Hemiciclo x={960} y={760} radio={720} encendidos={0} apagado="#55555e" />
			</>
		}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1.04, 1.12], y: [-20, 10]}}
		angulo={5}
	>
		{/* el atril */}
		<Actor x={960} y={1100} alto={720}>
			<Muneco ropa={PAPEN} pose={{...manosEn(undefined, [212, 420], {}, true), md: 'oculta', ...brazo(-1, alcanzar(-1, 20, 260)), mi: 'abierta', cabeza: -6}} ojos="feliz" cejas="arrogante" boca="sonrisa" />
		</Actor>
		<div style={{position: 'absolute', left: 820, top: 880, width: 280, height: 220, background: 'linear-gradient(180deg, #5a3a22, #3a2414)', border: `9px solid ${TINTA}`, borderRadius: 8}} />
		<div style={{position: 'absolute', left: 780, top: 860, width: 360, height: 36, background: '#6a4426', border: `8px solid ${TINTA}`, borderRadius: 6}} />
	</Toma>
);

const C7Marcador: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cuenta = tramo(f, antes(pal(159, 'quinientos')), pal(159, 'dos') + 4, (u) => u);
	const rep = ini(160);
	return (
		<Toma
			escena={
				<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #0a0e1c 0%, #1a2238 60%, #0e1422 100%)'}}>
					{/* gradas */}
					{Array.from({length: 7}, (_, i) => (
						<div key={i} style={{position: 'absolute', left: -40, right: -40, top: 640 + i * 66, height: 54, background: i % 2 ? '#2a3046' : '#232840', borderTop: `5px solid ${TINTA}`}} />
					))}
					{/* focos del estadio */}
					{[220, 1700].map((x) => (
						<div key={x} style={{position: 'absolute', left: x - 120, top: 40, width: 240, height: 110, background: '#e8eefc', border: `8px solid ${TINTA}`, borderRadius: 10, boxShadow: '0 0 120px 40px rgba(232,238,252,0.35)'}} />
					))}
				</div>
			}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => {
				const a = centrar(960, 470, 1.0 + 0.05 * tramo(ff, d, rep));
				const b = centrar(960, 470, 1.55);
				return mezclaCam(a, b, tramo(ff, rep - 2, rep + 4, (u) => 1 - Math.pow(1 - u, 3)));
			}}
		>
			<Marcador x={960} y={210} ancho={1240} izq={512 * cuenta} der={42 * cuenta} />
			{/* el público abuchea: siluetas con los brazos arriba */}
			{Array.from({length: 14}, (_, i) => {
				const brinca = f >= rep ? Math.abs(Math.sin((f + i * 5) / 4)) * 14 : 0;
				return (
					<div key={i} style={{position: 'absolute', left: 40 + i * 136, top: 900 - brinca + (i % 2) * 40, width: 110, height: 200, background: '#0c0f1a', borderRadius: '55px 55px 10px 10px'}}>
						<div style={{position: 'absolute', left: 25, top: -60, width: 60, height: 60, borderRadius: '50%', background: '#0c0f1a'}} />
					</div>
				);
			})}
		</Toma>
	);
};

/* ---------- el general astuto ---------- */

const C7General: React.FC<P> = ({d, h, e, s}) => {
	const llega = ini(162);
	return (
		<Toma
			escena={<EscSalonGenios humo={0.12} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(f) => mezclaCam(centrar(620, 560, 1.25), centrar(1240, 520, 1.25), tramo(f, d + 6, llega + 4))}
		>
			<Silla x={600} y={980} alto={340} etiqueta="CANCILLER" color="#5a3420" />
			<Actor x={600} y={1000} alto={760}>
				<Muneco ropa={PAPEN} pose={{agacha: 0.55, ...manosFrente([170, 560], [230, 560]), mi: 'relajada', md: 'relajada', pi: 14, pd: 14}} ojos="feliz" cejas="arrogante" boca="sonrisa" />
			</Actor>
			<Actor x={1260} y={1000} alto={800} voltear>
				<Muneco ropa={GENERAL} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno', cabeza: -6}} ojos="entrecerrados" cejas="arrogante" boca="picara" />
			</Actor>
		</Toma>
	);
};

const C7Alguien: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscSalonGenios humo={0.14} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.2], x: [40, -20], y: [40, 60]}}>
		{/* al fondo, Papen saluda a alguien, ajeno */}
		<Actor x={1500} y={880} alto={480}>
			<Muneco ropa={PAPEN} pose={{...brazo(1, alcanzar(1, 340, 200)), md: 'abierta'}} ojos="feliz" cejas="arrogante" boca="sonrisa" />
		</Actor>
		<Actor x={560} y={1010} alto={800}>
			<Muneco ropa={SENOR_2} pose={{...brazo(1, alcanzar(1, 380, 260)), md: 'abierta', ...manosEn([150, 548]), mi: 'puno', cuerpo: 8, cabeza: 10}} ojos="grandes" cejas="preocupado" boca="o" hablando={useCurrentFrame() < fin(163) - 20} />
		</Actor>
		<Actor x={900} y={1010} alto={800} voltear>
			<Muneco ropa={GENERAL} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno', cabeza: -4}} ojos="entrecerrados" cejas="arrogante" boca="picara" />
		</Actor>
	</Toma>
);

/* ---------- «No tiene que ser una cabeza. Es un sombrero.» ---------- */

const C7Sombrero: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cambio = antes(pal(164, 'Es'));
	const esSombrero = f >= cambio && f < pal(164, 'sombrero') + 14;
	const PX = 1240;
	const PY = 1010;
	const PA = 820;
	const [hx, hy] = aMundo(PX, PY, PA, 200, 300);
	return (
		<Toma escena={<EscSalonGenios humo={0.16} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.18, 1.26], x: [0, -30], y: [80, 100]}} golpes={[[cambio, 0.06]]}>
			<Actor x={680} y={1010} alto={820}>
				<Muneco ropa={GENERAL} pose={{...brazo(1, alcanzar(1, 400, 330)), md: 'abierta', ...manosEn([150, 548]), mi: 'puno', cabeza: 6}} ojos="entrecerrados" cejas="arrogante" boca="picara" hablando={f < fin(164)} />
			</Actor>
			<Actor x={PX} y={PY} alto={PA} voltear>
				<Muneco ropa={PAPEN} pose={{...manosEn(undefined, [212, 420], {}, true), md: 'oculta', cabeza: 4}} ojos="feliz" cejas="arrogante" boca="sonrisa" escalaCabeza={esSombrero ? 0.001 : 1} />
			</Actor>
			{esSombrero && <Chistera x={hx} y={hy} ancho={300} rot={-3} />}
		</Toma>
	);
};

/* ---------- el juego de las sillas ---------- */

const C7Sillas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const para = antes(pal(165, 'quita'));
	const sienta = pal(165, 'queda');
	const t = Math.min(f, para) - d;
	const th = t * 0.11;
	const pos = (fase: number) => ({x: 960 + Math.cos(th + fase) * 360, y: 960 + Math.sin(th + fase) * 50, z: Math.sin(th + fase)});
	const pg = pos(Math.PI);
	const pp = pos(0);
	// el general salta a la silla
	const salto = tramo(f, para + 2, sienta);
	const gx = pg.x + (960 - pg.x) * salto;
	const gy = pg.y + (930 - pg.y) * salto;
	const general = (
		<Actor key="g" x={gx} y={gy} alto={700 + pg.z * 40 * (1 - salto)} voltear={pg.z < 0}>
			<Muneco ropa={GENERAL} camina={f < para ? 1.4 : 0} pose={salto > 0.8 ? {agacha: 0.55, ...manosFrente([170, 560], [230, 560]), pi: 14, pd: 14} : {}} ojos={salto > 0.8 ? 'feliz' : 'entrecerrados'} cejas="arrogante" boca={salto > 0.8 ? 'sonrisaGrande' : 'picara'} />
		</Actor>
	);
	const papen = (
		<Actor key="p" x={pp.x} y={pp.y} alto={700 + pp.z * 40} voltear={pp.z > 0}>
			<Muneco ropa={PAPEN} camina={f < para ? 1.4 : 0} pose={f > sienta ? {...brazo(-1, alcanzar(-1, 40, 380)), mi: 'abierta', ...brazo(1, alcanzar(1, 360, 380)), md: 'abierta'} : {}} ojos={f > sienta ? 'grandes' : 'feliz'} cejas={f > sienta ? 'sorprendido' : 'arrogante'} boca={f > sienta ? 'o' : 'sonrisa'} />
		</Actor>
	);
	const silla = <Silla key="s" x={960} y={970} alto={300} etiqueta="CANCILLER" color="#5a3420" />;
	const capas: [number, React.ReactNode][] = [
		[salto > 0.8 ? 0.01 : pg.z, general],
		[pp.z, papen],
		[0, silla],
	];
	capas.sort((a, b) => a[0] - b[0]);
	return (
		<Toma escena={<EscSalonGenios humo={0.1} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.15], y: [20, 40]}}>
			<div style={{position: 'absolute', left: 480, top: 900, width: 960, height: 130, borderRadius: '50%', background: 'rgba(36,64,44,0.6)', border: '6px solid rgba(20,20,26,0.6)'}} />
			{capas.map(([, el]) => el)}
		</Toma>
	);
};

/* ---------- Papen a la luz de una vela, y el peón con bigote ---------- */

const C7Vela: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const idea = f >= antes(pal(167, 'vengarse'));
	return (
		<Toma escena={<div style={{position: 'absolute', inset: 0, background: '#0a0604'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.3], y: [60, 110]}} angulo={6}>
			<Actor x={960} y={1300} alto={1200}>
				<Muneco ropa={PAPEN} pose={{...manosFrente([170, 520], [230, 520]), mi: 'agarra', md: 'agarra', cabeza: idea ? -6 : 4}} ojos="entrecerrados" cejas={idea ? 'arrogante' : 'enojado'} boca={idea ? 'picara' : 'seria'} />
			</Actor>
			<div style={{position: 'absolute', left: 0, right: 0, top: 860, bottom: 0, background: '#1e120a', borderTop: `9px solid ${TINTA}`}} />
			<Vela x={1380} y={880} alto={300} />
			<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 62% 55%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.7) 80%)'}} />
		</Toma>
	);
};

const C7Peon: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const mueve = tramo(f, ini(168) - 4, ini(168) + 10);
	const px = 900 + mueve * 140;
	const py = 830 - mueve * 70;
	return (
		<Toma escena={<div style={{position: 'absolute', inset: 0, background: '#0a0604'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.25, 1.45], y: [0, 40]}} golpes={[[ini(168), 0.05]]}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 560, bottom: 0, background: '#24402c'}} />
			<Tablero x={960} y={1000} ancho={900} />
			{[[700, 880], [1160, 900], [1040, 700]].map(([x, y], i) => (
				<svg key={i} width={70} height={110} viewBox="0 0 120 200" style={{position: 'absolute', left: x - 35, top: y - 110}}>
					<path d="M 14 186 Q 20 150 42 130 L 78 130 Q 100 150 106 186 Z" fill="#efe6cf" stroke={TINTA} strokeWidth={8} />
					<circle cx={60} cy={92} r={40} fill="#efe6cf" stroke={TINTA} strokeWidth={8} />
				</svg>
			))}
			<PeonBigote x={px} y={py} alto={300 - mueve * 20} />
			{/* el guante de Papen que lo mueve */}
			<div style={{position: 'absolute', left: px - 70, top: py - 380, width: 140, height: 110, background: '#ffffff', border: `8px solid ${TINTA}`, borderRadius: '50px 50px 40px 40px'}} />
			<div style={{position: 'absolute', left: px - 50, top: py - 700, width: 100, height: 340, background: '#5a5f6a', border: `8px solid ${TINTA}`}} />
			<Vela x={1500} y={760} alto={280} />
			<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 60% 50%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.65) 85%)'}} />
		</Toma>
	);
};

/* ---------- la casa del banquero y el hijo del presidente ---------- */

const C7Casa: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscCasaNoche />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.5], x: [0, -140], y: [0, -280]}} />
);

const C7Hijo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscSalonGenios humo={0.1} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.2, 1.3], y: [140, 160], x: [30, -10]}} angulo={6}>
			<Actor x={760} y={1080} alto={1000}>
				<Muneco ropa={HINDENBURG} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno', cabeza: -8}} ojos="mirandoLado" cejas="enojado" boca="seria" />
			</Actor>
			<Actor x={1060} y={1010} alto={880} voltear>
				<Muneco ropa={HIJO} pose={{...brazo(1, alcanzar(1, 305, 196)), md: 'abierta', wd: 50, frenteD: 1, cuerpo: 12, cabeza: 14}} ojos="entrecerrados" cejas="arrogante" boca={Math.floor(f / 4) % 2 ? 'o' : 'picara'} />
			</Actor>
		</Toma>
	);
};

const C7Visita: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const avanza = tramo(f, d - 4, h);
	return (
		<Toma escena={<EscSalonGenios humo={0.12} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], x: [30, -30]}} angulo={7}>
			{/* Hindenburg, enorme, tras su escritorio */}
			<Actor x={1460} y={1180} alto={1180} voltear>
				<Muneco ropa={HINDENBURG} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno'}} ojos="normal" cejas="enojado" boca="seria" />
			</Actor>
			<div style={{position: 'absolute', left: 1150, top: 760, width: 640, height: 400, background: 'linear-gradient(180deg, #3a2414, #24160c)', border: `9px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 1120, top: 740, width: 700, height: 40, background: '#24402c', border: `8px solid ${TINTA}`}} />
			{[PAPEN, BANQUERO, HIJO].map((r, i) => (
				<Actor key={i} x={260 + i * 230 + avanza * 160} y={1020 + i * 6} alto={700}>
					<Muneco ropa={r} camina={1} semilla={i} pose={i === 0 ? {...manosEn(undefined, [212, 420], {}, true), md: 'oculta'} : {}} ojos={i === 0 ? 'feliz' : 'normal'} cejas="arrogante" boca="sonrisa" />
				</Actor>
			))}
		</Toma>
	);
};

/* ---------- «Lo nombramos, pero lo rodeamos de los nuestros»: la jaula de ministros ---------- */

const C7Jaula: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const forma = tramo(f, d - 2, d + 16);
	const RONDA = [
		{r: MINISTRO, x: 560, inc: 14},
		{r: SENOR_3, x: 760, inc: 7},
		{r: BANQUERO, x: 1160, inc: -7},
		{r: FUNCIONARIO, x: 1360, inc: -14},
	];
	return (
		<Toma escena={<EscSalonGenios humo={0.14} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [40, 60]}} angulo={-4}>
			{/* Hitler chiquito en el centro */}
			<Actor x={960} y={1000} alto={470}>
				<Muneco ropa={HITLER_TRAJE} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno'}} ojos="mirandoLado" cejas="enojado" boca="seria" />
			</Actor>
			{RONDA.map(({r, x, inc}, i) => {
				const lado = x < 960 ? 1 : -1;
				const brazos = forma > 0 ? {...brazo(1, alcanzar(1, 200 + lado * 120 + 60, -40)), ...brazo(-1, alcanzar(-1, 200 + lado * 120 - 60, -40)), mi: 'abierta' as const, md: 'abierta' as const} : {};
				return (
					<Actor key={i} x={x + lado * 60 * (1 - forma)} y={1010} alto={800} rot={inc * forma}>
						<Muneco ropa={r} pose={brazos} ojos="feliz" cejas="arrogante" boca="sonrisa" semilla={i} />
					</Actor>
				);
			})}
			{/* la argolla de la jaula, arriba */}
			<svg width={300} height={200} viewBox="0 0 300 200" style={{position: 'absolute', left: 810, top: 40, opacity: forma, overflow: 'visible'}}>
				<path d="M 40 200 Q 150 40 260 200" stroke="#c9a43a" strokeWidth={18} fill="none" />
				<circle cx={150} cy={70} r={36} stroke="#c9a43a" strokeWidth={16} fill="none" />
				<path d="M 40 200 Q 150 40 260 200" stroke={TINTA} strokeWidth={4} fill="none" />
			</svg>
			{/* Papen, satisfecho, lo explica a un lado */}
			<Actor x={1700} y={1040} alto={760} voltear>
				<Muneco ropa={PAPEN} pose={{...brazo(1, alcanzar(1, 380, 330)), md: 'abierta', ...manosEn([150, 548]), mi: 'relajada'}} ojos="feliz" cejas="arrogante" boca="sonrisa" hablando={f >= ini(171) && f < fin(171)} />
			</Actor>
		</Toma>
	);
};

/* ---------- tres de once ---------- */

const C7Ministros: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const marca = tramo(f, antes(pal(173, 'tres')), pal(173, 'tres') + 8);
	return (
		<Toma escena={<EscSalonGenios humo={0.12} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [-10, 20]}}>
			<MesaConsejo
				y={900}
				marca={marca}
				ocupadas={
					<>
						<Actor x={990} y={1060} alto={680}>
							<Muneco ropa={HINDENBURG} pose={{...manosFrente([160, 540], [240, 540]), mi: 'puno', md: 'puno'}} ojos="normal" cejas="enojado" boca="seria" />
						</Actor>
						<Actor x={780} y={1070} alto={620}>
							<Muneco ropa={PAPEN} pose={{...manosFrente([170, 540], [230, 540]), mi: 'relajada', md: 'relajada', cabeza: 8}} ojos="feliz" cejas="arrogante" boca="sonrisa" />
						</Actor>
					</>
				}
			/>
			<div style={{position: 'absolute', left: 1380, top: 170, padding: '8px 40px', background: '#efe8d4', border: `7px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 64, color: '#2a2218', opacity: marca, transform: `scale(${0.8 + 0.2 * marca})`}}>
				<span style={{color: '#8a4a22'}}>3</span> DE 11
			</div>
		</Toma>
	);
};

/* ---------- las riendas ---------- */

const C7Riendas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const riendas = tramo(f, antes(ini(175)), ini(175) + 6);
	const HX = 1260;
	const HY = 1000;
	const HA = 620;
	const PX = 620;
	const PY = 1010;
	const PA = 820;
	const [hi1, hi2] = aMundo(HX, HY, HA, 150, 330);
	const [hd1, hd2] = aMundo(HX, HY, HA, 250, 330);
	const [pm1, pm2] = aMundo(PX, PY, PA, 330, 420);
	const avance = (f - d) * 6;
	return (
		<Toma
			escena={
				<>
					<EscLiso color="#1e1a12" luz="255,214,150" />
					<div style={{position: 'absolute', left: 0, right: 0, top: 960, bottom: 0, background: '#2a1c10', borderTop: `8px solid ${TINTA}`}} />
					{Array.from({length: 12}, (_, i) => (
						<div key={i} style={{position: 'absolute', left: ((i * 240 - avance) % 2160 + 2160) % 2160 - 120, top: 990, width: 120, height: 10, background: 'rgba(0,0,0,0.35)', borderRadius: 5}} />
					))}
				</>
			}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.04, 1.12], x: [20, -20]}}
			angulo={5}
		>
			<Actor x={HX} y={HY} alto={HA}>
				<Muneco ropa={HITLER_TRAJE} camina={1.3} pose={{...manosEn([150, 400], [250, 400]), mi: 'agarra', md: 'agarra', cuerpo: 8}} ojos="grandes" cejas="enojado" boca="mueca" />
			</Actor>
			{/* el saco de votos a la espalda */}
			<div style={{position: 'absolute', left: HX - 170, top: HY - 560, width: 200, height: 230, background: '#c9b48a', border: `8px solid ${TINTA}`, borderRadius: '40% 40% 30% 30%', transform: 'rotate(-12deg)', fontFamily: CONDENSADA, fontSize: 44, color: '#2a2218', textAlign: 'center', lineHeight: '230px'}}>VOTOS</div>
			<Actor x={PX} y={PY} alto={PA}>
				<Muneco ropa={PAPEN} camina={0.8} pose={{...brazo(1, alcanzar(1, 330, 420)), md: 'agarra', ...brazo(-1, alcanzar(-1, 250, 440)), mi: 'agarra', cuerpo: -6}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" />
			</Actor>
			<svg width={1920} height={1080} style={{position: 'absolute', inset: 0, overflow: 'visible', opacity: riendas}}>
				<path d={`M ${pm1} ${pm2} Q ${(pm1 + hi1) / 2} ${pm2 + 60} ${hi1} ${hi2}`} stroke="#5a3420" strokeWidth={10} fill="none" />
				<path d={`M ${pm1} ${pm2 + 10} Q ${(pm1 + hd1) / 2} ${pm2 + 80} ${hd1} ${hd2}`} stroke="#5a3420" strokeWidth={10} fill="none" />
			</svg>
		</Toma>
	);
};

/* ---------- Hindenburg firma ---------- */

const C7Firma: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const g = antes(ini(177));
	const firma = tramo(f, g, g + 14, (u) => u);
	const tx = 680 + 360 * firma;
	const ty = 805 + Math.sin(firma * 18) * 22;
	const tiembla = f >= g - 20 ? Math.sin(f * 2.2) * 4 : 0;
	const cal = f >= antes(ini(178));
	return (
		<Toma escena={<EscMesaArriba tono="oscura" luz={[960, 560]} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.18], y: [0, -30], x: [0, -30]}} golpes={[[g, 0.04]]}>
			<Contrato x={900} y={540} ancho={560} rot={-3} firma={firma} />
			<SelloPostal x={1560} y={250} ancho={200} rot={8 + tiembla} />
			{cal && (
				<div style={{position: 'absolute', left: 230, top: 160, width: 260, height: 300, background: '#f6efdc', border: `7px solid ${TINTA}`, borderRadius: 6, textAlign: 'center', fontFamily: CONDENSADA, color: '#2a2218', transform: `rotate(-6deg) scale(${Math.min(1, 0.6 + (f - antes(ini(178))) * 0.08)})`, boxShadow: '10px 12px 0 rgba(0,0,0,0.3)'}}>
					<div style={{background: '#a8262e', color: '#f6efdc', fontSize: 44, letterSpacing: 3, borderBottom: `5px solid ${TINTA}`}}>ENERO</div>
					<div style={{fontSize: 140, lineHeight: 1.15}}>30</div>
					<div style={{fontSize: 40}}>1933</div>
				</div>
			)}
			<ManoPluma x={tx} y={ty} tam={300} />
		</Toma>
	);
};

/* ---------- canciller: ya no es un chiste (a la altura de los ojos) ---------- */

const C7Canciller: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={
			<>
				<div style={{position: 'absolute', inset: 0, background: '#141210'}} />
				<div style={{position: 'absolute', left: 1180, top: -60, width: 360, height: 1200, background: 'linear-gradient(180deg, rgba(220,214,200,0.22), rgba(220,214,200,0.02))', transform: 'skewX(-14deg)', filter: 'blur(10px)'}} />
				<div style={{position: 'absolute', left: 0, right: 0, top: 900, bottom: 0, background: '#0c0a08'}} />
			</>
		}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1.0, 1.1], y: [60, 90], curva: 'lineal'}}
	>
		<Actor x={960} y={1160} alto={1080}>
			<Muneco ropa={HITLER_CANCILLER} pose={{...manosEn([150, 548], [250, 548]), mi: 'puno', md: 'puno'}} ojos="normal" cejas="neutral" boca="seria" />
		</Actor>
		<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 30%, rgba(0,0,0,0.6) 85%)'}} />
	</Toma>
);

/* ---------- «Sin mayoría. Sin ganar. Por un acuerdo…»: tres zooms de golpe ---------- */

const C7SinMayoria: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={<EscSalonGenios humo={0.06} />}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1, 1]}}
		camFn={(f) => mezclaCam(centrar(960, 520, 1.05), centrar(960, 330, 1.9), tramo(f, d + 2, d + 7, (u) => 1 - Math.pow(1 - u, 3)))}
	>
		<div style={{position: 'absolute', left: 0, right: 0, top: 880, bottom: 0, background: '#2a1a10', borderTop: `9px solid ${TINTA}`}} />
		<JarraVotos x={960} y={890} alto={700} nivel={33.1} />
	</Toma>
);

const C7SinGanar: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		escena={<EscSalonGenios humo={0.06} />}
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1, 1]}}
		camFn={(f) => mezclaCam(centrar(960, 560, 1.05), centrar(960, 600, 1.6), tramo(f, d + 2, d + 7, (u) => 1 - Math.pow(1 - u, 3)))}
	>
		<div style={{position: 'absolute', left: 0, right: 0, top: 880, bottom: 0, background: '#2a1a10', borderTop: `9px solid ${TINTA}`}} />
		<UrnaCerrada x={960} y={900} ancho={560} />
	</Toma>
);

const C7Acuerdo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cierra = tramo(f, antes(pal(180, 'señores')), pal(180, 'despacho') + 2, (u) => u * u);
	return (
		<Toma
			escena={<PuertaPuros cierra={cierra} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => mezclaCam(centrar(960, 560, 1.0), centrar(960, 560, 1.3), tramo(ff, d + 2, d + 7, (u) => 1 - Math.pow(1 - u, 3)))}
			golpes={[[pal(180, 'despacho') + 2, 0.05]]}
		/>
	);
};

/* ---------- «Y Papen, feliz de la vida…»: la escena de la apertura, mismo encuadre, y la cámara sigue ---------- */

const InteriorFeliz: React.FC<{sombra: number}> = ({sombra}) => {
	const f = useCurrentFrame();
	const desliza = tramo(f, ini(182) + 30, pal(182, 'va'));
	return (
		<div style={{position: 'absolute', inset: 0}}>
			<OficinaPapen desliza={desliza} habla={f >= ini(182) && f < fin(182)} />
			{sombra > 0 && <SombraHitler x={1880 - 420 * sombra} y={1000} alto={1100} opacidad={0.6 * sombra} />}
		</div>
	);
};

const C7Feliz: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const va = pal(182, 'va');
	const sombra = tramo(f, va - 10, h - 6);
	return (
		<Toma
			escena={<InteriorFeliz sombra={sombra} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			angulo={ANGULO_PAPEN}
			camFn={(ff) => {
				// el mismo recorrido que la apertura (ventana nevada → contrato)…
				const ida = mezclaCam(ENCUADRE_VENTANA, ENCUADRE_CONTRATO, tramo(ff, ini(182) + 6, va + 4));
				// …y esta vez la cámara sigue: hasta la cara satisfecha de Papen, mientras entra la sombra
				return mezclaCam(ida, centrar(1220, 380, 1.6), tramo(ff, va + 4, h));
			}}
		/>
	);
};

/* ---------- al día siguiente: el socio arrepentido ---------- */

const PERIODICO_CANCILLER = (
	<div style={{position: 'absolute', inset: 0, background: '#9a8e74'}}>
		<div style={{position: 'absolute', left: '22%', top: '18%', width: '56%', height: '82%', background: '#3a3530', borderRadius: '50% 50% 0 0'}} />
		<div style={{position: 'absolute', left: '34%', top: '10%', width: '32%', height: '36%', background: '#e6e0d0', borderRadius: '50%', border: `3px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: '33%', top: '8%', width: '24%', height: '14%', background: '#1a1814', borderRadius: '50% 40% 10% 50%'}} />
		<div style={{position: 'absolute', left: '46%', top: '30%', width: '8%', height: '5%', background: '#1a1814'}} />
	</div>
);

const Desayuno: React.FC<{palmada: number; habla: boolean}> = ({palmada, habla}) => (
	<>
		<EscDesayuno />
		<Actor x={760} y={1150} alto={860}>
			<Muneco
				ropa={SOCIO}
				pose={palmada > 0 ? {...brazo(1, alcanzar(1, 250, 150 + (1 - palmada) * 120)), md: 'abierta', frenteD: 1, ...manosFrente([170, 560]), mi: 'relajada', cabeza: -6 * palmada} : {...manosFrente([170, 560], [240, 560]), mi: 'agarra', md: 'agarra', cabeza: 6}}
				ojos={palmada > 0.5 ? 'cerrados' : 'grandes'}
				cejas={palmada > 0 ? 'preocupado' : 'sorprendido'}
				boca={palmada > 0 ? 'mueca' : 'o'}
				hablando={habla}
			/>
		</Actor>
		<MesaDesayuno y={760} />
		<div style={{position: 'absolute', left: 1080, top: 520, width: 420, height: 525, transform: 'rotate(8deg)'}}>
			<Periodico x={210} y={262} ancho={420} fecha="31 DE ENERO DE 1933" titular="HITLER CANCILLER" foto={PERIODICO_CANCILLER} />
		</div>
	</>
);

const C7Desayuno: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Desayuno palmada={0} habla={false} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], x: [40, -10], y: [10, 30]}} />
);

const C7Palmada: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const golpe = antes(pal(184, 'mayor'));
	const palmada = f < golpe - 6 ? 0 : tramo(f, golpe - 6, golpe);
	return (
		<Toma
			escena={<Desayuno palmada={palmada} habla={f >= ini(184) && f < fin(184)} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => mezclaCam(centrar(900, 460, 1.35), centrar(880, 440, 1.45), tramo(ff, d, h))}
			golpes={[[golpe, 0.04]]}
		/>
	);
};

/* ---------- lista de planos ---------- */

export const PLANOS_C7: Plano[] = [
	{n: 'c7-tarjeta', d: fin(155) + 4, e: 'latigoDer', C: C7Tarjeta},
	{n: 'c7-concurso', d: ini(157), e: 'zoom', C: C7Concurso},
	{n: 'c7-gobierno', d: ini(159), e: 'latigoIzq', C: C7Gobierno},
	{n: 'c7-marcador', d: antes(pal(159, 'votación')), e: 'latigoDer', C: C7Marcador},
	{n: 'c7-general', d: ini(161), e: 'latigoIzq', C: C7General},
	{n: 'c7-alguien', d: ini(163), e: 'latigoDer', C: C7Alguien},
	{n: 'c7-sombrero', d: ini(164), e: 'zoom', C: C7Sombrero},
	{n: 'c7-sillas', d: ini(165), e: 'latigoArriba', C: C7Sillas},
	{n: 'c7-vela', d: ini(166), e: 'latigoIzq', C: C7Vela},
	{n: 'c7-peon', d: antes(pal(167, 'idea')), e: 'zoom', C: C7Peon},
	{n: 'c7-casa', d: ini(169), e: 'latigoDer', C: C7Casa},
	{n: 'c7-hijo', d: antes(pal(169, 'convence')), e: 'latigoIzq', C: C7Hijo},
	{n: 'c7-visita', d: ini(170), e: 'latigoDer', C: C7Visita},
	{n: 'c7-jaula', d: ini(171), e: 'zoom', C: C7Jaula},
	{n: 'c7-ministros', d: ini(172), e: 'latigoIzq', C: C7Ministros},
	{n: 'c7-riendas', d: ini(174), e: 'latigoDer', C: C7Riendas},
	{n: 'c7-firma', d: ini(176), e: 'zoom', C: C7Firma},
	{n: 'c7-canciller', d: ini(179), e: 'latigoArriba', C: C7Canciller},
	{n: 'c7-sinmayoria', d: ini(180), e: 'zoom', C: C7SinMayoria},
	{n: 'c7-singanar', d: antes(pal(180, 'Sin', 2)), e: 'zoom', C: C7SinGanar},
	{n: 'c7-acuerdo', d: antes(pal(180, 'Por')), e: 'zoom', C: C7Acuerdo},
	{n: 'c7-feliz', d: ini(181), e: 'fundido', C: C7Feliz},
	{n: 'c7-desayuno', d: ini(183), e: 'latigoDer', C: C7Desayuno},
	{n: 'c7-palmada', d: ini(184), e: 'zoom', C: C7Palmada},
];

export const SONIDOS_C7: [string, number, number][] = [
	['ding', fin(155) + 8, 0.6],
	['aplausos', ini(157), 0.9],
	['grillos', ini(158) + 4, 0.9],
	['abucheos', ini(160), 1.0],
	['pop', antes(pal(164, 'Es')), 0.7],
	['rayado', antes(pal(165, 'quita')), 0.8],
	['pop', pal(165, 'queda'), 0.7],
	['objeto', ini(168), 0.6],
	['viento', ini(169), 0.5],
	['murmullo', antes(pal(169, 'convence')) + 4, 0.4],
	['clic', ini(171) + 16, 0.7],
	['pop', antes(pal(173, 'tres')), 0.7],
	['garabato', antes(ini(177)), 0.9],
	['puerta', pal(180, 'despacho') + 2, 0.8],
	['hoja', ini(183) + 6, 0.6],
	['palmada', antes(pal(184, 'mayor')), 0.9],
];

