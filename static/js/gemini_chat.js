/* =============================================================================
   gemini_chat.js — Extracted from main.js
   ============================================================================= */

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

async function runGeminiAnalysis(probs, tests = null) {
  const sortedBayes = Object.entries(probs).sort(([,a],[,b]) => b - a);
  const topBayesDiag = sortedBayes[0]?.[0];
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
      motivo_consulta: document.getElementById('diag-motivo')?.value.trim() || null,
      doctor_notes:  document.getElementById('diag-doctor-notes')?.value.trim() || null,
      tests_resultados: tests,
      tests_sugeridos: STATE.tests || [],
      patient_profile: STATE.currentPatient ? {
        name: STATE.currentPatient.name,
        gender: STATE.currentPatient.gender,
        dob: STATE.currentPatient.dob,
        blood_type: STATE.currentPatient.blood_type || STATE.currentPatient.tipo_sangre || null,
        age: STATE.currentPatient.age || (typeof calcAge === 'function' ? calcAge(STATE.currentPatient.dob) : (STATE.diagConstantes?.edad || 30))
      } : null
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

    const urgencia = res.nivel_urgencia || 'Ambulatorio';
    const urgenciaColor = { 'Emergencia': '#ef4444', 'Urgente': '#f59e0b', 'Ambulatorio': '#10b981' }[urgencia] || '#10b981';
    const urgenciaEmoji = { 'Emergencia': '🔴', 'Urgente': '🟡', 'Ambulatorio': '🟢' }[urgencia] || '🟢';

    panel.innerHTML = `
      <div class="gemini-panel">
        <div class="gemini-panel-header">
          <span class="gemini-badge">✨ Gemini AI — Internista de Apoyo</span>
          <span style="color:var(--text-muted);font-size:12px;">${res.fallback ? 'Modo offline' : 'Análisis en tiempo real'}</span>
        </div>

        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;padding:8px 12px;background:rgba(0,0,0,0.04);border-radius:8px;border-left:3px solid ${urgenciaColor}">
          <span style="font-size:16px;">${urgenciaEmoji}</span>
          <div>
            <div style="font-size:11px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.8px;">Nivel de Urgencia Estimado</div>
            <div style="font-weight:700;color:${urgenciaColor};font-size:14px;">${urgencia}</div>
          </div>
        </div>

        <div class="gemini-validacion">
          <div style="font-size:11px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">🧬 Análisis Clínico</div>
          <p>${res.validacion || ''}</p>
        </div>

        ${res.plan_terapeutico_sugerido ? `
          <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.2);border-radius:8px;padding:12px;margin:12px 0;">
            <div style="font-size:11px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">💊 Plan Terapéutico Orientativo</div>
            <p style="margin:0;font-size:13px;color:var(--text);">${res.plan_terapeutico_sugerido}</p>
          </div>
        ` : ''}

        ${alertas ? `<div class="gemini-alertas-section">${alertas}</div>` : ''}

        ${sugeridos ? `
          <div class="gemini-sugeridos-section">
            <div class="gemini-sugeridos-label">🔎 Explorar también:</div>
            <div class="gemini-tags">${sugeridos}</div>
          </div>
        ` : ''}

        ${res.confianza_gemini ? `
          <div class="gemini-confianza">
            <strong>Valoración de Confianza Clínica:</strong> ${res.confianza_gemini}
          </div>
        ` : ''}

        ${res.diagnostico_propuesto && res.diagnostico_propuesto !== topBayesDiag ? `
          <div class="gemini-correction-banner">
            <div class="gemini-correction-text" style="display: flex; flex-direction: column; gap: 4px;">
              <span class="gemini-correction-title">
                ⚠️ Discrepancia Clínica Detectada
              </span>
              <span>
                La IA sugiere cambiar el diagnóstico a: <strong class="gemini-correction-diag">${res.diagnostico_propuesto}</strong>.
              </span>
            </div>
            <button type="button" class="btn-primary" style="padding: 6px 12px; font-size: 0.85rem; margin: 0; background-color: #ef4444; border-color: #ef4444;" onclick="applyAIDiagnosis('${res.diagnostico_propuesto.replace(/'/g, "\\'")}')">
              Aplicar Corrección de IA
            </button>
          </div>
        ` : ''}

        <div style="margin-top:14px;padding:10px 12px;background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.2);border-radius:8px;font-size:11.5px;color:var(--text-muted);line-height:1.6;">
          ⚕️ <strong>Aviso Clínico:</strong> Este análisis es generado por inteligencia artificial como herramienta de apoyo diagnóstico. <strong>No constituye un diagnóstico médico definitivo</strong> y no reemplaza la evaluación presencial ni el juicio del médico tratante.
        </div>
      </div>
    `;
  } catch(e) {
    panel.innerHTML = '';
  }
}
