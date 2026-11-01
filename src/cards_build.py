import re, os, html as H
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sh=open(os.path.join(ROOT,'sheet.html')).read(); css=open(os.path.join(ROOT,'sheet.css')).read()
tpl=re.search(r'<rolltemplate class="sheet-rolltemplate-cofd-entry">(.*?)</rolltemplate>',sh,re.S).group(1)
def cls(t): return re.sub(r'class="([^"]+)"',lambda m:'class="'+' '.join('sheet-'+c for c in m.group(1).split())+'"',t)
tpl=cls(tpl)
def truth(name,d):
    m=re.match(r'(rollGreater|rollLess|rollBetween|rollWasFumble)\(\) roll ?([\d ]*)',name)
    if m:
        f,a=m.group(1),[int(x) for x in m.group(2).split()]; t=d['roll'][0]
        if f=='rollGreater': return t>a[0]
        if f=='rollLess': return t<a[0]
        if f=='rollBetween': return a[0]<=t<=a[1]
        return d['roll'][1]
    return bool(d.get(name))
def render(t,d):
    pat=re.compile(r'\{\{#(\^?)([^}]+)\}\}(.*?)\{\{/\1\2\}\}',re.S)
    while True:
        n=pat.sub(lambda m:(m.group(3) if truth(m.group(2),d)!=(m.group(1)=='^') else ''),t,count=1)
        if n==t: break
        t=n
    def val(m):
        k=m.group(1)
        if k=='roll': return f'<span class="inlinerollresult">{d["roll"][0]}</span>'
        return H.escape(str(d.get(k,'')))
    return re.sub(r'\{\{([^}#/^]+)\}\}',val,t)
C=[dict(charname='Vince Knight',gl_hunter=1,kind='Attack',name='Bowie Knife',f_damage='Successes + 1',f_pool='Strength 3 + Weaponry 2 + Other 0 = 5',f_initiative='-1',f_range='Melee',f_tags='Concealable',dmg_L=1,roll=(3,False)),
   dict(charname='Vince Knight',gl_hunter=1,kind='Merit',name='Contacts',dots='●●●',f_pool='Manipulation 4 + Socialize 2 = 6',o_exc='Your contact also volunteers a second, juicier lead.',roll=(5,False)),
   dict(charname='Vince Knight',gl_hunter=1,kind='Skill',name='Investigation',f_pool='Intelligence 3 + Investigation 3 + Willpower dice 1 = 7',exc3=1,risk='+1 die and 9-again',**{'9again':1},roll=(2,False)),
   dict(charname='Vince Knight',gl_hunter=1,kind='Perception',name='Wits + Composure',f_pool='Wits 3 + Composure 3 + Form 0 + Wounds 0',f_mod='Modifier 0',roll=(0,False)),
   dict(charname='Marcus Vale',gl_vampire=1,kind='Attack',name='Fists',f_pool='Strength 3 + Brawl 2 = 5',f_damage='Successes + 0',dmg_B=1,roll=(0,True),chance=1),
   dict(charname='Sees-Far',gl_werewolf=1,kind='Attack',name='Gauru Claws',f_pool='Strength 6 + Brawl 4 = 10',f_damage='Successes + 1',dmg_A=1,wpspend=1,roll=(4,False))]
def page(dark):
    cards=''.join(f'<div class="card"><div class="sheet-rolltemplate-cofd-entry{" sheet-rolltemplate-darkmode" if dark else ""}">{render(tpl,d)}</div></div>' for d in C)
    bg='#1d1d1f' if dark else '#fff'
    return f'<!doctype html><meta charset=utf-8><style>body{{background:{bg};margin:0;padding:14px;font-family:Arial}} .wrap{{display:flex;flex-wrap:wrap;gap:16px}} .card{{width:250px;padding-left:7px}} .inlinerollresult{{display:inline}}{css}</style><div class="wrap">{cards}</div>'
open(os.path.join(ROOT,'cards-dark.html'),'w').write(page(True)); open(os.path.join(ROOT,'cards-light.html'),'w').write(page(False)); print('cards ok')
