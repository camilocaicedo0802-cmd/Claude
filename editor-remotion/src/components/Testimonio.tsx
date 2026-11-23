// Prueba social: el vídeo vertical del alumno en una tarjeta, con chip «Testimonio» y rótulo de nombre.
import React from "react";
import { Video } from "@remotion/media";
import { AbsoluteFill, Easing, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { keys, ramp } from "../anim";
import { C, FONT } from "../theme";
import { Segment } from "../timeline";

export const CARD = { x: 140, y: 250, w: 800, h: 940 };

export const Testimonio: React.FC<{ s: Segment; nombre: string; rol: string }> = ({ s, nombre, rol }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lt = frame / fps; // tiempo local
  const z = keys(lt, [[0, 1.12], [0.7, 1.0], [s.end - s.start, 1.07]]);
  const cover = (CARD.w / s.srcW) * z;
  const vw = s.srcW * cover;
  const vh = s.srcH * cover;
  const left = (CARD.w - vw) / 2 - 20 * z;
  const top = Math.min(0, Math.max(CARD.h - vh, CARD.h * 0.42 - 0.585 * vh));
  const chip = ramp(lt, 0.15, 0.18);
  const name = ramp(lt, 0.35, 0.2, Easing.out(Easing.cubic));
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, borderRadius: 40, overflow: "hidden", backgroundColor: "#000", boxShadow: "0 40px 120px rgba(0,0,0,0.8), 0 0 0 1px rgba(255,255,255,0.14)" }}>
        <Video src={staticFile(s.file)} volume={0.9} style={{ position: "absolute", left, top, width: vw, height: vh, maxWidth: "none", filter: "contrast(1.08) saturate(0.94) brightness(0.94)" }} />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.72) 100%)" }} />
        <div style={{ position: "absolute", left: 28, top: 28, height: 54, padding: "0 22px", borderRadius: 30, display: "flex", alignItems: "center", gap: 12, background: "rgba(10,10,10,0.72)", border: "1px solid rgba(255,255,255,0.2)", fontFamily: FONT.wide, fontSize: 23, letterSpacing: "0.2em", color: C.white, opacity: chip, translate: `${-14 * (1 - chip)}px 0px` }}>
          <span style={{ width: 11, height: 11, borderRadius: 11, background: C.redDot, boxShadow: "0 0 10px rgba(212,0,42,0.9)" }} />
          TESTIMONIO
        </div>
        <div style={{ position: "absolute", left: 34, bottom: 30, opacity: name, translate: `0px ${16 * (1 - name)}px` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <span style={{ width: 6, height: 62, borderRadius: 6, background: C.lime, boxShadow: `0 0 16px ${C.limeGlow}` }} />
            <div>
              <div style={{ fontFamily: FONT.grotesk, fontWeight: 700, fontSize: 56, letterSpacing: "-0.04em", lineHeight: 1, color: C.white, textShadow: "0 4px 18px rgba(0,0,0,0.7)" }}>{nombre}</div>
              <div style={{ marginTop: 6, fontFamily: FONT.wide, fontWeight: 300, fontSize: 25, color: "rgba(255,255,255,0.82)" }}>{rol}</div>
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
