"""r13b: Kuruth tiers Specific > Common > Passive; centred Touchstones / Kuruth headers, labels and inputs (Werewolf
Kuruth tab and Vampire Frenzy tab); skill specialty/used box removed (the roller handles Specialties) and rows
spaced; Equipment fields sized by purpose."""
import re

P = '.charsheet.charsheet.charsheet.charsheet.charsheet.charsheet'
SK = ['academics', 'computer', 'crafts', 'enigmas', 'investigation', 'medicine', 'occult', 'politics', 'science',
      'archery', 'athletics', 'brawl', 'drive', 'firearms', 'larceny', 'ride', 'stealth', 'survival', 'weaponry',
      'animalken', 'empathy', 'expression', 'intimidation', 'persuasion', 'socialize', 'streetwise', 'subterfuge']


def apply(h, c):
    # (c) drop the per-skill specialty/used box and its worker wiring (nothing else reads <skill>_box)
    n0 = len(re.findall(r'<span class="sheet-checkbox sheet-eq-1">', h))
    h, n = re.subn(r'<span class="sheet-checkbox sheet-eq-1">\s*<input type="hidden" class="sheet-flag" name="attr_(\w+)_box" value="0">\s*'
                   r'<button type="action" name="act_\1_box"[^>]*></button>\s*</span>\s*', '', h)
    assert n == n0 == 27, (n, n0)
    for s in SK:
        h = h.replace(f'"{s}_box",', '').replace(f',"{s}_box"', '').replace(f'"{s}_box"', '')
    rb = 'on("clicked:ride_box", () => getAttrs(["ride_box"], v => setAttrs({ride_box: v.ride_box === "1" ? "0" : "1"})));'
    h = h.replace(rb, '')
    for s in SK:
        assert f'act_{s}_box' not in h and f'"{s}_box"' not in h, s
    K = f'{P} .sheet-mp-kuruth'
    T = f'{P} .sheet-kuruth-tiers.sheet-kt-rows'
    VT = f'{P} .repcontainer[data-groupname="repeating_vtouchstones"]'
    L = [
        # (a) visual order Specific, Common, Passive; the hidden Harmony input stays first in the DOM for the ~ selectors
        f'{T} > label.sheet-kt-specific {{ order: 1 !important; }}',
        f'{T} > label.sheet-kt-common {{ order: 2 !important; }}',
        f'{T} > label.sheet-kt-passive {{ order: 3 !important; }}',
        f'{T} {{ display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr)) !important; flex-direction: row !important; gap: 4px !important; }}',
        f'{T} > input.sheet-kt-hm {{ display: none !important; }}',
        f'{T} > label.sheet-kuruth-tier {{ min-width: 0 !important; padding: 3px 4px !important; gap: 2px; }}',
        f'{T} textarea.sheet-trig-ta {{ height: 48px !important; min-height: 32px !important; margin: 0 !important; font-size: 12px !important; }}',
        # (b) centring
        f'{K} .sheet-subheader, {K} .sheet-subheader > span {{ text-align: center !important; justify-content: center !important; width: 100%; }}',
        f'{K} .sheet-wolf-ts > label {{ display: flex !important; flex-direction: column !important; align-items: center !important; text-align: center !important; }}',
        f'{K} .sheet-wolf-ts > label > span {{ text-align: center !important; width: 100%; }}',
        f'{K} .sheet-wolf-ts > label > input {{ text-align: center !important; width: 100% !important; box-sizing: border-box; }}',
        f'{T} .sheet-kt-lbl {{ flex-direction: column !important; align-items: center !important; justify-content: center !important; text-align: center !important; gap: 1px; }}',
        f'{T} .sheet-kt-rng {{ text-align: center !important; }}',
        f'{P} .sheet-vtouchstones .sheet-entry-section-head {{ justify-content: center !important; text-align: center !important; }}',
        f'{P} .sheet-vtouchstones .sheet-entry-section-head > .sheet-subheader {{ text-align: center !important; justify-content: center !important; }}',
        f'{VT} .sheet-entry-head .sheet-entry-post {{ justify-content: center !important; text-align: center !important; }}',
        f'{VT} .sheet-entry-body label {{ text-align: center !important; align-items: center !important; }}',
        f'{VT} .sheet-entry-body input[type=text] {{ text-align: center !important; }}',
        # (c) skill rows: clear space between the remaining mark box and the name, even row rhythm
        f'{P} div:has(> button.sheet-toggle + button.sheet-spec-caret) > .sheet-skm {{ margin-right: 5px !important; }}',
        f'{P} div:has(> button.sheet-toggle + button.sheet-spec-caret) {{ margin: 0 0 2px !important; }}',
    ]
    # Equipment / weapons / armor fields sized by purpose instead of a flat 10em
    G = lambda s: f'{P} .repcontainer[data-groupname="repeating_{s}"] .sheet-entry-body'
    for sec in ('equipment', 'weapons', 'armor'):
        L += [f'{G(sec)} > label:not(.sheet-wide) > input[type=text], {G(sec)} > label:not(.sheet-wide) > select {{ width: auto !important; max-width: 100% !important; }}',
              f'{G(sec)} > label:not(.sheet-wide) > select {{ field-sizing: content; min-width: 4em; }}']
    L += [f'{G("equipment")} input[name="attr_cost"] {{ width: 6em !important; }}',
          f'{G("weapons")} > label.sheet-hl-name, {G("weapons")} > label.sheet-hl-preset {{ flex: 1 1 100% !important; }}',
          f'{G("weapons")} > label.sheet-hl-name > input, {G("weapons")} > label.sheet-hl-preset > select {{ flex: 1 1 auto !important; width: auto !important; }}',
          f'{G("weapons")} input[name="attr_enhance"] {{ width: 9em !important; }}',
          f'{G("weapons")} label:has(> input[name="attr_tags_extra"]), {G("armor")} label:has(> input[name="attr_ar_tags"]) {{ flex: 1 1 100% !important; }}',
          f'{G("weapons")} input[name="attr_tags_extra"], {G("armor")} input[name="attr_ar_tags"] {{ flex: 1 1 auto !important; width: auto !important; }}',
          f'{G("armor")} input[name="attr_ar_coverage"] {{ width: 9em !important; }}']
    return armor(*devnotes(*firstname(*cards(*tabrow(*slides(*weapons(h, c + '\n' + '\n'.join(L) + '\n')))))))


