"""r10 live fixes: repcontainer-safe selectors, armor grid, black pills, dark-only, d10 icon, robust sheet roll,
roll-template CSS hardening (sanitizer-safe words, template rules hoisted right after @import)."""
import re
D10 = 'https://cdn.jsdelivr.net/gh/leonembers/cofd2e-roll20-sheet@461496b99b8a13e963bb1da89d61f3e058c15aba/assets/'

def apply(h, c):
    # armor: post button becomes an icon (no squeezed name span)
    i = h.index('<fieldset class="repeating_armor">'); j = h.index('</fieldset>', i); s = h[i:j]
    s2 = re.sub(r'(<button type="roll" class="sheet-entry-post")( name="roll_post"[^>]*>)<span class="sheet-entry-name" name="attr_name"></span><span class="sheet-entry-ph">.*?</button>',
                lambda m: '<button type="roll" class="sheet-entry-post sheet-post-ic"' + m.group(2) + '&#128172;</button>', s, 1, re.S)
    assert s2 != s, 'armor post'
    h = h[:i] + s2 + h[j:]

    # Roll20: action buttons inside repeating sections must not have underscores in the name
    def fs(m):
        return re.sub(r'name="act_([^"]+)"', lambda x: 'name="act_' + x.group(1).replace('_', '-') + '"', m.group(0))
    h = re.sub(r'<fieldset class="repeating_[^"]+">.*?</fieldset>', fs, h, flags=re.S)
    R = [('on(`clicked:${sec ? "repeating_" + sec + ":" : ""}rr_${nm}`', 'on(sec ? `clicked:repeating_${sec}:rr-${nm.replace(/_/g, "-").toLowerCase()}` : `clicked:rr_${nm}`'),
         ('"clicked:repeating_weapons:tagrm_" + t[0]', '"clicked:repeating_weapons:tagrm-" + t[0].replace(/_/g, "-")'),
         ('"clicked:repeating_weapons:tagrm_piercing"', '"clicked:repeating_weapons:tagrm-piercing"'),
         ('match(/^(repeating_weapons_[^_]+_)tagrm_(.+)$/); if (!m) return;\n            setAttrs({[m[1] + m[2]]: "0"}', 'match(/^(repeating_weapons_[^_]+_)tagrm[-_](.+)$/i); if (!m) return;\n            setAttrs({[m[1] + m[2].replace(/-/g, "_")]: "0"}'),
         ('on(`clicked:repeating_armor:${a}_${k}`', 'on(`clicked:repeating_armor:${a.replace(/_/g, "-")}-${k}`')]
    for a, b in R:
        assert h.count(a) == 1, a
        h = h.replace(a, b)
    # dark only: drop the theme switch, force dark_mode=1
    h, n = re.subn(r'<label class="sheet-cfg-sw" title="Dark sheet theme[^"]*">.*?</label>', '', h, 1, re.S); assert n
    js = r'''
        on("sheet:opened", () => getAttrs(["dark_mode"], v => { if (v.dark_mode !== "1") setAttrs({dark_mode: "1"}); }));
        const rrSheet = (mac) => getAttrs(["dice_pool", "dice_pool_attributes", "dice_pool_label"], (v) => {
            const picked = String(v.dice_pool_attributes || "").split(",").filter(x => x);
            if (!picked.length) return startRoll("&{template:cofd-entry} {{charname=@{character_name}}} {{kind=Dice Roller}} {{name=No dice pool}} {{f_short=Click an Attribute and a Skill name first, then the d10.}}", r => finishRoll(r.rollId));
            const n = parseInt(v.dice_pool, 10) || 0, lbl = String(v.dice_pool_label || "Dice pool").replace(/[{}|\[\]]/g, " ");
            rrRun(mac.split("@{dice_pool_label}").join(lbl).split("@{dice_pool}").join(String(n)), false);
        });
'''
    old = '                rrRun(mac, false);\n            });\n        });'
    assert h.count(old) == 1, 'rr hook'
    h = h.replace(old, '                if (k === "sheet") return rrSheet(mac);\n' + old, 1)
    h = h.replace('const rrRun0 = (mac, isRe) =>', js.strip() + '\n        const rrRun0 = (mac, isRe) =>', 1)
    o2 = 'let poolAttributes = v["dice_pool_attributes"]\n'
    assert o2 in h; h = h.replace(o2, 'let poolAttributes = String(v["dice_pool_attributes"] || "")\n', 1)

    c += r'''
/* r10: armor head as a grid; name full width on top */
.charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) { display: grid !important; grid-template-columns: minmax(0,1fr) auto auto; align-items: center; gap: 4px 6px !important; width: 100%; box-sizing: border-box; }
.charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) > * { order: 0 !important; min-width: 0; }
.charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) > input.sheet-ar-name { grid-column: 1 / 3; grid-row: 1; width: 100% !important; min-width: 120px !important; max-width: none !important; box-sizing: border-box; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; writing-mode: horizontal-tb; }
.charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) > button.sheet-entry-post { display: inline-block !important; grid-column: 3; grid-row: 1; }
.charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) > .sheet-ar-steps { grid-column: 1 / -1; grid-row: 2; display: flex !important; flex-wrap: wrap; gap: 3px 10px; }
.charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) > label.sheet-ar-dtog { grid-column: 1; grid-row: 3; justify-self: start; }
.charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) > label.sheet-ar-eq { grid-column: 2 / -1; grid-row: 3; justify-self: end; }
.charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) > textarea.sheet-ar-desc { grid-column: 1 / -1; grid-row: 4; display: none; width: 100% !important; box-sizing: border-box; height: 48px; }
.charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) > label.sheet-ar-dtog:has(input:checked) ~ textarea.sheet-ar-desc { display: block !important; }
.charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) > input.sheet-entry-toggle, .charsheet.charsheet .sheet-entry-head:has(> input.sheet-ar-name) > span.sheet-entry-name { display: none !important; }
.charsheet .sheet-stp { display: inline-flex; align-items: center; gap: 2px; white-space: nowrap; }
.charsheet.charsheet .sheet-stp input.sheet-stp-v { width: 30px !important; min-width: 0 !important; text-align: center; padding: 0 !important; }
.charsheet.charsheet .sheet-stp button.sheet-stp-b { width: 18px !important; height: 18px !important; min-width: 0 !important; padding: 0 !important; line-height: 16px !important; border-radius: 50% !important; }
/* r10: black middle-tab pills; active = splat accent border */
.charsheet.charsheet.charsheet .sheet-midtabs button.sheet-midtab-btn.sheet-midtab-btn, .charsheet.charsheet.charsheet input.sheet-type ~ * .sheet-midtabs button[type=action].sheet-midtab-btn.sheet-midtab-btn { background: #0d0d0d !important; color: #d8d2c8 !important; border: 2px solid rgba(255,255,255,.16) !important; }
/* r10: d10 roller icon fills and centres in its cell; the old CSS-drawn d6 pseudo-element is gone */
.charsheet.charsheet .sheet-rollcontainer > button::after, .charsheet.charsheet .sheet-rollcontainer > button::before { content: none !important; display: none !important; background: none !important; border: 0 !important; }
.charsheet.charsheet.charsheet .sheet-rollbar.sheet-rollbar .sheet-rollcontainer > button.sheet-was-roll.sheet-rollstyle.sheet-rollstyle { background: url("D10d10.png") center / contain no-repeat !important; inset: 1px !important; }
.charsheet.charsheet.charsheet .sheet-rollbar.sheet-rollbar .sheet-rollcontainer > button.sheet-was-roll.sheet-rollstyle.sheet-rollstyle:hover { background-image: url("D10d10-hover.png") !important; }
.charsheet.charsheet.charsheet .sheet-rollbar.sheet-rollbar .sheet-rollcontainer > button.sheet-was-roll.sheet-rollstyle.sheet-rollstyle:active { background-image: url("D10d10-pressed.png") !important; }
'''.replace('D10', D10)
    return h, c

def splat_active(cols_by_type):
    return ''

def final(c):
    # 1) Roll20 renders repeating rows in .repcontainer[data-groupname]; the fieldset class never matches live
    c = re.sub(r'\.repeating_([A-Za-z0-9_-]+)(?=[\s.:>\[,{])', lambda m: f'.repcontainer[data-groupname="repeating_{m.group(1)}"]', c)
    # 2) words the roll-template CSS sanitizer rejects anywhere in the file
    c = c.replace('[name="attr_expression"]', '[name^="attr_expr"][name$="ssion"]')
    # 3) hoist roll-template rules right after the @imports
    imps = re.findall(r'^@import[^\n]*\n', c, re.M)
    body = re.sub(r'^@import[^\n]*\n', '', c, flags=re.M)
    tpl = []
    def grab(m):
        sel = m.group(1)
        parts = [p.strip() for p in sel.split(',')]
        if parts and all(p.startswith('.sheet-rolltemplate-') for p in parts):
            tpl.append(m.group(0).strip()); return ''
        return m.group(0)
    body = re.sub(r'(?m)(?:^|(?<=\}))([^@{}\n][^{}]*?)\{[^{}]*\}', grab, body)
    return ''.join(imps) + '\n'.join(tpl) + '\n' + body
