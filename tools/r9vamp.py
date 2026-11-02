exec('\n'.join(open('/workspace/cofd/roll20/tools/r7shot.py').read().split('\n')[:10])+r'''
    go(pg,'vampire2',page='1',w=1000)
    pg.evaluate("""()=>{setAttrs({strength:'2',stamina:'3',dexterity:'3',wits:'2',athletics:'1',manipulation:'3',occult:'2',intelligence:'2',academics:'3',
      'repeating_disciplines_-a1_name':'Vigor','repeating_disciplines_-a1_rating':'2','repeating_disciplines_-a2_name':'Resilience','repeating_disciplines_-a2_rating':'1',
      'repeating_disciplines_-a3_name':'Celerity','repeating_disciplines_-a3_rating':'3','repeating_disciplines_-a4_name':'Cruac','repeating_disciplines_-a4_rating':'2',
      'repeating_rituals_-r1_rit_name':'Pangs of Proserpina','repeating_rituals_-r1_rit_trad':'cruac','repeating_rituals_-r1_rit_level':'1','repeating_rituals_-r1_rit_cost':'1 Vitae',
      'repeating_rituals_-r2_rit_name':'Blood Scourge','repeating_rituals_-r2_rit_trad':'theban','repeating_rituals_-r2_rit_level':'1','repeating_rituals_-r2_rit_cost':'1 Willpower + sacrament'})}""")
    pg.wait_for_timeout(1200)
    A=pg.evaluate("()=>{const a=window.__A;return ['strength_boost','strength_eff','stamina_eff','health','disc_celerity','defense_base','defense_calc','health_calc','strength_vcalc','strength_vb','defense_vb','repeating_rituals_-r1_rit_pool_txt','repeating_rituals_-r2_rit_pool_txt'].map(k=>k+'='+a[k])}")
    print('\n'.join(A))
    print('def shown',pg.evaluate("()=>document.querySelector('input[name=attr_defense]').value"), 'err',pg.evaluate("()=>(window.__werr||[]).length"))
    pg.screenshot(path=S+'r9-vampire-main.png',full_page=True)
    print('tabs',pg.evaluate("()=>[...document.querySelectorAll('.sheet-midtabs button')].filter(b=>b.getClientRects().length).map(b=>b.innerText.trim())"))
    pg.click('button[name=act_midtab_rituals]'); pg.wait_for_timeout(500)
    pg.query_selector('.sheet-mp-rituals').screenshot(path=S+'r9-vampire-rituals.png')
    e=pg.query_selector('.sheet-midtabs'); e.screenshot(path=S+'r9-midtab-pills-vampire.png')
    go(pg,'werewolf2',page='1',w=1000)
    print('wolf tabs',pg.evaluate("()=>[...document.querySelectorAll('.sheet-midtabs button')].filter(b=>b.getClientRects().length).map(b=>b.innerText.trim()+':'+getComputedStyle(b).backgroundColor)"))
    pg.query_selector('.sheet-midtabs').screenshot(path=S+'r9-midtab-pills-werewolf.png')
''')
