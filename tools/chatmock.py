"""Render dist/ roll templates inside a mock Roll20 chat log (light + dark) -> shots/card-*.png.
Uses dist/sheet.css only (what Roll20 receives) and the actual button macros parsed from dist/sheet.html."""
import re, os, sys, html as H
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sh = open(f'{R}/dist/sheet.html').read(); css = open(f'{R}/dist/sheet.css').read()
tpl = re.search(r'<rolltemplate class="sheet-rolltemplate-cofd-entry">(.*?)</rolltemplate>', sh, re.S).group(1)
import importlib.util
spec = importlib.util.spec_from_file_location('cb', f'{R}/src/cards_build.py')
src = open(f'{R}/src/cards_build.py').read().split('C=[dict')[0]
ns = {}; exec(src.replace("sh=open(os.path.join(ROOT,'sheet.html')).read(); css=open(os.path.join(ROOT,'sheet.css')).read()", "sh=css=''").replace("tpl=re.search(", "tpl='' #").replace('tpl=cls(tpl)', ''), {'__file__': f'{R}/src/cards_build.py'} | ns, ns) if False else None
exec(compile(src.replace("sh=open(os.path.join(ROOT,'sheet.html')).read(); css=open(os.path.join(ROOT,'sheet.css')).read()\n", '').replace(re.search(r"tpl=re\.search.*\n", src).group(0), '').replace('tpl=cls(tpl)\n', ''), 'cb', 'exec'), ns := {'__file__': f'{R}/src/cards_build.py'})
render = ns['render']
# Live Roll20: roll templates use the LEGACY CSS sanitizer even in CSE mode; one trigger anywhere in
# sheet.css => "Potential CSS security violation; character sheet template styling thrown out" and the
# chat cards get NO sheet CSS at all. Emulate that so the mock fails the same way live does.
def legacy_template_css(c):
    hits = []
    for pat, why in [(r'\.webp', '.webp image'), (r'webp', "'webp' substring"), (r'\\0*77\b|\\0*57\b', 'escaped w (decoded by sanitizer)'), (r'\*\*', 'double asterisk'), (r'eval', "'eval' substring"), (r'overscroll-behavior', 'overscroll-behavior'),
                     (r'@charset', '@charset'), (r'url\([^)]*;', "';' inside url() (statement split breaks quote balance)"), (r'\\', 'backslash escape'), (r'parent', "'parent' substring")]:
        m = re.search(pat, c, re.I)
        if m: hits.append(f'{why}: ...{c[max(0, m.start()-50):m.end()+10]!r}')
    if any(ord(ch) > 127 for ch in c): hits.append('raw non-ASCII char')
    for m in re.finditer(r'\\([0-9a-fA-F]{1,6})', c):
        if int(m.group(1), 16) > 0xff: hits.append(f'high-unicode escape \\{m.group(1)}'); break
    return hits
def template_scope(sh, c):
    """Roll20 applies to chat only selectors that START with .sheet-rolltemplate-NAME (never under .charsheet);
    every &{template:X} used in buttons or worker startRoll must have <rolltemplate class="sheet-rolltemplate-X"> and CSS."""
    bad = []
    defined = set(re.findall(r'<rolltemplate class="sheet-rolltemplate-([a-z0-9-]+)"', sh))
    used = set(re.findall(r'&\{template:([a-z0-9-]+)\}', sh))
    for t in used - defined: bad.append(f'template used but not defined: {t}')
    for t in used:
        if not re.search(r'(^|[},\s])\.sheet-rolltemplate-' + re.escape(t) + r'[\s.:\[,{]', c): bad.append(f'no CSS for template {t}')
    for m in re.finditer(r'([^{}]*rolltemplate[^{}]*)\{', re.sub(r'/\*.*?\*/', '', c, flags=re.S)):
        for sel in m.group(1).split(','):
            sel = sel.strip()
            if 'rolltemplate-' in sel and not sel.startswith('.sheet-rolltemplate-'): bad.append(f'mis-scoped template selector: {sel[:90]}')
    return sorted(set(bad)), sorted(used), sorted(defined)
_tb, _used, _def = template_scope(sh, css)
print('templates used', _used, 'defined', _def)
if _tb: print('TEMPLATE SCOPE FAIL:', *_tb, sep='\n  ')
_hits = legacy_template_css(css)
if _hits:
    print('LIVE ROLL20 WOULD DROP ALL ROLL-TEMPLATE CSS:', *_hits, sep='\n  ')
    css = ''
