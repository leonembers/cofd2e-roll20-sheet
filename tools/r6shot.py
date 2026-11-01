import sys
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'
def go(pg,t,page=1,w=820):
    pg.set_viewport_size({'width':w,'height':1800})
    pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page={page}&worker=1&r20dark=1&dm=1")
    pg.evaluate('w=>{const d=document.querySelector(".ui-dialog");if(d){d.style.width=w+"px";d.style.maxWidth=w+"px"}}',w-20); pg.wait_for_timeout(700)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page()
    go(pg,'werewolf2'); pg.screenshot(path=f'{R}/shots/r6-wolf-main-820.png',full_page=True)
    go(pg,'werewolf2',w=700); pg.screenshot(path=f'{R}/shots/r6-wolf-main-700.png',full_page=True)
