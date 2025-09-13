const form = document.querySelector('#quote-form');
const inputSymbol = document.querySelector('#ticker');
const inputKey = document.querySelector('#apikey');
const remember = document.querySelector('#remember');
const out = document.querySelector('#out');

// Load saved key if user opted in previously
const savedKey = localStorage.getItem('TD_API_KEY');
if (savedKey) {
  inputKey.value = savedKey;
  remember.checked = true;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault(); // don't navigate away

  const symbol = inputSymbol.value.trim().toUpperCase();
  const key = inputKey.value.trim();

  if (!symbol || !key) {
    out.textContent = 'Please enter both ticker and API key.';
    return;
  }

  // Optional: persist key locally if the user asked us to
  if (remember.checked) {
    localStorage.setItem('TD_API_KEY', key);
  } else {
    localStorage.removeItem('TD_API_KEY');
  }

  const url = new URL('https://api.twelvedata.com/quote');
  url.searchParams.set('symbol', symbol);
  // url.searchParams.set('exchange', 'NASDAQ'); // uncomment to hint the exchange
  url.searchParams.set('apikey', key);

  out.textContent = 'Fetching…';
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    const data = await res.json();

    if (data.status === 'error') {
      throw new Error(data.message || 'Twelve Data error');
    }

    const price = Number(data.price ?? data.close);
    if (!Number.isFinite(price)) throw new Error('No price field in response');

    console.log(`${symbol} price:`, price);  // <-- logs to console as requested
    out.textContent = `${symbol} price: ${price}`;
  } catch (err) {
    console.error('Fetch failed:', err);
    out.textContent = `Error: ${err.message || err}`;
  }
});

