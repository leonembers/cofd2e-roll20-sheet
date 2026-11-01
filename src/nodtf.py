"""Remove Demon the Fallen (WoD 2E Translation Guide, sheet type wod-demon2 / game line wod-demon). Demon: the Descent ('demon') is kept."""
import re
TOK = ('sheet-wod-demon', 'sheet-wod-demon2', 'sheet-active-wod-demon2')
def _close(h, i, tag):
    d = 0
    for m in re.finditer(r'<(/?)%s\b[^>]*?(/?)>' % tag, h[i:]):
        if m.group(2): continue
        d += -1 if m.group(1) else 1
        if d == 0: return i + m.end()
    raise ValueError(tag)
def apply(h, c, t):
    before = set(re.findall(r'data-i18n(?:-[a-z]+)?="([^"]+)"', h))
    n0 = len(h) + len(c)
    # selector heading + pill
    h, k = re.subn(r'\s*<div class="sheet-edition-label" data-i18n="second-edition-translation-guides">.*?</div>\s*<div>\s*<button[^>]*act_sheet_type_wod-demon2[^>]*>.*?</button>\s*</div>', '', h, count=1, flags=re.S)
    assert k == 1, 'dtf pill'
    h = re.sub(r'\s*<img class="sheet-game-line sheet-wod-demon"[^>]*>', '', h)
    h = h.replace('<div class= "sheet-game-line', '<div class="sheet-game-line')
    h = h.replace(' !wod-demon-->', '-->')
    c = re.sub(r'\s*--color-wod-demon:[^;]*;', '', c)
    removed = 0
    while True:
        m = None
        for mm in re.finditer(r'<(div|span|label|button|input|option|select|textarea|fieldset)\b[^>]*class="([^"]*)"[^>]*>', h):
            cls = mm.group(2).split()
            if any(x in TOK for x in cls): m = mm; break
        if not m: break
        cls = m.group(2).split(); gl = [x for x in cls if x.startswith('sheet-') and x not in ('sheet-game-line',)]
        lines = [x for x in cls if x not in TOK]
        only = 'sheet-game-line' in cls and not any(x for x in lines if x not in ('sheet-game-line', 'sheet-grow', 'sheet-flex', 'sheet-input-group') and not x.startswith('sheet-preserve'))
        tag = m.group(1)
        if only or 'sheet-active-wod-demon2' in cls:
            end = m.end() if tag == 'input' or m.group(0).endswith('/>') else _close(h, m.start(), tag)
            h = h[:m.start()] + h[end:]; removed += 1
        else:
            newtag = m.group(0).replace(m.group(2), ' '.join(lines))
            h = h[:m.start()] + newtag + h[m.end():]
    # css: drop selectors mentioning wod-demon; drop rules left empty
    def rw(mm):
        sels = [s for s in mm.group(1).split(',') if 'wod-demon' not in s]
        return (','.join(sels) + '{') if sels else '\x00{'
    c = re.sub(r'([^{}]+)\{', rw, c)
    c = re.sub(r'\x00\{[^}]*\}', '', c)
    # worker: drop the type from lists / switch cases (keep code valid)
    h = re.sub(r'\s*case "wod-demon2":\s*return "wod-demon";', '', h)
    h = re.sub(r'\s*"wod-demon2":"faith",', '', h)
    h = h.replace('"homebrew2","wod-demon2",', '"homebrew2",')
    h = re.sub(r'\s*case "wod-demon2":(?=\s*case)', '', h)
    after = set(re.findall(r'data-i18n(?:-[a-z]+)?="([^"]+)"', h))
    gone = sorted(k for k in before - after if k in t)
    for k in gone: t.pop(k, None)
    return h, c, t, removed, gone, n0 - len(h) - len(c)
