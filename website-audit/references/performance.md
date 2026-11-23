# Performance checks

**Scripts:** `check_html.py` reports static indicators only (compression, render-blocking scripts, image dimensions, third-party hosts, HTML size); `check_headers.py` reports Cache-Control and Content-Encoding. **No script measures Core Web Vitals.** Without Lighthouse or field data, write "Not measured".

## Core Web Vitals (C, or external data)
Targets at the 75th percentile: **LCP 2.5s or less, INP 200ms or less, CLS 0.1 or less**.
- Prefer field data (Chrome UX Report, PageSpeed Insights) over lab data. Lab data (Lighthouse) is a useful proxy but varies by run and device profile.
- If you cannot measure, write **Not measured**. Do not estimate Core Web Vitals from HTML.

## Static indicators (A or B)
These are signals, not metrics. Label them as indicators.
- **Compression** (B): HTML/CSS/JS served with gzip or brotli.
- **Caching** (B): long `Cache-Control` on fingerprinted static assets; sensible policy on HTML.
- **Render-blocking resources** (A): scripts in `<head>` without `async`/`defer`; large CSS loaded synchronously.
- **Images**: oversized files, legacy formats where WebP/AVIF would fit, missing `width`/`height` (layout shift risk), missing `loading="lazy"` below the fold, hero image wrongly lazy-loaded.
- **Fonts**: `font-display` set; number of font files; preconnect for font hosts.
- **Third parties**: count and weight of tags, analytics, chat widgets, embeds. Name the heaviest.
- **Page weight and request count** (B): report the numbers you measured, with the page and conditions.

## Reporting
Say what was measured, where, and how (tool, device profile, lab vs field). One slow lab run is not a conclusion; mention variance.
