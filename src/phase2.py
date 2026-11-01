"""Phase-2 splats: Mage, Promethean, Changeling, Geist, Mummy, Demon, Beast, Deviant, Changing Breeds."""
SPLATS2 = [('mage2', 'Mage: The Awakening', 'mage-the-awakening', 'mage'),
           ('promethean2', 'Promethean: The Created', 'promethean-the-created', 'promethean'),
           ('changeling2', 'Changeling: The Lost', 'changeling-the-lost', 'changeling'),
           ('geist2', 'Geist: The Sin-Eaters', 'geist-the-sin-eaters', 'geist'),
           ('mummy2', 'Mummy: The Curse', 'mummy-the-curse', 'mummy'),
           ('demon', 'Demon: The Descent', 'demon-the-descent', 'demon'),
           ('beast', 'Beast: The Primordial', 'beast-the-primordial', 'beast'),
           ('deviant-the-renegades', 'Deviant: The Renegades', 'deviant-the-renegades', 'deviant'),
           ('breeds2', 'Werewolf: Changing Breeds', 'changing-breeds', 'breeds')]

def sections(entry, T, SRC, DESC, NOTES):
    A = ('action', 'Action / duration', 'text'); C = ('cost', 'Cost', 'text')
    g = lambda cls, body: f'<div class="game-line {cls}">' + ''.join(body) + '</div>'
    return '\n'.join([
        g('mage2', [entry('rotes', 'rotes', 'Rotes', [('arcanum', 'Arcanum', 'text'), ('level', 'Level', 'text'), ('rote_skill', 'Rote skill', 'text'), ('order', 'Order', 'text'), C, A, SRC, DESC, NOTES], rating=None),
                    entry('praxes', 'praxes', 'Praxes', [('arcanum', 'Arcanum', 'text'), ('level', 'Level', 'text'), SRC, DESC, NOTES], rating=None),
                    entry('activespells', 'active-spells', 'Active Spells', [('arcanum', 'Arcanum', 'text'), ('potency', 'Potency', 'text'), ('duration', 'Duration', 'text'), ('scale', 'Scale', 'text'), ('target', 'Target', 'text'), ('reach', 'Reach used', 'text'), NOTES], rating=None, pool=False),
                    entry('obsessions', 'obsessions', 'Obsessions', [DESC], rating=None, pool=False)]),
        g('promethean2', [entry('transmutations', 'transmutations', 'Transmutations', [('category', 'Transmutation / Alembic', 'text'), C, A, SRC, DESC, NOTES], rating=None),
                          entry('bestowments', 'bestowments', 'Bestowments', [C, A, SRC, DESC, NOTES], rating=None),
                          entry('milestones', 'milestones', 'Milestones', [('role', 'Role', 'text'), ('achieved', 'Achieved', 'check'), DESC], rating=None, pool=False)]),
        g('changeling2', [entry('contracts', 'contracts', 'Contracts', [('regalia', 'Regalia / Court', 'text'), ('ctype', 'Common / Royal', 'select:Common;Royal;Court;Goblin'), C, A, ('loophole', 'Loophole', 'text'), ('seeming_benefit', 'Seeming benefit', 'textarea'), SRC, DESC, NOTES], rating=None),
                          entry('pledges', 'pledges', 'Pledges', [('ptype', 'Type', 'select:Sealing;Oath;Bargain'), ('parties', 'Parties', 'text'), ('boons', 'Boons', 'text'), ('penalty', 'Penalty', 'text'), ('duration', 'Duration', 'text'), NOTES], rating=None, pool=False),
                          entry('goblincontracts', 'goblin-contracts', 'Goblin Contracts', [C, A, ('debt', 'Goblin Debt', 'text'), SRC, DESC, NOTES], rating=None)]),
        g('geist2', [entry('keys', 'keys', 'Keys', [('unlock', 'Unlock attribute', 'text'), ('doom', 'Doom', 'textarea'), DESC], rating=None, pool=False),
                     entry('ceremonies', 'ceremonies', 'Ceremonies', [('pool_text', 'Ceremony pool', 'text'), A, SRC, DESC, NOTES]),
                     entry('mementos', 'mementos', 'Mementos', [('key', 'Key', 'text'), ('mtype', 'Type', 'select:Charm;Deathmask;Vanitas;Other'), DESC, NOTES], rating=None, pool=False)]),
        g('mummy2', [entry('utterances', 'utterances', 'Utterances', [('tier', 'Tier', 'select:Lesser;Greater;Supreme;All'), ('pillar', 'Pillar / cost', 'text'), A, SRC, DESC, NOTES], rating=None),
                     entry('affinities', 'affinities', 'Affinities', [('pillar', 'Pillar', 'text'), C, SRC, DESC, NOTES], rating=None),
                     entry('vessels', 'vessels', 'Vessels / Relics', [('vtype', 'Type', 'text'), ('sekhem', 'Sekhem', 'text'), DESC, NOTES], pool=False)]),
        g('demon', [entry('embeds', 'embeds', 'Embeds', [('category', 'Incarnation', 'text'), A, SRC, DESC, NOTES], rating=None),
                    entry('exploits', 'exploits', 'Exploits', [C, A, SRC, DESC, NOTES], rating=None),
                    entry('covers', 'covers', 'Covers', [('cover_identity', 'Identity', 'text'), ('compromise', 'Compromise notes', 'textarea'), DESC]),
                    entry('pacts', 'pacts', 'Pacts', [('parties', 'Party', 'text'), ('terms', 'Terms', 'textarea'), ('rider', 'Riders / cost', 'text'), NOTES], rating=None, pool=False)]),
        g('beast', [entry('atavisms', 'atavisms', 'Atavisms', [('family', 'Family', 'text'), C, A, SRC, DESC, NOTES], rating=None),
                    entry('nightmares', 'nightmares', 'Nightmares', [C, A, SRC, DESC, NOTES], rating=None)]),
        g('werewolf breeds2', [entry('favors', 'favors-aspects', 'Favors & Aspects', [('ftype', 'Type', 'select:Favor;Aspect'), C, A, SRC, DESC, NOTES], rating=None),
                      entry('bspecials', 'special-abilities', 'Special Abilities', [A, SRC, DESC, NOTES], rating=None),
                      entry('skillpro', 'skill-proficiencies', 'Skill Proficiencies', [('skill', 'Skill', 'text'), DESC], rating=None, pool=False),
                      entry('btotem', 'totem', 'Totem', [('attributes', 'Power / Finesse / Resistance', 'text'), ('influences', 'Influences / Numina', 'textarea'), ('ban', 'Ban', 'text'), ('bonuses', 'Bonuses', 'textarea')], rating=None, pool=False, default_open=False),
                      f'<div class="kt"><label>{T("kt-set","Kuruth Triggers (set)")}<input type="text" name="attr_kt_set" /></label><label>{T("kt-active","Kuruth Triggers (active)")}<input type="text" name="attr_kt_active" /></label></div>']),
    ])

