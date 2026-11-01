"""Repeating armor list (Rogue Trader / Pathfinder style cards). Only equipped rows feed the derived
armor_*0 attrs (kept as hidden attrs so every existing autocalc keeps working). Non-destructive migration
of the old single-armor line into the first row."""
import html as _h
def opts(rng, fmt=str): return ''.join(f'<option value="{v}">{fmt(v)}</option>' for v in rng)

def section(entry, T, ARMOR):
    pre = ''.join(f'<option value="{k}">{_h.escape(l)}</option>' for k, l, _ in ARMOR)
    hdr = ('<span class="ar-pills">'
           '<span class="ar-pill ar-g" title="General armor">G <span name="attr_ar_general"></span></span>'
           '<span class="ar-pill ar-b" title="Ballistic armor">B <span name="attr_ar_ballistic"></span></span>'
           '<span class="ar-pill ar-s" title="Strength requirement">Str <span name="attr_ar_str"></span></span>'
           '<span class="ar-pill ar-d" title="Defense / Speed penalty">Def <span name="attr_ar_def"></span> Spd <span name="attr_ar_spd"></span></span></span>'
           '<label class="ar-eq" title="Equipped: only equipped armor counts toward Armor, Defense and Speed">'
           '<input type="checkbox" name="attr_ar_equipped" value="1" checked /><span>Worn</span></label>')
    f = [('ar_preset', 'Preset (Hurt Locker)', 'select:' + ';'.join(f'{k}={l}' for k, l, _ in ARMOR)),
         ('ar_general', 'General', 'select:' + ';'.join(str(i) for i in range(0, 9))),
         ('ar_ballistic', 'Ballistic', 'select:' + ';'.join(str(i) for i in range(0, 9))),
         ('ar_str', 'Str req.', 'select:' + ';'.join(str(i) for i in range(0, 6))),
         ('ar_def', 'Defense penalty', 'select:' + ';'.join(str(-i) for i in range(0, 6))),
         ('ar_spd', 'Speed penalty', 'select:' + ';'.join(str(-i) for i in range(0, 6))),
         ('ar_coverage', 'Coverage', 'text'),
         ('ar_conceal', 'Concealment', 'select:=-;Concealed=Concealed (under clothes);Suspicious=Suspicious;Obvious=Obvious'),
         ('ar_helmet', 'Helmet', 'check'),
         ('ar_tags', 'Tags (comma-separated)', 'text'),
         ('notes', 'Notes', 'textarea')]
    s = entry('armor', 'armor', 'Armor', f, rating=None, pool=False, default_open=False, extra_header=hdr)
    s = s.replace('<input type="checkbox" class="entry-toggle"', '<input type="hidden" class="ar-eqf" name="attr_ar_equipped" value="1" /><input type="checkbox" class="entry-toggle"', 1)
    s = s.replace('<div class="entry-body">', '<div class="entry-body"><div class="ar-tagline"><span class="ar-tagpills" name="attr_ar_tagsum"></span></div>', 1)
    hid = ''.join(f'<input type="hidden" name="attr_armor_{k}0" value="{v}" />' for k, v in
                  [('general', 0), ('ballistic', 0), ('strength', 0), ('defense', 0), ('speed', 0), ('flag', 1)])
    hid += ''.join(f'<input type="hidden" name="attr_armor_{k}0" value="" />' for k in ('name', 'coverage', 'description', 'preset'))
    hid += '<input type="hidden" name="attr_armor_helmet0" value="0" /><input type="hidden" name="attr_armor_mig_v1" value="" />'
    hint = '<div class="ar-hint">Only worn armor counts. Several worn pieces: highest General and Ballistic, Str req. and penalties add up. Ballistic applies first against firearms.</div>'
    return '<div class="armor-list">' + s + hint + hid + '</div>'

