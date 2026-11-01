"""Hover tooltips for calculated traits: worker keeps hidden *_calc attrs; elements carry title="@{x_calc}"."""
import re
JS = r'''
        // ---- calculated-trait tooltips (live values) ----
        const CALC_IN = ["strength","dexterity","stamina","wits","composure","resolve","athletics","base_size","giant","small_framed","form_size","species_factor","speed_base","speed_penalty","fleet_of_foot","form_speed_extra",
            "defense_base","defense_penalty","initiative_base","initiative_penalty","fast_reflexes","form_init_extra","form_perception","form","iron_stamina","health","willpower","vitae_max","sheettype","xp_earned","xp_spent","xpalt_earned","xpalt_spent","balistic_armor","general_armor"];
        const calcUpd = () => getAttrs(CALC_IN, (v) => {
            const n = k => parseInt(v[k], 10) || 0, sg = x => (x < 0 ? "- " + (-x) : "+ " + x);
            const form = (v.form || "hishu"); const fl = form.charAt(0).toUpperCase() + form.slice(1);
            const size = n("base_size") + n("giant") - n("small_framed") + n("form_size");
            const parts = (arr) => arr.filter(([l, x, keep]) => keep || x).map(([l, x], i) => (i ? sg(x) + " " : x + " ").replace(/^(\S+) $/, "$1 ") + "").join("");
            const fmt = (name, arr, total) => name + " = " + arr.filter(([l, x, keep]) => keep || x).map(([l, x], i) => (i ? (x < 0 ? " - " : " + ") : "") + l + " " + Math.abs(x)).join("") + " = " + total;
            const u = {};
            u.size_calc = fmt("Size", [["Base", n("base_size"), 1], ["Giant", n("giant")], ["Small-Framed", -n("small_framed")], [fl + " form", n("form_size")]], size);
            const def = n("defense_base") + n("defense_penalty");
            u.defense_calc = `Defense = min(Wits ${n("wits")}, Dex ${n("dexterity")}) + Athletics ${n("athletics")} = ${n("defense_base")}` + (n("defense_penalty") ? ` ${sg(n("defense_penalty"))} armor` : "") + ` = ${def}` + (form !== "hishu" ? ` (${fl} form mods included in Wits/Dex)` : "");
            const spd = n("species_factor") + n("speed_base") + n("speed_penalty") + n("fleet_of_foot") + n("form_speed_extra") + n("form_size");
            u.speed_calc = fmt("Speed", [["Str + Dex", n("speed_base"), 1], ["Species", n("species_factor"), 1], ["Armor", n("speed_penalty")], ["Fleet of Foot", n("fleet_of_foot")], [fl + " form", n("form_speed_extra") + n("form_size")]], spd);
            const ini = n("initiative_base") + n("initiative_penalty") + n("fast_reflexes") + n("form_init_extra");
            u.initiative_calc = fmt("Initiative", [["Dex + Composure", n("initiative_base"), 1], ["Armor", n("initiative_penalty")], ["Fast Reflexes", n("fast_reflexes")], [fl + " form", n("form_init_extra")]], ini);
            u.health_calc = `Health = Size ${size} + Stamina ${n("stamina")} = ${size + n("stamina")}` + (n("iron_stamina") ? ` (Iron Stamina ${n("iron_stamina")}: offsets wound penalties)` : "");
            u.willpower_calc = `Willpower max = Resolve ${n("resolve")} + Composure ${n("composure")} = ${n("resolve") + n("composure")}`;
            u.perception_calc = fmt("Perception", [["Wits", n("wits"), 1], ["Composure", n("composure"), 1], [fl + " form", n("form_perception")]], n("wits") + n("composure") + n("form_perception"));
            u.armor_calc = `Armor = General ${n("general_armor")} / Ballistic ${n("balistic_armor")} (equipped armor rows)`;
            u.experience_calc = `Available = Earned ${n("xp_earned")} - Spent ${n("xp_spent")} = ${n("xp_earned") - n("xp_spent")}`;
            u.experience_alt_calc = `Available = Earned ${n("xpalt_earned")} - Spent ${n("xpalt_spent")} = ${n("xpalt_earned") - n("xpalt_spent")}`;
            u.vitae_max_calc = `Maximum ${n("vitae_max")} (from the power stat: Blood Potency / Primal Urge / Gnosis ..., or 10 + power stat)`;
            setAttrs(u, {silent: true});
        });
        on("sheet:opened " + CALC_IN.map(k => "change:" + k).join(" "), calcUpd);
'''
def apply(h):
    def tip(h, pat, attr, n=1):
        h2, k = re.subn(pat, lambda m: m.group(0)[:-1].rstrip('/').rstrip() + f' title="@{{{attr}}}"' + ('/>' if m.group(0).endswith('/>') else '>'), h, count=n)
        assert k, pat
        return h2
    for a in ['size', 'speed', 'defense', 'initiative']:
        h = tip(h, r'<input type="number" name="attr_%s" value="[^"]*" disabled="disabled"\s*/>' % a, a + '_calc')
    h = tip(h, r'<input type="number" name="attr_balistic_armor_display"[^>]*/>', 'armor_calc')
    h = tip(h, r'<span class="sheet-corporeal" data-i18n="health">', 'health_calc')
    h = tip(h, r'<div class="sheet-subheader" data-i18n="willpower">', 'willpower_calc')
    h = tip(h, r'<span class="sheet-xp-avail" name="attr_experience">', 'experience_calc')
    h = tip(h, r'<span class="sheet-xp-avail" name="attr_experience_alt">', 'experience_alt_calc')
    h = h.replace('<span class="sheet-res-max" name="attr_vitae_max" title="Maximum (from Blood Potency, Primal Urge, Gnosis, etc.)">', '<span class="sheet-res-max" name="attr_vitae_max" title="@{vitae_max_calc}">')
    hid = ''.join(f'<input type="hidden" name="attr_{a}_calc" value="" />' for a in ['size','speed','defense','initiative','armor','health','willpower','perception','experience','experience_alt','vitae_max'])
    h = h.replace('<div class="sheet-rollcontainer">', hid + '<div class="sheet-rollcontainer">', 1)
    i = h.rfind('</script>'); h = h[:i] + JS + h[i:]
    return h
