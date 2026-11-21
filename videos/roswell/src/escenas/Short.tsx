import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {MaquinaEscribir} from '../componentes/Gamer';
import {Actor, Muneco, alcanzar, manosEn, manosFrente} from '../componentes/Muneco';
import {CamaraFoto} from '../componentes/Objetos';
import {Toma} from '../componentes/Toma';
import {Sello} from '../componentes/Utileria';
import {CONDENSADA} from '../fuentes';
import {Montaje, P, Plano, TINTA, antes, clamp, fin, ini, pal, tramo} from './base';
import {brazo} from './compartidas';
import {Candado, Periodico, Silueta} from './utileria_c89';
import {
	CadenaGlobos,
	EscDesiertoNoche,
	EscRancho,
	FOTOGRAFO,
	GENERAL_47,
	GRANJERO,
	GloboRisa,
	Imprenta,
	Informe1994,
	LetreroRoswell,
	MILITAR_VIEJO,
	Microfono,
	MunecoPrueba,
	Nube,
	OvniBrillante,
	Oveja,
	PolvoTelarana,
	Red,
	Restos,
	SOLDADO_47,
	TeleRetro,
} from './utileria_roswell';

/*
 * Short «Roswell: el ovni que era un globo espía» (1080x1920, 30 fps).
 * Sin cortes secos: barridos y zooms. La autopsia es una parodia en dibujo, sin nada sangriento.
 */

const Liso: React.FC<{color: string; luz?: string}> = ({color, luz}) => (
	<div style={{position: 'absolute', inset: 0, background: color}}>
		{luz && <div style={{position: 'absolute', left: -300, top: 200, width: 1680, height: 1680, borderRadius: '50%', background: `radial-gradient(circle, rgba(${luz},0.28) 0%, rgba(${luz},0) 62%)`}} />}
	</div>
);

/* ---------------- 0 · el periódico que gira (y se arruga en «lo negó») ---------------- */

const PeriodicoGira: React.FC<{d: number; arruga: number}> = ({d, arruga}) => {
	const f = useCurrentFrame();
	const giro = tramo(f, d - 4, d + 26, (t) => 1 - Math.pow(1 - t, 3));
	const a = tramo(f, arruga, arruga + 10);
	return (
		<div style={{position: 'absolute', inset: 0, transform: `rotate(${(1 - giro) * 720 - 4}deg) scale(${0.15 + 0.85 * giro})`, transformOrigin: '540px 860px'}}>
			<div style={{position: 'absolute', inset: 0, transform: `scale(${1 - 0.25 * a}, ${1 - 0.45 * a}) rotate(${a * 8}deg)`, transformOrigin: '540px 860px', filter: `brightness(${1 - 0.3 * a})`}}>
				<Periodico x={540} y={480} ancho={900} titular="¡CAPTURAN UN PLATILLO VOLADOR!" fecha="8 DE JULIO DE 1947" nombre="Roswell Daily Record" />
				{a > 0 && (
					<svg viewBox="0 0 900 800" width={900} height={800} style={{position: 'absolute', left: 90, top: 480, opacity: a}}>
						{['M 0 200 L 300 260 L 520 180 L 900 250', 'M 100 0 L 220 300 L 160 560 L 260 800', 'M 600 0 L 520 320 L 640 600 L 560 800', 'M 0 520 L 340 470 L 600 560 L 900 500'].map((dd, i) => (
							<path key={i} d={dd} stroke="rgba(40,30,20,0.55)" strokeWidth={6} fill="none" />
						))}
					</svg>
				)}
			</div>
		</div>
	);
};

const R0: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscDesiertoNoche />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [0, 30]}}>
		<PeriodicoGira d={d} arruga={antes(pal(0, 'negó'))} />
	</Toma>
);

/* ---------------- 1 · el granjero, las ovejas y los restos ---------------- */

const R1: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscRancho />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], x: [20, -20]}}>
		<Restos x={560} y={1500} tam={520} brillo={0.6} />
		<Oveja x={200} y={1380} tam={300} fase={0} />
		<Oveja x={900} y={1330} tam={260} voltear fase={2} />
		<Oveja x={860} y={1700} tam={300} voltear fase={4} />
		<Actor x={500} y={1640} alto={1100}>
			<Muneco ropa={GRANJERO} pose={{agacha: 0.35, cuerpo: 14, ...manosFrente([170, 640], [250, 660]), mi: 'agarra', md: 'abierta', cabeza: 14}} ojos="grandes" cejas="sorprendido" boca="o" />
		</Actor>
	</Toma>
);

