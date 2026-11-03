#!/usr/bin/env python3
"""Builds the ClearKarat static website.
Usage: python3 build.py [BASE_URL] [OUT_DIR] [--artifact]
BASE_URL defaults to https://www.clearkarat.com (change to your real domain).
"""
import os, re, sys, json, shutil, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_core import *
from content_guides import GUIDES

HERE = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
ARTIFACT = "--artifact" in sys.argv
BASE = (args[0] if args else "https://www.clearkarat.com").rstrip("/")
OUT = args[1] if len(args) > 1 else os.path.join(HERE, "..", "clearkarat-site")
SRC = open(os.path.join(HERE, "v5-source.html"), encoding="utf-8").read()

# ---------------------------------------------------------------- reusable chunks from the single-page design
def between(a, b):
    i = SRC.index(a); j = SRC.index(b, i + len(a))
    return SRC[i + len(a):j]

CSS = re.search(r"<style>(.*?)</style>", SRC, re.S).group(1)
DEFS = re.search(r'(<svg width="0" height="0".*?</svg>)\s*<header', SRC, re.S).group(1)
LOGO = re.search(r'<a class="logo" href="#top".*?</a>', SRC, re.S).group(0)
SEC = {
 "hero": between("<!-- HERO -->", "<!-- SERVICES -->"),
 "services": between("<!-- SERVICES -->", "<!-- PROMISE -->"),
 "promise": between("<!-- PROMISE -->", "<!-- PROCESS -->"),
 "process": between("<!-- PROCESS -->", "<!-- MOMENTS -->"),
 "moments": between("<!-- MOMENTS -->", "<!-- ESTIMATOR -->"),
 "estimator": between("<!-- ESTIMATOR -->", "<!-- CONTACT FORMS -->"),
 "forms": between("<!-- CONTACT FORMS -->", "<!-- SAFETY -->"),
 "safety": between("<!-- SAFETY -->", "<!-- FAQ -->"),
}

def contact_swap(s):
    s = s.replace("919182387752", WA).replace("+91 91823 87752", PHONE_DISP).replace("+919182387752", PHONE)
    return s

for k in SEC:
    SEC[k] = contact_swap(SEC[k])
LOGO = contact_swap(LOGO).replace('href="#top"', 'href="index.html"')

def fill(s):
    for k, v in {"{PHONE}": PHONE_DISP, "{WA}": WA, "{EMAIL}": EMAIL, "{INSTA}": INSTA, "{ADDR}": ADDR_FULL,
                 "{MAPS}": MAPS, "{PIN}": PIN, "{UPDATED_H}": UPDATED_H}.items():
        s = s.replace(k, v)
    return s

