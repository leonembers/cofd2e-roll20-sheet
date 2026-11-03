"""r15b: Werewolf Auspice/Tribe mid tabs, mid-tab leak fixes, merit rows (splat type, caret collapse), mid-tab tooltips."""
import re
P = '.charsheet.charsheet.charsheet.charsheet'
G = 'var(--color-game-line, #b4743a)'


def take_div(h, start):
    d = 0
    for m in re.finditer(r'<div\b|</div>', h[start:]):
        d += 1 if m.group(0) == '<div' else -1
        if d == 0:
            return start, start + m.end()
    raise ValueError


TRIBES = {  # own-words summaries (no book text)
    'blood-talons': 'Warrior tribe: they prove themselves in battle and seek out worthy foes.',
    'bone-shadows': 'Mystics and spirit-dealers who chase hidden lore and always pay their debts.',
    'hunters-in-darkness': 'Silent guardians of sacred ground who stalk their territory unseen.',
    'storm-lords': 'Driven leaders who push for excellence and take the hard decisions.',
    'iron-masters': 'Adaptable hunters of the cities who embrace change, people and technology.',
    'ghost-wolves': 'Forsaken with no tribe: they rely on their own wits and their Auspice.',
    'fire-touched': 'Pure zealots who preach the old faith and burn with conviction.',
    'ivory-claws': 'Pure tribe obsessed with bloodlines, purity and tradition.',
    'predator-kings': 'Pure tribe of savage hunters who reject the human world.',
}


def wolftabs(h, c):
    i = h.index('<div class="sheet-game-line sheet-werewolf2 sheet-wolf-block">')
    a, b = take_div(h, i)
    blk = h[a:b]
    h = h[:a] + h[b:]
    trs = re.findall(r'<div class="sheet-wolf-tr sheet-wolf-tr-[a-z-]+">.*?</div>', blk)
    assert len(trs) >= 6
    for t in trs:
        blk = blk.replace(t, '', 1)
    blk = blk.replace('<input type="hidden" class="sheet-wolf-tk" name="attr_tribe_key" value=""/>', '', 1)
    blk = blk.replace('Choose an Auspice and Tribe on Main.', 'Choose an Auspice on Main.', 1)
    summ = ''.join(f'<div class="sheet-wolf-tr sheet-wolf-tr-{k} sheet-wolf-ts">{v}</div>' for k, v in TRIBES.items())
    tribe = ('<div class="sheet-midpane sheet-mp-tribe sheet-game-line sheet-werewolf2"><div class="sheet-leon-page sheet-leon-pane"><div class="sheet-wolf-block sheet-tribe-block">'
             '<input type="hidden" class="sheet-wolf-tk" name="attr_tribe_key" value=""/>'
             '<div class="sheet-entry-section-head"><span class="sheet-subheader">Tribe: <span name="attr_tribe"></span></span></div>'
             '<div class="sheet-tribe-none">Choose a Tribe on Main.</div>' + summ + ''.join(trs) + '</div></div></div>')
    ausp = ('<div class="sheet-midpane sheet-mp-auspice sheet-game-line sheet-werewolf2"><div class="sheet-leon-page sheet-leon-pane">' + blk + '</div></div>')
    r = h.index('<div class="sheet-midpane sheet-mp-rituals')
    h = h[:r] + ausp + tribe + h[r:]
    btn = ('<button type="action" class="sheet-midtab-btn sheet-mt-auspice sheet-game-line sheet-werewolf2" name="act_midtab_auspice" title="x">Auspice</button>'
           '<button type="action" class="sheet-midtab-btn sheet-mt-tribe sheet-game-line sheet-werewolf2" name="act_midtab_tribe" title="x">Tribe</button>')
    k = h.index('<button type="action" class="sheet-midtab-btn sheet-mt-rites')
    h = h[:k] + btn + h[k:]
    h, n = re.subn(r'(\["merits","powers",[^\]]*)\]\.forEach\(', r'\1,"auspice","tribe"].forEach(', h, 1)
    assert n == 1
    c += '\n'.join([
        f'{P} input.sheet-midtab[value="auspice"] ~ .sheet-midpane.sheet-mp-auspice, {P} input.sheet-midtab[value="tribe"] ~ .sheet-midpane.sheet-mp-tribe {{ display: block !important; }}',
        f'{P} input.sheet-midtab[value="auspice"] + .sheet-midtabs button.sheet-mt-auspice, {P} input.sheet-midtab[value="tribe"] + .sheet-midtabs button.sheet-mt-tribe {{ opacity: 1; background-color: rgba(160,40,40,.28) !important; border-color: #b06a3a !important; }}',
        f'{P} .sheet-tribe-block input.sheet-wolf-tk:not([value=""]) ~ .sheet-tribe-none {{ display: none !important; }}',
        f'{P} .sheet-tribe-block .sheet-wolf-ts {{ font-style: italic; margin: 4px 0 6px; display: none !important; }}',
    ] + [f'{P} .sheet-tribe-block input.sheet-wolf-tk[value="{k}"] ~ .sheet-wolf-ts.sheet-wolf-tr-{k} {{ display: block !important; }}' for k in TRIBES] + [
    ]) + '\n'
    return h, c


def midaudit(h, c):
    tabs = ['rites', 'totem', 'devotions', 'frenzy', 'rituals', 'kuruth', 'auspice', 'tribe']
    sel = ', '.join(f'{P} input.sheet-midtab[value="{t}"] ~ .sheet-midtabs + .sheet-columns' for t in tabs)
    c += '\n'.join([
        f'{sel} {{ display: none !important; }}',
        # homebrew: the Powers tab already holds every section, so the pseudo tabs would only repeat it
        ', '.join(f'.charsheet:has(input.sheet-type[value="homebrew"]) .sheet-midtabs button.sheet-mt-{t}' for t in ('rites', 'totem', 'devotions', 'auspice', 'tribe')) + ' { display: none !important; }',
        f'{P} input.sheet-midtab[value="devotions"] ~ .sheet-midpane.sheet-mp-powers .sheet-vamp-banes {{ display: none !important; }}',
    ]) + '\n'
    return h, c


SPLAT = {'mortal2': 'Mortal', 'vampire2': 'Vampire', 'werewolf2': 'Werewolf', 'mage2': 'Mage', 'promethean2': 'Promethean',
         'changeling2': 'Changeling', 'hunter2': 'Hunter', 'geist2': 'Geist', 'mummy2': 'Mummy', 'demon': 'Demon', 'beast': 'Beast',
         'deviant-the-renegades': 'Deviant', 'breeds2': 'Breed', 'homebrew': 'Supernatural'}


def merits(h, c):
    i = h.index('<fieldset class="repeating_merits">'); j = h.index('</fieldset>', i); f = h[i:j]
    sh = '<input type="text" class="sheet-entry-short" name="attr_short_desc" placeholder="short description" title="One-line summary (shown on the collapsed row and in chat)" />'
    assert sh in f
    f = f.replace(sh, '', 1)
    f = f.replace('<option value="Supernatural">Supernatural</option>', '<option value="Supernatural">Splat (Werewolf, Vampire...)</option>', 1)
    h = h[:i] + f + h[j:]
    E = f'{P}{P} .sheet-entry'
    T = f'{E} > input.sheet-entry-toggle'
    X = ':not(.sheet-ar-x)'
    rules = [
        # generic reliable collapse (armor pattern) for every repeating entry
        f'{E} > input.sheet-entry-toggle:not(:checked) ~ .sheet-entry-body {{ display: none !important; }}',
        # visible caret on every entry that uses the top-level toggle
        f'{T} {{ -webkit-appearance: none !important; appearance: none !important; position: absolute !important; left: 2px !important; top: 5px !important; width: 12px !important; height: 12px !important; '
        f'min-width: 0 !important; margin: 0 !important; padding: 0 !important; opacity: 1 !important; z-index: 3 !important; cursor: pointer !important; border: none !important; background: none !important; display: block !important; }}',
        f'{T}::before {{ content: ""; position: absolute; left: 3px; top: 2px; width: 5px; height: 5px; border-right: 1.5px solid {G}; border-bottom: 1.5px solid {G}; transform: rotate(-45deg); transition: transform .15s; }}',
        f'{T}:checked::before {{ transform: rotate(45deg); }}',
        f'{E}:has(> input.sheet-entry-toggle) {{ position: relative !important; }}',
        f'{E} > input.sheet-entry-toggle + .sheet-entry-head {{ padding-left: 15px !important; }}',
        # empty short description: hidden on the collapsed row
        f'{E} > .sheet-entry-head > input.sheet-entry-short:placeholder-shown {{ display: none !important; }}',
        # merit rows: tight, type pill fits its text
        f'{P} .repcontainer[data-groupname="repeating_merits"] .sheet-entry-head {{ min-height: 0 !important; padding-top: 1px !important; padding-bottom: 1px !important; flex-wrap: nowrap !important; }}',
        f'{P} .repcontainer[data-groupname="repeating_merits"] .sheet-entry {{ margin: 0 !important; padding-top: 0 !important; padding-bottom: 0 !important; }}',
        f'{P}{P} .sheet-entry-head .sheet-mcat-badge {{ width: auto !important; max-width: none !important; min-width: 0 !important; overflow: visible !important; white-space: nowrap !important; padding: 0 6px !important; flex: 0 0 auto !important; box-sizing: content-box !important; height: auto !important; line-height: 13px !important; }}',
        f'{E} label.sheet-switch {{ display: inline-flex !important; align-items: center !important; gap: 5px !important; }}',
        f'{E} label.sheet-switch > input {{ position: absolute !important; opacity: 0 !important; width: 1px !important; height: 1px !important; margin: 0 !important; }}',
        f'{E} label.sheet-switch > .sheet-sw-track {{ display: inline-block !important; position: relative !important; width: 28px !important; height: 14px !important; border-radius: 7px !important; background: #666 !important; }}',
        f'{E} label.sheet-switch > .sheet-sw-track::after {{ content: ""; position: absolute; left: 2px; top: 2px; width: 10px; height: 10px; border-radius: 50%; background: #fff; transition: left .15s; }}',
        f'{E} label.sheet-switch > input:checked + .sheet-sw-track {{ background: {G} !important; }}',
        f'{E} label.sheet-switch > input:checked + .sheet-sw-track::after {{ left: 16px; }}',
        f'{P} .sheet-entry > input.sheet-mcat-flag[value="Supernatural"] ~ .sheet-entry-head .sheet-mcat-badge {{ font-size: 0 !important; letter-spacing: 0 !important; }}',
    ]
    for k, v in SPLAT.items():
        rules.append(f'.charsheet:has(input.sheet-type[value="{k}"]) .sheet-entry > input.sheet-mcat-flag[value="Supernatural"] ~ .sheet-entry-head .sheet-mcat-badge::after {{ content: "{v}"; font-size: 9px; line-height: 13px; letter-spacing: .4px; display: inline-block; }}')
    c += '\n'.join(rules) + '\n'
    return h, c


TIPS = {
    'weapons': 'Weapons: attack entries, damage and pools',
    'gear': 'Gear: armor, equipment and Expanded Merits',
    'merits': 'Merits: your Merits, dots and dice pools',
    'powers': 'Powers: your splat powers, pools and costs',
    'auspice': 'Auspice: ability, Moon Gift and facets',
    'tribe': 'Tribe: your tribe, its theme and Gift affinities',
    'rites': 'Rites: Werewolf rites, pools and effects',
    'totem': 'Totem: your pack totem and its traits',
    'kuruth': 'Kuruth: Touchstones, triggers and Death Rage',
    'devotions': 'Devotions: Devotions, rites and Vinculum',
    'frenzy': 'Frenzy: Touchstones, Frenzy rolls and Banes',
    'rituals': 'Rituals: Cruac and Theban Sorcery rituals',
}


def tooltips(h, c):
    def fix(m):
        t = m.group(2)
        tag = re.sub(r'\stitle="[^"]*"', '', m.group(0))
        return tag[:-1] + f' title="{TIPS[t]}">' if t in TIPS else m.group(0)
    h, n = re.subn(r'<button type="action" class="sheet-midtab-btn sheet-mt-([a-z]+)([^"]*)"[^>]*>',
                   lambda m: fix(type('M', (), {'group': lambda s, k: m.group(0) if k == 0 else m.group(1)})()), h)
    for v in TIPS.values():
        assert len(v) < 60 and v.isascii()
    return h, c


LOCK = 'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@014361730d569cc5ea0bab7170aaf905b2e79735/icons/lock/lock.svg'
AREN = {'Rahu': 'Purity', 'Cahalith': 'Glory', 'Elodoth': 'Honor', 'Ithaeur': 'Wisdom', 'Irraka': 'Cunning'}


def giftrows(h, c):
    pat = re.compile(r'<div class="sheet-entry-head">(<button type="roll" class="sheet-entry-post" name="(roll_mgf_\w+?)_post"[^>]*>)<span class="sheet-entry-name">([^<]*)</span></button>'
                     r'<span class="sheet-mgf-lock" title="([^"]*)">locked</span><span class="sheet-mgf-dots" title="([^"]*)"><span class="(sheet-ren-ic sheet-ren-\w+)"></span>\w+ (\d)</span>'
                     r'<span class="sheet-entry-pool">([^<]*)</span>(<button type="action" class="sheet-entry-roll sheet-was-roll"\s+title="([^"]*)" name="(act_rr_mgf_\w+)">&#127922;</button>)?'
                     r'<span class="sheet-entry-short sheet-mgf-short">([^<]*)</span><span class="sheet-entry-cost">([^<]*)</span></div><div class="sheet-entry-body">')

    def rep(m):
        post, nm, lt, dt, ric, n, pool, rb, rt, ract, short, cost = m.group(1), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7), m.group(8), m.group(9), m.group(10), m.group(11), m.group(12), m.group(13)
        sc = cost.replace('Essence', 'Ess').replace('Willpower', 'WP')
        if rb:
            name = f'<button type="action" class="sheet-entry-post sheet-mgf-rollname" name="{ract}" title="{rt}"><span class="sheet-entry-name">{nm}</span></button>'
            extra = post + 'Post to chat</button>'
        else:
            name = post + f'<span class="sheet-entry-name">{nm}</span></button>'
            extra = ''
        return (f'<div class="sheet-entry-head"><span class="sheet-mgf-nm">{name}<span class="sheet-mgf-lock" title="{lt}"></span></span>'
                f'<span class="sheet-entry-cost sheet-mgf-cost" title="{cost}">{sc}</span>'
                f'<span class="sheet-mgf-dots" title="{dt}"><span class="{ric}"></span>{n}</span><span class="sheet-entry-pool">{pool}</span></div>'
                f'<div class="sheet-entry-body"><div class="sheet-mgf-short">{short}</div>' + (f'<div class="sheet-mgf-postrow">{extra}</div>' if extra else ''))
    h, n = pat.subn(rep, h)
    assert n >= 20, n
    assert 'locked</span>' not in h
    # Auspice Renown symbol beside the Auspice (Main header and Auspice tab)
    badge = '<input type="hidden" class="sheet-ren-flag" name="attr_auspice_ren" value="" /><span class="sheet-ren-ic sheet-ren-badge sheet-ausp-ren" title="Auspice Renown"></span>'
    s = '<select class="sheet-game-line sheet-werewolf2 sheet-wolf-sel" name="attr_auspice">'
    i = h.index(s); j = h.index('</select>', i) + 9
    h = h[:j] + badge + h[j:]
    s2 = '<span class="sheet-subheader">Auspice &amp; Moon Gift</span>'
    assert s2 in h
    h = h.replace(s2, '<span class="sheet-subheader">Auspice &amp; Moon Gift</span>' + badge, 1)
    js = ('        const R15_AREN = ' + repr(AREN).replace("'", '"') + ';\n'
          '        const r15Aren = () => getAttrs(["auspice"], v => setAttrs({auspice_ren: R15_AREN[(v.auspice || "").trim()] || ""}, {silent: true}));\n'
          '        on("change:auspice sheet:opened", r15Aren);\n')
    k = h.index('<script type="text/worker">') + len('<script type="text/worker">')
    h = h[:k] + '\n' + js + h[k:]
    M = f'{P}{P} .sheet-mgx .sheet-mgf'
    c += '\n'.join([
        f'{M} > .sheet-entry-head {{ display: flex !important; flex-wrap: nowrap !important; align-items: center !important; gap: 8px !important; grid-template-columns: none !important; min-height: 0 !important; padding-top: 1px !important; padding-bottom: 1px !important; }}',
        f'{M} > .sheet-entry-head > * {{ grid-row: auto !important; grid-column: auto !important; margin: 0 !important; }}',
        f'{M} .sheet-mgf-nm {{ position: relative !important; display: inline-flex !important; flex: 0 0 auto !important; min-width: 140px !important; }}',
        f'{M} .sheet-mgf-nm > button {{ width: 100% !important; text-align: left !important; cursor: pointer !important; }}',
        f'{M} .sheet-mgf-lock {{ position: absolute !important; right: 3px !important; top: 50% !important; transform: translateY(-50%); width: 12px !important; height: 12px !important; padding: 0 !important; border: none !important; border-radius: 0 !important; '
        f'font-size: 0 !important; background: url("{LOCK}") center / 12px 12px no-repeat !important; opacity: .9 !important; pointer-events: none; }}',
        f'{M} .sheet-mgf-cost, {M} .sheet-mgf-dots, {M} > .sheet-entry-head > .sheet-entry-pool {{ flex: 0 0 auto !important; white-space: nowrap !important; font-size: 12px !important; }}',
        f'{M} .sheet-mgf-dots {{ display: inline-flex !important; align-items: center !important; gap: 2px !important; }}',
        f'{M} .sheet-mgf-short {{ font-style: italic; margin: 0 0 3px !important; }}',
        f'{M} > .sheet-entry-body {{ padding-top: 2px !important; padding-bottom: 2px !important; gap: 2px !important; }}',
        f'{M} .sheet-mgf-postrow > button {{ font-size: 11px !important; padding: 1px 8px !important; }}',
        f'{P} span.sheet-ausp-ren {{ margin-left: 4px !important; }}',
    ]) + '\n'
    return h, c


def beats(h, c):
    X = f'{P}{P} .sheet-input-group:has(> .sheet-xp-beats)'
    c += '\n'.join([
        f'{X} {{ justify-content: flex-start !important; column-gap: 0 !important; }}',
        f'{X} > span:first-child {{ flex: 0 0 auto !important; width: auto !important; }}',
        f'{X} > .sheet-xp-beats {{ margin: 0 0 0 12px !important; justify-content: flex-start !important; gap: 2px !important; flex: 0 0 auto !important; width: auto !important; max-width: 90px !important; }}',
        f'{X} > .sheet-xp-beats > * {{ flex: 0 0 14px !important; width: 14px !important; height: 14px !important; margin: 0 !important; padding: 0 !important; }}',
        f'{X} > .sheet-xp-beats button {{ width: 14px !important; height: 14px !important; min-width: 0 !important; margin: 0 !important; }}',
    ]) + '\n'
    return h, c


def rituals(h, c):
    i = h.index('<fieldset class="repeating_rituals">'); j = h.index('</fieldset>', i); f = h[i:j]
    f = f.replace('<div class="sheet-rit"><div class="sheet-rit-top">', '<div class="sheet-rit sheet-entry"><input type="checkbox" class="sheet-entry-toggle" name="attr_show" value="1" title="Expand / collapse" /><div class="sheet-rit-top">', 1)
    f = f.replace('<div class="sheet-rit-bot">', '<div class="sheet-rit-bot sheet-entry-body">', 1)
    assert 'sheet-entry-toggle' in f and 'sheet-entry-body' in f
    h = h[:i] + f + h[j:]
    c += f'{P}{P} .sheet-rit.sheet-entry > .sheet-rit-top {{ padding-left: 15px !important; }}\n'
    return h, c


def splitgifts(h, c):
    a = h.index('<div class="sheet-entry-section sheet-gifts sheet-pw">')
    a0, a1 = take_div(h, a)
    s = h[a0:a1]
    s = re.sub(r'<select class="sheet-gfilt".*?</select>', '', s, 1, re.S)
    sh = s.replace('<span data-i18n="gifts">Gifts</span>', '<span>Shadow Gifts</span>', 1).replace('<option value="Shadow">', '<option value="Shadow" selected>', 1)
    w = s.replace('<span data-i18n="gifts">Gifts</span>', '<span>Wolf Gifts</span>', 1).replace('<option value="Wolf">', '<option value="Wolf" selected>', 1)
    w = w.replace('class="sheet-entry-section sheet-gifts sheet-pw"', 'class="sheet-entry-section sheet-gifts sheet-wgifts sheet-pw"', 1)
    w = w.replace('repeating_gifts', 'repeating_wgifts')
    w = re.sub(r'name="act_([a-z_]*?)gifts\b', r'name="act_\1wgifts', w)
    assert 'repeating_wgifts' in w and 'Wolf Gifts' in w and 'Shadow Gifts' in sh
    h = h[:a0] + sh + w + h[a1:]
    k = h.index('<script type="text/worker">'); e = h.index('</script>', k)
    js = h[k:e]
    js = js.replace('"gifts", "', '"gifts", "wgifts", "')
    js = re.sub(r'"gifts": (\[[^\]]*\]|"[^"]*")', lambda m: m.group(0) + ', "wgifts": ' + m.group(1).replace('"Gifts"', '"Wolf Gifts"'), js)
    mig = r'''
        // r15: Gifts split into Shadow (repeating_gifts) and Wolf (repeating_wgifts); move rows by their Gift type
        const R15_GA = ["name", "gtype", "facet", "renown", "rating", "cost", "action", "source", "description", "notes", "short_desc", "pool", "pool_dice", "pp_attr", "pp_skill", "pp_mod", "cost_wp", "cost_pw", "cost_auto", "o_dramatic", "o_failure", "o_success", "o_exceptional", "show"];
        let r15GBusy = false;
        const r15MoveGifts = () => { if (r15GBusy) return; r15GBusy = true; let left = 2; const done = () => { if (--left === 0) r15GBusy = false; }; ["gifts", "wgifts"].forEach(src => getSectionIDs(src, ids => {
            const dst = src === "gifts" ? "wgifts" : "gifts", want = src === "gifts" ? "Wolf" : "Shadow";
            getAttrs(ids.flatMap(id => R15_GA.map(a => `repeating_${src}_${id}_${a}`)), v => {
                const out = {}; const gone = [];
                ids.forEach(id => { if ((v[`repeating_${src}_${id}_gtype`] || "") !== want) return;
                    const nid = generateRowID(); R15_GA.forEach(a => { const x = v[`repeating_${src}_${id}_${a}`]; if (x !== undefined && x !== "") out[`repeating_${dst}_${nid}_${a}`] = x; }); gone.push(id); });
                gone.forEach(id => removeRepeatingRow(`repeating_${src}_${id}`));
                if (gone.length) setAttrs(out, {silent: true}, done); else done();
            });
        })); };
        on("sheet:opened change:repeating_gifts:gtype change:repeating_wgifts:gtype", r15MoveGifts);
'''
    js = js.replace('<script type="text/worker">', '<script type="text/worker">' + mig, 1)
    h = h[:k] + js + h[e:]
    add = []
    for m in re.finditer(r'[^{}]*repeating_gifts[^{}]*\{[^}]*\}', c):
        add.append(m.group(0).strip().replace('repeating_gifts', 'repeating_wgifts'))
    c += '\n'.join(add) + '\n'
    c += f'{P} input.sheet-midtab[value="powers"] ~ .sheet-midpane.sheet-mp-powers .sheet-entry-section.sheet-wgifts {{ margin-top: 4px !important; }}\n'
    return h, c


def cardfix(h, c):
    i = h.index('<rolltemplate class="sheet-rolltemplate-cofd-entry">'); j = h.index('</rolltemplate>', i); t = h[i:j]
    mod = '{{#f_mod}}<tr><th>Modifier</th><td>{{f_mod}}</td></tr>{{/f_mod}}'
    wnd = '{{#f_wounds}}<tr><th>Penalties</th><td>{{f_wounds}}</td></tr>{{/f_wounds}}'
    assert t.count(mod) == 1 and t.count(wnd) == 1
    t = t.replace(wnd, '{{#^f_mod}}' + wnd + '{{/^f_mod}}', 1)
    t = t.replace(mod, '{{#f_mod}}<tr><td colspan="2" class="sheet-ce-mp"><span class="sheet-ce-mpi"><span class="sheet-ce-mpl">Modifier</span> {{f_mod}}</span>'
                  '{{#f_wounds}}<span class="sheet-ce-mpi"><span class="sheet-ce-mpl">Penalties</span> {{f_wounds}}</span>{{/f_wounds}}</td></tr>{{/f_mod}}', 1)
    h = h[:i] + t + h[j:]
    R = '.sheet-rolltemplate-cofd-entry'
    c += '\n'.join([
        f'{R} td.sheet-ce-mp {{ text-align: center !important; padding: 2px 4px !important; }}',
        f'{R} .sheet-ce-mpi {{ display: inline-block; margin: 0 8px; white-space: nowrap; }}',
        f'{R} .sheet-ce-mpl {{ font: 10px Arial, sans-serif; letter-spacing: 1px; text-transform: uppercase; color: #b08a3a; margin-right: 3px; }}',
        f'{R} .sheet-ce-rn {{ align-items: center !important; }}',
        f'{R} .sheet-ce-rn .sheet-ce-sl {{ line-height: 1 !important; align-self: center !important; }}',
        f'{R} .sheet-ce-head {{ display: flex !important; flex-wrap: wrap !important; align-items: baseline !important; column-gap: 6px !important; }}',
        f'{R} .sheet-ce-head > .sheet-ce-char {{ order: 0; flex: 0 1 auto; margin-right: auto !important; display: inline-block !important; }}',
        f'{R} .sheet-ce-head > .sheet-ce-name {{ order: 1; flex: 0 1 auto; text-align: right; }}',
        f'{R} .sheet-ce-head > * {{ order: 2; }}',
        f'{R} .sheet-ce-head > .sheet-ce-kind {{ order: 3; flex: 0 0 100%; text-align: right; }}',
    ]) + '\n'
    return h, c


