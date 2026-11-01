"""Werewolf: Auspice/Tribe dropdowns, Moon Gift block with moon graphic, Auspice Ability, gift suggestions."""
import json
AUSP = {  # verified: WtF 2E auspice table (skills, renown, gifts) and Auspice Benefit text
 'Cahalith': dict(moon='gibbous', skills=['crafts','expression','persuasion'], renown='Glory', gifts='Inspiration, Knowledge',
   ability='Prophetic Dreams', text="The Storyteller may grant prophetic dreams; roll Intelligence + Occult to interpret. After a night of 4+ hours' sleep, once you may declare an action or event was foretold: you or a packmate gain +3 to one action, or a Storyteller character takes -3."),
 'Elodoth': dict(moon='half', skills=['empathy','investigation','politics'], renown='Honor', gifts='Insight, Warding',
   ability='Darkness Into Light', text="Once per chapter, cure a werewolf of Death Rage (the target is Stunned for the next turn if in Basu-Im), or force one into Death Rage with Presence + Empathy + Primal Urge vs Resolve + Composure (works only on Uratha)."),
 'Irraka': dict(moon='new', skills=['larceny','stealth','subterfuge'], renown='Cunning', gifts='Evasion, Stealth',
   ability='Closer Than You Thought', text="Once per chapter, choose one: move your Initiative to within 1 of a target's; close to use teeth/claws on one opponent not attacking you; or reduce Doors needed in Social maneuvering by 2."),
 'Ithaeur': dict(moon='crescent', skills=['animalken','medicine','occult'], renown='Wisdom', gifts='Elemental, Shaping',
   ability='Spirit Howl', text="Once per chapter, spend 1 Essence (no roll): a howl silent in the Flesh echoes through the Shadow. Lower-Rank spirits flee or hide, more powerful ones show deference; hostile spirits' Defense is penalised by your Wisdom."),
 'Rahu': dict(moon='full', skills=['brawl','intimidation','survival'], renown='Purity', gifts='Dominance, Strength',
   ability='Tenacious', text="Once per chapter, ignore the effects of any Conditions or Tilts hindering you in combat for two turns (they are not resolved)."),
}
# Moon Gift Facet names: from memory, NOT verified (OCR of the book lost the headings)
FACETS = {'full': "Full Moon's Gift: Killer Instinct •, Warrior's Hide ••, Bloody-Handed Hunter •••, Butchery ••••, Crimson Spasm •••••",
 'gibbous': "Gibbous Moon's Gift: War Howl •, Voice of Glory ••, Dream Hunter •••, Thousand-Throat Howl ••••, End of Story •••••",
 'half': "Half Moon's Gift: Scent Beneath the Surface •, Binding Oath ••, Sly Hunter •••, Horizon Run ••••, Know the Path •••••",
 'crescent': "Crescent Moon's Gift: Shadow Gaze •, Spirit Whispers ••, Shadow Hunter •••, Shadow Masquerade ••••, Panoptic Shadow •••••",
 'new': "New Moon's Gift: Eviscerate •, Slip Away ••, Divide and Conquer •••, Breach the Gauntlet ••••, Unseen Hunter •••••"}
TRIBES = {  # Gift affinities. v = checked against the book
 'Blood Talons': ('Inspiration, Rage, Strength', True), 'Bone Shadows': ('Death, Elements, Insight', True),
 'Hunters in Darkness': ('Nature, Stealth, Warding', True), 'Storm Lords': ('Evasion, Dominance, Weather', True),
 'Iron Masters': ('Knowledge, Shaping, Technology', False),
 'Ghost Wolves': ('No Gift affinities; start with one Shadow Gift', True),
 'Fire-Touched (Pure)': ('Inspiration, Insight, Knowledge (unverified)', False), 'Ivory Claws (Pure)': ('Dominance, Insight, Warding (unverified)', False),
 'Predator Kings (Pure)': ('Dominance, Nature, Rage (unverified)', False)}
def key(s): return s.split(' (')[0].lower().replace(' ', '-')

def moon_svg(ph):
    # PNG background (Roll20 strips inline SVG); art pinned in pdfstyle.MOON_BASE
    return f'<div class="moon-img moon-{ph}" title="{ph.title()} moon"></div>'

