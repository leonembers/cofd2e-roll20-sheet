// Minimal local emulation of the Roll20 sheet sandbox (preview only; NOT uploaded to Roll20).
(function(){
const Q = new URLSearchParams(location.search);
const store = {}; const handlers = {};
let ctxRow = null;
window.on = (evs, cb) => evs.toLowerCase().split(/\s+/).filter(Boolean).forEach(e => (handlers[e] = handlers[e] || []).push(cb));
const fire = (e, info) => (handlers[e.toLowerCase()] || []).forEach(cb => { try { cb(info || {}); } catch (err) { console.error(e, err); } });
window.getTranslationByKey = (k) => (window.TRANSLATION || {})[k] || false;
window.generateRowID = () => '-' + Math.random().toString(36).slice(2, 12);
window.removeRepeatingRow = (r) => { const id = r.split('_')[2]; document.querySelectorAll('.repitem[data-reprowid="' + id + '"]').forEach(e => e.remove()); Object.keys(rows).forEach(s => rows[s] = rows[s].filter(x => x !== id)); };
window.setSectionOrder = (sec, order) => { const c = document.querySelector('.repcontainer[data-groupname="repeating_' + sec + '"]'); order.forEach(id => { const e = c && c.querySelector('.repitem[data-reprowid="' + id + '"]'); if (e) c.appendChild(e); }); rows[sec] = order.slice(); store[('_reporder_repeating_' + sec).toLowerCase()] = order.join(','); };
const resolve = (n) => {
  const m = n.match(/^repeating_([^_]+)_(.+)$/);
  if (m && ctxRow && ctxRow.sec === m[1] && !m[2].startsWith('-')) return `repeating_${m[1]}_${ctxRow.id}_${m[2]}`;
  return n;
};
window.getAttrs = (names, cb) => { const o = {}; names.forEach(n => { const r = resolve(n); o[n] = store[r.toLowerCase()] ?? defaults(r); }); setTimeout(() => cb(o), 0); };
const defaults = (n) => { const el = findEls(n)[0]; if (!el) return ''; if (el.type === 'checkbox' || el.type === 'radio') return el.hasAttribute('checked') ? el.value : '0'; return el.getAttribute('value') ?? ''; };
window.setAttrs = (obj, opts, cb) => {
  if (typeof opts === 'function') { cb = opts; opts = {}; }
  Object.entries(obj).forEach(([k, v]) => {
    const r = resolve(k); const key = r.toLowerCase(); const old = store[key]; store[key] = String(v); render(r);
    if (!(opts && opts.silent) && old !== String(v)) changed(r, old, v);
  });
  if (cb) setTimeout(cb, 0);
};
window.getSectionIDs = (sec, cb) => { sec = sec.replace(/^repeating_/, ''); setTimeout(() => cb(rows[sec] || []), 0); };
const rows = {};
function findEls(full) {
  const m = full.match(/^repeating_([^_]+)_(-[^_]+)_(.+)$/);
  if (m) { const item = document.querySelector(`.repitem[data-reprowid="${m[2]}"]`); return item ? [...item.querySelectorAll(`[name="attr_${m[3]}"]`)] : []; }
  return [...document.querySelectorAll(`[name="attr_${full}" i]`)].filter(e => !e.closest('.repitem'));
}
function render(full) {
  const v = store[full.toLowerCase()];
  findEls(full).forEach(el => {
    if (el.tagName === 'SPAN') el.textContent = v;
    else if (el.tagName === 'IMG') { if (v) el.src = v; }
    else if (el.type === 'checkbox' || el.type === 'radio') el.checked = (el.value === v);
    else { el.value = v; if (el.type === 'hidden') el.setAttribute('value', v); }
  });
}
function changed(full, old, v) {
  const m = full.match(/^repeating_([^_]+)_(-[^_]+)_(.+)$/);
  const info = { sourceAttribute: full, previousValue: old, newValue: String(v), sourceType: 'sheetworker' };
  if (m) { const prev = ctxRow; ctxRow = { sec: m[1], id: m[2] }; fire(`change:repeating_${m[1]}:${m[3]}`, info); fire(`change:repeating_${m[1]}`, info); ctxRow = prev; }
  else fire(`change:${full}`, info);
}
function bind(root, row) {
  root.querySelectorAll('[name^="attr_"]').forEach(el => {
    const a = el.getAttribute('name').slice(5);
    const full = row ? `repeating_${row.sec}_${row.id}_${a}` : a;
    el.addEventListener('change', () => {
      const v = el.type === 'checkbox' ? (el.checked ? el.value : '0') : el.value;
      const old = store[full.toLowerCase()]; store[full.toLowerCase()] = v; if (el.type !== 'hidden') render(full); changed(full, old, v);
    });
  });
  root.querySelectorAll('button[type="action"]').forEach(b => b.addEventListener('click', () => {
    const a = b.getAttribute('name').replace(/^act_/, '');
    if (row) { const prev = ctxRow; ctxRow = row; fire(`clicked:repeating_${row.sec}:${a}`, { sourceAttribute: `repeating_${row.sec}_${row.id}_${a}`, triggerName: `clicked:repeating_${row.sec}_${row.id}_${a}` }); ctxRow = prev; }
    else fire(`clicked:${a}`, { triggerName: `clicked:${a}` });
  }));
  root.querySelectorAll('button[type="roll"]').forEach(b => b.addEventListener('click', () => console.log('ROLL', b.value)));
}
function addRow(fs, sec, data) {
  const id = window.generateRowID();
  const item = document.createElement('div'); item.className = 'repitem'; item.dataset.reprowid = id; item.innerHTML = fs.innerHTML;
  fs._container.appendChild(item); (rows[sec] = rows[sec] || []).push(id);
  bind(item, { sec, id });
  Object.entries(data || {}).forEach(([k, v]) => { if (v !== null && v !== undefined) { store[`repeating_${sec}_${id}_${k}`.toLowerCase()] = String(v); render(`repeating_${sec}_${id}_${k}`); } });
  return id;
}
window.addEventListener('DOMContentLoaded', () => {
  const root = document.querySelector('.charsheet');
  // Roll20 legacy sanitizer prefixes classes with "sheet-"
  root.querySelectorAll('[class]').forEach(el => { if (el.closest('fieldset') && false) return;
    el.className = (el.getAttribute('class')||'').split(/\s+/).filter(Boolean).map(c => c.startsWith('sheet-') || ['repcontainer','repitem','repcontrol','charsheet'].includes(c) ? c : 'sheet-' + c).join(' '); });
  root.querySelectorAll('rolltemplate, .sheet-rolltemplates').forEach(e => e.remove());
  // repeating sections
  const fss = [...root.querySelectorAll('fieldset')];
  fss.forEach(fs => {
    const sec = [...fs.classList].find(c => c.startsWith('sheet-repeating_') || c.startsWith('repeating_')).replace(/^sheet-repeating_|^repeating_/, '');
    fs.style.display = 'none';
    const c = document.createElement('div'); c.className = 'repcontainer'; c.dataset.groupname = 'repeating_' + sec; fs.after(c); fs._container = c; fs._sec = sec;
    const ctl = document.createElement('div'); ctl.className = 'repcontrol';
    const add = document.createElement('button'); add.className = 'btn repcontrol_add'; add.textContent = '+Add'; add.onclick = () => addRow(fs, sec);
    ctl.appendChild(add); c.after(ctl);
  });
  bind(root, null);
  const data = window.PREVIEW_DATA || {};
  Object.entries(data).forEach(([k, v]) => {
    if (k.startsWith('_')) return;
    if (k.startsWith('repeating_')) { const sec = k.slice(10); const fs = fss.find(f => f._sec === sec); if (fs) v.forEach(r => addRow(fs, sec, r)); return; }
    store[k.toLowerCase()] = String(v); render(k);
  });
  // compute repeating derived (dots, roll parts)
  Object.keys(rows).forEach(sec => rows[sec].forEach(id => ['merit','rating','pool_dice'].forEach(a => { const f = `repeating_${sec}_${id}_${a}`; if (store[f.toLowerCase()] !== undefined) changed(f, '', store[f.toLowerCase()]); })));
  // make sure every attr has its default rendered
  root.querySelectorAll('[name^="attr_"]').forEach(el => { if (el.closest('.repitem') || el.closest('fieldset')) return; const a = el.getAttribute('name').slice(5); if (store[a.toLowerCase()] === undefined && el.type === 'hidden') store[a.toLowerCase()] = el.getAttribute('value') ?? ''; });
  fire('sheet:opened', {});
  Object.keys(data).filter(k => !k.startsWith('_') && !k.startsWith('repeating_')).forEach(k => changed(k, '', data[k]));
  if (Q.get('splat')) setTimeout(() => fire('clicked:sheet_type_' + Q.get('splat'), {}), 30);
  if (Q.get('page')) setTimeout(() => fire('clicked:page_' + Q.get('page'), {}), 50);
  if (Q.get('form')) setTimeout(() => setAttrs({ form: Q.get('form') }), 60);
  if (Q.get('cond')) setTimeout(() => { const o = {}; Q.get('cond').split(',').forEach(c => o['cond_' + c] = '1'); setAttrs(o); }, 70);
  if (Q.get('urkhar')) setTimeout(() => setAttrs({ urkhar_enabled: '1' }), 60);
});
})();
