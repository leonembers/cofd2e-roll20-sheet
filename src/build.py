#!/usr/bin/env python3
"""Build sheet.html / sheet.css / translation.json from the Roll20 community
'Chronicles of Darkness' sheet (base/) plus Leon's 2E multi-splat extensions.
Change IMG_BASE to wherever you host /workspace/cofd/roll20/img/ (https only)."""
import re, json, os, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extras, meritmod, powermod, moongift
IMG_BASE = "https://example.com/cofd-roll20/img"   # <-- REPLACE with your hosted image folder (no trailing slash)
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
B = os.path.join(ROOT, 'base')
h = open(os.path.join(B, 'CofD.html'), encoding='utf-8').read()
css = open(os.path.join(B, 'CofD.css'), encoding='utf-8').read()
tr = json.load(open(os.path.join(B, 'translation.json'), encoding='utf-8'))
NEWKEYS = {}
def T(key, text):
    NEWKEYS[key] = text
    return f'<span data-i18n="{key}">{html.escape(text)}</span>'
def must_sub(pat, rep, s, flags=0, count=1):
    n = re.subn(pat, rep, s, count=count, flags=flags)
    if n[1] == 0: raise SystemExit('pattern not found: ' + pat[:80])
    return n[0]

# ---------- 0. defaults: 2E mortal ----------
h = h.replace('name="attr_sheettype" value="mortal1"', 'name="attr_sheettype" value="mortal2"')
h = h.replace('name="attr_edition" value="1"', 'name="attr_edition" value="2"')

# ---------- 1. settings: only 2E Mortal/Hunter/Vampire/Werewolf + dice rule ----------
import phase2, markers, wolf, vamp
SPLATS = [('mortal2', 'Mortal (Chronicles of Darkness)', 'chronicles-of-darkness'),
          ('hunter2', 'Hunter: The Vigil', 'hunter-the-vigil'),
          ('vampire2', 'Vampire: The Requiem', 'vampire-the-requiem'),
          ('werewolf2', 'Werewolf: The Forsaken', 'werewolf-the-forsaken')] + [(k, t, i) for k, t, i, _ in phase2.SPLATS2]
# To add a splat later (e.g. mage2, promethean2): append here, add its sections in SPLAT_SECTIONS below.
btns = '\n'.join(f'            <button type="action" class="toggle active-{k}" name="act_sheet_type_{k}" title="{t}" data-i18n="{i}">{t}</button>' for k, t, i in SPLATS)
settings_block = f'''<div class="edition-label">{T("splat-u","SPLAT / GAME LINE (2nd Edition)")}</div>
        <div class="splat-select">
{btns}
        </div>
        <div class="spacer"></div>
        <div class="edition-label">{T("dice-rules-u","DICE RULES")}</div>
        <div class="dice-rule">
            <label>{T("success-on","Successes on")}:
                <select name="attr_success_target">
                    <option value="8" selected>{"8+ (Standard)"}</option>
                    <option value="7">{"7+ (House rule)"}</option>
                </select>
            </label>
            <input type="hidden" name="attr_rote_reroll" value="7" />
            <span class="hint">{T("dice-rule-hint","Applies to every sheet roll, entry roll, Perception and quick action. Chance dice always succeed only on 10. Again/Rote options are set in the roll bar.")}</span>
        </div>
        <div class="spacer"></div>
        '''
h = must_sub(r'<div class="edition-label" data-i18n="first-edition">.*?(?=<div class="edition-label" data-i18n="second-edition-translation-guides">)',
             settings_block, h, flags=re.S)
h = meritmod.config(h)
h = h.replace('data-i18n="settings">Settings</button>', 'title="Config: splat, rules options, merit effects">Config</button>')

# ---------- 2. success target in all dice expressions ----------
h = h.replace('}>8]]', '}>@{success_target}]]').replace('ro<7', 'ro<@{rote_reroll}')
h = h.replace('name="attr_rolltype" value=")d10!cs>10}>@{success_target}]]}}"', 'name="attr_rolltype" value=")d10!cs>10}>@{success_target}]]}}"')

# ---------- 3. dice roller panel -> inline roll bar (no separate panel) ----------
m = re.search(r'\s*<!-- DICE ROLLER -->\s*<div class="page page1 diceroller">.*?\n    </div>\n', h, flags=re.S)
dr = m.group(0); h = h.replace(dr, '\n')
dr = dr.replace('<div class="page page1 diceroller">', '<div class="page page1 page2 page3 powers conditions diceroller rollbar">')
dr = dr.replace('<div class="subheader" data-i18n="dice-roller-u">DICE ROLLER</div>', '')
PERC = ('<button type="roll" class="quick perception" name="roll_perception" title="Perception: Wits + Composure" '
        'value="&{template:cofd-entry} {{splat=@{game_line}}} {{kind=Perception}} {{name=Wits + Composure}} {{f_pool=Wits @{wits_eff} + Composure @{composure_eff} + Form @{form_perception} + Wounds @{wound_penalty}}} {{f_mod=Modifier ?{@{modifiermacro}|0}}} '
        '{{roll=[[{((@{wits}+@{wits_boost}+@{composure}+@{composure_boost}+@{form_perception}+?{@{modifiermacro}|0}+@{wound_penalty})@{rolltype}">'
        '&#128065; <span data-i18n="perception">Perception</span></button>')
NEWKEYS['perception'] = 'Perception'
dr = dr.replace('<div class="rollcontainer">', '<div class="corporeal span">' + PERC + '</div>\n            <div class="rollcontainer">', 1)
h = must_sub(r'(<!-- PAGE 1 -->)', lambda mm: dr + '\n    ' + mm.group(1), h)

# ---------- 4. header: per-splat logo art from Leon's PDFs ----------
h = re.sub(r'<img class="game-line hunter2" src="[^"]*">', f'<img class="game-line hunter2 leon-logo" src="{IMG_BASE}/hunter-logo.png">', h)
h = h.replace('<img class="game-line vampire" src=', '<img class="game-line vampire1" src=', 1)
h = h.replace('<img class="game-line werewolf" src=', '<img class="game-line werewolf1" src=', 1)
h = must_sub(r'(<img class="game-line hunter2 leon-logo"[^>]*>)', lambda mm: mm.group(1) +
    f'\n        <img class="game-line vampire2 leon-logo" src="{IMG_BASE}/vampire-logo.png">'
    f'\n        <img class="game-line werewolf2 leon-logo" src="{IMG_BASE}/werewolf-logo.png">', h)
h = h.replace('<div class="page page1 page2 page3 scars-variations conditions logo">', '<div class="page page1 page2 page3 scars-variations conditions powers logo">')

# ---------- 5. tab for new Powers & Gear page ----------
h = h.replace('<button type="action" class="toggle page-conditions 2nd" name="act_page_conditions" data-i18n="conditions">Conditions</button>',
    '<button type="action" class="toggle page-conditions 2nd" name="act_page_conditions" data-i18n="conditions">Conditions</button>\n'
    '    <button type="action" class="toggle page-powers" name="act_page_powers" data-i18n="powers-gear">Powers &amp; Gear</button>')
NEWKEYS['powers-gear'] = 'Powers & Gear'

# ---------- 6. expandable entry generator ----------
SECTIONS = []   # (section, has_rating)
def dots(attr, n=5, cls=''):
    b = [f'<input type="hidden" name="attr_{attr}" value="0" />', f'<button type="action" class="dot zero" name="act_{attr}-0">&times;</button>']
    for i in range(1, n + 1):
        ne = ' '.join(f'ne-{j}' for j in range(1, i))
        b.append(f'<button type="action" class="dot {ne}" name="act_{attr}-{i}"></button>')
    return f'<div class="dots {cls}">' + ''.join(b) + '</div>'

