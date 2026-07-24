"""Maps skill names (as written in user.yml -> skills) to simple-icons
slugs (https://simpleicons.org), for rendering real brand-colored logos
next to skill tags instead of plain bracketed text.

Compound labels ("XGBoost / LightGBM / CatBoost", "Node.js / Express")
intentionally have no entry — one icon can't represent three tools, so
those chips just render text-only. Add an entry here any time you add a
skill whose name matches a simple-icons slug 1:1.
"""

from __future__ import annotations

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
    "Microsoft Azure": "microsoftazure",
    "PostgreSQL": "postgresql",
    "MySQL": "mysql",
    "Docker": "docker",
    "Kubernetes (basics)": "kubernetes",
    "Terraform (basics)": "terraform",
    "VS Code": "visualstudiocode",
    "Postman": "postman",
    "Jupyter Notebook": "jupyter",
}


def slug_for(skill_name: str) -> str | None:
    return SKILL_ICON_SLUGS.get(skill_name)
