import re, json
SKILLS = ["academics","computer","crafts","investigation","medicine","occult","politics","science","athletics","brawl","drive","firearms","larceny","stealth","survival","weaponry","animalken","empathy","expression","intimidation","persuasion","socialize","streetwise","subterfuge"]
def apply_html(h):
    for sk in SKILLS:
        pat = r'(<button type="action" class="toggle" name="act_%s" data-i18n="%s">[^<]*</button>)(\s*</div>\s*<div class="[^"]*dots">.*?</div>)' % (sk, sk)
        def rep(mm, sk=sk):
            caret = ('<button type="action" class="spec-caret" name="act_%s_spec_toggle" title="Specialties">'
                     '<input type="hidden" class="spec-has" name="attr_%s_spec_has" value="0" />'
                     '<input type="hidden" class="spec-openflag" name="attr_%s_spec_open" value="0" /><span></span></button>') % (sk, sk, sk)
            row = ('<div class="spec-row"><input type="hidden" class="spec-openflag" name="attr_%s_spec_open" value="0" />'
                   '<div class="spec-inner"><input type="text" class="spec-input" name="attr_%s_specialties" placeholder="Specialties, comma-separated" /></div></div>') % (sk, sk)
            return mm.group(1) + caret + mm.group(2) + row
        h, n = re.subn(pat, rep, h, count=1, flags=re.S)
        assert n == 1, sk
    old = '<div class="corporeal">\n                            <div class="subheader" data-i18n="specializations">'
    assert old in h
    h = h.replace(old, '<div class="corporeal legacy-specs">\n                            <div class="subheader" data-i18n="specializations">', 1)
    qa = re.findall(r'\s*<div class="quick-actions game-line (?:hunter2|mortal2)">.*?</div>', h, flags=re.S)
    for q in qa: h = h.replace(q, '', 1)
    h = h.replace('<div class="corporeal legacy-specs">', ''.join(qa) + '\n                        <div class="corporeal legacy-specs">', 1)
    h = h.replace('@{wound_penalty}', '@{wound_penalty}+@{cond_mod}+@{spec_bonus}')
    h = h.replace('<input type="hidden" name="attr_cond_mod" value="0" />', '<input type="hidden" name="attr_cond_mod" value="0" /><input type="hidden" name="attr_spec_bonus" value="0" />')
    extra = ''.join('{{#%s}}<tr><th>%s</th><td>{{%s}}</td></tr>{{/%s}}' % (k, l, k, k) for k, l in [('f_spec','Specialty'),('f_mod','Modifier'),('f_def','Defense'),('f_wtype','Type'),('f_avail','Availability'),('f_tags','Tags')] + __import__('hurtlocker').TPL_EXTRA)
    a = '{{#f_pool}}<tr><th>Dice pool</th><td>{{f_pool}}</td></tr>{{/f_pool}}'
    assert a in h
    h = h.replace(a, a + extra, 1)
    return h
TOOLS = ''  # per-entry move/delete removed: use Roll20's native list edit mode
def worker(sections):
    return '''
        // Per-skill specialties (caret dropdown) + optional +1 specialty die
        const SKILLS = %s;
        SKILLS.forEach(sk => {
            on(`clicked:${sk}_spec_toggle`, () => getAttrs([`${sk}_spec_open`], v => setAttrs({[`${sk}_spec_open`]: v[`${sk}_spec_open`] === "1" ? "0" : "1"})));
            on(`change:${sk}_specialties`, e => setAttrs({[`${sk}_spec_has`]: (e.newValue || "").trim() ? "1" : "0"}));
        });
        const updateSpecBonus = () => getAttrs(["spec_apply"].concat(SKILLS.flatMap(sk => [`${sk}_flag`, `${sk}_specialties`])), v => {
            const n = SKILLS.filter(sk => v.spec_apply === "1" && v[`${sk}_flag`] === "1" && (v[`${sk}_specialties`] || "").trim()).length;
            setAttrs({ spec_bonus: n });
        });
        on(SKILLS.flatMap(sk => [`change:${sk}_flag`, `change:${sk}_specialties`]).join(" ") + " change:spec_apply sheet:opened", updateSpecBonus);
        on("sheet:opened", () => getAttrs(SKILLS.map(sk => `${sk}_specialties`), v => { const u = {}; SKILLS.forEach(sk => u[`${sk}_spec_has`] = (v[`${sk}_specialties`] || "").trim() ? "1" : "0"); setAttrs(u); }));
        // Pathfinder-style per-row reorder / delete
''' % (json.dumps(SKILLS),)

ATK_MACRO = ('&{template:cofd-entry} {{splat=@{game_line}}} {{kind=Attack}} {{name=@{name}}} {{f_pool=@{atk_breakdown}}} '
             '{{f_spec=Specialty +?{Specialty applies?|No,0|Yes,1}}} {{f_mod=Modifier ?{@{modifiermacro}|0}}} {{f_def=Target Defense -?{Target Defense (0 for firearms)|@{atk_def_default}}}} '
             '{{roll=[[{((@{atk_base}+?{Specialty applies?|No,0|Yes,1}+?{@{modifiermacro}|0}-?{Target Defense (0 for firearms)|@{atk_def_default}}+@{wp_dice})@{atk_rt} '
             '{{f_damage=Successes + @{damage}}} {{f_dtype=@{dtype}}} {{dmg_@{dtype}=1}} {{f_range=@{range}}} {{f_tags=@{tags}}}')
