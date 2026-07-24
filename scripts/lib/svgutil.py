"""Small SVG-building utilities shared by every generator."""

from __future__ import annotations

import textwrap
from xml.sax.saxutils import escape as _xml_escape

from .theme import KEYFRAMES, css_variables


def esc(text: str) -> str:
    return _xml_escape(str(text), {"'": "&apos;", '"': "&quot;"})


def wrap_text(text: str, width_chars: int) -> list[str]:
    return textwrap.wrap(text, width=width_chars) or [""]


def font_stack(cfg: dict, mono: bool = False) -> str:
    key = "mono_family" if mono else "font_family"
    return cfg["typography"][key]


def document(
    cfg: dict,
    width: int,
    height: int,
    body: str,
    defs: str = "",
    extra_style: str = "",
    title: str = "",
    role: str = "img",
) -> str:
    """Wrap generator-specific `body`/`defs` markup in a full, theme-aware
    SVG document. Every generator calls this exactly once so the resulting
    files share one <style> block, one viewBox convention, and one
    accessibility pattern (role=img + <title>)."""
    style = f"{css_variables(cfg)}\n{KEYFRAMES}\n{extra_style}"
    title_tag = f"<title>{esc(title)}</title>" if title else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {width} {height}" width="{width}" height="{height}"
     role="{role}" aria-label="{esc(title)}">
  {title_tag}
  <style>{style}</style>
  <defs>{defs}</defs>
  {body}
</svg>
"""


def glass_panel(
    uid: str,
    x: float,
    y: float,
    w: float,
    h: float,
    rx: int = 20,
    fill: str = "var(--surface)",
    stroke: str = "var(--border)",
    extra_class: str = "",
) -> str:
    return (
        f'<rect class="{extra_class}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1" '
        f'filter="url(#soft-shadow-{uid})"/>'
    )
