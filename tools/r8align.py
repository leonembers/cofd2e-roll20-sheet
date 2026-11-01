import json
import sys
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'; S=R+'/shots/'
def go(pg,t,page=1,w=850,h=1800):
    pg.set_viewport_size({'width':w,'height':h})
    pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page={page}&worker=1&r20dark=1&dm=1")
    pg.evaluate('w=>{const d=document.querySelector(".ui-dialog");if(d){d.style.width=w+"px";d.style.maxWidth=w+"px"}}',w-20); pg.wait_for_timeout(1500)
out={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page()
    tag=sys.argv[1] if len(sys.argv)>1 else 'after'
    go(pg,'werewolf2',w=1300)
    pg.evaluate("()=>{setAttrs({renown_purity:2,renown_glory:3,renown_honor:1,renown_wisdom:4,renown_cunning:2,auspice:'Rahu',mid_tab:'powers'});['Moon','Shadow','Wolf'].forEach((g,i)=>__addRow('gifts',{name:'War Howl '+i,gtype:g,renown:['Glory','Purity','Cunning'][i],rating:'2'}))}")
    pg.wait_for_timeout(800)
    def crop(sel,name,pad=6):
        el=pg.query_selector(sel)
        if not el or not el.bounding_box(): print('missing',sel); return
        el.scroll_into_view_if_needed(); bb=el.bounding_box()
        el.screenshot(path=S+f'r8-align-{name}-{tag}.png')
        print(name,'ok')
    # per-row icon/label vertical centre offsets
    print(pg.evaluate("""()=>[...document.querySelectorAll('.sheet-skills-renown .sheet-renown-row')].map(r=>{const i=r.querySelector('.sheet-ren-ic').getBoundingClientRect(),l=r.querySelector('span[data-i18n]').getBoundingClientRect(),d=r.querySelector('.sheet-dots').getBoundingClientRect();return [Math.round(i.width)+'x'+Math.round(i.height),+((i.top+i.bottom)/2-(l.top+l.bottom)/2).toFixed(1),+((d.top+d.bottom)/2-(l.top+l.bottom)/2).toFixed(1)]})"""))
    crop('.sheet-skills-renown','renown')
    crop('.sheet-mgx','moongift')
    crop('.sheet-entry-section.sheet-gifts','giftrows')