# (f) weapon cards: inline labels and per-type stat visibility (CofD 2E core weapon tables + Hurt Locker)
WVIS = {
    # field attr: types that show it
    'initiative': ('melee', 'thrown', 'ranged', 'bow', 'explosive'),
    'str_req': ('melee', 'thrown', 'ranged', 'bow'),
    'wsize': ('melee', 'thrown', 'ranged', 'bow', 'explosive'),
    'avail': ('melee', 'thrown', 'ranged', 'bow', 'explosive'),
    'max_range': ('thrown', 'ranged', 'bow', 'explosive'),
    'capacity': ('ranged', 'bow'),
    'piercing': ('melee', 'ranged', 'bow'),
    'expl_delivery': ('explosive',), 'blast': ('explosive',), 'force': ('explosive',),
    'onehanded': ('melee', 'ranged'),
}
WTYPES = ('melee', 'unarmed', 'thrown', 'ranged', 'bow', 'explosive')


def weapons(h, c):
    B = f'{P} .repcontainer[data-groupname="repeating_weapons"] .sheet-entry-body'
    BO = f'{P} .repcontainer[data-groupname="repeating_weapons"] .sheet-entry > input.sheet-entry-toggle:checked ~ .sheet-entry-body'
    L = [f'{BO} {{ display: flex !important; flex-wrap: wrap !important; gap: 3px 10px !important; align-items: center !important; justify-content: flex-start !important; grid-template-columns: none !important; }}',
         f'{B} > label {{ display: inline-flex !important; flex-direction: row !important; align-items: center !important; gap: 4px !important; width: auto !important; margin: 0 !important; text-align: left !important; flex: 0 0 auto; }}',
         f'{B} > label > span.sheet-lbl, {B} > label > span:first-child {{ width: auto !important; margin: 0 !important; white-space: nowrap; text-align: left !important; }}',
         f'{B} > label > select, {B} > label > input[type=number] {{ width: auto !important; margin: 0 !important; }}',
         f'{B} > label > input[type=number] {{ width: 3.6em !important; }}',
         f'{B} > label.sheet-hl-preset, {B} > label.sheet-hl-name, {B} > label:has(> input[name="attr_tags_extra"]), {B} > label:has(> textarea) {{ flex: 1 1 100% !important; }}',
         f'{B} > label:has(> textarea) {{ flex-direction: column !important; align-items: stretch !important; }}',
         f'{B} > .sheet-hl-tags {{ flex: 1 1 100%; margin: 0 !important; }}']
    for sec in ('weapons', 'armor', 'equipment'):
        L.append(f'{P} .repcontainer[data-groupname="repeating_{sec}"] .sheet-entry > input.sheet-entry-toggle:not(:checked) ~ .sheet-entry-body {{ display: none !important; }}')
    for fld, shown in WVIS.items():
        if fld != 'onehanded':
            show = ', '.join(f'{B} > input.sheet-hl-wt[value="{t}"] ~ label:has(> [name="attr_{fld}"])' for t in shown)
            L.append(f'{show} {{ display: inline-flex !important; }}')
    for fld, shown in WVIS.items():
        hide = [t for t in WTYPES if t not in shown]
        L.append(', '.join(f'{B} > input.sheet-hl-wt[value="{t}"] ~ label:has(> [name="attr_{fld}"])' for t in hide) + ' { display: none !important; }')
    L.append(f'{B} > input.sheet-hl-2hv:not([value="1"]) ~ label.sheet-hl-2h.sheet-hl-2h {{ display: none !important; }}')
    L.append(f'{B} > label:has(> input[type=checkbox]) {{ flex: 0 0 auto; }}')
    return h, c + '\n'.join(L) + '\n'


