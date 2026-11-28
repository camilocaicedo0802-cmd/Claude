import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {Toma} from '../componentes/Toma';
import {Sello} from '../componentes/Utileria';
import {CONDENSADA} from '../fuentes';
import {Montaje, P, Plano, TINTA, antes, clamp, fin, golpeCam, ini, pal, pop, tramo} from './base';
import {brazo} from './compartidas';
import {Periodico} from './utileria_c89';
import {Escritorio} from './utileria_eiffel';
import {
	Armario,
	BLAIR,
	Bitacora,
	Carta,
	CofaFrente,
	CuentaAtras,
	EscAudiencia,
	EscMuelle,
	EscNocheMar,
	EscPuente,
	Iceberg,
	Llave,
	MesaAudiencia,
	Nudos,
	OFICIAL,
	Pasarela,
	Prismaticos,
	SENADOR,
	Telegrama,
	Titanic,
	VIGIA,
	VIGIA2,
} from './utileria_titanic';

/*
 * Short «La llave del Titanic» (1080x1920, 30 fps). Sin cortes secos: barridos y zooms.
 * Es una tragedia real: no se muestra el choque ni a ninguna víctima; el hundimiento solo aparece como titular.
 */

/** cámara vertical: lleva el punto (wx, wy) del mundo a la altura `sy` de la pantalla, con escala s y sin ver bordes */
const centrarV = (wx: number, wy: number, s: number, sy = 960) => {
	const mx = Math.max(0, (s - 1) * 540);
	const my = Math.max(0, (s - 1) * 960);
	return {s, x: Math.max(-mx, Math.min(mx, -(wx - 540) * s)), y: Math.max(-my, Math.min(my, sy - 960 - (wy - 960) * s))};
};

/** ojos de un Actor (para poner los prismáticos en la cara) */
const ojosDe = (x: number, y: number, alto: number) => ({ox: x, oy: y - alto * (880 / 900) + alto * (205 / 900)});

const VIGIA_CIVIL = {...VIGIA, cabeza: {...VIGIA.cabeza, gorra: undefined}, casaca: '#4a4a56', casacaSombra: '#34343e', chaleco: '#e9e4d6', corbata: '#2a2a30', punos: '#ffffff'};

/** maleta de mano */
const Maleta: React.FC<{x: number; y: number; tam: number}> = ({x, y, tam}) => (
	<div style={{position: 'absolute', left: x - tam / 2, top: y, width: tam, height: tam * 0.7, background: '#7a4a26', border: `${tam * 0.05}px solid ${TINTA}`, borderRadius: tam * 0.08}}>
		<div style={{position: 'absolute', left: '30%', top: -tam * 0.16, width: '40%', height: tam * 0.18, border: `${tam * 0.05}px solid ${TINTA}`, borderBottom: 'none', borderRadius: `${tam * 0.08}px ${tam * 0.08}px 0 0`}} />
		<div style={{position: 'absolute', left: 0, right: 0, top: '45%', height: tam * 0.05, background: '#4a2a14'}} />
	</div>
);

/* ---------------- 0 · gancho: la llave delante del barco ---------------- */

const Gancho: React.FC<{d: number; brillo: number}> = ({d, brillo}) => {
	const f = useCurrentFrame();
	return (
		<>
			<EscNocheMar horizonte={1000} />
			<Titanic x={420 + (f - d) * 0.5} y={1000} ancho={900} luces={1} noche />
			<Iceberg x={985} y={1000} ancho={200} noche silueta={1} />
			<Llave x={560} y={400 + Math.sin(f / 14) * 12} tam={640} rot={-12 + Math.sin(f / 20) * 4} brillo={brillo} />
		</>
	);
};

const T0: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return <Toma escena={<Gancho d={d} brillo={0.3 + 0.7 * tramo(f, antes(pal(0, 'salvar')), pal(0, 'salvar') + 10)} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], y: [0, 40]}} />;
};

/* ---------------- 1 · al bolsillo de un oficial ---------------- */