# ---------------------------------------------------------------- extra css
EXTRA_CSS = """
/* ---- multi-page additions ---- */
.tagline { font-family: var(--display); font-size: clamp(1.35rem, 3.4vw, 2rem); line-height: 1.2; margin-top: .8rem; }
.tagline .ps { background: linear-gradient(transparent 82%, var(--gold-fill) 82%, var(--gold-fill) 93%, transparent 93%); }
.hero h1 { font-size: clamp(2rem, 5.2vw, 3.5rem); }
.mnav { display: none; position: relative; }
.mnav summary { list-style: none; cursor: pointer; font-weight: 600; font-size: .95rem; padding: .55rem .8rem; border: 1.5px solid var(--ink); border-radius: 10px; display: block; }
.mnav summary::after { content: none; }
.mnav summary::-webkit-details-marker { display: none; }
.mnav nav { position: absolute; right: 0; top: calc(100% + .5rem); z-index: 40; min-width: 15rem; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: .5rem; display: grid; box-shadow: 0 14px 30px -16px rgba(16, 38, 43, .5); }
.mnav nav a { padding: .7rem .8rem; border-radius: 8px; text-decoration: none; font-weight: 500; }
.mnav nav a:hover, .mnav nav a[aria-current] { background: var(--surface-2); }
.nav a[aria-current] { color: var(--ink); border-bottom: 2px solid var(--gold-fill); }
.top-r { display: flex; align-items: center; gap: .6rem; }
@media (max-width: 880px) { .mnav { display: block; } }
@media (max-width: 520px) { .top .btn-wa .lbl { display: none; } .top .btn-wa { padding: .55rem .7rem; } .logo .wm { font-size: 1.25rem; } .logo svg { width: 36px; height: 36px; } }
.crumbs { display: flex; flex-wrap: wrap; gap: .35rem; font-size: .86rem; color: var(--muted); padding-top: 1rem; }
.crumbs a { color: var(--muted); }
.phero { padding-block: clamp(1.2rem, 3vw, 2.2rem) clamp(1.2rem, 3vw, 2rem); }
.phero h1 { font-size: clamp(2rem, 5.2vw, 3.4rem); margin-top: .7rem; max-width: 22em; }
.phero .lead { max-width: 44rem; }
.phero .meta { margin-top: .8rem; font-family: var(--mono); font-size: .78rem; color: var(--muted); }
.pagegrid { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: clamp(1.5rem, 4vw, 3.5rem); align-items: start; }
.pagegrid > * { min-width: 0; }
@media (max-width: 940px) { .pagegrid { grid-template-columns: 1fr; } }
.prose { max-width: 46rem; }
.prose > h2 { font-size: clamp(1.45rem, 3vw, 2rem); margin: 2.2rem 0 .8rem; }
.prose > h2:first-child { margin-top: 0; }
.prose h3 { font-size: 1.25rem; margin: 1.5rem 0 .5rem; }
.prose p { margin-top: .9rem; }
.prose p:first-child { margin-top: 0; }
.prose ul, .prose ol:not(.steps) { padding-left: 1.3rem; display: grid; gap: .55rem; margin: 1rem 0; }
.prose ul.areas { grid-template-columns: 1fr 1fr; gap: .4rem 1.5rem; }
@media (max-width: 560px) { .prose ul.areas { grid-template-columns: 1fr; } }
.prose a { color: var(--gold); text-underline-offset: 3px; }
.prose .btn { color: var(--trust-ink); text-decoration: none; }
.prose ol.steps { margin: 1.2rem 0; }
.callout { border: 1.5px solid var(--ink); background: var(--surface); border-radius: 14px; padding: 1rem 1.2rem; margin: 1.4rem 0; }
.callout b { display: block; font-family: var(--display); font-weight: 400; font-size: 1.15rem; margin-bottom: .4rem; }
.callout ul { margin: .4rem 0 0; }
.callout p { margin: 0; }
.tbl-wrap { overflow-x: auto; margin: 1.2rem 0; border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }
table.t { border-collapse: collapse; width: 100%; min-width: 440px; font-size: .95rem; }
table.t th, table.t td { padding: .7rem .9rem; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
table.t tr:last-child td { border-bottom: 0; }
table.t th { font-family: var(--mono); font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 500; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.2rem 0; }
.grid3 > * { min-width: 0; }
@media (max-width: 860px) { .grid3 { grid-template-columns: 1fr; } }
.card-link { display: grid; gap: .4rem; align-content: start; padding: 1.2rem; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; text-decoration: none; color: var(--ink); }
a.card-link:hover { border-color: var(--ink); }
.card-link h3 { font-size: 1.22rem; margin: 0; }
.card-link p { color: var(--muted); font-size: .95rem; margin: 0; }
.card-link .go { font-family: var(--mono); font-size: .76rem; color: var(--gold); letter-spacing: .08em; text-transform: uppercase; margin-top: .3rem; }
.prose .card-link a, .card-link a { color: var(--gold); }
.side { position: sticky; top: calc(5.2rem + env(safe-area-inset-top, 0px)); }
@media (max-width: 940px) { .side { position: static; } }
.side-card { background: var(--surface); border: 1.5px solid var(--ink); border-radius: 16px; padding: 1.3rem; display: grid; gap: .8rem; }
.side-card h2 { font-size: 1.4rem; }
.side-card p { font-size: .94rem; color: var(--muted); }
.side-card .row2 { display: grid; gap: .1rem; font-size: .92rem; }
.side-card .row2 b { font-family: var(--mono); font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; color: var(--gold); font-weight: 500; }
.side-card .row2 span, .side-card .row2 a { overflow-wrap: anywhere; }
.side-card ul { margin: 0; padding: 0; list-style: none; display: grid; gap: .4rem; font-size: .9rem; }
.side-card li { display: flex; gap: .5rem; }
.side-card li svg { color: var(--trust); margin-top: .12em; width: 1.1em; height: 1.1em; }
.ctaband { background: var(--band); color: var(--band-ink); }
.ctaband .wrap { padding-block: clamp(2.2rem, 5vw, 3.4rem); display: grid; gap: 1rem; }
.ctaband h2 { font-size: clamp(1.7rem, 4vw, 2.6rem); max-width: 18em; }
.ctaband p { color: var(--band-muted); max-width: 36rem; }
.ctaband .btn-ghost { border-color: var(--band-ink); color: var(--band-ink); }
.ctaband .btn-ghost:hover { background: var(--band-card); }
.keys ul { margin: .3rem 0 0; padding-left: 1.2rem; display: grid; gap: .35rem; }
.fine a { color: var(--gold); }
.foot a { color: var(--band-ink); text-underline-offset: 3px; }
.foot-grid { grid-template-columns: 1.5fr 1fr 1fr 1fr; }
@media (max-width: 900px) { .foot-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 560px) { .foot-grid { grid-template-columns: 1fr; } }
.foot h2 { font-family: var(--mono); font-size: .74rem; letter-spacing: .12em; text-transform: uppercase; color: var(--band-gold); font-weight: 500; margin-bottom: .7rem; }
.foot ul { list-style: none; margin: 0; padding: 0; display: grid; gap: .45rem; }
.foot .legal { grid-column: 1 / -1; border-top: 1px solid var(--band-line); padding-top: 1.2rem; display: flex; flex-wrap: wrap; gap: .6rem 1.4rem; align-items: center; justify-content: space-between; }
.foot .legal small { margin: 0; }
.foot { padding-bottom: calc(5.5rem + env(safe-area-inset-bottom, 0px)); }
.sr:focus { position: fixed; z-index: 100; top: .5rem; left: .5rem; width: auto; height: auto; clip: auto; padding: .6rem 1rem; background: var(--ink); color: var(--bg); border-radius: 8px; }
html[lang="te"] body { font-family: 'Noto Sans Telugu', var(--body); }
html[lang="te"] h1, html[lang="te"] h2, html[lang="te"] h3 { font-family: 'Noto Sans Telugu', var(--body); font-weight: 600; line-height: 1.3; }
.guide-meta { font-family: var(--mono); font-size: .76rem; color: var(--muted); }
.textlink { color: var(--gold); font-weight: 600; text-underline-offset: 3px; }
.contactgrid .card-link p a { font-weight: 600; word-break: break-word; }
"""

