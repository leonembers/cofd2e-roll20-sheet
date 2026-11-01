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
    go(pg,'werewolf2',w=700)
    pg.evaluate("()=>setAttrs({kuruth_passive:'Smell of blood\\nBeing caged',kuruth_common:'Seeing a pack-mate wounded',kuruth_specific:'Silver weapon drawn on me'})")
    pg.screenshot(path=S+'r8-wolf-main-700.png',full_page=True)
    pg.evaluate("()=>setAttrs({mid_tab:'kuruth'})"); pg.wait_for_timeout(600)
    el=pg.query_selector('.sheet-mp-kuruth'); el.scroll_into_view_if_needed()
    bb=el.bounding_box(); print('kuruth pane',bb)
    pg.screenshot(path=S+'r8-wolf-kuruth.png',clip={'x':0,'y':max(0,bb['y']-60),'width':700,'height':bb['height']+80})
    pg.click('button[name="act_rr_wasuim"] >> nth=-1'); pg.wait_for_timeout(600)
    print('rolls',pg.evaluate("()=>(window.__rolls||[]).slice(-1)"))
    pg.screenshot(path=S+'r8-wolf-kuruth-roll.png',full_page=True)
