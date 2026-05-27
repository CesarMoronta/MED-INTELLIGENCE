/* =============================================================================
   main.js — MED-INTELLIGENCE PRO v2.0 — Lógica Frontend Completa
   ============================================================================= */

// Estado global
const STATE = {
  user:            null,
  patients:        [],
  history:         [],
  tests:           [],
  visitPatient:    null,      // Paciente seleccionado para visita
  currentVisitId:  null,      // ID de visita activa para diagnóstico
  phase1Probs:     {},        // Probabilidades fase 1
  diagConstantes:  {},
  diagSintomas:    {},
  diagAntecedentes:{},
  allUsers:        [],
  editingPatientId: null,
};

// Lista de síntomas y antecedentes
const ALL_SYMPTOMS = [
  "Tos Persistente","Dificultad Respiratoria (Disnea)","Tos con Sangre (Hemoptisis)",
  "Dolor en el Pecho","Palpitaciones","Edema (Hinchazón)",
  "Dolor de Cabeza Severo","Confusión / Convulsiones","Pérdida de Fuerza/Sensibilidad Unilateral",
  "Dificultad para Hablar/Entender","Mareos / Vértigo",
  "Fatiga / Cansancio Extremo","Dolor de Cuerpo Generalizado",
  "Pérdida del Olfato o Gusto","Erupciones Cutáneas (Rash)",
  "Náuseas / Vómitos","Diarrea","Dolor Abdominal Agudo",
  "Dolor de Garganta","Dolor de Oído / Cara",
];

const ALL_ANTECEDENTES = [
  "Asma","EPOC","Cardiopatía","Hipertensión Arterial (HTA)","Diabetes",
  "Diabetes Mellitus","Inmunosupresión","Tabaquismo","Meningitis","Cáncer",
  "HIV / SIDA","Obesidad","Fibrilación Auricular","ACV / Derrame Previo",
  "Insuficiencia Renal Crónica",
];

function resetDiagnose() {
  // Clear select and info
  const sel = document.getElementById('diag-visit-select');
  if (sel) sel.value = '';
  const infoEl = document.getElementById('diag-patient-info');
  if (infoEl) infoEl.style.display = 'none';
  STATE.currentVisitId = null;

  // Clear inputs
  const nameInput = document.getElementById('diag-patient-name');
  if (nameInput) nameInput.value = '';
  const motivoInput = document.getElementById('diag-motivo');
  if (motivoInput) motivoInput.value = '';

  // Reset vital sliders to defaults
  const vitals = {
    'v-edad': 30, 'v-temperatura': 37.0, 'v-spo2': 98,
    'v-pas': 120, 'v-pad': 80, 'v-fc': 80, 'v-fr': 16
  };
  Object.keys(vitals).forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.value = vitals[id]; updateVitalBadge(el); }
  });

  // Uncheck all symptoms and antecedents
  document.querySelectorAll('#symptoms-checkboxes input, #antecedentes-checkboxes input').forEach(cb => {
    if (cb.checked) {
      cb.checked = false;
      toggleSymptom(cb);
    }
  });

  // Hide phase 1 and final results, show phase 1 inputs
  const phase1Result = document.getElementById('phase1-result');
  if (phase1Result) phase1Result.style.display = 'none';
  const finalResultPanel = document.getElementById('final-result-panel');
  if (finalResultPanel) finalResultPanel.style.display = 'none';
  const phase1Inputs = document.getElementById('phase-1-inputs');
  if (phase1Inputs) phase1Inputs.style.display = '';

  // Clear tests inputs
  const testsForm = document.getElementById('tests-form');
  if (testsForm) testsForm.innerHTML = '';
}

// API helper
async function api(method, path, body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res  = await fetch(path, opts);
  const data = await res.json().catch(() => ({ success: false, error: 'Error de respuesta del servidor' }));
  return data;
}

// Toast
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

// Modal helpers
function openModal(id) { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }
function closeModalOnBg(e, id) { if (e.target.id === id) closeModal(id); }

// Tab switching
function switchTab(tab) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const panel = document.getElementById(`tab-${tab}`);
  if (panel) panel.classList.add('active');

  const btn = document.querySelector(`[data-tab="${tab}"]`);
  if (btn) btn.classList.add('active');

  // Cargar datos de la pestaña
  const loaders = {
    'patients':      loadPatients,
    'history':       loadHistory,
    'admin-patients': loadAdminPatients,
    'admin-history': loadAdminHistory,
    'admin-doctors': loadDoctorsTab,
    'admin-users':   loadUsersTab,
    'admin-audit':   loadAuditLogs,
    'admin-bayes':   loadBayesParams,
    'new-visit':     loadVisitPatients,
    'diagnose':      loadDiagnoseTab,
    'dashboard':     loadDashboard,
    'admin-dashboard': loadAdminDashboard,
    'simulator':     initSimulator,
  };
  if (loaders[tab]) loaders[tab]();
}

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
  const status = await api('GET', '/api/auth/status');
  if (!status.authenticated) { window.location.href = '/login'; return; }

  STATE.user = status.user;
  setupUI();
  buildSymptomToggles();

  if (STATE.user.role === 'doctor') {
    loadDashboard();
  } else {
    switchTab('admin-dashboard');
  }
});

function setupUI() {
  const u = STATE.user;
  const first = (u.full_name || u.username || '?')[0].toUpperCase();
  document.getElementById('profile-avatar').textContent = first;
  document.getElementById('profile-name').textContent   = u.full_name || u.username;
  const roleEl = document.getElementById('profile-role');
  roleEl.textContent  = u.role === 'admin' ? '⚙️ Administrador' : '🩺 Doctor';
  roleEl.className    = `profile-role ${u.role}`;

  // Mostrar navegación según rol
  if (u.role === 'admin') {
    document.getElementById('nav-admin').style.display = 'block';
    document.querySelectorAll('.admin-only-btn').forEach(b => b.style.display = '');
  } else {
    document.getElementById('nav-doctor').style.display = 'block';
    document.querySelectorAll('.admin-only-btn').forEach(b => b.style.display = 'none');
  }
}

async function handleLogout() {
  await api('POST', '/api/auth/logout');
  window.location.href = '/login';
}

// DASHBOARD
async function loadDashboard() {
  const data = await api('GET', '/api/dashboard/stats');
  if (!data.success) return;
  const s = data.stats;
  document.getElementById('stat-patients-val').textContent    = s.total_patients     ?? '—';
  document.getElementById('stat-visits-val').textContent      = s.total_visits        ?? '—';
  document.getElementById('stat-diagnoses-val').textContent   = s.total_diagnoses     ?? '—';
  document.getElementById('stat-emergencias-val').textContent = s.total_emergencias   ?? '—';
  document.getElementById('most-common-diag').textContent     = s.most_common         || '—';
}