# ---------------------------------------------------------------- JS
APP_JS = r"""(function () {
  var WA = '__WA__';
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
    var shown = '__PHONE_DISP__';
    try { navigator.clipboard.writeText('__PHONE__').then(function () { cm.textContent = 'Copied.'; }, function () { cm.textContent = shown; }); }
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
""".replace("__WA__", WA).replace("__PHONE_DISP__", PHONE_DISP).replace("__PHONE__", PHONE)

# ---------------------------------------------------------------- navigation
NAV = [("Sell gold", "sell-gold.html"), ("Release pledged gold", "release-pledged-gold.html"),
       ("Estimate", "gold-estimator.html"), ("Guides", "guides.html"), ("About", "about.html"), ("Contact", "contact.html")]

FONTS = ("https://fonts.googleapis.com/css2?family=Young+Serif&family=Public+Sans:wght@400;500;600;700"
         "&family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+Telugu:wght@400;600&"
         "family=Noto+Sans+Devanagari:wght@400;600&display=swap")

def e(s): return H.escape(s, quote=True)
def strip_tags(s): return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()
def url(slug): return BASE + "/" + ("" if slug == "index.html" else slug)

def header(current):
    def lk(n, u):
        cur = ' aria-current="page"' if u == current else ""
        return '<a href="' + u + '"' + cur + '>' + n + '</a>'
    links = "".join(lk(n, u) for n, u in NAV)
    msg = "Hello ClearKarat, I found you on your website and have a question about my gold."
    return f"""<header class="top"><div class="wrap top-in">
 {LOGO}
 <nav class="nav" aria-label="Main">{links}</nav>
 <div class="top-r">
  <a class="btn btn-wa btn-sm" data-wa="{msg}" href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp"><svg class="ic" aria-hidden="true"><use href="#i-chat"/></svg><span class="lbl"> WhatsApp</span></a>
  <details class="mnav"><summary>Menu</summary><nav aria-label="Mobile">{links}<a href="index.html">Home</a></nav></details>
 </div></div></header>"""

def footer():
    svc = [("Sell old gold", "sell-gold.html"), ("Release pledged gold", "release-pledged-gold.html"), ("Gold value calculator", "gold-estimator.html")]
    if HOME_VISIT: svc.append(("Home visit evaluation", "home-visit-gold-evaluation.html"))
    svc += [("Gold buyers in Hyderabad", "gold-buyers-in-hyderabad.html"), ("Gold buyers in Kukatpally", "gold-buyers-in-kukatpally.html")]
    gl = [(g["h1"].split(":")[0].capitalize() if False else g["title"].split(" | ")[0], g["slug"] + ".html") for g in GUIDES[:5]]
    li = lambda items: "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in items)
    comp = [("About ClearKarat", "about.html"), ("Our Plain Sight Promise", "transparency.html"), ("Questions and answers", "faq.html"),
            ("All guides", "guides.html"), ("Contact", "contact.html"), ("తెలుగు", "telugu.html")]
    return f"""<footer class="foot"><div class="wrap foot-grid">
 <div>
  <div class="logo" style="pointer-events:none"><svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="30" fill="url(#gGold)"/><circle cx="32" cy="32" r="24.5" fill="none" stroke="#10262B" stroke-opacity=".55" stroke-width="1.4"/><path d="M24 17.5V46.5M25.5 32.5L41 17.5M28.5 30.5L42 46.5" fill="none" stroke="#10262B" stroke-width="5.6"/><path d="M12.5 24.5A21 21 0 0 1 27 11.5" fill="none" stroke="#FFFFFF" stroke-opacity=".75" stroke-width="2.4" stroke-linecap="round"/></svg><span class="wm">Clear<b>Karat</b></span></div>
  <p class="tag">{TAGLINE}</p>
  <p style="margin-top:.8rem">{ADDR_FULL}</p>
  <p style="margin-top:.4rem">WhatsApp and call: <a href="https://wa.me/{WA}">{PHONE_DISP}</a></p>
  <p style="margin-top:.4rem">Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  <p style="margin-top:.4rem"><a href="{INSTA}" target="_blank" rel="noopener">Instagram: @clearkaratofficial</a></p>
  <p style="margin-top:.4rem"><a href="{MAPS}" target="_blank" rel="noopener">Open in Google Maps</a></p>
 </div>
 <div><h2>Services</h2><ul>{li(svc)}</ul></div>
 <div><h2>Guides</h2><ul>{li(gl)}</ul></div>
 <div><h2>ClearKarat</h2><ul>{li(comp)}</ul></div>
 <div class="legal"><small>&copy; 2026 ClearKarat. Gold rates change through the day. Estimates on this site are indicative. The figure that counts is the one on your written slip, after weighing and testing in front of you.</small>
 <small><a href="privacy-policy.html">Privacy policy</a> &middot; <a href="terms.html">Terms</a></small></div>
</div></footer>
<a class="btn btn-wa float" data-wa="Hello ClearKarat, I found you on your website and would like to talk about my gold." href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="Chat with ClearKarat on WhatsApp"><svg class="ic" aria-hidden="true"><use href="#i-chat"/></svg> WhatsApp</a>"""

