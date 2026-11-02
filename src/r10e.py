"""r10e: Health wound labels under their boxes (Iron Stamina aware), Full Heal button."""
import re
from r10b import take_div

def apply(h, c):
    hr = h.index('<div class="sheet-heal-row">')
    p = re.compile(r'<div class="sheet-corporeal sheet-dots">\s*<input type="hidden" name="attr_health" class="sheet-if" />').search(h, hr).start()
    a0, a1 = take_div(h, p); blk = h[a0:a1]
    assert 'attr_wound_penalty_3' in blk
    blk = blk.replace('<div class="sheet-corporeal sheet-dots">', '<div class="sheet-corporeal sheet-healthboxes sheet-hp-pen" title="Wound penalties on the last three Health boxes: -1, -2, -3. Each dot of Iron Stamina cancels 1 point (Iron Stamina 2: 0, 0, -1). Labels at 0 are hidden.">', 1)
    h = h[:a0] + h[a1:]
    h = h[:hr] + blk + h[hr:]
    full = ('<button type="action" class="sheet-hb-full" name="act_fullheal" title="Full Heal: clear every Health box (all bashing, lethal and aggravated damage)">'
            '&#10010; Full</button>')
    k = h.index('<span class="sheet-hb-grp sheet-hb-heal"'); h = h[:k] + full + h[k:]
    js = r'''
        on("clicked:fullheal", () => { const u = {}; for (let i = 1; i <= 16; i++) u["healthbox_" + i] = "0"; setAttrs(u); });
        on("sheet:opened change:iron_stamina change:health", () => getAttrs(["iron_stamina"], v => setAttrs(getWoundPenalties(parseInt(v.iron_stamina, 10) || 0), {silent: true})));
'''
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    O = '.charsheet.charsheet.charsheet'
    c += '\n' + '\n'.join([
        f'{O} .sheet-hp-pen {{ margin-top: 1px !important; min-height: 0 !important; height: auto !important; }}',
        f'{O} .sheet-hp-pen > .sheet-healthbox {{ height: 12px !important; min-height: 0 !important; border: 0 !important; background: none !important; box-shadow: none !important; }}',
        f'{O} .sheet-hp-pen > span.sheet-healthbox {{ font: bold 10px/12px Arial, sans-serif !important; text-align: center; color: #e0a040; }}',
        f'{O} .sheet-heal-row {{ display: flex !important; align-items: center; justify-content: center; gap: 6px; flex-wrap: wrap; }}',
        f'{O} button.sheet-hb-full {{ height: 18px !important; width: auto !important; padding: 0 7px !important; border-radius: 9px !important; border: 1px solid #3f8f4f !important; background: #12301a !important; color: #9fe0a8 !important; font: bold 11px/16px Arial, sans-serif !important; cursor: pointer; }}',
        f'{O} button.sheet-hb-full:hover {{ background: #1f5a2e !important; color: #fff !important; }}',
    ]) + '\n'
    return h, c