def moon_css():
    from pdfstyle import MOON_BASE
    o = ['.charsheet .sheet-moon-img { width: 68px; height: 68px; margin: 0 auto 2px; background-repeat: no-repeat; background-position: center; background-size: contain; }']
    o += [f'.charsheet .sheet-moon-{p} {{ background-image: url("{MOON_BASE}/{p}.png"); }}' for p in ('new', 'crescent', 'half', 'gibbous', 'full')]
    return '\n'.join(o) + '\n'

def header(h):
    ao = '<option value="">—</option>' + ''.join(f'<option value="{a}">{a}</option>' for a in AUSP)
    to = '<option value="">—</option>' + ''.join(f'<option value="{t}">{t}</option>' for t in TRIBES)
    for attr, opts, name in [('Age', ao, 'auspice'), ('Faction', to, 'tribe')]:
        a = f'<input type="text" name="attr_{attr}">'
        assert a in h, attr
        h = h.replace(a, f'<span class="wolf-hdr-wrap"><input type="text" class="wolf-generic" name="attr_{attr}"><select class="game-line werewolf2 wolf-sel" name="attr_{name}">{opts}</select></span>', 1)
    return h

def page(h):
    ab = ''.join(f'<div class="wolf-ab wolf-ab-{a.lower()}"><div class="wolf-moon">{moon_svg(d["moon"])}<div class="wolf-moonname">{d["moon"].title()} Moon</div></div>'
        f'<div class="wolf-abtxt"><div class="wolf-h">Auspice Ability: <b>{d["ability"]}</b> '
        f'<button type="roll" class="mini" name="roll_ausp_ability_{a.lower()}" value="&amp;{{template:cofd-entry}} {{{{kind=Auspice Ability ({a})}}}} {{{{name={d["ability"]}}}}} {{{{f_description={d["text"]}}}}}">💬</button></div>'
        f'<div class="wolf-t">{d["text"]}</div><div class="wolf-sub">Auspice Skills: {", ".join(s.title().replace("Animalken","Animal Ken") for s in d["skills"])} · Renown: {d["renown"]} · Gift affinities: {d["gifts"]}, {d["moon"].title()} Moon</div></div></div>' for a, d in AUSP.items())
    mg = ''.join(f'<div class="wolf-mg wolf-mg-{d["moon"]}"><span class="wolf-t">{FACETS[d["moon"]]}</span> <i class="wolf-unv">(Facet names not checked against the book)</i></div>' for a, d in AUSP.items())
    tr = ''.join(f'<div class="wolf-tr wolf-tr-{key(t)}">Tribe Gift affinities: <b>{g}</b>{"" if v else " <i class=wolf-unv>(not checked against the book)</i>"}</div>' for t, (g, v) in TRIBES.items())
    dots = ''.join(f'<label class="wolf-dot"><input type="radio" name="attr_moon_gift_dots" value="{i}"{" checked" if i==0 else ""}/><span></span></label>' for i in range(0, 6))
    block = f'''<div class="game-line werewolf2 wolf-block">
  <input type="hidden" class="wolf-a" name="attr_auspice" value=""/><input type="hidden" class="wolf-tk" name="attr_tribe_key" value=""/>
  <div class="entry-section-head"><span class="subheader">Auspice &amp; Moon Gift</span></div>
  <div class="wolf-none">Choose an Auspice and Tribe on Main.</div>
  {ab}
  <div class="wolf-mgrow"><span class="wolf-h">Moon Gift</span> <span class="wolf-dots">{dots}</span>
   <input type="text" name="attr_moon_gift_facets" placeholder="Facets learned" />
   <button type="roll" class="mini" name="roll_moon_gift" value="&amp;{{template:cofd-entry}} {{{{kind=Moon Gift}}}} {{{{name=@{{auspice}} — @{{moon_gift_name}}}}}} {{{{dots=@{{moon_gift_dots}}}}}} {{{{f_description=@{{moon_gift_facets}}}}}}">💬</button>
   <input type="hidden" name="attr_moon_gift_name" value=""/></div>
  {mg}
  {tr}
</div>
'''
    a = '<div class="game-line werewolf breeds2 breeds-head">'
    assert a in h
    return h.replace(a, block + a, 1)

