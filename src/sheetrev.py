"""Layout pass on the pasted Roll20 sheet (dist HTML/CSS).

Reads the live extract when uploads/sheet.html, sheet.css and translation.json
are present. Otherwise reads the committed dist and writes the updated dist.
Transforms are idempotent. Does not run the historical roll20_dist pipeline.
"""
import os, re, json, shutil

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _pick(files, exact):
    for f in files:
        if os.path.basename(f) == exact:
            return f
    return files[-1]

def _src():
    import glob
    cands = [
        os.path.join(R, "uploads"),
        "/home/ubuntu/.cursor/projects/agent-repos-cofd2e-roll20-sheet/uploads",
        "/home/ubuntu/.cursor/projects/workspace/uploads",
    ]
    for d in cands:
        if not os.path.isdir(d):
            continue
        htmls = sorted(glob.glob(os.path.join(d, "sheet*.html")))
        csss = sorted(glob.glob(os.path.join(d, "sheet*.css")))
        trs = sorted(glob.glob(os.path.join(d, "translation*.json")))
        if htmls and csss and trs:
            found = {"html": _pick(htmls, "sheet.html"), "css": _pick(csss, "sheet.css"), "tr": _pick(trs, "translation.json")}
            print("baseline", found["html"])
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
    pool = '<button type="action" class="sheet-hl-poolbtn sheet-was-roll"  title="Roll attack (pool shown; damage is added on successes)" name="act_rr-attack"><span class="sheet-entry-pool sheet-hl-pool" name="attr_atk_short"></span></button>'
    if h.count(pool) != 1:
        raise SystemExit("pool btn %s" % h.count(pool))
    h = h.replace(pool, "", 1)
    name_end = '</span></button>\n\n<span class="sheet-wx">'
    if h.count(name_end) != 1:
        raise SystemExit("weapon name %s" % h.count(name_end))
    h = h.replace(name_end, '</span></button><span class="sheet-hl-pool" name="attr_atk_short"></span>\n\n<span class="sheet-wx">', 1)
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
    sec = sec.replace('<span class="sheet-mstyle-badge">Style</span>', '', 1)
    name_end = '<span class="sheet-entry-ph">(<span data-i18n="new-entry">new entry</span>)</span></button>'
    if sec.count(name_end) < 1:
        raise SystemExit("merit name button")
    sec = sec.replace(name_end, name_end.replace('</button>', '<sup class="sheet-mstyle-s">S</sup></button>'), 1)
    sec = sec.replace('>Post</button>', '>&#128172;</button>')
    sec = re.sub(
        r'<textarea class="sheet-mv-effect" name="(attr_mv\d_effect)" rows="2" placeholder="Effect"></textarea>',
        r'<input type="text" class="sheet-mv-effect" name="\1" placeholder="Short effect" />',
        sec)
    h = h[:i] + sec + h[j:]
    return h

def forms(h):
    if "act_form_prev" not in h:
        # Live sheet already stores form_view (hidden, plus a preview <select>). Drop only the dropdown.
        h, nprev = re.subn(
            r'<label>Preview form<select name="attr_form_view" title="Select a form to inspect without shapeshifting">.*?</select></label>',
            '', h, count=1, flags=re.S)
        old = '<div class="sheet-fcards">'
        if h.count(old) != 1:
            raise SystemExit("fcards")
        # Do not add a second form_view input when the card list already has one.
        extra = '' if 'name="attr_form_view"' in h else '<input type="hidden" class="sheet-form-view" name="attr_form_view" value="hishu" />'
        h = h.replace(old,
            '<div class="sheet-form-stage">'
            + extra +
            '<button type="action" class="sheet-form-arrow sheet-form-prev" name="act_form_prev" title="Previous form">&#9664;</button>'
            + old, 1)
        i = h.find('<div class="sheet-huref')
        if i < 0:
            raise SystemExit("huref")
        a, b = take_div(h, i)
        h = h[:a] + '<button type="action" class="sheet-form-arrow sheet-form-next" name="act_form_next" title="Next form">&#9654;</button></div>' + h[b:]
        if nprev not in (0, 1):
            raise SystemExit("preview %s" % nprev)
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
    h = h.replace(">No image<br/>200 x 300<", ">No image<br/>100 x 300<")
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
    img = ('<div class="sheet-totem-card"><div class="sheet-fc-img sheet-totem-img"><span class="sheet-fc-imgph">No image<br/>200 x 300</span>'
           '<img class="sheet-fc-imgel" name="attr_totem_img" alt="" />'
           '<input type="hidden" name="attr_totem_img" />'
           '<button type="action" class="sheet-fc-imgbtn" name="act_timg" title="Set image URL">&#9998;</button></div></div>')
    needle = '</div><div class="sheet-entry-body">'
    if needle not in sec:
        raise SystemExit("totem head")
    sec = sec.replace(needle, '</div>' + img + '<div class="sheet-entry-body sheet-totem-body">', 1)
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
        if "form-hw" not in hw or len(hw) > 12000:
            raise SystemExit("hw block %s" % len(hw))
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

def dice(h):
    # Keep @{wp_dice} and @{spec_bonus} as numbers inside [[ ]]. A ?{...} whose
    # label contains parentheses, or whose value contains ">", is substituted only
    # after Roll20 has already tokenised the group roll, so the resolved
    # [[{((pool)d10!cs>10}>target]] is invalid and the message is dropped.
    oldp = "@{cond_mod}+@{spec_bonus}"
    newp = "@{cond_mod}+@{buff_mod}+@{spec_bonus}"
    if oldp in h:
        h = h.replace(oldp, newp)
    if "sheet-roll-extra" not in h:
        anchor = "</span></span></label>\n            </div>\n        </div>\n    </div>\n\n    <!-- PAGE 1 -->"
        if h.count(anchor) != 1:
            raise SystemExit("roller anchor %s" % h.count(anchor))
        extra = (
            '</span></span></label>'
            '<label class="sheet-ovbtn sheet-ovb-buff" title="Custom buffs you can turn on">'
            '<input type="checkbox" class="sheet-ovf sheet-buff-tg" name="attr_ov_buff" value="1" />Buffs</label>\n'
            '            </div>\n'
            '<div class="sheet-roll-extra"><div class="sheet-buff-panel"><fieldset class="repeating_buffs"><div class="sheet-buff-row">'
            '<label class="sheet-switch" title="Activate this buff"><input type="checkbox" name="attr_buff_on" value="1" /><span class="sheet-sw-track"></span></label>'
            '<input type="text" name="attr_buff_name" placeholder="Buff" />'
            '<input type="number" class="sheet-buff-n" name="attr_buff_mod" value="0" title="Dice" />'
            '</div></fieldset></div></div>\n'
            '<input type="hidden" name="attr_buff_mod" value="0" /><input type="hidden" name="attr_roll_prompt" value="1" />\n'
            '        </div>\n    </div>\n\n    <!-- PAGE 1 -->')
        h = h.replace(anchor, extra, 1)
    if "const rrAsk" not in h:
        needle = 'const rrRun1 = (mac, isRe, slot) => startRoll(mac + (isRe ? "" : ` {{reroll=[Reroll](~@{character_id}|rrs${slot})}}`), (r) => {'
        if h.count(needle) != 1:
            raise SystemExit("rrRun1 %s" % h.count(needle))
        h = h.replace(needle, RR_ASK + needle.replace(
            "startRoll(mac + (isRe ? \"\" :",
            "rrAsk(mac, isRe, (m, note) => startRoll(m + (note || \"\") + (isRe ? \"\" :",
            1), 1)
        end = "finishRoll(r.rollId); if (!isRe && R.roll) riskWp(R.roll.result || 0);\n        });\n        Object.keys(RR_MAC)"
        if h.count(end) != 1:
            raise SystemExit("rrRun1 end %s" % h.count(end))
        h = h.replace(end, end.replace("});\n        Object.keys(RR_MAC)", "}));\n        Object.keys(RR_MAC)"), 1)
    return h

