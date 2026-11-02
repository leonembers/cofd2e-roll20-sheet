"""r9: Armor rows (name on top, collapsible description, steppers, Worn switch); Weapons (no legacy Range/Clip, name = attack roll, icon post, even name widths); compact boxes."""
import re
ST = [('ar_general', 'General', 0, 8), ('ar_ballistic', 'Ballistic', 0, 8), ('ar_str', 'Str req.', 0, 5), ('ar_def', 'Def pen.', -5, 0), ('ar_spd', 'Spd pen.', -5, 0)]
ICON = '&#128172;'
def step(a, lbl, lo, hi):
    return (f'<span class="sheet-stp" title="{lbl}"><span class="sheet-stp-l">{lbl}</span>'
            f'<button type="action" class="sheet-stp-b" name="act_{a}_dec" title="{lbl} -1">-</button>'
            f'<input type="number" class="sheet-stp-v" name="attr_{a}" value="0" min="{lo}" max="{hi}" step="1" />'
            f'<button type="action" class="sheet-stp-b" name="act_{a}_inc" title="{lbl} +1">+</button></span>')
def apply(h, c):
    i = h.index('<fieldset class="repeating_armor">'); j = h.index('</fieldset>', i); s = h[i:j]
    s = re.sub(r'<span class="sheet-ar-pills">.*?</span></span></span>', '', s, 1, re.S)
    s = re.sub(r'<label class="sheet-ar-eq"[^>]*><input type="checkbox" name="attr_ar_equipped" value="1" checked /><span>Worn</span></label>',
               '<label class="sheet-ar-eq sheet-switch" title="Worn: only worn armor counts toward Armor, Defense and Speed"><input type="checkbox" name="attr_ar_equipped" value="1" checked /><span class="sheet-sw-track"></span><span class="sheet-sw-lbl">Worn</span></label>', s, 1)
    s = s.replace('<span class="sheet-entry-ph">(<span data-i18n="new-entry">new entry</span>)</span></button>',
                  '<span class="sheet-entry-ph">(<span data-i18n="new-entry">new entry</span>)</span></button>'
                  '<input type="text" class="sheet-ar-name" name="attr_name" placeholder="Armor name" title="Armor name" />'
                  '<div class="sheet-ar-steps">' + ''.join(step(*x) for x in ST) + '</div>'
                  '<label class="sheet-ar-dtog" title="Show / hide the description"><input type="checkbox" name="attr_ar_desc_open" value="1" /><span>Description</span></label>'
                  '<textarea class="sheet-ar-desc" name="attr_notes" rows="2" placeholder="Description / notes"></textarea>', 1)
    for a, *_ in ST:
        s = re.sub(rf'<label><span class="sheet-lbl">[^<]*</span><select name="attr_{a}">.*?</select></label>\s*', '', s, 1, re.S)
    s = re.sub(r'<label class="sheet-wide"><span data-i18n="name">Name</span><input type="text" name="attr_name" /></label>\s*', '', s, 1)
    s = re.sub(r'<label class="sheet-wide"><span class="sheet-lbl">Notes</span><textarea name="attr_notes"></textarea></label>\s*', '', s, 1)
    h = h[:i] + s + h[j:]
    js = '        ' + repr({a: [lo, hi] for a, _, lo, hi in ST}).replace("'", '"').join(['const AR_ST = ', ';\n'])
    js += r'''        Object.keys(AR_ST).forEach(a => [["dec", -1], ["inc", 1]].forEach(([k, d]) => on(`clicked:repeating_armor:${a}_${k}`, () => {
            const p = "repeating_armor_" + a; getAttrs([p], v => { const [lo, hi] = AR_ST[a]; setAttrs({[p]: Math.max(lo, Math.min(hi, (parseInt(v[p], 10) || 0) + d))}); }); })));
'''
    # ---- weapons
    i = h.index('<fieldset class="repeating_weapons">'); j = h.index('</fieldset>', i); s = h[i:j]
    s = re.sub(r'<label><span class="sheet-lbl">Range \(custom[^<]*</span><input type="text" name="attr_range_txt" /></label>\s*', '', s, 1)
    s = re.sub(r'<label><span class="sheet-lbl">Clip \(custom[^<]*</span><input type="text" name="attr_clip_txt" /></label>\s*', '', s, 1)
    m = re.search(r'(<button type="roll" class="sheet-entry-post" name="roll_post" title="Post to chat" value="[^"]*">)(<span class="sheet-entry-name" name="attr_name"></span><span class="sheet-entry-ph">.*?)</button>', s, re.S); assert m
    s = s.replace(m.group(0), '<button type="action" class="sheet-w-atk sheet-was-roll" name="act_rr_attack" title="Roll this attack">' + m.group(2) + '</button>'
                  + m.group(1).replace('class="sheet-entry-post"', 'class="sheet-entry-post sheet-post-ic"') + ICON + '</button>', 1)
    h = h[:i] + s + h[j:]
    assert 'attr_range_txt' not in s and 'attr_clip_txt' not in s
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    c += r'''
.charsheet.charsheet .repeating_armor .sheet-entry-head { display: flex !important; flex-wrap: wrap !important; align-items: center; gap: 3px 6px !important; }
.charsheet.charsheet .repeating_armor .sheet-entry-head > button.sheet-entry-post { display: none !important; }
.charsheet.charsheet .repeating_armor .sheet-entry-head > input.sheet-ar-name { flex: 1 1 100% !important; order: -2; width: 100% !important; max-width: none !important; min-width: 0 !important; box-sizing: border-box; font-weight: bold; white-space: nowrap; }
.charsheet.charsheet .repeating_armor .sheet-entry-head > input.sheet-entry-toggle { order: -3; }
.charsheet .sheet-ar-steps { display: flex; flex-wrap: wrap; gap: 3px 8px; flex: 1 1 auto; }
.charsheet .sheet-stp { display: inline-flex; align-items: center; gap: 2px; font-size: 11px; white-space: nowrap; }
.charsheet .sheet-stp-l { margin-right: 2px; opacity: .85; }
.charsheet.charsheet .sheet-stp button.sheet-stp-b { width: 16px !important; height: 16px !important; min-width: 0 !important; padding: 0 !important; line-height: 14px !important; border-radius: 50% !important; border: 1px solid currentColor !important; font: bold 11px/14px Arial, sans-serif !important; text-align: center; }
.charsheet.charsheet .sheet-stp input.sheet-stp-v { width: 30px !important; min-width: 0 !important; height: 18px !important; padding: 0 !important; text-align: center !important; -moz-appearance: textfield; }
.charsheet .sheet-stp input.sheet-stp-v::-webkit-inner-spin-button, .charsheet .sheet-stp input.sheet-stp-v::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
.charsheet label.sheet-ar-dtog { flex: 1 1 100%; font-size: 11px; cursor: pointer; opacity: .85; display: flex; align-items: center; gap: 4px; }
.charsheet.charsheet .repeating_armor textarea.sheet-ar-desc { display: none; flex: 1 1 100%; width: 100% !important; box-sizing: border-box; height: 44px; resize: vertical; }
.charsheet.charsheet .repeating_armor label.sheet-ar-dtog:has(input:checked) + textarea.sheet-ar-desc { display: block !important; }
.charsheet.charsheet .repeating_weapons .sheet-entry-head { display: flex !important; align-items: center; gap: 4px !important; }
.charsheet.charsheet .repeating_weapons .sheet-entry-head > button.sheet-w-atk { flex: 1 1 0 !important; min-width: 0 !important; width: auto !important; max-width: none !important; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: left; padding: 1px 4px !important; background: none !important; border: 0 !important; font-weight: bold; cursor: pointer; }
.charsheet.charsheet .repeating_weapons .sheet-entry-head > button.sheet-w-atk:hover { text-decoration: underline; }
.charsheet.charsheet button.sheet-entry-post.sheet-post-ic { flex: 0 0 auto !important; width: 22px !important; height: 20px !important; min-width: 0 !important; padding: 0 !important; font-size: 13px !important; line-height: 18px !important; text-align: center; border-radius: 4px !important; }
.charsheet.charsheet .sheet-entry-body input[type=number] { width: 52px !important; min-width: 0 !important; }
.charsheet.charsheet .sheet-entry-body select { width: auto !important; max-width: 100%; min-width: 0 !important; }
.charsheet.charsheet .sheet-entry-section .repitem .sheet-entry-body { gap: 3px 8px !important; }
.charsheet.charsheet .sheet-entry-section .repitem .sheet-entry-body > label:not(.sheet-wide) { flex: 0 1 auto !important; width: auto !important; min-width: 0 !important; }
'''
    return h, c
