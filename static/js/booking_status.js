setTimeout(() => {
  document.querySelectorAll('.toast-message').forEach(t => t.remove());
}, 4000);

(function () {
  function $id(id){ return document.getElementById(id); }
  const root = $id('booking-root');
  if (!root) { console.warn('booking-root not found — make sure template has <div id="booking-root"...>'); return; }

  const SEND_URL = root.dataset.sendUrl || '/api/send-otp/';
  const VERIFY_URL = root.dataset.verifyUrl || '/api/verify-otp/';
  const OTP_EXPIRE_SECONDS = parseInt(root.dataset.expireSeconds || '300', 10);

  function getCookie(name) {
    const v = document.cookie.split('; ').find(c => c.trim().startsWith(name + '='));
    return v ? decodeURIComponent(v.split('=')[1]) : null;
  }
  const csrftoken = getCookie('csrftoken');

  const mobileInput = $id('mobileInput');
  const sendOtpBtn = $id('sendOtpBtn');
  const sendOtpSpinner = $id('sendOtpSpinner');
  const stepMobile = $id('step-mobile');
  const stepOtp = $id('step-otp');
  const stepStatus = $id('step-status');
  const otpInput = $id('otpInput');
  const verifyOtpBtn = $id('verifyOtpBtn');
  const resendOtpBtn = $id('resendOtpBtn');
  const otpProgress = $id('otpProgress');
  const otpExpiryLabel = $id('otpExpiryLabel');
  const devOtpReveal = $id('devOtpReveal');
  const alerts = $id('alerts');
  const toastContainer = $id('toastContainer');

  function showAlert(text, cls='info'){
    if (alerts) {
      alerts.innerHTML = `<div class="alert alert-${cls}">${text}</div>`;
      setTimeout(()=> { if (alerts) alerts.innerHTML = ''; }, 4000);
    } else console.log('[alert]', text);
  }
  function toast(msg){
    if (!toastContainer) return console.log('[toast]', msg);
    const t = document.createElement('div');
    t.className = 'toast show';
    t.role = 'alert';
    t.style.minWidth = '200px';
    t.innerHTML = `<div class="toast-body">${msg}</div>`;
    toastContainer.appendChild(t);
    setTimeout(()=>{ t.remove(); }, 3000);
  }
  function prettyPhone(v){
    if(!v) return '';
    const plus = v.trim().startsWith('+') ? '+' : '';
    const digits = v.replace(/\D/g,'');
    return plus + digits;
  }
  function disable(el, yes=true){ if(el) el.disabled = yes; }

  let otpTimerIdx = null;
  function startOtpTimer(seconds){
    const start = Date.now();
    function tick(){
      const passed = Math.floor((Date.now() - start)/1000);
      const left = Math.max(0, seconds - passed);
      if(otpProgress) otpProgress.style.width = Math.max(0, Math.round((left / seconds) * 100)) + '%';
      if(otpExpiryLabel) otpExpiryLabel.textContent = left>0 ? `Expires in ${left}s` : 'Expired';
      if(left<=0){ clearInterval(otpTimerIdx); }
    }
    clearInterval(otpTimerIdx);
    tick();
    otpTimerIdx = setInterval(tick, 500);
  }

  async function doSendOtp(){
    if(!mobileInput || !sendOtpBtn){ console.error('Missing mobileInput or sendOtpBtn'); return; }
    const raw = mobileInput.value.trim();
    const mobile = prettyPhone(raw);
    if(!mobile || mobile.length < 6){ showAlert('Enter a valid mobile number', 'warning'); return; }
    disable(sendOtpBtn, true);
    if (sendOtpSpinner) sendOtpSpinner.classList.remove('d-none');
    try {
      const res = await fetch(SEND_URL, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken, 'Accept': 'application/json' },
        body: new URLSearchParams({ mobile })
      });
      const data = await res.json();
      disable(sendOtpBtn, false);
      if (sendOtpSpinner) sendOtpSpinner.classList.add('d-none');
      if (data.ok) {
        showAlert('OTP sent', 'success');
        if (stepMobile) stepMobile.style.display = 'none';
        if (stepOtp) stepOtp.style.display = 'block';
        startOtpTimer(data.expires_in || OTP_EXPIRE_SECONDS);
        if (data.otp && devOtpReveal) devOtpReveal.innerHTML = `Dev OTP: <strong>${data.otp}</strong>`;
        toast('OTP sent');
      } else {
        showAlert(data.error || 'Failed to send OTP', 'danger');
      }
    } catch (err) {
      disable(sendOtpBtn, false);
      if (sendOtpSpinner) sendOtpSpinner.classList.add('d-none');
      console.error(err);
      showAlert('Network error sending OTP', 'danger');
    }
  }

  async function doVerifyOtp(){
    if(!verifyOtpBtn || !otpInput){ console.error('Missing verifyOtpBtn or otpInput'); return; }
    const otp = otpInput.value.trim();
    const mobile = prettyPhone(mobileInput ? mobileInput.value.trim() : '');
    if(!mobile || !otp){ showAlert('Enter mobile and OTP', 'warning'); return; }
    disable(verifyOtpBtn, true);
    try {
      const res = await fetch(VERIFY_URL, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken, 'Accept': 'application/json' },
        body: new URLSearchParams({ mobile, otp })
      });
      const data = await res.json();
      disable(verifyOtpBtn, false);
      if (data.ok) {
        showAlert('OTP verified', 'success');
        if (stepOtp) stepOtp.style.display = 'none';
        if (stepStatus) stepStatus.style.display = 'block';
        toast('Verified');
      } else {
        showAlert(data.error || 'Invalid OTP', 'danger');
      }
    } catch (err) {
      disable(verifyOtpBtn, false);
      console.error(err);
      showAlert('Network error verifying OTP', 'danger');
    }
  }

  // Attach handlers safely
  if (sendOtpBtn) sendOtpBtn.addEventListener('click', doSendOtp);
  if (verifyOtpBtn) verifyOtpBtn.addEventListener('click', doVerifyOtp);
  if (resendOtpBtn) resendOtpBtn.addEventListener('click', function(e){ e.preventDefault(); doSendOtp(); });

  if (mobileInput) mobileInput.addEventListener('keydown', function(e){ if (e.key === 'Enter') { e.preventDefault(); doSendOtp(); } });
  if (otpInput) otpInput.addEventListener('keydown', function(e){ if (e.key === 'Enter') { e.preventDefault(); doVerifyOtp(); } });

  // helpful debug object
  window._booking_debug = { SEND_URL, VERIFY_URL, OTP_EXPIRE_SECONDS };
})();