/** primer plano: los restos en la mano del granjero */
const ManoRestos: React.FC = () => (
	<>
		<div style={{position: 'absolute', left: 230, top: 1180, width: 620, height: 900, background: '#b8442e', border: `12px solid ${TINTA}`, borderRadius: '120px 120px 0 0'}} />
		<div style={{position: 'absolute', left: 170, top: 820, width: 740, height: 460, background: '#f2dcc8', border: `12px solid ${TINTA}`, borderRadius: '200px 200px 220px 220px'}} />
		{[0, 1, 2, 3].map((i) => (
			<div key={i} style={{position: 'absolute', left: 160 + i * 180, top: 700 + Math.abs(i - 1.5) * 30, width: 150, height: 240, background: '#f2dcc8', border: `12px solid ${TINTA}`, borderRadius: 75}} />
		))}
		<Restos x={540} y={860} tam={820} brillo={1} />
	</>
);

const R1b: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<EscRancho />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.07], y: [0, 30]}}>
		<div style={{position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.15)'}} />
		<ManoRestos />
	</Toma>
);

/* ---------------- 1 · el comunicado: máquina de escribir e imprenta ---------------- */

const R2: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Liso color="#3a3a30" luz="255,230,170" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.15], y: [40, 80]}}>
		<div style={{position: 'absolute', left: 120, top: 380, padding: '10px 26px', background: '#f6efdc', border: `7px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 52, color: TINTA, transform: 'rotate(-3deg)'}}>BASE AÉREA DE ROSWELL</div>
		<MaquinaEscribir x={540} y={1380} ancho={900} hoja={1} titular="CAPTURAMOS UN PLATILLO" desde={d + 4} />
	</Toma>
);

const R2b: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<Liso color="#2a2a30" luz="255,230,170" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [-20, -50]}}>
			<Imprenta x={540} y={250} ancho={920} sale={tramo(f, d + 2, h - 6)} titular="¡CAPTURAN UN PLATILLO VOLADOR!" />
		</Toma>
	);
};

/* ---------------- 2 · el general y los restos en el suelo, entre flashes ---------------- */

const OficinaGeneral: React.FC = () => (
	<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #6a5a48 0%, #4a3e30 55%, #2a2018 100%)'}}>
		{[0, 1, 2].map((i) => (
			<div key={i} style={{position: 'absolute', left: 60 + i * 340, top: 260, width: 280, height: 700, border: '8px solid rgba(0,0,0,0.25)', borderRadius: 8}} />
		))}
		<div style={{position: 'absolute', left: 380, top: 330, width: 320, height: 230, background: '#c9a43a', border: `8px solid ${TINTA}`, padding: 14, boxSizing: 'border-box'}}>
			<div style={{width: '100%', height: '100%', background: 'linear-gradient(180deg, #8fa6b8, #6a7a5a)', border: `4px solid ${TINTA}`}} />
		</div>
		<div style={{position: 'absolute', left: 0, right: 0, top: 1080, bottom: 0, background: 'linear-gradient(180deg, #5a4030, #2e2018)'}} />
	</div>
);

const R3: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const flashes = [d + 8, d + 26, pal(4, 'globo'), fin(4) - 4];
	const flash = flashes.reduce((m, t) => Math.max(m, f >= t ? interpolate(f - t, [0, 1, 7], [0, 1, 0], clamp) : 0), 0);
	const habla = f >= ini(4) && f < fin(4);
	return (
		<Toma escena={<OficinaGeneral />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], y: [10, 40]}} encima={<div style={{position: 'absolute', inset: 0, background: '#fff', opacity: 0.35 * flash}} />}>
			<Restos x={560} y={1380} tam={760} />
			<Actor x={600} y={1300} alto={1000}>
				<Muneco ropa={GENERAL_47} pose={{agacha: 0.45, ...brazo(1, alcanzar(1, 320, 520)), md: 'agarra', ...manosEn([160, 560]), mi: 'puno', cabeza: -6}} objDer={<g transform="translate(0 60)"><rect x={-60} y={-10} width={120} height={70} fill="#c9ced6" stroke={TINTA} strokeWidth={5} /></g>} ojos="entrecerrados" cejas="enojado" boca="seria" hablando={habla} />
			</Actor>
			<Actor x={160} y={1820} alto={900}>
				<Muneco ropa={FOTOGRAFO} pose={{...manosEn([150, 300], [262, 250]), mi: 'agarra', md: 'agarra', frenteD: 1, frenteI: 1}} objDer={<CamaraFoto rot={-90} flash={flash} />} ojos="cerrados" cejas="neutral" boca="seria" />
			</Actor>
			<Actor x={930} y={1840} alto={900} voltear>
				<Muneco ropa={FOTOGRAFO} pose={{...manosEn([150, 300], [262, 250]), mi: 'agarra', md: 'agarra', frenteD: 1, frenteI: 1}} objDer={<CamaraFoto rot={-90} flash={flash} />} ojos="cerrados" cejas="neutral" boca="seria" />
			</Actor>
		</Toma>
	);
};

/* ---------------- 2 · el mundo se ríe y Roswell se sonroja ---------------- */

const R4: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Liso color="#0a0c20" luz="120,160,255" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08]}}>
		<GloboRisa x={540} y={880} tam={820} />
	</Toma>
);

const R4b: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<EscRancho />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12]}}>
			<LetreroRoswell x={540} y={520} ancho={860} rubor={tramo(f, d + 2, d + 14)} />
		</Toma>
	);
};

/* ---------------- 3 · escalada: polvo, la tele de 1978, testigos y la «autopsia» ---------------- */

const R5: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const t = tramo(f, d + 2, h, (u) => u);
	const anio = Math.round(1947 + 30 * t);
	return (
		<Toma escena={<Liso color="#3a3226" luz="255,220,170" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}}>
			<Periodico x={540} y={480} ancho={900} titular="¡CAPTURAN UN PLATILLO VOLADOR!" fecha="8 DE JULIO DE 1947" nombre="Roswell Daily Record" rot={-3} />
			<PolvoTelarana t={t} />
			<div style={{position: 'absolute', left: 340, top: 1500, width: 400, padding: '6px 0', textAlign: 'center', background: '#f6efdc', border: `8px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 110, color: TINTA}}>{anio}</div>
		</Toma>
	);
};

