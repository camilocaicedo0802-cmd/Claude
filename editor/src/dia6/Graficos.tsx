import React from "react";
import { interpolate } from "remotion";
import { COLORS, FONTS } from "../brand";
import { CARD, Pop } from "../rutinas/Graficos";
import { CLAMP, useT } from "../rutinas/util";

/** Lista que se va marcando: cada fila se enciende y su ✓ se dibuja en la palabra que la nombra. */
export const Lista: React.FC<{
  at: number;
  titulo: string;
  filas: { texto: string; at: number }[];
  style: React.CSSProperties;
}> = ({ at: atSec, titulo, filas, style }) => {
  const { t } = useT();
  return (
    <div style={{ position: "absolute", width: 300, ...style }}>
      <Pop at={atSec} kind="up">
        <div
          style={{
            background: CARD,
            borderRadius: 30,
            padding: "18px 20px 14px",
            boxShadow: "0 16px 40px rgba(69,89,90,.35)",
          }}
        >
          <div
            style={{
              fontFamily: FONTS.body,
              fontWeight: 700,
              fontSize: 22,
              letterSpacing: "0.2em",
              color: COLORS.durazno,
              marginBottom: 6,
            }}
          >
            {titulo}
          </div>
          {filas.map((f) => {
            const d = interpolate(t, [f.at, f.at + 0.3], [0, 1], CLAMP);
            return (
              <div
                key={f.texto}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 14,
                  padding: "7px 0",
                  opacity: 0.45 + 0.55 * d,
                }}
              >
                <svg width={38} height={38} viewBox="0 0 56 56">
                  <circle
                    cx={28}
                    cy={28}
                    r={25}
                    fill={d > 0 ? COLORS.salvia : "none"}
                    stroke={COLORS.durazno}
                    strokeWidth={d > 0 ? 0 : 4}
                  />
                  <path
                    d="M16 29 L25 38 L41 20"
                    stroke={COLORS.marfil}
                    strokeWidth={6}
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeDasharray={40}
                    strokeDashoffset={40 * (1 - d)}
                  />
                </svg>
                <div
                  style={{
                    fontFamily: FONTS.body,
                    fontWeight: 700,
                    fontSize: 27,
                    color: COLORS.marfil,
                    whiteSpace: "nowrap",
                    transform: `scale(${1 + 0.08 * Math.sin(d * Math.PI)})`,
                    transformOrigin: "left center",
                  }}
                >
                  {f.texto}
                </div>
              </div>
            );
          })}
        </div>
      </Pop>
    </div>
  );
};
