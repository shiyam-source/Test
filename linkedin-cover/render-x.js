// Renders x-header.html to X/Twitter header PNGs (1500x500 at 2x) in dark and cream variants.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1500, height: 500 }, deviceScaleFactor: 2 });
  await p.goto('file://' + path.join(__dirname, 'x-header.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(__dirname, 'slate-x-header-dark.png') });
  await p.evaluate(() => document.body.classList.add('cream'));
  await p.waitForTimeout(200);
  await p.screenshot({ path: path.join(__dirname, 'slate-x-header-cream.png') });
  // Preview with X's avatar and crop zones, for checking only
  await p.evaluate(() => { document.body.classList.remove('cream');
    document.body.insertAdjacentHTML('beforeend','<div style="position:absolute;left:40px;top:333px;width:335px;height:335px;border-radius:50%;background:rgba(255,0,0,.35)"></div><div style="position:absolute;left:0;right:0;top:0;height:60px;background:rgba(255,0,0,.15)"></div><div style="position:absolute;left:0;right:0;bottom:0;height:60px;background:rgba(255,0,0,.15)"></div>'); });
  await p.screenshot({ path: process.argv[2] || path.join(__dirname, 'zones.png'), scale: 'css' });
  await b.close();
})();
