"""2026-10-31: merit categories + Style maneuver slots, Main middle sub-tabs, Config tab merit effects."""
import re, html
CATS = [('Mental', 'Mental'), ('Physical', 'Physical'), ('Social', 'Social'),
        ('Supernatural', 'Supernatural'), ('Splat', 'Splat-specific')]
CAT_SELECT = 'select:=-;' + ';'.join(f'{v}={l}' for v, l in CATS)
NSLOT = 5

def _slot(n):
    post = html.escape('&{template:cofd-entry} {{splat=@{game_line}}} {{kind=Style Maneuver}} {{name=@{mv%d_name}}} '
                       '{{subtitle=@{merit_name}}} {{f_level=@{mv%d_lvl}}} {{f_description=@{mv%d_effect}}}' % (n, n, n), quote=True)
    opts = ''.join(f'<option value="{i}"{" selected" if i == n else ""}>{"&#9679;" * i}</option>' for i in range(1, 6))
    return (f'<div class="mv mv-{n}"><input type="hidden" class="mvon" name="attr_mv{n}_on" value="1" />'
            f'<div class="mv-row"><select class="mv-lvl" name="attr_mv{n}_lvl" title="Dot level">{opts}</select>'
            f'<input type="text" class="mv-name" name="attr_mv{n}_name" placeholder="Maneuver / bonus name" />'
            f'<button type="roll" class="mv-post" name="roll_mv{n}_post" title="Post this maneuver to chat" value="{post}">Post</button>'
            f'<span class="mv-lock">needs more dots</span></div>'
            f'<textarea class="mv-effect" name="attr_mv{n}_effect" rows="2" placeholder="Effect"></textarea></div>')

STYLE_BLOCK = ('<div class="style-block"><div class="style-title">Style maneuvers (one slot per dot; slots above the merit rating are greyed out)</div>'
               + ''.join(_slot(n) for n in range(1, NSLOT + 1)) + '</div>')

def merit_html(mh):
    """mh: html from entry('merits', ...)."""
    flags = ('<input type="hidden" class="mcat-flag" name="attr_mcat" value="" /><input type="hidden" class="mstyle-flag" name="attr_mstyle" value="0" />')
    mh = mh.replace('<div class="entry">\n<input type="checkbox" class="entry-toggle"', '<div class="entry">\n' + flags + '\n<input type="checkbox" class="entry-toggle"', 1)
    assert 'mcat-flag' in mh
    j = mh.index('name="attr_mcat"', mh.index('<select')); j = mh.index('</label>', j) + len('</label>')
    mh = mh[:j] + '<label class="mstyle-cb" title="Fighting/Social/Mental Style: shows the 5 maneuver slots; independent of the category"><input type="checkbox" name="attr_mstyle" value="1" /> Style</label>' + mh[j:]
    i = mh.index('<label><span data-i18n="lbl-prereq">')
    mh = mh[:i] + STYLE_BLOCK + mh[i:]
    fopts = '<option value="all">All</option>' + ''.join(f'<option value="{v}">{l}</option>' for v, l in CATS) + '<option value="style">Styles</option><option value="none">Uncategorised</option>'
    tools = (f'<select class="mfilter-sel" name="attr_merit_filter" title="Show only one category">{fopts}</select>'
             '<label class="mgroup" title="Sort the list by category"><input type="checkbox" name="attr_merit_group" value="1" />Group</label>')
    mh = mh.replace('<span data-i18n="merits">Merits</span></span>', '<span data-i18n="merits">Merits</span></span>' + tools, 1)
    mh = mh.replace('<fieldset class="repeating_merits">', '<input type="hidden" class="mfilter" name="attr_merit_filter" value="all" />'
                    '<input type="hidden" class="mgroup-flag" name="attr_merit_group" value="0" />\n<fieldset class="repeating_merits">', 1)
    return mh

EXTRA_HEADER = '<span class="mcat-badge" name="attr_mcat"></span><span class="mstyle-badge">Style</span>'