# Prompts are a silent startRoll of integer queries only (no ">" and no
# parentheses). The real roll is built afterwards and contains no ?{roll type}
# and no ?{Willpower}. Order: Roll type, Modifier, Willpower, Specialty, then
# weapon Target Defense when that roll has one.
RR_ASK = r'''const rrAsk = (mac, isRe, go) => {
            if (isRe || mac.indexOf("{{roll=") < 0) return go(mac, "");
            const needRt = /@\{(?:rolltype_eff|rolltype|atk_rt|repeating_[\w-]+_atk_rt)\}/.test(mac);
            const needWp = mac.indexOf("@{wp_dice}") >= 0;
            const needSp = mac.indexOf("@{spec_bonus}") >= 0;
            const needWsp = mac.indexOf("?{Specialty applies?|No,0|Yes,1}") >= 0;
            const needMd = mac.indexOf("?{@{modifiermacro}|0}") >= 0;
            const needDf = /\?\{@\{(?:repeating_[\w-]+_)?atk_defq\}\|@\{(?:repeating_[\w-]+_)?atk_def_default\}\}/.test(mac);
            if (!needRt && !needWp && !needSp && !needWsp && !needMd && !needDf) return go(mac, "");
            let q = "!{{template:default}}";
            if (needRt) q += "{{rt=![[?{Roll type|Normal,0|9-again,1|8-again,2|No 10s,3|Rote,4|Chance,5}]]}}";
            if (needMd) q += "{{md=![[?{@{modifiermacro}|0}]]}}";
            if (needWp) q += "{{wp=![[?{Willpower|None,0|Spend 1,3}]]}}";
            if (needSp) q += "{{sp=![[?{Specialty|No,0|Yes,1}]]}}";
            else if (needWsp) q += "{{sp=![[?{Specialty applies?|No,0|Yes,1}]]}}";
            if (needDf) q += "{{df=![[?{@{atk_defq}|@{atk_def_default}}]]}}";
            startRoll(q, (res) => {
                if (res && res.rollId && typeof finishRoll === "function") finishRoll(res.rollId);
                const R = (res && res.results) || {};
                const num = (k) => { const o = R[k]; if (!o) return 0; const n = parseInt(o.result, 10); return isNaN(n) ? 0 : n; };
                const rt = needRt ? num("rt") : 0, wp = needWp ? num("wp") : 0, sp = (needSp || needWsp) ? num("sp") : 0, md = needMd ? num("md") : 0, df = needDf ? num("df") : 0;
                const RTB = {1: ")d10!>9cs>9}>@{success_target}]]}} {{9again=1}}", 2: ")d10!>8cs>8}>@{success_target}]]}} {{8again=1}}", 3: ")d10cs>10}>@{success_target}]]}}", 4: ")d10ro<@{rote_reroll}}>@{success_target}]]}}", 5: "*0+1)d10cf<1}>10]]}} {{chance=1}}"};
                let m = mac;
                if (needWp) m = m.split("@{wp_dice}").join(String(wp));
                if (needSp) m = m.split("@{spec_bonus}").join(String(sp));
                if (needWsp) m = m.split("?{Specialty applies?|No,0|Yes,1}").join(String(sp));
                if (needMd) m = m.split("?{@{modifiermacro}|0}").join(String(md));
                if (needDf) m = m.replace(/\?\{@\{(?:repeating_[\w-]+_)?atk_defq\}\|@\{(?:repeating_[\w-]+_)?atk_def_default\}\}/g, String(df));
                if (rt && RTB[rt]) m = m.split("@{rolltype_eff}").join(RTB[rt]).split("@{rolltype}").join(RTB[rt]).replace(/@\{(?:repeating_[\w-]+_)?atk_rt\}/g, RTB[rt]);
                const done = (note) => go(m, note || "");
                if (wp < 1) return done("");
                getAttrs(["willpower", "willpower_cur"], (v) => {
                    const cur = Math.max(0, parseInt(v.willpower_cur, 10) || 0), max = parseInt(v.willpower, 10) || 0;
                    if (cur <= 0) return startRoll("&{template:cofd-entry} {{charname=@{character_name}}} {{kind=Willpower}} {{name=No Willpower left}} {{f_short=WP 0/" + max + ". Regain Willpower first.}}", (r) => finishRoll(r.rollId));
                    setAttrs({willpower_cur: cur - 1}, {}, () => done(" {{wpst=Spent 1 Willpower (+3). Left: WP " + (cur - 1) + "/" + max + "}}"));
                });
            });
        };
        on("clicked:roll_bp_flesh", () => rrRun("&{template:cofd-entry} {{charname=@{character_name}}} {{gl_@{game_line}=1}} {{splat=@{game_line}}} {{kind=Breaking Point}} {{name=Flesh Breaking Point}} {{f_pool=Resolve @{resolve_eff} + Composure @{composure_eff}}} {{roll=[[{((@{resolve}+@{resolve_boost}+@{composure}+@{composure_boost}+?{@{modifiermacro}|0}+@{wound_penalty}+@{wp_dice}+@{cond_mod}+@{buff_mod}+@{spec_bonus})@{rolltype_eff}", false));
        on("clicked:roll_bp_spirit", () => rrRun("&{template:cofd-entry} {{charname=@{character_name}}} {{gl_@{game_line}=1}} {{splat=@{game_line}}} {{kind=Breaking Point}} {{name=Spirit Breaking Point}} {{f_pool=Resolve @{resolve_eff} + Composure @{composure_eff}}} {{roll=[[{((@{resolve}+@{resolve_boost}+@{composure}+@{composure_boost}+?{@{modifiermacro}|0}+@{wound_penalty}+@{wp_dice}+@{cond_mod}+@{buff_mod}+@{spec_bonus})@{rolltype_eff}", false));
        '''

def dice_layout(h):
    if "sheet-roll-break" in h:
        return h
    needle = '<div class="sheet-diceroller-options">'
    if h.count(needle) != 1:
        raise SystemExit("roller options %s" % h.count(needle))
    return h.replace(needle, '<div class="sheet-roll-break"></div>' + needle, 1)

def breaking(h):
    if "roll_bp_flesh" in h:
        return h
    anchor = '<button type="action" class="sheet-dot sheet-zero" name="act_morality-0">&#215;</button>\n                            </div>'
    if h.count(anchor) != 1:
        raise SystemExit("morality clear %s" % h.count(anchor))
    btns = (
        '<div class="sheet-bp-rolls sheet-game-line sheet-werewolf sheet-werewolf2">'
        '<button type="action" class="sheet-quick sheet-bp" name="act_roll_bp_flesh" title="Flesh breaking point: Resolve + Composure. The modifier prompt is the Harmony modifier.">Flesh Breaking Point</button>'
        '<button type="action" class="sheet-quick sheet-bp" name="act_roll_bp_spirit" title="Spirit breaking point: Resolve + Composure. The modifier prompt is the Harmony modifier.">Spirit Breaking Point</button>'
        '</div>'
    )
    return h.replace(anchor, anchor + btns, 1)

def maneuvers(h):
    if "sheet-mv-full" in h:
        return h
    for n in range(1, 6):
        old = '<input type="text" class="sheet-mv-effect" name="attr_mv%d_effect" placeholder="Short effect" />' % n
        if h.count(old) != 1:
            raise SystemExit("mv effect %s %s" % (n, h.count(old)))
        h = h.replace(old, old + '<textarea class="sheet-mv-full" name="attr_mv%d_desc" rows="3" placeholder="Full description"></textarea>' % n, 1)
        bit = '{{f_description=@{mv%d_effect}}}' % n
        if h.count(bit) != 1:
            raise SystemExit("mv post %s" % n)
        h = h.replace(bit, bit + ' {{f_full=@{mv%d_desc}}}' % n, 1)
    return h

def roll_above(h):
    i = h.find('<fieldset class="repeating_merits">')
    j = h.find("</fieldset>", i)
    sec = h[i:j]
    req = '<label class="sheet-wide sheet-m-nrl" title="Off: the Merit posts without dice and its pool fields are hidden">'
    a = sec.find(req)
    if a < 0:
        raise SystemExit("merit requires")
    b = sec.find("</label>", a) + len("</label>")
    lab = sec[a:b]
    eff = '<label class="sheet-wide sheet-m-nrl" title="On: separate Dramatic Failure'
    e = sec.find(eff)
    if e < 0:
        raise SystemExit("merit outcomes")
    if not lab.strip().endswith("</label>") or "Requires roll" not in lab:
        raise SystemExit("merit requires label")
    if e != b and "Requires roll" not in sec[e-len(lab):e]:
        sec = sec[:a] + sec[b:e] + lab + sec[e:]
        h = h[:i] + sec + h[j:]
    pat = re.compile(
        r'(<label class="sheet-gfn" title="Off: one static effect[^"]*">.*?</label>)'
        r'(<label class="sheet-gfn" title="Off: the Facet posts its card without rolling dice">.*?</label>)',
        re.S)
    h, n = pat.subn(r'\2<div class="sheet-gfx-br"></div>\1', h)
    if n not in (0, 10):
        raise SystemExit("gift swap %s" % n)
    return h

def vamp_quick(h):
    pat = re.compile(
        r'(<div class="sheet-quick-actions sheet-game-line sheet-vampire2">)\s*'
        r'<button type="action" class="sheet-quick sheet-rage sheet-was-roll"[^>]*name="act_rr_frenzy">.*?</button>\s*'
        r'<button type="action" class="sheet-quick" name="act_spend_vitae"[^>]*>.*?</button>\s*',
        re.S)
    h, n = pat.subn(r"\1", h, count=1)
    if n not in (0, 1):
        raise SystemExit("vamp quick %s" % n)
    if 'name="act_spend_vitae"' in h:
        raise SystemExit("vitae button left")
    return h

