
const fs = require('node:fs/promises');

const ua = process.env.SEC_UA;
if (!ua) {
  console.error('Set SEC_UA, e.g. export SEC_UA="Your Name you@email (VisionApp/1.0)"');
  process.exit(1);
}

const url = 'https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json';

(async () => {
  const res = await fetch(url, {
    headers: { 'User-Agent': ua, 'Accept-Encoding': 'gzip, deflate' }
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }

  // Already PARSED JS value:
  const data = await res.json();  // <-- no JSON.parse here, DA!


  await fs.writeFile('output.json', JSON.stringify(data, null, 2), 'utf8');

  console.log('Wrote output.json');
})().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});

console.log(data.facts.);