"""Werewolf-only read-only reference: Primal Urge and Harmony tables, at the bottom of the Forms page (collapsible)."""
import re
F = ' <sup class="sheet-ref-q" title="Not checked against the W:tF 2E book; verify">?</sup>'
PU_T = [l.split('|') for l in """1|5|10/1|1B|10 minutes|None|3 months|0|0
2|5|11/2|1B|10 minutes|Meat|3 months|0|0
3|5|12/3|1B|15 minutes|Meat|1 month|0|0
4|5|13/4|2B|20 minutes|Raw meat|1 month|-2|+1
5|5|15/5|2B|30 minutes|Raw meat|3 weeks|-2|+1
6|6|20/6|3B|1 hour|Carnivore|3 weeks|-2|+2
7|7|25/7|3B|2 hour|Carnivore|1 week|-2|+2
8|8|30/8|4B|3 hours|Essence|1 week|-3|+3
9|9|50/10|5B|6 hours|Essence|3 days|-4|+3
10|10|75/15|6B|12 hours|Essence|3 days|-5|+4""".split('\n')]
PU_ESS = {int(r[0]): tuple(int(x) for x in r[2].split('/')) for r in PU_T}
def pu_rows():
    return ''.join(f'<tr class="sheet-pu-{r[0]}">' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in PU_T)
def shift(hm):
    if hm >= 9: return 'Instant action, always costs 1 Essence'
    if hm >= 7: return 'Instant action free, or reflexive for 1 Essence'
    if hm >= 4: return 'Reflexive, no cost'
    if hm >= 2: return 'Reflexive, no cost; involuntary shifts each scene, resisting is an instant action or 1 Essence'
    return 'Reflexive, no cost; involuntary shifts each scene, resisting needs an instant action and 1 Essence'
def side(hm):
    if hm >= 9: return 'Leans hard toward Spirit: the werewolf drifts from the physical world and human ties.' + F
    if hm >= 7: return 'Balanced, slightly spirit-leaning.' + F
    if hm >= 4: return 'Balanced: neither side dominates.'
    if hm >= 2: return 'Leans toward Flesh: driven by hunger and instinct, spirits react badly.' + F
    return 'Lost to one side: severe Flesh or Spirit effects; the Storyteller may take the character.' + F
def apply(h, c):
    a = '<div class="sheet-fcards">'; assert h.count(a) == 1
    i = h.index(a); depth = 0
    for m in re.finditer(r'<div\b|</div>', h[i:]):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0: e = i + m.end(); break
    th = lambda t, tip: f'<th title="{tip}">{t}</th>'
    hm_rows = ''.join(f'<tr class="sheet-hm-{x}"><td>{x}</td><td>{shift(x)}</td><td>{side(x)}</td></tr>' for x in range(10, -1, -1))
    box = ('<div class="sheet-huref sheet-game-line sheet-werewolf2">'
           '<input type="checkbox" class="sheet-huref-tg" name="attr_huref_open" value="1" title="Show or hide the reference tables" />'
           '<div class="sheet-huref-head">Harmony &amp; Primal Urge reference <span class="sheet-huref-hint">(read-only; click to open)</span></div>'
           '<div class="sheet-huref-body">'
           '<input type="hidden" class="sheet-pu-cur" name="attr_potency" value="1" /><input type="hidden" class="sheet-hm-cur" name="attr_morality" value="7" />'
           '<div class="sheet-huref-t">Primal Urge</div><table class="sheet-huref-tbl sheet-pu-tbl"><tr>'
           + th('PU', 'Primal Urge dots') + th('Attr/Skill Max', 'Attribute / Skill maximum') + th('Max Ess./Per Turn', 'Maximum Essence / Essence per turn') + th('Regen.', 'Regeneration') + th('Basu-Im Time', 'Basu-Im duration') + th('Feeding', 'Feeding restriction') + th('Hunt Time', 'Hunt time') + th('Lunacy', 'Lunacy penalty') + th('Tracking', 'Tracking bonus') + '</tr>' + pu_rows() + '</table>'
           '<div class="sheet-huref-t">Harmony</div><table class="sheet-huref-tbl sheet-hm-tbl"><tr>'
           + th('H', 'Harmony dots') + th('Shapeshifting', 'Action and Essence cost to change form') + th('Flesh / Spirit', 'Which side the werewolf leans toward and what that does') + '</tr>' + hm_rows + '</table>'
           '<div class="sheet-huref-note">Breaking points: Harmony is lost by acts that betray either the Flesh (denying the wolf, living as a mere human) or the Spirit '
           '(cruelty to spirits, neglecting the duty of the hunt); which side was sinned against decides the direction of the drift. Kuruth links to Harmony: TBD.' + F +
           ' Cells marked ? are from rules knowledge, not the book.</div>'
           '</div></div>')
    h = h[:e] + box + h[e:]
    c += ('\n/* r8 Harmony & Primal Urge reference */\n'
          '.charsheet .sheet-huref { position: relative; margin: 8px 2px 4px; padding: 2px 4px; border: 1px solid rgba(170,90,30,.6); border-radius: 6px; }\n'
          '.charsheet .sheet-huref input.sheet-huref-tg { position: absolute; top: 0; left: 0; width: 100%; height: 22px; margin: 0; opacity: 0; cursor: pointer; z-index: 2; }\n'
          '.charsheet .sheet-huref-head { font-weight: bold; line-height: 20px; }\n.charsheet .sheet-huref-hint { font-weight: normal; font-size: 11px; opacity: .7; }\n'
          '.charsheet .sheet-huref-body { display: none; }\n.charsheet .sheet-huref input.sheet-huref-tg:checked ~ .sheet-huref-body { display: block; }\n'
          '.charsheet .sheet-huref-t { margin: 6px 0 2px; font-weight: bold; }\n'
          '.charsheet table.sheet-huref-tbl { width: 100%; border-collapse: collapse; table-layout: auto; font-size: 11.5px; line-height: 1.3; }\n'
          '.charsheet table.sheet-huref-tbl th, .charsheet table.sheet-huref-tbl td { border: 1px solid rgba(255,255,255,.15); padding: 2px 4px; text-align: left; vertical-align: top; white-space: normal; word-break: normal; overflow-wrap: anywhere; }\n'
          '.charsheet table.sheet-huref-tbl th { cursor: help; }\n.charsheet .sheet-huref-note { font-size: 11px; margin: 4px 0 2px; opacity: .9; }\n'
          '.charsheet .sheet-ref-q { cursor: help; font-size: 9px; opacity: .8; }\n')
    for p in range(1, 11):
        c += f'.charsheet input.sheet-pu-cur[value="{p}"] ~ table.sheet-pu-tbl tr.sheet-pu-{p} td {{ background: rgba(170,90,30,.35); font-weight: bold; }}\n'
    for x in range(0, 11):
        c += f'.charsheet input.sheet-hm-cur[value="{x}"] ~ table.sheet-hm-tbl tr.sheet-hm-{x} td {{ background: rgba(170,90,30,.35); font-weight: bold; }}\n'
    return h, c
