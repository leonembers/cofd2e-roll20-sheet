import json
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'
M=json.load(open(f'{R}/michael_import.json'))['attributes']; V=json.load(open(f'{R}/vince_values.json'))
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    for nm,t,A in [('Michael / Sheet Check','werewolf2',M),('Vince Knight','hunter2',V),('legacy 1E vampire','vampire1',{'sheettype':'vampire1','character_name':'Old'})]:
        pg=b.new_page(viewport={'width':900,'height':1500}); errs=[]
        pg.on('pageerror',lambda e: errs.append(str(e)[:120])); pg.on('console',lambda m: m.type=='error' and errs.append(m.text[:120]))
        pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page=1&worker=1"); pg.wait_for_timeout(1000)
        pg.evaluate('a=>{setAttrs(a);__fire("sheet:opened",{})}',{k:str(v) for k,v in A.items() if not isinstance(v,(list,dict))}); pg.wait_for_timeout(2000)
        r=pg.evaluate('()=>({type:__A.sheettype,gl:__A.game_line,ed:__A.edition,legacy:__A.legacy_sheettype_1e,name:__A.character_name,werr:window.__werr||[]})')
        print(nm, r, 'errors:', [e for e in errs if 'fonts.g' not in e and 'jsdelivr' not in e][:5]); pg.close()