async function loadAdminDashboard() {
  const data = await api('GET', '/api/dashboard/stats');
  if (!data.success) return;
  const s = data.stats;
  document.getElementById('adm-stat-patients').textContent  = s.total_patients  ?? '—';
  document.getElementById('adm-stat-doctors').textContent   = s.active_doctors  ?? '—';
  document.getElementById('adm-stat-diagnoses').textContent = s.total_diagnoses ?? '—';
  document.getElementById('adm-stat-red').textContent       = s.red_alerts      ?? '—';
  document.getElementById('adm-most-common').textContent    = s.most_common     || '—';
}

// PACIENTES
async function loadPatients(search = '') {
  const url  = '/api/patients' + (search ? `?search=${encodeURIComponent(search)}` : '');
  const data = await api('GET', url);
  if (!data.success) return;
  STATE.patients = data.patients;
  renderPatientsTable('patients-list', data.patients, false);
}

async function loadAdminPatients() {
  const search = document.getElementById('admin-patient-search')?.value || '';
  const url  = '/api/patients' + (search ? `?search=${encodeURIComponent(search)}` : '');
  const data = await api('GET', url);
  if (!data.success) return;
  renderPatientsTable('admin-patients-list', data.patients, true);
}

function renderPatientsTable(containerId, patients, canEdit) {
  const el = document.getElementById(containerId);
  if (!patients.length) {
    el.innerHTML = `<div class="empty-state"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg><span>No se encontraron pacientes.</span></div>`;
    return;
  }
  const rows = patients.map(p => {
    const age = p.age ?? calcAge(p.dob);
    const ants = Object.entries(p.antecedentes || {})
      .filter(([,v]) => v).map(([k]) => k).slice(0,3).join(', ') || '—';
    const editBtn = canEdit
      ? `<button class="btn-icon" title="Editar" onclick="editPatient(${p.id})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></button>`
      : '';
    const deleteBtn = (canEdit && STATE.user && STATE.user.role === 'admin')
      ? `<button class="btn-icon" title="Eliminar" onclick="deletePatient(${p.id}, '${p.name.replace(/'/g, "\\'")}')" style="color: var(--danger)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg></button>`
      : '';
    return `<tr>
      <td><strong style="color:var(--text-primary)">${p.name}</strong></td>
      <td><code style="font-family:var(--mono);font-size:12px;">${p.cedula}</code></td>
      <td>${p.gender}</td>
      <td>${age} años</td>
      <td><small style="color:var(--text-muted)">${ants}</small></td>
      <td>
        <div style="display:flex;gap:6px;">
          <button class="btn-icon" title="Ver" onclick="viewPatient(${p.id})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg></button>
          ${editBtn}
          ${deleteBtn}
        </div>
      </td>
    </tr>`;
  }).join('');
  el.innerHTML = `<table class="data-table"><thead><tr><th>Nombre</th><th>Cédula</th><th>Género</th><th>Edad</th><th>Antecedentes</th><th>Acciones</th></tr></thead><tbody>${rows}</tbody></table>`;
}

