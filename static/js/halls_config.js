// SECTION: CSRF Helpers
function getCsrf() {
  return document.cookie
    .split(';')
    .find(c => c.trim().startsWith('csrftoken='))
    ?.split('=')[1] ?? '';
}

async function api(url, opts = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf(), ...opts.headers },
    ...opts,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// SECTION: State
const hallState = {
  halls: [],
};

// SECTION: Message Helpers
function setHallMessage(type, text) {
  const msgEl = document.getElementById('hall-msg');
  if (!msgEl) return;
  msgEl.className = '';
  msgEl.textContent = '';
  if (!text) return;
  if (type === 'success') {
    msgEl.classList.add('cfg-msg-success');
    msgEl.textContent = text;
    setTimeout(() => msgEl.classList.add('fade'), 1500);
    setTimeout(() => {
      msgEl.className = '';
      msgEl.textContent = '';
    }, 2500);
  } else {
    msgEl.classList.add('cfg-msg-error');
    msgEl.textContent = text;
  }
}

// SECTION: Save Success Badge
// CHANGED: inline success badge after save
function showSuccess(containerEl, message) {
  if (!containerEl) return;
  const existing = containerEl.querySelector('.save-success-msg');
  if (existing) existing.remove();
  const msg = document.createElement('div');
  msg.className = 'save-success-msg';
  msg.innerHTML = `<svg width="12" height="12" viewBox="0 0 12 12" fill="none">
    <path d="M2 6l3 3 5-5" stroke="#16a34a" stroke-width="1.5"
      fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>${message}`;
  containerEl.appendChild(msg);
  setTimeout(() => msg.classList.add('fade'), 1800);
  setTimeout(() => msg.remove(), 2500);
}

// SECTION: Hall Form Blocks
function createHallBlock(index) {
  const block = document.createElement('div');
  block.className = 'hall-form-block';
  block.dataset.index = index;

  // CHANGED: rows/cols/spb in one row + hall capacity badge
  block.innerHTML = `
    <div class="hfb-header">
      <span class="hfb-label">Hall ${index}</span>
      <button type="button" class="cfg-btn cfg-btn-danger-ghost hfb-remove">Remove</button>
    </div>

    <div class="cfg-field">
      <label>Hall name</label>
      <input type="text" data-field="name" placeholder="Hall A">
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">
      <div class="cfg-field">
        <label>Rows</label>
        <input type="number" data-field="rows" name="rows" min="1">
      </div>
      <div class="cfg-field">
        <label>Columns</label>
        <input type="number" data-field="cols" name="columns" min="1">
      </div>
      <div class="cfg-field">
        <label>Seats / bench</label>
        <select data-field="spb" name="seats_per_bench">
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
        </select>
      </div>
    </div>

    <div class="hall-cap-badge">
      Total capacity <span class="hall-cap-num">0</span> seats
    </div>
  `;

  if (index === 1) {
    block.querySelector('.hfb-remove').style.display = 'none';
  }

  const inputs = block.querySelectorAll('[data-field="rows"], [data-field="cols"], [data-field="spb"]');
  inputs.forEach(input => {
    input.addEventListener('input', () => window.updateCapacity(block));
    input.addEventListener('change', () => window.updateCapacity(block));
  });

  block.querySelector('.hfb-remove')?.addEventListener('click', () => {
    block.remove();
    renumberHallBlocks();
    window.updateTotalCapacity?.();
  });

  return block;
}

function renumberHallBlocks() {
  const blocks = Array.from(document.querySelectorAll('.hall-form-block'));
  blocks.forEach((block, idx) => {
    const index = idx + 1;
    block.dataset.index = index;
    const label = block.querySelector('.hfb-label');
    if (label) label.textContent = `Hall ${index}`;
    const removeBtn = block.querySelector('.hfb-remove');
    if (removeBtn) removeBtn.style.display = index === 1 ? 'none' : 'inline-flex';
  });
}

function resetHallBlocks() {
  const container = document.getElementById('hall-forms-container');
  if (!container) return;
  container.innerHTML = '';
  const block = createHallBlock(1);
  container.appendChild(block);
  window.updateCapacity(block);
  window.updateTotalCapacity?.();
}