def weapons_entry(entry, html):
    hdr = ('<span class="entry-pool" name="attr_atk_breakdown"></span>'
           '<button type="roll" class="entry-roll" name="roll_attack" title="Attack roll" value="' + html.escape(ATK_MACRO, quote=True) + '">&#9876;</button>')
    f = [('wtype','Type','select:melee=Melee;thrown=Thrown;ranged=Ranged;unarmed=Unarmed'),
         ('damage','Damage rating','select:0=0;1=1;2=2;3=3;4=4;5=5;6=5+ (6)'),
         ('dtype','Damage type','select:B=Bashing;L=Lethal;A=Aggravated'),
         ('range','Range (short/medium/long)','text'),
         ('clip','Clip','select:Melee=Melee / N/A;1=1;2=2;5+1=5+1;6=6;7+1=7+1;8+1=8+1;10+1=10+1;15+1=15+1;17+1=17+1;20+1=20+1;30+1=30+1;42+1=42+1;100=100 (belt)'),
         ('initiative','Initiative mod','select:0=0;-1=-1;-2=-2;-3=-3;-4=-4;-5=-5;1=+1'),
         ('str_req','Strength req.','select:1=1;2=2;3=3;4=4;5=5'),
         ('wsize','Size','select:1=1;2=2;3=3;4=4;5=5'),
         ('avail','Availability','select:0=—;1=•;2=••;3=•••;4=••••;5=•••••'),
         ('atk_attr','Attribute','select:auto=Auto (by Type);strength=Strength;dexterity=Dexterity;wits=Wits;presence=Presence;manipulation=Manipulation'),
         ('atk_skill','Skill','select:auto=Auto (by Type);brawl=Brawl;weaponry=Weaponry;firearms=Firearms;athletics=Athletics'),
         ('other_mod','Other mods (dice)','number'),('tags','Tags','text'),('notes','Notes','textarea')]
    s = entry('weapons','weapons','Weapons & Attacks',f,rating=None,pool=False,default_open=False,extra_header=hdr)
    hidden = ('<input type="hidden" name="attr_atk_base" value="0" /><input type="hidden" name="attr_atk_rt" value="@{rolltype}" />'
              '<input type="hidden" name="attr_atk_def_default" value="0" />')
    return s.replace('<input type="hidden" name="attr_rating_dots"', hidden + '<input type="hidden" name="attr_rating_dots"', 1)
import hurtlocker as _hl
ATK_JS = _hl.js()


def notes_page(entry, h, T):
    """Replace base page 3 note blocks with repeating collapsible entries; drop base page 2 (custom rolls)."""
    i, j = h.index('    <!-- PAGE 3 -->'), h.index('    <!-- PAGE4,')
    p3 = h[i:j]
    pairs, seen = [], set()
    for m in re.finditer(r'data-i18n="([^"]+)">([^<]+)</span>(?:<br>)?\s*<textarea[^>]*name="attr_([^"]+)"', p3):
        if m.group(3) not in seen:
            seen.add(m.group(3)); pairs.append((m.group(1), m.group(2).strip(), m.group(3)))
    dl = '<datalist id="note-names">' + ''.join(f'<option value="{l}">' for _, l, _ in pairs) + '</datalist>'
    notes = entry('notes', 'notes-entries', 'Notes & Background Entries',
                  [('category', 'Category', 'text'), ('description', 'Description', 'textarea'), ('source', 'Source / page', 'text')],
                  rating=None, pool=False, default_open=False)
    notes = notes.replace('<input type="text" name="attr_name" />', '<input type="text" name="attr_name" list="note-names" />', 1)
    rolls = entry('customrolls', 'custom-rolls', 'Custom Rolls',
                  [('action', 'Action', 'select:instant;reflexive;contested;resisted;extended'), ('description', 'Description', 'textarea'), ('source', 'Source / page', 'text')],
                  rating=None, pool=True, default_open=False)
    global NOTES_BLOCK
    NOTES_BLOCK = ('        <div class="det-notes"><div class="section-header">' + T('notes-u', 'NOTES & ENTRIES') + '</div>\n' + dl + notes + rolls + '</div>\n')
    newp = '    <!-- PAGE 2 (was base page 3) -->\n'
    h = h[:i] + newp + h[j:]
    a, b = h.index('    <!-- PAGE 2 -->'), h.index('    <!-- PAGE 2 (was base page 3)')
    h = h[:a] + h[b:]
    h = h.replace('    <button type="action" class="toggle page-2" name="act_page_2" data-i18n="page-2">Page 2</button>\n', '', 1)
    h = re.sub(r'\s*<button type="action" class="toggle page-3" name="act_page_3" data-i18n="page-3">Page 3</button>', '', h, count=1)
    h = h.replace('name="act_page_1" data-i18n="page-1">Page 1</button>', 'name="act_page_1" data-i18n="main">Main</button>', 1)
    mig = [(l, a) for _, l, a in pairs] + [('Custom notes (left)', 'textleft'), ('Custom notes (right)', 'textright')]
    js = '''
        // Migrate base page-3 note textareas into repeating_notes (once)
        const NOTE_MIG = %s;
        on("sheet:opened", () => getAttrs(["notes_migrated", "titleleft", "titleright"].concat(NOTE_MIG.map(x => x[1])), v => {
            if (v.notes_migrated === "1") return;
            const u = { notes_migrated: "1" };
            NOTE_MIG.forEach(([label, a]) => {
                const t = (v[a] || "").trim(); if (!t) return;
                const id = generateRowID(), nm = a === "textleft" ? (v.titleleft || label) : a === "textright" ? (v.titleright || label) : label;
                u[`repeating_notes_${id}_name`] = nm; u[`repeating_notes_${id}_description`] = t;
            });
            setAttrs(u);
        }));
        // Details portrait = the character's Roll20 avatar (no manual URL)
        const syncPortrait = () => getAttrs(["character_avatar"], v => {
            let a = (v.character_avatar || "").trim();
            a = a.replace(/\\/(med|thumb|original)\\.(png|jpg|jpeg|gif|webp)/i, "/max.$2");
            setAttrs({ portrait_src: a }, { silent: true });
        });
        on("sheet:opened change:character_avatar", syncPortrait);
        // Page 2 tab removed: anyone left on it (or remembering it) lands on Main
        on("sheet:opened", () => getAttrs(["pagenumber", "last_page"], v => {
            const u = {};
            if (v.pagenumber === "3" || v.pagenumber === "2") u.pagenumber = "1";
            if (v.last_page === "3" || v.last_page === "2") u.last_page = "1";
            if (Object.keys(u).length) setAttrs(u);
        }));
''' % json.dumps(mig)
    return h, js