async function deletePatient(id, name) {
  if (!confirm(`¿Estás seguro de que deseas eliminar permanentemente al paciente "${name}"? Esta acción no se puede deshacer.`)) return;
  try {
    const res = await fetch(`/api/patients/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
      toast('success', 'Paciente eliminado correctamente');
      if (typeof loadPatients === 'function') loadPatients('');
      if (typeof loadAdminPatients === 'function') loadAdminPatients();
    } else {
      toast('error', data.error || 'Error al eliminar');
    }
  } catch (err) {
    toast('error', 'Error de conexión');
  }
}

function searchPatients() {
  const q = document.getElementById('patient-search').value;
  clearTimeout(searchPatients._timer);
  searchPatients._timer = setTimeout(() => loadPatients(q), 350);
}
function adminSearchPatients() {
  clearTimeout(adminSearchPatients._timer);
  adminSearchPatients._timer = setTimeout(loadAdminPatients, 350);
}

async function viewPatient(id) {
  const data = await api('GET', `/api/patients/${id}`);
  if (!data.success) { toast('error', 'No se pudo cargar el paciente.'); return; }
  const p = data.patient;
  const age = p.age ?? calcAge(p.dob);
  const ants = Object.entries(p.antecedentes || {})
    .filter(([,v]) => v).map(([k]) => `<span class="badge badge-amarillo">${k}</span>`).join(' ')
    || '<span style="color:var(--text-muted)">Ninguno registrado</span>';

  document.getElementById('view-patient-title').textContent = p.name;
  document.getElementById('view-patient-body').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;">
      <div><div class="form-label">Cédula</div><div style="font-family:var(--mono)">${p.cedula}</div></div>
      <div><div class="form-label">Edad</div><div>${age} años (${p.dob})</div></div>
      <div><div class="form-label">Género</div><div>${p.gender}</div></div>
      <div><div class="form-label">Tipo de Sangre</div><div>${p.blood_type || '—'}</div></div>
      <div><div class="form-label">Teléfono</div><div>${p.phone || '—'}</div></div>
      <div><div class="form-label">Registrado</div><div style="font-size:12px;color:var(--text-muted)">${fmtDate(p.created_at)}</div></div>
    </div>
    <div><div class="form-label" style="margin-bottom:10px;">Antecedentes Patológicos</div><div style="display:flex;flex-wrap:wrap;gap:6px;">${ants}</div></div>
  `;
  const editBtn = document.getElementById('btn-edit-patient-modal');
  if (editBtn) {
    editBtn.setAttribute('data-patient-id', id);
    editBtn.style.display = STATE.user.role === 'admin' ? '' : 'none';
  }
  STATE.editingPatientId = id;
  openModal('modal-view-patient');
}

async function editPatientFromModal() {
  closeModal('modal-view-patient');
  editPatient(STATE.editingPatientId);
}

async function editPatient(id) {
  const data = await api('GET', `/api/patients/${id}`);
  if (!data.success) { toast('error', 'No se pudo cargar el paciente.'); return; }
  const p = data.patient;
  document.getElementById('modal-patient-title').textContent = '✏️ Editar Paciente';
  document.getElementById('pt-cedula').value = p.cedula || '';
  document.getElementById('pt-name').value   = p.name   || '';
  document.getElementById('pt-dob').value    = (p.dob || '').substring(0,10);
  document.getElementById('pt-gender').value = p.gender || 'Otro';
  document.getElementById('pt-phone').value  = p.phone  || '';
  document.getElementById('pt-blood').value  = p.blood_type || '';
  buildAntecedentesGrid('modal-antecedentes-grid', p.antecedentes || {});
  STATE.editingPatientId = id;
  openModal('modal-new-patient');
}

function buildAntecedentesGrid(containerId, values = {}) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = ALL_ANTECEDENTES.map(ant => {
    const checked = values[ant] ? 'checked' : '';
    return `<label class="symptom-toggle ${values[ant] ? 'checked' : ''}">
      <div class="toggle-dot"></div>
      <input type="checkbox" name="ant_${ant.replace(/\s/g,'_')}" ${checked} onchange="toggleSymptom(this)"/>
      ${ant}
    </label>`;
  }).join('');
}

async function savePatient() {
  const cedula  = document.getElementById('pt-cedula').value.trim();
  const name    = document.getElementById('pt-name').value.trim();
  const dob     = document.getElementById('pt-dob').value;
  const gender  = document.getElementById('pt-gender').value;
  const phone   = document.getElementById('pt-phone').value.trim();
  const blood   = document.getElementById('pt-blood').value;

  if (!cedula || !name) { toast('warning', 'Cédula y nombre son obligatorios.'); return; }

  const ants = {};
  document.querySelectorAll('#modal-antecedentes-grid .symptom-toggle').forEach(lbl => {
    const cb = lbl.querySelector('input[type=checkbox]');
    const n  = lbl.textContent.trim();
    ants[n]  = cb.checked;
  });

  const payload = { cedula, name, dob, gender, phone: phone || null,
                    blood_type: blood || null, antecedentes: ants };

  let res;
  if (STATE.editingPatientId) {
    res = await api('PUT', `/api/patients/${STATE.editingPatientId}`, payload);
  } else {
    res = await api('POST', '/api/patients', payload);
  }

  if (res.success) {
    toast('success', STATE.editingPatientId ? 'Paciente actualizado correctamente.' : 'Paciente registrado correctamente.');
    closeModal('modal-new-patient');
    STATE.editingPatientId = null;
    loadPatients();
    if (STATE.user.role === 'admin') loadAdminPatients();
    document.getElementById('modal-patient-title').textContent = 'Registrar Nuevo Paciente';
    clearPatientForm();
  } else {
    toast('error', res.error || 'Error al guardar el paciente.');
  }
}

function clearPatientForm() {
  ['pt-cedula','pt-name','pt-dob','pt-gender','pt-phone','pt-blood']
    .forEach(id => { const el = document.getElementById(id); if (el) el.value = el.tagName === 'SELECT' ? el.options[0].value : ''; });
  buildAntecedentesGrid('modal-antecedentes-grid', {});
  STATE.editingPatientId = null;
}

// NUEVA VISITA — WIZARD
let visitWizardStep = 1;
function loadVisitPatients() {
  resetVisitWizard();
  searchPatientsForVisit();
}

async function searchPatientsForVisit() {
  const q    = document.getElementById('visit-patient-search')?.value || '';
  const url  = '/api/patients' + (q ? `?search=${encodeURIComponent(q)}` : '');
  const data = await api('GET', url);
  if (!data.success) return;

  const list = document.getElementById('visit-patient-list');
  if (!data.patients.length) {
    list.innerHTML = `<div class="empty-state"><span>No se encontraron pacientes.</span></div>`;
    return;
  }
  list.innerHTML = data.patients.slice(0,20).map(p => `
    <div class="patient-picker-item" id="ppick-${p.id}" onclick="selectVisitPatient(${p.id},'${escHtml(p.name)}','${p.cedula}',${p.age ?? 30})">
      <div>
        <div class="picker-name">${p.name}</div>
        <div class="picker-cedula">${p.cedula} · ${p.gender} · ${p.age ?? calcAge(p.dob)} años</div>
      </div>
      <span class="picker-btn">Seleccionar →</span>
    </div>
  `).join('');
}

function selectVisitPatient(id, name, cedula, age) {
  STATE.visitPatient = { id, name, cedula, age };
  document.querySelectorAll('.patient-picker-item').forEach(el => el.classList.remove('selected'));
  document.getElementById(`ppick-${id}`)?.classList.add('selected');

  const card = document.getElementById('visit-selected-patient');
  card.style.display = 'block';
  card.innerHTML = `
    <div class="sp-name">✓ ${name}</div>
    <div class="sp-details">Cédula: ${cedula} · Edad: ${age} años</div>
  `;
  document.getElementById('btn-visit-step2').disabled = false;
}

function goToVisitStep(step) {
  document.getElementById('visit-step-1').style.display = step === 1 ? '' : 'none';
  document.getElementById('visit-step-2').style.display = step === 2 ? '' : 'none';
  document.getElementById('visit-step-3').style.display = step === 3 ? '' : 'none';
  visitWizardStep = step;

  document.querySelectorAll('.wizard-step').forEach((s, i) => {
    s.classList.remove('active', 'done');
    if (i + 1 < step)      s.classList.add('done');
    else if (i + 1 === step) s.classList.add('active');
  });
}

function onVisitTypeChange() {
  const type = document.querySelector('input[name="visit_type"]:checked')?.value;
  document.getElementById('visit-motivo-emergencia-group').style.display =
    type === 'emergencia' ? '' : 'none';
}

async function createVisit() {
  if (!STATE.visitPatient) { toast('warning', 'Selecciona un paciente primero.'); return; }

  const visitType        = document.querySelector('input[name="visit_type"]:checked')?.value || 'consulta';
  const motivoConsulta   = document.getElementById('visit-motivo-consulta')?.value.trim() || null;
  const motivoEmergencia = document.getElementById('visit-motivo-emergencia')?.value.trim() || null;

  if (visitType === 'emergencia' && !motivoEmergencia) {
    toast('warning', 'El motivo de emergencia es obligatorio.'); return;
  }

  const res = await api('POST', '/api/visits', {
    patient_id: STATE.visitPatient.id,
    visit_type: visitType,
    motivo_consulta: motivoConsulta,
    motivo_emergencia: motivoEmergencia,
  });

  if (res.success) {
    STATE.currentVisitId = res.visit_id;
    document.getElementById('visit-created-msg').textContent =
      `Visita #${res.visit_id} creada para ${STATE.visitPatient.name} — ${visitType.toUpperCase()}`;
    goToVisitStep(3);
    toast('success', '¡Visita creada correctamente!');
  } else {
    toast('error', res.error || 'Error al crear la visita.');
  }
}

function goToDiagnose() {
  switchTab('diagnose');
  setTimeout(() => {
    if (STATE.currentVisitId) {
      const sel = document.getElementById('diag-visit-select');
      if (sel) {
        sel.value = STATE.currentVisitId;
        onDiagVisitChange(); // Carga todos los datos (nombre, edad, antecedentes)
      }
    } else if (STATE.visitPatient) {
      document.getElementById('diag-patient-name').value = STATE.visitPatient.name;
    }
  }, 400); // Dar tiempo a que carguen las visitas abiertas
}

function resetVisitWizard() {
  STATE.visitPatient   = null;
  STATE.currentVisitId = null;
  document.getElementById('visit-patient-search').value = '';
  document.getElementById('visit-patient-list').innerHTML = '';
  document.getElementById('visit-selected-patient').style.display = 'none';
  document.getElementById('btn-visit-step2').disabled = true;
  document.getElementById('visit-motivo-consulta').value  = '';
  document.getElementById('visit-motivo-emergencia').value = '';
  goToVisitStep(1);
  searchPatientsForVisit();
}

// CONSULTA CLÍNICA / DIAGNÓSTICO
function buildSymptomToggles() {
  buildGrid('symptoms-checkboxes',   ALL_SYMPTOMS,      {});
  buildGrid('antecedentes-checkboxes', ALL_ANTECEDENTES, {});
  buildGrid('sim-symptoms-grid',     ALL_SYMPTOMS,      {});
  buildAntecedentesGrid('modal-antecedentes-grid', {});
}

function buildGrid(containerId, items, values) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = items.map(sym => `
    <label class="symptom-toggle ${values[sym] ? 'checked' : ''}">
      <div class="toggle-dot"></div>
      <input type="checkbox" ${values[sym] ? 'checked' : ''} onchange="toggleSymptom(this)"/>
      ${sym}
    </label>
  `).join('');
}

