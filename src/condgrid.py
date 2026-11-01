# Pathfinder-style toggle grid for CofD 2E Conditions & Tilts.
# (key, name, icon, kind, splat, persistent, effect, resolution, auto_mod)
# kind: C=Condition, PT=Personal Tilt, ET=Environmental Tilt. auto_mod = universal dice modifier auto-applied to rolls.
C = [
 ('blind','Blind','🙈','C','',0,'Lose sight; -3 to sight-based rolls (one eye) or -5 (both) per Blinded rules.','Sight restored.',0),
 ('broken','Broken','💔','C','',1,'Persistent: -2 to Social and Willpower-spending rolls; cannot use Willpower on violence.','Regain a Willpower dot or a story-scale recovery.',0),
 ('deprived','Deprived','🍞','C','',0,'-1 to all rolls while deprived of a fix/need.','Need is met.',-1),
 ('distracted','Distracted','💭','C','',0,'-2 to Mental and perception rolls.','Focus restored / scene ends.',0),
 ('frightened','Frightened','😱','C','',0,'Must flee or freeze; -2 to rolls that aren\'t escape.','Escape the source or fight it.',0),
 ('guilty','Guilty','😔','C','',0,'-2 to Resolve/Composure rolls resisting interrogation or manipulation.','Confess or atone.',0),
 ('inspired','Inspired','✨','C','',0,'Spend to gain the rote quality on one roll.','Use it on a roll.',0),
 ('lethargic','Lethargic','😴','C','',0,'-1 to Initiative, -1 to physical actions.','Rest.',0),
 ('madness','Madness','🌀','C','',1,'Persistent: Storyteller may impose penalties equal to Integrity loss.','Resolve the underlying cause.',0),
 ('obsession','Obsession','🎯','C','',1,'Persistent: +1 die to obsession, -2 to unrelated.','Obsession satisfied / let go.',0),
 ('shaken','Shaken','😰','C','',0,'Next failure is a dramatic failure (or -2 on next roll).','Accept a dramatic failure.',0),
 ('spooked','Spooked','👻','C','',0,'Supernatural seen; -2 to Composure-based rolls.','Investigate or flee.',0),
 ('swooning','Swooning','💘','C','',0,'-2 to act against the object of affection.','Act against them anyway.',0),
 ('wanton','Wanton','🍷','C','',0,'-2 to resist temptation.','Indulge the vice.',0),
 ('hunted','Hunted','🐺','C','',1,'Persistent: a supernatural foe stalks you.','The hunter is dealt with.',0),
 ('tempted','Tempted','😈','C','hunter2',0,'(Hunter) -2 to resist the temptation.','Give in or overcome it.',0),
 ('bestial','Bestial','🦇','C','vampire2',0,'(Vampire) -2 Social; Beast closer to the surface.','Feed or ride the wave.',0),
 ('tasked','Tasked','📜','C','vampire2',0,'(Vampire) Bound to complete a task.','Task complete.',0),
 ('kuruth','Kuruth','🔥','C','werewolf2',0,'(Werewolf) Death Rage; in Gauru, attack nearest.','Rage ends.',0),
 ('arm_wrack','Arm Wrack','💪','PT','',0,'-2 to arm-based actions; one arm unusable.','Medical treatment / heal damage.',0),
 ('leg_wrack','Leg Wrack','🦵','PT','',0,'-2 Dexterity-based, halve Speed; may be Knocked Down.','Heal / splint.',0),
 ('blinded','Blinded','😵','PT','',0,'-3 (one eye) / -5 (both) sight rolls; Defense halved if both.','End of scene / treatment.',0),
 ('deafened','Deafened','🙉','PT','',0,'-3 hearing-based perception; -2 combat if both ears.','Recovers.',0),
 ('drugged','Drugged','💊','PT','',0,'Ignore wound penalties; Defense/Wits penalties per drug (Storyteller).','Wears off.',0),
 ('insane','Insane','🤪','PT','',0,'Must succeed Resolve+Composure to act coherently.','Scene ends.',0),
 ('immobilized','Immobilized','⛓️','PT','',0,'Cannot move or use Defense.','Break free.',0),
 ('knocked_down','Knocked Down','⤵️','PT','',0,'Prone: no Defense vs close; ranged -2 to hit you.','Stand up (action).',0),
 ('poisoned','Poisoned','☠️','PT','',0,'Toxicity damage per turn; penalties per poison.','Antidote / time.',0),
 ('sick','Sick','🤒','PT','',0,'-1 (moderate) or worse to all actions.','Recover.',-1),
 ('stunned','Stunned','💫','PT','',0,'Lose next action; Defense halved.','Next turn.',0),
 ('beaten_down','Beaten Down','🥊','PT','',0,'Cannot take violent action without spending Willpower.','Scene ends or spend Willpower.',0),
 ('surrender','Surrender','🏳️','PT','',0,'Yields the fight; gains a Beat.','Fight ends.',0),
 ('blizzard','Blizzard','🌨️','ET','',0,'-1 to -3 sight-based; Speed halved.','Weather passes.',0),
 ('earthquake','Earthquake','🌋','ET','',0,'-1 to -5 all rolls; Dex+Athletics to stay standing.','Quake ends.',-1),
 ('extreme_cold','Extreme Cold','🥶','ET','',0,'-1 cumulative per hour exposed.','Warmth.',-1),
 ('extreme_heat','Extreme Heat','🥵','ET','',0,'-1 cumulative per hour exposed.','Shade / cooling.',-1),
 ('flooded','Flooded','🌊','ET','',0,'-2 physical actions; swimming rules.','Water recedes.',0),
 ('heavy_rain','Heavy Rain','🌧️','ET','',0,'-3 to sight/hearing perception.','Rain stops.',0),
 ('heavy_winds','Heavy Winds','🌬️','ET','',0,'-1 to -5 to physical actions and ranged attacks.','Winds die.',0),
 ('ice','Ice','🧊','ET','',0,'Speed halved; Dex+Athletics or Knocked Down.','Leave ice.',0),
 ('darkness','Darkness','🌑','ET','',0,'As Blinded for sight actions.','Light source.',0),
]
GROUPS = [('C','Conditions'),('PT','Personal Tilts'),('ET','Environmental Tilts')]
def cell(c):
    k,n,ic,kind,sp,per,eff,res,mod = c
    import html as H
    pcls = ' persistent' if per else ''
    gl = f' game-line {sp}' if sp else ''
    beat = 'Gain a Beat when resolved.' if kind=='C' else ''
    chat = (f'&{{template:cofd-entry}} {{{{kind={"Persistent Condition" if per else dict(GROUPS)[kind][:-1]}}}}} {{{{name={ic} {n}}}}}'
            f' {{{{f_description={H.escape(eff)}}}}} {{{{f_condition-resolution={H.escape(res)}}}}}' + (f' {{{{f_condition-beat={beat}}}}}' if beat else ''))
    return (f'<div class="cg-cell{pcls}{gl}"><input type="checkbox" class="cg-toggle" name="attr_cond_{k}" value="1" title="{H.escape(eff)}" />'
            f'<span class="cg-btn"><span class="cg-icon">{ic}</span>{H.escape(n)}{"<sup>P</sup>" if per else ""}</span>'
            f'<button type="roll" class="cg-chat" name="roll_cond_{k}" title="Post to chat" value="{H.escape(chat)}">💬</button></div>')
