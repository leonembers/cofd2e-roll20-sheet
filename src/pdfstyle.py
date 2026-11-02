"""PDF-sheet look: serif type, banner / ornamental section headers, ruled fields, splat accents, splat textures.
Returns CSS (ASCII only). base = https art folder (tex/<splat>-tex.jpg)."""
import json, os
HERE = os.path.dirname(__file__)
FONTS = '@import url("https://fonts.googleapis.com/css?family=IM+Fell+English+SC%7CSorts+Mill+Goudy:400,400i&display=swap");\n'
# splat: (light-mode accent, dark-mode accent, banner colour)
ACC = {'mortal': ('#2d3a6e', '#9fb0e8', '#1c2140'), 'vampire': ('#7a1418', '#e0565c', '#2a0d0e'),
       'werewolf': ('#7a3a12', '#d98a4a', '#1c2416'), 'mage': ('#3a2f7a', '#b9a8ff', '#1a1640'),
       'hunter': ('#1e4646', '#7fc2c2', '#142828'), 'promethean': ('#7a4a1e', '#e0a060', '#2a1a0c'),
       'changeling': ('#0a5a3a', '#6fd0a0', '#0c2a1c'), 'geist': ('#245a68', '#8fd0e0', '#0e2228'),
       'mummy': ('#7a5a14', '#e0c070', '#2a2010'), 'demon': ('#5a2a1a', '#f08a50', '#1a1012'),
       'beast': ('#4a2a4a', '#d09ad0', '#1e121e'), 'deviant': ('#6a1e1e', '#e07a7a', '#1e1416'),
       'breeds': ('#5a321e', '#d0a070', '#20160e')}
