"""r15: compact power edit row (steppers + Deduct switch), compact Full Heal pill, Warrior's Hide health, pill typography."""
import re
P = '.charsheet.charsheet.charsheet.charsheet'
G = 'var(--color-game-line, #b4743a)'
PWF = [('pp_mod', 'Modifier', -10, 10), ('cost_wp', 'Willpower', 0, 10), ('cost_pw', None, 0, 20)]


def stp(a, lbl, lo, hi):
    lab = f'<span class="sheet-stp-l">{lbl}</span>' if lbl else '<span class="sheet-stp-l" name="attr_pw_label">Power</span>'
    t = lbl or 'Power cost'
    d = a.replace('_', '-')
    return (f'<span class="sheet-stp sheet-pw-stp" title="{t}">{lab}'
            f'<button type="action" class="sheet-stp-b" name="act_{d}-dec" title="{t} -1">-</button>'
            f'<input type="number" class="sheet-stp-v" name="attr_{a}" value="0" min="{lo}" max="{hi}" step="1" />'
            f'<button type="action" class="sheet-stp-b" name="act_{d}-inc" title="{t} +1">+</button></span>')


def powers(h, c):
    secs = []
    out, pos = [], 0
    for m in re.finditer(r'<fieldset class="repeating_([a-z0-9_]+)">.*?</fieldset>', h, re.S):
        f = m.group(0)
        if 'class="sheet-pw-box"' not in f:
            continue
        secs.append(m.group(1))
        f = re.sub(r'<label>Modifier <input type="number" name="attr_pp_mod" value="0" /></label></div><div class="sheet-pw-row"><b>Cost</b>'
                   r'<label>Willpower <input type="number" min="0" name="attr_cost_wp" value="0" /></label>'
                   r'<label><span name="attr_pw_label">Power</span> <input type="number" min="0" name="attr_cost_pw" value="0" /></label>'
                   r'<label class="sheet-pw-auto" title="[^"]*"><input type="checkbox" name="attr_cost_auto" value="1" /> Deduct when rolled</label></div>'
                   r'<div class="sheet-pw-hint">[^<]*</div>',
                   '</div><div class="sheet-pw-row sheet-pw-row2">' + ''.join(stp(*x) for x in PWF) +
                   '<label class="sheet-pw-auto sheet-switch" title="Roll button also deducts the cost"><input type="checkbox" name="attr_cost_auto" value="1" />'
                   '<span class="sheet-sw-track"></span><span class="sheet-sw-lbl">Deduct when rolled</span></label></div>', f, 1)
        assert 'sheet-pw-row2' in f, m.group(1)
        out.append(h[pos:m.start()] + f); pos = m.end()
    h = ''.join(out) + h[pos:]
    js = ('        ' + repr({a: [lo, hi] for a, _, lo, hi in PWF}).replace("'", '"').join(['const R15_ST = ', ';\n']) +
          '        ' + repr(secs).replace("'", '"').join(['const R15_SECS = ', ';\n']) +
          r'''        R15_SECS.forEach(sec => Object.keys(R15_ST).forEach(a => [["dec", -1], ["inc", 1]].forEach(([k, d]) => on(`clicked:repeating_${sec}:${a.replace(/_/g, "-")}-${k}`, () => {
            const p = `repeating_${sec}_${a}`; getAttrs([p], v => { const [lo, hi] = R15_ST[a]; setAttrs({[p]: Math.max(lo, Math.min(hi, (parseInt(v[p], 10) || 0) + d))}); }); }))));
''')
    k = h.index('<script type="text/worker">') + len('<script type="text/worker">')
    h = h[:k] + '\n' + js + h[k:]
    B = f'{P}{P} .sheet-pw-box'
    c += '\n'.join([
        f'{B} .sheet-pw-row {{ display: flex !important; flex-wrap: wrap !important; align-items: center !important; gap: 4px 12px !important; }}',
        f'{B} .sheet-pw-row > label {{ display: inline-flex !important; align-items: center; gap: 4px; width: auto !important; flex: 0 0 auto !important; margin: 0 !important; }}',
        f'{B} .sheet-pw-row select {{ width: auto !important; min-width: 0 !important; max-width: 150px !important; flex: 0 0 auto !important; }}',
        f'{B} .sheet-pw-stp {{ display: inline-flex !important; align-items: center; gap: 3px; flex: 0 0 auto !important; white-space: nowrap; }}',
        f'{B} .sheet-pw-stp input.sheet-stp-v {{ width: 30px !important; min-width: 0 !important; text-align: center; -moz-appearance: textfield; appearance: textfield; padding: 0 !important; }}',
        f'{B} .sheet-pw-stp input.sheet-stp-v::-webkit-inner-spin-button, {B} .sheet-pw-stp input.sheet-stp-v::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}',
        f'{B} .sheet-pw-stp button.sheet-stp-b {{ width: 16px !important; height: 16px !important; min-width: 0 !important; padding: 0 !important; border-radius: 50% !important; border: 1px solid currentColor !important; font: bold 11px/14px Arial, sans-serif !important; text-align: center; background: none !important; color: inherit !important; }}',
        f'{B} label.sheet-pw-auto.sheet-switch {{ display: inline-flex !important; align-items: center !important; white-space: nowrap; }}',
        f'{B} .sheet-pw-hint {{ display: none !important; }}',
        f'{B} .sheet-pw-row > label > span {{ display: inline !important; margin: 0 !important; }}',
        f'{B} .sheet-pw-row > label {{ flex-direction: row !important; }}',
        f'{B} .sheet-pw-row > b {{ flex: 0 0 auto !important; margin: 0 !important; }}',
        f'{B} .sheet-pw-row2 {{ gap: 4px 10px !important; }}',
        f'{B} label.sheet-pw-auto.sheet-switch > input {{ position: absolute !important; opacity: 0 !important; width: 1px !important; height: 1px !important; margin: 0 !important; }}',
        f'{B} label.sheet-pw-auto.sheet-switch > .sheet-sw-track {{ display: inline-block !important; position: relative !important; width: 28px !important; height: 14px !important; border-radius: 7px !important; background: #666 !important; margin-right: 5px !important; }}',
        f'{B} label.sheet-pw-auto.sheet-switch > .sheet-sw-track::after {{ content: ""; position: absolute; left: 2px; top: 2px; width: 10px; height: 10px; border-radius: 50%; background: #fff; transition: left .15s; }}',
        f'{B} label.sheet-pw-auto.sheet-switch > input:checked + .sheet-sw-track {{ background: {G} !important; }}',
        f'{B} label.sheet-pw-auto.sheet-switch > input:checked + .sheet-sw-track::after {{ left: 16px; }}',
        f'{B} label.sheet-pw-auto.sheet-switch > .sheet-sw-lbl {{ display: inline !important; font-size: 11px !important; text-transform: none !important; }}',
    ]) + '\n'
    return h, c