ATTRS = ["intelligence","wits","resolve","strength","dexterity","stamina","presence","manipulation","composure"]
def patch_derived(h):
    """Feed form/temporary modifiers into the base derived stats; 10-dot attribute tracks with coloured temporary dots."""
    rep = [
        ('value="@{base_size}+@{giant}-@{small_framed}"', 'value="@{base_size}+@{giant}-@{small_framed}+@{form_size}"'),
        ('value="@{species_factor}+@{speed_base}+@{speed_penalty}+@{fleet_of_foot}"', 'value="@{species_factor}+@{speed_base}+@{speed_penalty}+@{fleet_of_foot}+@{form_speed_extra}+@{form_size}"'),
        ('value="@{initiative_base}+@{initiative_penalty}+@{fast_reflexes}"', 'value="@{initiative_base}+@{initiative_penalty}+@{fast_reflexes}+@{form_init_extra}"'),
        ('getAttrs(["stamina","resistance","base_size","giant","small_framed","sheettype","entity","bonus_health"], function(v) {',
         'getAttrs(["stamina","stamina_boost","form_size","resistance","base_size","giant","small_framed","sheettype","entity","bonus_health"], function(v) {'),
        ('health = Number(v.stamina) + Number(v.base_size) + Number(v.giant) + Number(v.small_framed) + Number(v.bonus_health);',
         'health = Number(v.stamina) + (Number(v.stamina_boost) || 0) + (Number(v.form_size) || 0) + Number(v.base_size) + Number(v.giant) + Number(v.small_framed) + Number(v.bonus_health);'),
        ('getAttrs(["defense_select","entity","athletics","brawl","dexterity","weaponry","wits","potency","power","finesse"], function(v) {',
         'getAttrs(["defense_select","entity","athletics","brawl","dexterity","weaponry","wits","potency","power","finesse","dexterity_boost","wits_boost"], function(v) {\n                v.dexterity = (parseInt(v.dexterity, 10) || 0) + (parseInt(v.dexterity_boost, 10) || 0); v.wits = (parseInt(v.wits, 10) || 0) + (parseInt(v.wits_boost, 10) || 0);'),
    ]
    for a, b in rep:
        assert a in h, a[:60]
        h = h.replace(a, b, 1)
    # hidden defaults
    h = h.replace('<input type="hidden" name="attr_cond_mod" value="0" />',
                  '<input type="hidden" name="attr_cond_mod" value="0" /><input type="hidden" name="attr_form_size" value="0" /><input type="hidden" name="attr_form_speed_extra" value="0" /><input type="hidden" name="attr_form_init_extra" value="0" />', 1)
    # 10-dot attribute tracks + temp (effective) dots
    for a in ATTRS:
        old = f'<input type="hidden" name="attr_{a}" value="1" />'
        assert old in h, a
        new = f'<input type="hidden" class="eff" name="attr_{a}_eff" value="1" /><input type="hidden" class="perm" name="attr_{a}" value="1" />'
        h = h.replace(old, new, 1)
        last = f'<button type="action" class="dot ne-1 ne-2 ne-3 ne-4" name="act_{a}-5"></button>'
        assert last in h, a
        more = ''.join(f'<button type="action" class="dot ext {" ".join("ne-%d" % i for i in range(1, k))}" name="act_{a}-{k}"></button>' for k in range(6, 11))
        h = h.replace(last, last + more, 1)
    return h
def eff_worker():
    return '''
        // Effective (permanent + temporary) attribute dots, and 6-10 dot clicks
        const ATTRS10 = %s;
        ATTRS10.forEach(a => {
            for (let k = 6; k <= 10; k++) on(`clicked:${a}-${k}`, () => setAttrs({[a]: k}));
            on(`change:${a} change:${a}_boost sheet:opened`, () => getAttrs([a, `${a}_boost`], v => setAttrs({[`${a}_eff`]: Math.max(0, (parseInt(v[a], 10) || 0) + (parseInt(v[`${a}_boost`], 10) || 0))})));
        });
        on("change:form_size change:stamina_boost", () => updateHealth());
        on("change:dexterity_boost change:wits_boost", () => updateDefense());
''' % json.dumps(ATTRS)
def eff_css(colors):
    out = []
    # coloured temporary dots: effective N > permanent M
    for N in range(1, 16):
        for M in range(0, N):
            sel = f'input.sheet-eff[value="{N}"] ~ input.sheet-perm[value="{M}"] ~ button.sheet-dot:not(.sheet-zero)' + (f'.sheet-ne-{M}' if M else '') + f':not(.sheet-ne-{N})'
            out.append(sel)
    css = ',\n'.join(out) + ' { background: var(--temp-dot, #c0392b) !important; border-color: var(--temp-dot, #c0392b) !important; }\n'
    # extra dots 6-10 hidden for Mortal/Hunter unless the attribute is already above 5 or "allow_over5" is on
    css += 'button.sheet-dot.sheet-ext { margin-left: 1px; }\n'
    for k in ('mortal2', 'hunter2'):
        css += (f'input.sheet-type[value="{k}"] ~ * input.sheet-eff[value="0"] ~ button.sheet-ext, ' +
                ', '.join(f'input.sheet-type[value="{k}"] ~ * input.sheet-eff[value="{v}"] ~ button.sheet-ext' for v in range(1, 6)) +
                ' { display: none; }\n')
    for k, c in colors.items():
        css += f'input.sheet-type[value="{k}"] ~ * {{ --temp-dot: {c}; }}\n'
    return css

TYPE_OF = {'mortal': ['mortal2'], 'hunter': ['hunter2'], 'vampire': ['vampire2'], 'werewolf': ['werewolf2'], 'mage': ['mage2'],
           'promethean': ['promethean2'], 'changeling': ['changeling2'], 'geist': ['geist2'], 'mummy': ['mummy2'], 'demon': ['demon'],
           'beast': ['beast'], 'deviant': ['deviant-the-renegades'], 'breeds': ['breeds2']}