def disciplines(h):
    i = h.find('<fieldset class="repeating_disciplines">')
    j = h.find("</fieldset>", i)
    if i < 0:
        raise SystemExit("disciplines")
    sec = h[i:j]
    if "sheet-disc-on" not in sec:
        needle = '</div>\n<span class="sheet-entry-pool" name="attr_pool"></span>'
        if sec.count(needle) != 1:
            raise SystemExit("disc pool %s" % sec.count(needle))
        tog = ('<label class="sheet-switch sheet-disc-on" title="Active effect. Vigor adds to Strength (and Speed). Celerity adds to Defense and Speed. Resilience adds to Stamina and Health.">'
               '<input type="checkbox" name="attr_disc_active" value="1" /><span class="sheet-sw-track"></span></label>'
               '<input type="hidden" name="attr_disc_on_mig" value="" />')
        sec = sec.replace(needle, "</div>" + tog + '\n<span class="sheet-entry-pool" name="attr_pool"></span>', 1)
        sec = sec.replace('<div class="sheet-entry">', '<div class="sheet-entry sheet-disc-card">', 1)
        h = h[:i] + sec + h[j:]
    if 'name="attr_disc_vigor"' not in h:
        old = '<input type="hidden" name="attr_disc_celerity" value="0" />'
        if h.count(old) != 1:
            raise SystemExit("disc_celerity input %s" % h.count(old))
        h = h.replace(old, old + '<input type="hidden" name="attr_disc_vigor" value="0" />', 1)
    speed = 'value="@{species_factor}+@{speed_base}+@{speed_penalty}+@{fleet_of_foot}+@{form_speed_extra}+@{form_size}"'
    if "@{disc_vigor}" not in h and speed in h:
        h = h.replace(speed, speed[:-1] + '+@{disc_vigor}+@{disc_celerity}"', 1)
    old_dots = '''const discDots = (cb) => getSectionIDs("repeating_disciplines", ids => getAttrs(["sheettype", ...ids.flatMap(i => [`repeating_disciplines_${i}_name`, `repeating_disciplines_${i}_rating`])], v => {
            const d = {vigor: 0, celerity: 0, resilience: 0, cruac: 0, theban: 0};
            ids.forEach(i => { const nm = (v[`repeating_disciplines_${i}_name`] || "").toLowerCase(), r = parseInt(v[`repeating_disciplines_${i}_rating`], 10) || 0;
                for (const k of Object.keys(d)) if (nm.indexOf(k === "vigor" ? "vigo" : k) >= 0) d[k] = Math.max(d[k], r); });
            cb(v.sheettype, d);
        }));'''
    new_dots = '''const discDots = (cb) => getSectionIDs("repeating_disciplines", ids => getAttrs(["sheettype", ...ids.flatMap(i => [`repeating_disciplines_${i}_name`, `repeating_disciplines_${i}_rating`, `repeating_disciplines_${i}_disc_active`, `repeating_disciplines_${i}_disc_on_mig`])], v => {
            const d = {vigor: 0, celerity: 0, resilience: 0, cruac: 0, theban: 0};
            const mig = {};
            ids.forEach(i => {
                const p = `repeating_disciplines_${i}_`;
                const nm = (v[p + "name"] || "").toLowerCase(), r = parseInt(v[p + "rating"], 10) || 0;
                const physical = nm.indexOf("vigo") >= 0 || nm.indexOf("celerity") >= 0 || nm.indexOf("resilien") >= 0;
                mig[p + "disc_has_effect"] = physical ? "1" : "0";
                let on = v[p + "disc_active"];
                if (v[p + "disc_on_mig"] !== "1") {
                    mig[p + "disc_on_mig"] = "1";
                    if (physical && on !== "0") { mig[p + "disc_active"] = "1"; on = "1"; }
                }
                for (const k of Object.keys(d)) {
                    if (nm.indexOf(k === "vigor" ? "vigo" : k) < 0) continue;
                    if ((k === "vigor" || k === "celerity" || k === "resilience") && on !== "1") continue;
                    d[k] = Math.max(d[k], r);
                }
            });
            const finish = () => cb(v.sheettype, d);
            if (Object.keys(mig).length) setAttrs(mig, {silent: true}, finish); else finish();
        }));'''
    if old_dots in h:
        h = h.replace(old_dots, new_dots, 1)
    elif "disc_on_mig" not in h[h.find("const discDots"):h.find("const discDots") + 900]:
        raise SystemExit("discDots missing")
    clear = 'setAttrs({disc_vamp: "0", strength_boost: 0, stamina_boost: 0, disc_celerity: 0, strength_vb: "", stamina_vb: "", defense_vb: ""});'
    clear2 = 'setAttrs({disc_vamp: "0", strength_boost: 0, stamina_boost: 0, disc_celerity: 0, disc_vigor: 0, strength_vb: "", stamina_vb: "", defense_vb: ""});'
    if clear in h:
        h = h.replace(clear, clear2, 1)
    apply = 'setAttrs({disc_vamp: "1", strength_boost: d.vigor, stamina_boost: d.resilience, disc_celerity: d.celerity,'
    apply2 = 'setAttrs({disc_vamp: "1", strength_boost: d.vigor, stamina_boost: d.resilience, disc_celerity: d.celerity, disc_vigor: d.vigor,'
    if apply in h:
        h = h.replace(apply, apply2, 1)
    calc = 'const CALC_IN = ["strength","dexterity","stamina","stamina_boost","strength_boost","disc_celerity","wits","composure","resolve","athletics","base_size","giant","small_framed","form_size","species_factor","speed_'
    if '"disc_vigor"' not in h and calc in h:
        h = h.replace(calc, calc.replace('"disc_celerity"', '"disc_celerity","disc_vigor"'), 1)
    spd = 'const spd = n("species_factor") + n("speed_base") + n("speed_penalty") + n("fleet_of_foot") + n("form_speed_extra") + n("form_size");'
    spd2 = 'const spd = n("species_factor") + n("speed_base") + n("speed_penalty") + n("fleet_of_foot") + n("form_speed_extra") + n("form_size") + n("disc_vigor") + n("disc_celerity");'
    if spd in h:
        h = h.replace(spd, spd2, 1)
    fmt = 'u.speed_calc = fmt("Speed", [["Str + Dex", n("speed_base"), 1], ["Species", n("species_factor"), 1], ["Armor", n("speed_penalty")], ["Fleet of Foot", n("fleet_of_foot")], [fl + " form", n("form_speed_extra") + n("form_size")]], spd);'
    fmt2 = 'u.speed_calc = fmt("Speed", [["Str + Dex", n("speed_base"), 1], ["Species", n("species_factor"), 1], ["Armor", n("speed_penalty")], ["Fleet of Foot", n("fleet_of_foot")], [fl + " form", n("form_speed_extra") + n("form_size")], ["Vigor", n("disc_vigor")], ["Celerity", n("disc_celerity")]], spd);'
    if fmt in h:
        h = h.replace(fmt, fmt2, 1)
    return disc_row(h)

def disc_row(h):
    i = h.find('<fieldset class="repeating_disciplines">')
    j = h.find("</fieldset>", i)
    sec = h[i:j]
    if "sheet-disc-name" in sec:
        return h
    m = re.search(
        r'<button type="roll" class="sheet-entry-post" name="roll_post" title="Post to chat" value="([^"]*)">'
        r'<span class="sheet-entry-name" name="attr_name"></span>'
        r'<span class="sheet-entry-ph">\(<span data-i18n="new-entry">new entry</span>\)</span></button>',
        sec)
    if not m:
        raise SystemExit("disc name button")
    name = ('<span class="sheet-disc-name"><span class="sheet-entry-name" name="attr_name"></span>'
            '<span class="sheet-entry-ph">(<span data-i18n="new-entry">new entry</span>)</span></span>')
    sec = sec[:m.start()] + name + sec[m.end():]
    icon = ('<button type="roll" class="sheet-entry-post sheet-post-ic sheet-disc-post" name="roll_post" title="Post to chat" value="%s">&#128172;</button>'
            % m.group(1))
    if sec.count('<span class="sheet-amenu">') != 1:
        raise SystemExit("disc menu")
    sec = sec.replace('<span class="sheet-amenu">', icon + '<span class="sheet-amenu">', 1)
    sec = sec.replace('<div class="sheet-entry-head">', '<div class="sheet-entry-head sheet-disc-row">', 1)
    return disc_flat(h[:i] + sec + h[j:])

def disc_flat(h):
    i = h.find('<fieldset class="repeating_disciplines">')
    j = h.find("</fieldset>", i)
    sec = h[i:j]
    if "sheet-disc-flat" in sec:
        return h
    marker = '<div class="sheet-entry-head sheet-disc-row">'
    a = sec.find(marker)
    if a < 0:
        raise SystemExit("disc head")
    a2, b = take_div(sec, a)
    inner = sec[sec.find(">", a) + 1:b - 6]
    if "sheet-disc-has" not in inner:
        inner = inner.replace(
            '<label class="sheet-switch sheet-disc-on"',
            '<input type="hidden" class="sheet-disc-has" name="attr_disc_has_effect" value="0" /><label class="sheet-switch sheet-disc-on"',
            1)
    sec = sec[:a] + inner + sec[b:]
    sec = sec.replace('class="sheet-entry sheet-disc-card"', 'class="sheet-entry sheet-disc-card sheet-disc-flat"', 1)
    return disc_line(h[:i] + sec + h[j:])

