import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { EscenaBarra as EscenaT, PalabraTL } from "../datos/edicion";
import { COLOR, DEGRADADO_DESTACADO, FUENTE } from "../estilo";

// Motion graphic a pantalla completa (estilo.md §7): una barra-cápsula dividida en 3 tramos,
// uno por beneficio. Cada tramo se enciende cuando la voz lo nombra y su rótulo se conecta
// con una flecha que se dibuja.

const fijar = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
/** "Nunca ocurre en esta escena" (interpolate no admite Infinity). */
const NUNCA = 1e6;

// Geometría de la barra (px en 1080 × 1920)
const X0 = 100;
const X1 = 980;
const YC = 845;
const ALTO = 96;
const Y0 = YC - ALTO / 2;
const Y1 = YC + ALTO / 2;
const LIMITES = [X0, X0 + (X1 - X0) / 3, X0 + (2 * (X1 - X0)) / 3, X1];
const CENTROS = [0, 1, 2].map((k) => (LIMITES[k] + LIMITES[k + 1]) / 2);

// Texto de los rótulos cuando ya están hechos al entrar en la escena.
const ROTULO_HECHO: Record<number, string[][]> = {
  1: [["Libre", "de"], ["malezas"]],
  2: [["Garantía"]],
  3: [["Sanidad", "y"], ["rendimiento"]],
};

// Colocación de cada rótulo y de su flecha (arriba-izquierda, abajo-centro, arriba-derecha).
const COLOCACION: Record<
  number,
  { alinear: "left" | "center" | "right"; x: number; y: number; flecha: string; punta: string }
> = {
  1: {
    alinear: "left",
    x: 292,
    y: 631,
    flecha: `M 278 631 Q ${CENTROS[0]} 631 ${CENTROS[0]} ${Y0 - 30}`,
    punta: `${CENTROS[0] - 10},${Y0 - 30} ${CENTROS[0] + 10},${Y0 - 30} ${CENTROS[0]},${Y0 - 12}`,
  },
  2: {
    alinear: "center",
    x: CENTROS[1],
    y: 1086,
    flecha: `M ${CENTROS[1]} 1042 L ${CENTROS[1]} ${Y1 + 30}`,
    punta: `${CENTROS[1] - 10},${Y1 + 30} ${CENTROS[1] + 10},${Y1 + 30} ${CENTROS[1]},${Y1 + 12}`,
  },
  3: {
    alinear: "right",
    x: 788,
    y: 631,
    flecha: `M 802 631 Q ${CENTROS[2]} 631 ${CENTROS[2]} ${Y0 - 30}`,
    punta: `${CENTROS[2] - 10},${Y0 - 30} ${CENTROS[2] + 10},${Y0 - 30} ${CENTROS[2]},${Y0 - 12}`,
  },
};

const TAM_ROTULO = 47;
const ALTO_LINEA_ROTULO = 54;

