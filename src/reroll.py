"""Generic WP reroll: every dice roll button ({{roll=[[ ... ]]}}) becomes an action button that runs the SAME macro via one
shared startRoll path, remembers the resolved roll, and the card carries one shared 'Willpower reroll' chat button (act_wp_reroll)."""
import re, html as H, json

def apply(h, c):
    secs = {}
    for m in re.finditer(r'<fieldset class="repeating_([\w-]+)">(.*?)</fieldset>', h, re.S):
        secs.setdefault(m.group(1), set()).update(re.findall(r'name="attr_([\w-]+)"', m.group(2)))
    spans = [(m.start(), m.group(1)) for m in re.finditer(r'<fieldset class="repeating_([\w-]+)">', h)]
    ends = {s: h.find('</fieldset>', s) for s, _ in spans}
    mac = {}; out = []; pos = 0
    for m in re.finditer(r'<button type="roll"([^>]*?)name="roll_([\w-]+)"([^>]*?)value="([^"]*)"([^>]*)>', h):
        v = H.unescape(m.group(4))
        if '{{roll=[[' not in v: continue
        sec = next((sn for s, sn in spans if s < m.start() < ends[s]), None)
        em = re.match(r'/em ([^\n]*)\n', v)
        if em: v = v[em.end():] + ' {{emote=' + em.group(1) + '}}'
        key = m.group(2) if not sec else sec + '|' + m.group(2)
        mac[key] = v
        attrs = (m.group(1) + m.group(3) + m.group(5))
        attrs = re.sub(r'class="([^"]*)"', r'class="\1 sheet-was-roll"', attrs) if 'class="' in attrs else attrs + ' class="sheet-was-roll"'
        out.append(h[pos:m.start()] + f'<button type="action"{attrs.rstrip()} name="act_rr_{m.group(2)}">')
        pos = m.end()
    out.append(h[pos:]); h = ''.join(out)
    import os; os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'build'), exist_ok=True)
    json.dump(mac, open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'build', 'rr_mac.json'), 'w'), indent=0)
    fields = {s: sorted(f) for s, f in secs.items() if any(k.startswith(s + '|') for k in mac)}
    js = r'''
        // ---- generic roll path + Willpower reroll (one shared action) ----
        const RR_MAC = %s, RR_FIELDS = %s;
        const rrStrip = s => { let p; do { p = s; s = s.replace(/\?\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}/g, "0"); } while (s !== p); return s; };
        const rrTag = ' {{reroll=[Willpower reroll +3](~@{character_id}|wp_reroll)}}';
        const rrRun = (mac, isRe) => startRoll(mac + (isRe ? "" : rrTag), (r) => {
            const R = r.results || {}; const ex = R.roll ? R.roll.expression : "";
            if (!isRe) setAttrs({rr_last_mac: mac, rr_last_expr: ex, rr_last_id: String(r.rollId), rr_used: ""}, {silent: true});
            finishRoll(r.rollId);
        });
        Object.keys(RR_MAC).forEach((k) => {
            const [sec, nm] = k.includes("|") ? k.split("|") : [null, k];
            on(`clicked:${sec ? "repeating_" + sec + ":" : ""}rr_${nm}`, (ev) => {
                let mac = RR_MAC[k];
                if (sec) {
                    const mm = (ev.sourceAttribute || ev.triggerName || "").match(new RegExp("repeating_" + sec.replace(/[-]/g, "\\-") + "_([^_]+)_", "i"));
                    const id = mm ? mm[1] : "";
                    const F = RR_FIELDS[sec] || [];
                    mac = mac.replace(/@\{([\w-]+)\}/g, (a, n) => F.includes(n) ? `@{repeating_${sec}_${id}_${n}}` : a);
                }
                rrRun(mac, false);
            });
        });
        on("clicked:wp_reroll", () => getAttrs(["rr_last_mac", "rr_last_expr", "rr_last_id", "rr_used", "willpower"].concat(Array.from({length: 20}, (_, i) => `willpower_box${i + 1}`)), (v) => {
            const max = Math.min(20, parseInt(v.willpower, 10) || 0); let free = 0, first = 0;
            for (let i = 1; i <= max; i++) if (!["1", "on"].includes(v[`willpower_box${i}`])) { free++; if (!first) first = i; }
            const head = "&{template:cofd-entry} {{charname=@{character_name}}} {{kind=Willpower reroll}} ";
            if (!v.rr_last_mac || !v.rr_last_expr) return startRoll(head + "{{name=Nothing to reroll}} {{f_short=Roll something first.}}", r => finishRoll(r.rollId));
            if (v.rr_used === v.rr_last_id) return startRoll(head + "{{name=Already rerolled}} {{f_short=Willpower was already spent to reroll this roll.}}", r => finishRoll(r.rollId));
            if (!free) return startRoll(head + `{{name=No Willpower left}} {{f_short=WP 0/${max}: cannot reroll.}}`, r => finishRoll(r.rollId));
            const ex = v.rr_last_expr.includes("))d10") ? v.rr_last_expr.replace("))d10", "+3))d10") : v.rr_last_expr.replace(/(\d+)d10/, (a, n) => `${parseInt(n, 10) + 3}d10`);
            let mac = rrStrip(v.rr_last_mac.replace(/\{\{roll=\[\[[\s\S]*$/, "").replace(/\{\{(f_mod|f_wounds|reroll)=[^}]*\}\}/g, ""));
            mac += ` {{roll=[[${ex}]]}} {{wpspend=1}} {{wpst=Willpower reroll: +3 dice, WP ${free - 1}/${max}}}`;
            setAttrs({[`willpower_box${first}`]: "1", rr_used: v.rr_last_id});
            rrRun(mac.replace(/\{\{kind=[^}]*\}\}/, "{{kind=Willpower reroll (+3)}}"), true);
        }));
''' % (json.dumps(mac), json.dumps(fields))
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    h = h.replace('</div>\n    <!--RR-->', '', 1)
    # hidden action + state attrs (top level)
    h = h.replace('<div class="sheet-rollcontainer">', '<button type="action" name="act_wp_reroll" class="sheet-hidden-act" title="Willpower reroll (+3 dice) of your last roll"></button>'
                  '<input type="hidden" name="attr_rr_last_mac" value="" /><input type="hidden" name="attr_rr_last_expr" value="" /><input type="hidden" name="attr_rr_last_id" value="" /><input type="hidden" name="attr_rr_used" value="" />'
                  '<div class="sheet-rollcontainer">', 1)
    # template: emote line, reroll button, WP status
    t = '{{#roll}}<div class="sheet-ce-roll">'
    assert t in h
    h = h.replace(t, '{{#emote}}<div class="sheet-ce-emote">{{emote}}</div>{{/emote}}{{#wpst}}<div class="sheet-ce-wpst">{{wpst}}</div>{{/wpst}}' + t, 1)
    h = re.sub(r'(<rolltemplate class="sheet-rolltemplate-cofd-entry">.*?)(\s*</div>\s*</rolltemplate>)', lambda m: m.group(1) + '{{#reroll}}<div class="sheet-ce-reroll">{{reroll}}</div>{{/reroll}}' + m.group(2), h, count=1, flags=re.S)
    c = re.sub(r'button\[type="?roll"?\]', ':is(button[type="roll"], button.sheet-was-roll)', c)
    c += ('\n.charsheet button.sheet-hidden-act { display: none !important; }'
          '\n.sheet-rolltemplate-cofd-entry .sheet-ce-reroll { text-align: center; margin: 4px 0 2px; }'
          '\n.sheet-rolltemplate-cofd-entry .sheet-ce-reroll a { display: inline-block; padding: 2px 10px; border-radius: 999px; border: 1px solid #b0542a; background: #3a1c10; color: #f3d9b8; font-size: 12px; }'
          '\n.sheet-rolltemplate-cofd-entry .sheet-ce-emote { font-style: italic; text-align: center; margin: 2px 0 4px; opacity: .9; }'
          '\n.sheet-rolltemplate-cofd-entry .sheet-ce-wpst { text-align: center; font-size: 11px; font-weight: bold; color: #e0a060; }\n')
    return h, c, len(mac)
