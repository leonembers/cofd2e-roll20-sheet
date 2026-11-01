"""Forms tab: feature pills that open a read-only rules note, active-card highlight, Ur'Khar (Leon's homebrew) tracking."""
import re
U = ' <i>(Not checked against the W:tF 2E book; verify.)</i>'
LUN = ('Ordinary humans who see the werewolf in this form fall under the Lunacy: they panic, flee or freeze according to their Willpower, '
       'and afterwards remember a rationalised version of events (wild dog, big guy, nothing at all).')
DESC = {
 "Sheep's Clothing": 'Hishu is the fully human shape. Nothing about the body gives the werewolf away to ordinary senses, it never triggers the Lunacy, '
                     'and she can pass among people with no special precautions.' + U,
 'Teeth/Claws +0L': 'Bite and claws count as natural weapons that inflict lethal damage instead of bashing. Attack with Strength + Brawl; this form adds no extra dice.',
 'Teeth/Claws +2L (Init +3)': 'Bite and claws are natural weapons that inflict lethal damage and add +2 dice to Brawl attacks made with them. '
                              'The listed +3 is an Initiative modifier while the werewolf fights with these natural weapons.' + U,
 'Teeth/Claws +2L': 'Bite and claws are natural weapons that inflict lethal damage and add +2 dice to Brawl attacks made with them.',
 'Teeth +2L/Claws +1L': 'Natural weapons that inflict lethal damage: the bite adds +2 dice, the claws +1 die to Brawl attacks.',
 'Teeth +1L': 'The bite is a natural weapon that inflicts lethal damage and adds +1 die to Brawl attacks.',
 'Defense vs. Firearms': 'The werewolf may apply her Defense against firearms and other ranged gun attacks, which normally ignore Defense.',
 'Defense vs Firearms': 'The werewolf may apply her Defense against firearms and other ranged gun attacks, which normally ignore Defense.',
 'Mild Lunacy': LUN + ' In this near-human shape the effect is weakest: witnesses resist as if their Willpower were 4 higher.' + U,
 'Moderate Lunacy': LUN + ' In this near-wolf shape witnesses resist as if their Willpower were 2 higher.' + U,
 'Full Lunacy': LUN + ' The war form applies the Lunacy at full strength, with no bonus to the witnesses.',
 'Badass Motherfucker': 'The near-human shape looks so physically dangerous that ordinary people instinctively back down: '
                        'it bolsters intimidation and makes humans reluctant to start a fight with her. Exact dice effect TBD.' + U,
 'Regeneration': 'The war form heals at a supernatural rate: each turn the werewolf may reflexively heal one point of bashing or lethal damage. '
                 'Aggravated damage is not healed this way.' + U,
 'Rage': 'The war form is pure aggression. Holding it is limited to Stamina + Primal Urge turns, and while in it the werewolf is driven toward violence: '
         'mental and social actions other than intimidation are restricted, and staying past the limit risks Death Rage.' + U,
 'Primal Fear': 'The war form terrifies even the supernatural. Beyond the human Lunacy, other creatures who see it may need to steel themselves '
                'before acting against it (Storyteller adjudicates).' + U,
 'Weaken the Prey': 'The near-wolf shape is built to bring prey down: its bite attacks can hamper the victim instead of only wounding it. Exact effect TBD.' + U,
 'Chase Down': 'The wolf shape is a tireless pursuer: it excels at tracking and running down fleeing prey. Exact effect TBD.' + U,
 'once per story': "Voluntary shift into Ur'Khar is allowed once per story (tick 'Used this story'). Basu-Im forces the shift regardless and does not use up the allowance.",
}
UR = {
 'Teeth/Claws +2L': 'Bite and claws are natural weapons that inflict lethal damage and add +2 dice to Brawl attacks made with them.',
 'Regeneration': 'Full Gauru regeneration (the same rule as the Gauru card). Exact rate: see Gauru; TBD until verified.',
 'Rage': "The ancestral killing form narrows the mind: conscious, careful action is restricted by Rage. A voluntary shift lasts Hishu Stamina + Primal Urge turns; "
         "when it runs out the werewolf must change to another form or suffer the normal consequences of staying in the killing form. "
         "Under Basu-Im it lasts as long as the Death Rage, with no conscious control at all.",
 'Full Lunacy': LUN + " Ur'Khar applies the Lunacy at full strength, like Gauru.",
 'Primal Fear': "As Gauru's Primal Fear (exact effect TBD).",
}
def pill(k, i, name, desc):
    return (f'<span class="sheet-fc-tw"><input type="checkbox" class="sheet-fc-tg" name="attr_fcd_{k}_{i}" value="1" title="Show what {name} does" />'
            f'<span class="sheet-fc-trait">{name}</span><span class="sheet-fc-desc">{desc}</span></span>')