def grid_html():
    out = ['<div class="cond-grid-wrap"><div class="subheader">Conditions &amp; Tilts</div>',
           '<div class="cg-mods"><span>Active roll modifier: <b><span name="attr_cond_mod"></span></b></span>'
           '<input type="hidden" name="attr_cond_mod_manual" value="0" /><input type="hidden" name="attr_cond_mig_v1" value="" />'
           ' <span class="cg-note" name="attr_cond_note"></span></div>']
    for g, lab in GROUPS:
        out.append(f'<div class="cg-group"><div class="cg-glabel">{lab}</div><div class="cg-grid">' + ''.join(cell(c) for c in C if c[3]==g) + '</div></div>')
    out.append('<input type="hidden" name="attr_cond_mod" value="0" /></div>')
    return '\n'.join(out)
def worker_js():
    import json
    data = {c[0]: [c[1], c[8], c[6]] for c in C}
    return '''
        // Conditions & Tilts grid (Pathfinder-style)
        const COND = %s;
        const updateConds = () => getSectionIDs("conditions", ids => {
            const rn = ids.flatMap(id => [`repeating_conditions_${id}_c_active`, `repeating_conditions_${id}_c_mod`, `repeating_conditions_${id}_condition-title`]);
            getAttrs(Object.keys(COND).map(k => "cond_" + k).concat(["cond_mod_manual", "cond_mig_v1"], rn), v => {
                const u = {};
                if (v.cond_mig_v1 !== "1") { u.cond_mig_v1 = "1"; const m = parseInt(v.cond_mod_manual, 10) || 0;
                    if (m) { const id = generateRowID(), p = `repeating_conditions_${id}_`; u[p + "condition-title"] = "Manual modifier"; u[p + "c_mod"] = m; u[p + "c_active"] = "1"; u[p + "ctype"] = "Condition"; u.cond_mod_manual = 0; ids.push(id); v[p + "c_active"] = "1"; v[p + "c_mod"] = m; v[p + "condition-title"] = "Manual modifier"; } }
                let mod = 0; const notes = [];
                Object.keys(COND).forEach(k => { if (v["cond_" + k] === "1") { mod += COND[k][1]; notes.push(COND[k][0] + (COND[k][1] ? " (" + COND[k][1] + ")" : "")); } });
                ids.forEach(id => { const p = `repeating_conditions_${id}_`; if (v[p + "c_active"] === "1") { const m = parseInt(v[p + "c_mod"], 10) || 0; mod += m; notes.push((v[p + "condition-title"] || "Custom") + (m ? " (" + m + ")" : "")); } });
                Object.assign(u, { cond_mod: mod, cond_note: notes.length ? "Active: " + notes.join(", ") : "" });
                setAttrs(u);
            });
        });
        on(Object.keys(COND).map(k => "change:cond_" + k).join(" ") + " change:repeating_conditions:c_active change:repeating_conditions:c_mod remove:repeating_conditions sheet:opened", updateConds);
''' % json.dumps(data, ensure_ascii=False)
CSS = '''
.sheet-cond-grid-wrap { margin: 6px 0 10px; }
.sheet-cg-mods { font-size: 12px; margin: 4px 0; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.sheet-cg-mods input[type="number"] { width: 40px; }
.sheet-cg-note { font-style: italic; color: #7a1010; }
.sheet-cg-glabel { font-weight: bold; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #333; margin-top: 6px; }
.sheet-cg-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px; margin-top: 3px; }
.sheet-cg-cell { position: relative; display: flex; align-items: stretch; }
.sheet-cg-cell input.sheet-cg-toggle { position: absolute; opacity: 0; width: calc(100% - 22px); height: 100%; margin: 0; z-index: 2; cursor: pointer; }
.sheet-cg-btn { flex: 1; font-size: 11px; padding: 3px 4px; border: 1px solid #555; border-radius: 4px; background: rgba(255,255,255,.85); color: #555; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sheet-cg-icon { margin-right: 3px; filter: grayscale(1); opacity: .6; }
input.sheet-cg-toggle:checked + .sheet-cg-btn { background: #7a1010; color: #fff; border-color: #300; font-weight: bold; box-shadow: 0 0 4px #c33; }
input.sheet-cg-toggle:checked + .sheet-cg-btn .sheet-cg-icon { filter: none; opacity: 1; }
.sheet-cg-cell.sheet-persistent .sheet-cg-btn { border-style: double; border-width: 3px; }
button.sheet-cg-chat { width: 22px; padding: 0; font-size: 11px; background: none; border: none; }
'''