JS = r'''
        // ===== repeating armor (src/armormod.py) =====
        const AR_F = ["ar_equipped","ar_general","ar_ballistic","ar_str","ar_def","ar_spd","ar_coverage","ar_helmet","name","ar_tags","ar_conceal","notes"];
        const arTotals = () => getSectionIDs("armor", ids => {
            getAttrs(ids.flatMap(id => AR_F.map(f => `repeating_armor_${id}_${f}`)), v => {
                let g = 0, b = 0, s = 0, d = 0, p = 0, helm = 0, names = [], cov = [], notes = [];
                const out = {};
                ids.forEach(id => {
                    const q = f => v[`repeating_armor_${id}_${f}`] || "";
                    const tags = q("ar_tags").split(",").map(t => t.trim()).filter(Boolean);
                    if (q("ar_conceal")) tags.unshift(q("ar_conceal"));
                    if (q("ar_helmet") === "1") tags.push("Helmet");
                    out[`repeating_armor_${id}_ar_tagsum`] = tags.join(" | ");
                    if (q("ar_equipped") !== "1") return;
                    g = Math.max(g, parseInt(q("ar_general")) || 0); b = Math.max(b, parseInt(q("ar_ballistic")) || 0);
                    s = Math.max(s, parseInt(q("ar_str")) || 0); d += parseInt(q("ar_def")) || 0; p += parseInt(q("ar_spd")) || 0;
                    if (q("ar_helmet") === "1") helm = 1; if (q("name")) names.push(q("name")); if (q("ar_coverage")) cov.push(q("ar_coverage"));
                    if (q("notes")) notes.push(q("notes"));
                });
                Object.assign(out, {armor_general0: g, armor_ballistic0: b, armor_strength0: s, armor_defense0: d, armor_speed0: p, armor_helmet0: helm,
                    armor_name0: names.join(" + "), armor_coverage0: cov.join("; "), armor_description0: notes.join(" / ")});
                setAttrs(out, {silent: true}, () => { if (typeof updateWeaponAttacks === "function") updateWeaponAttacks(); });
            });
        });
        on("change:repeating_armor:ar_preset", e => {
            const a = HL_ARMOR[e.newValue]; if (!a || e.sourceType !== "player") return;
            const p = "repeating_armor_";
            setAttrs({[p + "name"]: a[0], [p + "ar_general"]: a[1], [p + "ar_ballistic"]: a[2], [p + "ar_str"]: a[3], [p + "ar_def"]: a[4], [p + "ar_spd"]: a[5], [p + "ar_coverage"]: a[6]}, arTotals);
        });
        on("change:repeating_armor remove:repeating_armor", e => { if (!/ar_preset|ar_tagsum/.test(e.sourceAttribute || "")) arTotals(); });
        on("sheet:opened", () => getAttrs(["armor_mig_v1","armor_name0","armor_general0","armor_ballistic0","armor_strength0","armor_defense0","armor_speed0","armor_coverage0","armor_helmet0","armor_description0","armor_preset0"], v => {
            if (v.armor_mig_v1 === "1") return arTotals();
            getSectionIDs("armor", ids => {
                const has = v.armor_name0 || ["armor_general0","armor_ballistic0","armor_strength0","armor_defense0","armor_speed0"].some(k => parseInt(v[k]));
                const out = {armor_mig_v1: "1"};
                if (has && !ids.length) {
                    const id = generateRowID(), p = `repeating_armor_${id}_`;
                    Object.assign(out, {[p + "name"]: v.armor_name0 || "Armor", [p + "ar_general"]: v.armor_general0 || "0", [p + "ar_ballistic"]: v.armor_ballistic0 || "0",
                        [p + "ar_str"]: v.armor_strength0 || "0", [p + "ar_def"]: v.armor_defense0 || "0", [p + "ar_spd"]: v.armor_speed0 || "0",
                        [p + "ar_coverage"]: v.armor_coverage0 || "", [p + "ar_helmet"]: v.armor_helmet0 || "0", [p + "notes"]: v.armor_description0 || "",
                        [p + "ar_preset"]: v.armor_preset0 || "", [p + "ar_equipped"]: "1", [p + "show"]: "0"});
                }
                setAttrs(out, {silent: true}, arTotals);
            });
        }));
'''

CSS = r'''
.charsheet .sheet-armor-list { margin-top: 6px; }
.charsheet .sheet-entry-section.sheet-armor .sheet-entry-head { display: grid !important; grid-template-columns: minmax(0,1fr) auto auto; column-gap: 6px; align-items: center; height: auto !important; }
.charsheet .sheet-entry-section.sheet-armor .sheet-entry-head > button.sheet-entry-post { white-space: normal !important; overflow-wrap: break-word; }
.charsheet .sheet-ar-pills { display: flex; flex-wrap: wrap; gap: 3px; justify-content: flex-end; }
.charsheet .sheet-ar-pill { display: inline-block; font: bold 10px/14px Arial, sans-serif; padding: 0 6px; border: 1px solid var(--temp-dot, #aa5a1e); border-radius: 8px; white-space: nowrap; }
.charsheet .sheet-ar-pill.sheet-ar-g, .charsheet .sheet-ar-pill.sheet-ar-b { background: rgba(170,90,30,.18); }
.charsheet .sheet-ar-eq { display: flex !important; align-items: center; gap: 3px; margin: 0 !important; font: bold 10px Arial, sans-serif; white-space: nowrap; }
.charsheet .sheet-ar-eq input { width: auto !important; height: auto !important; margin: 0 !important; }
.charsheet input.sheet-ar-eqf[value="0"] ~ .sheet-entry-head .sheet-ar-pills { opacity: .55; text-decoration: line-through; }
.charsheet .sheet-ar-tagline { grid-column: 1 / -1; min-height: 0; }
.charsheet .sheet-ar-tagpills { font: italic 11px Arial, sans-serif; opacity: .85; }
.charsheet .sheet-ar-hint { font-size: 9px; font-style: italic; opacity: .7; padding: 2px 4px; }
.charsheet .sheet-darkmode .sheet-ar-pill { border-color: #e08a3c; color: #f0d8c0; }
'''
