"""Input-value clip audit: fill every visible text input with a realistic long value (Michael's data on werewolf2) and flag scrollWidth>clientWidth."""
from playwright.sync_api import sync_playwright
import json, sys, collections
R='/workspace/cofd/roll20'
TYPES=['mortal2','hunter2','vampire2','werewolf2','mage2','promethean2','changeling2','geist2','mummy2','demon','beast','deviant-the-renegades','breeds2']
TABS=[('1','merits'),('1','powers'),('1','gear'),('1','notes'),('conditions',None),('forms',None),('scars-variations',None),('settings',None)]
MI=json.load(open(f'{R}/michael_import.json'))['attributes']
FILL=r"""(mi)=>{const pick=n=>{n=n.replace(/^attr_/,'');if(mi[n]!==undefined&&String(mi[n]).length>2)return String(mi[n]);
 const k=n.toLowerCase();
 if(/height/.test(k))return `9'11"`; if(/weight/.test(k))return '1,234 lb'; if(/dob|birth/.test(k))return 'November 14, 1994';
 if(/(^|_)age/.test(k))return '134'; if(/range/.test(k))return '20/40/80'; if(/clip|ammo/.test(k))return '7+1'; if(/damage|dmg/.test(k))return '+3 L';
 if(/cost/.test(k))return '1 Essence + 1 WP'; if(/pool/.test(k))return 'Presence + Intimidation + Glory';
 if(/name|title/.test(k))return 'Professional Training (Investigation)';
 return 'Kevlar weave + graphene plates'};
 const out=[];document.querySelectorAll('.sheet-background input[type=text], .sheet-background input:not([type])').forEach(e=>{if(!e.offsetParent||e.readOnly||e.disabled)return;const r=e.getBoundingClientRect();if(r.width<1)return;
  if(/portrait_url|experience|^attr_conditions[0-9]/.test(e.getAttribute('name')||''))return;e.value=pick(e.getAttribute('name')||'');if(e.scrollWidth>e.clientWidth+1)out.push((e.getAttribute('name')||'?')+' w'+Math.round(r.width)+' need'+e.scrollWidth)});return out}"""
fails=collections.Counter(); ex={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=b.new_page()
    for t in (sys.argv[1:] or TYPES):
        for w in (700,850,1000,1300):
            pg.set_viewport_size({'width':w,'height':1000})
            for page,mid in TABS:
                pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page={page}&worker=1&r20dark=1&dm=1"); pg.wait_for_timeout(250)
                pg.evaluate("""()=>{document.querySelectorAll('fieldset[class^="repeating_"]').forEach(f=>{try{__addRow(f.className.split(' ')[0].replace('repeating_',''),{show:'1'})}catch(e){}})}""")
                if mid: pg.evaluate(f"()=>setAttrs({{mid_tab:'{mid}'}})")
                pg.wait_for_timeout(200)
                for s in pg.evaluate(FILL, MI):
                    k=s.split(' ')[0]; fails[k]+=1; ex.setdefault(k,f'{t}/{page}/{mid}/{w}: {s}')
for k,n in fails.most_common(): print(n,ex[k])
print('INPUT CLIP DISTINCT',len(fails))
