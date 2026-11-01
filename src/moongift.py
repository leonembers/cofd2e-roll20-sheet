"""Werewolf Moon Gift block: facet names/dots/pages verified against W:tF 2E core pp. 115-121 (page images).
Summaries are our own one-liners; no rules text copied."""
import html
from wolf import AUSP, moon_svg
# (dots, name, page, own summary, cost, pool as (attr, skill) or None)
F = {
 'crescent': [(1, 'Shadow Gaze', 115, 'Read a spirit, learning its ban or bane', '1 Essence', ('wits', 'occult')),
              (2, 'Spirit Whispers', 115, 'Wake a dormant object-spirit and ask it one question', '1 Essence', ('presence', 'persuasion')),
              (3, 'Shadow Hunter', 116, 'Hunt bonus while chasing prey through the Shadow (Siskur-Dah only)', '1 Essence', None),
              (4, 'Shadow Masquerade', 116, 'Pass as a spirit by wearing its Essence like a mask', '2 Essence', ('manipulation', 'occult')),
              (5, 'Panopticon', 117, 'Enlist local spirits as eyes and ears over a wide area', 'Essence = highest Rank', ('intelligence', 'occult'))],
 'full': [(1, 'Killer Instinct', 117, 'Brawl and Weaponry gain 8-again for the scene', '1 Essence', None),
          (2, "Warrior's Hide", 117, 'Permanently add Purity to Health', 'none', None),
          (3, 'Bloody-Handed Hunter', 117, 'Attack bonus against anyone standing between you and the prey (Siskur-Dah only)', '1 Essence', None),
          (4, 'Butchery', 117, 'Inflict Tilts with every blow while fighting several foes', '2 Essence', ('wits', 'brawl')),
          (5, 'Crimson Spasm', 117, 'Feed Essence into raw physical boosts, turn by turn', '1 Essence / turn', ('stamina', 'survival'))],
 'gibbous': [(1, 'War Howl', 118, 'Howl to give the pack bonus lethal damage', '1 Essence', ('presence', 'expression')),
             (2, 'Voice of Glory', 118, 'Glory bonus to Expression and Persuasion; better first impressions', '1 Essence', None),
             (3, 'Dream Hunter', 118, "Stalk the prey through its dreams (Siskur-Dah only)", '1 Essence', ('manipulation', 'empathy')),
             (4, 'Thousand-Throat Howl', 118, 'A howl of many voices that demoralizes the prey', '2 Essence', ('presence', 'intimidation')),
             (5, 'End of Story', 119, 'Name the prey as doomed; it suffers broad penalties for a day', '3 Essence', ('presence', 'persuasion'))],
 'half': [(1, 'Scent Beneath the Surface', 119, 'Sense whether the target is lying or deceiving', '1 Essence', ('wits', 'empathy')),
          (2, 'Binding Oath', 119, 'Seal an agreement so oath-breakers suffer penalties', '1 Essence', ('resolve', 'persuasion')),
          (3, 'Sly Hunter', 119, "Honor bonus when working the prey's social web (Siskur-Dah only)", '1 Essence', None),
          (4, 'Ties of Word and Promise', 120, 'Gain temporary social Merits through a group', '1 Essence / Merit dot', ('manipulation', 'persuasion')),
          (5, 'Ties of Blood and Bone', 120, 'Swap places with a packmate at a distance', '3 Essence', ('stamina', 'empathy'))],
 'new': [(1, 'Eviscerate', 120, 'Turn a surprise Brawl or Weaponry attack into a rote action', '1 Essence', None),
         (2, 'Slip Away', 120, 'Witnesses struggle to remember you for the scene', '1 Essence', None),
         (3, 'Relentless Hunter', 120, 'Cunning bonus to stealth and to getting past obstacles (Siskur-Dah only)', '1 Essence', None),
         (4, 'Divide and Conquer', 121, 'Lure one target away from its group', '1 Essence', ('manipulation', 'subterfuge')),
         (5, 'Breach', 121, 'Cross the Gauntlet anywhere, no locus needed', '3 Essence', ('wits', 'stealth'))],
}
RENOWN = {d['moon']: d['renown'].lower() for d in AUSP.values()}

