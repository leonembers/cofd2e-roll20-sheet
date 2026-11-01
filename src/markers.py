"""Data-driven splat skill markers. Add a splat by adding an entry to MARKS."""
import json
# game_line -> (marker label, tooltip, verified?, source note, extra checkbox (key,label,tooltip) or None)
MARKS = {
 'hunter':   ('Asset', 'Asset Skill (Professional Training). At Professional Training ••, Asset Skills get 9-again.', True, 'HtV 2E Professional Training Merit', None),
 'werewolf': ('Auspice', 'Auspice Skill (Cahalith: Crafts/Expression/Persuasion; Elodoth: Empathy/Investigation/Politics; Irraka: Larceny/Stealth/Subterfuge; Ithaeur: Animal Ken/Medicine/Occult; Rahu: Brawl/Intimidation/Survival)', True, 'WtF 2E auspice table', ('mk', 'MK', 'Moon-Kissed: 9-again on this Auspice Skill (8-again if you already have 9-again). Spending Willpower gives +4 instead of +3 while your auspice moon is visible')),
 'vampire':  ('Favored', 'Marked/favoured Skill (custom: e.g. clan or covenant focus). Set the again quality if a Merit or Discipline grants one.', False, 'no Skill-marking rule in VtR 2E (clans favour Attributes)', None),
 'mage':     ('Rote', 'Rote Skill (Order Rote Skills; also Mudras)', False, 'MtAw 2E Order Rote Skills (from memory, not checked against the book)', None),
 'changeling': ('Favored', 'Marked Skill (custom: e.g. Seeming/Court/Mantle focus)', False, 'not checked', None),
 'promethean': ('Role', 'Marked Skill (custom: e.g. Refinement/Role focus)', False, 'not checked', None),
 'mummy':    ('Guild', 'Marked Skill (custom: e.g. Guild/Decree affinity)', False, 'not checked', None),
 'demon':    ('Cover', 'Marked Skill (custom: e.g. Incarnation/Cover focus)', False, 'not checked', None),
 'beast':    ('Family', 'Marked Skill (custom: e.g. Family/Hunger focus)', False, 'not checked', None),
 'deviant-the-renegades': ('Origin', 'Marked Skill (custom: e.g. Origin/Clade focus)', False, 'not checked', None),
 'geist':    ('Burden', 'Marked Skill (custom: e.g. Burden/Archetype focus)', False, 'not checked', None),
 'breeds2':  ('Proficiency', 'Skill Proficiency (Changing Breeds): mark the Skills your Breed is proficient in', False, 'Hurt Locker/Changing Breeds not checked', None),
 'mortal':   ('Marked', 'Marked Skill (custom)', False, 'custom', None),
}
# splat-skill check box next to each Skill name: only the lines whose rules mark Skills (type, tooltip, accent key in splat_colors.json)
CB = [('werewolf2', 'Auspice Skill'), ('breeds2', 'Favored Skill (Breed)'), ('hunter2', 'Asset Skill'), ('mage2', 'Order Rote Skill')]
CB_COLOR = {'werewolf2': 'werewolf', 'breeds2': 'breeds', 'hunter2': 'hunter', 'mage2': 'mage'}
AGAIN = [('', '–'), ('9', '9'), ('8', '8'), ('no10', '⊘')]

def html(sk):
    """collapsed skill line: read-only indicator badges only (hidden mirrors of the panel controls)"""
    cbs = ''.join(f'<input type="checkbox" class="skm-cb skm-{t} game-line {'werewolf ' if t == 'breeds2' else ''}{t}" name="attr_{sk}_mark" value="1" title="{tip}" />' for t, tip in CB)
    return (f'<span class="skm">{cbs}<input type="hidden" class="skm-markv" name="attr_{sk}_mark" value="0"/>'
            f'<input type="hidden" class="skm-mkv" name="attr_{sk}_mk" value="0"/>'
            f'<input type="hidden" class="skm-q" name="attr_{sk}_again" value=""/><span class="skm-badge"></span></span>')

ROLLTYPES = [('', 'Normal'), ('9', '9-again'), ('8', '8-again'), ('no10', 'No 10-again')]
def panel(sk):
    """controls inside the skill's drop-down panel (next to the Specialties field)"""
    opts = ''.join(f'<option value="{v}">{l}</option>' for v, l in ROLLTYPES)
    mk = MARKS['werewolf'][4][2]
    return (f'<div class="skm-panel"><label class="skm-p" title="Roll quality for this Skill">Roll type <select class="skm-psel" name="attr_{sk}_again">{opts}</select></label>'
            f'<label class="skm-p skm-pill game-line werewolf" title="{mk}"><input type="checkbox" name="attr_{sk}_mk" value="1"/><span>Moon-Kissed</span></label></div>')

def apply(h, skills):
    for sk in skills:
        a = f'name="act_{sk}_spec_toggle"'
        i = h.find(a)
        if i < 0: continue
        j = h.find('</button>', i) + len('</button>')
        h = h[:j] + html(sk) + h[j:]
        k = f'name="attr_{sk}_specialties" placeholder="Specialties, comma-separated" />'
        i2 = h.find(k, j); assert i2 > 0, sk
        e = i2 + len(k)
        h = h[:e] + panel(sk) + h[e:]
    return h

