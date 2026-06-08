const res = await fetch('https://julio-modern.vercel.app/');
const ref = await res.text();
console.log('section-stepper', ref.includes('section-stepper'));
console.log('boot-fix', ref.includes('boot-fix'));
console.log('intro-hero-title', ref.includes('intro-hero-title'));
const m = ref.match(/#intro-hero[^}]{0,200}/g);
console.log('intro-hero css snippets', m?.slice(0, 5));
