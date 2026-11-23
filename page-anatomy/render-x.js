// node render-x.js -> x-infographic.png (long side capped at 4096px for X)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const logo = fs.readFileSync(path.join(__dirname, 'logo.svg.txt'), 'utf8');
  const html = fs.readFileSync(path.join(__dirname, 'x-infographic.html'), 'utf8').replace('<!--LOGO-->', logo);
  const built = path.join(__dirname, '.x-built.html'); fs.writeFileSync(built, html);
  const b = await chromium.launch();
  let p = await b.newPage({ viewport: { width: 1080, height: 1200 } });
  await p.goto('file://' + built); await p.evaluate(() => document.fonts.ready);
  const h = await p.$eval('#cap', e => e.getBoundingClientRect().height);
  const scale = Math.min(2, 4096 / h);
  await p.close();
  p = await b.newPage({ viewport: { width: 1080, height: Math.ceil(h) }, deviceScaleFactor: scale });
  await p.goto('file://' + built); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  await (await p.$('#cap')).screenshot({ path: path.join(__dirname, 'x-infographic.png') });
  await b.close(); fs.unlinkSync(built);
  console.log('height', h, 'scale', scale.toFixed(3), 'px', Math.round(1080 * scale), 'x', Math.round(h * scale));
})();