def entry(section, title_key, title, fields, rating='rating', rating_max=5, pool=True, name_attr='name', subtitle=None, default_open=True, extra_header=''):
    """fields: list of (attr, label, kind) kind in text|textarea|number|select:opt1;opt2"""
    PWR = section in powermod.POWER_SECS
    if PWR: pool = True
    SECTIONS.append(dict(section=section, rating=rating, pool=pool, name=name_attr, fields=fields, title=title, subtitle=subtitle))
    tpl = ['&{template:cofd-entry}', '{{splat=@{game_line}}}', f'{{{{kind={title}}}}}', f'{{{{name=@{{{name_attr}}}}}}}']
    if rating: tpl.append('{{dots=@{rating_dots}}}')
    if subtitle: tpl.append(f'{{{{subtitle=@{{{subtitle}}}}}}}')
    for a, lab, kind in fields:
        if a in ('pool_dice',): continue
        tpl.append(f'{{{{f_{a}=@{{{a}}}}}}}')
    if PWR: tpl[4:4] = ['{{f_short=@{short_desc}}}', '{{f_costs=@{cost_disp}}}']
    if pool: tpl.append('@{roll_part}')
    macro = html.escape(' '.join(tpl), quote=True)
    out = [f'<div class="entry-section {section}{" pw" if PWR else ""}">',
           f'<div class="entry-section-head"><span class="subheader">{T(title_key, title)}</span>'
           f'<button type="action" class="mini" name="act_expand_{section}" title="Expand all"><span class="pictos ic-down">3</span> {T("expand-all","all")}</button>'
           f'<button type="action" class="mini" name="act_collapse_{section}" title="Collapse all"><span class="pictos">3</span> {T("collapse-all","all")}</button></div>',
           f'<fieldset class="repeating_{section}">', '<div class="entry">',
           f'<input type="checkbox" class="entry-toggle" name="attr_show" value="1" {"checked" if default_open else ""} title="Expand / collapse" />',
           '<div class="entry-head">',
           f'<button type="roll" class="entry-post" name="roll_post" title="Post to chat" value="{macro}"><span class="entry-name" name="attr_{name_attr}"></span><span class="entry-ph">({T("new-entry","new entry")})</span></button>',
           powermod.SHORT if PWR else '', extra_header]
    if rating: out.append(dots(rating.replace('rating', 'rating'), rating_max) if rating == 'rating' else dots(rating, rating_max))
    if pool:
        out.append('<span class="entry-pool" name="attr_pool"></span>')
        out.append('<input type="hidden" class="haspool" name="attr_pool_dice" value="0" />'
                   '<button type="roll" class="entry-roll" name="roll_roll" title="Roll dice pool" value="'
                   + html.escape(f'&{{template:cofd-entry}} {{{{splat=@{{game_line}}}}}} {{{{kind={title}}}}} {{{{name=@{{{name_attr}}}}}}} {{{{f_pool=@{{pool}}}}}}{(' {{f_short=@{short_desc}}} {{f_costs=@{cost_disp}}}' if PWR else '')} {{{{o_dram=@{{o_dramatic}}}}}} {{{{o_fail=@{{o_failure}}}}}} {{{{o_succ=@{{o_success}}}}}} {{{{o_exc=@{{o_exceptional}}}}}} {{{{roll=[[{{((@{{pool_dice}}+?{{@{{modifiermacro}}|0}}+@{{wound_penalty}})@{{rolltype}}', quote=True)
                   + '">&#127922;</button>')
        if PWR: out.append(powermod.HEADCOST + powermod.PROLL)
    out.append('</div><div class="entry-body">')
    out.append(f'<label class="wide">{T("name","Name")}<input type="text" name="attr_{name_attr}" /></label>')
    for a, lab, kind in fields:
        key = 'lbl-' + a.replace('_', '-')
        if kind == 'textarea':
            out.append(f'<label class="wide">{T(key, lab)}<textarea name="attr_{a}"></textarea></label>')
        elif kind == 'number':
            out.append(f'<label>{T(key, lab)}<input type="number" name="attr_{a}" value="0" /></label>')
        elif kind == 'check':
            out.append(f'<label>{T(key, lab)}<input type="checkbox" name="attr_{a}" value="1" /></label>')
        elif kind.startswith('select:'):
            opts = ''.join(f'<option value="{o.split("=",1)[0]}">{o.split("=",1)[-1]}</option>' for o in kind[7:].split(';'))
            out.append(f'<label>{T(key, lab)}<select name="attr_{a}">{opts}</select></label>')
        else:
            out.append(f'<label>{T(key, lab)}<input type="text" name="attr_{a}" /></label>')
    if PWR: out.append(f'<label class="wide">{T("lbl-short","Short description")}<input type="text" name="attr_short_desc" /></label>' + powermod.body(section))
    if pool:
        out.append(f'<label>{T("lbl-pool","Dice pool (text)")}<input type="text" name="attr_pool" placeholder="e.g. Wits + Investigation" /></label>')
        out.append(f'<label>{T("lbl-pool-dice","Dice pool (number, 0 = no roll)")}<input type="number" name="attr_pool_dice" value="0" /></label>')
    if pool:
        out.append('<div class="outcomes"><div class="ohint">' + T("outcomes-hint", "Optional outcome text: only the matching one is shown when the pool is rolled") + '</div>')
        for a, lab in [('o_dramatic', 'Dramatic Failure'), ('o_failure', 'Failure'), ('o_success', 'Success'), ('o_exceptional', 'Exceptional Success')]:
            out.append(f'<label class="wide">{T("lbl-" + a.replace("_", "-"), lab)}<textarea name="attr_{a}" rows="2"></textarea></label>')
        out.append('</div>')
    out.append('<input type="hidden" name="attr_rating_dots" value="" /><input type="hidden" name="attr_roll_part" value="" />')
    out.append('</div></div></fieldset></div>')
    return '\n'.join(out)

SRC = ('source', 'Source / page', 'text'); DESC = ('description', 'Description', 'textarea'); NOTES = ('notes', 'Notes', 'textarea')

# ---------- 7. Merits -> expandable (keeps attr_merit_name / attr_merit) ----------
merits_html = entry('merits', 'merits', 'Merits',
    [('mcat', 'Category', meritmod.CAT_SELECT), ('prereq', 'Prerequisites', 'text'), SRC, ('cost', 'Cost / activation', 'text'), DESC, NOTES],
    rating='merit', name_attr='merit_name', default_open=False, extra_header=meritmod.EXTRA_HEADER)
merits_html = meritmod.merit_html(merits_html)
# merit name datalist from Leon's PDF combo /Opt list
fields = json.load(open(os.path.join(ROOT, '..', 'fields.json'))) if os.path.exists(os.path.join(ROOT, '..', 'fields.json')) else []
merit_opts = next((f['opts'] for f in fields if f['name'] == 'merits11'), [])
merit_opts = [o for o in merit_opts if o.strip() and not o.strip().startswith('-')]
h = must_sub(r'<div class="subheader" data-i18n="merits">Merits</div>\s*<fieldset class="repeating_merits">.*?</fieldset>',
             lambda mm: merits_html, h, flags=re.S)
h = meritmod.mid_tabs(h)
# merits header dots use attr "merit" -> rename dots inside entry() handled; rating_dots computed by worker

# ---------- 8. Conditions -> expandable ----------
cond_html = entry('conditions', 'custom-conditions', 'Custom Conditions & Tilts',
    [('ctype', 'Type', 'select:Condition;Persistent Condition;Tilt (personal);Tilt (environmental)'),
     ('condition-description', 'Effect', 'textarea'), ('condition-resolution', 'Resolution', 'textarea'),
     ('condition-beat', 'Beat', 'textarea'), ('c_mod', 'Roll modifier (applies while active)', 'number'), SRC], rating=None, pool=False, name_attr='condition-title', default_open=False,
    extra_header='<span class="cc-modpill" title="Roll modifier while active"><span name="attr_c_mod"></span></span><label class="cc-act" title="Active: counts toward the Active roll modifier"><input type="checkbox" name="attr_c_active" value="1" /> Active</label>')
import condgrid
cond_html = condgrid.grid_html() + '\n' + cond_html
h = must_sub(r'<fieldset class="repeating_conditions">.*?</fieldset>', lambda mm: cond_html, h, flags=re.S)

# ---------- 9. splat quick actions next to Potency / Morality ----------
FORMS = ['Hishu', 'Dalu', 'Gauru', "Ur'Khar", 'Urshul', 'Urhan']
form_opts = ''.join(f'<option value="{f.lower().replace(chr(39),"")}">{f}</option>' for f in FORMS)
def rollbtn(name, icon, label, pool_expr, pool_label, cls='', emote='', outs=None, kind='Quick Action'):
    o = ''.join(f' {{{{{k}={t}}}}}' for k, t in (outs or {}).items())
    v = ((f'/em {emote}\n' if emote else '') + f'&{{template:cofd-entry}} {{{{splat=@{{game_line}}}}}} {{{{kind={kind}}}}} {{{{name={label}}}}} {{{{f_pool={pool_label}}}}}{o} {{{{f_mod=[[?{{@{{modifiermacro}}|0}}]]}}}} '
         f'{{{{f_wounds=[[@{{wound_penalty}}]]}}}} {{{{roll=[[{{(({pool_expr}+?{{@{{modifiermacro}}|0}}+@{{wound_penalty}})@{{rolltype}}')
    return f'<button type="roll" class="quick {cls}" name="roll_{name}" title="{html.escape(pool_label)}" value="{html.escape(v, quote=True)}">{icon} {T("q-"+name, label)}</button>'
