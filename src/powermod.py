"""Pathfinder-feat-style power rows (Roll20 'Pathfinder Community' repeating_feat: name + inline short description on the
collapsed row, long text only when expanded, post-to-chat carries both) + optional dice-pool picker and Willpower / power-stat cost."""
import html

POWER_SECS = {'merits', 'tactics', 'endowments', 'disciplines', 'devotions', 'vrites', 'gifts', 'writes', 'rotes', 'praxes',
              'transmutations', 'bestowments', 'contracts', 'goblincontracts', 'ceremonies', 'utterances', 'affinities',
              'embeds', 'exploits', 'atavisms', 'nightmares', 'favors', 'bspecials', 'covers', 'vessels', 'keys', 'fetishes'}
ATTRS = [('intelligence', 'Int'), ('wits', 'Wit'), ('resolve', 'Res'), ('strength', 'Str'), ('dexterity', 'Dex'), ('stamina', 'Sta'),
         ('presence', 'Pre'), ('manipulation', 'Man'), ('composure', 'Com')]
MENTAL = ['academics', 'computer', 'crafts', 'investigation', 'medicine', 'occult', 'politics', 'science']
SKILLS = [('academics', 'Aca'), ('computer', 'Cmp'), ('crafts', 'Cra'), ('investigation', 'Inv'), ('medicine', 'Med'), ('occult', 'Occ'),
          ('politics', 'Pol'), ('science', 'Sci'), ('athletics', 'Ath'), ('brawl', 'Bra'), ('drive', 'Dri'), ('firearms', 'Fir'),
          ('larceny', 'Lar'), ('stealth', 'Ste'), ('survival', 'Sur'), ('weaponry', 'Wea'), ('animalken', 'AnK'), ('empathy', 'Emp'),
          ('expression', 'Exp'), ('intimidation', 'Inti'), ('persuasion', 'Pers'), ('socialize', 'Soc'), ('streetwise', 'Str'), ('subterfuge', 'Sub')]
TRAITS = [('_dots', "Dots"), ('potency', 'Pot'), ('morality', 'Mor')]
LBL = {**dict(ATTRS), **dict(SKILLS), **dict(TRAITS)}

def _sel(name, opts, none='—'):
    return f'<select name="attr_{name}"><option value="" selected>{none}</option>' + ''.join(f'<option value="{v}">{l}</option>' for v, l in opts) + '</select>'

SHORT = '<input type="text" class="entry-short" name="attr_short_desc" placeholder="short description" title="One-line summary (shown on the collapsed row and in chat)" />'
HEADCOST = '<span class="entry-cost" name="attr_cost_disp" title="Cost"></span>'
def body(section):
    trait_opts = [('_dots', "This entry's dots"), ('potency', 'Power stat (Potency, Primal Urge, Gnosis...)'), ('morality', 'Integrity / Morality track')]
    return (f'<div class="pw-box"><div class="pw-row"><b>Dice pool</b>'
            f'<label>Attribute {_sel("pp_attr", [(v, v.capitalize()) for v, _ in ATTRS])}</label>'
            f'<label>Skill / trait {_sel("pp_skill", [(v, v.capitalize() if v != "animalken" else "Animal Ken") for v, _ in SKILLS] + trait_opts)}</label>'
            f'<label>Modifier <input type="number" name="attr_pp_mod" value="0" /></label></div>'
            f'<div class="pw-row"><b>Cost</b><label>Willpower <input type="number" min="0" name="attr_cost_wp" value="0" /></label>'
            f'<label><span name="attr_pw_label">Power</span> <input type="number" min="0" name="attr_cost_pw" value="0" /></label>'
            f'<label class="pw-auto" title="Use the row roll button to roll and deduct the cost">'
            f'<input type="checkbox" name="attr_cost_auto" value="1" /> Deduct when rolled</label></div>'
            f'<div class="pw-hint">Picking an Attribute fills the dice pool below. The cost is shown on the row and in chat.</div></div>')

def patch(section, out_head, title, name_attr):
    """called by build.entry for power sections: returns (head_after_name, head_after_pool, extra template parts)"""
    return SHORT, HEADCOST, ['{{f_short=@{short_desc}}}', '{{f_costs=@{cost_disp}}}']

