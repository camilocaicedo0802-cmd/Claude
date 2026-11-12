// Renderiza fotogramas sueltos de SlateReel para revisión: node scripts/stills.mjs 10 50 120 ...
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const frames = process.argv.slice(2).map(Number);
const outDir = process.env.OUT ?? "/home/user/media-in/work/stills";
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: "SlateReel" });
for (const f of frames) {
  await renderStill({ composition, serveUrl, frame: f, output: `${outDir}/f${String(f).padStart(3, "0")}.jpg`, imageFormat: "jpeg", jpegQuality: 85, scale: 0.5 });
  console.log("frame", f);
}
