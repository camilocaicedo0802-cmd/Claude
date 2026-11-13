import React from 'react';
import {interpolate, random, useCurrentFrame} from 'remotion';

/*
 * Fondos ilustrados por código (SVG 1080x1920) para la Atlántida.
 * Estilo: ilustración plana con degradados, contornos finos oscuros y capas animadas.
 */

const LINEA = '#2a2433';
const MARMOL = '#f6f0e4';
const MARMOL_S = '#dcd0bb';
const ORO = '#f2c14e';
const ORO_S = '#d39a28';
const TURQ = '#1fb5c9';

const Lienzo: React.FC<{children: React.ReactNode}> = ({children}) => (
	<svg viewBox="0 0 1080 1920" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" style={{position: 'absolute', inset: 0}}>
		{children}
	</svg>
);

const Degradado: React.FC<{id: string; colores: [string, number][]; x2?: number; y2?: number}> = ({id, colores, x2 = 0, y2 = 1}) => (
	<linearGradient id={id} x1={0} y1={0} x2={x2} y2={y2}>
		{colores.map(([c, o]) => (
			<stop key={o} offset={o} stopColor={c} />
		))}
	</linearGradient>
);

const useId = (base: string) => `${base}-${React.useId().replace(/:/g, '')}`;

/* ---------------- piezas reutilizables ---------------- */

const Sol: React.FC<{x: number; y: number; r: number; color?: string; halo?: string}> = ({x, y, r, color = '#fff6c8', halo = 'rgba(255,230,150,0.35)'}) => (
	<g>
		<circle cx={x} cy={y} r={r * 2.6} fill={halo} />
		<circle cx={x} cy={y} r={r * 1.6} fill={halo} />
		<circle cx={x} cy={y} r={r} fill={color} />
	</g>
);

const Nube: React.FC<{x: number; y: number; s?: number; color?: string; sombra?: string}> = ({x, y, s = 1, color = '#ffffff', sombra = '#d6e6f5'}) => (
	<g transform={`translate(${x} ${y}) scale(${s})`}>
		<ellipse cx={0} cy={40} rx={190} ry={46} fill={sombra} />
		<circle cx={-90} cy={10} r={62} fill={color} />
		<circle cx={0} cy={-20} r={86} fill={color} />
		<circle cx={95} cy={8} r={66} fill={color} />
		<ellipse cx={0} cy={36} rx={180} ry={40} fill={color} />
	</g>
);

const Nubes: React.FC<{y: number; n?: number; color?: string; sombra?: string; vel?: number; escala?: number; semilla?: string}> = ({y, n = 4, color, sombra, vel = 0.6, escala = 1, semilla = 'n'}) => {
	const f = useCurrentFrame();
	return (
		<g>
			{Array.from({length: n}).map((_, i) => {
				const x0 = random(`${semilla}x${i}`) * 1500 - 200;
				const x = ((x0 + f * vel * (0.6 + random(`${semilla}v${i}`))) % 1600) - 260;
				return <Nube key={i} x={x} y={y + (random(`${semilla}y${i}`) - 0.5) * 220} s={escala * (0.6 + random(`${semilla}s${i}`) * 0.6)} color={color} sombra={sombra} />;
			})}
		</g>
	);
};

/** Agua con brillos que se mueven. */
const Agua: React.FC<{y: number; alto: number; arriba: string; abajo: string; brillo?: string; x?: number; ancho?: number}> = ({y, alto, arriba, abajo, brillo = 'rgba(255,255,255,0.55)', x = -50, ancho = 1180}) => {
	const f = useCurrentFrame();
	const id = useId('agua');
	return (
		<g>
			<defs>
				<Degradado id={id} colores={[[arriba, 0], [abajo, 1]]} />
			</defs>
			<rect x={x} y={y} width={ancho} height={alto} fill={`url(#${id})`} />
			{Array.from({length: 26}).map((_, i) => {
				const yy = y + 14 + random(`ay${i}`) * (alto - 20);
				const prof = (yy - y) / alto;
				const w = 30 + prof * 90;
				const xx = x + ((random(`ax${i}`) * ancho + f * (0.8 + prof * 1.5)) % ancho);
				return <rect key={i} x={xx} y={yy} width={w} height={3 + prof * 4} rx={3} fill={brillo} opacity={0.4 + 0.5 * Math.abs(Math.sin(f / 12 + i))} />;
			})}
		</g>
	);
};

/** Columna de mármol con capitel. */
const Columna: React.FC<{x: number; y: number; w: number; h: number; color?: string; sombra?: string; rot?: number}> = ({x, y, w, h, color = MARMOL, sombra = MARMOL_S, rot = 0}) => (
	<g transform={`rotate(${rot} ${x + w / 2} ${y + h})`}>
		<rect x={x - w * 0.18} y={y} width={w * 1.36} height={w * 0.28} rx={4} fill={color} stroke={LINEA} strokeWidth={3} />
		<rect x={x} y={y + w * 0.28} width={w} height={h - w * 0.56} fill={color} stroke={LINEA} strokeWidth={3} />
		<rect x={x + w * 0.62} y={y + w * 0.28} width={w * 0.38} height={h - w * 0.56} fill={sombra} />
		{[0.25, 0.5].map((k) => (
			<line key={k} x1={x + w * k} y1={y + w * 0.3} x2={x + w * k} y2={y + h - w * 0.3} stroke={sombra} strokeWidth={3} />
		))}
		<rect x={x - w * 0.18} y={y + h - w * 0.28} width={w * 1.36} height={w * 0.28} rx={4} fill={color} stroke={LINEA} strokeWidth={3} />
	</g>
);

