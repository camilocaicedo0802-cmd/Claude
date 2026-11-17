const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 3260, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + process.cwd() + '/overlay.html');
  await p.evaluate(() => document.fonts.ready);
  console.log(JSON.stringify(await p.evaluate(() => window.go())));
  await p.waitForTimeout(300);
  await p.screenshot({ path: 'overlay.png' });
  await b.close();
})();
