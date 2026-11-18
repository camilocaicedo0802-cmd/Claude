import React from 'react';
import {random, useCurrentFrame} from 'remotion';
import {TITULAR} from '../fuentes';

/* Fondos ilustrados por código (SVG 1080x1920) para el short de Napoleón. */

const LINEA = '#2a2433';
const ORO = '#e0b23a';
const ORO_S = '#b7861f';

const Lienzo: React.FC<{children: React.ReactNode}> = ({children}) => (
	<svg viewBox="0 0 1080 1920" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" style={{position: 'absolute', inset: 0}}>
		{children}
	</svg>
);

const useId = (base: string) => `${base}-${React.useId().replace(/:/g, '')}`;

const Degradado: React.FC<{id: string; colores: [string, number][]}> = ({id, colores}) => (
	<linearGradient id={id} x1={0} y1={0} x2={0} y2={1}>
		{colores.map(([c, o]) => (
			<stop key={o} offset={o} stopColor={c} />
		))}
	</linearGradient>
);

const Nube: React.FC<{x: number; y: number; s?: number; color?: string}> = ({x, y, s = 1, color = '#ffffff'}) => (
	<g transform={`translate(${x} ${y}) scale(${s})`}>
		<circle cx={-90} cy={10} r={62} fill={color} />
		<circle cx={0} cy={-20} r={86} fill={color} />
		<circle cx={95} cy={8} r={66} fill={color} />
		<ellipse cx={0} cy={36} rx={180} ry={40} fill={color} />
	</g>
);

/* ---------- Tabla de estaturas (como una rueda de reconocimiento) ---------- */

/** Suelo de la tabla y escala: 1 cm = 4,6 px. La coronilla de alguien de h cm queda en PISO - h*7. */
export const PISO = 1760;
export const PX_CM = 5.6;
export const yDeCm = (cm: number) => PISO - cm * PX_CM;
/** Alto del lienzo de un Muñeco (Actor) para que su coronilla marque `cm`. */
export const altoParaCm = (cm: number) => (cm * PX_CM) / (870 / 900);

export const EscMedidas: React.FC<{color?: string}> = ({color = '#2f4f74'}) => {
	const id = useId('pared');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[[color, 0], ['#1d3150', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{Array.from({length: 281}).map((_, i) => {
				const cm = 20 + i;
				const y = yDeCm(cm);
				const fuerte = cm % 10 === 0;
				const medio = cm % 5 === 0;
				return (
					<g key={cm}>
						<line x1={0} y1={y} x2={1080} y2={y} stroke="#ffffff" strokeWidth={fuerte ? 4 : medio ? 2.5 : 1} opacity={fuerte ? 0.55 : medio ? 0.35 : 0.15} />
						{fuerte && (
							<text x={24} y={y + 12} fontFamily={TITULAR} fontWeight={900} fontSize={34} fill="#ffffff" opacity={0.85}>
								{`${(cm / 100).toFixed(2).replace('.', ',')}`}
							</text>
						)}
						{fuerte && (
							<text x={1056} y={y + 12} textAnchor="end" fontFamily={TITULAR} fontWeight={900} fontSize={34} fill="#ffffff" opacity={0.85}>
								{`${(cm / 100).toFixed(2).replace('.', ',')}`}
							</text>
						)}
					</g>
				);
			})}
			<rect x={0} y={PISO} width={1080} height={200} fill="#8a6a4a" />
			<rect x={0} y={PISO + 60} width={1080} height={4} fill="#6e5236" opacity={0.6} />
			<rect x={0} y={PISO} width={1080} height={14} fill="#5e452c" />
		</Lienzo>
	);
};

/* ---------- Estudio del caricaturista en Londres ---------- */

export const EscEstudio: React.FC = () => {
	const f = useCurrentFrame();
	const id = useId('estudio');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#7a5232', 0], ['#4a2f1a', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{Array.from({length: 9}).map((_, i) => (
				<line key={i} x1={i * 130} y1={0} x2={i * 130} y2={1300} stroke="#5e3f24" strokeWidth={6} />
			))}
			{/* ventana con Londres neblinoso */}
			<rect x={300} y={180} width={480} height={560} fill="#b9c4cc" stroke={LINEA} strokeWidth={10} />
			<path d="M 300 560 L 360 520 L 400 560 L 440 470 L 480 560 L 520 520 L 560 560 L 780 560 L 780 740 L 300 740 Z" fill="#7d8894" />
			<g transform="translate(600 540)">
				<path d="M -70 0 A 70 70 0 0 1 70 0 Z" fill="#6b7682" />
				<rect x={-90} y={0} width={180} height={200} fill="#6b7682" />
				<rect x={-8} y={-110} width={16} height={50} fill="#6b7682" />
			</g>
			<rect x={300} y={180} width={480} height={560} fill="rgba(230,235,240,0.35)" />
			<line x1={540} y1={180} x2={540} y2={740} stroke={LINEA} strokeWidth={8} />
			<line x1={300} y1={460} x2={780} y2={460} stroke={LINEA} strokeWidth={8} />
			{/* dibujos clavados en la pared */}
			{[
				[110, 330, -6],
				[950, 300, 5],
				[140, 820, 4],
				[930, 800, -4],
			].map(([x, y, r], i) => (
				<g key={i} transform={`translate(${x} ${y}) rotate(${r})`}>
					<rect x={-90} y={-110} width={180} height={220} fill="#f4ead2" stroke={LINEA} strokeWidth={4} />
					<circle cx={0} cy={-30} r={34} fill="none" stroke={LINEA} strokeWidth={4} />
					<path d="M -40 70 Q 0 20 40 70 M -30 -64 L 30 -64 L 0 -100 Z" stroke={LINEA} strokeWidth={4} fill="none" />
					<circle cx={0} cy={-100} r={7} fill="#e3262e" />
				</g>
			))}
			{/* escritorio */}
			<rect x={0} y={1320} width={1080} height={600} fill="#8a5a32" />
			<rect x={0} y={1300} width={1080} height={40} fill="#a06a3c" stroke={LINEA} strokeWidth={6} />
			<g transform="translate(860 1290)">
				<path d="M -40 0 L -34 -70 L 34 -70 L 40 0 Z" fill="#20202a" stroke={LINEA} strokeWidth={5} />
				<path d="M 0 -60 Q 60 -190 120 -260 Q 50 -160 10 -64" fill="#f6f2e8" stroke={LINEA} strokeWidth={4} />
			</g>
			<g transform="translate(160 1290)">
				<rect x={-26} y={-100} width={52} height={100} rx={6} fill="#f6eedd" stroke={LINEA} strokeWidth={5} />
				<path d={`M 0 -100 Q ${14 + Math.sin(f / 3) * 5} -146 ${Math.sin(f / 2) * 5} -176 Q -12 -140 0 -100 Z`} fill="#ffb02e" />
				<circle cx={0} cy={-140} r={150} fill="rgba(255,190,80,0.12)" />
			</g>
		</Lienzo>
	);
};

/* ---------- Salón imperial ---------- */

