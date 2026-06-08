import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.goto('http://127.0.0.1:5136/', { waitUntil: 'domcontentloaded', timeout: 30000 });
await page.waitForTimeout(3000);

// Start experience
const startBtn = page.locator('#footer-hero-button');
if (await startBtn.isVisible()) {
  await startBtn.click();
  await page.waitForTimeout(1500);
}

const samples = [];
for (let i = 0; i <= 10; i++) {
  await page.evaluate((ratio) => {
    const container = document.getElementById('pages-container');
    if (!container) return;
    const max = container.getBoundingClientRect().height - window.innerHeight;
    window.scrollTo(0, max * ratio);
  }, i / 10);
  await page.waitForTimeout(400);
  const bar = await page.evaluate(() => {
    const bar = document.getElementById('scroll-indicator-bar');
    const style = bar ? getComputedStyle(bar) : null;
    const transform = style?.transform || 'none';
    const end = document.getElementById('end');
    const endVisible = end ? end.getBoundingClientRect().top < window.innerHeight : false;
    return { transform, endVisible };
  });
  samples.push({ ratio: i / 10, ...bar });
}

// Scroll to absolute bottom via wheel simulation on body
await page.evaluate(() => {
  const el = document.getElementById('pages-container');
  const h = el?.scrollHeight ?? document.body.scrollHeight;
  window.scrollTo(0, h);
});
await page.waitForTimeout(800);

const bottom = await page.evaluate(() => {
  const bar = document.getElementById('scroll-indicator-bar');
  const style = bar ? getComputedStyle(bar) : null;
  const hasSeasonsTitle = !!document.getElementById('story-airdrops-post-seasons-title');
  const seasonsText = document.getElementById('story-airdrops-post-seasons-title')?.textContent?.trim();
  return {
    scrollY: window.scrollY,
    maxScroll: (document.getElementById('pages-container')?.scrollHeight ?? 0) - window.innerHeight,
    barTransform: style?.transform,
    barHeight: style?.height,
    hasSeasonsTitle,
    seasonsText,
    endHero: !!document.getElementById('end-hero'),
  };
});

console.log(JSON.stringify({ samples, bottom }, null, 2));
await browser.close();
