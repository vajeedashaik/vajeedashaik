"""Minimal ANSI-Shadow-style block lettering, for rendering a name as big
figlet-style ASCII art inside the terminal banner.

Only the glyphs actually needed are hand-defined here (add more as you
rename things — see docs/CUSTOMIZATION.md#banner-name). Any undefined
letter falls back to a generic block glyph instead of breaking the whole
generation pipeline.
"""

from __future__ import annotations

HEIGHT = 5

GLYPHS: dict[str, list[str]] = {
    "V": [
        "██╗   ██╗",
        "██║   ██║",
        "██║   ██║",
        "╚██╗ ██╔╝",
        " ╚████╔╝ ",
    ],
    "A": [
        " █████╗ ",
        "██╔══██╗",
        "███████║",
        "██╔══██║",
        "██║  ██║",
    ],
    "J": [
        "     ██╗",
        "     ██║",
        "     ██║",
        "██   ██║",
        "╚█████╔╝",
    ],
    "E": [
        "███████╗",
        "██╔════╝",
        "█████╗  ",
        "██╔══╝  ",
        "███████╗",
    ],
    "D": [
        "██████╗ ",
        "██╔══██╗",
        "██║  ██║",
        "██║  ██║",
        "██████╔╝",
    ],
    "S": [
        "███████╗",
        "██╔════╝",
        "███████╗",
        "╚════██║",
        "███████║",
    ],
    "H": [
        "██╗  ██╗",
        "██║  ██║",
        "███████║",
        "██╔══██║",
        "██║  ██║",
    ],
    "I": [
        "██╗",
        "██║",
        "██║",
        "██║",
        "██║",
    ],
    "K": [
        "██╗  ██╗",
        "██║ ██╔╝",
        "█████╔╝ ",
        "██╔═██╗ ",
        "██║  ██╗",
    ],
    " ": ["  ", "  ", "  ", "  ", "  "],
}

_FALLBACK_WIDTH = 6


def _fallback_glyph(ch: str) -> list[str]:
    if ch == " ":
        return [" " * _FALLBACK_WIDTH] * HEIGHT
    label = ch if ch.isalnum() else "?"
    return [
        "▓▓▓▓▓▓",
        "▓    ▓",
        f"▓ {label}  ▓",
        "▓    ▓",
        "▓▓▓▓▓▓",
    ]


def render_word(word: str) -> tuple[list[str], list[str]]:
    """Returns (rows, missing_letters). `rows` is HEIGHT strings, one per
    scanline of the rendered word; `missing_letters` lists any characters
    that fell back to the generic glyph (so callers can warn)."""
    rows = ["" for _ in range(HEIGHT)]
    missing: list[str] = []
    for ch in word.upper():
        glyph = GLYPHS.get(ch)
        if glyph is None:
            missing.append(ch)
            glyph = _fallback_glyph(ch)
        for i in range(HEIGHT):
            rows[i] += glyph[i]
    return rows, missing
