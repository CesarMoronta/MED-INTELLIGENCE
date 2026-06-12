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
  rxList:          [],
  allAppointments: [],
  finalDiagnosisRes: null,    // Resultado final del diagnóstico
  finalTestsResultados: [],
  geminiChatHistory: [],      // Historial del chat médico Gemini
  lastReport:      '',
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
  const diagAppId = document.getElementById('diag-appointment-id');
  if (diagAppId) diagAppId.value = '';
  const diagPtId = document.getElementById('diag-patient-id');
  if (diagPtId) diagPtId.value = '';

  // Clear inputs
  const nameInput = document.getElementById('diag-patient-name');
  if (nameInput) nameInput.value = '';
  const motivoInput = document.getElementById('diag-motivo');
  if (motivoInput) motivoInput.value = '';

  // Reset vital sliders to defaults
  const vitals = {
    'v-edad': 30, 'v-temperatura': 37.0, 'v-spo2': 98,
    'v-pas': 120, 'v-pad': 80, 'v-fc': 80, 'v-fr': 16,
    'v-peso': 70, 'v-altura': 170, 'v-grasa_corporal': 20
  };
  Object.keys(vitals).forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.value = vitals[id]; updateVitalBadge(el); }
  });
  const imcBadge = document.getElementById('badge-imc');
  if (imcBadge) { imcBadge.className = 'vital-badge ok'; imcBadge.textContent = 'Normal'; }
  const imcVal = document.getElementById('val-imc');
  if (imcVal) imcVal.textContent = '24.2';
  const imcHid = document.getElementById('v-imc');
  if (imcHid) imcHid.value = '24.2';
  const diagNotes = document.getElementById('diag-doctor-notes');
  if (diagNotes) diagNotes.value = '';

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
    'appointments':  loadAppointments,
    'billing':       loadBillingTab,
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
  loadClinicName();

  // Cargar perfil completo en segundo plano para obtener avatar real si es base64
  api('GET', '/api/profile').then(res => {
    if (res.success && res.user) {
      STATE.user = res.user;
      const avatarEl = document.getElementById('profile-avatar');
      if (avatarEl && res.user.photo_url) {
        avatarEl.innerHTML = `<img src="${res.user.photo_url}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;" />`;
      }
    }
  });

  if (STATE.user.role === 'doctor') {
    loadDashboard();
  } else if (STATE.user.role === 'secretaria') {
    switchTab('waiting-room');
    loadWaitingRoom();
  } else {
    switchTab('admin-dashboard');
  }
});

async function loadClinicName() {
  const data = await api('GET', '/api/settings/clinic_name');
  if (data.success && data.clinic_name) {
    const el = document.getElementById('app-clinic-name');
    if (el) el.textContent = data.clinic_name;
  }
}

function setupUI() {
  const u = STATE.user;
  const first = (u.full_name || u.username || '?')[0].toUpperCase();
  const avatarEl = document.getElementById('profile-avatar');
  if (avatarEl) {
    if (u.photo_url) {
      avatarEl.innerHTML = `<img src="${u.photo_url}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;" />`;
    } else {
      avatarEl.innerHTML = first;
    }
  }
  document.getElementById('profile-name').textContent   = u.full_name || u.username;
  const roleEl = document.getElementById('profile-role');
  const roleLabels = { admin: '⚙️ Administrador', doctor: '🩺 Doctor', secretaria: '📋 Secretaría' };
  roleEl.textContent = roleLabels[u.role] || u.role;
  roleEl.className   = `profile-role ${u.role}`;

  // Mostrar navegación según rol
  if (u.role === 'admin') {
    document.getElementById('nav-admin').style.display = 'block';
    document.querySelectorAll('.admin-only-btn').forEach(b => b.style.display = '');
  } else if (u.role === 'secretaria') {
    document.getElementById('nav-secretaria').style.display = 'block';
    document.querySelectorAll('.admin-only-btn').forEach(b => b.style.display = 'none');
  } else {
    // doctor
    document.getElementById('nav-doctor').style.display = 'block';
    document.querySelectorAll('.admin-only-btn').forEach(b => b.style.display = 'none');
    // Ocultar botón "Nuevo Paciente" para doctores
    const btnNewPt = document.getElementById('btn-new-patient');
    if (btnNewPt) btnNewPt.style.display = 'none';
  }

  // Poblar selector de usuarios para notificaciones
  loadNotifUserList();
  // Cargar conteo de mensajes no leídos
  loadUnreadCount();
}

async function handleLogout() {
  await api('POST', '/api/auth/logout');
  window.location.href = '/login';
}

async function loadDashboard() {
  const data = await api('GET', '/api/dashboard/stats');
  if (!data.success) return;
  const s = data.stats;
  
  if (s.is_doctor) {
    document.getElementById('stat-citas-hoy-val').textContent = s.citas_hoy ?? '0';
    document.getElementById('stat-citas-pendientes-val').textContent = s.citas_pendientes ?? '0';
    document.getElementById('stat-citas-hechas-val').textContent = s.citas_hechas ?? '0';
    document.getElementById('stat-citas-manana-val').textContent = s.citas_manana ?? '0';
  } else {
    document.getElementById('stat-citas-hoy-val').textContent    = s.total_patients     ?? '—';
    document.getElementById('stat-citas-pendientes-val').textContent      = s.total_visits        ?? '—';
    document.getElementById('stat-citas-hechas-val').textContent   = s.total_diagnoses     ?? '—';
    document.getElementById('stat-citas-manana-val').textContent = s.total_emergencias   ?? '—';
    // Fix labels if admin visits doctor dashboard instead
    document.querySelector('#stat-citas-hoy .stat-label').textContent = "Pacientes Registrados";
    document.querySelector('#stat-citas-pendientes .stat-label').textContent = "Visitas Totales";
    document.querySelector('#stat-citas-hechas .stat-label').textContent = "Diagnósticos Generados";
    document.querySelector('#stat-citas-manana .stat-label').textContent = "Emergencias Atendidas";
  }
  
  const emEl = document.getElementById('stat-emergencias-val');
  if (emEl) emEl.textContent = s.total_emergencias ?? '—';
  
  const commonEl = document.getElementById('most-common-diag');
  if (commonEl) commonEl.textContent = s.most_common || '—';
}

async function loadAdminDashboard() {
  const data = await api('GET', '/api/dashboard/stats');
  if (!data.success) return;
  const s = data.stats;
  document.getElementById('adm-stat-patients').textContent  = s.total_patients  ?? '—';
  document.getElementById('adm-stat-doctors').textContent   = s.active_doctors  ?? '—';
  document.getElementById('adm-stat-diagnoses').textContent = s.total_diagnoses ?? '—';
  document.getElementById('adm-stat-red').textContent       = s.red_alerts      ?? '—';
  const admMostCommon = document.getElementById('adm-most-common');
  if (admMostCommon) admMostCommon.textContent = s.most_common || '—';

  // Gráficas con Chart.js
  renderAdminCharts(s);
}

function renderAdminCharts(s) {
  const chartDefaults = {
    plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
    scales: {
      x: { ticks: { color: '#475569' }, grid: { color: 'rgba(255,255,255,0.04)' } },
      y: { ticks: { color: '#475569' }, grid: { color: 'rgba(255,255,255,0.04)' } }
    }
  };

  // 1. Visitas por semana (barras)
  const ctxVisits = document.getElementById('chart-visits-week');
  if (ctxVisits) {
    if (ctxVisits._chartInstance) ctxVisits._chartInstance.destroy();
    const visitLabels = s.visits_by_week?.labels || ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'];
    const visitData   = s.visits_by_week?.data   || [0,0,0,0,0,0,0];
    ctxVisits._chartInstance = new Chart(ctxVisits, {
      type: 'bar',
      data: {
        labels: visitLabels,
        datasets: [{ label: 'Visitas', data: visitData,
          backgroundColor: 'rgba(59,130,246,0.4)', borderColor: '#3b82f6',
          borderWidth: 1, borderRadius: 6 }]
      },
      options: { ...chartDefaults, responsive: true, maintainAspectRatio: true }
    });
  }

  // 2. Top diagnósticos (dona)
  const ctxDiag = document.getElementById('chart-diag-dist');
  if (ctxDiag && s.top_diagnoses) {
    if (ctxDiag._chartInstance) ctxDiag._chartInstance.destroy();
    const colors = ['#3b82f6','#06b6d4','#10b981','#f59e0b','#8b5cf6','#ef4444'];
    ctxDiag._chartInstance = new Chart(ctxDiag, {
      type: 'doughnut',
      data: {
        labels: s.top_diagnoses.map(d => d.name),
        datasets: [{ data: s.top_diagnoses.map(d => d.count),
          backgroundColor: colors, borderColor: 'rgba(255,255,255,0.06)', borderWidth: 2 }]
      },
      options: {
        responsive: true, maintainAspectRatio: true,
        plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 } } } }
      }
    });
  }

  // 3. Nuevos pacientes / mes (línea)
  const ctxGrowth = document.getElementById('chart-patients-growth');
  if (ctxGrowth) {
    if (ctxGrowth._chartInstance) ctxGrowth._chartInstance.destroy();
    const labels = s.patients_by_month?.labels || [];
    const pdata  = s.patients_by_month?.data   || [];
    ctxGrowth._chartInstance = new Chart(ctxGrowth, {
      type: 'line',
      data: {
        labels,
        datasets: [{ label: 'Nuevos Pacientes', data: pdata,
          borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)',
          fill: true, tension: 0.4, pointRadius: 4, pointBackgroundColor: '#10b981' }]
      },
      options: { ...chartDefaults, responsive: true, maintainAspectRatio: true }
    });
  }

  // 4. Consultas vs Emergencias (dona)
  const ctxTypes = document.getElementById('chart-visit-types');
  if (ctxTypes) {
    if (ctxTypes._chartInstance) ctxTypes._chartInstance.destroy();
    const consultas   = s.total_visits   - (s.total_emergencias || 0) || 0;
    const emergencias = s.total_emergencias || 0;
    ctxTypes._chartInstance = new Chart(ctxTypes, {
      type: 'doughnut',
      data: {
        labels: ['Consultas', 'Emergencias'],
        datasets: [{ data: [consultas, emergencias],
          backgroundColor: ['rgba(59,130,246,0.6)', 'rgba(239,68,68,0.6)'],
          borderColor: ['#3b82f6','#ef4444'], borderWidth: 2 }]
      },
      options: {
        responsive: true, maintainAspectRatio: true,
        plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 } } } }
      }
    });
  }
}

// PACIENTES
async function loadPatients(search = '') {
  const url  = '/api/patients' + (search ? `?search=${encodeURIComponent(search)}` : '');
  const data = await api('GET', url);
  if (!data.success) return;
  STATE.patients = data.patients;
  const canEdit = STATE.user && (STATE.user.role === 'admin' || STATE.user.role === 'secretaria');
  renderPatientsTable('patients-list', data.patients, canEdit);
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
    editBtn.style.display = (STATE.user.role === 'admin' || STATE.user.role === 'secretaria') ? '' : 'none';
  }
  STATE.editingPatientId = id;
  openModal('modal-view-patient');
}

