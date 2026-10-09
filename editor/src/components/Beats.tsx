import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONTS } from "../brand";
import { at, DURATION, pop } from "../lib/timing";

// Gráficos dinámicos: cada uno nace de una frase concreta del vídeo (estilo.md §10).
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const SOMBRA = "0 4px 24px rgba(69,89,90,.6), 0 2px 6px rgba(69,89,90,.45)";
const CARD = "rgba(69,89,90,0.9)";

const useT = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return { frame, fps, t: frame / fps };
};

type Kind = "up" | "scale" | "left" | "right";
const Pop: React.FC<{ at: number; kind?: Kind; children: React.ReactNode; style?: React.CSSProperties }> = ({
  at: atSec,
  kind = "up",
  children,
  style,
}) => {
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

const Top: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", top: 150, left: 60, right: 60, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
    {children}
  </div>
);
const Bottom: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ position: "absolute", top: 1390, left: 66, right: 66, display: "flex", flexDirection: "column", alignItems: "center", gap: 16 }}>
    {children}
  </div>
);

const kicker: React.CSSProperties = {
  fontFamily: FONTS.body,
  fontWeight: 700,
  fontSize: 40,
  letterSpacing: "0.22em",
  color: COLORS.marfil,
  textShadow: SOMBRA,
  textAlign: "center",
};
const display = (size: number, color: string = COLORS.marfil): React.CSSProperties => ({
  fontFamily: FONTS.display,
  fontSize: size,
  lineHeight: 1,
  color,
  textShadow: SOMBRA,
});
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

// 1 · "Bienvenidas al reto de 21 días con Beleza" → contador 1→21 + marca
const Reto: React.FC = () => {
  const { t } = useT();
  const d = at("21 días");
  const n = Math.round(interpolate(t, [d.start, d.start + 0.7], [1, 21], { ...CLAMP, easing: Easing.out(Easing.cubic) }));
  return (
    <Top>
      <Pop at={at("bienvenidas").start}>
        <div style={kicker}>BIENVENIDAS AL RETO</div>
      </Pop>
      <Pop at={d.start} kind="scale">
        <div style={{ display: "flex", alignItems: "baseline", gap: 26 }}>
          <span style={{ ...display(250, COLORS.durazno), fontFamily: FONTS.body, fontWeight: 700 }}>{n}</span>
          <span style={display(130)}>días</span>
        </div>
      </Pop>
      <Pop at={at("beleza").start}>
        <div style={{ ...kicker, letterSpacing: "0.1em", fontWeight: 400 }}>
          con <span style={display(64)}>BELEZA</span>
        </div>
      </Pop>
    </Top>
  );
};

// 2 · "las próximas tres semanas" → 3 barras que se llenan una a una
const TresSemanas: React.FC = () => {
  const { t } = useT();
  const s = at("tres semanas").start;
  return (
    <Top>
      <Pop at={s} kind="scale">
        <div style={{ display: "flex", alignItems: "baseline", gap: 26 }}>
          <span style={{ ...display(220, COLORS.durazno), fontFamily: FONTS.body, fontWeight: 700 }}>3</span>
          <span style={display(130)}>semanas</span>
        </div>
      </Pop>
      <div style={{ display: "flex", gap: 18, marginTop: 24 }}>
        {[0, 1, 2].map((i) => {
          const fill = interpolate(t, [s + 0.15 + i * 0.3, s + 0.45 + i * 0.3], [0, 1], CLAMP);
          return (
            <div key={i} style={{ width: 210, height: 22, borderRadius: 11, background: "rgba(245,240,236,.35)", overflow: "hidden" }}>
              <div style={{ width: `${fill * 100}%`, height: "100%", background: COLORS.durazno }} />
            </div>
          );
        })}
      </div>
    </Top>
  );
};

// 3 · "tu Luma Body con nuestro aceite para masajes" → los dos productos se unen
const Combo: React.FC = () => (
  <Bottom>
    <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
      <Pop at={at("luma body").start} kind="left">
        <div style={chip(false)}>Luma Body</div>
      </Pop>
      <Pop at={at("nuestro aceite").start} kind="scale">
        <div style={{ ...display(80, COLORS.durazno), fontFamily: FONTS.body }}>+</div>
      </Pop>
      <Pop at={at("nuestro aceite").start + 0.1} kind="right">
        <div style={chip(true)}>Aceite de masajes</div>
      </Pop>
    </div>
  </Bottom>
);