const R6: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const susurra = f >= ini(8) && f < fin(8);
	return (
		<Toma escena={<Liso color="#5a4632" luz="255,210,150" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.1], y: [0, 40]}}>
			{/* papel tapiz de los 70 */}
			<div style={{position: 'absolute', inset: 0, background: 'repeating-radial-gradient(circle at 50% 50%, rgba(200,120,40,0.18) 0 30px, rgba(120,70,20,0.12) 30px 60px)'}} />
			<TeleRetro x={540} y={560} ancho={940}>
				<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #4a6a8a, #2a3a4a)'}} />
				<Actor x={300} y={820} alto={760}>
					<Muneco ropa={MILITAR_VIEJO} pose={{...manosEn(undefined, [236, 292], {}, true), md: 'abierta', frenteD: 1, cabeza: 8}} ojos="entrecerrados" cejas="preocupado" boca={susurra ? 'o' : 'seria'} hablando={susurra} />
				</Actor>
				<div style={{position: 'absolute', left: 20, top: 20, fontFamily: CONDENSADA, fontSize: 40, color: '#ffe27a', textShadow: '0 3px 0 #000'}}>1978</div>
			</TeleRetro>
			<div style={{position: 'absolute', left: 0, right: 0, top: 1500, bottom: 0, background: '#3a2a1a', borderTop: `10px solid ${TINTA}`}} />
		</Toma>
	);
};

const R7: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma escena={<Liso color="#141826" luz="150,170,230" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06], x: [20, -20]}}>
			{[180, 540, 900].map((x, i) => (
				<React.Fragment key={i}>
					<Silueta x={x} y={1500 + (i % 2) * 60} alto={1000} ropa={i === 1 ? GRANJERO : FOTOGRAFO} voltear={i === 2} tono={0.06} pose={i === 1 ? manosEn(undefined, [236, 292], {}, true) : {}} />
					<div style={{position: 'absolute', left: x - 120, top: 560 + (i % 2) * 70, padding: '12px 22px', background: '#f4f1e8', border: `6px solid ${TINTA}`, borderRadius: 30, fontFamily: CONDENSADA, fontSize: 52, color: TINTA, opacity: tramo(f, d + 4 + i * 6, d + 10 + i * 6)}}>
						psst…
					</div>
				</React.Fragment>
			))}
		</Toma>
	);
};