# (g) chat cards: splat fonts + colours on title / labels, keyed off the {{gl_<splat>}} band the macro already sends
CARD = {  # band key: (font stack, text colour readable on light and dark cards)
    'werewolf': ('"WolfsRain", "Fondamento", cursive', '#d9772b'),
    'vampire': ('"Chomsky", "IM Fell English SC", serif', '#b02a2a'),
    'hunter': ('"1980sWriter", "Special Elite", monospace', '#2f8a8a'),
    'mortal': ('"IM Fell English SC", "Sorts Mill Goudy", serif', '#5a60c8'),
    'mage': ('"Cinzel Decorative", serif', '#b89a3c'),
    'promethean': ('"Metamorphous", serif', '#5a5ac0'),
    'changeling': ('"Almendra", serif', '#14915c'),
    'geist': ('"Pirata One", serif', '#5e94ae'),
    'mummy': ('"Cinzel", serif', '#b09a58'),
    'demon': ('"Black Ops One", sans-serif', '#6a6a96'),
    'beast': ('"Creepster", cursive', '#8a5a8a'),
    'deviant-the-renegades': ('"Metal Mania", serif', '#b03a3a'),
}


def cards(h, c):
    o = '<div class="sheet-ce-big">{{roll}}</div><div class="sheet-ce-sl">successes</div>'
    assert h.count(o) == 1
    h = h.replace(o, '<div class="sheet-ce-rn"><span class="sheet-ce-big">{{roll}}</span><span class="sheet-ce-sl">successes</span></div>')
    T = '.sheet-rolltemplate-cofd-entry'
    L = [f'{T} .sheet-ce-rn {{ display: flex; align-items: baseline; justify-content: center; gap: 6px; }}',
         f'{T} .sheet-ce-rn .sheet-ce-big {{ display: inline-block; }}',
         f'{T} .sheet-ce-rn .sheet-ce-sl {{ display: inline-block; }}',
         f'{T} .sheet-ce-big, {T} .sheet-ce-big .inlinerollresult, {T} td, {T} .sheet-ce-out {{ font-family: Arial, Helvetica, sans-serif; }}']
    for k, (f, col) in CARD.items():
        B = f'{T} .sheet-ce-band-{k}'
        L += [f'{B} ~ .sheet-ce-head .sheet-ce-name, {B} ~ .sheet-ce-head .sheet-ce-kind {{ font-family: {f} !important; color: {col} !important; }}',
              f'{B} ~ .sheet-ce-head .sheet-ce-name {{ font-size: 17px; letter-spacing: .5px; }}',
              f'{B} ~ table th, {B} ~ * th, {B} ~ .sheet-ce-roll .sheet-ce-sl {{ font-family: {f} !important; color: {col} !important; letter-spacing: .5px; }}']
    # template CSS goes first in sheet.css (before everything else)
    return h, '\n'.join(L) + '\n' + c


