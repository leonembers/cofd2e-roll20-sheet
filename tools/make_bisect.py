"""Write dist/bisect/*.css variants of dist/sheet.css for live Roll20 roll-template CSS bisection."""
import re, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
c = open(f'{R}/dist/sheet.css').read()
def blocks(s):  # top-level blocks (handles one nesting level such as @media)
    out, i, n = [], 0, len(s)
    while i < n:
        j = s.find('{', i)
        if j < 0: break
        d, k = 1, j + 1
        while d and k < n: d += {'{': 1, '}': -1}.get(s[k], 0); k += 1
        out.append((s[i:j].strip(), s[j:k])); i = k
    return out
B = blocks(c)
tpl = lambda sel: 'rolltemplate' in sel
def w(name, bs): open(f'{R}/dist/bisect/{name}.css', 'w').write('\n'.join(f'{s} {b}' for s, b in bs) + '\n'); return name
A = [(s, b) for s, b in B if tpl(s)]
w('A_template_only', A)
w('B_no_url', [(s, re.sub(r'url\([^)]*\)', 'none', b)) for s, b in B])
def novar(b):
    b = re.sub(r'var\(--[\w-]+\s*,\s*([^()]*(?:\([^()]*\))?[^()]*)\)', r'\1', b)
    b = re.sub(r'var\(--[\w-]+\)', 'inherit', b)
    return re.sub(r'(?<![\w-])--[\w-]+\s*:[^;{}]*;?', '', b)
w('C_no_custom_props', [(s, novar(b)) for s, b in B])
w('D_no_is_where_has_supports', [(s, b) for s, b in B if not re.search(r':(is|where|has)\(|@supports', s + b)])
w('E_no_important', [(s, b.replace('!important', '')) for s, b in B])
w('F_template_only_plain', [(s, novar(re.sub(r'url\([^)]*\)', 'none', b)).replace('!important', '')) for s, b in A])
for f in sorted(os.listdir(f'{R}/dist/bisect')):
    if f.endswith('.css'): print(f, os.path.getsize(f'{R}/dist/bisect/{f}'), 'webp' in open(f'{R}/dist/bisect/{f}').read().lower())