def mid_tabs(h):
    """Sub-tab bar inside the Main tab's middle (OTHER TRAITS) area."""
    a = '<div class="columns">\n                            <!-- MERITS -->'
    assert h.count(a) == 1, 'mid anchor'
    i = h.index(a)
    # splat label spans from the OTHER TRAITS subheader of the second column
    j = h.index('<div class="subheader">', h.index('<!-- OTHER TRAITS -->', i)); k = h.index('</div>', j)
    spans = h[j + len('<div class="subheader">'):k]
    spans = spans.replace('data-i18n="renown">Renown<', '>Gifts &amp; Renown<').replace('data-i18n="other">Other<', '>Other Traits<')
    spans = re.sub(r' data-i18n="[^"]*"', '', spans)
    bar = ('<input type="hidden" class="midtab" name="attr_mid_tab" value="merits" />\n'
           '<div class="midtabs">'
           '<button type="action" class="midtab-btn mt-merits" name="act_midtab_merits">Merits</button>'
           f'<button type="action" class="midtab-btn mt-powers" name="act_midtab_powers">{spans.strip()}</button>'
           '<button type="action" class="midtab-btn mt-weapons" name="act_midtab_weapons" title="Weapons and attack rolls">Weapons</button>'
           '<button type="action" class="midtab-btn mt-kuruth game-line werewolf2" name="act_midtab_kuruth" title="Death Rage: Kuruth triggers and Wasu-Im / Basu-Im rolls">Kuruth</button>'
           '<button type="action" class="midtab-btn mt-gear" name="act_midtab_gear" title="Armor, equipment and Expanded Merits">Gear</button>'
           '<button type="action" class="midtab-btn mt-notes" name="act_midtab_notes" title="Character details, portrait and notes">Notes</button>'
           '</div>\n')
    return h[:i] + bar + h[i:]

CONFIG_BLOCK = '''
        <div class="subheader">Portrait</div>
        <div class="merit-fx"><label>Portrait image URL <input type="text" name="attr_portrait_url" placeholder="blank = use the character avatar" style="width:320px" /></label>
          <span class="hint">Shown beside the dice roller and on Notes. Leave blank to use the Roll20 avatar.</span></div>
        <div class="subheader">Merit effects (feed derived stats)</div>
        <div class="merit-fx">
          <label title="Read Fleet of Foot, Fast Reflexes, Iron Stamina, Giant, Small-Framed, Hardy and Defensive Combat from the Merits list and fill the fields below automatically"><input type="checkbox" name="attr_merit_auto" value="1" checked /> Auto-detect from the Merits list</label>
          <span class="hint">Fleet of Foot adds to Speed, Fast Reflexes to Initiative, Iron Stamina offsets wound penalties (the number fields further down this tab). Giant / Small-Framed set the Size flags below (Size and Health). Defensive Combat sets the Defense trait. Hardy is shown as a reminder (situational dice).</span>
          <label>Defensive Combat
            <select name="attr_defensive_combat"><option value="none">None (Athletics)</option><option value="brawl">Brawl</option><option value="weaponry">Weaponry</option></select></label>
          <span class="hint" name="attr_merit_fx_summary"></span>
        </div>
        <div class="spacer"></div>
'''

def config(h):
    a = '<div class="sheet-edition-label">' if '<div class="sheet-edition-label"><span data-i18n="splat-u">' in h else '<div class="edition-label">'
    anchor = a + '<span data-i18n="splat-u">'
    assert anchor in h, 'config anchor'
    h = h.replace(anchor, '<div class="config-title">CONFIG</div>\n        ' + anchor, 1)
    i = h.index('<div class="edition-label"><span data-i18n="dice-rules-u">')
    j = h.index('<div class="spacer"></div>', h.index('</div>', h.index('class="dice-rule"', i)))
    h = h[:j] + CONFIG_BLOCK + h[j:]
    return h

