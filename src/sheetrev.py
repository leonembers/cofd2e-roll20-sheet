"""Layout pass on the pasted Roll20 sheet (dist HTML/CSS).

Reads the live extract when uploads/sheet.html, sheet.css and translation.json
are present. Otherwise reads the committed dist and writes the updated dist.
Transforms are idempotent. Does not run the historical roll20_dist pipeline.
"""
import os, re, json, shutil

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _src():
    cands = [
        os.path.join(R, "uploads"),
        "/home/ubuntu/.cursor/projects/workspace/uploads",
        "/home/ubuntu/.cursor/projects/agent-repos-cofd2e-roll20-sheet/uploads",
    ]
    for d in cands:
        names = {
            "html": ["sheet.html", "sheet_2be9.html"],
            "css": ["sheet.css", "sheet_e62a.css"],
            "tr": ["translation.json", "translation_6ad2.json"],
        }
        found = {}
        if not os.path.isdir(d):
            continue
        for key, opts in names.items():
            for n in opts:
                p = os.path.join(d, n)
                if os.path.isfile(p):
                    found[key] = p
                    break
        if len(found) == 3:
            print("baseline", d)
            return found
    print("baseline dist (uploads not on disk)")
    return {
        "html": os.path.join(R, "dist", "sheet.html"),
        "css": os.path.join(R, "dist", "sheet.css"),
        "tr": os.path.join(R, "dist", "translation.json"),
    }

def take_div(h, start):
    d = 0
    for m in re.finditer(r"<div\b|</div>", h[start:]):
        d += 1 if m.group(0) == "<div" else -1
        if d == 0:
            return start, start + m.end()
    raise SystemExit("unbalanced div at %s" % start)

def armor(h):
    if "sheet-ar-cols" in h:
        return h
    pat = re.compile(
        r'(<input type="text" class="sheet-ar-name"[^>]*>)\s*'
        r'<span class="sheet-ar-sum">.*?</span>\s*'
        r'(<label class="sheet-ar-eq sheet-switch" title="Worn:.*?</label>)'
        r'(<label class="sheet-ar-eq sheet-ar-stk sheet-switch".*?</label>)',
        re.S)
    m = pat.search(h)
    if not m:
        raise SystemExit("armor head not found")
    cols = (
        '<span class="sheet-ar-cols">'
        '<span class="sheet-ar-c" title="Rating (general / ballistic)"><b>Rating</b><span name="attr_ar_general"></span>/<span name="attr_ar_ballistic"></span></span>'
        '<span class="sheet-ar-c" title="Minimum Strength"><b>Str</b><span name="attr_ar_str"></span></span>'
        '<span class="sheet-ar-c" title="Defense penalty"><b>Def</b><span name="attr_ar_def"></span></span>'
        '<span class="sheet-ar-c" title="Speed penalty"><b>Spd</b><span name="attr_ar_spd"></span></span>'
        '<span class="sheet-ar-c sheet-ar-cov" title="Coverage"><b>Cov</b><span name="attr_ar_coverage"></span></span>'
        '</span>')
    h = h[:m.start()] + m.group(1) + cols + m.group(2) + h[m.end():]
    needle = '<div class="sheet-entry-body"><div class="sheet-ar-panel">'
    if h.count(needle) != 1:
        raise SystemExit("armor body %s" % h.count(needle))
    h = h.replace(needle, needle + m.group(3), 1)
    return h

