"""r10f: live-bug hardening (Clear clickable + renamed, template CSS first, no @import), d10, logos, Wolf's Rain
on section headers, Health label colour/gap."""
import re, os
R = os.path.dirname(os.path.abspath(__file__))
W2 = '.charsheet.charsheet.charsheet.charsheet input.sheet-type.sheet-type.sheet-type[value="werewolf2"] ~ *'
W2X = '.charsheet.charsheet.charsheet.charsheet input.sheet-type.sheet-type.sheet-type[value="werewolf2"] ~'

def apply(h, c):
    # Clear: rename (no underscore) and make it clickable (rolldisplay children had pointer-events:none)
    h = h.replace('name="act_pool_clear"', 'name="act_poolclear"').replace('"clicked:pool_clear"', '"clicked:poolclear"')
    js = r'''
        on("clicked:poolclear", () => setAttrs({dice_pool_attributes: "", dice_pool: "0", dice_pool_label: "", rolldisplay: ""}));
        ["ceremonies","vessels","covers","fetishes"].forEach((sec) => { for (let d = 0; d <= 5; d++) on(`clicked:repeating_${sec}:rating-${d}`, () => setAttrs({[`repeating_${sec}_rating`]: d})); });
        on("clicked:ride_box", () => getAttrs(["ride_box"], v => setAttrs({ride_box: v.ride_box === "1" ? "0" : "1"})));
        on("clicked:goblin-debt", () => getAttrs(["goblin-debt_flag"], v => setAttrs({"goblin-debt_flag": v["goblin-debt_flag"] === "1" ? "0" : "1"})));
        on("sheet:opened", () => getAttrs(["modifiermacro", "dicepoolmacro"], v => { const u = {}; if (!v.modifiermacro || v.modifiermacro === "false") u.modifiermacro = "Modifier"; if (!v.dicepoolmacro || v.dicepoolmacro === "false") u.dicepoolmacro = "Dice pool"; if (Object.keys(u).length) setAttrs(u, {silent: true}); }));
'''
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    O = '.charsheet.charsheet.charsheet'
    c += '\n' + '\n'.join([
        f'{O} .sheet-diceroller .sheet-rolldisplay > button.sheet-pool-clear {{ pointer-events: auto !important; cursor: pointer; position: relative; z-index: 2; }}',
        # d10 fills and centres in its cell
        f'{O} .sheet-rollbar .sheet-rollcontainer > button.sheet-was-roll.sheet-rollstyle {{ background-position: center !important; background-size: contain !important; background-repeat: no-repeat !important; }}',
        # Wolf's Rain on every Werewolf section header
        f'{W2} .sheet-section-header.sheet-section-header.sheet-section-header, {W2} .sheet-subheader.sheet-subheader.sheet-subheader, {W2} .sheet-section-header.sheet-section-header.sheet-section-header *, {W2} .sheet-subheader.sheet-subheader.sheet-subheader > span, {W2X} .sheet-section-header.sheet-section-header.sheet-section-header, {W2X} .sheet-subheader.sheet-subheader.sheet-subheader {{ font-family: "WolfsRain", "IM Fell English SC", serif !important; letter-spacing: .04em; }}',
        # logos: contained, centred, unclipped; Vampire larger
        f'{O} .sheet-logo.sheet-toplogo {{ overflow: visible !important; display: flex !important; justify-content: center; align-items: center; }}',
        f'{O} .sheet-logo img.sheet-leon-logo {{ object-fit: contain; object-position: center; max-width: 100% !important; }}',
        f'{O} .sheet-logo img.sheet-leon-logo.sheet-vampire2 {{ height: 175px !important; max-height: 175px !important; width: auto !important; }}',
        # Health penalty labels: readable colour, no gap
        f'{O} .sheet-healthboxes.sheet-hp-pen > span.sheet-healthbox, {O} .sheet-healthboxes.sheet-hp-pen > span.sheet-healthbox[name] {{ color: #ffb347 !important; -webkit-text-fill-color: #ffb347; opacity: 1 !important; font: bold 11px/12px Arial, sans-serif !important; text-shadow: 0 0 2px #000; }}',
        f'{O} .sheet-healthboxes:has(+ .sheet-hp-pen) {{ margin-bottom: 0 !important; padding-bottom: 0 !important; }}',
        f'{O} .sheet-healthboxes.sheet-hp-pen {{ margin: 0 !important; padding: 0 !important; line-height: 12px !important; }}',
        f'{O} div:has(> .sheet-res-ctr):has(> .sheet-subheader) {{ display: flex !important; flex-direction: column; }}',
        f'{O} div:has(> .sheet-res-ctr) > .sheet-subheader {{ order: -2; }}',
        f'{O} div:has(> .sheet-subheader) > .sheet-res-ctr {{ order: -1; margin-top: 2px; }}',
        f'{W2} .sheet-ifield:has(> span.sheet-wolf-hdr-wrap:not(.sheet-vamp)) {{ display: flex !important; align-items: center; grid-template-columns: none !important; }}',
        f'{W2} .sheet-ifield:has(> span.sheet-wolf-hdr-wrap:not(.sheet-vamp)) > .sheet-input-label {{ flex: 0 0 85px; width: 85px !important; }}',
        f'{W2} .sheet-ifield > span.sheet-wolf-hdr-wrap:not(.sheet-vamp) {{ flex: 1 1 auto; min-width: 0; width: auto !important; }}',
        '.charsheet.charsheet.charsheet input.sheet-type[value="mummy"] ~ * div:has(> .sheet-res-ctr.sheet-vitae) { display: none !important; }',
        '.charsheet.charsheet.charsheet input.sheet-type:not([value="vampire2"]) ~ * .sheet-quick-actions.sheet-vampire2 { display: none !important; }',
    ]) + '\n'
    return h, c

def fonts():
    return open(os.path.join(R, 'gfonts.css')).read()