function toggleSymptom(el) {
  const label = el.closest('.symptom-toggle');
  if (el.checked) {
    label.classList.add('checked');
  } else {
    label.classList.remove('checked');
  }
}

function getCheckedFrom(containerId) {
  const result = {};
  document.querySelectorAll(`#${containerId} .symptom-toggle`).forEach(lbl => {
    const name = lbl.textContent.trim();
    result[name] = lbl.classList.contains('checked');
  });
  return result;
}

function loadDiagnoseTab() {
  updateVitalBadge(null);
}

async function openPatientSelectModal() {
  if (!STATE.allPatients || STATE.allPatients.length === 0) {
    const data = await api('GET', '/api/patients');
    if (data.success) STATE.allPatients = data.patients;
  }
  document.getElementById('search-select-patient').value = '';
  filterSelectPatients();
  openModal('modal-select-patient');
}

function filterSelectPatients() {
  const q = document.getElementById('search-select-patient').value.toLowerCase();
  const listEl = document.getElementById('select-patient-list');
  const pts = (STATE.allPatients || []).filter(p => p.name.toLowerCase().includes(q) || p.cedula.includes(q));
  
  if (!pts.length) {
    listEl.innerHTML = '<div style="padding:16px;color:var(--text-muted);text-align:center;">No se encontraron pacientes.</div>';
    return;
  }
  
  listEl.innerHTML = pts.map(p => `
    <div class="patient-select-item" style="padding: 12px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
      <div>
        <div style="font-weight: 600; color: var(--text-primary);">${p.name}</div>
        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Cédula: ${p.cedula} | Edad: ${p.age ?? calcAge(p.dob)} años</div>
      </div>
      <button class="btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="selectConsultPatient(${p.id})">Seleccionar</button>
    </div>
  `).join('');
}

function selectConsultPatient(id) {
  const p = STATE.allPatients.find(x => x.id === id);
  if (!p) return;
  STATE.currentPatient = p;
  STATE.currentVisitId = null; // Visita aún no creada
  closeModal('modal-select-patient');
  
  const infoEl = document.getElementById('diag-patient-info');
  infoEl.style.display = 'block';
  infoEl.innerHTML = `<strong>Paciente seleccionado:</strong> ${p.name} (${p.cedula})`;
  
  const nameInput = document.getElementById('diag-patient-name');
  const nameGroup = document.getElementById('diag-name-group');
  if (nameInput) { nameInput.value = p.name; nameGroup.style.display = 'block'; }
  document.getElementById('diag-patient-id').value = p.id;
  
  const edadInput = document.getElementById('v-edad');
  if (edadInput) {
    edadInput.value = p.age ?? calcAge(p.dob);
    updateVitalBadge(edadInput);
  }
  
  if (p.antecedentes) {
    document.querySelectorAll('#antecedentes-checkboxes input[type="checkbox"]').forEach(cb => {
      if (cb.checked) { cb.checked = false; toggleSymptom(cb); }
    });
    Object.entries(p.antecedentes).forEach(([ant, has]) => {
      if (has) {
        const labels = document.querySelectorAll('#antecedentes-checkboxes .symptom-toggle');
        for (let lbl of labels) {
          if (lbl.textContent.trim() === ant) {
            const cb = lbl.querySelector('input');
            if (cb && !cb.checked) { cb.checked = true; toggleSymptom(cb); }
            break;
          }
        }
      }
    });
  }
}


function updateVitalBadge(input) {
  const rules = {
    'v-temperatura': v => v >= 37.8 ? ['alert','FIEBRE'] : v >= 37.3 ? ['warn','FEBRÍCULA'] : ['ok','NORMAL'],
    'v-spo2':        v => v < 92 ? ['alert','HIPOXIA SEVERA'] : v < 95 ? ['warn','HIPOXIA LEVE'] : ['ok','NORMAL'],
    'v-pas':         v => v >= 140 ? ['alert','HTA'] : v < 90 ? ['alert','HIPOTENSIÓN'] : ['ok','NORMAL'],
    'v-pad':         v => v >= 90 ? ['alert','HTA'] : ['ok','NORMAL'],
    'v-fc':          v => v > 100 ? ['warn','TAQUICARDIA'] : v < 60 ? ['warn','BRADICARDIA'] : ['ok','NORMAL'],
    'v-fr':          v => v > 20 ? ['warn','TAQUIPNEA'] : ['ok','NORMAL'],
    'v-edad':        () => ['ok',''],
  };
  const ids = input ? [input.id] : Object.keys(rules);
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const rule = rules[id];
    if (!rule) return;
    const val = parseFloat(el.value) || 0;
    
    // Update visual label
    const valDisplay = document.getElementById(`val-${id.replace('v-','')}`);
    if (valDisplay) valDisplay.textContent = el.step === "0.1" ? val.toFixed(1) : Math.round(val);

    const [cls, label] = rule(val);
    const badgeEl = document.getElementById(`badge-${id.replace('v-','')}`);
    if (badgeEl) { badgeEl.className = `vital-badge ${cls}`; badgeEl.textContent = label; }
  });
}

function getConstantes() {
  return {
    edad:        parseFloat(document.getElementById('v-edad')?.value)        || 30,
    temperatura: parseFloat(document.getElementById('v-temperatura')?.value) || 37.0,
    spo2:        parseInt(document.getElementById('v-spo2')?.value)          || 98,
    pas:         parseInt(document.getElementById('v-pas')?.value)           || 120,
    pad:         parseInt(document.getElementById('v-pad')?.value)           || 80,
    fc:          parseInt(document.getElementById('v-fc')?.value)            || 80,
    fr:          parseInt(document.getElementById('v-fr')?.value)            || 16,
  };
}