JS = r'''
        /* ===== merits: categories, Style maneuver slots, mid tabs, merit effects ===== */
        ["merits","powers","weapons","kuruth","gear","notes"].forEach((t) => on(`clicked:midtab_${t}`, () => setAttrs({mid_tab: t})));
        const MV_N = %NSLOT%;
        const mvUpdate = (ids) => {
            const keys = [];
            ids.forEach((id) => { keys.push(`repeating_merits_${id}_merit`); for (let n = 1; n <= MV_N; n++) keys.push(`repeating_merits_${id}_mv${n}_lvl`); });
            getAttrs(keys, (v) => {
                const u = {};
                ids.forEach((id) => { const r = parseInt(v[`repeating_merits_${id}_merit`]) || 0;
                    for (let n = 1; n <= MV_N; n++) { const l = parseInt(v[`repeating_merits_${id}_mv${n}_lvl`]) || n; u[`repeating_merits_${id}_mv${n}_on`] = r >= l ? "1" : "0"; } });
                setAttrs(u, {silent: true});
            });
        };
        const mmRowOf = (s) => (s.match(/^repeating_merits_([^_]+)_/i) || [])[1];
        on("change:repeating_merits:merit " + [...Array(MV_N).keys()].map(i => `change:repeating_merits:mv${i + 1}_lvl`).join(" "), (ev) => { const id = mmRowOf(ev.sourceAttribute || ""); if (id) mvUpdate([id]); });
        const STYLE_RE = /style|relentless assault|grappling|boxing|kung fu|krav maga|parkour|sniping|street fighting|weaponry|systema|berserker|fenris/i;
        const MCAT_GUESS = [[STYLE_RE, "Physical"],
            [/defensive combat|fast reflexes|close quarters|ambidextrous|armed defense|firefight/i, "Physical"],
            [/iron stamina|fleet of foot|giant|hardy|small.framed|strong back|stunt driver|quick draw|athletics dodge|survival/i, "Physical"],
            [/language|encyclopedic|eidetic|common sense|danger sense|direction sense|indomitable|meditative|trained observer|investigative|good time|holistic|library|multilingual|professional|scarred|tolerance/i, "Mental"],
            [/resources|mentor|allies|contacts|retainer|status|fame|safe ?place|safehouse|striking looks|barfly|inspiring|staff|true friend|mystery cult|alternate identity|anonymity|fast.talking|pusher|sympathetic|table turner|takes one|untouchable|closed book|cheap shot|small unit|hobbyist/i, "Social"],
            [/totem|pack|territorial|moon.kissed|favored form|wolf.blooded|feral|lodge|sacred|eidolon|wind|weakened bond|fetish|hunting|ritualist|anchor|dream visions|vitae|feeding|herd|haven|mandragora|kindred|dynasty|clan|covenant|blood/i, "Splat"],
            [/psychic|medium|unseen sense|clairvoyance|telekinesis|aura|biokinesis|apportation|thief of fate|laying on hands|omen sensitivity/i, "Supernatural"]];
        on("sheet:opened", () => getSectionIDs("repeating_merits", (ids) => {
            if (!ids.length) return;
            const keys = []; ids.forEach((id) => keys.push(`repeating_merits_${id}_mcat`, `repeating_merits_${id}_mcat_mig`, `repeating_merits_${id}_mcat_mig2`, `repeating_merits_${id}_mstyle`, `repeating_merits_${id}_merit_name`));
            getAttrs(keys, (v) => {
                const u = {};
                ids.forEach((id) => { const p = `repeating_merits_${id}_`;
                    if (v[p + "mcat_mig2"] !== "1") {   // r6: Fighting/Style are not categories: Fighting -> Physical, Style -> Physical + Style flag
                        u[p + "mcat_mig2"] = "1";
                        if (v[p + "mcat"] === "Fighting") { u[p + "mcat"] = "Physical"; v[p + "mcat"] = "Physical"; }
                        if (v[p + "mcat"] === "Style") { u[p + "mcat"] = "Physical"; u[p + "mstyle"] = "1"; v[p + "mcat"] = "Physical"; }
                        else if (v[p + "mstyle"] !== "1" && STYLE_RE.test(v[p + "merit_name"] || "") && (!v[p + "mcat"] || v[p + "mcat"] === "Physical")) u[p + "mstyle"] = "1";
                    }
                    if (v[p + "mcat_mig"] === "1") return;
                    u[p + "mcat_mig"] = "1";
                    if (v[p + "mcat"]) return;   // never overwrite a category the player chose
                    const nm = v[p + "merit_name"] || ""; const g = MCAT_GUESS.find(([re]) => re.test(nm));
                    if (g) u[p + "mcat"] = g[1]; });
                setAttrs(u, {silent: true}, () => mvUpdate(ids));
            });
        }));
        const FX_KEYS = ["fleet_of_foot", "fast_reflexes", "iron_stamina", "giant", "small_framed"];
        const meritFx = () => getSectionIDs("repeating_merits", (ids) => {
            const keys = ["merit_auto", "defensive_combat", "merit_fx_keys", ...FX_KEYS]; ids.forEach((id) => keys.push(`repeating_merits_${id}_merit_name`, `repeating_merits_${id}_merit`));
            getAttrs(keys, (v) => {
                const u = {}; const dc = v.defensive_combat || "none"; const auto = v.merit_auto !== "0";
                const found = {}; let hardy = 0;
                ids.forEach((id) => { const nm = (v[`repeating_merits_${id}_merit_name`] || "").toLowerCase(); const r = parseInt(v[`repeating_merits_${id}_merit`]) || 0;
                    if (/fleet of foot/.test(nm)) found.fleet_of_foot = r; if (/fast reflexes/.test(nm)) found.fast_reflexes = r;
                    if (/iron stamina/.test(nm)) found.iron_stamina = r;
                    if (/\bgiant\b/.test(nm)) found.giant = 1; if (/small.framed/.test(nm)) found.small_framed = 1;
                    if (/\bhardy\b/.test(nm)) hardy = r;
                    if (/defensive combat/.test(nm)) found.dc = /weapon/.test(nm) ? "weaponry" : "brawl"; });
                let d = dc; const prev = (v.merit_fx_keys || "").split(",").filter(Boolean); const now = [];
                if (auto) {
                    FX_KEYS.forEach((k) => {
                        if (found[k] !== undefined) { if (String(v[k]) !== String(found[k])) u[k] = found[k]; now.push(k); }
                        else if (prev.indexOf(k) >= 0) u[k] = 0;   // only clear values this feature set itself; manual entries are kept
                    });
                    if (found.dc && dc === "none") { d = found.dc; u.defensive_combat = d; }
                }
                u.merit_fx_keys = now.join(",");
                if (d === "brawl") u.defense_select = "lowest_plus_brawl";
                else if (d === "weaponry") u.defense_select = "lowest_plus_weaponry";
                const s = [];
                if (auto) {
                    if (found.fleet_of_foot) s.push(`Fleet of Foot ${found.fleet_of_foot} (Speed +${found.fleet_of_foot})`);
                    if (found.fast_reflexes) s.push(`Fast Reflexes ${found.fast_reflexes} (Initiative +${found.fast_reflexes})`);
                    if (found.iron_stamina) s.push(`Iron Stamina ${found.iron_stamina} (offsets ${found.iron_stamina} wound penalty)`);
                    if (found.giant) s.push("Giant (Size +1, Health +1)");
                    if (found.small_framed) s.push("Small-Framed (Size -1, Health -1; +2 to hide or spot-evade and to roll stealthily)");
                    if (hardy) s.push(`Hardy ${hardy} (+${hardy} to resist disease, poison, deprivation, unconsciousness and suffocation)`);
                }
                if (d !== "none") s.push("Defensive Combat (" + d + ": Defense uses " + (d === "brawl" ? "Brawl" : "Weaponry") + " instead of Athletics)");
                u.merit_fx_summary = s.length ? "Active effects: " + s.join("; ") : "Active effects: none";
                setAttrs(u);
            });
        });
        on("sheet:opened change:merit_auto change:defensive_combat change:repeating_merits:merit_name change:repeating_merits:merit remove:repeating_merits", meritFx);
'''.replace('%NSLOT%', str(NSLOT))

