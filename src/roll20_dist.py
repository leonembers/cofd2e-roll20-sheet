"""Post-process the build into a Roll20-ready dist/ (modern / non-legacy CSS mode).
- Prefixes every HTML class with sheet- (modern mode does not do this, our CSS expects it).
- Wraps the sheet in <div class="charsheet"> so .charsheet selectors match in modern mode.
- Swaps IMG_BASE/<file> for the Roll20 library URLs in img_urls.json.
- Adds missing i18n keys."""
import re, json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = re.search(r'IMG_BASE = "([^"]+)"', open(f'{R}/src/build.py').read()).group(1)
urls = json.load(open(f'{R}/img_urls.json'))
def img(s):
    def f(m):
        n = m.group(1)
        if n not in urls: raise SystemExit(f'missing image url: {n}')
        return urls[n]
    s = s.replace(BASE + " is replaced", "IMG_BASE is replaced")
    s = re.sub(re.escape(BASE) + r'/([A-Za-z0-9_.-]+)', f, s)
    assert BASE not in s
    return s
h = open(f'{R}/sheet.html', encoding='utf-8').read()
c = open(f'{R}/sheet.css', encoding='utf-8').read()
i = h.index('<rolltemplate')
body, rest = h[:i], h[i:]
def pre(m):
    toks = m.group(2).split()
    return m.group(1) + ' '.join(t if t.startswith('sheet-') or t.startswith('repeating_') or '{{' in t else 'sheet-' + t for t in toks) + m.group(3)
cls = re.compile(r'(\bclass\s*=\s*")([^"]*)(")')
body = cls.sub(pre, body)
rest = cls.sub(pre, rest)
body = '<!--CS-->\n' + body  # Roll20 CSE supplies the .charsheet wrapper itself; no nested wrapper
h = img(body + rest)
# --- (1) default values + init worker for every attribute referenced by rolls ---
nonrep = re.sub(r'<fieldset.*?</fieldset>', '', h, flags=re.S)
nonrep = re.sub(r'<rolltemplate.*?</rolltemplate>', '', nonrep, flags=re.S)
nonrep_noscript = re.sub(r'<script.*?</script>', '', nonrep, flags=re.S)
refs = set(re.findall(r'@\{([A-Za-z0-9_]+)\}', nonrep_noscript))
for m in re.finditer(r'(?:@\{|getAttrs\(\[)[^\]]*', nonrep): pass
inp = {}
for m in re.finditer(r'<(input|select|textarea)\b[^>]*name="attr_([^"]+)"[^>]*>', nonrep_noscript):
    inp.setdefault(m.group(2).lower(), m.group(0))
SKIP = {'character_name', 'modifiermacro', 'dicepoolmacro'}
init = {}
AUDIT = []
for r in sorted(refs):
    k = r.lower()
    if k in SKIP: continue
    tag = inp.get(k)
    textish = tag is not None and (tag.startswith('<textarea') or tag.startswith('<select') or 'type="text"' in tag)
    if tag is None and re.search(r'(name|text|label|summary|breakdown|attack|sun|note)$', k): textish = True
    init[r] = '' if textish else '0'
    if tag is None: AUDIT.append(f'{r}: no input (worker-set); init "{init[r]}"')
    elif 'value=' not in tag and not textish:
        AUDIT.append(f'{r}: input without default; added value="0"')
        h = h.replace(tag, tag.replace('name=', 'value="0" name=', 1), 1)
INIT_JS = """
        // Roll20 'No attribute was found' guard: give every roll-referenced attribute a stored value
        const R20_DEFAULTS = %s;
        on("sheet:opened", () => getAttrs(["dark_mode"], v => { if (v.dark_mode === undefined || v.dark_mode === null || v.dark_mode === "") setAttrs({dark_mode: "1"}, {silent: true}); }));
        on("sheet:opened", () => getAttrs(Object.keys(R20_DEFAULTS), v => {
            const u = {};
            Object.keys(R20_DEFAULTS).forEach(k => { if (v[k] === undefined || v[k] === null || (v[k] === "" && R20_DEFAULTS[k] === "0")) u[k] = R20_DEFAULTS[k]; });
            if (Object.keys(u).length) setAttrs(u, {silent: true});
        }));
""" % json.dumps(init)
h = h.replace('<script type="text/worker">', '<script type="text/worker">' + INIT_JS, 1)
open(f'{R}/dist/AUDIT.txt', 'w').write(f'{len(init)} roll-referenced attributes initialised on sheet:opened\n' + '\n'.join(AUDIT) + '\n')
# --- (2) ASCII-only output: entities in HTML, \\u in worker JS ---
def asc_html(s):
    out = []; pos = 0
    for m in re.finditer(r'<script type="text/worker">.*?</script>', s, re.S):
        out.append(''.join(ch if ord(ch) < 128 else f'&#{ord(ch)};' for ch in s[pos:m.start()]))
        out.append(''.join(ch if ord(ch) < 128 else (f'\\u{ord(ch):04x}' if ord(ch) < 0x10000 else ''.join(f'\\u{x:04x}' for x in __import__('struct').unpack('<2H', ch.encode('utf-16-le')))) for ch in m.group(0)))
        pos = m.end()
    out.append(''.join(ch if ord(ch) < 128 else f'&#{ord(ch)};' for ch in s[pos:]))
    return ''.join(out)
