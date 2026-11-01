# CofD 2E multi-splat Roll20 sheet: build report

**Base:** Roll20 community "Chronicles of Darkness" sheet (https://github.com/Roll20/roll20-character-sheets/tree/master/Chronicles%20of%20Darkness), commit 0cdae85d.
- MIT licence, © Roll20 2014–2018.
- Authors: Steve K., Shawn G., Natha, Primal Zed, Constantine F., Adolfo Domingues. Credits are kept in CREDITS-base-README.md.

**Outputs:** sheet.html, sheet.css, translation.json, preview.html (local preview shim only), vince_values.json, shots/*.png. Regenerate with `src/build.py` followed by `src/preview_build.py`.

**IMG_BASE:** `https://example.com/cofd-roll20/img`. Upload img/ to an https host and change IMG_BASE in src/build.py.

## Splats (Settings ⚙ → selector)
- Mortal, Hunter, Vampire, Werewolf
- Mage, Promethean, Changeling, Geist, Mummy, Demon, Beast, Deviant
- Werewolf: Changing Breeds (new `breeds2` type; game_line werewolf)

Every splat gets its PDF background, logo and temp-dot colour (src/splat_colors.json, sampled from the header art).

## Features
- **Repeating entries:** gear expand/collapse, 💬 post to chat, 🎲 roll, expand-all/collapse-all, ▲▼ reorder and 🗑 delete.
- **Dice:** inline roll bar, Perception button, splat quick buttons, and a choice of 8+ or 7+ successes.
- **Conditions & Tilts:** toggle grid. Automatic modifiers feed into rolls.
- **Specialties:** per-skill caret, with an optional +1.
- **Weapons:** auto-built attack macro.
- **Notes:** repeating notes on "Page 2". The old page-2 custom rolls are now repeating entries.
- **Forms tab (Werewolf/Breeds):**
  - Form picker, with an optional Ur'Khar form. The house-rule Gauru is +2 Str/+3 Spd; the book Gauru is +3/+4.
  - The worker updates temp dots (in the splat colour) and Size/Speed/Defense/Init/Health/Perception.
- **Attribute tracks:** 10 dots for supernatural splats. Mortal and Hunter show 5, plus a Settings toggle for 6+.
- **Details tab:**
  - Portrait, physical details, appearance/history/goals/aspirations/possessions.
  - Vampire Embrace/sire, Werewolf First Change, Hunter profession/cell.
  - Per-form height and weight (the Ur'Khar column only appears when enabled). The active form's height and weight also show on page 1.
- **Outcome fields:** every rollable entry has Dramatic Failure / Failure / Success / Exceptional text. The roll template shows only the one that matches the result:
  - chance die rolls a 1 (rollWasFumble + chance flag) → Dramatic Failure
  - 0 successes → Failure
  - 1–4 → Success
  - 5+ → Exceptional
- **Willpower:**
  - "Spend 1 WP (+3)" works for every splat.
  - Hunter also gets "Risk WP" (HtV 2E p.132) with two benefit selects:
    - +3 dice is added to the pool.
    - 9-again changes the roll.
    - Exceptional on 3 changes the template threshold.
    - +1 weapon damage, removing an opponent's 10-again, and Tactic (counts as both benefits) appear as text.
  - The template shows the book consequences:
    - Success: +1 Beat; regain the risked WP +1.
    - Failure: dramatic failure effects, +2 Beats; the WP stays spent.

## Caveats
- Custom sheets need a Roll20 Pro account.
- WP spend/risk checkboxes must be unticked by hand after a roll, and WP is not deducted automatically. A Roll20 roll button can't run a worker, so doing this would need a startRoll rewrite.
- Benefit eligibility (once per scene, no Perception/Endowment rolls) is the player's responsibility.
- Base-template (wod) rolls also get the WP dice, but not the outcome or risk text.
- `<img name="attr_portrait_url">`, `:has()` (active form highlight) and datalist depend on Roll20 support. Everything degrades gracefully without them.
- A query modifier can push the pool below 0 without turning it into a chance die. Weapon damage is shown as text.
- Automatic condition modifiers are limited to universal ones.
- Breeds custom forms are not stat-driven (it uses the Werewolf form table). Phase-2 PDF-specific trackers beyond what the base sheet already has (e.g. Mage Nimbus, Geist Haunts detail) are covered by repeating entries rather than bespoke layouts.
- 1E code from the base sheet is still present.
- The preview shim does not evaluate autocalc. It now ignores no-op attribute changes, as Roll20 does.

## Update: roller panel, chat cards, dark mode, pool labels
- Roller panel: a compact themed panel. Sheet/Attack/Simple and the again options are segmented toggles, and WP spend/risk are checkbox pills. The two Benefit selects are aligned, and the active state uses the splat colour.
- Chat card (cofd-entry):
  - Splat colour band and a header with character name, kind and roll name.
  - B/L/A damage badge, pool breakdown table and a large success count.
  - Coloured outcome banner and outcome text.
  - Supports Roll20 dark mode (`.sheet-rolltemplate-darkmode`).
  - Perception now uses this card.
- Sheet dark mode is supported via `.sheet-darkmode`. preview.html renders dark by default; add `?dark=0` for light.
- Weapon pools are capitalised: "Auto (by Type)", "Strength 3 + Weaponry 2 = 5", and so on.
- Sample cards: cards-dark.html and cards-light.html (built by src/cards_build.py).

## Update: dark frames and skill markers
- Dark mode shows each splat's own frame art (the 13 `*-bg.jpg` files), inverted and dimmed with `filter: invert hue-rotate brightness(.55)`. The Mortal and Geist logos on white boxes are inverted. A near-white scan finds only the logos.
- Skill markers come from `src/markers.py` (the MARKS dict). Each Skill has:
  - a diamond mark in the splat colour;
  - a roll-quality badge: none, 9, 8 or ⊘ (no 10-again).
  - Werewolf also gets an MK (Moon-Kissed) checkbox per Skill and an "Auspice moon visible" toggle on the roller.
- Rolling: the best quality among the selected Skills is combined with the roller's choice, and the chat card shows "Skill quality: …". Moon-Kissed means 9-again (8-again if 9-again is already on), and +4 instead of +3 for Willpower while the moon is visible.
- Checked against the books: HtV 2E Professional Training (Asset Skills; 9-again at ••; The Routine rote at ••••• is shown as text only). WtF 2E Moon-Kissed (p.107) and the auspice Skill table.
- Not checked: the marker names for other splats are placeholders, and no automatic effects are applied for them.

## Update: Werewolf Auspice/Tribe and frame slicing
- Page 1 Auspice and Tribe are dropdowns on Werewolf. Choosing an Auspice ticks its Auspice Skills automatically.
- The Powers page has an Auspice & Moon Gift block: moon-phase SVG, Auspice Ability text with a 💬 post-to-chat button, Moon Gift dots, a Facets field with 💬, the moon's Facet list and the Tribe's Gift affinities.
- Checked against WtF 2E: Auspice Skills, Renown, Gift affinities, the Auspice Benefit text (summarised) and the Gift affinities for Blood Talons, Bone Shadows, Hunters in Darkness, Storm Lords and Ghost Wolves.
- Not checked: Moon Gift Facet names, the Iron Masters affinities, and the Pure tribes' affinities.
- Frames are now 3 slices per splat: `*-bgtop.jpg`, `*-bgmid.jpg` repeated, and `*-bgbot.jpg` pinned to the bottom, with 150px bottom padding, so the frame always wraps the content. These new images must be uploaded to IMG_BASE.

## Update: Vampire Clan/Covenant + auto Banes
- Clan (attr_clan) and Covenant (attr_covenant) are now dropdowns on vampire2. The old free-text inputs are hidden on vampire.
- Banes (automatic) panel on the Powers page sits above the repeating Banes section. That section is kept: expandable, post to chat.
  - Clan Bane name + text, scaled by Humanity, active from Humanity 6.
  - Sunlight damage from Humanity and frequency from Blood Potency (attr_power). Mekhet use Humanity −1.
  - Personal-bane rules: max 3, −1 to detachment, frenzy caps.
- Recomputes on clan/morality/power change. Every line was checked against vtr2e.txt (book pp. 102 and 105–106).
- Torpor duration is not included.
