"""Hurt Locker (CofD 2E, Onyx Path) weapon / armor / explosive support for the Weapons & Attacks entries.
Source: Hurt Locker PDF (books/HL.pdf); page refs are PDF pages. See HURT_LOCKER_AUDIT.md.
Table corrections (verified from rendered pages, see audit section 5):
 - Light/Heavy Revolver rows are column-shifted in the printed table (p.134): read as
   Light Revolver +1 Medium/Medium Init 0 Str 2 Size 1 ..; Heavy Revolver +2 Long/Low Init -2 Str 3 Size 1 ..
 - Smoke / Thermite / White Phosphorus grenade rows are shifted one column left (p.136): Init blank -> 0.
"""
import html, json

# ---- tags (p.142-143) ----
TAGS = [('t_8again', '8-again'), ('t_9again', '9-again'), ('t_accurate', 'Accurate'), ('t_inaccurate', 'Inaccurate'),
        ('t_bleed', 'Bleed'), ('t_brawl', 'Brawl'), ('t_concealed', 'Concealed'), ('t_fragile', 'Fragile'),
        ('t_grapple', 'Grapple'), ('t_guard', 'Guard'), ('t_incendiary', 'Incendiary'), ('t_knockdown', 'Knockdown'),
        ('t_reach', 'Reach'), ('t_slow', 'Slow'), ('t_stun', 'Stun'), ('t_thrown', 'Thrown'), ('t_thrown_a', 'Thrown (A)'),
        ('t_twohanded', 'Two-Handed'), ('t_nodmg', 'No bonus dmg')]
TAG_HELP = {'t_8again': 'Re-roll 8, 9 and 10', 't_9again': 'Re-roll 9 and 10', 't_accurate': '+1 to attack rolls (incl. grapple)',
            't_inaccurate': '-1 to attack rolls', 't_bleed': 'Double weapon bonus for the Bleeding Tilt', 't_brawl': 'Attack with Brawl (still lethal)',
            't_concealed': 'Shield: +Size to Defense if not used to attack; Size is concealment vs ranged', 't_fragile': '-1 Durability',
            't_grapple': 'Add weapon bonus to grapple pools', 't_guard': '+1 Defense while wielded', 't_incendiary': 'Inflicts the Burning Tilt',
            't_knockdown': 'Double weapon bonus for the Knocked Down Tilt', 't_reach': '+1 Defense vs smaller weapons/unarmed; -1 in grapples',
            't_slow': 'Ranged only: defender gets full Defense', 't_stun': 'Double weapon bonus for the Stunned Tilt',
            't_thrown': 'Can be thrown', 't_thrown_a': 'Thrown, aerodynamic (+1 range band)', 't_twohanded': 'Two hands; one-handed at Strength req. +1',
            't_nodmg': 'Bonus successes do not add to damage (stun gun)'}

# ---- presets: (id, label, dict) ; keys: wtype dmg dt init str size av rng cap tags ap enh attr skill blast force deliv note ----
def P(id, label, wtype, dmg, init, st, size, av, tags='', rng='', cap='na', dt='L', ap=0, enh='', attr='auto', skill='auto', blast=0, force=0, deliv='thrown', note='', extra=''):
    return (id, label, dict(wtype=wtype, damage=str(dmg), initiative=str(init), str_req=str(st), wsize=str(size), avail=str(av),
                            max_range=rng or ('close' if wtype in ('melee', 'unarmed') else 'auto'), capacity=cap, dtype=dt, piercing=str(ap), enhance=enh,
                            atk_attr=attr, atk_skill=skill, blast=str(blast), force=str(force), expl_delivery=deliv, tags=[t for t in tags.split() if t],
                            note=note, tags_extra=extra))