def header_html(T):
    return (f'<div class="game-line werewolf breeds2 breeds-head"><label>{T("accord","Accord")}<input type="text" name="attr_accord" /></label>'
            f'<label>{T("breed","Breed")}<input type="text" name="attr_breed" /></label><label>{T("species","Species")}<input type="text" name="attr_species" /></label></div>')

def logos(h, IMG):
    for k in ['mage', 'promethean', 'changeling', 'geist', 'mummy']:
        h = h.replace(f'<img class="game-line {k}" src=', f'<img class="game-line {k}1" src=', 1)
    for t, art in [('mage2', 'mage'), ('promethean2', 'promethean'), ('changeling2', 'changeling'), ('geist2', 'geist'), ('mummy2', 'mummy'), ('breeds2', 'breeds')]:
        h = h.replace('<img class="game-line werewolf2 leon-logo"', f'<img class="game-line {"werewolf " if t == "breeds2" else ""}{t} leon-logo" src="{IMG}/{art}-logo.png">\n        <img class="game-line werewolf2 leon-logo"', 1)
    import re
    h = re.sub(r'<img class="game-line demon" src="[^"]*">', f'<img class="game-line demon leon-logo" src="{IMG}/demon-logo.png">', h)
    h = re.sub(r'<img class="game-line deviant-the-renegades" src="[^"]*">', f'<img class="game-line deviant-the-renegades leon-logo" src="{IMG}/deviant-logo.png">', h)
    h = h.replace('<img class="game-line werewolf2 leon-logo"', f'<img class="game-line beast leon-logo" src="{IMG}/beast-logo.png">\n        <img class="game-line werewolf2 leon-logo"', 1)
    return h

def worker(W):
    for fn in ['getGameLine', 'getEdition']:
        pass
    W = W.replace('                case "werewolf2":\n                    return "werewolf";', '                case "werewolf2":\n                case "breeds2":\n                    return "werewolf";', 1)
    W = W.replace('                case "deviant-the-renegades":\n                    return 2;', '                case "deviant-the-renegades":\n                case "breeds2":\n                    return 2;', 1)
    W = W.replace('"mortal2-organization","geist2-organization"', '"mortal2-organization","geist2-organization","breeds2"', 1)
    return W

def css(IMG):
    out = []
    for t, art in [('mage2', 'mage'), ('promethean2', 'promethean'), ('changeling2', 'changeling'), ('geist2', 'geist'), ('mummy2', 'mummy'), ('demon', 'demon'), ('beast', 'beast'), ('deviant-the-renegades', 'deviant'), ('breeds2', 'breeds')]:
        out.append(f'input.sheet-type[value="{t}"] ~ .sheet-background-image::after {{ background: url(\'{IMG}/{art}-bgtop.jpg\') top center / 100% auto no-repeat, url(\'{IMG}/{art}-bgbot.jpg\') bottom center / 100% auto no-repeat, url(\'{IMG}/{art}-bgmid.jpg\') center top / 100% auto repeat-y; }}')
    out.append('input.sheet-type[value="breeds2"] ~ * .sheet-game-line.sheet-werewolf2:not(.sheet-breeds2), input.sheet-type[value="breeds2"] ~ * .sheet-game-line.sheet-werewolf1:not(.sheet-breeds2) { display: none; }')
    out.append('input.sheet-type:not([value="breeds2"]) ~ * .sheet-game-line.sheet-breeds2:not(.sheet-werewolf2) { display: none; }')
    out.append('.sheet-breeds-head { display: flex; gap: 8px; margin: 4px 0; } .sheet-breeds-head label { flex: 1; font-weight: bold; } .sheet-kt label { display: block; font-weight: bold; }')
    return '\n'.join(out)
