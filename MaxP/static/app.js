const $ = (s, r = document) => r.querySelector(s);
const state = { token: localStorage.getItem('token'), me: null, scope: 'all', page: 1, size: 12, editingId: null, authMode: 'login' };

function h(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'class') n.className = v;
    else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) n.setAttribute(k, v === true ? '' : v);
  }
  n.append(...kids.flat().filter(x => x != null && x !== false));
  return n;
}

let toastTimer;
function toast(msg, bad = false) {
  const t = $('#toast');
  t.textContent = msg;
  t.className = 'show' + (bad ? ' bad' : '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.className = ''), 3200);
}

function errorText(d) {
  if (d && typeof d.detail === 'string') return d.detail;
  if (d && Array.isArray(d.detail)) return d.detail.map(e => e.msg).join('; ');
  return 'Щось пішло не так';
}

async function api(path, { method = 'GET', body, form } = {}) {
  const headers = {};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  let payload;
  if (form) payload = new URLSearchParams(form);
  else if (body) { headers['Content-Type'] = 'application/json'; payload = JSON.stringify(body); }
  const res = await fetch(path, { method, headers, body: payload });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    if (res.status === 401 && state.token) logout(true);
    throw new Error(errorText(data));
  }
  return data;
}

/* ---------- сесія ---------- */
function setToken(t) {
  state.token = t;
  t ? localStorage.setItem('token', t) : localStorage.removeItem('token');
}
async function loadMe() {
  try { state.me = await api('/auth/me'); } catch { state.me = null; setToken(null); }
}
function logout(expired = false) {
  setToken(null); state.me = null; state.scope = 'all'; state.page = 1;
  renderUser(); syncScope(); loadBooks();
  toast(expired ? 'Сесія закінчилась, увійди знову' : 'Ти вийшов з акаунта');
}
function renderUser() {
  const box = $('#userbox');
  box.replaceChildren();
  if (state.me) {
    box.append(h('span', { class: 'who' }, state.me.username), h('button', { class: 'ghost', onclick: () => logout() }, 'Вийти'));
  } else {
    box.append(h('button', { class: 'ghost', onclick: () => openAuth('login') }, 'Увійти'),
               h('button', { class: 'primary', onclick: () => openAuth('register') }, 'Реєстрація'));
  }
  $('[data-scope=mine]').disabled = !state.me;
}

/* ---------- авторизація ---------- */
function openAuth(mode) {
  state.authMode = mode;
  const reg = mode === 'register';
  $('#authTitle').textContent = reg ? 'Реєстрація' : 'Вхід';
  $('#authSubmit').textContent = reg ? 'Створити акаунт' : 'Увійти';
  $('#authSwitch').textContent = reg ? 'Вже є акаунт?' : 'Немає акаунта?';
  $('#emailRow').hidden = !reg;
  $('#emailRow input').required = reg;
  $('#authForm [name=password]').autocomplete = reg ? 'new-password' : 'current-password';
  $('#authErr').textContent = '';
  $('#authDlg').showModal();
}
async function submitAuth(e) {
  e.preventDefault();
  const f = new FormData(e.target);
  $('#authErr').textContent = '';
  try {
    if (state.authMode === 'register') {
      await api('/auth/register', { method: 'POST', body: { username: f.get('username'), email: f.get('email'), password: f.get('password') } });
    }
    setToken(null);
    const t = await api('/auth/login', { method: 'POST', form: { username: f.get('username'), password: f.get('password') } });
    setToken(t.access_token);
    await loadMe();
    renderUser();
    e.target.reset();
    $('#authDlg').close();
    toast(`Привіт, ${state.me.username}!`);
    loadBooks();
  } catch (err) {
    $('#authErr').textContent = err.message;
  }
}

/* ---------- книги ---------- */
const hue = s => [...s].reduce((a, c) => (a * 31 + c.charCodeAt(0)) % 360, 7);
const stars = n => (n ? '★'.repeat(n) + '☆'.repeat(5 - n) : '');

function bookCard(b) {
  const mine = state.me && b.owner_id === state.me.id;
  return h('article', { class: 'book' },
    h('div', { class: 'cover', style: `--h:${hue(b.title + b.author)}` }, h('h3', {}, b.title), h('p', {}, b.author)),
    h('div', { class: 'meta' }, h('span', {}, [b.genre, b.year].filter(Boolean).join(', ')),
      b.rating ? h('span', { class: 'stars', title: `Оцінка ${b.rating} з 5` }, stars(b.rating)) : null),
    b.description ? h('p', { class: 'desc' }, b.description) : null,
    mine ? h('div', { class: 'actions' },
      h('button', { onclick: () => openBook(b) }, 'Редагувати'),
      h('button', { class: 'danger', onclick: () => removeBook(b) }, 'Видалити')) : null);
}

