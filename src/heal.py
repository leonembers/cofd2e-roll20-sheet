"""Heal B / L / A buttons under the Health track: remove the rightmost box of one damage type and re-sort (A, L, B from the left)."""
import re
def apply(h, c):
    a = '<div class="sheet-healthboxes">'; assert h.count(a) == 1
    i = h.index(a); depth = 0; j = i
    for m in re.finditer(r'<div\b|</div>', h[i:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0: j = i + m.end(); break
    B = lambda n, k, t: f'<button type="action" class="sheet-hb sheet-hb-{k}" name="act_{n}" title="{t}"></button>'
    row = ('<div class="sheet-heal-row">'
           '<span class="sheet-hb-grp sheet-hb-dmg" title="Take damage"><span class="sheet-hb-lbl">+</span>'
           + B('dmg_b', 'b', 'Take 1 bashing (upgrades if the track is full)') + B('dmg_l', 'l', 'Take 1 lethal (upgrades if the track is full)') + B('dmg_a', 'a', 'Take 1 aggravated (upgrades if the track is full)') +
           '</span><span class="sheet-hb-grp sheet-hb-heal" title="Heal damage"><span class="sheet-hb-lbl">-</span>'
           + B('heal_b', 'b', 'Heal 1 bashing') + B('heal_l', 'l', 'Heal 1 lethal') + B('heal_a', 'a', 'Heal 1 aggravated') + '</span></div>')
    h = h[:j] + row + h[j:]
    js = r'''
        // Heal buttons: 1 = bashing, 2 = lethal, 3 = aggravated
        const healOne = (lvl) => { const ks = [...Array(16).keys()].map(i => `healthbox_${i + 1}`);
            getAttrs(["health"].concat(ks), v => { const n = Math.min(16, parseInt(v.health) || 0);
                const vals = ks.slice(0, n).map(k => parseInt(v[k]) || 0);
                const at = vals.indexOf(lvl); if (at < 0) return;
                vals.splice(at, 1); vals.push(0); vals.sort((x, y) => y - x);
                const u = {}; vals.forEach((x, i) => { if ((parseInt(v[ks[i]]) || 0) !== x) u[ks[i]] = x; }); setAttrs(u); }); };
        const dmgOne = (lvl) => { const ks = [...Array(16).keys()].map(i => `healthbox_${i + 1}`);
            getAttrs(["health"].concat(ks), v => { const n = Math.min(16, parseInt(v.health) || 0); if (!n) return;
                const vals = ks.slice(0, n).map(k => parseInt(v[k]) || 0).sort((x, y) => y - x);
                const empty = vals.indexOf(0);
                if (empty >= 0) vals[empty] = lvl;
                else if (lvl === 3) { const i = vals.findIndex(x => x < 3); if (i >= 0) vals[i] = 3; }
                else { let i = vals.indexOf(1); if (i >= 0) vals[i] = 2; else { i = vals.indexOf(2); if (i >= 0) vals[i] = 3; } }
                vals.sort((x, y) => y - x);
                const u = {}; vals.forEach((x, i) => { if ((parseInt(v[ks[i]]) || 0) !== x) u[ks[i]] = x; }); setAttrs(u); }); };
        on("clicked:dmg_b", () => dmgOne(1)); on("clicked:dmg_l", () => dmgOne(2)); on("clicked:dmg_a", () => dmgOne(3));
        on("clicked:heal_b", () => healOne(1)); on("clicked:heal_l", () => healOne(2)); on("clicked:heal_a", () => healOne(3));
'''
    k = h.rfind('</script>'); h = h[:k] + js + h[k:]
    g = lambda d: 'linear-gradient(%s, rgba(0,0,0,0) calc(50%% - 1px), currentColor 50%%, rgba(0,0,0,0) calc(50%% + 1px))' % d
    sym = {'b': g('to top left'), 'l': g('to top left') + ', ' + g('to top right'),
           'a': ', '.join([g('to top left'), g('to top right'), g('to right'), g('to bottom')])}
    c += '\n/* r8 health damage / heal buttons: same marks as the track boxes */\n'
    c += '.charsheet .sheet-heal-row { display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 3px 10px; margin: 3px 0 2px; padding: 1px 2px; }\n'
    c += '.charsheet .sheet-heal-row .sheet-hb-grp { display: inline-flex; align-items: center; gap: 3px; }\n'
    c += '.charsheet .sheet-heal-row .sheet-hb-lbl { font-weight: bold; font-size: 13px; line-height: 14px; width: 8px; text-align: center; }\n'
    c += '.charsheet .sheet-heal-row .sheet-hb-dmg { color: #d0453a; }\n.charsheet .sheet-heal-row .sheet-hb-heal { color: #4fb36a; }\n'
    c += ('.charsheet.charsheet.charsheet.charsheet div.sheet-heal-row span.sheet-hb-grp > button.sheet-hb.sheet-hb { width: 16px !important; height: 16px !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important; '
          'border: 1px solid currentColor !important; border-radius: 2px !important; color: #4fb36a !important; border-color: #4fb36a !important; background-color: rgba(0,0,0,.25) !important; '
          'background-repeat: no-repeat !important; background-size: 100% 100% !important; cursor: pointer; box-sizing: border-box !important; }\n')
    c += '.charsheet.charsheet.charsheet.charsheet div.sheet-heal-row span.sheet-hb-dmg > button.sheet-hb.sheet-hb.sheet-hb { background-color: #d0453a !important; color: #1a1a1a !important; border-color: #d0453a !important; }\n'
    c += '.charsheet.charsheet.charsheet.charsheet div.sheet-heal-row span.sheet-hb-grp > button.sheet-hb.sheet-hb:hover { filter: brightness(1.25); }\n'
    c += '.charsheet.charsheet.charsheet.charsheet div.sheet-heal-row span.sheet-hb-grp > button.sheet-hb.sheet-hb::before, .charsheet.charsheet.charsheet.charsheet div.sheet-heal-row span.sheet-hb-grp > button.sheet-hb.sheet-hb::after { content: none !important; }\n'
    for k, v in sym.items():
        c += f'.charsheet.charsheet.charsheet.charsheet div.sheet-heal-row span.sheet-hb-grp > button.sheet-hb.sheet-hb.sheet-hb-{k} {{ background-image: {v} !important; }}\n'
    return h, c
