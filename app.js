'use strict';
/* Ôn trắc nghiệm — app tĩnh, đọc dữ liệu từ data/catalog.json và data/lessons/<id>.json.
   Không cần build. Toàn bộ trộn câu, trộn đáp án, chấm điểm diễn ra trên máy người dùng. */

const app = document.getElementById('app');
const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

/* ---------- Lưu trữ trên máy (điểm, câu sai) ---------- */
const store = {
  key: (id) => 'mcq:v1:' + id,
  get(id) {
    try { return JSON.parse(localStorage.getItem(this.key(id))) || {}; } catch (e) { return {}; }
  },
  set(id, v) {
    try { localStorage.setItem(this.key(id), JSON.stringify(v)); } catch (e) { /* bỏ qua */ }
  }
};

/* ---------- Tải dữ liệu ---------- */
const lessonCache = {};
async function getJSON(url) {
  const r = await fetch(url, { cache: 'no-cache' });
  if (!r.ok) throw new Error('Không tải được ' + url + ' (' + r.status + ')');
  return r.json();
}
const loadCatalog = () => getJSON('data/catalog.json');
async function loadLesson(id) {
  if (!lessonCache[id]) lessonCache[id] = await getJSON('data/lessons/' + encodeURIComponent(id) + '.json');
  return lessonCache[id];
}

/* ---------- Tiện ích ---------- */
function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function inline(s) {
  return esc(s)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
}
/* Markdown tối giản: **đậm**, *nghiêng*, dòng "- " thành gạch đầu dòng, xuống dòng giữ nguyên. */
function md(text) {
  if (!text) return '';
  const lines = String(text).replace(/<\/?br\s*\/?>/gi, '\n').split('\n');
  let html = '', inList = false;
  for (const raw of lines) {
    const line = raw.trimEnd();
    const m = line.match(/^\s*[-•]\s+(.*)$/);
    if (m) {
      if (!inList) { html += '<ul>'; inList = true; }
      html += '<li>' + inline(m[1]) + '</li>';
      continue;
    }
    if (inList) { html += '</ul>'; inList = false; }
    if (line.trim() === '') continue;
    html += '<p>' + inline(line) + '</p>';
  }
  if (inList) html += '</ul>';
  return html;
}
/* Gắn nhãn "Câu x." vào đầu đoạn đầu tiên của câu hỏi. */
function withNumber(html, n) {
  const label = '<strong class="qnum">Câu ' + n + '.</strong> ';
  return html.startsWith('<p>') ? html.replace('<p>', '<p>' + label) : '<p>' + label + '</p>' + html;
}
function questionHtml(q, n) {
  const stem = md(q.stem);
  const lead = md(q.lead);
  if (stem) return '<div class="stem">' + withNumber(stem, n) + '</div><div class="lead">' + lead + '</div>';
  return '<div class="lead lead-only">' + withNumber(lead, n) + '</div>';
}
function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function pct(a, b) { return b ? Math.round((a / b) * 100) : 0; }
function fmtDate(iso) {
  try { return new Date(iso).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }); } catch (e) { return ''; }
}
function setTitle(t) { document.title = t ? t + ' · Ôn trắc nghiệm' : 'Ôn trắc nghiệm'; }
function wrongIdsFor(lesson) {
  const st = store.get(lesson.id);
  const valid = new Set(lesson.questions.map((q) => q.id));
  return (st.wrong || []).filter((id) => valid.has(id));
}
function errorView(msg, back) {
  app.innerHTML = topbar({ title: 'Có lỗi', back }) +
    '<main class="page"><div class="empty"><p>' + esc(msg) + '</p><p class="muted">Kiểm tra kết nối mạng hoặc tên file dữ liệu.</p></div></main>';
}
function topbar({ title, sub, back }) {
  return '<header class="topbar">' +
    (back ? '<button class="icon-btn" data-act="back" aria-label="Quay lại">' + ICON.back + '</button>' : '<span class="topbar-logo">' + ICON.logo + '</span>') +
    '<div class="topbar-title"><span>' + esc(title) + '</span>' + (sub ? '<small>' + esc(sub) + '</small>' : '') + '</div>' +
    '</header>';
}
const ICON = {
  back: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  logo: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="4" fill="currentColor" opacity=".15"/><circle cx="8" cy="9" r="1.6" fill="currentColor"/><path d="M11 9h6M11 15h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M6.6 15l1 1 2-2.2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  grid: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
  check: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  cross: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>'
};