export const EscPalacio: React.FC = () => {
	const id = useId('salon');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#1f3f8a', 0], ['#162c63', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1300} fill={`url(#${id})`} />
			{/* abejas doradas (símbolo napoleónico) */}
			{Array.from({length: 48}).map((_, i) => {
				const x = 70 + (i % 8) * 135 + (Math.floor(i / 8) % 2) * 67;
				const y = 120 + Math.floor(i / 8) * 190;
				return (
					<g key={i} transform={`translate(${x} ${y})`} opacity={0.55}>
						<ellipse cx={0} cy={0} rx={9} ry={14} fill={ORO} />
						<ellipse cx={-11} cy={-6} rx={9} ry={6} fill={ORO} />
						<ellipse cx={11} cy={-6} rx={9} ry={6} fill={ORO} />
					</g>
				);
			})}
			{/* emblema: N con laureles */}
			<g transform="translate(540 330)">
				<circle cx={0} cy={0} r={150} fill="#163070" stroke={ORO} strokeWidth={14} />
				<text x={0} y={70} textAnchor="middle" fontFamily="Georgia, serif" fontWeight={900} fontSize={210} fill={ORO} stroke={LINEA} strokeWidth={4}>
					N
				</text>
				{[-1, 1].map((l) =>
					Array.from({length: 6}).map((_, i) => {
						const a = (200 + i * 22) * (Math.PI / 180);
						const cx = Math.cos(a) * 175 * -l;
						const cy = -Math.sin(a) * 175;
						return <ellipse key={`${l}${i}`} cx={cx} cy={cy} rx={26} ry={12} fill="#6fb64a" stroke={LINEA} strokeWidth={3} transform={`rotate(${l * (i * 22 + 20)} ${cx} ${cy})`} />;
					}),
				)}
			</g>
			{/* columnas */}
			{[60, 940].map((x) => (
				<g key={x}>
					<rect x={x} y={80} width={80} height={1220} fill="#f1e6cf" stroke={LINEA} strokeWidth={4} />
					<rect x={x + 50} y={80} width={30} height={1220} fill="#d8c8a6" />
					<rect x={x - 14} y={60} width={108} height={36} fill={ORO} stroke={LINEA} strokeWidth={4} />
				</g>
			))}
			{/* trono */}
			<g transform="translate(540 1300)">
				<rect x={-150} y={-420} width={300} height={420} rx={30} fill="#b0182a" stroke={LINEA} strokeWidth={6} />
				<rect x={-120} y={-390} width={240} height={300} rx={20} fill="#d42a3c" />
				<rect x={-170} y={-130} width={340} height={60} rx={14} fill={ORO} stroke={LINEA} strokeWidth={5} />
				<circle cx={-150} cy={-420} r={26} fill={ORO} stroke={LINEA} strokeWidth={4} />
				<circle cx={150} cy={-420} r={26} fill={ORO} stroke={LINEA} strokeWidth={4} />
			</g>
			{/* suelo y alfombra */}
			<rect x={0} y={1300} width={1080} height={620} fill="#c9a77a" />
			{Array.from({length: 7}).map((_, i) => (
				<line key={i} x1={0} y1={1320 + i * i * 14} x2={1080} y2={1320 + i * i * 14} stroke="#b08e60" strokeWidth={4} />
			))}
			<path d="M 440 1300 L 640 1300 L 860 1920 L 220 1920 Z" fill="#b0182a" />
			<path d="M 460 1300 L 470 1300 L 260 1920 L 240 1920 Z M 620 1300 L 610 1300 L 820 1920 L 840 1920 Z" fill={ORO} />
		</Lienzo>
	);
};

/* ---------- Mapa de Europa (estilizado) ---------- */

export const CIUDADES: Record<string, [number, number]> = {
	LONDRES: [350, 640],
	PARÍS: [430, 820],
	MADRID: [240, 1180],
	BERLÍN: [700, 640],
	VIENA: [780, 850],
	ROMA: [660, 1110],
};

export const EscMapa: React.FC<{ciudades?: string[]; resaltar?: string[]; nombres?: Record<string, string>}> = ({ciudades, resaltar = ['LONDRES'], nombres = {}}) => {
	const f = useCurrentFrame();
	return (
		<Lienzo>
			<rect x={0} y={0} width={1080} height={1920} fill="#9ed6e6" />
			{Array.from({length: 30}).map((_, i) => (
				<path key={i} d={`M ${(random(`m${i}`) * 1200 + f) % 1200 - 60} ${random(`n${i}`) * 1920} q 20 -10 40 0`} stroke="rgba(255,255,255,0.6)" strokeWidth={4} fill="none" />
			))}
			{/* Gran Bretaña */}
			<path d="M 300 360 L 360 330 L 400 420 L 380 520 L 430 600 L 400 680 L 300 700 L 270 640 L 320 560 L 280 470 Z" fill="#e9dcb8" stroke={LINEA} strokeWidth={5} strokeLinejoin="round" />
			{/* continente */}
			<path
				d="M 1080 380 L 860 420 L 760 480 L 640 520 L 560 600 L 480 690 L 420 720 L 380 800 L 330 880 L 300 960 L 160 1000 L 120 1080 L 140 1260 L 260 1340 L 420 1300 L 470 1180 L 560 1120 L 600 1080 L 640 1160 L 700 1300 L 760 1360 L 780 1290 L 720 1180 L 680 1080 L 760 1030 L 860 1080 L 920 1200 L 980 1240 L 1080 1200 Z"
				fill="#e9dcb8"
				stroke={LINEA}
				strokeWidth={5}
				strokeLinejoin="round"
			/>
			<path d="M 160 1000 L 300 960 L 330 880 L 380 800 L 420 720 L 480 690 L 520 760 L 470 900 L 420 1000 L 300 1060 Z" fill="#d6e4b6" opacity={0.6} />
			{Object.entries(CIUDADES).filter(([n]) => !ciudades || ciudades.includes(n)).map(([n, [x, y]]) => (
				<g key={n}>
					<circle cx={x} cy={y} r={resaltar.includes(n) ? 18 : 14} fill={resaltar.includes(n) ? '#e3262e' : LINEA} stroke="#ffffff" strokeWidth={4} />
					<text x={x} y={y - 30} textAnchor="middle" fontFamily={TITULAR} fontWeight={900} fontSize={resaltar.includes(n) ? 46 : 36} fill={LINEA}>
						{nombres[n] ?? n}
					</text>
				</g>
			))}
		</Lienzo>
	);
};

/* ---------- Santa Helena, 1821 ---------- */

export const EscSantaHelena: React.FC = () => {
	const f = useCurrentFrame();
	const id = useId('cuarto');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#e7dcc4', 0], ['#cbbb98', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			<rect x={330} y={200} width={420} height={520} fill="#7fc6e0" stroke={LINEA} strokeWidth={10} />
			<rect x={330} y={520} width={420} height={200} fill="#2f7fb0" />
			<path d="M 520 520 L 560 420 L 640 400 L 700 460 L 740 520 Z" fill="#6f8a5a" stroke={LINEA} strokeWidth={4} />
			{Array.from({length: 6}).map((_, i) => (
				<path key={i} d={`M ${350 + ((i * 70 + f) % 400)} ${560 + i * 24} q 14 -8 28 0`} stroke="rgba(255,255,255,0.7)" strokeWidth={4} fill="none" />
			))}
			<line x1={540} y1={200} x2={540} y2={720} stroke={LINEA} strokeWidth={8} />
			<rect x={300} y={720} width={480} height={30} fill="#a07a50" stroke={LINEA} strokeWidth={5} />
			<rect x={0} y={1350} width={1080} height={570} fill="#9a7b54" />
			{Array.from({length: 6}).map((_, i) => (
				<line key={i} x1={0} y1={1380 + i * i * 16} x2={1080} y2={1380 + i * i * 16} stroke="#86683f" strokeWidth={4} />
			))}
			{/* mesa con el cuerpo cubierto (caricaturesco) */}
			<rect x={130} y={1150} width={820} height={60} rx={10} fill="#8a5a32" stroke={LINEA} strokeWidth={6} />
			<rect x={170} y={1210} width={30} height={200} fill="#6b4422" stroke={LINEA} strokeWidth={4} />
			<rect x={880} y={1210} width={30} height={200} fill="#6b4422" stroke={LINEA} strokeWidth={4} />
			<path d="M 150 1150 Q 200 1040 330 1060 Q 500 1010 700 1050 Q 860 1030 930 1150 Z" fill="#f6f6f2" stroke={LINEA} strokeWidth={6} />
			{/* bicornio sobre la sábana */}
			<g transform="translate(520 1020) scale(0.55)">
				<path d="M 20 110 Q 60 -20 200 -10 Q 340 -20 380 110 Q 300 70 200 74 Q 100 70 20 110 Z" fill="#141418" stroke={LINEA} strokeWidth={9} transform="translate(-200 -60)" />
			</g>
		</Lienzo>
	);
};

