const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.cwd() + '/measure.html');
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const target = {s1:365, s2:330, k1:376, k2:272, k3:212, h1:920, h2:765, h3:1180};
  const w = await p.evaluate(() => Object.fromEntries([...document.querySelectorAll('span')].map(s => [s.id, s.getBoundingClientRect().width])));
  for (const k in w) console.log(k, 'w100=', w[k].toFixed(0), ' -> font-size para ancho', target[k], '=', (100*target[k]/w[k]).toFixed(1), 'px');
  await b.close();
})();