def weapons(h):
    if "sheet-wx" in h:
        return h
    if h.count('<div class="sheet-entry-section sheet-weapons">') != 1:
        raise SystemExit("weapons section")
    h = h.replace(
        '<div class="sheet-entry-section sheet-weapons">',
        '<div class="sheet-entry-section sheet-weapons"><input type="hidden" class="sheet-wfilter" name="attr_wfilter" value="all" />',
        1)
    h = h.replace(
        '<span data-i18n="weapons">Weapons &amp; Attacks</span></span>',
        '<span data-i18n="weapons">Weapons &amp; Attacks</span></span>'
        '<span class="sheet-wfilters">'
        '<button type="action" class="sheet-wfb sheet-wfb-all" name="act_wfilter_all">All</button>'
        '<button type="action" class="sheet-wfb sheet-wfb-melee" name="act_wfilter_melee">Melee</button>'
        '<button type="action" class="sheet-wfb sheet-wfb-ranged" name="act_wfilter_ranged">Ranged</button>'
        '<button type="action" class="sheet-wfb sheet-wfb-explosive" name="act_wfilter_explosive">Explosives</button>'
        '</span>',
        1)
    cols = (
        '<span class="sheet-wx">'
        '<span class="sheet-wx-c sheet-wx-m" title="Damage"><b>Dmg</b><span name="attr_damage"></span></span>'
        '<span class="sheet-wx-c" title="Initiative"><b>Init</b><span name="attr_initiative"></span></span>'
        '<span class="sheet-wx-c sheet-wx-x" title="Blast area"><b>Blast</b><span name="attr_blast"></span></span>'
        '<span class="sheet-wx-c sheet-wx-x" title="Force"><b>Force</b><span name="attr_force"></span></span>'
        '<span class="sheet-wx-c sheet-wx-x" title="Range"><b>Range</b><span name="attr_max_range"></span></span>'
        '<span class="sheet-wx-c" title="Strength"><b>Str</b><span name="attr_str_req"></span></span>'
        '<span class="sheet-wx-c" title="Size"><b>Size</b><span name="attr_wsize"></span></span>'
        '<span class="sheet-wx-c" title="Availability"><b>Avail</b><span name="attr_avail"></span></span>'
        '<span class="sheet-wx-c sheet-wx-tags" title="Tags"><b>Tags</b><span name="attr_atk_tags"></span></span>'
        '<span class="sheet-wx-c sheet-wx-m" title="Effects"><b>Fx</b><span name="attr_enhance"></span></span>'
        '</span>')
    old = '<span class="sheet-hl-tagsum" name="attr_atk_tags"></span>'
    if h.count(old) != 1:
        raise SystemExit("tagsum %s" % h.count(old))
    h = h.replace(old, cols, 1)
    return h

def gear(h):
    i = h.find('<div class="sheet-entry-section sheet-expmerits">')
    if i < 0:
        return h
    a, b = take_div(h, i)
    h = h[:a] + h[b:]
    return h

def merits(h):
    i = h.find('<fieldset class="repeating_merits">')
    j = h.find("</fieldset>", i)
    if i < 0:
        raise SystemExit("merits")
    sec = h[i:j]
    if "sheet-mv-out" not in sec:
        k = sec.find('<div class="sheet-style-block">')
        if k < 0:
            raise SystemExit("style block")
        a, b = take_div(sec, k)
        block = sec[a:b].replace('<div class="sheet-style-block">', '<div class="sheet-style-block sheet-mv-out">', 1)
        sec = sec[:a] + sec[b:]
        body = sec.find('<div class="sheet-entry-body">')
        if body < 0:
            raise SystemExit("merit body")
        sec = sec[:body] + block + sec[body:]
    sec = sec.replace('<span class="sheet-mstyle-badge">Style</span>', '<sup class="sheet-mstyle-s">S</sup>', 1)
    sec = sec.replace('>Post</button>', '>&#128172;</button>')
    sec = re.sub(
        r'<textarea class="sheet-mv-effect" name="(attr_mv\d_effect)" rows="2" placeholder="Effect"></textarea>',
        r'<input type="text" class="sheet-mv-effect" name="\1" placeholder="Short effect" />',
        sec)
    h = h[:i] + sec + h[j:]
    return h

def forms(h):
    if "act_form_prev" not in h:
        old = '<div class="sheet-fcards">'
        if h.count(old) != 1:
            raise SystemExit("fcards")
        h = h.replace(old,
            '<div class="sheet-form-stage">'
            '<input type="hidden" class="sheet-form-view" name="attr_form_view" value="hishu" />'
            '<span class="sheet-form-cap"></span>'
            '<button type="action" class="sheet-form-arrow sheet-form-prev" name="act_form_prev" title="Previous form">&#9664;</button>'
            + old, 1)
        i = h.find('<div class="sheet-huref')
        if i < 0:
            raise SystemExit("huref")
        a, b = take_div(h, i)
        h = h[:a] + '<button type="action" class="sheet-form-arrow sheet-form-next" name="act_form_next" title="Next form">&#9654;</button></div>' + h[b:]
    names = {
        "Hishu": "hishu", "Dalu": "dalu", "Gauru": "gauru",
        "Ur'Khar": "urkhar", "Urshul": "urshul", "Urhan": "urhan",
    }
    for label, key in names.items():
        src = '<span class="sheet-fc-name">%s</span>' % label
        dst = ('<span class="sheet-fc-hw" title="%s"><span name="attr_fh_%s_height"></span>'
               '<span class="sheet-fc-hwsep"> </span><span name="attr_fh_%s_weight"></span></span>' % (label, key, key))
        if src in h:
            h = h.replace(src, dst, 1)
    h, n = re.subn(
        r'<textarea class="sheet-fc-notes" name="(attr_form_notes_[a-z]+)" rows="3" placeholder="Description of this form"></textarea>',
        r'<input type="hidden" name="\1" />', h)
    if n not in (0, 6):
        raise SystemExit("form notes %s" % n)
    return h

