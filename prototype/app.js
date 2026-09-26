/* ============================================================
   SIMULACRA — прототип механик
   Состояние, рендер, взаимодействия.
   ============================================================ */

const SAVE_KEY = 'simulacra_proto_v1';

const defaultState = () => ({
  sync: 0,
  pass: 1,
  found: ['f_11g', 'f_masha', 'f_lee'],
  links: [],          // id комбинаций
  achievements: [],
  canvasDone: false,
  seenFlashback: false,
});

let S = load();

function load() {
  try { return Object.assign(defaultState(), JSON.parse(localStorage.getItem(SAVE_KEY))); }
  catch (e) { return defaultState(); }
}
function save() { localStorage.setItem(SAVE_KEY, JSON.stringify(S)); }

const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));

/* ───────── уведомления ───────── */
function toast(text, kind) {
  const el = document.createElement('div');
  el.className = 'toast ' + (kind || '');
  el.innerHTML = text;
  $('#toasts').appendChild(el);
  setTimeout(() => el.classList.add('out'), 3200);
  setTimeout(() => el.remove(), 3800);
}
function unlock(id, text) {
  if (S.achievements.includes(id)) return;
  S.achievements.push(id); save();
  toast('🏆 ДОСТИЖЕНИЕ: ' + text, 'ach');
}
function addSync(n) {
  S.sync = Math.min(100, S.sync + n); save(); renderHUD();
}

/* ───────── HUD ───────── */
function renderHUD() {
  $('#hud-sync').textContent = S.sync + '%';
  $('#hud-frag').textContent = S.found.length;
  $('#hud-pass').textContent = S.pass;
}

/* ═════════════ 1. ФЛЕШБЕК ═════════════ */
const FB = { i: 0, timer: null, per: 260 };

function playFlashback() {
  const wrap = $('#flashback');
  wrap.classList.remove('hidden');
  FB.i = 0;
  const total = FRAMES.length;
  const step = () => {
    if (FB.i >= total) return endFlashback();
    const f = FRAMES[FB.i];
    const img = $('#fb-img');
    img.style.opacity = 0;
    setTimeout(() => {
      img.src = f.src;
      img.style.opacity = 1;
      // случайный сдвиг кадра — «дёрганая» нарезка
      img.style.transform = `scale(${(1 + Math.random() * 0.05).toFixed(3)}) translate(${(Math.random()*8-4).toFixed(1)}px, ${(Math.random()*4-2).toFixed(1)}px)`;
      img.style.filter = `saturate(${(0.25 + Math.random()*0.25).toFixed(2)}) contrast(${(1.1 + Math.random()*0.3).toFixed(2)}) sepia(${(0.2 + Math.random()*0.2).toFixed(2)})`;
    }, 40);
    $('#fb-cap').textContent = f.cap;
    if (Math.random() < 0.35) {  // пропуск кадра — эффект «выпадения»
      const fl = document.querySelector('.fb-flash');
      fl.style.opacity = 0.85;
      setTimeout(() => fl.style.opacity = 0, 60);
    }
    $('#fb-bar').style.width = Math.round(((FB.i + 1) / total) * 100) + '%';
    FB.i++;
    FB.timer = setTimeout(step, FB.per + Math.random() * 120);
  };
  step();
}
function endFlashback() {
  $('#fb-enter').classList.remove('hidden');
  $('#fb-cap').textContent = 'ДОМ ЖДЁТ';
}
function stopFlashback() {
  clearTimeout(FB.timer);
  $('#flashback').classList.add('hidden');
  $('#fb-enter').classList.add('hidden');
  S.seenFlashback = true; save();
}

/* ═════════════ 2. ФОКУС ВНИМАНИЯ ═════════════ */
function buildHotspots() {
  const wrap = $('#hotspots');
  wrap.innerHTML = '';
  HOTSPOTS.forEach(h => {
    const el = document.createElement('div');
    el.className = 'hs';
    el.dataset.id = h.id;
    el.style.cssText = `left:${h.x}%;top:${h.y}%;width:${h.w}%;height:${h.h}%`;
    el.innerHTML = `<span class="ring" style="--p:0"></span><span class="tag">${h.label}</span>`;
    el.addEventListener('mouseenter', () => holdStart(el, h));
    el.addEventListener('mouseleave', () => holdStop(el));
    wrap.appendChild(el);
  });
}