h = asc_html(h)
c = img(c)
c += """
/* ---- Roll20 dialog fit (~800-850px) ---- */
.charsheet .sheet-background { width: auto !important; max-width: 905px; box-sizing: border-box; padding: 14px 34px 60px 40px; }
.charsheet button.sheet-page-settings { position: static !important; vertical-align: middle; margin-right: 4px; }
.charsheet .sheet-background img, .charsheet .sheet-background textarea, .charsheet .sheet-background input[type=text] { max-width: 100%; }
.charsheet .sheet-rollbar, .charsheet .sheet-wp-bar, .charsheet .sheet-entry-body { flex-wrap: wrap; }
"""

# --- (3) Dark mode: own toggle + Roll20 native body.sheet-darkmode, stacking-context fix ---
DM = 'input.sheet-dm[value="1"] ~ .sheet-background'
h = h.replace('<!--CS-->\n', '<input type="hidden" class="sheet-dm" name="attr_dark_mode" value="1" />\n', 1)
anchor = '<div class="sheet-edition-label"><span data-i18n="dice-rules-u">'
assert anchor in h
h = h.replace(anchor, '<div class="sheet-edition-label">DISPLAY</div>\n        <div class="sheet-display-opts"><label title="Dark sheet theme (independent of Roll20\'s own dark mode switch)"><input type="checkbox" name="attr_dark_mode" value="1" checked /> Dark mode (uncheck for light mode)</label></div>\n        <div class="sheet-spacer"></div>\n        ' + anchor, 1)
c = re.sub(r'/\*.*?\*/', '', c, flags=re.S)
def split_sel(t):
    out, d, cur = [], 0, ''
    for ch in t:
        if ch in '([': d += 1
        elif ch in ')]': d -= 1
        if ch == ',' and d == 0: out.append(cur); cur = ''
        else: cur += ch
    out.append(cur); return out
def dm_sel(sel):
    s2 = sel.strip()
    s2 = re.sub(r'^(?:body)?\.charsheet\.sheet-darkmode\b', DM, s2)
    s2 = re.sub(r'^(?:body)?\.sheet-darkmode\s+(?:\.charsheet\s+)?\.sheet-background(?![-\w])', DM, s2)
    s2 = re.sub(r'^(?:body)?\.sheet-darkmode\s+(?:\.charsheet\s+)?', DM + ' ', s2)
    return s2
def rw(m):
    pre = m.group(1)
    if 'sheet-darkmode' not in pre or 'rolltemplate' in pre: return m.group(0)
    sels = [x.strip() for x in split_sel(pre) if x.strip()]
    extra = [dm_sel(x) for x in sels if re.match(r'^(?:body)?\.(?:charsheet\.)?sheet-darkmode\b', x)]
    return ',\n'.join(sels + extra) + ' {'
c = re.sub(r'([^{}]+)\{', rw, c)
D = ['body.sheet-darkmode .sheet-background', DM]
c += """
/* ---- Roll20 fixes: stacking context so the z-index:-1 frame art is not painted behind Roll20's dialog ---- */
.charsheet .sheet-background { position: relative; z-index: 0; isolation: isolate; }
/* ---- dark theme base (Roll20 native dark mode OR the sheet's own Dark mode checkbox) ---- */
%(D0)s, %(D1)s { background: #141417 !important; color: #e4e4e4; border-radius: 6px; }
/* splat picker as pills */
.charsheet .sheet-splat-select { display: flex; flex-wrap: wrap; gap: 6px; }
.charsheet .sheet-splat-select button.sheet-toggle, .charsheet .sheet-settings button.sheet-toggle[name^="act_sheet_type_"] { margin: 0; padding: 4px 12px; border: 1px solid #888 !important; border-radius: 14px; background: #f4f1ea !important; color: #222 !important; font-weight: bold; text-shadow: none !important; cursor: pointer; }
%(D0)s .sheet-splat-select button.sheet-toggle, %(D1)s .sheet-splat-select button.sheet-toggle, %(D0)s .sheet-settings button.sheet-toggle[name^="act_sheet_type_"], %(D1)s .sheet-settings button.sheet-toggle[name^="act_sheet_type_"] { background: #26262b !important; color: #e8e8e8 !important; border-color: #5a5a62 !important; }
%(ACT)s { background: var(--temp-dot, #7a1a1a) !important; color: #fff !important; border-color: #fff !important; box-shadow: 0 0 0 2px var(--temp-dot, #7a1a1a); }
.charsheet .sheet-display-opts label { font-weight: bold; }
%(D0)s .sheet-edition-label, %(D1)s .sheet-edition-label { color: #d4b25a !important; letter-spacing: 1px; }
""" % dict(D0=D[0], D1=D[1], ACT=',\n'.join(f'.charsheet input.sheet-type[value="{k}"] ~ * button.sheet-active-{k}' for k in sorted(set(re.findall(r'sheet-active-([A-Za-z0-9-]+)"', h)))))