JS = r'''
        const updateSkillAgain = () => getAttrs(["rolltype","wp_spend","moon_visible"].concat(SKILLS.flatMap(sk => [`${sk}_flag`,`${sk}_again`,`${sk}_mark`,`${sk}_mk`])), v => {
            const sel = SKILLS.filter(sk => v[`${sk}_flag`] === "1");
            const rank = {"": 0, "no10": -1, "9": 1, "8": 2};
            let best = "", names = [], mk = false;
            sel.forEach(sk => { let q = v[`${sk}_again`] || ""; if (v[`${sk}_mk`] === "1" && rank[q] < 1) q = "9";
                if (v[`${sk}_mk`] === "1") mk = true;
                if (q && (rank[q] > rank[best] || (best === "" && q === "no10"))) best = q;
                if (q || v[`${sk}_mark`] === "1") names.push(sk); });
            setAttrs({skill_again: best, skill_again_names: names.join(", "), skill_mk: mk ? "1" : "0"}, {silent: true}, () => updateRollEff());
        });
        on("sheet:opened change:moon_visible " + SKILLS.flatMap(sk => [`change:${sk}_flag`,`change:${sk}_again`,`change:${sk}_mk`,`change:${sk}_mark`]).join(" "), updateSkillAgain);
'''

CSS = '''
/* collapsed row: one small badge, only when something non-default is set (never wraps) */
.sheet-skm { display: inline-flex; align-items: center; margin-left: 2px; vertical-align: middle; flex: 0 0 auto; white-space: nowrap; }
.sheet-skm-badge { display: none; height: 11px; min-width: 11px; padding: 0 2px; box-sizing: border-box; border-radius: 6px; font: bold 8px/11px Arial, sans-serif; text-align: center; color: #fff !important; background: var(--temp-dot, #555) !important; }
.sheet-skm-mkv[value="1"] ~ .sheet-skm-badge, .sheet-skm-q[value="9"] + .sheet-skm-badge, .sheet-skm-q[value="8"] + .sheet-skm-badge, .sheet-skm-q[value="no10"] + .sheet-skm-badge { display: inline-block; }
.sheet-skm-mkv[value="1"] ~ .sheet-skm-badge::after { content: "MK"; }
.sheet-skm-q[value="9"] + .sheet-skm-badge::after { content: "9"; }
.sheet-skm-q[value="8"] + .sheet-skm-badge::after { content: "8"; }
.sheet-skm-q[value="no10"] + .sheet-skm-badge { background: #a33 !important; }
.sheet-skm-q[value="no10"] + .sheet-skm-badge::after { content: "-10"; }
.sheet-skm-mkv[value="1"] ~ .sheet-skm-q[value="9"] + .sheet-skm-badge::after { content: "9 MK"; }
.sheet-skm-mkv[value="1"] ~ .sheet-skm-q[value="8"] + .sheet-skm-badge::after { content: "8 MK"; }
.sheet-skm-mkv[value="1"] ~ .sheet-skm-q[value="no10"] + .sheet-skm-badge::after { content: "-10 MK"; }
.sheet-darkmode .sheet-skm-badge, input.sheet-dm[value="1"] ~ .sheet-background .sheet-skm-badge { filter: brightness(1.6); }
/* drop-down panel: labelled controls (Rogue Trader-style detail line) */
.charsheet .sheet-spec-inner { flex-wrap: wrap; row-gap: 3px; }
.charsheet .sheet-spec-inner input.sheet-spec-input { flex: 1 1 100%; min-width: 0; }
.sheet-skm-panel { display: flex; flex-wrap: wrap; gap: 3px 6px; align-items: center; flex: 1 1 100%; }
.charsheet .sheet-spec-inner label.sheet-skm-p { display: inline-flex; align-items: center; gap: 3px; font-size: 11px; white-space: nowrap; margin: 0; }
.charsheet .sheet-skm-p select.sheet-skm-psel { width: auto !important; min-width: 0 !important; height: 18px !important; padding: 0 2px !important; margin: 0 !important; font-size: 11px !important; }
.charsheet .sheet-spec-inner label.sheet-skm-pill { position: relative; height: 16px; padding: 0 7px; border-radius: 8px; border: 1px solid rgba(128,128,128,.55); cursor: pointer; }
.charsheet .sheet-skm-pill input { position: absolute; inset: 0; opacity: 0; margin: 0; width: 100%; height: 100%; cursor: pointer; z-index: 1; }
.charsheet .sheet-skm-pill input:checked + span { font-weight: bold; }
.charsheet .sheet-spec-inner label.sheet-skm-pill:has(input:checked) { background: color-mix(in srgb, var(--temp-dot, #8b1010) 30%, rgba(0,0,0,0)); border-color: var(--temp-dot, #8b1010); }
'''

_COL = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__), 'splat_colors.json')))
CSS += ('.charsheet input.sheet-type:not([value="breeds2"]) ~ * .sheet-skm input.sheet-skm-cb.sheet-skm-breeds2.sheet-skm-breeds2 { display: none !important; }\n'
        '.charsheet.charsheet .sheet-skm input.sheet-skm-cb { -webkit-appearance: none; -moz-appearance: none; appearance: none; flex: 0 0 11px; width: 11px !important; height: 11px !important; min-width: 0 !important; '
        'margin: 0 3px 0 1px !important; padding: 0 !important; border: 1.5px solid currentColor; border-radius: 2px; background: rgba(0,0,0,0); box-sizing: border-box !important; cursor: pointer; vertical-align: middle; opacity: .8; position: static !important; }\n'
        '.charsheet.charsheet .sheet-skm input.sheet-skm-cb:checked { opacity: 1; }\n'
        + ''.join(f'.charsheet.charsheet .sheet-skm input.sheet-skm-cb.sheet-skm-{t}:checked {{ background: {_COL[k]} !important; border-color: {_COL[k]} !important; box-shadow: inset 0 0 0 1px rgba(255,255,255,.35); }}\n' for t, k in CB_COLOR.items()))
