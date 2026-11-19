import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Actor, Muneco, animarPose, manosEn, manosFrente} from '../componentes/Muneco';
import {Lapiz} from '../componentes/Objetos';
import {Toma} from '../componentes/Toma';
import {Brillos} from '../componentes/Utileria';
import {FUNDADOR, HITLER_1919, HITLER_ESPIA, SENOR_1, SENOR_3} from '../componentes/Vestuario';
import {Cara} from '../componentes/Recurrentes';
import {ConoLuz, EscCerveceria, EscLiso, EscMesaArriba, EscOficinaBerlin, Humo, Jarra, Pizarra} from '../escenarios/Epoca';
import {CONDENSADA, SERIF} from '../fuentes';
import {P, Plano, TINTA, antes, centrar, clamp, fin, golpeCam, ini, mezclaCam, pal, tramo} from './base';
import {CuadroEspia, Silla, brazo} from './compartidas';
import {Barba, Carnet, PancartaMano, CartelAlquila, GloboNumero, LibretaPlan, MarcoVacio, PARROQUIANOS, PlatoVacio, RelojBolsillo, RelojPared, Sudor, Vapor, enActor} from './utileria_c12';

/* CAPÍTULO 1 · EL ESPÍA (frases 16–38). Paleta: sepia y ámbar de cervecería, con humo. Hitler siempre desde arriba. */

/** mesa vista de frente con mantel que tapa las piernas (y = tablero) */
export const MesaFrente: React.FC<{x: number; y: number; ancho: number; color?: string; mantel?: string}> = ({x, y, ancho, color = '#7a5230', mantel}) => (
	<>
		<div style={{position: 'absolute', left: x - ancho / 2, top: y - 24, width: ancho, height: 40, background: color, border: `8px solid ${TINTA}`, borderRadius: 8, zIndex: 0}} />
		<div style={{position: 'absolute', left: x - ancho / 2 + 16, top: y + 16, width: ancho - 32, height: 1100 - y, background: mantel ?? 'linear-gradient(180deg, #5a3a1e, #3a2412)', border: `8px solid ${TINTA}`, borderTop: 'none'}} />
	</>
);

/* ---------- el rótulo: la pizarra del menú, y Hitler solo frente a un plato vacío ---------- */

const C1Pizarra: React.FC<P> = ({d, h, e, s}) => {
	const baja = pal(16, 'Hitler');
	return (
		<Toma
			escena={<EscCerveceria tono="sepia" vacia humo={0.18} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			angulo={-7}
			focoEntrada={[960, 330]}
			camFn={(f) => mezclaCam(centrar(960, 250, 1.5), centrar(960, 640, 1.22), tramo(f, baja - 4, baja + 22))}
		>
			<Pizarra x={960} y={70} ancho={640} titulo="Plato del día" lineas={['MÚNICH · 1919']} />
			<Actor x={960} y={1040} alto={640}>
				<Muneco ropa={HITLER_1919} pose={{...manosFrente([150, 600], [250, 600]), mi: 'relajada', md: 'relajada', cabeza: -6, agacha: 0.3}} ojos="entrecerrados" cejas="preocupado" boca="mueca" />
			</Actor>
			<MesaFrente x={960} y={880} ancho={620} />
			<PlatoVacio x={960} y={862} ancho={300} />
		</Toma>
	);
};

const C1Alquila: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#1e2632" luz="200,220,255" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.15], r: [-1, 1]}}>
		<CartelAlquila x={960} y={180} ancho={720} />
	</Toma>
);

const C1Marco: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscLiso color="#2a1e1a" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.18], r: [1, -1]}}>
		<div style={{position: 'absolute', left: 560, right: 560, top: 860, height: 40, background: '#6a4a2a', border: `8px solid ${TINTA}`}} />
		<MarcoVacio x={960} y={260} ancho={480} />
	</Toma>
);

const C1Plan: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscMesaArriba tono="madera" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.2], r: [-2, 0]}}>
		<LibretaPlan x={960} y={170} ancho={560} />
	</Toma>
);

/* ---------- el espía (la misma imagen del adelanto) ---------- */

const C1Espia: React.FC<P> = ({d, h, e, s}) => <Toma escena={<CuadroEspia />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.18], x: [40, -30], y: [20, 60]}} angulo={-6} />;

/* ---------- la puerta del cuarto del fondo: un partido chiquitito ---------- */

