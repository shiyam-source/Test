// node render.js -> carousel/slide-XX.png + airslate-carousel.pdf (LinkedIn), x-infographic.png (X)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
(async () => {
  const dir = __dirname, logo = fs.readFileSync(path.join(dir, 'logo.svg.txt'), 'utf8');
  const build = f => { const o = path.join(dir, '.b-' + f); fs.writeFileSync(o, fs.readFileSync(path.join(dir, f), 'utf8').split('<!--LOGO-->').join(logo)); return o; };
  const b = await chromium.launch();
  // carousel
  const cdir = path.join(dir, 'carousel'); fs.rmSync(cdir, { recursive: true, force: true }); fs.mkdirSync(cdir);
  const c = build('carousel.html');
  let p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  await p.goto('file://' + c); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const slides = await p.$$('section.slide'); const files = [];
  for (let i = 0; i < slides.length; i++) { const f = path.join(cdir, `slide-${String(i + 1).padStart(2, '0')}.png`); await slides[i].screenshot({ path: f }); files.push(f); }
  await p.close(); fs.unlinkSync(c);
  execFileSync('convert', [...files, '-resize', '1080x1350', '-quality', '92', path.join(dir, 'airslate-carousel.pdf')]);
  // X infographic
  const x = build('x-infographic.html');
  p = await b.newPage({ viewport: { width: 1080, height: 1400 } });
  await p.goto('file://' + x); await p.evaluate(() => document.fonts.ready);
  const h = await p.$eval('#cap', e => e.getBoundingClientRect().height); await p.close();
  const s = Math.min(2, 4090 / h);
  p = await b.newPage({ viewport: { width: 1080, height: 1400 }, deviceScaleFactor: s });
  await p.goto('file://' + x); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  await (await p.$('#cap')).screenshot({ path: path.join(dir, 'x-infographic.png') });
  await b.close(); fs.unlinkSync(x);
  console.log('slides', files.length, 'x height', Math.round(h), 'scale', s.toFixed(2));
})();