def over5(h):
    a = '<input type="hidden" class="game-line" name="attr_game_line" value="mortal" />'
    assert a in h
    h = h.replace(a, a + '\n    <input type="hidden" class="over5" name="attr_allow_over5" value="0" />', 1)
    b = '<div class="dice-rule">'
    if b in h:
        h = h.replace(b, '<div class="dice-rule"><label title="Mortal/Hunter: show attribute dots 6-10"><input type="checkbox" name="attr_allow_over5" value="1" /> Allow 6+ attribute dots (Mortal/Hunter)</label>', 1)
    return h

FORMS = [('hishu', 'Hishu'), ('dalu', 'Dalu'), ('gauru', 'Gauru'), ('urkhar', "Ur'Khar"), ('urshul', 'Urshul'), ('urhan', 'Urhan')]
def forms_details(h, T):
    # ---- cut forms table out of Powers page
    a = h.index('          <div class="subheader"><span data-i18n="forms">Forms</span></div>')
    b = h.index('<!--/forms-->', a) + len('<!--/forms-->')
    table = h[a:b].replace('<div class="subheader"><span data-i18n="forms">Forms</span></div>', '', 1); h = h[:a] + h[b:]
    btns = ''.join(f'<button type="action" class="form-btn{" urkhar-col" if k == "urkhar" else ""}" name="act_setform_{k}" title="Shift to {l} form"><input type="hidden" class="form-cur" name="attr_form" value="hishu" /><span class="fb-{k}">{l}</span></button>' for k, l in FORMS)
    forms_page = f'''
    <!-- FORMS (Werewolf / Changing Breeds) -->
    <div class="page forms">
      <div class="leon-page">
        <div class="section-header">{T("forms-u", "FORMS")}</div>
        <input type="hidden" class="urkhar-flag" name="attr_urkhar_enabled" value="0" />
        <div class="form-active">{T("active-form", "Active form")}: <b><span name="attr_form_label">Hishu</span></b> &mdash; <span name="attr_form_summary"></span>
          &nbsp;|&nbsp; {T("height", "Height")}: <span name="attr_form_height"></span> &nbsp; {T("weight", "Weight")}: <span name="attr_form_weight"></span></div>
{table}
      </div>
    </div>
'''
    def inp(attr, label, kind='text'):
        if kind == 'textarea':
            return f'<label class="wide">{T("d-" + attr, label)}<textarea name="attr_{attr}"></textarea></label>'
        return f'<label>{T("d-" + attr, label)}<input type="text" name="attr_{attr}" /></label>'
    basic = ''.join(inp(a, l) for a, l in [('det_age', 'Age'), ('det_apparent_age', 'Apparent age'), ('det_dob', 'D.O.B.'), ('det_height', 'Height'), ('det_weight', 'Weight'),
                                            ('det_hair', 'Hair'), ('det_eyes', 'Eyes'), ('det_sex', 'Sex / Gender'), ('det_race', 'Race / Ethnicity'), ('det_nationality', 'Nationality')])
    longs = ''.join(inp(a, l, 'textarea') for a, l in [('det_appearance', 'Appearance / Distinguishing characteristics'), ('det_history', 'History / Background'),
                                                        ('det_goals', 'Goals'), ('det_aspirations', 'Aspirations'), ('det_possessions', 'Possessions')])
    splat = (f'<div class="game-line vampire2 det-splat"><div class="subheader">{T("det-vampire", "Vampire")}</div>{inp("det_embrace", "Date of Embrace")}{inp("det_sire", "Sire")}{inp("det_apparent_embrace", "Apparent age at Embrace")}</div>'
             f'<div class="game-line werewolf2 breeds2 det-splat"><div class="subheader">{T("det-werewolf", "First Change")}</div>{inp("det_first_change", "First Change (date / place)")}{inp("det_first_change_notes", "Circumstances", "textarea")}</div>'
             f'<div class="game-line hunter2 det-splat"><div class="subheader">{T("det-hunter", "Hunter")}</div>{inp("det_profession", "Profession")}{inp("det_cell", "Cell (also on Main)")}{inp("det_first_encounter", "First encounter with the supernatural", "textarea")}</div>')
    hw = ['<table class="forms-table hw-table"><tr><th></th>' + ''.join(f'<th class="{"urkhar-col" if k == "urkhar" else ""}">{l}</th>' for k, l in FORMS) + '</tr>']
    for a, l in [('height', 'Height'), ('weight', 'Weight')]:
        hw.append(f'<tr><th>{l}</th>' + ''.join(f'<td class="{"urkhar-col" if k == "urkhar" else ""}"><input type="text" name="attr_fh_{k}_{a}" /></td>' for k, _ in FORMS) + '</tr>')
    hw.append('</table>')
    details = f'''
    <!-- CHARACTER DETAILS -->
    <div class="page details">
      <div class="leon-page">
        <div class="section-header">{T("details-u", "CHARACTER DETAILS")}</div>
        <div class="det-top"><div class="det-portrait"><input type="hidden" class="portrait-flag" name="attr_portrait_src" value="" /><img class="portrait-img" name="attr_portrait_src" src="" alt="" /><div class="portrait-ph">{T("d-portrait-ph", "No avatar")}</div></div>
          <div class="det-grid">{basic}</div></div>
        <div class="game-line werewolf2 breeds2"><div class="subheader">{T("form-hw", "Height and Weight by Form")}</div><input type="hidden" class="urkhar-flag" name="attr_urkhar_enabled" value="0" />{"".join(hw)}</div>
        {splat}
        <div class="det-long">{longs}</div>
{NOTES_BLOCK}
      </div>
    </div>
'''
    anchor = '\n    <!-- PAGE 4, CONDITIONS -->'
    assert anchor in h
    h = h.replace(anchor, forms_page + anchor, 1)
    i = h.index('    <!-- POWERS & GEAR')
    h = h[:i] + details + h[i:]
    # tabs: Forms after Page 1 (Page 2 = notes); Details last
    h = h.replace('    <button type="action" class="toggle page-1" name="act_page_1" data-i18n="main">Main</button>\n',
                  '    <button type="action" class="toggle page-1" name="act_page_1" data-i18n="main">Main</button>\n'
                  '    <button type="action" class="toggle page-forms" name="act_page_forms" data-i18n="forms">Forms</button>\n', 1)
    h = h.replace('data-i18n="powers-gear">Powers &amp; Gear</button>',
                  'data-i18n="powers-gear">Powers &amp; Gear</button>\n    <button type="action" class="toggle page-details" name="act_page_details" data-i18n="details">Details</button>', 1)
    h = h.replace('<div class="page page1 page2 page3 powers conditions diceroller rollbar">', '<div class="page page1 page2 page3 powers forms details conditions diceroller rollbar">', 1)
    h = h.replace('<div class="page page1 page2 page3 scars-variations conditions powers logo">', '<div class="page page1 page2 page3 scars-variations conditions powers forms details logo">', 1)
    
    # active-form height/weight on main page (werewolf quick actions)
    _a = '<div class="section-header" data-i18n="attributes-u">ATTRIBUTES</div>'
    assert h.count(_a) == 1
    h = h.replace(_a, '<div class="main-forms game-line werewolf2" title="Shapeshift: click a form to change into it"><input type="hidden" class="urkhar-flag" name="attr_urkhar_enabled" value="0" /><div class="form-picker">' + btns + '</div></div>' + _a, 1)
    h = h.replace('<div class="quick-actions game-line werewolf2">', '<div class="quick-actions game-line werewolf2 breeds2"><span class="form-hw-mini" title="Active form height / weight"><span name="attr_form_height"></span> <span name="attr_form_weight"></span></span>', 1)
    js = '''
        // Form picker buttons + per-form height/weight on main page
        %s.forEach(f => on(`clicked:setform_${f}`, () => setAttrs({form: f})));
        const updateFormHW = () => getAttrs(["form","urkhar_enabled"].concat(%s.flatMap(f => [`fh_${f}_height`, `fh_${f}_weight`])), v => {
            let f = v.form || "hishu"; if (f === "urkhar" && v.urkhar_enabled !== "1") f = "gauru";
            setAttrs({form_height: v[`fh_${f}_height`] || "", form_weight: v[`fh_${f}_weight`] || ""});
        });
        on("change:form change:urkhar_enabled sheet:opened " + %s.flatMap(f => [`change:fh_${f}_height`, `change:fh_${f}_weight`]).join(" "), updateFormHW);
''' % ((json.dumps([k for k, _ in FORMS]),) * 3)
    return h, js
