// usage: node render_overlay.mjs <timeline.json> <outdir> <startFrame> <endFrame> [times...]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
const [,, tlPath, outDir, sf, ef, ...extra] = process.argv;
const T = JSON.parse(fs.readFileSync(tlPath, 'utf8'));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto('file://' + path.resolve(__dirname, 'overlay.html'));
await page.evaluate(async (t) => await window.setup(t), T);
const stage = await page.$('#stage');
fs.mkdirSync(outDir, { recursive: true });
const frames = [];
if (extra.length) extra.forEach(x => frames.push(parseFloat(x)));
else for (let f = parseInt(sf); f < parseInt(ef); f++) frames.push(f);
for (const f of frames) {
  const t = extra.length ? f : f / T.fps;
  await page.evaluate((tt) => window.renderAt(tt), t);
  const name = extra.length ? `t_${t.toFixed(2)}.png` : `${String(f).padStart(5, '0')}.png`;
  await stage.screenshot({ path: path.join(outDir, name), omitBackground: true });
}
await browser.close();

})();
