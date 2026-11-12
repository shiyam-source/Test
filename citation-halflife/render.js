// node render.js out/carousel.html out [dpr]  -> out/slides/slide-NN.png + out/carousel.pdf
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const [html, outdir, dpr] = process.argv.slice(2);
  fs.mkdirSync(path.join(outdir, 'slides'), { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: +(dpr || 2) });
  await p.goto('file://' + path.resolve(html));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const els = await p.$$('section.slide');
  for (let i = 0; i < els.length; i++) {
    await els[i].screenshot({ path: path.join(outdir, 'slides', `slide-${String(i + 1).padStart(2, '0')}.png`) });
  }
  await p.pdf({ path: path.join(outdir, 'carousel.pdf'), width: '1080px', height: '1350px', printBackground: true });
  console.log('rendered', els.length, 'slides');
  await b.close();
})();
