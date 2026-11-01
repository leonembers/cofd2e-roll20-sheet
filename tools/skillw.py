"""Measure min Skills name-column width (checkbox+name+caret+badge) and dot track width across all splats, profession checkboxes on, 5 and 10 dots."""
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'
T=['mortal2','vampire2','werewolf2','breeds2','mage2','promethean2','changeling2','hunter2','geist2','demon','beast','deviant-the-renegades','mummy2']
JS="""()=>{let m=[0,''],dm=0;document.querySelectorAll('.sheet-skills > div').forEach(row=>{if(!row.offsetParent)return;const nb=row.querySelector(':scope > button.sheet-toggle');if(!nb){dm=Math.max(dm,row.scrollWidth);return}
 nb.style.setProperty('width','max-content','important');nb.style.setProperty('max-width','none','important');nb.style.setProperty('flex','none','important');nb.style.setProperty('overflow','visible','important');
 const rs=getComputedStyle(row);const g=parseFloat(rs.columnGap)||0;let w=parseFloat(rs.paddingLeft)+parseFloat(rs.paddingRight),n=0;
 for(const c of row.children){const cs=getComputedStyle(c);if(cs.display==='none'||cs.position==='absolute')continue;w+=c.getBoundingClientRect().width+parseFloat(cs.marginLeft)+parseFloat(cs.marginRight);n++}
 w+=g*Math.max(0,n-1);if(w>m[0])m=[Math.ceil(w),nb.textContent.trim()]});return [m,dm,getComputedStyle(document.querySelector('.sheet-skills')).gridTemplateColumns]}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome');pg=b.new_page(viewport={'width':1400,'height':1400})
    best=[0,'']; bd=0
    for t in T:
        pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page=1&worker=1&r20dark=1&dm=1");pg.wait_for_timeout(400)
        pg.evaluate("()=>setAttrs({enable_profession:'1',extended_dots:'1',attr_max:'10',skill_max:'10'})");pg.wait_for_timeout(300)
        r=pg.evaluate(JS); print(t,r,flush=True)
        if r[0][0]>best[0]: best=[r[0][0],t+':'+r[0][1]]
        bd=max(bd,r[1])
    print('BEST',best,'DOTS',bd)