def block():
    out = ['<div class="mgx"><input type="hidden" class="mgx-r" name="attr_moon_renown" value="0" />']
    for a, d in AUSP.items():
        m = d['moon']; r = RENOWN[m]
        rows = []
        for dots, name, page, summ, cost, pool in F[m]:
            k = f'mgf_{m}_{dots}'
            pd = f'{pool[0].title()} + {pool[1].title()} + {d["renown"]}' if pool else 'no roll'
            post = html.escape(f'&{{template:cofd-entry}} {{{{charname=@{{character_name}}}}}} {{{{gl_@{{game_line}}=1}}}} {{{{splat=@{{game_line}}}}}} {{{{kind={m.title()} Moon\'s Gift}}}} {{{{name={name}}}}} {{{{dots={"●" * dots}}}}} {{{{f_short={summ}}}}} {{{{f_costs={cost}}}}} {{{{f_pool={pd}}}}} {{{{f_source=W:tF 2E p. {page}}}}} {{{{f_notes=@{{{k}_notes}}}}}}', quote=True)
            roll = ''
            if pool:
                roll = ('<button type="roll" class="entry-roll" name="roll_' + k + '" title="Roll ' + pd + '" value="' + html.escape(
                    f'&{{template:cofd-entry}} {{{{charname=@{{character_name}}}}}} {{{{gl_@{{game_line}}=1}}}} {{{{splat=@{{game_line}}}}}} {{{{kind={m.title()} Moon\'s Gift}}}} {{{{name={name}}}}} {{{{f_short={summ}}}}} {{{{f_costs={cost}}}}} {{{{f_pool={pd}}}}} {{{{f_source=W:tF 2E p. {page}}}}} '
                    f'{{{{roll=[[{{((@{{{pool[0]}}}+@{{{pool[1]}}}+@{{renown_{r}}}+?{{@{{modifiermacro}}|0}}+@{{wound_penalty}})@{{rolltype}}', quote=True) + '">&#127922;</button>')
            rows.append(
                f'<div class="entry mgf mgf-{dots}"><input type="checkbox" class="entry-toggle" name="attr_{k}_show" value="1" title="Expand / collapse" />'
                f'<div class="entry-head"><button type="roll" class="entry-post" name="roll_{k}_post" title="Post to chat" value="{post}"><span class="entry-name">{name}</span></button>'
                f'<span class="mgf-lock" title="Unlocks at {d["renown"]} {dots}">locked</span>'
                f'<span class="mgf-dots" title="Unlocks at {d["renown"]} {dots} (primal Renown)"><span class="ren-ic ren-{d["renown"].lower()}"></span>{d["renown"]} {dots}</span><span class="entry-pool">{"" if not pool else pool[0][:3].title() + "+" + pool[1][:3].title() + "+" + d["renown"][:3]}</span>{roll}'
                f'<span class="entry-short mgf-short">{summ}</span><span class="entry-cost">{cost}</span></div>'
                f'<div class="entry-body"><div class="mgf-meta">Cost: {cost} · Dice pool: {pd} · W:tF 2E p. {page}</div>'
                f'<label class="wide">Notes<textarea name="attr_{k}_notes" rows="2"></textarea></label></div></div>')
        out.append(f'<div class="mgx-a mgx-{a.lower()}"><div class="mgx-head">{moon_svg(m)}<div><div class="mgx-title">{m.title()} Moon&#8217;s Gift</div>'
                   f'<div class="mgx-sub">{a} · unlocks one Facet per dot of {d["renown"]} · W:tF 2E {("p. " + str(F[m][0][2])) if F[m][0][2] == F[m][-1][2] else ("pp. " + str(F[m][0][2]) + "-" + str(F[m][-1][2]))}</div></div></div>'
                   f'<div class="entry-section pw mgx-list">{"".join(rows)}</div></div>')
    out.append('</div>')
    return ''.join(out)

def apply(h):
    a = '<div class="wolf-mgrow">'
    assert h.count(a) == 1
    return h.replace(a, block() + a, 1)