FD_CSS = '''
input.sheet-page[value="forms"] ~ .sheet-page:not(.sheet-forms), input.sheet-page[value="details"] ~ .sheet-page:not(.sheet-details) { display: none; }
input.sheet-page[value="forms"] ~ button.sheet-page-forms, input.sheet-page[value="details"] ~ button.sheet-page-details { background: #000; color: #fff; }
input.sheet-type:not([value="werewolf2"]):not([value="breeds2"]) ~ button.sheet-page-forms { display: none; }
.sheet-form-picker { display: flex; gap: 6px; flex-wrap: wrap; margin: 6px 0; }
button.sheet-form-btn { min-width: 90px; padding: 6px 10px; border: 2px solid #333; border-radius: 6px; background: #f4f0e8; font-weight: bold; }
''' + ''.join(f'input.sheet-form-cur[value="{k}"] + span.sheet-fb-{k} {{ color: #fff; }}\nbutton.sheet-form-btn input.sheet-form-cur[value="{k}"] ~ .sheet-fb-{k} {{ color: #fff; }}\n' for k, _ in FORMS) + '''
button.sheet-form-btn:has(input.sheet-form-cur[value="hishu"] + .sheet-fb-hishu), button.sheet-form-btn:has(input.sheet-form-cur[value="dalu"] + .sheet-fb-dalu), button.sheet-form-btn:has(input.sheet-form-cur[value="gauru"] + .sheet-fb-gauru), button.sheet-form-btn:has(input.sheet-form-cur[value="urshul"] + .sheet-fb-urshul), button.sheet-form-btn:has(input.sheet-form-cur[value="urhan"] + .sheet-fb-urhan), button.sheet-form-btn:has(input.sheet-form-cur[value="urkhar"] + .sheet-fb-urkhar) { background: var(--temp-dot, #aa5a1e); }
input.sheet-urkhar-flag:not([value="1"]) ~ .sheet-form-picker .sheet-urkhar-col { display: none; }
.sheet-form-active { margin: 6px 0; font-size: 13px; }
.sheet-form-hw-mini { font-size: 10px; color: #555; margin-right: 4px; }
.sheet-det-top { display: flex; gap: 12px; }
.sheet-det-portrait { width: 200px; }
.sheet-det-portrait img { display: block; width: 200px; min-height: 120px; max-height: 260px; object-fit: cover; border: 1px solid #333; background: rgba(0,0,0,.05); }
.sheet-det-portrait .sheet-portrait-ph { display: none; width: 200px; height: 200px; box-sizing: border-box; border: 1px dashed rgba(127,127,127,.6); border-radius: 4px; background: rgba(127,127,127,.12); color: rgba(127,127,127,.9); font-size: 12px; align-items: center; justify-content: center; }
.sheet-det-portrait input.sheet-portrait-flag[value=""] ~ img.sheet-portrait-img { display: none; }
.sheet-det-portrait input.sheet-portrait-flag[value=""] ~ .sheet-portrait-ph { display: flex; }
.sheet-det-grid { flex: 1; display: grid; grid-template-columns: repeat(2, 1fr); gap: 4px 12px; }
.sheet-det-grid label, .sheet-det-splat label, .sheet-det-long label { display: flex; flex-direction: column; font-weight: bold; font-size: 11px; }
.sheet-det-long textarea { min-height: 70px; width: 100%; }
.sheet-hw-table input { width: 90%; }
'''
FD_CSS += '''
input.sheet-urkhar-flag:not([value="1"]) ~ table .sheet-urkhar-col { display: none; }
table.sheet-hw-table { table-layout: fixed; width: 100%; }
'''

