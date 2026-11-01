import sys
exec('\n'.join(open('/workspace/cofd/roll20/tools/r7shot.py').read().split('\n')[:10])+r'''
    rd=lambda: pg.evaluate("()=>[1,2,3,4,5,6,7].map(i=>'.BLA'[+__A['healthbox_'+i]||0]).join('')+' wp='+__A.wound_penalty")
    def c(b,lab): pg.click(f'button[name=act_{b}]'); pg.wait_for_timeout(250); print(f'  {lab:14}', rd())
    for t in ('vampire2','werewolf2','mortal2'):
        go(pg,t,page='1',w=1000)
        pg.evaluate("()=>setAttrs({health:7,healthbox_1:2,healthbox_2:2,healthbox_3:1,healthbox_4:1,healthbox_5:1,healthbox_6:0,healthbox_7:0})"); pg.wait_for_timeout(400)
        print(t,'start 2L+3B', rd())
        c('heal_b','Heal B'); c('heal_a','Heal A(none)'); c('heal_l','Heal L'); c('heal_l','Heal L'); c('heal_l','Heal L(none)')
        c('dmg_l','+L'); c('dmg_b','+B'); c('dmg_b','+B'); c('dmg_b','+B (full)'); c('dmg_b','+B (full)'); c('dmg_l','+L (full)'); c('dmg_a','+A (full)')
        c('dmg_b','+B (full)'); c('dmg_l','+L (full)'); c('heal_b','Heal B')
        print('  worker errors', pg.evaluate("()=>(window.__werr||[]).length"))
    el=pg.query_selector('.sheet-heal-row'); b=el.bounding_box(); pg.screenshot(path=S+'r8-heal.png',clip={'x':b['x']-40,'y':b['y']-50,'width':b['width']+80,'height':80})
''')
