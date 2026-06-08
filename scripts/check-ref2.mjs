const res = await fetch('https://julio-modern.vercel.app/');
const ref = await res.text();
const i = ref.indexOf('section-stepper');
console.log(ref.slice(i, i + 800));
