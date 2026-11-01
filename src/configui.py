"""Config tab glow-up: responsive card grid. Every attribute name / flag structure is kept; only the layout changes."""
import re
from nodtf import _close

def _cut(s, start_pat, tag='div'):
    m = re.search(start_pat, s)
    if not m: raise ValueError(start_pat)
    e = _close(s, m.start(), tag)
    return s[m.start():e]

def _flag(src, name):
    """the <span class="sheet-checkbox"> ... attr_{name} ... </span> toggle, as is"""
    m = re.search(r'<span class="sheet-checkbox[^"]*">\s*<input type="hidden" class="sheet-flag"[^>]*name="attr_%s"' % name, src)
    return src[m.start():_close(src, m.start(), 'span')]

def card(key, title, body, extra='', tip=''):
    return (f'<div class="sheet-cfg-card sheet-cfg-{key} {extra}" title="{tip}">'
            f'<div class="sheet-subheader sheet-cfg-head">{title}</div><div class="sheet-cfg-body">{body}</div></div>')

def row(label, ctl, tip):
    return f'<label class="sheet-cfg-row" title="{tip}"><span class="sheet-cfg-lbl">{label}</span>{ctl}</label>'

def sw(name, label, tip, checked=False):
    return (f'<label class="sheet-cfg-sw" title="{tip}"><input type="checkbox" name="attr_{name}" value="1"{" checked" if checked else ""} />'
            f'<span class="sheet-cfg-knob"></span><span>{label}</span></label>')

def apply(h, c):
    i = h.find('<div class="sheet-page sheet-settings">'); e = _close(h, i, 'div'); s = h[i:e]
    pills = _cut(s, r'<div class="sheet-splat-select">')
    homebrew = _cut(s, r'<div class="sheet-game-line sheet-homebrew">')
    defsel = re.search(r'<select name="attr_defense_select">.*?</select>', s, re.S).group(0)
    dcomb = re.search(r'<select name="attr_defensive_combat">.*?</select>', s, re.S).group(0)
    succ = re.search(r'<select name="attr_success_target">.*?</select>', s, re.S).group(0)
    num = lambda n, v='0': f'<input type="number" name="attr_{n}" value="{v}" class="sheet-cfg-num" />'
    eras = ''.join(f'<div class="sheet-cfg-flag">{_flag(s, n)}</div>' for n in ('archery_era', 'ride_era', 'enigmas_era'))
    out = ['<div class="sheet-page sheet-settings">', '<div class="sheet-config-title">CONFIG</div>', '<div class="sheet-cfg-grid">']
    out.append(card('splat', 'Game Line', pills, 'sheet-cfg-wide', 'Chronicles of Darkness 2nd Edition game lines'))
    out.append(card('splatopt', 'Splat Options',
        '<div class="sheet-game-line sheet-werewolf2 sheet-urkhar-cfg">' + sw('urkhar_enabled', "Ur'Khar (Shunned Form)", "Optional rule: adds the Ur'Khar column to Forms and a Shunned Form pill") + '</div>'
        + '<span class="sheet-game-line sheet-changeling2">' + row('Bonus Clarity', num('bonus_moralhealth'), 'Extra Clarity boxes') + '</span>'
        + '<span class="sheet-game-line sheet-deviant-the-renegades">' + row('Bonus Stability', num('bonus_moralhealth'), 'Extra Stability boxes') + '</span>'
        + '<div class="sheet-cfg-flag sheet-deviant-the-renegades-inverse">' + _flag(s, 'vitae_counter') + '</div>'
        + homebrew.replace('<div class="sheet-subheader">Homebrew Labels</div>', '<div class="sheet-cfg-sub">Homebrew labels</div>').replace('<div class="sheet-spacer"></div>', ''),
        '', 'Options for the current game line'))
    out.append(card('rules', 'Rules Options',
        sw('allow_over5', 'Attribute dots 6+', 'Show Attribute dots 6 to 10 (Mortal / Hunter)')
        + '<div class="sheet-cfg-flag">' + _flag(s, 'enable_profession') + '</div>'
        + '<div class="sheet-organization-inverse">'
        + row('Defense', defsel, 'Which traits make up Defense')
        + row('Base Size', num('base_size', '5'), 'Size before Giant / Small-Framed')
        + row('Species factor', num('species_factor', '5'), 'Added to Speed (5 for humans)')
        + row('Bonus Health', num('bonus_health'), 'Extra Health boxes')
        + row('Bonus Willpower', num('bonus_willpower'), 'Extra Willpower dots')
        + '</div>', '', 'House and optional rules'))
    out.append(card('eras', 'Dark Eras', eras, '', 'Dark Eras 2 skill swaps: each toggle replaces a modern skill on the Main tab'))
    out.append(card('merits', 'Merit Effects',
        sw('merit_auto', 'Auto-detect from Merits', 'Read Fleet of Foot, Fast Reflexes, Iron Stamina, Giant, Small-Framed, Hardy and Defensive Combat from the Merits list', True)
        + '<div class="sheet-organization-inverse">'
        + row('Fleet of Foot', num('fleet_of_foot'), 'Adds to Speed')
        + row('Fast Reflexes', num('fast_reflexes'), 'Adds to Initiative')
        + row('Iron Stamina', num('iron_stamina'), 'Offsets wound penalties')
        + row('Hardy', num('hardy_override'), 'Reminder only: situational dice against disease, poison, deprivation and fatigue')
        + row('Defensive Combat', dcomb, 'Swap Athletics in Defense for Brawl or Weaponry')
        + '<div class="sheet-cfg-flags">' + _flag(s, 'giant') + _flag(s, 'small_framed') + '</div>'
        + '</div><span class="sheet-cfg-sum" name="attr_merit_fx_summary"></span>', '', 'Merits that change derived traits'))
    out.append(card('roll', 'Roll &amp; Chat', row('Successes on', succ, 'Applies to every sheet roll. Chance dice succeed only on 10; Again / Rote are in the roll bar')
        + '<input type="hidden" name="attr_rote_reroll" value="7" />', '', 'Dice and chat card options'))
    out.append(card('portrait', 'Portrait &amp; Display',
        row('Portrait URL', '<input type="text" name="attr_portrait_url" placeholder="blank = Roll20 avatar" class="sheet-cfg-url" />', 'Shown beside the dice roller and on Notes; blank uses the Roll20 avatar')
        + sw('dark_mode', 'Dark mode', "Dark sheet theme (independent of Roll20's own switch)", True), '', 'Portrait and theme'))
    out.append('</div></div>')
    return h[:i] + ''.join(out) + h[e:], c

