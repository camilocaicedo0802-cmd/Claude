import React from "react";
import { AbsoluteFill } from "remotion";
import { Phone } from "../components/Phone";
import { CreditCard } from "../components/Props";
import { TextBlock } from "../components/TextBlock";
import { easeIn, easeInOut, easeOut, kf } from "../lib/anim";
import { useSceneTime } from "../lib/useSceneTime";
import { BAND, C, PHONE_E2 } from "../theme";

export const S02 = { start: 5.9, end: 10.45 };

const PH_H = PHONE_E2.w * 2.05;

/**
 * E2 (papel + franja): la franja que arrastraron las monedas recibe la tarjeta (giro 3D moderado, entrada diagonal);
 * "cuenta bancaria" se lee unas décimas y se tacha justo cuando la voz cambia de idea; la tarjeta sale y la franja
 * SE TRANSFORMA en el móvil. Al final el entorno pasa a negro mientras el móvil se queda en su sitio.
 */
export const S02Bolsillo: React.FC<{ start?: number }> = ({ start = S02.start }) => {
  const { t, g } = useSceneTime(start);

  // tarjeta: entrada diagonal 3D (sin rebote) y salida diagonal tras el tachado
  const cin = kf(g, [6.86, 7.45], [0, 1], easeOut);
  const cout = kf(g, [8.45, 8.85], [0, 1], easeIn);
  const drift = Math.sin(t * 1.3) * 6;
  const cardX = 1250 + (540 - 1250) * cin - cout * 760 + drift;
  const cardY = 620 + (BAND.y - 620) * cin + cout * 620;
  const cardRot = 14 + (-6 - 14) * cin - cout * 24;
  const cardRotY = 38 + (6 - 38) * cin;

  // tachado de izquierda a derecha cuando la voz cambia de idea ("está en tu bolsillo" empieza en 8.51 s)
  const strike = kf(g, [8.2, 8.45], [0, 1], easeInOut);

  // la franja se convierte en el cuerpo del móvil
  const m = kf(g, [8.55, 9.15], [0, 1], easeInOut);
  const L = -60 + (PHONE_E2.cx - PHONE_E2.w / 2 + 60) * m;
  const R = 1140 + (PHONE_E2.cx + PHONE_E2.w / 2 - 1140) * m;
  const T = BAND.y - BAND.h / 2 + (PHONE_E2.cy - PH_H / 2 - (BAND.y - BAND.h / 2)) * m;
  const B = BAND.y + BAND.h / 2 + (PHONE_E2.cy + PH_H / 2 - (BAND.y + BAND.h / 2)) * m;
  const phoneIn = kf(g, [8.95, 9.2], [0, 1]);

  // el entorno pasa a negro desde el móvil, que se queda quieto
  const env = kf(g, [9.95, 10.45], [0, 2300], easeIn);

  return (
    <AbsoluteFill style={{ backgroundColor: C.paper }}>
      {phoneIn < 1 && <div style={{ position: "absolute", left: L, top: T, width: R - L, height: B - T, borderRadius: 75 * m, background: C.ink }} />}
      {cout < 1 && <CreditCard cx={cardX} cy={cardY} w={600} rotate={cardRot} rotY={cardRotY} opacity={kf(g, [6.86, 7.0], [0, 1])} />}

      <TextBlock g={g} guide={[16, 19]} keyw={[20, 21]} x={130} y={300} keySize={112} exitAt={9.9} />
      {strike > 0 && kf(g, [9.9, 10.18], [1, 0]) > 0 && (
        <div
          style={{
            position: "absolute",
            left: 120,
            top: 300 + 72 * 1.22 - 7 + 112 * 0.5 - 5,
            width: 820 * strike,
            height: 10,
            background: C.ink,
            rotate: "-1.5deg",
            transformOrigin: "0 50%",
            borderRadius: 5,
            opacity: kf(g, [9.9, 10.18], [1, 0]),
          }}
        />
      )}

      {env > 0 && (
        <div style={{ position: "absolute", left: PHONE_E2.cx - env, top: PHONE_E2.cy - env, width: env * 2, height: env * 2, borderRadius: "50%", background: C.night }} />
      )}
      {phoneIn > 0 && (
        <Phone cx={PHONE_E2.cx} cy={PHONE_E2.cy} w={PHONE_E2.w} screen="#1d1d1e" rim={0.35 + 0.4 * kf(g, [9.95, 10.4], [0, 1])} style={{ opacity: phoneIn }}>
          <div style={{ position: "absolute", top: 110, width: "100%", textAlign: "center", fontFamily: "Archivo", fontWeight: 600, color: "#e8e8e8", fontSize: 100, letterSpacing: "-0.02em", opacity: 0.88 }}>
            23:47
          </div>
        </Phone>
      )}
      <TextBlock g={g} guide={[22, 24]} keyw={[25, 25]} x={540} y={1600} align="center" keySize={124} exitAt={9.9} />
    </AbsoluteFill>
  );
};
