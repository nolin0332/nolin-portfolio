import { chromium } from 'playwright';

const URL = process.env.URL || 'http://127.0.0.1:5136/';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

const audioReqs = [];
page.on('response', async (res) => {
  const u = res.url();
  if (!/\.(mp3|ogg)/i.test(u)) return;
  audioReqs.push({ url: u.replace(URL, ''), status: res.status() });
});

const logs = [];
page.on('console', (msg) => logs.push(`[${msg.type()}] ${msg.text()}`));
page.on('pageerror', (err) => logs.push(`[pageerror] ${err.message}`));

await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });

// Wait for Enter button
for (let i = 0; i < 40; i++) {
  await page.waitForTimeout(2000);
  const ready = await page.evaluate(() => {
    const hero = document.getElementById('footer-hero-button');
    return (
      hero &&
      getComputedStyle(hero).pointerEvents === 'auto' &&
      parseFloat(getComputedStyle(hero).opacity) > 0.5
    );
  });
  if (ready) break;
}

await page.click('#footer-hero-button', { timeout: 5000 }).catch(() => {});
await page.waitForTimeout(3000);

const state = await page.evaluate(async () => {
  const Tone = window.Tone;
  const ctx = Tone?.context ?? window.AudioContext ? new AudioContext() : null;
  let toneState = Tone?.context?.state ?? null;
  if (Tone?.context?.state === 'suspended' && Tone.context.resume) {
    try {
      await Tone.context.resume();
      toneState = Tone.context.state;
    } catch (e) {
      toneState = 'resume-failed:' + e.message;
    }
  }
  const sound = document.getElementById('sound');
  const soundBtn = document.getElementById('sound-button');
  return {
    bodyClasses: document.body.className,
    toneState,
    soundExists: !!sound,
    soundBtnExists: !!soundBtn,
    soundDisplay: sound ? getComputedStyle(sound).display : null,
    soundVisibility: sound ? getComputedStyle(sound).visibility : null,
    soundPointer: sound ? getComputedStyle(sound).pointerEvents : null,
    soundActive: sound?.classList.contains('sound-is-active'),
    uiHidden: document.getElementById('ui')?.classList.contains('is-hidden'),
  };
});

console.log('audio responses:', audioReqs.length);
const failed = audioReqs.filter((r) => r.status >= 400);
console.log('failed audio:', failed.length, failed.slice(0, 10));
const ok = audioReqs.filter((r) => r.status === 200);
console.log('ok audio sample:', ok.slice(0, 5));

console.log('state:', JSON.stringify(state, null, 2));
console.log('--- console errors ---');
logs.filter((l) => l.includes('error') || l.includes('Error')).slice(0, 20).forEach((l) => console.log(l));

await browser.close();