PRESETS = [
    # Melee - bladed (p.139)
    P('battle_axe', 'Battle Axe', 'melee', 3, -4, 3, 3, 3, 't_9again t_twohanded'),
    P('fire_axe', 'Fire Axe', 'melee', 2, -4, 3, 3, 2, 't_9again t_twohanded'),
    P('great_sword', 'Great Sword', 'melee', 4, -5, 4, 3, 4, 't_9again t_twohanded'),
    P('hatchet', 'Hatchet', 'melee', 1, -2, 1, 1, 2),
    P('knife_small', 'Knife, Small', 'melee', 0, 0, 1, 1, 1, 't_thrown_a'),
    P('knife_hunting', 'Knife, Hunting', 'melee', 1, -1, 1, 2, 2, enh='Crafts or Survival'),
    P('machete', 'Machete', 'melee', 2, -2, 2, 2, 2),
    P('rapier', 'Rapier', 'melee', 1, -2, 1, 2, 2, ap=1),
    P('sword', 'Sword', 'melee', 3, -3, 2, 3, 3, note='+1 Durability (katana) or +1 Initiative (long sword).'),
    # Melee - blunt
    P('brass_knuckles', 'Brass Knuckles', 'melee', 0, 0, 1, 1, 1, 't_brawl'),
    P('metal_club', 'Metal Club', 'melee', 2, -2, 2, 2, 1, 't_stun'),
    P('nightstick', 'Nightstick', 'melee', 1, -1, 2, 2, 2, 't_stun'),
    P('nunchaku', 'Nunchaku', 'melee', 1, 1, 2, 2, 2, 't_stun', note='-1 Damage and Initiative without Dexterity 3+.'),
    P('sap', 'Sap', 'melee', 0, -1, 2, 2, 1, 't_stun'),
    P('sledgehammer', 'Sledgehammer', 'melee', 3, -4, 3, 3, 1, 't_knockdown t_stun'),
    # Melee - exotic
    P('catchpole', 'Catchpole', 'melee', 0, -3, 2, 2, 1, 't_grapple t_reach', note='Called shot to the head; escape at extra -2 (max -5).'),
    P('chain', 'Chain / Kusari Gama (chain)', 'melee', 1, -3, 2, 2, 1, 't_grapple t_inaccurate t_reach'),
    P('chainsaw', 'Chainsaw', 'melee', 3, -6, 4, 3, 3, 't_bleed t_inaccurate t_twohanded'),
    P('shield_small', 'Shield (small)', 'melee', 0, -2, 2, 2, 2, 't_concealed', dt='B'),
    P('shield_large', 'Shield (large)', 'melee', 2, -4, 3, 3, 2, 't_concealed', dt='B'),
    P('stake', 'Stake', 'melee', 0, -4, 1, 1, 0),
    P('stun_gun_melee', 'Stun Gun (melee)', 'melee', 0, -1, 1, 1, 1, 't_stun t_nodmg', dt='B'),
    P('tiger_claws', 'Tiger Claws', 'melee', 1, -1, 2, 2, 2, 't_brawl'),
    P('whip', 'Whip', 'melee', 0, -2, 1, 2, 1, 't_grapple t_stun', dt='B', attr='dexterity', note='Bashing; metal-tipped = Damage 0 lethal. Can disarm (called shot -1 less).'),
    P('spear', 'Spear', 'melee', 2, -2, 2, 4, 1, 't_reach t_twohanded'),
    P('staff', 'Staff', 'melee', 1, -1, 2, 4, 1, 't_knockdown t_reach t_twohanded', dt='B'),
    # Improvised (p.140)
    P('blowtorch', 'Blowtorch', 'melee', 0, -2, 2, 2, 2, 't_incendiary', ap=2, note='Attacker and target take -1 Defense or both suffer Blinded. Fire damage.'),
    P('board_nail', 'Board w/ Nail', 'melee', 1, -3, 2, 2, 0, 't_fragile t_stun'),
    P('improv_shield', 'Improvised Shield', 'melee', 0, -4, 2, 2, 1, 't_concealed', dt='B'),
    P('nail_gun', 'Nail Gun (contact)', 'melee', 0, -2, 2, 2, 1, 't_inaccurate', ap=1, attr='strength', skill='firearms', note='Strength + Firearms; Defense applies. Can pin (Pinned Tilt).'),
    P('shovel', 'Shovel', 'melee', 1, -3, 2, 2, 1, 't_knockdown'),
    P('tire_iron', 'Tire Iron', 'melee', 1, -3, 2, 2, 2, 't_guard t_inaccurate'),
    P('fists', 'Unarmed (fists)', 'unarmed', 0, 0, 0, 0, 0, dt='B'),
    # Ranged (p.134)
    P('light_pistol', 'Light Pistol', 'ranged', 1, 0, 2, 1, 2, rng='long', cap='medium'),
    P('heavy_pistol', 'Heavy Pistol', 'ranged', 2, -2, 3, 1, 3, rng='long', cap='medium'),
    P('light_revolver', 'Light Revolver', 'ranged', 1, 0, 2, 1, 2, rng='medium', cap='medium', note='Revolver: +1 to fix. (Table row corrected, see audit.)'),
    P('heavy_revolver', 'Heavy Revolver', 'ranged', 2, -2, 3, 1, 2, rng='long', cap='low', note='Revolver: +1 to fix. (Table row corrected, see audit.)'),
    P('smg_small', 'SMG, small', 'ranged', 1, -2, 2, 1, 3, rng='medium', cap='high'),
    P('smg_heavy', 'SMG, heavy', 'ranged', 2, -3, 3, 2, 3, rng='medium', cap='high'),
    P('rifle', 'Rifle', 'ranged', 4, -5, 2, 3, 2, rng='extreme', cap='low'),
    P('rifle_big', 'Rifle, Big Game', 'ranged', 5, -5, 3, 4, 5, 't_stun', rng='extreme', cap='low', note='Heavy recoil: unbraced = 1 bashing + Knocked Down.'),
    P('assault_rifle', 'Assault Rifle', 'ranged', 3, -3, 3, 3, 3, 't_9again', rng='long', cap='high'),
    P('shotgun', 'Shotgun', 'ranged', 3, -4, 3, 2, 2, 't_9again', rng='medium', cap='low'),
    P('short_bow', 'Short Bow', 'bow', 2, -3, 2, 3, 2, rng='medium', cap='low'),
    P('long_bow', 'Long Bow', 'bow', 3, -4, 3, 4, 2, rng='medium', cap='low'),
    P('crossbow', 'Crossbow', 'ranged', 2, -5, 3, 3, 3, rng='long', cap='low', note='Always Firearms. Can stake (-3, 5 damage).'),
    P('pepper_spray', 'Pepper Spray', 'ranged', 0, 0, 1, 1, 1, 't_slow', rng='close', cap='low', dt='B'),
    P('stun_gun_ranged', 'Stun Gun / Taser (ranged)', 'ranged', 0, -1, 1, 1, 1, 't_slow t_stun t_nodmg', rng='close', cap='medium', dt='B'),
    P('flamer_civ', 'Flamethrower, civilian', 'ranged', 0, -4, 3, 4, 3, 't_incendiary', rng='short', cap='high', note='Fire Damage 2+2 (max 4) + Burning; -2 without Heavy Weapons specialty; long burst ignores Defense; armor only if flame-resistant.'),
    P('flamer_mil', 'Flamethrower, military', 'ranged', 0, -5, 3, 4, 5, 't_incendiary', rng='medium', cap='high', note='Fire Damage 2+2 (max 4) + Burning; -2 without Heavy Weapons specialty; long burst ignores Defense; armor only if flame-resistant.'),
    # Explosives - hand grenades (p.136)
    P('frag', 'Grenade, Frag (standard)', 'explosive', 2, 0, 2, 1, 4, 't_knockdown t_stun t_thrown_a', blast=10, force=3),
    P('frag_heavy', 'Grenade, Frag (heavy)', 'explosive', 3, -1, 2, 1, 4, 't_knockdown t_stun t_thrown_a', blast=5, force=4),
    P('molotov', 'Molotov Cocktail', 'explosive', 1, -2, 2, 2, 1, 't_incendiary t_thrown', blast=3, force=2, note='Light one turn, throw the next; bursts on impact.'),
    P('pipe_bomb', 'Pipe Bomb', 'explosive', 1, -1, 2, 1, 1, 't_inaccurate t_stun t_thrown', blast=5, force=2, note='Light fuse (action), throw next turn.'),
    P('smoke', 'Grenade, Smoke', 'explosive', 0, 0, 2, 1, 2, 't_thrown_a', blast=10, force=0, extra='Concealment', note='Primary: severe Blinded; secondary: lesser Blinded; attacks into smoke -4. 40 turns.'),
    P('stun_gren', 'Grenade, Stun (flashbang)', 'explosive', 0, 0, 2, 1, 2, 't_knockdown t_stun t_thrown_a', blast=5, force=2, note='No damage: Stamina + Resolve -4 (GZ -5, secondary -2) or Blinded, Deafened, Stunned.'),
    P('thermite', 'Grenade, Thermite', 'explosive', 3, 0, 2, 1, 4, 't_incendiary t_thrown_a', ap=8, blast=5, force=4, note='Inferno chemical fire (~6 lethal/turn); AP applies to whole blast.'),
    P('white_phos', 'Grenade, White Phosphorus', 'explosive', 3, 0, 2, 1, 4, 't_incendiary t_thrown_a', ap=3, blast=5, force=4, extra='Concealment', note='Also a smoke grenade; AP applies to whole blast.'),
    # Grenade launchers + ammo (p.137); launcher adds no Damage bonus, ammo Damage listed
    P('gl_he', 'Grenade Launcher (stand-alone), HE', 'explosive', 3, 0, 3, 3, 4, 't_knockdown', rng='long', cap='low', blast=10, force=4, deliv='fired', note='Big-game recoil. Min arming 15 m.'),
    P('gl_hedp', 'Grenade Launcher (stand-alone), HEDP', 'explosive', 2, 0, 3, 3, 4, 't_knockdown', ap=4, rng='long', cap='low', blast=10, force=3, deliv='fired', note='Big-game recoil. Min arming 15 m.'),
    P('gl_buck', 'Grenade Launcher (stand-alone), Buckshot', 'explosive', 1, 0, 3, 3, 4, 't_knockdown', rng='long', cap='low', blast=10, force=4, deliv='fired', note='Big-game recoil.'),
    P('gl_baton', 'Grenade Launcher (stand-alone), Baton', 'ranged', 1, 0, 3, 3, 2, 't_knockdown t_stun', rng='long', cap='low', dt='B', note='Baton round: no explosion.'),
    P('ugl_he', 'Under-Barrel Launcher, HE', 'explosive', 3, 0, 2, 2, 4, 't_knockdown', rng='long', cap='low', blast=10, force=4, deliv='fired', note='Min arming 15 m.'),
    P('agl_he', 'Automatic Grenade Launcher, HE', 'explosive', 3, 0, 0, 4, 5, 't_knockdown', rng='extreme', cap='high', blast=10, force=4, deliv='fired', note='Tripod/vehicle mounted. Min arming 15 m.'),
]
PRESET_MAP = {i: d for i, l, d in PRESETS}
PRESET_LABEL = {i: l for i, l, d in PRESETS}
GROUPS = [('Melee', [p for p in PRESETS if p[2]['wtype'] in ('melee', 'unarmed')]), ('Ranged', [p for p in PRESETS if p[2]['wtype'] in ('ranged', 'bow')]),
          ('Explosive', [p for p in PRESETS if p[2]['wtype'] == 'explosive'])]