CSS = r'''
/* r7: Config card grid */
.charsheet .sheet-settings .sheet-cfg-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 250px), 1fr)); gap: 10px; padding: 4px 0 10px; align-items: start; grid-auto-flow: row dense; }
.charsheet .sheet-settings .sheet-cfg-card { border: 1px solid var(--accent, #b4743a); border-radius: 8px; background: rgba(0,0,0,0.28); padding: 6px 10px 8px; min-width: 0; box-shadow: 0 1px 6px rgba(0,0,0,0.35); }
.charsheet .sheet-settings .sheet-cfg-wide { grid-column: 1 / -1; }
.charsheet .sheet-settings .sheet-cfg-head { margin: 0 0 6px !important; text-align: center; }
.charsheet .sheet-settings .sheet-cfg-body { display: flex; flex-direction: column; gap: 5px; min-width: 0; }
.charsheet .sheet-settings .sheet-cfg-splat .sheet-splat-select { display: flex; flex-wrap: wrap; gap: 5px; justify-content: center; }
.charsheet .sheet-settings .sheet-cfg-splat .sheet-splat-select button.sheet-toggle { border-radius: 999px !important; padding: 2px 10px !important; font-size: 12px !important; width: auto !important; margin: 0 !important; }
.charsheet .sheet-settings .sheet-cfg-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; min-width: 0; font-size: 13px !important; }
.charsheet .sheet-settings .sheet-cfg-row > span, .charsheet .sheet-settings .sheet-cfg-sw > span:last-child { font-size: 13px !important; }
.charsheet .sheet-settings .sheet-cfg-lbl { flex: 0 0 auto; white-space: nowrap; }
.charsheet .sheet-settings .sheet-cfg-row select { flex: 1 1 auto; min-width: 0; max-width: 170px; width: auto !important; font-size: 12px !important; }
.charsheet .sheet-settings input.sheet-cfg-num { width: 52px !important; min-width: 52px !important; text-align: center; }
.charsheet .sheet-settings input.sheet-cfg-url { flex: 1 1 auto; min-width: 0; width: auto !important; font-size: 12px !important; }
.charsheet .sheet-settings .sheet-cfg-sw { display: flex; align-items: center; gap: 7px; cursor: pointer; font-size: 12px; position: relative; }
.charsheet .sheet-settings .sheet-cfg-sw input[type="checkbox"] { position: absolute; opacity: 0; width: 30px; height: 16px; margin: 0; cursor: pointer; z-index: 1; }
.charsheet.charsheet .sheet-settings.sheet-settings span.sheet-cfg-knob.sheet-cfg-knob { flex: 0 0 30px; height: 16px; border-radius: 999px; background: #555 !important; border: 1px solid #888; display: inline-block !important; position: relative; transition: background 0.15s; }
.charsheet.charsheet .sheet-settings.sheet-settings span.sheet-cfg-knob.sheet-cfg-knob::after { content: ""; position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 50%; background: #ddd !important; transition: left 0.15s; }
.charsheet.charsheet .sheet-settings.sheet-settings .sheet-cfg-sw input[type="checkbox"]:checked + span.sheet-cfg-knob.sheet-cfg-knob { background: #b4743a !important; border-color: #e0a060; }
.charsheet.charsheet .sheet-settings.sheet-settings .sheet-cfg-sw input[type="checkbox"]:checked + span.sheet-cfg-knob.sheet-cfg-knob::after { left: 16px; background: #fff !important; }
.charsheet .sheet-settings .sheet-cfg-flag .sheet-checkbox, .charsheet .sheet-settings .sheet-cfg-flags .sheet-checkbox { display: inline-flex; align-items: center; }
.charsheet .sheet-settings .sheet-cfg-flag button.sheet-toggle, .charsheet .sheet-settings .sheet-cfg-flags button.sheet-toggle { border-radius: 999px !important; padding: 1px 9px !important; font-size: 12px !important; white-space: normal; text-align: left; }
.charsheet .sheet-settings .sheet-cfg-flags { display: flex; gap: 6px; flex-wrap: wrap; }
.charsheet .sheet-settings .sheet-cfg-sub { font-size: 11px; font-weight: bold; opacity: 0.8; margin-top: 4px; }
.charsheet .sheet-settings .sheet-cfg-splatopt .sheet-homebrew > div { display: flex; justify-content: space-between; gap: 6px; font-size: 12px; }
.charsheet .sheet-settings .sheet-cfg-splatopt .sheet-homebrew input { min-width: 0; width: 120px !important; }
.charsheet .sheet-settings .sheet-cfg-sum { font-size: 11px; opacity: 0.8; }
.charsheet .sheet-settings .sheet-cfg-sum:empty { display: none; }
'''
