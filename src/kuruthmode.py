"""Death Rage (Basu-Im) mode: set by a failed Wasu-Im roll, cleared by End Death Rage."""
import re
OK = ['athletics', 'brawl', 'intimidation', 'stealth', 'survival']  # instinctive Skills kept usable (flagged: verify vs W:tF 2E)
ALL = ['academics', 'computer', 'crafts', 'investigation', 'medicine', 'occult', 'politics', 'science', 'athletics', 'brawl', 'drive', 'firearms', 'larceny', 'stealth', 'survival', 'weaponry', 'animalken', 'empathy', 'expression', 'intimidation', 'persuasion', 'socialize', 'streetwise', 'subterfuge']
RULES = ('<div class="sheet-km-rules"><b>Death Rage mode (Basu-Im)</b><br/>'
         'Entered automatically when Wasu-Im! fails. The sheet shifts to Gauru (or Ur&#39;Khar if the Form of the Firstborn toggle is on), turns red, '
         'and dims what Kuruth does not allow: in the Death Rage the werewolf attacks the nearest target each turn, cannot take social, mental or complex actions, and acts on instinct. '
         'Kept usable: Brawl, Athletics, Intimidation, Stealth, Survival, attacks and the dice roller (the instinctive Skill list is a best reading, not checked against the W:tF 2E book; verify). '
         'The Rage lasts until the scene ends, the werewolf drops unconscious, or nothing is left to attack; press End Death Rage then.</div>')
def apply(h, c):
    m = re.search(r'<input type="hidden" class="sheet-type"[^>]*>', h)
    h = h[:m.end()] + '<input type="hidden" class="sheet-kmode" name="attr_kuruth_active" value="0" /><input type="hidden" name="attr_kuruth_prev_form" value="" />' + h[m.end():]
    ban = ('<div class="sheet-km-banner"><span class="sheet-km-title">BASU-IM: Death Rage</span>'
           '<button type="action" class="sheet-km-end" name="act_kuruth_end" title="End the Death Rage and restore the normal sheet (form unchanged)">End Death Rage</button>'
           '<button type="action" class="sheet-km-end sheet-km-rev" name="act_kuruth_end_rev" title="End the Death Rage and return to the form you were in before">End and revert form</button></div>')
    a = h.index('<div class="sheet-page sheet-settings"'); h = h[:a] + ban + h[a:]
    k = h.index('<div class="sheet-kuruth-rolls">'); h = h[:k] + RULES + h[k:]
    # hook the roll result
    old = 'if (!isRe) setAttrs({rr_last_mac: mac, rr_last_expr: ex, rr_last_id: String(r.rollId), rr_used: ""}, {silent: true});'
    assert old in h
    h = h.replace(old, old + ' if (/\\{\\{kind=Death Rage\\}\\}/.test(mac) && /\\{\\{name=Wasu-Im!\\}\\}/.test(mac) && R.roll && (R.roll.result || 0) < 1) kuruthEnter();', 1)
    js = r'''
        const kuruthEnter = () => getAttrs(["urkhar_enabled", "form", "kuruth_active"], v => {
            if (v.kuruth_active === "1") return;
            setAttrs({kuruth_active: "1", kuruth_prev_form: v.form || "hishu", form: v.urkhar_enabled === "1" ? "urkhar" : "gauru"});
        });
        on("clicked:kuruth_end", () => setAttrs({kuruth_active: "0"}));
        on("clicked:kuruth_end_rev", () => getAttrs(["kuruth_prev_form"], v => setAttrs({kuruth_active: "0", form: v.kuruth_prev_form || "hishu"})));
        on("sheet:opened change:sheettype", () => getAttrs(["sheettype", "kuruth_active"], v => { if (v.sheettype !== "werewolf2" && v.kuruth_active === "1") setAttrs({kuruth_active: "0"}); }));
'''
    i = h.rfind('</script>'); h = h[:i] + js + h[i:]
    K = '.charsheet input.sheet-kmode[value="1"]'
    dim = 'opacity: .22 !important; pointer-events: none !important; filter: grayscale(1);'
    c += (f'\n.charsheet .sheet-km-banner {{ display: none; }}\n'
          f'{K} ~ .sheet-km-banner {{ display: flex !important; align-items: center; justify-content: center; gap: 10px; flex-wrap: wrap; margin: 4px 6px; padding: 6px 10px; '
          'background: linear-gradient(90deg, #4a0b0b, #8e1616, #4a0b0b); border: 2px solid #e03a2f; border-radius: 6px; box-shadow: 0 0 14px rgba(224,58,47,.55); color: #fff; }\n'
          f'{K} ~ .sheet-km-banner .sheet-km-title {{ font-size: 18px; font-weight: bold; letter-spacing: 2px; text-shadow: 0 0 6px #000; }}\n'
          f'.charsheet.charsheet .sheet-km-banner button.sheet-km-end {{ background: #fff !important; color: #8e1616 !important; border: 1px solid #fff !important; border-radius: 4px; padding: 3px 12px !important; font-weight: bold; height: auto !important; width: auto !important; }}\n'
          f'.charsheet.charsheet .sheet-km-banner button.sheet-km-rev {{ background: rgba(0,0,0,0) !important; color: #fff !important; }}\n'
          f'{K} ~ * {{ --km: 1; }}\n'
          f'{K} ~ .sheet-page {{ box-shadow: inset 0 0 40px rgba(200,30,30,.35); background-color: rgba(120,0,0,.12); }}\n'
          f'{K} ~ .sheet-page .sheet-subheader, {K} ~ .sheet-page .sheet-header, {K} ~ .sheet-page h1, {K} ~ .sheet-page h2, {K} ~ .sheet-page h3 {{ color: #ff5a4a !important; border-color: #c0302a !important; text-shadow: 0 0 6px rgba(224,58,47,.6); }}\n'
          f'{K} ~ .sheet-page .sheet-midtabs {{ border-bottom-color: #c0302a !important; }}\n'
          f'{K} ~ .sheet-page .sheet-dots button.sheet-dot {{ border-color: #c0302a !important; }}\n'
          f'.charsheet .sheet-km-rules {{ margin: 4px 0 8px; padding: 6px 8px; border: 1px solid #c0302a; border-radius: 4px; background: rgba(140,20,20,.15); font-size: 12px; line-height: 1.35; }}\n')
    no = [s for s in ALL if s not in OK]
    c += ', '.join(f'{K} ~ .sheet-page div:has(+ div.sheet-dots > input[name="attr_{s}"]), {K} ~ .sheet-page div.sheet-dots:has(> input[name="attr_{s}"])' for s in no) + f' {{ {dim} }}\n'
    c += (f'{K} ~ .sheet-page button.sheet-mt-merits, {K} ~ .sheet-page button.sheet-mt-gear, {K} ~ .sheet-page .sheet-midpane.sheet-mp-gear, '
          f'{K} ~ .sheet-page .sheet-rollcontainer select, {K} ~ .sheet-page input.sheet-midtab[value="merits"] ~ .sheet-midtabs + .sheet-columns {{ {dim} }}\n')
    return h, c
