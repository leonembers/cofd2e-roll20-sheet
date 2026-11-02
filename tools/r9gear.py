exec('\n'.join(open('/workspace/cofd/roll20/tools/r7shot.py').read().split('\n')[:10])+r'''
    go(pg,'werewolf2',page='1',w=1000)
    pg.evaluate("""()=>setAttrs({'repeating_merits_-m1_merit_name':'Fast Reflexes','repeating_merits_-m1_mcat':'Physical','repeating_merits_-m1_merit':'2',
      'repeating_merits_-m2_merit_name':'Kung Fu','repeating_merits_-m2_mcat':'Physical','repeating_merits_-m2_mstyle':'1','repeating_merits_-m2_merit':'3',
      'repeating_merits_-m3_merit_name':'Totem','repeating_merits_-m3_mcat':'Splat','repeating_merits_-m3_merit':'1',
      'repeating_weapons_-w1_name':'Knife','repeating_weapons_-w2_name':'Heavy revolver with a very long custom name','repeating_weapons_-w2_wtype':'ranged',
      'repeating_armor_-a1_name':'Kevlar weave + graphene plates','repeating_armor_-a1_ar_general':'1','repeating_armor_-a1_ar_ballistic':'3','repeating_armor_-a1_ar_def':'-1','repeating_armor_-a1_ar_desc_open':'1','repeating_armor_-a1_notes':'Custom rig.',
      strength_flag:'1',brawl_flag:'1'})""")
    pg.evaluate("()=>window.__reopen&&window.__reopen()"); pg.wait_for_timeout(1500)
    print('merits',pg.evaluate("()=>['-m1','-m2','-m3'].map(i=>__A['repeating_merits_'+i+'_mcat']+'/'+__A['repeating_merits_'+i+'_mstyle'])"), 'group ui',pg.evaluate("()=>document.querySelectorAll('label.sheet-mgroup').length"))
    pg.query_selector('.sheet-entry-section.sheet-merits').screenshot(path=S+'r9-merits.png')
    pg.click('button[name=act_midtab_weapons]'); pg.wait_for_timeout(500)
    print('weapon name widths',pg.evaluate("()=>[...document.querySelectorAll('.repeating_weapons .sheet-w-atk')].filter(b=>b.getClientRects().length).map(b=>Math.round(b.getBoundingClientRect().width))"),
          'range/clip fields',pg.evaluate("()=>document.querySelectorAll('[name=attr_range_txt],[name=attr_clip_txt]').length"))
    pg.query_selector('.sheet-mp-weapons').screenshot(path=S+'r9-weapons.png')
    pg.click('button[name=act_midtab_gear]'); pg.wait_for_timeout(500)
    pg.evaluate("()=>document.querySelector('.repcontainer[data-groupname=repeating_armor] button[name=act_ar-ballistic-inc]').click()"); pg.wait_for_timeout(300)
    print('ballistic after +',pg.evaluate("()=>__A['repeating_armor_-a1_ar_ballistic']"))
    e=pg.query_selector('.repeating_armor'); e.screenshot(path=S+'r9-armor.png')
    pg.click('button[name=act_midtab_merits]'); pg.click('button[name=act_pool_clear]'); pg.wait_for_timeout(400)
    print('after clear',pg.evaluate("()=>[__A.strength_flag,__A.brawl_flag,__A.rolltype_select,document.querySelectorAll('.sheet-rollstyle-sheet,.sheet-rollstyle-attack').length]"), 'err',pg.evaluate("()=>(window.__werr||[]).length"))
    go(pg,'werewolf2',page='1',w=1000); pg.click('button[name=act_midtab_kuruth]'); pg.wait_for_timeout(400)
    print('kuruth touchstones',pg.evaluate("()=>[...document.querySelectorAll('[name=attr_flesh_touchstone]')].filter(e=>e.getClientRects().length).map(e=>!!e.closest('.sheet-mp-kuruth'))"))
    pg.query_selector('.sheet-mp-kuruth').screenshot(path=S+'r9-kuruth.png')
''')