let holdRaf = null, holdStart_t = 0, holdHot = null;

function holdStart(el, h) {
  holdHot = h; holdStart_t = performance.now();
  cancelAnimationFrame(holdRaf);
  const tick = () => {
    const p = Math.min(1, (performance.now() - holdStart_t) / 1200);
    el.querySelector('.ring').style.setProperty('--p', p);
    if (p < 1) holdRaf = requestAnimationFrame(tick);
    else { holdStop(el); triggerFocus(h); }
  };
  holdRaf = requestAnimationFrame(tick);
}
function holdStop(el) {
  cancelAnimationFrame(holdRaf);
  holdHot = null;
  const r = el.querySelector('.ring');
  if (r) r.style.setProperty('--p', 0);
}
function triggerFocus(h) {
  const log = $('#focus-log');
  const line = document.createElement('div');
  line.className = 'log-line' + (h.trigger ? ' trig' : '');
  line.innerHTML = `<b>${h.label}</b> — ${h.note}`;
  log.prepend(line);

  if (h.trigger) {
    const stage = $('#stage');
    stage.classList.add('glitch');
    $('#focus-fx').innerHTML = '<span>МИКРО-ТРИГГЕР</span>';
    setTimeout(() => { stage.classList.remove('glitch'); $('#focus-fx').innerHTML = ''; }, 1000);
    if (h.frag && !S.found.includes(h.frag)) {
      S.found.push(h.frag); save(); renderHUD(); renderCards(); renderArchive();
      toast('📄 ФРАГМЕНТ ПОЛУЧЕН: ' + h.frag.toUpperCase(), 'ok');
      addSync(4);
      unlock('focus_first', 'первый микро-триггер');
    }
  } else {
    addSync(1);
  }
}

/* ═════════════ 3. ДОСТОВЕРНОСТЬ ═════════════ */
function renderCards() {
  const box = $('#frag-cards');
  box.innerHTML = '';
  FRAGMENTS.forEach(f => {
    const known = S.found.includes(f.id);
    const card = document.createElement('div');
    card.className = 'card' + (known ? '' : ' locked');
    if (known) {
      card.innerHTML = `
        <div class="card-h"><b>ВОСПОМИНАНИЕ ${f.num}</b> <span class="src ${f.src === '???' ? 'unk' : ''}">${f.src}</span></div>
        <div class="card-t">${f.title}</div>
        <div class="card-txt">${f.text}</div>
        <div class="meter"><label>Стабильность</label><span class="bar"><i style="width:${f.stab}%"></i></span><b>${f.stab}%</b></div>
        <div class="meter"><label>Совпадение</label><span class="bar"><i style="width:${f.match}%"></i></span><b>${f.match}%</b></div>
        <div class="card-src">Источник воспоминания: ${f.unknown ? 'неизвестен' : 'подтверждён'}</div>
        ${f.conflict ? '<div class="card-warn">⚠ Фрагмент содержит конфликтующие данные.</div>' : ''}
        ${f.stab < 45 ? '<div class="card-warn">⚠ Низкая стабильность: деталь может рассыпаться при следующем проходе.</div>' : ''}`;
    } else {
      card.innerHTML = `<div class="card-h"><b>ВОСПОМИНАНИЕ ${f.num}</b></div>
        <div class="card-t">███████████</div>
        <div class="card-txt">Фрагмент не найден. Найди его через «фокус внимания» или реконструкцию.</div>`;
    }
    box.appendChild(card);
  });
}

/* ═════════════ 4. ПОВТОРЕНИЕ С ИЗМЕНЕНИЯМИ ═════════════ */
function playScene() {
  const box = $('#scene-box');
  const pass = Math.min(S.pass, 3);
  const lines = SCENE[pass];
  const first = SCENE[1];
  box.innerHTML = `<div class="scene-pass">ПРОХОЖДЕНИЕ ${S.pass} — СЦЕНА: КАБИНЕТ</div>`;
  lines.forEach((l, i) => {
    const wasFirst = first[i];
    const changed = pass > 1 && (!wasFirst || wasFirst[1] !== l[1]);
    const d = document.createElement('div');
    d.className = 'dlg' + (changed ? ' changed' : '') + (l[0] === 'Уилл' ? ' will' : '');
    d.innerHTML = `<span class="who">${l[0]}</span><span class="txt">«${l[1]}»</span>${changed ? '<span class="chg">≠</span>' : ''}`;
    box.appendChild(d);
  });
  if (pass > 1) {
    const note = document.createElement('div');
    note.className = 'scene-note';
    note.textContent = 'Игра не объясняет изменение. Ты точно помнишь, что раньше было иначе.';
    box.appendChild(note);
    unlock('repeat_seen', 'заметить, что реальность поменялась');
  }
  S.pass = Math.min(3, S.pass + 1); save(); renderHUD();
}