/** la «autopsia» en la tele borrosa: una sábana, una cabecita gris y un señor con traje blanco. Nada sangriento. */
const AutopsiaParodia: React.FC = () => (
	<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #c9d2c8, #8a9a8a)'}}>
		<div style={{position: 'absolute', left: 60, top: 470, width: 640, height: 60, background: '#6a7a7a', border: `6px solid ${TINTA}`}} />
		<div style={{position: 'absolute', left: 80, top: 400, width: 560, height: 90, background: '#f4f4f0', border: `6px solid ${TINTA}`, borderRadius: '40px 40px 10px 10px'}} />
		<svg width={180} height={150} viewBox="0 0 180 150" style={{position: 'absolute', left: 560, top: 300}}>
			<ellipse cx={90} cy={80} rx={70} ry={66} fill="#a8b0a8" stroke={TINTA} strokeWidth={6} />
			<ellipse cx={62} cy={80} rx={20} ry={30} fill="#141418" transform="rotate(-20 62 80)" />
			<ellipse cx={118} cy={80} rx={20} ry={30} fill="#141418" transform="rotate(20 118 80)" />
		</svg>
		<div style={{position: 'absolute', left: 140, top: 120, width: 220, height: 300, background: '#f6f6f2', border: `6px solid ${TINTA}`, borderRadius: '110px 110px 30px 30px'}}>
			<div style={{position: 'absolute', left: 50, top: 40, width: 120, height: 70, background: '#2a3a4a', borderRadius: 30}} />
		</div>
	</div>
);

const R8: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Liso color="#3a2a4a" luz="160,190,255" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [0, 40]}}>
		{/* papel tapiz de los 90 */}
		<div style={{position: 'absolute', inset: 0, background: 'repeating-linear-gradient(90deg, rgba(120,170,160,0.25) 0 40px, rgba(200,120,150,0.18) 40px 80px)'}} />
		<TeleRetro x={540} y={360} ancho={900} borrosa={3.5} madera="#3a3a44">
			<AutopsiaParodia />
			<div style={{position: 'absolute', left: 16, top: 12, fontFamily: CONDENSADA, fontSize: 36, color: '#ffffff', textShadow: '0 3px 0 #000'}}>«AUTOPSIA ALIENÍGENA»</div>
		</TeleRetro>
		{/* el sofá y la familia de espaldas */}
		<div style={{position: 'absolute', left: -40, right: -40, top: 1420, height: 520, background: '#7a3a4a', border: `10px solid ${TINTA}`, borderRadius: '80px 80px 0 0'}} />
		{[[230, 1290, 170], [540, 1250, 190], [820, 1330, 130]].map(([x, y, r], i) => (
			<React.Fragment key={i}>
				<div style={{position: 'absolute', left: x - r * 1.3, top: y + r * 0.9, width: r * 2.6, height: r * 2.4, background: '#0e0e14', borderRadius: `${r}px ${r}px 0 0`}} />
				<div style={{position: 'absolute', left: x - r, top: y - r * 0.6, width: r * 2, height: r * 2, borderRadius: '50%', background: '#0e0e14', boxShadow: '0 0 40px 10px rgba(140,170,255,0.35)'}} />
			</React.Fragment>
		))}
	</Toma>
);

/* ---------------- 4 · el giro: el informe de 1994 ---------------- */

const R9: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const tacha = tramo(f, antes(pal(12, 'ovni')), pal(12, 'ovni') + 8, (t) => t);
	return (
		<Toma escena={<Liso color="#1e2228" luz="220,230,255" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.08], y: [0, -40]}} encima={<Sello x={700} y={1430} texto="SECRETO" desde={d + 6} tam={110} rot={-8} />}>
			<Informe1994 x={540} y={330} ancho={900} tacha={tacha} />
		</Toma>
	);
};

/* ---------------- 5 · el mecanismo: globos espía con micrófonos ---------------- */

