import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {Calendario, Destello, Etiqueta, Explosion} from '../componentes/Efectos';
import {COMPANERA, ENFERMERA, JUEZ, MEDICO, OFICINISTA, Personaje, VESNA} from '../componentes/Personaje';
import {EnMundo, Toma, Transicion} from '../componentes/Toma';
import {Bocadillo, Brillos, Confeti, Documento, Fundido, Icono, Puf, Rayos, Sello} from '../componentes/Utileria';
import {AvionPartido, Boom, Carrito, Certificado, ColaAvion, Cronometro, Escombros, FichaObjeto, LineasViento, Monitor, Nieve, Regla, Resena, Tarjeta, Zzz} from '../componentes/Vuelo';
import {TITULAR} from '../fuentes';
import {finFrase, palabra} from '../tiempos';

/* La historia de Vesna, toma por toma. Todo en cuadros GLOBALES. */

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const antes = (n: number) => n - 3;
const TINTA = '#1b1b1f';
const VESNA_SIN_GORRO = {...VESNA, gorra: 'ninguna' as const};

const W = {
	diezmil: palabra(0, '10.000'),
	sin: palabra(1, 'SIN'),
	paracaidas: palabra(1, 'PARACAÍDAS'),
	sobrevivio: palabra(2, 'SOBREVIVIÓ'),
	peor: palabra(3, 'peor'),
	aterrizaje: palabra(4, 'aterrizaje'),
	historia: palabra(4, 'historia'),
	vesna: palabra(5, 'Vesna'),
	anios: palabra(6, '23 años'),
	azafata: palabra(6, 'azafata'),
	confusion: palabra(7, 'confusión'),
	companera: palabra(7, 'compañera'),
	error: palabra(8, 'error'),
	minutos: palabra(9, '46 minutos'),
	despues: palabra(9, 'después'),
	boom: palabra(10, 'BOOM'),
	explosion: palabra(11, 'explosión'),
	aeronave: palabra(12, 'aeronave'),
	tres: palabra(12, 'tres'),
	cayo: palabra(13, 'cayó'),
	sobrevivir: palabra(14, 'sobrevivir'),
	carrito: palabra(16, 'carrito'),
	comida: palabra(16, 'comida'),
	carrito2: palabra(17, 'carrito'),
	supervivencia: palabra(17, 'supervivencia'),
	empleado: palabra(18, 'EMPLEADO'),
	nevado: palabra(19, 'nevado'),
	encontro: palabra(20, 'encontró'),
	auxiliarla: palabra(20, 'auxiliarla'),
	dias: palabra(21, '27 días'),
	gravisimas: palabra(22, 'gravísimas'),
	caminar: palabra(23, 'caminar'),
	record: palabra(24, 'récord'),
	verdad: palabra(25, 'VERDAD'),
	turbulencias: palabra(26, 'turbulencias'),
	masaje: palabra(26, 'masaje'),
};

export const FIN_VIDEO = finFrase(26) + 30;

type P = {d: number; h: number; e: Transicion; s: Transicion};

/* ---------- piezas de utilería pequeñas, solo de esta historia ---------- */

const ParacaidasTachado: React.FC<{x: number; y: number; desde: number; tam?: number}> = ({x, y, desde, tam = 360}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const p = interpolate(f, [desde, desde + 6], [0.3, 1], {...clamp, easing: Easing.out(Easing.back(2))});
	const tacha = interpolate(f, [desde + 6, desde + 12], [0, 1], clamp);
	return (
		<div style={{position: 'absolute', left: x - tam / 2, top: y - tam / 2, width: tam, height: tam, transform: `scale(${p})`}}>
			<svg viewBox="0 0 200 200" width="100%" height="100%" style={{overflow: 'visible'}}>
				<path d="M 20 90 Q 100 -10 180 90 Q 160 76 140 90 Q 120 76 100 90 Q 80 76 60 90 Q 40 76 20 90 Z" fill="#ff7a1a" stroke={TINTA} strokeWidth={8} strokeLinejoin="round" />
				<path d="M 60 90 Q 100 10 140 90" fill="#fff" opacity={0.6} />
				{[20, 60, 100, 140, 180].map((x0) => (
					<line key={x0} x1={x0} y1={90} x2={100} y2={160} stroke={TINTA} strokeWidth={4} />
				))}
				<rect x={84} y={156} width={32} height={30} rx={6} fill="#6b4a2b" stroke={TINTA} strokeWidth={5} />
				<circle cx={100} cy={100} r={92} fill="none" stroke="#e3262e" strokeWidth={18} opacity={tacha} />
				<line x1={36} y1={164} x2={36 + 128 * tacha} y2={164 - 128 * tacha} stroke="#e3262e" strokeWidth={18} strokeLinecap="round" />
			</svg>
		</div>
	);
};