# ---- Willpower: spend (+3, all splats) / Hunter 2E "Risking Willpower" (HtV 2E ch.4, p.132) ----
RISK_OPTS = [('dice', 'Gain a three-die bonus'), ('exc3', 'Exceptional success on 3 successes instead of 5'),
             ('dmg', '+1 to the attack\u2019s weapon damage bonus'), ('nine', 'Gain the 9-again quality'),
             ('no10', 'Remove 10-again from an opponent\u2019s contested roll'), ('tactic', 'Enact a Tactic (counts as both benefits)')]
def wp_html(T):
    o = "<option value=\"\">Benefit\u2026</option>" + ''.join(f'<option value="{k}">{l}</option>' for k, l in RISK_OPTS)
    return (f'<div class="wp-bar"><label title="Spend 1 Willpower: +3 dice (all splats)"><input type="checkbox" name="attr_wp_spend" value="1" /> {T("wp-spend","Spend 1 WP (+3)")}</label><label class="spec-apply" title="+1 die when the selected Skill has a Specialty written in its drop-down"><input type="checkbox" name="attr_spec_apply" value="1" /> {T("spec-apply","Specialty (+1)")}</label>'
            f'<span class="game-line hunter2 risk-ctl"><label title="Risk 1 Willpower instead of spending it (once per scene, only on actions in direct pursuit of the Vigil that carry risk; never Perception/investigation, self-preservation, or activating Endowments)">'
            f'<input type="checkbox" name="attr_wp_risk" value="1" /> {T("wp-risk","Risk WP")}</label>'
            f'<select name="attr_risk_b1" title="Benefit 1">{o}</select><select name="attr_risk_b2" title="Benefit 2">{o}</select>'
            f'</span><label class="game-line werewolf" title="Your auspice moon is visible: Moon-Kissed Skills get +4 instead of +3 for Willpower"><input type="checkbox" name="attr_moon_visible" value="1" /> Auspice moon visible</label></div>')
WP_JS = r'''
        const RISK_TXT = %s;
        const updateRollEff = () => getAttrs(["rolltype","wp_spend","wp_risk","risk_b1","risk_b2","sheettype","skill_again","skill_again_names","skill_mk","moon_visible"], v => {
            let rt = v.rolltype || ")d10!cs>10}>@{success_target}]]}}";
            const risk = v.wp_risk === "1" && v.sheettype === "hunter2";
            let b = risk ? [v.risk_b1, v.risk_b2].filter(x => x) : [];
            if (b.includes("tactic")) b = ["tactic"];
            b = b.slice(0, 2);
            let dice = 0, tags = "";
            if (risk) {
                if (b.includes("dice")) dice += 3;
                if (b.includes("nine") && rt.indexOf("*0+1)") < 0 && rt.indexOf("!>8") < 0) rt = rt.replace(/d10(!)?/, "d10!>9");
                if (b.includes("exc3")) tags += " {{exc3=1}}";
                tags += " {{risk=" + (b.length ? b.map(k => RISK_TXT[k]).join("; ") : "no benefit chosen") + "}}";
            } else if (v.wp_spend === "1") { dice = (v.skill_mk === "1" && v.moon_visible === "1") ? 4 : 3; tags += dice === 4 ? " {{wpspend=1}} {{mk4=1}}" : " {{wpspend=1}}"; }
            const sq = v.skill_again || "";
            if (sq && rt.indexOf("*0+1)") < 0) {
                const cur = rt.indexOf("!>8") >= 0 ? 2 : rt.indexOf("!>9") >= 0 ? 1 : 0;
                const want = sq === "8" ? 2 : sq === "9" ? 1 : 0;
                if (want > cur) rt = rt.replace(/d10!?(>\d)?(cs>\d+)?/, want === 2 ? "d10!>8cs>8" : "d10!>9cs>9");
                if (sq === "no10" && cur === 0) rt = rt.replace(/d10!(cs>10)?/, "d10cs>10");
                tags += " {{skq=" + (sq === "no10" ? "no 10-again" : (Math.max(want, cur) === 2 ? "8" : "9") + "-again") + " (" + (v.skill_again_names || "skill") + ")}}";
            }
            setAttrs({rolltype_eff: rt + tags, wp_dice: dice}, {silent: true}, () => { if (globalThis.__hlAtk) globalThis.__hlAtk(); });
        });
        on("sheet:opened change:rolltype change:wp_spend change:wp_risk change:risk_b1 change:risk_b2 change:sheettype", updateRollEff);
''' % json.dumps({k: l for k, l in RISK_OPTS})
def wp_apply(h, T):
    n = h.count('@{rolltype}')
    h = h.replace('@{rolltype}', '@{rolltype_eff}')
    h = h.replace('@{wound_penalty}+@{cond_mod}', '@{wound_penalty}+@{wp_dice}+@{cond_mod}')
    h = h.replace('<input type="hidden" name="attr_rolltype" value=")d10!cs>10}>@{success_target}]]}}" />',
                  '<input type="hidden" name="attr_rolltype" value=")d10!cs>10}>@{success_target}]]}}" /><input type="hidden" name="attr_rolltype_eff" value=")d10!cs>10}>@{success_target}]]}}" /><input type="hidden" name="attr_wp_dice" value="0" />', 1)
    a = '<div class="rollcontainer">'
    assert a in h
    h = h.replace(a, wp_html(T) + a, 1)
    return h, n
WP_CSS = '''
.sheet-wp-bar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font-size: 11px; margin: 2px 0; width: 100%; }
div.sheet-wp-bar select, .charsheet div.sheet-wp-bar select { width: 170px !important; min-width: 170px; font-size: 10px; height: 20px; padding: 0; border: 1px solid #666; background: #fff; display: inline-block; }
.sheet-rolltemplate-cofd-entry .sheet-ce-risk { font-size: 11px; background: rgba(30,70,70,.12); border-left: 3px solid #1e4646; padding: 2px 4px; margin: 2px 0; }
'''


