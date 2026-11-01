"""Strip 1st-edition (nWoD) content: sheet types mortal1, vampire1, werewolf1, mage1, promethean1, changeling1, geist1, hunter1/hunter, mummy1, homebrew1.
Game-line classes shared with 2E (sheet-vampire, sheet-mage, ...) are kept; only edition-specific ones go."""
import re
from nodtf import _close
OLD = ['mortal1', 'vampire1', 'werewolf1', 'mage1', 'promethean1', 'changeling1', 'geist1', 'hunter1', 'mummy1', 'homebrew1']
TOK = {'sheet-' + x for x in OLD}
NEW = {'mortal1': 'mortal2', 'vampire1': 'vampire2', 'werewolf1': 'werewolf2', 'mage1': 'mage2', 'promethean1': 'promethean2', 'changeling1': 'changeling2',
       'geist1': 'geist2', 'hunter1': 'hunter2', 'hunter': 'hunter2', 'mummy1': 'mummy2', 'homebrew1': 'homebrew2'}
NEUTRAL = {'sheet-game-line', 'sheet-grow', 'sheet-flex', 'sheet-input-group', 'sheet-columns'}
def apply(h, c, t):
    before = set(re.findall(r'data-i18n(?:-[a-z]+)?="([^"]+)"', h)); n0 = len(h) + len(c)
    w0 = h.find('<script type="text/worker">')
    body, worker = h[:w0], h[w0:]
    removed = retag = 0; pos = 0
    rx = re.compile(r'<(div|span|label|button|input|option|select|textarea|img|p|h\d|table|tr|td)\b[^>]*class="([^"]*)"[^>]*>')
    while True:
        m = None
        for mm in rx.finditer(body, pos):
            if TOK & set(mm.group(2).split()): m = mm; break
        if not m: break
        cls = m.group(2).split(); rest = [x for x in cls if x not in TOK]
        gl = 'sheet-game-line' in cls
        other_lines = [x for x in rest if x not in NEUTRAL]
        # element belongs only to 1E lines when it is a game-line element with no other game-line class
        lines2 = [x for x in other_lines if re.match(r'sheet-(mortal|vampire|werewolf|mage|promethean|changeling|geist|hunter|mummy|demon|beast|homebrew|deviant|breeds)', x)]
        tag = m.group(1)
        if gl and not lines2:
            end = m.end() if tag in ('input', 'img') or m.group(0).endswith('/>') else _close(body, m.start(), tag)
            body = body[:m.start()] + body[end:]; removed += 1; pos = m.start()
        else:
            nt = m.group(0).replace('class="' + m.group(2) + '"', 'class="' + ' '.join(rest) + '"')
            body = body[:m.start()] + nt + body[m.end():]; retag += 1; pos = m.start() + 1
    # comments naming 1E types
    body = re.sub(r' !(%s)\b' % '|'.join(OLD), '', body)
    # worker: drop 1E case labels; migrate old 1E characters to the 2E equivalent (non-destructive: other attributes untouched)
    for _ in range(4): worker = re.sub(r'\s*case "(%s|hunter)":(?=\s*case )' % '|'.join(OLD), '', worker)
    worker = re.sub(r'(case "[^"]+":)(\s*)case "(%s|hunter)":' % '|'.join(OLD), r'\1', worker)
    mig = ('\n        on("sheet:opened", () => getAttrs(["sheettype"], (v) => { const M = %s; if (M[v.sheettype]) setAttrs({sheettype: M[v.sheettype], game_line: (typeof getGameLine === "function" ? getGameLine(M[v.sheettype]) : undefined) || "mortal", edition: 2, legacy_sheettype_1e: v.sheettype}); }));\n' % repr(NEW).replace("'", '"'))
    worker = worker.replace('</script>', mig + '</script>', 1) if 'legacy_sheettype_1e' not in worker else worker
    worker = re.sub(r'"(%s)",\s*' % '|'.join(OLD), '', worker)  # type lists
    h = body + worker
    c = re.sub(r':not\(\.sheet-(%s)\)' % '|'.join(OLD), '', c)
    def rw(mm):
        sels = [s for s in mm.group(1).split(',') if not re.search(r'sheet-(%s)\b|value="(%s)"' % ('|'.join(OLD), '|'.join(OLD + ['hunter'])), s)]
        return (','.join(sels) + '{') if sels else '\x00{'
    c = re.sub(r'([^{}@]+)\{', rw, c); c = re.sub(r'\x00\{[^{}]*\}', '', c)
    after = set(re.findall(r'data-i18n(?:-[a-z]+)?="([^"]+)"', h))
    gone = sorted(k for k in before - after if k in t)
    return h, c, removed, retag, gone, n0 - len(h) - len(c)
