#!/usr/bin/env python3
"""Renders data/internships.json into a markdown table and injects it into
README.md between the INTERNSHIPS:START / INTERNSHIPS:END markers."""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "internships.json"
README_FILE = ROOT / "README.md"

START_MARKER = "<!-- INTERNSHIPS:START -->"
END_MARKER = "<!-- INTERNSHIPS:END -->"


def badge(first_seen: str) -> str:
    try:
        dt = datetime.fromisoformat(first_seen.replace("Z", "+00:00"))
    except Exception:
        return ""
    age_days = (datetime.now(timezone.utc) - dt).days
    return " 🆕" if age_days <= 3 else ""


def render_table(items, category_label):
    rows = [i for i in items if i["category"] == category_label]
    if not rows:
        return f"_No open {category_label} internships found in the last run._\n"

    lines = [
        "| Company | Role | Location | Link |",
        "|---|---|---|---|",
    ]
    for r in rows:
        new_tag = badge(r["first_seen"])
        lines.append(
            f"| {r['company']} | {r['title']}{new_tag} | {r['location']} | [Apply]({r['url']}) |"
        )
    return "\n".join(lines) + "\n"


def main():
    data = json.loads(DATA_FILE.read_text())
    items = data.get("internships", [])
    generated_at = data.get("generated_at", "")

    try:
        ts = datetime.fromisoformat(generated_at).strftime("%d %b %Y, %H:%M UTC")
    except Exception:
        ts = generated_at

    section = []
    section.append(f"_Last updated: **{ts}** · {len(items)} open roles found_\n")
    section.append("### 💻 Tech Internships\n")
    section.append(render_table(items, "tech"))
    section.append("### 📊 Quant Internships\n")
    section.append(render_table(items, "quant"))

    errors = data.get("errors", [])
    if errors:
        section.append("<details><summary>⚠️ Companies skipped this run (config needs fixing)</summary>\n")
        for e in errors:
            section.append(f"- {e}")
        section.append("\n</details>\n")

    new_block = "\n".join(section)

    readme = README_FILE.read_text()
    if START_MARKER not in readme or END_MARKER not in readme:
        raise SystemExit("README.md is missing the INTERNSHIPS:START/END markers.")

    before = readme.split(START_MARKER)[0]
    after = readme.split(END_MARKER)[1]
    updated = f"{before}{START_MARKER}\n{new_block}\n{END_MARKER}{after}"

    README_FILE.write_text(updated)
    print("README.md updated.")


if __name__ == "__main__":
    main()
