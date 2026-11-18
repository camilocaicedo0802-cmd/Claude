import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { Bloque, PalabraTL } from "../datos/edicion";
import { CITA, DEGRADADO_DESTACADO, DEST, FUENTE, PILDORA, SUB } from "../estilo";
import { Icono } from "./Iconos";

// Todos los tiempos `t` que reciben estos componentes son segundos desde el inicio del
// bloque (cada bloque vive en su propio <Sequence>).

const fijar = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const textoNormal = (tam: number): React.CSSProperties => ({
  fontFamily: FUENTE.normal,
  fontWeight: 300,
  fontSize: tam,
  letterSpacing: `${SUB.interletraje}em`,
  color: "#FFFFFF",
  textShadow: SUB.sombra,
  whiteSpace: "nowrap",
});

/** Mancha oscura difusa detrás del texto para que resalte sobre el campo claro (§5). */
const Mancha: React.FC<{ fuerza: number; margen: string }> = ({ fuerza, margen }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        inset: margen,
        zIndex: -2,
        background: `radial-gradient(ellipse at center, rgba(0,0,0,${fuerza}) 0%, rgba(0,0,0,${fuerza * 0.55}) 42%, rgba(0,0,0,0) 72%)`,
        opacity: interpolate(frame, [0, 0.12 * fps], [0, 1], fijar),
      }}
    />
  );
};

/** Palabra de subtítulo normal (§4): cae 12 px con ligera inclinación en 0,1 s. */
const PalabraNormal: React.FC<{ texto: string; t: number; ultimo: boolean }> = ({ texto, t, ultimo }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = Math.round(t * fps);
  const f1 = f0 + Math.max(2, Math.round(SUB.durEntrada * fps));
  const avance = interpolate(frame, [f0, f1], [0, 1], { ...fijar, easing: Easing.out(Easing.cubic) });

  return (
    <span
      style={{
        display: "inline-block",
        marginRight: ultimo ? 0 : `${SUB.separacionPalabras}em`,
        transformOrigin: "0% 100%",
        opacity: interpolate(frame, [f0, f0 + 0.035 * fps], [0, 1], fijar),
        translate: `0px ${(-SUB.caida * (1 - avance)).toFixed(2)}px`,
        rotate: `${(SUB.giro * (1 - avance)).toFixed(2)}deg`,
      }}
    >
      {texto}
    </span>
  );
};

/** Palabra destacada (§5): mayúsculas, degradado naranja → dorado, resplandor y pop 1,10 → 1. */
const PalabraDestacada: React.FC<{
  texto: string;
  t: number;
  tam: number;
  cursiva: boolean;
  ultimo: boolean;
  fija: boolean;
}> = ({ texto, t, tam, cursiva, ultimo, fija }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f0 = Math.round(t * fps);

  return (
    <span
      style={{
        display: "inline-block",
        fontFamily: FUENTE.fuerte,
        fontWeight: 700,
        fontStyle: cursiva ? "italic" : "normal",
        fontSize: tam,
        letterSpacing: `${DEST.interletraje}em`,
        // El relleno extra evita que el degradado recorte tildes y el vuelo de la cursiva.
        padding: "0.24em 0.14em 0.1em",
        margin: `-0.24em ${ultimo ? "-0.14em" : `${DEST.separacionPalabras - 0.14}em`} -0.1em -0.14em`,
        backgroundImage: DEGRADADO_DESTACADO,
        backgroundClip: "text",
        WebkitBackgroundClip: "text",
        color: "transparent",
        WebkitTextFillColor: "transparent",
        filter: DEST.resplandor,
        transformOrigin: "50% 62%",
        opacity: fija ? 1 : interpolate(frame, [f0, f0 + 0.03 * fps], [0, 1], fijar),
        scale: fija
          ? 1
          : interpolate(frame, [f0, f0 + DEST.durPop * fps], [DEST.popDe, 1], {
              ...fijar,
              easing: Easing.out(Easing.cubic),
            }),
      }}
    >
      {texto}
    </span>
  );
};

/** Píldora (§5): cápsula negra que entra con barrido; después caen las palabras dentro. */
const Pildora: React.FC<{ palabras: PalabraTL[]; ini: number; tam: number; sangria: number }> = ({
  palabras,
  ini,
  tam,
  sangria,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const alto = Math.round(tam * 1.22);
  const fP = Math.round((palabras[0].t - ini - PILDORA.retardoTexto) * fps);
  const oculto = interpolate(frame, [fP, fP + PILDORA.durBarrido * fps], [100, 0], fijar);
  const fondo = interpolate(frame, [fP + 0.14 * fps, fP + 0.36 * fps], [1, 0.55], fijar);
  const borde = interpolate(frame, [fP + 0.1 * fps, fP + 0.3 * fps], [0, 1], fijar);

  return (
    <div
      style={{
        ...textoNormal(tam),
        marginTop: 6,
        marginLeft: sangria,
        height: alto,
        borderRadius: alto / 2,
        padding: `0 ${PILDORA.margenX}px`,
        display: "inline-flex",
        alignItems: "center",
        backgroundColor: `rgba(4,14,10,${fondo})`,
        boxShadow: `inset 0 0 0 ${PILDORA.borde}px rgba(207,233,168,${borde}), 0 0 18px rgba(77,195,81,${0.35 * borde})`,
        clipPath: `inset(-20px ${oculto}% -20px -20px round ${alto / 2}px)`,
        opacity: frame >= fP ? 1 : 0,
      }}
    >
      {palabras.map((w, i) => (
        <PalabraNormal key={i} texto={w.texto} t={w.t - ini} ultimo={i === palabras.length - 1} />
      ))}
    </div>
  );
};

type Normal = Extract<Bloque, { tipo: "normal" }>;
type Apilado = Extract<Bloque, { tipo: "apilado" }>;
type Cita = Extract<Bloque, { tipo: "cita" }>;

const BloqueNormal: React.FC<{ b: Normal }> = ({ b }) => {
  const alto = SUB.tam * 1.2;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        width: "100%",
        top: b.y - alto / 2,
        display: "flex",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          ...textoNormal(SUB.tam),
          position: "relative",
          isolation: "isolate",
          height: alto,
          lineHeight: `${alto}px`,
        }}
      >
        <Mancha fuerza={0.42} margen="-50px -110px" />
        {b.palabras.map((w, i) => (
          <PalabraNormal key={i} texto={w.texto} t={w.t - b.ini} ultimo={i === b.palabras.length - 1} />
        ))}
      </div>
    </div>
  );
};

