"""r11: 1980s Writer for Hunter, one header font per splat on every header type, compact two-column right panel."""
import json, os
R = os.path.dirname(os.path.abspath(__file__))
F80 = 'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@d0f3424fc60b76ad44de65ae21be08ce1458b370/fonts/1980swriter/1980sWriter.ttf'
FONTS = {
    'mortal2': '"Sorts Mill Goudy", serif', 'vampire2': '"IM Fell English SC", serif',
    'werewolf2': '"WolfsRain", "IM Fell English SC", serif', 'breeds2': '"Fondamento", cursive',
    'mage2': '"Cinzel Decorative", serif', 'promethean2': '"Metamorphous", serif', 'changeling2': '"Almendra", serif',
    'hunter2': '"1980sWriter", "Special Elite", monospace', 'geist2': '"Pirata One", serif', 'demon': '"Black Ops One", sans-serif',
    'beast': '"Creepster", cursive', 'mummy': '"Sorts Mill Goudy", Georgia, serif',
    'deviant-the-renegades': '"Metal Mania", serif', 'homebrew': '"Sorts Mill Goudy", Georgia, serif',
}
HDR = ['.sheet-section-header', '.sheet-section-header *', '.sheet-subheader', '.sheet-subheader > span', '.sheet-subheader > button',
       '.sheet-subheader > span > span', '.sheet-huref-t', '.sheet-cg-glabel', 'button.sheet-midtab-btn', '.sheet-cfg-head', '.sheet-ovbtn']

def apply(h, c):
    O = '.charsheet.charsheet.charsheet.charsheet'
    L = ['@font-face { font-family: "1980sWriter"; src: url("' + F80 + '") format("truetype"); font-display: swap; }']
    for t, f in FONTS.items():
        sel = []
        for x in HDR:
            sel.append(f'{O} input.sheet-type.sheet-type.sheet-type[value="{t}"] ~ * {x}.sheet-x, {O} input.sheet-type.sheet-type.sheet-type[value="{t}"] ~ {x}'.replace('.sheet-x', ''))
        # extra weight so it beats the older per-splat rules
        sel = [s.replace(' .sheet-section-header', ' .sheet-section-header.sheet-section-header.sheet-section-header')
                .replace(' .sheet-subheader', ' .sheet-subheader.sheet-subheader.sheet-subheader') for s in sel]
        L.append(', '.join(sel) + ' { font-family: ' + f + ' !important; }')
    # pills stay compact and legible in display fonts
    L.append(f'{O} button.sheet-midtab-btn.sheet-midtab-btn {{ font-size: 13px !important; letter-spacing: .02em; }}')
    # Hunter credit on Config
    HC = ('<div class="sheet-fontcredit sheet-fc-hunter">Hunter headers: 1980s Writer by Johnny Face (SIL Open Font License; '
          'author: free to use personally and commercially), dafont.com/1980swriter.font</div>')
    i = h.find('class="sheet-fontcredit"')
    if i > 0:
        j = h.find('</div>', i) + 6; h = h[:j] + HC + h[j:]
    L.append('.charsheet.charsheet .sheet-fc-hunter { display: none; font-size: 11px; opacity: .8; text-align: center; margin: 2px 0 6px; }')
    L.append('.charsheet.charsheet input.sheet-type[value="hunter2"] ~ * .sheet-fc-hunter { display: block !important; }')
    # right panel: two columns for short items, Health stays full width
    P = '.charsheet.charsheet.charsheet'
    L += [
        f'{P} .sheet-organization-inverse:has(> .sheet-derived) {{ display: grid !important; grid-template-columns: 1fr 1fr; gap: 2px 8px; height: auto !important; }}',
        f'{P} .sheet-organization-inverse > .sheet-derived {{ height: auto !important; min-height: 0 !important; margin: 0 !important; display: flex !important; align-items: center; justify-content: flex-start; gap: 4px; white-space: nowrap; }}',
        f'{P} .sheet-organization-inverse > .sheet-derived > span {{ font-size: 12px; }}',
        f'{P} .sheet-organization-inverse > .sheet-derived:last-child:nth-child(odd) {{ grid-column: 1 / -1; justify-content: center; }}',
        f'{P} .sheet-xp-trio {{ display: flex !important; flex-direction: row !important; flex-wrap: nowrap; gap: 4px; height: auto !important; align-items: center; justify-content: space-between; }}',
        f'{P} .sheet-xp-trio input {{ width: 30px !important; min-width: 0 !important; }}',
        f'{P} .sheet-input-group:has(> .sheet-xp-trio) {{ display: flex !important; flex-wrap: wrap; align-items: center; gap: 2px 6px; height: auto !important; }}',
        f'{P} .sheet-input-group > .sheet-xp-trio {{ flex: 1 1 100%; }}',
        f'{P} .sheet-quick-actions.sheet-vampire2 {{ display: grid !important; grid-template-columns: 1fr 1fr; gap: 4px; }}',
        f'{P} .sheet-quick-actions.sheet-vampire2 > button.sheet-quick {{ width: auto !important; min-width: 0 !important; height: 26px !important; margin: 0 !important; padding: 0 4px !important; font-size: 12px !important; }}',
        f'{P} .sheet-quick-actions.sheet-vampire2 > button.sheet-quick:last-child {{ grid-column: 1 / -1; }}',
        f'{P} .sheet-input-group:has(> .sheet-xp-trio) > span:not([class]) + span:not([class]) {{ display: none !important; }}',
    f'{P} .sheet-subheader > button.sheet-toggle {{ color: inherit !important; }}',
    f'{P} .sheet-el_spacer {{ height: 4px !important; min-height: 0 !important; }}',
    ]
    return h, c + '\n' + '\n'.join(L) + '\n'
