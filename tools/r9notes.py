exec('\n'.join(open('/workspace/cofd/roll20/tools/r7shot.py').read().split('\n')[:10])+r'''
    def full(n): pg.screenshot(path=S+n,full_page=True); print(n)
    for w in (700,1300):
        go(pg,'werewolf2',page='1',w=w); pg.click('button[name=act_page_details]'); pg.wait_for_timeout(500)
        print('notes',w,pg.evaluate("()=>{const d=document.querySelector('.sheet-details-page');const p=d.querySelector('.sheet-det-portrait').getBoundingClientRect(),g=d.querySelector('.sheet-det-grid').getBoundingClientRect();return [getComputedStyle(d.parentElement).display,Math.round(p.width),Math.round(g.left-p.right),Math.round(g.top-p.top),Math.round(d.getBoundingClientRect().width),[...document.querySelectorAll('button.sheet-page-details')].filter(b=>b.getClientRects().length).length]}"))
        full(f'r9-notes-page-{w}.png')
''')