const C1Puerta: React.FC<P> = ({d, h, e, s}) => {
	const g = antes(pal(19, 'chiquitito'));
	return (
		<Toma
			escena={<EscCerveceria tono="sepia" vacia humo={0.12} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			angulo={-4}
			camFn={(f) => golpeCam(f, g, centrar(960, 560, 1.05 + 0.05 * tramo(f, d, g)), centrar(1180, 470, 3.2))}
		>
			{/* puerta del cuarto del fondo */}
			<div style={{position: 'absolute', left: 1020, top: 250, width: 330, height: 640, background: '#5a3a1e', border: `10px solid ${TINTA}`, borderRadius: '12px 12px 0 0'}}>
				<div style={{position: 'absolute', left: 40, right: 40, top: 40, height: 200, background: 'rgba(255,214,140,0.75)', border: `8px solid ${TINTA}`, boxShadow: '0 0 60px rgba(255,200,120,0.6)'}} />
				<div style={{position: 'absolute', right: 30, top: 330, width: 34, height: 34, borderRadius: '50%', background: '#c9a43a', border: `6px solid ${TINTA}`}} />
			</div>
			<div style={{position: 'absolute', left: 1020, top: 880, width: 330, height: 14, background: 'rgba(255,214,140,0.7)', filter: 'blur(4px)'}} />
			{/* el papelito clavado: el partido */}
			<div style={{position: 'absolute', left: 1120, top: 440, width: 130, height: 70, background: '#f6efdc', border: `4px solid ${TINTA}`, transform: 'rotate(-6deg)', fontFamily: "'Comic Sans MS', cursive", fontSize: 15, fontWeight: 700, lineHeight: 1.05, textAlign: 'center', padding: '6px 4px', boxSizing: 'border-box', color: '#2a2218'}}>
				Partido Obrero Alemán
				<div style={{position: 'absolute', left: 58, top: -8, width: 10, height: 10, borderRadius: '50%', background: '#a8262e', border: `2px solid ${TINTA}`}} />
			</div>
			<Actor x={640} y={1060} alto={760}>
				<Muneco ropa={HITLER_ESPIA} pose={{...manosFrente([150, 520], [300, 470]), mi: 'agarra', md: 'agarra', cuerpo: 6, cabeza: 8}} ojos="mirandoLado" cejas="arrogante" boca="seria" />
			</Actor>
			<Humo densidad={0.12} />
		</Toma>
	);
};

/* ---------- el cuarto del fondo: unos cuarenta tipos, una pancarta torcida y Hitler aburrido ---------- */

const Parroquianos: React.FC<{barbas?: number; habla?: number}> = ({barbas = 0, habla = -1}) => {
	const xs = [250, 520, 790, 1060];
	return (
		<>
			{xs.map((x, i) => {
				const ropa = PARROQUIANOS[i % PARROQUIANOS.length];
				const [bx, by] = enActor(x, 1010, 560, 200, 262, i % 2 === 1);
				return (
					<React.Fragment key={i}>
						<Actor x={x} y={1010} alto={560} voltear={i % 2 === 1}>
							<Muneco ropa={ropa} semilla={i} pose={habla === i ? {...brazo(1, {a: 120, c: 30}), md: 'abierta', agacha: 0.3} : {...manosFrente([170, 600], [230, 600]), mi: 'agarra', md: 'agarra', agacha: 0.3}} ojos={barbas > 0.3 ? 'cerrados' : 'normal'} cejas="neutral" boca={habla === i ? 'abierta' : 'seria'} hablando={habla === i} />
						</Actor>
						<Barba x={bx} y={by + 40} ancho={110} largo={barbas} />
					</React.Fragment>
				);
			})}
		</>
	);
};

const C1Cuarto: React.FC<P> = ({d, h, e, s}) => {
	const pan = ini(22);
	return (
		<Toma
			escena={<EscCerveceria tono="sepia" vacia humo={0.22} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1, 1]}}
			angulo={-6}
			camFn={(f) => mezclaCam(centrar(760, 560, 1.12), centrar(1380, 640, 1.3), tramo(f, pan - 6, pan + 24))}
		>
			<PancartaMano x={760} y={230} ancho={860} />
			<Parroquianos />
			<MesaFrente x={660} y={860} ancho={1100} />
			<Jarra x={420} y={850} alto={100} />
			<Jarra x={720} y={850} alto={100} />
			<Jarra x={960} y={850} alto={100} />
			{/* Hitler, aparte, aburrido (mano en la barbilla) */}
			<Actor x={1560} y={1010} alto={560}>
				<Muneco ropa={HITLER_1919} pose={{...manosEn(undefined, [222, 282]), md: 'puno', frenteD: 1, ...manosFrente([160, 600]), agacha: 0.3, cabeza: 8}} ojos="entrecerrados" cejas="neutral" boca="mueca" />
			</Actor>
			<MesaFrente x={1560} y={860} ancho={360} />
			<Jarra x={1640} y={850} alto={100} />
		</Toma>
	);
};

/* ---------- alguien dice algo que no le gusta ---------- */