# (97) same order as the left Renown panel
REN = [('pur', 'Purity', '#9ac3cd'), ('glo', 'Glory', '#efbb4a'), ('hon', 'Honor', '#c4af90'), ('wis', 'Wisdom', '#ae8fcd'), ('cun', 'Cunning', '#db8f3d')]  # sampled from the Renown panel icons (icons/renown/*.png)
REN_URL = 'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@91c021fee3f302f9f895454d1d06c355c48164e3/icons/renown/{}.png'
LOCK_URL = 'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@014361730d569cc5ea0bab7170aaf905b2e79735/icons/lock/lock.svg'
ATTRS = ['intelligence', 'wits', 'resolve', 'strength', 'dexterity', 'stamina', 'presence', 'manipulation', 'composure']
SKILLS = ['academics', 'computer', 'crafts', 'investigation', 'medicine', 'occult', 'politics', 'science', 'athletics', 'brawl', 'drive', 'firearms', 'larceny', 'stealth', 'survival', 'weaponry', 'animalken', 'empathy', 'expression', 'intimidation', 'persuasion', 'socialize', 'streetwise', 'subterfuge']


def _opts(xs):
    return '<option value="" selected>-</option>' + ''.join(f'<option value="{x}">{"Animal Ken" if x == "animalken" else x.title()}</option>' for x in xs)


def gift_row(gt):
    lines = ''.join(
        f'<input type="hidden" class="sheet-gf-on" name="attr_f_{k}_on" value="0" />'
        f'<button type="action" class="sheet-gf-line sheet-gf-{k}" name="act_froll_{k}" title="{n} Facet: click to roll">'
        f'<span class="sheet-gf-ic"></span><span class="sheet-gf-nm" name="attr_f_{k}_name"></span><span class="sheet-gf-q">???</span><span class="sheet-gf-lock"></span></button>'
        for k, n, _ in REN)
    def stp(lab, nm, lo, hi):
        return f'<label class="sheet-gfn">{lab}<input type="number" name="attr_f_{nm}" value="0" min="{lo}" max="{hi}" /></label>'
    facets = ''.join(
        f'<div class="sheet-gfx sheet-gf-{k}"><input type="checkbox" class="sheet-gfx-tg" name="attr_f_{k}_show" value="1" title="Show Facet details" />'
        f'<div class="sheet-gfx-top"><input type="checkbox" class="sheet-gfx-sw" name="attr_f_{k}_on" value="1" title="Learned" />'
        f'<span class="sheet-gf-ic"></span><input type="text" class="sheet-gfx-nm" name="attr_f_{k}_name" placeholder="{n} Facet" /></div>'
        f'<div class="sheet-gfx-body"><textarea name="attr_f_{k}_desc" placeholder="Description"></textarea>'
        f'<div class="sheet-gfx-r"><input type="text" name="attr_f_{k}_action" placeholder="Action / duration" /><input type="text" name="attr_f_{k}_dur" placeholder="Duration" /><input type="text" name="attr_f_{k}_src" placeholder="Source / page" /></div>'
        f'<div class="sheet-gfx-r">{stp("Cost", k + "_cost", 0, 20)}<select class="sheet-gfx-ct" name="attr_f_{k}_ctype" title="Cost type"><option value="Essence" selected>Ess</option><option value="Willpower">WP</option><option value="None">None</option></select>{stp("Mod", k + "_mod", -10, 10)}'
        f'<label class="sheet-gfn" title="Add {n} to the pool"><input type="checkbox" class="sheet-gfx-sw" name="attr_f_{k}_addren" value="1" checked />+{n}</label></div>'
        f'<div class="sheet-gfx-r"><select name="attr_f_{k}_attr" title="Attribute">{_opts(ATTRS)}</select><select name="attr_f_{k}_skill" title="Skill">{_opts(SKILLS)}</select></div>'
        f'<textarea class="sheet-gfx-o" name="attr_f_{k}_oexc" placeholder="Exceptional success effect"></textarea><textarea class="sheet-gfx-o" name="attr_f_{k}_osucc" placeholder="Success effect"></textarea>'
        f'<textarea class="sheet-gfx-o" name="attr_f_{k}_ofail" placeholder="Failure effect"></textarea><textarea class="sheet-gfx-o" name="attr_f_{k}_odram" placeholder="Dramatic failure effect"></textarea>'
        f'</div></div>' for k, n, _ in REN)
    return (f'<div class="sheet-gift"><input type="checkbox" class="sheet-gift-tg" name="attr_show" value="1" title="Expand / collapse" />'
            f'<input type="hidden" name="attr_gtype" value="{gt}" /><input type="hidden" name="attr_gv" value="" />'
            f'<input type="text" class="sheet-gift-nm" name="attr_name" placeholder="Gift name" />'
            f'<div class="sheet-gift-lines">{lines}</div>'
            f'<div class="sheet-gift-body">{facets}<textarea class="sheet-gift-notes" name="attr_notes" placeholder="Gift notes"></textarea></div></div>')


def giftgrid(h, c):
    for sec, gt in (('gifts', 'Shadow'), ('wgifts', 'Wolf')):
        i = h.index(f'<fieldset class="repeating_{sec}">') + len(f'<fieldset class="repeating_{sec}">')
        j = h.index('</fieldset>', i)
        h = h[:i] + gift_row(gt) + h[j:]
    k = h.index('<script type="text/worker">'); e = h.index('</script>', k); js = h[k:e]
    a = js.index('        // r15: Gifts split'); b = js.index('r15MoveGifts);', a) + len('r15MoveGifts);')
    js = js[:a] + WORKER + js[b:]
    h = h[:k] + js + h[e:]
    G = f'{P}{P} .sheet-gifts'
    css = [
        f'{G} .repcontainer {{ display: flex !important; flex-wrap: wrap !important; gap: 4px !important; container-type: inline-size; }}',
        f'{G} .repcontainer > .repitem {{ flex: 0 0 auto !important; margin: 0 !important; padding: 0 !important; max-width: 100% !important; }}',
        f'{G} .sheet-gift {{ position: relative; box-sizing: border-box; width: 172px; width: calc((100cqw - 5px) / 2); border: 1px solid var(--splat, #c8732a); border-radius: 5px; padding: 3px 3px 3px 15px; background: rgba(0,0,0,.25); }}',
        f'{G} .sheet-gift:has(> .sheet-gift-tg:checked), {G} .sheet-gift-tg:checked ~ .sheet-gift-body {{ }}',
        f'{G} .sheet-gift-tg {{ appearance: none; position: absolute; left: 2px; top: 5px; width: 12px; height: 12px; margin: 0; cursor: pointer; z-index: 2; }}',
        f'{G} .sheet-gift-tg::before {{ content: ">"; display: block; color: var(--splat, #c8732a); font: bold 12px Arial, sans-serif; line-height: 12px; text-align: center; }}',
        f'{G} .sheet-gift-tg:checked::before {{ transform: rotate(90deg); }}',
        f'{G} .sheet-gift-nm {{ width: 100% !important; box-sizing: border-box; font: 700 13px "Sorts Mill Goudy", serif !important; background: none !important; border: 0 !important; border-bottom: 1px solid rgba(255,255,255,.15) !important; padding: 0 2px !important; margin: 0 0 3px !important; height: 18px !important; color: inherit; }}',
        f'{G} .sheet-gift-lines {{ display: flex; flex-direction: column; gap: 2px; }}',
        f'{G} .sheet-gift-body {{ display: none; margin-top: 4px; }}',
        f'{G} .sheet-gift-tg:checked ~ .sheet-gift-body {{ display: block; }}',
        f'{G} .sheet-gift-tg:checked ~ .sheet-gift-lines {{ display: none; }}',
        f'{G} .sheet-gf-line {{ position: relative; display: flex !important; align-items: center; justify-content: center; gap: 3px; width: 100%; min-height: 18px; margin: 0 !important; padding: 1px 3px !important; border: 1px solid var(--ren) !important; border-radius: 3px !important; background: rgba(0,0,0,.3) !important; color: #e8e2d4 !important; font: 700 11px "Sorts Mill Goudy", serif !important; text-transform: none !important; cursor: pointer; overflow: hidden; white-space: nowrap; box-shadow: none !important; }}',
        f'{G} .sheet-gf-ic {{ flex: 0 0 14px; width: 14px; height: 14px; background-size: 14px 14px; background-position: center; background-repeat: no-repeat; }}',
        f'{G} .sheet-gf-nm {{ overflow: hidden; text-overflow: ellipsis; }}',
        f'{G} .sheet-gf-q, {G} .sheet-gf-lock {{ display: none; }}',
        f'{G} input.sheet-gf-on:not([value="1"]) + .sheet-gf-line {{ pointer-events: none; cursor: default; opacity: .75; }}',
        f'{G} input.sheet-gf-on:not([value="1"]) + .sheet-gf-line .sheet-gf-nm {{ display: none; }}',
        f'{G} input.sheet-gf-on:not([value="1"]) + .sheet-gf-line .sheet-gf-q {{ display: inline; color: #9a948a; }}',
        f'{G} input.sheet-gf-on:not([value="1"]) + .sheet-gf-line .sheet-gf-ic {{ filter: grayscale(1); opacity: .45; }}',
        f'{G} input.sheet-gf-on:not([value="1"]) + .sheet-gf-line .sheet-gf-lock {{ display: block; position: absolute; right: 3px; top: 50%; margin-top: -5px; width: 10px; height: 10px; background: url("{LOCK_URL}") center / 10px 10px no-repeat; opacity: .8; }}',
        f'{G} .sheet-gfx {{ position: relative; border: 1px solid var(--ren); border-radius: 3px; padding: 2px 3px 2px 15px; margin-bottom: 2px; }}',
        f'{G} .sheet-gfx-tg {{ appearance: none; position: absolute; left: 2px; top: 4px; width: 11px; height: 11px; margin: 0; cursor: pointer; }}',
        f'{G} .sheet-gfx-tg::before {{ content: ">"; display: block; color: var(--ren); font: bold 11px Arial, sans-serif; line-height: 11px; text-align: center; }}',
        f'{G} .sheet-gfx-tg:checked::before {{ transform: rotate(90deg); }}',
        f'{G} .sheet-gfx-top {{ display: flex; align-items: center; gap: 4px; }}',
        f'{G} .sheet-gfx-nm {{ flex: 1 1 auto; min-width: 0; height: 18px !important; padding: 0 3px !important; margin: 0 !important; font: 700 12px "Sorts Mill Goudy", serif !important; }}',
        f'{G} .sheet-gfx-body {{ display: none; padding-top: 3px; }}',
        f'{G} .sheet-gfx-tg:checked ~ .sheet-gfx-body {{ display: flex; flex-direction: column; gap: 3px; }}',
        f'{G} .sheet-gfx-body textarea {{ width: 100% !important; box-sizing: border-box; min-height: 40px; height: 44px; margin: 0 !important; font-size: 12px; }}',
        f'{G} .sheet-gfx-r {{ display: flex; flex-wrap: nowrap; gap: 4px; align-items: center; }}',
        f'{G} .sheet-gfx-r > input[type="text"], {G} .sheet-gfx-r > select {{ flex: 1 1 0; min-width: 0; width: auto !important; height: 20px !important; margin: 0 !important; padding: 0 3px !important; font-size: 12px; }}',
        f'{G} .sheet-gfn {{ display: inline-flex !important; align-items: center; gap: 2px; margin: 0 !important; font: 10px Arial, sans-serif; text-transform: uppercase; white-space: nowrap; }}',
        f'{G} select.sheet-gfx-ct {{ flex: 0 0 auto !important; width: 54px !important; height: 18px !important; margin: 0 !important; padding: 0 2px !important; font-size: 11px; }}',
        f'{G} .sheet-gfn input[type="number"] {{ width: 34px !important; height: 18px !important; margin: 0 !important; padding: 0 2px !important; text-align: center; }}',
        f'{G} input.sheet-gfx-sw {{ appearance: none; flex: 0 0 24px; width: 24px; height: 12px; margin: 0 !important; border-radius: 6px; background: #555; position: relative; cursor: pointer; }}',
        f'{G} input.sheet-gfx-sw::before {{ content: ""; position: absolute; left: 1px; top: 1px; width: 10px; height: 10px; border-radius: 50%; background: #ddd; transition: left .15s; }}',
        f'{G} input.sheet-gfx-sw:checked {{ background: var(--ren, var(--splat, #c8732a)); }}',
        f'{G} input.sheet-gfx-sw:checked::before {{ left: 13px; }}',
        f'{G} input.sheet-gfx-sw:not(:checked) ~ .sheet-gf-ic {{ filter: grayscale(1); opacity: .45; }}',
        f'{G} .sheet-gift-notes {{ width: 100% !important; box-sizing: border-box; height: 34px; margin: 0 !important; font-size: 12px; }}',
    ]
    c_rules = []
    for k, n, col in REN:
        c_rules.append(f'{G} .sheet-gf-{k} {{ --ren: {col}; }}')
        c_rules.append(f'{G} .sheet-gf-{k} .sheet-gf-ic {{ background-image: url("{REN_URL.format(n.lower())}"); }}')
    css = [x for x in css if '{ }' not in x]
    # expanded card spans the full row (falls back to the narrow card where :has is unsupported)
    css.append(f'{G} .repcontainer > .repitem:has(.sheet-gift-tg:checked) {{ flex-basis: 100% !important; }}')
    css.append(f'{G} .repitem:has(.sheet-gift-tg:checked) .sheet-gift {{ width: 100%; }}')
    c += '\n'.join(css + c_rules) + '\n'
    return h, c


WORKER = r'''
        // r15: one repeating row per Gift; its 5 Facets are prefixed fields f_cun_*, f_glo_*, f_hon_*, f_pur_*, f_wis_*
        const R15_RK = {Cunning: "cun", Glory: "glo", Honor: "hon", Purity: "pur", Wisdom: "wis"};
        const R15_RN = {cun: "Cunning", glo: "Glory", hon: "Honor", pur: "Purity", wis: "Wisdom"};
        const R15_OLD = ["name", "facet", "renown", "gtype", "gv", "cost", "action", "source", "description", "notes", "short_desc", "pp_attr", "pp_skill", "pp_mod", "cost_wp", "cost_pw", "o_exceptional", "o_success", "o_failure", "o_dramatic"];
        // Non-destructive: old per-Facet rows are copied into new Gift rows and flagged gv=old; nothing is deleted.
        let r15GBusy = false;
        const r15MigrateGifts = () => {
            if (r15GBusy) return; r15GBusy = true;
            getSectionIDs("gifts", gi => getSectionIDs("wgifts", wi => {
                const rows = gi.map(id => ["gifts", id]).concat(wi.map(id => ["wgifts", id]));
                const keys = []; rows.forEach(([s, id]) => { R15_OLD.forEach(a => keys.push(`repeating_${s}_${id}_${a}`)); Object.keys(R15_RN).forEach(k => keys.push(`repeating_${s}_${id}_f_${k}_name`)); });
                getAttrs(keys, v => {
                    const out = {}, byKey = {};
                    const g = (s, id, a) => v[`repeating_${s}_${id}_${a}`] || "";
                    const isOld = (s, id) => g(s, id, "gv") === "" && !!(g(s, id, "renown") || g(s, id, "facet") || g(s, id, "description") || g(s, id, "cost"));
                    rows.forEach(([s, id]) => { if (g(s, id, "gv") !== "old" && !isOld(s, id)) byKey[s + "|" + g(s, id, "name").trim().toLowerCase()] = [s, id]; });
                    rows.forEach(([s, id]) => {
                        if (!isOld(s, id)) return;
                        const dst = g(s, id, "gtype") === "Wolf" ? "wgifts" : "gifts";
                        const gift = (g(s, id, "facet") || g(s, id, "name") || "Unnamed Gift").trim();
                        const key = dst + "|" + gift.toLowerCase();
                        let tgt = byKey[key];
                        if (!tgt) { tgt = [dst, generateRowID()]; byKey[key] = tgt; const p = `repeating_${dst}_${tgt[1]}_`; out[p + "gv"] = "2"; out[p + "name"] = gift; out[p + "gtype"] = dst === "wgifts" ? "Wolf" : "Shadow"; }
                        const p = `repeating_${tgt[0]}_${tgt[1]}_`;
                        const k = R15_RK[g(s, id, "renown")];
                        const taken = k && (out[p + `f_${k}_name`] || v[p + `f_${k}_name`]);
                        const fname = g(s, id, "facet") ? g(s, id, "name") : "";
                        if (k && !taken) {
                            const f = p + `f_${k}_`;
                            Object.assign(out, {[f + "name"]: fname || R15_RN[k] + " Facet", [f + "on"]: "1", [f + "desc"]: g(s, id, "description") || g(s, id, "short_desc"), [f + "action"]: g(s, id, "action"), [f + "src"]: g(s, id, "source"),
                                [f + "ess"]: g(s, id, "cost_pw") || "0", [f + "wp"]: g(s, id, "cost_wp") || "0", [f + "cost"]: (parseInt(g(s, id, "cost_pw")) || 0) > 0 ? g(s, id, "cost_pw") : ((parseInt(g(s, id, "cost_wp")) || 0) > 0 ? g(s, id, "cost_wp") : "0"), [f + "ctype"]: (parseInt(g(s, id, "cost_pw")) || 0) > 0 ? "Essence" : ((parseInt(g(s, id, "cost_wp")) || 0) > 0 ? "Willpower" : "Essence"), [f + "mod"]: g(s, id, "pp_mod") || "0", [f + "attr"]: g(s, id, "pp_attr"), [f + "skill"]: g(s, id, "pp_skill"),
                                [f + "oexc"]: g(s, id, "o_exceptional"), [f + "osucc"]: g(s, id, "o_success"), [f + "ofail"]: g(s, id, "o_failure"), [f + "odram"]: g(s, id, "o_dramatic")});
                        } else {
                            out[p + "notes"] = ((out[p + "notes"] || "") + `\nUnplaced Facet: ${fname || gift} (${g(s, id, "renown") || "no Renown"}) ${g(s, id, "cost")} ${g(s, id, "description")}`).trim();
                        }
                        out[`repeating_${s}_${id}_gv`] = "old";
                    });
                    setAttrs(out, {silent: true}, () => { r15GBusy = false; });
                });
            }));
        };
        // r15b (23): one cost stepper + type; fill it once from the older f_*_ess / f_*_wp values (kept, never deleted)
        const r15CostMig = () => ["gifts", "wgifts"].forEach(sec => getSectionIDs(sec, ids => {
            const ks = []; ids.forEach(id => Object.keys(R15_RN).forEach(k => ["ess", "wp", "cost", "cmig"].forEach(x => ks.push(`repeating_${sec}_${id}_f_${k}_${x}`))));
            getAttrs(ks, v => { const u = {};
                ids.forEach(id => Object.keys(R15_RN).forEach(k => { const f = `repeating_${sec}_${id}_f_${k}_`; if (v[f + "cmig"] === "1") return;
                    const e = parseInt(v[f + "ess"]) || 0, w = parseInt(v[f + "wp"]) || 0;
                    if (!(parseInt(v[f + "cost"]) || 0) && (e > 0 || w > 0)) { u[f + "cost"] = String(e > 0 ? e : w); u[f + "ctype"] = e > 0 ? "Essence" : "Willpower"; }
                    u[f + "cmig"] = "1"; }));
                setAttrs(u, {silent: true}); });
        }));
        on("sheet:opened", r15CostMig);
        on("sheet:opened change:repeating_gifts:renown change:repeating_wgifts:renown change:repeating_gifts:gtype change:repeating_wgifts:gtype", r15MigrateGifts);
        // r15b: one global "Deduct costs when rolled" switch drives every power row's cost_auto flag
        const r15DedSecs = () => Object.keys(RR_FIELDS).filter(s => RR_FIELDS[s].includes("cost_auto"));
        const r15SyncDeduct = (first) => getAttrs(["deduct_auto", "deduct_mig"], gv => {
            const secs = r15DedSecs(); let left = secs.length; const all = [];
            secs.forEach(sec => getSectionIDs(sec, ids => { ids.forEach(id => all.push(`repeating_${sec}_${id}_cost_auto`)); if (--left) return;
                getAttrs(all, rv => {
                    let on1 = gv.deduct_auto === "1"; const u = {};
                    if (gv.deduct_mig !== "1") { on1 = all.some(k => rv[k] === "1"); u.deduct_auto = on1 ? "1" : "0"; u.deduct_mig = "1"; }
                    all.forEach(k => { const want = on1 ? "1" : "0"; if (rv[k] !== want) u[k] = want; });
                    setAttrs(u, {silent: true});
                });
            }));
        });
        on("sheet:opened change:deduct_auto", () => r15SyncDeduct());
        Object.keys(RR_FIELDS).forEach(sec => { if ((RR_FIELDS[sec] || []).includes("cost_auto")) on(`change:repeating_${sec}:name change:repeating_${sec}:merit_name`, () => r15SyncDeduct()); });
        const r15Fx = (v) => String(v === undefined || v === null ? "" : v).replace(/[{}\[\]|]/g, " ").replace(/\s+/g, " ").trim();
        const r15Lbl = (x) => x === "animalken" ? "Animal Ken" : x.charAt(0).toUpperCase() + x.slice(1);
        ["gifts", "wgifts"].forEach(sec => Object.keys(R15_RN).forEach(k => on(`clicked:repeating_${sec}:froll_${k}`, ev => {
            const id = (ev.sourceAttribute || ev.triggerName).split("_")[2]; const p = `repeating_${sec}_${id}_`, f = p + `f_${k}_`;
            const fl = ["name", "on", "attr", "skill", "mod", "cost", "ctype", "addren", "desc", "action", "dur", "oexc", "osucc", "ofail", "odram"];
            getAttrs([p + "name", "deduct_auto", "vitae", "willpower", "willpower_cur", "game_line", "sheettype"].concat(fl.map(x => f + x)), v => {
                if (v[f + "on"] !== "1") return;
                const ren = "renown_" + R15_RN[k].toLowerCase();
                const st = [v[f + "attr"], v[f + "skill"]].filter(Boolean); if (v[f + "addren"] !== "0") st.push(ren);
                getAttrs(st, sv => {
                    const mod = parseInt(v[f + "mod"]) || 0;
                    const dice = st.reduce((t, a) => t + (parseInt(sv[a]) || 0), 0) + mod;
                    const cn = parseInt(v[f + "cost"]) || 0, ct = v[f + "ctype"] || "Essence";
                    const ess = ct === "Essence" ? cn : 0, wp = ct === "Willpower" ? cn : 0;
                    const poolTxt = st.map(a => a === ren ? R15_RN[k] : r15Lbl(a)).join(" + ") + (mod ? (mod > 0 ? " + " : " - ") + Math.abs(mod) : "");
                    const gl = r15Fx(v.game_line) || "werewolf";
                    const kv = {charname: "@{character_name}", ["gl_" + gl]: "1", splat: gl, name: `${sec === "wgifts" ? "Wolf" : "Shadow"} Gift roll`,
                        f_title: r15Fx(v[p + "name"]) || "Gift", f_sub: r15Fx(v[f + "name"]), f_fdesc: r15Fx(v[f + "desc"]), f_fpool: st.length ? `${poolTxt} (${dice} dice)` : "",
                        f_costs: [ess ? ess + " Essence" : "", wp ? wp + " Willpower" : ""].filter(Boolean).join(" + "), f_action: r15Fx(v[f + "action"]), f_duration: r15Fx(v[f + "dur"]),
                        o_exc: r15Fx(v[f + "oexc"]), o_succ: r15Fx(v[f + "osucc"]), o_fail: r15Fx(v[f + "ofail"]), o_dram: r15Fx(v[f + "odram"])};
                    if (dice <= 0 && st.length) kv.chance = "1";
                    if (v.deduct_auto === "1" && (ess || wp)) {
                        const free = parseInt(v.willpower_cur) || 0, pool = parseInt(v.vitae) || 0;
                        if (wp > free || ess > pool) { startRoll(`&{template:cofd-entry} {{charname=@{character_name}}} {{splat=${gl}}} {{name=Gift roll}} {{f_title=${kv.f_title}}} {{f_sub=${kv.f_sub}}} {{f_short=Not activated: not enough Essence or Willpower}}`, r => finishRoll(r.rollId)); return; }
                        setAttrs({vitae: pool - ess, willpower_cur: free - wp});
                        kv.wpst = `Paid ${kv.f_costs}. Left: Willpower ${free - wp}/${parseInt(v.willpower) || 0}, Essence ${pool - ess}`;
                    }
                    let tpl = "&{template:cofd-entry}" + Object.entries(kv).filter(([a, b]) => b !== "").map(([a, b]) => ` {{${a}=${b}}}`).join("");
                    if (st.length) tpl += dice > 0 ? ` {{roll=[[{((${dice}+?{@{modifiermacro}|0}+@{wound_penalty}+@{wp_dice}+@{cond_mod}+@{spec_bonus})@{rolltype_eff}` : ` {{roll=[[{1d10cf1}>10]]}}`;
                    startRoll(tpl, r => finishRoll(r.rollId));
                });
            });
        })));
'''