# ---------------------------------------------------------------- schema
def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"

def ld_business():
    return {"@context": "https://schema.org", "@type": "LocalBusiness", "@id": BASE + "/#business", "name": BRAND,
            "url": BASE + "/", "logo": BASE + "/logo.png", "image": BASE + "/og-image.png",
            "description": "ClearKarat buys old gold and pledged gold in Hyderabad. Gold is weighed and tested in front of you, and every number is on a written slip before you decide.",
            "slogan": TAGLINE, "telephone": PHONE, "email": EMAIL,
            "address": {"@type": "PostalAddress", "streetAddress": ADDR_LINE, "addressLocality": CITY,
                        "addressRegion": STATE, "postalCode": PIN, "addressCountry": "IN"},
            "areaServed": [{"@type": "City", "name": "Hyderabad"}, {"@type": "Country", "name": "India"}],
            "sameAs": [INSTA], "knowsAbout": ["Selling old gold", "Releasing pledged gold", "Gold purity testing", "Gold valuation"],
            "contactPoint": {"@type": "ContactPoint", "telephone": PHONE, "email": EMAIL, "contactType": "customer service",
                             "areaServed": "IN", "availableLanguage": ["English", "Telugu", "Hindi"]}}

def ld_site():
    return {"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": BRAND,
            "publisher": {"@id": BASE + "/#business"}, "inLanguage": "en-IN"}

def ld_crumbs(crumbs):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": url(s)} for i, (n, s) in enumerate(crumbs)]
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}

def ld_faq(items):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

def ld_service(name, desc, slug):
    return {"@context": "https://schema.org", "@type": "Service", "name": name, "description": desc, "url": url(slug),
            "provider": {"@id": BASE + "/#business"}, "areaServed": [{"@type": "City", "name": "Hyderabad"}, {"@type": "Country", "name": "India"}],
            "serviceType": name}

def ld_article(title, desc, slug):
    return {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
            "mainEntityOfPage": url(slug), "datePublished": UPDATED, "dateModified": UPDATED,
            "author": {"@type": "Organization", "name": BRAND, "url": BASE + "/"},
            "publisher": {"@id": BASE + "/#business"}, "image": BASE + "/og-image.png", "inLanguage": "en-IN"}

# ---------------------------------------------------------------- blocks
def faq_block(items, title="Straight answers", eyebrow="Questions"):
    d = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items)
    return f'<section class="sec" id="faq"><div class="wrap"><div class="sec-head"><p class="eyebrow">{eyebrow}</p><h2>{title}</h2></div><div class="faq">{d}</div></div></section>'

def cta_band(h="See the weight. See the test. See the price. Then decide."):
    return f"""<section class="ctaband"><div class="wrap"><p class="eyebrow" style="color:var(--band-gold)">Start with one message</p><h2>{h}</h2>
<p>Send us a line on WhatsApp. We will tell you what we need, and you will not be asked to commit to anything.</p>
<div class="cta-row"><a class="btn btn-wa" data-wa="Hello ClearKarat, I would like to talk about my gold." href="https://wa.me/{WA}" target="_blank" rel="noopener"><svg class="ic" aria-hidden="true"><use href="#i-chat"/></svg> Chat on WhatsApp</a>
<a class="btn btn-ghost" href="contact.html">Contact and forms</a></div></div></section>"""