RULED = {'werewolf', 'breeds'}   # ornamental-rule headers like the Forsaken PDF; others get the brush banner
def css(base, type_of):
    base = base.rstrip('/')
    D = ('.sheet-darkmode', 'input.sheet-dm[value="1"] ~ .sheet-background')
    o = [FONTS]
    for sp, (l, d, band) in ACC.items():
        for t in type_of.get(sp, []):
            sel = f'.charsheet:has(input.sheet-type[value="{t}"])'
            o.append(f'{sel} {{ --pa: {l}; --pad: {d}; --pb: {band}; --ptex: url("{base}/tex/{sp}-tex.jpg"); }}')
            if sp in RULED:
                o.append(f'{sel} .sheet-section-header {{ --hdr-bg: none; --hdr-fg: var(--pa); --hdr-rule: 1; }}')
    o.append(r'''
.charsheet { --pa: #2d3a6e; --pad: #9fb0e8; --pb: #1c2140; }
/* body texture: light mode = pale wash over the splat texture, dark = dim overlay */
.charsheet .sheet-background { background-image: linear-gradient(rgba(246,242,234,.80), rgba(246,242,234,.84)), var(--ptex) !important; background-size: auto, 640px 640px !important; background-repeat: repeat !important; }
input.sheet-dm[value="1"] ~ .sheet-background, body.sheet-darkmode .charsheet .sheet-background { background-image: linear-gradient(rgba(10,10,12,.50), rgba(10,10,12,.62)), var(--ptex) !important; background-size: auto, 640px 640px !important; background-repeat: repeat !important; }
/* type */
.charsheet .sheet-background, .charsheet .sheet-background :is(div, span, label, button.sheet-toggle, .sheet-input-label, .sheet-subheader, .sheet-subsubheader, .sheet-attributes-category):not(.sheet-ic):not(.sheet-pictos):not(.sheet-hl-pill-x) { font-family: "Sorts Mill Goudy", "Goudy Old Style", Garamond, Georgia, serif !important; }
.charsheet .sheet-background button.sheet-toggle { font-size: 14px; letter-spacing: 0; }
.charsheet .sheet-skills button.sheet-toggle { font-size: 13px; }
.charsheet .sheet-input-label { color: var(--pa) !important; font-size: 14px; } .charsheet .sheet-attributes-category { color: var(--pa) !important; font-size: 13px; padding-right: 3px; }
.charsheet .sheet-attributes-category { font-style: italic; text-transform: lowercase; }
input.sheet-dm[value="1"] ~ .sheet-background :is(.sheet-input-label, .sheet-attributes-category), .sheet-darkmode .sheet-background :is(.sheet-input-label, .sheet-attributes-category) { color: var(--pad) !important; }
/* section headers: brush banner (default) or ornamental rules (Forsaken) */
.charsheet .sheet-section-header { --hdr-bg: var(--pb); --hdr-fg: #f3ecdf; font-family: "IM Fell English SC", "Caslon Antique", Georgia, serif !important; font-size: 22px !important; font-weight: normal !important;
  letter-spacing: 2px; text-transform: uppercase; text-decoration: none !important; line-height: 28px; color: var(--hdr-fg) !important; margin: 8px 0 6px !important; padding: 0 12px !important;
  background: linear-gradient(90deg, rgba(0,0,0,0) 0, var(--hdr-bg) 3%, var(--hdr-bg) 97%, rgba(0,0,0,0) 100%) !important; text-shadow: 0 1px 2px rgba(0,0,0,.6) !important;
  border-top: 1px solid rgba(0,0,0,0) !important; border-bottom: 1px solid rgba(0,0,0,0) !important;
  -webkit-mask-image: repeating-linear-gradient(90deg, #000 0 37px, rgba(0,0,0,.86) 37px 41px, #000 41px 63px, rgba(0,0,0,.93) 63px 66px); mask-image: repeating-linear-gradient(90deg, #000 0 37px, rgba(0,0,0,.86) 37px 41px, #000 41px 63px, rgba(0,0,0,.93) 63px 66px); }
input.sheet-dm[value="1"] ~ .sheet-background .sheet-section-header, .sheet-darkmode .sheet-section-header { --hdr-bg: color-mix(in srgb, var(--pa) 55%, #000); color: #f3ecdf !important; }
.charsheet:has(input.sheet-type[value="werewolf2"]) .sheet-section-header, .charsheet:has(input.sheet-type[value="breeds2"]) .sheet-section-header {
  display: flex; align-items: center; gap: 10px; background: none !important; -webkit-mask-image: none; mask-image: none; color: var(--pa) !important; text-shadow: none !important; justify-content: center; }
.charsheet:has(input.sheet-type[value="werewolf2"]) .sheet-section-header::before, .charsheet:has(input.sheet-type[value="werewolf2"]) .sheet-section-header::after,
.charsheet:has(input.sheet-type[value="breeds2"]) .sheet-section-header::before, .charsheet:has(input.sheet-type[value="breeds2"]) .sheet-section-header::after {
  content: ""; flex: 1; height: 3px; border-top: 1px solid currentColor; border-bottom: 1px solid currentColor; opacity: .7; }
.sheet-darkmode .sheet-section-header, input.sheet-dm[value="1"] ~ .sheet-background .sheet-section-header { }
.charsheet:has(input.sheet-type[value="werewolf2"]) input.sheet-dm[value="1"] ~ .sheet-background .sheet-section-header,
.sheet-darkmode .charsheet:has(input.sheet-type[value="werewolf2"]) .sheet-section-header,
.charsheet:has(input.sheet-type[value="breeds2"]) input.sheet-dm[value="1"] ~ .sheet-background .sheet-section-header { color: var(--pad) !important; }
/* sub headers */
.charsheet .sheet-subheader, .charsheet .sheet-subheader span { font-family: "IM Fell English SC", Georgia, serif !important; font-weight: normal !important; text-decoration: none !important; color: var(--pa) !important; letter-spacing: 1px; }
input.sheet-dm[value="1"] ~ .sheet-background :is(.sheet-subheader, .sheet-subheader span), .sheet-darkmode .sheet-background :is(.sheet-subheader, .sheet-subheader span) { color: var(--pad) !important; }
.charsheet .sheet-subsubheader { font-style: italic; opacity: .85; }
/* ruled info fields like the PDF (underline, no box) */
.charsheet .sheet-info-grid input[type=text], .charsheet .sheet-info-grid select { border: 0 !important; border-bottom: 1px solid color-mix(in srgb, var(--pa) 60%, rgba(0,0,0,0)) !important; border-radius: 0 !important; background: rgba(255,255,255,.35) !important; box-shadow: none !important; }
input.sheet-dm[value="1"] ~ .sheet-background .sheet-info-grid :is(input[type=text], select), .sheet-darkmode .sheet-info-grid :is(input[type=text], select) { background: rgba(0,0,0,.35) !important; border-bottom-color: color-mix(in srgb, var(--pad) 60%, rgba(0,0,0,0)) !important; }
/* dots: thin accent ring, filled = ink */
.charsheet button.sheet-dot { border: 1px solid color-mix(in srgb, var(--pa) 70%, #000) !important; }
input.sheet-dm[value="1"] ~ .sheet-background button.sheet-dot, .sheet-darkmode button.sheet-dot { border-color: color-mix(in srgb, var(--pad) 75%, #fff) !important; }

/* Rogue Trader-style repeating entries: each row is a thin bordered card, one-line head, compact detail body */
.charsheet .repcontainer .repitem > .sheet-entry { border: 1px solid color-mix(in srgb, var(--pa) 35%, rgba(128,128,128,.45)); border-radius: 3px; margin: 0 0 2px; background: rgba(255,255,255,.45); }
input.sheet-dm[value="1"] ~ .sheet-background .repcontainer .repitem > .sheet-entry, .sheet-darkmode .repcontainer .repitem > .sheet-entry { background: rgba(0,0,0,.32); border-color: color-mix(in srgb, var(--pad) 30%, rgba(128,128,128,.35)); }
.charsheet .sheet-entry > .sheet-entry-head { white-space: nowrap; min-height: 18px; }
.charsheet .sheet-entry > .sheet-entry-head .sheet-entry-name { font-weight: bold; }
.charsheet .sheet-entry > input.sheet-entry-toggle:checked + .sheet-entry-head { border-bottom: 1px dashed color-mix(in srgb, var(--pa) 40%, rgba(128,128,128,.4)); }
.charsheet .sheet-entry > .sheet-entry-body { padding: 3px 5px 4px !important; gap: 3px 6px !important; }
.charsheet .sheet-entry > .sheet-entry-body label { font-size: 10px !important; letter-spacing: .3px; text-transform: uppercase; opacity: .95; margin: 0 !important; line-height: 1.25; }
.charsheet .sheet-entry > .sheet-entry-body > label > input, .charsheet .sheet-entry > .sheet-entry-body > label > select { height: 20px !important; font-size: 12px !important; text-transform: none; letter-spacing: 0; }
.charsheet .sheet-entry > .sheet-entry-body textarea { min-height: 34px !important; height: 34px; font-size: 12px !important; text-transform: none; letter-spacing: 0; resize: vertical; }

/* usability: Merits and the splat power list stack in one full-width middle column (were two cramped ~130px columns) */
.charsheet .sheet-page1 .sheet-columns:has(> div > .sheet-entry-section.sheet-merits) { display: flex !important; flex-direction: column !important; gap: 6px; }
.charsheet .sheet-page1 .sheet-columns:has(> div > .sheet-entry-section.sheet-merits) > div { width: 100% !important; max-width: none !important; flex: 0 0 auto !important; }

/* header block above the tabs (layout after the VtM 5E Roll20 sheet: centred logo, rule, 3 x 3 label/field grid, rule) */
.charsheet .sheet-topinfo { position: relative; z-index: 1; margin: 0 0 8px !important; padding: 4px 6px 8px; border-bottom: 2px solid color-mix(in srgb, var(--pa) 70%, rgba(0,0,0,0)); }
input.sheet-dm[value="1"] ~ .sheet-background .sheet-topinfo, .sheet-darkmode .sheet-topinfo { border-bottom-color: color-mix(in srgb, var(--pad) 55%, rgba(0,0,0,0)); }
.charsheet .sheet-topinfo .sheet-toplogo { padding: 2px 0 6px; margin-bottom: 6px; border-bottom: 1px solid color-mix(in srgb, var(--pa) 45%, rgba(128,128,128,.4)); }
.charsheet .sheet-topinfo .sheet-toplogo img { max-height: 110px; width: auto; max-width: 70%; }
.charsheet .sheet-topinfo .sheet-info-grid.sheet-ig2 { display: grid !important; grid-template-columns: repeat(3, minmax(0, 1fr)) !important; gap: 4px 14px !important; margin: 0 !important; width: 100% !important; box-sizing: border-box; }
.charsheet .sheet-ig2 > .sheet-ifield { display: flex; align-items: center; gap: 6px; min-width: 0; }
.charsheet .sheet-ig2 > .sheet-ifield > .sheet-input-label { flex: 0 0 74px; text-align: right; font-weight: bold; white-space: nowrap; font-size: 14px; overflow: hidden; text-overflow: ellipsis; }
.charsheet .sheet-ig2 > .sheet-ifield :is(input[type=text], select) { flex: 1 1 auto; width: auto !important; min-width: 0 !important; max-width: none !important; box-sizing: border-box; height: 22px !important; margin: 0 !important;
  border: 1px solid color-mix(in srgb, var(--pa) 45%, rgba(128,128,128,.6)) !important; border-radius: 3px !important; padding: 0 5px !important; font-size: 13px !important; }

/* dice roller: no roll-type tag under the die (the active toggle shows it) */
.charsheet .sheet-rollbar .sheet-rollcontainer::before, .charsheet input.sheet-rolltype-select ~ * .sheet-rollcontainer::before { content: none !important; display: none !important; }
.charsheet .sheet-rollbar .sheet-rollcontainer { height: 34px !important; }
/* compact pool line */
.charsheet .sheet-rollbar .sheet-rolldisplay input.sheet-pooltxt { width: 100% !important; height: 22px !important; min-height: 0 !important; box-sizing: border-box; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-family: inherit !important; font-size: 12px !important; padding: 0 6px !important; border-radius: 4px !important; cursor: default; }
/* roller checkboxes as pill toggles */
.charsheet .sheet-wp-bar { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; }
.charsheet .sheet-wp-bar label:not(.sheet-game-line) { display: inline-flex; }
.charsheet .sheet-wp-bar label { position: relative; align-items: center; height: 20px; padding: 0 9px !important; margin: 0 !important; border-radius: 10px !important; cursor: pointer; white-space: nowrap; font-size: 11px !important; line-height: 20px;
  border: 1px solid color-mix(in srgb, var(--pa) 55%, rgba(128,128,128,.5)) !important; background: rgba(0,0,0,0) !important; color: inherit; user-select: none; }
.charsheet .sheet-wp-bar label > input[type=checkbox] { position: absolute !important; opacity: 0 !important; width: 1px !important; height: 1px !important; margin: 0 !important; pointer-events: none; }
.charsheet .sheet-wp-bar label:hover { border-color: var(--pa) !important; }
.charsheet .sheet-wp-bar label:has(> input[type=checkbox]:checked) { background: var(--pa) !important; border-color: var(--pa) !important; color: #fff !important; }
input.sheet-dm[value="1"] ~ .sheet-background .sheet-wp-bar label:has(> input[type=checkbox]:checked), .sheet-darkmode .sheet-wp-bar label:has(> input[type=checkbox]:checked) { background: color-mix(in srgb, var(--pad) 80%, rgba(0,0,0,.4)) !important; border-color: var(--pad) !important; color: #111 !important; }
.charsheet .sheet-wp-bar label > input[type=checkbox]:focus-visible + span { outline: 1px dotted currentColor; }
.charsheet .sheet-wp-bar select { height: 20px !important; border-radius: 10px !important; font-size: 11px !important; }
/* roll-type and roll-style toggles: accent highlight, uniform pills */
.charsheet .sheet-rollbar .sheet-diceroller-options button.sheet-toggle { border-radius: 10px !important; height: 20px; padding: 0 8px !important; font-size: 11px !important; white-space: nowrap; }

/* clear-backdrop geist logo: no dark-mode invert */
input.sheet-dm[value="1"] ~ .sheet-background .sheet-logo img.sheet-geist2, .sheet-darkmode .sheet-logo img.sheet-geist2 { filter: none !important; }

/* header logos: one fixed, centred box for every splat */
.charsheet .sheet-topinfo .sheet-toplogo { display: flex !important; align-items: center; justify-content: center; height: 132px; padding: 6px 0 !important; margin: 0 0 8px !important; box-sizing: border-box; overflow: hidden; }
.charsheet .sheet-topinfo .sheet-toplogo img { height: 120px !important; max-height: 120px !important; width: auto !important; max-width: 90% !important; object-fit: contain; margin: 0 auto !important; padding: 0 !important; position: static !important; float: none !important; transform: none !important; }
/* vampire bloodline: show the free-text field (attr_Faction) */
.charsheet input.sheet-game-line[value="vampire"] ~ * .sheet-topinfo .sheet-wolf-hdr-wrap input.sheet-wolf-generic[name="attr_Faction"], .charsheet input.sheet-game-line[value="vampire"] ~ .sheet-topinfo .sheet-wolf-hdr-wrap input.sheet-wolf-generic[name="attr_Faction"] { display: block !important; }

/* werewolf2: procedural Forsaken frame (umber/rust/amber, claw marks, crescent) replaces the darkened frame art */
input.sheet-type[value="werewolf2"] ~ .sheet-background-image .sheet-bgart { display: block !important; filter: none !important; background: url("@ABW@/wtf/wtf-top.jpg") top center / 100% auto no-repeat, url("@ABW@/wtf/wtf-bot.jpg") bottom center / 100% auto no-repeat, url("@ABW@/wtf/wtf-mid.jpg") center top / 100% auto repeat-y !important; }
body.sheet-darkmode .charsheet input.sheet-type[value="werewolf2"] ~ .sheet-background-image .sheet-bgart, .charsheet:has(input.sheet-dm[value="1"]) input.sheet-type[value="werewolf2"] ~ .sheet-background-image .sheet-bgart { filter: none !important; background: url("@ABW@/wtf/wtf-top-dark.jpg") top center / 100% auto no-repeat, url("@ABW@/wtf/wtf-bot-dark.jpg") bottom center / 100% auto no-repeat, url("@ABW@/wtf/wtf-mid-dark.jpg") center top / 100% auto repeat-y !important; }
input.sheet-type[value="breeds2"] ~ .sheet-background-image .sheet-bgart { display: block !important; filter: none !important; background: url("@ABW@/wtf/wtf-top.jpg") top center / 100% auto no-repeat, url("@ABW@/wtf/wtf-bot.jpg") bottom center / 100% auto no-repeat, url("@ABW@/wtf/wtf-mid.jpg") center top / 100% auto repeat-y !important; }
body.sheet-darkmode .charsheet input.sheet-type[value="breeds2"] ~ .sheet-background-image .sheet-bgart, .charsheet:has(input.sheet-dm[value="1"]) input.sheet-type[value="breeds2"] ~ .sheet-background-image .sheet-bgart { filter: none !important; background: url("@ABW@/wtf/wtf-top-dark.jpg") top center / 100% auto no-repeat, url("@ABW@/wtf/wtf-bot-dark.jpg") bottom center / 100% auto no-repeat, url("@ABW@/wtf/wtf-mid-dark.jpg") center top / 100% auto repeat-y !important; }
input.sheet-type[value="mortal2"] ~ .sheet-background-image .sheet-bgart { display: block !important; filter: none !important; background: url("@ABN@/mortal/mortal-top.jpg") top center / 100% auto no-repeat, url("@ABN@/mortal/mortal-bot.jpg") bottom center / 100% auto no-repeat, url("@ABN@/mortal/mortal-mid.jpg") center top / 100% auto repeat-y !important; }
body.sheet-darkmode .charsheet input.sheet-type[value="mortal2"] ~ .sheet-background-image .sheet-bgart, .charsheet:has(input.sheet-dm[value="1"]) input.sheet-type[value="mortal2"] ~ .sheet-background-image .sheet-bgart { filter: none !important; background: url("@ABN@/mortal/mortal-top-dark.jpg") top center / 100% auto no-repeat, url("@ABN@/mortal/mortal-bot-dark.jpg") bottom center / 100% auto no-repeat, url("@ABN@/mortal/mortal-mid-dark.jpg") center top / 100% auto repeat-y !important; }
input.sheet-type[value="hunter2"] ~ .sheet-background-image .sheet-bgart { display: block !important; filter: none !important; background: url("@ABN@/hunter/hunter-top.jpg") top center / 100% auto no-repeat, url("@ABN@/hunter/hunter-bot.jpg") bottom center / 100% auto no-repeat, url("@ABN@/hunter/hunter-mid.jpg") center top / 100% auto repeat-y !important; }
body.sheet-darkmode .charsheet input.sheet-type[value="hunter2"] ~ .sheet-background-image .sheet-bgart, .charsheet:has(input.sheet-dm[value="1"]) input.sheet-type[value="hunter2"] ~ .sheet-background-image .sheet-bgart { filter: none !important; background: url("@ABN@/hunter/hunter-top-dark.jpg") top center / 100% auto no-repeat, url("@ABN@/hunter/hunter-bot-dark.jpg") bottom center / 100% auto no-repeat, url("@ABN@/hunter/hunter-mid-dark.jpg") center top / 100% auto repeat-y !important; }
input.sheet-type[value="mage2"] ~ .sheet-background-image .sheet-bgart { display: block !important; filter: none !important; background: url("@ABN@/mage/mage-top.jpg") top center / 100% auto no-repeat, url("@ABN@/mage/mage-bot.jpg") bottom center / 100% auto no-repeat, url("@ABN@/mage/mage-mid.jpg") center top / 100% auto repeat-y !important; }
body.sheet-darkmode .charsheet input.sheet-type[value="mage2"] ~ .sheet-background-image .sheet-bgart, .charsheet:has(input.sheet-dm[value="1"]) input.sheet-type[value="mage2"] ~ .sheet-background-image .sheet-bgart { filter: none !important; background: url("@ABN@/mage/mage-top-dark.jpg") top center / 100% auto no-repeat, url("@ABN@/mage/mage-bot-dark.jpg") bottom center / 100% auto no-repeat, url("@ABN@/mage/mage-mid-dark.jpg") center top / 100% auto repeat-y !important; }
input.sheet-type[value="demon"] ~ .sheet-background-image .sheet-bgart { display: block !important; filter: none !important; background: url("@ABN@/demon/demon-top.jpg") top center / 100% auto no-repeat, url("@ABN@/demon/demon-bot.jpg") bottom center / 100% auto no-repeat, url("@ABN@/demon/demon-mid.jpg") center top / 100% auto repeat-y !important; }
body.sheet-darkmode .charsheet input.sheet-type[value="demon"] ~ .sheet-background-image .sheet-bgart, .charsheet:has(input.sheet-dm[value="1"]) input.sheet-type[value="demon"] ~ .sheet-background-image .sheet-bgart { filter: none !important; background: url("@ABN@/demon/demon-top-dark.jpg") top center / 100% auto no-repeat, url("@ABN@/demon/demon-bot-dark.jpg") bottom center / 100% auto no-repeat, url("@ABN@/demon/demon-mid-dark.jpg") center top / 100% auto repeat-y !important; }
input.sheet-type[value="beast"] ~ .sheet-background-image .sheet-bgart { display: block !important; filter: none !important; background: url("@ABN@/beast/beast-top.jpg") top center / 100% auto no-repeat, url("@ABN@/beast/beast-bot.jpg") bottom center / 100% auto no-repeat, url("@ABN@/beast/beast-mid.jpg") center top / 100% auto repeat-y !important; }
body.sheet-darkmode .charsheet input.sheet-type[value="beast"] ~ .sheet-background-image .sheet-bgart, .charsheet:has(input.sheet-dm[value="1"]) input.sheet-type[value="beast"] ~ .sheet-background-image .sheet-bgart { filter: none !important; background: url("@ABN@/beast/beast-top-dark.jpg") top center / 100% auto no-repeat, url("@ABN@/beast/beast-bot-dark.jpg") bottom center / 100% auto no-repeat, url("@ABN@/beast/beast-mid-dark.jpg") center top / 100% auto repeat-y !important; }
''')
    o.append('.charsheet .sheet-bloodbone{margin:4px 0 2px;max-width:100%;box-sizing:border-box}')
    o.append('.charsheet .sheet-bloodbone .sheet-bb-grid{display:grid;grid-template-columns:1fr 1fr;gap:3px 8px;align-items:start}')
    o.append('.charsheet .sheet-bb-entry{border:1px solid color-mix(in srgb,var(--pa) 35%,rgba(128,128,128,.45));border-radius:3px;background:rgba(255,255,255,.45);position:relative;min-width:0}')
    o.append('input.sheet-dm[value="1"] ~ .sheet-background .sheet-bb-entry,.sheet-darkmode .sheet-bb-entry{background:rgba(0,0,0,.32);border-color:color-mix(in srgb,var(--pad) 30%,rgba(128,128,128,.35))}')
    o.append('.charsheet .sheet-bb-entry > .sheet-entry-head{display:flex;align-items:center;gap:4px;min-height:22px;padding:1px 4px 1px 20px}')
    o.append('.charsheet .sheet-bb-entry .sheet-bb-lbl{font-weight:bold;color:var(--pa);flex:0 0 auto;font-size:12px}')
    o.append('.charsheet .sheet-bb-entry input.sheet-bb-name{flex:1 1 auto;min-width:0;width:auto !important;height:20px;margin:0 !important;padding:0 4px !important;font-weight:bold;font-size:12px;box-sizing:border-box}')
    o.append('.charsheet .sheet-bb-entry button.sheet-bb-post{flex:0 0 22px;width:22px;height:20px;padding:0;margin:0;font-size:11px;line-height:1;min-width:0}')
    o.append('.charsheet .sheet-bb-entry button.sheet-bb-post::before{content:none !important}')
    o.append('.charsheet .sheet-bb-entry > .sheet-entry-body{display:block;padding:3px 5px 4px}')
    o.append('.charsheet .sheet-bb-entry > input.sheet-entry-toggle:not(:checked) ~ .sheet-entry-body{display:none}')
    o.append('.charsheet .sheet-bb-entry .sheet-bb-desc-l{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.3px}')
    o.append('.charsheet .sheet-bb-entry textarea{display:block;width:100% !important;box-sizing:border-box;min-height:46px;height:46px;font-size:12px;text-transform:none;letter-spacing:0;resize:vertical;margin:1px 0 0}')
    o.append('.charsheet .sheet-bb-entry > input[type="checkbox"].sheet-entry-toggle{position:absolute;left:0;top:0;width:20px;height:22px;margin:0;opacity:0;z-index:3;cursor:pointer}')
    o.append('.charsheet .sheet-bb-entry > .sheet-entry-head{position:relative}')
    o.append('.charsheet .sheet-bb-entry > input[type="checkbox"].sheet-entry-toggle + .sheet-entry-head::before{content:"" !important;font-family:Arial,sans-serif !important;position:absolute;left:6px !important;top:7px !important;width:5px;height:5px;border:0 solid var(--pa,#8b1010);border-right-width:2px;border-bottom-width:2px;transform:rotate(-45deg) !important;transition:transform .12s;text-shadow:none !important;color:inherit}')
    o.append('.charsheet .sheet-bb-entry > input[type="checkbox"].sheet-entry-toggle:checked + .sheet-entry-head::before{transform:rotate(45deg) !important;top:5px !important}')
    o.append('.charsheet .sheet-page1{padding-right:8px !important;box-sizing:border-box}')
    o.append('.charsheet .sheet-page1 label.sheet-form-select{display:flex;align-items:center;gap:4px;max-width:100%;box-sizing:border-box;flex-wrap:wrap}')
    o.append('.charsheet .sheet-page1 label.sheet-form-select select{width:auto !important;min-width:0;max-width:100% !important;flex:1 1 90px;box-sizing:border-box}')
    o.append('.charsheet .sheet-page1 input[type=text],.charsheet .sheet-page1 select{max-width:100%;box-sizing:border-box}')
    return '\n'.join(o).replace('@ABN@', base.rstrip('/').replace('@main', '@2fc8fd2')).replace('@ABW@', base.rstrip('/').replace('@main', '@a0a7be1')).replace('@AB@', base.rstrip('/'))

# Art pins (jsDelivr, pinned by commit in leonembers/cofd-sheet-art)
MOON_BASE = 'https://cdn.jsdelivr.net/gh/leonembers/cofd-sheet-art@763e6e88d0ea305ae02f787cba83afe8597111ff/moon'