def apply(h, c):
    # 1) summary line and Active tag go; the active card gets a glow instead
    h, n = re.subn(r'<div class="sheet-form-active">.*?</div>', '', h, count=1, flags=re.S); assert n == 1
    h = h.replace('<span class="sheet-fc-badge">Active</span>', '')
    h = h.replace('<input type="hidden" class="sheet-fc-cur" name="attr_form" value="hishu" />', '<input type="hidden" class="sheet-fc-cur" name="attr_form" value="hishu" /><div class="sheet-fc-glow"></div>')
    missing = []
    # 2) Werewolf: Form select block leaves the right pane; h/w + Death Rage buttons go in one row above the form pills
    m = re.search(r'<div class="sheet-quick-actions sheet-game-line sheet-werewolf2 sheet-breeds2">(.*?)</div>', h, re.S); assert m
    blk = m.group(1)
    hw = re.search(r'<span class="sheet-form-hw-mini".*?</span></span>', blk, re.S).group(0)
    rage = ''.join(re.findall(r'<button type="(?:action|roll)" class="sheet-quick sheet-rage[^"]*"[^>]*name="(?:act_rr|roll)_(?:wasuim|basuim)"[^>]*>.*?</button>', blk, re.S)); assert rage.count('<button') == 2
    h = h.replace(m.group(0), m.group(0).replace('sheet-game-line sheet-werewolf2 sheet-breeds2"', 'sheet-game-line sheet-breeds2"', 1), 1)
    a = '<div class="sheet-form-picker">'; assert h.count(a) == 1
    h = h.replace(a, '<div class="sheet-form-qrow">' + hw + rage + '</div>' + a, 1)
    # simpler pass: rebuild every fc-traits block in place
    def blk(m):
        k = m.group(1); seg = m.group(0)
        t = re.search(r'<div class="sheet-fc-traits">(.*?)</div>', seg, re.S)
        names = re.findall(r'<span class="sheet-fc-trait">(.*?)</span>', t.group(1))
        out = []
        for i, nm in enumerate(names):
            key = nm.replace('&#8217;', "'").replace('&#39;', "'")
            d = (UR.get(key) if k == 'urkhar' else None) or DESC.get(key)
            if not d: d = 'TBD'; missing.append(f'{k}:{key}')
            out.append(pill(k, i, nm, d))
        extra = ''
        if k == 'gauru':
            extra = ('<div class="sheet-fc-urnote"><b>Stable Gauru</b> (Ur&#39;Khar enabled): Strength +2 instead of the usual bonus, '
                     'held at will with no time limit, normal regeneration. The stat grid already uses these values.</div>')
        if k == 'urkhar':
            extra = ('<div class="sheet-fc-urtrack"><label class="sheet-ur-used" title="Voluntary Ur&#39;Khar is once per story; Basu-Im does not use this up">'
                     '<input type="checkbox" name="attr_urkhar_used" value="1" /> Used this story</label>'
                     '<span class="sheet-ur-tl" title="Turns left on a voluntary shift (set to Hishu Stamina + Primal Urge when you shift)">Turns left '
                     '<button type="action" class="sheet-res-btn" name="act_urkhar_turn_dec">&minus;</button>'
                     '<input type="number" readonly="readonly" tabindex="-1" class="sheet-ur-turns" name="attr_urkhar_turns" value="0" />'
                     '<button type="action" class="sheet-res-btn" name="act_urkhar_turn_inc">+</button></span>'
                     '<span class="sheet-fc-urinfo">Unlocked by the Facet Form of the Firstborn. Cost and action: a normal shapeshift (by Harmony).</span></div>')
        return seg[:t.start()] + '<div class="sheet-fc-traits">' + ''.join(out) + '</div>' + extra + seg[t.end():]
    h, n = re.subn(r'<div class="sheet-fcard sheet-fc-([a-z]+)[^"]*">.*?<textarea class="sheet-fc-notes"', blk, h, flags=re.S)
    assert n == 6, n
    forms = ['hishu', 'dalu', 'gauru', 'urkhar', 'urshul', 'urhan']
    c += ('.charsheet .sheet-main-forms .sheet-form-qrow { display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 4px 10px; margin: 2px 0 4px; padding: 0 2px; }\n'
          '.charsheet .sheet-main-forms .sheet-form-qrow .sheet-form-hw-mini { font-size: 12px; white-space: nowrap; opacity: .9; }\n'
          '.charsheet .sheet-main-forms .sheet-form-qrow button.sheet-quick { margin: 0; padding: 1px 8px; font-size: 12px; line-height: 18px; height: auto; width: auto; }\n')
    c += '\n/* r8 forms: active-card glow, feature notes, Ur\'Khar */\n'
    c += '.charsheet .sheet-fcard { position: relative; }\n.charsheet .sheet-fc-glow { display: none; position: absolute; top: -1px; left: -1px; right: -1px; bottom: -1px; border: 2px solid var(--temp-dot, #aa5a1e); border-radius: 6px; box-shadow: 0 0 8px var(--temp-dot, #aa5a1e), inset 0 0 6px rgba(170,90,30,.35); pointer-events: none; }\n'
    c += ''.join(f'.charsheet .sheet-fcard.sheet-fc-{f} input.sheet-fc-cur[value="{f}"] + .sheet-fc-glow {{ display: block; }}\n' for f in forms)
    c += ('.charsheet .sheet-fcards > input.sheet-urkhar-flag:not([value="1"]) ~ .sheet-fcard.sheet-fc-urkhar { display: none !important; }\n'
          '.charsheet .sheet-fc-urnote { display: none; font-size: 11px; margin: 2px 0; opacity: .9; }\n'
          '.charsheet .sheet-fcards > input.sheet-urkhar-flag[value="1"] ~ .sheet-fc-gauru .sheet-fc-urnote { display: block; }\n'
          '.charsheet .sheet-fc-tw { position: relative; display: inline-flex; flex-direction: column; max-width: 100%; }\n'
          '.charsheet .sheet-fc-tw input.sheet-fc-tg { position: absolute; top: 0; left: 0; width: 100%; height: 19px; margin: 0; opacity: 0; cursor: pointer; z-index: 2; }\n'
          '.charsheet .sheet-fc-tw .sheet-fc-trait { cursor: pointer; align-self: flex-start; }\n'
          '.charsheet .sheet-fc-tw .sheet-fc-trait::after { content: ""; display: inline-block; margin-left: 4px; vertical-align: middle; border: 3px solid rgba(0,0,0,0); border-top: 4px solid currentColor; border-bottom: 0; opacity: .7; }\n'
          '.charsheet .sheet-fc-tw input.sheet-fc-tg:checked ~ .sheet-fc-trait { background: color-mix(in srgb, var(--temp-dot, #aa5a1e) 35%, rgba(0,0,0,0)); border-color: var(--temp-dot, #aa5a1e); }\n'
          '.charsheet .sheet-fc-tw .sheet-fc-desc { display: none; font-size: 11px; line-height: 1.35; margin: 3px 0 4px; padding: 4px 8px; border-left: 2px solid var(--temp-dot, #aa5a1e); background: rgba(0,0,0,.18); white-space: normal; user-select: text; }\n'
          '.charsheet .sheet-fc-tw:has(input.sheet-fc-tg:checked) { flex: 1 1 100%; }\n'
          '.charsheet .sheet-fc-tw input.sheet-fc-tg:checked ~ .sheet-fc-desc { display: block; }\n'
          '.charsheet .sheet-fcard .sheet-fc-traits { opacity: 1 !important; }\n'
          '.charsheet .sheet-fc-urtrack { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 12px; margin: 4px 0; font-size: 12px; }\n'
          '.charsheet .sheet-fc-urtrack label, .charsheet .sheet-fc-urtrack .sheet-ur-tl { display: inline-flex; align-items: center; gap: 4px; margin: 0; }\n'
          '.charsheet .sheet-fc-urtrack input.sheet-ur-turns { width: 34px !important; text-align: center; -webkit-appearance: textfield; -moz-appearance: textfield; appearance: textfield; pointer-events: none; }\n'
          '.charsheet .sheet-fc-urtrack input.sheet-ur-turns::-webkit-inner-spin-button, .charsheet .sheet-fc-urtrack input.sheet-ur-turns::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }\n'
          '.charsheet .sheet-fc-urinfo { flex: 1 1 100%; font-size: 11px; opacity: .85; }\n')
    js = r'''
        const urTurns = (d) => getAttrs(["urkhar_turns"], v => { setAttrs({urkhar_turns: Math.max(0, Math.min(30, (parseInt(v.urkhar_turns) || 0) + d))}); });
        on("clicked:urkhar_turn_dec", () => urTurns(-1)); on("clicked:urkhar_turn_inc", () => urTurns(1));
        on("sheet:opened change:urkhar_enabled", () => getAttrs(["urkhar_enabled"], v => setAttrs({urkhar_basu_note: v.urkhar_enabled === "1" ?
            "Form of the Firstborn: Basu-Im forces Ur'Khar now. It lasts as long as the Death Rage, with no conscious control, and does not use the once-per-story allowance." : ""}, {silent: true})));
        on("change:form", (ev) => { if (ev.sourceType !== "player" || ev.newValue !== "urkhar") return;
            getAttrs(["urkhar_enabled", "urkhar_used", "stamina", "potency"], v => { if (v.urkhar_enabled !== "1") return;
                const turns = (parseInt(v.stamina) || 0) + (parseInt(v.potency) || 0);
                const warn = v.urkhar_used === "1" ? " WARNING: voluntary Ur'Khar was already used this story." : "";
                setAttrs({urkhar_used: "1", urkhar_turns: turns});
                if (typeof startRoll === "function") startRoll(`&{template:cofd-entry} {{charname=@{character_name}}} {{gl_werewolf=1}} {{splat=werewolf}} {{kind=Ur'Khar}} {{name=Form of the Firstborn}} {{f_notes=Voluntary shift: ${turns} turns (Hishu Stamina + Primal Urge). Then shift form or face the killing-form consequences.${warn}}}`, r => { if (typeof finishRoll === "function") finishRoll(r.rollId); });
            }); });
'''
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    return h, c, missing
