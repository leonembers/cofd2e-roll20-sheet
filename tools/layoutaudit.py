"""Overflow / spill audit: every splat x tab x width. An element spills when it extends past its parent's box (by >2px)
or past the sheet background; text clips when a text control's content is wider than the control while not editable-scrolling."""
from playwright.sync_api import sync_playwright
import json, sys, collections
R = '/workspace/cofd/roll20'
TYPES = ['mortal2', 'hunter2', 'vampire2', 'werewolf2', 'mage2', 'promethean2', 'changeling2', 'geist2', 'mummy2', 'demon', 'beast', 'deviant-the-renegades', 'breeds2']
TABS = [('1', 'merits'), ('1', 'powers'), ('1', 'gear'), ('1', 'notes'), ('conditions', None), ('forms', None), ('scars-variations', None), ('settings', None)]
WIDTHS = [760, 1280]
JS = r"""()=>{const bg=document.querySelector('.sheet-background')||document.body;const B=bg.getBoundingClientRect();const out=[];
 const vis=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&e.offsetParent!==null};
 const sel=e=>{let s=e.tagName.toLowerCase();if(e.getAttribute('name'))s+='['+e.getAttribute('name')+']';else if(e.className&&typeof e.className==='string')s+='.'+e.className.trim().split(/\s+/).slice(0,2).join('.');return s};
 document.querySelectorAll('.sheet-background *').forEach(e=>{if(!vis(e))return;const cs=getComputedStyle(e);if(cs.position==='absolute'||cs.position==='fixed')return;
   const r=e.getBoundingClientRect();
   if(r.right>B.right+2||r.left<B.left-2)out.push(['sheet',sel(e),Math.round(r.right-B.right)]);
   const p=e.parentElement;if(p&&vis(p)&&!['TD','TH','TR','TABLE','TBODY'].includes(p.tagName)){const pr=p.getBoundingClientRect();const pc=getComputedStyle(p);
     if(pc.overflowX==='visible'&&(r.right>pr.right+3||r.left<pr.left-3)&&r.width>4&&e.tagName!=='OPTION')out.push(['parent',sel(e)+' in '+sel(p),Math.round(Math.max(r.right-pr.right,pr.left-r.left))]);}
   if((e.tagName==='BUTTON'||e.tagName==='SPAN'||e.tagName==='LABEL'||e.tagName==='SELECT')&&cs.overflowX!=='visible'&&e.scrollWidth>e.clientWidth+2&&cs.textOverflow!=='ellipsis'&&e.children.length===0)out.push(['clip',sel(e),e.scrollWidth-e.clientWidth]);
 });return out}"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg = b.new_page()
    agg = collections.Counter(); ex = {}
    only = sys.argv[1:] or TYPES
    for t in only:
        for w in WIDTHS:
            pg.set_viewport_size({'width': w, 'height': 1000})
            for page, mid in TABS:
                pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page={page}&worker=1&r20dark=1&dm=1"); pg.wait_for_timeout(250)
                pg.evaluate("""()=>{document.querySelectorAll('fieldset[class^="repeating_"]').forEach(f=>{const sec=f.className.split(' ')[0].replace('repeating_','');
                   try{__addRow(sec,{name:'A fairly long power name for testing',merit_name:'A fairly long merit name for testing',short_desc:'A short summary that is quite long indeed',rating:'3',merit:'3',pool:'Pre+Inti+1 = 8',pool_dice:'8',cost_disp:'1 WP 2 Essence',show:'0'})}catch(e){}})}"""); pg.wait_for_timeout(200)
                if mid: pg.evaluate(f"()=>setAttrs({{mid_tab:'{mid}'}})"); pg.wait_for_timeout(150)
                for kind, s, d in pg.evaluate(JS):
                    k = (kind, s.split('[')[0] if 'repeating' in s else s); agg[k] += 1; ex.setdefault(k, f'{t}/{page}/{mid}/{w}px +{d}')
    for k, n in agg.most_common(60): print(n, k, ex[k])
    print('TOTAL', sum(agg.values()), 'distinct', len(agg))