/** Edificio atlante: bloque de mármol con columnas y techo dorado. */
const Edificio: React.FC<{x: number; base: number; w: number; h: number; techo?: 'triangulo' | 'cupula' | 'plano'; oscuro?: number}> = ({x, base, w, h, techo = 'triangulo', oscuro = 0}) => {
	const y = base - h;
	const cols = Math.max(2, Math.round(w / 55));
	return (
		<g>
			<rect x={x} y={y} width={w} height={h} fill={MARMOL} stroke={LINEA} strokeWidth={3} />
			<rect x={x + w * 0.78} y={y} width={w * 0.22} height={h} fill={MARMOL_S} />
			{Array.from({length: cols}).map((_, i) => (
				<rect key={i} x={x + (w / cols) * i + w / cols / 2 - w * 0.03} y={y + h * 0.18} width={w * 0.06} height={h * 0.74} fill={MARMOL_S} />
			))}
			<rect x={x - 6} y={y} width={w + 12} height={Math.max(10, h * 0.08)} fill={ORO} stroke={LINEA} strokeWidth={3} />
			{techo === 'triangulo' && <path d={`M ${x - 10} ${y} L ${x + w / 2} ${y - w * 0.32} L ${x + w + 10} ${y} Z`} fill={ORO} stroke={LINEA} strokeWidth={3} strokeLinejoin="round" />}
			{techo === 'cupula' && (
				<g>
					<path d={`M ${x + w * 0.12} ${y} A ${w * 0.38} ${w * 0.38} 0 0 1 ${x + w * 0.88} ${y} Z`} fill={ORO} stroke={LINEA} strokeWidth={3} />
					<path d={`M ${x + w * 0.62} ${y - w * 0.3} A ${w * 0.38} ${w * 0.38} 0 0 1 ${x + w * 0.88} ${y} L ${x + w * 0.7} ${y} Z`} fill={ORO_S} opacity={0.6} />
				</g>
			)}
			{oscuro > 0 && <rect x={x - 12} y={y - w * 0.4} width={w + 24} height={h + w * 0.4} fill="#080c23" opacity={oscuro} />}
		</g>
	);
};

/** Templo dorado con cúpula (el corazón de la ciudad). */
const Templo: React.FC<{cx: number; base: number; s?: number; brillo?: number}> = ({cx, base, s = 1, brillo = 0}) => (
	<g transform={`translate(${cx} ${base}) scale(${s})`}>
		<ellipse cx={0} cy={-330} rx={260 + brillo * 60} ry={260 + brillo * 60} fill="rgba(255,220,120,0.25)" />
		<rect x={-230} y={-40} width={460} height={40} fill={MARMOL} stroke={LINEA} strokeWidth={4} />
		<rect x={-210} y={-80} width={420} height={40} fill={MARMOL} stroke={LINEA} strokeWidth={4} />
		{Array.from({length: 7}).map((_, i) => (
			<Columna key={i} x={-190 + i * 60} y={-320} w={30} h={240} color="#fbe9b8" sombra={ORO} />
		))}
		<rect x={-215} y={-350} width={430} height={34} fill={ORO} stroke={LINEA} strokeWidth={4} />
		<path d="M -170 -350 A 170 170 0 0 1 170 -350 Z" fill={ORO} stroke={LINEA} strokeWidth={4} />
		<path d="M 40 -510 A 170 170 0 0 1 170 -350 L 80 -350 Z" fill={ORO_S} opacity={0.6} />
		<path d="M -120 -440 Q -60 -505 20 -515" stroke="#fff6c8" strokeWidth={10} fill="none" strokeLinecap="round" opacity={0.8} />
		<rect x={-8} y={-560} width={16} height={60} fill={ORO} stroke={LINEA} strokeWidth={3} />
		<circle cx={0} cy={-566} r={16} fill={TURQ} stroke={LINEA} strokeWidth={3} />
	</g>
);

const Barco: React.FC<{x: number; y: number; s?: number; vela?: string}> = ({x, y, s = 1, vela = '#e3262e'}) => (
	<g transform={`translate(${x} ${y}) scale(${s})`}>
		<path d="M -70 0 L 70 0 L 50 26 L -50 26 Z" fill="#8a5a32" stroke={LINEA} strokeWidth={4} strokeLinejoin="round" />
		<line x1={0} y1={0} x2={0} y2={-110} stroke={LINEA} strokeWidth={5} />
		<path d="M 4 -104 Q 60 -60 4 -14 Z" fill={vela} stroke={LINEA} strokeWidth={4} strokeLinejoin="round" />
		<path d="M -4 -96 Q -46 -60 -4 -24 Z" fill="#fff" stroke={LINEA} strokeWidth={4} strokeLinejoin="round" />
	</g>
);

/* ---------------- ESCENARIOS ---------------- */