const R10: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const boom = antes(pal(13, 'detectar'));
	const ondas = f - boom;
	return (
		<Toma escena={<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #0e1e4a 0%, #2a5a9a 50%, #8ab6e0 85%, #c9a06a 86%, #8a6a4a 100%)'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.04], y: [80, -40]}}>
			<Nube x={250} y={300} ancho={560} />
			<Nube x={850} y={520} ancho={480} opacidad={0.75} />
			<CadenaGlobos x={430} abajo={1300} arriba={-200} />
			<Microfono x={430} y={1290} tam={120} />
			<Nube x={700} y={980} ancho={520} opacidad={0.7} />
			{/* explosión lejana en el horizonte (silueta) y ondas de sonido que llegan al micrófono */}
			{f >= boom && (
				<>
					<svg width={260} height={240} viewBox="0 0 260 240" style={{position: 'absolute', left: 760, top: 1400, opacity: Math.min(1, ondas / 6)}}>
						<ellipse cx={130} cy={70} rx={110} ry={60} fill="#5a3a4a" />
						<rect x={110} y={100} width={40} height={130} fill="#5a3a4a" />
						<ellipse cx={130} cy={230} rx={100} ry={16} fill="#5a3a4a" />
					</svg>
					{[0, 1, 2, 3].map((i) => {
						const r = (ondas - i * 7) * 22;
						if (r <= 0 || r > 700) return null;
						return <div key={i} style={{position: 'absolute', left: 890 - r, top: 1470 - r, width: r * 2, height: r * 2, borderRadius: '50%', border: '8px solid rgba(255,236,160,0.75)', clipPath: 'polygon(0 0, 50% 0, 50% 50%, 0 50%)'}} />;
					})}
				</>
			)}
		</Toma>
	);
};

const R11: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Liso color="#22262e" luz="220,220,230" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.06]}}>
		<div style={{position: 'absolute', left: 140, top: 520, width: 800, height: 600, background: '#c99a4a', border: `10px solid ${TINTA}`, borderRadius: 14, transform: 'rotate(-4deg)'}}>
			<div style={{position: 'absolute', left: 0, top: -70, width: 300, height: 90, background: '#b88a3a', border: `10px solid ${TINTA}`, borderRadius: '18px 18px 0 0'}} />
			<div style={{position: 'absolute', left: 60, top: 80, padding: '10px 26px', background: '#f6efdc', border: `7px solid ${TINTA}`, fontFamily: CONDENSADA, fontSize: 64, color: TINTA}}>PROYECTO ULTRASECRETO</div>
			<div style={{position: 'absolute', left: 260, top: 260, fontFamily: CONDENSADA, fontSize: 90, color: '#c8202a', border: '8px solid #c8202a', padding: '0 20px', transform: 'rotate(-8deg)'}}>SECRETO</div>
		</div>
		<Candado x={540} y={1300} tam={300} cierra={d + 10} />
	</Toma>
);

const R11b: React.FC<P> = ({d, h, e, s}) => (
	<Toma escena={<Liso color="#0a0c20" luz="120,160,255" />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12]}}>
		<GloboRisa x={540} y={880} tam={820} />
	</Toma>
);

/* ---------------- 6 · el remate: muñecos de prueba y el «ovni» que era su propio globo ---------------- */

const R12: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const cae = (f - d) * 7;
	return (
		<Toma escena={<div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #4a8ad8 0%, #9ccaf0 70%, #e8d0a0 100%)'}} />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.0, 1.05]}}>
			<Nube x={260} y={420} ancho={500} />
			<Nube x={860} y={900} ancho={420} opacidad={0.8} />
			<div style={{position: 'absolute', left: 700, top: 60 - cae * 0.4, width: 220, height: 260, borderRadius: '50%', background: 'radial-gradient(circle at 35% 30%, #ffffff, #d8dce4 60%, #aab0bc)', border: `7px solid ${TINTA}`}} />
			<MunecoPrueba x={440} y={300 + Math.min(cae, 700)} tam={480} />
		</Toma>
	);
};