def r16(h, c):
    # (17) remove per-row deduct switches; one global switch on Config
    n0 = h.count('<label class="sheet-pw-auto sheet-switch"')
    h = re.sub(r'<label class="sheet-pw-auto sheet-switch".*?</label>', '', h, flags=re.S)
    assert n0 and 'sheet-pw-auto sheet-switch' not in h
    h = h.replace('<div class="sheet-config-title">CONFIG</div>', '<div class="sheet-config-title">CONFIG</div><label class="sheet-cfg-ded" title="Power rolls automatically spend their Willpower and Essence / Vitae / pool cost"><input type="checkbox" class="sheet-cfg-sw" name="attr_deduct_auto" value="1" /><span>Deduct costs when rolled</span></label>', 1)
    assert 'attr_deduct_auto' in h
    # (16) repeating refs that only exist on spans or nowhere: give each a hidden empty default so @{x} resolves to ""
    added = 0
    def fix(m):
        nonlocal added
        f = m.group(0)
        refs = set(re.findall(r'@\{([a-z0-9_]+)\}', f))
        have = set(re.findall(r'<(?:input|select|textarea)[^>]*name="attr_([a-z0-9_]+)"', f))
        glob = GLOBAL
        miss = sorted(r for r in refs if r not in have and r not in glob)
        added += len(miss)
        if not miss: return f
        k = f.index('>', f.index('<fieldset')) + 1
        k = f.index('>', k) + 1  # after first inner tag
        return f[:k] + ''.join(f'<input type="hidden" name="attr_{r}" value="" />' for r in miss) + f[k:]
    out = re.sub(r'<fieldset class="repeating_[a-z0-9_]+">.*?</fieldset>', lambda m: m.group(0), h, flags=re.S)
    nofs = re.sub(r'<fieldset class="repeating_[a-z0-9_]+">.*?</fieldset>', '', h, flags=re.S)
    GLOBAL = set(re.findall(r'name="attr_([a-z0-9_]+)"', nofs)) | {'character_name', 'character_id'}
    h = re.sub(r'<fieldset class="repeating_[a-z0-9_]+">.*?</fieldset>', fix, out, flags=re.S)
    print('r16 hidden defaults added', added)
    # (16) Facet card rows in cofd-entry
    i = h.index('<rolltemplate class="sheet-rolltemplate-cofd-entry">'); j = h.index('</rolltemplate>', i); t = h[i:j]
    t = t.replace('</div>\n            <table>', '</div>\n            {{#f_title}}<div class="sheet-ce-ttl">{{f_title}}{{#f_sub}}<div class="sheet-ce-sub">{{f_sub}}</div>{{/f_sub}}</div>{{/f_title}}<table>'
                  '{{#f_fdesc}}<tr><th>Description</th><td>{{f_fdesc}}</td></tr>{{/f_fdesc}}{{#f_fpool}}<tr><th>Dice pool</th><td>{{f_fpool}}</td></tr>{{/f_fpool}}', 1)
    t = t.replace('{{#f_action}}<tr><th>Action</th><td>{{f_action}}</td></tr>{{/f_action}}', '{{#f_action}}<tr><th>Action</th><td>{{f_action}}</td></tr>{{/f_action}}{{#f_duration}}<tr><th>Duration</th><td>{{f_duration}}</td></tr>{{/f_duration}}', 1)
    assert 'f_fdesc' in t and 'f_duration' in t
    h = h[:i] + t + h[j:]
    R = '.sheet-rolltemplate-cofd-entry'
    S = f'{P}{P}'
    c += '\n'.join([
        f'{R} .sheet-ce-ttl {{ text-align: center; font: 700 17px "Sorts Mill Goudy", serif; padding: 4px 6px 2px; }}',
        f'{R} .sheet-ce-sub {{ font: italic 13px "Sorts Mill Goudy", serif; opacity: .85; }}',
        f'{R} .sheet-ce-out::before {{ content: "Effect: "; font-weight: 700; }}',
        f'{S} .sheet-cfg-ded {{ display: flex !important; align-items: center; justify-content: center; gap: 6px; margin: 4px auto 8px !important; font: 700 13px "Sorts Mill Goudy", serif; cursor: pointer; }}',
        f'{S} input.sheet-cfg-sw {{ appearance: none; flex: 0 0 28px; width: 28px !important; height: 14px !important; margin: 0 !important; border-radius: 7px; background: #555; position: relative; cursor: pointer; opacity: 1 !important; }}',
        f'{S} input.sheet-cfg-sw::before {{ content: ""; position: absolute; left: 1px; top: 1px; width: 12px; height: 12px; border-radius: 50%; background: #ddd; }}',
        f'{S} input.sheet-cfg-sw:checked {{ background: var(--splat, #c8732a); }}',
        f'{S} input.sheet-cfg-sw:checked::before {{ left: 15px; }}',
        f'{S} {S} select.sheet-rp-formsel, {S} {S} select.sheet-rp-formsel option {{ font-family: "Sorts Mill Goudy", "Goudy Old Style", Georgia, serif !important; font-size: 13px !important; font-weight: 700 !important; text-transform: none !important; letter-spacing: normal !important; text-align: center !important; text-align-last: center !important; }}',
    ]) + '\n'
    return h, c


def r16css(h, c):
    S = f'{P}{P}'
    c += '\n'.join([
        # (21) skill selection box: clean box only, no ring / pseudo dot / focus ring
        f'{S} .sheet-skills input[type="checkbox"], {S} .sheet-skills input[type="checkbox"]:checked, {S} .sheet-skills input[type="checkbox"]:focus {{ outline: none !important; -webkit-appearance: none !important; appearance: none !important; border-radius: 2px !important; }}',
        f'{S} .sheet-skills input[type="checkbox"]::before, {S} .sheet-skills input[type="checkbox"]::after {{ content: none !important; display: none !important; }}',
        f'{S} .sheet-skills input[type="checkbox"]:checked {{ box-shadow: none !important; }}',
        f'{S} .sheet-skills button:focus, {S} .sheet-skills button:focus-visible {{ outline: none !important; box-shadow: none !important; }}',
        # (20) Renown rows: same geometry as skill rows, all 5 dots and the border visible
        f'{S} .sheet-renown-row {{ display: flex !important; align-items: center !important; box-sizing: border-box !important; width: 100% !important; max-width: 100% !important; min-height: 18px; padding: 0 4px 0 2px !important; gap: 4px !important; overflow: visible !important; }}',
        f'{S} .sheet-renown-row > span {{ flex: 1 1 auto !important; min-width: 0 !important; display: flex; align-items: center; gap: 4px; overflow: hidden; white-space: nowrap; }}',
        f'{S} .sheet-renown-row > .sheet-dots {{ flex: 0 0 auto !important; width: auto !important; margin: 0 0 0 auto !important; padding: 0 !important; display: flex !important; flex-wrap: nowrap !important; gap: 0 !important; overflow: visible !important; }}',
        f'{S} .sheet-renown-row > .sheet-dots button.sheet-dot:not(.sheet-zero) {{ flex: 0 0 auto !important; }}',
        f'{S} .sheet-renown-row, {S} .sheet-renown-row * {{ box-sizing: border-box; }}',
        # (20) left column: every panel full column width with identical edges
        f'{S} .sheet-corporeal.sheet-skills, {S} .sheet-corporeal.sheet-skills ~ * {{ box-sizing: border-box !important; }}',
        f'{S} .sheet-corporeal.sheet-skills > div:not([class*="header"]) {{ min-height: 18px; }}',
    ]) + '\n'
    return h, c


def r22(h, c):
    k = h.index('<script type="text/worker">'); e = h.index('</script>', k); js = h[k:e]
    a = 'if (!isRe) setAttrs({rr_last_mac: mac, rr_last_expr: ex, rr_last_id: String(r.rollId), rr_used: ""}, {silent: true});'
    assert js.count(a) == 1
    js = js.replace(a, 'if (!isRe) setAttrs({rr_last_mac: mac, rr_last_base: rrBase(mac), rr_last_expr: ex, rr_last_id: String(r.rollId), rr_used: ""}, {silent: true});')
    b = 'const rrTag = '
    js = js.replace(b, '// r15b: rerolls never carry the modifier or penalties (wounds, WP dice, conditions, specialty)\n        const rrBase = (m) => { const i = m.search(/\\{\\{roll=\\[\\[/); if (i < 0) return ""; let r = m.slice(i).replace(/\\?\\{@\\{modifiermacro\\}\\|0\\}/g, "0"); ["wound_penalty", "wp_dice", "cond_mod", "spec_bonus"].forEach(x => { r = r.split("@{" + x + "}").join("0"); }); return r.replace(/\\}\\}\\s*\\{\\{[\\s\\S]*$/, "}}").replace(/^\\{\\{roll=\\[\\[\\{\\(\\(/, "{{roll=[[{((3+"); };\n        ' + b, 1)
    c1 = 'getAttrs(["rr_last_mac", "rr_last_expr", "rr_last_id", "rr_used", "willpower", "willpower_cur"]'
    assert js.count(c1) == 1
    js = js.replace(c1, 'getAttrs(["rr_last_mac", "rr_last_base", "rr_last_expr", "rr_last_id", "rr_used", "willpower", "willpower_cur"]')
    d = 'mac += ` {{roll=[[${ex}]]}} {{wpspend=1}}'
    assert js.count(d) == 1
    a1 = js.index('        // r15b: one global'); a2 = js.index('        const r15Fx', a1)
    blk = js[a1:a2]; js = js[:a1] + js[a2:] + '\n' + blk
    js = js.replace(d, 'mac += (v.rr_last_base && v.rr_last_base.indexOf("{{roll=[[{((3+") === 0 ? " " + v.rr_last_base : ` {{roll=[[${ex}]]}}`) + ` {{f_mod=0}} {{wpspend=1}}')
    h = h[:k] + js + h[e:]
    return h, c


def r24(h, c):
    S = f'{P}{P}'
    F = 'font-family: "Sorts Mill Goudy", "Goudy Old Style", Garamond, Georgia, serif !important; font-size: 13px !important; font-weight: 700 !important; text-transform: none !important; font-variant: normal !important; letter-spacing: normal !important;'
    B = 'border: 1px solid color-mix(in srgb, var(--pad, var(--pa, #888)) 78%, rgba(0,0,0,0)) !important; border-radius: 10px !important;'
    bar = f'{S} .sheet-diceroller-grid'
    c += '\n'.join([
        # (24a) one Initiative: the unused ephemeral (Finesse + Resistance) copy is hidden; the one beside Perception stays
        f'{bar} > .sheet-ephemeral.sheet-span {{ display: none !important; }}',
        # (24b) Initiative / Perception pills = skill-name font, same pill border as Spend 1 WP
        f'{bar} button.sheet-quick, {bar} button.sheet-quick span, {bar} button[name="roll_initiative"] {{ {F} }}',
        f'{bar} button.sheet-quick, {bar} button[name="roll_initiative"], {bar} > .sheet-wp-bar > label, {S} .sheet-diceroller-options button.sheet-toggle {{ {B} border-style: solid !important; border-width: 1px !important; }}',
        # (25) every mid-tab pill / sub-tab / conditions-tilts pill uses the skill-name font
        f'{S}{P} .sheet-midtabs button, {S}{P} .sheet-midtabs button span, {S}{P} .sheet-midtabs button.sheet-midtab-btn, {S}{P} label.sheet-ovbtn, {S}{P} label.sheet-ovbtn span, {S}{P} button.sheet-quick, {S}{P} button.sheet-quick span, {S} button.sheet-midtab-btn, {S} .sheet-subtabs button, {S} button[class*="subtab"], {S} button[class*="-tab-btn"], {S} .sheet-cg-tabs button, {S} button[name^="act_ctab"], {S} button[name^="act_gtab"], {S} button[name^="act_wtab"] {{ {F} }}',
    ]) + '\n'
    return h, c


def r26(h, c):
    import re
    S = f'{P}{P}'
    def box(k, w, lab, ph):
        return f'<label class="sheet-bb3-l">{lab}<textarea class="sheet-bb3-t" name="attr_{k}_{w}" placeholder="{ph}"></textarea></label>'
    n = 0
    for k, lab, nm in (('blood', 'Blood', 'Virtue'), ('bone', 'Bone', 'Vice')):
        wp = box(k, 'wp1', 'Restore 1 Willpower', 'Condition that regains one Willpower') + box(k, 'wpall', 'Fully Restore Willpower', 'Condition that regains all Willpower')
        pat = re.compile(r'<label class="sheet-bb-desc-l">[^<]*<textarea name="attr_' + k + r'_desc"[^>]*></textarea></label>')
        h, m = pat.subn('<div class="sheet-bb3">' + box(k, 'desc', 'Description', 'What it means and when it applies') + wp + '</div>', h); n += m
        pat2 = re.compile(r'(<textarea class="sheet-vv-desc" name="attr_' + k + r'_desc"[^>]*></textarea>)')
        h, m = pat2.subn(lambda mm: mm.group(1) + '<div class="sheet-game-line sheet-werewolf2 sheet-bb3 sheet-bb3-ov">' + wp + '</div>', h); n += m
        old = '{{kind=' + lab + '}} {{name=@{' + nm + '}}} {{f_description=@{' + k + '_desc}}}'
        assert old in h, old
        h = h.replace(old, old + ' {{f_wp1=@{' + k + '_wp1}}} {{f_wpall=@{' + k + '_wpall}}}')
    assert n == 4, n
    i = h.index('{{#f_description}}<div class="sheet-long">')
    h = h[:i] + '{{#f_wp1}}<div class="sheet-long"><b>Restore 1 Willpower: </b>{{f_wp1}}</div>{{/f_wp1}}{{#f_wpall}}<div class="sheet-long"><b>Fully Restore Willpower: </b>{{f_wpall}}</div>{{/f_wpall}}' + h[i:]
    F = '"Sorts Mill Goudy", "Goudy Old Style", Garamond, Georgia, serif'
    c += '\n'.join([
        f'{S} .sheet-bb3 {{ display: flex; flex-direction: column; gap: 4px; margin: 0; padding: 0; }}',
        f'{S} .sheet-ovwin .sheet-bb3-ov {{ margin-top: 4px; }}',
        f'{S} .sheet-bb3 label.sheet-bb3-l {{ display: flex !important; flex-direction: column; margin: 0 !important; padding: 0 !important; width: 100% !important; text-align: center !important; font-family: {F} !important; font-size: 12px !important; font-weight: 700 !important; text-transform: none !important; letter-spacing: normal !important; line-height: 15px; }}',
        f'{S} .sheet-bb3 textarea.sheet-bb3-t {{ display: block; width: 100% !important; box-sizing: border-box; min-height: 40px; height: 50px; margin: 1px 0 0 0 !important; padding: 3px 5px !important; resize: vertical; font-size: 12px; line-height: 15px; border-radius: 4px; }}',
        f'{S} .sheet-bb-entry .sheet-entry-body {{ padding: 4px 6px 6px !important; margin: 0 !important; }}',
        f'{S} input.sheet-type[value="werewolf2"] ~ * .sheet-ovwin textarea.sheet-vv-desc {{ min-height: 100px !important; height: 130px !important; }}',
    ]) + '\n'
    return h, c


def r27(h, c):
    S = f'{P}{P}'
    c += (f'{S} input.sheet-type[value="werewolf2"] ~ * .sheet-ig2 > .sheet-ifield:has(select[name="attr_tribe"]) > .sheet-input-label '
          f'{{ text-align: right !important; line-height: normal !important; min-width: 85px !important; width: auto !important; padding: 0 4px 0 2px !important; margin: 0 !important; }}\n')
    return h, c


def r28(h, c):
    M = f'{P}{P} .repcontainer[data-groupname="repeating_merits"] .sheet-entry-head'
    c += '\n'.join([
        # empty pool / cost spans were forcing a 2nd (blank) grid row under every merit
        f'{M} > span.sheet-entry-pool:empty, {M} > span.sheet-entry-cost:empty {{ display: none !important; }}',
        f'{M} {{ row-gap: 0 !important; grid-auto-rows: auto !important; min-height: 0 !important; }}',
        # type pill sizes to its text (incl. the splat-name label)
        f'{M} > .sheet-mcat-badge {{ width: max-content !important; min-width: 0 !important; max-width: none !important; overflow: visible !important; justify-self: start; }}',
    ]) + '\n'
    return h, c


def r29(h, c):
    import re
    S = f'{P}{P}'
    m = re.search(r'<div class="sheet-tabfill"></div><div class="sheet-ovrow">(.*?)</div>\s*', h, re.S)
    assert m
    labels = m.group(1)
    h = h[:m.start()] + '<div class="sheet-tabfill"></div>' + h[m.end():]
    k = h.index('name="act_rolltype_select_rote"'); k = h.index('</button>', k) + 9
    h = h[:k] + labels.replace('class="sheet-ovbtn ', 'class="sheet-ovbtn sheet-ovbtn-rr ') + h[k:]
    # (30) Config tab last: move it right after the Notes tab
    cm = re.search(r'<button type="action" class="sheet-toggle sheet-page-settings"[^>]*>Config</button>\s*', h)
    cfg = cm.group(0).strip(); h = h[:cm.start()] + h[cm.end():]
    n = h.index('name="act_page_details"'); n = h.index('</button>', n) + 9
    h = h[:n] + ' ' + cfg + h[n:]
    F = 'font-family: "Sorts Mill Goudy", "Goudy Old Style", Garamond, Georgia, serif !important; font-size: 13px !important; font-weight: 700 !important; text-transform: none !important; letter-spacing: normal !important;'
    B = 'border: 1px solid color-mix(in srgb, var(--pad, var(--pa, #888)) 78%, rgba(0,0,0,0)) !important; border-radius: 10px !important;'
    R = f'{S}{P} .sheet-diceroller-options label.sheet-ovbtn'
    c += '\n'.join([
        f'{R} {{ display: inline-flex !important; align-items: center !important; align-self: center !important; gap: 4px; margin: 0 !important; padding: 3px 11px !important; min-height: 23px !important; line-height: 16px !important; box-sizing: border-box !important; white-space: nowrap !important; cursor: pointer; vertical-align: middle; {F} {B} }}',
        f'{R} > input.sheet-ovf {{ position: absolute !important; opacity: 0 !important; width: 1px !important; height: 1px !important; margin: 0 !important; }}',
        f'{R}:has(> input:checked) {{ background: var(--pa) !important; color: #fff !important; }}',
        f'{S} .sheet-background > .sheet-tabfill, {S} .sheet-background > .sheet-ovrow {{ display: none !important; }}',
        f'{S} .sheet-background > .sheet-spacer {{ height: 2px !important; min-height: 0 !important; margin: 0 !important; padding: 0 !important; }}',
        f'{S} .sheet-background > .sheet-page {{ padding-top: 2px !important; }}',
        f'{S}{P} .sheet-background > button.sheet-toggle.sheet-page-1 {{ margin-left: auto !important; }}',
        f'{S}{P} .sheet-background > button.sheet-toggle.sheet-page-settings {{ margin-right: auto !important; }}',
        f'{S}{P} .sheet-diceroller-options {{ column-gap: 3px !important; }}',
        f'{S}{P} .sheet-diceroller-options button.sheet-toggle, {R} {{ padding-left: 7px !important; padding-right: 7px !important; }}',
        # (30) Config tab looks like Main / Forms / Notes
        f'{S}{P} .sheet-background > input.sheet-page:not([value="settings"]) ~ button.sheet-toggle.sheet-page-settings {{ border-bottom-color: rgba(0,0,0,0) !important; }}',
        f'{S}{P} .sheet-background > button.sheet-toggle.sheet-page-settings {{ border-top-width: 0 !important; border-left-width: 0 !important; border-right-width: 0 !important; border-bottom-style: solid !important; background: none !important; box-shadow: none !important; outline: 0 !important;  margin-top: 6px !important; margin-left: 0 !important; margin-bottom: 0 !important; order: 2 !important; padding: 2px 6px !important; font-size: 14px !important; line-height: 20px !important; letter-spacing: normal !important; height: 27px !important; border-bottom-width: 3px !important; border-radius: 4px !important; }}',
    ]) + '\n'
    return h, c


def r31(h, c):
    import re
    S = f'{P}{P}'
    # (a) Used this story -> slide toggle (same label.sheet-switch pattern as the rest of the sheet)
    old = '<input type="checkbox" name="attr_urkhar_used" value="1" /> Used this story'
    assert old in h
    h = h.replace(old, '<input type="checkbox" name="attr_urkhar_used" value="1" /><span class="sheet-sw-track"></span><span>Used this story</span>')
    h = h.replace('<label class="sheet-ur-used"', '<label class="sheet-ur-used sheet-switch"')
    # (b) feature pills: fixed row of radios + ONE detail box whose content follows the selected pill
    def conv(m):
        block = m.group(0)
        items = re.findall(r'<span class="sheet-fc-tw"><input type="checkbox" class="sheet-fc-tg" name="attr_fcd_([a-z]+)_(\d+)" value="1" title="([^"]*)" /><span class="sheet-fc-trait">(.*?)</span><span class="sheet-fc-desc">(.*?)</span></span>', block, re.S)
        if not items:
            return block
        form = items[0][0]
        pills = ''.join(f'<span class="sheet-fc-tw"><input type="radio" class="sheet-fc-tg" name="attr_fcsel_{form}" value="{i}" title="{t}" /><span class="sheet-fc-trait">{tr}</span></span>' for _, i, t, tr, _d in items)
        det = ''.join(f'<span class="sheet-fc-d sheet-fc-d{i}"><b>{tr}: </b>{d}</span>' for _, i, t, tr, d in items)
        return (f'<div class="sheet-fc-traits">{pills}</div>'
                f'<div class="sheet-fc-detail"><input type="hidden" class="sheet-fc-selv" name="attr_fcsel_{form}" value="" />{det}'
                f'<span class="sheet-fc-d sheet-fc-dnone">Select a feature above to read what it does.</span></div>')
    h, n = re.subn(r'<div class="sheet-fc-traits">(?:<span class="sheet-fc-tw">.*?</span></span>)+</div>', conv, h, flags=re.S)
    assert n >= 6, n
    assert 'class="sheet-fc-desc"' not in h
    rules = [
        f'{S} .sheet-fc-traits {{ display: flex !important; flex-wrap: wrap !important; gap: 4px !important; align-items: center !important; }}',
        f'{S} .sheet-fc-traits > .sheet-fc-tw {{ flex: 0 0 auto !important; position: relative; display: inline-flex !important; }}',
        f'{S} .sheet-fc-traits > .sheet-fc-tw > input.sheet-fc-tg {{ position: absolute !important; inset: 0 !important; width: 100% !important; height: 100% !important; margin: 0 !important; opacity: 0 !important; cursor: pointer; z-index: 2; }}',
        f'{S} .sheet-fc-traits > .sheet-fc-tw > .sheet-fc-trait::after {{ display: none !important; }}',
        f'{S} .sheet-fc-traits > .sheet-fc-tw > input.sheet-fc-tg:checked + .sheet-fc-trait {{ background: color-mix(in srgb, var(--temp-dot, #aa5a1e) 35%, rgba(0,0,0,0)) !important; border-color: var(--temp-dot, #aa5a1e) !important; }}',
        f'{S} .sheet-fc-detail {{ display: block; margin: 4px 0 0; padding: 4px 8px; min-height: 30px; box-sizing: border-box; font-size: 11px; line-height: 1.35; border-left: 2px solid var(--temp-dot, #aa5a1e); background: rgba(0,0,0,.18); border-radius: 0 4px 4px 0; }}',
        f'{S} .sheet-fc-detail > .sheet-fc-d {{ display: none; }}',
        f'{S} .sheet-fc-detail > input.sheet-fc-selv[value=""] ~ .sheet-fc-dnone {{ display: block; opacity: .65; font-style: italic; }}',
    ] + [f'{S} .sheet-fc-detail > input.sheet-fc-selv[value="{i}"] ~ .sheet-fc-d{i} {{ display: block; }}' for i in range(12)]
    # (c) compact stats / steppers, inline labels
    rules += [
        f'{S} .sheet-fc-urtrack {{ display: flex !important; flex-wrap: wrap; align-items: center !important; gap: 4px 10px !important; margin: 4px 0 0 !important; padding: 0 !important; min-height: 0 !important; }}',
        f'{S} .sheet-fc-urtrack label.sheet-ur-used {{ display: inline-flex !important; align-items: center; gap: 5px; margin: 0 !important; font-size: 12px; white-space: nowrap; }}',
        f'{S} .sheet-fc-urtrack .sheet-ur-tl {{ display: inline-flex !important; align-items: center !important; gap: 3px !important; margin: 0 !important; font-size: 12px; white-space: nowrap; }}',
        f'{S} .sheet-fcard button.sheet-res-btn {{ width: 18px !important; height: 18px !important; min-width: 0 !important; padding: 0 !important; line-height: 16px !important; font-size: 12px !important; margin: 0 !important; }}',
        f'{S} .sheet-fcard input[type=number] {{ width: 30px !important; min-width: 0 !important; height: 18px !important; padding: 0 2px !important; margin: 0 !important; text-align: center !important; font-size: 12px !important; box-sizing: border-box !important; }}',
        f'{S} .sheet-fc-urtrack label.sheet-ur-used > input {{ position: absolute !important; opacity: 0 !important; width: 32px !important; height: 16px !important; margin: 0 !important; z-index: 2; cursor: pointer; }}',
        f'{S} .sheet-fc-urtrack label.sheet-ur-used > .sheet-sw-track {{ display: inline-block !important; position: relative !important; width: 28px !important; height: 14px !important; border-radius: 7px !important; background: #666 !important; flex: 0 0 auto; }}',
        f'{S} .sheet-fc-urtrack label.sheet-ur-used > .sheet-sw-track::after {{ content: ""; position: absolute; left: 2px; top: 2px; width: 10px; height: 10px; border-radius: 50%; background: #fff; transition: left .15s; }}',
        f'{S} .sheet-fc-urtrack label.sheet-ur-used > input:checked + .sheet-sw-track {{ background: var(--temp-dot, var(--pa, #aa5a1e)) !important; }}',
        f'{S} .sheet-fc-urtrack label.sheet-ur-used > input:checked + .sheet-sw-track::after {{ left: 16px; }}',
        f'{S} .sheet-fc-urtrack label.sheet-ur-used::before, {S} .sheet-fc-urtrack label.sheet-ur-used::after {{ display: none !important; content: none !important; }}',
        f'{S} .sheet-fc-urinfo {{ flex: 1 1 100%; margin: 0 !important; font-size: 11px; opacity: .8; }}',
        f'{S} .sheet-fc-stats {{ gap: 3px !important; }}',
        f'{S} .sheet-fc-stat {{ padding: 1px 5px !important; min-width: 0 !important; width: auto !important; }}',
    ]
    c += '\n'.join(rules) + '\n'
    return h, c