/** Rótulo naranja en negrita que entra palabra a palabra (o ya hecho si `lineas` no trae tiempos). */
const Rotulo: React.FC<{ tramo: number; lineas: PalabraTL[][]; hecho: boolean }> = ({ tramo, lineas, hecho }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const c = COLOCACION[tramo];
  const altoTotal = ALTO_LINEA_ROTULO * lineas.length;

  return (
    <div
      style={{
        position: "absolute",
        top: c.y - altoTotal / 2,
        ...(c.alinear === "left"
          ? { left: c.x }
          : c.alinear === "right"
            ? { right: 1080 - c.x }
            : { left: c.x, translate: "-50% 0" }),
        textAlign: c.alinear,
        fontFamily: FUENTE.fuerte,
        fontWeight: 700,
        fontSize: TAM_ROTULO,
        letterSpacing: "-0.03em",
        lineHeight: `${ALTO_LINEA_ROTULO}px`,
        whiteSpace: "nowrap",
      }}
    >
      {lineas.map((linea, k) => (
        <div key={k}>
          {linea.map((w, i) => {
            const f0 = Math.round(w.t * fps);
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  padding: "0.2em 0.06em 0.12em",
                  margin: `-0.2em ${i === linea.length - 1 ? "-0.06em" : "0.16em"} -0.12em -0.06em`,
                  backgroundImage: DEGRADADO_DESTACADO,
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  color: "transparent",
                  WebkitTextFillColor: "transparent",
                  filter: "drop-shadow(0 0 14px rgba(232,135,58,0.6))",
                  opacity: hecho ? 1 : interpolate(frame, [f0, f0 + 0.04 * fps], [0, 1], fijar),
                  scale: hecho
                    ? 1
                    : interpolate(frame, [f0, f0 + 0.12 * fps], [1.12, 1], {
                        ...fijar,
                        easing: Easing.out(Easing.cubic),
                      }),
                }}
              >
                {w.texto}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

export const EscenaBarra: React.FC<{ escena: EscenaT; idx: number }> = ({ escena, idx }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const id = `ak-barra-${idx}`;

  // ── Cámara: la 1.ª vez la barra se construye; después entra con zoom 2,6× → 1× ──
  const zoomEntrada = escena.construir
    ? 1
    : interpolate(t, [0, 0.32], [2.6, 1], { ...fijar, easing: Easing.out(Easing.cubic) });
  const desenfoque = escena.construir ? 0 : interpolate(t, [0, 0.2], [9, 0], fijar);
  const camara = zoomEntrada * (1 + 0.012 * t);

  const estirar = escena.construir
    ? interpolate(t, [0, 0.25], [0.45, 1], { ...fijar, easing: Easing.out(Easing.cubic) })
    : 1;
  const aparecer = interpolate(t, [0, 0.05], [0, 1], fijar);
  const divisores = escena.construir ? interpolate(t, [0.08, 0.26], [0, 1], fijar) : 1;
  const xBrillo = interpolate(t, [0.05, 0.7], [X0 - 320, X1 + 120], fijar);

  // ── Estado de cada tramo ──
  const tEncendido = (tramo: number) => {
    if (escena.tramosYaEncendidos.includes(tramo)) return -10;
    return escena.encender.find((e) => e.tramo === tramo)?.t ?? NUNCA;
  };
  const tPulso = (tramo: number) =>
    escena.pulsoFinal === undefined ? NUNCA : escena.pulsoFinal + (tramo - 1) * 0.16;
  const golpe = (t0: number) => interpolate(t, [t0, t0 + 0.09, t0 + 0.34], [0, 1, 0], fijar);
  const tNumero = (tramo: number) => (escena.construir ? [0.13, 0.23, 0.43][tramo - 1] : -10);

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse 80% 46% at 50% 44%, #1F5C40 0%, #153F2E 30%, ${COLOR.verdeOscuro} 62%, #050F0D 100%)`,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          transformOrigin: `${width / 2}px ${YC}px`,
          scale: camara,
          filter: desenfoque > 0.3 ? `blur(${desenfoque.toFixed(1)}px)` : undefined,
        }}
      >
        {/* Resplandor detrás de la barra */}
        <div
          style={{
            position: "absolute",
            left: 0,
            top: YC - 260,
            width,
            height: 520,
            background:
              "radial-gradient(ellipse 58% 34% at 50% 50%, rgba(230,144,87,0.3) 0%, rgba(230,144,87,0.1) 45%, rgba(230,144,87,0) 75%)",
            opacity: aparecer,
          }}
        />

        <svg width={width} height={height} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
          <defs>
            <clipPath id={`${id}-clip`}>
              <rect x={X0} y={Y0} width={X1 - X0} height={ALTO} rx={ALTO / 2} />
            </clipPath>
            <linearGradient id={`${id}-relleno`} gradientUnits="userSpaceOnUse" x1={X0} y1="0" x2={X1} y2="0">
              <stop offset="0" stopColor="#D9783F" />
              <stop offset="0.35" stopColor="#EFAE6E" />
              <stop offset="0.56" stopColor="#F6D9A6" />
              <stop offset="0.8" stopColor="#E88A4E" />
              <stop offset="1" stopColor="#D9783F" />
            </linearGradient>
            <linearGradient id={`${id}-brillo`} x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stopColor="#FFFFFF" stopOpacity="0" />
              <stop offset="0.5" stopColor="#FFFFFF" stopOpacity="0.9" />
              <stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
            </linearGradient>
          </defs>

          <g style={{ transformOrigin: `${width / 2}px ${YC}px`, scale: `${estirar} 1`, opacity: aparecer }}>
            {/* Fondo de la barra */}
            <rect x={X0} y={Y0} width={X1 - X0} height={ALTO} rx={ALTO / 2} fill="rgba(255,255,255,0.07)" />

            <g clipPath={`url(#${id}-clip)`}>
              {[1, 2, 3].map((tramo) => {
                const t0 = tEncendido(tramo);
                const lleno = interpolate(t, [t0, t0 + 0.28], [0, 1], { ...fijar, easing: Easing.out(Easing.cubic) });
                const x = LIMITES[tramo - 1];
                const ancho = LIMITES[tramo] - x;
                const destello = Math.max(golpe(t0), golpe(tPulso(tramo)));
                return (
                  <g key={tramo}>
                    <rect x={x} y={Y0} width={ancho * lleno} height={ALTO} fill={`url(#${id}-relleno)`} />
                    <rect x={x} y={Y0} width={ancho} height={ALTO} fill="#FFFFFF" opacity={destello * 0.55} />
                  </g>
                );
              })}
              {/* Brillo diagonal que recorre la barra al entrar */}
              <rect
                x={xBrillo}
                y={Y0 - 30}
                width={200}
                height={ALTO + 60}
                fill={`url(#${id}-brillo)`}
                transform={`skewX(-22)`}
                style={{ transformOrigin: `${xBrillo}px ${YC}px`, mixBlendMode: "screen" }}
                opacity={0.75}
              />
            </g>

            {/* Contorno con resplandor */}
            <rect
              x={X0}
              y={Y0}
              width={X1 - X0}
              height={ALTO}
              rx={ALTO / 2}
              fill="none"
              stroke="#FFF7EA"
              strokeWidth={3.5}
              style={{ filter: "drop-shadow(0 0 7px rgba(255,255,255,0.85))" }}
            />
            {/* Divisores */}
            {[1, 2].map((k) => (
              <line
                key={k}
                x1={LIMITES[k]}
                x2={LIMITES[k]}
                y1={YC - (ALTO / 2 + 34) * divisores}
                y2={YC + (ALTO / 2 + 34) * divisores}
                stroke="#FFFFFF"
                strokeWidth={3}
                strokeLinecap="round"
                opacity={divisores}
                style={{ filter: "drop-shadow(0 0 5px rgba(255,255,255,0.7))" }}
              />
            ))}
          </g>

          {/* Flechas que se dibujan */}
          {[1, 2, 3].map((tramo) => {
            const animado = escena.rotulos.find((r) => r.tramo === tramo);
            const hecho = escena.rotulosYaHechos.includes(tramo);
            if (!animado && !hecho) return null;
            const t0 = animado ? animado.tFlecha : -10;
            const trazo = interpolate(t, [t0, t0 + 0.3], [0, 1], { ...fijar, easing: Easing.out(Easing.quad) });
            return (
              <g key={tramo} style={{ filter: "drop-shadow(0 0 4px rgba(255,255,255,0.5))" }}>
                <path
                  d={COLOCACION[tramo].flecha}
                  pathLength={1}
                  fill="none"
                  stroke="#FFFFFF"
                  strokeWidth={3.5}
                  strokeLinecap="round"
                  strokeDasharray="1"
                  strokeDashoffset={1 - trazo}
                  opacity={trazo > 0 ? 1 : 0}
                />
                <polygon
                  points={COLOCACION[tramo].punta}
                  fill="#FFFFFF"
                  opacity={interpolate(trazo, [0.85, 1], [0, 1], fijar)}
                />
              </g>
            );
          })}
        </svg>

        {/* Números de cada tramo */}
        {[1, 2, 3].map((tramo) => {
          const encendido = t >= tEncendido(tramo);
          const fN = Math.round(tNumero(tramo) * fps);
          const pop = Math.max(golpe(tEncendido(tramo)), golpe(tPulso(tramo)));
          const entrada = interpolate(frame, [fN, fN + 0.12 * fps], [0.4, 1], {
            ...fijar,
            easing: Easing.out(Easing.back(2)),
          });
          return (
            <div
              key={tramo}
              style={{
                position: "absolute",
                left: CENTROS[tramo - 1] - 60,
                top: Y0,
                width: 120,
                height: ALTO,
                lineHeight: `${ALTO}px`,
                textAlign: "center",
                fontFamily: encendido ? FUENTE.fuerte : FUENTE.normal,
                fontWeight: encendido ? 700 : 300,
                fontSize: 62,
                color: encendido ? COLOR.verdeOscuro : "#FFF6E6",
                textShadow: encendido ? "0 1px 0 rgba(255,255,255,0.35)" : "0 2px 8px rgba(0,0,0,0.5)",
                opacity: frame >= fN ? (encendido ? 1 : 0.7) : 0,
                scale: entrada * (1 + 0.32 * pop),
              }}
            >
              {tramo}
            </div>
          );
        })}

        {/* Checks verdes de beneficio completado */}
        {[1, 2, 3].map((tramo) => {
          const animado = escena.checks.find((c) => c.tramo === tramo);
          const hecho = escena.rotulosYaHechos.includes(tramo);
          if (!animado && !hecho) return null;
          const f0 = Math.round((animado ? animado.t : -10) * fps);
          const x = tramo === 3 ? X1 - 74 : LIMITES[tramo] - 44;
          return (
            <svg
              key={tramo}
              viewBox="0 0 48 48"
              width={48}
              height={48}
              style={{
                position: "absolute",
                left: x - 24,
                top: Y0 - 24,
                opacity: frame >= f0 ? 1 : 0,
                scale: interpolate(frame, [f0, f0 + 0.12 * fps, f0 + 0.2 * fps], [0, 1.25, 1], {
                  ...fijar,
                  easing: Easing.out(Easing.quad),
                }),
                filter: "drop-shadow(0 0 10px rgba(77,195,81,0.75)) drop-shadow(0 2px 4px rgba(0,0,0,0.5))",
              }}
            >
              <circle cx="24" cy="24" r="22" fill={COLOR.verdeVivo} stroke="#FFFFFF" strokeWidth="2.5" />
              <path
                d="M13 25 L21 33 L36 17"
                fill="none"
                stroke="#FFFFFF"
                strokeWidth="5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          );
        })}

        {/* Rótulos */}
        {[1, 2, 3].map((tramo) => {
          const animado = escena.rotulos.find((r) => r.tramo === tramo);
          if (animado) return <Rotulo key={tramo} tramo={tramo} lineas={animado.lineas} hecho={false} />;
          if (escena.rotulosYaHechos.includes(tramo))
            return (
              <Rotulo
                key={tramo}
                tramo={tramo}
                lineas={ROTULO_HECHO[tramo].map((l) => l.map((texto) => ({ texto, t: 0 })))}
                hecho
              />
            );
          return null;
        })}
      </div>
    </AbsoluteFill>
  );
};