QUICK = f'''
                            <div class="quick-actions game-line werewolf2">
                                <label class="form-select">&#128058; {T("form","Form")}
                                    <select name="attr_form">{form_opts}</select></label>
                                {rollbtn("wasuim","&#128165;","Wasu-Im!","@{resolve}+@{composure}","Death Rage resistance: Resolve + Composure when a Kuruth trigger hits (pool not re-checked against the W:tF 2E book; apply trigger modifiers in the prompt)", cls="rage", kind="Death Rage", emote="@{character_name} snarls and fights for control as the Rage rises...", outs={"o_succ":"Resisted: you keep control, or may choose Wasu-Im, the Soft Rage.","o_exc":"Resisted: you keep control, or may choose Wasu-Im, the Soft Rage.","o_fail":"Basu-Im! Hard Rage: @{character_name} howls as the Hard Rage tears loose. Gauru, kill everything in reach.","o_dram":"Basu-Im! Hard Rage: @{character_name} howls as the Hard Rage tears loose. Friend and foe alike are prey.","f_notes":"@{urkhar_basu_note}"})}
                            </div>
                            <div class="quick-actions game-line vampire2">
                                {rollbtn("frenzy","&#129656;","Rötschreck!","@{resolve}+@{potency}","Resist Frenzy / Rötschreck (Resolve + Blood Potency)", cls="rage", kind="Frenzy", emote="@{character_name} struggles against Rötschreck as the Beast claws at the bars!", outs={"o_succ":"The Beast is held back, for now.","o_exc":"Mastery: the Beast cowers.","o_fail":"The Beast takes over: frenzy, or flee in terror.","o_dram":"The Beast takes over completely."})}
                                <button type="action" class="quick" name="act_spend_vitae" title="Spend 1 Vitae">&#129656;&minus;1 {T("vitae","Vitae")}</button>
                                {rollbtn("detachment","&#9878;","Detachment (Humanity)","@{morality}","Detachment (Humanity dice)")}
                            </div>
                            <div class="quick-actions game-line hunter2">
                                {rollbtn("breaking","&#9888;","Breaking Point","@{resolve}+@{composure}+@{integrity_bp_mod}","Breaking Point (Resolve + Composure + Integrity mod)")}
                            </div>
                            <div class="quick-actions game-line mortal2">
                                {rollbtn("breaking_m","&#9888;","Breaking Point","@{resolve}+@{composure}+@{integrity_bp_mod}","Breaking Point (Resolve + Composure + Integrity mod)")}
                            </div>
                            <input type="hidden" name="attr_form_perception" value="0" />
                            <input type="hidden" name="attr_integrity_bp_mod" value="0" />
'''
h = must_sub(r'(\n\s*<input type="hidden" class="if" name="attr_vitae_counter">)', lambda mm: QUICK + mm.group(1), h)
# ---------- numeric resource counter: [-] current / max [+] (replaces box track) ----------
h = must_sub(r'<div class="eq-1 vitae">\s*<input type="number" min="0" name="attr_vitae" />\s*</div>',
    lambda mm: '<div class="eq-1 vitae res-ctr">'
      '<button type="action" class="res-btn" name="act_vitae_dec" title="Spend 1 (minus one)">&minus;</button>'
      '<input type="number" min="0" class="res-cur" name="attr_vitae" title="Current pool: type to edit" />'
      '<span class="res-sep">/</span><span class="res-max" name="attr_vitae_max" title="Maximum (from Blood Potency, Primal Urge, Gnosis, etc.)"></span>'
      '<input type="hidden" name="attr_vitae_max" value="10" />'
      '<button type="action" class="res-btn" name="act_vitae_inc" title="Regain 1 (plus one, capped at max)">+</button></div>', h)
h = h.replace('<input type="hidden" class="if" name="attr_vitae_counter">', '<input type="hidden" class="if" name="attr_vitae_counter" value="1">', 1)
h = h.replace('name="attr_vitae_counter" value="0"', 'name="attr_vitae_counter" value="1"', 1)
RES_JS = r"""
        const RES_TBL = {vampire2:[5,10,11,12,13,15,20,25,30,50,75], werewolf2:[10,10,11,12,13,15,20,25,30,50,75], mage2:[10,11,12,13,15,20,25,30,50,75,75]};
        const resMax = (v) => { const t = RES_TBL[v.sheettype]; const p = Math.max(0, Math.min(10, parseInt(v.potency) || 0)); return t ? t[p] : Math.max(10, 10 + p); };
        const resSync = (extra) => getAttrs(["sheettype", "potency", "vitae", "vitae_max", "res_ctr_v1", ...Array.from({length: 30}, (_, i) => `vitae_box${i + 1}`)], (v) => {
            const mx = resMax(v); const u = {vitae_max: mx};
            if (v.res_ctr_v1 !== "1") { u.res_ctr_v1 = "1"; u.vitae_counter = "1";
                if (v.vitae === "" || v.vitae === undefined) { let n = 0; for (let i = 1; i <= 30; i++) if (["1", "on"].includes(v[`vitae_box${i}`])) n++; u.vitae = n; } }
            let cur = parseInt(u.vitae !== undefined ? u.vitae : v.vitae) || 0;
            if (extra) cur += extra;
            cur = Math.max(0, Math.min(mx, cur)); if (extra || String(cur) !== String(v.vitae)) u.vitae = cur;
            setAttrs(u);
        });
        on("sheet:opened change:potency change:sheettype", () => resSync(0));
        on("clicked:vitae_dec", () => resSync(-1));
        on("clicked:vitae_inc", () => resSync(1));
"""
h = must_sub(r'(\n\s*</script>\s*)$', lambda mm: '\n' + RES_JS + mm.group(1), h.rstrip() + '\n')
css += """
.charsheet .sheet-res-ctr { display: flex; align-items: center; justify-content: center; gap: 4px; font-family: inherit; }
.charsheet .sheet-res-ctr input.sheet-res-cur { width: 44px; text-align: center; font-weight: bold; font-size: 15px; }
.charsheet .sheet-res-ctr .sheet-res-sep, .charsheet .sheet-res-ctr .sheet-res-max { font-size: 15px; font-weight: bold; opacity: .85; }
.charsheet .sheet-res-ctr button.sheet-res-btn { width: 22px; height: 22px; padding: 0; line-height: 20px; border-radius: 50%; border: 1px solid currentColor; background: none; color: inherit; font-weight: bold; cursor: pointer; }
.charsheet .sheet-res-ctr button.sheet-res-btn:hover { background: rgba(128,128,128,.25); }
"""


# ---------- 10. Powers & Gear page ----------
def textblock(attr, key, label, rows=4):
    return f'<label class="block">{T(key,label)}<textarea name="attr_{attr}" rows="{rows}"></textarea></label>'
form_rows = [('strength', 'Strength'), ('dexterity', 'Dexterity'), ('stamina', 'Stamina'), ('manipulation', 'Manipulation'), ('size', 'Size'),
             ('defense', 'Defense'), ('initiative', 'Initiative'), ('speed', 'Speed'), ('health', 'Health'), ('perception', 'Perception')]
_TRAITS = {"Hishu": "Sheep&#8217;s Clothing", "Dalu": "Teeth/Claws +0L; Defense vs. Firearms; Mild Lunacy; Badass Motherfucker",
           "Gauru": "Teeth/Claws +2L (Init +3); Defense vs. Firearms; Full Lunacy; Regeneration; Rage; Primal Fear",
           "Urshul": "Teeth +2L/Claws +1L; Defense vs Firearms; Moderate Lunacy; Weaken the Prey", "Urhan": "Teeth +1L; Chase Down",
           "Ur'Khar": "Teeth/Claws +2L; Defense vs. Firearms; Full Lunacy; Regeneration; Rage; Primal Fear; once per story"}
_SHORT = {'strength': 'Str', 'dexterity': 'Dex', 'stamina': 'Sta', 'manipulation': 'Man', 'size': 'Size', 'defense': 'Def', 'initiative': 'Init', 'speed': 'Speed', 'health': 'Health', 'perception': 'Perc'}
ftab = ['<div class="fcards"><input type="hidden" class="urkhar-flag" name="attr_urkhar_enabled" value="0" />']
for f in FORMS:
    k = f.lower().replace(chr(39), "").replace("&#39;", "")
    traits = ''.join(f'<span class="fc-trait">{t.strip()}</span>' for t in _TRAITS.get(f, '').split('; ') if t.strip())
    ftab.append(f'<div class="fcard fc-{k}{" urkhar-col" if "Khar" in f else ""}"><input type="hidden" class="fc-cur" name="attr_form" value="hishu" />'
                f'<div class="fc-head"><span class="fc-name">{f}</span><span class="fc-badge">Active</span></div>'
                '<div class="fc-stats">' + ''.join(f'<span class="fc-stat"><b>{_SHORT[a]}</b><span name="attr_fv_{k}_{a}"></span></span>' for a, _ in form_rows) + '</div>'
                f'<div class="fc-traits">{traits}</div>'
                f'<textarea class="fc-notes" name="attr_form_notes_{k}" rows="2" placeholder="Notes on this form&#8217;s features"></textarea></div>')
ftab.append('</div><!--/forms-->')
REN_ICON = "https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@91c021fee3f302f9f895454d1d06c355c48164e3/icons/renown/"
GIFT_HDR = ('<input type="hidden" class="ren-flag" name="attr_renown" value="" /><span class="ren-ic ren-badge" title="Renown"></span>'
            '<input type="hidden" name="attr_rating" value="0" />')