FIMG_JS = '''
        const fimgSet = (attr) => getAttrs([attr], v => {
            const cur = String(v[attr] || "").replace(/[|}\\]\\[]/g, "");
            startRoll("!fimg [[0[?{Image URL (blank to clear)|" + cur + "}]]]", (r) => {
                finishRoll(r.rollId);
                const k = Object.keys(r.results || {})[0]; let u = "";
                if (k) { const m = /\\[(.*)\\]/.exec(r.results[k].expression || ""); u = m ? m[1].trim() : ""; }
                if (u && !/^https?:\\/\\//i.test(u)) return;
                const o = {}; o[attr] = u; setAttrs(o);
            });
        });
        ["hishu", "dalu", "gauru", "urkhar", "urshul", "urhan"].forEach(f => on("clicked:fimg_" + f, () => fimgSet("form_" + f + "_img")));
'''


FORMS5 = ['hishu', 'dalu', 'gauru', 'urkhar', 'urshul', 'urhan']


def r32(h, c):
    import re
    S = f'{P}{P}'
    for f in FORMS5:
        a = h.index(f'<div class="sheet-fcard sheet-fc-{f}')
        b = h.index('<div class="sheet-fcard', a + 10) if f != 'urhan' else h.index('</textarea></div>', h.index(f'name="attr_form_notes_{f}"', a)) + 17
        card = h[a:b]
        # stats inline with the title
        sm = re.search(r'<div class="sheet-fc-stats">.*?</div>', card, re.S)
        stats = sm.group(0); card = card.replace(stats, '', 1)
        card = re.sub(r'(<div class="sheet-fc-head"><span class="sheet-fc-name">[^<]*</span>)', lambda m: m.group(1) + stats, card, 1)
        # image slot at top
        img = (f'<div class="sheet-fc-img"><span class="sheet-fc-imgph">No image<br/>200 x 300</span>'
               f'<img class="sheet-fc-imgel" name="attr_form_{f}_img" alt="" /><input type="hidden" name="attr_form_{f}_img" value="" />'
               f'<button type="action" class="sheet-fc-imgbtn" name="act_fimg_{f}" title="Set image URL">&#9998;</button></div>')
        card = card.replace('<div class="sheet-fc-glow"></div>', '<div class="sheet-fc-glow"></div>' + img, 1)
        # description + image URL field
        card = card.replace(f'<textarea class="sheet-fc-notes" name="attr_form_notes_{f}" rows="2" placeholder="Notes on this form&#8217;s features"></textarea>',
                            f'<textarea class="sheet-fc-notes" name="attr_form_notes_{f}" rows="3" placeholder="Description of this form"></textarea>'
                            )
        # turn counter off the Forms tab
        card = re.sub(r'<span class="sheet-ur-tl".*?</span>', '', card, 1, re.S)
        h = h[:a] + card + h[b:]
    # Main: Ur'Khar turn track under the form picker
    boxes = ''.join(f'<button type="action" class="sheet-ut-b" name="act_urk_tb_{i}" title="{i} turn(s) left"></button>' for i in range(1, 16))
    track = (f'<div class="sheet-ut-row sheet-urkhar-col"><span class="sheet-ut-l">Turns left</span>'
             f'<input type="hidden" class="sheet-ut-v" name="attr_urkhar_turns" value="0" />{boxes}</div>')
    k = h.index('act_setform_urhan'); e = h.index('</div>', k) + 6
    h = h[:e] + track + h[e:]
    js = ('\n        for (let i = 1; i <= 15; i++) on("clicked:urk_tb_" + i, () => getAttrs(["urkhar_turns"], v => { const cur = parseInt(v.urkhar_turns) || 0; setAttrs({urkhar_turns: cur === i ? i - 1 : i}); }));\n')
    js += FIMG_JS
    k = h.index('on("clicked:urkhar_turn_dec"'); k = h.index('\n', k)
    h = h[:k] + js + h[k:]
    F = f'{S} .sheet-fcards'
    rules = [
        f'{F} {{ display: grid !important; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)) !important; gap: 8px !important; align-items: start !important; }}',
        f'{F} > input {{ display: none !important; }}',
        f'{F} > .sheet-fcard {{ min-width: 0 !important; width: auto !important; margin: 0 !important; padding: 6px !important; box-sizing: border-box !important; display: flex !important; flex-direction: column; gap: 4px; }}',
        f'{F} > input.sheet-urkhar-flag:not([value="1"]) ~ .sheet-fcard.sheet-fc-urkhar {{ display: none !important; }}',
        f'{F} .sheet-fc-img {{ position: relative; width: 100%; max-width: 200px; height: 300px; margin: 0 auto; border: 1px dashed rgba(255,255,255,.25); border-radius: 6px; overflow: hidden; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,.2); box-sizing: border-box; }}',
        f'{F} .sheet-fc-imgph {{ font-size: 11px; opacity: .5; text-align: center; }}',
        f'{F} img.sheet-fc-imgel {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}',
        f'{F} img.sheet-fc-imgel:not([src]), {F} img.sheet-fc-imgel[src=""] {{ display: none; }}',
        f'{F} .sheet-fc-head {{ display: flex !important; flex-wrap: wrap !important; align-items: center !important; gap: 3px 6px !important; margin: 0 !important; padding: 0 !important; }}',
        f'{F} .sheet-fc-head > .sheet-fc-stats {{ display: flex !important; flex-wrap: wrap !important; gap: 2px !important; margin: 0 !important; padding: 0 !important; flex: 1 1 auto; }}',
        f'{F} .sheet-fc-head .sheet-fc-stat {{ font-size: 10px !important; padding: 0 4px !important; line-height: 15px !important; border-radius: 8px; border: 1px solid rgba(255,255,255,.2); white-space: nowrap; }}',
        f'{F} .sheet-fc-head .sheet-fc-stat > span:empty {{ display: none; }}',
        f'{F} .sheet-fc-head .sheet-fc-stat:has(> span:empty) {{ display: none !important; }}',
        f'{F} textarea.sheet-fc-notes {{ display: block !important; width: 100% !important; box-sizing: border-box; min-height: 44px; margin: 0 !important; resize: vertical; }}',
        f'{S}{P} .sheet-fcards button.sheet-fc-imgbtn {{ position: absolute !important; right: 4px; bottom: 4px; z-index: 3; width: 22px !important; height: 22px !important; min-width: 0 !important; padding: 0 !important; border-radius: 50% !important; font-size: 12px !important; line-height: 20px !important; background: rgba(0,0,0,.6) !important; border: 1px solid rgba(255,255,255,.4) !important; color: #fff !important; cursor: pointer; }}',
        f'{F} label.sheet-fc-url {{ display: flex !important; align-items: center; gap: 4px; font-size: 10px; margin: 0 !important; opacity: .8; }}',
        f'{F} label.sheet-fc-url > input {{ flex: 1 1 auto; min-width: 0 !important; width: auto !important; height: 18px !important; font-size: 10px !important; padding: 0 3px !important; }}',
        f'{F} .sheet-fc-detail {{ margin: 0 !important; }}',
        # Main turn track
        f'{S} .sheet-ut-row {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 2px; margin: 3px 0 0; }}',
        f'{S} input.sheet-urkhar-flag:not([value="1"]) ~ .sheet-ut-row {{ display: none !important; }}',
        f'{S} .sheet-ut-l {{ font-size: 11px; font-weight: 700; margin-right: 4px; }}',
        f'{S}{P} button.sheet-ut-b {{ width: 12px !important; height: 12px !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important; border: 1px solid var(--temp-dot, #aa5a1e) !important; border-radius: 2px !important; background: none !important; box-shadow: none !important; cursor: pointer; }}',
    ] + [f'{S}{P} input.sheet-ut-v[value="{n}"] ~ button.sheet-ut-b:nth-of-type(-n+{n}) {{ background: var(--temp-dot, #aa5a1e) !important; }}' for n in range(1, 16)]
    c += '\n'.join(rules) + '\n'
    return h, c


def r37(h, c):
    old = '<label class="sheet-det-m"><span data-i18n="d-det_eyes">Eyes</span><textarea class="sheet-det-ta" rows="1" name="attr_det_eyes"></textarea></label>'
    assert h.count(old) == 1
    h = h.replace(old, '<label class="sheet-det-s"><span data-i18n="d-det_eyes">Eyes</span><input type="text" name="attr_det_eyes" /></label>')
    return h, c


CB_SLOTS = ['hishu', 'dalu', 'gauru', 'urshul', 'urhan']
CB_K = [('strength', 'Str'), ('dexterity', 'Dex'), ('stamina', 'Sta'), ('manipulation', 'Man'), ('size', 'Size'),
        ('initiative', 'Init'), ('speed', 'Speed'), ('health', 'Health'), ('perception', 'Perc')]
CB_NF = 4


def r33(h, c):
    import re
    S = f'{P}{P}'
    CB = S + P + ':has(input.sheet-type[value="breeds2"])'
    for f in CB_SLOTS:
        a = h.index(f'<div class="sheet-fcard sheet-fc-{f}')
        hd = h.index('<div class="sheet-fc-head">', a)
        # caret + custom name in the head
        hd += len('<div class="sheet-fc-head">')
        h = h[:hd] + f'<input type="checkbox" class="sheet-cbf-edit" name="attr_cbf_{f}_edit" value="1" title="Edit this form" />' + h[hd:]
        hn = h.index('<span class="sheet-fc-name">', a); hn = h.index('</span>', hn) + 7
        h = h[:hn] + f'<span class="sheet-fc-name sheet-cbn" name="attr_cbf_{f}_name"></span>' + h[hn:]
        # custom features display + edit panel, inserted before the description
        pills = ''.join(f'<span class="sheet-fc-tw"><input type="radio" class="sheet-fc-tg" name="attr_cbfsel_{f}" value="{n}" /><span class="sheet-fc-trait" name="attr_cbf_{f}_ft{n}_name"></span></span>' for n in range(CB_NF))
        det = ''.join(f'<span class="sheet-fc-d sheet-fc-d{n}"><span class="sheet-cbf-fn" name="attr_cbf_{f}_ft{n}_name"></span>: <span name="attr_cbf_{f}_ft{n}_text"></span></span>' for n in range(CB_NF))
        disp = (f'<div class="sheet-cbf-view"><div class="sheet-fc-traits">{pills}</div>'
                f'<div class="sheet-fc-detail"><input type="hidden" class="sheet-fc-selv" name="attr_cbfsel_{f}" value="" />{det}'
                f'<span class="sheet-fc-d sheet-fc-dnone">Select a feature above to read what it does.</span></div></div>')
        steps = ''.join(f'<label class="sheet-cbf-st"><b>{lab}</b><input type="number" name="attr_cbf_{f}_{k}" value="0" step="1" /></label>' for k, lab in CB_K)
        feats = ''.join(f'<div class="sheet-cbf-ft"><input type="text" name="attr_cbf_{f}_ft{n}_name" placeholder="Feature {n + 1} name" /><textarea name="attr_cbf_{f}_ft{n}_text" rows="2" placeholder="What it does"></textarea></div>' for n in range(CB_NF))
        edit = (f'<div class="sheet-cbf-panel"><label class="sheet-cbf-nm">Form name <input type="text" name="attr_cbf_{f}_name" placeholder="Form name" /></label>'
                f'<div class="sheet-cbf-stats">{steps}</div>{feats}<input type="hidden" name="attr_cbf_{f}_set" value="" /></div>')
        t = h.index(f'<textarea class="sheet-fc-notes" name="attr_form_notes_{f}"', a)
        h = h[:t] + disp + edit + h[t:]
    # Main (Breeds): picker buttons showing the custom names + turn boxes
    sel = re.search(r'<label class="sheet-form-select">[^<]*<span data-i18n="form">Form</span>\s*<select name="attr_form">.*?</select>\s*</label>', h, re.S)
    assert sel
    btns = ''.join(f'<button type="action" class="sheet-form-btn sheet-cbp-{f}" name="act_setform_{f}"><input type="hidden" class="sheet-form-cur" name="attr_form" value="hishu" /><span name="attr_cbf_{f}_name"></span></button>' for f in CB_SLOTS)
    boxes = ''.join(f'<button type="action" class="sheet-ut-b" name="act_urk_tb_{i}" title="{i} turn(s) left"></button>' for i in range(1, 16))
    h = h[:sel.start()] + f'<span class="sheet-cb-picker">{btns}</span><div class="sheet-ut-row sheet-ut-cb"><span class="sheet-ut-l">Turns left</span><input type="hidden" class="sheet-ut-v" name="attr_urkhar_turns" value="0" />{boxes}</div>' + h[sel.end():]
    # worker: custom mods for Breeds, names, migration
    attrs = [f'cbf_{f}_{k}' for f in CB_SLOTS for k, _ in CB_K] + [f'cbf_{f}_name' for f in CB_SLOTS] + [f'cbf_{f}_set' for f in CB_SLOTS]
    js_pre = ('const CBF_SLOTS = ' + str(CB_SLOTS).replace("'", '"') + ', CBF_K = ' + str([k for k, _ in CB_K]).replace("'", '"') + ', CBF_ATTRS = ' + str(attrs).replace("'", '"') + ';\n'
              '        const cbM = (v, f) => { if (v.sheettype !== "breeds2" || CBF_SLOTS.indexOf(f) < 0 || v["cbf_" + f + "_set"] !== "1") return null; const m = {}; CBF_K.forEach(k => m[k] = parseInt(v["cbf_" + f + "_" + k]) || 0); return m; };\n'
              '        ')
    old1 = 'const updateForms = () => {\n            getAttrs(["strength","dexterity","stamina","manipulation","wits","composure","athletics","base_size","form","urkhar_enabled","sheettype"], (v) => {'
    assert old1 in h, 'uf'
    h = h.replace(old1, js_pre + 'const updateForms = () => {\n            getAttrs(["strength","dexterity","stamina","manipulation","wits","composure","athletics","base_size","form","urkhar_enabled","sheettype"].concat(CBF_ATTRS), (v) => {')
    o2 = 'const m = (f === "gauru" && ur) ? GAURU_URKHAR_VARIANT : FORM_MODS[f];'
    assert h.count(o2) == 1
    h = h.replace(o2, 'const m = cbM(v, f) || ((f === "gauru" && ur) ? GAURU_URKHAR_VARIANT : FORM_MODS[f]);')
    o3 = 'const m = (form === "gauru" && ur) ? GAURU_URKHAR_VARIANT : FORM_MODS[form];'
    assert h.count(o3) == 1
    h = h.replace(o3, 'const m = cbM(v, form) || ((form === "gauru" && ur) ? GAURU_URKHAR_VARIANT : FORM_MODS[form]);')
    o4 = 'u.form_label = FORM_LABEL[form];'
    assert o4 in h
    h = h.replace(o4, 'u.form_label = (v.sheettype === "breeds2" && v["cbf_" + form + "_name"]) || FORM_LABEL[form];')
    o5 = 'change:base_size change:sheettype sheet:opened", updateForms);'
    assert o5 in h
    mig = ('\n        on("change:base_size change:sheettype sheet:opened " + CBF_ATTRS.map(a => "change:" + a).join(" "), updateForms);\n'
           '        // r33: Changing Breeds form slots, seeded once from the stock forms; existing values are never overwritten\n'
           '        on("sheet:opened change:sheettype", () => getAttrs(["sheettype"].concat(CBF_ATTRS), v => { if (v.sheettype !== "breeds2") return; const u = {};\n'
           '            CBF_SLOTS.forEach(f => { if (v["cbf_" + f + "_set"] === "1") return; if (!v["cbf_" + f + "_name"]) u["cbf_" + f + "_name"] = FORM_LABEL[f];\n'
           '                CBF_K.forEach(k => { const cur = v["cbf_" + f + "_" + k]; if (cur === undefined || cur === "" || cur === "0") u["cbf_" + f + "_" + k] = FORM_MODS[f][k]; }); u["cbf_" + f + "_set"] = "1"; });\n'
           '            if (Object.keys(u).length) setAttrs(u); }));\n')
    h = h.replace(o5, 'change:base_size change:sheettype sheet:opened", updateForms);' + mig, 1)
    o6 = 'const label = SHIFT_FORMS[f] || f;'
    if o6 in h:
        h = h.replace('const shiftTo = (f, already) => getAttrs(["character_name", "morality", "form", "sheettype", "urkhar_enabled"]', 'const shiftTo = (f, already) => getAttrs(["character_name", "morality", "form", "sheettype", "urkhar_enabled", "cbf_" + f + "_name"]')
        h = h.replace(o6, 'const label = (v.sheettype === "breeds2" && v["cbf_" + f + "_name"]) || SHIFT_FORMS[f] || f;')
    F = f'{S} .sheet-fcards'
    rules = [
        # werewolf: fixed; breeds: custom view
        f'{F} .sheet-cbn, {F} .sheet-cbf-view, {F} .sheet-cbf-panel, {F} input.sheet-cbf-edit {{ display: none !important; }}',
        f'{CB} .sheet-fcards .sheet-cbn {{ display: inline !important; }}',
        f'{CB} .sheet-fcards .sheet-fc-head > .sheet-fc-name:not(.sheet-cbn), {CB} .sheet-fcards .sheet-fcard > .sheet-fc-traits, {CB} .sheet-fcards .sheet-fcard > .sheet-fc-detail, {CB} .sheet-fcards .sheet-fc-urnote, {CB} .sheet-fcards .sheet-fc-urtrack {{ display: none !important; }}',
        f'{CB} .sheet-fcards .sheet-cbf-view {{ display: flex !important; flex-direction: column; gap: 4px; }}',
        f'{CB} .sheet-fcards input.sheet-cbf-edit {{ display: block !important; -webkit-appearance: none; appearance: none !important; width: 14px !important; height: 14px !important; min-width: 14px !important; opacity: 1 !important; visibility: visible !important; margin: 0 !important; cursor: pointer; position: relative; align-self: center; flex: 0 0 14px; }}',
        f'{CB} .sheet-fcards input.sheet-cbf-edit::before {{ content: ""; position: absolute; left: 3px; top: 3px; width: 5px; height: 5px; border-right: 1.5px solid var(--temp-dot, #aa5a1e); border-bottom: 1.5px solid var(--temp-dot, #aa5a1e); transform: rotate(-45deg); transition: transform .15s; }}',
        f'{CB} .sheet-fcards input.sheet-cbf-edit:checked::before {{ transform: rotate(45deg); }}',
        f'{CB} .sheet-fcards .sheet-fcard:has(input.sheet-cbf-edit:checked) .sheet-cbf-panel {{ display: flex !important; flex-direction: column; gap: 4px; padding: 4px; border: 1px solid rgba(255,255,255,.15); border-radius: 4px; }}',
        f'{F} .sheet-fc-tw:has(> .sheet-fc-trait:empty) {{ display: none !important; }}',
        f'{F} label.sheet-cbf-nm {{ display: flex; align-items: center; gap: 4px; font-size: 11px; margin: 0; }}',
        f'{F} label.sheet-cbf-nm > input {{ flex: 1 1 auto; min-width: 0; height: 20px; }}',
        f'{F} .sheet-cbf-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 2px 4px; }}',
        f'{F} label.sheet-cbf-st {{ display: flex; align-items: center; justify-content: space-between; gap: 2px; font-size: 10px; margin: 0; }}',
        f'{F} label.sheet-cbf-st > input {{ width: 36px !important; height: 18px !important; padding: 0 2px !important; font-size: 11px !important; text-align: center; }}',
        f'{F} .sheet-cbf-ft {{ display: flex; flex-direction: column; gap: 1px; }}',
        f'{F} .sheet-cbf-ft > input {{ height: 18px; font-size: 11px; width: 100%; box-sizing: border-box; }}',
        f'{F} .sheet-cbf-fn {{ font-weight: 700; }}',
        f'{F} label.sheet-cbf-nm {{ white-space: nowrap; }}',
        f'{F} .sheet-cbf-ft > textarea {{ height: 34px !important; min-height: 26px; font-size: 11px; width: 100%; box-sizing: border-box; resize: vertical; }}',
        f'{CB} .sheet-fcards .sheet-fcard.sheet-fc-urkhar {{ display: none !important; }}',
        f'{CB} .sheet-quick-actions.sheet-breeds2 {{ display: flex !important; flex-wrap: wrap; justify-content: center !important; align-items: center; gap: 4px; }}',
        f'{CB} .sheet-quick-actions.sheet-breeds2 > .sheet-ut-row {{ flex: 1 1 100%; }}',
        f'{S} .sheet-cb-picker {{ display: inline-flex; flex-wrap: wrap; gap: 3px; }}',
        f'{S}{P} .sheet-cb-picker > button.sheet-form-btn {{ display: inline-flex !important; align-items: center; padding: 2px 8px !important; width: auto !important; height: auto !important; font-size: 13px !important; }}',
        f'{S} .sheet-cb-picker > button.sheet-form-btn > span:empty::before {{ content: "?"; }}',
    ] + [f'{S} .sheet-cb-picker > button.sheet-cbp-{f} > input.sheet-form-cur[value="{f}"] + span {{ text-decoration: underline; color: var(--temp-dot, #aa5a1e); }}' for f in CB_SLOTS]
    c += '\n'.join(rules) + '\n'
    return h, c


D10 = 'https://raw.githubusercontent.com/leonembers/cofd-sheet-art/ff25d89770db9e4c52b37855910dd23574d91a3d/icons/d10/'


def r38(h, c):
    S = f'{P}{P}'
    RB = f'{S} .sheet-rollcontainer > button.sheet-rollstyle, {S} .sheet-rollcontainer > button[type="roll"], {S} .sheet-rollcontainer > button.sheet-was-roll'
    ER = f'{S} button.sheet-entry-roll'
    DK = ['input.sheet-dm[value="1"] ~ .sheet-background', '.sheet-darkmode']
    def dark(sel_tail):
        return ', '.join(f'{S} {d} {sel_tail}' if d.startswith('input') else f'{d} {S} {sel_tail}' for d in DK)
    rules = [
        f'{RB} {{ background-image: url("{D10}d10-black-128.png") !important; background-size: contain !important; background-repeat: no-repeat !important; background-position: center !important; transition: transform .1s, filter .15s; }}',
        f'{RB.replace(", ", ":hover, ")}:hover {{ background-image: url("{D10}d10-black-128.png") !important; filter: drop-shadow(0 0 3px var(--pa, #aa5a1e)); }}',
        f'{RB.replace(", ", ":active, ")}:active {{ background-image: url("{D10}d10-black-128.png") !important; transform: scale(.92); }}',
        f'{ER} {{ font-size: 0 !important; color: rgba(0,0,0,0) !important; background-image: url("{D10}d10-black-64.png") !important; background-size: 16px 16px !important; background-repeat: no-repeat !important; background-position: center !important; min-width: 20px !important; min-height: 18px !important; }}',
        f'{ER}:hover {{ filter: drop-shadow(0 0 2px var(--pa, #aa5a1e)); }}',
    ]
    for tail, img in (('.sheet-rollcontainer > button.sheet-rollstyle', '128'), ('.sheet-rollcontainer > button[type="roll"]', '128'), ('.sheet-rollcontainer > button.sheet-was-roll', '128'), ('button.sheet-entry-roll', '64')):
        for st in ('', ':hover', ':active'):
            rules.append(f'{dark(tail + st)} {{ background-image: url("{D10}d10-white-{img}.png") !important; }}')
    c += '\n'.join(rules) + '\n'
    return h, c