def side_card():
    return f"""<aside class="side"><div class="side-card"><h2>Talk to ClearKarat</h2>
<p>Message us the basics and we reply with next steps. No commitment.</p>
<a class="btn btn-wa" data-wa="Hello ClearKarat, I found you on your website and would like to talk about my gold." href="https://wa.me/{WA}" target="_blank" rel="noopener"><svg class="ic" aria-hidden="true"><use href="#i-chat"/></svg> WhatsApp {PHONE_DISP}</a>
<div class="row2"><b>Call</b><a href="tel:{PHONE}">{PHONE_DISP}</a></div>
<div class="row2"><b>Email</b><a href="mailto:{EMAIL}">{EMAIL}</a></div>
<div class="row2"><b>Visit</b><span>{ADDR_FULL}</span><a href="{MAPS}" target="_blank" rel="noopener">Open in Google Maps</a></div>
<div class="row2"><b>Instagram</b><a href="{INSTA}" target="_blank" rel="noopener">@clearkaratofficial</a></div>
<ul><li><svg class="ic" aria-hidden="true"><use href="#i-check"/></svg>Open scale facing you</li>
<li><svg class="ic" aria-hidden="true"><use href="#i-check"/></svg>Purity tested at your side</li>
<li><svg class="ic" aria-hidden="true"><use href="#i-check"/></svg>Itemised written slip</li>
<li><svg class="ic" aria-hidden="true"><use href="#i-check"/></svg>Free to say no</li></ul></div></aside>"""

def forms_block(default_tab):
    return SEC["forms"].replace('<section class="sec" id="contact">', f'<section class="sec" id="contact" data-default-tab="{default_tab}">')

def card(href, h, p): return f'<a class="card-link" href="{href}"><h3>{h}</h3><p>{p}</p><span class="go">Read more</span></a>'

# ---------------------------------------------------------------- shell
def shell(slug, title, desc, body_main, lds, lang="en", og_type="website", robots="index,follow,max-image-preview:large"):
    canonical = url(slug)
    head = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#10262B">
<meta name="geo.region" content="IN-TG"><meta name="geo.placename" content="Hyderabad">
<meta property="og:site_name" content="{BRAND}"><meta property="og:type" content="{og_type}"><meta property="og:locale" content="en_IN">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE}/og-image.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{BASE}/og-image.png">
<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="styles.css">
{''.join(ld(x) for x in lds)}"""
    body = f"""{DEFS}
<a class="sr" href="#top">Skip to content</a>
{header(slug)}
<main id="top">
{body_main}
</main>
{footer()}
<script src="app.js" defer></script>"""
    if ARTIFACT and slug == "index.html":
        # the artifact viewer wraps this page in its own skeleton
        art_head = f'<title>ClearKarat</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="stylesheet" href="{FONTS}">\n<link rel="stylesheet" href="styles.css">'
        return art_head + "\n" + body
    return f'<!doctype html>\n<html lang="{lang}">\n<head>\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'

def content_page(slug, title, desc, h1, eyebrow, lead, body, crumbs, lds_extra=(), forms=None, faq=None, meta=None, side=True,
                 lang="en", og_type="website", after=""):
    cr = [("Home", "index.html")] + crumbs + [(h1 if len(h1) < 60 else title.split(" | ")[0], slug)]
    crumb_html = '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(
        f'<a href="{s}">{n}</a>' for n, s in cr[:-1]) + f' <span aria-hidden="true">/</span> <span aria-current="page">{e(cr[-1][0])}</span></nav>'
    m = f'<p class="meta">{meta}</p>' if meta else ""
    hero = f'<section class="phero"><div class="wrap">{crumb_html}<p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lead">{lead}</p>{m}</div></section>'
    inner = f'<div class="prose">{fill(body)}</div>'
    grid = f'<section class="sec" style="padding-top:0"><div class="wrap pagegrid">{inner}{side_card() if side else ""}</div></section>' if side else \
           f'<section class="sec" style="padding-top:0"><div class="wrap"><div class="prose" style="max-width:none">{fill(body)}</div></div></section>'
    parts = [hero, grid]
    if forms: parts.append(forms_block(forms))
    if faq: parts.append(faq_block(faq))
    if after: parts.append(fill(after))
    parts.append(cta_band())
    lds = [ld_crumbs(cr)] + list(lds_extra)
    if faq: lds.append(ld_faq(faq))
    return shell(slug, title, desc, "\n".join(parts), lds, lang=lang, og_type=og_type)

PAGES = {}
def add(slug, html_): PAGES[slug] = html_

def faq_pick(idx): return [FAQS[i] for i in idx]

# ---------------------------------------------------------------- home
def build_home():
    hero = SEC["hero"]
    hero = hero.replace("Pledged gold release &middot; Old gold buying &middot; India and worldwide",
                        "Hyderabad &middot; Old gold buying &middot; Pledged gold release")
    h1_old = '<h1>Your gold, your terms, <span class="ps">in plain sight.</span></h1>'
    assert h1_old in hero
    hero = hero.replace(h1_old, '<h1>Sell old gold or release pledged gold in Hyderabad</h1>\n      <p class="tagline">Your gold, your terms, <span class="ps">in plain sight.</span></p>')
    hi = '<p lang="hi">आपका सोना, आपकी शर्तें, आपकी आँखों के सामने।</p>'
    assert hi in hero
    hero = hero.replace(hi, hi + '\n        <p><a class="textlink" href="telugu.html" lang="te">తెలుగులో చదవండి</a></p>')
    svc = SEC["services"]
    a1 = '<a class="btn btn-wa" href="#contact" data-tab="release">Get my release quote</a>'
    a2 = '<a class="btn btn-wa" href="#contact" data-tab="sell">Ask for a quote</a>'
    assert a1 in svc and a2 in svc
    svc = svc.replace(a1, a1 + '\n        <a class="textlink" href="release-pledged-gold.html">How release works</a>')
    svc = svc.replace(a2, a2 + '\n        <a class="textlink" href="sell-gold.html">How selling works</a>')
    find = f"""<section class="sec" id="find"><div class="wrap"><div class="sec-head"><p class="eyebrow">Find us</p><h2>Near Manjeera Trinity Homes, Kukatpally</h2>
