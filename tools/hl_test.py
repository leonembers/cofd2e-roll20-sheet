"""Hurt Locker weapons verification in r20sim (worker emulation) + chat card mock -> shots/hl-*.png"""
import os, re, json, sys, html as H, random
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
sh = open(f'{R}/dist/sheet.html').read(); css = open(f'{R}/dist/sheet.css').read()
src = open(f'{R}/src/cards_build.py').read().split('C=[dict')[0]
src = src.replace("sh=open(os.path.join(ROOT,'sheet.html')).read(); css=open(os.path.join(ROOT,'sheet.css')).read()\n", '')
src = src.replace(re.search(r"tpl=re\.search.*\n", src).group(0), '').replace('tpl=cls(tpl)\n', '')
ns = {'__file__': f'{R}/src/cards_build.py'}; exec(compile(src, 'cb', 'exec'), ns); render = ns['render']
tpl = re.search(r'<rolltemplate class="sheet-rolltemplate-cofd-entry">(.*?)</rolltemplate>', sh, re.S).group(1)
fs = sh[sh.index('<fieldset class="repeating_weapons"'):]; sys.path.insert(0, f'{R}/tools'); import rrmac; macro = rrmac.get('attack', 'weapons')
ROWS = [dict(preset='battle_axe'), dict(preset='assault_rifle'), dict(preset='short_bow'), dict(preset='frag'), dict(preset='whip'),
        dict(preset='stun_gun_ranged'), dict(preset='gl_hedp'), dict(preset='fists'),
        dict(legacy=dict(name='Old Glock', wtype='ranged', damage='1', dtype='L', clip='17+1', range='20/40/80', tags='Concealable, 9-again, AP 1', str_req='2', wsize='1'))]
