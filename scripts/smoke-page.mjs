import { chromium } from 'playwright';

const url = 'http://127.0.0.1:5136/';
const errors = [];
const failed = [];

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

page.on('pageerror', (err) => errors.push(`PAGE: ${err.message}`));
page.on('console', (msg) => {
  if (msg.type() === 'error') errors.push(`CONSOLE: ${msg.text()}`);
});
page.on('requestfailed', (req) => {
  failed.push(`${req.url()} :: ${req.failure()?.errorText ?? 'unknown'}`);
});

await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
await page.waitForTimeout(5000);

const state = await page.evaluate(() => {
  const preloader = document.getElementById('preloader');
  const canvas = document.getElementById('canvas');
  const nameEl = document.querySelector('#preloader .jl-name');
  const style = preloader ? getComputedStyle(preloader) : null;
  return {
    preloaderDisplay: style?.display ?? null,
    preloaderOpacity: style?.opacity ?? null,
    preloaderZ: style?.zIndex ?? null,
    nameText: nameEl?.textContent ?? null,
    canvasSize: canvas ? `${canvas.width}x${canvas.height}` : null,
    bodyClasses: document.body.className,
  };
});

console.log(JSON.stringify({ state, failed, errors }, null, 2));
await browser.close();
