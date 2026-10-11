import React from "react";
import { AbsoluteFill } from "remotion";
import { Camera } from "../components/Camera";
import { Halo } from "../components/Overlays";
import { Glyph, Notification, Phone, VideoThumb } from "../components/Phone";
import { TextBlock } from "../components/TextBlock";
import { easeIn, easeInOut, kf, springy } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { C } from "../theme";

export const S03 = { start: 10.3, end: 16.1 };

const PW = 540; // ancho del móvil
const INSET = PW * 0.038;
const SW = PW - INSET * 2; // ancho de pantalla
const SH = PW * 2.05 - INSET * 2; // alto de pantalla

const NOTIFS = [
  { at: 10.8, kind: "chat", title: "Mensaje nuevo", body: "¿Viste lo que subieron?" },
  { at: 11.05, kind: "heart", title: "A 128 personas", body: "les gusta tu publicación" },
  { at: 11.3, kind: "bell", title: "En directo", body: "Empezó una transmisión" },
  { at: 11.55, kind: "play", title: "Para ti", body: "12 vídeos nuevos" },
] as const;

const FLOAT = [
  { at: 10.95, x: -10, y: 700, r: -8, kind: "bell", title: "Recordatorio", body: "Llevas 3 h en el móvil" },
  { at: 11.2, x: 600, y: 1290, r: 7, kind: "heart", title: "Nuevo seguidor", body: "y 47 más" },
  { at: 11.45, x: 20, y: 1540, r: -5, kind: "chat", title: "Grupo (99+)", body: "Te mencionaron" },
] as const;