const BloqueApilado: React.FC<{ b: Apilado }> = ({ b }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const izquierda = b.alinear === "izquierda";
  const fija = b.destacadoFijo ?? false;
  const altoLinea1 = SUB.tam * 1.12;
  const altoDest = b.tam * 0.95;
  // La línea destacada queda centrada en `y`; la línea 1 va encima y la píldora debajo.
  const arriba = (b.linea1 ? altoLinea1 : 0) + altoDest / 2;
  const fDest = Math.round((b.destacado[0][0].t - b.ini) * fps);
  const atenuacion = interpolate(frame, [fDest, fDest + 0.07 * fps], [1, DEST.atenuacionLineaAnterior], fijar);

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        width: "100%",
        top: b.y - arriba,
        display: "flex",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          position: "relative",
          isolation: "isolate",
          display: "inline-flex",
          flexDirection: "column",
          alignItems: izquierda ? "flex-start" : "center",
        }}
      >
        <Mancha fuerza={0.5} margen="-70px -150px" />

        {/* Iconos: encima y a la derecha del destacado, parcialmente tapados por él */}
        {b.iconos?.map((ic, k) => (
          <Icono
            key={ic.icono}
            icono={ic.icono}
            t={ic.t - b.ini}
            style={{
              zIndex: -1,
              right: -44 + (b.iconos!.length - 1 - k) * 122,
              top: (b.linea1 ? altoLinea1 : 0) - 104,
            }}
          />
        ))}

        {b.linea1 ? (
          <div
            style={{
              ...textoNormal(SUB.tam),
              height: altoLinea1,
              lineHeight: `${altoLinea1}px`,
              marginLeft: izquierda ? 6 : 0,
              opacity: atenuacion,
            }}
          >
            {b.linea1.map((w, i) => (
              <PalabraNormal key={i} texto={w.texto} t={w.t - b.ini} ultimo={i === b.linea1!.length - 1} />
            ))}
          </div>
        ) : null}

        {b.destacado.map((linea, k) => (
          <div key={k} style={{ height: altoDest, lineHeight: `${altoDest}px`, whiteSpace: "nowrap" }}>
            {linea.map((w, i) => (
              <PalabraDestacada
                key={i}
                texto={w.texto}
                t={w.t - b.ini}
                tam={b.tam}
                cursiva={b.cursiva}
                ultimo={i === linea.length - 1}
                fija={fija}
              />
            ))}
          </div>
        ))}

        {b.pildora ? (
          <Pildora
            palabras={b.pildora}
            ini={b.ini}
            tam={b.tamPildora ?? PILDORA.tam}
            sangria={izquierda ? 34 : 0}
          />
        ) : null}
      </div>
    </div>
  );
};

/** Cita en negrita (§5): toda la frase al 35 % y cada palabra pasa al 100 % al pronunciarse. */
const BloqueCita: React.FC<{ b: Cita }> = ({ b }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const altoLinea = CITA.tam * CITA.interlineado;
  const alto = altoLinea * b.lineas.length;

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        width: "100%",
        top: b.y - alto / 2,
        display: "flex",
        justifyContent: "center",
        opacity: interpolate(frame, [0, 0.08 * fps], [0, 1], fijar),
      }}
    >
      <div
        style={{
          position: "relative",
          isolation: "isolate",
          fontFamily: FUENTE.fuerte,
          fontWeight: 700,
          fontSize: CITA.tam,
          letterSpacing: "-0.03em",
          lineHeight: `${altoLinea}px`,
          color: "#FFFFFF",
          textShadow: SUB.sombra,
          textAlign: "center",
          whiteSpace: "nowrap",
        }}
      >
        <Mancha fuerza={0.5} margen="-70px -120px" />
        {b.lineas.map((linea, k) => (
          <div key={k}>
            {linea.map((w, i) => {
              const f0 = Math.round((w.t - b.ini) * fps);
              return (
                <span
                  key={i}
                  style={{
                    display: "inline-block",
                    marginRight: i === linea.length - 1 ? 0 : "0.24em",
                    opacity: interpolate(frame, [f0, f0 + 0.08 * fps], [CITA.opacidadPendiente, 1], fijar),
                  }}
                >
                  {w.texto}
                </span>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
};

export const BloqueSubtitulo: React.FC<{ b: Bloque }> = ({ b }) => {
  if (b.tipo === "normal") return <BloqueNormal b={b} />;
  if (b.tipo === "apilado") return <BloqueApilado b={b} />;
  return <BloqueCita b={b} />;
};
