"""Shared image -> ASCII conversion + SVG rendering, used by both the
standalone ASCII portrait generator and the combined terminal generator."""

from __future__ import annotations

from PIL import Image, ImageDraw

from .data import repo_root
from .svgutil import esc

CELL_W = 7.2
CELL_H = 13
FONT_SIZE = 12.5

# name -> (fill CSS var / color, opacity floor, opacity ceiling)
MODE_STYLES = {
    "terminal": {"color": "var(--accent-teal)", "floor": 0.12, "ceil": 1.0},
    "matrix": {"color": "#39ff88", "floor": 0.08, "ceil": 1.0},
    "wireframe": {"color": "var(--accent-blue)", "floor": 0.15, "ceil": 0.9},
    "normal": {"color": "var(--text-primary)", "floor": 0.2, "ceil": 1.0},
    "pixel": {"color": "var(--accent-purple)", "floor": 0.15, "ceil": 1.0},
}


def make_placeholder(size=(420, 520)) -> Image.Image:
    """A generic gradient silhouette used until a real photo is provided."""
    w, h = size
    img = Image.new("RGB", size, "#0b0e14")
    px = img.load()
    for y in range(h):
        t = y / h
        r = int(11 + t * 30)
        g = int(14 + t * 60)
        b = int(20 + t * 90)
        for x in range(w):
            px[x, y] = (r, g, b)
    draw = ImageDraw.Draw(img)
    cx = w // 2
    draw.ellipse([cx - 78, 60, cx + 78, 216], fill="#3a4a63")
    draw.rounded_rectangle([cx - 140, 230, cx + 140, h - 20], radius=60, fill="#2c3a52")
    return img


def load_source(cfg: dict, override: str | None) -> Image.Image:
    if override:
        return Image.open(override).convert("RGB")
    rel = cfg["ascii_portrait"]["source_image"]
    path = repo_root() / rel
    if path.exists():
        return Image.open(path).convert("RGB")
    print(f"[ascii] {rel} not found — using placeholder silhouette (see docs/CUSTOMIZATION.md)")
    return make_placeholder()


def image_to_ascii(img: Image.Image, columns: int, charset: str) -> list[str]:
    gray = img.convert("L")
    aspect_correction = 0.52  # terminal glyphs are taller than wide
    w, h = gray.size
    rows = max(1, round(columns * (h / w) * aspect_correction))
    gray = gray.resize((columns, rows))
    pixels = gray.load()
    n = len(charset) - 1
    lines = []
    for y in range(rows):
        line = []
        for x in range(columns):
            brightness = pixels[x, y]
            idx = round((brightness / 255) * n)
            line.append(charset[idx])
        lines.append("".join(line))
    return lines


def ascii_grid_svg(
    ascii_lines: list[str],
    charset: str,
    style: dict,
    pad_x: float,
    start_y: float,
    anim_delay_base: float = 0.4,
    cell_w: float = CELL_W,
    cell_h: float = CELL_H,
) -> tuple[str, float, float]:
    """Renders `ascii_lines` as brightness-quantized, run-length-encoded
    <text> rows (a naive per-character tspan would balloon a single
    portrait to hundreds of KB). Returns (svg, grid_width_px, bottom_y_px)."""
    n = len(charset) - 1
    buckets = 6

    def bucket_of(ch: str) -> int:
        idx = charset.index(ch)
        return round((idx / n) * (buckets - 1)) if n else 0

    def opacity_of(bucket: int) -> float:
        return style["floor"] + (style["ceil"] - style["floor"]) * (bucket / (buckets - 1))

    rows_svg = []
    for ry, line in enumerate(ascii_lines):
        y = start_y + ry * cell_h + cell_h * 0.8
        spans = []
        run_bucket = None
        run_start_cx = None
        run_chars: list[str] = []

        def flush():
            if not run_chars:
                return
            x = pad_x + run_start_cx * cell_w
            opacity = opacity_of(run_bucket)
            spans.append(f'<tspan x="{x:.1f}" y="{y:.1f}" opacity="{opacity:.2f}">{esc("".join(run_chars))}</tspan>')

        for cx, ch in enumerate(line):
            if ch == " ":
                flush()
                run_chars = []
                run_bucket = None
                continue
            b = bucket_of(ch)
            if run_bucket is not None and b == run_bucket and run_chars:
                run_chars.append(ch)
            else:
                flush()
                run_chars = [ch]
                run_bucket = b
                run_start_cx = cx
        flush()

        if not spans:
            continue
        delay = anim_delay_base + ry * 0.018
        rows_svg.append(f'<text class="glyph" style="animation: fadeIn .5s ease-out {delay:.2f}s both">{"".join(spans)}</text>')

    grid_w = len(ascii_lines[0]) * cell_w
    bottom_y = start_y + len(ascii_lines) * cell_h
    return "".join(rows_svg), grid_w, bottom_y