def css():
    o = []
    D = ['input.sheet-dm[value="1"] ~ .sheet-background', '.sheet-darkmode']
    # badge
    o.append('.charsheet .sheet-entry-head .sheet-mcat-badge { display: inline-block; flex: 0 0 auto; margin: 0 4px; padding: 0 4px; border-radius: 7px; font: bold 9px/13px Arial, sans-serif; text-transform: uppercase; letter-spacing: .4px; border: 1px solid currentColor; opacity: .9; color: #6a5a3a; vertical-align: middle; }')
    o.append('.charsheet .sheet-entry-head .sheet-mcat-badge:empty { display: none; }')
    col = {'Mental': '#3a6fb0', 'Physical': '#3d8a3d', 'Social': '#a0602a', 'Fighting': '#a83232', 'Style': '#b0303c', 'Supernatural': '#7a4bb0', 'Splat': '#8a7a2a'}
    dcol = {'Mental': '#8ab4ff', 'Physical': '#8fd48f', 'Social': '#f0b070', 'Fighting': '#ff8a8a', 'Style': '#ff9fb0', 'Supernatural': '#c9a2ff', 'Splat': '#e6d27a'}
    for k in col:
        o.append(f'.charsheet .sheet-entry > input.sheet-mcat-flag[value="{k}"] ~ .sheet-entry-head .sheet-mcat-badge {{ color: {col[k]}; }}')
        o.append(f'{D[0]} .sheet-entry > input.sheet-mcat-flag[value="{k}"] ~ .sheet-entry-head .sheet-mcat-badge, {D[1]} .sheet-entry > input.sheet-mcat-flag[value="{k}"] ~ .sheet-entry-head .sheet-mcat-badge {{ color: {dcol[k]}; }}')
    o.append('.charsheet .sheet-entry > input.sheet-mstyle-flag:not([value="1"]) ~ .sheet-entry-head .sheet-mstyle-badge { display: none; }')
    o.append('.charsheet .sheet-entry-head .sheet-mstyle-badge { display: inline-block; flex: 0 0 auto; margin: 0 4px 0 0; padding: 0 4px; border-radius: 7px; font: bold 9px/13px Arial, sans-serif; text-transform: uppercase; color: #ff9fb0; background: rgba(176,48,60,.18); }')
    o.append('.charsheet label.sheet-mstyle-cb { display: inline-flex !important; align-items: center; gap: 4px; flex: 0 0 auto !important; }')
    o.append('.charsheet input.sheet-mfilter[value="style"] ~ .repcontainer > .repitem:not(:has(input.sheet-mstyle-flag[value="1"])) { display: none !important; }')
    # style block
    o.append('.charsheet .sheet-style-block { display: none; flex: 1 1 100%; width: 100%; margin: 3px 0 2px; padding: 3px 4px; border: 1px dashed rgba(160,60,60,.55); border-radius: 3px; box-sizing: border-box; }')
    o.append('.charsheet .sheet-entry > input.sheet-mstyle-flag[value="1"] ~ .sheet-entry-body .sheet-style-block { display: block; }')
    o.append('.charsheet .sheet-style-block .sheet-style-title { font: bold 10px/14px Arial, sans-serif; text-transform: uppercase; letter-spacing: .3px; margin-bottom: 2px; }')
    o.append('.charsheet .sheet-style-block .sheet-mv { margin: 0 0 3px; }')
    o.append('.charsheet .sheet-style-block .sheet-mv-row { display: flex; align-items: center; gap: 4px; }')
    o.append('.charsheet .sheet-style-block select.sheet-mv-lvl { flex: 0 0 62px; width: 62px !important; height: 20px !important; margin: 0 !important; padding: 0 2px !important; font-size: 10px !important; letter-spacing: -1px; }')
    o.append('.charsheet .sheet-style-block input.sheet-mv-name { flex: 1 1 auto; min-width: 0; width: auto !important; height: 20px !important; margin: 0 !important; padding: 0 4px !important; font-weight: bold; font-size: 12px !important; box-sizing: border-box; }')
    o.append('.charsheet .sheet-style-block button.sheet-mv-post { flex: 0 0 auto; height: 20px; padding: 0 6px !important; margin: 0 !important; font-size: 10px !important; line-height: 18px !important; }')
    o.append('.charsheet .sheet-style-block button.sheet-mv-post::before { content: none !important; display: none !important; }')
    o.append('.charsheet .sheet-style-block textarea.sheet-mv-effect { display: block; width: 100% !important; box-sizing: border-box; min-height: 30px !important; height: 30px; margin: 2px 0 0 !important; font-size: 11px !important; }')
    o.append('.charsheet .sheet-style-block .sheet-mv-lock { display: none; flex: 0 0 auto; font: italic 9px/12px Arial, sans-serif; opacity: .8; }')
    o.append('.charsheet .sheet-style-block .sheet-mv > input.sheet-mvon[value="0"] ~ * { opacity: .38; }')
    o.append('.charsheet .sheet-style-block .sheet-mv > input.sheet-mvon[value="0"] ~ .sheet-mv-row .sheet-mv-lock { display: inline; }')
    o.append('.charsheet .sheet-style-block .sheet-mv > input.sheet-mvon[value="0"] ~ .sheet-mv-row button.sheet-mv-post { pointer-events: none; }')
    # filter + group
    o.append('.charsheet .sheet-entry-section.sheet-merits .sheet-entry-section-head select.sheet-mfilter-sel { width: 92px !important; height: 18px !important; margin: 0 2px 0 6px !important; padding: 0 2px !important; font-size: 10px !important; line-height: 16px; vertical-align: middle; }')
    o.append('.charsheet .sheet-entry-section.sheet-merits .sheet-entry-section-head label.sheet-mgroup { display: inline-flex !important; align-items: center; gap: 2px; margin: 0 4px 0 0 !important; font: 10px/16px Arial, sans-serif !important; vertical-align: middle; }')
    o.append('.charsheet .sheet-entry-section.sheet-merits .sheet-entry-section-head label.sheet-mgroup input { margin: 0 !important; width: 11px !important; height: 11px !important; }')
    for v, _ in CATS:
        o.append(f'.charsheet input.sheet-mfilter[value="{v}"] ~ .repcontainer > .repitem:not(:has(input.sheet-mcat-flag[value="{v}"])) {{ display: none !important; }}')
    o.append('.charsheet input.sheet-mfilter[value="none"] ~ .repcontainer > .repitem:has(input.sheet-mcat-flag:not([value=""])) { display: none !important; }')
    o.append('.charsheet input.sheet-mgroup-flag[value="1"] ~ .repcontainer[data-groupname="repeating_merits"] { display: flex !important; flex-direction: column; }')
    for i, (v, _) in enumerate(CATS):
        o.append(f'.charsheet input.sheet-mgroup-flag[value="1"] ~ .repcontainer > .repitem:has(input.sheet-mcat-flag[value="{v}"]) {{ order: {i + 1}; }}')
    o.append('.charsheet input.sheet-mgroup-flag[value="1"] ~ .repcontainer > .repitem:has(input.sheet-mcat-flag[value=""]) { order: 99; }')
    # mid tabs
    o.append('.charsheet .sheet-midtabs { display: flex; flex-wrap: wrap; gap: 0; margin: 0 0 5px; border-bottom: 1px solid rgba(160,130,90,.6); }')
    o.append('.charsheet .sheet-midtabs button.sheet-midtab-btn { flex: 0 0 auto; margin: 0 2px -1px 0 !important; padding: 2px 9px !important; height: auto; font: bold 12px/16px Arial, sans-serif !important; border: 1px solid rgba(160,130,90,.6) !important; border-bottom: 0 !important; border-radius: 4px 4px 0 0 !important; background-image: none !important; background-color: rgba(128,128,128,.12) !important; box-shadow: none !important; text-shadow: none !important; cursor: pointer; opacity: .75; }')
    o.append('.charsheet .sheet-midtabs button.sheet-midtab-btn::before { content: none !important; display: none !important; }')
    o.append('.charsheet .sheet-midpane { display: none; min-width: 0; }')
    for t in ('powers', 'weapons', 'kuruth', 'gear', 'notes'):
        o.append(f'.charsheet input.sheet-midtab[value="{t}"] ~ .sheet-midpane.sheet-mp-{t} {{ display: block !important; }}')
    o.append('.charsheet input.sheet-midtab:is([value="weapons"],[value="kuruth"],[value="gear"],[value="notes"]) ~ div:not(.sheet-midtabs):not(.sheet-midpane) { display: none !important; }')
    o.append('.charsheet .sheet-midpane .sheet-leon-pane { padding: 0 !important; margin: 0 !important; width: 100%; box-sizing: border-box; overflow-x: auto; }')
    o.append('.charsheet .sheet-midpane .sheet-two-col { display: grid !important; grid-template-columns: minmax(0,1fr) minmax(0,1fr); gap: 6px; }')
    o.append('.charsheet .sheet-midpane table.sheet-forms-table { font-size: 10px; width: 100%; }')
    # dedupe: base-sheet power lists replaced by the expandable lists (data migrated by the worker)
    for t in ('werewolf2',):
        o.append(f'.charsheet input.sheet-type[value="{t}"] ~ * input.sheet-midtab ~ .sheet-columns.sheet-werewolf, .charsheet input.sheet-type[value="{t}"] ~ * input.sheet-midtab ~ .sheet-columns.sheet-mummy {{ display: none !important; }}')
    for t in ('werewolf2', 'vampire2'):
        o.append(f'.charsheet input.sheet-type[value="{t}"] ~ * input.sheet-midtab ~ .sheet-midtabs + .sheet-columns > div:not(:first-child) {{ display: none !important; }}')
    for t in ('merits', 'powers', 'weapons', 'kuruth', 'gear', 'notes'):
        o.append(f'.charsheet input.sheet-midtab[value="{t}"] + .sheet-midtabs button.sheet-mt-{t} {{ opacity: 1; background-color: rgba(160,40,40,.28) !important; border-color: #b06a3a !important; }}')
    o.append('.charsheet input.sheet-midtab[value="merits"] ~ .sheet-midtabs + .sheet-columns > div:not(:first-child) { display: none !important; }')
    o.append('.charsheet input.sheet-midtab[value="merits"] ~ .sheet-midtabs + .sheet-columns ~ div { display: none !important; }')
    o.append('.charsheet input.sheet-midtab[value="powers"] ~ .sheet-midtabs + .sheet-columns > div:first-child, .charsheet input.sheet-midtab[value="powers"] ~ .sheet-midtabs + .sheet-columns > div.sheet-horizontal-spacer { display: none !important; }')
    # config tab
    o.append('.charsheet .sheet-config-title { font: bold 16px/22px Arial, sans-serif; letter-spacing: 2px; margin: 0 0 6px; color: #d4b25a; }')
    o.append('.charsheet .sheet-merit-fx { display: flex; flex-direction: column; gap: 4px; }')
    o.append('.charsheet .sheet-merit-fx label { display: flex !important; align-items: center; gap: 6px; margin: 0 !important; }')
    o.append('.charsheet .sheet-merit-fx label input[type=checkbox] { margin: 0 !important; }')
    o.append('.charsheet .sheet-merit-fx select { width: 160px !important; height: 22px !important; margin: 0 !important; padding: 0 4px !important; }')
    o.append('.charsheet .sheet-merit-fx .sheet-hint { font-size: 11px; opacity: .85; line-height: 14px; }')
    o.append('.charsheet button.sheet-page-settings { margin-right: 14px !important; padding: 1px 8px !important; border: 1px solid rgba(212,178,90,.7) !important; border-radius: 4px !important; font: bold 11px/16px Arial, sans-serif !important; letter-spacing: 1px; }')
    # chevron toggles: hit area centred exactly on the CSS chevron (all collapsible entries incl. Blood / Bone)
    S = '.charsheet .sheet-background .sheet-entry'
    o.append(f'{S} > .sheet-entry-head {{ position: static !important; }}')
    o.append(f'{S} {{ position: relative; }}')
    o.append(f'{S} > input[type=checkbox].sheet-entry-toggle {{ position: absolute !important; left: 1.5px !important; top: 2.5px !important; width: 16px !important; height: 16px !important; margin: 0 !important; z-index: 3; }}')
    o.append(f'{S} > input[type=checkbox].sheet-entry-toggle + .sheet-entry-head::before {{ left: 6px !important; top: 7px !important; }}')
    o.append(f'{S} > input[type=checkbox].sheet-entry-toggle:checked + .sheet-entry-head::before {{ left: 6px !important; top: 6px !important; }}')
    # fix: dark-mode base rule (background-color reset on every dot) blanked the fill of entry rating dots (merits, gifts, rites ...) and Renown
    for n in range(1, 6):
        o.append(f'.charsheet .sheet-background .repitem .sheet-entry-head .sheet-dots > input[type=hidden][value="{n}"] ~ button.sheet-dot:not(.sheet-zero):not(.sheet-ne-{n}), '
                 f'.charsheet .sheet-background .sheet-renown-row .sheet-dots > input[type=hidden][value="{n}"] ~ button.sheet-dot:not(.sheet-zero):not(.sheet-ne-{n}) {{ background-color: currentColor !important; }}')
    # skills width
    o.append('.charsheet .sheet-flex > .sheet-skills { flex: 0 0 172px !important; width: 172px !important; max-width: 172px !important; grid-template-columns: minmax(0,1fr) auto !important; }')
    o.append('.charsheet .sheet-skills button.sheet-toggle { flex: 0 1 auto !important; min-width: 0 !important; overflow: hidden !important; text-overflow: ellipsis; }')
    o.append('.charsheet .sheet-skills > div:not(.sheet-dots):not(.sheet-spec-row):not(.sheet-section-header):not(.sheet-subheader):not(.sheet-subsubheader) { overflow: hidden !important; padding-right: 2px !important; min-width: 0; }')
    return '\n'.join(o) + '\n'