function openNewPatientModal() {
  clearPatientForm();
  document.getElementById('modal-patient-title').textContent = 'Registrar Nuevo Paciente';
  openModal('modal-new-patient');
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
  
  const photoUrlField = document.getElementById('pt-photo-url');
  const photoPreview = document.getElementById('pt-photo-preview');
  const photoPlaceholder = document.getElementById('pt-photo-placeholder');
  
  if (photoUrlField) photoUrlField.value = p.photo_url || '';
  if (photoPreview && photoPlaceholder) {
    if (p.photo_url) {
      photoPreview.src = p.photo_url;
      photoPreview.style.display = 'block';
      photoPlaceholder.style.display = 'none';
    } else {
      photoPreview.src = '';
      photoPreview.style.display = 'none';
      photoPlaceholder.style.display = 'block';
    }
  }

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
  const photo_url = document.getElementById('pt-photo-url') ? document.getElementById('pt-photo-url').value : null;

  if (!cedula || !name) { toast('warning', 'Cédula y nombre son obligatorios.'); return; }

  const ants = {};
  document.querySelectorAll('#modal-antecedentes-grid .symptom-toggle').forEach(lbl => {
    const cb = lbl.querySelector('input[type=checkbox]');
    const n  = lbl.textContent.trim();
    ants[n]  = cb.checked;
  });

  const payload = { cedula, name, dob, gender, phone: phone || null,
                    blood_type: blood || null, antecedentes: ants, photo_url: photo_url };

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
  ['pt-cedula','pt-name','pt-dob','pt-gender','pt-phone','pt-blood','pt-photo-url']
    .forEach(id => { const el = document.getElementById(id); if (el) el.value = el.tagName === 'SELECT' ? el.options[0].value : ''; });
  
  const photoPreview = document.getElementById('pt-photo-preview');
  const photoPlaceholder = document.getElementById('pt-photo-placeholder');
  if (photoPreview) { photoPreview.src = ''; photoPreview.style.display = 'none'; }
  if (photoPlaceholder) photoPlaceholder.style.display = 'block';

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

async function loadDiagnoseTab() {
  updateVitalBadge(null);
  
  // Si no hay usuario en sesión, salir
  if (!STATE.user) return;
  
  // Ocultar elementos de IA y manual al cargar
  document.getElementById('no-sub-banner').style.display = 'none';
  document.getElementById('manual-diagnosis-inputs').style.display = 'none';
  document.getElementById('btn-diag-phase1').style.display = '';

  // Si no es doctor, no es necesario validar suscripción
  if (STATE.user.role !== 'doctor') return;

  // Cargar datos del perfil para obtener el estado de suscripción más reciente
  const res = await api('GET', '/api/profile');
  if (res.success && res.user) {
    STATE.user = res.user; // Actualizar estado local
    
    const isSubscribed = STATE.user.subscription_active;
    const banner = document.getElementById('no-sub-banner');
    const btnIA = document.getElementById('btn-diag-phase1');
    const manualInputs = document.getElementById('manual-diagnosis-inputs');

    if (!isSubscribed) {
      if (banner) banner.style.display = 'block';
      if (btnIA) btnIA.style.display = 'none';
      if (manualInputs) manualInputs.style.display = 'block';
    } else {
      if (banner) banner.style.display = 'none';
      if (btnIA) btnIA.style.display = '';
      if (manualInputs) manualInputs.style.display = 'none';
    }
  }
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
  const diagAppId = document.getElementById('diag-appointment-id');
  if (diagAppId) diagAppId.value = '';
  closeModal('modal-select-patient');
  
  const infoEl = document.getElementById('diag-patient-info');
  infoEl.style.display = 'flex';
  infoEl.style.alignItems = 'center';
  infoEl.style.gap = '16px';
  infoEl.innerHTML = `
    ${p.photo_url ? `<img src="${p.photo_url}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border);" />` : ''}
    <div>
      <strong>Paciente seleccionado:</strong><br/>
      <span style="font-size: 16px;">${p.name}</span> <span style="color: var(--text-muted);">(${p.cedula})</span>
    </div>
  `;
  
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

async function openAppointmentSelectModal() {
  const data = await api('GET', '/api/appointments');
  if (!data.success) return;
  const docs = await api('GET', '/api/users');
  if (docs.success) STATE.allUsers = docs.users;

  STATE.allAppointments = data.appointments.filter(a => a.status !== 'completada' && a.status !== 'cancelada');
  document.getElementById('search-select-patient').value = '';
  document.getElementById('search-select-patient').onkeyup = filterSelectAppointments;
  filterSelectAppointments();
  openModal('modal-select-patient');
}

function filterSelectAppointments() {
  const q = document.getElementById('search-select-patient').value.toLowerCase();
  const listEl = document.getElementById('select-patient-list');
  const apps = STATE.allAppointments.filter(a => a.patient_name.toLowerCase().includes(q) || a.patient_cedula.includes(q));
  
  if (!apps.length) {
    listEl.innerHTML = '<div style="padding:16px;color:var(--text-muted);text-align:center;">No hay citas abiertas para consultar.</div>';
    return;
  }
  
  listEl.innerHTML = apps.map(a => `
    <div class="patient-select-item" style="padding: 12px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center;">
      <div>
        <div style="font-weight: 600; color: var(--text-primary);">${a.patient_name}</div>
        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Cita: ${a.scheduled_date} ${a.scheduled_time || ''} | Motivo: ${a.notes || '—'}</div>
      </div>
      <button class="btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="selectConsultAppointment(${a.id}, ${a.patient_id})">Atender</button>
    </div>
  `).join('');
}

async function selectConsultAppointment(appId, ptId) {
  const data = await api('GET', `/api/patients/${ptId}`);
  if (!data.success) return;
  const p = data.patient;
  STATE.currentPatient = p;
  STATE.currentVisitId = null;
  document.getElementById('diag-appointment-id').value = appId;
  
  closeModal('modal-select-patient');
  
  const infoEl = document.getElementById('diag-patient-info');
  infoEl.style.display = 'flex';
  infoEl.style.alignItems = 'center';
  infoEl.style.gap = '16px';
  infoEl.innerHTML = `
    ${p.photo_url ? `<img src="${p.photo_url}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border);" />` : ''}
    <div>
      <strong>Paciente en consulta (Cita):</strong><br/>
      <span style="font-size: 16px;">${p.name}</span> <span style="color: var(--text-muted);">(${p.cedula})</span>
    </div>
  `;
  
  const nameInput = document.getElementById('diag-patient-name');
  const nameGroup = document.getElementById('diag-name-group');
  if (nameInput) { nameInput.value = p.name; nameGroup.style.display = 'block'; }
  document.getElementById('diag-patient-id').value = p.id;
  
  const app = STATE.allAppointments.find(a => a.id === appId);
  if (app && app.notes) {
    document.getElementById('diag-motivo').value = app.notes;
  }
  
  const edadInput = document.getElementById('v-edad');
  if (edadInput) {
    edadInput.value = p.age ?? calcAge(p.dob);
    updateVitalBadge(edadInput);
  }
  
  // Marcar antecedentes ...
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

function calculateIMC() {
  const peso = parseFloat(document.getElementById('v-peso').value) || 0;
  const altura = parseFloat(document.getElementById('v-altura').value) || 1;
  const imc = peso / Math.pow(altura/100, 2);
  const imcStr = imc.toFixed(1);
  
  document.getElementById('val-imc').textContent = imcStr;
  document.getElementById('v-imc').value = imcStr;
  
  const badgeEl = document.getElementById('badge-imc');
  if (!badgeEl) return;
  if (imc < 18.5) { badgeEl.className = 'vital-badge warn'; badgeEl.textContent = 'Bajo peso'; }
  else if (imc < 25) { badgeEl.className = 'vital-badge ok'; badgeEl.textContent = 'Normal'; }
  else if (imc < 30) { badgeEl.className = 'vital-badge warn'; badgeEl.textContent = 'Sobrepeso'; }
  else { badgeEl.className = 'vital-badge alert'; badgeEl.textContent = 'Obesidad'; }
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
    const val = parseFloat(el.value) || 0;
    
    // Update visual label regardless of rules
    const valDisplay = document.getElementById(`val-${id.replace('v-','')}`);
    if (valDisplay) valDisplay.textContent = el.step === "0.1" ? val.toFixed(1) : Math.round(val);

    const rule = rules[id];
    if (rule) {
        const [cls, label] = rule(val);
        const badgeEl = document.getElementById(`badge-${id.replace('v-','')}`);
        if (badgeEl) { badgeEl.className = `vital-badge ${cls}`; badgeEl.textContent = label; }
    }
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
    peso:        parseFloat(document.getElementById('v-peso')?.value)        || 70,
    altura:      parseFloat(document.getElementById('v-altura')?.value)      || 170,
    grasa_corporal: parseFloat(document.getElementById('v-grasa_corporal')?.value) || 20,
    imc:         parseFloat(document.getElementById('v-imc')?.value)         || 24.2,
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
  STATE.geminiChatHistory = []; // Reset chat on new diagnosis

  // Mostrar resultado y ocultar inputs
  document.getElementById('phase-1-inputs').style.display = 'none';
  renderPhase1Result(res);
  document.getElementById('phase1-result').style.display = '';
  document.getElementById('phase1-result').scrollIntoView({ behavior: 'smooth' });

  // Lanzar análisis Gemini en paralelo (no bloquea la UI)
  runGeminiAnalysis(res.probabilities);
}

async function runGeminiAnalysis(probs) {
  const panel = document.getElementById('gemini-analisis-panel');
  if (!panel) return;
  panel.style.display = '';
  panel.innerHTML = `
    <div class="gemini-panel">
      <div class="gemini-panel-header">
        <span class="gemini-badge">✨ Gemini AI</span>
        <span>Analizando con IA clínica...</span>
      </div>
      <div class="gemini-loading">
        <div class="spinner-ring" style="width:20px;height:20px;border-width:2px;"></div>
        <span>El motor de IA está procesando el contexto bayesiano...</span>
      </div>
    </div>
  `;

  try {
    const res = await api('POST', '/api/diagnose/gemini-analisis', {
      probabilities: probs,
      sintomas:      STATE.diagSintomas,
      constantes:    STATE.diagConstantes,
      antecedentes:  STATE.diagAntecedentes,
    });

    if (!res.success) {
      panel.innerHTML = '';
      return;
    }

    const alertas = (res.alertas_gemini || []).map(a =>
      `<div class="gemini-alerta">⚠️ ${a}</div>`
    ).join('');

    const sugeridos = (res.sintomas_sugeridos || []).map(s =>
      `<span class="gemini-tag">${s}</span>`
    ).join('');

    panel.innerHTML = `
      <div class="gemini-panel">
        <div class="gemini-panel-header">
          <span class="gemini-badge">✨ Gemini AI</span>
          <span style="color:var(--text-muted);font-size:12px;">${res.fallback ? 'Modo offline' : 'Análisis en tiempo real'}</span>
        </div>

        <div class="gemini-validacion">
          <p>${res.validacion || ''}</p>
        </div>

        ${alertas ? `<div class="gemini-alertas-section">${alertas}</div>` : ''}

        ${sugeridos ? `
          <div class="gemini-sugeridos-section">
            <div class="gemini-sugeridos-label">🔎 Explorar también:</div>
            <div class="gemini-tags">${sugeridos}</div>
          </div>
        ` : ''}

        ${res.confianza_gemini ? `
          <div class="gemini-confianza">
            <strong>Valoración Gemini:</strong> ${res.confianza_gemini}
          </div>
        ` : ''}
      </div>
    `;
  } catch(e) {
    panel.innerHTML = '';
  }
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
    const appIdRaw = document.getElementById('diag-appointment-id')?.value;
    const appointmentId = appIdRaw ? parseInt(appIdRaw) : null;
    // Crear visita silenciosamente para poder guardar el diagnóstico
    const visitRes = await api('POST', '/api/visits', {
      patient_id: patientId,
      visit_type: 'consulta',
      motivo_consulta: motivoConsulta,
      doctor_notes: document.getElementById('diag-doctor-notes')?.value.trim() || null,
      constantes: STATE.diagConstantes,
      sintomas: STATE.diagSintomas,
      appointment_id: appointmentId
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

  // Guardar datos temporalmente para la decisión final
  STATE.finalDiagnosisRes = res;
  STATE.finalTestsResultados = testsResultados;

  renderFinalResult(res);
  toast('success', '✅ Diagnóstico final calculado. Verifique y finalice la consulta.');
}

function toggleRefutationFields(chk) {
  const fields = document.getElementById('refutation-fields');
  if (fields) fields.style.display = chk.checked ? 'block' : 'none';
}

async function saveFinalDecision(createPrescription) {
  const btn1 = document.getElementById('btn-finish-prescribe');
  const btn2 = document.getElementById('btn-finish-only');
  if (btn1) btn1.disabled = true;
  if (btn2) btn2.disabled = true;

  const isRefuted = document.getElementById('chk-refute-ai')?.checked || false;
  const doctorOverride = document.getElementById('doctor-override-diagnosis')?.value.trim();
  const refutationReason = document.getElementById('refutation-reason')?.value.trim();

  if (isRefuted && !doctorOverride) {
    toast('warning', 'Si refutas el diagnóstico, debes escribir el diagnóstico médico real.');
    if (btn1) btn1.disabled = false;
    if (btn2) btn2.disabled = false;
    return;
  }

  // Guardar usando /api/diagnose/final pero con save_diagnosis: true
  const patientName = document.getElementById('diag-patient-name').value.trim() || 'Paciente Anónimo';
  const motivoConsulta = document.getElementById('diag-motivo').value.trim() || 'Sin especificar';

  const res = await api('POST', '/api/diagnose/final', {
    patient_id: STATE.currentPatient?.id,
    patient_name: patientName,
    motivo_consulta: motivoConsulta,
    visit_id: STATE.currentVisitId,
    preliminar_probs: STATE.phase1Probs,
    tests_resultados: STATE.finalTestsResultados,
    sintomas: STATE.diagSintomas,
    antecedentes: STATE.diagAntecedentes,
    constantes: STATE.diagConstantes,
    save_diagnosis: true,
    is_refuted: isRefuted,
    refutation_reason: refutationReason,
    doctor_override_diagnosis: doctorOverride
  });

  if (!res.success) {
    toast('error', res.error || 'Error al guardar el diagnóstico final.');
    if (btn1) btn1.disabled = false;
    if (btn2) btn2.disabled = false;
    return;
  }

  // Marcar la cita como completada
  const appId = document.getElementById('diag-appointment-id')?.value;
  if (appId) {
    api('POST', `/api/appointments/${appId}/status`, { status: 'completada' });
  }

  toast('success', 'Consulta finalizada con éxito.');

  if (createPrescription && STATE.currentPatient && STATE.currentVisitId) {
    // Abrir modal de receta
    openPrescriptionModal(STATE.currentPatient.id, STATE.currentVisitId);
  } else {
    // Limpiar para nueva consulta
    resetDiagnose();
  }
}

function renderFinalResult(res) {
  const alertClass = { Verde: 'verde', Amarillo: 'amarillo', Rojo: 'rojo' }[res.alert_level] || 'verde';
  const report     = markdownToHtml(res.explanation || '');
  const geminiUsed = res.gemini_used === true;

  const html = `
    <div class="section-card">
      <div class="section-header">
        <h2>🏆 Diagnóstico Final — ${res.diagnosis}</h2>
        <div style="display:flex;gap:8px;align-items:center;">
          <span class="badge badge-${alertClass}">${res.alert_level}</span>
          <span class="confidence-pill">${(res.probability * 100).toFixed(2)}%</span>
          ${geminiUsed ? '<span class="gemini-badge" style="font-size:11px;">✨ Gemini AI</span>' : ''}
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
        <h2>📋 Informe Clínico Detallado ${geminiUsed ? '<span class="gemini-badge" style="font-size:11px;margin-left:8px;">✨ IA Enriquecido</span>' : ''}</h2>
        <button class="btn-outline" onclick="openFullReport()">Ver en pantalla completa</button>
      </div>
      <div class="clinical-report" id="clinical-report-preview">${report}</div>
    </div>

    <!-- Panel de Chat Médico Gemini AI -->
    <div class="section-card gemini-chat-card" style="margin-top:20px;">
      <div class="section-header">
        <div style="display:flex;align-items:center;gap:10px;">
          <h2>🧠 Consultar al Internista IA</h2>
          <span class="gemini-badge">✨ Gemini AI</span>
        </div>
        <span style="font-size:12px;color:var(--text-muted);">Haz preguntas sobre el diagnóstico, medicamentos o señales de alarma</span>
      </div>
      <div id="gemini-chat-messages" class="gemini-chat-messages">
        <div class="gemini-chat-msg model">
          <div class="gemini-chat-bubble">
            Hola, soy tu Internista de Apoyo IA. He analizado el caso de <strong>${res.patient_name || 'tu paciente'}</strong> y el diagnóstico bayesiano apunta a <strong>${res.diagnosis}</strong> con un ${(res.probability*100).toFixed(1)}% de confianza. ¿Qué deseas consultar sobre este caso?
          </div>
        </div>
      </div>
      <div class="gemini-chat-input-row">
        <input
          type="text"
          id="gemini-chat-input"
          class="form-input gemini-chat-input"
          placeholder="Ej. ¿Cuáles son las señales de alarma para este diagnóstico?"
          onkeydown="if(event.key==='Enter') sendGeminiMessage()"
        />
        <button class="btn-primary gemini-send-btn" id="gemini-send-btn" onclick="sendGeminiMessage()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </div>
    </div>

    <div class="section-card" style="margin-top:20px; border: 1px solid var(--border-color); background: rgba(255, 255, 255, 0.02);">
      <div class="section-header">
        <h2>⚖️ Decisión del Especialista</h2>
        <span class="badge badge-verde" id="ai-accepted-badge">Diagnóstico IA Aceptado por defecto</span>
      </div>
      <p style="color:var(--text-muted); font-size:13px; margin-bottom:16px;">
        Si difieres del diagnóstico proporcionado por el motor bayesiano, puedes refutarlo e indicar el diagnóstico médico final.
      </p>
      
      <div class="form-group" style="margin-bottom: 12px;">
        <label class="form-label" style="display:flex;align-items:center;gap:8px;cursor:pointer;">
          <input type="checkbox" id="chk-refute-ai" onchange="toggleRefutationFields(this)" />
          Refutar este diagnóstico de IA
        </label>
      </div>

      <div id="refutation-fields" style="display:none; padding:16px; background:rgba(239, 68, 68, 0.05); border-radius:8px; margin-bottom:16px;">
        <div class="form-group" style="margin-bottom:12px;">
          <label class="form-label">Diagnóstico Final Real (Doctor)</label>
          <input type="text" id="doctor-override-diagnosis" class="form-input" placeholder="Ej. Migraña Crónica" />
        </div>
        <div class="form-group">
          <label class="form-label">Motivo de Refutación Clínica</label>
          <textarea id="refutation-reason" class="form-input" rows="2" placeholder="Ej. El paciente presenta historial de X, los exámenes descartan Y..."></textarea>
        </div>
      </div>

      <div class="form-actions" style="margin-top:24px; border-top:1px solid var(--border-color); padding-top:16px; justify-content: flex-start; gap: 12px;">
        <button id="btn-finish-prescribe" class="btn-primary" onclick="saveFinalDecision(true)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" style="margin-right:6px;vertical-align:middle;"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          Finalizar y Crear Receta
        </button>
        <button id="btn-finish-only" class="btn-secondary" onclick="saveFinalDecision(false)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" style="margin-right:6px;vertical-align:middle;"><path d="M5 12l5 5L20 7"/></svg>
          Solo Finalizar Consulta
        </button>
      </div>
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

async function sendGeminiMessage() {
  const input   = document.getElementById('gemini-chat-input');
  const sendBtn = document.getElementById('gemini-send-btn');
  const message = input?.value.trim();
  if (!message || !STATE.finalDiagnosisRes) return;

  const res = STATE.finalDiagnosisRes;
  input.value = '';
  sendBtn.disabled = true;

  // Mostrar mensaje del usuario
  appendGeminiMessage('user', message);

  // Mostrar indicador de escritura
  const typingId = 'gemini-typing-' + Date.now();
  appendGeminiTyping(typingId);

  // Añadir al historial
  STATE.geminiChatHistory.push({ role: 'user', text: message });

  try {
    const chatRes = await api('POST', '/api/diagnose/chat-gemini', {
      diagnostico:        res.diagnosis,
      probabilidad:       res.probability,
      sintomas_activos:   Object.keys(STATE.diagSintomas).filter(k => STATE.diagSintomas[k]),
      antecedentes_activos: Object.keys(STATE.diagAntecedentes).filter(k => STATE.diagAntecedentes[k]),
      constantes:         STATE.diagConstantes,
      message:            message,
      history:            STATE.geminiChatHistory.slice(-10), // últimos 10 turnos
    });

    removeGeminiTyping(typingId);

    const responseText = chatRes.success
      ? chatRes.response
      : 'Lo siento, el asistente no está disponible en este momento. Consulte el informe clínico.';

    appendGeminiMessage('model', responseText);
    STATE.geminiChatHistory.push({ role: 'model', text: responseText });
  } catch(e) {
    removeGeminiTyping(typingId);
    appendGeminiMessage('model', 'Error de conexión con el asistente médico. Intente nuevamente.');
  }

  sendBtn.disabled = false;
  input.focus();
}

function appendGeminiMessage(role, text) {
  const container = document.getElementById('gemini-chat-messages');
  if (!container) return;
  const div = document.createElement('div');
  div.className = `gemini-chat-msg ${role}`;
  // Simple markdown parsing for bold
  const formatted = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>');
  div.innerHTML = `<div class="gemini-chat-bubble">${formatted}</div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function appendGeminiTyping(id) {
  const container = document.getElementById('gemini-chat-messages');
  if (!container) return;
  const div = document.createElement('div');
  div.id = id;
  div.className = 'gemini-chat-msg model';
  div.innerHTML = `<div class="gemini-chat-bubble gemini-typing-bubble">
    <span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>
  </div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function removeGeminiTyping(id) {
  document.getElementById(id)?.remove();
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

// AGENDA / CITAS
let calendarInstance = null;

async function loadAppointments() {
  const filterDoc = document.getElementById('appointment-doctor-filter')?.value;
  const url = '/api/appointments' + (filterDoc ? `?doctor_id=${filterDoc}` : '');
  const data = await api('GET', url);
  if (!data.success) { toast('error', 'Error cargando citas.'); return; }
  
  STATE.allAppointments = data.appointments;
  renderAppointmentsTable(STATE.allAppointments);
  
  // Update calendar if it's visible
  if (calendarInstance && document.getElementById('app-calendar-view').style.display !== 'none') {
    renderCalendar();
  }
  
  // Cargar pacientes y doctores para el modal si no están cargados
  if (STATE.user.role === 'admin' || STATE.user.role === 'secretaria') {
    document.getElementById('appointment-doctor-filter').style.display = 'block';
    document.getElementById('app-view-toggles').style.display = 'flex';
    
    const docs = await api('GET', '/api/users');
    if (docs.success) {
      const doctors = docs.users.filter(u => u.role === 'doctor');
      STATE.allDoctors = doctors;
      
      const filterSelect = document.getElementById('appointment-doctor-filter');
      if (filterSelect.options.length <= 1) {
          filterSelect.innerHTML = `<option value="">Todos los doctores</option>` + doctors.map(d => `<option value="${d.id}">${d.full_name || d.username}</option>`).join('');
      }
    }
    const pts = await api('GET', '/api/patients');
    if (pts.success) {
      STATE.allPatients = pts.patients;
    }
  } else {
    // Si es doctor, no mostrar el botón de agendar ni el filtro de doctores
    document.getElementById('btn-new-appointment').style.display = 'none';
  }
}

function switchAppointmentView(viewType) {
  document.getElementById('btn-view-table').style.background = viewType === 'table' ? 'var(--bg-hover)' : 'transparent';
  document.getElementById('btn-view-calendar').style.background = viewType === 'calendar' ? 'var(--bg-hover)' : 'transparent';
  
  document.getElementById('app-table-view').style.display = viewType === 'table' ? 'block' : 'none';
  document.getElementById('app-calendar-view').style.display = viewType === 'calendar' ? 'block' : 'none';
  
  if (viewType === 'calendar') {
    renderCalendar();
  }
}

function renderCalendar() {
  const calendarEl = document.getElementById('calendar');
  if (!calendarInstance) {
    calendarInstance = new FullCalendar.Calendar(calendarEl, {
      initialView: 'timeGridWeek',
      locale: 'es',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      slotMinTime: '00:00:00',
      slotMaxTime: '24:00:00',
      contentHeight: 'auto', // Expande el contenedor para evitar celdas apretadas
      expandRows: true, // Expande las filas al máximo disponible
      allDaySlot: false,
      editable: true,
      eventClick: function(info) {
        if (STATE.user.role === 'secretaria' || STATE.user.role === 'admin') {
            openEditAppointmentModal(info.event.id);
        }
      },
      eventDrop: async function(info) {
        const appId = info.event.id;
        const d = info.event.start;
        const pad = n => n.toString().padStart(2, '0');
        const newDate = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
        const newTime = `${pad(d.getHours())}:${pad(d.getMinutes())}:00`;
        
        const res = await api('PUT', `/api/appointments/${appId}/reschedule`, {
          scheduled_date: newDate,
          scheduled_time: newTime
        });
        
        if (res.success) {
          toast('success', 'Cita reprogramada correctamente.');
          loadAppointments(); // refresh both table and state
        } else {
          toast('error', res.error || 'Error al reprogramar la cita.');
          info.revert();
        }
      }
    });
    calendarInstance.render();
  }
  
  calendarInstance.removeAllEvents();
  
  const activeApps = STATE.allAppointments.filter(a => a.status !== 'cancelada' && a.status !== 'eliminada');
  const events = activeApps.map(a => {
    let color = '#3b82f6';
    if (a.status === 'completada') color = '#10b981';
    else if (a.status === 'cancelada') color = '#ef4444';
    else if (a.status === 'en_curso') color = '#f59e0b';
    
    let endStr = undefined;
    let startStr = a.scheduled_date;
    
    if (a.scheduled_time) {
        const timePart = a.scheduled_time.substring(0, 8); // Ensure HH:MM:SS
        startStr = `${a.scheduled_date}T${timePart}`;
        const d = new Date(startStr);
        if (!isNaN(d.getTime())) {
            d.setHours(d.getHours() + 1);
            const pad = n => n.toString().padStart(2, '0');
            endStr = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}:00`;
        }
    }
    
    return {
      id: a.id,
      title: `${a.patient_name} - ${a.doctor_fullname}`,
      start: startStr,
      end: endStr,
      color: color,
      allDay: !a.scheduled_time
    };
  });
  
  calendarInstance.addEventSource(events);
}

function searchAppointments() {
  const q = (document.getElementById('appointment-search')?.value || '').toLowerCase();
  const filtered = STATE.allAppointments.filter(a => 
    (a.patient_name || '').toLowerCase().includes(q) ||
    (a.patient_cedula || '').toLowerCase().includes(q)
  );
  renderAppointmentsTable(filtered);
}

function renderAppointmentsTable(apps) {
  const el = document.getElementById('appointments-list');
  if (!apps.length) {
    el.innerHTML = `<div class="empty-state"><span>No hay citas agendadas.</span></div>`;
    return;
  }
  const rows = apps.map(a => {
    let statusBadge = '';
    if (a.status === 'abierta') statusBadge = '<span class="badge" style="background:#3b82f6;color:white;">Abierta</span>';
    else if (a.status === 'completada') statusBadge = '<span class="badge badge-verde">Completada</span>';
    else if (a.status === 'cancelada') statusBadge = '<span class="badge badge-rojo">Cancelada</span>';
    else statusBadge = `<span class="badge badge-amarillo">${a.status}</span>`;
    
    return `<tr>
      <td>
        <strong style="color:var(--text-primary)">${a.patient_name}</strong>
        ${a.parent_appointment_id ? '<span class="badge badge-amarillo" style="font-size:10px; margin-left:8px;">Seguimiento</span>' : ''}
      </td>
      <td>${a.scheduled_date} ${a.scheduled_time || ''}</td>
      <td>${a.doctor_fullname || '—'}</td>
      <td>${a.notes || '—'}</td>
      <td>${statusBadge}</td>
      <td style="display:flex; gap:6px;">
        ${(STATE.user.role === 'secretaria' || STATE.user.role === 'admin') ? 
          `<button class="btn-icon" title="Editar Cita" style="color:var(--brand-primary);" onclick="openEditAppointmentModal(${a.id})">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
           </button>
           ${a.status === 'abierta' ? `<button class="btn-icon" title="Cancelar Cita" style="color:var(--danger);" onclick="cancelAppointment(${a.id})"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>` : ''}
          ` : ''
        }
      </td>
    </tr>`;
  }).join('');
  el.innerHTML = `<table class="data-table"><thead><tr><th>Paciente</th><th>Fecha y Hora</th><th>Doctor</th><th>Notas</th><th>Estado</th><th>Acción</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function openNewAppointmentModal() {
  document.getElementById('app-id').value = '';
  document.getElementById('app-patient').value = '';
  document.getElementById('app-patient-name').value = '';
  document.getElementById('app-doctor').value = '';
  document.getElementById('app-doctor-name').value = '';
  document.getElementById('app-date').value = '';
  document.getElementById('app-time').value = '';
  document.getElementById('app-status').value = 'abierta';
  document.getElementById('app-notes').value = '';
  document.getElementById('app-parent-appointment').value = '';
  
  document.getElementById('app-status-group').style.display = 'none';
  document.getElementById('app-parent-group').style.display = 'block';
  document.getElementById('modal-appointment-title').textContent = 'Agendar Nueva Cita';
  document.getElementById('btn-save-appointment').textContent = 'Agendar Cita';
  
  openModal('modal-new-appointment');
  loadPatientFollowupAppointments();
}

function openEditAppointmentModal(id) {
  const app = STATE.allAppointments.find(a => a.id == id);
  if (!app) return;
  document.getElementById('app-id').value = app.id;
  document.getElementById('app-patient').value = app.patient_id;
  document.getElementById('app-doctor').value = app.doctor_id;
  document.getElementById('app-date').value = app.scheduled_date;
  document.getElementById('app-time').value = app.scheduled_time ? app.scheduled_time.substring(0, 5) : '';
  document.getElementById('app-status').value = app.status;
  document.getElementById('app-notes').value = app.notes || '';
  
  // Buscar nombres en estado global
  const patient = STATE.allPatients ? STATE.allPatients.find(p => p.id == app.patient_id) : null;
  const doctor = STATE.allDoctors ? STATE.allDoctors.find(d => d.id == app.doctor_id) : null;
  document.getElementById('app-patient-name').value = patient ? patient.name : (app.patient_name || 'Paciente ID: ' + app.patient_id);
  document.getElementById('app-doctor-name').value = doctor ? (doctor.full_name || doctor.username) : (app.doctor_fullname || 'Doctor ID: ' + app.doctor_id);

  document.getElementById('app-status-group').style.display = 'block';
  document.getElementById('app-parent-group').style.display = 'none'; // No se edita el seguimiento
  document.getElementById('modal-appointment-title').textContent = 'Editar Cita';
  document.getElementById('btn-save-appointment').textContent = 'Guardar Cambios';
  
  openModal('modal-new-appointment');
}

function loadPatientFollowupAppointments() {
  const patientId = document.getElementById('app-patient').value;
  const select = document.getElementById('app-parent-appointment');
  select.innerHTML = '<option value="">-- No es seguimiento --</option>';
  if (!patientId || !STATE.allAppointments) return;

  const pastCompleted = STATE.allAppointments.filter(a => a.patient_id == patientId && a.status === 'completada');
  pastCompleted.sort((a,b) => new Date(b.scheduled_date) - new Date(a.scheduled_date));

  pastCompleted.forEach(a => {
    select.innerHTML += `<option value="${a.id}">${fmtDate(a.scheduled_date)} - Dr. ${a.doctor_fullname}</option>`;
  });
}

async function saveAppointment() {
  const appId = document.getElementById('app-id').value;
  const payload = {
    patient_id: document.getElementById('app-patient').value,
    doctor_id: document.getElementById('app-doctor').value,
    scheduled_date: document.getElementById('app-date').value,
    scheduled_time: document.getElementById('app-time').value,
    status: document.getElementById('app-status').value || 'abierta',
    notes: document.getElementById('app-notes').value.trim(),
    parent_appointment_id: document.getElementById('app-parent-appointment').value || null
  };
  
  if (!payload.patient_id || !payload.doctor_id || !payload.scheduled_date || !payload.scheduled_time) {
    toast('warning', 'Faltan campos obligatorios'); return;
  }
  
  const isEdit = !!appId;
  const url = isEdit ? `/api/appointments/${appId}` : '/api/appointments';
  const method = isEdit ? 'PUT' : 'POST';

  const res = await api(method, url, payload);
  if (res.success) {
    toast('success', isEdit ? 'Cita actualizada correctamente' : 'Cita agendada correctamente');
    closeModal('modal-new-appointment');
    loadAppointments();
  } else {
    toast('error', res.error || 'Error al guardar cita');
  }
}

async function cancelAppointment(id) {
  if (!confirm('¿Desea cancelar esta cita?')) return;
  const res = await api('POST', `/api/appointments/${id}/status`, { status: 'cancelada' });
  if (res.success) {
    toast('success', 'Cita cancelada');
    loadAppointments();
  } else {
    toast('error', 'Error al cancelar');
  }
}

// RECETAS MÉDICAS
function openPrescriptionModal() {
  STATE.rxList = [];
  renderRxList();
  document.getElementById('rx-medication').value = '';
  document.getElementById('rx-dosage').value = '';
  document.getElementById('rx-frequency').value = '';
  document.getElementById('rx-days').value = '';
  document.getElementById('rx-quantity').value = '';
  document.getElementById('rx-notes').value = '';
  openModal('modal-prescription');
}

function addMedicationToList() {
  const med = document.getElementById('rx-medication').value.trim();
  const dos = document.getElementById('rx-dosage').value.trim();
  const freq = document.getElementById('rx-frequency').value.trim();
  const days = document.getElementById('rx-days').value;
  const qty = document.getElementById('rx-quantity').value;
  const notes = document.getElementById('rx-notes').value.trim();
  
  if (!med || !dos || !freq || !days || !qty) {
    toast('warning', 'Completa los campos obligatorios (*) del medicamento.');
    return;
  }
  
  STATE.rxList.push({ med, dos, freq, days, qty, notes });
  renderRxList();
  
  document.getElementById('rx-medication').value = '';
  document.getElementById('rx-dosage').value = '';
  document.getElementById('rx-frequency').value = '';
  document.getElementById('rx-days').value = '';
  document.getElementById('rx-quantity').value = '';
  document.getElementById('rx-notes').value = '';
}

function removeMedication(index) {
  STATE.rxList.splice(index, 1);
  renderRxList();
}

function renderRxList() {
  const el = document.getElementById('rx-list');
  if (STATE.rxList.length === 0) {
    el.innerHTML = `<p style="color:var(--text-muted); font-size:13px; text-align:center; padding-top:20px;">No hay medicamentos en la receta.</p>`;
    return;
  }
  
  el.innerHTML = STATE.rxList.map((r, i) => `
    <div style="background:var(--bg-card); padding:10px; margin-bottom:10px; border-radius:6px; border:1px solid var(--border); display:flex; justify-content:space-between;">
      <div>
        <div style="font-weight:bold;">${r.med}</div>
        <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">
          ${r.dos} | ${r.freq} | x${r.days} días | Cant: ${r.qty}
          ${r.notes ? `<br/><i>Nota: ${r.notes}</i>` : ''}
        </div>
      </div>
      <button class="btn-icon" style="color:var(--danger);" onclick="removeMedication(${i})"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
  `).join('');
}

async function savePrescription() {
  if (STATE.rxList.length === 0) {
    toast('warning', 'Añade al menos un medicamento a la receta.');
    return;
  }
  if (!STATE.currentVisitId) {
    toast('error', 'Error: No hay visita activa.');
    return;
  }
  
  const btn = event.target;
  const orig = btn.textContent;
  btn.textContent = 'Guardando...';
  btn.disabled = true;
  
  let successCount = 0;
  for (const rx of STATE.rxList) {
    const res = await api('POST', `/api/visits/${STATE.currentVisitId}/prescription`, {
      medication: rx.med,
      dosage: rx.dos,
      frequency: rx.freq,
      duration_days: rx.days,
      quantity: rx.qty,
      notes: rx.notes
    });
    if (res.success) successCount++;
  }
  
  btn.textContent = orig;
  btn.disabled = false;
  
  if (successCount === STATE.rxList.length) {
    toast('success', 'Receta guardada correctamente en el historial.');
    closeModal('modal-prescription');
  } else {
    toast('error', 'Ocurrió un error al guardar algunos medicamentos.');
  }
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
      : u.role === 'secretaria'
        ? `<span class="badge badge-amarillo">Secretaria</span>`
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
  const cedula      = document.getElementById('usr-cedula').value.trim() || null;
  const photoUrl    = document.getElementById('usr-photourl').value.trim() || null;

  if (!username) { toast('warning', 'El nombre de usuario es obligatorio.'); return; }
  if (!id && !password) { toast('warning', 'La contraseña es obligatoria al crear un usuario.'); return; }
  if (password && password.length < 6) { toast('warning', 'La contraseña debe tener al menos 6 caracteres.'); return; }

  const payload = { username, role, full_name: fullName, email,
    matricula, especialidad, telefono, hospital, cedula, photo_url: photoUrl };
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
  document.getElementById('usr-cedula').value                 = u.cedula || '';
  document.getElementById('usr-photourl').value               = u.photo_url || '';
  onRoleChange();
  openModal('modal-new-user');
}

function clearUserForm() {
  document.getElementById('modal-user-title').textContent = 'Crear Nuevo Usuario';
  document.getElementById('edit-user-id').value = '';
  ['usr-username','usr-password','usr-fullname','usr-email',
   'usr-matricula','usr-especialidad','usr-telefono','usr-hospital','usr-cedula','usr-photourl']
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

// =============================================================================
// v3.0 — NUEVAS FUNCIONES
// =============================================================================

// ── MODAL PACIENTE CON TABS ──────────────────────────────────────────────────
STATE.viewingPatientId = null;

function switchPatientTab(tab) {
  ['info','vitals','meds','alerts','docs'].forEach(t => {
    document.getElementById(`patient-tab-${t}`).style.display = t === tab ? '' : 'none';
    const btn = document.getElementById(`mtab-${t}`);
    if (btn) btn.classList.toggle('active', t === tab);
  });
  // Lazy-load según pestaña
  if (tab === 'vitals')  loadPatientVitals(STATE.viewingPatientId);
  if (tab === 'meds')    loadPatientMeds(STATE.viewingPatientId);
  if (tab === 'alerts')  loadPatientAlerts(STATE.viewingPatientId);
  if (tab === 'docs')    loadPatientDocs(STATE.viewingPatientId);
}

async function viewPatient(id) {
  STATE.viewingPatientId = id;
  // Reset tabs
  switchPatientTab('info');

  const data = await api('GET', `/api/patients/${id}`);
  if (!data.success) { toast('error', 'No se pudo cargar el paciente.'); return; }
  const p = data.patient;

  document.getElementById('view-patient-title').textContent = p.name || 'Paciente';

  const age = p.age ?? calcAge(p.dob);
  const antsObj = p.antecedentes || {};
  const antsList = Object.keys(antsObj).filter(k => antsObj[k]);
  const ants = antsList.length ? antsList.map(a => `<span class="badge badge-amarillo">${a}</span>`).join(' ') : 'Ninguno registrado';

  const photoHtml = p.photo_url 
    ? `<img src="${p.photo_url}" style="width: 100px; height: 120px; object-fit: cover; border-radius: 8px; border: 1px solid var(--border);" />`
    : `<div style="width: 100px; height: 120px; border-radius: 8px; border: 1px dashed var(--border); background: var(--bg-input); display: flex; align-items: center; justify-content: center;"><svg viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="2" style="width: 40px; height: 40px;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div>`;

  document.getElementById('patient-tab-info').innerHTML = `
    <div style="padding:20px 28px; display: flex; gap: 24px; align-items: flex-start;">
      <div style="flex-shrink: 0;">
        ${photoHtml}
      </div>
      <div style="flex: 1;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
          <div class="form-group" style="margin:0;">
            <div class="form-label">Cédula / ID</div>
            <div style="color:var(--text-primary);font-weight:600;">${escHtml(p.cedula || '—')}</div>
          </div>
        <div class="form-group" style="margin:0;">
          <div class="form-label">Tipo de Sangre</div>
          <div style="color:var(--text-primary);font-weight:600;">${escHtml(p.blood_type || '—')}</div>
        </div>
        <div class="form-group" style="margin:0;">
          <div class="form-label">Fecha de Nacimiento</div>
          <div style="color:var(--text-primary);">${escHtml(p.dob || '—')} (${age} años)</div>
        </div>
        <div class="form-group" style="margin:0;">
          <div class="form-label">Género</div>
          <div style="color:var(--text-primary);">${escHtml(p.gender || '—')}</div>
        </div>
        <div class="form-group" style="margin:0;">
          <div class="form-label">Teléfono</div>
          <div style="color:var(--text-primary);">${escHtml(p.phone || '—')}</div>
        </div>
        <div class="form-group" style="margin:0;">
          <div class="form-label">Registrado</div>
          <div style="color:var(--text-muted);font-size:13px;">${fmtDate(p.created_at)}</div>
        </div>
        </div>
        <div style="margin-top:20px;">
          <div class="form-label">Antecedentes Patológicos</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">${ants}</div>
        </div>
      </div>
    </div>
  `;

  openModalOrig('modal-view-patient');
}

async function loadPatientVitals(id) {
  if (!id) return;
  const el = document.getElementById('patient-vitals-content');
  el.innerHTML = '<div class="loading-state"><div class="spinner-ring"></div></div>';
  const data = await api('GET', `/api/history?patient_id=${id}&limit=10`);
  if (!data.success || !data.records?.length) {
    el.innerHTML = '<div class="empty-state"><span>Sin registros de vitales.</span></div>'; return;
  }
  const headers = ['Fecha','Temp','SpO2','PAS','PAD','FC','FR','Peso','Altura','IMC'];
  const rows = data.records.map(r => {
    const c = r.constantes || {};
    return `<tr>
      <td>${fmtDate(r.created_at)}</td>
      <td>${c.temperatura ?? '—'}</td><td>${c.spo2 ?? '—'}</td>
      <td>${c.pas ?? '—'}</td><td>${c.pad ?? '—'}</td>
      <td>${c.fc ?? '—'}</td><td>${c.fr ?? '—'}</td>
      <td>${c.peso ?? '—'}</td><td>${c.altura ?? '—'}</td>
      <td>${c.imc ?? '—'}</td>
    </tr>`;
  }).join('');
  el.innerHTML = `<table class="vitals-history-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows}</tbody></table>`;
}

async function loadPatientMeds(id) {
  if (!id) return;
  const el = document.getElementById('patient-meds-content');
  el.innerHTML = '<div class="loading-state"><div class="spinner-ring"></div></div>';
  const data = await api('GET', `/api/documents/prescriptions?patient_id=${id}`);
  if (!data.success || !data.prescriptions?.length) {
    el.innerHTML = '<div class="empty-state"><span>Sin recetas registradas.</span></div>'; return;
  }
  el.innerHTML = data.prescriptions.map(rx => `
    <div class="doc-item">
      <div class="doc-info">
        <div class="doc-name">${escHtml(rx.medication)} — ${escHtml(rx.dosage)}</div>
        <div class="doc-meta">${escHtml(rx.frequency)} &bull; ${rx.days} días &bull; ${fmtDate(rx.created_at)}</div>
      </div>
    </div>
  `).join('');
}

async function loadPatientAlerts(id) {
  if (!id) return;
  const el = document.getElementById('patient-alerts-content');
  el.innerHTML = '<div class="loading-state"><div class="spinner-ring"></div></div>';
  const data = await api('GET', `/api/history?patient_id=${id}&alert=rojo`);
  if (!data.success || !data.records?.length) {
    el.innerHTML = '<div class="empty-state"><span>Sin alertas críticas registradas. ✅</span></div>'; return;
  }
  el.innerHTML = data.records.map(r => `
    <div class="doc-item" style="border-color:rgba(239,68,68,0.3);">
      <div class="doc-info">
        <div class="doc-name" style="color:#f87171;">&#x26A0;&#xFE0F; ${escHtml(r.final_diagnosis || r.phase1_diagnosis || '—')}</div>
        <div class="doc-meta">${fmtDate(r.created_at)}</div>
      </div>
    </div>
  `).join('');
}

async function loadPatientDocs(id) {
  if (!id) return;
  const el = document.getElementById('patient-docs-content');
  el.innerHTML = '<div class="loading-state"><div class="spinner-ring"></div></div>';
  const data = await api('GET', `/api/documents?patient_id=${id}`);
  if (!data.success) { el.innerHTML = '<div class="empty-state"><span>No disponible.</span></div>'; return; }
  const docs = data.documents || [];
  if (!docs.length) { el.innerHTML = '<div class="empty-state"><span>No hay documentos subidos aún.</span></div>'; return; }
  el.innerHTML = docs.map(d => `
    <div class="doc-item">
      <div class="doc-info">
        <div class="doc-name">${escHtml(d.original_name)}</div>
        <div class="doc-meta">${d.file_type} &bull; ${(d.file_size/1024).toFixed(1)}KB &bull; ${fmtDate(d.uploaded_at)}</div>
      </div>
      <div class="doc-actions">
        <a href="/api/documents/${d.id}/download" class="btn-icon" title="Descargar" target="_blank">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        </a>
        <button class="btn-icon danger" title="Eliminar" onclick="deleteDocument(${d.id}, ${id})">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
        </button>
      </div>
    </div>
  `).join('');
}

async function uploadDocument(event) {
  const file = event.target.files[0];
  if (!file || !STATE.viewingPatientId) return;
  const formData = new FormData();
  formData.append('file', file);
  formData.append('patient_id', STATE.viewingPatientId);

  toast('info', 'Subiendo archivo...');
  try {
    const res = await fetch('/api/documents/upload', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.success) { toast('success', 'Archivo subido correctamente.'); loadPatientDocs(STATE.viewingPatientId); }
    else { toast('error', data.error || 'Error al subir el archivo.'); }
  } catch (e) { toast('error', 'Error de conexión.'); }
  event.target.value = '';
}

async function deleteDocument(docId, patientId) {
  if (!confirm('¿Eliminar este documento?')) return;
  const res = await api('DELETE', `/api/documents/${docId}`);
  if (res.success) { toast('success', 'Documento eliminado.'); loadPatientDocs(patientId); }
  else { toast('error', res.error || 'Error al eliminar.'); }
}

// ── SALA DE ESPERA ────────────────────────────────────────────────────────────
async function loadWaitingRoom() {
  const el = document.getElementById('waiting-room-list');
  if (!el) return;
  el.innerHTML = '<div class="loading-state"><div class="spinner-ring"></div><span>Cargando...</span></div>';
  const data = await api('GET', '/api/appointments?today=1');
  if (!data.success) { el.innerHTML = '<div class="empty-state"><span>No se pudo cargar la sala de espera.</span></div>'; return; }
  
  let apps = data.appointments || [];
  // Ocultar de la sala de espera las citas que ya están completadas
  apps = apps.filter(a => a.status !== 'completada');
  
  if (!apps.length) { el.innerHTML = '<div class="empty-state"><span>Sin pacientes en espera para hoy.</span></div>'; return; }

  el.innerHTML = apps.map(a => {
    const isArrived = a.confirmed || a.status === 'en_curso' || a.status === 'completada';
    const time = a.appointment_time ? a.appointment_time.substring(0,5) : '—';
    return `
    <div class="waiting-row ${isArrived ? 'arrived' : ''}" id="wr-${a.id}">
      <span class="wr-time">${time}</span>
      <div class="wr-patient">
        <div class="wr-patient-name">
          ${escHtml(a.patient_name || '—')}
          ${a.parent_appointment_id ? '<span class="badge badge-amarillo" style="font-size:10px; margin-left:8px;">Seguimiento</span>' : ''}
        </div>
        <div class="wr-patient-cedula">${escHtml(a.patient_cedula || '')} &bull; Dr. ${escHtml(a.doctor_fullname || '-')}</div>
      </div>
      <span class="badge ${a.status === 'completada' ? 'badge-verde' : a.status === 'en_curso' ? 'badge-amarillo' : 'badge-rojo'}"
            style="font-size:10px;">${a.status || 'abierta'}</span>
      <div class="wr-actions">
        ${!isArrived ? `<button class="btn-primary" style="font-size:12px;padding:6px 14px;" onclick="confirmArrival(${a.id}, ${a.doctor_id}, '${escHtml(a.patient_name)}')">Marcar Llegada</button>` : '<span style="color:var(--green);font-size:13px;">&#10003; Llegó</span>'}
      </div>
    </div>`;
  }).join('');
}

async function confirmArrival(appointmentId, doctorId, patientName) {
  const res = await api('PUT', `/api/appointments/${appointmentId}`, { status: 'en_curso', confirmed: true });
  if (res.success) { 
    toast('success', 'Llegada confirmada.'); 
    loadWaitingRoom(); 
    
    // Auto-enviar notificación al doctor si hay doctor y nombre
    if (doctorId && patientName) {
      const msg = `🔔 El paciente ${patientName} ha llegado a su cita y está en la Sala de Espera.`;
      api('POST', '/api/notifications/send', { to_user_id: doctorId, message: msg });
    }
  }
  else { toast('error', res.error || 'No se pudo confirmar.'); }
}

// ── AJUSTES DEL CONSULTORIO ──────────────────────────────────────────────────
async function loadClinicSettings() {
  const data = await api('GET', '/api/settings/all');
  if (!data.success) return;
  const s = data.settings || {};
  const fields = {
    'cfg-clinic-name':    'clinic_name',
    'cfg-clinic-address': 'clinic_address',
    'cfg-clinic-phone':   'clinic_phone',
    'cfg-clinic-rnc':     'clinic_rnc',
    'cfg-clinic-email':   'clinic_email',
    'cfg-clinic-hours':   'clinic_hours',
  };
  Object.entries(fields).forEach(([elId, key]) => {
    const el = document.getElementById(elId);
    if (el) el.value = s[key] || '';
  });
}

async function saveClinicSettings() {
  const fields = {
    'cfg-clinic-name':    'clinic_name',
    'cfg-clinic-address': 'clinic_address',
    'cfg-clinic-phone':   'clinic_phone',
    'cfg-clinic-rnc':     'clinic_rnc',
    'cfg-clinic-email':   'clinic_email',
    'cfg-clinic-hours':   'clinic_hours',
  };
  const payload = {};
  Object.entries(fields).forEach(([elId, key]) => {
    const el = document.getElementById(elId);
    if (el) payload[key] = el.value.trim();
  });

  const res = await api('POST', '/api/settings/update', payload);
  if (res.success) {
    toast('success', 'Ajustes guardados correctamente.');
    loadClinicName(); // Actualizar nombre en sidebar
  } else {
    toast('error', res.error || 'Error al guardar ajustes.');
  }
}

// ── NOTIFICACIONES / CHAT INTERNO ────────────────────────────────────────────
async function loadNotifUserList() {
  const data = await api('GET', '/api/notifications/contacts');
  if (!data.success) return;
  const sel = document.getElementById('notif-to-user');
  if (!sel) return;
  
  let others = data.contacts || [];
  
  if (STATE.user?.role === 'doctor') {
    // El doctor solo chatea con la secretaria
    others = others.filter(u => u.role === 'secretaria');
    if (others.length > 0) {
      sel.innerHTML = `<option value="${others[0].id}">${escHtml(others[0].full_name || others[0].username)} (Secretaria)</option>`;
    } else {
      sel.innerHTML = `<option value="">Sin secretaria disponible</option>`;
    }
    sel.style.display = 'none'; // Ocultar el select para el doctor
  } else {
    // La secretaria o admin ven a los doctores
    if (STATE.user?.role === 'secretaria') {
       others = others.filter(u => u.role === 'doctor');
    }
    sel.innerHTML = `<option value="">Seleccione chat...</option>` +
      others.map(u => `<option value="${u.id}">Dr. ${escHtml(u.full_name || u.username)}</option>`).join('');
    sel.style.display = 'block';
    sel.onchange = loadNotifMessages; // Al cambiar, recargar mensajes de ese chat
  }
}

async function loadUnreadCount() {
  const data = await api('GET', '/api/notifications/unread_count');
  const el   = document.getElementById('notif-count');
  if (!el) return;
  const count = data.count || 0;
  el.textContent = count > 99 ? '99+' : count;
  el.style.display = count > 0 ? 'flex' : 'none';
}

async function openNotificationsPanel() {
  document.getElementById('notif-panel-overlay').style.display = 'block';
  document.getElementById('notif-panel').style.display = 'flex';
  if (!document.getElementById('notif-to-user').options.length) {
    await loadNotifUserList();
  }
  await loadNotifMessages();
  // Marcar como leidas
  api('POST', '/api/notifications/mark_read').then(() => {
    loadUnreadCount();
  });
}

function closeNotificationsPanel() {
  document.getElementById('notif-panel-overlay').style.display = 'none';
  document.getElementById('notif-panel').style.display = 'none';
}

async function loadNotifMessages(silent = false) {
  const el = document.getElementById('notif-messages-list');
  if (!silent) {
    el.innerHTML = '<div class="loading-state"><div class="spinner-ring"></div></div>';
  }
  
  const data = await api('GET', '/api/notifications');
  if (!data.success) return;
  
  let notifications = data.notifications || [];
  const sel = document.getElementById('notif-to-user');
  
  // Filtrar notificaciones según el contacto seleccionado si no somos doctor
  if (STATE.user?.role !== 'doctor') {
    if (sel && sel.value) {
      const selectedId = parseInt(sel.value, 10);
      notifications = notifications.filter(n => n.from_user_id === selectedId || n.to_user_id === selectedId);
    } else {
      if (!silent) el.innerHTML = '<div class="empty-state" style="padding:24px;"><span>Seleccione un chat para ver los mensajes.</span></div>';
      return;
    }
  }

  if (!notifications.length) {
    if (!silent) el.innerHTML = '<div class="empty-state" style="padding:24px;"><span>No hay mensajes aún en este chat.</span></div>';
    return;
  }
  
  const myId = STATE.user?.id;
  // Ordenar por fecha ascendente para mostrar los más viejos arriba y los nuevos abajo
  notifications.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  
  const newHTML = notifications.map(n => {
    const sent = n.from_user_id === myId;
    return `
    <div class="notif-message ${sent ? 'sent' : 'received'}">
      <div>${escHtml(n.message)}</div>
      <div class="notif-meta">${sent ? 'Tú' : escHtml(n.from_name || 'Sistema')} • ${fmtDate(n.created_at)}</div>
    </div>`;
  }).join('');
  
  // Si estamos en modo silencioso y no hay cambios en el HTML, no re-renderizar para no perder el foco
  if (silent && el.innerHTML === newHTML) return;
  
  el.innerHTML = newHTML;
  
  // Scroll abajo
  setTimeout(() => {
    el.scrollTop = el.scrollHeight;
  }, 100);
}

async function sendNotification() {
  const toUser = document.getElementById('notif-to-user')?.value;
  const msg    = document.getElementById('notif-message-input')?.value.trim();
  
  if (!msg) { toast('warning', 'Escribe un mensaje.'); return; }
  if (!toUser) { toast('warning', 'Selecciona un chat primero.'); return; }

  const res = await api('POST', '/api/notifications/send', { to_user_id: toUser, message: msg });
  if (res.success) {
    document.getElementById('notif-message-input').value = '';
    await loadNotifMessages();
    loadUnreadCount();
    toast('success', 'Mensaje enviado.');
  } else {
    toast('error', res.error || 'Error al enviar.');
  }
}

async function markAllNotificationsRead() {
  await api('POST', '/api/notifications/mark_read');
  loadUnreadCount();
  loadNotifMessages();
}

// Polling de notificaciones (burbuja y chat en vivo) cada 5 segundos
setInterval(() => {
  if (STATE.user) {
    loadUnreadCount();
    const panel = document.getElementById('notif-panel-overlay');
    if (panel && panel.style.display === 'block') {
      loadNotifMessages(true);
    }
  }
}, 5000);

// ── PDF DOWNLOADS ────────────────────────────────────────────────────────────
async function downloadPrescriptionPDF() {
  const visitId = STATE.currentVisitId;
  if (!visitId) { toast('warning', 'No hay una visita activa.'); return; }
  window.open(`/api/pdf/prescription/${visitId}`, '_blank');
}

async function downloadLabOrderPDF() {
  const visitId = STATE.currentVisitId;
  if (!visitId) { toast('warning', 'No hay una visita activa.'); return; }
  window.open(`/api/pdf/lab_order/${visitId}`, '_blank');
}

async function downloadDailySchedulePDF() {
  const today = new Date().toISOString().split('T')[0];
  window.open(`/api/pdf/agenda?date=${today}`, '_blank');
}

// Mostrar botones PDF en modal de diagnóstico cuando hay visita activa
function showPdfButtons() {
  document.getElementById('btn-pdf-prescription')?.style && (document.getElementById('btn-pdf-prescription').style.display = 'inline-flex');
  document.getElementById('btn-pdf-lab')?.style && (document.getElementById('btn-pdf-lab').style.display = 'inline-flex');
}

// Hook en el final de fase 2 (cuando se guarda un diagnóstico)
// Se llama desde el JS existente de runPhase2
const _origSwitchTab = switchTab;
window.switchTab = function(tab) {
  _origSwitchTab(tab);
  // Lazy-load por pestaña
  if (tab === 'waiting-room')   loadWaitingRoom();
  if (tab === 'admin-settings') loadClinicSettings();
  if (tab === 'admin-dashboard') loadAdminDashboard();
};

async function autoFillCedula(cedula) {
  const ced = cedula.replace(/-/g, '').trim();
  if (ced.length !== 11 || isNaN(ced)) return;

  toast('info', 'Consultando cédula...');
  try {
    const res = await fetch(`/api/patients/consulta-cedula/${ced}`);
    const data = await res.json();
    
    if (data.success && data.data) {
      const p = data.data;
      const nameField = document.getElementById('pt-name');
      if (nameField && !nameField.value) {
        nameField.value = p.nombre || '';
      }
      
      const dobField = document.getElementById('pt-dob');
      if (dobField && p.fechaNacimiento) {
        dobField.value = p.fechaNacimiento.substring(0, 10);
      }
      
      const genderField = document.getElementById('pt-gender');
      if (genderField && p.sexo) {
        const s = p.sexo.toUpperCase();
        if (s.startsWith('M')) {
          genderField.value = 'Masculino';
        } else if (s.startsWith('F')) {
          genderField.value = 'Femenino';
        } else {
          genderField.value = 'Otro';
        }
      }
      
      const photoUrlField = document.getElementById('pt-photo-url');
      const photoPreview = document.getElementById('pt-photo-preview');
      const photoPlaceholder = document.getElementById('pt-photo-placeholder');
      
      if (p.foto) {
        if (photoUrlField) photoUrlField.value = p.foto;
        if (photoPreview && photoPlaceholder) {
          photoPreview.src = p.foto;
          photoPreview.style.display = 'block';
          photoPlaceholder.style.display = 'none';
        }
      }
      
      toast('success', 'Datos obtenidos de la JCE');
    } else if (data.error) {
      toast('warning', data.error);
    }
  } catch (err) {
    console.error(err);
    toast('error', 'Error al consultar cédula.');
  }
}


// ── SISTEMA DE PERFILES Y SUSCRIPCIONES (NUEVOS EN GENERAL) ──────────────────
async function openMyAccountModal() {
  const data = await api('GET', '/api/profile');
  if (!data.success) {
    toast('error', 'No se pudo cargar la información del perfil.');
    return;
  }
  
  const user = data.user;
  STATE.user = user; // Actualizar estado local

  // Cargar campos básicos
  document.getElementById('my-username').value = user.username || '';
  document.getElementById('my-role').value = user.role || '';
  document.getElementById('my-fullname').value = user.full_name || '';
  document.getElementById('my-email').value = user.email || '';
  document.getElementById('my-password').value = '';

  // Foto de perfil preview
  const preview = document.getElementById('my-profile-preview');
  const placeholder = document.getElementById('my-profile-placeholder');
  if (user.photo_url) {
    preview.src = user.photo_url;
    preview.style.display = 'block';
    placeholder.style.display = 'none';
  } else {
    preview.style.display = 'none';
    placeholder.style.display = 'block';
    placeholder.textContent = (user.full_name || user.username || '?')[0].toUpperCase();
  }

  // Si es doctor, mostrar campos adicionales y sección de suscripción
  const isDoctor = user.role === 'doctor';
  document.getElementById('my-doctor-fields').style.display = isDoctor ? 'block' : 'none';
  document.getElementById('my-subscription-section').style.display = isDoctor ? 'block' : 'none';

  if (isDoctor) {
    document.getElementById('my-matricula').value = user.matricula || '';
    document.getElementById('my-especialidad').value = user.especialidad || '';
    document.getElementById('my-telefono').value = user.telefono || '';
    document.getElementById('my-hospital').value = user.hospital || '';
    document.getElementById('my-cedula').value = user.cedula || '';
    document.getElementById('my-photourl').value = user.photo_url || '';

    // Estado suscripción
    const badge = document.getElementById('sub-status-badge');
    const details = document.getElementById('sub-details');
    const actions = document.getElementById('sub-actions');

    if (user.subscription_active) {
      const isCancelled = user.subscription_plan === 'VIP (Cancelada)';
      badge.className = isCancelled ? 'badge badge-amarillo' : 'badge badge-verde';
      badge.textContent = isCancelled ? 'VIP (CANCELADO)' : 'VIP ACTIVO';
      details.style.display = 'block';
      document.getElementById('sub-plan-name').textContent = user.subscription_plan || 'VIP';
      document.getElementById('sub-renewal-date').textContent = user.subscription_expires_at ? user.subscription_expires_at.substring(0, 10) : '—';
      document.getElementById('sub-id-display').textContent = user.subscription_id || '—';

      if (isCancelled) {
        actions.innerHTML = `
          <div style="text-align: center; color: var(--text-muted); font-size: 13px; padding: 10px; border: 1px dashed var(--border); border-radius: 6px; width: 100%;">
            Suscripción cancelada. Activa hasta el ${user.subscription_expires_at ? user.subscription_expires_at.substring(0, 10) : '—'}.
          </div>
        `;
      } else {
        actions.innerHTML = `
          <button class="btn-outline" style="border-color: #ef4444; color: #ef4444; width: 100%;" onclick="cancelSubscription()">
            Cancelar Suscripción VIP
          </button>
        `;
      }
    } else {
      badge.className = 'badge badge-rojo';
      badge.textContent = 'INACTIVO';
      details.style.display = 'none';

      actions.innerHTML = `
        <div id="paypal-button-container" style="width: 100%;"></div>
        <button class="btn-primary" style="background-color: var(--brand-light); border-color: var(--brand-light); width: 100%; font-size: 13px;" onclick="simulatePayPalPayment()">
          ⚡ Simular Pago Directo (Pruebas)
        </button>
      `;

      // Renderizar el botón de PayPal de manera diferida
      setTimeout(() => {
        renderPayPalButton();
      }, 100);
    }
  }

  openModal('modal-profile');
}

let paypalSdkLoaded = false;

async function loadPayPalSdk(clientId) {
  if (paypalSdkLoaded || window.paypal) {
    return Promise.resolve();
  }
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = `https://www.paypal.com/sdk/js?client-id=${clientId}&vault=true&intent=subscription`;
    script.type = 'text/javascript';
    script.async = true;
    script.onload = () => {
      paypalSdkLoaded = true;
      resolve();
    };
    script.onerror = (err) => {
      reject(new Error('No se pudo cargar el SDK de PayPal.'));
    };
    document.head.appendChild(script);
  });
}

