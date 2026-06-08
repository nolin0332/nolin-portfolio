import { chromium } from 'playwright';

const URL = process.env.URL || 'http://127.0.0.1:5136/';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

const failed = [];
const pending = new Map();

page.on('request', (req) => {
  const u = req.url();
  if (u.includes('/assets/') || u.includes('/_astro/')) {
    pending.set(req.url(), { method: req.method(), start: Date.now() });
  }
});

page.on('response', async (res) => {
  const u = res.url();
  if (!u.includes('/assets/') && !u.includes('/_astro/')) return;
  pending.delete(u);
  const ct = res.headers()['content-type'] || '';
  const status = res.status();
  if (status >= 400 || ct.includes('text/html')) {
    let size = 0;
    try {
      const b = await res.body();
      size = b.length;
    } catch {
      /* ignore */
    }
    failed.push({ status, ct, size, url: u.replace(URL, '') });
  }
});

page.on('requestfailed', (req) => {
  const u = req.url();
  if (u.includes('/assets/') || u.includes('/_astro/')) {
    failed.push({ status: 'FAILED', url: u.replace(URL, ''), error: req.failure()?.errorText });
  }
});

await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(45000);

const pct = await page.evaluate(() => {
  const foot = document.getElementById('footer-loading-indicator');
  return foot ? foot.textContent.trim() : null;
});

console.log('footer at 45s:', pct);
console.log('failed/poisoned count:', failed.length);
failed.slice(0, 40).forEach((f) => console.log(JSON.stringify(f)));
console.log('still pending:', pending.size);
[...pending.values()].slice(0, 10).forEach((p) => console.log('pending', p));

await browser.close();