const C1Alguien: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const molesto = f >= antes(pal(23, 'gusta'));
	return (
		<Toma escena={<EscCerveceria tono="sepia" vacia humo={0.2} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.3, 1.45], x: [-260, -330], y: [-90, -120]}} angulo={-6}>
			<PancartaMano x={1000} y={230} ancho={760} />
			<Actor x={760} y={1010} alto={560}>
				<Muneco ropa={PARROQUIANOS[1]} pose={{...brazo(1, {a: 120, c: 30}), md: 'abierta', agacha: 0.3}} ojos="normal" cejas="arrogante" boca="abierta" hablando={f < fin(23)} />
			</Actor>
			<MesaFrente x={760} y={860} ancho={520} />
			<Actor x={1300} y={1010} alto={560}>
				<Muneco ropa={HITLER_1919} pose={molesto ? {...manosFrente([150, 600], [250, 600]), mi: 'puno', md: 'puno', agacha: 0.3, cabeza: -4} : {...manosEn(undefined, [222, 282]), md: 'puno', frenteD: 1, agacha: 0.3, cabeza: 8}} ojos={molesto ? 'grandes' : 'entrecerrados'} cejas={molesto ? 'enojado' : 'neutral'} boca={molesto ? 'mueca' : 'seria'} />
			</Actor>
			<MesaFrente x={1300} y={860} ancho={360} />
		</Toma>
	);
};

/* ---------- y se para, y empieza a gritar, y no para ---------- */

const C1Grita: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const para = antes(pal(24, 'para', 1));
	const grita = antes(pal(24, 'gritar'));
	const noPara = antes(pal(24, 'no'));
	const pose = animarPose(f, [
		[d, {...manosFrente([150, 600], [250, 600]), mi: 'puno', md: 'puno', agacha: 0.3}],
		[para + 2, {...manosFrente([150, 560], [250, 560]), agacha: 0, cabeza: 0}],
		[grita + 2, {...manosEn([40, 250], [360, 250]), mi: 'puno', md: 'puno', cabeza: -4}],
		[grita + 8, {...manosEn([30, 300], [370, 300]), cabeza: 4}],
		[noPara, {...manosEn([30, 230], [370, 300]), cabeza: -4}],
		[noPara + 8, {...manosEn([40, 300], [360, 230]), cabeza: 4}],
		[noPara + 16, {...manosEn([30, 230], [370, 300]), cabeza: -4}],
		[noPara + 24, {...manosEn([40, 300], [360, 230]), cabeza: 4}],
	]);
	const [ox, oy] = enActor(960, 1010, 640, 200, 150);
	const barbas = tramo(f, noPara, noPara + 60);
	return (
		<Toma
			escena={<EscCerveceria tono="sepia" vacia humo={0.2} />}
			desde={d}
			hasta={h}
			entrada={e}
			salida={s}
			cam={{s: [1.04, 1.12], y: [30, 50]}}
			angulo={-7}
			golpes={[
				[para, 0.06],
				[grita, 0.07],
				[noPara, 0.07],
			]}
		>
			<PancartaMano x={960} y={130} ancho={820} />
			<RelojPared x={1640} y={330} tam={220} vel={f >= noPara ? 40 : 1} desde={noPara} />
			<Actor x={960} y={1010} alto={640}>
				<Muneco ropa={HITLER_1919} pose={pose} ojos="grandes" cejas="enojado" boca={f >= grita ? 'grito' : 'mueca'} hablando={false} />
			</Actor>
			<Vapor x={ox} y={oy} separacion={240} desde={grita} tam={0.8} />
			{[260, 1660].map((x, i) => {
				const [bx, by] = enActor(x, 1010, 520, 200, 262, i === 1);
				return (
					<React.Fragment key={i}>
						<Actor x={x} y={1010} alto={520} voltear={i === 1}>
							<Muneco ropa={PARROQUIANOS[i * 2]} semilla={i} pose={{...manosFrente([170, 600], [230, 600]), mi: 'agarra', md: 'agarra', agacha: 0.3}} ojos={barbas > 0.4 ? 'cerrados' : 'grandes'} cejas="sorprendido" boca="o" />
						</Actor>
						<Barba x={bx} y={by + 36} ancho={100} largo={barbas} color="#b8b0a2" />
					</React.Fragment>
				);
			})}
			<div style={{position: 'absolute', left: -40, right: -40, top: 860, height: 40, background: '#7a5230', border: `8px solid ${TINTA}`}} />
			<div style={{position: 'absolute', left: -40, right: -40, top: 900, bottom: -40, background: 'linear-gradient(180deg, #5a3a1e, #3a2412)'}} />
			{[360, 620, 1300, 1560].map((x, i) => (
				<Jarra key={i} x={x} y={870} alto={110} tiembla={f >= grita ? 7 : 0} />
			))}
		</Toma>
	);
};

/* ---------- el fundador, fascinado (desde abajo) ---------- */