async function runPhase1() {
  const patientId = document.getElementById('diag-patient-id')?.value;
  if (!patientId || !STATE.currentPatient) {
    toast('error', 'Debes buscar y seleccionar un paciente primero.');
    return;
  }
  
  const motivoConsulta = document.getElementById('diag-motivo')?.value.trim();
  if (!motivoConsulta) {
    toast('error', 'El motivo de consulta es obligatorio.');
    return;
  }
  
  STATE.diagSintomas = getCheckedFrom('symptoms-checkboxes');
  const hasSymptom = Object.values(STATE.diagSintomas).some(v => v);
  if (!hasSymptom) {
    toast('error', 'Debes seleccionar al menos un síntoma.');
    return;
  }

  const btn    = document.getElementById('btn-diag-phase1');
  const orig   = btn.innerHTML;
  btn.disabled = true; btn.innerHTML = '<div class="spinner-ring" style="width:20px;height:20px;border-width:2px;"></div> Calculando...';

  STATE.diagConstantes   = getConstantes();
  STATE.diagAntecedentes = getCheckedFrom('antecedentes-checkboxes');

  const res = await api('POST', '/api/diagnose/preliminar', {
    constantes:   STATE.diagConstantes,
    sintomas:     STATE.diagSintomas,
    antecedentes: STATE.diagAntecedentes,
  });

  btn.disabled = false; btn.innerHTML = orig;

  if (!res.success) { toast('error', res.error || 'Error en el diagnóstico.'); return; }

  STATE.phase1Probs = res.probabilities;
  STATE.tests       = res.tests_sugeridos || [];

  // Mostrar resultado y ocultar inputs
  document.getElementById('phase-1-inputs').style.display = 'none';
  renderPhase1Result(res);
  document.getElementById('phase1-result').style.display = '';
  document.getElementById('phase1-result').scrollIntoView({ behavior: 'smooth' });
}

function renderPhase1Result(res) {
  const diag = res.diagnosis_preliminar;
  const prob = res.probabilities;
  const top  = prob[diag];

  const alertColors = {
    'Verde': '#10b981', 'Amarillo': '#f59e0b', 'Rojo': '#ef4444'
  };

  document.getElementById('phase1-confidence').textContent = `${(top * 100).toFixed(2)}%`;

  const dd = document.getElementById('phase1-diagnosis-display');
  dd.innerHTML = `
    <div class="diagnosis-name" style="color:var(--brand-light)">${diag}</div>
    <div class="diagnosis-specialist" style="margin-top:6px;">Confianza bayesiana: <strong style="font-family:var(--mono)">${(top*100).toFixed(2)}%</strong> · ${res.pasos_calculo} iteraciones calculadas</div>
  `;

  // Top 10 diagnósticos
  const sorted = Object.entries(prob).sort(([,a],[,b]) => b - a).slice(0, 10);
  const max    = sorted[0][1];
  const chart  = document.getElementById('phase1-probs-chart');
  chart.innerHTML = sorted.map(([d, p]) => {
    const pct  = ((p / max) * 100).toFixed(1);
    const col  = p > 0.3 ? '#ef4444' : p > 0.1 ? '#f59e0b' : '#3b82f6';
    return `<div class="prob-row">
      <div class="prob-name" title="${d}">${d}</div>
      <div class="prob-track"><div class="prob-fill" style="width:${pct}%;background:${col};"></div></div>
      <div class="prob-pct">${(p*100).toFixed(2)}%</div>
    </div>`;
  }).join('');

  // Tests sugeridos
  const testsForm = document.getElementById('tests-form');
  if (!res.tests_sugeridos?.length) {
    testsForm.innerHTML = `<div style="color:var(--text-muted);font-size:13px;">No se requieren análisis adicionales mandatorios.</div>`;
    return;
  }
  testsForm.innerHTML = res.tests_sugeridos.map((t, i) => `
    <div class="test-item" id="test-item-${i}">
      <div class="test-name">🔬 ${t}</div>
      <div class="test-done-toggle">
        <input type="checkbox" id="test-done-${i}" onchange="onTestDoneToggle(${i})"/>
        <label for="test-done-${i}">¿Realizado?</label>
      </div>
      <div id="test-result-wrap-${i}" style="display:none;">
        <select class="form-input test-result-select" id="test-result-${i}">
          <option value="">— Resultado —</option>
        </select>
      </div>
    </div>
  `).join('');

  // Populsar opciones del motor
  populateTestResultOptions(res.tests_sugeridos);
}

async function populateTestResultOptions(tests) {
  const data = await api('GET', '/api/medical_tests');
  const testsDB = data.success ? data.tests : [];

  tests.forEach((testName, i) => {
    const wrap = document.getElementById(`test-result-wrap-${i}`);
    if (!wrap) return;

    const match = testsDB.find(t => {
      const dbName = t.test_name.toLowerCase();
      const query = testName.toLowerCase();
      return query === dbName || query.includes(dbName.split(' ')[0]);
    });

    if (match && match.possible_results && match.possible_results.length > 0) {
      wrap.innerHTML = `<select class="form-input test-result-select" id="test-result-${i}">
        <option value="">— Seleccionar Resultado —</option>
        ${match.possible_results.map(r => `<option value="${r}">${r}</option>`).join('')}
      </select>`;
    } else {
      wrap.innerHTML = `<input type="text" class="form-input test-result-select" id="test-result-${i}" placeholder="Escriba el resultado del estudio..." />`;
    }
  });
}

function onTestDoneToggle(i) {
  const done = document.getElementById(`test-done-${i}`).checked;
  document.getElementById(`test-result-wrap-${i}`).style.display = done ? '' : 'none';
}

async function runPhase2() {
  const patientId      = STATE.currentPatient?.id;
  const patientName    = document.getElementById('diag-patient-name').value.trim() || 'Paciente Anónimo';
  const motivoConsulta = document.getElementById('diag-motivo').value.trim() || 'Sin especificar';

  if (!STATE.currentVisitId && patientId) {
    // Crear visita silenciosamente para poder guardar el diagnóstico
    const visitRes = await api('POST', '/api/visits', {
      patient_id: patientId,
      visit_type: 'consulta',
      motivo_consulta: motivoConsulta,
      constantes: STATE.diagConstantes,
      sintomas: STATE.diagSintomas
    });
    if (!visitRes.success) {
      toast('error', visitRes.error || 'Error al crear visita para la consulta.');
      return;
    }
    STATE.currentVisitId = visitRes.visit_id;
  }

  const testsResultados = STATE.tests.map((t, i) => {
    const done   = document.getElementById(`test-done-${i}`)?.checked || false;
    const result = document.getElementById(`test-result-${i}`)?.value || null;
    return { test_name: t, done, result: done ? result : null };
  });

  const btn = document.getElementById('btn-diag-phase2');
  const orig = btn.innerHTML;
  btn.disabled = true; btn.innerHTML = '<div class="spinner-ring" style="width:20px;height:20px;border-width:2px;"></div> Finalizando...';

  const res = await api('POST', '/api/diagnose/final', {
    patient_id:      patientId,
    patient_name:    patientName,
    motivo_consulta: motivoConsulta,
    visit_id:        STATE.currentVisitId,
    preliminar_probs: STATE.phase1Probs,
    tests_resultados: testsResultados,
    sintomas:        STATE.diagSintomas,
    antecedentes:    STATE.diagAntecedentes,
    constantes:      STATE.diagConstantes,
  });
  
  btn.disabled = false; btn.innerHTML = orig;

  if (!res.success) { toast('error', res.error || 'Error en diagnóstico final.'); return; }

  renderFinalResult(res);
  toast('success', '✅ Diagnóstico final calculado y guardado.');
}

