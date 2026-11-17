const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2170, height: 1920 } });
  await p.goto('file://' + process.cwd() + '/bold_stroke.html');
  console.log(JSON.stringify(await p.evaluate(() => window.go())));
  await p.screenshot({ path: 'bold_stroke.png' }); await b.close();
})();
