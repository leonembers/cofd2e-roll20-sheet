"""r9: dice pool: Sheet roll only (no Sheet/Attack/Simple pills), plus a Clear button."""
import re
def apply(h, c):
    m = re.search(r'<div class="sheet-diceroller-options">\s*<button type="action" class="sheet-toggle sheet-rollstyle-sheet".*?</div>', h, re.S); assert m
    h = h[:m.start()] + h[m.end():]
    old = '<input type="text" readonly class="sheet-rollstyle sheet-sheet sheet-pooltxt"'
    assert old in h
    h = h.replace(old, '<button type="action" class="sheet-pool-clear" name="act_pool_clear" title="Clear the selected traits from the dice pool">Clear</button>' + old, 1)
    js = r'''
        on("clicked:pool_clear", () => { const u = resetRollFlags(); delete u.rolltype_select; setAttrs(u); });
        on("sheet:opened", () => getAttrs(["rollstyle"], v => { if (v.rollstyle && v.rollstyle !== "sheet") setAttrs({rollstyle: "sheet"}); }));
'''
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    c += ('\n.charsheet .sheet-rolldisplay { display: flex !important; align-items: center; gap: 6px; }\n'
          '.charsheet.charsheet .sheet-rolldisplay button.sheet-pool-clear { flex: 0 0 auto; order: 2; padding: 1px 10px !important; height: 22px !important; width: auto !important; border-radius: 11px !important; font: bold 11px/18px Arial, sans-serif !important; }\n'
          '.charsheet.charsheet .sheet-rolldisplay input.sheet-pooltxt { flex: 1 1 auto; min-width: 0; }\n')
    return h, c

def touchstones(h, c):
    m = re.search(r'<div class="sheet-game-line sheet-werewolf2 sheet-wolf-rpane"><div class="sheet-wolf-ts">(.*?)</div></div>', h, re.S); assert m
    inner = m.group(1); h = h[:m.start()] + h[m.end():]
    k = h.index('<div class="sheet-km-rules">')
    h = h[:k] + '<div class="sheet-subheader"><span>Touchstones</span></div><div class="sheet-wolf-ts sheet-ts-kuruth">' + inner + '</div>' + h[k:]
    c += ('\n.charsheet .sheet-ts-kuruth { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 10px; margin: 2px 0 8px; }\n'
          '.charsheet .sheet-ts-kuruth label { display: flex; flex-direction: column; font-size: 12px; font-weight: bold; }\n')
    return h, c