const C1Fundador: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const [ox, oy] = enActor(720, 1120, 1000, 200, 142);
	return (
		<Toma escena={<EscCerveceria tono="sepia" vacia humo={0.18} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.1], x: [30, -20], y: [-20, 10]}} angulo={7}>
			{/* Hitler gritando al fondo */}
			<Actor x={1460} y={880} alto={430}>
				<Muneco ropa={HITLER_1919} pose={{...manosEn([40, 250 + Math.sin(f / 4) * 30], [360, 250 - Math.sin(f / 4) * 30]), mi: 'puno', md: 'puno'}} ojos="grandes" cejas="enojado" boca="grito" />
			</Actor>
			<Actor x={720} y={1120} alto={1000}>
				<Muneco ropa={FUNDADOR} pose={{...manosFrente([180, 500], [220, 500]), mi: 'agarra', md: 'agarra', cuerpo: 4, cabeza: 6}} ojos="grandes" cejas="sorprendido" boca="sonrisa" />
			</Actor>
			<Brillos x={ox} y={oy} desde={d + 8} radio={160} n={8} />
		</Toma>
	);
};

const C1Dicen: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const habla = f >= ini(27) && f < fin(27);
	return (
		<Toma escena={<EscCerveceria tono="sepia" vacia humo={0.16} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.12, 1.22], x: [0, -40], y: [0, 20]}} angulo={6}>
			<Actor x={1180} y={1060} alto={780} voltear>
				<Muneco ropa={SENOR_3} pose={{...manosFrente([180, 600], [220, 600]), mi: 'agarra', md: 'agarra', cabeza: -6}} ojos="mirandoLado" cejas="sorprendido" boca="o" />
			</Actor>
			<Actor x={820} y={1080} alto={820}>
				<Muneco ropa={FUNDADOR} pose={{...manosEn(undefined, [300, 214]), md: 'abierta', wd: -30, frenteD: 1, ...manosFrente([170, 520]), cabeza: 10, cuerpo: 6}} ojos="feliz" cejas="arrogante" boca="picara" hablando={habla} />
			</Actor>
		</Toma>
	);
};

/** la boca de Hitler, enorme por un instante */
const C1Boca: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const T = 820;
	const u = T / 380;
	const left = 960 - T / 2;
	const top = 170;
	const mx = left + T * 0.0263 + (200 - 20) * u;
	const my = top + 272 * u;
	const abre = 0.75 + 0.25 * Math.abs(Math.sin(f / 3));
	return (
		<Toma escena={<EscLiso color="#4a2a14" luz="255,200,120" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08]}} angulo={-4}>
			{/* rayos de cómic */}
			<div style={{position: 'absolute', inset: 0, background: 'repeating-conic-gradient(from 0deg at 50% 60%, rgba(255,214,120,0.18) 0deg 8deg, rgba(0,0,0,0) 8deg 18deg)'}} />
			<Cara d={HITLER_1919.cabeza} tam={T} ojos="grandes" cejas="enojado" boca="seria" style={{position: 'absolute', left, top}} />
			<div style={{position: 'absolute', left: mx - 330, top: my, width: 660, height: 380 * abre, background: '#5a1416', border: `16px solid ${TINTA}`, borderRadius: '45% 45% 50% 50%', overflow: 'hidden'}}>
				<div style={{position: 'absolute', left: 60, right: 60, top: 0, height: 60, background: '#ffffff', borderBottom: `8px solid ${TINTA}`}} />
				<div style={{position: 'absolute', left: 180, right: 180, bottom: -40, height: 160, borderRadius: '50%', background: '#e2626a'}} />
			</div>
			<Vapor x={960} y={top + 180 * u} separacion={T * 0.9} desde={d} tam={1.2} />
		</Toma>
	);
};

/* ---------- lo mandan a espiar… y termina afiliándose ---------- */

const C1Afilia: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const suelta = antes(pal(28, 'partido'));
	const firma = antes(ini(29));
	const caida = tramo(f, suelta, suelta + 12, (t) => t * t);
	const [lx, ly] = enActor(900, 1040, 760, 330, 470);
	const pose = animarPose(f, [
		[d, {...manosFrente([170, 560], [330, 470]), mi: 'agarra', md: 'agarra'}],
		[suelta, {...manosFrente([170, 560], [330, 470]), md: 'abierta'}],
		[firma, {...manosFrente([150, 640], [262, 650]), mi: 'abierta', md: 'agarra'}],
	]);
	return (
		<Toma escena={<EscCerveceria tono="sepia" vacia humo={0.16} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.2], x: [0, -40], y: [-40, -80]}} angulo={-6}>
			<PancartaMano x={960} y={110} ancho={820} />
			<Actor x={900} y={1040} alto={760}>
				<Muneco ropa={HITLER_ESPIA} pose={{...pose, cabeza: f >= firma ? 10 : -4}} objDer={f >= firma ? <Lapiz rot={150 + Math.sin(f) * 8} /> : undefined} ojos={f >= firma ? 'entrecerrados' : 'mirandoLado'} cejas="arrogante" boca={f >= firma ? 'picara' : 'seria'} />
			</Actor>
			<MesaFrente x={960} y={870} ancho={760} />
			{/* la hoja de afiliación sobre la mesa */}
			<div style={{position: 'absolute', left: 900, top: 836, width: 200, height: 46, background: '#f6efdc', border: `5px solid ${TINTA}`, transform: 'perspective(400px) rotateX(55deg)'}} />
			{/* la libreta del espía, que cae */}
			{f < suelta + 40 && (
				<div style={{position: 'absolute', left: lx - 40 + caida * 120, top: ly + caida * (1060 - ly) - 50, width: 80, height: 110, background: '#f4ecd6', border: `6px solid ${TINTA}`, borderRadius: 6, transform: `rotate(${caida * 300}deg)`, opacity: f > suelta + 30 ? 0 : 1}} />
			)}
		</Toma>
	);
};

