import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { Icono as IconoT } from "../datos/edicion";
import { COLOR } from "../estilo";

// Siluetas planas con degradado y resplandor, como los iconos de la referencia (estilo.md §5),
// en el verde del logo. Lienzo de 120 × 140.
const FORMAS: Record<IconoT, React.ReactNode> = {
  // Brote del logo: tallo, dos hojas y yema.
  brote: (
    <>
      <rect x="55" y="52" width="10" height="82" rx="5" />
      <path d="M60 96 C40 96 20 84 16 58 C40 54 60 68 60 96 Z" />
      <path d="M60 86 C80 86 100 74 104 48 C80 44 60 58 60 86 Z" />
      <path d="M60 50 C48 40 46 22 60 8 C74 22 72 40 60 50 Z" />
    </>
  ),
  // Sello de certificación: roseta con check y cintas.
  sello: (
    <>
      <path d="M38 86 L28 136 L50 122 L60 138 L60 92 Z" />
      <path d="M82 86 L92 136 L70 122 L60 138 L60 92 Z" />
      <path
        fillRule="evenodd"
        d="M60 4 L72 12 L86 10 L92 24 L106 30 L104 44 L112 56 L104 68 L106 82 L92 88 L86 102 L72 100 L60 108 L48 100 L34 102 L28 88 L14 82 L16 68 L8 56 L16 44 L14 30 L28 24 L34 10 L48 12 Z M52 74 L84 42 L76 34 L52 58 L42 48 L34 56 Z"
      />
    </>
  ),
  // Escudo con check: garantía.
  escudo: (
    <path
      fillRule="evenodd"
      d="M60 6 L108 24 V66 C108 98 88 122 60 134 C32 122 12 98 12 66 V24 Z M52 92 L90 54 L80 44 L52 72 L40 60 L30 70 Z"
    />
  ),
  // Hoja con cruz: sanidad.
  salud: (
    <path
      fillRule="evenodd"
      d="M60 6 C96 30 112 60 106 92 C100 120 80 134 60 134 C40 134 20 120 14 92 C8 60 24 30 60 6 Z M50 52 H70 V70 H88 V90 H70 V108 H50 V90 H32 V70 H50 Z"
    />
  ),
  // Barras ascendentes con flecha: rendimiento.
  grafico: (
    <>
      <rect x="10" y="96" width="24" height="38" rx="5" />
      <rect x="48" y="72" width="24" height="62" rx="5" />
      <rect x="86" y="46" width="24" height="88" rx="5" />
      <path d="M8 62 L50 34 L62 46 L92 18 L80 12 L112 4 L110 36 L102 26 L64 62 L52 50 L16 74 Z" />
    </>
  ),
};

/** Icono que entra con pop (escala 0 → 1,15 → 1 en 0,2 s). `t` en segundos desde el inicio del bloque. */
export const Icono: React.FC<{ icono: IconoT; t: number; tam?: number; style?: React.CSSProperties }> = ({
  icono,
  t,
  tam = 128,
  style,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = Math.round(t * fps);
  const id = `ak-ico-${icono}`;

  return (
    <svg
      viewBox="0 0 120 140"
      width={tam}
      height={(tam * 140) / 120}
      style={{
        position: "absolute",
        overflow: "visible",
        transformOrigin: "50% 100%",
        opacity: interpolate(frame, [f0, f0 + 2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        scale: interpolate(frame, [f0, f0 + 0.12 * fps, f0 + 0.2 * fps], [0, 1.15, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.quad),
        }),
        filter: "drop-shadow(0 0 16px rgba(77,195,81,0.6)) drop-shadow(0 4px 8px rgba(0,0,0,0.45))",
        ...style,
      }}
    >
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={COLOR.verdeClaro} />
          <stop offset="0.5" stopColor={COLOR.verdeVivo} />
          <stop offset="1" stopColor="#2C8A3A" />
        </linearGradient>
      </defs>
      <g fill={`url(#${id})`}>{FORMAS[icono]}</g>
    </svg>
  );
};