// 4 · "de forma gradual" → escalones que suben poco a poco
const Gradual: React.FC = () => {
  const { t } = useT();
  const s = at("gradual").start;
  return (
    <Top>
      <Pop at={s - 0.25}>
        <div style={kicker}>DE FORMA</div>
      </Pop>
      <Pop at={s} kind="scale">
        <div style={display(150, COLORS.durazno)}>gradual</div>
      </Pop>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 14, height: 120, marginTop: 18 }}>
        {[0, 1, 2, 3].map((i) => {
          const h = interpolate(t, [s + 0.1 + i * 0.15, s + 0.4 + i * 0.15], [0, 30 + i * 30], { ...CLAMP, easing: Easing.out(Easing.cubic) });
          return <div key={i} style={{ width: 60, height: h, borderRadius: 10, background: i === 3 ? COLORS.durazno : COLORS.salvia }} />;
        })}
      </div>
    </Top>
  );
};

// 5 · "15 minutos diarios" → temporizador circular que se completa
const Temporizador: React.FC<{ desde?: number }> = ({ desde = 0 }) => {
  const { t } = useT();
  const s = at("15 minutos", desde).start;
  const p = interpolate(t, [s, s + 0.9], [0, 1], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  const R = 120;
  const C = 2 * Math.PI * R;
  return (
    <Top>
      <Pop at={s - 0.1} kind="scale">
        <div style={{ position: "relative", width: 300, height: 300 }}>
          <svg width={300} height={300} style={{ position: "absolute", transform: "rotate(-90deg)" }}>
            <circle cx={150} cy={150} r={R} stroke="rgba(245,240,236,.35)" strokeWidth={16} fill={CARD} />
            <circle cx={150} cy={150} r={R} stroke={COLORS.durazno} strokeWidth={16} fill="none" strokeLinecap="round" strokeDasharray={C} strokeDashoffset={C * (1 - p)} />
          </svg>
          <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 120, lineHeight: 1, color: COLORS.marfil }}>{Math.round(p * 15)}</div>
            <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 30, letterSpacing: "0.2em", color: COLORS.durazno }}>MIN</div>
          </div>
        </div>
      </Pop>
      <Pop at={at("diarios", s).start}>
        <div style={kicker}>AL DÍA</div>
      </Pop>
    </Top>
  );
};

// 6 · "convertir en rutina para ti" → palabra protagonista con subrayado que se dibuja
const Rutina: React.FC = () => {
  const { t } = useT();
  const s = at("rutina para ti").start;
  const u = interpolate(t, [s + 0.2, s + 0.6], [0, 1], { ...CLAMP, easing: Easing.inOut(Easing.cubic) });
  return (
    <Top>
      <Pop at={s - 0.3}>
        <div style={kicker}>TU MOMENTO, TU</div>
      </Pop>
      <Pop at={s} kind="scale">
        <div style={display(170, COLORS.durazno)}>rutina</div>
      </Pop>
      <div style={{ width: 460 * u, height: 8, borderRadius: 4, background: COLORS.marfil, marginTop: 6 }} />
    </Top>
  );
};

// 7 · "No recibiste solamente un producto, también recibirás una guía" → producto + guía
const MasGuia: React.FC = () => (
  <Top>
    <Pop at={at("no recibiste").start}>
      <div style={kicker}>NO SOLO UN PRODUCTO</div>
    </Pop>
    <Pop at={at("una guía").start} kind="scale">
      <div style={display(170, COLORS.durazno)}>+ guía</div>
    </Pop>
  </Top>
);

// 8 · "qué rutina realizar cada día, cómo usar este producto y cómo avanzar según tu tolerancia" → checklist
const Check: React.FC<{ at: number; texto: string }> = ({ at: atSec, texto }) => {
  const { t } = useT();
  const d = interpolate(t, [atSec + 0.1, atSec + 0.4], [0, 1], CLAMP);
  return (
    <Pop at={atSec} kind="left">
      <div style={{ display: "flex", alignItems: "center", gap: 22, padding: "14px 0" }}>
        <svg width={56} height={56}>
          <circle cx={28} cy={28} r={26} fill={COLORS.salvia} />
          <path d="M16 29 L25 38 L41 20" stroke={COLORS.marfil} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={40} strokeDashoffset={40 * (1 - d)} />
        </svg>
        <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 44, color: COLORS.marfil }}>{texto}</div>
      </div>
    </Pop>
  );
};
const Guia: React.FC = () => (
  <Bottom>
    <Pop at={at("donde sabrás").start} kind="up" style={{ width: "100%" }}>
      <div style={{ background: CARD, borderRadius: 32, padding: "28px 44px", boxShadow: "0 16px 40px rgba(69,89,90,.35)" }}>
        <div style={{ ...kicker, textShadow: "none", fontSize: 30, color: COLORS.durazno, textAlign: "left", marginBottom: 6 }}>TU GUÍA INCLUYE</div>
        <Check at={at("qué rutina realizar").start} texto="Qué rutina hacer cada día" />
        <Check at={at("cómo usar este producto").start} texto="Cómo usar el producto" />
        <Check at={at("cómo avanzar").start} texto="Cómo avanzar según tu tolerancia" />
      </div>
    </Pop>
  </Bottom>
);