/* ---------- el carnet Nº 555 ---------- */

const C1Carnet: React.FC<P> = ({d, h, e, s}) => {
	const g = antes(pal(30, '555'));
	return (
		<Toma escena={<EscMesaArriba tono="madera" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} camFn={(f) => golpeCam(f, g, centrar(960, 540, 1.02 + 0.04 * tramo(f, d, g)), centrar(1080, 690, 2.1))}>
			<Carnet x={960} y={560} ancho={1000} />
		</Toma>
	);
};

/* ---------- empezaron desde el 501: el globo se desinfla ---------- */

const C1Globo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const pues = antes(pal(32, 'Pues'));
	const n501 = antes(pal(32, '501'));
	const infla = 1 - tramo(f, pues + 2, pues + 22, (t) => t * t);
	const salto = f >= n501 ? Math.max(0, 1 - (f - n501) / 8) : 1;
	return (
		<Toma escena={<EscCerveceria tono="sepia" vacia humo={0.1} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.15], y: [0, 30]}} angulo={-3}>
			<ConoLuz x={960} y={0} ancho={1300} alto={1000} fuerza={0.3} />
			<GloboNumero x={960 + (1 - infla) * Math.sin(f) * 40} y={880} tam={420} texto="555" infla={infla} />
			{f >= n501 && (
				<div style={{position: 'absolute', left: 1240, top: 380, padding: '20px 30px', background: '#26302a', border: `14px solid #6a4a2a`, outline: `5px solid ${TINTA}`, color: '#f2f0e6', fontFamily: CONDENSADA, fontSize: 64, lineHeight: 1.1, textAlign: 'center', transform: `rotate(4deg) scale(${1 - 0.4 * salto})`}}>
					MIEMBRO Nº 1
					<div style={{fontSize: 110}}>= 501</div>
				</div>
			)}
		</Toma>
	);
};

const C1Pancarta: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const resp = 0.7 + 0.3 * (0.5 + 0.5 * Math.sin((f - d) / 5));
	return (
		<Toma escena={<EscCerveceria tono="sepia" vacia humo={0.14} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], x: [30, -30]}} angulo={-3}>
			<div style={{position: 'absolute', left: 260, right: 260, top: 300, height: 260, background: '#efe6cf', border: `9px solid ${TINTA}`, borderRadius: 30, transform: `rotate(-3deg) scale(${0.9 + 0.12 * resp}, ${0.7 + 0.35 * resp})`, boxShadow: '12px 14px 0 rgba(0,0,0,0.3)'}} />
			<GloboNumero x={960} y={530} tam={84} texto="PARTIDO OBRERO ALEMÁN" infla={resp} color="#c8402a" />
		</Toma>
	);
};

/* ---------- el espía resulta ser un show ---------- */

const C1Show: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const grita = antes(pal(34, 'grita'));
	const suda = antes(pal(34, 'suda'));
	const golpea = antes(pal(34, 'golpea'));
	const pose = animarPose(f, [
		[d, {...manosEn([40, 300], [360, 300]), mi: 'puno', md: 'puno'}],
		[grita, {...manosEn([40, 220], [360, 300])}],
		[suda, {...manosEn([60, 320], [340, 230])}],
		[golpea - 4, {...manosEn([60, 320], [330, 180]), md: 'puno'}],
		[golpea + 1, {...manosEn([60, 320], [300, 600]), md: 'puno', cuerpo: 6}],
		[golpea + 12, {...manosEn([40, 240], [360, 300]), cuerpo: 0}],
	]);
	const golpe = f >= golpea + 1 && f < golpea + 6;
	const [cx, cy] = enActor(960, 1000, 700, 200, 120);
	return (
		<Toma escena={<EscCerveceria tono="ambar" vacia humo={0.25} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.04, 1.14], y: [20, 40]}} angulo={-5} golpes={[[golpea + 1, 0.06]]}>
			<div style={{position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, background: 'rgba(0,0,0,0.35)'}} />
			<PancartaMano x={960} y={100} ancho={820} />
			<ConoLuz x={960} y={-60} ancho={900} alto={1100} fuerza={0.55} />
			<Actor x={960} y={1000} alto={700}>
				<Muneco ropa={HITLER_1919} pose={pose} ojos="grandes" cejas="enojado" boca="grito" />
			</Actor>
			<Sudor x={cx} y={cy} desde={suda} tam={1} />
			<div style={{position: 'absolute', left: 600, top: 840 + (golpe ? 6 : 0), width: 720, height: 40, background: '#7a5230', border: `8px solid ${TINTA}`, borderRadius: 6}} />
			<div style={{position: 'absolute', left: 620, top: 880, width: 680, height: 220, background: 'linear-gradient(180deg, #5a3a1e, #3a2412)', border: `8px solid ${TINTA}`, borderTop: 'none'}} />
			{[700, 1220].map((x, i) => (
				<Jarra key={i} x={x} y={850 - (golpe ? 30 : 0)} alto={110} tiembla={golpe ? 10 : 2} />
			))}
		</Toma>
	);
};

