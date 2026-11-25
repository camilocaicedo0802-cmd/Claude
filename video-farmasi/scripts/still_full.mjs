import fs from "node:fs";
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const [comp, ...ts] = process.argv.slice(2);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts"), publicDir: path.resolve("public") });
const composition = await selectComposition({ serveUrl, id: comp });
for (const t of ts.map(Number)) {
  const output = path.resolve(`out/stills/full_${comp}_${t.toFixed(2)}.png`);
  await renderStill({ serveUrl, composition, frame: Math.round(t * composition.fps), output, imageFormat: "png", scale: 1, chromiumOptions: { gl: "swangle" } });
  console.log("ok", output);
}
fs.rmSync(serveUrl, { recursive: true, force: true }); // no dejar copias del bundle en /tmp
