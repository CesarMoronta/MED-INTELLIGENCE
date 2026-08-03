/* =============================================================================
   utils.js — Extracted from main.js
   ============================================================================= */

async function api(method, path, body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res  = await fetch(path, opts);
  const data = await res.json().catch(() => ({ success: false, error: 'Error de respuesta del servidor' }));
  return data;
}

function toast(type, msg, duration = 4000) {
  const icons = {
    success: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
    error:   `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
    warning: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
    info:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
  };
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.innerHTML = `${icons[type] || icons.info} <span>${msg}</span>`;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => {
    el.classList.add('removing');
    setTimeout(() => el.remove(), 350);
  }, duration);
}

function setButtonLoading(btn, isLoading, loadingText = 'Procesando...') {
  if (!btn) return;
  if (isLoading) {
    if (btn.disabled) return;
    btn.disabled = true;
    btn.dataset.oldHtml = btn.innerHTML;
    btn.innerHTML = `<span>${loadingText}</span> <span class="spinner-ring" style="width:14px; height:14px; border-width:1.5px; display:inline-block; vertical-align:middle; margin-left:6px; border-top-color: currentColor;"></span>`;
  } else {
    btn.disabled = false;
    if (btn.dataset.oldHtml) {
      btn.innerHTML = btn.dataset.oldHtml;
      delete btn.dataset.oldHtml;
    }
  }
}

function openModal(id) { document.getElementById(id)?.classList.add('open'); }

function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

function closeModalOnBg(e, id) { if (e.target.id === id) closeModal(id); }

function escHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}

function markdownToHtml(md) {
  if (!md) return '';
  return md
    .replace(/^### (.+)$/gm,    '<h3>$1</h3>')
    .replace(/^#### (.+)$/gm,   '<h4>$1</h4>')
    .replace(/^##### (.+)$/gm,  '<h5>$1</h5>')
    .replace(/\*\*(.+?)\*\*/g,  '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,      '<em>$1</em>')
    .replace(/`(.+?)`/g,        '<code>$1</code>')
    .replace(/^---$/gm,         '<hr/>')
    .replace(/^\*   (.+)$/gm,   '<li>$1</li>')
    .replace(/^1\.  (.+)$/gm,   '<li>$1</li>')
    .replace(/(<li>[\s\S]*?<\/li>)+/g, s => `<ul>${s}</ul>`)
    .replace(/\|(.+)\|/g, row => {
      const cells = row.split('|').filter(c => c.trim());
      return `<tr>${cells.map(c => `<td>${c.trim()}</td>`).join('')}</tr>`;
    })
    .replace(/<tr>(.+)<\/tr>/g, t => {
      if (t.includes('---')) return '';
      return t;
    })
    .replace(/(?:<tr>[\s\S]*?<\/tr>\s*)+/g, s => `<table>${s.replace(/\n/g, '')}</table>`)
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/\n/g,     '<br/>');
}
