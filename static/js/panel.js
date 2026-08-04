/* ============================================================
   EduNova — Shared Panel JS
   ============================================================ */

// ── Toast notifications ───────────────────────────────
function toast(msg, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${msg}</span>`;
  container.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(100px)'; setTimeout(() => t.remove(), 300); }, 3000);
}

// ── Modal helpers ─────────────────────────────────────
function openModal(id) {
  const m = document.getElementById(id);
  if (m) { m.classList.add('active'); document.body.style.overflow = 'hidden'; }
}
function closeModal(id) {
  const m = document.getElementById(id);
  if (m) { m.classList.remove('active'); document.body.style.overflow = ''; }
}
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
    document.body.style.overflow = '';
  }
});

// ── API helper ────────────────────────────────────────
async function api(url, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Format helpers ────────────────────────────────────
function fmtCurrency(n) { return '₹' + (n || 0).toLocaleString('en-IN', { minimumFractionDigits: 0 }); }
function fmtDate(d) { if (!d) return '—'; return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }); }
function fmtPct(n) { return (n || 0).toFixed(1) + '%'; }

function gradeClass(g) {
  const m = { 'A+': 'grade-aplus', A: 'grade-a', 'B+': 'grade-b', B: 'grade-b', C: 'grade-c', D: 'grade-d', F: 'grade-f' };
  return m[g] || '';
}

function attBadge(status) {
  const m = {
    present:    '<span class="badge badge-green"><i class="fas fa-check"></i> Present</span>',
    absent:     '<span class="badge badge-red"><i class="fas fa-times"></i> Absent</span>',
    late:       '<span class="badge badge-yellow"><i class="fas fa-clock"></i> Late</span>',
    not_marked: '<span class="badge badge-gray">Not Marked</span>',
  };
  return m[status] || '<span class="badge badge-gray">—</span>';
}

// ── Confirm dialog ────────────────────────────────────
function confirm(msg) { return window.confirm(msg); }

// ── Debounce ──────────────────────────────────────────
function debounce(fn, ms = 300) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// ── Pagination ────────────────────────────────────────
function renderPagination(container, current, total, perPage, onPage) {
  const pages = Math.ceil(total / perPage);
  let html = '';
  if (pages <= 1) { container.innerHTML = ''; return; }
  html += `<button class="page-btn${current === 1 ? ' disabled' : ''}" onclick="(${onPage})(${current - 1})">&laquo;</button>`;
  for (let i = 1; i <= pages; i++) {
    if (i === 1 || i === pages || Math.abs(i - current) <= 2) {
      html += `<button class="page-btn${i === current ? ' active' : ''}" onclick="(${onPage})(${i})">${i}</button>`;
    } else if (Math.abs(i - current) === 3) {
      html += `<span style="padding:0 4px;color:#94a3b8">…</span>`;
    }
  }
  html += `<button class="page-btn${current === pages ? ' disabled' : ''}" onclick="(${onPage})(${current + 1})">&raquo;</button>`;
  container.innerHTML = html;
}