ARMOR_LINE = """<div class="armor-line">
  <input type="hidden" name="attr_armor_flag0" value="1" />
  <span class="al-h">Armor</span>
  <label>Name<input type="text" name="attr_armor_name0" /></label>
  <label>Gen<select name="attr_armor_general0">%(r)s</select></label>
  <label>Ball<select name="attr_armor_ballistic0">%(r)s</select></label>
  <label>Str<select name="attr_armor_strength0"><option value="0">—</option>%(s)s</select></label>
  <label>Def pen<select name="attr_armor_defense0">%(d)s</select></label>
  <label>Spd pen<select name="attr_armor_speed0">%(p)s</select></label>
  <label>Coverage<input type="text" name="attr_armor_coverage0" placeholder="torso, arms…" /></label>
  <label class="al-notes">Notes<input type="text" name="attr_armor_description0" /></label>
</div>""" % dict(r=''.join(f'<option value="{i}">{i}</option>' for i in range(0, 6)),
                 s=''.join(f'<option value="{i}">{i}</option>' for i in range(1, 6)),
                 d=''.join(f'<option value="{-i}">{-i if i else 0}</option>' for i in range(0, 4)),
                 p=''.join(f'<option value="{-i}">{-i if i else 0}</option>' for i in range(0, 5)))
def weapons_armor_page1(h, entry, html, T):
    import re, hurtlocker
    a = h.index('                            <div class="el_spacer"></div>\n                            <input type="hidden" name="attr_attack" value=')
    b = h.index('                            </div>\n                        </div>\n                   </div>\n                    <div class="game-line geist2-geist grow">', a)
    b += len('                            </div>\n')
    h = h[:a] + h[b:]
    # Hurt Locker: weapons + armor live in a full-width block below the multi-column area of page 1
    mk = '        <!-- MEMBERS AND REGALIA -->'
    assert h.count(mk) == 1
    h = h.replace(mk, '        <div class="p1-combat"><div class="p1-weapons">' + hurtlocker.weapons_entry(entry, T) + '</div>' + __import__('armormod').section(entry, T, hurtlocker.ARMOR) + '</div>\n' + mk, 1)
    # armor feeds derived stats from the single line (flag fixed at 1)
    for k, f in [('balistic_armor', 'ballistic'), ('general_armor', 'general'), ('defense_penalty', 'defense'), ('speed_penalty', 'speed')]:
        h, n = re.subn(r'<input type="hidden" name="attr_%s" value="[^"]*" />' % k, f'<input type="hidden" name="attr_{k}" value="(@{{armor_{f}0}}+0)" />', h)
        assert n == 1, k
    return h
WA_CSS = __import__("hurtlocker").CSS + """
.sheet-p1-weapons { width: 100%; margin-top: 6px; }
.sheet-armor-line { display: flex; flex-wrap: wrap; gap: 4px 8px; align-items: flex-end; border-top: 1px solid #555; border-bottom: 1px solid #555; padding: 4px 2px; margin: 6px 0; font-size: 11px; background: rgba(255,255,255,.35); }
.sheet-armor-line .sheet-al-h { font-weight: bold; font-size: 14px; }
.sheet-armor-line label { display: flex; flex-direction: column; font-weight: bold; }
.sheet-armor-line input[type=text] { width: 120px; }
.sheet-armor-line select { width: 52px !important; min-width: 52px; height: 20px; padding: 0; font-size: 11px; display: inline-block; }
.sheet-armor-line .sheet-al-notes { flex: 1; } .sheet-armor-line .sheet-al-notes input { width: 100%; }
.sheet-entry-section.sheet-weapons select { width: 100% !important; height: 22px; padding: 0; display: inline-block; }
/* transparent tab buttons; active = splat-colour text + underline */
button.sheet-toggle[name^="act_page_"] { background: transparent !important; border: none !important; box-shadow: none !important; color: #111; text-shadow: 0 0 3px #fff, 0 0 3px #fff, 0 0 6px #fff; padding: 2px 6px; border-bottom: 3px solid transparent !important; }
input.sheet-page[value="1"] ~ button.sheet-page-1, input.sheet-page[value="3"] ~ button.sheet-page-3, input.sheet-page[value="scars-variations"] ~ button.sheet-page-scars-variations,
input.sheet-page[value="conditions"] ~ button.sheet-page-conditions, input.sheet-page[value="powers"] ~ button.sheet-page-powers, input.sheet-page[value="forms"] ~ button.sheet-page-forms,
input.sheet-page[value="details"] ~ button.sheet-page-details, input.sheet-page[value="settings"] ~ button.sheet-page-settings
{ background: transparent !important; color: var(--temp-dot, #000) !important; border-bottom: 3px solid var(--temp-dot, #000) !important; text-shadow: 0 0 3px #fff, 0 0 3px #fff, 0 0 6px #fff; }
"""