def disc_line(h):
    i = h.find('<fieldset class="repeating_disciplines">')
    j = h.find("</fieldset>", i)
    sec = h[i:j]
    if '<div class="sheet-disc-row">' in sec:
        return h
    caret = '<input type="checkbox" class="sheet-entry-toggle sheet-entry-settings" name="attr_show" value="1" title="Show / hide entry settings" aria-label="Show / hide entry settings" />'
    if caret not in sec:
        raise SystemExit("disc caret")
    body = '<div class="sheet-entry-body">'
    b = sec.find(body)
    c = sec.find(caret)
    if b < 0 or c < 0 or c > b:
        raise SystemExit("disc line bounds")
    mid = sec[c + len(caret):b]
    pool = re.search(r'<span class="sheet-entry-pool" name="attr_pool"></span>', mid)
    cost = re.search(r'<span class="sheet-entry-cost" name="attr_cost_disp" title="Cost"></span>', mid)
    if pool and cost:
        mid = mid.replace(pool.group(0), '', 1).replace(cost.group(0), '', 1)
        at = mid.find('</span></span>')
        if at < 0:
            raise SystemExit("disc name end")
        at += len('</span></span>')
        mid = mid[:at] + pool.group(0) + cost.group(0) + mid[at:]
        ce = mid.find(cost.group(0)) + len(cost.group(0))
        ns = mid.find('<span class="sheet-disc-name">')
        if ns >= 0 and ce > ns:
            mid = mid[:ns] + '<span class="sheet-disc-id">' + mid[ns:ce] + '</span>' + mid[ce:]
    cog = '<input type="checkbox" class="sheet-entry-settings sheet-disc-cog" name="attr_show" value="1" title="Show / hide entry settings" aria-label="Show / hide entry settings" />'
    hidden = '<input type="checkbox" class="sheet-disc-caret" name="attr_show" value="1" />'
    row = '<div class="sheet-disc-row">' + cog + mid.strip() + '</div>'
    sec = sec[:c] + hidden + row + sec[b:]
    return h[:i] + sec + h[j:]

def notes_fit(h):
    for name in ("attr_det_hair", "attr_det_dob", "attr_det_race", "attr_det_nationality"):
        old = '<textarea class="sheet-det-ta" rows="1" name="%s"></textarea>' % name
        if old in h:
            h = h.replace(old, '<input type="text" name="%s" />' % name, 1)
    marker = '<div class="sheet-game-line sheet-vampire2 sheet-det-splat">'
    if marker not in h:
        return h
    top = h.find('<div class="sheet-det-top">')
    a, b = take_div(h, top)
    vi = h.find(marker)
    if a < vi < b:
        return h
    v1, v2 = take_div(h, vi)
    block = h[v1:v2]
    h = h[:v1] + h[v2:]
    top = h.find('<div class="sheet-det-top">')
    a, b = take_div(h, top)
    return h[:b - 6] + block + h[b - 6:]

def weapons_fix(h):
    old = '<fieldset class="repeating_weapons">\n<div class="sheet-entry">'
    if "sheet-wtype-f" not in h:
        if old not in h:
            raise SystemExit("weapon row")
        h = h.replace(old, '<fieldset class="repeating_weapons">\n<input type="hidden" class="sheet-wtype-f" name="attr_wtype" value="melee" />\n<div class="sheet-entry">', 1)
    if "sheet-whide" not in h:
        needle = '<input type="hidden" class="sheet-wtype-f" name="attr_wtype" value="melee" />\n'
        if h.count(needle) != 1:
            raise SystemExit("wtype flag %s" % h.count(needle))
        h = h.replace(needle, needle + '<input type="hidden" class="sheet-whide" name="attr_whide" value="0" />\n', 1)
    return h

TOTEM_CARD = (
    '<div class="sheet-totem-card"><div class="sheet-totem-top">'
    '<div class="sheet-fc-img sheet-totem-img"><span class="sheet-fc-imgph">No image<br/>110 x 160</span>'
    '<img class="sheet-fc-imgel" name="attr_totem_img" alt="" />'
    '<input type="hidden" name="attr_totem_img" />'
    '<button type="action" class="sheet-fc-imgbtn" name="act_timg" title="Set image URL">&#9998;</button></div>'
    '<div class="sheet-totem-stats">'
    '<span><b>Power</b><span name="attr_totem_power"></span></span>'
    '<span><b>Finesse</b><span name="attr_totem_finesse"></span></span>'
    '<span><b>Resistance</b><span name="attr_totem_resistance"></span></span>'
    '<span><b>Willpower</b><span name="attr_totem_willpower"></span></span>'
    '<span><b>Essence</b><span name="attr_totem_essence"></span></span>'
    '<span><b>Initiative</b><span name="attr_totem_initiative"></span></span>'
    '<span><b>Defense</b><span name="attr_totem_defense"></span></span>'
    '<span><b>Speed</b><span name="attr_totem_speed"></span></span>'
    '<span><b>Size</b><span name="attr_totem_size"></span></span>'
    '<span><b>Corpus</b><span name="attr_totem_corpus"></span></span>'
    '</div></div><div class="sheet-totem-more">'
    '<div><b>Influences</b> <span name="attr_totem_influences"></span></div>'
    '<div><b>Numina</b> <span name="attr_totem_numina"></span></div>'
    '<div><b>Ban</b> <span name="attr_totem_ban"></span></div>'
    '<div><b>Bane</b> <span name="attr_totem_bane"></span></div>'
    '<div><b>Bonuses</b> <span name="attr_bonuses"></span></div>'
    '<div><b>Notes</b> <span name="attr_totem_legacy"></span></div>'
    '</div></div>'
)

TOTEM_BODY = (
    '<label class="sheet-wide"><span data-i18n="name">Name</span><input type="text" name="attr_name" /></label>'
    '<div class="sheet-totem-nums">'
    '<label>Power<input type="number" name="attr_totem_power" value="0" /></label>'
    '<label>Finesse<input type="number" name="attr_totem_finesse" value="0" /></label>'
    '<label>Resistance<input type="number" name="attr_totem_resistance" value="0" /></label>'
    '<label>Willpower<input type="number" name="attr_totem_willpower" value="0" /></label>'
    '<label>Essence<input type="number" name="attr_totem_essence" value="0" /></label>'
    '<label>Initiative<input type="number" name="attr_totem_initiative" value="0" /></label>'
    '<label>Defense<input type="number" name="attr_totem_defense" value="0" /></label>'
    '<label>Speed<input type="number" name="attr_totem_speed" value="0" /></label>'
    '<label>Size<input type="number" name="attr_totem_size" value="0" /></label>'
    '<label>Corpus<input type="number" name="attr_totem_corpus" value="0" /></label>'
    '</div>'
    '<label class="sheet-wide"><span>Ban</span><input type="text" name="attr_totem_ban" /></label>'
    '<label class="sheet-wide"><span>Bane</span><input type="text" name="attr_totem_bane" /></label>'
    '<label class="sheet-wide"><span>Influences</span><textarea name="attr_totem_influences" rows="2"></textarea></label>'
    '<label class="sheet-wide"><span>Numina</span><textarea name="attr_totem_numina" rows="2"></textarea></label>'
    '<label class="sheet-wide"><span data-i18n="lbl-bonuses">Bonuses</span><textarea name="attr_bonuses" rows="2"></textarea></label>'
    '<label class="sheet-wide"><span>Notes</span><textarea name="attr_totem_legacy" rows="2" title="Kept text from the old combined fields"></textarea></label>'
    '<label><span data-i18n="lbl-aspiration">Aspiration</span><textarea name="attr_aspiration" rows="2" class="sheet-asp-ta" title="Aspiration"></textarea></label>'
    '<input type="hidden" name="attr_attributes" /><input type="hidden" name="attr_stats" />'
    '<input type="hidden" name="attr_influences" /><input type="hidden" name="attr_ban" />'
    '<input type="hidden" name="attr_totem_mig" value="0" />'
)

