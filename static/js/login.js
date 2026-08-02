    let failedAttempts = 0;
    let lockoutTimer = null;

    const form = document.getElementById('login-form');
    const loginBtn = document.getElementById('login-btn');
    const alertBox = document.getElementById('alert-box');
    const attemptBar = document.getElementById('attempt-bar');
    const attemptCount = document.getElementById('attempt-count');
    const attemptFill = document.getElementById('attempt-fill');

    function showAlert(type, message, extra = '') {
      const icons = {
        danger: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
        warning: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
        success: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
      };
      alertBox.style.display = 'flex';
      alertBox.className = `alert alert-${type}`;
      alertBox.innerHTML = `${icons[type]} <div>${message}${extra ? `<div style="margin-top:6px;font-size:12px;opacity:0.8;">${extra}</div>` : ''}</div>`;
    }

    function hideAlert() { alertBox.style.display = 'none'; }

    function updateAttemptBar(count) {
      if (count <= 0) { attemptBar.style.display = 'none'; return; }
      attemptBar.style.display = 'block';
      const pct = (count / 5) * 100;
      attemptFill.style.width = pct + '%';
      attemptCount.textContent = `${count} / 5`;
      const colors = ['#10b981', '#84cc16', '#f59e0b', '#ef4444', '#dc2626'];
      attemptFill.style.background = colors[Math.min(count - 1, 4)];
    }

    function startLockoutCountdown(minutes = 15) {
      let seconds = minutes * 60;
      loginBtn.disabled = true;
      form.querySelectorAll('input').forEach(i => i.disabled = true);

      function tick() {
        const m = Math.floor(seconds / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        const timerHTML = `<div class="lockout-timer">${m}:${s}</div>`;
        showAlert('warning',
          '🔒 Cuenta bloqueada temporalmente por múltiples intentos fallidos.',
          `Intente nuevamente en: ${timerHTML}Protección activa para prevenir acceso no autorizado.`
        );
        if (seconds <= 0) {
          loginBtn.disabled = false;
          form.querySelectorAll('input').forEach(i => i.disabled = false);
          failedAttempts = 0;
          updateAttemptBar(0);
          showAlert('success', 'Cuenta desbloqueada. Puede intentar ingresar nuevamente.');
          setTimeout(hideAlert, 3000);
          return;
        }
        seconds--;
        lockoutTimer = setTimeout(tick, 1000);
      }
      tick();
    }

    function setLoading(loading) {
      loginBtn.disabled = loading;
      loginBtn.classList.toggle('loading', loading);
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();

      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value.trim();
      if (!username || !password) {
        showAlert('warning', 'Ingresa usuario y contraseña para continuar.');
        return;
      }

      setLoading(true);

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        const data = await res.json();

        if (data.success) {
          showAlert('success', `✅ Bienvenido, ${data.user.full_name || data.user.username}. Redirigiendo...`);
          setTimeout(() => { window.location.href = '/'; }, 800);
        } else {
          setLoading(false);
          if (data.locked) {
            failedAttempts = 5;
            updateAttemptBar(5);
            startLockoutCountdown(15);
          } else {
            failedAttempts = Math.min(failedAttempts + 1, 4);
            updateAttemptBar(failedAttempts);
            const remaining = 5 - failedAttempts;
            showAlert('danger', data.error || 'Credenciales incorrectas.',
              remaining > 0 ? `⚠️ Te quedan ${remaining} intento${remaining !== 1 ? 's' : ''} antes del bloqueo temporal.` : '');
            document.getElementById('password').value = '';
            document.getElementById('password').focus();
          }
        }
      } catch (err) {
        setLoading(false);
        showAlert('danger', 'Error de conexión con el servidor.', 'Verifica que el servidor esté activo.');
      }
    });

    /* ── Liquid Glass: Mouse 3D Card Tilt ── */
    (function initLiquidGlass() {
      const card = document.querySelector('.login-card');
      if (!card) return;

      let targetX = 0, targetY = 0;
      let currentX = 0, currentY = 0;

      function lerp(a, b, t) { return a + (b - a) * t; }

      document.addEventListener('mousemove', (e) => {
        const cx = window.innerWidth  / 2;
        const cy = window.innerHeight / 2;
        targetX = ((e.clientY - cy) / cy) * -5;
        targetY = ((e.clientX - cx) / cx) *  5;
      });

      document.addEventListener('mouseleave', () => {
        targetX = 0; targetY = 0;
      });

      (function animate() {
        currentX = lerp(currentX, targetX, 0.055);
        currentY = lerp(currentY, targetY, 0.055);
        card.style.transform =
          `perspective(900px) rotateX(${currentX}deg) rotateY(${currentY}deg)`;
        requestAnimationFrame(animate);
      })();
    })();