/* ---------- Pizarra ---------- */

export const EscPizarra: React.FC = () => (
	<Lienzo>
		<rect x={0} y={0} width={1080} height={1920} fill="#c9a77a" />
		<rect x={40} y={180} width={1000} height={1300} rx={20} fill="#8a5a32" stroke={LINEA} strokeWidth={8} />
		<rect x={80} y={220} width={920} height={1220} fill="#2f5d4a" />
		<rect x={60} y={1480} width={960} height={36} fill="#a06a3c" stroke={LINEA} strokeWidth={6} />
		<rect x={200} y={1460} width={70} height={22} rx={6} fill="#ffffff" />
	</Lienzo>
);

/* ---------- Campo de desfile de la Guardia ---------- */

export const EscDesfile: React.FC = () => {
	const f = useCurrentFrame();
	const id = useId('cielo');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#5ec8ff', 0], ['#bfe9ff', 0.7], ['#fff4cf', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1100} fill={`url(#${id})`} />
			<Nube x={260} y={260} s={0.9} />
			<Nube x={820} y={380} s={0.7} />
			<path d="M 0 980 Q 270 920 540 960 T 1080 940 L 1080 1100 L 0 1100 Z" fill="#7cb862" />
			{/* tiendas de campaña */}
			{[140, 320, 760, 940].map((x) => (
				<path key={x} d={`M ${x - 80} 1020 L ${x} 900 L ${x + 80} 1020 Z`} fill="#f4ead2" stroke={LINEA} strokeWidth={4} />
			))}
			{/* banderas tricolores */}
			{[460, 620].map((x, i) => (
				<g key={x}>
					<line x1={x} y1={1000} x2={x} y2={700} stroke={LINEA} strokeWidth={8} />
					<g transform={`translate(${x} 700) skewY(${Math.sin(f / 8 + i) * 4})`}>
						<rect x={0} y={0} width={60} height={110} fill="#1f3a7a" />
						<rect x={60} y={0} width={60} height={110} fill="#ffffff" />
						<rect x={120} y={0} width={60} height={110} fill="#e3262e" />
					</g>
				</g>
			))}
			<rect x={0} y={1080} width={1080} height={840} fill="#c9a86a" />
			{Array.from({length: 8}).map((_, i) => (
				<line key={i} x1={0} y1={1100 + i * i * 14} x2={1080} y2={1100 + i * i * 14} stroke="#b39257" strokeWidth={4} />
			))}
		</Lienzo>
	);
};

/* ---------- Celular con "el primer meme de la historia" ---------- */

/** Zona de la imagen del meme dentro de la pantalla. */
export const MEME = {x: 210, y: 470, w: 660, h: 760};

export const EscCelular: React.FC<{reacciones?: number}> = ({reacciones = 0}) => {
	const f = useCurrentFrame();
	const id = useId('fondo');
	const likes = Math.round(1200 + reacciones * 98000);
	return (
		<Lienzo>
			<defs>
				<linearGradient id={id} x1={0} y1={0} x2={1} y2={1}>
					<stop offset={0} stopColor="#7b3fe4" />
					<stop offset={1} stopColor="#ff5f8f" />
				</linearGradient>
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{Array.from({length: 14}).map((_, i) => (
				<circle key={i} cx={random(`c${i}`) * 1080} cy={(random(`d${i}`) * 1920 - f * 2) % 1920} r={8 + random(`r${i}`) * 14} fill="rgba(255,255,255,0.18)" />
			))}
			{/* teléfono */}
			<rect x={160} y={240} width={760} height={1480} rx={70} fill="#16161c" stroke={LINEA} strokeWidth={10} />
			<rect x={190} y={300} width={700} height={1370} rx={40} fill="#ffffff" />
			<rect x={470} y={262} width={140} height={22} rx={11} fill="#2c2c34" />
			{/* cabecera de la publicación */}
			<circle cx={260} cy={390} r={40} fill="#e0b23a" stroke={LINEA} strokeWidth={4} />
			<text x={320} y={384} fontFamily={TITULAR} fontWeight={900} fontSize={36} fill="#16161c">
				memes_de_1803
			</text>
			<text x={320} y={424} fontFamily={TITULAR} fontWeight={700} fontSize={26} fill="#8a8a96">
				Londres · hace 220 años
			</text>
			{/* imagen del meme (fondo papel) */}
			<rect x={MEME.x} y={MEME.y} width={MEME.w} height={MEME.h} fill="#f4ead2" stroke="#d8cfb8" strokeWidth={4} />
			{/* barra de reacciones */}
			<text x={220} y={1310} fontFamily={TITULAR} fontWeight={900} fontSize={48}>
				❤️ 😂 🔁
			</text>
			<text x={220} y={1380} fontFamily={TITULAR} fontWeight={900} fontSize={36} fill="#16161c">
				{`${likes.toLocaleString('es-ES')} me gusta`}
			</text>
			<text x={220} y={1440} fontFamily={TITULAR} fontWeight={700} fontSize={30} fill="#3a3a44">
				<tspan fontWeight={900}>memes_de_1803 </tspan>cuando eres emperador
			</text>
			<text x={220} y={1482} fontFamily={TITULAR} fontWeight={700} fontSize={30} fill="#3a3a44">
				pero mides 1,57 😂😂 #LittleBoney
			</text>
		</Lienzo>
	);
};

/* ---------- Escenario con foco (veredicto), como el pedestal del video de referencia ---------- */

export const EscEscenario: React.FC = () => {
	const f = useCurrentFrame();
	const id = useId('esc');
	const foco = useId('foco');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#1a2550', 0], ['#0d1430', 1]]} />
				<linearGradient id={foco} x1={0} y1={0} x2={0} y2={1}>
					<stop offset={0} stopColor="#fff6c8" stopOpacity={0.85} />
					<stop offset={1} stopColor="#fff6c8" stopOpacity={0.12} />
				</linearGradient>
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{Array.from({length: 40}).map((_, i) => (
				<circle key={i} cx={random(`e${i}`) * 1080} cy={random(`ey${i}`) * 1300} r={2 + random(`er${i}`) * 4} fill="#ffffff" opacity={0.25 + 0.25 * Math.sin(f / 6 + i)} />
			))}
			{/* telones */}
			{[-1, 1].map((l) => (
				<g key={l}>
					<path d={l < 0 ? 'M 0 0 L 230 0 Q 170 600 210 1500 L 0 1500 Z' : 'M 1080 0 L 850 0 Q 910 600 870 1500 L 1080 1500 Z'} fill="#8a1424" stroke={LINEA} strokeWidth={6} />
					{[0, 1, 2, 3].map((k) => (
						<path key={k} d={l < 0 ? `M ${40 + k * 48} 0 Q ${20 + k * 44} 700 ${40 + k * 46} 1500` : `M ${1040 - k * 48} 0 Q ${1060 - k * 44} 700 ${1040 - k * 46} 1500`} stroke="#5e0c18" strokeWidth={10} fill="none" />
					))}
				</g>
			))}
			<path d="M 0 0 L 1080 0 L 1080 120 Q 540 190 0 120 Z" fill="#a51c2e" stroke={LINEA} strokeWidth={6} />
			{/* foco */}
			<path d="M 470 0 L 610 0 L 900 1560 L 180 1560 Z" fill={`url(#${foco})`} />
			{/* suelo */}
			<rect x={0} y={1500} width={1080} height={420} fill="#3a2414" />
			<ellipse cx={540} cy={1560} rx={380} ry={60} fill="#fff6c8" opacity={0.35} />
			{Array.from({length: 5}).map((_, i) => (
				<line key={i} x1={0} y1={1520 + i * i * 22} x2={1080} y2={1520 + i * i * 22} stroke="#2a1a0e" strokeWidth={5} />
			))}
		</Lienzo>
	);
};