ARMOR = [('', '- custom -', None),
         ('reinforced', 'Reinforced Clothing', (1, 0, 1, 0, 0, 'Torso, arms, legs')), ('sports', 'Sports Gear', (2, 0, 2, -1, -1, 'Torso, arms, legs')),
         ('kevlar', 'Kevlar Vest', (1, 3, 1, 0, 0, 'Torso')), ('flak', 'Flak Jacket', (2, 4, 1, -1, 0, 'Torso, arms')),
         ('riot', 'Full Riot Gear', (3, 5, 2, -2, -1, 'Torso, arms, legs')), ('bomb', 'Bomb Suit', (4, 6, 3, -5, -4, 'Torso, arms, head')),
         ('leather', 'Leather (hard)', (2, 0, 2, -1, 0, 'Torso, arms')), ('lorica', 'Lorica Segmentata', (2, 2, 3, -2, -3, 'Torso')),
         ('chain', 'Chainmail', (3, 1, 3, -2, -2, 'Torso, arms')), ('plate', 'Plate', (4, 2, 3, -2, -3, 'Torso, arms, legs'))]

def opts(pairs): return ''.join(f'<option value="{v}">{html.escape(str(l))}</option>' for v, l in pairs)
def preset_select():
    o = '<option value="">- custom -</option>'
    for g, ps in GROUPS:
        o += f'<optgroup label="{g}">' + ''.join(f'<option value="{i}">{html.escape(l)}</option>' for i, l, d in ps) + '</optgroup>'
    return o

DOTS = ['-', '1', '2', '3', '4', '5']
FIELDS = [
    ('preset', 'Preset (Hurt Locker)', 'RAW'),
    ('wtype', 'Type', 'select:melee=Melee;unarmed=Unarmed;thrown=Thrown;ranged=Firearm / ranged;bow=Bow;explosive=Explosive'),
    ('atk_attr', 'Attribute', 'select:auto=Auto (by Type);strength=Strength;dexterity=Dexterity;wits=Wits;presence=Presence;manipulation=Manipulation'),
    ('atk_skill', 'Skill', 'select:auto=Auto (by Type);brawl=Brawl;weaponry=Weaponry;firearms=Firearms;athletics=Athletics'),
    ('damage', 'Damage', 'select:' + ';'.join(f'{i}=+{i}' for i in range(0, 16))),
    ('dtype', 'Damage type', 'select:L=Lethal;B=Bashing;A=Aggravated'),
    ('initiative', 'Initiative', 'select:1=+1;0=0;-1=-1;-2=-2;-3=-3;-4=-4;-5=-5;-6=-6'),
    ('str_req', 'Strength req.', 'select:0=-;1=1;2=2;3=3;4=4;5=5'),
    ('wsize', 'Size', 'select:0=0;1=1;2=2;3=3;4=4;5=5'),
    ('avail', 'Availability', 'select:0=-;1=1 dot;2=2 dots;3=3 dots;4=4 dots;5=5 dots'),
    ('max_range', 'Max range', 'select:auto=Auto;close=Close;short=Short;medium=Medium;long=Long;extreme=Extreme'),
    ('capacity', 'Capacity', 'select:na=- (none);single=Single Shot;low=Low;medium=Medium;high=High'),
    ('range_txt', 'Range (custom, e.g. 20/40/80)', 'text'),
    ('clip_txt', 'Clip (custom, e.g. 7+1)', 'text'),
    ('piercing', 'Piercing', 'select:' + ';'.join(f'{i}={i if i else "-"}' for i in range(9))),
    ('expl_delivery', 'Delivery', 'select:thrown=Thrown;fired=Fired (launcher);placed=Placed'),
    ('blast', 'Blast (m)', 'select:' + ';'.join(f'{i}={i if i else "-"}' for i in (0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30))),
    ('force', 'Force', 'select:' + ';'.join(f'{i}={i if i else "-"}' for i in range(9))),
    ('other_mod', 'Other mods (dice)', 'number'),
    ('onehanded', 'Used one-handed', 'check'),
    ('enhance', 'Enhance (Skill)', 'text'),
    ('tags_extra', 'Other tags', 'text'),
    ('notes', 'Notes', 'textarea')]
CLS = {'max_range': 'hl-r', 'capacity': 'hl-r', 'expl_delivery': 'hl-x', 'blast': 'hl-x', 'force': 'hl-x', 'onehanded': 'hl-2h'}

MACRO = ('&{template:cofd-entry} {{splat=@{game_line}}} {{kind=Attack}} {{name=@{name}}} {{f_pool=@{atk_breakdown}}} {{f_wtype=@{atk_wtxt}}} '
         '{{f_spec=Specialty +?{Specialty applies?|No,0|Yes,1}}} {{f_mod=Modifier ?{@{modifiermacro}|0}}} {{f_def=Target Defense -?{@{atk_defq}|@{atk_def_default}}}} '
         '{{f_rng=@{atk_rngshow}}} {{f_burst=@{atk_burstshow}}} '
         '{{roll=[[{((@{atk_base}+?{Specialty applies?|No,0|Yes,1}+?{@{modifiermacro}|0}-?{@{atk_defq}|@{atk_def_default}}+@{atk_rangeq}+@{atk_burstq}+@{wp_dice})@{atk_rt} '
         '{{f_damage=@{atk_dmgtxt}}} {{dmg_@{dtype}=1}} {{f_range=@{atk_maxtxt}}} {{f_ammo=@{atk_ammo}}} {{f_tags=@{atk_tags}}} {{f_ap=@{atk_ap}}} '
         '{{f_tilt=@{atk_tilt}}} {{f_force=@{atk_force}}} {{f_blast=@{atk_blast}}}')