# --- Background art -----------------------------------------------------------
# Roll20 strips <img> from sheet HTML on save, and its legacy roll-template sanitizer rejects
# '.webp' (and data: URIs) anywhere in sheet.css. Roll20's image library serves webp only.
#  * ART_BASE set (art_base.txt or env ART_BASE: an https folder holding img/*-bg{top,mid,bot}.jpg):
#    plain CSS background-image url()s to the JPGs.
#  * ART_BASE unset: the art layers are <div name="attr_bgart_*"> elements. Roll20 sets an inline
#    background-image from the attribute value, and a sheet worker fills in the library URLs per splat,
#    so no image URL appears in sheet.css or in an <img> tag.
_BG = re.compile(r'input\.sheet-type\[value="([^"]+)"\]\s*~\s*\.sheet-background-image::after\s*\{\s*background:\s*'
                 r"url\('([^']+)'\) top center / 100% auto no-repeat,\s*url\('([^']+)'\) bottom center / 100% auto no-repeat,\s*"
                 r"url\('([^']+)'\) center top / 100% auto repeat-y;?\s*\}")
_inv = {v: k for k, v in urls.items()}
_art = {}
for m in _BG.finditer(c): _art[m.group(1)] = m.groups()[1:]
c = _BG.sub('', c)
_ab = (os.environ.get('ART_BASE') or (open(f'{R}/art_base.txt').read().strip() if os.path.exists(f'{R}/art_base.txt') else '')).rstrip('/')
ART_MODE = 'css' if _ab else 'attr'
c += '\n.sheet-bgart { display: none; position: absolute; top: 0; left: 0; right: 0; bottom: 0; overflow: hidden; z-index: -1; pointer-events: none; }\n'
c += '.charsheet .sheet-background-image::after, .charsheet input.sheet-type ~ .sheet-background-image::after { background: none !important; content: none !important; }\n'
c += 'body.sheet-darkmode .charsheet, .charsheet:has(input.sheet-dm[value="1"]) { background-color: #141417 !important; }\n'
c += 'body.sheet-darkmode .charsheet .sheet-background, .charsheet input.sheet-dm[value="1"] ~ .sheet-background { border-radius: 0 !important; }\n'
c += '.sheet-darkmode .sheet-bgart,\ninput.sheet-dm[value="1"] ~ .sheet-background .sheet-bgart { filter: invert(1) hue-rotate(180deg) brightness(.55) contrast(1.2) saturate(1.6); }\n'
if _art:
    keys = list(_art)
    c += ',\n'.join(f'input.sheet-type[value="{k}"] ~ .sheet-background-image .sheet-bgart' for k in keys) + ' { display: block; }\n'
    if ART_MODE == 'css':
        assert _ab.startswith('https://') and not re.search(r'webp|eval|parent|data:', _ab, re.I), _ab
        for k, (top, bot, mid) in _art.items():
            f = [_inv[u] for u in (top, bot, mid)]
            assert all(re.match(r'^[a-z0-9-]+\.(jpg|png)$', x) for x in f), f
            c += (f'input.sheet-type[value="{k}"] ~ .sheet-background-image .sheet-bgart {{ background: url("{_ab}/{f[0]}") top center / 100% auto no-repeat, '
                  f'url("{_ab}/{f[1]}") bottom center / 100% auto no-repeat, url("{_ab}/{f[2]}") center top / 100% auto repeat-y; }}\n')
            # dark mode: pre-darkened art (white paper -> near-black, ink kept) instead of the invert filter, which turned dark greys into white bands
            c += (f'body.sheet-darkmode .charsheet input.sheet-type[value="{k}"] ~ .sheet-background-image .sheet-bgart, .charsheet:has(input.sheet-dm[value="1"]) input.sheet-type[value="{k}"] ~ .sheet-background-image .sheet-bgart {{ filter: none !important; background: url("{_ab}/dark/{f[0]}") top center / 100% auto no-repeat, '
                  f'url("{_ab}/dark/{f[1]}") bottom center / 100% auto no-repeat, url("{_ab}/dark/{f[2]}") center top / 100% auto repeat-y; }}\n')
        layers = ''
    else:
        # side art: Roll20's documented dynamic-image mechanism <img name="attr_x"> (src filled from the attribute);
        # a column of 48 tiles (about 115px each at sheet width) covers sheets up to ~5500px tall. Top/bottom stay attr-divs.
        layers = ('<input type="hidden" name="attr_bgart_top" value="" /><input type="hidden" name="attr_bgart_mid" value="" /><input type="hidden" name="attr_bgart_bot" value="" />'
                  '<div class="bgart-midcol">' + '<img class="bgart-tile" name="attr_bgart_mid" alt="" />' * 48 + '</div>'
                  '<div class="bgart-top" name="attr_bgart_top"></div><div class="bgart-bot" name="attr_bgart_bot"></div>')
        # Roll20 writes the attribute into an inline style on the div; inline declarations beat sheet CSS, so the
        # layout properties are !important and every layer gets explicit full-size geometry (no top/bottom-only sizing).
        c += '.sheet-bgart > div { position: absolute !important; display: block !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 100% !important; min-height: 100%; background-color: rgba(0,0,0,0) !important; background-size: 100% auto !important; background-attachment: scroll !important; }\n'
        c += '.sheet-bgart > .sheet-bgart-midcol { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: 0; display: block; }\n'
        c += '.sheet-bgart img.sheet-bgart-tile { display: block !important; width: 100% !important; max-width: 100% !important; height: auto !important; margin: 0 !important; padding: 0 !important; border: 0 !important; }\n'
        c += '.sheet-bgart img.sheet-bgart-tile:not([src]), .sheet-bgart img.sheet-bgart-tile[src=""] { visibility: hidden; }\n'
        c += '.sheet-bgart > .sheet-bgart-top { background-repeat: no-repeat !important; background-position: center top !important; z-index: 1; }\n'
        c += '.sheet-bgart > .sheet-bgart-bot { background-repeat: no-repeat !important; background-position: center bottom !important; z-index: 1; }\n'
        ART_JS = ('\n    /* background art: library URLs live in attributes (Roll20 strips <img>; CSS may not name webp) */\n'
                  '    const BGART = ' + json.dumps({k: dict(top=t, bot=b_, mid=m_) for k, (t, b_, m_) in _art.items()}) + ';\n'
                  '    const bgArt = () => getAttrs(["sheettype", "bgart_top", "bgart_mid", "bgart_bot"], v => { const a = BGART[v.sheettype] || {top: "", mid: "", bot: ""}; const u = {};\n'
                  '        ["top", "mid", "bot"].forEach(L => { if ((v["bgart_" + L] || "") !== a[L]) u["bgart_" + L] = a[L]; }); if (Object.keys(u).length) setAttrs(u, {silent: true}); });\n'
                  '    on("sheet:opened change:sheettype", bgArt);\n')
        h = h.replace('<script type="text/worker">', '<script type="text/worker">' + ART_JS, 1)
    h = h.replace('<div class="sheet-background-image"></div>', f'<div class="sheet-background-image"><div class="sheet-bgart">{"".join(cls.sub(pre, layers))}</div></div>', 1)
    assert 'class="sheet-bgart"' in h
