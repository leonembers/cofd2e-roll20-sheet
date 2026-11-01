"""Merit categories / Style maneuvers / mid tabs / config / chevron alignment checks -> shots/merit-*.png"""
import os, json
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROWS = [dict(merit_name='Relentless Assault', merit='4'), dict(merit_name='Fenris Style', merit='3', show='1',
        mv1_name='Bite and Hold', mv1_effect='Grapple with jaws; +1 to overpower while holding.', mv2_name='Shake the Prey', mv2_effect='Damage on a held foe adds +1L.',
        mv3_name='Tear Free', mv3_effect='Break a grapple reflexively once per turn.', mv4_name='Hamstring', mv4_effect='Knockdown + Arm Wrack tilt.'),
        dict(merit_name='Iron Stamina', merit='3'), dict(merit_name='Resources', merit='3'), dict(merit_name='Language', merit='2'),
        dict(merit_name='Totem', merit='2'), dict(merit_name='Defensive Combat', merit='1'), dict(merit_name='Fleet of Foot', merit='2', mcat='Physical')]
CHEV = """()=>{const out=[];document.querySelectorAll('input.sheet-entry-toggle').forEach(cb=>{if(!cb.offsetParent)return;const hd=cb.nextElementSibling;if(!hd)return;
 const r=cb.getBoundingClientRect();const b=cb.parentElement.getBoundingClientRect();const s=getComputedStyle(hd,'::before');if(s.content==='none')return;
 const l=parseFloat(s.left),t=parseFloat(s.top),w=parseFloat(s.width)+parseFloat(s.borderRightWidth),hh=parseFloat(s.height)+parseFloat(s.borderBottomWidth);
 const cx=b.left+parseFloat(getComputedStyle(cb.parentElement).borderLeftWidth||0)+l+w/2, cy=b.top+parseFloat(getComputedStyle(cb.parentElement).borderTopWidth||0)+t+hh/2;
 out.push({n:cb.getAttribute('name'),dx:+(r.left+r.width/2-cx).toFixed(1),dy:+(r.top+r.height/2-cy).toFixed(1),w:r.width,h:r.height})});return out}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 900, 'height': 1500})
    pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page=1&worker=1&r20dark=1&dm=1"); pg.add_style_tag(content=".ui-dialog{width:880px !important}")
    pg.wait_for_timeout(400)
    ids = pg.evaluate("(rows)=>rows.map(r=>window.__addRow('merits',r))", ROWS)
    pg.evaluate("()=>window.__fire('sheet:opened',{})"); pg.wait_for_timeout(900)
    pg.evaluate("()=>setAttrs({strength:3,dexterity:3,wits:3,composure:3,athletics:2,brawl:4,stamina:3})"); pg.wait_for_timeout(500)
    A = pg.evaluate("()=>window.__A")
    print('categories', {A.get(f'repeating_merits_{i}_merit_name'.lower()): A.get(f'repeating_merits_{i}_mcat'.lower()) for i in ids})
    print('mv_on', [A.get(f'repeating_merits_{ids[1]}_mv{n}_on'.lower()) for n in range(1, 6)])
    print('skills width', pg.evaluate("()=>document.querySelector('.sheet-skills').getBoundingClientRect().width"))
    print('werr', pg.evaluate("()=>window.__werr||[]"))
    print('chevrons', json.dumps(pg.evaluate(CHEV)))
    mid = pg.locator('.sheet-midtabs').first
    def shot(name, loc=None, pad=None):
        if loc is None: pg.screenshot(path=f'{R}/shots/{name}.png', full_page=False); return
        bb = loc.bounding_box(); x, y = max(0, bb['x'] - 8), max(0, bb['y'] - 8)
        pg.screenshot(path=f'{R}/shots/{name}.png', clip=dict(x=x, y=y, width=min(900 - x, bb['width'] + 16), height=bb['height'] + 16))
    pg.locator('.sheet-skills').first.scroll_into_view_if_needed()
    shot('merit-skills-narrow', pg.locator('.sheet-page1 .sheet-flex:has(> .sheet-skills)').first)
    shot('merit-midtabs-merits', pg.locator('.sheet-midtabs').first.locator('xpath=..'))
    ri = pg.locator('.repitem').filter(has=pg.locator('input.sheet-mstyle-flag[value="1"]')).nth(1)
    shot('merit-style-expanded', ri)
    shot('merit-style-maneuvers', ri.locator('.sheet-style-block'))
    shot('merit-badges', pg.locator('.repcontainer[data-groupname="repeating_merits"]').first)
    pg.locator('select[name="attr_merit_filter"]').first.select_option('style'); pg.wait_for_timeout(300)
    shot('merit-filter-style', pg.locator('.sheet-midtabs').first.locator('xpath=..'))
    pg.locator('select[name="attr_merit_filter"]').first.select_option('all'); pg.wait_for_timeout(200)
    for t in ['powers', 'gear', 'notes']:
        pg.locator(f'button[name="act_midtab_{t}"]').first.click(); pg.wait_for_timeout(400)
        print('mid_tab', pg.evaluate("()=>window.__A.mid_tab"), 'visible panes', pg.evaluate("()=>[...document.querySelectorAll('.sheet-midpane')].filter(e=>e.offsetParent).map(e=>e.className)"))
        shot(f'merit-tab-{t}', pg.locator('.sheet-midtabs').first.locator('xpath=..'))
    pg.locator('button[name="act_midtab_powers"]').first.click(); pg.wait_for_timeout(300)
    shot('merit-main-full'); pg.screenshot(path=f'{R}/shots/merit-main-fullpage.png', full_page=True)
    pg.evaluate("()=>window.__addRow('merits',{merit_name:'Giant',merit:'3'})"); pg.evaluate("()=>window.__addRow('merits',{merit_name:'Hardy',merit:'2'})")
    pg.evaluate("()=>setAttrs({merit_auto:'1', fast_reflexes:'1'}); __fire('change:merit_auto',{})"); pg.wait_for_timeout(900)
    A = pg.evaluate("()=>window.__A")
    print('fx', {k: A.get(k) for k in ['giant','small_framed','size','health','merit_fx_keys','fleet_of_foot', 'fast_reflexes', 'iron_stamina', 'defensive_combat', 'defense_select', 'merit_fx_summary', 'speed']})
    # migration of old base-sheet lists
    pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page=1&worker=1&r20dark=1&dm=1"); pg.wait_for_timeout(400)
    pg.evaluate("""()=>{__addRow('power-list',{'power-list':'Shadow Gaze'});__addRow('ability2',{ability2_name:'War Howl',ability2:'1'});__addRow('power2-list',{'power2-list':'Sense Weakness'});
      __addRow('power3',{power3_name:'Sacred Hunt'});__addRow('abilities',{ability_name:'Purity',ability:'2'});__addRow('abilities',{ability_name:'Odd Thing',ability:'1'});__addRow('gifts',{name:'War Howl',rating:'1'});
      setAttrs({dedupe_v1_werewolf2:'0'});__fire('sheet:opened',{})}"""); pg.wait_for_timeout(1200)
    A = pg.evaluate("()=>window.__A")
    print('migrated', {k: v for k, v in A.items() if (k.startswith('repeating_gifts') or k.startswith('repeating_writes')) and k.split('_')[-1] in ('name', 'gtype', 'rating', 'notes')}, {k: A.get(k) for k in ['renown_purity', 'dedupe_v1_werewolf2', 'dedupe_v1_note', 'power-list']})
    pg.evaluate("()=>__fire('sheet:opened',{})"); pg.wait_for_timeout(800)
    print('rerun gifts rows', len(window_ids := pg.evaluate("()=>__SEC.gifts.ids")))
    pg.locator('button[name="act_midtab_powers"]').first.click(); pg.wait_for_timeout(300)
    shot('merit-tab-gifts-migrated', pg.locator('.sheet-midtabs').first.locator('xpath=..'))
    pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page=settings&worker=1&r20dark=1&dm=1"); pg.add_style_tag(content=".ui-dialog{width:880px !important}"); pg.wait_for_timeout(500)
    pg.screenshot(path=f'{R}/shots/merit-config-tab.png', full_page=True)
    b.close()
