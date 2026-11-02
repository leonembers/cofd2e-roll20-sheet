"""r10b: own middle tabs (Gifts/Rites/Totem for Werewolf; Disciplines/Devotions/Frenzy for Vampire), compact
collapsible power rows, Kuruth order + voluntary Basu-Im, Vampire Frenzy mode, Changing-Breeds isolation."""
import re

def take_div(h, start):
    """Return (begin, end) of the balanced <div ...> starting at index start."""
    d = 0
    for m in re.finditer(r'<div\b|</div>', h[start:]):
        d += 1 if m.group(0) == '<div' else -1
        if d == 0:
            return start, start + m.end()
    raise ValueError

def compact(h, sec):
    i = h.index(f'<fieldset class="repeating_{sec}">'); j = h.index('</fieldset>', i); s = h[i:j]
    s = s.replace('name="attr_show" value="1" checked', 'name="attr_show" value="1"', 1)
    s = re.sub(r'<input type="text" class="sheet-entry-short"[^>]*/>', '', s, 1)
    s = re.sub(r'<label class="sheet-wide"><span data-i18n="lbl-short">Short description</span><input type="text" name="attr_short_desc" /></label>', '', s, 1)
    if sec == 'gifts':
        s = s.replace('<div class="sheet-entry-head">', '<input type="hidden" class="sheet-gt-flag" name="attr_gtype" value="" /><div class="sheet-entry-head">', 1)
    return h[:i] + s + h[j:]

PT = {  # pseudo-tabs that reuse the powers pane: type -> {tab: sections shown}
    'werewolf2': {'powers': ['gifts'], 'rites': ['writes'], 'totem': ['totem']},
    'vampire2': {'powers': ['disciplines'], 'devotions': ['devotions', 'vrites', 'vinculum']},
}
LBL = {'rites': ('werewolf2', 'Rites', 'Werewolf Rites'), 'totem': ('werewolf2', 'Totem', 'Pack Totem'),
       'devotions': ('vampire2', 'Devotions', 'Devotions and Vinculum'), 'frenzy': ('vampire2', 'Frenzy', 'Frenzy / R&#246;tschreck, Touchstones and Banes')}
FRULES = ('<div class="sheet-km-rules"><b>Frenzy mode</b><br/>A failed Resist roll (Resolve + Blood Potency) means the Beast takes over: '
          'Frenzy (Wrath) attacks the source of anger, R&#246;tschreck (Fear) flees from fire or sunlight, Hunger feeds on the nearest vessel. '
          'Riding the Wave: the vampire may give in voluntarily and keeps a single purpose (rules reading not checked against the V:tR 2E book; verify). '
          'The frenzy ends when the trigger is gone or the scene ends; press End Frenzy then.</div>'
          '<div class="sheet-fr-trig"><b>Common triggers</b> (verify vs V:tR 2E): provocation or humiliation (Wrath), fire or sunlight (R&#246;tschreck), '
          'blood when Vitae is low (Hunger).</div>')