HIDDEN = {'atk_base': '0', 'atk_rt': '@{rolltype_eff}', 'atk_def_default': '0', 'atk_defq': 'Target Defense', 'atk_rangeq': '0', 'atk_burstq': '0',
          'atk_rngshow': '', 'atk_burstshow': '', 'atk_dmgtxt': 'Successes + 0', 'atk_maxtxt': '', 'atk_ammo': '', 'atk_tags': '', 'atk_ap': '',
          'atk_tilt': '', 'atk_force': '', 'atk_blast': '', 'atk_wtxt': 'Melee', 'hl_mig': '0', 'atk_breakdown': 'Attack pool (reopen the sheet to compute)'}
TPL_EXTRA = [('f_rng', 'Range mod'), ('f_burst', 'Burst'), ('f_ammo', 'Ammo'), ('f_ap', 'Piercing'), ('f_tilt', 'Tilts'), ('f_force', 'Force'), ('f_blast', 'Blast')]

def weapons_entry(entry, T):
    hdr = ('<span class="hl-tagsum" name="attr_atk_tags"></span>'
           '<button type="roll" class="hl-poolbtn" name="roll_attack" title="Roll attack (pool shown; damage is added on successes)" value="' + html.escape(MACRO, quote=True) + '"><span class="entry-pool hl-pool" name="attr_atk_short"></span></button>')
    f = [x for x in FIELDS if x[2] != 'RAW']
    s = entry('weapons', 'weapons', 'Weapons & Attacks', f, rating=None, pool=False, default_open=False, extra_header=hdr)
    # body: hidden mirrors for CSS show/hide, preset select, tag chips
    mirror = ('<input type="hidden" class="hl-wt" name="attr_wtype" value="melee" />'
              '<input type="hidden" class="hl-2hv" name="attr_t_twohanded" value="0" />')
    pre = f'<label class="hl-preset">{T("lbl-preset", "Preset (Hurt Locker)")}<select name="attr_preset">{preset_select()}</select></label>'
    s = s.replace('<div class="entry-body">', '<div class="entry-body">' + mirror, 1)
    s = s.replace('<label class="wide"><span data-i18n="name">', pre + '<label class="hl-name"><span data-i18n="name">', 1)
    for a, c in CLS.items():
        k = 'lbl-' + a.replace('_', '-')
        assert f'<label><span data-i18n="{k}">' in s, a
        s = s.replace(f'<label><span data-i18n="{k}">', f'<label class="{c}"><span data-i18n="{k}">', 1)
    # tags: hidden flags + removable pills for active ones + an 'add tag' select (Rogue Trader-style qualities line)
    flags = ''.join(f'<input type="hidden" class="hl-tf hl-tf-{a}" name="attr_{a}" value="0" />' for a, l in TAGS)
    flags += '<input type="hidden" class="hl-tf-ap" name="attr_piercing" value="0" />'
    pills = ''.join(f'<span class="hl-pill hl-pill-{a}" title="{html.escape(TAG_HELP[a])}">{html.escape(l)}<button type="action" class="hl-pill-x" name="act_tagrm_{a}" title="Remove">x</button></span>' for a, l in TAGS)
    pills += '<span class="hl-pill hl-pill-ap" title="Piercing: ignores this much armor">Piercing <span name="attr_piercing"></span><button type="action" class="hl-pill-x" name="act_tagrm_piercing" title="Remove">x</button></span>'
    addsel = ('<select class="hl-tagadd" name="attr_tag_add" title="Add a tag"><option value="" selected>+ add tag</option>'
              + ''.join(f'<option value="{a}">{html.escape(l)}</option>' for a, l in TAGS) + '<option value="piercing">Piercing 1</option></select>')
    tagdiv = f'<div class="hl-tags">{flags}<span class="hl-tags-h">{T("lbl-tags", "Tags")}</span><span class="hl-pills">{pills}</span>{addsel}</div>'
    k = '<label><span data-i18n="lbl-enhance">'
    assert k in s
    s = s.replace(k, tagdiv + k, 1)
    hid = ''.join(f'<input type="hidden" name="attr_{k2}" value="{html.escape(v, quote=True)}" />' for k2, v in HIDDEN.items())
    hid += '<input type="hidden" name="attr_atk_short" value="" />'
    assert s.count('<div class="entry-body">' + mirror) == 1
    return s.replace('<div class="entry-body">' + mirror, '<div class="entry-body">' + mirror + hid, 1)

ARMOR_LINE = """<div class="armor-line">
  <input type="hidden" name="attr_armor_flag0" value="1" />
  <span class="al-h al-title">Armor</span>
  <label>Preset<select name="attr_armor_preset0">%(pre)s</select></label>
  <label class="al-cov">Name<input type="text" name="attr_armor_name0" /></label>
  <label>General<select name="attr_armor_general0">%(r)s</select></label>
  <label>Ballistic<select name="attr_armor_ballistic0">%(r)s</select></label>
  <label>Str req.<select name="attr_armor_strength0"><option value="0">-</option>%(s)s</select></label>
  <label>Defense<select name="attr_armor_defense0">%(d)s</select></label>
  <label>Speed<select name="attr_armor_speed0">%(p)s</select></label>
  <label class="al-cov">Coverage<input type="text" name="attr_armor_coverage0" placeholder="Torso, arms..." /></label>
  <label class="al-helm" title="Helmet: head covered at half rating (round up); -1 sight/hearing Perception"><span>Helmet</span><input type="checkbox" name="attr_armor_helmet0" value="1" /></label>
  <label class="al-notes">Notes<input type="text" name="attr_armor_description0" /></label>
  <span class="al-hint">Ballistic first (lethal to bashing vs firearms), then General. Armor Str req. unmet: -1 Brawl/Weaponry. Explosives: half ballistic.</span>
</div>""" % dict(pre=opts([(k, l) for k, l, _ in ARMOR]), r=opts([(i, i) for i in range(7)]), s=opts([(i, i) for i in range(1, 6)]),
                 d=opts([(-i, -i) for i in range(6)]), p=opts([(-i, -i) for i in range(6)]))

