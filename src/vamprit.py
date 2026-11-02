"""r9: Vampire Rituals tab, physical Discipline bonuses, pill-style middle tabs."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
TABS = ['merits', 'powers', 'rites', 'totem', 'devotions', 'frenzy', 'weapons', 'kuruth', 'rituals', 'gear']
ROLL = ('&amp;{template:cofd-entry} {{charname=@{character_name}}} {{gl_@{game_line}=1}} {{splat=@{game_line}}} {{kind=Ritual}} '
        '{{name=@{rit_name}}} {{f_category=@{rit_trad_name}}} {{f_level=@{rit_level}}} {{f_costs=@{rit_cost}}} {{f_pool=@{rit_pool_txt}}} '
        '{{f_description=@{rit_desc}}} {{roll=[[{((@{rit_pool}+?{@{modifiermacro}|0}+@{wound_penalty}+@{wp_dice}+@{cond_mod})@{rolltype_eff}')
PANE = ('<div class="sheet-midpane sheet-mp-rituals sheet-game-line sheet-vampire2"><div class="sheet-leon-page sheet-leon-pane">'
        '<div class="sheet-subheader"><span>Rituals</span></div>'
        '<div class="sheet-rit-help">Cruac: Manipulation + Occult + Cruac. Theban Sorcery: Intelligence + Academics + Theban Sorcery. '
        'Tradition dots are read from the Disciplines list (a Discipline named Cruac / Theban Sorcery).</div>'
        '<fieldset class="repeating_rituals"><div class="sheet-rit">'
        '<div class="sheet-rit-top">'
        '<input type="text" class="sheet-rit-name" name="attr_rit_name" placeholder="Ritual name" title="Ritual name" />'
        '<select name="attr_rit_trad" class="sheet-rit-trad" title="Tradition"><option value="cruac" selected>Cruac</option><option value="theban">Theban Sorcery</option></select>'
        '<select name="attr_rit_level" class="sheet-rit-lvl" title="Ritual level (dots)"><option value="1" selected>&#9679;</option><option value="2">&#9679;&#9679;</option>'
        '<option value="3">&#9679;&#9679;&#9679;</option><option value="4">&#9679;&#9679;&#9679;&#9679;</option><option value="5">&#9679;&#9679;&#9679;&#9679;&#9679;</option></select>'
        '<input type="hidden" name="attr_rit_trad_name" value="Cruac" /><input type="hidden" name="attr_rit_pool" value="0" />'
        '<span class="sheet-rit-pool" name="attr_rit_pool_txt" title="Dice pool (computed)"></span>'
        f'<button type="roll" class="sheet-rit-roll" name="roll_ritual" title="Roll this ritual" value="{ROLL}">Roll</button></div>'
        '<div class="sheet-rit-bot"><input type="text" class="sheet-rit-cost" name="attr_rit_cost" placeholder="Cost (e.g. 1 Vitae / 1 Willpower + sacrament)" title="Cost" />'
        '<textarea class="sheet-rit-desc" name="attr_rit_desc" rows="2" placeholder="Description / effect"></textarea></div>'
        '</div></fieldset></div></div>')
JS = r'''
        // ---- r9 Vampire: Discipline-derived bonuses (Vigor -> Strength, Resilience -> Stamina, Celerity -> Defense) + ritual pools
        const discDots = (cb) => getSectionIDs("repeating_disciplines", ids => getAttrs(["sheettype", ...ids.flatMap(i => [`repeating_disciplines_${i}_name`, `repeating_disciplines_${i}_rating`])], v => {
            const d = {vigor: 0, celerity: 0, resilience: 0, cruac: 0, theban: 0};
            ids.forEach(i => { const nm = (v[`repeating_disciplines_${i}_name`] || "").toLowerCase(), r = parseInt(v[`repeating_disciplines_${i}_rating`], 10) || 0;
                for (const k of Object.keys(d)) if (nm.indexOf(k === "vigor" ? "vigo" : k) >= 0) d[k] = Math.max(d[k], r); });
            cb(v.sheettype, d);
        }));
        const vampBoost = () => discDots((st, d) => {
            if (st !== "vampire2") { getAttrs(["disc_vamp"], w => { if (w.disc_vamp === "1") setAttrs({disc_vamp: "0", strength_boost: 0, stamina_boost: 0, disc_celerity: 0, strength_vb: "", stamina_vb: "", defense_vb: ""}); }); return; }
            setAttrs({disc_vamp: "1", strength_boost: d.vigor, stamina_boost: d.resilience, disc_celerity: d.celerity,
                strength_vb: d.vigor ? "+" + d.vigor : "", stamina_vb: d.resilience ? "+" + d.resilience : "", defense_vb: d.celerity ? "+" + d.celerity : "",
                disc_cruac: d.cruac, disc_theban: d.theban});
        });
        on("sheet:opened change:sheettype change:repeating_disciplines remove:repeating_disciplines", vampBoost);
        const ritUpd = () => getSectionIDs("repeating_rituals", ids => getAttrs(["manipulation_eff", "manipulation", "occult", "intelligence_eff", "intelligence", "academics", "disc_cruac", "disc_theban", ...ids.map(i => `repeating_rituals_${i}_rit_trad`)], v => {
            const n = k => parseInt(v[k], 10) || 0, e = k => (v[k + "_eff"] !== undefined && v[k + "_eff"] !== "") ? n(k + "_eff") : n(k), u = {};
            ids.forEach(i => { const p = `repeating_rituals_${i}_`, th = v[p + "rit_trad"] === "theban";
                const a = th ? ["Intelligence", e("intelligence"), "Academics", n("academics"), "Theban Sorcery", n("disc_theban")] : ["Manipulation", e("manipulation"), "Occult", n("occult"), "Cruac", n("disc_cruac")];
                u[p + "rit_pool"] = a[1] + a[3] + a[5]; u[p + "rit_trad_name"] = th ? "Theban Sorcery" : "Cruac";
                u[p + "rit_pool_txt"] = `${a[0]} ${a[1]} + ${a[2]} ${a[3]} + ${a[4]} ${a[5]} = ${a[1] + a[3] + a[5]}`; });
            setAttrs(u, {silent: true});
        }));
        on("sheet:opened change:repeating_rituals:rit_trad change:repeating_rituals remove:repeating_rituals change:manipulation change:manipulation_eff change:occult change:intelligence change:intelligence_eff change:academics change:disc_cruac change:disc_theban", ritUpd);
'''
def apply(h, c):
    # hidden attrs right after the sheet-type input
    m = re.search(r'<input type="hidden" class="sheet-type"[^>]*>', h)
    h = h[:m.end()] + ('<input type="hidden" name="attr_disc_vamp" value="0" /><input type="hidden" name="attr_disc_celerity" value="0" />'
                       '<input type="hidden" name="attr_disc_cruac" value="0" /><input type="hidden" name="attr_disc_theban" value="0" />') + h[m.end():]
    # +N badges on the Strength / Stamina labels and on Defense
    for a, t in (('strength', 'Vigor'), ('stamina', 'Resilience')):
        old = f'<button type="action" class="sheet-toggle" name="act_{a}" data-i18n="{a}" title="{a.title()}">{a.title()}</button>'
        assert old in h, a
        h = h.replace(old, old + f'<span class="sheet-vb" name="attr_{a}_vb" title="Vampire: {t} dots added to {a.title()} (effective value used in pools and derived traits)"></span>', 1)
    old = '<input type="number" name="attr_defense" value="@{defense_base}+@{defense_penalty}" disabled="disabled" title="@{defense_calc}"/>'
    assert old in h
    h = h.replace(old, '<input type="number" name="attr_defense" value="@{defense_base}+@{defense_penalty}+@{disc_celerity}" disabled="disabled" title="@{defense_calc}"/>'
                  '<span class="sheet-vb sheet-vb-def" name="attr_defense_vb" title="Vampire: Celerity dots added to Defense"></span>', 1)
    # calc tooltips show the math
    o = 'u.defense_calc = `Defense = min(Wits ${n("wits")}, Dex ${n("dexterity")}) + Athletics ${n("athletics")} = ${n("defense_base")}`'
    assert o in h
    h = h.replace('const def = n("defense_base") + n("defense_penalty");', 'const def = n("defense_base") + n("defense_penalty") + n("disc_celerity");', 1)
    h = h.replace(o, o + ' + (n("disc_celerity") ? ` + Celerity ${n("disc_celerity")}` : "")', 1)
    o = 'u.health_calc = `Health = Size ${size} + Stamina ${n("stamina")} = ${size + n("stamina")}`'
    assert o in h
    h = h.replace(o, 'u.health_calc = `Health = Size ${size} + Stamina ${n("stamina") + n("stamina_boost")}` + (v.sheettype === "vampire2" && n("stamina_boost") ? ` (${n("stamina")} + Resilience ${n("stamina_boost")})` : "") + ` = ${size + n("stamina") + n("stamina_boost")}`', 1)
    h = h.replace('const CALC_IN = ["strength","dexterity","stamina",', 'const CALC_IN = ["strength","dexterity","stamina","stamina_boost","strength_boost","disc_celerity",', 1)
    h = h.replace('u.willpower_calc =', 'u.strength_vcalc = v.sheettype === "vampire2" && n("strength_boost") ? `Strength = ${n("strength")} + Vigor ${n("strength_boost")} = ${n("strength") + n("strength_boost")}` : "Strength";\n            u.stamina_vcalc = v.sheettype === "vampire2" && n("stamina_boost") ? `Stamina = ${n("stamina")} + Resilience ${n("stamina_boost")} = ${n("stamina") + n("stamina_boost")}` : "Stamina";\n            u.willpower_calc =', 1)
    for a in ('strength', 'stamina'):
        h = h.replace(f'name="act_{a}" data-i18n="{a}" title="{a.title()}"', f'name="act_{a}" data-i18n="{a}" title="@{{{a}_vcalc}}"', 1)
    assert 'CALC_IN.map' in h or 'CALC_IN' in h
    # calc triggers on boost changes
    JS2 = JS + '        on("change:stamina_boost change:strength_boost change:disc_celerity", () => { if (typeof calcUpd === "function") calcUpd(); });\n'
    # rituals tab + pane
    b = re.search(r'<button type="action" class="sheet-midtab-btn sheet-mt-kuruth[^>]*>.*?</button>', h, re.S)
    h = h[:b.end()] + '<button type="action" class="sheet-midtab-btn sheet-mt-rituals sheet-game-line sheet-vampire2" name="act_midtab_rituals" title="Cruac and Theban Sorcery rituals">Rituals</button>' + h[b.end():]
    k = h.index('<div class="sheet-midpane sheet-mp-kuruth">'); h = h[:k] + PANE + h[k:]
    h = h.replace('["merits","powers","weapons","kuruth","gear"].forEach', '["merits","powers","weapons","kuruth","rituals","gear"].forEach', 1)
    i = h.rfind('</script>'); h = h[:i] + JS2 + h[i:]
    # CSS
    c += ('\n.charsheet input.sheet-midtab[value="rituals"] ~ .sheet-midpane.sheet-mp-rituals { display: block !important; }\n'
          '.charsheet span.sheet-vb { display: inline-block; margin-left: 3px; padding: 0 4px; border-radius: 8px; background: #8e1616; color: #fff; font: bold 10px/14px Arial, sans-serif; vertical-align: middle; }\n'
          '.charsheet span.sheet-vb:empty { display: none !important; }\n'
          '.charsheet .sheet-rit-help { font-size: 11px; opacity: .8; margin: 2px 0 6px; }\n'
          '.charsheet .repeating_rituals .sheet-rit { border: 1px solid rgba(160,130,90,.4); border-radius: 6px; padding: 4px 6px; margin-bottom: 6px; }\n'
          '.charsheet .sheet-rit-top { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 6px; }\n'
          '.charsheet.charsheet .sheet-rit-top input.sheet-rit-name { flex: 1 1 160px; min-width: 120px; width: auto !important; }\n'
          '.charsheet.charsheet .sheet-rit-top select { width: auto !important; min-width: 0; height: 22px; padding: 0 2px; font-size: 12px; }\n'
          '.charsheet .sheet-rit-pool { font-size: 11px; opacity: .85; flex: 1 1 100%; order: 5; }\n'
          '.charsheet.charsheet button.sheet-rit-roll { padding: 1px 10px !important; height: auto !important; width: auto !important; border-radius: 10px !important; }\n'
          '.charsheet .sheet-rit-bot { display: flex; flex-direction: column; gap: 3px; margin-top: 3px; }\n'
          '.charsheet.charsheet .sheet-rit-bot input, .charsheet.charsheet .sheet-rit-bot textarea { width: 100% !important; box-sizing: border-box; }\n')
    # pill-style middle tabs, active pill in splat accent
    P = '.charsheet.charsheet.charsheet .sheet-midtabs'
    c += (f'{P} {{ display: flex !important; flex-wrap: wrap; justify-content: center; gap: 6px !important; border-bottom: 0 !important; margin: 4px 0 8px !important; }}\n'
          f'{P} button.sheet-midtab-btn.sheet-midtab-btn, .charsheet.charsheet.charsheet input.sheet-type ~ * .sheet-midtabs button[type=action].sheet-midtab-btn.sheet-midtab-btn {{ margin: 0 !important; padding: 3px 12px !important; border: 2px solid rgba(160,130,90,.7) !important; border-radius: 999px !important; '
          'background: rgba(244,240,232,.92) !important; color: #222 !important; opacity: 1 !important; font: bold 12px/16px Arial, sans-serif !important; }\n')
    c += f'{P} button.sheet-midtab-btn span {{ color: inherit !important; text-shadow: none !important; font: inherit !important; }}\n'
    cols = json.load(open(os.path.join(HERE, 'splat_colors.json')))
    import extras
    sels = []
    for k, col in cols.items():
        for t in extras.TYPE_OF.get(k, []):
            s = ', '.join(f'.charsheet.charsheet.charsheet input.sheet-type[value="{t}"] ~ * input.sheet-midtab[value="{tb}"] + .sheet-midtabs button.sheet-midtab-btn.sheet-mt-{tb}' for tb in TABS)
            c += s + f' {{ background: #000 !important; border-color: {col} !important; color: #fff !important; box-shadow: 0 0 6px {col} !important; }}\n'
    c += (', '.join(f'{P[:-len(" .sheet-midtabs")]} input.sheet-midtab[value="{tb}"] + .sheet-midtabs button.sheet-midtab-btn.sheet-mt-{tb}' for tb in TABS)
          + ' { box-shadow: 0 0 6px rgba(0,0,0,.35); }\n')
    return h, c