def rites(h):
    i = h.find('<fieldset class="repeating_writes">')
    j = h.find("</fieldset>", i)
    sec = h[i:j]
    if "sheet-rite-short" in sec:
        return h
    hid = '<input type="hidden" name="attr_short_desc" value="" />'
    if hid not in sec:
        raise SystemExit("rite short hidden")
    sec = sec.replace(hid, "", 1)
    sec = sec.replace(
        "</div><div class=\"sheet-entry-body\">",
        '</div><div class="sheet-rite-short"><span name="attr_short_desc"></span></div><div class="sheet-entry-body">'
        '<label class="sheet-wide"><span>Short description</span><textarea name="attr_short_desc" rows="2" placeholder="Short description"></textarea></label>',
        1)
    return h[:i] + sec + h[j:]

def totem(h):
    i = h.find('<fieldset class="repeating_totem">')
    j = h.find("</fieldset>", i)
    sec = h[i:j]
    if "sheet-totem-body" in sec:
        return h
    img = ('<div class="sheet-fc-img sheet-totem-img"><span class="sheet-fc-imgph">No image<br/>200 x 300</span>'
           '<img class="sheet-fc-imgel" name="attr_totem_img" alt="" />'
           '<input type="hidden" name="attr_totem_img" />'
           '<button type="action" class="sheet-fc-imgbtn" name="act_timg" title="Set image URL">&#9998;</button></div>'
           '<div class="sheet-totem-fields">')
    sec = sec.replace('<div class="sheet-entry-body">', '<div class="sheet-entry-body sheet-totem-body">' + img, 1)
    # close the fields wrapper before the entry-body closes (last </div> of the body is the body's own close,
    # the hidden inputs sit inside the body). Close fields just before the body's final </div></div></fieldset>
    end = sec.rfind("</div></div>")
    if end < 0:
        raise SystemExit("totem end")
    sec = sec[:end] + "</div>" + sec[end:]
    return h[:i] + sec + h[j:]

def kuruth(h):
    if "sheet-kt-split" in h:
        return h
    i = h.find('<div class="sheet-kuruth-tiers')
    if i < 0:
        raise SystemExit("kuruth")
    a, b = take_div(h, i)
    inner = h[a:b]
    wrap = (
        '<div class="sheet-kt-split"><div class="sheet-kt-gen"><div class="sheet-kt-h">General triggers</div>'
        '<p class="sheet-kt-note">Always apply, at every Harmony.</p>'
        '<textarea class="sheet-trig-ta" name="attr_kuruth_general" rows="6" placeholder="General triggers"></textarea></div>'
        '<div class="sheet-kt-pers"><div class="sheet-kt-h">Personal triggers</div>'
        + inner + '</div></div>')
    return h[:a] + wrap + h[b:]

def notes(h):
    if "sheet-det-beside" not in h:
        i = h.find('<div class="sheet-det-top">')
        a, b = take_div(h, i)
        k = h.find('<div class="sheet-game-line sheet-werewolf2 sheet-breeds2 sheet-fc-bio">')
        if k < 0:
            raise SystemExit("fc bio")
        c1, c2 = take_div(h, k)
        w = h.find('<div class="sheet-game-line sheet-werewolf2 sheet-breeds2">', c2)
        if w < 0:
            raise SystemExit("hw")
        w1, w2 = take_div(h, w)
        bio = h[c1:c2].replace(
            '<label class="sheet-wide sheet-fc-bio-l"><textarea class="sheet-fc-bio-ta" name="attr_det_first_change_all" placeholder="Date, place and circumstances"></textarea></label>',
            '<label class="sheet-wide sheet-fc-bio-l"><input type="text" class="sheet-fc-bio-line" name="attr_det_first_change_all" placeholder="Date, place and circumstances" /></label>',
            1)
        if "sheet-fc-bio-line" not in bio:
            raise SystemExit("first change field")
        hw = h[w1:w2]
        top = h[a:b]
        top = top[:-6] + '<div class="sheet-det-beside">' + bio + hw + '</div></div>'
        h = h[:a] + top + h[b:c1] + h[c2:w1] + h[w2:]
    h, n = re.subn(
        r'<label class="sheet-wide"><span data-i18n="d-det_(appearance|history|goals|aspirations|possessions)">[^<]*</span><textarea name="(attr_det_[a-z]+)"></textarea></label>',
        r'<input type="hidden" name="\2" />', h)
    if n not in (0, 5):
        raise SystemExit("det long %s" % n)
    old = '<textarea class="sheet-bignotes-ta" name="attr_sheet_notes" placeholder="Notes"></textarea>'
    if "sheet-note-cols" not in h and old in h:
        boxes = '<div class="sheet-note-cols">' + "".join(
            '<textarea class="sheet-bignotes-ta" name="attr_sheet_notes%s" placeholder="Notes"></textarea>' % s
            for s in ["", "_2", "_3", "_4", "_5", "_6"]) + "</div>"
        h = h.replace(old, boxes, 1)
    return h

