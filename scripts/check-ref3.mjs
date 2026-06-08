const res = await fetch('https://julio-modern.vercel.app/');
const ref = await res.text();
console.log('html div', ref.includes('id="section-stepper"'));
console.log('visibility hidden', ref.includes('section-stepper{visibility:hidden'));
const i = ref.indexOf('id="section-stepper"');
console.log('at', i, i >= 0 ? ref.slice(i, i + 400) : 'n/a');