renown = ''.join(f'<div class="renown-row"><span><span class="ren-ic ren-{r.lower()}" title="{r} Renown"></span>{T("renown-"+r.lower(), r)}</span>{dots("renown_"+r.lower())}</div>' for r in ['Purity', 'Glory', 'Honor', 'Wisdom', 'Cunning'])

POWERS = f'''
    <!-- POWERS & GEAR (Leon's 2E multi-splat extension) -->
    <div class="page powers">
      <div class="leon-page">
        <div class="section-header">{T("powers-gear-u","POWERS & GEAR")}</div>
        {phase2.header_html(T)}

        <div class="game-line hunter2">
          {entry('tactics','tactics','Tactics',[('category','Category','select:Mental;Physical;Social;Other'),('requirements','Requirements / roles','text'),('action','Action','text'),('cost','Cost','text'),SRC,DESC,NOTES],rating=None)}
          {entry('endowments','endowments','Endowments',[('etype','Endowment type','text'),('loadout','Loadout','text'),('cost','Cost','text'),('action','Action / duration','text'),SRC,DESC,NOTES])}
          <div class="two-col">{textblock('the_code','the-code','The Code',7)}{textblock('touchstones','touchstones','Touchstones',7)}</div>
        </div>

        <div class="game-line vampire2">
          {entry('disciplines','disciplines','Disciplines',[('inclan','In-clan','check'),('powers','Powers known','textarea'),SRC,DESC,NOTES],pool=False)}
          {entry('devotions','devotions','Devotions',[('disciplines','Disciplines','text'),('cost','Cost','text'),('action','Action / duration','text'),SRC,DESC,NOTES],rating=None)}
          {entry('vrites','rites-miracles','Rites / Miracles',[('rtype','Tradition','select:Crúac;Theban Sorcery;Coils of the Dragon;Other'),('cost','Cost','text'),('action','Action / target','text'),SRC,DESC,NOTES])}
          {entry('banes','banes','Banes',[DESC,NOTES],rating=None,pool=False)}
          {entry('vtouchstones','touchstones','Touchstones',[('humanity','Humanity dot','number'),('attached','Attached / detached','text'),DESC],rating=None,pool=False)}
          {entry('vinculum','vinculum','Vinculum',[('stage','Stage (1-3)','number'),NOTES],rating=None,pool=False,default_open=False)}
        </div>

        <div class="game-line werewolf2">
          <div class="subheader">{T("forms","Forms")}</div>
          <input type="hidden" class="urkhar-flag" name="attr_urkhar_enabled" value="0" />
          {''.join(ftab)}
          <div class="two-col">
            <div class="wolf-lcol"><div class="subheader">{T("renown","Renown")}</div>{renown}
              <div class="wolf-ts">
              <label>{T("flesh-touchstone","Flesh Touchstone")}<input type="text" name="attr_flesh_touchstone" /></label>
              <label>{T("spirit-touchstone","Spirit Touchstone")}<input type="text" name="attr_spirit_touchstone" /></label>
              </div></div>
            <div class="wolf-rcol"><div class="subheader">{T("kuruth-triggers","Kuruth Triggers")}</div>
              <label>{T("passive","Passive")}<textarea class="trig-ta" rows="2" name="attr_kuruth_passive"></textarea></label>
              <label>{T("common","Common")}<textarea class="trig-ta" rows="2" name="attr_kuruth_common"></textarea></label>
              <label>{T("specific","Specific / Active (from Harmony)")}<textarea class="trig-ta" rows="2" name="attr_kuruth_specific"></textarea></label>
            </div>
          </div>
          {entry('gifts','gifts','Gifts',[('gtype','Gift type','select:Moon;Shadow;Wolf;Other'),('facet','Gift / Facet','text'),('renown','Renown','select:Purity;Glory;Honor;Wisdom;Cunning;—'),('cost','Cost','text'),('action','Action / duration','text'),SRC,DESC,NOTES],rating=None,extra_header=GIFT_HDR)}
          {entry('writes','rites','Rites',[('rtype','Rite type','select:Wolf Rite;Pack Rite;Other'),('action','Action / duration','text'),SRC,DESC,NOTES])}
          {entry('totem','totem','Totem',[('attributes','Power / Finesse / Resistance','text'),('stats','Willpower / Essence / Initiative / Defense / Speed / Size / Corpus','textarea'),('influences','Influences / Numina','textarea'),('bonuses','Bonuses','textarea'),('ban','Ban / Bane','text'),('aspiration','Aspiration','text')],rating=None,pool=False,default_open=False)}
        </div>

        {phase2.sections(entry, T, SRC, DESC, NOTES)}
        {entry('equipment','equipment','Equipment',[('durability','Durability','text'),('structure','Structure','text'),('esize','Size','text'),('cost','Cost','text'),('dice_bonus','Dice bonus','text'),NOTES],rating=None,pool=False,default_open=False)}
        <div class="game-line werewolf2">{entry('fetishes','fetishes','Fetishes',[('spirit','Bound spirit','text'),SRC,DESC,NOTES],rating_max=5,default_open=False)}</div>
        {entry('expmerits','expanded-merits','Expanded Merits',[DESC,NOTES],rating=None,pool=False,default_open=False)}
      </div>
    </div>
'''
h = must_sub(r'(\n\s*<!-- PAGE 4, CONDITIONS -->)', lambda mm: POWERS + mm.group(1), h)
h = extras.weapons_armor_page1(h, entry, html, T)
h, NOTES_JS = extras.notes_page(entry, h, T)
h, FD_JS = extras.forms_details(h, T)

# ---------- 11. roll template ----------
TPL_FIELDS = [('f_short', 'Summary'), ('subtitle', 'Type'), ('f_costs', 'Cost'), ('f_mcat', 'Category'), ('f_level', 'Dot level'), ('f_ctype', 'Type'), ('f_category', 'Category'), ('f_etype', 'Type'), ('f_gtype', 'Gift'), ('f_rtype', 'Type'), ('f_facet', 'Facet'), ('f_renown', 'Renown'),
              ('f_inclan', 'In-clan'), ('f_disciplines', 'Disciplines'), ('f_prereq', 'Prerequisites'), ('f_requirements', 'Requirements'), ('f_loadout', 'Loadout'), ('f_cost', 'Cost'), ('f_action', 'Action'),
              ('f_damage', 'Damage'), ('f_range', 'Range'), ('f_clip', 'Clip'), ('f_wsize', 'Size'), ('f_strength', 'Strength'), ('f_initiative', 'Init'), ('f_durability', 'Durability'), ('f_structure', 'Structure'),
              ('f_esize', 'Size'), ('f_dice_bonus', 'Dice bonus'), ('f_humanity', 'Humanity'), ('f_attached', 'Status'), ('f_stage', 'Stage'), ('f_attributes', 'Attributes'), ('f_ban', 'Ban'), ('f_aspiration', 'Aspiration'),
              ('f_mods', 'Form'), ('f_shift', 'Shift'), ('f_pool', 'Dice pool'), ('f_wounds', 'Penalties'), ('f_init', 'Initiative'), ('f_source', 'Source')]
rows = ''.join(f'{{{{#{k}}}}}<tr><th>{lab}</th><td>{{{{{k}}}}}</td></tr>{{{{/{k}}}}}' for k, lab in TPL_FIELDS)
longs = ''.join(f'{{{{#{k}}}}}<div class="long"><b>{lab}</b>{{{{{k}}}}}</div>{{{{/{k}}}}}' for k, lab in
                [('f_description', ''), ('f_condition-description', 'Effect: '), ('f_condition-resolution', 'Resolution: '), ('f_condition-beat', 'Beat: '), ('f_powers', 'Powers: '), ('f_stats', ''), ('f_influences', ''), ('f_bonuses', ''), ('f_notes', 'Notes: ')])
