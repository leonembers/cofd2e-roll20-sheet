import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def get(name, sec=None):
    """Roll macro for a former type=roll button (now act_rr_*), from build/rr_mac.json written by src/reroll.py."""
    m = json.load(open(os.path.join(R, 'build', 'rr_mac.json')))
    name = name.replace('roll_', '', 1) if name.startswith('roll_') else name
    k = (sec + '|' + name) if sec else name
    if k in m: return m[k]
    import re, html
    sh = open(os.path.join(R, 'dist', 'sheet.html')).read()
    return html.unescape(re.search(r'name="roll_' + name + r'"[^>]*value="([^"]*)"', sh).group(1))