# (d) stock checkboxes -> slide toggles in the splat colour (drawn on the input itself: appearance none + ::after knob)
SW_NAMES = ['c_active', 'cost_auto', 'onehanded']  # the stock checkboxes found by the audit (ar_helmet is now a Stacking switch)
SW_EXTRA = []  # extra class-bearing checkboxes found by the audit get added here


def slides(h, c):
    G = 'var(--color-game-line, #b4743a)'
    S = ', '.join([f'{P} input[type=checkbox][name=attr_{k}]:not(#sw)' for k in SW_NAMES])
    on = ', '.join(f'{x.strip()}:checked' for x in S.split(','))
    kn = ', '.join(f'{x.strip()}::after' for x in S.split(','))
    kno = ', '.join(f'{x.strip()}:checked::after' for x in S.split(','))
    L = [f'{S} {{ -webkit-appearance: none !important; -moz-appearance: none !important; appearance: none !important; position: relative !important; display: inline-block !important; '
         f'width: 26px !important; height: 14px !important; min-width: 26px !important; max-width: 26px !important; min-height: 14px !important; max-height: 14px !important; margin: 0 2px !important; padding: 0 !important; border-radius: 999px !important; '
         f'border: 1px solid #888 !important; background: #555 !important; box-sizing: border-box !important; cursor: pointer; vertical-align: middle; flex: 0 0 26px; opacity: 1 !important; box-shadow: none !important; }}',
         f'{kn} {{ content: "" !important; position: absolute; top: 1px; left: 1px; width: 10px; height: 10px; border-radius: 50%; background: #ddd; transition: left .15s; display: block !important; }}',
         f'{on} {{ background: {G} !important; border-color: {G} !important; }}',
         f'{kno} {{ left: 13px; background: #fff; }}']
    return h, c + '\n'.join(L) + '\n'


# (e) Conditions / Tilts buttons: own centred row right under the centred page tabs, same font as the tabs
TABFONT = {'mortal2': '"Sorts Mill Goudy", serif', 'vampire2': '"IM Fell English SC", serif', 'werewolf2': 'Fondamento, cursive',
           'mage2': '"Cinzel Decorative", serif', 'promethean2': 'Metamorphous, serif', 'changeling2': 'Almendra, serif',
           'hunter2': '"Special Elite", monospace', 'geist2': '"Pirata One", serif', 'mummy2': 'Cinzel, serif', 'demon': '"Black Ops One", sans-serif',
           'beast': 'Creepster, cursive', 'deviant-the-renegades': '"Metal Mania", serif', 'breeds2': 'Fondamento, cursive',
           'homebrew': '"Sorts Mill Goudy", "Goudy Old Style", Garamond, Georgia, serif'}