/** E3 (oscura): notificaciones, vídeos y un feed que se desliza; texto con jerarquía invertida. */
export const S03Pantalla: React.FC<{ start?: number }> = ({ start = S03.start }) => {
  const { t, g } = useSceneTime(start);

  const camScale = kf(t, [0, 0.55], [1.35, 1.0]) * kf(t, [0.55, 5.8], [1, 1.07], easeInOut);
  const rot = Math.sin(t * 0.9) * 0.8;
  const fadeIn = kf(t, [0, 0.15], [1, 0]);

  const scatter = kf(g, [12.17, 12.5], [0, 1], easeIn); // notificaciones salen volando
  const gridIn = g >= 12.17 && g < 13.62;
  const feed = g >= 13.62;

  // desplazamiento del feed: tres gestos de deslizar
  const swipes = [14.44, 14.95, 15.3];
  const scroll = swipes.reduce((acc, s) => acc + kf(g, [s, s + 0.28], [0, 1], easeInOut), 0);
  const swiping = swipes.find((s) => g >= s - 0.05 && g <= s + 0.35);
  const fingerP = swiping !== undefined ? kf(g, [swiping - 0.05, swiping + 0.3], [0, 1], easeInOut) : -1;

  const playPop = springy(g, 12.6, 0.4, 0.15);

  return (
    <AbsoluteFill style={{ backgroundColor: C.night }}>
      <Camera cx={540} cy={1000} scale={camScale} rotate={rot}>
        <Halo cx={540} cy={1180} w={900} h={1400} opacity={0.9} />
        <Phone cx={540} cy={1180} w={PW} screen={feed ? "#0f0f10" : "#1d1d1e"} glow={0.5}>
          {/* pantalla de bloqueo con la hora */}
          {!feed && (
            <div
              style={{
                position: "absolute",
                top: 90,
                width: "100%",
                textAlign: "center",
                fontFamily: "Archivo",
                fontWeight: 600,
                color: "#e8e8e8",
                fontSize: 104,
                letterSpacing: "-0.02em",
                opacity: 0.88 * (1 - scatter * 0.6),
              }}
            >
              23:47
            </div>
          )}
          {/* notificaciones apiladas */}
          {!feed &&
            NOTIFS.map((n, i) => {
              const s = springy(g, n.at, 0.4, 0.1);
              if (s <= 0) return null;
              const fly = scatter * (i % 2 === 0 ? -1 : 1);
              return (
                <Notification
                  key={i}
                  x={SW * 0.05 + fly * 700}
                  y={260 + i * 132 - (1 - s) * 80 - scatter * 120}
                  w={SW * 0.9}
                  kind={n.kind}
                  title={n.title}
                  body={n.body}
                  scale={0.85 + 0.15 * s}
                  opacity={Math.min(1, s * 1.5) * (1 - scatter)}
                  rotate={fly * 25}
                />
              );
            })}
          {/* rejilla de vídeos */}
          {gridIn &&
            new Array(6).fill(0).map((_, i) => {
              const s = springy(g, 12.22 + i * 0.07, 0.35, 0.12);
              const col = i % 2;
              const row = Math.floor(i / 2);
              const tw = SW * 0.44;
              const th = tw * 1.45;
              return (
                <VideoThumb
                  key={i}
                  x={SW * 0.04 + col * (tw + SW * 0.04)}
                  y={150 + row * (th + 18)}
                  w={tw}
                  h={th}
                  tone={((i * 37) % 10) / 10}
                  scale={0.6 + 0.4 * s}
                  opacity={Math.min(1, s * 2)}
                  progress={0.2 + i * 0.12}
                  showPlay={false}
                />
              );
            })}
          {gridIn && playPop > 0 && (
            <div
              style={{
                position: "absolute",
                left: SW / 2 - 110,
                top: SH / 2 - 110,
                width: 220,
                height: 220,
                borderRadius: "50%",
                background: "rgba(240,240,240,0.95)",
                scale: `${playPop}`,
                boxShadow: "0 20px 50px rgba(0,0,0,0.5)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <svg width={100} height={100} viewBox="0 0 24 24">
                <path d="M8 5l11 7-11 7z" fill="#141414" />
              </svg>
            </div>
          )}
          {/* feed vertical */}
          {feed &&
            new Array(6).fill(0).map((_, i) => (
              <VideoThumb
                key={i}
                x={0}
                y={(i - scroll) * SH}
                w={SW}
                h={SH}
                tone={((i * 53) % 10) / 10}
                radius={0}
                progress={0.15 + ((i * 29) % 70) / 100}
                showPlay={false}
              />
            ))}
          {feed && (
            <div style={{ position: "absolute", right: 22, bottom: 190, display: "flex", flexDirection: "column", alignItems: "center", gap: 26, fontFamily: "Archivo", fontWeight: 800, color: "#F0F0F0", fontSize: 22 }}>
              {(
                [
                  ["heart", `${(98 + Math.floor(scroll * 37)).toString()}k`],
                  ["chat", "2.1k"],
                  ["user", "+"],
                ] as const
              ).map(([k, label]) => (
                <div key={k} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                  <Glyph kind={k} size={58} />
                  <span>{label}</span>
                </div>
              ))}
            </div>
          )}
          {feed && (
            <div style={{ position: "absolute", left: 30, bottom: 70, fontFamily: "Archivo", color: "#F0F0F0" }}>
              <div style={{ fontWeight: 800, fontSize: 30 }}>@contenido_infinito</div>
              <div style={{ fontWeight: 600, fontSize: 24, opacity: 0.75 }}>no dejes de mirar…</div>
            </div>
          )}
          {/* dedo que desliza */}
          {fingerP >= 0 && (
            <div
              style={{
                position: "absolute",
                left: SW / 2 - 45,
                top: SH * (0.78 - 0.5 * fingerP) - 45,
                width: 90,
                height: 90,
                borderRadius: "50%",
                background: "rgba(255,255,255,0.35)",
                boxShadow: "0 0 0 6px rgba(255,255,255,0.55)",
                opacity: Math.sin(fingerP * Math.PI),
              }}
            />
          )}
        </Phone>
        {/* notificaciones flotando alrededor del móvil */}
        {FLOAT.map((n, i) => {
          const s = springy(g, n.at, 0.45, 0.12);
          if (s <= 0) return null;
          const fly = scatter * (i % 2 === 0 ? -1 : 1);
          return (
            <Notification
              key={i}
              x={n.x + fly * 600}
              y={n.y - scatter * 200}
              w={470}
              kind={n.kind}
              title={n.title}
              body={n.body}
              scale={0.7 + 0.3 * s}
              opacity={Math.min(1, s * 1.5) * (1 - scatter)}
              rotate={n.r + fly * 20}
            />
          );
        })}
      </Camera>

      {/* texto en pantalla (jerarquía invertida sobre negro) */}
      <TextBlock g={g} theme="dark" guide={[26, 26]} keyw={[27, 27]} x={110} y={150} keySize={150} exitAt={12.05} />
      <TextBlock g={g} theme="dark" guide={[28, 28]} keyw={[29, 29]} x={110} y={150} keySize={175} exitAt={13.5} />
      <TextBlock g={g} theme="dark" guide={[30, 32]} keyw={[33, 35]} x={110} y={140} width={880} keySize={122} />
      <AbsoluteFill style={{ backgroundColor: C.night, opacity: fadeIn }} />
    </AbsoluteFill>
  );
};