def r39(h, c):
    import re
    order = ['normal', '9-again', '8-again', 'dont-reroll', 'chance', 'rote', 'chance-rote']
    btn = {}
    for k in order:
        m = re.search(r'<button type="action" class="sheet-toggle sheet-rolltype-' + re.escape(k) + r'" name="act_rolltype_select_' + re.escape(k) + r'"[^>]*>.*?</button>\s*', h, re.S)
        assert m, k
        btn[k] = m
    first = min(m.start() for m in btn.values()); last = max(m.end() for m in btn.values())
    seg = h[first:last]
    rest = seg
    for m in btn.values():
        rest = rest.replace(m.group(0), '')
    assert rest.strip() == '', rest[:200]
    h = h[:first] + '\n                '.join(btn[k].group(0).strip() for k in order) + '\n                ' + h[last:]
    return h, c


def r40(h, c):
    import re
    S = f'{P}{P}'
    d = re.search(r'<div class="(?:sheet-)?derived">\s*<span data-i18n="defense">Defense</span>.*?</div>', h, re.S)
    a = re.search(r'\s*<div class="(?:sheet-)?derived">\s*<span data-i18n="armor">Armor</span>:<input type="number" name="attr_balistic_armor_display"[^>]*>/<input type="number" name="attr_general_armor_display"[^>]*>\s*</div>', h, re.S)
    assert a
    ds = [m for m in re.finditer(r'<div class="(?:sheet-)?derived">\s*<span data-i18n="defense">Defense</span>.*?</div>', h[:a.start()], re.S)]
    d = ds[-1]
    h = h[:a.start()] + h[a.end():]
    arm = ('<div class="sheet-derived sheet-derived-armor" title="Armor from worn pieces (Stacking pieces add on top): General / Ballistic">'
           '<span data-i18n="armor">Armor</span>:<span class="sheet-ar-si sheet-ar-si-g"></span>'
           '<input type="number" name="attr_general_armor_display" value="@{general_armor}" disabled="disabled" title="@{armor_calc}"/>'
           '<span class="sheet-dslash">/</span><span class="sheet-ar-si sheet-ar-si-b"></span>'
           '<input type="number" name="attr_balistic_armor_display" value="@{balistic_armor}" disabled="disabled" /></div>')
    h = h[:d.start()] + '<div class="sheet-derived-pair">' + d.group(0) + arm + '</div>' + h[d.end():]
    c += '\n'.join([
        f'{S} .sheet-derived-pair {{ display: flex !important; align-items: center; justify-content: space-between; gap: 2px; flex-wrap: nowrap; max-width: 100%; }}',
        f'{S} .sheet-derived-pair > .sheet-derived {{ display: inline-flex !important; align-items: center; gap: 1px; margin: 0 !important; padding: 0 !important; width: auto !important; flex: 0 1 auto; min-width: 0; white-space: nowrap; }}',
        f'{S} .sheet-derived-pair input[type=number] {{ display: inline-block !important; flex: 0 0 20px !important; height: 18px !important; width: 20px !important; font-size: 12px !important; min-width: 0 !important; padding: 0 1px !important; text-align: center; }}',
        f'{S} .sheet-derived-armor > .sheet-ar-si {{ flex: 0 0 12px; margin: 0 0 0 2px; background-size: 12px 12px !important; }}',
        f'{S} .sheet-derived-armor > .sheet-dslash {{ margin: 0 1px; opacity: .7; }}',
    ]) + '\n'
    return h, c


REN5 = ['purity', 'glory', 'honor', 'wisdom', 'cunning']


def r41(h, c):
    import re
    S = f'{P}{P}'
    n = 0
    for r in REN5:
        pat = re.compile(r'(<span class="(?:sheet-)?ren-ic (?:sheet-)?ren-' + r + r'"[^>]*></span>)(<span data-i18n="renown-' + r + r'">[^<]*</span>)')
        h, k = pat.subn(lambda m: f'<input type="hidden" class="sheet-flag sheet-ren-flag" name="attr_renown_{r}_flag" value="0" />' + m.group(1)
                        + f'<button type="action" class="sheet-toggle sheet-ren-tg" name="act_renown_{r}" title="Add {r.capitalize()} Renown to the dice pool">' + m.group(2) + '</button>', h)
        n += k
    assert n >= 5, n
    h = h.replace('var allStats = [ ...attributes, ...skills, "potency" ];',
                  'var allStats = [ ...attributes, ...skills, "potency", "renown_purity", "renown_glory", "renown_honor", "renown_wisdom", "renown_cunning" ];', 1)
    assert '"renown_cunning" ];' in h
    old = '                default:\n                    return getTranslationByKey(attribute);'
    assert old in h
    h = h.replace(old, '                default:\n                    if (/^renown_/.test(attribute)) { const _k = attribute.replace("_", "-"), _t = getTranslationByKey(_k); return (_t && _t !== _k) ? _t : (attribute.charAt(7).toUpperCase() + attribute.slice(8)); }\n                    return getTranslationByKey(attribute);', 1)
    js = ('\n        ["renown_purity","renown_glory","renown_honor","renown_wisdom","renown_cunning"].forEach((r) => on(`clicked:${r}`, () => updateDicePoolAttributes(r)));\n'
          '        on("change:renown_purity change:renown_glory change:renown_honor change:renown_wisdom change:renown_cunning", () => updateDicePool());\n')
    i = h.rfind('</script>')
    h = h[:i] + js + h[i:]
    sel = 'input.sheet-ren-flag[value="1"] ~ button.sheet-ren-tg'
    c += '\n'.join([
        f'{S}{P} .sheet-renown-row button.sheet-ren-tg {{ cursor: pointer; font: inherit; margin: 0; line-height: 1.15; padding: 0 3px !important; border-radius: 4px; background-color: rgba(0,0,0,0); outline: none !important; box-shadow: none !important; border: 0 !important; }}',
        f'{S}{P} .sheet-renown-row button.sheet-ren-tg:focus, {S}{P} .sheet-renown-row button.sheet-ren-tg:focus-visible, {S}{P} .sheet-renown-row button.sheet-ren-tg:active {{ outline: none !important; box-shadow: none !important; }}',
        # (44) selected state: no override, so the sheet's own selected-toggle rule applies exactly as on skills/attributes
    ]) + '\n'
    return h, c


def r42(h, c):
    import re
    # power-stat / integrity / resource tooltips read sheet-worker attrs derived from the existing translation keys
    h, n1 = re.subn(r'(name="act_potency"[^>]*?)title="Potency"', r'\1title="@{potency_tip}"', h)
    h = re.sub(r'title="Clear Potency"', 'title="Clear @{potency_name}"', h)
    h = re.sub(r'title="Set Potency to (\d+)"', r'title="Set @{potency_name} to \1"', h)
    # (43) no tooltips at all on the morality track dots
    h = re.sub(r'(<button[^>]*name="act_morality-\d+"[^>]*?) title="[^"]*"', r'\1', h)
    h = re.sub(r'(<button[^>]*name="act_moralhealthbox_\d+"[^>]*?) title="[^"]*"', r'\1', h)
    h = re.sub(r'title="Mark / clear Vitae box"', 'title="Mark / clear @{resource_name} box"', h)
    for k in ['integrity', 'humanity', 'pilgrimage', 'harmony', 'wisdom', 'clarity', 'memory', 'cover', 'satiety', 'stability']:
        h = re.sub(r'(<span class="[^"]*" data-i18n="' + k + r'")>', r'\1 title="@{morality_tip}">', h)
    for k in ['resource', 'pillars', 'vitae', 'essence', 'mana', 'pyros', 'glamour', 'plasm']:
        h = re.sub(r'(<span (?:class="[^"]*" )?data-i18n="' + k + r'")>', r'\1 title="@{resource_name}">', h)
    assert n1 >= 10, n1
    h = h.replace('name="attr_sheettype"', 'name="attr_sheettype"', 1)
    hid = ''.join(f'<input type="hidden" name="attr_{a}" value="" />' for a in ['potency_name', 'potency_tip', 'morality_name', 'morality_tip', 'resource_name'])
    i = h.find('<div class="sheet-background')
    if i < 0:
        i = h.find('<div class="background')
    assert i > 0
    h = h[:i] + hid + h[i:]
    js = r'''
        const TIP_MOR = {mortal2:"integrity","mortal2-ghost":"integrity",hunter2:"integrity",hunter:"integrity",vampire1:"humanity",vampire2:"humanity",werewolf1:"harmony",werewolf2:"harmony",breeds2:"harmony",mage1:"wisdom",mage2:"wisdom",promethean1:"pilgrimage",promethean2:"pilgrimage",changeling1:"clarity",changeling2:"clarity",mummy1:"memory",mummy2:"memory",demon:"cover",beast:"satiety","deviant-the-renegades":"stability"};
        const TIP_RES = {vampire1:"vitae",vampire2:"vitae",werewolf1:"essence",werewolf2:"essence",breeds2:"essence","mortal2-ghost":"essence",mage1:"mana",mage2:"mana",promethean1:"pyros",promethean2:"pyros",changeling1:"glamour",changeling2:"glamour",geist1:"plasm",geist2:"plasm",mummy1:"pillars",mummy2:"pillars"};
        const tipTr = (k) => { const x = getTranslationByKey(k); return (x && x !== k) ? x : ""; };
        const tipCap = (s) => String(s || "").replace(/(^|[\s-])([a-z])/g, (m, a, b) => a + b.toUpperCase());
        const updateTips = () => getAttrs(["sheettype", "homebrew_rank"], (v) => {
            const t = v.sheettype || "";
            const pk = potencyTranslationKeys[t];
            const pn = (pk && (tipTr(pk) || tipCap(pk.replace(/-/g, " ")))) || v.homebrew_rank || "Power stat";
            const mk = TIP_MOR[t] || "integrity";
            const mn = tipTr(mk) || tipCap(mk);
            const rk = TIP_RES[t] || "resource";
            const rn = tipTr(rk) || tipCap(rk);
            setAttrs({potency_name: pn, potency_tip: pn + ": click to add to the dice pool", morality_name: mn, morality_tip: mn + " (this sheet's Integrity trait)", resource_name: rn}, {silent: true});
        });
        on("sheet:opened change:sheettype change:homebrew_rank", updateTips);
'''
    i = h.rfind('</script>')
    h = h[:i] + js + h[i:]
    return h, c


def r45(h, c):
    import re
    # (45) no trailing colons on derived stat labels (Size, Speed, Defense, Armor, Initiative, Perception, ...)
    h, n = re.subn(r'(<div class="(?:sheet-)?derived[^"]*"[^>]*>\s*(?:<span[^>]*></span>)?\s*<span data-i18n="[a-z-]+"[^>]*>[^<:]*</span>)\s*:', r'\1', h)
    h, n2 = re.subn(r'(<span data-i18n="(?:perception|health|willpower|size|speed|defense|initiative|armor)"[^>]*>[^<]*)\s*:\s*(</span>)', r'\1\2', h)
    assert n >= 4, n
    return h, c


def r46(h, c):
    # (46) gift cards: no overflow at Roll20 live widths; dark collapse carets everywhere. (47) centred gift name.
    Q = f'{P}{P}{P}'
    G = f'{Q} .sheet-gifts'
    CAR = 'background: #1a1a1a !important; border: 1px solid color-mix(in srgb, var(--pad, var(--pa, #888)) 70%, rgba(0,0,0,0)) !important; border-radius: 3px !important; box-shadow: none !important; outline: none !important;'
    c += '\n'.join([
        f'{G} .repcontainer {{ display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)) !important; gap: 4px !important; flex-wrap: nowrap !important; }}',
        f'{G} .repcontainer > .repitem {{ min-width: 0 !important; max-width: 100% !important; width: auto !important; box-sizing: border-box !important; }}',
        f'{G} .sheet-gift {{ box-sizing: border-box !important; width: 100% !important; min-width: 0 !important; max-width: 100% !important; overflow: hidden; padding: 3px !important; }}',
        f'{G} .sheet-gift-lines, {G} .sheet-gift-body {{ box-sizing: border-box !important; min-width: 0 !important; max-width: 100% !important; }}',
        f'{G} .sheet-gf-line, {G} button.sheet-gf-line {{ box-sizing: border-box !important; width: 100% !important; min-width: 0 !important; max-width: 100% !important; padding: 1px 16px 1px 3px !important; overflow: hidden; }}',
        f'{G} .sheet-gf-line .sheet-gf-lock {{ right: 3px !important; left: auto !important; }}',
        f'{G} .sheet-gf-nm {{ min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}',
        f'{G} .sheet-gift-nm {{ text-align: center !important; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; min-width: 0 !important; padding: 0 16px !important; }}',
        f'{G} .sheet-gift-tg, {G} .sheet-gfx-tg {{ -webkit-appearance: none !important; appearance: none !important; width: 13px !important; height: 13px !important; {CAR} }}',
        f'{G} .sheet-gift-tg::before {{ color: var(--pad, var(--pa, #ddd)) !important; line-height: 11px !important; font-size: 11px !important; }}',
        f'{Q} .sheet-entry > input.sheet-entry-toggle {{ width: 13px !important; height: 13px !important; {CAR} }}',
        f'{Q} .sheet-entry > input.sheet-entry-toggle::before {{ border-color: var(--pad, var(--pa, #ddd)) !important; }}',
    ]) + '\n'
    return h, c


def r48(h, c):
    import re
    # (48) per-entry inline roll buttons -> one compact action menu (named attr checkbox toggle, never written by workers)
    pat = re.compile(r'(<input type="hidden" class="(?:sheet-)?haspool"[^>]*/>)(<button[^>]*name="act_rr-roll"[^>]*>)[^<]*(</button>)'
                     r'(\s*<span class="(?:sheet-)?entry-cost"[^>]*></span>)?'
                     r'(?:\s*(<input type="hidden" class="(?:sheet-)?pw-auto-flag"[^>]*/>)\s*(<button[^>]*name="act_proll"[^>]*>)[^<]*(</button>))?')

    def rep(m):
        cost = m.group(4) or ''
        items = m.group(1) + m.group(2) + '<span class="sheet-am-l">Roll pool</span>' + m.group(3)
        if m.group(6):
            items += m.group(5) + m.group(6) + '<span class="sheet-am-l">Roll &amp; pay cost</span>' + m.group(7)
        return (cost + '<span class="sheet-amenu"><input type="checkbox" class="sheet-amenu-tg" name="attr_amenu" value="1" title="Actions" />'
                '<span class="sheet-amenu-list">' + items + '</span></span>')
    h, n = pat.subn(rep, h)
    assert n >= 20, n
    Q = f'{P}{P}{P}'
    A = f'{Q} .sheet-amenu'
    c += '\n'.join([
        f'{A} {{ position: relative !important; display: inline-flex !important; align-items: center; flex: 0 0 auto !important; width: 18px; height: 18px; margin: 0 0 0 2px !important; order: 99; }}',
        f'{A} > input.sheet-amenu-tg {{ -webkit-appearance: none !important; appearance: none !important; position: static !important; display: block !important; width: 18px !important; height: 16px !important; margin: 0 !important; padding: 0 !important; cursor: pointer; background: #1a1a1a !important; border: 1px solid color-mix(in srgb, var(--pad, var(--pa, #888)) 70%, rgba(0,0,0,0)) !important; border-radius: 3px !important; box-shadow: none !important; outline: none !important; opacity: 1 !important; }}',
        f'{A} > input.sheet-amenu-tg::before {{ content: "..."; display: block; text-align: center; font: bold 11px/9px Arial, sans-serif; color: var(--pad, var(--pa, #ddd)); letter-spacing: 0; }}',
        f'{A} > .sheet-amenu-list {{ display: none !important; position: absolute; right: 0; top: 19px; z-index: 60; min-width: 120px; max-width: 200px; flex-direction: column; gap: 2px; padding: 3px; background: #1a1a1a; border: 1px solid var(--pad, var(--pa, #888)); border-radius: 5px; box-shadow: 0 4px 10px rgba(0,0,0,.6); }}',
        f'{A} > input.sheet-amenu-tg:checked + .sheet-amenu-list {{ display: flex !important; }}',
        f'{A} .sheet-amenu-list button {{ display: flex !important; visibility: visible !important; align-items: center; width: 100% !important; height: auto !important; min-height: 20px; box-sizing: border-box !important; margin: 0 !important; padding: 2px 6px 2px 22px !important; text-align: left; white-space: nowrap; color: #e8e8e8 !important; font-family: "Sorts Mill Goudy", "Goudy Old Style", Garamond, Georgia, serif !important; font-size: 13px !important; font-weight: 700 !important; background-color: rgba(0,0,0,0) !important; background-position: 3px center !important; background-size: 14px 14px !important; background-repeat: no-repeat !important; border: 1px solid rgba(0,0,0,0) !important; border-radius: 3px !important; text-shadow: none !important; box-shadow: none !important; }}',
        f'{A} .sheet-amenu-list button:hover {{ border-color: var(--pad, var(--pa, #888)) !important; background-color: color-mix(in srgb, var(--pad, var(--pa, #888)) 18%, rgba(0,0,0,0)) !important; }}',
        f'{A} .sheet-amenu-list input.sheet-haspool[value="0"] + button, {A} .sheet-amenu-list input.sheet-haspool[value=""] + button {{ display: none !important; }}',
        f'{A} .sheet-am-l {{ font-size: 13px !important; }}',
    ]) + '\n'
    return h, c


def r49(h, c):
    # (49) worker setAttrs guard: drop no-op writes and never touch collapse/menu open flags
    js = r'''
        (function () { try {
            const _sa = setAttrs;
            const OPEN = /(^|_)(show|amenu)$|_f_(cun|glo|hon|pur|wis)_show$/;
            setAttrs = function (u, o, cb) {
                if (typeof o === "function") { cb = o; o = {}; }
                o = o || {};
                const allowOpen = !!o.allowOpen;
                const k = Object.keys(u || {}).filter(x => allowOpen || !OPEN.test(x));
                if (!k.length) { if (cb) cb(); return; }
                getAttrs(k, (v) => {
                    const d = {}; let n = 0;
                    k.forEach(x => { const a = v[x], b = u[x]; if (a === undefined || String(a) !== String(b)) { d[x] = b; n++; } });
                    const o2 = Object.assign({}, o); delete o2.allowOpen;
                    if (n) _sa(d, o2, cb); else if (cb) cb();
                });
            };
        } catch (e) {} })();
'''
    i = h.find('<script type="text/worker">')
    assert i > 0
    j = i + len('<script type="text/worker">')
    h = h[:j] + js + h[j:]
    # the explicit expand/collapse-all buttons and new-row creation are the only intended writers of show
    h = h.replace('u[`repeating_${sec}_${id}_show`] = val); setAttrs(u, {silent: true});', 'u[`repeating_${sec}_${id}_show`] = val); setAttrs(u, {silent: true, allowOpen: true});')
    h = h.replace('[p + "show"]: "0"});', '[p + "show"]: "0"}, {allowOpen: true});') if False else h
    return h, c


def r50(h, c):
    # (50) label + slide toggle (and label + checkbox) inline on one line inside collapsible bodies; (48) menu not clipped
    Q = f'{P}{P}{P}'
    B = f'{Q} .sheet-entry-body'
    c += '\n'.join([
        f'{B} label.sheet-switch, {Q} .sheet-gift-body label.sheet-switch {{ display: inline-flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; gap: 6px !important; width: auto !important; }}',
        f'{B} label.sheet-switch > .sheet-sw-lbl, {Q} .sheet-gift-body label.sheet-switch > .sheet-sw-lbl {{ order: -1; display: inline-block !important; margin: 0 !important; line-height: normal !important; }}',
        f'{B} label.sheet-switch > .sheet-sw-track {{ order: 1; flex: 0 0 auto; margin: 0 !important; }}',
        f'{B} label:has(> input[type=checkbox]):not(.sheet-switch) {{ display: inline-flex !important; flex-direction: row !important; align-items: center !important; gap: 6px !important; }}',
        f'{B} label:has(> input[type=checkbox]):not(.sheet-switch) > input[type=checkbox] {{ margin: 0 !important; position: static !important; }}',
        f'{Q} .sheet-entry-head:has(.sheet-amenu) {{ overflow: visible !important; position: relative; z-index: 6; }}',
        f'{Q} .sheet-entry:has(.sheet-amenu-tg:checked) {{ overflow: visible !important; z-index: 7; position: relative; }}',
    ]) + '\n'
    return h, c


def r51(h, c):
    # (52)(53) gift name = roll button in display mode; name edited in the caret panel; worker-built roll (no @{} refs)
    Q = f'{P}{P}{P}'
    nm = '<input type="text" class="sheet-gift-nm" name="attr_name" placeholder="Gift name" />'
    n = h.count(nm)
    assert n == 2, n
    h = h.replace(nm, '<button type="action" class="sheet-gift-nmb" name="act_gpost" title="Post Gift to chat"><span name="attr_name"></span></button>')
    h = re.sub(r'(<div class="(?:sheet-)?gift-body">)', r'\1<input type="text" class="sheet-gift-nmed" name="attr_name" placeholder="Gift name" />', h)
    # (54) Notes page: one big free-text notes area above the old list (old rows kept, list only shown when it has rows)
    k = '<div class="sheet-entry-section sheet-notes">'
    assert k in h
    h = h.replace(k, '<div class="sheet-bignotes"><div class="sheet-subheader"><span>Notes</span></div><textarea class="sheet-bignotes-ta" name="attr_sheet_notes" placeholder="Notes"></textarea></div>' + k, 1)
    # (58) gift migration idempotent: never touch rows that already have facet data; stamp checked rows gv=2 once
    o = 'const isOld = (s, id) => g(s, id, "gv") === "" && !!('
    assert o in h
    h = h.replace(o, 'const isOld = (s, id) => g(s, id, "gv") === "" && !Object.keys(R15_RN).some(k => g(s, id, `f_${k}_name`)) && !!(')
    o = 'rows.forEach(([s, id]) => { if (g(s, id, "gv") !== "old" && !isOld(s, id))'
    assert o in h
    h = h.replace(o, 'rows.forEach(([s, id]) => { if (g(s, id, "gv") === "" && !isOld(s, id)) out[`repeating_${s}_${id}_gv`] = "2"; });\n                    ' + o)
    js = r'''
        // r15b (53): Gift name posts via the worker with real row values
        ["gifts", "wgifts"].forEach(sec => on(`clicked:repeating_${sec}:gpost`, ev => {
            const id = (ev.sourceAttribute || ev.triggerName).split("_")[2]; const p = `repeating_${sec}_${id}_`;
            const ks = [p + "name", p + "notes", "game_line"]; Object.keys(R15_RN).forEach(k => ["on", "name", "desc"].forEach(x => ks.push(p + `f_${k}_${x}`)));
            getAttrs(ks, v => {
                const gl = r15Fx(v.game_line) || "werewolf";
                const fs = Object.keys(R15_RN).filter(k => v[p + `f_${k}_on`] === "1").map(k => `${R15_RN[k]}: ${r15Fx(v[p + `f_${k}_name`]) || "-"}`).join("; ");
                const kv = {charname: "@{character_name}", ["gl_" + gl]: "1", splat: gl, kind: `${sec === "wgifts" ? "Wolf" : "Shadow"} Gift`, name: r15Fx(v[p + "name"]) || "Gift", f_fdesc: fs || "No Facets learned", f_notes: r15Fx(v[p + "notes"])};
                startRoll("&{template:cofd-entry} " + Object.keys(kv).filter(x => kv[x]).map(x => `{{${x}=${kv[x]}}}`).join(" "), r => finishRoll(r.rollId));
            });
        }));
'''
    o = '        on("sheet:opened", r15CostMig);'
    assert o in h
    h = h.replace(o, js + o)
    c += '\n'.join([
        f'{Q} .sheet-gift button.sheet-gift-nmb {{ display: block; width: 100%; box-sizing: border-box; margin: 0 !important; padding: 0 16px !important; background: rgba(0,0,0,0) !important; border: none !important; box-shadow: none !important; color: inherit; font-family: inherit; font-size: 14px; font-weight: bold; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; }}',
        f'{Q} .sheet-gift button.sheet-gift-nmb:hover {{ color: var(--color-game-line, #c8732a); }}',
        f'{Q} .sheet-gift input.sheet-gift-nmed {{ display: block; width: 100%; box-sizing: border-box; margin: 0 0 4px; text-align: center; }}',
        f'{Q} .sheet-bignotes {{ margin: 4px 0 10px; }}',
        f'{Q} textarea.sheet-bignotes-ta {{ display: block; width: 100%; box-sizing: border-box; min-height: 420px; resize: vertical; }}',
        f'{Q} .sheet-entry-section.sheet-notes:not(:has(.repitem)) {{ display: none; }}',
        f'{Q} .sheet-page1 .sheet-main-forms, {Q} .sheet-ut-row {{ display: none !important; }}',
        f'{Q} .sheet-gifts, {Q} .sheet-gifts .repcontainer, {Q} .sheet-gifts fieldset + .repcontainer {{ overflow-x: hidden !important; max-width: 100%; }}',
        f'{Q} .sheet-det-splat input[name="attr_det_first_change"] {{ background: rgba(0,0,0,0) !important; border: none !important; border-bottom: 1px solid var(--color-game-line, #888) !important; box-shadow: none !important; color: inherit !important; border-radius: 0 !important; height: auto; padding: 2px 4px; }}',
        f'{Q} .sheet-entry-body .sheet-pw-box ~ label:has(> input[name="attr_pool"]), {Q} .sheet-entry-body .sheet-pw-box ~ label:has(> input[name="attr_pool_dice"]) {{ display: none !important; }}',
        f'{Q} .sheet-entry-body .sheet-pw-box .sheet-pw-row {{ display: flex !important; flex-wrap: wrap; align-items: center; gap: 4px 10px; }}',
        f'{Q} .sheet-entry-body .sheet-pw-box .sheet-pw-row > b {{ flex: 0 0 100%; }}',
        f'{Q} .sheet-entry-body .sheet-pw-box .sheet-pw-row > label {{ display: inline-flex !important; align-items: center; gap: 4px; flex: 1 1 40%; min-width: 0; width: auto !important; }}',
        f'{Q} .sheet-entry-body .sheet-pw-box .sheet-pw-row > label select {{ min-width: 0; flex: 1 1 auto; width: auto !important; }}',
        f'{Q} .repcontainer input.sheet-gfx-sw:checked {{ background: var(--color-game-line, #b4743a) !important; }}',
        f'{Q} .repcontainer label.sheet-switch > input:checked + .sheet-sw-track {{ background: var(--color-game-line, #b4743a) !important; }}',
    ]) + '\n'
    return h, c