const T1: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const entra = antes(pal(1, 'bolsillo'));
	const u = tramo(f, d, entra + 4, (t) => t * t);
	const B = {x: 540, y: 2360, alto: 1900};
	const bolsillo = {x: 400, y: 1330};
	return (
		<Toma escena={<EscMuelle />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}}>
			<Actor x={B.x} y={B.y} alto={B.alto}>
				<Muneco ropa={BLAIR} pose={f >= entra + 6 ? {...manosEn([150, 470]), mi: 'abierta', ...manosEn(undefined, [250, 560]), md: 'relajada'} : manosFrente([150, 560], [250, 560])} ojos={f >= entra + 6 ? 'feliz' : 'normal'} cejas="neutral" boca="sonrisa" />
			</Actor>
			{/* bolsillo del pecho */}
			<div style={{position: 'absolute', left: bolsillo.x - 90, top: bolsillo.y, width: 180, height: 120, background: '#141a32', border: `8px solid ${TINTA}`, borderRadius: '0 0 16px 16px'}} />
			{u < 1 && <Llave x={interpolate(u, [0, 1], [760, bolsillo.x])} y={interpolate(u, [0, 1], [200, bolsillo.y + 20])} tam={interpolate(u, [0, 1], [420, 150])} rot={interpolate(u, [0, 1], [-30, 70])} brillo={0.8} etiqueta={false} />}
			{/* solapa del bolsillo encima de la llave */}
			<div style={{position: 'absolute', left: bolsillo.x - 96, top: bolsillo.y - 10, width: 192, height: 54, background: '#1c2340', border: `8px solid ${TINTA}`, borderRadius: 10}} />
		</Toma>
	);
};

/* ---------------- 2 · lo dejan en tierra ---------------- */

const T2: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const tierra = antes(pal(2, 'tierra'));
	return (
		<Toma escena={<EscMuelle />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05], x: [20, -20]}}>
			<Titanic x={1250} y={1340} ancho={2300} luces={0} />
			<Pasarela retira={tramo(f, tierra, tierra + 20)} />
			<Actor x={900} y={1250} alto={560} voltear>
				<Muneco ropa={OFICIAL} pose={{...brazo(1, alcanzar(1, 360, 330)), md: 'abierta'}} ojos="normal" cejas="neutral" boca="seria" />
			</Actor>
			<Actor x={300} y={1720} alto={980}>
				<Muneco ropa={BLAIR} pose={{...manosEn([150, 560]), mi: 'relajada', ...brazo(1, alcanzar(1, 330, 560)), md: 'agarra'}} ojos={f >= tierra ? 'grandes' : 'normal'} cejas={f >= tierra ? 'preocupado' : 'neutral'} boca={f >= tierra ? 'o' : 'sonrisa'} />
			</Actor>
			<Maleta x={470} y={1560} tam={170} />
			<Sello x={540} y={560} texto="SE QUEDA EN TIERRA" desde={tierra} color="#c8202a" tam={54} rot={-6} solido />
		</Toma>
	);
};

/* ---------------- 3 · se va con prisa ---------------- */

const T3: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const x = interpolate(f, [d - 6, h + 6], [180, 900], clamp);
	return (
		<Toma escena={<EscMuelle />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.05], x: [40, -60]}}>
			<Actor x={x} y={1760} alto={1000}>
				<Muneco ropa={BLAIR} camina={2.2} pose={{...brazo(1, alcanzar(1, 330, 560)), md: 'agarra', cuerpo: 8}} ojos="grandes" cejas="preocupado" boca="o" />
			</Actor>
			<Maleta x={x + 150} y={1580} tam={160} />
			{[0, 1, 2].map((i) => (
				<div key={i} style={{position: 'absolute', left: x - 380 - i * 40, top: 1000 + i * 120, width: 220, height: 10, borderRadius: 5, background: 'rgba(255,255,255,0.8)'}} />
			))}
		</Toma>
	);
};

/* ---------------- 4 · la llave del armario de los prismáticos ---------------- */