def totem_layout(h):
    i = h.find('<fieldset class="repeating_totem">')
    j = h.find("</fieldset>", i)
    sec = h[i:j]
    if "sheet-totem-stats" in sec:
        return h
    a = sec.find('<div class="sheet-totem-card">')
    b = sec.find('<div class="sheet-entry-body', a if a >= 0 else 0)
    if a < 0 or b < 0:
        raise SystemExit("totem card")
    sec = sec[:a] + TOTEM_CARD + sec[b:]
    old = (
        '<label class="sheet-wide"><span data-i18n="name">Name</span><input type="text" name="attr_name" /></label>\n'
        '<label><span data-i18n="lbl-attributes">Power / Finesse / Resistance</span><input type="text" name="attr_attributes" /></label>\n'
        '<label class="sheet-wide"><span data-i18n="lbl-stats">Willpower / Essence / Initiative / Defense / Speed / Size / Corpus</span><textarea name="attr_stats"></textarea></label>\n'
        '<label class="sheet-wide"><span data-i18n="lbl-influences">Influences / Numina</span><textarea name="attr_influences"></textarea></label>\n'
        '<label class="sheet-wide"><span data-i18n="lbl-bonuses">Bonuses</span><textarea name="attr_bonuses"></textarea></label>\n'
        '<label><span data-i18n="lbl-ban">Ban / Bane</span><input type="text" name="attr_ban" /></label>\n'
    )
    if old not in sec:
        raise SystemExit("totem fields")
    sec = sec.replace(old, TOTEM_BODY, 1)
    oldp = '{{f_attributes=@{attributes}}} {{f_stats=@{stats}}} {{f_influences=@{influences}}} {{f_bonuses=@{bonuses}}} {{f_ban=@{ban}}} {{f_aspiration=@{aspiration}}}'
    newp = '{{f_power=@{totem_power}}} {{f_finesse=@{totem_finesse}}} {{f_resistance=@{totem_resistance}}} {{f_willpower=@{totem_willpower}}} {{f_essence=@{totem_essence}}} {{f_initiative=@{totem_initiative}}} {{f_defense=@{totem_defense}}} {{f_speed=@{totem_speed}}} {{f_size=@{totem_size}}} {{f_corpus=@{totem_corpus}}} {{f_influences=@{totem_influences}}} {{f_numina=@{totem_numina}}} {{f_ban=@{totem_ban}}} {{f_bane=@{totem_bane}}} {{f_bonuses=@{bonuses}}} {{f_notes=@{totem_legacy}}} {{f_aspiration=@{aspiration}}} {{f_attributes=@{attributes}}} {{f_stats=@{stats}}}'
    if oldp not in sec:
        raise SystemExit("totem post")
    sec = sec.replace(oldp, newp, 1)
    return h[:i] + sec + h[j:]

REV112 = r'''
        // rev112: totem field migration (keeps the old combined text)
        const totemMig = () => getSectionIDs("totem", ids => {
            const keys = ["attributes","stats","influences","ban","bonuses","totem_legacy","totem_mig","totem_power","totem_finesse","totem_resistance","totem_willpower","totem_essence","totem_initiative","totem_defense","totem_speed","totem_size","totem_corpus","totem_ban","totem_bane","totem_influences","totem_numina"];
            getAttrs(ids.flatMap(id => keys.map(a => "repeating_totem_" + id + "_" + a)), v => {
                const u = {}, num = {power:"totem_power",finesse:"totem_finesse",resistance:"totem_resistance",willpower:"totem_willpower",essence:"totem_essence",initiative:"totem_initiative",defense:"totem_defense",speed:"totem_speed",size:"totem_size",corpus:"totem_corpus"};
                ids.forEach(id => {
                    const p = "repeating_totem_" + id + "_";
                    if (v[p + "totem_mig"] === "1") return;
                    const olds = ["attributes","stats","influences","ban","bonuses"].map(a => (v[p + a] || "").trim() ? (a + ": " + (v[p + a] || "").trim()) : "").filter(Boolean);
                    if (olds.length && !(v[p + "totem_legacy"] || "").trim()) u[p + "totem_legacy"] = olds.join("\n");
                    const src = [v[p + "stats"], v[p + "attributes"], v[p + "influences"], v[p + "ban"]].join(" ; ");
                    const re = /(power|finesse|resistance|willpower|essence|initiative|defense|speed|size|corpus)\s*[:=]?\s*(\d+)/ig;
                    let m, found = {};
                    while ((m = re.exec(src))) found[m[1].toLowerCase()] = m[2];
                    const trip = (v[p + "attributes"] || "").match(/^\s*(\d+)\s*[/|,]\s*(\d+)\s*[/|,]\s*(\d+)\s*$/);
                    if (trip) { found.power = found.power || trip[1]; found.finesse = found.finesse || trip[2]; found.resistance = found.resistance || trip[3]; }
                    Object.keys(num).forEach(k => { const cur = (v[p + num[k]] || "").trim(); if (found[k] && (cur === "" || cur === "0")) u[p + num[k]] = found[k]; });
                    const banSrc = (v[p + "ban"] || "") + "\n" + (v[p + "attributes"] || "");
                    const banM = banSrc.match(/ban\s*:\s*([^\n;]+)/i), baneM = banSrc.match(/bane\s*:\s*([^\n;]+)/i);
                    if (baneM && !(v[p + "totem_bane"] || "").trim()) u[p + "totem_bane"] = baneM[1].trim();
                    if (banM && !(v[p + "totem_ban"] || "").trim()) u[p + "totem_ban"] = banM[1].trim();
                    else if (!banM && !baneM && (v[p + "ban"] || "").trim() && !(v[p + "totem_ban"] || "").trim()) u[p + "totem_ban"] = (v[p + "ban"] || "").trim();
                    const inf = v[p + "influences"] || "";
                    const nm = inf.match(/numina\s*:\s*([\s\S]*)$/i), im = inf.match(/influences?\s*:\s*([\s\S]*?)(?=numina\s*:|$)/i);
                    if (inf.trim() && !(v[p + "totem_influences"] || "").trim()) u[p + "totem_influences"] = (im ? im[1] : inf).trim();
                    if (nm && !(v[p + "totem_numina"] || "").trim()) u[p + "totem_numina"] = nm[1].trim();
                    u[p + "totem_mig"] = "1";
                });
                if (Object.keys(u).length) setAttrs(u, {silent: true});
            });
        });
        const weaponHide = () => getAttrs(["wfilter"], fv => {
            const f = fv.wfilter || "all";
            getSectionIDs("weapons", ids => {
                getAttrs(ids.map(id => "repeating_weapons_" + id + "_wtype"), v => {
                    const u = {};
                    ids.forEach(id => {
                        const t = (v["repeating_weapons_" + id + "_wtype"] || "melee").toLowerCase();
                        let hide = "0";
                        if (f === "melee") hide = (t === "melee" || t === "unarmed" || t === "thrown") ? "0" : "1";
                        else if (f === "ranged") hide = (t === "ranged" || t === "bow") ? "0" : "1";
                        else if (f === "explosive") hide = t === "explosive" ? "0" : "1";
                        u["repeating_weapons_" + id + "_whide"] = hide;
                    });
                    setAttrs(u, {silent: true});
                });
            });
        });
        if (!globalThis.__rev112) {
            globalThis.__rev112 = 1;
            on("sheet:opened change:repeating_totem", totemMig);
            on("sheet:opened change:wfilter change:repeating_weapons:wtype remove:repeating_weapons", weaponHide);
        }
'''

