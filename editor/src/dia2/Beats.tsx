import React from "react";
import { Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS } from "../brand";
import { APOYO, FIN_APOYO } from "./Footage";
import { Camara3D, Carpeta3D, Cinta3D, Libreta3D, Pin3D } from "./Objetos3D";
import { at, DURATION, pop } from "./timing";

// Día 2 · "Punto de partida". Cada gráfico nace de una frase concreta (estilo.md §10).
// Zonas (crudo 1080×1920 sin recorte; cabeza ≈ x 470–640, y 675–880):
//   títulos con base en y = 580 · cara libre entre y ≈ 620 y 1180 · recursos de apoyo entre y = 1180 y 1560
//   objetos 3D a los lados de la cabeza (x < 360 o x > 740), a > 100 px de la cara.
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const SOMBRA = "0 4px 24px rgba(69,89,90,.6), 0 2px 6px rgba(69,89,90,.45)";
const CARD = "rgba(69,89,90,0.9)";

const useT = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { frame, fps, t: frame / fps };
};

type Kind = "up" | "scale" | "left" | "right";
const Pop: React.FC<{ at: number; kind?: Kind; children: React.ReactNode; style?: React.CSSProperties }> = ({ at: atSec, kind = "up", children, style }) => {
  const { frame, fps } = useT();
  const p = pop(frame, fps, atSec);
  const tr = {
    up: `translateY(${(1 - p) * 40}px)`,
    scale: `scale(${0.6 + 0.4 * p})`,
    left: `translateX(${(1 - p) * -160}px)`,
    right: `translateX(${(1 - p) * 160}px)`,
  }[kind];
  return <div style={{ opacity: Math.min(1, p * 1.4), transform: tr, ...style }}>{children}</div>;
};

// Base 550: los trazos descendentes de TAN Pearl (p, q) bajan ~30 px y deben quedar sobre y = 580
const BASE_TITULOS = 550;
const Top: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", top: 60, height: BASE_TITULOS - 60, left: 60, right: 60, display: "flex", flexDirection: "column", justifyContent: "flex-end", alignItems: "center", gap: 10 }}>
    {children}
  </div>
);
const TECHO_RECURSOS = 1180;
const BASE_RECURSOS = 1560;
const Bottom: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", top: TECHO_RECURSOS, height: BASE_RECURSOS - TECHO_RECURSOS, left: 66, right: 66, display: "flex", flexDirection: "column", justifyContent: "flex-end", alignItems: "center", gap: 16 }}>
    {children}
  </div>
);
// Huecos laterales para los objetos 3D (a la altura de la cabeza, sin tocarla)
const IZQ = { left: 20, top: 560 } as const;
const DER = { left: 740, top: 560 } as const;

const kicker: React.CSSProperties = { fontFamily: FONTS.body, fontWeight: 700, fontSize: 40, letterSpacing: "0.22em", color: COLORS.marfil, textShadow: SOMBRA, textAlign: "center" };
const display = (size: number, color: string = COLORS.marfil): React.CSSProperties => ({ fontFamily: FONTS.display, fontSize: size, lineHeight: 1, color, textShadow: SOMBRA, textAlign: "center" });
const chip = (activo = true): React.CSSProperties => ({
  fontFamily: FONTS.body,
  fontWeight: 700,
  fontSize: 44,
  padding: "14px 34px 18px",
  borderRadius: 999,
  background: activo ? COLORS.durazno : CARD,
  color: activo ? COLORS.petroleo : COLORS.marfil,
  boxShadow: "0 10px 30px rgba(69,89,90,.35)",
});

// 1 · "vamos a fijar nuestro punto de partida" → título + pin 3D que cae y se clava
const PuntoPartida: React.FC = () => (
  <>
    <Top>
      <Pop at={at("antes de comenzar").start}>
        <div style={kicker}>ANTES DE COMENZAR</div>
      </Pop>
      <Pop at={at("punto de partida").start} kind="scale">
        <div style={display(104)}>punto de</div>
        <div style={display(140, COLORS.durazno)}>partida</div>
      </Pop>
    </Top>
    <Pin3D desde={at("fijar").start - 0.1} clavado={at("punto de partida").start} ancho={320} alto={400} style={DER} />
  </>
);

