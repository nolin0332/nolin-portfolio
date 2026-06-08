#!/usr/bin/env python3
import re
from pathlib import Path

h = (Path(__file__).resolve().parents[1] / "public" / "index.html").read_text(encoding="utf-8")
out = Path(__file__).resolve().parents[1] / "scripts" / "section-dump.txt"

parts = []
for sid in re.findall(r'id="(story-[^"]+)"', h):
    start = h.find(f'id="{sid}"')
    nxt = h.find('id="story-', start + 10)
    c = h[start : min(nxt if nxt > start else start + 5000, start + 5000)]
    if "story-feature-title" in c or "skills-cats" in c or "quest-number" in c:
        parts.append(f"\n{'='*60}\n{sid}\n{'='*60}\n{c[:3500]}\n")

out.write_text("".join(parts), encoding="utf-8")
print("Wrote", out)
