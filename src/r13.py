"""r13: power-stat headers (Primal Urge, Blood Potency, Gnosis, Wyrd, Azoth, Synergy, Primum, Lair, Sekhem, Acclimation...)
are toggle buttons inside .sheet-subheader; a button colour rule beat the r11 'inherit', so they were light grey instead of the
splat header colour. Force every subheader button to the header colour, size, weight and shadow in all states; font comes from the r11 per-splat rule."""
def apply(h, c):
    P = '.charsheet.charsheet.charsheet.charsheet.charsheet'
    B = [f'{P} .sheet-subheader > button.sheet-toggle', f'{P} .sheet-subheader > button.sheet-toggle span']
    sel = ', '.join(b + s for b in B for s in ('', ':hover', ':active', ':focus', ':focus-visible'))
    r = (sel + ' { color: inherit !important; font-size: inherit !important;'
         ' font-weight: inherit !important; letter-spacing: inherit !important; text-transform: inherit !important;'
         ' font-style: inherit !important; text-shadow: 0 0 3px #000 !important; }')
    return percpill(*ragetint(*fullheal(*more(h, c + '\n' + r + '\n'))))


ICA = 'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@e9f7b1876a225bfdc8b31e70b328ffe29f1bb3df/icons/armor/'
HSZ = '22px'  # measured font-size of the OTHER TRAITS section header: target for headers and pills

