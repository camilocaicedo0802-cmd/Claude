import React, { useCallback, useRef } from "react";
import { AbsoluteFill, Easing, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from "remotion";
import { CUTS, EDL, Highlight as H, Segment, segmentAt, zoomAt } from "../edl";
import { CAP, SF } from "../fonts";

const W = 1080;
const H_ = 1920;
const LINE = 0.92; // interlineado de la palabra grande (estilo.md)
const TRACK = -0.055; // interletraje en em (medido sobre "CLIENTES")

const fit = (lines: string[], size: number) => {
  // ancho aproximado de SF Pro Display Black en mayúsculas (0,64 em por carácter con el tracking)
  const longest = Math.max(...lines.map((l) => l.length));
  const est = longest * size * 0.64;
  return est > 1000 ? (size * 1000) / est : size;
};

/** Colores de la textura (medidos en la referencia). */
const RED_DARK = [215, 0, 0];
const RED_LIGHT = [253, 64, 64];

/**
 * Pinta en `out` la textura de un fotograma: el vídeo posterizado a dos rojos (rojo) o
 * en grises muy claros (blanco). Se calcula a media resolución y se escala.
 */
const paintTexture = (out: HTMLCanvasElement, img: CanvasImageSource, isWhite: boolean, place: (ctx: CanvasRenderingContext2D, k: number) => void) => {
  const k = 0.5;
  const tw = W * k;
  const th = H_ * k;
  if (out.width !== tw) {
    out.width = tw;
    out.height = th;
  }
  const ctx = out.getContext("2d", { willReadFrequently: true })!;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, tw, th);
  place(ctx, k);
  ctx.drawImage(img, 0, 0, W, H_);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  const data = ctx.getImageData(0, 0, tw, th);
  const d = data.data;
  for (let i = 0; i < d.length; i += 4) {
    const lum = (0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]) / 255;
    if (isWhite) {
      const v = Math.round(255 * (0.8 + 0.2 * lum));
      d[i] = v;
      d[i + 1] = v;
      d[i + 2] = v;
    } else {
      const c = lum < 0.62 ? RED_DARK : RED_LIGHT;
      d[i] = c[0];
      d[i + 1] = c[1];
      d[i + 2] = c[2];
    }
    d[i + 3] = 255;
  }
  ctx.putImageData(data, 0, 0);
};

/**
 * Palabra grande con la textura de la referencia, pintada en canvas (bordes suavizados y
 * letras exactas): color base + vídeo de la toma convertido en textura + recorte con la
 * forma de las letras (SF Pro Display Black). Sin franjas desplazadas.
 */
