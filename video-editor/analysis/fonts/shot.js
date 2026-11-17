const { chromium } = require('playwright');
(async () => {
  const [,, file, out, w] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: Number(w || 1500), height: 400 }, deviceScaleFactor: 1 });
  await p.goto('file://' + file);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(1500);
  await p.screenshot({ path: out, fullPage: true });
  await b.close();
})();