def macro(name):
    import sys; sys.path.insert(0, R + '/tools'); import rrmac; v = rrmac.get(name)
    assert '{template:cofd-entry}' in v, name
    return dict(re.findall(r'\{\{([^=}]+)=(.*?)\}\}(?=\s|$|\{\{|@)', v))
def card(name, roll, over):
    f = macro(name); d = {k: v for k, v in f.items() if not k.startswith('gl_')}
    d.update({'charname': 'Michael Remington', 'gl_werewolf': 1, 'roll': roll, **over})
    for k in ('f_mod', 'f_wounds', 'f_init'):
        if k in d: d[k] = over.get(k, '0')
    if 'f_init' in f: d.pop('roll'); return d
    return d
CARDS = [('roll_wasuim', (3, False), dict(f_mod='0', f_wounds='0')), ('roll_wasuim', (0, False), dict(f_mod='0', f_wounds='0')),
         ('roll_sheet', (5, False), dict(name='Wits (3) + Occult (2)', f_pool='5 dice', f_mod='0', f_wounds='0')),
         ('roll_perception', (0, False), dict(f_pool='Wits 3 + Composure 3 + Form 1 + Wounds 0', f_mod='Modifier 0')),
         ('roll_initiative', (0, False), dict(f_pool='1d10 + Dexterity 3 + Composure 3 + Fast Reflexes 0 + Penalty 0', f_init='13')),
         ('roll_simple', (1, False), dict(f_pool='4 dice')),
         ('roll_frenzy', (0, True), dict(chance=1, f_mod='0', f_wounds='0', gl_werewolf=0, gl_vampire=1, charname='Marcus Vale'))]
def page(dark):
    msgs = ''
    for n, r, o in CARDS:
        d = card(n, r, o)
        if not d.get('roll'): d.pop('roll', None)
        body = render(tpl, {**d, 'roll': d.get('roll', (0, False))}) if 'roll' in d else render(re.sub(r'\{\{#roll\}\}.*?\{\{/roll\}\}', '', tpl, flags=re.S), d)
        body = re.sub(r'class="([^"]+)"', lambda m: 'class="' + ' '.join(c if c.startswith('sheet-') else 'sheet-' + c for c in m.group(1).split()) + '"', body)
        body = body.replace('<td>13</td>', '<td><span class="inlinerollresult">13</span></td>')
        msgs += f'<div class="message rollresult you"><div class="spacer"></div><div class="avatar"></div><span class="by">Storyteller (GM):</span><div class="sheet-rolltemplate-cofd-entry{" sheet-rolltemplate-darkmode" if dark else ""}">{body}</div></div>'
    bg, fg = ('#1e1e22', '#ddd') if dark else ('#fff', '#000')
    return f'''<!doctype html><meta charset=utf-8><style>body{{margin:0;background:{bg};color:{fg};font-family:"Helvetica Neue",Arial,sans-serif;font-size:13px}}
#textchat{{width:290px;padding:6px}} .message{{position:relative;padding:4px 4px 6px 45px;border-bottom:1px solid {"#333" if dark else "#eee"}}} .avatar{{position:absolute;left:4px;top:4px;width:30px;height:30px;background:#8a3;border-radius:3px}} .by{{font-weight:bold;display:block;margin-bottom:3px}}
.inlinerollresult{{display:inline-block;min-width:1.5em;text-align:center;border:2px solid #fef68e;background:#fef68e;color:#000;padding:0 3px;font-weight:bold}}
</style><style>{css}</style><div id="textchat"><div class="content">{msgs}</div></div>'''
os.makedirs(f'{R}/shots', exist_ok=True)
for dark in (False, True):
    open(f'{R}/shots/chatmock-{"dark" if dark else "light"}.html', 'w').write(page(dark))
_dk = page(True)
assert _dk.count('Resisted: you keep control') == 1 and _dk.count('Basu-Im! Hard Rage') == 1, 'Death Rage card outcomes'
assert 'roll_basuim' not in open(f'{R}/dist/sheet.html').read(), 'standalone Basu-Im button'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg = b.new_page(viewport={'width': 310, 'height': 400}, device_scale_factor=2)
    for m in ('light', 'dark'):
        pg.goto(f'file://{R}/shots/chatmock-{m}.html'); pg.screenshot(path=f'{R}/shots/card-chat-{m}.png', full_page=True)
    b.close()
print('ok')
