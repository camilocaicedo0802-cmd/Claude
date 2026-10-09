import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS } from "../brand";
import { PASOS } from "./Footage";
import { Aceite3D, Apagar3D, FlechaAbajo3D, FlechaCirculo3D, Lupa3D, Perilla3D, SinAgua3D } from "./Objetos3D";
import { at, DURATION, pop } from "./timing";

// Día 3 · "Preparación y uso seguro". Cada gráfico nace de una frase concreta (estilo.md §10).
// Zonas (crudo 1080×1920 sin recorte; cabeza ≈ x 460–640, y 650–860):
//   títulos con base en y = 550 · cara libre entre y ≈ 600 y 1180 · recursos de apoyo entre y = 1180 y 1560
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

// Base 550: los trazos descendentes de TAN Pearl (p, g) bajan ~30 px y deben quedar sobre y = 580
const BASE_TITULOS = 550;
const Top: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", top: 60, height: BASE_TITULOS - 60, left: 50, right: 50, display: "flex", flexDirection: "column", justifyContent: "flex-end", alignItems: "center", gap: 10 }}>
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
const DER = { left: 735, top: 560 } as const;

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
  display: "flex",
  alignItems: "center",
  gap: 14,
});

// Iconos ✓ / ✕ que se dibujan
const Icono: React.FC<{ tipo: "si" | "no"; at: number; size?: number }> = ({ tipo, at: atSec, size = 46 }) => {
  const { t } = useT();
  const d = interpolate(t, [atSec + 0.1, atSec + 0.4], [0, 1], CLAMP);
  return (
    <svg width={size} height={size} viewBox="0 0 56 56">
      <circle cx={28} cy={28} r={26} fill={tipo === "si" ? COLORS.salvia : COLORS.petroleo} />
      {tipo === "si" ? (
        <path d="M16 29 L25 38 L41 20" stroke={COLORS.marfil} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={40} strokeDashoffset={40 * (1 - d)} />
      ) : (
        <path d="M19 19 L37 37 M37 19 L19 37" stroke={COLORS.durazno} strokeWidth={6} fill="none" strokeLinecap="round" strokeDasharray={52} strokeDashoffset={52 * (1 - d)} />
      )}
    </svg>
  );
};

// Título de paso: número grande (Glacial Bold) + idea corta (TAN Pearl)
const Paso: React.FC<{ n: number; numAt: number; kicker?: string; kickerAt?: number; titulo: string; tituloAt: number; size?: number }> = ({ n, numAt, kicker: k, kickerAt, titulo, tituloAt, size = 120 }) => (
  <Top>
    {k ? (
      <Pop at={kickerAt ?? numAt}>
        <div style={kicker}>{k}</div>
      </Pop>
    ) : null}
    <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
      <Pop at={numAt} kind="scale">
        <div style={{ width: 128, height: 128, borderRadius: 64, background: COLORS.durazno, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 10px 30px rgba(69,89,90,.4)" }}>
          <span style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 90, color: COLORS.petroleo, lineHeight: 1, marginTop: -6 }}>{n}</span>
        </div>
      </Pop>
      <Pop at={tituloAt} kind="left">
        <div style={display(size)}>{titulo}</div>
      </Pop>
    </div>
  </Top>
);

// 0 · "Antes de empezar vamos a tener las siguientes instrucciones en cuenta"
const Intro: React.FC = () => (
  <Top>
    <Pop at={0}>
      <div style={kicker}>ANTES DE EMPEZAR</div>
    </Pop>
    <Pop at={at("instrucciones").start} kind="scale">
      <div style={display(124, COLORS.durazno)}>uso seguro</div>
    </Pop>
  </Top>
);