PROLL = '<input type="hidden" class="pw-auto-flag" name="attr_cost_auto" value="0" /><button type="action" class="entry-roll entry-proll" name="act_proll" title="Roll and pay the cost">&#127922;</button>'

def js(rating_map, titles={}):
    import json
    ab = json.dumps(LBL)
    return r'''
        /* ===== power rows: dice pool picker + cost (Pathfinder-feat style) ===== */
        const PW_SECS = %SECS%; const PW_TITLE = %TITLES%; const PW_RATING = %RATING%; const PW_AB = %AB%; const PW_MENTAL = %MENTAL%;
        const PW_STAT = {vampire2: "Vitae", werewolf2: "Essence", breeds2: "Essence", mage2: "Mana", promethean2: "Pyros", changeling2: "Glamour",
                         geist2: "Plasm", demon: "Aether", beast: "Satiety", mummy2: "Pillar", "deviant-the-renegades": "Instability"};
        const PW_POOL_STAT = ["vampire2", "werewolf2", "breeds2", "mage2", "promethean2", "changeling2", "geist2", "demon"];
        const pwRow = (sec, id, cb) => {
            const p = `repeating_${sec}_${id}_`; const r = PW_RATING[sec] || "rating";
            getAttrs([p + "pp_attr", p + "pp_skill", p + "pp_mod", p + "cost_wp", p + "cost_pw", p + r, "sheettype",
                      ...Object.keys(PW_AB).filter((k) => k[0] !== "_").reduce((a, k) => a.concat([k, k + "_eff"]), [])], (v) => {
                const u = {}; const lab = PW_STAT[v.sheettype] || "Power";
                const val = (k) => { if (k === "_dots") return parseInt(v[p + r]) || 0; const e = v[k + "_eff"]; const n = parseInt(e !== undefined && e !== "" ? e : v[k]) || 0;
                    if (!n && PW_AB[k] && Object.prototype.hasOwnProperty.call(PW_AB, k) && k !== "potency" && k !== "morality" && !["intelligence","wits","resolve","strength","dexterity","stamina","presence","manipulation","composure"].includes(k))
                        return PW_MENTAL.includes(k) ? -3 : -1;
                    return n; };
                const a = v[p + "pp_attr"], s = v[p + "pp_skill"], m = parseInt(v[p + "pp_mod"]) || 0;
                if (a) {
                    const parts = [PW_AB[a]]; let t = val(a);
                    if (s) { parts.push(PW_AB[s]); t += val(s); }
                    if (m) { parts.push(String(m)); t += m; }
                    t = Math.max(0, t);
                    u[p + "pool"] = parts.join("+").replace(/\+-/g, "-") + " = " + t; u[p + "pool_dice"] = t;
                    u[p + "roll_part"] = t > 0 ? "{{roll=[[{((@{" + p + "pool_dice}+?{@{modifiermacro}|0}+@{wound_penalty})@{rolltype}" : "";
                }
                const w = parseInt(v[p + "cost_wp"]) || 0, c = parseInt(v[p + "cost_pw"]) || 0;
                u[p + "cost_disp"] = [w ? w + " WP" : "", c ? c + " " + (lab.length <= 6 ? lab : lab.slice(0, 3)) : ""].filter(Boolean).join(" ");
                u[p + "pw_label"] = lab;
                setAttrs(u, {silent: true}, cb);
            });
        };
        const pwAll = () => PW_SECS.forEach((sec) => getSectionIDs(`repeating_${sec}`, (ids) => ids.forEach((id) => pwRow(sec, id))));
        PW_SECS.forEach((sec) => {
            const r = PW_RATING[sec] || "rating";
            on(`change:repeating_${sec}:pp_attr change:repeating_${sec}:pp_skill change:repeating_${sec}:pp_mod change:repeating_${sec}:cost_wp change:repeating_${sec}:cost_pw change:repeating_${sec}:${r}`, (ev) => {
                const id = ev.sourceAttribute.split("_")[2]; pwRow(sec, id);
            });
            on(`clicked:repeating_${sec}:proll`, (ev) => {
                const id = (ev.sourceAttribute || ev.triggerName).split("_")[2]; const p = `repeating_${sec}_${id}_`;
                getAttrs([p + "cost_wp", p + "cost_pw", p + "pool_dice", "sheettype", "vitae", "willpower", ...Array.from({length: 20}, (_, i) => `willpower_box${i + 1}`)], (v) => {
                    const nm = sec === "merits" ? "merit_name" : "name"; const n = parseInt(v[p + "pool_dice"]) || 0;
                    let tpl = `&{template:cofd-entry} {{charname=@{character_name}}} {{gl_@{game_line}=1}} {{splat=@{game_line}}} {{kind=${PW_TITLE[sec] || sec}}} {{name=@{${p}${nm}}}} {{f_short=@{${p}short_desc}}} {{f_costs=@{${p}cost_disp} (paid)}} {{f_pool=@{${p}pool}}} {{f_description=@{${p}description}}}`;
                    if (n > 0) tpl += ` {{roll=[[{((@{${p}pool_dice}+?{@{modifiermacro}|0}+@{wound_penalty})@{rolltype}`;
                    const u = {}; const w = parseInt(v[p + "cost_wp"]) || 0, c = parseInt(v[p + "cost_pw"]) || 0;
                    const max = parseInt(v.willpower) || 0; let free = 0; for (let i = 1; i <= max; i++) if (!["1", "on"].includes(v[`willpower_box${i}`])) free++;
                    const pool = parseInt(v.vitae) || 0, usesPool = PW_POOL_STAT.includes(v.sheettype);
                    const lack = [];
                    if (w > free) lack.push(`Willpower ${free}/${w} needed`);
                    if (c && usesPool && c > pool) lack.push(`${v.sheettype === "werewolf2" ? "Essence" : "power points"} ${pool}/${c} needed`);
                    if (lack.length) { startRoll(`&{template:cofd-entry} {{charname=@{character_name}}} {{splat=@{game_line}}} {{kind=${PW_TITLE[sec] || sec}}} {{name=@{${p}${nm}}}} {{f_short=Not activated: not enough ${lack.join(", ")}}}`, r => finishRoll(r.rollId)); return; }
                    if (c && usesPool) u.vitae = pool - c;
                    // Willpower: mark the next unmarked boxes (up to the Willpower max) as spent
                    let left = w;
                    for (let i = 1; i <= max && left > 0; i++) { if (!["1", "on"].includes(v[`willpower_box${i}`])) { u[`willpower_box${i}`] = "1"; left--; } }
                    if (w || c) tpl += ` {{wpst=Paid ${[w ? w + " WP" : "", c ? c + (v.sheettype === "werewolf2" ? " Essence" : " pts") : ""].filter(Boolean).join(" + ")}. Left: WP ${free - w}/${max}${usesPool ? ", " + (v.sheettype === "werewolf2" ? "Essence " : "pool ") + (pool - (usesPool ? c : 0)) : ""}}}`;
                    setAttrs(u);
                    if (typeof startRoll === "function") startRoll(tpl, (r) => { if (typeof finishRoll === "function") finishRoll(r.rollId); });
                });
            });
        });
        on("sheet:opened change:sheettype", pwAll);
'''.replace('%SECS%', json.dumps(sorted(POWER_SECS))).replace('%RATING%', json.dumps(rating_map)).replace('%AB%', ab).replace('%MENTAL%', json.dumps(MENTAL)).replace('%TITLES%', json.dumps(titles))

