const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const src = process.argv[2], out = process.argv[3];
  let h = fs.readFileSync(src, 'utf8');
  const css = fs.readFileSync(process.argv[4], 'utf8');
  h = h.replace('<link rel="stylesheet" href="../_estilo/documento.css">', () => `<style>${css}</style>`)
       .replace('<script src="MERMAID"></script>', () => `<script>${fs.readFileSync(path.join(__dirname,"node_modules/mermaid/dist/mermaid.min.js"),"utf8")}</script>`);
  const b = await chromium.launch(); const p = await b.newPage();
  p.on('console', m => { if (m.type()==='error') console.log('ERR', m.text()); });
  await p.setContent(h, { waitUntil: 'load' });
  await p.waitForSelector('body[data-pronto="1"]', { timeout: 30000 });
  await p.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#666"><span class="pageNumber"></span>/<span class="totalPages"></span></div>' });
  await b.close();
})();
