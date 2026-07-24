"""Config/user data loading shared by every generator."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def load_config() -> dict:
    with open(repo_root() / "config.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=1)
def load_user() -> dict:
    with open(repo_root() / "user.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def svg_out_dir() -> Path:
    cfg = load_config()
    out = repo_root() / cfg["output"]["svg_dir"]
    out.mkdir(parents=True, exist_ok=True)
    return out


def write_svg(filename: str, content: str) -> Path:
    path = svg_out_dir() / filename
    path.write_text(content, encoding="utf-8", newline="\n")
    return path
