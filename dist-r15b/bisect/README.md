# Roll-template CSS bisect kit (live Roll20)
First try the real fix: the new dist/sheet.css + dist/sheet.html, which contain no "webp" in any form,
including escaped forms like `.\77 ebp`. The art is now HTML <img>. If cards are styled, you're done.
Otherwise paste dist/sheet.html unchanged as the HTML, and paste each CSS below in turn as the CSS.
Then roll one cofd-entry card. Order = most likely culprit first:
1. A_template_only.css   - only rules whose selector mentions rolltemplate. Styled => the trigger is in sheet CSS. Unstyled => it's in template CSS.
2. F_template_only_plain.css - A minus url()/var()/custom props/!important. Styled while A isn't => one of those.
3. B_no_url.css           - full CSS, every url() -> none (tests host allow-list / remaining jpg/png urls).
4. D_no_is_where_has_supports.css - drops rules using :is/:where/:has/@supports (23 :has( rules).
5. C_no_custom_props.css  - var() replaced by its fallback, --custom props removed.
6. E_no_important.css     - !important stripped (unlikely; wiki examples use it).
Regenerate: python3 tools/make_bisect.py (after the normal build).
