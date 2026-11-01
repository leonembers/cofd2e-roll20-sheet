from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'; S=f'{R}/shots/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    for w in (700,900):
        pg=b.new_page(viewport={'width':w,'height':1200})
        pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page=1&worker=1&r20dark=1&dm=1"); pg.wait_for_timeout(700)
        pg.evaluate("()=>setAttrs({wp_spend:'1',kuruth_passive:'Seeing a packmate bleed out in front of me while I can do nothing',kuruth_common:'Being caged or restrained',kuruth_specific:'Hearing the name of the man who killed my father',flesh_touchstone:'Sarah (sister)',spirit_touchstone:'The old mill locus'})"); pg.wait_for_timeout(300)
        pg.evaluate("()=>{const c=document.querySelector('input[name=attr_wp_spend]');c.checked=true}")
        g=pg.locator('.sheet-diceroller-grid').first; print(w,'roller h',g.bounding_box()['height']); g.screenshot(path=S+f'r5-roller-{w}.png')
        pg.locator('button[name="act_midtab_powers"]').first.click(); pg.wait_for_timeout(500)
        el=pg.locator('.sheet-wolf-rcol').first.locator('xpath=..'); el.scroll_into_view_if_needed(); el.screenshot(path=S+f'r5-renown-{w}.png')
        print('cols',[round(pg.locator(c).first.bounding_box()['height']) for c in ('.sheet-wolf-lcol','.sheet-wolf-rcol')])
        pg.close()
