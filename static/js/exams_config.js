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
const examState = {
  exams: [],
};

// SECTION: Icons
// CHANGED: person icon for student count pill
const personIcon = `
  <svg width="11" height="11" viewBox="0 0 11 11" fill="none" style="flex-shrink:0" aria-hidden="true">
    <circle cx="5.5" cy="4" r="2.5" stroke="currentColor" stroke-width="1"></circle>
    <path d="M1.5 10c0-2.2 1.8-4 4-4s4 1.8 4 4" stroke="currentColor" stroke-width="1" stroke-linecap="round"></path>
  </svg>
`;

// SECTION: Message Helpers
function setExamMessage(type, text) {
  const msgEl = document.getElementById('exam-msg');
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

// SECTION: Exam Form
async function createExam() {
  const name = document.getElementById('exam-name')?.value.trim();
  const date = document.getElementById('exam-date')?.value;
  const session = document.getElementById('exam-session')?.value;
  const subjectsRaw = document.getElementById('subject-codes')?.value || '';

  const subjectCodes = subjectsRaw
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);

  if (!name || !date || !session || subjectCodes.length === 0) {
    setExamMessage('error', 'Please fill all fields');
    return;
  }

  try {
    await api('/api/exams/create/', {
      method: 'POST',
      body: JSON.stringify({ name, date, session, subject_codes: subjectCodes }),
    });
    document.getElementById('exam-name').value = '';
    document.getElementById('exam-date').value = '';
    document.getElementById('exam-session').value = 'AM';
    document.getElementById('subject-codes').value = '';
    // CHANGED: success badge
    showSuccess(document.getElementById('exam-card'), 'Exam saved');
    await loadExams();
  } catch (err) {
    setExamMessage('error', 'Failed to save exam');
  }
}

// SECTION: Exam List
function sortExams(exams, mode) {
  const sorted = [...exams];
  sorted.sort((a, b) => {
    const dateA = a.date ? new Date(a.date) : new Date(0);
    const dateB = b.date ? new Date(b.date) : new Date(0);
    const nameA = (a.name || '').toLowerCase();
    const nameB = (b.name || '').toLowerCase();
    if (mode === 'oldest') return dateA - dateB;
    if (mode === 'az') return nameA.localeCompare(nameB);
    return dateB - dateA;
  });
  return sorted;
}

function filterExams(exams, term) {
  if (!term) return exams;
  const q = term.toLowerCase();
  return exams.filter(e => (e.name || '').toLowerCase().includes(q));
}

// CHANGED: DOM-based count helper
function updateExamCount() {
  const visible = document.querySelectorAll('#exam-list .exam-item:not([style*=\"display:none\"])').length;
  const total = document.querySelectorAll('#exam-list .exam-item').length;
  const countEl = document.getElementById('exam-count');
  if (countEl) {
    countEl.textContent = visible === total ? `${total} exams` : `${visible} of ${total} exams`;
  }
}

function renderExamList() {
  const listEl = document.getElementById('exam-list');
  const term = document.getElementById('exam-search')?.value || '';
  const sortMode = document.getElementById('exam-sort')?.value || 'newest';

  if (!listEl) return;

  listEl.innerHTML = '';
  let exams = filterExams(examState.exams, term);
  exams = sortExams(exams, sortMode);

  exams.forEach(exam => {
    const item = document.createElement('div');
    item.className = 'exam-item';
    item.dataset.id = exam.id;
    item.dataset.name = exam.name || '';
    item.dataset.date = exam.date || '';
    item.innerHTML = `
      <div class="ei-top">
        <div class="ei-name exam-name">${exam.name}</div>
        <button class="cfg-btn cfg-btn-danger-ghost ei-delete" data-id="${exam.id}">Delete</button>
      </div>
      <div class="ei-meta">${exam.date || '-'} · Session ${exam.session || '-'}</div>
      <div class="ei-bottom">
        <span class="ei-tag">${personIcon}${exam.student_count ?? 0} students</span>
        <span class="ei-del-note">Removes exam only</span>
      </div>
    `;
    listEl.appendChild(item);
  });
  updateExamCount();
}

async function loadExams() {
  try {
    const data = await api('/api/exams/list/', { method: 'GET' });
    examState.exams = Array.isArray(data) ? data : [];
    renderExamList();
  } catch (err) {
    examState.exams = [];
    renderExamList();
  }
}

async function deleteExam(id) {
  if (!window.confirm('Delete this exam? This cannot be undone.')) return;
  try {
    await api(`/api/exams/delete/${id}/`, { method: 'POST' });
    examState.exams = examState.exams.filter(e => String(e.id) !== String(id));
    renderExamList();
    updateExamCount();
  } catch (err) {
    // CHANGED: show error on the specific exam item (not in form)
    const item = document.querySelector(`.exam-item[data-id="${id}"]`);
    if (item) {
      item.querySelector('.inline-error-badge')?.remove();
      const badge = document.createElement('div');
      badge.className = 'inline-error-badge';
      let text = 'Cannot delete exam before its session ends';
      try {
        const parsed = JSON.parse(err.message);
        if (parsed?.error) text = parsed.error;
      } catch (e) {
        if (err?.message && err.message.length < 120) {
          text = err.message;
        }
      }
      badge.textContent = text;
      item.appendChild(badge);
    }
  }
}

// SECTION: Event Wiring
document.addEventListener('DOMContentLoaded', () => {
  loadExams();

  document.getElementById('btn-save-exam')?.addEventListener('click', createExam);

  // CHANGED: exam search filter
  document.getElementById('exam-search')?.addEventListener('input', function() {
    const q = this.value.toLowerCase();
    document.querySelectorAll('#exam-list .exam-item').forEach(item => {
      const name = item.querySelector('.exam-name')?.textContent?.toLowerCase() ?? '';
      item.style.display = name.includes(q) ? '' : 'none';
    });
    updateExamCount();
  });

  // CHANGED: exam sort
  document.getElementById('exam-sort')?.addEventListener('change', function() {
    const list = document.getElementById('exam-list');
    if (!list) return;
    const items = [...list.querySelectorAll('.exam-item')];
    items.sort((a, b) => {
      const na = a.dataset.name ?? '';
      const nb = b.dataset.name ?? '';
      const da = a.dataset.date ?? '';
      const db = b.dataset.date ?? '';
      if (this.value === 'az') return na.localeCompare(nb);
      if (this.value === 'oldest') return da.localeCompare(db);
      return db.localeCompare(da);
    });
    items.forEach(i => list.appendChild(i));
  });

  document.getElementById('exam-list')?.addEventListener('click', e => {
    const btn = e.target.closest('.ei-delete');
    if (!btn) return;
    deleteExam(btn.dataset.id);
  });
});