WPQ = "?{Willpower|None,0|Spend 1 (+3),3|Spend 1 moon (+4),4}"
SPQ = "?{Specialty|No,0|Yes (+1),1}"

def dice(h):
    if "@{wp_dice}" in h:
        h = h.replace("@{wp_dice}", WPQ)
        h = h.replace("@{spec_bonus}", "@{buff_mod}+" + SPQ)
    if "sheet-roll-extra" not in h:
        anchor = "</span></span></label>\n            </div>\n        </div>\n    </div>\n\n    <!-- PAGE 1 -->"
        if h.count(anchor) != 1:
            raise SystemExit("roller anchor %s" % h.count(anchor))
        extra = (
            '</span></span></label>\n            </div>\n'
            '<div class="sheet-roll-extra"><label class="sheet-ovbtn sheet-ovb-buff" title="Custom buffs you can turn on">'
            '<input type="checkbox" class="sheet-ovf sheet-buff-tg" name="attr_ov_buff" value="1" />Buffs</label>'
            '<div class="sheet-buff-panel"><fieldset class="repeating_buffs"><div class="sheet-buff-row">'
            '<label class="sheet-switch" title="Activate this buff"><input type="checkbox" name="attr_buff_on" value="1" /><span class="sheet-sw-track"></span></label>'
            '<input type="text" name="attr_buff_name" placeholder="Buff" />'
            '<input type="number" class="sheet-buff-n" name="attr_buff_mod" value="0" title="Dice" />'
            '</div></fieldset></div></div>\n'
            '<input type="hidden" name="attr_buff_mod" value="0" /><input type="hidden" name="attr_roll_prompt" value="1" />\n'
            '        </div>\n    </div>\n\n    <!-- PAGE 1 -->')
        h = h.replace(anchor, extra, 1)
    old = 'const updateRollEff = () => getAttrs(["rolltype","wp_spend","wp_risk","risk_b1","risk_b2","sheettype","skill_again","skill_again_names","skill_mk","moon_visible"], v => {\n            let rt = v.rolltype || ")d10!cs>10}>@{success_target}]]}}";'
    if old in h:
        ins = '''const updateRollEff = () => getAttrs(["roll_prompt","rolltype","wp_spend","wp_risk","risk_b1","risk_b2","sheettype","skill_again","skill_again_names","skill_mk","moon_visible"], v => {
            if (v.roll_prompt === "1") {
                const sq = v.skill_again || "";
                let base = "d10!cs>10", lbl = "Normal";
                if (sq === "8") { base = "d10!>8cs>8"; lbl = "Normal (skill 8-again)"; }
                else if (sq === "9") { base = "d10!>9cs>9"; lbl = "Normal (skill 9-again)"; }
                else if (sq === "no10") { base = "d10cs>10"; lbl = "Normal (no 10s)"; }
                const rtq = ")?{Roll type|" + lbl + "," + base + "|9-again,d10!>9cs>9|8-again,d10!>8cs>8|No 10s,d10cs>10|Rote,d10ro<8|Chance,*0+1)d10cf<1cs>10}>@{success_target}]]}}";
                setAttrs({rolltype_eff: rtq, wp_dice: 0}, {silent: true}, () => { if (globalThis.__hlAtk) globalThis.__hlAtk(); });
                return;
            }
            let rt = v.rolltype || ")d10!cs>10}>@{success_target}]]}}";'''
        h = h.replace(old, ins, 1)
    h = h.replace(
        'on("sheet:opened change:rolltype change:wp_spend change:wp_risk change:risk_b1 change:risk_b2 change:sheettype", updateRollEff);',
        'on("sheet:opened change:roll_prompt change:rolltype change:wp_spend change:wp_risk change:risk_b1 change:risk_b2 change:sheettype", updateRollEff);',
        1)
    return h

