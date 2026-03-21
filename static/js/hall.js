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
  updateTotalCapacity();
}

// SECTION: Export
window.updateCapacity = updateCapacity;

// SECTION: Total Capacity
function updateTotalCapacity() {
  const blocks = document.querySelectorAll('.hall-form-block');
  let total = 0;
  blocks.forEach(block => {
    const rows = parseInt(block.querySelector('[name="rows"]')?.value) || 0;
    const cols = parseInt(block.querySelector('[name="columns"]')?.value) || 0;
    const spb = parseInt(block.querySelector('[name="seats_per_bench"]')?.value) || 1;
    total += rows * cols * spb;
  });
  const totalEl = document.getElementById('hall-total-cap-num');
  if (totalEl) totalEl.textContent = String(total);
}

window.updateTotalCapacity = updateTotalCapacity;