def tabrow(h, c):
    import re
    m = re.search(r'<label class="sheet-ovbtn sheet-ovb-cond".*?</label><label class="sheet-ovbtn sheet-ovb-tilt".*?</label>', h, re.S)
    assert m and h.count('sheet-ovb-cond"') == 1
    h = h[:m.start()] + '<div class="sheet-tabfill"></div><div class="sheet-ovrow">' + m.group(0) + '</div>' + h[m.end():]
    k = h.index('<button type="action" class="sheet-toggle sheet-page-settings"')
    h = h[:k] + '<div class="sheet-tabfill"></div>' + h[k:]
    B = '.charsheet.charsheet.charsheet.charsheet .sheet-background'
    L = [f'{B} > .sheet-tabfill {{ display: none !important; }}',
         f'{B} > button.sheet-page-settings {{ margin-left: auto !important; }}',
         f'{B} > .sheet-tabfill:has(+ .sheet-ovrow) {{ display: block !important; order: 2; flex: 0 0 0; width: 0; min-width: 0; height: 1px; margin-left: auto !important; }}',
         f'{B} > .sheet-ovrow {{ order: 2; flex: 0 0 100%; display: flex; justify-content: center; align-items: center; gap: 8px; margin: 2px 0 0; }}',
         f'{B} > .sheet-ovrow > label.sheet-ovbtn {{ margin: 0 !important; font-size: 14px !important; font-weight: 700 !important; }}']
    for t, f in TABFONT.items():
        L.append(f'.charsheet:has(input.sheet-type[value="{t}"]) .sheet-ovrow > label.sheet-ovbtn.sheet-ovbtn {{ font-family: {f} !important; }}')
    return h, c + '\n'.join(L) + '\n'


def firstname(h, c):
    """(g) card prose uses the first name only: worker-maintained attr firstname = first word of character_name."""
    import re
    n = [0]
    def sub(m):
        if m.group(1) in ('charname', 'name') :
            return m.group(0)
        n[0] += 1
        return '{{' + m.group(1) + '=' + m.group(2).replace('@{character_name}', '@{firstname}') + '}}'
    h = re.sub(r'\{\{(\w+)=([^{}]*(?:@\{(?!character_name)[\w|]+\}[^{}]*)*@\{character_name\}[^{}]*(?:@\{[\w|]+\}[^{}]*)*)\}\}', sub, h)
    assert n[0] >= 6, n[0]
    k = h.index('<input type="hidden" class="sheet-type"')
    h = h[:k] + '<input type="hidden" name="attr_firstname" value="" />' + h[k:]
    js = r'''
        const setFirstName = () => getAttrs(["character_name", "firstname"], v => { const f = String(v.character_name || "").trim().split(/\s+/)[0] || "";
            if (f !== (v.firstname || "")) setAttrs({firstname: f}, {silent: true}); });
        on("sheet:opened change:character_name", setFirstName);
'''
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    return h, c


def devnotes(h, c):
    """(j) strip developer / 'unverified' notes from player-facing sheet text, titles and chat card fields."""
    import re
    subs = [
        (r'\s*<i class="?(?:sheet-)?wolf-unv"?>[^<]*</i>', ''),
        (r'\s*<sup class="sheet-ref-q"[^>]*>\?</sup>', ''),
        (r'\s*<i>\(Not checked against the [^<]*?\)</i>', ''),
        (r' \(unverified\)', ''),
        (r' Cells marked \? are from rules knowledge, not the book\.', ''),
        (r' Kuruth links to Harmony: TBD\.', ''),
        (r' Exact (?:dice )?effect TBD\.', ''),
        (r' Exact rate: see Gauru; TBD until verified\.', ''),
        (r' \(exact effect TBD\)', ''),
        (r' \(rules reading not checked against the V:tR 2E book; verify\)', ''),
        (r' \(verify vs V:tR 2E\)', ''),
        (r' \(the instinctive Skill list is a best reading, not checked against the W:tF 2E book; verify\)', ''),
        (r' \(pool not re-checked against the W:tF 2E book; apply trigger modifiers in the prompt\)', ' (apply trigger modifiers in the prompt)'),
    ]
    for pat, rep in subs:
        h = re.sub(pat, rep, h)
    body = re.sub(r'<script type="text/worker">.*?</script>', '', h, flags=re.S)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    left = re.findall(r'.{60}(?:verify|not checked|unverified|best reading|TBD|re-checked).{30}', body, re.I)
    assert not left, left[:5]
    return h, c


