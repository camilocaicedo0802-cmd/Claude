import React from "react";
import { AbsoluteFill } from "remotion";
import { Camera } from "../components/Camera";
import { Halo } from "../components/Overlays";
import { Glyph, Notification, Phone, VideoThumb } from "../components/Phone";
import { TextBlock } from "../components/TextBlock";
import { easeIn, easeInOut, easeOut, kf, springy } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C, PHONE_E2 } from "../theme";

export const S03 = { start: 10.4, end: 16.1 };

const PW = PHONE_E2.w;
const INSET = PW * 0.038;
const SW = PW - INSET * 2;
const SH = PW * 2.05 - INSET * 2;

// notificaciones dentro del móvil: la primera sola y después cada vez más seguidas (0.42 → 0.16 s)
const NOTIFS = [
  { at: 10.8, kind: "chat", title: "Mensaje nuevo", body: "¿Viste lo que subieron?", dx: 0, s: 1 },
  { at: 11.22, kind: "heart", title: "A 128 personas", body: "les gusta tu publicación", dx: -8, s: 0.98 },
  { at: 11.52, kind: "bell", title: "En directo", body: "Empezó una transmisión", dx: 10, s: 0.99 },
  { at: 11.74, kind: "play", title: "Para ti", body: "12 vídeos nuevos", dx: -5, s: 0.97 },
  { at: 11.9, kind: "user", title: "Nuevo seguidor", body: "y 47 personas más", dx: 6, s: 0.98 },
] as const;

// notificaciones flotando alrededor, con profundidad distinta (escala, desenfoque, opacidad)
const FLOAT = [
  { at: 11.08, x: -30, y: 640, r: -8, depth: 0.8, kind: "bell", title: "Recordatorio", body: "Llevas 3 h en el móvil" },
  { at: 11.4, x: 610, y: 1260, r: 7, depth: 1.05, kind: "heart", title: "Te mencionaron", body: "en un comentario" },
  { at: 11.64, x: 0, y: 1500, r: -5, depth: 0.92, kind: "chat", title: "Grupo (99+)", body: "Mensajes sin leer" },
  { at: 11.82, x: 640, y: 560, r: 6, depth: 0.85, kind: "play", title: "En vivo ahora", body: "No te lo pierdas" },
  { at: 11.96, x: 40, y: 1080, r: -9, depth: 0.78, kind: "user", title: "Sugerencia", body: "Personas que quizá conozcas" },
] as const;

const SWIPES = [
  { at: 14.44, dur: 0.38 },
  { at: 14.95, dur: 0.3 },
  { at: 15.3, dur: 0.22 },
  { at: 15.52, dur: 0.16 },
];
const BUZZ = [10.8, 11.9, 15.52]; // vibración solo cuando suena el SFX de vibración