def fullheal(h, c):
    h = h.replace('<label class="sheet-hb-full" title="Full Heal toggle: while lit, a heal button clears ALL damage of that type. Click again to turn off.">', '<label class="sheet-hb-full" title="Full Heal">', 1)
    h = h.replace('<span>&#10010; Full</span></label>', '<span>Full</span></label>', 1)
    F = f'{P} .sheet-heal-row > label.sheet-hb-full'
    c += '\n'.join([
        f'{P} .sheet-heal-row {{ display: flex !important; flex-wrap: nowrap !important; align-items: center !important; justify-content: center !important; gap: 6px !important; }}',
        f'{F} {{ position: relative !important; display: inline-flex !important; align-items: center !important; justify-content: center !important; flex: 0 0 auto !important; '
        f'width: auto !important; min-width: 0 !important; max-width: 48px !important; height: 16px !important; padding: 0 6px !important; margin: 0 !important; '
        f'border-radius: 8px !important; border: 1px solid #777 !important; background: #2a2a2a !important; color: #ccc !important; font: bold 10px/14px Arial, sans-serif !important; box-shadow: none !important; overflow: hidden; }}',
        f'{F} > input.sheet-fh-cb {{ position: absolute !important; left: 0 !important; top: 0 !important; width: 100% !important; height: 100% !important; max-width: 100% !important; margin: 0 !important; opacity: 0 !important; }}',
        f'{F}:has(> input.sheet-fh-cb:checked) {{ background: {G} !important; border-color: {G} !important; color: #fff !important; box-shadow: 0 0 4px {G} !important; }}',
    ]) + '\n'
    return h, c