const Botiquin: React.FC<{x: number; y: number; desde: number}> = ({x, y, desde}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const s = interpolate(f, [desde, desde + 6], [0.2, 1], {...clamp, easing: Easing.out(Easing.back(2))});
	return (
		<div style={{position: 'absolute', left: x - 110, top: y - 90, width: 220, height: 180, transform: `scale(${s})`}}>
			<svg viewBox="0 0 220 180" width="100%" height="100%" style={{overflow: 'visible'}}>
				<path d="M 80 30 L 80 12 L 140 12 L 140 30" stroke={TINTA} strokeWidth={10} fill="none" />
				<rect x={8} y={30} width={204} height={142} rx={18} fill="#fff" stroke={TINTA} strokeWidth={10} />
				<rect x={94} y={58} width={32} height={86} rx={6} fill="#e3262e" />
				<rect x={67} y={85} width={86} height={32} rx={6} fill="#e3262e" />
			</svg>
		</div>
	);
};

const Cartel: React.FC<{x: number; y: number; texto: string; desde: number; color?: string; tam?: number}> = ({x, y, texto, desde, color = '#ffd84a', tam = 76}) => {
	const f = useCurrentFrame();
	if (f < desde) return null;
	const s = interpolate(f, [desde, desde + 7], [0, 1], {...clamp, easing: Easing.out(Easing.back(2.2))});
	return (
		<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, 0) scale(${s}) rotate(-3deg)`, background: color, border: `10px solid ${TINTA}`, borderRadius: 26, padding: '12px 36px 18px', fontFamily: TITULAR, fontWeight: 900, fontSize: tam, color: TINTA, whiteSpace: 'nowrap', boxShadow: '0 12px 0 rgba(0,0,0,0.4)'}}>
			{texto}
		</div>
	);
};

const temblor = (amp: number) => () => amp;

/* ------------------------------ GANCHO ------------------------------ */

const Caida: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma fondo="cielo_alto.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.3], y: [-80, 60]}} sacudida={temblor(4)}>
			<LineasViento />
			<EnMundo x={540 + Math.sin(f / 9) * 40} y={1500} alto={1050} rot={Math.sin(f / 7) * 12}>
				<Personaje diseno={VESNA} ojos="grandes" cejas="sorprendido" boca="grito" brazoIzq={150 + Math.sin(f / 2) * 15} brazoDer={150 + Math.cos(f / 2) * 15} sombra={false} />
			</EnMundo>
		</Toma>
	);
};

const Altura: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const y = interpolate(f, [d, h], [300, 1500], clamp);
	return (
		<Toma fondo="cielo_abajo.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.2]}}>
			<LineasViento intensidad={0.7} />
			<Regla desde={d} hasta={h} />
			<EnMundo x={760} y={y} alto={380} rot={f * 6}>
				<Personaje diseno={VESNA} ojos="grandes" cejas="sorprendido" boca="grito" brazoIzq={150} brazoDer={150} sombra={false} />
			</EnMundo>
			<Cartel x={700} y={260} texto="10.000 m" desde={W.diezmil} tam={96} />
		</Toma>
	);
};

const SinParacaidas: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma fondo="cielo_alto.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.3, 1.4], y: [40, 40]}} sacudida={(g) => (g >= W.paracaidas ? 10 : 5)} golpes={[[W.paracaidas, 0.1]]}>
			<LineasViento intensidad={1.3} />
			<EnMundo x={540} y={2150} alto={1650} rot={Math.sin(f / 6) * 5}>
				<Personaje diseno={VESNA} ojos="grandes" cejas="sorprendido" boca="grito" brazoIzq={150} brazoDer={150} sombra={false} />
			</EnMundo>
			<ParacaidasTachado x={790} y={660} desde={W.sin} tam={320} />
		</Toma>
	);
};

const Sobrevivio: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="bosque_amanecer.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.16]}} golpes={[[W.sobrevivio, 0.08]]}>
		<Rayos x={540} y={900} color="#fff2c4" opacidad={0.3} />
		<Nieve n={40} />
		<EnMundo x={540} y={1800} alto={1080}>
			<Personaje diseno={VESNA} acc={{vendas: true}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={150} brazoDer={150} />
		</EnMundo>
		<Brillos x={540} y={950} desde={W.sobrevivio} radio={420} n={9} />
	</Toma>
);

const PeorVuelo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma fondo="cabina.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.22], r: [-6, 6]}} sacudida={temblor(14)}>
			<Escombros desde={d - 10} n={8} subiendo />
			<EnMundo x={540} y={1820} alto={1060} rot={Math.sin(f / 3) * 6}>
				<Personaje diseno={VESNA} ojos="grandes" cejas="preocupado" boca="mueca" brazoIzq={110 + Math.sin(f) * 20} brazoDer={110 + Math.cos(f) * 20} />
			</EnMundo>
			<Resena x={540} y={300} desde={W.peor} />
		</Toma>
	);
};

const MejorAterrizaje: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="bosque_amanecer.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.18, 1.1], y: [-60, -20]}}>
		<Nieve n={30} />
		{[240, 540, 840].map((x, i) => (
			<EnMundo key={x} x={x} y={1180} alto={520}>
				<Personaje diseno={JUEZ} semilla={i * 3} ojos="feliz" cejas="arrogante" boca="sonrisa" brazoDer={150} codoDer={-10} />
			</EnMundo>
		))}
		{[240, 540, 840].map((x, i) => (
			<Tarjeta key={x} x={x + 70} y={560} texto="10" desde={W.aterrizaje + i * 5} rot={[-6, 2, 7][i]} />
		))}
		<EnMundo x={540} y={2340} alto={980}>
			<Personaje diseno={VESNA} acc={{vendas: true}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={120} brazoDer={120} />
		</EnMundo>
		<Puf x={540} y={1900} desde={d - 2} tam={900} />
		<Confeti desde={W.historia} n={50} />
	</Toma>
);

/* ------------------------------ CONTEXTO ------------------------------ */

const SeLlamaba: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma fondo="pista.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.18], x: [40, -20]}}>
			<EnMundo x={500} y={1800} alto={1050}>
				<Personaje diseno={VESNA} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoDer={140 + Math.sin(f / 3) * 18} codoDer={-25} />
			</EnMundo>
			<Etiqueta x={500} y={620} texto="VESNA" desde={W.vesna - 2} tam={80} />
		</Toma>
	);
};

const Azafata: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="cabina.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.16], y: [0, -20]}}>
		<EnMundo x={380} y={1800} alto={1040}>
			<Personaje diseno={VESNA} ojos="normal" cejas="arrogante" boca="sonrisa" brazoDer={70} codoDer={-30} />
		</EnMundo>
		<Carrito x={790} y={1830} ancho={380} ojos="normal" />
		<Cartel x={300} y={330} texto="23 AÑOS" desde={W.anios} tam={70} color="#ffffff" />
		<Brillos x={380} y={780} desde={W.azafata} radio={300} />
	</Toma>
);

const Confusion: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const duda = f >= W.confusion - 2;
	const elige = f >= W.companera;
	const mira = duda && !elige ? Math.floor((f - W.confusion) / 8) % 2 === 0 : false;
	return (
		<Toma fondo="oficina_aerolinea.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.15]}}>
			<EnMundo x={540} y={1700} alto={860} voltear={mira}>
				<Personaje diseno={OFICINISTA} ojos={duda ? 'mirandoLado' : 'normal'} cejas={duda ? 'preocupado' : 'neutral'} boca={duda ? 'mueca' : 'seria'} brazoIzq={elige ? 100 : 12} codoIzq={-15} />
			</EnMundo>
			<EnMundo x={170} y={1790} alto={880}>
				<Personaje diseno={VESNA} ojos="normal" cejas="neutral" boca="sonrisa" semilla={1} />
			</EnMundo>
			<EnMundo x={910} y={1790} alto={880}>
				<Personaje diseno={COMPANERA} ojos="feliz" cejas="arrogante" boca="sonrisa" semilla={4} />
			</EnMundo>
			<Etiqueta x={170} y={900} texto="VESNA" desde={d + 4} tam={54} />
			<Etiqueta x={910} y={900} texto="VESNA" desde={d + 8} tam={54} />
			<Icono tipo="interrogacion" x={540} y={700} desde={W.confusion} tam={190} />
		</Toma>
	);
};

const ErrorOficina: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="oficina_aerolinea.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.22, 1.3], x: [0, 20], y: [-40, -40]}} golpes={[[W.error, 0.05]]}>
		<EnMundo x={540} y={2150} alto={1550}>
			<Personaje diseno={OFICINISTA} ojos="feliz" cejas="preocupado" boca="mueca" brazoIzq={70} codoIzq={-60} brazoDer={70} codoDer={-60} />
		</EnMundo>
		<Documento x={750} y={600} ancho={320} desde={d + 2} rot={8} titulo="TRIPULACIÓN" />
		<Sello x={740} y={650} texto="ERROR" desde={W.error} tam={76} />
	</Toma>
);

/* ------------------------------ GIRO ------------------------------ */

const Minutos: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="avion_cielo.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.02, 1.14], x: [0, 30], y: [0, 40], curva: 'lineal'}}>
		<Cronometro x={720} y={1060} tam={400} desde={W.minutos} hasta={W.despues + 4} valor={46} />
	</Toma>
);

const Explota: React.FC<P> = ({d, h, e, s}) => (
	<Toma
		fondo="avion_cielo.jpg"
		desde={d}
		hasta={h}
		entrada={e}
		salida={s}
		cam={{s: [1.3, 1.4], x: [80, 80], y: [280, 280]}}
		sacudida={(g) => (g >= W.boom ? 26 * Math.exp(-(g - W.boom) / 8) : 0)}
		encima={<Destello desde={W.boom} color="#ffffff" fuerza={0.85} duracion={12} />}
	>
		<Explosion x={460} y={660} desde={W.boom} tam={900} />
		<Explosion x={300} y={600} desde={W.boom + 4} tam={600} />
		<Boom x={500} y={700} desde={W.boom} tam={600} />
	</Toma>
);

const Destrozo: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="restos_cielo.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.2], y: [0, 60]}} sacudida={(g) => 10 * Math.exp(-(g - d) / 20)}>
		<Explosion x={560} y={700} desde={W.explosion} tam={500} />
		<Escombros desde={d - 30} n={14} />
	</Toma>
);

const EnTres: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="cielo_alto.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.12], y: [-200, -200]}}>
		<AvionPartido x={540} y={900} ancho={1000} cortes={W.aeronave} parte={W.tres} />
		<Etiqueta x={230} y={760} texto="1" desde={W.tres + 2} tam={70} />
		<Etiqueta x={530} y={760} texto="2" desde={W.tres + 5} tam={70} />
		<Etiqueta x={850} y={720} texto="3" desde={W.tres + 8} tam={70} />
	</Toma>
);

const CaeConRestos: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma fondo="cielo_alto.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.2, 1.3], y: [60, -60]}} sacudida={temblor(5)}>
			<LineasViento intensidad={1.2} />
			<Escombros desde={d} n={8} subiendo />
			<ColaAvion x={700} y={620} ancho={720} rot={-20 + Math.sin(f / 12) * 8} />
			<EnMundo x={360 + Math.sin(f / 8) * 30} y={1500} alto={900} rot={Math.sin(f / 6) * 14}>
				<Personaje diseno={VESNA} ojos="grandes" cejas="sorprendido" boca="grito" brazoIzq={150} brazoDer={150} sombra={false} />
			</EnMundo>
		</Toma>
	);
};

/* ------------------------------ EL SECRETO ------------------------------ */

const Secreto: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="escenario.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.18], y: [-30, -30]}} golpes={[[W.sobrevivir, 0.06]]}>
		<EnMundo x={540} y={1780} alto={1060}>
			<Personaje diseno={VESNA} ojos="mirandoLado" cejas="arrogante" boca="picara" brazoIzq={60} codoIzq={-70} brazoDer={60} codoDer={-70} />
		</EnMundo>
		<Icono tipo="interrogacion" x={210} y={640} desde={d + 6} tam={200} rot={-14} />
		<Icono tipo="interrogacion" x={880} y={560} desde={d + 14} tam={230} rot={12} />
		<Icono tipo="interrogacion" x={540} y={340} desde={W.sobrevivir} tam={260} />
	</Toma>
);

const Atrapada: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="cola_interior.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.2], x: [0, 40], y: [0, 40]}}>
		<Nieve n={50} />
		<EnMundo x={360} y={1280} alto={700} rot={-12}>
			<Personaje diseno={VESNA} ojos="grandes" cejas="preocupado" boca="o" brazoIzq={60} brazoDer={100} codoDer={-20} />
		</EnMundo>
		<Carrito x={640} y={1290} ancho={320} rot={10} ojos="grandes" boca="o" />
	</Toma>
);

const CarritoHeroe: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const guino = f >= W.comida;
	return (
		<Toma fondo="cola_interior.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.4, 1.5], x: [-160, -160], y: [-240, -240]}} golpes={[[W.carrito, 0.06]]}>
			<Rayos x={640} y={1100} color="#fff2a8" opacidad={0.35} />
			<Carrito x={640} y={1420} ancho={470} ojos={guino ? 'guino' : 'normal'} boca={guino ? 'grande' : 'sonrisa'} />
			<Brillos x={640} y={1100} desde={W.carrito} radio={330} n={8} />
		</Toma>
	);
};

const Inventario: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="escenario.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.1]}}>
		<div style={{position: 'absolute', inset: 0, background: 'rgba(10,6,30,0.55)'}} />
		<FichaObjeto desde={W.carrito2 - 2} />
		<Carrito x={540} y={980} ancho={350} ojos="feliz" boca="grande" escala={1} />
	</Toma>
);

const Equipo: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	return (
		<Toma fondo="cielo_alto.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.15, 1.25], y: [-40, 40]}} sacudida={temblor(4)}>
			<LineasViento />
			<Rayos x={540} y={1000} color="#bfe6ff" opacidad={0.3} />
			<EnMundo x={380} y={1560} alto={900} rot={Math.sin(f / 6) * 8}>
				<Personaje diseno={VESNA} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoDer={95} codoDer={-10} brazoIzq={140} sombra={false} />
			</EnMundo>
			<Carrito x={740} y={1500} ancho={360} ojos="feliz" boca="grande" rot={Math.sin(f / 5) * 10} />
			<Brillos x={600} y={1150} desde={W.supervivencia} radio={380} n={9} />
		</Toma>
	);
};

const EmpleadoDelMes: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const aplauso = Math.floor(f / 3) % 2 === 0;
	return (
		<Toma fondo="ceremonia.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.08, 1.18], y: [-30, -30]}} golpes={[[W.empleado, 0.06]]}>
			<Cartel x={540} y={300} texto="EMPLEADO DEL MES" desde={W.empleado} tam={70} />
			<div style={{position: 'absolute', left: 540 - 230, top: 1060, width: 460, height: 150, background: '#d9a441', border: `10px solid ${TINTA}`, borderRadius: 14}} />
			<Carrito x={540} y={1075} ancho={440} ojos="feliz" boca="grande" medalla />
			<EnMundo x={190} y={1840} alto={900}>
				<Personaje diseno={VESNA} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={aplauso ? 45 : 75} codoIzq={aplauso ? -80 : -40} brazoDer={aplauso ? 45 : 75} codoDer={aplauso ? -80 : -40} />
			</EnMundo>
			<Confeti desde={W.empleado} />
		</Toma>
	);
};

/* ------------------------------ RESCATE ------------------------------ */

const BosqueNevado: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const impacto = W.nevado + 2;
	const p = interpolate(f, [d, impacto], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
	return (
		<Toma fondo="bosque_aereo.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.2]}} sacudida={(g) => (g >= impacto ? 18 * Math.exp(-(g - impacto) / 6) : 0)}>
			{f < impacto + 2 && <ColaAvion x={interpolate(p, [0, 1], [760, 540])} y={interpolate(p, [0, 1], [-300, 1000])} ancho={interpolate(p, [0, 1], [1100, 380])} rot={interpolate(p, [0, 1], [-30, 10])} />}
			<Puf x={540} y={1000} desde={impacto} tam={950} />
		</Toma>
	);
};

const Medico: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const llega = W.encontro + 4;
	const x = interpolate(f, [d, llega], [1300, 760], {...clamp, easing: Easing.out(Easing.cubic)});
	const ayuda = f >= W.auxiliarla - 2;
	return (
		<Toma fondo="bosque_restos.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.16], x: [20, -20]}}>
			<Nieve n={40} />
			<EnMundo x={x} y={1560} alto={920}>
				<Personaje diseno={MEDICO} caminando={f < llega - 2} ojos={ayuda ? 'feliz' : 'grandes'} cejas={ayuda ? 'arrogante' : 'sorprendido'} boca={ayuda ? 'sonrisa' : 'o'} brazoIzq={ayuda ? 70 : 20} codoIzq={-10} />
			</EnMundo>
			<EnMundo x={930} y={1740} alto={700} rot={-90}>
				<Personaje diseno={VESNA_SIN_GORRO} acc={{vendas: ayuda}} ojos={ayuda ? 'cerrados' : 'x'} cejas="preocupado" boca={ayuda ? 'sonrisa' : 'seria'} respira={ayuda} sombra={false} />
			</EnMundo>
			<Botiquin x={220} y={1520} desde={W.auxiliarla - 2} />
			<Icono tipo="exclamacion" x={x} y={640} desde={W.encontro} hasta={W.auxiliarla - 2} tam={170} />
			<Brillos x={420} y={1720} desde={W.auxiliarla} radio={260} />
		</Toma>
	);
};

/* ------------------------------ RECUPERACIÓN ------------------------------ */

const Coma: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="hospital.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.16]}}>
		<EnMundo x={820} y={1070} alto={700} rot={-90}>
			<Personaje diseno={VESNA_SIN_GORRO} acc={{vendas: true}} ojos="cerrados" cejas="neutral" boca="seria" sombra={false} />
		</EnMundo>
		<Zzz x={300} y={880} />
		<Monitor x={820} y={420} ancho={340} />
		<Calendario x={290} y={250} ancho={380} anios={[1, 7, 14, 21, 27]} cambios={[W.dias + 2, W.dias + 6, W.dias + 10, W.dias + 14]} />
	</Toma>
);

const Heridas: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="hospital.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.25, 1.35], y: [-60, -60]}} golpes={[[W.gravisimas, 0.05]]}>
		<EnMundo x={430} y={1840} alto={1040}>
			<Personaje diseno={VESNA_SIN_GORRO} acc={{vendas: true, momia: true}} ojos="cerrados" cejas="preocupado" boca="mueca" brazoIzq={30} brazoDer={30} respira={false} />
		</EnMundo>
		<EnMundo x={860} y={1860} alto={880}>
			<Personaje diseno={ENFERMERA} ojos="normal" cejas="preocupado" boca="o" semilla={2} />
		</EnMundo>
	</Toma>
);

const Camina: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const x = interpolate(f, [d, W.caminar + 6], [150, 470], {...clamp, easing: Easing.out(Easing.quad)});
	const aplauso = Math.floor(f / 3) % 2 === 0;
	return (
		<Toma fondo="rehabilitacion.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.14]}}>
			<EnMundo x={x} y={1830} alto={1000}>
				<Personaje diseno={VESNA_SIN_GORRO} acc={{vendas: true}} caminando={f < W.caminar + 6} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={95} brazoDer={95} />
			</EnMundo>
			<EnMundo x={880} y={1850} alto={880}>
				<Personaje diseno={ENFERMERA} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" semilla={2} brazoIzq={aplauso ? 45 : 75} codoIzq={aplauso ? -80 : -40} brazoDer={aplauso ? 45 : 75} codoDer={aplauso ? -80 : -40} />
			</EnMundo>
			<Brillos x={470} y={1000} desde={W.caminar} radio={360} />
		</Toma>
	);
};

const Record: React.FC<P> = ({d, h, e, s}) => (
	<Toma fondo="escenario.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.06, 1.14], y: [-40, -40]}} golpes={[[W.record, 0.05]]}>
		<Certificado x={540} y={220} ancho={800} desde={W.record - 2} />
		<EnMundo x={540} y={1830} alto={960}>
			<Personaje diseno={VESNA} acc={{medalla: true}} ojos="feliz" cejas="arrogante" boca="sonrisaGrande" brazoIzq={150} brazoDer={150} />
		</EnMundo>
		<Confeti desde={W.record} n={60} />
	</Toma>
);

/* ------------------------------ VEREDICTO Y CIERRE ------------------------------ */

const Veredicto: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const gana = f >= W.verdad;
	return (
		<Toma fondo="tribunal.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.05, 1.16]}} golpes={[[W.verdad, 0.08]]} encima={<Destello desde={W.verdad} color="#7dff9a" fuerza={0.5} duracion={12} />}>
			<Rayos x={540} y={700} opacidad={0.22} />
			<EnMundo x={210} y={1790} alto={860}>
				<Personaje diseno={MEDICO} ojos={gana ? 'feliz' : 'normal'} cejas="arrogante" boca={gana ? 'sonrisaGrande' : 'seria'} brazoIzq={gana ? 150 : 15} brazoDer={gana ? 150 : 15} />
			</EnMundo>
			<EnMundo x={540} y={1770} alto={900}>
				<Personaje diseno={VESNA} acc={{medalla: true}} ojos={gana ? 'feliz' : 'normal'} cejas="arrogante" boca={gana ? 'sonrisaGrande' : 'sonrisa'} brazoIzq={gana ? 150 : 15} brazoDer={gana ? 150 : 15} />
			</EnMundo>
			<Carrito x={870} y={1790} ancho={330} ojos={gana ? 'feliz' : 'normal'} boca={gana ? 'grande' : 'sonrisa'} medalla />
			<Sello x={540} y={560} texto="VERDAD" icono="✔" color="#1f9d48" desde={W.verdad} tam={118} rot={-8} />
			<Confeti desde={W.verdad + 2} n={50} />
		</Toma>
	);
};

const Masaje: React.FC<P> = ({d, h, e, s}) => {
	const f = useCurrentFrame();
	const turbulencia = f >= W.turbulencias - 4;
	return (
		<Toma fondo="cabina.jpg" desde={d} hasta={h} entrada={e} salida={s} cam={{s: [1.1, 1.22], r: turbulencia ? [-3, 3] : [0, 0]}} sacudida={(g) => (g >= W.turbulencias - 4 ? 16 : 0)}>
			<EnMundo x={540} y={1830} alto={1080} rot={turbulencia ? Math.sin(f * 1.3) * 4 : 0}>
				<Personaje diseno={VESNA} acc={{pepinos: true, toalla: true}} ojos="cerrados" cejas="arrogante" boca={f >= W.masaje ? 'sonrisaGrande' : 'sonrisa'} brazoIzq={40} codoIzq={-95} brazoDer={40} codoDer={-95} />
			</EnMundo>
			<Bocadillo x={760} y={560} texto="¡Ahhh!" desde={W.turbulencias + 4} hasta={W.masaje + 2} cola="izq" ancho={380} />
			<Bocadillo x={660} y={560} texto="¡Más fuerte!" desde={W.masaje + 2} cola="izq" ancho={520} tam={64} />
			<Fundido desde={h - 14} duracion={14} />
		</Toma>
	);
};

/* ------------------------------ Montaje ------------------------------ */

type Plano = {desde: number; Comp: React.FC<P>; entrada: Transicion};

const PLANOS: Plano[] = [
	{desde: 0, Comp: Caida, entrada: 'corte'},
	{desde: antes(W.diezmil), Comp: Altura, entrada: 'latigoArriba'},
	{desde: antes(W.sin), Comp: SinParacaidas, entrada: 'zoom'},
	{desde: antes(palabra(2, 'Y')), Comp: Sobrevivio, entrada: 'latigoArriba'},
	{desde: antes(palabra(3, 'Básicamente')), Comp: PeorVuelo, entrada: 'latigoDer'},
	{desde: antes(palabra(4, 'pero')), Comp: MejorAterrizaje, entrada: 'latigoIzq'},
	{desde: antes(palabra(5, 'Se')), Comp: SeLlamaba, entrada: 'latigoDer'},
	{desde: antes(palabra(6, 'Tenía')), Comp: Azafata, entrada: 'latigoIzq'},
	{desde: antes(palabra(7, 'Terminó')), Comp: Confusion, entrada: 'latigoDer'},
	{desde: antes(palabra(8, 'Sí')), Comp: ErrorOficina, entrada: 'zoom'},
	{desde: antes(palabra(9, 'Pero')), Comp: Minutos, entrada: 'latigoArriba'},
	{desde: antes(W.boom), Comp: Explota, entrada: 'corte'},
	{desde: antes(palabra(11, 'Una')), Comp: Destrozo, entrada: 'zoom'},
	{desde: antes(palabra(12, 'La')), Comp: EnTres, entrada: 'latigoDer'},
	{desde: antes(palabra(13, 'Y')), Comp: CaeConRestos, entrada: 'latigoArriba'},
	{desde: antes(palabra(14, 'Su')), Comp: Secreto, entrada: 'latigoIzq'},
	{desde: antes(palabra(15, 'Quedó')), Comp: Atrapada, entrada: 'latigoDer'},
	{desde: antes(palabra(16, 'junto')), Comp: CarritoHeroe, entrada: 'zoom'},
	{desde: antes(palabra(17, 'Sí')), Comp: Inventario, entrada: 'latigoIzq'},
	{desde: antes(palabra(17, 'parte')), Comp: Equipo, entrada: 'latigoArriba'},
	{desde: antes(W.empleado), Comp: EmpleadoDelMes, entrada: 'zoom'},
	{desde: antes(palabra(19, 'Los')), Comp: BosqueNevado, entrada: 'latigoArriba'},
	{desde: antes(palabra(20, 'Un')), Comp: Medico, entrada: 'latigoDer'},
	{desde: antes(palabra(21, 'Vesna')), Comp: Coma, entrada: 'latigoIzq'},
	{desde: antes(palabra(22, 'Sufrió')), Comp: Heridas, entrada: 'zoom'},
	{desde: antes(palabra(23, 'pero')), Comp: Camina, entrada: 'latigoDer'},
	{desde: antes(palabra(24, 'Y')), Comp: Record, entrada: 'latigoArriba'},
	{desde: antes(palabra(25, 'VEREDICTO')), Comp: Veredicto, entrada: 'latigoIzq'},
	{desde: antes(palabra(26, 'Después')), Comp: Masaje, entrada: 'latigoDer'},
];

export const Historia: React.FC = () => (
	<>
		{PLANOS.map((p, i) => {
			const sig = PLANOS[i + 1];
			return <p.Comp key={i} d={p.desde} h={sig ? sig.desde : FIN_VIDEO} e={p.entrada} s={sig ? sig.entrada : 'corte'} />;
		})}
	</>
);

/** Efectos de sonido: [archivo, cuadro, volumen] */
export const SONIDOS: [string, number, number][] = [
	...PLANOS.filter((p) => p.entrada !== 'corte').map((p) => ['whoosh', p.desde - 5, 0.45] as [string, number, number]),
	['viento', 0, 0.5],
	['viento', 80, 0.4],
	['pop', W.diezmil, 0.45],
	['dundun', W.paracaidas - 2, 0.45],
	['ding', W.sobrevivio, 0.45],
	['viento', palabra(3, 'Básicamente') - 3, 0.3],
	['pop', W.peor, 0.45],
	['pop', W.aterrizaje, 0.4],
	['pop', W.aterrizaje + 5, 0.4],
	['pop', W.aterrizaje + 10, 0.4],
	['aplausos', W.historia - 4, 0.45],
	['pop', W.vesna - 2, 0.45],
	['pop', W.anios, 0.4],
	['ding', W.azafata, 0.3],
	['pop', W.confusion, 0.4],
	['sello', W.error, 0.6],
	...Array.from({length: 11}).map((_, i) => ['tic', W.minutos + i * 4, 0.35] as [string, number, number]),
	['boom', W.boom - 1, 0.65],
	['boom', W.explosion, 0.3],
	['viento', palabra(11, 'Una') - 3, 0.35],
	['pop', W.tres + 2, 0.4],
	['pop', W.tres + 5, 0.4],
	['pop', W.tres + 8, 0.4],
	['viento', palabra(13, 'Y') - 3, 0.5],
	['pop', W.sobrevivir, 0.4],
	['ding', W.carrito, 0.4],
	['pop', W.comida, 0.45],
	['objeto', W.carrito2 - 2, 0.55],
	['viento', palabra(17, 'parte') - 3, 0.35],
	['ding', W.supervivencia, 0.35],
	['aplausos', W.empleado - 2, 0.55],
	['ding', W.empleado, 0.4],
	['viento', palabra(19, 'Los') - 3, 0.3],
	['boom', W.nevado + 1, 0.4],
	['pop', W.encontro, 0.4],
	['ding', W.auxiliarla, 0.35],
	...Array.from({length: 4}).map((_, i) => ['beep', palabra(21, 'Vesna') + i * 20, 0.3] as [string, number, number]),
	['hoja', W.dias + 2, 0.4],
	['hoja', W.dias + 6, 0.4],
	['hoja', W.dias + 10, 0.4],
	['sello', W.dias + 14, 0.5],
	['dundun', W.gravisimas, 0.3],
	['aplausos', W.caminar - 2, 0.45],
	['ding', W.caminar, 0.35],
	['ding', W.record, 0.45],
	['aplausos', W.record, 0.5],
	['sello', W.verdad, 0.75],
	['ding', W.verdad + 1, 0.45],
	['pop', W.turbulencias + 4, 0.4],
	['pop', W.masaje + 2, 0.45],
];
