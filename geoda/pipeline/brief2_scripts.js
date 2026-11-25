const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const url = process.argv[2], out = process.argv[3];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1400, height: 1000 } });
  await p.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
  await p.waitForTimeout(4000);
  const f = p.frames().find(x => x.url().includes('__cursor/frame'));
  const re = /^GEO-(TOFU|MOFU|BOFU)-A\d+-\d+ · /;
  // abrir todas las secciones de ángulos
  const secs = await f.$$eval('*', els => [...new Set(els.map(e => (e.innerText || '').trim()).filter(t => /^Guiones A\d+ · /.test(t) && t.split('\n').length === 1))]);
  console.log('secciones', secs.length);
  for (const sname of secs.filter(x => !x.startsWith(process.argv[4] || "~"))) {
    const all = f.getByText(sname, { exact: true });
    const n = await all.count();
    for (let k = n - 1; k >= 0; k--) { try { const el = all.nth(k); await el.scrollIntoViewIfNeeded({ timeout: 2000 }); await el.click({ timeout: 2000 }); await p.waitForTimeout(300); } catch (e) {} }
  }
  await p.waitForTimeout(1000);
  const res = {};
  const ids = await f.$$eval('*', els => {
    const out = [];
    for (const e of els) {
      const t = (e.innerText || '').trim();
      if (/^GEO-(TOFU|MOFU|BOFU)-A\d+-\d+ · /.test(t) && t.split('\n').length === 1 && e.children.length <= 3) out.push(t);
    }
    return [...new Set(out)];
  });
  console.log('headers', ids.length);
  for (const h of ids) {
    const id = h.split(' · ')[0];
    try {
      const el = f.getByText(h, { exact: true }).first();
      await el.scrollIntoViewIfNeeded({ timeout: 3000 });
      await el.click({ timeout: 3000 });
      await p.waitForTimeout(700);
      const t = await f.evaluate(() => document.body.innerText);
      const i = t.indexOf(h);
      // bloque desde el encabezado hasta el siguiente encabezado de guion o fin de sección
      let rest = t.slice(i + h.length);
      const m = rest.search(/\nGEO-(TOFU|MOFU|BOFU)-A\d+-\d+ · |\nGuiones A\d+ · |\nChecklist de los 60 videos/);
      res[id] = h + '\n' + (m > 0 ? rest.slice(0, m) : rest.slice(0, 6000));
      // volver a plegar si quedó abierto y el siguiente no se ve
    } catch (e) { res[id] = 'ERROR ' + e; }
  }
  fs.writeFileSync(out, JSON.stringify(res, null, 1));
  console.log('ok', Object.keys(res).length);
  await b.close();
})();