ROLLER_CSS = """
/* ===== Polished on-sheet roller ===== */
.charsheet .sheet-diceroller.sheet-rollbar { background: rgba(255,255,255,.55); backdrop-filter: blur(2px); border: 1px solid var(--temp-dot,#333); border-left: 6px solid var(--temp-dot,#333); border-radius: 8px; padding: 6px 10px; box-shadow: 0 1px 4px rgba(0,0,0,.25); font-family: inherit; }
.charsheet .sheet-rollbar .sheet-diceroller-grid { display: flex; flex-wrap: wrap; gap: 6px 10px; align-items: center; }
.charsheet .sheet-rollbar .sheet-diceroller-grid > .sheet-span { order: 1; }
.charsheet .sheet-rollbar .sheet-wp-bar { order: 2; width: auto; flex: 1 1 auto; margin: 0; }
.charsheet .sheet-rollbar .sheet-rollcontainer { order: 3; }
.charsheet .sheet-rollbar .sheet-diceroller-options { order: 4; }
.charsheet .sheet-rollbar .sheet-rolldisplay { order: 5; flex: 1 1 160px; }
.charsheet .sheet-rollbar .sheet-rolldisplay ~ .sheet-diceroller-options { order: 6; flex: 1 1 100%; }
/* buttons: Initiative / Perception */
.charsheet .sheet-rollbar button[name="roll_initiative"], .charsheet .sheet-rollbar button.sheet-perception { background: var(--pa, var(--temp-dot,#333)) !important; color: #fff !important; border: none !important; border-radius: 14px; padding: 3px 12px; font-size: 12px; font-weight: bold; box-shadow: 0 1px 2px rgba(0,0,0,.4); }
/* segmented toggles */
.charsheet .sheet-rollbar .sheet-diceroller-options { display: inline-flex; flex-wrap: wrap; gap: 0; border: 1px solid var(--temp-dot,#333); border-radius: 6px; overflow: hidden; background: rgba(255,255,255,.4); }
.charsheet .sheet-rollbar .sheet-diceroller-options > button.sheet-toggle { display: inline-block; margin: 0; padding: 3px 9px; font-size: 11px; font-weight: bold; font-family: inherit; color: #222; background: transparent; border: none; border-right: 1px solid rgba(0,0,0,.15); text-shadow: none !important; line-height: 16px; }
.charsheet .sheet-rollbar .sheet-diceroller-options > button.sheet-toggle:last-child { border-right: none; }
.charsheet .sheet-rollbar .sheet-diceroller-options > button.sheet-toggle:hover { background: rgba(0,0,0,.08); }
""" + "".join(f"""input.sheet-rollstyle[value="{v}"] ~ * button.sheet-rollstyle-{v}, input.sheet-rollstyle[value="{v}"] ~ .sheet-diceroller-grid button.sheet-rollstyle-{v} {{ background: var(--pa, var(--temp-dot,#333)) !important; color: #fff !important; }}
""" for v in ["sheet", "attack", "simple"]) + "".join(f"""input.sheet-rolltype-select[value="{v}"] ~ * button.sheet-rolltype-{v} {{ background: var(--pa, var(--temp-dot,#333)) !important; color: #fff !important; }}
""" for v in ["chance", "normal", "9-again", "8-again", "dont-reroll", "chance-rote", "rote"]) + """
/* d10 roll button */
.charsheet .sheet-rollbar .sheet-rollcontainer button[type=roll] { filter: drop-shadow(0 1px 2px rgba(0,0,0,.5)); transform: scale(1.15); }
/* roll display textarea */
.charsheet .sheet-rollbar .sheet-rolldisplay textarea, .charsheet .sheet-rollbar .sheet-rolldisplay > div { width: 100%; height: 24px; min-height: 24px; resize: none; border: 1px solid rgba(0,0,0,.3); border-radius: 4px; background: rgba(255,255,255,.6); font-size: 11px; padding: 2px 6px; box-sizing: border-box; line-height: 18px; }
/* WP pills */
.charsheet .sheet-wp-bar { gap: 6px; font-size: 11px; }
.charsheet .sheet-wp-bar label { display: inline-flex; align-items: center; gap: 4px; padding: 2px 10px 2px 4px; border: 1px solid var(--temp-dot,#333); border-radius: 12px; background: rgba(255,255,255,.5); font-weight: bold; cursor: pointer; }
.charsheet .sheet-wp-bar label input[type=checkbox] { margin: 0; width: 13px; height: 13px; accent-color: var(--temp-dot,#333); }
.charsheet .sheet-wp-bar .sheet-risk-ctl { display: inline-flex; gap: 6px; align-items: center; }
.charsheet .sheet-wp-bar select, .charsheet div.sheet-wp-bar select { width: 165px !important; min-width: 0; height: 22px; padding: 0 4px; font-size: 11px; border: 1px solid rgba(0,0,0,.35); border-radius: 4px; background: rgba(255,255,255,.7); }
/* ===== Dark mode (Roll20 adds .sheet-darkmode to the sheet root) ===== */
.sheet-darkmode .sheet-diceroller.sheet-rollbar, .charsheet.sheet-darkmode .sheet-diceroller.sheet-rollbar { background: rgba(20,20,24,.72); color: #e8e8e8; }
.sheet-darkmode .sheet-rollbar .sheet-diceroller-options { background: rgba(0,0,0,.35); }
.sheet-darkmode .sheet-rollbar .sheet-diceroller-options > button.sheet-toggle { color: #e8e8e8; border-right-color: rgba(255,255,255,.15); }
.sheet-darkmode .sheet-rollbar .sheet-rolldisplay textarea, .sheet-darkmode .sheet-rollbar .sheet-rolldisplay > div, .sheet-darkmode .sheet-wp-bar label, .sheet-darkmode .sheet-wp-bar select { background: rgba(0,0,0,.45); color: #eee; border-color: rgba(255,255,255,.3); }
"""
ROLLER_CSS += """
.charsheet .sheet-rollbar .sheet-diceroller-grid { border: none !important; }
.charsheet .sheet-rollbar .sheet-diceroller-grid > * { border: none; }
.charsheet .sheet-rollbar .sheet-diceroller-grid > .sheet-diceroller-options { flex-direction: row !important; align-items: stretch; border: 1px solid var(--temp-dot,#333) !important; flex: 0 0 auto; }
.charsheet .sheet-rollbar .sheet-diceroller-grid > .sheet-diceroller-options > * { padding: 3px 9px; width: auto; }
.charsheet .sheet-rollbar .sheet-rolldisplay ~ .sheet-diceroller-options { flex: 0 1 auto !important; }
.charsheet .sheet-rollbar .sheet-rollcontainer { width: 38px; height: 38px; flex: 0 0 38px; }
.charsheet .sheet-rollbar .sheet-rolldisplay { justify-content: flex-start; }
.charsheet .sheet-rollbar .sheet-diceroller .sheet-rolldisplay > *, .charsheet .sheet-rollbar .sheet-rolldisplay > * { height: 24px !important; width: 100% !important; text-align: left; padding: 2px 6px !important; }
.charsheet .sheet-rollbar .sheet-wp-bar { flex: 1 1 100%; order: 2; }
"""
