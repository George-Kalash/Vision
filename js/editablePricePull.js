// editablePricePull.js
const ENDPOINT = 'https://script.google.com/macros/s/AKfycby5U2mFe2KqSJX4aPWIHKrnYXWd7iT8b4E5dtDnpcWqk5ntevjvGwiHOZYLKetbBSpDkA/exec';

async function main() {
  const symbol = (process.argv[2] || '').toUpperCase().trim();
  if (!symbol) {
    console.error('Usage: node editablePricePull.js SYMBOL');
    process.exit(1);
  }
  const r = await fetch(`${ENDPOINT}?action=set&symbol=${encodeURIComponent(symbol)}`);
  const j = await r.json();
  if (!j.ok) {
    console.error('Server error:', j);
    process.exit(1);
  }
  // Pretty-print all fields
  console.log(JSON.stringify(j, null, 2));
}
main().catch(e => { console.error(e); process.exit(1); });
