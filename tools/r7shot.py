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
    for t in ['werewolf2','vampire2','mage2','changeling2']:
        go(pg,t); pg.screenshot(path=S+f'r7-font-{t}.png',clip={'x':0,'y':0,'width':850,'height':700})
        out[t]=pg.evaluate('()=>{const e=[...document.querySelectorAll(".sheet-section-header")].find(x=>x.offsetParent);return e?getComputedStyle(e).fontFamily+" | loaded:"+document.fonts.check("16px \\""+getComputedStyle(e).fontFamily.split(",")[0].replace(/"/g,"")+"\\"") :null}')
    go(pg,'werewolf2',w=700); pg.screenshot(path=S+'r7-wolf-main-700.png',full_page=True)
    go(pg,'werewolf2',w=1300); pg.screenshot(path=S+'r7-wolf-main-1300.png',full_page=True)
    # D10 icon
    out['d10']=pg.evaluate('()=>{const b=document.querySelector(".sheet-rollbar .sheet-rollcontainer > button.sheet-rollstyle");return b?getComputedStyle(b).backgroundImage:null}')
    out['renown_icons']=pg.evaluate('()=>[...document.querySelectorAll("span.sheet-ren-ic")].filter(x=>x.offsetParent).map(x=>getComputedStyle(x).backgroundImage.slice(-30)).slice(0,6)')
    for tab in ['weapons','gear']:
        r=pg.evaluate('t=>{const b=[...document.querySelectorAll("button.sheet-midtab-btn")].find(x=>(x.getAttribute("name")||"").includes(t));if(b){b.click();return b.getAttribute("name")}return null}',tab)
        pg.wait_for_timeout(800); out['tab_'+tab]=r; pg.screenshot(path=S+f'r7-wolf-{tab}.png',full_page=True)
    print(json.dumps(out,indent=1))
