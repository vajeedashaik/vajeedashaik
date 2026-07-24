#!/usr/bin/env python3
"""Assembles README.md.

The profile is currently a single terminal window (assets/svg/terminal.svg
— see generate_terminal.py) plus a profile-views counter, per
config.yml -> features. Every other section generator still exists and
works standalone; if you flip a feature back on in config.yml, add its
markup block back here.

The counter is rendered as a plain <img>/<picture> here in the README
itself rather than inside the SVG: GitHub serves committed SVGs with a
CSP that blocks them from loading any external resource at view time, so
a *live*, view-incrementing badge can only work as a normal markdown
image, never embedded inside our SVG.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.data import load_config, load_user, repo_root  # noqa: E402


def counter_block(cfg: dict, username: str) -> list[str]:
    vc = cfg["visitor_counter"]

    def url(color: str) -> str:
        return (
            f"https://komarev.com/ghpvc/?username={username}&label=Profile%20Views"
            f"&color={color}&style={vc['style']}"
        )

    light, dark = url(vc["light_color"]), url(vc["dark_color"])
    return [
        "<picture>",
        f'  <source media="(prefers-color-scheme: dark)" srcset="{dark}">',
        f'  <source media="(prefers-color-scheme: light)" srcset="{light}">',
        f'  <img src="{light}" alt="Profile views">',
        "</picture>",
        "",
    ]


def main() -> None:
    cfg = load_config()
    user = load_user()
    ident = user["identity"]
    features = cfg["features"]

    lines = ['<div align="center">', ""]

    if features.get("terminal", True):
        lines += [f'<img src="assets/svg/terminal.svg" alt="{ident["name"]} — terminal profile" width="100%"/>', ""]

    if features.get("visitor_counter", True):
        lines += counter_block(cfg, ident["github_username"])

    lines += ["</div>", ""]

    readme = "\n".join(lines)
    out_path = repo_root() / "README.md"
    out_path.write_text(readme, encoding="utf-8", newline="\n")
    print(f"wrote {out_path} ({len(readme)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