function renderFinalResult(res) {
  const alertClass = { Verde: 'verde', Amarillo: 'amarillo', Rojo: 'rojo' }[res.alert_level] || 'verde';
  const report     = markdownToHtml(res.explanation || '');

  const html = `
    <div class="section-card">
      <div class="section-header">
        <h2>🏆 Diagnóstico Final — ${res.diagnosis}</h2>
        <div style="display:flex;gap:8px;align-items:center;">
          <span class="badge badge-${alertClass}">${res.alert_level}</span>
          <span class="confidence-pill">${(res.probability * 100).toFixed(2)}%</span>
        </div>
      </div>
      <div class="diagnosis-display">
        <div class="diagnosis-name" style="color:${res.color || 'var(--brand-light)'}">${res.diagnosis}</div>
        <div class="diagnosis-specialist">Especialista sugerido: <strong>${res.specialist || '—'}</strong></div>
      </div>
      <div class="probs-bar-list" style="margin-top:16px;" id="final-probs-chart"></div>
    </div>
    <div class="section-card" style="margin-top:20px;">
      <div class="section-header">
        <h2>📋 Informe Clínico Detallado</h2>
        <button class="btn-outline" onclick="openFullReport()">Ver en pantalla completa</button>
      </div>
      <div class="clinical-report" id="clinical-report-preview">${report}</div>
    </div>
  `;

  const panel = document.getElementById('final-result-panel');
  panel.style.display = '';
  panel.innerHTML     = html;
  panel.scrollIntoView({ behavior: 'smooth' });

  // Gráfica final
  const sorted = Object.entries(res.probabilities || {}).sort(([,a],[,b]) => b - a).slice(0, 8);
  const max    = sorted[0]?.[1] || 1;
  document.getElementById('final-probs-chart').innerHTML = sorted.map(([d, p]) => {
    const pct = ((p / max) * 100).toFixed(1);
    const col = p > 0.3 ? '#ef4444' : p > 0.1 ? '#f59e0b' : '#3b82f6';
    return `<div class="prob-row">
      <div class="prob-name" title="${d}">${d}</div>
      <div class="prob-track"><div class="prob-fill" style="width:${pct}%;background:${col};"></div></div>
      <div class="prob-pct">${(p*100).toFixed(2)}%</div>
    </div>`;
  }).join('');

  // Guardar reporte para modal
  STATE.lastReport = res.explanation || '';
}

function openFullReport() {
  document.getElementById('diagnosis-result-content').innerHTML =
    `<div class="clinical-report">${markdownToHtml(STATE.lastReport)}</div>`;
  openModal('modal-diagnosis-result');
}

function printReport() {
  const win = window.open('', '_blank');
  win.document.write(`<html><head><title>Informe Clínico</title>
    <style>body{font-family:Arial,sans-serif;padding:40px;line-height:1.6;}
    table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ccc;padding:8px;}
    </style></head><body>${document.getElementById('diagnosis-result-content').innerHTML}</body></html>`);
  win.document.close();
  win.print();
}

// HISTORIAL
async function loadHistory() {
  const data = await api('GET', '/api/records');
  if (!data.success) { toast('error', 'Error cargando historial.'); return; }
  STATE.history = data.records || [];
  renderHistoryTable('history-table', STATE.history);
}

async function loadAdminHistory() {
  const data = await api('GET', '/api/records');
  if (!data.success) return;
  renderHistoryTable('admin-history-table', data.records || [], true);
}

function renderHistoryTable(containerId, records, showDoctor = false) {
  const el = document.getElementById(containerId);
  if (!records.length) {
    el.innerHTML = `<div class="empty-state"><span>No hay registros en el historial.</span></div>`;
    return;
  }
  const rows = records.map(r => {
    const alertClass = { Verde: 'verde', Amarillo: 'amarillo', Rojo: 'rojo' }[r.alert_level] || 'verde';
    const visitType  = r.visit_type === 'emergencia' ? `<span class="badge badge-emergencia">EMERGENCIA</span>` : `<span class="badge badge-consulta">CONSULTA</span>`;
    const doctorCol  = showDoctor ? `<td style="font-size:12px;color:var(--text-muted)">${r.doctor_fullname || r.doctor_username || '—'}</td>` : '';
    return `<tr>
      <td style="color:var(--text-primary);font-weight:600;">${r.patient_name || '—'}</td>
      <td><strong>${r.diagnosis_primary || '—'}</strong></td>
      <td>${visitType}</td>
      <td><span class="badge badge-${alertClass}">${r.alert_level || '—'}</span></td>
      ${doctorCol}
      <td style="font-family:var(--mono);font-size:11px;color:var(--text-muted)">${fmtDate(r.diagnosis_date || r.visit_date)}</td>
      <td>
        <button class="btn-icon" title="Ver Reporte Completo" onclick="viewFullHistoryReport(${r.diagnosis_id})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        </button>
      </td>
    </tr>`;
  }).join('');
  const doctorTh = showDoctor ? '<th>Doctor</th>' : '';
  el.innerHTML = `<table class="data-table"><thead><tr><th>Paciente</th><th>Diagnóstico</th><th>Tipo</th><th>Triage</th>${doctorTh}<th>Fecha</th><th>Acción</th></tr></thead><tbody>${rows}</tbody></table>`;
}

async function viewFullHistoryReport(diagId) {
  const data = await api('GET', `/api/records/${diagId}`);
  if (!data.success) { toast('error', data.error || 'No se pudo cargar el reporte.'); return; }
  
  document.getElementById('diagnosis-result-content').innerHTML =
    `<div class="clinical-report">${markdownToHtml(data.clinical_report)}</div>`;
  openModal('modal-diagnosis-result');
}

function filterHistory() {
  const q = (document.getElementById('history-search')?.value || '').toLowerCase();
  const filtered = STATE.history.filter(r =>
    (r.patient_name || '').toLowerCase().includes(q) ||
    (r.diagnosis_primary || '').toLowerCase().includes(q)
  );
  renderHistoryTable('history-table', filtered);
}

function filterAdminHistory() {
  // Recargar con filtro (implementación básica — hacer búsqueda local)
  filterHistory();
}

