#!/usr/bin/env python3
"""Generates assets/svg/terminal.svg — the ENTIRE profile as one terminal
window / one continuous session:

  $ figlet <name>                  big block-letter name banner  ─┐ side
  $ whoami --render=<mode>         ASCII portrait                 ┘ by side
  $ cat whoami.txt                 tagline + short bio + profile views
  $ cat about.md                   about paragraph + motto
  $ column -t focus.tsv            "currently focused on" box-drawing table
  $ cat stack.yaml                 grouped tech-stack tags
  $ cat contact.txt                clickable social/contact links
  $ echo "thanks..."               footer + final cursor

One shared chrome (title bar, traffic lights, decorative theme-toggle
indicator), one blinking cursor at the very end, a slow CRT scanline
drift — this is deliberately the ONLY asset README.md embeds, per
config.yml -> features. See docs/CUSTOMIZATION.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.ascii_art import MODE_STYLES, ascii_grid_svg, image_to_ascii, load_source  # noqa: E402
from lib.blockfont import HEIGHT as BLOCK_HEIGHT  # noqa: E402
from lib.blockfont import render_word  # noqa: E402
from lib.data import load_config, load_user, write_svg  # noqa: E402
from lib.skill_icons import slug_for  # noqa: E402
from lib.svgutil import document, esc, wrap_text  # noqa: E402
from lib.theme import ACCENT_CYCLE, aurora_gradient_defs, aurora_layer, glass_filter_defs  # noqa: E402

UID = "terminal"
PAD_X = 44
GAP = 48
HEADER_H = 46
OUTER_PAD = 80  # margin around the floating terminal panel where the colorful aurora backdrop shows

# The particle field is built from real brand logos (simple-icons), not
# plain dots — this is your stack floating in the backdrop. Browsers cache
# by URL, so repeating slugs across many particles costs nothing extra.
PARTICLE_ICON_SLUGS = [
    "c", "cplusplus", "python", "javascript", "typescript",
    "react", "nextdotjs", "tailwindcss", "html5", "css3",
    "nodedotjs", "express", "flask", "mysql", "postgresql", "supabase",
    "opencv", "tensorflow", "pytorch", "numpy", "pandas",
    "git", "github", "docker", "netlify", "vercel",
]


def _margin_particles(canvas_w: float, canvas_h: float, outer_pad: float, n: int, seed: int) -> list[tuple[float, float, float, float]]:
    """Particles confined to the OUTER_PAD ring around the panel, in
    absolute pixels — computed from the *actual* margin, not a fraction of
    the full canvas (a fractional "12% from the edge" can land well inside
    a fixed-width margin once the canvas is large, hiding the particle
    behind the opaque panel — hence absolute coordinates here)."""
    import random

    rng = random.Random(seed)
    band = max(20.0, outer_pad - 14)
    pts = []
    for _ in range(n):
        side = rng.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x, y = rng.uniform(10, canvas_w - 10), rng.uniform(12, band)
        elif side == "bottom":
            x, y = rng.uniform(10, canvas_w - 10), rng.uniform(canvas_h - band, canvas_h - 12)
        elif side == "left":
            x, y = rng.uniform(12, band), rng.uniform(10, canvas_h - 10)
        else:
            x, y = rng.uniform(canvas_w - band, canvas_w - 12), rng.uniform(10, canvas_h - 10)
        pts.append((x, y, rng.uniform(22, 34), rng.uniform(0, 4)))
    return pts


def _overlay_particles(canvas_w: float, canvas_h: float, n: int, seed: int) -> list[tuple[float, float, float, float]]:
    """Particles scattered across the *entire* canvas, drawn on top of the
    panel at low opacity — the ones that visibly "hover over the screen"
    rather than staying confined to the backdrop margin."""
    import random

    rng = random.Random(seed)
    return [
        (rng.uniform(20, canvas_w - 20), rng.uniform(20, canvas_h - 20), rng.uniform(18, 28), rng.uniform(0, 5))
        for _ in range(n)
    ]


def _particles_svg(points: list[tuple[float, float, float, float]], seed: int) -> str:
    """Renders each (x, y, size, delay) point as a floating/drifting/
    twinkling brand-icon logo, cycling through PARTICLE_ICON_SLUGS."""
    import random

    rng = random.Random(seed)
    order = PARTICLE_ICON_SLUGS[:]
    rng.shuffle(order)

    out = []
    for i, (x, y, size, delay) in enumerate(points):
        slug = order[i % len(order)]
        out.append(
            f'<g style="animation: driftX {6+i%5}s ease-in-out {delay:.2f}s infinite alternate;">'
            f'<image x="{x-size/2:.1f}" y="{y-size/2:.1f}" width="{size:.1f}" height="{size:.1f}" '
            f'href="https://cdn.simpleicons.org/{slug}" '
            f'style="animation: floatY {5+i%6*0.6:.1f}s ease-in-out {delay:.2f}s infinite, '
            f'twinkle {2.6+i%4*0.4:.1f}s ease-in-out {delay:.2f}s infinite;"/>'
            f'</g>'
        )
    return "".join(out)


BLOCK_FONT = 20
BLOCK_LINE_H = 24
PROMPT_FONT = 16
TAGLINE_FONT = 17
BODY_FONT = 15
TABLE_FONT = 14.5
STACK_FONT = 13.5
CHIP_H = 30
ICON_SIZE = 16

ASCII_CELL_W = 7.2
ASCII_CELL_H = 13

TAG_COLORS = ACCENT_CYCLE

GROUP_LABELS = {
    "languages": "LANGUAGES",
    "frontend": "FRONTEND",
    "backend": "BACKEND",
    "ai_ml": "AI / MACHINE LEARNING",
    "cloud": "CLOUD",
    "databases": "DATABASES",
    "devops": "DEVOPS & TOOLING",
    "tools": "EDITOR & TOOLS",
}


def bold_tspans(line: str) -> str:
    parts = line.split("**")
    out = []
    for i, part in enumerate(parts):
        if not part:
            continue
        out.append(f'<tspan class="bold">{esc(part)}</tspan>' if i % 2 == 1 else esc(part))
    return "".join(out)


def prompt_line(x: float, y: float, cmd: str, delay: float, color: str = "accent-teal") -> str:
    # NOTE: a bare fill="..." attribute is a *presentation attribute* — it
    # loses to any CSS class rule that also sets fill (a `<style>` rule
    # always outranks presentation attributes, regardless of specificity).
    # style="fill:..." is a real inline style, which does win — use that
    # for every per-instance color override in this file.
    return (
        f'<text x="{x}" y="{y}" class="prompt" style="animation: fadeInUp .4s ease-out {delay:.2f}s both">'
        f'$ <tspan class="cmd-word" style="fill:var(--{color})">{esc(cmd)}</tspan></text>'
    )


class SectionAccents:
    """Hands out a different accent color to each successive section so the
    page reads as genuinely multi-color rather than one hue repeated."""

    def __init__(self) -> None:
        self._i = 0

    def next(self) -> str:
        color = ACCENT_CYCLE[self._i % len(ACCENT_CYCLE)]
        self._i += 1
        return color


def build() -> str:
    cfg = load_config()
    user = load_user()
    ident = user["identity"]
    username = ident["github_username"]
    ac = cfg["ascii_portrait"]
    mode = ac.get("mode", "terminal")
    style = MODE_STYLES.get(mode, MODE_STYLES["terminal"])
    vc = cfg["visitor_counter"]

    # ---- pre-compute widths so the canvas fits banner + portrait side by side
    first_name = ident["short_name"]
    last_name = ident["name"].split()[-1] if len(ident["name"].split()) > 1 else ""
    word1_rows, missing1 = render_word(first_name)
    word2_rows, missing2 = render_word(last_name) if last_name else ([], [])
    missing = missing1 + missing2
    if missing:
        print(f"[terminal] no block-letter glyph for {missing} — add to scripts/lib/blockfont.py, using fallback")
    banner_col_w = max(len(word1_rows[0]), len(word2_rows[0]) if word2_rows else 0) * (BLOCK_FONT * 0.6)

    img = load_source(cfg, None)
    ascii_lines = image_to_ascii(img, ac["columns"], ac["charset"])
    charset = ac["charset"]
    portrait_w = len(ascii_lines[0]) * ASCII_CELL_W

    WIDTH = round(PAD_X + banner_col_w + GAP + portrait_w + PAD_X)
    CONTENT_W = WIDTH - PAD_X * 2
    portrait_x0 = PAD_X + banner_col_w + GAP

    parts: list[str] = []
    accents = SectionAccents()
    defs = glass_filter_defs(UID) + aurora_gradient_defs(UID) + f"""
    <pattern id="scanlines-{UID}" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="#000000" opacity="0.15"/>
      <animateTransform attributeName="patternTransform" type="translate"
                         from="0 0" to="0 4" dur="6s" repeatCount="indefinite"/>
    </pattern>
  """

    # =====================================================================
    # Row 1: figlet banner (VAJEEDA / SHAIK, stacked) + whoami ASCII portrait
    # side by side — the portrait's height is fixed by the photo, so we
    # compute it first and then stretch the gap between the two banner
    # words to land the tagline at (roughly) the same bottom edge.
    # =====================================================================
    y0 = HEADER_H + 40
    ascii_start_y = y0 + 40
    ascii_rows_svg, _, portrait_bottom = ascii_grid_svg(
        ascii_lines, charset, style, pad_x=portrait_x0, start_y=ascii_start_y,
        anim_delay_base=0.3, cell_w=ASCII_CELL_W, cell_h=ASCII_CELL_H,
    )

    block_start_y = y0 + 40
    word1_bottom = block_start_y + (BLOCK_HEIGHT - 1) * BLOCK_LINE_H
    fixed_span = BLOCK_LINE_H + (BLOCK_HEIGHT - 1) * BLOCK_LINE_H + 34 + 20  # gap + word2 + tagline gap + margin
    extra_gap = (portrait_bottom - word1_bottom - fixed_span) if word2_rows else 0
    extra_gap = max(16, min(180, extra_gap)) if word2_rows else 0

    parts.append(prompt_line(PAD_X, y0, f"figlet {first_name.lower()}", 0.05, accents.next()))
    for i, row in enumerate(word1_rows):
        parts.append(
            f'<text x="{PAD_X}" y="{block_start_y + i*BLOCK_LINE_H}" class="block-letters" '
            f'style="animation: fadeInUp .5s ease-out {0.2+i*0.08:.2f}s both">{esc(row)}</text>'
        )

    if word2_rows:
        word2_start = word1_bottom + BLOCK_LINE_H + extra_gap
        for i, row in enumerate(word2_rows):
            parts.append(
                f'<text x="{PAD_X}" y="{word2_start + i*BLOCK_LINE_H}" class="block-letters" '
                f'style="animation: fadeInUp .5s ease-out {0.55+i*0.08:.2f}s both">{esc(row)}</text>'
            )
        last_word_bottom = word2_start + (BLOCK_HEIGHT - 1) * BLOCK_LINE_H
    else:
        last_word_bottom = word1_bottom

    tagline_y = last_word_bottom + 34
    parts.append(
        f'<text x="{PAD_X}" y="{tagline_y}" class="tagline" style="animation: fadeInUp .5s ease-out 1.0s both">'
        f'{esc(ident.get("banner_tagline") or ident["role"])}</text>'
    )
    banner_bottom = tagline_y + 20

    parts.append(prompt_line(portrait_x0, y0, f"whoami --render={mode}", 0.15, accents.next()))
    cursor1_x = portrait_x0 + len(ascii_lines[-1].rstrip()) * ASCII_CELL_W + 4
    cursor1_y = ascii_start_y + (len(ascii_lines) - 1) * ASCII_CELL_H
    parts.append(f'<g style="animation: glowPulse 4s ease-in-out infinite;">{ascii_rows_svg}</g>')
    parts.append(f'<rect class="cursor-ghost" x="{cursor1_x:.1f}" y="{cursor1_y:.1f}" width="{ASCII_CELL_W*0.8:.1f}" height="{ASCII_CELL_H:.1f}"/>')

    y = max(banner_bottom, portrait_bottom) + GAP

    # Character budget for proportional (sans-serif) body text, sized to
    # BODY_FONT so wrapped lines track the actual font size instead of a
    # fixed char count going physically wider every time the font grows.
    body_wrap_chars = max(50, int(CONTENT_W / (BODY_FONT * 0.54)))

    # =====================================================================
    # Section: whoami.txt (header tagline + short bio + profile views)
    # =====================================================================
    parts.append(prompt_line(PAD_X, y, "cat whoami.txt", 1.1, accents.next()))
    y += 30
    parts.append(f'<text x="{PAD_X}" y="{y}" class="h3">{esc(ident["header_tagline"])}</text>')
    y += 28
    for line in wrap_text(ident["short_bio"], body_wrap_chars):
        parts.append(f'<text x="{PAD_X}" y="{y}" class="italic">{esc(line)}</text>')
        y += 22
    y += 14
    counter_h = 20

    def counter_url(color: str) -> str:
        return (
            f"https://komarev.com/ghpvc/?username={username}&label=Profile%20Views"
            f"&color={color}&style={vc['style']}"
        )

    parts.append(f"""
    <g class="toggle-light">
      <image x="{PAD_X}" y="{y}" height="{counter_h}" href="{esc(counter_url(vc['light_color']))}"/>
    </g>
    <g class="toggle-dark">
      <image x="{PAD_X}" y="{y}" height="{counter_h}" href="{esc(counter_url(vc['dark_color']))}"/>
    </g>""")
    y += counter_h + GAP

    # =====================================================================
    # Section: about.md
    # =====================================================================
    about_color = accents.next()
    parts.append(prompt_line(PAD_X, y, "cat about.md", 0, about_color))
    y += 30
    about = user["about"]
    intro_lines = wrap_text(" ".join(about["intro"].split()), body_wrap_chars)
    for line in intro_lines:
        parts.append(f'<text x="{PAD_X}" y="{y}" class="body">{bold_tspans(line)}</text>')
        y += 23
    y += 10
    parts.append(f'<rect x="{PAD_X}" y="{y-16}" width="4" height="26" fill="var(--{about_color})"/>')
    parts.append(f'<text x="{PAD_X+16}" y="{y}" class="motto" style="fill:var(--{about_color})">{esc(about["motto"])}</text>')
    y += GAP

    # =====================================================================
    # Section: focus.tsv table
    # =====================================================================
    table_color = accents.next()
    parts.append(prompt_line(PAD_X, y, "column -t focus.tsv", 0, table_color))
    y += 30
    table_svg, table_h = build_focus_table(user["focus_table"], PAD_X, y)
    parts.append(table_svg)
    y += table_h + GAP

    # =====================================================================
    # Section: stack.yaml (tech stack tags, grouped)
    # =====================================================================
    parts.append(prompt_line(PAD_X, y, "cat stack.yaml", 0, accents.next()))
    y += 30
    stack_svg, stack_h = build_stack_block(user["skills"], PAD_X, y, CONTENT_W)
    parts.append(stack_svg)
    y += stack_h + GAP

    # =====================================================================
    # Section: contact.txt (connect links)
    # =====================================================================
    parts.append(prompt_line(PAD_X, y, "cat contact.txt", 0, accents.next()))
    y += 34
    links = user["links"]
    link_specs = [
        ("GitHub", links.get("github")),
        ("LinkedIn", links.get("linkedin")),
        ("Portfolio", links.get("portfolio")),
        ("Email", links.get("email")),
    ]
    for i, (label, url) in enumerate(link_specs):
        if not url:
            continue
        color = TAG_COLORS[i % len(TAG_COLORS)]
        parts.append(f"""
      <a href="{esc(url)}">
        <g style="animation: fadeInUp .4s ease-out {0.05*i:.2f}s both;">
          <circle cx="{PAD_X+4}" cy="{y-5}" r="4" fill="var(--{color})" style="animation: glowPulse 2.2s ease-in-out infinite {0.2*i:.2f}s;"/>
          <text x="{PAD_X+18}" y="{y}" class="link-line">
            <tspan class="bold" style="fill:var(--{color})">{esc(label):<11}</tspan>
            <tspan style="fill:var(--text-secondary)">{esc(url)}</tspan>
          </text>
        </g>
      </a>""")
        y += 27
    y += GAP - 27

    # =====================================================================
    # Footer
    # =====================================================================
    footer_color = accents.next()
    footer_cmd = f'echo "{about.get("footer_note", "Thanks for stopping by")}"'
    parts.append(prompt_line(PAD_X, y, footer_cmd, 0, footer_color))
    y += 26
    parts.append(
        f'<text x="{PAD_X}" y="{y}" class="body">{esc(about.get("footer_note", ""))} '
        f'<tspan style="fill:var(--{footer_color})">★</tspan></text>'
    )
    y += 36

    prompt_prefix_w = 2 * (PROMPT_FONT * 0.6)  # "$ " in the monospace .prompt font
    parts.append(f'<text x="{PAD_X}" y="{y}" class="prompt">$</text>')
    parts.append(f'<rect class="cursor" x="{PAD_X + prompt_prefix_w:.1f}" y="{y-14}" width="9" height="18"/>')
    y += 26

    PANEL_H = y
    CANVAS_W = WIDTH + OUTER_PAD * 2
    CANVAS_H = PANEL_H + OUTER_PAD * 2

    # Backdrop particles, confined to the visible margin behind the panel.
    margin_sparkles = _particles_svg(_margin_particles(CANVAS_W, CANVAS_H, OUTER_PAD, n=22, seed=7), seed=7)
    # Foreground particles, drifting on top of the whole panel — low
    # opacity + pointer-events:none so they never block the contact links.
    overlay_sparkles = _particles_svg(_overlay_particles(CANVAS_W, CANVAS_H, n=16, seed=13), seed=13)

    dots = "".join(
        f'<circle cx="{28 + i*22}" cy="23" r="6" fill="{c}"/>'
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"])
    )

    theme_toggle = f"""
    <g transform="translate({WIDTH-104},12)">
      <rect width="60" height="22" rx="11" fill="var(--surface)" stroke="var(--border)"/>
      <g class="toggle-light">
        <g transform="translate(15,11)">
          <circle r="6" fill="var(--accent-blue)"/>
          <g stroke="var(--accent-blue)" stroke-width="1.5" stroke-linecap="round">
            <line x1="0" y1="-9" x2="0" y2="-7"/><line x1="0" y1="7" x2="0" y2="9"/>
            <line x1="-9" y1="0" x2="-7" y2="0"/><line x1="9" y1="0" x2="7" y2="0"/>
            <line x1="-6.5" y1="-6.5" x2="-5" y2="-5"/><line x1="6.5" y1="6.5" x2="5" y2="5"/>
            <line x1="-6.5" y1="6.5" x2="-5" y2="5"/><line x1="6.5" y1="-6.5" x2="5" y2="-5"/>
          </g>
        </g>
      </g>
      <g class="toggle-dark">
        <path transform="translate(38,4)" d="M 10 2 A 7 7 0 1 0 10 16 A 5.5 5.5 0 1 1 10 2 Z" fill="var(--accent-blue)"/>
      </g>
      <text x="30" y="35" text-anchor="middle" class="toggle-caption">theme: auto</text>
    </g>
  """

    body = f"""
  <rect width="{CANVAS_W:.0f}" height="{CANVAS_H:.1f}" fill="var(--bg-alt)"/>
  <clipPath id="canvas-clip-{UID}"><rect width="{CANVAS_W:.0f}" height="{CANVAS_H:.1f}" rx="26"/></clipPath>
  <g clip-path="url(#canvas-clip-{UID})">
    {aurora_layer(UID, int(CANVAS_W), int(CANVAS_H))}
    <rect width="{CANVAS_W:.0f}" height="{CANVAS_H:.1f}" filter="url(#noise-{UID})" opacity="0.4"/>
    {margin_sparkles}
  </g>

  <g transform="translate({OUTER_PAD},{OUTER_PAD})">
    <rect width="{WIDTH}" height="{PANEL_H:.1f}" rx="16" fill="var(--bg)" stroke="var(--border)"
          filter="url(#soft-shadow-{UID})"/>
    <rect width="{WIDTH}" height="{PANEL_H:.1f}" rx="16" fill="none" stroke="url(#text-gradient-{UID})"
          stroke-width="2" style="animation: borderGlow 4s ease-in-out infinite;"/>
    <rect width="{WIDTH}" height="{HEADER_H}" rx="16" fill="var(--surface)"/>
    <rect y="{HEADER_H - 16}" width="{WIDTH}" height="16" fill="var(--surface)"/>
    {dots}
    <text x="{WIDTH/2}" y="29" text-anchor="middle" class="title">{esc(username)}@terminal — ~/profile</text>
    <line x1="0" y1="{HEADER_H}" x2="{WIDTH}" y2="{HEADER_H}" stroke="var(--border)"/>
    {theme_toggle}

    <g style="animation: fadeIn .4s ease-out both;">
      {''.join(parts)}
    </g>

    <clipPath id="panel-clip-{UID}"><rect width="{WIDTH}" height="{PANEL_H:.1f}" rx="16"/></clipPath>
    <g clip-path="url(#panel-clip-{UID})">
      <rect x="0" y="{HEADER_H}" width="{WIDTH}" height="{PANEL_H-HEADER_H:.1f}" fill="url(#scanlines-{UID})" opacity="0.4" pointer-events="none"/>
      <rect width="{WIDTH}" height="{PANEL_H:.1f}" fill="#000000" class="flicker" pointer-events="none"/>
    </g>
  </g>

  <!-- foreground particles: hover over the entire canvas, panel included -->
  <g clip-path="url(#canvas-clip-{UID})" opacity="0.32" pointer-events="none">
    {overlay_sparkles}
  </g>
  """

    extra_style = f"""
    .toggle-light {{ display: block; }}
    .toggle-dark {{ display: none; }}
    @media (prefers-color-scheme: dark) {{
      .toggle-light {{ display: none; }}
      .toggle-dark {{ display: block; }}
    }}
    .flicker {{ opacity: 0; animation: crtFlicker 5s ease-in-out infinite; }}
    @keyframes crtFlicker {{ 0%, 96%, 100% {{ opacity: 0; }} 97% {{ opacity: 0.025; }} 98% {{ opacity: 0; }} }}
    .title {{ font-family: var(--mono); font-size: 12px; fill: var(--text-secondary); }}
    .toggle-caption {{ font-family: var(--mono); font-size: 9px; fill: var(--text-secondary); letter-spacing: .5px; }}
    .prompt {{ font-family: var(--mono); font-size: {PROMPT_FONT}px; fill: var(--text-secondary); white-space: pre; }}
    .cmd-word {{ fill: {style['color']}; font-weight: 700; }}
    .block-letters {{ font-family: var(--mono); font-size: {BLOCK_FONT}px; font-weight: 700; fill: url(#text-gradient-{UID});
                       filter: url(#glow-{UID}); white-space: pre; }}
    .tagline {{ font-family: var(--mono); font-size: {TAGLINE_FONT}px; fill: var(--text-primary); letter-spacing: 0.5px; }}
    .h3 {{ font-family: var(--sans); font-size: 17px; font-weight: 700; fill: var(--text-primary); }}
    .italic {{ font-family: var(--sans); font-size: {BODY_FONT}px; font-style: italic; fill: var(--text-secondary); }}
    .body {{ font-family: var(--sans); font-size: {BODY_FONT}px; fill: var(--text-secondary); }}
    .bold {{ fill: var(--text-primary); font-weight: 700; }}
    .motto {{ font-family: var(--sans); font-size: 14.5px; font-style: italic; font-weight: 700; fill: var(--accent-purple); }}
    .table-font {{ font-family: var(--mono); font-size: {TABLE_FONT}px; white-space: pre; }}
    .table-border {{ fill: var(--border); }}
    .table-header {{ fill: var(--{table_color}); font-weight: 700; }}
    .table-row {{ fill: var(--text-secondary); }}
    .stack-label {{ font-family: var(--mono); font-size: 12.5px; font-weight: 700; letter-spacing: 1.5px; fill: var(--text-secondary); }}
    .chip-text {{ font-family: var(--mono); font-size: {STACK_FONT}px; font-weight: 600; }}
    .link-line {{ font-family: var(--mono); font-size: {BODY_FONT+1}px; white-space: pre; }}
    .glyph {{ font-family: var(--mono); font-size: 12.5px; fill: {style['color']}; }}
    .cursor {{ fill: {style['color']}; animation: blink 0.9s step-end infinite; }}
    .cursor-ghost {{ fill: {style['color']}; opacity: 0.6; animation: blink 0.9s step-end infinite; }}
    a {{ cursor: pointer; }}
    a:hover .link-line {{ fill: var(--accent-teal); }}
    :root {{ --mono: {cfg['typography']['mono_family']}; --sans: {cfg['typography']['font_family']}; }}
    """

    return document(cfg, CANVAS_W, CANVAS_H, body, defs=defs, extra_style=extra_style,
                     title=f"{ident['name']} — terminal profile")


def build_focus_table(rows_data: list[dict], x0: float, y0: float) -> tuple[str, float]:
    headers = ("AREA", "WHAT I'M WORKING ON", "TOOLS & TECH")
    keys = ("area", "working_on", "tools")
    col_w = [
        max(len(headers[i]), max(len(r[k]) for r in rows_data))
        for i, k in enumerate(keys)
    ]

    def border(left: str, mid: str, right: str) -> str:
        return left + mid.join("─" * (w + 2) for w in col_w) + right

    def data(cells: list[str]) -> str:
        return "│ " + " │ ".join(c.ljust(w) for c, w in zip(cells, col_w)) + " │"

    row_h = 24
    lines = [
        (border("┌", "┬", "┐"), "table-border"),
        (data(list(headers)), "table-header"),
        (border("├", "┼", "┤"), "table-border"),
    ]
    for r in rows_data:
        lines.append((data([r[k] for k in keys]), "table-row"))
    lines.append((border("└", "┴", "┘"), "table-border"))

    svg = []
    for i, (text, cls) in enumerate(lines):
        svg.append(
            f'<text x="{x0}" y="{y0 + i*row_h}" class="{cls} table-font" '
            f'style="animation: fadeInUp .35s ease-out {0.03*i:.2f}s both">{esc(text)}</text>'
        )
    return "\n".join(svg), len(lines) * row_h


def build_stack_block(skills: dict, x0: float, y0: float, content_w: float) -> tuple[str, float]:
    """Renders each skill as a rounded chip — a real simple-icons brand
    logo (where one maps cleanly to the name) plus its label — wrapping
    within `content_w`, instead of plain bracketed text."""
    char_w = STACK_FONT * 0.62
    counter = [0]
    svg = []
    y = y0
    for key, items in skills.items():
        label = GROUP_LABELS.get(key, key.upper())
        label_color = TAG_COLORS[counter[0] % len(TAG_COLORS)]
        svg.append(f'<text x="{x0}" y="{y}" class="stack-label" style="fill:var(--{label_color})">{esc(label)}</text>')
        y += 24
        row_top = y
        x = x0
        for item in items:
            name = item["name"]
            slug = slug_for(name)
            icon_block_w = (ICON_SIZE + 8) if slug else 0
            chip_w = 24 + icon_block_w + len(name) * char_w
            if x + chip_w > x0 + content_w and x > x0:
                x = x0
                y = row_top = row_top + CHIP_H + 10
            color = TAG_COLORS[counter[0] % len(TAG_COLORS)]
            counter[0] += 1
            baseline = row_top + CHIP_H * 0.66
            chip = [
                f'<rect x="{x:.1f}" y="{row_top:.1f}" width="{chip_w:.1f}" height="{CHIP_H}" rx="{CHIP_H/2:.0f}" '
                f'fill="var(--bg-alt)" stroke="var(--{color})" stroke-opacity="0.6" '
                f'style="animation: popIn .4s ease-out {0.03*counter[0]:.2f}s both;"/>'
            ]
            tx = x + 12
            if slug:
                icon_y = row_top + (CHIP_H - ICON_SIZE) / 2
                chip.append(
                    f'<image x="{tx:.1f}" y="{icon_y:.1f}" width="{ICON_SIZE}" height="{ICON_SIZE}" '
                    f'href="https://cdn.simpleicons.org/{slug}"/>'
                )
                tx += ICON_SIZE + 8
            chip.append(f'<text x="{tx:.1f}" y="{baseline:.1f}" class="chip-text" style="fill:var(--{color})">{esc(name)}</text>')
            svg.append("".join(chip))
            x += chip_w + 10
        y = row_top + CHIP_H + 20
    return "\n".join(svg), y - y0 - 20


if __name__ == "__main__":
    path = write_svg("terminal.svg", build())
    print(f"wrote {path}")
