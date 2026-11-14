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

export const EscMapa: React.FC = () => {
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
			{Object.entries(CIUDADES).map(([n, [x, y]]) => (
				<g key={n}>
					<circle cx={x} cy={y} r={14} fill={n === 'LONDRES' ? '#e3262e' : LINEA} stroke="#ffffff" strokeWidth={4} />
					<text x={x} y={y - 26} textAnchor="middle" fontFamily={TITULAR} fontWeight={900} fontSize={36} fill={LINEA}>
						{n}
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