/* ---------- Điều hướng (hash) ---------- */
let leaveGuard = null;   // hàm trả về true nếu được phép rời trang hiện tại
let lastHash = location.hash;
let skipNext = false;

function go(hash) {
  if (location.hash === hash || (hash === '#/' && location.hash === '')) {
    if (leaveGuard && !leaveGuard()) return;
    leaveGuard = null;
    route();
  } else {
    location.hash = hash;
  }
}
window.addEventListener('hashchange', () => {
  if (skipNext) { skipNext = false; return; }
  if (leaveGuard && !leaveGuard()) { skipNext = true; location.hash = lastHash; return; }
  leaveGuard = null;
  lastHash = location.hash;
  route();
});
window.addEventListener('beforeunload', (e) => {
  if (quiz && !quiz.submitted && quiz.items.some((i) => i.choice !== null)) { e.preventDefault(); e.returnValue = ''; }
});

function route() {
  const h = location.hash.slice(1) || '/';
  const [path, qs] = h.split('?');
  const parts = path.split('/').filter(Boolean).map(decodeURIComponent);
  window.scrollTo(0, 0);
  if (parts[0] === 'lesson' && parts[1]) return viewLesson(parts[1]);
  if (parts[0] === 'quiz' && parts[1]) return viewQuiz(parts[1], new URLSearchParams(qs).get('mode') || 'all');
  if (parts[0] === 'review' && parts[1]) return viewReview(parts[1]);
  return viewHome();
}

/* ---------- Trang 1: Danh mục bài học ---------- */
async function viewHome() {
  quiz = null;
  app.innerHTML = topbar({ title: 'Ôn trắc nghiệm' }) + '<main class="page"><div class="loading">Đang tải…</div></main>';
  let cat;
  try { cat = await loadCatalog(); } catch (e) { return errorView(e.message); }
  const title = cat.title || 'Ôn trắc nghiệm';
  setTitle('');
  const lessons = cat.lessons || [];
  const groups = [];
  const byTopic = {};
  for (const l of lessons) {
    const t = l.topic || 'Khác';
    if (!byTopic[t]) { byTopic[t] = []; groups.push(t); }
    byTopic[t].push(l);
  }
  const card = (l) => {
    const st = store.get(l.id);
    const wrong = (st.wrong || []).length;
    const last = st.last ? pct(st.last.score, st.last.total) + '%' : null;
    return '<a class="lesson-card" href="#/lesson/' + encodeURIComponent(l.id) + '" data-search="' + esc((l.title + ' ' + (l.topic || '')).toLowerCase()) + '">' +
      '<div class="lesson-main"><div class="lesson-title">' + esc(l.title) + '</div>' +
      '<div class="lesson-meta">' + (l.count || '?') + ' câu' + (last ? ' · Lần gần nhất <b>' + last + '</b>' : ' · Chưa làm') + '</div></div>' +
      (wrong ? '<span class="pill pill-bad">' + wrong + ' câu sai</span>' : (last ? '<span class="pill pill-ok">' + ICON.check + '</span>' : '')) +
      '</a>';
  };
  const body = lessons.length
    ? (lessons.length > 6 ? '<input class="search" type="search" placeholder="Tìm bài học…" aria-label="Tìm bài học">' : '') +
      groups.map((g) => '<section class="group" data-group><h2>' + esc(g) + '</h2>' + byTopic[g].map(card).join('') + '</section>').join('')
    : '<div class="empty"><p>Chưa có bài học nào.</p><p class="muted">Thêm file vào <code>data/lessons/</code> và cập nhật <code>data/catalog.json</code>.</p></div>';
  app.innerHTML = topbar({ title }) + '<main class="page">' + body + '</main>';
  const search = app.querySelector('.search');
  if (search) {
    search.addEventListener('input', () => {
      const q = search.value.trim().toLowerCase();
      app.querySelectorAll('.lesson-card').forEach((el) => { el.hidden = q && !el.dataset.search.includes(q); });
      app.querySelectorAll('[data-group]').forEach((g) => { g.hidden = !g.querySelector('.lesson-card:not([hidden])'); });
    });
  }
}

