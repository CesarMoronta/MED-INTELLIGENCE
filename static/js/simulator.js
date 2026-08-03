/* =============================================================================
   simulator.js — Extracted from main.js
   ============================================================================= */

function initSimulator() {
  // ya está construido en buildSymptomToggles
}

function resetSimulation() {
  document.querySelectorAll('#sim-symptoms-grid .symptom-toggle').forEach(el => {
    el.classList.remove('checked');
    const cb = el.querySelector('input[type=checkbox]');
    if (cb) cb.checked = false;
  });
  document.getElementById('sim-chart').innerHTML = '';
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
