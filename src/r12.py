"""r12: Chomsky (Fredrick R. Brennan, SIL OFL 1.1) as the Vampire header font, IM Fell English SC fallback.
Covers the same header types Wolf's Rain covers for Werewolf (r10b/r10f/r11) plus Config card and popup titles."""
CH = 'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@6a58e5250284a0e98157f57a4058755dc6a684ab/fonts/chomsky/Chomsky.otf'
FAM = '"Chomsky", "IM Fell English SC", serif'
EXTRA = ['* .sheet-subheader', '* .sheet-subheader span', '* .sheet-midtabs button', '* h1', '* h2', '* h3',
         '* .sheet-section-header.sheet-section-header.sheet-section-header', '* .sheet-section-header.sheet-section-header.sheet-section-header *',
         '* .sheet-config-title', '* .sheet-cfg-head', '* .sheet-cfg-card > .sheet-subheader', '* .sheet-km-title',
         '* .sheet-entry-section-head', '* .sheet-huref-t', '* .sheet-ovbtn',
         '.sheet-section-header.sheet-section-header.sheet-section-header', '.sheet-subheader.sheet-subheader.sheet-subheader']

def apply(h, c):
    V = '.charsheet.charsheet.charsheet.charsheet input.sheet-type.sheet-type.sheet-type[value="vampire2"] ~ '
    L = ['@font-face { font-family: "Chomsky"; src: url("' + CH + '") format("opentype"); font-display: swap; }',
         ', '.join(V + x for x in EXTRA) + ' { font-family: ' + FAM + ' !important; }']
    VC = ('<div class="sheet-fontcredit sheet-fc-vampire">Vampire headers: Chomsky by Fredrick R. Brennan '
          '(SIL Open Font License 1.1), dafont.com/chomsky.font</div>')
    i = h.find('class="sheet-fontcredit"')
    assert i > 0
    j = h.find('</div>', i) + 6; h = h[:j] + VC + h[j:]
    L.append('.charsheet.charsheet .sheet-fc-vampire { display: none; font-size: 11px; opacity: .8; text-align: center; margin: 2px 0 6px; }')
    L.append('.charsheet.charsheet input.sheet-type[value="vampire2"] ~ * .sheet-fc-vampire { display: block !important; }')
    L.append('.charsheet.charsheet.charsheet.charsheet input.sheet-type.sheet-type:not([value="vampire2"]) ~ * .sheet-fc-vampire { display: none !important; }')
    # r11 Hunter credit also carries .sheet-fontcredit, so the Werewolf show-rule leaked it onto Werewolf Config
    L.append('.charsheet.charsheet.charsheet.charsheet input.sheet-type.sheet-type:not([value="hunter2"]) ~ * .sheet-fc-hunter { display: none !important; }')
    return h, repctl(c + '\n' + '\n'.join(L) + '\n')

# ---- repeating-section header controls (Roll20's own repcontrol_edit / repcontrol_add) ----
IC = 'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@10ffd168cf8356d3ffe9de8ca062462124cd625a/icons/repcontrol/'

def repctl(c):
    """Gear for Modify, plus for New, check for Done, drawn as background images so ::before/::after are free.
    ::before is cleared (it held the old drawn icon); ::after is a real tooltip (Roll20 makes these buttons, so no title attr)."""
    P = '.charsheet.charsheet.charsheet.charsheet .repcontrol'
    E, A = f'{P} .repcontrol_edit', f'{P} .repcontrol_add'
    DK = '.charsheet.charsheet.charsheet.charsheet input.sheet-dm[value="1"] ~ .sheet-background .repcontrol'
    DM = '.sheet-darkmode .charsheet.charsheet.charsheet.charsheet .repcontrol'
    L = [f'{P} {{ overflow: visible !important; }}',
         f'{E}, {A} {{ overflow: visible !important; background-repeat: no-repeat !important; background-position: center !important; background-size: 12px 12px !important; }}',
         f'{E} {{ background-image: url("{IC}gear-dark.svg") !important; }}',
         f'{A} {{ background-image: url("{IC}plus-dark.svg") !important; }}',
         f'{DK} .repcontrol_edit, {DM} .repcontrol_edit {{ background-image: url("{IC}gear-light.svg") !important; }}',
         f'{DK} .repcontrol_add, {DM} .repcontrol_add {{ background-image: url("{IC}plus-light.svg") !important; }}',
         f'.charsheet.charsheet.charsheet.charsheet .repcontainer.editmode ~ .repcontrol .repcontrol_edit {{ background-image: url("{IC}check.svg") !important; }}',
         f'{E}::before, {A}::before, {E}::after, {A}::after {{ content: none !important; display: none !important; }}',
         f'{E}:hover::after, {A}:hover::after {{ display: block !important; position: absolute; bottom: 120%; right: 0; left: auto; top: auto; z-index: 80; width: auto; height: auto;'
         f' white-space: nowrap; background: #222 !important; color: #eee !important; border: 1px solid #555; border-radius: 3px; padding: 2px 6px;'
         f' font: 11px/1.3 Arial, sans-serif !important; transform: none !important; pointer-events: none; box-shadow: 0 2px 6px rgba(0,0,0,.4); }}',
         f'{E}:hover::after {{ content: "Modify" !important; }}',
         f'{A}:hover::after {{ content: "New" !important; }}',
         f'.charsheet.charsheet.charsheet.charsheet .repcontainer.editmode ~ .repcontrol .repcontrol_edit:hover::after {{ content: "Done" !important; }}']
    return c + '\n' + '\n'.join(L) + '\n'