/** Calle con canal. variante: normal | temblor | inundada */
export const EscCanales: React.FC<{variante?: 'normal' | 'temblor' | 'inundada'; nivelAgua?: number; templo?: number}> = ({variante = 'normal', nivelAgua = 0, templo = 0}) => {
	const f = useCurrentFrame();
	const id = useId('cielo');
	const cielo: [string, number][] =
		variante === 'inundada'
			? [['#1d2645', 0], ['#4a5878', 0.55], ['#7a86a0', 1]]
			: variante === 'temblor'
				? [['#c98b55', 0], ['#efc48f', 0.6], ['#f7e0b8', 1]]
				: [['#5ec8ff', 0], ['#a8e4ff', 0.5], ['#fff1c7', 1]];
	const oscuro = variante === 'inundada' ? 0.35 : 0;
	const izq = [
		{x: -60, w: 250, h: 520, base: 1180, t: 'triangulo' as const},
		{x: 150, w: 180, h: 380, base: 1030, t: 'cupula' as const},
		{x: 300, w: 120, h: 260, base: 930, t: 'triangulo' as const},
	];
	const der = [
		{x: 890, w: 250, h: 540, base: 1180, t: 'cupula' as const},
		{x: 750, w: 180, h: 380, base: 1030, t: 'triangulo' as const},
		{x: 660, w: 120, h: 260, base: 930, t: 'cupula' as const},
	];
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={cielo} />
			</defs>
			<rect x={0} y={0} width={1080} height={1000} fill={`url(#${id})`} />
			{variante === 'normal' && <Sol x={820} y={260} r={70} />}
			<Nubes y={330} n={4} vel={0.5} color={variante === 'inundada' ? '#5b6787' : '#ffffff'} sombra={variante === 'inundada' ? '#3c4766' : '#d6e6f5'} />
			{/* montañas lejanas */}
			<path d="M -20 900 L 160 700 L 320 860 L 470 690 L 640 870 L 820 720 L 1100 900 Z" fill={variante === 'inundada' ? '#3e4b6b' : '#8fc6d8'} />
			<Templo cx={540} base={900} s={0.62} brillo={templo} />
			{oscuro > 0 && <rect x={0} y={0} width={1080} height={940} fill="#0b1230" opacity={oscuro} />}
			{/* suelo del fondo */}
			<rect x={0} y={895} width={1080} height={40} fill={MARMOL_S} stroke={LINEA} strokeWidth={3} />
			{[...izq, ...der].map((e, i) => (
				<Edificio key={i} x={e.x} base={e.base} w={e.w} h={e.h} techo={e.t} oscuro={oscuro * 0.8} />
			))}
			{/* aceras */}
			<path d="M 0 1180 L 440 920 L 520 920 L 300 1920 L 0 1920 Z" fill="#efe3c9" stroke={LINEA} strokeWidth={3} />
			<path d="M 1080 1180 L 640 920 L 560 920 L 780 1920 L 1080 1920 Z" fill="#efe3c9" stroke={LINEA} strokeWidth={3} />
			{Array.from({length: 9}).map((_, i) => {
				const t = (i + 1) / 10;
				const yy = 920 + (1920 - 920) * t * t;
				return (
					<g key={i} stroke="#d8c7a3" strokeWidth={3}>
						<line x1={0} y1={yy} x2={520 - 220 * t} y2={yy} />
						<line x1={560 + 220 * t} y1={yy} x2={1080} y2={yy} />
					</g>
				);
			})}
			{/* canal */}
			<path d="M 520 920 L 560 920 L 780 1920 L 300 1920 Z" fill={TURQ} />
			<clipPath id={`${id}-canal`}>
				<path d="M 520 920 L 560 920 L 780 1920 L 300 1920 Z" />
			</clipPath>
			<g clipPath={`url(#${id}-canal)`}>
				<Agua y={920} alto={1000} arriba="#5fd8e6" abajo="#0d7f9e" />
			</g>
			{variante !== 'inundada' && (
				<g>
					<Barco x={540 + Math.sin(f / 40) * 6} y={1080 + ((f * 1.2) % 300)} s={0.55 + ((f * 1.2) % 300) / 600} />
					<Barco x={470} y={1500 + Math.sin(f / 20) * 6} s={1.1} vela="#1f5fa8" />
				</g>
			)}
			{variante === 'temblor' && (
				<g stroke={LINEA} strokeWidth={8} fill="none" strokeLinejoin="round">
					<path d="M 60 1900 L 140 1700 L 110 1560 L 200 1400 L 180 1260" />
					<path d="M 1040 1880 L 930 1720 L 980 1560 L 890 1420" />
					<path d="M 140 1700 L 230 1660" />
				</g>
			)}
			{variante === 'inundada' && (
				<g>
					<rect x={0} y={1150 - nivelAgua} width={1080} height={900} fill="rgba(16,52,96,0.88)" />
					{Array.from({length: 3}).map((_, k) => {
						const yb = 1150 - nivelAgua + k * 120;
						const pts = Array.from({length: 25})
							.map((__, i) => `${(i / 24) * 1180 - 50},${yb + Math.sin(i * 0.8 + f / 5 + k) * 16}`)
							.join(' ');
						return <polyline key={k} points={pts} fill="none" stroke="rgba(200,235,255,0.7)" strokeWidth={8 - k * 2} />;
					})}
				</g>
			)}
		</Lienzo>
	);
};

/** Vista aérea de la ciudad en anillos de tierra y agua. `revelar` 0..1 dibuja los anillos. */
export const EscCiudadAerea: React.FC<{revelar?: number}> = ({revelar = 1}) => {
	const f = useCurrentFrame();
	const id = useId('mar');
	const cx = 540;
	const cy = 900;
	const anillos = [
		{r: 560, tipo: 'tierra'},
		{r: 480, tipo: 'agua'},
		{r: 400, tipo: 'tierra'},
		{r: 300, tipo: 'agua'},
		{r: 220, tipo: 'tierra'},
		{r: 140, tipo: 'agua'},
		{r: 95, tipo: 'tierra'},
	];
	return (
		<Lienzo>
			<defs>
				<radialGradient id={id} cx="50%" cy="47%" r="70%">
					<stop offset={0} stopColor="#2bc6d6" />
					<stop offset={1} stopColor="#0a4f7c" />
				</radialGradient>
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{Array.from({length: 40}).map((_, i) => (
				<rect key={i} x={(random(`mx${i}`) * 1200 + f * 0.6) % 1200 - 60} y={random(`my${i}`) * 1920} width={60} height={4} rx={2} fill="rgba(255,255,255,0.35)" />
			))}
			<g transform={`translate(${cx} ${cy}) scale(${interpolate(revelar, [0, 1], [0.6, 1])}) translate(${-cx} ${-cy})`} opacity={interpolate(revelar, [0, 0.15], [0, 1], {extrapolateRight: 'clamp'})}>
				{anillos.map((a, i) => {
					const visible = interpolate(revelar, [i / anillos.length, (i + 1) / anillos.length], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
					return (
						<circle
							key={i}
							cx={cx}
							cy={cy}
							r={a.r}
							fill={a.tipo === 'tierra' ? (i === 0 ? '#9ccf6a' : '#e9dcb8') : '#33c9d6'}
							stroke={LINEA}
							strokeWidth={4}
							opacity={visible}
						/>
					);
				})}
				{/* edificios diminutos sobre los anillos de tierra */}
				{[
					[430, 470],
					[240, 290],
				].map(([r1, r2], k) =>
					Array.from({length: k === 0 ? 46 : 26}).map((_, i) => {
						const n = k === 0 ? 46 : 26;
						const a = (i / n) * Math.PI * 2;
						const r = (r1 + r2) / 2 - 10;
						const x = cx + Math.cos(a) * r;
						const y = cy + Math.sin(a) * r;
						return (
							<g key={`${k}-${i}`} transform={`rotate(${(a * 180) / Math.PI + 90} ${x} ${y})`} opacity={revelar}>
								<rect x={x - 14} y={y - 10} width={28} height={20} fill={MARMOL} stroke={LINEA} strokeWidth={2} />
								<rect x={x - 14} y={y - 10} width={28} height={7} fill={ORO} />
							</g>
						);
					}),
				)}
				{/* puentes y canal de entrada */}
				{[0, 90, 180, 270].map((a) => (
					<rect key={a} x={cx - 14} y={cy - 560} width={28} height={470} fill="#d8c7a3" stroke={LINEA} strokeWidth={3} transform={`rotate(${a} ${cx} ${cy})`} opacity={revelar} />
				))}
				<rect x={cx - 40} y={cy + 140} width={80} height={900} fill="#33c9d6" stroke={LINEA} strokeWidth={3} opacity={revelar} />
				{/* templo central visto desde arriba */}
				<circle cx={cx} cy={cy} r={70} fill={ORO} stroke={LINEA} strokeWidth={4} />
				<circle cx={cx} cy={cy} r={44} fill="#ffd978" stroke={LINEA} strokeWidth={3} />
				<circle cx={cx - 14} cy={cy - 14} r={14} fill="#fff6c8" />
			</g>
		</Lienzo>
	);
};

/** Terraza de palacio frente al mar al atardecer. */
export const EscTerraza: React.FC = () => {
	const id = useId('atard');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#ff9a5c', 0], ['#ffc77a', 0.45], ['#ffe9b8', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={980} fill={`url(#${id})`} />
			<Sol x={560} y={860} r={110} color="#fff2b8" halo="rgba(255,210,120,0.35)" />
			<Nubes y={300} n={4} vel={0.3} color="#ffd6b0" sombra="#f0a982" semilla="t" />
			<Agua y={940} alto={420} arriba="#5fc8d8" abajo="#0f6f93" brillo="rgba(255,236,170,0.8)" />
			{/* reflejo del sol */}
			<path d="M 520 950 L 600 950 L 680 1360 L 440 1360 Z" fill="rgba(255,235,160,0.35)" />
			{/* balaustrada */}
			<rect x={0} y={1270} width={1080} height={36} fill={MARMOL} stroke={LINEA} strokeWidth={4} />
			{Array.from({length: 14}).map((_, i) => (
				<path key={i} d={`M ${30 + i * 78} 1306 q -18 40 0 70 q 18 30 0 64 h 36 q -18 -34 0 -64 q 18 -30 0 -70 Z`} fill={MARMOL} stroke={LINEA} strokeWidth={3} />
			))}
			<rect x={0} y={1440} width={1080} height={30} fill={MARMOL} stroke={LINEA} strokeWidth={4} />
			{/* suelo */}
			<rect x={0} y={1470} width={1080} height={460} fill="#efe3c9" />
			{Array.from({length: 6}).map((_, i) => (
				<line key={i} x1={0} y1={1520 + i * i * 16} x2={1080} y2={1520 + i * i * 16} stroke="#d8c7a3" strokeWidth={3} />
			))}
			{/* columnas que enmarcan */}
			<Columna x={-40} y={60} w={140} h={1420} />
			<Columna x={980} y={60} w={140} h={1420} />
			<rect x={-20} y={0} width={1120} height={80} fill={ORO} stroke={LINEA} strokeWidth={4} />
			{/* mesa con fruta */}
			<g transform="translate(830 1600)">
				<rect x={-130} y={0} width={260} height={30} rx={8} fill={ORO} stroke={LINEA} strokeWidth={4} />
				<rect x={-110} y={30} width={20} height={110} fill={ORO_S} stroke={LINEA} strokeWidth={3} />
				<rect x={90} y={30} width={20} height={110} fill={ORO_S} stroke={LINEA} strokeWidth={3} />
				<path d="M -90 0 Q -60 -60 0 -60 Q 60 -60 90 0 Z" fill="#8a5a32" stroke={LINEA} strokeWidth={4} />
				{[
					[-40, -70, '#e3262e'],
					[0, -86, '#7a3fa0'],
					[40, -70, '#f2a531'],
					[-15, -50, '#6fb64a'],
				].map(([x, y, c], i) => (
					<circle key={i} cx={x as number} cy={y as number} r={24} fill={c as string} stroke={LINEA} strokeWidth={3} />
				))}
			</g>
		</Lienzo>
	);
};