JS = r'''
        const MG_REN = %s;
        on("sheet:opened change:auspice change:renown_purity change:renown_glory change:renown_honor change:renown_wisdom change:renown_cunning", () =>
            getAttrs(["auspice", "renown_purity", "renown_glory", "renown_honor", "renown_wisdom", "renown_cunning"], (v) => {
                const r = MG_REN[v.auspice]; setAttrs({moon_renown: r ? (parseInt(v["renown_" + r]) || 0) : 0}, {silent: true}); }));
''' % __import__('json').dumps({a: d['renown'].lower() for a, d in AUSP.items()})

def css():
    o = ['.charsheet .sheet-mgx-a { display: none; margin: 6px 0; }',
         '.charsheet .sheet-wolf-mg, .charsheet .sheet-wolf-mgrow { display: none !important; }',
         '.charsheet .sheet-mgx-head { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; padding-top: 6px; overflow: visible; }',
         '.charsheet .sheet-mgx-head .sheet-moon-img { width: 64px; height: 64px; flex: 0 0 64px; margin: 0; }',
         '.charsheet .sheet-mgx-title { font-weight: bold; font-size: 15px; letter-spacing: .5px; }',
         '.charsheet .sheet-mgx-sub { font-size: 11px; opacity: .8; }',
         '.charsheet .sheet-mgx .sheet-mgf-dots { grid-row: 1 !important; grid-column: 3 !important; text-align: right; font-size: 9px; letter-spacing: 1px; color: #e08a3c; white-space: nowrap; }',
         '.charsheet .sheet-mgx .sheet-mgf-lock { grid-row: 1 !important; grid-column: 2 !important; display: none; font: bold 9px/13px Arial, sans-serif; text-transform: uppercase; padding: 0 4px; border-radius: 7px; border: 1px solid currentColor; opacity: .75; }',
         '.charsheet .sheet-mgx span.sheet-mgf-short { grid-row: 2 !important; grid-column: 1 !important; font-style: italic; font-size: 11px; opacity: .85; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }',
         '.charsheet .sheet-mgx .sheet-entry > .sheet-entry-head > .sheet-entry-cost { grid-row: 2 !important; }',
         '.charsheet .sheet-mgx .sheet-entry > .sheet-entry-head > * { white-space: normal !important; overflow: visible !important; text-overflow: clip !important; overflow-wrap: break-word; height: auto !important; min-width: 0; }',
         '.charsheet .sheet-mgx .sheet-entry > .sheet-entry-head { overflow: visible !important; height: auto !important; max-height: none !important; grid-template-columns: minmax(0,1fr) 70px 76px 22px !important; }',
         '.charsheet .sheet-mgx .sheet-entry > .sheet-entry-head > .sheet-entry-pool { grid-row: 2 !important; grid-column: 3 / 5 !important; line-height: 14px !important; text-align: right; }',
         '.charsheet .sheet-mgx .sheet-entry > .sheet-entry-head > .sheet-entry-cost { grid-row: 2 !important; grid-column: 2 !important; line-height: 14px !important; text-align: right; }',
         '.charsheet .sheet-mgx span.sheet-mgf-short { line-height: 14px; align-self: start; }',
         '.charsheet .sheet-mgx, .charsheet .sheet-mgx-a, .charsheet .sheet-mgx .sheet-entry-section, .charsheet .sheet-mgx .sheet-entry { overflow: visible !important; height: auto !important; max-height: none !important; }',
         '.charsheet .sheet-midpane .sheet-leon-pane { overflow-y: visible; }',
         '.charsheet .sheet-mgf-meta { font-size: 11px; margin: 2px 0 4px; grid-column: 1 / -1; }']
    for a, d in AUSP.items():
        o.append(f'.charsheet input.sheet-wolf-a[value="{a}"] ~ .sheet-mgx .sheet-mgx-{a.lower()} {{ display: block; }}')
    for n in range(0, 5):
        locked = ', '.join(f'.charsheet input.sheet-mgx-r[value="{n}"] ~ .sheet-mgx-a .sheet-mgf-{k}' for k in range(n + 1, 6))
        o.append(f'{locked} {{ opacity: .45; }}')
        o.append(', '.join(f'.charsheet input.sheet-mgx-r[value="{n}"] ~ .sheet-mgx-a .sheet-mgf-{k} .sheet-mgf-lock' for k in range(n + 1, 6)) + ' { display: inline-block; }')
    return '\n'.join(o)
