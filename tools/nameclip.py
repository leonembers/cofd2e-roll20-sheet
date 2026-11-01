"""Find clipped/ellipsized names: skills, conditions, gear, entry rows, all types, 760/1280."""
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'
TYPES=['mortal2','vampire2','werewolf2','mage2','changeling2','hunter2','promethean2','geist2','demon2','mummy2','beast2','deviant2','wolfblooded2']
JS='''()=>{const o=[];for(const e of document.querySelectorAll('.sheet-entry-head button.sheet-entry-post, .sheet-skill-name, .sheet-skills label, .sheet-skills span, .sheet-cond-name, .sheet-conditions span, .sheet-conditions button, [class*=weapon] span, [class*=gear] span, [class*=equip] span')){if(!e.offsetParent)continue;const t=e.textContent.trim();if(!t)continue;if(e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+1)o.push(e.className.slice(0,30)+':'+t.slice(0,30))}return [...new Set(o)]}'''
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
  for w in (760,1280):
    pg=b.new_page(viewport={'width':w,'height':1000})
    for t in TYPES:
      try: pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page=1&worker=1&r20dark=1&dm=1"); pg.wait_for_timeout(500)
      except Exception as x: print(t,x); continue
      for sec,a in [('weapons',dict(name='Heckler & Koch MP5 Submachine Gun (Suppressed)')),('conditions',dict(name='Shaken (Persistent, Supernatural Fear)')),('merits',dict(merit_name='Professional Training (Investigation)'))]:
        try: pg.evaluate("([s,a])=>window.__addRow(s,a)",[sec,a])
        except Exception: pass
      pg.wait_for_timeout(400); r=pg.evaluate(JS)
      if r: print(w,t,r)
  print('done')