def r60(h, c):
    # (60) facet slide toggles: the checkbox itself is invisible; a real span draws the track/knob (no native ring can show)
    Q = f'{P}{P}{P}'
    h, n = re.subn(r'(<input type="checkbox" class="(?:sheet-)?gfx-sw"[^>]*/>)', r'<span class="sheet-gfx-swr">\1<span class="sheet-gfx-trk"></span></span>', h)
    assert n > 10, n
    G = f'{Q}{P} .sheet-gifts'
    c += '\n'.join([
        f'{G} .sheet-gfx-swr {{ position: relative; display: inline-block !important; flex: 0 0 24px !important; width: 24px !important; height: 12px !important; min-width: 24px !important; padding: 0 !important; margin: 0 !important; overflow: visible !important; vertical-align: middle; }}',
        f'{G} .sheet-gfx-swr input.sheet-gfx-sw {{ -webkit-appearance: none !important; -moz-appearance: none !important; appearance: none !important; position: absolute !important; inset: 0; width: 24px !important; height: 12px !important; margin: 0 !important; padding: 0 !important; opacity: 0 !important; z-index: 2; cursor: pointer; border: 0 !important; background: none !important; box-shadow: none !important; }}',
        f'{G} .sheet-gfx-swr input.sheet-gfx-sw::before, {G} .sheet-gfx-swr input.sheet-gfx-sw::after {{ content: none !important; display: none !important; }}',
        f'{G} .sheet-gfx-trk {{ position: absolute; display: block !important; left: 0 !important; top: 0 !important; width: 24px !important; height: 12px !important; border-radius: 6px !important; background: #555 !important; pointer-events: none; }}',
        f'{G} .sheet-gfx-trk::after {{ content: ""; position: absolute; left: 1px; top: 1px; width: 10px; height: 10px; border-radius: 50%; background: #ddd; transition: left .15s; }}',
        f'{G} .sheet-gfx-swr input.sheet-gfx-sw:checked + .sheet-gfx-trk {{ background: var(--color-game-line, #b4743a) !important; }}',
        f'{G} .sheet-gfx-swr input.sheet-gfx-sw:checked + .sheet-gfx-trk::after {{ left: 13px; background: #fff; }}',
        f'{G} .sheet-gfx-top:has(input.sheet-gfx-sw:not(:checked)) .sheet-gf-ic {{ filter: grayscale(1); opacity: .45; }}',
        f'{G} .sheet-gift-tg {{ -webkit-appearance: none !important; -moz-appearance: none !important; border: 0 !important; background: none !important; box-shadow: none !important; }}',
        f'{G} .sheet-gift-tg::after, {G} .sheet-gfx-tg::after {{ content: none !important; }}',
        f'{G} .sheet-gfx-tg {{ -webkit-appearance: none !important; -moz-appearance: none !important; border: 0 !important; background: none !important; box-shadow: none !important; }}',
        f'{Q}{P} .sheet-background > button.sheet-toggle.sheet-page-settings {{ vertical-align: baseline !important; position: static !important; top: auto !important; right: auto !important; align-self: auto !important; font-size: 14px !important; line-height: 20px !important; padding: 2px 6px !important; margin-top: 6px !important; margin-bottom: 0 !important; transform: none !important; }}',
        # (61) gift-level note field hidden, data kept
        f'{G} textarea.sheet-gift-notes {{ display: none !important; }}',
    ]) + '\n'
    return h, c


def r64(h, c):
    # (64) Facet edit panel: no Mod field (roll prompts ?{Modifier}), no source/page field, clean rows
    o = 'const mod = parseInt(v[f + "mod"]) || 0;'
    assert h.count(o) == 1, h.count(o)
    h = h.replace(o, 'const mod = 0; // r15b (64): stored Facet mod ignored; the roll prompts for a modifier')
    G = f'{P}{P}{P}{P} .sheet-gifts .sheet-gfx-body'
    F = "font-family: 'Sorts Mill Goudy', serif !important; font-size: 13px !important; text-transform: none !important;"
    c += '\n'.join([
        f'{G} label.sheet-gfn:has(input[name$="_mod"]), {G} input[name$="_src"] {{ display: none !important; }}',
        f'{G} .sheet-gfx-r {{ display: flex !important; flex-wrap: wrap !important; align-items: center !important; gap: 4px 6px !important; width: 100% !important; box-sizing: border-box; }}',
        f'{G} .sheet-gfx-r > input[type=text] {{ flex: 1 1 120px !important; min-width: 110px !important; width: auto !important; box-sizing: border-box; }}',
        f'{G} .sheet-gfx-r > label.sheet-gfn {{ display: inline-flex !important; align-items: center !important; gap: 6px !important; margin: 0 !important; white-space: nowrap; {F} }}',
        f'{G} .sheet-gfx-r > label.sheet-gfn:has(input[name$="_cost"]) {{ flex: 0 0 auto !important; }}',
        f'{G} .sheet-gfx-r > label.sheet-gfn input[name$="_cost"] {{ width: 48px !important; min-width: 48px !important; height: 22px; text-align: center; box-sizing: border-box; }}',
        f'{G} .sheet-gfx-r > select.sheet-gfx-ct {{ flex: 1 1 60px !important; min-width: 60px !important; width: auto !important; }}',
        f'{G} .sheet-gfx-r > label.sheet-gfn:has(input[name$="_addren"]) {{ flex: 0 0 100% !important; justify-content: flex-start; }}',
        f'{G} .sheet-gfx-r:has(> select.sheet-gfx-ct) {{ display: grid !important; grid-template-columns: auto minmax(0,1fr) !important; }}',
        f'{G} .sheet-gfx-r:has(> select.sheet-gfx-ct) > label.sheet-gfn {{ width: auto !important; max-width: none !important; }}',
        f'{G} .sheet-gfx-r > label.sheet-gfn:has(input[name$="_addren"]) {{ grid-column: 1 / -1 !important; }}',
        f'{G} .sheet-gfx-r:has(> select[name$="_attr"]) {{ display: grid !important; grid-template-columns: minmax(0,1fr) minmax(0,1fr) !important; }}',
        f'{G} .sheet-gfx-r > select[name$="_attr"], {G} .sheet-gfx-r > select[name$="_skill"] {{ width: 100% !important; min-width: 0 !important; box-sizing: border-box; {F} }}',
    ]) + '\n'
    return h, c


def r65(h, c):
    # (65) skill rows: compact, one straight border-bottom per row; no partial borders on toggle / caret / name
    R = f'{P}{P}{P}{P} .sheet-skills > div:not(.sheet-section-header):not(.sheet-subheader):not(.sheet-subsubheader):not(.sheet-spec-row)'
    c += '\n'.join([
        f'{P}{P}{P}{P} .sheet-skills {{ row-gap: 0 !important; }}',
        f'{R} {{ display: flex !important; align-items: center !important; box-sizing: border-box !important; min-height: 20px !important; height: auto !important; margin: 0 !important; padding: 1px 0 !important; border: 0 !important; border-bottom: 1px solid rgba(127,127,127,.55) !important; }}',
        f'{R} > button.sheet-toggle, {R} > button.sheet-spec-caret, {R} > .sheet-dots {{ border-top: 0 !important; border-left: 0 !important; border-right: 0 !important; border-bottom: 0 !important; box-shadow: none !important; margin-top: 0 !important; margin-bottom: 0 !important; }}',
        f'{R} > button.sheet-toggle {{ padding-top: 0 !important; padding-bottom: 0 !important; line-height: 18px !important; }}',
        f'{P}{P}{P}{P} .sheet-skills > div.sheet-spec-row {{ min-height: 0 !important; margin: 0 !important; padding: 0 !important; border: 0 !important; }}',
        f'{R} > input[type=checkbox] {{ margin: 0 4px 0 0 !important; vertical-align: middle; align-self: center; }}',
    ]) + '\n'
    return h, c


def r66(h, c):
    # (66a) form selects use the skill-name font; (66b) equal-height Form cards
    X = f'{P}{P}{P}{P}'
    FN = "font-family: 'Sorts Mill Goudy', 'Goudy Old Style', Garamond, Georgia, serif !important; font-size: 13px !important; font-weight: 700 !important; line-height: 18px !important; font-style: normal !important; letter-spacing: normal !important; text-transform: none !important;"
    c += '\n'.join([
        f'{X} select[name="attr_form"], {X} select[name="attr_form"] option, {X} select.sheet-rp-formsel, {X} select.sheet-rp-formsel option {{ {FN} }}',
        f'{X} .sheet-fcards {{ align-items: stretch !important; grid-auto-rows: 1fr !important; }}',
        f'{X} .sheet-fcards > .sheet-fcard {{ height: 100% !important; box-sizing: border-box !important; display: flex; flex-direction: column !important; }}',
        f'{X} .sheet-fcards > .sheet-fcard > .sheet-fc-detail {{ flex: 1 1 auto !important; }}',
    ]) + '\n'
    return h, c


def r67(h, c):
    # (67) action menus: flat black; Roll (pay cost) / Roll without paying / Post to chat (no roll); roll items hidden with no pool
    out, pos, n = [], 0, 0
    for m in re.finditer(r'<span class="(?:sheet-)?amenu-list">(.*?)</span></span>', h, re.S):
        body = m.group(1)
        hp = re.search(r'<input type="hidden" class="(?:sheet-)?haspool"[^>]*/>', body)
        rr = re.search(r'<button type="action"[^>]*name="act_rr-roll">.*?</button>', body, re.S)
        pr = re.search(r'<button type="action"[^>]*name="act_proll"[^>]*>.*?</button>', body, re.S)
        af = re.search(r'<input type="hidden" class="(?:sheet-)?pw-auto-flag"[^>]*/>', body)
        posts = list(re.finditer(r'<button type="roll" class="(?:sheet-)?entry-post" name="roll_post" title="Post to chat" value="([^"]*)"', h[:m.start()]))
        assert hp and rr and posts, m.start()
        val = posts[-1].group(1).replace(' @{roll_part}', '').replace('@{roll_part}', '')
        pr_s = re.sub(r'<span class="(?:sheet-)?am-l">.*?</span>', '<span class="sheet-am-l">Roll (pay cost)</span>', pr.group(0)) if pr else ''
        rr_s = re.sub(r'<span class="(?:sheet-)?am-l">.*?</span>', '<span class="sheet-am-l">Roll without paying</span>', rr.group(0)).replace('title="Roll dice pool"', 'title="Roll the pool without paying any cost"')
        post = f'<button type="roll" class="sheet-am-post" name="roll_ampost" title="Post the description to chat (no roll)" value="{val}"><span class="sheet-am-l">Post to chat</span></button>'
        new = '<span class="sheet-amenu-list">' + hp.group(0) + pr_s + rr_s + (af.group(0) if af else '') + post + '</span></span>'
        out.append(h[pos:m.start()]); out.append(new); pos = m.end(); n += 1
    out.append(h[pos:]); h = ''.join(out)
    assert n >= 20, n
    X = f'{P}{P}{P}{P}'
    c += '\n'.join([
        f'{X} .sheet-amenu .sheet-amenu-list {{ background: #000 !important; background-image: none !important; opacity: 1 !important; border: 1px solid var(--color-game-line, #b4743a) !important; box-shadow: none !important; }}',
        f'{X} .sheet-amenu .sheet-amenu-list > button {{ background: #000 !important; background-image: none !important; }}',
        f'{X} .sheet-amenu .sheet-amenu-list > button:hover {{ background: #1a1a1a !important; }}',
        f'{X} .sheet-amenu .sheet-amenu-list > input.sheet-haspool[value="0"] ~ button.sheet-entry-roll, {X} .sheet-amenu .sheet-amenu-list > input.sheet-haspool[value=""] ~ button.sheet-entry-roll {{ display: none !important; }}',
        f'{X} .sheet-amenu .sheet-amenu-list > button.sheet-am-post {{ display: flex !important; align-items: center; gap: 6px; width: 100%; text-align: left; border: 0 !important; color: inherit; font-family: inherit; font-size: inherit; padding: inherit; }}',
    ]) + '\n'
    return h, c


def r68(h, c):
    X = f'{P}{P}{P}{P}'
    # (68) Roll20 does not resolve @{} in titles: static titles instead
    for a, b in [('title="@{potency_tip}"', 'title="Power stat: click to add it to the dice pool"'),
                 ('title="@{morality_tip}"', 'title="Morality trait (Integrity, Humanity, Harmony, Wisdom, Clarity...)"'),
                 ('title="@{resource_name}"', 'title="Power resource (Vitae, Essence, Mana, Glamour...)"'),
                 ('title="Clear @{potency_name}"', 'title="Clear power stat"'),
                 ('title="Mark / clear @{resource_name} box"', 'title="Mark / clear resource box"')]:
        h = h.replace(a, b)
    h = re.sub(r'title="Set @\{potency_name\} to (\d+)"', r'title="Set power stat to \1"', h)
    # (71 replaced) First Change: one textarea, placed above the Height and Weight by Form table
    m = re.search(r'<div class="(?:sheet-)?game-line (?:sheet-)?werewolf2 (?:sheet-)?breeds2 (?:sheet-)?det-splat"><div class="(?:sheet-)?subheader"><span data-i18n="det-werewolf">First Change</span></div>.*?<textarea name="attr_det_first_change_notes"></textarea></label></div>', h, re.S)
    assert m
    h = h[:m.start()] + h[m.end():]
    blk = ('<div class="sheet-game-line sheet-werewolf2 sheet-breeds2 sheet-fc-bio"><div class="sheet-subheader"><span data-i18n="det-werewolf">First Change</span></div>'
           '<input type="hidden" name="attr_det_first_change" value="" /><input type="hidden" name="attr_det_first_change_notes" value="" /><input type="hidden" name="attr_det_fc_mig" value="" />'
           '<label class="sheet-wide sheet-fc-bio-l"><textarea class="sheet-fc-bio-ta" name="attr_det_first_change_all" placeholder="Date, place and circumstances"></textarea></label></div>')
    k = re.search(r'<div class="(?:sheet-)?game-line (?:sheet-)?werewolf2 (?:sheet-)?breeds2"><div class="(?:sheet-)?subheader"><span data-i18n="form-hw">', h)
    assert k
    h = h[:k.start()] + blk + h[k.start():]
    js = r'''
        // r15b (71): First Change date/place + circumstances merged once into one textarea (old attrs kept)
        on("sheet:opened", () => getAttrs(["det_fc_mig", "det_first_change", "det_first_change_notes", "det_first_change_all"], v => {
            if (v.det_fc_mig === "1") return; const u = {det_fc_mig: "1"};
            if (!(v.det_first_change_all || "").trim()) { const a = (v.det_first_change || "").trim(), b = (v.det_first_change_notes || "").trim();
                const t = [a, b].filter(Boolean).join("\n\n"); if (t) u.det_first_change_all = t; }
            setAttrs(u, {silent: true}); }));
        // r15b (70): action menus never come back open after a reload / paste
        on("sheet:opened", () => ["merits","tactics","endowments","disciplines","devotions","vrites","writes","rotes","praxes","transmutations","bestowments","contracts","goblincontracts","keys","ceremonies","utterances","affinities","vessels","embeds","exploits","covers","atavisms","nightmares","favors","bspecials","fetishes","customrolls"].forEach(sec => getSectionIDs(sec, ids => {
            if (!ids.length) return; getAttrs(ids.map(id => `repeating_${sec}_${id}_amenu`), v => { const u = {}; Object.keys(v).forEach(k => { if (v[k] === "1") u[k] = "0"; });
                if (Object.keys(u).length) setAttrs(u, {silent: true, allowOpen: true}); }); })));
'''
    o = '        on("sheet:opened", r15CostMig);'
    assert o in h
    h = h.replace(o, js + o)
    c += '\n'.join([
        f'{X} .sheet-fc-bio {{ margin: 6px 0 4px !important; }}',
        f'{X} .sheet-fc-bio label.sheet-fc-bio-l {{ display: block !important; width: 100% !important; margin: 0 !important; }}',
        f'{X} .sheet-fc-bio textarea.sheet-fc-bio-ta {{ display: block; width: 100% !important; box-sizing: border-box; min-height: 70px; resize: vertical; }}',
        # (72) splat merit pill = same pill as the other categories
        f'{X} .sheet-entry > input.sheet-mcat-flag[value="Supernatural"] ~ .sheet-entry-head .sheet-mcat-badge {{ font-size: 0 !important; line-height: 0 !important; padding: 0 6px !important; margin: 0 4px !important; width: auto !important; min-width: 0 !important; height: auto !important; border-radius: 7px !important; border: 1px solid currentColor !important; }}',
        f'{X} .sheet-entry > input.sheet-mcat-flag[value="Supernatural"] ~ .sheet-entry-head .sheet-mcat-badge::after {{ display: inline-block !important; font: bold 9px/13px Arial, sans-serif !important; letter-spacing: .4px !important; text-transform: uppercase !important; vertical-align: top !important; margin: 0 !important; padding: 0 !important; }}',
        # (73) select options: splat colour + black text on checked / hover / focus
        f'{X} select option:checked, {X} select option:hover, {X} select option:focus {{ background-color: var(--color-game-line, #b4743a) !important; color: #000 !important; box-shadow: 0 0 10px 100px var(--color-game-line, #b4743a) inset !important; }}',
        # (69) menu above everything, opens to the left under the trigger
        f'{X} .sheet-amenu {{ position: relative !important; }}',
        f'{X} .sheet-amenu .sheet-amenu-list {{ position: absolute !important; right: 0 !important; top: 100% !important; z-index: 1000 !important; min-width: 170px; }}',
        f'{X} .repitem:has(.sheet-amenu-tg:checked) {{ position: relative; z-index: 999 !important; }}',
        f'{X} .sheet-amenu-tg:not(:checked) ~ .sheet-amenu-list {{ display: none !important; }}',
    ]) + '\n'
    return h, c


def r74(h, c):
    X = f'{P}{P}{P}{P}'
    # (74) Config tab: same element and classes as the other tabs; drop its special-case CSS
    h = h.replace('class="sheet-toggle sheet-page-settings" name="act_page_settings"', 'class="sheet-toggle sheet-page-cfg" name="act_page_settings"')
    c = re.sub(r'[^{}]*sheet-page-settings[^{}]*\{[^{}]*\}', lambda m: '' if '[value=' not in m.group(0) or 'button' in m.group(0) else m.group(0), c)
    c = c.replace('input.sheet-page[value="details"] ~ button.sheet-page-details {', 'input.sheet-page[value="details"] ~ button.sheet-page-details, input.sheet-page[value="settings"] ~ button.sheet-page-cfg {', 1)
    # (76) power stat header tooltip names the splat's actual trait
    def tip(m):
        name = m.group(2).strip() or 'Power stat'
        return m.group(1) + f'title="{name}: click to add it to the dice pool">' + m.group(2)
    h = re.sub(r'(<button type="action" class="[^"]*" name="act_potency"[^>]*?)title="Power stat: click to add it to the dice pool">([^<]*)', tip, h)
    # (75) outside click closes menus: toggle wrapped in a label with a full-sheet backdrop
    h = h.replace('<input type="checkbox" class="sheet-amenu-tg" name="attr_amenu" value="1" title="Actions" />',
                  '<label class="sheet-amenu-lb"><input type="checkbox" class="sheet-amenu-tg" name="attr_amenu" value="1" title="Actions" /><span class="sheet-amenu-bd"></span></label>')
    c = c.replace('.sheet-amenu > input.sheet-amenu-tg', '.sheet-amenu input.sheet-amenu-tg')
    c += '\n' + '\n'.join([
        f'{X} .sheet-amenu > label.sheet-amenu-lb {{ display: block; margin: 0; padding: 0; position: static; cursor: pointer; }}',
        f'{X} .sheet-amenu span.sheet-amenu-bd {{ display: none; }}',
        f'{X} .sheet-amenu input.sheet-amenu-tg:checked + span.sheet-amenu-bd {{ display: block !important; position: fixed !important; left: -100vw; top: -100vh; width: 300vw; height: 300vh; background: rgba(0,0,0,0) !important; z-index: 998 !important; cursor: default; }}',
        f'{X} .sheet-amenu:has(input.sheet-amenu-tg:checked) > .sheet-amenu-list {{ display: flex !important; }}',
    ])
    return h, c


def r78(h, c):
    # (78/79) r65's skill-row rule (display:flex !important at high specificity) beat the era and splat hide rules
    # and flattened the Renown block: scope it to plain rows and re-assert the hides above it
    R = f'{P}{P}{P}{P} .sheet-skills > div:not(.sheet-section-header):not(.sheet-subheader):not(.sheet-subsubheader):not(.sheet-spec-row)'
    c = c.replace(R, R + ':not(.sheet-skills-renown):not(.sheet-game-line)')
    # era skills built like the other rows (caret, skill marks, specialties)
    m = re.search(r'<div>\s*<input type="hidden" class="sheet-if" name="attr_enable_profession">\s*<input type="hidden" class="sheet-flag" name="attr_larceny_flag".*?</div>(?=\s*<div class="sheet-dots">)', h, re.S)
    sp = re.search(r'<div class="sheet-spec-row"><input type="hidden" class="sheet-spec-openflag" name="attr_larceny_spec_open".*?</div></div></div>', h, re.S)
    for e, t in (('ride', 'Ride'), ('enigmas', 'Enigmas'), ('archery', 'Archery')):
        o = re.search(r'<div class="sheet-is-' + e + r'-era">.*?</div>', h, re.S)
        if not (m and sp and o) or ('act_' + e + '_spec_toggle') in h:
            continue
        row = m.group(0).replace('larceny', e).replace('Larceny', t).replace('<div>', f'<div class="sheet-is-{e}-era">', 1)
        dm = re.search(r'(<div class="sheet-is-' + e + r'-era sheet-dots">.*?</div>)', h[o.end():], re.S)
        spec = sp.group(0).replace('larceny', e).replace('<div class="sheet-spec-row">', f'<div class="sheet-spec-row sheet-is-{e}-era">', 1)
        h = h[:o.start()] + row + h[o.end():o.end() + dm.end()] + spec + h[o.end() + dm.end():]
    def addsk(m):
        arr = m.group(1)
        for e in ('ride', 'enigmas', 'archery'):
            if f'"{e}"' not in arr and f"'{e}'" not in arr:
                arr = arr[:-1] + f', "{e}"]'
        return 'const SKILLS = ' + arr
    h = re.sub(r'const SKILLS = (\[[^\]]*\])', addsk, h, 1)
    Y = f'{P}{P}{P}{P}{P}'
    rules = []
    for e in ('ride', 'enigmas', 'archery'):
        for sep in (' ~ ', ' ~ * '):
            rules.append(f'{Y} input.sheet-{e}-era[value="1"]{sep}.sheet-not-{e}-era, {Y} input.sheet-{e}-era:not([value="1"]){sep}.sheet-is-{e}-era')
    c += '\n' + ', '.join(rules) + ' { display: none !important; }'
    return h, c


R81_SK = [('Mental', [('academics', 'Academics'), ('computer', 'Computer'), ('crafts', 'Crafts'), ('investigation', 'Investigation'), ('medicine', 'Medicine'), ('occult', 'Occult'), ('politics', 'Politics'), ('science', 'Science')]),
          ('Physical', [('athletics', 'Athletics'), ('brawl', 'Brawl'), ('drive', 'Drive'), ('firearms', 'Firearms'), ('larceny', 'Larceny'), ('stealth', 'Stealth'), ('survival', 'Survival'), ('weaponry', 'Weaponry')]),
          ('Social', [('animalken', 'Animal Ken'), ('empathy', 'Empathy'), ('expression', 'Expression'), ('intimidation', 'Intimidation'), ('persuasion', 'Persuasion'), ('socialize', 'Socialize'), ('streetwise', 'Streetwise'), ('subterfuge', 'Subterfuge')])]


def r87cSafe(s):
    return s.replace('expression', 'xprssn')


def r87cNm(v):
    # name="...expression..." without the word: [name^="..expr"][name$="ession.."] (same element, the names are unique)
    if 'expression' not in v:
        return f'[name="{v}"]'
    k = v.index('expression') + 4
    return f'[name^="{v[:k]}"][name$="{v[k:]}"]'


