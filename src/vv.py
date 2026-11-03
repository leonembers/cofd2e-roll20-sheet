"""r12: header Virtue/Vice equivalents (Virtue/Vice, Mask/Dirge, Blood/Bone, Needle/Thread, Root/Bloom...) are free text,
each with a small button that opens a description popup (Conditions/Tilts overlay style). Replaces the r9 drop-downs.
Descriptions reuse blood_desc (Virtue slot) and bone_desc (Vice slot), the attrs the Werewolf Blood/Bone entries already use.
Old Virtue_pick / Vice_pick selections are migrated into the text once."""
import re
SLOTS = (('Virtue', 'virtue', 'blood_desc'), ('Vice', 'vice', 'bone_desc'))

def apply(h, c):
    wins = []
    for attr, k, desc in SLOTS:
        old = f'<input type="text" name="attr_{attr}">'
        assert h.count(old) == 1, attr
        i = h.find(old)
        ls = h.rfind('<div class="sheet-input-label">', 0, i); le = h.find('</div>', ls)
        lab = h[ls + len('<div class="sheet-input-label">'):le].replace(':</span>', '</span>')
        lab = re.sub(r'\s+', ' ', lab).strip()
        new = (f'<span class="sheet-vv"><input type="text" class="sheet-vv-txt" name="attr_{attr}" />'
               f'<label class="sheet-vv-ib" title="Open the description window"><input type="checkbox" class="sheet-ovf" name="attr_ov_{k}" value="1" />&#9998;</label></span>')
        h = h.replace(old, new, 1)
        wins.append(f'<div class="sheet-ovwin sheet-ov-{k}"><input type="checkbox" class="sheet-ov-x" name="attr_ov_{k}" value="1" title="Close" />'
                    f'<div class="sheet-subheader sheet-vv-wt">{lab} <span class="sheet-vv-wn" name="attr_{attr}"></span></div>'
                    f'<input type="text" class="sheet-vv-wname" name="attr_{attr}" placeholder="Name" />'
                    f'<textarea class="sheet-vv-desc" name="attr_{desc}" placeholder="Description: what it means, when it applies, how it restores Willpower"></textarea></div>')
    a = '<div class="sheet-ovwin sheet-ov-cond">'
    assert h.count(a) == 1
    h = h.replace(a, ''.join(wins) + a, 1)
    js = r'''        on("sheet:opened", () => getAttrs(["vv_mig_v1", "Virtue", "Vice", "Virtue_pick", "Vice_pick"], v => {
            if (v.vv_mig_v1 === "1") return; const u = {vv_mig_v1: "1"};
            ["Virtue", "Vice"].forEach(a => { const p = (v[a + "_pick"] || "").trim(); if (!(v[a] || "").trim() && p && p !== "custom") u[a] = p; });
            setAttrs(u, {silent: true});
        }));
'''
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    P = '.charsheet.charsheet.charsheet'
    c += '\n'.join([
        f'{P} .sheet-vv {{ display: flex; gap: 3px; align-items: center; min-width: 0; }}',
        f'{P} .sheet-vv input.sheet-vv-txt {{ flex: 1 1 auto; min-width: 0; width: auto !important; }}',
        f'{P} label.sheet-vv-ib {{ flex: 0 0 18px; width: 18px; height: 18px; line-height: 18px; text-align: center; font-size: 12px; cursor: pointer; border: 1px solid var(--color-game-line, #b4743a); border-radius: 4px; opacity: .85; margin: 0; padding: 0; }}',
        f'{P} label.sheet-vv-ib:hover {{ opacity: 1; }}',
        f'{P} label.sheet-vv-ib > input.sheet-ovf {{ display: none !important; }}',
        f'{P} label.sheet-vv-ib:has(input.sheet-ovf:checked) {{ background: var(--color-game-line, #b4743a); color: #fff; }}',
        '.charsheet:has(input.sheet-ovf[name="attr_ov_virtue"]:checked) .sheet-ovwin.sheet-ov-virtue, .charsheet:has(input.sheet-ovf[name="attr_ov_vice"]:checked) .sheet-ovwin.sheet-ov-vice { display: block !important; }',
        f'{P} .sheet-ovwin.sheet-ov-virtue, {P} .sheet-ovwin.sheet-ov-vice {{ top: 120px; }}',
        f'{P} .sheet-ovwin .sheet-vv-wn:not(:empty)::before {{ content: ": "; }}',
        f'{P} .sheet-ovwin input.sheet-vv-wname {{ display: block; width: 100% !important; box-sizing: border-box; margin: 6px 0 !important; }}',
        f'{P} .sheet-ovwin textarea.sheet-vv-desc {{ display: block; width: 100% !important; box-sizing: border-box; min-height: 320px; height: 320px; resize: vertical; }}',
    ]) + '\n'
    return h, c
