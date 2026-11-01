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
    for w in (700,1300):
        go(pg,'werewolf2',w=w)
        pg.evaluate("()=>setAttrs({mid_tab:'notes',det_age:'27',det_apparent_age:'27',det_dob:'November 20th, 1990',det_height:\"6'6\\\"\",det_weight:'269 lbs',det_hair:'Black, shoulder-length',det_eyes:'Brown',det_sex:'male',det_sex_mig:'',det_race:'Mixed (Caucasian, Half-Mohawk)',det_nationality:'Canadian-American'})")
        pg.wait_for_timeout(500)
        pg.evaluate("()=>{const f=window.__fire||null}")
        el=pg.query_selector('.sheet-mp-notes .sheet-det-grid'); bb=el.bounding_box()
        print(w,bb, pg.evaluate("()=>[...document.querySelectorAll('.sheet-mp-notes .sheet-det-grid input,.sheet-mp-notes .sheet-det-grid select')].filter(i=>i.scrollWidth>i.clientWidth+1).map(i=>i.name+' '+i.scrollWidth+'>'+i.clientWidth)"), pg.evaluate("()=>window.__A.det_sex_sel"))
        pg.screenshot(path=S+f'r8-details-{w}.png',clip={'x':bb['x']-10,'y':bb['y']-10,'width':bb['width']+20,'height':bb['height']+20})