/** Palacio gigantesco visto desde abajo. */
export const EscPalacio: React.FC = () => {
	const id = useId('cielo');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#3fb8ff', 0], ['#a6e1ff', 0.7], ['#fff4cf', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			<Nubes y={220} n={3} vel={0.4} semilla="p" />
			{/* cúpula */}
			<path d="M 260 470 A 280 280 0 0 1 820 470 Z" fill={ORO} stroke={LINEA} strokeWidth={5} />
			<path d="M 600 210 A 280 280 0 0 1 820 470 L 690 470 Z" fill={ORO_S} opacity={0.6} />
			<rect x={530} y={150} width={20} height={60} fill={ORO} stroke={LINEA} strokeWidth={4} />
			{/* frontón */}
			<path d="M 60 760 L 540 470 L 1020 760 Z" fill={MARMOL} stroke={LINEA} strokeWidth={5} strokeLinejoin="round" />
			<path d="M 160 730 L 540 520 L 920 730 Z" fill={ORO} stroke={LINEA} strokeWidth={4} strokeLinejoin="round" />
			<rect x={40} y={760} width={1000} height={60} fill={ORO} stroke={LINEA} strokeWidth={5} />
			{/* columnata con perspectiva */}
			{Array.from({length: 8}).map((_, i) => {
				const x = 70 + i * 122;
				return <Columna key={i} x={x} y={820} w={76} h={780} />;
			})}
			<rect x={0} y={1600} width={1080} height={40} fill={MARMOL} stroke={LINEA} strokeWidth={4} />
			{/* escalinata */}
			{Array.from({length: 7}).map((_, i) => (
				<rect key={i} x={-40 - i * 20} y={1640 + i * 44} width={1160 + i * 40} height={44} fill={i % 2 ? MARMOL : '#ece2cc'} stroke={LINEA} strokeWidth={3} />
			))}
		</Lienzo>
	);
};

