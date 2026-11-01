import json
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'; S=R+'/shots/'
def go(pg,t,page=1,w=850,h=1800):
    pg.set_viewport_size({'width':w,'height':h})
    pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page={page}&worker=1&r20dark=1&dm=1")
    pg.evaluate('w=>{const d=document.querySelector(".ui-dialog");if(d){d.style.width=w+"px";d.style.maxWidth=w+"px"}}',w-20); pg.wait_for_timeout(1500)
out={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page()
    for ur in ('0','1'):
        go(pg,'werewolf2',page='forms',w=1000)
        pg.evaluate("u=>setAttrs({urkhar_enabled:u,form:'dalu',fcd_dalu_3:'1',fcd_gauru_3:'1'})",ur); pg.wait_for_timeout(600)
        if ur=='1':
            pg.evaluate("()=>{setAttrs({stamina:4,potency:3});}"); pg.wait_for_timeout(200)
            pg.evaluate("()=>window.__fire('change:form',{sourceType:'player',newValue:'urkhar'})"); pg.evaluate("()=>setAttrs({form:'urkhar'})"); pg.wait_for_timeout(600)
            print('urkhar', pg.evaluate("()=>[__A.urkhar_used,__A.urkhar_turns,__A.urkhar_basu_note,(window.__werr||[]).length]"))
        print(ur, pg.evaluate("()=>[...document.querySelectorAll('.sheet-fcard')].filter(e=>e.getClientRects().length).map(e=>e.className.split(' ')[1])"))
        el=pg.query_selector('.sheet-fcards'); el.screenshot(path=f'/workspace/cofd/roll20/shots/r8-forms-urkhar{ur}.png')
