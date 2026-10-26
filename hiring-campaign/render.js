// Renders every slide in src/ to a still PNG, a looping MP4 and a GIF.
// Animations are CSS; we pause them and seek frame by frame so every
// export is deterministic and loops cleanly.
//
//   node render.js            all slides
//   node render.js 01 03      only slides whose filename starts with these
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const SRC = path.join(ROOT, "src");
const OUT = path.join(ROOT, "output");
const FRAMES = path.join(require("os").tmpdir(), "td-frames");
const LOOP_MS = 5000;
const FPS = 25;
const STILL_MS = Number(process.env.STILL_MS || 3200);
const GIF_WIDTH = Number(process.env.GIF_WIDTH || 720);

const only = process.argv.slice(2);
const slides = fs.readdirSync(SRC).filter((f) => /^\d\d-.*\.html$/.test(f))
  .filter((f) => !only.length || only.some((p) => f.startsWith(p))).sort();

for (const d of ["png", "mp4", "gif"]) fs.mkdirSync(path.join(OUT, d), { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });

  for (const file of slides) {
    const name = file.replace(/\.html$/, "");
    await page.goto("file://" + path.join(SRC, file));
    await page.evaluate(() => window.slideReady);
    const seek = (ms) => page.evaluate((t) => {
      for (const a of document.getAnimations()) { a.pause(); a.currentTime = t; }
    }, ms);

    const still = Number(await page.evaluate(() => document.body.dataset.still || 0)) || STILL_MS;
    await seek(still);
    await page.screenshot({ path: path.join(OUT, "png", name + ".png") });

    if (process.env.STILL_ONLY) { console.log("still", name); continue; }
    fs.rmSync(FRAMES, { recursive: true, force: true });
    fs.mkdirSync(FRAMES, { recursive: true });
    const total = Math.round(LOOP_MS / 1000 * FPS);
    for (let i = 0; i < total; i++) {
      await seek(i * 1000 / FPS);
      await page.screenshot({ path: path.join(FRAMES, String(i).padStart(4, "0") + ".png") });
    }

    const input = ["-y", "-loglevel", "error", "-framerate", String(FPS), "-i", path.join(FRAMES, "%04d.png")];
    // MP4: 3 loops so Instagram/LinkedIn players have something to chew on
    execFileSync("ffmpeg", [...input.slice(0, 5), "-stream_loop", "2", ...input.slice(5),
      "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-movflags", "+faststart",
      path.join(OUT, "mp4", name + ".mp4")]);
    execFileSync("ffmpeg", [...input,
      "-vf", `scale=${GIF_WIDTH}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle`,
      "-loop", "0", path.join(OUT, "gif", name + ".gif")]);
    console.log("rendered", name);
  }
  await browser.close();

  if (process.env.STILL_ONLY) return;
  // LinkedIn document carousel: stills stitched into one PDF
  const pngs = fs.readdirSync(path.join(OUT, "png")).sort().map((f) => path.join(OUT, "png", f));
  execFileSync("convert", [...pngs, "-quality", "92", path.join(OUT, "tripledart-hiring-carousel.pdf")]);
  console.log("pdf ok");
})();