def worker_extra(h):
    if "__rev112" in h:
        return h
    anchor = 'on("change:repeating_buffs remove:repeating_buffs sheet:opened", buffSum);'
    if h.count(anchor) != 1:
        raise SystemExit("buff anchor %s" % h.count(anchor))
    return h.replace(anchor, anchor + "\n" + REV112, 1)

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
.charsheet .sheet-armor .sheet-entry-head{display:flex!important;flex-wrap:wrap!important;align-items:center!important;gap:3px 6px!important;padding-right:2px!important}
.charsheet .sheet-ar-name{flex:1 1 120px!important;min-width:90px!important;width:auto!important;margin:0!important}
.charsheet .sheet-ar-cols{display:flex!important;flex:1 1 auto;flex-wrap:wrap;gap:2px 6px;align-items:center;font-size:11px}
.charsheet .sheet-ar-c{white-space:nowrap}
.charsheet .sheet-ar-c>b{font-weight:700;margin-right:3px;opacity:.8}
.charsheet .sheet-armor .sheet-entry-head>.sheet-ar-eq{margin-left:auto!important;flex:0 0 auto}
.charsheet .sheet-ar-panel>.sheet-ar-stk{margin:2px 0 4px!important}
.charsheet .sheet-wfilters{display:inline-flex;gap:4px;margin-left:8px;flex:0 0 auto}
.charsheet[class][class][class][class][class][class][class][class] .sheet-wfb{font-size:11px!important;padding:1px 8px!important;border-radius:10px!important;border:1px solid color-mix(in srgb,var(--pa,#888) 55%,rgba(128,128,128,.4))!important;background:none!important}
.charsheet input.sheet-wfilter[value=all]~.sheet-entry-section-head .sheet-wfb-all,.charsheet input.sheet-wfilter[value=melee]~.sheet-entry-section-head .sheet-wfb-melee,.charsheet input.sheet-wfilter[value=ranged]~.sheet-entry-section-head .sheet-wfb-ranged,.charsheet input.sheet-wfilter[value=explosive]~.sheet-entry-section-head .sheet-wfb-explosive{background:var(--pa,#8a4b1f)!important;color:#fff!important}
.charsheet .sheet-wx{display:flex;flex:1 1 220px;flex-wrap:wrap;gap:1px 6px;align-items:center;font-size:11px;min-width:0}
.charsheet .sheet-wx-c{white-space:nowrap}
.charsheet .sheet-wx-c>b{margin-right:2px;opacity:.75}
.charsheet .sheet-wx-tags{flex:1 1 80px;min-width:0;white-space:normal}
.charsheet .sheet-entry:not(:has(input.sheet-hl-wt[value=explosive])) .sheet-wx-x{display:none!important}
.charsheet .sheet-entry:has(input.sheet-hl-wt[value=explosive]) .sheet-wx-m{display:none!important}
.charsheet .repcontainer[data-groupname=repeating_weapons] input.sheet-whide[value="1"]~.sheet-entry{display:none!important}
.charsheet .sheet-weapons>.sheet-entry-section-head{flex-wrap:wrap!important;row-gap:2px;overflow:visible!important}
.charsheet .sheet-weapons .sheet-subheader{flex:1 0 100%!important;min-width:0!important;overflow:visible!important;text-overflow:clip!important}
.charsheet .sheet-weapons .sheet-subheader span{white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important}
.charsheet .sheet-wfilters{flex:1 1 auto!important;margin-left:0!important}
.charsheet .sheet-weapons .sheet-entry-head{flex-wrap:wrap!important}
.charsheet .sheet-weapons .sheet-wx{flex:1 0 100%!important;width:100%!important;justify-content:center!important;text-align:center!important}
.charsheet .sheet-weapons .sheet-wx-tags{flex:0 0 auto!important}
.charsheet .sheet-entry-head>input.sheet-entry-short{flex:1 1 100%!important;min-width:0!important;width:100%!important;white-space:normal!important;height:auto!important;overflow:visible!important;text-overflow:clip!important;margin:0 0 1px!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-section{position:relative}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-section>.repcontrol{position:absolute!important;top:0!important;right:0!important;margin:0!important;z-index:4}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-section-head{display:flex!important;align-items:center!important;min-height:22px;padding-right:54px!important;justify-content:flex-start}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-section-head .sheet-subheader,.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-section-head .sheet-subheader span{border:0!important;background:none!important;box-shadow:none!important;text-align:left;padding-left:0!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry-head>button.sheet-entry-post:not(.sheet-post-ic){border:0!important;background:none!important;box-shadow:none!important;text-align:left!important;padding-left:2px!important}
.charsheet .sheet-mstyle-s{display:none;font-size:9px;line-height:0;vertical-align:super;margin-left:1px}
.charsheet .sheet-entry>input.sheet-mstyle-flag[value="1"]~.sheet-entry-head .sheet-mstyle-s,.charsheet .sheet-entry:has(>input.sheet-mcat-flag[value=Style]) .sheet-mstyle-s{display:inline!important}
.charsheet .repcontainer[data-groupname=repeating_merits] .sheet-entry:has(>input.sheet-mstyle-flag[value="1"]) .sheet-mcat-badge,.charsheet .repcontainer[data-groupname=repeating_merits] .sheet-entry:has(>input.sheet-mcat-flag[value=Style]) .sheet-mcat-badge{display:none!important}
.charsheet[class][class][class][class][class][class][class][class] .repcontainer[data-groupname=repeating_merits] .sheet-entry-head{flex-wrap:wrap!important;padding-left:14px!important}
.charsheet[class][class][class][class][class][class][class][class] .repcontainer[data-groupname=repeating_merits] .sheet-entry-head>button.sheet-entry-post{flex:1 1 100%!important;width:auto!important;max-width:100%!important;min-width:0!important;overflow:visible!important;white-space:nowrap!important}
.charsheet[class][class][class][class][class][class][class][class] .repcontainer[data-groupname=repeating_merits] .sheet-entry-body>label.sheet-wide,.charsheet[class][class][class][class][class][class][class][class] .repcontainer[data-groupname=repeating_merits] .sheet-entry-body input[name=attr_short_desc]{flex:1 1 100%!important;width:100%!important;max-width:100%!important;box-sizing:border-box!important}
.charsheet .sheet-mv-out .sheet-mv-row{flex-wrap:wrap!important}
.charsheet .sheet-mv-out .sheet-mv-effect{flex:1 1 100%!important;width:100%!important;max-width:100%!important;display:block!important;box-sizing:border-box!important}
.charsheet .sheet-mv-out{display:none}
.charsheet .sheet-entry>input.sheet-mstyle-flag[value="1"]~.sheet-mv-out{display:block!important;border:0!important;padding:1px 2px 2px 16px!important;margin:0!important}
.charsheet .sheet-mv-out .sheet-style-title{display:none}
.charsheet .sheet-mv-out .sheet-mv-post{flex:0 0 16px!important;width:16px!important;height:16px!important;min-width:0!important;padding:0!important;font-size:9px!important;line-height:14px!important}
.charsheet .sheet-mv-full{display:block!important;flex:1 0 100%!important;width:100%!important;max-width:100%!important;box-sizing:border-box!important;min-height:44px;margin:0 0 3px!important}
.charsheet[class][class][class][class][class][class] .sheet-mp-forms,.charsheet[class][class][class][class][class][class] .sheet-mp-forms .sheet-leon-pane,.charsheet[class][class][class][class][class][class] .sheet-form-stage{overflow:visible!important}
.charsheet[class][class][class][class][class][class] .sheet-form-stage{display:grid!important;grid-template-columns:36px minmax(0,1fr) 36px!important;gap:4px!important;align-items:center!important;width:100%!important}
.charsheet[class][class][class][class][class][class] .sheet-form-prev{grid-column:1!important;grid-row:1!important}
.charsheet[class][class][class][class][class][class] .sheet-form-stage>.sheet-fcards{grid-column:2!important;grid-row:1!important;min-width:0!important}
.charsheet[class][class][class][class][class][class] .sheet-form-next{grid-column:3!important;grid-row:1!important}
.charsheet[class][class][class][class][class][class][class][class] button.sheet-form-arrow{display:inline-flex!important;opacity:1!important;visibility:visible!important;width:32px!important;height:48px!important;padding:0!important;border:1px solid #fff!important;background:var(--pa,#8a4b1f)!important;color:#fff!important;font-size:22px!important}
.charsheet[class][class][class][class][class][class] .sheet-mp-forms .sheet-fc-hw{display:flex!important;flex-direction:column!important;align-items:center!important;max-width:100%!important;overflow:hidden!important;text-align:center!important;font-size:12px!important;line-height:1.2!important;white-space:normal!important}
.charsheet[class][class][class][class][class][class] .sheet-mp-forms .sheet-fc-hwsep{display:none!important}
.charsheet[class][class][class][class][class][class] .sheet-mp-forms .sheet-fc-head{min-width:0!important;overflow:hidden!important;max-width:100%!important}
.charsheet .sheet-fc-hw{display:block;text-align:center;font-weight:700;font-size:14px}
.charsheet .sheet-rite-short{display:block;margin:0 4px 2px 16px;white-space:normal;overflow-wrap:anywhere;font-style:italic;font-size:12px;line-height:1.3}
.charsheet .sheet-rite-short:empty,.charsheet .sheet-rite-short:has(>span:empty){display:none}
.charsheet .sheet-totem>.sheet-entry-section-head{justify-content:center!important}
.charsheet .sheet-totem .sheet-subheader,.charsheet .sheet-totem .sheet-subheader span{text-align:center!important;width:100%}
.charsheet .sheet-totem-card{display:flex!important;flex-direction:column;align-items:stretch;gap:4px;margin:4px 0!important}
.charsheet .sheet-entry>input.sheet-entry-toggle:not(:checked)~.sheet-totem-card{display:flex!important}
.charsheet .sheet-totem-top{display:flex;gap:8px;align-items:center;min-width:0}
.charsheet .sheet-totem-img{position:relative!important;display:flex!important;width:110px!important;height:160px!important;max-width:110px!important;flex:0 0 110px;align-items:center;justify-content:center;overflow:hidden}
.charsheet .sheet-totem-img .sheet-fc-imgph{display:block!important}
.charsheet .sheet-totem-stats{flex:1 1 auto;display:grid;grid-template-columns:1fr 1fr;gap:1px 8px;align-content:center;font-size:11px;min-width:0}
.charsheet .sheet-totem-stats b{margin-right:4px}
.charsheet .sheet-totem-more{font-size:11px;line-height:1.3;min-width:0}
.charsheet .sheet-totem-more div{white-space:normal;overflow-wrap:anywhere}
.charsheet .sheet-totem-nums{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(72px,1fr))!important;gap:6px 8px!important;width:100%!important}
.charsheet .sheet-totem-nums>label{display:flex!important;flex-direction:column!important;min-width:0!important;width:auto!important;max-width:100%!important;margin:0!important;white-space:normal!important;overflow:hidden!important;font-size:9px!important;line-height:1.15!important;letter-spacing:0!important}
.charsheet .sheet-totem-nums input{width:100%!important;min-width:0!important;max-width:100%!important;box-sizing:border-box!important}
.charsheet .sheet-kt-split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:10px;align-items:start}
.charsheet .sheet-kt-h{font-weight:700;text-align:center;margin:0 0 4px}
.charsheet .sheet-kt-note{font-size:11px;font-style:italic;text-align:center;margin:0 0 4px}
.charsheet .sheet-kt-gen textarea{width:100%!important;min-height:140px;box-sizing:border-box}
.charsheet[class][class][class][class][class][class][class][class] .sheet-det-top{display:grid!important;grid-template-columns:200px minmax(0,1fr)!important;gap:12px!important;align-items:start!important;width:100%!important}
.charsheet[class][class] .sheet-det-portrait,.charsheet[class][class] .sheet-det-portrait img{width:200px!important;max-width:200px!important;box-sizing:border-box!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-det-portrait{grid-column:1;grid-row:1/span 3}
.charsheet[class][class][class][class][class][class][class][class] .sheet-det-grid{grid-column:2;grid-row:1}
.charsheet[class][class][class][class][class][class][class][class] .sheet-det-beside{grid-column:2;grid-row:2}
.charsheet .sheet-fc-bio-line{width:100%!important;box-sizing:border-box}
.charsheet .sheet-note-cols{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.charsheet .sheet-note-cols textarea{min-height:70px;width:100%!important;box-sizing:border-box}
.charsheet[class][class][class][class][class][class][class][class] .sheet-diceroller-options>button.sheet-toggle,.charsheet[class][class][class][class][class][class][class][class] .sheet-wp-bar{display:none!important}
.charsheet[class][class][class][class] .sheet-rollbar{padding:4px 8px!important}
.charsheet[class][class][class][class] .sheet-rollbar .sheet-diceroller-grid{display:flex!important;flex-flow:row wrap!important;align-items:center!important;justify-content:center!important;gap:4px 8px!important;width:100%!important}
.charsheet[class][class][class][class] .sheet-rollbar .sheet-corporeal.sheet-span{display:flex!important;flex:1 0 100%!important;justify-content:center!important;width:100%!important;order:1;gap:6px}
.charsheet[class][class][class][class] .sheet-rollbar .sheet-roll-portrait{order:0!important;width:64px!important;height:72px!important;flex:0 0 64px!important;align-self:center!important}
.charsheet[class][class][class][class] .sheet-rollbar .sheet-diceroller-grid>.sheet-rollcontainer{order:3;width:40px!important;height:40px!important;min-width:40px!important;flex:0 0 40px!important}
.charsheet[class][class][class][class] .sheet-rollbar .sheet-rolldisplay{order:4;flex:0 1 200px!important;width:200px!important;max-width:200px!important;height:24px!important}
.charsheet[class][class][class][class] .sheet-roll-break{order:5;flex:1 0 100%;height:0;width:100%;margin:0;padding:0;overflow:hidden}
.charsheet[class][class][class][class] .sheet-rollbar .sheet-diceroller-options{order:6;display:flex!important;flex:0 1 auto!important;justify-content:center!important;width:auto!important;border:0!important;background:none!important;gap:4px}
.charsheet[class][class][class][class] .sheet-roll-extra{order:7;display:flex!important;flex:1 0 100%!important;justify-content:center!important;width:100%!important}
.charsheet[class][class][class][class] .sheet-fc-bio,.charsheet[class][class][class][class] .sheet-fc-bio-l,.charsheet[class][class][class][class] .sheet-det-beside{min-width:0!important;max-width:100%!important}
.charsheet[class][class][class][class] input.sheet-fc-bio-line{width:100%!important;max-width:100%!important;min-width:0!important;box-sizing:border-box!important}
.charsheet .sheet-buff-panel{display:none;width:min(100%,440px)}
.charsheet .sheet-diceroller-grid:has(input.sheet-buff-tg:checked) .sheet-buff-panel{display:block}
.charsheet .sheet-buff-row{display:flex;align-items:center;gap:6px}
.charsheet .sheet-buff-row input[type=text]{flex:1 1 auto;min-width:0}
.charsheet .sheet-buff-n{width:54px!important;flex:0 0 54px}
.charsheet .sheet-right-touchstones,.charsheet .sheet-right-touchstones label,.charsheet .sheet-right-touchstones span,.charsheet .sheet-right-touchstones input,.charsheet .sheet-ts-kuruth,.charsheet .sheet-ts-kuruth label,.charsheet .sheet-ts-kuruth input{text-align:center!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-right-touchstone-fields label{align-items:center}
.charsheet .sheet-right-touchstone-fields input,.charsheet .sheet-ts-kuruth input{max-width:220px!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-ig2>.sheet-ifield>.sheet-input-label,.charsheet[class][class][class][class][class][class][class][class] .sheet-ig2>.sheet-ifield>.sheet-input-label span{color:var(--pa)!important}
.sheet-darkmode .charsheet[class][class][class][class][class][class][class][class] .sheet-ig2>.sheet-ifield>.sheet-input-label,.sheet-darkmode .charsheet[class][class][class][class][class][class][class][class] .sheet-ig2>.sheet-ifield>.sheet-input-label span,input.sheet-dm[value="1"]~.sheet-background .sheet-ig2>.sheet-ifield>.sheet-input-label,input.sheet-dm[value="1"]~.sheet-background .sheet-ig2>.sheet-ifield>.sheet-input-label span{color:var(--pad)!important}
.charsheet[class][class][class][class][class][class][class][class][class][class][class][class] .sheet-mp-forms .sheet-fcards .sheet-fc-img{width:100px!important;max-width:100px!important;height:300px!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-entry>input.sheet-entry-settings{border:0!important;outline:0!important;box-shadow:none!important;background:none!important}
.charsheet[class][class] .sheet-skills>div>button.sheet-spec-caret{order:2!important;flex:0 0 14px!important;width:14px!important;min-width:14px!important;height:14px!important;margin:0 2px!important;padding:0!important;border:0!important;background:none!important;box-shadow:none!important}
.charsheet[class][class] .sheet-skills>div>button.sheet-toggle{order:3!important}
.charsheet[class][class] .sheet-skills span.sheet-skm{order:1!important}
.charsheet[class][class] .sheet-skills button.sheet-spec-caret>span{font:12px/14px Arial,sans-serif!important}
.charsheet[class][class] .sheet-skills button.sheet-spec-caret>span::before{content:none!important;border:0!important;width:0!important;height:0!important;transform:none!important}
.charsheet .sheet-gfx-br{flex:1 0 100%;width:100%;height:0;margin:0;padding:0}
.charsheet[class][class] .sheet-disciplines .sheet-disc-card{position:relative!important;display:block!important;width:100%!important;box-sizing:border-box!important;border:1px solid rgba(139,16,16,.55);margin:3px 0}
.charsheet .sheet-disc-caret{position:absolute!important;width:0!important;height:0!important;opacity:0!important}
.charsheet .sheet-disc-card>.sheet-disc-caret:not(:checked)~.sheet-entry-body{display:none!important}
.charsheet .sheet-disc-row{display:flex!important;flex-wrap:nowrap!important;align-items:center!important;width:100%!important;min-width:0!important;gap:3px}
.charsheet[class][class][class][class] .sheet-disc-row>*{flex:0 0 auto!important;width:auto!important;min-width:0!important;display:inline-flex!important;float:none!important}
.charsheet[class][class][class][class] .sheet-disc-row>.sheet-disc-id{flex:1 1 auto!important;min-width:0!important;display:flex!important;flex-direction:column!important;overflow:hidden!important}
.charsheet .sheet-disc-id>.sheet-disc-name{overflow:hidden!important;white-space:nowrap!important;text-overflow:ellipsis!important}
.charsheet .sheet-disc-id .sheet-entry-pool,.charsheet .sheet-disc-id .sheet-entry-cost{font-size:10px!important;line-height:1.1}
.charsheet[class][class][class][class] .sheet-disc-row>.sheet-disc-cog{-webkit-appearance:none!important;appearance:none!important;position:relative!important;width:14px!important;height:14px!important;border:0!important;background:none!important;padding:0!important}
.charsheet[class][class][class][class][class][class][class][class] .sheet-disc-row>input.sheet-disc-has[value="0"]~label.sheet-disc-on{display:none!important}
.charsheet .sheet-disc-card .sheet-amenu>.sheet-amenu-list{left:auto!important;right:0!important}
.charsheet .sheet-bp-rolls{display:flex;flex-wrap:wrap;justify-content:center;gap:4px;max-width:100%;margin:4px 0}
.charsheet .sheet-bp{max-width:100%;white-space:normal;text-align:center;font-size:11px;line-height:1.2;padding:2px 8px}
.charsheet[class][class][class] .sheet-det-top>.sheet-det-grid.sheet-det-grid{display:grid!important;grid-template-columns:repeat(6,minmax(0,1fr))!important;width:100%!important;min-width:0!important;max-width:100%!important}
.charsheet[class][class] .sheet-det-top,.charsheet[class][class] .sheet-det-top>.sheet-det-grid,.charsheet[class][class] .sheet-det-grid>label{min-width:0!important;max-width:100%!important}
.charsheet[class][class] .sheet-det-grid>label.sheet-det-s,.charsheet[class][class] .sheet-det-grid>label.sheet-det-m,.charsheet[class][class] .sheet-det-grid>label.sheet-det-l{flex:none!important;min-width:0!important;max-width:none!important;width:auto!important}
.charsheet[class][class] .sheet-det-grid>label.sheet-det-m,.charsheet[class][class] .sheet-det-grid>label.sheet-det-l{grid-column:span 3}
.charsheet[class][class] .sheet-det-grid>label>span,.charsheet .sheet-det-splat label>span{white-space:normal!important}
.charsheet .sheet-det-top>.sheet-vampire2.sheet-det-splat{grid-column:2;grid-row:3;min-width:0;max-width:100%;display:flex;flex-wrap:wrap;gap:4px 8px}
.charsheet .sheet-det-top>.sheet-vampire2.sheet-det-splat>.sheet-subheader{flex:1 0 100%;text-align:center}
.charsheet .sheet-det-top>.sheet-vampire2.sheet-det-splat>label{flex:1 1 30%;min-width:0}
.charsheet .sheet-det-top>.sheet-vampire2.sheet-det-splat input{width:100%!important;min-width:0!important;box-sizing:border-box}
.charsheet[class][class] .sheet-det-portrait{grid-row:1 / span 4}
.charsheet[class][class][class][class][class][class][class][class][class][class][class][class] label.sheet-ovbtn,.charsheet[class][class][class][class][class][class][class][class][class][class][class][class] button.sheet-quick,.charsheet[class][class][class][class][class][class][class][class][class][class][class][class] button.sheet-wfb,.charsheet[class][class][class][class][class][class][class][class][class][class][class][class] button.sheet-bp{display:inline-flex!important;align-items:center!important;justify-content:center!important;margin:0!important;padding:3px 11px!important;min-height:23px!important;line-height:16px!important;box-sizing:border-box!important;border:1px solid color-mix(in srgb,var(--pad,var(--pa,#888)) 78%,rgba(0,0,0,0))!important;border-radius:10px!important;background:none!important;box-shadow:none!important}
.charsheet[class][class][class][class][class][class][class][class][class][class][class][class] .sheet-diceroller-options,.charsheet[class][class][class][class][class][class][class][class][class][class][class][class] .sheet-wfilters,.charsheet[class][class][class][class][class][class][class][class][class][class][class][class] .sheet-bp-rolls{display:flex!important;flex-wrap:wrap!important;justify-content:center!important;align-items:center!important;gap:8px!important;column-gap:8px!important;row-gap:8px!important;border:0!important;background:none!important}
.charsheet[class][class] .repcontainer[data-groupname=repeating_weapons] .sheet-entry-head>button.sheet-w-atk{flex:0 1 auto!important;width:auto!important}
.charsheet .sheet-weapons .sheet-hl-pool{flex:0 0 auto!important;margin:0 6px 0 4px!important;padding:0!important;border:0!important;background:none!important;white-space:nowrap!important;font-weight:400!important;pointer-events:none}
.charsheet .sheet-set-gear{position:absolute;left:2px;top:4px;width:13px;height:13px;margin:0;padding:0;line-height:13px;text-align:center;font:12px/13px Arial,sans-serif;color:var(--pad,var(--pa,#ccc));pointer-events:none;z-index:5}
.charsheet .sheet-disc-row{position:relative}
.charsheet .sheet-disc-row>.sheet-set-gear{left:0;top:0;width:14px;height:14px;line-height:14px}
'''

def cards(h):
    old = '{{#f_description}}<div class="sheet-long"><b></b>{{f_description}}</div>{{/f_description}}'
    if "{{#f_full}}" not in h and old in h:
        if h.count(old) != 1:
            raise SystemExit("f_description %s" % h.count(old))
        h = h.replace(old, old + '{{#f_full}}<div class="sheet-long">{{f_full}}</div>{{/f_full}}', 1)
    span = ' /><span></span></button><span class="sheet-skm">'
    if span in h:
        h = h.replace(span, ' /><span>&#9881;</span></button><span class="sheet-skm">')
    return h

def settings_gear(h):
    if 'class="sheet-set-gear"' in h:
        return h
    g = '<span class="sheet-set-gear">&#9881;</span>'
    pairs = [
        ('aria-label="Show / hide entry settings" /><div class="sheet-entry-head">',
         'aria-label="Show / hide entry settings" /><div class="sheet-entry-head">' + g),
        ('aria-label="Show / hide entry settings" />\n<div class="sheet-entry-head">',
         'aria-label="Show / hide entry settings" />\n<div class="sheet-entry-head">' + g),
        ('aria-label="Show / hide entry settings" /><div class="sheet-gfx-top">',
         'aria-label="Show / hide entry settings" /><div class="sheet-gfx-top">' + g),
        ('aria-label="Show / hide entry settings" /><div class="sheet-rit-top">',
         'aria-label="Show / hide entry settings" /><div class="sheet-rit-top">' + g),
        ('aria-label="Show / hide entry settings" /><span class="sheet-disc-id">',
         'aria-label="Show / hide entry settings" />' + g + '<span class="sheet-disc-id">'),
        ('aria-label="Show / hide entry settings" /><input type="hidden" name="attr_gtype"',
         'aria-label="Show / hide entry settings" />' + g + '<input type="hidden" name="attr_gtype"'),
    ]
    n = h.count('aria-label="Show / hide entry settings"')
    for a, b in pairs:
        if a not in h:
            raise SystemExit("gear site missing")
        h = h.replace(a, b)
    if h.count('class="sheet-set-gear"') != n:
        raise SystemExit("gears %s of %s" % (h.count('class="sheet-set-gear"'), n))
    return h

def css_add(c):
    # Roll20 drops every roll-template rule if the CSS contains a non-ASCII
    # character or a hex escape of one. The settings cog is an HTML entity.
    c = c.replace("\\2699", "*")
    c = c.replace('content:"\u2699"', "content:none")
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
    h = totem_layout(h)
    h = kuruth(h)
    h = notes(h)
    h = notes_fit(h)
    h = dice(h)
    h = cards(h)
    h = dice_layout(h)
    h = breaking(h)
    h = maneuvers(h)
    h = roll_above(h)
    h = vamp_quick(h)
    h = disciplines(h)
    h = weapons_fix(h)
    h, ncol = collapse(h)
    h = settings_gear(h)
    h = worker(h)
    h = worker_extra(h)
    c = css_add(c)
    bad = banned(c)
    if bad:
        raise SystemExit("banned CSS %s" % bad)
    if "\\2699" in c or any(ord(ch) > 127 for ch in c):
        raise SystemExit("non-ascii css")
    for m in re.finditer(r"\\([0-9a-fA-F]{1,6})", c):
        if int(m.group(1), 16) > 127:
            raise SystemExit("css escape %s" % m.group(0))
    if 'class="sheet-set-gear"' not in h:
        raise SystemExit("settings gear missing")
    if len(c) > 625000:
        raise SystemExit("css %s over 625k cap" % len(c))
    checks = [
        "sheet-ar-cols", "sheet-wx", "sheet-wfilter", "sheet-mv-out", "act_form_prev",
        "sheet-form-view", "sheet-rite-short", "sheet-totem-body", "sheet-kt-split",
        "attr_kuruth_general", "sheet-det-beside", "sheet-fc-bio-line", "sheet-note-cols",
        "sheet-roll-extra", "attr_roll_prompt", "repeating_buffs", "__rev111",
        "sheet-mstyle-s", "sheet-roll-break", "roll_bp_flesh", "roll_bp_spirit",
        "sheet-mv-full", "sheet-disc-card", "sheet-disc-name", "sheet-disc-flat", "sheet-disc-row", "sheet-disc-has", "attr_disc_has_effect", "attr_disc_active", "attr_disc_vigor",
        "sheet-wtype-f", "sheet-whide", "sheet-totem-stats", "attr_totem_power", "attr_totem_legacy",
        "__rev112",
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
    if "Preview form" in h:
        raise SystemExit("preview dropdown left")
    if h.count('name="attr_form_view"') != 1:
        raise SystemExit("form_view inputs %s" % h.count('name="attr_form_view"'))
    # Live-only markers that must survive when the source was the pasted sheet.
    if "sheet-mp-forms" in open(src["html"], encoding="utf-8").read():
        live_keep = ["sheet-mp-forms", "sheet-entry-settings", "act_kuruth_end_rev", "sheet-merit-summary", "Auspice &amp; Tribe"]
        gone = [k for k in live_keep if k not in h]
        if gone:
            raise SystemExit("live markers lost " + ",".join(gone))
        if "Grenze" not in c:
            raise SystemExit("Grenze font lost")
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