// 2 · "sin filtros y sin poses perfectas" → dos etiquetas que se tachan al decir "sin"
const Tachada: React.FC<{ texto: string; at: number }> = ({ texto, at: atSec }) => {
  const { t } = useT();
  const raya = interpolate(t, [atSec + 0.25, atSec + 0.5], [0, 1], CLAMP);
  return (
    <Pop at={atSec} kind="up">
      <div style={{ ...chip(false), position: "relative", opacity: 1 - raya * 0.25 }}>
        {texto}
        <div style={{ position: "absolute", left: 24, top: "50%", height: 7, width: `calc(${raya * 100}% - ${raya * 48}px)`, borderRadius: 4, background: COLORS.durazno }} />
      </div>
    </Pop>
  );
};
const SinFiltros: React.FC = () => (
  <Bottom>
    <div style={{ display: "flex", gap: 18 }}>
      <Tachada texto="Filtros" at={at("sin filtros").start} />
      <Tachada texto="Poses perfectas" at={at("sin poses").start} />
    </div>
  </Bottom>
);

// 3 · "usa un fondo neutro, ropa cómoda… ver tu silueta" → lista de preparación que se escribe
export const SEG_POR_LETRA = 0.03;
const Check: React.FC<{ at: number; texto: string }> = ({ at: atSec, texto }) => {
  const { t } = useT();
  const d = interpolate(t, [atSec + 0.1, atSec + 0.4], [0, 1], CLAMP);
  const letras = Math.floor(interpolate(t, [atSec + 0.05, atSec + 0.05 + texto.length * SEG_POR_LETRA], [0, texto.length], CLAMP));
  return (
    <Pop at={atSec} kind="left">
      <div style={{ display: "flex", alignItems: "center", gap: 22, padding: "12px 0" }}>
        <svg width={56} height={56}>
          <circle cx={28} cy={28} r={26} fill={COLORS.salvia} />
          <path d="M16 29 L25 38 L41 20" stroke={COLORS.marfil} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={40} strokeDashoffset={40 * (1 - d)} />
        </svg>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 44, color: COLORS.marfil }}>
          {texto.slice(0, letras)}
          <span style={{ opacity: 0 }}>{texto.slice(letras)}</span>
        </div>
      </div>
    </Pop>
  );
};
export const PREPARA = [
  { frase: "fondo neutro", texto: "Fondo neutro" },
  { frase: "ropa cómoda", texto: "Ropa cómoda" },
  { frase: "ver tu silueta", texto: "Que se vea tu silueta" },
] as const;
const Prepara: React.FC = () => (
  <>
    <Top>
      <Pop at={at("usa un fondo").start}>
        <div style={kicker}>PREPARA EL LUGAR</div>
      </Pop>
    </Top>
    <Bottom>
      <Pop at={at("usa un fondo").start - 0.1} kind="up" style={{ width: "100%" }}>
        <div style={{ background: CARD, borderRadius: 32, padding: "26px 44px", boxShadow: "0 16px 40px rgba(69,89,90,.35)" }}>
          {PREPARA.map((p) => (
            <Check key={p.frase} at={at(p.frase).start} texto={p.texto} />
          ))}
        </div>
      </Pop>
    </Bottom>
  </>
);

// 4 · "vas a tomar una foto" → título + celular 3D cuyo diafragma dispara en "foto"
const TomaFoto: React.FC = () => (
  <>
    <Top>
      <Pop at={at("vas a tomar una foto").start}>
        <div style={kicker}>TOMA</div>
      </Pop>
      <Pop at={at("foto").start} kind="scale">
        <div style={{ display: "flex", alignItems: "baseline", gap: 24 }}>
          <span style={{ ...display(200, COLORS.durazno), fontFamily: FONTS.body, fontWeight: 700 }}>3</span>
          <span style={display(130)}>fotos</span>
        </div>
      </Pop>
    </Top>
    <Camara3D desde={at("vas a tomar una foto").start} disparo={at("foto").start} ancho={320} alto={400} style={IZQ} />
  </>
);

