const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const url = process.argv[2], out = process.argv[3];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 1000 } });
  await p.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
  await p.waitForTimeout(5000);
  let all = '';
  for (const f of p.frames()) {
    try {
      // expandir acordeones / detalles dentro del frame
      for (const sel of ['details:not([open]) > summary', '[aria-expanded="false"]']) {
        const els = await f.$$(sel);
        for (const e of els) { try { await e.click({ timeout: 300 }); } catch (err) {} }
      }
      await p.waitForTimeout(500);
      const t = await f.evaluate(() => document.body ? document.body.innerText : '');
      all += `\n===== FRAME ${f.url()} (${t.length})\n` + t;
      const h = await f.content();
      fs.writeFileSync(out + '.' + all.length + '.html', h);
    } catch (e) { all += `\n===== FRAME ${f.url()} ERROR ${e}`; }
  }
  fs.writeFileSync(out, all);
  console.log('frames', p.frames().length, 'chars', all.length);
  await b.close();
})();
