"""r9: header Virtue/Vice equivalents as per-splat drop-downs (book example lists + Custom). Lists not checked against the books (no PDFs on the box)."""
import re
CV = ['Ambitious', 'Courageous', 'Generous', 'Honest', 'Hopeful', 'Humble', 'Just', 'Loving', 'Loyal', 'Patient', 'Peaceful', 'Righteous', 'Trustworthy']
CC = ['Ambitious', 'Arrogant', 'Competitive', 'Corrupt', 'Cowardly', 'Cruel', 'Deceitful', 'Dogmatic', 'Greedy', 'Hasty', 'Hateful', 'Pessimistic']
MASK = ['Authoritarian', 'Child', 'Competitor', 'Conformist', 'Conspirator', 'Courtesan', 'Cult Leader', 'Deviant', 'Follower', 'Guru', 'Idealist', 'Jester', 'Junkie', 'Martyr', 'Masochist', 'Monster', 'Nomad', 'Nurturer', 'Perfectionist', 'Penitent', 'Questioner', 'Rebel', 'Scholar', 'Social Chameleon', 'Spy', 'Survivor', 'Visionary']
BLOOD = ['Alpha', 'Challenger', 'Destroyer', 'Fox', 'Lone Wolf', 'Monster', 'Reaver', 'Soldier', 'Survivor', 'Thief']
BONE = ['Community Organizer', 'Cub', 'Destroyer', 'Free Spirit', 'Guardian', 'Hedonist', 'Philosopher', 'Seeker', 'Teacher', 'Traditionalist', 'Trickster', 'Visionary']
NEEDLE = ['Bon Vivant', 'Chess Master', 'Commander', 'Composer', 'Dancer', 'Daredevil', 'Eavesdropper', 'Mentor', 'Protector', 'Scholar']
THREAD = ['Acceptance', 'Anger', 'Ambition', 'Duty', 'Family', 'Friendship', 'Love', 'Revenge']
L = {  # type: (virtue-slot list, vice-slot list)
    'mortal2': (CV, CC), 'mage2': (CV, CC), 'hunter2': (CV, CC), 'breeds2': (CV, CC), 'demon': (CV, CC),
    'vampire2': (MASK, MASK), 'werewolf2': (BLOOD, BONE), 'changeling2': (NEEDLE, THREAD)}
def sel(attr, t, opts):
    o = '<option value="">-</option>' + ''.join(f'<option value="{x}">{x}</option>' for x in opts) + '<option value="custom">Custom / other...</option>'
    return f'<select class="sheet-vv-sel sheet-vv-{t}" name="attr_{attr}_pick" title="Book examples (lists not checked against the book; verify) or Custom">{o}</select>'
def apply(h, c):
    for attr, k in (('Virtue', 0), ('Vice', 1)):
        old = f'<input type="text" name="attr_{attr}">'
        assert h.count(old) == 1, attr
        new = (f'<span class="sheet-vv">' + ''.join(sel(attr, t, v[k]) for t, v in L.items())
               + f'<input type="text" class="sheet-vv-txt" name="attr_{attr}" placeholder="other" /></span>')
        h = h.replace(old, new, 1)
    js = 'const VV = ' + repr({t: [v[0], v[1]] for t, v in L.items()}).replace("'", '"') + ';\n'
    js += r'''        ["Virtue", "Vice"].forEach((a, k) => {
            on(`change:${a}_pick`, (e) => { if (e.sourceType !== "player") return; const p = e.newValue || ""; if (p !== "custom") setAttrs({[a]: p}); });
        });
        // keep the picker in step with the text (non-destructive: unknown text stays and the picker shows Custom)
        const vvSync = () => getAttrs(["sheettype", "Virtue", "Vice", "Virtue_pick", "Vice_pick"], v => {
            const lst = VV[v.sheettype]; if (!lst) return; const u = {};
            ["Virtue", "Vice"].forEach((a, k) => { const t = v[a] || ""; const want = !t ? (v[a + "_pick"] === "custom" ? "custom" : "") : (lst[k].includes(t) ? t : "custom");
                if (v[a + "_pick"] !== want) u[a + "_pick"] = want; });
            if (Object.keys(u).length) setAttrs(u, {silent: true});
        });
        on("sheet:opened change:sheettype change:virtue change:vice", vvSync);
'''
    i = h.rfind('</script>'); h = h[:i] + '        ' + js + h[i:]
    c += '\n.charsheet .sheet-vv { display: flex; gap: 4px; align-items: center; min-width: 0; }\n.charsheet.charsheet .sheet-vv select.sheet-vv-sel { display: none; flex: 0 1 auto; min-width: 0; max-width: 100%; height: 22px; padding: 0 2px; }\n.charsheet.charsheet .sheet-vv input.sheet-vv-txt { flex: 1 1 60px; min-width: 0; }\n'
    for t in L:
        c += f'.charsheet.charsheet input.sheet-type[value="{t}"] ~ * .sheet-vv select.sheet-vv-{t} {{ display: block !important; flex: 1 1 auto; }}\n'
        # text box only when Custom is picked: the picker sits before the text; we cannot read select state in CSS, so shrink it
        c += f'.charsheet.charsheet input.sheet-type[value="{t}"] ~ * .sheet-vv input.sheet-vv-txt {{ flex: 0 1 70px !important; }}\n'
    return h, c