/** E3 (oscura): el móvil de E2 sigue en su sitio; notificaciones progresivas, vídeos y un feed que acelera. */
export const S03Pantalla: React.FC<{ start?: number }> = ({ start = S03.start }) => {
  const { g } = useSceneTime(start);

  // cámara: estable al principio (continuidad con E2) y se acerca para el feed
  const camScale = 1 + 0.04 * kf(g, [10.4, 11.6], [0, 1], easeInOut) + 0.09 * kf(g, [13.35, 14.1], [0, 1], easeInOut);
  const camY = 960 + 40 * kf(g, [13.35, 14.1], [0, 1], easeInOut);

  const scatter = kf(g, [12.17, 12.5], [0, 1], easeIn);
  const gridIn = g >= 12.17 && g < 13.62;
  const feed = g >= 13.62;

  const scroll = SWIPES.reduce((acc, s) => acc + kf(g, [s.at, s.at + s.dur], [0, 1], easeInOut), 0);
  const sw = SWIPES.find((s) => g >= s.at - 0.04 && g <= s.at + s.dur + 0.04);
  const fingerP = sw ? kf(g, [sw.at - 0.04, sw.at + sw.dur], [0, 1], easeInOut) : -1;
  const buzz = BUZZ.find((b) => g >= b && g < b + 0.18);
  const shake = buzz !== undefined ? Math.sin((g - buzz) * 220) * 4 * (1 - (g - buzz) / 0.18) : 0;

  // toque final: círculo que servirá de match cut con el círculo del reloj (E4)
  const tap = kf(g, [15.72, 15.82], [0, 1], easeOut);

  const playPop = springy(g, 12.6, 0.4, 0.12);

  return (
    <AbsoluteFill style={{ backgroundColor: C.night }}>
      <Camera cx={540} cy={camY} scale={camScale}>
        <Halo cx={PHONE_E2.cx} cy={PHONE_E2.cy} w={900} h={1400} opacity={0.9} />
        <Phone cx={PHONE_E2.cx} cy={PHONE_E2.cy} w={PW} screen={feed ? "#101011" : "#1d1d1e"} glow={0.45} rim={0.75} shake={shake}>
          {!feed && (
            <div style={{ position: "absolute", top: 90, width: "100%", textAlign: "center", fontFamily: "Archivo", fontWeight: 600, color: "#e8e8e8", fontSize: 100, letterSpacing: "-0.02em", opacity: 0.88 * (1 - scatter * 0.6) }}>
              23:47
            </div>
          )}
          {!feed &&
            NOTIFS.map((n, i) => {
              const s = springy(g, n.at, 0.32, 0.06);
              if (s <= 0) return null;
              const fly = scatter * (i % 2 === 0 ? -1 : 1);
              return (
                <Notification
                  key={i}
                  x={SW * 0.05 + n.dx + fly * 700}
                  y={250 + i * 122 - (1 - s) * 70 - scatter * 120}
                  w={SW * 0.9}
                  kind={n.kind}
                  title={n.title}
                  body={n.body}
                  scale={(0.86 + 0.14 * s) * n.s}
                  opacity={Math.min(1, s * 1.6) * (1 - scatter)}
                  rotate={fly * 25}
                />
              );
            })}
          {gridIn &&
            new Array(6).fill(0).map((_, i) => {
              const s = springy(g, 12.22 + i * 0.07, 0.35, 0.1);
              const tw = SW * 0.44;
              const th = tw * 1.45;
              return (
                <VideoThumb key={i} x={SW * 0.04 + (i % 2) * (tw + SW * 0.04)} y={140 + Math.floor(i / 2) * (th + 16)} w={tw} h={th} tone={0.45 + ((i * 37) % 10) / 18} scale={0.6 + 0.4 * s} opacity={Math.min(1, s * 2)} progress={0.2 + i * 0.12} showPlay={false} />
              );
            })}
          {gridIn && playPop > 0 && (
            <div style={{ position: "absolute", left: SW / 2 - 105, top: SH / 2 - 105, width: 210, height: 210, borderRadius: "50%", background: "rgba(245,245,245,0.96)", scale: `${playPop}`, boxShadow: "0 20px 50px rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <svg width={96} height={96} viewBox="0 0 24 24">
                <path d="M8 5l11 7-11 7z" fill="#141414" />
              </svg>
            </div>
          )}
          {feed &&
            new Array(7).fill(0).map((_, i) => (
              // contenido del feed más claro y contrastado para que se lea en móvil
              <VideoThumb key={i} x={0} y={(i - scroll) * SH} w={SW} h={SH} tone={0.55 + ((i * 53) % 10) / 22} radius={0} progress={0.15 + ((i * 29) % 70) / 100} showPlay={false} />
            ))}
          {feed && (
            <>
              <div style={{ position: "absolute", right: 20, bottom: 190, display: "flex", flexDirection: "column", alignItems: "center", gap: 24, fontFamily: "Archivo", fontWeight: 800, color: "#F4F4F4", fontSize: 24, textShadow: "0 2px 8px rgba(0,0,0,0.5)" }}>
                {(
                  [
                    ["heart", `${98 + Math.floor(scroll * 37)}k`],
                    ["chat", "2.1k"],
                    ["user", "+"],
                  ] as const
                ).map(([k, label]) => (
                  <div key={k} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                    <Glyph kind={k} size={60} color="#F4F4F4" />
                    <span>{label}</span>
                  </div>
                ))}
              </div>
              <div style={{ position: "absolute", left: 28, bottom: 64, fontFamily: "Archivo", color: "#F4F4F4", textShadow: "0 2px 8px rgba(0,0,0,0.5)" }}>
                <div style={{ fontWeight: 800, fontSize: 30 }}>@contenido_infinito</div>
                <div style={{ fontWeight: 600, fontSize: 24, opacity: 0.85 }}>no dejes de mirar…</div>
              </div>
            </>
          )}
          {fingerP >= 0 && (
            <div style={{ position: "absolute", left: SW / 2 - 45, top: SH * (0.78 - 0.5 * fingerP) - 45, width: 90, height: 90, borderRadius: "50%", background: "rgba(255,255,255,0.38)", boxShadow: "0 0 0 6px rgba(255,255,255,0.6)", opacity: Math.sin(fingerP * Math.PI) }} />
          )}
          {tap > 0 && (
            <div style={{ position: "absolute", left: SW / 2 - 45, top: SH / 2 - 45, width: 90, height: 90, borderRadius: "50%", background: "rgba(240,240,240,0.92)", boxShadow: "0 0 0 6px rgba(255,255,255,0.7)", scale: `${0.6 + 0.4 * tap}`, opacity: tap }} />
          )}
        </Phone>
        {FLOAT.map((n, i) => {
          const s = springy(g, n.at, 0.38, 0.08);
          if (s <= 0) return null;
          const fly = scatter * (i % 2 === 0 ? -1 : 1);
          const far = 1 - n.depth; // las lejanas, más pequeñas y algo desenfocadas
          return (
            <Notification
              key={i}
              x={n.x + fly * 600}
              y={n.y - scatter * 200}
              w={460}
              kind={n.kind}
              title={n.title}
              body={n.body}
              scale={(0.72 + 0.28 * s) * n.depth}
              opacity={Math.min(1, s * 1.5) * (1 - scatter) * (1 - far * 0.8)}
              rotate={n.r + fly * 20}
              blur={Math.max(0, far * 9)}
            />
          );
        })}
      </Camera>

      <TextBlock g={g} theme="dark" guide={[26, 26]} keyw={[27, 27]} x={110} y={140} keySize={132} exitAt={12.05} />
      <TextBlock g={g} theme="dark" guide={[28, 28]} keyw={[29, 29]} x={110} y={140} keySize={156} exitAt={13.5} />
      <TextBlock g={g} theme="dark" guide={[30, 32]} keyw={[33, 35]} x={110} y={110} width={880} keySize={108} reveal="scrollUp" />
    </AbsoluteFill>
  );
};