const T4: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const llave = antes(pal(4, 'llave'));
	const prism = antes(pal(4, 'prismáticos'));
	const tiembla = f >= prism && f < prism + 14 ? Math.sin(f * 2.4) * 6 : 0;
	const sale = interpolate(f, [d, h + 6], [620, 1180], clamp);
	return (
		<Toma escena={<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 35%, #4a3a2e, #1a120c)'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05], y: [0, 20]}}>
			<div style={{position: 'absolute', inset: 0, transform: `translateX(${tiembla}px)`}}>
				<Armario x={540} y={180} ancho={620} cerradura={tramo(f, llave, llave + 8)} />
			</div>
			{/* la silueta de la llave que falta */}
			{f >= llave && (
				<div style={{position: 'absolute', inset: 0, opacity: 0.85 * tramo(f, llave + 4, llave + 12)}}>
					<svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
						<rect x={760} y={540} width={220} height={110} rx={20} fill="none" stroke="#ffd66a" strokeWidth={6} strokeDasharray="18 12" />
						<text x={870} y={615} textAnchor="middle" fontFamily={CONDENSADA} fontSize={64} fill="#ffd66a">?</text>
					</svg>
				</div>
			)}
			{/* el oficial se aleja con la llave en el bolsillo */}
			<Actor x={sale} y={1960} alto={780}>
				<Muneco ropa={BLAIR} camina={1.6} pose={{...brazo(1, alcanzar(1, 330, 560)), md: 'agarra'}} ojos="normal" cejas="neutral" boca="sonrisa" />
			</Actor>
			<Llave x={sale - 60} y={1440} tam={120} rot={60} brillo={0.9 * tramo(f, llave, llave + 8)} etiqueta={false} />
		</Toma>
	);
};

/* ---------------- 5 · los vigías, a ojo ---------------- */

const Cofa: React.FC<{iceberg?: number; asombro?: number; campana?: number; horizonte?: number}> = ({iceberg = 0, asombro = 0, campana = 0, horizonte = 1560}) => (
	<>
		<EscNocheMar horizonte={horizonte} />
		{iceberg > 0 && (
			<div style={{position: 'absolute', inset: 0, opacity: iceberg}}>
				<Iceberg x={910} y={horizonte} ancho={250 + 50 * iceberg} noche silueta={1} />
			</div>
		)}
		<Actor x={300} y={1500} alto={900}>
			<Muneco ropa={VIGIA} pose={asombro ? {...brazo(1, alcanzar(1, 390, 290)), md: 'senala'} : manosFrente([150, 520], [250, 520])} ojos={asombro ? 'grandes' : 'entrecerrados'} cejas={asombro ? 'sorprendido' : 'neutral'} boca={asombro ? 'o' : 'seria'} />
		</Actor>
		<Actor x={640} y={1500} alto={880}>
			<Muneco ropa={VIGIA2} pose={manosFrente([150, 520], [250, 520])} ojos={asombro ? 'grandes' : 'entrecerrados'} cejas={asombro ? 'sorprendido' : 'neutral'} boca={asombro ? 'o' : 'seria'} />
		</Actor>
		<CofaFrente x={540} y={1040} ancho={820} campana={campana} />
	</>
);

const T5: React.FC<P> = ({d, h, e, s}) => <Toma escena={<Cofa />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.0], y: [-40, 0]}} />;

/* ---------------- 6 · 14 de abril, 23:40 ---------------- */

const T6: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscNocheMar horizonte={1300} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}}>
			<Bitacora x={540} y={260} ancho={760} aparece={tramo(f, d, d + 10)} />
			<Titanic x={540 + (f - d) * 0.6} y={1300} ancho={760} luces={1} noche />
		</Toma>
	);
};

const T6b: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const ve = antes(pal(6, 'iceberg'));
	return <Toma escena={<Cofa horizonte={1040} iceberg={tramo(f, d, ve + 6)} asombro={f >= ve ? 1 : 0} campana={tramo(f, ve, ve + 40, (u) => u)} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => golpeCam(ff, ve, {s: 1.0, x: 0, y: 0}, {s: 1.12, x: -60, y: 60})} />;
};

/* ---------------- 7 · quedan 37 segundos ---------------- */

const T7: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const t37 = antes(pal(8, '37'));
	return (
		<Toma escena={<EscNocheMar horizonte={1000} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], x: [0, -30]}} golpes={[[t37, 0.05]]}>
			<Titanic x={330 + (f - d) * 0.9} y={1000} ancho={620} luces={1} noche />
			<Iceberg x={900} y={1000} ancho={230} noche silueta={1} />
			{f >= t37 && (
				<div style={{position: 'absolute', inset: 0, transform: `scale(${1 + 0.3 * Math.max(0, 1 - (f - t37) / 6)})`, transformOrigin: '540px 380px'}}>
					<CuentaAtras x={540} y={250} ancho={560} segundos={37 - (f - t37) / 30} />
				</div>
			)}
		</Toma>
	);
};

/* ---------------- 8 · la audiencia ---------------- */

