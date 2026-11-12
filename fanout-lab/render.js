// node render.js -> fanout-ranks.png (2x)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: +(process.argv[2] || 2) });
  await p.goto('file://' + path.resolve(__dirname, 'fanout.html'));
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  await (await p.$('section.slide')).screenshot({ path: path.join(__dirname, 'fanout-ranks.png') });
  await b.close(); console.log('rendered');
})();