// 5 · "si quieres llevar un reporte adicional, puedes tomar tus medidas" → título + cinta métrica 3D
const Medidas: React.FC = () => (
  <>
    <Top>
      <Pop at={at("reporte adicional").start}>
        <div style={kicker}>REPORTE ADICIONAL</div>
      </Pop>
      <Pop at={at("tus medidas").start} kind="scale">
        <div style={display(150, COLORS.durazno)}>medidas</div>
      </Pop>
    </Top>
    <Cinta3D desde={at("tomar tus medidas").start} ancho={360} alto={330} style={{ left: 10, top: 640 }} />
  </>
);
// "en cintura, en abdomen bajo, en cadera y muslos" → una etiqueta por zona, en el instante en que la nombra
export const ZONAS = [
  { frase: "cintura", texto: "Cintura" },
  { frase: "abdomen bajo", texto: "Abdomen bajo" },
  { frase: "cadera", texto: "Cadera" },
  { frase: "muslos", texto: "Muslos" },
] as const;
const Zonas: React.FC = () => {
  const { t } = useT();
  const ultima = ZONAS.reduce((a, z, i) => (t >= at(z.frase).start ? i : a), 0);
  return (
    <Bottom>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 18, width: 860 }}>
        {ZONAS.map((z, i) => (
          <Pop key={z.frase} at={at(z.frase).start} kind="up">
            <div style={chip(i === ultima)}>{z.texto}</div>
          </Pop>
        ))}
      </div>
    </Bottom>
  );
};

// 6 · "mirar cómo avanzas con los días" → una línea de progreso que sube día a día
const Avance: React.FC = () => {
  const { t } = useT();
  const s = at("cómo avanzas").start;
  const p = interpolate(t, [s, s + 1.0], [0, 1], { ...CLAMP, easing: Easing.inOut(Easing.cubic) });
  const puntos = [0, 1, 2, 3, 4].map((i) => [40 + i * 170, 190 - i * 38 - (i % 2) * 12] as const);
  const d = puntos.map(([x, y], i) => `${i ? "L" : "M"} ${x} ${y}`).join(" ");
  return (
    <Top>
      <Pop at={at("mirar").start}>
        <div style={kicker}>MIRA CÓMO AVANZAS</div>
      </Pop>
      <svg width={760} height={220} style={{ overflow: "visible", filter: "drop-shadow(0 4px 14px rgba(69,89,90,.5))" }}>
        <path d={d} stroke={COLORS.durazno} strokeWidth={12} fill="none" strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
        {puntos.map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r={18 * Math.min(1, Math.max(0, (p - i / 4.2) * 6))} fill={i === 4 ? COLORS.durazno : COLORS.salvia} stroke={COLORS.marfil} strokeWidth={5} />
        ))}
      </svg>
    </Top>
  );
};