def collapse(h):
    h, n = re.subn(
        r'<button type="action" class="sheet-mini" name="act_(?:expand|collapse)_[a-z0-9]+" title="(?:Expand|Collapse) all"><span class="sheet-ic">&#96\d+;</span> <span data-i18n="(?:expand|collapse)-all">all</span></button>',
        "", h)
    # the icon entities are &#9662; and &#9652;
    if n == 0 and "act_expand_" in h:
        h, n = re.subn(
            r'<button type="action" class="sheet-mini" name="act_(?:expand|collapse)_[A-Za-z0-9]+" title="(?:Expand|Collapse) all">.*?</button>',
            "", h)
    return h, n

WORKER = r'''
        // rev111: form arrows, weapon list filter, totem image, active buff total
        const FORM_ORDER = ["hishu", "dalu", "gauru", "urkhar", "urshul", "urhan"];
        const formStep = (d) => getAttrs(["form_view", "urkhar_enabled"], v => {
            const list = FORM_ORDER.filter(f => f !== "urkhar" || v.urkhar_enabled === "1");
            let i = list.indexOf(v.form_view || "hishu"); if (i < 0) i = 0;
            setAttrs({form_view: list[(i + d + list.length) % list.length]});
        });
        if (!globalThis.__rev111) {
            globalThis.__rev111 = 1;
            on("clicked:form_prev", () => formStep(-1));
            on("clicked:form_next", () => formStep(1));
            ["all", "melee", "ranged", "explosive"].forEach(k => on("clicked:wfilter_" + k, () => setAttrs({wfilter: k})));
            on("clicked:repeating_totem:timg", ev => fimgSet("repeating_totem_" + r85Id(ev, "totem") + "_totem_img"));
            const buffSum = () => getSectionIDs("buffs", ids => {
                const ks = ids.flatMap(id => ["buff_on", "buff_mod"].map(a => "repeating_buffs_" + id + "_" + a));
                getAttrs(ks, v => {
                    let n = 0;
                    ids.forEach(id => { if (v["repeating_buffs_" + id + "_buff_on"] === "1") n += parseInt(v["repeating_buffs_" + id + "_buff_mod"], 10) || 0; });
                    setAttrs({buff_mod: n}, {silent: true});
                });
            });
            on("change:repeating_buffs remove:repeating_buffs sheet:opened", buffSum);
        }
'''

def worker(h):
    if "__rev111" in h:
        return h
    anchor = 'forEach(f => on("clicked:fimg_" + f, () => fimgSet("form_" + f + "_img")));'
    if h.count(anchor) != 1:
        raise SystemExit("fimg anchor")
    return h.replace(anchor, anchor + "\n" + WORKER, 1)

