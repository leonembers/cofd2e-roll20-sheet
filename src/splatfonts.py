"""Per-splat header fonts (closest Google Font to each official PDF sheet's header face). Body text font unchanged."""
MAP = [  # (sheet types, PDF header font, Google font, fallback)
    (['mortal2', 'mortal2-ghost'], 'Goudy Old Style (CofD core sheet)', 'Sorts Mill Goudy', 'serif'),
    (['vampire2'], 'Caslon Antique / Mrs Eaves SC', 'IM Fell English SC', 'serif'),
    (['werewolf2', 'breeds2'], 'FlatEarthScribe (+ Treefrog)', 'Fondamento', 'cursive'),
    (['mage2'], 'Lilith', 'Cinzel Decorative', 'serif'),
    (['promethean2'], 'Pterra / Industrial Schizophrenic', 'Metamorphous', 'serif'),
    (['changeling2'], 'Rackham', 'Almendra', 'serif'),
    (['hunter2'], 'VTSmith Upright', 'Special Elite', 'monospace'),
    (['geist2'], 'Trinigan FG / Swansea', 'Pirata One', 'serif'),
    (['demon'], 'Conspiracy / Crack Babies', 'Black Ops One', 'sans-serif'),
    (['beast'], 'Whiffy / Hans Hand', 'Creepster', 'cursive'),
    (['deviant-the-renegades'], 'Repent / Swede-Trauma', 'Metal Mania', 'serif'),
    (['mummy2'], 'Lumiera / Daela', 'Cinzel', 'serif'),
]
def css():
    fams = sorted({g for _, _, g, _ in MAP if g != 'Sorts Mill Goudy'})
    imp = '@import url("https://fonts.googleapis.com/css?family=' + '%7C'.join(f.replace(' ', '+') for f in fams) + '&display=swap");\n'
    tgt = ['.sheet-section-header.sheet-section-header.sheet-section-header', '.sheet-subheader.sheet-subheader.sheet-subheader', 'button.sheet-midtab-btn.sheet-midtab-btn.sheet-midtab-btn', 'button.sheet-toggle.sheet-toggle.sheet-toggle[name^="act_page_"]']
    o = []
    for types, _, g, fb in MAP:
        sels = []
        for t in types:
            for x in tgt:
                sels.append(f'.charsheet.charsheet input.sheet-type.sheet-type[value="{t}"] ~ {x}')
                sels.append(f'.charsheet.charsheet input.sheet-type.sheet-type[value="{t}"] ~ * {x}')
        o.append(', '.join(sels) + f' {{ font-family: "{g}", {fb} !important; }}')
    return imp, '\n'.join(o) + '\n'
def report():
    return '\n'.join(f'{", ".join(t)}: {p} -> {g}' for t, p, g, _ in MAP)
