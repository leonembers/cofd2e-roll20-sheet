exec('\n'.join(open('/workspace/cofd/roll20/tools/r7shot.py').read().split('\n')[:10])+r'''
    def st(): return pg.evaluate("()=>[__A.kuruth_active,__A.form,__A.kuruth_prev_form,(window.__werr||[]).length]")
    for ur in ('0','1'):
        go(pg,'werewolf2',page='1',w=1000)
        pg.evaluate(f"()=>setAttrs({{mid_tab:'kuruth',form:'dalu',urkhar_enabled:'{ur}'}})"); pg.wait_for_timeout(300)
        pg.evaluate("()=>{const o=window.startRoll;window.startRoll=(m,cb)=>o(m,r=>{if(r.results.roll)r.results.roll.result=3;cb&&cb(r)})}")
        pg.click('.sheet-mp-kuruth button[name="act_rr_wasuim"]'); pg.wait_for_timeout(400); print('ur',ur,'success ->',st())
        pg.evaluate("()=>{const o=window.startRoll;window.startRoll=(m,cb)=>o(m,r=>{if(r.results.roll)r.results.roll.result=0;cb&&cb(r)})}")
        pg.click('.sheet-mp-kuruth button[name="act_rr_wasuim"]'); pg.wait_for_timeout(500); print('ur',ur,'fail ->',st())
        print(' banner',pg.evaluate("()=>getComputedStyle(document.querySelector('.sheet-km-banner')).display"),
              'dim academics',pg.evaluate("()=>getComputedStyle(document.querySelector('input[name=attr_academics]').closest('.sheet-dots').previousElementSibling).opacity"),
              'brawl',pg.evaluate("()=>getComputedStyle(document.querySelector('input[name=attr_brawl]').closest('.sheet-dots').previousElementSibling).opacity"))
        if ur=='0': pg.screenshot(path=S+'r9-deathrage-mode.png',full_page=True); print('shot')
        pg.click('button[name="act_kuruth_end_rev" if ur=="1" else "act_kuruth_end"]'.replace('"act_kuruth_end_rev" if ur=="1" else "act_kuruth_end"', 'act_kuruth_end_rev' if ur=='1' else 'act_kuruth_end'), force=True); pg.wait_for_timeout(400)
        print(' end ->',st(),pg.evaluate("()=>getComputedStyle(document.querySelector('.sheet-km-banner')).display"))
''')
