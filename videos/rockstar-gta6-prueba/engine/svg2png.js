// usage: node svg2png.js in.svg out.png width height
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [inp, out, w, h] = process.argv.slice(2);
  const svg = fs.readFileSync(inp, 'utf8');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +w, height: +h } });
  await p.setContent(`<html><body style="margin:0;background:transparent"><div style="width:${w}px;height:${h}px;display:flex;align-items:center;justify-content:center">${svg.replace(/<\?xml[^>]*>/,'').replace('<svg','<svg style="width:100%;height:100%"')}</div></body></html>`);
  await p.screenshot({ path: out, omitBackground: true });
  await b.close();
})();
