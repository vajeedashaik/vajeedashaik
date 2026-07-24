#!/usr/bin/env python3
"""Runs the terminal generator, then rebuilds README.md.

This is the single entry point the GitHub Actions workflow calls, and the
one command you run locally after editing config.yml / user.yml:

    py scripts/generate_all.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.data import load_config, write_svg  # noqa: E402


def main() -> None:
    cfg = load_config()
    t0 = time.time()

    if cfg.get("features", {}).get("terminal", True):
        import generate_terminal

        svg = generate_terminal.build()
        path = write_svg("terminal.svg", svg)
        print(f"[ok]   terminal -> {path.name} ({len(svg)/1024:.1f} KB)")
    else:
        print("[skip] terminal disabled in config.yml")

    import build_readme
    build_readme.main()

    print(f"\nDone in {time.time()-t0:.2f}s")


if __name__ == "__main__":
    main()