const C1Fila: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscCerveceria tono="sepia" vacia humo={0.1} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.1], x: [160, -140]}} angulo={-3}>
			{/* la puerta de la cervecería como entrada de teatro */}
			<div style={{position: 'absolute', left: 1500, top: 240, width: 360, height: 660, background: '#3a1e14', border: `10px solid ${TINTA}`, borderRadius: '180px 180px 0 0'}}>
				<div style={{position: 'absolute', left: 30, right: 30, top: 60, bottom: 0, background: 'radial-gradient(ellipse at 50% 80%, rgba(255,200,120,0.8), rgba(255,160,60,0.2))', borderRadius: '150px 150px 0 0'}} />
			</div>
			<div style={{position: 'absolute', left: 1430, top: 130, width: 500, padding: '10px 0', background: '#a8262e', border: `8px solid ${TINTA}`, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 72, color: '#fff3c0', letterSpacing: 6}}>
				ENTRADAS
				<div style={{display: 'flex', justifyContent: 'space-around', marginTop: 6}}>
					{Array.from({length: 8}, (_, i) => (
						<div key={i} style={{width: 16, height: 16, borderRadius: '50%', background: Math.floor(f / 4 + i) % 2 ? '#ffe28a' : '#7a4a14'}} />
					))}
				</div>
			</div>
			{[1300, 1100, 900, 700, 500, 300, 100].map((x, i) => (
				<Actor key={i} x={x} y={1010} alto={600 - i * 10}>
					<Muneco
						ropa={PARROQUIANOS[i % PARROQUIANOS.length]}
						semilla={i * 3}
						pose={{...manosFrente([150, 520]), mi: 'agarra', ...manosFrente(undefined, [300, 470]), md: 'agarra'}}
						objIzq={<g transform="translate(-10 30) rotate(-10)"><rect x={-40} y={0} width={80} height={44} rx={4} fill="#ffe28a" stroke={TINTA} strokeWidth={5} /><line x1={-14} y1={0} x2={-14} y2={44} stroke={TINTA} strokeWidth={4} strokeDasharray="6 4" /></g>}
						ojos="feliz"
						cejas="neutral"
						boca="sonrisa"
					/>
				</Actor>
			))}
		</Toma>
	);
};

/* ---------- el letrero nuevo y la cabecera ---------- */

const C1Letrero: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const texto = 'PARTIDO NACIONALSOCIALISTA';
	const p = tramo(f, d + 6, antes(ini(36)) - 6);
	const n = Math.floor(p * texto.length);
	const bx = 290 + p * 1340;
	return (
		<Toma escena={<EscCerveceria tono="sepia" vacia humo={0.1} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.16], x: [120, -120], y: [60, 70]}} angulo={-2}>
			<div style={{position: 'absolute', left: 240, right: 240, top: 240, height: 200, background: '#e9dcb4', border: `10px solid ${TINTA}`, borderRadius: 10, boxShadow: '12px 14px 0 rgba(0,0,0,0.3)'}}>
				<div style={{position: 'absolute', left: 40, top: 40, fontFamily: CONDENSADA, fontSize: 104, color: '#7a1e1e', letterSpacing: 6, whiteSpace: 'nowrap'}}>{texto.slice(0, n)}</div>
			</div>
			{/* la pancarta vieja, en el suelo */}
			<div style={{position: 'absolute', left: 420, top: 930, width: 560, padding: '8px 0', background: '#efe6cf', border: `6px solid ${TINTA}`, transform: 'rotate(8deg)', textAlign: 'center', fontFamily: "'Comic Sans MS', cursive", fontWeight: 700, fontSize: 40, color: '#2a2218', opacity: 0.85}}>
				PARTIDO OBRERO ALEMÁN
			</div>
			{/* la brocha */}
			<svg width={120} height={260} viewBox="0 0 120 260" style={{position: 'absolute', left: bx - 60, top: 270 + Math.sin(f / 2) * 20, overflow: 'visible'}}>
				<rect x={50} y={90} width={20} height={170} rx={8} fill="#8a5a32" stroke={TINTA} strokeWidth={6} />
				<rect x={30} y={60} width={60} height={34} fill="#c9c9d0" stroke={TINTA} strokeWidth={6} />
				<path d="M 30 0 L 90 0 L 90 60 L 30 60 Z" fill="#7a1e1e" stroke={TINTA} strokeWidth={6} />
			</svg>
			<Actor x={Math.min(1700, bx + 160)} y={1060} alto={760} voltear>
				<Muneco ropa={SENOR_1} pose={{...manosEn(undefined, [380, 240]), md: 'agarra', ...manosFrente([170, 560]), cabeza: -10}} ojos="entrecerrados" cejas="neutral" boca="seria" />
			</Actor>
		</Toma>
	);
};