async function renderPayPalButton() {
  const container = document.getElementById('paypal-button-container');
  if (!container) return;
  container.innerHTML = '<div style="color:var(--text-muted);font-size:12px;text-align:center;">Cargando pasarela de PayPal...</div>';

  try {
    const configRes = await fetch('/api/config/paypal');
    const config = await configRes.json();
    if (!config.success) {
      container.innerHTML = '<div style="color:var(--text-muted);font-size:12px;text-align:center;">Error al cargar config de PayPal</div>';
      return;
    }

    const { client_id, plan_id } = config;

    await loadPayPalSdk(client_id);

    container.innerHTML = ''; // Limpiar mensaje de carga

    if (typeof paypal === 'undefined') {
      container.innerHTML = '<div style="color:var(--text-muted);font-size:12px;text-align:center;">SDK de PayPal no disponible</div>';
      return;
    }

    paypal.Buttons({
      style: {
        shape: 'rect',
        color: 'gold',
        layout: 'vertical',
        label: 'subscribe'
      },
      createSubscription: function(data, actions) {
        return actions.subscription.create({
          'plan_id': plan_id
        });
      },
      onApprove: async function(data, actions) {
        toast('info', 'Procesando aprobación de PayPal...');
        const res = await api('POST', '/api/subscription/paypal-approved', {
          subscription_id: data.subscriptionID,
          plan_id: 'VIP'
        });
        if (res.success) {
          toast('success', '¡Suscripción VIP de PayPal activada!');
          STATE.user = res.user;
          setupUI();
          closeModal('modal-profile');
        } else {
          toast('error', res.error || 'Error al guardar suscripción.');
        }
      },
      onError: function(err) {
        console.error(err);
        toast('error', 'Ocurrió un error con la pasarela de PayPal.');
      }
    }).render('#paypal-button-container');

  } catch (err) {
    console.error(err);
    container.innerHTML = `<div style="color:var(--text-muted);font-size:12px;text-align:center;">${err.message || 'Error al conectar con PayPal'}</div>`;
  }
}

