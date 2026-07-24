"""Shared theme tokens + reusable CSS (variables, keyframes) for every SVG.

Every generator embeds the SAME variable block and keyframe library so the
whole profile reads as one design system instead of a pile of widgets.
GitHub renders committed SVGs as standalone documents (even via <img>), so
plain CSS custom properties + @media (prefers-color-scheme) + @keyframes all
work with zero JavaScript.
"""

from __future__ import annotations

_VAR_NAMES = [
    "bg", "bg_alt", "surface", "border", "text_primary", "text_secondary",
    "accent_blue", "accent_purple", "accent_teal", "accent_pink", "glow",
]

# A fixed 4-color palette, in a fixed order, for generators that want to
# hand a different hue to each section/row/tag instead of one flat accent
# color — four is enough for real variety without reading as "rainbow".
ACCENT_CYCLE = ["accent-blue", "accent-purple", "accent-teal", "accent-pink"]


def css_variables(cfg: dict) -> str:
    dark = cfg["theme"]["dark"]
    light = cfg["theme"]["light"]

    def block(tokens: dict) -> str:
        return " ".join(f"--{n.replace('_', '-')}:{tokens[n]};" for n in _VAR_NAMES)

    return (
        f":root {{ {block(light)} }}\n"
        f"@media (prefers-color-scheme: dark) {{ :root {{ {block(dark)} }} }}"
    )


# A shared keyframe library. Individual generators only use the subset they
# need, but keeping them centralized guarantees identical timing/easing
# everywhere (e.g. every "glow" pulses at the same rate).
KEYFRAMES = """
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes floatY {
  0%, 100% { transform: translateY(0px); }
  50%      { transform: translateY(-8px); }
}
@keyframes glowPulse {
  0%, 100% { opacity: 0.55; }
  50%      { opacity: 1; }
}
@keyframes auroraDrift {
  0%   { transform: translate(-4%, -2%) scale(1); }
  50%  { transform: translate(4%, 3%) scale(1.08); }
  100% { transform: translate(-4%, -2%) scale(1); }
}
@keyframes shimmer {
  0%   { transform: translateX(-120%); }
  100% { transform: translateX(120%); }
}
@keyframes blink {
  0%, 49%  { opacity: 1; }
  50%, 100% { opacity: 0; }
}
@keyframes dashDraw {
  from { stroke-dashoffset: var(--dash-len, 1000); }
  to   { stroke-dashoffset: 0; }
}
@keyframes growBar {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}
@keyframes popIn {
  from { opacity: 0; transform: scale(0.92); }
  to   { opacity: 1; transform: scale(1); }
}
@keyframes borderGlow {
  0%, 100% { stroke-opacity: 0.35; }
  50%      { stroke-opacity: 0.85; }
}
@keyframes driftX {
  0%, 100% { transform: translateX(0px); }
  50%      { transform: translateX(14px); }
}
@keyframes twinkle {
  0%, 100% { opacity: 0.15; transform: scale(0.8); }
  50%      { opacity: 1; transform: scale(1.15); }
}
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; }
}
"""


def glass_filter_defs(uid: str) -> str:
    """Blur + soft-shadow + noise filters, namespaced by `uid` so multiple
    SVGs can be inlined on one page (GitHub READMEs) without id clashes."""
    return f"""
    <filter id="glass-blur-{uid}" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="18" />
    </filter>
    <filter id="soft-shadow-{uid}" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
    <filter id="glow-{uid}" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="noise-{uid}">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" result="noise"/>
      <feColorMatrix in="noise" type="matrix"
        values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.02 0"/>
    </filter>
  """


# Ten blobs, one per accent hue, spread around the canvas perimeter/center
# in a rough ring so nothing bunches up in one corner.
_AURORA_BLOBS = [
    ("a", "22%", "18%", "62%", "accent-blue", "0.5"),
    ("b", "80%", "22%", "62%", "accent-purple", "0.45"),
    ("c", "78%", "82%", "65%", "accent-teal", "0.42"),
    ("d", "18%", "82%", "62%", "accent-pink", "0.42"),
]


def aurora_gradient_defs(uid: str) -> str:
    blobs = "".join(
        f"""
    <radialGradient id="aurora-{key}-{uid}" cx="{cx}" cy="{cy}" r="{r}">
      <stop offset="0%" stop-color="var(--{color})" stop-opacity="{op}"/>
      <stop offset="100%" stop-color="var(--{color})" stop-opacity="0"/>
    </radialGradient>"""
        for key, cx, cy, r, color, op in _AURORA_BLOBS
    )
    stops = "".join(
        f'<stop offset="{i/(len(ACCENT_CYCLE)-1)*100:.1f}%" stop-color="var(--{color})"/>'
        for i, color in enumerate(ACCENT_CYCLE)
    )
    return blobs + f"""
    <linearGradient id="text-gradient-{uid}" x1="0%" y1="0%" x2="100%" y2="0%">
      {stops}
      <animateTransform attributeName="gradientTransform" type="translate"
                         values="-1 0; 1 0; -1 0" dur="10s" repeatCount="indefinite"/>
    </linearGradient>
  """


def aurora_layer(uid: str, width: int, height: int) -> str:
    """Four drifting radial-gradient blobs behind glass content, one per
    accent hue — the colorful animated backdrop every panel floats on."""
    groups = []
    for i, (key, *_rest) in enumerate(_AURORA_BLOBS):
        dur = 16 + (i % 5) * 3
        direction = "reverse" if i % 2 else "normal"
        groups.append(f"""
    <g style="animation: auroraDrift {dur}s ease-in-out infinite {direction}; transform-origin: center;">
      <rect x="{-width*0.2:.0f}" y="{-height*0.2:.0f}" width="{width*1.4:.0f}" height="{height*1.4:.0f}" fill="url(#aurora-{key}-{uid})"/>
    </g>""")
    return "".join(groups)
