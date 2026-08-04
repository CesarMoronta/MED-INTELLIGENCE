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
  "Tos Seca Irritativa", "Tos Productiva / con Flema", "Tos Ferina / Accesos",
  "Dificultad Respiratoria (Disnea)", "Tos con Sangre (Hemoptisis)",
  "Dolor en el Pecho", "Palpitaciones", "Edema (Hinchazón)",
  "Dolor de Cabeza Severo", "Confusión / Convulsiones", "Pérdida de Fuerza/Sensibilidad Unilateral",
  "Dificultad para Hablar/Entender", "Mareos / Vértigo",
  "Fiebre Alta", "Febrícula", "Fatiga / Cansancio Extremo", "Dolor de Cuerpo Generalizado",
  "Pérdida del Olfato o Gusto", "Erupciones Cutáneas (Rash)",
  "Náuseas / Vómitos", "Diarrea Acuosa Profusa", "Diarrea Disentérica (con Sangre/Moco)",
  "Dolor Abdominal Cólico", "Dolor Abdominal Sordo / Difuso", "Dispepsia / Ardor Epigástrico",
  "Dolor de Garganta", "Dolor de Oído / Cara", "Otalgia (Dolor de oído)", "Odor Fétido / Secreción Ótica",
  "Disuria (Ardor al orinar)", "Polaquiuria (Orinar muy seguido)", "Dolor Lumbar / Suprapúbico",
  "Pirosis (Acidez estomacal)", "Regurgitación Ácida", "Congestión Nasal / Estornudos", "Rinorrea (Moqueo)",
  "Artralgias Severas", "Mialgias Intensas", "Dolor Retroocular", "Lesiones Vesiculares Cutáneas", "Prurito Generalizado"
];

const ALL_ANTECEDENTES = [
  "Asma", "EPOC", "Cardiopatía", "Hipertensión Arterial (HTA)", "Diabetes",
  "Diabetes Mellitus", "Inmunosupresión", "Tabaquismo", "Meningitis", "Cáncer",
  "HIV / SIDA", "Obesidad", "Fibrilación Auricular", "ACV / Derrame Previo",
  "Insuficiencia Renal Crónica", "Viaje Reciente a Zona Endémica",
  "Consumo de Alimentos en la Calle / Agua No Tratada", "Uso Reciente de Antibióticos",
  "Contacto con Casos Similares", "Antecedente de Litiasis Renal"
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

  const refPanel = document.getElementById('refinement-panel');
  if (refPanel) refPanel.style.display = 'none';
}

// API helper
// Extracted api to utils.js

// Toast
// Extracted toast to utils.js

// Button loading helper
// Extracted setButtonLoading to utils.js

// Modal helpers
// Extracted openModal to utils.js
// Extracted closeModal to utils.js
// Extracted closeModalOnBg to utils.js

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
    'reports':       loadReportsTab,
    'admin-schedules': loadAdminSchedulesTab,
    'doctor-schedules': loadDoctorSchedulesTab,
  };
  if (loaders[tab]) loaders[tab]();
}