def more(h, c):
    import re
    P = '.charsheet.charsheet.charsheet.charsheet.charsheet.charsheet'
    L = []
    # (6) headers and pills at the OTHER TRAITS size
    L.append(f'{P} .sheet-subheader, {P} .sheet-subheader > span, {P} .sheet-subheader > span > span, {P} .sheet-subheader > button.sheet-toggle {{ font-size: {HSZ} !important; line-height: 1.15 !important; }}')
    L.append(f'{P} button.sheet-midtab-btn.sheet-midtab-btn, {P} button.sheet-midtab-btn.sheet-midtab-btn span, {P} label.sheet-ovbtn {{ font-size: 15px !important; }}')
    # (1)(2) right-panel stats block
    D = f'{P} .sheet-organization-inverse > .sheet-derived'
    L += [f'{D} {{ gap: 3px !important; justify-content: space-between !important; }}',
          f'{D} > span {{ font-size: 14px !important; }}',
          f'{P} .sheet-organization-inverse:has(> .sheet-derived) {{ display: grid !important; grid-template-columns: 1fr 1fr; gap: 3px 8px !important; }}',
          f'{P} .sheet-organization-inverse:has(> .sheet-derived) > :not(.sheet-derived) {{ grid-column: 1 / -1; }}',
          f'{D} {{ display: flex !important; align-items: center; min-width: 0 !important; width: auto !important; margin: 0 !important; white-space: nowrap; overflow: visible; }}',
          f'{D}:has(> input[name="attr_balistic_armor_display"]), {D}:has(> input[name="attr_initiative"]) {{ grid-column: 1 / -1; justify-content: flex-start !important; gap: 4px !important; }}',
          f'{D}:has(> input[name="attr_balistic_armor_display"]) > span:first-child, {D}:has(> input[name="attr_initiative"]) > span:first-child {{ flex: 0 0 auto !important; }}',
          f'{D} > span:first-child {{ flex: 1 1 auto; min-width: 0; overflow: hidden; text-overflow: ellipsis; }}',
          f'{D} > input {{ width: 2.6em !important; min-width: 2.6em !important; max-width: 2.6em !important; padding: 0 2px !important; text-align: center !important; box-sizing: border-box; flex: 0 0 auto; }}',
          f'{D}:has(> input[name="attr_balistic_armor_display"]) > input {{ width: 2.1em !important; min-width: 2.1em !important; max-width: 2.1em !important; }}',
          f'{P} .sheet-input-group > span[data-i18n="experience"], {P} .sheet-input-group > .sheet-preserve-whitespace, {P} .sheet-input-group > .sheet-preserve-whitespace > span {{ font-size: 17px !important; color: var(--pa) !important; letter-spacing: .5px; }}',
          f'.sheet-darkmode {P} .sheet-input-group > span[data-i18n="experience"], .sheet-darkmode {P} .sheet-input-group > .sheet-preserve-whitespace > span {{ color: var(--pad) !important; }}',
          f'{P} .sheet-xp-trio {{ display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4px !important; width: 100%; }}',
          f'{P} .sheet-xp-trio > label {{ display: flex !important; flex-direction: column; align-items: center; gap: 1px; font-size: 14px !important; color: var(--pa); min-width: 0; }}',
          f'.sheet-darkmode {P} .sheet-xp-trio > label {{ color: var(--pad); }}',
          f'{P} .sheet-xp-trio > label > input[type=number] {{ width: 100% !important; max-width: 4.2em; min-width: 0 !important; box-sizing: border-box; text-align: center; padding: 0 2px !important; }}',
          f'{P} .sheet-xp-trio > label > .sheet-xp-avail {{ min-width: 2.4em; color: inherit; }}']
    # (3)(4)(5) armor rows
    A = f'{P} .repcontainer[data-groupname="repeating_armor"] .sheet-entry'
    H = A + ' > .sheet-entry-head'
    old = re.search(r'<label class="sheet-ar-dtog"[^>]*><input type="checkbox" name="attr_ar_desc_open" value="1" /><span>Description</span></label>', h)
    assert old, 'ar-dtog'
    h = h.replace(old.group(0), '<label class="sheet-ar-dtog" title="Show / hide the description"><input type="checkbox" name="attr_ar_desc_open" value="1" />'
                  '<span class="sheet-car sheet-car-c">&#9656;</span><span class="sheet-car sheet-car-o">&#9662;</span><span>Description</span></label>', 1)
    a = '<input type="text" class="sheet-ar-name" name="attr_name" placeholder="Armor name" title="Armor name" />'
    assert h.count(a) == 1
    h = h.replace(a, a + '<span class="sheet-ar-sum"><span class="sheet-ar-si sheet-ar-si-g" title="General armor"></span><span class="sheet-ar-sv" name="attr_ar_general" title="General armor"></span>'
                  '<span class="sheet-ar-si sheet-ar-si-b" title="Ballistic armor"></span><span class="sheet-ar-sv" name="attr_ar_ballistic" title="Ballistic armor"></span></span>', 1)
    NC = 'input.sheet-entry-toggle:not(:checked) ~ .sheet-entry-head'
    L += [f'{H} {{ display: flex !important; flex-wrap: wrap; align-items: center; gap: 3px 6px !important; }}',
          f'{H} > * {{ order: 5 !important; }}',
          f'{H} > button.sheet-entry-post {{ order: 1 !important; }}',
          f'{H} > input.sheet-ar-name {{ order: 2 !important; flex: 1 1 8em !important; width: auto !important; min-width: 6em !important; }}',
          f'{H} > .sheet-ar-sum {{ order: 3 !important; display: inline-flex; align-items: center; gap: 3px; font-weight: bold; white-space: nowrap; }}',
          f'{H} > label.sheet-ar-eq {{ order: 4 !important; margin-left: auto !important; }}',
          f'{H} > .sheet-ar-steps {{ flex: 1 1 100% !important; order: 6 !important; }}',
          f'{H} > label.sheet-ar-dtog {{ order: 7 !important; flex: 0 0 auto !important; }}',
          f'{H} > textarea.sheet-ar-desc {{ flex: 1 1 100% !important; order: 8 !important; }}',
          f'{P} .sheet-ar-si {{ display: inline-block; width: 13px; height: 13px; background: url("{ICA}shield-dark.svg") center / 13px 13px no-repeat; }}',
          f'{P} .sheet-ar-si.sheet-ar-si-b {{ background-image: url("{ICA}bullet-dark.svg"); }}',
          f'.sheet-darkmode {P} .sheet-ar-si.sheet-ar-si-g, {P} input.sheet-dm[value="1"] ~ * .sheet-ar-si.sheet-ar-si-g {{ background-image: url("{ICA}shield-light.svg"); }}',
          f'.sheet-darkmode {P} .sheet-ar-si.sheet-ar-si-b, {P} input.sheet-dm[value="1"] ~ * .sheet-ar-si.sheet-ar-si-b {{ background-image: url("{ICA}bullet-light.svg"); }}',
          f'{P} .sheet-ar-sv {{ min-width: 1em; margin-right: 4px; }}',
          f'{A} > {NC} > .sheet-ar-steps, {A} > {NC} > label.sheet-ar-dtog, {A} > {NC} > textarea.sheet-ar-desc {{ display: none !important; }}',
          f'{A} > input.sheet-entry-toggle:checked ~ .sheet-entry-head > .sheet-ar-sum {{ display: none !important; }}',
          f'{H} > label.sheet-ar-dtog > input {{ display: none !important; }}',
          f'{H} > label.sheet-ar-dtog {{ font-size: 12px !important; opacity: 1 !important; color: var(--color-game-line, #b4743a); cursor: pointer; gap: 3px !important; }}',
          f'{H} > label.sheet-ar-dtog > span:last-child {{ text-decoration: underline; text-underline-offset: 2px; }}',
          f'{H} > label.sheet-ar-dtog .sheet-car-o, {H} > label.sheet-ar-dtog:has(input:checked) .sheet-car-c {{ display: none; }}',
          f'{H} > label.sheet-ar-dtog:has(input:checked) .sheet-car-o {{ display: inline; }}',
          f'{H} > label.sheet-ar-eq {{ position: relative; gap: 5px !important; cursor: pointer; font: bold 11px Arial, sans-serif !important; }}',
          f'{H} > label.sheet-ar-eq > input {{ position: absolute !important; opacity: 0 !important; width: 30px !important; height: 16px !important; left: 0; top: 0; margin: 0 !important; z-index: 1; cursor: pointer; }}',
          f'{H} > label.sheet-ar-eq > .sheet-sw-track {{ display: inline-block !important; position: relative; width: 30px !important; height: 16px !important; border-radius: 999px; background: #555 !important; border: 1px solid #888; box-sizing: border-box; flex: 0 0 30px; }}',
          f'{H} > label.sheet-ar-eq > .sheet-sw-track::after {{ content: ""; position: absolute; top: 1px; left: 1px; width: 12px; height: 12px; border-radius: 50%; background: #ddd; transition: left .15s; }}',
          f'{H} > label.sheet-ar-eq > input:checked + .sheet-sw-track {{ background: var(--color-game-line, #b4743a) !important; border-color: var(--color-game-line, #b4743a); }}',
          f'{H} > label.sheet-ar-eq > input:checked + .sheet-sw-track::after {{ left: 15px; background: #fff; }}',
          f'{A} .sheet-stp-v {{ width: 2.6em !important; min-width: 0 !important; text-align: center; padding: 0 !important; }}']
    # (8) equipment entries: numeric fields become number steppers; inputs sized to content
    m = re.search(r'<fieldset class="repeating_equipment">.*?</fieldset>', h, re.S); b = m.group(0)
    for f in ('durability', 'structure', 'esize', 'dice_bonus'):
        o = f'<input type="text" name="attr_{f}" />'; assert o in b, f
        b = b.replace(o, f'<input type="number" class="sheet-eq-num" name="attr_{f}" step="1" />', 1)
    h = h[:m.start()] + b + h[m.end():]
    for sec in ('equipment', 'armor', 'weapons'):
        G = f'{P} .repcontainer[data-groupname="repeating_{sec}"] .sheet-entry-body'
        L += [f'{G} {{ display: flex !important; flex-wrap: wrap; gap: 3px 10px !important; align-items: center; }}',
              f'{G} > label:not(.sheet-wide) {{ display: inline-flex !important; align-items: center; gap: 4px; width: auto !important; flex: 0 0 auto; }}',
              f'{G} > label:not(.sheet-wide) > input[type=text], {G} > label:not(.sheet-wide) > select {{ width: 10em !important; flex: 0 0 auto; }}',
              f'{G} input[type=number] {{ width: 3.6em !important; min-width: 0 !important; text-align: center; flex: 0 0 auto; }}',
              f'{G} input[type=number]::-webkit-inner-spin-button, {G} input[type=number]::-webkit-outer-spin-button {{ opacity: 1; }}',
              f'{G} > .sheet-wide, {G} > label.sheet-wide {{ flex: 1 1 100% !important; }}']
    # (7) Werewolf Forms drop-down
    o = '<option value="urkhar">Ur&#39;Khar (Firstborn rules)</option>'; assert o in h
    h = h.replace(o, '<option value="urkhar">Ur&#39;Khar</option>')
    WR = '"WolfsRain", "IM Fell English SC", serif'
    L.append(f'{P} select.sheet-rp-formsel {{ width: auto !important; min-width: 7em; max-width: 100%; display: block; margin: 2px auto !important; text-align: center; text-align-last: center; font-family: {WR} !important; font-size: 18px !important; }}')
    L.append(f'{P} select.sheet-rp-formsel option {{ font-family: {WR}; text-align: center; }}')
    # (10) middle pills: Weapons first, Gear second; Weapons is the default tab
    m = re.search(r'<div class="sheet-midtabs">(.*?)</div>', h, re.S)
    btns = re.findall(r'<button type="action" class="sheet-midtab-btn.*?</button>', m.group(1), re.S)
    assert ''.join(btns) == m.group(1)
    key = lambda x: 0 if 'sheet-mt-weapons' in x else 1 if 'sheet-mt-gear' in x else 2
    h = h[:m.start(1)] + ''.join(sorted(btns, key=key)) + h[m.end(1):]
    o = 'name="attr_mid_tab" value="merits"'; assert h.count(o) == 1
    h = h.replace(o, 'name="attr_mid_tab" value="weapons"')
    h = h.replace('setAttrs({mid_tab: "merits"}', 'setAttrs({mid_tab: "weapons"}').replace('u.mid_tab = "merits"', 'u.mid_tab = "weapons"')
    # (11) resource counters: current value styled exactly like the max, no box
    R = f'{P} input.sheet-res-cur.sheet-res-cur'
    L += [f'{R}, {P} .sheet-res-max, {P} .sheet-res-sep {{ font-family: inherit !important; font-size: 15px !important; font-weight: 700 !important; color: inherit !important; line-height: 20px !important; vertical-align: baseline !important; }}',
          f'{R} {{ -webkit-appearance: textfield !important; -moz-appearance: textfield !important; appearance: textfield !important; border: 0 !important; background: transparent !important; box-shadow: none !important; outline: 0; padding: 0 !important; margin: 0 !important; height: 20px !important; width: 2ch !important; min-width: 2ch !important; text-align: right !important; }}',
          f'{R}::-webkit-inner-spin-button, {R}::-webkit-outer-spin-button {{ -webkit-appearance: none !important; margin: 0; }}',
          f'{P} .sheet-res-max {{ min-width: 2ch; text-align: left; display: inline-block; }}']
    L += [f'{P} .sheet-res-max, {P} .sheet-res-sep, {R} {{ display: inline-block !important; height: 20px !important; box-sizing: border-box !important; align-self: center !important; vertical-align: middle !important; position: static !important; top: auto !important; transform: none !important; }}']
    L += [f'{P} input[name="attr_auspice"], {P} input[name="attr_GroupName"], {P} select[name="attr_auspice"] {{ max-width: 100% !important; min-width: 0 !important; box-sizing: border-box !important; }}']
    return h, c + '\n'.join(L) + '\n'