def relocate(h):
    """Move the Powers & Gear and Details pages into Main's middle tabs; drop their top-level tab buttons."""
    i = h.index('    <div class="page details">'); j = h.index('<!-- POWERS & GEAR', i)
    det = h[i:j]; dl = re.search(r'<datalist id="merit-list">.*?</datalist>', det, re.S)
    dl = dl.group(0) if dl else ''
    det = det.replace(dl, '')
    k = h.index('<!-- FORMS (Werewolf', j)
    pw = h[j:k]
    h = h[:i] + dl + '\n    ' + h[k:]
    def inner(pg, hdr):
        a = pg.index('<div class="leon-page">') + len('<div class="leon-page">')
        a = pg.index('</div>', pg.index(hdr, a)) + 6
        b = pg.rstrip().rfind('</div>'); b = pg.rstrip()[:b].rstrip().rfind('</div>')
        return pg[a:b]
    det_in = inner(det, 'class="section-header"'); pw_in = inner(pw, 'class="section-header"')
    e = pw_in.index('<div class="entry-section equipment">')
    powers, gear = pw_in[:e], pw_in[e:]
    panes = (f'\n<div class="midpane mp-powers"><div class="leon-page leon-pane">{powers}</div></div>'
             f'\n<div class="midpane mp-gear"><div class="leon-page leon-pane">{gear}</div></div>'
             f'\n<div class="midpane mp-notes"><div class="leon-page leon-pane">{det_in}</div></div>\n')
    a = h.index('<div class="midtabs">')
    c = h.index('<!-- !mortal2-organization !geist2-geist !geist2-organization -->', a)
    c = h.index('</div>', c) + 6       # end of the empty game-line div
    c = h.index('</div>', c)           # closing tag of the middle grow div
    h = h[:c] + panes + h[c:]
    for btn in ('act_page_powers', 'act_page_details'):
        h = re.sub(r'\s*<button type="action" class="toggle page-(?:powers|details)"[^>]*name="' + btn + r'"[^>]*>.*?</button>', '', h, count=1, flags=re.S)
    old = 'const TABS = ["settings", "1", "scars-variations", "conditions", "powers", "forms", "details"];'
    assert old in h
    h = h.replace(old, 'const TABS = ["settings", "1", "scars-variations", "conditions", "forms"];', 1)
    return h