/* =================== María Antonieta =================== */

const Arana: React.FC<{x: number; y: number; s?: number}> = ({x, y, s = 1}) => {
	const f = useCurrentFrame();
	return (
		<g transform={`translate(${x} ${y}) scale(${s})`}>
			<line x1={0} y1={-400} x2={0} y2={-40} stroke={ORO_S} strokeWidth={6} />
			<circle cx={0} cy={60} r={170} fill="#fff3c4" opacity={0.18 + 0.04 * Math.sin(f / 6)} />
			<path d="M -120 0 Q 0 70 120 0 L 90 60 Q 0 110 -90 60 Z" fill={ORO} stroke={LINEA} strokeWidth={5} strokeLinejoin="round" />
			{[-100, -50, 0, 50, 100].map((dx) => (
				<g key={dx}>
					<rect x={dx - 6} y={-34} width={12} height={34} fill="#fffaf0" stroke={LINEA} strokeWidth={3} />
					<path d={`M ${dx} -36 q 8 -14 0 -26 q -8 12 0 26`} fill="#ffb02e" />
				</g>
			))}
			{[-80, -40, 0, 40, 80].map((dx, i) => (
				<path key={dx} d={`M ${dx} ${70 + (i % 2) * 14} l -9 22 l 9 16 l 9 -16 Z`} fill="#dff4ff" stroke={LINEA} strokeWidth={3} />
			))}
		</g>
	);
};

/** Galería de los Espejos de Versalles */
export const EscVersalles: React.FC<{tono?: 'oro' | 'noche'}> = ({tono = 'oro'}) => {
	const pared = useId('vpared');
	const espejo = useId('vesp');
	const noche = tono === 'noche';
	return (
		<Lienzo>
			<defs>
				<Degradado id={pared} colores={noche ? [['#5a4a3a', 0], ['#2e241a', 1]] : [['#f6e2b0', 0], ['#e1bf78', 1]]} />
				<linearGradient id={espejo} x1={0} y1={0} x2={1} y2={1}>
					<stop offset={0} stopColor={noche ? '#56657a' : '#c9e2ee'} />
					<stop offset={0.5} stopColor={noche ? '#3b4658' : '#9cc3d6'} />
					<stop offset={1} stopColor={noche ? '#56657a' : '#d8ecf4'} />
				</linearGradient>
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${pared})`} />
			{/* bóveda pintada */}
			<rect x={0} y={0} width={1080} height={230} fill={noche ? '#3a2e22' : '#c99a45'} />
			{[0, 1, 2, 3].map((i) => (
				<ellipse key={i} cx={135 + i * 270} cy={110} rx={110} ry={70} fill={noche ? '#4b5a78' : '#9ccbe6'} stroke={ORO} strokeWidth={10} />
			))}
			<rect x={0} y={222} width={1080} height={26} fill={ORO} stroke={LINEA} strokeWidth={4} />
			{/* espejos en arco y pilastras */}
			{[180, 540, 900].map((cx) => (
				<g key={cx}>
					<path d={`M ${cx - 135} 1270 L ${cx - 135} 470 A 135 135 0 0 1 ${cx + 135} 470 L ${cx + 135} 1270 Z`} fill={ORO} stroke={LINEA} strokeWidth={6} />
					<path d={`M ${cx - 112} 1250 L ${cx - 112} 474 A 112 112 0 0 1 ${cx + 112} 474 L ${cx + 112} 1250 Z`} fill={`url(#${espejo})`} />
					{[560, 760, 960, 1160].map((y) => (
						<line key={y} x1={cx - 112} y1={y} x2={cx + 112} y2={y} stroke={ORO_S} strokeWidth={5} />
					))}
					<line x1={cx} y1={360} x2={cx} y2={1250} stroke={ORO_S} strokeWidth={5} />
					<path d={`M ${cx - 80} 620 L ${cx - 20} 520 M ${cx - 60} 900 L ${cx + 10} 790`} stroke="#ffffff" strokeWidth={10} opacity={0.35} strokeLinecap="round" />
				</g>
			))}
			{[360, 720].map((x) => (
				<g key={x}>
					<rect x={x - 36} y={250} width={72} height={1030} fill={noche ? '#5e4a52' : '#d9a7a0'} stroke={LINEA} strokeWidth={5} />
					<rect x={x - 46} y={250} width={92} height={40} fill={ORO} stroke={LINEA} strokeWidth={4} />
					<rect x={x - 46} y={1240} width={92} height={40} fill={ORO} stroke={LINEA} strokeWidth={4} />
				</g>
			))}
			<Arana x={360} y={420} s={0.8} />
			<Arana x={720} y={420} s={0.8} />
			{/* parqué */}
			<rect x={0} y={1280} width={1080} height={640} fill={noche ? '#5a3a20' : '#b07a42'} />
			{Array.from({length: 14}).map((_, i) => (
				<line key={i} x1={i * 90 - 300} y1={1280} x2={i * 90 + 300} y2={1920} stroke={noche ? '#4a2e18' : '#94612f'} strokeWidth={5} />
			))}
			{Array.from({length: 14}).map((_, i) => (
				<line key={`b${i}`} x1={i * 90 + 300} y1={1280} x2={i * 90 - 300} y2={1920} stroke={noche ? '#4a2e18' : '#94612f'} strokeWidth={5} />
			))}
			<rect x={0} y={1272} width={1080} height={16} fill={ORO} stroke={LINEA} strokeWidth={4} />
		</Lienzo>
	);
};

const Edificio: React.FC<{x: number; ancho: number; alto: number; color: string; noche?: boolean}> = ({x, ancho, alto, color, noche}) => {
	const f = useCurrentFrame();
	const base = 1320;
	return (
		<g>
			<rect x={x} y={base - alto} width={ancho} height={alto} fill={color} stroke={LINEA} strokeWidth={6} />
			<path d={`M ${x - 14} ${base - alto} L ${x + 30} ${base - alto - 110} L ${x + ancho - 30} ${base - alto - 110} L ${x + ancho + 14} ${base - alto} Z`} fill="#4f6178" stroke={LINEA} strokeWidth={6} strokeLinejoin="round" />
			{Array.from({length: Math.floor((alto - 120) / 170)}).map((_, fila) =>
				Array.from({length: Math.floor(ancho / 110)}).map((__, col) => {
					const wx = x + 30 + col * 110;
					const wy = base - alto + 60 + fila * 170;
					const luz = noche && (fila * 3 + col + Math.floor(f / 40)) % 3 === 0;
					return (
						<g key={`${fila}-${col}`}>
							<rect x={wx} y={wy} width={60} height={100} fill={luz ? '#ffd27a' : '#3e4f66'} stroke={LINEA} strokeWidth={4} />
							<rect x={wx - 8} y={wy + 100} width={76} height={12} fill="#e6dcc8" stroke={LINEA} strokeWidth={3} />
						</g>
					);
				}),
			)}
		</g>
	);
};