def r81(h, c):
    X = f'{P}{P}{P}{P}'
    Y = f'{P}{P}{P}{P}{P}'
    G = f'{P}{P}{P}{P} .sheet-gifts'
    # (81) Facet Action: select (Instant / Extended / Reflexive); Duration stays text; old attr kept
    def sel(m):
        k = m.group(1)
        return (f'<select class="sheet-gfx-act" name="attr_f_{k}_actsel" title="Action"><option value="">-</option><option value="Instant">Instant</option>'
                f'<option value="Extended">Extended</option><option value="Reflexive">Reflexive</option></select>')
    h = re.sub(r'<input type="text" name="attr_f_(cun|glo|hon|pur|wis)_action" placeholder="Action / duration" />', sel, h)
    h = h.replace('const fl = ["name", "on", "attr", "skill", "mod", "cost", "ctype", "addren", "desc", "action",', 'const fl = ["name", "on", "attr", "skill", "mod", "cost", "ctype", "addren", "desc", "action", "actsel",', 1)
    h = h.replace('f_action: r15Fx(v[f + "action"])', 'f_action: r15Fx(v[f + "actsel"])', 1)
    a = 'on("sheet:opened", r15CostMig);'
    assert a in h
    h = h.replace(a, a + '''
        const r81ActMig = () => ["gifts", "wgifts"].forEach(sec => getSectionIDs(`repeating_${sec}`, ids => {
            const ks = ["cun", "glo", "hon", "pur", "wis"], names = [];
            ids.forEach(id => ks.forEach(k => ["action", "actsel", "actmig"].forEach(x => names.push(`repeating_${sec}_${id}_f_${k}_${x}`))));
            if (!names.length) return;
            getAttrs(names, v => { const u = {};
                ids.forEach(id => ks.forEach(k => { const f = `repeating_${sec}_${id}_f_${k}_`;
                    if (v[f + "actmig"] === "1") return; u[f + "actmig"] = "1";
                    const m = /instant|extended|reflexive/i.exec(v[f + "action"] || "");
                    if (m && !v[f + "actsel"]) u[f + "actsel"] = m[0][0].toUpperCase() + m[0].slice(1).toLowerCase(); }));
                if (Object.keys(u).length) setAttrs(u, {silent: true}); });
        }));
        on("sheet:opened", r81ActMig);''', 1)
    c += '\n' + '\n'.join([
        f'{G} .sheet-gfx-r > select.sheet-gfx-act {{ flex: 0 0 96px !important; width: 96px !important; height: 20px !important; margin: 0 !important; padding: 0 2px !important; font: 700 13px/18px "Sorts Mill Goudy", "Goudy Old Style", Garamond, Georgia, serif !important; background: #1a1a1a !important; color: #e8e8e8 !important; border: 1px solid rgba(127,127,127,.6) !important; border-radius: 3px !important; }}',
    ])
    # (82) Config: per-skill show toggles; Dark Eras skills kept in their own group
    cols = ''.join(
        f'<div class="sheet-cfg-skcol"><div class="sheet-cfg-skh">{grp}</div>' + ''.join(
            f'<label class="sheet-cfg-sw" title="Show {t} on the Main tab"><input type="checkbox" name="attr_sk_show_{s}" value="1" checked="checked" /><span class="sheet-cfg-knob"></span><span>{t}</span></label>'
            for s, t in sk) + '</div>' for grp, sk in R81_SK)
    card = ('<div class="sheet-cfg-card sheet-cfg-skills" title="Hide individual skills on the Main tab"><div class="sheet-subheader sheet-cfg-head">Skills</div>'
            f'<div class="sheet-cfg-body sheet-cfg-skgrid">{cols}</div></div>')
    e = '<div class="sheet-cfg-card sheet-cfg-eras '
    assert e in h
    h = h.replace(e, card + e, 1)
    h = h.replace('<div class="sheet-subheader sheet-cfg-head">Dark Eras</div>', '<div class="sheet-subheader sheet-cfg-head">Dark Eras skills</div>', 1)
    allsk = [s for _, sk in R81_SK for s, _ in sk]
    k = '<div class="sheet-corporeal sheet-skills">'
    assert k in h
    h = h.replace(k, k + ''.join(f'<input type="hidden" class="sheet-skh sheet-skh-{r87cSafe(s)}" name="attr_sk_show_{s}" value="1" />' for s in allsk), 1)
    hide = []
    for s in allsk:
        # (87c) Roll20's legacy roll-template sanitizer drops ALL template CSS if the word "expression" appears anywhere
        i = f'{Y} .sheet-skills > input.sheet-skh-{r87cSafe(s)}[value="0"] ~ '
        hide += [i + f'div:has(> button{r87cNm("act_" + s)})', i + f'div.sheet-dots:has(> input{r87cNm("attr_" + s)})', i + f'div.sheet-spec-row:has(input{r87cNm("attr_" + s + "_spec_open")})']
    c += '\n' + ', '.join(hide) + ' { display: none !important; }'
    S = f'{X} .sheet-settings'
    c += '\n' + '\n'.join([
        f'{S} .sheet-cfg-skgrid {{ display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 2px 12px; }}',
        f'{S} .sheet-cfg-skcol {{ display: flex; flex-direction: column; gap: 3px; min-width: 0; }}',
        f'{S} .sheet-cfg-skh {{ font: 700 12px/16px "Sorts Mill Goudy", "Goudy Old Style", Garamond, Georgia, serif; color: var(--color-game-line, #b4743a); border-bottom: 1px solid rgba(127,127,127,.4); margin-bottom: 2px; }}',
        f'{S} .sheet-cfg-skgrid .sheet-cfg-sw > span:last-child {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 12px !important; }}',
    ])
    return h, c


def r83(h, c):
    G = f'{P}{P}{P}{P} .sheet-gifts'
    Y = f'{P}{P}{P}{P}{P} .sheet-gifts'
    # (85) row ids from click events: Roll20 row ids can contain "_", so split("_")[2] cut them short and the
    # handler read empty attrs; take everything between the section prefix and the action name
    h = h.replace('const id = (ev.sourceAttribute || ev.triggerName).split("_")[2];', 'const id = r85Id(ev, sec);')
    h = h.replace('const id = ev.sourceAttribute.split("_")[2];', 'const id = r85Id(ev, sec);')
    k = '<script type="text/worker">'
    assert k in h
    h = h.replace(k, k + '''
        const r85Id = (ev, sec) => { const s = String(ev.sourceAttribute || ev.triggerName || "").replace(/^clicked:/, ""); const pre = `repeating_${sec}_`;
            const i = s.toLowerCase().indexOf(pre); const rest = i < 0 ? s : s.slice(i + pre.length);
            const m = /^(-[A-Za-z0-9_-]{19})(?=_|$)/.exec(rest); return m ? m[1] : rest.split("_")[0]; };''', 1)
    assert 'split("_")[2]' not in h
    # (85) Roll20 does not reliably fire clicked: events for repeating action buttons whose names contain "_":
    # froll_<k> -> froll<k>
    for k in ('cun', 'glo', 'hon', 'pur', 'wis'):
        h = h.replace(f'name="act_froll_{k}"', f'name="act_froll{k}"')
    a = 'on(`clicked:repeating_${sec}:froll_${k}`'
    assert a in h
    h = h.replace(a, 'on(`clicked:repeating_${sec}:froll${k}`', 1)
    # (85) resolve the roll suffix in the worker: an empty success_target or modifier prompt broke the inline roll
    a = 'getAttrs([p + "name", "deduct_auto",'
    assert a in h
    h = h.replace(a, 'getAttrs([p + "name", "rolltype_eff", "success_target", "deduct_auto",', 1)
    a = 'tpl += dice > 0 ? ` {{roll=[[{((${dice}+?{@{modifiermacro}|0}+@{wound_penalty}+@{wp_dice}+@{cond_mod}+@{spec_bonus})@{rolltype_eff}`'
    assert a in h
    h = h.replace(a, 'tpl += dice > 0 ? ` {{roll=[[{((${dice}+?{Modifier|0}+@{wound_penalty}+@{wp_dice}+@{cond_mod}+@{spec_bonus})${r85Rt(v)}`', 1)
    k2 = 'const r85Id = '
    h = h.replace(k2, 'const r85Rt = (v) => { const t = parseInt(v.success_target) || 8; let r = String(v.rolltype_eff || "").replace(/@\\{success_target\\}/g, t);'
                  ' if (!/\\]\\]\\}\\}$/.test(r) || /@\\{/.test(r)) r = `)d10!cs>10}>${t}]]}}`; return r; };\n        ' + k2, 1)
    # (83/84) Facet panel: Effects by outcome / Requires roll toggles
    def tg(m):
        f = m.group(1)
        return (m.group(0) + f'<div class="sheet-gfx-r sheet-gfx-tgl">'
                f'<label class="sheet-gfn" title="Off: one static effect. On: separate effects for Dramatic Failure, Failure, Success and Exceptional Success"><span class="sheet-gfx-swr"><input type="checkbox" class="sheet-gfx-sw sheet-gfx-byo" name="attr_f_{f}_byout" value="1" /><span class="sheet-gfx-trk"></span></span>Effects by outcome</label>'
                f'<label class="sheet-gfn" title="Off: the Facet posts its card without rolling dice"><span class="sheet-gfx-swr"><input type="checkbox" class="sheet-gfx-sw sheet-gfx-nr" name="attr_f_{f}_needroll" value="1" checked /><span class="sheet-gfx-trk"></span></span>Requires roll</label></div>')
    n0 = h.count('placeholder="Description"></textarea>')
    h = re.sub(r'<textarea name="attr_f_(cun|glo|hon|pur|wis)_desc" placeholder="Description"></textarea>', tg, h)
    assert h.count('sheet-gfx-byo') == 10, h.count('sheet-gfx-byo')
    # worker: needroll / byout
    a = '"desc", "action", "actsel",'
    assert a in h
    h = h.replace(a, '"desc", "byout", "needroll", "action", "actsel",', 1)
    a = '                if (v[f + "on"] !== "1") return;\n'
    assert a in h
    h = h.replace(a, '', 1)
    a = 'const st = [v[f + "attr"], v[f + "skill"]].filter(Boolean); if (v[f + "addren"] !== "0") st.push(ren);'
    assert a in h
    h = h.replace(a, 'const st = v[f + "needroll"] === "0" ? [] : [v[f + "attr"], v[f + "skill"]].filter(Boolean); if (v[f + "needroll"] !== "0" && v[f + "addren"] !== "0") st.push(ren);', 1)
    a = 'o_exc: r15Fx(v[f + "oexc"]), o_succ: r15Fx(v[f + "osucc"]), o_fail: r15Fx(v[f + "ofail"]), o_dram: r15Fx(v[f + "odram"])};'
    assert a in h
    h = h.replace(a, a + '\n                    if (v[f + "byout"] !== "1") ["o_exc", "o_succ", "o_fail", "o_dram"].forEach(x => delete kv[x]);'
                  '\n                    if (v[f + "on"] !== "1") kv.f_short = "Facet not learned yet";', 1)
    # migration: outcome texts already filled -> Effects by outcome on (once per Facet, nothing removed)
    a = 'on("sheet:opened", r15CostMig);'
    h = h.replace(a, a + '''
        const r83Mig = () => ["gifts", "wgifts"].forEach(sec => getSectionIDs(`repeating_${sec}`, ids => {
            const ks = ["cun", "glo", "hon", "pur", "wis"], xs = ["oexc", "osucc", "ofail", "odram", "byout", "omig"], names = [];
            ids.forEach(id => ks.forEach(k => xs.forEach(x => names.push(`repeating_${sec}_${id}_f_${k}_${x}`))));
            if (!names.length) return;
            getAttrs(names, v => { const u = {};
                ids.forEach(id => ks.forEach(k => { const f = `repeating_${sec}_${id}_f_${k}_`;
                    if (v[f + "omig"] === "1") return; u[f + "omig"] = "1";
                    if (v[f + "byout"] !== "1" && ["oexc", "osucc", "ofail", "odram"].some(x => (v[f + x] || "").trim())) u[f + "byout"] = "1"; }));
                if (Object.keys(u).length) setAttrs(u, {silent: true}); });
        }));
        on("sheet:opened", r83Mig);''', 1)
    # roll template: without a roll, list every outcome effect that was sent
    i = h.index('<rolltemplate class="sheet-rolltemplate-cofd-entry">'); j = h.index('</rolltemplate>', i); t = h[i:j]
    rows = ''.join(f'{{{{#{k}}}}}<tr><th>{lab}</th><td>{{{{{k}}}}}</td></tr>{{{{/{k}}}}}' for k, lab in
                   [('o_dram', 'Dramatic Failure'), ('o_fail', 'Failure'), ('o_succ', 'Success'), ('o_exc', 'Exceptional Success')])
    a = '{{#f_duration}}<tr><th>Duration</th><td>{{f_duration}}</td></tr>{{/f_duration}}'
    assert a in t
    t = t.replace(a, a + '{{#^roll}}' + rows + '{{/^roll}}', 1)
    h = h[:i] + t + h[j:]
    c += '\n' + '\n'.join([
        f'{Y} .sheet-gfx-body:not(:has(input.sheet-gfx-byo:checked)) > textarea.sheet-gfx-o {{ display: none !important; }}',
        f'{Y} .sheet-gfx-body:has(input.sheet-gfx-nr:not(:checked)) > .sheet-gfx-r:has(select[name$="_attr"]) {{ display: none !important; }}',
        f'{Y} .sheet-gfx-body:has(input.sheet-gfx-nr:not(:checked)) label.sheet-gfn:has(input[name$="_addren"]), {Y} .sheet-gfx-body:has(input.sheet-gfx-nr:not(:checked)) label.sheet-gfn:has(input[name$="_mod"]) {{ display: none !important; }}',
        f'{Y} .sheet-gfx-r.sheet-gfx-tgl {{ display: flex !important; flex-wrap: wrap !important; gap: 2px 10px !important; margin: 0 !important; }}',
        f'{Y} .sheet-gfx-r.sheet-gfx-tgl > label.sheet-gfn {{ display: inline-flex !important; align-items: center; gap: 4px; white-space: nowrap; font-size: 12px; margin: 0 !important; }}',
    ])
    return h, c


def r86(h, c):
    # (86) Facet panel fits its column at any width
    Y = f'{P}{P}{P}{P}{P}{P} .sheet-gifts'
    c += '\n' + '\n'.join([
        f'{Y} .sheet-gfx, {Y} .sheet-gfx-body {{ min-width: 0 !important; max-width: 100% !important; box-sizing: border-box !important; overflow: hidden !important; }}',
        f'{Y} .sheet-gfx-body > *, {Y} .sheet-gfx-body textarea, {Y} .sheet-gfx-r > * {{ min-width: 0 !important; max-width: 100% !important; box-sizing: border-box !important; }}',
        f'{Y} .sheet-gfx-r {{ display: flex !important; flex-wrap: wrap !important; gap: 3px 6px !important; min-width: 0 !important; width: 100% !important; box-sizing: border-box !important; }}',
        f'{Y} .sheet-gfx-r > input[type="text"], {Y} .sheet-gfx-r > select {{ flex: 1 1 60px !important; width: auto !important; }}',
        f'{Y} .sheet-gfx-r > select.sheet-gfx-act {{ flex: 1 1 80px !important; width: auto !important; }}',
        f'{Y} .sheet-gfx-r > label.sheet-gfn {{ display: inline-flex !important; align-items: center; gap: 3px; flex: 0 1 auto !important; white-space: nowrap; }}',
        f'{Y} .sheet-gfx-r label.sheet-gfn input[type="number"] {{ width: 34px !important; min-width: 0 !important; flex: 0 0 34px !important; padding: 0 2px !important; box-sizing: border-box !important; }}',
        f'{Y} .sheet-gfx-r > select.sheet-gfx-ct {{ flex: 0 1 52px !important; width: 52px !important; }}',
        f'{Y} .sheet-gfx-r.sheet-gfx-tgl > label.sheet-gfn {{ flex: 1 1 auto !important; overflow: hidden; text-overflow: ellipsis; }}',
        f'{Y} .sheet-gfx-r > label.sheet-gfn:has(input[name$="_mod"]) {{ display: none !important; }}',
        f'{Y} .sheet-gfx-body:has(input.sheet-gfx-nr:not(:checked)) label.sheet-gfn:has(input[name$="_addren"]) {{ display: none !important; }}',
    ])
    return h, c


def r87(h, c):
    # (86b) cost row: number box + Ess/WP select in their own grid, select fills the rest with its arrow visible
    X = f'{P}{P}{P}{P}'
    n = 0
    def wrap(m):
        nonlocal n
        n += 1
        return '<div class="sheet-gfx-cost">' + m.group(1) + m.group(2) + '</div>'
    h = re.sub(r'(<label class="sheet-gfn">Cost<input type="number" name="attr_f_[a-z]+_cost"[^>]*/></label>)(<select class="sheet-gfx-ct".*?</select>)', wrap, h, flags=re.S)
    assert n == 10, n
    G = f'{X} .sheet-gifts .sheet-gfx-body .sheet-gfx-r'
    c += '\n' + '\n'.join([
        f'{G} > .sheet-gfx-cost {{ display: grid !important; grid-template-columns: auto minmax(0, 1fr); align-items: center; gap: 4px; flex: 1 1 100% !important; width: 100% !important; min-width: 0 !important; max-width: 100% !important; box-sizing: border-box !important; padding: 0 3px 0 0 !important; margin: 0 !important; }}',
        f'{G} > .sheet-gfx-cost > label.sheet-gfn {{ display: inline-flex !important; align-items: center; gap: 3px; text-transform: none !important; font-variant: normal !important; letter-spacing: normal !important; font-size: 13px !important; min-width: 0 !important; margin: 0 !important; white-space: nowrap; }}',
        f'{G} > .sheet-gfx-cost > label.sheet-gfn > input[type="number"] {{ width: 38px !important; min-width: 0 !important; max-width: 38px !important; height: 20px !important; margin: 0 !important; padding: 0 2px !important; box-sizing: border-box !important; }}',
        f'{G} > .sheet-gfx-cost > select.sheet-gfx-ct {{ display: block !important; width: 100% !important; min-width: 0 !important; max-width: 100% !important; height: 20px !important; margin: 0 !important; padding: 0 2px !important; box-sizing: border-box !important; flex: none !important; -webkit-appearance: none !important; appearance: none !important; padding-right: 12px !important; background-image: linear-gradient(45deg, rgba(0,0,0,0) 50%, #bbb 50%), linear-gradient(135deg, #bbb 50%, rgba(0,0,0,0) 50%) !important; background-position: calc(100% - 7px) 8px, calc(100% - 3px) 8px !important; background-size: 4px 4px, 4px 4px !important; background-repeat: no-repeat !important; font-size: 12px !important; line-height: 18px !important; }}',
    ])
    return h, c


def r88(h, c):
    # (87) RR_MAC repeating rolls: same "_" row-id bug as (85); and empty attrs that were never written
    # (hidden inputs with value="") print as "Name|attr" in chat, so send literal row values instead
    a = 'const mm = (ev.sourceAttribute || ev.triggerName || "").match(new RegExp("repeating_" + sec.replace(/[-]/g, "\\\\-") + "_([^_]+)_", "i"));\n                    const id = mm ? mm[1] : "";'
    assert a in h, 'rr id'
    h = h.replace(a, 'const id = r85Id(ev, sec);', 1)
    a = """                    mac = mac.replace(/@\\{([\\w-]+)\\}/g, (a, n) => F.includes(n) ? `@{repeating_${sec}_${id}_${n}}` : a);
                }
                if (k === "sheet") return rrSheet(mac);
                rrRun(mac, false);"""
    assert a in h, 'rr sub'
    h = h.replace(a, """                    const used = [...new Set([...mac.matchAll(/@\\{([\\w-]+)\\}/g)].map(x => x[1]).filter(n => F.includes(n)))];
                    return getAttrs(used.map(n => `repeating_${sec}_${id}_${n}`).concat([`repeating_${sec}_${id}_byout`, `repeating_${sec}_${id}_needroll`]), rv => {
                        if (sec === "merits" && rv[`repeating_${sec}_${id}_byout`] === "0") ["o_dramatic", "o_failure", "o_success", "o_exceptional"].forEach(n => { rv[`repeating_${sec}_${id}_${n}`] = ""; });
                        const m2 = mac.replace(/@\\{([\\w-]+)\\}/g, (a, n) => { if (!F.includes(n)) return a; const x = rv[`repeating_${sec}_${id}_${n}`];
                            // (99) keep real refs (roll parts like atk_rt hold nested @{...} and ]]}}); only blank-out missing attrs and pass multi-line text literally
                            if (x === undefined || x === null || x === "") return "";
                            if (/\\n/.test(x) && !/[@\\[\\]{}|]/.test(x)) return String(x).replace(/\\r/g, "").replace(/[ \\t]+/g, " ").trim().replace(/ *\\n */g, "%NEWLINE%");
                            return `@{repeating_${sec}_${id}_${n}}`; });
                        if (sec === "merits" && rv[`repeating_${sec}_${id}_needroll`] === "0") { const m3 = m2.replace(/\\s*\\{\\{roll=[\\s\\S]*?(?=\\{\\{reroll=|$)/, "").replace(/\\s*\\{\\{reroll=[^}]*\\}\\}/, ""); return k === "sheet" ? rrSheet(m3) : startRoll(m3, r => finishRoll(r.rollId)); }
                        if (k === "sheet") return rrSheet(m2);
                        rrRun(m2, false);
                    });
                }
                if (k === "sheet") return rrSheet(mac);
                rrRun(mac, false);""", 1)
    # (88) Willpower reroll: no "+3" text on the card or the button
    for o, n in [('"{{kind=Willpower reroll (+3)}}"', '"{{kind=Willpower reroll}}"'), ('Willpower reroll (+3 dice) of your last roll', 'Willpower reroll of your last roll'),
                 ('{{wpspend=1}} {{wpst=Willpower reroll: +3 dice, WP ${free - 1}/${max}}}', '{{wpst=Willpower reroll: WP ${free - 1}/${max}}}')]:
        assert o in h, o
        h = h.replace(o, n)
    return h, c


def r89(h, c):
    # (88b) Reroll carries no modifier: same pool exactly, no +3, no Willpower spend
    i = h.index('        on("clicked:wp_reroll", () => getAttrs(')
    j = h.index('        }));\n', i) + len('        }));\n')
    h = h[:i] + """        on("clicked:wp_reroll", () => getAttrs(["rr_last_mac", "rr_last_base", "rr_last_expr"], (v) => {
            const head = "&{template:cofd-entry} {{charname=@{character_name}}} {{kind=Reroll}} ";
            if (!v.rr_last_mac || !v.rr_last_expr) return startRoll(head + "{{name=Nothing to reroll}} {{f_short=Roll something first.}}", r => finishRoll(r.rollId));
            let mac = rrStrip(v.rr_last_mac.replace(/\\{\\{roll=\\[\\[[\\s\\S]*$/, "").replace(/\\{\\{reroll=[^}]*\\}\\}/g, ""));
            mac += v.rr_last_base ? " " + v.rr_last_base : ` {{roll=[[${v.rr_last_expr}]]}}`;
            rrRun(mac.replace(/\\{\\{kind=[^}]*\\}\\}/, "{{kind=Reroll}}"), true);
        }));
""" + h[j:]
    for o, n in [('[Willpower reroll +3]', '[Reroll]'), ('title="Willpower reroll of your last roll"', 'title="Reroll your last roll"'),
                 ('// ---- generic roll path + Willpower reroll', '// ---- generic roll path + Reroll')]:
        assert o in h, o
        h = h.replace(o, n)
    return h, c


def r90(h, c):
    # (87c) dice-rolling Facet cards go through the shared roll path so they get the Reroll button and can be rerolled
    a = """                    if (st.length) tpl += dice > 0 ? ` {{roll=[[{((${dice}+?{Modifier|0}+@{wound_penalty}+@{wp_dice}+@{cond_mod}+@{spec_bonus})${r85Rt(v)}` : ` {{roll=[[{1d10cf1}>10]]}}`;
                    startRoll(tpl, r => finishRoll(r.rollId));"""
    assert a in h, 'facet roll'
    h = h.replace(a, a.replace('startRoll(tpl, r => finishRoll(r.rollId));', 'if (st.length) rrRun0(tpl, false); else startRoll(tpl, r => finishRoll(r.rollId));'), 1)
    return h, c


def _r91opts():
    sk = sorted(SKILLS, key=lambda x: x)
    o = '<option value="" selected>-</option><option value="" disabled>--- Attributes ---</option>'
    o += ''.join(f'<option value="{x}">{x.title()}</option>' for x in ATTRS)
    o += '<option value="" disabled>--- Skills ---</option>'
    o += ''.join(f'<option value="{x}">{"Animal Ken" if x == "animalken" else x.title()}</option>' for x in sk)
    o += '<option value="" disabled>--- Other ---</option><option value="morality">Morality (Harmony etc.)</option><option value="potency">Power Stat (Primal Urge etc.)</option>'
    return o


