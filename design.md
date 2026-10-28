# HotRadar news index

Hallmark v2.0.0, full redesign in app scope. Existing categories, source filters, refresh, settings and diagnostics remain.

- Audience: people scanning public trending stories across domestic, international and technology sources.
- Signature: cross-source matches shown as a news index with source names and actual hit counts.
- Keep: HotRadar identity, red hot-news accent, every external source link, fetch/cache/sample behavior, all settings, diagnostics and historical metadata.
- Surface: neutral paper (#f4f3ef), ink (#222825), quiet rules; original red (#ff453a) marks the refresh action. Accessible darker red labels are separate tokens. This is the approved editorial direction, not a marketing page.
- Type: one system UI stack, 16px story text, 13–14px explanation, 21px section, 30px title. All CSS colors/fonts live in theme.css :root.
- Layout: capped 1120px index. Fixed rank/story/status columns. Category and source controls precede results. On phones retain source links, descriptions and time-on-board information.
- Components: 44px controls, 6px corners, visible focus. Source badges are neutral text labels so uncontrolled source colors cannot impair contrast.
- Ticker: existing story summary remains, scrollable by the visitor rather than moving automatically. No duplicate story sequence.
- States: loading, fresh, old cache, built-in sample, unavailable and empty remain explicit. Never label sample content as live.
- File plan: app.py, styles.py, theme.css, .streamlit/config.toml, design.md. No data-layer changes or file deletions.
- Baseline: 46e8c48b788a3d8dd7aec01ea9adea16f16d6d57 on master, archive in local .hallmark/before-source.zip. Independent hallmark-redesign branch; no deployment.