def css():
    S = '.charsheet .sheet-entry-section.sheet-pw'
    H = f'{S} .sheet-entry > .sheet-entry-head'
    o = [
      # two-line feat row: [name | badge | dots | pool | roll] / [short description ............ | cost]
      f'{H} {{ display: grid !important; grid-template-columns: minmax(0,1fr) 70px 76px 22px; grid-auto-rows: minmax(18px, auto); column-gap: 4px; row-gap: 0; padding-right: 4px !important; box-sizing: border-box; height: auto !important; min-height: 36px !important; overflow: hidden; align-items: center; }}',
      f'{H} > * {{ grid-row: 1; min-width: 0; }}',
      f'{H} > button.sheet-entry-post {{ grid-column: 1 !important; max-width: none !important; width: auto !important; height: auto !important; text-align: left; overflow: visible !important; text-overflow: clip !important; white-space: normal !important; overflow-wrap: break-word; word-break: normal; line-height: 1.15 !important; padding-top: 1px; padding-bottom: 1px; }}',
      f'{H} > button.sheet-entry-post * {{ white-space: normal !important; overflow: visible !important; text-overflow: clip !important; max-width: none !important; }}',
      f'{H} > .sheet-mcat-badge {{ grid-column: 2; }}',
      f'{H} > .sheet-dots {{ grid-column: 3; justify-content: flex-end; }}',
      f'{H} > .sheet-entry-pool {{ grid-row: 2; grid-column: 3 / 5; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: right; font-size: 10px !important; }}',
      f'{H} > button.sheet-entry-roll {{ grid-column: 4; width: 22px; justify-self: end; }}',
      f'{H} > input.sheet-entry-short {{ grid-row: 2; grid-column: 1; width: 100% !important; box-sizing: border-box; border: none !important; border-bottom: 1px dotted rgba(128,128,128,.45) !important; background: none !important; font-style: italic; font-size: 11px !important; opacity: .85; text-overflow: ellipsis; }}',
      f'{H} > .sheet-entry-cost {{ grid-row: 2; grid-column: 2; font-size: 10px; line-height: 18px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; text-align: right; opacity: .85; }}',
      f'{H} input.sheet-haspool[value="0"] + button.sheet-entry-roll {{ visibility: hidden; display: inline-block !important; }}',
      f'{H} > .sheet-entry-proll {{ display: none !important; }}',
      f'{H} > input.sheet-pw-auto-flag[value="1"] ~ .sheet-entry-proll {{ display: inline-block !important; }}',
      f'{H} > input.sheet-pw-auto-flag[value="1"] ~ button.sheet-entry-roll:not(.sheet-entry-proll) {{ display: none !important; }}',
      '.charsheet .sheet-pw-box { grid-column: 1 / -1; width: 100%; border: 1px solid rgba(128,128,128,.35); border-radius: 4px; padding: 3px 6px; margin: 4px 0; box-sizing: border-box; }',
      '.charsheet .sheet-entry-body .sheet-pw-row { display: grid !important; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 2px 8px; margin: 2px 0; align-items: end; }',
      '.charsheet .sheet-entry-body .sheet-pw-row > b { grid-column: 1 / -1; font-size: 11px; text-transform: uppercase; letter-spacing: .5px; opacity: .8; }',
      '.charsheet .sheet-entry-body .sheet-pw-row label { margin: 0 !important; min-width: 0; }',
      '.charsheet .sheet-entry-body .sheet-pw-row select, .charsheet .sheet-entry-body .sheet-pw-row input[type=number] { display: block; width: 100% !important; box-sizing: border-box; }',
      '.charsheet .sheet-entry-body .sheet-pw-row label.sheet-pw-auto { display: flex !important; align-items: center; gap: 4px; }',
      '.charsheet .sheet-entry-body .sheet-pw-row label.sheet-pw-auto input { width: auto !important; margin: 0 !important; }',
      '.charsheet .sheet-pw-hint { font-size: 10px; opacity: .7; }',
    ]
    return '\n'.join(o)