# --- i18n fallback for the Hurt Locker block: Roll20 renders "[key]" when the pasted Translation lacks a key,
# so the weapon/armor field labels are plain text (keys stay in translation.json for completeness).
_i = h.index('<div class="sheet-p1-combat">'); _j = h.index('<!-- MEMBERS AND REGALIA -->', _i)
_blk, _n = re.subn(r'<span data-i18n="(lbl-[a-z0-9-]+)">([^<]*)</span>', lambda m: f'<span class="sheet-lbl">{m.group(2)}</span>', h[_i:_j])
assert _n >= 20, _n
h = h[:_i] + _blk + h[_j:]
# --- font-independent icons (no Pictos: it is not guaranteed in the CSE sheet frame; glyphs fell back to letters) ---
h = h.replace('<span class="sheet-pictos sheet-ic-down">3</span>', '<span class="sheet-ic">&#9662;</span>')
h = h.replace('<span class="sheet-pictos">3</span>', '<span class="sheet-ic">&#9652;</span>')
h = h.replace('<span class="sheet-pictos">y</span>', '<span class="sheet-ic sheet-ic-gear">&#9881;&#65038;</span>')
assert 'sheet-pictos' not in h.split('<rolltemplate')[0], 'Pictos span left'
c += """
/* font-independent icons */
.charsheet .sheet-ic { font-family: Arial, sans-serif; font-weight: normal; font-style: normal; display: inline-block; line-height: 1; }
.charsheet button[name="act_page_settings"] .sheet-ic-gear { font-size: 15px; }
.charsheet .sheet-entry > input[type=checkbox].sheet-entry-toggle + .sheet-entry-head::before,
input[type="checkbox"].sheet-entry-toggle + .sheet-entry-head::before { content: "" !important; font-family: Arial, sans-serif !important; position: absolute; left: 5px !important; top: 7px !important; width: 5px; height: 5px; border-right: 2px solid #777; border-bottom: 2px solid #777; transform: rotate(-45deg) !important; text-shadow: none !important; }
input[type="checkbox"].sheet-entry-toggle:checked + .sheet-entry-head::before { border-color: #8b1010 !important; transform: rotate(45deg) !important; top: 5px !important; }
.sheet-darkmode input[type="checkbox"].sheet-entry-toggle + .sheet-entry-head::before, input.sheet-dm[value="1"] ~ .sheet-background input[type="checkbox"].sheet-entry-toggle + .sheet-entry-head::before { border-color: #aaa; }
.sheet-darkmode input[type="checkbox"].sheet-entry-toggle:checked + .sheet-entry-head::before, input.sheet-dm[value="1"] ~ .sheet-background input[type="checkbox"].sheet-entry-toggle:checked + .sheet-entry-head::before { border-color: #e06060 !important; }
.charsheet button[type=roll].sheet-entry-post::before, button.sheet-entry-post::before { content: "" !important; display: none !important; }
button.sheet-spec-caret > span::before { content: "" !important; font-family: Arial, sans-serif !important; width: 4px; height: 4px; border-right: 1.5px solid currentColor; border-bottom: 1.5px solid currentColor; transform: rotate(-45deg); margin: 0 2px 1px 0; vertical-align: middle; }
input.sheet-spec-openflag[value="1"] ~ span::before { transform: rotate(45deg) !important; }
input.sheet-spec-has[value="1"] ~ span::after { content: "*" !important; font-family: Arial, sans-serif !important; font-size: 10px; }
"""
c = re.sub(r'\btransparent\b', 'rgba(0,0,0,0)', c)  # Roll20 filter blocks the substring 'parent'
# --- Roll template CSS guard -------------------------------------------------
# Roll templates (chat) ALWAYS use Roll20's legacy CSS sanitizer, even when the
# sheet itself is CSE/non-legacy. If that sanitizer flags anything in the WHOLE
# sheet.css it silently throws out ALL roll-template styling (sheet still looks
# fine). Known triggers (wiki Building_Character_Sheets/Roll_Templates#Restrictions
# + forum 10407369): '.webp', high-unicode chars even as CSS escapes, '**',
# 'eval' substring, 'overscroll-behavior', '@charset', 'parent' substring.
ASCII_FALLBACK = {'\u2298': 'x', '\u00b7': '-'}
c = ''.join(ASCII_FALLBACK.get(ch, ch) for ch in c)
ESC_FALLBACK = {'25B8': '>', '25BE': 'v', '2699': '=', '2605': '*', '1F4AC': ''}
def _esc(m):
    cp = m.group(1).upper()
    if int(cp, 16) <= 0x7f: return m.group(0)
    if cp not in ESC_FALLBACK: raise SystemExit(f'high-unicode CSS escape \\{cp}: add an ASCII fallback (it kills roll template CSS)')
    return ESC_FALLBACK[cp]