JS = r'''
        const AUSP_SK = %s, MOONS = %s;
        on("change:auspice", ev => { const a = ev.newValue || ""; const up = {};
            if (ev.previousValue && AUSP_SK[ev.previousValue]) AUSP_SK[ev.previousValue].forEach(s => up[`${s}_mark`] = "0");
            (AUSP_SK[a] || []).forEach(s => up[`${s}_mark`] = "1");
            up.moon_gift_name = a ? MOONS[a] : ""; setAttrs(up); });
        on("change:tribe sheet:opened", () => getAttrs(["tribe"], v => setAttrs({tribe_key: (v.tribe || "").split(" (")[0].toLowerCase().replace(/ /g, "-")}, {silent: true})));
''' % (json.dumps({a: d['skills'] for a, d in AUSP.items()}), json.dumps({a: d['moon'].title() + " Moon's Gift" for a, d in AUSP.items()}))

def css():
    out = ['.sheet-wolf-block { border: 1px solid var(--temp-dot,#aa5a1e); border-radius: 8px; padding: 6px 10px; margin: 6px 0 10px; background: rgba(170,90,30,.08); }',
     '.sheet-wolf-ab, .sheet-wolf-mg, .sheet-wolf-tr { display: none; }',
     '.sheet-wolf-ab { gap: 12px; align-items: flex-start; }',
     '.sheet-wolf-moon { text-align: center; min-width: 74px; display: flex; flex-direction: column; align-items: center; } .sheet-wolf-moonname { font: bold 10px Arial; color: var(--temp-dot,#aa5a1e); text-transform: uppercase; letter-spacing: 1px; }',
     '.sheet-wolf-h { font-weight: bold; font-size: 13px; } .sheet-wolf-t { font-size: 12px; } .sheet-wolf-sub { font-size: 11px; opacity: .8; margin-top: 3px; } .sheet-wolf-unv { font-size: 10px; opacity: .7; }',
     '.sheet-wolf-mgrow { display: flex; gap: 8px; align-items: center; margin: 6px 0 2px; } .sheet-wolf-mgrow input[type=text] { flex: 1; }',
     '.sheet-wolf-dot { position: relative; display: inline-block; width: 12px; height: 12px; } .sheet-wolf-dot input { position: absolute; opacity: 0; inset: 0; margin: 0; z-index: 2; cursor: pointer; width: 12px; height: 12px; }',
     '.sheet-wolf-dot span { position: absolute; inset: 1px; border-radius: 50%; border: 1.5px solid var(--temp-dot,#aa5a1e); } .sheet-wolf-dot:first-child { width: 0; overflow: hidden; }',
     '.sheet-wolf-dots:has(input[value="5"]:checked) span, .sheet-wolf-dot:has(~ .sheet-wolf-dot input:checked) span, .sheet-wolf-dot input:checked + span { background: var(--temp-dot,#aa5a1e); }',
     'input.sheet-wolf-a:not([value=""]) ~ .sheet-wolf-none { display: none; }',
     '.sheet-wolf-hdr-wrap { display: contents; } input.sheet-game-line[value="werewolf"] ~ * .sheet-wolf-hdr-wrap input.sheet-wolf-generic { display: none; }',
     'select.sheet-wolf-sel { width: 100%; }',
     '.sheet-darkmode .sheet-wolf-block { background: rgba(224,138,60,.08); border-color: #e08a3c; } .sheet-darkmode .sheet-wolf-moonname { color: #e08a3c !important; } .sheet-darkmode .sheet-wolf-dot span { border-color: #e08a3c; }']
    for a, d in AUSP.items():
        out.append(f'input.sheet-wolf-a[value="{a}"] ~ .sheet-wolf-ab-{a.lower()} {{ display: flex; }} input.sheet-wolf-a[value="{a}"] ~ .sheet-wolf-mg-{d["moon"]} {{ display: block; }}')
    for t in TRIBES:
        out.append(f'input.sheet-wolf-tk[value="{key(t)}"] ~ .sheet-wolf-tr-{key(t)} {{ display: block; }}')
    return '\n'.join(out)
_css0 = css
def css():
    return _css0() + '''
.sheet-wolf-dots { display: inline-flex; gap: 2px; }
.sheet-wolf-dot input:checked + span, .sheet-wolf-dot:has(~ .sheet-wolf-dot input:checked) span, .sheet-darkmode .sheet-wolf-dot input:checked + span, .sheet-darkmode .sheet-wolf-dot:has(~ .sheet-wolf-dot input:checked) span { background-color: #e08a3c !important; }
.sheet-wolf-dot:first-child span { display: none; }
'''