const Audiencia: React.FC<{pregunta: number; responde: number; esquiva: number}> = ({pregunta, responde, esquiva}) => {
	const f = useCurrentFrame();
	const S = {x: 270, y: 1560, alto: 1080};
	const {ox, oy} = ojosDe(S.x, S.y, S.alto);
	const alza = f >= pregunta;
	return (
		<>
			<EscAudiencia />
			<Actor x={S.x} y={S.y} alto={S.alto}>
				<Muneco ropa={SENADOR} pose={alza ? {...manosEn([150, 300], [250, 300]), mi: 'agarra', md: 'agarra'} : manosFrente([150, 560], [250, 560])} ojos="normal" cejas="neutral" boca="seria" hablando={f >= pregunta && f < responde} />
			</Actor>
			{alza && <Prismaticos x={ox} y={oy + S.alto * 0.12} tam={S.alto * 0.26} rot={-4} />}
			<Actor x={800} y={1560} alto={1040} voltear>
				<Muneco ropa={VIGIA_CIVIL} pose={manosFrente([150, 560], [250, 560])} ojos={f >= responde ? 'entrecerrados' : 'normal'} cejas={f >= responde ? 'preocupado' : 'neutral'} boca="seria" hablando={f >= responde} />
			</Actor>
			<MesaAudiencia y={1300} />
			{/* lo que habría pasado: el barco esquiva el iceberg */}
			{esquiva > 0 && (
				<div style={{position: 'absolute', left: 540, top: 210, width: 470, height: 300, transform: `scale(${esquiva})`, transformOrigin: '60% 100%'}}>
					<div style={{position: 'absolute', inset: 0, borderRadius: '50%', background: '#0a1326', border: `9px solid ${TINTA}`, overflow: 'hidden'}}>
						<svg width={470} height={300} viewBox="0 0 520 400" preserveAspectRatio="none">
							<path d="M 60 300 Q 250 300 330 220 Q 400 150 470 150" stroke="#7dffb8" strokeWidth={8} strokeDasharray="20 14" fill="none" />
							<path d="M 470 150 l -24 -8 l 6 22 z" fill="#7dffb8" />
						</svg>
						<Iceberg x={300} y={240} ancho={100} noche silueta={1} />
						<Titanic x={120} y={240} ancho={170} luces={1} noche humo={false} />
					</div>
					{[0, 1].map((i) => (
						<div key={i} style={{position: 'absolute', left: 300 + i * 40, top: 300 + i * 34, width: 40 - i * 14, height: 40 - i * 14, borderRadius: '50%', background: '#0a1326', border: `7px solid ${TINTA}`}} />
					))}
				</div>
			)}
		</>
	);
};

const T8: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const pregunta = antes(ini(10));
	const responde = antes(ini(11));
	return (
		<Toma
			escena={<Audiencia pregunta={pregunta} responde={responde} esquiva={tramo(f, pal(11, 'esquivarlo'), pal(11, 'esquivarlo') + 10)} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			camFn={(ff) => (ff < responde ? golpeCam(ff, pregunta, {s: 1.0, x: 0, y: 0}, centrarV(330, 900, 1.25, 760)) : golpeCam(ff, responde, centrarV(330, 900, 1.25, 760), centrarV(760, 900, 1.15, 820)))}
		/>
	);
};

/* ---------------- 9 · en el puente sí tenían prismáticos ---------------- */

const T9: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const O = {x: 540, y: 1700, alto: 1150};
	const {ox, oy} = ojosDe(O.x, O.y, O.alto);
	const si = antes(pal(12, 'sí'));
	return (
		<Toma escena={<EscPuente><EscNocheMar horizonte={1000} /></EscPuente>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}}>
			<Actor x={O.x} y={O.y} alto={O.alto}>
				<Muneco ropa={OFICIAL} pose={{...manosEn([140, 250], [260, 250]), mi: 'agarra', md: 'agarra'}} ojos="normal" cejas="neutral" boca="seria" />
			</Actor>
			<Prismaticos x={ox} y={oy + O.alto * 0.02} tam={O.alto * 0.27} />
			{f >= si && (
				<div style={{position: 'absolute', left: 640, top: 960, padding: '10px 26px', background: '#1f9d48', border: `8px solid ${TINTA}`, borderRadius: 14, fontFamily: CONDENSADA, fontSize: 70, color: '#fff', transform: `scale(${pop(f, si, 8)}) rotate(-6deg)`}}>✓ SÍ</div>
			)}
		</Toma>
	);
};