TPL = f'''
    <rolltemplate class="sheet-rolltemplate-cofd-entry">
        <div class="ce">
            {{{{#gl_mortal}}}}<div class="ce-band ce-band-mortal"></div>{{{{/gl_mortal}}}}{{{{#gl_hunter}}}}<div class="ce-band ce-band-hunter"></div>{{{{/gl_hunter}}}}{{{{#gl_vampire}}}}<div class="ce-band ce-band-vampire"></div>{{{{/gl_vampire}}}}{{{{#gl_werewolf}}}}<div class="ce-band ce-band-werewolf"></div>{{{{/gl_werewolf}}}}{{{{#gl_mage}}}}<div class="ce-band ce-band-mage"></div>{{{{/gl_mage}}}}{{{{#gl_promethean}}}}<div class="ce-band ce-band-promethean"></div>{{{{/gl_promethean}}}}{{{{#gl_changeling}}}}<div class="ce-band ce-band-changeling"></div>{{{{/gl_changeling}}}}{{{{#gl_geist}}}}<div class="ce-band ce-band-geist"></div>{{{{/gl_geist}}}}{{{{#gl_mummy}}}}<div class="ce-band ce-band-mummy"></div>{{{{/gl_mummy}}}}{{{{#gl_demon}}}}<div class="ce-band ce-band-demon"></div>{{{{/gl_demon}}}}{{{{#gl_beast}}}}<div class="ce-band ce-band-beast"></div>{{{{/gl_beast}}}}{{{{#gl_deviant-the-renegades}}}}<div class="ce-band ce-band-deviant-the-renegades"></div>{{{{/gl_deviant-the-renegades}}}}
            <div class="ce-head">{{{{#charname}}}}<span class="ce-char">{{{{charname}}}}</span>{{{{/charname}}}}{{{{#kind}}}}<span class="ce-kind">{{{{kind}}}}</span>{{{{/kind}}}}<span class="ce-name">{{{{name}}}}</span>{{{{#dots}}}}<span class="ce-dots">{{{{dots}}}}</span>{{{{/dots}}}}{{{{#dmg_B}}}}<span class="ce-badge ce-b" title="Bashing">B</span>{{{{/dmg_B}}}}{{{{#dmg_L}}}}<span class="ce-badge ce-l" title="Lethal">L</span>{{{{/dmg_L}}}}{{{{#dmg_A}}}}<span class="ce-badge ce-a" title="Aggravated">A</span>{{{{/dmg_A}}}}</div>
            <table>{rows}</table>
            {{{{#roll}}}}<div class="ce-roll"><div class="ce-big">{{{{roll}}}}</div><div class="ce-sl">successes</div>
              {{{{#^exc3}}}}{{{{#rollGreater() roll 4}}}}<div class="ce-exc">Exceptional success</div>{{{{#o_exc}}}}<div class="ce-out">{{{{o_exc}}}}</div>{{{{/o_exc}}}}{{{{/rollGreater() roll 4}}}}{{{{/^exc3}}}}
              {{{{#exc3}}}}{{{{#rollGreater() roll 2}}}}<div class="ce-exc">Exceptional success (3+, risked WP)</div>{{{{#o_exc}}}}<div class="ce-out">{{{{o_exc}}}}</div>{{{{/o_exc}}}}{{{{/rollGreater() roll 2}}}}{{{{#rollBetween() roll 1 2}}}}<div class="ce-succ">Success</div>{{{{#o_succ}}}}<div class="ce-out">{{{{o_succ}}}}</div>{{{{/o_succ}}}}{{{{/rollBetween() roll 1 2}}}}{{{{/exc3}}}}
              {{{{#^exc3}}}}{{{{#rollBetween() roll 1 4}}}}<div class="ce-succ">Success</div>{{{{#o_succ}}}}<div class="ce-out">{{{{o_succ}}}}</div>{{{{/o_succ}}}}{{{{/rollBetween() roll 1 4}}}}{{{{/^exc3}}}}
              {{{{#rollLess() roll 1}}}}
                {{{{#chance}}}}{{{{#rollWasFumble() roll}}}}<div class="ce-dram">Dramatic failure</div>{{{{#o_dram}}}}<div class="ce-out">{{{{o_dram}}}}</div>{{{{/o_dram}}}}{{{{/rollWasFumble() roll}}}}
                  {{{{#^rollWasFumble() roll}}}}<div class="ce-fail">Failure</div>{{{{#o_fail}}}}<div class="ce-out">{{{{o_fail}}}}</div>{{{{/o_fail}}}}{{{{/^rollWasFumble() roll}}}}{{{{/chance}}}}
                {{{{#^chance}}}}<div class="ce-fail">Failure</div>{{{{#o_fail}}}}<div class="ce-out">{{{{o_fail}}}}</div>{{{{/o_fail}}}}{{{{/^chance}}}}
              {{{{/rollLess() roll 1}}}}
              {{{{#wpspend}}}}{{{{#mk4}}}}<div class="ce-flag">+4 dice: spent 1 Willpower (Moon-Kissed, auspice moon visible)</div>{{{{/mk4}}}}{{{{#^mk4}}}}<div class="ce-flag">+3 dice: spent 1 Willpower (mark it on the sheet)</div>{{{{/^mk4}}}}{{{{/wpspend}}}}{{{{#skq}}}}<div class="ce-flag ce-skq">Skill quality: {{{{skq}}}}</div>{{{{/skq}}}}
              {{{{#risk}}}}<div class="ce-risk"><b>Risked Willpower:</b> {{{{risk}}}}
                {{{{#rollGreater() roll 0}}}}<br>Success: gain 1 Beat; regain the risked Willpower +1 more (up to max).{{{{/rollGreater() roll 0}}}}
                {{{{#rollLess() roll 1}}}}<br>Failure: treat as a dramatic failure; gain 2 Beats; the risked Willpower stays spent.{{{{/rollLess() roll 1}}}}</div>{{{{/risk}}}}
              {{{{#chance}}}}<div class="ce-flag">Chance die</div>{{{{/chance}}}}{{{{#9again}}}}<div class="ce-flag">9-again</div>{{{{/9again}}}}{{{{#8again}}}}<div class="ce-flag">8-again</div>{{{{/8again}}}}
            </div>{{{{/roll}}}}
            {longs}
        </div>
    </rolltemplate>
'''
h = must_sub(r'(\n\s*<script type="text/worker">)', lambda mm: TPL + mm.group(1), h)