// 9 · "primera semana… técnica / segunda… tiempo / tercera… zonas del cuerpo" → plan en 3 tarjetas
const Semanas: React.FC = () => {
  const { t } = useT();
  const semanas = [
    { n: 1, en: at("primera semana").start, label: "Técnica", labelAt: at("técnica").start },
    { n: 2, en: at("segunda").start, label: "+ Tiempo", labelAt: at("tiempo de trabajo").start },
    { n: 3, en: at("tercera").start, label: "+ Zonas", labelAt: at("zonas del cuerpo").start },
  ];
  const activa = semanas.reduce((a, s, i) => (t >= s.en ? i : a), 0);
  return (
    <Bottom>
      <div style={{ display: "flex", gap: 24 }}>
        {semanas.map((s, i) => {
          const on = i === activa;
          return (
            <Pop key={s.n} at={s.en} kind="up">
              <div
                style={{
                  width: 300,
                  height: 330,
                  borderRadius: 32,
                  background: on ? COLORS.durazno : CARD,
                  color: on ? COLORS.petroleo : COLORS.marfil,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 6,
                  transform: `scale(${on ? 1.04 : 0.96})`,
                  boxShadow: "0 16px 40px rgba(69,89,90,.35)",
                }}
              >
                <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 28, letterSpacing: "0.22em" }}>SEMANA</div>
                <div style={{ fontFamily: FONTS.body, fontWeight: 700, fontSize: 130, lineHeight: 1 }}>{s.n}</div>
                <div style={{ opacity: interpolate(t, [s.labelAt, s.labelAt + 0.2], [0, 1], CLAMP), fontFamily: FONTS.body, fontWeight: 700, fontSize: 38 }}>
                  {s.label}
                </div>
              </div>
            </Pop>
          );
        })}
      </div>
    </Bottom>
  );
};

// 10 · "No necesitas hacerlo perfecto, solo necesitas ser constante" → "perfecto" tachado → "constante"
const Constante: React.FC = () => {
  const { t } = useT();
  const perf = at("perfecto");
  const cons = at("constante").start;
  const tachado = interpolate(t, [perf.end, perf.end + 0.25], [0, 1], CLAMP);
  const fuera = interpolate(t, [cons - 0.25, cons], [1, 0], CLAMP);
  return (
    <Top>
      {t < cons ? (
        <Pop at={perf.start} kind="scale" style={{ opacity: fuera }}>
          <div style={{ position: "relative" }}>
            <div style={{ ...display(150), opacity: 0.9 }}>perfecto</div>
            <div style={{ position: "absolute", left: 0, top: "52%", height: 10, width: `${tachado * 100}%`, borderRadius: 5, background: COLORS.durazno }} />
          </div>
        </Pop>
      ) : (
        <>
          <Pop at={cons - 0.2}>
            <div style={kicker}>SOLO NECESITAS SER</div>
          </Pop>
          <Pop at={cons} kind="scale">
            <div style={display(140, COLORS.durazno)}>constante</div>
          </Pop>
        </>
      )}
    </Top>
  );
};

// 11 · "constante, escuchar tu cuerpo y completar esos 15 minutos" → 3 claves que se apilan
const Claves: React.FC = () => {
  const cons = at("constante").start;
  return (
    <Bottom>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 18 }}>
        <Pop at={cons + 0.3} kind="up">
          <div style={chip(false)}>Constancia</div>
        </Pop>
        <Pop at={at("escuchar tu cuerpo").start} kind="up">
          <div style={chip(false)}>Escucha tu cuerpo</div>
        </Pop>
        <Pop at={at("15 minutos", cons).start} kind="up">
          <div style={chip(true)}>15 min diarios</div>
        </Pop>
      </div>
    </Bottom>
  );
};

