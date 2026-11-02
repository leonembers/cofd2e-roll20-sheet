"""Move the Notes mid-pane to its own top-level page (reuses the existing, unused 'details' page id)."""
import re
def _block(h, start):
    i = start; d = 0
    for m in re.finditer(r'<div\b|</div>', h[start:]):
        d += 1 if m.group(0) == '<div' else -1
        if d == 0: return h[start:start + m.end()]
    raise ValueError
def apply(h, c):
    s = h.index('<div class="sheet-midpane sheet-mp-notes">')
    blk = _block(h, s); inner = blk[len('<div class="sheet-midpane sheet-mp-notes">'):-6]
    h = h.replace(blk, '', 1)
    h = re.sub(r'<button type="action" class="sheet-midtab-btn sheet-mt-notes"[^>]*>.*?</button>', '', h, 1, re.S)
    page = '<div class="sheet-page sheet-details"><div class="sheet-details-page">' + inner + '</div></div>\n'
    a = h.index('<div class="sheet-page sheet-scars-variations"'); h = h[:a] + page + h[a:]
    b = re.search(r'<button type="action" class="sheet-toggle sheet-page-forms"[^>]*>.*?</button>', h, re.S)
    h = h[:b.end()] + '<button type="action" class="sheet-toggle sheet-page-details" name="act_page_details" title="Character details, portrait, notes and history">Notes</button>' + h[b.end():]
    h = h.replace('["merits","powers","weapons","kuruth","gear","notes"]', '["merits","powers","weapons","kuruth","gear"]')
    js = ('\n        on("sheet:opened", () => getAttrs(["mid_tab"], v => { if (v.mid_tab === "notes") setAttrs({mid_tab: "merits"}, {silent: true}); }));\n')
    h = h.replace('</script>', js + '</script>', 1) if h.count('</script>') == 1 else h[::-1].replace('>tpircs/<', ('>tpircs/<' + js[::-1]), 1)[::-1]
    c += '\n.charsheet.charsheet.charsheet .sheet-details-page { padding: 6px 10px !important; }\n.charsheet.charsheet.charsheet .sheet-details-page .sheet-det-top { display: flex !important; flex-wrap: wrap !important; gap: 10px 14px !important; align-items: flex-start !important; }\n.charsheet.charsheet.charsheet .sheet-details-page .sheet-det-top > .sheet-det-portrait { flex: 0 0 210px !important; max-width: 210px !important; width: 210px !important; }\n.charsheet.charsheet.charsheet .sheet-details-page .sheet-det-top > .sheet-det-grid.sheet-det-grid { flex: 1 1 300px !important; min-width: 0 !important; }\n.charsheet.charsheet.charsheet .sheet-details-page .sheet-det-long, .charsheet.charsheet.charsheet .sheet-details-page .sheet-det-notes { width: 100% !important; }\n.charsheet.charsheet.charsheet .sheet-details-page textarea { width: 100% !important; box-sizing: border-box !important; }\n'
    return h, c