<p>{ADDR_FULL}. We serve customers across Hyderabad, India and abroad. Message us on WhatsApp before you visit so we can confirm timings.</p></div>
<div class="cta-row" style="margin-top:0"><a class="btn btn-ghost" href="{MAPS}" target="_blank" rel="noopener">Open in Google Maps</a>
<a class="btn btn-ghost" href="gold-buyers-in-hyderabad.html">Gold buyers in Hyderabad</a>
<a class="btn btn-ghost" href="gold-buyers-in-kukatpally.html">Gold buyers in Kukatpally</a></div></div></section>"""
    gteaser = '<section class="sec" id="guides" style="padding-top:0"><div class="wrap"><div class="sec-head"><p class="eyebrow">Free guides</p><h2>Learn before you sell</h2><p>Plain-language guides on valuing gold, releasing pledged gold and avoiding scams.</p></div><div class="grid3">' + \
        "".join(card(g["slug"] + ".html", g["h1"][0].upper() + g["h1"][1:], g["desc"]) for g in GUIDES[:3]) + \
        '</div><p style="margin-top:1rem"><a class="textlink" href="guides.html">See all guides</a></p></div></section>'
    main = "\n".join([hero, svc, SEC["promise"], SEC["moments"], SEC["process"], SEC["estimator"], forms_block("release"), SEC["safety"],
                      gteaser, faq_block(FAQS[:8]).replace("</div></div></section>", '</div><p style="margin-top:1rem"><a class="textlink" href="faq.html">Read all questions and answers</a></p></div></section>'),
                      find, cta_band()])
    # keep the service hub links visible on the home page
    title = "Sell Old Gold, Release Pledged Gold, Hyderabad | ClearKarat"
    desc = "ClearKarat buys old gold and pledged gold in Hyderabad. We weigh and test in front of you, put every number on a written slip, and you are free to say no."
    add("index.html", shell("index.html", title, desc, fill(main), [ld_business(), ld_site(), ld_faq(FAQS[:8])]))

# ---------------------------------------------------------------- pages
def build_pages():
    build_home()
    add("sell-gold.html", content_page("sell-gold.html", "Sell Old Gold in Hyderabad at Today's Rate | ClearKarat",
        "Sell old gold jewellery, coins and broken pieces in Hyderabad. Weighed on an open scale, tested in front of you, priced on a written slip. Free to say no.",
        "Sell old gold in Hyderabad", "Old gold buying", "Weighed on a scale that faces you, tested at your side, and priced on a written slip. If the number is not right for you, you leave with your gold.",
        SELL_BODY, [("Services", "index.html#services")], [ld_service("Old gold buying", "Buying old gold jewellery, coins and broken pieces at the day's rate with open weighing and testing.", "sell-gold.html")],
        forms="sell", faq=faq_pick([0, 1, 2, 3, 9, 10])))
    add("release-pledged-gold.html", content_page("release-pledged-gold.html", "Release Pledged Gold in Hyderabad | ClearKarat",
        "We buy pledged gold at the day's market price, clear your loan with the lender and pay you the rest. Every figure on a written slip first.",
        "Release your pledged gold in Hyderabad", "Pledged gold release", "We buy your pledged gold at the day's current market price, clear your loan with your lender, and pay you the rest of the money.",
        RELEASE_BODY, [("Services", "index.html#services")], [ld_service("Pledged gold release", "Buying pledged gold at the day's market price, clearing the loan with the lender and paying the customer the remaining money.", "release-pledged-gold.html")],
        forms="release", faq=faq_pick([4, 5, 6, 7, 3, 11])))
    add("gold-estimator.html", content_page("gold-estimator.html", "Gold Value Calculator for 22K, 24K and 18K | ClearKarat",
        "Estimate the value of your old or pledged gold. Enter weight, purity, today's rate and any loan payoff to see the slip arithmetic ClearKarat uses.",
        "Gold value calculator", "Estimate your gold", "Work out a rough value for your old or pledged gold. It uses the same arithmetic that goes on your written slip.",
        ESTIMATOR_INTRO, [("Services", "index.html#services")], [ld_service("Gold value calculator", "Online calculator to estimate the value of old or pledged gold from weight, purity and rate.", "gold-estimator.html")],
        faq=faq_pick([0, 2, 8]), side=False,
        after=""))
    # estimator page: put the live calculator right after the hero
    est = PAGES["gold-estimator.html"]
    est = est.replace('<section class="sec" style="padding-top:0"><div class="wrap"><div class="prose"', SEC["estimator"].replace('style="background:var(--surface-2)"', 'style="background:var(--surface-2)"') + '<section class="sec"><div class="wrap"><div class="prose"', 1)
    PAGES["gold-estimator.html"] = est
    if HOME_VISIT:
        add("home-visit-gold-evaluation.html", content_page("home-visit-gold-evaluation.html", "Home Visit Gold Evaluation in Hyderabad | ClearKarat",
            "Ask for a gold evaluation at your home in Hyderabad. Weighed and tested in front of you with a written slip, and no obligation to sell.",
            "Home visit gold evaluation in Hyderabad", "Doorstep evaluation", "Have your gold weighed and tested at your door, with the numbers on a written slip and no obligation to sell.",
            HOME_VISIT_BODY, [("Services", "index.html#services")], [ld_service("Home visit gold evaluation", "Gold weighed and tested at the customer's home with a written slip and no obligation to sell.", "home-visit-gold-evaluation.html")],
            forms="sell", faq=faq_pick([3, 10, 12])))
    add("gold-buyers-in-hyderabad.html", content_page("gold-buyers-in-hyderabad.html", "Open-Scale Gold Buyers in Hyderabad | ClearKarat",
        "ClearKarat buys old and pledged gold across Hyderabad. Weighed and tested in front of you, with a written slip. Near Manjeera Trinity Homes, Kukatpally.",
        "Gold buyers in Hyderabad", "Hyderabad", "Sell old gold or release pledged gold with the weight, the test and the price shown to you first.",
        HYD_BODY, [], [], forms="sell", faq=faq_pick([11, 0, 3, 12])))
    add("gold-buyers-in-kukatpally.html", content_page("gold-buyers-in-kukatpally.html", "Gold Buyers in Kukatpally, Hyderabad | ClearKarat",
        "Sell old gold or release pledged gold in Kukatpally. ClearKarat is near Manjeera Trinity Homes, with open weighing, testing and a written slip.",
        "Gold buyers in Kukatpally, Hyderabad", "Kukatpally", "Based near Manjeera Trinity Homes. Bring your gold, or message us first and we will tell you what to bring.",
        KUK_BODY, [("Hyderabad", "gold-buyers-in-hyderabad.html")], [], forms="sell", faq=faq_pick([0, 3, 4, 12])))
    add("about.html", content_page("about.html", "About ClearKarat | Transparent Gold Buyers in Hyderabad",
        "ClearKarat buys old and pledged gold in plain sight: open scale, purity tested at your side, written slip, free to say no. Learn how we work.",
        "About ClearKarat", "Who we are", "Gold buyers built around one idea: do everything in plain sight, so nobody has to take our word for it.",
        ABOUT_BODY, [], []))
    add("transparency.html", content_page("transparency.html", "Our Plain Sight Promise | ClearKarat",
        "The six things ClearKarat does in front of you: open scale, purity test, itemised slip, written quote, free to say no and named charges.",
        "The Plain Sight Promise", "Transparency", "Six things we do in front of you, what is on every slip, and what we will never do.",
        TRANSPARENCY_BODY, [("About", "about.html")], [], faq=faq_pick([12, 13])))
    add("faq.html", content_page("faq.html", "Gold Selling and Pledge Release FAQ | ClearKarat",
        "Answers about valuing gold, purity testing, stone deduction, documents, payment, pledged gold release and safety at ClearKarat, Hyderabad.",
        "Questions and answers", "FAQ", "Clear answers about how we value gold, release pledged gold and keep everything in plain sight.",
        "<p>Cannot find your question? Message us on WhatsApp at {PHONE} and we will answer it.</p>", [], [], faq=FAQS, side=True))
    add("contact.html", content_page("contact.html", "Contact ClearKarat | WhatsApp, Call and Visit in Kukatpally",
        "Contact ClearKarat on WhatsApp or call +91 63006 95591, email clearkaratcare@gmail.com or visit near Manjeera Trinity Homes, Kukatpally, Hyderabad 500072.",
        "Contact ClearKarat", "Talk to us", "WhatsApp, call, email or visit. The forms below open WhatsApp with your message ready to send.",
        CONTACT_INTRO, [], [ld_business()], forms="release", side=False))
    gl = "".join(card(g["slug"] + ".html", g["h1"][0].upper() + g["h1"][1:], g["desc"]) for g in GUIDES)
    add("guides.html", content_page("guides.html", "Gold Selling Guides and Articles | ClearKarat",
        "Free guides on how old gold is valued, releasing pledged gold, purity and hallmarks, testing methods, documents, scams and the gold rate.",
        "Gold guides", "Learn before you sell", "Plain-language guides to help you understand your gold, your loan and your options.",
        f'<div class="grid3" style="grid-template-columns:repeat(2,1fr)">{gl}</div>', [], [], side=False))
    for i, g in enumerate(GUIDES):
        rel = [GUIDES[(i + k) % len(GUIDES)] for k in (1, 2, 3)]
        keys = '<div class="callout keys"><b>Key takeaways</b><ul>' + "".join(f"<li>{t}</li>" for t in g["takeaways"]) + "</ul></div>"
        after = '<section class="sec"><div class="wrap"><div class="sec-head"><p class="eyebrow">Keep reading</p><h2>Related guides and services</h2></div><div class="grid3">' + \
            "".join(card(r["slug"] + ".html", r["h1"][0].upper() + r["h1"][1:], r["desc"]) for r in rel[:2]) + \
            card("release-pledged-gold.html" if i % 2 == 0 else "sell-gold.html", "Release pledged gold" if i % 2 == 0 else "Sell old gold", "See how ClearKarat does it in plain sight.") + "</div></div></section>"
        add(g["slug"] + ".html", content_page(g["slug"] + ".html", g["title"], g["desc"], g["h1"][0].upper() + g["h1"][1:], "Guide",
            g["desc"], keys + g["body"], [("Guides", "guides.html")], [ld_article(g["h1"], g["desc"], g["slug"] + ".html")],
            meta=f"Updated {UPDATED_H} &middot; ClearKarat", after=after, og_type="article"))
    add("telugu.html", content_page("telugu.html", "హైదరాబాద్‌లో బంగారం అమ్మకం, తాకట్టు బంగారం విడిపించడం | ClearKarat",
        "హైదరాబాద్‌లో పాత బంగారం అమ్మండి లేదా తాకట్టు బంగారం విడిపించుకోండి. బరువు, స్వచ్ఛత, రేటు మీ కళ్ల ముందే. కూకట్‌పల్లి, మంజీరా ట్రినిటీ హోమ్స్ దగ్గర.",
        "హైదరాబాద్‌లో పాత బంగారం అమ్మండి లేదా తాకట్టు బంగారం విడిపించుకోండి", "తెలుగు", "మీ బంగారం, మీ షరతులు, మీ కళ్ల ముందే. ధర కాగితంపై చూసిన తర్వాతే నిర్ణయం తీసుకోండి.",
        TELUGU_BODY, [], [], lang="te"))
    add("privacy-policy.html", content_page("privacy-policy.html", "Privacy Policy | ClearKarat", "How ClearKarat handles information on its website and when you message or visit us.",
        "Privacy policy", "Legal", "How we handle information when you use this website or contact us.", PRIVACY_BODY, [], [], side=False))
    add("terms.html", content_page("terms.html", "Terms of Use | ClearKarat", "Terms for using the ClearKarat website: estimates, no obligation, pledged gold and safety.",
        "Terms of use", "Legal", "The terms that apply when you use this website.", TERMS_BODY, [], [], side=False))
    # 404
    nf = f"""<section class="phero"><div class="wrap"><p class="eyebrow">Page not found</p><h1>We could not find that page</h1><p class="lead">The link may be old. Try one of these.</p>
