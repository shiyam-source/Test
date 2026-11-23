// node render-gif.js -> linkedin-anatomy.gif, linkedin-anatomy.mp4, linkedin-anatomy-still.png
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
(async () => {
  const dir = __dirname, fr = path.join(dir, '.frames');
  fs.rmSync(fr, { recursive: true, force: true }); fs.mkdirSync(fr);
  const logo = fs.readFileSync(path.join(dir, 'logo.svg.txt'), 'utf8');
  const built = path.join(dir, '.gif-built.html');
  fs.writeFileSync(built, fs.readFileSync(path.join(dir, 'linkedin-gif.html'), 'utf8').replace('<!--LOGO-->', logo));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await p.goto('file://' + built); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const el = await p.$('#cap');
  const N = await p.evaluate(() => MAP.length);
  const tl = [[0, -1, 0.7]];
  for (let i = 1; i <= N; i++) tl.push([i, i - 1, 0.32]);
  tl.push([N, -1, 4.5]);
  let list = '';
  for (let k = 0; k < tl.length; k++) {
    const [n, a, sec] = tl[k];
    await p.evaluate(([n, a]) => setStep(n, a), [n, a]);
    const f = path.join(fr, `f${String(k).padStart(3, '0')}.png`);
    await el.screenshot({ path: f });
    list += `file '${f}'\nduration ${sec}\n`;
  }
  list += `file '${path.join(fr, `f${String(tl.length - 1).padStart(3, '0')}.png`)}'\n`;
  fs.writeFileSync(path.join(fr, 'list.txt'), list);
  await p.evaluate(n => setStep(n, -1), N);
  await el.screenshot({ path: path.join(dir, 'linkedin-anatomy-still.png') });
  await b.close(); fs.unlinkSync(built);
  const L = path.join(fr, 'list.txt');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', L,
    '-vf', 'fps=25,split[a][b];[a]palettegen=max_colors=96:stats_mode=full[p];[b][p]paletteuse=dither=none',
    '-loop', '0', path.join(dir, 'linkedin-anatomy.gif')]);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', L,
    '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-crf', '18', '-movflags', '+faststart',
    path.join(dir, 'linkedin-anatomy.mp4')]);
  fs.rmSync(fr, { recursive: true, force: true });
  console.log('done');
})();