# ---------- compact roller + portrait ----------
import json as _json, os as _os
POOL_W = 236   # px: measured longest 3-part string "Empathy 10 + Enigmas 10 + Stamina 10 = 30" = 216.6px @12px Sorts Mill Goudy + 12px padding + 2px border + slack
PORTRAIT = ('<div class="roll-portrait" title="Portrait: the character\'s Roll20 avatar, or the image URL set in Config">'
            '<input type="hidden" class="portrait-flag" name="attr_portrait_src" value="" />'
            '<img class="rp-img" name="attr_portrait_src" src="" alt="" />'
            '<div class="rp-ph"><span class="rp-ph-c"></span><span class="rp-ph-t">No avatar</span></div></div>')
def roller(h):
    a = '<div class="diceroller-grid">'
    assert h.count(a) == 1
    h = h.replace(a, PORTRAIT + a, 1)
    old = 'const syncPortrait = () => getAttrs(["character_avatar"], v => {\n            let a = (v.character_avatar || "").trim();'
    assert old in h
    h = h.replace(old, 'const syncPortrait = () => getAttrs(["character_avatar", "portrait_url"], v => {\n            let a = ((v.portrait_url || "").trim() || (v.character_avatar || "").trim());', 1)
    h = h.replace('on("sheet:opened change:character_avatar", syncPortrait);', 'on("sheet:opened change:character_avatar change:portrait_url", syncPortrait);', 1)
    return h
