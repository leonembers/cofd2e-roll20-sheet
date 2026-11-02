"""r10d: Conditions / Tilts overlay windows (CSS toggles), Notes page grid, bare resource counters."""
import re
from r10b import take_div

def apply(h, c):
    # --- Conditions page -> two overlay windows ---
    i = h.index('<div class="sheet-page sheet-conditions">'); a0, a1 = take_div(h, i); s = h[a0:a1]
    s = re.sub(r'<div class="sheet-hint">.*?</div>\s*', '', s, count=2, flags=re.S)
    tilts = []
    for lab in ('Personal Tilts', 'Environmental Tilts'):
        j = s.index(f'<div class="sheet-cg-group"><div class="sheet-cg-glabel">{lab}</div>'); b0, b1 = take_div(s, j)
        tilts.append(s[b0:b1]); s = s[:b0] + s[b1:]
    ids = lambda t: re.findall(r'class="sheet-cg-toggle" name="attr_(\w+)"', t)
    cids, tids = ids(s), ids(''.join(tilts))
    x = lambda n: f'<input type="checkbox" class="sheet-ov-x" name="attr_{n}" value="1" title="Close" />'
    s = s.replace('<div class="sheet-page sheet-conditions">', '<div class="sheet-ovwin sheet-ov-cond">' + x('ov_cond'), 1)
    s = s.replace('<div class="sheet-subheader">Conditions &amp; Tilts</div>', '<div class="sheet-subheader">Conditions</div>'
                  '<div class="sheet-ov-note">Tick to activate. Resolving a Condition gives a Beat unless it says otherwise; Persistent ones (P) give a Beat each time they hinder you. Custom entries (Conditions or Tilts) are at the bottom.</div>', 1)
    tw = ('<div class="sheet-ovwin sheet-ov-tilt">' + x('ov_tilt') + '<div class="sheet-cond-grid-wrap"><div class="sheet-subheader">Tilts</div>'
          '<div class="sheet-ov-note">Tilts are combat effects: they apply while the situation lasts and do not give Beats. Add custom Tilts in the Conditions window (Type: Tilt).</div>'
          + ''.join(tilts) + '</div></div>')
    h = h[:a0] + s + tw + h[a1:]
    btn = lambda n, lb, cnt, ti: (f'<label class="sheet-ovbtn sheet-ovb-{n}" title="{ti}"><input type="checkbox" class="sheet-ovf" name="attr_ov_{n}" value="1" />'
                                  f'{lb}<span class="sheet-ov-badge"><input type="hidden" class="sheet-ov-cnt" name="attr_{cnt}" value="0" /><span name="attr_{cnt}"></span></span></label>')
    t = '<button type="action" class="sheet-toggle sheet-page-conditions sheet-2nd"'
    k = h.index(t); k2 = h.index('</button>', k) + 9
    h = h[:k] + btn('cond', 'Conditions', 'cond_count', 'Open the Conditions window') + btn('tilt', 'Tilts', 'tilt_count', 'Open the Tilts window') + h[k2:]
    js = ('\n        const OV_C = ' + repr(cids).replace("'", '"') + ', OV_T = ' + repr(tids).replace("'", '"') + ';\n' + r'''
        const ovCount = () => getAttrs(OV_C.concat(OV_T, ["pagenumber"]), v => { const n = a => a.filter(k => v[k] === "1").length;
            const u = {cond_count: n(OV_C), tilt_count: n(OV_T)}; if (v.pagenumber === "conditions") u.pagenumber = "1"; setAttrs(u, {silent: true}); });
        on("sheet:opened " + OV_C.concat(OV_T).map(k => "change:" + k).join(" "), ovCount);
''')
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    C = []
    O = '.charsheet.charsheet.charsheet'
    C += [f'{O} .sheet-ovwin {{ display: none; position: absolute; z-index: 60; left: 70px; right: 60px; top: 150px; max-height: 1400px; overflow: auto; padding: 8px 12px 12px; background: #141210; border: 2px solid var(--color-game-line, #b4743a); border-radius: 8px; box-shadow: 0 8px 30px rgba(0,0,0,.85); }}',
          f'{O} .sheet-ov-tilt {{ top: 190px; left: 110px; right: 30px; z-index: 61; }}',
          f'.charsheet:has(input.sheet-ovf[name="attr_ov_cond"]:checked) .sheet-ovwin.sheet-ov-cond, .charsheet:has(input.sheet-ovf[name="attr_ov_tilt"]:checked) .sheet-ovwin.sheet-ov-tilt {{ display: block !important; }}',
          f'{O} .sheet-ovwin input.sheet-ov-x {{ -webkit-appearance: none; appearance: none; float: right; width: 26px !important; height: 26px !important; margin: 0 0 4px 8px !important; border-radius: 50%; background: #3a1010 !important; border: 1px solid #e03a2f !important; cursor: pointer; opacity: 1 !important; }}',
          f'{O} .sheet-ovwin input.sheet-ov-x::after {{ content: "X"; display: block; text-align: center; line-height: 24px; color: #fff; font: bold 14px/24px Arial, sans-serif; }}',
          f'{O} .sheet-ov-note {{ font-size: 12px; opacity: .8; margin: 2px 0 6px; text-align: center; }}',
          f'{O} .sheet-background > button.sheet-page-conditions {{ display: none !important; }}',
          f'{O} label.sheet-ovbtn {{ order: 2; display: inline-flex !important; align-items: center; gap: 5px; margin: 0 4px; padding: 2px 10px; border: 1px solid var(--color-game-line, #b4743a); border-radius: 999px; background: #0d0d0d; color: #d8d2c8; cursor: pointer; font-weight: bold; font-size: 13px; width: auto !important; }}',
          f'{O} label.sheet-ovbtn > input.sheet-ovf {{ display: none !important; }}',
          f'{O} label.sheet-ovbtn:has(input.sheet-ovf:checked) {{ background: var(--color-game-line, #b4743a); color: #fff; }}',
          f'{O} .sheet-ov-badge {{ display: inline-block; min-width: 16px; padding: 0 4px; border-radius: 8px; background: #8e1616; color: #fff; font-size: 11px; line-height: 16px; text-align: center; }}',
          f'{O} .sheet-ov-badge:has(input.sheet-ov-cnt[value="0"]) {{ display: none; }}']
    # --- Notes page: short fields in a grid, long text two columns, auto-grow ---
    C += [f'{O} .sheet-det-splat {{ display: grid !important; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 4px 10px; }}',
          f'{O} .sheet-det-splat > * {{ grid-column: span 2; min-width: 0; margin: 0 !important; }}',
          f'{O} .sheet-det-splat > .sheet-subheader {{ grid-column: 1 / -1; }}',
          f'{O} .sheet-det-splat > label.sheet-wide, {O} .sheet-det-splat > .sheet-wide {{ grid-column: span 3; }}',
          f'{O} .sheet-det-splat > div:has(table), {O} .sheet-det-splat > table {{ grid-column: 1 / -1; }}',
          f'{O} .sheet-det-splat input, {O} .sheet-det-long textarea, {O} .sheet-det-splat textarea {{ width: 100% !important; box-sizing: border-box; }}',
          f'{O} .sheet-det-long {{ display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px 12px; }}',
          f'{O} .sheet-det-long > label {{ grid-column: auto !important; margin: 0 !important; min-width: 0; }}',
          f'{O} .sheet-details textarea {{ field-sizing: content; min-height: 54px; resize: vertical; }}']
    # --- resource counters: bare current value like the max ---
    C += [f'{O} .sheet-res-ctr {{ display: flex !important; align-items: center; justify-content: center; gap: 2px; }}',
          f'{O} .sheet-res-ctr input.sheet-res-cur {{ -webkit-appearance: none; appearance: none; -moz-appearance: textfield; background: rgba(0,0,0,0) !important; border: 0 !important; box-shadow: none !important; outline: 0 !important; padding: 0 !important; margin: 0 !important; width: 2.4ch !important; min-width: 0 !important; height: auto !important; text-align: right; font: inherit !important; color: inherit !important; pointer-events: none; }}',
          f'{O} .sheet-res-ctr input.sheet-res-cur::-webkit-inner-spin-button, {O} .sheet-res-ctr input.sheet-res-cur::-webkit-outer-spin-button {{ -webkit-appearance: none; margin: 0; }}',
          f'{O} .sheet-res-ctr .sheet-res-max {{ min-width: 2.4ch; text-align: left; }}']
    c += '\n' + '\n'.join(C) + '\n'
    return h, c