// 1 · "primero vas a revisar muy bien tu piel" → lupa 3D; "no… sobre moretones, várices, el hueso" → lista de lo que se evita
const RevisaPiel: React.FC = () => (
  <>
    <Paso n={1} numAt={PASOS.uno} titulo="revisa tu piel" tituloAt={at("revisar").start} size={92} />
    <Lupa3D desde={at("revisar").start} ancho={330} alto={360} style={{ left: 735, top: 600 }} />
  </>
);
export const EVITA = [
  { frase: "moretones", texto: "Moretones" },
  { frase: "varices|várices", texto: "Várices" },
  { frase: "el hueso", texto: "Hueso" },
] as const;
const Evita: React.FC = () => (
  <Bottom>
    <Pop at={at("no puedes pasar").start} kind="up" style={{ width: "100%" }}>
      <div style={{ background: CARD, borderRadius: 32, padding: "24px 40px 30px", boxShadow: "0 16px 40px rgba(69,89,90,.35)" }}>
        <div style={{ ...kicker, textShadow: "none", fontSize: 28, color: COLORS.durazno, textAlign: "left", marginBottom: 14 }}>NO LO PASES SOBRE</div>
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
          {EVITA.map((e) => (
            <Pop key={e.texto} at={at(e.frase).start} kind="up">
              <div style={{ ...chip(true), fontSize: 40, padding: "10px 26px 14px 12px" }}>
                <Icono tipo="no" at={at(e.frase).start} />
                {e.texto}
              </div>
            </Pop>
          ))}
        </div>
      </div>
    </Pop>
  </Bottom>
);
const Dolor: React.FC = () => (
  <Bottom>
    <Pop at={at("dolor").start} kind="up">
      <div style={{ ...chip(false), fontSize: 40 }}>Puede generar dolor e irritación</div>
    </Pop>
  </Bottom>
);