// SIMULADOR BAYES
function initSimulator() {
  // ya está construido en buildSymptomToggles
}

async function runSimulation() {
  const sintomas = getCheckedFrom('sim-symptoms-grid');
  const activeSintomas = Object.keys(sintomas).filter(k => sintomas[k]);
  if (!activeSintomas.length) { toast('warning', 'Selecciona al menos un síntoma.'); return; }

  const res = await api('POST', '/api/diagnose/preliminar', {
    constantes: { edad: 40, temperatura: 37.0, spo2: 98, pas: 120, pad: 80, fc: 80, fr: 16 },
    sintomas,
    antecedentes: {},
  });
  if (!res.success) { toast('error', res.error || 'Error.'); return; }

  const sorted = Object.entries(res.probabilities).sort(([,a],[,b]) => b - a).slice(0, 12);
  const max    = sorted[0][1];
  document.getElementById('sim-chart').innerHTML = sorted.map(([d, p]) => {
    const pct = ((p / max) * 100).toFixed(1);
    const col = p > 0.3 ? '#ef4444' : p > 0.1 ? '#f59e0b' : '#3b82f6';
    return `<div class="prob-row">
      <div class="prob-name" title="${d}">${d}</div>
      <div class="prob-track"><div class="prob-fill" style="width:${pct}%;background:${col};"></div></div>
      <div class="prob-pct">${(p*100).toFixed(2)}%</div>
    </div>`;
  }).join('');
}

function resetSimulation() {
  document.querySelectorAll('#sim-symptoms-grid .symptom-toggle').forEach(el => {
    el.classList.remove('checked');
    const cb = el.querySelector('input[type=checkbox]');
    if (cb) cb.checked = false;
  });
  document.getElementById('sim-chart').innerHTML = '';
}

// USUARIOS (ADMIN)
async function loadUsersTab() {
  const data = await api('GET', '/api/users');
  if (!data.success) { toast('error', 'Error cargando usuarios.'); return; }
  STATE.allUsers = data.users;
  renderUsersTable(data.users);
}

async function loadDoctorsTab() {
  const data = await api('GET', '/api/users');
  if (!data.success) return;
  const doctors = (data.users || []).filter(u => u.role === 'doctor');
  renderDoctorsTable(doctors);
}

function renderUsersTable(users) {
  const el = document.getElementById('users-list');
  if (!users.length) { el.innerHTML = `<div class="empty-state"><span>No hay usuarios.</span></div>`; return; }
  const rows = users.map(u => {
    const roleBadge = u.role === 'admin'
      ? `<span class="badge badge-admin">Admin</span>`
      : `<span class="badge badge-doctor">Doctor</span>`;
    const activeBadge = u.is_active
      ? `<span class="badge badge-active">Activo</span>`
      : `<span class="badge badge-inactive">Inactivo</span>`;
    return `<tr>
      <td><strong style="color:var(--text-primary)">${u.username}</strong></td>
      <td>${u.full_name || '—'}</td>
      <td>${roleBadge}</td>
      <td>${activeBadge}</td>
      <td style="font-size:12px;color:var(--text-muted)">${fmtDate(u.last_login)}</td>
      <td>
        <div style="display:flex;gap:6px;">
          <button class="btn-icon" title="${u.is_active ? 'Desactivar' : 'Activar'}" onclick="toggleUserStatus(${u.id}, ${u.is_active})" style="color: ${u.is_active ? 'var(--warning)' : 'var(--success)'}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              ${u.is_active 
                ? '<path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/>' 
                : '<path d="M12 2v10"/><path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>'}
            </svg>
          </button>
          <button class="btn-icon" title="Editar" onclick="editUser(${u.id})">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
        </div>
      </td>
    </tr>`;
  }).join('');
  el.innerHTML = `<table class="data-table"><thead><tr><th>Usuario</th><th>Nombre</th><th>Rol</th><th>Estado</th><th>Último Login</th><th>Acciones</th></tr></thead><tbody>${rows}</tbody></table>`;
}