/** lo que se ve por los prismáticos: nada */
const T10: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscNocheMar horizonte={1000} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.25]}}>
		<svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
			<defs>
				<mask id="binoculo">
					<rect width={1080} height={1920} fill="#fff" />
					<circle cx={380} cy={900} r={330} fill="#000" />
					<circle cx={700} cy={900} r={330} fill="#000" />
				</mask>
			</defs>
			<rect width={1080} height={1920} fill="#000" mask="url(#binoculo)" />
			<line x1={540} y1={860} x2={540} y2={940} stroke="#8fb4d8" strokeWidth={3} opacity={0.5} />
			<line x1={500} y1={900} x2={580} y2={900} stroke="#8fb4d8" strokeWidth={3} opacity={0.5} />
		</svg>
		<div style={{position: 'absolute', left: 0, right: 0, top: 620, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 200, color: 'rgba(255,255,255,0.85)'}}>?</div>
	</Toma>
);

/* ---------------- 10 · sin luna, mar espejo, sin espuma ---------------- */

const T11: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sin = tramo(f, d + 4, d + 18);
	return (
		<Toma escena={<EscNocheMar horizonte={1500} luna={1 - sin} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.0]}}>
			{/* el hueco de la luna: un contorno punteado tachado */}
			<svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity: sin}}>
				<circle cx={795} cy={355} r={95} fill="none" stroke="#c8d8ff" strokeWidth={7} strokeDasharray="22 16" />
				<line x1={700} y1={450} x2={890} y2={260} stroke="#c8202a" strokeWidth={14} strokeLinecap="round" />
			</svg>
		</Toma>
	);
};

/** mar en calma total: el barco y las estrellas se reflejan como en un espejo */
const T12: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const barco = <Titanic x={500 + (f - d) * 0.4} y={760} ancho={760} luces={1} noche humo={false} />;
	return (
		<Toma escena={<EscNocheMar horizonte={760} espejo={1} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [0, -30]}}>
			{barco}
			<div style={{position: 'absolute', inset: 0, transform: 'scaleY(-1)', transformOrigin: '50% 768px', opacity: 0.4, filter: 'blur(1.5px)'}}>{barco}</div>
		</Toma>
	);
};

const Mitad: React.FC<{y: number; alto: number; espuma: number; etiqueta: string; color: string}> = ({y, alto, espuma, etiqueta, color}) => (
	<div style={{position: 'absolute', left: 0, top: y, width: 1080, height: alto, overflow: 'hidden', borderBottom: `8px solid ${TINTA}`}}>
		<div style={{position: 'absolute', left: 0, top: -560, width: 1080, height: 1920}}>
			<EscNocheMar horizonte={1000} espejo={espuma ? 0 : 1} />
			<Iceberg x={540} y={1000} ancho={420} noche espuma={espuma} />
		</div>
		<div style={{position: 'absolute', left: 40, top: 40, padding: '8px 22px', background: color, border: `7px solid ${TINTA}`, borderRadius: 12, fontFamily: CONDENSADA, fontSize: 56, color: '#fff'}}>{etiqueta}</div>
	</div>
);

const T13: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const u = tramo(f, d, d + 10);
	return (
		<Toma escena={<div style={{position: 'absolute', inset: 0, background: '#000'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.03]}}>
			<div style={{position: 'absolute', inset: 0, opacity: u}}>
				<Mitad y={0} alto={1060} espuma={1} etiqueta="NOCHE NORMAL" color="#3a6ab0" />
			</div>
			<Mitad y={1250} alto={670} espuma={0} etiqueta="ESA NOCHE" color="#c8202a" />
		</Toma>
	);
};

/* ---------------- 11 · seis avisos de hielo ---------------- */