/* ═════════════ 5. АРХИВ МАЙКА ═════════════ */
function renderArchive() {
  const chips = $('#arch-chips');
  chips.innerHTML = '';
  FRAGMENTS.filter(f => S.found.includes(f.id)).forEach(f => {
    const c = document.createElement('div');
    c.className = 'chip';
    c.draggable = true;
    c.dataset.id = f.id;
    c.textContent = f.title;
    c.title = f.num + ' · ' + f.src;
    c.addEventListener('dragstart', e => { e.dataTransfer.setData('text/plain', f.id); c.classList.add('drag'); });
    c.addEventListener('dragend', () => c.classList.remove('drag'));
    c.addEventListener('dragover', e => { e.preventDefault(); c.classList.add('over'); });
    c.addEventListener('dragleave', () => c.classList.remove('over'));
    c.addEventListener('drop', e => {
      e.preventDefault(); c.classList.remove('over');
      tryLink(e.dataTransfer.getData('text/plain'), f.id);
    });
    chips.appendChild(c);
  });

  const links = $('#arch-links');
  if (!S.links.length) { links.innerHTML = '<div class="empty">связей пока нет</div>'; return; }
  links.innerHTML = '';
  S.links.forEach(id => {
    const combo = COMBOS.find(c => c.id === id);
    if (!combo) return;
    const a = FRAGMENTS.find(f => f.id === combo.a).title;
    const b = FRAGMENTS.find(f => f.id === combo.b).title;
    const d = document.createElement('div');
    d.className = 'link';
    d.innerHTML = `<div class="link-pair">${a} <b>+</b> ${b} <b>↓</b></div>
                   <div class="link-out">СВЯЗЬ ОБНАРУЖЕНА: ${combo.out}</div>
                   <div class="link-sync">+${combo.sync}% СИНХРОНИЗАЦИИ</div>`;
    links.appendChild(d);
  });
}

function tryLink(a, b) {
  if (!a || !b || a === b) return;
  const combo = COMBOS.find(c => (c.a === a && c.b === b) || (c.a === b && c.b === a));
  if (!combo) {
    toast('Связь не подтверждена. Пока.', 'bad');
    addSync(1);
    return;
  }
  if (S.links.includes(combo.id)) { toast('Эта связь уже в архиве.', 'bad'); return; }
  S.links.push(combo.id); save();
  renderArchive();
  addSync(combo.sync);
  toast('🔗 СВЯЗЬ ОБНАРУЖЕНА', 'ok');
  unlock('first_link', 'первая связь в архиве');
  if (S.links.length >= 4) unlock('detective', 'собрать 4 связи');
}

/* ═════════════ 6. NEURAL CANVAS ═════════════ */
function buildCanvas() {
  const cv = $('#canvas');
  cv.innerHTML = '';
  for (let i = 1; i <= 9; i++) {
    const cell = document.createElement('div');
    cell.className = 'cell';
    cell.dataset.cell = 'c' + i;
    cell.innerHTML = `<span class="cell-id">${i}</span>`;
    cell.addEventListener('dragover', e => { e.preventDefault(); cell.classList.add('over'); });
    cell.addEventListener('dragleave', () => cell.classList.remove('over'));
    cell.addEventListener('drop', e => {
      e.preventDefault(); cell.classList.remove('over');
      const pid = e.dataTransfer.getData('text/plain');
      if (!pid.startsWith('p_')) return;
      if (cell.children.length > 1) return;
      const piece = document.querySelector(`.piece[data-id="${pid}"]`);
      if (piece) { cell.appendChild(piece); renderCanvasBar(); }
    });
    cv.appendChild(cell);
  }

  const tray = $('#tray');
  tray.innerHTML = '';
  CANVAS_PIECES.forEach(p => {
    const el = document.createElement('div');
    el.className = 'piece';
    el.draggable = true;
    el.dataset.id = p.id;
    el.innerHTML = `<i>${p.icon}</i><span>${p.label}</span>`;
    el.addEventListener('dragstart', e => e.dataTransfer.setData('text/plain', p.id));
    tray.appendChild(el);
  });

  tray.addEventListener('dragover', e => e.preventDefault());
  tray.addEventListener('drop', e => {
    e.preventDefault();
    const pid = e.dataTransfer.getData('text/plain');
    const piece = document.querySelector(`.piece[data-id="${pid}"]`);
    if (piece) { tray.appendChild(piece); renderCanvasBar(); }
  });
  renderCanvasBar();
}