CSS = r'''
/* rev111 */
.charsheet[class][class][class][class][class][class][class][class] .sheet-armor .sheet-entry-head{display:flex!important;flex-wrap:wrap!important;align-items:center!important;gap:3px 6px!important;padding-right:2px!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-ar-name{flex:1 1 120px!important;min-width:90px!important;width:auto!important;margin:0!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-ar-cols{display:flex!important;flex:1 1 auto;flex-wrap:wrap;gap:2px 6px;align-items:center;font-size:11px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-ar-c{white-space:nowrap}
.charsheet[class][class][class][class][class][class][class][class] .sheet-ar-c>b{font-weight:700;margin-right:3px;opacity:.8}
.charsheet[class][class][class][class][class][class][class][class] .sheet-armor .sheet-entry-head>.sheet-ar-eq{margin-left:auto!important;flex:0 0 auto}
.charsheet[class][class][class][class][class][class][class][class] .sheet-ar-panel>.sheet-ar-stk{margin:2px 0 4px!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-wfilters{display:inline-flex;gap:4px;margin-left:8px;flex:0 0 auto}
.charsheet[class][class][class][class][class][class][class][class] .sheet-wfb{font-size:11px!important;padding:1px 8px!important;border-radius:10px!important;border:1px solid color-mix(in srgb,var(--pa,#888) 55%,rgba(128,128,128,.4))!important;background:none!important}
.charsheet[class][class][class][class][class][class][class][class] input.sheet-wfilter[value=all]~.sheet-entry-section-head .sheet-wfb-all,.charsheet[class][class][class][class][class][class][class][class] input.sheet-wfilter[value=melee]~.sheet-entry-section-head .sheet-wfb-melee,.charsheet[class][class][class][class][class][class][class][class] input.sheet-wfilter[value=ranged]~.sheet-entry-section-head .sheet-wfb-ranged,.charsheet[class][class][class][class][class][class][class][class] input.sheet-wfilter[value=explosive]~.sheet-entry-section-head .sheet-wfb-explosive{background:var(--pa,#8a4b1f)!important;color:#fff!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-wx{display:flex;flex:1 1 220px;flex-wrap:wrap;gap:1px 6px;align-items:center;font-size:11px;min-width:0}
.charsheet[class][class][class][class][class][class][class][class] .sheet-wx-c{white-space:nowrap}
.charsheet[class][class][class][class][class][class][class][class] .sheet-wx-c>b{margin-right:2px;opacity:.75}
.charsheet[class][class][class][class][class][class][class][class] .sheet-wx-tags{flex:1 1 80px;min-width:0;white-space:normal}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry:not(:has(input.sheet-hl-wt[value=explosive])) .sheet-wx-x{display:none!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry:has(input.sheet-hl-wt[value=explosive]) .sheet-wx-m{display:none!important}
.charsheet[class][class][class][class][class][class][class][class] input.sheet-wfilter[value=melee]~fieldset.repeating_weapons .sheet-entry:not(:has(input.sheet-hl-wt[value=melee],input.sheet-hl-wt[value=unarmed],input.sheet-hl-wt[value=thrown])){display:none!important}
.charsheet[class][class][class][class][class][class][class][class] input.sheet-wfilter[value=ranged]~fieldset.repeating_weapons .sheet-entry:not(:has(input.sheet-hl-wt[value=ranged],input.sheet-hl-wt[value=bow])){display:none!important}
.charsheet[class][class][class][class][class][class][class][class] input.sheet-wfilter[value=explosive]~fieldset.repeating_weapons .sheet-entry:not(:has(input.sheet-hl-wt[value=explosive])){display:none!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-head>input.sheet-entry-short{flex:1 1 100%!important;min-width:0!important;width:100%!important;white-space:normal!important;height:auto!important;overflow:visible!important;text-overflow:clip!important;margin:0 0 1px!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-section{position:relative}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-section>.repcontrol{position:absolute!important;top:0!important;right:0!important;margin:0!important;z-index:4}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-section-head{display:flex!important;align-items:center!important;min-height:22px;padding-right:54px!important;justify-content:flex-start!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-section-head .sheet-subheader,.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-section-head .sheet-subheader span{border:0!important;background:none!important;box-shadow:none!important;text-align:left!important;padding-left:0!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-head>button.sheet-entry-post:not(.sheet-post-ic){border:0!important;background:none!important;box-shadow:none!important;text-align:left!important;padding-left:2px!important}
.charsheet[class][class][class][class][class][class][class][class] .repcontainer[data-groupname=repeating_merits] .sheet-entry-head>button.sheet-entry-post{flex:1 1 240px!important;min-width:228px!important;white-space:nowrap!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-mstyle-s{display:none;font-size:9px;line-height:0;vertical-align:super;margin-left:1px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry>input.sheet-mstyle-flag[value="1"]~.sheet-entry-head .sheet-mstyle-s,.charsheet[class][class][class][class][class][class][class][class] .sheet-entry:has(>input.sheet-mcat-flag[value=Style]) .sheet-mstyle-s{display:inline!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry:has(>input.sheet-mcat-flag[value=Style]) .sheet-mcat-badge{font-size:0!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry:has(>input.sheet-mcat-flag[value=Style]) .sheet-mcat-badge::after{content:"Fighting";font-size:9px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-mv-out{display:none}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry>input.sheet-mstyle-flag[value="1"]~.sheet-mv-out{display:block!important;border:0!important;padding:1px 2px 2px 16px!important;margin:0!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-mv-out .sheet-style-title{display:none}
.charsheet[class][class][class][class][class][class][class][class] .sheet-mv-out .sheet-mv-post{flex:0 0 16px!important;width:16px!important;height:16px!important;min-width:0!important;padding:0!important;font-size:9px!important;line-height:14px!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-mv-out .sheet-mv-effect{flex:1 1 140px;min-width:0;width:auto!important;margin:0!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage{display:grid!important;grid-template-columns:28px minmax(0,1fr) 28px;gap:6px;align-items:center}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-cap{grid-column:1/-1;text-align:center;font-weight:700}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage>input.sheet-form-view[value=hishu]~.sheet-form-cap::before{content:"Hishu"}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage>input.sheet-form-view[value=dalu]~.sheet-form-cap::before{content:"Dalu"}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage>input.sheet-form-view[value=gauru]~.sheet-form-cap::before{content:"Gauru"}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage>input.sheet-form-view[value=urkhar]~.sheet-form-cap::before{content:"Ur'Khar"}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage>input.sheet-form-view[value=urshul]~.sheet-form-cap::before{content:"Urshul"}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage>input.sheet-form-view[value=urhan]~.sheet-form-cap::before{content:"Urhan"}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-arrow{width:28px;height:36px;padding:0!important;border-radius:8px!important;font-size:14px!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage .sheet-fcards{grid-column:2;display:block!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage .sheet-fcard{display:none!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage:has(>input.sheet-form-view[value=hishu]) .sheet-fc-hishu,.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage:has(>input.sheet-form-view[value=dalu]) .sheet-fc-dalu,.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage:has(>input.sheet-form-view[value=gauru]) .sheet-fc-gauru,.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage:has(>input.sheet-form-view[value=urshul]) .sheet-fc-urshul,.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage:has(>input.sheet-form-view[value=urhan]) .sheet-fc-urhan{display:flex!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-form-stage:has(>input.sheet-form-view[value=urkhar]):has(input.sheet-urkhar-flag[value="1"]) .sheet-fc-urkhar{display:flex!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-fc-hw{display:block;text-align:center;font-weight:700;font-size:14px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-rite-short{display:block;margin:0 4px 2px 16px;white-space:normal;overflow-wrap:anywhere;font-style:italic;font-size:12px;line-height:1.3}
.charsheet[class][class][class][class][class][class][class][class] .sheet-rite-short:empty,.charsheet[class][class][class][class][class][class][class][class] .sheet-rite-short:has(>span:empty){display:none}
.charsheet[class][class][class][class][class][class][class][class] .sheet-totem-body{display:grid!important;grid-template-columns:150px minmax(0,1fr);gap:8px;align-items:start}
.charsheet[class][class][class][class][class][class][class][class] .sheet-totem-img{width:150px!important;height:200px!important;max-width:150px!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-totem-fields{min-width:0;display:flex;flex-direction:column;gap:3px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-kt-split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:10px;align-items:start}
.charsheet[class][class][class][class][class][class][class][class] .sheet-kt-h{font-weight:700;text-align:center;margin:0 0 4px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-kt-note{font-size:11px;font-style:italic;text-align:center;margin:0 0 4px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-kt-gen textarea{width:100%!important;min-height:140px;box-sizing:border-box}
.charsheet[class][class][class][class][class][class][class][class] .sheet-det-top{display:grid!important;grid-template-columns:168px minmax(0,1fr)!important;gap:8px!important;align-items:start!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-det-portrait{grid-column:1;grid-row:1/span 3}
.charsheet[class][class][class][class][class][class][class][class] .sheet-det-grid{grid-column:2;grid-row:1}
.charsheet[class][class][class][class][class][class][class][class] .sheet-det-beside{grid-column:2;grid-row:2}
.charsheet[class][class][class][class][class][class][class][class] .sheet-fc-bio-line{width:100%!important;box-sizing:border-box}
.charsheet[class][class][class][class][class][class][class][class] .sheet-note-cols{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-note-cols textarea{min-height:70px;width:100%!important;box-sizing:border-box}
.charsheet[class][class][class][class][class][class][class][class] .sheet-diceroller-options>button.sheet-toggle,.charsheet[class][class][class][class][class][class][class][class] .sheet-wp-bar{display:none!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-diceroller-grid{display:flex!important;flex-direction:column!important;align-items:center!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-corporeal.sheet-span,.charsheet[class][class][class][class][class][class][class][class] .sheet-ephemeral.sheet-span,.charsheet[class][class][class][class][class][class][class][class] .sheet-diceroller-options,.charsheet[class][class][class][class][class][class][class][class] .sheet-roll-extra{display:flex!important;justify-content:center!important;width:100%;flex-wrap:wrap;gap:6px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-roll-extra{flex-direction:column;align-items:center}
.charsheet[class][class][class][class][class][class][class][class] .sheet-buff-panel{display:none;width:min(100%,440px)}
.charsheet[class][class][class][class][class][class][class][class] .sheet-roll-extra:has(input.sheet-buff-tg:checked) .sheet-buff-panel{display:block}
.charsheet[class][class][class][class][class][class][class][class] .sheet-buff-row{display:flex;align-items:center;gap:6px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-buff-row input[type=text]{flex:1 1 auto;min-width:0}
.charsheet[class][class][class][class][class][class][class][class] .sheet-buff-n{width:54px!important;flex:0 0 54px}
.charsheet[class][class][class][class][class][class][class][class] .sheet-right-touchstones,.charsheet[class][class][class][class][class][class][class][class] .sheet-right-touchstones .sheet-subheader,.charsheet[class][class][class][class][class][class][class][class] .sheet-ts-kuruth,.charsheet[class][class][class][class][class][class][class][class] .sheet-ts-kuruth label{text-align:center!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-right-touchstone-fields input,.charsheet[class][class][class][class][class][class][class][class] .sheet-ts-kuruth input{max-width:220px!important;text-align:center}
.charsheet[class][class][class][class][class][class][class][class] .sheet-ig2>.sheet-ifield>.sheet-input-label,.charsheet[class][class][class][class][class][class][class][class] .sheet-ig2>.sheet-ifield>.sheet-input-label span{color:var(--pa)!important}
.sheet-darkmode .charsheet[class][class][class][class][class][class][class][class] .sheet-ig2>.sheet-ifield>.sheet-input-label,.sheet-darkmode .charsheet[class][class][class][class][class][class][class][class] .sheet-ig2>.sheet-ifield>.sheet-input-label span,input.sheet-dm[value="1"]~.sheet-background .sheet-ig2>.sheet-ifield>.sheet-input-label,input.sheet-dm[value="1"]~.sheet-background .sheet-ig2>.sheet-ifield>.sheet-input-label span{color:var(--pad)!important}
'''