def apply(h, c):
    for sec in ('gifts', 'disciplines', 'devotions', 'writes', 'vrites'):
        h = compact(h, sec)
    # gift display filter
    a = '<div class="sheet-entry-section sheet-gifts sheet-pw">\n<div class="sheet-entry-section-head"><span class="sheet-subheader"><span data-i18n="gifts">Gifts</span></span>'
    assert a in h
    h = h.replace(a, a + '<select class="sheet-gfilt" name="attr_gift_filter" title="Show gifts of one type"><option value="all" selected>All</option><option value="Moon">Moon</option><option value="Shadow">Shadow</option><option value="Wolf">Wolf</option><option value="Other">Other</option></select>', 1)
    # tab buttons
    b = '<button type="action" class="sheet-midtab-btn sheet-mt-weapons"'
    add = ''.join(f'<button type="action" class="sheet-midtab-btn sheet-mt-{t} sheet-game-line sheet-{ty}" name="act_midtab_{t}" title="{ti}">{lb}</button>'
                  for t, (ty, lb, ti) in LBL.items())
    assert h.count(b) == 1; h = h.replace(b, add + b, 1)
    h = h.replace('<span class="sheet-game-line sheet-werewolf" >Gifts &amp; Renown</span>', '<span class="sheet-game-line sheet-werewolf" >Gifts</span>', 1)
    old = '["merits","powers","weapons","kuruth","rituals","gear"].forEach('
    assert old in h; h = h.replace(old, '["merits","powers","weapons","kuruth","rituals","gear","rites","totem","devotions","frenzy"].forEach(', 1)
    # Kuruth: voluntary Basu-Im button
    k = '<button type="action" class="sheet-kuruth-roll sheet-rage sheet-was-roll"'
    i = h.index(k); j = h.index('</button>', i) + 9
    h = h[:j] + ('<button type="action" class="sheet-kuruth-roll sheet-rage sheet-basu" name="act_basuim" title="Give in to the Hard Rage from Wasu-Im: enter the Death Rage now (no roll)">'
                 '&#128293; Basu-Im!</button>') + h[j:]
    # Vampire Frenzy pane: move Touchstones and Banes into it
    parts = []
    for cls in ('sheet-vtouchstones', 'sheet-banes'):
        i = h.index(f'<div class="sheet-entry-section {cls}">'); a0, a1 = take_div(h, i)
        parts.append(h[a0:a1]); h = h[:a0] + h[a1:]
    pane = ('<div class="sheet-midpane sheet-mp-frenzy sheet-game-line sheet-vampire2"><div class="sheet-leon-page sheet-leon-pane">'
            + parts[0] + '<div class="sheet-subheader"><span>Frenzy</span></div>' + FRULES +
            '<div class="sheet-kuruth-rolls">'
            '<button type="action" class="sheet-kuruth-roll sheet-rage sheet-was-roll" name="act_rr_frenzy" title="Resist Frenzy: Resolve + Blood Potency">&#128165; Resist Frenzy</button>'
            '<button type="action" class="sheet-kuruth-roll sheet-rage sheet-was-roll" name="act_rr_rotschreck" title="Resist R&#246;tschreck: Resolve + Blood Potency">&#128293; Resist R&#246;tschreck</button>'
            '<button type="action" class="sheet-kuruth-roll sheet-rage sheet-basu" name="act_ridewave" title="Ride the Wave: give in to the Beast voluntarily (no roll)">&#127754; Ride the Wave</button>'
            '</div>' + parts[1] + '</div></div>')
    r = h.index('<div class="sheet-midpane sheet-mp-rituals'); h = h[:r] + pane + h[r:]
    # Frenzy mode state + banner
    m = re.search(r'<input type="hidden" class="sheet-kmode"[^>]*/>', h)
    h = h[:m.end()] + '<input type="hidden" class="sheet-fmode" name="attr_frenzy_active" value="0" /><input type="hidden" name="attr_frenzy_kind" value="" />' + h[m.end():]
    ban = ('<div class="sheet-fm-banner"><span class="sheet-km-title">FRENZY: <span name="attr_frenzy_kind"></span></span>'
           '<button type="action" class="sheet-km-end" name="act_frenzyend" title="End the frenzy">End Frenzy</button></div>')
    a = h.index('<div class="sheet-km-banner">'); h = h[:a] + ban + h[a:]
    # RR: Rotschreck macro + result hook
    rm = re.search(r'"frenzy": "(.*?)", "detachment"', h)
    rot = rm.group(1).replace('{{kind=Frenzy}}', '{{kind=Rotschreck}}').replace('{{f_pool=Resist Frenzy / R\\u00f6tschreck (Resolve + Blood Potency)}}', '{{f_pool=Resist R\\u00f6tschreck: Resolve + Blood Potency}}')
    h = h[:rm.start()] + f'"frenzy": "{rm.group(1)}", "rotschreck": "{rot}", "detachment"' + h[rm.end():]
    hook = 'if (/\\{\\{kind=Death Rage\\}\\}/.test(mac)'
    assert hook in h
    h = h.replace(hook, 'if (!isRe && /\\{\\{kind=(Frenzy|Rotschreck)\\}\\}/.test(mac) && R.roll && (R.roll.result || 0) < 1) frenzyEnter(/kind=Rotschreck/.test(mac) ? "R\\u00f6tschreck" : "Wrath"); ' + hook, 1)
    js = r'''
        const frenzyEnter = (kind) => setAttrs({frenzy_active: "1", frenzy_kind: kind});
        on("clicked:frenzyend", () => setAttrs({frenzy_active: "0", frenzy_kind: ""}));
        on("clicked:ridewave", () => { frenzyEnter("Riding the Wave");
            startRoll("&{template:cofd-entry} {{charname=@{character_name}}} {{gl_vampire=1}} {{splat=vampire}} {{kind=Frenzy}} {{name=Riding the Wave}} {{emote=@{character_name} lets the Beast loose, holding on to one purpose.}}", r => finishRoll(r.rollId)); });
        on("clicked:basuim", () => { kuruthEnter();
            startRoll("&{template:cofd-entry} {{charname=@{character_name}}} {{gl_werewolf=1}} {{splat=werewolf}} {{kind=Death Rage}} {{name=Basu-Im!}} {{emote=@{character_name} gives in to the Hard Rage. Friend and foe alike are prey.}}", r => finishRoll(r.rollId)); });
        on("sheet:opened change:sheettype", () => getAttrs(["sheettype", "frenzy_active", "mid_tab"], v => { const u = {};
            if (v.sheettype !== "vampire2" && v.frenzy_active === "1") u.frenzy_active = "0";
            const own = {rites: "werewolf2", totem: "werewolf2", kuruth: "werewolf2", devotions: "vampire2", frenzy: "vampire2", rituals: "vampire2"}[v.mid_tab];
            if (own && own !== v.sheettype) u.mid_tab = "merits"; if (Object.keys(u).length) setAttrs(u); }));
'''
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]

    # ---- CSS ----
    C = []
    for t in ('rites', 'totem', 'devotions'):
        C.append(f'.charsheet input.sheet-midtab[value="{t}"] ~ .sheet-midpane.sheet-mp-powers {{ display: block !important; }}')
    C.append('.charsheet input.sheet-midtab[value="frenzy"] ~ .sheet-midpane.sheet-mp-frenzy { display: block !important; }')
    for ty, tabs in PT.items():
        for tab, show in tabs.items():
            others = sorted({s for v in tabs.values() for s in v} - set(show))
            pre = f'.charsheet input.sheet-type[value="{ty}"] ~ * input.sheet-midtab[value="{tab}"] ~ .sheet-midpane.sheet-mp-powers'
            C.append(', '.join(f'{pre} .sheet-entry-section.sheet-{s}' for s in others) + ' { display: none !important; }')
            if tab != 'powers':
                C.append(f'{pre} .sheet-wolf-block, {pre} .sheet-leon-pane > .sheet-entry-section-head {{ display: none !important; }}')
    C += [
        '.charsheet .sheet-mp-powers .sheet-wolf-moon { display: none !important; }',
        # Changing Breeds-only fields stay on Changing Breeds
        '.charsheet input.sheet-type:not([value="breeds2"]) ~ * .sheet-breeds2:not(.sheet-werewolf2), .charsheet input.sheet-type:not([value="breeds2"]) ~ .sheet-breeds2:not(.sheet-werewolf2) { display: none !important; }',
        '.charsheet input.sheet-type[value="breeds2"] ~ * .sheet-werewolf2:not(.sheet-breeds2) { display: none !important; }',
        # Kuruth tab order: Touchstones, Kuruth Triggers, tiers, rolls, rules
        '.charsheet .sheet-mp-kuruth > .sheet-leon-pane { display: flex !important; flex-direction: column; }',
        '.charsheet .sheet-mp-kuruth > .sheet-leon-pane > * { order: 9; }',
        '.charsheet .sheet-mp-kuruth > .sheet-leon-pane > .sheet-subheader:not(:has(span[data-i18n="kuruth-triggers"])) { order: 1; }',
        '.charsheet .sheet-mp-kuruth > .sheet-leon-pane > .sheet-wolf-ts { order: 2; }',
        '.charsheet .sheet-mp-kuruth > .sheet-leon-pane > .sheet-subheader:has(span[data-i18n="kuruth-triggers"]) { order: 3; }',
        '.charsheet .sheet-mp-kuruth > .sheet-leon-pane > .sheet-kuruth-tiers { order: 4; }',
        '.charsheet .sheet-mp-kuruth > .sheet-leon-pane > .sheet-kuruth-rolls { order: 5; }',
        '.charsheet .sheet-mp-kuruth > .sheet-leon-pane > .sheet-km-rules { order: 6; }',
        '.charsheet .sheet-kuruth-rolls { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }',
        '.charsheet.charsheet button.sheet-basu { background: #5a0d0d !important; color: #fff !important; border: 1px solid #e03a2f !important; border-radius: 999px !important; padding: 3px 12px !important; font-weight: bold; width: auto !important; height: auto !important; }',
        '.charsheet .sheet-fr-trig { font-size: 12px; margin: 0 0 8px; opacity: .9; }',
        # Frenzy banner/tint
        '.charsheet .sheet-fm-banner { display: none; }',
        '.charsheet input.sheet-fmode[value="1"] ~ .sheet-fm-banner { display: flex !important; align-items: center; justify-content: center; gap: 10px; margin: 4px 6px; padding: 6px 10px; background: linear-gradient(90deg, #4a0b0b, #8e1616, #4a0b0b); border: 2px solid #e03a2f; border-radius: 6px; box-shadow: 0 0 14px rgba(224,58,47,.55); color: #fff; }',
        '.charsheet input.sheet-fmode[value="1"] ~ .sheet-fm-banner .sheet-km-title { font-size: 18px; font-weight: bold; letter-spacing: 2px; }',
        '.charsheet.charsheet .sheet-fm-banner button.sheet-km-end { background: #fff !important; color: #8e1616 !important; border-radius: 4px; padding: 3px 12px !important; font-weight: bold; width: auto !important; height: auto !important; }',
        '.charsheet input.sheet-fmode[value="1"] ~ .sheet-page { box-shadow: inset 0 0 40px rgba(200,30,30,.35); background-color: rgba(120,0,0,.12); }',
        '.charsheet input.sheet-fmode[value="1"] ~ .sheet-page .sheet-subheader { color: #ff5a4a !important; }',
        '.charsheet.charsheet .sheet-background > .sheet-fm-banner { order: 0; }',
        # gift filter
        '.charsheet.charsheet select.sheet-gfilt { width: 84px !important; height: 22px; margin-left: auto; font-size: 12px; }',
    ]
    for v in ('Moon', 'Shadow', 'Wolf', 'Other'):
        C.append(f'.charsheet .sheet-entry-section.sheet-gifts:has(select.sheet-gfilt option[value="{v}"]:checked) .repitem:not(:has(input.sheet-gt-flag[value="{v}"])) {{ display: none !important; }}')
    # compact one-line rows
    for sec in ('gifts', 'disciplines', 'devotions', 'writes', 'vrites'):
        g = f'.charsheet.charsheet .repcontainer[data-groupname="repeating_{sec}"]'
        C += [f'{g} .sheet-entry-head {{ display: flex !important; flex-wrap: nowrap !important; align-items: center; gap: 4px !important; min-height: 24px; padding: 1px 4px !important; }}',
              f'{g} .sheet-entry-head > button.sheet-entry-post {{ flex: 1 1 0 !important; min-width: 0 !important; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: left; }}',
              f'{g} .sheet-entry-head > .sheet-entry-pool {{ flex: 0 1 auto; max-width: 40%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 11px; }}',
              f'{g} .sheet-entry-body {{ display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px 8px; }}',
              f'{g} .sheet-entry-body > .sheet-wide, {g} .sheet-entry-body > .sheet-pw-box, {g} .sheet-entry-body > .sheet-outcomes {{ grid-column: 1 / -1; }}',
              f'{g} .sheet-entry-body input[type=number] {{ width: 52px !important; }}',
              f'{g} .sheet-entry-body input[type=text], {g} .sheet-entry-body select {{ width: 100% !important; box-sizing: border-box; }}',
              f'{g} .sheet-entry-item {{ margin-bottom: 2px !important; }}']
    WR = 'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@79f50b7a14503fe7c6009d1b7febafb78b2d2094/fonts/wolfsrain/WolfsRain.ttf'
    C.append('@font-face { font-family: "WolfsRain"; src: url("' + WR + '") format("truetype"); font-display: swap; }')
    W = '.charsheet input.sheet-type[value="werewolf2"] ~ '
    W2 = '.charsheet.charsheet.charsheet.charsheet input.sheet-type[value="werewolf2"] ~ '
    C.append(', '.join(W2 + x for x in ('* .sheet-subheader', '* .sheet-subheader span', '* .sheet-midtabs button', '* h1', '* h2', '* h3')) +
             ' { font-family: "WolfsRain", "IM Fell English SC", serif !important; letter-spacing: 1px; }')
    C.append('.charsheet .sheet-fontcredit { display: none; font-size: 10px; opacity: .6; text-align: center; margin: 6px 0; }')
    C.append(W + '.sheet-fontcredit, ' + W + '* .sheet-fontcredit { display: block !important; }')
    G = '.charsheet.charsheet .sheet-settings .sheet-cfg-grid'
    C += [G + ' { display: block !important; column-width: 300px; column-count: 3; column-gap: 10px; }',
          G + ' > .sheet-cfg-card { display: inline-block !important; width: 100% !important; box-sizing: border-box; break-inside: avoid; margin: 0 0 10px !important; vertical-align: top; }',
          G + ' > .sheet-cfg-card.sheet-cfg-wide { column-span: all; display: block !important; }']
    import json, os, extras
    T = '.charsheet.charsheet .sheet-settings input[type=checkbox]:not(.sheet-cfg-sw > input):not(.sheet-switch > input)'
    C += [T + ' { -webkit-appearance: none !important; appearance: none !important; position: relative; display: inline-block !important; width: 32px !important; height: 16px !important; min-width: 32px; margin: 0 4px !important; padding: 0 !important; border: 0 !important; border-radius: 8px !important; background: #777 !important; opacity: 1 !important; cursor: pointer; vertical-align: middle; transition: background .15s; }',
          T + '::after { content: ""; position: absolute; left: 2px; top: 2px; width: 12px; height: 12px; border-radius: 50%; background: #fff; transition: left .15s; }',
          T + ':checked { background: #b4743a !important; }', T + ':checked::after { left: 18px; }',
          T + '::before { display: none !important; content: none !important; }']
    B = '.charsheet.charsheet.charsheet .sheet-settings button.sheet-toggle:not([name^="act_sheet_type_"])'
    C += ['.charsheet.charsheet.charsheet .sheet-settings input.sheet-flag ~ button:not(.sheet-toggle) { display: none !important; }',
          B + ', .charsheet.charsheet.charsheet.charsheet input.sheet-dm ~ .sheet-background .sheet-settings button.sheet-toggle:not([name^="act_sheet_type_"]), .charsheet.charsheet.charsheet.charsheet .sheet-settings input.sheet-flag[value="1"] ~ button.sheet-toggle:not([name^="act_sheet_type_"]) { background: rgba(0,0,0,0) !important; background-color: rgba(0,0,0,0) !important; color: inherit !important; border: 0 !important; box-shadow: none !important; }',
          B + ' { position: relative; background: rgba(0,0,0,0) !important; border: 0 !important; box-shadow: none !important; color: inherit !important; padding: 2px 4px 2px 42px !important; text-align: left; min-height: 20px; }',
          B + '::before { content: "" !important; display: block !important; position: absolute; left: 4px; top: 50%; margin-top: -8px; width: 32px; height: 16px; border-radius: 8px; background: #777; border: 0 !important; }',
          B + '::after { content: "" !important; display: block !important; position: absolute; left: 6px; top: 50%; margin-top: -6px; width: 12px; height: 12px; border-radius: 50%; background: #fff; transition: left .15s; }',
          '.charsheet.charsheet.charsheet .sheet-settings input.sheet-flag[value="1"] ~ button.sheet-toggle:not([name^="act_sheet_type_"])::before { background: #b4743a; }',
          '.charsheet.charsheet.charsheet .sheet-settings input.sheet-flag[value="1"] ~ button.sheet-toggle:not([name^="act_sheet_type_"])::after { left: 22px; }',
          '.charsheet .sheet-quick-actions.sheet-hunter2 { display: flex !important; flex-wrap: wrap; justify-content: center !important; text-align: center !important; }',
          '.charsheet div:has(> .sheet-quick-actions.sheet-hunter2) { text-align: center !important; }',
          '.charsheet div:has(> .sheet-quick-actions.sheet-hunter2) > .sheet-subheader { justify-content: center !important; text-align: center !important; }']
    C.append('.charsheet.charsheet.charsheet .sheet-diceroller-options { display: flex !important; flex-wrap: wrap; justify-content: center !important; gap: 4px; border: 0 !important; background: none !important; box-shadow: none !important; outline: 0 !important; }')
    C.append('.charsheet.charsheet .sheet-spacer:has(+ .sheet-page.sheet-page1), .charsheet.charsheet .sheet-background > button.sheet-page-conditions + .sheet-spacer, .charsheet.charsheet .sheet-page.sheet-page1 > .sheet-spacer:first-child { display: none !important; }')
    C.append('.charsheet.charsheet .sheet-page.sheet-page1 > .sheet-corporeal:first-of-type > .sheet-section-header:first-child { margin-top: 6px !important; }')
    cols = json.load(open(os.path.join(os.path.dirname(__file__), 'splat_colors.json')))
    for k, col in cols.items():
        for t in extras.TYPE_OF.get(k, []):
            C.append(f'.charsheet.charsheet input.sheet-type[value="{t}"] ~ .sheet-settings input[type=checkbox]:checked, .charsheet.charsheet input.sheet-type[value="{t}"] ~ * .sheet-settings input[type=checkbox]:checked, .charsheet.charsheet input.sheet-type[value="{t}"] ~ * .sheet-settings input.sheet-flag[value="1"] ~ button.sheet-toggle::before, .charsheet.charsheet.charsheet input.sheet-type[value="{t}"] ~ * .sheet-settings .sheet-cfg-sw > input:checked + .sheet-cfg-knob {{ background: {col} !important; }}')
    c += '\n' + '\n'.join(C) + '\n'
    h = h.replace('<div class="sheet-config-title">CONFIG</div>', '<div class="sheet-config-title">CONFIG</div><div class="sheet-fontcredit">Headers: Wolf&#39;s Rain font by Gabriel Beatty (wolfs-rain.org), CC BY-NC-ND 4.0.</div>', 1)
    return h, c