const T14: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const a = antes(pal(18, 'seis'));
	const b = fin(18) - 4;
	const tiempos = [d + 6, ...Array.from({length: 5}, (_, i) => Math.round(a + ((b - a) * i) / 4))];
	const POS: [number, number, number][] = [[540, 160, -3], [420, 330, 5], [660, 470, -6], [430, 640, 4], [650, 800, -4], [540, 1290, 3]];
	return (
		<Toma escena={<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 40%, #4a3a2e, #1a120c)'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04]}} golpes={tiempos.slice(1).map((t) => [t, 0.025] as [number, number])}>
			{tiempos.map((t, i) => {
				if (f < t) return null;
				const p = Math.min(1, (f - t) / 5);
				return (
					<div key={i} style={{position: 'absolute', inset: 0, opacity: p, transform: `scale(${1 + 0.25 * (1 - p)})`, transformOrigin: `${POS[i][0]}px ${POS[i][1] + 150}px`}}>
						<Telegrama x={POS[i][0]} y={POS[i][1]} ancho={620} n={i + 1} rot={POS[i][2]} />
					</div>
				);
			})}
		</Toma>
	);
};

/* ---------------- 12 · ¿y frenaron? no ---------------- */

const T15: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const no = antes(ini(20));
	return (
		<Toma escena={<EscPuente><EscNocheMar horizonte={1000} /></EscPuente>} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(ff) => golpeCam(ff, no, {s: 1.0, x: 0, y: 0}, centrarV(540, 620, 1.2, 620))}>
			<Nudos x={540} y={620} tam={620} nudos={22 + Math.sin(f / 3) * 0.25} />
			{f >= no && <Sello x={540} y={1440} texto="SIN FRENAR" desde={no} color="#c8202a" tam={100} rot={-8} solido />}
		</Toma>
	);
};

/* ---------------- 13 · la carta ---------------- */