PORTRAIT_CFG = ('<div class="cfg-row"><label>Portrait image URL <input type="text" name="attr_portrait_url" placeholder="blank = use the character avatar" /></label>'
                '<span class="hint">Shown beside the dice roller and on Notes. Leave blank to use the Roll20 avatar.</span></div>')

def roller_css(HERE, TYPE_OF):
    cols = _json.load(open(_os.path.join(HERE, 'splat_colors.json')))
    o = ['.charsheet .sheet-diceroller.sheet-rollbar { display: flex !important; flex-wrap: nowrap !important; align-items: stretch; gap: 8px; }',
         '.charsheet .sheet-rollbar > .sheet-diceroller-grid { flex: 1 1 auto; min-width: 0; }',
         '.charsheet .sheet-roll-portrait { flex: 0 0 96px; width: 96px; height: 112px; align-self: center; position: relative; box-sizing: border-box; border: 2px solid var(--rp, #8a6a3a); border-radius: 6px; box-shadow: inset 0 0 0 2px rgba(0,0,0,.35), 0 1px 3px rgba(0,0,0,.4); overflow: hidden; background: rgba(0,0,0,.15); }',
         '.charsheet .sheet-roll-portrait img.sheet-rp-img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: center top; }',
         '.charsheet .sheet-roll-portrait .sheet-rp-ph { display: none; position: absolute; top: 0; left: 0; right: 0; bottom: 0; flex-direction: column; align-items: center; justify-content: center; gap: 6px; background: radial-gradient(circle at 50% 40%, var(--rp, #8a6a3a) 0, rgba(0,0,0,0) 70%); }',
         '.charsheet .sheet-roll-portrait input.sheet-portrait-flag[value=""] ~ img.sheet-rp-img { display: none; }',
         '.charsheet .sheet-roll-portrait input.sheet-portrait-flag[value=""] ~ .sheet-rp-ph { display: flex; }',
         '.charsheet .sheet-rp-ph-c { width: 34px; height: 34px; border-radius: 50%; border: 2px solid rgba(255,255,255,.55); box-shadow: 0 18px 0 6px rgba(255,255,255,.18); }',
         '.charsheet .sheet-rp-ph-t { margin-top: 14px; font: 10px/12px Arial, sans-serif; opacity: .75; color: #ddd; }',
         # compact pool display: exactly the longest three-part string
         f'.charsheet .sheet-rollbar .sheet-rolldisplay {{ flex: 0 0 {POOL_W}px !important; width: {POOL_W}px !important; max-width: {POOL_W}px; }}',
         '.charsheet .sheet-rollbar .sheet-rolldisplay input.sheet-pooltxt { font-family: "Sorts Mill Goudy", "Goudy Old Style", Garamond, Georgia, serif !important; font-size: 12px !important; }',
         '.charsheet .sheet-rollbar .sheet-diceroller-options button { padding: 0 6px !important; }',
         '.charsheet .sheet-rollbar .sheet-diceroller-grid { row-gap: 3px !important; }']
    for k, c in cols.items():
        for t in TYPE_OF.get(k, []):
            o.append(f'.charsheet input.sheet-type[value="{t}"] ~ * .sheet-roll-portrait {{ --rp: {c}; }}')
    return '\n'.join(o)

LAYOUT_CSS = '''
.charsheet input[name="attr_deviations"], .charsheet input[name="attr_scar_variation"] { box-sizing: border-box; max-width: 100%; }
.charsheet label.sheet-wide textarea, .charsheet .sheet-midpane textarea, .charsheet .sheet-midpane input[type=text] { box-sizing: border-box; max-width: 100%; }
.charsheet .sheet-entry-section-head .sheet-subheader { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
'''
