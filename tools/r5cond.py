from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page(viewport={'width':820,'height':1300})
    pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page=conditions&worker=1&r20dark=1&dm=1");pg.wait_for_timeout(600)
    pg.evaluate("()=>{setAttrs({cond_mod_manual:'-2',cond_mig_v1:''});__fire('sheet:opened',{})}");pg.wait_for_timeout(900)
    A=pg.evaluate("()=>__A");print('migrated',[ (k,v) for k,v in A.items() if k.startswith('repeating_conditions')][:4],'mod',A.get('cond_mod'),'manual',A.get('cond_mod_manual'))
    pg.evaluate("()=>{setAttrs({cond_shaken:'1'});__fire('change:cond_shaken',{})}");pg.wait_for_timeout(500)
    print('mod after shaken',pg.evaluate("()=>[__A.cond_mod,__A.cond_note]"),'werr',pg.evaluate("()=>window.__werr||[]"))
    pg.locator('.sheet-cond-grid-wrap').first.locator('xpath=..').screenshot(path=f'{R}/shots/r5-conditions.png')
