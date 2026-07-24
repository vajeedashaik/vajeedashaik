# Customization Reference

## How the pipeline fits together

The whole profile is **one asset**: `assets/svg/terminal.svg`, built by
`scripts/generate_terminal.py`. It's a single terminal window rendering,
top to bottom: `figlet <name>` (big block-letter name banner) + `whoami
--render=<mode>` (ASCII portrait) side by side, then `cat whoami.txt`
(tagline/bio/profile-views), `cat about.md`, `column -t focus.tsv`, `cat
stack.yaml` (skill icon chips), `cat contact.txt`, and a footer — one
shared chrome, one cursor, an aurora + particle backdrop.

```
config.yml  ─┐
             ├─►  scripts/generate_terminal.py  ──►  assets/svg/terminal.svg  ─►  scripts/build_readme.py  ──►  README.md
user.yml    ─┘
             assets/img/profile.jpg  ──────────────────────────────────────────┘
```

- **`config.yml`** — how things look: theme colors (light + dark, 5
  accents each), fonts, ASCII-portrait settings, GitHub repo slug.
- **`user.yml`** — what things say: your identity, links, skills, focus
  table, about copy, projects/timeline/experience/certifications (kept
  for future use — see "Data not currently rendered" below).
- **`scripts/lib/`** — shared building blocks: `theme.py` (CSS
  variables/keyframes/gradients/filters), `svgutil.py` (the SVG document
  wrapper + text helpers), `data.py` (YAML loading), `ascii_art.py`
  (image → ASCII conversion + rendering), `blockfont.py` (the figlet-style
  name banner font), `skill_icons.py` (skill name → simple-icons slug map).
- **`scripts/generate_all.py`** — runs the generator, then calls
  `build_readme.py`. The one command / one workflow step that rebuilds
  everything.

Run `python scripts/generate_all.py` any time to preview locally; nothing
requires GitHub Actions to work.

## How theming works (dark/light, no JS)

`terminal.svg` embeds **both** palettes as CSS custom properties:

```css
:root { --bg: #faf3e0; --accent-blue: #e0a526; /* light: beige + gold */ }
@media (prefers-color-scheme: dark) {
  :root { --bg: #150b1e; --accent-blue: #ff6fb5; /* dark: plum + pink */ }
}
```

Because GitHub renders committed SVGs as standalone documents (even when
referenced via `<img src="...">` in Markdown), this media query is
evaluated by the viewer's browser using their actual OS/browser theme —
the SVG adapts with zero JavaScript. The little sun/moon pill in the
terminal's title bar is a *decorative* reflection of that same media
query, not a clickable control — GitHub disables JS in rendered SVGs, so
nothing in a README can actually be clicked to change state.

Each theme has **5** accent tokens (`accent_blue/purple/teal/pink/gold` —
names are historical, not literal: in the light theme `accent_blue` is
gold, not blue), used for the shimmering name-banner gradient, the
animated panel border, and cycling through the different sections/tags/
links so the page reads as multi-color rather than one hue repeated.

To change the palette: edit `config.yml` → `theme.dark` / `theme.light`,
then `python scripts/generate_all.py`.

## Profile picture

Drop any photo at `assets/img/profile.jpg` (path is configurable via
`config.yml` → `ascii_portrait.source_image`) and run
`python scripts/generate_all.py`. Until you add a photo, a generic
gradient silhouette is used so the pipeline still works out of the box.

**Render modes** — `terminal` (default, teal monochrome), `matrix` (green),
`wireframe` (blue outline), `normal` (neutral), `pixel` (purple). Set via
`config.yml` → `ascii_portrait.mode`.

`ascii_portrait.columns` controls resolution/detail vs. file size — higher
columns = a more detailed portrait but a larger SVG (glyphs are
run-length-encoded by brightness bucket to keep file size small).

## Banner name

`generate_terminal.py` renders `identity.short_name` and your surname
(from `identity.name`) as big block letters via `scripts/lib/blockfont.py`,
which only defines glyphs for the letters currently needed (V, A, J, E, D,
S, H, I, K). If you rename to something using other letters, undefined
ones fall back to a generic block glyph — add the missing letter's 5-row
glyph to `GLYPHS` in that file (steal from any "ANSI Shadow" figlet
generator/reference for the exact box-drawing pattern). The gap between
the two stacked words is computed automatically to land roughly level
with the ASCII portrait's bottom edge, whatever its aspect ratio.
`identity.banner_tagline` controls the line underneath.

## Skills & icons

Edit `user.yml` → `skills.<category>`, each item is `{ name, level }`
(`level` isn't currently rendered — chips just show icon + name — but
it's kept for a possible future proficiency-bar view). Category headers
map via `GROUP_LABELS` in `scripts/generate_terminal.py`. Each skill
renders as a chip with a real brand icon if one is mapped in
`scripts/lib/skill_icons.py`; unmapped names (or compound labels like
"XGBoost / LightGBM / CatBoost") render text-only. Add an entry there any
time you add a skill with a clean 1:1 [simpleicons.org](https://simpleicons.org) slug.

## Currently-focused-on table

Edit `user.yml` → `focus_table:`, a list of `{ area, working_on, tools }`.
Rendered as a real box-drawing ASCII table (`column -t` style) — column
widths are computed from your longest entry per column, so keep them
reasonably short for a clean table.

## Contact links

Edit `user.yml` → `links:`. GitHub/LinkedIn/Portfolio/Email render as
clickable lines in `cat contact.txt` if non-blank.

## Feature toggle

`config.yml` → `features.terminal` is the only toggle left — set it
`false` to ship an empty README instead of the terminal window.

## Data not currently rendered

`user.yml` still has `projects`, `timeline`, `experience`,
`certifications`, `achievements`, and `leadership` — left in place from
an earlier multi-section design, not read by `generate_terminal.py`
today. They're harmless to keep (future material if you want a project-
cards or timeline section back) or you can delete them; nothing depends
on them.

## GitHub repo slug

`config.yml` → `github.repo` (format `owner/repo`) is informational
metadata for whichever repo you push this to — not currently consumed by
any script, since the profile-views counter and everything else key off
`identity.github_username` in `user.yml` instead. Keep both in sync with
your actual GitHub username regardless.
