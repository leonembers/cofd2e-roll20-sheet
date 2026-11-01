"""Splat isolation audit: per sheet type, collect visible text on every page/middle tab and flag other splats' terms."""
import re, sys, json
from playwright.sync_api import sync_playwright
R='/workspace/cofd/roll20'
TYPES=['mortal2','mortal2-ghost','vampire2','werewolf2','breeds2','mage2','promethean2','changeling2','hunter2','geist2','demon','beast','deviant-the-renegades']
TERMS={
 'vampire':['Vitae','Blood Potency','Disciplines?','Clan','Covenant','Devotions?','Banes?','Coils?','Kindred','Predatory Aura'],
 'werewolf':['Auspices?','Renown','Kuruth','Primal Urge','Tribes?','Lodges?','Fetish(?:es)?','Death Rage','Wasu-Im','Basu-Im','Gauru','Urshul','Hishu','Urhan',"Ur'Khar",'Rites?','Hunter.s Aspect','Gifts? & Renown','Moon Gifts?','Shadow Gifts?','Wolf Gifts?','Uratha'],
 'mage':['Arcana','Arcanum','Gnosis','Mana','Path','Orders?','Nimbus','Rotes','Praxis','Praxes','Obsessions','Legacy','Awakened','Paradox'],
 'changeling':['Seemings?','Wyrd','Glamour','Kith','Courts?','Contracts?','Needle','Thread','Mantle','Frailt(?:y|ies)','Lost'],
 'promethean':['Pyros','Azoth','Lineages?','Refinements?','Transmutations?','Pilgrimage','Elpis','Bestowments?','Disquiet','Pilgrim Marks','Role'],
 'demon':['Embeds?','Exploits?','Cover','Aether','Primum','Incarnation','Agenda','Demonic Form','Glitch','Ring'],
 'beast':['Lair','Satiety','Hunger','Atavisms?','Nightmares?','Kinship','Legend','Horror','Brood','Family'],
 'geist':['Synergy','Haunts?','Keys','Ceremon(?:y|ies)','Plasm','Burden','Archetype','Krewe','Mementos?','Geist'],
 'deviant':['Variations?','Scars?','Instability','Convictions?','Loyalt(?:y|ies)','Clade','Divergence','Origin','Remade'],
 'hunter':['Endowments?','Tactics?','Professions?','Conspirac(?:y|ies)','Compacts?','Tier'],
 'mummy':['Sekhem','Pillars?','Utterances?','Affinit(?:y|ies)','Deceived'],
 'ghost':['Numina','Manifestations?','Influences?','Anchors?'],
}
OWN={'mortal2':[],'mortal2-ghost':['ghost'],'vampire2':['vampire'],'werewolf2':['werewolf'],'breeds2':['werewolf'],'mage2':['mage'],
 'promethean2':['promethean'],'changeling2':['changeling'],'hunter2':['hunter'],'geist2':['geist'],'demon':['demon'],'beast':['beast'],'deviant-the-renegades':['deviant']}
# words shared by several lines (or plain English in core rules) that must not be flagged for the type listed
SHARED={'Essence':None}
PAGES=['1','conditions','settings','forms','scars-variations']+['mt:'+m for m in ('merits','powers','weapons','kuruth','gear','notes')]
JS=r'''()=>{const out=new Set();const vis=e=>{if(!e)return false;const s=getComputedStyle(e);return e.getClientRects().length>0&&s.visibility!=='hidden'&&s.display!=='none'};
const root=document.querySelector('.ui-dialog')||document.body;
const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){const t=n.textContent.trim();if(!t)continue;const p=n.parentElement;if(!p||p.closest('script,style,select,textarea,.sheet-rolltemplate-wrap,[class*=rolltemplate]'))continue;if(vis(p))out.add(t.slice(0,80))}
document.querySelectorAll('select').forEach(s=>{if(vis(s))[...s.options].forEach(o=>out.add('opt:'+o.textContent.trim().slice(0,60)))});
document.querySelectorAll('input[placeholder],textarea[placeholder]').forEach(i=>{if(vis(i))out.add('ph:'+i.placeholder.slice(0,60))});
return [...out]}'''
def main():
    only=sys.argv[1:] or TYPES; res={}; total=0
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/google-chrome'); pg=b.new_page(viewport={'width':1300,'height':1600})
        for t in only:
            hits={}
            for page in PAGES:
                mt=page[3:] if page.startswith('mt:') else None
                pg.goto(f"file://{R}/dist/r20sim.html?type={t}&page={'1' if mt else page}&worker=1&r20dark=1&dm=1"); pg.wait_for_timeout(700)
                if mt: pg.evaluate('m=>setAttrs({mid_tab:m})',mt); pg.wait_for_timeout(300)
                for txt in pg.evaluate(JS):
                    if page=='settings' and re.search(r': The ',txt): continue  # Config sheet-type selector lists every line by design
                    if t=='vampire2' and 'Rites / Miracles' in txt: continue  # Cruac rites / Theban miracles are Vampire
                    for sp,words in TERMS.items():
                        if sp in OWN[t]: continue
                        for wd in words:
                            if re.search(r'(?<![A-Za-z])'+wd+r'(?![A-Za-z])',txt):
                                hits.setdefault(f'{sp}:{wd}',set()).add(f'{page}|{txt}')
            res[t]={k:sorted(v)[:6] for k,v in hits.items()}; total+=len(hits)
            print(t,len(hits)); [print('   ',k,sorted(v)[:4]) for k,v in hits.items()]
    json.dump(res,open(f'{R}/build/isoaudit.json','w'),indent=1)
    print('ISOLATION LEAKS',total)
main()
