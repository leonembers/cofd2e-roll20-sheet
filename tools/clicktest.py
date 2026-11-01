"""Click every visible action button (dots/boxes/toggles) in r20sim with the worker emulator; report attr + visual change."""
import sys, json, os
from playwright.sync_api import sync_playwright
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES=sys.argv[1].split(',') if len(sys.argv)>1 else ['werewolf2']
PAGES=(os.environ.get('PAGES') or '1,forms,3,conditions,powers,details,settings').split(',')
JS="""async () => {
 const sig=el=>{const c=getComputedStyle(el);return [c.backgroundColor,c.backgroundImage,c.color,c.borderColor,c.opacity,c.visibility].join('|')};
 const vis=el=>{const r=el.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(el).visibility!=='hidden'&&!el.closest('fieldset')};
 const out=[]; const seen=new Set();
 const btns=[...document.querySelectorAll('button[type="action"]')].filter(vis);
 for(const b of btns){const name=b.getAttribute('name')||''; if(/^act_(page_|sheet_type_|rollstyle_)/.test(name))continue;
   const grp=b.parentElement; const key=name.replace(/[-_]?\\d+$/,''); 
   const sib=[...grp.querySelectorAll('button,span')].concat([b]);
   const before=sib.map(sig).join(';'); const A0=JSON.stringify(window.__A);
   b.click(); await new Promise(r=>setTimeout(r,60));
   const after=sib.map(sig).join(';'); const A1=JSON.stringify(window.__A);
   const a0=JSON.parse(A0),a1=JSON.parse(A1); const ch=Object.keys(a1).filter(k=>a0[k]!==a1[k]);
   out.push({name, attr:ch.slice(0,4), vis: before!==after});
 }
 return {out, err: window.__werr||[]};
}"""
res={}
with sync_playwright() as p:
  br=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  for t in TYPES:
    for dark in ('1','0'):
      for pg in PAGES:
        pgo=br.new_page(viewport={'width':900,'height':1400})
        q=f"type={t}&page={pg}&worker=1&r20dark={dark}&dm={dark}"
        pgo.goto(f"file://{R}/dist/r20sim.html?{q}"); pgo.wait_for_timeout(400)
        r=pgo.evaluate(JS); pgo.close()
        bad=[o for o in r['out'] if not (o['attr'] and o['vis'])]
        res[f'{t}/{"dark" if dark=="1" else "light"}/{pg}']={'tested':len(r['out']),'bad':bad,'err':r['err'][:5]}
  br.close()
json.dump(res,open(f'{R}/dist/clicktest.json','w'),indent=1)
for k,v in res.items(): print(k,'tested',v['tested'],'bad',len(v['bad']),[b['name']+('' if b['attr'] else '[noattr]')+('' if b['vis'] else '[novis]') for b in v['bad']][:12], v['err'][:2])
