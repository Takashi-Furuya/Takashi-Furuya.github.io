from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]

ABOUT = ROOT / "_pages" / "about.md"
PUBLICATIONS = ROOT / "_pages" / "publications.md"
FUNDING = ROOT / "_pages" / "funding.md"
TALKS_DIR = ROOT / "_talks"

OUTPUT = ROOT / "cv_generated.md"


def remove_front_matter(text):
    """Remove Jekyll YAML front matter."""
    return re.sub(
        r"\A---\s*\n.*?\n---\s*\n",
        "",
        text,
        flags=re.DOTALL,
    )


def read_markdown(path):
    text = path.read_text(encoding="utf-8")
    return remove_front_matter(text).strip()


# ============================================================
# Main page
# ============================================================

about = read_markdown(ABOUT)

# Recent News は CV には入れない
about = re.sub(
    r"## Recent News.*?(?=## Education and Professional Experience)",
    "",
    about,
    flags=re.DOTALL,
)

# Contact → Contact Information
about = about.replace("## Contact", "## Contact Information")


# ============================================================
# Publications
# ============================================================

publications = read_markdown(PUBLICATIONS)


# ============================================================
# Funding
# ============================================================

funding = read_markdown(FUNDING)


# ============================================================
# Talks
# ============================================================

talk_entries = []

if TALKS_DIR.exists():
    for path in sorted(TALKS_DIR.glob("*.*"), reverse=True):

        if path.suffix not in [".md", ".html"]:
            continue

        text = path.read_text(encoding="utf-8")

        match = re.match(
            r"\A---\s*\n(.*?)\n---",
            text,
            flags=re.DOTALL,
        )

        if not match:
            continue

        try:
            data = yaml.safe_load(match.group(1))
        except Exception:
            continue

        title = data.get("title", "")
        event = data.get("event", data.get("venue", ""))
        date = data.get("date", "")
        location = data.get("location", "")

        pieces = []

        if date:
            pieces.append(str(date))

        if title:
            pieces.append(f"**{title}**")

        if event:
            pieces.append(str(event))

        if location:
            pieces.append(str(location))

        if pieces:
            talk_entries.append("- " + ". ".join(pieces))


talks = "\n".join(talk_entries)

if not talks:
    talks = "_No talks found._"


# ============================================================
# Build CV Markdown
# ============================================================

cv = f"""
---
title: "Curriculum Vitae"
author: "Takashi Furuya"
geometry: margin=22mm
fontsize: 10pt
papersize: a4
colorlinks: true
linkcolor: blue
urlcolor: blue
---

# Takashi Furuya

{about}

# Publications

{publications}

# Talks and Presentations

{talks}

# Funding and Fellowships

{funding}
"""

OUTPUT.write_text(cv.strip() + "\n", encoding="utf-8")

print(f"Generated: {OUTPUT}")