/* ---------- Trang 2: Giới thiệu bài học ---------- */
async function viewLesson(id) {
  quiz = null;
  app.innerHTML = topbar({ title: 'Bài học', back: true }) + '<main class="page"><div class="loading">Đang tải…</div></main>';
  bindBack('#/');
  let L;
  try { L = await loadLesson(id); } catch (e) { return errorView(e.message, true), bindBack('#/'); }
  setTitle(L.title);
  const st = store.get(id);
  const wrong = wrongIdsFor(L).length;
  const n = L.questions.length;
  const stats = st.attempts
    ? '<div class="stats">' +
        '<div><b>' + st.attempts + '</b><span>lần làm</span></div>' +
        '<div><b>' + pct(st.last.score, st.last.total) + '%</b><span>gần nhất</span></div>' +
        '<div><b>' + (st.best ?? 0) + '%</b><span>cao nhất</span></div>' +
      '</div>'
    : '';
  app.innerHTML = topbar({ title: L.title, sub: L.topic, back: true }) +
    '<main class="page">' +
      '<div class="intro">' +
        '<h1>' + esc(L.title) + '</h1>' +
        '<p class="muted">' + n + ' câu hỏi' + (L.updated ? ' · cập nhật ' + fmtDate(L.updated) : '') + '</p>' +
        stats +
        (L.sections && L.sections.length ? '<details class="sections"><summary>Nội dung bao phủ (' + L.sections.length + ' phần)</summary><ol>' + L.sections.map((s) => '<li>' + esc(s) + '</li>').join('') + '</ol></details>' : '') +
      '</div>' +
      '<div class="actions">' +
        '<a class="btn btn-primary" href="#/quiz/' + encodeURIComponent(id) + '">Làm toàn bộ (' + n + ' câu)</a>' +
        (wrong
          ? '<a class="btn btn-bad" href="#/quiz/' + encodeURIComponent(id) + '?mode=wrong">Làm lại câu sai (' + wrong + ')</a>'
          : '<button class="btn" disabled>Chưa có câu sai để làm lại</button>') +
        '<a class="btn btn-ghost" href="#/review/' + encodeURIComponent(id) + '">Xem toàn bộ đề và đáp án</a>' +
      '</div>' +
    '</main>';
  bindBack('#/');
}

function bindBack(target) {
  const b = app.querySelector('[data-act="back"]');
  if (b) b.onclick = () => go(target);
}

/* ---------- Trang 3: Làm bài ---------- */
let quiz = null;

async function viewQuiz(id, mode) {
  app.innerHTML = topbar({ title: 'Đang chuẩn bị…', back: true }) + '<main class="page"><div class="loading">Đang tải…</div></main>';
  bindBack('#/lesson/' + encodeURIComponent(id));
  let L;
  try { L = await loadLesson(id); } catch (e) { return errorView(e.message, true), bindBack('#/'); }
  setTitle(L.title);
  let pool = L.questions;
  if (mode === 'wrong') {
    const w = new Set(wrongIdsFor(L));
    pool = pool.filter((q) => w.has(q.id));
    if (!pool.length) return go('#/lesson/' + encodeURIComponent(id));
  }
  quiz = {
    id, L, mode, submitted: false,
    items: shuffle(pool).map((q) => ({ q, order: shuffle(q.options.map((_, i) => i)), choice: null }))
  };
  leaveGuard = () => !quiz || quiz.submitted || quiz.items.every((i) => i.choice === null) ||
    confirm('Thoát khỏi bài đang làm? Kết quả lần này sẽ không được lưu.');
  renderQuiz();
}

