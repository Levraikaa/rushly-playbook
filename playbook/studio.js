// Studio : projets séparés, scripts et hooks. Données dans la base de l'artefact.
(function () {
  var PROJ = {
    rushly: { nom: 'RUSHLY', titre: 'de RUSHLY.' },
    perso: { nom: 'KILIAN ADAM', titre: 'de KILIAN ADAM.' },
    quentin: { nom: 'QUENTIN', titre: 'de QUENTIN.' }
  };
  var STATUTS = ['Idée', 'En écriture', 'Validé', 'Prêt à tourner', 'Tourné', 'Posté'];
  var ETATS = { 'a-tester': 'À tester', 'a-marche': 'A marché', 'flop': 'N\'a pas marché' };

  var $ = function (id) { return document.getElementById(id); };
  var project = 'rushly';
  try { var p0 = localStorage.getItem('rushly-projet'); if (p0 && PROJ[p0]) project = p0; } catch (err) {}
  var maps = { scripts: {}, veille: {}, idees: {} };
  var last = {};
  try { last = JSON.parse(localStorage.getItem('rushly-onglets') || '{}') || {}; } catch (err) {}
  var db = null;
  var current = null, origin = 'scripts';
  var DEFAUT = { rushly: 'calendrier', perso: 'calendrier', quentin: 'calendrier' };
  var dirty = {}, timers = {}, chains = {};
  var ouverts = {};

  /* ---------- Sauvegarde ---------- */
  function local() { try { localStorage.setItem('rushly-studio', JSON.stringify(maps)); } catch (err) {} }
  function saveErr() { var n = $('saveErr'); if (n) n.hidden = false; }
  // Chaque modif n'écrit que les champs touchés : une modif faite ailleurs (autre onglet, Claude) n'est jamais écrasée.
  function flush(col, id) {
    var k = col + '/' + id;
    clearTimeout(timers[k]);
    var d = dirty[k];
    if (!d) return;
    delete dirty[k];
    var body = maps[col][id];
    if (!db || !body) return;
    var copy = JSON.parse(JSON.stringify(body));
    var ref = db.collection(col).doc(id);
    var part = null;
    if (d !== true) { part = {}; Object.keys(d).forEach(function (f) { part[f] = copy[f] === undefined ? null : copy[f]; }); }
    chains[k] = (chains[k] || Promise.resolve()).then(function () {
      if (!part) return ref.set(copy);
      return ref.update(part).catch(function () { return ref.set(copy); });
    }).catch(saveErr);
  }
  function persist(col, id, fields) {
    var k = col + '/' + id;
    if (!fields || dirty[k] === true) dirty[k] = true;
    else { dirty[k] = dirty[k] || {}; fields.forEach(function (f) { dirty[k][f] = true; }); }
    local();
    clearTimeout(timers[k]);
    timers[k] = setTimeout(function () { flush(col, id); }, 600);
  }
  function flushAll() { Object.keys(dirty).forEach(function (k) { var p = k.split('/'); flush(p[0], p[1]); }); }
  function remove(col, id) {
    var k = col + '/' + id;
    delete dirty[k]; clearTimeout(timers[k]);
    delete maps[col][id];
    local();
    if (db) chains[k] = (chains[k] || Promise.resolve()).then(function () { return db.collection(col).doc(id).delete(); }).catch(saveErr);
  }
  function newId(col) { return db ? db.collection(col).doc().id : 'l' + Date.now() + Math.floor(Math.random() * 1000); }
  document.addEventListener('visibilitychange', function () { if (document.hidden) flushAll(); });
  window.addEventListener('pagehide', flushAll);

  function subscribe(col) {
    db.collection(col).onSnapshot(function (snap) {
      var next = {};
      snap.docs.forEach(function (d) { next[d.id] = JSON.parse(JSON.stringify(d.data())); });
      Object.keys(dirty).forEach(function (k) {
        var p = k.split('/'), mine = maps[col][p[1]];
        if (p[0] !== col || !mine) return;
        if (dirty[k] === true || !next[p[1]]) { next[p[1]] = mine; return; }
        Object.keys(dirty[k]).forEach(function (f) { next[p[1]][f] = mine[f]; });
      });
      maps[col] = next;
      renderAll();
      // Un script ouvert mais pas en cours de frappe reprend la version de la base
      if (col === 'veille') document.querySelectorAll('.vedit').forEach(function (ed) {
        var doc = maps.veille[ed.dataset.id];
        if (doc && !dirty['veille/' + ed.dataset.id] && ed.value !== (doc.adapte || '')) ed.value = doc.adapte || '';
      });
    }, saveErr);
  }

  /* ---------- Espaces et navigation ---------- */
  function go(id) {
    var b = document.querySelector('[data-tab="' + id + '"]');
    if (!b || b.hidden) b = document.querySelector('[data-tab="' + DEFAUT[project] + '"]');
    b.click();
  }
  function applyProject() {
    $('heroLine').textContent = PROJ[project].titre;
    document.querySelectorAll('[data-proj]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.dataset.proj === project)); });
    document.querySelectorAll('[data-only]').forEach(function (b) { b.hidden = b.dataset.only !== project; });
  }
  function setProject(p) {
    if (p === project) return;
    flushAll();
    project = p;
    try { localStorage.setItem('rushly-projet', p); } catch (err) {}
    if (current) leaveEditor();
    applyProject();
    go(last[p] || DEFAUT[p]);
    renderAll();
  }
  document.querySelectorAll('[data-proj]').forEach(function (b) { b.addEventListener('click', function () { setProject(b.dataset.proj); }); });
  document.querySelectorAll('[data-tab]').forEach(function (b) {
    b.addEventListener('click', function () {
      last[project] = b.dataset.tab;
      try { localStorage.setItem('rushly-onglets', JSON.stringify(last)); } catch (err) {}
      if (current) leaveEditor();
    });
  });
  document.querySelectorAll('[data-sub]').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('[data-sub]').forEach(function (x) {
        x.setAttribute('aria-pressed', String(x === b));
        $(x.dataset.sub).hidden = x !== b;
      });
    });
  });

  /* ---------- Scripts ---------- */
  function scriptsOf() {
    return Object.keys(maps.scripts).map(function (id) { return Object.assign({ id: id }, maps.scripts[id]); })
      .filter(function (s) { return s.project === project; })
      .sort(function (a, b) { return (b.updated || 0) - (a.updated || 0); });
  }
  function createScript(init) {
    var id = newId('scripts');
    maps.scripts[id] = Object.assign({ project: project, sujet: '', format: '', statut: STATUTS[0], notes: '', updated: Date.now() }, init || {});
    persist('scripts', id);
    return id;
  }
  function openScript(id) {
    var active = document.querySelector('[data-tab][aria-pressed="true"]');
    origin = active ? active.dataset.tab : 'scripts';
    current = id;
    document.querySelectorAll('.tab').forEach(function (t) { t.hidden = t.id !== 'scriptEdit'; });
    $('backScripts').textContent = '← Calendrier';
    $('delScript').textContent = 'Supprimer';
    $('delScript').dataset.arm = '';
    fillEditor();
    window.scrollTo({ top: document.querySelector('.hero').offsetHeight - 110 });
  }
  function isBlank(s) {
    return !['sujet', 'notes'].some(function (f) { return (s[f] || '').trim(); });
  }
  function leaveEditor() {
    var id = current;
    current = null;
    if (maps.scripts[id] && isBlank(maps.scripts[id])) remove('scripts', id);
    flushAll();
    renderCal();
  }
  function closeEditor() {
    leaveEditor();
    go(origin);
  }
  function fillEditor() {
    var s = maps.scripts[current];
    if (!s) { closeEditor(); return; }
    document.querySelectorAll('[data-f]').forEach(function (el) {
      if (el !== document.activeElement) el.value = s[el.dataset.f] || '';
    });
    fillSource(s);
    count();
  }
  // Carte Veille d'origine : miniature, lien et vidéo de base découpée
  function fillSource(s) {
    var box = $('fSource');
    if (!box) return;
    var v = s.veille && maps.veille[s.veille];
    if (!v && s.source) Object.keys(maps.veille).some(function (id) { if (maps.veille[id].lien === s.source) { v = maps.veille[id]; return true; } return false; });
    var cle = v ? (s.veille || v.lien) + '|' + (v.decoupe || v.transcription || '').length : (s.source || '');
    if (box.dataset.cle === cle) return;
    box.dataset.cle = cle;
    box.textContent = '';
    if (!v && !s.source) { box.hidden = true; return; }
    box.hidden = false;
    var lien = (v && v.lien) || s.source;
    var a = document.createElement('a'); a.className = 'fs-thumb'; a.href = lien; a.target = '_blank'; a.rel = 'noopener';
    a.title = 'Ouvrir la vidéo de base';
    if (v && v.thumb) { var im = document.createElement('img'); im.src = v.thumb; im.alt = ''; a.append(im); }
    else a.textContent = '▶';
    var info = document.createElement('div'); info.className = 'fs-info';
    var k = document.createElement('span'); k.className = 'fs-kicker'; k.textContent = 'Vidéo de base';
    var t = document.createElement('strong'); t.textContent = v ? ((v.createur ? v.createur + ' · ' : '') + (v.titre || '')) : lien;
    var go2 = document.createElement('a'); go2.href = lien; go2.target = '_blank'; go2.rel = 'noopener'; go2.className = 'fs-link'; go2.textContent = 'Voir la vidéo ↗';
    info.append(k, t, go2);
    var texte = v && (v.decoupe || v.transcription);
    if (texte) {
      var d = document.createElement('details'); d.className = 'fs-tr';
      var sm = document.createElement('summary'); sm.textContent = 'Lire la vidéo de base découpée';
      var p = document.createElement('p'); p.textContent = texte;
      d.append(sm, p); info.append(d);
    }
    box.append(a, info);
  }
  function words(s) { return (s.notes || '').trim().split(/\s+/).filter(Boolean).length; }
  function count() {
    var s = maps.scripts[current];
    if (!s) return;
    var n = words(s);
    $('wcount').textContent = n + (n > 1 ? ' mots' : ' mot');
  }
  document.querySelectorAll('[data-f]').forEach(function (el) {
    var on = function () {
      var s = maps.scripts[current];
      if (!s) return;
      s[el.dataset.f] = el.value;
      s.updated = Date.now();
      persist('scripts', current, [el.dataset.f, 'updated']);
      count();
    };
    el.addEventListener('input', on);
    el.addEventListener('blur', flushAll);
  });
  $('backScripts').addEventListener('click', closeEditor);
  $('delScript').addEventListener('click', function () {
    var b = $('delScript');
    if (b.dataset.arm !== '1') { b.dataset.arm = '1'; b.textContent = 'Confirmer la suppression'; return; }
    var id = current; closeEditor(); remove('scripts', id); renderCal();
  });
  $('copyScript').addEventListener('click', function () {
    var s = maps.scripts[current]; if (!s) return;
    var txt = s.notes || '', b = $('copyScript');
    var done = function () { b.textContent = 'Copié'; setTimeout(function () { b.textContent = 'Copier'; }, 1500); };
    var fallback = function () {
      var ta = document.createElement('textarea'); ta.value = txt; document.body.append(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (err) {}
      ta.remove();
    };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, fallback); else fallback();
  });

  /* ---------- Idées ---------- */
  $('iForm').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var txt = $('iTxt').value.trim();
    if (!txt) { $('iTxt').focus(); return; }
    var id = newId('idees');
    maps.idees[id] = { project: project, txt: txt, created: Date.now() };
    persist('idees', id);
    flushAll();
    $('iTxt').value = '';
    renderIdees();
  });
  function renderIdees() {
    var ul = $('iList');
    ul.textContent = '';
    var list = Object.keys(maps.idees).map(function (id) { return Object.assign({ id: id }, maps.idees[id]); })
      .filter(function (x) { return x.project === project; })
      .sort(function (a, b) { return (b.created || 0) - (a.created || 0); });
    $('iEmpty').hidden = list.length > 0;
    list.forEach(function (x) {
      var li = document.createElement('li'); li.className = 'card idee';
      var t = document.createElement('p'); t.className = 'vhook'; t.textContent = x.txt;
      var del = document.createElement('button');
      del.type = 'button'; del.className = 'vdel'; del.textContent = '×';
      del.setAttribute('aria-label', 'Enlever cette idée');
      del.title = 'Enlever cette idée';
      del.addEventListener('click', function () { remove('idees', x.id); renderIdees(); });
      li.append(t, del);
      ul.append(li);
    });
  }

  /* ---------- Veille ---------- */
  var vFiltre = '';
  // Catégories toujours proposées, même sans vidéo dedans
  var CATS = ['Split screen'];
  document.addEventListener('click', function (e) {
    if (!e.target.closest || !e.target.closest('.vcat')) document.querySelectorAll('.vmenu').forEach(function (m) { m.hidden = true; });
  });
  // La Veille et l'onglet Validés partagent les mêmes cartes : un script validé passe dans Validés
  function renderVeille() { renderCartes(false); renderCartes(true); }
  function renderCartes(valides) {
    var ul = $(valides ? 'okList' : 'vList');
    if (!ul) return;
    var act = document.activeElement;
    if (act && act.tagName === 'TEXTAREA' && ul.contains(act)) return;
    ul.textContent = '';
    var list = Object.keys(maps.veille).map(function (id) { return Object.assign({ id: id }, maps.veille[id]); })
      .filter(function (v) { return v.project === project && !v.exemple && !!v.valide === valides; })
      .sort(function (a, b) { return (b.created || 0) - (a.created || 0); });
    $(valides ? 'okEmpty' : 'vEmpty').hidden = list.length > 0;
    var cats = CATS.slice();
    Object.keys(maps.veille).forEach(function (id) { (maps.veille[id].tags || []).forEach(function (t) { if (cats.indexOf(t) < 0) cats.push(t); }); });
    cats.sort(function (a, b) { return a.localeCompare(b, 'fr'); });
    var tous = [];
    list.forEach(function (v) { (v.tags || []).forEach(function (t) { if (tous.indexOf(t) < 0) tous.push(t); }); });
    if (!valides && tous.indexOf(vFiltre) < 0) vFiltre = '';
    var bar = valides ? document.createElement('div') : $('vTags');
    bar.textContent = '';
    bar.hidden = !tous.length;
    if (valides) { tous = []; }
    if (tous.length) ['Tout'].concat(tous).forEach(function (t) {
      var val = t === 'Tout' ? '' : t;
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'vtag'; b.textContent = t;
      b.setAttribute('aria-pressed', String(vFiltre === val));
      b.addEventListener('click', function () { vFiltre = val; renderVeille(); });
      bar.append(b);
    });
    list.filter(function (v) { return valides || !vFiltre || (v.tags || []).indexOf(vFiltre) >= 0; }).forEach(function (v) {
      var li = document.createElement('li'); li.className = 'card vitem';
      var isLink = /^https?:\/\//i.test(v.lien || '');
      if (/^data:image\/jpeg;base64,/.test(v.thumb || '')) {
        var img = document.createElement('img'); img.className = 'vthumb'; img.src = v.thumb; img.alt = 'Image de la vidéo de ' + (v.createur || 'ce créateur');
        if (isLink) {
          var ta = document.createElement('a'); ta.href = v.lien; ta.target = '_blank'; ta.rel = 'noopener'; ta.append(img);
          li.append(ta);
        } else li.append(img);
      }
      var body = document.createElement('div'); body.className = 'vbody';
      var top = document.createElement('div'); top.className = 'sitem-top';
      var c = document.createElement('span'); c.className = 'sitem-t'; c.textContent = v.createur || 'Créateur non renseigné';
      top.append(c);
      if (v.format) { var f = document.createElement('span'); f.className = 'status'; f.textContent = v.format; top.append(f); }
      body.append(top);
      if (v.titre || v.hook) { var h = document.createElement('p'); h.className = 'vhook'; h.textContent = v.titre || v.hook; body.append(h); }
      if (v.titre && v.hook && !v.transcription) { var hk = document.createElement('p'); hk.className = 'vwhy'; hk.textContent = 'Hook : ' + v.hook; body.append(hk); }
      if (v.pourquoi) { var w = document.createElement('p'); w.className = 'vwhy'; w.textContent = v.pourquoi; body.append(w); }
      if (true) {
        var tg = document.createElement('div'); tg.className = 'vtags';
        (v.tags || []).forEach(function (t) {
          var wrap = document.createElement('span'); wrap.className = 'vcat';
          var b = document.createElement('button');
          b.type = 'button'; b.className = 'vtag'; b.textContent = t + ' ▾';
          b.title = 'Changer de catégorie';
          var menu = document.createElement('div'); menu.className = 'vmenu'; menu.hidden = true;
          var pick = function (n) {
            var doc = maps.veille[v.id]; if (!doc) return;
            var tags = (doc.tags || []).slice();
            tags[tags.indexOf(t)] = n;
            doc.tags = tags.filter(function (x, i) { return tags.indexOf(x) === i; });
            persist('veille', v.id, ['tags']);
            renderVeille();
          };
          cats.forEach(function (c) {
            var o = document.createElement('button');
            o.type = 'button'; o.textContent = c;
            o.setAttribute('aria-pressed', String(c === t));
            o.addEventListener('click', function () { if (c !== t) pick(c); else menu.hidden = true; });
            menu.append(o);
          });
          var nv = document.createElement('button');
          nv.type = 'button'; nv.className = 'vnew'; nv.textContent = '+ Nouvelle catégorie';
          nv.addEventListener('click', function () {
            var n = (window.prompt('Nom de la catégorie') || '').trim();
            if (n) pick(n);
          });
          menu.append(nv);
          b.addEventListener('click', function (e) {
            e.stopPropagation();
            document.querySelectorAll('.vmenu').forEach(function (m) { if (m !== menu) m.hidden = true; });
            menu.hidden = !menu.hidden;
          });
          wrap.append(b, menu);
          tg.append(wrap);
        });
        if (v.adapte) {
          var mine = document.createElement('button');
          mine.type = 'button'; mine.className = 'vmine'; mine.textContent = 'Mon script';
          mine.setAttribute('aria-expanded', String(!!ouverts[v.id]));
          mine.addEventListener('click', function () {
            ouverts[v.id] = !ouverts[v.id];
            mine.setAttribute('aria-expanded', String(!!ouverts[v.id]));
            panel.hidden = !ouverts[v.id];
          });
          tg.append(mine);
          var ok = document.createElement('button');
          ok.type = 'button'; ok.className = 'vok';
          ok.setAttribute('aria-pressed', String(!!v.valide));
          ok.textContent = v.valide ? 'Validé ✓' : 'Valider';
          ok.title = v.valide ? 'Script validé (cliquer pour annuler)' : 'Marquer ce script comme validé';
          ok.addEventListener('click', function () {
            var doc = maps.veille[v.id]; if (!doc) return;
            doc.valide = !doc.valide;
            persist('veille', v.id, ['valide']);
            flushAll();
            renderVeille();
          });
          tg.append(ok);
          var pw = document.createElement('span'); pw.className = 'vcat';
          var prog = document.createElement('button');
          prog.type = 'button'; prog.className = 'vprog'; prog.textContent = 'Programmer';
          var pop = document.createElement('div'); pop.className = 'vmenu vpick'; pop.hidden = true;
          var pm = new Date(); pm.setDate(1);
          var drawPick = function () {
            pop.textContent = '';
            var head = document.createElement('div'); head.className = 'vp-head';
            var prev = document.createElement('button'); prev.type = 'button'; prev.textContent = '‹'; prev.setAttribute('aria-label', 'Mois précédent');
            var next = document.createElement('button'); next.type = 'button'; next.textContent = '›'; next.setAttribute('aria-label', 'Mois suivant');
            var tt = document.createElement('strong'); tt.textContent = MOIS[pm.getMonth()] + ' ' + pm.getFullYear();
            prev.addEventListener('click', function (e) { e.stopPropagation(); pm.setMonth(pm.getMonth() - 1); drawPick(); });
            next.addEventListener('click', function (e) { e.stopPropagation(); pm.setMonth(pm.getMonth() + 1); drawPick(); });
            head.append(prev, tt, next);
            var grid = document.createElement('div'); grid.className = 'vp-grid';
            ['L', 'M', 'M', 'J', 'V', 'S', 'D'].forEach(function (w) { var s = document.createElement('span'); s.className = 'vp-w'; s.textContent = w; grid.append(s); });
            var used = {};
            scriptsOf().forEach(function (s) { if (s.date) used[s.date] = (used[s.date] || 0) + 1; });
            var off = (pm.getDay() + 6) % 7, nb = new Date(pm.getFullYear(), pm.getMonth() + 1, 0).getDate(), today = ymd(new Date());
            for (var i = 0; i < off; i++) grid.append(document.createElement('span'));
            for (var dd = 1; dd <= nb; dd++) (function (day) {
              var key = ymd(new Date(pm.getFullYear(), pm.getMonth(), day));
              var c = document.createElement('button'); c.type = 'button'; c.className = 'vp-d' + (key === today ? ' now' : '') + (key < today ? ' past' : '');
              c.textContent = day;
              if (used[key]) { var dot = document.createElement('i'); dot.title = used[key] + ' script' + (used[key] > 1 ? 's' : ''); c.append(dot); }
              c.addEventListener('click', function (e) {
                e.stopPropagation();
                var doc = maps.veille[v.id] || v;
                createScript({ date: key, sujet: doc.titre || '', statut: 'Validé', notes: doc.adapte || '', source: doc.lien || '', veille: v.id });
                renderCal();
                pop.hidden = true;
                prog.textContent = 'Programmé le ' + parseDay(key).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' }) + ' ✓';
              });
              grid.append(c);
            })(dd);
            var hint = document.createElement('p'); hint.className = 'vp-hint'; hint.textContent = 'Le script part dans le calendrier ce jour-là. Un point = déjà un script prévu.';
            pop.append(head, grid, hint);
          };
          prog.addEventListener('click', function (e) {
            e.stopPropagation();
            document.querySelectorAll('.vmenu').forEach(function (m) { if (m !== pop) m.hidden = true; });
            if (pop.hidden) drawPick();
            pop.hidden = !pop.hidden;
          });
          pop.addEventListener('click', function (e) { e.stopPropagation(); });
          pw.append(prog, pop);
          tg.append(pw);
        }
        // Déplacer la vidéo vers un autre espace
        var mw = document.createElement('span'); mw.className = 'vcat';
        var mv = document.createElement('button');
        mv.type = 'button'; mv.className = 'vmove'; mv.textContent = 'Déplacer ▾';
        mv.title = 'Envoyer cette vidéo dans un autre espace';
        var mm = document.createElement('div'); mm.className = 'vmenu'; mm.hidden = true;
        Object.keys(PROJ).forEach(function (p) {
          if (p === project) return;
          var o = document.createElement('button');
          o.type = 'button'; o.textContent = 'Vers ' + PROJ[p].nom;
          o.addEventListener('click', function (e) {
            e.stopPropagation();
            var doc = maps.veille[v.id]; if (!doc) return;
            doc.project = p;
            persist('veille', v.id, ['project']);
            flushAll();
            renderVeille();
          });
          mm.append(o);
        });
        mv.addEventListener('click', function (e) {
          e.stopPropagation();
          document.querySelectorAll('.vmenu').forEach(function (m) { if (m !== mm) m.hidden = true; });
          mm.hidden = !mm.hidden;
        });
        mw.append(mv, mm);
        tg.append(mw);
        body.append(tg);
      }
      if (v.adapte) {
        var panel = document.createElement('div'); panel.className = 'vpanel'; panel.hidden = !ouverts[v.id];
        var cmp = document.createElement('div'); cmp.className = 'vcmp';
        var base = document.createElement('div');
        var hb = document.createElement('h4'); hb.textContent = v.traduit ? 'Vidéo de base (traduite de l\'anglais)' : 'Vidéo de base';
        var pb = document.createElement('p'); pb.textContent = v.decoupe || v.transcription || '';
        base.append(hb, pb);
        var mineBox = document.createElement('div');
        var hm = document.createElement('h4'); hm.textContent = 'Mon script';
        var ed = document.createElement('textarea'); ed.className = 'vedit'; ed.dataset.id = v.id; ed.value = v.adapte;
        ed.setAttribute('aria-label', 'Mon script, modifiable');
        var fit = function () { ed.style.height = 'auto'; ed.style.height = ed.scrollHeight + 'px'; };
        ed.addEventListener('input', function () {
          var doc = maps.veille[v.id]; if (!doc) return;
          doc.adapte = ed.value;
          persist('veille', v.id, ['adapte']);
          fit();
        });
        ed.addEventListener('blur', function () { flushAll(); });
        mineBox.append(hm, ed);
        cmp.append(base, mineBox);
        panel.append(cmp);
        body.append(panel);
        requestAnimationFrame(fit);
        mine.addEventListener('click', function () { requestAnimationFrame(fit); });
      } else if (v.transcription) {
        var d = document.createElement('details'); d.className = 'vtr';
        var sum = document.createElement('summary'); sum.textContent = v.traduit ? 'Transcription (traduite de l\'anglais)' : 'Transcription';
        var tx = document.createElement('p'); tx.textContent = v.transcription;
        d.append(sum, tx);
        body.append(d);
      }
      if (isLink) {
        var a = document.createElement('a'); a.className = 'vlink'; a.href = v.lien; a.target = '_blank'; a.rel = 'noopener'; a.textContent = 'Voir la vidéo';
        body.append(a);
      }
      var del = document.createElement('button');
      del.type = 'button'; del.className = 'vdel'; del.textContent = '×';
      del.setAttribute('aria-label', 'Enlever cette vidéo de la veille');
      del.title = 'Enlever de la veille';
      del.addEventListener('click', function () {
        // Premier clic : on demande confirmation, pour ne pas supprimer par erreur
        if (del.dataset.arm !== '1') {
          del.dataset.arm = '1'; del.textContent = 'Supprimer ?'; del.classList.add('arm');
          setTimeout(function () { if (del.isConnected) { del.dataset.arm = ''; del.textContent = '×'; del.classList.remove('arm'); } }, 4000);
          return;
        }
        remove('veille', v.id); renderVeille();
      });
      li.append(body, del);
      ul.append(li);
    });
  }

  /* ---------- Calendrier ---------- */
  var MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
  function pad(n) { return n < 10 ? '0' + n : String(n); }
  function ymd(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function parseDay(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  var today = new Date(), calY = today.getFullYear(), calM = today.getMonth();
  function renderCal() {
    $('calTitle').textContent = MOIS[calM] + ' ' + calY;
    var grid = $('calGrid');
    grid.textContent = '';
    var offset = (new Date(calY, calM, 1).getDay() + 6) % 7;
    var nbDays = new Date(calY, calM + 1, 0).getDate();
    var byDay = {};
    scriptsOf().forEach(function (s) { if (s.date) (byDay[s.date] = byDay[s.date] || []).push(s); });
    var now = ymd(new Date());
    for (var i = 1; i <= nbDays; i++) {
      (function (d) {
        var key = ymd(d);
        var cell = document.createElement('div');
        cell.className = 'cal-d' + (key === now ? ' now' : '');
        if (d.getDate() === 1) cell.style.gridColumnStart = offset + 1;
        var head = document.createElement('div'); head.className = 'cal-top';
        var w = document.createElement('span'); w.className = 'cal-w'; w.textContent = d.toLocaleDateString('fr-FR', { weekday: 'short' });
        var n = document.createElement('span'); n.className = 'cal-n'; n.textContent = d.getDate();
        var plus = document.createElement('button');
        plus.type = 'button'; plus.className = 'cal-add'; plus.textContent = '+';
        plus.setAttribute('aria-label', 'Nouveau script le ' + d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' }));
        plus.addEventListener('click', function () {
          openScript(createScript({ date: key }));
          $('fSujet').focus({ preventScroll: true });
        });
        head.append(w, n, plus);
        cell.append(head);
        var list = document.createElement('div'); list.className = 'cal-list';
        (byDay[key] || []).sort(function (a, b) { return (a.updated || 0) - (b.updated || 0); }).forEach(function (s) {
          var c = document.createElement('button');
          c.type = 'button';
          c.className = 'cal-p';
          c.dataset.st = STATUTS.indexOf(s.statut) < 0 ? 0 : STATUTS.indexOf(s.statut);
          c.textContent = s.sujet || 'Sans titre';
          c.title = (s.sujet || 'Sans titre') + ' · ' + (s.statut || STATUTS[0]);
          c.draggable = true;
          c.addEventListener('dragstart', function (ev) { ev.dataTransfer.setData('text/plain', s.id); });
          c.addEventListener('click', function () { openScript(s.id); });
          list.append(c);
        });
        cell.append(list);
        cell.addEventListener('dragover', function (ev) { ev.preventDefault(); cell.classList.add('over'); });
        cell.addEventListener('dragleave', function () { cell.classList.remove('over'); });
        cell.addEventListener('drop', function (ev) {
          ev.preventDefault();
          var sc = maps.scripts[ev.dataTransfer.getData('text/plain')];
          if (!sc) return;
          sc.date = key; sc.updated = Date.now();
          persist('scripts', ev.dataTransfer.getData('text/plain'), ['date', 'updated']);
          renderCal();
        });
        grid.append(cell);
      })(new Date(calY, calM, i));
    }
  }
  $('calPrev').addEventListener('click', function () { calM--; if (calM < 0) { calM = 11; calY--; } renderCal(); });
  $('calNext').addEventListener('click', function () { calM++; if (calM > 11) { calM = 0; calY++; } renderCal(); });
  $('calToday').addEventListener('click', function () {
    var d = new Date(); calY = d.getFullYear(); calM = d.getMonth();
    renderCal();
  });

  // Exemples : les vidéos de l'espace qui ont le mieux marché, pour copier sa façon d'écrire
  function renderExemples() {
    var ul = $('xList'); if (!ul) return;
    ul.textContent = '';
    var list = Object.keys(maps.veille).map(function (id) { return Object.assign({ id: id }, maps.veille[id]); })
      .filter(function (v) { return v.exemple && v.project === project; })
      .sort(function (a, b) { return (b.vues || 0) - (a.vues || 0); });
    $('xEmpty').hidden = list.length > 0;
    list.forEach(function (v) {
      var li = document.createElement('li'); li.className = 'card vitem';
      if (/^data:image\/jpeg;base64,/.test(v.thumb || '')) {
        var a0 = document.createElement('a'); a0.href = v.lien; a0.target = '_blank'; a0.rel = 'noopener';
        var img = document.createElement('img'); img.className = 'vthumb'; img.src = v.thumb; img.alt = 'Image de la vidéo';
        a0.append(img); li.append(a0);
      }
      var body = document.createElement('div'); body.className = 'vbody';
      var h = document.createElement('p'); h.className = 'vhook'; h.textContent = v.titre || ''; body.append(h);
      var w = document.createElement('p'); w.className = 'vwhy';
      w.textContent = (v.vues ? v.vues.toLocaleString('fr-FR') + ' vues. ' : '') + (v.pourquoi || ''); body.append(w);
      var txt = v.decoupe || v.transcription;
      if (txt) {
        var d = document.createElement('details'); d.className = 'vtr';
        var s = document.createElement('summary'); s.textContent = 'Script';
        var p = document.createElement('p'); p.textContent = txt;
        d.append(s, p); body.append(d);
      }
      var a = document.createElement('a'); a.className = 'vlink'; a.href = v.lien; a.target = '_blank'; a.rel = 'noopener'; a.textContent = 'Voir la vidéo';
      body.append(a);
      li.append(body); ul.append(li);
    });
  }
  function renderAll() {
    if (current) fillEditor();
    renderIdees();
    renderVeille();
    renderExemples();
    renderCal();
  }

  /* ---------- Démarrage ---------- */
  var hash = location.hash.slice(1);
  if (hash && (['plan', 'createurs'].indexOf(hash) >= 0 || $('d-' + hash))) project = 'rushly';
  applyProject();
  if (!hash) go(last[project] || DEFAUT[project]);
  renderAll();
  if (window.claude && window.claude.use) {
    window.claude.use('db').then(function (d) {
      if (!d) { fromLocal(); return; }
      db = d;
      ['scripts', 'veille', 'idees'].forEach(subscribe);
      importer();
    }).catch(fromLocal);
  } else fromLocal();
  // Cartes et scripts préparés par Claude : appliqués une seule fois chacun.
  function importer() {
    fetch('veille-import.json', { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (pack) {
      if (!pack) return;
      var metaRef = db.collection('meta').doc('imports');
      return metaRef.get().then(function (snap) {
        var faits = (snap.exists && snap.data().faits) || [];
        var nouveaux = [];
        var suite = Promise.resolve();
        Object.keys(pack.set || {}).forEach(function (id) {
          var k = 'set:' + id;
          if (faits.indexOf(k) >= 0) return;
          suite = suite.then(function () { return db.collection('veille').doc(id).set(pack.set[id]); }).then(function () { nouveaux.push(k); });
        });
        // Remise en place d'une carte supprimée par erreur (clé « restore:<id>@<n> », une seule fois)
        Object.keys(pack.restore || {}).forEach(function (rk) {
          var k = 'restore:' + rk;
          if (faits.indexOf(k) >= 0) return;
          var id = rk.split('@')[0];
          suite = suite.then(function () { return db.collection('veille').doc(id).set(pack.restore[rk]); }).then(function () { nouveaux.push(k); });
        });
        var manques = [];
        (pack.patch || []).forEach(function (p) {
          var k = 'patch:' + p.k;
          if (faits.indexOf(k) >= 0) return;
          var ref = db.collection('veille').doc(p.id);
          suite = suite.then(function () {
            if (!p.cuts) return ref.update(p.data);
            // Découpe la transcription aux phrases données, dans l'ordre
            return ref.get().then(function (s) {
              if (!s.exists) return;
              var t = s.data().transcription || '', parts = [], last = null, from = 0;
              p.cuts.forEach(function (c) {
                var i = t.indexOf(c[1], from);
                if (i < 0) { manques.push(p.id + ' : ' + c[1]); return; }
                if (last) parts.push([last[0], t.slice(last[1], i).trim()]);
                else if (i > 0) parts.push(['', t.slice(0, i).trim()]);
                last = [c[0], i]; from = i + 1;
              });
              if (last) parts.push([last[0], t.slice(last[1]).trim()]);
              var data = Object.assign({}, p.data);
              data.decoupe = parts.map(function (x) { return (x[0] ? x[0] + '\n' : '') + x[1]; }).join('\n\n');
              return ref.update(data);
            });
          }).then(function () { nouveaux.push(k); }, function () {});
        });
        return suite.then(function () {
          if (manques.length) db.collection('meta').doc('decoupe').set({ quand: Date.now(), manques: manques });
          if (nouveaux.length) return metaRef.set({ faits: faits.concat(nouveaux) });
        }).then(function () {
          // Export texte (sans miniatures) pour que Claude relise la Veille, sur demande
          if (!pack.exporter) return;
          return db.collection('veille').get().then(function (qs) {
            var out = {};
            if (pack.exporter === 'ids') {
              qs.docs.forEach(function (d) { var x = d.data(); out[d.id] = [x.project || '', x.createur || '', x.titre || '']; });
              return db.collection('meta').doc('export').set({ quand: Date.now(), ids: out });
            }
            qs.docs.forEach(function (d) {
              var x = d.data();
              if (pack.exporter !== true && x.project !== pack.exporter) return;
              out[d.id] = { project: x.project, createur: x.createur || '', titre: x.titre || '', tags: x.tags || [], pourquoi: x.pourquoi || '', transcription: x.transcription || '', traduit: !!x.traduit, adapte: x.adapte || '', decoupe: x.decoupe || '', lien: x.lien || '' };
            });
            return db.collection('meta').doc('export').set({ quand: Date.now(), docs: out });
          });
        });
      });
    }).catch(saveErr);
  }
  function fromLocal() {
    try {
      var m = JSON.parse(localStorage.getItem('rushly-studio') || 'null');
      if (m) { maps = { scripts: m.scripts || {}, veille: m.veille || {}, idees: m.idees || {} }; renderAll(); }
    } catch (err) {}
  }
})();