def fullheal(h, c):
    """(12) Full Heal is a latching toggle: while armed, each heal button clears all damage of its type."""
    b = '<button type="action" class="sheet-hb-full" name="act_fullheal"'
    assert h.count(b) == 1
    h = h.replace(b, '<input type="hidden" class="sheet-fh-arm" name="attr_fullheal_arm" value="0" />' + b, 1)
    h = h.replace('title="Full Heal: clear every Health box (all bashing, lethal and aggravated damage)"',
                  'title="Full Heal toggle: while lit, a heal button clears ALL damage of that type. Click again to turn off."', 1)
    old = 'on("clicked:fullheal", () => { const u = {}; for (let i = 1; i <= 16; i++) u["healthbox_" + i] = "0"; setAttrs(u); });'
    assert h.count(old) == 1
    h = h.replace(old, 'on("clicked:fullheal", () => getAttrs(["fullheal_arm"], v => setAttrs({fullheal_arm: v.fullheal_arm === "1" ? "0" : "1"})));', 1)
    old = 'on("clicked:heal_b", () => healOne(1)); on("clicked:heal_l", () => healOne(2)); on("clicked:heal_a", () => healOne(3));'
    assert h.count(old) == 1
    new = r'''const healAll = (lvl) => { const ks = [...Array(16).keys()].map(i => `healthbox_${i + 1}`);
            getAttrs(["health"].concat(ks), v => { const n = Math.min(16, parseInt(v.health) || 0);
                const vals = ks.slice(0, n).map(k => parseInt(v[k]) || 0).map(x => x === lvl ? 0 : x).sort((x, y) => y - x);
                const u = {}; vals.forEach((x, i) => { if ((parseInt(v[ks[i]]) || 0) !== x) u[ks[i]] = x; }); setAttrs(u); }); };
        const healBtn = (lvl) => getAttrs(["fullheal_arm"], v => v.fullheal_arm === "1" ? healAll(lvl) : healOne(lvl));
        on("clicked:heal_b", () => healBtn(1)); on("clicked:heal_l", () => healBtn(2)); on("clicked:heal_a", () => healBtn(3));'''
    h = h.replace(old, new, 1)
    P = '.charsheet.charsheet.charsheet.charsheet'
    G = 'var(--color-game-line, #b4743a)'
    c += '\n'.join([
        f'{P} input.sheet-fh-arm[value="1"] + button.sheet-hb-full {{ background: {G} !important; border-color: {G} !important; color: #fff !important; box-shadow: 0 0 6px {G}, inset 0 0 3px rgba(255,255,255,.5) !important; }}',
        f'{P} input.sheet-fh-arm[value="1"] ~ .sheet-hb-heal button {{ box-shadow: 0 0 4px {G} !important; }}',
    ]) + '\n'
    return h, c


