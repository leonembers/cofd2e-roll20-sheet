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
    return h, c + '\n' + '\n'.join(L) + '\n'
