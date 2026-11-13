// Renders cover.html to LinkedIn-size PNGs (1584x396 at 2x) in dark and cream variants.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1584, height: 396 }, deviceScaleFactor: 2 });
  await p.goto('file://' + path.join(__dirname, 'cover.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  await p.screenshot({ path: path.join(__dirname, 'slate-linkedin-cover-dark.png') });
  await p.evaluate(() => document.body.classList.add('cream'));
  await p.waitForTimeout(200);
  await p.screenshot({ path: path.join(__dirname, 'slate-linkedin-cover-cream.png') });
  await b.close();
})();
