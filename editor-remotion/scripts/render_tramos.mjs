// Render por tramos (cada tramo abre y cierra su propio navegador, así la memoria no se acumula) y unión sin
// recomprimir. Es reanudable: los tramos ya renderizados se saltan.
//   node scripts/render_tramos.mjs ArmandoBitsHorizontal out/armando-bits-opcionB-render.mp4
// Renderiza solo la imagen; el audio se saca aparte (npx remotion render <id> mezcla.wav --codec=wav).
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const [id, output] = process.argv.slice(2);
const TRAMO = 600; // fotogramas por tramo (10 s)
const dir = `out/tramos-${id}`;
fs.mkdirSync(dir, { recursive: true });

const frames = (file) => Number(execFileSync("ffprobe", ["-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", file]).toString().trim());

const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), webpackOverride: (c) => c });
const composition = await selectComposition({ serveUrl, id });
const parts = [];
for (let a = 0; a < composition.durationInFrames; a += TRAMO) {
  const b = Math.min(composition.durationInFrames, a + TRAMO) - 1;
  const file = `${dir}/t_${String(a).padStart(5, "0")}.mp4`;
  parts.push(file);
  if (fs.existsSync(file) && frames(file) === b - a + 1) {
    console.log("ya estaba", file);
    continue;
  }
  const t0 = Date.now();
  await renderMedia({ composition, serveUrl, codec: "h264", outputLocation: file, frameRange: [a, b], muted: true, crf: 17, jpegQuality: 92, imageFormat: "jpeg", concurrency: 3, mediaCacheSizeInBytes: 2_500_000_000, logLevel: "error", overwrite: true });
  console.log("ok", file, frames(file), "fotogramas ·", Math.round((Date.now() - t0) / 1000), "s");
}
// Unión sin recomprimir (MPEG-TS intermedio).
const ts = parts.map((p) => {
  const out = p.replace(/\.mp4$/, ".ts");
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", p, "-c", "copy", "-bsf:v", "h264_mp4toannexb", "-f", "mpegts", out]);
  return out;
});
execFileSync("ffmpeg", ["-v", "error", "-y", "-i", `concat:${ts.join("|")}`, "-c", "copy", "-movflags", "+faststart", output]);
ts.forEach((f) => fs.unlinkSync(f));
console.log("UNIDO", output, frames(output), "fotogramas");
