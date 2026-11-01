"""Vampire: Clan/Covenant dropdowns and an auto Banes panel (VtR 2E, verified pp.102-106 of vtr2e.txt)."""
import json
CLANS = {
 'Daeva': ('The Wanton Curse', "On the second and later drinks from the same mortal, roll Humanity ({hum} dice). Failure: Persistent Dependent Condition toward that mortal (ends only with the mortal's death)."),
 'Gangrel': ('The Feral Curse', "All dice pools to resist frenzy are capped at Humanity ({hum}). Does not affect riding the wave."),
 'Mekhet': ('The Tenebrous Curse', "Gains one bane at Humanity 6 that is not tied to a breaking point (it counts toward the 3-bane limit). Treat Humanity as one lower ({hum1}) for all Humanity-based banes, including sunlight and torpor."),
 'Nosferatu': ('The Lonely Curse', "With humans (not Touchstones or Kindred), treat Humanity as two lower ({hum2}) for Social penalties, and Presence or Manipulation failures become dramatic failures."),
 'Ventrue': ('The Aloof Curse', "The first Touchstone is tied to Humanity 7, so the first Humanity loss detaches it. Further Touchstones go on dots 6 to 2."),
}
COVENANTS = ['Carthian Movement', 'Circle of the Crone', 'Invictus', 'Lancea et Sanctum', 'Ordo Dracul', 'Unaligned']
def header(h):
    co = '<option value="">—</option>' + ''.join(f'<option value="{c}">{c}</option>' for c in CLANS)
    h = h.replace('<select class="game-line werewolf2 wolf-sel" name="attr_auspice">', f'<select class="game-line vampire2 vamp-sel" name="attr_clan">{co}</select><select class="game-line werewolf2 wolf-sel" name="attr_auspice">', 1)
    vo = '<option value="">—</option>' + ''.join(f'<option value="{c}">{c}</option>' for c in COVENANTS)
    a = '<input type="text" name="attr_GroupName">'
    assert a in h
    h = h.replace(a, f'<span class="wolf-hdr-wrap vamp-cov"><input type="text" class="vamp-generic" name="attr_GroupName"><select class="game-line vampire2 vamp-sel" name="attr_covenant">{vo}</select></span>', 1)
    return h
def page(h):
    block = '''<div class="game-line vampire2 vamp-banes">
  <div class="entry-section-head"><span class="subheader">Banes (automatic)</span></div>
  <div class="vb-row"><b>Clan Bane: </b><span name="attr_bane_clan_name"></span>
   <button type="roll" class="mini" name="roll_bane_clan" value="&amp;{template:cofd-entry} {{charname=@{character_name}}} {{gl_vampire=1}} {{kind=Clan Bane}} {{name=@{bane_clan_name}}} {{f_description=@{bane_clan_text}}}">💬</button>
   <div class="vb-t"><span name="attr_bane_clan_text"></span></div></div>
  <div class="vb-row"><b>Sunlight: </b><span name="attr_bane_sun"></span>
   <button type="roll" class="mini" name="roll_bane_sun" value="&amp;{template:cofd-entry} {{charname=@{character_name}}} {{gl_vampire=1}} {{kind=Bane}} {{name=Sunlight}} {{f_description=@{bane_sun}}}">💬</button></div>
  <div class="vb-row"><b>Personal banes: </b><span name="attr_bane_note"></span></div>
</div>
'''
    a = '<div class="entry-section banes">'
    assert a in h
    return h.replace(a, block + a, 1)
JS = r'''
        const CLAN_BANE = %s;
        const SUN = h => h >= 7 ? "1 lethal" : h == 6 ? "2 lethal" : h == 5 ? "3 lethal" : h == 4 ? "1 aggravated" : h == 3 ? "2 aggravated" : h == 2 ? "3 aggravated" : h == 1 ? "4 aggravated" : "5 aggravated";
        const FREQ = bp => bp <= 0 ? "no damage (BP 0)" : bp <= 2 ? "every ten minutes" : bp == 3 ? "every minute" : bp <= 5 ? "every turn" : bp <= 7 ? "2x per turn" : bp <= 9 ? "3x per turn" : "5x per turn";
        const updBanes = () => getAttrs(["clan","morality","power","sheettype"], v => {
            if (v.sheettype !== "vampire2") return;
            const hum = parseInt(v.morality) || 0, bp = parseInt(v.power) || 0, c = CLAN_BANE[v.clan];
            const eff = v.clan === "Mekhet" ? hum - 1 : hum;
            const active = hum <= 6;
            let name = c ? c[0] : "Choose a Clan on Main", txt = "";
            if (c) txt = (active ? "" : "(Not active yet: clan banes take hold at Humanity 6 and stay once gained.) ") + c[1].replace("{hum}", hum).replace("{hum1}", hum - 1).replace("{hum2}", hum - 2);
            const n = Math.max(0, 10 - hum);
            setAttrs({bane_clan_name: name, bane_clan_text: txt,
              bane_sun: `${SUN(eff)} damage ${FREQ(bp)} (Humanity ${eff}${v.clan === "Mekhet" ? " (Mekhet: one lower)" : ""}, Blood Potency ${bp}). Resilience does not reduce it; with only the eyes exposed, treat Blood Potency as one lower.`,
              bane_note: `Max 3. Each gives -1 to detachment rolls. Taking a bane on Humanity loss gives a Beat and closes that breaking point. Common scaling: (10 - Humanity) = ${n}, Humanity cap = ${hum}. A frenzy caused by a bane can't be resisted with more dice than Humanity (${hum}).`}, {silent: true});
        });
        on("sheet:opened change:clan change:morality change:power change:sheettype", updBanes);
''' % json.dumps(CLANS)
CSS = '''
.sheet-vamp-banes { border: 1px solid var(--temp-dot,#6e1e1e); border-radius: 8px; padding: 6px 10px; margin: 6px 0 10px; background: rgba(110,30,30,.08); font-size: 12px; }
.sheet-vb-row { margin: 3px 0; } .sheet-vb-t { font-size: 12px; margin: 2px 0 0 10px; opacity: .9; }
.sheet-darkmode .sheet-vamp-banes { border-color: #c04848; background: rgba(192,72,72,.10); }
input.sheet-game-line[value="vampire"] ~ * .sheet-wolf-hdr-wrap input.sheet-wolf-generic, input.sheet-game-line[value="vampire"] ~ * .sheet-vamp-cov input.sheet-vamp-generic { display: none; }
select.sheet-vamp-sel { width: 100%; }
'''