const C1Cabecera: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const sillaX = interpolate(f, [d + 2, d + 12], [960, 1160], clamp);
	const fx = interpolate(f, [d + 2, d + 12], [960, 700], clamp);
	const hx = interpolate(f, [d - 4, d + 10], [1560, 1160], clamp);
	const sienta = tramo(f, d + 12, d + 20);
	return (
		<Toma escena={<EscCerveceria tono="sepia" vacia humo={0.12} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12], x: [-60, -100]}} angulo={-2}>
			<div style={{position: 'absolute', left: 300, right: 300, top: 220, padding: '14px 0', background: '#e9dcb4', border: `9px solid ${TINTA}`, textAlign: 'center', fontFamily: CONDENSADA, fontSize: 80, color: '#7a1e1e', letterSpacing: 6}}>PARTIDO NACIONALSOCIALISTA</div>
			<Silla x={sillaX} y={1000} alto={520} color="#6a3a1e" />
			<Actor x={fx} y={1010} alto={640}>
				<Muneco ropa={FUNDADOR} pose={{...manosEn([20, 330], [380, 330]), mi: 'abierta', md: 'abierta', agacha: f < d + 2 ? 0.35 : 0, cuerpo: f > d + 2 ? -8 : 0}} ojos="grandes" cejas="sorprendido" boca="o" />
			</Actor>
			<Actor x={hx} y={1010} alto={640}>
				<Muneco ropa={HITLER_1919} pose={{...manosEn([120, 560], [280, 560]), mi: 'puno', md: 'puno', agacha: 0.35 * sienta}} camina={f < d + 10 ? 1.5 : 0} ojos="entrecerrados" cejas="arrogante" boca="picara" />
			</Actor>
			<MesaFrente x={960} y={870} ancho={1400} />
		</Toma>
	);
};

/* ---------- un partido de cervecería no le quita el sueño a nadie ---------- */

const C1Siesta: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscOficinaBerlin nieve={false} lampara={0.6} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.28], x: [-200, -260], y: [-120, -150]}} angulo={2}>
			{/* sillón */}
			<div style={{position: 'absolute', left: 1020, top: 480, width: 560, height: 520, background: '#6a2a2a', border: `10px solid ${TINTA}`, borderRadius: '120px 120px 30px 30px'}} />
			<Actor x={1300} y={1000} alto={700}>
				<Muneco ropa={SENOR_3} pose={{...manosFrente([170, 520], [230, 520]), mi: 'relajada', md: 'relajada', agacha: 0.4, cabeza: 14 + Math.sin(f / 12) * 3}} ojos="cerrados" cejas="neutral" boca="o" respira />
			</Actor>
			<div style={{position: 'absolute', left: 1000, top: 760, width: 600, height: 60, background: '#6a2a2a', border: `10px solid ${TINTA}`, borderRadius: 30}} />
			{/* el periódico sobre la barriga */}
			<div style={{position: 'absolute', left: 1170, top: 640, width: 260, height: 150, background: '#efe9d8', border: `6px solid ${TINTA}`, transform: 'rotate(-8deg)', fontFamily: CONDENSADA, fontSize: 26, textAlign: 'center', padding: 8, boxSizing: 'border-box', color: '#2a2218'}}>
				UN PARTIDO DE CERVECERÍA
				<div style={{height: 6, background: 'rgba(0,0,0,0.3)', margin: '10px 10px'}} />
				<div style={{height: 6, background: 'rgba(0,0,0,0.3)', margin: '10px 20px'}} />
			</div>
			{[0, 1, 2].map((i) => {
				const u = ((f - d + i * 16) % 48) / 48;
				return (
					<div key={i} style={{position: 'absolute', left: 1400 + u * 160, top: 380 - u * 220, fontFamily: CONDENSADA, fontSize: 70 + u * 40, color: '#f2f0e6', opacity: 1 - u, WebkitTextStroke: `4px ${TINTA}`, paintOrder: 'stroke'}}>
						Z
					</div>
				);
			})}
		</Toma>
	);
};