def ragetint(h, c):
    """(14) Death Rage / Frenzy: one uniform red treatment over the whole sheet. A 'color' blend layer takes hue and
    saturation from red and keeps each pixel's luminosity, so every panel, input, pill and header turns red
    while white text (max luminosity) stays white."""
    L = []
    for m in ('input.sheet-kmode[value="1"]', 'input.sheet-fmode[value="1"]'):
        M = f'.charsheet.charsheet {m} ~ .sheet-page'
        R = f'.charsheet.charsheet:has({m})'
        L += [f'{R} {{ position: relative !important; isolation: isolate; }}',
              f'{R}::after {{ content: ""; position: absolute; inset: 0; z-index: 2147483000; pointer-events: none; background: #b82418; mix-blend-mode: color; }}',
              f'{M} input:not([type=checkbox]):not([type=radio]), {M} textarea, {M} select, {M} button.sheet-midtab-btn {{ border-color: #c0302a !important; }}']
    return h, c + '\n'.join(L) + '\n'


def percpill(h, c):
    """(15) Perception as a pill identical to Initiative, on the same row."""
    import re
    m = re.search(r'\s*<div class="sheet-corporeal sheet-span">(<button type="action" class="sheet-quick sheet-perception sheet-was-roll"[^>]*name="act_rr_perception">.*?</button>)</div>', h, re.S)
    assert m
    btn = m.group(1); h = h[:m.start()] + h[m.end():]
    k = h.index('<button type="roll" class="sheet-inline-flex" name="roll_initiative"')
    e = h.index('</button>', k) + len('</button>')
    h = h[:e] + btn + h[e:]
    P = '.charsheet.charsheet.charsheet.charsheet .sheet-diceroller-grid > .sheet-span'
    I = f'{P} button[name="roll_initiative"]'; Q = f'{P} button[name="act_rr_perception"]'
    c += '\n'.join([
        f'{P}:has(> button[name="roll_initiative"]) {{ display: flex !important; align-items: center; justify-content: center; gap: 6px !important; flex-wrap: wrap; }}',
        f'{I}, {Q} {{ font: bold 13px/1.3 Arial, sans-serif !important; color: rgb(232, 232, 232) !important; background: none !important; border: 1px solid rgba(160,160,160,.55) !important; border-radius: 999px !important; padding: 0 12px !important; height: 25px !important; box-sizing: border-box !important; display: inline-flex !important; align-items: center; gap: 4px; margin: 0 !important; box-shadow: 0 1px 2px rgba(0,0,0,.4) !important; text-shadow: 0 0 3px #000 !important; width: auto !important; }}',
        f'{I}:hover, {Q}:hover {{ border-color: var(--color-game-line, #b4743a) !important; }}',
    ]) + '\n'
    return h, c
