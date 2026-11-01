from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'; S=R+'/shots/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page(viewport={'width':900,'height':1600})
    # roll card with reroll button (chatmock html)
    pg.goto(f'file://{S}chatmock-dark.html'); pg.wait_for_timeout(1500); pg.screenshot(path=S+'r7-rollcards.png',full_page=True)
    for page,name in [('forms','forms'),('conditions','conditions')]:
        pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page={page}&worker=1&r20dark=1&dm=1"); pg.wait_for_timeout(1500); pg.screenshot(path=S+f'r7-wolf-{name}.png',full_page=True)
    pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page=1&worker=1&r20dark=1&dm=1"); pg.wait_for_timeout(1200)
    pg.evaluate("()=>{__addRow('gifts',{name:'Warning Growl',renown:'Purity',show:'1'});__addRow('gifts',{name:'Sense Malice',renown:'Wisdom'});__addRow('fetishes',{name:'Bone Knife',rating:2,cost_wp:1,show:'1'});setAttrs({mid_tab:'powers',purity:2,wisdom:1,glory:1})}"); pg.wait_for_timeout(1200)
    pg.screenshot(path=S+'r7-wolf-gifts.png',full_page=True)
    pg.evaluate("()=>setAttrs({mid_tab:'gear'})"); pg.wait_for_timeout(800); pg.screenshot(path=S+'r7-wolf-gear-fetishes.png',full_page=True)