JS_ADD = """(rows)=>{const ids=[];for(const r of rows){if(r.legacy){ids.push(window.__addRow('weapons',r.legacy));}else{const id=window.__addRow('weapons',{});ids.push(id);
 const it=document.querySelector('[data-reprowid="'+id+'"]');const s=it.querySelector('select[name="attr_preset"]');s.value=r.preset;s.dispatchEvent(new Event('change',{bubbles:true}));}}
 window.__fire('sheet:opened',{});return ids}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    res = {}
    for t, w in [('hunter2', 880), ('werewolf2', 780), ('vampire2', 900)]:
        pg = b.new_page(viewport={'width': w + 20, 'height': 1600})
        pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page=1&worker=1&r20dark=1&dm=1"); pg.add_style_tag(content=f".ui-dialog{{width:{w}px !important}}")
        pg.wait_for_timeout(400)
        pg.evaluate("()=>setAttrs({mid_tab:'weapons',strength:3,dexterity:3,weaponry:2,firearms:3,athletics:2,brawl:1,size:5})"); pg.wait_for_timeout(300)
        ids = pg.evaluate(JS_ADD, ROWS); pg.wait_for_timeout(800)
        # set a few stats for realistic pools
        A = pg.evaluate("()=>window.__A"); werr = pg.evaluate("()=>window.__werr||[]")
        chk = pg.evaluate("""()=>{const c=document.querySelector('.sheet-mp-weapons');const r=c.getBoundingClientRect();const pr=c.closest('.sheet-page1').getBoundingClientRect();const bad=[];
          c.querySelectorAll('*').forEach(e=>{if(!e.offsetParent)return;const b=e.getBoundingClientRect();if(b.right>r.right+1)bad.push((e.getAttribute('name')||e.className||e.tagName).toString().slice(0,40)+':'+Math.round(b.right-r.right))});
          const heads=[...c.querySelectorAll('.repitem .sheet-entry-head')].map(h=>Math.round(h.getBoundingClientRect().height));
          return {left:r.left,right:r.right,pageL:pr.left,pageR:pr.right,bad:bad.slice(0,10),heads}}""")
        print(t, w, 'errors', werr, json.dumps(chk))
        pg.screenshot(path=f'{R}/shots/hl-{t}-{w}-collapsed.png', clip=dict(x=0, y=max(0, chk and 0), width=w + 20, height=1600), full_page=False)
        el = pg.query_selector('.sheet-mp-weapons'); el.screenshot(path=f'{R}/shots/hl-{t}-{w}-block.png')
        if t == 'hunter2':
            pg.evaluate("()=>document.querySelectorAll('.repitem input.sheet-entry-toggle').forEach((e,i)=>{if(i===1||i===3){e.checked=true}})")
            pg.wait_for_timeout(200); el.screenshot(path=f'{R}/shots/hl-expanded-dark.png')
            chk2 = pg.evaluate("""()=>{const c=document.querySelector('.sheet-mp-weapons');const r=c.getBoundingClientRect();const bad=[];c.querySelectorAll('*').forEach(e=>{if(!e.offsetParent)return;const b=e.getBoundingClientRect();if(b.right>r.right+1)bad.push((e.getAttribute('name')||e.className).toString().slice(0,40))});return bad}""")
            print('expanded overflow', chk2)
            res = dict(A=A, ids=ids)
        pg.close()
    # light mode screenshot
    pg = b.new_page(viewport={'width': 900, 'height': 1600}); pg.goto(f"file://{R}/dist/r20sim.html?type=mortal2&page=1&worker=1&r20dark=0&dm=0"); pg.wait_for_timeout(300)
    pg.evaluate("()=>setAttrs({mid_tab:'weapons'})"); pg.evaluate(JS_ADD, ROWS[:4]); pg.wait_for_timeout(600)
    pg.evaluate("()=>document.querySelectorAll('.repitem input.sheet-entry-toggle').forEach((e,i)=>{if(i===3)e.checked=true})")
    pg.query_selector('.sheet-mp-weapons').screenshot(path=f'{R}/shots/hl-mortal-light.png'); pg.close()
    # ---- cards ----
    A = res['A']
    def resolve(s, pre):
        for _ in range(8):
            s2 = re.sub(r'@\{([^}]+)\}', lambda m: A.get(pre + m.group(1).lower(), A.get(m.group(1).lower(), '0' if m.group(1) != 'modifiermacro' else 'Modifier')), s)
            if s2 == s: break
            s = s2
        return s
    def queries(s):  # take default (first option value / default text)
        for _ in range(6):
            s2 = re.sub(r'\?\{([^{}|]*)\|([^{}]*)\}', lambda m: (m.group(2).split('|')[-1].split(',')[-1] if 'Range' in m.group(1) else (m.group(2).split('|')[1].split(',')[-1] if 'Fire mode' in m.group(1) and '|' in m.group(2) else m.group(2).split('|')[0].split(',')[-1])), s)
            s2 = re.sub(r'\?\{([^{}|]*)\}', '0', s2)
            if s2 == s: break
            s = s2
        return s
    msgs = {'dark': '', 'light': ''}
    for id in res['ids']:
        pre = f'repeating_weapons_{id}_'.lower()
        m = queries(resolve(macro, pre))
        d = dict(re.findall(r'\{\{([^=}]+)=(.*?)\}\}(?=\s|$|\{\{)', m))
        rollexpr = re.search(r'\{\{roll=\[\[(.*?)\]\]\}\}', m)
        d = {k: v for k, v in d.items() if v.strip()}
        d.pop('roll', None)
        d['f_force'] = re.sub(r'\[\[\{(\d+)d10.*?\]\]', lambda mm: str(random.randint(0, int(mm.group(1)) // 2 + 1)), d.get('f_force', '')) or None
        if not d['f_force']: d.pop('f_force')
        d.update(charname='Vince Knight', gl_hunter=1, roll=(random.randint(0, 4), False))
        print(d.get('name'), '|', rollexpr.group(1)[:160] if rollexpr else 'NO ROLL', '| flags', [k for k in d if k in ('9again', '8again', 'chance')])
        for mode in msgs:
            body = render(tpl, d)
            body = re.sub(r'class="([^"]+)"', lambda mm: 'class="' + ' '.join(c if c.startswith('sheet-') else 'sheet-' + c for c in mm.group(1).split()) + '"', body)
            msgs[mode] += f'<div class="message"><div class="sheet-rolltemplate-cofd-entry{" sheet-rolltemplate-darkmode" if mode == "dark" else ""}">{body}</div></div>'
    for mode, ms in msgs.items():
        bg = '#1e1e22' if mode == 'dark' else '#fff'
        open(f'{R}/shots/hl-chat-{mode}.html', 'w').write(f'<!doctype html><meta charset=utf-8><style>body{{margin:0;background:{bg};font-family:Arial;font-size:13px}}#c{{width:290px;padding:6px;display:grid;gap:6px}}.inlinerollresult{{border:2px solid #fef68e;background:#fef68e;color:#000;padding:0 3px;font-weight:bold}}</style><style>{css}</style><div id="c">{ms}</div>')
        pg = b.new_page(viewport={'width': 900, 'height': 600}, device_scale_factor=2)
        pg.goto(f'file://{R}/shots/hl-chat-{mode}.html')
        pg.add_style_tag(content='#c{grid-template-columns:repeat(3,290px)}'); pg.screenshot(path=f'{R}/shots/hl-cards-{mode}.png', full_page=True); pg.close()
    json.dump({k: v for k, v in A.items() if k.startswith('repeating_weapons')}, open(f'{R}/shots/hl-attrs.json', 'w'), indent=0)
    b.close()

# ---- Dark Eras toggles (Config): on/off visibility of the era skill swaps ----
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox']); pg = b.new_page()
    pg.goto(f"file://{R}/dist/r20sim.html?type=mortal2&page=1&worker=1"); pg.wait_for_timeout(1200)
    vis = "k=>[...document.querySelectorAll('.sheet-skills .sheet-'+k)].filter(e=>e.offsetParent).map(e=>e.textContent.trim().split(/\\s+/)[0]).join(',')"
    for k in ['archery', 'ride', 'enigmas']:
        st = []
        for step in range(3):
            st.append(f"{pg.evaluate('k=>window.__A[k+\"_era\"]||\"0\"', k)}: is=[{pg.evaluate(vis, 'is-'+k+'-era')}] not=[{pg.evaluate(vis, 'not-'+k+'-era')}]")
            pg.evaluate('k=>window.__fire("clicked:"+k+"_era",{})', k); pg.wait_for_timeout(500)
        print('DARK ERA', k, ' -> '.join(st))
    b.close()