/** Una calle de París en 1789, al atardecer, con banderas tricolores */
export const EscCalle: React.FC = () => {
	const f = useCurrentFrame();
	const cielo = useId('ccielo');
	return (
		<Lienzo>
			<defs>
				<Degradado id={cielo} colores={[['#3b2a52', 0], ['#c4553a', 0.55], ['#f2a65a', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1400} fill={`url(#${cielo})`} />
			{/* humo */}
			{[0, 1, 2].map((i) => (
				<circle key={i} cx={300 + i * 260 + Math.sin(f / 30 + i) * 20} cy={360 - ((f * 0.6 + i * 80) % 220)} r={90 + i * 20} fill="#5a4a5a" opacity={0.18} />
			))}
			<Edificio x={-40} ancho={360} alto={920} color="#e8d9bd" noche />
			<Edificio x={760} ancho={360} alto={980} color="#e3cfa9" noche />
			<Edificio x={330} ancho={420} alto={640} color="#d9c6a3" noche />
			{/* banderas */}
			{[150, 920].map((x, i) => (
				<g key={x} transform={`translate(${x} ${560 + i * 40})`}>
					<line x1={0} y1={0} x2={i ? -90 : 90} y2={-60} stroke={LINEA} strokeWidth={8} />
					<g transform={`translate(${i ? -90 : 90} -60) skewY(${Math.sin(f / 7 + i) * 6})`}>
						<rect x={i ? -150 : 0} y={0} width={50} height={110} fill={i ? '#e3262e' : '#1f3a7a'} stroke={LINEA} strokeWidth={4} />
						<rect x={i ? -100 : 50} y={0} width={50} height={110} fill="#ffffff" stroke={LINEA} strokeWidth={4} />
						<rect x={i ? -50 : 100} y={0} width={50} height={110} fill={i ? '#1f3a7a' : '#e3262e'} stroke={LINEA} strokeWidth={4} />
					</g>
				</g>
			))}
			{/* adoquines */}
			<rect x={0} y={1320} width={1080} height={600} fill="#8d8478" />
			{Array.from({length: 9}).map((_, fila) =>
				Array.from({length: 12}).map((__, col) => (
					<rect key={`${fila}-${col}`} x={col * 100 - (fila % 2) * 50} y={1330 + fila * fila * 9 + fila * 20} width={90} height={18 + fila * 4} rx={8} fill="#a39a8c" stroke="#6f675d" strokeWidth={3} />
				)),
			)}
		</Lienzo>
	);
};

/** Fachada del palacio con balcón (la reina arriba, el pueblo abajo) */
export const BALCON_Y = 980;
export const EscBalcon: React.FC = () => {
	const cielo = useId('bcielo');
	return (
		<Lienzo>
			<defs>
				<Degradado id={cielo} colores={[['#2b2347', 0], ['#7a3e4e', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${cielo})`} />
			<rect x={60} y={260} width={960} height={1100} fill="#e9dcc1" stroke={LINEA} strokeWidth={8} />
			<path d="M 40 270 L 540 120 L 1040 270 Z" fill="#d9c8a6" stroke={LINEA} strokeWidth={8} strokeLinejoin="round" />
			<circle cx={540} cy={220} r={46} fill={ORO} stroke={LINEA} strokeWidth={6} />
			{[160, 920].map((x) => (
				<g key={x}>
					<rect x={x - 40} y={300} width={80} height={1060} fill="#f4eada" stroke={LINEA} strokeWidth={6} />
					<rect x={x - 54} y={290} width={108} height={30} fill="#d9c8a6" stroke={LINEA} strokeWidth={5} />
				</g>
			))}
			{/* ventanal detrás del balcón */}
			<path d={`M 380 ${BALCON_Y} L 380 520 A 160 160 0 0 1 700 520 L 700 ${BALCON_Y} Z`} fill="#ffd98a" stroke={LINEA} strokeWidth={8} />
			<path d={`M 540 360 L 540 ${BALCON_Y} M 380 640 L 700 640`} stroke="#c9a04a" strokeWidth={8} />
			{/* balcón */}
			<rect x={300} y={BALCON_Y} width={480} height={40} fill="#d9c8a6" stroke={LINEA} strokeWidth={7} />
			<rect x={300} y={BALCON_Y - 150} width={480} height={18} fill="#d9c8a6" stroke={LINEA} strokeWidth={6} />
			{Array.from({length: 11}).map((_, i) => (
				<rect key={i} x={318 + i * 42} y={BALCON_Y - 132} width={16} height={132} rx={8} fill="#efe4cf" stroke={LINEA} strokeWidth={4} />
			))}
			<path d={`M 300 ${BALCON_Y + 40} L 360 ${BALCON_Y + 120} L 720 ${BALCON_Y + 120} L 780 ${BALCON_Y + 40} Z`} fill="#cbb892" stroke={LINEA} strokeWidth={6} strokeLinejoin="round" />
			{/* plaza */}
			<rect x={0} y={1360} width={1080} height={560} fill="#7f776c" />
			{Array.from({length: 6}).map((_, i) => (
				<line key={i} x1={0} y1={1380 + i * i * 18} x2={1080} y2={1380 + i * i * 18} stroke="#6a635a" strokeWidth={4} />
			))}
		</Lienzo>
	);
};

/** Estudio de Rousseau: libros, vela y noche */
export const EscFilosofo: React.FC = () => {
	const f = useCurrentFrame();
	const id = useId('filo');
	const colores = ['#a33b3b', '#2f5d8a', '#3f7a4a', '#c9902f', '#6b4a8a', '#8a5a32'];
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#5a3d26', 0], ['#2e1f13', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{/* librero */}
			{[0, 1, 2, 3].map((fila) => (
				<g key={fila}>
					<rect x={40} y={220 + fila * 230} width={420} height={18} fill="#8a5a32" stroke={LINEA} strokeWidth={4} />
					{Array.from({length: 11}).map((_, i) => {
						const h = 120 + ((i * 37 + fila * 13) % 60);
						return <rect key={i} x={50 + i * 37} y={220 + fila * 230 - h} width={32} height={h} fill={colores[(i + fila) % colores.length]} stroke={LINEA} strokeWidth={3} />;
					})}
				</g>
			))}
			{/* ventana con luna */}
			<rect x={600} y={240} width={380} height={520} fill="#1c2a4a" stroke={LINEA} strokeWidth={10} />
			<circle cx={840} cy={380} r={60} fill="#f6eec4" />
			<circle cx={862} cy={366} r={60} fill="#1c2a4a" />
			{Array.from({length: 9}).map((_, i) => (
				<circle key={i} cx={630 + ((i * 97) % 330)} cy={280 + ((i * 61) % 440)} r={3 + (i % 3)} fill="#ffffff" opacity={0.5 + 0.5 * Math.sin(f / 9 + i)} />
			))}
			<line x1={790} y1={240} x2={790} y2={760} stroke={LINEA} strokeWidth={8} />
			<line x1={600} y1={500} x2={980} y2={500} stroke={LINEA} strokeWidth={8} />
			{/* escritorio */}
			<rect x={0} y={1300} width={1080} height={620} fill="#7a4f2c" />
			<rect x={0} y={1280} width={1080} height={40} fill="#946036" stroke={LINEA} strokeWidth={6} />
			<g transform="translate(930 1280)">
				<rect x={-26} y={-110} width={52} height={110} rx={6} fill="#f6eedd" stroke={LINEA} strokeWidth={5} />
				<path d={`M 0 -110 Q ${14 + Math.sin(f / 3) * 5} -156 ${Math.sin(f / 2) * 5} -186 Q -12 -150 0 -110 Z`} fill="#ffb02e" />
				<circle cx={0} cy={-150} r={180} fill="rgba(255,190,80,0.14)" />
			</g>
		</Lienzo>
	);
};

/** Palacio de Schönbrunn (Viena), soleado */
export const EscViena: React.FC = () => {
	const f = useCurrentFrame();
	const cielo = useId('vcielo');
	return (
		<Lienzo>
			<defs>
				<Degradado id={cielo} colores={[['#6cc7f5', 0], ['#cdeefc', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1200} fill={`url(#${cielo})`} />
			<Nube x={240 + (f % 600) * 0.2} y={240} s={0.8} />
			<Nube x={820 - (f % 600) * 0.15} y={380} s={0.6} />
			{/* palacio amarillo */}
			<rect x={-20} y={560} width={1120} height={560} fill="#f2c94c" stroke={LINEA} strokeWidth={8} />
			<rect x={-20} y={540} width={1120} height={36} fill="#e3e0d6" stroke={LINEA} strokeWidth={6} />
			<path d="M 380 560 L 540 470 L 700 560 Z" fill="#f2c94c" stroke={LINEA} strokeWidth={8} strokeLinejoin="round" />
			{Array.from({length: 9}).map((_, i) =>
				[640, 860].map((y) => (
					<g key={`${i}-${y}`}>
						<rect x={30 + i * 120} y={y} width={60} height={130} fill="#ffffff" stroke={LINEA} strokeWidth={5} />
						<rect x={36 + i * 120} y={y + 6} width={48} height={118} fill="#9ec9ea" />
						<line x1={60 + i * 120} y1={y + 6} x2={60 + i * 120} y2={y + 124} stroke="#ffffff" strokeWidth={4} />
					</g>
				)),
			)}
			{/* jardín */}
			<rect x={0} y={1110} width={1080} height={810} fill="#7cc35b" />
			<ellipse cx={540} cy={1260} rx={300} ry={70} fill="#5ea8d8" stroke={LINEA} strokeWidth={6} />
			<path d={`M 540 1250 Q ${520 + Math.sin(f / 4) * 6} 1150 540 1110 Q ${560 + Math.sin(f / 4) * 6} 1150 540 1250`} fill="#cdeefc" stroke="#8fd0f0" strokeWidth={4} />
			{[120, 960].map((x) => (
				<g key={x}>
					<ellipse cx={x} cy={1240} rx={120} ry={40} fill="#4e9a3a" stroke={LINEA} strokeWidth={5} />
					{[-60, -20, 20, 60].map((dx) => (
						<circle key={dx} cx={x + dx} cy={1226} r={12} fill={dx % 40 === 0 ? '#ff6f91' : '#ffd84a'} stroke={LINEA} strokeWidth={3} />
					))}
				</g>
			))}
		</Lienzo>
	);
};

/** Plaza de la Revolución, 1793: cielo rojo y el cadalso (sin violencia explícita) */
export const EscCadalso: React.FC = () => {
	const cielo = useId('rcielo');
	return (
		<Lienzo>
			<defs>
				<Degradado id={cielo} colores={[['#1a0c10', 0], ['#7a1e1e', 0.6], ['#c4553a', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${cielo})`} />
			{/* guillotina (silueta) */}
			<g fill="#120a0c" stroke="#120a0c">
				<rect x={430} y={420} width={36} height={760} />
				<rect x={614} y={420} width={36} height={760} />
				<rect x={410} y={400} width={260} height={44} />
				<path d="M 466 520 L 614 470 L 614 560 L 466 560 Z" fill="#3a2a2e" stroke="#120a0c" strokeWidth={6} />
			</g>
			{/* tarima */}
			<rect x={240} y={1180} width={600} height={60} fill="#2a1a14" />
			<rect x={270} y={1240} width={540} height={260} fill="#1e130e" />
			{/* multitud en silueta */}
			{Array.from({length: 18}).map((_, i) => {
				const x = (i * 67) % 1100 - 20;
				const y = 1440 + (i % 3) * 70;
				return (
					<g key={i} fill="#0e0709">
						<circle cx={x} cy={y} r={46} />
						<rect x={x - 56} y={y + 30} width={112} height={400} rx={40} />
					</g>
				);
			})}
		</Lienzo>
	);
};

/* =================== Michael Jackson =================== */

/** Concierto: escenario con haces de luz de colores y público en silueta */
export const EscConcierto: React.FC<{color?: string}> = ({color = '#2a1650'}) => {
	const f = useCurrentFrame();
	const id = useId('conc');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[[color, 0], ['#08040f', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{[
				['#ff4fa3', 160, 0.9], ['#4fd1ff', 540, 0.7], ['#ffd84a', 920, 0.8], ['#7cff6b', 340, 1.1], ['#ff7a3d', 740, 1.0],
			].map(([c, x, v], i) => {
				const ang = Math.sin(f / (18 * (v as number)) + i) * 22;
				return <path key={i} d="M -26 0 L 26 0 L 260 1500 L -260 1500 Z" fill={c as string} opacity={0.16} transform={`translate(${x} 60) rotate(${ang})`} />;
			})}
			{Array.from({length: 30}).map((_, i) => (
				<circle key={i} cx={random(`cs${i}`) * 1080} cy={random(`cy${i}`) * 1100} r={3 + random(`cr${i}`) * 4} fill="#ffffff" opacity={0.3 + 0.3 * Math.sin(f / 5 + i)} />
			))}
			{/* tarima */}
			<rect x={0} y={1460} width={1080} height={80} fill="#1b1b22" />
			<rect x={0} y={1460} width={1080} height={10} fill="#ffd84a" opacity={0.7} />
			{/* público */}
			{Array.from({length: 16}).map((_, i) => {
				const x = (i * 71) % 1120 - 20;
				const y = 1640 + (i % 3) * 70 + Math.abs(Math.sin(f / 4 + i)) * -14;
				return (
					<g key={i} fill="#07040b">
						<circle cx={x} cy={y} r={44} />
						<rect x={x - 54} y={y + 30} width={108} height={300} rx={40} />
						{i % 3 === 0 && <rect x={x + 30} y={y - 120 + Math.sin(f / 3 + i) * 14} width={20} height={120} rx={10} />}
					</g>
				);
			})}
		</Lienzo>
	);
};

/** Camerino con espejo de bombillas */
export const EscCamerino: React.FC = () => {
	const id = useId('cam');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#6b4a5a', 0], ['#3a2533', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{Array.from({length: 12}).map((_, i) => (
				<line key={i} x1={i * 100} y1={0} x2={i * 100} y2={1300} stroke="#5a3b4a" strokeWidth={6} />
			))}
			{/* espejo */}
			<rect x={150} y={220} width={780} height={960} rx={30} fill="#f2c94c" stroke={LINEA} strokeWidth={8} />
			<rect x={190} y={260} width={700} height={880} rx={18} fill="#b8cdd8" stroke={LINEA} strokeWidth={6} />
			<path d="M 260 360 L 420 280 M 300 520 L 520 400" stroke="#ffffff" strokeWidth={14} opacity={0.35} strokeLinecap="round" />
			{Array.from({length: 9}).map((_, i) => (
				<g key={i}>
					<circle cx={190 + i * 87.5} cy={240} r={22} fill="#fff6c8" stroke={LINEA} strokeWidth={4} />
					<circle cx={190 + i * 87.5} cy={240} r={44} fill="#fff6c8" opacity={0.15} />
				</g>
			))}
			{[0, 1, 2, 3, 4, 5].map((i) => (
				<g key={`l${i}`}>
					<circle cx={170} cy={340 + i * 150} r={22} fill="#fff6c8" stroke={LINEA} strokeWidth={4} />
					<circle cx={910} cy={340 + i * 150} r={22} fill="#fff6c8" stroke={LINEA} strokeWidth={4} />
				</g>
			))}
			{/* tocador */}
			<rect x={0} y={1300} width={1080} height={620} fill="#7a4f3a" />
			<rect x={0} y={1280} width={1080} height={40} fill="#946036" stroke={LINEA} strokeWidth={6} />
		</Lienzo>
	);
};

/** Alfombra roja con muro de fotos y flashes */
export const EscAlfombra: React.FC<{flashes?: boolean}> = ({flashes = true}) => {
	const f = useCurrentFrame();
	return (
		<Lienzo>
			<rect x={0} y={0} width={1080} height={1920} fill="#1c1c26" />
			{Array.from({length: 7}).map((_, fila) =>
				Array.from({length: 5}).map((__, col) => (
					<text key={`${fila}-${col}`} x={col * 240 + (fila % 2) * 120 - 40} y={180 + fila * 170} fontFamily={TITULAR} fontWeight={900} fontSize={54} fill="#2e2e3c">
						★ PRENSA
					</text>
				)),
			)}
			{flashes &&
				Array.from({length: 8}).map((_, i) => {
					const t = (f + i * 13) % 40;
					return t < 3 ? <circle key={i} cx={(i * 173) % 1080} cy={300 + ((i * 251) % 900)} r={160} fill="#ffffff" opacity={0.55 - t * 0.15} /> : null;
				})}
			<path d="M 380 1300 L 700 1300 L 1080 1920 L 0 1920 Z" fill="#b0182a" />
			<rect x={0} y={1290} width={1080} height={14} fill="#d4a93c" />
			{[80, 1000].map((x) => (
				<g key={x}>
					<rect x={x - 12} y={1180} width={24} height={140} fill="#d4a93c" stroke={LINEA} strokeWidth={4} />
					<circle cx={x} cy={1170} r={20} fill="#d4a93c" stroke={LINEA} strokeWidth={4} />
				</g>
			))}
			<path d="M 80 1200 Q 540 1260 1000 1200" stroke="#7a1020" strokeWidth={16} fill="none" />
		</Lienzo>
	);
};

/** Globo terráqueo girando (las revistas dan la vuelta al mundo) */
export const EscMundo: React.FC = () => {
	const f = useCurrentFrame();
	const giro = (f * 2) % 360;
	return (
		<Lienzo>
			<rect x={0} y={0} width={1080} height={1920} fill="#0d1838" />
			{Array.from({length: 60}).map((_, i) => (
				<circle key={i} cx={random(`m${i}`) * 1080} cy={random(`n${i}`) * 1920} r={1.5 + random(`o${i}`) * 3} fill="#ffffff" opacity={0.6} />
			))}
			<defs>
				<clipPath id="globo-mj">
					<circle cx={540} cy={1000} r={360} />
				</clipPath>
			</defs>
			<circle cx={540} cy={1000} r={372} fill="#4fd1ff" opacity={0.18} />
			<circle cx={540} cy={1000} r={360} fill="#2f7fd0" stroke={LINEA} strokeWidth={10} />
			<g clipPath="url(#globo-mj)">
				{[0, 1].map((k) => (
					<g key={k} transform={`translate(${((giro * 4) % 1440) - 720 + k * 1440 - 720} 0)`}>
						<path d="M 300 760 Q 380 700 460 760 Q 500 860 430 920 Q 380 1020 330 960 Q 270 880 300 760 Z" fill="#7cc35b" stroke={LINEA} strokeWidth={6} />
						<path d="M 380 1000 Q 440 980 470 1060 Q 460 1180 400 1260 Q 360 1180 370 1080 Z" fill="#7cc35b" stroke={LINEA} strokeWidth={6} />
						<path d="M 620 760 Q 760 700 900 780 Q 960 880 860 900 Q 760 880 700 960 Q 650 900 620 760 Z" fill="#7cc35b" stroke={LINEA} strokeWidth={6} />
						<path d="M 640 980 Q 720 960 760 1040 Q 740 1160 680 1180 Q 630 1100 640 980 Z" fill="#7cc35b" stroke={LINEA} strokeWidth={6} />
						<path d="M 940 1100 Q 1010 1080 1040 1140 Q 1010 1200 950 1180 Z" fill="#7cc35b" stroke={LINEA} strokeWidth={6} />
					</g>
				))}
				<ellipse cx={460} cy={880} rx={160} ry={90} fill="#ffffff" opacity={0.12} />
			</g>
		</Lienzo>
	);
};

/** Tablero de corcho con fotos (las "pruebas") */
export const EscCorcho: React.FC = () => (
	<Lienzo>
		<rect x={0} y={0} width={1080} height={1920} fill="#5a3b26" />
		<rect x={40} y={200} width={1000} height={1340} rx={16} fill="#c9925a" stroke={LINEA} strokeWidth={10} />
		{Array.from({length: 160}).map((_, i) => (
			<circle key={i} cx={60 + random(`k${i}`) * 960} cy={220 + random(`l${i}`) * 1300} r={3 + random(`p${i}`) * 4} fill="#a87442" opacity={0.6} />
		))}
		<rect x={0} y={1560} width={1080} height={360} fill="#3e2a1c" />
	</Lienzo>
);

/** Fondo de explicación científica: cuadrícula clara */
export const EscCiencia: React.FC<{color?: string}> = ({color = '#e6f3fb'}) => (
	<Lienzo>
		<rect x={0} y={0} width={1080} height={1920} fill={color} />
		{Array.from({length: 28}).map((_, i) => (
			<line key={`v${i}`} x1={i * 40} y1={0} x2={i * 40} y2={1920} stroke="#c6dfee" strokeWidth={2} />
		))}
		{Array.from({length: 48}).map((_, i) => (
			<line key={`h${i}`} x1={0} y1={i * 40} x2={1080} y2={i * 40} stroke="#c6dfee" strokeWidth={2} />
		))}
	</Lienzo>
);

/** Estudio de televisión */
export const EscTV: React.FC = () => {
	const f = useCurrentFrame();
	const id = useId('tv');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#1f2e52', 0], ['#0e1428', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{Array.from({length: 7}).map((_, i) => (
				<rect key={i} x={40 + i * 150} y={260} width={120} height={780} rx={12} fill="#2c4170" opacity={0.6 + 0.3 * Math.sin(f / 10 + i)} />
			))}
			<circle cx={540} cy={640} r={260} fill="#4fd1ff" opacity={0.08} />
			<rect x={0} y={1240} width={1080} height={680} fill="#2a2a36" />
			<ellipse cx={540} cy={1300} rx={520} ry={60} fill="#3a3a4a" />
			{/* sofá */}
			<rect x={140} y={1180} width={800} height={180} rx={50} fill="#c8102e" stroke={LINEA} strokeWidth={8} />
			<rect x={110} y={1260} width={860} height={160} rx={60} fill="#a00d24" stroke={LINEA} strokeWidth={8} />
			{/* rótulo EN VIVO */}
			<g transform="translate(860 160)">
				<rect x={-120} y={-40} width={240} height={80} rx={14} fill="#e3262e" stroke={LINEA} strokeWidth={6} />
				<circle cx={-80} cy={0} r={14} fill="#ffffff" opacity={0.5 + 0.5 * Math.sin(f / 3)} />
				<text x={20} y={18} textAnchor="middle" fontFamily={TITULAR} fontWeight={900} fontSize={46} fill="#ffffff">
					EN VIVO
				</text>
			</g>
		</Lienzo>
	);
};

/** Sala de una casa con el televisor encendido */
export const EscSala: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Lienzo>
			<rect x={0} y={0} width={1080} height={1920} fill="#3b5a6b" />
			<rect x={0} y={0} width={1080} height={1920} fill="#7fd0ff" opacity={0.08 + 0.05 * Math.sin(f / 2)} />
			<rect x={80} y={300} width={260} height={360} fill="#2a4050" stroke={LINEA} strokeWidth={8} />
			<line x1={210} y1={300} x2={210} y2={660} stroke={LINEA} strokeWidth={6} />
			<circle cx={860} cy={420} r={70} fill="#f2c94c" stroke={LINEA} strokeWidth={6} />
			<path d="M 830 490 L 890 490 L 900 560 L 820 560 Z" fill="#c9a04a" stroke={LINEA} strokeWidth={5} />
			<rect x={0} y={1320} width={1080} height={600} fill="#6b4a32" />
			{/* sofá */}
			<rect x={60} y={1220} width={960} height={200} rx={60} fill="#5a6e8a" stroke={LINEA} strokeWidth={8} />
			<rect x={30} y={1320} width={1020} height={190} rx={70} fill="#4a5c76" stroke={LINEA} strokeWidth={8} />
		</Lienzo>
	);
};

/** Fondo partido en blanco y negro */
export const EscBlancoNegro: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<Lienzo>
			<rect x={0} y={0} width={540} height={1920} fill="#111114" />
			<rect x={540} y={0} width={540} height={1920} fill="#f4f4f0" />
			{Array.from({length: 18}).map((_, i) => (
				<circle key={i} cx={i < 9 ? 60 + (i % 3) * 180 : 600 + (i % 3) * 180} cy={260 + Math.floor((i % 9) / 3) * 420 + Math.sin(f / 9 + i) * 20} r={30} fill={i < 9 ? '#2a2a32' : '#dcdcd6'} />
			))}
			<rect x={0} y={1500} width={1080} height={420} fill="#2a2a32" />
			<rect x={0} y={1500} width={1080} height={10} fill="#ffd84a" opacity={0.8} />
		</Lienzo>
	);
};

/* ---------- Egipto (short de la Esfinge) ---------- */

const Piramide: React.FC<{x: number; base: number; ancho: number; alto: number; luz?: string; sombra?: string}> = ({x, base, ancho, alto, luz = '#e9c47c', sombra = '#c4964f'}) => (
	<g>
		<path d={`M ${x - ancho / 2} ${base} L ${x} ${base - alto} L ${x + ancho * 0.12} ${base} Z`} fill={luz} stroke={LINEA} strokeWidth={7} strokeLinejoin="round" />
		<path d={`M ${x + ancho * 0.12} ${base} L ${x} ${base - alto} L ${x + ancho / 2} ${base} Z`} fill={sombra} stroke={LINEA} strokeWidth={7} strokeLinejoin="round" />
		{[0.25, 0.5, 0.75].map((t) => (
			<path key={t} d={`M ${x - (ancho / 2) * (1 - t)} ${base - alto * t} L ${x + (ancho / 2) * (1 - t)} ${base - alto * t}`} stroke={LINEA} strokeWidth={3} opacity={0.25} />
		))}
	</g>
);

/** Desierto de Giza con pirámides. `tono`: día, leyenda (sepia) o noche. `horizonte` = línea de arena. */
export const EscDesierto: React.FC<{tono?: 'dia' | 'leyenda' | 'noche'; piramides?: boolean; horizonte?: number}> = ({tono = 'dia', piramides = true, horizonte = 1180}) => {
	const f = useCurrentFrame();
	const cielo = useId('dcielo');
	const colores: Record<string, [string, number][]> = {
		dia: [['#4fa3e0', 0], ['#9fd2f0', 0.55], ['#ffe9b8', 1]],
		leyenda: [['#a9824e', 0], ['#d9b57a', 0.6], ['#f0d9a6', 1]],
		noche: [['#0e1430', 0], ['#22305a', 0.6], ['#4a4a6a', 1]],
	};
	const arena = tono === 'noche' ? ['#5a5468', '#4a4458', '#3e3a4c'] : tono === 'leyenda' ? ['#d9b57a', '#c9a066', '#b98d54'] : ['#f0cf86', '#e6bd6e', '#d9a95a'];
	return (
		<Lienzo>
			<defs>
				<Degradado id={cielo} colores={colores[tono]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${cielo})`} />
			{tono === 'noche' ? (
				<>
					<circle cx={820} cy={330} r={70} fill="#f4efd6" />
					<circle cx={846} cy={312} r={62} fill="#22305a" />
					{Array.from({length: 26}).map((_, i) => (
						<circle key={i} cx={(i * 263) % 1080} cy={120 + ((i * 137) % 760)} r={i % 3 ? 3 : 5} fill="#ffffff" opacity={0.5 + 0.5 * Math.sin(f / 9 + i)} />
					))}
				</>
			) : (
				<>
					<circle cx={830} cy={360} r={110} fill={tono === 'leyenda' ? '#f6e2b0' : '#fff4c2'} opacity={0.9} />
					<circle cx={830} cy={360} r={150} fill={tono === 'leyenda' ? '#f6e2b0' : '#fff4c2'} opacity={0.25} />
					<Nube x={200 + ((f * 0.4) % 200)} y={520} s={0.6} color={tono === 'leyenda' ? '#efdcb4' : '#ffffff'} />
				</>
			)}
			{piramides && (
				<g opacity={tono === 'noche' ? 0.55 : 1}>
					<Piramide x={250} base={horizonte + 10} ancho={560} alto={420} luz={tono === 'leyenda' ? '#d8b27a' : '#e9c47c'} sombra={tono === 'leyenda' ? '#b48a54' : '#c4964f'} />
					<Piramide x={760} base={horizonte + 10} ancho={420} alto={300} luz={tono === 'leyenda' ? '#d8b27a' : '#e9c47c'} sombra={tono === 'leyenda' ? '#b48a54' : '#c4964f'} />
					<Piramide x={980} base={horizonte + 10} ancho={240} alto={170} luz={tono === 'leyenda' ? '#d8b27a' : '#e9c47c'} sombra={tono === 'leyenda' ? '#b48a54' : '#c4964f'} />
				</g>
			)}
			<path d={`M 0 ${horizonte} Q 270 ${horizonte - 40} 540 ${horizonte} T 1080 ${horizonte} L 1080 1920 L 0 1920 Z`} fill={arena[0]} />
			<path d={`M 0 ${horizonte + 180} Q 300 ${horizonte + 120} 620 ${horizonte + 190} T 1080 ${horizonte + 160} L 1080 1920 L 0 1920 Z`} fill={arena[1]} />
			<path d={`M 0 ${horizonte + 470} Q 360 ${horizonte + 420} 700 ${horizonte + 480} T 1080 ${horizonte + 450} L 1080 1920 L 0 1920 Z`} fill={arena[2]} />
			{Array.from({length: 14}).map((_, i) => (
				<path key={i} d={`M ${(i * 173) % 1080} ${horizonte + 240 + ((i * 97) % 520)} q 30 -14 60 0`} stroke={LINEA} strokeWidth={4} opacity={0.18} fill="none" />
			))}
		</Lienzo>
	);
};

/** Sala de museo con columnas y cordón rojo */
export const EscMuseo: React.FC = () => (
	<Lienzo>
		<rect x={0} y={0} width={1080} height={1920} fill="#e9dfca" />
		<rect x={0} y={0} width={1080} height={220} fill="#d8ccb2" />
		{[90, 990].map((x) => (
			<g key={x}>
				<rect x={x - 70} y={220} width={140} height={1180} fill="#f4efe2" stroke={LINEA} strokeWidth={7} />
				{Array.from({length: 4}).map((_, i) => (
					<line key={i} x1={x - 42 + i * 28} y1={250} x2={x - 42 + i * 28} y2={1370} stroke={LINEA} strokeWidth={4} opacity={0.25} />
				))}
				<rect x={x - 90} y={200} width={180} height={40} fill="#f4efe2" stroke={LINEA} strokeWidth={7} />
				<rect x={x - 90} y={1380} width={180} height={40} fill="#f4efe2" stroke={LINEA} strokeWidth={7} />
			</g>
		))}
		<rect x={190} y={300} width={700} height={160} rx={10} fill="#8a2f3a" stroke={LINEA} strokeWidth={7} opacity={0.9} />
		<rect x={0} y={1400} width={1080} height={520} fill="#b99c74" />
		{Array.from({length: 8}).map((_, i) => (
			<line key={i} x1={0} y1={1400 + i * i * 9 + i * 18} x2={1080} y2={1400 + i * i * 9 + i * 18} stroke={LINEA} strokeWidth={3} opacity={0.25} />
		))}
		{Array.from({length: 9}).map((_, i) => (
			<line key={`v${i}`} x1={540 + (i - 4) * 120} y1={1400} x2={540 + (i - 4) * 300} y2={1920} stroke={LINEA} strokeWidth={3} opacity={0.2} />
		))}
	</Lienzo>
);

/** Pergamino para la línea de tiempo */
export const EscPergamino: React.FC = () => (
	<Lienzo>
		<rect x={0} y={0} width={1080} height={1920} fill="#c9a77a" />
		<rect x={60} y={200} width={960} height={1500} rx={30} fill="#f4e6c4" stroke={LINEA} strokeWidth={9} />
		<rect x={90} y={230} width={900} height={1440} rx={20} fill="none" stroke="#b8925a" strokeWidth={5} />
		{Array.from({length: 12}).map((_, i) => (
			<circle key={i} cx={(i * 311) % 1000 + 40} cy={260 + ((i * 173) % 1380)} r={30 + (i % 4) * 14} fill="#e2cc9c" opacity={0.35} />
		))}
	</Lienzo>
);
