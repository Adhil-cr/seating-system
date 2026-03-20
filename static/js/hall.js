// SECTION: CSRF Helpers
function getCsrf() {
  return document.cookie
    .split(';')
    .find(c => c.trim().startsWith('csrftoken='))
    ?.split('=')[1] ?? '';
}

// SECTION: Capacity Calculator
// CHANGED: use name attributes + hall-cap-num badge
function updateCapacity(blockEl) {
  if (!blockEl) return;
  const rows = parseInt(blockEl.querySelector('[name="rows"]')?.value) || 0;
  const cols = parseInt(blockEl.querySelector('[name="columns"]')?.value) || 0;
  const spb = parseInt(blockEl.querySelector('[name="seats_per_bench"]')?.value) || 1;
  const cap = rows * cols * spb;
  const capEl = blockEl.querySelector('.hall-cap-num');
  if (capEl) capEl.textContent = String(cap);
}

// SECTION: Export
window.updateCapacity = updateCapacity;
