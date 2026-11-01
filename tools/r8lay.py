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
    import sys; tag=sys.argv[1]
    for w in (700,1300):
        go(pg,'werewolf2',page='1',w=w)
        pg.evaluate("()=>setAttrs({form:'gauru',fh_gauru_height:`6'6\"`,fh_gauru_weight:'269 lbs',det_dob:'November 20th, 1990',det_race:'Mixed (Caucasian, Half-Mohawk)'})"); pg.wait_for_timeout(500)
        print(w, pg.evaluate("()=>[document.querySelector('.sheet-form-qrow')?.innerText, [...document.querySelectorAll('.sheet-quick-actions')].filter(e=>e.getClientRects().length).length]"))
        pg.screenshot(path=S+f'r8-{tag}-main-{w}.png',full_page=False)
        pg.evaluate("()=>setAttrs({mid_tab:'notes'})"); pg.wait_for_timeout(500)
        el=pg.query_selector('.sheet-mp-notes') or pg.query_selector('.sheet-midpane')
        pg.screenshot(path=S+f'r8-{tag}-notes-{w}.png',full_page=False)
        g=pg.evaluate("""()=>{const q=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.right)]};return {skills:q('.sheet-skills'),mid:q('.sheet-midpane'),right:q('.sheet-rightpane')||q('.sheet-col3')}}""")
        print(w,g)
