// node render-linkedin.js -> linkedin-animated.gif, linkedin-animated.mp4, linkedin-static.png
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
(async () => {
  const dir = __dirname, fr = path.join(dir, '.frames');
  fs.rmSync(fr, { recursive: true, force: true }); fs.mkdirSync(fr);
  const logo = fs.readFileSync(path.join(dir, 'logo.svg.txt'), 'utf8');
  const built = path.join(dir, '.li-built.html');
  fs.writeFileSync(built, fs.readFileSync(path.join(dir, 'linkedin-animated.html'), 'utf8').replace('<!--LOGO-->', logo));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await p.goto('file://' + built); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const el = await p.$('#cap');
  // timeline: [done, scan, pop, seconds]
  const tl = [[0, -1, -1, 1.6]];
  for (let i = 0; i < 10; i++) tl.push([i, i, -1, 0.45], [i + 1, -1, i, 0.12], [i + 1, -1, -1, 0.28]);
  tl.push([10, -1, -1, 3.5]);
  let list = '';
  for (let k = 0; k < tl.length; k++) {
    const [d, s, pp, sec] = tl[k];
    await p.evaluate(([d, s, pp]) => setState(d, s, pp), [d, s, pp]);
    const f = path.join(fr, `f${String(k).padStart(3, '0')}.png`);
    await el.screenshot({ path: f });
    list += `file '${f}'\nduration ${sec}\n`;
  }
  list += `file '${path.join(fr, `f${String(tl.length - 1).padStart(3, '0')}.png`)}'\n`;
  fs.writeFileSync(path.join(fr, 'list.txt'), list);
  // static fallback = final, all-checked state
  await p.evaluate(() => setState(10, -1, -1));
  await el.screenshot({ path: path.join(dir, 'linkedin-static.png') });
  await b.close(); fs.unlinkSync(built);
  const L = path.join(fr, 'list.txt');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', L,
    '-vf', 'fps=25,split[a][b];[a]palettegen=max_colors=96:stats_mode=full[p];[b][p]paletteuse=dither=none',
    '-loop', '0', path.join(dir, 'linkedin-animated.gif')]);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', L,
    '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-crf', '18', '-movflags', '+faststart',
    path.join(dir, 'linkedin-animated.mp4')]);
  fs.rmSync(fr, { recursive: true, force: true });
  console.log('done');
})();
