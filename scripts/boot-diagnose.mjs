import { chromium } from 'playwright';

const URL = process.env.URL || 'http://127.0.0.1:5136/';
const TIMEOUT_MS = 180000;

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

const logs = [];
page.on('console', (msg) => logs.push(`[${msg.type()}] ${msg.text()}`));
page.on('pageerror', (err) => logs.push(`[pageerror] ${err.message}`));

try {
  await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
} catch (e) {
  console.log('GOTO_FAIL', e.message);
  await browser.close();
  process.exit(1);
}

const snap = async (label) => {
  const s = await page.evaluate((lbl) => {
    const pre = document.getElementById('preloader');
    const foot = document.getElementById('footer-loading-indicator');
    const hero = document.getElementById('footer-hero-button');
    const ui = document.getElementById('ui');
    return {
      label: lbl,
      preloaderDisplay: pre ? getComputedStyle(pre).display : null,
      preloaderHidden: pre ? pre.style.display : null,
      jlp: pre ? pre.style.getPropertyValue('--jlp') : null,
      footerPct: foot ? foot.textContent.trim() : null,
      heroVisible: hero ? getComputedStyle(hero).visibility : null,
      heroPointer: hero ? getComputedStyle(hero).pointerEvents : null,
      heroOpacity: hero ? getComputedStyle(hero).opacity : null,
      heroText: hero ? hero.textContent.trim().slice(0, 80) : null,
      uiHidden: ui ? ui.classList.contains('is-hidden') : null,
      bodyClasses: document.body.className,
      notSupported: [...document.documentElement.classList].filter((c) =>
        c.startsWith('not-supported'),
      ),
    };
  }, label);
  console.log(JSON.stringify(s));
};

await snap('t0');
for (let i = 1; i <= 24; i++) {
  await page.waitForTimeout(5000);
  await snap(`t${i * 5}s`);
  const done = await page.evaluate(() => {
    const pre = document.getElementById('preloader');
    const hidden = pre && (pre.style.display === 'none' || getComputedStyle(pre).display === 'none');
    const hero = document.getElementById('footer-hero-button');
    const heroReady =
      hero &&
      getComputedStyle(hero).pointerEvents === 'auto' &&
      parseFloat(getComputedStyle(hero).opacity) > 0.5;
    return { hidden, heroReady };
  });
  if (done.hidden && done.heroReady) {
    console.log('SUCCESS_AT', i * 5, 's');
    break;
  }
  if (i === 36) console.log('TIMEOUT_NO_ADVANCE');
}

console.log('--- console (last 30) ---');
logs.slice(-30).forEach((l) => console.log(l));

await browser.close();
