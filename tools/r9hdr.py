exec('\n'.join(open('/workspace/cofd/roll20/tools/r7shot.py').read().split('\n')[:10])+r'''
    for t in ('werewolf2','vampire2','mortal2','changeling2','geist2'):
        go(pg,t,page='1',w=1000)
        pg.evaluate("()=>setAttrs({Virtue:'Alpha',Vice:'my own thing'})"); pg.wait_for_timeout(500)
        print(t,pg.evaluate("()=>[__A.virtue,__A.virtue_pick,__A.vice,__A.vice_pick,[...document.querySelectorAll('.sheet-vv select')].filter(s=>s.getClientRects().length).length,(window.__werr||[]).length]"))
        e=pg.query_selector('.sheet-ig2') or pg.query_selector('.sheet-header'); b=e.bounding_box(); pg.screenshot(path=S+f'r9-header-{t}.png',clip={'x':b['x']-10,'y':b['y']-10,'width':b['width']+20,'height':b['height']+20})
''')