// SECTION: Save Halls
async function saveAllHalls() {
  const blocks = Array.from(document.querySelectorAll('.hall-form-block'));
  const payloads = [];

  for (const block of blocks) {
    const name = block.querySelector('[data-field="name"]')?.value.trim();
    if (!name) continue;
    const rows = block.querySelector('[data-field="rows"]')?.value;
    const cols = block.querySelector('[data-field="cols"]')?.value;
    const spb = block.querySelector('[data-field="spb"]')?.value;

    if (!rows || !cols || !spb) {
      setHallMessage('error', 'Please complete all fields for each hall');
      return;
    }

    payloads.push({
      name,
      rows: Number(rows),
      columns: Number(cols),
      seats_per_bench: Number(spb),
    });
  }

  if (payloads.length === 0) {
    setHallMessage('error', 'Add at least one hall');
    return;
  }

  try {
    for (const payload of payloads) {
      await api('/api/halls/create/', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    }
    showSuccess(document.getElementById('hall-add-card'), 'Halls saved');
    resetHallBlocks();
    await loadHalls();
  } catch (err) {
    setHallMessage('error', 'Failed to save halls');
  }
}

// SECTION: Hall List
function sortHalls(halls, mode) {
  const sorted = [...halls];
  sorted.sort((a, b) => {
    const nameA = (a.name || '').toLowerCase();
    const nameB = (b.name || '').toLowerCase();
    const capA = a.capacity ?? 0;
    const capB = b.capacity ?? 0;
    if (mode === 'za') return nameB.localeCompare(nameA);
    if (mode === 'cap-asc') return capA - capB;
    if (mode === 'cap-desc') return capB - capA;
    return nameA.localeCompare(nameB);
  });
  return sorted;
}

function filterHalls(halls, term) {
  if (!term) return halls;
  const q = term.toLowerCase();
  return halls.filter(h => (h.name || '').toLowerCase().includes(q));
}

// CHANGED: DOM-based count helper
function updateHallCount() {
  const visible = document.querySelectorAll('#hall-list .hall-item:not([style*="display:none"])').length;
  const total = document.querySelectorAll('#hall-list .hall-item').length;
  const countEl = document.getElementById('hall-count');
  if (countEl) {
    countEl.textContent = visible === total ? `${total} halls` : `${visible} of ${total} halls`;
  }
}

function renderHallList() {
  const listEl = document.getElementById('hall-list');
  const term = document.getElementById('hall-search')?.value || '';
  const sortMode = document.getElementById('hall-sort')?.value || 'az';

  if (!listEl) return;

  listEl.innerHTML = '';
  let halls = filterHalls(hallState.halls, term);
  halls = sortHalls(halls, sortMode);

  halls.forEach(hall => {
    const item = document.createElement('div');
    item.className = 'hall-item';
    item.dataset.id = hall.id;
    item.dataset.name = hall.name || '';
    item.dataset.capacity = hall.capacity ?? 0;
    item.innerHTML = `
      <div class="hi-left">
        <div class="hi-name hall-name">${hall.name}</div>
        <div class="hi-spec">${hall.rows} rows · ${hall.columns} cols · ${hall.seats_per_bench} seats/bench</div>
        <div class="hi-cap">Capacity ${hall.capacity}</div>
      </div>
      <button class="cfg-btn cfg-btn-danger-ghost hi-delete" data-id="${hall.id}">Delete</button>
    `;
    listEl.appendChild(item);
  });
  updateHallCount();
}

async function loadHalls() {
  try {
    const data = await api('/api/halls/list/', { method: 'GET' });
    hallState.halls = Array.isArray(data) ? data : [];
    renderHallList();
  } catch (err) {
    hallState.halls = [];
    renderHallList();
  }
}

async function deleteHall(id) {
  if (!window.confirm('Delete this hall? This cannot be undone.')) return;
  try {
    await api(`/api/halls/delete/${id}/`, { method: 'POST' });
    hallState.halls = hallState.halls.filter(h => String(h.id) !== String(id));
    renderHallList();
    updateHallCount();
  } catch (err) {
    setHallMessage('error', 'Failed to delete hall');
  }
}

// SECTION: Event Wiring
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('hall-forms-container');
  if (container) {
    container.appendChild(createHallBlock(1));
  }

  window.updateCapacity(container?.querySelector('.hall-form-block'));
  window.updateTotalCapacity?.();

  document.getElementById('btn-add-hall')?.addEventListener('click', () => {
    const block = createHallBlock(document.querySelectorAll('.hall-form-block').length + 1);
    container.appendChild(block);
    renumberHallBlocks();
    window.updateCapacity(block);
  });

  document.getElementById('btn-save-halls')?.addEventListener('click', saveAllHalls);

  // CHANGED: hall search filter
  document.getElementById('hall-search')?.addEventListener('input', function () {
    const q = this.value.toLowerCase();
    document.querySelectorAll('#hall-list .hall-item').forEach(item => {
      const name = item.querySelector('.hall-name')?.textContent?.toLowerCase() ?? '';
      item.style.display = name.includes(q) ? '' : 'none';
    });
    updateHallCount();
  });

  // CHANGED: hall sort
  document.getElementById('hall-sort')?.addEventListener('change', function () {
    const list = document.getElementById('hall-list');
    if (!list) return;
    const items = [...list.querySelectorAll('.hall-item')];
    items.sort((a, b) => {
      const na = a.dataset.name ?? '';
      const nb = b.dataset.name ?? '';
      const ca = parseInt(a.dataset.capacity) || 0;
      const cb = parseInt(b.dataset.capacity) || 0;
      if (this.value === 'za') return nb.localeCompare(na);
      if (this.value === 'cap-asc') return ca - cb;
      if (this.value === 'cap-desc') return cb - ca;
      return na.localeCompare(nb);
    });
    items.forEach(i => list.appendChild(i));
  });

  document.getElementById('hall-list')?.addEventListener('click', e => {
    const btn = e.target.closest('.hi-delete');
    if (!btn) return;
    deleteHall(btn.dataset.id);
  });

  loadHalls();
});
