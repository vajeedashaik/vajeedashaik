"""Maps skill names (as written in user.yml -> skills) to keys in
scripts/lib/icon_paths.py, for rendering real brand-colored logos next to
skill tags instead of plain bracketed text.

Compound labels ("XGBoost / LightGBM / CatBoost", "Node.js / Express")
intentionally have no entry — one icon can't represent three tools, so
those chips just render text-only. "Microsoft Azure" and "VS Code" are
also text-only: simple-icons doesn't publish those under any slug this
file's fetch script could find. Add an entry here any time you add a
skill with a clean 1:1 icon — see docs/CUSTOMIZATION.md.
"""

from __future__ import annotations

from .icon_paths import ICONS

SKILL_ICON_SLUGS: dict[str, str] = {
    "Python": "python",
    "Java": "openjdk",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "Bash": "gnubash",
    "React": "react",
    "Next.js": "nextdotjs",
    "Tailwind CSS": "tailwindcss",
    "HTML/CSS": "html5",
    "FastAPI": "fastapi",
    "Flask": "flask",
    "PyTorch": "pytorch",
    "TensorFlow": "tensorflow",
    "OpenCV": "opencv",
    "Scikit-learn": "scikitlearn",
    "PostgreSQL": "postgresql",
    "MySQL": "mysql",
    "Docker": "docker",
    "Kubernetes (basics)": "kubernetes",
    "Terraform (basics)": "terraform",
    "Postman": "postman",
    "Jupyter Notebook": "jupyter",
}

assert all(slug in ICONS for slug in SKILL_ICON_SLUGS.values()), "SKILL_ICON_SLUGS references a slug missing from icon_paths.ICONS"


def slug_for(skill_name: str) -> str | None:
    return SKILL_ICON_SLUGS.get(skill_name)