def armor(h, c):
    """(k) collapsed armor row = name + General/Ballistic summary + Worn + Stacking; everything else in the collapsible body."""
    import re
    i = h.index('<fieldset class="repeating_armor"'); j = h.index('</fieldset>', i); f = h[i:j]
    m = re.search(r'<div class="sheet-ar-steps">.*?</textarea>', f, re.S); assert m
    mid = m.group(0); f = f.replace(mid, '', 1)
    hl = '<label><span class="sheet-lbl">Helmet</span><input type="checkbox" name="attr_ar_helmet" value="1" /></label>'
    tg = '<label><span class="sheet-lbl">Tags (comma-separated)</span><input type="text" name="attr_ar_tags" /></label>'
    tl = '<div class="sheet-ar-tagline"><span class="sheet-ar-tagpills" name="attr_ar_tagsum"></span></div>'
    for x in (hl, tg, tl):
        assert f.count(x) == 1, x; f = f.replace(x, '', 1)
    f = f.replace(' {{f_ar_tags=@{ar_tags}}}', '', 1)
    k = f.index('</label>', f.index('class="sheet-ar-eq sheet-switch"')) + 8
    f = f[:k] + ('<label class="sheet-ar-eq sheet-ar-stk sheet-switch" title="Stacking: this piece (e.g. a helmet) adds on top of other worn armor instead of replacing it">'
                 '<input type="checkbox" name="attr_ar_helmet" value="1" /><span class="sheet-sw-track"></span><span class="sheet-sw-lbl">Stacking</span></label>') + f[k:]
    f = f.replace('<div class="sheet-entry-body">', '<div class="sheet-entry-body"><div class="sheet-ar-panel">' + mid + '</div>', 1)
    h = h[:i] + f + h[j:]
    A = f'{P} .repcontainer[data-groupname="repeating_armor"] .sheet-entry'
    c += '\n'.join([
        f'{A} > .sheet-entry-head .sheet-ar-sum {{ display: inline-flex !important; }}',
        f'{A} > .sheet-entry-head > label.sheet-ar-stk {{ margin-left: 4px !important; }}',
        f'{A} .sheet-ar-panel {{ flex: 0 0 100%; display: flex; flex-wrap: wrap; align-items: center; gap: 4px 10px; }}',
        f'{A} .sheet-ar-panel > .sheet-ar-steps {{ display: flex !important; flex-wrap: wrap; gap: 4px 10px; }}',
        f'{A} .sheet-ar-panel > label.sheet-ar-dtog {{ display: inline-flex !important; align-items: center; gap: 4px; cursor: pointer; flex: 0 0 100%; }}',
        f'{A} .sheet-ar-panel > label.sheet-ar-dtog > input {{ display: none !important; }}',
        f'{A} .sheet-ar-panel > label.sheet-ar-dtog > .sheet-car {{ display: none !important; }}',
        f'{A} .sheet-ar-panel > label.sheet-ar-dtog:not(:has(input:checked)) > .sheet-car-c, {A} .sheet-ar-panel > label.sheet-ar-dtog:has(input:checked) > .sheet-car-o {{ display: inline !important; }}',
        f'{A} > .sheet-entry-head {{ flex-wrap: nowrap !important; }}',
        f'{A} > .sheet-entry-head > input.sheet-ar-name {{ flex: 1 1 60px !important; width: 60px !important; min-width: 0 !important; }}',
        f'{A} > .sheet-entry-head > label.sheet-switch {{ flex: 0 0 auto !important; white-space: nowrap; }}',
        f'{A} .sheet-ar-panel > textarea.sheet-ar-desc {{ flex: 0 0 100%; }}',
    ]) + '\n'
    return h, c