/* ---------- Hitler tiene prisa: el reloj de bolsillo desbocado ---------- */

const C1Reloj: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const mucho = antes(pal(38, 'Muchísima'));
	const vel = f < mucho ? 6 : 24;
	return (
		<Toma escena={<EscLiso color="#2a1a10" luz="255,200,130" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.35], r: [-3, 4]}} golpes={[[mucho, 0.08]]}>
			{f >= mucho &&
				Array.from({length: 10}, (_, i) => (
					<div key={i} style={{position: 'absolute', left: 960 + Math.cos(i * 0.63) * 380 - 60, top: 560 + Math.sin(i * 0.63) * 330, width: 120, height: 10, background: '#f2e6c8', opacity: 0.5, transform: `rotate(${i * 36 + 90}deg)`}} />
				))}
			<RelojBolsillo x={960} y={560} tam={560} vel={vel} />
		</Toma>
	);
};

export const PLANOS_C1: Plano[] = [
	{n: 'c1-pizarra', d: fin(15) + 2, e: 'pantalla', C: C1Pizarra},
	{n: 'c1-alquila', d: antes(pal(16, 'no')), e: 'latigoDer', C: C1Alquila},
	{n: 'c1-marco', d: antes(pal(16, 'novia')), e: 'latigoIzq', C: C1Marco},
	{n: 'c1-plan', d: antes(pal(16, 'plan')), e: 'latigoDer', C: C1Plan},
	{n: 'c1-espia', d: antes(pal(17, 'espía')), e: 'zoom', C: C1Espia},
	{n: 'c1-puerta', d: ini(19), e: 'latigoDer', C: C1Puerta},
	{n: 'c1-cuarto', d: ini(21), e: 'zoom', C: C1Cuarto},
	{n: 'c1-alguien', d: ini(23), e: 'latigoIzq', C: C1Alguien},
	{n: 'c1-grita', d: ini(24), e: 'zoom', C: C1Grita},
	{n: 'c1-fundador', d: ini(25), e: 'latigoDer', C: C1Fundador},
	{n: 'c1-dicen', d: ini(26), e: 'latigoIzq', C: C1Dicen},
	{n: 'c1-boca', d: antes(pal(27, 'bocota')), e: 'zoom', C: C1Boca},
	{n: 'c1-afilia', d: ini(28), e: 'latigoDer', C: C1Afilia},
	{n: 'c1-carnet', d: ini(30), e: 'zoom', C: C1Carnet},
	{n: 'c1-globo', d: ini(32), e: 'latigoIzq', C: C1Globo},
	{n: 'c1-pancarta', d: ini(33), e: 'latigoDer', C: C1Pancarta},
	{n: 'c1-show', d: ini(34), e: 'zoom', C: C1Show},
	{n: 'c1-fila', d: antes(pal(34, 'gente')), e: 'latigoDer', C: C1Fila},
	{n: 'c1-letrero', d: ini(35), e: 'latigoIzq', C: C1Letrero},
	{n: 'c1-cabecera', d: ini(36), e: 'zoom', C: C1Cabecera},
	{n: 'c1-siesta', d: ini(37), e: 'latigoDer', C: C1Siesta},
	{n: 'c1-reloj', d: ini(38), e: 'zoom', C: C1Reloj},
];

export const SONIDOS_C1: [string, number, number][] = [
	['murmullo', fin(15) + 2, 0.5],
	['pop', antes(pal(16, 'no')), 0.5],
	['pop', antes(pal(16, 'novia')), 0.5],
	['hoja', antes(pal(16, 'plan')), 0.6],
	['murmullo', ini(21), 0.6],
	['jarras', antes(pal(24, 'gritar')), 0.7],
	['vapor', antes(pal(24, 'gritar')), 0.7],
	['tictac', antes(pal(24, 'no')), 0.7],
	['arpa', ini(25) + 8, 0.6],
	['boing', antes(pal(27, 'bocota')), 0.6],
	['objeto', antes(pal(28, 'partido')) + 12, 0.7],
	['garabato', antes(ini(29)), 0.7],
	['ding', antes(pal(30, '555')), 0.7],
	['desinfla', antes(pal(32, 'Pues')) + 2, 0.9],
	['pop', antes(pal(32, '501')), 0.6],
	['boing', ini(33) + 4, 0.4],
	['mazo', antes(pal(34, 'golpea')) + 1, 0.8],
	['aplausos', antes(pal(34, 'gente')), 0.5],
	['caja', antes(pal(34, 'gente')) + 10, 0.5],
	['garabato', ini(35) + 6, 0.6],
	['derrape', ini(36) + 2, 0.5],
	['ronquido', ini(37) + 6, 0.8],
	['tictac', ini(38), 0.9],
];

export {SERIF};