JS = r'''
        // ===== Hurt Locker weapons / attacks (src/hurtlocker.py) =====
        const HL_PRESETS = %(presets)s;
        const HL_TAGS = %(tags)s;
        const HL_ARMOR = %(armor)s;
        const HL_STATS = ["strength","dexterity","wits","presence","manipulation","brawl","weaponry","firearms","athletics","wound_penalty","cond_mod","strength_boost","dexterity_boost","wits_boost","presence_boost","manipulation_boost","armor_strength0","rolltype_eff"];
        const HL_ROW = ["name","wtype","atk_attr","atk_skill","str_req","other_mod","damage","dtype","initiative","wsize","max_range","capacity","onehanded","expl_delivery","blast","force","piercing","enhance","tags_extra","tags","clip","range","range_txt","clip_txt","hl_mig","notes"].concat(HL_TAGS.map(t => t[0]));
        const HL_BANDS = ["close","short","medium","long","extreme"], HL_BN = {close:"Close",short:"Short",medium:"Medium",long:"Long",extreme:"Extreme"}, HL_BMOD = {close:0,short:0,medium:-1,long:-2,extreme:-4};
        const HL_CAP = {single:"Single Shot: one use per scene (extra reloads / Loaded for Bear).",
            low:"Low: short burst only; empty after a short burst or any failed attack.",
            medium:"Medium: short/medium bursts; empty after 1 medium or 2 short bursts, or a dramatic failure.",
            high:"High: short/medium/long bursts; dry after 1 long, 2 medium or 3 short; jams on a dramatic failure (Dexterity + Firearms to fix)."};
        const HL_WT = {melee:"Melee",unarmed:"Unarmed",thrown:"Thrown",ranged:"Firearm / ranged",bow:"Bow",explosive:"Explosive"};
        const hlCap = x => x ? x.charAt(0).toUpperCase() + x.slice(1) : x;
        const hlMigrate = (p, v, u) => {
            // legacy clip -> capacity, range text -> max range band, free-text tags -> tag checkboxes (one-time per row)
            const t = v[p + "wtype"] || "melee", melee = (t === "melee" || t === "unarmed");
            if (!v[p + "capacity"] || (v[p + "capacity"] === "na" && (v[p + "clip"] || "").trim())) {
                const c = (v[p + "clip"] || "").trim().toLowerCase(); let cap = "na";
                if (!melee && c && c !== "melee") { const n = parseInt(c, 10) || 0; cap = n <= 2 ? "low" : (n < 20 ? "medium" : "high"); }
                if (t === "explosive") cap = "single";
                u[p + "capacity"] = cap;
            }
            if (!v[p + "max_range"] || (v[p + "max_range"] === "auto" && (v[p + "range"] || "").trim())) {
                const r = (v[p + "range"] || "").toLowerCase(); let b = melee ? "close" : "auto";
                const nums = (r.match(/\d+/g) || []).map(Number);
                if (/close|melee|touch/.test(r)) b = "close";
                else if (nums.length) { const y = nums[nums.length - 1]; b = y <= 5 ? "close" : y <= 33 ? "short" : y <= 109 ? "medium" : y <= 328 ? "long" : "extreme"; }
                else HL_BANDS.forEach(x => { if (r.indexOf(x) >= 0) b = x; });
                u[p + "max_range"] = b;
                if (v[p + "range"] && v[p + "range"].trim()) u[p + "notes"] = ((v[p + "notes"] || "") + (v[p + "notes"] ? "\n" : "") + "Legacy range: " + v[p + "range"]).trim();
            }
            const old = (v[p + "tags"] || "").trim();
            if (old) {
                let rest = old;
                const pats = {t_8again:/8[- ]?again/i, t_9again:/9[- ]?again/i, t_accurate:/\baccurate\b/i, t_inaccurate:/inaccurate/i, t_bleed:/bleed/i, t_brawl:/\bbrawl\b/i,
                    t_concealed:/conceal(ed|able)?/i, t_fragile:/fragile/i, t_grapple:/grapple/i, t_guard:/guard/i, t_incendiary:/incendiary/i, t_knockdown:/knock ?down/i,
                    t_reach:/reach/i, t_slow:/\bslow\b/i, t_stun:/\bstun\b/i, t_thrown_a:/thrown ?\(a\)/i, t_thrown:/\bthrown\b/i, t_twohanded:/two[- ]?handed/i};
                Object.keys(pats).forEach(k => { if (pats[k].test(rest)) { if (!(k === "t_thrown" && u[p + "t_thrown_a"] === "1")) u[p + k] = "1"; rest = rest.replace(pats[k], ""); } });
                if (k_ap(rest)) { u[p + "piercing"] = String(k_ap(rest)); rest = rest.replace(/(armor[- ]?piercing|piercing|ap)\s*\d+/i, ""); }
                if (/conceal(ed|able)?/i.test(old) && t !== "melee") {}
                rest = rest.replace(/[\s,;\/]+/g, " ").trim();
                if (rest && !v[p + "tags_extra"]) u[p + "tags_extra"] = rest;
                u[p + "tags"] = "";
            }
            u[p + "hl_mig"] = "2";
        };
        const k_ap = s => { const m = (s || "").match(/(?:armor[- ]?piercing|piercing|ap)\s*(\d+)/i); return m ? parseInt(m[1], 10) : 0; };
        const hlRowOf = e => { const m = ((e && (e.sourceAttribute || e.triggerName)) || "").match(/^repeating_weapons_([^_]+)_/i); return m ? m[1].toLowerCase() : null; };
        const updateWeaponAttacks = (e) => getSectionIDs("weapons", ids0 => {
            // a just-added row may not be listed by getSectionIDs yet: always include the row that fired the event
            const ids = ids0.map(x => x.toLowerCase()); const r = hlRowOf(e); if (r && ids.indexOf(r) < 0) ids.push(r);
            const f = ids.flatMap(id => HL_ROW.map(a => `repeating_weapons_${id}_${a}`));
            getAttrs(HL_STATS.concat(f), v => {
                const n = k => parseInt(v[k], 10) || 0, u = {};
                ids.forEach(id => {
                    const p = `repeating_weapons_${id}_`;
                    if (v[p + "hl_mig"] !== "2") { const m = {}; hlMigrate(p, v, m); Object.assign(u, m); Object.assign(v, m); }
                    const t = v[p + "wtype"] || "melee", tag = x => v[p + x] === "1";
                    const STR = n("strength") + n("strength_boost");
                    const deliv = v[p + "expl_delivery"] || "thrown", fired = (t === "ranged" || (t === "explosive" && deliv === "fired"));
                    const at = (v[p + "atk_attr"] && v[p + "atk_attr"] !== "auto") ? v[p + "atk_attr"] : ((t === "melee" || t === "unarmed") ? "strength" : "dexterity");
                    let sk = v[p + "atk_skill"];
                    if (!sk || sk === "auto") {
                        if (tag("t_brawl") || t === "unarmed") sk = "brawl";
                        else if (t === "melee") sk = "weaponry";
                        else if (t === "bow") sk = n("firearms") > n("athletics") ? "firearms" : "athletics";
                        else if (fired) sk = "firearms";
                        else sk = "athletics";
                    }
                    const av = n(at) + n(at + "_boost"), sv = n(sk), unsk = sv ? 0 : -1;
                    const sreq = n(p + "str_req") + ((tag("t_twohanded") && tag("onehanded")) ? 1 : 0);
                    const strpen = (sreq > 0 && STR < sreq) ? (t === "bow" ? 2 : 1) : 0;
                    const armpen = ((sk === "brawl" || sk === "weaponry") && n("armor_strength0") > STR) ? 1 : 0;
                    const acc = tag("t_accurate") ? 1 : 0, inacc = tag("t_inaccurate") ? 1 : 0, om = n(p + "other_mod");
                    const base = av + sv + unsk + om - strpen - armpen + acc - inacc + n("wound_penalty") + n("cond_mod");
                    const parts = [`${hlCap(at)} (${av})`, `${hlCap(sk)} (${sv})`];
                    if (unsk) parts.push("Unskilled -1"); if (om) parts.push(`Other ${om}`); if (acc) parts.push("Accurate +1"); if (inacc) parts.push("Inaccurate -1");
                    if (strpen) parts.push(`Str req. -${strpen}`); if (armpen) parts.push("Armor Str -1");
                    if (n("wound_penalty")) parts.push(`Wounds ${n("wound_penalty")}`); if (n("cond_mod")) parts.push(`Conditions ${n("cond_mod")}`);
                    u[p + "atk_base"] = base;
                    u[p + "atk_breakdown"] = parts.join(" + ").replace(/\+ -/g, "- ") + ` = ${base}` + (base <= 0 ? " (Chance Die)" : "");
                    u[p + "atk_short"] = `${hlCap(at)} + ${hlCap(sk)}: ${base}` + (base <= 0 ? " (chance)" : "");
                    u[p + "atk_wtxt"] = HL_WT[t] || "Melee";
                    // reroll quality
                    const again = tag("t_8again") ? 8 : (tag("t_9again") ? 9 : 10);
                    if (base <= 0) u[p + "atk_rt"] = "*0+1)d10cf<1}>10]]}} {{chance=1}}";
                    else if (again < 10) {
                        let rt = v.rolltype_eff || ")d10!cs>10}>@{success_target}]]}}";
                        rt = rt.replace(/d10!(?:>(\d+))?/, (m0, g) => "d10!>" + Math.min(again, g ? parseInt(g, 10) : 10));
                        u[p + "atk_rt"] = rt + ` {{${again}again=1}}`;
                    } else u[p + "atk_rt"] = "@{rolltype_eff}";
                    // range
                    const meleeish = (t === "melee" || t === "unarmed");
                    let mr = v[p + "max_range"] || "auto", thrownish = (t === "thrown" || (t === "explosive" && deliv === "thrown") || ((tag("t_thrown") || tag("t_thrown_a")) && t === "thrown"));
                    if (mr === "auto") {
                        if (meleeish) mr = "close";
                        else if (thrownish) { let i = STR <= 3 ? 0 : (STR <= 6 ? 1 : 3); if (tag("t_thrown_a")) i++; mr = HL_BANDS[Math.min(i, 4)]; }
                        else mr = "medium";
                    }
                    const mi = HL_BANDS.indexOf(mr);
                    if (meleeish) {
                        u[p + "atk_rangeq"] = "0"; u[p + "atk_rngshow"] = "";
                        u[p + "atk_maxtxt"] = "Close (melee)" + ((tag("t_thrown") || tag("t_thrown_a")) ? "; thrown: set Type to Thrown" : "");
                    } else {
                        const q = "?{Range band|" + HL_BANDS.slice(0, mi + 1).map(b => `${HL_BN[b]} (${HL_BMOD[b] || "0"}),${HL_BMOD[b]}`).join("|") + "}";
                        u[p + "atk_rangeq"] = q; u[p + "atk_rngshow"] = q;
                        u[p + "atk_maxtxt"] = `Max ${HL_BN[mr]}` + (thrownish ? ` (thrown, Str ${STR}${tag("t_thrown_a") ? ", aerodynamic" : ""})` : "") + (mi < 4 ? "; one band beyond = chance die" : "")
                            + ((thrownish && n(p + "wsize") >= STR) ? "; TOO BIG TO THROW (Size must be < Strength)" : "");
                    }
                    // burst / capacity
                    const cap = v[p + "capacity"] || "na";
                    const bo = {low:["Short burst +1,1"], medium:["Short burst +1,1","Medium burst +2,2"], high:["Short burst +1,1","Medium burst +2,2","Long burst +3,3"]}[cap];
                    if (bo && t !== "explosive") { const q = "?{Fire mode|Single attack,0|" + bo.join("|") + "}"; u[p + "atk_burstq"] = q; u[p + "atk_burstshow"] = q; }
                    else { u[p + "atk_burstq"] = "0"; u[p + "atk_burstshow"] = ""; }
                    u[p + "atk_ammo"] = (v[p + "clip_txt"] ? "Clip " + v[p + "clip_txt"] + ". " : "") + (HL_CAP[cap] ? HL_CAP[cap] + " Reload = an action." : "");
                    if (v[p + "range_txt"]) u[p + "atk_maxtxt"] = "Range " + v[p + "range_txt"] + (u[p + "atk_maxtxt"] ? " (" + u[p + "atk_maxtxt"] + ")" : "");
                    // defense
                    const size = n(p + "wsize");
                    if (t === "explosive") u[p + "atk_defq"] = "Target Defense (Force ignores Defense)";
                    else if (meleeish || t === "thrown") u[p + "atk_defq"] = "Target Defense (applies)";
                    else if (tag("t_slow")) u[p + "atk_defq"] = "Target Defense (Slow: full Defense applies)";
                    else u[p + "atk_defq"] = `Target Defense (firearms: Close = Size+1 = ${size + 1}; Short+ = 0)`;
                    u[p + "atk_def_default"] = 0;
                    // damage
                    let dmg = n(p + "damage"); if (t === "bow") dmg = Math.min(dmg, STR);
                    if (t === "explosive") u[p + "atk_dmgtxt"] = `+${dmg} automatic in the blast (plus attack successes on the primary target)`;
                    else if (tag("t_nodmg")) u[p + "atk_dmgtxt"] = `Weapon ${dmg}; bonus successes don't add to damage`;
                    else u[p + "atk_dmgtxt"] = `Successes + ${dmg}` + (t === "bow" ? ` (bow: lower of rating ${n(p + "damage")} / Str ${STR})` : "");
                    if (!v[p + "dtype"]) u[p + "dtype"] = (t === "unarmed") ? "B" : "L";
                    // tags / effects text
                    const tl = HL_TAGS.filter(x => tag(x[0])).map(x => x[1]);
                    if (n(p + "piercing")) tl.push(`Piercing ${n(p + "piercing")}`);
                    if (v[p + "enhance"]) tl.push(`Enhance: ${v[p + "enhance"]}`);
                    if (tag("t_twohanded") && tag("onehanded")) tl.push("used one-handed (Str req. +1)");
                    if (v[p + "tags_extra"]) tl.push(v[p + "tags_extra"]);
                    if (n(p + "initiative")) tl.push(`Init ${n(p + "initiative") > 0 ? "+" : ""}${n(p + "initiative")}`);
                    u[p + "atk_tags"] = tl.join(", ");
                    u[p + "atk_ap"] = n(p + "piercing") ? `Piercing ${n(p + "piercing")}: subtract from target armor (ballistic first, then general) or Durability` : "";
                    const tilts = [];
                    if (tag("t_knockdown")) tilts.push(`Knocked Down (bonus x2 = ${dmg * 2})`);
                    if (tag("t_stun")) tilts.push(`Stunned (bonus x2 = ${dmg * 2})`);
                    if (tag("t_bleed")) tilts.push(`Bleeding (bonus x2 = ${dmg * 2})`);
                    if (tag("t_incendiary")) tilts.push("Burning");
                    if (t === "explosive" && dmg > 0) tilts.push("Deafened");
                    u[p + "atk_tilt"] = tilts.join("; ");
                    // explosives
                    if (t === "explosive") {
                        const fo = n(p + "force"), bl = n(p + "blast");
                        u[p + "atk_force"] = fo ? `[[{${fo}d10!cs>10}>@{success_target}]] successes (Force ${fo}; no Defense; mundane armor = half ballistic; 1+ success adds +${dmg})` : "";
                        u[p + "atk_blast"] = bl ? `Ground zero: Aggravated; primary ${bl} m: Lethal; secondary ${bl * 2} m: Bashing` : "";
                    } else { u[p + "atk_force"] = ""; u[p + "atk_blast"] = ""; }
                });
                setAttrs(u, {silent: true});
            });
        });
        globalThis.__hlAtk = updateWeaponAttacks;
        on("change:repeating_weapons:preset", e => {
            if (e.sourceType !== "player") return;
            const id = (e.sourceAttribute.match(/^repeating_weapons_([^_]+)_/) || [])[1], P0 = HL_PRESETS[e.newValue]; if (!id || !P0) return;
            const p = `repeating_weapons_${id}_`;
            getAttrs([p + "name", p + "notes"], v => {
                const u = {};
                ["wtype","damage","dtype","initiative","str_req","wsize","avail","max_range","capacity","piercing","enhance","atk_attr","atk_skill","blast","force","expl_delivery","tags_extra"].forEach(k => u[p + k] = P0[k]);
                HL_TAGS.forEach(t => u[p + t[0]] = P0.tags.indexOf(t[0]) >= 0 ? "1" : "0");
                if (!v[p + "name"] || Object.values(HL_PRESETS).some(x => x.label === v[p + "name"])) u[p + "name"] = P0.label;
                if (P0.note && (!v[p + "notes"] || Object.values(HL_PRESETS).some(x => x.note && x.note === v[p + "notes"]))) u[p + "notes"] = P0.note;
                u[p + "hl_mig"] = "2"; u[p + "onehanded"] = "0";
                setAttrs(u, {silent: true}, () => updateWeaponAttacks(e));
            });
        });
        on("change:repeating_weapons:tag_add", e => {
            if (e.sourceType !== "player" || !e.newValue) return;
            const p = e.sourceAttribute.replace(/tag_add$/, ""), a = e.newValue;
            getAttrs([p + "piercing"], v => { const u = {[p + "tag_add"]: ""};
                if (a === "piercing") u[p + "piercing"] = String(Math.max(1, parseInt(v[p + "piercing"], 10) || 0)); else u[p + a] = "1";
                setAttrs(u, {silent: true}, () => updateWeaponAttacks(e)); });
        });
        on(HL_TAGS.map(t => "clicked:repeating_weapons:tagrm_" + t[0]).concat(["clicked:repeating_weapons:tagrm_piercing"]).join(" "), e => {
            const m = (e.sourceAttribute || "").match(/^(repeating_weapons_[^_]+_)tagrm_(.+)$/); if (!m) return;
            setAttrs({[m[1] + m[2]]: "0"}, {silent: true}, () => updateWeaponAttacks(e));
        });
        on("change:repeating_weapons:wtype", e => {
            if (e.sourceType !== "player") return;
            const p = e.sourceAttribute.replace(/wtype$/, "");
            setAttrs({[p + "dtype"]: e.newValue === "unarmed" ? "B" : "L"}, {silent: true}, updateWeaponAttacks);
        });
        on("change:armor_preset0", e => {
            const a = HL_ARMOR[e.newValue]; if (!a || e.sourceType !== "player") return;
            setAttrs({armor_name0: a[0], armor_general0: a[1], armor_ballistic0: a[2], armor_strength0: a[3], armor_defense0: a[4], armor_speed0: a[5], armor_coverage0: a[6]}, updateWeaponAttacks);
        });
        on("change:repeating_weapons remove:repeating_weapons sheet:opened " + HL_STATS.filter(s => s !== "rolltype_eff").map(s => "change:" + s).join(" "), updateWeaponAttacks);
'''
def js():
    pres = {i: dict(d, label=l) for i, l, d in PRESETS}
    arm = {k: [l] + list(v) for k, l, v in ARMOR if v}
    return JS % dict(presets=json.dumps(pres, separators=(',', ':')), tags=json.dumps(TAGS), armor=json.dumps(arm))

