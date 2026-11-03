"""Kuruth triggers as three full-width rows with Harmony ranges; active tiers highlighted from current Harmony.
Tiers per the W:tF 2E Harmony chart (p.105; Kuruth triggers p.103): the package tier that applies widens the further
Harmony is from 5. Harmony 0/10: Passive+Common+Specific; 1-2/8-9: Common+Specific; 3-4/6-7: Specific; 5: none.
General triggers (silver etc.) always apply."""
import re
TIERS = [('passive', 'Passive', 'Harmony 0 or 10', (0, 10)), ('common', 'Common', 'Harmony 0-2 or 8-10', (0, 1, 2, 8, 9, 10)),
         ('specific', 'Specific', 'Harmony 0-4 or 6-10', (0, 1, 2, 3, 4, 6, 7, 8, 9, 10))]
U = ' None of the personal triggers apply at Harmony 5; General triggers always apply.'
def apply(h, c):
    m = re.search(r'<div class="sheet-kuruth-tiers">.*?</label></div>', h, re.S); assert m
    rows = ['<input type="hidden" class="sheet-kt-hm" name="attr_morality" value="7" />']
    for k, n, r, _ in TIERS:
        rows.append(f'<label class="sheet-kuruth-tier sheet-kt-{k}" title="{n} triggers: can provoke Death Rage at {r}.{U}">'
                    f'<span class="sheet-kt-lbl"><span data-i18n="{k}">{n}</span> <span class="sheet-kt-rng">{r}</span></span>'
                    f'<textarea class="sheet-trig-ta" rows="3" name="attr_kuruth_{k}"></textarea></label>')
    h = h[:m.start()] + '<div class="sheet-kuruth-tiers sheet-kt-rows">' + ''.join(rows) + '</div>' + h[m.end():]
    P = '.charsheet.charsheet.charsheet .sheet-kuruth-tiers.sheet-kt-rows'
    c += (f'\n{P} {{ display: flex !important; flex-direction: column !important; gap: 6px !important; grid-template-columns: none !important; }}\n'
          f'{P} > label.sheet-kuruth-tier {{ display: flex !important; flex-direction: column !important; width: 100% !important; margin: 0 !important; padding: 3px 5px !important; box-sizing: border-box !important; border: 1px solid rgba(160,130,90,.35); border-radius: 4px; opacity: .6; }}\n'
          f'{P} .sheet-kt-lbl {{ display: flex; justify-content: space-between; font-weight: bold; font-size: 12px; }}\n'
          f'{P} .sheet-kt-rng {{ font-weight: normal; font-size: 11px; opacity: .85; }}\n'
          f'{P} textarea.sheet-trig-ta {{ width: 100% !important; height: 58px !important; min-height: 40px !important; box-sizing: border-box !important; resize: vertical; }}\n')
    for k, _, _, mx in TIERS:
        sel = ', '.join(f'{P} input.sheet-kt-hm[value="{v}"] ~ label.sheet-kt-{k}' for v in mx)
        c += f'{sel} {{ opacity: 1 !important; border-color: #c8873a !important; background: rgba(200,135,58,.14) !important; }}\n'
    return h, c
