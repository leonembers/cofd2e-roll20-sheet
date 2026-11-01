"""Moon Gift clip audit: all auspices x widths; spans/inputs text, row clip, ancestor scrollHeight>clientHeight."""
import sys
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'; SHOT='--shots' in sys.argv
JS='''()=>{const o=[];const blk=[...document.querySelectorAll('.sheet-mgx-a')].find(e=>e.offsetParent);if(!blk)return ['no visible block'];
 for(const e of blk.querySelectorAll('*')){if(!e.offsetParent)continue;
  const tx=(e.tagName=='INPUT'||e.tagName=='TEXTAREA')?e.value:(e.children.length?'':e.textContent.trim());
  if(tx&&(e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+1))o.push('clip '+e.className+': '+tx.slice(0,30));
  if(getComputedStyle(e).textOverflow=='ellipsis'&&tx)o.push('ellipsis '+e.className)}
 const br=blk.getBoundingClientRect();
 for(let a=blk;a&&a!==document.body;a=a.parentElement){const cs=getComputedStyle(a);
  if(a.scrollHeight>a.clientHeight+1&&/hidden|clip/.test(cs.overflowY))o.push('anc-clipY '+a.className.slice(0,40)+' '+a.scrollHeight+'>'+a.clientHeight);
  if(a.scrollWidth>a.clientWidth+1&&/hidden|clip/.test(cs.overflowX))o.push('anc-clipX '+a.className.slice(0,40));
  const r=a.getBoundingClientRect(); if(/hidden|clip|auto|scroll/.test(cs.overflow)&&(br.bottom>r.bottom+1||br.right>r.right+1)&&a!==blk&&!/auto|scroll/.test(cs.overflowY))o.push('anc-cuts '+a.className.slice(0,40))}
 return [...new Set(o)]}'''
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  for w in (700,820,1000):
    pg=b.new_page(viewport={'width':w,'height':1400})
    pg.goto(f"file://{R}/dist/r20sim.html?type=werewolf2&page=1&worker=1&r20dark=1&dm=1"); pg.wait_for_timeout(600)
    pg.locator('button[name="act_midtab_powers"]').first.click()
    for a,rn in [('Cahalith','glory'),('Elodoth','honor'),('Irraka','cunning'),('Ithaeur','wisdom'),('Rahu','purity')]:
      pg.evaluate(f"()=>{{setAttrs({{auspice:'{a}',renown_{rn}:'2'}});__fire('change:auspice',{{newValue:'{a}'}})}}"); pg.wait_for_timeout(500)
      r=pg.evaluate(JS); print(w,a,r)
      if SHOT and w in (700,820): pg.locator('.sheet-mgx').first.screenshot(path=f'{R}/shots/mgx-{a.lower()}-{w}.png')
