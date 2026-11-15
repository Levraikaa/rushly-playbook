"""Génère playbook-acquisition.html à partir de data.json.

Usage : python3 playbook/build.py
Pour ajouter une vidéo : l'ajouter dans data.json sous le bon créateur, puis relancer.
"""
import base64
import json
from html import escape as e
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE.parent / "playbook-acquisition.html"
data = json.loads((HERE / "data.json").read_text())
# Ce qui n'est pas pertinent pour Rushly (❌) n'apparaît pas sur la page.
for c in data["createurs"]:
    c["videos"] = [v for v in c["videos"] if v["verdict"] != "bad"]
    for v in c["videos"]:
        v["points"] = [pt for pt in v["points"] if pt[0] != "bad"]

EMO = {"ok": "✅", "warn": "⚠️", "bad": "❌"}


def b64(name):
    return base64.b64encode((HERE / "assets" / name).read_bytes()).decode()


def tc(sec):
    h, r = divmod(int(sec), 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


import datetime as _dt
TODAY = _dt.date.today()


def is_new(x):
    a = x.get("ajoute") if isinstance(x, dict) else None
    if not a:
        return False
    j, m, y = (int(p) for p in a.split("/"))
    return (TODAY - _dt.date(y, m, j)).days <= 14


NEW = '<span class="new">New</span>'
COURTS = data.get("courts", {})


def idea_html(idea):
    verdict, titre, detail, rushly, srcs = idea[:5]
    extra = idea[5] if len(idea) > 5 else {}
    vids = list(dict.fromkeys(v for v, _ in srcs))
    rep = f'<span class="rep">Revient dans {len(vids)} vidéos</span>' if len(vids) > 1 else ""
    chips = "".join(
        f'<a class="srcchip" href="https://www.youtube.com/watch?v={v}&amp;t={t}s" target="_blank" rel="noopener">{e(COURTS.get(v, v))} · {tc(t)}</a>'
        for v, t in srcs)
    r = f'<p class="idea-r">→ {e(rushly)}</p>' if rushly else ""
    dd = f'<p class="idea-d">{e(detail)}</p>' if detail else ""
    return f'''<li class="idea{' is-rep' if rep else ''}"><div class="idea-h"><span class="v">{EMO[verdict]}</span><h4>{e(titre)}</h4>{NEW if is_new(extra) else ""}{rep}</div>{dd}{r}<div class="srcs">{chips}</div></li>'''


def synth_html(c):
    if not c.get("synthese"):
        return ""
    blocks = []
    for th in c["synthese"]:
        ideas = [i for i in th["idees"] if i[0] != "bad"]
        ideas.sort(key=lambda i: -len(set(v for v, _ in i[4])))
        blocks.append(f'<div class="theme"><h3 class="tname">{e(th["theme"])}</h3><ul class="ideas">{"".join(idea_html(i) for i in ideas)}</ul></div>')
    return f'<section class="essentiel"><h2 class="ess-h">L\'essentiel</h2>{"".join(blocks)}</section>'


def video_html(v):
    items = []
    for verdict, bold, text, rushly, t in v["points"]:
        r = f'<span class="r">→ {e(rushly)}</span>' if rushly else ""
        link = (f'<a class="tc" href="https://www.youtube.com/watch?v={v["id"]}&amp;t={t}s" target="_blank" rel="noopener">{tc(t)}</a>'
                if v["id"] and t is not None else "<span></span>")
        items.append(f'<li><span class="v">{EMO[verdict]}</span><span class="t"><b>{e(bold)}</b> {e(text)}{r}</span>{link}</li>')
    meta = " · ".join(x for x in [v["duree"]] if x)
    watch = (f'<a class="watch" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener">Voir la vidéo</a>'
             if v["id"] else "")
    return f'''<details class="card vid">
  <summary><span class="sum"><span class="vtitle"><span class="badge b-{v["verdict"]}">{EMO[v["verdict"]]}</span><h3>{e(v["titre"])}</h3>{NEW if is_new(v) else ""}</span><span class="key">{e(v["key"])}</span>{f'<span class="meta">{e(meta)}</span>' if meta else ""}</span><span class="chev" aria-hidden="true"></span></summary>
  <div class="content"><ul>{"".join(items)}</ul>{watch}</div>
</details>'''


def counts(c):
    n = {"ok": 0, "warn": 0, "bad": 0}
    for v in c["videos"]:
        n[v["verdict"]] += 1
    return " ".join(f'<span class="cnt">{EMO[k]} {n[k]}</span>' for k in n if n[k])


creator_cards, creator_details = [], []
for c in data["createurs"]:
    av = f'data:image/jpeg;base64,{b64(c["avatar"])}'
    nb = len(c["videos"])
    creator_cards.append(f'''<a class="card ccard" href="#{c["id"]}" data-open="{c["id"]}">
  <img class="avatar" src="{av}" alt="Photo de profil de {e(c["nom"])}" width="64" height="64">
  <span class="ctext"><span class="cname">{e(c["nom"])}{NEW if any(is_new(v) for v in c["videos"]) else ""}</span><span class="csub">{e(c["sous"])}</span><span class="cmeta">{nb} vidéo{"s" if nb > 1 else ""} · {counts(c)}</span></span>
  <span class="go" aria-hidden="true"></span>
</a>''')
    chan = (f'<a class="chan" href="{c["chaine"]}" target="_blank" rel="noopener">Voir la chaîne</a>' if c["chaine"] else "")
    creator_details.append(f'''<div class="cdetail" id="d-{c["id"]}" hidden>
  <button type="button" class="back" data-back>← Tous les créateurs</button>
  <div class="chead"><img class="avatar big" src="{av}" alt="Photo de profil de {e(c["nom"])}" width="80" height="80"><div class="ctext"><h2 class="cbig">{e(c["nom"])}</h2><span class="csub">{e(c["sous"])}</span>{chan}</div></div>
  {synth_html(c)}
  <details class="allvids">
    <summary><span>Les {nb} vidéos analysées</span><span class="chev" aria-hidden="true"></span></summary>
    <div class="toolbar"><button type="button" class="ghost" data-all="1">Tout dérouler</button><button type="button" class="ghost" data-all="0">Tout replier</button></div>
    <div class="vlist">{"".join(video_html(v) for v in c["videos"])}</div>
  </details>
</div>''')

groups = []
for q in dict.fromkeys(x["quand"] for x in data["canaux"]):
    rows = "".join(f'<li class="card chitem"><span class="chname">{e(x["nom"])}</span><span class="chtxt">{e(x["txt"])}</span></li>' for x in data["canaux"] if x["quand"] == q)
    groups.append(f'<div class="chgroup"><h3 class="chwhen">{e(q)}</h3><ul class="chlist">{rows}</ul></div>')
canaux = "".join(groups)
regles = "".join(f'<li class="rule"><span class="rule-t">{e(t)}</span><span class="rule-d">{e(x)}</span></li>' for t, x in data.get("regles", []))
regles_html = f'<article class="card rules"><h3>Règles du compte Rushly</h3><ul class="rlist">{regles}</ul></article>' if regles else ""

av = data.get("avatar")
avatar_html = ""
if av:
    qui = "".join(f'<li class="avwho"><span class="avwho-t">{e(t)}</span><span class="avwho-s">{e(sub)}</span></li>' for t, sub in av["qui"])
    def chips(xs, cls, mark):
        return "".join(f'<li class="chip {cls}"><span class="mk" aria-hidden="true">{mark}</span>{e(x)}</li>' for x in xs)
    objs = "".join(f'<li class="obj"><span class="obj-q">{e(q)}</span><span class="obj-a">{e(r)}</span></li>' for q, r in av["objections"])
    rythme = "".join(f'<li class="avr"><span class="avr-n">{e(n)}</span><span class="avr-t">{e(t)}</span><span class="avr-p">Offre {e(p)}</span></li>' for n, t, p in av["rythme"])
    p = av["phrase"]
    avatar_html = f'''<details class="card vid avcard" id="avatar" open>
  <summary><span class="sum"><h3 class="avtitle">Avatar</h3></span><span class="chev" aria-hidden="true"></span></summary>
  <div class="content avbody">
    <ul class="avwhos">{qui}</ul>
    <div class="avcols">
      <div><h4>Il veut</h4><ul class="chips">{chips(av["veut"], "c-ok", "✓")}</ul></div>
      <div><h4>Ce qui le bloque</h4><ul class="chips">{chips(av["bloque"], "c-bad", "✕")}</ul></div>
      <div><h4>Ses peurs</h4><ul class="chips">{chips(av["peurs"], "c-warn", "?")}</ul></div>
    </div>
    <div class="avcols">
      <div><h4>Ce qu'il filme</h4><ul class="chips">{chips(av["filme"], "c-neu", "●")}</ul></div>
      <div><h4>Où il poste</h4><ul class="chips">{chips(av["poste"], "c-neu", "●")}</ul></div>
    </div>
    <div><h4>Son rythme</h4><ul class="avrythm">{rythme}</ul></div>
    <div class="avcols">
      <div><h4>Ce qu'il a déjà essayé</h4><ul class="chips">{chips(av["essaye"], "c-neu", "●")}</ul></div>
      <div><h4>Où le trouver</h4><ul class="chips">{chips(av["ou"], "c-neu", "●")}</ul></div>
    </div>
    <div><h4>Ce qui le fait payer</h4><ul class="chips">{chips(av["paye"], "c-ok", "✓")}</ul></div>
    <div><h4>Ses objections, et la réponse</h4><ul class="objs">{objs}</ul></div>
  </div>
</details>'''

tests = "".join(f'''<article class="card test">
  <div class="thead"><h3>{e(t["titre"])}</h3><span class="status">{e(t["statut"])} · {e(t["duree"])}</span></div>
    <p>{e(t["action"])}</p>
  <dl class="kpi"><dt>Succès</dt><dd>{e(t["succes"])}</dd><dt>Échec</dt><dd>{e(t["echec"])}</dd></dl>
</article>''' for t in data["tests"])
def src_html(src):
    who, vid, vid_id, t = src
    label = f"{who} · {vid}"
    if vid_id:
        t = t or 0
        return f'<a class="src" href="https://www.youtube.com/watch?v={vid_id}&amp;t={t}s" target="_blank" rel="noopener">{e(label)} · {tc(t)}</a>'
    return f'<span class="src">{e(label)}</span>'


steps = []
for i, ph in enumerate(data.get("roadmap", []), 1):
    items = "".join(
        f'<li><label class="check"><input type="checkbox" id="{iid}" data-item="{iid}"><span class="box" aria-hidden="true"></span><span class="ptxt">{e(txt)}</span></label></li>'
        for iid, txt in ph["items"])
    steps.append(f'''<li class="phase" data-step="{i}">
  <span class="dot" aria-hidden="true">{i}</span>
  <article class="card pcard">
    <div class="phead"><h3>{e(ph["titre"])}</h3><span class="prog" data-prog></span></div>
    <p class="lock" data-lock hidden>Termine l'étape {i - 1} pour débloquer celle-ci.</p>
    <ul class="pitems">{items}</ul>
  </article>
</li>''')
roadmap = "".join(steps)
formats = "".join(f'<li class="card fitem"><span class="fname">{e(f["nom"])}</span><span class="fdesc">{e(f["desc"])}</span><span class="status">{e(f["statut"])}</span></li>' for f in data["formats"])
hooks = "".join(f'<li class="card hitem"><span>{e(h["txt"])}</span><span class="status">{e(h["statut"])}</span></li>' for h in data["hooks"])

fonts = "".join(
    f'@font-face {{ font-family: "{fam}"; font-weight: {w}; font-style: normal; font-display: swap; src: url(data:font/woff2;base64,{b64(f)}) format("woff2"); }}\n'
    for fam, w, f in [("Satoshi", 400, "satoshi-400.woff2"), ("Satoshi", 500, "satoshi-500.woff2"),
                      ("Satoshi", 700, "satoshi-700.woff2"), ("General Sans", 600, "general-sans-600.woff2")])

CSS = fonts + (HERE / "style.css").read_text() + (HERE / "studio.css").read_text()


studio = data["studio"]
fmt_opts = "".join(f'<option value="{e(f["nom"])}">{e(f["nom"])}</option>' for f in data["formats"])
statuts = "".join(f'<option value="{x}">{x}</option>' for x in ["Idée", "En écriture", "Validé", "Prêt à tourner", "Tourné", "Posté"])


studio_html = f"""<p class="warnline" id="saveErr" hidden>Sauvegarde impossible. Copie ton texte avant de quitter la page.</p>
  <section class="tab" id="scriptEdit" hidden>
    <article class="card editor" id="editor">
      <div class="etop">
        <button type="button" class="back" id="backScripts"></button>
        <div class="btnrow">
          <button type="button" class="btn small" id="copyScript">Copier</button>
          <button type="button" class="btn small" id="delScript">Supprimer</button>
        </div>
      </div>
      <div class="fsource" id="fSource" hidden></div>
      <label class="field"><span>Sujet</span><input type="text" id="fSujet" data-f="sujet" autocomplete="off"></label>
      <div class="field2">
        <label class="field"><span>Format</span><select data-f="format"><option value="">Libre</option>{fmt_opts}</select></label>
        <label class="field"><span>Statut</span><select data-f="statut">{statuts}</select></label>
      </div>
      <div class="ehead"><h3>Script</h3><span class="wcount" id="wcount"></span></div>
      <textarea id="fNotes" class="bigta" data-f="notes" rows="16" aria-label="Script"></textarea>
    </article>
  </section>
  <section class="tab" id="calendrier" hidden>
    <div class="shead shead-row"><h2 id="calTitle"></h2><div class="btnrow"><button type="button" class="btn small" id="calPrev" aria-label="Mois précédent">‹</button><button type="button" class="btn small" id="calToday">Aujourd'hui</button><button type="button" class="btn small" id="calNext" aria-label="Mois suivant">›</button></div></div>
    <div class="card calcard"><div class="cal-head" aria-hidden="true"><span>Lun</span><span>Mar</span><span>Mer</span><span>Jeu</span><span>Ven</span><span>Sam</span><span>Dim</span></div><div class="cal-grid" id="calGrid"></div><div class="cal-leg" aria-label="Couleurs par statut"><span><i data-st="0"></i>Idée</span><span><i data-st="1"></i>En écriture</span><span><i data-st="2"></i>Validé</span><span><i data-st="3"></i>Prêt à tourner</span><span><i data-st="4"></i>Tourné</span><span><i data-st="5"></i>Posté</span></div></div>
  </section>
  <section class="tab" id="idees" hidden>
    <div class="shead"><h2>Idées</h2></div>
    <form class="ideeadd" id="iForm"><input type="text" id="iTxt" aria-label="Nouvelle idée de vidéo" placeholder="Une idée de vidéo" autocomplete="off"><button type="submit" class="btn primary">Ajouter</button></form>
    <p class="empty" id="iEmpty">Aucune idée pour l'instant.</p>
    <ul class="vlist" id="iList"></ul>
  </section>
  <section class="tab" id="valides" hidden>
    <div class="shead"><h2>Validés</h2><p>Les scripts prêts à tourner.</p></div>
    <p class="empty" id="okEmpty">Aucun script validé pour l'instant.</p>
    <ul class="vlist" id="okList"></ul>
  </section>
  <section class="tab" id="exemples" hidden>
    <div class="shead"><h2>Exemples</h2><p>Tes vidéos qui ont le mieux marché, avec leur script.</p></div>
    <p class="empty" id="xEmpty">Aucun exemple pour l'instant.</p>
    <ul class="vlist" id="xList"></ul>
  </section>
  <section class="tab" id="veille">
    <div class="shead"><h2>Veille</h2></div>
    <p class="empty" id="vEmpty">Aucune vidéo repérée pour l'instant.</p>
    <div class="vtags" id="vTags" hidden></div>
    <ul class="vlist" id="vList"></ul>
    <div class="pane" data-only="rushly">
      <div class="shead"><h2>Formats</h2><p>Validé = a percé au moins 3 fois à plus de 100 000 vues.</p></div>
      <ul class="flist">{formats}</ul>
    </div>
  </section>
"""
studio_js = (HERE / "studio.js").read_text()

html = f'''<title>Playbook viral Rushly</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
{CSS}
</style>
<header class="hero">
  <div class="projs" role="group" aria-label="Projet">
    <button type="button" data-proj="rushly" aria-pressed="true">RUSHLY</button>
    <button type="button" data-proj="perso" aria-pressed="false">KILIAN ADAM</button>
    <button type="button" data-proj="quentin" aria-pressed="false">QUENTIN</button>
  </div>
  <h1>Le playbook <span class="pill">viral</span><span class="line2" id="heroLine">de RUSHLY.</span></h1>
  <nav class="tabs" aria-label="Parties du playbook">
    <button type="button" data-tab="calendrier" aria-pressed="false">Calendrier</button>
    <button type="button" data-tab="veille" aria-pressed="true">Veille</button>
    <button type="button" data-tab="createurs" data-only="rushly" aria-pressed="false">Créateurs</button>
    <button type="button" data-tab="plan" data-only="rushly" aria-pressed="false">Plan</button>
    <button type="button" data-tab="valides" aria-pressed="false">Validés</button>
    <button type="button" data-tab="exemples" data-only="perso" aria-pressed="false">Exemples</button>
    <button type="button" data-tab="idees" aria-pressed="false">Idées</button>
  </nav>
</header>
<main class="wrap">
  {studio_html}
  <section class="tab" id="createurs" hidden>
    <div class="shead"><h2>Créateurs</h2></div>
    {avatar_html}
    <div class="cgrid" id="clist">{"".join(creator_cards)}</div>
    {"".join(creator_details)}
  </section>
  <section class="tab" id="plan" hidden>
    <div class="subnav" role="group" aria-label="Parties du plan">
      <button type="button" data-sub="roadmap" aria-pressed="true">Roadmap</button>
      <button type="button" data-sub="canaux" aria-pressed="false">Canaux</button>
      <button type="button" data-sub="tests" aria-pressed="false">Tests</button>
    </div>
    <div class="pane" id="roadmap">
      <ol class="timeline">{roadmap}</ol>
    </div>
    <div class="pane" id="canaux" hidden>
      {regles_html}
      {canaux}
    </div>
    <div class="pane" id="tests" hidden>
      <div class="tlist">{tests}</div>
    </div>
  </section>
</main>
<script>
(function () {{
  var tabs = Array.prototype.slice.call(document.querySelectorAll('[data-tab]'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('.tab'));
  var list = document.getElementById('clist');
  function showTab(id) {{
    tabs.forEach(function (b) {{ b.setAttribute('aria-pressed', String(b.dataset.tab === id)); }});
    sections.forEach(function (s) {{ s.hidden = s.id !== id; }});
  }}
  function showCreator(id) {{
    showTab('createurs');
    var found = false;
    document.querySelectorAll('.cdetail').forEach(function (d) {{ var on = d.id === 'd-' + id; d.hidden = !on; if (on) found = true; }});
    list.hidden = found;
    var avc = document.getElementById('avatar'); if (avc) avc.hidden = found;
    document.querySelector('#createurs .shead').hidden = found;
    window.scrollTo({{ top: document.querySelector('.hero').offsetHeight - 40, behavior: 'smooth' }});
  }}
  function showList() {{
    document.querySelectorAll('.cdetail').forEach(function (d) {{ d.hidden = true; }});
    list.hidden = false;
    var avc = document.getElementById('avatar'); if (avc) avc.hidden = false;
    document.querySelector('#createurs .shead').hidden = false;
  }}
  tabs.forEach(function (b) {{ b.addEventListener('click', function () {{ showTab(b.dataset.tab); if (b.dataset.tab === 'createurs') showList(); }}); }});
  document.querySelectorAll('[data-open]').forEach(function (a) {{ a.addEventListener('click', function (ev) {{ ev.preventDefault(); showCreator(a.dataset.open); }}); }});
  document.querySelectorAll('[data-back]').forEach(function (b) {{ b.addEventListener('click', showList); }});
  document.querySelectorAll('[data-all]').forEach(function (b) {{ b.addEventListener('click', function () {{
    var open = b.dataset.all === '1';
    b.closest('.allvids').querySelectorAll('details.vid').forEach(function (d) {{ d.open = open; }});
  }}); }});

  // Roadmap : cases cochées, sauvegardées dans la base de l'artefact
  var boxes = Array.prototype.slice.call(document.querySelectorAll('[data-item]'));
  var steps = Array.prototype.slice.call(document.querySelectorAll('.phase'));
  var done = {{}};
  var db = null;
  var writing = Promise.resolve();
  function paint() {{
    var unlocked = true;
    steps.forEach(function (st) {{
      var bx = Array.prototype.slice.call(st.querySelectorAll('[data-item]'));
      var n = bx.filter(function (b) {{ return done[b.dataset.item]; }}).length;
      bx.forEach(function (b) {{ b.checked = !!done[b.dataset.item]; b.disabled = !unlocked; }});
      st.classList.toggle('locked', !unlocked);
      st.classList.toggle('complete', unlocked && n === bx.length);
      st.querySelector('[data-lock]').hidden = unlocked;
      st.querySelector('[data-prog]').textContent = n + ' / ' + bx.length;
      if (n < bx.length) unlocked = false;
    }});
  }}
  function save() {{
    var body = {{ done: Object.assign({{}}, done) }};
    if (db) {{ writing = writing.then(function () {{ return db.doc('roadmap/progress').set(body); }}).catch(function () {{}}); }}
    else {{ try {{ localStorage.setItem('rushly-roadmap', JSON.stringify(body.done)); }} catch (err) {{}} }}
  }}
  boxes.forEach(function (b) {{ b.addEventListener('change', function () {{
    if (b.checked) done[b.dataset.item] = true; else delete done[b.dataset.item];
    paint(); save();
  }}); }});
  try {{ done = JSON.parse(localStorage.getItem('rushly-roadmap') || '{{}}') || {{}}; }} catch (err) {{ done = {{}}; }}
  paint();
  if (window.claude && window.claude.use) {{
    window.claude.use('db').then(function (d) {{
      if (!d) return;
      db = d;
      db.doc('roadmap/progress').onSnapshot(function (snap) {{
        var body = snap.exists ? snap.data() : null;
        done = Object.assign({{}}, (body && body.done) || {{}});
        paint();
      }}, function () {{}});
    }}).catch(function () {{}});
  }}
  var h = location.hash.slice(1);
  if (h && document.getElementById('d-' + h)) showCreator(h);
  else if (h && document.getElementById(h) && document.getElementById(h).classList.contains('tab')) showTab(h);
}})();
</script>
<script>
{studio_js}
</script>
'''
OUT.write_text(html)
print(f"OK {OUT.name} {len(html)//1024} Ko, {len(data['createurs'])} créateurs, {sum(len(c['videos']) for c in data['createurs'])} vidéos")