/** Bóveda del tesoro. */
export const EscTesoro: React.FC = () => {
	const f = useCurrentFrame();
	const id = useId('boveda');
	const monton = (cx: number, base: number, w: number, h: number, semilla: string) => (
		<g>
			<path d={`M ${cx - w / 2} ${base} Q ${cx} ${base - h * 2} ${cx + w / 2} ${base} Z`} fill={ORO} stroke={LINEA} strokeWidth={4} />
			{Array.from({length: Math.round(w / 12)}).map((_, i) => {
				const t = random(`${semilla}t${i}`);
				const x = cx - w / 2 + t * w;
				const alto = (1 - Math.pow((t - 0.5) * 2, 2)) * h;
				const y = base - random(`${semilla}y${i}`) * alto;
				return <ellipse key={i} cx={x} cy={y} rx={22} ry={9} fill={random(`${semilla}c${i}`) > 0.5 ? '#ffd978' : ORO_S} stroke={LINEA} strokeWidth={2} />;
			})}
		</g>
	);
	return (
		<Lienzo>
			<defs>
				<radialGradient id={id} cx="50%" cy="40%" r="75%">
					<stop offset={0} stopColor="#9a5f1c" />
					<stop offset={1} stopColor="#2a1406" />
				</radialGradient>
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{[180, 540, 900].map((x) => (
				<path key={x} d={`M ${x - 150} 1100 L ${x - 150} 520 A 150 150 0 0 1 ${x + 150} 520 L ${x + 150} 1100 Z`} fill="#4a2a0e" stroke={LINEA} strokeWidth={5} />
			))}
			<rect x={0} y={1100} width={1080} height={820} fill="#5a3412" />
			{monton(220, 1500, 520, 260, 'a')}
			{monton(860, 1460, 480, 240, 'b')}
			{monton(540, 1780, 900, 380, 'c')}
			{/* cofres */}
			{[
				[160, 1640],
				[900, 1620],
			].map(([x, y], i) => (
				<g key={i} transform={`translate(${x} ${y})`}>
					<rect x={-90} y={-60} width={180} height={110} rx={10} fill="#8a4f1c" stroke={LINEA} strokeWidth={5} />
					<path d="M -90 -60 Q 0 -140 90 -60 Z" fill="#9a5c24" stroke={LINEA} strokeWidth={5} />
					<rect x={-14} y={-50} width={28} height={36} rx={4} fill={ORO} stroke={LINEA} strokeWidth={3} />
				</g>
			))}
			{/* destellos */}
			{Array.from({length: 14}).map((_, i) => {
				const x = random(`gx${i}`) * 1000 + 40;
				const y = 1250 + random(`gy${i}`) * 560;
				const s = Math.max(0, Math.sin(f / 6 + i * 1.7));
				return <path key={i} d={`M ${x} ${y - 26 * s} L ${x + 6 * s} ${y} L ${x} ${y + 26 * s} L ${x - 6 * s} ${y} Z M ${x - 26 * s} ${y} L ${x} ${y + 6 * s} L ${x + 26 * s} ${y} L ${x} ${y - 6 * s} Z`} fill="#fffbe0" />;
			})}
		</Lienzo>
	);
};

/** Gran plaza con la estatua del dios del mar. */
export const EscPlaza: React.FC<{gris?: number}> = ({gris = 0}) => {
	const f = useCurrentFrame();
	const id = useId('cielo');
	return (
		<div style={{position: 'absolute', inset: 0, filter: gris ? `grayscale(${gris}) brightness(${1 - gris * 0.15})` : undefined}}>
			<Lienzo>
				<defs>
					<Degradado id={id} colores={[['#4cc0ff', 0], ['#b6e8ff', 0.6], ['#fff4cf', 1]]} />
				</defs>
				<rect x={0} y={0} width={1080} height={1100} fill={`url(#${id})`} />
				<Nubes y={260} n={3} vel={0.4} semilla="pz" />
				{/* columnatas laterales */}
				{Array.from({length: 5}).map((_, i) => (
					<Columna key={`l${i}`} x={-20 + i * 70} y={620 + i * 30} w={44 - i * 3} h={480 - i * 30} />
				))}
				{Array.from({length: 5}).map((_, i) => (
					<Columna key={`r${i}`} x={1056 - i * 70 - 44} y={620 + i * 30} w={44 - i * 3} h={480 - i * 30} />
				))}
				{/* estatua del dios del mar */}
				<g transform="translate(540 1060)">
					<rect x={-120} y={-80} width={240} height={80} fill={MARMOL} stroke={LINEA} strokeWidth={4} />
					<path d="M -60 -80 L -40 -300 Q 0 -330 40 -300 L 60 -80 Z" fill={ORO} stroke={LINEA} strokeWidth={4} />
					<circle cx={0} cy={-350} r={56} fill={ORO} stroke={LINEA} strokeWidth={4} />
					<path d="M -40 -330 Q 0 -260 40 -330 Q 0 -300 -40 -330 Z" fill={ORO_S} />
					<line x1={90} y1={-60} x2={110} y2={-460} stroke={LINEA} strokeWidth={10} />
					<line x1={90} y1={-60} x2={110} y2={-460} stroke={ORO} strokeWidth={5} />
					<path d="M 80 -440 L 82 -490 M 110 -460 L 112 -520 M 140 -440 L 142 -490 M 80 -440 Q 110 -420 140 -440" stroke={ORO} strokeWidth={8} fill="none" strokeLinecap="round" />
					<path d="M 40 -260 L 100 -180" stroke={ORO} strokeWidth={22} strokeLinecap="round" />
				</g>
				{/* suelo en perspectiva */}
				<rect x={0} y={1060} width={1080} height={900} fill="#efe3c9" />
				{Array.from({length: 9}).map((_, i) => {
					const t = (i + 1) / 10;
					return <line key={i} x1={0} y1={1060 + 860 * t * t} x2={1080} y2={1060 + 860 * t * t} stroke="#d8c7a3" strokeWidth={3} />;
				})}
				{Array.from({length: 11}).map((_, i) => (
					<line key={`v${i}`} x1={540} y1={1060} x2={-1000 + i * 308} y2={1920} stroke="#d8c7a3" strokeWidth={3} />
				))}
				{/* fuentes */}
				{[200, 880].map((x) => (
					<g key={x}>
						<ellipse cx={x} cy={1230} rx={110} ry={30} fill={TURQ} stroke={LINEA} strokeWidth={4} />
						{[-1, 0, 1].map((k) => (
							<path key={k} d={`M ${x} 1200 Q ${x + k * 40} ${1100 - Math.abs(Math.sin(f / 6)) * 10} ${x + k * 80} 1220`} stroke="#bff3ff" strokeWidth={8} fill="none" strokeLinecap="round" />
						))}
					</g>
				))}
			</Lienzo>
		</div>
	);
};