def warriors_hide(h, c):
    """W:tF 2E p.117 Full Moon Gift (Rahu), Purity 2 facet: permanently add Purity to Health."""
    a = 'getAttrs(["stamina","stamina_boost","form_size","resistance","base_size","giant","small_framed","sheettype","entity","bonus_health"], function(v) {'
    assert h.count(a) == 1
    h = h.replace(a, a.replace('"bonus_health"]', '"bonus_health","auspice","renown_purity"]'), 1)
    b = '+ Number(v.base_size) + Number(v.giant) - Number(v.small_framed) + Number(v.bonus_health);'
    i = h.index('health = Number(v.stamina) + (Number(v.stamina_boost) || 0) + (Number(v.form_size) || 0) ' + b)
    j = i + len('health = Number(v.stamina) + (Number(v.stamina_boost) || 0) + (Number(v.form_size) || 0) ' + b)
    h = h[:j - 1] + ' + ((v.sheettype === "werewolf2" && /rahu/i.test(v.auspice || "") && (Number(v.renown_purity) || 0) >= 2) ? Number(v.renown_purity) : 0);' + h[j:]
    k = h.index('var updateHealth = function()')
    h = h[:k] + 'on("change:auspice change:renown_purity", () => updateHealth());\n        ' + h[k:]
    h = h.replace("{{f_short=Permanently add Purity to Health}}", "{{f_short=Permanently add Purity to Health (applied to the Health track automatically)}}", 1)
    return h, c


def pills(h, c):
    S = (f'{P} .sheet-diceroller-options button.sheet-toggle, {P} .sheet-midtabs button.sheet-midtab-btn, {P} button.sheet-quick, {P} button.sheet-quick span')
    c += '\n'.join([
        f'{S} {{ font-family: "Sorts Mill Goudy", "Goudy Old Style", Garamond, Georgia, serif !important; font-size: 13px !important; font-weight: 700 !important; text-transform: none !important; font-variant: normal !important; letter-spacing: normal !important; }}',
        f'{P} .sheet-diceroller-options button.sheet-toggle, {P} .sheet-midtabs button.sheet-midtab-btn, {P} button.sheet-quick {{ padding: 3px 11px !important; min-height: 23px !important; line-height: 16px !important; white-space: nowrap !important; }}',
        f'{P} .sheet-diceroller-options, {P} .sheet-midtabs {{ flex-wrap: wrap !important; row-gap: 4px !important; justify-content: center !important; }}',
    ]) + '\n'
    return h, c


def apply(h, c):
    for f in (powers, fullheal, warriors_hide, pills, wolftabs, giftrows, midaudit, merits, tooltips, beats, rituals, splitgifts, cardfix, giftgrid, r16, r16css, r22, r24, r26, r27, r28, r29, r31):
        h, c = f(h, c)
    return h, c
from r15b import wolftabs, midaudit, merits, tooltips, giftrows, beats, rituals, splitgifts, cardfix, giftgrid, r16, r16css, r22, r24, r26, r27, r28, r29, r31  # noqa: E402