// 7 · "algo muy importante… cómo sientes la calidad de tus piernas / de tu abdomen, si se sienten pesados, inflamados"
//     → ficha con escala del 1 al 5 (guion: "Muestra una ficha con una escala del 1 al 5")
const Sientes: React.FC = () => (
  <Top>
    <Pop at={at("algo muy importante").start}>
      <div style={kicker}>ALGO MUY IMPORTANTE</div>
    </Pop>
    <Pop at={at("cómo sientes").start} kind="scale">
      <div style={display(104)}>¿cómo te</div>
      <div style={display(150, COLORS.durazno)}>sientes?</div>
    </Pop>
  </Top>
);
export const FICHA = [
  { zona: "piernas", nota: "pesados", etiqueta: "Piernas", sensacion: "pesadez", valor: 4 },
  { zona: "abdomen", nota: "inflamados", etiqueta: "Abdomen", sensacion: "inflamación", valor: 3 },
] as const;
const Ficha: React.FC = () => {
  const { t } = useT();
  return (
    <Bottom>
      <Pop at={at("piernas").start - 0.1} kind="up" style={{ width: "100%" }}>
        <div style={{ background: CARD, borderRadius: 32, padding: "24px 40px 30px", boxShadow: "0 16px 40px rgba(69,89,90,.35)" }}>
          <div style={{ ...kicker, textShadow: "none", fontSize: 28, color: COLORS.durazno, textAlign: "left", marginBottom: 10 }}>TU FICHA · DEL 1 AL 5</div>
          {FICHA.map((f) => {
            const zona = at(f.zona).start;
            const nota = at(f.nota).start;
            return (
              <Pop key={f.zona} at={zona} kind="left">
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 0" }}>
                  <div style={{ fontFamily: FONTS.body, color: COLORS.marfil, fontSize: 44, fontWeight: 700 }}>
                    {f.etiqueta}
                    <span style={{ fontWeight: 400, fontSize: 32, color: COLORS.durazno, marginLeft: 14, opacity: interpolate(t, [nota, nota + 0.2], [0, 1], CLAMP) }}>{f.sensacion}</span>
                  </div>
                  <div style={{ display: "flex", gap: 12 }}>
                    {[1, 2, 3, 4, 5].map((n) => {
                      const on = n <= f.valor && t >= nota + (n - 1) * 0.08;
                      return (
                        <div key={n} style={{ width: 46, height: 46, borderRadius: 23, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONTS.body, fontWeight: 700, fontSize: 26, background: on ? COLORS.durazno : "rgba(245,240,236,.18)", color: on ? COLORS.petroleo : COLORS.marfil, transform: `scale(${on ? 1.08 : 1})` }}>
                          {n}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </Pop>
            );
          })}
        </div>
      </Pop>
    </Bottom>
  );
};

// 8 · "anota muy bien esto" → libreta 3D donde el lápiz escribe
const Anota: React.FC = () => (
  <>
    <Top>
      <Pop at={at("anota").start} kind="scale">
        <div style={display(150, COLORS.durazno)}>anótalo</div>
      </Pop>
    </Top>
    <Libreta3D desde={at("anota").start} ancho={330} alto={360} style={{ left: 735, top: 600 }} />
  </>
);

// 9 · "revisar cómo va a ser el resultado al final de los 21 días" → calendario 3D (el del día 1) + cuenta 1→21
const CAL = { w: 650, h: 604, relojX: 0.7723, relojY: 0.6772 };
const Calendario3D: React.FC<{ desde: number }> = ({ desde }) => {
  const { frame, fps, t } = useT();
  const p = pop(frame, fps, desde, 9);
  if (p <= 0) return null;
  const ancho = 320;
  const alto = (ancho * CAL.h) / CAL.w;
  const k = ancho / CAL.w;
  const local = t - desde;
  const giro = interpolate(local, [0, 1.4], [0, 720], { ...CLAMP, easing: Easing.out(Easing.cubic) }) + Math.max(0, local - 1.4) * 40;
  const aguja = (largo: number, grados: number) => <rect x={-10 * k} y={-largo * k} width={20 * k} height={(largo + 10) * k} rx={10 * k} fill="#3D424C" transform={`rotate(${grados})`} />;
  return (
    <div
      style={{
        position: "absolute",
        left: 30,
        top: 660,
        width: ancho,
        height: alto,
        transform: `translateY(${Math.sin(local * Math.PI * 1.2) * 10}px) rotate(${(1 - p) * -25 + Math.sin(local * Math.PI * 0.9) * 3}deg) scale(${p})`,
        transformOrigin: "60% 100%",
        filter: "drop-shadow(0 18px 30px rgba(69,89,90,.45))",
      }}
    >
      <Img src={staticFile("graficos/calendario_base.png")} style={{ width: "100%", height: "100%" }} />
      <svg width={ancho} height={alto} style={{ position: "absolute", inset: 0 }}>
        <g transform={`translate(${CAL.relojX * ancho} ${CAL.relojY * alto})`}>
          {aguja(52, 45 + giro / 12)}
          {aguja(78, giro)}
          <circle r={22 * k} fill="#1F2329" />
          <circle r={17 * k} fill="#58A9E8" />
        </g>
      </svg>
    </div>
  );
};
const Resultado: React.FC = () => {
  const { t } = useT();
  const d = at("21 días").start;
  const n = Math.round(interpolate(t, [d, d + 0.6], [1, 21], { ...CLAMP, easing: Easing.out(Easing.cubic) }));
  return (
    <>
      <Top>
        <Pop at={at("el resultado").start}>
          <div style={kicker}>EL RESULTADO AL FINAL</div>
        </Pop>
        <Pop at={d - 0.1} kind="scale">
          <div style={{ display: "flex", alignItems: "baseline", gap: 24 }}>
            <span style={{ ...display(200, COLORS.durazno), fontFamily: FONTS.body, fontWeight: 700 }}>{n}</span>
            <span style={display(130)}>días</span>
          </div>
        </Pop>
      </Top>
      <Calendario3D desde={at("al final").start} />
    </>
  );
};

// 10 · "estos cambios son personales" → carpeta 3D "Día 1" (guion: guarda fotos y anotaciones en la carpeta Día 1)
const Personales: React.FC = () => (
  <>
    <Top>
      <Pop at={at("estos cambios").start}>
        <div style={kicker}>ESTOS CAMBIOS SON</div>
      </Pop>
      <Pop at={at("personales").start} kind="scale">
        <div style={display(140, COLORS.durazno)}>personales</div>
      </Pop>
    </Top>
  </>
);
const Carpeta: React.FC = () => <Carpeta3D desde={at("estos cambios").start + 0.1} cierra={at("personales").start} ancho={340} alto={340} style={{ left: 730, top: 620 }} />;
const Resultados: React.FC = () => (
  <Bottom>
    <Pop at={at("revisar los resultados").start} kind="up">
      <div style={chip(false)}>Revisa tus resultados</div>
    </Pop>
  </Bottom>
);

// 11 · "sin compararnos con nadie más" → "compararnos" se tacha y queda "solo tú"
const SinComparar: React.FC = () => {
  const { t } = useT();
  const s = at("sin compararnos").start;
  const raya = interpolate(t, [at("compararnos").end - 0.1, at("compararnos").end + 0.2], [0, 1], CLAMP);
  return (
    <Top>
      <Pop at={s}>
        <div style={{ position: "relative", ...kicker }}>
          SIN COMPARARTE
          <div style={{ position: "absolute", left: 0, top: "48%", height: 6, width: `${raya * 100}%`, borderRadius: 3, background: COLORS.durazno }} />
        </div>
      </Pop>
      <Pop at={at("con nadie más").start} kind="scale">
        <div style={display(104, COLORS.durazno)}>con nadie más</div>
      </Pop>
    </Top>
  );
};

type Beat = { nombre: string; desde: number; hasta: number; Comp: React.FC };

const BEATS: Beat[] = [
  { nombre: "Punto de partida", desde: 0, hasta: at("usa un fondo").start, Comp: PuntoPartida },
  { nombre: "Sin filtros", desde: at("sin filtros").start - 0.05, hasta: at("usa un fondo").start, Comp: SinFiltros },
  { nombre: "Prepara el lugar", desde: at("usa un fondo").start, hasta: at("vas a tomar una foto").start, Comp: Prepara },
  { nombre: "Toma foto", desde: at("vas a tomar una foto").start, hasta: APOYO[0].desde, Comp: TomaFoto },
  { nombre: "Medidas", desde: FIN_APOYO, hasta: at("mirar").start, Comp: Medidas },
  { nombre: "Zonas", desde: at("cintura").start - 0.05, hasta: at("algo muy importante").start, Comp: Zonas },
  { nombre: "Avance", desde: at("mirar").start, hasta: at("algo muy importante").start, Comp: Avance },
  { nombre: "Cómo te sientes", desde: at("algo muy importante").start, hasta: at("anota").start, Comp: Sientes },
  { nombre: "Ficha 1-5", desde: at("piernas").start - 0.15, hasta: at("el resultado").start, Comp: Ficha },
  { nombre: "Anota", desde: at("anota").start, hasta: at("el resultado").start - 0.1, Comp: Anota },
  { nombre: "Resultado 21 días", desde: at("el resultado").start - 0.1, hasta: at("estos cambios").start, Comp: Resultado },
  { nombre: "Personales", desde: at("estos cambios").start, hasta: at("sin compararnos").start, Comp: Personales },
  { nombre: "Carpeta Día 1", desde: at("estos cambios").start, hasta: DURATION + 1, Comp: Carpeta },
  { nombre: "Revisa resultados", desde: at("revisar los resultados").start - 0.05, hasta: DURATION + 1, Comp: Resultados },
  { nombre: "Sin comparar", desde: at("sin compararnos").start, hasta: DURATION + 1, Comp: SinComparar },
];

export const Beats: React.FC = () => {
  const { t } = useT();
  return (
    <>
      {BEATS.filter((b) => t >= b.desde && t < b.hasta).map((b) => {
        const salida = interpolate(t, [b.hasta - 0.2, b.hasta], [1, 0], CLAMP);
        return (
          <div key={b.nombre} style={{ position: "absolute", inset: 0, opacity: salida, transform: `translateY(${(1 - salida) * -20}px)` }}>
            <b.Comp />
          </div>
        );
      })}
    </>
  );
};
