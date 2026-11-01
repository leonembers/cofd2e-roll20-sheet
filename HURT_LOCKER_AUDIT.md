# Hurt Locker (CofD 2E, Onyx Path) — Weapons/Attacks audit of our Roll20 sheet

Status: PROPOSAL ONLY. No sheet files edited, nothing rebuilt (live test in progress).

## Sources
- **Authoritative:** `/workspace/cofd/books/HL.pdf` (full book) / `HL.txt` (pdftotext -layout). Page refs below are
  **PDF page (printed page)**, e.g. `p.135 (134)`. Check with `pdftotext -f N -l N -layout HL.pdf -`.
  `/workspace/cofd/books/hurtlocker/N.txt` is the same text split per PDF page.
- The user's Drive extract (`agent-tools/62afebf6-…txt`, 100 KB) only covers the opening chapters (groups/intro);
  it has **none** of the equipment rules (no Piercing/Knockdown/range band text). Not used for weapon rules.
- Web sources: not needed; superseded by the full PDF.
- Legend: **[HL]** = confirmed in Hurt Locker text; **[core]** = CofD 2E core rule, not restated in HL (inferred, verify);
  **[?]** = garbled/ambiguous in the PDF table.

## 1. Rules summary

### 1.1 Stat block fields
**Ranged** (p.135 (134), table + key): Type · Damage · Ranges · Capacity · Initiative · Strength · Size · Availability · Tags · Example.
- Damage: bonus successes added to a *successful* attack. Firearms & bows deal **lethal** unless noted. [HL]
- Range: weapon's **maximum range band**; one band beyond = **chance die**. [HL]
- Capacity: Low / Medium / High / Single Shot — governs bursts and running dry (replaces core "Clip"). [HL p.133 (132)]
- Initiative: penalty while wielded. Strength: min Str; below it **−1** to attack. [HL]
- Size (ranged): 1 = one-handed, pocketable; 2 = two-handed, hide in coat; 3 = two-handed, not concealable. [HL]
- Availability: Resources / Social Merit dots. Tags: special qualities.

**Melee** (p.140 (139) key): Type · Damage · Initiative · Strength · Size · Availability · Tags · Effects.
- "Weapons always deal lethal damage" (exception: whip = bashing unless metal-tipped, then Damage 0 lethal). [HL p.141]
- Two weapons: take the higher Initiative penalty, +1 more. [HL]
- Size: 1 hide in hand; 2 hide in coat; 3+ can't hide. [HL]
- Improvised: as nearest weapon type, −1 Damage and −1 Initiative. Paying +1 Availability can buy +1 Damage, a lower Init
  penalty, or Knockdown/Stun. [HL p.140–141]

**Explosives** (p.136–137 (135–136)): Type · Damage · Initiative · Blast Area · Force · Range · Strength · Size · Availability · Tags.
- Ground zero: Damage as automatic **aggravated**; primary area: automatic **lethal**; secondary (2× diameter): automatic **bashing**.
- Force: rolled as an attack pool, Defense doesn't apply (unless supernatural speed); mundane armor counts **half ballistic**;
  success adds Damage in auto successes. All damaging explosives also inflict **Deafened**. AP applies to primary target only
  (except thermite/WP). Thrown = Str or Dex + Athletics; fired = Dex + Firearms; no Heavy Weapons specialty = −1. [HL]

**Armor** (p.142–143 (141–142)): Rating general/ballistic · Strength · Defense · Speed · Availability · Coverage.
- Apply **ballistic first** (each point downgrades lethal→bashing on firearms), then **general** subtracts from the total,
  most severe first. A successful attack always deals ≥1 bashing to an armored mortal. Str below armor's = −1 Brawl & Weaponry.
  Helmets: half ratings (round up) to head, −1 sight/hearing Perception. [HL]

