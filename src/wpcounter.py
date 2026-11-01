"""Willpower as a numeric counter (current / max, -/+ only). Every Willpower spend uses attr_willpower_cur."""
import re
BOX = 'Array.from({length: 20}, (_, i) => `willpower_box${i + 1}`)'
def apply(h, c):
    a = '<div class="sheet-subheader" data-i18n="willpower" title="@{willpower_calc}">Willpower</div>'
    assert h.count(a) == 1, h.count(a)
    i = h.index(a) + len(a); k = h.index('<div class="sheet-checkboxes">', i); assert k - i < 40
    depth = 0
    for m in re.finditer(r'<div\b|</div>', h[k:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0: e = k + m.end(); break
    old = h[k:e]
    keep = ''.join(re.findall(r'<input type="hidden" name="attr_willpower(?:_box\d+)?"[^>]*/>', old))
    ctr = ('<div class="sheet-checkboxes sheet-wp-old">' + keep + '</div>'
           '<div class="sheet-wp-ctr sheet-res-ctr"><button type="action" class="sheet-res-btn" name="act_wp_dec" title="Spend 1 Willpower">&minus;</button>'
           '<input type="number" readonly="readonly" tabindex="-1" class="sheet-res-cur sheet-wp-cur" name="attr_willpower_cur" value="0" title="Current Willpower: use the - and + buttons" />'
           '<span class="sheet-res-sep">/</span><span class="sheet-res-max" name="attr_willpower" title="@{willpower_calc}"></span>'
           '<button type="action" class="sheet-res-btn" name="act_wp_inc" title="Regain 1 Willpower (capped at max)">+</button></div>')
    h = h[:k] + ctr + h[e:]
    s0 = h.count('willpower_box')
    # powers / merits activation cost
    h = h.replace('"willpower", ...' + BOX.replace('Array.from', 'Array.from') + ']', '"willpower", "willpower_cur"]')
    h = h.replace('const max = parseInt(v.willpower) || 0; let free = 0; for (let i = 1; i <= max; i++) if (!["1", "on"].includes(v[`willpower_box${i}`])) free++;',
                  'const max = parseInt(v.willpower) || 0; const free = Math.max(0, Math.min(max, parseInt(v.willpower_cur) || 0));')
    h = h.replace('for (let i = 1; i <= max && left > 0; i++) { if (!["1", "on"].includes(v[`willpower_box${i}`])) { u[`willpower_box${i}`] = "1"; left--; } }',
                  'if (left) u.willpower_cur = free - left;')
    # Willpower reroll
    h = h.replace('"rr_used", "willpower"].concat(' + BOX + ')', '"rr_used", "willpower", "willpower_cur"]')
    h = h.replace('for (let i = 1; i <= max; i++) if (!["1", "on"].includes(v[`willpower_box${i}`])) { free++; if (!first) first = i; }',
                  'free = Math.max(0, Math.min(max, parseInt(v.willpower_cur, 10) || 0));')
    h = h.replace('setAttrs({[`willpower_box${first}`]: "1", rr_used: v.rr_last_id});', 'setAttrs({willpower_cur: free - 1, rr_used: v.rr_last_id});')
    # Spend 1 WP (+3) toggle: deduct on the roll, refuse at 0
    old_rr = 'const rrRun = (mac, isRe) => startRoll(mac + (isRe ? "" : rrTag), (r) => {'
    assert h.count(old_rr) == 1
    h = h.replace(old_rr, '''const rrRun = (mac, isRe) => { if (isRe || !/wp_dice/.test(mac)) return rrRun0(mac, isRe);
            getAttrs(["wp_spend", "willpower", "willpower_cur"], (v) => { if (v.wp_spend !== "1") return rrRun0(mac, isRe);
                const cur = Math.max(0, parseInt(v.willpower_cur, 10) || 0), max = parseInt(v.willpower, 10) || 0;
                if (cur <= 0) return startRoll("&{template:cofd-entry} {{charname=@{character_name}}} {{kind=Willpower}} {{name=No Willpower left}} {{f_short=WP 0/" + max + ": untick Spend 1 WP or regain Willpower first.}}", r => finishRoll(r.rollId));
                setAttrs({willpower_cur: cur - 1});
                rrRun0(mac + " {{wpst=Spent 1 Willpower (+3 dice). Left: WP " + (cur - 1) + "/" + max + "}}", isRe); }); };
        const rrRun0 = (mac, isRe) => startRoll(mac + (isRe ? "" : rrTag), (r) => {''')
    left = re.findall(r'.{60}willpower_box\$\{.{60}', h[h.find('<script'):])
    js = r'''
        // Willpower counter: -/+ clamp 0..max; max follows Resolve + Composure; one-time migration from the old boxes
        const wpStep = (d) => getAttrs(["willpower", "willpower_cur"], v => { const m = parseInt(v.willpower, 10) || 0;
            setAttrs({willpower_cur: Math.max(0, Math.min(m, (parseInt(v.willpower_cur, 10) || 0) + d))}); });
        on("clicked:wp_dec", () => wpStep(-1)); on("clicked:wp_inc", () => wpStep(1));
        on("change:willpower", (ev) => getAttrs(["willpower", "willpower_cur", "wp_mig"], v => { if (v.wp_mig !== "1") return wpMig();
            const m = parseInt(v.willpower, 10) || 0, c = parseInt(v.willpower_cur, 10) || 0;
            const was = parseInt(ev.previousValue, 10); const nc = (!isNaN(was) && c === was) ? m : Math.min(c, m);
            if (nc !== c) setAttrs({willpower_cur: nc}); }));
        const wpMig = () => getAttrs(["willpower", "willpower_cur", "wp_mig"].concat(Array.from({length: 20}, (_, i) => `willpower_box${i + 1}`)), v => {
            if (v.wp_mig === "1") return; const m = parseInt(v.willpower, 10) || 0; if (!m) return; let used = 0;
            for (let i = 1; i <= Math.min(20, m); i++) if (["1", "on"].includes(v[`willpower_box${i}`])) used++;
            setAttrs({willpower_cur: Math.max(0, m - used), wp_mig: "1"}); });
        on("sheet:opened", wpMig);
'''
    k = h.rfind('</script>'); h = h[:k] + js + h[k:]
    c += ('\n/* r8 Willpower counter */\n.charsheet .sheet-wp-old { display: none !important; }\n'
          '.charsheet .sheet-wp-ctr { display: flex; justify-content: center; align-items: center; gap: 4px; margin: 2px 0; padding: 1px 2px; }\n'
          '.charsheet input.sheet-wp-cur { -webkit-appearance: textfield; -moz-appearance: textfield; appearance: textfield; pointer-events: none; }\n'
          '.charsheet input.sheet-wp-cur::-webkit-inner-spin-button, .charsheet input.sheet-wp-cur::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }\n')
    return h, c, left
