"""r9: Merits: no Group checkbox, no Splat category, Style is its own category via a slide toggle; compact boxes."""
import re
def apply(h, c):
    h = re.sub(r'<label class="sheet-mgroup"[^>]*>.*?</label>', '', h, 1, re.S)
    h = h.replace('<option value="Splat">Splat-specific</option><option value="style">Styles</option>', '<option value="Style">Style</option>', 1)
    n = h.count('<option value="Supernatural">Supernatural</option><option value="Splat">Splat-specific</option></select>')
    h = h.replace('<option value="Supernatural">Supernatural</option><option value="Splat">Splat-specific</option></select>', '<option value="Supernatural">Supernatural</option><option value="Style">Style</option></select>')
    old = re.search(r'<label class="sheet-mstyle-cb"[^>]*><input type="checkbox" name="attr_mstyle" value="1" /> Style</label>', h); assert old and n
    h = h.replace(old.group(0), '<label class="sheet-mstyle-cb sheet-switch" title="Style merit: category becomes Style and the 5 maneuver slots appear (off = Physical)"><input type="checkbox" name="attr_mstyle" value="1" /><span class="sheet-sw-track"></span><span class="sheet-sw-lbl">Style</span></label>')
    js = r'''
        // r9 merits: Style toggle <-> Style category; Splat category retired (-> Supernatural)
        on("change:repeating_merits:mstyle", (e) => { if (e.sourceType !== "player") return; const p = "repeating_merits_";
            getAttrs([p + "mcat", p + "mcat_prev"], v => setAttrs(e.newValue === "1" ? {[p + "mcat_prev"]: v[p + "mcat"] === "Style" ? (v[p + "mcat_prev"] || "Physical") : (v[p + "mcat"] || "Physical"), [p + "mcat"]: "Style"} : {[p + "mcat"]: (v[p + "mcat_prev"] && v[p + "mcat_prev"] !== "Style") ? v[p + "mcat_prev"] : "Physical"})); });
        on("change:repeating_merits:mcat", (e) => { if (e.sourceType !== "player") return; setAttrs({"repeating_merits_mstyle": e.newValue === "Style" ? "1" : "0"}); });
        const merit9 = () => getSectionIDs("repeating_merits", ids => getAttrs(["merit_filter", ...ids.flatMap(i => [`repeating_merits_${i}_mcat`, `repeating_merits_${i}_mstyle`])], v => {
            const u = {merit_group: "0"}; if (v.merit_filter === "style") u.merit_filter = "Style"; if (v.merit_filter === "Splat") u.merit_filter = "Supernatural";
            ids.forEach(i => { const p = `repeating_merits_${i}_`;
                if (v[p + "mcat"] === "Splat") u[p + "mcat"] = "Supernatural";
                if (v[p + "mstyle"] === "1" && v[p + "mcat"] !== "Style") { u[p + "mcat_prev"] = v[p + "mcat"] || "Physical"; u[p + "mcat"] = "Style"; } });
            if (Object.keys(u).length) setAttrs(u, {silent: true});
        }));
        on("sheet:opened", merit9);
'''
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    c += ('\n.charsheet input.sheet-mfilter[value="Style"] ~ .repcontainer > .repitem:not(:has(input.sheet-mcat-flag[value="Style"])) { display: none !important; }\n'
          '.charsheet.charsheet .sheet-mstyle-badge { display: none !important; }\n'
          '.charsheet label.sheet-switch { display: inline-flex !important; align-items: center; gap: 5px; cursor: pointer; position: relative; }\n'
          '.charsheet.charsheet label.sheet-switch > input[type=checkbox] { position: absolute !important; opacity: 0 !important; width: 34px !important; height: 18px !important; margin: 0 !important; z-index: 2; cursor: pointer; }\n'
          '.charsheet label.sheet-switch .sheet-sw-track { position: relative; width: 32px; height: 16px; border-radius: 8px; background: #777; transition: background .15s; flex: 0 0 auto; }\n'
          '.charsheet label.sheet-switch .sheet-sw-track::after { content: ""; position: absolute; left: 2px; top: 2px; width: 12px; height: 12px; border-radius: 50%; background: #fff; transition: left .15s; }\n'
          '.charsheet label.sheet-switch > input:checked + .sheet-sw-track { background: #b4743a; }\n'
          '.charsheet label.sheet-switch > input:checked + .sheet-sw-track::after { left: 18px; }\n'
          '.charsheet.charsheet .sheet-merits .repitem .sheet-entry { margin: 0 0 3px !important; padding: 2px 4px !important; }\n'
          '.charsheet.charsheet .sheet-merits .repitem .sheet-entry-head { min-height: 0 !important; gap: 3px !important; padding: 0 !important; }\n'
          '.charsheet.charsheet .sheet-merits .repitem .sheet-entry-body { padding: 3px 2px !important; gap: 3px 6px !important; }\n')
    return h, c