/** Cielo (soleado o de tormenta) con mar y la ciudad en el horizonte. */
export const EscCielo: React.FC<{tormenta?: boolean; rayos?: number[]}> = ({tormenta = false, rayos = []}) => {
	const f = useCurrentFrame();
	const id = useId('cielo');
	const flash = rayos.reduce((acc, r) => acc + (f >= r && f < r + 6 ? 1 - (f - r) / 6 : 0), 0);
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={tormenta ? [['#140f2a', 0], ['#2f2856', 0.55], ['#4b4470', 1]] : [['#3fb8ff', 0], ['#9fdcff', 0.6], ['#e6f6ff', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1500} fill={`url(#${id})`} />
			{tormenta ? (
				<g>
					{Array.from({length: 7}).map((_, i) => {
						const x = ((i * 190 + f * (1 + i * 0.2)) % 1400) - 160;
						return <ellipse key={i} cx={x} cy={180 + (i % 3) * 140} rx={260} ry={90} fill={i % 2 ? '#2a2347' : '#383060'} />;
					})}
					{rayos.map((r) =>
						f >= r && f < r + 8 ? (
							<path key={r} d={`M ${300 + (r % 5) * 110} 0 L ${260 + (r % 5) * 110} 320 L ${340 + (r % 5) * 110} 320 L ${280 + (r % 5) * 110} 700`} stroke="#fff7c8" strokeWidth={14} fill="none" strokeLinejoin="round" />
						) : null,
					)}
				</g>
			) : (
				<Nubes y={500} n={6} vel={0.5} escala={1.3} semilla="c" />
			)}
			<Agua y={1500} alto={420} arriba={tormenta ? '#2b3d63' : '#4fc6dc'} abajo={tormenta ? '#121b33' : '#0d6f93'} />
			{/* la ciudad en el horizonte */}
			<g transform="translate(540 1500) scale(0.35)">
				{[-600, -400, -200, 200, 400, 600].map((x, i) => (
					<Edificio key={x} x={x - 80} base={0} w={160} h={160 + (i % 3) * 60} techo={i % 2 ? 'cupula' : 'triangulo'} oscuro={tormenta ? 0.45 : 0} />
				))}
				<Templo cx={0} base={0} s={0.8} />
				{tormenta && <rect x={-760} y={-560} width={1520} height={560} fill="#0b0d26" opacity={0.5} />}
			</g>
			{flash > 0 && <rect x={0} y={0} width={1080} height={1920} fill="#ffffff" opacity={flash * 0.55} />}
		</Lienzo>
	);
};

/** Ola gigante que se levanta sobre la ciudad. `subida` 0..1 */
export const EscTsunami: React.FC<{subida: number}> = ({subida}) => {
	const f = useCurrentFrame();
	const id = useId('ola');
	const idc = useId('cielo');
	const top = interpolate(subida, [0, 1], [1500, 260]);
	const curva = `M -100 1920 L -100 ${top + 260} Q 160 ${top - 40} 520 ${top} Q 860 ${top + 20} 1020 ${top + 220} Q 1080 ${top + 340} 980 ${top + 360} Q 900 ${top + 330} 930 ${top + 260} Q 960 ${top + 200} 880 ${top + 170} Q 760 ${top + 160} 760 ${top + 300} L 1180 ${top + 420} L 1180 1920 Z`;
	return (
		<Lienzo>
			<defs>
				<Degradado id={idc} colores={[['#1a1733', 0], ['#3f3a63', 0.6], ['#8b7f8f', 1]]} />
				<Degradado id={id} colores={[['#4fd0d8', 0], ['#127c99', 0.4], ['#06334f', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${idc})`} />
			{/* ciudad abajo */}
			{[-20, 160, 340, 560, 760, 920].map((x, i) => (
				<Edificio key={x} x={x} base={1700} w={170} h={220 + (i % 3) * 80} techo={i % 2 ? 'cupula' : 'triangulo'} oscuro={0.25} />
			))}
			<Templo cx={480} base={1700} s={0.5} />
			<rect x={0} y={1700} width={1080} height={220} fill="#cbb994" />
			{/* la ola */}
			<path d={curva} fill={`url(#${id})`} stroke={LINEA} strokeWidth={5} />
			{/* espuma de la cresta */}
			{Array.from({length: 18}).map((_, i) => {
				const t = i / 17;
				const x = -60 + t * 1080;
				const y = top + 40 - Math.sin(t * Math.PI) * 60 + (t > 0.85 ? (t - 0.85) * 1200 : 0);
				return <circle key={i} cx={x} cy={y + Math.sin(f / 3 + i) * 8} r={34 + (i % 3) * 10} fill="#eafcff" stroke={LINEA} strokeWidth={3} />;
			})}
			{Array.from({length: 12}).map((_, i) => (
				<path key={`s${i}`} d={`M ${random(`sx${i}`) * 1080} ${top + 300 + random(`sy${i}`) * 900} q 30 -20 60 0`} stroke="rgba(220,250,255,0.6)" strokeWidth={6} fill="none" />
			))}
		</Lienzo>
	);
};

/** De noche: las últimas torres de la ciudad se hunden en el mar. `hundir` 0..1 */
export const EscNoche: React.FC<{hundir: number}> = ({hundir}) => {
	const f = useCurrentFrame();
	const id = useId('noche');
	const baja = hundir * 620;
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#050a1c', 0], ['#14234a', 0.65], ['#2a3a66', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{Array.from({length: 60}).map((_, i) => (
				<circle key={i} cx={random(`ex${i}`) * 1080} cy={random(`ey${i}`) * 900} r={1.5 + random(`er${i}`) * 2.5} fill="#ffffff" opacity={0.4 + 0.6 * Math.abs(Math.sin(f / 15 + i))} />
			))}
			<Sol x={760} y={360} r={110} color="#f4f1e0" halo="rgba(220,230,255,0.18)" />
			<g transform={`translate(0 ${baja})`}>
				<Templo cx={540} base={1300} s={0.9} />
				<Edificio x={140} base={1300} w={200} h={420} techo="cupula" oscuro={0.3} />
				<Edificio x={760} base={1300} w={200} h={360} techo="triangulo" oscuro={0.3} />
			</g>
			<Agua y={1180} alto={740} arriba="#1d3a66" abajo="#060f22" brillo="rgba(220,230,255,0.55)" />
			{/* reflejo de la luna */}
			<path d={`M 720 1190 L 800 1190 L 860 1920 L 660 1920 Z`} fill="rgba(240,240,220,0.12)" />
			{Array.from({length: 10}).map((_, i) => {
				const l = (f * 2 + i * 37) % 300;
				return <circle key={i} cx={400 + random(`bx${i}`) * 300} cy={1200 - l * 0.6} r={6 + (i % 3) * 3} fill="none" stroke="rgba(200,230,255,0.7)" strokeWidth={3} opacity={hundir > 0.2 ? 1 - l / 300 : 0} />;
			})}
		</Lienzo>
	);
};

