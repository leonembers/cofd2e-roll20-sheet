# Roll20 paste checklist (game 20630499)
1. Paste from dist/: sheet.html into HTML Layout, sheet.css into CSS Styling, translation.json into Translation.
2. Leave "Legacy Sanitization" OFF (modern mode). Save.
3. Open a character and check:
   - The tabs show as styled pills and the Settings (gear) panel is hidden until you click the gear.
   - The splat buttons read "Promethean the Created" and "Changing Breeds", and the last tab reads "Details" (no [brackets]).
   - The frame art and logos load (they come from files.d20.io).
   - Picking a splat changes the frame and colour; that proves the action buttons and sheet workers run.
   - Clicking a skill dot changes its value, and a skill roll posts a styled card in chat.
4. If it is still unstyled, open the browser console (F12) on the sheet and look for "Uncaught" or CSS errors.
