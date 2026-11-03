(function () {
  var WA = '916300695591';
  function link(t) { return 'https://wa.me/' + WA + '?text=' + encodeURIComponent(t); }
  function $(id) { return document.getElementById(id); }

  document.querySelectorAll('[data-wa]').forEach(function (a) { a.href = link(a.getAttribute('data-wa')); });

  /* tabs on the contact forms */
  var tabs = document.querySelectorAll('.tab');
  if (tabs.length) {
    var panels = { release: $('panel-release'), sell: $('panel-sell'), ask: $('panel-ask') };
    var showTab = function (name) {
      tabs.forEach(function (t) { t.setAttribute('aria-selected', String(t.dataset.tab === name)); });
      Object.keys(panels).forEach(function (k) { if (panels[k]) panels[k].hidden = (k !== name); });
    };
    tabs.forEach(function (t) { t.addEventListener('click', function () { showTab(t.dataset.tab); }); });
    document.querySelectorAll('a[data-tab]').forEach(function (a) {
      a.addEventListener('click', function () { showTab(a.dataset.tab); });
    });
    var sec = $('contact');
    showTab((sec && sec.getAttribute('data-default-tab')) || 'release');
  }

  /* forms -> WhatsApp */
  function compose(form) {
    var lines = [form.dataset.intro, ''];
    form.querySelectorAll('[data-label]').forEach(function (el) {
      var v = (el.value || '').trim();
      if (v) lines.push(el.dataset.label + ': ' + v);
    });
    lines.push('', 'Sent from the ClearKarat website. Please reply with the next steps.');
    return lines.join('\n');
  }
  document.querySelectorAll('form[data-intro]').forEach(function (form) {
    var send = form.querySelector('.send'), prev = form.querySelector('.preview');
    var copy = form.querySelector('.copy'), note = form.querySelector('.copied');
    function update() { var msg = compose(form); prev.textContent = msg; send.href = link(msg); }
    form.addEventListener('input', update);
    form.addEventListener('change', update);
    send.addEventListener('click', function (e) {
      if (!form.checkValidity()) { e.preventDefault(); form.reportValidity(); }
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (form.checkValidity()) { send.focus(); note.textContent = 'Looks good. Press Send on WhatsApp.'; }
      else { form.reportValidity(); }
    });
    copy.addEventListener('click', function () {
      var msg = compose(form);
      function fallback() {
        var r = document.createRange(); r.selectNodeContents(prev);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        note.textContent = 'Message selected. Copy it with your keyboard.';
      }
      try { navigator.clipboard.writeText(msg).then(function () { note.textContent = 'Copied.'; }, fallback); }
      catch (err) { fallback(); }
    });
    update();
  });

  /* copy the phone number */
  var cn = $('copy-num'), cm = $('copy-num-msg');
  if (cn) cn.addEventListener('click', function () {
    var shown = '+91 63006 95591';
    try { navigator.clipboard.writeText('+916300695591').then(function () { cm.textContent = 'Copied.'; }, function () { cm.textContent = shown; }); }
    catch (e) { cm.textContent = shown; }
  });

  /* estimator */
  if ($('est-gross')) {
    var edited = false;
    var fmtG = function (n) { return n.toFixed(2) + ' g'; };
    var inr = function (n) { return '₹ ' + Math.round(n).toLocaleString('en-IN'); };
    var plain = function (n) { return 'Rs ' + Math.round(n).toLocaleString('en-IN'); };
    var calc = function () {
      var gross = Math.max(parseFloat($('est-gross').value) || 0, 0);
      var stone = Math.min(Math.max(parseFloat($('est-stone').value) || 0, 0), gross);
      var p = parseFloat($('est-purity').value);
      var rate = Math.max(parseFloat($('est-rate').value) || 0, 0);
      var pledged = $('est-mode').value === 'pledged';
      var loan = Math.max(parseFloat($('est-loan').value) || 0, 0);
      var net = gross - stone, fine = net * p, value = fine * rate;
      var total = pledged ? Math.max(value - loan, 0) : value;
      var sel = $('est-purity'), ptxt = sel.options[sel.selectedIndex].text;
      $('loan-wrap').hidden = !pledged; $('row-loan').hidden = !pledged;
      $('o-warn').hidden = !(pledged && value < loan);
      $('o-value').textContent = inr(value); $('o-loan').textContent = inr(loan);
      $('o-total-label').textContent = pledged ? 'You receive' : 'Estimate';
      $('o-gross').textContent = fmtG(gross); $('o-stone').textContent = fmtG(stone);
      $('o-net').textContent = fmtG(net); $('o-purity').textContent = ptxt;
      $('o-fine').textContent = fmtG(fine); $('o-rate').textContent = inr(rate);
      $('o-total').textContent = inr(total);
      $('slip-chip').textContent = edited ? 'Your estimate' : 'Example values';
      var intro = pledged ? 'Hello ClearKarat, I would like a written quote for my pledged gold.' : 'Hello ClearKarat, I would like a written quote for my old gold.';
      var msg = intro;
      if (edited) {
        msg = intro + '\n' + 'My own rough estimate: gross ' + fmtG(gross) + ', stones/dirt ' + fmtG(stone) + ', purity ' + ptxt +
          ', 24K rate Rs ' + Math.round(rate) + '/g, value about ' + plain(value) +
          (pledged ? ', loan payoff ' + plain(loan) + ', money I would receive about ' + plain(total) : '') +
          ', before any charges.\n' + 'Please tell me the weighed and tested figure.';
      }
      $('est-send').href = link(msg);
    };
    ['est-mode', 'est-gross', 'est-stone', 'est-purity', 'est-rate', 'est-loan'].forEach(function (id) {
      $(id).addEventListener('input', function () { edited = true; calc(); });
      $(id).addEventListener('change', function () { edited = true; calc(); });
    });
    calc();
  }
})();
