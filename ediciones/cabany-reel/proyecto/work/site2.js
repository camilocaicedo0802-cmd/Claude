const { chromium } = require('playwright');
(async () => {
  const out = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 430, height: 932 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  await p.goto('https://www.cabanypanama.com/', { waitUntil: 'networkidle', timeout: 60000 });
  await p.waitForTimeout(2000);
  const cards = await p.evaluate(() => [...document.querySelectorAll('a')].filter(a => a.querySelector('img')).map(a => {
    const img = a.querySelector('img'); return { href: a.href, img: img.currentSrc || img.src, alt: img.alt, text: a.innerText.replace(/\n+/g, ' | ') };
  }));
  console.log(JSON.stringify(cards.slice(0, 40), null, 0));
  require('fs').writeFileSync(out + '/cards.json', JSON.stringify(cards));
  const lcs = cards.find(c => /Luxury Canyon/i.test(c.alt));
  if (lcs) {
    const el = await p.$(`a[href="${new URL(lcs.href).pathname}"]`) || await p.$(`a[href="${lcs.href}"]`);
    if (el) { await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(800); await el.screenshot({ path: out + '/lcs_card.png' }); }
    await p.goto(lcs.href, { waitUntil: 'networkidle', timeout: 60000 }); await p.waitForTimeout(2500);
    await p.screenshot({ path: out + '/lcs_page.png' });
    const imgs = await p.evaluate(() => [...document.querySelectorAll('img')].map(i => (i.currentSrc || i.src) + ' | ' + i.alt));
    console.log('LCS IMGS', JSON.stringify(imgs.slice(0, 40)));
    require('fs').writeFileSync(out + '/lcs_imgs.json', JSON.stringify(imgs));
    console.log(await p.evaluate(() => document.body.innerText.slice(0, 2500)));
  }
  await b.close();
})();