function renderQuiz() {
  const { L, items, mode } = quiz;
  const total = items.length;
  app.innerHTML =
    topbar({ title: L.title, sub: mode === 'wrong' ? 'Làm lại câu sai' : 'Làm toàn bộ', back: true }) +
    '<div class="progress" role="progressbar" aria-valuemin="0" aria-valuemax="' + total + '" aria-valuenow="0"><div style="width:0%"></div></div>' +
    '<main class="page quiz">' +
      items.map((it, i) =>
        '<section class="qblock" id="q-' + i + '">' +
          '<article class="qcard">' + questionHtml(it.q, i + 1) + '</article>' +
          '<div class="options" role="radiogroup">' +
            it.order.map((orig, k) =>
              '<button class="opt" role="radio" aria-checked="false" data-i="' + i + '" data-orig="' + orig + '">' +
                '<span class="opt-letter">' + LETTERS[k] + '</span><span class="opt-text">' + inline(it.q.options[orig]) + '</span>' +
              '</button>'
            ).join('') +
          '</div>' +
        '</section>'
      ).join('') +
      '<div class="quiz-end"><button class="btn btn-primary btn-block" data-act="submit">Nộp bài</button></div>' +
    '</main>' +
    '<footer class="qnav">' +
      '<button class="btn btn-ghost grid-btn" data-act="grid" aria-label="Danh sách câu">' + ICON.grid + '<span>0/' + total + ' đã trả lời</span></button>' +
      '<button class="btn btn-primary" data-act="submit">Nộp bài</button>' +
    '</footer>';

  bindBack('#/lesson/' + encodeURIComponent(quiz.id));
  app.querySelectorAll('.opt').forEach((b) => {
    b.onclick = () => choose(Number(b.dataset.i), Number(b.dataset.orig));
  });
  app.querySelectorAll('[data-act="submit"]').forEach((b) => { b.onclick = submit; });
  app.querySelector('[data-act="grid"]').onclick = openGrid;
}

function choose(i, orig) {
  const it = quiz.items[i];
  it.choice = orig;
  const block = document.getElementById('q-' + i);
  block.classList.add('answered');
  block.querySelectorAll('.opt').forEach((b) => {
    const on = Number(b.dataset.orig) === orig;
    b.classList.toggle('selected', on);
    b.setAttribute('aria-checked', on);
  });
  const answered = quiz.items.filter((x) => x.choice !== null).length;
  const total = quiz.items.length;
  const bar = app.querySelector('.progress');
  bar.firstChild.style.width = pct(answered, total) + '%';
  bar.setAttribute('aria-valuenow', answered);
  app.querySelector('.grid-btn span').textContent = answered + '/' + total + ' đã trả lời';
}

