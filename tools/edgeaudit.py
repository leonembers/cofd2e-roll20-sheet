"""Edge-safe audit: no visible element may cross the frame's content-safe inset (SAFE px, per side) at 700/820/1200 for all types."""
import sys
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'
TYPES=['mortal2','mortal2-ghost','vampire2','werewolf2','breeds2','mage2','promethean2','changeling2','hunter2','geist2','demon','beast','deviant-the-renegades']
SAFE=float(sys.argv[1]) if len(sys.argv)>1 else 0.028
JS='''(safe)=>{const bg=document.querySelector('.sheet-background-image .sheet-bgart')||document.querySelector('.charsheet');const r=(bg.offsetParent?bg:document.querySelector('.charsheet')).getBoundingClientRect();
const ins=Math.max(18,r.width*safe);const L=r.left+ins,Rr=r.right-ins;const bad=[];
for(const e of document.querySelectorAll('.charsheet *')){if(!e.offsetParent||e.closest('.sheet-background-image,.repcontrol,rolltemplate,.sheet-footer')||e.matches('.sheet-spacer,.sheet-topinfo,.sheet-el_spacer')||e.classList.contains('sheet-footer'))continue;const cs=getComputedStyle(e);if(cs.visibility==='hidden'||cs.position==='fixed')continue;
const b=e.getBoundingClientRect();if(b.width<2||b.height<2||b.bottom<0)continue;if(e.children.length&&cs.backgroundImage==='none'&&cs.borderLeftStyle==='none'&&cs.borderRightStyle==='none'&&!(e.textContent||'').trim())continue;
if(e.children.length>3)continue;
if(b.left<L-0.5||b.right>Rr+0.5)bad.push((e.className||e.tagName)+'|'+(e.getAttribute('name')||'')+'|'+Math.round(b.left-r.left)+'..'+Math.round(r.right-b.right))}const ov=[];for(const e of document.querySelectorAll('.charsheet, .charsheet *')){if(!e.offsetParent&&e!==document.querySelector('.charsheet'))continue;const cs=getComputedStyle(e);if(!/auto|scroll/.test(cs.overflowX)&&e!==document.querySelector('.charsheet')&&e.tagName!=='BODY')continue;if(e.tagName==='TEXTAREA'||e.tagName==='INPUT'||e.tagName==='SELECT')continue;if(e.scrollWidth>e.clientWidth+1){let w=null,mx=0;const er=e.getBoundingClientRect();for(const c of e.querySelectorAll('*')){if(!c.offsetParent)continue;const x=c.getBoundingClientRect().right-er.right;if(x>mx){mx=x;w=c}}ov.push((e.className||e.tagName).slice(0,40)+' sw'+e.scrollWidth+'>cw'+e.clientWidth+' cause:'+(w?((w.className||w.tagName)+'|'+(w.getAttribute('name')||'')).slice(0,60):'?'))}}
for(const de of document.querySelectorAll('.ui-dialog, .tab-content, .charsheet, .sheet-background')){if(de.scrollWidth>de.clientWidth+1){let w=null,mx=0;const er=de.getBoundingClientRect();for(const c of de.querySelectorAll('*')){if(!c.offsetParent)continue;const x=c.getBoundingClientRect().right-er.right;if(x>mx){mx=x;w=c}}ov.push('HSCROLL '+(de.className||'').slice(0,20)+' sw'+de.scrollWidth+'>'+de.clientWidth+' cause:'+(w?((w.className||w.tagName)+'|'+(w.getAttribute('name')||'')).slice(0,70):'?'))}}
return {ins:Math.round(ins),bad:bad.slice(0,6),n:bad.length+ov.length,ov:ov.slice(0,5)}}'''
fails=0
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    for w in (700,850,1000,1300):
        pg=b.new_page(viewport={'width':w,'height':1400})
        for t in TYPES:
            for page in ('1','conditions','forms','settings','mt:merits','mt:powers','mt:weapons','mt:kuruth','mt:gear','mt:notes'):
                mt=page[3:] if page.startswith('mt:') else None; pgq='1' if mt else page
                if mt=='kuruth' and t!='werewolf2': continue
                pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page={pgq}&worker=1&r20dark=1&dm=1"); pg.evaluate('w=>{const d=document.querySelector(".ui-dialog");if(d){d.style.width=w+"px";d.style.maxWidth=w+"px"}}',w-20); pg.wait_for_timeout(500)
                if mt: pg.evaluate('m=>setAttrs({mid_tab:m})',mt); pg.wait_for_timeout(300)
                r=pg.evaluate(JS,SAFE)
                if r['n']: fails+=1; print(w,t,page,r)
        pg.close()
print('EDGE FAILS',fails)
