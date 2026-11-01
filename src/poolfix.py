"""Pool display "Strength (6) + Dexterity (6)" incl. bonus dots (_eff), refreshed on every change."""
LBL = '`${%s[`${%s}_name`] || getAttributeTranslation(%s, %s["sheettype"], %s["homebrew_rank"])} (${getAttributePool(%s, %s)})`'
SHORT = '`${((n) => (n = n.charAt(0).toUpperCase() + n.slice(1), n.length > 7 ? n.slice(0, 3) : n))(String(%s[`${%s}_name`] || getAttributeTranslation(%s, %s["sheettype"], %s["homebrew_rank"])))} ${getAttributePool(%s, %s)}`'
R = [
 ('return Number(values[attribute]) || getUnskilledPenalty(attribute);',
  'const _e = values[`${attribute}_eff`]; return Number(_e !== undefined && _e !== "" ? _e : values[attribute]) || getUnskilledPenalty(attribute);'),
 ('getAttrs([...allStats, ...abilityValueAttributes, "dice_pool_attributes", "sheettype", "homebrew_rank"], (v) => {',
  'getAttrs([...allStats, ...allStats.map((a) => `${a}_eff`), ...abilityValueAttributes, "dice_pool_attributes", "sheettype", "homebrew_rank"], (v) => {'),
 ('getAttrs([...allStats, "dice_pool_attributes", "sheettype", "homebrew_rank"], (values) => {',
  'getAttrs([...allStats, ...allStats.map((a) => `${a}_eff`), "dice_pool_attributes", "sheettype", "homebrew_rank"], (values) => {'),
 ('.map((poolAttribute) => v[`${poolAttribute}_name`] || getAttributeTranslation(poolAttribute, v["sheettype"], v["homebrew_rank"]))\n                        .join(" +\\n");',
  '.map((poolAttribute) => ' + SHORT % ('v','poolAttribute','poolAttribute','v','v','poolAttribute','v') + ')\n                        .join(" + ") + (poolAttributes.length ? " = " + dicePool : "");'),
 ('                    ["dice_pool"]: dicePool\n                });',
  '                    ["dice_pool"]: dicePool,\n                    ["rolldisplay"]: (poolAttributes.length ? poolAttributes.map((a) => ' + SHORT % ('values','a','a','values','values','a','values') + ').join(" + ") + " = " + dicePool : "")\n                });'),
 ('        allStats.forEach((attr) => {\n            on(`change:${attr}`, (eventInfo) => {',
  '        on(allStats.map((a) => `change:${a}_eff`).join(" "), () => updateDicePool());\n        allStats.forEach((attr) => {\n            on(`change:${attr}`, (eventInfo) => {'),
]
def apply(h):
    for a, b in R:
        assert h.count(a) == 1, a[:70]
        h = h.replace(a, b)
    return h