c = re.sub(r'\\([0-9a-fA-F]{2,6}) ?', _esc, c)
assert not re.search(r'webp|\\77', c, re.I), 'webp left in CSS'  # CSS escape for 'w': same URL to the browser, no '.webp' text for the sanitizer
bad = [ch for ch in c if ord(ch) > 127]
assert not bad, f'non-ASCII left in CSS (kills roll templates): {sorted(set(bad))}'
for pat in [r'\.webp', r'webp', r'\*\*', r'eval', r'overscroll', r'@charset', r'parent', r'\\[0-9a-fA-F]{3,6}']:
    m = re.search(pat, c, re.I)
    if m and pat != r'\\[0-9a-fA-F]{3,6}': raise SystemExit(f'roll-template sanitizer trigger {pat!r} at: {c[max(0,m.start()-60):m.end()+20]!r}')
    if m and int(re.sub(r'\\', '', m.group(0)), 16) > 0xff and not m.group(0).startswith('\\77'): raise SystemExit(f'high-unicode escape {m.group(0)}')
os.makedirs(f'{R}/dist', exist_ok=True)

# --- TOPINFO: logo + character info block above the tab bar (visible on every tab) ---
def _cut_div(h, start):
    i = start; depth = 0
    import re as _re
    for m in _re.finditer(r'<div\b|</div>', h[start:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            e = start + m.end(); return h[:start] + h[e:], h[start:e]
    raise AssertionError('unbalanced')
_lg = h.index('<!-- HEADER -->'); _lg = h.index('<div', _lg)
h, _logo = _cut_div(h, _lg)
assert 'sheet-logo' in _logo[:300]
_logo = _logo.replace(_logo[:_logo.index('>') + 1], '<div class="sheet-logo sheet-toplogo">', 1)
_ig = h.index('<div class="sheet-info-grid">')
h, _info = _cut_div(h, _ig)
import re as _re2
# regroup the info grid into label+field cells (robust 3-column layout regardless of per-splat hidden selects)
_inner = _info[len('<div class="sheet-info-grid">'):-len('</div>')]
_inner = _re2.sub(r'<!--.*?-->', '', _inner, flags=_re2.S)
_inner = _re2.sub(r'<div class="sheet-spacer"></div>', '', _inner)
_parts = _re2.split(r'(?=<div class="sheet-input-label">)', _inner)
_pre, _cells = _parts[0], _parts[1:]
assert len(_cells) >= 9, len(_cells)
_info = '<div class="sheet-info-grid sheet-ig2">' + _pre + ''.join(f'<div class="sheet-ifield">{x.strip()}</div>' for x in _cells) + '</div>'
if ART_MODE == 'css':
    import json as _json
    for _u, _f in _json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logo_map.json'))).items():
        assert _u in _logo, _u
        _logo = _logo.replace('src="' + _u + '"', 'src="' + _ab + '/logo/' + _f + '"')
_ta = '<textarea type="text" class="sheet-rollstyle sheet-sheet" name="attr_rolldisplay"></textarea>'
assert h.count(_ta) == 1
h = h.replace(_ta, '<input type="text" readonly class="sheet-rollstyle sheet-sheet sheet-pooltxt" name="attr_rolldisplay" value="" title="Dice pool from the selected traits (abbreviated). Click into the field and scroll to read it in full." />')
_tabs = h.index('<!-- SHEET OPTIONS & PAGE TABS-->')
h = h[:_tabs] + '<div class="sheet-topinfo">' + _logo + _info + '</div>\n' + h[_tabs:]
c += '\n.charsheet .sheet-topinfo { display: block; margin: 0 0 6px; }\n.charsheet .sheet-topinfo .sheet-toplogo { display: block; text-align: center; }\n'
# r6 (Leon override): Werewolf Renown under Skills (left column); Kuruth Triggers + Touchstones at the bottom of the right pane
def _div_span(h, i):
    d = 0
    for m in re.finditer(r'<div\b|</div>', h[i:]):
        d += 1 if m.group(0) == '<div' else -1
        if d == 0: return i, i + m.end()
    raise ValueError(i)
_tc = h.find('<div class="sheet-two-col">\n            <div class="sheet-wolf-lcol">')
assert _tc > 0
_a, _b = _div_span(h, _tc); _two = h[_a:_b]; h = h[:_a] + h[_b:]
_l = _two.find('<div class="sheet-wolf-lcol">'); _la, _lb = _div_span(_two, _l); _lcol = _two[_la:_lb]
_r = _two.find('<div class="sheet-wolf-rcol">'); _ra, _rb = _div_span(_two, _r); _rcol = _two[_ra:_rb]
_t = _lcol.find('<div class="sheet-wolf-ts">'); _ta, _tb = _div_span(_lcol, _t); _ts = _lcol[_ta:_tb]
_ren = _lcol[len('<div class="sheet-wolf-lcol">'):_ta] + _lcol[_tb:-len('</div>')]
_sk = h.find('<div class="sheet-corporeal sheet-skills">'); assert _sk > 0
_sa, _sb = _div_span(h, _sk)
h = h[:_sb - 6] + '<div class="sheet-game-line sheet-werewolf2 sheet-skills-renown">' + _ren + '</div>' + h[_sb - 6:]
_g = h.find('<div class="sheet-grow">'); _f = h.find('<div class="sheet-flex">', _g); _fa, _fb = _div_span(h, _f)
_kids = []; _k = _fa + len('<div class="sheet-flex">')
while True:
    _n = h.find('<div', _k)
    if _n < 0 or _n >= _fb - 6: break
    _ka, _kb = _div_span(h, _n); _kids.append((_ka, _kb)); _k = _kb
_last = _kids[-1]
h = h[:_last[1] - 6] + '<div class="sheet-game-line sheet-werewolf2 sheet-wolf-rpane">' + _rcol + _ts + '</div>' + h[_last[1] - 6:]
print('wolf moved: renown->skills, kuruth+touchstones->right pane', len(_kids))
# r6: Weapons get their own middle tab; Armor goes to the top of the Gear tab (removed from Main bottom)
_pc = h.find('<div class="sheet-p1-combat">'); assert _pc > 0
_pa, _pb = _div_span(h, _pc); _comb = h[_pa:_pb]; h = h[:_pa] + h[_pb:]
_w = _comb.find('<div class="sheet-p1-weapons">'); _wa, _wb = _div_span(_comb, _w); _weap = _comb[_wa:_wb]
_armor = _comb[len('<div class="sheet-p1-combat">'):_wa] + _comb[_wb:-6]
_mg = h.find('<div class="sheet-midpane sheet-mp-gear"><div class="sheet-leon-page sheet-leon-pane">'); assert _mg > 0
_ins = _mg + len('<div class="sheet-midpane sheet-mp-gear"><div class="sheet-leon-page sheet-leon-pane">')
h = h[:_ins] + '<div class="sheet-gear-armor">' + _armor + '</div>' + h[_ins:]
h = h[:_mg] + '<div class="sheet-midpane sheet-mp-weapons"><div class="sheet-leon-page sheet-leon-pane">' + _weap + '</div></div>\n' + h[_mg:]

# r7: Kuruth Triggers + Death Rage rolls get a Werewolf-only middle tab (right pane keeps the Touchstones)
_kr = h.find('<div class="sheet-wolf-rcol">'); assert _kr > 0
_ka, _kb = _div_span(h, _kr); _kcol = h[_ka:_kb]; h = h[:_ka] + h[_kb:]
_tiers = re.findall(r'<label><span data-i18n="(passive|common|specific)">(.*?)</span>(<textarea[^>]*></textarea>)</label>', _kcol, re.S)
assert len(_tiers) == 3, _tiers
_rage = re.findall(r'<button type="roll"[^>]*name="roll_(?:wasuim|basuim)"[^>]*>.*?</button>', h, re.S)
assert len(_rage) == 1
_tip = {'passive': 'Passive triggers: resist with Wasu-Im', 'common': 'Common triggers', 'specific': 'Specific triggers: apply at every Harmony except 5'}
_ktab = ('<div class="sheet-midpane sheet-mp-kuruth"><div class="sheet-leon-page sheet-leon-pane">'
         '<div class="sheet-subheader"><span data-i18n="kuruth-triggers">Kuruth Triggers</span></div>'
         '<div class="sheet-kuruth-rolls">' + ''.join(b.replace('sheet-quick sheet-rage', 'sheet-kuruth-roll sheet-rage') for b in _rage) + '</div>'
         '<div class="sheet-kuruth-tiers">' + ''.join(f'<label class="sheet-kuruth-tier" title="{_tip[k]}"><span data-i18n="{k}">{lbl}</span>{ta.replace(chr(39)+"rows="+chr(39), "rows=").replace(chr(34)+"2"+chr(34), chr(34)+"8"+chr(34))}</label>' for k, lbl, ta in _tiers) + '</div>'
         '</div></div>\n')
_mg = h.find('<div class="sheet-midpane sheet-mp-gear">'); h = h[:_mg] + _ktab + h[_mg:]
c += """
/* r7: Kuruth tab */
.charsheet .sheet-mp-kuruth .sheet-kuruth-tier > span { min-height: 2.6em; display: flex; align-items: flex-end; line-height: 1.2; }
.charsheet .sheet-mp-kuruth .sheet-kuruth-rolls { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin: 4px 0 8px; }
.charsheet .sheet-mp-kuruth button.sheet-kuruth-roll { border-radius: 999px !important; padding: 3px 14px !important; font-size: 13px !important; width: auto !important; height: auto !important; }
.charsheet .sheet-mp-kuruth .sheet-kuruth-tiers { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 88px), 1fr)); gap: 8px; }
.charsheet .sheet-mp-kuruth .sheet-kuruth-tier { display: flex; flex-direction: column; gap: 3px; min-width: 0; font-weight: bold; font-size: 12px; }
.charsheet .sheet-mp-kuruth .sheet-kuruth-tier textarea { width: 100% !important; min-width: 0 !important; box-sizing: border-box; min-height: 140px; resize: vertical; font-weight: normal; }
"""
print('kuruth tab built')
import formsfx as _ff
h, c, _ffmiss = _ff.apply(h, c); print('forms: TBD features', _ffmiss)
import huref as _hu
h, c = _hu.apply(h, c)
import heal as _heal
h, c = _heal.apply(h, c)
import nodtf as _nd
h = h.replace('<input type="text" name="attr_aspiration" />', '<textarea name="attr_aspiration" rows="2" class="sheet-asp-ta" title="Aspiration"></textarea>', 1)  # long sentences: wrap instead of clipping
h, c, _tt, _ndn, _ndgone, _ndsaved = _nd.apply(h, c, json.load(open(f'{R}/translation.json', encoding='utf-8')))
import no1e as _n1
h, c, _n1r, _n1t, _n1gone, _n1saved = _n1.apply(h, c, _tt)
_ndgone = _ndgone + _n1gone
print('1E removed elements', _n1r, 'retagged', _n1t, 'keys', len(_n1gone), 'bytes', _n1saved)
import configui as _cu
h, c = _cu.apply(h, c); c = c + _cu.CSS
print('DtF removed elements', _ndn, 'keys', _ndgone, 'bytes', _ndsaved)
import reroll as _rr, calcs as _calcs, splatfonts as _sf
_sfi, _sfc = _sf.css(); c = _sfi + c + '\n' + _sfc
h = _calcs.apply(h)
h, c, _nrr = _rr.apply(h, c); print('reroll buttons', _nrr)
import wpcounter as _wpc
h, c, _wpl = _wpc.apply(h, c); print('wp box refs left in JS', _wpl)
import kuruthrows as _kr
h, c = _kr.apply(h, c)
import kuruthmode as _km
h, c = _km.apply(h, c)
import notespage as _np
h, c = _np.apply(h, c)
import vamprit as _vr
h, c = _vr.apply(h, c)
import dicepool as _dp
h, c = _dp.apply(h, c)
h, c = _dp.touchstones(h, c)
import merits9 as _m9
h, c = _m9.apply(h, c)
import gear9 as _g9
h, c = _g9.apply(h, c)
import formsel as _fs
h, c = _fs.apply(h, c)
import r10 as _r10
h, c = _r10.apply(h, c)
import r10b as _r10b
h, c = _r10b.apply(h, c)
import r10c as _r10c
h, c = _r10c.apply(h, c)
import r10d as _r10d
h, c = _r10d.apply(h, c)
import r10e as _r10e
h, c = _r10e.apply(h, c)
import r10f as _r10f
h, c = _r10f.apply(h, c)
import r11 as _r11
h, c = _r11.apply(h, c)
import r12 as _r12
h, c = _r12.apply(h, c)
import vv as _vv
h, c = _vv.apply(h, c)
import r13 as _r13
h, c = _r13.apply(h, c)
import r13b as _r13b
h, c = _r13b.apply(h, c)
import r15 as _r15
h, c = _r15.apply(h, c)
import isolate as _iso
h, c, _nis = _iso.apply(h, c); print('isolation selectors', _nis)
open(f'{R}/dist/sheet.html', 'w', encoding='utf-8').write(h)
import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pdfstyle, extras as _ex
if _ab:
    _ps = pdfstyle.css(_ab, _ex.TYPE_OF)
    _imp = _ps.split('\n', 1)[0]; c = _imp + '\n' + c + '\n' + _ps.split('\n', 1)[1]
c = _iso.expand_is(c)
c = _r10.final(c)
# r14: chat cards get only the roll-template block live; put the card fonts' @font-face rules at the very top, inline with it
_ffs = [m.group(0) for m in re.finditer(r'@font-face\s*\{[^}]*\}', c)]
for _x in _ffs: c = c.replace(_x, '', 1)
_hd = re.match(r'(?:@import[^;]*;\s*)*', c).group(0)
c = _hd + '\n'.join(_ffs) + '\n' + c[len(_hd):]
# r15: Roll20 chat only honours ONE legacy Google Fonts @import (css?family=, not css2, no @font-face); custom TTF/OTF never reach chat
_GF = ['Almendra', 'Black Ops One', 'Cinzel', 'Cinzel Decorative', 'Creepster', 'Fondamento', 'IM Fell English SC', 'Metal Mania',
       'Metamorphous', 'Pirata One', 'Sorts Mill Goudy', 'Special Elite', 'UnifrakturMaguntia']
c = re.sub(r'@import[^;]*;\s*', '', c)
c = "@import url('https://fonts.googleapis.com/css?family=" + '|'.join(x.replace(' ', '+') for x in _GF) + "&display=swap');\n" + c
c = c.replace('"Chomsky", "IM Fell English SC", serif', '"Chomsky", "UnifrakturMaguntia", "IM Fell English SC", serif')
c = c.replace('"WolfsRain", "IM Fell English SC", serif', '"WolfsRain", "Metal Mania", "IM Fell English SC", serif')
c = c.replace('"WolfsRain", "Fondamento", cursive', '"WolfsRain", "Metal Mania", "Fondamento", cursive')
c = re.sub(r'/\*.*?\*/', '', c, flags=re.S)  # (86b) no comments / blank lines: pasted text matches the file line for line
c = '\n'.join(l.rstrip() for l in c.replace('\r', '').split('\n') if l.strip()) + '\n'
open(f'{R}/dist/sheet.css', 'w', encoding='utf-8').write(c)
t = json.load(open(f'{R}/translation.json', encoding='utf-8'))
for _k in _ndgone: t.pop(_k, None)
t.update({k: v for k, v in {'promethean-the-created': 'Promethean the Created', 'changing-breeds': 'Changing Breeds', 'details': 'Details'}.items() if k not in t})
keys = set(re.findall(r'data-i18n(?:-[a-z]+)?="([^"]+)"', h))
miss = sorted(k for k in keys if k not in t)
assert not miss, miss
json.dump(t, open(f'{R}/dist/translation.json', 'w', encoding='utf-8'), ensure_ascii=True, indent=2)
print('dist ok', len(h), len(c))