<div class="cta-row"><a class="btn btn-wa" href="index.html">Go to the home page</a><a class="btn btn-ghost" href="sell-gold.html">Sell gold</a><a class="btn btn-ghost" href="release-pledged-gold.html">Release pledged gold</a></div></div></section>"""
    add("404.html", shell("404.html", "Page not found | ClearKarat", "This page could not be found.", nf, [], robots="noindex"))

# ---------------------------------------------------------------- assets
FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F6D983"/><stop offset=".5" stop-color="#D4A237"/><stop offset="1" stop-color="#94680F"/></linearGradient></defs>
<circle cx="32" cy="32" r="30" fill="url(#g)"/><circle cx="32" cy="32" r="24.5" fill="none" stroke="#10262B" stroke-opacity=".55" stroke-width="1.4"/>
<path d="M24 17.5V46.5M25.5 32.5L41 17.5M28.5 30.5L42 46.5" fill="none" stroke="#10262B" stroke-width="5.6"/>
<path d="M12.5 24.5A21 21 0 0 1 27 11.5" fill="none" stroke="#FFFFFF" stroke-opacity=".75" stroke-width="2.4" stroke-linecap="round"/></svg>"""

def write_all():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    build_pages()
    for slug, h_ in PAGES.items():
        open(os.path.join(OUT, slug), "w", encoding="utf-8").write(h_)
    open(os.path.join(OUT, "styles.css"), "w", encoding="utf-8").write(CSS + EXTRA_CSS)
    open(os.path.join(OUT, "app.js"), "w", encoding="utf-8").write(APP_JS)
    open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8").write(FAVICON)
    pri = {"index.html": "1.0", "sell-gold.html": "0.9", "release-pledged-gold.html": "0.9", "gold-estimator.html": "0.8",
           "gold-buyers-in-hyderabad.html": "0.8", "gold-buyers-in-kukatpally.html": "0.8", "home-visit-gold-evaluation.html": "0.7"}
    urls = "".join(f"<url><loc>{url(s)}</loc><lastmod>{UPDATED}</lastmod><priority>{pri.get(s, '0.6')}</priority></url>\n"
                   for s in sorted(PAGES) if s != "404.html")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    print(len(PAGES), "pages ->", os.path.abspath(OUT))

if __name__ == "__main__":
    write_all()