MIG_JS = r"""
        /* ===== one-time, non-destructive migration: old top-level tabs + base-sheet duplicate power lists ===== */
        on("sheet:opened", () => getAttrs(["pagenumber", "last_page"], (v) => {
            const map = {powers: "powers", details: "notes"}; const u = {};
            if (map[v.pagenumber]) { u.pagenumber = "1"; u.mid_tab = map[v.pagenumber]; }
            if (map[v.last_page]) u.last_page = "1";
            if (Object.keys(u).length) setAttrs(u, {silent: true});
        }));
        const DD_SRC = {werewolf2: [["power-list", "power-list", null, "gifts", {gtype: "Shadow"}], ["ability2", "ability2_name", "ability2", "gifts", {gtype: "Moon"}],
                                    ["power2-list", "power2-list", null, "gifts", {gtype: "Wolf"}], ["power3", "power3_name", null, "writes", {}],
                                    ["abilities", "ability_name", "ability", "RENOWN", {}]],
                        vampire2:  [["abilities", "ability_name", "ability", "disciplines", {}]]};
        const ddList = (secs, cb, acc) => { acc = acc || {}; if (!secs.length) return cb(acc); const s = secs[0];
            getSectionIDs(`repeating_${s}`, (ids) => { acc[s] = ids; ddList(secs.slice(1), cb, acc); }); };
        on("sheet:opened change:sheettype", () => getAttrs(["sheettype", "dedupe_v1_werewolf2", "dedupe_v1_vampire2", "renown_purity", "renown_glory", "renown_honor", "renown_wisdom", "renown_cunning"], (g) => {
            const st = g.sheettype; const plan = DD_SRC[st]; if (!plan || g[`dedupe_v1_${st}`] === "1") return;
            const srcs = [...new Set(plan.map(p => p[0]))], tgts = [...new Set(plan.map(p => p[3]).filter(t => t !== "RENOWN"))];
            ddList(srcs.concat(tgts), (ids) => {
                const keys = [];
                plan.forEach(([sec, nm, rt]) => ids[sec].forEach((id) => { keys.push(`repeating_${sec}_${id}_${nm}`); if (rt) keys.push(`repeating_${sec}_${id}_${rt}`); }));
                tgts.forEach((t) => ids[t].forEach((id) => keys.push(`repeating_${t}_${id}_name`)));
                getAttrs(keys, (v) => {
                    const u = {[`dedupe_v1_${st}`]: "1"}; const have = {};
                    tgts.forEach((t) => { have[t] = new Set(ids[t].map((id) => (v[`repeating_${t}_${id}_name`] || "").trim().toLowerCase())); });
                    let n = 0;
                    plan.forEach(([sec, nm, rt, tgt, extra]) => ids[sec].forEach((id) => {
                        const name = (v[`repeating_${sec}_${id}_${nm}`] || "").trim(); const r = rt ? (parseInt(v[`repeating_${sec}_${id}_${rt}`]) || 0) : 0;
                        if (!name && !r) return;
                        if (tgt === "RENOWN") { const k = "renown_" + name.toLowerCase();
                            if (k in g) { if (!(parseInt(g[k]) || 0) && r) u[k] = r; return; }
                            tgt = "gifts"; extra = {gtype: "Other", notes: "Migrated from the old Renown list"}; }
                        if (!name || have[tgt].has(name.toLowerCase())) return;
                        have[tgt].add(name.toLowerCase());
                        const nid = generateRowID(); const p = `repeating_${tgt}_${nid}_`;
                        u[p + "name"] = name; if (r) { u[p + "rating"] = r; u[p + "rating_dots"] = "\u25CF".repeat(r); }
                        u[p + "show"] = "0"; Object.entries(extra).forEach(([k, x]) => { u[p + k] = x; }); n++;
                    }));
                    if (n) u.dedupe_v1_note = `Moved ${n} entr${n === 1 ? "y" : "ies"} from the old power lists (originals kept, hidden)`;
                    setAttrs(u, {silent: true});
                });
            });
        }));
"""
