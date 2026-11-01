"""Power rows (Pathfinder-feat style) + compact roller/portrait check & dark screenshots."""
from playwright.sync_api import sync_playwright
import json
R = '/workspace/cofd/roll20'; S = f'{R}/shots/'
def url(t, w=1): return f"file://{R}/dist/r20sim.html?type={t}&page=1&worker={w}&r20dark=1&dm=1"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = b.new_page(viewport={'width': 900, 'height': 1000})
    def fill(sec, rows):
        for r in rows: pg.evaluate("([s,a])=>window.__addRow(s,a)", [sec, r])
        pg.wait_for_timeout(300)
    def sect(cls): return pg.locator(f'.sheet-entry-section.sheet-{cls}').first
    # ---- Werewolf
    pg.goto(url('werewolf2')); pg.wait_for_timeout(600)
    pg.evaluate("()=>setAttrs({wits:3,composure:3,presence:4,intimidation:3,resolve:2,occult:0,vitae:7,willpower:5,stamina:3,manipulation:2,survival:2})")
    fill('gifts', [dict(name="Father Wolf's Speed (Gift of Evasion)", gtype='Shadow', rating='2', short_desc='Rattle a foe with presence alone', pp_attr='presence', pp_skill='intimidation', pp_mod='1', cost_wp='1', description='Long effect text only shown when expanded.', show='0'),
                   dict(name='Partial Change (Dalu Form Mastery of the Wolf-Blooded)', gtype='Moon', rating='4', short_desc='Very long short description that keeps going and going past the row width', pp_attr='wits', pp_skill='occult', cost_pw='2', cost_wp='1', cost_auto='1', show='0'),
                   dict(name='Gift C', rating='1', short_desc='No pool, no cost', show='0')])
    fill('merits', [dict(merit_name='Professional Training (Investigation)', merit='2', mcat='Mental', short_desc='+2 to detect ambushes', show='0'),
                    dict(merit_name='Fighting Style: Relentless Assault', merit='2', mcat='Mental', short_desc='Substitute Resolve when contesting', pp_attr='resolve', pp_skill='_dots', cost_wp='1', show='0'),
                    dict(merit_name='Fast-Talking', merit='3', mcat='Social', show='0'),
                    dict(merit_name='Interdisciplinary Specialty', merit='1', mcat='Mental', short_desc='Extra specialty bonus', show='0'),
                    dict(merit_name='Defensive Combat (Weaponry)', merit='3', mcat='Social', short_desc='Comfortable middle class', show='0')])
    fill('writes', [dict(name='Rite A', rating='2', short_desc='Pack ritual of binding', pp_attr='stamina', pp_skill='survival', cost_pw='1', show='0'),
                    dict(name='Rite B', rating='1', short_desc='Short one', show='0')])
    pg.evaluate("()=>{__fire('change:sheettype',{})}"); pg.wait_for_timeout(1200)
    def clipcheck(tag):
        r = pg.evaluate('''()=>[...document.querySelectorAll('.sheet-entry-head button.sheet-entry-post, .sheet-entry-head .sheet-entry-name')].filter(e=>e.offsetParent&&(e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+1)).map(e=>e.textContent.trim().slice(0,40))''')
        print('nameclip', tag, r)
    A = pg.evaluate("()=>window.__A")
    print('pools', {k: v for k, v in A.items() if k.endswith('_pool') or k.endswith('_cost_disp')})
    # roll-and-pay on Gift B
    gid = [k.split('_')[2] for k, v in A.items() if k.startswith('repeating_gifts_') and v == 'Partial Change (Dalu Form Mastery of the Wolf-Blooded)'][0]
    pg.evaluate("(id)=>__fire('clicked:repeating_gifts:proll',{sourceAttribute:`repeating_gifts_${id}_proll`, triggerName:`clicked:repeating_gifts_${id}_proll`})", gid); pg.wait_for_timeout(600)
    A = pg.evaluate("()=>window.__A")
    print('after pay vitae', A.get('vitae'), 'wp boxes', [A.get(f'willpower_box{i}') for i in range(1, 6)], 'werr', pg.evaluate("()=>window.__werr||[]"))
    pg.locator('button[name="act_midtab_powers"]').first.click(); pg.wait_for_timeout(400)
    pg.evaluate("()=>{setAttrs({auspice:'Cahalith',renown_glory:'2'});__fire('change:auspice',{newValue:'Cahalith'})}"); pg.wait_for_timeout(600)
    print('moon_renown', pg.evaluate("()=>__A.moon_renown"))
    pg.locator('.sheet-mgx').first.screenshot(path=S + 'pw-wolf-moongift-cahalith.png')
    pg.evaluate("()=>{setAttrs({auspice:'Irraka',renown_cunning:'4'});__fire('change:auspice',{newValue:'Irraka'})}"); pg.wait_for_timeout(600)
    print('moon_renown irraka', pg.evaluate("()=>__A.moon_renown"))
    pg.locator('.sheet-mgx').first.screenshot(path=S + 'pw-wolf-moongift-irraka.png')
    clipcheck('wolf'); sect('gifts').screenshot(path=S + 'pw-wolf-gifts.png'); sect('writes').screenshot(path=S + 'pw-wolf-rites.png')
    # expand one gift
    pg.evaluate("(id)=>setAttrs({[`repeating_gifts_${id}_show`]:'1'})", gid); pg.wait_for_timeout(300)
    sect('gifts').screenshot(path=S + 'pw-wolf-gift-expanded.png')
    pg.locator('button[name="act_midtab_merits"]').first.click(); pg.wait_for_timeout(400)
    clipcheck('merits'); sect('merits').screenshot(path=S + 'pw-wolf-merits.png')
    # roller: fit longest string
    pg.evaluate("()=>setAttrs({rolldisplay:'Empathy 10 + Enigmas 10 + Stamina 10 = 30'})"); pg.wait_for_timeout(300)
    print('pooltxt', pg.evaluate("()=>{const e=document.querySelector('input.sheet-pooltxt');return [e.scrollWidth,e.clientWidth,e.getBoundingClientRect().width]}"))
    pg.locator('.sheet-rollbar').first.screenshot(path=S + 'pw-roller-placeholder.png')
    pg.evaluate("()=>setAttrs({portrait_url:'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@main/logo/werewolf2.png'})"); pg.evaluate("()=>__fire('change:portrait_url',{})"); pg.wait_for_timeout(1500)
    print('portrait_src', pg.evaluate("()=>__A.portrait_src"))
    pg.locator('.sheet-rollbar').first.screenshot(path=S + 'pw-roller-portrait.png')
    pg.screenshot(path=S + 'pw-wolf-main.png', full_page=False)
    # ---- Vampire
    pg.goto(url('vampire2')); pg.wait_for_timeout(600)
    pg.evaluate("()=>setAttrs({presence:3,intimidation:2,vitae:9})")
    fill('disciplines', [dict(name='Theban Sorcery: Blood Price of the Unholy Sacrament', rating='3', inclan='1', short_desc='Fear and command', pp_attr='presence', pp_skill='intimidation', cost_pw='1', show='0'),
                         dict(name='Discipline B', rating='2', short_desc='Physical boost', cost_pw='1', show='0'),
                         dict(name='Discipline C', rating='1', short_desc='Sense the unseen', pp_attr='wits', pp_skill='_dots', show='0')])
    pg.evaluate("()=>__fire('change:sheettype',{})"); pg.wait_for_timeout(1000)
    pg.locator('button[name="act_midtab_powers"]').first.click(); pg.wait_for_timeout(400)
    clipcheck('vamp'); sect('disciplines').screenshot(path=S + 'pw-vamp-disciplines.png')
    # ---- Mage
    pg.goto(url('mage2')); pg.wait_for_timeout(600)
    pg.evaluate("()=>setAttrs({intelligence:3,occult:3})")
    fill('rotes', [dict(name='Rote A', arcanum='Forces', short_desc='Bend light around you', pp_attr='intelligence', pp_skill='occult', pp_mod='2', cost_pw='1', show='0'),
                   dict(name='Rote B', short_desc='Read the threads', cost_wp='1', show='0')])
    pg.evaluate("()=>__fire('change:sheettype',{})"); pg.wait_for_timeout(1000)
    pg.locator('button[name="act_midtab_powers"]').first.click(); pg.wait_for_timeout(400)
    sect('rotes').screenshot(path=S + 'pw-mage-rotes.png')
    print('mage', {k: v for k, v in pg.evaluate("()=>window.__A").items() if k.endswith('_pool') or k.endswith('_cost_disp')})
    # overlap audit of power rows at 3 widths
    for w in (700, 900, 1200):
        pg.set_viewport_size({'width': w, 'height': 1000}); pg.wait_for_timeout(300)
        bad = pg.evaluate("""()=>{const out=[];document.querySelectorAll('.sheet-entry-section.sheet-pw .sheet-entry-head').forEach(h=>{if(!h.offsetParent)return;const hb=h.getBoundingClientRect();
          const seen=[];[...h.children].filter(c=>c.offsetParent&&getComputedStyle(c).display!=='none'&&getComputedStyle(c).visibility!=='hidden').forEach(c=>{const r=c.getBoundingClientRect();if(r.width===0)return;
          if(r.right>hb.right+1||r.left<hb.left-1)out.push(['spill',c.className]);seen.forEach(q=>{if(r.left<q.r.right-1&&q.r.left<r.right-1&&r.top<q.r.bottom-1&&q.r.top<r.bottom-1)out.push(['overlap',c.className,q.c])});if(r.bottom>hb.bottom+1)out.push(['vclip',c.className]);seen.push({r,c:c.className});});});return out.slice(0,8)}""")
        print('width', w, 'issues', bad)
    b.close()
