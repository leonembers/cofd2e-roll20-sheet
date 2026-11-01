import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
IMG_BASE = re.search(r'IMG_BASE = "([^"]+)"', open(os.path.join(HERE, 'build.py')).read()).group(1)
h = open(os.path.join(ROOT, 'sheet.html'), encoding='utf-8').read()
c = open(os.path.join(ROOT, 'sheet.css'), encoding='utf-8').read().replace(IMG_BASE, 'img')
h = h.replace(IMG_BASE, 'img')
worker = re.search(r'<script type="text/worker">(.*?)</script>', h, re.S).group(1)
h = re.sub(r'<script type="text/worker">.*?</script>', '', h, flags=re.S)
tr = open(os.path.join(ROOT, 'translation.json'), encoding='utf-8').read()
data = open(os.path.join(ROOT, 'vince_values.json'), encoding='utf-8').read()
shim = open(os.path.join(HERE, 'shim.js'), encoding='utf-8').read()
out = f'''<!doctype html><html><head><meta charset="utf-8"><title>CofD 2E multi-splat sheet - local preview</title>
<style>body{{background:var(--pbg,#fff);margin:0;padding:10px;font-family:Arial,sans-serif}} .charsheet{{width:1080px;position:relative;z-index:0}}
.repcontrol button{{font-size:11px;margin:2px}}
{c}</style>
<script>window.TRANSLATION={tr};
const _P=new URLSearchParams(location.search); window.PREVIEW_DATA = _P.get('splat')==='hunter2' || !_P.get('splat') ? {data} : (_P.get('splat')==='werewolf2' ? {{version:5, sheettype:'werewolf2', game_line:'werewolf', character_name:'Sees-Far', auspice:'Rahu', tribe:'Blood Talons', tribe_key:'blood-talons', moon_gift_dots:'2', moon_gift_name:"Full Moon's Gift", moon_gift_facets:"Killer Instinct, Warrior's Hide", brawl_mark:'1', intimidation_mark:'1', survival_mark:'1', brawl_mk:'1', brawl_again:'9', primal_urge:'3'}} : _P.get('splat')==='vampire2' ? {{version:5, sheettype:'vampire2', game_line:'vampire', character_name:'Marcus Vale', clan:'Mekhet', covenant:'Ordo Dracul', morality:'5', power:'3'}} : {{version:5}});</script>
<script>{shim}</script>
<script>{worker}</script>
</head><body><script>if(new URLSearchParams(location.search).get("dark")!=="0"){{document.documentElement.style.setProperty("--pbg","#1d1d1f")}}</script><div class="charsheet" id="cs">{h}</div><script>if(new URLSearchParams(location.search).get("dark")!=="0")document.getElementById("cs").classList.add("sheet-darkmode");</script></body></html>'''
open(os.path.join(ROOT, 'preview.html'), 'w', encoding='utf-8').write(out)
print('preview ok')