async function loadBooks() {
  const p = new URLSearchParams({ page: state.page, size: state.size, sort: $('#sort').value });
  const q = $('#q').value.trim();
  if (q) p.set('q', q);
  if ($('#genre').value) p.set('genre', $('#genre').value);
  try {
    const data = await api(`/books/${state.scope === 'mine' ? 'my' : ''}?${p}`);
    const grid = $('#grid');
    grid.replaceChildren(...(data.items.length
      ? data.items.map(bookCard)
      : [h('p', { class: 'empty' }, q || $('#genre').value ? 'За цим запитом нічого не знайдено.' : state.scope === 'mine' ? 'У тебе ще немає книг. Додай першу!' : 'Полиця порожня.')]));
    renderPager(data);
  } catch (err) { toast(err.message, true); }
}
function renderPager({ page, pages }) {
  const nav = $('#pager');
  nav.replaceChildren();
  if (pages <= 1) return;
  nav.append(
    h('button', { disabled: page <= 1, onclick: () => goTo(page - 1) }, 'Назад'),
    h('span', { class: 'muted' }, `Сторінка ${page} з ${pages}`),
    h('button', { disabled: page >= pages, onclick: () => goTo(page + 1) }, 'Далі'));
}
function goTo(p) { state.page = p; loadBooks(); window.scrollTo({ top: 0 }); }

async function loadMeta() {
  try {
    const [genres, s] = await Promise.all([api('/books/genres'), api('/books/stats')]);
    const cur = $('#genre').value;
    $('#genre').replaceChildren(h('option', { value: '' }, 'Усі жанри'), ...genres.map(g => h('option', { value: g }, g)));
    $('#genre').value = genres.includes(cur) ? cur : '';
    $('#genreList').replaceChildren(...genres.map(g => h('option', { value: g })));
    const rating = s.avg_rating ? `, середня оцінка ${String(s.avg_rating).replace('.', ',')}` : '';
    $('#summary').textContent = s.books ? `${s.books} книг від ${s.authors} авторів${rating}.` : 'Тут поки порожньо, стань першим, хто додасть книгу.';
  } catch { /* не критично */ }
}

function syncScope() {
  document.querySelectorAll('.seg button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.scope === state.scope)));
}

/* ---------- форма книги ---------- */
function openBook(book = null) {
  if (!state.me) { toast('Спочатку увійди в акаунт'); return openAuth('login'); }
  state.editingId = book ? book.id : null;
  const f = $('#bookForm');
  f.reset();
  $('#bookTitle').textContent = book ? 'Редагувати книгу' : 'Нова книга';
  $('#bookErr').textContent = '';
  if (book) for (const k of ['title', 'author', 'genre', 'year', 'rating', 'description']) f.elements[k].value = book[k] ?? '';
  $('#bookDlg').showModal();
}
async function submitBook(e) {
  e.preventDefault();
  const f = new FormData(e.target);
  const val = k => (f.get(k) || '').toString().trim() || null;
  const body = {
    title: val('title'), author: val('author'), genre: val('genre'), description: val('description'),
    year: val('year') ? Number(val('year')) : null, rating: val('rating') ? Number(val('rating')) : null,
  };
  try {
    if (state.editingId) await api(`/books/${state.editingId}`, { method: 'PATCH', body });
    else await api('/books/', { method: 'POST', body });
    $('#bookDlg').close();
    toast(state.editingId ? 'Збережено' : 'Книгу додано');
    await Promise.all([loadBooks(), loadMeta()]);
  } catch (err) { $('#bookErr').textContent = err.message; }
}
async function removeBook(b) {
  if (!confirm(`Видалити «${b.title}»?`)) return;
  try {
    await api(`/books/${b.id}`, { method: 'DELETE' });
    toast('Книгу видалено');
    await Promise.all([loadBooks(), loadMeta()]);
  } catch (err) { toast(err.message, true); }
}

/* ---------- старт ---------- */
let debounce;
function refresh() { state.page = 1; loadBooks(); }

$('#tools').addEventListener('submit', e => e.preventDefault());
$('#q').addEventListener('input', () => { clearTimeout(debounce); debounce = setTimeout(refresh, 250); });
$('#genre').addEventListener('change', refresh);
$('#sort').addEventListener('change', refresh);
$('.seg').addEventListener('click', e => {
  const b = e.target.closest('button');
  if (!b || b.disabled) return;
  state.scope = b.dataset.scope; syncScope(); refresh();
});
$('#addBtn').addEventListener('click', () => openBook());
$('#authForm').addEventListener('submit', submitAuth);
$('#authSwitch').addEventListener('click', () => openAuth(state.authMode === 'login' ? 'register' : 'login'));
$('#bookForm').addEventListener('submit', submitBook);
document.querySelectorAll('[data-close]').forEach(b => b.addEventListener('click', () => b.closest('dialog').close()));

(async () => {
  if (state.token) await loadMe();
  renderUser();
  await Promise.all([loadMeta(), loadBooks()]);
})();
