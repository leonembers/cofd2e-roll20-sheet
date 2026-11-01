"""Splat isolation: re-assert the game-line gating with !important so later display rules cannot un-hide other splats' content."""
import re
def apply(h, c):
    sels = []
    for m in re.finditer(r'([^{}]+)\{\s*display:\s*none;?\s*\}', c):
        for s in m.group(1).split(','):
            s = s.strip()
            if re.match(r'input\.sheet-(type|game-line)\[value="[^"]+"\] ~ \* \.sheet-game-line', s) and '/*' not in s:
                sels.append('.charsheet ' + s.replace('~ * .sheet-game-line', '~ * .sheet-game-line.sheet-game-line', 1))
    sels = list(dict.fromkeys(sels))
    c += '\n/* isolation: each sheet type shows only its own game-line content */\n' + ',\n'.join(sels) + ' { display: none !important; }\n'
    # Kuruth pane is Werewolf-only even if mid_tab is left on "kuruth" after a sheet-type change
    h = h.replace('<div class="sheet-midpane sheet-mp-kuruth">', '<div class="sheet-midpane sheet-mp-kuruth sheet-game-line sheet-werewolf2">', 1)
    js = ('\n        on("sheet:opened change:sheettype", () => getAttrs(["sheettype","mid_tab"], v => { '
          'if (v.mid_tab === "kuruth" && v.sheettype !== "werewolf2") setAttrs({mid_tab: "merits"}, {silent: true}); }));\n')
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    # pool counter (Vitae / Essence / Mana / Glamour / ... share one counter): buttons only, value is display text
    old = '<input type="number" min="0" class="sheet-res-cur" name="attr_vitae" title="Current pool: type to edit" />'
    assert old in h
    h = h.replace(old, '<input type="number" readonly="readonly" tabindex="-1" class="sheet-res-cur" name="attr_vitae" title="Current pool: use the - and + buttons" />')
    c += ('.charsheet.charsheet .sheet-res-ctr input.sheet-res-cur { -webkit-appearance: textfield !important; -moz-appearance: textfield !important; appearance: textfield !important; '
          'pointer-events: none; user-select: none; cursor: default; caret-color: rgba(0,0,0,0); }\n'
          '.charsheet.charsheet .sheet-res-ctr input.sheet-res-cur::-webkit-outer-spin-button, .charsheet.charsheet .sheet-res-ctr input.sheet-res-cur::-webkit-inner-spin-button { -webkit-appearance: none !important; margin: 0 !important; display: none !important; }\n')
    # D10 roller: explicit selectors (no :is(), no body prefix) so Roll20 keeps the rule; hide Roll20's d6 glyph
    A = 'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@e4bf0904448b0247d0aefa0421c531c37345ea4e/icons/'
    bs = ['.charsheet.charsheet .sheet-rollbar.sheet-rollbar .sheet-rollcontainer > button[type="roll"].sheet-rollstyle.sheet-rollstyle',
          '.charsheet.charsheet .sheet-rollbar.sheet-rollbar .sheet-rollcontainer > button[type="action"].sheet-rollstyle.sheet-rollstyle',
          '.charsheet.charsheet .sheet-rollcontainer > button.sheet-rollstyle.sheet-rollstyle.sheet-was-roll']
    J = lambda suf: ', '.join(b + suf for b in bs)
    c += (f'\n{J("")} {{ position: absolute !important; top: 3px !important; left: 3px !important; right: 3px !important; bottom: 3px !important; width: auto !important; min-width: 0 !important; height: auto !important; min-height: 0 !important; margin: 0 !important; padding: 0 !important; cursor: pointer !important; flex: none !important; transform: none; border: 0 !important; box-shadow: none !important; '
          f'font-size: 0 !important; color: rgba(0,0,0,0) !important; background-color: rgba(0,0,0,0) !important; background-image: url("{A}d10-silver.png") !important; '
          'background-position: center !important; background-size: contain !important; background-repeat: no-repeat !important; text-shadow: none !important; }\n'
          f'{J(":hover")} {{ background-image: url("{A}d10-silver-hover.png") !important; }}\n'
          f'{J(":active")} {{ background-image: url("{A}d10-silver-pressed.png") !important; }}\n'
          f'{J("::before")}, {J("::after")} {{ content: none !important; display: none !important; font-size: 0 !important; }}\n')
    c += ('.charsheet.charsheet .sheet-diceroller-grid > .sheet-rollcontainer.sheet-rollcontainer { position: relative !important; display: block !important; align-self: center !important; height: 40px !important; min-height: 0 !important; width: 48px !important; min-width: 48px !important; flex: 0 0 48px !important; }\n')
    h = re.sub(r'(<button type="action" class="sheet-rollstyle sheet-(?:sheet|simple) sheet-was-roll"\s+)title="Roll pool"', r'\1title="Roll the dice pool (D10)"', h)
    # Changing Breeds: the Skill Proficiencies list becomes the check box beside each Skill (rows kept, list hidden)
    c += '.charsheet.charsheet .sheet-entry-section.sheet-skillpro { display: none !important; }\n'
    js2 = r"""
        on("sheet:opened", () => getAttrs(["skillpro_mig"], m => { if (m.skillpro_mig === "1") return;
            getSectionIDs("skillpro", ids => getAttrs(ids.flatMap(id => [`repeating_skillpro_${id}_name`, `repeating_skillpro_${id}_skill`]), v => {
                const norm = x => (x || "").toLowerCase().replace(/[^a-z]/g, ""); const u = {skillpro_mig: "1"};
                ids.forEach(id => [v[`repeating_skillpro_${id}_name`], v[`repeating_skillpro_${id}_skill`]].forEach(t => {
                    (t || "").split(/[,;\/]/).forEach(p => { const k = norm(p); if (SKILLS.includes(k)) u[`${k}_mark`] = "1"; }); }));
                setAttrs(u);
            }));
        }));
"""
    i = h.rfind('</script>'); h = h[:i] + js2 + h[i:]
    return h, c, len(sels)

def expand_is(c):
    """Rewrite simple :is(a, b) selectors as plain selector lists (older CSS sanitizers drop :is())."""
    out = []
    pos = 0
    for m in re.finditer(r'([^{}]*)\{', c):
        sel = m.group(1)
        if ':is(' not in sel or '@' in sel:
            continue
        parts = []
        for one in _split(sel):
            stack = [one]; done = []
            while stack:
                x = stack.pop()
                k = re.search(r':is\(([^()]*)\)', x)
                if not k: done.append(x); continue
                for alt in k.group(1).split(','):
                    stack.append(x[:k.start()] + alt.strip() + x[k.end():])
            parts += done[::-1]
        out.append((m.start(1), m.end(1), ',\n'.join(p.strip() for p in parts)))
    for a, b, rep in reversed(out):
        lead = c[a:b][:len(c[a:b]) - len(c[a:b].lstrip())]
        c = c[:a] + lead + rep + ' ' + c[b:]
    return c
def _split(sel):
    r, d, cur = [], 0, ''
    for ch in sel:
        if ch == '(': d += 1
        elif ch == ')': d -= 1
        if ch == ',' and d == 0: r.append(cur); cur = ''
        else: cur += ch
    r.append(cur); return [x for x in r if x.strip()]