const SIDEBAR_ITEMS = {
  'dashboard': { label: 'Dashboard', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>' },
  'appointments': { label: 'Agenda / Citas', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>' },
  'waiting-room': { label: 'Sala de Espera', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
  'patients': { label: 'Pacientes', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
  'diagnose': { label: 'Consulta Clínica', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4.5 10c1.7 0 3-1.3 3-3s-1.3-3-3-3-3 1.3-3 3 1.3 3 3 3z"/><path d="M22 20l-6-6"/><path d="M19.5 10c1.7 0 3-1.3 3-3s-1.3-3-3-3-3 1.3-3 3 1.3 3 3 3z"/><path d="M10 20v-4"/><circle cx="10" cy="20" r="2"/><path d="M7.5 7.5h6"/></svg>' },
  'history': { label: 'Historial Clínico', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v18H3zM3 9h18M9 21V9"/></svg>' },
  'simulator': { label: 'Simulador Bayes', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' },
  'billing': { label: 'Cobros y Facturación', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><line x1="12" y1="10" x2="12" y2="18"/><line x1="8" y1="14" x2="16" y2="14"/></svg>' },
  'admin-dashboard': { label: 'Dashboard Global', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>' },
  'admin-doctors': { label: 'Gestión de Doctores', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
  'admin-patients': { label: 'Gestión de Pacientes', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  'admin-history': { label: 'Historial Clínico', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v18H3zM3 9h18M9 21V9"/></svg>' },
  'admin-bayes': { label: 'Config. Bayesiana', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' },
  'admin-users': { label: 'Usuarios y Admins', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M16 16v2M8 16v2M4 20a8 8 0 0 1 16 0"/></svg>' },
  'admin-settings': { label: 'Ajustes Consultorio', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>' },
  'admin-audit': { label: 'Logs de Auditoría', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>' },
  'reports': { label: 'Consultas y Reportes', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>' },
  'admin-schedules': { label: 'Horarios Consultorio', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' },
  'doctor-schedules': { label: 'Mi Disponibilidad', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' }
};

function applyPrimaryColor(hex) {
  if (!hex || !/^#[0-9A-F]{6}$/i.test(hex)) return;
  const root = document.documentElement;

  // Parse hex to RGB
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);

  // Compute dark shade (80%)
  const rDark = Math.max(0, Math.floor(r * 0.8));
  const gDark = Math.max(0, Math.floor(g * 0.8));
  const bDark = Math.max(0, Math.floor(b * 0.8));
  const hexDark = '#' + ((1 << 24) + (rDark << 16) + (gDark << 8) + bDark).toString(16).slice(1);

  // Compute light shade (120%)
  const rLight = Math.min(255, Math.floor(r + (255 - r) * 0.2));
  const gLight = Math.min(255, Math.floor(g + (255 - g) * 0.2));
  const bLight = Math.min(255, Math.floor(b + (255 - b) * 0.2));
  const hexLight = '#' + ((1 << 24) + (rLight << 16) + (gLight << 8) + bLight).toString(16).slice(1);

  // Compute focus ring shade (110%)
  const rFocus = Math.min(255, Math.floor(r + (255 - r) * 0.1));
  const gFocus = Math.min(255, Math.floor(g + (255 - g) * 0.1));
  const bFocus = Math.min(255, Math.floor(b + (255 - b) * 0.1));
  const hexFocus = '#' + ((1 << 24) + (rFocus << 16) + (gFocus << 8) + bFocus).toString(16).slice(1);

  // Apply base brand variables
  root.style.setProperty('--brand', hex);
  root.style.setProperty('--brand-dark', hexDark);
  root.style.setProperty('--brand-light', hexLight);
  root.style.setProperty('--border-focus', hexFocus);
  root.style.setProperty('--shadow-glow', `0 0 40px rgba(${r}, ${g}, ${b}, 0.10)`);

  // Apply RGBA-based nav & logo variables (both modes share same base, opacity differs)
  const isDark = root.classList.contains('dark');
  root.style.setProperty('--bg-nav-active', `rgba(${r}, ${g}, ${b}, ${isDark ? '0.14' : '0.10'})`);
  root.style.setProperty('--color-nav-active', isDark ? hexLight : hex);
  root.style.setProperty('--bg-logo', `rgba(${r}, ${g}, ${b}, ${isDark ? '0.10' : '0.08'})`);
  root.style.setProperty('--border-logo', `rgba(${r}, ${g}, ${b}, ${isDark ? '0.28' : '0.25'})`);
  root.style.setProperty('--color-logo-tag', isDark ? hexLight : hex);

  // Apply icon stroke variable used by buttons and nav icons
  root.style.setProperty('--brand-icon', hexLight);

  // FullCalendar accent
  root.style.setProperty('--fc-daygrid-event-dot-color', hexLight);
  root.style.setProperty('--fc-today-bg-color', `rgba(${r}, ${g}, ${b}, 0.08)`);
}


function renderSidebars() {
  const settings = STATE.systemSettings || {};
  const allowDoctorBilling = settings.allow_doctor_billing === 'true';

  const defaultOrders = {
    admin: ['admin-dashboard', 'admin-doctors', 'admin-patients', 'admin-history', 'admin-schedules', 'billing', 'reports', 'admin-bayes', 'admin-users', 'admin-settings', 'admin-audit'],
    doctor: ['dashboard', 'appointments', 'waiting-room', 'patients', 'diagnose', 'history', 'doctor-schedules', 'simulator', 'reports'],
    secretaria: ['waiting-room', 'appointments', 'patients', 'admin-schedules', 'billing']
  };

  if (allowDoctorBilling && !defaultOrders.doctor.includes('billing')) {
    defaultOrders.doctor.push('billing');
  }
  
  const enableSecretariaReports = settings.enable_secretaria_reports === '1';
  if (enableSecretariaReports && !defaultOrders.secretaria.includes('reports')) {
    defaultOrders.secretaria.push('reports');
  }

  let orderAdmin = settings.sidebar_order_admin ? settings.sidebar_order_admin.split(',').map(s => s.trim()) : defaultOrders.admin;
  let orderDoctor = settings.sidebar_order_doctor ? settings.sidebar_order_doctor.split(',').map(s => s.trim()) : defaultOrders.doctor;
  let orderSecretaria = settings.sidebar_order_secretaria ? settings.sidebar_order_secretaria.split(',').map(s => s.trim()) : defaultOrders.secretaria;

  if (allowDoctorBilling && !orderDoctor.includes('billing')) {
    orderDoctor.push('billing');
  } else if (!allowDoctorBilling && orderDoctor.includes('billing')) {
    orderDoctor = orderDoctor.filter(x => x !== 'billing');
  }

  // Garantizar que 'admin-schedules' aparezca en admin
  if (!orderAdmin.includes('admin-schedules')) {
    const settingsIdx = orderAdmin.indexOf('admin-settings');
    if (settingsIdx >= 0) orderAdmin.splice(settingsIdx, 0, 'admin-schedules');
    else orderAdmin.push('admin-schedules');
  }

  // Garantizar que 'admin-schedules' aparezca en secretaria
  if (!orderSecretaria.includes('admin-schedules')) {
    const billIdx = orderSecretaria.indexOf('billing');
    if (billIdx >= 0) orderSecretaria.splice(billIdx, 0, 'admin-schedules');
    else orderSecretaria.push('admin-schedules');
  }

  // Garantizar que 'doctor-schedules' aparezca en doctor
  if (!orderDoctor.includes('doctor-schedules')) {
    const simIdx = orderDoctor.indexOf('simulator');
    if (simIdx >= 0) orderDoctor.splice(simIdx, 0, 'doctor-schedules');
    else orderDoctor.push('doctor-schedules');
  }

  // Garantizar que 'reports' siempre aparezca en el sidebar de doctor
  if (!orderDoctor.includes('reports')) {
    orderDoctor.push('reports');
  }

  // Garantizar que 'reports' aparezca/desaparezca en el sidebar de secretaria
  if (enableSecretariaReports && !orderSecretaria.includes('reports')) {
    orderSecretaria.push('reports');
  } else if (!enableSecretariaReports && orderSecretaria.includes('reports')) {
    orderSecretaria = orderSecretaria.filter(x => x !== 'reports');
  }

  // Garantizar que 'reports' siempre aparezca en el sidebar de admin
  if (!orderAdmin.includes('reports')) {
    const auditIdx = orderAdmin.indexOf('admin-audit');
    if (auditIdx >= 0) orderAdmin.splice(auditIdx, 0, 'reports');
    else orderAdmin.push('reports');
  }

  renderSidebarNav('nav-admin', 'Administración', orderAdmin, 'admin-dashboard');
  renderSidebarNav('nav-doctor', 'Módulo Médico', orderDoctor, 'dashboard');
  renderSidebarNav('nav-secretaria', 'Recepción', orderSecretaria, 'waiting-room');
}

function renderSidebarNav(navId, label, order, defaultActiveTab) {
  const navContainer = document.getElementById(navId);
  if (!navContainer) return;

  let html = `<div class="nav-section-label">${label}</div>`;

  order.forEach(tabId => {
    const item = SIDEBAR_ITEMS[tabId];
    if (item) {
      const activeClass = tabId === defaultActiveTab ? 'nav-item active' : 'nav-item';
      html += `
        <button class="${activeClass}" data-tab="${tabId}" onclick="switchTab('${tabId}')" title="${item.label}">
          ${item.icon}
          <span class="nav-item-text">${item.label}</span>
        </button>
      `;
    }
  });

  navContainer.innerHTML = html;
}

async function loadSystemConfig() {
  const data = await api('GET', '/api/settings/all');
  if (data.success && data.settings) {
    const s = data.settings;
    if (s.clinic_name) {
      const el = document.getElementById('app-clinic-name');
      if (el) el.textContent = s.clinic_name;
    }
    if (s.ui_primary_color) {
      applyPrimaryColor(s.ui_primary_color);
    }
    STATE.systemSettings = s;
    renderSidebars();
  }
}

function makeVitalManual(valInputId, rangeId) {
  const input = document.getElementById(valInputId);
  const range = document.getElementById(rangeId);
  if (!input || !range) return;
  
  if (range.disabled) input.disabled = true;
  input.min = range.min;
  input.max = range.max;

  const syncValue = () => {
    let val = parseFloat(input.value);
    if (isNaN(val)) return;
    val = Math.max(parseFloat(range.min), Math.min(parseFloat(range.max), val));
    if (range.value != val) {
      range.value = val;
      updateVitalBadge(range);
      if (rangeId === 'v-peso' || rangeId === 'v-altura') {
        calculateIMC();
      }
    }
  };

  input.addEventListener('input', syncValue);
  input.addEventListener('blur', () => {
    let val = parseFloat(input.value) || parseFloat(range.min);
    val = Math.max(parseFloat(range.min), Math.min(parseFloat(range.max), val));
    input.value = range.step === "0.1" ? val.toFixed(1) : Math.round(val);
    syncValue();
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      input.blur();
    }
  });
}

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
  const status = await api('GET', '/api/auth/status');
  if (!status.authenticated) { window.location.href = '/login'; return; }

  STATE.user = status.user;
  await loadSystemConfig();
  setupUI();
  buildSymptomToggles();

  ['edad', 'temperatura', 'spo2', 'pas', 'pad', 'fc', 'fr', 'peso', 'altura', 'grasa_corporal'].forEach(k => {
    makeVitalManual(`val-${k}`, `v-${k}`);
  });

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

  // Auto-uppercase en los inputs de nombre completo
  ['pt-name', 'usr-fullname', 'my-fullname'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('blur', () => { el.value = el.value.toUpperCase(); });
    }
  });
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
    document.getElementById('stat-citas-hoy-val').textContent = s.citas_pendientes ?? '0';
    document.querySelector('#stat-citas-hoy .stat-label').textContent = "Citas Pendientes";

    document.getElementById('stat-citas-pendientes-val').textContent = s.citas_hoy ?? '0';
    document.querySelector('#stat-citas-pendientes .stat-label').textContent = "Citas de Hoy";

    document.getElementById('stat-citas-manana-val').textContent = s.citas_manana ?? '0';
    document.querySelector('#stat-citas-manana .stat-label').textContent = "Citas de Mañana";

    document.getElementById('stat-citas-hechas-val').textContent = s.citas_mes ?? '0';
    document.querySelector('#stat-citas-hechas .stat-label').textContent = "Completadas este Mes";

    // Cargar citas para renderizar el calendario de la agenda del doctor en su dashboard
    api('GET', '/api/appointments').then(appData => {
      if (appData.success) {
        STATE.allAppointments = appData.appointments;
        renderDashboardCalendar(appData.appointments);
      }
    });
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
  const isDark = document.documentElement.classList.contains('dark');
  const textColor = isDark ? '#cbd5e1' : '#475569';
  const gridColor = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.04)';

  const chartDefaults = {
    animation: false,
    plugins: { legend: { labels: { color: textColor, font: { size: 10 } } } },
    scales: {
      x: { ticks: { color: textColor, font: { size: 10 } }, grid: { color: gridColor } },
      y: { ticks: { color: textColor, font: { size: 10 } }, grid: { color: gridColor } }
    }
  };

  // 1. Visitas por semana (barras)
  const ctxVisits = document.getElementById('chart-visits-week');
  if (ctxVisits) {
    if (ctxVisits._chartInstance) {
      try { ctxVisits._chartInstance.destroy(); } catch(e) {}
    }
    const visitLabels = s.visits_by_week?.labels || ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'];
    const visitData   = s.visits_by_week?.data   || [0,0,0,0,0,0,0];
    ctxVisits._chartInstance = new Chart(ctxVisits, {
      type: 'bar',
      data: {
        labels: visitLabels,
        datasets: [{ label: 'Visitas', data: visitData,
          backgroundColor: 'rgba(59,130,246,0.5)', borderColor: '#3b82f6',
          borderWidth: 1, borderRadius: 4, maxBarThickness: 28 }]
      },
      options: { ...chartDefaults, responsive: true, maintainAspectRatio: false }
    });
  }

  // 2. Top diagnósticos (dona)
  const ctxDiag = document.getElementById('chart-diag-dist');
  if (ctxDiag && s.top_diagnoses) {
    if (ctxDiag._chartInstance) {
      try { ctxDiag._chartInstance.destroy(); } catch(e) {}
    }
    const colors = ['#3b82f6','#06b6d4','#10b981','#f59e0b','#8b5cf6','#ef4444'];
    ctxDiag._chartInstance = new Chart(ctxDiag, {
      type: 'doughnut',
      data: {
        labels: s.top_diagnoses.map(d => d.name),
        datasets: [{ data: s.top_diagnoses.map(d => d.count),
          backgroundColor: colors, borderColor: '#ffffff', borderWidth: 2 }]
      },
      options: {
        animation: false,
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } } }
      }
    });
  }

  // 3. Nuevos pacientes / mes (línea)
  const ctxGrowth = document.getElementById('chart-patients-growth');
  if (ctxGrowth) {
    if (ctxGrowth._chartInstance) {
      try { ctxGrowth._chartInstance.destroy(); } catch(e) {}
    }
    const labels = s.patients_by_month?.labels || [];
    const pdata  = s.patients_by_month?.data   || [];
    ctxGrowth._chartInstance = new Chart(ctxGrowth, {
      type: 'line',
      data: {
        labels,
        datasets: [{ label: 'Nuevos Pacientes', data: pdata,
          borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)',
          fill: true, tension: 0.3, pointRadius: 3, pointBackgroundColor: '#10b981' }]
      },
      options: { ...chartDefaults, responsive: true, maintainAspectRatio: false }
    });
  }

  // 4. Consultas vs Emergencias (dona)
  const ctxTypes = document.getElementById('chart-visit-types');
  if (ctxTypes) {
    if (ctxTypes._chartInstance) {
      try { ctxTypes._chartInstance.destroy(); } catch(e) {}
    }
    const consultas   = s.total_visits   - (s.total_emergencias || 0) || 0;
    const emergencias = s.total_emergencias || 0;
    ctxTypes._chartInstance = new Chart(ctxTypes, {
      type: 'doughnut',
      data: {
        labels: ['Consultas', 'Emergencias'],
        datasets: [{ data: [consultas, emergencias],
          backgroundColor: ['rgba(59,130,246,0.6)', 'rgba(239,68,68,0.6)'],
          borderColor: '#ffffff', borderWidth: 2 }]
      },
      options: {
        animation: false,
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } } }
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
    return `<tr ondblclick="viewPatient(${p.id})" style="cursor: pointer;">
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
  const nameInput = document.getElementById('pt-name');
  const name    = nameInput ? nameInput.value.trim().toUpperCase() : '';
  if (nameInput) nameInput.value = name;
  const dob     = document.getElementById('pt-dob').value;
  const gender  = document.getElementById('pt-gender').value;
  const phone   = document.getElementById('pt-phone').value.trim();
  const blood   = document.getElementById('pt-blood').value;
  const photo_url = document.getElementById('pt-photo-url') ? document.getElementById('pt-photo-url').value : null;

  const cedulaDigits = cedula.replace(/\D/g, '');
  if (cedulaDigits.length !== 11) {
    toast('warning', 'La cédula debe contener exactamente 11 dígitos numéricos.');
    return;
  }
  if (!name) { toast('warning', 'El nombre completo es obligatorio.'); return; }
  if (!dob) { toast('warning', 'La fecha de nacimiento es obligatoria.'); return; }
  if (new Date(dob) > new Date()) { toast('warning', 'La fecha de nacimiento no puede ser en el futuro.'); return; }

  const btn = document.querySelector('#modal-new-patient .modal-footer .btn-primary');
  setButtonLoading(btn, true);

  try {
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
  } finally {
    setButtonLoading(btn, false);
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

async function createVisit() {
  if (!STATE.visitPatient) { toast('warning', 'Selecciona un paciente primero.'); return; }

  const motivo = document.getElementById('visit-motivo-consulta')?.value.trim() || null;

  if (!motivo) {
    toast('warning', 'El motivo de la visita es obligatorio.'); return;
  }

  const btn = document.querySelector('button[onclick="createVisit()"]');
  setButtonLoading(btn, true);

  try {
    const res = await api('POST', '/api/visits', {
      patient_id: STATE.visitPatient.id,
      visit_type: 'consulta',
      motivo_consulta: motivo,
      motivo_emergencia: null,
    });

    if (res.success) {
      STATE.currentVisitId = res.visit_id;
      document.getElementById('visit-created-msg').textContent =
        `Visita #${res.visit_id} creada para ${STATE.visitPatient.name}`;
      goToVisitStep(3);
      toast('success', '¡Visita creada correctamente!');
    } else {
      toast('error', res.error || 'Error al crear la visita.');
    }
  } finally {
    setButtonLoading(btn, false);
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

async function extractSymptomsFromNarrative() {
  const motivo = document.getElementById('diag-motivo')?.value.trim();
  if (!motivo) {
    toast('warning', 'Por favor, escribe primero el relato o motivo de consulta del paciente.');
    return;
  }

  const btn = document.getElementById('btn-extract-symptoms');
  setButtonLoading(btn, true, 'Analizando relato...');

  try {
    const res = await api('POST', '/api/diagnose/extract-symptoms', { narrative: motivo });
    if (!res.success) {
      toast('error', res.error || 'Error al extraer síntomas con IA.');
      return;
    }

    // Desmarcar todos primero
    document.querySelectorAll('#symptoms-checkboxes .symptom-toggle').forEach(lbl => {
      const cb = lbl.querySelector('input[type="checkbox"]');
      if (cb) cb.checked = false;
      lbl.classList.remove('checked');
    });

    // Marcar los que la IA detectó como True
    let count = 0;
    document.querySelectorAll('#symptoms-checkboxes .symptom-toggle').forEach(lbl => {
      const name = lbl.textContent.trim();
      const cb = lbl.querySelector('input[type="checkbox"]');
      if (cb && res.sintomas && res.sintomas[name] === true) {
        cb.checked = true;
        lbl.classList.add('checked');
        count++;
      }
    });

    toast('success', `Síntomas actualizados por IA (${count} detectados).`);
  } catch (e) {
    toast('error', 'Error al llamar a la API de extracción.');
    console.error(e);
  } finally {
    setButtonLoading(btn, false);
  }
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
    <div class="patient-select-item" onclick="selectConsultPatient(${p.id})"
      style="padding: 12px 16px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.15s;">
      <div style="font-weight: 600; color: var(--text-primary);">${p.name}</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 3px;">Cédula: ${p.cedula} | Edad: ${p.age ?? calcAge(p.dob)} años</div>
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
    <div class="patient-select-item" onclick="selectConsultAppointment(${a.id}, ${a.patient_id})"
      style="padding: 12px 16px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.15s;">
      <div style="font-weight: 600; color: var(--text-primary);">${a.patient_name}</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 3px;">Cita: ${a.scheduled_date} ${a.scheduled_time || ''} | Motivo: ${a.notes || '—'}</div>
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
  switchTab('diagnose');
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
  const ids = input ? [input.id] : Array.from(document.querySelectorAll('input[type="range"][id^="v-"]')).map(el => el.id);
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    const val = parseFloat(el.value) || 0;
    
    // Update visual label regardless of rules
    const key = id.replace('v-', '');
    const valDisplay = document.getElementById(`val-${key}`);
    if (valDisplay) {
      const formattedVal = (el.step === "0.1" || key === 'temperatura') ? val.toFixed(1) : Math.round(val);
      if (valDisplay.tagName === 'INPUT') {
        if (document.activeElement !== valDisplay) {
          valDisplay.value = formattedVal;
        }
      } else {
        valDisplay.textContent = formattedVal;
      }
    }

    const rule = rules[id];
    if (rule) {
        const [cls, label] = rule(val);
        const badgeEl = document.getElementById(`badge-${key}`);
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

  const btn = document.getElementById('btn-diag-phase1');
  setButtonLoading(btn, true, 'Calculando...');

  try {
    STATE.diagConstantes   = getConstantes();
    STATE.diagAntecedentes = getCheckedFrom('antecedentes-checkboxes');

    const res = await api('POST', '/api/diagnose/preliminar', {
      constantes:   STATE.diagConstantes,
      sintomas:     STATE.diagSintomas,
      antecedentes: STATE.diagAntecedentes,
    });

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
    loadRefinementQuestions(res.probabilities);
  } finally {
    setButtonLoading(btn, false);
  }
}

// Extracted runGeminiAnalysis to gemini_chat.js

function applyAIDiagnosis(newDiag) {
  if (!newDiag) return;
  const currentProbs = STATE.phase1Probs || {};
  const updatedProbs = {};
  
  let maxVal = 0.95;
  for (let k in currentProbs) {
    updatedProbs[k] = 0.01;
  }
  updatedProbs[newDiag] = maxVal;
  
  STATE.phase1Probs = updatedProbs;
  
  const dd = document.getElementById('phase1-diagnosis-display');
  if (dd) {
    dd.innerHTML = `
      <div class="diagnosis-name" style="color:var(--brand-light)">${newDiag} <span class="badge badge-verde" style="font-size:12px;margin-left:8px;">Sugerido por IA</span></div>
      <div class="diagnosis-specialist" style="margin-top:6px;">El diagnóstico preliminar ha sido corregido según la sugerencia clínica de la IA.</div>
    `;
  }
  
  const chart = document.getElementById('phase1-probs-chart');
  if (chart) {
    const sorted = Object.entries(updatedProbs).sort(([,a],[,b]) => b - a).slice(0, 10);
    const max = sorted[0][1];
    chart.innerHTML = sorted.map(([d, p]) => {
      const pct  = ((p / max) * 100).toFixed(1);
      const col  = p > 0.3 ? '#ef4444' : p > 0.1 ? '#f59e0b' : '#3b82f6';
      return `<div class="prob-row">
        <div class="prob-name" title="${d}">${d}</div>
        <div class="prob-track"><div class="prob-fill" style="width:${pct}%;background:${col};"></div></div>
        <div class="prob-pct">${(p*100).toFixed(2)}%</div>
      </div>`;
    }).join('');
  }
  
  toast('success', `Se aplicó la corrección de la IA: ${newDiag}`);
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

  // Inicializar estudios sugeridos dinámicamente en el estado
  STATE.selectedTests = (res.tests_sugeridos || []).map(t => ({
    name: t,
    done: false,
    result: ""
  }));

  // Cargar todos los disponibles en paralelo
  loadAvailableTestsAndRender();
}

async function loadAvailableTestsAndRender() {
  if (!STATE.allAvailableTests || STATE.allAvailableTests.length === 0) {
    try {
      const data = await api('GET', '/api/medical_tests');
      STATE.allAvailableTests = data.success ? data.tests : [];
    } catch (e) {
      console.error("Error al obtener estudios médicos:", e);
      STATE.allAvailableTests = [];
    }
  }
  renderTestsList();
}

function getPersonalizedGlucoseLabel(key) {
  const edad = parseFloat(document.getElementById('v-edad')?.value) || 30;
  const imc  = parseFloat(document.getElementById('v-imc')?.value) || 24.2;
  const sexo = (STATE.currentPatient && STATE.currentPatient.sexo) ? STATE.currentPatient.sexo.toUpperCase() : "M";
  
  let shift = 0;
  if (edad > 50) shift += (edad - 50) * 0.15;
  if (imc > 25)  shift += (imc - 25) * 0.3;
  if (sexo === 'F' && edad >= 18 && edad <= 45) shift -= 2.0;
  
  const s = Math.min(Math.max(Math.round(shift), -5), 12);
  
  if (key === "Normal en adulto sano (70-99 mg/dL)") {
    return `Normal en adulto (${70 + s}-${99 + s} mg/dL)`;
  }
  if (key === "Normal ajustado por edad/gestación") {
    return `Normal ajustado por perfil (${75 + s}-${104 + s} mg/dL)`;
  }
  if (key === "Hipoglucemia clínica (<70 mg/dL)") {
    return `Hipoglucemia clínica (<${70 + s} mg/dL)`;
  }
  if (key === "Hipoglucemia severa (<55 mg/dL)") {
    return `Hipoglucemia severa (<${55 + s} mg/dL)`;
  }
  if (key === "Glucemia basal alterada / Prediabetes (100-125 mg/dL)") {
    return `Glucemia basal alterada / Prediabetes (${100 + s}-${125 + s} mg/dL)`;
  }
  if (key === "Hiperglucemia clínica compatible con Diabetes (>=126 mg/dL)") {
    return `Hiperglucemia clínica compatible con Diabetes (>=${126 + s} mg/dL)`;
  }
  if (key === "Hiperglucemia severa en crisis (>250 mg/dL)") {
    return `Hiperglucemia severa en crisis (>${250 + s} mg/dL)`;
  }
  return key;
}

function getPersonalizedHemogramaLabel(key) {
  const sexo = (STATE.currentPatient && STATE.currentPatient.sexo) ? STATE.currentPatient.sexo.toUpperCase() : "M";
  if (key === "Normal (Valores de referencia estables)") {
    const hbRange = (sexo === 'F') ? "12.0 - 15.5" : "13.5 - 17.5";
    return `Normal (Valores estables - Hb: ${hbRange} g/dL)`;
  }
  return key;
}

function getPersonalizedNTproBNPLabel(key) {
  const edad = parseFloat(document.getElementById('v-edad')?.value) || 30;
  if (key === "Elevación severa (>450 pg/mL en jóvenes / >900 pg/mL en mayores - ICC descompensada)") {
    let limit = 450;
    if (edad >= 50 && edad <= 75) limit = 900;
    if (edad > 75) limit = 1800;
    return `Elevación severa (>${limit} pg/mL - ICC descompensada)`;
  }
  return key;
}

function renderTestsList() {
  const testsForm = document.getElementById('tests-form');
  if (!testsForm) return;
  
  let html = '';
  
  if (!STATE.selectedTests || STATE.selectedTests.length === 0) {
    html += `<div style="color:var(--text-muted);font-size:13px;margin-bottom:16px;">No se requieren análisis adicionales obligatorios. Puedes añadir estudios usando la caja inferior.</div>`;
  } else {
    html += STATE.selectedTests.map((t, i) => {
      const match = (STATE.allAvailableTests || []).find(dbT => dbT.test_name.toLowerCase() === t.name.toLowerCase());
      const defaultResults = ["Normal", "Alto", "Bajo", "Positivo", "Negativo"];
      const possibleResults = (match && match.possible_results && match.possible_results.length > 0)
        ? match.possible_results
        : defaultResults;
      
      const resultField = `
        <select class="form-input test-result-select" style="margin:0; width: 100%;" onchange="updateTestState(${i}, 'result', this.value)">
          <option value="">— Seleccionar Resultado —</option>
          ${possibleResults.map(r => {
            let label = r;
            const nameLower = t.name.toLowerCase();
            if (nameLower === 'glucosa en ayunas') {
              label = getPersonalizedGlucoseLabel(r);
            } else if (nameLower === 'hemograma completo') {
              label = getPersonalizedHemogramaLabel(r);
            } else if (nameLower === 'nt-probnp') {
              label = getPersonalizedNTproBNPLabel(r);
            }
            return `<option value="${r}" ${t.result === r ? 'selected' : ''}>${label}</option>`;
          }).join('')}
        </select>
      `;
      
      return `
        <div class="test-item" style="display:grid; grid-template-columns: 2.5fr 1.2fr 2fr auto; align-items:center; gap:12px; margin-bottom:12px; padding:10px; background:rgba(255,255,255,0.02); border-radius:6px; border: 1px solid var(--border-color);">
          <div class="test-name" style="font-weight:600; font-size:13px; color:var(--text); text-align: left;">🔬 ${t.name}</div>
          <div class="test-done-toggle" style="display:flex; align-items:center; gap:6px;">
            <input type="checkbox" id="test-done-${i}" ${t.done ? 'checked' : ''} onchange="updateTestState(${i}, 'done', this.checked)"/>
            <label for="test-done-${i}" style="margin:0; font-size:12px; cursor:pointer;">¿Realizado?</label>
          </div>
          <div id="test-result-wrap-${i}" style="display: ${t.done ? 'block' : 'none'};">
            ${resultField}
          </div>
          <div>
            <button type="button" class="btn-secondary" style="padding:4px 8px; margin:0; border-color:transparent; background:transparent; color:#ef4444; font-size: 15px;" onclick="removeTestFromList(${i})">
              🗑️
            </button>
          </div>
        </div>
      `;
    }).join('');
  }
  
  const addedNames = (STATE.selectedTests || []).map(t => t.name.toLowerCase());
  const remainingTests = (STATE.allAvailableTests || []).filter(t => !addedNames.includes(t.test_name.toLowerCase()));
  
  html += `
    <div class="add-test-row" style="display:flex; gap:12px; align-items:center; margin-top:16px; padding-top:12px; border-top: 1px dashed var(--border-color);">
      <select id="select-new-test" class="form-input" style="margin:0; flex: 2;" onchange="handleNewTestSelect(this)">
        <option value="">— Seleccionar estudio para añadir (+) —</option>
        ${remainingTests.map(t => `<option value="${t.test_name}">${t.test_name}</option>`).join('')}
        <option value="__custom__">Otro estudio (escribir)...</option>
      </select>
      <input type="text" id="custom-test-name" class="form-input" style="display:none; margin:0; flex: 2;" placeholder="Nombre del estudio..." />
      <button type="button" class="btn-primary" style="padding: 8px 16px; margin:0; background-color: var(--brand);" onclick="addTestToList()">
        ➕ Añadir Estudio
      </button>
    </div>
  `;
  
  testsForm.innerHTML = html;
}

function updateTestState(index, key, val) {
  if (STATE.selectedTests[index]) {
    STATE.selectedTests[index][key] = val;
    if (key === 'done') {
      const wrap = document.getElementById(`test-result-wrap-${index}`);
      if (wrap) wrap.style.display = val ? 'block' : 'none';
    }
  }
}

function removeTestFromList(index) {
  STATE.selectedTests.splice(index, 1);
  renderTestsList();
}

function handleNewTestSelect(el) {
  const customInput = document.getElementById('custom-test-name');
  if (!customInput) return;
  if (el.value === '__custom__') {
    customInput.style.display = 'block';
  } else {
    customInput.style.display = 'none';
  }
}

function addTestToList() {
  const select = document.getElementById('select-new-test');
  const customInput = document.getElementById('custom-test-name');
  if (!select) return;
  
  let testName = "";
  if (select.value === '__custom__') {
    testName = customInput?.value.trim();
  } else {
    testName = select.value;
  }
  
  if (!testName) {
    toast('warning', 'Selecciona o escribe un nombre de estudio válido.');
    return;
  }
  
  if (STATE.selectedTests.some(t => t.name.toLowerCase() === testName.toLowerCase())) {
    toast('warning', 'Este estudio ya está en la lista.');
    return;
  }
  
  STATE.selectedTests.push({
    name: testName,
    done: false,
    result: ""
  });
  
  renderTestsList();
}

async function runPhase2() {
  const patientId      = STATE.currentPatient?.id;
  const patientName    = document.getElementById('diag-patient-name').value.trim() || 'Paciente Anónimo';
  const motivoConsulta = document.getElementById('diag-motivo').value.trim() || 'Sin especificar';

  if (!STATE.currentVisitId && patientId) {
    const appIdRaw = document.getElementById('diag-appointment-id')?.value;
    const appointmentId = appIdRaw ? parseInt(appIdRaw) : null;
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

  const testsResultados = (STATE.selectedTests || []).map(t => ({
    test_name: t.name,
    done: t.done,
    result: t.done ? t.result : null
  }));

  const btn = document.getElementById('btn-diag-phase2');
  setButtonLoading(btn, true, 'Calculando Fase 2...');

  try {
    const res = await api('POST', '/api/diagnose/phase2-calculate', {
      preliminar_probs: STATE.phase1Probs,
      tests_resultados: testsResultados,
    });

    if (!res.success) { toast('error', res.error || 'Error al calcular Fase 2.'); return; }

    STATE.finalProbs = res.probabilities;
    STATE.finalTestsResultados = testsResultados;

    renderPhase2ReviewScreen(res);
    runGeminiAnalysis(res.probabilities, testsResultados);
    toast('success', '✅ Fase 2 calculada. Revise y seleccione el diagnóstico final.');
  } finally {
    setButtonLoading(btn, false);
  }
}

function renderPhase2ReviewScreen(res) {
  document.getElementById('phase1-result').style.display = 'none';
  
  let reviewPanel = document.getElementById('phase2-review-panel');
  if (!reviewPanel) {
    reviewPanel = document.createElement('div');
    reviewPanel.id = 'phase2-review-panel';
    reviewPanel.style.marginTop = '24px';
    const parent = document.getElementById('phase1-result').parentNode;
    parent.insertBefore(reviewPanel, document.getElementById('phase1-result').nextSibling);
  }
  
  reviewPanel.style.display = '';
  
  const sorted = Object.entries(res.probabilities || {}).sort(([,a],[,b]) => b - a);
  const topDiag = sorted[0]?.[0] || '';
  const topProb = sorted[0]?.[1] || 0.0;
  
  STATE.confirmedDiagnosisSelected = topDiag;
  
  let html = `
    <div class="section-card">
      <div class="section-header">
        <h2>⚖️ Revisión del Diagnóstico Final (Fase 2)</h2>
        <div class="confidence-pill" style="background-color: var(--brand); font-family:var(--mono);">${(topProb * 100).toFixed(2)}%</div>
      </div>
      <p style="color:var(--text-muted); font-size:13px; margin-bottom:16px;">
        Los análisis y estudios clínicos han actualizado las probabilidades. Seleccione el diagnóstico final definitivo para generar el informe clínico final y la receta médica:
      </p>
      
      <div class="review-diagnoses-list" style="display:flex; flex-direction:column; gap:10px; margin-bottom:20px;">
  `;
  
  html += sorted.slice(0, 8).map(([d, p], idx) => {
    const isChecked = d === topDiag ? 'checked' : '';
    const pct = (p * 100).toFixed(2);
    return `
      <label class="symptom-toggle ${d === topDiag ? 'checked' : ''}" id="review-lbl-${idx}" style="display:flex; align-items:center; justify-content:space-between; padding:12px; border: 1px solid var(--border-color); border-radius:8px; cursor:pointer;" onclick="selectReviewDiagnosis('${d.replace(/'/g, "\\'")}', ${idx}, ${sorted.length + 1})">
        <div style="display:flex; align-items:center; gap:10px; text-align:left;">
          <input type="radio" name="review-diagnosis-radio" id="radio-diag-${idx}" value="${d}" ${isChecked} style="margin:0;" />
          <span style="font-weight:600; font-size:14px; color: var(--text);">${d}</span>
        </div>
        <span style="font-family:var(--mono); font-weight:bold; color: var(--brand-light);">${pct}%</span>
      </label>
    `;
  }).join('');
  
  html += `
        <!-- Opción manual -->
        <label class="symptom-toggle" id="review-lbl-manual" style="display:flex; flex-direction:column; gap:8px; padding:12px; border: 1px solid var(--border-color); border-radius:8px; cursor:pointer;">
          <div style="display:flex; align-items:center; gap:10px; text-align:left;" onclick="selectReviewDiagnosis('__manual__', 'manual', ${sorted.length + 1})">
            <input type="radio" name="review-diagnosis-radio" id="radio-diag-manual" value="__manual__" style="margin:0;" />
            <span style="font-weight:600; font-size:14px; color: var(--text);">Otro diagnóstico (Escribir manualmente)</span>
          </div>
          <input type="text" id="custom-final-diagnosis" class="form-input" style="display:none; margin: 4px 0 0 24px;" placeholder="Ej. Síndrome de Intestino Irritable..." oninput="STATE.confirmedDiagnosisSelected = this.value" />
        </label>
      </div>
      
      <div class="form-actions" style="margin-top:24px; border-top: 1px solid var(--border-color); padding-top:16px; justify-content: flex-end; gap:12px;">
        <button id="btn-confirm-final" class="btn-primary btn-large" onclick="confirmFinalDiagnosis()">
          📄 Generar Informe Clínico y Receta
        </button>
      </div>
    </div>
  `;
  
  reviewPanel.innerHTML = html;
}

function selectReviewDiagnosis(diag, idx, total) {
  for (let i = 0; i < total; i++) {
    const lbl = document.getElementById(`review-lbl-${i}`);
    if (lbl) lbl.classList.remove('checked');
    const rd = document.getElementById(`radio-diag-${i}`);
    if (rd) rd.checked = false;
  }
  const lblManual = document.getElementById('review-lbl-manual');
  if (lblManual) lblManual.classList.remove('checked');
  const rdManual = document.getElementById('radio-diag-manual');
  if (rdManual) rdManual.checked = false;
  
  const customInput = document.getElementById('custom-final-diagnosis');
  if (customInput) customInput.style.display = 'none';

  if (diag === '__manual__') {
    if (lblManual) lblManual.classList.add('checked');
    if (rdManual) rdManual.checked = true;
    if (customInput) {
      customInput.style.display = 'block';
      STATE.confirmedDiagnosisSelected = customInput.value.trim();
    }
  } else {
    const activeLbl = document.getElementById(`review-lbl-${idx}`);
    if (activeLbl) activeLbl.classList.add('checked');
    const activeRd = document.getElementById(`radio-diag-${idx}`);
    if (activeRd) activeRd.checked = true;
    STATE.confirmedDiagnosisSelected = diag;
  }
}

async function confirmFinalDiagnosis() {
  const diag = STATE.confirmedDiagnosisSelected;
  if (!diag) {
    toast('warning', 'Por favor, seleccione o ingrese un diagnóstico final.');
    return;
  }

  const patientId      = STATE.currentPatient?.id;
  const patientName    = document.getElementById('diag-patient-name').value.trim() || 'Paciente Anónimo';
  const motivoConsulta = document.getElementById('diag-motivo').value.trim() || 'Sin especificar';
  
  const btn = document.getElementById('btn-confirm-final');
  setButtonLoading(btn, true, 'Generando reporte e informe...');

  try {
    const res = await api('POST', '/api/diagnose/final', {
      patient_id:      patientId,
      patient_name:    patientName,
      motivo_consulta: motivoConsulta,
      visit_id:        STATE.currentVisitId,
      preliminar_probs: STATE.phase1Probs,
      tests_resultados: STATE.finalTestsResultados,
      sintomas:        STATE.diagSintomas,
      antecedentes:    STATE.diagAntecedentes,
      constantes:      STATE.diagConstantes,
      confirmed_diagnosis: diag,
      save_diagnosis:  false
    });

    if (!res.success) {
      toast('error', res.error || 'Error al confirmar diagnóstico final.');
      return;
    }

    STATE.finalDiagnosisRes = res;
    
    const reviewPanel = document.getElementById('phase2-review-panel');
    if (reviewPanel) reviewPanel.style.display = 'none';

    renderFinalResult(res);
    toast('success', '✅ Informe generado. Revise las indicaciones y finalice la consulta para guardar.');
  } catch (e) {
    toast('error', 'Error en la conexión con el servidor.');
    console.error(e);
  } finally {
    setButtonLoading(btn, false);
  }
}

function toggleRefutationFields(chk) {
  const fields = document.getElementById('refutation-fields');
  if (fields) fields.style.display = chk.checked ? 'block' : 'none';
}

async function saveFinalDecision(createPrescription) {
  const btn1 = document.getElementById('btn-finish-prescribe');
  const btn2 = document.getElementById('btn-finish-only');
  const activeBtn = createPrescription ? btn1 : btn2;
  const secondaryBtn = createPrescription ? btn2 : btn1;

  const isRefuted = document.getElementById('chk-refute-ai')?.checked || false;
  const doctorOverride = document.getElementById('doctor-override-diagnosis')?.value.trim();
  const refutationReason = document.getElementById('refutation-reason')?.value.trim();

  if (isRefuted && !doctorOverride) {
    toast('warning', 'Si refutas el diagnóstico, debes escribir el diagnóstico médico real.');
    return;
  }

  if (activeBtn) setButtonLoading(activeBtn, true);
  if (secondaryBtn) secondaryBtn.disabled = true;

  try {
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
      confirmed_diagnosis: STATE.confirmedDiagnosisSelected || null,
      save_diagnosis: true,
      is_refuted: isRefuted,
      refutation_reason: refutationReason,
      doctor_override_diagnosis: doctorOverride
    });

    if (!res.success) {
      toast('error', res.error || 'Error al guardar el diagnóstico final.');
      return;
    }

    // Marcar la cita como completada solo si no va a crear receta
    if (!createPrescription) {
      const appId = document.getElementById('diag-appointment-id')?.value;
      if (appId) {
        api('POST', `/api/appointments/${appId}/status`, { status: 'completada' });
      }
    }

    toast('success', 'Consulta finalizada con éxito.');

    if (createPrescription && STATE.currentPatient && STATE.currentVisitId) {
      // Abrir modal de selección de receta
      openPrescriptionChoice();
    } else {
      // Limpiar para nueva consulta
      resetDiagnose();
    }
  } finally {
    if (activeBtn) setButtonLoading(activeBtn, false);
    if (secondaryBtn) secondaryBtn.disabled = false;
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

// Extracted sendGeminiMessage to gemini_chat.js

// Extracted appendGeminiMessage to gemini_chat.js

// Extracted appendGeminiTyping to gemini_chat.js

// Extracted removeGeminiTyping to gemini_chat.js


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


async function loadAppointments() {
  const filterDoc = document.getElementById('appointment-doctor-filter')?.value;
  const url = '/api/appointments' + (filterDoc ? `?doctor_id=${filterDoc}` : '');
  const data = await api('GET', url);
  if (!data.success) { toast('error', 'Error cargando citas.'); return; }
  
  STATE.allAppointments = data.appointments || [];
  filterAppointmentsTable();
  
  // Update calendar if it's visible
  if (calendarInstance && document.getElementById('app-calendar-view')?.style.display !== 'none') {
    renderCalendar();
  }
  
  // Cargar pacientes y doctores para el modal si no están cargados
  if (STATE.user.role === 'admin' || STATE.user.role === 'secretaria') {
    const docWrap = document.getElementById('appointment-doctor-filter-wrap');
    if (docWrap) docWrap.style.display = 'flex';
    const toggles = document.getElementById('app-view-toggles');
    if (toggles) toggles.style.display = 'flex';
    
    const docs = await api('GET', '/api/users');
    if (docs.success) {
      const doctors = docs.users.filter(u => u.role === 'doctor');
      STATE.allDoctors = doctors;
      
      const filterSelect = document.getElementById('appointment-doctor-filter');
      if (filterSelect && filterSelect.options.length <= 1) {
          filterSelect.innerHTML = `<option value="">Todos los doctores</option>` + doctors.map(d => `<option value="${d.id}">${d.full_name || d.username}</option>`).join('');
      }
    }
    const pts = await api('GET', '/api/patients');
    if (pts.success) {
      STATE.allPatients = pts.patients;
    }
  } else {
    // Si es doctor, ocultar filtro de doctores pero mostrar toggle de vista si lo desea
    const docWrap = document.getElementById('appointment-doctor-filter-wrap');
    if (docWrap) docWrap.style.display = 'none';
    const btnNew = document.getElementById('btn-new-appointment');
    if (btnNew) btnNew.style.display = 'none';
  }
}

function switchAppointmentView(viewType) {
  const btnTable = document.getElementById('btn-view-table');
  const btnCal = document.getElementById('btn-view-calendar');
  if (btnTable) btnTable.style.background = viewType === 'table' ? 'var(--bg-hover)' : 'transparent';
  if (btnCal) btnCal.style.background = viewType === 'calendar' ? 'var(--bg-hover)' : 'transparent';
  
  const tableView = document.getElementById('app-table-view');
  const calView = document.getElementById('app-calendar-view');
  if (tableView) tableView.style.display = viewType === 'table' ? 'block' : 'none';
  if (calView) calView.style.display = viewType === 'calendar' ? 'block' : 'none';
  
  if (viewType === 'calendar') {
    renderCalendar();
  }
}

let calendarInstance = null;
let dashboardCalendarInstance = null;

function renderCalendar() {
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) return;
  const isMobile = window.innerWidth < 768;

  if (!calendarInstance) {
    calendarInstance = new FullCalendar.Calendar(calendarEl, {
      initialView: isMobile ? 'timeGridDay' : 'timeGridWeek',
      locale: 'es',
      headerToolbar: isMobile ? {
        left: 'prev,next today',
        center: 'title',
        right: 'timeGridDay,timeGridWeek,listWeek'
      } : {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
      },
      slotMinTime: '06:00:00',
      slotMaxTime: '22:00:00',
      contentHeight: 'auto',
      expandRows: true,
      allDaySlot: false,
      editable: true,
      eventClick: function(info) {
        if (STATE.user && (STATE.user.role === 'secretaria' || STATE.user.role === 'admin')) {
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
          loadAppointments();
        } else {
          toast('error', res.error || 'Error al reprogramar la cita.');
          info.revert();
        }
      }
    });
    calendarInstance.render();
  }
  
  calendarInstance.removeAllEvents();
  const activeApps = (STATE.allAppointments || []).filter(a => a.status !== 'cancelada' && a.status !== 'eliminada');
  const events = activeApps.map(a => {
    let color = '#3b82f6';
    if (a.status === 'completada') color = '#10b981';
    else if (a.status === 'cancelada') color = '#ef4444';
    else if (a.status === 'en_curso') color = '#f59e0b';
    
    let endStr = undefined;
    let startStr = a.scheduled_date;
    
    if (a.scheduled_time) {
        const timePart = a.scheduled_time.substring(0, 8);
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
      title: `${a.patient_name || 'Paciente'} (${a.doctor_fullname || ''})`,
      start: startStr,
      end: endStr,
      color: color,
      allDay: !a.scheduled_time
    };
  });
  
  calendarInstance.addEventSource(events);
}

function renderDashboardCalendar(appointments) {
  const calendarEl = document.getElementById('doctor-dashboard-calendar');
  if (!calendarEl) return;
  const isMobile = window.innerWidth < 768;

  if (!dashboardCalendarInstance) {
    dashboardCalendarInstance = new FullCalendar.Calendar(calendarEl, {
      initialView: isMobile ? 'timeGridDay' : 'timeGridWeek',
      locale: 'es',
      headerToolbar: isMobile ? {
        left: 'prev,next today',
        center: 'title',
        right: 'timeGridDay,timeGridWeek,listWeek'
      } : {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
      },
      slotMinTime: '06:00:00',
      slotMaxTime: '22:00:00',
      contentHeight: 'auto',
      expandRows: true,
      allDaySlot: false,
      editable: false,
      eventClick: function(info) {
        const app = (STATE.allAppointments || []).find(a => a.id == info.event.id);
        if (app && app.patient_id) {
          viewPatient(app.patient_id);
        }
      }
    });
    dashboardCalendarInstance.render();
  }

  setTimeout(() => {
    try { if (dashboardCalendarInstance) dashboardCalendarInstance.updateSize(); } catch(e) {}
  }, 50);

  dashboardCalendarInstance.removeAllEvents();
  const activeApps = (appointments || STATE.allAppointments || []).filter(a => a.status !== 'cancelada' && a.status !== 'eliminada');
  const events = activeApps.map(a => {
    let color = '#3b82f6';
    if (a.status === 'completada') color = '#10b981';
    else if (a.status === 'cancelada') color = '#ef4444';
    else if (a.status === 'en_curso') color = '#f59e0b';
    
    let endStr = undefined;
    let startStr = a.scheduled_date;
    if (a.scheduled_time) {
        const timePart = a.scheduled_time.substring(0, 8);
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
      title: `${a.patient_name || 'Paciente'} - ${a.notes || 'Consulta'}`,
      start: startStr,
      end: endStr,
      color: color,
      allDay: !a.scheduled_time
    };
  });

  dashboardCalendarInstance.addEventSource(events);
}

function filterAppointmentsTable() {
  if (!STATE.allAppointments) return;
  const q = (document.getElementById('appointment-search')?.value || '').toLowerCase().trim();
  const status = document.getElementById('appointment-status-filter')?.value || '';
  const dateFrom = document.getElementById('appointment-date-from')?.value || '';
  const dateTo = document.getElementById('appointment-date-to')?.value || '';
  const sortVal = document.getElementById('appointment-sort-filter')?.value || 'date-desc';

  let list = [...STATE.allAppointments];

  // 1. Text search
  if (q) {
    list = list.filter(a =>
      (a.patient_name || '').toLowerCase().includes(q) ||
      (a.patient_cedula || '').toLowerCase().includes(q) ||
      (a.doctor_fullname || '').toLowerCase().includes(q) ||
      (a.notes || '').toLowerCase().includes(q)
    );
  }

  // 2. Status filter
  if (status) {
    list = list.filter(a => a.status === status);
  }

  // 3. Date range filter (Desde / Hasta)
  if (dateFrom) {
    list = list.filter(a => a.scheduled_date >= dateFrom);
  }
  if (dateTo) {
    list = list.filter(a => a.scheduled_date <= dateTo);
  }

  // 4. Sort
  list.sort((a, b) => {
    if (sortVal === 'date-desc') {
      const dtA = `${a.scheduled_date} ${a.scheduled_time || ''}`;
      const dtB = `${b.scheduled_date} ${b.scheduled_time || ''}`;
      return dtB.localeCompare(dtA);
    } else if (sortVal === 'date-asc') {
      const dtA = `${a.scheduled_date} ${a.scheduled_time || ''}`;
      const dtB = `${b.scheduled_date} ${b.scheduled_time || ''}`;
      return dtA.localeCompare(dtB);
    } else if (sortVal === 'patient-asc') {
      return (a.patient_name || '').localeCompare(b.patient_name || '');
    } else if (sortVal === 'doctor-asc') {
      return (a.doctor_fullname || '').localeCompare(b.doctor_fullname || '');
    } else if (sortVal === 'status') {
      return (a.status || '').localeCompare(b.status || '');
    }
    return 0;
  });

  renderAppointmentsTable(list);
}

function resetAppointmentFilters() {
  const search = document.getElementById('appointment-search');
  const status = document.getElementById('appointment-status-filter');
  const dFrom = document.getElementById('appointment-date-from');
  const dTo = document.getElementById('appointment-date-to');
  const sort = document.getElementById('appointment-sort-filter');
  if (search) search.value = '';
  if (status) status.value = '';
  if (dFrom) dFrom.value = '';
  if (dTo) dTo.value = '';
  if (sort) sort.value = 'date-desc';
  filterAppointmentsTable();
}

function searchAppointments() {
  filterAppointmentsTable();
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
    
    const clickAction = ((STATE.user.role === 'secretaria' || STATE.user.role === 'admin') && a.status !== 'completada' && a.status !== 'cancelada') 
      ? `openEditAppointmentModal(${a.id})` 
      : (STATE.user.role === 'doctor' && (a.status === 'abierta' || a.status === 'en_curso')) 
        ? `selectConsultAppointment(${a.id}, ${a.patient_id})` 
        : '';

    return `<tr ${clickAction ? `ondblclick="${clickAction}" style="cursor: pointer;"` : ''}>
      <td>
        <strong style="color:var(--text-primary)">${a.patient_name}</strong>
        ${a.parent_appointment_id ? '<span class="badge badge-amarillo" style="font-size:10px; margin-left:8px;">Seguimiento</span>' : ''}
      </td>
      <td>${a.scheduled_date} ${a.scheduled_time || ''}</td>
      <td>${a.doctor_fullname || '—'}</td>
      <td>${a.notes || '—'}</td>
      <td>${statusBadge}</td>
      <td>
        <div style="display:flex; gap:6px; align-items:center; min-height:32px;">
          ${(STATE.user.role === 'secretaria' || STATE.user.role === 'admin') ? 
            `
             ${a.status !== 'completada' && a.status !== 'cancelada' ? 
               `<button class="btn-icon" title="Editar Cita" style="color:var(--brand);" onclick="openEditAppointmentModal(${a.id})">
                 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>` : ''
             }
             ${a.status === 'abierta' ? 
               `<button class="btn-icon" title="Cancelar Cita" style="color:var(--red);" onclick="cancelAppointment(${a.id})">
                 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>` : ''
             }
             ${a.status === 'cancelada' ? 
               `<button class="btn-icon" title="Activar Cita" style="color:var(--green);" onclick="activateAppointment(${a.id})">
                 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                </button>` : ''
             }
            ` : (STATE.user.role === 'doctor' && (a.status === 'abierta' || a.status === 'en_curso')) ?
            `<button class="btn-icon" title="Atender Consulta" style="color:var(--brand);" onclick="selectConsultAppointment(${a.id}, ${a.patient_id})">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
             </button>` : ''
          }
        </div>
      </td>
    </tr>`;
  }).join('');
  el.innerHTML = `<table class="data-table"><thead><tr><th>Paciente</th><th>Fecha y Hora</th><th>Doctor</th><th>Notas</th><th>Estado</th><th style="min-width:80px;">Acción</th></tr></thead><tbody>${rows}</tbody></table>`;
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
  if (app.status === 'completada') {
    toast('warning', 'Las citas completadas no se pueden editar.');
    return;
  }
  if (app.status === 'cancelada') {
    toast('warning', 'Las citas canceladas deben ser activadas antes de editar.');
    return;
  }
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
  
  const btn = document.getElementById('btn-save-appointment');
  setButtonLoading(btn, true);

  try {
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
  } finally {
    setButtonLoading(btn, false);
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

async function activateAppointment(id) {
  if (!confirm('¿Desea activar esta cita cancelada?')) return;
  const res = await api('POST', `/api/appointments/${id}/status`, { status: 'abierta' });
  if (res.success) {
    toast('success', 'Cita activada correctamente');
    loadAppointments();
  } else {
    toast('error', res.error || 'Error al activar cita');
  }
}

// RECETAS MÉDICAS
function openPrescriptionChoice() {
  STATE.rxList = [];
  closeModal('modal-diagnosis-result');
  openModal('modal-prescription-choice');
}

function generatePrescriptionManual() {
  closeModal('modal-prescription-choice');
  openPrescriptionModal();
}

async function generatePrescriptionAI() {
  const btn = document.getElementById('btn-prescription-ai');
  if (!STATE.currentVisitId) {
    toast('error', 'No hay ninguna visita activa seleccionada.');
    return;
  }
  
  setButtonLoading(btn, true, 'Generando con IA...');
  
  try {
    const res = await api('POST', `/api/visits/${STATE.currentVisitId}/prescription/generate-ai`);
    if (!res.success) {
      if (res.error === 'subscription_required') {
        toast('error', res.message || 'Se requiere suscripción VIP.');
      } else {
        toast('error', res.error || 'Error al generar la receta con IA.');
      }
      return;
    }
    
    STATE.rxList = [];
    if (res.medications && res.medications.length > 0) {
      res.medications.forEach(m => {
        STATE.rxList.push({
          med: m.medication || '',
          dos: m.dosage || '',
          freq: m.frequency || '',
          days: m.duration_days || 1,
          qty: m.quantity || 1,
          notes: m.notes || ''
        });
      });
      toast('success', 'Receta sugerida por IA generada. Revísela antes de guardar.');
    } else {
      toast('warning', 'La IA no pudo sugerir medicamentos para este caso.');
    }
    
    closeModal('modal-prescription-choice');
    renderRxList();
    
    // Clear inputs in manual section in case
    document.getElementById('rx-medication').value = '';
    document.getElementById('rx-dosage').value = '';
    document.getElementById('rx-frequency').value = '';
    document.getElementById('rx-days').value = '';
    document.getElementById('rx-quantity').value = '';
    document.getElementById('rx-notes').value = '';
    
    openModal('modal-prescription');
  } catch (err) {
    toast('error', 'Error al invocar la API de generación.');
  } finally {
    setButtonLoading(btn, false);
  }
}

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
  
  const btn = document.querySelector('button[onclick="savePrescription()"]');
  setButtonLoading(btn, true);
  
  try {
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
    
    if (successCount === STATE.rxList.length) {
      toast('success', 'Receta guardada correctamente en el historial.');
      
      const appId = document.getElementById('diag-appointment-id')?.value;
      if (appId) {
        api('POST', `/api/appointments/${appId}/status`, { status: 'completada' });
      }
      
      closeModal('modal-prescription');
      openModal('modal-prescription-success');
    } else {
      toast('error', 'Ocurrió un error al guardar algunos medicamentos.');
    }
  } finally {
    setButtonLoading(btn, false);
  }
}

function printPrescriptionFromSuccess() {
  const visitId = STATE.currentVisitId;
  if (visitId) {
    window.open(`/api/pdf/prescription/${visitId}`, '_blank');
  } else {
    toast('error', 'No hay una visita activa.');
  }
}

function closeModalPrescriptionSuccess() {
  closeModal('modal-prescription-success');
  resetDiagnose();
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
    return `<tr ondblclick="viewFullHistoryReport(${r.diagnosis_id})" style="cursor: pointer;">
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
// Extracted initSimulator to simulator.js

// Extracted runSimulation to simulator.js

// Extracted resetSimulation to simulator.js

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
    return `<tr ondblclick="editUser(${d.id})" style="cursor: pointer;">
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
  const fullNameInput = document.getElementById('usr-fullname');
  const fullName    = fullNameInput ? fullNameInput.value.trim().toUpperCase() : null;
  if (fullNameInput) fullNameInput.value = fullName || '';
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

  const btn = document.querySelector('#modal-new-user .modal-footer .btn-primary');
  setButtonLoading(btn, true);

  try {
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
  } finally {
    setButtonLoading(btn, false);
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

// Extracted escHtml to utils.js

// Extracted markdownToHtml to utils.js

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
  ['info','vitals','meds','alerts','docs','statement'].forEach(t => {
    const el = document.getElementById(`patient-tab-${t}`);
    if (el) el.style.display = t === tab ? '' : 'none';
    const btn = document.getElementById(`mtab-${t}`);
    if (btn) btn.classList.toggle('active', t === tab);
  });
  // Lazy-load según pestaña
  if (tab === 'vitals')  loadPatientVitals(STATE.viewingPatientId);
  if (tab === 'meds')    loadPatientMeds(STATE.viewingPatientId);
  if (tab === 'alerts')  loadPatientAlerts(STATE.viewingPatientId);
  if (tab === 'docs')    loadPatientDocs(STATE.viewingPatientId);
  if (tab === 'statement') loadPatientStatement(STATE.viewingPatientId);
}

async function loadPatientStatement(id) {
  if (!id) return;
  const el = document.getElementById('patient-statement-content');
  const totalEl = document.getElementById('patient-statement-total');
  el.innerHTML = '<div class="loading-state"><div class="spinner-ring"></div></div>';
  totalEl.textContent = 'Calculando...';
  
  const data = await api('GET', `/api/patients/${id}/account-statement`);
  if (!data.success) {
    el.innerHTML = `<div class="empty-state"><span>${escHtml(data.error || 'Error al cargar')}</span></div>`;
    totalEl.textContent = 'Total Pendiente: RD$ 0.00';
    return;
  }
  
  const stmt = data.statement;
  totalEl.textContent = `Total Pendiente: RD$ ${stmt.total_balance.toFixed(2)}`;
  
  if (!stmt.invoices || stmt.invoices.length === 0) {
    el.innerHTML = '<div class="empty-state"><span>No hay historial de cargos.</span></div>';
    return;
  }
  
  const rows = stmt.invoices.map(item => {
    let statusBadge = '<span class="badge badge-verde">Pagado</span>';
    if (item.balance_due > 0 && item.amount_paid === 0) statusBadge = '<span class="badge badge-rojo">Pendiente</span>';
    else if (item.balance_due > 0 && item.amount_paid > 0) statusBadge = '<span class="badge badge-amarillo">Parcial</span>';
    
    return `<tr>
      <td>${item.created_at}</td>
      <td style="text-transform: capitalize;">${escHtml(item.invoice_type)}</td>
      <td>RD$ ${item.total.toFixed(2)}</td>
      <td>RD$ ${item.amount_paid.toFixed(2)}</td>
      <td style="color:var(--rojo); font-weight:bold;">RD$ ${item.balance_due.toFixed(2)}</td>
      <td>${statusBadge}</td>
    </tr>`;
  }).join('');
  
  el.innerHTML = `
    <div class="table-responsive" style="width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch;">
      <table class="vitals-history-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Concepto</th>
            <th>Total</th>
            <th>Pagado</th>
            <th>Pendiente</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
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

  let statusHtml = '';
  if (p.vital_status === 'Fallecido') {
    statusHtml = `
      <div style="background-color: #fee2e2; border: 1px solid #ef4444; color: #b91c1c; padding: 12px; border-radius: 8px; margin-bottom: 16px; font-weight: 600; display:flex; align-items:center; gap: 8px;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
          <path d="M12 2v20M8 6h8" />
        </svg>
        PACIENTE FALLECIDO — ${fmtDate(p.death_date)}
        ${p.death_notes ? `<span style="font-weight:normal; font-size: 13px;">(${escHtml(p.death_notes)})</span>` : ''}
        ${p.death_certificate_url ? `<a href="${p.death_certificate_url}" target="_blank" style="margin-left:auto; color: #991b1b; text-decoration: underline; font-size: 13px;">Ver Acta</a>` : ''}
      </div>
    `;
  } else {
    // Si es doctor, mostrar botón para marcar fallecido
    if (STATE.currentUser && STATE.currentUser.role === 'doctor') {
       statusHtml = `
         <div style="margin-bottom: 16px; text-align: right;">
           <button class="btn-outline" style="color: var(--rojo); border-color: var(--rojo);" onclick="promptMarkDeceased(${id}, '${escHtml(p.name)}')">
             Marcar como Fallecido
           </button>
         </div>
       `;
    }
  }

  document.getElementById('patient-tab-info').innerHTML = `
    <div style="padding:20px 28px; display: flex; gap: 24px; align-items: flex-start; flex-direction: column;">
      ${statusHtml}
      <div style="display: flex; gap: 24px; width: 100%;">
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
    </div>
  `;

  openModalOrig('modal-view-patient');
}

async function promptMarkDeceased(id, name) {
  const { value: formValues } = await Swal.fire({
    title: `Fallecimiento de ${escHtml(name)}`,
    html: `
      <div style="text-align: left; display: flex; flex-direction: column; gap: 12px; margin-top: 10px;">
        <div class="form-group" style="margin: 0;">
          <label class="form-label">Fecha de Fallecimiento <span class="badge-required">*</span></label>
          <input type="date" id="swal-death-date" class="form-input" max="${new Date().toISOString().split('T')[0]}" />
        </div>
        <div class="form-group" style="margin: 0;">
          <label class="form-label">Acta de Defunción (PDF o Imagen)</label>
          <input type="file" id="swal-death-cert" class="form-input" accept="image/*,application/pdf" />
        </div>
        <div class="form-group" style="margin: 0;">
          <label class="form-label">Notas Adicionales</label>
          <textarea id="swal-death-notes" class="form-input" rows="2" placeholder="Causa preliminar, lugar, etc."></textarea>
        </div>
      </div>
    `,
    showCancelButton: true,
    confirmButtonText: 'Registrar Fallecimiento',
    confirmButtonColor: '#ef4444',
    cancelButtonText: 'Cancelar',
    focusConfirm: false,
    preConfirm: () => {
      const date = document.getElementById('swal-death-date').value;
      if (!date) {
        Swal.showValidationMessage('La fecha de fallecimiento es obligatoria');
        return false;
      }
      return {
        date,
        file: document.getElementById('swal-death-cert').files[0],
        notes: document.getElementById('swal-death-notes').value
      };
    }
  });

  if (formValues) {
    const formData = new FormData();
    formData.append('death_date', formValues.date);
    if (formValues.file) formData.append('certificate', formValues.file);
    if (formValues.notes) formData.append('notes', formValues.notes);

    try {
      const res = await fetch(`/api/patients/${id}/mark-deceased`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        toast('success', data.message || 'Paciente marcado como fallecido.');
        viewPatient(id); // recargar
        if (typeof loadPatients === 'function') loadPatients();
      } else {
        Swal.fire('Error', data.error || 'No se pudo procesar la solicitud.', 'error');
      }
    } catch (e) {
      console.error(e);
      Swal.fire('Error', 'Error de red.', 'error');
    }
  }
}

async function loadPatientVitals(id) {
  if (!id) return;
  const el = document.getElementById('patient-vitals-content');
  el.innerHTML = '<div class="loading-state"><div class="spinner-ring"></div></div>';
  const data = await api('GET', `/api/patients/${id}/vitals-history?limit=10`);
  if (!data.success || !data.vitals_history?.length) {
    el.innerHTML = '<div class="empty-state"><span>Sin registros de vitales.</span></div>'; return;
  }
  const headers = ['Fecha','Temp','SpO2','PAS','PAD','FC','FR','Peso','Altura','IMC'];
  const rows = data.vitals_history.map(r => {
    const c = r.vitals || {};
    return `<tr>
      <td>${r.visit_date || '—'}</td>
      <td>${c.temperatura ?? '—'}</td><td>${c.spo2 ?? '—'}</td>
      <td>${c.pas ?? '—'}</td><td>${c.pad ?? '—'}</td>
      <td>${c.fc ?? '—'}</td><td>${c.fr ?? '—'}</td>
      <td>${c.peso ?? '—'}</td><td>${c.altura ?? '—'}</td>
      <td>${c.imc ?? '—'}</td>
    </tr>`;
  }).join('');
  el.innerHTML = `<div class="table-responsive" style="width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch;"><table class="vitals-history-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows}</tbody></table></div>`;
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
  // Ocultar de la sala de espera las citas que ya están completadas o canceladas
  apps = apps.filter(a => a.status !== 'completada' && a.status !== 'cancelada');
  
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
let CURRENT_SIDEBAR_ORDERS = { admin: [], doctor: [], secretaria: [] };

function renderSidebarOrderEditor(role) {
  const container = document.getElementById(`editor-list-${role}`);
  if (!container) return;
  
  const order = CURRENT_SIDEBAR_ORDERS[role];
  let html = '';
  
  order.forEach((tabId, index) => {
    const item = SIDEBAR_ITEMS[tabId];
    if (!item) return;
    
    const isFirst = index === 0;
    const isLast = index === order.length - 1;
    
    html += `
      <div class="order-card">
        <div class="order-card-info">
          ${item.icon}
          <span>${item.label}</span>
        </div>
        <div class="order-card-actions">
          <button type="button" class="btn-order-action" ${isFirst ? 'disabled' : ''} onclick="moveSidebarTab('${role}', ${index}, -1)">▲</button>
          <button type="button" class="btn-order-action" ${isLast ? 'disabled' : ''} onclick="moveSidebarTab('${role}', ${index}, 1)">▼</button>
        </div>
      </div>
    `;
  });
  
  container.innerHTML = html;
  
  const input = document.getElementById(`cfg-sidebar-order-${role}`);
  if (input) {
    input.value = order.join(',');
  }
}

function moveSidebarTab(role, index, direction) {
  const order = CURRENT_SIDEBAR_ORDERS[role];
  const targetIndex = index + direction;
  if (targetIndex < 0 || targetIndex >= order.length) return;
  
  const temp = order[index];
  order[index] = order[targetIndex];
  order[targetIndex] = temp;
  
  renderSidebarOrderEditor(role);
}

async function loadClinicSettings() {
  const data = await api('GET', '/api/settings/all');
  if (!data.success) return;
  const s = data.settings || {};
  
  const fields = {
    'cfg-clinic-name':            'clinic_name',
    'cfg-clinic-address':       'clinic_address',
    'cfg-clinic-phone':         'clinic_phone',
    'cfg-clinic-rnc':           'clinic_rnc',
    'cfg-clinic-email':         'clinic_email',
    'cfg-ui-primary-color':     'ui_primary_color',
    'cfg-sidebar-order-admin':  'sidebar_order_admin',
    'cfg-sidebar-order-doctor': 'sidebar_order_doctor',
    'cfg-sidebar-order-secretaria': 'sidebar_order_secretaria',
    'cfg-max-login-attempts':    'max_login_attempts',
    'cfg-lockout-minutes':       'lockout_minutes',
    'cfg-session-timeout-hours': 'session_timeout_hours',
  };
  
  Object.entries(fields).forEach(([elId, key]) => {
    const el = document.getElementById(elId);
    if (el) el.value = s[key] || '';
  });
  
  const checkbox = document.getElementById('cfg-allow-doctor-billing');
  if (checkbox) {
    checkbox.checked = s.allow_doctor_billing === 'true';
  }
  
  const secRepCheckbox = document.getElementById('cfg-enable-secretaria-reports');
  if (secRepCheckbox) {
    secRepCheckbox.checked = s.enable_secretaria_reports === '1';
  }

  // Cargar visual editor del sidebar
  const defaultOrders = {
    admin: ['admin-dashboard', 'admin-doctors', 'admin-patients', 'admin-history', 'billing', 'reports', 'admin-bayes', 'admin-users', 'admin-settings', 'admin-audit'],
    doctor: ['dashboard', 'appointments', 'waiting-room', 'patients', 'diagnose', 'history', 'simulator', 'reports'],
    secretaria: ['waiting-room', 'appointments', 'patients', 'billing']
  };
  
  const allowDoctorBilling = s.allow_doctor_billing === 'true';
  if (allowDoctorBilling && !defaultOrders.doctor.includes('billing')) {
    defaultOrders.doctor.push('billing');
  }

  CURRENT_SIDEBAR_ORDERS.admin = s.sidebar_order_admin ? s.sidebar_order_admin.split(',').map(x => x.trim()) : defaultOrders.admin;
  CURRENT_SIDEBAR_ORDERS.doctor = s.sidebar_order_doctor ? s.sidebar_order_doctor.split(',').map(x => x.trim()) : defaultOrders.doctor;
  CURRENT_SIDEBAR_ORDERS.secretaria = s.sidebar_order_secretaria ? s.sidebar_order_secretaria.split(',').map(x => x.trim()) : defaultOrders.secretaria;

  if (allowDoctorBilling && !CURRENT_SIDEBAR_ORDERS.doctor.includes('billing')) {
    CURRENT_SIDEBAR_ORDERS.doctor.push('billing');
  } else if (!allowDoctorBilling && CURRENT_SIDEBAR_ORDERS.doctor.includes('billing')) {
    CURRENT_SIDEBAR_ORDERS.doctor = CURRENT_SIDEBAR_ORDERS.doctor.filter(x => x !== 'billing');
  }

  const enableSecretariaReports = s.enable_secretaria_reports === '1';
  if (enableSecretariaReports && !CURRENT_SIDEBAR_ORDERS.secretaria.includes('reports')) {
    CURRENT_SIDEBAR_ORDERS.secretaria.push('reports');
  } else if (!enableSecretariaReports && CURRENT_SIDEBAR_ORDERS.secretaria.includes('reports')) {
    CURRENT_SIDEBAR_ORDERS.secretaria = CURRENT_SIDEBAR_ORDERS.secretaria.filter(x => x !== 'reports');
  }

  renderSidebarOrderEditor('admin');
  renderSidebarOrderEditor('doctor');
  renderSidebarOrderEditor('secretaria');
}

async function saveClinicSettings() {
  const fields = {
    'cfg-clinic-name':          'clinic_name',
    'cfg-clinic-address':       'clinic_address',
    'cfg-clinic-phone':         'clinic_phone',
    'cfg-clinic-rnc':           'clinic_rnc',
    'cfg-clinic-email':         'clinic_email',
    'cfg-ui-primary-color':     'ui_primary_color',
    'cfg-sidebar-order-admin':  'sidebar_order_admin',
    'cfg-sidebar-order-doctor': 'sidebar_order_doctor',
    'cfg-sidebar-order-secretaria': 'sidebar_order_secretaria',
    'cfg-max-login-attempts':    'max_login_attempts',
    'cfg-lockout-minutes':       'lockout_minutes',
    'cfg-session-timeout-hours': 'session_timeout_hours',
  };
  
  const payload = {};
  Object.entries(fields).forEach(([elId, key]) => {
    const el = document.getElementById(elId);
    if (el) payload[key] = el.value.trim();
  });
  
  const checkbox = document.getElementById('cfg-allow-doctor-billing');
  if (checkbox) {
    payload['allow_doctor_billing'] = checkbox.checked ? 'true' : 'false';
  }
  
  const secRepCb = document.getElementById('cfg-enable-secretaria-reports');
  if (secRepCb) {
    payload['enable_secretaria_reports'] = secRepCb.checked ? '1' : '0';
  }

  const btn = document.querySelector('button[onclick="saveClinicSettings()"]');
  setButtonLoading(btn, true);

  try {
    const res = await api('POST', '/api/settings/update', payload);
    if (res.success) {
      toast('success', 'Ajustes guardados correctamente.');
      await loadSystemConfig();
    } else {
      toast('error', res.error || 'Error al guardar ajustes.');
    }
  } finally {
    setButtonLoading(btn, false);
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

function sanitize_dgii_url(url) {
  if (!url) return '';
  let cleanUrl = String(url).trim();
  cleanUrl = cleanUrl.replace(/[\r\n\t]/g, '').trim();

  while (cleanUrl.endsWith('%20') || cleanUrl.endsWith(' ')) {
    if (cleanUrl.endsWith('%20')) {
      cleanUrl = cleanUrl.slice(0, -3).trim();
    } else {
      cleanUrl = cleanUrl.trim();
    }
  }

  cleanUrl = cleanUrl.replace(/([?&][a-zA-Z0-9_]+)=(?:%20|\s+)(?=&|$)/g, '$1=');

  if (cleanUrl.includes("fc.dgii.gov.do") && !cleanUrl.includes("consultatimbrefc")) {
    cleanUrl = cleanUrl.replace("fc.dgii.gov.do", "ecf.dgii.gov.do");
  }

  return cleanUrl;
}

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

// Extracted simulatePayPalPayment to simulator.js

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
  const fullnameInput = document.getElementById('my-fullname');
  const fullname = fullnameInput ? fullnameInput.value.trim().toUpperCase() : '';
  if (fullnameInput) fullnameInput.value = fullname;
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

  const btn = document.querySelector('#modal-profile .modal-footer .btn-primary');
  setButtonLoading(btn, true);

  try {
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
  } finally {
    setButtonLoading(btn, false);
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

  const btn = document.querySelector('button[onclick="saveManualDiagnosis(' + createPrescription + ')"]');
  setButtonLoading(btn, true);

  try {
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
  } finally {
    setButtonLoading(btn, false);
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
    const pendingAmount = p.pending_amount !== undefined ? p.pending_amount : 3000.00;
    let amountHtml = `RD$ ${pendingAmount.toLocaleString('es-DO', { minimumFractionDigits: 2 })}`;
    if (pendingAmount < 3000.00) {
      amountHtml += `<div style="font-size:11px; color:var(--text-muted); font-weight:normal; margin-top:2px;">(Faltante de RD$ 3,000.00)</div>`;
    }
    return `
      <tr>
        <td>${date}</td>
        <td style="font-weight:600; color:var(--text-primary);">${escHtml(p.patient_name)}</td>
        <td>${escHtml(p.patient_cedula || '—')}</td>
        <td>Dr. ${escHtml(p.doctor_fullname)}</td>
        <td style="color:var(--brand-light); font-weight:600;">${amountHtml}</td>
        <td>
          <button class="btn-primary" style="font-size:12px; padding:6px 12px;" onclick="openChargeModal(${p.visit_id}, '${escHtml(p.patient_name)}', ${p.patient_id}, ${pendingAmount})">
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
    STATE.invoices = [];
    el.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">No hay facturas registradas.</td></tr>';
    return;
  }

  STATE.invoices = res.invoices;
  renderBillingHistory(res.invoices);
}

function renderBillingHistory(invoices) {
  const el = document.getElementById('billing-history-list');
  if (!el) return;
  if (!invoices || !invoices.length) {
    el.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 20px;">No se encontraron facturas.</td></tr>';
    return;
  }

  el.innerHTML = invoices.map(i => {
    const date = i.created_at ? i.created_at.substring(0, 16).replace('T', ' ') : '—';
    const client = i.patient_name || 'Médico (Suscripción)';
    const paymentMethodText = i.payment_method === 'tarjeta' ? '💳 Tarjeta' : '💵 Efectivo';
    
    // Links de acciones
    const pdfLink = `<a href="/api/pdf/invoice/${i.id}" target="_blank" class="btn-icon" title="Ver Factura PDF" style="color:var(--brand-light);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg></a>`;

    const cleanDgiiUrl = sanitize_dgii_url(i.dgii_url);
    const dgiiLink = cleanDgiiUrl 
      ? `<a href="${cleanDgiiUrl}" target="_blank" rel="noreferrer noopener" class="btn-icon" title="Ver Timbre en DGII" style="color:var(--brand-light);"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg></a>`
      : '';

    // Credit Note Button E34
    // E34 can be applied if tipo_ecf starts with E31 or E32 (or is null/empty for legacy consultations) and it is not already a credit note and has not been cancelled yet
    const isE31orE32 = (i.tipo_ecf && (i.tipo_ecf.startsWith('E31') || i.tipo_ecf.startsWith('E32'))) || (!i.tipo_ecf && i.invoice_type === 'consulta');
    const showCreditNoteBtn = isE31orE32 && i.invoice_type !== 'nota_credito' && !i.is_cancelled;
    const creditNoteBtn = showCreditNoteBtn
      ? `<button class="btn-icon danger" title="Emitir Nota de Crédito (E34)" onclick="openCreditNoteModal(${i.id}, '${escHtml(i.encf)}', '${escHtml(client)}', ${i.total}, '${escHtml(i.created_at)}', '${escHtml(i.tipo_ecf || 'E32')}')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
         </button>`
      : '';

    // Class and colors for different invoices
    let badgeClass = 'badge-azul';
    if (i.invoice_type === 'suscripcion') badgeClass = 'badge-verde';
    else if (i.invoice_type === 'nota_credito') badgeClass = 'badge-rojo';

    const statusText = i.is_cancelled ? 'Anulada' : escHtml(i.estado);
    const statusBadgeClass = i.is_cancelled ? 'badge-rojo' : 'badge-verde';

    return `
      <tr ondblclick="window.open('/api/pdf/invoice/${i.id}', '_blank')" style="cursor: pointer; ${i.is_cancelled ? 'opacity: 0.65; background-color: rgba(0,0,0,0.02);' : ''}">
        <td>${date}</td>
        <td><span class="badge ${badgeClass}" style="font-size:10px;">${i.invoice_type.toUpperCase()} ${i.tipo_ecf || ''}</span></td>
        <td style="font-weight:500; ${i.is_cancelled ? 'text-decoration: line-through;' : ''}">${escHtml(client)}</td>
        <td>${paymentMethodText}</td>
        <td style="font-family:var(--mono); font-size:12px; color:var(--text-primary); font-weight:600; ${i.is_cancelled ? 'text-decoration: line-through;' : ''}">${escHtml(i.encf || '—')}</td>
        <td><span class="badge ${statusBadgeClass}" style="font-size:10px;">${statusText}</span></td>
        <td style="font-weight:600; color:${i.total < 0 || i.is_cancelled ? 'var(--red)' : 'var(--text-primary)'}; ${i.is_cancelled ? 'text-decoration: line-through;' : ''}">
          RD$ ${i.total.toLocaleString('es-DO', { minimumFractionDigits: 2 })}
          ${(i.balance_due > 0 && !i.is_cancelled && i.invoice_type !== 'nota_credito') ? `
            <div style="font-size: 11px; color: var(--text-secondary); font-weight: normal; margin-top: 4px;">
              <span style="color:var(--brand-light);">Cobrado: RD$ ${i.amount_paid.toLocaleString('es-DO', { minimumFractionDigits: 2 })}</span><br/>
              <span style="color:var(--rojo);">Faltante: RD$ ${i.balance_due.toLocaleString('es-DO', { minimumFractionDigits: 2 })}</span>
            </div>
          ` : ''}
        </td>
        <td>
          <div style="display:flex; gap:8px; align-items:center;">
            ${pdfLink}
            ${dgiiLink}
            ${creditNoteBtn}
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function filterBillingHistory() {
  const query = document.getElementById('billing-history-search').value.toLowerCase().trim();
  if (!STATE.invoices) return;
  if (!query) {
    renderBillingHistory(STATE.invoices);
    return;
  }

  const filtered = STATE.invoices.filter(i => {
    const encf = (i.encf || '').toLowerCase();
    const client = (i.patient_name || 'Médico (Suscripción)').toLowerCase();
    const date = (i.created_at || '').toLowerCase();
    const payment = (i.payment_method === 'tarjeta' ? 'tarjeta' : 'efectivo').toLowerCase();
    const tipo = (i.tipo_ecf || '').toLowerCase();
    const typeStr = (i.invoice_type || '').toLowerCase();
    return encf.includes(query) || client.includes(query) || date.includes(query) || payment.includes(query) || tipo.includes(query) || typeStr.includes(query);
  });

  renderBillingHistory(filtered);
}

function openCreditNoteModal(invoiceId, encf, clientName, totalAmount, dateStr, tipoEcf) {
  document.getElementById('cn-invoice-id').value = invoiceId;
  document.getElementById('cn-original-total').value = totalAmount;
  document.getElementById('cn-original-tipo-ecf').value = tipoEcf;
  document.getElementById('cn-original-encf').textContent = encf;
  document.getElementById('cn-client-name').textContent = clientName;
  document.getElementById('cn-original-total-text').textContent = `RD$ ${totalAmount.toLocaleString('es-DO', { minimumFractionDigits: 2 })}`;

  // Default behavior: Anulación total
  const codeSelect = document.getElementById('cn-modification-code');
  codeSelect.value = '1';
  
  const amountInput = document.getElementById('cn-credit-amount');
  amountInput.value = totalAmount.toFixed(2);
  amountInput.disabled = true;

  const conceptInput = document.getElementById('cn-concept');
  conceptInput.value = 'Anulacion total de factura';

  openModal('modal-credit-note');
}

function onCreditNoteTypeChange() {
  const code = document.getElementById('cn-modification-code').value;
  const amountInput = document.getElementById('cn-credit-amount');
  const conceptInput = document.getElementById('cn-concept');
  const originalTotal = parseFloat(document.getElementById('cn-original-total').value || '0');

  if (code === '1') {
    // Anulación
    amountInput.value = originalTotal.toFixed(2);
    amountInput.disabled = true;
    conceptInput.value = 'Anulacion total de factura';
  } else {
    // Ajuste / Descuento
    amountInput.disabled = false;
    amountInput.value = '';
    amountInput.focus();
    conceptInput.value = 'Ajuste de monto / Devolucion de servicios';
  }
}

async function submitCreditNote() {
  const invoiceId = document.getElementById('cn-invoice-id').value;
  const codigoModificacion = document.getElementById('cn-modification-code').value;
  const amountVal = document.getElementById('cn-credit-amount').value;
  const concepto = document.getElementById('cn-concept').value.trim();
  const originalTotal = parseFloat(document.getElementById('cn-original-total').value || '0');

  if (!invoiceId) return;
  if (!concepto) {
    toast('error', 'El concepto es requerido.');
    return;
  }

  let montoCredito = parseFloat(amountVal);
  if (isNaN(montoCredito) || montoCredito <= 0) {
    toast('error', 'El monto a devolver debe ser un número válido mayor a 0.');
    return;
  }

  if (montoCredito > originalTotal) {
    toast('error', 'El monto de la nota de crédito no puede exceder el total original.');
    return;
  }

  const btn = document.querySelector('#modal-credit-note .modal-footer .btn-primary');
  setButtonLoading(btn, true);

  try {
    toast('info', 'Emitiendo Nota de Crédito y firmando e-CF con la DGII...');
    
    const res = await api('POST', '/api/billing/credit-note', {
      invoice_id: parseInt(invoiceId, 10),
      codigo_modificacion: codigoModificacion,
      monto_credito: montoCredito,
      concepto: concepto
    });

    if (res.success) {
      toast('success', '¡Nota de Crédito emitida y aceptada con éxito!');
      closeModal('modal-credit-note');
      loadBillingTab();
    } else {
      toast('error', res.error || 'Error al emitir la Nota de Crédito.');
    }
  } finally {
    setButtonLoading(btn, false);
  }
}

function toggleChargeEcfFields() {
  const type = document.getElementById('charge-ecf-type').value;
  const fields = document.getElementById('charge-ecf-31-fields');
  
  const subtotalEl = document.getElementById('charge-breakdown-subtotal');
  const itbisEl = document.getElementById('charge-breakdown-itbis');
  const totalEl = document.getElementById('charge-breakdown-total');
  const subtotalLabel = document.getElementById('charge-breakdown-subtotal-label');
  const itbisLabel = document.getElementById('charge-breakdown-itbis-label');

  // Obtener el monto pendiente actual a cobrar
  const pendingAmount = parseFloat(document.getElementById('modal-charge-visit').getAttribute('data-pending-amount') || '3000.00');

  if (type === '31') {
    if (fields) fields.style.display = 'block';
    
    // E31 details: Subtotal (Base) = pendingAmount / 1.18, ITBIS = pendingAmount * 18/118, Total = pendingAmount
    const itbis = pendingAmount * 18 / 118;
    const subtotal = pendingAmount - itbis;

    if (subtotalLabel) subtotalLabel.textContent = 'Subtotal (Base Gravable):';
    if (subtotalEl) subtotalEl.textContent = `RD$ ${subtotal.toLocaleString('es-DO', { minimumFractionDigits: 2 })}`;
    if (itbisLabel) itbisLabel.textContent = 'ITBIS (18%):';
    if (itbisEl) itbisEl.textContent = `RD$ ${itbis.toLocaleString('es-DO', { minimumFractionDigits: 2 })}`;
    if (totalEl) totalEl.textContent = `RD$ ${pendingAmount.toLocaleString('es-DO', { minimumFractionDigits: 2 })}`;
  } else {
    if (fields) fields.style.display = 'none';
    
    // E32 details: Subtotal (Exento) = pendingAmount, ITBIS = 0.00, Total = pendingAmount
    if (subtotalLabel) subtotalLabel.textContent = 'Subtotal (Monto Exento):';
    if (subtotalEl) subtotalEl.textContent = `RD$ ${pendingAmount.toLocaleString('es-DO', { minimumFractionDigits: 2 })}`;
    if (itbisLabel) itbisLabel.textContent = 'ITBIS (0%):';
    if (itbisEl) itbisEl.textContent = 'RD$ 0.00';
    if (totalEl) totalEl.textContent = `RD$ ${pendingAmount.toLocaleString('es-DO', { minimumFractionDigits: 2 })}`;
  }
}

function clearChargeBillingFields() {
  document.getElementById('charge-rnc').value = '';
  document.getElementById('charge-razon-social').value = '';
  document.getElementById('charge-correo').value = '';
  document.getElementById('charge-is-credit').checked = false;
  toggleCreditFields();
}

let isRncLookupInProgress = false;
async function lookupChargeRnc(rncVal) {
  const rnc = (rncVal || '').replace(/-/g, '').trim();
  if (!rnc || (rnc.length !== 9 && rnc.length !== 11)) return;
  if (isRncLookupInProgress) return;

  isRncLookupInProgress = true;
  toast('info', 'Buscando RNC/Cédula en la DGII...');
  try {
    const res = await api('GET', `/api/patients/consulta-rnc/${rnc}`);
    if (res.success && res.data) {
      toast('success', 'Contribuyente encontrado.');
      if (res.data.nombre) {
        document.getElementById('charge-razon-social').value = res.data.nombre;
      }
    } else {
      toast('warning', res.error || 'RNC/Cédula no encontrado en la DGII.');
    }
  } catch (err) {
    console.error(err);
    toast('error', 'Error al consultar RNC/Cédula.');
  } finally {
    isRncLookupInProgress = false;
  }
}

async function openChargeModal(visitId, patientName, patientId, pendingAmount) {
  pendingAmount = pendingAmount !== undefined ? parseFloat(pendingAmount) : 3000.00;
  
  document.getElementById('charge-visit-id').value = visitId;
  document.getElementById('charge-patient-id').value = patientId || '';
  document.getElementById('charge-patient-name').textContent = patientName;
  document.getElementById('charge-payment-method').value = 'efectivo';
  document.getElementById('charge-ecf-type').value = '32';
  
  // Guardamos el total actual a cobrar en el modal
  document.getElementById('modal-charge-visit').setAttribute('data-pending-amount', pendingAmount);
  
  toggleChargeEcfFields();
  clearChargeBillingFields();

  if (patientId) {
    try {
      const data = await api('GET', `/api/patients/${patientId}/billing-info`);
      if (data.success && data.billing_info) {
        document.getElementById('charge-rnc').value = data.billing_info.rnc || '';
        document.getElementById('charge-razon-social').value = data.billing_info.razon_social || '';
        document.getElementById('charge-correo').value = data.billing_info.correo || '';
        
        // Autoseleccionar E31 si el paciente ya tiene datos de facturación registrados
        document.getElementById('charge-ecf-type').value = '31';
        toggleChargeEcfFields();
      }
    } catch (err) {
      console.error('Error al obtener info de facturación:', err);
    }
  }

  openModal('modal-charge-visit');
}

function toggleCreditFields() {
  const isCredit = document.getElementById('charge-is-credit').checked;
  const fields = document.getElementById('charge-credit-fields');
  fields.style.display = isCredit ? 'flex' : 'none';
  if (!isCredit) {
    document.getElementById('charge-amount-paid').value = '';
    document.getElementById('charge-due-date').value = '';
  }
  calcChargeCreditBalance();
}

function calcChargeCreditBalance() {
  const total = parseFloat(document.getElementById('modal-charge-visit').getAttribute('data-pending-amount') || '3000.00');
  let paid = parseFloat(document.getElementById('charge-amount-paid').value);
  if (isNaN(paid)) paid = 0;
  if (paid < 0) paid = 0;
  if (paid > total) paid = total;
  
  const balance = total - paid;
  document.getElementById('charge-balance-due').textContent = `RD$ ${balance.toFixed(2)}`;
}

async function submitChargeVisit() {
  const visitId = document.getElementById('charge-visit-id').value;
  const paymentMethod = document.getElementById('charge-payment-method').value;
  const tipoEcf = document.getElementById('charge-ecf-type').value;

  if (!visitId) return;

  const payload = {
    visit_id: parseInt(visitId, 10),
    payment_method: paymentMethod,
    tipo_ecf: tipoEcf,
    is_credit: document.getElementById('charge-is-credit').checked
  };

  if (payload.is_credit) {
    const amtPaid = document.getElementById('charge-amount-paid').value;
    const dueDate = document.getElementById('charge-due-date').value;
    payload.amount_paid = amtPaid ? parseFloat(amtPaid) : 0;
    if (dueDate) payload.due_date = dueDate;
  }

  if (tipoEcf === '31') {
    const rnc = document.getElementById('charge-rnc').value.trim();
    const razonSocial = document.getElementById('charge-razon-social').value.trim();
    const correo = document.getElementById('charge-correo').value.trim();

    if (!rnc || !razonSocial) {
      toast('error', 'El RNC y la Razón Social son requeridos para Crédito Fiscal (E31).');
      return;
    }
    payload.rnc_comprador = rnc;
    payload.razon_social_comprador = razonSocial;
    payload.correo_comprador = correo;
  }

  const btn = document.querySelector('#modal-charge-visit .modal-footer .btn-primary');
  setButtonLoading(btn, true);

  try {
    toast('info', 'Procesando pago y firmando e-CF con DGII...');
    const res = await api('POST', '/api/billing/charge', payload);

    if (res.success) {
      toast('success', '¡Pago procesado y e-CF aceptado!');
      closeModal('modal-charge-visit');

      // Llenar datos de éxito
      document.getElementById('res-invoice-encf').textContent = res.invoice.encf || '—';
      document.getElementById('res-invoice-code').textContent = res.invoice.codigo_seguridad || '—';
      document.getElementById('res-invoice-status').textContent = res.invoice.estado || 'Aceptado';
      
      const printBtn = document.getElementById('btn-print-invoice-pdf');
      if (printBtn && res.invoice_id) {
        printBtn.setAttribute('data-invoice-id', res.invoice_id);
      }

      const linkEl = document.getElementById('res-invoice-dgii-link');
      const cleanDgiiUrlRes = sanitize_dgii_url(res.invoice.dgii_url);
      if (cleanDgiiUrlRes) {
        linkEl.href = cleanDgiiUrlRes;
        linkEl.style.display = 'block';
      } else {
        linkEl.style.display = 'none';
      }

      openModal('modal-invoice-result');
      loadBillingTab();
    } else {
      toast('error', res.error || 'Error al procesar la factura electrónica.');
    }
  } finally {
    setButtonLoading(btn, false);
  }
}

function printInvoicePDF() {
  const printBtn = document.getElementById('btn-print-invoice-pdf');
  const invoiceId = printBtn ? printBtn.getAttribute('data-invoice-id') : null;
  if (!invoiceId) {
    toast('error', 'No se encontró el ID de la factura para imprimir.');
    return;
  }
  window.open(`/api/pdf/invoice/${invoiceId}`, '_blank');
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
    <div class="patient-select-item" ondblclick="selectPatientForAppointment(${p.id}, '${p.name.replace(/'/g, "\\'")}')"
      style="padding: 12px 16px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.15s;">
      <div style="font-weight: 600; color: var(--text-primary);">${p.name}</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 3px;">Cédula: ${p.cedula || '—'}</div>
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
    <div class="patient-select-item" ondblclick="selectDoctorForAppointment(${d.id}, '${(d.full_name || d.username).replace(/'/g, "\\'")}')"
      style="padding: 12px 16px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.15s;">
      <div style="font-weight: 600; color: var(--text-primary);">${d.full_name || d.username}</div>
      <div style="font-size: 12px; color: var(--text-muted); margin-top: 3px;">${d.especialidad || 'Sin especialidad'} | Matrícula: ${d.matricula || '—'}</div>
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

// ─── CALCULADORA DE APOYO (NOTA DE CRÉDITO) ──────────────────────────────────
let calcExpression = '';
let calcResultCalculated = false;

function pressCalc(val) {
  const display = document.getElementById('calc-display');
  const history = document.getElementById('calc-history');
  if (!display) return;

  if (val === 'C') {
    calcExpression = '';
    display.textContent = '0';
    history.textContent = '';
    calcResultCalculated = false;
  } else if (val === 'DEL') {
    if (calcResultCalculated) {
      calcExpression = '';
      display.textContent = '0';
      history.textContent = '';
      calcResultCalculated = false;
    } else {
      calcExpression = calcExpression.slice(0, -1);
      display.textContent = calcExpression || '0';
    }
  } else if (val === '=') {
    try {
      if (!calcExpression) return;
      const cleanExpr = calcExpression.replace(/×/g, '*').replace(/÷/g, '/');
      // Evaluación matemática segura: solo permitimos números, operadores básicos y paréntesis
      if (/^[0-9.+\-*/\s()]+$/.test(cleanExpr)) {
        const res = new Function(`return (${cleanExpr})`)();
        history.textContent = calcExpression + ' =';
        display.textContent = Number(res.toFixed(4)).toString();
        calcExpression = display.textContent;
        calcResultCalculated = true;
      } else {
        display.textContent = 'Error';
        calcExpression = '';
      }
    } catch (e) {
      display.textContent = 'Error';
      calcExpression = '';
    }
  } else {
    if (calcResultCalculated) {
      if (['+', '-', '*', '/'].includes(val)) {
        calcResultCalculated = false;
      } else {
        calcExpression = '';
        calcResultCalculated = false;
      }
    }
    // Evitar acumulaciones inválidas como operadores consecutivos
    if (['+', '-', '*', '/'].includes(val) && ['+', '-', '*', '/'].includes(calcExpression.slice(-1))) {
      calcExpression = calcExpression.slice(0, -1);
    }
    calcExpression += val;
    display.textContent = calcExpression;
  }
}

function applyCalcToAmount() {
  const display = document.getElementById('calc-display');
  const amountInput = document.getElementById('cn-credit-amount');
  if (!display || !amountInput) return;
  const val = parseFloat(display.textContent);
  if (!isNaN(val) && val >= 0) {
    amountInput.value = val.toFixed(2);
    // Disparar evento change si es necesario para lógica reactiva
    amountInput.dispatchEvent(new Event('input'));
  }
}


// =============================================================================
// CONSULTAS Y REPORTES
// =============================================================================

function loadReportsTab() {
  const reportsTypeSelect = document.getElementById('reports-type');
  if (!reportsTypeSelect) return;

  const role = STATE.user ? STATE.user.role : '';
  
  // Limpiar selector y rellenar según permisos
  reportsTypeSelect.innerHTML = '';
  
  // Configurar las opciones basadas en el rol
  let options = [];
  
  if (role === 'doctor') {
    options = [
      { value: 'agenda', text: 'Agenda y Citas' },
      { value: 'recurrent', text: 'Pacientes Recurrentes' },
      { value: 'ai-comparison', text: 'Comparación IA vs Médico' },
      { value: 'prescriptions', text: 'Prescripciones Emitidas' },
      { value: 'activity', text: 'Mi Actividad' },
      { value: 'billing', text: 'Mis Cobros y Facturación' }
    ];
  } else {
    // Admin o Secretaria
    options = [
      { value: 'agenda', text: 'Agenda y Citas' },
      { value: 'recurrent', text: 'Pacientes Recurrentes' },
      { value: 'ai-comparison', text: 'Comparación IA vs Médico' },
      { value: 'prescriptions', text: 'Prescripciones Emitidas' },
      { value: 'activity', text: 'Actividad de Doctores' },
      { value: 'billing', text: 'Facturación General' }
    ];
    if (role === 'admin') {
      options.push({ value: 'audit', text: 'Registro de Auditoría' });
    }
    
    // Cargar selector de doctores
    const doctorFilter = document.getElementById('reports-filter-doctor');
    const doctorSelect = document.getElementById('reports-doctor-select');
    if (doctorFilter && doctorSelect) {
      doctorFilter.style.display = 'block';
      api('GET', '/api/reports/doctor-list').then(res => {
        if (res.success) {
          let html = '<option value="">Todos los doctores / General</option>';
          res.doctors.forEach(d => {
            html += `<option value="${d.id}">${d.full_name} ${d.especialidad ? `(${d.especialidad})` : ''}</option>`;
          });
          doctorSelect.innerHTML = html;
        }
      });
    }
  }

  options.forEach(opt => {
    reportsTypeSelect.innerHTML += `<option value="${opt.value}">${opt.text}</option>`;
  });

  // Fechas por defecto: primer día del mes actual hasta hoy
  const now = new Date();
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
  const formatDate = (d) => {
    const month = '' + (d.getMonth() + 1);
    const day = '' + d.getDate();
    const year = d.getFullYear();
    return [year, month.padStart(2, '0'), day.padStart(2, '0')].join('-');
  };

  document.getElementById('reports-date-from').value = formatDate(firstDay);
  document.getElementById('reports-date-to').value = formatDate(now);

  onReportTypeChange();
  
  // Resetear interfaz
  document.getElementById('reports-stats-grid').style.display = 'none';
  document.getElementById('reports-stats-grid').innerHTML = '';
  document.getElementById('reports-table-wrap').innerHTML = `
    <div class="empty-state">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
        <line x1="9" y1="9" x2="15" y2="9"/>
        <line x1="9" y1="13" x2="15" y2="13"/>
        <line x1="9" y1="17" x2="13" y2="17"/>
      </svg>
      <span>Selecciona un reporte y presiona "Generar Reporte" para ver los resultados.</span>
    </div>`;
}

function onReportTypeChange() {
  const type = document.getElementById('reports-type').value;
  
  // Ocultar todos los subfiltros
  document.getElementById('reports-filter-visit-type').style.display = 'none';
  document.getElementById('reports-filter-invoice-type').style.display = 'none';
  document.getElementById('reports-filter-audit-action').style.display = 'none';
  document.getElementById('reports-filter-audit-entity').style.display = 'none';

  // Mostrar los específicos
  if (type === 'visits') {
    document.getElementById('reports-filter-visit-type').style.display = 'block';
  } else if (type === 'billing') {
    document.getElementById('reports-filter-invoice-type').style.display = 'block';
  } else if (type === 'audit') {
    document.getElementById('reports-filter-audit-action').style.display = 'block';
    document.getElementById('reports-filter-audit-entity').style.display = 'block';
  }
}

async function generateReport() {
  const btn = document.getElementById('btn-generate-report');
  const type = document.getElementById('reports-type').value;
  const dateFrom = document.getElementById('reports-date-from').value;
  const dateTo = document.getElementById('reports-date-to').value;

  if (!type) return;

  setButtonLoading(btn, true, 'Generando...');

  let url = `/api/reports/`;
  const params = new URLSearchParams();
  if (dateFrom) params.append('date_from', dateFrom);
  if (dateTo) params.append('date_to', dateTo);
  
  const doctorFilter = document.getElementById('reports-filter-doctor');
  const doctorSelect = document.getElementById('reports-doctor-select');
  if (doctorFilter && doctorFilter.style.display !== 'none' && doctorSelect.value) {
    params.append('doctor_id', doctorSelect.value);
  }

  if (type === 'agenda') {
    url += 'agenda';
  } else if (type === 'recurrent') {
    url += 'recurrent';
  } else if (type === 'ai-comparison') {
    url += 'ai-comparison';
  } else if (type === 'prescriptions') {
    url += 'prescriptions';
  } else if (type === 'activity') {
    url += 'activity';
  } else if (type === 'billing') {
    url += 'billing';
    const it = document.getElementById('reports-val-invoice-type').value;
    if (it) params.append('invoice_type', it);
  } else if (type === 'audit') {
    url = '/api/audit_logs'; // Usar el existente
    const action = document.getElementById('reports-val-audit-action').value;
    const entity = document.getElementById('reports-val-audit-entity').value.trim();
    if (action) params.append('action', action);
    if (entity) params.append('entity', entity);
  }

  const queryString = params.toString();
  const finalUrl = url + (queryString ? `?${queryString}` : '');

  try {
    const res = await api('GET', finalUrl);
    if (res.success) {
      renderReportStats(type, res);
      renderReportTable(type, res);
      toast('success', 'Reporte generado correctamente');
    } else {
      if (res.error === 'subscription_required') {
        toast('error', res.message || 'Se requiere una suscripción VIP activa.');
      } else {
        toast('error', res.error || 'Error al generar reporte');
      }
    }
  } catch (err) {
    toast('error', 'Error al consultar la base de datos');
  } finally {
    setButtonLoading(btn, false);
  }
}

function renderReportStats(type, res) {
  const statsGrid = document.getElementById('reports-stats-grid');
  statsGrid.innerHTML = '';
  statsGrid.style.display = 'none';

  let cardsHtml = '';

  // ── Tipos nuevos ─────────────────────────────────────────────────────────
  if (type === 'agenda') {
    const data = res.agenda || [];
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${data.length}</div>
        <div class="stat-label">Citas en período</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${data.filter(d => d.appointment_status === 'atendido').length}</div>
        <div class="stat-label">Atendidas</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="color:var(--danger)">${data.filter(d => d.appointment_status === 'cancelada').length}</div>
        <div class="stat-label">Canceladas</div>
      </div>`;
  } else if (type === 'recurrent') {
    const data = res.recurrent_patients || [];
    const totalVisits = data.reduce((a, r) => a + (r.total_visits || 0), 0);
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${data.length}</div>
        <div class="stat-label">Pacientes Recurrentes</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${totalVisits}</div>
        <div class="stat-label">Visitas Acumuladas</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${data.length ? Math.round(totalVisits / data.length) : 0}</div>
        <div class="stat-label">Promedio Visitas / Paciente</div>
      </div>`;
  } else if (type === 'ai-comparison') {
    const perf = res.performance || {};
    const refutations = res.refutations || [];
    const rate = perf.refutation_rate ? (perf.refutation_rate * 100).toFixed(1) + '%' : '0%';
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${perf.total_diagnoses || 0}</div>
        <div class="stat-label">Diagnósticos IA Totales</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="color:var(--danger)">${perf.total_refuted || 0}</div>
        <div class="stat-label">Refutados por el Médico</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${rate}</div>
        <div class="stat-label">Tasa de Refutación</div>
      </div>`;
  } else if (type === 'prescriptions') {
    const data = res.prescriptions || [];
    const meds = [...new Set(data.map(p => p.medication).filter(Boolean))];
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${data.length}</div>
        <div class="stat-label">Prescripciones Emitidas</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${meds.length}</div>
        <div class="stat-label">Medicamentos Distintos</div>
      </div>`;
  } else if (type === 'activity') {
    const data = res.activity || [];
    const totalVisits = data.reduce((a, r) => a + (r.total_visits || 0), 0);
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${data.length}</div>
        <div class="stat-label">Doctores con Actividad</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${totalVisits}</div>
        <div class="stat-label">Visitas Totales</div>
      </div>`;
  // ── Tipos legacy ─────────────────────────────────────────────────────────
  } else if (type === 'visits') {
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${res.total || 0}</div>
        <div class="stat-label">Total Visitas</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${res.data.filter(v => v.visit_type === 'consulta').length}</div>
        <div class="stat-label">Consultas Médicas</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="color: var(--danger);">${res.data.filter(v => v.visit_type === 'emergencia').length}</div>
        <div class="stat-label">Emergencias</div>
      </div>
    `;
  } else if (type === 'waiting-time' && res.stats) {
    const s = res.stats;
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${s.avg_wait_minutes ?? '0'} min</div>
        <div class="stat-label">Tiempo Espera Promedio</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${s.max_wait_minutes ?? '0'} min</div>
        <div class="stat-label">Tiempo de Espera Máximo</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${s.total_with_arrival ?? '0'}</div>
        <div class="stat-label">Pacientes Atendidos</div>
      </div>
    `;
  } else if (type === 'diagnoses-summary') {
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${res.total_diagnoses || 0}</div>
        <div class="stat-label">Diagnósticos Emitidos</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${res.total_groups || 0}</div>
        <div class="stat-label">Patologías Únicas Detectadas</div>
      </div>
    `;
  } else if (type === 'model-performance') {
    const d = res.data;
    const rate = d.refutation_rate ? (d.refutation_rate * 100).toFixed(1) + '%' : '0%';
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${d.total_diagnoses || 0}</div>
        <div class="stat-label">Predicciones Totales</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${d.total_refuted || 0}</div>
        <div class="stat-label">Predicciones Refutadas</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${rate}</div>
        <div class="stat-label">Tasa de Refutación</div>
      </div>
    `;
  } else if (type === 'billing' && res.data) {
    const d = res.data;
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">$${(d.total_amount || 0).toLocaleString('es-DO', {minimumFractionDigits: 2})}</div>
        <div class="stat-label">Total Facturado</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">$${(d.total_collected || 0).toLocaleString('es-DO', {minimumFractionDigits: 2})}</div>
        <div class="stat-label">Total Recaudado</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${d.invoices ? d.invoices.length : 0}</div>
        <div class="stat-label">Comprobantes Emitidos</div>
      </div>
    `;
  } else if (type === 'doctor-activity') {
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${res.total_doctors || 0}</div>
        <div class="stat-label">Doctores Evaluados</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${res.data.reduce((acc, curr) => acc + (curr.total_visits || 0), 0)}</div>
        <div class="stat-label">Visitas Totales Procesadas</div>
      </div>
    `;
  } else if (type === 'audit') {
    cardsHtml = `
      <div class="stat-card">
        <div class="stat-value">${res.total || 0}</div>
        <div class="stat-label">Acciones Registradas</div>
      </div>
    `;
  }

  if (cardsHtml) {
    statsGrid.innerHTML = cardsHtml;
    statsGrid.style.display = 'flex';
  }
}

function renderReportTable(type, res) {
  const wrap = document.getElementById('reports-table-wrap');
  wrap.innerHTML = '';

  // Resolver el array de filas según el key real de cada endpoint
  let list = [];
  if (type === 'agenda')         list = res.agenda || [];
  else if (type === 'recurrent') list = res.recurrent_patients || [];
  else if (type === 'ai-comparison') list = res.refutations || [];
  else if (type === 'prescriptions') list = res.prescriptions || [];
  else if (type === 'activity')  list = res.activity || [];
  else if (type === 'billing')   list = (res.data && res.data.invoices) ? res.data.invoices : [];
  else if (type === 'audit')     list = res.logs || [];
  else { const rows = res.data || []; list = Array.isArray(rows) ? rows : []; }

  if (!list.length) {
    wrap.innerHTML = `
      <div class="empty-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>No se encontraron registros con los filtros seleccionados.</span>
      </div>`;
    return;
  }

  let tableHtml = '<table class="data-table"><thead><tr>';
  let rowsHtml = '';

  const fmtDate = (str) => {
    if (!str) return '—';
    try { return str.substring(0, 16).replace('T', ' '); } catch(e) { return str; }
  };

  // ── Tablas para tipos nuevos ──────────────────────────────────────────────
  if (type === 'agenda') {
    tableHtml += `
      <th>Fecha</th><th>Hora</th><th>Paciente</th><th>Doctor</th>
      <th>Estado</th><th>Confirmada</th>
    </tr></thead><tbody>`;
    rowsHtml = list.map(v => {
      const statusBadge = v.appointment_status === 'atendido' ? 'badge-verde' : v.appointment_status === 'cancelada' ? 'badge-rojo' : 'badge-amarillo';
      return `<tr>
        <td>${v.scheduled_date || '—'}</td>
        <td><code>${v.scheduled_time || '—'}</code></td>
        <td><strong>${v.patient_name || '—'}</strong></td>
        <td>${v.doctor_fullname || '—'}</td>
        <td><span class="badge ${statusBadge}">${(v.appointment_status || '—').toUpperCase()}</span></td>
        <td><span class="badge ${v.confirmed ? 'badge-verde' : 'badge-amarillo'}">${v.confirmed ? 'SÍ' : 'NO'}</span></td>
      </tr>`;
    }).join('');

  } else if (type === 'recurrent') {
    tableHtml += `
      <th>Paciente</th><th>Cédula</th><th>Teléfono</th>
      <th>Total Visitas</th><th>Primera Visita</th><th>Última Visita</th>
    </tr></thead><tbody>`;
    rowsHtml = list.map(v => `<tr>
      <td><strong>${v.patient_name || '—'}</strong></td>
      <td><code style="font-family:var(--mono);font-size:12px;">${v.patient_cedula || '—'}</code></td>
      <td>${v.phone || '—'}</td>
      <td><code style="font-weight:bold;color:var(--primary);">${v.total_visits || 0}</code></td>
      <td>${v.first_visit_date || '—'}</td>
      <td>${v.last_visit_date || '—'}</td>
    </tr>`).join('');

  } else if (type === 'ai-comparison') {
    tableHtml += `
      <th>Paciente</th><th>Dx IA (rechazado)</th>
      <th>Dx Médico Final</th><th>Razón Refutación</th><th>Fecha</th>
    </tr></thead><tbody>`;
    rowsHtml = list.map(v => `<tr>
      <td><strong>${v.patient_name || '—'}</strong></td>
      <td style="color:var(--danger);">${v.final_diagnosis || '—'}</td>
      <td style="color:var(--success);">${v.doctor_override_diagnosis || '—'}</td>
      <td><span style="font-size:12px;">${v.refutation_reason || '—'}</span></td>
      <td>${fmtDate(v.created_at)}</td>
    </tr>`).join('');

  } else if (type === 'prescriptions') {
    tableHtml += `
      <th>Paciente</th><th>Cédula</th><th>Medicamento</th>
      <th>Dosis</th><th>Frecuencia</th><th>Días</th><th>Fecha</th>
    </tr></thead><tbody>`;
    rowsHtml = list.map(v => `<tr>
      <td><strong>${v.patient_name || '—'}</strong></td>
      <td><code style="font-family:var(--mono);font-size:12px;">${v.patient_cedula || '—'}</code></td>
      <td><strong>${v.medication || '—'}</strong></td>
      <td>${v.dosage || '—'}</td>
      <td>${v.frequency || '—'}</td>
      <td>${v.duration_days != null ? v.duration_days + 'd' : '—'}</td>
      <td>${fmtDate(v.created_at)}</td>
    </tr>`).join('');

  } else if (type === 'activity') {
    tableHtml += `
      <th>Médico</th><th>Especialidad</th><th>Visitas Totales</th>
      <th>Consultas</th><th>Emergencias</th><th>Diagnósticos</th><th>Alertas Rojas</th>
    </tr></thead><tbody>`;
    rowsHtml = list.map(v => `<tr>
      <td><strong>${v.doctor_fullname || '—'}</strong></td>
      <td>${v.especialidad || 'General'}</td>
      <td><code>${v.total_visits || 0}</code></td>
      <td>${v.total_consultas || 0}</td>
      <td style="${(v.total_emergencias || 0) > 0 ? 'color:var(--danger);font-weight:bold;' : ''}">${v.total_emergencias || 0}</td>
      <td>${v.visits_with_diagnosis || 0}</td>
      <td style="${(v.red_alerts || 0) > 0 ? 'color:var(--danger);font-weight:bold;' : ''}">${v.red_alerts || 0}</td>
    </tr>`).join('');

  // ── Tablas legacy ─────────────────────────────────────────────────────────
  } else if (type === 'visits') {
    tableHtml += `
      <th>Fecha</th>
      <th>Tipo</th>
      <th>Paciente</th>
      <th>Cédula</th>
      <th>Doctor</th>
      <th>Diagnóstico</th>
      <th>Alerta</th>
      <th>Estado</th>
    </tr></thead><tbody>`;

    rowsHtml = list.map(v => {
      const alertClass = v.alert_level === 'rojo' ? 'danger' : (v.alert_level === 'amarillo' ? 'warning' : 'success');
      const typeClass = v.visit_type === 'emergencia' ? 'badge-rojo' : 'badge-verde';
      return `
        <tr>
          <td>${fmtDate(v.visit_date)}</td>
          <td><span class="badge ${typeClass}">${v.visit_type.toUpperCase()}</span></td>
          <td><strong>${v.patient_name || '—'}</strong></td>
          <td><code style="font-family:var(--mono);font-size:12px;">${v.patient_cedula || '—'}</code></td>
          <td>${v.doctor_fullname || '—'}</td>
          <td>${v.diagnosis_primary || '—'}</td>
          <td><span class="badge badge-${alertClass}">${(v.alert_level || '—').toUpperCase()}</span></td>
          <td>${v.status || '—'}</td>
        </tr>
      `;
    }).join('');

  } else if (type === 'waiting-time') {
    tableHtml += `
      <th>Fecha</th>
      <th>Hora Prog.</th>
      <th>Paciente</th>
      <th>Doctor</th>
      <th>Llegada Real</th>
      <th>Espera</th>
      <th>Estado Cita</th>
    </tr></thead><tbody>`;

    rowsHtml = list.map(v => {
      const wait = v.wait_minutes !== null ? `${v.wait_minutes} min` : '—';
      const waitColor = v.wait_minutes > 30 ? 'color: var(--danger); font-weight:bold;' : '';
      return `
        <tr>
          <td>${v.scheduled_date || '—'}</td>
          <td><code>${v.scheduled_time || '—'}</code></td>
          <td><strong>${v.patient_name || '—'}</strong></td>
          <td>${v.doctor_fullname || '—'}</td>
          <td><code>${v.actual_arrival ? v.actual_arrival.substring(11, 16) : '—'}</code></td>
          <td style="${waitColor}">${wait}</td>
          <td>${v.appointment_status || '—'}</td>
        </tr>
      `;
    }).join('');

  } else if (type === 'diagnoses-summary') {
    tableHtml += `
      <th>Diagnóstico</th>
      <th>Nivel Alerta</th>
      <th>Frecuencia</th>
      <th>Prob. Promedio</th>
      <th>Prob. Máx.</th>
      <th>Prob. Mín.</th>
    </tr></thead><tbody>`;

    rowsHtml = list.map(v => {
      const alertClass = v.alert_level === 'rojo' ? 'danger' : (v.alert_level === 'amarillo' ? 'warning' : 'success');
      return `
        <tr>
          <td><strong>${v.diagnosis_primary || '—'}</strong></td>
          <td><span class="badge badge-${alertClass}">${(v.alert_level || '—').toUpperCase()}</span></td>
          <td><code>${v.total || 0}</code></td>
          <td>${(v.avg_probability * 100).toFixed(1)}%</td>
          <td>${(v.max_probability * 100).toFixed(1)}%</td>
          <td>${(v.min_probability * 100).toFixed(1)}%</td>
        </tr>
      `;
    }).join('');

  } else if (type === 'model-performance') {
    // Rendimiento de la IA viene en un formato diferente, serializado o estructurado
    tableHtml += `
      <th>Métrica del Motor de IA</th>
      <th>Valor de Rendimiento</th>
    </tr></thead><tbody>`;

    const metrics = [
      { name: 'Total diagnósticos evaluados', val: res.data.total_diagnoses },
      { name: 'Diagnósticos refutados por el médico', val: res.data.total_refuted },
      { name: 'Tasa de discrepancia / refutación', val: (res.data.refutation_rate * 100).toFixed(1) + '%' },
      { name: 'Probabilidad bayesiana promedio', val: (res.data.avg_probability * 100).toFixed(1) + '%' },
      { name: 'Visitas críticas (Alertas Rojas)', val: res.data.red_alerts },
      { name: 'Visitas moderadas (Alertas Amarillas)', val: res.data.yellow_alerts }
    ];

    if (res.data.top_diagnoses) {
      res.data.top_diagnoses.forEach(td => {
        metrics.push({ name: `Top Patología detectada por IA: ${td.diagnosis}`, val: `${td.total} veces` });
      });
    }

    rowsHtml = metrics.map(m => `
      <tr>
        <td><strong>${m.name}</strong></td>
        <td><code>${m.val ?? '0'}</code></td>
      </tr>
    `).join('');

  } else if (type === 'billing') {
    const listInvoices = res.data.invoices || [];
    tableHtml += `
      <th>ID</th>
      <th>Fecha</th>
      <th>Tipo Comprobante</th>
      <th>Paciente</th>
      <th>Cédula</th>
      <th>e-CF / NCF</th>
      <th>Monto Neto</th>
      <th>ITBIS</th>
      <th>Total</th>
      <th>Metodo</th>
      <th>Estado</th>
    </tr></thead><tbody>`;

    rowsHtml = listInvoices.map(v => {
      const statusClass = v.estado === 'pagada' ? 'badge-verde' : 'badge-rojo';
      return `
        <tr>
          <td><code>#${v.id}</code></td>
          <td>${fmtDate(v.created_at)}</td>
          <td><span class="badge badge-amarillo">${(v.invoice_type || 'factura').toUpperCase()}</span></td>
          <td><strong>${v.patient_name || '—'}</strong></td>
          <td><code style="font-family:var(--mono);font-size:12px;">${v.patient_cedula || '—'}</code></td>
          <td><code>${v.encf || v.ncf || '—'}</code></td>
          <td>$${(v.amount || 0).toFixed(2)}</td>
          <td>$${(v.itbis || 0).toFixed(2)}</td>
          <td><strong>$${(v.total || 0).toFixed(2)}</strong></td>
          <td>${(v.payment_method || 'efectivo').toUpperCase()}</td>
          <td><span class="badge ${statusClass}">${(v.estado || 'pendiente').toUpperCase()}</span></td>
        </tr>
      `;
    }).join('');

  } else if (type === 'doctor-activity') {
    tableHtml += `
      <th>Médico</th>
      <th>Especialidad</th>
      <th>Visitas Totales</th>
      <th>Consultas</th>
      <th>Emergencias</th>
      <th>Diagnósticos</th>
      <th>Alertas Rojas</th>
    </tr></thead><tbody>`;

    rowsHtml = list.map(v => `
      <tr>
        <td><strong>${v.doctor_fullname || '—'}</strong></td>
        <td>${v.especialidad || 'General'}</td>
        <td><code>${v.total_visits || 0}</code></td>
        <td>${v.total_consultas || 0}</td>
        <td style="${v.total_emergencias > 0 ? 'color: var(--danger); font-weight:bold;' : ''}">${v.total_emergencias || 0}</td>
        <td>${v.visits_with_diagnosis || 0}</td>
        <td style="${v.red_alerts > 0 ? 'color: var(--danger); font-weight:bold;' : ''}">${v.red_alerts || 0}</td>
      </tr>
    `).join('');

  } else if (type === 'audit') {
    tableHtml += `
      <th>Fecha/Hora</th>
      <th>Usuario</th>
      <th>Acción</th>
      <th>Entidad</th>
      <th>ID Entidad</th>
      <th>Detalles de la Actividad</th>
      <th>Dirección IP</th>
    </tr></thead><tbody>`;

    rowsHtml = list.map(v => {
      let actionClass = 'badge-verde';
      if (v.action === 'DELETE') actionClass = 'badge-rojo';
      else if (v.action === 'UPDATE') actionClass = 'badge-amarillo';
      else if (v.action === 'LOGIN') actionClass = 'badge-cyan';
      
      return `
        <tr>
          <td><small>${fmtDate(v.logged_at)}</small></td>
          <td><strong>${v.username || '—'}</strong></td>
          <td><span class="badge ${actionClass}">${v.action || '—'}</span></td>
          <td><code>${v.entity || '—'}</code></td>
          <td><code>${v.entity_id || '—'}</code></td>
          <td><span style="font-size:12px; color:var(--text-primary);">${v.details || '—'}</span></td>
          <td><code>${v.ip_address || '—'}</code></td>
        </tr>
      `;
    }).join('');
  }

  tableHtml += rowsHtml + '</tbody></table>';
  wrap.innerHTML = tableHtml;
}

async function exportReport(format) {
  const tableWrap = document.getElementById('reports-table-wrap');
  const table = tableWrap ? tableWrap.querySelector('table') : null;

  if (!table) {
    toast('warning', 'Primero genera un reporte antes de exportar.');
    return;
  }

  const type = document.getElementById('reports-type').value;
  const typeLabel = document.getElementById('reports-type').options[document.getElementById('reports-type').selectedIndex]?.text || type;
  const filename = `reporte_${type}_${new Date().toISOString().split('T')[0]}`;

  if (format === 'pdf') {
    // Imprimir la tabla como PDF usando el diálogo de impresión del navegador
    const printWin = window.open('', '_blank');
    const statsHtml = document.getElementById('reports-stats-grid')?.innerHTML || '';
    printWin.document.write(`
      <!DOCTYPE html><html><head>
        <meta charset="UTF-8">
        <title>Reporte: ${typeLabel}</title>
        <style>
          body { font-family: Arial, sans-serif; font-size: 12px; margin: 20px; color: #111; }
          h1 { font-size: 16px; margin-bottom: 4px; }
          p.sub { color: #666; font-size: 11px; margin-bottom: 16px; }
          .stats { display: flex; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
          .stat-card { border: 1px solid #ddd; border-radius: 6px; padding: 10px 16px; min-width: 120px; }
          .stat-value { font-size: 20px; font-weight: bold; }
          .stat-label { font-size: 10px; color: #666; }
          table { width: 100%; border-collapse: collapse; }
          th { background: #1e293b; color: #fff; padding: 6px 8px; text-align: left; font-size: 11px; }
          td { padding: 5px 8px; border-bottom: 1px solid #eee; font-size: 11px; }
          tr:nth-child(even) td { background: #f8fafc; }
          .badge { padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; }
          code { font-family: monospace; font-size: 11px; }
          @media print { button { display: none; } }
        </style>
      </head><body>
        <h1>Reporte: ${typeLabel}</h1>
        <p class="sub">Generado el ${new Date().toLocaleString('es-DO')} &mdash; Sistema MED-INTELLIGENCE PRO</p>
        <div class="stats">${statsHtml}</div>
        ${table.outerHTML}
        <script>window.onload = () => { window.print(); }<\/script>
      </body></html>`);
    printWin.document.close();

  } else if (format === 'csv') {
    // Exportar la tabla visible como CSV
    const headers = [];
    table.querySelectorAll('thead th').forEach(th => headers.push(`"${th.innerText.trim()}"`));

    const csvRows = [headers.join(',')];
    table.querySelectorAll('tbody tr').forEach(tr => {
      const cols = [];
      tr.querySelectorAll('td').forEach(td => {
        cols.push(`"${td.innerText.trim().replace(/"/g, "'")}"`); 
      });
      csvRows.push(cols.join(','));
    });

    const blob = new Blob(["\uFEFF" + csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${filename}.csv`;
    link.click();

  } else if (format === 'xlsx') {
    // 1. Intentar usar SheetJS para generar un archivo .xlsx binario verdadero (OpenXML)
    if (typeof XLSX === 'undefined') {
      try {
        await new Promise((resolve, reject) => {
          const script = document.createElement('script');
          script.src = 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';
          script.onload = resolve;
          script.onerror = reject;
          document.head.appendChild(script);
        });
      } catch (e) {
        console.warn('No se pudo cargar SheetJS dinámicamente:', e);
      }
    }

    if (typeof XLSX !== 'undefined') {
      try {
        const wb = XLSX.utils.table_to_book(table, { sheet: "Reporte" });
        XLSX.writeFile(wb, `${filename}.xlsx`);
        return;
      } catch (err) {
        console.error('Error generando .xlsx con SheetJS:', err);
      }
    }

    // 2. Fallback: Excel XML Spreadsheet formato .xls para abrir directo en Excel sin error de extensión
    const excelXml = `
      <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
      <head><meta charset="UTF-8"><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>Reporte</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--></head>
      <body>${table.outerHTML}</body>
      </html>`;
    const blob = new Blob(["\uFEFF" + excelXml], { type: 'application/vnd.ms-excel;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${filename}.xls`;
    link.click();
  }
}

async function loadRefinementQuestions(probs) {
  const panel = document.getElementById('refinement-panel');
  const container = document.getElementById('refinement-questions-container');
  if (!panel || !container) return;

  panel.style.display = '';
  container.innerHTML = `
    <div class="gemini-loading" style="padding:10px; display:flex; align-items:center; gap:8px;">
      <div class="spinner-ring" style="width:20px;height:20px;border-width:2px;"></div>
      <span>Obteniendo preguntas de depuración...</span>
    </div>
  `;

  // Inicializar respuestas temporales
  STATE.tempRefinementAnswers = {};

  try {
    const res = await api('POST', '/api/diagnose/refinement-questions', {
      probabilities: probs,
      sintomas:      STATE.diagSintomas,
      constantes:    STATE.diagConstantes,
      antecedentes:  STATE.diagAntecedentes,
    });

    if (!res.success || !res.preguntas || res.preguntas.length === 0) {
      panel.style.display = 'none';
      return;
    }

    let questionsHtml = res.preguntas.map((q, i) => `
      <div class="refinement-q-item" id="q-item-${i}" style="padding:12px; background:rgba(255,255,255,0.02); border-radius:6px; border:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center; gap:16px;">
        <div style="text-align:left; flex:1;">
          <div style="font-weight:600; font-size:13.5px; color:var(--brand-light);">${q.pregunta}</div>
          <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">Evalúa: <strong>${q.sintoma}</strong></div>
        </div>
        <div style="display:flex; gap:8px;" class="q-btn-group">
          <button type="button" class="btn-secondary btn-q-yes" style="padding:6px 12px; font-size:12px; margin:0;" onclick="selectRefinementOption(${i}, '${q.sintoma.replace(/'/g, "\\'")}', true)">Sí</button>
          <button type="button" class="btn-secondary btn-q-no" style="padding:6px 12px; font-size:12px; margin:0;" onclick="selectRefinementOption(${i}, '${q.sintoma.replace(/'/g, "\\'")}', false)">No</button>
        </div>
      </div>
    `).join('');

    // Agregar botón de aplicar al final
    questionsHtml += `
      <div style="display:flex; justify-content:flex-end; margin-top:16px; padding-top:12px; border-top:1px dashed var(--border-color);">
        <button type="button" class="btn-primary" style="padding:10px 20px; font-weight:bold;" onclick="applyRefinementAnswers()">
          💾 Aplicar Respuestas y Recalcular
        </button>
      </div>
    `;

    container.innerHTML = questionsHtml;
  } catch (e) {
    console.error("Error al obtener preguntas de depuración:", e);
    panel.style.display = 'none';
  }
}

function selectRefinementOption(qIndex, sintoma, val) {
  // Guardar en las respuestas temporales
  STATE.tempRefinementAnswers[sintoma] = val;

  // Actualizar el estado visual de los botones del grupo
  const qItem = document.getElementById(`q-item-${qIndex}`);
  if (!qItem) return;

  const btnYes = qItem.querySelector('.btn-q-yes');
  const btnNo = qItem.querySelector('.btn-q-no');

  if (val === true) {
    btnYes.style.setProperty('background-color', 'var(--brand-light)', 'important');
    btnYes.style.setProperty('color', '#000', 'important');
    btnYes.style.setProperty('border-color', 'var(--brand-light)', 'important');
    
    // Resetear el botón "No"
    btnNo.style.removeProperty('background-color');
    btnNo.style.removeProperty('color');
    btnNo.style.removeProperty('border-color');
  } else {
    btnNo.style.setProperty('background-color', '#ef4444', 'important');
    btnNo.style.setProperty('color', '#fff', 'important');
    btnNo.style.setProperty('border-color', '#ef4444', 'important');
    
    // Resetear el botón "Sí"
    btnYes.style.removeProperty('background-color');
    btnYes.style.removeProperty('color');
    btnYes.style.removeProperty('border-color');
  }
}

async function applyRefinementAnswers() {
  const keys = Object.keys(STATE.tempRefinementAnswers || {});
  if (keys.length === 0) {
    toast('error', 'Debes responder al menos una pregunta antes de aplicar.');
    return;
  }

  // 1. Aplicar cada respuesta al estado y a la UI
  keys.forEach(sintoma => {
    const val = STATE.tempRefinementAnswers[sintoma];
    
    // Marcar en la UI
    document.querySelectorAll('#symptoms-checkboxes input[type="checkbox"], #antecedentes-checkboxes input[type="checkbox"]').forEach(cb => {
      const labelText = cb.parentElement.innerText.trim();
      if (labelText.toLowerCase() === sintoma.toLowerCase()) {
        cb.checked = val;
        if (typeof toggleSymptom === 'function') toggleSymptom(cb);
      }
    });

    // Guardar en el estado interno
    if (ALL_SYMPTOMS.includes(sintoma)) {
      STATE.diagSintomas[sintoma] = val;
    } else if (ALL_ANTECEDENTES.includes(sintoma)) {
      STATE.diagAntecedentes[sintoma] = val;
    } else {
      STATE.diagSintomas[sintoma] = val;
    }
  });

  toast('success', `Se aplicaron ${keys.length} respuestas de depuración. Recalculando...`);

  // Ocultar el panel
  const panel = document.getElementById('refinement-panel');
  if (panel) panel.style.display = 'none';

  // 2. Recalcular el diagnóstico preliminar
  const btn = document.getElementById('btn-diag-phase1');
  if (btn) setButtonLoading(btn, true, 'Recalculando...');

  try {
    const res = await api('POST', '/api/diagnose/preliminar', {
      constantes:   STATE.diagConstantes,
      sintomas:     STATE.diagSintomas,
      antecedentes: STATE.diagAntecedentes,
    });

    if (res.success) {
      STATE.phase1Probs = res.probabilities;
      STATE.tests       = res.tests_sugeridos || [];
      renderPhase1Result(res);
      runGeminiAnalysis(res.probabilities);
      loadRefinementQuestions(res.probabilities);
    } else {
      toast('error', res.error || 'Error al recalcular.');
    }
  } catch (err) {
    console.error("Error al recalcular diagnóstico:", err);
  } finally {
    if (btn) setButtonLoading(btn, false);
  }
}


/* ─────────────────────────────────────────────────────────────────────────── */
/* FUNCIONES DE CONTROL DE SIDEBAR RESPONSIVO Y PLEGABLE                      */
/* ─────────────────────────────────────────────────────────────────────────── */

function toggleDesktopSidebar() {
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('main-content');
  if (!sidebar) return;

  const isCollapsed = sidebar.classList.toggle('collapsed');
  if (mainContent) {
    mainContent.classList.toggle('sidebar-collapsed', isCollapsed);
  }
  try {
    localStorage.setItem('sidebar_collapsed', isCollapsed ? '1' : '0');
  } catch (e) {}
}

function toggleMobileSidebar(forceState) {
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (!sidebar) return;

  const shouldOpen = forceState !== undefined ? forceState : !sidebar.classList.contains('mobile-open');

  if (shouldOpen) {
    sidebar.classList.remove('collapsed');
    sidebar.classList.add('mobile-open');
    if (backdrop) backdrop.classList.add('active');
    document.body.classList.add('mobile-nav-open');
  } else {
    sidebar.classList.remove('mobile-open');
    if (backdrop) backdrop.classList.remove('active');
    document.body.classList.remove('mobile-nav-open');
  }
}

function closeMobileSidebar() {
  toggleMobileSidebar(false);
}

// Inicialización de estado guardado y eventos responsivos
document.addEventListener('DOMContentLoaded', () => {
  // Cargar estado de plegado guardado en desktop
  try {
    const saved = localStorage.getItem('sidebar_collapsed');
    if (saved === '1' && window.innerWidth > 992) {
      const sidebar = document.getElementById('sidebar');
      const mainContent = document.getElementById('main-content');
      if (sidebar) sidebar.classList.add('collapsed');
      if (mainContent) mainContent.classList.add('sidebar-collapsed');
    }
  } catch (e) {}

  // Cerrar sidebar al hacer clic en un item de navegación en pantallas móviles
  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 992) {
      const navItem = e.target.closest('.nav-item');
      if (navItem && !navItem.classList.contains('dropdown-toggle')) {
        closeMobileSidebar();
      }
    }
  });

  // Limpiar clases al redimensionar la pantalla a desktop
  window.addEventListener('resize', () => {
    if (window.innerWidth > 992) {
      closeMobileSidebar();
    }
  });
});

// ── Lógica de Alternancia de Tema (Modo Oscuro / Claro) ──
// Extracted toggleTheme to theme.js

// Extracted updateThemeUI to theme.js

// Auto-inicializar tema
// Extracted initTheme to theme.js

// ==========================================
// MÓDULO DE HORARIOS Y DISPONIBILIDAD
// ==========================================

const DAY_NAMES = {
  1: 'Lunes',
  2: 'Martes',
  3: 'Miércoles',
  4: 'Jueves',
  5: 'Viernes',
  6: 'Sábado',
  7: 'Domingo'
};

async function loadAdminSchedulesTab() {
  // 1. Cargar horario de la clínica
  const resClinic = await api('GET', '/api/schedules/clinic');
  if (resClinic.success && resClinic.hours) {
    renderClinicHoursEditor(resClinic.hours);
  }

  // 2. Cargar listado de doctores para el selector de bloqueos
  const resDocs = await api('GET', '/api/users');
  const select = document.getElementById('block-doctor-id');
  if (select && resDocs.success && resDocs.users) {
    const doctors = resDocs.users.filter(u => u.role === 'doctor');
    select.innerHTML = '<option value="">Seleccione un doctor...</option>' + 
      doctors.map(d => `<option value="${d.id}">${d.full_name || d.username}</option>`).join('');
  }
  
  // Limpiar tabla de bloqueos al inicio
  const tbody = document.getElementById('blocked-slots-table-body');
  if (tbody) {
    tbody.innerHTML = `<tr><td colspan="5" style="padding:20px; text-align:center; color:var(--text-secondary);">Seleccione un doctor para ver sus horarios bloqueados.</td></tr>`;
  }
}

function renderClinicHoursEditor(hours) {
  const container = document.getElementById('clinic-hours-container');
  if (!container) return;

  container.innerHTML = hours.map(h => {
    const checked = h.is_active ? 'checked' : '';
    return `
      <div class="clinic-day-row" data-day="${h.day_of_week}" style="display:grid; grid-template-columns:1fr auto; align-items:center; gap:8px; padding:10px 0; border-bottom:1px solid var(--border-color);">
        <div style="display:flex; align-items:center; gap:10px;">
          <input type="checkbox" class="day-active-checkbox" id="clinic-day-chk-${h.day_of_week}" ${checked} style="cursor:pointer; flex-shrink:0;" />
          <label for="clinic-day-chk-${h.day_of_week}" style="font-weight:600; cursor:pointer;">${DAY_NAMES[h.day_of_week]}</label>
        </div>
        <div style="display:flex; align-items:center; gap:6px; flex-shrink:0;">
          <input type="time" class="day-start-time search-input" value="${h.start_time}" style="padding:4px 6px; width:82px;" />
          <span style="color:var(--text-secondary); font-size:12px;">–</span>
          <input type="time" class="day-end-time search-input" value="${h.end_time}" style="padding:4px 6px; width:82px;" />
        </div>
      </div>
    `;
  }).join('');
}

async function saveClinicWorkingHoursSettings() {
  const rows = document.querySelectorAll('#clinic-hours-container .clinic-day-row');
  const hours = [];
  rows.forEach(r => {
    const day = parseInt(r.getAttribute('data-day'));
    const is_active = r.querySelector('.day-active-checkbox').checked;
    const start_time = r.querySelector('.day-start-time').value;
    const end_time = r.querySelector('.day-end-time').value;
    hours.push({ day_of_week: day, is_active, start_time, end_time });
  });

  const res = await api('POST', '/api/schedules/clinic', { hours });
  if (res.success) {
    toast('success', 'Horario de la clínica actualizado correctamente.');
  } else {
    toast('error', res.error || 'Error al guardar horario.');
  }
}

async function loadBlockedSlotsForAdmin() {
  const doctorId = document.getElementById('block-doctor-id').value;
  const tbody = document.getElementById('blocked-slots-table-body');
  if (!tbody) return;

  if (!doctorId) {
    tbody.innerHTML = `<tr><td colspan="5" style="padding:20px; text-align:center; color:var(--text-secondary);">Seleccione un doctor para ver sus horarios bloqueados.</td></tr>`;
    return;
  }

  tbody.innerHTML = `<tr><td colspan="5" style="padding:20px; text-align:center;"><div class="spinner-ring"></div> Cargando...</td></tr>`;

  const res = await api('GET', `/api/schedules/doctor/${doctorId}/blocked`);
  if (res.success && res.slots) {
    if (res.slots.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="padding:20px; text-align:center; color:var(--text-secondary);">Este doctor no tiene horarios bloqueados registrados.</td></tr>`;
      return;
    }
    
    // Obtener nombre del doctor seleccionado
    const select = document.getElementById('block-doctor-id');
    const doctorName = select.options[select.selectedIndex].text;

    tbody.innerHTML = res.slots.map(s => `
      <tr style="border-bottom:1px solid var(--border-color);">
        <td style="padding:12px;">${doctorName}</td>
        <td style="padding:12px;">${s.blocked_date}</td>
        <td style="padding:12px;">${s.start_time} - ${s.end_time}</td>
        <td style="padding:12px; color:var(--text-secondary);">${s.reason || '—'}</td>
        <td style="padding:12px;">
          <button class="btn-outline" onclick="deleteBlockedSlotAdmin(${s.id})" style="color:var(--status-danger-color); padding:4px 8px; font-size:12px;">
            Eliminar
          </button>
        </td>
      </tr>
    `).join('');
  } else {
    tbody.innerHTML = `<tr><td colspan="5" style="padding:20px; text-align:center; color:var(--status-danger-color);">Error al cargar horarios bloqueados.</td></tr>`;
  }
}

async function handleBlockSchedule(e) {
  e.preventDefault();
  const doctorId = document.getElementById('block-doctor-id').value;
  const date = document.getElementById('block-date').value;
  const startTime = document.getElementById('block-start-time').value;
  const endTime = document.getElementById('block-end-time').value;
  const reason = document.getElementById('block-reason').value;

  if (!doctorId || !date || !startTime || !endTime) {
    toast('warning', 'Por favor complete todos los campos obligatorios.');
    return;
  }

  const res = await api('POST', '/api/schedules/doctor/blocked', {
    doctor_id: parseInt(doctorId),
    blocked_date: date,
    start_time: startTime,
    end_time: endTime,
    reason: reason
  });

  if (res.success) {
    toast('success', 'Horario bloqueado con éxito.');
    document.getElementById('form-block-schedule').reset();
    document.getElementById('block-doctor-id').value = doctorId;
    loadBlockedSlotsForAdmin();
  } else {
    toast('error', res.error || 'Error al bloquear horario.');
  }
}

async function deleteBlockedSlotAdmin(slotId) {
  if (!confirm('¿Está seguro de que desea eliminar este bloqueo de horario?')) return;
  const res = await api('DELETE', `/api/schedules/doctor/blocked/${slotId}`);
  if (res.success) {
    toast('success', 'Bloqueo eliminado.');
    loadBlockedSlotsForAdmin();
  } else {
    toast('error', res.error || 'Error al eliminar bloqueo.');
  }
}

// --- VISTA DOCTOR ---

async function loadDoctorSchedulesTab() {
  const user = STATE.user || {};
  if (!user.id) return;

  // 1. Cargar horario de la clínica (Solo Lectura)
  const resClinic = await api('GET', '/api/schedules/clinic');
  const viewContainer = document.getElementById('doctor-clinic-hours-view');
  if (viewContainer && resClinic.success && resClinic.hours) {
    viewContainer.innerHTML = resClinic.hours.map(h => {
      const statusText = h.is_active 
        ? `<span class="badge badge-success" style="background-color:rgba(16,185,129,0.1); color:#10b981; border:1px solid rgba(16,185,129,0.2); padding:2px 8px; font-size:11px; border-radius:12px;">Activo</span>`
        : `<span class="badge badge-danger" style="background-color:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.2); padding:2px 8px; font-size:11px; border-radius:12px;">Cerrado</span>`;
      const timeText = h.is_active ? `${h.start_time} - ${h.end_time}` : '—';
      return `
        <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 0; border-bottom:1px solid var(--border-color);">
          <span style="font-weight:600; width:120px;">${DAY_NAMES[h.day_of_week]}</span>
          <span style="color:var(--text-secondary);">${timeText}</span>
          ${statusText}
        </div>
      `;
    }).join('');
  }

  // 2. Cargar mis horarios bloqueados
  loadBlockedSlotsForDoctor();
}

async function loadBlockedSlotsForDoctor() {
  const user = STATE.user || {};
  const tbody = document.getElementById('doctor-blocked-slots-table-body');
  if (!tbody || !user.id) return;

  tbody.innerHTML = `<tr><td colspan="4" style="padding:20px; text-align:center;"><div class="spinner-ring"></div> Cargando...</td></tr>`;

  const res = await api('GET', `/api/schedules/doctor/${user.id}/blocked`);
  if (res.success && res.slots) {
    if (res.slots.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="padding:20px; text-align:center; color:var(--text-secondary);">No tienes horarios bloqueados registrados.</td></tr>`;
      return;
    }

    tbody.innerHTML = res.slots.map(s => `
      <tr style="border-bottom:1px solid var(--border-color);">
        <td style="padding:12px;">${s.blocked_date}</td>
        <td style="padding:12px;">${s.start_time} - ${s.end_time}</td>
        <td style="padding:12px; color:var(--text-secondary);">${s.reason || '—'}</td>
        <td style="padding:12px;">
          <button class="btn-outline" onclick="deleteBlockedSlotDoctor(${s.id})" style="color:var(--status-danger-color); padding:4px 8px; font-size:12px;">
            Eliminar
          </button>
        </td>
      </tr>
    `).join('');
  } else {
    tbody.innerHTML = `<tr><td colspan="4" style="padding:20px; text-align:center; color:var(--status-danger-color);">Error al cargar tus bloqueos.</td></tr>`;
  }
}

async function handleDoctorBlockSchedule(e) {
  e.preventDefault();
  const user = STATE.user || {};
  if (!user.id) return;

  const date = document.getElementById('doc-block-date').value;
  const startTime = document.getElementById('doc-block-start-time').value;
  const endTime = document.getElementById('doc-block-end-time').value;
  const reason = document.getElementById('doc-block-reason').value;

  if (!date || !startTime || !endTime) {
    toast('warning', 'Por favor complete todos los campos obligatorios.');
    return;
  }

  const res = await api('POST', '/api/schedules/doctor/blocked', {
    doctor_id: user.id,
    blocked_date: date,
    start_time: startTime,
    end_time: endTime,
    reason: reason
  });

  if (res.success) {
    toast('success', 'Agenda bloqueada con éxito.');
    document.getElementById('form-doctor-block-schedule').reset();
    loadBlockedSlotsForDoctor();
  } else {
    toast('error', res.error || 'Error al bloquear horario.');
  }
}

async function deleteBlockedSlotDoctor(slotId) {
  if (!confirm('¿Está seguro de que desea eliminar este bloqueo de horario?')) return;
  const res = await api('DELETE', `/api/schedules/doctor/blocked/${slotId}`);
  if (res.success) {
    toast('success', 'Bloqueo eliminado.');
    loadBlockedSlotsForDoctor();
  } else {
    toast('error', res.error || 'Error al eliminar bloqueo.');
  }
}