function placed() {
  return CANVAS_PIECES.map(p => {
    const el = document.querySelector(`.piece[data-id="${p.id}"]`);
    const cell = el && el.parentElement && el.parentElement.dataset.cell;
    return { p, cell: cell || null };
  });
}
function renderCanvasBar() {
  const n = placed().filter(x => x.cell).length;
  $('#canvas-bar').querySelector('i').style.width = Math.round(n / (CANVAS_PIECES.length + 3) * 100) + '%';
}

function reconstruct() {
  const pl = placed();
  const onCanvas = pl.filter(x => x.cell);
  if (onCanvas.length < 4) { $('#verdict').className = 'verdict bad'; $('#verdict').textContent = 'Недостаточно фрагментов. Память не собирается.'; return; }

  let ok = 0, wrong = 0;
  pl.forEach(({ p, cell }) => {
    if (!cell) return;
    if (p.target && cell === p.target) { ok++; }
    else if (!p.target) { ok += 0.5; }   // неизвестный объект — куда угодно
    else wrong++;
  });

  const v = $('#verdict');
  v.innerHTML = '';
  const total = CANVAS_PIECES.filter(p => p.target).length;

  if (ok >= total) {
    v.className = 'verdict good';
    v.innerHTML = `<b>НАСТОЯЩЕЕ ВОСПОМИНАНИЕ</b><br>Реконструкция совпала с архивной схемой 11-G. Фрагмент зафиксирован.`;
    if (!S.found.includes('f_redlamp')) { S.found.push('f_redlamp'); save(); renderHUD(); renderCards(); renderArchive(); toast('📄 ФРАГМЕНТ ПОЛУЧЕН: КРАСНАЯ ЛАМПА', 'ok'); }
    addSync(10);
    unlock('true_memory', 'собрать истинное воспоминание');
    if (!S.canvasDone) { S.canvasDone = true; save(); }
  } else if (ok >= total * 0.6) {
    v.className = 'verdict partial';
    v.innerHTML = `<b>ЧАСТИЧНО ВЕРНО · ${Math.round(ok)}/${total}</b><br>Оба варианта оказались по-своему правы. Разница записана как вариант памяти.`;
    addSync(5);
    unlock('partial_memory', 'частично верная реконструкция');
  } else {
    v.className = 'verdict bad';
    v.innerHTML = `<b>ЛОЖНОЕ ВОСПОМИНАНИЕ</b><br>Ты собрал то, чего не было. Теперь оно в архиве — и ты будешь помнить именно так.`;
    addSync(-3);
    unlock('false_memory', 'собрать ложное воспоминание');
  }
  renderHUD();
}

