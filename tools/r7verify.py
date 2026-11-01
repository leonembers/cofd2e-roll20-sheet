import json
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page()
    pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page=1&worker=1"); pg.wait_for_timeout(1500)
    o={}
    W=lambda n=500: pg.wait_for_timeout(n)
    pg.evaluate('()=>setAttrs({willpower:3,willpower_max:5,dexterity:3,wits:2,stamina:3,resolve:2,composure:3,size:5,strength:3})'); W(800)
    o['calc']=pg.evaluate('()=>({def:__A.defense_calc,init:__A.initiative_calc,size:__A.size_calc,wp:__A.willpower_calc})')
    pg.evaluate('()=>setAttrs({dexterity:5})'); W(800)
    o['calc_after_dex5']=pg.evaluate('()=>__A.initiative_calc')
    nm=pg.evaluate('()=>{const b=[...document.querySelectorAll("button[name^=act_rr_]")].find(x=>!x.closest(".repcontainer,fieldset"));return b&&b.getAttribute("name")}')
    o['rollbtn']=nm
    pg.evaluate('n=>__fire("clicked:"+n.slice(4),{sourceAttribute:n.slice(4)})',nm); W(800)
    o['roll1']=pg.evaluate('()=>__rolls.slice(-1)[0]&&__rolls.slice(-1)[0].slice(0,220)')
    o['rr_last']=pg.evaluate('()=>({mac:(__A.rr_last_mac||"").slice(0,60),id:__A.rr_last_id})')
    pg.evaluate('()=>__fire("clicked:wp_reroll",{})'); W(800)
    o['reroll']=pg.evaluate('()=>__rolls.slice(-1)[0].slice(0,260)'); o['wp_after']=pg.evaluate('()=>__A.willpower')
    pg.evaluate('()=>__fire("clicked:wp_reroll",{})'); W(800)
    o['reroll2']=pg.evaluate('()=>__rolls.slice(-1)[0].slice(0,160)')
    o['werr']=pg.evaluate('()=>window.__werr||[]')
    # dark eras via config action
    pg.evaluate('()=>__fire("clicked:archery_era",{})'); W(600)
    o['archery_era_after_click']=pg.evaluate('()=>__A.archery_era')
    print(json.dumps(o,indent=1))