CSS = """
/* ===== Hurt Locker weapons: full-width combat block ===== */
.sheet-p1-combat { width: 100%; flex-basis: 100%; clear: both; margin-top: 6px; box-sizing: border-box; }
.sheet-p1-combat .sheet-p1-weapons { width: 100%; }
.sheet-entry-section.sheet-weapons .sheet-entry-head { min-height: 20px; }
.sheet-entry-section.sheet-weapons .sheet-entry-pool { max-width: 260px; }
.charsheet button[type=roll].sheet-hl-poolbtn { margin-left: auto; padding: 0 4px; border: 0; background: none; box-shadow: none; text-shadow: none; color: inherit; cursor: pointer; font: inherit; line-height: 16px; height: 18px; }
.charsheet button[type=roll].sheet-hl-poolbtn::before { content: "\2694"; margin-right: 3px; }
.charsheet button[type=roll].sheet-hl-poolbtn:hover .sheet-entry-pool { text-decoration: underline; }
.sheet-entry-section.sheet-weapons .sheet-entry-body { gap: 3px 8px; }
.sheet-entry-section.sheet-weapons .sheet-entry-body label { flex: 1 1 96px; min-width: 88px; max-width: 200px; font-size: 10px; }
.sheet-entry-section.sheet-weapons .sheet-entry-body label.sheet-wide { max-width: none; }
.sheet-entry-section.sheet-weapons .sheet-entry-body label.sheet-hl-name, .sheet-entry-section.sheet-weapons .sheet-entry-body label.sheet-hl-preset { flex: 2 1 220px; max-width: 360px; }
.sheet-entry-section.sheet-weapons select, .sheet-entry-section.sheet-weapons .sheet-entry-body input[type=text], .sheet-entry-section.sheet-weapons .sheet-entry-body input[type=number] { width: 100% !important; height: 20px; padding: 0 2px; margin: 0; font-size: 11px; display: inline-block; box-sizing: border-box; }
.sheet-entry-section.sheet-weapons .sheet-entry-body label.sheet-hl-2h { flex-direction: row; align-items: center; gap: 4px; }
/* tag pills (active tags only) + add-tag select */
.sheet-entry-section.sheet-weapons .sheet-hl-tags { display: flex; flex-wrap: wrap; align-items: center; gap: 3px; flex: 1 1 100%; font-size: 11px; }
.sheet-hl-tags .sheet-hl-pills { display: contents; }
.sheet-hl-tags .sheet-hl-pill { display: none; align-items: center; gap: 2px; height: 16px; line-height: 16px; padding: 0 1px 0 7px; border-radius: 8px; font-size: 11px; white-space: nowrap;
  background: color-mix(in srgb, var(--temp-dot, #8b1010) 22%, rgba(0,0,0,0)); border: 1px solid color-mix(in srgb, var(--temp-dot, #8b1010) 65%, #888); }
.sheet-hl-tf-t_8again[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_8again,
.sheet-hl-tf-t_9again[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_9again,
.sheet-hl-tf-t_accurate[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_accurate,
.sheet-hl-tf-t_inaccurate[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_inaccurate,
.sheet-hl-tf-t_bleed[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_bleed,
.sheet-hl-tf-t_brawl[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_brawl,
.sheet-hl-tf-t_concealed[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_concealed,
.sheet-hl-tf-t_fragile[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_fragile,
.sheet-hl-tf-t_grapple[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_grapple,
.sheet-hl-tf-t_guard[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_guard,
.sheet-hl-tf-t_incendiary[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_incendiary,
.sheet-hl-tf-t_knockdown[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_knockdown,
.sheet-hl-tf-t_reach[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_reach,
.sheet-hl-tf-t_slow[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_slow,
.sheet-hl-tf-t_stun[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_stun,
.sheet-hl-tf-t_thrown[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_thrown,
.sheet-hl-tf-t_thrown_a[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_thrown_a,
.sheet-hl-tf-t_twohanded[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_twohanded,
.sheet-hl-tf-t_nodmg[value="1"] ~ .sheet-hl-pills .sheet-hl-pill-t_nodmg, .sheet-hl-tf-ap:not([value="0"]):not([value=""]) ~ .sheet-hl-pills .sheet-hl-pill-ap { display: inline-flex; }
.charsheet .sheet-hl-tags button.sheet-hl-pill-x { width: 14px !important; height: 14px !important; min-width: 0 !important; padding: 0 !important; margin: 0 !important; border: 0 !important; border-radius: 50% !important;
  background: none !important; box-shadow: none !important; font: bold 10px/14px Arial, sans-serif !important; color: inherit !important; opacity: .65; cursor: pointer; text-shadow: none !important; }
.charsheet .sheet-hl-tags button.sheet-hl-pill-x:hover { opacity: 1; background: rgba(128,128,128,.3) !important; }
.charsheet .sheet-entry-section.sheet-weapons .sheet-hl-tags select.sheet-hl-tagadd { width: auto !important; max-width: 110px; height: 18px !important; padding: 0 2px !important; margin: 0 !important; font-size: 11px !important; border-radius: 8px !important; border-style: dashed !important; }
/* collapsed row: active tags as compact text */
.sheet-entry-section.sheet-weapons .sheet-entry-head .sheet-hl-tagsum { flex: 0 1 auto; min-width: 0; max-width: 34%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 10px; font-style: italic; opacity: .75; margin: 0 4px; }
.sheet-entry-section.sheet-weapons .sheet-entry-toggle:checked ~ .sheet-entry-head .sheet-hl-tagsum { display: none; }

.sheet-hl-tags { display: flex; flex-wrap: wrap; align-items: center; gap: 2px 4px; flex: 1 1 100%; font-size: 10px; }
.sheet-hl-tags .sheet-hl-tags-h { font-weight: bold; margin-right: 4px; }
.sheet-entry-section.sheet-weapons .sheet-entry-body .sheet-hl-tags label.sheet-hl-chip { flex: 0 0 auto; min-width: 0; max-width: none; flex-direction: row; align-items: center; gap: 2px; font-weight: normal; border: 1px solid rgba(128,128,128,.6); border-radius: 9px; padding: 0 6px 0 2px; line-height: 16px; cursor: pointer; }
.sheet-hl-tags label.sheet-hl-chip input[type=checkbox] { margin: 0; width: 11px; height: 11px; }
.sheet-hl-tags label.sheet-hl-chip input[type=checkbox]:checked + span { font-weight: bold; color: var(--temp-dot, #8b1010); }
.sheet-entry-section.sheet-weapons .sheet-entry-body label.sheet-hl-x { display: none; }
.sheet-entry-section.sheet-weapons .sheet-entry-body input.sheet-hl-wt[value="explosive"] ~ label.sheet-hl-x { display: flex; }
.sheet-entry-section.sheet-weapons .sheet-entry-body input.sheet-hl-wt[value="melee"] ~ label.sheet-hl-r, .sheet-entry-section.sheet-weapons .sheet-entry-body input.sheet-hl-wt[value="unarmed"] ~ label.sheet-hl-r { display: none; }
.sheet-entry-section.sheet-weapons .sheet-entry-body input.sheet-hl-2hv:not([value="1"]) ~ label.sheet-hl-2h { display: none; }
.sheet-entry-section.sheet-weapons .sheet-entry-body label { display: flex; flex-direction: column; gap: 0; margin: 0; line-height: 12px; }
.sheet-entry-section.sheet-weapons .sheet-entry-body input[type=number] { max-width: 100%; }
.sheet-entry-section.sheet-weapons .sheet-entry-body textarea { height: 22px; min-height: 22px; font-size: 11px; width: 100% !important; box-sizing: border-box; }
.sheet-entry-section.sheet-weapons .sheet-entry-body label.sheet-hl-notes { flex: 2 1 220px; max-width: none; }
.sheet-p1-combat .sheet-armor-line { display: flex !important; flex-wrap: wrap; align-items: flex-end; gap: 3px 8px; padding: 3px 4px; font-size: 10px; box-sizing: border-box; width: 100%; }
.sheet-p1-combat .sheet-armor-line > label { font-size: 10px; font-weight: bold; display: flex; flex-direction: column; flex: 0 0 auto; margin: 0; line-height: 12px; }
.sheet-p1-combat .sheet-armor-line > label input, .sheet-p1-combat .sheet-armor-line > label select { height: 20px; font-size: 11px; padding: 0 2px; margin: 0; box-sizing: border-box; width: 56px !important; }
.sheet-p1-combat .sheet-armor-line > label.sheet-al-cov input { width: 120px !important; }
.sheet-p1-combat .sheet-armor-line > label.sheet-al-helm { flex-direction: row; align-items: center; height: 20px; }
.sheet-p1-combat .sheet-armor-line > label.sheet-al-helm input { width: auto !important; height: auto; }
.sheet-p1-combat .sheet-armor-line > .sheet-al-title { font-weight: bold; font-size: 12px; align-self: center; flex: 0 0 auto; }
.sheet-armor-line .sheet-al-hint { flex: 1 1 100%; font-size: 9px; font-style: italic; opacity: .75; }
.sheet-armor-line label.sheet-al-helm { flex-direction: row; align-items: center; gap: 3px; }
.sheet-armor-line label.sheet-al-helm input { margin: 0; }
.sheet-p1-combat .sheet-armor-line select[name=attr_armor_preset0] { width: 130px !important; min-width: 130px; }
.sheet-p1-combat .sheet-armor-line label.sheet-al-notes { flex: 1 1 120px; min-width: 0; }
.sheet-p1-combat .sheet-armor-line label.sheet-al-notes input { width: 100% !important; box-sizing: border-box; min-width: 0; }
.sheet-darkmode .sheet-hl-tags label.sheet-hl-chip { border-color: rgba(220,220,220,.35); }
.sheet-darkmode .sheet-hl-tags label.sheet-hl-chip input[type=checkbox]:checked + span { color: #f0c060; }
"""