async function simulatePayPalPayment() {
  if (!confirm('¿Desea simular una suscripción VIP exitosa de $20 USD para desarrollo?')) return;
  const mockSubId = 'SIM-SUB-' + Math.floor(Math.random() * 10000000);
  
  toast('info', 'Procesando pago simulado...');
  const res = await api('POST', '/api/subscription/paypal-approved', {
    subscription_id: mockSubId,
    plan_id: 'VIP (Simulado)'
  });
  
  if (res.success) {
    toast('success', '¡Suscripción VIP Simulada activada correctamente!');
    STATE.user = res.user;
    setupUI();
    closeModal('modal-profile');
  } else {
    toast('error', res.error || 'Error al activar suscripción simulada.');
  }
}

async function cancelSubscription() {
  if (!confirm('¿Está seguro de que desea cancelar su suscripción VIP? Mantendrá su acceso VIP hasta la fecha de vencimiento de su periodo facturado actual.')) return;
  
  toast('info', 'Procesando cancelación...');
  const res = await api('POST', '/api/subscription/cancel');
  if (res.success) {
    toast('success', res.message || 'Suscripción VIP cancelada correctamente.');
    STATE.user = res.user;
    setupUI();
    closeModal('modal-profile');
  } else {
    toast('error', res.error || 'Error al cancelar la suscripción.');
  }
}

