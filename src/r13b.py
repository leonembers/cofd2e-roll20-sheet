"""r13b: Kuruth tiers Specific > Common > Passive; centred Touchstones / Kuruth headers, labels and inputs (Werewolf
Kuruth tab and Vampire Frenzy tab); skill specialty/used box removed (the roller handles Specialties) and rows
spaced; Equipment fields sized by purpose."""
import re

P = '.charsheet.charsheet.charsheet.charsheet.charsheet.charsheet'
SK = ['academics', 'computer', 'crafts', 'enigmas', 'investigation', 'medicine', 'occult', 'politics', 'science',
      'archery', 'athletics', 'brawl', 'drive', 'firearms', 'larceny', 'ride', 'stealth', 'survival', 'weaponry',
      'animalken', 'empathy', 'expression', 'intimidation', 'persuasion', 'socialize', 'streetwise', 'subterfuge']


def apply(h, c):
    # (c) drop the per-skill specialty/used box and its worker wiring (nothing else reads <skill>_box)
    n0 = len(re.findall(r'<span class="sheet-checkbox sheet-eq-1">', h))
    h, n = re.subn(r'<span class="sheet-checkbox sheet-eq-1">\s*<input type="hidden" class="sheet-flag" name="attr_(\w+)_box" value="0">\s*'
                   r'<button type="action" name="act_\1_box"[^>]*></button>\s*</span>\s*', '', h)
    assert n == n0 == 27, (n, n0)
    for s in SK:
        h = h.replace(f'"{s}_box",', '').replace(f',"{s}_box"', '').replace(f'"{s}_box"', '')
    rb = 'on("clicked:ride_box", () => getAttrs(["ride_box"], v => setAttrs({ride_box: v.ride_box === "1" ? "0" : "1"})));'
    h = h.replace(rb, '')
    for s in SK:
        assert f'act_{s}_box' not in h and f'"{s}_box"' not in h, s
    K = f'{P} .sheet-mp-kuruth'
    T = f'{P} .sheet-kuruth-tiers.sheet-kt-rows'
    VT = f'{P} .repcontainer[data-groupname="repeating_vtouchstones"]'
    L = [
        # (a) visual order Specific, Common, Passive; the hidden Harmony input stays first in the DOM for the ~ selectors
        f'{T} > label.sheet-kt-specific {{ order: 1 !important; }}',
        f'{T} > label.sheet-kt-common {{ order: 2 !important; }}',
        f'{T} > label.sheet-kt-passive {{ order: 3 !important; }}',
        f'{T} {{ display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr)) !important; flex-direction: row !important; gap: 4px !important; }}',
        f'{T} > input.sheet-kt-hm {{ display: none !important; }}',
        f'{T} > label.sheet-kuruth-tier {{ min-width: 0 !important; padding: 3px 4px !important; gap: 2px; }}',
        f'{T} textarea.sheet-trig-ta {{ height: 48px !important; min-height: 32px !important; margin: 0 !important; font-size: 12px !important; }}',
        # (b) centring
        f'{K} .sheet-subheader, {K} .sheet-subheader > span {{ text-align: center !important; justify-content: center !important; width: 100%; }}',
        f'{K} .sheet-wolf-ts > label {{ display: flex !important; flex-direction: column !important; align-items: center !important; text-align: center !important; }}',
        f'{K} .sheet-wolf-ts > label > span {{ text-align: center !important; width: 100%; }}',
        f'{K} .sheet-wolf-ts > label > input {{ text-align: center !important; width: 100% !important; box-sizing: border-box; }}',
        f'{T} .sheet-kt-lbl {{ flex-direction: column !important; align-items: center !important; justify-content: center !important; text-align: center !important; gap: 1px; }}',
        f'{T} .sheet-kt-rng {{ text-align: center !important; }}',
        f'{P} .sheet-vtouchstones .sheet-entry-section-head {{ justify-content: center !important; text-align: center !important; }}',
        f'{P} .sheet-vtouchstones .sheet-entry-section-head > .sheet-subheader {{ text-align: center !important; justify-content: center !important; }}',
        f'{VT} .sheet-entry-head .sheet-entry-post {{ justify-content: center !important; text-align: center !important; }}',
        f'{VT} .sheet-entry-body label {{ text-align: center !important; align-items: center !important; }}',
        f'{VT} .sheet-entry-body input[type=text] {{ text-align: center !important; }}',
        # (c) skill rows: clear space between the remaining mark box and the name, even row rhythm
        f'{P} div:has(> button.sheet-toggle + button.sheet-spec-caret) > .sheet-skm {{ margin-right: 5px !important; }}',
        f'{P} div:has(> button.sheet-toggle + button.sheet-spec-caret) {{ margin: 0 0 2px !important; }}',
    ]
    # Equipment / weapons / armor fields sized by purpose instead of a flat 10em
    G = lambda s: f'{P} .repcontainer[data-groupname="repeating_{s}"] .sheet-entry-body'
    for sec in ('equipment', 'weapons', 'armor'):
        L += [f'{G(sec)} > label:not(.sheet-wide) > input[type=text], {G(sec)} > label:not(.sheet-wide) > select {{ width: auto !important; max-width: 100% !important; }}',
              f'{G(sec)} > label:not(.sheet-wide) > select {{ field-sizing: content; min-width: 4em; }}']
    L += [f'{G("equipment")} input[name="attr_cost"] {{ width: 6em !important; }}',
          f'{G("weapons")} > label.sheet-hl-name, {G("weapons")} > label.sheet-hl-preset {{ flex: 1 1 100% !important; }}',
          f'{G("weapons")} > label.sheet-hl-name > input, {G("weapons")} > label.sheet-hl-preset > select {{ flex: 1 1 auto !important; width: auto !important; }}',
          f'{G("weapons")} input[name="attr_enhance"] {{ width: 9em !important; }}',
          f'{G("weapons")} label:has(> input[name="attr_tags_extra"]), {G("armor")} label:has(> input[name="attr_ar_tags"]) {{ flex: 1 1 100% !important; }}',
          f'{G("weapons")} input[name="attr_tags_extra"], {G("armor")} input[name="attr_ar_tags"] {{ flex: 1 1 auto !important; width: auto !important; }}',
          f'{G("armor")} input[name="attr_ar_coverage"] {{ width: 9em !important; }}']
    return h, c + '\n' + '\n'.join(L) + '\n'