// 12 · "guardar el calendario en tu celular o imprímelo" → calendario de 21 días que se construye
const Calendario: React.FC<{ desde: number; soloDia1?: boolean }> = ({ desde, soloDia1 = false }) => {
  const { frame, fps } = useT();
  const pulso = 1 + 0.06 * Math.sin((frame / fps) * Math.PI * 2);
  return (
    <div style={{ background: CARD, borderRadius: 32, padding: 28, display: "grid", gridTemplateColumns: "repeat(7, 96px)", gap: 14, boxShadow: "0 16px 40px rgba(69,89,90,.35)" }}>
      {Array.from({ length: 21 }, (_, i) => {
        const p = pop(frame, fps, desde + i * 0.03);
        const dia1 = i === 0;
        return (
          <div
            key={i}
            style={{
              height: 84,
              borderRadius: 18,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 36,
              opacity: p * (soloDia1 && !dia1 ? 0.45 : 1),
              transform: `scale(${(0.5 + 0.5 * p) * (soloDia1 && dia1 ? pulso : 1)})`,
              background: dia1 ? COLORS.durazno : "rgba(245,240,236,.14)",
              color: dia1 ? COLORS.petroleo : COLORS.marfil,
            }}
          >
            {i + 1}
          </div>
        );
      })}
    </div>
  );
};
const GuardaCalendario: React.FC = () => {
  const cal = at("el calendario").start;
  return (
    <>
      <Top>
        <Pop at={at("recuerda guardar").start}>
          <div style={kicker}>GUARDA TU</div>
        </Pop>
        <Pop at={cal} kind="scale">
          <div style={display(135, COLORS.durazno)}>calendario</div>
        </Pop>
      </Top>
      <Bottom>
        <Calendario desde={cal + 0.1} />
        <div style={{ display: "flex", gap: 18 }}>
          <Pop at={at("celular").start} kind="left">
            <div style={chip(true)}>En tu celular</div>
          </Pop>
          <Pop at={at("imprímelo").start} kind="right">
            <div style={chip(false)}>o impreso</div>
          </Pop>
        </div>
      </Bottom>
    </>
  );
};

// 13 · "adecua muy bien el espacio donde vas a hacer tu rutina de masajes" → prepara tu espacio
const Espacio: React.FC = () => (
  <Top>
    <Pop at={at("adecua").start}>
      <div style={kicker}>PREPARA TU</div>
    </Pop>
    <Pop at={at("el espacio").start} kind="scale">
      <div style={display(160, COLORS.durazno)}>espacio</div>
    </Pop>
    <Pop at={at("rutina de masajes").start} kind="up" style={{ marginTop: 14 }}>
      <div style={chip(false)}>para tu rutina de masajes</div>
    </Pop>
  </Top>
);

// 14 · "acompáñame a comenzar el primer día" → Día 1 con el calendario
const Dia1: React.FC = () => {
  const d = at("primer día").start;
  return (
    <>
      <Top>
        <Pop at={at("acompáñame").start}>
          <div style={kicker}>ACOMPÁÑAME A COMENZAR</div>
        </Pop>
        <Pop at={d} kind="scale">
          <div style={{ display: "flex", alignItems: "baseline", gap: 26 }}>
            <span style={display(150)}>día</span>
            <span style={{ ...display(220, COLORS.durazno), fontFamily: FONTS.body, fontWeight: 700 }}>1</span>
          </div>
        </Pop>
      </Top>
      <Bottom>
        <Calendario desde={d + 0.15} soloDia1 />
      </Bottom>
    </>
  );
};

type Beat = { nombre: string; desde: number; hasta: number; Comp: React.FC };

const BEATS: Beat[] = [
  { nombre: "Reto 21 días", desde: 0, hasta: at("durante").start, Comp: Reto },
  { nombre: "3 semanas", desde: at("las próximas").start, hasta: at("luma body").start - 0.1, Comp: TresSemanas },
  { nombre: "Luma Body + aceite", desde: at("luma body").start - 0.1, hasta: at("de forma gradual").end + 0.2, Comp: Combo },
  { nombre: "Gradual", desde: at("de forma gradual").start - 0.2, hasta: at("y podrás hacer").start + 0.4, Comp: Gradual },
  { nombre: "15 min", desde: at("15 minutos").start - 0.15, hasta: at("rutina para ti").start - 0.1, Comp: Temporizador },
  { nombre: "Rutina", desde: at("rutina para ti").start - 0.4, hasta: at("no recibiste").start, Comp: Rutina },
  { nombre: "+ Guía", desde: at("no recibiste").start, hasta: at("en la primera semana").start, Comp: MasGuia },
  { nombre: "Checklist guía", desde: at("donde sabrás").start, hasta: at("en la primera semana").start, Comp: Guia },
  { nombre: "Plan 3 semanas", desde: at("en la primera semana").start, hasta: at("no necesitas hacerlo").start, Comp: Semanas },
  { nombre: "Perfecto → constante", desde: at("no necesitas hacerlo").start, hasta: at("recuerda guardar").start, Comp: Constante },
  { nombre: "Claves", desde: at("constante").start + 0.2, hasta: at("recuerda guardar").start, Comp: Claves },
  { nombre: "Calendario", desde: at("recuerda guardar").start, hasta: at("además").start, Comp: GuardaCalendario },
  { nombre: "Espacio", desde: at("además").start, hasta: at("acompáñame").start, Comp: Espacio },
  { nombre: "Día 1", desde: at("acompáñame").start, hasta: DURATION + 1, Comp: Dia1 },
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
