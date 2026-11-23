// node render-panels.js -> x-01..04.png (each capped at 4096px tall), anatomy-full.png, anatomy-carousel.pdf
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
(async () => {
  const dir = __dirname;
  const logo = fs.readFileSync(path.join(dir, 'logo.svg.txt'), 'utf8');
  const built = path.join(dir, '.panels-built.html');
  fs.writeFileSync(built, fs.readFileSync(path.join(dir, 'panels.html'), 'utf8').split('<!--LOGO-->').join(logo));
  const b = await chromium.launch();
  const out = [];
  for (const id of ['p1', 'p2', 'p3', 'p4']) {
    let p = await b.newPage({ viewport: { width: 1080, height: 1400 } });
    await p.goto('file://' + built); await p.evaluate(() => document.fonts.ready);
    const h = await p.$eval('#' + id, e => e.getBoundingClientRect().height);
    await p.close();
    const scale = Math.min(2, 4090 / h);
    p = await b.newPage({ viewport: { width: 1080, height: 1400 }, deviceScaleFactor: scale });
    await p.goto('file://' + built); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(250);
    const f = path.join(dir, `x-0${id[1]}.png`);
    await (await p.$('#' + id)).screenshot({ path: f });
    await p.close();
    out.push(f); console.log(id, Math.round(h), 'scale', scale.toFixed(2));
  }
  await b.close(); fs.unlinkSync(built);
  // full master: stack panels at a common width of 1600px
  execFileSync('convert', [...out, '-resize', '1600x', '-background', 'white', '-gravity', 'center', '-append', path.join(dir, 'anatomy-full.png')]);
  // LinkedIn document carousel (one panel per page)
  execFileSync('convert', [...out, '-resize', '1600x', '-quality', '92', path.join(dir, 'anatomy-carousel.pdf')]);
  console.log('done');
})();