const T16: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<Escritorio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [0, 30]}}>
			<Actor x={540} y={1560} alto={1000}>
				<Muneco ropa={BLAIR} pose={{...brazo(1, alcanzar(1, 300, 600)), md: 'agarra', ...manosEn([150, 600]), mi: 'abierta', cabeza: 10}} ojos="entrecerrados" cejas="preocupado" boca="seria" />
			</Actor>
			<div style={{position: 'absolute', left: -40, right: -40, top: 1180, bottom: -40, background: 'linear-gradient(180deg, #5a3a22, #2e1a0e)', borderTop: `12px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: 360, top: 1200, width: 380, height: 90, background: '#fbf6e8', border: `6px solid ${TINTA}`, transform: 'perspective(600px) rotateX(50deg)'}} />
			<div style={{position: 'absolute', left: 700, top: 1080 + Math.sin(f * 0.9) * 6, width: 14, height: 170, background: '#f4f0e6', border: `5px solid ${TINTA}`, borderRadius: '50% 50% 3px 3px', transform: 'rotate(20deg)'}} />
		</Toma>
	);
};

const T17: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<Escritorio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}}>
			<Carta x={540} y={240} ancho={900} escribe={tramo(f, antes(pal(22, 'qué')), fin(22), (u) => u)} rot={-2} />
		</Toma>
	);
};

/* ---------------- 14 · esa pena le salvó la vida ---------------- */

const T18: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Escritorio />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}}>
		<Actor x={540} y={1950} alto={1200}>
			<Muneco ropa={BLAIR} pose={{...manosEn([120, 330], [280, 330]), mi: 'agarra', md: 'agarra'}} ojos="normal" cejas="preocupado" boca="seria" />
		</Actor>
		<Periodico x={540} y={190} ancho={760} titular="SE HUNDE EL TITANIC" fecha="16 DE ABRIL DE 1912" nombre="THE DAILY NEWS" rot={-3} />
	</Toma>
);

/* ---------------- 15 · el único que tenía la llave… ---------------- */

const T19: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<div style={{position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 40%, #2a2a36 0%, #050508 60%)'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08]}}>
			<Llave x={540} y={700} tam={720} rot={-10 + (f - d) * 0.15} brillo={0.6 + 0.4 * Math.sin(f / 10)} />
		</Toma>
	);
};

/** el barco se va y él se queda en el muelle */
const T20: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const va = tramo(f, d, h + 10, (u) => u);
	return (
		<Toma escena={<EscMuelle />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.2, 1.0]}}>
			<Titanic x={interpolate(va, [0, 1], [760, 900])} y={1330} ancho={interpolate(va, [0, 1], [900, 620])} />
			<Actor x={300} y={1760} alto={1000}>
				<Muneco ropa={BLAIR} pose={{...brazo(1, alcanzar(1, 340, 380)), md: 'abierta', ...manosEn([150, 560]), mi: 'relajada'}} ojos="normal" cejas="preocupado" boca="seria" />
			</Actor>
			<Llave x={420} y={1180} tam={150} rot={-20} brillo={0.7} etiqueta={false} />
		</Toma>
	);
};

/* ---------------- 16 · veredicto ---------------- */

const T21: React.FC<P> = ({d, h, e, s}) => <Toma escena={<Gancho d={d} brillo={1} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.0]}} encima={<Sello x={540} y={1460} texto="MEDIO MITO" desde={SELLO} color="#e07a1a" tam={130} rot={-10} solido />} />;

/** el sello cae con la palabra «mito» y queda en el último segundo */
const SELLO = antes(pal(26, 'mito'));
export const FIN_VIDEO = Math.max(fin(26) + 18, SELLO + 33);

const PLANOS: Plano[] = [
	{n: 'gancho', d: 0, e: 'corte', C: T0},
	{n: 'bolsillo', d: ini(1), e: 'zoom', C: T1},
	{n: 'muelle', d: ini(2), e: 'latigoDer', C: T2},
	{n: 'prisa', d: ini(3), e: 'latigoIzq', C: T3},
	{n: 'armario', d: antes(pal(4, 'llave')), e: 'zoom', C: T4},
	{n: 'vigias', d: ini(5), e: 'latigoArriba', C: T5},
	{n: 'bitacora', d: ini(6), e: 'zoom', C: T6},
	{n: 'iceberg', d: antes(pal(6, 'vigía')), e: 'latigoDer', C: T6b},
	{n: 'segundos', d: ini(7), e: 'latigoIzq', C: T7},
	{n: 'audiencia', d: ini(9), e: 'latigoDer', C: T8},
	{n: 'puente', d: ini(12), e: 'latigoIzq', C: T9},
	{n: 'prismaticos', d: ini(13), e: 'zoom', C: T10},
	{n: 'luna', d: ini(14), e: 'latigoArriba', C: T11},
	{n: 'espejo', d: ini(15), e: 'zoom', C: T12},
	{n: 'espuma', d: ini(16), e: 'latigoDer', C: T13},
	{n: 'avisos', d: ini(17), e: 'latigoIzq', C: T14},
	{n: 'nudos', d: ini(19), e: 'zoom', C: T15},
	{n: 'escribe', d: ini(21), e: 'latigoDer', C: T16},
	{n: 'carta', d: antes(ini(22)), e: 'zoom', C: T17},
	{n: 'salvo', d: ini(23), e: 'latigoIzq', C: T18},
	{n: 'llave', d: ini(24), e: 'fundido', C: T19},
	{n: 'se-va', d: antes(ini(25)), e: 'zoom', C: T20},
	{n: 'veredicto', d: ini(26), e: 'latigoDer', C: T21},
];

const WHOOSH: [string, number, number][] = PLANOS.filter((p) => p.e && p.e.startsWith('latigo')).map((p) => ['whoosh', p.d - 5, 0.35]);

export const SONIDOS: [string, number, number][] = [
	...WHOOSH,
	['ola', 0, 0.35],
	['tintineo', antes(pal(0, 'salvar')), 0.5],
	['objeto', pal(1, 'bolsillo') + 2, 0.6],
	['bocina', ini(2) + 6, 0.45],
	['sello', antes(pal(2, 'tierra')), 0.8],
	['pasos', ini(3), 0.5],
	['ding', antes(pal(4, 'llave')) + 2, 0.6],
	['cadena', antes(pal(4, 'prismáticos')), 0.5],
	['viento', ini(5), 0.45],
	['campana', antes(pal(6, 'iceberg')), 0.75],
	['dundun', antes(pal(8, '37')), 0.7],
	['mazo', ini(9) - 2, 0.6],
	['murmullo', ini(9), 0.25],
	['clic', antes(pal(12, 'sí')), 0.6],
	['viento', ini(14), 0.4],
	['ola', ini(15), 0.25],
	['morse', ini(17), 0.45],
	['sello', antes(pal(18, 'seis')), 0.6],
	['sello', antes(ini(20)), 0.9],
	['garabato', antes(pal(22, 'qué')), 0.5],
	['hoja', ini(23), 0.6],
	['tintineo', ini(24) + 4, 0.45],
	['bocina', antes(ini(25)) + 8, 0.35],
	['sello', SELLO, 1.0],
];

export const Historia: React.FC = () => <Montaje planos={PLANOS} fin={FIN_VIDEO} />;
