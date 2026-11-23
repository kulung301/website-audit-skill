# Accessibility checks (WCAG 2.2)

**Scripts:** `check_html.py` covers the static-HTML list below. Everything under "Needs a rendered browser" is not covered by any script here; list it under Not checked unless you ran axe-core or Lighthouse yourself.

Automated and static checks catch only part of real accessibility problems. Say so in the report.

## Checkable from static HTML (A)
- `<html lang>` present and valid (WCAG 3.1.1).
- Page has a meaningful `<title>` (2.4.2).
- Images: informative images have alt text; decorative ones use `alt=""` (1.1.1).
- Form controls have programmatic labels (`<label for>`, `aria-label`), not placeholder-only (1.3.1, 3.3.2, 4.1.2).
- Links and buttons have accessible names; flag empty links and icon-only buttons without a label (2.4.4, 4.1.2).
- Heading structure is logical; landmarks (`main`, `nav`, `header`, `footer`) present (1.3.1, 2.4.1); skip link on content-heavy pages.
- Viewport meta does not disable zoom (`user-scalable=no`, tiny `maximum-scale`) (1.4.4).
- `tabindex` greater than 0; `aria-hidden="true"` on focusable elements; ARIA roles that contradict the element.
- Data tables have header cells (`th`, `scope`); video has captions or a transcript link.

## Needs a rendered browser or axe-core (C)
- Color contrast (1.4.3, 1.4.11), visible focus (2.4.7, 2.4.11), keyboard traps and tab order (2.1.1, 2.1.2), reflow at 320px width (1.4.10), text spacing (1.4.12), motion and autoplay.
- If Tier C is unavailable, list these under **Not checked**.

## Reporting
Cite the WCAG criterion with each finding. Group repeated issues (for example, "23 images missing alt, all in the gallery template") instead of listing every instance.