function scrollToQuestion(i) {
  const el = document.getElementById('q-' + i);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function openGrid() {
  const sheet = document.createElement('div');
  sheet.className = 'sheet-wrap';
  sheet.innerHTML =
    '<div class="sheet" role="dialog" aria-label="Danh sách câu hỏi">' +
      '<div class="sheet-head"><b>Danh sách câu</b><button class="icon-btn" data-act="close" aria-label="Đóng">' + ICON.cross + '</button></div>' +
      '<div class="grid">' +
        quiz.items.map((it, i) =>
          '<button class="cell' + (it.choice !== null ? ' done' : '') + '" data-i="' + i + '">' + (i + 1) + '</button>'
        ).join('') +
      '</div>' +
      '<div class="sheet-legend"><span><i class="dot done"></i>Đã trả lời</span><span><i class="dot"></i>Chưa trả lời</span></div>' +
      '<button class="btn btn-primary btn-block" data-act="submit">Nộp bài</button>' +
    '</div>';
  document.body.appendChild(sheet);
  const close = () => sheet.remove();
  sheet.addEventListener('click', (e) => { if (e.target === sheet) close(); });
  sheet.querySelector('[data-act="close"]').onclick = close;
  sheet.querySelectorAll('.cell').forEach((c) => {
    c.onclick = () => { close(); scrollToQuestion(Number(c.dataset.i)); };
  });
  sheet.querySelector('[data-act="submit"]').onclick = () => { close(); submit(); };
}

function submit() {
  const left = quiz.items.filter((i) => i.choice === null).length;
  if (left && !confirm('Còn ' + left + ' câu chưa trả lời (sẽ tính là sai). Vẫn nộp bài?')) {
    scrollToQuestion(quiz.items.findIndex((i) => i.choice === null));
    return;
  }
  quiz.submitted = true;
  leaveGuard = null;

  const { id, items, mode } = quiz;
  const total = items.length;
  const score = items.filter((i) => i.choice === i.q.answer).length;
  const st = store.get(id);
  if (mode === 'all') {
    st.wrong = items.filter((i) => i.choice !== i.q.answer).map((i) => i.q.id);
    st.attempts = (st.attempts || 0) + 1;
    st.last = { score, total, date: new Date().toISOString() };
    st.best = Math.max(st.best || 0, pct(score, total));
  } else {
    const set = new Set(st.wrong || []);
    items.forEach((i) => { if (i.choice === i.q.answer) set.delete(i.q.id); else set.add(i.q.id); });
    st.wrong = [...set];
  }
  store.set(id, st);
  quiz.result = { score, total, remainingWrong: wrongIdsFor(quiz.L).length };
  renderResult('wrong');
}

/* ---------- Trang 4: Kết quả ---------- */
function renderResult(tab) {
  const { L, items, result, mode, id } = quiz;
  const wrongItems = items.filter((i) => i.choice !== i.q.answer);
  const rightItems = items.filter((i) => i.choice === i.q.answer);
  const blank = items.filter((i) => i.choice === null).length;
  if (tab === 'wrong' && !wrongItems.length) tab = 'all';
  const p = pct(result.score, result.total);
  const list = tab === 'wrong' ? wrongItems : tab === 'right' ? rightItems : items;

  const itemHtml = (it) => {
    const n = items.indexOf(it) + 1;
    const ok = it.choice === it.q.answer;
    const opts = it.order.map((orig, k) => {
      const cls = orig === it.q.answer ? ' is-correct' : (orig === it.choice ? ' is-wrong' : '');
      const mark = orig === it.q.answer ? ICON.check : (orig === it.choice ? ICON.cross : '');
      return '<li class="ropt' + cls + '"><span class="opt-letter">' + LETTERS[k] + '</span><span class="opt-text">' + inline(it.q.options[orig]) + '</span><span class="mark">' + mark + '</span></li>';
    }).join('');
    const correctLetter = LETTERS[it.order.indexOf(it.q.answer)];
    const ww = it.q.why_wrong && it.choice !== null && !ok ? it.q.why_wrong[it.choice] : null;
    const explain = ok
      ? (it.q.explanation ? '<details class="explain-toggle"><summary>Xem giải thích</summary><div class="explain">' + md(it.q.explanation) + '</div></details>' : '')
      : '<div class="answer-box">' +
          '<div class="answer-line">' + (it.choice === null ? '<span class="tag tag-muted">Chưa trả lời</span> ' : '') + 'Đáp án đúng: <b>' + correctLetter + '. ' + inline(it.q.options[it.q.answer]) + '</b></div>' +
          (it.q.explanation ? '<div class="explain"><span class="explain-label">Giải thích</span>' + md(it.q.explanation) + '</div>' : '') +
          (ww ? '<div class="explain explain-wrong"><span class="explain-label">Vì sao ' + LETTERS[it.order.indexOf(it.choice)] + ' sai</span>' + md(ww) + '</div>' : '') +
        '</div>';
    return '<article class="rcard ' + (ok ? 'ok' : 'bad') + '">' +
      '<div class="rcard-status">' + (ok ? ICON.check + ' Đúng' : ICON.cross + ' Sai') + '</div>' +
      questionHtml(it.q, n) +
      '<ul class="ropts">' + opts + '</ul>' + explain +
    '</article>';
  };

  const retryWrong = result.remainingWrong
    ? '<a class="btn btn-bad" href="#/quiz/' + encodeURIComponent(id) + '?mode=wrong" data-retry="wrong">Làm lại câu sai (' + result.remainingWrong + ')</a>'
    : '';
  app.innerHTML =
    topbar({ title: L.title, sub: 'Kết quả' + (mode === 'wrong' ? ' · làm lại câu sai' : ''), back: true }) +
    '<main class="page">' +
      '<section class="summary">' +
        '<div class="ring" style="--p:' + p + '"><div><b>' + p + '%</b><span>' + result.score + '/' + result.total + '</span></div></div>' +
        '<div class="summary-counts">' +
          '<span class="c-ok">' + rightItems.length + ' đúng</span>' +
          '<span class="c-bad">' + (wrongItems.length - blank) + ' sai</span>' +
          (blank ? '<span class="c-muted">' + blank + ' bỏ trống</span>' : '') +
        '</div>' +
        '<div class="actions">' +
          retryWrong +
          '<a class="btn' + (result.remainingWrong ? ' btn-ghost' : ' btn-primary') + '" href="#/quiz/' + encodeURIComponent(id) + '" data-retry="all">Làm lại toàn bộ</a>' +
          '<a class="btn btn-ghost" href="#/">Về danh mục</a>' +
        '</div>' +
      '</section>' +
      '<div class="tabs" role="tablist">' +
        (wrongItems.length ? '<button role="tab" data-tab="wrong" class="' + (tab === 'wrong' ? 'on' : '') + '">Câu sai (' + wrongItems.length + ')</button>' : '') +
        '<button role="tab" data-tab="right" class="' + (tab === 'right' ? 'on' : '') + '">Câu đúng (' + rightItems.length + ')</button>' +
        '<button role="tab" data-tab="all" class="' + (tab === 'all' ? 'on' : '') + '">Tất cả</button>' +
      '</div>' +
      '<div class="rlist">' + (list.length ? list.map(itemHtml).join('') : '<p class="muted center">Không có câu nào.</p>') + '</div>' +
    '</main>';

  bindBack('#/lesson/' + encodeURIComponent(id));
  app.querySelectorAll('[data-tab]').forEach((b) => { b.onclick = () => renderResult(b.dataset.tab); });
  app.querySelectorAll('[data-retry]').forEach((a) => {
    a.onclick = (e) => { e.preventDefault(); go(a.getAttribute('href')); };
  });
}

/* ---------- Xem toàn bộ đề và đáp án (để duyệt / ôn nhanh) ---------- */
async function viewReview(id) {
  quiz = null;
  app.innerHTML = topbar({ title: 'Đề và đáp án', back: true }) + '<main class="page"><div class="loading">Đang tải…</div></main>';
  bindBack('#/lesson/' + encodeURIComponent(id));
  let L;
  try { L = await loadLesson(id); } catch (e) { return errorView(e.message, true), bindBack('#/'); }
  setTitle(L.title);
  const sections = L.sections && L.sections.length ? L.sections : [...new Set(L.questions.map((q) => q.section || 'Khác'))];
  let n = 0;
  const body = sections.map((s) => {
    const qs = L.questions.filter((q) => (q.section || 'Khác') === s);
    if (!qs.length) return '';
    return '<section class="rv-section"><h2>' + esc(s) + ' <span class="muted">· ' + qs.length + ' câu</span></h2>' +
      qs.map((q) => {
        n++;
        return '<article class="rcard rv">' +
          '<div class="rcard-status"><span class="tag ' + (q.type === 'lam-sang' ? 'tag-case' : 'tag-recall') + '">' + (q.type === 'lam-sang' ? 'Lâm sàng' : 'Ghi nhớ') + '</span></div>' +
          questionHtml(q, n) +
          '<ul class="ropts">' + q.options.map((o, k) =>
            '<li class="ropt' + (k === q.answer ? ' is-correct' : '') + '"><span class="opt-letter">' + LETTERS[k] + '</span><span class="opt-text">' + inline(o) +
            (q.why_wrong && q.why_wrong[k] ? '<small class="why">' + inline(q.why_wrong[k]) + '</small>' : '') +
            '</span><span class="mark">' + (k === q.answer ? ICON.check : '') + '</span></li>'
          ).join('') + '</ul>' +
          (q.explanation ? '<div class="explain"><span class="explain-label">Giải thích</span>' + md(q.explanation) + '</div>' : '') +
        '</article>';
      }).join('') + '</section>';
  }).join('');
  app.innerHTML = topbar({ title: L.title, sub: 'Đề và đáp án', back: true }) + '<main class="page">' + body + '</main>';
  bindBack('#/lesson/' + encodeURIComponent(id));
}

/* ---------- Khởi động ---------- */
if ('serviceWorker' in navigator && location.protocol !== 'file:') {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
if (location.protocol === 'file:') {
  app.innerHTML = '<main class="page"><div class="empty"><p>Không mở trực tiếp file này.</p><p class="muted">Chạy <code>python3 -m http.server</code> trong thư mục app rồi mở <code>http://localhost:8000</code>, hoặc dùng bản trên GitHub Pages.</p></div></main>';
} else {
  route();
}
