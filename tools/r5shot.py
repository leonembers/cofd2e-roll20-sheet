"""Round-5 shots: armor, gifts widths, vitae counter, rage buttons."""
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'; S=f'{R}/shots/'
def url(t): return f"file://{R}/dist/r20sim.html?type={t}&page=1&worker=1&r20dark=1&dm=1"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=b.new_page(viewport={'width':900,'height':1000})
    pg.goto(url('werewolf2')); pg.wait_for_timeout(700)
    pg.evaluate("()=>setAttrs({armor_general0:'3',armor_ballistic0:'3',armor_mig_v1:'',armor_name0:'Kevlar weave + graphene plates',armor_strength0:'2',armor_defense0:'-1',armor_speed0:'-1',potency:'2',vitae:'9',resolve:'3',composure:'3'})")
    pg.evaluate("()=>__fire('sheet:opened',{})"); pg.wait_for_timeout(1200)
    A=pg.evaluate("()=>__A"); print('armor rows',[k for k in A if k.startswith('repeating_armor_')][:6]); print('vitae',A.get('vitae'),A.get('vitae_max'),A.get('vitae_counter'),'werr',pg.evaluate("()=>window.__werr||[]"))
    for n in ('vitae_dec','vitae_inc','vitae_inc','vitae_inc','vitae_inc'): pg.evaluate("n=>__fire('clicked:'+n,{})",n); pg.wait_for_timeout(200)
    print('after -1 +4 (clamp 12):',pg.evaluate("()=>__A.vitae"))
    pg.evaluate("()=>__addRow('armor',{ar_name:'Riot shield',ar_general:'1',ar_ballistic:'0',ar_def:'-1',ar_equipped:'0'})"); pg.wait_for_timeout(800)
    A=pg.evaluate("()=>__A"); print('derived',{k:A.get(k) for k in ('armor_general0','armor_ballistic0','armor_defense0','general_armor','defense_penalty')})
    el=pg.locator('.sheet-entry-section.sheet-armor').first; el.scroll_into_view_if_needed(); el.screenshot(path=S+'r5-armor-collapsed.png')
    pg.locator('.sheet-entry-section.sheet-armor .sheet-repitem, .sheet-entry-section.sheet-armor .repitem').first.locator('input[type=checkbox]').first.check(force=True); pg.wait_for_timeout(400)
    el.screenshot(path=S+'r5-armor-expanded.png')
    pg.locator('.sheet-res-ctr').first.screenshot(path=S+'r5-vitae-counter.png')
    pg.locator('button[name="roll_wasuim"]').first.locator('xpath=..').screenshot(path=S+'r5-rage-buttons.png')
    for r in [dict(name='Sense Weakness',rating='1',gtype='Moon',show='0'),dict(name="Father Wolf's Speed, the Long and Winding Name of the Gift of Evasion",rating='3',gtype='Shadow',show='0'),dict(name='Ox',rating='2',gtype='Wolf',show='0')]:
        pg.evaluate("a=>__addRow('gifts',a)",r)
    pg.locator('button[name="act_midtab_powers"]').first.click(); pg.wait_for_timeout(700)
    w=pg.evaluate("()=>[...document.querySelectorAll('.sheet-gifts .sheet-entry-head')].filter(e=>e.offsetParent).map(e=>Math.round(e.firstElementChild.getBoundingClientRect().width))"); print('gift name col widths',w)
    pg.locator('.sheet-entry-section.sheet-gifts').first.screenshot(path=S+'r5-gifts-mixed.png')
    b.close()