# ---------- 12. worker additions ----------
sec_list = json.dumps([s['section'] for s in SECTIONS])
rating_map = json.dumps({s['section']: s['rating'] for s in SECTIONS if s['rating']})
pool_secs = json.dumps([s['section'] for s in SECTIONS if s['pool']])
W = r'''
        /* ===== Leon 2E multi-splat extensions ===== */
        const LEON_SECTIONS = %SECS%;
        const LEON_RATING = %RATING%;
        const LEON_POOL = %POOL%;
        const dotStr = (n) => { n = parseInt(n) || 0; return n > 0 ? "\u25CF".repeat(n) : ""; };
        LEON_SECTIONS.forEach((sec) => {
            on(`clicked:expand_${sec} clicked:collapse_${sec}`, (ev) => {
                const val = ev.triggerName.indexOf("expand") >= 0 ? "1" : "0";
                getSectionIDs(`repeating_${sec}`, (ids) => {
                    const u = {}; ids.forEach((id) => u[`repeating_${sec}_${id}_show`] = val); setAttrs(u, {silent: true});
                });
            });
        });
        Object.entries(LEON_RATING).forEach(([sec, attr]) => {
            on(`change:repeating_${sec}:${attr}`, (ev) => {
                const p = ev.sourceAttribute.replace(new RegExp(`_${attr}$`), "");
                setAttrs({[`${p}_rating_dots`]: dotStr(ev.newValue)}, {silent: true});
            });
        });
        LEON_POOL.forEach((sec) => {
            on(`change:repeating_${sec}:pool_dice`, (ev) => {
                const p = ev.sourceAttribute.replace(/_pool_dice$/, "");
                const n = parseInt(ev.newValue) || 0;
                setAttrs({[`${p}_roll_part`]: n > 0 ? "{{roll=[[{((@{" + p + "_pool_dice}+?{@{modifiermacro}|0}+@{wound_penalty})@{rolltype}" : ""}, {silent: true});
            });
        });
        // the merit/rating dot buttons in our sections
        ["tactics","endowments","disciplines","vrites","gifts","writes"].forEach((sec) => {
            for (let d = 0; d <= 5; d++) on(`clicked:repeating_${sec}:rating-${d}`, () => setAttrs({[`repeating_${sec}_rating`]: d}));
        });
        ["purity","glory","honor","wisdom","cunning"].forEach((r) => {
            for (let d = 0; d <= 5; d++) on(`clicked:renown_${r}-${d}`, () => setAttrs({[`renown_${r}`]: d}));
        });
        // dice rule
        on("change:success_target sheet:opened", () => {
            getAttrs(["success_target"], (v) => {
                const t = parseInt(v.success_target) === 7 ? 7 : 8;
                setAttrs({success_target: t, rote_reroll: t - 1}, {silent: true});
            });
        });
        // Hunter / Mortal breaking point modifier from Integrity (CofD 2E)
        on("change:morality sheet:opened", () => {
            getAttrs(["morality"], (v) => {
                const i = parseInt(v.morality) || 0;
                const m = i >= 8 ? 2 : i >= 6 ? 1 : i >= 4 ? 0 : i >= 2 ? -1 : -2;
                setAttrs({integrity_bp_mod: m}, {silent: true});
            });
        });
        // Vampire: spend Vitae
        on("clicked:spend_vitae", () => getAttrs(["vitae"], (v) => setAttrs({vitae: Math.max(0, (parseInt(v.vitae) || 0) - 1)})));
        // Werewolf forms (Leon's sheet values; Ur'Khar variant changes Gauru and adds Ur'Khar)
        const FORM_MODS = {
            hishu:  {strength:0,dexterity:0,stamina:0,manipulation:0,size:0,initiative:0,speed:0,health:0,perception:1},
            dalu:   {strength:1,dexterity:0,stamina:1,manipulation:-1,size:1,initiative:0,speed:1,health:2,perception:2},
            gauru:  {strength:3,dexterity:1,stamina:2,manipulation:0,size:2,initiative:1,speed:4,health:4,perception:3},
            urshul: {strength:2,dexterity:2,stamina:2,manipulation:-1,size:1,initiative:2,speed:7,health:3,perception:3},
            urhan:  {strength:0,dexterity:2,stamina:1,manipulation:-1,size:-1,initiative:2,speed:5,health:0,perception:4},
            urkhar: {strength:3,dexterity:2,stamina:2,manipulation:0,size:4,initiative:2,speed:8,health:6,perception:3}
        };
        const GAURU_URKHAR_VARIANT = {strength:2,dexterity:1,stamina:2,manipulation:0,size:2,initiative:1,speed:3,health:4,perception:3};
        const FORM_LABEL = {hishu:"Hishu",dalu:"Dalu",gauru:"Gauru",urshul:"Urshul",urhan:"Urhan",urkhar:"Ur'Khar"};
        const updateForms = () => {
            getAttrs(["strength","dexterity","stamina","manipulation","wits","composure","athletics","base_size","form","urkhar_enabled","sheettype"], (v) => {
                const n = (k) => parseInt(v[k]) || 0;
                const size = parseInt(v.base_size) || 5;
                const ur = v.urkhar_enabled === "1";
                const u = {};
                Object.keys(FORM_MODS).forEach((f) => {
                    const m = (f === "gauru" && ur) ? GAURU_URKHAR_VARIANT : FORM_MODS[f];
                    const str = n("strength")+m.strength, dex = n("dexterity")+m.dexterity, sta = n("stamina")+m.stamina, sz = size+m.size;
                    u[`fv_${f}_strength`] = str; u[`fv_${f}_dexterity`] = dex; u[`fv_${f}_stamina`] = sta;
                    u[`fv_${f}_manipulation`] = n("manipulation")+m.manipulation; u[`fv_${f}_size`] = sz;
                    u[`fv_${f}_defense`] = Math.min(n("wits"), dex) + n("athletics");
                    u[`fv_${f}_initiative`] = n("dexterity") + n("composure") + m.initiative;
                    u[`fv_${f}_speed`] = n("strength") + n("dexterity") + 5 + m.speed;
                    u[`fv_${f}_health`] = n("stamina") + size + m.health;
                    u[`fv_${f}_perception`] = n("wits") + n("composure") + m.perception;
                });
                let form = v.form || "hishu"; if (form === "urkhar" && !ur) form = "gauru";
                const m = (form === "gauru" && ur) ? GAURU_URKHAR_VARIANT : FORM_MODS[form];
                const isWolf = (v.sheettype || "").indexOf("werewolf") === 0 || v.sheettype === "breeds2";
                u.form_label = FORM_LABEL[form];
                u.form_perception = isWolf ? m.perception : 0;
                u.form_summary = Object.entries(m).filter(([k, x]) => x).map(([k, x]) => `${k} ${x > 0 ? "+" : ""}${x}`).join(", ") || "no modifiers";
                u.form_size = isWolf ? m.size : 0; u.form_speed_extra = isWolf ? m.speed - m.strength - m.dexterity : 0; u.form_init_extra = isWolf ? m.initiative - m.dexterity : 0;
                if (isWolf) { u.strength_boost = m.strength; u.dexterity_boost = m.dexterity; u.stamina_boost = m.stamina; u.manipulation_boost = m.manipulation; }
                setAttrs(u);
            });
        };
        on("change:form change:urkhar_enabled change:strength change:dexterity change:stamina change:manipulation change:wits change:composure change:athletics change:base_size change:sheettype sheet:opened", updateForms);
'''.replace('%SECS%', sec_list).replace('%RATING%', rating_map).replace('%POOL%', pool_secs)
W = W + condgrid.worker_js() + extras.worker([x['section'] for x in SECTIONS]) + extras.ATK_JS + NOTES_JS + extras.eff_worker() + FD_JS + extras.WP_JS + markers.JS + wolf.JS + moongift.JS + __import__('armormod').JS + vamp.JS + meritmod.JS + meritmod.MIG_JS + powermod.js({x['section']: x['rating'] for x in SECTIONS if x['rating'] and x['section'] in powermod.POWER_SECS}, {x['section']: x['title'] for x in SECTIONS})
h = must_sub(r'(\n\s*</script>\s*)$', lambda mm: '\n' + W + mm.group(1), h.rstrip() + '\n')
h = extras.apply_html(h)
h = extras.patch_derived(h)
h = extras.over5(h)
h = phase2.logos(h, IMG_BASE)
h, _nrt = extras.wp_apply(h, T)
h = h.replace('const pages = ["settings", "1", "2", "3", "scars-variations", "conditions"];', 'const pages = ["settings", "1", "2", "3", "scars-variations", "conditions", "powers"];')
# merits use repeating_merits:merit dot handler from base (already registered)
# datalist for merit names (Leon's PDF list)
if merit_opts:
    dl = '<datalist id="merit-list">' + ''.join(f'<option value="{html.escape(o)}">' for o in merit_opts) + '</datalist>'
    h = h.replace('<label class="wide"><span data-i18n="name">Name</span><input type="text" name="attr_merit_name" />',
                  '<label class="wide"><span data-i18n="name">Name</span><input type="text" name="attr_merit_name" list="merit-list" />' , 1)
    h = h.replace('<!-- POWERS & GEAR', dl + '\n    <!-- POWERS & GEAR', 1)

# ---------- 13. CSS ----------
ext = open(os.path.join(HERE, 'extensions.css'), encoding='utf-8').read().replace('%IMG%', IMG_BASE) + condgrid.CSS + extras.FD_CSS + extras.WP_CSS + extras.WA_CSS + extras.ROLLER_CSS + markers.CSS + wolf.css() + __import__('armormod').CSS + wolf.moon_css() + moongift.css() + vamp.CSS + '\n.sheet-background { padding-bottom: 150px !important; }\n' + open(os.path.join(HERE, 'tpl_dark.css')).read() + phase2.css(IMG_BASE) + open(os.path.join(HERE, 'fixes.css')).read() + meritmod.css() + '\n' + powermod.css() + '\n' + powermod.roller_css(HERE, extras.TYPE_OF) + powermod.LAYOUT_CSS + '\n' + extras.eff_css({k2: c for k, c in json.load(open(os.path.join(HERE, 'splat_colors.json'))).items() for k2 in extras.TYPE_OF.get(k, [])})
css = css + '\n\n/* ===== Leon 2E multi-splat extensions ===== */\n' + ext
for k, v in NEWKEYS.items(): tr.setdefault(k, v)
h = phase2.worker(h)
h = markers.apply(h, extras.SKILLS)
h = wolf.page(wolf.header(h))
h = moongift.apply(h)
h = vamp.page(vamp.header(h))
# ---------- 13b. route every base-sheet roll through our styled cofd-entry template (base wod-* templates render unstyled in modern/dark chat) ----------
def _btnval(name, newval, count):
    global h
    pat = re.compile(r'(<button type="roll"[^>]*name="' + name + r'"[^>]*value=")&(?:amp;)?\{template:wod[a-z0-9-]*\}[^"]*(")', re.S)
    vals = iter(newval if isinstance(newval, list) else [newval] * count)
    h, n = pat.subn(lambda m: m.group(1) + html.escape(next(vals), quote=True) + m.group(2), h)
    assert n == count, (name, n)
_MOD = '{{f_mod=[[?{@{modifiermacro}|0}]]}}'
_btnval('roll_sheet', '&{template:cofd-entry} {{splat=@{game_line}}} {{kind=Dice Roller}} {{name=@{dice_pool_label}}} {{f_pool=@{dice_pool} dice}} ' + _MOD +
        ' {{f_wounds=[[@{wound_penalty}+@{wp_dice}+@{cond_mod}+@{spec_bonus}]]}} {{roll=[[{((?{@{modifiermacro}|0}+@{wound_penalty}+@{wp_dice}+@{cond_mod}+@{spec_bonus}+@{dice_pool})@{rolltype_eff}', 1)
_btnval('roll_simple', '&{template:cofd-entry} {{splat=@{game_line}}} {{kind=Simple Roll}} {{name=Simple roll}} {{f_pool=?{@{dicepoolmacro}|1} dice}} {{roll=[[{(?{@{dicepoolmacro}|1}@{rolltype_eff}', 1)
_btnval('roll_initiative', [
    '&{template:cofd-entry} {{splat=@{game_line}}} {{kind=Initiative}} {{name=Initiative}} {{f_pool=1d10 + Dexterity @{dexterity} + Composure @{composure} + Fast Reflexes @{fast_reflexes} + Penalty @{initiative_penalty}}} {{f_init=[[1d10 + @{dexterity} + @{composure} + @{fast_reflexes} + @{initiative_penalty} &{tracker}]]}}',
    '&{template:cofd-entry} {{splat=@{game_line}}} {{kind=Initiative}} {{name=Initiative}} {{f_pool=1d10 + Finesse @{finesse} + Resistance @{resistance} + Fast Reflexes @{fast_reflexes} + Penalty @{initiative_penalty}}} {{f_init=[[1d10 + @{finesse} + @{resistance} + @{fast_reflexes} + @{initiative_penalty} &{tracker}]]}}'], 2)
