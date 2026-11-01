"""Build a Roll20-like (CSE) preview of dist/: Roll20 wraps sheet in .ui-dialog .tab-content .charsheet,
adds body.sheet-darkmode, bootstrap-ish button/input defaults. Hidden attr values set via ?page=&dm=&r20dark="""
import os,re,sys
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h=open(f'{R}/dist/sheet.html').read(); c=open(f'{R}/dist/sheet.css').read()
W=re.search(r'<script type="text/worker">(.*?)</script>',h,flags=re.S).group(1); h=re.sub(r'<script type="text/worker">.*?</script>','',h,flags=re.S); h=re.sub(r'<rolltemplate.*?</rolltemplate>','',h,flags=re.S)
sim="""label{display:block;margin-bottom:5px;font-size:14px;font-weight:normal;line-height:20px}
.ui-dialog .charsheet select{width:220px;height:30px;padding:4px 6px;margin-bottom:10px;font-size:14px;line-height:20px}
.ui-dialog .charsheet input[type=checkbox]{width:13px;height:13px;margin:4px 0 0;line-height:normal}
.ui-dialog .charsheet input{margin-bottom:10px;font-size:14px}
body{margin:0;font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:14px;color:#333;background:#eee}
.ui-dialog{width:880px;margin:8px;background:#fff;border:1px solid #aaa}.ui-dialog .tab-content{padding:6px;overflow:auto}
.ui-dialog .charsheet button,.btn{display:inline-block;padding:4px 12px;font-size:14px;line-height:20px;color:#333;text-shadow:0 1px 1px rgba(255,255,255,.75);background-color:#f5f5f5;background-image:linear-gradient(#fff,#e6e6e6);border:1px solid #ccc;border-radius:4px}
.ui-dialog .charsheet input[type=text],.ui-dialog .charsheet select,.ui-dialog .charsheet textarea{border:1px solid #ccc;border-radius:3px;padding:2px;background:#fff;color:#555}
.ui-dialog .charsheet button[type=roll]::before{content:"t";font-family:dicefontd20,serif;color:#c00;font-size:1.3em;padding-right:3px}
body.sheet-darkmode{background:#111;color:#eee}body.sheet-darkmode .ui-dialog{background:#1f1f1f;border-color:#444}
body.sheet-darkmode .ui-dialog .charsheet button{color:#c8c3bc;text-shadow:rgba(24,26,27,.75) 0 1px 1px;background-image:linear-gradient(#181a1b,#26292b);border-color:#3e4446}
body.sheet-darkmode .ui-dialog .charsheet input,body.sheet-darkmode .ui-dialog .charsheet select,body.sheet-darkmode .ui-dialog .charsheet textarea{background:#000;color:#eee}
"""
js="""<script>const P=new URLSearchParams(location.search);const set=(n,v)=>document.querySelectorAll('[name="attr_'+n+'"]').forEach(e=>{if(e.type==='checkbox'||e.type==='radio'){e.checked=(e.value==v);}else{e.value=v;e.setAttribute('value',v);}});
if(P.get('r20dark')==='1')document.body.classList.add('sheet-darkmode');set('pagenumber',P.get('page')||'1');set('dark_mode',P.get('dm')||'1');set('sheettype',P.get('type')||'mortal2');</script>"""
import json as _j; wjs=open(f'{R}/tools/r20worker.js').read(); wsrc=_j.dumps(W).replace('</','<\\/')
wtail='<script>'+wjs.replace('</','<\\/')+'</script><script>if(new URLSearchParams(location.search).get("worker")==="1")window.__runWorker('+wsrc+');</script>'
open(f'{R}/dist/r20sim.html','w').write(f'<!doctype html><html><head><meta charset="utf-8"><style>{sim}</style><style>{c}</style></head><body><div class="ui-dialog"><div class="tab-content"><div class="charsheet">{h}</div></div></div>{js}{wtail}</body></html>')
