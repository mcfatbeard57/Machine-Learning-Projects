(() => {
"use strict";

const MAX_HEARTS = 5;
const HEART_REFILL_MS = 20 * 60 * 1000;
const LESSON_SIZE = 5;
const STORE_KEY = "kili-ml-v1";

// ---------- helpers ----------
const $app = document.getElementById("app");
const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const shuffle = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const pick = (a, n) => shuffle(a).slice(0, n);
const today = () => { const d = new Date(); return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate(); };
const yesterday = () => { const d = new Date(); d.setDate(d.getDate() - 1); return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate(); };

const CONTRACTIONS = { "i'm": "i am", "you're": "you are", "he's": "he is", "she's": "she is", "it's": "it is", "we're": "we are", "they're": "they are", "what's": "what is", "where's": "where is", "who's": "who is", "that's": "that is", "i'll": "i will", "don't": "do not", "didn't": "did not", "isn't": "is not", "name's": "name is" };
function norm(s) {
  s = String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  s = s.replace(/[’‘`]/g, "'").replace(/\([^)]*\)/g, " ");
  s = s.split(/\s+/).map(w => CONTRACTIONS[w.replace(/[^a-z']/g, "")] || w).join(" ");
  return s.replace(/[^a-z0-9ഀ-ൿ ]/g, " ").replace(/\s+/g, " ").trim();
}
function accepted(item) { return [item.en, ...(item.alt || [])].map(norm); }

// ---------- course index ----------
const COURSE = window.COURSE;
const ALL_ITEMS = [];
COURSE.forEach((u, ui) => {
  u.items.forEach(it => { it.unit = u.id; it.script = !!u.script; it.noType = !!u.noType; it.key = u.id + ":" + it.ml; ALL_ITEMS.push(it); });
  (u.sentences || []).forEach(s => { s.unit = u.id; s.key = u.id + ":s:" + s.ml.join(" "); });
  // build lessons: chunks of words, then a sentence lesson
  const chunks = [];
  for (let i = 0; i < u.items.length; i += LESSON_SIZE) chunks.push(u.items.slice(i, i + LESSON_SIZE));
  if (chunks.length > 1 && chunks[chunks.length - 1].length < 3) chunks[chunks.length - 2].push(...chunks.pop());
  u.lessons = chunks.map((items, i) => ({ id: u.id + "-" + i, unit: u, kind: "words", items, label: "Lesson " + (i + 1) }));
  if (u.sentences && u.sentences.length) u.lessons.push({ id: u.id + "-s", unit: u, kind: "sentences", items: u.items, sentences: u.sentences, label: "Sentences" });
  u.index = ui;
});
const ALL_LESSONS = COURSE.flatMap(u => u.lessons);
const ITEM_BY_KEY = Object.fromEntries(ALL_ITEMS.map(i => [i.key, i]));
const SENT_BY_KEY = Object.fromEntries(COURSE.flatMap(u => u.sentences || []).map(s => [s.key, s]));

// ---------- state ----------
const DEFAULT = { xp: 0, hearts: MAX_HEARTS, heartTs: Date.now(), streak: 0, lastDay: null, done: {}, mistakes: {}, seen: {}, showTr: true, goal: 30, dayXp: 0, day: today(), sound: true };
let S = load();
function load() {
  try { const raw = localStorage.getItem(STORE_KEY); if (raw) return Object.assign({}, DEFAULT, JSON.parse(raw)); } catch (e) {}
  return Object.assign({}, DEFAULT);
}
function save() { try { localStorage.setItem(STORE_KEY, JSON.stringify(S)); } catch (e) {} }
function tick() {
  if (S.day !== today()) { S.day = today(); S.dayXp = 0; }
  if (S.lastDay && S.lastDay !== today() && S.lastDay !== yesterday()) S.streak = 0;
  if (S.hearts >= MAX_HEARTS) { S.heartTs = Date.now(); return; }
  const gained = Math.floor((Date.now() - S.heartTs) / HEART_REFILL_MS);
  if (gained > 0) { S.hearts = Math.min(MAX_HEARTS, S.hearts + gained); S.heartTs += gained * HEART_REFILL_MS; }
}
function isUnlocked(lesson) {
  const i = ALL_LESSONS.indexOf(lesson);
  return i === 0 || !!S.done[ALL_LESSONS[i - 1].id] || !!S.done[lesson.id] || (lesson.unit.open && lesson.unit.lessons[0] === lesson);
}

// ---------- speech ----------
let voices = [];
function loadVoices() { try { voices = speechSynthesis.getVoices(); } catch (e) { voices = []; } }
if ("speechSynthesis" in window) { loadVoices(); speechSynthesis.onvoiceschanged = loadVoices; }
const mlVoice = () => voices.find(v => /^ml/i.test(v.lang));
const canSpeakML = () => !!mlVoice();
function speak(text, lang) {
  if (!S.sound || !("speechSynthesis" in window)) return;
  try {
    const u = new SpeechSynthesisUtterance(text.replace(/[?,]/g, " "));
    u.lang = lang === "ml" ? "ml-IN" : "en-US";
    const v = lang === "ml" ? mlVoice() : voices.find(v => /^en/i.test(v.lang));
    if (lang === "ml" && !v) return;
    if (v) u.voice = v;
    u.rate = 0.85;
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  } catch (e) {}
}
let audioCtx;
function beep(ok) {
  if (!S.sound) return;
  try {
    audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    const notes = ok ? [660, 880] : [220, 180];
    notes.forEach((f, i) => {
      const o = audioCtx.createOscillator(), g = audioCtx.createGain();
      o.frequency.value = f; o.type = ok ? "sine" : "square";
      g.gain.setValueAtTime(0.0001, audioCtx.currentTime + i * 0.1);
      g.gain.exponentialRampToValueAtTime(0.08, audioCtx.currentTime + i * 0.1 + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + i * 0.1 + 0.15);
      o.connect(g).connect(audioCtx.destination); o.start(audioCtx.currentTime + i * 0.1); o.stop(audioCtx.currentTime + i * 0.1 + 0.16);
    });
  } catch (e) {}
}

// ---------- rendering helpers ----------
function mlHTML(ml, tr, cls = "") {
  return `<span class="ml ${cls}">${esc(ml)}</span>${S.showTr && tr ? `<span class="tr">${esc(tr)}</span>` : ""}`;
}
function topBar() {
  return `<div class="top">
    <div class="logo">🦜 Kili</div>
    <div class="stats">
      <span class="stat streak" title="Day streak">🔥 ${S.streak}</span>
      <span class="stat heart" title="Hearts">❤️ ${S.hearts}</span>
      <span class="stat xp" title="Total XP">⚡ ${S.xp}</span>
    </div></div>`;
}

// ---------- HOME ----------
function renderHome() {
  tick(); save();
  let html = topBar();
  const pct = Math.min(100, Math.round(S.dayXp / S.goal * 100));
  html += `<div class="goal"><div class="row"><span>Daily goal</span><span>${S.dayXp} / ${S.goal} XP</span></div><div class="bar"><i style="width:${pct}%"></i></div></div>`;
  const mistakeCount = Object.keys(S.mistakes).length;
  html += `<div class="actions">
    <button class="small-btn" data-act="practice">🏋️ Practice${mistakeCount ? ` (${mistakeCount} mistakes)` : ""}</button>
    <button class="small-btn" data-act="words">📖 Words</button>
    <button class="small-btn" data-act="sing">🎤 Sing-along</button>
    <button class="small-btn" data-act="settings">⚙️ Settings</button>
  </div>`;
  if (S.hearts === 0) {
    const mins = Math.ceil((HEART_REFILL_MS - (Date.now() - S.heartTs)) / 60000);
    html += `<p class="muted" style="text-align:center;font-weight:700">Out of hearts. Next heart in ${mins} min — or do Practice to earn one.</p>`;
  }
  COURSE.forEach(u => {
    const doneN = u.lessons.filter(l => S.done[l.id]).length;
    html += `<section class="unit"><div class="unit-head"><div><h2>Unit ${u.index + 1}: ${esc(u.title)}</h2><div class="ml">${esc(u.mlTitle)}</div></div><span class="pct">${doneN}/${u.lessons.length}</span></div><div class="path">`;
    u.lessons.forEach((l, i) => {
      const done = !!S.done[l.id], open = isUnlocked(l);
      const offset = Math.round(Math.sin(i * 1.3) * 70);
      const icon = done ? "★" : !open ? "🔒" : l.kind === "sentences" ? "💬" : "▶";
      html += `<div class="node-wrap" style="transform:translateX(${offset}px)"><button class="node ${done ? "done" : ""} ${open ? "" : "locked"}" data-lesson="${l.id}" ${open ? "" : "disabled"} aria-label="${esc(l.label)}">${icon}</button><div class="node-label">${esc(l.label)}${done && S.done[l.id] > 1 ? ` ×${S.done[l.id]}` : ""}</div></div>`;
    });
    html += `</div></section>`;
  });
  $app.innerHTML = html;
  $app.querySelectorAll("[data-lesson]").forEach(b => b.onclick = () => {
    const l = ALL_LESSONS.find(x => x.id === b.dataset.lesson);
    tick();
    if (S.hearts <= 0) { alert("No hearts left. Do a Practice session to earn one, or wait for a refill."); return; }
    startSession(buildLesson(l), { lesson: l, hearts: true });
  });
  $app.querySelector("[data-act=practice]").onclick = () => {
    const ex = buildPractice();
    if (!ex) { alert("Finish your first lesson to unlock practice."); return; }
    startSession(ex, { practice: true, hearts: false });
  };
  $app.querySelector("[data-act=words]").onclick = renderWords;
  $app.querySelector("[data-act=settings]").onclick = renderSettings;
  $app.querySelector("[data-act=sing]").onclick = renderSongs;
  window.scrollTo(0, 0);
}

// ---------- WORDS ----------
function renderWords() {
  let html = topBar() + `<button class="small-btn" id="back">← Back</button><h2>Words you've seen</h2>`;
  const seen = ALL_ITEMS.filter(i => S.seen[i.key]);
  if (!seen.length) html += `<p class="muted">Nothing yet — start Unit 1.</p>`;
  COURSE.forEach(u => {
    const list = u.items.filter(i => S.seen[i.key]);
    if (!list.length) return;
    html += `<div class="panel"><h3>${esc(u.title)}</h3><div class="word-list">` + list.map(i =>
      `<div class="word-row"><span><span class="ml" style="font-size:20px">${esc(i.ml)}</span> <span class="muted">${esc(i.tr)}</span></span><span style="font-weight:700;text-align:right">${esc(i.en)}${S.mistakes[i.key] ? " ⚠️" : ""}${i.note ? `<div class="muted" style="font-size:13px;font-weight:400">${esc(i.note)}</div>` : ""}</span></div>`).join("") + `</div></div>`;
  });
  $app.innerHTML = html;
  document.getElementById("back").onclick = renderHome;
}

// ---------- SETTINGS ----------
function renderSettings() {
  const ml = canSpeakML();
  $app.innerHTML = topBar() + `<button class="small-btn" id="back">← Back</button><h2>Settings</h2>
  <div class="panel">
    <div class="setting"><span>Show transliteration (Manglish)</span><button class="toggle ${S.showTr ? "on" : ""}" id="tTr" aria-label="Transliteration"></button></div>
    <div class="setting"><span>Sound &amp; speech</span><button class="toggle ${S.sound ? "on" : ""}" id="tSound" aria-label="Sound"></button></div>
    <div class="setting"><span>Daily goal</span><select id="goal">${[10, 20, 30, 50, 100].map(g => `<option value="${g}" ${g === S.goal ? "selected" : ""}>${g} XP</option>`).join("")}</select></div>
  </div>
  <p class="muted">Malayalam voice: ${ml ? "available ✅ (listening exercises on)" : "not found on this device — listening exercises are skipped. Install a Malayalam text‑to‑speech voice (Android: Google TTS → Malayalam) to enable them."}</p>
  <div class="panel"><div class="setting"><span>Reset all progress</span><button class="small-btn" id="reset" style="color:var(--bad)">Reset</button></div></div>`;
  document.getElementById("back").onclick = renderHome;
  document.getElementById("tTr").onclick = () => { S.showTr = !S.showTr; save(); renderSettings(); };
  document.getElementById("tSound").onclick = () => { S.sound = !S.sound; save(); renderSettings(); };
  document.getElementById("goal").onchange = e => { S.goal = +e.target.value; save(); };
  document.getElementById("reset").onclick = () => { if (confirm("Erase all progress?")) { S = Object.assign({}, DEFAULT, { day: today(), heartTs: Date.now(), done: {}, mistakes: {}, seen: {} }); save(); renderHome(); } };
}

// ---------- EXERCISE BUILDERS ----------
function distractors(item, n) {
  const sameUnit = ALL_ITEMS.filter(i => i.unit === item.unit && i !== item && norm(i.en) !== norm(item.en));
  const pool = sameUnit.length >= n ? sameUnit : sameUnit.concat(ALL_ITEMS.filter(i => i.unit !== item.unit && i.script === item.script && norm(i.en) !== norm(item.en)));
  const out = [], seenEn = new Set([norm(item.en)]);
  for (const c of shuffle(pool)) { if (!seenEn.has(norm(c.en))) { seenEn.add(norm(c.en)); out.push(c); } if (out.length === n) break; }
  return out;
}
const mc = (item, dir, isNew) => ({ type: "mc", dir, item, isNew, options: shuffle([item, ...distractors(item, 3)]) });
const listen = item => ({ type: "listen", item, options: shuffle([item, ...distractors(item, 3)]) });
const typeEx = item => ({ type: "type", item });
const matchEx = items => ({ type: "match", items: pick(items, Math.min(5, items.length)) });
function buildEx(sent, dir) {
  const allSents = COURSE.flatMap(u => u.sentences || []).filter(s => s !== sent);
  let tokens, extra;
  if (dir === "ml2en") {
    tokens = sent.en.replace(/[.?!,]/g, "").split(/\s+/);
    const pool = [...new Set(allSents.flatMap(s => s.en.replace(/[.?!,]/g, "").split(/\s+/)))].filter(w => !tokens.map(t => t.toLowerCase()).includes(w.toLowerCase()));
    extra = pick(pool, 3);
  } else {
    tokens = sent.ml.slice();
    const pool = [...new Set(allSents.flatMap(s => s.ml))].filter(w => !tokens.includes(w));
    extra = pick(pool, 3);
  }
  return { type: "build", dir, sent, bank: shuffle([...tokens, ...extra]) };
}

function buildLesson(l) {
  const ex = [];
  if (l.kind === "words") {
    const isFirstTime = !S.done[l.id];
    l.items.forEach(it => ex.push(mc(it, "ml2en", isFirstTime && !S.seen[it.key])));
    const mix = [];
    l.items.forEach(it => {
      mix.push(mc(it, "en2ml"));
      if (canSpeakML()) mix.push(listen(it));
      else if (!it.noType && Math.random() < 0.5) mix.push(typeEx(it));
    });
    ex.push(...shuffle(mix).slice(0, 7));
    ex.splice(Math.min(ex.length, l.items.length + 2), 0, matchEx(l.items));
  } else {
    l.sentences.forEach((s, i) => ex.push(buildEx(s, i % 2 ? "en2ml" : "ml2en")));
    ex.push(matchEx(l.items));
    pick(l.items.filter(it => !it.noType), 3).forEach(it => ex.push(typeEx(it)));
    return shuffle(ex);
  }
  return ex;
}

function buildPractice() {
  const doneUnits = new Set(ALL_LESSONS.filter(l => S.done[l.id]).map(l => l.unit.id));
  const learned = ALL_ITEMS.filter(i => S.seen[i.key]);
  if (!learned.length) return null;
  const mistakes = Object.keys(S.mistakes).map(k => ITEM_BY_KEY[k]).filter(Boolean);
  const mistakeSents = Object.keys(S.mistakes).map(k => SENT_BY_KEY[k]).filter(Boolean);
  const focus = [...pick(mistakes, 6), ...pick(learned.filter(i => !S.mistakes[i.key]), 6)].slice(0, 8);
  const ex = [];
  focus.forEach((it, i) => {
    const r = i % 3;
    ex.push(r === 0 ? mc(it, "en2ml") : r === 1 ? (canSpeakML() ? listen(it) : mc(it, "ml2en")) : it.noType ? mc(it, "ml2en") : typeEx(it));
  });
  const sents = [...mistakeSents, ...pick(COURSE.filter(u => doneUnits.has(u.id)).flatMap(u => u.sentences || []), 2)];
  [...new Set(sents)].slice(0, 3).forEach((s, i) => ex.push(buildEx(s, i % 2 ? "en2ml" : "ml2en")));
  ex.push(matchEx(learned));
  return shuffle(ex);
}

// ---------- SESSION ----------
let sess = null;
function startSession(queue, opts) {
  sess = Object.assign({ queue, i: 0, total: queue.length, correct: 0, answered: 0, wrongOnce: new Set(), answer: null, checked: false, xp: 0, start: Date.now() }, opts);
  renderEx();
}
function quitSession() {
  if (confirm("Quit this lesson? Progress in this lesson will be lost.")) { sess = null; renderHome(); }
}

function renderEx() {
  const ex = sess.queue[sess.i];
  sess.answer = null; sess.checked = false;
  const progress = Math.round(sess.i / sess.queue.length * 100);
  let body = "";
  if (ex.type === "mc") body = renderMC(ex);
  else if (ex.type === "listen") body = renderListen(ex);
  else if (ex.type === "type") body = renderType(ex);
  else if (ex.type === "match") body = renderMatch(ex);
  else if (ex.type === "build") body = renderBuild(ex);
  else if (ex.type === "blank") body = renderBlank(ex);
  $app.innerHTML = `<div class="lesson-top"><button class="x" id="quit" aria-label="Quit">✕</button><div class="bar"><i style="width:${progress}%"></i></div>${sess.hearts ? `<span class="stat heart" style="font-weight:800">❤️ ${S.hearts}</span>` : `<span class="muted" style="font-weight:800">Practice</span>`}</div>
  <div id="ex">${body}</div>
  <div class="foot" id="foot"><div class="foot-in" id="footIn">${ex.type === "match" ? `<button class="cta ghost" id="skip">Can't do this now</button>` : `<button class="cta" id="check" disabled>Check</button>`}</div></div>`;
  document.getElementById("quit").onclick = quitSession;
  const check = document.getElementById("check");
  if (check) check.onclick = doCheck;
  const skip = document.getElementById("skip");
  if (skip) skip.onclick = () => nextEx();
  bindEx(ex);
  window.scrollTo(0, 0);
}
function setAnswer(a) {
  sess.answer = a;
  const c = document.getElementById("check");
  if (c) c.disabled = a == null || (Array.isArray(a) ? a.length === 0 : String(a).trim() === "");
}

// --- multiple choice ---
function renderMC(ex) {
  const it = ex.item;
  const head = ex.isNew ? `<div class="badge">NEW WORD</div>` : "";
  if (ex.dir === "ml2en") {
    const title = it.script ? "What sound does this letter make?" : "What does this mean?";
    return `${head}<div class="prompt-type">${title}</div>
      <div class="q">${canSpeakML() ? `<button class="spk" data-say="${esc(it.ml)}" aria-label="Play">🔊</button>` : ""}<div class="text">${mlHTML(it.ml, it.script ? null : it.tr, it.script ? "big" : "")}</div></div>
      <div class="opts">${ex.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="k">${i + 1}</span><span>${esc(o.en)}</span></button>`).join("")}</div>`;
  }
  const title = it.script ? `Which letter makes the sound “${esc(it.en)}”?` : `Which one is “${esc(it.en)}”?`;
  return `<div class="prompt-type">${title}</div>
    <div class="opts">${ex.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="k">${i + 1}</span><span class="text">${mlHTML(o.ml, it.script ? null : o.tr, it.script ? "big" : "")}</span></button>`).join("")}</div>`;
}
function renderListen(ex) {
  return `<div class="prompt-type">What do you hear?</div>
    <div class="q" style="justify-content:center"><button class="spk big" data-say="${esc(ex.item.ml)}" aria-label="Play">🔊</button></div>
    <div class="opts">${ex.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="k">${i + 1}</span><span>${esc(o.en)}</span></button>`).join("")}</div>`;
}
function renderType(ex) {
  const it = ex.item;
  return `<div class="prompt-type">${it.script ? "Type the sound of this letter" : "Write this in English"}</div>
    <div class="q">${canSpeakML() ? `<button class="spk" data-say="${esc(it.ml)}" aria-label="Play">🔊</button>` : ""}<div class="text">${mlHTML(it.ml, it.script ? null : it.tr, it.script ? "big" : "")}</div></div>
    <textarea class="type-in" id="typeIn" placeholder="Type in English" autocomplete="off" autocapitalize="off" spellcheck="false"></textarea>`;
}
function renderMatch(ex) {
  ex.left = shuffle(ex.items); ex.right = shuffle(ex.items); ex.matched = new Set(); ex.sel = null;
  return `<div class="prompt-type">Tap the matching pairs</div>
    <div class="match">${ex.left.map((it, i) => `<button class="opt" data-side="L" data-i="${i}"><span class="ml" style="font-size:22px">${esc(it.ml)}</span></button><button class="opt" data-side="R" data-i="${i}">${esc(ex.right[i].en)}</button>`).join("")}</div>`;
}
function renderBuild(ex) {
  const s = ex.sent;
  const prompt = ex.dir === "ml2en"
    ? `<div class="q">${canSpeakML() ? `<button class="spk" data-say="${esc(s.ml.join(" "))}" aria-label="Play">🔊</button>` : ""}<div class="text">${mlHTML(s.ml.join(" "), s.tr)}</div></div>`
    : `<div class="q"><div class="text">${esc(s.en)}</div></div>`;
  return `<div class="prompt-type">${ex.dir === "ml2en" ? "Translate this sentence" : "Translate into Malayalam"}</div>${prompt}
    <div class="answer-line" id="ansLine"></div>
    <div class="bank" id="bank">${ex.bank.map((w, i) => `<button class="chip ${ex.dir === "en2ml" ? "ml" : ""}" data-b="${i}">${esc(w)}</button>`).join("")}</div>`;
}

function bindEx(ex) {
  $app.querySelectorAll("[data-say]").forEach(b => b.onclick = () => speak(b.dataset.say, "ml"));
  if (ex.type === "blank") {
    $app.querySelectorAll(".opt").forEach(b => b.onclick = () => {
      if (sess.checked) return;
      $app.querySelectorAll(".opt").forEach(x => x.classList.remove("sel"));
      b.classList.add("sel"); setAnswer(+b.dataset.i);
    });
  } else if (ex.type === "mc" || ex.type === "listen") {
    if (ex.type === "listen" || (ex.dir === "ml2en" && canSpeakML())) setTimeout(() => speak(ex.item.ml, "ml"), 250);
    $app.querySelectorAll(".opt").forEach(b => b.onclick = () => {
      if (sess.checked) return;
      $app.querySelectorAll(".opt").forEach(x => x.classList.remove("sel"));
      b.classList.add("sel"); setAnswer(+b.dataset.i);
      if (ex.dir === "en2ml") speak(ex.options[+b.dataset.i].ml, "ml");
    });
  } else if (ex.type === "type") {
    const t = document.getElementById("typeIn");
    t.oninput = () => setAnswer(t.value);
    t.onkeydown = e => { if (e.key === "Enter") { e.preventDefault(); if (!sess.checked && sess.answer && sess.answer.trim()) doCheck(); else if (sess.checked) nextEx(); } };
    setTimeout(() => t.focus(), 50);
  } else if (ex.type === "build") {
    const line = document.getElementById("ansLine"), bank = document.getElementById("bank");
    const chosen = [];
    const draw = () => {
      line.innerHTML = chosen.map((bi, pos) => `<button class="chip ${ex.dir === "en2ml" ? "ml" : ""}" data-pos="${pos}">${esc(ex.bank[bi])}</button>`).join("");
      bank.querySelectorAll("[data-b]").forEach(b => b.classList.toggle("used", chosen.includes(+b.dataset.b)));
      line.querySelectorAll("[data-pos]").forEach(b => b.onclick = () => { if (sess.checked) return; chosen.splice(+b.dataset.pos, 1); draw(); });
      setAnswer(chosen.map(bi => ex.bank[bi]));
    };
    bank.querySelectorAll("[data-b]").forEach(b => b.onclick = () => {
      if (sess.checked) return;
      const bi = +b.dataset.b; if (chosen.includes(bi)) return;
      chosen.push(bi); if (ex.dir === "en2ml") speak(ex.bank[bi], "ml"); draw();
    });
  } else if (ex.type === "match") {
    $app.querySelectorAll(".match .opt").forEach(b => b.onclick = () => {
      const side = b.dataset.side, i = +b.dataset.i;
      const it = side === "L" ? ex.left[i] : ex.right[i];
      if (ex.matched.has(it.key)) return;
      if (side === "L") speak(it.ml, "ml");
      if (!ex.sel || ex.sel.side === side) {
        $app.querySelectorAll(`.match .opt[data-side="${side}"]`).forEach(x => x.classList.remove("sel"));
        ex.sel = { side, i, it, el: b }; b.classList.add("sel"); return;
      }
      const a = ex.sel; ex.sel = null; a.el.classList.remove("sel");
      if (a.it.key === it.key) {
        ex.matched.add(it.key); beep(true);
        [a.el, b].forEach(x => { x.classList.add("right"); setTimeout(() => { x.classList.remove("right"); x.classList.add("gone"); }, 300); });
        if (ex.matched.size === ex.items.length) setTimeout(() => { sess.correct++; sess.answered++; ex.items.forEach(markSeen); nextEx(); }, 500);
      } else {
        beep(false);
        [a.el, b].forEach(x => { x.classList.add("wrong", "shake"); setTimeout(() => x.classList.remove("wrong", "shake"), 450); });
      }
    });
  }
}

function markSeen(it) { if (it && it.key) S.seen[it.key] = 1; }

// --- checking ---
function evaluate(ex) {
  if (ex.type === "mc" || ex.type === "listen") {
    const ok = ex.options[sess.answer] === ex.item;
    const solution = ex.dir === "en2ml" ? { ml: ex.item.ml, tr: ex.item.tr, en: ex.item.en } : { ml: ex.item.ml, tr: ex.item.tr, en: ex.item.en };
    return { ok, solution, key: ex.item.key };
  }
  if (ex.type === "blank") {
    return { ok: ex.options[sess.answer] === ex.word, solution: { ml: ex.line.ml, tr: ex.line.tr, en: ex.line.en }, key: "song:" + ex.line.ml };
  }
  if (ex.type === "type") {
    const ok = accepted(ex.item).includes(norm(sess.answer));
    return { ok, solution: { ml: ex.item.ml, tr: ex.item.tr, en: ex.item.en }, key: ex.item.key };
  }
  if (ex.type === "build") {
    const s = ex.sent; let ok;
    if (ex.dir === "ml2en") ok = [s.en, ...(s.alt || [])].map(norm).includes(norm(sess.answer.join(" ")));
    else ok = norm(sess.answer.join(" ")) === norm(s.ml.join(" "));
    return { ok, solution: { ml: s.ml.join(" "), tr: s.tr, en: s.en }, key: s.key };
  }
}

function doCheck() {
  if (sess.checked || sess.answer == null) return;
  const ex = sess.queue[sess.i];
  const r = evaluate(ex);
  sess.checked = true; sess.answered++;
  if (ex.item) markSeen(ex.item);
  // highlight options
  if (ex.type === "mc" || ex.type === "listen" || ex.type === "blank") {
    $app.querySelectorAll(".opt").forEach(b => {
      b.disabled = true;
      const o = ex.options[+b.dataset.i];
      if (o === (ex.type === "blank" ? ex.word : ex.item)) b.classList.add("right"); else if (+b.dataset.i === sess.answer) b.classList.add("wrong");
    });
  }
  if (r.ok) {
    sess.correct++; beep(true);
    if (S.mistakes[r.key] && sess.practice) delete S.mistakes[r.key];
  } else {
    beep(false);
    if (ex.type !== "blank") S.mistakes[r.key] = (S.mistakes[r.key] || 0) + 1;
    if (sess.hearts) S.hearts = Math.max(0, S.hearts - 1), S.heartTs = S.hearts === MAX_HEARTS - 1 ? Date.now() : S.heartTs;
    if (!sess.wrongOnce.has(sess.i)) { sess.wrongOnce.add(sess.i); sess.queue.push(Object.assign({}, ex, { retry: true })); }
  }
  save();
  const foot = document.getElementById("foot"), fin = document.getElementById("footIn");
  foot.className = "foot " + (r.ok ? "ok" : "bad");
  const sol = r.solution;
  const solHTML = ex.type === "blank" || ex.type === "build" && ex.dir === "en2ml" || ex.type === "mc" && ex.dir === "en2ml"
    ? `<span class="ml">${esc(sol.ml)}</span>${S.showTr ? ` <span class="tr">(${esc(sol.tr)})</span>` : ""}`
    : esc(sol.en);
  const praise = ["Nice!", "Great!", "Correct!", "കൊള്ളാം! (Nice!)", "Excellent!", "അടിപൊളി! (Awesome!)"];
  fin.innerHTML = `<div class="fb-title">${r.ok ? praise[Math.floor(Math.random() * praise.length)] : "Correct answer:"}</div>
    ${r.ok ? `<div class="fb-ans"><span class="ml">${esc(sol.ml)}</span> = ${esc(sol.en)}</div>` : `<div class="fb-ans">${solHTML}</div><div class="fb-ans muted"><span class="ml">${esc(sol.ml)}</span> = ${esc(sol.en)}</div>`}
    ${ex.item && ex.item.note ? `<div class="fb-ans muted" style="font-size:14px">🎬 ${esc(ex.item.note)}</div>` : ""}
    <button class="cta" id="next">Continue</button>`;
  document.getElementById("next").onclick = nextEx;
  document.getElementById("next").focus();
  if (sess.hearts && S.hearts === 0) {
    document.getElementById("next").onclick = () => outOfHearts();
  }
}

function nextEx() {
  sess.i++;
  if (sess.i >= sess.queue.length) return finish();
  renderEx();
}

function outOfHearts() {
  sess = null;
  $app.innerHTML = `<div class="center"><div class="emoji">💔</div><h1>Out of hearts</h1><p class="muted">Hearts refill one every 20 minutes. Practice earns one back.</p>
  <div class="foot"><div class="foot-in"><button class="cta" id="prac">Practice to earn a heart</button><button class="cta ghost" id="home">Back home</button></div></div></div>`;
  document.getElementById("home").onclick = renderHome;
  document.getElementById("prac").onclick = () => { const ex = buildPractice(); if (ex) startSession(ex, { practice: true, hearts: false }); else renderHome(); };
}

function finish() {
  const s = sess; sess = null;
  const acc = Math.round(s.correct / Math.max(1, s.answered) * 100);
  let xp = s.practice ? 10 : 15;
  if (s.wrongOnce.size === 0) xp += 5;
  S.xp += xp; tick(); S.dayXp += xp;
  if (S.lastDay !== today()) { S.streak = S.lastDay === yesterday() ? S.streak + 1 : 1; S.lastDay = today(); }
  if (s.lesson) S.done[s.lesson.id] = (S.done[s.lesson.id] || 0) + 1;
  let heartMsg = "";
  if (s.practice && S.hearts < MAX_HEARTS) { S.hearts++; heartMsg = "+1 ❤️ earned"; }
  save();
  const mins = Math.max(1, Math.round((Date.now() - s.start) / 60000));
  $app.innerHTML = `<div class="center"><div class="emoji">${s.wrongOnce.size === 0 ? "🏆" : "🎉"}</div><h1>${s.practice ? "Practice complete!" : "Lesson complete!"}</h1>
  <p class="muted" style="font-weight:700">${s.wrongOnce.size === 0 ? "Flawless — no mistakes!" : "Mistakes get extra practice later."} ${heartMsg}</p>
  <div class="tiles"><div class="tile"><b>Total XP</b><span>⚡ ${xp}</span></div><div class="tile g"><b>Accuracy</b><span>🎯 ${acc}%</span></div><div class="tile"><b>Streak</b><span>🔥 ${S.streak}</span></div><div class="tile g"><b>Time</b><span>⏱ ${mins}m</span></div></div>
  <div class="foot"><div class="foot-in"><button class="cta" id="cont">Continue</button></div></div></div>`;
  document.getElementById("cont").onclick = s.song ? renderSongs : renderHome;
  document.getElementById("cont").focus();
}

// ---------- SING-ALONG ----------
const SONGS = window.SONGS || [];
function renderSongs() {
  let html = topBar() + `<button class="small-btn" id="back">← Back</button><h2>🎤 Sing-along</h2>
  <p class="muted">Read along line by line, say each line out loud, then play fill-in-the-blank to lock it in.</p>`;
  SONGS.forEach(sg => {
    html += `<div class="panel" style="padding:14px 16px"><h3 style="margin:4px 0">${esc(sg.title)}</h3><div class="ml" style="font-size:18px">${esc(sg.mlTitle)}</div>
      <p class="muted" style="font-size:14px">${esc(sg.credit)}</p>
      <div class="actions" style="margin-top:0"><button class="small-btn" data-open="${sg.id}">📜 Lyrics</button><button class="small-btn" data-quiz="${sg.id}">🧩 Fill the blank</button></div></div>`;
  });
  $app.innerHTML = html;
  document.getElementById("back").onclick = renderHome;
  $app.querySelectorAll("[data-open]").forEach(b => b.onclick = () => renderSong(SONGS.find(x => x.id === b.dataset.open), 0));
  $app.querySelectorAll("[data-quiz]").forEach(b => b.onclick = () => startSession(buildSongQuiz(SONGS.find(x => x.id === b.dataset.quiz)), { practice: true, hearts: false, song: true }));
  window.scrollTo(0, 0);
}
let karaokeTimer = null;
function renderSong(sg, cur, playing) {
  clearTimeout(karaokeTimer);
  const showEn = S.songEn !== false;
  let html = `<div class="lesson-top"><button class="x" id="back" aria-label="Back">✕</button><div class="bar"><i style="width:${Math.round((cur + 1) / sg.lines.length * 100)}%"></i></div></div>
  <h2 style="margin:0">${esc(sg.title)}</h2><div class="ml muted" style="margin-bottom:12px">${esc(sg.mlTitle)}</div>
  <div class="setting" style="border:none;padding:0 0 10px"><span class="muted">Show English meaning</span><button class="toggle ${showEn ? "on" : ""}" id="tEn" aria-label="English"></button></div>`;
  html += sg.lines.map((ln, i) => `<div class="lyric ${i === cur ? "cur" : ""}" data-line="${i}">
      <div class="ml" style="font-size:${i === cur ? 24 : 19}px;font-weight:700">${esc(ln.ml)}</div>
      ${S.showTr ? `<div class="tr">${esc(ln.tr)}</div>` : ""}
      ${showEn ? `<div class="muted" style="font-size:14px">${esc(ln.en)}</div>` : ""}</div>`).join("");
  html += `<div class="foot"><div class="foot-in" style="flex-direction:row">
    <button class="cta ghost" id="prev" ${cur === 0 ? "disabled" : ""}>◀</button>
    <button class="cta" id="play">${playing ? "⏸ Pause" : "▶ Sing along"}</button>
    <button class="cta ghost" id="nextL" ${cur === sg.lines.length - 1 ? "disabled" : ""}>▶</button></div></div>`;
  $app.innerHTML = html;
  const cel = $app.querySelector(".lyric.cur"); if (cel) cel.scrollIntoView({ block: "center", behavior: "smooth" });
  document.getElementById("back").onclick = () => { clearTimeout(karaokeTimer); renderSongs(); };
  document.getElementById("tEn").onclick = () => { S.songEn = !showEn; save(); renderSong(sg, cur, playing); };
  document.getElementById("prev").onclick = () => renderSong(sg, Math.max(0, cur - 1));
  document.getElementById("nextL").onclick = () => renderSong(sg, Math.min(sg.lines.length - 1, cur + 1));
  $app.querySelectorAll("[data-line]").forEach(el => el.onclick = () => { speak(sg.lines[+el.dataset.line].ml, "ml"); renderSong(sg, +el.dataset.line); });
  document.getElementById("play").onclick = () => playing ? renderSong(sg, cur, false) : renderSong(sg, cur, true);
  if (playing) {
    speak(sg.lines[cur].ml, "ml");
    // time per line scales with length so you can read and repeat it aloud
    const ms = Math.max(3500, sg.lines[cur].tr.length * 180);
    karaokeTimer = setTimeout(() => {
      if (!document.getElementById("play")) return;
      if (cur < sg.lines.length - 1) renderSong(sg, cur + 1, true); else renderSong(sg, cur, false);
    }, ms);
  }
}
function buildSongQuiz(sg) {
  const words = [...new Set(sg.lines.flatMap(l => l.ml.split(/\s+/)).filter(w => !w.endsWith("-")))];
  return shuffle(sg.lines).map(line => {
    const toks = line.ml.split(/\s+/);
    const candidates = toks.map((w, i) => i).filter(i => !toks[i].endsWith("-"));
    const bi = candidates[Math.floor(Math.random() * candidates.length)];
    const word = toks[bi];
    const others = pick(words.filter(w => w !== word), 3);
    return { type: "blank", song: sg, line, toks, bi, word, options: shuffle([word, ...others]) };
  });
}
function renderBlank(ex) {
  const shown = ex.toks.map((w, i) => i === ex.bi ? `<span class="blank">____</span>` : esc(w)).join(" ");
  return `<div class="prompt-type">Fill in the missing word</div>
    <div class="muted" style="font-weight:700;margin-bottom:6px">🎵 ${esc(ex.song.title)}</div>
    <div class="q"><div class="text"><span class="ml">${shown}</span>${S.showTr ? `<span class="tr">${esc(ex.line.tr.split(/\s+/).map((w, i) => i === ex.bi ? "____" : w).join(" "))}</span>` : ""}<span class="tr">${esc(ex.line.en)}</span></div></div>
    <div class="opts">${ex.options.map((o, i) => `<button class="opt" data-i="${i}"><span class="k">${i + 1}</span><span class="ml">${esc(o)}</span></button>`).join("")}</div>`;
}

// ---------- keyboard ----------
document.addEventListener("keydown", e => {
  if (!sess) return;
  if (e.target && e.target.id === "typeIn") return;
  const ex = sess.queue[sess.i];
  if (/^[1-9]$/.test(e.key)) {
    if (ex && (ex.type === "mc" || ex.type === "listen" || ex.type === "blank") && !sess.checked) {
      const b = $app.querySelector(`.opt[data-i="${+e.key - 1}"]`); if (b) b.click();
    }
  } else if (e.key === "Enter") {
    e.preventDefault();
    const next = document.getElementById("next");
    if (next) next.click(); else if (!sess.checked) doCheck();
  } else if (e.key === "Backspace" && ex && ex.type === "build" && !sess.checked) {
    const chips = $app.querySelectorAll("#ansLine [data-pos]"); if (chips.length) chips[chips.length - 1].click();
  }
});

window.__kili = { get sess() { return sess; }, get state() { return S; } };
renderHome();
})();