/* ═════════════ 7. СИНХРОНИЗАЦИЯ ═════════════ */
function renderSync() {
  const val = S.sync;
  $('#sync-num').textContent = val + '%';
  $('#sync-range').value = val;

  const scale = $('#sync-scale');
  scale.innerHTML = '';
  SYNC_STAGES.forEach(s => {
    const d = document.createElement('div');
    d.className = 'stage-mark' + (val >= s.at ? ' on' : '');
    d.style.left = s.at + '%';
    d.innerHTML = `<i></i><span>${s.at}</span>`;
    scale.appendChild(d);
  });

  const cur = SYNC_STAGES.slice().reverse().find(s => val >= s.at);
  const box = $('#sync-dialogue');

  if (val >= 100) {
    box.className = 'dialogue merged';
    box.innerHTML = `<div class="dlg"><span class="who both">МАЙК+УИЛЛ</span><span class="txt">«Мы помним одно и то же. Значит, один из нас — лишний.»</span></div>`;
  } else if (val >= 90) {
    box.className = 'dialogue split';
    box.innerHTML = `<div class="dlg flick"><span class="who will">УИЛЛ</span><span class="txt">«Я вошёл первым. Или это ты?»</span></div>
                     <div class="dlg flick alt"><span class="who">МАЙК</span><span class="txt">«Я вошёл первым. Или это ты?»</span></div>`;
  } else if (val >= 70) {
    box.className = 'dialogue unison';
    box.innerHTML = `<div class="dlg"><span class="who">МАЙК</span><span class="txt">«Дверь была закрыта.»</span></div>
                     <div class="dlg"><span class="who will">УИЛЛ</span><span class="txt">«Дверь была закрыта.»</span></div>`;
  } else if (val >= 50) {
    box.className = 'dialogue';
    box.innerHTML = `<div class="dlg"><span class="who will">УИЛЛ</span><span class="txt">«Смотри. Вот моё воспоминание о твоём доме. Оно точнее твоего.»</span></div>`;
  } else if (val >= 30) {
    box.className = 'dialogue';
    box.innerHTML = `<div class="dlg"><span class="who will">УИЛЛ</span><span class="txt">«Не думай об этом вслух. Я слышу.»</span></div>
                     <div class="dlg"><span class="who">МАЙК</span><span class="txt">«Я ничего не говорил.»</span></div>`;
  } else {
    box.className = 'dialogue';
    box.innerHTML = `<div class="dlg"><span class="who">МАЙК</span><span class="txt">«Я один в своей голове. Пока.»</span></div>`;
  }

  const note = document.createElement('div');
  note.className = 'sync-note';
  note.textContent = cur.title + ' — ' + cur.text;
  box.appendChild(note);
}

/* ═════════════ 8. EXTRAS ═════════════ */
function renderExtras() {
  const box = $('#extras');
  box.innerHTML = '';
  EXTRAS.forEach(e => {
    const c = document.createElement('div');
    c.className = 'extra';
    let status = 'открыто';
    if (e.name === 'New Game+') status = S.pass > 1 ? 'доступно (прохождение ' + S.pass + ')' : 'нужен второй круг';
    if (e.name === 'Scene Replay') status = S.pass > 1 ? S.pass - 1 + ' сцен(ы) с изменениями' : 'нет данных';
    if (e.name === 'Achievement') status = S.achievements.length + ' / 6';
    if (e.name === 'Character Gallery') status = 'Майк, Уилл, Ким, Ли, ' + (S.found.includes('f_masha') ? 'Маша, ' : '') + '???';
    c.innerHTML = `<div class="ex-icon">${e.icon}</div><div class="ex-name">${e.name}</div>
                   <div class="ex-desc">${e.desc}</div><div class="ex-status">${status}</div>`;
    box.appendChild(c);
  });
}

/* ═════════════ ТАБЫ / INIT ═════════════ */
$$('.tab').forEach(t => t.addEventListener('click', () => {
  $$('.tab').forEach(x => x.classList.remove('active'));
  $$('.tabpage').forEach(x => x.classList.remove('active'));
  t.classList.add('active');
  $('#tab-' + t.dataset.tab).classList.add('active');
  if (t.dataset.tab === 'reliability') renderCards();
  if (t.dataset.tab === 'archive') renderArchive();
  if (t.dataset.tab === 'sync') renderSync();
  if (t.dataset.tab === 'extras') renderExtras();
}));

$('#btn-fb').addEventListener('click', playFlashback);
$('#fb-skip').addEventListener('click', stopFlashback);
$('#fb-enter').addEventListener('click', () => { stopFlashback(); toast('Майк заходит в дом.', 'ok'); });
$('#btn-scene').addEventListener('click', playScene);
$('#btn-newpass').addEventListener('click', () => { S.pass = 1; save(); renderHUD(); $('#scene-box').innerHTML = ''; toast('Круг начат заново. Воспоминания остались.', 'ok'); });
$('#btn-reconstruct').addEventListener('click', reconstruct);
$('#btn-clear').addEventListener('click', () => { buildCanvas(); $('#verdict').textContent = ''; $('#verdict').className = 'verdict'; });
$('#sync-range').addEventListener('input', e => { S.sync = +e.target.value; save(); renderHUD(); renderSync(); if (S.sync >= 100) unlock('sync100', '100% синхронизации'); });
$('#btn-reset').addEventListener('click', () => { S = defaultState(); save(); location.reload(); });

buildHotspots();
renderCards();
renderArchive();
buildCanvas();
renderSync();
renderExtras();
renderHUD();

if (!S.seenFlashback) setTimeout(playFlashback, 600);
