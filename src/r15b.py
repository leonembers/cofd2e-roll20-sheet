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
        f'{P} .sheet-entry > input.sheet-mcat-flag[value="Supernatural"] ~ .sheet-entry-head .sheet-mcat-badge {{ font-size: 0 !important; letter-spacing: 0 !important; color: {G} !important; }}',
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


REN = [('cun', 'Cunning', '#9a6ad6'), ('glo', 'Glory', '#d9a521'), ('hon', 'Honor', '#3f86d6'), ('pur', 'Purity', '#e4e4e4'), ('wis', 'Wisdom', '#3fb39a')]
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