async function toggleUserStatus(id, currentStatus) {
  try {
    const res = await fetch(`/api/users/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: !currentStatus })
    });
    const data = await res.json();
    if (data.success) {
      toast('success', `Usuario ${!currentStatus ? 'activado' : 'desactivado'} correctamente`);
      if (typeof loadUsersTab === 'function') loadUsersTab();
      if (typeof loadDoctorsTab === 'function') loadDoctorsTab();
    } else {
      toast('error', data.error || 'Error al cambiar estado');
    }
  } catch (err) {
    toast('error', 'Error de conexión');
  }
}

function renderDoctorsTable(doctors) {
  const el = document.getElementById('doctors-list');
  if (!doctors.length) { el.innerHTML = `<div class="empty-state"><span>No hay doctores registrados.</span></div>`; return; }
  const rows = doctors.map(d => {
    const activeBadge = d.is_active ? `<span class="badge badge-active">Activo</span>` : `<span class="badge badge-inactive">Inactivo</span>`;
    return `<tr>
      <td><strong style="color:var(--text-primary)">${d.username}</strong></td>
      <td>${d.full_name || '—'}</td>
      <td>${d.especialidad || '—'}</td>
      <td>${d.matricula || '—'}</td>
      <td>${d.hospital || '—'}</td>
      <td>${activeBadge}</td>
      <td>
        <div style="display:flex;gap:6px;">
          <button class="btn-icon" title="${d.is_active ? 'Desactivar' : 'Activar'}" onclick="toggleUserStatus(${d.id}, ${d.is_active})" style="color: ${d.is_active ? 'var(--warning)' : 'var(--success)'}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              ${d.is_active 
                ? '<path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/>' 
                : '<path d="M12 2v10"/><path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>'}
            </svg>
          </button>
          <button class="btn-icon" onclick="editUser(${d.id})">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
        </div>
      </td>
    </tr>`;
  }).join('');
  el.innerHTML = `<table class="data-table"><thead><tr><th>Usuario</th><th>Nombre</th><th>Especialidad</th><th>Matrícula</th><th>Hospital</th><th>Estado</th><th>Acción</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function onRoleChange() {
  const role = document.getElementById('usr-role').value;
  document.getElementById('doctor-fields').style.display = role === 'doctor' ? '' : 'none';
}

async function saveUser() {
  const id          = document.getElementById('edit-user-id').value;
  const username    = document.getElementById('usr-username').value.trim();
  const password    = document.getElementById('usr-password').value.trim();
  const role        = document.getElementById('usr-role').value;
  const fullName    = document.getElementById('usr-fullname').value.trim() || null;
  const email       = document.getElementById('usr-email').value.trim() || null;
  const matricula   = document.getElementById('usr-matricula').value.trim() || null;
  const especialidad = document.getElementById('usr-especialidad').value.trim() || null;
  const telefono    = document.getElementById('usr-telefono').value.trim() || null;
  const hospital    = document.getElementById('usr-hospital').value.trim() || null;

  if (!username) { toast('warning', 'El nombre de usuario es obligatorio.'); return; }
  if (!id && !password) { toast('warning', 'La contraseña es obligatoria al crear un usuario.'); return; }
  if (password && password.length < 6) { toast('warning', 'La contraseña debe tener al menos 6 caracteres.'); return; }

  const payload = { username, role, full_name: fullName, email,
    matricula, especialidad, telefono, hospital };
  if (password) payload.password = password;

  let res;
  if (id) {
    res = await api('PUT', `/api/users/${id}`, payload);
  } else {
    res = await api('POST', '/api/users', payload);
  }

  if (res.success) {
    toast('success', id ? 'Usuario actualizado correctamente.' : 'Usuario creado correctamente.');
    closeModal('modal-new-user');
    clearUserForm();
    loadUsersTab();
    loadDoctorsTab();
  } else {
    toast('error', res.error || 'Error al guardar el usuario.');
  }
}

async function editUser(id) {
  const data = await api('GET', `/api/users/${id}`);
  if (!data.success) { toast('error', 'No se pudo cargar el usuario.'); return; }
  const u = data.user;
  document.getElementById('modal-user-title').textContent     = '✏️ Editar Usuario';
  document.getElementById('edit-user-id').value               = u.id;
  document.getElementById('usr-username').value               = u.username || '';
  document.getElementById('usr-password').value               = '';
  document.getElementById('usr-role').value                   = u.role || 'doctor';
  document.getElementById('usr-fullname').value               = u.full_name || '';
  document.getElementById('usr-email').value                  = u.email || '';
  document.getElementById('usr-matricula').value              = u.matricula || '';
  document.getElementById('usr-especialidad').value           = u.especialidad || '';
  document.getElementById('usr-telefono').value               = u.telefono || '';
  document.getElementById('usr-hospital').value               = u.hospital || '';
  onRoleChange();
  openModal('modal-new-user');
}

function clearUserForm() {
  document.getElementById('modal-user-title').textContent = 'Crear Nuevo Usuario';
  document.getElementById('edit-user-id').value = '';
  ['usr-username','usr-password','usr-fullname','usr-email',
   'usr-matricula','usr-especialidad','usr-telefono','usr-hospital']
    .forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
  const roleEl = document.getElementById('usr-role');
  if (roleEl) roleEl.value = 'doctor';
  onRoleChange();
}

// CONFIGURACIÓN BAYESIANA
async function loadBayesParams() {
  const data = await api('GET', '/api/parameters');
  if (!data.success) return;
  const priors = data.priors || {};
  const el = document.getElementById('priors-editor');
  el.innerHTML = Object.entries(priors).map(([disease, prior]) => `
    <div class="prior-item">
      <div class="prior-name">${disease}</div>
      <input type="number" class="form-input prior-input" id="prior-${btoa(disease).replace(/=/g,'')}"
             value="${(prior * 100).toFixed(2)}" step="0.01" min="0.01" max="99"/>
      <span style="font-size:12px;color:var(--text-muted);">%</span>
    </div>
  `).join('');
}

async function saveBayesParams() {
  const items = document.querySelectorAll('.prior-item');
  const priors = {};
  items.forEach(item => {
    const name  = item.querySelector('.prior-name')?.textContent.trim();
    const input = item.querySelector('input');
    if (name && input) priors[name] = parseFloat(input.value) / 100 || 0.01;
  });

  const res = await api('POST', '/api/parameters', { priors });
  if (res.success) { toast('success', 'Parámetros bayesianos guardados.'); }
  else             { toast('error', res.error || 'Error al guardar parámetros.'); }
}

async function resetBayesParams() {
  if (!confirm('¿Restaurar los parámetros bayesianos a los valores clínicos originales?')) return;
  const res = await api('POST', '/api/parameters', { reset: true });
  if (res.success) { toast('success', 'Parámetros restablecidos a valores originales.'); loadBayesParams(); }
  else             { toast('error', res.error || 'Error al restablecer.'); }
}

// AUDIT LOGS
async function loadAuditLogs() {
  const data = await api('GET', '/api/audit_logs');
  if (!data.success) return;
  const logs = data.logs || [];
  const el   = document.getElementById('audit-table');
  if (!logs.length) { el.innerHTML = `<div class="empty-state"><span>No hay logs de auditoría.</span></div>`; return; }
  const actionColors = {
    LOGIN: '#10b981', LOGOUT: '#6b7280', CREATE: '#3b82f6',
    UPDATE: '#f59e0b', DELETE: '#ef4444', RESET: '#8b5cf6'
  };
  const rows = logs.map(l => `<tr>
    <td style="font-family:var(--mono);font-size:11px;color:var(--text-muted)">${fmtDate(l.logged_at)}</td>
    <td><strong style="color:var(--text-primary)">${l.username || '—'}</strong></td>
    <td><span style="color:${actionColors[l.action] || '#94a3b8'};font-weight:700;font-size:12px;">${l.action}</span></td>
    <td>${l.entity || '—'}</td>
    <td style="font-size:12px;color:var(--text-muted)">${(l.details || '—').substring(0,60)}</td>
    <td style="font-family:var(--mono);font-size:11px;color:var(--text-muted)">${l.ip_address || '—'}</td>
  </tr>`).join('');
  el.innerHTML = `<table class="data-table"><thead><tr><th>Fecha</th><th>Usuario</th><th>Acción</th><th>Entidad</th><th>Detalles</th><th>IP</th></tr></thead><tbody>${rows}</tbody></table>`;
}

// UTILIDADES
function calcAge(dob) {
  if (!dob) return '?';
  const b  = new Date(dob);
  const n  = new Date();
  let age  = n.getFullYear() - b.getFullYear();
  const m  = n.getMonth() - b.getMonth();
  if (m < 0 || (m === 0 && n.getDate() < b.getDate())) age--;
  return age;
}

function fmtDate(iso) {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('es-DO', { year: 'numeric', month: '2-digit', day: '2-digit' })
      + ' ' + d.toLocaleTimeString('es-DO', { hour: '2-digit', minute: '2-digit' });
  } catch { return iso; }
}

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

// Inicializar modal de paciente con antecedentes al abrir
document.getElementById('modal-new-patient')?.addEventListener('click', function(e) {
  if (this === e.target) return;
});

// Re-inicializar grid de antecedentes cuando se abre el modal
const openModalOrig = openModal;
window.openModal = function(id) {
  if (id === 'modal-new-patient' && !STATE.editingPatientId) {
    buildAntecedentesGrid('modal-antecedentes-grid', {});
    clearPatientForm();
  }
  if (id === 'modal-new-user') {
    if (!document.getElementById('edit-user-id')?.value) clearUserForm();
  }
  openModalOrig(id);
};