/** Ruinas bajo el mar, con rayos de luz y burbujas. */
export const EscSubmarino: React.FC<{oscuro?: number}> = ({oscuro = 0}) => {
	const f = useCurrentFrame();
	const id = useId('mar');
	return (
		<div style={{position: 'absolute', inset: 0, filter: oscuro ? `brightness(${1 - oscuro})` : undefined}}>
			<Lienzo>
				<defs>
					<Degradado id={id} colores={[['#1aa7c4', 0], ['#0b5f86', 0.5], ['#031b36', 1]]} />
				</defs>
				<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
				{/* rayos de luz */}
				{[0, 1, 2, 3, 4].map((i) => (
					<path key={i} d={`M ${120 + i * 210} -20 L ${200 + i * 210} -20 L ${360 + i * 200} 1400 L ${160 + i * 200} 1400 Z`} fill="#bff3ff" opacity={0.08 + 0.06 * Math.sin(f / 18 + i)} />
				))}
				{/* fondo lejano de ruinas */}
				<g opacity={0.45}>
					<Templo cx={540} base={1240} s={0.55} />
				</g>
				<rect x={0} y={1400} width={1080} height={520} fill="#c9b27a" />
				<path d="M 0 1400 Q 270 1350 540 1400 T 1080 1390 L 1080 1460 L 0 1460 Z" fill="#b89d63" />
				{/* columnas rotas y caídas */}
				<Columna x={90} y={980} w={90} h={460} color="#d9e6dc" sombra="#9fbcae" />
				<rect x={70} y={960} width={130} height={30} fill="#3f7f6a" opacity={0.8} />
				<Columna x={860} y={1100} w={90} h={340} color="#d9e6dc" sombra="#9fbcae" rot={-8} />
				<g transform="rotate(-80 520 1500)">
					<Columna x={470} y={1200} w={90} h={520} color="#d9e6dc" sombra="#9fbcae" />
				</g>
				{/* cabeza de estatua */}
				<g transform="translate(300 1520) rotate(-18)">
					<circle cx={0} cy={0} r={90} fill="#e6c27a" stroke={LINEA} strokeWidth={5} />
					<path d="M -40 -10 L -10 -10 M 15 -10 L 45 -10" stroke={LINEA} strokeWidth={8} strokeLinecap="round" />
					<path d="M -20 40 Q 0 52 22 40" stroke={LINEA} strokeWidth={6} fill="none" />
					<path d="M -88 -20 Q -90 -100 0 -104 Q 90 -100 88 -20 Q 60 -70 0 -66 Q -60 -70 -88 -20 Z" fill="#d6ad62" stroke={LINEA} strokeWidth={5} />
					<path d="M -70 30 Q -60 120 0 130 Q 60 120 70 30 Q 40 70 0 66 Q -40 70 -70 30 Z" fill="#d6ad62" stroke={LINEA} strokeWidth={5} />
				</g>
				{/* algas */}
				{[60, 180, 700, 980, 1040].map((x, i) => (
					<path key={x} d={`M ${x} 1920 Q ${x + Math.sin(f / 12 + i) * 30} 1700 ${x - 10} 1560 Q ${x + 20 + Math.sin(f / 10 + i) * 30} 1440 ${x} 1380`} stroke="#2f9d6a" strokeWidth={22} fill="none" strokeLinecap="round" />
				))}
				{/* burbujas */}
				{Array.from({length: 18}).map((_, i) => {
					const v = 2 + random(`bv${i}`) * 3;
					const y = 1920 - ((f * v + random(`by${i}`) * 2000) % 2000);
					return <circle key={i} cx={random(`bx${i}`) * 1080 + Math.sin(f / 10 + i) * 12} cy={y} r={5 + random(`br${i}`) * 10} fill="none" stroke="rgba(220,250,255,0.75)" strokeWidth={3} />;
				})}
				{/* peces */}
				{[0, 1, 2].map((i) => {
					const x = ((f * (2 + i) + i * 400) % 1400) - 160;
					return (
						<g key={i} transform={`translate(${x} ${500 + i * 230})`}>
							<ellipse cx={0} cy={0} rx={40} ry={18} fill={['#ff9a3c', '#ffd84a', '#7fe0ff'][i]} stroke={LINEA} strokeWidth={3} />
							<path d="M -38 0 L -66 -18 L -66 18 Z" fill={['#ff9a3c', '#ffd84a', '#7fe0ff'][i]} stroke={LINEA} strokeWidth={3} />
							<circle cx={20} cy={-4} r={4} fill={LINEA} />
						</g>
					);
				})}
			</Lienzo>
		</div>
	);
};

/** Estudio de Platón en Atenas. */
export const EscAtenas: React.FC = () => {
	const f = useCurrentFrame();
	const id = useId('pared');
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#f0d3a3', 0], ['#e2b981', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{/* ventana con la Acrópolis */}
			<rect x={240} y={260} width={600} height={620} fill="#8fd3ff" stroke={LINEA} strokeWidth={8} />
			<rect x={240} y={700} width={600} height={180} fill="#c9b27a" />
			<path d="M 240 760 Q 540 600 840 760 L 840 880 L 240 880 Z" fill="#b89d63" stroke={LINEA} strokeWidth={4} />
			<g transform="translate(540 650)">
				<path d="M -160 0 L 0 -60 L 160 0 Z" fill={MARMOL} stroke={LINEA} strokeWidth={4} />
				{Array.from({length: 8}).map((_, i) => (
					<rect key={i} x={-150 + i * 40} y={0} width={18} height={70} fill={MARMOL} stroke={LINEA} strokeWidth={3} />
				))}
				<rect x={-165} y={70} width={330} height={16} fill={MARMOL} stroke={LINEA} strokeWidth={3} />
			</g>
			<Nube x={420} y={360} s={0.6} />
			<rect x={220} y={240} width={640} height={40} fill="#a0703c" stroke={LINEA} strokeWidth={5} />
			{/* columnas del cuarto */}
			<Columna x={30} y={120} w={120} h={1250} color="#f6ead2" sombra="#d9c39a" />
			<Columna x={930} y={120} w={120} h={1250} color="#f6ead2" sombra="#d9c39a" />
			{/* estante con pergaminos */}
			<rect x={250} y={960} width={580} height={22} fill="#8a5a32" stroke={LINEA} strokeWidth={4} />
			{Array.from({length: 7}).map((_, i) => (
				<g key={i}>
					<rect x={270 + i * 78} y={900} width={60} height={60} rx={28} fill="#f3e3bd" stroke={LINEA} strokeWidth={4} />
					<circle cx={300 + i * 78} cy={930} r={10} fill="#c9a86a" stroke={LINEA} strokeWidth={3} />
				</g>
			))}
			{/* suelo */}
			<rect x={0} y={1370} width={1080} height={560} fill="#b98a55" />
			{Array.from({length: 6}).map((_, i) => (
				<line key={i} x1={0} y1={1400 + i * i * 18} x2={1080} y2={1400 + i * i * 18} stroke="#a27443" strokeWidth={4} />
			))}
			{/* lámpara de aceite */}
			<g transform="translate(880 1330)">
				<path d="M -60 0 Q 0 40 60 0 L 40 -20 L -40 -20 Z" fill={ORO} stroke={LINEA} strokeWidth={4} />
				<path d={`M 52 -24 Q ${62 + Math.sin(f / 3) * 6} -70 ${56 + Math.sin(f / 2) * 4} -96 Q 44 -60 52 -24 Z`} fill="#ffb02e" />
				<path d={`M 52 -30 Q ${58 + Math.sin(f / 3) * 4} -60 ${54 + Math.sin(f / 2) * 3} -76 Q 48 -52 52 -30 Z`} fill="#fff1a8" />
				<circle cx={52} cy={-60} r={120} fill="rgba(255,200,90,0.12)" />
			</g>
		</Lienzo>
	);
};

