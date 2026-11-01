from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page(viewport={'width':820,'height':1300})
    pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page=1&worker=1&r20dark=1&dm=1");pg.wait_for_timeout(700)
    pg.evaluate("()=>setAttrs({strength:3,dexterity:3,stamina:3})")
    pg.locator('.sheet-main-forms').first.screenshot(path=f'{R}/shots/r5-main-forms.png')
    for f in ('gauru','urhan'):
        pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page=1&worker=1&r20dark=1&dm=1");pg.wait_for_timeout(600)
        pg.locator(f'.sheet-main-forms button[name="act_setform_{f}"]').first.click();pg.wait_for_timeout(700)
        print(f,pg.evaluate("()=>[__A.form,__A.strength_eff||'',__A.form_label]"),pg.evaluate("()=>window.__werr||[]"))
        pg.evaluate("()=>setAttrs({pagenumber:'forms'})");pg.wait_for_timeout(500)
        pg.locator('.sheet-fcards').first.screenshot(path=f'{R}/shots/r5-forms-{f}.png')