### 1.2 Tags (p.142–143 (141–142)) [HL, complete list]
| Tag | Effect |
|---|---|
| 8-again | Re-roll 8, 9, 10 |
| 9-again | Re-roll 9, 10 on attack |
| Accurate | +1 to attack rolls (incl. grapple use) |
| Bleed | Doubles weapon bonus for Bleeding Tilt |
| Brawl | Attacks with Brawl, benefits from unarmed boosts, still lethal |
| Concealed | (shields) if not used to attack, +Size to Defense; Size acts as concealment vs ranged |
| Enhance (Skill) | Usually +1 to non-attack rolls of that Skill when usable as a tool |
| Fragile | −1 Durability |
| Grapple | Add weapon bonus to grapple pools |
| Guard | +1 Defense while wielded |
| Inaccurate | −1 attack (stacks with improvised/unskilled) |
| Incendiary | Inflicts Burning Tilt |
| Knockdown | Double weapon bonus for Knockdown Tilt |
| Piercing N | Subtract N from armor (ballistic first, then general) or object Durability (a.k.a. "AP N" in explosive tables) |
| Reach | +1 Defense vs opponents with smaller-Size weapons/unarmed; not in grapple, −1 to grapple actions |
| Slow | Defender gets full Defense — **ranged only** |
| Stun | Double weapon bonus for Stun Tilt |
| Thrown / Thrown (A) | Throwable; (A) = aerodynamic (+1 range band) |
| Two-Handed | Needs two hands; one-handed at Str req +1 |
Note: "Armor-piercing", "Brutal", "Knockdown" as *Tilt*, "Stun" as *Tilt*: Brutal is **not** an HL tag (it's from other lines). Tilts referenced: Knocked Down, Stunned, Bleeding, Burning, Blinded, Deafened, Pinned, Arm Wrack.

### 1.3 Attack pools [HL unless marked]
- Melee: Strength + Weaponry (whip: **Dex** + Weaponry; catchpole Str + Weaponry). [HL]
- Unarmed / Brawl-tagged: Strength + Brawl [core]; unarmed bashing [core].
- Firearms / crossbow / grenade launcher / flamethrower: Dexterity + Firearms. Nail gun unmodified: **Strength + Firearms**, Defense applies. [HL]
- Bows: Dexterity + **Athletics or Firearms** (player's choice); crossbow always Firearms. [HL p.134]
- Thrown: Str **or** Dex + Athletics. [HL p.136] Throw only Size < Strength; base range Close (Str ≤3), Short (Str 4–5), +1 band if (A). [HL p.131]
- Flamethrower: −2 without Heavy Weapons specialty; long burst ignores Defense; armor only if flame-resistant. [HL p.138]
- Bow damage = lower of bow's min Str or archer's Str; Str shortfall penalty doubled; stake: −3, needs 5 damage. [HL p.135]
- Unskilled −1 physical [core]. Specialty +1 [core].

### 1.4 Defense & range bands (p.130–132 (129–131)) [HL]
| Band | Distance | Ranged attack mod | Concealment | Cover |
|---|---|---|---|---|
| Close | ≤5 m | 0; **target gets Defense = gun Size + 1** (can WP +2/Dodge doubles & rolls; successes subtract) | normal | normal |
| Short | 5–30 m | 0; **no Defense** vs firearms | normal | normal |
| Medium | 30–100 m | −1 | −1 worse | normal |
| Long | 100–300 m | −2 | −2 worse | +1 Durability |
| Extreme | 300 m+ | −4 (chance die unless weapon reaches) | −2 worse | +2 Durability |
- Beyond weapon's max band by one: chance die. Melee normally only at Close. Slow tag restores full Defense vs ranged.
- Melee/thrown: target's Defense applies [core].

### 1.5 Capacity, bursts, reload (p.133 (132), p.144 merits) [HL]
| Capacity | Bursts allowed | Runs dry after | On dramatic failure |
|---|---|---|---|
| High | short/medium/long | 1 long, 2 medium, or 3 short | **jams** (Dex + Firearms to fix) |
| Medium | short/medium | 1 medium or 2 short | empties |
| Low | short only | 1 short, or any **failure** | empties |
| Single Shot | none | one use per scene | — |
- Reloads: buy at weapon Availability −1 (last the scene); Wits + Firearms to scavenge; reloading takes an action.
- Trigger Discipline (•, per weapon class): capacity +1 level (High: +1 extra long burst). Loaded for Bear (•/••): 1–2 free reloads.
- Burst **dice bonuses / multi-target rules are not given in HL** → use core [core]: short +1 (one target), medium +2
  (up to 3 targets, −1 per extra), long +3 (any in arc, −1 per extra target). Mark as inferred.
- Revolvers: +1 to fix. Big-game rifles / stand-alone launchers: unbraced recoil → 1 bashing + Knocked Down. [HL]

### 1.6 Sample tables [HL; [?] = PDF table garbled]
**Ranged (p.135 (134))** Dmg / Range / Capacity / Init / Str / Size / Avail / Tags
| Light Pistol | +1 | Long | Med | 0 | 2 | 1 | •• | — |
| Heavy Pistol | +2 | Long | Med | −2 | 3 | 1 | ••• | — |
| Light Revolver [?] | +1 | Medium | Med | "6"? | 0? | 2? | •• | — |
| Heavy Revolver [?] | +2 | "Low"? | Long? | "6"? | −2 | 3 | •• | — |
| SMG small | +1 | Med | High | −2 | 2 | 1 | ••• | — |
| SMG heavy | +2 | Med | High | −3 | 3 | 2 | ••• | — |
| Rifle | +4 | Extreme | Low | −5 | 2 | 3 | •• | — |
| Big Game Rifle | +5 | Extreme | Low | −5 | 3 | 4 | ••••• | Stun (recoil) |
| Assault Rifle | +3 | Long | High | −3 | 3 | 3 | ••• | 9-again |
| Shotgun | +3 | Med | Low | −4 | 3 | 2 | •• | 9-again |
| Short Bow | +2 | Med | Low | −3 | 2 | 3 | •• | — |
| Long Bow | +3 | Med | Low | −4 | 3 | 4 | •• | — |
| Crossbow | +2 | Long | Low | −5 | 3 | 3 | ••• | — |
| Pepper Spray | +0 | Close | Low | 0 | 1 | 1 | • | Slow |
| Stun Gun (ranged) | +0 | Close | Med | −1 | 1 | 1 | • | Slow, Stun; bonus successes don't add damage |
Revolver rows have columns shifted in the PDF (the "6" looks like a stray cylinder count); confirm visually before seeding presets.

**Melee (p.139–140 (138–139))** Dmg / Init / Str / Size / Avail / Tags
Battle Axe +3/−4/3/3/•••/9-again, Two-Handed · Fire Axe +2/−4/3/3/••/9-again, Two-Handed · Great Sword +4/−5/4/3/••••/9-again, Two-Handed ·
Hatchet +1/−2/1/1/•• · Knife small +0/0/1/1/•/Thrown (A) · Knife hunting +1/−1/1/2/••/Enhance Crafts or Survival · Machete +2/−2/2/2/•• ·
Rapier +1/−2/1/2/••/Piercing 1 · Sword +3/−3/2/3/•••/(+1 Durability katana or +1 Init long sword) ·
Brass Knuckles +0/0/1/1/•/Brawl · Metal Club +2/−2/2/2/•/Stun · Nightstick +1/−1/2/2/••/Stun · Nunchaku +1/+1/2/2/••/Stun (−1 Dmg & Init w/o Dex 3) ·
Sap +0/−1/2/2/•/Stun · Sledgehammer +3/−4/3/3/•/Knockdown, Stun · Catchpole +0/−3/2/2/•/Grapple, Reach · Chain +1/−3/2/2/•/Grapple, Inaccurate, Reach ·
Chainsaw +3/−6/4/3/•••/Bleed, Inaccurate, Two-Handed · Kusari gama (= chain / = hunting knife) · Shield small +0/−2/2/2/••/Concealed · Shield large +2/−4/3/3/••/Concealed ·
Stake +0/−4/1/1/n/a · Stun Gun +0/−1/1/1/•/Stun (no dmg from successes) · Tiger Claws +1/−1/2/2/••/Brawl · Whip +0/−2/1/2/•/Grapple, Stun (Dex+Weaponry) ·
Improvised (p.141): Board w/ Nail +1/−3/2/2/n/a/Fragile, Stun · Improvised Shield +0/−4/2/2/•/Concealed · Nail Gun +0/−2/2/2/•/Inaccurate, Piercing 1 ·
Shovel +1/−3/2/2/•/Knockdown · Tire Iron +1/−3/2/2/••/Guard, Inaccurate · Spear +2/−2/2/4/•/Reach, Two-Handed · Staff +1/−1/2/4/•/Knockdown, Reach, Two-Handed ·
Blowtorch (Size 2, ••, Incendiary, Piercing 2; Blinded unless −1 Defense; Str+Firearms per table note [?]).

**Grenades (p.137 (136))** Dmg / Init / Blast / Force / Range / Str / Size / Avail / Tags
Frag std +2/0/10/3/Thrown(A)/2/1/••••/Knockdown, Stun · Frag heavy +3/−1/5?/4/…/Knockdown, Stun · Molotov +1/−2/3/2?/Thrown/2/2/•/Incendiary ·
Pipe Bomb +1/−1/5/2/Thrown/2/1/•/Inaccurate, Stun · Smoke +0/10?/—/Thrown(A)/••/Concealment · Stun +0/0/5/…/••/Knockdown, Stun ·
Thermite +3/5?/4/…/••••/AP 8, Incendiary · White Phosphorus +3/5?/4/…/••••/AP 3, Incendiary, Concealment.
(Init/Blast/Force columns partially misaligned in text extraction [?].)
Launchers (p.138 (137)): Stand-alone Long/Low/Str 3/Size 3/•••• · Under-barrel Long/Low/2/2/•••• · Automatic Extreme/High/—/4/•••••.
Launcher ammo: Baton +1, Knockdown, Stun (no explosion) · Buckshot +1 Blast 10? Force 5, Knockdown · HE +3/10/4 Knockdown · HEDP +2/10/3 Knockdown, AP 4. Min arming 15 m.
Flamethrowers: Civilian Init −4 Short High Str 3 Size 4 ••• Incendiary · Military −5 Medium High 3 4 ••••• Incendiary; fire Damage 2+2, max 4, Burning.

**Armor (p.144 (143))** Rating / Str / Def / Speed / Avail / Coverage
Modern: Reinforced clothing 1/0,1,0,0,•,T/A/L · Sports gear 2/0,2,−1,−1,•,T/A/L · Kevlar vest 1/3,1,0,0,•,Torso · Flak 2/4,1,−1,0,••,T/A ·
Full riot 3/5,2,−2,−1,•••,T/A/L · Bomb suit 4/6,3,−5,−4,•••••,T/A/Head · Helmet special,2,−1,0,•••,Head.
Archaic: Leather 2/0,2,−1,0,•,T/A · Lorica 2/2,3,−2,−3,••••,Torso · Chain 3/1,3,−2,−2,••,T/A · Plate 4/2,3,−2,−3,••••,T/A/L · Helmet special,2,−1,0,•••,Head.
(Def/Speed pairs read sequentially from extraction; verify against PDF image.)

## 2. Current sheet implementation (src/extras.py `weapons_entry`, `ATK_JS`, `ATK_MACRO`, `ARMOR_LINE`)
Repeating section `weapons`: `wtype` (Melee/Thrown/Ranged/Unarmed), `damage` select 0–5,"5+(6)", `dtype` B/L/A, `range` free text,
`clip` select (core-style clip counts 1…100 belt), `initiative` 0…−5,+1, `str_req` 1–5, `wsize` 1–5, `avail` 0–5 dots,
`atk_attr`/`atk_skill` (Auto by Type), `other_mod`, `tags` free text, `notes`.
JS: pool = Attr(+boost) + Skill (−1 unskilled for the 4 combat skills) + other − max(0, str_req − Str) + wounds + conditions;
Auto: melee Str+Weaponry, ranged Dex+Firearms, thrown Dex+Athletics, unarmed Str+Brawl. `atk_def_default` = 0 for everything
(the "?" placeholder for melee is coerced to 0). Macro prompts Specialty, Modifier, Target Defense; prints damage = successes + rating.
Armor: single line (name, general, ballistic, str, defense/speed) feeding derived stats.

## 3. Gaps / mismatches
1. **Str requirement penalty wrong**: sheet subtracts the full shortfall (Str 1 vs req 3 → −2). HL: flat **−1** (bows: −2, "doubled"). [HL p.135, 140]
2. **No Capacity**: `clip` uses core-book round counts; HL uses Low/Medium/High/Single Shot. No burst selection or "runs dry" tracking.
3. **Range is free text**; no range band selector, no −1/−2/−4 penalties, no "one band beyond = chance die".
4. **Defense default**: melee/thrown/unarmed default to 0 (should prompt with target Defense); firearms at Close should be Size+1, short+ = 0; Slow tag → full Defense.
5. **Tags are free text**: no mechanical effect (9-again/8-again reroll, Accurate +1, Inaccurate −1, Guard/Reach Defense notes, Brawl skill switch, Piercing N, Two-Handed one-hand Str+1).
6. **Damage type**: HL melee & firearms always lethal; unarmed bashing; default `dtype` should follow `wtype` (currently manual). Stun-gun/"bonus successes don't add damage" not representable.
7. **Damage select** missing +0…+5 sign and no 6 cleanly ("5+ (6)"); HL range is +0…+5 (explosive Damage up to +3; Force separate).
8. **Initiative select** lacks −6 (chainsaw) and +1 exists (nunchaku OK).
9. **Size select** 1–5 OK (spear/staff 4); Availability "n/a" missing (stake, board) — use "—" fine.
10. **Bow pool**: Athletics or Firearms choice exists via manual skill; bow damage = min(bow Str, user Str) not computed.
11. **Explosives** not modeled (blast zones, Force pool, half ballistic armor, Deafened).
12. **Armor interaction** not applied to rolls (fine — target's armor), but card doesn't print Piercing; armor Str penalty (−1 Brawl/Weaponry) not applied to attack pool.
13. **Off-hand/two weapons** Initiative rule (higher +1) not supported.

## 4. Proposed changes (for build.py/extras.py, after the live test)
A. Fields
- `capacity` select: `single=Single Shot;low=Low;medium=Medium;high=High;na=— (melee)`; keep `clip` as hidden legacy (migrate: blank/Melee→na, 1–2→low, ≤17+1→medium, ≥20→high).
- `max_range` select: `close;short;medium;long;extreme;melee`. Thrown auto-computed: Close if Str≤3 else Short, +1 if tag Thrown (A).
- Tag checkboxes (or multi-toggle chips) instead of free text: `t_8again,t_9again,t_accurate,t_inaccurate,t_bleed,t_brawl,t_concealed,
  t_enhance(+text skill),t_fragile,t_grapple,t_guard,t_incendiary,t_knockdown,t_piercing(number 0–8),t_reach,t_slow,t_stun,t_thrown,t_thrown_a,t_twohanded,t_nodmg`. Keep `tags` text auto-composed for the card.
- `onehanded` checkbox (Two-Handed weapon used one-handed → str_req+1).
- `damage` select values `0..5` labeled `+0..+5`; `initiative` add −6.
B. Pool JS
- Str shortfall → `−1` flat (−2 if `wtype=bow`); armor Str shortfall → −1 for Brawl/Weaponry.
- `+1` Accurate, `−1` Inaccurate; Brawl tag forces skill=brawl; add `wtype` options `bow`, `explosive`; bow auto skill = higher of Athletics/Firearms, damage = min(rating,str).
- Auto `dtype`: unarmed→B, others→L unless user overrides (add `dtype_override`).
- Rerolls: `atk_again` = 8/9/10 → macro uses `!>8`/`!>9` exploding per existing rolltype convention.
C. Macro
- Query **Range band** `?{Range|Close,0|Short,0|Medium,-1|Long,-2|Extreme,-4}`, plus "beyond max → chance die" note computed from max_range.
- Defense default by type: melee/thrown/unarmed → prompt default `@{target|defense}`-style manual; ranged at Close → Size+1, else 0; Slow → full Defense prompt.
- Burst query (gated by capacity): `Single|0` / `Short +1` / `Medium +2 (≤3 targets)` / `Long +3` [core values — label as such]; card prints "Ammo: empties after …" from table §1.5.
- Card lines: Piercing N, Tags, Knockdown/Stun/Bleed "×2 bonus for Tilt", "bonus successes don't add damage".
D. Presets (optional drop-down `preset` that fills fields via sheet worker) seeded from §1.6 tables (skip revolver rows until verified).
E. Explosives: separate mini block or `wtype=explosive` with `blast_gz/primary`, `force`, tags; macro rolls Force (no Defense) and prints zone damage (A/L/B) + Deafened.
F. Armor line: add `armor_coverage` text and Piercing reminder; optionally a second armor row for helmet (half ratings).

## 5. Implementation status and table corrections (2026-10-31)
All proposals A–F are implemented in src/hurtlocker.py, which is wired in through src/extras.py. Weapons and armor now sit in a full-width `.p1-combat` block on page 1, just above MEMBERS AND REGALIA. Verification is tools/hl_test.py, with output in shots/hl-*.png.

Table corrections were checked against pdftoppm renders. The book's own rows are misprinted:
- p.134 Light Revolver: as printed "Init 6 / Str 0 / Size 2". Used: Dmg +1, Range Medium, Capacity Medium, Init 0, Str 2, Size 1 (inferred).
- p.134 Heavy Revolver: Range and Capacity are swapped and Init reads "6". Used: Dmg +2, Range Long, Capacity Low, Init -2, Str 3, Size 1 (inferred).
- p.136 Smoke, Thermite and White Phosphorus grenades: these rows are shifted one column left. Used: Smoke Blast 10 / Force none; Thermite and WP Blast 5 / Force 4. Init is assumed 0.
- p.137 and p.143 matched the audit. p.140 Blowtorch: +0 / -2 / 2 / 2 / dots 2, Incendiary, Piercing 2.

Uncertain or inferred:
- The burst dice bonuses (+1/+2/+3) come from the core rules.
- Thrown range at Str 7+ is set to Long.
- Pepper spray and stun gun damage is Bashing.
- Beyond max range is shown as a note on the card, not converted to a chance die automatically.
- Bow skill is the higher of Firearms or Athletics.
- Optgroups in the preset select: Roll20 support is unverified.
