// Responsive audit: each page x viewport x {prod, staging}.
// Checks horizontal overflow, offending elements, small tap targets, tiny text, broken images,
// page height, and an above-the-fold pixel diff between prod and staging.
const S = '/tmp/claude-0/-home-user-Test/fb647a80-1772-5a33-98bf-885a44633475/scratchpad';
const { chromium } = require('playwright');
const fs = require('fs');
const { PNG } = require(S + '/lh/node_modules/pngjs');
const pixelmatch = require(S + '/lh/node_modules/pixelmatch');
const OUT = S + '/resp'; fs.mkdirSync(OUT, { recursive: true });
const pages = process.argv.slice(2);
const VPS = [
  { name: 'm360', width: 360, height: 800, mobile: true },
  { name: 'm390', width: 390, height: 844, mobile: true },
  { name: 't768', width: 768, height: 1024, mobile: true },
  { name: 'd1024', width: 1024, height: 768, mobile: false },
  { name: 'd1440', width: 1440, height: 900, mobile: false },
];
const HOSTS = { prd: 'https://www.tripledart.com', stg: 'https://staging.tripledart.com' };

async function audit(page) {
  return page.evaluate(() => {
    const vw = document.documentElement.clientWidth;
    const sw = document.documentElement.scrollWidth;
    const offenders = [];
    const small = [];
    let tiny = 0;
    const seen = new Set();
    for (const el of document.querySelectorAll('body *')) {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      // overflow: element extends past the right edge and is not inside a clipping/scrolling ancestor
      if (r.right > vw + 2 && offenders.length < 400) {
        let clipped = false;
        for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
          const pc = getComputedStyle(p);
          if (/(hidden|clip|auto|scroll)/.test(pc.overflowX)) { clipped = true; break; }
        }
        if (!clipped) offenders.push({ sel: el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : ''), right: Math.round(r.right) });
      }
      if ((el.tagName === 'A' || el.tagName === 'BUTTON') && (r.width < 24 || r.height < 24) && el.innerText.trim()) {
        const k = el.tagName + el.innerText.trim().slice(0, 30);
        if (!seen.has(k)) { seen.add(k); small.push(el.innerText.trim().slice(0, 30)); }
      }
      if (el.childNodes.length && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 2) && parseFloat(cs.fontSize) < 12) tiny++;
    }
    const imgs = [...document.images];
    const broken = imgs.filter(i => i.complete && i.naturalWidth === 0 && i.getAttribute('src') && !i.src.startsWith('data:')).map(i => i.currentSrc || i.src).slice(0, 10);
    // dedupe offenders by top-most ancestor selector
    const offSel = [...new Set(offenders.map(o => o.sel))].slice(0, 8);
    return {
      vw, sw, hOverflow: sw > vw + 1, offenders: offSel, offenderCount: offenders.length,
      smallTargets: small.length, smallSample: small.slice(0, 6), tinyText: tiny,
      broken, imgCount: imgs.length, height: document.documentElement.scrollHeight,
      viewportMeta: (document.querySelector('meta[name=viewport]') || {}).content || null,
    };
  });
}

(async () => {
  const browser = await chromium.launch();
  const results = [];
  for (const path of pages) {
    const slug = path.replace(/^\//, '').replace(/\//g, '_') || 'home';
    for (const vp of VPS) {
      const shots = {};
      for (const [site, host] of Object.entries(HOSTS)) {
        const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, isMobile: vp.mobile, hasTouch: vp.mobile, deviceScaleFactor: 1,
          userAgent: vp.mobile ? 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36' : undefined });
        // Block ad/analytics/consent/visitor-ID tags on both sites so the layout isolates the platform.
        await ctx.route(/googletagmanager|google-analytics|doubleclick|google\.com\/(rmkt|ccm)|cookiebot|hs-scripts|hs-analytics|licdn|clarity\.ms|facebook|lfeeder|happierleads|popt\.in|albacross|apollo|snitcher|visitortracking|warmly|svrdntfctn|vector\.co|\/gjbe\//, r => r.abort());
        const page = await ctx.newPage();
        const errors = [];
        page.on('pageerror', e => errors.push(e.message.slice(0, 160)));
        try {
          await page.goto(host + path, { waitUntil: 'load', timeout: 60000 });
          await page.waitForTimeout(1500);
          // scroll through to trigger lazy images and scroll animations
          const h = await page.evaluate(() => document.documentElement.scrollHeight);
          for (let y = 0; y < h; y += vp.height * 0.8) { await page.evaluate(y => window.scrollTo(0, y), y); await page.waitForTimeout(120); }
          await page.waitForTimeout(800);
          const a = await audit(page);
          await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(1500);
          const fold = `${OUT}/${slug}__${vp.name}__${site}.png`;
          await page.screenshot({ path: fold });
          shots[site] = fold;
          if (vp.name === 'm390' || vp.name === 'd1440') await page.screenshot({ path: `${OUT}/${slug}__${vp.name}__${site}__full.png`, fullPage: true }).catch(() => {});
          results.push({ path, vp: vp.name, site, ...a, jsErrors: errors.slice(0, 5) });
        } catch (e) {
          results.push({ path, vp: vp.name, site, error: e.message.slice(0, 200) });
        }
        await ctx.close();
      }
      if (shots.prd && shots.stg) {
        const A = PNG.sync.read(fs.readFileSync(shots.prd)), B = PNG.sync.read(fs.readFileSync(shots.stg));
        if (A.width === B.width && A.height === B.height) {
          const diff = new PNG({ width: A.width, height: A.height });
          const n = pixelmatch(A.data, B.data, diff.data, A.width, A.height, { threshold: 0.15 });
          fs.writeFileSync(`${OUT}/${slug}__${vp.name}__diff.png`, PNG.sync.write(diff));
          results.push({ path, vp: vp.name, site: 'diff', foldDiffPct: +(100 * n / (A.width * A.height)).toFixed(2) });
        }
      }
      console.log(new Date().toISOString().slice(11, 19), path, vp.name);
    }
  }
  fs.writeFileSync(S + '/responsive.json', JSON.stringify(results, null, 1));
  await browser.close();
})();