// 2 · "nunca, nunca puede utilizarse sobre la piel seca" → "piel seca" se tacha; "siempre debes usar el aceite" → frasco 3D vierte
const PielSeca: React.FC = () => {
  const { t } = useT();
  const seca = at("piel seca");
  const raya = interpolate(t, [seca.end, seca.end + 0.3], [0, 1], CLAMP);
  return (
    <Top>
      <Pop at={at("nunca nunca").start}>
        <div style={kicker}>NUNCA, NUNCA SOBRE</div>
      </Pop>
      <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
        <Pop at={PASOS.dos} kind="scale">
          <div style={{ width: 128, height: 128, borderRadius: 64, background: COLORS.durazno, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 90, color: COLORS.petroleo, lineHeight: 1, marginTop: -6 }}>2</span>
          </div>
        </Pop>
        <Pop at={seca.start} kind="left">
          <div style={{ position: "relative" }}>
            <div style={display(120)}>piel seca</div>
            <div style={{ position: "absolute", left: 0, top: "46%", height: 9, width: `${raya * 100}%`, borderRadius: 5, background: COLORS.durazno }} />
          </div>
        </Pop>
      </div>
    </Top>
  );
};
const ConAceite: React.FC = () => (
  <>
    <Top>
      <Pop at={at("siempre debes usar").start}>
        <div style={kicker}>SIEMPRE CON</div>
      </Pop>
      <Pop at={at("el aceite").start} kind="scale">
        <div style={display(150, COLORS.durazno)}>aceite</div>
      </Pop>
    </Top>
    <Aceite3D desde={at("siempre debes usar").start} vierte={at("el aceite").start} ancho={330} alto={420} style={{ left: 740, top: 520 }} />
  </>
);
// "entre más aceite pongas, mucho mejor se va a deslizar" → barra de deslizamiento que se llena gota a gota
const Desliza: React.FC = () => {
  const { t } = useT();
  const s = at("entre más|mas aceite").start;
  const e = at("se va a deslizar").end;
  const p = interpolate(t, [s, e], [0.15, 1], { ...CLAMP, easing: Easing.inOut(Easing.cubic) });
  return (
    <Bottom>
      <Pop at={s} kind="up" style={{ width: "100%" }}>
        <div style={{ background: CARD, borderRadius: 32, padding: "26px 40px 32px", boxShadow: "0 16px 40px rgba(69,89,90,.35)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: FONTS.body, fontWeight: 700, fontSize: 36, color: COLORS.marfil, marginBottom: 16 }}>
            <span>+ aceite</span>
            <span style={{ color: COLORS.durazno }}>+ deslizamiento</span>
          </div>
          <div style={{ height: 30, borderRadius: 15, background: "rgba(245,240,236,.2)", overflow: "hidden" }}>
            <div style={{ width: `${p * 100}%`, height: "100%", borderRadius: 15, background: `linear-gradient(90deg, ${COLORS.salvia}, ${COLORS.durazno})` }} />
          </div>
        </div>
      </Pop>
    </Bottom>
  );
};
// "No uses agua… debes usar un aceite para masajes" → gota de agua prohibida + agua ✕ / aceite ✓
const SinAgua: React.FC = () => (
  <>
    <SinAgua3D desde={at("no uses agua").start - 0.1} prohibe={at("agua").end} ancho={320} alto={360} style={{ left: 20, top: 600 }} />
    <Bottom>
      <div style={{ display: "flex", gap: 18 }}>
        <Pop at={at("agua").start} kind="left">
          <div style={chip(false)}>
            <Icono tipo="no" at={at("agua").start} />
            Agua
          </div>
        </Pop>
        <Pop at={at("un aceite para masajes").start} kind="right">
          <div style={chip(true)}>
            <Icono tipo="si" at={at("un aceite para masajes").start} />
            Aceite de masajes
          </div>
        </Pop>
      </div>
    </Bottom>
  </>
);

// 3 · "desde la intensidad más baja. Aumenta solo si te empiezas a sentir cómoda" → perilla 3D: nivel 1 → sube poco a poco
const Intensidad: React.FC = () => (
  <>
    <Paso n={3} numAt={PASOS.tres} kicker="EMPIEZA SIEMPRE CON LA" kickerAt={at("vas a empezar a usar").start} titulo="más baja" tituloAt={at("intensidad más|mas baja").start} size={130} />
    <Perilla3D
      desde={at("vas a empezar a usar").start}
      ancho={330}
      alto={340}
      style={{ left: 735, top: 610 }}
      niveles={[
        [at("vas a empezar a usar").start, 1],
        [at("aumenta").start, 1],
        [at("cómoda").end, 3],
      ]}
    />
  </>
);
const Comoda: React.FC = () => (
  <Bottom>
    <Pop at={at("aumenta").start} kind="up">
      <div style={chip(false)}>Aumenta solo si estás cómoda</div>
    </Pop>
  </Bottom>
);
// "la intensidad sí debe sentirse, pero no debe doler" → se siente ✓ / duele ✕
const NoDuele: React.FC = () => (
  <Bottom>
    <div style={{ display: "flex", gap: 18 }}>
      <Pop at={at("sentirte").start} kind="left">
        <div style={chip(false)}>
          <Icono tipo="si" at={at("sentirte").start} />
          Se siente
        </div>
      </Pop>
      <Pop at={at("no debe doler").start} kind="right">
        <div style={chip(true)}>
          <Icono tipo="no" at={at("no debe doler").start} />
          No duele
        </div>
      </Pop>
    </div>
  </Bottom>
);

// 4 · "haz primero una prueba en una zona pequeña de tu abdomen o de tus piernas"
const Prueba: React.FC = () => (
  <Paso n={4} numAt={PASOS.cuatro} kicker="HAZ PRIMERO UNA" kickerAt={at("vas a hacer primero").start} titulo="prueba" tituloAt={at("una prueba").start} size={140} />
);
const ZonaPequena: React.FC = () => (
  <Bottom>
    <Pop at={at("zona pequeña").start} kind="up">
      <div style={{ ...kicker, fontSize: 30, marginBottom: 6 }}>EN UNA ZONA PEQUEÑA</div>
    </Pop>
    <div style={{ display: "flex", gap: 18 }}>
      <Pop at={at("abdomen").start} kind="left">
        <div style={chip(true)}>Abdomen</div>
      </Pop>
      <Pop at={at("piernas").start} kind="right">
        <div style={chip(true)}>Piernas</div>
      </Pop>
    </div>
  </Bottom>
);
// "si jala demasiado o si duele demasiado, vas a parar, bajar la intensidad y aplicar más aceite" → 3 pasos que se encienden
export const SI_DUELE = [
  { frase: "vas a parar", texto: "Para" },
  { frase: "bajar la intensidad", texto: "Baja la intensidad" },
  { frase: "aplicar", texto: "Aplica más aceite" },
] as const;
const SiDuele: React.FC = () => {
  const { t } = useT();
  const activo = SI_DUELE.reduce((a, s, i) => (t >= at(s.frase).start ? i : a), -1);
  return (
    <>
      <Bottom>
        <Pop at={at("si jala").start} kind="up" style={{ width: "100%" }}>
          <div style={{ background: CARD, borderRadius: 32, padding: "22px 36px 28px", boxShadow: "0 16px 40px rgba(69,89,90,.35)" }}>
            <div style={{ ...kicker, textShadow: "none", fontSize: 28, color: COLORS.durazno, textAlign: "left", marginBottom: 12 }}>SI JALA O DUELE DEMASIADO</div>
            {SI_DUELE.map((s, i) => (
              <Pop key={s.texto} at={at(s.frase).start} kind="left">
                <div style={{ display: "flex", alignItems: "center", gap: 20, padding: "8px 0", opacity: i === activo ? 1 : 0.7 }}>
                  <div style={{ width: 54, height: 54, borderRadius: 27, background: i === activo ? COLORS.durazno : COLORS.salvia, color: COLORS.petroleo, fontFamily: FONTS.body, fontWeight: 700, fontSize: 32, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</div>
                  <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 42, color: i === activo ? COLORS.durazno : COLORS.marfil }}>{s.texto}</div>
                </div>
              </Pop>
            ))}
          </div>
        </Pop>
      </Bottom>
      {/* La perilla vuelve y baja de nivel al decir "bajar la intensidad" */}
      <Perilla3D
        desde={at("bajar la intensidad").start - 0.2}
        ancho={300}
        alto={310}
        style={{ left: 745, top: 630 }}
        niveles={[
          [at("bajar la intensidad").start, 4],
          [at("bajar la intensidad").end + 0.2, 1],
        ]}
      />
    </>
  );
};

// 5 · "mantener siempre el Luma Body en movimiento, nunca lo puedes dejar quieto porque van a salir moretones"
const Movimiento: React.FC = () => (
  <Paso n={5} numAt={PASOS.cinco} kicker="SIEMPRE EN" kickerAt={at("vas a mantener").start} titulo="movimiento" tituloAt={at("movimiento").start} size={104} />
);
const NoQuieto: React.FC = () => {
  const { t } = useT();
  const q = at("quieto");
  const raya = interpolate(t, [q.end, q.end + 0.3], [0, 1], CLAMP);
  return (
    <Bottom>
      <Pop at={q.start} kind="up">
        <div style={{ ...chip(false), position: "relative" }}>
          Quieto en un punto
          <div style={{ position: "absolute", left: 30, right: 30, top: "50%", height: 7, borderRadius: 4, background: COLORS.durazno, transform: `scaleX(${raya})`, transformOrigin: "left" }} />
        </div>
      </Pop>
      <Pop at={at("moretones", PASOS.cinco).start} kind="up">
        <div style={{ ...kicker, fontSize: 32 }}>PUEDEN SALIR MORETONES</div>
      </Pop>
    </Bottom>
  );
};
// "de arriba hacia abajo o en forma de círculos" → flecha 3D que baja y flecha 3D que gira
const ComoMover: React.FC = () => (
  <>
    <FlechaAbajo3D desde={at("de arriba hacia abajo").start} ancho={300} alto={380} style={{ left: 30, top: 580 }} />
    <FlechaCirculo3D desde={at("círculos").start} ancho={320} alto={340} style={{ left: 735, top: 600 }} />
    <Bottom>
      <div style={{ display: "flex", gap: 18 }}>
        <Pop at={at("de arriba hacia abajo").start} kind="left">
          <div style={chip(true)}>De arriba hacia abajo</div>
        </Pop>
        <Pop at={at("círculos").start} kind="right">
          <div style={chip(false)}>En círculos</div>
        </Pop>
      </div>
    </Bottom>
  </>
);

// Cierre · "al terminar solo debes apagar y limpiar muy bien tu dispositivo" → botón 3D que se apaga + brillos
const Cierre: React.FC = () => (
  <>
    <Top>
      <Pop at={at("al terminar").start}>
        <div style={kicker}>AL TERMINAR</div>
      </Pop>
      <Pop at={at("apagar").start} kind="scale">
        <div style={display(100, COLORS.durazno)}>apaga y limpia</div>
      </Pop>
    </Top>
    <Apagar3D desde={at("al terminar").start} apaga={at("apagar").start} limpia={at("limpiar").start} ancho={320} alto={340} style={DER} />
  </>
);

type Beat = { nombre: string; desde: number; hasta: number; Comp: React.FC };

const BEATS: Beat[] = [
  { nombre: "Intro", desde: 0, hasta: PASOS.uno, Comp: Intro },
  { nombre: "1 Revisa la piel", desde: PASOS.uno, hasta: PASOS.dos, Comp: RevisaPiel },
  { nombre: "1 Evita", desde: at("no puedes pasar").start - 0.1, hasta: at("dolor").start, Comp: Evita },
  { nombre: "1 Dolor", desde: at("dolor").start, hasta: PASOS.dos, Comp: Dolor },
  { nombre: "2 Piel seca", desde: PASOS.dos, hasta: at("siempre debes usar").start, Comp: PielSeca },
  { nombre: "2 Con aceite", desde: at("siempre debes usar").start, hasta: at("no uses agua").start, Comp: ConAceite },
  { nombre: "2 Desliza", desde: at("entre más|mas aceite").start - 0.1, hasta: at("no uses agua").start, Comp: Desliza },
  { nombre: "2 Sin agua", desde: at("no uses agua").start - 0.1, hasta: PASOS.tres, Comp: SinAgua },
  { nombre: "3 Intensidad", desde: PASOS.tres, hasta: PASOS.cuatro, Comp: Intensidad },
  { nombre: "3 Cómoda", desde: at("aumenta").start - 0.1, hasta: at("recuerda").start, Comp: Comoda },
  { nombre: "3 No duele", desde: at("recuerda").start, hasta: PASOS.cuatro, Comp: NoDuele },
  { nombre: "4 Prueba", desde: PASOS.cuatro, hasta: PASOS.cinco, Comp: Prueba },
  { nombre: "4 Zona pequeña", desde: at("zona pequeña").start - 0.1, hasta: at("si jala").start, Comp: ZonaPequena },
  { nombre: "4 Si duele", desde: at("si jala").start - 0.1, hasta: PASOS.cinco, Comp: SiDuele },
  { nombre: "5 Movimiento", desde: PASOS.cinco, hasta: PASOS.cierre, Comp: Movimiento },
  { nombre: "5 No quieto", desde: at("nunca lo puedes").start - 0.1, hasta: at("de arriba hacia abajo").start - 0.1, Comp: NoQuieto },
  { nombre: "5 Cómo mover", desde: at("de arriba hacia abajo").start - 0.1, hasta: PASOS.cierre, Comp: ComoMover },
  { nombre: "Cierre", desde: PASOS.cierre, hasta: DURATION + 1, Comp: Cierre },
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