def r91(h, c):
    import re as _re
    G = f'{P}{P}{P}{P}{P} .sheet-gifts'
    # (91) line breaks survive into chat cards
    a = 'const r15Fx = (v) => String(v === undefined || v === null ? "" : v).replace(/[{}\\[\\]|]/g, " ").replace(/\\s+/g, " ").trim();'
    assert a in h, 'r15Fx'
    h = h.replace(a, 'const r15Fx = (v) => String(v === undefined || v === null ? "" : v).replace(/\\r/g, "").replace(/[{}\\[\\]|]/g, " ").replace(/[ \\t]+/g, " ").trim().replace(/ *\\n */g, "%NEWLINE%");')
    a = 'const r15Lbl = (x) => x === "animalken" ? "Animal Ken" :'
    assert a in h, 'r15Lbl'
    h = h.replace(a, 'const r15Lbl = (x) => x === "potency" ? "Power Stat" : x === "morality" ? "Morality" : x === "animalken" ? "Animal Ken" :')
    c += '\n.sheet-rolltemplate-cofd-entry td, .sheet-rolltemplate-cofd-entry .sheet-ce-out { white-space: pre-line; }'
    # (92) Facet pool selects: every Attribute, Skill, Morality and the power stat, grouped
    h, n = _re.subn(r'(<select name="attr_f_[a-z]{3}_(?:attr|skill)"[^>]*>).*?(</select>)', lambda m: m.group(1) + _r91opts() + m.group(2), h)
    assert n == 20, n
    for k, nm, _ in REN:
        # (93) outcome boxes: Dramatic Failure, Failure, Success, Exceptional Success
        o = [f'<textarea class="sheet-gfx-o" name="attr_f_{k}_o{x}" placeholder="{t}"></textarea>' for x, t in (('exc', 'Exceptional success effect'), ('succ', 'Success effect'), ('fail', 'Failure effect'), ('dram', 'Dramatic failure effect'))]
        a = ''.join(o)
        assert h.count(a) == 2, ('out', k)
        h = h.replace(a, o[3].replace('Dramatic failure effect', 'Dramatic Failure effect') + o[2] + o[1] + o[0].replace('Exceptional success effect', 'Exceptional Success effect'))
        # (94) +Renown toggle under the pool selects
        lbs = _re.findall(r'<label class="sheet-gfn" title="Add ' + nm + r' to the pool">.*?</label>', h)
        assert len(lbs) == 2 and lbs[0] == lbs[1], ('ren', k, len(lbs))
        lb = lbs[0]; h = h.replace(lb, '')
        h, n = _re.subn(r'(<div class="sheet-gfx-r"><select name="attr_f_' + k + r'_attr".*?</select><select name="attr_f_' + k + r'_skill".*?</select></div>)', lambda m: m.group(1) + '<div class="sheet-gfx-r sheet-gfx-rn">' + lb + '</div>', h)
        assert n == 2, ('rn', k)
    c += f'\n{G} .sheet-gfx-body:has(input.sheet-gfx-nr:not(:checked)) > .sheet-gfx-rn {{ display: none !important; }}'
    c += f'\n{G} .sheet-gfx-r.sheet-gfx-rn {{ display: flex !important; margin: 0 !important; }}'
    # (95) armor tooltips
    TG = 'General armor: subtract its rating from the damage of every attack (Armor Piercing lowers it).'
    TB = 'Ballistic armor: against firearms and other ballistic attacks, downgrades that many points of lethal damage to bashing.'
    for o, t in (('title="General armor"', TG), ('title="Ballistic armor"', TB), ('<span class="sheet-stp" title="General">', None), ('<span class="sheet-stp" title="Ballistic">', None)):
        assert o in h, o
        h = h.replace(o, f'title="{t}"' if t else o.replace('"General"', f'"{TG}"').replace('"Ballistic"', f'"{TB}"'))
    h = h.replace('title="Armor from worn pieces (Stacking pieces add on top): General / Ballistic"', f'title="Armor from worn pieces (Stacking pieces add on top). {TG} {TB}"')
    # (96) Gift name toggles the card instead of posting
    a = '<button type="action" class="sheet-gift-nmb" name="act_gpost" title="Post Gift to chat"><span name="attr_name"></span></button>'
    assert h.count(a) == 2, 'gpost'
    h = h.replace(a, '<label class="sheet-gift-nmb" title="Expand / collapse"><input type="checkbox" class="sheet-gift-nmc" name="attr_show" value="1" /><span name="attr_name"></span></label>')
    c += '\n'.join(['',
        f'{G} .sheet-gift label.sheet-gift-nmb {{ display: block; width: 100%; box-sizing: border-box; margin: 0 !important; padding: 0 16px !important; color: inherit; font-family: inherit; font-size: 14px; font-weight: bold; line-height: 22px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; }}',
        f'{G} .sheet-gift label.sheet-gift-nmb:hover {{ color: var(--color-game-line, #c8732a); }}',
        f'{G} .sheet-gift label.sheet-gift-nmb > input.sheet-gift-nmc {{ display: none !important; }}'])
    # (98) Kuruth trigger boxes about twice as tall; header ranges in words
    h, n = _re.subn(r'<textarea class="sheet-trig-ta" rows="3"', '<textarea class="sheet-trig-ta" rows="6"', h)
    assert n == 3, n
    for o, t in (('Harmony 0-4 or 6-10', 'Harmony 4 or lower, 6 or higher'), ('Harmony 0-2 or 8-10', 'Harmony 2 or lower, 8 or higher')):
        assert f'<span class="sheet-kt-rng">{o}</span>' in h, o
        h = h.replace(f'<span class="sheet-kt-rng">{o}</span>', f'<span class="sheet-kt-rng">{t}</span>')
    c += f'\n{P}{P}{P}{P}{P} textarea.sheet-trig-ta {{ min-height: 96px !important; height: auto !important; }}'
    # (100) Merits: Cost field hidden (dots say it), Requires-roll toggle hides the pool fields, no-roll clicks post without dice
    i = h.index('<fieldset class="repeating_merits">'); j = h.index('</fieldset>', i); s = h[i:j]
    s = s.replace(' {{f_cost=@{cost}}}', '')
    a = '<div class="sheet-pw-box">'
    assert s.count(a) == 1
    s = s.replace(a, '<label class="sheet-wide sheet-m-nrl" title="Off: the Merit posts without dice and its pool fields are hidden"><input type="checkbox" class="sheet-gfx-sw sheet-m-nr" name="attr_needroll" value="1" /><span>Requires roll</span></label>' + a, 1)
    # (101) Effects by outcome toggle (off: single description; on: the four outcome boxes)
    a = '<div class="sheet-outcomes">'
    assert s.count(a) == 1, 'outcomes'
    s = s.replace(a, '<label class="sheet-wide sheet-m-nrl" title="On: separate Dramatic Failure / Failure / Success / Exceptional Success effects; the card shows the one rolled"><input type="checkbox" class="sheet-gfx-sw sheet-m-bo" name="attr_byout" value="1" /><span>Effects by outcome</span></label>' + a, 1)
    h = h[:i] + s + h[j:]
    M = f'{P}{P}{P}{P}{P} .repeating_merits ~ .repcontainer .repitem, {P}{P}{P}{P}{P} .repcontainer[data-groupname="repeating_merits"] .repitem'
    def ms(x):
        return ', '.join(f'{m} {x}' for m in M.split(', '))
    def mh(x):
        return ', '.join(f'{m}:has(input.sheet-m-nr:not(:checked)) {x}' for m in M.split(', '))
    c += '\n'.join(['',
        f'{ms("label:has(> input[name=\'attr_cost\'])")}, {ms("span.sheet-entry-cost")} {{ display: none !important; }}',
        f'{mh(".sheet-pw-3")}, {mh(".sheet-pw-hd")}, {mh(".sheet-pw-row:has(input[name=\'attr_pp_mod\']) > .sheet-stp:has(input[name=\'attr_pp_mod\'])")}, {mh("label:has(> input[name=\'attr_pool\'])")}, {mh("label:has(> input[name=\'attr_pool_dice\'])")}, {mh(".sheet-entry-pool")}, {mh("button.sheet-was-roll")} {{ display: none !important; }}',
        ', '.join(f'{m}:has(input.sheet-m-bo:not(:checked)) .sheet-outcomes' for m in M.split(', ')) + ' { display: none !important; }',
        f'{ms("label.sheet-m-nrl")} {{ display: flex !important; align-items: center; gap: 6px; margin: 4px 0 !important; }}'])
    c = c.replace("\\'", '"')
    # worker: needroll gate + migration (pool already set -> on)
    a = '                if (a) {\n                    const parts = [PW_AB[a]]; let t = val(a);'
    assert a in h, 'pwRow'
    h = h.replace(a, a.replace('if (a) {', 'if (a && !(sec === "merits" && v[p + "needroll"] === "0")) {'), 1)
    a = 'getAttrs([p + "pp_attr", p + "pp_skill", p + "pp_mod", p + "cost_wp", p + "cost_pw", p + r, "sheettype",'
    assert a in h
    h = h.replace(a, 'getAttrs([p + "pp_attr", p + "pp_skill", p + "pp_mod", p + "cost_wp", p + "cost_pw", p + r, p + "needroll", "sheettype",', 1)
    a = '                const a = v[p + "pp_attr"], s = v[p + "pp_skill"], m = parseInt(v[p + "pp_mod"]) || 0;\n'
    assert a in h
    h = h.replace(a, a + '                if (sec === "merits" && v[p + "needroll"] === "0") { u[p + "roll_part"] = ""; u[p + "pool"] = ""; }\n', 1)
    a = 'change:repeating_${sec}:cost_pw change:repeating_${sec}:${r}`'
    assert a in h
    h = h.replace(a, 'change:repeating_${sec}:cost_pw change:repeating_${sec}:needroll change:repeating_${sec}:${r}`', 1)
    a = 'getAttrs([p + "cost_wp", p + "cost_pw", p + "pool_dice", "sheettype", "vitae", "willpower", "willpower_cur"], (v) => {\n                    const nm = sec === "merits" ? "merit_name" : "name"; const n = parseInt(v[p + "pool_dice"]) || 0;'
    assert a in h, 'proll'
    h = h.replace(a, 'getAttrs([p + "cost_wp", p + "cost_pw", p + "pool_dice", p + "needroll", "sheettype", "vitae", "willpower", "willpower_cur"], (v) => {\n                    const nm = sec === "merits" ? "merit_name" : "name"; const n = (sec === "merits" && v[p + "needroll"] === "0") ? 0 : (parseInt(v[p + "pool_dice"]) || 0);', 1)
    a = '        on("sheet:opened", r15CostMig);'
    assert a in h
    h = h.replace(a, a + '''
        // (100) Merit "Requires roll": once per row, on if a pool is already set, otherwise off; never touches the pool data
        const r101Mig = () => getSectionIDs("repeating_merits", ids => getAttrs(ids.flatMap(i => ["o_dramatic", "o_failure", "o_success", "o_exceptional", "bomig"].map(x => `repeating_merits_${i}_${x}`)), v => {
            const u = {}; ids.forEach(i => { const p = `repeating_merits_${i}_`; if (v[p + "bomig"] === "1") return;
                u[p + "byout"] = ["o_dramatic", "o_failure", "o_success", "o_exceptional"].some(x => String(v[p + x] || "").trim()) ? "1" : "0"; u[p + "bomig"] = "1"; });
            if (Object.keys(u).length) setAttrs(u, {silent: true});
        }));
        on("sheet:opened", r101Mig);
        const r100Mig = () => getSectionIDs("repeating_merits", ids => getAttrs(ids.flatMap(i => ["pp_attr", "pool_dice", "nrmig"].map(x => `repeating_merits_${i}_${x}`)), v => {
            const u = {}; ids.forEach(i => { const p = `repeating_merits_${i}_`; if (v[p + "nrmig"] === "1") return;
                u[p + "needroll"] = (v[p + "pp_attr"] || (parseInt(v[p + "pool_dice"]) || 0) > 0) ? "1" : "0"; u[p + "nrmig"] = "1"; });
            if (Object.keys(u).length) setAttrs(u, {silent: true}, () => PW_SECS.includes("merits") && ids.forEach(i => pwRow("merits", i)));
        }));
        on("sheet:opened", r100Mig);''', 1)
    return h, c


def r92(h, c):
    """(102) 3-slot dice pool for power rows (Merits etc.) and a 3rd optional slot for Gift Facets; steppers on one row"""
    import re as _re
    sel = lambda nm, t: f'<select name="attr_{nm}" title="{t}">' + _r91opts().replace('<option value="morality">', '<option value="_dots">This entry\'s dots</option><option value="morality">') + '</select>'
    rx = r'<div class="sheet-pw-row"><b>Dice pool</b><label>Attribute <select name="attr_pp_attr">.*?</select></label><label>Skill / trait <select name="attr_pp_skill">.*?</select></label></div>'
    new = ('<div class="sheet-pw-hd">Dice Pool</div><div class="sheet-pw-3">' + sel('pp_attr', 'Dice pool 1') + sel('pp_skill', 'Dice pool 2') + sel('pp_3', 'Dice pool 3') + '</div>')
    h, n = _re.subn(rx, lambda m: new, h)
    assert n == 26, ('pw3', n)
    for a, b in (('<span class="sheet-stp-l">Modifier</span><button type="action" class="sheet-stp-b" name="act_pp-mod-dec"', '<span class="sheet-stp-l">Mod</span><button type="action" class="sheet-stp-b" name="act_pp-mod-dec"'),
                 ('<span class="sheet-stp-l">Willpower</span><button type="action" class="sheet-stp-b" name="act_cost-wp-dec"', '<span class="sheet-stp-l">WP</span><button type="action" class="sheet-stp-b" name="act_cost-wp-dec"')):
        assert h.count(a) == 26, a
        h = h.replace(a, b)
    # worker: pool = sum of the three slots (blank = none); old pp_attr/pp_skill stay as slots 1 and 2
    a = 'getAttrs([p + "pp_attr", p + "pp_skill", p + "pp_mod",'
    assert h.count(a) >= 1, 'ga'
    h = h.replace(a, 'getAttrs([p + "pp_attr", p + "pp_skill", p + "pp_3", p + "pp_mod",', 1)
    a = 'const a = v[p + "pp_attr"], s = v[p + "pp_skill"], m = parseInt(v[p + "pp_mod"]) || 0;'
    assert a in h
    h = h.replace(a, 'const a = v[p + "pp_attr"], s = v[p + "pp_skill"], s3 = v[p + "pp_3"], m = parseInt(v[p + "pp_mod"]) || 0;', 1)
    a = 'if (a && !(sec === "merits" && v[p + "needroll"] === "0")) {\n                    const parts = [PW_AB[a]]; let t = val(a);\n                    if (s) { parts.push(PW_AB[s]); t += val(s); }'
    assert a in h, 'pwsum'
    h = h.replace(a, 'if ((a || s || s3) && !(sec === "merits" && v[p + "needroll"] === "0")) {\n                    const parts = []; let t = 0;\n                    [a, s, s3].forEach(k => { if (k && PW_AB[k]) { parts.push(PW_AB[k]); t += val(k); } });', 1)
    a = 'on(`change:repeating_${sec}:pp_attr change:repeating_${sec}:pp_skill '
    assert a in h
    h = h.replace(a, 'on(`change:repeating_${sec}:pp_attr change:repeating_${sec}:pp_skill change:repeating_${sec}:pp_3 ', 1)
    # Facets: optional 3rd slot
    h, n = _re.subn(r'(<select name="attr_f_([a-z]{3})_skill"[^>]*>.*?</select>)', lambda m: m.group(1) + f'<select name="attr_f_{m.group(2)}_x3" title="Optional third trait">' + _r91opts() + '</select>', h)
    assert n == 10, ('fx3', n)
    a = 'const fl = ["name", "on", "attr", "skill", '
    assert a in h
    h = h.replace(a, 'const fl = ["name", "on", "attr", "skill", "x3", ', 1)
    a = '[v[f + "attr"], v[f + "skill"]].filter(Boolean)'
    assert a in h, 'fst'
    h = h.replace(a, '[v[f + "attr"], v[f + "skill"], v[f + "x3"]].filter(Boolean)', 1)
    c += ('\n.charsheet .sheet-pw-hd{text-align:center;font-weight:bold;margin:2px 0}'
          '\n.charsheet .sheet-pw-3{display:grid !important;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px}'
          '\n.charsheet .sheet-pw-3 select{width:100% !important;min-width:0 !important;margin:0 !important}'
          '\n.charsheet .sheet-pw-row2{display:flex !important;flex-wrap:nowrap !important;gap:4px;justify-content:space-between}'
          '\n.charsheet .sheet-pw-row2 .sheet-stp{white-space:nowrap;margin:0 !important}'
          f'\n{P}{P}{P}{P}{P} .sheet-gifts .sheet-gfx-r:has(> select[name$="_x3"]){{grid-template-columns:repeat(auto-fit,minmax(64px,1fr)) !important}}'
          f'\n{P}{P}{P}{P}{P} .sheet-gifts .sheet-gfx-r > select[name$="_x3"]{{width:100% !important;min-width:0 !important;box-sizing:border-box}}\n')
    return h, c


def r93(h, c):
    """(103) Config: Instinctive Defense (WtF 2e p.109 Merit: in Urshul and Urhan, Defense uses the higher, not lower, of Wits and Dexterity)"""
    a = '<span>Attribute dots 6+</span></label>'
    assert h.count(a) == 1, 'cfg'
    h = h.replace(a, a + '<label class="sheet-cfg-sw" title="Instinctive Defense (Werewolf: the Forsaken 2e p.109): in Urshul and Urhan, Defense uses the higher of Wits and Dexterity, not the lower"><input type="checkbox" name="attr_inst_def" value="1" /><span class="sheet-cfg-knob"></span><span>Instinctive Defense</span></label>', 1)
    # the forms the rule applies to; change here if the table rules differ
    ID = 'const INST_DEF_FORMS = ["urshul", "urhan"]; const instDef = (v, f) => v.inst_def === "1" && INST_DEF_FORMS.includes(String(f || "").toLowerCase());\n'
    a = '        var updateDefense = function() {\n            getAttrs(["defense_select",'
    assert h.count(a) == 1, 'upd'
    h = h.replace(a, '        ' + ID + '        var updateDefense = function() {\n            getAttrs(["inst_def", "form", "defense_select",', 1)
    a = 'v.wits = (parseInt(v.wits, 10) || 0) + (parseInt(v.wits_boost, 10) || 0);\n'
    assert h.count(a) == 1, 'wits'
    h = h.replace(a, a + '                if (instDef(v, v.form)) { v.dexterity = v.wits = Math.max(v.dexterity, v.wits); }\n'
                  '                if (!updateDefense._on) { updateDefense._on = 1; on("change:inst_def change:form", () => { updateDefense(); if (typeof updateForms === "function") updateForms(); }); }\n', 1)
    a = 'u[`fv_${f}_defense`] = Math.min(n("wits"), dex) + n("athletics");'
    assert h.count(a) == 1, 'fv'
    h = h.replace(a, 'u[`fv_${f}_defense`] = (instDef(v, f) ? Math.max : Math.min)(n("wits"), dex) + n("athletics");', 1)
    a = 'getAttrs(["strength","dexterity","stamina","manipulation","wits","composure","athletics","base_size","form","urkhar_enabled","sheettype"]'
    assert h.count(a) == 1, 'fga'
    h = h.replace(a, a[:-1] + ',"inst_def"]', 1)
    a = 'u.defense_calc = `Defense = min(Wits'
    n = h.count(a); assert n >= 1, 'calc'
    h = h.replace(a, 'u.defense_calc = `Defense = ${instDef(v, v.form) ? "max" : "min"}(Wits')
    # (97b) Renown panel: drop the partial (top/bottom/left only) border
    c += f'\n{P}{P}{P}{P}{P} .sheet-game-line.sheet-skills-renown{{border:0 none !important;box-shadow:none !important}}\n'
    a = '"defense_base","defense_penalty",'
    assert h.count(a) == 1, 'cga'
    h = h.replace(a, '"defense_base","defense_penalty","inst_def",', 1)
    return h, c


def r94(h, c):
    """polish: Merit Requires roll / Effects by outcome as the Facet slide switches (splat colour)"""
    import re as _re
    h, n = _re.subn(r'(<input type="checkbox" class="sheet-gfx-sw sheet-m-(?:nr|bo)"[^>]*/>)', r'<span class="sheet-gfx-swr">\1<span class="sheet-gfx-trk"></span></span>', h)
    assert n == 2, ('msw', n)
    G = f'{P}{P}{P}{P}{P} .sheet-mswz'
    rules = [
        f'{G} .sheet-gfx-swr {{ position: relative; display: inline-block !important; flex: 0 0 24px !important; width: 24px !important; height: 12px !important; min-width: 24px !important; padding: 0 !important; margin: 0 !important; overflow: visible !important; vertical-align: middle; }}',
        f'{G} .sheet-gfx-swr input.sheet-gfx-sw {{ -webkit-appearance: none !important; -moz-appearance: none !important; appearance: none !important; position: absolute !important; inset: 0; width: 24px !important; height: 12px !important; margin: 0 !important; padding: 0 !important; opacity: 0 !important; z-index: 2; cursor: pointer; border: 0 !important; background: none !important; box-shadow: none !important; }}',
        f'{G} .sheet-gfx-swr input.sheet-gfx-sw::before, {G} .sheet-gfx-swr input.sheet-gfx-sw::after {{ content: none !important; display: none !important; }}',
        f'{G} .sheet-gfx-trk {{ position: absolute; display: block !important; left: 0 !important; top: 0 !important; width: 24px !important; height: 12px !important; border-radius: 6px !important; background: #555 !important; pointer-events: none; }}',
        f'{G} .sheet-gfx-trk::after {{ content: ""; position: absolute; left: 1px; top: 1px; width: 10px; height: 10px; border-radius: 50%; background: #ddd; transition: left .15s; }}',
        f'{G} .sheet-gfx-swr input.sheet-gfx-sw:checked + .sheet-gfx-trk {{ background: var(--color-game-line, #b4743a) !important; }}',
        f'{G} .sheet-gfx-swr input.sheet-gfx-sw:checked + .sheet-gfx-trk::after {{ left: 13px; background: #fff; }}',
        f'{G} label.sheet-m-nrl {{ display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; justify-content: flex-start !important; align-items: center !important; gap: 6px; cursor: pointer; text-align: left !important; }}', f'{G} label.sheet-m-nrl > span:not(.sheet-gfx-swr) {{ display: inline !important; margin: 0 !important; width: auto !important; }}',
    ]
    M = (f'{P}{P}{P}{P}{P} .repeating_merits ~ .repcontainer .repitem', f'{P}{P}{P}{P}{P} .repcontainer[data-groupname="repeating_merits"] .repitem')
    out = []
    for r in rules:
        sel, body = r.split('{', 1)
        ps = [p.strip() for p in sel.split(', ')]
        out.append(', '.join(p.replace(G, m) for p in ps for m in M) + ' {' + body)
    c += '\n' + '\n'.join(out) + '\n'
    return h, c


def r95(h, c):
    """(104) Weapons / Armor rows: speech-bubble post button sits right beside the expand caret, caret-sized, name after it"""
    import re as _re
    def mv(m):
        head, body = m.group(1), m.group(2)
        b = _re.search(r'<button type="roll" class="sheet-entry-post sheet-post-ic"[^>]*>&#128172;</button>', body)
        return head + b.group(0) + body.replace(b.group(0), '', 1)
    h, n = _re.subn(r'(<div class="sheet-entry-head">\n?)((?:(?!</div>).)*?<button type="roll" class="sheet-entry-post sheet-post-ic")', lambda m: m.group(0), h, flags=_re.S)
    n = 0
    out = []; i = 0
    for m in _re.finditer(r'<div class="sheet-entry-head">\n?', h):
        j = h.find('sheet-entry-post sheet-post-ic', m.end()); k = h.find('</div>', m.end())
        if j < 0 or j > k: continue
        bs = h.rfind('<button', m.end(), j); be = h.find('</button>', j) + 9
        out.append(h[i:m.end()] + h[bs:be] + h[m.end():bs]); i = be; n += 1
    h = ''.join(out) + h[i:]
    assert n == 2, ('post', n)
    E = f'{P}{P}{P}{P}{P} .sheet-entry-head'
    c += (f'\n{E}:has(> button.sheet-post-ic:first-child) {{ padding-left: 0 !important; }}'
          f'\n{E} > button.sheet-entry-post.sheet-post-ic:first-child {{ order: -1 !important; flex: 0 0 13px !important; width: 13px !important; height: 13px !important; min-height: 13px !important; max-height: 13px !important; min-width: 13px !important; padding: 0 !important; margin: 0 2px 0 0 !important; '
          f'border: 1px solid rgba(217,138,74,0.7) !important; border-radius: 3px !important; background: #1a1a1a !important; font-size: 7px !important; line-height: 11px !important; text-align: center !important; box-sizing: border-box !important; align-self: center !important; position: relative !important; top: 2px !important; float: none !important; overflow: hidden; }}\n')
    return h, c


def r96(h, c):
    """(106) Shadow / Wolf Gifts titles centred over the whole grid; expand/collapse buttons absolutely on the right"""
    H = f'{P}{P}{P}{P}{P} .sheet-gifts > .sheet-entry-section-head'
    c += (f'\n{H} {{ position: relative !important; justify-content: center !important; padding-left: 0 !important; padding-right: 0 !important; }}'
          f'\n{H} > .sheet-subheader {{ flex: 1 1 100% !important; width: 100% !important; text-align: center !important; margin: 0 !important; }}'
          f'\n{H} > button.sheet-mini {{ position: absolute !important; top: 50% !important; transform: translateY(-50%); margin: 0 !important; }}'
          f'\n{H} > button.sheet-mini:nth-of-type(1) {{ right: 57px !important; }}'
          f'\n{H} > button.sheet-mini:nth-of-type(2) {{ right: 40px !important; }}\n')
    return h, c