_btnval('roll_ScarRoll1', [
    '&{template:cofd-entry} {{splat=@{game_line}}} {{kind=Scar}} {{name=@{scar-title}}} {{f_pool=@{variationType} @{scar_dicepool} + Acclimation @{potency}}} ' + _MOD + ' {{roll=[[{((?{@{modifiermacro}|0}+(@{scar_dicepool}+0)+(@{potency}+0))@{rolltype_eff}',
    '&{template:cofd-entry} {{splat=@{game_line}}} {{kind=Variation}} {{name=@{variation-title}}} {{f_pool=Composure @{composure} + Scar Finesse @{scar_finesse} + Acclimation @{potency} + Magnitude @{magnitude}}} ' + _MOD + ' {{roll=[[{((?{@{modifiermacro}|0}+(@{composure}+0)+(@{scar_finesse}+0)+(@{potency}+0)+(@{magnitude}+0))@{rolltype_eff}'], 2)
_dp = '["dice_pool_html"]: dicePoolHtml,'
assert h.count(_dp) == 2
h = h.replace(_dp, _dp + ' ["dice_pool_label"]: dicePoolHtml.replace(/<\\/div><div>/g, " + ").replace(/<\\/?div>/g, "") || "Dice pool",')
h = h.replace('<input type="hidden" name="attr_dice_pool_html" value="" />', '<input type="hidden" name="attr_dice_pool_html" value="" /><input type="hidden" name="attr_dice_pool_label" value="Dice pool" />', 1)
assert 'attr_dice_pool_label' in h
h = h.replace("{template:cofd-entry}", "{template:cofd-entry} {{charname=@{character_name}}} {{gl_@{game_line}=1}}")
_pg = "\"conditions\", \"powers\"];"
assert _pg in h
h = h.replace(_pg, "\"conditions\", \"powers\", \"forms\", \"details\"];", 1)
# ---------- 14. tab memory across splat switches (fix: splat change must not move the active tab) ----------
_old_pg = """            on(`clicked:page_${page}`, () => {
                setAttrs({
                    "pagenumber": page
                });
            });"""
assert _old_pg in h
h = h.replace(_old_pg, """            on(`clicked:page_${page}`, () => {
                const u = {"pagenumber": page};
                if (page !== "settings") u.last_page = page;
                setAttrs(u);
            });""", 1)
_old_st = """                setAttrs({
                    "sheettype": sheettype,
                    "game_line": gameLine,
                    "edition": edition,
                    "entity": entity
                });"""
assert _old_st in h
h = h.replace(_old_st, """                getAttrs(["pagenumber", "last_page"], (pv) => {
                    // keep the tab the user is on; if it does not exist for the new splat, fall back to Main
                    const TABS = ["settings", "1", "scars-variations", "conditions", "powers", "forms", "details"];
                    const wolf = sheettype === "werewolf2" || sheettype === "breeds2";
                    let pg = pv.pagenumber || "1";
                    if (TABS.indexOf(pg) < 0 || (pg === "forms" && !wolf)) pg = "1";
                    let lp = pv.last_page || "1";
                    if (TABS.indexOf(lp) < 0 || lp === "settings" || (lp === "forms" && !wolf)) lp = "1";
                    setAttrs({
                        "sheettype": sheettype,
                        "game_line": gameLine,
                        "edition": edition,
                        "entity": entity,
                        "pagenumber": pg,
                        "last_page": lp
                    });
                });""", 1)
h = h.replace('<input type="hidden" class="page" name="attr_pagenumber" value="1" />', '<input type="hidden" class="page" name="attr_pagenumber" value="1" /><input type="hidden" name="attr_last_page" value="1" />', 1)
# ---------- 15. health boxes: cycle empty -> bashing -> lethal -> aggravated -> empty, auto-sorted agg/lethal/bashing from the left ----------
_old_hb = """                getAttrs([attr], (v) => {
                    const healthValue = parseInt(v[attr]) || 0;
                    setAttrs({
                        [attr]: (healthValue + 1) % depth
                    });
                });"""
assert _old_hb in h
h = h.replace(_old_hb, """                const trait = attr.replace(/_\\d+$/, "");
                const names = [...Array(24).keys()].map(i => `${trait}_${i + 1}`);
                getAttrs([attr, "health", "moralhealth", ...names], (v) => {
                    const healthValue = parseInt(v[attr]) || 0;
                    const u = {[attr]: (healthValue + 1) % depth};
                    if (trait === "healthbox") {
                        const max = Math.min(24, parseInt(v.health) || 24);
                        const vals = names.slice(0, max).map(n => n === attr ? u[attr] : (parseInt(v[n]) || 0)).sort((a, b) => b - a);
                        vals.forEach((x, i) => { u[names[i]] = x; });
                    }
                    setAttrs(u);
                });""", 1)
# ---------- 16. shapeshifting per WtF 2E Harmony table (no shift roll in 2E) ----------
_old_sf = 'forEach(f => on(`clicked:setform_${f}`, () => setAttrs({form: f})));'
assert _old_sf in h
h = h.replace(_old_sf, 'forEach(f => on(`clicked:setform_${f}`, () => shiftTo(f)));', 1)
h = h.replace('        const FORM_MODS = {', """        // WtF 2E (core p. ~ "Harmony" / "Shapeshifting"): 9-10 = 1 Essence + instant action; 7-8 = instant action free, or 1 Essence reflexive;
        // 4-6 = reflexive, free; 2-3 / 0-1 = shifting is fluid (involuntary shifts each scene; resisting costs an action/Essence) - voluntary shift treated as reflexive, free.
        const SHIFT_FORMS = {hishu:"Hishu",dalu:"Dalu",gauru:"Gauru",urshul:"Urshul",urhan:"Urhan",urkhar:"Ur'Khar"};
        const shiftTo = (f, already) => getAttrs(["character_name", "morality", "form", "sheettype", "urkhar_enabled"], (v) => {
            const isWolf = (v.sheettype || "").indexOf("werewolf") === 0 || v.sheettype === "breeds2";
            if (!already) setAttrs({form: f});
            if (!isWolf) return;
            const hm = parseInt(v.morality, 10); const H = isNaN(hm) ? 7 : hm;
            let shift;
            if (H >= 9) shift = `Instant action; spent 1 Essence (Harmony ${H}: 9-10 always costs Essence)`;
            else if (H >= 7) shift = `?{Shift method (Harmony ${H})|Instant action - no cost,Instant action; no Essence (Harmony ${H})|Reflexive - spend 1 Essence,Reflexive; spent 1 Essence (Harmony ${H})}`;
            else if (H >= 4) shift = `Reflexive; no cost (Harmony ${H})`;
            else shift = `Reflexive; no cost (Harmony ${H}: flesh is fluid - expect involuntary shifts each scene; resisting needs an instant action${H >= 2 ? " or 1 Essence reflexively" : " and 1 Essence"})`;
            const label = SHIFT_FORMS[f] || f;
            const fm = (f === "gauru" && v.urkhar_enabled === "1") ? GAURU_URKHAR_VARIANT : (FORM_MODS[f] || {});
            const mods = Object.entries(fm).filter(([k, x]) => x).map(([k, x]) => `${k} ${x > 0 ? "+" : ""}${x}`).join(", ") || "no modifiers";
            const tpl = `&{template:cofd-entry} {{charname=@{character_name}}} {{gl_werewolf=1}} {{splat=werewolf}} {{kind=Shapeshift}} {{name=@{character_name} shifts to ${label}}} {{f_shift=${shift}}} {{f_mods=${mods}}}`;
            if (typeof startRoll === "function") startRoll(tpl, (r) => { if (typeof finishRoll === "function") finishRoll(r.rollId); });
        });
        on("change:form", (ev) => { if (ev.sourceType === "player") shiftTo(ev.newValue, true); });
        const FORM_MODS = {""", 1)
# ---------- 17. wound penalties: base updateAttacks crashed when attack attr empty / iron_stamina blank -> wound_penalty never updated ----------
for _o, _n in [('var atknum = v.attack.match(regex)[1];', 'var _am = (v.attack || "").match(regex); var atknum = _am ? _am[1] : "0";'),
               ('var ironStamina = parseInt(v.iron_stamina, 10);', 'var ironStamina = parseInt(v.iron_stamina, 10) || 0;')]:
    assert _o in h, _o
    h = h.replace(_o, _n, 1)
import poolfix; h = poolfix.apply(h)