const R13: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const revela = tramo(f, antes(pal(17, 'globo')), pal(17, 'globo') + 8);
	const atrapa = tramo(f, d + 4, d + 16);
	// la cámara se aleja hasta el desierto de noche del principio
	const lejos = tramo(f, fin(17) - 6, h - 4);
	return (
		<Toma escena={<EscDesiertoNoche />} desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1, 1]}} encima={<Sello x={540} y={860} texto="MITO" desde={SELLO_MITO} color="#d6262e" tam={200} rot={-10} solido />}>
			<div style={{position: 'absolute', inset: 0, transform: `scale(${1 - 0.55 * lejos})`, transformOrigin: '540px 1500px', opacity: 1 - 0.2 * lejos}}>
				<Actor x={330} y={1720} alto={1000}>
					<Muneco ropa={SOLDADO_47} pose={{...brazo(1, alcanzar(1, 340, 200)), md: 'agarra', ...brazo(-1, alcanzar(-1, 150, 380)), mi: 'agarra', cabeza: -8}} ojos={revela > 0.5 ? 'grandes' : 'entrecerrados'} cejas={revela > 0.5 ? 'sorprendido' : 'enojado'} boca={revela > 0.5 ? 'o' : 'seria'} />
				</Actor>
				<Red x1={470} y1={1260} x2={640 + 60 * (1 - atrapa)} y2={900 - 80 * (1 - atrapa)} radio={190} />
				<OvniBrillante x={640} y={690} tam={420} revela={revela} />
			</div>
		</Toma>
	);
};

/** fin de la voz + 1,2 s: el sello de MITO ocupa el último segundo */
export const FIN_VIDEO = fin(17) + 36;
const SELLO_MITO = FIN_VIDEO - 30;

const PLANOS: Plano[] = [
	{n: 'periodico', d: 0, e: 'corte', C: R0},
	{n: 'granjero', d: ini(1), e: 'latigoDer', C: R1},
	{n: 'restos', d: antes(pal(1, 'goma')), e: 'zoom', C: R1b},
	{n: 'maquina', d: ini(2), e: 'latigoIzq', C: R2},
	{n: 'imprenta', d: antes(pal(2, 'Capturamos')), e: 'zoom', C: R2b},
	{n: 'general', d: ini(3), e: 'latigoDer', C: R3},
	{n: 'globo', d: ini(5), e: 'zoom', C: R4},
	{n: 'letrero', d: antes(pal(5, 'pueblo')), e: 'latigoIzq', C: R4b},
	{n: 'polvo', d: ini(6), e: 'latigoDer', C: R5},
	{n: 'tele78', d: ini(7), e: 'latigoIzq', C: R6},
	{n: 'testigos', d: ini(9), e: 'latigoDer', C: R7},
	{n: 'autopsia', d: ini(10), e: 'latigoIzq', C: R8},
	{n: 'informe', d: ini(11), e: 'zoom', C: R9},
	{n: 'globos', d: ini(13), e: 'latigoArriba', C: R10},
	{n: 'candado', d: ini(14), e: 'latigoDer', C: R11},
	{n: 'risa', d: antes(pal(14, 'prefirieron')), e: 'zoom', C: R11b},
	{n: 'muneco', d: ini(15), e: 'latigoArriba', C: R12},
	{n: 'red', d: ini(17), e: 'latigoDer', C: R13},
];

const WHOOSH: [string, number, number][] = PLANOS.filter((p) => p.e && p.e.startsWith('latigo')).map((p) => ['whoosh', p.d - 5, 0.35]);

export const SONIDOS: [string, number, number][] = [
	...WHOOSH,
	['viento', 0, 0.7],
	['arruga', antes(pal(0, 'negó')), 0.9],
	['viento', ini(1), 0.5],
	['balido', ini(1) + 10, 0.6],
	['teclas', ini(2) + 4, 0.7],
	['imprenta', antes(pal(2, 'Capturamos')) + 2, 0.7],
	['flash', ini(3) + 8, 0.6],
	['flash', ini(3) + 26, 0.6],
	['flash', pal(4, 'globo'), 0.6],
	['risas', ini(5), 0.9],
	['estatica', ini(7), 0.5],
	['susurro', ini(9) + 4, 0.8],
	['estatica', ini(10), 0.5],
	['sello', ini(11) + 6, 1.0],
	['garabato', antes(pal(12, 'ovni')), 0.8],
	['sonar', ini(13) + 6, 0.6],
	['boom', antes(pal(13, 'detectar')), 0.35],
	['clic', ini(14) + 10, 0.9],
	['risas', antes(pal(14, 'prefirieron')), 0.9],
	['pop', ini(15) + 6, 0.6],
	['whoosh', ini(17) + 4, 0.6],
	['ding', antes(pal(17, 'globo')), 0.7],
	['sello', SELLO_MITO, 1.0],
];

export const Historia: React.FC = () => <Montaje planos={PLANOS} fin={FIN_VIDEO} />;
