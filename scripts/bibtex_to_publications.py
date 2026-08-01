#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

ROOT = Path(__file__).resolve().parents[1]
BIB = ROOT / "_bibliography" / "publications.bib"
OUT = ROOT / "_publications"

def slugify(text):
    text = text.lower()
    text = re.sub(r"[{}\\]", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:90].rstrip("-")

def yaml_quote(text):
    text = str(text).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'

def clean_latex(text):
    # bibtexparser's unicode conversion handles common accents.
    text = text.replace("{", "").replace("}", "")
    return text.strip()

def author_display(author_field):
    people = [a.strip() for a in author_field.split(" and ")]
    names = []
    for p in people:
        if "," in p:
            last, first = [x.strip() for x in p.split(",", 1)]
            # Show Takashi Furuya as T. Furuya, matching the CV.
            if last == "Furuya" and first.startswith("Takashi"):
                names.append("T. Furuya")
            else:
                initials = " ".join(
                    [part[0] + "." if part and part[0].isalpha() else part
                     for part in first.split()]
                )
                names.append(f"{initials} {last}".strip())
        else:
            names.append(p)
    return ", ".join(names)

def venue(entry):
    return clean_latex(entry.get("journal") or entry.get("booktitle") or "arXiv preprint")

def citation(entry, authors, title, ven):
    year = entry.get("year", "")
    bits = [f"{authors}.", f'"{title}."']
    if ven:
        bits.append(ven + ",")
    if entry.get("volume"):
        bits.append(entry["volume"] + ",")
    if entry.get("number"):
        bits.append("(" + entry["number"] + "),")
    if entry.get("pages"):
        bits.append(entry["pages"] + ",")
    bits.append(f"({year}).")
    return " ".join(bits).replace(" ,", ",")

def main():
    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode
    with BIB.open(encoding="utf-8") as f:
        db = bibtexparser.load(f, parser=parser)

    # Clear only generated Markdown files.
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*.md"):
        f.unlink()

    entries = sorted(
        db.entries,
        key=lambda e: (int(e.get("year", "0")), e.get("title", "")),
        reverse=True,
    )

    for entry in entries:
        year = entry.get("year", "1900")
        title = clean_latex(entry.get("title", "Untitled"))
        authors = author_display(entry.get("author", ""))
        ven = venue(entry)
        status = entry.get("status", "published").strip().lower()
        category = "under-review" if status in {"under-review", "preprint"} else "published"
        key = entry.get("ID", slugify(title))
        permalink = f"/publication/{year}-{slugify(key)}"
        date = f"{year}-01-01"  # sorting placeholder when only the year is known

        lines = [
            "---",
            f"title: {yaml_quote(title)}",
            "collection: publications",
            f"category: {yaml_quote(category)}",
            f"permalink: {permalink}",
            f"date: {date}",
            f"venue: {yaml_quote(ven)}",
            f"authors: {yaml_quote(authors)}",
        ]

        eprint = entry.get("eprint", "")
        if eprint:
            arxiv_url = f"https://arxiv.org/abs/{eprint}"
            lines.append(f"paperurl: {yaml_quote(arxiv_url)}")

        lines += [
            f"citation: {yaml_quote(citation(entry, authors, title, ven))}",
            "---",
            "",
        ]

        if eprint:
            lines += [f"[arXiv](https://arxiv.org/abs/{eprint})", ""]

        filename = f"{year}-{slugify(key)}.md"
        (OUT / filename).write_text("\n".join(lines), encoding="utf-8")

    print(f"Generated {len(entries)} files in {OUT}")

if __name__ == "__main__":
    main()
