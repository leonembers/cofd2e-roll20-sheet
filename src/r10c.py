"""r10c: header 3x3 (Concept under Vice; Hunter Cell/Compact/Conspiracy), Forsaken-only tribes, Risk WP control + auto WP."""
import re
def apply(h, c):
    for t in ('Fire-Touched (Pure)', 'Ivory Claws (Pure)', 'Predator Kings (Pure)'):
        h = h.replace(f'<option value="{t}">{t}</option>', '')
    # Risk Willpower outcome (Hunter: the Vigil 2E p.135)
    old = 'finishRoll(r.rollId);\n        });\n        Object.keys(RR_MAC)'
    assert old in h
    h = h.replace(old, 'finishRoll(r.rollId); if (!isRe && R.roll) riskWp(R.roll.result || 0);\n        });\n        Object.keys(RR_MAC)', 1)
    js = r'''
        const riskWp = (succ) => getAttrs(["wp_risk", "sheettype", "willpower", "willpower_cur"], v => {
            if (v.wp_risk !== "1" || v.sheettype !== "hunter2") return;
            const max = parseInt(v.willpower, 10) || 0, cur = Math.max(0, parseInt(v.willpower_cur, 10) || 0);
            const ok = succ >= 1, nw = Math.max(0, Math.min(max, ok ? cur + 1 : cur - 1));
            setAttrs({willpower_cur: nw, wp_risk: "0", risk_b1: "", risk_b2: ""});
            const txt = ok ? "Success: the risked point is kept and 1 Willpower is regained, plus a Beat." : "Failure: the risked Willpower point is lost. Take the failure Beat(s).";
            startRoll("&{template:cofd-entry} {{charname=@{character_name}}} {{gl_hunter=1}} {{splat=hunter}} {{kind=Willpower}} {{name=Risked Willpower}} {{f_short=" + txt + " WP " + cur + " to " + nw + " of " + max + ".}}", r => finishRoll(r.rollId));
        });
'''
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    C = []
    G = '.charsheet.charsheet.charsheet.charsheet .sheet-info-grid.sheet-ig2'
    C.append(G + ' { grid-auto-flow: row dense !important; }')
    place = [('attr_character_name', 1, 1), ('attr_Player', 1, 2), ('attr_Chronicle', 1, 3),
             ('attr_Virtue', 2, 1), ('attr_Vice', 2, 2), ('attr_Concept', 2, 3),
             ('attr_GroupName', 3, 2)]
    for n, col, row in place:
        C.append(f'{G} > .sheet-ifield:has([name="{n}"]) {{ grid-column: {col} / span 1 !important; grid-row: {row} !important; }}')
    # third column row 3: the faction field (Conspiracy, Tribe, Order...) unless covenant took it
    C.append(f'{G} > .sheet-ifield:has(input[name="attr_Faction"]) {{ grid-column: 3 / span 1 !important; grid-row: 3 !important; }}')
    V = '.charsheet.charsheet.charsheet.charsheet input.sheet-type[value="vampire2"] ~ * .sheet-info-grid.sheet-ig2.sheet-ig2'
    C.append(f'{V} > .sheet-ifield:has(input[name="attr_Faction"]) {{ grid-row: 2 !important; }}')
    C.append(f'{V} > .sheet-ifield:has(input[name="attr_GroupName"]) {{ grid-row: auto !important; grid-column: auto !important; }}')
    C.append(f'{V} > .sheet-ifield:has(select[name="attr_covenant"]) {{ grid-column: 3 / span 1 !important; grid-row: 3 !important; }}')
    C.append(f'{G} > .sheet-ifield {{ grid-column-end: span 1 !important; min-width: 0; }}')
    # Risk WP pill + benefits only while risking
    C += ['.charsheet.charsheet.charsheet .sheet-risk-ctl > label { width: auto !important; flex: 0 0 auto !important; padding: 1px 8px !important; white-space: nowrap; }',
          '.charsheet.charsheet.charsheet .sheet-risk-ctl { display: inline-flex; flex-wrap: wrap; gap: 4px; align-items: center; width: auto !important; }',
          '.charsheet.charsheet.charsheet .sheet-risk-ctl:not(:has(input[name="attr_wp_risk"]:checked)) > select { display: none !important; }']
    c += '\n' + '\n'.join(C) + '\n'
    return h, c