# ---------- Werewolf Blood / Bone entry cards on Main (full width; names share attr_Virtue / attr_Vice with the header) ----------
def _bbcard(key, attr, label, ph):
    post = html.escape(f'&{{template:cofd-entry}} {{{{charname=@{{character_name}}}}}} {{{{gl_@{{game_line}}=1}}}} {{{{splat=@{{game_line}}}}}} {{{{kind={label}}}}} {{{{name=@{{{attr}}}}}}} {{{{f_description=@{{{key}_desc}}}}}}', quote=True)
    return (f'<div class="sheet-entry sheet-bb-entry"><input type="checkbox" class="sheet-entry-toggle" name="attr_{key}_show" value="1" title="Expand / collapse" />'
            f'<div class="sheet-entry-head"><span class="sheet-bb-lbl">{label}</span>'
            f'<input type="text" class="sheet-bb-name" name="attr_{attr}" placeholder="{ph}" title="{label} (same field as the header)" />'
            f'<button type="roll" class="sheet-entry-post sheet-bb-post" name="roll_{key}_post" title="Post {label} to chat" value="{post}">&#128172;</button></div>'
            f'<div class="sheet-entry-body"><label class="sheet-bb-desc-l">{label}: description / effect'
            f'<textarea name="attr_{key}_desc" placeholder="What it means, when it applies, how it restores Willpower"></textarea></label></div></div>')
BB = ('\n        <div class="sheet-bloodbone sheet-game-line sheet-werewolf2"><div class="sheet-subheader">Blood and Bone</div>'
      '<div class="sheet-bb-grid">' + _bbcard('blood', 'Virtue', 'Blood', 'e.g. The Destroyer of Hope') + _bbcard('bone', 'Vice', 'Bone', 'e.g. The Guardian of the Pack') + '</div></div>\n')
_m = re.search(r'<div class="(?:sheet-)?el_spacer"></div>\s*<div class="(?:sheet-)?flex">\s*<!-- SKILL FIELDS -->', h)
assert _m, 'skills anchor'
if 'class="el_spacer"' in _m.group(0): BB = BB.replace('class="sheet-', 'class="').replace(' sheet-', ' ')
h = h[:_m.start()] + BB + h[_m.start():]
h = meritmod.relocate(h)
h = powermod.roller(h)
# Small-Framed lowers Size, so it must lower Health too (base sheet added it)
assert h.count('+ Number(v.small_framed)') == 2
h = h.replace('+ Number(v.small_framed)', '- Number(v.small_framed)')
for k, v in NEWKEYS.items(): tr.setdefault(k, v)
_ur = ('<div class="game-line werewolf2 werewolf urkhar-cfg"><label class="urkhar-toggle" title="Enable the Ur&#39;Khar form (the Shunned Form: optional rule, Signs of the Moon / Night Horrors). Adds an Ur&#39;Khar column to the Forms table and lets you shift into it.">'
       '<input type="checkbox" name="attr_urkhar_enabled" value="1" /> Ur&#39;Khar (Shunned Form, optional rule)</label></div>')
_cfg = '<span class="sheet-checkbox">\n                    <input type="hidden" class="sheet-flag" name="attr_enable_profession"'
if _cfg not in h: _cfg = '<span class="checkbox">\n                    <input type="hidden" class="flag" name="attr_enable_profession"'
assert _cfg in h, 'cfg anchor'
i = h.index(_cfg); i = h.rfind('<div>', 0, i)
h = h[:i] + _ur + '\n            ' + h[i:]
PAGE_GUARD = r"""
        const PAGE_ONLY = {"scars-variations": ["deviant-the-renegades"], "forms": ["werewolf2", "breeds2"]};
        on("sheet:opened change:sheettype", () => getAttrs(["pagenumber", "sheettype"], v => {
            const ok = PAGE_ONLY[v.pagenumber]; if (ok && !ok.includes(v.sheettype)) setAttrs({pagenumber: "1"});
        }));
"""
h = must_sub(r'(\n\s*</script>\s*)$', lambda mm: '\n' + PAGE_GUARD + mm.group(1), h.rstrip() + '\n')
# ---------- experience: Earned / Spent / Available (read-only) ----------
def _xp(pre, attr):
    return (f'<span class="xp-trio"><label title="Total Experience earned">Earned <input type="number" min="0" name="attr_{pre}_earned" value="0" /></label>'
            f'<label title="Total Experience spent">Spent <input type="number" min="0" name="attr_{pre}_spent" value="0" /></label>'
            f'<label title="Available = Earned - Spent (calculated)">Avail <span class="xp-avail" name="attr_{attr}"></span></label>'
            f'<input type="hidden" name="attr_{attr}" value="0" /><input type="hidden" name="attr_{attr}_legacy" value="" /></span>')
h = must_sub(r'<input type="text" name="attr_experience">', lambda mm: _xp('xp', 'experience'), h)
h = must_sub(r'<input type="text" name="attr_experience_alt">', lambda mm: _xp('xpalt', 'experience_alt'), h)
XP_JS = r"""
        const XP_SETS = [["xp", "experience"], ["xpalt", "experience_alt"]];
        const xpSync = () => getAttrs(XP_SETS.flatMap(([p, a]) => [p + "_earned", p + "_spent", a, a + "_legacy", p + "_mig_v1"]), v => {
            const u = {};
            XP_SETS.forEach(([p, a]) => {
                let e = parseInt(v[p + "_earned"], 10) || 0, s = parseInt(v[p + "_spent"], 10) || 0;
                if (v[p + "_mig_v1"] !== "1") {
                    u[p + "_mig_v1"] = "1"; const old = String(v[a] || "").trim();
                    if (old && !e && !s) {
                        u[a + "_legacy"] = old;
                        const me = old.match(/(\d+)\s*(?:xp\s*)?earned/i), ms = old.match(/(\d+)\s*(?:xp\s*)?spent/i);
                        if (me) { e = parseInt(me[1], 10); s = ms ? parseInt(ms[1], 10) : 0; }
                        else { const n = old.match(/-?\d+/); e = n ? parseInt(n[0], 10) : 0; s = 0; }
                        u[p + "_earned"] = e; u[p + "_spent"] = s;
                    }
                }
                u[a] = e - s;
            });
            setAttrs(u);
        });
        on("sheet:opened change:xp_earned change:xp_spent change:xpalt_earned change:xpalt_spent", xpSync);
"""
h = must_sub(r'(\n\s*</script>\s*)$', lambda mm: '\n' + XP_JS + mm.group(1), h.rstrip() + '\n')
css += """
.charsheet .sheet-xp-trio { display: inline-flex; flex-wrap: wrap; gap: 4px 8px; align-items: center; }
.charsheet .sheet-xp-trio label { display: inline-flex; align-items: center; gap: 3px; font-size: 12px; white-space: nowrap; }
.charsheet .sheet-xp-trio input[type=number] { width: 52px !important; text-align: center; }
.charsheet .sheet-xp-trio .sheet-xp-avail { font-weight: bold; min-width: 22px; display: inline-block; text-align: center; border-bottom: 1px solid rgba(160,160,160,.5); }
"""
# ---------- tooltips: every icon-only button gets a title ----------
def _tip(m):
    a = m.group(1)
    if 'title=' in a: return m.group(0)
    if 'rollstyle' in a and 'type="roll"' in a: return f'<button{a} title="Roll pool">'
    n = re.search(r'name="(?:act|roll)_([^"]*)"', a); n = n.group(1) if n else ''
    nice = lambda x: x.replace('-', ' ').replace('_', ' ').strip().title()
    t = None
    d = re.match(r'(.+)-(\d+)$', n)
    if d: t = f'Clear {nice(d.group(1))}' if d.group(2) == '0' else f'Set {nice(d.group(1))} to {d.group(2)}'
    elif re.search(r'_box\d+$', n): t = f'Mark / clear {nice(re.sub(r"_box\d+$", "", n))} box'
    elif n.endswith('_box'): t = f'Toggle {nice(n[:-4])} (specialty / used)'
    elif n.endswith('_era'): t = f'{nice(n[:-4])}: era-dependent skill'
    elif 'type="roll"' in a: t = 'Post to chat' if ('mini' in a or 'post' in n) else f'Roll {nice(n)}'
    elif n: t = nice(n)
    return m.group(0) if not t else f'<button{a} title="{html.escape(t, quote=True)}">'
h = re.sub(r'<button\b([^>]*)>', _tip, h)
# r12: repcontrol tooltips moved to r12.repctl (the old ::after tooltip was clipped by the 16px icon button)
open(os.path.join(ROOT, 'sheet.html'), 'w', encoding='utf-8').write(h)
open(os.path.join(ROOT, 'sheet.css'), 'w', encoding='utf-8').write(css)
tr.pop('page-1', None); tr.pop('page-2', None); tr.pop('page-3', None); tr['main'] = 'Main'
json.dump(tr, open(os.path.join(ROOT, 'translation.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('ok', len(h), len(css), 'sections', [s['section'] for s in SECTIONS], 'merit opts', len(merit_opts))
