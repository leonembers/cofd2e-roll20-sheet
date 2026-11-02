"""r9: Werewolf form = one drop-down in the right panel under a 'Forms' header, h/w under it; pills removed; right-pane headers centred."""
import re
def apply(h, c):
    anchor = '<div class="sheet-subheader">\n                            <span class="sheet-corporeal" data-i18n="health" title="@{health_calc}">Health</span>'
    assert h.count(anchor) == 1
    blk = ('<div class="sheet-game-line sheet-werewolf2 sheet-rp-forms"><div class="sheet-subheader"><span>Forms</span></div>'
           '<select class="sheet-rp-formsel" name="attr_form" title="Current form (Death Rage sets Gauru / Ur&#39;Khar here too)">'
           '<option value="hishu">Hishu</option><option value="dalu">Dalu</option><option value="gauru">Gauru</option>'
           '<option value="urkhar">Ur&#39;Khar (Firstborn rules)</option><option value="urshul">Urshul</option><option value="urhan">Urhan</option></select>'
           '<div class="sheet-rp-hw" title="Active form height / weight"><span name="attr_form_height"></span> <span name="attr_form_weight"></span></div></div>')
    h = h.replace(anchor, blk + anchor, 1)
    c += ('\n.charsheet.charsheet .sheet-page1 .sheet-main-forms .sheet-form-picker, .charsheet.charsheet .sheet-page1 .sheet-main-forms .sheet-form-qrow { display: none !important; }\n'
          '.charsheet .sheet-rp-forms { text-align: center; margin-bottom: 6px; }\n'
          '.charsheet.charsheet .sheet-rp-forms select.sheet-rp-formsel { width: 170px !important; max-width: 100%; height: 24px; margin: 2px auto 0 !important; display: block; font-weight: bold; }\n'
          '.charsheet .sheet-rp-hw { font-size: 12px; opacity: .9; margin-top: 2px; min-height: 14px; }\n'
          '.charsheet.charsheet.charsheet .sheet-page1 .sheet-grow > .sheet-flex > div:last-child .sheet-subheader { text-align: center !important; justify-content: center !important; }\n')
    return h, c
