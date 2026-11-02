exec('\n'.join(open('/workspace/cofd/roll20/tools/r7shot.py').read().split('\n')[:10])+r'''
    for t in ('vampire2','werewolf2'):
        go(pg,t,page='settings',w=1000); pg.wait_for_timeout(500)
        e=pg.query_selector('.sheet-settings'); print(t,e.bounding_box())
        e.screenshot(path=S+f'r10-config-{t}.png')
    go(pg,'werewolf2',w=1000); pg.wait_for_timeout(1500)
    print('font',pg.evaluate("()=>[getComputedStyle(document.querySelector('.sheet-subheader')).fontFamily, document.fonts.check('16px WolfsRain')]"))
    pg.evaluate("()=>setAttrs({mid_tab:'powers'})"); pg.wait_for_timeout(1500); pg.screenshot(path=S+'r10-wolf-font.png',clip={'x':0,'y':0,'width':1000,'height':1400})
''')