/** Fondo del mar profundo: un submarino de investigación busca... y no encuentra nada. */
export const EscProfundo: React.FC = () => {
	const f = useCurrentFrame();
	const id = useId('prof');
	const barrido = Math.sin(f / 20) * 18;
	return (
		<Lienzo>
			<defs>
				<Degradado id={id} colores={[['#0a2f55', 0], ['#04152b', 0.7], ['#020a16', 1]]} />
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{Array.from({length: 40}).map((_, i) => (
				<circle key={i} cx={random(`px${i}`) * 1080} cy={(random(`py${i}`) * 1920 + f * 0.4) % 1920} r={2 + random(`pr${i}`) * 2} fill="rgba(180,220,255,0.35)" />
			))}
			{/* suelo de arena vacío */}
			<path d="M 0 1480 Q 300 1420 600 1480 T 1080 1470 L 1080 1920 L 0 1920 Z" fill="#3a3a52" />
			<path d="M 0 1560 Q 320 1520 640 1570 T 1080 1560 L 1080 1920 L 0 1920 Z" fill="#2c2c42" />
			{/* anillos de sonar */}
			{[0, 1, 2].map((k) => {
				const l = (f + k * 25) % 75;
				return <circle key={k} cx={560} cy={760} r={60 + l * 9} fill="none" stroke="rgba(110,255,190,0.6)" strokeWidth={5} opacity={1 - l / 75} />;
			})}
			{/* cono de luz */}
			<path d={`M 640 800 L ${900 + barrido * 10} 1500 L ${380 + barrido * 10} 1500 Z`} fill="rgba(255,250,200,0.16)" />
			{/* submarino */}
			<g transform={`translate(560 ${760 + Math.sin(f / 15) * 10}) rotate(${barrido * 0.3})`}>
				<ellipse cx={0} cy={0} rx={190} ry={95} fill="#ffd23a" stroke={LINEA} strokeWidth={7} />
				<rect x={-60} y={-150} width={120} height={70} rx={20} fill="#ffd23a" stroke={LINEA} strokeWidth={7} />
				<line x1={20} y1={-150} x2={20} y2={-200} stroke={LINEA} strokeWidth={7} />
				{[-90, -20, 50].map((x) => (
					<circle key={x} cx={x} cy={0} r={28} fill="#8fd3ff" stroke={LINEA} strokeWidth={6} />
				))}
				<path d="M -190 0 L -250 -50 L -250 50 Z" fill="#f2a531" stroke={LINEA} strokeWidth={6} strokeLinejoin="round" />
				<circle cx={175} cy={30} r={22} fill="#fffbd0" stroke={LINEA} strokeWidth={5} />
			</g>
		</Lienzo>
	);
};

/** Libro antiguo abierto sobre un escritorio, con vela. */
export const EscLibro: React.FC = () => {
	const f = useCurrentFrame();
	const id = useId('mesa');
	return (
		<Lienzo>
			<defs>
				<radialGradient id={id} cx="50%" cy="45%" r="75%">
					<stop offset={0} stopColor="#6b3f1e" />
					<stop offset={1} stopColor="#1f0f05" />
				</radialGradient>
			</defs>
			<rect x={0} y={0} width={1080} height={1920} fill={`url(#${id})`} />
			{/* libro */}
			<path d="M 60 470 L 530 520 L 530 1560 L 60 1500 Z" fill="#7a2f1f" stroke={LINEA} strokeWidth={6} />
			<path d="M 1020 470 L 550 520 L 550 1560 L 1020 1500 Z" fill="#7a2f1f" stroke={LINEA} strokeWidth={6} />
			<path d="M 90 450 Q 320 420 540 500 L 540 1530 Q 320 1450 90 1480 Z" fill="#f3e3bd" stroke={LINEA} strokeWidth={5} />
			<path d="M 990 450 Q 760 420 540 500 L 540 1530 Q 760 1450 990 1480 Z" fill="#efdcb0" stroke={LINEA} strokeWidth={5} />
			<line x1={540} y1={500} x2={540} y2={1530} stroke="#c9a86a" strokeWidth={8} />
			{Array.from({length: 14}).map((_, i) => (
				<line key={i} x1={600} y1={600 + i * 58} x2={930} y2={590 + i * 58} stroke="rgba(90,60,30,0.45)" strokeWidth={8} strokeLinecap="round" />
			))}
			{/* vela */}
			<g transform="translate(920 300)">
				<rect x={-34} y={0} width={68} height={140} rx={8} fill="#f6eedd" stroke={LINEA} strokeWidth={5} />
				<path d={`M 0 0 Q ${16 + Math.sin(f / 3) * 6} -50 ${Math.sin(f / 2) * 6} -86 Q -14 -46 0 0 Z`} fill="#ffb02e" />
				<path d={`M 0 -6 Q ${8 + Math.sin(f / 3) * 4} -36 ${Math.sin(f / 2) * 4} -60 Q -6 -34 0 -6 Z`} fill="#fff1a8" />
				<circle cx={0} cy={-40} r={200} fill="rgba(255,190,80,0.1)" />
			</g>
		</Lienzo>
	);
};
