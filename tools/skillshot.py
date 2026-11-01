import sys,os
from playwright.sync_api import sync_playwright
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tag=sys.argv[1] if len(sys.argv)>1 else 'fix'
JS="""()=>{const sk=document.querySelector('.sheet-skills');const r=sk.getBoundingClientRect();let bad=[];
sk.querySelectorAll(':scope > div').forEach(d=>{if(!d.offsetParent)return;const b=d.getBoundingClientRect();if(b.right>r.right+0.5)bad.push('over:'+d.textContent.trim().slice(0,12));});
sk.querySelectorAll(':scope > div:not(.sheet-dots):not(.sheet-spec-row):not(.sheet-section-header):not(.sheet-subheader):not(.sheet-subsubheader):not(.sheet-skills-renown)').forEach(d=>{if(!d.offsetParent)return;if(d.getBoundingClientRect().height>26)bad.push('wrap:'+d.textContent.trim().slice(0,12));});
const sib=sk.nextElementSibling;const sr=sib?sib.getBoundingClientRect():null;
return {skR:r.right,skW:r.width,nextL:sr&&sr.left,bad}}"""
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  for t in ['werewolf2','vampire2','hunter2']:
    for w in [780,850,900]:
      pg=br.new_page(viewport={'width':w+20,'height':1500})
      pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page=1&worker=1&r20dark=1&dm=1")
      pg.add_style_tag(content=f".ui-dialog{{width:{w}px !important}}"); pg.wait_for_timeout(500)
      print(t,w,pg.evaluate(JS))
      pg.screenshot(path=f"{R}/shots/{tag}-{t}-{w}.png",full_page=False); pg.close()
  br.close()