async function uploadProfilePhoto(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('photo', file);

  toast('info', 'Subiendo foto de perfil...');
  try {
    const res = await fetch('/api/profile/upload-photo', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (data.success && data.photo_url) {
      toast('success', 'Foto de perfil actualizada.');
      document.getElementById('my-profile-preview').src = data.photo_url;
      document.getElementById('my-profile-preview').style.display = 'block';
      document.getElementById('my-profile-placeholder').style.display = 'none';
      
      STATE.user.photo_url = data.photo_url;
      setupUI();
    } else {
      toast('error', data.error || 'Error al subir la foto.');
    }
  } catch(e) {
    toast('error', 'Error de red al subir foto.');
  }
}

async function saveMyProfile() {
  const fullname = document.getElementById('my-fullname').value.trim();
  const email = document.getElementById('my-email').value.trim();
  const password = document.getElementById('my-password').value;

  const payload = {
    full_name: fullname || null,
    email: email || null,
    password: password || null
  };

  if (STATE.user.role === 'doctor') {
    payload.matricula = document.getElementById('my-matricula').value.trim() || null;
    payload.especialidad = document.getElementById('my-especialidad').value.trim() || null;
    payload.telefono = document.getElementById('my-telefono').value.trim() || null;
    payload.hospital = document.getElementById('my-hospital').value.trim() || null;
    payload.cedula = document.getElementById('my-cedula').value.trim() || null;
    payload.photo_url = document.getElementById('my-photourl').value.trim() || null;
  }

  toast('info', 'Guardando cambios del perfil...');
  const res = await api('PUT', '/api/profile', payload);
  if (res.success) {
    toast('success', '¡Perfil actualizado con éxito!');
    STATE.user = res.user;
    setupUI();
    closeModal('modal-profile');
  } else {
    toast('error', res.error || 'Error al guardar perfil.');
  }
}

async function sendTestEmail() {
  toast('info', 'Enviando correo de prueba...');
  const res = await api('POST', '/api/subscription/send-test-email');
  if (res.success) {
    toast('success', res.message || 'Correo de prueba enviado.');
  } else {
    toast('error', res.error || 'Error al enviar correo.');
  }
}

async function saveManualDiagnosis(createPrescription) {
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

  const diagnosis = document.getElementById('manual-diag-primary').value.trim();
  if (!diagnosis) {
    toast('error', 'El diagnóstico clínico manual es obligatorio.');
    return;
  }

  const alertLevel = document.getElementById('manual-diag-alert').value;
  const specialist = document.getElementById('manual-diag-specialist').value.trim();
  const report = document.getElementById('manual-diag-report').value.trim();

  // Crear la visita si no se ha creado aún
  if (!STATE.currentVisitId) {
    const constantes = getConstantes();
    const sintomas = getCheckedFrom('symptoms-checkboxes');
    const appIdRaw = document.getElementById('diag-appointment-id')?.value;
    const appointmentId = appIdRaw ? parseInt(appIdRaw) : null;
    
    toast('info', 'Registrando visita médica...');
    const visitRes = await api('POST', '/api/visits', {
      patient_id: patientId,
      visit_type: 'consulta',
      motivo_consulta: motivoConsulta,
      doctor_notes: document.getElementById('diag-doctor-notes')?.value.trim() || null,
      constantes: constantes,
      sintomas: sintomas,
      appointment_id: appointmentId
    });
    if (!visitRes.success) {
      toast('error', visitRes.error || 'Error al crear la visita.');
      return;
    }
    STATE.currentVisitId = visitRes.visit_id;
  }

  // Guardar diagnóstico manual
  toast('info', 'Guardando diagnóstico...');
  const res = await api('POST', '/api/diagnose/final', {
    patient_id: STATE.currentPatient.id,
    patient_name: STATE.currentPatient.name,
    motivo_consulta: motivoConsulta,
    visit_id: STATE.currentVisitId,
    preliminar_probs: {},
    tests_resultados: [],
    sintomas: getCheckedFrom('symptoms-checkboxes'),
    antecedentes: getCheckedFrom('antecedentes-checkboxes'),
    constantes: getConstantes(),
    is_manual: true,
    save_diagnosis: true,
    diagnosis_primary: diagnosis,
    alert_level: alertLevel,
    specialist: specialist || 'Medicina General',
    explanation: report || 'Diagnóstico y evolución ingresados manualmente.'
  });

  if (res.success) {
    toast('success', 'Consulta y diagnóstico registrados con éxito.');
    
    const appId = document.getElementById('diag-appointment-id')?.value;
    if (appId) {
      api('POST', `/api/appointments/${appId}/status`, { status: 'completada' });
    }

    if (createPrescription) {
      openPrescriptionModal(STATE.currentPatient.id, STATE.currentVisitId);
    } else {
      resetDiagnose();
    }
  } else {
    toast('error', res.error || 'Error al guardar el diagnóstico.');
  }
}


// ── COBROS Y FACTURACIÓN ELECTRÓNICA (e-CF) ──────────────────────────────────
async function loadBillingTab() {
  await loadBillingPending();
  await loadBillingHistory();
}

async function loadBillingPending() {
  const el = document.getElementById('billing-pending-list');
  if (!el) return;
  el.innerHTML = '<tr><td colspan="6" style="text-align:center;"><div class="spinner-ring" style="margin:10px auto;"></div></td></tr>';

  const res = await api('GET', '/api/billing/pending');
  if (!res.success || !res.pending?.length) {
    el.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 20px;">No hay consultas pendientes de cobro.</td></tr>';
    return;
  }

  el.innerHTML = res.pending.map(p => {
    // Formatear fecha corta
    const date = p.visit_date ? p.visit_date.substring(0, 16).replace('T', ' ') : '—';
    return `
      <tr>
        <td>${date}</td>
        <td style="font-weight:600; color:var(--text-primary);">${escHtml(p.patient_name)}</td>
        <td>${escHtml(p.patient_cedula || '—')}</td>
        <td>Dr. ${escHtml(p.doctor_fullname)}</td>
        <td style="color:var(--brand-light); font-weight:600;">RD$ 3,000.00</td>
        <td>
          <button class="btn-primary" style="font-size:12px; padding:6px 12px;" onclick="openChargeModal(${p.visit_id}, '${escHtml(p.patient_name)}')">
            💳 Cobrar
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

async function loadBillingHistory() {
  const el = document.getElementById('billing-history-list');
  if (!el) return;
  el.innerHTML = '<tr><td colspan="8" style="text-align:center;"><div class="spinner-ring" style="margin:10px auto;"></div></td></tr>';

  const res = await api('GET', '/api/billing/invoices');
  if (!res.success || !res.invoices?.length) {
    el.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">No hay facturas registradas.</td></tr>';
    return;
  }

  el.innerHTML = res.invoices.map(i => {
    const date = i.created_at ? i.created_at.substring(0, 16).replace('T', ' ') : '—';
    const client = i.patient_name || 'Médico (Suscripción)';
    const paymentMethodText = i.payment_method === 'tarjeta' ? '💳 Tarjeta' : '💵 Efectivo';
    
    // Links de acciones
    const dgiiLink = i.dgii_url 
      ? `<a href="${i.dgii_url}" target="_blank" class="btn-icon" title="Ver Timbre en DGII" style="color:var(--brand-light);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg></a>`
      : '—';

    return `
      <tr>
        <td>${date}</td>
        <td><span class="badge ${i.invoice_type === 'suscripcion' ? 'badge-verde' : 'badge-azul'}" style="font-size:10px;">${i.invoice_type.toUpperCase()}</span></td>
        <td style="font-weight:500;">${escHtml(client)}</td>
        <td>${paymentMethodText}</td>
        <td style="font-family:var(--mono); font-size:12px; color:var(--text-primary); font-weight:600;">${escHtml(i.encf || '—')}</td>
        <td><span class="badge badge-verde" style="font-size:10px;">${escHtml(i.estado)}</span></td>
        <td style="font-weight:600; color:var(--text-primary);">RD$ ${i.total.toLocaleString('es-DO', { minimumFractionDigits: 2 })}</td>
        <td>
          <div style="display:flex; gap:8px; align-items:center;">
            ${dgiiLink}
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function openChargeModal(visitId, patientName) {
  document.getElementById('charge-visit-id').value = visitId;
  document.getElementById('charge-patient-name').textContent = patientName;
  document.getElementById('charge-payment-method').value = 'efectivo';
  openModal('modal-charge-visit');
}

async function submitChargeVisit() {
  const visitId = document.getElementById('charge-visit-id').value;
  const paymentMethod = document.getElementById('charge-payment-method').value;

  if (!visitId) return;

  toast('info', 'Procesando pago y firmando e-CF con DGII...');
  const res = await api('POST', '/api/billing/charge', {
    visit_id: parseInt(visitId, 10),
    payment_method: paymentMethod
  });

  if (res.success) {
    toast('success', '¡Pago procesado y e-CF aceptado!');
    closeModal('modal-charge-visit');

    // Llenar datos de éxito
    document.getElementById('res-invoice-encf').textContent = res.invoice.encf || '—';
    document.getElementById('res-invoice-code').textContent = res.invoice.codigo_seguridad || '—';
    document.getElementById('res-invoice-status').textContent = res.invoice.estado || 'Aceptado';
    
    const linkEl = document.getElementById('res-invoice-dgii-link');
    if (res.invoice.dgii_url) {
      linkEl.href = res.invoice.dgii_url;
      linkEl.style.display = 'block';
    } else {
      linkEl.style.display = 'none';
    }

    openModal('modal-invoice-result');
    loadBillingTab();
  } else {
    toast('error', res.error || 'Error al procesar la factura electrónica.');
  }
}

async function lookupDoctorCedula(prefix) {
  const inputEl = document.getElementById(`${prefix}-cedula`);
  const cedula = inputEl ? inputEl.value.trim() : '';
  if (!cedula) {
    toast('warning', 'Ingresa una cédula para consultar.');
    return;
  }
  toast('info', 'Consultando cédula en JCE...');
  try {
    const data = await api('GET', `/api/patients/consulta-cedula/${cedula}`);
    if (data.success && data.data.found) {
      toast('success', 'Persona encontrada en la JCE.');
      const info = data.data;
      const nameEl = document.getElementById(`${prefix}-fullname`);
      if (nameEl) nameEl.value = info.nombre;
      
      const photoEl = document.getElementById(`${prefix}-photourl`);
      if (photoEl) photoEl.value = info.foto || '';
      
      // Update preview if it's the current user profile modal
      if (prefix === 'my' && info.foto) {
        const preview = document.getElementById('my-profile-preview');
        const placeholder = document.getElementById('my-profile-placeholder');
        if (preview && placeholder) {
          preview.src = info.foto;
          preview.style.display = 'block';
          placeholder.style.display = 'none';
        }
      }
    } else {
      toast('error', data.error || 'Cédula no encontrada en la JCE.');
    }
  } catch(e) {
    console.error(e);
    toast('error', 'Error al realizar la consulta.');
  }
}

function openSearchPatientAppointmentModal() {
  document.getElementById('search-patient-app-input').value = '';
  filterPatientAppList();
  openModal('modal-search-patient-app');
}

function openSearchDoctorAppointmentModal() {
  document.getElementById('search-doctor-app-input').value = '';
  filterDoctorAppList();
  openModal('modal-search-doctor-app');
}

function filterPatientAppList() {
  const query = document.getElementById('search-patient-app-input').value.toLowerCase();
  const listEl = document.getElementById('patient-app-list');
  if (!listEl) return;
  if (!STATE.allPatients || STATE.allPatients.length === 0) {
    listEl.innerHTML = '<p style="text-align:center; padding:10px; color:var(--text-muted);">No hay pacientes cargados. Cargando...</p>';
    api('GET', '/api/patients').then(pts => {
      if (pts.success) {
        STATE.allPatients = pts.patients;
        filterPatientAppList();
      }
    });
    return;
  }

  const filtered = STATE.allPatients.filter(p => 
    p.name.toLowerCase().includes(query) || (p.cedula && p.cedula.includes(query))
  );

  listEl.innerHTML = filtered.map(p => `
    <div class="patient-picker-item" onclick="selectPatientForAppointment(${p.id}, '${p.name.replace(/'/g, "\\'")}')">
      <div>
        <div class="picker-name">${p.name}</div>
        <div class="picker-cedula">Cédula: ${p.cedula || '—'}</div>
      </div>
      <div class="picker-btn">Seleccionar</div>
    </div>
  `).join('');
}

function filterDoctorAppList() {
  const query = document.getElementById('search-doctor-app-input').value.toLowerCase();
  const listEl = document.getElementById('doctor-app-list');
  if (!listEl) return;
  if (!STATE.allDoctors || STATE.allDoctors.length === 0) {
    listEl.innerHTML = '<p style="text-align:center; padding:10px; color:var(--text-muted);">No hay doctores cargados. Cargando...</p>';
    api('GET', '/api/users').then(data => {
      if (data.success) {
        STATE.allDoctors = data.users.filter(u => u.role === 'doctor');
        filterDoctorAppList();
      }
    });
    return;
  }

  const filtered = STATE.allDoctors.filter(d => 
    (d.full_name || d.username).toLowerCase().includes(query) || (d.especialidad && d.especialidad.toLowerCase().includes(query))
  );

  listEl.innerHTML = filtered.map(d => `
    <div class="patient-picker-item" onclick="selectDoctorForAppointment(${d.id}, '${(d.full_name || d.username).replace(/'/g, "\\'")}')">
      <div>
        <div class="picker-name">${d.full_name || d.username}</div>
        <div class="picker-cedula">${d.especialidad || 'Sin especialidad'} - Matrícula: ${d.matricula || '—'}</div>
      </div>
      <div class="picker-btn">Seleccionar</div>
    </div>
  `).join('');
}

function selectPatientForAppointment(id, name) {
  document.getElementById('app-patient').value = id;
  document.getElementById('app-patient-name').value = name;
  closeModal('modal-search-patient-app');
  // Trigger followup check
  loadPatientFollowupAppointments();
}

function selectDoctorForAppointment(id, name) {
  document.getElementById('app-doctor').value = id;
  document.getElementById('app-doctor-name').value = name;
  closeModal('modal-search-doctor-app');
}