const BigWord: React.FC<{ h: H; seg: Segment; start: number }> = ({ h, seg, start }) => {
  const frame = useCurrentFrame();
  const canvas = useRef<HTMLCanvasElement>(null);
  const tex = useRef<HTMLCanvasElement | null>(null);
  const g = start + frame; // fotograma global
  const lines = h.big.split("\n");
  const size = fit(lines, h.layout.size);
  const top = h.layout.bigY;
  const bottom = top + size * (CAP + (lines.length - 1) * LINE) + size * 0.12;
  const since = g - h.bFrom;
  const isWhite = h.style === "white";
  const offset = start - seg.from_; // fotograma local de la toma en el que empieza esta secuencia

  const draw = useCallback(
    (img: CanvasImageSource) => {
      const c = canvas.current;
      if (!c) return;
      if (!tex.current) tex.current = document.createElement("canvas");
      // misma transformación que la toma (reencuadre) + desplazamiento de la textura
      const z = zoomAt(seg, offset + frame);
      const ox = (z.ox / 100) * W;
      const oy = (z.oy / 100) * H_;
      const shift = isWhite ? [-10, 6] : [-28, 16];
      const extra = isWhite ? 1.02 : 1.05;
      paintTexture(tex.current, img, isWhite, (ctx, k) => {
        ctx.setTransform(k, 0, 0, k, 0, 0);
        ctx.translate(W / 2 + shift[0], H_ / 2 + shift[1]);
        ctx.scale(extra, extra);
        ctx.translate(-W / 2, -H_ / 2);
        ctx.translate(ox, oy);
        ctx.scale(z.s, z.s);
        ctx.translate(-ox, -oy);
      });
      const ctx = c.getContext("2d")!;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.globalCompositeOperation = "source-over";
      ctx.globalAlpha = 1;
      ctx.clearRect(0, 0, W, H_);
      // 1) todas las letras (todas las líneas) como forma
      ctx.fillStyle = "#000";
      ctx.font = `900 ${size}px "${SF}"`;
      (ctx as unknown as { letterSpacing: string }).letterSpacing = `${(TRACK * size).toFixed(2)}px`;
      ctx.textAlign = h.layout.align;
      ctx.textBaseline = "alphabetic";
      lines.forEach((l, i) => ctx.fillText(l, h.layout.x, top + size * CAP + i * size * LINE));
      // 2) color base solo dentro de las letras (conserva el suavizado del borde)
      ctx.globalCompositeOperation = "source-in";
      ctx.fillStyle = isWhite ? "#FFFFFF" : "#E10000";
      ctx.fillRect(0, 0, W, H_);
      // 3) textura del vídeo encima, también solo dentro de las letras
      ctx.globalCompositeOperation = "source-atop";
      ctx.globalAlpha = isWhite ? 0.9 : 0.88;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(tex.current, 0, 0, W, H_);
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = "source-over";
    },
    [frame, h, isWhite, lines, offset, seg, size, top],
  );

  // entrada: rojo = aparición seca con escala 1,10 -> 1; blanco = zoom-blur 1,25 -> 1 y desenfoque 20 -> 0
  const inDur = isWhite ? 4 : 3;
  const scale = interpolate(Math.max(0, since), [0, inDur], [isWhite ? 1.25 : 1.1, 1], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const blur = isWhite ? interpolate(Math.max(0, since), [0, inDur], [20, 0], { extrapolateRight: "clamp" }) : 0;
  const fadeOut = CUTS.has(h.to) ? 1 : interpolate(g, [h.to - 6, h.to], [1, 0.3], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const opacity = since < 0 ? 0 : Math.min(interpolate(since, [0, 1], [0.4, 1], { extrapolateRight: "clamp" }), fadeOut);

  return (
    <AbsoluteFill>
      {/* vídeo de la toma solo como fuente de la textura (invisible) */}
      <AbsoluteFill style={{ opacity: 0 }}>
        <OffthreadVideo
          src={staticFile(seg.file)}
          trimBefore={offset}
          muted
          onVideoFrame={draw}
          style={{ width: "100%", height: "100%" }}
        />
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          opacity,
          scale: String(scale),
          transformOrigin: `${h.layout.x}px ${(top + bottom) / 2}px`,
          // las blancas llevan una sombra suave para leerse sobre paredes claras
          filter:
            [blur > 0.2 ? `blur(${blur}px)` : "", isWhite ? "drop-shadow(0 6px 22px rgba(0,0,0,0.32))" : ""].join(" ").trim() ||
            undefined,
        }}
      >
        <canvas ref={canvas} width={W} height={H_} style={{ width: W, height: H_ }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Texto pequeño (kicker) tecleado letra a letra. */
const Kicker: React.FC<{ h: H; start: number }> = ({ h, start }) => {
  const frame = useCurrentFrame();
  const g = start + frame;
  if (!h.kicker || h.kFrom === null || g < h.kFrom) return null;
  const n = Math.min(h.kicker.length, g - h.kFrom + 1);
  const size = Math.max(54, Math.min(104, h.layout.size * 0.42));
  const fadeOut = CUTS.has(h.to) ? 1 : interpolate(g, [h.to - 6, h.to], [1, 0.3], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const align = h.layout.align;
  return (
    <div
      style={{
        position: "absolute",
        top: h.layout.kickerY - size * 0.95,
        left: align === "left" ? h.layout.x + 8 : undefined,
        right: align === "right" ? W - h.layout.x + 8 : undefined,
        width: align === "center" ? W : undefined,
        textAlign: align,
        fontFamily: SF,
        fontWeight: 300,
        fontStyle: h.kickerItalic ? "italic" : "normal",
        fontSize: size,
        lineHeight: 1,
        color: "#FFFFFF",
        letterSpacing: "0.01em",
        whiteSpace: "pre",
        textShadow: "0 2px 10px rgba(0,0,0,0.35)",
        opacity: fadeOut,
      }}
    >
      {/* la parte aún no tecleada ocupa su sitio pero es invisible: el bloque no se recoloca */}
      {h.kicker.slice(0, n)}
      <span style={{ opacity: 0 }}>{h.kicker.slice(n)}</span>
    </div>
  );
};

export const HighlightItem: React.FC<{ h: H; index: number; part: "big" | "kicker" }> = ({ h, index, part }) => {
  const start = Math.min(h.kFrom ?? h.bFrom, h.bFrom);
  const seg = segmentAt(h.bFrom);
  if (!seg) return null;
  return (
    <Sequence from={start} durationInFrames={h.to - start} name={`${part === "big" ? "Palabra" : "Kicker"} ${h.big.replace("\n", " ")}`}>
      {part === "big" ? <BigWord h={h} seg={seg} start={start} /> : <Kicker h={h} start={start} />}
    </Sequence>
  );
};

/**
 * Capas de destacados. "behind": palabras grandes que van detrás de la persona.
 * "front": palabras grandes delante + todos los kickers (siempre delante).
 */
export const HighlightsLayer: React.FC<{ layer: "behind" | "front" }> = ({ layer }) => (
  <>
    {EDL.highlights.map((h, i) => (
      <React.Fragment key={i}>
        {h.behind === (layer === "behind") ? <HighlightItem h={h} index={i} part="big" /> : null}
        {layer === "front" && h.kicker ? <HighlightItem h={h} index={i} part="kicker" /> : null}
      </React.Fragment>
    ))}
  </>
);