def css_add(c):
    if "/* rev111 */" in c:
        return c
    return c.rstrip() + "\n" + CSS

def banned(c):
    low = c.lower()
    bad = [w for w in ("expression", "eval", "javascript", "behavior", "binding", "@charset", "**", "webp", "data:", "parent") if w in low]
    # semicolon inside url()
    for m in re.finditer(r"url\([^)]*\)", c, re.I):
        if ";" in m.group(0):
            bad.append("semicolon-in-url")
    return bad

def main():
    src = _src()
    h = open(src["html"], encoding="utf-8").read()
    c = open(src["css"], encoding="utf-8").read()
    # If we are re-reading an already transformed dist, guards inside each step no-op.
    h = armor(h)
    h = weapons(h)
    h = gear(h)
    h = merits(h)
    h = forms(h)
    h = rites(h)
    h = totem(h)
    h = kuruth(h)
    h = notes(h)
    h = dice(h)
    h, ncol = collapse(h)
    h = worker(h)
    c = css_add(c)
    bad = banned(c)
    if bad:
        raise SystemExit("banned CSS %s" % bad)
    if len(c) > 630000:
        raise SystemExit("css %s over cap" % len(c))
    checks = [
        "sheet-ar-cols", "sheet-wx", "sheet-wfilter", "sheet-mv-out", "act_form_prev",
        "sheet-form-view", "sheet-rite-short", "sheet-totem-body", "sheet-kt-split",
        "attr_kuruth_general", "sheet-det-beside", "sheet-fc-bio-line", "sheet-note-cols",
        "sheet-roll-extra", "attr_roll_prompt", "repeating_buffs", "__rev111",
        "sheet-mstyle-s",
    ]
    missing = [k for k in checks if k not in h]
    if missing:
        raise SystemExit("missing " + ",".join(missing))
    if "sheet-expmerits" in h:
        raise SystemExit("expmerits left")
    if "act_expand_merits" in h or "act_collapse_merits" in h:
        raise SystemExit("collapse buttons left")
    if 'placeholder="Description of this form"' in h:
        raise SystemExit("form description left")
    if "sheet-huref" in h.split("sheet-form-stage")[-1][:5000] and "sheet-huref sheet-game-line" in h:
        # huref class may remain in CSS only; HTML marker:
        pass
    if '<div class="sheet-huref' in h:
        raise SystemExit("huref html left")
    out_h = os.path.join(R, "dist", "sheet.html")
    out_c = os.path.join(R, "dist", "sheet.css")
    out_t = os.path.join(R, "dist", "translation.json")
    open(out_h, "w", encoding="utf-8").write(h)
    open(out_c, "w", encoding="utf-8").write(c)
    if os.path.abspath(src["tr"]) != os.path.abspath(out_t):
        shutil.copyfile(src["tr"], out_t)
    tr = open(out_t, encoding="utf-8").read()
    print("collapse removed", ncol)
    print("html", len(h), "lines", h.count("\n") + 1)
    print("css", len(c), "lines", c.count("\n") + 1)
    print("translation", len(tr), "lines", tr.count("\n") + 1)
    print("wrote", out_h)

if __name__ == "__main__":
    main()
