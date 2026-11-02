const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  for (const [src, out] of [["coin-flip-report", "The Coin-Flip Report - Slate Research.pdf"], ["quota-tax-report", "The Quota Tax - Slate Research.pdf"]]) {
    await p.goto('file://' + path.resolve(__dirname, '../build', src + '.rendered.html')); await p.waitForTimeout(500);
    await p.pdf({ path: path.resolve(__dirname, '../pdf', out), format: 'A4', printBackground: true, preferCSSPageSize: true,
      displayHeaderFooter: true, headerTemplate: '<div></div>',
      footerTemplate: '<div style="width:100%;font-family:Inter,sans-serif;font-size:7px;color:#8a8984;padding:0 17mm;display:flex;justify-content:space-between"><span>Slate Research · November 2026</span><span class="pageNumber"></span></div>' });
  }
  await b.close(); console.log('pdfs ok');
})();
