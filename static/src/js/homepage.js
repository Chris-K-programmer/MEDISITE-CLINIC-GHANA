/* ===== MediSite Clinic Homepage JS ===== */
document.addEventListener('DOMContentLoaded', function() {

  // ===== DARK MODE TOGGLE =====
  var toggle = document.getElementById('themeToggle');
  var body = document.body;
  var saved = localStorage.getItem('medi_darkmode');
  if (saved === 'true') body.classList.add('dark-mode');

  if (toggle) {
    toggle.addEventListener('click', function() {
      body.classList.toggle('dark-mode');
      localStorage.setItem('medi_darkmode', body.classList.contains('dark-mode'));
    });
  }

  // ===== FLOATING PARTICLES =====
  var colors = ['#0ea5e9','#06d6a0','#f72585','#7209b7','#3b82f6'];
  var canvas = document.querySelector('.medi-bg-canvas');
  if (canvas) {
    for (var i = 0; i < 15; i++) {
      var p = document.createElement('div');
      p.className = 'particle';
      var size = Math.random() * 8 + 3;
      p.style.cssText =
        'width:' + size + 'px;height:' + size + 'px;' +
        'left:' + (Math.random()*100) + '%;top:' + (Math.random()*100) + '%;' +
        'background:' + colors[i % colors.length] + ';' +
        'animation-duration:' + (Math.random()*10+10) + 's;' +
        'animation-delay:' + (Math.random()*5) + 's;';
      canvas.appendChild(p);
    }
  }

  // ===== PASSWORD VISIBILITY TOGGLE =====
  var pwToggle = document.getElementById('pwToggle');
  var pwInput = document.getElementById('password');
  if (pwToggle && pwInput) {
    pwToggle.addEventListener('click', function() {
      var isPassword = pwInput.type === 'password';
      pwInput.type = isPassword ? 'text' : 'password';
      pwToggle.textContent = isPassword ? '🙈' : '👁️';
    });
  }
});
